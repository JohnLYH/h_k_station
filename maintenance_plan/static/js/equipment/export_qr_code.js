odoo.define('export_qr_code', function (require) {
    'use strict';

    var Widget = require('web.Widget');
    var core = require('web.core');

    var export_qr_code = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.vue_data = {
                tableData: record.params.records_list
            }
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'export_qr_code'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#export_qr_code_div',
                    data() {
                        return self.vue_data
                    },
                    methods: {
                        cancel: function () {
                            self.do_action(false)
                        },
                        enter: function () {
                            // 導出設備的二維碼
                            var this_vue = this;
                            this_vue.loading = this_vue.$loading({
                                lock: true
                            })
                            var oReq = new XMLHttpRequest();
                            oReq.open("POST", '/maintenance_plan/export_qr_code_zip', true);
                            oReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                            //指定返回类型
                            oReq.responseType = "arraybuffer";
                            oReq.onload = function (oEvent) {
                                this_vue.loading.close();
                                self.do_action(false);
                                if (oReq.readyState == 4 && oReq.status == 200) {
                                    var blob = new Blob([oReq.response], {
                                        type: "application/zip"
                                    });
                                    // 转换Blob完成，创建一个a标签用于下载
                                    var a = document.createElement('a');
                                    //点击事件
                                    var evt = document.createEvent("HTMLEvents");
                                    evt.initEvent("click", false, false);
                                    // 设置文件名
                                    a.download = moment().format("YYYY-MM-DD") + '下載设备二维码.zip';
                                    // 利用URL.createObjectURL()方法为a元素生成blob URL
                                    a.href = URL.createObjectURL(blob);
                                    a.click();
                                }
                            };
                            // 发送待参数的请求
                            oReq.send("qr_list=" + JSON.stringify(this_vue.tableData.map(function (record) {
                                return record.id
                            })));
                        }
                    },
                })
            })
        }
    });
    core.action_registry.add('export_qr_code', export_qr_code);
    return {
        export_qr_code: export_qr_code
    }
});