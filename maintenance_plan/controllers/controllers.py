# -*- coding: utf-8 -*-
import json
import xlrd
import xlwt
from datetime import datetime as dt
import time
import os
import random
import struct
from xlutils3.copy import copy as xl_copy


from odoo import http
from odoo.http import request

ROW_1_LIST = ['Work Order No', 'Work Nature Level 1', 'Work Nature Level 2', 'Equipment No',
              'Equipment Description', 'Equipment Class', 'Equipment Class Description', 'Work Group',
              'Work Group Name', 'Standard Job Code', 'Standard Job Description', 'Standard Job ParamSet Name',
              'Person In Charge', 'Priority', 'Quantity', 'Work Order Description', 'Planned Start Date',
              'Planned Completion Date', 'Actual Start Date', 'Actual Complete Date', 'Status',
              'Service Break Down', 'Start Work Date', 'Finish Work Date', 'Line Code', 'Direction Code',
              'Location From Code', 'Detail IDs', 'Hash X', 'Hash Y']

APP_DIR = os.path.dirname(os.path.dirname(__file__))


class MaintenancePlan(http.Controller):

    @staticmethod
    def excel_validate(sheet, new_sheet, num, cols_list, red_style):
        row_error = False
        for col in cols_list:
            if sheet.cell(num, col).value == '':
                new_sheet.write(num, col, style=red_style)
                row_error = True
            elif col == 16 or col == 17:
                try:
                    dt.strptime(sheet.cell(num, col).value, '%Y-%m-%d %H:%M')
                except Exception as e:
                    new_sheet.write(num, col, sheet.cell(num, col).value, style=red_style)
                    row_error = True
        return row_error

    @http.route('/maintenance_plan/put_in_excel', type='http', csrf=False, auth='user')
    def put_in_excel(self, **kwargs):
        file = kwargs['file']
        filename = kwargs['file'].filename
        workbook = xlrd.open_workbook(file_contents=file.read())
        sheet = workbook.sheets()[0]
        new_workbook = xl_copy(workbook)
        new_sheet = new_workbook.get_sheet(0)
        nrows = sheet.nrows
        # 设置单元格背景色紅色
        red_style = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = 1
        pattern.pattern_fore_colour = xlwt.Style.colour_map['red']
        red_style.pattern = pattern
        # 设置单元格背景色綠色
        green_style = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = 1
        pattern.pattern_fore_colour = xlwt.Style.colour_map['green']
        green_style.pattern = pattern
        error = False
        if [i.value for i in sheet.row(0)] != ROW_1_LIST:
            return json.dumps({'message': '表格不符', 'error': True})
        else:
            for num in range(1, nrows):
                row_error = self.excel_validate(sheet, new_sheet, num, [0, 1, 15, 16, 17], red_style)
                work_order_count = request.env['maintenance_plan.maintenance.plan'].search_count([
                    ('num', '=', sheet.cell(num, 0).value)
                ])
                equipment_record = request.env['maintenance_plan.equipment'].search([
                    ('num', '=', sheet.cell(num, 3).value)
                ])
                if work_order_count != 0 and sheet.cell(num, 0).value != '':
                    new_sheet.write(num, 0, sheet.cell(num, 0).value, style=green_style)
                if len(equipment_record) == 0 and sheet.cell(num, 3).value != '':
                    new_sheet.write(num, 3, sheet.cell(num, 3).value, style=red_style)
                if work_order_count == 0 and len(equipment_record) != 0:
                    request.env['maintenance_plan.maintenance.plan'].create({
                        'num': sheet.cell(num, 0).value, 'work_order_type': sheet.cell(num, 1).value,
                        'work_order_description': sheet.cell(num, 15).value, 'equipment_id': equipment_record.id,
                        'plan_start_time': sheet.cell(num, 16).value.split(' ')[0],
                        'plan_end_time': sheet.cell(num, 17).value.split(' ')[0],
                    })
                if row_error is True:
                    error = True
        if error is True:
            name = str(int(round(time.time() * 1000))) + str(random.randint(1, 1000)) + '.xls'
            path = APP_DIR + '/static/excel/'
            file_path = path + name
            new_workbook.save(file_path)
            with open(file_path, 'rb') as f:
                data = f.read()
                new_file = request.env['maintenance_plan.trans.excel'].create({
                    'name': filename.split('.')[0],
                    'file': data
                })
                os.remove(file_path)
            return json.dumps({'error': error, 'message': '文件有部分錯誤信息，請修改后再次傳入', 'file_id': new_file.id})
        else:
            return json.dumps({'error': error, 'message': '上傳成功'})

    @http.route('/maintenance_plan/down_wrong_file', type='http', auth="user", methods=['GET'])
    def down_wrong_file(self, **kwargs):
        '''
        返回错误excel内容
        :param kwargs:
        :return:
        '''
        file_id = int(kwargs['file_id'])
        wb = request.env['maintenance_plan.trans.excel'].browse(file_id)
        response = request.make_response(wb.file)
        response.headers["Content-Disposition"] = "attachment; filename={}". \
            format((wb.name + '错误.xls').encode().decode('latin-1'))
        return response

    @http.route('/maintenance_plan/export_work_order', auth='user')
    def export_work_order(self, **kw):
        return "Hello, world"

    @http.route('/maintenance_plan/approval_management', auth='none')
    def approval_management(self, **kw):
        print(kw)
        # return {
        #     'type': 'ir.actions.client',
        #     'name': '工单审批详情',
        #     'tag': 'maintenance_plan.maintenance_plan_approval_management',
        # }
        return http.request.render('maintenance_plan.maintenance_plan_approval_management', {})
