# -*- coding: utf-8 -*-

from odoo import api, models, fields
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import datetime

class Email_List(models.Model):
    _name = 'user.send_email'
    _description = '接收，發送郵件'

    send_person = fields.Char(string='發件人')
    email_theme = fields.Char(string='郵件主題')
    recipient_person = fields.Char(string='收件人')
    send_time = fields.Datetime(string='發送時間')
    send_content = fields.Text(string='發送內容')

    @api.model
    def reset_password(self, **kwargs):
        '''
        重置密碼的時候發送郵件
        '''
        receive_name = ''  # 收件人的人名
        sender = ''  # 发送人的邮箱
        receiver = kwargs.get('email')  # 接收人的邮箱 是list
        subject = kwargs.get('title')  # 标题
        email_name = kwargs.get('title')  # 邮箱的标题
        smtpserver = ''  # 邮箱的server
        username = ''  # 发送人的邮箱
        password = ''  # 发送人的授权码,不是密码
        content = kwargs.get('content') #邮件的内容

        msg = MIMEText(content, 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')  # 标题
        msg['From'] = '%s<xxxx@163.com>' % email_name
        msg['To'] = "xxxxxx@163.com"
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver, 25)
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        smtp.quit()  # 退出
        self.env['user.send_email'].create({
                    'send_person':'admin'+'<'+sender+'>',
                    'email_theme': subject,
                    'recipient_person': receive_name,
                    'send_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'send_content':kwargs.get('content')
                    })
    def email_delete(self):
        self.unlink()

    def email_edit(self):
        return {
            'name': '邮件详情',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'user.send_email',
            'context': {'edit': False},
            'res_id': self.id,
            'flags': {'initial_mode': 'readonly'},
            'target': 'new',
        }
