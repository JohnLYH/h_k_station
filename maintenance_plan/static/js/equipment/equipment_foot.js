/**
 * Created by artorias on 2019/1/17.
 */
odoo.define('equipment_foot', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var equipment_foot = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.vue_data = {
                activeName: 'record'
            }
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'equipment_foot'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#app',
                    data() {
                        return self.vue_data
                    }
                })
            })
        }
    });
    widget_registry.add('equipment_foot', equipment_foot);
    return {
        equipment_foot: equipment_foot
    }

});