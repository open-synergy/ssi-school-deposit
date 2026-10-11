# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import api, fields, models

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
    This first version only carries the document and its workflow --
    ``draft``, ``confirm``, ``reject`` and ``cancel`` -- and has no
    accounting effect yet.
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
    _accounting_date_field_name = "date"
    _currency_id_field_name = "currency_id"
    _company_currency_id_field_name = "company_currency_id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    # -- the header credits the partner's receivable, the reverse of
    # ``customer_invoice``'s debit line.
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
