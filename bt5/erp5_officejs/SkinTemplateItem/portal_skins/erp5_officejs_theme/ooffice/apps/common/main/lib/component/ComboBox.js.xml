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
            <value> <string>ts44308798.86</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ComboBox.js</string> </value>
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
    Common.UI.ComboBoxModel = Backbone.Model.extend({\r\n
        defaults: function () {\r\n
            return {\r\n
                id: Common.UI.getId(),\r\n
                value: null,\r\n
                displayValue: null\r\n
            };\r\n
        }\r\n
    });\r\n
    Common.UI.ComboBoxStore = Backbone.Collection.extend({\r\n
        model: Common.UI.ComboBoxModel\r\n
    });\r\n
    Common.UI.ComboBox = Common.UI.BaseView.extend((function () {\r\n
        return {\r\n
            options: {\r\n
                id: null,\r\n
                cls: "",\r\n
                style: "",\r\n
                hint: false,\r\n
                editable: true,\r\n
                disabled: false,\r\n
                menuCls: "",\r\n
                menuStyle: "",\r\n
                displayField: "displayValue",\r\n
                valueField: "value"\r\n
            },\r\n
            template: _.template([\'<span class="input-group combobox <%= cls %>" id="<%= id %>" style="<%= style %>">\', \'<input type="text" class="form-control">\', \'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>\', \'<ul class="dropdown-menu <%= menuCls %>" style="<%= menuStyle %>" role="menu">\', "<% _.each(items, function(item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a tabindex="-1" type="menuitem"><%= scope.getDisplayValue(item) %></a></li>\', "<% }); %>", "</ul>", "</span>"].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                var me = this,\r\n
                el = $(this.el);\r\n
                this.id = me.options.id || Common.UI.getId();\r\n
                this.cls = me.options.cls;\r\n
                this.style = me.options.style;\r\n
                this.menuCls = me.options.menuCls;\r\n
                this.menuStyle = me.options.menuStyle;\r\n
                this.template = me.options.template || me.template;\r\n
                this.hint = me.options.hint;\r\n
                this.editable = me.options.editable;\r\n
                this.disabled = me.options.disabled;\r\n
                this.store = me.options.store || new Common.UI.ComboBoxStore();\r\n
                this.displayField = me.options.displayField;\r\n
                this.valueField = me.options.valueField;\r\n
                me.rendered = me.options.rendered || false;\r\n
                this.lastValue = null;\r\n
                me.store.add(me.options.data);\r\n
                if (me.options.el) {\r\n
                    me.render();\r\n
                }\r\n
            },\r\n
            render: function (parentEl) {\r\n
                var me = this;\r\n
                if (!me.rendered) {\r\n
                    this.cmpEl = $(this.template({\r\n
                        id: this.id,\r\n
                        cls: this.cls,\r\n
                        style: this.style,\r\n
                        menuCls: this.menuCls,\r\n
                        menuStyle: this.menuStyle,\r\n
                        items: this.store.toJSON(),\r\n
                        scope: me\r\n
                    }));\r\n
                    if (parentEl) {\r\n
                        this.setElement(parentEl, false);\r\n
                        parentEl.html(this.cmpEl);\r\n
                    } else {\r\n
                        $(this.el).html(this.cmpEl);\r\n
                    }\r\n
                } else {\r\n
                    this.cmpEl = $(this.el);\r\n
                }\r\n
                if (!me.rendered) {\r\n
                    var el = this.cmpEl;\r\n
                    this._input = el.find("input");\r\n
                    this._button = el.find(".btn");\r\n
                    el.on("click", "a", _.bind(this.itemClicked, this));\r\n
                    el.on("mousedown", "a", _.bind(this.itemMouseDown, this));\r\n
                    if (this.editable) {\r\n
                        el.on("change", "input", _.bind(this.onInputChanged, this));\r\n
                        el.on("keydown", "input", _.bind(this.onInputKeyDown, this));\r\n
                        el.on("click", ".form-control", _.bind(this.onEditableInputClick, this));\r\n
                    } else {\r\n
                        el.on("click", ".form-control", _.bind(this.onInputClick, this));\r\n
                        this._input.attr("readonly", "readonly");\r\n
                        this._input.attr("data-can-copy", false);\r\n
                    }\r\n
                    if (me.options.hint) {\r\n
                        el.attr("data-toggle", "tooltip");\r\n
                        el.tooltip({\r\n
                            title: me.options.hint,\r\n
                            placement: me.options.hintAnchor || "cursor"\r\n
                        });\r\n
                    }\r\n
                    el.on("show.bs.dropdown", _.bind(me.onBeforeShowMenu, me));\r\n
                    el.on("shown.bs.dropdown", _.bind(me.onAfterShowMenu, me));\r\n
                    el.on("hide.bs.dropdown", _.bind(me.onBeforeHideMenu, me));\r\n
                    el.on("hidden.bs.dropdown", _.bind(me.onAfterHideMenu, me));\r\n
                    el.on("keydown.after.bs.dropdown", _.bind(me.onAfterKeydownMenu, me));\r\n
                    Common.NotificationCenter.on("menumanager:hideall", _.bind(me.closeMenu, me));\r\n
                    this.scroller = new Common.UI.Scroller({\r\n
                        el: $(".dropdown-menu", me.cmpEl),\r\n
                        minScrollbarLength: 40,\r\n
                        scrollYMarginOffset: 30,\r\n
                        includePadding: true\r\n
                    });\r\n
                    this.setDefaultSelection();\r\n
                    this.listenTo(this.store, "reset", this.onResetItems);\r\n
                }\r\n
                me.rendered = true;\r\n
                if (me.disabled) {\r\n
                    me.setDisabled(me.disabled);\r\n
                }\r\n
                return this;\r\n
            },\r\n
            setData: function (data) {\r\n
                this.store.reset([]);\r\n
                this.store.add(data);\r\n
                this.setRawValue("");\r\n
                this.onResetItems();\r\n
            },\r\n
            openMenu: function (delay) {\r\n
                var me = this;\r\n
                _.delay(function () {\r\n
                    me.cmpEl.addClass("open");\r\n
                },\r\n
                delay || 0);\r\n
            },\r\n
            closeMenu: function () {\r\n
                this.cmpEl.removeClass("open");\r\n
            },\r\n
            isMenuOpen: function () {\r\n
                return this.cmpEl.hasClass("open");\r\n
            },\r\n
            onBeforeShowMenu: function (e) {\r\n
                this.trigger("show:before", this, e);\r\n
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
            onAfterShowMenu: function (e) {\r\n
                var $list = $(this.el).find("ul"),\r\n
                $selected = $list.find("> li.selected");\r\n
                if ($selected.length) {\r\n
                    var itemTop = $selected.position().top,\r\n
                    itemHeight = $selected.height(),\r\n
                    listHeight = $list.height();\r\n
                    if (itemTop < 0 || itemTop + itemHeight > listHeight) {\r\n
                        $list.scrollTop($list.scrollTop() + itemTop + itemHeight - (listHeight / 2));\r\n
                    }\r\n
                }\r\n
                if (this.scroller) {\r\n
                    this.scroller.update();\r\n
                }\r\n
                this.trigger("show:after", this, e);\r\n
            },\r\n
            onBeforeHideMenu: function (e) {\r\n
                this.trigger("hide:before", this, e);\r\n
                if (Common.UI.Scroller.isMouseCapture()) {\r\n
                    e.preventDefault();\r\n
                }\r\n
            },\r\n
            onAfterHideMenu: function (e) {\r\n
                this.cmpEl.find(".dropdown-toggle").blur();\r\n
                this.trigger("hide:after", this, e);\r\n
            },\r\n
            onAfterKeydownMenu: function (e) {\r\n
                if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                    $(e.target).click();\r\n
                    var me = this;\r\n
                    if (this.rendered) {\r\n
                        if (Common.Utils.isIE) {\r\n
                            this._input.trigger("change", {\r\n
                                onkeydown: true\r\n
                            });\r\n
                        } else {\r\n
                            this._input.blur();\r\n
                        }\r\n
                    }\r\n
                    return false;\r\n
                } else {\r\n
                    if (e.keyCode == Common.UI.Keys.ESC && this.isMenuOpen()) {\r\n
                        this.closeMenu();\r\n
                        this.onAfterHideMenu(e);\r\n
                        return false;\r\n
                    }\r\n
                }\r\n
            },\r\n
            onInputKeyDown: function (e) {\r\n
                var me = this;\r\n
                if (e.keyCode == Common.UI.Keys.ESC) {\r\n
                    this.closeMenu();\r\n
                    this.onAfterHideMenu(e);\r\n
                } else {\r\n
                    if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN) {\r\n
                        if (!this.isMenuOpen()) {\r\n
                            this.openMenu();\r\n
                        }\r\n
                        _.delay(function () {\r\n
                            me._skipInputChange = true;\r\n
                            me.cmpEl.find("ul li:first a").focus();\r\n
                        },\r\n
                        10);\r\n
                    } else {\r\n
                        me._skipInputChange = false;\r\n
                    }\r\n
                }\r\n
            },\r\n
            onInputChanged: function (e, extra) {\r\n
                if (extra && extra.synthetic) {\r\n
                    return;\r\n
                }\r\n
                if (this._skipInputChange) {\r\n
                    this._skipInputChange = false;\r\n
                    return;\r\n
                }\r\n
                var val = $(e.target).val(),\r\n
                record = {};\r\n
                if (this.lastValue === val) {\r\n
                    if (extra && extra.onkeydown) {\r\n
                        this.trigger("combo:blur", this, e);\r\n
                    }\r\n
                    return;\r\n
                }\r\n
                record[this.valueField] = val;\r\n
                this.trigger("changed:before", this, record, e);\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                var obj;\r\n
                this._selectedItem = this.store.findWhere((obj = {},\r\n
                obj[this.displayField] = val, obj));\r\n
                if (this._selectedItem) {\r\n
                    record = this._selectedItem.toJSON();\r\n
                    $(".selected", $(this.el)).removeClass("selected");\r\n
                    $("#" + this._selectedItem.get("id"), $(this.el)).addClass("selected");\r\n
                }\r\n
                this.trigger("changed:after", this, record, e);\r\n
            },\r\n
            onInputClick: function (e) {\r\n
                if (this._button) {\r\n
                    this._button.dropdown("toggle");\r\n
                }\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
            },\r\n
            onEditableInputClick: function (e) {\r\n
                if (this.options.hint) {\r\n
                    var tip = this.cmpEl.data("bs.tooltip");\r\n
                    if (tip) {\r\n
                        if (tip.dontShow === undefined) {\r\n
                            tip.dontShow = true;\r\n
                        }\r\n
                        tip.hide();\r\n
                    }\r\n
                }\r\n
                if (this.isMenuOpen() && e.which == 1) {\r\n
                    e.stopPropagation();\r\n
                }\r\n
            },\r\n
            setDefaultSelection: function () {\r\n
                if (!this.rendered) {\r\n
                    return;\r\n
                }\r\n
                var val = this._input.val(),\r\n
                obj;\r\n
                if (val) {\r\n
                    this._selectedItem = this.store.findWhere((obj = {},\r\n
                    obj[this.displayField] = val, obj));\r\n
                    if (this._selectedItem) {\r\n
                        $(".selected", $(this.el)).removeClass("selected");\r\n
                        $("#" + this._selectedItem.get("id"), $(this.el)).addClass("selected");\r\n
                    }\r\n
                }\r\n
            },\r\n
            setDisabled: function (disabled) {\r\n
                this.disabled = disabled;\r\n
                if (!this.rendered) {\r\n
                    return;\r\n
                }\r\n
                disabled ? this._input.attr("disabled", true) : this._input.removeAttr("disabled");\r\n
                this.cmpEl.toggleClass("disabled", disabled);\r\n
                this._button.toggleClass("disabled", disabled);\r\n
            },\r\n
            isDisabled: function () {\r\n
                return this.disabled;\r\n
            },\r\n
            setRawValue: function (value) {\r\n
                if (this.rendered) {\r\n
                    this._input.val(value).trigger("change", {\r\n
                        synthetic: true\r\n
                    });\r\n
                    this.lastValue = (value !== null && value !== undefined) ? value.toString() : value;\r\n
                }\r\n
            },\r\n
            getRawValue: function () {\r\n
                return this.rendered ? this._input.val() : null;\r\n
            },\r\n
            setValue: function (value) {\r\n
                if (!this.rendered) {\r\n
                    return;\r\n
                }\r\n
                var obj;\r\n
                this._selectedItem = this.store.findWhere((obj = {},\r\n
                obj[this.valueField] = value, obj));\r\n
                $(".selected", $(this.el)).removeClass("selected");\r\n
                if (this._selectedItem) {\r\n
                    this.setRawValue(this._selectedItem.get(this.displayField));\r\n
                    $("#" + this._selectedItem.get("id"), $(this.el)).addClass("selected");\r\n
                } else {\r\n
                    this.setRawValue(value);\r\n
                }\r\n
            },\r\n
            getValue: function () {\r\n
                if (!this.rendered) {\r\n
                    return null;\r\n
                }\r\n
                if (this._selectedItem && !_.isUndefined(this._selectedItem.get(this.valueField))) {\r\n
                    return this._selectedItem.get(this.valueField);\r\n
                }\r\n
                return this._input.val();\r\n
            },\r\n
            getDisplayValue: function (record) {\r\n
                return Common.Utils.String.htmlEncode(record[this.displayField]);\r\n
            },\r\n
            getSelectedRecord: function () {\r\n
                if (!this.rendered) {\r\n
                    return null;\r\n
                }\r\n
                if (this._selectedItem && !_.isUndefined(this._selectedItem.get(this.valueField))) {\r\n
                    return _.extend({},\r\n
                    this._selectedItem.toJSON());\r\n
                }\r\n
                return null;\r\n
            },\r\n
            selectRecord: function (record) {\r\n
                if (!this.rendered || !record) {\r\n
                    return;\r\n
                }\r\n
                this._selectedItem = record;\r\n
                $(".selected", $(this.el)).removeClass("selected");\r\n
                this.setRawValue(this._selectedItem.get(this.displayField));\r\n
                $("#" + this._selectedItem.get("id"), $(this.el)).addClass("selected");\r\n
            },\r\n
            itemClicked: function (e) {\r\n
                var el = $(e.target).closest("li");\r\n
                this._selectedItem = this.store.findWhere({\r\n
                    id: el.attr("id")\r\n
                });\r\n
                if (this._selectedItem) {\r\n
                    this.lastValue = this._selectedItem.get(this.displayField);\r\n
                    this._input.val(this.lastValue).trigger("change", {\r\n
                        synthetic: true\r\n
                    });\r\n
                    $(".selected", $(this.el)).removeClass("selected");\r\n
                    el.addClass("selected");\r\n
                    this.trigger("selected", this, _.extend({},\r\n
                    this._selectedItem.toJSON()), e);\r\n
                    e.preventDefault();\r\n
                }\r\n
                this._isMouseDownMenu = false;\r\n
            },\r\n
            itemMouseDown: function (e) {\r\n
                if (e.which != 1) {\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                    return false;\r\n
                }\r\n
                this._isMouseDownMenu = true;\r\n
            },\r\n
            onResetItems: function () {\r\n
                $(this.el).find("ul").html(_.template(["<% _.each(items, function(item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a tabindex="-1" type="menuitem"><%= scope.getDisplayValue(item) %></a></li>\', "<% }); %>"].join(""), {\r\n
                    items: this.store.toJSON(),\r\n
                    scope: this\r\n
                }));\r\n
                if (!_.isUndefined(this.scroller)) {\r\n
                    this.scroller.destroy();\r\n
                    delete this.scroller;\r\n
                }\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(".dropdown-menu", this.cmpEl),\r\n
                    minScrollbarLength: 40,\r\n
                    scrollYMarginOffset: 30,\r\n
                    includePadding: true\r\n
                });\r\n
            }\r\n
        };\r\n
    })());\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>19287</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
