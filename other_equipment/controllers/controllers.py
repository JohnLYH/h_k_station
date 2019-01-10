# -*- coding: utf-8 -*-
import json
import os
import random
import time
import xlrd
import xlwt
from openpyxl import Workbook

from odoo import http
from odoo.http import request
from xlutils3.copy import copy as xl_copy
from datetime import datetime as dt

ROW_1_LIST = ['EQUIPMENT No.', 'TEAM NO.', 'RESULT \nREFERENCE', 'EQUIPMENT',
              'BRAND', 'MODEL', 'SERIAL_NO', 'MANUAL REF. NO.',
              'EQUIPMENT OWNER', 'LOCATION OF EQUIPMENT', 'FREQ. OF CAL.', 'CALIBRATION BODY',
              'CALIBRATION REQUIPEMNETS  (SEE NOTE)', 'LAST MAINTENANCE DATE', 'MAINTENANCE DUE DATE', 'STATUS',
              'REMARK']
APP_DIR = os.path.dirname(os.path.dirname(__file__))


class OtherEquipment(http.Controller):
    @staticmethod
    def excel_validate(request, sheet, new_sheet, num, cols_list, style, has_date_col):
        '''
        驗證excel的一行的錯誤性
        :param sheet: sheet活動表
        :param new_sheet: 用來變更顏色的複製sheet活動表
        :param num: 行數，0開始
        :param cols_list: 需要驗證的列數列表
        :param style: sheet顏色style
        :param has_date_col: 是否驗證第13、14列的時間格式
        :return:
        '''
        row_error = False
        for col in cols_list:
            if sheet.cell(num, col).value == '':
                new_sheet.write(num, col, style=style)
                row_error = True
            elif (col == 13 or col == 14) and has_date_col is True:
                try:
                    dt.strptime(sheet.cell(num, col).value, '%Y/%m/%d')
                except Exception as e:
                    new_sheet.write(num, col, sheet.cell(num, col).value, style=style)
                    row_error = True
            else:
                if col == 0:
                    # 設備編號
                    equipment_num = sheet.cell(num, col).value
                    # 組號
                    if sheet.cell(num, 1).value == '':
                        row_error = True
                    else:
                        departments = sheet.cell(num, 1).value
                        # 檢查當前組是否有這個設備編號了
                        if request.env['other_equipment.other_equipment'].sudo().search_count(
                                [('equipment_num', '=', equipment_num),
                                 ('departments.department_order', '=', departments)]) > 0:
                            row_error = True
                # 驗證這個組是否存在
                if col == 1:
                    departments = sheet.cell(num, 1).value
                    if not request.env['user.department'].sudo().search([
                             ('department_order', '=', departments)]):
                        row_error = True
        return row_error

    @staticmethod
    def set_excel_style_color(colour_map_key):
        '''
        設置單元格背景色
        :param colour_map_key: 顏色對應鍵值對的key
        :return:
        '''
        style = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = 1
        pattern.pattern_fore_colour = xlwt.Style.colour_map[colour_map_key]
        style.pattern = pattern
        return style

    @http.route('/other_equipment/put_in_excel', type='http', csrf=False, auth='user')
    def put_in_excel(self, **kwargs):
        '''
        工器具管理導入excel按鈕
        :param kwargs: excel的file信息
        :return:
        '''
        file = kwargs['file']
        filename = kwargs['file'].filename
        workbook = xlrd.open_workbook(file_contents=file.read())
        sheet = workbook.sheets()[0]
        new_workbook = xl_copy(workbook)
        new_sheet = new_workbook.get_sheet(0)
        nrows = sheet.nrows
        # 设置单元格背景色紅色
        red_style = self.set_excel_style_color('red')
        # 设置单元格背景色綠色
        green_style = self.set_excel_style_color('green')
        error = False
        x = [i.value for i in sheet.row(0)]
        if [i.value for i in sheet.row(0)] != ROW_1_LIST:
            return json.dumps({'message': '表格不符', 'error': True})
        else:
            for num in range(1, nrows):
                # 這裡是檢測日期格式是否正確
                row_error = self.excel_validate(request, sheet, new_sheet, num, [13, 14], red_style, has_date_col=True)
                # 這裡檢查機器編號是否合格
                row_error2 = self.excel_validate(request, sheet, new_sheet, num,
                                                 [0, 1, 3, 9, 10, 15], red_style, has_date_col=False)
                if row_error or row_error2:
                    error = True
                else:
                    # 設備編號
                    equipment_num = sheet.cell(num, 0).value
                    # 所屬群組
                    departments = request.env['user.department'].search([
                             ('department_order', '=', sheet.cell(num, 1).value)]).id
                    # 結果參考
                    result_reference = sheet.cell(num, 2).value
                    # 設備名稱
                    equipment_name = sheet.cell(num, 3).value
                    # 品牌
                    brand = sheet.cell(num, 4).value
                    # 型號
                    model = sheet.cell(num, 5).value
                    # 序列號
                    serial_no = sheet.cell(num, 6).value
                    # 參考手冊編號
                    manual_ref_no = sheet.cell(num, 7).value
                    # 設備擁有者
                    equipment_owner = sheet.cell(num, 8).value
                    # 設備位置
                    location_of_equipment = sheet.cell(num, 9).value
                    # 檢驗週期
                    freq_of_cal = sheet.cell(num, 10).value
                    # 檢驗主體
                    calibration_body = sheet.cell(num, 11).value
                    # 檢驗要求
                    calibration_requipemnets = sheet.cell(num, 12).value
                    # 最後維護日期
                    last_maintenance_date = sheet.cell(num, 13).value
                    # 應用到期時間
                    maintenance_due_data = sheet.cell(num, 14).value
                    # 狀態
                    status = sheet.cell(num, 15).value
                    # 備註
                    remark = sheet.cell(num, 16).value
                    request.env['other_equipment.other_equipment'].create({
                        'departments': departments, 'equipment_num': equipment_num,
                        'result_reference': result_reference, 'equipment_name': equipment_name,
                        'brand': brand, 'model': model,'serial_no': serial_no, 'manual_ref_no': manual_ref_no,
                        'equipment_owner': equipment_owner, 'location_of_equipment': location_of_equipment,
                        'freq_of_cal': freq_of_cal, 'calibration_body': calibration_body,
                        'calibration_requipemnets': calibration_requipemnets,
                        'last_maintenance_date': last_maintenance_date, 'status': status,
                        'maintenance_due_data': maintenance_due_data, 'remark': remark,
                    })
                    error = False
        if error is True:
            name = str(int(round(time.time() * 1000))) + str(random.randint(1, 1000)) + '.xls'
            path = APP_DIR + '/static/excel/'
            file_path = path + name
            new_workbook.save(file_path)
            with open(file_path, 'rb') as f:
                data = f.read()
                new_file = request.env['other_equipment.trans.excel'].create({
                    'name': filename.split('.')[0],
                    'file': data
                })
                os.remove(file_path)
            return json.dumps({'error': error, 'message': '文件有部分錯誤信息，請修改后再次傳入', 'file_id': new_file.id})
        else:
            return json.dumps({'error': error, 'message': '上傳成功'})

    @http.route('/other_equipment/get_in_excel', type='http', csrf=False, auth='user')
    def get_in_excel(self, **kwargs):
        '''
        工器具管理導出excel按鈕
        :param kwargs: 需要導出的domian條件
        :return:
        '''
        domains = kwargs['domains']
        arr = []
        try:
            if domains:
                x = domains.split(',')
                num = int(len(x)/3 + 1)
                for i in range(1, num):
                    tuples = (x[3*i-3], x[3*i-2], x[3*i-1])
                    arr.append(tuples)
                other_equipments = request.env['other_equipment.other_equipment'].search(arr)
            else:
                other_equipments = request.env['other_equipment.other_equipment'].search([])
            wb = Workbook()
            # 激活 worksheet
            ws = wb.active
            ws.append(ROW_1_LIST)
            len_other_equipments = len(other_equipments)
            for i in range(1, len_other_equipments+1):
                my_records = [
                    other_equipments[i-1].equipment_num if other_equipments[i-1].equipment_num else '',
                    other_equipments[i - 1].departments.department_order if other_equipments[
                        i - 1].departments.department_order else '',
                    other_equipments[i - 1].result_reference if other_equipments[i - 1].result_reference else '',
                    other_equipments[i - 1].equipment_name if other_equipments[i - 1].equipment_name else '',
                    other_equipments[i - 1].brand if other_equipments[i - 1].brand else '',
                    other_equipments[i - 1].model if other_equipments[i - 1].model else '',
                    other_equipments[i - 1].serial_no if other_equipments[i - 1].serial_no else '',
                    other_equipments[i - 1].manual_ref_no if other_equipments[i - 1].manual_ref_no else '',
                    other_equipments[i - 1].equipment_owner if other_equipments[i - 1].equipment_owner else '',
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
            wb.save("sample.xlsx")
            with open('sample.xlsx', 'rb') as f:
                data = f.read()
                new_file = request.env['other_equipment.trans.excel'].create({
                    'name': '工器具導出數據',
                    'file': data
                })
                os.remove('sample.xlsx')
            return json.dumps({'error': 0, 'message': '下載成功', 'file_id': new_file.id})
        except:
            return json.dumps({'error': 1, 'message': '下載失敗'})

    @http.route('/other_equipment/down_wrong_file', type='http', auth="user", methods=['GET'])
    def down_wrong_file(self, **kwargs):
        '''
        返回错误excel内容
        :param kwargs: file_id
        :return:
        '''
        file_id = int(kwargs['file_id'])
        filetype = kwargs['type']
        wb = request.env['other_equipment.trans.excel'].browse(file_id)
        response = request.make_response(wb.file)
        if filetype == '錯誤':
            response.headers["Content-Disposition"] = "attachment; filename={}". \
                format((wb.name + '错误.xls').encode().decode('latin-1'))
        if filetype == '下載':
            response.headers["Content-Disposition"] = "attachment; filename={}". \
                format((wb.name + '.xlsx').encode().decode('latin-1'))
        return response