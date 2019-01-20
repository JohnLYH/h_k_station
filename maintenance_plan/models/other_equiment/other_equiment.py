# -*- coding: utf-8 -*-
import datetime
import json
import os
import random
import time
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from openpyxl import Workbook

from odoo import models, fields, api
from datetime import datetime as dt

from odoo.exceptions import ValidationError
from odoo.osv import osv

STATUS = [
    ('OK', '正常'), ('Expired', '失效'), ('Scraped', '已報廢')
]
ROW_1_LIST = ['EQUIPMENT No.', 'EQUIPMENT', 'BRAND', 'MODEL', 'SERIAL_NO', 'MANUAL REF. NO.', 'EQUIPMENT OWNER',
              'LOCATION OF EQUIPMENT', 'FREQ. OF CAL.', 'CALIBRATION BODY',
              'CALIBRATION REQUIPEMNETS  (SEE NOTE)', 'LAST MAINTENANCE DATE',
              'MAINTENANCE DUE DATE', 'STATUS', 'REMARK']


class OtherEquipment(models.Model):
    _name = 'maintenance_plan.other_equipment'
    _description = '工器具'

    departments = fields.Many2one('user.department', string='設備擁有者', ondelete='cascade')
    # team_num
    status = fields.Selection(STATUS, string='狀態', required=True)
    maintenance_due_data = fields.Date(string='應用到期時間', )
    last_maintenance_date = fields.Date(string='最後維護日期', )
    calibration_requipemnets = fields.Text(string='檢驗要求', size=500)
    calibration_body = fields.Text(string='檢驗主體', size=500)
    # 单位为月
    freq_of_cal = fields.Text(string='檢驗週期')
    location_of_equipment = fields.Text(string='設備位置', size=500)
    manual_ref_no = fields.Text(string='參考手冊編號', size=500)
    serial_no = fields.Text(string='序列號', size=500)
    model = fields.Text(string='型號', size=500)
    brand = fields.Text(string='品牌', size=500)
    result_reference = fields.Text(string='結果參考', size=500)
    equipment_name = fields.Text('設備名稱', size=500, required=True)
    equipment_num = fields.Text('設備編號', size=500, required=True)
    equipment_records_ids = fields.One2many('maintenance_plan.other_equipment_records', 'other_equipment_id',
                                            string='操作記錄')
    remark = fields.Text(string='備註', size=500)

    @api.constrains('equipment_num')
    def _check_equipment_num(self):
        for record in self:
            if self.search_count([('equipment_num', '=', record.equipment_num),
                                  ('departments', '=', record.departments.id)
                                  ]) > 1:
                raise ValidationError("設備編號已存在，請重新輸入")

    @api.onchange('last_maintenance_date')
    def _maintenance_due_data(self):
        if self.last_maintenance_date:
            if self.freq_of_cal == 'ON\nCONDITION':
                pass
            else:
                try:
                    self.maintenance_due_data = dt.strptime(self.last_maintenance_date, '%Y-%m-%d') \
                                                + relativedelta(months=int(self.freq_of_cal))
                except:
                    pass

    @api.multi
    def write(self, vals):
        if 'type' in vals:
            vals.pop('type')
            return super(OtherEquipment, self).write(vals)
        for i in vals:
            old_value = self[i]
            field_string = self._fields[i].get_description(self.env)['string']
            content = '修改{}{}為{}'.format(field_string, old_value, vals[i]) if old_value else '修改{}為{}'.format(
                field_string, vals[i])
            new_records = self.env['maintenance_plan.other_equipment_records'].create({
                'other_equipment_id': self.id,
                'operation_time': datetime.now(),
                'operation_type': '編輯',
                'content': content,
                'user_id': self._uid,
            })
        return super(OtherEquipment, self).write(vals)

    @api.model
    def create(self, vals):
        if 'type' in vals:
            vals.pop('type')
            print(vals)
            return super(OtherEquipment, self).create(vals)
        records = super(OtherEquipment, self).create(vals)
        new_records = self.env['maintenance_plan.other_equipment_records'].create({
            'other_equipment_id': records.id,
            'operation_time': datetime.now(),
            'operation_type': '新建',
            'content': '工器具新增',
            'user_id': self._uid,
            'remark': records.remark,
        })
        return records

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
                'equipment_name': equipment_name,
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
        last_maintenance_date = kw['last_maintenance_date']
        maintenance_due_data = kw['maintenance_due_data']
        this_env = self.env['maintenance_plan.other_equipment'].search([
            ('id', '=', id), ('equipment_name', '=', equipment_name), ('equipment_num', '=', equipment_num),
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
                'status': 'OK',
                'type': '檢修'
            })
            new_records = self.env['maintenance_plan.other_equipment_records'].create({
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
        this_env = self.env['maintenance_plan.other_equipment'].browse(id)
        # ('id', '=', id), ('equipment_name', '=', equipment_name), ('equipment_num', '=', equipment_num),
        # ('model', '=', model), ('brand', '=', brand)
        if this_env:
            this_env.write({
                'status': 'Scraped',
                'type': '報廢'
            })
            self.env['maintenance_plan.other_equipment_records'].create({
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

    # 定時器
    @api.model
    def other_equipment_scheduler_queue(self):
        nowtime = datetime.datetime.now() + datetime.timedelta(hours=8)
        for record in self:
            if record.maintenance_due_data:
                maintenance_due_data = record.maintenance_due_data
                maintenance_due_data = datetime.strptime(maintenance_due_data, '%Y-%m-%d %H:%M:%S') \
                                       + datetime.timedelta(hours=8)
                if nowtime > maintenance_due_data:
                    record.status = '失效'
            else:
                pass

    @api.model
    def get_in_excel(self, **kwargs):
        # try:
        arr = []
        if kwargs:
            for kw in kwargs['domains']:
                arr.append(kw[0])
            other_equipments = self.env['maintenance_plan.other_equipment'].search(arr)
        else:
            other_equipments = self.env['maintenance_plan.other_equipment'].search([])
        wb = Workbook()
        # 激活 worksheet
        ws = wb.active
        ws.append(ROW_1_LIST)
        len_other_equipments = len(other_equipments)
        for i in range(1, len_other_equipments + 1):
            my_records = [
                other_equipments[i - 1].equipment_num if other_equipments[i - 1].equipment_num else '',
                other_equipments[i - 1].equipment_name if other_equipments[i - 1].equipment_name else '',
                other_equipments[i - 1].brand if other_equipments[i - 1].brand else '',
                other_equipments[i - 1].model if other_equipments[i - 1].model else '',
                other_equipments[i - 1].serial_no if other_equipments[i - 1].serial_no else '',
                other_equipments[i - 1].manual_ref_no if other_equipments[i - 1].manual_ref_no else '',
                other_equipments[i - 1].departments.name if other_equipments[i - 1].departments.name else '',
                other_equipments[i - 1].location_of_equipment if other_equipments[
                    i - 1].location_of_equipment else '',
                other_equipments[i - 1].freq_of_cal if other_equipments[i - 1].freq_of_cal else '',
                other_equipments[i - 1].calibration_body if other_equipments[i - 1].calibration_body else '',
                other_equipments[i - 1].calibration_requipemnets if other_equipments[
                    i - 1].calibration_requipemnets else '',
                other_equipments[i - 1].last_maintenance_date if other_equipments[
                    i - 1].last_maintenance_date else '',
                other_equipments[i - 1].maintenance_due_data if other_equipments[i - 1].maintenance_due_data else '',
                other_equipments[i - 1].status if other_equipments[i - 1].status else '',
                other_equipments[i - 1].remark if other_equipments[i - 1].remark else '',
            ]
            ws.append(my_records)
        file_name = str(time.time()) + str(random.randint(1, 10000)) + "sample.xlsx"
        wb.save(file_name)
        with open(file_name, 'rb') as f:
            data = f.read()
            new_file = self.env['maintenance_plan.trans.excel'].create({
                'name': '工器具導出數據',
                'file': data
            })
            os.remove(file_name)
        return json.dumps({'error': 0, 'message': '下載成功', 'file_id': new_file.id})
        # except:
        #     return json.dumps({'error': 1, 'message': '失败'})


class OtherEquipmentRecords(models.Model):
    _name = 'maintenance_plan.other_equipment_records'
    _description = '工器具操作記錄'

    other_equipment_id = fields.Many2one('maintenance_plan.other_equipment', '工器具', ondelete='cascade')
    user_id = fields.Many2one('res.users', '操作人')
    content = fields.Char('內容')
    remark = fields.Char(string='備註')
    operation_time = fields.Datetime('操作時間')
    operation_type = fields.Char('操作類型')
