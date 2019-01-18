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
                            if (self_vue.files === '') {
                                self_vue.$notify({
                                    title: '錯誤',
                                    message: '請上傳文件',
                                    type: 'error'
                                });
                                return
                            } else {
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
                            }
                        },
                        handleChange: function (file, fileList) {
                            this.files = file;
                        },
                        before_remove: function(file, fileList){
                            this.files = ''
                        },
                        beforeAvatarUpload: function (file) {
                            console.log(file.type);
                            console.log(file.size);
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