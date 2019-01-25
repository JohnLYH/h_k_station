odoo.define('materials_detail_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var data_manager = require('web.data_manager');

    var materials_detail_btn = Widget.extend({
            init: function (parent, model) {
                this._super(parent, model);
                this.vue_data = {
                    id: model.params.id,
                    record: model.params.record,
                    description: '',
                    equipment_model: '',
                    wi: [],
                    recovery_procedur: [],
                    m_tube: [],
                    fault_finding: [],
                    edoc: [],
                    url: '',
                    upload_tpye: '',
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
                        template_name: 'materials_manage_details'
                    }
                }).then(function (el) {
                    // 加载vue模板
                    self.replaceElement($(el));
                    self.vue = new Vue({
                        el: '#details',
                        mounted() {
                            this.materials_detail()
                        },
                        data() {
                            return self.vue_data
                        },
                        methods: {
                            upload_btn: function () {
                                var self_vue = this;
                                self.do_action({
                                    "name": "上傳文件",
                                    "type": "ir.actions.client",
                                    "tag": "materials_upload_btn",
                                    "target": "new",
                                    "params": {record: self_vue.record, id: self_vue.id}
                                }, {
                                    on_close: function () {
                                        self_vue.materials_detail()
                                    },
                                    size: 'medium',
                                })
                            },
                            cancel: function () {
                                self.getParent().destroy()
                            },
                            materials_detail: function () {
                                var self_vue = this;
                                self._rpc({
                                    model: 'maintenance_plan.equipment_model',
                                    method: 'get_value',
                                    kwargs: {id: self_vue.id},
                                }).then(function (data) {
                                    data = JSON.parse(data);
                                    self_vue.description = data.description;
                                    self_vue.equipment_model = data.equipment_model;
                                    self_vue.wi = data.wi;
                                    self_vue.recovery_procedur = data.recovery_procedur;
                                    self_vue.m_tube = data.m_tube;
                                    self_vue.fault_finding = data.fault_finding;
                                    self_vue.edoc = data.edoc;
                                    self_vue.url = data.url;
                                    self_vue.upload_tpye = data.upload_tpye;
                                })
                            },
                            come_to_detail: function () {
                                var this_detail = this;
                                event.stopPropagation();
                                self.do_action({
                                    name: '變更記錄',
                                    type: 'ir.actions.act_window',
                                    res_model: 'maintenance_plan.reference_materials_manage_record',
                                    views: [[false, 'list']],
                                    target: 'current',
                                    domain: [['reference_materials_manage_id', '=', this_detail.id]],
                                    context: {'description': this_detail.description,'equipment_model': this_detail.equipment_model}
                                });
                                // TODO: 刷新了之後顯示不出來
                            },
                            remove: function (data) {
                                var self_vue = this;
                                self.do_action({
                                    "name": "刪除文件",
                                    "type": "ir.actions.client",
                                    "tag": "materials_remove_btn",
                                    "target": "new",
                                    "params": {id: data, res_id: self_vue.id}
                                }, {
                                    on_close: function () {
                                        self_vue.materials_detail()
                                    },
                                    size: 'medium',
                                })
                            },
                            change: function (data) {
                                var self_vue = this;
                                self.do_action({
                                    "name": "修改文件",
                                    "type": "ir.actions.client",
                                    "tag": "materials_change_btn",
                                    "target": "new",
                                    "params": {id: data, res_id: self_vue.id}
                                }, {
                                    on_close: function () {
                                        self_vue.materials_detail()
                                    },
                                    size: 'medium',
                                })
                            },
                            // go_to_pdf: function(id) {
                            //     alert(id)
                            // }
                        }
                    })
                })
            }

        })
    ;
    core.action_registry.add('materials_detail_btn', materials_detail_btn);
    return {
        materials_detail_btn: materials_detail_btn
    };
})
;