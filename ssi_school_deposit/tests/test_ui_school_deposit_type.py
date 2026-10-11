# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolDepositType(HttpSavepointCase):
    """Tour tests for the ``school_deposit_type`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the account, journal and products picked by the tour."""
        super().setUpClass()
        liability_type = cls.env.ref("account.data_account_type_current_liabilities")
        cls.env["account.account"].create(
            {
                "code": "TOURSDTD",
                "name": "TOUR SDT Deposit Account",
                "user_type_id": liability_type.id,
                "reconcile": True,
            }
        )
        cls.env["account.journal"].create(
            {
                "name": "TOUR SDT Journal",
                "code": "TSDTJ",
                "type": "general",
            }
        )
        cls.env["product.product"].create(
            {"name": "TOUR SDT Deposit Product", "type": "service"}
        )
        cls.env["product.product"].create(
            {"name": "TOUR SDT Payable Product", "type": "service"}
        )

    def test_create(self):
        """Run the create tour for ``school_deposit_type``.

        IK: docs/school_deposit_type/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_type_create",
            login="admin",
        )
