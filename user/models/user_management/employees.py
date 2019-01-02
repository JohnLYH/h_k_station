# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields


class EmployeesGet(models.Model):
    _name = 'user.employees_get'
    _description = '用来获取角色'

    @models
    def get_employees(self):
        '''
          部门下的人员
        :param department_id: 是表的id 不是部门字段departmentId
        :return:
        '''
        users = self.env['cdtct_dingtalk.cdtct_dingtalk_users'].search_read([()])
        # department_hierarchy departmentId
        return users
