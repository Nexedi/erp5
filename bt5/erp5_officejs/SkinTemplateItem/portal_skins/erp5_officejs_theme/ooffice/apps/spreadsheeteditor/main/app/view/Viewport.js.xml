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
            <value> <string>ts44321339.9</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/Viewport.template", "jquery", "underscore", "backbone", "common/main/lib/component/BaseView", "common/main/lib/component/Layout"], function (viewportTemplate, $, _, Backbone) {\r\n
    SSE.Views.Viewport = Backbone.View.extend({\r\n
        el: "#viewport",\r\n
        template: _.template(viewportTemplate),\r\n
        events: {},\r\n
        initialize: function () {},\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({}));\r\n
            if (Common.Utils.isSafari) {\r\n
                $("body").addClass("safari");\r\n
                $("body").mousewheel(function (e) {\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                });\r\n
            } else {\r\n
                if (Common.Utils.isChrome) {\r\n
                    $("body").addClass("chrome");\r\n
                }\r\n
            }\r\n
            var $container = $("#viewport-vbox-layout", el);\r\n
            var items = $container.find(" > .layout-item");\r\n
            this.vlayout = new Common.UI.VBoxLayout({\r\n
                box: $container,\r\n
                items: [{\r\n
                    el: items[0],\r\n
                    rely: true\r\n
                },\r\n
                {\r\n
                    el: items[1],\r\n
                    rely: true\r\n
                },\r\n
                {\r\n
                    el: items[2],\r\n
                    stretch: true\r\n
                },\r\n
                {\r\n
                    el: items[3],\r\n
                    height: 25\r\n
                }]\r\n
            });\r\n
            $container = $("#viewport-hbox-layout", el);\r\n
            items = $container.find(" > .layout-item");\r\n
            this.hlayout = new Common.UI.HBoxLayout({\r\n
                box: $container,\r\n
                items: [{\r\n
                    el: items[0],\r\n
                    rely: true,\r\n
                    resize: {\r\n
                        hidden: true,\r\n
                        autohide: false,\r\n
                        min: 300,\r\n
                        max: 600\r\n
                    }\r\n
                },\r\n
                {\r\n
                    el: items[1],\r\n
                    stretch: true\r\n
                },\r\n
                {\r\n
                    el: $(items[2]).hide(),\r\n
                    rely: true\r\n
                }]\r\n
            });\r\n
            $container = $container.find(".layout-ct.vbox");\r\n
            items = $container.find(" > .layout-item");\r\n
            this.celayout = new Common.UI.VBoxLayout({\r\n
                box: $container,\r\n
                items: [{\r\n
                    el: items[0],\r\n
                    rely: true,\r\n
                    resize: {\r\n
                        min: 19,\r\n
                        max: -100\r\n
                    }\r\n
                },\r\n
                {\r\n
                    el: items[1],\r\n
                    stretch: true\r\n
                }]\r\n
            });\r\n
            return this;\r\n
        },\r\n
        applyEditorMode: function () {\r\n
            var me = this,\r\n
            toolbarView = SSE.getController("Toolbar").getView("Toolbar"),\r\n
            rightMenuView = SSE.getController("RightMenu").getView("RightMenu");\r\n
            me._toolbar = toolbarView.render(this.mode.isEditDiagram);\r\n
            me._rightMenu = rightMenuView.render();\r\n
        },\r\n
        setMode: function (mode, delay) {\r\n
            if (mode.isDisconnected) {\r\n
                if (_.isUndefined(this.mode)) {\r\n
                    this.mode = {};\r\n
                }\r\n
                this.mode.canCoAuthoring = false;\r\n
            } else {\r\n
                this.mode = mode;\r\n
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
            <value> <int>5227</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
