# -*- coding: utf-8 -*-
from odoo import http

# class VueTemplateManager(http.Controller):
#     @http.route('/vue_template_manager/vue_template_manager/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vue_template_manager/vue_template_manager/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vue_template_manager.listing', {
#             'root': '/vue_template_manager/vue_template_manager',
#             'objects': http.request.env['vue_template_manager.vue_template_manager'].search([]),
#         })

#     @http.route('/vue_template_manager/vue_template_manager/objects/<model("vue_template_manager.vue_template_manager"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vue_template_manager.object', {
#             'object': obj
#         })