# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields


class EmployeesGet(models.Model):
    _name = 'user.employees_get'
    _description = '用来获取角色'

    name = fields.Char(string='姓名')
    account = fields.Char(string='賬號')
    post = fields.Char(string='崗位')
    role = fields.Char(string='角色')
    email = fields.Char(string='郵箱')
    state = fields.Char(string='狀態')

    @api.model
    def get_users(self,department_id):
        '''
          部门下的人员
        :param department_id: 是表的id 不是部门字段departmentId
        :return:
        '''
        users = self.env['cdtct_dingtalk.cdtct_dingtalk_users'].search_read([('departments','=',department_id)])
        # department_hierarchy departmentId
        department = self.env['cdtct_dingtalk.cdtct_dingtalk_department'].search([('id','=',department_id)])
        for user in users:
            if department:
                if department.department_hierarchy == 3:
                     user['department_name'] = department.name
                else:
                    user['department_name'] = None

        return users

    @api.model
    def page_size(self,**kw):
        users = self.env['cdtct_dingtalk.cdtct_dingtalk_users'].search_read([])
        # department_hierarchy departmentId
        return users[:kw['size']]    \

    @api.model
    def init_record(self,**kw):
        users = self.env['cdtct_dingtalk.cdtct_dingtalk_users'].search_read([])
        # department_hierarchy departmentId
        return users[:10]

    @api.model
    def current_change(self,**kw):
        users = self.env['cdtct_dingtalk.cdtct_dingtalk_users'].search_read([])
        # department_hierarchy departmentId
        return users[(kw['record'] - 1)*kw['page']: kw['record']*kw['page']]


