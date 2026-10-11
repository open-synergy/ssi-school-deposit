# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolDepositRealization(models.Model):
    """Represents the use of a school deposit to settle an invoice.

    A parent's deposit is recorded as a credit on the deposit account
    of a deposit type when the deposit invoice is posted. This
    document is how that deposit is used afterwards: it names the
    payable customer invoice being settled and, per line, the deposit
    credit journal item the amount is taken from. The header is meant
    to credit the partner's receivable and each line to debit the
    deposit account, the reverse of the customer invoice's own entry.
    When the document is finished it books the entry (debit deposit
    account per line, credit receivable of the invoice) and reconciles
    it against both the deposit credits and the invoice. Cancelling a
    finished document undoes the reconciliation and deletes the entry,
    restoring the remaining deposit and the invoice residual.
    """

    _name = "school_deposit_realization"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.account_move_single_line",
    ]
    _description = "School Deposit Realization"
    _order = "date desc, id desc"

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "done"
    _approval_state = "confirm"
    _after_approved_method = "action_done"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True
    _automatically_insert_done_policy_fields = False
    _automatically_insert_done_button = False

    _statusbar_visible_label = "draft,confirm,done"
    _policy_field_order = [
        "confirm_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]
    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    # Sequence attribute
    _create_sequence_state = "done"

    # Accounting Entry Header Mixin (``mixin.account_move``)
    _journal_id_field_name = "journal_id"
    _move_id_field_name = "move_id"
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    # -- the header credits the partner's receivable, the reverse of
    # ``customer_invoice``'s debit line.
    _account_id_field_name = "receivable_account_id"
    _partner_id_field_name = "partner_id"
    _amount_currency_field_name = "amount_total"
    _date_field_name = "date"
    _label_field_name = "name"
    _need_date_due = False
    _normal_amount = "credit"

    date = fields.Date(
        string="Date",
        default=lambda r: datetime_date.today(),
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Accounting date of this realization document.",
    )
    type_id = fields.Many2one(
        string="Type",
        comodel_name="school_deposit_type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Deposit type this document realizes. It decides which "
        "deposit account and journal are used.",
    )
    deposit_account_id = fields.Many2one(
        string="Deposit Account",
        comodel_name="account.account",
        related="type_id.deposit_account_id",
        store=False,
        help="Deposit Account of the selected Type. Technical field "
        "used to filter the source journal items of the lines.",
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Partner who paid the deposit and owes the invoice. Must "
        "match the Partner of the selected invoice and of every "
        "source journal item.",
    )
    customer_invoice_id = fields.Many2one(
        string="Customer Invoice",
        comodel_name="customer_invoice",
        required=True,
        ondelete="restrict",
        domain="[('state', '=', 'open'), ('partner_id', '=', partner_id)]",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Open customer invoice of the Partner that this " "realization settles.",
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        related="company_currency_id",
        store=True,
        compute_sudo=True,
        help="Currency this document is expressed in. This document "
        "does not support a currency other than the Company "
        "Currency.",
    )
    journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        readonly=True,
        domain="[('type', 'not in', ('bank', 'cash'))]",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Accounting journal in which the entry of this document "
        "is posted. Defaulted from the Realization Journal of the "
        "selected Type.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="school_deposit_realization_line",
        inverse_name="realization_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Realization lines, one per deposit journal item used. "
        "Their sum is this document's Amount Total.",
    )
    receivable_account_id = fields.Many2one(
        string="Receivable Account",
        comodel_name="account.account",
        related="customer_invoice_id.receivable_account_id",
        store=False,
        help="Receivable Account of the selected invoice. The header "
        "entry line credits it.",
    )
    move_id = fields.Many2one(
        string="Journal Entry",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is finished.",
    )
    receivable_move_line_id = fields.Many2one(
        string="Receivable Journal Item",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Credit journal item on the Receivable Account created "
        "together with the journal entry, then reconciled against the "
        "receivable journal item of the invoice.",
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        currency_field="currency_id",
        compute="_compute_amount_total",
        store=True,
        compute_sudo=True,
        help="Sum of the lines' Amount. This is also the amount "
        "credited to the partner's receivable account.",
    )

    @api.depends("line_ids.amount")
    def _compute_amount_total(self):
        """Sum the lines into this document's total.

        :return: nothing; assigns ``amount_total``
        """
        for record in self:
            record.amount_total = sum(record.line_ids.mapped("amount"))

    def _get_school_deposit_allowed_amount(self):
        """Return the amount this document may settle on its invoice.

        It is the smaller of the invoice residual and the invoice
        lines of the Payable Products, minus the amount reserved by
        extension modules (see ``customer_invoice``), never below
        zero.

        :return: allowed amount in the document currency
        """
        self.ensure_one()
        invoice = self.customer_invoice_id
        targets = self.type_id.target_product_ids
        payable = sum(
            invoice.line_ids.filtered(lambda line: line.product_id in targets).mapped(
                "price_subtotal"
            )
        )
        amount = min(invoice.amount_residual, payable)
        amount -= invoice._get_school_deposit_reserved_amount()
        return max(self.currency_id.round(amount), 0.0)

    def action_compute_line(self):
        """Fill the lines from the available deposit of the Partner.

        :return: nothing
        """
        for record in self.sudo():
            record._compute_line()

    def _compute_line(self):
        """Replace the lines with the oldest available deposit items.

        Takes from the source journal items of the Type, oldest
        first, until the allowed amount is reached.

        :return: nothing
        """
        self.ensure_one()
        Line = self.env["school_deposit_realization_line"]
        self.line_ids.unlink()
        remaining = self._get_school_deposit_allowed_amount()
        rounding = self.currency_id.rounding
        domain = self.type_id._get_school_deposit_source_domain(self.partner_id)
        sources = self.env["account.move.line"].search(domain, order="date, id")
        for source in sources:
            if float_compare(remaining, 0.0, precision_rounding=rounding) <= 0:
                break
            take = min(-source.amount_residual, remaining)
            if float_compare(take, 0.0, precision_rounding=rounding) <= 0:
                continue
            Line.create(
                {
                    "realization_id": self.id,
                    "source_move_line_id": source.id,
                    "account_id": self.type_id.deposit_account_id.id,
                    "amount": take,
                }
            )
            remaining -= take

    @api.onchange("type_id")
    def onchange_journal_id(self):
        """Default Journal from the Realization Journal of the Type.

        :return: nothing
        """
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.realization_journal_id

    @ssi_decorator.insert_on_form_view()
    def _insert_form_element(self, view_arch):
        """Reconfigure the statusbar's visible states on the form view.

        :param view_arch: the parsed form view architecture
        :return: the (possibly modified) view architecture
        """
        if self._automatically_insert_view_element:
            view_arch = self._reconfigure_statusbar_visible(view_arch)
        return view_arch

    @api.model
    def _get_policy_field(self):
        """Register this model's policy fields for ``mixin.policy``.

        ``done_ok`` (from ``mixin.transaction_done``) must be listed
        here too, or Odoo raises ``ValueError: Compute method failed
        to assign ...done_ok`` as soon as the field is read.

        :return: the base policy fields of the standard three-mixin
            workflow combo
        """
        res = super()._get_policy_field()
        policy_field = [
            "confirm_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "done_ok",
            "cancel_ok",
            "restart_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @ssi_decorator.pre_done_check()
    def _01_check_amount(self):
        """Check the lines against the invoice and the deposit items.

        :raises UserError: when the total exceeds the amount allowed
            on the invoice, or the lines take more from a source
            journal item than it still has.
        """
        self.ensure_one()
        rounding = self.currency_id.rounding
        allowed = self._get_school_deposit_allowed_amount()
        if float_compare(self.amount_total, allowed, precision_rounding=rounding) > 0:
            error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: Amount Total %s exceeds the amount allowed on the invoice (%s)
Solution: Reduce the line amounts or recompute the lines
""" % (
                self._description,
                self.id,
                self.amount_total,
                allowed,
            )
            raise UserError(_(error_message))
        taken = {}
        for line in self.line_ids:
            source = line.source_move_line_id
            taken[source] = taken.get(source, 0.0) + line.amount
        for source, amount in taken.items():
            available = -source.amount_residual
            if float_compare(amount, available, precision_rounding=rounding) > 0:
                error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: Lines take %s from journal item '%s' which only has %s left
Solution: Reduce the line amounts or recompute the lines
""" % (
                    self._description,
                    self.id,
                    amount,
                    source.display_name,
                    available,
                )
                raise UserError(_(error_message))

    @ssi_decorator.post_done_action()
    def _10_create_accounting_entry(self):
        """Create and post this document's ``account.move``.

        Creates the header move, the credit line to the receivable
        account (saved to ``receivable_move_line_id``) and a debit
        line per document line, then posts the move.

        :return: nothing
        """
        self.ensure_one()
        self._create_standard_move()  # Mixin
        ml = self._create_standard_ml()  # Mixin
        self.write({"receivable_move_line_id": ml.id})
        for line in self.line_ids:
            line._create_school_deposit_source_entry()
        self._post_standard_move()  # Mixin

    def _prepare_standard_move(self):
        """Add this document's Partner to the ``account.move`` header.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["partner_id"] = self.partner_id.id
        return res

    @ssi_decorator.post_done_action()
    def _20_reconcile(self):
        """Reconcile the entry against the deposit items and the invoice.

        Each debit line is reconciled against its source journal
        item; the receivable credit line is reconciled against the
        receivable journal item of the invoice.

        :return: nothing
        """
        self.ensure_one()
        for line in self.line_ids:
            (line.move_line_id + line.source_move_line_id).reconcile()
        invoice_ml = self.customer_invoice_id.receivable_move_line_id
        (self.receivable_move_line_id + invoice_ml).reconcile()

    @ssi_decorator.post_cancel_action()
    def _10_unreconcile(self):
        """Undo the reconciliation created by ``_20_reconcile``.

        Must run before ``_20_delete_accounting_entry``: the journal
        entry cannot be deleted while its lines are reconciled.

        :return: nothing
        """
        self.ensure_one()
        lines = self.receivable_move_line_id + self.line_ids.mapped("move_line_id")
        lines.remove_move_reconcile()

    @ssi_decorator.post_cancel_action()
    def _20_delete_accounting_entry(self):
        """Delete this document's ``account.move``.

        :return: nothing
        """
        self.ensure_one()
        self.line_ids.write({"move_line_id": False})
        self.write({"receivable_move_line_id": False})
        self._delete_standard_move()  # Mixin
