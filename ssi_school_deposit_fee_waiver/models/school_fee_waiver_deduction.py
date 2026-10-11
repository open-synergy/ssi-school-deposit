# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolFeeWaiverDeduction(models.Model):
    _inherit = "school_fee_waiver_deduction"

    def _get_school_deposit_accounts(self):
        """Return the deposit liability accounts of every deposit type.

        :return: ``account.account`` recordset
        """
        types = (
            self.env["school_deposit_type"]
            .sudo()
            .with_context(active_test=False)
            .search([])
        )
        return types.mapped("deposit_account_id")

    def _get_school_deposit_lines(self):
        """Return the lines booked to a deposit liability account.

        :return: ``school_fee_waiver_deduction_line`` recordset
        """
        self.ensure_one()
        accounts = self._get_school_deposit_accounts()
        return self.line_ids.filtered(lambda line: line.account_id in accounts)

    @ssi_decorator.pre_done_check()
    def _02_check_school_deposit_recognition(self):
        """Reject a deposit deduction that enrollment recognition defers.

        Enrollment recognition replaces the account of every line by
        the deferred discount account (see
        ``_03_apply_enrollment_recognition``), so a line booked to a
        deposit liability account would no longer reduce the deposit.
        This check runs before that hook and rejects the document
        when it is already deferred, or when that hook is about to
        defer it.

        :raises UserError: when a line is booked to a deposit
            liability account and the document uses the enrollment
            recognition method
        """
        self.ensure_one()
        if not self._get_school_deposit_lines():
            return
        deferred = self.recognition_method == "enrollment"
        if not deferred and self.waiver_id.type_id.deferred_discount_account_id:
            enrollments = self._get_revenue_recognition_enrollments()
            deferred = (
                bool(enrollments)
                and all(enrollments.mapped("revenue_recognition"))
                and not any(enrollment.state == "done" for enrollment in enrollments)
            )
        if deferred:
            error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: A line is booked to a deposit account, but this document uses \
the enrollment recognition method, which replaces the account of every line
Solution: Remove the Deferred Discount Account from the Waiver Type, or \
book the lines to a discount account
""" % (
                self._description,
                self.id,
            )
            raise UserError(_(error_message))

    @ssi_decorator.post_done_action()
    def _25_reconcile_school_deposit(self):
        """Reconcile each deposit line against the source deposit.

        For every line booked to a deposit liability account, its
        debit journal item is reconciled against the credit deposit
        items of the allocated invoices, oldest first, so the
        remaining deposit drops by the deduction amount.

        :return: nothing
        :raises UserError: when the deposit items of the allocated
            invoices cannot absorb a line
        """
        self.ensure_one()
        rounding = self.company_currency_id.rounding
        invoices = self.allocation_ids.mapped("customer_invoice_id")
        for line in self._get_school_deposit_lines():
            debit_line = line.move_line_id
            if not debit_line:
                continue
            sources = self.env["account.move.line"].search(
                [
                    ("account_id", "=", line.account_id.id),
                    ("credit", ">", 0.0),
                    ("amount_residual", "<", 0.0),
                    ("move_id.state", "=", "posted"),
                    ("move_id", "in", invoices.mapped("move_id").ids),
                ],
                order="date, id",
            )
            if sources:
                debit_line.partner_id = sources[0].partner_id
            for source in sources:
                if (
                    float_compare(
                        debit_line.amount_residual, 0.0, precision_rounding=rounding
                    )
                    <= 0
                ):
                    break
                (debit_line + source).reconcile()
            if (
                float_compare(
                    debit_line.amount_residual, 0.0, precision_rounding=rounding
                )
                > 0
            ):
                error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: The deposit left on the allocated invoices cannot absorb %s of \
account '%s'
Solution: Reduce the line amount or allocate an invoice that carries the \
deposit
""" % (
                    self._description,
                    self.id,
                    line.amount,
                    line.account_id.display_name,
                )
                raise UserError(_(error_message))

    @ssi_decorator.post_cancel_action()
    def _05_unreconcile_school_deposit(self):
        """Undo the reconciliation created by the deposit lines.

        Must run before ``_20_delete_accounting_entry``: the journal
        entry cannot be deleted while its lines are reconciled. It
        restores the remaining deposit.

        :return: nothing
        """
        self.ensure_one()
        lines = self.line_ids.filtered("move_line_id")
        move_lines = lines.mapped("move_line_id")
        if move_lines:
            move_lines.remove_move_reconcile()
        lines.write({"move_line_id": False})
