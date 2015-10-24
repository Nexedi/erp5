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
            <value> <string>ts44308800.87</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>TabBar.js</string> </value>
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
 define(["common/main/lib/component/BaseView", "common/main/lib/component/Tab"], function () {\r\n
    var Events = {\r\n
        bind: function () {\r\n
            if (!this.o) {\r\n
                this.o = $({});\r\n
            }\r\n
            this.o.on.apply(this.o, arguments);\r\n
        },\r\n
        unbind: function () {\r\n
            if (this.o) {\r\n
                this.o.off.apply(this.o, arguments);\r\n
            }\r\n
        },\r\n
        trigger: function () {\r\n
            if (!this.o) {\r\n
                this.o = $({});\r\n
            }\r\n
            this.o.trigger.apply(this.o, arguments);\r\n
        }\r\n
    };\r\n
    var StateManager = function (options) {\r\n
        this.initialize.call(this, options);\r\n
    };\r\n
    _.extend(StateManager.prototype, Events);\r\n
    StateManager.prototype.initialize = function (options) {\r\n
        this.bar = options.bar;\r\n
    };\r\n
    StateManager.prototype.attach = function (tab) {\r\n
        tab.changeState = $.proxy(function () {\r\n
            this.trigger("tab:change", tab);\r\n
            this.bar.$el.find("ul > li.active").removeClass("active");\r\n
            tab.activate();\r\n
            this.bar.trigger("tab:changed", this.bar, this.bar.tabs.indexOf(tab), tab);\r\n
        },\r\n
        this);\r\n
        var dragHelper = new(function () {\r\n
            return {\r\n
                bounds: [],\r\n
                drag: undefined,\r\n
                calculateBounds: function () {\r\n
                    var me = this,\r\n
                    length = me.bar.tabs.length,\r\n
                    barBounds = me.bar.$bar.get(0).getBoundingClientRect();\r\n
                    if (barBounds) {\r\n
                        me.bounds = [];\r\n
                        me.scrollLeft = me.bar.$bar.scrollLeft();\r\n
                        me.bar.scrollX = this.scrollLeft;\r\n
                        for (var i = 0; i < length; ++i) {\r\n
                            this.bounds.push(me.bar.tabs[i].$el.get(0).getBoundingClientRect());\r\n
                        }\r\n
                        me.tabBarLeft = me.bounds[0].left;\r\n
                        me.tabBarRight = me.bounds[length - 1].right;\r\n
                        me.tabBarRight = Math.min(me.tabBarRight, barBounds.right - 1);\r\n
                    }\r\n
                },\r\n
                setAbsTabs: function () {\r\n
                    var me = this,\r\n
                    tab = null,\r\n
                    length = this.bounds.length;\r\n
                    for (var i = 0; i < length; ++i) {\r\n
                        tab = me.bar.tabs[i].$el;\r\n
                        tab.css("position", "absolute");\r\n
                        tab.css("left", (me.bounds[i].left - me.tabBarLeft - this.scrollLeft) + "px");\r\n
                        if (tab.hasClass("active")) {\r\n
                            tab.css("top", "1px");\r\n
                        } else {\r\n
                            tab.css("top", "0px");\r\n
                        }\r\n
                    }\r\n
                },\r\n
                updatePositions: function () {\r\n
                    this.drag.place = undefined;\r\n
                    var i, tabBound, center, place = -1,\r\n
                    next = -this.scrollLeft,\r\n
                    tabsCount = this.bounds.length,\r\n
                    dragBound = this.drag.tab.$el.get(0).getBoundingClientRect();\r\n
                    if (this.drag.moveX - this.drag.mouseX > 0) {\r\n
                        for (i = tabsCount - 1; i >= 0; --i) {\r\n
                            tabBound = this.bounds[i];\r\n
                            center = (tabBound.right + tabBound.left) * 0.5;\r\n
                            if (dragBound.left < center && center < dragBound.right) {\r\n
                                place = i;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (-1 === place) {\r\n
                            for (i = tabsCount - 1; i >= 0; --i) {\r\n
                                tabBound = dragBound;\r\n
                                center = (tabBound.right + tabBound.left) * 0.5;\r\n
                                if (this.bounds[i].left < center && center < this.bounds[i].right) {\r\n
                                    place = i;\r\n
                                    break;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    } else {\r\n
                        for (i = 0; i < tabsCount; ++i) {\r\n
                            tabBound = this.bounds[i];\r\n
                            center = (tabBound.right + tabBound.left) * 0.5;\r\n
                            if (dragBound.left < center && center < dragBound.right) {\r\n
                                place = i;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (-1 === place) {\r\n
                            for (i = 0; i < tabsCount; ++i) {\r\n
                                tabBound = dragBound;\r\n
                                center = (tabBound.right + tabBound.left) * 0.5;\r\n
                                if (this.bounds[i].left < center && center < this.bounds[i].right) {\r\n
                                    place = i;\r\n
                                    break;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    if (-1 !== place) {\r\n
                        this.drag.place = place;\r\n
                        for (i = 0; i < tabsCount; ++i) {\r\n
                            if (i === place) {\r\n
                                if (place < this.drag.index) {\r\n
                                    next += this.drag.tabWidth;\r\n
                                }\r\n
                            }\r\n
                            if (place > this.drag.index) {\r\n
                                if (i === place + 1) {\r\n
                                    next += this.drag.tabWidth;\r\n
                                }\r\n
                            }\r\n
                            if (i !== this.drag.index) {\r\n
                                this.bar.tabs[i].$el.css("left", next + "px");\r\n
                            } else {\r\n
                                if (this.drag.index === place) {\r\n
                                    next += this.drag.tabWidth;\r\n
                                }\r\n
                                continue;\r\n
                            }\r\n
                            next += this.bounds[i].width;\r\n
                        }\r\n
                    }\r\n
                },\r\n
                setHook: function (e, bar, tab) {\r\n
                    var me = this;\r\n
                    function dragComplete() {\r\n
                        if (!_.isUndefined(me.drag)) {\r\n
                            me.drag.tab.$el.css("z-index", "");\r\n
                            var tab = null;\r\n
                            for (var i = me.bar.tabs.length - 1; i >= 0; --i) {\r\n
                                tab = me.bar.tabs[i].$el;\r\n
                                if (tab) {\r\n
                                    tab.css("top", "");\r\n
                                    tab.css("position", "");\r\n
                                    tab.css("left", "");\r\n
                                }\r\n
                            }\r\n
                            if (!_.isUndefined(me.drag.place)) {\r\n
                                me.bar.trigger("tab:move", me.drag.index, me.drag.place);\r\n
                                me.bar.$bar.scrollLeft(me.scrollLeft);\r\n
                                me.bar.scrollX = undefined;\r\n
                            } else {\r\n
                                me.bar.trigger("tab:move", me.drag.index);\r\n
                                me.bar.$bar.scrollLeft(me.scrollLeft);\r\n
                                me.bar.scrollX = undefined;\r\n
                            }\r\n
                            me.drag = undefined;\r\n
                        }\r\n
                    }\r\n
                    function dragMove(e) {\r\n
                        if (!_.isUndefined(me.drag)) {\r\n
                            me.drag.moveX = e.clientX;\r\n
                            var leftPos = Math.max(e.clientX - me.drag.anchorX - me.tabBarLeft - me.scrollLeft, 0);\r\n
                            leftPos = Math.min(leftPos, me.tabBarRight - me.tabBarLeft - me.drag.tabWidth - me.scrollLeft);\r\n
                            me.drag.tab.$el.css("left", leftPos + "px");\r\n
                            me.drag.tab.$el.css("z-index", "100");\r\n
                            me.updatePositions();\r\n
                        }\r\n
                    }\r\n
                    function dragDropText(e) {\r\n
                        e.preventDefault();\r\n
                    }\r\n
                    if (!_.isUndefined(bar) && !_.isUndefined(tab) && bar.tabs.length > 1) {\r\n
                        var index = bar.tabs.indexOf(tab);\r\n
                        me.bar = bar;\r\n
                        me.drag = {\r\n
                            tab: tab,\r\n
                            index: index\r\n
                        };\r\n
                        this.calculateBounds();\r\n
                        this.setAbsTabs();\r\n
                        me.drag.moveX = e.clientX;\r\n
                        me.drag.mouseX = e.clientX;\r\n
                        me.drag.anchorX = e.clientX - this.bounds[index].left;\r\n
                        me.drag.tabWidth = this.bounds[index].width;\r\n
                        document.addEventListener("dragstart", dragDropText);\r\n
                        $(document).on("mousemove", dragMove);\r\n
                        $(document).on("mouseup", function (e) {\r\n
                            dragComplete(e);\r\n
                            $(document).off("mouseup", dragComplete);\r\n
                            $(document).off("mousemove", dragMove);\r\n
                            document.removeEventListener("dragstart", dragDropText);\r\n
                        });\r\n
                    }\r\n
                }\r\n
            };\r\n
        });\r\n
        tab.$el.on({\r\n
            click: $.proxy(function () {\r\n
                if (!tab.disabled && !tab.$el.hasClass("active")) {\r\n
                    if (tab.control == "manual") {\r\n
                        this.bar.trigger("tab:manual", this.bar, this.bar.tabs.indexOf(tab), tab);\r\n
                    } else {\r\n
                        tab.changeState();\r\n
                    }\r\n
                }\r\n
            },\r\n
            this),\r\n
            dblclick: $.proxy(function () {\r\n
                this.trigger("tab:dblclick", this, this.tabs.indexOf(tab), tab);\r\n
            },\r\n
            this.bar),\r\n
            contextmenu: $.proxy(function () {\r\n
                this.trigger("tab:contextmenu", this, this.tabs.indexOf(tab), tab);\r\n
            },\r\n
            this.bar),\r\n
            mousedown: $.proxy(function (e) {\r\n
                if (this.bar.options.draggable && !_.isUndefined(dragHelper) && (3 !== e.which)) {\r\n
                    if (!tab.isLockTheDrag) {\r\n
                        dragHelper.setHook(e, this.bar, tab);\r\n
                    }\r\n
                }\r\n
            },\r\n
            this)\r\n
        });\r\n
    };\r\n
    StateManager.prototype.detach = function (tab) {\r\n
        tab.$el.off();\r\n
    };\r\n
    Common.UI.TabBar = Common.UI.BaseView.extend({\r\n
        config: {\r\n
            placement: "top",\r\n
            items: [],\r\n
            draggable: false\r\n
        },\r\n
        tabs: [],\r\n
        template: _.template(\'<ul class="nav nav-tabs <%= placement %>" />\'),\r\n
        initialize: function (options) {\r\n
            _.extend(this.config, options);\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            this.saved = [];\r\n
        },\r\n
        render: function () {\r\n
            this.$el.html(this.template(this.config));\r\n
            this.$bar = this.$el.find("ul");\r\n
            var addEvent = function (elem, type, fn) {\r\n
                elem.addEventListener ? elem.addEventListener(type, fn, false) : elem.attachEvent("on" + type, fn);\r\n
            };\r\n
            var eventname = (/Firefox/i.test(navigator.userAgent)) ? "DOMMouseScroll" : "mousewheel";\r\n
            addEvent(this.$bar[0], eventname, _.bind(this._onMouseWheel, this));\r\n
            this.manager = new StateManager({\r\n
                bar: this\r\n
            });\r\n
            this.insert(-1, this.config.items);\r\n
            this.insert(-1, this.saved);\r\n
            delete this.saved;\r\n
            this.rendered = true;\r\n
            return this;\r\n
        },\r\n
        _onMouseWheel: function (e) {\r\n
            var hidden = this.checkInvisible(true),\r\n
            forward = ((e.detail && -e.detail) || e.wheelDelta) > 0;\r\n
            if (forward) {\r\n
                if (hidden.last) {\r\n
                    this.setTabVisible("forward");\r\n
                }\r\n
            } else {\r\n
                if (hidden.first) {\r\n
                    this.setTabVisible("backward");\r\n
                }\r\n
            }\r\n
        },\r\n
        add: function (tabs) {\r\n
            return this.insert(-1, tabs) > 0;\r\n
        },\r\n
        insert: function (index, tabs) {\r\n
            var count = 0;\r\n
            if (tabs) {\r\n
                if (! (tabs instanceof Array)) {\r\n
                    tabs = [tabs];\r\n
                }\r\n
                if (tabs.length) {\r\n
                    count = tabs.length;\r\n
                    if (this.rendered) {\r\n
                        var me = this,\r\n
                        tab;\r\n
                        if (index < 0 || index > me.tabs.length) {\r\n
                            for (var i = 0; i < tabs.length; i++) {\r\n
                                tab = new Common.UI.Tab(tabs[i]);\r\n
                                me.$bar.append(tab.render().$el);\r\n
                                me.tabs.push(tab);\r\n
                                me.manager.attach(tab);\r\n
                            }\r\n
                        } else {\r\n
                            for (i = tabs.length; i-->0;) {\r\n
                                tab = new Common.UI.Tab(tabs[i]);\r\n
                                if (index === 0) {\r\n
                                    me.$bar.prepend(tab.render().$el);\r\n
                                    me.tabs.unshift(tab);\r\n
                                } else {\r\n
                                    me.$bar.find("li:nth-child(" + index + ")").before(tab.render().$el);\r\n
                                    me.tabs.splice(index, 0, tab);\r\n
                                }\r\n
                                me.manager.attach(tab);\r\n
                            }\r\n
                        }\r\n
                    } else {\r\n
                        this.saved.push(tabs);\r\n
                    }\r\n
                    this.checkInvisible();\r\n
                }\r\n
            }\r\n
            return count;\r\n
        },\r\n
        remove: function (index) {\r\n
            if (index >= 0 && index < this.tabs.length) {\r\n
                var tab = this.tabs.splice(index, 1)[0];\r\n
                this.manager.detach(tab);\r\n
                tab.$el.remove();\r\n
                this.checkInvisible();\r\n
            }\r\n
        },\r\n
        empty: function (suppress) {\r\n
            var me = this;\r\n
            this.tabs.forEach(function (tab) {\r\n
                me.manager.detach(tab);\r\n
            });\r\n
            this.$bar.empty();\r\n
            me.tabs = [];\r\n
            this.checkInvisible(suppress);\r\n
        },\r\n
        setActive: function (t) {\r\n
            if (t instanceof Common.UI.Tab) {\r\n
                tab = t;\r\n
            } else {\r\n
                if (typeof t == "number") {\r\n
                    if (t >= 0 && t < this.tabs.length) {\r\n
                        var tab = this.tabs[t];\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (tab && tab.control != "manual" && !tab.disabled && !tab.$el.hasClass("active")) {\r\n
                tab.changeState();\r\n
            }\r\n
            this.checkInvisible();\r\n
        },\r\n
        getActive: function (iselem) {\r\n
            return iselem ? this.$bar.find("> li.active") : this.$bar.find("> li.active").index();\r\n
        },\r\n
        getAt: function (index) {\r\n
            return (index >= 0 && index < this.tabs.length) ? this.tabs[index] : undefined;\r\n
        },\r\n
        getCount: function () {\r\n
            return this.tabs.length;\r\n
        },\r\n
        addClass: function (cls) {\r\n
            if (cls.length && !this.$bar.hasClass(cls)) {\r\n
                this.$bar.addClass(cls);\r\n
            }\r\n
        },\r\n
        removeClass: function (cls) {\r\n
            if (cls.length && this.$bar.hasClass(cls)) {\r\n
                this.$bar.removeClass(cls);\r\n
            }\r\n
        },\r\n
        hasClass: function (cls) {\r\n
            return this.$bar.hasClass(cls);\r\n
        },\r\n
        setTabVisible: function (index, suppress) {\r\n
            if (index <= 0 || index == "first") {\r\n
                this.$bar.scrollLeft(0);\r\n
                this.checkInvisible(suppress);\r\n
            } else {\r\n
                if (index >= (this.tabs.length - 1) || index == "last") {\r\n
                    var left = this.tabs[this.tabs.length - 1].$el.position().left;\r\n
                    this.$bar.scrollLeft(left);\r\n
                    this.checkInvisible(suppress);\r\n
                } else {\r\n
                    var rightbound = this.$bar.width();\r\n
                    if (index == "forward") {\r\n
                        var tab, right;\r\n
                        for (var i = 0; i < this.tabs.length; i++) {\r\n
                            tab = this.tabs[i].$el;\r\n
                            right = tab.position().left + parseInt(tab.css("width"));\r\n
                            if (right > rightbound) {\r\n
                                this.$bar.scrollLeft(this.$bar.scrollLeft() + (right - rightbound) + 20);\r\n
                                this.checkInvisible(suppress);\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                    } else {\r\n
                        if (index == "backward") {\r\n
                            for (i = this.tabs.length; i-->0;) {\r\n
                                tab = this.tabs[i].$el;\r\n
                                left = tab.position().left;\r\n
                                if (left < 0) {\r\n
                                    this.$bar.scrollLeft(this.$bar.scrollLeft() + left - 26);\r\n
                                    this.checkInvisible(suppress);\r\n
                                    break;\r\n
                                }\r\n
                            }\r\n
                        } else {\r\n
                            if (typeof index == "number") {\r\n
                                tab = this.tabs[index].$el;\r\n
                                left = tab.position().left;\r\n
                                right = left + parseInt(tab.css("width"));\r\n
                                if (left < 0) {\r\n
                                    this.$bar.scrollLeft(this.$bar.scrollLeft() + left - 26);\r\n
                                    this.checkInvisible(suppress);\r\n
                                } else {\r\n
                                    if (right > rightbound) {\r\n
                                        this.$bar.scrollLeft(this.$bar.scrollLeft() + (right - rightbound) + 20);\r\n
                                        this.checkInvisible(suppress);\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        checkInvisible: function (suppress) {\r\n
            var result = {\r\n
                first: !this.isTabVisible(0),\r\n
                last: !this.isTabVisible(this.tabs.length - 1)\r\n
            }; ! suppress && this.fireEvent("tab:invisible", this, result);\r\n
            return result;\r\n
        },\r\n
        hasInvisible: function () {\r\n
            var _left_bound_ = this.$bar.offset().left,\r\n
            _right_bound_ = _left_bound_ + this.$bar.width();\r\n
            for (var i = this.tabs.length; i-->0;) {\r\n
                if (!this.isTabVisible(i, _left_bound_, _right_bound_)) {\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        isTabVisible: function (index) {\r\n
            var leftbound = arguments[1] || this.$bar.offset().left,\r\n
            rightbound = arguments[2] || (leftbound + this.$bar.width()),\r\n
            left,\r\n
            right,\r\n
            tab,\r\n
            rect;\r\n
            if (index < this.tabs.length && index >= 0) {\r\n
                tab = this.tabs[index].$el;\r\n
                rect = tab.get(0).getBoundingClientRect();\r\n
                left = rect.left;\r\n
                right = rect.right;\r\n
                return ! (left < leftbound) && !(right > rightbound);\r\n
            }\r\n
            return false;\r\n
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
            <value> <int>22243</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
