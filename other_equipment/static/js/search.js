odoo.define("tool_search", function (require) {
    "use strict";

    // 自定义控制面版，添加js进行更加灵活的控制

    var core = require('web.core');
    var widgetRegistry = require('web.widget_registry');
    var search_pannel_default = require('layui_theme.search_pannel_default');

    var tool_search = search_pannel_default.extend({
        events: _.extend({}, search_pannel_default.prototype.events, {
            'click .search_export': 'search_export',
            'click .search_import': 'search_import',
        }),

        start: function() {
            this._super.apply(this, arguments);
            // this.collapse_search()
            this.vue = new Vue({
                el: '#app',
                data() {
                    return {}
                }
            });
        },
        uploadExcel: function (dom) {
            var file = dom.files[0];
            var self = this;
            // new一个FormData实例
            var formData = new FormData();
            formData.append('file', file);
            $.ajax({
                url: '/other_equipment/put_in_excel/',
                type: 'POST',
                data: formData,
                processData: false,  //tell jQuery not to process the data
                contentType: false,  //tell jQuery not to set contentType
                //这儿的三个参数其实就是XMLHttpRequest里面带的信息。
                success: function (response) {
                    response = JSON.parse(response);
                    if (response.error === false) {
                        self.vue.$notify({
                            title: '成功',
                            message: '上傳成功',
                            type: 'success'
                        });
                    } else if (response.error === true && response.file_id) {
                        self.vue.$notify({
                            title: '警告',
                            message: response.message,
                            type: 'warning'
                        });
                        self.do_action({
                            name: '返回錯誤文件',
                            target: 'new',
                            type: 'ir.actions.act_url',
                            url: '/other_equipment/down_wrong_file?file_id=' + response.file_id
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
        

        search_export: function() {
            var self = this;
            var domains = []
            _.each(this.propositions, function (proposition) {
                var domain = proposition.get_domain()
                if (!domain) {
                    return
                }
                // 针对时间做特别处理
                if (proposition.field.type == 'date' || proposition.field.type == 'datetime') {
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
            });
            var formData = new FormData();
            formData.append('domains', domains);
            $.ajax({
                url: '/other_equipment/get_in_excel/',
                type: 'POST',
                data: formData,
                processData: false,  //tell jQuery not to process the data
                contentType: false,  //tell jQuery not to set contentType
                //这儿的三个参数其实就是XMLHttpRequest里面带的信息。
                success: function (response) {
                    response = JSON.parse(response);
                    console.log(response)
                    if (response.error === 0) {
                        // self.vue.$notify({
                        //     title: '成功',
                        //     message: '導出成功',
                        //     type: 'success'
                        // });
                        self.do_action({
                            name: '返回錯誤文件',
                            target: 'new',
                            type: 'ir.actions.act_url',
                            url: '/other_equipment/down_wrong_file?file_id=' + response.file_id
                        })
                    }
                    else {
                        // self.vue.$notify({
                        //     title: '錯誤',
                        //     message: response.message,
                        //     type: 'error'
                        // });
                    }
                }
            })
        },

        search_import: function() {
            var self = this;
            var target = this.$el.find('[name="file"]');
            target.change(function () {
                if ($(this).val()) {
                    var fileName = $(this).val().substring($(this).val().lastIndexOf(".") + 1).toLowerCase();
                    if (fileName != "xlsx") {
                        self.vue.$notify({
                            title: '錯誤',
                            message: '请选择xls格式文件上传！',
                            type: 'error'
                        });
                        $(this).val("");
                        return
                    }
                    // $(this).parent().submit();
                    self.uploadExcel(this);
                    $(this).val("");
                }
            });
            target.trigger('click');
        }
    });

    widgetRegistry.add("tool_search", tool_search);

    return tool_search
});