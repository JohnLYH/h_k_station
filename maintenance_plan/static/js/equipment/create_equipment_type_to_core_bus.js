odoo.define('create_equipment_type_to_core_bus', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');

    var create_equipment_type_to_core_bus = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.record = record;
            this.node_id = parent.state.context.node;
        },
        events: _.extend({}, Widget.prototype.events, {
            'click': '_create_type',
        }),
        _create_type: function () {
            var self = this;
            var contoller = this.getParent().getParent();
            contoller.saveRecord().then(function () {
                var record = contoller.model.get(self.record.id);
                self.do_action(false);
                core.bus.trigger('update_type_tree', {
                    id: record.res_id,
                    name: record.data.name,
                    leaf: true,
                    node_id: self.node_id
                });
            })
        },
        renderElement: function () {
            this.replaceElement($('<button class="btn btn-sm btn-primary"><span>保存</span></button>'))
        },
    });
    widget_registry.add('create_equipment_type_to_core_bus', create_equipment_type_to_core_bus);
    return {
        create_equipment_type_to_core_bus: create_equipment_type_to_core_bus
    }

});