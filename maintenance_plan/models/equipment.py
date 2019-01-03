# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import fields, models


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'

    num = fields.Char('Equipment No')
