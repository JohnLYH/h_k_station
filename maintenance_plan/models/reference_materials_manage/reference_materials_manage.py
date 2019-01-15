# -*- coding: utf-8 -*-

from odoo import models, fields, api

file_type = [
    ('WI', 'WI'), ('M-tube', 'M-tube'), ('EDOC', 'EDOC'), ('Fault finding', 'Fault finding'),
    ('Recovery procedur', 'Recovery procedur')
]


class ReferenceMaterialsManage(models.Model):
    _name = 'maintenance_plan.reference_materials_manage'
    _description = '參考資料管理的詳細管理'

    equipment_id = fields.Many2one('maintenance_plan.equipment','設備編號', ondelete='cascade')
    field_type = fields.Selection(file_type, '文件類型', required=True)
    select_file_name = fields.Char('文件名稱')
    select_file = fields.Binary(string='文件', attachment=True, required=True)
    edition = fields.Char(string='版本', required=True)
    numbering = fields.Char(string='編號', required=True)

    @api.model
    def create(self, vals):
        print(vals)
        return super(ReferenceMaterialsManage, self).create(vals)


class ReferenceMaterialsManageRecord(models.Model):
    _name = 'maintenance_plan.reference_materials_manage_record'
    _description = '參考資料管理的操作記錄'

    reasons_change = fields.Char(string='變更原因')
    reasons_details = fields.Text(string='變更細節')
    reference_materials_manage_id = fields.Many2one('maintenance_plan.reference_materials_manage', '對應的參考資料管理的詳細管理', ondelete='cascade')
    user_id = fields.Many2one('res.users', '操作人')
    operation_time = fields.Datetime('操作時間')
    field_type = fields.Selection(file_type, '文件類型', required=True, compute='_get_value', store=True)
    select_file_name = fields.Char('文件名稱', compute='_get_value', store=True)
    edition = fields.Char(string='版本', required=True, compute='_get_value', store=True)
    numbering = fields.Char(string='編號', required=True, compute='_get_value', store=True)

    @api.depends('reference_materials_manage_id')
    def _get_value(self):
        for re in self:
            if re.reference_materials_manage_id:
                re.field_type = re.reference_materials_manage_id.field_type
                re.numbering = re.reference_materials_manage_id.numbering
                re.select_file_name = re.reference_materials_manage_id.select_file_name
                re.edition = re.reference_materials_manage_id.edition
