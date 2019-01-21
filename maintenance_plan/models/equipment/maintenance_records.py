# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api


class MaintenanceRecords(models.Model):
    _name = 'maintenance_plan.maintenance.records'
    _description = '設備維修記錄'

    equipment_id = fields.Many2one('maintenance_plan.equipment', compute='_com_work_order', store=True)
    work_order_id = fields.Many2one('maintenance_plan.maintenance.plan', '工單', required=True)
    equipment_serial_number = fields.Char('設備序列號', compute='_com_work_order', store=True)
    action_dep = fields.Char('執行班組', compute='_com_work_order', store=True)
    executor = fields.Char('執行人', compute='_com_work_order', store=True)
    actual_start_time = fields.Datetime('實際開始時間', compute='_com_work_order', store=True)
    actual_end_time = fields.Datetime('實際結束時間', compute='_com_work_order', store=True)

    @api.one
    @api.depends('work_order_id')
    def _com_work_order(self):
        self.equipment_id = self.work_order_id.equipment_id
        self.equipment_serial_number = self.work_order_id.equipment_id.serial_number
        self.action_dep = self.work_order_id.action_dep_id.name
        self.actual_start_time = self.work_order_id.actual_start_time
        self.actual_end_time = self.work_order_id.actual_end_time
