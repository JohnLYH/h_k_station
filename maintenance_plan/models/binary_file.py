# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class BinaryFile(models.Model):
    _name = 'maintenance_plan.binary.file'
    _description = '附件'

    file = fields.Binary('文件', attachment=True)
    filename = fields.Char('文件名')