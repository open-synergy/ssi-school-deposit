# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolDepositForfeit(HttpSavepointCase):
    """Tour tests for the ``school_deposit_forfeit`` instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the master data and forfeits required by the tours.

        Every tour scenario gets its own dedicated Partner (suffixed
        CREATE/COMPUTE/CONFIRM/APPROVE/REJECT/CANCEL), and each Partner
        owns at most one forfeit. No suffix is a prefix of another, so
        the list view always shows one uniquely-named row per scenario,
        searchable by the Partner column, and a tour that moves its own
        document can never affect the fixture of another scenario.
        """
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")

        receivable_type = cls.env.ref("account.data_account_type_receivable")
        liability_type = cls.env.ref("account.data_account_type_current_liabilities")
        income_type = cls.env.ref("account.data_account_type_revenue")
        receivable_account = cls.env["account.account"].create(
            {
                "code": "TOURSDFR",
                "name": "TOUR SDF Receivable Account",
                "user_type_id": receivable_type.id,
                "reconcile": True,
            }
        )
        deposit_account = cls.env["account.account"].create(
            {
                "code": "TOURSDFD",
                "name": "TOUR SDF Deposit Account",
                "user_type_id": liability_type.id,
                "reconcile": True,
            }
        )
        forfeit_account = cls.env["account.account"].create(
            {
                "code": "TOURSDFF",
                "name": "TOUR SDF Forfeit Account",
                "user_type_id": income_type.id,
            }
        )
        sale_journal = cls.env["account.journal"].create(
            {"name": "TOUR SDF Sale Journal", "code": "TSDFS", "type": "sale"}
        )
        general_journal = cls.env["account.journal"].create(
            {"name": "TOUR SDF General Journal", "code": "TSDFG", "type": "general"}
        )
        source_product = cls.env["product.product"].create(
            {"name": "TOUR SDF Deposit Product", "type": "service"}
        )
        target_product = cls.env["product.product"].create(
            {"name": "TOUR SDF Payable Product", "type": "service"}
        )
        cls.deposit_type = cls.env["school_deposit_type"].create(
            {
                "name": "TOUR SDF Type",
                "code": "TOURSDFT",
                "deposit_account_id": deposit_account.id,
                "realization_journal_id": general_journal.id,
                "forfeit_journal_id": general_journal.id,
                "forfeit_account_id": forfeit_account.id,
                "source_product_ids": [(6, 0, source_product.ids)],
                "target_product_ids": [(6, 0, target_product.ids)],
            }
        )
        cls.deposit_account = deposit_account
        cls.source_product = source_product
        cls.general_journal = general_journal
        cls.sale_journal = sale_journal
        cls.receivable_account = receivable_account
        cls.admin = admin
        cls.invoice_type = cls.env["customer_invoice_type"].create(
            {
                "name": "TOUR SDF Invoice Type",
                "code": "/",
                "journal_id": sale_journal.id,
                "receivable_account_id": receivable_account.id,
            }
        )
        # ``global_use`` makes the reason selectable on every document;
        # without it the wizard radio does not offer the reason.
        cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR SDF Cancel Reason",
                "code": "TOURSDFCR",
                "global_use": True,
            }
        )

        # ── Create tour: a posted deposit entry, no forfeit yet ──
        create_partner = cls._create_partner("CREATE")
        contra_account = cls.env["account.account"].create(
            {
                "code": "TOURSDFC",
                "name": "TOUR SDF Contra Account",
                "user_type_id": income_type.id,
            }
        )
        deposit_move = cls.env["account.move"].create(
            {
                "journal_id": general_journal.id,
                "date": "2026-07-15",
                "ref": "TOUR SDF Deposit Entry",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR SDF Deposit Entry - Contra",
                            "account_id": contra_account.id,
                            "partner_id": create_partner.id,
                            "debit": 500000.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "TOUR SDF Deposit Entry - Deposit",
                            "account_id": deposit_account.id,
                            "partner_id": create_partner.id,
                            "debit": 0.0,
                            "credit": 500000.0,
                        },
                    ),
                ],
            }
        )
        deposit_move.action_post()

        # ── Compute Lines tour: a Draft forfeit without lines ──
        partner = cls._create_partner("COMPUTE")
        cls._open_deposit_invoice(partner)
        cls._create_forfeit(partner)

        # ── Confirm tour: a Draft forfeit with lines ──
        partner = cls._create_partner("CONFIRM")
        cls._open_deposit_invoice(partner)
        confirm = cls._create_forfeit(partner)
        confirm.action_compute_line()

        # ── Approve tour: a forfeit Waiting for Approval ──
        partner = cls._create_partner("APPROVE")
        cls._open_deposit_invoice(partner)
        approve = cls._create_forfeit(partner)
        approve.action_compute_line()
        approve = approve.with_user(admin)
        approve.action_confirm()
        approve.invalidate_cache()

        # ── Reject tour: a forfeit Waiting for Approval ──
        partner = cls._create_partner("REJECT")
        cls._open_deposit_invoice(partner)
        reject = cls._create_forfeit(partner)
        reject.action_compute_line()
        reject = reject.with_user(admin)
        reject.action_confirm()
        reject.invalidate_cache()

        # ── Cancel tour: a Done forfeit ──
        partner = cls._create_partner("CANCEL")
        cls._open_deposit_invoice(partner)
        done = cls._create_forfeit(partner)
        done.action_compute_line()
        done.with_context(bypass_policy_check=True).action_done()

    @classmethod
    def _create_partner(cls, suffix):
        """Create the dedicated partner of one tour scenario.

        :param suffix: scenario name appended to the partner name
        :return: the new ``res.partner`` record
        """
        return cls.env["res.partner"].create(
            {"name": "TOUR SDF Customer %s" % suffix, "is_company": True}
        )

    @classmethod
    def _open_deposit_invoice(cls, partner):
        """Create a deposit invoice and open it through its workflow.

        The opened invoice posts a credit of 1000 on the deposit
        account, which is the unused deposit the forfeit takes.

        :param partner: the ``res.partner`` the invoice is billed to
        :return: the opened ``customer_invoice`` record
        """
        invoice = cls.env["customer_invoice"].create(
            {
                "type_id": cls.invoice_type.id,
                "partner_id": partner.id,
                "date": "2026-08-01",
                "date_due": "2026-09-01",
                "currency_id": cls.env.ref("base.USD").id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "journal_id": cls.sale_journal.id,
                "receivable_account_id": cls.receivable_account.id,
            }
        )
        cls.env["customer_invoice.line"].create(
            {
                "customer_invoice_id": invoice.id,
                "product_id": cls.source_product.id,
                "name": cls.source_product.name,
                "account_id": cls.deposit_account.id,
                "uom_quantity": 1,
                "price_unit": 1000.0,
            }
        )
        invoice = invoice.with_user(cls.admin).with_context(bypass_policy_check=True)
        invoice.action_confirm()
        invoice.invalidate_cache()
        invoice.action_approve_approval()
        invoice.invalidate_cache()
        return invoice

    @classmethod
    def _create_forfeit(cls, partner):
        """Create a Draft forfeit without lines for a partner.

        :param partner: the ``res.partner`` who paid the deposit
        :return: the new ``school_deposit_forfeit`` record
        """
        return cls.env["school_deposit_forfeit"].create(
            {
                "type_id": cls.deposit_type.id,
                "partner_id": partner.id,
                "journal_id": cls.general_journal.id,
                "date": "2026-08-10",
                "user_id": cls.admin.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_create",
            login="admin",
        )

    def test_compute_line(self):
        """Run the compute lines tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/02-compute-line.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_compute_line",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/03-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_confirm",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/04-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_approve",
            login="admin",
        )

    def test_reject(self):
        """Run the reject tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/05-reject.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_reject",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_deposit_forfeit``.

        IK: docs/school_deposit_forfeit/06-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_forfeit_cancel",
            login="admin",
        )
