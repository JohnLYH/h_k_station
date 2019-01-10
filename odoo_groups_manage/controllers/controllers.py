# -*- coding: utf-8 -*-
from odoo import http

# class OdooGroupsManage(http.Controller):
#     @http.route('/odoo_groups_manage/odoo_groups_manage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_groups_manage/odoo_groups_manage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_groups_manage.listing', {
#             'root': '/odoo_groups_manage/odoo_groups_manage',
#             'objects': http.request.env['odoo_groups_manage.odoo_groups_manage'].search([]),
#         })

#     @http.route('/odoo_groups_manage/odoo_groups_manage/objects/<model("odoo_groups_manage.odoo_groups_manage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_groups_manage.object', {
#             'object': obj
#         })