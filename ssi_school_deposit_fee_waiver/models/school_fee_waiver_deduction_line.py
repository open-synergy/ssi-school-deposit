# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SchoolFeeWaiverDeductionLine(models.Model):
    _inherit = "school_fee_waiver_deduction_line"

    def _create_standard_ml(self):
        """Remember the journal item of a deposit deduction line.

        The base model never fills ``move_line_id``. A line booked to
        a deposit liability account needs it, because the deduction
        reconciles that journal item against the source deposit.

        :return: the ``account.move.line`` created for this line
        """
        self.ensure_one()
        move_line = super()._create_standard_ml()
        accounts = self.deduction_id._get_school_deposit_accounts()
        if self.account_id in accounts:
            self.move_line_id = move_line
        return move_line
