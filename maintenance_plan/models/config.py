# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import os
import base64

from odoo import models, fields

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


class Config(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'maintenance_plan.config'

    max_advance_days = fields.Integer('最大提前天數')
    max_delay_days = fields.Integer('最大延遲天數')

    def set_values(self):
        self.env['ir.config_parameter'] \
            .set_param('maintenance_plan_max_advance_days', self.max_advance_days)
        self.env['ir.config_parameter'] \
            .set_param('maintenance_plan_max_delay_days', self.max_delay_days)

    def get_values(self):
        max_advance_days = self.env['ir.config_parameter'] \
            .get_param('maintenance_plan_max_advance_days', default=0)
        max_delay_days = self.env['ir.config_parameter'] \
            .get_param('maintenance_plan_max_delay_days', default=0)
        return dict(max_advance_days=int(max_advance_days), max_delay_days=int(max_delay_days))