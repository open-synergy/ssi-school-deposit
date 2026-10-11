# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolDepositForfeitOperatingUnit(HttpSavepointCase):
    """Tour test for the Operating Unit field of the Forfeit form.

    Pairs with IK ``docs/school_deposit_forfeit/01-create.md`` (delta),
    backed by the base IK of ``ssi_school_deposit`` for the
    navigation up to the New button.
    """

    @classmethod
    def setUpClass(cls):
        """Give the admin user a visible, filled Operating Unit field.

        The field is gated by the multi operating unit group, so the
        admin user joins it and gets one assigned and default
        operating unit.
        """
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin")
        partner = cls.env["res.partner"].create({"name": "TOUR SDOU Forfeit Partner"})
        cls.operating_unit = cls.env["operating.unit"].create(
            {
                "name": "TOUR SDOU Forfeit Operating Unit",
                "code": "TSDOUF",
                "partner_id": partner.id,
            }
        )
        cls.env.ref("operating_unit.group_multi_operating_unit").sudo().write(
            {"users": [(4, cls.user_admin.id)]}
        )
        cls.user_admin.sudo().write(
            {
                "assigned_operating_unit_ids": [(4, cls.operating_unit.id)],
                "default_operating_unit_id": cls.operating_unit.id,
            }
        )

    def test_field_operating_unit(self):
        """IK: docs/school_deposit_forfeit/01-create.md (E1 delta)."""
        self.start_tour(
            "/web",
            "ssi_school_deposit_operating_unit_school_deposit_forfeit_create",
            login="admin",
        )
