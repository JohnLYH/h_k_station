# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields


class EmployeesGet(models.Model):
    _inherit = 'res.users'

    post = fields.Char(string='崗位')
    role = fields.Char(string='角色')
    state = fields.Char(string='狀態')

    @api.model
    def get_users(self,department_id):
        '''
          部门下的人员
        :param department_id: 是表的id 不是部门字段departmentId
        :return:
        '''
        users = self.env['res.users'].search_read([('departments','=',department_id)])
        # department_hierarchy departmentId
        department = self.env['user.department'].search([('id','=',department_id)])
        for user in users:
            if department:
                if department.department_hierarchy == 3:
                     user['department_name'] = department.name
                else:
                    user['department_name'] = None

        return users

    @api.model
    def page_size(self,**kw):
        users = self.env['res.users'].search_read([])
        # department_hierarchy departmentId
        return users[:kw['size']]    \

    @api.model
    def init_record(self,**kw):
        users = self.env['res.users'].search_read([])
        # department_hierarchy departmentId
        return users[:10]

    @api.model
    def current_change(self,**kw):
        users = self.env['res.users'].search_read([])
        # department_hierarchy departmentId
        return users[(kw['record'] - 1)*kw['page']: kw['record']*kw['page']]

    @api.model
    def get_department_users(self):
        department_tree = []

        # # 客运部
        # parent_department_ids = self.env['cdtct_dingtalk.cdtct_dingtalk_department'].sudo(1).search(
        #     [('department_hierarchy', '=', 1)])
        # for parent_department_id in parent_department_ids:
        #     parent_department = {'label': parent_department_id.name}
        #     parent_department['id'] = parent_department_id.id
        #
        #     # 中心部门
        #     gentral_department_ids = self.env['cdtct_dingtalk.cdtct_dingtalk_department'].sudo(1).search_read(
        #         [('parentid', '=', parent_department_id.departmentId)], ['parentid', 'name', 'id', 'departmentId'])
        #     child_departments = []
        #     for gentral_department_id in gentral_department_ids:
        #         department_map = {}
        #         department_map['label'] = gentral_department_id.get('name')
        #         department_map['id'] = gentral_department_id.get('id')
        #
        #         gentral_department_department_id = gentral_department_id.get('departmentId')
        #
        #         site_department_ids = self.env['cdtct_dingtalk.cdtct_dingtalk_department'].sudo(1).search_read(
        #             [('parentid', '=', gentral_department_department_id)], ['parentid', 'name', 'id', 'departmentId'])
        #         # 站点部门
        #         site_department_list = []
        #         for site_department_id in site_department_ids:
        #             site_department_map = {}
        #             site_department_map['label'] = site_department_id.get('name')
        #             site_department_map['id'] = site_department_id.get('id')
        #             site_department_list.append(site_department_map)
        #         department_map['children'] = site_department_list
        #         child_departments.append(department_map)
        #     parent_department['children'] = child_departments
        #     department_tree.append(parent_department)
        #
        # return department_tree


