# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


# Overrides the entry contract of the realization line so a line whose
# deposit was recorded in another operating unit is booked through the
# Interunit Account instead of straight on the deposit account.
class SchoolDepositRealizationLine(models.Model):
    _name = "school_deposit_realization_line"
    _inherit = ["school_deposit_realization_line"]

    def _is_school_deposit_interunit(self):
        """Tell whether the line uses a deposit of another unit.

        True when both the realization and the source journal item
        have an operating unit and the two differ.

        :return: ``True`` for an interunit line
        """
        self.ensure_one()
        source_ou = self.source_move_line_id.operating_unit_id
        target_ou = self.realization_id.operating_unit_id
        return bool(source_ou and target_ou and source_ou != target_ou)

    def _create_school_deposit_source_entry(self):
        """Book the line, through the Interunit Account if needed.

        Same operating unit: the base behavior. Otherwise (a) the
        main journal debits the Interunit Account instead of the
        deposit account; (b) the additional journal of the source
        unit debits the deposit account and credits the Interunit
        Account. The deposit debit of the additional journal is saved
        to ``move_line_id``, so the base reconciliation matches it
        with the source journal item.

        :raises UserError: when the Type has no Interunit Account
        :return: the debit ``account.move.line`` to reconcile with
            the source journal item
        """
        self.ensure_one()
        if not self._is_school_deposit_interunit():
            return super()._create_school_deposit_source_entry()
        realization = self.realization_id
        interunit_account = realization.type_id.interunit_account_id
        if not interunit_account:
            error_message = """
Document Type: %s
Context: Book realization line
Database ID: %s
Problem: The Type has no Interunit Account
Solution: Fill in the Interunit Account of the Type '%s'
""" % (
                self._description,
                self.id,
                realization.type_id.display_name,
            )
            raise UserError(_(error_message))
        MoveLine = self.env["account.move.line"].with_context(check_move_validity=False)
        vals = self._prepare_standard_ml()
        # (a) main journal: debit the Interunit Account
        MoveLine.create(dict(vals, account_id=interunit_account.id))
        # (b) additional journal of the source unit
        move = realization._get_school_deposit_interunit_move(
            self.source_move_line_id.operating_unit_id
        )
        deposit_ml = MoveLine.create(dict(vals, move_id=move.id))
        MoveLine.create(
            dict(
                vals,
                move_id=move.id,
                account_id=interunit_account.id,
                debit=vals["credit"],
                credit=vals["debit"],
                amount_currency=-vals["amount_currency"],
            )
        )
        self.write({"move_line_id": deposit_ml.id})
        return deposit_ml
