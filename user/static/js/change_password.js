odoo.define('change_password_usr', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var change_password_usr = Widget.extend({
        app: undefined,
        group_id: 0,
        is_update: false,
        dom_id: 'change_password_usr' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {
                input: '',
                user_id: action.context.paw,
                login: action.context.login
            };
        },
        start: function () {
            var self = this;

            $.when(
                this._rpc({
                    model: 'html_model.template_manage',
                    method: 'get_template_content',
                    kwargs: {module_name: 'user', template_name: 'change_password_usr'}
                })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#change_password_usr',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                        onSubmit: function () {
                            self._rpc({
                                model: 'res.users',
                                method: 'change_password_usr',
                                kwargs: {
                                    user_id: self.vue_data.user_id,
                                    paw: self.vue_data.input,
                                    login: self.vue_data.login
                                    }
                            })
                            self.do_action({"type": "ir.actions.act_window_close"})
                        },
                        cancel: function () {
                            self.do_action({"type": "ir.actions.act_window_close"})
                        },

                    },

                });
            })
        },
    });

    core.action_registry.add('change_password_usr', change_password_usr);
    return {'change_password_usr': change_password_usr};


});
