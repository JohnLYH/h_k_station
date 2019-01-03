# -*- coding: utf-8 -*-
{
    'name': "vue_template_manager",

    'summary': """
    富能通vue资源管理""",

    'description': """
        富能通vue资源管理,对vue资源进行管理
    """,

    'author': "funenc",
    'website': "http://www.funenc.com",
    'category': 'funenc',
    'version': '0.1',
    'depends': ['base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml'
    ],
    'application': True
}