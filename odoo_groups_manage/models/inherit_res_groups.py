# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models, fields, api


class PositionSettings(models.Model):
    _inherit = 'res.groups'
    _description = '职位设置'
    _parent_store = True  # set to True to compute MPTT (parent_left, parent_right)
    parent_id = fields.Many2one('res.groups', ondelete='cascade')
    child_ids = fields.One2many('res.groups', 'parent_id')
    parent_left = fields.Integer(index=True)
    parent_right = fields.Integer(index=True)
    sequence = fields.Integer(index=True, default=0)

    @staticmethod
    def get_config_info():
        '''
        该函数返回一个dict, 共有4个key,
        key: module_name 当前项目的module名，一般是__manifest__.py中的name对应的值，category_id_list会在此module下搜索相应的id
        key: category_id_list 需要展示group的对应的category的id的列表，这个id不包含自定义的组category的id
        key: custom_group_id 自定义的组category的id
        :return:
        '''
        return {
            'module_name': 'odoo_groups_manage', 'category_id_list': [],
            'custom_group_id': 'odoo_groups_manage_category_custom_groups'}

    def recursion_tree_data(self, cats):
        '''
        递归添加group树
        :param cats: 根节点的list
        :return:
        '''
        for cat in cats:
            if len(cat['child_ids']) == 0:
                cat['children'] = []
            else:
                cat['children'] = self.search_read([
                    ('id', 'in', cat['child_ids'])], fields=['name', 'child_ids', 'parent_left', 'parent_right'],
                    order='sequence')
                self.recursion_tree_data(cat['children'])
        return

    @api.model
    def get_group_data(self, group_id):
        '''
        获取group树和template模板
        :param group_id: 当前group的id，如果是新建，则此值为None
        :return:
        '''
        config_dict = self.get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()
        # 获取父节点
        # 组装子节点
        category_record_ids = [self.env.ref('{}.{}'.format(config_dict['module_name'], i)).id
                               for i in config_dict['category_id_list']]
        cats = self.search_read([('category_id', 'in', category_record_ids), ('parent_id', '=', None)], fields=[
            'name', 'parent_id', 'child_ids', 'parent_left', 'parent_right', 'category_id'], order='sequence')
        self.recursion_tree_data(cats)
        # 获取已选择节点
        checked_groups_ids = self.browse(group_id).implied_ids.filtered(lambda x: len(x.child_ids) == 0).ids
        template = self.env['vue_template_manager.template_manage'].get_template_content(
            'odoo_groups_manage', 'group_config')
        rst = dict(cats=cats, template=template, checked_groups_ids=checked_groups_ids)
        return rst

    @api.model
    def add_or_write_custom_group(self, open_type, group_id, group_name, implied_ids):
        '''
        添加或更改依赖组
        :param open_type: 'add' or 'update'
        :param group_id: 当前组id
        :param group_name: 当前组name
        :param implied_ids: 选中的group_id
        :return:
        '''
        config_dict = self.get_config_info()
        category_id = self.env.ref('{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id']))
        category_id.ensure_one()
        if open_type == 'add':
            self.create({'name': group_name, 'category_id': category_id.id, 'implied_ids': [(6, 0, implied_ids)]})
        elif open_type == 'update':
            self.browse(group_id).write({'implied_ids': [(6, 0, implied_ids)]})

    @api.model
    def del_group_users(self, group_id, del_groups_ids, del_users_ids):
        '''
        sql语句删除相应的user与group关系
        :param group_id: 当前所在自定义组的id
        :param del_groups_ids: 需要踢出人员的继承组的id列表
        :param del_users_ids: 需要踢出的人员id列表
        :return:
        '''
        # 检查踢出的人员是否在其他组内
        config_dict = self.get_config_info()
        groups = self.env['res.groups'].search(
            [('id', '!=', group_id),
             ('category_id', '=', self.env.ref(
                 '{}.{}'.format(config_dict['module_name'], config_dict['custom_group_id'])).id)])
        del_group_user_map = defaultdict(list)
        for item in del_groups_ids:
            del_group_user_map[item] = del_users_ids
        for group in groups:
            cur_group_users = group.users.ids  # 当前分组的用户
            deal_cur_groups_ids = list(set(group.implied_ids.ids).intersection(
                set(del_groups_ids)))  # 当前分组需处理的子分组
            for del_group_id in deal_cur_groups_ids:
                del_group_user_map[del_group_id] = list(
                    set(del_group_user_map[del_group_id]).difference(set(cur_group_users)))
        # 创建sql语句
        sql = '''DELETE FROM res_groups_users_rel WHERE'''
        num = 0
        for gid in del_group_user_map:
            if len(del_group_user_map[gid]) > 1:
                join_word = '''''' if num == 0 else ''' or'''
                sql = sql + join_word + ''' (gid = {} AND uid IN {})'''.format(gid, str(tuple(del_group_user_map[gid])))
                num += 1
            elif len(del_group_user_map[gid]) == 1:
                join_word = '''''' if num == 0 else ''' or'''
                sql = sql + join_word + ''' (gid = {} AND uid = {})'''.format(gid, del_group_user_map[gid][0])
                num += 1
        if num > 0:
            self._cr.execute(sql)
        return

    @api.multi
    def write(self, vals):
        '''
        重写write，避免子组变化时，对应子组的人员的人员还具体原子组权限
        '''
        if 'users' in vals and vals['users'][0][0] == 6:
            # 如果不是添加组内人员的情况, 即为删除组内人员
            if not set(self.users.ids).issubset(vals['users'][0][2]):
                del_users_ids = list(
                    set(self.users.ids).difference(set(vals['users'][0][2])))
                self.del_group_users(self.id, self.implied_ids.ids, del_users_ids)
        if 'implied_ids' in vals and vals['implied_ids'][0][0] == 6:
            # 如果添加组的情况, 即为继承组, 此时应去继承组内删除所有当前自定义组内人员
            if not set(self.implied_ids.ids).issubset(vals['implied_ids'][0][2]):
                del_groups_ids = list(
                    set(self.implied_ids.ids).difference(set(vals['implied_ids'][0][2])))
                self.del_group_users(self.id, del_groups_ids, self.users.ids)
        return super().write(vals)

    @api.multi
    def unlink(self):
        '''
        当前组的子组中人的删除处理：
        若其他组的子组中包含该子组，且当前组的子组中包含的人被被包含在该子组中，则不能删除，否则，删除
        '''
        del_groups_ids = self.implied_ids.ids  # 需要删除的分组的
        self.del_group_users(self.id, del_groups_ids, self.users.ids)
        return super(models.Model, self).unlink()
