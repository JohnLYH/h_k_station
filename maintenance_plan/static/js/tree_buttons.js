odoo.define("treebtns", function (require) {
	"use strict";

	var listRenderer = require("web.ListRenderer");
	var config = require("web.config");

	var Widget = require('web.Widget');
    var core = require('web.core');
    var QWeb = core.qweb;

	listRenderer.include({
		_renderHeaderCell: function (node) {
			var name = node.attrs.name;
			var order = this.state.orderedBy;
			var isNodeSorted = order[0] && order[0].name === name;
			var field = this.state.fields[name];
			var $th = $("<th>");
			if (!field) {
				if ((name = "treebtns")) {
					$th.text(node.attrs.string).data("name", node.attrs.string);
				}
				return $th;
			}
			var description;
			if (node.attrs.widget) {
				description = this.state.fieldsInfo.list[name].Widget.prototype
						.description;
			}
			if (description === undefined) {
				description = node.attrs.string || field.string;
			}
			if (name == "treebtns") {
				description = node.attrs.string;
			}
			$th
					.text(description)
					.data("name", name)
					.toggleClass("o-sort-down", isNodeSorted ? !order[0].asc : false)
					.toggleClass("o-sort-up", isNodeSorted ? order[0].asc : false)
					.addClass(field.sortable && "o_column_sortable");
			if (
					field.type === "float" ||
					field.type === "integer" ||
					field.type === "monetary"
			) {
				$th.css({
					textAlign: "right"
				});
			}
			if (config.debug) {
				var fieldDescr = {
					field: field,
					name: name,
					string: description || name,
					record: this.state,
					attrs: node.attrs
				};
				this._addFieldTooltip(fieldDescr, $th);
			}
			return $th;
		}
	});

	var tree_button = Widget.extend({
        events: {
            'click': '_click_tree_buttons'
        },
		template: '',
        init: function (parent, record, node) {
            this._super(parent, record, node);
            this.id = record.res_id;
            this.record = record;
        },
        start: function () {
            var $el = $(QWeb.render(this.template, {widget: this}).trim());
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
        }
    });
    return tree_button
});
