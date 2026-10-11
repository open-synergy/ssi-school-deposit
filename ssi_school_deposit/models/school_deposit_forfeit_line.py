# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolDepositForfeitLine(models.Model):
    """Represents one debit line of a school deposit forfeit.

    A line takes ``amount`` out of exactly one deposit credit journal
    item (``source_move_line_id``) posted on the deposit account of
    the forfeit's type, for the same partner. The line itself is
    booked as a debit to that deposit account; ``move_line_id`` is
    filled once the forfeit is accounted for.
    """

    _name = "school_deposit_forfeit_line"
    _inherit = [
        "mixin.account_move_single_line",
    ]
    _description = "School Deposit Forfeit - Line"
    _order = "forfeit_id, id"

    # Accounting Move Single Line Mixin (``mixin.account_move_single_line``)
    _move_id_field_name = "move_id"
    _account_id_field_name = "deposit_account_id"
    _partner_id_field_name = "partner_id"
    _amount_currency_field_name = "amount"
    _date_field_name = "date"
    _normal_amount = "debit"

    forfeit_id = fields.Many2one(
        string="# Forfeit",
        comodel_name="school_deposit_forfeit",
        required=True,
        ondelete="cascade",
        help="Forfeit document this line belongs to.",
    )
    source_move_line_id = fields.Many2one(
        string="Source Journal Item",
        comodel_name="account.move.line",
        required=True,
        ondelete="restrict",
        domain="[('credit', '>', 0), ('amount_residual', '<', 0), "
        "('move_id.state', '=', 'posted')]",
        help="Deposit credit journal item this line forfeits. It must "
        "be posted on the Deposit Account of the document's Type, for "
        "the same Partner, and still have an unreconciled credit.",
    )
    amount = fields.Monetary(
        string="Amount",
        currency_field="currency_id",
        required=True,
        help="Portion of the source journal item being forfeited. "
        "Must be greater than zero and not more than what the source "
        "still has. Defaulted to the whole remaining amount.",
    )
    move_line_id = fields.Many2one(
        string="Journal Item",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
        help="Journal item created for this line once the forfeit is " "accounted for.",
    )

    # Convenience fields mirrored from the header, following the
    # pattern of ``school_deposit_realization_line``.
    deposit_account_id = fields.Many2one(
        related="forfeit_id.deposit_account_id",
        compute_sudo=True,
    )
    move_id = fields.Many2one(
        related="forfeit_id.move_id",
        compute_sudo=True,
    )
    partner_id = fields.Many2one(
        related="forfeit_id.partner_id",
        compute_sudo=True,
    )
    date = fields.Date(
        related="forfeit_id.date",
        compute_sudo=True,
    )
    currency_id = fields.Many2one(
        related="forfeit_id.currency_id",
        compute_sudo=True,
    )
    company_id = fields.Many2one(
        related="forfeit_id.company_id",
        compute_sudo=True,
    )
    company_currency_id = fields.Many2one(
        related="forfeit_id.company_currency_id",
        compute_sudo=True,
    )

    def _create_school_deposit_forfeit_entry(self):
        """Create the debit journal item of this line on the deposit.

        The item is saved to ``move_line_id``.

        :return: the created debit ``account.move.line``
        """
        self.ensure_one()
        ml = self._create_standard_ml()  # Mixin
        self.write({"move_line_id": ml.id})
        return ml

    @api.onchange("source_move_line_id")
    def onchange_amount(self):
        """Default Amount to what the source item still has.

        :return: nothing
        """
        self.amount = 0.0
        if self.source_move_line_id:
            self.amount = -self.source_move_line_id.amount_residual

    @api.constrains("amount")
    def _check_amount_positive(self):
        """Require the Amount to be greater than zero.

        :raises ValidationError: when ``amount`` is zero or negative.
        """
        for record in self:
            if record.amount <= 0.0:
                error_message = """
Document Type: %s
Context: Configure forfeit line
Database ID: %s
Problem: Amount %s is not greater than zero
Solution: Enter an Amount greater than zero
""" % (
                    record._description,
                    record.id,
                    record.amount,
                )
                raise ValidationError(_(error_message))
