from odoo import models, fields

STATUS = [
    ('have_passed', '已通過'), ('pending_approval', '待審批'), ('rejected', '已拒絕')
]


class ApprovalManagement(models.Model):
    '''工單審批管理'''
    _name = 'maintenance_plan.order.approval'
    _description = '審批流水'
    _order = 'create_date DESC'

    work_order_id = fields.Many2one('maintenance_plan.maintenance.plan', '工單')
    execute_user_id = fields.Many2one('res.users', '操作人')
    approver_user_id = fields.Many2one('res.users', '下級審批人')
    old_status = fields.Selection(STATUS, string='原始狀態')
    to_status = fields.Selection(STATUS, string='目標狀態')
    signature = fields.Char('簽名')  # 圖片url

class ReferenceExaminationApproval(models.Model):
    '''參考資料審批'''
    _name = 'maintenance_plan.data.approval'
    _description = '參考資料審批'

    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    submitter = fields.Many2one('res.users', '提交人')
    submit_time = fields.Datetime('提交時間')
    approver = fields.Many2one('res.users', '審批人')
    status = fields.Selection(STATUS, string='審批狀態')
    approval_time = fields.Datetime('審批時間')
    approval_type = fields.Char('審判類型', default='WO')
