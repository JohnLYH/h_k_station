odoo.define('person_edit', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var person_edit = Widget.extend({
        app: undefined,
        group_id: 0,
        is_update: false,
        dom_id: 'person_edit' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {
                role_name: action.context.name,
                role_id: action.context.login,
                deparment: '',
                deparments: '',
                post: action.context.post,
                posts: '',
                role: action.context.role,
                roles: '',
                role_email: action.context.email,

            };
        },
        willStart: function () {
            var self = this
            return $.when(
                self._rpc({
                    model: 'res.users',
                    method: 'gt_all_department',
                }).then(function (get_data) {
                    self.vue_data.posts = get_data[0];
                    self.vue_data.roles = get_data[2];
                })
            )
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
                        onSubmit: function () {
                            self._rpc({
                                model: 'res.users',
                                method: 'edit_per_information',
                                kwargs: {
                                    name: self.vue_data.role_name,
                                    role_id: self.vue_data.role_id,
                                    deparment: self.vue_data.deparment,
                                    post: self.vue_data.post,
                                    role: self.vue_data.role,
                                    role_email: self.vue_data.role_email
                                }
                            }).then(function () {
                                core.bus.trigger('person_edit_return',{
                                    name: self.vue_data.role_name,
                                    login: self.vue_data.role_id,
                                    deparment: self.vue_data.deparment,
                                    post: self.vue_data.post,
                                    role: self.vue_data.role,
                                    email: self.vue_data.role_email
                                });
                                self.do_action({"type": "ir.actions.act_window_close"})
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

    core.action_registry.add('person_edit', person_edit);
    return {'person_edit': person_edit};


});
