odoo.define("plan_search_pannel", function (require) {
    "use strict";

    // 自定义控制面版，添加js进行更加灵活的控制

    var widgetRegistry = require('web.widget_registry');
    var search_pannel_default = require('layui_theme.search_pannel_default');

    var plan_search_pannel = search_pannel_default.extend({
        events: _.extend({}, search_pannel_default.prototype.events, {
            'click .export_excel': 'export_excel',
            'click .put_in_excel': 'put_in_excel',
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
        put_in_excel: function (event) {
            var self = this;
            var target = this.$el.find('[name="file"]');
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
                    self.uploadExcel(this);
                    $(this).val("");
                }
            });
            target.trigger('click');
        },

        uploadExcel: function (dom) {
            var file = dom.files[0];
            var self = this;
            // new一个FormData实例
            var formData = new FormData();
            formData.append('file', file);
            $.ajax({
                url: '/maintenance_plan/put_in_excel/',
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
                },
                success: function (response) {
                    self.loading.close();
                    response = JSON.parse(response);
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
                }
            })
        },

        export_excel: function (event) {
            // TODO: 導出excel
            var self = this;
            var limit = self.getParent().getParent().pager.state.limit;
            var offset = self.getParent().getParent().pager.state.current_min;
            var oReq = new XMLHttpRequest();
            oReq.open("POST", '/maintenance_plan/export_work_order', true);
            oReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            //指定返回类型
            oReq.responseType = "arraybuffer";
            oReq.onload = function (oEvent) {

                if (oReq.readyState == 4 && oReq.status == 200) {
                    console.log(oReq.getResponseHeader("File-name"))
                    var blob = new Blob([oReq.response], {
                        type: "application/vnd.ms-excel"
                    });

                    // 转换Blob完成，创建一个a标签用于下载
                    var a = document.createElement('a');
                    //点击事件
                    var evt = document.createEvent("HTMLEvents");
                    evt.initEvent("click", false, false);
                    // 设置文件名
                    a.download = '导出工单.xlsx';
                    // 利用URL.createObjectURL()方法为a元素生成blob URL
                    a.href = URL.createObjectURL(blob);
                    a.click();
                }
            };
            // 发送待参数的请求
            oReq.send("domain=" + JSON.stringify(self.domains) + "&limit=" + limit + "&offset=" + offset);
        },
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