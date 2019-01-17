# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields
import xlrd
import base64


class ImportDate(models.Model):
    _name = 'user.import_date'
    _description = '導入人員信息'

    file = fields.Binary(string='選擇需要導入的文件')

    def import_record(self):
        '''
        用來導入人員的個人信息

        '''
        # TODO: 暫時的數據
        data = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet_data = data.sheet_by_name(data.sheet_names()[0])
        rows = sheet_data.nrows
        cols = sheet_data.ncols
        keys = ('login', 'name', 'email','role', 'post')
        one_sheet_content = []
        for i in range(1, rows):
            row_content = []
            for j in range(cols):
                cell = sheet_data.cell_value(i, j)
                row_content.append(cell)
                one_dict = dict(zip(keys, row_content))
            one_sheet_content.append(one_dict)
        for i, item in enumerate(one_sheet_content):
            record = self.env['res.users'].search([('login', '=', item.get('login'))])
            if not record.id:
                self.env['res.users'].create(item)
            else:
                del item['login']
                record.write(item)
