# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSchoolDepositRealization(YamlTransactionCase):
    """Scenario tests for ``school_deposit_realization``."""

    def test_school_deposit_realization(self):
        """Run the create, workflow and negative-path scenarios."""
        self.run_yaml_scenario("test_data_school_deposit_realization.yaml")
