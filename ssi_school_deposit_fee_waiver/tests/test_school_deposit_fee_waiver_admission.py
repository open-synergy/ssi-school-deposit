# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositFeeWaiverAdmission(YamlTransactionCase):
    """Scenario test for the reservation on an admission invoice."""

    def test_school_deposit_fee_waiver_admission(self):
        """Run the admission reservation and realization scenario."""
        self.run_yaml_scenario("test_data_school_deposit_fee_waiver_admission.yaml")
