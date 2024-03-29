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

                departmentList: [],

                defaultProps: {
                    children: 'children',
                    label: 'label'
                },

                tableData: [],
                multipleSelection: [],
                default_checked_keys: [],
                input: '',
                currentPage4: 1,
                message: 0,
                value: [],
                options: [
                    {value: 'normal', label: '正常'},
                    {value: 'disable', label: '禁用'},
                    {value: 'all', label: '全部'}
                ],
                size_: 30,
                node_record: '',
                edit_department_id: '',
                act_id: '',
                data5: [{'value': 'login', 'label': '部門分組', 'children': []}],
                tree_input: false,
                tree_date: '',
                tree_data5: '',
                data5_data: '',
                selectedDepartment: '',
                department_data: [],
                handleChange: '',
                handledepartment: '',
                optionsdepartment: '',
            };
        },

        willStart: function () {

            var self = this;

            var re_data = self._rpc({
                model: 'res.users',
                method: 'get_department_users',
            }).then(function (data) {
                self.vue_data.data5[0].children = data.department_tree
                self.vue_data.act_id = data.act_id
            })

            var select_data = self._rpc({
                model: 'user.department',
                method: 'get_equipment_class',
            }).then(function (data) {
                self.vue_data.optionsdepartment = data
            })
            return $.when(re_data,select_data)
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
                        click_node: function (data) {
                            self.vue_data.node_record = data.value;
                            self.vue_data.currentPage4 = 1;
                            self._rpc({
                                model: 'res.users',
                                method: 'get_users_info',
                                kwargs: {'department_id': data.value, 'page': 1, 'limit': 30}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data.users;
                                self.vue_data.message = get_data.count;
                                self.vue_data.edit_department_id = get_data.department;
                            });
                        },

                        click_node_page: function (data) {
                            self._rpc({
                                model: 'res.users',
                                method: 'get_users_info',
                                kwargs: {'department_id': self.vue_data.node_record, 'page': self.vue_data.currentPage4, 'limit': 30}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data.users;
                                self.vue_data.message = get_data.count;
                                self.vue_data.edit_department_id = get_data.department;
                            });
                        },

                        handleSelectionChange: function (data) {

                        },

                        handleSizeChange: function (data) {
                            self._rpc({
                                model: 'res.users',
                                method: 'page_size',
                                kwargs: {'size': data}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data;
                            });
                        },

                        handleCurrentChange: function (page) {
                            self.vue_data.currentPage4 = page;
                            self._rpc({
                                model: 'res.users',
                                method: 'per_current_change',
                                kwargs: {
                                    'record': page,
                                    'page': self.vue_data.tableData.length,
                                    'name': self.vue_data.input,
                                    'chose': self.vue_data.value,
                                    'message': self.vue_data.message,
                                }
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data;
                            });
                        },

                        handleEdit: function (index, row) {

                            var this_vue = this;
                            self.do_action({
                                name: '員工編輯',
                                type: 'ir.actions.client',
                                tag: 'person_edit',
                                target: 'new',
                                context: {
                                    'self_id': row.id,
                                    'name': row.name,
                                    'login': row.login,
                                    'post': row.post,
                                    'role': row.role,
                                    'email': row.email,
                                    'page': self.vue_data.currentPage4,
                                    'node': self.vue_data.node_record,
                                    'edit_id': self.vue_data.edit_department_id,
                                }
                            }, {
                                on_close: function () {
                                    this_vue.click_node_page(this_vue)
                                }
                            });
                        },

                        handleReset: function (index, row) {
                            self.do_action({
                                name: '重置密码',
                                type: 'ir.actions.client',
                                tag: 'change_password_usr',
                                target: 'new',
                                context: {paw: row.id, login: row.login},
                            }, {size: 'medium'});
                        },

                        handleDisable: function (index, row) {
                            var current_info = this
                            self._rpc({
                                model: 'res.users',
                                method: 'disable_info',
                                kwargs: {'disable_id': row.login}
                            }).then(function (get_data) {
                                current_info.click_node_page(current_info)
                            });
                        },

                        search: function (data) {
                           var search_data = this;
                            self._rpc({
                                model: 'res.users',
                                method: 'get_chose_user_info',
                                kwargs: {'name': self.vue_data.input, 'chose': self.vue_data.value}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data
                            });
                        },

                        reset: function (data) {
                            self.vue_data.input = '';
                            self.vue_data.value = '';
                        },

                        loaddown: function (data) {
                            self.do_action({
                                name: '導入數據',
                                type: 'ir.actions.act_window',
                                res_model: 'user.import_date',
                                views: [[self.vue_data.views, 'form']],
                                target: 'new',
                            });
                        },

                        enable: function (index, row) {
                            var start_act = this
                            self._rpc({
                                model: 'res.users',
                                method: 'enable_button_act',
                                kwargs: {value: row.state, self_id: row.id}
                            }).then(function (get_data) {
                                start_act.click_node_page(start_act)
                            });
                        },
                        crete_new_record: function () {
                            var this_vue = this
                            self.do_action({
                                name: '新增',
                                type: 'ir.actions.act_window',
                                res_model: 'res.users',
                                views: [[self.vue_data.act_id, 'form']],
                                target: 'new',
                            });
                        },

                        append(data) {
                            self.vue_data.data5_data = data
                            self.vue_data.tree_data5 = data.value;
                            self.vue_data.tree_date = '';
                            self.vue_data.selectedDepartment = [];
                            var data_chose = this;
                            $.when(self.vue_data.tree_input = true,
                            )
                        },

                        remove(node, data) {
                            self._rpc({
                                model: 'res.users',
                                method: 'delete_tree_button',
                                kwargs: {value: data.value}
                            })
                            const parent = node.parent;
                            const children = parent.data.children || parent.data;
                            const index = children.findIndex(d => d.id === data.value);
                            children.splice(index, 1);
                        },

                        data_return: function(){
                             self._rpc({
                                model: 'res.users',
                                method: 'get_department_users',
                            }).then(function (data) {
                                self.vue_data.data5[0].children = data.department_tree
                                self.vue_data.act_id = data.act_id
                            })
                        },

                        sure_tree: function () {
                            var button = this;
                            self._rpc({
                                model: 'res.users',
                                method: 'add_tree_button',
                                kwargs: {parent_id: self.vue_data.selectedDepartment, value: self.vue_data.tree_date}
                            }).then(function (get_data) {
                                if(get_data=='err'){
                                    alert('部門已近存在請從星輸入')

                                }else {
                                    var id = get_data;
                                    const newChild = {id: id++, label: self.vue_data.tree_date, children: []};
                                    if (!self.vue_data.data5_data.children) {
                                        button.$set(self.vue_data.data5_data, 'children', []);
                                    }
                                    button.data_return(button)
                                }
                            });
                            $.when(this.tree_input = false)

                        },

                        before_data: function () {
                            return self.vue_data.data5;
                        },

                        cancel_tree: function () {
                            this.tree_input = false
                        },

                        add_department: function () {
                        }
                    },

                });
            })
        },
    });

    core.action_registry.add('employees_management_action', employees_management_action);
    return {'employees_management_action': employees_management_action};

});
