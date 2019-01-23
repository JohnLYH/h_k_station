/**
 * Created by artorias on 2019/1/23.
 */
odoo.define('equipment_notebook', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');

    var equipment_notebook = Widget.extend({
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.record = record;
            this.vue_data = {
                activeName: 'record',
                migrate_data: [],
                record_data: []
            }
        },
        willStart: function () {
            var self = this;
            var serial_number_id = self.record.data.serial_number_id.res_id;
            var get_migrate_data = self._rpc({
                model: 'maintenance_plan.migrate.records',
                method: 'search_read',
                domain: [
                    ['serial_number_id', '=', serial_number_id]
                ],
                fields: ['info', 'remark', 'executor_user_id', 'create_date']
            })
            var get_record_data = self._rpc({
                model: 'maintenance_plan.maintenance.plan',
                method: 'search_read',
                domain: [
                    ['equipment_id', '=', self.record.res_id],
                    ['status', '=', 'closed']
                ],
                fields: [
                    'num', 'equipment_serial_number', 'action_dep_id', 'executor_id', 'actual_start_time',
                    'actual_end_time'
                ]
            })
            return $.when(get_migrate_data, get_record_data).then(function (migrate_data, record_data) {
                self.vue_data.migrate_data = migrate_data;
                self.vue_data.record_data = record_data;
            })
        },
        start: function () {
            var self = this;
            self._rpc({
                model: 'vue_template_manager.template_manage',
                method: 'get_template_content',
                kwargs: {
                    module_name: 'maintenance_plan',
                    template_name: 'equipment_notebook'
                }
            }).then(function (el) {
                self.replaceElement($(el));
                new Vue({
                    el: '#app',
                    data() {
                        return self.vue_data
                    },
                    computed: {
                        add_create_date: function () {
                            return function (create_date) {
                                return moment(create_date).add(8, 'h').format("YYYY/MM/DD HH:mm:ss")
                            }
                        },
                        format_datetime: function () {
                            return function (datetime) {
                                return datetime.replace(/-/g, "/")
                            }
                        }
                    },
                })
            })
        }
    });
    widget_registry.add('equipment_notebook', equipment_notebook);
    return {
        equipment_notebook: equipment_notebook
    }

});