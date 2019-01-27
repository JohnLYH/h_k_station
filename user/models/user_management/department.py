# !user/bin/env python3
# -*- coding: utf-8 -*-
from odoo import models, fields, api
import xlrd
import base64

lis_departmnet_id = [] # 全局变量用来存放编辑的时候的部门ID

class Department(models.Model):
    _name = 'user.department'
    _rec_name = 'name'
    _description = '部門信息'
    # _order = 'parent_order desc, department_order'
    _parent_store = True
    # _parent_order = 'department_order'

    name = fields.Char('部门名称', readonly=True)
    department_order = fields.Integer('部门编号', readonly=True)
    parent_order = fields.Integer('父部门编号', readonly=True)
    department_hierarchy = fields.Integer(string='部门层级')  # 用于计算
    parent_id = fields.Many2one('user.department', string='父部门')
    child_ids = fields.One2many('user.department', 'parent_id', string='子部门')
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)

    users = fields.Many2many(
        'res.users',
        'user_department_rel',
        'user_id',
        'udepartment_id', readonly=True)

    @api.model
    def department_information(self):
        '''
        导入人员信息
        '''

        data = xlrd.open_workbook(file_contents=base64.decodebytes(self.env['user.import_date'].search([])[-1].file))
        sheet_data = data.sheet_by_name(data.sheet_names()[0])
        rows = sheet_data.nrows  # 获取有多好行
        cols = sheet_data.ncols
        keys = ('name',)  # 用来作为父部门 和 子部门装载器
        for i in range(1, rows):
            for j in range(cols):
                cell = sheet_data.cell_value(i, j)
                if cell:
                    if j == 0:
                        one_record = self.search([('name', '=', cell)])
                        if not one_record:
                            one_class = self.create({'name': cell, 'department_hierarchy': 1})
                            one_class.department_order = one_class.id
                        else:
                            one_class = one_record
                    if j == 1:
                        two_record = self.search([('name', '=', cell)])
                        if not two_record:
                            two_class = self.create({
                                'name': cell,
                                'parent_order': one_class.id,
                                'parent_id': one_class.id,
                                'department_hierarchy': 2
                            })
                            two_class.department_order = two_class.id
                        else:
                            two_class = two_record
                    if j == 2:
                        three_record = self.search([('name', '=', cell)])
                        if not three_record:
                            three_class = self.create({
                                'name': cell,
                                'parent_order': two_class.id,
                                'parent_id': two_class.id,
                                'department_hierarchy': 3
                            })
                            three_class.department_order = three_class.id

    @api.model
    def get_department_users(self):
        '''
        页面初始化的时候 获取角色名称组
        :return: 角色组
        '''
        lis = []  # 存放角色组
        record = self.env['res.users'].search_read([])
        for i in record:
            rec = {}
            rec['name'] = i.get('role')
            if rec['name']:
                if not rec['name'] in lis:
                    lis.append(rec)
        return lis

    # 获取权限组
    @api.model
    def get_pers_group(self):
        config_dict = self.env['res.groups'].get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()
        # 获取父节点
        # 组装子节点
        category_record_ids = [self.env.ref('{}.{}'.format(config_dict['module_name'], i)).id
                               for i in config_dict['category_id_list']]
        cats = self.env['res.groups'].search_read(
            [('category_id', 'in', category_record_ids), ('parent_id', '=', None)], fields=[
                'name', 'parent_id', 'child_ids', 'parent_left', 'parent_right', 'category_id'], order='sequence')
        self.env['res.groups'].recursion_tree_data(cats)
        return cats

    # 层级选择
    @api.model
    def get_equipment_class(self, id=False):
        '''
        获取分组
        :return:
        '''
        rst = []
        class_a = self.env['user.department'].search_read([('parent_id', '=', id)],
                                                          fields=['child_ids', 'name'])
        for record in class_a:
            vals = {
                'value': record['id'],
                'label': record['name'],
            }
            children = self.get_equipment_class(record['id'])
            if children:
                vals['children'] = children
            rst.append(vals)
        return rst

    # 默认部门权限
    @api.model
    def get_default_department_edit(self, **kwargs):
        parent_id = self.env['res.users'].search([('id', '=', kwargs.get('self_id'))]).depertment_many.id
        del lis_departmnet_id[:]
        lis_record = self.get_parent(parent_id)

        return lis_record[::-1]

    def get_parent(self, parent_id):
        lis_departmnet_id.append(parent_id)
        local_rec = self.search([('id', '=', parent_id)])
        if local_rec.parent_id.id:
            return self.get_parent(local_rec.parent_id.id)

        else:
            return lis_departmnet_id
