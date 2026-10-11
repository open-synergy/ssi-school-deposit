# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase -- NOT HttpCase. In 14.0, HttpCase does not set up
# cls.env in setUpClass, so fixtures written there would fail with
# AttributeError before the browser even starts.
from odoo.tests import HttpSavepointCase, tagged


@tagged("post_install", "-at_install")
class TestUiSchoolDepositRealization(HttpSavepointCase):
    """Tour tests for the ``school_deposit_realization`` instructions."""

    @classmethod
    def setUpClass(cls):
        """Create the master data and realizations required by the tours.

        Every tour scenario gets its own dedicated Partner (suffixed
        CREATE/CONFIRM/REJECT/CANCEL/RESTART), so the list view always
        shows one uniquely-named row per scenario, searchable by the
        Partner column, and a tour that moves its own document can never
        affect the fixture of another scenario.
        """
        super().setUpClass()
        admin = cls.env.ref("base.user_admin")

        receivable_type = cls.env.ref("account.data_account_type_receivable")
        liability_type = cls.env.ref("account.data_account_type_current_liabilities")
        income_type = cls.env.ref("account.data_account_type_revenue")
        receivable_account = cls.env["account.account"].create(
            {
                "code": "TOURSDRR",
                "name": "TOUR SDR Receivable Account",
                "user_type_id": receivable_type.id,
                "reconcile": True,
            }
        )
        deposit_account = cls.env["account.account"].create(
            {
                "code": "TOURSDRD",
                "name": "TOUR SDR Deposit Account",
                "user_type_id": liability_type.id,
                "reconcile": True,
            }
        )
        contra_account = cls.env["account.account"].create(
            {
                "code": "TOURSDRC",
                "name": "TOUR SDR Contra Account",
                "user_type_id": income_type.id,
            }
        )
        sale_journal = cls.env["account.journal"].create(
            {"name": "TOUR SDR Sale Journal", "code": "TSDRS", "type": "sale"}
        )
        general_journal = cls.env["account.journal"].create(
            {"name": "TOUR SDR General Journal", "code": "TSDRG", "type": "general"}
        )
        source_product = cls.env["product.product"].create(
            {"name": "TOUR SDR Deposit Product", "type": "service"}
        )
        target_product = cls.env["product.product"].create(
            {"name": "TOUR SDR Payable Product", "type": "service"}
        )
        deposit_type = cls.env["school_deposit_type"].create(
            {
                "name": "TOUR SDR Type",
                "code": "TOURSDRT",
                "deposit_account_id": deposit_account.id,
                "realization_journal_id": general_journal.id,
                "source_product_ids": [(6, 0, source_product.ids)],
                "target_product_ids": [(6, 0, target_product.ids)],
            }
        )
        cls.deposit_type = deposit_type
        cls.deposit_account = deposit_account
        cls.source_product = source_product
        cls.target_product = target_product
        cls.contra_account = contra_account
        cls.general_journal = general_journal
        cls.sale_journal = sale_journal
        cls.receivable_account = receivable_account
        cls.admin = admin
        cls.invoice_type = cls.env["customer_invoice_type"].create(
            {
                "name": "TOUR SDR Invoice Type",
                "code": "/",
                "journal_id": sale_journal.id,
                "receivable_account_id": receivable_account.id,
            }
        )
        # ``global_use`` makes the reason selectable on every document;
        # without it the wizard radio does not offer the reason.
        cls.env["base.cancel_reason"].create(
            {
                "name": "TOUR SDR Cancel Reason",
                "code": "TOURSDRCR",
                "global_use": True,
            }
        )

        # ── Create tour: an open invoice and a posted deposit entry ──
        # The Customer Invoice dropdown only offers invoices in state
        # ``open``. Opening one through its own approval workflow would
        # book receivable entries that this tour does not exercise, so
        # the fixture sets the state directly -- the dropdown reads the
        # state and nothing else of the invoice.
        create_partner = cls._create_partner("CREATE")
        cls._create_invoice(create_partner).write({"state": "open"})
        deposit_move = cls.env["account.move"].create(
            {
                "journal_id": general_journal.id,
                "date": "2026-07-15",
                "ref": "TOUR SDR Deposit Entry",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "TOUR SDR Deposit Entry - Contra",
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
                            "name": "TOUR SDR Deposit Entry - Deposit",
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

        # ── Confirm tour: a Draft realization ──
        cls._create_realization("CONFIRM")

        # ── Reject tour: a realization Waiting for Approval ──
        reject = cls._create_realization("REJECT").with_user(admin)
        reject.action_confirm()
        reject.invalidate_cache()

        # ── Cancel tour: a Draft realization ──
        cls._create_realization("CANCEL")

        # ── Restart tour: a Cancelled realization ──
        cls._create_realization("RESTART").write({"state": "cancel"})

        # ── Compute Lines tour: a Draft realization without lines ──
        # The payable invoice is opened first, so that opening the
        # deposit invoice afterwards cannot realize anything.
        partner = cls._create_partner("COMPUTE")
        invoice = cls._open_invoice(partner, cls.target_product, 600.0)
        cls._open_invoice(partner, cls.source_product, 1000.0, deposit=True)
        cls._create_realization_of(partner, invoice)

        # ── Approve tour: a realization Waiting for Approval ──
        partner = cls._create_partner("APPROVE")
        invoice = cls._open_invoice(partner, cls.target_product, 600.0)
        cls._open_invoice(partner, cls.source_product, 1000.0, deposit=True)
        approve = cls._create_realization_of(partner, invoice)
        approve.action_compute_line()
        approve = approve.with_user(admin)
        approve.action_confirm()
        approve.invalidate_cache()

        # ── Automatic realization tour: the deposit is open, the payable
        # invoice waits for approval ──
        partner = cls._create_partner("AUTO")
        cls._open_invoice(partner, cls.source_product, 1000.0, deposit=True)
        auto_invoice = cls._create_invoice_with_line(partner, cls.target_product, 600.0)
        auto_invoice.with_user(admin).action_confirm()
        auto_invoice.invalidate_cache()

        # ── Cancel Done tour: a Done realization ──
        partner = cls._create_partner("CANCELDONE")
        invoice = cls._open_invoice(partner, cls.target_product, 600.0)
        cls._open_invoice(partner, cls.source_product, 1000.0, deposit=True)
        done = cls._create_realization_of(partner, invoice)
        done.action_compute_line()
        done.with_context(bypass_policy_check=True).action_done()

        # ── Reprocess tour: an open payable invoice and a later deposit ──
        partner = cls._create_partner("REPROCESS")
        cls._open_invoice(partner, cls.target_product, 600.0)
        cls._open_invoice(partner, cls.source_product, 1000.0, deposit=True)

    @classmethod
    def _create_partner(cls, suffix):
        """Create the dedicated partner of one tour scenario.

        :param suffix: scenario name appended to the partner name
        :return: the new ``res.partner`` record
        """
        return cls.env["res.partner"].create(
            {"name": "TOUR SDR Customer %s" % suffix, "is_company": True}
        )

    @classmethod
    def _create_invoice(cls, partner):
        """Create a draft customer invoice of the given partner.

        :param partner: the ``res.partner`` the invoice is billed to
        :return: the new ``customer_invoice`` record
        """
        return cls.env["customer_invoice"].create(
            {
                "type_id": cls.invoice_type.id,
                "partner_id": partner.id,
                "date": "2026-08-01",
                "date_due": "2026-09-01",
                "currency_id": cls.env.ref("base.USD").id,
                "journal_id": cls.sale_journal.id,
                "receivable_account_id": cls.receivable_account.id,
            }
        )

    @classmethod
    def _create_invoice_with_line(cls, partner, product, amount, deposit=False):
        """Create a draft customer invoice with one line.

        :param partner: the ``res.partner`` the invoice is billed to
        :param product: the ``product.product`` of the line
        :param amount: unit price of the line
        :param deposit: credit the deposit account instead of income
        :return: the new ``customer_invoice`` record
        """
        invoice = cls._create_invoice(partner)
        invoice.write({"pricelist_id": cls.env.ref("product.list0").id})
        account = cls.deposit_account if deposit else cls.contra_account
        cls.env["customer_invoice.line"].create(
            {
                "customer_invoice_id": invoice.id,
                "product_id": product.id,
                "name": product.name,
                "account_id": account.id,
                "uom_quantity": 1,
                "price_unit": amount,
            }
        )
        return invoice

    @classmethod
    def _open_invoice(cls, partner, product, amount, deposit=False):
        """Create a customer invoice and open it through its workflow.

        :param partner: the ``res.partner`` the invoice is billed to
        :param product: the ``product.product`` of the line
        :param amount: unit price of the line
        :param deposit: credit the deposit account instead of income
        :return: the opened ``customer_invoice`` record
        """
        invoice = cls._create_invoice_with_line(partner, product, amount, deposit)
        invoice = invoice.with_user(cls.admin)
        invoice.action_confirm()
        invoice.invalidate_cache()
        invoice.action_approve_approval()
        invoice.invalidate_cache()
        return invoice

    @classmethod
    def _create_realization_of(cls, partner, invoice):
        """Create a Draft realization of an existing invoice.

        :param partner: the ``res.partner`` who paid the deposit
        :param invoice: the open ``customer_invoice`` to settle
        :return: the new ``school_deposit_realization`` record
        """
        return cls.env["school_deposit_realization"].create(
            {
                "type_id": cls.deposit_type.id,
                "partner_id": partner.id,
                "customer_invoice_id": invoice.id,
                "journal_id": cls.general_journal.id,
                "date": "2026-08-10",
                "user_id": cls.admin.id,
            }
        )

    @classmethod
    def _create_realization(cls, suffix):
        """Create a Draft realization with its own partner and invoice.

        :param suffix: scenario name appended to the partner name
        :return: the new ``school_deposit_realization`` record
        """
        partner = cls._create_partner(suffix)
        invoice = cls._create_invoice(partner)
        return cls.env["school_deposit_realization"].create(
            {
                "type_id": cls.deposit_type.id,
                "partner_id": partner.id,
                "customer_invoice_id": invoice.id,
                "journal_id": cls.general_journal.id,
                "date": "2026-08-10",
                "user_id": cls.admin.id,
            }
        )

    def test_create(self):
        """Run the create tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/01-create.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_create",
            login="admin",
        )

    def test_confirm(self):
        """Run the confirm tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/02-confirm.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_confirm",
            login="admin",
        )

    def test_reject(self):
        """Run the reject tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/03-reject.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_reject",
            login="admin",
        )

    def test_cancel(self):
        """Run the cancel tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/04-cancel.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_cancel",
            login="admin",
        )

    def test_restart(self):
        """Run the restart tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/05-restart.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_restart",
            login="admin",
        )

    def test_compute_line(self):
        """Run the compute lines tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/06-compute-line.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_compute_line",
            login="admin",
        )

    def test_approve(self):
        """Run the approve tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/07-approve.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_approve",
            login="admin",
        )

    def test_auto_done(self):
        """Run the automatic realization tour on a customer invoice.

        IK: docs/school_deposit_realization/08-auto-done.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_auto_done",
            login="admin",
        )

    def test_cancel_done(self):
        """Run the cancel done tour for ``school_deposit_realization``.

        IK: docs/school_deposit_realization/09-cancel-done.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_realization_cancel_done",
            login="admin",
        )

    def test_reprocess(self):
        """Run the reprocess tour for ``school_deposit_reprocess``.

        IK: docs/school_deposit_reprocess/01-reprocess.md
        """
        self.start_tour(
            "/web",
            "ssi_school_deposit_school_deposit_reprocess_reprocess",
            login="admin",
        )
