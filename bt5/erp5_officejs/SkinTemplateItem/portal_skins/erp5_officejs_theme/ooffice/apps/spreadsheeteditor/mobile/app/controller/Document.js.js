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
            <value> <string>ts44308767.32</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Document.js</string> </value>
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
 Ext.define("SSE.controller.Document", {\r\n
    extend: "Ext.app.Controller",\r\n
    config: {\r\n
        refs: {},\r\n
        control: {\r\n
            "#id-btn-zoom-in": {\r\n
                tap: "onZoomIn"\r\n
            },\r\n
            "#id-btn-zoom-out": {\r\n
                tap: "onZoomOut"\r\n
            }\r\n
        }\r\n
    },\r\n
    _currZoom: 1,\r\n
    _baseZoom: 1,\r\n
    _maxZoom: 2,\r\n
    _incrementZoom: 0.05,\r\n
    init: function () {},\r\n
    launch: function () {},\r\n
    setApi: function (o) {\r\n
        this.api = o;\r\n
        if (this.api) {\r\n
            this.api.asc_registerCallback("asc_onDoubleTapEvent", Ext.bind(this._onDoubleTapDocument, this));\r\n
            this.api.asc_registerCallback("asc_onStartAction", Ext.bind(this._onLongActionBegin, this));\r\n
            this.api.asc_registerCallback("asc_onEndAction", Ext.bind(this._onLongActionEnd, this));\r\n
        }\r\n
    },\r\n
    _onLongActionBegin: function (type, id) {},\r\n
    _onLongActionEnd: function (type, id) {\r\n
        if (type === c_oAscAsyncActionType["BlockInteraction"]) {\r\n
            switch (id) {\r\n
            case c_oAscAsyncAction["Open"]:\r\n
                var i = this.api.asc_getActiveWorksheetIndex();\r\n
                this.api.asc_showWorksheet(i);\r\n
                break;\r\n
            }\r\n
        }\r\n
    },\r\n
    _onDoubleTapDocument: function () {\r\n
        if (this.api) {\r\n
            if (this._currZoom != this._baseZoom) {\r\n
                this._currZoom = this._baseZoom;\r\n
            } else {\r\n
                this._currZoom = this._maxZoom;\r\n
            }\r\n
            this.api.asc_setZoom(this._currZoom);\r\n
        }\r\n
    },\r\n
    onZoomIn: function (event, node, opt) {\r\n
        this._currZoom += this._incrementZoom;\r\n
        if (this._currZoom > this._maxZoom) {\r\n
            this._currZoom = this._maxZoom;\r\n
        }\r\n
        this.api.asc_setZoom(this._currZoom);\r\n
    },\r\n
    onZoomOut: function (event, node, opt) {\r\n
        this._currZoom -= this._incrementZoom;\r\n
        if (this._currZoom < this._baseZoom) {\r\n
            this._currZoom = this._baseZoom;\r\n
        }\r\n
        this.api.asc_setZoom(this._currZoom);\r\n
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
            <value> <int>3680</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
