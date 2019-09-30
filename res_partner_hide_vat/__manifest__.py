# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hide VAT',
    'version': '1.0.0',
    'author': "MathBenTech",
    'website': 'https://mathben.tech',
    'license': 'AGPL-3',
    'category': 'Hidden',
    'summary': 'Hide VAT in RES.Partner',
    'description': """
Hide VAT
========
Some country, provinces or state doesn't need VAT, so ignore it.
""",
    'depends': ['base'],
    'data': [
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
