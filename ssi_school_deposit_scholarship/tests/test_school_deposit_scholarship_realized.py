# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositScholarshipRealized(YamlTransactionCase):
    """Scenario test for the room of a scholarship: realized schedule line."""

    def test_school_deposit_scholarship_realized(self):
        """Run the reservation and realization scenario."""
        self.run_yaml_scenario("test_data_school_deposit_scholarship_realized.yaml")
