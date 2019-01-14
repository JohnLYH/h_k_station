# -*- coding: utf-8 -*-

from odoo import api, models, fields


class InventoryManagement(models.Model):
    _name = 'equipment.inventory_management'

    inventory_id = fields.Char(string='庫存編碼')
    inventory_description = fields.Char(string='描述')
    work_prepare = fields.Many2many('maintenance_plan.standard.job',
                                    'inventory_standard_ref', 'standard_id', 'inventory_id', string='標準工作')
    inventory_count = fields.Integer(string='库存数量')
    lastest_update_time = fields.Datetime(string='最後更新時間')
    _sql_constraints = [('name_unique', 'unique(inventory_id)', "庫存編碼已经存在请重新输入")]

    # 创建一条新的记录
    def create_new_record(self):
        return {
            'name': '库存管理新增',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'equipment.inventory_management',
            'context': self.env.context,
            'flags': {'initial_mode': 'edit'},
            'target': 'new',
        }

    # 导入数据
    def import_record(self):
        pass

    # 标记当前的记录
    def inventory_edit(self):
        return {
            'name': '库存管理新增',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'equipment.inventory_management',
            'context': self.env.context,
            'flags': {'initial_mode': 'edit'},
            'target': 'new',
        }