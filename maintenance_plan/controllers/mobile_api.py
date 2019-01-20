# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import json
import os
import base64
from PIL import Image, ImageDraw, ImageFont
import datetime as dt
from dateutil.relativedelta import relativedelta

from odoo import http
from odoo.http import request, Root, session_gc
from addons.web.controllers.main import ensure_db

# 前後端審批狀態映射
STATUS_MAP = {
    'TODO': 'be_executed', 'EDITING': 'executing', 'PENDING': 'pending_approval', 'APPROVALED': 'closed'}

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


def add_text_to_image(image, left_text, center_text, rigth_text):
    '''
    圖片添加水印，思路是連原圖總共分為3層圖片，第二層與原圖尺寸相同，將水印圖片塊粘貼到第二層后，再將第一層、第二層復合為一個新的image
    :param image: Image.open()的文件內容
    :param left_text: 左下文字
    :param center_text: 中下文字
    :param rigth_text: 右下文字
    :return: 帶水印的image
    '''
    white_font = (255, 255, 255, 180)
    black_bg = (0, 0, 0, 30)
    font = ImageFont.truetype(os.path.join(BASE_DIR, 'static/font/STHeiti-Light.ttc'), size=44, index=0)
    # 將原圖轉換為rgba模式
    rgba_image = image.convert('RGBA')
    # 創建水印層
    text_overlay = Image.new('RGBA', (rgba_image.size[0], 50), black_bg)
    # 創建復合背景層
    layer = Image.new('RGBA', rgba_image.size, (255, 255, 255, 0))
    # 水印層添加文字
    image_draw = ImageDraw.Draw(text_overlay)
    # 设置文本文字位置
    text_size_x, text_size_y = image_draw.textsize(rigth_text, font=font)
    text_xy_left = (0, (text_overlay.size[1] - text_size_y) / 2)  # 底部左
    text_xy_center = ((text_overlay.size[0] - text_size_x) / 2, (text_overlay.size[1] - text_size_y) / 2)  # 底部中
    text_xy_right = (text_overlay.size[0] - text_size_x, (text_overlay.size[1] - text_size_y) / 2)  # 底部右
    # 设置文本颜色和透明度
    image_draw.text(text_xy_left, left_text, font=font, fill=white_font)
    image_draw.text(text_xy_center, center_text, font=font, fill=white_font)
    image_draw.text(text_xy_right, rigth_text, font=font, fill=white_font)
    # 粘貼水印層到復合背景層
    layer.paste(text_overlay, (0, layer.size[1] - text_overlay.size[1]))
    # 復合圖片
    image_with_text = Image.alpha_composite(rgba_image, layer)
    return image_with_text


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


def get_last_record(query):
    '''
    獲取最後一條記錄
    :param query:
    :return:
    '''
    if len(query) == 0:
        return query
    else:
        return query[-1]


class Public(http.Controller):
    '''
    公共接口類
    '''

    @http.route('/mtr/login', type='json', auth='none')
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

    @http.route('/mtr/upload/img', type='http', auth='none', csrf=False, cors='*')
    def upload_img(self, **kwargs):
        '''
        圖片上傳
        :param kwargs: file或者base64為key，有file時傳的文件類型，base64時傳的文件的base64數據
        :return:
        '''
        if kwargs.get('file', None) is not None:
            file = kwargs['file']
            filename = file.filename
            now_datetime = dt.datetime.now() + relativedelta(hours=8)
            now_date = dt.datetime.strftime(now_datetime, '%Y-%m-%d')
            now_time = dt.datetime.strftime(now_datetime, '%H:%M:%S')
            name = request.env.user.name or ''
            # 添加水印
            image = add_text_to_image(Image.open(file), now_date, now_time, name)
            file_content = base64.b64encode(image.tobytes())
        else:
            file = json.loads(kwargs['base64'])
            file_content = file['data']
            filename = file['name']
        file_record = request.env['maintenance_plan.binary.file'].sudo().create({
            'file': file_content,
            'filename': filename
        })
        url = '/web/content?model={}&id={}&field={}&filename_field={}'.format(
            'maintenance_plan.binary.file', file_record.id, 'file', 'filename'
        )
        return to_json({'errcode': 0, 'msg': '', 'data': {'url': url}})


