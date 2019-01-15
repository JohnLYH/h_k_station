odoo.define('work_order_tree_button', function (require) {
    "use strict";

    var widget_registry = require('web.widget_registry');
    var tree_button = require('treebtns');
    var data_manager = require('web.data_manager');

    var work_order_tree_button = tree_button.extend({
        template: 'tem_work_order_tree_button',
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            data_manager.load_action('maintenance_plan.act_order_approval').then(function (result) {
                self.do_action(result, {
                    res_id: self.id,
                    view_type: 'form',
                })
            })
        }
    });
    widget_registry.add('work_order_tree_button', work_order_tree_button);
    return {work_order_tree_button: work_order_tree_button}

});