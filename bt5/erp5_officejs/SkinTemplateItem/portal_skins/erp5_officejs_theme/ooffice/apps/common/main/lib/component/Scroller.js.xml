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
            <value> <string>ts44308800.44</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Scroller.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>﻿/*\r\n
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
define(["jmousewheel", "perfectscrollbar", "common/main/lib/component/BaseView"], function () {\r\n
    Common.UI.Scroller = (function () {\r\n
        var mouseCapture;\r\n
        return _.extend(Common.UI.BaseView.extend({\r\n
            options: {\r\n
                wheelSpeed: 20,\r\n
                wheelPropagation: false,\r\n
                minScrollbarLength: null,\r\n
                useBothWheelAxes: false,\r\n
                useKeyboard: true,\r\n
                suppressScrollX: false,\r\n
                suppressScrollY: false,\r\n
                scrollXMarginOffset: 5,\r\n
                scrollYMarginOffset: 5,\r\n
                includePadding: true,\r\n
                includeMargin: true,\r\n
                alwaysVisibleX: false,\r\n
                alwaysVisibleY: false\r\n
            },\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                if (this.options.el) {\r\n
                    this.render();\r\n
                }\r\n
            },\r\n
            render: function () {\r\n
                var me = this;\r\n
                me.cmpEl = $(this.el);\r\n
                if (!me.rendered) {\r\n
                    me.cmpEl.perfectScrollbar(_.extend({},\r\n
                    me.options));\r\n
                    me.rendered = true;\r\n
                    this.setAlwaysVisibleX(me.options.alwaysVisibleX);\r\n
                    this.setAlwaysVisibleY(me.options.alwaysVisibleY);\r\n
                }\r\n
                return this;\r\n
            },\r\n
            remove: function () {\r\n
                this.destroy();\r\n
                Backbone.View.prototype.remove.call(this);\r\n
            },\r\n
            update: function (config) {\r\n
                var options = this.options;\r\n
                if (config) {\r\n
                    this.destroy();\r\n
                    options = _.extend(this.options, config);\r\n
                    this.cmpEl.perfectScrollbar(options);\r\n
                } else {\r\n
                    this.cmpEl.perfectScrollbar("update");\r\n
                }\r\n
                this.setAlwaysVisibleX(options.alwaysVisibleX);\r\n
                this.setAlwaysVisibleY(options.alwaysVisibleY);\r\n
                var mouseDownHandler = function (e) {\r\n
                    mouseCapture = true;\r\n
                    var upHandler = function (e) {\r\n
                        $(document).unbind("mouseup", upHandler);\r\n
                        _.delay(function () {\r\n
                            mouseCapture = false;\r\n
                        },\r\n
                        10);\r\n
                    };\r\n
                    $(document).mouseup(upHandler);\r\n
                };\r\n
                $(".ps-scrollbar-x-rail, .ps-scrollbar-y-rail, .ps-scrollbar-x, .ps-scrollbar-y", this.cmpEl).off("mousedown", mouseDownHandler).on("mousedown", mouseDownHandler);\r\n
            },\r\n
            destroy: function () {\r\n
                this.cmpEl.perfectScrollbar("destroy");\r\n
            },\r\n
            scrollLeft: function (pos) {\r\n
                this.cmpEl.scrollLeft(pos);\r\n
                this.update();\r\n
            },\r\n
            scrollTop: function (pos) {\r\n
                this.cmpEl.scrollTop(pos);\r\n
                this.update();\r\n
            },\r\n
            getScrollTop: function () {\r\n
                return this.cmpEl.scrollTop();\r\n
            },\r\n
            getScrollLeft: function () {\r\n
                return this.cmpEl.scrollLeft();\r\n
            },\r\n
            setAlwaysVisibleX: function (flag) {\r\n
                if (flag) {\r\n
                    $(this.el).find(".ps-scrollbar-x-rail").addClass("always-visible-x");\r\n
                    $(this.el).find(".ps-scrollbar-x").addClass("always-visible-x");\r\n
                } else {\r\n
                    $(this.el).find(".ps-scrollbar-x-rail").removeClass("always-visible-x");\r\n
                    $(this.el).find(".ps-scrollbar-x").addClass("always-visible-x");\r\n
                }\r\n
            },\r\n
            setAlwaysVisibleY: function (flag) {\r\n
                if (flag) {\r\n
                    $(this.el).find(".ps-scrollbar-y-rail").addClass("always-visible-y");\r\n
                    $(this.el).find(".ps-scrollbar-y").addClass("always-visible-y");\r\n
                } else {\r\n
                    $(this.el).find(".ps-scrollbar-y-rail").removeClass("always-visible-y");\r\n
                    $(this.el).find(".ps-scrollbar-y").addClass("always-visible-y");\r\n
                }\r\n
            }\r\n
        }), {\r\n
            isMouseCapture: function () {\r\n
                return mouseCapture;\r\n
            }\r\n
        });\r\n
    })();\r\n
});</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6168</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
