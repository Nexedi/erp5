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
            <value> <string>ts44308799.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Layout.js</string> </value>
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
define(["backbone"], function () {\r\n
    var BaseLayout = function (options) {\r\n
        this.box = null;\r\n
        this.panels = [];\r\n
        _.extend(this, options || {});\r\n
    };\r\n
    var LayoutPanel = function () {\r\n
        return {\r\n
            width: null,\r\n
            height: null,\r\n
            resize: false,\r\n
            stretch: false,\r\n
            rely: false\r\n
        };\r\n
    };\r\n
    _.extend(BaseLayout.prototype, Backbone.Events, {\r\n
        initialize: function (options) {\r\n
            this.$parent = this.box.parent();\r\n
            this.resize = {\r\n
                eventMove: _.bind(this.resizeMove, this),\r\n
                eventStop: _.bind(this.resizeStop, this)\r\n
            };\r\n
            var panel, resizer, stretch = false;\r\n
            options.items.forEach(function (item) {\r\n
                item.el instanceof HTMLElement && (item.el = $(item.el));\r\n
                panel = _.extend(new LayoutPanel(), item);\r\n
                if (panel.stretch) {\r\n
                    stretch = true;\r\n
                    panel.rely = false;\r\n
                    panel.resize = false;\r\n
                }\r\n
                this.panels.push(panel);\r\n
                if (panel.resize) {\r\n
                    resizer = {\r\n
                        isresizer: true,\r\n
                        minpos: panel.resize.min || 0,\r\n
                        maxpos: panel.resize.max || 0\r\n
                    };\r\n
                    if (!stretch) {\r\n
                        panel.resize.el = resizer.el = panel.el.after(\'<div class="layout-resizer after"></div>\').next();\r\n
                        this.panels.push(resizer);\r\n
                    } else {\r\n
                        panel.resize.el = resizer.el = panel.el.before(\'<div class="layout-resizer before"></div>\').prev();\r\n
                        this.panels.splice(this.panels.length - 1, 0, resizer);\r\n
                    }\r\n
                    panel.resize.hidden && resizer.el.hide();\r\n
                }\r\n
            },\r\n
            this);\r\n
        },\r\n
        doLayout: function () {},\r\n
        getElementHeight: function (el) {\r\n
            return parseInt(el.css("height"));\r\n
        },\r\n
        getElementWidth: function (el) {\r\n
            return parseInt(el.css("width"));\r\n
        },\r\n
        onSelectStart: function (e) {\r\n
            if (e.preventDefault) {\r\n
                e.preventDefault();\r\n
            }\r\n
            return false;\r\n
        },\r\n
        addHandler: function (elem, type, handler) {\r\n
            if (elem.addEventListener) {\r\n
                elem.addEventListener(type, handler);\r\n
            } else {\r\n
                if (elem.attachEvent) {\r\n
                    elem.attachEvent("on" + type, handler);\r\n
                } else {\r\n
                    elem["on" + type] = handler;\r\n
                }\r\n
            }\r\n
        },\r\n
        removeHandler: function (elem, type, handler) {\r\n
            if (elem.removeEventListener) {\r\n
                elem.removeEventListener(type, handler);\r\n
            } else {\r\n
                if (elem.detachEvent) {\r\n
                    elem.detachEvent("on" + type, handler);\r\n
                } else {\r\n
                    elem["on" + type] = null;\r\n
                }\r\n
            }\r\n
        },\r\n
        clearSelection: function () {\r\n
            if (window.getSelection) {\r\n
                var selection = window.getSelection();\r\n
                if (selection.empty) {\r\n
                    selection.empty();\r\n
                } else {\r\n
                    if (selection.removeAllRanges) {\r\n
                        selection.removeAllRanges();\r\n
                    }\r\n
                }\r\n
            } else {\r\n
                if (document.selection) {\r\n
                    document.selection.empty();\r\n
                }\r\n
            }\r\n
        },\r\n
        resizeStart: function (e) {\r\n
            this.clearSelection();\r\n
            this.addHandler(window.document, "selectstart", this.onSelectStart);\r\n
            $(document).on({\r\n
                mousemove: this.resize.eventMove,\r\n
                mouseup: this.resize.eventStop\r\n
            });\r\n
            var panel = e.data.panel;\r\n
            this.resize.type = e.data.type;\r\n
            this.resize.$el = panel.el;\r\n
            this.resize.min = panel.minpos;\r\n
            this.resize.$el.addClass("move");\r\n
            if (e.data.type == "vertical") {\r\n
                this.resize.height = parseInt(this.resize.$el.css("height"));\r\n
                this.resize.max = (panel.maxpos > 0 ? panel.maxpos : this.resize.$el.parent().height() + panel.maxpos) - this.resize.height;\r\n
                this.resize.inity = e.pageY - parseInt(e.currentTarget.style.top);\r\n
            } else {\r\n
                if (e.data.type == "horizontal") {\r\n
                    this.resize.width = parseInt(this.resize.$el.css("width"));\r\n
                    this.resize.max = (panel.maxpos > 0 ? panel.maxpos : this.resize.$el.parent().height() + panel.maxpos) - this.resize.width;\r\n
                    this.resize.initx = e.pageX - parseInt(e.currentTarget.style.left);\r\n
                }\r\n
            }\r\n
        },\r\n
        resizeMove: function (e) {\r\n
            if (this.resize.type == "vertical") {\r\n
                var prop = "top",\r\n
                value = e.pageY - this.resize.inity;\r\n
            } else {\r\n
                if (this.resize.type == "horizontal") {\r\n
                    prop = "left";\r\n
                    value = e.pageX - this.resize.initx;\r\n
                }\r\n
            }\r\n
            if (! (value < this.resize.min) && !(value > this.resize.max)) {\r\n
                this.resize.$el[0].style[prop] = value + "px";\r\n
            }\r\n
        },\r\n
        resizeStop: function (e) {\r\n
            this.removeHandler(window.document, "selectstart", this.onSelectStart);\r\n
            $(document).off({\r\n
                mousemove: this.resize.eventMove,\r\n
                mouseup: this.resize.eventStop\r\n
            });\r\n
            if (this.resize.type == "vertical") {\r\n
                var prop = "height";\r\n
                var value = e.pageY - this.resize.inity;\r\n
            } else {\r\n
                if (this.resize.type == "horizontal") {\r\n
                    prop = "width";\r\n
                    value = e.pageX - this.resize.initx;\r\n
                }\r\n
            }\r\n
            value < this.resize.min && (value = this.resize.min);\r\n
            value > this.resize.max && (value = this.resize.max);\r\n
            if (this.resize.$el.hasClass("after")) {\r\n
                var panel = this.resize.$el.prev();\r\n
            } else {\r\n
                panel = this.resize.$el.next();\r\n
                value = panel.parent()[prop]() - (value + this.resize[prop]);\r\n
            }\r\n
            panel.css(prop, value + "px");\r\n
            this.resize.$el.removeClass("move");\r\n
            delete this.resize.$el;\r\n
            if (this.resize.value != value) {\r\n
                this.doLayout();\r\n
                this.trigger("layout:resizedrag", this);\r\n
            }\r\n
        }\r\n
    }); ! Common.UI && (Common.UI = {});\r\n
    Common.UI.VBoxLayout = function (options) {\r\n
        BaseLayout.apply(this, arguments);\r\n
        this.initialize.apply(this, arguments);\r\n
    };\r\n
    Common.UI.VBoxLayout.prototype = _.extend(new BaseLayout(), {\r\n
        initialize: function (options) {\r\n
            BaseLayout.prototype.initialize.call(this, options);\r\n
            this.panels.forEach(function (panel) { ! panel.stretch && !panel.height && (panel.height = this.getElementHeight(panel.el));\r\n
                if (panel.isresizer) {\r\n
                    panel.el.on("mousedown", {\r\n
                        type: "vertical",\r\n
                        panel: panel\r\n
                    },\r\n
                    _.bind(this.resizeStart, this));\r\n
                }\r\n
            },\r\n
            this);\r\n
            this.doLayout.call(this);\r\n
        },\r\n
        doLayout: function () {\r\n
            var height = 0,\r\n
            stretchable, style;\r\n
            this.panels.forEach(function (panel) {\r\n
                if (!panel.stretch) {\r\n
                    style = panel.el.is(":visible");\r\n
                    if (style) {\r\n
                        height += (panel.rely !== true ? panel.height : this.getElementHeight(panel.el));\r\n
                    }\r\n
                    if (panel.resize && panel.resize.autohide !== false && panel.resize.el) {\r\n
                        if (style) {\r\n
                            panel.resize.el.show();\r\n
                            stretchable && (height += panel.resize.height);\r\n
                        } else {\r\n
                            panel.resize.el.hide();\r\n
                            stretchable && (height -= panel.resize.height);\r\n
                        }\r\n
                    }\r\n
                } else {\r\n
                    stretchable = panel;\r\n
                }\r\n
            },\r\n
            this);\r\n
            stretchable && (stretchable.height = this.$parent.height() - height);\r\n
            height = 0;\r\n
            this.panels.forEach(function (panel) {\r\n
                if (panel.el.is(":visible")) {\r\n
                    style = {\r\n
                        top: height\r\n
                    };\r\n
                    panel.rely !== true && (style.height = panel.height);\r\n
                    panel.el.css(style);\r\n
                    height += this.getElementHeight(panel.el);\r\n
                }\r\n
            },\r\n
            this);\r\n
        }\r\n
    });\r\n
    Common.UI.HBoxLayout = function (options) {\r\n
        BaseLayout.apply(this, arguments);\r\n
        this.initialize.apply(this, arguments);\r\n
    };\r\n
    Common.UI.HBoxLayout.prototype = _.extend(new BaseLayout(), {\r\n
        initialize: function (options) {\r\n
            BaseLayout.prototype.initialize.call(this, options);\r\n
            this.panels.forEach(function (panel) { ! panel.stretch && !panel.width && (panel.width = this.getElementWidth(panel.el));\r\n
                if (panel.isresizer) {\r\n
                    panel.el.on("mousedown", {\r\n
                        type: "horizontal",\r\n
                        panel: panel\r\n
                    },\r\n
                    _.bind(this.resizeStart, this));\r\n
                }\r\n
            },\r\n
            this);\r\n
            this.doLayout.call(this);\r\n
        },\r\n
        doLayout: function (event) {\r\n
            var width = 0,\r\n
            stretchable, style;\r\n
            this.panels.forEach(function (panel) {\r\n
                if (!panel.stretch) {\r\n
                    style = panel.el.is(":visible");\r\n
                    if (style) {\r\n
                        width += (panel.rely !== true ? panel.width : this.getElementWidth(panel.el));\r\n
                    }\r\n
                    if (panel.resize && panel.resize.autohide !== false && panel.resize.el) {\r\n
                        if (style) {\r\n
                            panel.resize.el.show();\r\n
                            stretchable && (width -= panel.resize.width);\r\n
                        } else {\r\n
                            panel.resize.el.hide();\r\n
                            stretchable && (width -= panel.resize.width);\r\n
                        }\r\n
                    }\r\n
                } else {\r\n
                    stretchable = panel;\r\n
                }\r\n
            },\r\n
            this);\r\n
            stretchable && (stretchable.width = this.$parent.width() - width);\r\n
            width = 0;\r\n
            this.panels.forEach(function (panel) {\r\n
                if (panel.el.is(":visible")) {\r\n
                    style = {\r\n
                        left: width\r\n
                    };\r\n
                    panel.rely !== true && (style.width = panel.width);\r\n
                    panel.el.css(style);\r\n
                    width += this.getElementWidth(panel.el);\r\n
                }\r\n
            },\r\n
            this);\r\n
        }\r\n
    });\r\n
    Common.UI.VBoxLayout.prototype.constructor = Common.UI.VBoxLayout;\r\n
    Common.UI.HBoxLayout.prototype.constructor = Common.UI.HBoxLayout;\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>13498</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
