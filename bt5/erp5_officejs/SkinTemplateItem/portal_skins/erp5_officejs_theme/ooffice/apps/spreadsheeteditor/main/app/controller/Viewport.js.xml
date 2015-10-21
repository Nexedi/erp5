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
            <value> <string>ts44308425.83</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Viewport.js</string> </value>
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
 define(["core", "common/main/lib/view/Header", "spreadsheeteditor/main/app/view/Viewport"], function (Viewport) {\r\n
    SSE.Controllers.Viewport = Backbone.Controller.extend({\r\n
        models: [],\r\n
        collections: [],\r\n
        views: ["Viewport", "Common.Views.Header"],\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "Viewport": {}\r\n
            });\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.viewport = this.createView("Viewport").render();\r\n
            this.header = this.createView("Common.Views.Header", {\r\n
                headerCaption: "Spreadsheet Editor"\r\n
            }).render();\r\n
            Common.NotificationCenter.on("layout:changed", _.bind(this.onLayoutChanged, this));\r\n
            $(window).on("resize", _.bind(this.onWindowResize, this));\r\n
            this.viewport.celayout.on("layout:resizedrag", function () {\r\n
                this.viewport.fireEvent("layout:resizedrag", [this, "cell:edit"]);\r\n
                this.api.asc_Resize();\r\n
            },\r\n
            this);\r\n
            this.viewport.hlayout.on("layout:resizedrag", function () {\r\n
                this.api.asc_Resize();\r\n
            },\r\n
            this);\r\n
            this.boxSdk = $("#editor_sdk");\r\n
            this.boxFormula = $("#cell-editing-box");\r\n
            this.boxSdk.css("border-left", "none");\r\n
            this.boxFormula.css("border-left", "none");\r\n
        },\r\n
        onLayoutChanged: function (area) {\r\n
            switch (area) {\r\n
            default:\r\n
                this.viewport.vlayout.doLayout();\r\n
                this.viewport.celayout.doLayout();\r\n
            case "rightmenu":\r\n
                this.viewport.hlayout.doLayout();\r\n
                break;\r\n
            case "leftmenu":\r\n
                var panel = this.viewport.hlayout.items[0];\r\n
                if (panel.resize.el) {\r\n
                    if (panel.el.width() > 40) {\r\n
                        this.boxSdk.css("border-left", "");\r\n
                        this.boxFormula.css("border-left", "");\r\n
                        panel.resize.el.show();\r\n
                    } else {\r\n
                        panel.resize.el.hide();\r\n
                        this.boxSdk.css("border-left", "none");\r\n
                        this.boxFormula.css("border-left", "none");\r\n
                    }\r\n
                }\r\n
                this.viewport.hlayout.doLayout();\r\n
                break;\r\n
            case "header":\r\n
                case "toolbar":\r\n
                case "status":\r\n
                this.viewport.vlayout.doLayout();\r\n
                this.viewport.celayout.doLayout();\r\n
                break;\r\n
            case "celleditor":\r\n
                if (arguments[1]) {\r\n
                    this.boxSdk.css("border-top", arguments[1] == "hidden" ? "none" : "");\r\n
                }\r\n
                this.viewport.celayout.doLayout();\r\n
                break;\r\n
            }\r\n
            this.api.asc_Resize();\r\n
        },\r\n
        onWindowResize: function (e) {\r\n
            this.onLayoutChanged("window");\r\n
            Common.NotificationCenter.trigger("window:resize");\r\n
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
            <value> <int>4778</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
