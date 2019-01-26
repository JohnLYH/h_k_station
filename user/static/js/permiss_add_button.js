odoo.define('permiss_add_button', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var permiss_add_button = Widget.extend({
        dom_id: 'permiss_add_button' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {
                name: '',
                permiss: '',
                person_data: '',
                options: '',
                departmentList: '',
                default_checked_keys: '',
                defaultProps: {
                    children: 'children',
                    label: 'name'
                },
                ruleForm: {name:''},
                rules: {name: [{required: true, message: '請輸入角色組姓名', trigger: 'blur'}],},
            };
        },

        willStart: function () {
            var self = this;
            var user_date = self._rpc({
                model: 'res.groups',
                method: 'get_new_create_data',
            }).then(function (data) {
                self.vue_data.options = data
            });
            var tree_date = self._rpc({
                model: 'res.groups',
                method: 'get_group_data',
                kwargs: {group_id: false},
            }).then(function (data) {
                self.vue_data.departmentList = data.cats
            })

            return $.when(user_date, tree_date)
        },

        start: function () {
            var self = this;
            $.when(
                this._rpc({
                    model: 'html_model.template_manage',
                    method: 'get_template_content',
                    kwargs: {module_name: 'user', template_name: 'permiss_add_button'}
                })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#permiss_add_button',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                        click_node: function (date) {
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
                                        method: 'creste_new_record',
                                        kwargs: {
                                            name: self.vue_data.ruleForm.name,
                                            permiss: self.vue_data.permiss,
                                            user_name: self.vue_data.person_data,
                                            tree_id: implied_ids,
                                        },
                                    }).then(function (data) {
                                        self.vue_data.user_name = data
                                        self.do_action({"type": "ir.actions.act_window_close"})
                                    })
                                }
                                else {

                                }
                            })
                        },
                        cancel: function () {
                            self.do_action({"type": "ir.actions.act_window_close"})
                        }
                    },

                });
            })
        },
    });

    core.action_registry.add('permiss_add_button', permiss_add_button);
    return {'permiss_add_button': permiss_add_button};


});