class WorkOrder(http.Controller):

    @http.route('/mtr/wo/list', type='json', auth='user')
    def get_work_oder_list(self, **kwargs):
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
        output_status_map = dict([(index, word) for (word, index) in STATUS_MAP.items()])
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
                no=record.num, status=output_status_map[record.status], equipmentNo=record.equipment_num,
                executionTime=record.action_time, group=record.action_dep_id.name,
                executor=record.executor_id.name or '', standardJob=record.standard_job_id.name, id=record.id
            ))
        return to_json({'errcode': 0, 'data': {'list': result}, 'msg': ''})

    @http.route('/mtr/wo/detail', type='json', auth='user')
    def get_work_order_detail(self, **kwargs):
        '''
        工單詳情
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        record = request.env['maintenance_plan.maintenance.plan'].browse(int(params['id']))
        output_status_map = dict([(index, word) for (word, index) in STATUS_MAP.items()])
        result = dict(
            no=record.num, status='' if record.status is False else output_status_map[record.status],
            equipmentNo=record.equipment_id.name, fatherEquipmentNo=record.equipment_id.parent_equipment_num,
            equipmentSerialNo=record.equipment_id.serial_number,
            equipmentLocation=record.equipment_id.detailed_location,
            executionTime=record.action_time, group=record.action_dep_id.name,
            standardJob=record.standard_job_id.name, id=record.id, description=record.equipment_id.description,
            model=record.equipment_id.equipment_model.name, woDescription=record.work_order_description,
            materialList=[{
                'description': inventory_management.inventory_description, 'code': inventory_management.inventory_id,
                'stock': inventory_management.inventory_count
            } for inventory_management in record.standard_job_id.inventory_management_ids]
        )
        return to_json({'errcode': 0, 'data': result, 'msg': ''})

    @http.route('/mtr/wo/test', type='json', auth='user')
    def get_work_order_test_form(self, **kwargs):
        '''
        獲取對象波口測試表單json數據
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(params['id'])
        test_form = order_record.order_form_ids.filtered(lambda f: f.name == '對向波口測試')
        last_submit_approval = get_last_record(
            test_form.approval_ids.filtered(lambda f: f.to_status == 'SUBMIT'))
        last_check_user_approval = get_last_record(
            test_form.approval_ids.filtered(lambda f: f.to_status == 'CHECK')
        )
        last_complete_user_approval = get_last_record(
            test_form.approval_ids.filtered(lambda f: f.to_status == 'CHECK')
        )
        assert len(test_form) in [0, 1]
        return to_json({
            'errcode': 0, 'msg': '', 'data': {
                'no': order_record.num, 'equipmentNo': order_record.equipment_num,
                'station': order_record.equipment_id.equipment_type_id.station_id.name,
                'submitStatus': test_form.status, 'submitData': test_form.content or None,
                'submitUser': {
                    'id': last_submit_approval.execute_user_id.id or None,
                    'name': last_submit_approval.execute_user_id.name or None,
                    'role': last_submit_approval.execute_user_id.role or None,
                    'time': last_submit_approval.create_date,
                    'signature': last_submit_approval.signature_url
                },
                'checkUser': {
                    'id': last_check_user_approval.execute_user_id.id or None,
                    'name': last_check_user_approval.execute_user_id.name or None,
                    'role': last_check_user_approval.execute_user_id.role or None,
                    'time': last_check_user_approval.create_date,
                    'signature': last_check_user_approval.signature_url
                },
                'completeUser': {
                    'id': last_complete_user_approval.execute_user_id.id or None,
                    'name': last_complete_user_approval.execute_user_id.name or None,
                    'role': last_complete_user_approval.execute_user_id.role or None,
                    'time': last_complete_user_approval.create_date,
                    'signature': last_complete_user_approval.signature_url
                }
            }
        })

    @http.route('/mtr/wo/tools/list', type='json', auth='user')
    def get_tools_list(self, **kwargs):
        '''
        獲取工器具列表
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        no = params['key']
        domain = [('status', '=', '正常')]
        if no != '':
            domain.append(('equipment_name', 'ilike', no))
        tools_records = request.env['maintenance_plan.other_equipment'].search(domain)
        result = {
            'errcode': 0, 'data': {
                'list': [{
                    'id': tool.id, 'no': tool.equipment_num, 'name': tool.equipment_name,
                    'modle': tool.model, 'expired': False if tool.status == '正常' else True
                } for tool in tools_records]
            },
            'msg': ''
        }
        return to_json(result)

    @http.route('/mtr/wo/test/save', type='json', auth='user')
    def auto_save_form(self, **kwargs):
        '''
        對向波口測試自動保存
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(params['id'])
        test_form = order_record.order_form_ids.filtered(lambda f: f.name == '對向波口測試')
        test_form.write({
            'content': params['submitDataBODY']
        })
        return to_json({'errcode': 0, 'data': '', 'msg': '保存成功'})
