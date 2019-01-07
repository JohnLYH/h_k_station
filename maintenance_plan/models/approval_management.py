from odoo import models, fields, api

STATUS = [
    ('have_passed', '已通過'), ('pending_approval', '待審批'), ('rejected', '已拒絕')
]


class ApprovalManagement(models.Model):
    '''工單審批管理'''
    _name = 'maintenance_plan.approval'
    _description = '審批管理'

    num = fields.Many2one('maintenance_plan.maintenance.plan', '工單')
    work_order = fields.Char('工單編號', compute='_get_work_order')
    # TODO: 提交人
    submitter = fields.Many2one('user.employees_get', '提交人')
    submit_time = fields.Datetime('提交時間')
    # TODO: 群組
    # TODO: 審批人
    approver = fields.Many2one('user.employees_get', '審批人')
    status = fields.Selection(STATUS, string='審批狀態')
    approval_time = fields.Datetime('審批時間')
    work_order_description = fields.Char('工單描述:', compute='_get_work_order')
    plan_end_time = fields.Char('規定完成時間:', compute='_get_work_order')
    actual_start_time = fields.Char('實際開始時間:', compute='_get_work_order')
    actual_end_time = fields.Char('實際結算時間:', compute='_get_work_order')

    @api.depends('num', 'work_order_description', 'plan_end_time', 'actual_start_time', 'actual_end_time')
    def _get_work_order(self):
        for record in self:
            record.work_order = record.num.num
            record.actual_end_time = record.num.actual_end_time
            record.actual_start_time = record.num.actual_start_time
            record.plan_end_time = record.num.plan_end_time
            record.work_order_description = record.num.work_order_description

    @api.multi
    def _go_to_details(self):
        print("李容成")
