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
            <value> <string>ts44308796.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Analytics.js</string> </value>
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
Common.component = Common.component || {};\r\n
Common.Analytics = Common.component.Analytics = new(function () {\r\n
    var _category;\r\n
    return {\r\n
        initialize: function (id, category) {\r\n
            if (typeof id === "undefined") {\r\n
                throw "Analytics: invalid id.";\r\n
            }\r\n
            if (typeof category === "undefined" || Object.prototype.toString.apply(category) !== "[object String]") {\r\n
                throw "Analytics: invalid category type.";\r\n
            }\r\n
            _category = category;\r\n
            $("head").append(\'<script type="text/javascript">\' + "var _gaq = _gaq || [];" + \'_gaq.push(["_setAccount", "\' + id + \'"]);\' + \'_gaq.push(["_trackPageview"]);\' + "(function() {" + \'var ga = document.createElement("script"); ga.type = "text/javascript"; ga.async = true;\' + \'ga.src = ("https:" == document.location.protocol ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js";\' + \'var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(ga, s);\' + "})();" + "</script>");\r\n
        },\r\n
        trackEvent: function (action, label, value) {\r\n
            if (typeof action !== "undefined" && Object.prototype.toString.apply(action) !== "[object String]") {\r\n
                throw "Analytics: invalid action type.";\r\n
            }\r\n
            if (typeof label !== "undefined" && Object.prototype.toString.apply(label) !== "[object String]") {\r\n
                throw "Analytics: invalid label type.";\r\n
            }\r\n
            if (typeof value !== "undefined" && !(Object.prototype.toString.apply(value) === "[object Number]" && isFinite(value))) {\r\n
                throw "Analytics: invalid value type.";\r\n
            }\r\n
            if (typeof _gaq === "undefined") {\r\n
                return;\r\n
            }\r\n
            if (_category === "undefined") {\r\n
                throw "Analytics is not initialized.";\r\n
            }\r\n
            _gaq.push(["_trackEvent", _category, action, label, value]);\r\n
        }\r\n
    };\r\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3627</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
