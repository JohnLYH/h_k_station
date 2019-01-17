# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class OrderForm(models.Model):
    _name = 'maintenance_plan.order.form'
    _description = '工單內審批表單'

    order_id = fields.Many2one('maintenance_plan.maintenance.plan', string='工單')
    name = fields.Char('表單名稱')
    content = fields.Text('表單json內容')
    status = fields.Char('表單狀態')
    approval_ids = fields.One2many('maintenance_plan.order.form.approval', 'order_form_id', string='審批流水')