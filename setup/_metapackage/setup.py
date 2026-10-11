import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-deposit",
    description="Meta package for open-synergy-ssi-school-deposit Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_school_deposit',
        'odoo14-addon-ssi_school_deposit_admission',
        'odoo14-addon-ssi_school_deposit_fee_waiver',
        'odoo14-addon-ssi_school_deposit_operating_unit',
        'odoo14-addon-ssi_school_deposit_scholarship',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
