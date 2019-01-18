odoo.define('manage_record_details', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var manage_record_details = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                res_id: model.params.res_id,
                field_type: '',
                select_file_name: '',
                numbering: '',
                edition: '',
                reasons_change: '',
                reasons_details: '',
            }
            ;
        },
        start: function () {
            var self = this;
            // 获取vue模板
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'manage_record_details'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#manage_record_details',
                    mounted() {
                        this.get_details_value()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        get_details_value: function () {
                            var this_vue = this;
                            self._rpc({
                                model: 'maintenance_plan.reference_materials_manage_record',
                                method: 'get_details_value',
                                kwargs: {id: this_vue.res_id},
                            }).then(function (data) {
                                data = JSON.parse(data);
                                this_vue.numbering = data.numbering;
                                this_vue.field_type = data.field_type;
                                this_vue.select_file_name = data.file_name;
                                this_vue.edition = data.edition;
                                this_vue.reasons_change = data.reasons_change;
                                this_vue.reasons_details = data.reasons_details;
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
    core.action_registry.add('manage_record_details', manage_record_details);
    return {
        manage_record_details: manage_record_details
    };
});