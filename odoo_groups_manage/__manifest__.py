# -*- coding: utf-8 -*-
{
    'name': "odoo_groups_manage",

    'summary': """
        odoo权限管理模块""",

    'description': """
        odoo权限管理模块，需要依赖与vue_template和layui_theme模块
    """,

    'author': "funenc",
    'website': "http://www.funenc.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'layui_theme', 'vue_template_manager'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/add_category.xml',
        'views/depend_static.xml',
        'views/res_groups_view.xml',
    ],
    # only loaded in demonstration mode
    'application': True
}
