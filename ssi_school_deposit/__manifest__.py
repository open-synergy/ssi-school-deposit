# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "School Deposit",
    "version": "14.0.1.1.0",
    "website": "https://simetri-sinergi.id",
    # pylint: disable=line-too-long
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia, Odoo Community Association (OCA)",  # noqa: B950
    # pylint: enable=line-too-long
    "contributors": [
        "Andhitia Rama <andhitia.r@gmail.com>",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "ssi_school",
        "ssi_customer_invoice",
        "ssi_accounting_entry_mixin",
        "ssi_company_currency_mixin",
        "ssi_master_data_mixin",
        "web_tour",
    ],
    "data": [
        "security/ir_module_category/school_deposit_realization.xml",
        "security/ir_module_category/school_deposit_forfeit.xml",
        "security/res_groups/school_deposit_type.xml",
        "security/res_groups/school_deposit_realization.xml",
        "security/res_groups/school_deposit_forfeit.xml",
        "security/ir_model_access/school_deposit_type.xml",
        "security/ir_model_access/school_deposit_realization.xml",
        "security/ir_model_access/school_deposit_forfeit.xml",
        "security/ir_model_access/school_deposit_reprocess.xml",
        "security/ir_rule/school_deposit_realization.xml",
        "security/ir_rule/school_deposit_forfeit.xml",
        "ir_sequence/school_deposit_realization.xml",
        "ir_sequence/school_deposit_forfeit.xml",
        "sequence_template/school_deposit_realization.xml",
        "sequence_template/school_deposit_forfeit.xml",
        "approval_template/school_deposit_realization.xml",
        "approval_template/school_deposit_forfeit.xml",
        "policy_template/school_deposit_realization.xml",
        "policy_template/school_deposit_forfeit.xml",
        "menu.xml",
        "views/school_deposit_type.xml",
        "wizards/school_deposit_reprocess.xml",
        "views/school_deposit_realization.xml",
        "views/school_deposit_forfeit.xml",
        "views/school_enrollment.xml",
        "views/assets.xml",
    ],
}
