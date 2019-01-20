# -*- coding: utf-8 -*-
import base64
import datetime
import json
import random
import time
from datetime import datetime as dt
import os
import openpyxl
import xlwt
from openpyxl import load_workbook, Workbook
from openpyxl.styles import PatternFill
from openpyxl.writer.excel import save_virtual_workbook


from odoo import http
from odoo.http import request

import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.writer.excel import save_virtual_workbook

ROW_1_LIST = ['Work Order No', 'Work Nature Level 1', 'Work Nature Level 2', 'Equipment No',
              'Equipment Description', 'Equipment Class', 'Equipment Class Description', 'Work Group',
              'Work Group Name', 'Standard Job Code', 'Standard Job Description', 'Standard Job ParamSet Name',
              'Person In Charge', 'Priority', 'Quantity', 'Work Order Description', 'Planned Start Date',
              'Planned Completion Date', 'Actual Start Date', 'Actual Complete Date', 'Status',
              'Service Break Down', 'Start Work Date', 'Finish Work Date', 'Line Code', 'Direction Code',
              'Location From Code', 'Detail IDs', 'Hash X', 'Hash Y']

OTHER_ROW_1_LIST = ['EQUIPMENT No.', 'EQUIPMENT', 'BRAND', 'MODEL', 'SERIAL_NO', 'MANUAL REF. NO.', 'EQUIPMENT OWNER',
                    'LOCATION OF EQUIPMENT', 'FREQ. OF CAL.', 'CALIBRATION BODY',
                    'CALIBRATION REQUIPEMNETS  (SEE NOTE)', 'LAST MAINTENANCE DATE',
                    'MAINTENANCE DUE DATE', 'STATUS', 'REMARK']

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

    @http.route('/maintenance_plan/materials_upload_files', auth='user', csrf=False, methods=['POST'])
    def materials_upload_files(self, **kw):
        try:
            # 設備類型
            field_type = kw['field_type']
            edition = kw['edition']
            file = kw['file']
            # 編號
            numbering = kw['numbering']
            select_file_name = file.filename
            # 設備型號
            equipment_id = kw['id']
            # 上傳的文件時pdf還是視頻
            upload_tpye = kw['upload_tpye']
            # 判斷這個型號下是否有相同的版本號或者編號存在
            # maintenance_plan.reference_materials_manage
            materials_manage_count = request.env['maintenance_plan.reference_materials_manage'].search_count([
                ('equipment_id', '=', equipment_id), ('field_type', '=', field_type), '|',
                ('numbering', '=', numbering), ('edition', '=', edition)])
            if materials_manage_count > 0:
                return json.dumps({'error': 1, 'message': '上傳失敗,已存在相同的編號或者版本'})
            file_name = str(int(time.time())) + str(random.randint(1, 1000)) + select_file_name
            file.save(file_name)
            with open(file_name, "rb") as e:
                b64str = base64.b64encode(e.read())
            os.remove(file_name)
            values = {
                'equipment_id': int(equipment_id),
                'field_type': field_type,
                'edition': edition,
                'numbering': numbering,
                'select_file': b64str,
                'select_file_name': select_file_name,
                'upload_tpye': upload_tpye
            }
            equipment_model = request.env['maintenance_plan.equipment_model'].sudo().search([('id', '=', equipment_id)])
            if upload_tpye == 'mp4':
                values['status'] = True
                equipment_model.write({'reference_materials_manage_ids': [(0, 0, values)]})
            else:
                equipment_model.write({'reference_materials_manage_ids': [(0, 0, values)]})
                # TODO：生成審批記錄
            # TODO: 生成記錄
            try:
                # 變更原因
                reasons_change = kw['reasons_change']
            except:
                reasons_change = ''
            try:
                # 變更細節
                reasons_details = kw['reasons_details']
            except:
                reasons_details = ''
            operation_type = '新增'
            user_id = request.uid
            operation_time = datetime.datetime.now()
            values = {
                'reasons_change': reasons_change,
                'reasons_details': reasons_details,
                'operation_type': operation_type,
                'user_id': user_id,
                'operation_time': operation_time,
                'field_type': field_type,
                'select_file_name': select_file_name,
                'edition': edition,
                'numbering': numbering,
            }
            equipment_model.write({'reference_materials_manage_records': [(0, 0, values)]})
        except:
            return json.dumps({'error': 1, 'message': '上傳失敗'})
        return json.dumps({'error': 0})

    @http.route('/maintenance_plan/materials_change', auth='user', csrf=False, methods=['POST'])
    def materials_change(self, **kw):
        try:
            # 設備類型
            field_type = kw['field_type']
            edition = kw['edition']
            # 編號
            numbering = kw['numbering']
            # 設備型號
            equipment_id = kw['res_id']
            # 上傳的文件是視頻還是pdf(pdf需要生成審批記錄,視頻不需要)
            upload_tpye = kw['upload_tpye']
            reference_materials_manage_id = kw['id']
            # 判斷這個型號下是否有相同的版本號或者編號存在
            materials_manage_count = request.env['maintenance_plan.reference_materials_manage'].search_count([
                ('equipment_id', '=', equipment_id), ('field_type', '=', field_type),
                ('id', '!=', reference_materials_manage_id), '|',
                ('numbering', '=', numbering), ('edition', '=', edition)])
            if materials_manage_count > 0:
                return json.dumps({'error': 1, 'message': '上傳失敗,已存在相同的編號或者版本'})
            if kw['file'] == 'undefined':
                values = {
                    'field_type': field_type,
                    'edition': edition,
                    'numbering': numbering,
                    'upload_tpye': upload_tpye
                }
                select_file_name = request.env['maintenance_plan.reference_materials_manage'].sudo().search(
                    [('id', '=', reference_materials_manage_id)]).select_file_name
            else:
                file = kw['file']
                select_file_name = file.filename
                file_name = str(int(time.time())) + str(random.randint(1, 1000)) + select_file_name
                file.save(file_name)
                with open(file_name, "rb") as e:
                    b64str = base64.b64encode(e.read())
                os.remove(file_name)
                values = {
                    'equipment_id': int(equipment_id),
                    'field_type': field_type,
                    'edition': edition,
                    'numbering': numbering,
                    'select_file': b64str,
                    'select_file_name': select_file_name,
                    'upload_tpye': upload_tpye
                }
            equipment_model = request.env['maintenance_plan.equipment_model'].sudo().search([('id', '=', equipment_id)])
            if upload_tpye == 'mp4':
                values['status'] = True
            equipment_model.write({'reference_materials_manage_ids': [(1, reference_materials_manage_id, values)]})
            # TODO：生成審批記錄
            # 生成記錄
            try:
                # 變更原因
                reasons_change = kw['reasons_change']
            except:
                reasons_change = ''
            try:
                # 變更細節
                reasons_details = kw['reasons_details']
            except:
                reasons_details = ''
            operation_type = '修改'
            user_id = request.uid
            operation_time = datetime.datetime.now()
            values = {
                'reasons_change': reasons_change,
                'reasons_details': reasons_details,
                'operation_type': operation_type,
                'user_id': user_id,
                'operation_time': operation_time,
                'field_type': field_type,
                'select_file_name': select_file_name,
                'edition': edition,
                'numbering': numbering,
            }
            equipment_model.write({'reference_materials_manage_records': [(0, 0, values)]})
        except:
            return json.dumps({'error': 1, 'message': '上傳失敗'})
        return json.dumps({'error': 0})


