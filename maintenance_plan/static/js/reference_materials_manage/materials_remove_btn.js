odoo.define('materials_remove_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var materials_remove_btn = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                res_id: model.params.res_id,
                reasons_details: '',
                numbering: '',
                edition: '',
                file_name: '',
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
                    template_name: 'materials_remove'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#materials_remove_btn',
                    mounted() {
                        this.get_remove_value()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        get_remove_value: function () {
                            var this_vue = this;
                            self._rpc({
                                model: 'maintenance_plan.reference_materials_manage',
                                method: 'get_remove_value',
                                kwargs: {id: this_vue.id},
                            }).then(function (data) {
                                data = JSON.parse(data);
                                this_vue.numbering = data.numbering;
                                this_vue.edition = data.edition;
                                this_vue.file_name = data.file_name;
                            })
                        },
                        save: function () {
                            var this_vue = this;
                            self._rpc({
                                model: 'maintenance_plan.equipment_model',
                                method: 'remove_reference_materials_manage',
                                kwargs: {
                                    id: this_vue.id,
                                    res_id: this_vue.res_id,
                                    reasons_details: this_vue.reasons_details
                                },
                            }).then(function (result) {
                                var response = JSON.parse(result)
                                if (response.error === 0) {
                                    self.do_action(false)
                                } else {
                                    this_vue.$notify({
                                        title: '錯誤',
                                        message: response.message,
                                        type: 'error'
                                    });
                                }
                            })
                        },
                        cancel: function () {
                            self.getParent().destroy()
                        },
                    }
                })
            })
        }

    });
    core.action_registry.add('materials_remove_btn', materials_remove_btn);
    return {
        materials_remove_btn: materials_remove_btn
    };
});