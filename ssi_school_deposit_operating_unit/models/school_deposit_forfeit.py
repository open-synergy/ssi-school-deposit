# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError

from odoo.addons.ssi_decorator import ssi_decorator


# Gives the forfeit a single operating unit and books its journal
# there. A deposit is always forfeited in the unit that recorded it, so
# finishing is refused when a line's source journal item belongs to
# another unit; there is no interunit forfeit.
class SchoolDepositForfeit(models.Model):
    _name = "school_deposit_forfeit"
    _inherit = [
        "school_deposit_forfeit",
        "mixin.single_operating_unit",
    ]

    def _prepare_standard_move(self):
        """Add this document's operating unit to the ``account.move``.

        :return: dict of ``account.move`` values
        """
        res = super()._prepare_standard_move()
        res["operating_unit_id"] = self.operating_unit_id.id
        return res

    @ssi_decorator.pre_done_check()
    def _03_check_operating_unit(self):
        """Reject lines whose source belongs to another unit.

        Skipped for a line or a document without an operating unit.

        :raises UserError: when the operating unit of a line's source
            journal item differs from the document's
        """
        self.ensure_one()
        if not self.operating_unit_id:
            return
        for line in self.line_ids:
            source_ou = line.source_move_line_id.operating_unit_id
            if source_ou and source_ou != self.operating_unit_id:
                error_message = """
Document Type: %s
Context: Finish document
Database ID: %s
Problem: Journal item '%s' belongs to Operating Unit '%s', not to '%s' of \
this document
Solution: Forfeit it in the Operating Unit that recorded the deposit
""" % (
                    self._description,
                    self.id,
                    line.source_move_line_id.display_name,
                    source_ou.display_name,
                    self.operating_unit_id.display_name,
                )
                raise UserError(_(error_message))
