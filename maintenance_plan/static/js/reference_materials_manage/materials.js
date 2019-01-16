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
                self.do_action({
                    "name": "參考資料詳情",
                    "type": "ir.actions.client",
                    "tag": "materials_detail_btn",
                    "params": {record: self.record, id: self.id}
                })
            } else {
                self.do_action({
                    "name": "上傳文件",
                    "type": "ir.actions.client",
                    "tag": "materials_upload_btn",
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

odoo.define('materials_upload_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var materials_upload_btn = Widget.extend({
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
                files: '',
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
                            var self_vue = this;
                            self_vue.$confirm('確認上傳文件后將提交審核，是否繼續？', '提示', {
                                confirmButtonText: '确定',
                                cancelButtonText: '取消',
                                type: 'warning'
                            }).then(() => {
                                var formData = new FormData();
                                formData.append('file', self_vue.files.raw);
                                formData.append('field_type', self_vue.field_type);
                                formData.append('edition', self_vue.edition);
                                formData.append('numbering', self_vue.numbering);
                                formData.append('reasons_change', self_vue.reasons_change);
                                formData.append('reasons_details', self_vue.reasons_details);
                                formData.append('id', self_vue.id);
                                $.ajax({
                                    url: '/maintenance_plan/materials_upload_files',
                                    type: 'POST',
                                    data: formData,
                                    processData: false,  //tell jQuery not to process the data
                                    contentType: false,  //tell jQuery not to set contentType
                                    //这儿的三个参数其实就是XMLHttpRequest里面带的信息。
                                    success: function (response) {
                                        response = JSON.parse(response);
                                        if (response.error === 0) {
                                            self_vue.$notify({
                                                title: '成功',
                                                message: '上傳成功',
                                                type: 'success'
                                            });
                                            self.do_action(false);
                                        } else {
                                            self_vue.$notify({
                                                title: '錯誤',
                                                message: response.message,
                                                type: 'error'
                                            });
                                        }
                                    }
                                })
                            });

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
    core.action_registry.add('materials_upload_btn', materials_upload_btn);
    return {
        materials_upload_btn: materials_upload_btn
    };
});

odoo.define('materials_detail_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;

    var materials_detail_btn = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                description: '',
                equipment_model: '',
                wi: [],
                recovery_procedur: [],
                m_tube: [],
                fault_finding: [],
                edoc: [],
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
                    el: '#app',
                    mounted() {
                        this.materials_detail()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        save: function () {
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
                            })
                        },
                        come_to_detail: function () {

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
                            self._rpc({
                                model: 'maintenance_plan.equipment_model',
                                method: 'remove_reference_materials_manage',
                                kwargs: {id: data, res_id: self.id},
                            })
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