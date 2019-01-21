# !user/bin/env python3
# -*- coding: utf-8 -*-

from odoo import api, models, fields
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime


class EmployeesGet(models.Model):
    _inherit = 'res.users'

    post = fields.Char(string='崗位')
    role = fields.Char(string='角色')
    state = fields.Selection([('正常', '正常'), ('禁用', '禁用')], default='正常')
    branch = fields.Char(string='員工部門')

    @api.model
    def get_users_info(self, **kw):
        '''
        部门下的人员
        :return:
        '''
        role_ids = self.env['user.department'].search([('id', '=', kw.get('department_id'))])
        count = self.env['res.users'].search_count([('id', 'in', role_ids.users.ids)])
        users = self.env['res.users'].search_read(
            [('id', 'in', role_ids.users.ids)],
            fields=['name', 'login', 'post', 'role', 'state', 'branch', 'email'
                    ], limit=30)
        lis = []  # 用来存放部门
        lis.append(kw.get('department_id'))
        dep_id = self.env['user.department'].search_read([('id', '=', kw.get('department_id'))], ['parent_id'])
        if dep_id:
            if dep_id[0].get('parent_id'):
                lis.append(dep_id[0].get('parent_id')[0])
                two_id = self.env['user.department'].search_read([('id', '=', dep_id[0].get('parent_id')[0])],
                                                                 ['parent_id'])
                if two_id[0].get('parent_id'):
                    lis.append(two_id[0].get('parent_id')[0])
        return {'users': users, 'count': count, 'department': lis[::-1]}


    @api.model
    def page_size(self, **kw):
        users = self.env['res.users'].search_read([])
        return users[:kw['size']]

    @api.model
    def init_record(self, **kw):
        users = self.env['res.users'].search_read([])
        return users[:10]

    @api.model
    def current_change(self, **kw):
        config_dict = self.env['res.groups'].get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()

        users = self.env['res.groups'].search_read([('category_id', '=', category_id.id)],
                                                   limit=kw.get('record') * 30)[-30:]
        page_count = kw.get('message') // 30
        remainder = kw.get('message') % 30  # 余数来判断最后一页的数据
        if kw.get('record') == page_count + 1:
            users = self.env['res.groups'].search_read([('category_id', '=', category_id.id)],
                                                       limit=kw.get('record') * 30)[-remainder:]
        return users

    @api.model
    def get_department_users(self,id=False):
        '''
        获取部门信息
        :return:
         '''
        rst = []
        class_a = self.env['user.department'].search_read([('parent_id', '=', id)],
                                                          fields=['child_ids', 'name'])
        for record in class_a:
            vals = {
                'value': record['id'],
                'label': record['name'],
            }
            children = self.get_department_edit(record['id'])
            if children:
                vals['children'] = children
            rst.append(vals)
        act_id = self.env.ref('user.create_new_ifo').id
        return {'department_tree': rst, 'act_id': act_id}

    @api.model
    def get_department_edit(self, id=False):
        '''
        获取分组
        :return:
        '''
        rst = []
        class_a = self.env['user.department'].search_read([('parent_id', '=', id)],
                                                          fields=['child_ids', 'name'])
        for record in class_a:
            vals = {
                'value': record['id'],
                'label': record['name'],
            }
            children = self.get_department_edit(record['id'])
            if children:
                vals['children'] = children
            rst.append(vals)
        return rst

    @api.model
    def get_chose_user_info(self, name, chose):
        if chose == 'all':
            record = self.search_read([('name', '=', name)])
        else:
            record = self.search_read([('name', '=', name), ('state', '=', chose)])

        return record

    @api.model
    def disable_info(self, **kw):
        record = self.search([('login', '=', kw.get('disable_id'))])
        record.write({'state': '禁用'})

    # 编辑人员信息
    @api.model
    def edit_per_information(self, **kw):
        record = self.search([('id', '=', kw.get('self_id'))])

        record = self.env['user.department'].search_read([('id', '=', kw.get('deparment')[-1])], ['name'])
        dic = {
            'name': kw.get('name'),
            'branch': record[0].get('name'),
            'post': kw.get('post'),
            'role': kw.get('role'),
            'email': kw.get('role_email')
        }
        record.write(dic)

    # 獲取所有的部門 崗位 和員工角色
    @api.model
    def gt_all_department(self):
        lis = []
        post_lis = []  # 用來存放崗位
        dep_lis = []  # 用來存放部門
        role_lis = []  # 用來存放角色組
        record = self.search_read([], ['post', 'branch', 'role'])
        for post in record:
            dic = {}
            if post.get('post'):
                dic['value'] = post.get('post')
                dic['label'] = post.get('post')
                post_lis.append(dic)
        for dep in record:
            dep_dic = {}
            if dep.get('branch'):
                dep_dic['value'] = dep.get('branch')
                dep_dic['label'] = dep.get('branch')
                dep_lis.append(dep_dic)
        for role in record:
            role_dic = {}
            if role.get('role'):
                role_dic['value'] = role.get('role')
                role_dic['label'] = role.get('role')
                role_lis.append(role_dic)
        lis.append(post_lis)
        lis.append(dep_lis)
        lis.append(role_lis)
        return lis

    # 修改密码
    @api.model
    def change_password_usr(self, **kw):
        usr_record = self.search([('login', '=', kw.get('login'))])
        record = self.search([('id', '=', kw.get('user_id'))])
        record.write({'password': 123456})

        # TODO: 密碼重置發送郵件
        # 重置密碼的時候發送郵件
        receive_name = ''  # 收件人的人名
        sender = 'businessempire@163.com'  # 发送人的邮箱
        receiver = 'merchantfield@163.com'  # 接收人的邮箱 是list
        subject = '密碼重置'  # 标题
        email_name = '密碼重置'  # 邮箱的标题
        smtpserver = 'smtp.163.com'  # 邮箱的server
        username = 'businessempire@163.com'  # 发送人的邮箱
        password = '57624530asd'  # 发送人的授权码,不是密码
        info = '''
                        內容：管理員已將您MTR移動管理應用密碼重置為初始密碼。
                
                APP下載地址：https://pro.modao.cc/app/wtl9bDa7gySi56dReeSDeH9IhnXSHko，
                
                管理後台地址：https://pro.modao.cc/app/XsU5ZiLTlpyAoAV59PHOPQpC1QdVKo6，
                
                請盡快登錄修改密碼。
                '''
        msg = MIMEText(info, 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')  # 标题
        msg['From'] = '%s<merchantfield@163.com>' % email_name
        msg['To'] = 'merchantfield@163.com'
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver, 25)
        smtp.login(username, password)
        smtp.sendmail(sender, [receiver], msg.as_string())
        smtp.quit()  # 退出

        self.env['user.send_email'].create(
            {'email_theme': subject, 'recipient_person': receive_name,
             'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    @api.model
    def enable_button_act(self, **kwargs):
        self.browse(kwargs.get('self_id')).write({'state': '正常'})

    # 人员列表
    @api.model
    def per_current_change(self, **kw):
        users = self.env['res.groups'].search_read([],
                                                   limit=kw.get('record') * 30)[-30:]
        page_count = kw.get('message') // 30
        remainder = kw.get('message') % 30  # 余数来判断最后一页的数据
        if kw.get('record') == page_count + 1:
            users = self.env['res.groups'].search_read([],
                                                       limit=kw.get('record') * 30)[-remainder:]
        return users

    def create_new_send_email(self):
        # TODO: 新建賬號發送郵件
        # 重置密碼的時候發送郵件
        receive_name = ''  # 收件人的人名
        sender = 'businessempire@163.com'  # 发送人的邮箱
        receiver = 'merchantfield@163.com'  # 接收人的邮箱 是list
        subject = '賬號信息詳情'  # 标题
        email_name = '賬號信息詳情'  # 邮箱的标题
        smtpserver = 'smtp.163.com'  # 邮箱的server
        username = 'businessempire@163.com'  # 发送人的邮箱
        password = '57624530asd'  # 发送人的授权码,不是密码
        info = '''
                        管理員已為您開通MTR移動管理應用，賬號：%s，初始密碼：123456，APP下載地址：https://pro.modao.cc/app/wtl9bDa7gySi56dReeSDeH9IhnXSHko，
                        
                        管理後台地址：https://pro.modao.cc/app/XsU5ZiLTlpyAoAV59PHOPQpC1QdVKo6，
                        
                        請盡快登錄修改密碼。
                        ''' % self.login
        msg = MIMEText(info, 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')  # 标题
        msg['From'] = '%s<merchantfield@163.com>' % email_name
        msg['To'] = 'merchantfield@163.com'
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver, 25)
        smtp.login(username, password)
        smtp.sendmail(sender, [receiver], msg.as_string())
        smtp.quit()  # 退出
        self.write({'password': 123456})
        self.env['user.send_email'].create(
            {'email_theme': subject, 'recipient_person': self.name,
             'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    # 添加tree数据
    @api.model
    def add_tree_button(self, **kwargs):
        date_int = max(self.env['user.department'].search([]).ids)
        self.env['user.department'].create({'name':kwargs.get('value'),'parent_id':kwargs.get('parent_id')})
        return date_int + 1

    # 删除tree数据
    @api.model
    def delete_tree_button(self, **kwargs):
        self.env['user.department'].search([('id', '=', kwargs.get('value'))]).unlink()
