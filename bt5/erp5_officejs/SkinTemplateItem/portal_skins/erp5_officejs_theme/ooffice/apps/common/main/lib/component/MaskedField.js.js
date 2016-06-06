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
            <value> <string>ts44308799.8</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>MaskedField.js</string> </value>
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
    Common.UI.MaskedField = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            maskExp: "",\r\n
            maxLength: 999\r\n
        },\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            el.addClass("masked-field");\r\n
            el.attr("maxlength", me.options.maxLength);\r\n
            el.on("keypress", function (e) {\r\n
                var charCode = String.fromCharCode(e.which);\r\n
                if (!me.options.maskExp.test(charCode) && !e.ctrlKey && e.keyCode !== Common.UI.Keys.DELETE && e.keyCode !== Common.UI.Keys.BACKSPACE && e.keyCode !== Common.UI.Keys.LEFT && e.keyCode !== Common.UI.Keys.RIGHT && e.keyCode !== Common.UI.Keys.HOME && e.keyCode !== Common.UI.Keys.END && e.keyCode !== Common.UI.Keys.ESC && e.keyCode !== Common.UI.Keys.INSERT && e.keyCode !== Common.UI.Keys.TAB) {\r\n
                    if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                        me.trigger("changed", me, el.val());\r\n
                    }\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                }\r\n
            });\r\n
            el.on("input", function (e) {\r\n
                me.trigger("change", me, el.val());\r\n
            });\r\n
            el.on("blur", function (e) {\r\n
                me.trigger("changed", me, el.val());\r\n
            });\r\n
        },\r\n
        render: function () {\r\n
            return this;\r\n
        },\r\n
        setValue: function (value) {\r\n
            if (this.options.maskExp.test(value) && value.length <= this.options.maxLength) {\r\n
                $(this.el).val(value);\r\n
            }\r\n
        },\r\n
        getValue: function () {\r\n
            $(this.el).val();\r\n
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
            <value> <int>3489</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
