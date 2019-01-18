/**
 * Created by artorias on 2019/1/17.
 */
odoo.define('qr_code_to_image', function (require) {
    "use strict";

    var registry = require('web.field_registry');
    var basic_fields = require('web.basic_fields');
    var core = require('web.core');

    var qr_code_to_image = basic_fields.FieldText.extend({
        template: 'tem_qr_code_to_image',
        events: {
            'click button': '_click_buttons'
        },
        _click_buttons: function (event) {
            event.stopPropagation();

            var iframe = document.getElementById("print-iframe");
            if (!iframe) {
                var el = document.getElementById("print_content");
                iframe = document.createElement('IFRAME');
                var doc;
                iframe.setAttribute("id", "print-iframe");
                document.body.appendChild(iframe);
                doc = iframe.contentWindow.document;
                //这里可以自定义样式
                doc.write('<div style="width: 500px;">' + el.innerHTML + '</div>');
                doc.close();
                iframe.contentWindow.focus();
            }
            iframe.contentWindow.print();
            document.body.removeChild(iframe);
        },
        start: function () {
            var $el = $(core.qweb.render(this.template, {widget: this}).trim());
            this.replaceElement($el);
        }
    });
    registry.add('qr_code_to_image', qr_code_to_image);
    return {qr_code_to_image: qr_code_to_image}

});