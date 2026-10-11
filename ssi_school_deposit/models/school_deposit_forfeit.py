# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date as datetime_date

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare

from odoo.addons.ssi_decorator import ssi_decorator


class SchoolDepositForfeit(models.Model):
    """Represents the forfeit of a school deposit that was never used.

    A deposit that is no longer needed, for example because the
    student withdrew, is forfeited: the liability held on the deposit
    account of a deposit type is turned into income. The document
    names the partner and, per line, the deposit credit journal item
    the amount is taken from. The header credits the Forfeit Account of
    the type and each line debits the deposit account. When the
    document is finished it books that entry and reconciles every
    debit against its deposit credit, so the remaining deposit of the
    source becomes zero. Cancelling a finished document undoes the
    reconciliation and deletes the entry, restoring the deposit.
    """

    _name = "school_deposit_forfeit"
    _inherit = [
        "mixin.transaction_cancel",
        "mixin.transaction_done",
        "mixin.transaction_confirm",
        "mixin.company_currency",
        "mixin.account_move",
        "mixin.account_move_single_line",
    ]
    _description = "School Deposit Forfeit"
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
    # -- the header credits the Forfeit Account, the reverse of the
    # debit of every line on the deposit account.
    _account_id_field_name = "forfeit_account_id"
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
        help="Accounting date of this forfeit document.",
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
        help="Deposit type this document forfeits. It decides which "
        "deposit account, forfeit account and journal are used.",
    )
    deposit_account_id = fields.Many2one(
        string="Deposit Account",
        comodel_name="account.account",
        related="type_id.deposit_account_id",
        store=False,
        help="Deposit Account of the selected Type. Technical field "
        "used to filter the source journal items of the lines.",
    )
    forfeit_account_id = fields.Many2one(
        string="Forfeit Account",
        comodel_name="account.account",
        related="type_id.forfeit_account_id",
        store=False,
        help="Forfeit Account of the selected Type. The header entry "
        "line credits it.",
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
        help="Partner who paid the deposit being forfeited. Must "
        "match the Partner of every source journal item.",
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
        ondelete="restrict",
        readonly=True,
        domain="[('type', 'not in', ('bank', 'cash'))]",
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Accounting journal in which the entry of this document "
        "is posted. Defaulted from the Forfeit Journal of the "
        "selected Type. It must be filled before the document can be "
        "finished.",
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="school_deposit_forfeit_line",
        inverse_name="forfeit_id",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        help="Forfeit lines, one per deposit journal item forfeited. "
        "Their sum is this document's Amount Total.",
    )
    move_id = fields.Many2one(
        string="Journal Entry",
        comodel_name="account.move",
        readonly=True,
        copy=False,
        help="Journal entry generated when this document is finished.",
    )
    amount_total = fields.Monetary(
        string="Amount Total",
        currency_field="currency_id",
        compute="_compute_amount_total",
        store=True,
        compute_sudo=True,
        help="Sum of the lines' Amount. This is also the amount "
        "credited to the Forfeit Account.",
    )

    @api.depends("line_ids.amount")
    def _compute_amount_total(self):
        """Sum the lines into this document's total.

        :return: nothing; assigns ``amount_total``
        """
        for record in self:
            result = sum(record.line_ids.mapped("amount"))
            record.amount_total = result

    def action_compute_line(self):
        """Fill the lines from the unused deposit of the Partner.

        :return: nothing
        """
        for record in self.sudo():
            record._compute_line()

    def _compute_line(self):
        """Replace the lines with every available deposit item.

        Takes the whole remaining amount of each source journal item
        of the Type for the Partner, oldest first.

        :return: nothing
        """
        self.ensure_one()
        Line = self.env["school_deposit_forfeit_line"]
        self.line_ids.unlink()
        domain = self.type_id._get_school_deposit_source_domain(self.partner_id)
        sources = self.env["account.move.line"].search(domain, order="date, id")
        for source in sources:
            Line.create(
                {
                    "forfeit_id": self.id,
                    "source_move_line_id": source.id,
                    "amount": -source.amount_residual,
                }
            )

    @api.onchange("type_id")
    def onchange_journal_id(self):
        """Default Journal from the Forfeit Journal of the Type.

        :return: nothing
        """
        self.journal_id = False
        if self.type_id:
            self.journal_id = self.type_id.forfeit_journal_id

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
    def _01_check_accounting_setup(self):
        """Check that the forfeit account and journal are filled in.

        :raises UserError: when the Type has no Forfeit Account, or
            the document has no Journal.
        """
        self.ensure_one()
        if not self.forfeit_account_id or not self.journal_id:
            error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: The Forfeit Account of the Type or the Journal is empty
Solution: Fill in the Forfeit Account and Forfeit Journal of the Type '%s' \
and the Journal of this document
""" % (
                self._description,
                self.id,
                self.type_id.display_name,
            )
            raise UserError(_(error_message))

    @ssi_decorator.pre_done_check()
    def _02_check_amount(self):
        """Check that the lines do not exceed the deposit items.

        :raises UserError: when the document has no lines, or the
            lines take more from a source journal item than it still
            has.
        """
        self.ensure_one()
        rounding = self.currency_id.rounding
        if not self.line_ids:
            error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: The document has no lines
Solution: Add a line or compute the lines
""" % (
                self._description,
                self.id,
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

        Creates the header move, the credit line to the Forfeit
        Account and a debit line per document line, then posts the
        move.

        :return: nothing
        """
        self.ensure_one()
        self._create_standard_move()  # Mixin
        self._create_standard_ml()  # Mixin
        for line in self.line_ids:
            line._create_school_deposit_forfeit_entry()
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
        """Reconcile every debit line against its deposit credit.

        :return: nothing
        """
        self.ensure_one()
        for line in self.line_ids:
            (line.move_line_id + line.source_move_line_id).reconcile()

    @ssi_decorator.post_cancel_action()
    def _10_unreconcile(self):
        """Undo the reconciliation created by ``_20_reconcile``.

        Must run before ``_20_delete_accounting_entry``: the journal
        entry cannot be deleted while its lines are reconciled.

        :return: nothing
        """
        self.ensure_one()
        self.line_ids.mapped("move_line_id").remove_move_reconcile()

    @ssi_decorator.post_cancel_action()
    def _20_delete_accounting_entry(self):
        """Delete this document's ``account.move``.

        :return: nothing
        """
        self.ensure_one()
        self.line_ids.write({"move_line_id": False})
        self._delete_standard_move()  # Mixin
