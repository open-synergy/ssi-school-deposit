import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-school-deposit",
    description="Meta package for open-synergy-ssi-school-deposit Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_school_deposit',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
