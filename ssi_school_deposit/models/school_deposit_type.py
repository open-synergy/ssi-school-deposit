# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SchoolDepositType(models.Model):
    """Represents a kind of school deposit and how it is realized.

    A school records a parent's deposit as a payment term product line
    on an admission or enrollment invoice, whose posted journal item
    credits a deposit liability account. A deposit type tells the
    school which account holds that liability, which products identify
    the deposit invoice lines (Deposit Products), which products the
    deposit may later be used to settle (Payable Products), and which
    journal the realization entry is booked in. Finance staff
    configure the accounting once here; non-accounting users then work
    only with products.
    """

    _name = "school_deposit_type"
    _inherit = ["mixin.master_data"]
    _description = "School Deposit Type"

    deposit_account_id = fields.Many2one(
        string="Deposit Account",
        comodel_name="account.account",
        required=True,
        ondelete="restrict",
        help="Liability account credited when a deposit invoice is "
        "posted. It must allow reconciliation, because a realization "
        "reconciles its journal item against the deposit credit.",
    )
    realization_journal_id = fields.Many2one(
        string="Realization Journal",
        comodel_name="account.journal",
        required=True,
        ondelete="restrict",
        domain="[('type', 'not in', ('bank', 'cash'))]",
        help="Journal in which the entry of a realization of this "
        "deposit type is posted. Bank and Cash journals are not "
        "offered, since a realization is not a received payment.",
    )
    source_product_ids = fields.Many2many(
        string="Deposit Products",
        comodel_name="product.product",
        relation="school_deposit_type_source_product_rel",
        column1="type_id",
        column2="product_id",
        required=True,
        help="Products whose invoice lines record a deposit of this "
        "type. A deposit is only taken from invoices that carry one "
        "of these products.",
    )
    target_product_ids = fields.Many2many(
        string="Payable Products",
        comodel_name="product.product",
        relation="school_deposit_type_target_product_rel",
        column1="type_id",
        column2="product_id",
        required=True,
        help="Products whose invoice lines this deposit may be used " "to settle.",
    )
    auto_realize = fields.Boolean(
        string="Auto Realize",
        default=True,
        help="If checked, a realization is proposed automatically "
        "whenever a payable invoice is posted. If unchecked, "
        "realizations of this type are created by hand only.",
    )

    @api.constrains("deposit_account_id")
    def _check_deposit_account_reconcile(self):
        """Require the Deposit Account to allow reconciliation.

        :raises ValidationError: when ``deposit_account_id.reconcile``
            is not set.
        """
        for record in self:
            if record.deposit_account_id and not record.deposit_account_id.reconcile:
                error_message = """
Document Type: %s
Context: Configure deposit type
Database ID: %s
Problem: Account '%s' does not allow reconciliation
Solution: Select an account with Allow Reconciliation checked
""" % (
                    record._description,
                    record.id,
                    record.deposit_account_id.display_name,
                )
                raise ValidationError(_(error_message))
