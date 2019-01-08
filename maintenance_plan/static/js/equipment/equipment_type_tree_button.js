odoo.define('equipment_type_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var equipment_type_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
            console.log(record)
        },
        start: function () {
            var $el = $(QWeb.render('tem_equipment_type_tree_button', {widget: this}).trim());
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
            if ($(event.target).hasClass('maintenance_plan_detail')) {
                // TODO: 詳情
            } else {
                self.vue.$confirm('設備類別刪除后不可恢復，是否確認刪除？', '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    self._rpc({
                        model: self.record.model,
                        method: 'unlink',
                        args: [self.id],
                    }).then(function () {
                        self.vue.$message({
                            type: 'success',
                            message: '刪除成功!'
                        });
                        self.trigger_up('reload')
                    })
                });
            }
        }
    });
    widget_registry.add('equipment_type_tree_button', equipment_type_tree_button);
    return {equipment_type_tree_button: equipment_type_tree_button}

});