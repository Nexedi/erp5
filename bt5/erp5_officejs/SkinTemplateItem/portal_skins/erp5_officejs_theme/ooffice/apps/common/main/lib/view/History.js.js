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
            <value> <string>ts44321418.93</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>History.js</string> </value>
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
Common.Views = Common.Views || {};\r\n
define(["common/main/lib/util/utils", "common/main/lib/component/BaseView", "common/main/lib/component/Layout"], function (template) {\r\n
    Common.Views.History = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#left-panel-history",\r\n
        storeHistory: undefined,\r\n
        template: _.template([\'<div id="history-box" class="layout-ct vbox">\', \'<div id="history-header" class="">\', \'<label id="history-btn-back" class="btn"><%=scope.textHistoryHeader%></label>\', "</div>", \'<div id="history-list" class="">\', "</div>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            _.extend(this, options);\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
        },\r\n
        render: function (el) {\r\n
            el = el || this.el;\r\n
            $(el).html(this.template({\r\n
                scope: this\r\n
            })).width((parseInt(localStorage.getItem("de-mainmenu-width")) || MENU_SCALE_PART) - SCALE_MIN);\r\n
            this.viewHistoryList = new Common.UI.DataView({\r\n
                el: $("#history-list"),\r\n
                store: this.storeHistory,\r\n
                enableKeyEvents: false,\r\n
                itemTemplate: _.template([\'<div id="<%= id %>" class="history-item-wrap" style="display: block;">\', \'<div class="user-date"><%= created %></div>\', "<% if (markedAsVersion) { %>", \'<div class="user-version">ver.<%=version%></div>\', "<% } %>", \'<div class="user-name">\', \'<div class="color" style="display: inline-block; background-color:\' + "<%=usercolor%>;" + \'" >\', "</div><%= Common.Utils.String.htmlEncode(username) %>", "</div>", "</div>"].join(""))\r\n
            });\r\n
            this.btnBackToDocument = new Common.UI.Button({\r\n
                el: $("#history-btn-back"),\r\n
                enableToggle: false\r\n
            });\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        textHistoryHeader: "Back to Document"\r\n
    },\r\n
    Common.Views.History || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3639</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
