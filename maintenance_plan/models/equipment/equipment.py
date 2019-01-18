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
    description = fields.Char('設備描述', required=True)
    status = fields.Selection(STATUS, required=True, default='Effective', string='狀態')
    item_code = fields.Char('庫存編碼', required=True)
    direction = fields.Char('方向')
    start_chainage = fields.Char('起始公里標')
    end_chainage = fields.Char('終點公里標')
    detailed_location = fields.Char('設備詳細位置')
    last_installation_date = fields.Date('最近安裝時間')
    service_since = fields.Date('啟用時間')
    expected_asset_life = fields.Integer('使用壽命')
    warranty = fields.Integer('保修期')
    supplier = fields.Char('供應商')
    oem_manufacturer = fields.Char('原始設備製造商')
    lead_maintainer = fields.Char('設備維護者')
    qr_code = fields.Text('二維碼')

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

    @api.model
    def create(self, vals):
        equipment = super(Equipment, self).create(vals)
        equipment.qr_code = self.generate_2_code(equipment.id)
        return equipment
