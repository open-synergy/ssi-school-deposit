# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositOperatingUnit(YamlTransactionCase):
    """Scenario tests for the operating unit of the school deposit."""

    def test_school_deposit_operating_unit(self):
        """Run the same-unit, interunit, cancel and rule scenarios."""
        self.run_yaml_scenario("test_data_school_deposit_operating_unit.yaml")
