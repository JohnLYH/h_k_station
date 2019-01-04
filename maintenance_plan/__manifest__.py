# -*- coding: utf-8 -*-
{
    'name': "maintenance_plan",

    'summary': """
        维修计划管理模块""",

    'description': """
        mtr港铁维修计划管理模块
    """,

    'author': "funenc",
    'website': "http://www.funenc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'mtr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'layui_theme', 'vue_template_manager'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/templates.xml',
        'views/config/config_view.xml',
        'views/maintenance_plan/maintenance_plan_view.xml',
        'views/device_management/device_management_view.xml',
        'views/wok_order/work_order_view.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': ['static/xml/*.xml'],
    'application': True
}
