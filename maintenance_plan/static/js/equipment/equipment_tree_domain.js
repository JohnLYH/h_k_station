/**
 * Created by artorias on 2018/9/28.
 */
odoo.define('equipment_tree_domain', function (require) {
    'use strict';

    var ListView = require("web.ListView");
    var view_registry = require("web.view_registry");
    var ListRenderer = require("web.ListRenderer");
    var ListController = require("web.ListController");
    var core = require('web.core');

    var equipment_tree_domain = ListRenderer.extend({
        app: undefined,
        $tree_list_box: undefined,

        events: _.extend({}, ListRenderer.prototype.events, {
            'click #add_quipment_bt': '_add_equipment',
        }),

        init: function (parent, state, params) {
            this._super(parent, state, params);
            this.record = state
        },

        _add_equipment: function () {
            var self = this;
            self._rpc({
                model: 'maintenance_plan.config',
                method: 'get_ref_id',
                kwargs: {list_string_name: ['maintenance_plan.maintenance_plan_equipment_form']}
            }).then(function (result) {
                self.do_action({
                    type: "ir.actions.act_window",
                    res_model: "maintenance_plan.equipment",
                    views: [[result[0], "form"]],
                    target: "new",
                    context: {
                        "default_equipment_type_id": self.app.current_id
                    },
                }, {
                    on_close: function () {
                        self.trigger_up('reload')
                    }
                })
            })
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
                    '<div class="col-lg-3 col-md-4 col-md-sm-12 col-md-xs-12" style="padding: 0px 5px 5px 0px; min-height: 100%; overflow-x: hidden" id="equipment_tree_box"></div>' +
                    '<div class="col-lg-9 col-md-8 col-md-sm-12 col-md-xs-12" style="padding: 0px; min-height: 100%"><div>' +
                    '<div style="margin-bottom: 20px">' +
                    '<span id="type_route">信號系統</span><button id="add_quipment_bt" style="float: right" class="btn btn-primary btn-sm">添加</button>' +
                    '</div></div><div id="list_box"></div></div>' +
                    '</div>').appendTo(self.$el);
                self.$tree_list_box = self.$("#list_box");
                self.$tree_box = self.$("#equipment_tree_box");

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
                        el: "#equipment_tree_box",
                        data() {
                            return {
                                defaultProps: {
                                    children: "sub",
                                    label: "name",
                                    id: "id",
                                    isLeaf: 'leaf'
                                },
                                current_id: null,
                                resolve: null
                            };
                        },
                        methods: {
                            handleNodeClick(data) {
                                var domains;
                                if (data.id == 0) {
                                    domains = []
                                }
                                else {
                                    domains = [[["equipment_type_id.id", "=", data.id]]]
                                }
                                var this_vue = this;
                                self.trigger_up("search", {
                                    domains: domains,
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
                                var id;
                                if (node.level === 0) {
                                    id = false;
                                    this.resolve = resolve
                                } else {
                                    id = (node.data && node.data.id) || 0
                                }
                                self._rpc({
                                    model: 'maintenance_plan.equipment.type',
                                    method: 'get_type_tree',
                                    kwargs: {type_id: id}
                                }).then(function (data) {
                                    return resolve(data);
                                });
                            },

                            add_equipment(event, node) {
                                var this_vue = this;
                                event.stopPropagation();
                                self.do_action({
                                    type: "ir.actions.act_window",
                                    res_model: "maintenance_plan.equipment.type",
                                    views: [[false, "form"]],
                                    target: "new",
                                    context: {
                                        "default_parent_id": node.data.id,
                                        "node": node.data.id
                                    },
                                })
                            },
                            del_equipment(event, node) {
                                var this_vue = this;
                                event.stopPropagation();
                                this_vue.$confirm('設備類型刪除后不可修改，是否確認刪除？', '提示', {
                                    confirmButtonText: '确定',
                                    cancelButtonText: '取消',
                                    type: 'warning'
                                }).then(() => {
                                    self._rpc({
                                        model: 'maintenance_plan.equipment.type',
                                        method: 'unlink',
                                        args: [node.data.id]
                                    }).then(function () {
                                        this_vue.$message({
                                            type: 'success',
                                            message: '刪除成功!'
                                        });
                                        // 刪除節點并恢復到頂層節點
                                        this_vue.$refs.tree.remove(node);
                                        this_vue.$refs.tree.setCurrentKey(0);
                                        self.$('#type_route').html(this_vue.$refs.tree.getCurrentNode().name);
                                        self.getParent().reload({domain: []})
                                    })
                                });
                            }
                        }
                    });
                    core.bus.on('update_type_tree', self, function (data) {
                        var this_vue = self.app;
                        var parent_node = this_vue.$refs.tree.getNode(data.node_id);
                        // 父節點下添加子節點并設置父節點為isLeaf = false狀態
                        this_vue.$refs.tree.append(data, parent_node);
                        parent_node.isLeaf = false;
                        // 重新定位到頂節點為點擊狀態
                        this_vue.$refs.tree.setCurrentKey(0);
                        self.$('#type_route').html(this_vue.$refs.tree.getCurrentNode().name);
                        self.getParent().reload({domain: []})
                    })
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