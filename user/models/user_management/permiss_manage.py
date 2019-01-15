# -*- coding: utf-8 -*-

from odoo import api, models, fields


class PermissManage(models.Model):
    _inherit = 'res.groups'

    permission_illustrate = fields.Char(string='權限說明')
    user_person = fields.Integer(string='使用人數')
    state = fields.Selection([('正常','正常'),('已禁用','已禁用')],string='狀態',default='正常')

    # 權限管理編輯操作
    @api.model
    def edit_save(self, **kw):
        rocord = self.env['res.users'].search([('role', '=', kw.get('role_name'))])
        for i in rocord:
            i.write({'name': kw.get('modify_name')})

    @api.model
    def get_permiss_role(self):
        config_dict = self.env['res.groups'].get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()
        record = self.search_read([('category_id', '=',category_id.id)])
        return record

    @api.model
    def get_disable_info_act(self, **kwargs):
        rec = self.search([('name','=',kwargs.get('name'))])
        rec.write({'state':'已禁用'})

