odoo.define('person_edit', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var person_edit = Widget.extend({
        dom_id: 'person_edit' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {
                role_name: action.context.name,
                role_id: action.context.login,
                post: action.context.post,
                posts: '',
                role: action.context.role,
                roles: '',
                role_email: action.context.email,
                department_list: [],
                selectedOptions: '',
                self_id: action.context.self_id,
                tree_input: false,
                old_deparment: action.context.node,
                ruleForm: {
                    role_name: action.context.name,
                    selectedOptions: '',
                    post: action.context.post,
                    role: action.context.role,
                    role_email: action.context.email
                },
                rules: {
                    role_name: [{required: true, message: '請輸入員工姓名', trigger: 'blur'}],
                    selectedOptions: [{required: true, message: '請選擇所屬部門', trigger: 'blur'}],
                    post: [{required: true, message: '請選擇崗位', trigger: 'blur'}],
                    role: [{required: true, message: '請選擇角色組', trigger: 'blur'}],
                    role_email: [{required: true, message: '請輸入郵箱地址', trigger: 'blur'}],
                },

            };
        },
        willStart: function () {
            var self = this

            var post_data = self._rpc({
                model: 'res.users',
                method: 'gt_all_department',
            }).then(function (get_data) {
                self.vue_data.posts = get_data[0];
                self.vue_data.roles = get_data[1];
            });

            var department_data = self._rpc({
                model: 'res.users',
                method: 'get_department_edit',
            }).then(function (data) {
                self.vue_data.department_list = data
            });

            var default_department = self._rpc({
                model: 'user.department',
                method: 'get_default_department_edit',
                kwargs: {self_id: self.vue_data.self_id}
            }).then(function (data) {
                console.log('99', data)
                self.vue_data.ruleForm.selectedOptions = data
            });

            return $.when(post_data, department_data,default_department)
        },

        start: function () {
            var self = this;

            $.when(
                this._rpc({
                    model: 'html_model.template_manage',
                    method: 'get_template_content',
                    kwargs: {module_name: 'user', template_name: 'person_edit'}
                })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#per_edit',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                        onSubmit: function (formName) {
                            this.$refs[formName].validate((valid) => {
                                if (valid) {
                                    self._rpc({
                                        model: 'res.users',
                                        method: 'edit_per_information',
                                        kwargs: {
                                            self_id: self.vue_data.self_id,
                                            name: self.vue_data.ruleForm.role_name,
                                            role_id: self.vue_data.ruleForm.role_id,
                                            deparment: self.vue_data.ruleForm.selectedOptions,
                                            old_deparment: self.vue_data.old_deparment,
                                            post: self.vue_data.ruleForm.post,
                                            role: self.vue_data.ruleForm.role,
                                            role_email: self.vue_data.ruleForm.role_email
                                        }
                                    }).then(function () {
                                        self.do_action({"type": "ir.actions.act_window_close"})
                                    })
                                } else {
                                }
                            })
                        },

                        cancel: function () {
                            self.do_action({"type": "ir.actions.act_window_close"})
                        },

                        handleChange: function () {
                            self._rpc({
                                model: 'res.users',
                                method: 'get_department_edit',
                            }).then(function (data) {
                                self.vue_data.department_list = data
                            })
                        }
                    },
                });
            })
        },
    });

    core.action_registry.add('person_edit', person_edit);
    return {'person_edit': person_edit};

});
