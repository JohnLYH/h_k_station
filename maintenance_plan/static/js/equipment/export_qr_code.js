odoo.define('export_qr_code', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');

    var export_qr_code = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.records_list = record.params.records_list;
            console.log(this.records_list)
            this.vue_data = {
                props: {
                    label: 'name',
                    children: 'children'
                },
                checked_equipment_type_tree_data: [],
                equipment_type_tree_data: [],
                count: 0
            }
        },
        willStart: function () {
            var self = this;
            var get_equipment_type_tree_data = self._rpc({
                model: 'maintenance_plan.equipment.type',
                method: 'get_equipment_type_tree_data'
            })

            return $.when(get_equipment_type_tree_data).then(function (data) {
                self.vue_data.equipment_type_tree_data = data.records;
                self.vue_data.count = data.records_count
            })
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'export_qr_code'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#export_qr_code_div',
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        cancel: function () {
                            self.do_action(false)
                        },

                        /**
                         * 選擇節點時子節點也一起變更選擇狀態
                         * @param {*} node 
                         * @param {*} checked 
                         */
                        change_children(node, checked) {
                            var this_vue = this;
                            if (node.child_ids.length > 0) {
                                for (var children_node in node.children) {
                                    this_vue.$refs.equipment_type_tree.setChecked(node.children[children_node].id, checked);
                                }
                            }
                        },
                        /**
                         * 選擇節點時觸發函數
                         * @param {*} node 
                         * @param {*} checked 
                         */
                        check_change: function (node, checked) {
                            var this_vue = this;
                            if (checked === true) {
                                this_vue.checked_equipment_type_tree_data.push(node.name);
                                this_vue.change_children(node, checked)
                            } else {
                                this_vue.checked_equipment_type_tree_data.splice(this_vue.checked_equipment_type_tree_data.indexOf(node.name), 1)
                                this_vue.change_children(node, checked)
                            }
                        },
                        enter: function () {
                            var this_vue = this;
                            console.log(this_vue.$refs.equipment_type_tree.getCheckedKeys())
                        }
                    },
                })
            })
        }
    });
    core.action_registry.add('export_qr_code', export_qr_code);
    return {
        export_qr_code: export_qr_code
    }
});