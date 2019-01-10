# -*- coding: utf-8 -*-

from odoo import models, fields, api


STATUS = [
    ('正常', '正常'), ('失效', '失效'), ('已報廢', '已報廢')
]
file_type = [
    ('WI', 'WI'), ('M-tube', 'M-tube'), ('EDOC', 'EDOC'), ('Fault finding', 'Fault finding'),
    ('Recovery procedur', 'Recovery procedur')
]

class reference_materials_manage(models.Model):
    _name = 'other_equipment.reference_materials_manage'
    _description = '參考資料管理'

    equipment_ids = fields.Many2one('maintenance_plan.equipment')


