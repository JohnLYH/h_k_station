# -*- coding: utf-8 -*-
from odoo import http

# class MaintenancePlan(http.Controller):
#     @http.route('/maintenance_plan/maintenance_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/maintenance_plan/maintenance_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('maintenance_plan.listing', {
#             'root': '/maintenance_plan/maintenance_plan',
#             'objects': http.request.env['maintenance_plan.maintenance_plan'].search([]),
#         })

#     @http.route('/maintenance_plan/maintenance_plan/objects/<model("maintenance_plan.maintenance_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('maintenance_plan.object', {
#             'object': obj
#         })