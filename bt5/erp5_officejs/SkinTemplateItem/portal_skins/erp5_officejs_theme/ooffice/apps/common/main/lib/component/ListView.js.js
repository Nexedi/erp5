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
            <value> <string>ts44308799.59</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ListView.js</string> </value>
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
define(["common/main/lib/component/DataView"], function () {\r\n
    Common.UI.ListView = Common.UI.DataView.extend((function () {\r\n
        return {\r\n
            options: {\r\n
                handleSelect: true,\r\n
                enableKeyEvents: true,\r\n
                showLast: true,\r\n
                keyMoveDirection: "vertical",\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="list-item" style=""><%= value %></div>\')\r\n
            },\r\n
            template: _.template([\'<div class="listview inner"></div>\'].join("")),\r\n
            onAddItem: function (record, index) {\r\n
                var view = new Common.UI.DataViewItem({\r\n
                    template: this.itemTemplate,\r\n
                    model: record\r\n
                });\r\n
                var idx = _.indexOf(this.store.models, record);\r\n
                if (view) {\r\n
                    var innerEl = $(this.el).find(".inner");\r\n
                    if (innerEl) {\r\n
                        var innerDivs = innerEl.find("> div");\r\n
                        innerEl.find(".empty-text").remove();\r\n
                        if (idx > 0) {\r\n
                            $(innerDivs.get(idx - 1)).after(view.render().el);\r\n
                        } else {\r\n
                            (innerDivs.length > 0) ? $(innerDivs[idx]).before(view.render().el) : innerEl.append(view.render().el);\r\n
                        }\r\n
                        this.dataViewItems.push(view);\r\n
                        this.listenTo(view, "change", this.onChangeItem);\r\n
                        this.listenTo(view, "remove", this.onRemoveItem);\r\n
                        this.listenTo(view, "click", this.onClickItem);\r\n
                        this.listenTo(view, "dblclick", this.onDblClickItem);\r\n
                        this.listenTo(view, "select", this.onSelectItem);\r\n
                        if (!this.isSuspendEvents) {\r\n
                            this.trigger("item:add", this, view, record);\r\n
                        }\r\n
                    }\r\n
                }\r\n
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
            <value> <int>3688</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
