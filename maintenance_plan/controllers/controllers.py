# -*- coding: utf-8 -*-
from odoo import http


class MaintenancePlan(http.Controller):
    @http.route('/maintenance_plan/export_work_order', auth='user')
    def export_work_order(self, **kw):
        return "Hello, world"

    @http.route('/maintenance_plan/approval_management', auth='none')
    def approval_management(self, **kw):
        print(kw)
        # return {
        #     'type': 'ir.actions.client',
        #     'name': '工单审批详情',
        #     'tag': 'maintenance_plan.maintenance_plan_approval_management',
        # }
        return http.request.render('maintenance_plan.maintenance_plan_approval_management', {})
