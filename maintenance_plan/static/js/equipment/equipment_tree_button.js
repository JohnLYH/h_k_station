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
                model: 'maintenance_plan.config',
                method: 'get_ref_id',
                kwargs: {
                    list_string_name: ['maintenance_plan.maintenance_plan_equipment_detail_form']
                }
            }).then(function (result) {
                self.do_action({
                    type: "ir.actions.act_window",
                    res_model: "maintenance_plan.equipment",
                    res_id: self.id,
                    views: [
                        [result[0], "form"]
                    ],
                    flags: {
                        'initial_mode': 'readonly'
                    },
                })
            })
        }
    });
    widget_registry.add('equipment_tree_button', equipment_tree_button);
    return {
        equipment_tree_button: equipment_tree_button
    }

});