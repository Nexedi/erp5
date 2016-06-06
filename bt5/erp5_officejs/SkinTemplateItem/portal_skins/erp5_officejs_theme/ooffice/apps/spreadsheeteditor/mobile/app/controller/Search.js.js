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
            <value> <string>ts44308767.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Search.js</string> </value>
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
 Ext.define("SSE.controller.Search", {\r\n
    extend: "Ext.app.Controller",\r\n
    config: {\r\n
        refs: {\r\n
            nextResult: "#id-btn-search-prev",\r\n
            previousResult: "#id-btn-search-next",\r\n
            searchField: "#id-field-search"\r\n
        },\r\n
        control: {\r\n
            "#id-btn-search-prev": {\r\n
                tap: "onPreviousResult"\r\n
            },\r\n
            "#id-btn-search-next": {\r\n
                tap: "onNextResult"\r\n
            },\r\n
            "#id-field-search": {\r\n
                keyup: "onSearchKeyUp",\r\n
                change: "onSearchChange",\r\n
                clearicontap: "onSearchClear"\r\n
            }\r\n
        }\r\n
    },\r\n
    _step: -1,\r\n
    init: function () {},\r\n
    setApi: function (o) {\r\n
        this.api = o;\r\n
    },\r\n
    onNextResult: function () {\r\n
        var searchField = this.getSearchField();\r\n
        if (this.api && searchField) {\r\n
            this.api.asc_findText(searchField.getValue(), true, true);\r\n
        }\r\n
    },\r\n
    onPreviousResult: function () {\r\n
        var searchField = this.getSearchField();\r\n
        if (this.api && searchField) {\r\n
            this.api.asc_findText(searchField.getValue(), true, false);\r\n
        }\r\n
    },\r\n
    onSearchKeyUp: function (field, e) {\r\n
        var keyCode = e.event.keyCode,\r\n
        searchField = this.getSearchField();\r\n
        if (keyCode == 13 && this.api) {\r\n
            this.api.asc_findText(searchField.getValue(), true, true);\r\n
        }\r\n
        this.updateNavigation();\r\n
    },\r\n
    onSearchChange: function (field, newValue, oldValue) {\r\n
        this.updateNavigation();\r\n
    },\r\n
    onSearchClear: function (field, e) {\r\n
        this.updateNavigation();\r\n
        window.focus();\r\n
        document.activeElement.blur();\r\n
    },\r\n
    updateNavigation: function () {\r\n
        var searchField = this.getSearchField(),\r\n
        nextResult = this.getNextResult(),\r\n
        previousResult = this.getPreviousResult();\r\n
        if (searchField && nextResult && previousResult) {\r\n
            nextResult.setDisabled(searchField.getValue() == "");\r\n
            previousResult.setDisabled(searchField.getValue() == "");\r\n
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
            <value> <int>3727</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
