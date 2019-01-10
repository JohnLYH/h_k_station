# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class Station(models.Model):
    _name = 'maintenance_plan.station'
    _description = '車站'
    _rec_name = 'name'

    name = fields.Char('車站名稱')