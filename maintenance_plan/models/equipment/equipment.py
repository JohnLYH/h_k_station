# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import fields, models


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'
    _rec_name = 'num'

    num = fields.Char('設備編號')
    parent_equipment_num = fields.Char('父設備編號')
    serial_number = fields.Char('設備序列號')
    equipment_type_id = fields.Many2one('maintenance_plan.equipment.type', string='設備類別')
    equipment_model = fields.Char('設備型號')
    description = fields.Char('設備描述')
    status = fields.Char('狀態')
    item_code = fields.Char('庫存編碼')
    line_id = fields.Many2one('maintenance_plan.line', string='線別')
    station_id = fields.Many2one('maintenance_plan.station', string='車站')
    direction = fields.Char('方向')
    start_chainage = fields.Char('起始公里標')
    end_chainage = fields.Char('終點公里標')
    last_installation_date = fields.Date('最近安裝時間')
    service_since = fields.Date('啟用時間')
    expected_asset_life = fields.Integer('使用壽命')
    warranty = fields.Integer('保修期')
    supplier = fields.Char('供應商')
    oem_manufacturer = fields.Char('原始設備製造商')
    lead_maintainer = fields.Char('設備維護者')


