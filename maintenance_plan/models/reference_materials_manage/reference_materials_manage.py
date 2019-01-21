# -*- coding: utf-8 -*-
import json

from odoo import models, fields, api

file_type = [
    ('WI', 'WI'), ('M-tube', 'M-tube'), ('EDOC', 'EDOC'), ('Fault finding', 'Fault finding'),
    ('Recovery procedur', 'Recovery procedur')
]


class ReferenceMaterialsManage(models.Model):
    _name = 'maintenance_plan.reference_materials_manage'
    _description = '參考資料管理的詳細管理'

    equipment_id = fields.Many2one('maintenance_plan.equipment_model','設備型號')
    field_type = fields.Selection(file_type, '文件類型', required=True)
    select_file_name = fields.Char('文件名稱')
    select_file = fields.Binary(string='文件', attachment=True, required=True)
    edition = fields.Char(string='版本', required=True)
    numbering = fields.Char(string='編號', required=True)
    url = fields.Char(string='文件url', compute='_get_url', store=True)
    status = fields.Boolean(string='是否已經通過審批', default=False, required=True)
    upload_tpye = fields.Char(string='視頻或者pdf')

    @api.one
    @api.depends('select_file')
    def _get_url(self):
        self.url = '/web/content?model=maintenance_plan.reference_materials_manage&id={}' \
                   '&field=select_file&filename={}'.format(self.id, self.select_file_name)

    @api.model
    def create(self, vals):
        return super(ReferenceMaterialsManage, self).create(vals)

    @api.model
    def get_remove_value(self,**kwargs):
        reference_materials_manage = self.env['maintenance_plan.reference_materials_manage'].browse(kwargs['id'])
        if reference_materials_manage:
            numbering = reference_materials_manage.numbering
            edition = reference_materials_manage.edition
            file_name = reference_materials_manage.select_file_name
            return json.dumps({'error': 0, 'numbering': numbering,'edition': edition, 'file_name': file_name})
        else:
            return json.dumps({'error': 1})

    @api.model
    def get_change_value(self, **kwargs):
        reference_materials_manage = self.env['maintenance_plan.reference_materials_manage'].browse(kwargs['id'])
        if reference_materials_manage:
            numbering = reference_materials_manage.numbering
            edition = reference_materials_manage.edition
            file_name = reference_materials_manage.select_file_name
            field_type = reference_materials_manage.field_type
            upload_tpye = reference_materials_manage.upload_tpye
            return json.dumps({'error': 0, 'numbering': numbering, 'edition': edition, 'file_name': file_name,
                               'field_type': field_type, 'upload_tpye': upload_tpye})
        else:
            return json.dumps({'error': 1})


class ReferenceMaterialsManageRecord(models.Model):
    _name = 'maintenance_plan.reference_materials_manage_record'
    _description = '參考資料管理的操作記錄'

    reasons_change = fields.Char(string='變更原因')
    reasons_details = fields.Text(string='變更細節')
    operation_type = fields.Char(string='操作類型')
    reference_materials_manage_id = fields.Many2one(
        'maintenance_plan.equipment_model', '對應的設備編號')
    user_id = fields.Many2one('res.users', '操作人')
    operation_time = fields.Datetime('操作時間')
    field_type = fields.Selection(file_type, '文檔類型', required=True)
    select_file_name = fields.Char('文件名稱')
    edition = fields.Char(string='版本', required=True)
    numbering = fields.Char(string='文檔編號', required=True)

    @api.model
    def get_details_value(self,**kwargs):
        id = kwargs['id']
        details_values = self.env['maintenance_plan.reference_materials_manage_record'].browse(id)
        if details_values:
            numbering = details_values.numbering
            edition = details_values.edition
            file_name = details_values.select_file_name
            field_type = details_values.field_type
            reasons_change = details_values.reasons_change
            reasons_details = details_values.reasons_details
            values = {'numbering': numbering, 'edition': edition,
                               'file_name': file_name, 'field_type': field_type,
                               'reasons_change': reasons_change, 'reasons_details': reasons_details}
            return json.dumps({'error': 0, 'numbering': numbering, 'edition': edition,
                               'file_name': file_name, 'field_type': field_type,
                               'reasons_change': reasons_change, 'reasons_details': reasons_details})
        else:
            return json.dumps({'error': 1})

