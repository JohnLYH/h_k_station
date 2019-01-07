# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields


class EmployeesGet(models.Model):
    _inherit = 'res.users'

    post = fields.Char(string='崗位')
    role = fields.Char(string='角色')
    state = fields.Selection([('normal', '正常'), ('disable', '禁用')], default='normal')
    branch = fields.Char(string='員工部門')

    @api.model
    def get_users_info(self,department_id):
        '''
          部门下的人员
        :param department_id: 是表的id 不是部门字段departmentId
        :return:
        '''
        users = self.env['res.users'].search_read([('post','=',department_id)])
        # department_hierarchy departmentId
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
        lis = []
        users = self.env['user.department'].search_read([])
        for parent_department_id in users:
            parent_department = {'label': parent_department_id.get('name')}
            parent_department['id'] = parent_department_id.get('name')
            lis.append(parent_department)
        return lis

    @api.model
    def get_chose_user_info(self,name,chose):
        if chose == 'all':
            record = self.search_read([('name','=',name)])
        else:
            record = self.search_read([('name','=',name),('state','=',chose)])

        return  record

    @api.model
    def disable_info(self, **kw):
        print(kw.get('disable_id'))
        record = self.search([('login','=',kw.get('disable_id'))])
        record.write({'state':'disable'})


