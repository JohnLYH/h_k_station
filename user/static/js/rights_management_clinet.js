odoo.define('rights_management', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 1234;

    var rights_management = Widget.extend({
        app: undefined,
        group_id: 0,
        is_update: false,
        dom_id: 'rights_management' + construct_id++,
        init: function (parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.vue_data = {

                                departmentList:[],

                                defaultProps: {
                                                  children: 'children',
                                                  label: 'label'
                                                },

                                tableData: [],
                                multipleSelection: [],
                                default_checked_keys:[],
                                input:'',
                                currentPage4:1,
                                message:0,
                                value:[],
                                options:'',
                                size_:10,
                                list_size:[10, 20, 30, 40],

                };
        },

        willStart: function () {

                    var self= this;

                    return self._rpc({
                        model: 'res.users',
                        method: 'get_department_users',
                    }).then(function(data){
                        self.vue_data.tableData = data
                    })
            },

        start: function () {
            var self = this;

            $.when(
            this._rpc({
                model: 'html_model.template_manage',
                method: 'get_template_content',
                kwargs: {module_name: 'user', template_name: 'rights_management_clinet'}
            })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#rights_management',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                                click_node: function(data){

                                   self._rpc({
                                              model: 'res.users',
                                              method:'get_users',
                                              kwargs: {'department_id':data.id}
                                            }).then(function(get_data){
                                              self.vue_data.tableData=get_data.slice(0,10);
                                              self.vue_data.message=get_data.length;
                                            });


                                 },

                                 handleSelectionChange: function(data){
//                                   alert('123');
//                                   self._rpc({
//                                              model: 'user.employees_get',
//                                              method:'get_employees',
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


                                 },

                                 handleSizeChange: function(data){
                                   self._rpc({
                                              model: 'res.users',
                                              method:'page_size',
                                              kwargs: {'size':data}
                                            }).then(function(get_data){
                                              self.vue_data.tableData=get_data;
                                            });


                                 },

                                 handleCurrentChange: function(page){
                                   self._rpc({
                                              model: 'res.users',
                                              method:'current_change',
                                              kwargs: {'record':page,'page':self.vue_data.tableData.length}
                                            }).then(function(get_data){
                                              self.vue_data.tableData=get_data;
                                            });
                                 },

                                 handleEdit: function(data){
                               self.do_action({
                                                name: '\u7de8\u8f2f\u4eba\u54e1\u4fe1\u606f',
                                                type: 'ir.actions.client',
                                                tag: 'edit_role',
                                                target: 'new',
                                            });


                                 },

                                 handleReset: function(data){
                                 alert('handleReset')

//                                   self._rpc({
//                                              model: 'cdtct_dingtalk.cdtct_dingtalk_users',
//                                              method:'get_users',
//                                              kwargs: {'department_id':data.id}
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


                                 },

                                 handleDisable: function(data){
                                    alert('handleDisable')
//                                   self._rpc({
//                                              model: 'cdtct_dingtalk.cdtct_dingtalk_users',
//                                              method:'get_users',
//                                              kwargs: {'department_id':data.id}
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


                                 },

                                 search: function(data){
                                    alert('handleDisable')
//                                   self._rpc({
//                                              model: 'cdtct_dingtalk.cdtct_dingtalk_users',
//                                              method:'get_users',
//                                              kwargs: {'department_id':data.id}
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


                                 },

                                 reset: function(data){
                                    alert('handleDisable')
//                                   self._rpc({
//                                              model: 'cdtct_dingtalk.cdtct_dingtalk_users',
//                                              method:'get_users',
//                                              kwargs: {'department_id':data.id}
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


                                 },
                    },

                });
            })
        },
    });

    core.action_registry.add('rights_management', rights_management);
    return {'rights_management': rights_management};


});
