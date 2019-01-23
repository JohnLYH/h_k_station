odoo.define("cascader_widget", function (require) {
    "use strict";

    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');

    var cascader_widget = AbstractField.extend({

        init: function () {
            this._super.apply(this, arguments);

        },

        start: function (parent, action) {
            if (this.mode === 'edit') {
                var self = this;
                self._rpc({
                    model: 'html_model.template_manage',
                    method: 'get_template_content',
                    kwargs: {module_name: 'user', template_name: 'caseder_class'},
                }).then(function (vals) {
                    setTimeout(function () {
                        self.$el.append(vals)
                        new Vue({
                            el: '#cascader_widget',
                            data: function () {
                                return {
                                    options: [],
                                    sel_value: []
                                };
                            },

                            mounted: function () {
                                var now_vue = this;
                                self._rpc({
                                    model: 'user.department',
                                    method: 'get_equipment_class',
                                    args: [],
                                }).then(function (vals) {
                                    now_vue.example(vals)
                                })
                            },

                            methods: {
                                example: function (vals) {
                                    this.options = vals
                                },
                                handleChange(value) {
                                    self._setValue(value[value.length - 1])
                                }
                            }
                        })

                    })

                })
            }


        }

    });

    registry.add('cascader_widget', cascader_widget);

    return {
        cascader_widget: cascader_widget
    }
});
