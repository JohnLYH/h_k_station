# -*- coding: utf-8 -*-
import json

from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from datetime import datetime as dt
STATUS = [
    ('normal', '正常'), ('invalid', '失效'), ('scrap', '已報廢')
]


class other_equipment(models.Model):
    _name = 'other_equipment.other_equipment'

    # TODO: 組號
    departments = fields.Many2one('res.users', string='組號')
    # team_num
    remark = fields.Char(string='備註')
    status = fields.Selection(STATUS, string='狀態')
    maintenance_due_data = fields.Date(string='應用到期時間')
    last_maintenance_date = fields.Date(string='最後維護日期')
    calibration_requipemnets = fields.Char(string='標準要求')
    calibration_body = fields.Char(string='標準體')
    # 单位为月
    freq_of_cal = fields.Char(string='檢驗週期')
    location_of_equipment = fields.Char(string='設備位置')
    equipment_owner = fields.Char(string='設備擁有者')
    manual_ref_no = fields.Char(string='手动参考号')
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
