odoo.define('equipment_type_tree_button', function (require) {
    "use strict";

    var widget_registry = require('web.widget_registry');
    var tree_button = require('treebtns');

    var equipment_type_tree_button = tree_button.extend({
        template: 'tem_equipment_type_tree_button',
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