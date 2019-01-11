# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields


class EmployeesGet(models.Model):
    _inherit = 'res.users'

    post = fields.Char(string='崗位')
    role = fields.Char(string='角色')
    state = fields.Selection([('正常', '正常'), ('禁用', '禁用')], default='正常')
    branch = fields.Char(string='員工部門')

    @api.model
    def get_users_info(self, department_id, page=1, limit=10):
        '''
          部门下的人员
        :return:
        '''
        count = self.env['res.users'].search_count([('post', '=', department_id)])
        users = self.env['res.users'].search_read(
            [('post', '=', department_id)], limit=limit, offset=(page - 1) * limit,
            fields=['name', 'login', 'post', 'role', 'state', 'branch', 'email'])
        return {'users': users, 'count': count}

    @api.model
    def page_size(self, **kw):
        users = self.env['res.users'].search_read([])
        return users[:kw['size']]

    @ api.model
    def init_record(self, **kw):
        users = self.env['res.users'].search_read([])
        return users[:10]

    @api.model
    def current_change(self, **kw):
        users = self.env['res.users'].search_read([])
        return users[(kw['record'] - 1) * kw['page']: kw['record'] * kw['page']]

    @api.model
    def get_department_users(self):
        '''
        获取部门信息
        :return:
        '''

        department_tree = []

        # 一级部门
        one_department_ids = self.env['user.department'].sudo(1).search(
            [('department_hierarchy', '=', 1)])
        for parent_department_id in one_department_ids:
            parent_department = {'label': parent_department_id.name}
            parent_department['id'] = parent_department_id.id

            # 二级部门
            two_department_ids = self.env['user.department'].sudo(1).search_read(
                [('parent_order', '=', parent_department_id.department_order)], ['parent_order', 'name', 'id', 'department_order'])
            child_departments = []
            for two_department_id in two_department_ids:
                department_map = {}
                department_map['label'] = two_department_id.get('name')
                department_map['id'] = two_department_id.get('id')
                two_department_department_id = two_department_id.get('department_order')

                # 三级部门
                three_department_ids = self.env['user.department'].sudo(1).search_read(
                    [('parent_order', '=', two_department_department_id)], ['parent_order', 'name', 'id', 'department_order'])
                three_department_list = []
                for three_department_id in three_department_ids:
                    three_department_map = {}
                    three_department_map['label'] = three_department_id.get('name')
                    three_department_map['id'] = three_department_id.get('id')
                    three_department_list.append(three_department_map)
                department_map['children'] = three_department_list
                child_departments.append(department_map)
            parent_department['children'] = child_departments
            department_tree.append(parent_department)

        return department_tree

    @api.model
    def get_chose_user_info(self, name, chose):
        if chose == 'all':
            record = self.search_read([('name', '=', name)])
        else:
            record = self.search_read([('name', '=', name), ('state', '=', chose)])

        return record

    @api.model
    def disable_info(self, **kw):
        print(kw.get('disable_id'))
        record = self.search([('login', '=', kw.get('disable_id'))])
        record.write({'state': 'disable'})

    # 编辑人员信息
    @api.model
    def edit_per_information(self, **kw):
        record = self.search([('login', '=', kw.get('role_id'))])
        dic = {
            'name': kw.get('name'),
            # 'branch': kw.get('deparment'),
            'post': kw.get('post'),
            'role': kw.get('role'),
            'email': kw.get('role_email')
        }
        record.write(dic)

    # 獲取所有的部門 崗位 和員工角色
    @api.model
    def gt_all_department(self):
        lis = []
        post_lis = []  # 用來存放崗位
        dep_lis = []  # 用來存放部門
        role_lis = []  # 用來存放角色組
        record = self.search_read([], ['post', 'branch', 'role'])
        for post in record:
            dic = {}
            if post.get('post'):
                dic['value'] = post.get('id')
                dic['label'] = post.get('post')
                post_lis.append(dic)
        for dep in record:
            dep_dic = {}
            if dep.get('branch'):
                dep_dic['value'] = dep.get('id')
                dep_dic['label'] = dep.get('branch')
                dep_lis.append(dep_dic)
        for role in record:
            role_dic = {}
            if role.get('role'):
                role_dic['value'] = role.get('id')
                role_dic['label'] = role.get('role')
                role_lis.append(role_dic)
        lis.append(post_lis)
        lis.append(dep_lis)
        lis.append(role_lis)
        return lis

    # 修改密码
    @api.model
    def change_password_usr(self, **kw):
        record = self.search([('id', '=', kw.get('user_id'))])
        record.write({'password': kw.get('paw')})

    # 搜索权限页面的数据
    @api.model
    def permissions_search(self, **kw):
        print(kw)
