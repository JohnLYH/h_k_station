odoo.define('materials_change_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var materials_change_btn = Widget.extend({
        init: function (parent, model) {
            this._super(parent, model);
            this.vue_data = {
                id: model.params.id,
                res_id: model.params.res_id,
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
                file_name: ''
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
                    template_name: 'materials_change_btn'
                }
            }).then(function (el) {
                // 加载vue模板
                self.replaceElement($(el));
                self.vue = new Vue({
                    el: '#materials_remove_btn',
                    mounted() {
                        this.get_change_value()
                    },
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        get_change_value: function () {
                            var this_vue = this;
                            self._rpc({
                                model: 'maintenance_plan.reference_materials_manage',
                                method: 'get_change_value',
                                kwargs: {id: this_vue.id},
                            }).then(function (data) {
                                data = JSON.parse(data);
                                this_vue.numbering = data.numbering;
                                this_vue.edition = data.edition;
                                this_vue.file_name = data.file_name;
                                this_vue.field_type = data.field_type;
                            })
                        },
                        save: function () {
                            var self_vue = this;
                            if (self_vue.field_type === '') {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '請選擇文件類型',
                                    type: 'error'
                                });
                                return
                            }
                            if (/.*[\u4e00-\u9fa5]+.*$/.test(self_vue.edition)) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '版本不能有中文',
                                    type: 'error'
                                });
                                return
                            }
                            if (self_vue.edition.length > 16 || self_vue.edition.length <= 0) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '版本號16位以内且必填',
                                    type: 'error'
                                });
                                return
                            }
                            if (/.*[\u4e00-\u9fa5]+.*$/.test(self_vue.numbering)) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '編號不能有中文',
                                    type: 'error'
                                });
                                return
                            }
                            if (self_vue.numbering.length > 16 || self_vue.numbering.length <= 0) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '編號16位以内且必填',
                                    type: 'error'
                                });
                                return
                            }
                            if (self_vue.reasons_change.length > 100) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '變更原因100字以內',
                                    type: 'error'
                                });
                                return
                            }
                            if (self_vue.reasons_details.length > 5000) {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '變更細節5000字以內',
                                    type: 'error'
                                });
                                return
                            }
                            else {
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
                                    formData.append('res_id', self_vue.res_id);
                                    $.ajax({
                                        url: '/maintenance_plan/materials_change',
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
                            }
                        },
                        handleChange: function (file, fileList) {
                            this.files = file;
                        },
                        beforeAvatarUpload: function (file) {
                        },
                        cancel: function () {
                            self.getParent().destroy()
                        },
                        before_remove: function(file, fileList){
                            this.files = ''
                        },
                    }
                })
            })
        }

    });
    core.action_registry.add('materials_change_btn', materials_change_btn);
    return {
        materials_change_btn: materials_change_btn
    };
});