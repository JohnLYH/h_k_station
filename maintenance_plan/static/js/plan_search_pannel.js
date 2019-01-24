odoo.define("plan_search_pannel", function (require) {
    "use strict";

    // 自定义控制面版，添加js进行更加灵活的控制

    var widgetRegistry = require('web.widget_registry');
    var search_pannel_default = require('layui_theme.search_pannel_default');
    var core = require('web.core');
    var Dialog = require('web.Dialog');

    var plan_search_pannel = search_pannel_default.extend({
        events: _.extend({}, search_pannel_default.prototype.events, {
            // 導出工單
            'click .export_excel': function (event) {
                var controller = this.getParent().getParent().pager.state;
                this.download_template_excel(
                    '/maintenance_plan/export_work_order',
                    'application/vnd.ms-excel',
                    '導出工單.xlsx',
                    'domain=' + JSON.stringify(this.domains) + '&limit=' + controller.limit + '&offset=' + controller.current_min
                )
            },
            // 導入維修計劃管理
            'click .put_in_excel': function (event) {
                this.put_in_excel(this.$el.find('[name="file"]'), '/maintenance_plan/put_in_excel/', this.success_callback)
            },
            'click .equipment_search_apply': 'equipment_search_apply', // 設備頁面的搜索，因為有左側設備類型，單獨提出
            'click .equipment_reset_search': 'equipment_reset_search', // 設備頁面的重置搜索，因為有左側設備類型，單獨提出
            // 導入設備
            'click .put_in_equipment': function (event) {
                this.put_in_excel(this.$el.find('[name="file"]'), '/maintenance_plan/equipment_put_in_excel/', this.put_in_equipment_callback)
            },
            'click .export_qr_code': 'export_qr_code', // 導出設備二維碼
        }),

        start: function () {
            var self = this;
            self.domains = [];
            this.vue = new Vue({
                el: '#app',
                data() {
                    return {
                        fullscreenLoading: false
                    }
                }
            });
            return self._super()
        },

        /**
         * 請求後台下載excel模板
         * @param url
         * @param type
         * @param name
         * @param params
         */
        download_template_excel: function (url, type, name, params) {
            var self = this;
            var oReq = new XMLHttpRequest();
            oReq.open("POST", url, true);
            oReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            //指定返回类型
            oReq.responseType = "arraybuffer";
            oReq.onload = function (oEvent) {
                if (self.loading) {
                    self.loading.close();
                }
                if (oReq.readyState == 4 && oReq.status == 200) {
                    var blob = new Blob([oReq.response], {
                        type: type
                    });
                    // 转换Blob完成，创建一个a标签用于下载
                    var a = document.createElement('a');
                    //点击事件
                    var evt = document.createEvent("HTMLEvents");
                    evt.initEvent("click", false, false);
                    // 设置文件名
                    a.download = name;
                    // 利用URL.createObjectURL()方法为a元素生成blob URL
                    a.href = URL.createObjectURL(blob);
                    a.click();
                }
            };
            // 发送待参数的请求
            oReq.send(params);
        },

        /**
         * 上傳excel的具體執行函數
         * @param {*} dom: 上傳的文件input[name=file]的dom
         * @param {str} url: 上傳url
         */
        uploadExcel: function (dom, url, success_callback) {
            var file = dom.files[0];
            var self = this;
            // new一个FormData实例
            var formData = new FormData();
            formData.append('file', file);
            return $.ajax({
                url: url,
                type: 'POST',
                data: formData,
                processData: false, //tell jQuery not to process the data
                contentType: false, //tell jQuery not to set contentType
                //这儿的三个参数其实就是XMLHttpRequest里面带的信息。
                beforeSend: function (xhr) {
                    self.loading = self.vue.$loading({
                        lock: true
                    })
                },
                error: function (textStatus) {
                    self.loading.close();
                    self.vue.$notify({
                        title: '錯誤',
                        message: '導入發生了錯誤，請聯繫管理員',
                        type: 'error'
                    });
                },
                success: function (response) {
                    if (self.loading) {
                        self.loading.close();
                    }
                    response = JSON.parse(response);
                    success_callback(self, response)
                }
            })
        },

        /**
         * ajax成功后的回調
         * @param {*} response
         */
        success_callback: function (self, response) {
            if (response.error === false) {
                self.vue.$notify({
                    title: '成功',
                    message: '上傳成功',
                    type: 'success'
                });
                self.trigger_up('reload')
            } else if (response.error === true && response.file_id) {
                self.vue.$notify({
                    title: '警告',
                    message: response.message,
                    type: 'warning'
                });
                self.trigger_up('reload');
                self.do_action({
                    name: '返回錯誤文件',
                    target: 'new',
                    type: 'ir.actions.act_url',
                    url: '/maintenance_plan/down_wrong_file?file_id=' + response.file_id
                })
            } else {
                self.vue.$notify({
                    title: '錯誤',
                    message: response.message,
                    type: 'error'
                });
            }
        },

        /**
         * 導入設備后的回調
         * @param {*} self
         * @param {*} response
         */
        put_in_equipment_callback: function (self, response) {
            self.trigger_up('reload');
            if (response.error === true && !response.file_id) {
                self.vue.$notify({
                    title: '錯誤',
                    message: response.message,
                    type: 'error'
                });
                return
            }
            if (response.error === true && response.file_id) {
                self.do_action({
                    name: '返回錯誤文件',
                    target: 'new',
                    type: 'ir.actions.act_url',
                    url: '/maintenance_plan/down_wrong_file?file_id=' + response.file_id
                });
            }
            var dialog = new Dialog(self, {
                title: "導入設備",
                size: 'medium',
                buttons: [],
                $content: core.qweb.render('tem_equipment_callback', {
                    response: response
                })
            });
            dialog.opened().then(function () {
                dialog.$('.download_qr').click(function () {
                    // 導出設備的二維碼
                    self.loading = self.vue.$loading({
                        lock: true
                    })
                    self.download_template_excel(
                        '/maintenance_plan/export_qr_code_zip',
                        'application/zip',
                        moment().format("YYYY-MM-DD") + '导入设备二维码.zip',
                        "qr_list=" + JSON.stringify(response.qr_code_record_ids)
                    )
                });
                dialog.$('.dialog_close').click(function () {
                    dialog.close()
                });
            });
            dialog.open();
        },

        /**
         * 點擊導入設備
         * @param {*} 上傳的文件input[name=file]的dom
         * @param {str} 上傳url
         */
        put_in_excel: function (target, url, success_callback) {
            var self = this;
            var dialog = new Dialog(self, {
                title: "導入設備",
                size: 'small',
                buttons: [],
                $content: core.qweb.render('tem_equipment_put_in_excel')
            });
            dialog.opened().then(function () {
                // 上傳文件
                dialog.$('.put_in').click(function () {
                    target.change(function () {
                        if ($(this).val()) {
                            var fileName = $(this).val().substring($(this).val().lastIndexOf(".") + 1).toLowerCase();
                            if (fileName != "xlsx") {
                                self.vue.$notify({
                                    title: '錯誤',
                                    message: '请选择xlsx格式文件上传！',
                                    type: 'error'
                                });
                                $(this).val("");
                                return
                            }
                            dialog.close()
                            self.uploadExcel(this, url, success_callback);
                            $(this).val("");
                        }
                    });
                    target.trigger('click');
                });
                // 下載模板
                dialog.$('.download').click(function () {
                    self.download_template_excel(
                        '/maintenance_plan/download_template_excel',
                        "application/vnd.ms-excel",
                        '導入設備模板.xlsx',
                        'path=static/excel/equipment_template.xlsx'
                    )
                });
                dialog.$('.dialog_close').click(function () {
                    dialog.close()
                });
            });
            dialog.open();
        },

        /**
         * 導出tree勾選二維碼
         * @param {*} event
         */
        export_qr_code: function (event) {
            var self = this;
            // 獲取勾選記錄
            var records_list = self.getParent().getParent().getSelectedRecords().map(function (record) {
                return {
                    id: record.res_id,
                    num: record.data.num || '',
                    description: record.data.description,
                    serial_number: record.data.serial_number,
                    model_name: record.data.display_equipment_model_name
                }
            })
            if (records_list.length > 0) {
                self.do_action({
                    type: 'ir.actions.client',
                    name: '導出設備',
                    tag: 'export_qr_code',
                    target: 'new',
                    params: {
                        records_list: records_list
                    }
                }, {
                    size: 'medium'
                })
            } else {
                self.vue.$notify({
                    title: '警告',
                    message: '未勾選需要導出二維碼的設備',
                    type: 'warning'
                });
            }
        },

        /**
         * 設備管理搜索, 需要core.bus傳遞domains
         */
        equipment_search_apply: function () {
            var domains = []
            var self = this;
            _.each(this.propositions, function (proposition) {
                var domain = proposition.get_domain()
                if (!domain) {
                    return
                }
                // 针对时间做特别处理
                else if (proposition.field.type == 'date' || proposition.field.type == 'datetime') {
                    if (domain.length == 2) {
                        var d1 = domain[0]
                        var d2 = domain[1]

                        if (!d1[2] || d1[2] == '' || !d2[2] || d2[2] == '') {
                            return
                        } else {
                            domains.push(domain)
                        }
                        return
                    }
                }

                domain = domain[0]
                if (domain[2] == '' || domain[2] == undefined) {
                    return
                } else {
                    domains.push([domain])
                }
            })
            // 添加type搜索條件
            if (self.getParent().getParent().renderer.app.current_id && self.getParent().getParent().renderer.app.current_id !== 0) {
                domains.push([
                    ['equipment_type_id.id', '=', self.getParent().getParent().renderer.app.current_id]
                ])
            }
            self.domains = domains;
            core.bus.trigger('update_equipment_domins', {
                domains: domains
            });
            this.trigger_up('search', {
                domains: domains
            });
        },

        /**
         * 設備管理搜索欄重置，需要core.bus傳遞domains
         */
        equipment_reset_search: function () {
            this.$('input').val("")
            this.$('select[class="o_input"]').find('option').removeAttr("selected")
            this.$('select[class="o_input"]').find('option').first().attr("selected", "selected")
            _.each(this.propositions, function (proposition) {
                if (proposition.reset) {
                    proposition.reset()
                }
            })
            core.bus.trigger('update_equipment_domins', {
                domains: []
            });
            // flag中没有search_view的时候不显示搜索
            if (this.search_view) {
                this.search_view.query.reset();
            } else {
                this.commit_search();
            }
        },

        /**
         * 通用搜索欄搜索按鈕
         */
        commit_search: function () {
            var domains = []
            var self = this;
            _.each(this.propositions, function (proposition) {
                var domain = proposition.get_domain()
                if (!domain) {
                    return
                }
                // 添加計劃時間段搜索
                if (proposition.field.name === 'plan_start_time') {
                    if (domain.length == 2) {
                        var d1 = domain[0]
                        var d2 = domain[1]

                        if (!d1[2] || d1[2] == '' || !d2[2] || d2[2] == '') {
                            return
                        } else {
                            domain[1][0] = 'plan_end_time' // 第二個字段改為結束時間的範圍
                            domains.push(domain)
                        }
                        return
                    }
                }
                // 针对时间做特别处理
                else if (proposition.field.type == 'date' || proposition.field.type == 'datetime') {
                    if (domain.length == 2) {
                        var d1 = domain[0]
                        var d2 = domain[1]

                        if (!d1[2] || d1[2] == '' || !d2[2] || d2[2] == '') {
                            return
                        } else {
                            domains.push(domain)
                        }
                        return
                    }
                }

                domain = domain[0]
                if (domain[2] == '' || domain[2] == undefined) {
                    return
                } else {
                    domains.push([domain])
                }
            })
            self.domains = domains;
            this.trigger_up('search', {
                domains: domains
            });
        },
        reset_search: function () {
            var self = this;
            self._super();
            self.domains = [];
        }
    });

    widgetRegistry.add("plan_search_pannel", plan_search_pannel);

    return plan_search_pannel
});