# -*- coding: utf-8 -*-

from odoo import api, models, fields


class PermissManage(models.Model):
    _inherit = 'res.groups'

    permission_illust = fields.Char(string='權限說明')
    user_person = fields.Integer(string='使用人數')
    state = fields.Selection([('正常', '正常'), ('已禁用', '已禁用')], string='狀態', default='正常')

    # 计算本用户组的使用人数
    @api.model
    def calculate_per_couont(self, **kwargs):
        pass

    # 權限管理編輯操作
    @api.model
    def edit_save(self, **kw):
        rocord = self.env['res.groups'].search([('id', '=', kw.get('self_id'))])
        rocord.write({
            'name': kw.get('modify_name'),
            'permission_illust': kw.get('modify_per'),
            'implied_ids': [(6, 0, kw.get('per_id'))]
        })

    @api.model
    def get_permiss_role(self):
        config_dict = self.env['res.groups'].get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()
        record = self.search_read([('category_id', '=', category_id.id)])
        return record

    @api.model
    def get_disable_info_act(self, **kwargs):
        rec = self.search([('name', '=', kwargs.get('name'))])
        rec.write({'state': '已禁用'})

    # 获取当前组的角色
    @api.model
    def get_user_name_data(self, **kw):
        record = self.search([('id', '=', kw.get('group_id'))])
        lis = []
        for i in record.users:
            dic = {}
            dic['name'] = i.name
            lis.append(dic)
        return lis

    # 搜索权限页面的数据
    @api.model
    def permissions_search(self, **kw):
        if kw.get('chose') == 'all':
            record = self.search_read([('name','=',kw.get('name'))])
            return record
        elif kw.get('chose') == 'disable':
            record = self.search_read([('name','=',kw.get('name')),('state','=','禁用')])
            return record
        elif kw.get('chose') == 'normal':
            record = self.search_read([('name', '=', kw.get('name')), ('state', '=', '正常')])
            return record
        else:
            record =[]
            return record

    # 删除数据
    @api.model
    def delete_record(self, **kwargs):
        print(kwargs)
        self.search([('id','=',kwargs.get('self_id'))]).unlink()
