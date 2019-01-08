from odoo import models, fields, api

STATUS = [
    ('have_passed', '已通過'), ('pending_approval', '待審批'), ('rejected', '已拒絕')
]


class ApprovalManagement(models.Model):
    '''工單審批管理'''
    _name = 'maintenance_plan.approval'
    _description = '審批管理'

    maintenance_plan_id = fields.Many2one('maintenance_plan.maintenance.plan', '工單')
    work_order = fields.Char('工單編號', compute='_get_maintenance_plan_id')
    submitter = fields.Many2one('res.users', '提交人')
    submit_time = fields.Datetime('提交時間')
    # TODO: 群組
    approver = fields.Many2one('res.users', '審批人')
    status = fields.Selection(STATUS, string='審批狀態')
    approval_time = fields.Datetime('審批時間')
    work_order_description = fields.Char('工單描述:', compute='_get_work_order')
    plan_end_time = fields.Char('規定完成時間:', compute='_get_work_order')
    actual_start_time = fields.Char('實際開始時間:', compute='_get_work_order')
    actual_end_time = fields.Char('實際結算時間:', compute='_get_work_order')

    @api.depends('maintenance_plan_id')
    def _get_maintenance_plan_id(self):
        for record in self:
            if record.maintenance_plan_id:
                record.work_order = record.maintenance_plan_id.num
                record.actual_end_time = record.maintenance_plan_id.actual_end_time
                record.actual_start_time = record.maintenance_plan_id.actual_start_time
                record.plan_end_time = record.maintenance_plan_id.plan_end_time
                record.work_order_description = record.maintenance_plan_id.work_order_description


class ReferenceExaminationApproval(models.Model):
    '''參考資料審批'''
    _name = 'maintenance_plan.data.approval'
    _description = '參考資料審批'

    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    submitter = fields.Many2one('user.employees_get', '提交人')
    submit_time = fields.Datetime('提交時間')
    approver = fields.Many2one('user.employees_get', '審批人')
    status = fields.Selection(STATUS, string='審批狀態')
    approval_time = fields.Datetime('審批時間')
