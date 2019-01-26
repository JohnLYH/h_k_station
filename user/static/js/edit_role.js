odoo.define('edit_role', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var edit_role = Widget.extend({
        app: undefined,
        group_id: 0,
        is_update: false,
        dom_id: 'edit_role' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {
                input: action.context.role_name,
                textarea: action.context.per,
                user_name: '',
                departmentList: [],
                default_checked_keys: [],
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                role: action.context.role_name,
                per: action.context.per,
                group_id: action.context.groups_id,
                tree_input: false,
                tree_date: '',
                options_per: '',
                ruleForm: {input: action.context.role_name},
                rules: {input: [{required: true, message: '請輸入角色名', trigger: 'blur'}]},


            };
        },
        willStart: function () {
            var self = this;

            var data_defau = self._rpc({
                model: 'res.groups',
                method: 'get_group_data',
                kwargs: {group_id: self.vue_data.group_id},
            }).then(function (data) {
                self.vue_data.departmentList = data.cats
                self.vue_data.default_checked_keys = data.checked_groups_ids
            });
            var name_data = self._rpc({
                model: 'res.groups',
                method: 'get_user_name_data',
                kwargs: {group_id: self.vue_data.group_id},
            }).then(function (data) {
                self.vue_data.user_name = data
            })

            var per_data = self._rpc({
                model: 'res.users',
                method: 'get_per_data',
            }).then(function (data) {
                self.vue_data.options_per = data
            })

            return $.when(data_defau, name_data, per_data)
        },

        start: function () {
            var self = this;

            $.when(
                this._rpc({
                    model: 'html_model.template_manage',
                    method: 'get_template_content',
                    kwargs: {module_name: 'user', template_name: 'edit_role'}
                })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#edit_role',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                        click_node: function (data) {
                        },

                        onSubmit: function (formName) {
                            this.$refs[formName].validate((valid) => {
                                if (valid) {
                                var implied_ids = [];
                                this.$refs.tree.getCheckedNodes(false, true).map(function (node) {
                                    implied_ids.push(node.id)
                                });
                                self._rpc({
                                    model: 'res.groups',
                                    method: 'edit_save',
                                    kwargs: {
                                        role_name: self.vue_data.role,
                                        permission_illust: self.vue_data.per,
                                        modify_name: self.vue_data.ruleForm.input,
                                        modify_per: self.vue_data.textarea,
                                        per_id: implied_ids,
                                        self_id: self.vue_data.group_id
                                    }
                                }).then(function () {
                                    self.do_action({"type": "ir.actions.act_window_close"})
                                })
                            }else {

                                }
                        })
                        },
                        cancel: function () {
                            self.do_action({"type": "ir.actions.act_window_close"})
                        },
                        button_act: function (date) {
                            self.vue_data.tree_input = true
                        },

                        cancel_tree: function () {
                            self.vue_data.tree_input = false
                        },

                        per_data_return: function () {
                            self._rpc({
                                model: 'res.groups',
                                method: 'get_user_name_data',
                                kwargs: {group_id: self.vue_data.group_id},
                            }).then(function (data) {
                                self.vue_data.user_name = data
                            })
                        },

                        sure_tree: function () {
                            var per_data = this;
                            self._rpc({
                                model: 'res.users',
                                method: 'create_per_data',
                                kwargs: {self_id: self.vue_data.group_id, per_name_id: self.vue_data.tree_date}
                            }).then(function (data) {
                                self.vue_data.tree_input = false
                                per_data.per_data_return(per_data)
                            })
                        }
                    },

                });
            })
        },
    });

    core.action_registry.add('edit_role', edit_role);
    return {'edit_role': edit_role};


});
