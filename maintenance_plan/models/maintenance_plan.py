# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api

STATUS = [
    ('be_executed', '待執行'), ('pending_approval', '待審批'), ('closed', '已關閉')
]


class MaintenancePlan(models.Model):
    _name = 'maintenance_plan.maintenance.plan'
    _description = '維修計劃'

    num = fields.Char('工單編號')
    work_order_type = fields.Char('工單類型')
    work_order_description = fields.Text('工單描述')
    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    equipment_num = fields.Char('設備編號', compute='_com_equipment', store=True)
    plan_start_time = fields.Date('計劃執行時間(開始)')
    plan_end_time = fields.Date('計劃執行時間(結束)')
    display_plan_time = fields.Char('計劃執行時間', compute='_com_plan_time', store=True)
    action_time = fields.Date('具體執行時間')
    display_action_time = fields.Char('具體執行時間', compute='_com_action_time', store=True)
    # TODO：執行班組
    actual_start_time = fields.Datetime('實際開始時間')
    actual_end_time = fields.Datetime('實際結束時間')
    status = fields.Selection(STATUS, string='狀態')


    @api.depends('equipment_id')
    def _com_equipment(self):
        for record in self:
            if len(record.equipment_id) != 0:
                record.equipment_num = record.equipment_id.num

    @api.depends('plan_start_time', 'plan_end_time')
    def _com_plan_time(self):
        for record in self:
            if record.plan_start_time is not False and record.plan_end_time is not False:
                record.display_plan_time = '{}至{}'.format(
                    record.plan_start_time.replace('-', '/'),
                    record.plan_end_time.replace('-', '/')
                )

    @api.depends('action_time')
    def _com_action_time(self):
        for record in self:
            if record.action_time is not False:
                record.display_action_time = record.action_time.replace('-', '/')

    @api.model
    def get_config(self):
        config = self.env['maintenance_plan.config'].sudo().get_values()
        return config

    @api.model
    def get_departs(self):
        config = self.env['maintenance_plan.config'].sudo().get_values()
        return config
