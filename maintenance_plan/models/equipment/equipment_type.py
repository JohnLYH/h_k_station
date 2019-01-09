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

    @api.model
    def get_type_tree(self, type_id=None):
        '''
        tree页获取類型树结构
        :param type_id: 類型的id
        :return:
        '''
        records = self.search([('parent_id', '=', type_id)])
        result = [{
            'id': i.id, 'name': i.name, 'leaf': True if len(i.child_ids) == 0 else False,
            'parent_left': i.parent_left, 'parent_right': i.parent_right
        } for i in records]
        return result

    @api.model
    def get_type_route(self, type_id=None):
        current_type = self.browse(type_id)
        route = current_type.name or ' '
        while len(current_type.parent_id) > 0:
            current_type = current_type.parent_id
            route = current_type.name + '>>' + route
        return route
