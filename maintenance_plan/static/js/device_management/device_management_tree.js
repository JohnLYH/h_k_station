/**
 *Time:2019/01/04 10:04
 *Author:lrc
 */

odoo.define('device_management', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var device_management = Widget.extend({
        init: function (parent, model) {
            var self = this;
            self.vue_data = {
                cols: [],
                tableData: [],
                leader_duty_type: 'off',
                name: '',
                month: moment().format("YYYY-MM"),

                is_checked_all: false,
                chioce_able: false,
                checkAll: false,
                choice_month: null,
                choice_checkbox: [],
                checked_duty_crop: [], // 选中的id
                value1: '',
                value2: ''
            };
            self._super(parent);
        },
        start: function () {
            var self = this;
            setTimeout(function () {
                // 获取vue模板
                self._rpc({
                    model: 'vue_template_manager.template_manage',
                    method: 'get_template_content',
                    kwargs: {
                        module_name: 'maintenance_plan',
                        template_name: 'device_management'
                    }
                }).then(function (el) {
                    // 加载vue模板
                    self.replaceElement($(el));
                    new Vue({
                        el: '#device_management',
                        mounted() {
                            // this.search()
                        },
                        data() {
                            return self.vue_data
                        },
                        methods: {
                            // 重置
                            reset: function () {
                                this.value1 = '';
                                this.value2 = '';
                            },
                            search: function () {
                                console.log( this.value1,this.value2,this.name)
                            },
                            // 下载模板选择弹窗
                            open_chioce: function () {
                                var this_vue = this;
                                this_vue.chioce_able = true
                                console.log("你點擊了他")
                            },
                            handleOpen(key, keyPath) {
                                // console.log(key, keyPath);
                              },
                            handleClose(key, keyPath) {
                                // console.log(key, keyPath);
                          }
                        }
                    })
                })
            }, 100)
        }

    });
    core.action_registry.add('device_management', device_management);
    return {
        device_management: device_management
    };
});