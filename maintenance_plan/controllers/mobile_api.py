# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import json

from odoo import http
from odoo.http import request, Root, session_gc
from addons.web.controllers.main import ensure_db

STATUS_MAP = {
    'TODO': 'be_executed', 'EDITING': 'executing', 'PENDING': 'pending_approval', 'APPROVALED': 'closed'}


def e_login_setup_session(self, httprequest):
    '''
    變更登錄讀取session_id的驗證函數
    :param self:
    :param httprequest:
    :return:
    '''
    # recover or create session
    session_gc(self.session_store)

    sid = httprequest.args.get('session_id')
    explicit_session = True
    if not sid:
        sid = httprequest.headers.get("X-Openerp-Session-Id") or \
              httprequest.headers.environ.get('HTTP_X_OPENERP_SESSION_ID')
    if not sid:
        sid = httprequest.cookies.get('session_id')
        explicit_session = False
    if sid is None:
        httprequest.session = self.session_store.new()
    else:
        httprequest.session = self.session_store.get(sid)
    return explicit_session


Root.setup_session = e_login_setup_session


def to_json(json_dict):
    '''
    內容轉換為json格式
    :param json_dict:
    :return:
    '''
    return json.dumps(json_dict)


class Login(http.Controller):

    @http.route('/mtr/login', type='json', auth="none")
    def login(self, **kwargs):
        '''
        登錄接口
        :param kwargs:
        :return:
        '''
        ensure_db()
        params = request.jsonrequest
        account = params.get('account', None)
        password = params.get('password', None)
        user = request.session.authenticate(request.session.db, account, password)
        if user is False:
            return to_json({'errcode': 0, 'msg': '登錄失敗, 用戶名/密碼有誤'})
        else:
            session_info = http.request.env['ir.http'].session_info()
            return to_json({'errcode': 1, 'data': {'token': session_info}, 'msg': '登錄成功'})


class WorkOrder(http.Controller):

    @http.route('/mtr/wo/list', type='json', auth='user')
    def work_oder_list(self, **kwargs):
        '''
        工單列表
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        search_key = params['key']
        status = params['state']
        begin_date = params['beginDate']
        end_date = params['endDate']
        page = params['pageIndex']
        limit = params['pageSize']
        auto_status_map = dict([(index, word) for (word, index) in STATUS_MAP.items()])
        domain = []
        result = []
        if search_key != '':
            domain.extend([
                '|', '|', '|',
                ('num', 'ilike', search_key),
                ('equipment_num', 'ilike', search_key),
                ('executor_id.name', 'ilike', search_key),
                ('action_dep_id.name', 'ilike', search_key)
            ])
        if status != '':
            # todo狀態下搜索計劃執行時間
            if status == 'TODO':
                domain.extend([
                    ('status', '=', STATUS_MAP[status]),
                    ('action_time', '>=', begin_date),
                    ('action_time', '<=', end_date),
                ])
            # 其他狀態下搜索實際執行時間
            else:
                domain.extend([
                    ('status', '=', STATUS_MAP[status]),
                    ('actual_start_time', '>=', begin_date),
                    ('actual_end_time', '<=', end_date),
                ])
        # 所有狀態搜索時，搜索計劃執行時間或實際執行時間滿足date範圍
        else:
            domain.extend([
                ('status', '!=', None),
                '|',
                ('plan_start_time', '>=', begin_date),
                ('plan_end_time', '<=', end_date),
                '|',
                ('action_time', '>=', begin_date),
                ('action_time', '<=', end_date)
            ])
        records = request.env['maintenance_plan.maintenance.plan'].search(
            domain, limit=limit, offset=(page - 1) * limit)
        for record in records:
            result.append(dict(
                no=record.num, status=auto_status_map[record.status], equipmentNo=record.equipment_num,
                executionTime=record.action_time, group=record.action_dep_id.name,
                executor=record.executor_id.name or '', standardJob=record.standard_job_id.name, id=record.id
            ))
        return to_json({'errcode': 0, 'data': {'list': result}, 'msg': ''})

    @http.route('/mtr/wo/detail', type='json', auth='user')
    def get_work_order_detail(self, **kwargs):
        params = request.jsonrequest
        record = request.env['maintenance_plan.maintenance.plan'].browse(int(params['id']))
        auto_status_map = dict([(index, word) for (word, index) in STATUS_MAP.items()])
        result = dict(
            no=record.num, status='' if record.status is False else auto_status_map[record.status],
            equipmentNo=record.equipment_id.name, fatherEquipmentNo=record.equipment_id.parent_equipment_num,
            equipmentSerialNo=record.equipment_id.serial_number,
            equipmentLocation=record.equipment_id.detailed_location,
            executionTime=record.action_time, group=record.action_dep_id.name,
            standardJob=record.standard_job_id.name, id=record.id, description=record.equipment_id.description,
            model=record.equipment_id.equipment_model.name, woDescription=record.work_order_description
        )

