odoo.define('equipment_tree_button', function (require) {
    "use strict";

    var widget_registry = require('web.widget_registry');
    var tree_button = require('treebtns');

    var equipment_tree_button = tree_button.extend({
        template: 'tem_equipment_tree_button',
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            self._rpc({
                model: 'maintenance_plan.maintenance.plan',
                method: 'get_ref_id',
                args: ['maintenance_plan.act_equipment_management']
            }).then(function (act_id) {
                self.do_action(act_id, {
                    res_id: self.id,
                    view_type: 'form',
                })
            })
        }
    });
    widget_registry.add('equipment_tree_button', equipment_tree_button);
    return {equipment_tree_button: equipment_tree_button}

});