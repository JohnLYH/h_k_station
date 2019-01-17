# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import base64
import datetime
import json
import os

import qrcode
from PIL import Image

from odoo import fields, models, api


class EquipmentModel(models.Model):
    _name = 'maintenance_plan.equipment_model'
    _description = '設備型號'
    _rec_name = 'equipment_model'

    equipment_model = fields.Char('型號名稱', required=True)
    description = fields.Char('設備名稱', required=True)
    reference_materials_manage_ids = fields.One2many('maintenance_plan.reference_materials_manage', 'equipment_id',
                                                     string='设备参考资料')
    wi = fields.Char(string='WI', compute='_get_value', store=True)
    edoc = fields.Char(string='EDOC', compute='_get_value', store=True)
    m_tube = fields.Char(string='M-tube', compute='_get_value', store=True)
    fault_finding = fields.Char(string='Fault finding', compute='_get_value', store=True)
    recovery_procedur = fields.Char(string='Recovery procedur', compute='_get_value', store=True)
    reference_materials_manage_records = fields.One2many('maintenance_plan.reference_materials_manage_record',
                                                         'reference_materials_manage_id',string='操作記錄')

    @api.one
    @api.depends('reference_materials_manage_ids')
    def _get_value(self):
        if self:
            arr = []
            for reference_materials_manage_id in self.reference_materials_manage_ids:
                arr.append(reference_materials_manage_id.field_type)
            arr = list(set(arr))
            self.wi = '已上傳' if 'WI' in arr else '未上傳'
            self.edoc = '已上傳' if 'EDOC' in arr else '未上傳'
            self.m_tube = '已上傳' if 'M-tube' in arr else '未上傳'
            self.fault_finding = '已上傳' if 'Fault finding' in arr else '未上傳'
            self.recovery_procedur = '已上傳' if 'Recovery procedur' in arr else '未上傳'

    @api.model
    def get_value(self,**kwargs):
        # reference_materials_manage = self.env['maintenance_plan.reference_materials_manage'].browse(59)
        # print(reference_materials_manage)
        if kwargs['id']:
            maintenance_equipment_model = self.env['maintenance_plan.equipment_model'].browse(kwargs['id'])
            if maintenance_equipment_model:
                description = maintenance_equipment_model.description
                equipment_model = maintenance_equipment_model.equipment_model
                wi = []
                edoc = []
                m_tube = []
                fault_finding = []
                recovery_procedur = []
                reference_materials_manage_ids = maintenance_equipment_model.reference_materials_manage_ids
                if reference_materials_manage_ids:
                    for reference_materials_manage_id in reference_materials_manage_ids:
                        if reference_materials_manage_id.field_type == 'WI':
                            wi.append(self.get_field_type_value(reference_materials_manage_id))
                        elif reference_materials_manage_id.field_type == 'EDOC':
                            edoc.append(self.get_field_type_value(reference_materials_manage_id))
                        elif reference_materials_manage_id.field_type == 'M-tube':
                            m_tube.append(self.get_field_type_value(reference_materials_manage_id))
                        elif reference_materials_manage_id.field_type == 'Fault finding':
                            fault_finding.append(self.get_field_type_value(reference_materials_manage_id))
                        else:
                            recovery_procedur.append(self.get_field_type_value(reference_materials_manage_id))
            else:
                return json.dumps({'error': 1, 'msg': '未知錯誤'})
            return json.dumps({'error': 0, 'description': description, 'equipment_model': equipment_model, 'wi': wi, 'edoc': edoc, 'm_tube': m_tube,
                               'fault_finding': fault_finding, 'recovery_procedur': recovery_procedur})
        else:
            return json.dumps({'error': 1, 'msg': '未知錯誤'})

    @staticmethod
    def get_field_type_value(manage_id):
        select_file_name = manage_id.select_file_name
        edition = manage_id.edition
        numbering = manage_id.numbering
        id = manage_id.id
        # select_file = manage_id.select_file
        return {'select_file_name': select_file_name,
                'edition': edition,
                'numbering': numbering,
                'id': id,
                }

    @api.model
    def remove_reference_materials_manage(self,**kwargs):
        materials_manage_id = kwargs['id']
        model_id = kwargs['res_id']
        # 設備編號
        equipment_model = self.env['maintenance_plan.equipment_model'].sudo().browse(model_id)
        # 資料
        reference_materials_manage_id = self.env['maintenance_plan.reference_materials_manage'].sudo().browse(
            materials_manage_id)
        if equipment_model and reference_materials_manage_id:
            # 文檔類型
            field_type = reference_materials_manage_id.field_type
            # 文檔編號
            numbering = reference_materials_manage_id.numbering
            # 版本
            edition = reference_materials_manage_id.edition
            # 文件名稱
            select_file_name = reference_materials_manage_id.select_file_name
            # 變更原因
            try:
                reasons_change = kwargs['reasons_details']
            except:
                reasons_change = ''
            # 操作人
            user_id = self._uid
            # 操作時間
            operation_time = datetime.datetime.now()
            # 操作類型
            operation_type = '删除'
            values = {
                'reasons_change': reasons_change,
                'reasons_details': '',
                'operation_type': operation_type,
                'user_id': user_id,
                'operation_time': operation_time,
                'field_type': field_type,
                'select_file_name': select_file_name,
                'edition': edition,
                'numbering': numbering,
            }
            equipment_model.write({'reference_materials_manage_ids': [(2, materials_manage_id)]})
            equipment_model.write({'reference_materials_manage_records': [(0, 0, values)]})
            # TODO: 刪除審批
        else:
            return json.dumps({'error': 0, 'message': '參考資料或設備編號不存在'})
        return json.dumps({'error': 0})
