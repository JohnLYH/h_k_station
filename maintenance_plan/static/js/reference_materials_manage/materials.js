odoo.define('materials_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var materials_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_materials_manage_tree_button', {widget: this}).trim());
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
            if ($(event.target).hasClass('materials_manage_detail')) {
                // self.do_action({
                //     name: "上傳文件",
                //     type: "ir.actions.act_window",
                //     res_model: "maintenance_plan.reference_materials_manage",
                //     views: [[false, "form"]],
                //     target: "new",
                //     // "params": {record: self.record, id: self.id}
                // }, {
                //     on_close: function () {
                //         self.trigger_up('reload')
                //     },
                //     size: 'medium',
                // })
            } else {
                self.do_action({
                    "name": "上傳文件",
                    "type": "ir.actions.client",
                    "tag": "materials_detail_btn",
                    "target": "new",
                    "params": {record: self.record, id: self.id}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    },
                    size: 'medium',
                })
            }
        }
    });
    widget_registry.add('materials_tree_button', materials_tree_button);
    return {materials_tree_button: materials_tree_button}

});

odoo.define('materials_detail_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var materials_detail_btn = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                options: [{
                    value: 'WI',
                    label: 'WI'
                }, {
                    value: 'M-tube',
                    label: 'M-tube'
                }, {
                    value: 'EDOC',
                    label: 'EDOC'
                }, {
                    value: 'Fault finding',
                    label: 'Fault finding'
                }, {
                    value: 'Recovery procedur',
                    label: 'Recovery procedur'
                }],
                field_type: '',
                select_file: '',
                edition: '',
                numbering: '',
                reasons_change: '',
                reasons_details: '',
                fileList: [],
                files:'',
            };
        },
        start: function () {
            var self = this;
            // 获取vue模板
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'materials_manage_upload'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#app',
                    mounted() {
                        // this.get_tool_information()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        save: function () {
                            alert('保存')

                        },
                        handleChange: function (file, fileList) {
                            this.files = file
                        },
                        cancel: function () {
                            self.getParent().destroy()
                        }
                    }
                })
            })
        }

    });
    core.action_registry.add('materials_detail_btn', materials_detail_btn);
    return {
        materials_detail_btn: materials_detail_btn
    };
});