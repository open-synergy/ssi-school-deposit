# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


# Gives the realization a single operating unit, always the one of the
# customer invoice it settles, and books it in that unit. When a line
# takes its deposit from a journal item recorded in ANOTHER operating
# unit, the realization is booked as two journals joined by the
# Interunit Account of the Type: the main journal (this unit) and one
# additional journal per source unit (``interunit_move_ids``). Each
# journal holds a single operating unit, as the journal items of
# ``ssi_financial_accounting_operating_unit`` must follow their entry.
class SchoolDepositRealization(models.Model):
    _name = "school_deposit_realization"
    _inherit = [
        "school_deposit_realization",
        "mixin.single_operating_unit",
    ]

    operating_unit_id = fields.Many2one(
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Operating unit of this realization. It is the operating "
        "unit of the selected Customer Invoice.",
    )
    interunit_move_ids = fields.Many2many(
        string="Interunit Journal Entries",
        comodel_name="account.move",
        relation="school_deposit_realization_interunit_move_rel",
        column1="realization_id",
        column2="move_id",
        readonly=True,
        copy=False,
        help="Additional journal entries, one per source operating "
        "unit, created when a line takes its deposit from another "
        "operating unit. Each debits the deposit account and credits "
        "the Interunit Account of the Type.",
    )

    @api.model
    def create(self, vals):
        """Derive the operating unit from the selected invoice.

        An explicit ``operating_unit_id`` in ``vals`` always wins.

        :param vals: values for the new record
        :return: the created realization
        """
        self._derive_operating_unit_from_invoice(vals)
        return super().create(vals)

    def write(self, vals):
        """Re-derive the operating unit when the invoice changes.

        :param vals: values to write
        :return: ``True``
        """
        self._derive_operating_unit_from_invoice(vals)
        return super().write(vals)

    def _derive_operating_unit_from_invoice(self, vals):
        """Set ``operating_unit_id`` in ``vals`` from the invoice.

        Applies only when ``customer_invoice_id`` is in ``vals``, the
        caller gave no ``operating_unit_id`` and the invoice has one.

        :param vals: the ``create``/``write`` values, changed in place
        :return: nothing
        """
        if "customer_invoice_id" not in vals or "operating_unit_id" in vals:
            return
        invoice = self.env["customer_invoice"].browse(vals["customer_invoice_id"])
        if invoice.operating_unit_id:
            vals["operating_unit_id"] = invoice.operating_unit_id.id

    @api.onchange("customer_invoice_id")
    def onchange_operating_unit_id(self):
        """Default the operating unit from the selected invoice.

        :return: nothing
        """
        if self.customer_invoice_id.operating_unit_id:
            self.operating_unit_id = self.customer_invoice_id.operating_unit_id

    def _prepare_standard_move(self):
        """Add this document's operating unit to the ``account.move``.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["operating_unit_id"] = self.operating_unit_id.id
        return res

    def _check_operating_unit_matches_invoice(self):
        """Require the operating unit to be the invoice's.

        Skipped when either side has no operating unit.

        :raises UserError: when the two operating units differ
        """
        self.ensure_one()
        invoice_ou = self.customer_invoice_id.operating_unit_id
        if (
            self.operating_unit_id
            and invoice_ou
            and invoice_ou != self.operating_unit_id
        ):
            error_message = """
Document Type: %s
Context: Check operating unit
Database ID: %s
Problem: Operating Unit '%s' differs from the Operating Unit '%s' of the \
Customer Invoice
Solution: Select the same Operating Unit as the Customer Invoice
""" % (
                self._description,
                self.id,
                self.operating_unit_id.display_name,
                invoice_ou.display_name,
            )
            raise UserError(_(error_message))

    @ssi_decorator.pre_confirm_check()
    def _10_check_operating_unit(self):
        """Reject a realization whose unit differs from the invoice's.

        :raises UserError: when the operating units differ
        """
        self.ensure_one()
        self._check_operating_unit_matches_invoice()

    @ssi_decorator.pre_done_check()
    def _02_check_operating_unit(self):
        """Reject a realization whose unit differs from the invoice's.

        Repeated at done because a realization created by the
        automatic realization never passes the confirm step.

        :raises UserError: when the operating units differ
        """
        self.ensure_one()
        self._check_operating_unit_matches_invoice()

    @ssi_decorator.pre_done_check()
    def _03_check_interunit_account(self):
        """Require an Interunit Account for an interunit realization.

        :raises UserError: when a line takes its deposit from another
            operating unit and the Type has no Interunit Account
        """
        self.ensure_one()
        interunit_lines = self.line_ids.filtered(
            lambda line: line._is_school_deposit_interunit()
        )
        if interunit_lines and not self.type_id.interunit_account_id:
            error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: A line uses a deposit of another operating unit but the Type has no \
Interunit Account
Solution: Fill in the Interunit Account of the Type '%s'
""" % (
                self._description,
                self.id,
                self.type_id.display_name,
            )
            raise UserError(_(error_message))

    def _get_school_deposit_interunit_move(self, operating_unit):
        """Return the additional journal entry of a source unit.

        Created (and kept in ``interunit_move_ids``) the first time a
        line of that source operating unit is booked. It is booked in
        the document's Journal, which therefore must allow every
        operating unit involved.

        :param operating_unit: the source ``operating.unit``
        :return: the draft ``account.move`` of that operating unit
        """
        self.ensure_one()
        move = self.interunit_move_ids.filtered(
            lambda m: m.operating_unit_id == operating_unit
        )
        if move:
            return move[0]
        move = (
            self.env["account.move"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "name": "%s/%s"
                    % (self.name, operating_unit.code or operating_unit.id),
                    "journal_id": self.journal_id.id,
                    "date": self.date,
                    "partner_id": self.partner_id.id,
                    "operating_unit_id": operating_unit.id,
                }
            )
        )
        self.write({"interunit_move_ids": [(4, move.id)]})
        return move

    @ssi_decorator.post_done_action()
    def _15_post_interunit_moves(self):
        """Post the additional journal entries.

        Runs after ``_10_create_accounting_entry``, which created
        their lines.

        :return: nothing
        """
        self.ensure_one()
        if self.interunit_move_ids:
            self.interunit_move_ids.action_post()

    @ssi_decorator.post_done_action()
    def _30_reconcile_interunit(self):
        """Reconcile the main journal against the additional ones.

        The debit of the Interunit Account in the main journal and
        the credit in the additional journals cancel each other, so
        the account ends with a zero balance. The deposit side is
        already reconciled by ``_20_reconcile``.

        :return: nothing
        """
        self.ensure_one()
        if not self.interunit_move_ids:
            return
        account = self.type_id.interunit_account_id
        lines = (
            self.move_id.line_ids + self.interunit_move_ids.mapped("line_ids")
        ).filtered(lambda line: line.account_id == account)
        lines.reconcile()

    @ssi_decorator.post_cancel_action()
    def _15_delete_interunit_moves(self):
        """Undo and delete the additional journal entries.

        Runs after ``_10_unreconcile`` and before
        ``_20_delete_accounting_entry``. Removing the reconciliation of
        their lines also releases the Interunit Account lines of the
        main journal.

        :return: nothing
        """
        self.ensure_one()
        moves = self.interunit_move_ids
        if not moves:
            return
        moves.mapped("line_ids").remove_move_reconcile()
        self.write({"interunit_move_ids": [(5, 0, 0)]})
        moves.button_cancel()
        moves.with_context(force_delete=True).unlink()