class OtherEquipment(http.Controller):
    @staticmethod
    def excel_validate(request, new_sheet, num, cols_list, style):
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

            if new_sheet.cell(num, col).value is None:
                pass
            elif col == 7:
                departments = new_sheet.cell(num, col).value
                if not request.env['user.department'].sudo().search([('name', '=', departments)]):
                    new_sheet.cell(num, col).fill = style
                    row_error = True
                else:
                    pass
            else:
                freq_of_cal = new_sheet.cell(num, col).value
                if freq_of_cal == 'ON\nCONDITION':
                    pass
                else:
                    try:
                        freq_of_cal = int(freq_of_cal)
                    except:
                        new_sheet.cell(num, col).fill = style
                        row_error = True
        return row_error

    @staticmethod
    def check_date(new_sheet, num, cols_list, style):
        row_error = False
        for col in cols_list:
            if new_sheet.cell(num, col).value is None:
                pass
            else:
                try:
                    dt.strptime(new_sheet.cell(num, col).value, '%Y/%m/%d')
                except Exception as e:
                    try:
                        dt.strptime(new_sheet.cell(num, col).value, '%Y-%m-%d')
                    except:
                        new_sheet.cell(num, col).fill = style
                        row_error = True
        return row_error

    @staticmethod
    def check_none(new_sheet, num, cols_list, style):
        row_error = False
        for col in cols_list:
            if new_sheet.cell(num, col).value is None:
                new_sheet.cell(num, col).fill = style
                row_error = True
            if col == 14:
                if new_sheet.cell(num, col).value in ['OK', 'Expired', 'Scraped']:
                    pass
                else:
                    new_sheet.cell(num, col).fill = style
                    row_error = True
            if col == 1:
                equipment_num = new_sheet.cell(num, col).value
                if new_sheet.cell(num, 7).value:
                    departments = new_sheet.cell(num, 7).value
                    # 檢查當前組是否有這個設備編號了
                    if request.env['maintenance_plan.other_equipment'].sudo().search_count(
                            [('equipment_num', '=', equipment_num),
                             ('departments.name', '=', departments)]) > 0:
                        new_sheet.cell(num, col).fill = style
                        row_error = True
                else:
                    if request.env['maintenance_plan.other_equipment'].sudo().search_count(
                            [('equipment_num', '=', equipment_num)]) > 0:
                        new_sheet.cell(num, col).fill = style
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
        try:
            file = kwargs['file']
            filename = kwargs['file'].filename
            workbook = load_workbook(file)
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
                    if [i.value for i in row] != OTHER_ROW_1_LIST:
                        return json.dumps({'message': '表格不符', 'error': True})
                else:
                    print([i.value for i in row])
                    # 這裡是檢測日期格式是否正確
                    row_error = self.check_date(sheet, n_row, [12, 13], red_style)
                    # 檢驗三個必填字段是否為空
                    row_error2 = self.check_none(sheet, n_row, [1, 2, 14], red_style)
                    # 這裡檢查參數是否合格
                    row_error3 = self.excel_validate(request, sheet, n_row,
                                                     [7, 9], red_style)
                    if row_error or row_error2 or row_error3:
                        error = True
                    else:
                        # 設備編號
                        equipment_num = sheet.cell(n_row, 1).value
                        # 設備名稱
                        equipment_name = sheet.cell(n_row, 2).value
                        # 品牌
                        brand = sheet.cell(n_row, 3).value
                        # 型號
                        model = sheet.cell(n_row, 4).value
                        # 序列號
                        serial_no = sheet.cell(n_row, 5).value
                        # 參考手冊編號
                        manual_ref_no = sheet.cell(n_row, 6).value
                        # 設備擁有者
                        equipment_owner = sheet.cell(n_row, 7).value
                        # 設備位置
                        location_of_equipment = sheet.cell(n_row, 8).value
                        # 檢驗週期
                        freq_of_cal = sheet.cell(n_row,9).value
                        # 檢驗主體
                        calibration_body = sheet.cell(n_row, 10).value
                        # 檢驗要求
                        calibration_requipemnets = sheet.cell(n_row, 11).value
                        # 最後維護日期
                        last_maintenance_date = sheet.cell(n_row, 12).value
                        # 應用到期時間
                        maintenance_due_data = sheet.cell(n_row, 13).value
                        # 狀態
                        status = sheet.cell(n_row, 14).value
                        # 備註
                        remark = sheet.cell(n_row, 15).value
                        equipment_owner = request.env['user.department'].sudo().search([('name', '=', equipment_owner)]).id
                        records = request.env['maintenance_plan.other_equipment'].create({
                            'departments': equipment_owner, 'equipment_num': equipment_num,
                            'equipment_name': equipment_name, 'brand': brand, 'model': model,
                            'serial_no': serial_no, 'manual_ref_no': manual_ref_no,
                            'location_of_equipment': location_of_equipment,
                            'freq_of_cal': freq_of_cal, 'calibration_body': calibration_body,
                            'calibration_requipemnets': calibration_requipemnets,
                            'last_maintenance_date': last_maintenance_date, 'status': status,
                            'maintenance_due_data': maintenance_due_data, 'type': 'create',
                        })
                        request.env['maintenance_plan.other_equipment_records'].create({
                            'other_equipment_id': records.id,
                            'operation_time': datetime.datetime.now(),
                            'operation_type': '新建',
                            'content': '工器具新增',
                            'user_id': request.uid,
                            'remark': remark,
                        })
                        error = False
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
        except:
            error = True
            return json.dumps({'error': error, 'message': '上傳失敗'})

    @http.route('/other_equipment/get_in_excel', type='http', website=True, csrf=False, auth='user')
    def get_in_excel(self, domains):
        '''
        工器具管理導出excel按鈕
        :param kwargs: 需要導出的domian條件
        :return:
        '''
        arr = []
        # try:
        if domains:
            x = domains.split(',')
            num = int(len(x)/3 + 1)
            for i in range(1, num):
                tuples = (x[3*i-3], x[3*i-2], x[3*i-1])
                arr.append(tuples)
            other_equipments = request.env['maintenance_plan.other_equipment'].search(arr)
        else:
            other_equipments = request.env['maintenance_plan.other_equipment'].search([])
        wb = Workbook()
        # 激活 worksheet
        ws = wb.active
        ws.append(OTHER_ROW_1_LIST)
        len_other_equipments = len(other_equipments)
        for i in range(1, len_other_equipments+1):
            my_records = [
                other_equipments[i-1].equipment_num if other_equipments[i-1].equipment_num else '',
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
        print('xxx')
        file_name = str(time.time()) + str(random.randint(1, 10000)) + "sample.xlsx"
        wb.save(file_name)
        with open(file_name, 'rb') as f:
            data = f.read()
            new_file = request.env['maintenance_plan.trans.excel'].create({
                'name': '工器具導出數據',
                'file': data
            })
            os.remove(file_name)
        return json.dumps({'error': 0, 'message': '下載成功', 'file_id': new_file.id})
        # except:
        #     return json.dumps({'error': 1, 'message': '下載失敗'})

    @http.route('/other_equipment/down_wrong_file', type='http', auth="user", methods=['GET'])
    def down_wrong_file(self, **kwargs):
        '''
        返回错误excel内容
        :param kwargs: file_id
        :return:
        '''
        file_id = int(kwargs['file_id'])
        filetype = kwargs['type']
        wb = request.env['maintenance_plan.trans.excel'].browse(file_id)
        response = request.make_response(wb.file)
        if filetype == '錯誤':
            response.headers["Content-Disposition"] = "attachment; filename={}". \
                format((wb.name + '错误.xlsx').encode().decode('latin-1'))
        if filetype == '下載':
            response.headers["Content-Disposition"] = "attachment; filename={}". \
                format((wb.name + '.xlsx').encode().decode('latin-1'))
        return response
