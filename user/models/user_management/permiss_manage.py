# -*- coding: utf-8 -*-

from odoo import api, models, fields


class PermissManage(models.Model):
    _name = 'user.permiss_management'

    name = fields.Char(string='角色名稱')
    permission_illustrate = fields.Char(string='權限說明')
    user_person = fields.Integer(string='使用人數')
    state = fields.Char(string='狀態')