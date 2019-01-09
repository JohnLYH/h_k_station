# -*- coding: utf-8 -*-
import datetime
import json
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime as dt
STATUS = [
    ('normal', '正常'), ('invalid', '失效'), ('scrap', '已報廢')
]


class other_equipment(models.Model):
    _name = 'other_equipment.other_equipment'

    # TODO: 組號
    departments = fields.Many2one('res.users', string='所屬班組')
    # team_num
    status = fields.Selection(STATUS, string='狀態')
    maintenance_due_data = fields.Date(string='應用到期時間')
    last_maintenance_date = fields.Date(string='最後維護日期')
    calibration_requipemnets = fields.Char(string='檢驗要求')
    calibration_body = fields.Char(string='檢驗主體')
    # 单位为月
    freq_of_cal = fields.Char(string='檢驗週期')
    location_of_equipment = fields.Char(string='設備位置')
    equipment_owner = fields.Char(string='設備擁有者')
    manual_ref_no = fields.Char(string='參考手冊編號')
    serial_no = fields.Char(string='序列號')
    model = fields.Char(string='型號')
    brand = fields.Char(string='品牌')
    result_reference = fields.Char(string='結果參考')
    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    equipment_name = fields.Char('設備名稱', compute='_com_equipment', store=True)
    equipment_num = fields.Char('設備編號', compute='_com_equipment', store=True)

    @api.depends('equipment_id')
    def _com_equipment(self):
        for record in self:
            if len(record.equipment_id) != 0:
                record.equipment_num = record.equipment_id.num
                record.equipment_name = record.equipment_id.name

    @api.onchange('last_maintenance_date')
    def _maintenance_due_data(self):
        if self.last_maintenance_date:
            self.maintenance_due_data = dt.strptime(self.last_maintenance_date, '%Y-%m-%d')\
                                        + relativedelta(months=int(self.freq_of_cal))

    @api.model
    def get_tool_information(self, id):
        tool_info = self.env.search_read([('id', '=', id)])
        if tool_info:
            equipment_name = tool_info.equipment_name
            equipment_num = tool_info.equipment_name
            model = tool_info.model
            freq_of_cal = tool_info.freq_of_cal
            last_maintenance_date = tool_info.last_maintenance_date
            maintenance_due_data = tool_info.maintenance_due_data
            data = {
                'equipment_name':equipment_name,
                'equipment_num': equipment_num,
                'model': model,
                'freq_of_cal': freq_of_cal,
                'last_maintenance_date': last_maintenance_date,
                'maintenance_due_data': maintenance_due_data,
            }
            return json.dumps(data)
        return False

    @api.model
    def save_tool_management_inspection(self, **kw):
        id = kw['id']
        equipment_name = kw['equipment_name']
        equipment_num = kw['equipment_num']
        remark = kw['remark']
        model = kw['model']
        freq_of_cal = kw['freq_of_cal']
        last_maintenance_date = kw['last_maintenance_date']
        maintenance_due_data = kw['maintenance_due_data']
        this_env = self.env['other_equipment.other_equipment'].search([
            ('id', '=', id), ('equipment_name', '=', equipment_name), ('equipment_num', '=', equipment_num),
            ('model', '=', model), ('freq_of_cal', '=', freq_of_cal)
        ])
        if this_env:
            try:
                last_maintenance_date = datetime.strptime(last_maintenance_date, "%Y-%m-%dT%H:%M:%S.%fZ")
                last_maintenance_date = last_maintenance_date + timedelta(hours=8)
                last_maintenance_date = last_maintenance_date.strftime('%Y-%m-%d')
            except ValueError:
                last_maintenance_date = last_maintenance_date
            try:
                maintenance_due_data = datetime.strptime(maintenance_due_data, "%Y-%m-%dT%H:%M:%S.%fZ")
                maintenance_due_data = maintenance_due_data + timedelta(hours=8)
                maintenance_due_data = maintenance_due_data.strftime('%Y-%m-%d')
            except ValueError:
                maintenance_due_data = maintenance_due_data
            content = '更新有效期{}为{}'.format(this_env.maintenance_due_data, maintenance_due_data)
            this_env.write({
                'last_maintenance_date': last_maintenance_date,
                'maintenance_due_data': maintenance_due_data,
                # 'remark': remark
            })
            self.env['other_equipment.other_equipment_records'].create({
                'other_equipment_id': id,
                'remark': remark,
                'operation_time': datetime.now(),
                'operation_type': '檢修',
                'content': content,
                'user_id': self._uid,
            })
            return True
        else:
            return False

    @api.model
    def save_tool_management_scrap(self, **kw):
        id = kw['id']
        equipment_name = kw['equipment_name']
        equipment_num = kw['equipment_num']
        remark = kw['remark']
        model = kw['model']
        brand = kw['brand']
        this_env = self.env['other_equipment.other_equipment'].search([
            ('id', '=', id), ('equipment_name', '=', equipment_name), ('equipment_num', '=', equipment_num),
            ('model', '=', model), ('brand', '=', brand)
        ])
        if this_env:
            this_env.write({
                'status': 'scrap',
                # 'remark': remark
            })
            self.env['other_equipment.other_equipment_records'].create({
                'other_equipment_id': id,
                'remark': remark,
                'operation_time': datetime.now(),
                'operation_type': '報廢',
                'content': '工器具報廢',
                'user_id': self._uid,
            })
            return True
        else:
            return False


class other_equipment_records(models.Model):
    _name = 'other_equipment.other_equipment_records'
    _description = '工器具操作記錄'

    other_equipment_id = fields.Many2one('other_equipment.other_equipment', '工器具')
    user_id = fields.Many2one('res.users', '操作人')
    content = fields.Char('內容')
    remark = fields.Char(string='備註')
    operation_time = fields.Datetime('操作時間')
    operation_type = fields.Char('操作類型')

