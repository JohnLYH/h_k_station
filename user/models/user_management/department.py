# !user/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xlrd
import base64


class Department(models.Model):
    _name = 'user.department'
    _rec_name = 'name'
    _description = '部門信息'
    _order = 'parent_order desc, department_order'
    _parent_store = True
    _parent_order = 'department_order'

    name = fields.Char('部门名称', readonly=True)
    department_order = fields.Integer('部门编号', readonly=True)
    parent_order = fields.Integer('父部门编号', readonly=True)

    parent_id = fields.Many2one('user.department', string='父部门', ondelete='cascade')
    child_ids = fields.One2many('user.department', 'parent_id', string='子部门')

    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

    users = fields.Many2many(
        'user.employees_get',
        'user_department_rel',
        'user_id',
        'udepartment_id', readonly=True)

    @api.model
    def department_information(self):
        data = xlrd.open_workbook(file_contents=base64.decodebytes(self.env['user.import_date'].search([])[-1].file))
        sheet_data = data.sheet_by_name(data.sheet_names()[0])
        rows = sheet_data.nrows
        cols = sheet_data.ncols
        keys = ('parent','child')
        one_sheet_content =[]
        for i in range(1, rows):
            row_content = []
            k = 6
            for j in range(2):
                k += j
                cell = sheet_data.cell_value(i, k)
                row_content.append(cell)
                one_dict = dict(zip(keys, row_content))

            one_sheet_content.append(one_dict)
        for i, item in enumerate(one_sheet_content):
            dic = {}
            record = self.search([('name','=',item['parent'])])
            if not record and item['parent']:
                dic['name']=item['parent']
                self.create(dic)
            record_child = self.search([('name', '=', item['child'])])
            if not record_child and item['child']:
                dic['name']= item['child']
                self.create(dic)

    @api.model
    def create(self, vals):
        record = super(Department, self).create(vals)
        vals['parent_order']=record.id
        print(record.id)
        return record