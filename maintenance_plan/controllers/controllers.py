# -*- coding: utf-8 -*-
import json
from datetime import datetime as dt
import os
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.writer.excel import save_virtual_workbook


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
    def excel_validate(sheet, num, cols_list, style, has_date_col=True):
        '''
        驗證excel的一行的錯誤性
        :param sheet: sheet活動表
        :param num: 行數，1開始
        :param cols_list: 需要驗證的列數列表
        :param style: sheet顏色style
        :param has_date_col: 是否驗證第17、18列的時間格式
        :return:
        '''
        row_error = False
        for col in cols_list:
            if sheet.cell(num, col).value is None:
                sheet.cell(num, col).fill = style
                row_error = True
            elif (col == 17 or col == 18) and has_date_col is True:
                try:
                    dt.strptime(sheet.cell(num, col).value, '%Y-%m-%d %H:%M')
                except Exception as e:
                    sheet.cell(num, col).fill = style
                    row_error = True
        return row_error

    @http.route('/maintenance_plan/put_in_excel', type='http', csrf=False, auth='user')
    def put_in_excel(self, **kwargs):
        '''
        維修計劃管理頁面導入excel按鈕
        :param kwargs: excel的file信息
        :return:
        '''
        file = kwargs['file']
        filename = kwargs['file'].filename
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        # 设置单元格背景色紅色
        red_style = PatternFill(fill_type='solid', fgColor="FF3030")
        # 设置单元格背景色綠色
        green_style = PatternFill(fill_type='solid', fgColor="458B74")
        error = False
        n_row = 0
        for row in sheet.rows:
            n_row += 1
            if n_row == 1:
                if [i.value for i in row] != ROW_1_LIST:
                    return json.dumps({'message': '表格不符', 'error': True})
            else:
                row_error = self.excel_validate(sheet, n_row, [1, 2, 4, 16, 17, 18], red_style)
                work_order_count = request.env['maintenance_plan.maintenance.plan'].search_count([
                    ('num', '=', sheet.cell(n_row, 1).value)
                ])
                equipment_record = request.env['maintenance_plan.equipment'].search([
                    ('num', '=', sheet.cell(n_row, 4).value)
                ])
                if work_order_count != 0 and sheet.cell(n_row, 1).value is not None:
                    sheet.cell(n_row, 1).fill = green_style
                if len(equipment_record) == 0:
                    sheet.cell(n_row, 4).fill = red_style
                if work_order_count == 0 and len(equipment_record) != 0:
                    request.env['maintenance_plan.maintenance.plan'].create({
                        'num': sheet.cell(n_row, 1).value, 'work_order_type': sheet.cell(n_row, 2).value,
                        'work_order_description': sheet.cell(n_row, 16).value, 'equipment_id': equipment_record.id,
                        'plan_start_time': sheet.cell(n_row, 17).value.split(' ')[0],
                        'plan_end_time': sheet.cell(n_row, 18).value.split(' ')[0],
                    })
                if row_error is True:
                    error = True
        if error is True:
            new_file = request.env['maintenance_plan.trans.excel'].create({
                'name': filename.split('.')[0],
                'file': save_virtual_workbook(workbook)
            })
            return json.dumps({'error': error, 'message': '文件有部分錯誤信息，請修改后再次傳入', 'file_id': new_file.id})
        else:
            return json.dumps({'error': error, 'message': '上傳成功'})

    @http.route('/maintenance_plan/down_wrong_file', type='http', auth="user", methods=['GET'])
    def down_wrong_file(self, **kwargs):
        '''
        返回错误excel内容
        :param kwargs: file_id
        :return:
        '''
        file_id = int(kwargs['file_id'])
        wb = request.env['maintenance_plan.trans.excel'].browse(file_id)
        response = request.make_response(wb.file)
        response.headers["Content-Disposition"] = "attachment; filename={}". \
            format((wb.name + '錯誤.xlsx').encode().decode('latin-1'))
        return response

    @http.route('/maintenance_plan/export_work_order', auth='user')
    def export_work_order(self, **kwargs):
        '''
        工單管理頁面導出excel
        :param kwargs:
        :return:
        '''
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
