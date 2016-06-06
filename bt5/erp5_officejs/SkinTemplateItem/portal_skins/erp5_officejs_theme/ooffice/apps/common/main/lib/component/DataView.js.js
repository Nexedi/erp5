<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44308799.11</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DataView.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\r\n
 * (c) Copyright Ascensio System SIA 2010-2015\r\n
 *\r\n
 * This program is a free software product. You can redistribute it and/or \r\n
 * modify it under the terms of the GNU Affero General Public License (AGPL) \r\n
 * version 3 as published by the Free Software Foundation. In accordance with \r\n
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect \r\n
 * that Ascensio System SIA expressly excludes the warranty of non-infringement\r\n
 * of any third-party rights.\r\n
 *\r\n
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied \r\n
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For \r\n
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html\r\n
 *\r\n
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,\r\n
 * EU, LV-1021.\r\n
 *\r\n
 * The  interactive user interfaces in modified source and object code versions\r\n
 * of the Program must display Appropriate Legal Notices, as required under \r\n
 * Section 5 of the GNU AGPL version 3.\r\n
 *\r\n
 * Pursuant to Section 7(b) of the License you must retain the original Product\r\n
 * logo when distributing the program. Pursuant to Section 7(e) we decline to\r\n
 * grant you any rights under trademark law for use of our trademarks.\r\n
 *\r\n
 * All the Product\'s GUI elements, including illustrations and icon sets, as\r\n
 * well as technical writing content are licensed under the terms of the\r\n
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License\r\n
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode\r\n
 *\r\n
 */\r\n
 if (Common === undefined) {\r\n
    var Common = {};\r\n
}\r\n
define(["common/main/lib/component/BaseView", "common/main/lib/component/Scroller"], function () {\r\n
    Common.UI.DataViewGroupModel = Backbone.Model.extend({\r\n
        defaults: function () {\r\n
            return {\r\n
                id: Common.UI.getId(),\r\n
                caption: ""\r\n
            };\r\n
        }\r\n
    });\r\n
    Common.UI.DataViewGroupStore = Backbone.Collection.extend({\r\n
        model: Common.UI.DataViewGroupModel\r\n
    });\r\n
    Common.UI.DataViewModel = Backbone.Model.extend({\r\n
        defaults: function () {\r\n
            return {\r\n
                id: Common.UI.getId(),\r\n
                selected: false,\r\n
                allowSelected: true,\r\n
                value: null\r\n
            };\r\n
        }\r\n
    });\r\n
    Common.UI.DataViewStore = Backbone.Collection.extend({\r\n
        model: Common.UI.DataViewModel\r\n
    });\r\n
    Common.UI.DataViewItem = Common.UI.BaseView.extend({\r\n
        options: {},\r\n
        template: _.template([\'<div id="<%= id %>"><%= value %></div>\'].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this;\r\n
            me.template = me.options.template || me.template;\r\n
            me.listenTo(me.model, "change", me.render);\r\n
            me.listenTo(me.model, "change:selected", me.onSelectChange);\r\n
            me.listenTo(me.model, "remove", me.remove);\r\n
        },\r\n
        render: function () {\r\n
            if (_.isUndefined(this.model.id)) {\r\n
                return this;\r\n
            }\r\n
            var el = $(this.el);\r\n
            el.html(this.template(this.model.toJSON()));\r\n
            el.toggleClass("selected", this.model.get("selected") && this.model.get("allowSelected"));\r\n
            el.off("click").on("click", _.bind(this.onClick, this));\r\n
            el.off("dblclick").on("dblclick", _.bind(this.onDblClick, this));\r\n
            if (!_.isUndefined(this.model.get("cls"))) {\r\n
                el.addClass(this.model.get("cls"));\r\n
            }\r\n
            this.trigger("change", this, this.model);\r\n
            return this;\r\n
        },\r\n
        remove: function () {\r\n
            this.stopListening(this.model);\r\n
            this.trigger("remove", this, this.model);\r\n
            Common.UI.BaseView.prototype.remove.call(this);\r\n
        },\r\n
        onClick: function (e) {\r\n
            this.trigger("click", this, this.model, e);\r\n
        },\r\n
        onDblClick: function (e) {\r\n
            this.trigger("dblclick", this, this.model, e);\r\n
        },\r\n
        onSelectChange: function (model, selected) {\r\n
            this.trigger("select", this, model, selected);\r\n
        }\r\n
    });\r\n
    Common.UI.DataView = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            multiSelect: false,\r\n
            handleSelect: true,\r\n
            enableKeyEvents: true,\r\n
            keyMoveDirection: "both",\r\n
            restoreHeight: 0,\r\n
            emptyText: "",\r\n
            listenStoreEvents: true,\r\n
            allowScrollbar: true\r\n
        },\r\n
        template: _.template([\'<div class="dataview inner" style="<%= style %>">\', "<% _.each(groups, function(group) { %>", \'<div class="grouped-data" id="<%= group.id %>">\', \'<div class="group-description">\', "<span><b><%= group.caption %></b></span>", "</div>", \'<div class="group-items-container">\', "</div>", "</div>", "<% }); %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this;\r\n
            me.template = me.options.template || me.template;\r\n
            me.store = me.options.store || new Common.UI.DataViewStore();\r\n
            me.groups = me.options.groups || null;\r\n
            me.itemTemplate = me.options.itemTemplate || null;\r\n
            me.multiSelect = me.options.multiSelect;\r\n
            me.handleSelect = me.options.handleSelect;\r\n
            me.parentMenu = me.options.parentMenu;\r\n
            me.enableKeyEvents = me.options.enableKeyEvents;\r\n
            me.style = me.options.style || "";\r\n
            me.emptyText = me.options.emptyText || "";\r\n
            me.listenStoreEvents = (me.options.listenStoreEvents !== undefined) ? me.options.listenStoreEvents : true;\r\n
            me.allowScrollbar = (me.options.allowScrollbar !== undefined) ? me.options.allowScrollbar : true;\r\n
            me.rendered = false;\r\n
            me.dataViewItems = [];\r\n
            if (me.options.keyMoveDirection == "vertical") {\r\n
                me.moveKeys = [Common.UI.Keys.UP, Common.UI.Keys.DOWN];\r\n
            } else {\r\n
                if (me.options.keyMoveDirection == "horizontal") {\r\n
                    me.moveKeys = [Common.UI.Keys.LEFT, Common.UI.Keys.RIGHT];\r\n
                } else {\r\n
                    me.moveKeys = [Common.UI.Keys.UP, Common.UI.Keys.DOWN, Common.UI.Keys.LEFT, Common.UI.Keys.RIGHT];\r\n
                }\r\n
            }\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            this.trigger("render:before", this);\r\n
            this.cmpEl = $(this.el);\r\n
            if (parentEl) {\r\n
                this.setElement(parentEl, false);\r\n
                this.cmpEl = $(this.template({\r\n
                    groups: me.groups ? me.groups.toJSON() : null,\r\n
                    style: me.style\r\n
                }));\r\n
                parentEl.html(this.cmpEl);\r\n
            } else {\r\n
                this.cmpEl.html(this.template({\r\n
                    groups: me.groups ? me.groups.toJSON() : null,\r\n
                    style: me.style\r\n
                }));\r\n
            }\r\n
            if (!this.rendered) {\r\n
                if (this.listenStoreEvents) {\r\n
                    this.listenTo(this.store, "add", this.onAddItem);\r\n
                    this.listenTo(this.store, "reset", this.onResetItems);\r\n
                }\r\n
                this.onResetItems();\r\n
                if (this.parentMenu) {\r\n
                    this.cmpEl.closest("li").css("height", "100%");\r\n
                    this.cmpEl.css("height", "100%");\r\n
                    this.parentMenu.on("show:after", _.bind(this.alignPosition, this));\r\n
                }\r\n
                if (this.enableKeyEvents && this.parentMenu && this.handleSelect) {\r\n
                    this.parentMenu.on("show:after", function () {\r\n
                        me.showLastSelected();\r\n
                        Common.NotificationCenter.trigger("dataview:focus");\r\n
                    });\r\n
                    this.parentMenu.on("hide:after", function () {\r\n
                        Common.NotificationCenter.trigger("dataview:blur");\r\n
                    });\r\n
                }\r\n
            }\r\n
            if (_.isUndefined(this.scroller) && this.allowScrollbar) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el).find(".inner").andSelf().filter(".inner"),\r\n
                    useKeyboard: this.enableKeyEvents && !this.handleSelect,\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
            var modalParents = this.cmpEl.closest(".asc-window");\r\n
            if (modalParents.length > 0) {\r\n
                this.tipZIndex = parseInt(modalParents.css("z-index")) + 10;\r\n
            }\r\n
            this.rendered = true;\r\n
            this.cmpEl.on("click", function (e) {\r\n
                if (/dataview/.test(e.target.className)) {\r\n
                    return false;\r\n
                }\r\n
            });\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        setStore: function (store) {\r\n
            if (store) {\r\n
                this.stopListening(this.store);\r\n
                this.store = store;\r\n
                if (this.listenStoreEvents) {\r\n
                    this.listenTo(this.store, "add", this.onAddItem);\r\n
                    this.listenTo(this.store, "reset", this.onResetItems);\r\n
                }\r\n
            }\r\n
        },\r\n
        selectRecord: function (record, suspendEvents) {\r\n
            if (!this.handleSelect) {\r\n
                return;\r\n
            }\r\n
            if (suspendEvents) {\r\n
                this.suspendEvents();\r\n
            }\r\n
            if (!this.multiSelect) {\r\n
                _.each(this.store.where({\r\n
                    selected: true\r\n
                }), function (rec) {\r\n
                    rec.set({\r\n
                        selected: false\r\n
                    });\r\n
                });\r\n
                if (record) {\r\n
                    record.set({\r\n
                        selected: true\r\n
                    });\r\n
                }\r\n
            } else {\r\n
                if (record) {\r\n
                    record.set({\r\n
                        selected: !record.get("selected")\r\n
                    });\r\n
                }\r\n
            }\r\n
            if (suspendEvents) {\r\n
                this.resumeEvents();\r\n
            }\r\n
        },\r\n
        selectByIndex: function (index, suspendEvents) {\r\n
            if (this.store.length > 0 && index > -1 && index < this.store.length) {\r\n
                this.selectRecord(this.store.at(index), suspendEvents);\r\n
            }\r\n
        },\r\n
        deselectAll: function (suspendEvents) {\r\n
            if (suspendEvents) {\r\n
                this.suspendEvents();\r\n
            }\r\n
            _.each(this.store.where({\r\n
                selected: true\r\n
            }), function (record) {\r\n
                record.set({\r\n
                    selected: false\r\n
                });\r\n
            });\r\n
            if (suspendEvents) {\r\n
                this.resumeEvents();\r\n
            }\r\n
        },\r\n
        getSelectedRec: function () {\r\n
            if (this.multiSelect) {\r\n
                var items = [];\r\n
                _.each(this.store.where({\r\n
                    selected: true\r\n
                }), function (rec) {\r\n
                    items.push(rec);\r\n
                });\r\n
                return items;\r\n
            }\r\n
            return this.store.where({\r\n
                selected: true\r\n
            });\r\n
        },\r\n
        onAddItem: function (record, index, opts) {\r\n
            var view = new Common.UI.DataViewItem({\r\n
                template: this.itemTemplate,\r\n
                model: record\r\n
            });\r\n
            if (view) {\r\n
                var innerEl = $(this.el).find(".inner").andSelf().filter(".inner");\r\n
                if (this.groups && this.groups.length > 0) {\r\n
                    var group = this.groups.findWhere({\r\n
                        id: record.get("group")\r\n
                    });\r\n
                    if (group) {\r\n
                        innerEl = innerEl.find("#" + group.id + " " + ".group-items-container");\r\n
                    }\r\n
                }\r\n
                if (innerEl) {\r\n
                    if (opts && opts.at == 0) {\r\n
                        innerEl.prepend(view.render().el);\r\n
                    } else {\r\n
                        innerEl.append(view.render().el);\r\n
                    }\r\n
                    innerEl.find(".empty-text").remove();\r\n
                    this.dataViewItems.push(view);\r\n
                    if (record.get("tip")) {\r\n
                        var view_el = $(view.el);\r\n
                        view_el.attr("data-toggle", "tooltip");\r\n
                        view_el.tooltip({\r\n
                            title: record.get("tip"),\r\n
                            placement: "cursor",\r\n
                            zIndex: this.tipZIndex\r\n
                        });\r\n
                    }\r\n
                    this.listenTo(view, "change", this.onChangeItem);\r\n
                    this.listenTo(view, "remove", this.onRemoveItem);\r\n
                    this.listenTo(view, "click", this.onClickItem);\r\n
                    this.listenTo(view, "dblclick", this.onDblClickItem);\r\n
                    this.listenTo(view, "select", this.onSelectItem);\r\n
                    if (!this.isSuspendEvents) {\r\n
                        this.trigger("item:add", this, view, record);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onResetItems: function () {\r\n
            $(this.el).html(this.template({\r\n
                groups: this.groups ? this.groups.toJSON() : null,\r\n
                style: this.style\r\n
            }));\r\n
            if (!_.isUndefined(this.scroller)) {\r\n
                this.scroller.destroy();\r\n
                delete this.scroller;\r\n
            }\r\n
            if (this.store.length < 1 && this.emptyText.length > 0) {\r\n
                $(this.el).find(".inner").andSelf().filter(".inner").append(\'<table class="empty-text"><tr><td>\' + this.emptyText + "</td></tr></table>");\r\n
            }\r\n
            _.each(this.dataViewItems, function (item) {\r\n
                this.stopListening(item);\r\n
                item.stopListening(item.model);\r\n
            },\r\n
            this);\r\n
            this.dataViewItems = [];\r\n
            this.store.each(this.onAddItem, this);\r\n
            if (this.allowScrollbar) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el).find(".inner").andSelf().filter(".inner"),\r\n
                    useKeyboard: this.enableKeyEvents && !this.handleSelect,\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
            this.attachKeyEvents();\r\n
        },\r\n
        onChangeItem: function (view, record) {\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("item:change", this, view, record);\r\n
            }\r\n
        },\r\n
        onRemoveItem: function (view, record) {\r\n
            this.stopListening(view);\r\n
            view.stopListening();\r\n
            if (this.store.length < 1 && this.emptyText.length > 0) {\r\n
                var el = $(this.el).find(".inner").andSelf().filter(".inner");\r\n
                if (el.find(".empty-text").length <= 0) {\r\n
                    el.append(\'<table class="empty-text"><tr><td>\' + this.emptyText + "</td></tr></table>");\r\n
                }\r\n
            }\r\n
            for (var i = 0; i < this.dataViewItems.length; i++) {\r\n
                if (_.isEqual(view, this.dataViewItems[i])) {\r\n
                    this.dataViewItems.splice(i, 1);\r\n
                    break;\r\n
                }\r\n
            }\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("item:remove", this, view, record);\r\n
            }\r\n
        },\r\n
        onClickItem: function (view, record, e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            window._event = e;\r\n
            this.selectRecord(record);\r\n
            this.lastSelectedRec = undefined;\r\n
            var tip = view.$el.data("bs.tooltip");\r\n
            if (tip) {\r\n
                tip.hide();\r\n
            }\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("item:click", this, view, record, e);\r\n
            }\r\n
        },\r\n
        onDblClickItem: function (view, record, e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            window._event = e;\r\n
            this.selectRecord(record);\r\n
            this.lastSelectedRec = undefined;\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("item:dblclick", this, view, record, e);\r\n
            }\r\n
        },\r\n
        onSelectItem: function (view, record, selected) {\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger(selected ? "item:select": "item:deselect", this, view, record);\r\n
            }\r\n
        },\r\n
        scrollToRecord: function (record) {\r\n
            var innerEl = $(this.el).find(".inner");\r\n
            var inner_top = innerEl.offset().top;\r\n
            var div = innerEl.find("#" + record.get("id"));\r\n
            var div_top = div.offset().top;\r\n
            if (div_top < inner_top || div_top + div.height() > inner_top + innerEl.height()) {\r\n
                if (this.scroller && this.allowScrollbar) {\r\n
                    this.scroller.scrollTop(innerEl.scrollTop() + div_top - inner_top, 0);\r\n
                } else {\r\n
                    innerEl.scrollTop(innerEl.scrollTop() + div_top - inner_top);\r\n
                }\r\n
            }\r\n
        },\r\n
        onKeyDown: function (e, data) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (data === undefined) {\r\n
                data = e;\r\n
            }\r\n
            if (_.indexOf(this.moveKeys, data.keyCode) > -1 || data.keyCode == Common.UI.Keys.RETURN) {\r\n
                data.preventDefault();\r\n
                data.stopPropagation();\r\n
                var rec = this.getSelectedRec()[0];\r\n
                if (this.lastSelectedRec === undefined) {\r\n
                    this.lastSelectedRec = rec;\r\n
                }\r\n
                if (data.keyCode == Common.UI.Keys.RETURN) {\r\n
                    this.lastSelectedRec = undefined;\r\n
                    this.trigger("item:click", this, this, rec, e);\r\n
                    this.trigger("item:select", this, this, rec, e);\r\n
                    this.trigger("entervalue", this, rec, e);\r\n
                } else {\r\n
                    var idx = _.indexOf(this.store.models, rec);\r\n
                    idx = (data.keyCode == Common.UI.Keys.UP || data.keyCode == Common.UI.Keys.LEFT) ? Math.max(0, idx - 1) : Math.min(this.store.length - 1, idx + 1);\r\n
                    rec = this.store.at(idx);\r\n
                    if (rec) {\r\n
                        this.selectRecord(rec);\r\n
                        this.scrollToRecord(rec);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        attachKeyEvents: function () {\r\n
            if (this.enableKeyEvents && this.handleSelect) {\r\n
                var el = $(this.el).find(".inner").andSelf().filter(".inner");\r\n
                el.addClass("canfocused");\r\n
                el.attr("tabindex", "0");\r\n
                el.on((this.parentMenu) ? "dataview:keydown": "keydown", _.bind(this.onKeyDown, this));\r\n
            }\r\n
        },\r\n
        showLastSelected: function () {\r\n
            if (this.lastSelectedRec) {\r\n
                this.selectRecord(this.lastSelectedRec, true);\r\n
                this.scrollToRecord(this.lastSelectedRec);\r\n
                this.lastSelectedRec = undefined;\r\n
            }\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            this.disabled = disabled;\r\n
            $(this.el).find(".inner").andSelf().filter(".inner").toggleClass("disabled", disabled);\r\n
        },\r\n
        isDisabled: function () {\r\n
            return this.disabled;\r\n
        },\r\n
        alignPosition: function () {\r\n
            var menuRoot = (this.parentMenu.cmpEl.attr("role") === "menu") ? this.parentMenu.cmpEl : this.parentMenu.cmpEl.find("[role=menu]"),\r\n
            innerEl = $(this.el).find(".inner").andSelf().filter(".inner"),\r\n
            docH = $(document).height(),\r\n
            menuH = menuRoot.outerHeight(),\r\n
            top = parseInt(menuRoot.css("top"));\r\n
            if (menuH > docH) {\r\n
                innerEl.css("max-height", (docH - parseInt(menuRoot.css("padding-top")) - parseInt(menuRoot.css("padding-bottom")) - 5) + "px");\r\n
                if (this.allowScrollbar) {\r\n
                    this.scroller.update({\r\n
                        minScrollbarLength: 40\r\n
                    });\r\n
                }\r\n
            } else {\r\n
                if (innerEl.height() < this.options.restoreHeight) {\r\n
                    innerEl.css("max-height", (Math.min(docH - parseInt(menuRoot.css("padding-top")) - parseInt(menuRoot.css("padding-bottom")) - 5, this.options.restoreHeight)) + "px");\r\n
                    menuH = menuRoot.outerHeight();\r\n
                    if (top + menuH > docH) {\r\n
                        menuRoot.css("top", 0);\r\n
                    }\r\n
                    if (this.allowScrollbar) {\r\n
                        this.scroller.update({\r\n
                            minScrollbarLength: 40\r\n
                        });\r\n
                    }\r\n
                }\r\n
            }\r\n
        }\r\n
    });\r\n
    $(document).on("keydown.bs.dropdown.data-api", "[data-toggle=dropdown], [role=menu]", function (e) {\r\n
        if (e.keyCode !== Common.UI.Keys.UP && e.keyCode !== Common.UI.Keys.DOWN && e.keyCode !== Common.UI.Keys.LEFT && e.keyCode !== Common.UI.Keys.RIGHT && e.keyCode !== Common.UI.Keys.RETURN) {\r\n
            return;\r\n
        }\r\n
        _.defer(function () {\r\n
            var target = $(e.target).closest(".dropdown-toggle");\r\n
            target.parent().find(".inner.canfocused").trigger("dataview:keydown", e);\r\n
        },\r\n
        100);\r\n
    });\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>22106</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
