odoo.define('tool_management', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var tool_management = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_tool_management_tree_button', {widget: this}).trim());
            this.replaceElement($el);
            this.vue = new Vue({
                el: '#app',
                data() {
                    return {}
                }
            });
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            if ($(event.target).hasClass('tool_detail')) {
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'other_equipment.other_equipment',
                    res_id: self.id,
                    views: [[false, "form"]],
                })
            } else if ($(event.target).hasClass('tool_inspection')) {
                self.do_action({
                    "name": "檢驗",
                    "type": "ir.actions.client",
                    "tag": "tool_management_inspection",
                    "target": "new",
                    "params": {record: self.record, id: self.id}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    },
                })
            } else {
                self.do_action({
                    "name": "報廢",
                    "type": "ir.actions.client",
                    "tag": "tool_management_scrap",
                    "target": "new",
                    "params": {record: self.record, id: self.id}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    },
                });
            }
        }
    });
    widget_registry.add('tool_management', tool_management);
    return {tool_management: tool_management}

});

odoo.define('tool_management_inspection', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var tool_management_inspection = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                equipment_name: '',
                equipment_num: '',
                model: '',
                freq_of_cal: '',
                last_maintenance_date: '',
                maintenance_due_data: '',
                remark: ''
            };
        },
        start: function () {
            var self = this;
            // 获取vue模板
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'other_equipment',
                    template_name: 'tool_management_inspection'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#tool_management_inspection',
                    mounted() {
                        this.get_tool_information()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        get_tool_information: function () {
                            var this_vue = this;
                            var get_info = self._rpc({
                                model: 'other_equipment.other_equipment',
                                method: 'search_read',
                                domain: [['id', '=', this_vue.id]] || None,
                            });
                            $.when(get_info).then(function (tool_info) {
                                this_vue.equipment_name = tool_info[0].equipment_name;
                                this_vue.equipment_num = tool_info[0].equipment_num;
                                this_vue.model = tool_info[0].model;
                                this_vue.freq_of_cal = tool_info[0].freq_of_cal;
                                this_vue.last_maintenance_date = tool_info[0].last_maintenance_date;
                                this_vue.maintenance_due_data = tool_info[0].maintenance_due_data;

                            });
                        },
                        save: function () {
                            var this_vue = this;
                            this_vue.$confirm('是否確認保存校驗信息？', '提示', {
                                confirmButtonText: '确定',
                                cancelButtonText: '取消',
                                type: 'warning'
                            }).then(() => {
                                self._rpc({
                                    model: 'other_equipment.other_equipment',
                                    method: 'save_tool_management_inspection',
                                    kwargs: {
                                        'id': this_vue.id,
                                        'equipment_name': this_vue.equipment_name,
                                        'equipment_num': this_vue.equipment_num,
                                        'model': this_vue.model,
                                        'freq_of_cal': this_vue.freq_of_cal,
                                        'last_maintenance_date': this_vue.last_maintenance_date,
                                        'maintenance_due_data': this_vue.maintenance_due_data,
                                        'remark': this_vue.remark
                                    }
                                }).then(function (e) {
                                    if (e) {
                                        self.do_action(false);
                                    } else {
                                        self.vue.$message({
                                            message: '未找到這條記錄',
                                            type: 'warning'
                                        });
                                    }
                                });
                            });
                        },
                        cancel: function () {
                            self.getParent().destroy()
                        },
                        reverse_maintenance_due_data: function () {
                            var this_vue = this;
                            console.log(moment(this_vue.last_maintenance_date).format('l'));
                            var freq_of_cal = this_vue.freq_of_cal;
                            if (freq_of_cal === 'ON CONDITION') {
                                return
                            } else {
                                // l是 YYYY-MM-DD格式
                                var new_maintenance_due_data = moment(this_vue.last_maintenance_date).add(Number(freq_of_cal), 'months').format('l');
                                this_vue.maintenance_due_data = new_maintenance_due_data
                            }
                        }

                    }
                })
            })
        }

    });
    core.action_registry.add('tool_management_inspection', tool_management_inspection);
    return {
        tool_management_inspection: tool_management_inspection
    };
});

odoo.define('tool_management_scrap', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var tool_management_scrap = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                equipment_name: '',
                equipment_num: '',
                model: '',
                brand: '',
                remark: ''
            };
        },
        start: function () {
            var self = this;
            // 获取vue模板
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'other_equipment',
                    template_name: 'tool_management_scrap'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#tool_management_scrap',
                    mounted() {
                        this.get_tool_information()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        get_tool_information: function () {
                            var this_vue = this;
                            var get_info = self._rpc({
                                model: 'other_equipment.other_equipment',
                                method: 'search_read',
                                domain: [['id', '=', this_vue.id]] || None,
                            });
                            $.when(get_info).then(function (tool_info) {
                                this_vue.equipment_name = tool_info[0].equipment_name;
                                this_vue.equipment_num = tool_info[0].equipment_num;
                                this_vue.model = tool_info[0].model;
                                this_vue.brand = tool_info[0].brand;
                            });
                        },
                        save: function () {
                            var this_vue = this;
                            this_vue.$confirm('是否確認該設備已報廢？', '提示', {
                                confirmButtonText: '确定',
                                cancelButtonText: '取消',
                                type: 'warning'
                            }).then(() => {
                                self._rpc({
                                    model: 'other_equipment.other_equipment',
                                    method: 'save_tool_management_scrap',
                                    kwargs: {
                                        'id': this_vue.id,
                                        'equipment_name': this_vue.equipment_name,
                                        'equipment_num': this_vue.equipment_num,
                                        'model': this_vue.model,
                                        'brand': this_vue.brand,
                                        'remark': this_vue.remark
                                    }
                                }).then(function (e) {
                                    if (e) {
                                        self.do_action(false);
                                        // self.getParent().destroy();
                                        // window.location.reload();
                                        // return this.parent.load(['invitations']);
                                    } else {
                                        self.vue.$message({
                                            message: '未找到這條記錄',
                                            type: 'warning'
                                        });
                                    }
                                });
                            });
                        },
                        cancel: function () {
                            self.getParent().destroy()
                        }
                    }
                })
            })
        }

    });
    core.action_registry.add('tool_management_scrap', tool_management_scrap);
    return {
        tool_management_scrap: tool_management_scrap
    };
});