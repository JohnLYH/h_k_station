/**
 *Time:2019/01/04 10:04
 *Author:lrc
 */

odoo.define('equipment_management', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var equipment_management = Widget.extend({
        init: function (parent, model) {
            var self = this;
            self.vue_data = {
                name: '',
                date: '',
                chioce_able_visible: false,
                current_node: '',
                tree_data: [{
                    label: '一级 1',
                    children: [{
                        label: '二级 1-1',
                        children: [{
                            label: '三级 1-1-1'
                        }]
                    }]
                }, {
                    label: '一级 2',
                    children: [{
                        label: '二级 2-1',
                        children: [{
                            label: '三级 2-1-1'
                        }]
                    }, {
                        label: '二级 2-2',
                        children: [{
                            label: '三级 2-2-1'
                        }]
                    }]
                }, {
                    label: '一级 3',
                    children: [{
                        label: '二级 3-1',
                        children: [{
                            label: '三级 3-1-1'
                        }]
                    }, {
                        label: '二级 3-2',
                        children: [{
                            label: '三级 3-2-1'
                        }]
                    }]
                }]
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
                        template_name: 'equipment_management'
                    }
                }).then(function (el) {
                    // 加载vue模板
                    self.replaceElement($(el));
                    new Vue({
                        el: '#app',
                        mounted() {
                            // this.search()
                        },
                        data() {
                            return self.vue_data
                        },
                        computed: {
                            get_tree_route: function () {
                                return 'w'
                            }
                        },
                        methods: {
                            // 重置
                            reset: function () {
                                this.value1 = '';
                                this.value2 = '';
                            },
                            search: function () {
                                console.log(this.value1, this.value2, this.name)
                            },
                            // 下载模板选择弹窗
                            open_chioce: function () {
                                var this_vue = this;
                                this_vue.chioce_able = true
                                console.log("你點擊了他")
                            },
                            download_code: function () {

                            },
                            handleOpen(key, keyPath) {
                                // console.log(key, keyPath);
                            },
                            handleClose(key, keyPath) {
                                // console.log(key, keyPath);
                            },
                            add_equipment: function (event, node) {
                                event.stopPropagation();
                                console.log(node)
                            },
                            delete_equipment: function (event, node) {
                                event.stopPropagation()
                            },
                            tree_click: function (data, node, dom) {
                                console.log(data)
                                console.log(node)
                                console.log(dom)
                            }
                        }
                    })
                })
            }, 100)
        }

    });
    core.action_registry.add('equipment_management', equipment_management);
    return {
        equipment_management: equipment_management
    };
});