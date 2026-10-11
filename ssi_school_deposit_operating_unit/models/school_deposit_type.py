# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


# Adds the Interunit Account to the deposit type. A realization that
# uses a deposit recorded in another operating unit books its two
# journals against this single account, so it is configured once by
# finance staff and never chosen by a school user.
class SchoolDepositType(models.Model):
    _name = "school_deposit_type"
    _inherit = ["school_deposit_type"]

    interunit_account_id = fields.Many2one(
        string="Interunit Account",
        comodel_name="account.account",
        ondelete="restrict",
        help="Account that links the two journals of a realization "
        "that uses a deposit recorded in another operating unit. It "
        "must allow reconciliation. Required before such a "
        "realization can be finished.",
    )

    @api.constrains("interunit_account_id")
    def _check_interunit_account_reconcile(self):
        """Require the Interunit Account to allow reconciliation.

        :raises ValidationError: when ``interunit_account_id.reconcile``
            is not set.
        """
        for record in self:
            account = record.interunit_account_id
            if account and not account.reconcile:
                error_message = """
Document Type: %s
Context: Configure deposit type
Database ID: %s
Problem: Account '%s' does not allow reconciliation
Solution: Select an account with Allow Reconciliation checked
""" % (
                    record._description,
                    record.id,
                    account.display_name,
                )
                raise ValidationError(_(error_message))
