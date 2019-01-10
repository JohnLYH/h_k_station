# -*- coding: utf-8 -*-

from odoo import api, models, fields
import smtplib
from email.mime.text import MIMEText
from email.header import Header

class Email_List(models.Model):
    _name = 'user.send_email'
    _description = '接收，發送郵件'

    email_theme = fields.Char(string='郵件主題')
    recipient_person = fields.Char(string='收件人')
    send_time = fields.Datetime(string='發送時間')

    @api.model
    def reset_password(self):
        '''
        重置密碼的時候發送郵件
        '''
        sender = ''  # 发送人的邮箱
        receiver = '' # 接收人的邮箱 是list
        subject = '' #标题
        email_name = '' #邮箱的标题
        smtpserver = '' # 邮箱的server
        username = '' #发送人的邮箱
        password = '' #发送人的授权码,不是密码

        msg = MIMEText('大家关好窗户', 'plain', 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8') #标题
        msg['From'] = '%s<xxxx@163.com>'%email_name
        msg['To'] = "xxxxxx@163.com"
        smtp = smtplib.SMTP()
        smtp.connect(smtpserver,25)
        smtp.login(username, password)
        smtp.sendmail(sender, [receiver], msg.as_string())
        smtp.quit() # 退出

    def email_delete(self):
        self.unlink()

    def email_edit(self):
        pass
