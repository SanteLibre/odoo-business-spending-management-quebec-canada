# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Tip fees hr expense quebec canada',
    'version': '0.1',
    'category': 'Human Resources',
    'description': """
Implement tips in hr expense for human resources
================================================

TODO
""",
    'depends': ['hr_expense'],
    'data': [
        'views/hr_expense_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
