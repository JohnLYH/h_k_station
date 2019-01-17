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
                value: '',
                options: [
                    {value: 'normal', label: '正常'},
                    {value: 'disable', label: '禁用'},
                    {value: 'all', label: '全部'}
                ],
                size_: 10,
                list_size: [10, 20, 30, 40],
                view_id: '',
                state: '',
            };
        },

        willStart: function () {

            var self = this;

            var info_data = self._rpc({
                model: 'res.groups',
                method: 'get_permiss_role',
            }).then(function (data) {
                self.vue_data.tableData = data.record;
                self.vue_data.view_id = data.view_id;
            });

            var count_info = self._rpc({
                model: 'res.groups',
                method: 'calculate_per_couont',
            })

            return $.when(info_data, count_info)
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
                        date_return: function (data) {

                            self._rpc({
                                model: 'res.users',
                                method: 'get_users',
                                kwargs: {'department_id': data.id}
                            }).then(function (get_data) {
                            });


                        },

                        date_return_act: function (data) {
                            var act_info = self._rpc({
                                model: 'res.groups',
                                method: 'get_permiss_role',
                            }).then(function (data) {
                                self.vue_data.tableData = data.record
                            });

                            return $.when(act_info)

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
                            self._rpc({
                                model: 'res.users',
                                method: 'current_change',
                                kwargs: {'record': page, 'page': self.vue_data.tableData.length}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data;
                            });
                        },

                        handleEdit: function (index, row) {
                            var this_vue = this
                            self.do_action({
                                name: '權限管理編輯',
                                type: 'ir.actions.client',
                                res_id: row.id,
                                tag: 'edit_role',
                                target: 'new',
                                context: {
                                    role_name: row.name,
                                    per: row.permission_illust,
                                    groups_id: row.id
                                },
                            }, {
                                on_close: function () {
                                    this_vue.date_return_act(this_vue)
                                }
                            });
                        },

                        handleReset: function (data) {
                            alert('handleReset')
                        },

                        handleDisable: function (index, row) {
                            var self_date = this;
                            self._rpc({
                                model: 'res.groups',
                                method: 'get_disable_info_act',
                                kwargs: {'name': row.name}
                            }).then(function (get_data) {
                                self_date.date_return_act(self_date)
                            });
                        },

                        handleDelete: function (index, row) {
                            this.$confirm('是否刪除本條記錄', '提示', {
                                confirmButtonText: '确定',
                                cancelButtonText: '取消',
                                type: 'warning'
                            }).then(() => {
                                var delete_date = this;
                                self._rpc({
                                    model: 'res.groups',
                                    method: 'delete_record',
                                    kwargs: {'self_id': row.id}
                                }).then(function (get_data) {
                                    delete_date.date_return_act(delete_date)
                                });
                            }).catch(() => {
                                this.$message({
                                    type: 'info',
                                    message: '已取消删除'
                                });
                            });

                        },

                        search: function (data) {
                            self._rpc({
                                model: 'res.groups',
                                method: 'permissions_search',
                                kwargs: {'name': self.vue_data.input, 'chose': self.vue_data.value}
                            }).then(function (get_data) {
                                self.vue_data.tableData = get_data
                            });
                        },

                        reset: function (data) {
                            self.vue_data.input = '';
                            self.vue_data.value = '';
                        },
                        create_rec: function () {
                            var this_vue = this
                            self.do_action({
                                name: '新增',
                                type: 'ir.actions.client',
                                tag: 'permiss_add_button',
                                target: 'new',
                            }, {
                                on_close: function () {
                                    this_vue.date_return_act(this_vue)
                                }
                            });
                        },
                        handleiStart: function (index, row) {
                            var start_act = this
                            self._rpc({
                                model: 'res.groups',
                                method: 'start_button_act',
                                kwargs: {value: row.state, self_id: row.id}
                            }).then(function (get_data) {
                                start_act.date_return_act(start_act)
                            });

                        },
                    },

                });
            })
        },
    });

    core.action_registry.add('rights_management', rights_management);
    return {'rights_management': rights_management};


});
