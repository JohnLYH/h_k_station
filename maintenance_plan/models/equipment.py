# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import fields, models


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'

    name = fields.Char('Equipment Name')
    num = fields.Char('Equipment No')  # 設備編號
    description = fields.Char('Equipment Description')  # 設備描述
    equipment_type_id = fields.Many2one('maintenance_plan.equipment.type', string='設備類別')


