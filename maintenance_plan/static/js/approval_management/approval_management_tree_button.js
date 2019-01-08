odoo.define('approval_management_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var approval_management_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_maintenance_plan_approval_tree_button', {widget: this}).trim());
            this.replaceElement($el)
        },
        _click_tree_buttons: function (event) {
            console.log('我愛你');
            var self = this;
            console.log(self);
            event.stopPropagation();
        }
    });
    widget_registry.add('approval_management_tree_button', approval_management_tree_button);
    return {approval_management_tree_button: approval_management_tree_button}

});

odoo.define('maintenance_plan_approval_management', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var maintenance_plan_approval_management = Widget.extend({
        init: function (parent, model) {
            var self = this;
            self.vue_data = {
                cols: [],
                tableData: [],
                leader_duty_type: 'off',
                name: '',
                month: moment().format("YYYY-MM"),

                is_checked_all: false,
                chioce_able: false,
                checkAll: false,
                choice_month: null,
                choice_checkbox: [],
                checked_duty_crop: [], // 选中的id
                value1: '',
                value2: ''
            };
            self._super(parent);
        },
        start: function () {
            var self = this;
            setTimeout(function () {
                // 获取vue模板
                self._rpc({
                    model: 'vue_template_manager.template_manage',
                    method: 'get_template_content',
                    kwargs: {
                        module_name: 'maintenance_plan',
                        template_name: 'approval_management'
                    }
                }).then(function (el) {
                    // 加载vue模板
                    self.replaceElement($(el));
                    new Vue({
                        el: '#approval_management',
                        mounted() {
                        },
                        data() {
                            return self.vue_data
                        },
                        methods: {
                        }
                    })
                })
            }, 100)
        }

    });
    core.action_registry.add('maintenance_plan_approval_management', maintenance_plan_approval_management);
    return {
        maintenance_plan_approval_management: maintenance_plan_approval_management
    };
});

odoo.define('data_approval_management_tree_button', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var core = require('web.core');
    var QWeb = core.qweb;

    var data_approval_management_tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render('tem_maintenance_plan_data_approval_tree_button', {widget: this}).trim());
            this.replaceElement($el)
        },
        _click_tree_buttons: function (event) {
            console.log('我愛你');
            var self = this;
            console.log(self);
            event.stopPropagation();
        }
    });
    widget_registry.add('data_approval_management_tree_button', data_approval_management_tree_button);
    return {data_approval_management_tree_button: data_approval_management_tree_button}

});
