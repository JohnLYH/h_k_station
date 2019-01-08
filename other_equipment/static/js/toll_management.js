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
                // TODO: 詳情
                console.log('詳情')
            }
            else if ($(event.target).hasClass('tool_inspection')) {
                // TODO: 检验
                self.do_action({
                    "name": "檢驗",
                    "type": "ir.actions.client",
                    "tag": "tool_management_inspection",
                    "target": "new",
                    "params": {record: self.record,id: self.id}
                })
                // console.log('检验')
            }else {
                self.vue.$confirm('設備類別刪除后不可恢復，是否確認刪除？', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    self._rpc({
                        model: self.record.model,
                        method: 'unlink',
                        args: [self.id],
                    }).then(function () {
                        self.vue.$message({
                            type: 'success',
                            message: '刪除成功!'
                        });
                        self.trigger_up('reload')
                    })
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
            this.vue_data = {
                id: model.params.id,
                equipment_name:'xxx',
                equipment_num: 'xxx',
                model: 'xxx',
                freq_of_cal: 'xxxx',
                last_maintenance_date: '',
                maintenance_due_data: '',
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
                        module_name: 'other_equipment',
                        template_name: 'tool_management_inspection'
                    }
                }).then(function (el) {
                    // 加载vue模板
                    self.replaceElement($(el));
                    new Vue({
                        el: '#approval_management',
                        mounted() {
                            this.get_tool_information()
                        },
                        data() {
                            return self.vue_data
                        },
                        methods: {
                            get_tool_information:function () {
                                console.log('测',this.vue_data)
                                var this_vue = this;
                                var get_info = self._rpc({
                                    model: 'other_equipment.other_equipment',
                                    method: 'search_read',
                                    domain: [['id', '=', this_vue.id]] || None,
                                });
                                $.when(get_info).then(function (tool_info) {
                                    console.log(tool_info);
                                    this_vue.equipment_name = tool_info.equipment_name;
                                    this_vue.equipment_num = tool_info.equipment_num;
                                    this_vue.model = tool_info.model;
                                    this_vue.freq_of_cal = tool_info.freq_of_cal;
                                    this_vue.last_maintenance_date = tool_info.last_maintenance_date;
                                    this_vue.maintenance_due_data = tool_info.maintenance_due_data;
                                    console.log('测',this_vue)
                                })
                            },
                        }
                    })
                })
            }, 100)
        }

    });
    core.action_registry.add('tool_management_inspection', tool_management_inspection);
    return {
        tool_management_inspection: tool_management_inspection
    };
});