/**
 * Created by artorias on 2018/12/11.
 */
odoo.define('layui_pager', function (require) {
    'use strict';

    var Widget = require('web.Widget');

    var Pager = Widget.extend({
            template: 'layui_pager',
            init: function (parent) {
                this.count = parent.state.count; // 数据总条数
                this.limit = parent.state.limit; // 数据当前页显示条数
                this.offset = parent.state.offset; // 数据查询偏移条数
                this._super(parent);
                this.id = this.getParent().state.id;
            },
            start: function () {
                var self = this;
                if (this.count !== 0) {
                    setTimeout(function () {
                        layui.use('laypage', function () {
                                var laypage = layui.laypage;
                                //执行一个laypage实例
                                laypage.render({
                                    elem: self.id + '.layui_pager', //注意，这里的 test1 是 ID，不用加 # 号
                                    count: self.count, //数据总数，从服务端得到
                                    limit: self.limit,
                                    curr: (self.offset) / self.limit + 1, // 当前页
                                    layout: ['prev', 'page', 'next', 'skip'],
                                    jump: function (obj, first) {
                                        //首次不执行
                                        if (!first) {
                                            //do something
                                            self.trigger_up('layui_pager_change', {
                                                curr: obj.curr, limit: obj.limit
                                            })
                                        }
                                    }
                                });
                            }
                        );
                    });
                }
                return $.when()
            },
        })
    ;

    return Pager
})
;