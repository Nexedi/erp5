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
            <value> <string>ts44308798.43</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Button.js</string> </value>
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
    Common.UI.Button = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            id: null,\r\n
            hint: false,\r\n
            enableToggle: false,\r\n
            allowDepress: true,\r\n
            toggleGroup: null,\r\n
            cls: "",\r\n
            iconCls: "",\r\n
            caption: "",\r\n
            menu: null,\r\n
            disabled: false,\r\n
            pressed: false,\r\n
            split: false\r\n
        },\r\n
        template: _.template(["<% if (menu == null) { %>", \'<button type="button" class="btn <%= cls %>" id="<%= id %>" style="<%= style %>">\', \'<span class="caption"><%= caption %></span>\', \'<% if (iconCls != "") { %>\', \'<span class="btn-icon <%= iconCls %>">&nbsp;</span>\', "<% } %>", "</button>", "<% } else if (split == false) {%>", \'<div class="btn-group" id="<%= id %>" style="<%= style %>">\', \'<button type="button" class="btn dropdown-toggle <%= cls %>" data-toggle="dropdown">\', \'<span class="caption"><%= caption %></span>\', \'<% if (iconCls != "") { %>\', \'<span class="btn-icon <%= iconCls %>">&nbsp;</span>\', "<% } %>", \'<span class="caret"></span>\', "</button>", "</div>", "<% } else { %>", \'<div class="btn-group split" id="<%= id %>" style="<%= style %>">\', \'<button type="button" class="btn <%= cls %>">\', \'<span class="caption"><%= caption %></span>\', \'<% if (iconCls != "") { %>\', \'<span class="btn-icon <%= iconCls %>">&nbsp;</span>\', "<% } %>", "</button>", \'<button type="button" class="btn <%= cls %> dropdown-toggle" data-toggle="dropdown">\', \'<span class="caret"></span>\', \'<span class="sr-only"></span>\', "</button>", "</div>", "<% } %>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this;\r\n
            me.id = me.options.id || Common.UI.getId();\r\n
            me.hint = me.options.hint;\r\n
            me.enableToggle = me.options.enableToggle;\r\n
            me.allowDepress = me.options.allowDepress;\r\n
            me.cls = me.options.cls;\r\n
            me.iconCls = me.options.iconCls;\r\n
            me.menu = me.options.menu;\r\n
            me.split = me.options.split;\r\n
            me.toggleGroup = me.options.toggleGroup;\r\n
            me.disabled = me.options.disabled;\r\n
            me.pressed = me.options.pressed;\r\n
            me.caption = me.options.caption;\r\n
            me.template = me.options.template || me.template;\r\n
            me.style = me.options.style;\r\n
            me.rendered = false;\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            me.trigger("render:before", me);\r\n
            me.cmpEl = $(me.el);\r\n
            if (parentEl) {\r\n
                me.setElement(parentEl, false);\r\n
                if (!me.rendered) {\r\n
                    me.cmpEl = $(this.template({\r\n
                        id: me.id,\r\n
                        cls: me.cls,\r\n
                        iconCls: me.iconCls,\r\n
                        menu: me.menu,\r\n
                        split: me.split,\r\n
                        disabled: me.disabled,\r\n
                        pressed: me.pressed,\r\n
                        caption: me.caption,\r\n
                        style: me.style\r\n
                    }));\r\n
                    if (me.menu && _.isFunction(me.menu.render)) {\r\n
                        me.menu.render(me.cmpEl);\r\n
                    }\r\n
                    parentEl.html(me.cmpEl);\r\n
                }\r\n
            }\r\n
            if (!me.rendered) {\r\n
                var el = me.cmpEl,\r\n
                isGroup = el.hasClass("btn-group"),\r\n
                isSplit = el.hasClass("split");\r\n
                if (me.options.hint) {\r\n
                    var modalParents = me.cmpEl.closest(".asc-window");\r\n
                    me.cmpEl.attr("data-toggle", "tooltip");\r\n
                    me.cmpEl.tooltip({\r\n
                        title: me.options.hint,\r\n
                        placement: me.options.hintAnchor || "cursor"\r\n
                    });\r\n
                    if (modalParents.length > 0) {\r\n
                        me.cmpEl.data("bs.tooltip").tip().css("z-index", parseInt(modalParents.css("z-index")) + 10);\r\n
                    }\r\n
                }\r\n
                if (_.isString(me.toggleGroup)) {\r\n
                    me.enableToggle = true;\r\n
                }\r\n
                var buttonHandler = function (e) {\r\n
                    if (!me.disabled && e.which == 1) {\r\n
                        me.doToggle();\r\n
                        if (me.options.hint) {\r\n
                            var tip = me.cmpEl.data("bs.tooltip");\r\n
                            if (tip) {\r\n
                                if (tip.dontShow === undefined) {\r\n
                                    tip.dontShow = true;\r\n
                                }\r\n
                                tip.hide();\r\n
                            }\r\n
                        }\r\n
                        me.trigger("click", me, e);\r\n
                    }\r\n
                };\r\n
                var doSplitSelect = function (select, e) {\r\n
                    if (!select) {\r\n
                        var isUnderMouse = false;\r\n
                        _.each($("button", el), function (el) {\r\n
                            if ($(el).is(":hover")) {\r\n
                                isUnderMouse = true;\r\n
                                return false;\r\n
                            }\r\n
                        });\r\n
                        if (!isUnderMouse) {\r\n
                            el.removeClass("over");\r\n
                            $("button", el).removeClass("over");\r\n
                        }\r\n
                    }\r\n
                    if (!select && (me.enableToggle && me.allowDepress && me.pressed)) {\r\n
                        return;\r\n
                    }\r\n
                    if (select && !isSplit && (me.enableToggle && me.allowDepress && !me.pressed)) {\r\n
                        e.preventDefault();\r\n
                        return;\r\n
                    }\r\n
                    $("button:first", el).toggleClass("active", select);\r\n
                    $("[data-toggle^=dropdown]", el).toggleClass("active", select);\r\n
                    el.toggleClass("active", select);\r\n
                };\r\n
                var menuHandler = function (e) {\r\n
                    if (!me.disabled && e.which == 1) {\r\n
                        if (isSplit) {\r\n
                            if (me.options.hint) {\r\n
                                var tip = me.cmpEl.data("bs.tooltip");\r\n
                                if (tip) {\r\n
                                    if (tip.dontShow === undefined) {\r\n
                                        tip.dontShow = true;\r\n
                                    }\r\n
                                    tip.hide();\r\n
                                }\r\n
                            }\r\n
                            var isOpen = el.hasClass("open");\r\n
                            doSplitSelect(!isOpen, e);\r\n
                        }\r\n
                    }\r\n
                };\r\n
                var doSetActiveState = function (e, state) {\r\n
                    if (isSplit) {\r\n
                        doSplitSelect(state, e);\r\n
                    } else {\r\n
                        el.toggleClass("active", state);\r\n
                        $("button", el).toggleClass("active", state);\r\n
                    }\r\n
                };\r\n
                var onMouseDown = function (e) {\r\n
                    doSplitSelect(true, e);\r\n
                    $(document).on("mouseup", onMouseUp);\r\n
                };\r\n
                var onMouseUp = function (e) {\r\n
                    doSplitSelect(false, e);\r\n
                    $(document).off("mouseup", onMouseUp);\r\n
                };\r\n
                var onAfterHideMenu = function (e) {\r\n
                    me.cmpEl.find(".dropdown-toggle").blur();\r\n
                };\r\n
                if (isGroup) {\r\n
                    if (isSplit) {\r\n
                        $("[data-toggle^=dropdown]", el).on("mousedown", _.bind(menuHandler, this));\r\n
                        $("button", el).on("mousedown", _.bind(onMouseDown, this));\r\n
                    }\r\n
                    el.on("hide.bs.dropdown", _.bind(doSplitSelect, me, false));\r\n
                    el.on("show.bs.dropdown", _.bind(doSplitSelect, me, true));\r\n
                    el.on("hidden.bs.dropdown", _.bind(onAfterHideMenu, me));\r\n
                    $("button:first", el).on("click", buttonHandler);\r\n
                } else {\r\n
                    el.on("click", buttonHandler);\r\n
                }\r\n
                el.on("button.internal.active", _.bind(doSetActiveState, me));\r\n
                el.on("mouseover", function (e) {\r\n
                    if (!me.disabled) {\r\n
                        me.cmpEl.addClass("over");\r\n
                        me.trigger("mouseover", me, e);\r\n
                    }\r\n
                });\r\n
                el.on("mouseout", function (e) {\r\n
                    if (!me.disabled) {\r\n
                        me.cmpEl.removeClass("over");\r\n
                        me.trigger("mouseout", me, e);\r\n
                    }\r\n
                });\r\n
                Common.UI.ToggleManager.register(me);\r\n
            }\r\n
            me.rendered = true;\r\n
            if (me.pressed) {\r\n
                me.toggle(me.pressed, true);\r\n
            }\r\n
            if (me.disabled) {\r\n
                me.setDisabled(me.disabled);\r\n
            }\r\n
            me.trigger("render:after", me);\r\n
            return this;\r\n
        },\r\n
        doToggle: function () {\r\n
            var me = this;\r\n
            if (me.enableToggle && (me.allowDepress !== false || !me.pressed)) {\r\n
                me.toggle();\r\n
            }\r\n
        },\r\n
        toggle: function (toggle, suppressEvent) {\r\n
            var state = toggle === undefined ? !this.pressed : !!toggle;\r\n
            this.pressed = state;\r\n
            if (this.cmpEl) {\r\n
                this.cmpEl.trigger("button.internal.active", [state]);\r\n
            }\r\n
            if (!suppressEvent) {\r\n
                this.trigger("toggle", this, state);\r\n
            }\r\n
        },\r\n
        isActive: function () {\r\n
            if (this.enableToggle) {\r\n
                return this.pressed;\r\n
            }\r\n
            return this.cmpEl.hasClass("active");\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            if (this.rendered) {\r\n
                var el = this.cmpEl,\r\n
                isGroup = el.hasClass("btn-group");\r\n
                disabled = (disabled === true);\r\n
                if (disabled !== el.hasClass("disabled")) {\r\n
                    var decorateBtn = function (button) {\r\n
                        button.toggleClass("disabled", disabled);\r\n
                        (disabled) ? button.attr({\r\n
                            disabled: disabled\r\n
                        }) : button.removeAttr("disabled");\r\n
                    };\r\n
                    decorateBtn(el);\r\n
                    isGroup && decorateBtn(el.children("button"));\r\n
                }\r\n
                if (disabled) {\r\n
                    var tip = this.cmpEl.data("bs.tooltip");\r\n
                    if (tip) {\r\n
                        tip.hide();\r\n
                    }\r\n
                }\r\n
            }\r\n
            this.disabled = disabled;\r\n
        },\r\n
        isDisabled: function () {\r\n
            return this.disabled;\r\n
        },\r\n
        setIconCls: function (cls) {\r\n
            var btnIconEl = $(this.el).find("span.btn-icon"),\r\n
            oldCls = this.iconCls;\r\n
            this.iconCls = cls;\r\n
            btnIconEl.removeClass(oldCls);\r\n
            btnIconEl.addClass(cls || "");\r\n
        },\r\n
        setVisible: function (visible) {\r\n
            this.cmpEl.toggleClass("hidden", !visible);\r\n
        },\r\n
        updateHint: function (hint) {\r\n
            this.options.hint = hint;\r\n
            var cmpEl = this.cmpEl,\r\n
            modalParents = cmpEl.closest(".asc-window");\r\n
            cmpEl.attr("data-toggle", "tooltip");\r\n
            cmpEl.tooltip("destroy").tooltip({\r\n
                title: hint,\r\n
                placement: this.options.hintAnchor || "cursor"\r\n
            });\r\n
            if (modalParents.length > 0) {\r\n
                cmpEl.data("bs.tooltip").tip().css("z-index", parseInt(modalParents.css("z-index")) + 10);\r\n
            }\r\n
        },\r\n
        setCaption: function (caption) {\r\n
            if (this.caption != caption) {\r\n
                this.caption = caption;\r\n
                if (this.rendered) {\r\n
                    var captionNode = this.cmpEl.find("button:first > .caption").andSelf().filter("button > .caption");\r\n
                    if (captionNode.length > 0) {\r\n
                        captionNode.text(caption);\r\n
                    } else {\r\n
                        this.cmpEl.find("button:first").andSelf().filter("button").text(caption);\r\n
                    }\r\n
                }\r\n
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
            <value> <int>14607</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
