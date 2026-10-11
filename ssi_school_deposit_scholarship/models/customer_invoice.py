# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class CustomerInvoice(models.Model):
    _inherit = "customer_invoice"

    def _get_school_deposit_reserved_amount(self):
        """Reserve the scheduled scholarship deduction of this invoice.

        Adds the planned amount of every scheduled scholarship award
        schedule line billed by this invoice, whose award is open or
        done, so a deposit realization leaves room for the deduction
        and only settles the rest.

        :return: reserved amount of the base hook plus the scheduled
            scholarship amount
        """
        self.ensure_one()
        res = super()._get_school_deposit_reserved_amount()
        schedules = (
            self.env["school_scholarship_award_schedule"]
            .sudo()
            .search(
                [
                    ("customer_invoice_id", "=", self.id),
                    ("state", "=", "scheduled"),
                    ("award_id.state", "in", ("open", "done")),
                ]
            )
        )
        return res + sum(schedules.mapped("amount_planned"))
