# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import datetime as dt
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

from ..approval_management.order_approval import STATUS as APPROVER_STATUS

STATUS = [
    ('be_executed', '待執行'), ('executing', '執行中'), ('pending_approval', '待審批'), ('closed', '已關閉')
]


class MaintenancePlan(models.Model):
    _name = 'maintenance_plan.maintenance.plan'
    _description = '維修計劃'
    _rec_name = 'num'
    _order = 'create_date DESC'

    def _default_order_forms(self):
        return [(0, 0, {'name': '對向波口測試', 'status': 'NOTBEGIN'}), (0, 0, {'name': '檢測證書', 'status': 'NOTBEGIN'})]

    num = fields.Char('工單編號')
    work_order_type = fields.Char('工單類型', required=True)
    work_order_description = fields.Text('工單描述', required=True)
    standard_job_id = fields.Many2one('maintenance_plan.standard.job', string='標準工作', required=True)
    equipment_id = fields.Many2one('maintenance_plan.equipment', string='設備', required=True)
    equipment_num = fields.Char('設備編號', compute='_com_equipment', store=True)
    equipment_serial_number = fields.Char('設備序列號')  # 因設備序列號會變，故在此記錄生成工單時的瞬時設備序列號
    equipment_type_id = fields.Char(string='設備類別', compute='_com_equipment')
    medol = fields.Char(string='設備型號', compute='_com_equipment')
    description = fields.Char(string='設備描述', compute='_com_equipment')
    plan_start_time = fields.Date('建議時間(開始)', required=True)
    plan_end_time = fields.Date('建議時間(結束)', required=True)
    display_plan_time = fields.Char('建議時間', compute='_com_plan_time', store=True)
    action_time = fields.Date('計劃執行時間')
    display_action_time = fields.Char('計劃執行時間', compute='_com_action_time', store=True)
    action_dep_id = fields.Many2one('user.department', string='執行班組')
    actual_start_time = fields.Datetime('實際開始時間')
    actual_end_time = fields.Datetime('實際結束時間')
    status = fields.Selection(STATUS, string='狀態')
    is_overdue = fields.Selection([('yes', '是'), ('no', '否')], string='是否逾期', default='no')
    executor_id = fields.Many2one('res.users', string='執行人')  # 執行人一旦開始填表，則不可更改，執行人只能在執行班組中
    # 審批關聯
    order_approval_ids = fields.One2many('maintenance_plan.order.approval', 'work_order_id', string='審批')
    approver_status = fields.Selection(APPROVER_STATUS, string='審批狀態', compute='_com_approval', store=True)
    submit_user_id = fields.Many2one('res.users', string='提交人', compute='_com_approval', store=True)
    approver_user_id = fields.Many2one('res.users', string='審批人', compute='_com_approval', store=True)
    submit_date = fields.Datetime('提交時間')
    last_submit_date = fields.Datetime('最後提交時間', compute='_com_approval', store=True)
    last_approver_date = fields.Datetime('最後審批時間', compute='_com_approval', store=True)
    order_form_ids = fields.One2many('maintenance_plan.order.form', 'order_id', string='工單內審批表單',
                                     default=_default_order_forms)
    approval_type = fields.Char('審批類型', default='Maintenance Reference')

    @api.model
    def create(self, vals):
        # 給超過當前時間仍然未完成的工單標記逾期
        now_day = dt.datetime.now() + relativedelta(hours=8)
        if (dt.datetime.strptime(vals['plan_end_time'].replace('/', '-'), '%Y-%m-%d') - now_day < dt.timedelta(0) and
                vals.get('status', None) != 'closed'):
            vals['is_overdue'] = 'yes'
        serial_number = self.env['maintenance_plan.equipment'].browse(vals['equipment_id']).serial_number
        vals['equipment_serial_number'] = serial_number
        return super().create(vals)

    @api.one
    @api.depends('order_approval_ids')
    def _com_approval(self):
        if len(self.order_approval_ids) != 0:
            # 最後提交審批的記錄
            last_submit_approver = self.order_approval_ids.filtered(lambda r: r.to_status == 'pending_approval')[-1]
            approver_approver_ids = self.order_approval_ids.filtered(lambda r: r.old_status == 'pending_approval')
            # 最後審批的記錄，可能為空記錄
            last_approver_approver = approver_approver_ids[-1] if len(approver_approver_ids) > 0 else None
            self.approver_status = last_approver_approver.to_status if last_approver_approver is not None else None
            self.submit_user_id = last_submit_approver.execute_user_id
            self.approver_user_id = last_approver_approver.approver_user_id if last_approver_approver is not None else None
            self.last_submit_date = last_submit_approver.create_date
            self.last_approver_date = last_approver_approver.create_date if last_approver_approver is not None else None

    @api.one
    @api.depends('equipment_id')
    def _com_equipment(self):
        if len(self.equipment_id) != 0:
            self.equipment_num = self.equipment_id.num
            self.equipment_type_id = self.equipment_id.equipment_type_id.name
            self.medol = self.equipment_id.equipment_model.equipment_model
            self.description = self.equipment_id.description

    @api.one
    @api.depends('plan_start_time', 'plan_end_time')
    def _com_plan_time(self):
        if self.plan_start_time is not False and self.plan_end_time is not False:
            self.display_plan_time = '{}至{}'.format(
                self.plan_start_time.replace('-', '/'),
                self.plan_end_time.replace('-', '/')
            )

    @api.one
    @api.depends('action_time')
    def _com_action_time(self):
        if self.action_time is not False:
            self.display_action_time = self.action_time.replace('-', '/')

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
    def get_equipment_and_type_info(self, id):
        record = self.browse(id)
        equipment = record.equipment_id
        equipment_type_name = equipment.equipment_type_id.name
        equipment_description = equipment.description
        equipment_type_description = equipment.equipment_type_id.description
        standard_job = record.standard_job_id.name
        return {'equipment_type_name': equipment_type_name, 'equipment_description': equipment_description,
                'equipment_type_description': equipment_type_description, 'standard_job': standard_job}

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

    def cron_order_check_overdue(self):
        '''
        定时检查工單逾期
        :return:
        '''
        now_day = dt.datetime.strftime(dt.datetime.now() + relativedelta(hours=8), '%Y-%m-%d')
        # 給超過當前時間仍然未完成的工單標記逾期
        self.search([('is_overdue', '!=', 'yes'), ('plan_end_time', '<', now_day), ('status', '=', 'closed')]) \
            .write({'is_overdue': 'yes'})
