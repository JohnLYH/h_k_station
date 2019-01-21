# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import base64
import os
import random
import time

import qrcode
from PIL import Image

from odoo import fields, models, api

STATUS = [
    ('Expired', '失效'), ('Effective', '有效')
]


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'
    _rec_name = 'num'

    num = fields.Char('設備編號', required=True)  # 設備座位號，一個座位會有多個放過的設備
    parent_equipment_num = fields.Char('父設備編號', required=True)
    serial_number = fields.Char('設備序列號', required=True)
    equipment_type_id = fields.Many2one('maintenance_plan.equipment.type', string='設備類型', required=True)
    equipment_model = fields.Many2one('maintenance_plan.equipment_model', '設備型號', required=True)
    description = fields.Text('設備描述', required=True)
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
    qr_code = fields.Text('二維碼', readonly=True)
    # 維修記錄
    maintenance_records_ids = fields.One2many('maintenance_plan.maintenance.records', 'equipment_id', string='維修記錄')
    # 遷移記錄, 与序列号绑定
    migrate_records_ids = fields.Many2many('maintenance_plan.migrate.records', 'equipment_migrate', 'equipment_id',
                                           'migrate_id', string='遷移歷史', compute='_com_migrate', store=True)

    @staticmethod
    def generate_2_code(arr):
        '''
        获取二维码二进制
        :param arr:显示内容
        :return:
        '''
        qr = qrcode.QRCode(
            version=1,
            # 设置容错率为最高
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=10,
            border=4
        )
        qr.make(arr)
        img = qr.make_image()
        file_name = str(int(time.time())) + str(random.randint(1,1000)) + 'simpleqrcode.jpg'
        img.save(file_name)
        with open(file_name, 'rb') as open_icon:
            b64str = base64.b64encode(open_icon.read())
        os.remove(file_name)
        return b64str

    @api.one
    @api.depends('serial_number')
    def _com_migrate(self):
        migrate_records = self.env['maintenance_plan.migrate.records'].search([
            ('equipment_serial_number', '=', self.serial_number)
        ])
        self.migrate_records_ids = [[6, 0, migrate_records.ids]]

    @api.model
    def create(self, vals):
        equipment = super(Equipment, self).create(vals)
        equipment.qr_code = self.generate_2_code(equipment.id)
        return equipment

