odoo.define('materials_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var materials_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_materials_manage_tree_button', {widget: this}).trim());
            this.replaceElement($el);
            this.vue = new Vue({
                el: '#app',
                data() {
                    return {}
                }
            });
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            if ($(event.target).hasClass('materials_manage_detail')) {
                self.do_action({
                    "name": "參考資料詳情",
                    "type": "ir.actions.client",
                    "tag": "materials_detail_btn",
                    "params": {record: self.record, id: self.id}
                })
            } else {
                self.do_action({
                    "name": "上傳文件",
                    "type": "ir.actions.client",
                    "tag": "materials_upload_btn",
                    "target": "new",
                    "params": {record: self.record, id: self.id}
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    },
                    size: 'medium',
                })
            }
        }
    });
    widget_registry.add('materials_tree_button', materials_tree_button);
    return {materials_tree_button: materials_tree_button}

});
