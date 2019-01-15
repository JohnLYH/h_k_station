# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import base64
import os

import qrcode
from PIL import Image

from odoo import fields, models, api


class Equipment_model(models.Model):
    _name = 'maintenance_plan.equipment_model'
    _description = '設備型號'
    # _rec_name = 'equipment_model'

    equipment_model = fields.Char('設備型號')
    description = fields.Char('設備名稱')
    wi_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='WI')
    wi = fields.Char(string='WI', compute='_get_wi', store=True)
    edoc_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='EDOC')
    eodc = fields.Char(string='EDOC', compute='_get_eodc', store=True)
    m_tube_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='M-tube')
    m_tube = fields.Char(string='M-tube', compute='_get_m_tube', store=True)
    fault_finding_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='Fault finding')
    fault_finding = fields.Char(string='Fault finding', compute='_get_fault_finding', store=True)
    recovery_procedur_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id', string='Recovery procedur')
    recovery_procedur = fields.Char(string='Recovery procedur', compute='_get_recovery_procedur', store=True)


    @api.depends('wi_ids')
    def _get_wi(self):
        for re in self:
            if re.wi_ids:
                re.wi = '已上傳'
            else:
                re.wi = '未上傳'

    @api.depends('edoc_ids')
    def _get_edoc(self):
        for re in self:
            if re.edoc_ids:
                re.edoc = '已上傳'
            else:
                re.edoc = '未上傳'

    @api.depends('m_tube_ids')
    def _get_m_tube(self):
        for re in self:
            if re.m_tube_ids:
                re.m_tube = '已上傳'
            else:
                re.m_tube = '未上傳'

    @api.depends('fault_finding_ids')
    def _get_fault_finding(self):
        for re in self:
            if re.fault_finding_ids:
                re.fault_finding = '已上傳'
            else:
                re.fault_finding = '未上傳'

    @api.depends('recovery_procedur_ids')
    def _get_recovery_procedur(self):
        for re in self:
            if re.recovery_procedur_ids:
                re.recovery_procedur = '已上傳'
            else:
                re.recovery_procedur = '未上傳'