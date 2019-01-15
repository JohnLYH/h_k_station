/**
 * Created by artorias on 2018/10/19.
 */
odoo.define('odoo_groups_manage_group_config_client', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');

    var odoo_groups_manage_group_config_client = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.group_id = record.params.type === 'add' ? null : record.context.active_id;
            this.vue_data = {
                open_type: record.params.type,
                normalCats: [],
                group_name: '',
                group_tree_data: [],
                checked_groups_ids: [],
                defaultProps: {
                    children: 'children',
                    label: 'name'
                }
            }
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'res.groups',
                method: 'get_group_data',
                kwargs: {group_id: self.group_id}
            }).then(function (rst) {
                self.replaceElement($(rst.template));
                self.vue_data.normalCats = rst.cats;
                self.vue_data.group_tree_data = rst.cats;
                self.vue_data.checked_groups_ids = rst.checked_groups_ids;
                new Vue({
                    el: '#app',
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        save_group: function () {
                            if (this.open_type === 'add' && this.group_name === '') {
                                this.$notify({
                                    title: '警告',
                                    message: '名称不能为空',
                                    type: 'warning'
                                });
                                return
                            }
                            var implied_ids = [];
                            this.$refs.group_tree.getCheckedNodes(false, true).map(function (node) {
                                implied_ids.push(node.id)
                            });
                            self._rpc({
                                model: 'res.groups',
                                method: 'add_or_write_custom_group',
                                args: [this.open_type, self.group_id, this.group_name, implied_ids],
                            }).then(function () {
                                self.do_action({
                                    type: 'ir.actions.act_window_close'
                                })
                            })
                        }
                    }
                })
            })
        }
    });
    core.action_registry.add('odoo_groups_manage_group_config_client', odoo_groups_manage_group_config_client);
    return {odoo_groups_manage_group_config_client: odoo_groups_manage_group_config_client}
});