odoo.define("ssi_school_deposit.school_deposit_forfeit_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // Shared navigation block, Flow step 1 of every IK in
    // docs/school_deposit_forfeit/: "Open the School > School Deposit >
    // Deposit Forfeits menu." App root > School Deposit section > leaf,
    // the same 3-level shape as the Deposit Realizations menu.
    function openForfeitsList() {
        return [
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
        ];
    }

    // The search text is the dedicated Partner name of the scenario. Each
    // partner owns exactly one forfeit, and no scenario name is a prefix of
    // another, so the row is unique in the list.
    function openRecord(searchText) {
        return [
            {
                content: "Open the record",
                trigger: ".o_data_row:contains(" + searchText + ") .o_data_cell:first",
            },
            {
                content: "Form is open",
                trigger: ".o_form_view",
                extra_trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ];
    }

    function confirmDialog() {
        return [
            {
                content: "Confirm the dialog",
                trigger: ".modal-footer button.btn-primary",
                in_modal: true,
            },
        ];
    }

    // IK: docs/school_deposit_forfeit/01-create.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_create",
        {test: true, url: "/web"},
        [].concat(openForfeitsList(), [
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
                content: "Select the Type",
                trigger: ".o_field_many2one[name='type_id'] input",
                run: "text TOUR SDF Type",
            },
            {
                content: "Pick the Type from the dropdown",
                trigger: ".ui-autocomplete .ui-menu-item a:contains(TOUR SDF Type)",
                in_modal: false,
            },
            {
                content: "Select the Partner",
                trigger: ".o_field_many2one[name='partner_id'] input",
                run: "text TOUR SDF Customer CREATE",
            },
            {
                content: "Pick the Partner from the dropdown",
                trigger:
                    ".ui-autocomplete .ui-menu-item a:contains(TOUR SDF Customer CREATE)",
                in_modal: false,
            },
            {
                content: "Open the Accounting tab",
                trigger: ".o_notebook .nav-link:contains(Accounting)",
                extra_trigger: ".o_form_view.o_form_editable",
            },
            {
                content: "Journal was defaulted from the Type",
                trigger: ".o_field_many2one[name='journal_id'] input",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
            {
                content: "Open the Lines tab",
                trigger: ".o_notebook .nav-link:contains(Lines)",
            },
            {
                content: "Add a Line",
                trigger:
                    ".o_field_widget[name='line_ids'] .o_field_x2many_list_row_add a",
            },
            {
                content: "Open the Source Journal Item dropdown",
                trigger:
                    ".o_selected_row .o_field_widget[name='source_move_line_id'] input",
                run: "click",
            },
            {
                // Scope to the VISIBLE dropdown and drop the "Start
                // typing..." placeholder row, so a stale closed dropdown
                // earlier in the DOM is never picked.
                content: "Pick the only Source Journal Item",
                trigger:
                    ".ui-autocomplete:visible .ui-menu-item:not(.o_m2o_start_typing) a:eq(0)",
                in_modal: false,
            },
            {
                // Monetary's edit-mode root is a wrapper div; the real
                // <input> sits inside it.
                content: "Fill in the Amount",
                trigger: ".o_selected_row .o_field_widget[name='amount'] input",
                run: "text 100000",
            },
            {
                content: "Commit the Line",
                trigger: ".o_field_widget[name='line_ids']",
                run: "click",
            },
            {
                content: "Save the record",
                trigger: ".o_form_button_save",
            },
            {
                content: "Record is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
            {
                content: "Status is Draft",
                trigger:
                    ".o_statusbar_status .o_arrow_button[data-value='draft'].btn-primary",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ])
    );

    // IK: docs/school_deposit_forfeit/02-compute-line.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_compute_line",
        {test: true, url: "/web"},
        [].concat(openForfeitsList(), openRecord("TOUR SDF Customer COMPUTE"), [
            {
                content: "Click the Compute Lines button",
                trigger: ".o_statusbar_buttons button[name='action_compute_line']",
                extra_trigger: ".o_form_view",
            },
            {
                content: "Open the Lines tab",
                trigger: ".o_notebook .nav-link:contains(Lines)",
                extra_trigger: ".o_form_view",
            },
            {
                // Post-Condition: a line was computed from the deposit.
                // The fixture forfeit starts without lines, so a row can
                // only appear once the computation ran.
                content: "A line is listed",
                trigger: ".o_field_one2many[name='line_ids'] .o_data_row",
                run: function () {
                    // Assertion only; do not trigger the default click.
                },
            },
        ])
    );

    // IK: docs/school_deposit_forfeit/03-confirm.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_confirm",
        {test: true, url: "/web"},
        [].concat(
            openForfeitsList(),
            openRecord("TOUR SDF Customer CONFIRM"),
            [
                {
                    content: "Click the Confirm button",
                    trigger: ".o_statusbar_buttons button[name='action_confirm']",
                    extra_trigger: ".o_form_view",
                },
            ],
            confirmDialog(),
            [
                {
                    content: "Status is Waiting for Approval",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='confirm'].btn-primary",
                    extra_trigger: "body:not(:has(.modal))",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        )
    );

    // IK: docs/school_deposit_forfeit/04-approve.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_approve",
        {test: true, url: "/web"},
        [].concat(
            openForfeitsList(),
            openRecord("TOUR SDF Customer APPROVE"),
            [
                {
                    content: "Click the Approve button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_approve_approval']",
                    extra_trigger: ".o_form_view",
                },
            ],
            confirmDialog(),
            [
                {
                    content: "Status is Done",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='done'].btn-primary",
                    extra_trigger: "body:not(:has(.modal))",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        )
    );

    // IK: docs/school_deposit_forfeit/05-reject.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_reject",
        {test: true, url: "/web"},
        [].concat(
            openForfeitsList(),
            openRecord("TOUR SDF Customer REJECT"),
            [
                {
                    content: "Click the Reject button",
                    trigger:
                        ".o_statusbar_buttons button[name='action_reject_approval']",
                    extra_trigger: ".o_form_view",
                },
            ],
            confirmDialog(),
            [
                {
                    content: "Status is Rejected",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='reject'].btn-primary",
                    extra_trigger: "body:not(:has(.modal))",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        )
    );

    // IK: docs/school_deposit_forfeit/06-cancel.md
    tour.register(
        "ssi_school_deposit_school_deposit_forfeit_cancel",
        {test: true, url: "/web"},
        [].concat(
            openForfeitsList(),
            openRecord("TOUR SDF Customer CANCEL"),
            [
                // The Cancel button is a `type="action"` button, so its
                // `name` attribute is a numeric action id in the DOM;
                // target it by label instead.
                {
                    content: "Click the Cancel button",
                    trigger: ".o_statusbar_buttons button:enabled:contains('Cancel')",
                    extra_trigger: ".o_form_view",
                },
                {
                    // The wizard renders cancel_reason_id with
                    // widget="radio" -- select the matching radio item by
                    // its label text. 14.0: do NOT prefix the trigger with
                    // `.modal`.
                    content: "Select the Cancellation Reason",
                    trigger:
                        ".o_field_widget[name='cancel_reason_id'] .o_radio_item:contains(TOUR SDF Cancel Reason) input",
                    in_modal: true,
                },
                {
                    content: "Confirm the wizard",
                    trigger: ".modal-footer button[name='action_confirm']",
                },
            ],
            confirmDialog(),
            [
                {
                    content: "Status is Cancelled",
                    trigger:
                        ".o_statusbar_status .o_arrow_button[data-value='cancel'].btn-primary",
                    extra_trigger: "body:not(:has(.modal))",
                    run: function () {
                        // Assertion only; do not trigger the default click.
                    },
                },
            ]
        )
    );
});
