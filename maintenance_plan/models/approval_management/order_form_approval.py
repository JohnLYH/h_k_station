# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class OrderFormApproval(models.Model):
    _name = 'maintenance_plan.order.form.approval'
    _description = '工單內審批表單操作流水'
    _order = 'create_date DESC'

    order_form_id = fields.Many2one('maintenance_plan.order.form', string='審批表單')
    execute_user_id = fields.Many2one('res.users', '操作人')
    next_execute_user_id = fields.Many2one('res.users', '下級審批人')
    # 表單狀態：對向波口測試 WRITE、SUBMIT、CHECK、COMPLETE
    old_status = fields.Char('原始狀態')
    to_status = fields.Char('目標狀態')
    signature = fields.Char('簽名')  # 圖片url
    reason = fields.Char('拒絕原因')  # 當被拒絕是才有這項數據
    approval_time = fields.Datetime('簽署時間')
