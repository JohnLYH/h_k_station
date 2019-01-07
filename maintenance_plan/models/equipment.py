# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import fields, models


class Equipment(models.Model):
    _name = 'maintenance_plan.equipment'
    _description = '設備'

    num = fields.Char('Equipment No')  # 設備編號
    description = fields.Char('Equipment Description')  # 設備描述
    # TODO: 設備類別
    standard_job = fields.Char('Standard Job Description')  # 標準工作


