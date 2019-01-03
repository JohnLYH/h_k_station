odoo.define('work_order_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var work_order_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_work_order_tree_button', {widget: this}).trim());
            this.replaceElement($el)
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
        }
    });
    widget_registry.add('work_order_tree_button', work_order_tree_button);
    return {work_order_tree_button: work_order_tree_button}

});