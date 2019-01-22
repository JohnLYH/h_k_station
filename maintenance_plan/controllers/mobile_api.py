# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
import datetime
import json
import os
import base64
import random
import time

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
    '''
    工單接口
    '''

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
                executor=record.executor_id.name or '', standardJob=record.standard_job_id.name, id=record.id,
                deadline=record.plan_end_time, planedTime=record.display_action_time,
                completionTime=record.actual_start_time, overdue=True if time.strptime(
                    record.actual_end_time, '%Y-%m-%d %H:%M:S') > datetime.datetime.now() else False
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
            equipmentNo=record.equipment_id.num,
            fatherEquipmentNo=record.equipment_id.parent_equipment_num,
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
        # TODO: 待验证
        return to_json({
            'errcode': 0, 'msg': '', 'data': {
                'no': order_record.num, 'equipmentNo': order_record.equipment_num,
                'station': order_record.equipment_id.station,
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
        pageIndex = int(params['pageIndex', 0])
        pageSize = params['pageSize']
        domain = [('status', '=', 'OK')]
        # TODO: 需要验证
        if no != '':
            domain.append(('equipment_name', 'ilike', no))
        tools_records = request.env['maintenance_plan.other_equipment'].search(
            domain, limit=pageSize, offset=pageSize * (pageIndex - 1))
        result = {
            'errcode': 0, 'data': {
                'list': [{
                    'id': tool.id, 'no': tool.equipment_num, 'name': tool.equipment_name,
                    'modle': tool.model, 'expired': False if tool.status == 'OK' else True
                } for tool in tools_records]
            },
            'msg': ''
        }
        return to_json(result)

    @http.route('/mtr/wo/tools/input', type='json', auth='user')
    def tools_input(self, **kwargs):
        pass

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

    @http.route('/mtr/wo/start', type='json', auth='user')
    def auto_star_form(self, **kwargs):
        '''
        開始測試
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(params['id'])
        userid = int(params['userid'])
        # 获取执行班组
        action_dep_id = order_record.action_dep_id
        # 判断这个人是否是这个班组的
        if action_dep_id.search_count([('users', 'in', userid)]) > 0:
            order_record.write({
                'action_dep_id': userid,
                'status': 'executing',
                'actual_start_time': datetime.datetime.now()
            })
            return to_json({'errcode': 0, 'data': '', 'msg': '保存成功'})
        return to_json({'errcode': 1, 'data': '', 'msg': '保存失敗,此組沒有這個人'})

    @http.route('/mtr/wo/test/submit', type='json', auth='user')
    def auto_submit_form(self, **kwargs):
        '''
        對向波口測試提交、簽署
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        submitData = params['submitData']
        # 提交狀態
        submitStatus = params['submitStatus']
        # 下級審批人
        approver = params['approver']
        # 圖片地址
        signature = params['signature']
        # 工單id
        id = params['id']
        # 獲取工單
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
        test_form = order_record.order_form_ids.filtered(lambda f: f.name == '對向波口測試')
        if submitStatus == 'SUBMIT':
            test_form.write({
                'content': submitData,
                'status': submitStatus
            })
            order_record.write({
                'actual_end_time': datetime.datetime.now()
            })
        else:
            test_form.write({
                'status': submitStatus
            })
        # 表單id
        order_form_id = test_form.id
        # 當前操作人
        execute_user_id = request.uid
        if submitStatus == 'SUBMIT':
            old_status = 'WRITE'
        else:
            # 找到之前的最後條記錄
            order_form_approval = request.env['maintenance_plan.order.form.approval'].search([
                ('next_execute_user_id', '=', execute_user_id), ('order_form_id', '=', order_form_id)], limit=1)
            old_status = order_form_approval.to_status if order_form_approval else 'WRITE'
        to_status = submitStatus
        request.env['maintenance_plan.order.form.approval'].create({
            'order_form_id': order_form_id,
            'execute_user_id': execute_user_id,
            'next_execute_user_id': approver,
            'old_status': old_status,
            'to_status': to_status,
            'signature': signature,
            'approval_time': datetime.datetime.now()
        })
        # TODO: 判断是否要修改工单状态到审批
        return to_json({'errcode': 0, 'data': '', 'msg': '提交成功'})

    @http.route('/mtr/wo/test/reject', type='json', auth='user')
    def auto_reject_form(self, **kwargs):
        '''
        對向波口測試拒絕
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        # 工單id
        id = params['id']
        # 拒绝原因
        reason = params['reason']
        # 拒絕的狀態
        rejectStatus = params['rejectStatus']
        # 签名
        signature = params['signature']
        # 當前操作人
        execute_user_id = request.uid
        # 獲取工單
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
        # 修改状态为前一步
        test_form = order_record.order_form_ids.filtered(lambda f: f.name == '對向波口測試')
        test_form.write({
            'status': rejectStatus
        })
        # 表單id
        order_form_id = test_form.id
        # 找到之前的最後條記錄
        order_form_approval = request.env['maintenance_plan.order.form.approval'].search([
            ('next_execute_user_id', '=', execute_user_id), ('order_form_id', '=', order_form_id)], limit=1)
        old_status = order_form_approval.to_status if order_form_approval else 'SUBMIT'
        next_execute_user_id = order_form_approval.execute_user_id.id
        request.env['maintenance_plan.order.form.approval'].create({
            'order_form_id': order_form_id,
            'execute_user_id': execute_user_id,
            'next_execute_user_id': next_execute_user_id,
            'old_status': old_status,
            'to_status': rejectStatus,
            'signature': signature,
        })
        return to_json({'errcode': 0, 'data': '', 'msg': '拒絕成功'})

    @http.route('/mtr/wo/equipment/exchange', type='json', auth='user')
    def auto_exchange_form(self, **kwargs):
        '''
        設備更換
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        # 工單id
        id = params['id']
        # 更換原因
        reason = params['reason']
        # 新設備序列號
        serialNo = params['serialNo']
        # 签名
        signature = params['signature']
        # 當前操作人
        execute_user_id = request.uid
        # 獲取工單
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
        # 獲取設備編號
        equipment_id = order_record.equipment_id
        if not equipment_id:
            return to_json({'errcode': 1, 'data': '', 'msg': '找不到該設備'})
        # 原有設備的設備序列號
        old_serialNo = equipment_id.serial_number
        equipment = equipment_id.description
        station = equipment_id.station
        equipmentNo = equipment_id.num
        # 找到序列號的id
        serial_number_id = request.env['maintenance_plan.equipment.serial_number'].search([('num', '=', serialNo)])
        if not serial_number_id:
            return to_json({'errcode': 1, 'data': '', 'msg': '未找到該序列號'})
        serial_number_id = serial_number_id.id
        # 找到舊設備序列號id
        old_serial_number_id = request.env['maintenance_plan.equipment.serial_number'].search(
            [('num', '=', old_serialNo)])
        if not old_serial_number_id:
            return to_json({'errcode': 1, 'data': '', 'msg': '未找到舊序列號'})
        old_serial_number_id = old_serial_number_id.id
        # 去找到新設備序列號的原來那台設備并更改設備序列號為過度序列號
        to_old_equipment = request.env['maintenance_plan.equipment'].search([{
            ('serial_number', '=', serialNo), ('num', '=', None)
        }])
        if not to_old_equipment:
            to_old_equipment = request.env['maintenance_plan.equipment'].search([{
                ('serial_number', '=', serialNo)
            }])
            if to_old_equipment:
                return to_json({'errcode': 1, 'data': '', 'msg': '設備序列號已安裝在编号：{}設備編號下，請確認是否輸入正確'.format(
                    to_old_equipment.num)})
            else:
                return to_json({'errcode': 1, 'data': '', 'msg': '未找到該序列號'})
        # 新序列號的拆卸記錄
        request.env['maintenance_plan.migrate.records'].write({
            'info': '從設備No.：{}上拆卸'.format(to_old_equipment.num),
            'equipment_serial_number': serialNo,
            'remark': reason,
            'executor_user_id': execute_user_id,
            'signature': signature
        })
        # 老序列號的拆卸記錄
        request.env['maintenance_plan.migrate.records'].write({
            'info': '從設備No.：{}上拆卸'.format(equipment_id.num),
            'equipment_serial_number': old_serialNo,
            'remark': reason,
            'executor_user_id': execute_user_id,
            'signature': signature
        })
        # 新序列號的安裝記錄
        request.env['maintenance_plan.migrate.records'].write({
            'info': '安裝到設備No.：{}'.format(equipment_id.num),
            'equipment_serial_number': serialNo,
            'remark': reason,
            'executor_user_id': execute_user_id,
            'signature': signature
        })
        # 新序列號的安裝記錄
        request.env['maintenance_plan.migrate.records'].write({
            'info': '安裝到設備No.：{}'.format(to_old_equipment.num),
            'equipment_serial_number': old_serialNo,
            'remark': reason,
            'executor_user_id': execute_user_id,
            'signature': signature
        })
        # 更改序列號
        equipment_id.write({
            'serial_number_id': serial_number_id
        })
        # 丟棄老設備
        to_old_equipment.write({
            'serial_number_id': old_serial_number_id,
            'num': None,
        })
        user = request.env['res.users'].browse(execute_user_id)
        # 操作人的信息
        exchangeUser = {
            'signature': signature,
            'time': datetime.datetime.now(),
            'id': execute_user_id,
            'name': user.name,
            'role': user.role,
        }
        # 新設備
        newEquipment = {
            'serialNo': serialNo,
            'description': equipment_id.description,
            'remarks': reason
        }
        return to_json({'errcode': 0, 'data': {'equipment': equipment, 'equipmentNo': equipmentNo,
                                               'serialNo': old_serialNo, 'station': station,
                                               'newEquipment': newEquipment, 'exchangeUser': exchangeUser},
                        'msg': '拒絕成功'})

    @http.route('/mtr/wo/certificate', type='json', auth='user')
    def auto_certificate_form(self, **kwargs):
        '''
        獲取檢測證書數據
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        if request.httprequest.method == 'GET':
            # 工單id
            id = int(params['id'])
            # 獲取工單
            order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
            # 當前操作人
            execute_user_id = request.uid
            test_form = order_record.order_form_ids.filtered(lambda f: f.name == '對向波口測試')
            if test_form.content:
                # 數據
                content = json.loads(test_form.content)
                # TODO: 查看检测证书里面的数据是不是这样
                no = content['no']
                name = content['name']
                date = content['date']
            else:
                no = '無'
                name = '無'
                date = '無'
            test_form2 = order_record.order_form_ids.filtered(lambda f: f.name == '檢測證書')
            # 找到對應的審批記錄
            order_form_approval = request.env['maintenance_plan.order.form.approval'].search([(
                'order_form_id', '=', test_form2.id)])
            # TODO:檢驗證書多個人都要簽署還是什麼
            if order_form_approval:
                status = 'SIGNATURED'
                execute_user_id = order_form_approval.execute_user_id
                signatureUser = {
                    'id': execute_user_id.id,
                    'role': execute_user_id.role,
                    'time': order_form_approval.approval_time,
                    'signature': order_form_approval.signature
                }
                return to_json({'errcode': 0, 'data': {'no': no, 'date': date, 'name': name, 'status': status,
                                                       'signatureUser': signatureUser}, 'msg': '成功'})
            else:
                status = 'UNSIGNATURE'
                return to_json(
                    {'errcode': 0, 'data': {'no': no, 'date': date, 'name': name, 'status': status}, 'msg': '成功'})
        else:
            # 工單id
            id = int(params['id'])
            # 下級審批人
            approvers = int(params['approvers'])
            signature = params['signature']
            # 獲取工單
            order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
            test_form2 = order_record.order_form_ids.filtered(lambda f: f.name == '檢測證書')
            request.env['maintenance_plan.order.form.approval'].create({
                'order_form_id': test_form2.id,
                'execute_user_id': request.uid,
                'next_execute_user_id': approvers,
                'old_status': 'UNSIGNATURE',
                'to_status': 'SIGNATURED',
                'signature': signature,
                'approval_time': datetime.datetime.now()
            })
            return to_json({"errcode": "0", "msg": "", "data": {}})

    @http.route('/mtr/wo/submit', type='json', auth='user')
    def auto_submit(self, **kwargs):
        '''
        提交工單
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        # 工單id
        id = int(params['id'])
        # 獲取工單
        order_record = request.env['maintenance_plan.maintenance.plan'].browse(id)
        # 開始時間
        begin = params['begin']
        # 結束時間
        end = params['end']
        approver = int(params['approver'])
        request.env['maintenance_plan.order.approval'].create({
            'work_order_id': id,
            'execute_user_id': request.uid,
            'approver_user_id': approver,
            'old_status': None,
            'to_status': 'pending_approval'
        })
        order_record.write({
            'actual_start_time': begin,
            'actual_end_time': end,
            'approver_user_id': approver,
            'status': 'pending_approval'
        })
        return to_json({"errcode": "0", "msg": "", "data": {}})


class Approval(http.Controller):
    """
    審批接口
    """
    @http.route('/mtr/approval/list', type='json', auth='user')
    def approval_list(self, **kwargs):
        """
        审批列表
        :param kwargs:
        :return:
        """
        params = request.jsonrequest
        page = params['pageIndex']
        limit = params['pageSize']
        # 搜索值
        key = params['key']
        # 狀態:PENDING:待审批，PROGRESS:审批中，APPROVED: 已审批
        status = params['status']
        beginDate = params['beginDate']
        endDate = params['endDate']
        # 先去搜索
        domian = []
        if key != '':
            domain.extend([
                '|', '|', '|',
                ('num', 'ilike', search_key),
                ('equipment_num', 'ilike', search_key),
                ('executor_id.name', 'ilike', search_key),
                ('action_dep_id.name', 'ilike', search_key)
            ])

class Center_User(http.Controller):
    """
    個人中心
    """
    @http.route('/mtr/center', type='json', auth='user')
    def center(self, **kwargs):
        '''
        获取个人中心数据
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        # 請求人id
        id = request.uid
        name = request.env.user.name
        department = request.env.user.branch
        position = request.env.user.role
        email = request.env.user.email
        userInfo = {
            'name': name,
            'position': position,
            'department': department,
            'email': email,
        }
        return to_json({'errcode': 0, 'data': {'userInfo': userInfo}, 'msg': ''})

    @http.route('/mtr/password/reset', type='json', auth='user')
    def password_reset(self, **kwargs):
        '''
        修改密码
        :param kwargs:
        :return:
        '''
        params = request.jsonrequest
        # 原始密碼
        original = params['original']
        # 新密碼
        new = params['new']
        try:
            if request.env['res.users'].change_password(original, new):
                return to_json({'errcode': 0, 'data': {}, 'msg': ''})
        except Exception:
            return to_json({'errcode': 1, 'data': {}, 'msg': '原始密碼輸入錯誤'})
        return to_json({'errcode': 1, 'data': {}, 'msg': '更改密碼失敗'})
