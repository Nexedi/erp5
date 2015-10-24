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
            <value> <string>ts44308799.0</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ComboDataView.js</string> </value>
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
define(["common/main/lib/component/BaseView", "common/main/lib/component/DataView"], function () {\r\n
    Common.UI.ComboDataView = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            id: null,\r\n
            cls: "",\r\n
            style: "",\r\n
            hint: false,\r\n
            itemWidth: 80,\r\n
            itemHeight: 40,\r\n
            menuMaxHeight: 300,\r\n
            enableKeyEvents: false,\r\n
            beforeOpenHandler: null\r\n
        },\r\n
        template: _.template([\'<div id="<%= id %>" class="combo-dataview <%= cls %>" style="<%= style %>">\', \'<div class="view"></div> \', \'<div class="button"></div> \', "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            this.id = this.options.id || Common.UI.getId();\r\n
            this.cls = this.options.cls;\r\n
            this.style = this.options.style;\r\n
            this.hint = this.options.hint;\r\n
            this.store = this.options.store || new Common.UI.DataViewStore();\r\n
            this.itemWidth = this.options.itemWidth;\r\n
            this.itemHeight = this.options.itemHeight;\r\n
            this.menuMaxHeight = this.options.menuMaxHeight;\r\n
            this.beforeOpenHandler = this.options.beforeOpenHandler;\r\n
            this.rootWidth = 0;\r\n
            this.rootHeight = 0;\r\n
            this.rendered = false;\r\n
            this.fieldPicker = new Common.UI.DataView({\r\n
                cls: "field-picker",\r\n
                allowScrollbar: false,\r\n
                itemTemplate: _.template([\'<div class="style" id="<%= id %>">\', \'<img src="<%= imageUrl %>" width="\' + this.itemWidth + \'" height="\' + this.itemHeight + \'"/>\', \'<% if (typeof title !== "undefined") {%>\', \'<span class="title"><%= title %></span>\', "<% } %>", "</div>"].join(""))\r\n
            });\r\n
            this.openButton = new Common.UI.Button({\r\n
                cls: "open-menu",\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-bl",\r\n
                    offset: [0, 3],\r\n
                    items: [{\r\n
                        template: _.template(\'<div class="menu-picker-container"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.menuPicker = new Common.UI.DataView({\r\n
                cls: "menu-picker",\r\n
                parentMenu: this.openButton.menu,\r\n
                restoreHeight: this.menuMaxHeight,\r\n
                style: "max-height: " + this.menuMaxHeight + "px;",\r\n
                enableKeyEvents: this.options.enableKeyEvents,\r\n
                itemTemplate: _.template([\'<div class="style" id="<%= id %>">\', \'<img src="<%= imageUrl %>" width="\' + this.itemWidth + \'" height="\' + this.itemHeight + \'"/>\', \'<% if (typeof title !== "undefined") {%>\', \'<span class="title"><%= title %></span>\', "<% } %>", "</div>"].join(""))\r\n
            });\r\n
            setInterval(_.bind(this.checkSize, this), 500);\r\n
            if (this.options.el) {\r\n
                this.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            if (!this.rendered) {\r\n
                var me = this;\r\n
                me.trigger("render:before", me);\r\n
                me.cmpEl = $(me.el);\r\n
                var templateEl = me.template({\r\n
                    id: me.id,\r\n
                    cls: me.cls,\r\n
                    style: me.style\r\n
                });\r\n
                if (parentEl) {\r\n
                    me.setElement(parentEl, false);\r\n
                    me.cmpEl = $(templateEl);\r\n
                    parentEl.html(me.cmpEl);\r\n
                } else {\r\n
                    me.cmpEl.html(templateEl);\r\n
                }\r\n
                me.rootWidth = me.cmpEl.width();\r\n
                me.rootHeight = me.cmpEl.height();\r\n
                me.fieldPicker.render($(".view", me.cmpEl));\r\n
                me.openButton.render($(".button", me.cmpEl));\r\n
                me.menuPicker.render($(".menu-picker-container", me.cmpEl));\r\n
                if (me.openButton.menu.cmpEl) {\r\n
                    if (me.openButton.menu.cmpEl) {\r\n
                        me.openButton.menu.menuAlignEl = me.cmpEl;\r\n
                        me.openButton.menu.cmpEl.css("min-width", me.itemWidth);\r\n
                        me.openButton.menu.on("show:before", _.bind(me.onBeforeShowMenu, me));\r\n
                        me.openButton.menu.on("show:after", _.bind(me.onAfterShowMenu, me));\r\n
                        me.openButton.cmpEl.on("hide.bs.dropdown", _.bind(me.onBeforeHideMenu, me));\r\n
                        me.openButton.cmpEl.on("hidden.bs.dropdown", _.bind(me.onAfterHideMenu, me));\r\n
                    }\r\n
                }\r\n
                if (me.options.hint) {\r\n
                    me.cmpEl.attr("data-toggle", "tooltip");\r\n
                    me.cmpEl.tooltip({\r\n
                        title: me.options.hint,\r\n
                        placement: me.options.hintAnchor || "cursor"\r\n
                    });\r\n
                }\r\n
                me.fieldPicker.on("item:select", _.bind(me.onFieldPickerSelect, me));\r\n
                me.menuPicker.on("item:select", _.bind(me.onMenuPickerSelect, me));\r\n
                me.fieldPicker.on("item:click", _.bind(me.onFieldPickerClick, me));\r\n
                me.menuPicker.on("item:click", _.bind(me.onMenuPickerClick, me));\r\n
                me.onResize();\r\n
                me.rendered = true;\r\n
                me.trigger("render:after", me);\r\n
            }\r\n
            return this;\r\n
        },\r\n
        checkSize: function () {\r\n
            if (this.cmpEl) {\r\n
                var width = this.cmpEl.width(),\r\n
                height = this.cmpEl.height();\r\n
                if (this.rootWidth != width || this.rootHeight != height) {\r\n
                    this.rootWidth = width;\r\n
                    this.rootHeight = height;\r\n
                    this.onResize();\r\n
                }\r\n
            }\r\n
        },\r\n
        onResize: function () {\r\n
            if (this.openButton) {\r\n
                var button = $("button", this.openButton.cmpEl);\r\n
                button && button.css({\r\n
                    width: $(".button", this.cmpEl).width(),\r\n
                    height: $(".button", this.cmpEl).height()\r\n
                });\r\n
                this.openButton.menu.hide();\r\n
                var picker = this.menuPicker;\r\n
                if (picker) {\r\n
                    var record = picker.getSelectedRec();\r\n
                    if (record) {\r\n
                        record = record[0];\r\n
                        this.fillComboView(record || picker.store.at(0), !!record, true);\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("resize", this);\r\n
            }\r\n
        },\r\n
        onBeforeShowMenu: function (e) {\r\n
            var me = this;\r\n
            if (_.isFunction(me.beforeOpenHandler)) {\r\n
                me.beforeOpenHandler(me, e);\r\n
            } else {\r\n
                if (me.openButton.menu.cmpEl) {\r\n
                    var itemMargin = 0;\r\n
                    try {\r\n
                        var itemEl = $($(".dropdown-menu .dataview.inner .style", me.cmpEl)[0]);\r\n
                        itemMargin = itemEl ? (parseInt(itemEl.css("margin-left")) + parseInt(itemEl.css("margin-right"))) : 0;\r\n
                    } catch(e) {}\r\n
                    me.openButton.menu.cmpEl.css({\r\n
                        "width": Math.round((me.cmpEl.width() + (itemMargin * me.fieldPicker.store.length)) / me.itemWidth - 0.2) * (me.itemWidth + itemMargin),\r\n
                        "min-height": this.cmpEl.height()\r\n
                    });\r\n
                }\r\n
            }\r\n
            if (me.options.hint) {\r\n
                var tip = me.cmpEl.data("bs.tooltip");\r\n
                if (tip) {\r\n
                    if (tip.dontShow === undefined) {\r\n
                        tip.dontShow = true;\r\n
                    }\r\n
                    tip.hide();\r\n
                }\r\n
            }\r\n
        },\r\n
        onBeforeHideMenu: function (e) {\r\n
            this.trigger("hide:before", this, e);\r\n
            if (Common.UI.Scroller.isMouseCapture()) {\r\n
                e.preventDefault();\r\n
            }\r\n
        },\r\n
        onAfterShowMenu: function (e) {\r\n
            var me = this;\r\n
            if (me.menuPicker.scroller) {\r\n
                me.menuPicker.scroller.update({\r\n
                    includePadding: true,\r\n
                    suppressScrollX: true,\r\n
                    alwaysVisibleY: true\r\n
                });\r\n
            }\r\n
        },\r\n
        onAfterHideMenu: function (e) {\r\n
            this.trigger("hide:after", this, e);\r\n
        },\r\n
        onFieldPickerSelect: function (picker, item, record) {},\r\n
        onMenuPickerSelect: function (picker, item, record) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            this.fillComboView(record, false);\r\n
            if (record && !this.isSuspendEvents) {\r\n
                this.trigger("select", this, record);\r\n
            }\r\n
        },\r\n
        onFieldPickerClick: function (dataView, itemView, record) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("click", this, record);\r\n
            }\r\n
            if (this.options.hint) {\r\n
                var tip = this.cmpEl.data("bs.tooltip");\r\n
                if (tip) {\r\n
                    if (tip.dontShow === undefined) {\r\n
                        tip.dontShow = true;\r\n
                    }\r\n
                    tip.hide();\r\n
                }\r\n
            }\r\n
        },\r\n
        onMenuPickerClick: function (dataView, itemView, record) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (!this.isSuspendEvents) {\r\n
                this.trigger("click", this, record);\r\n
            }\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            this.disabled = disabled;\r\n
            if (!this.rendered) {\r\n
                return;\r\n
            }\r\n
            this.cmpEl.toggleClass("disabled", disabled);\r\n
            $("button", this.openButton.cmpEl).toggleClass("disabled", disabled);\r\n
            this.fieldPicker.setDisabled(disabled);\r\n
        },\r\n
        isDisabled: function () {\r\n
            return this.disabled;\r\n
        },\r\n
        fillComboView: function (record, forceSelect, forceFill) {\r\n
            if (!_.isUndefined(record) && record instanceof Backbone.Model) {\r\n
                var me = this,\r\n
                store = me.menuPicker.store,\r\n
                fieldPickerEl = $(me.fieldPicker.el);\r\n
                if (store) {\r\n
                    if (forceFill || !me.fieldPicker.store.findWhere({\r\n
                        "id": record.get("id")\r\n
                    })) {\r\n
                        if (me.itemMarginLeft === undefined) {\r\n
                            var div = $($(this.menuPicker.el).find(".inner > div:not(.grouped-data):not(.ps-scrollbar-x-rail):not(.ps-scrollbar-y-rail)")[0]);\r\n
                            if (div.length > 0) {\r\n
                                me.itemMarginLeft = parseInt(div.css("margin-left"));\r\n
                                me.itemMarginRight = parseInt(div.css("margin-right"));\r\n
                                me.itemPaddingLeft = parseInt(div.css("padding-left"));\r\n
                                me.itemPaddingRight = parseInt(div.css("padding-right"));\r\n
                                me.itemBorderLeft = parseInt(div.css("border-left-width"));\r\n
                                me.itemBorderRight = parseInt(div.css("border-right-width"));\r\n
                            }\r\n
                        }\r\n
                        me.fieldPicker.store.reset([]);\r\n
                        var indexRec = store.indexOf(record),\r\n
                        countRec = store.length,\r\n
                        maxViewCount = Math.floor((fieldPickerEl.width()) / (me.itemWidth + (me.itemMarginLeft || 0) + (me.itemMarginRight || 0) + (me.itemPaddingLeft || 0) + (me.itemPaddingRight || 0) + (me.itemBorderLeft || 0) + (me.itemBorderRight || 0))),\r\n
                        newStyles = [];\r\n
                        if (fieldPickerEl.height() / me.itemHeight > 2) {\r\n
                            maxViewCount *= Math.floor(fieldPickerEl.height() / me.itemHeight);\r\n
                        }\r\n
                        if (indexRec < 0) {\r\n
                            return;\r\n
                        }\r\n
                        indexRec = Math.floor(indexRec / maxViewCount) * maxViewCount;\r\n
                        for (var index = indexRec, viewCount = 0; index < countRec && viewCount < maxViewCount; index++, viewCount++) {\r\n
                            newStyles.push(store.at(index));\r\n
                        }\r\n
                        me.fieldPicker.store.add(newStyles);\r\n
                    }\r\n
                    if (forceSelect) {\r\n
                        var selectRecord = me.fieldPicker.store.findWhere({\r\n
                            "id": record.get("id")\r\n
                        });\r\n
                        if (selectRecord) {\r\n
                            me.suspendEvents();\r\n
                            me.fieldPicker.selectRecord(selectRecord, true);\r\n
                            me.resumeEvents();\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        selectByIndex: function (index) {\r\n
            if (index < 0) {\r\n
                this.fieldPicker.deselectAll();\r\n
            }\r\n
            this.menuPicker.selectByIndex(index);\r\n
        },\r\n
        setItemWidth: function (width) {\r\n
            if (this.itemWidth != width) {\r\n
                this.itemWidth = window.devicePixelRatio > 1 ? width / 2 : width;\r\n
            }\r\n
        },\r\n
        setItemHeight: function (height) {\r\n
            if (this.itemHeight != height) {\r\n
                this.itemHeight = window.devicePixelRatio > 1 ? height / 2 : height;\r\n
            }\r\n
        }\r\n
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
            <value> <int>15547</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
