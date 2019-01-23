odoo.define('freq_of_cal_btn', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractField = require('web.AbstractField');
    var registry = require('web.field_registry');
    var freq_of_cal_btn = AbstractField.extend({
        init: function (parent, name, record, options) {
            this.content = record.data[name];

            this._super(parent, name, record, options)
        },

        renderElement: function () {
            var self = this;
            var $el = $(core.qweb.render('freq_of_cal_radio_btn', {widget: this}));
            self.replaceElement($el)
        },

        start: function () {
            var self = this;
            if (self.mode === 'readonly') {
                return
            } else {
                return
            }
        },

        commitChanges: function () {
            var self = this;
            var req_value = self.$el.find('input#freq_of_cal_id').val();
            var freq_of_cal_type = self.$el.find('input[name="freq_of_cal"]:checked').val();
            if (freq_of_cal_type === 'ON CONDITION') {
                self._setValue('ON CONDITION')
            } else {
                self._setValue(req_value)
            }
        },
    });
    registry.add("freq_of_cal_btn", freq_of_cal_btn);
    return freq_of_cal_btn
});