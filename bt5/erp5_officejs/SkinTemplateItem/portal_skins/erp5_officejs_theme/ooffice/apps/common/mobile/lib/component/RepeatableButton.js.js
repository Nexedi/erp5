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
            <value> <string>ts44308812.4</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>RepeatableButton.js</string> </value>
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
 Ext.define("Common.component.RepeatableButton", {\r\n
    extend: "Ext.Button",\r\n
    xtype: "repeatablebutton",\r\n
    requires: ["Ext.util.TapRepeater"],\r\n
    initialize: function () {\r\n
        this.callParent(arguments);\r\n
        this.repeater = this.createRepeater(this.element, this.onRepeatTap);\r\n
    },\r\n
    destroy: function () {\r\n
        var me = this;\r\n
        Ext.destroy(me.repeater);\r\n
        me.callParent(arguments);\r\n
    },\r\n
    createRepeater: function (el, fn) {\r\n
        var me = this,\r\n
        repeater = Ext.create("Ext.util.TapRepeater", {\r\n
            el: el,\r\n
            accelerate: true,\r\n
            delay: 500\r\n
        });\r\n
        repeater.on({\r\n
            tap: fn,\r\n
            touchstart: "onTouchStart",\r\n
            touchend: "onTouchEnd",\r\n
            scope: me\r\n
        });\r\n
        return repeater;\r\n
    },\r\n
    onRepeatTap: function (e) {\r\n
        this.fireAction("tap", [this, e, true], "doTap");\r\n
    },\r\n
    doTap: function (me, e, handle) {\r\n
        if (Ext.isBoolean(handle) && handle) {\r\n
            this.callParent(arguments);\r\n
        } else {\r\n
            return false;\r\n
        }\r\n
    },\r\n
    onTouchStart: function (repeater) {\r\n
        if (!this.getDisabled()) {\r\n
            this.element.addCls(Ext.baseCSSPrefix + "button-pressing");\r\n
        }\r\n
    },\r\n
    onTouchEnd: function (repeater) {\r\n
        this.element.removeCls(Ext.baseCSSPrefix + "button-pressing");\r\n
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
            <value> <int>2996</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
