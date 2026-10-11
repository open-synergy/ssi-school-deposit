odoo.define("ssi_school_deposit.school_deposit_type_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Flow step 1 of docs/school_deposit_type/01-create.md: "Open the
    // School > Configuration > School Deposit > School Deposit Types
    // menu." The "School Deposit" group
    // (menu_school_deposit_configuration) has children and is level 3, so
    // it is rendered as a non-clickable dropdown header without
    // data-menu-xmlid -- skip straight to the leaf item.
    function openMenuSteps() {
        return [
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the School app",
                trigger: '.o_app[data-menu-xmlid="ssi_school.menu_school_root"]',
            },
            {
                content: "Open the Configuration menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school.menu_school_configuration"]',
            },
            {
                content: "Open the School Deposit Types menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_school_deposit.school_deposit_type_menu"]',
            },
            {
                content: "School Deposit Types list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(School Deposit Types)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                    return true;
                },
            },
        ];
    }

    // IK: docs/school_deposit_type/01-create.md
    tour.register(
        "ssi_school_deposit_school_deposit_type_create",
        {test: true, url: "/web"},
        [
            ...openMenuSteps(),
            {
                content: "Click New",
                trigger: ".o_list_button_add",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Form is open in edit mode",
                trigger: ".o_form_view.o_form_editable",
                run: function () {
                    // Assertion only.
                    return true;
                },
            },
            {
                content: "Fill in Name",
                trigger: ".o_field_widget[name='name']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Tour School Deposit Type New",
            },
            {
                content: "Fill in Code",
                trigger: ".o_field_widget[name='code']",
                run: "text TOUR-SDT-NEW",
            },
            {
                content: "Select the Deposit Account",
                trigger: ".o_field_many2one[name='deposit_account_id'] input",
                run: "text TOUR SDT Deposit Account",
            },
            {
                content: "Pick the Deposit Account from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR SDT Deposit Account)",
                in_modal: false,
            },
            {
                content: "Select the Realization Journal",
                trigger: ".o_field_many2one[name='realization_journal_id'] input",
                run: "text TOUR SDT Journal",
            },
            {
                content: "Pick the Realization Journal from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a:contains(TOUR SDT Journal)",
                in_modal: false,
            },
            {
                content: "Open the Products tab",
                trigger: ".o_notebook .nav-link:contains(Products)",
            },
            {
                content: "Select a Deposit Product",
                trigger: ".o_field_many2manytags[name='source_product_ids'] input",
                run: "text TOUR SDT Deposit Product",
            },
            {
                content: "Pick the Deposit Product from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR SDT Deposit Product)",
                in_modal: false,
            },
            {
                content: "Select a Payable Product",
                trigger: ".o_field_many2manytags[name='target_product_ids'] input",
                run: "text TOUR SDT Payable Product",
            },
            {
                content: "Pick the Payable Product from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR SDT Payable Product)",
                in_modal: false,
            },
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only.
                    return true;
                },
            },
        ]
    );
});
