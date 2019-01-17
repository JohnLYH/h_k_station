# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import os

from odoo import models, fields, api

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


class Config(models.TransientModel):
    _inherit = 'res.config.settings'
    _name = 'maintenance_plan.config'

    max_advance_days = fields.Integer('最大提前天數')
    max_delay_days = fields.Integer('最大延遲天數')
    send_email_time = fields.Datetime('逾期工單郵件發送時間')

    def set_values(self):
        self.env['ir.config_parameter'] \
            .sudo().set_param('maintenance_plan_max_advance_days', self.max_advance_days)
        self.env['ir.config_parameter'] \
            .sudo().set_param('maintenance_plan_max_delay_days', self.max_delay_days)
        self.env['ir.config_parameter'] \
            .sudo().set_param('maintenance_plan_send_email_time', self.send_email_time)

    def get_values(self):
        max_advance_days = self.env['ir.config_parameter'] \
            .sudo().get_param('maintenance_plan_max_advance_days', default=0)
        max_delay_days = self.env['ir.config_parameter'] \
            .sudo().get_param('maintenance_plan_max_delay_days', default=0)
        send_email_time = self.env['ir.config_parameter'] \
            .sudo().get_param('maintenance_plan_send_email_time', default=None)
        return dict(max_advance_days=int(max_advance_days), max_delay_days=int(max_delay_days),
                    send_email_time=send_email_time)

    @api.model
    def get_ref_id(self, list_string_name):
        result = []
        for name in list_string_name:
            result.append(self.env.ref(name).id)
        return result