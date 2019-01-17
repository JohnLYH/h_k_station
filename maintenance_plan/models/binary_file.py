# !user/bin/env python3
# -*- coding: utf-8 -*-
# Author: Artorias
from odoo import models, fields


class BinaryFile(models.Model):
    _name = 'maintenance_plan.binary.file'
    _description = '附件'

    file = fields.Binary('文件', attachment=True)
    order_form_approval_id = fields.Many2one('maintenance_plan.order.form.approval', string='表單操作流水')