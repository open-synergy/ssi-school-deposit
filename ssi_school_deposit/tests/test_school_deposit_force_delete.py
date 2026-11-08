# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositForceDelete(YamlTransactionCase):
    """Scenario tests for the force delete guard of a deposit."""

    def test_school_deposit_force_delete(self):
        """Run the force delete rejection scenario."""
        self.run_yaml_scenario("test_data_school_deposit_force_delete.yaml")
