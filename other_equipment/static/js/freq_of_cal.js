odoo.define('freq_of_cal_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');

    var freq_of_cal_btn = Widget.extend({
        propositions: [],
        events: {
            'click .search_extend_reset': 'reset_search',
            'click .search_extend_apply': 'commit_search',
            'click .search_extend_export': 'export_search',
            'keyup .o_searchview_extended_prop_value': function (ev) {
                if (ev.which === $.ui.keyCode.ENTER) {
                    this.commit_search();
                }
            },
        },

        init: function (parent, fields, pannel_template, search_view) {
            this.fields = fields;
            this.pannel_template = pannel_template;
            this.search_view = search_view
            this._super(parent, arguments);
        },

        // 读取模板，同时读取属性并构造搜索对象
        renderElement: function () {
            var $el;
            var bHaveExt = false
            if (this.pannel_template) {
                this.propositions = [];
                $el = $(core.qweb.render(this.pannel_template, {
                    widget: this
                }).trim());
                var fields_place_holders = $el.find("[for]")
                for (var i = 0; i < fields_place_holders.length; i++) {
                    var holder = fields_place_holders[i]
                    var filed_name = $(holder).attr('for')
                    var option = $(holder).attr('option') || '{"range": true}'
                    option = pyeval.py_eval(option)
                    var field = this.fields[filed_name]
                    if (field) {
                        var prop = new layui_search_proposition(this, field, option);
                        prop.appendTo(holder)
                        this.propositions.push(prop);
                        bHaveExt = true
                    }
                }
            } else {
                $el = this._make_descriptive();
            }

            this.replaceElement($el);
            if (bHaveExt) {
                this.do_show();
            } else {
                this.do_hide();
            }
        },

    });

    widgetRegistry.add("freq_of_cal_btn", freq_of_cal_btn);

    return freq_of_cal_btn
});