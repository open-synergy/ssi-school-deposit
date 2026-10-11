# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolDepositRealizationLine(models.Model):
    """Represents one debit line of a school deposit realization.

    A line takes ``amount`` out of exactly one deposit credit journal
    item (``source_move_line_id``) posted on the deposit account of
    the realization's type, for the same partner. The line itself is
    booked as a debit to that deposit account; ``move_line_id`` is
    filled once the realization is accounted for.
    """

    _name = "school_deposit_realization_line"
    _inherit = [
        "mixin.account_move_single_line",
    ]
    _description = "School Deposit Realization - Line"
    _order = "realization_id, id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    _account_id_field_name = "account_id"
    _amount_currency_field_name = "amount"
    _date_field_name = "date"
    _normal_amount = "debit"

    realization_id = fields.Many2one(
        string="# Realization",
        comodel_name="school_deposit_realization",
        required=True,
        ondelete="cascade",
        help="Realization document this line belongs to.",
    )
    source_move_line_id = fields.Many2one(
        string="Source Journal Item",
        comodel_name="account.move.line",
        required=True,
        ondelete="restrict",
        domain="[('credit', '>', 0), ('amount_residual', '<', 0), "
        "('move_id.state', '=', 'posted')]",
        help="Deposit credit journal item this line takes from. It must "
        "be posted on the Deposit Account of the document's Type, for "
        "the same Partner, and still have an unreconciled credit.",
    )
    account_id = fields.Many2one(
        string="Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Deposit account this line debits. Defaulted from the "
        "Deposit Account of the document's Type.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
        help="Portion of the source journal item being used. Must be "
        "greater than zero.",
    )
    move_line_id = fields.Many2one(
        string="Journal Item",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item created for this line once the realization "
        "is accounted for.",
    )

    # Convenience fields mirrored from the header, following the
    # pattern of ``customer_invoice.line``.
    date = fields.Date(
        related="realization_id.date",
        compute_sudo=True,
    )
    currency_id = fields.Many2one(
        related="realization_id.currency_id",
        compute_sudo=True,
    )
    company_id = fields.Many2one(
        related="realization_id.company_id",
        compute_sudo=True,
    )
    company_currency_id = fields.Many2one(
        related="realization_id.company_currency_id",
        compute_sudo=True,
    )

    @api.onchange("realization_id", "source_move_line_id")
    def onchange_account_id(self):
        """Default Account from the Type, else from the source item.

        :return: nothing
        """
        self.account_id = False
        if self.realization_id.type_id:
            self.account_id = self.realization_id.type_id.deposit_account_id
        elif self.source_move_line_id:
            self.account_id = self.source_move_line_id.account_id

    @api.constrains("amount")
    def _check_amount_positive(self):
        """Require the Amount to be greater than zero.

        :raises ValidationError: when ``amount`` is zero or negative.
        """
        for record in self:
            if record.amount <= 0.0:
                error_message = """
Document Type: %s
Context: Configure realization line
Database ID: %s
Problem: Amount %s is not greater than zero
Solution: Enter an Amount greater than zero
""" % (
                    record._description,
                    record.id,
                    record.amount,
                )
                raise ValidationError(_(error_message))
