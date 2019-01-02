# -*- coding: utf-8 -*-
{
    'name': "user",

    'summary': """
        用户管理模块""",

    'description': """
        mtr港铁项目用户管理模块
    """,

    'author': "funenc",
    'website': "http://www.funenc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'mtr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'layui_theme'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/user_management/employees_management.xml',
        'views/insert.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/xml/*.xml',
    ],
    'application': True
}