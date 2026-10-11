# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SchoolEnrollment(models.Model):
    _inherit = "school_enrollment"

    amount_deposit_realized = fields.Monetary(
        string="Deposit Realized",
        compute="_compute_amount_deduction",
        store=True,
        compute_sudo=True,
        currency_field="currency_id",
        help="Part of the settled amount that came from finished "
        "school deposit realizations. It is not a deduction and is "
        "left out of Other Credits.",
    )

    @api.depends(
        "payment_term_ids.customer_invoice_id.receivable_move_line_id."
        "matched_credit_ids.credit_move_id",
    )
    def _compute_amount_deduction(self):
        """Subtract the deposit part from ``amount_other_credit``.

        Deposit is not a deduction, so ``_get_amount_deduction`` and
        ``_get_amount_deducted`` are untouched. Sums the partial
        reconciliations whose credit side is the receivable item of a
        finished deposit realization.

        :return: nothing; assigns ``amount_deposit_realized``
        """
        super()._compute_amount_deduction()
        Realization = self.env["school_deposit_realization"]
        for record in self:
            round_ = record.currency_id.round
            counted_terms = record.payment_term_ids.filtered(
                lambda term: term.state not in ("cancelled", "voided")
            )
            partials = counted_terms.mapped(
                "customer_invoice_id.receivable_move_line_id.matched_credit_ids"
            )
            credit_lines = partials.mapped("credit_move_id")
            realizations = Realization.sudo().search(
                [
                    ("state", "=", "done"),
                    ("receivable_move_line_id", "in", credit_lines.ids),
                ]
            )
            deposit_lines = realizations.mapped("receivable_move_line_id")
            amount = sum(
                partials.filtered(lambda p: p.credit_move_id in deposit_lines).mapped(
                    "amount"
                )
            )
            amount = round_(amount)
            record.amount_deposit_realized = amount
            record.amount_other_credit = round_(record.amount_other_credit - amount)
