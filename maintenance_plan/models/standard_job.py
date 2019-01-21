# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class StandardJob(models.Model):
    _name = 'maintenance_plan.standard.job'
    _description = '標準工作'
    _rec_name = 'name'

    name = fields.Char('標準工作名稱')
    description = fields.Text('標準工作描述')
    inventory_management_ids = fields.Many2many('maintenance_plan.inventory_management', 'inventory_standard_ref',
                                                'standard_id', 'inventory_id', string='庫存管理')
