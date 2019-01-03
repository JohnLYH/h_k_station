odoo.define('maintenance_plan_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var maintenance_plan_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
            console.log(this)
        },
        start: function () {
            var $el = $(QWeb.render('tem_maintenance_plan_tree_button', {widget: this}).trim());
            this.replaceElement($el)
        },
        _click_tree_buttons: function (event) {
            var self = this;
            event.stopPropagation();
            var record_id = $(event.target).attr('record-id');
            if ($(event.target).hasClass('maintenance_plan_edit')) {
                var el = QWeb.render('tem_maintenance_plan_tree_edit', {widget: self}).trim();
                layui.layer.open({
                    type: 1,
                    content: el,
                    title: ['編輯工單', 'text-align: center;padding: 0px'],
                    area: '500px',
                    resize: false,
                    fixed: false,
                    move: false,
                    closeBtn: 0,
                    btn: ['確認', '取消'],
                    btnAlign: 'c',
                    yes: function (index, layero) {
                        layui.layer.confirm('工單指派后不能修改，是否確認指派？', function (index) {
                            //do something
                            console.log('enter')
                            layui.layer.closeAll()
                        });
                    }
                });
                layui.use(['laydate', 'form'], function () {
                    var laydate = layui.laydate;
                    var form = layui.form;
                    //执行一个laydate实例
                    laydate.render({
                        elem: '#action_time', //指定元素
                        min: '2017-1-1', // 最大執行日期
                        max: '2017-12-31'
                    });
                    form.render(null, 'plan_tree_form');
                });
            }
        }
    });
    widget_registry.add('maintenance_plan_tree_button', maintenance_plan_tree_button);
    return {maintenance_plan_tree_button: maintenance_plan_tree_button}

});