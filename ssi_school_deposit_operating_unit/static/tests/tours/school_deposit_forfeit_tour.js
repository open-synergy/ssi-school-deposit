// Copyright 2026 OpenSynergy Indonesia
// Copyright 2026 PT. Simetri Sinergi Indonesia
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define("ssi_school_deposit_operating_unit.school_deposit_forfeit_tour", function (
    require
) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/school_deposit_forfeit/01-create.md (E1 delta -- Additional Fields)
    // Navigation (open menu -> New) is taken from the base IK
    // ssi_school_deposit docs/school_deposit_forfeit/01-create.md Flow steps 1-2
    // (skill odoo-development-ui-test scope-and-boundaries.md section 1,
    // backing base IK + delta IK). The delta assertion is this module's
    // own: the Operating Unit field is visible on the create form AND
    // already filled with the acting user's default operating unit, for a
    // user in the operating_unit.group_multi_operating_unit group. The
    // tour stops there; it does not fill the remaining fields or save
    // (E1 delta-only).
    tour.register(
        "ssi_school_deposit_operating_unit_school_deposit_forfeit_create",
        {test: true, url: "/web"},
        [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the School Deposit menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_deposit.menu_school_deposit"]',
            },
            {
                content: "Open the Deposit Forfeits menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_deposit.school_deposit_forfeit_menu"]',
            },
            {
                // Gate: wait for the Deposit Forfeits action itself to be
                // mounted, not just any list view left over from the
                // landing action.
                content: "Deposit Forfeits list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(School Deposit Forfeits)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
            {
                content: "Click New",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
            {
                // Delta assertion: visible, editable (Draft) and filled
                // with a default value (not `.o_field_empty`).
                content:
                    "Operating Unit field is visible, editable, and filled with a default",
                trigger:
                    ".o_form_view.o_form_editable " +
                    ".o_field_widget.o_field_many2one[name='operating_unit_id']" +
                    ":not(.o_field_empty)",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ]
    );
});
