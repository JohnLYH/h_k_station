# -*- coding: utf-8 -*-
{
    'name': "other_equipment",

    'summary': """
        其他设备管理模块""",

    'description': """
        mtr港铁其他设备管理模块
    """,

    'author': "funenc",
    'website': "http://www.funenc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'mtr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'layui_theme', 'maintenance_plan'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/tool_management.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/xml/*.xml'],
    'application': True
}