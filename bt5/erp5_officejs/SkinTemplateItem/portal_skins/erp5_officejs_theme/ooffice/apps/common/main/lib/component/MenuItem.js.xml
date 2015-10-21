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
            <value> <string>ts44308800.02</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>MenuItem.js</string> </value>
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
define(["common/main/lib/component/BaseView", "common/main/lib/component/ToggleManager"], function () {\r\n
    Common.UI.MenuItem = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            id: null,\r\n
            cls: "",\r\n
            style: "",\r\n
            hint: false,\r\n
            checkable: false,\r\n
            checked: false,\r\n
            allowDepress: false,\r\n
            disabled: false,\r\n
            value: null,\r\n
            toggleGroup: null,\r\n
            iconCls: "",\r\n
            menu: null,\r\n
            canFocused: true\r\n
        },\r\n
        tagName: "li",\r\n
        template: _.template([\'<a id="<%= id %>" style="<%= style %>" <% if(options.canFocused) { %> tabindex="-1" type="menuitem" <% }; if(!_.isUndefined(options.stopPropagation)) { %> data-stopPropagation="true" <% }; %> >\', "<% if (!_.isEmpty(iconCls)) { %>", \'<span class="menu-item-icon <%= iconCls %>"></span>\', "<% } %>", "<%= caption %>", "</a>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            this.id = me.options.id || Common.UI.getId();\r\n
            this.cls = me.options.cls;\r\n
            this.style = me.options.style;\r\n
            this.caption = me.options.caption;\r\n
            this.menu = me.options.menu || null;\r\n
            this.checkable = me.options.checkable;\r\n
            this.checked = me.options.checked;\r\n
            me.allowDepress = me.options.allowDepress;\r\n
            this.disabled = me.options.disabled;\r\n
            this.value = me.options.value;\r\n
            this.toggleGroup = me.options.toggleGroup;\r\n
            this.template = me.options.template || this.template;\r\n
            this.iconCls = me.options.iconCls;\r\n
            this.rendered = false;\r\n
            if (this.menu !== null && !(this.menu instanceof Common.UI.Menu)) {\r\n
                this.menu = new Common.UI.Menu(_.extend({},\r\n
                me.options.menu));\r\n
            }\r\n
            if (me.options.el) {\r\n
                this.render();\r\n
            }\r\n
        },\r\n
        render: function () {\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            me.trigger("render:before", me);\r\n
            if (me.caption === "--") {\r\n
                el.addClass("divider");\r\n
            } else {\r\n
                if (!this.rendered) {\r\n
                    el.off("click");\r\n
                    Common.UI.ToggleManager.unregister(me);\r\n
                    $(this.el).html(this.template({\r\n
                        id: me.id,\r\n
                        caption: me.caption,\r\n
                        iconCls: me.iconCls,\r\n
                        style: me.style,\r\n
                        options: me.options\r\n
                    }));\r\n
                    if (me.menu) {\r\n
                        el.addClass("dropdown-submenu");\r\n
                        me.menu.render($(this.el));\r\n
                        el.mouseenter(_.bind(me.menu.alignPosition, me.menu));\r\n
                        el.focusout(_.bind(me.onBlurItem, me));\r\n
                        el.hover(_.bind(me.onHoverItem, me), _.bind(me.onUnHoverItem, me));\r\n
                    }\r\n
                    var firstChild = el.children(":first");\r\n
                    if (this.checkable && firstChild) {\r\n
                        firstChild.toggleClass("checkable", this.checkable);\r\n
                        firstChild.toggleClass("checked", this.checked);\r\n
                        if (!_.isEmpty(this.iconCls)) {\r\n
                            firstChild.css("background-image", "none");\r\n
                        }\r\n
                    }\r\n
                    if (this.disabled) {\r\n
                        $(this.el).toggleClass("disabled", this.disabled);\r\n
                    }\r\n
                    el.on("click", _.bind(this.onItemClick, this));\r\n
                    el.on("mousedown", _.bind(this.onItemMouseDown, this));\r\n
                    Common.UI.ToggleManager.register(me);\r\n
                }\r\n
            }\r\n
            me.cmpEl = $(this.el);\r\n
            me.rendered = true;\r\n
            me.trigger("render:after", me);\r\n
            return this;\r\n
        },\r\n
        setCaption: function (caption) {\r\n
            this.caption = caption;\r\n
            if (this.rendered) {\r\n
                this.cmpEl.find("a").contents().last()[0].textContent = Common.Utils.String.htmlEncode(caption);\r\n
            }\r\n
        },\r\n
        setChecked: function (check, suppressEvent) {\r\n
            this.toggle(check, suppressEvent);\r\n
        },\r\n
        isChecked: function () {\r\n
            return this.checked;\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            this.disabled = !!disabled;\r\n
            if (this.rendered) {\r\n
                this.cmpEl.toggleClass("disabled", this.disabled);\r\n
            }\r\n
        },\r\n
        isDisabled: function () {\r\n
            return this.disabled;\r\n
        },\r\n
        toggle: function (toggle, suppressEvent) {\r\n
            var state = toggle === undefined ? !this.checked : !!toggle;\r\n
            if (this.checkable) {\r\n
                this.checked = state;\r\n
                if (this.rendered) {\r\n
                    var firstChild = this.cmpEl.children(":first");\r\n
                    if (firstChild) {\r\n
                        firstChild.toggleClass("checked", this.checked);\r\n
                        if (!_.isEmpty(this.iconCls)) {\r\n
                            firstChild.css("background-image", "none");\r\n
                        }\r\n
                    }\r\n
                }\r\n
                if (!suppressEvent) {\r\n
                    this.trigger("toggle", this, state);\r\n
                }\r\n
            }\r\n
        },\r\n
        onItemMouseDown: function (e) {\r\n
            if (e.which != 1) {\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                return false;\r\n
            }\r\n
        },\r\n
        onItemClick: function (e) {\r\n
            if (e.which != 1 && (e.which !== undefined || this.menu)) {\r\n
                return false;\r\n
            }\r\n
            if (!this.disabled && (this.allowDepress || !(this.checked && this.toggleGroup))) {\r\n
                this.setChecked(!this.checked);\r\n
            }\r\n
            if (this.menu) {\r\n
                if (e.target.id == this.id) {\r\n
                    return false;\r\n
                }\r\n
                if (!this.menu.isOver) {\r\n
                    this.cmpEl.removeClass("over");\r\n
                }\r\n
                return;\r\n
            }\r\n
            if (!this.disabled) {\r\n
                this.trigger("click", this, e);\r\n
            } else {\r\n
                return false;\r\n
            }\r\n
        },\r\n
        onHoverItem: function (e) {\r\n
            this._doHover(e);\r\n
        },\r\n
        onUnHoverItem: function (e) {\r\n
            this._doUnHover(e);\r\n
        },\r\n
        onBlurItem: function (e) {\r\n
            this._doUnHover(e);\r\n
        },\r\n
        _doHover: function (e) {\r\n
            var me = this;\r\n
            if (me.menu && !me.disabled) {\r\n
                clearTimeout(me.hideMenuTimer);\r\n
                me.cmpEl.trigger("show.bs.dropdown");\r\n
                me.expandMenuTimer = _.delay(function () {\r\n
                    me.cmpEl.addClass("over");\r\n
                    me.cmpEl.trigger("shown.bs.dropdown");\r\n
                },\r\n
                200);\r\n
            }\r\n
        },\r\n
        _doUnHover: function (e) {\r\n
            var me = this;\r\n
            if (me.menu && !me.disabled) {\r\n
                clearTimeout(me.expandMenuTimer);\r\n
                me.hideMenuTimer = _.delay(function () {\r\n
                    if (!me.menu.isOver) {\r\n
                        me.cmpEl.removeClass("over");\r\n
                    }\r\n
                },\r\n
                200);\r\n
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
            <value> <int>9380</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
