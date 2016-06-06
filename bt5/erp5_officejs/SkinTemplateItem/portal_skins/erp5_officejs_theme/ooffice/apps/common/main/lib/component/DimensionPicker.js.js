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
            <value> <string>ts44308799.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DimensionPicker.js</string> </value>
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
define(["common/main/lib/component/BaseView"], function () {\r\n
    Common.UI.DimensionPicker = Common.UI.BaseView.extend((function () {\r\n
        var me, rootEl, areaMouseCatcher, areaUnHighLighted, areaHighLighted, areaStatus, curColumns = 0,\r\n
        curRows = 0;\r\n
        var onMouseMove = function (event) {\r\n
            me.setTableSize(Math.ceil((event.offsetX === undefined ? event.originalEvent.layerX : event.offsetX) / me.itemSize), Math.ceil((event.offsetY === undefined ? event.originalEvent.layerY : event.offsetY) / me.itemSize), event);\r\n
        };\r\n
        var onMouseLeave = function (event) {\r\n
            me.setTableSize(0, 0, event);\r\n
        };\r\n
        var onHighLightedMouseClick = function (e) {\r\n
            me.trigger("select", me, curColumns, curRows, e);\r\n
        };\r\n
        return {\r\n
            options: {\r\n
                itemSize: 18,\r\n
                minRows: 5,\r\n
                minColumns: 5,\r\n
                maxRows: 20,\r\n
                maxColumns: 20\r\n
            },\r\n
            template: _.template([\'<div style="width: 100%; height: 100%;">\', \'<div class="dimension-picker-status">0x0</div>\', \'<div class="dimension-picker-observecontainer">\', \'<div class="dimension-picker-mousecatcher"></div>\', \'<div class="dimension-picker-unhighlighted"></div>\', \'<div class="dimension-picker-highlighted"></div>\', "</div>", "</div>"].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                me = this;\r\n
                rootEl = $(this.el);\r\n
                me.itemSize = me.options.itemSize;\r\n
                me.minRows = me.options.minRows;\r\n
                me.minColumns = me.options.minColumns;\r\n
                me.maxRows = me.options.maxRows;\r\n
                me.maxColumns = me.options.maxColumns;\r\n
                this.render();\r\n
                if (rootEl) {\r\n
                    areaMouseCatcher = rootEl.find(".dimension-picker-mousecatcher");\r\n
                    areaUnHighLighted = rootEl.find(".dimension-picker-unhighlighted");\r\n
                    areaHighLighted = rootEl.find(".dimension-picker-highlighted");\r\n
                    areaStatus = rootEl.find(".dimension-picker-status");\r\n
                    rootEl.css({\r\n
                        width: me.minColumns + "em"\r\n
                    });\r\n
                    areaMouseCatcher.css("z-index", 1);\r\n
                    areaMouseCatcher.width(me.maxColumns + "em").height(me.maxRows + "em");\r\n
                    areaUnHighLighted.width(me.minColumns + "em").height(me.minRows + "em");\r\n
                    areaStatus.html(curColumns + " x " + curRows);\r\n
                    areaStatus.width(areaUnHighLighted.width());\r\n
                }\r\n
                areaMouseCatcher.on("mousemove", onMouseMove);\r\n
                areaHighLighted.on("mousemove", onMouseMove);\r\n
                areaUnHighLighted.on("mousemove", onMouseMove);\r\n
                areaMouseCatcher.on("mouseleave", onMouseLeave);\r\n
                areaHighLighted.on("mouseleave", onMouseLeave);\r\n
                areaUnHighLighted.on("mouseleave", onMouseLeave);\r\n
                areaMouseCatcher.on("click", onHighLightedMouseClick);\r\n
                areaHighLighted.on("click", onHighLightedMouseClick);\r\n
                areaUnHighLighted.on("click", onHighLightedMouseClick);\r\n
            },\r\n
            render: function () {\r\n
                $(this.el).html(this.template());\r\n
                return this;\r\n
            },\r\n
            setTableSize: function (columns, rows, event) {\r\n
                if (columns > this.maxColumns) {\r\n
                    columns = this.maxColumns;\r\n
                }\r\n
                if (rows > this.maxRows) {\r\n
                    rows = this.maxRows;\r\n
                }\r\n
                if (curColumns != columns || curRows != rows) {\r\n
                    curColumns = columns;\r\n
                    curRows = rows;\r\n
                    areaHighLighted.width(curColumns + "em").height(curRows + "em");\r\n
                    areaUnHighLighted.width(((curColumns < me.minColumns) ? me.minColumns : ((curColumns + 1 > me.maxColumns) ? me.maxColumns : curColumns + 1)) + "em").height(((curRows < me.minRows) ? me.minRows : ((curRows + 1 > me.maxRows) ? me.maxRows : curRows + 1)) + "em");\r\n
                    rootEl.width(areaUnHighLighted.width());\r\n
                    areaStatus.html(curColumns + " x " + curRows);\r\n
                    areaStatus.width(areaUnHighLighted.width());\r\n
                    me.trigger("change", me, curColumns, curRows, event);\r\n
                }\r\n
            },\r\n
            getColumnsCount: function () {\r\n
                return curColumns;\r\n
            },\r\n
            getRowsCount: function () {\r\n
                return curRows;\r\n
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
            <value> <int>6434</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
