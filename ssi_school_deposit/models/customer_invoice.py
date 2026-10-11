# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class CustomerInvoice(models.Model):
    _inherit = "customer_invoice"

    def _get_school_deposit_reserved_amount(self):
        """Return the amount deposit must leave on this invoice.

        Public hook: glue modules (fee waiver, scholarship) override
        it to add the scheduled deduction. This module reserves
        nothing.

        :return: reserved amount, ``0.0`` here
        """
        self.ensure_one()
        return 0.0

    @ssi_decorator.post_open_action()
    def _90_realize_school_deposit(self):
        """Realize every auto-realize deposit type payable here.

        :return: nothing
        """
        self.ensure_one()
        types = self.env["school_deposit_type"].search([("auto_realize", "=", True)])
        self._realize_school_deposit(types)

    def _realize_school_deposit(self, types):
        """Create, compute and finish one realization per matching type.

        A failure leaves the realization in draft and is reported on
        the invoice chatter; the invoice itself stays open.

        :param types: ``school_deposit_type`` records to realize
        :return: ``True``
        """
        self.ensure_one()
        if self.state != "open":
            return True
        Realization = self.env["school_deposit_realization"].sudo()
        products = self.line_ids.mapped("product_id")
        for deposit_type in types:
            if not (deposit_type.target_product_ids & products):
                continue
            realization = Realization.create(
                {
                    "type_id": deposit_type.id,
                    "partner_id": self.partner_id.id,
                    "customer_invoice_id": self.id,
                    "journal_id": deposit_type.realization_journal_id.id,
                }
            )
            realization.action_compute_line()
            if not realization.line_ids:
                realization.unlink()
                continue
            try:
                with self.env.cr.savepoint():
                    realization.with_context(bypass_policy_check=True).action_done()
            except (UserError, ValidationError) as exc:
                self.invalidate_cache()
                msg = (
                    "Deposit realization %s could not be finished and was "
                    "left in draft: %s"
                ) % (realization.display_name, exc.args[0] if exc.args else "")
                self.message_post(
                    body=_(msg),
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )
        return True
