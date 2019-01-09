/**
 * Created by artorias on 2018/9/28.
 */
odoo.define('equipment_tree_domain', function (require) {
    'use strict';

    var ListView = require("web.ListView");
    var view_registry = require("web.view_registry");
    var ListRenderer = require("web.ListRenderer");
    var ListController = require("web.ListController");

    var equipment_tree_domain = ListRenderer.extend({
        app: undefined,
        $tree_list_box: undefined,

        events: _.extend({}, ListRenderer.prototype.events, {
            'click #add_quipment_type_bt': '_add_quipment_type',
        }),

        init: function (parent, state, params) {
            this._super(parent, state, params);
            this.record = state
        },

        _add_quipment_type: function(){

        },

        _renderNoContentHelper: function () {
            var $msg = $('<div>').addClass('oe_view_nocontent').html(this.noContentHelp);
            this.$tree_list_box.html($msg);
        },

        _renderView: function () {
            var self = this;
            if (self.app) {
                this.$tree_list_box
                    .removeClass('table-responsive')
                    .empty();

                // destroy the previously instantiated pagers, if any
                _.invoke(this.pagers, 'destroy');
                this.pagers = [];

                // display the no content helper if there is no data to display
                if (!this._hasContent() && this.noContentHelp) {
                    this._renderNoContentHelper();
                    return this._super();
                }

                var $table = $('<table>').addClass('o_list_view table table-condensed table-striped');
                this.$tree_list_box
                    .addClass('table-responsive')
                    .append($table);
                var is_grouped = !!this.state.groupedBy.length;
                this._computeAggregates();
                $table.toggleClass('o_list_view_grouped', is_grouped);
                $table.toggleClass('o_list_view_ungrouped', !is_grouped);
                if (is_grouped) {
                    $table
                        .append(this._renderHeader(true))
                        .append(this._renderGroups(this.state.data))
                        .append(this._renderFooter(true));
                } else {
                    $table
                        .append(this._renderHeader())
                        .append(this._renderBody())
                        .append(this._renderFooter());
                }
                if (this.selection.length) {
                    var $checked_rows = this.$('tr').filter(function (index, el) {
                        return _.contains(self.selection, $(el).data('id'));
                    });
                    $checked_rows.find('.o_list_record_selector input').prop('checked', true);
                }
            } else {
                self.$el
                    .removeClass('table-responsive')
                    .empty();
                $('<div class="container-fluid" style="padding: 0px">' +
                    '<div class="col-lg-2 col-md-4 col-md-sm-12 col-md-xs-12" style="padding: 0px 5px 5px 0px; min-height: 100%; overflow-x: hidden" id="tree_box"></div>' +
                    '<div class="col-lg-10 col-md-8 col-md-sm-12 col-md-xs-12" style="padding: 0px; min-height: 100%"><div>' +
                    '<div style="margin-bottom: 20px">' +
                    '<span id="type_route">&nbsp;</span><button id="add_quipment_type_bt" style="float: right" class="btn btn-primary btn-sm">添加</button>' +
                    '</div></div><div id="list_box"></div></div>' +
                    '</div>').appendTo(self.$el);
                self.$tree_list_box = self.$("#list_box");
                self.$tree_box = self.$("#tree_box");

                self._rpc({
                    model: 'vue_template_manager.template_manage',
                    method: 'get_template_content',
                    kwargs: {
                        module_name: 'maintenance_plan',
                        template_name: 'equipment_tree_domain'
                    }
                }).then(function (el) {
                    $(el).appendTo(self.$tree_box);
                    self.app = new Vue({
                        el: "#tree_box",
                        data() {
                            return {
                                defaultProps: {
                                    children: "sub",
                                    label: "name",
                                    id: "id",
                                    isLeaf: 'leaf'
                                },
                                current_id: null
                            };
                        },
                        methods: {
                            handleNodeClick(data) {
                                var this_vue = this;
                                self.trigger_up("search", {
                                    domains: [[["equipment_type_id.id", "=", data.id]]],
                                    contexts: [],
                                    groupbys: []
                                });
                                self._rpc({
                                    model: 'maintenance_plan.equipment.type',
                                    method: 'get_type_route',
                                    kwargs: {type_id: data.id}
                                }).then(function (route) {
                                    self.$('#type_route').html(route);
                                    this_vue.current_id = data.id;
                                })
                            },

                            loadNode(node, resolve) {
                                var id = (node.data && node.data.id) || null;
                                self._rpc({
                                    model: 'maintenance_plan.equipment.type',
                                    method: 'get_type_tree',
                                    kwargs: {type_id: id}
                                }).then(function (data) {
                                    return resolve(data);
                                });
                            },

                            add_equipment(event, node) {

                            },
                            del_equipment(event, node) {

                            }
                        }
                    });
                });

                _.invoke(this.pagers, 'destroy');
                this.pagers = [];

                // display the no content helper if there is no data to display
                if (!this._hasContent() && this.noContentHelp) {
                    this._renderNoContentHelper();
                    return this._super();
                }

                var $table = $('<table>').addClass('o_list_view table table-condensed table-striped');
                self.$tree_list_box
                    .addClass('table-responsive')
                    .append($table);
                var is_grouped = !!this.state.groupedBy.length;
                this._computeAggregates();
                $table.toggleClass('o_list_view_grouped', is_grouped);
                $table.toggleClass('o_list_view_ungrouped', !is_grouped);
                if (is_grouped) {
                    $table
                        .append(this._renderHeader(true))
                        .append(this._renderGroups(this.state.data))
                        .append(this._renderFooter(true));
                } else {
                    $table
                        .append(this._renderHeader())
                        .append(this._renderBody())
                        .append(this._renderFooter());
                }
                if (this.selection.length) {
                    var $checked_rows = this.$('tr').filter(function (index, el) {
                        return _.contains(self.selection, $(el).data('id'));
                    });
                    $checked_rows.find('.o_list_record_selector input').prop('checked', true);
                }
            }
            return $.when();
        },
    });
    var equipment_tree_domain = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: equipment_tree_domain,
            Controller: ListController
        }),
        viewType: "list"
    });

    view_registry.add("equipment_tree_domain", equipment_tree_domain);
});