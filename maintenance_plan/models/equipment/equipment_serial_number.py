# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import base64
import os
import random
import time
import qrcode

from odoo import models, fields, api


class EquipmentSerialNumber(models.Model):
    _name = 'maintenance_plan.equipment.serial_number'
    _description = '設備序列號'
    _rec_name = 'num'

    num = fields.Char('設備序列號', required=True)
    qr_code = fields.Text('二維碼', compute='_com_qr_code', store=True)
    equipment_ids = fields.One2many('maintenance_plan.equipment', 'serial_number_id')
    # 遷移記錄
    migrate_records_ids = fields.One2many('maintenance_plan.migrate.records', 'serial_number_id', string='遷移歷史')

    _sql_constraints = [('num_unique', 'unique(num)', '該設備序列號已經存在')]

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
        qr.add_data(arr)
        qr.make()
        img = qr.make_image()
        file_name = str(int(time.time())) + str(random.randint(1, 1000)) + 'simpleqrcode.jpg'
        img.save(file_name)
        with open(file_name, 'rb') as open_icon:
            b64str = base64.b64encode(open_icon.read())
        os.remove(file_name)
        return b64str

    @api.one
    @api.depends('num')
    def _com_qr_code(self):
        if self.num is not False:
            self.qr_code = self.generate_2_code(self.num)
