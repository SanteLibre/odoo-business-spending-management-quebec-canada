{
    'name': 'Helpdesk res partner team',
    'category': 'Website',
    'summary': 'Support res partner team',
    'version': '12.0.0.0',
    'description': """
Helpdesk res partner team
=========================
Add employee
    """,
    'depends': [
        'helpdesk_service_call',
        'hr',
        'auth_signup',
    ],
    'data': [
        'view/helpdesk_ticket_view.xml',
    ],
    'qweb': [],
    'installable': True,
    'auto_install': False,
}
