odoo.define('manage_record_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var manage_record_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;

        },
        start: function () {
            var $el = $(QWeb.render('tem_manage_record_tree_button', {widget: this}).trim());
            this.replaceElement($el);
            this.vue = new Vue({
                el: '#app',
                data() {
                    return {}
                }
            });
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            if ($(event.target).hasClass('manage_record_detail')) {
                self.do_action({
                    "name": "詳情",
                    "type": "ir.actions.client",
                    "tag": "manage_record_details",
                    "target": "new",
                    "params": {res_id: self.id}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    },
                    size: 'medium',
                })
            }
        }
    });
    widget_registry.add('manage_record_tree_button', manage_record_tree_button);
    return {manage_record_tree_button: manage_record_tree_button}

});





