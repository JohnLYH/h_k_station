odoo.define("plan_search_pannel", function (require) {
    "use strict";

    // 自定义控制面版，添加js进行更加灵活的控制

    var core = require('web.core');
    var widgetRegistry = require('web.widget_registry');
    var search_pannel_default = require('layui_theme.search_pannel_default');

    var plan_search_pannel = search_pannel_default.extend({
        events: _.extend({}, search_pannel_default.prototype.events, {
            'click .export_excel': 'export_excel',
        }),
        export_excel: function(event){
            // TODO: 導出excel
            console.log(event)
        },
        commit_search: function () {
            var domains = []
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
            this.trigger_up('search', {
                domains: domains
            });
        }
    });

    widgetRegistry.add("plan_search_pannel", plan_search_pannel);

    return plan_search_pannel
});