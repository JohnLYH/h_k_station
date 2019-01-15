# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class TransExcel(models.TransientModel):
    _name = 'other_equipment.trans.excel'
    _description = '临时错误文件模型'

    name = fields.Char('文件名')
    file = fields.Binary('文件内容')