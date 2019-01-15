# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields, api

from .approval_management.order_approval import STATUS as APPROVER_STATUS

STATUS = [
    ('be_executed', '待執行'), ('executing', '執行中'), ('pending_approval', '待審批'), ('closed', '已關閉')
]


class MaintenancePlan(models.Model):
    _name = 'maintenance_plan.maintenance.plan'
    _description = '維修計劃'
    _rec_name = 'num'

    num = fields.Char('工單編號')
    work_order_type = fields.Char('工單類型')
    work_order_description = fields.Text('工單描述')
    standard_job_id = fields.Many2one('maintenance_plan.standard.job', string='標準工作')
    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備')
    equipment_num = fields.Char('設備編號', compute='_com_equipment', store=True)
    plan_start_time = fields.Date('計劃執行時間(開始)')
    plan_end_time = fields.Date('計劃執行時間(結束)')
    display_plan_time = fields.Char('計劃執行時間', compute='_com_plan_time', store=True)
    action_time = fields.Date('具體執行時間')
    display_action_time = fields.Char('具體執行時間', compute='_com_action_time', store=True)
    action_dep_id = fields.Many2one('user.department', string='執行班組')
    actual_start_time = fields.Datetime('實際開始時間')
    actual_end_time = fields.Datetime('實際結束時間')
    status = fields.Selection(STATUS, string='狀態')
    # TODO: compute
    order_approval_ids = fields.One2many('maintenance_plan.order.approval', 'work_order_id', string='審批')
    approver_status = fields.Selection(APPROVER_STATUS, string='審批狀態')
    submit_user_id = fields.Many2one('res.users', string='提交人')
    approver_user_id = fields.Many2one('res.users', string='審批人')
    last_submit_date = fields.Datetime('最後提交時間')
    last_approver_date = fields.Datetime('最後審批時間')

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

    def recursion_tree_data(self, cats):
        '''
        递归添加树
        :param cats: 根节点的list
        :return:
        '''
        for cat in cats:
            if len(cat['child_ids']) != 0:
                cat['children'] = self.env['user.department'].search_read([
                    ('id', 'in', cat['child_ids'])], fields=['name', 'child_ids', 'parent_left', 'parent_right'])
                self.recursion_tree_data(cat['children'])
        return

    @api.model
    def get_departs(self):
        '''
        獲取編輯工單頁的執行班組下拉
        :return:
        '''
        deps = self.env['user.department'].search_read([
            ('parent_id', '=', None)
        ], fields=['name', 'child_ids', 'parent_left', 'parent_right'])
        self.recursion_tree_data(deps)
        return deps

    @api.model
    def assign_work_order(self, order_id, action_time, dep):
        '''
        指派工單
        :param order_id: 工單id
        :param action_time: 具體執行時間
        :param dep: 執行班組list，取最後一個
        :return:
        '''
        self.browse(order_id).write({
            'action_time': action_time,
            'action_dep_id': dep[-1],
            'status': 'be_executed'
        })
        return