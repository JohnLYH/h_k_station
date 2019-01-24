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
    'depends': ['base', 'web', 'layui_theme', 'odoo_groups_manage'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/user_management/employees_management.xml',
        'views/insert.xml',
        'views/user_management/import_date.xml',
        'views/rights_management/rights_management_clinet.xml',
        'views/rights_management/per_information.xml',
        'security/add_category.xml',
        'security/catagory_menu.xml',
        'security/category_group.xml',
        'views/send_email/email-list.xml',
        'views/user_management/create_new_rec.xml',
        'views/user_management/create_new_record.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'qweb': [
        'static/xml/*.xml'
    ],
    'application': True
}