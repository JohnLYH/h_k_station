# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class MigrateRecords(models.Model):
    _name = 'maintenance_plan.migrate.records'
    _description = '設備遷移歷史'

    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    info = fields.Char('遷移信息')
    old_equipment_serial_number = fields.Char('遷出設備序列號')
    new_equipment_serial_number = fields.Char('遷入設備序列號')
    remark = fields.Char('備註')
    executor_user_id = fields.Many2one('res.users', string='操作人')
    signature = fields.Char('簽名')  # 圖片url, binary_file的記錄