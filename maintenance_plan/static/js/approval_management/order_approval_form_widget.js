/**
 * Created by artorias on 2019/1/8.
 */
odoo.define('order_approval_form_widget', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var order_approval_form_widget = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.vue_data = {
                activeName: ''
            }
        },
        willStart: function () {
            return $.when()
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'order_approval_form_widget'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#app',
                    data(){
                        return self.vue_data
                    }
                })
            })
        }
    });
    widget_registry.add('order_approval_form_widget', order_approval_form_widget);
    return {order_approval_form_widget: order_approval_form_widget}

});