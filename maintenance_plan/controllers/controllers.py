# -*- coding: utf-8 -*-
from odoo import http


class MaintenancePlan(http.Controller):
    @http.route('/maintenance_plan/export_work_order', auth='user')
    def export_work_order(self, **kw):
        return "Hello, world"
