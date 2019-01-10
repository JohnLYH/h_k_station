# -*- coding: utf-8 -*-

from odoo import api, models, fields
import base64
import xlrd
import datetime


class InventoryExport(models.Model):
    _name = 'equipment.inventory.export'

    name = fields.Binary(string='選擇文件導入信息')

    def export(self):
        data = xlrd.open_workbook(file_contents=base64.decodebytes(self.name))
        sheet_data = data.sheet_by_name(data.sheet_names()[0])
        rows = sheet_data.nrows
        cols = sheet_data.ncols
        keys = ('inventory_id', 'inventory_description', 'work_prepare', 'inventory_count', 'lastest_update_time')
        one_sheet_content = []
        for i in range(1, rows):
            row_content = []
            for j in range(cols):
                ctype = sheet_data.cell(i, j).ctype  # 獲取當前表單的數據類型
                cell = sheet_data.cell_value(i, j)
                if ctype == 3:
                    cell = xlrd.xldate.xldate_as_tuple(sheet_data.cell(i, j).value, 0)
                    cell = datetime.datetime(*cell)
                    cell = cell + datetime.timedelta(hours=-8) # 页面显示需要减去8个小时
                    cell = cell.strftime('%Y-%m-%d %H:%M:%S')
                if j == 2 and cell:
                    re_list = []  # 用來存放標準工作的ID
                    if ',' in cell:
                        cell_list = cell.split(',')
                        # 用來分割字符串
                        for lis in cell_list:
                            record_id = self.env['maintenance_plan.standard.job'].search([('name', '=', lis)])
                            # 判断当前的记录是否存在
                            if not  record_id:
                                record = self.env['maintenance_plan.standard.job'].create({'name': lis})
                                re_list.append(record.id)
                            else:
                                re_list.append(record_id.id)
                        cell = [(6, 0, re_list)]
                    if '，' in cell:
                        cell_list = cell.split('，')
                        # 用來分割字符串
                        for lis in cell_list:
                            record_id = self.env['maintenance_plan.standard.job'].search([('name', '=', lis)])
                            # 判断当前的记录是否存在
                            if not  record_id:
                                record = self.env['maintenance_plan.standard.job'].create({'name': lis})
                                re_list.append(record.id)
                            else:
                                re_list.append(record_id.id)
                        cell = [(6, 0, re_list)]
                row_content.append(cell)
            one_dict = dict(zip(keys, row_content))
            one_sheet_content.append(one_dict)
        for item in one_sheet_content:
            # 查看当前的库存编号是否存在 存在就不再创建
            record = self.env['equipment.inventory_management'].search(
                [('inventory_id', '=', item.get('inventory_id'))])
            if not record.id:
                self.env['equipment.inventory_management'].create(item)
