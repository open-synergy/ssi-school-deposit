# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositFeeWaiverDeduction(YamlTransactionCase):
    """Scenario test for a fee waiver deduction on a deposit item."""

    def test_school_deposit_fee_waiver_deduction(self):
        """Run the deposit deduction, forfeit and cancel scenario."""
        self.run_yaml_scenario("test_data_school_deposit_fee_waiver_deduction.yaml")
