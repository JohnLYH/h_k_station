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
                            input:'',
                            textarea:'',
                            user_name:'',
                            departmentList:[],
                            default_checked_keys:[],
                            defaultProps: {
                                              children: 'children',
                                              label: 'label'
                                            },

                };
        },
        willStart: function () {

                    var self= this;

                    return self._rpc({
                        model: 'cdtct_dingtalk.cdtct_dingtalk_users',
                        method: 'get_department_users',
                    }).then(function(data){
                        self.vue_data.departmentList = data
                    })
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
                                click_node: function(data){
                                 },

                    },

                });
            })
        },
    });

    core.action_registry.add('edit_role', edit_role);
    return {'edit_role': edit_role};


});
