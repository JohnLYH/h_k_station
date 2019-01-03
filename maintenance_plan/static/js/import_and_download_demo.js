/**
 * Created by artorias on 2019/1/2.
 */
odoo.define('import_and_download_demo', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');

    var import_and_download_demo = Widget.extend({
        template: '',
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.vue_data = {

            }
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'import_and_download_demo'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#app',
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        submitUpload() {
                            this.$refs.upload.submit();
                        },
                        // 上传后提示
                        upload_success: function (response, file, fileList) {
                            if (response.error == false) {
                                this.$notify({
                                    title: '成功',
                                    message: response.message,
                                    type: 'success'
                                });
                            } else {
                                this.$notify({
                                    title: '警告',
                                    message: response.message,
                                    type: 'warning'
                                });
                                self.do_action({
                                    name: '下载错误文件',
                                    target: 'new',
                                    type: 'ir.actions.act_url',
                                    url: '/on_duty_manage/down_wrong_file?file_id=' + response.file_id
                                })
                            }
                        }
                    }
                })
            })
        }
    });
    core.action_registry.add('import_and_download_demo', import_and_download_demo);
    return {
        import_and_download_demo: import_and_download_demo
    }
});