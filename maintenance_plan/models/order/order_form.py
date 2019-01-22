# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api


class OrderForm(models.Model):
    _name = 'maintenance_plan.order.form'
    _description = '工單內審批表單'

    order_id = fields.Many2one('maintenance_plan.maintenance.plan', string='工單')
    name = fields.Char('表單名稱')
    content = fields.Text('表單json內容')
    # 表單狀態：對向波口測試 WRITE、SUBMIT、CHECK、COMPLETE
    status = fields.Char('表單狀態')
    approval_ids = fields.One2many('maintenance_plan.order.form.approval', 'order_form_id', string='審批流水')
    next_execute_user_id = fields.Many2one('res.users', '下級審批人', compute='_com_next_execute')
    approval_type = fields.Char('審判類型', default='Form')

    # 计算
    @api.one
    @api.depends('approval_ids')
    def _com_next_execute(self):
        if len(self.approval_ids) != 0:
            # 最後提交審批的記錄
            self.next_execute_user_id = self.approval_ids[-1].next_execute_user_id.id or None
