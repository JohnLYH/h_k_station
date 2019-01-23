# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api


class EquipmentType(models.Model):
    _name = 'maintenance_plan.equipment.type'
    _description = '設備類別'
    _rec_name = 'name'
    _parent_store = True

    name = fields.Char('類型名稱', required=True)
    description = fields.Text('設備類別描述')
    equipment_ids = fields.One2many('maintenance_plan.equipment', 'equipment_type_id', string='設備')

    parent_id = fields.Many2one('maintenance_plan.equipment.type', string='上級', ondelete='cascade')
    child_ids = fields.One2many('maintenance_plan.equipment.type', 'parent_id', string='下級')

    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

    _sql_constraints = [('name_unique', 'unique(name)', '該設備類別已經存在')]

    @api.model
    def get_type_tree(self, type_id=False):
        '''
        tree页获取類型树结构懶加載模式
        :param type_id: 類型的id
        :return:
        '''
        if type_id is False:
            result = [{
                'id': 0, 'name': '信號系統', 'leaf': True if self.search_count([]) == 0 else False
            }]
        else:
            records = self.search([('parent_id', '=', None if type_id == 0 else type_id)])
            result = [{
                'id': i.id, 'name': i.name, 'leaf': True if len(i.child_ids) == 0 else False,
                'parent_left': i.parent_left, 'parent_right': i.parent_right
            } for i in records]
        return result

    @api.model
    def get_equipment_type_tree_data(self, records=None, first=True):
        '''
        遞歸獲取設備類型樹
        :param records:
        :param first: 是否是首次進入該方法
        :return:
        '''
        if first is True:
            records_count = self.search_count([])
            records = self.search_read([('parent_id', '=', None)], fields=['name', 'child_ids'])
        for record in records:
            if len(record['child_ids']) != 0:
                record['children'] = self.search_read([('parent_id', '=', record['id'])], fields=['name', 'child_ids'])
                self.get_equipment_type_tree_data(record['children'], False)
        if first is True:
            return {'records': records, 'records_count': records_count}
        else:
            return None

    @api.model
    def get_type_route(self, type_id=None):
        current_type = self.browse(type_id)
        if type_id == 0:
            root = '信號系統'
            route = ''
        else:
            root = '信號系統>>'
            route = current_type.name
        while len(current_type.parent_id) > 0:
            current_type = current_type.parent_id
            route = current_type.name + '>>' + route
        return root + route

