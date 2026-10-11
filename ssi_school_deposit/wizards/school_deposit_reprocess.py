# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SchoolDepositReprocess(models.TransientModel):
    """Realizes deposit again on invoices that are already open.

    An invoice opened before the deposit was recorded is not settled
    by the automatic realization. This wizard runs the same
    realization for the open invoices of the chosen deposit types,
    optionally limited to some partners.
    """

    _name = "school_deposit_reprocess"
    _description = "School Deposit Reprocess"

    type_ids = fields.Many2many(
        string="Types",
        comodel_name="school_deposit_type",
        relation="school_deposit_reprocess_type_rel",
        column1="wizard_id",
        column2="type_id",
        required=True,
        help="Deposit types to realize again.",
    )
    partner_ids = fields.Many2many(
        string="Partners",
        comodel_name="res.partner",
        relation="school_deposit_reprocess_partner_rel",
        column1="wizard_id",
        column2="partner_id",
        help="Limit the run to these partners. Leave empty for all.",
    )

    def action_reprocess(self):
        """Realize deposit on every matching open invoice.

        :return: an action closing the dialog
        """
        for record in self.sudo():
            record._reprocess()
        return {"type": "ir.actions.act_window_close"}

    def _reprocess(self):
        """Run the realization of the chosen types on open invoices.

        :return: nothing
        """
        self.ensure_one()
        domain = [
            ("state", "=", "open"),
            (
                "line_ids.product_id",
                "in",
                self.type_ids.mapped("target_product_ids").ids,
            ),
        ]
        if self.partner_ids:
            domain.append(("partner_id", "in", self.partner_ids.ids))
        invoices = self.env["customer_invoice"].search(domain, order="date, id")
        for invoice in invoices:
            invoice._realize_school_deposit(self.type_ids)
