odoo.define('maintenance_plan_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var maintenance_plan_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_maintenance_plan_tree_button', {widget: this}).trim());
            this.replaceElement($el)
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            if ($(event.target).hasClass('maintenance_plan_edit')) {
                self.do_action({
                    "name": "编辑工单",
                    "type": "ir.actions.client",
                    "tag": "maintenance_plan_edit",
                    "target": "new",
                    "params": {record: self.record}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    }
                })
            } else {
                self._rpc({
                    model: self.record.model,
                    method: 'get_ref_id',
                    args: ['maintenance_plan.act_order_approval']
                }).then(function (act_id) {
                    self.do_action(act_id, {
                        res_id: self.id,
                        view_type: 'form',
                    })
                })
            }
        }
    });
    widget_registry.add('maintenance_plan_tree_button', maintenance_plan_tree_button);
    return {maintenance_plan_tree_button: maintenance_plan_tree_button}

});