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
            <value> <string>ts44308799.91</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Menu.js</string> </value>
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
define(["common/main/lib/extend/Bootstrap", "common/main/lib/component/BaseView", "common/main/lib/component/MenuItem", "common/main/lib/component/Scroller"], function () {\r\n
    Common.UI.Menu = (function () {\r\n
        var manager = (function () {\r\n
            var active = [],\r\n
            menus = {};\r\n
            return {\r\n
                register: function (menu) {\r\n
                    menus[menu.id] = menu;\r\n
                    menu.on("show:after", function (m) {\r\n
                        active.push(m);\r\n
                    }).on("hide:after", function (m) {\r\n
                        var index = active.indexOf(m);\r\n
                        if (index > -1) {\r\n
                            active.splice(index, 1);\r\n
                        }\r\n
                    });\r\n
                },\r\n
                unregister: function (menu) {\r\n
                    var index = active.indexOf(menu);\r\n
                    delete menus[menu.id];\r\n
                    if (index > -1) {\r\n
                        active.splice(index, 1);\r\n
                    }\r\n
                    menu.off("show:after").off("hide:after");\r\n
                },\r\n
                hideAll: function () {\r\n
                    Common.NotificationCenter.trigger("menumanager:hideall");\r\n
                    if (active && active.length > 0) {\r\n
                        _.each(active, function (menu) {\r\n
                            menu.hide();\r\n
                        });\r\n
                        return true;\r\n
                    }\r\n
                    return false;\r\n
                }\r\n
            };\r\n
        })();\r\n
        return _.extend(Common.UI.BaseView.extend({\r\n
            options: {\r\n
                cls: "",\r\n
                style: "",\r\n
                itemTemplate: null,\r\n
                items: [],\r\n
                menuAlign: "tl-bl",\r\n
                menuAlignEl: null,\r\n
                offset: [0, 0]\r\n
            },\r\n
            template: _.template([\'<ul class="dropdown-menu <%= options.cls %>" style="<%= options.style %>" role="menu"></ul>\'].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                var me = this;\r\n
                this.id = this.options.id || Common.UI.getId();\r\n
                this.itemTemplate = this.options.itemTemplate || Common.UI.MenuItem.prototype.template;\r\n
                this.rendered = false;\r\n
                this.items = [];\r\n
                this.offset = [0, 0];\r\n
                this.menuAlign = this.options.menuAlign;\r\n
                this.menuAlignEl = this.options.menuAlignEl;\r\n
                _.each(this.options.items, function (item) {\r\n
                    if (item instanceof Common.UI.MenuItem) {\r\n
                        me.items.push(item);\r\n
                    } else {\r\n
                        me.items.push(new Common.UI.MenuItem(_.extend({\r\n
                            tagName: "li",\r\n
                            template: me.itemTemplate\r\n
                        },\r\n
                        item)));\r\n
                    }\r\n
                });\r\n
                if (this.options.el) {\r\n
                    this.render();\r\n
                }\r\n
                manager.register(this);\r\n
            },\r\n
            remove: function () {\r\n
                manager.unregister(this);\r\n
                Common.UI.BaseView.prototype.remove.call(this);\r\n
            },\r\n
            render: function (parentEl) {\r\n
                var me = this;\r\n
                this.trigger("render:before", this);\r\n
                this.cmpEl = $(this.el);\r\n
                if (parentEl) {\r\n
                    this.setElement(parentEl, false);\r\n
                    if (!me.rendered) {\r\n
                        this.cmpEl = $(this.template({\r\n
                            options: me.options\r\n
                        }));\r\n
                        parentEl.append(this.cmpEl);\r\n
                    }\r\n
                } else {\r\n
                    if (!me.rendered) {\r\n
                        this.cmpEl = this.template({\r\n
                            options: me.options\r\n
                        });\r\n
                        $(this.el).append(this.cmpEl);\r\n
                    }\r\n
                }\r\n
                var rootEl = this.cmpEl.parent(),\r\n
                menuRoot = (rootEl.attr("role") === "menu") ? rootEl : rootEl.find("[role=menu]");\r\n
                if (menuRoot) {\r\n
                    if (!me.rendered) {\r\n
                        _.each(me.items || [], function (item) {\r\n
                            menuRoot.append(item.render().el);\r\n
                            item.on("click", _.bind(me.onItemClick, me));\r\n
                            item.on("toggle", _.bind(me.onItemToggle, me));\r\n
                        });\r\n
                    }\r\n
                    menuRoot.css({\r\n
                        "max-height": me.options.maxHeight || "none",\r\n
                        position: "fixed",\r\n
                        right: "auto",\r\n
                        left: -1000,\r\n
                        top: -1000\r\n
                    });\r\n
                    this.parentEl = menuRoot.parent();\r\n
                    this.parentEl.on("show.bs.dropdown", _.bind(me.onBeforeShowMenu, me));\r\n
                    this.parentEl.on("shown.bs.dropdown", _.bind(me.onAfterShowMenu, me));\r\n
                    this.parentEl.on("hide.bs.dropdown", _.bind(me.onBeforeHideMenu, me));\r\n
                    this.parentEl.on("hidden.bs.dropdown", _.bind(me.onAfterHideMenu, me));\r\n
                    this.parentEl.on("keydown.after.bs.dropdown", _.bind(me.onAfterKeydownMenu, me));\r\n
                    menuRoot.on("scroll", _.bind(me.onScroll, me));\r\n
                    menuRoot.hover(function (e) {\r\n
                        me.isOver = true;\r\n
                    },\r\n
                    function (e) {\r\n
                        me.isOver = false;\r\n
                    });\r\n
                }\r\n
                this.rendered = true;\r\n
                this.trigger("render:after", this);\r\n
                return this;\r\n
            },\r\n
            isVisible: function () {\r\n
                return this.rendered && (this.cmpEl.is(":visible"));\r\n
            },\r\n
            show: function () {\r\n
                if (this.rendered && this.parentEl && !this.parentEl.hasClass("open")) {\r\n
                    this.cmpEl.dropdown("toggle");\r\n
                }\r\n
            },\r\n
            hide: function () {\r\n
                if (this.rendered && this.parentEl && this.parentEl.hasClass("open")) {\r\n
                    this.cmpEl.dropdown("toggle");\r\n
                }\r\n
            },\r\n
            insertItem: function (index, item) {\r\n
                var me = this,\r\n
                el = this.cmpEl;\r\n
                if (! (item instanceof Common.UI.MenuItem)) {\r\n
                    item = new Common.UI.MenuItem(_.extend({\r\n
                        tagName: "li",\r\n
                        template: me.itemTemplate\r\n
                    },\r\n
                    item));\r\n
                }\r\n
                if (index < 0 || index >= me.items.length) {\r\n
                    me.items.push(item);\r\n
                } else {\r\n
                    me.items.splice(index, 0, item);\r\n
                }\r\n
                if (this.rendered) {\r\n
                    var menuRoot = (el.attr("role") === "menu") ? el : el.find("[role=menu]");\r\n
                    if (menuRoot) {\r\n
                        if (index < 0) {\r\n
                            menuRoot.append(item.render().el);\r\n
                        } else {\r\n
                            if (index === 0) {\r\n
                                menuRoot.prepend(item.render().el);\r\n
                            } else {\r\n
                                $("li:nth-child(" + index + ")", menuRoot).before(item.render().el);\r\n
                            }\r\n
                        }\r\n
                        item.on("click", _.bind(me.onItemClick, me));\r\n
                        item.on("toggle", _.bind(me.onItemToggle, me));\r\n
                    }\r\n
                }\r\n
            },\r\n
            doLayout: function () {\r\n
                if (this.options.maxHeight > 0) {\r\n
                    if (!this.rendered) {\r\n
                        this.mustLayout = true;\r\n
                        return;\r\n
                    }\r\n
                    var me = this,\r\n
                    el = this.cmpEl;\r\n
                    var menuRoot = (el.attr("role") === "menu") ? el : el.find("[role=menu]");\r\n
                    if (!menuRoot.is(":visible")) {\r\n
                        var pos = [menuRoot.css("left"), menuRoot.css("top")];\r\n
                        menuRoot.css({\r\n
                            left: "-1000px",\r\n
                            top: "-1000px",\r\n
                            display: "block"\r\n
                        });\r\n
                    }\r\n
                    var $items = menuRoot.find("li");\r\n
                    if ($items.height() * $items.length > this.options.maxHeight) {\r\n
                        var scroll = \'<div class="menu-scroll top"></div>\';\r\n
                        menuRoot.prepend(scroll);\r\n
                        scroll = \'<div class="menu-scroll bottom"></div>\';\r\n
                        menuRoot.append(scroll);\r\n
                        menuRoot.css({\r\n
                            "box-shadow": "none",\r\n
                            "overflow-y": "hidden",\r\n
                            "padding-top": "18px"\r\n
                        });\r\n
                        menuRoot.find("> li:last-of-type").css("margin-bottom", 18);\r\n
                        var addEvent = function (elem, type, fn) {\r\n
                            elem.addEventListener ? elem.addEventListener(type, fn, false) : elem.attachEvent("on" + type, fn);\r\n
                        };\r\n
                        var eventname = (/Firefox/i.test(navigator.userAgent)) ? "DOMMouseScroll" : "mousewheel";\r\n
                        addEvent(menuRoot[0], eventname, _.bind(this.onMouseWheel, this));\r\n
                        menuRoot.find(".menu-scroll").on("click", _.bind(this.onScrollClick, this));\r\n
                    }\r\n
                    if (pos) {\r\n
                        menuRoot.css({\r\n
                            display: "",\r\n
                            left: pos[0],\r\n
                            top: pos[1]\r\n
                        });\r\n
                    }\r\n
                }\r\n
            },\r\n
            addItem: function (item) {\r\n
                this.insertItem(-1, item);\r\n
            },\r\n
            removeItem: function (item) {\r\n
                var me = this,\r\n
                index = me.items.indexOf(item);\r\n
                if (index > -1) {\r\n
                    me.items.splice(index, 1);\r\n
                    item.off("click").off("toggle");\r\n
                    item.remove();\r\n
                }\r\n
            },\r\n
            removeAll: function () {\r\n
                var me = this;\r\n
                _.each(me.items, function (item) {\r\n
                    item.off("click").off("toggle");\r\n
                    item.remove();\r\n
                });\r\n
                me.items = [];\r\n
            },\r\n
            onBeforeShowMenu: function (e) {\r\n
                if (this.mustLayout) {\r\n
                    delete this.mustLayout;\r\n
                    this.doLayout.call(this);\r\n
                }\r\n
                this.trigger("show:before", this, e);\r\n
                this.alignPosition();\r\n
            },\r\n
            onAfterShowMenu: function (e) {\r\n
                this.trigger("show:after", this, e);\r\n
                if (this.$el.find("> ul > .menu-scroll").length) {\r\n
                    var el = this.$el.find("li .checked")[0];\r\n
                    if (el) {\r\n
                        var offset = el.offsetTop - this.options.maxHeight / 2;\r\n
                        this.scrollMenu(offset < 0 ? 0 : offset);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onBeforeHideMenu: function (e) {\r\n
                this.trigger("hide:before", this, e);\r\n
                if (Common.UI.Scroller.isMouseCapture()) {\r\n
                    e.preventDefault();\r\n
                }\r\n
            },\r\n
            onAfterHideMenu: function (e) {\r\n
                this.trigger("hide:after", this, e);\r\n
            },\r\n
            onAfterKeydownMenu: function (e) {\r\n
                if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                    var li = $(e.target).closest("li");\r\n
                    if (li.length <= 0) {\r\n
                        li = $(e.target).parent().find("li .dataview");\r\n
                    }\r\n
                    if (li.length > 0) {\r\n
                        li.click();\r\n
                    }\r\n
                } else {\r\n
                    if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN) {\r\n
                        this.fromKeyDown = true;\r\n
                    }\r\n
                }\r\n
            },\r\n
            onScroll: function (item, e) {\r\n
                if (this.fromKeyDown) {\r\n
                    var menuRoot = (this.cmpEl.attr("role") === "menu") ? this.cmpEl : this.cmpEl.find("[role=menu]");\r\n
                    menuRoot.find(".menu-scroll.top").css("top", menuRoot.scrollTop() + "px");\r\n
                    menuRoot.find(".menu-scroll.bottom").css("bottom", (-menuRoot.scrollTop()) + "px");\r\n
                }\r\n
            },\r\n
            onItemClick: function (item, e) {\r\n
                if (!item.menu) {\r\n
                    this.isOver = false;\r\n
                }\r\n
                if (item.options.stopPropagation) {\r\n
                    e.stopPropagation();\r\n
                    var me = this;\r\n
                    _.delay(function () {\r\n
                        me.$el.parent().parent().find("[data-toggle=dropdown]").focus();\r\n
                    },\r\n
                    10);\r\n
                    return;\r\n
                }\r\n
                this.trigger("item:click", this, item, e);\r\n
            },\r\n
            onItemToggle: function (item, state, e) {\r\n
                this.trigger("item:toggle", this, item, state, e);\r\n
            },\r\n
            onScrollClick: function (e) {\r\n
                this.scrollMenu(/top/.test(e.currentTarget.className));\r\n
                return false;\r\n
            },\r\n
            onMouseWheel: function (e) {\r\n
                this.scrollMenu(((e.detail && -e.detail) || e.wheelDelta) > 0);\r\n
            },\r\n
            scrollMenu: function (up) {\r\n
                this.fromKeyDown = false;\r\n
                var menuRoot = (this.cmpEl.attr("role") === "menu") ? this.cmpEl : this.cmpEl.find("[role=menu]"),\r\n
                value = typeof(up) === "boolean" ? menuRoot.scrollTop() + (up ? -20 : 20) : up;\r\n
                menuRoot.scrollTop(value);\r\n
                menuRoot.find(".menu-scroll.top").css("top", menuRoot.scrollTop() + "px");\r\n
                menuRoot.find(".menu-scroll.bottom").css("bottom", (-menuRoot.scrollTop()) + "px");\r\n
            },\r\n
            setOffset: function (offsetX, offsetY) {\r\n
                this.offset[0] = _.isUndefined(offsetX) ? this.offset[0] : offsetX;\r\n
                this.offset[1] = _.isUndefined(offsetY) ? this.offset[1] : offsetY;\r\n
                this.alignPosition();\r\n
            },\r\n
            getOffset: function () {\r\n
                return this.offset;\r\n
            },\r\n
            alignPosition: function () {\r\n
                var menuRoot = (this.cmpEl.attr("role") === "menu") ? this.cmpEl : this.cmpEl.find("[role=menu]"),\r\n
                menuParent = this.menuAlignEl || menuRoot.parent(),\r\n
                m = this.menuAlign.match(/^([a-z]+)-([a-z]+)/),\r\n
                offset = menuParent.offset(),\r\n
                docW = Math.min($(document).width(), $("body").width()),\r\n
                docH = $(document).height() - 10,\r\n
                menuW = menuRoot.outerWidth(),\r\n
                menuH = menuRoot.outerHeight(),\r\n
                parentW = menuParent.outerWidth(),\r\n
                parentH = menuParent.outerHeight();\r\n
                var posMenu = {\r\n
                    "tl": [0, 0],\r\n
                    "bl": [0, menuH],\r\n
                    "tr": [menuW, 0],\r\n
                    "br": [menuW, menuH]\r\n
                };\r\n
                var posParent = {\r\n
                    "tl": [0, 0],\r\n
                    "tr": [parentW, 0],\r\n
                    "bl": [0, parentH],\r\n
                    "br": [parentW, parentH]\r\n
                };\r\n
                var left = offset.left - posMenu[m[1]][0] + posParent[m[2]][0] + this.offset[0];\r\n
                var top = offset.top - posMenu[m[1]][1] + posParent[m[2]][1] + this.offset[1];\r\n
                if (left + menuW > docW) {\r\n
                    if (menuParent.is("li.dropdown-submenu")) {\r\n
                        left = offset.left - menuW + 2;\r\n
                    } else {\r\n
                        left = docW - menuW;\r\n
                    }\r\n
                }\r\n
                if (top + menuH > docH) {\r\n
                    top = docH - menuH;\r\n
                }\r\n
                if (top < 0) {\r\n
                    top = 0;\r\n
                }\r\n
                menuRoot.css({\r\n
                    left: left,\r\n
                    top: top\r\n
                });\r\n
            }\r\n
        }), {\r\n
            Manager: (function () {\r\n
                return manager;\r\n
            })()\r\n
        });\r\n
    })();\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>18820</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
