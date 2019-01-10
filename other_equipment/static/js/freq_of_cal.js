odoo.define('freq_of_cal_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    console.log('我進來了按鈕')
    var freq_of_cal_btn = Widget.extend({
        template: 'WidgetWebsiteButton',

        init: function (parent) {
            this._super(parent, arguments);
        },

        // 替換模板
        renderElement: function () {
            var $el = '<input name="Fruit" type="radio" value="" />苹果 </label>';
            this.replaceElement($el);
        },
    });

    widgetRegistry.add("freq_of_cal_btn", freq_of_cal_btn);

    return freq_of_cal_btn
});