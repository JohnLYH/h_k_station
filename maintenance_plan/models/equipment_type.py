# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api


class EquipmentType(models.Model):
    _name = 'maintenance_plan.equipment.type'
    _description = '設備類別'
    _rec_name = 'name'
    _parent_store = True

    name = fields.Char('類型名稱')
    equipment_ids = fields.One2many('maintenance_plan.equipment', 'equipment_type_id', string='設備')

    parent_id = fields.Many2one('maintenance_plan.equipment.type', string='上級')
    child_ids = fields.One2many('maintenance_plan.equipment.type', 'parent_id', string='下級')

    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

