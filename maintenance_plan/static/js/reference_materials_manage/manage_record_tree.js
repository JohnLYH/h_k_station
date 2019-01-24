/**
 * Created by artorias on 2018/9/28.
 */
odoo.define('manage_record_tree', function (require) {
    'use strict';

    var ListView = require("web.ListView");
    var view_registry = require("web.view_registry");
    var ListRenderer = require("web.ListRenderer");
    var ListController = require("web.ListController");

    var manage_record_render = ListRenderer.extend({
        app: undefined,
        $tree_list_box: undefined,

        init: function (parent, state, params) {
            this._super(parent, state, params);
            this.record = state
        },

        _renderView: function () {
            var $el = $('<div style="margin-bottom: 10px;font-size: 15px;"><span>設備名稱：</span>' + this.record.context.description + '<span></span>' +
                '<span style="margin-left: 30px">設備型號：</span>' + this.record.context.equipment_model + '<span></span></div>');
            if (this.$el.prev('.config_div').length > 0) {
                this.$el.prev('.config_div').remove()
            }
            this.$el.before($el);
            return this._super()
        }
    });

    var manage_record_tree = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Renderer: manage_record_render,
            Controller: ListController
        }),
        viewType: "list"
    });

    view_registry.add("manage_record_tree", manage_record_tree);
});