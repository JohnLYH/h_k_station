odoo.define('employees_management_action', function (require) {
    "use strict";
    var core = require('web.core');
    var Widget = require('web.Widget');

    var construct_id = 12345124;

    var employees_management_action = Widget.extend({
        app: undefined,
        group_id: 0,
        is_update: false,
        dom_id: 'employees_management_action' + construct_id++,
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
                kwargs: {module_name: 'user', template_name: 'employees_management'}
            })).then(function (res) {
                self.replaceElement($(res));
                var vue = new Vue({
                    el: '#employees_html',
                    data() {
                        return self.vue_data
                    },

                    methods: {
                                click_node: function(data){

                                   self._rpc({
                                              model: 'user.employees_get',
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
                                              model: 'user.employees_get',
                                              method:'page_size',
                                              kwargs: {'size':data}
                                            }).then(function(get_data){
                                              self.vue_data.tableData=get_data;
                                            });


                                 },

                                 handleCurrentChange: function(page){
                                   self._rpc({
                                              model: 'user.employees_get',
                                              method:'current_change',
                                              kwargs: {'record':page,'page':self.vue_data.tableData.length}
                                            }).then(function(get_data){
                                              self.vue_data.tableData=get_data;
                                            });
                                 },

                                 handleEdit: function(data){
                                     alert(self.vue_data.list_size)
//                                   self._rpc({
//                                              model: 'cdtct_dingtalk.cdtct_dingtalk_users',
//                                              method:'get_users',
//                                              kwargs: {'department_id':data.id}
//                                            }).then(function(get_data){
//                                              self.vue_data.tableData=get_data;
//                                            });


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
                                 loaddown: function(data){
                                      self.do_action({
                                                name: '\u5c0e\u5165\u4eba\u54e1\u4fe1\u606f',
                                                type: 'ir.actions.act_window',
                                                res_model: 'user.import_date',
                                                views: [[self.vue_data.views, 'form']],
                                                target: 'new',
                                            });


                                 },
                    },

                });
            })
        },
    });

    core.action_registry.add('employees_management_action', employees_management_action);
    return {'employees_management_action': employees_management_action};


});
