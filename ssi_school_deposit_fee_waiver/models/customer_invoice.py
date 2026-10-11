# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CustomerInvoice(models.Model):
    _inherit = "customer_invoice"

    def _get_school_deposit_reserved_amount(self):
        """Reserve the scheduled fee waiver deduction of this invoice.

        Adds the planned amount of every scheduled fee waiver
        schedule line whose payment term, enrollment or admission,
        was billed by this invoice, so a deposit realization leaves
        room for the deduction and only settles the rest.

        :return: reserved amount of the base hook plus the scheduled
            fee waiver amount
        """
        self.ensure_one()
        res = super()._get_school_deposit_reserved_amount()
        schedules = (
            self.env["school_fee_waiver_schedule"]
            .sudo()
            .search(
                [
                    ("state", "=", "scheduled"),
                    ("waiver_id.state", "in", ("open", "done")),
                    "|",
                    ("payment_term_id.customer_invoice_id", "=", self.id),
                    ("admission_payment_term_id.customer_invoice_id", "=", self.id),
                ]
            )
        )
        return res + sum(schedules.mapped("amount_planned"))
