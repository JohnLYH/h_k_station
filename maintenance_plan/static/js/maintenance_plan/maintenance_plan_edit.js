/**
 * Created by artorias on 2019/1/4.
 */
odoo.define('maintenance_plan_edit', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');

    var maintenance_plan_edit = Widget.extend({
        init: function (parent, record, node) {
            var self = this;
            this._super(parent, record, node);
            this.record = record.params.record;
            this.max_advance_days = 0;
            this.max_delay_days = 0;

            this.vue_data = {
                num: this.record.data.num,
                deps: [], // 選擇班組下拉
                deps_props: {
                    label: 'name',
                    value: 'id',
                    children: 'children'
                },
                work_order_type: this.record.data.work_order_type,
                equipment_num: this.record.data.equipment_num,
                display_plan_time: this.record.data.display_plan_time,
                pickerDate: {
                    disabledDate(time) {
                        var this_time = moment(time);
                        return !(this_time >= self.max_advance_days && this_time <= self.max_delay_days);
                    }
                },
                form: {
                    display_action_time: this.record.data.display_action_time || '',
                    selected_dep: '', // 選擇班組
                },
                rules: {
                    display_action_time: [
                        {required: true, message: '請選擇具體執行時間', trigger: 'change'},
                    ],
                    selected_dep: [
                        {required: true, message: '請選擇執行班組', trigger: 'change'},
                    ]
                }
            }
        },
        willStart: function () {
            var self = this;
            // 獲取最大日期參數
            var get_config = self._rpc({
                model: 'maintenance_plan.maintenance.plan',
                method: 'get_config'
            }).then(function (config) {
                self.max_advance_days = self.record.data.plan_start_time.subtract(config.max_advance_days, 'days');
                self.max_delay_days = self.record.data.plan_end_time.add(config.max_delay_days, 'days');
            });
            // 獲取班組tree圖
            var get_deps = self._rpc({
                model: 'maintenance_plan.maintenance.plan',
                method: 'get_departs'
            }).then(function (deps) {
                self.vue_data.deps = deps
            });
            return $.when(get_config, get_deps)
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'maintenance_plan_edit'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#app',
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        cancel: function () {
                            self.do_action(false)
                        },
                        confirm: function (formName) {
                            var this_vue = this;
                            this.$refs[formName].validate((valid) => {
                                if (valid) {
                                    this_vue.$confirm('工單指派后不可修改，是否確認指派？', '提示', {
                                        confirmButtonText: '确定',
                                        cancelButtonText: '取消',
                                        type: 'warning'
                                    }).then(() => {
                                        self._rpc({
                                            model: 'maintenance_plan.maintenance.plan',
                                            method: 'assign_work_order',
                                            kwargs: {
                                                order_id: self.record.res_id,
                                                action_time: this_vue.form.display_action_time,
                                                dep: this_vue.form.selected_dep
                                            }
                                        }).then(function () {
                                            this_vue.$message({
                                                type: 'success',
                                                message: '更改成功!'
                                            });
                                            self.do_action(false);
                                        })
                                    });
                                } else {
                                    return false;
                                }
                            });
                        },
                    }
                })
            })
        }
    });
    core.action_registry.add('maintenance_plan_edit', maintenance_plan_edit);
    return {
        maintenance_plan_edit: maintenance_plan_edit
    }
});