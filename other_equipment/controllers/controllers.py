# -*- coding: utf-8 -*-
from odoo import http

# class OtherEquipment(http.Controller):
#     @http.route('/other_equipment/other_equipment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/other_equipment/other_equipment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('other_equipment.listing', {
#             'root': '/other_equipment/other_equipment',
#             'objects': http.request.env['other_equipment.other_equipment'].search([]),
#         })

#     @http.route('/other_equipment/other_equipment/objects/<model("other_equipment.other_equipment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('other_equipment.object', {
#             'object': obj
#         })