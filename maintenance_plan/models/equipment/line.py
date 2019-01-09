# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class Line(models.Model):
    _name = 'maintenance_plan.line'
    _description = '線別'
    _rec_name = 'name'

    name = fields.Char('線別名稱')