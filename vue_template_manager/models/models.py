# -*- coding: utf-8 -*-
import os
from odoo import models, fields, api, exceptions, tools

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
config = tools.config.options

class template_manage(models.Model):
    _name = 'vue_template_manager.template_manage'

    module_name = fields.Char(string="model名")
    template_name = fields.Char(string="模板名", required=True)
    template_content = fields.Text(string="模板内容", readonly=True)
    remark = fields.Text(string="备注")

    @api.model
    def get_template_content(self, module_name,  template_name):
        def read_template():
            path = BASE_DIR + '/' + module_name + '/static/vue_template/' + template_name + '.html'
            with open(path, 'r', encoding="utf8") as f:
                return f.read()

        # 如果是开发环境，直接读取文件
        if 'development_environment' in tools.config.options:
            return read_template()
        # 如果是生产环境，首先检查数据库是否有值，没有则先保存到数据库
        else:
            record = self.search([('template_name', '=', template_name),
                                  ('module_name', '=', module_name)])
            if len(record) > 0 and record.template_content:
                return record[0].template_content
            else:
                content = read_template()
                self.create({
                    'template_content': content,
                    'module_name': module_name,
                    'template_name': template_name
                })
                return content

