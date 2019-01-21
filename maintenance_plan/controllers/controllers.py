# -*- coding: utf-8 -*-
import base64
import datetime
import json
import random
import time
from datetime import datetime as dt
import os

from odoo import http
from odoo.http import request

import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.writer.excel import save_virtual_workbook

APP_DIR = os.path.dirname(os.path.dirname(__file__))


class MaintenancePlan(http.Controller):

    @staticmethod
    def get_row1_list_colnum(row1_list, value):
        '''
        獲取list中某詞的index并+1，若沒有則返回None
        :param row1_list:
        :param value:
        :return:
        '''
        try:
            return {'col'}
        except ValueError as e:
            return None

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
                title_list = [i.value for i in row]
            else:
                work_num = self.get_row1_list_colnum(title_list, 'Work Order No')  # 工單編號
                work_order_type = self.get_row1_list_colnum(title_list, 'Work Nature Level 1')  # 工單類型
                equipment_num = self.get_row1_list_colnum(title_list, 'Equipment No')  # 設備編號
                standard_job = self.get_row1_list_colnum(title_list, 'Standard Job Code')  # 標準工作
                work_order_description = self.get_row1_list_colnum(title_list, 'Work Order Description')  # 工單描述
                plan_start_time = self.get_row1_list_colnum(title_list, 'Planned Start Date')  # 建議開始時間
                plan_end_time = self.get_row1_list_colnum(title_list, 'Planned Completion Date')  # 建議結束時間
                # 檢查是否有colnum未存在的列
                none_col_list = []
                for check_col in [work_num, work_order_type, equipment_num, standard_job, work_order_description,
                                  plan_start_time, plan_end_time]:
                    if check_col is None:
                        none_col_list.append()


        # if error is True:
        #     new_file = request.env['maintenance_plan.trans.excel'].create({
        #         'name': filename.split('.')[0],
        #         'file': save_virtual_workbook(workbook)
        #     })
        #     return json.dumps({'error': error, 'message': '文件有部分錯誤信息，請修改后再次傳入', 'file_id': new_file.id})
        # else:
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
            # 判斷這個型號下是否有相同的版本號或者編號存在
            # maintenance_plan.reference_materials_manage
            materials_manage_count = request.env['maintenance_plan.reference_materials_manage'].search_count([
                ('equipment_id', '=', equipment_id), ('field_type', '=', field_type), '|',
                ('numbering', '=', numbering), ('edition', '=', edition)])
            if materials_manage_count > 0:
                return json.dumps({'error': 1, 'message': '上傳失敗,已存在相同的編號或者版本'})
            # TODO:修改並發
            file.save(select_file_name)
            # open_file = open(select_file_name, "rb")
            # b64str = base64.b64encode(open_file.read())
            # open_file.close()
            with open(select_file_name, "rb") as e:
                b64str = base64.b64encode(e.read())
            os.remove(select_file_name)
            values = {
                'equipment_id': int(equipment_id),
                'field_type': field_type,
                'edition': edition,
                'numbering': numbering,
                'select_file': b64str,
                'select_file_name': select_file_name
            }
            equipment_model = request.env['maintenance_plan.equipment_model'].sudo().search([('id', '=', equipment_id)])
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
            print(user_id)
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
                    'select_file_name': select_file_name
                }
            equipment_model = request.env['maintenance_plan.equipment_model'].sudo().search([('id', '=', equipment_id)])
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
