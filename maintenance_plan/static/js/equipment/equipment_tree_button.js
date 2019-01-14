odoo.define('equipment_tree_button', function (require) {
    "use strict";

    var widget_registry = require('web.widget_registry');
    var tree_button = require('treebtns');
    var data_manager = require('web.data_manager');

    var equipment_tree_button = tree_button.extend({
        template: 'tem_equipment_tree_button',
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            data_manager.load_action('maintenance_plan.act_equipment_management').then(function (result) {
                self.do_action(result, {
                    res_id: self.id,
                    view_type: 'form',
                    replace_last_action: true
                })
            })
        }
    });
    widget_registry.add('equipment_tree_button', equipment_tree_button);
    return {equipment_tree_button: equipment_tree_button}

});