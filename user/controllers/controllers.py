# -*- coding: utf-8 -*-
from odoo import http

# class User(http.Controller):
#     @http.route('/user/user/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/user/user/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('user.listing', {
#             'root': '/user/user',
#             'objects': http.request.env['user.user'].search([]),
#         })

#     @http.route('/user/user/objects/<model("user.user"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('user.object', {
#             'object': obj
#         })