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
            this.collapse_search()
        },

        search_export: function() {
            alert('導出')
        },

        search_import: function() {
            alert('導入')
        }
    });

    widgetRegistry.add("tool_search", tool_search);

    return tool_search
});