# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import fields, models, api

STATUS = [
    ('Expired', '失效'), ('Effective', '有效')
]


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'
    _rec_name = 'serial_number'

    num = fields.Char('設備編號')  # 設備座位號，一個座位會有多個放過的設備
    parent_equipment_num = fields.Char('父設備編號')
    serial_number_id = fields.Many2one('maintenance_plan.equipment.serial_number', required=True, string='序列號',
                                       domain="[('equipment_ids', '=', False)]", readonly=True)  # 唯一
    serial_number = fields.Char('序列號', compute='_com_serial_number_id', store=True)  # 唯一
    qr_code = fields.Text('二維碼', compute='_com_serial_number_id')
    equipment_type_id = fields.Many2one('maintenance_plan.equipment.type', string='設備類型', required=True)
    line = fields.Char('線別')
    station = fields.Char('車站')
    equipment_model = fields.Many2one('maintenance_plan.equipment_model', '設備型號', required=True)
    display_equipment_model_name = fields.Char('設備型號', compute='_com_equipment_model')  # 設備型號名稱的展示字段
    description = fields.Text('設備描述', compute='_com_equipment_model', store=True)
    status = fields.Selection(STATUS, required=True, default='Effective', string='狀態')
    item_code = fields.Char('庫存編號', required=True)
    direction = fields.Char('方向')
    start_chainage = fields.Char('起始公里標')
    end_chainage = fields.Char('結束公里標')
    detailed_location = fields.Char('設備詳細位置')
    last_installation_date = fields.Date('安裝時間')
    service_since = fields.Date('啟用時間')
    expected_asset_life = fields.Date('預期壽命')
    warranty = fields.Char('保修期')
    supplier = fields.Char('供應商')
    oem_manufacturer = fields.Char('原始製造商')
    lead_maintainer = fields.Char('設備維護者')
    # 維修記錄
    maintenance_records_ids = fields.One2many('maintenance_plan.maintenance.records', 'equipment_id', string='維修記錄')

    @api.one
    @api.depends('serial_number_id')
    def _com_serial_number_id(self):
        if len(self.serial_number_id) != 0:
            self.qr_code = self.serial_number_id.qr_code
            self.serial_number = self.serial_number_id.num

    @api.one
    @api.depends('equipment_model')
    def _com_equipment_model(self):
        if len(self.equipment_model) != 0:
            self.description = self.equipment_model.description
            self.display_equipment_model_name = self.equipment_model.equipment_model
