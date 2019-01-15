# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import base64
import os

import qrcode
from PIL import Image

from odoo import fields, models, api


class EquipmentModel(models.Model):
    _name = 'maintenance_plan.equipment_model'
    _description = '設備型號'
    # _rec_name = 'equipment_model'

    equipment_model = fields.Char('設備型號')
    description = fields.Char('設備名稱')
    wi_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='WI')
    wi = fields.Char(string='WI', compute='_get_value', store=True)
    edoc_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='EDOC')
    edoc = fields.Char(string='EDOC', compute='_get_value', store=True)
    m_tube_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='M-tube')
    m_tube = fields.Char(string='M-tube', compute='_get_value', store=True)
    fault_finding_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id',
                                        string='Fault finding')
    fault_finding = fields.Char(string='Fault finding', compute='_get_value', store=True)
    recovery_procedur_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id',
                                            string='Recovery procedur')
    recovery_procedur = fields.Char(string='Recovery procedur', compute='_get_value', store=True)
    reference_materials_manage_records = fields.One2many('maintenance_plan.reference_materials_manage_record',
                                                         'reference_materials_manage_id',string='操作記錄')

    @api.depends('wi_ids', 'edoc_ids', 'm_tube_ids', 'm_tube_ids', 'fault_finding_ids', 'recovery_procedur_ids')
    def _get_value(self):
        for re in self:
            print(re)
            re.wi = '已上傳' if re.wi_ids else '未上傳'
            re.edoc = '已上傳' if re.edoc_ids else '未上傳'
            re.m_tube = '已上傳' if re.m_tube_ids else '未上傳'
            re.fault_finding = '已上傳' if re.fault_finding_ids else '未上傳'
            re.recovery_procedur = '已上傳' if re.recovery_procedur_ids else '未上傳'
