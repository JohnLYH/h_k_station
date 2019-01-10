odoo.define('work_order_tree_button', function (require) {
    "use strict";

    var widget_registry = require('web.widget_registry');
    var tree_button = require('treebtns');

    var work_order_tree_button = tree_button.extend({
        template: 'tem_work_order_tree_button',
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
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
    });
    widget_registry.add('work_order_tree_button', work_order_tree_button);
    return {work_order_tree_button: work_order_tree_button}

});