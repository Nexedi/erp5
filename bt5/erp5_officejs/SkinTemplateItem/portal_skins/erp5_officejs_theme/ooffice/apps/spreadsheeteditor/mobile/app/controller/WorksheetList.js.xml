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
            <value> <string>ts44308767.56</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>WorksheetList.js</string> </value>
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
 Ext.define("SSE.controller.WorksheetList", {\r\n
    extend: "Ext.app.Controller",\r\n
    config: {\r\n
        refs: {\r\n
            worksheetList: {\r\n
                selector: "seworksheetlist list"\r\n
            }\r\n
        }\r\n
    },\r\n
    init: function () {\r\n
        this.control({\r\n
            "seworksheetlist list": {\r\n
                itemtap: this._worksheetSelect\r\n
            }\r\n
        });\r\n
    },\r\n
    setApi: function (o) {\r\n
        this.api = o;\r\n
        if (this.api) {\r\n
            this.api.asc_registerCallback("asc_onEndAction", Ext.bind(this.onLongActionEnd, this));\r\n
        }\r\n
    },\r\n
    _worksheetSelect: function (dataview, index, target, record, event, eOpts) {\r\n
        if (this.api) {\r\n
            var dataIndex = record.data.index;\r\n
            if ((dataIndex > -1) && (this.api.asc_getActiveWorksheetIndex() != dataIndex)) {\r\n
                this.api.asc_showWorksheet(dataIndex);\r\n
            }\r\n
        }\r\n
    },\r\n
    _loadWorksheets: function () {\r\n
        if (this.api) {\r\n
            var worksheetsStore = Ext.getStore("Worksheets"),\r\n
            worksheetList = this.getWorksheetList();\r\n
            if (worksheetsStore && worksheetList) {\r\n
                worksheetsStore.removeAll(false);\r\n
                var worksheetsCount = this.api.asc_getWorksheetsCount();\r\n
                if (worksheetsCount) {\r\n
                    for (var i = 0; i < worksheetsCount; i++) {\r\n
                        var result = {\r\n
                            text: this.api.asc_getWorksheetName(i),\r\n
                            index: i\r\n
                        };\r\n
                        worksheetsStore.add(result);\r\n
                    }\r\n
                    var rec = worksheetsStore.findRecord("index", this.api.asc_getActiveWorksheetIndex());\r\n
                    if (rec) {\r\n
                        worksheetList.select(rec);\r\n
                    } else {\r\n
                        worksheetList.select(worksheetsStore.getAt(0));\r\n
                    }\r\n
                }\r\n
            }\r\n
        }\r\n
    },\r\n
    onLongActionEnd: function (type, id) {\r\n
        if (type === c_oAscAsyncActionType["BlockInteraction"]) {\r\n
            switch (id) {\r\n
            case c_oAscAsyncAction["Open"]:\r\n
                this._loadWorksheets();\r\n
                break;\r\n
            }\r\n
        }\r\n
    }\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3877</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
