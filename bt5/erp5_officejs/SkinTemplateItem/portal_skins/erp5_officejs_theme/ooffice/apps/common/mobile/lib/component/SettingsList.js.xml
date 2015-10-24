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
            <value> <string>ts44308812.49</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>SettingsList.js</string> </value>
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
 Ext.define("Common.component.SettingsList", {\r\n
    extend: "Ext.List",\r\n
    alias: "widget.settingslist",\r\n
    config: {\r\n
        disableSelection: true,\r\n
        pinHeaders: false,\r\n
        grouped: true,\r\n
        cls: "settings",\r\n
        ui: "round",\r\n
        itemTpl: Ext.create("Ext.XTemplate", \'<tpl for=".">\', \'<tpl if="this.hasIcon(icon)">\', \'<span class="list-icon {icon}"></span>\', "</tpl>", \'<tpl if="this.hasIcon(icon)">\', \'<strong class="icon-offset">{setting}</strong>\', "<tpl else>", "<strong>{setting}</strong>", "</tpl>", \'<tpl if="this.hasChild(child)">\', \'<span class="list-icon disclosure"></span>\', "</tpl>", "</tpl>", {\r\n
            hasIcon: function (icon) {\r\n
                return !Ext.isEmpty(icon);\r\n
            },\r\n
            hasChild: function (child) {\r\n
                return !Ext.isEmpty(child);\r\n
            }\r\n
        })\r\n
    },\r\n
    findGroupHeaderIndices: function () {\r\n
        var me = this,\r\n
        store = me.getStore(),\r\n
        storeLn = store.getCount(),\r\n
        groups = store.getGroups(),\r\n
        groupLn = groups.length,\r\n
        headerIndices = me.headerIndices = {},\r\n
        footerIndices = me.footerIndices = {},\r\n
        i,\r\n
        previousIndex,\r\n
        firstGroupedRecord,\r\n
        storeIndex;\r\n
        me.groups = groups;\r\n
        for (i = 0; i < groupLn; i++) {\r\n
            firstGroupedRecord = groups[i].children[0];\r\n
            storeIndex = store.indexOf(firstGroupedRecord);\r\n
            headerIndices[storeIndex] = true;\r\n
            previousIndex = storeIndex - 1;\r\n
            if (previousIndex >= 0) {\r\n
                footerIndices[previousIndex] = true;\r\n
            }\r\n
        }\r\n
        footerIndices[storeLn - 1] = true;\r\n
        return headerIndices;\r\n
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
            <value> <int>3313</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
