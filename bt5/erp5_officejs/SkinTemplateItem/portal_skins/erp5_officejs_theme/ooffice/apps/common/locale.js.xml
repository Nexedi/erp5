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
            <value> <string>ts44308796.73</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>locale.js</string> </value>
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
Common.Locale = new(function () {\r\n
    var l10n = {};\r\n
    var _createXMLHTTPObject = function () {\r\n
        var xmlhttp;\r\n
        try {\r\n
            xmlhttp = new ActiveXObject("Msxml2.XMLHTTP");\r\n
        } catch(e) {\r\n
            try {\r\n
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");\r\n
            } catch(E) {\r\n
                xmlhttp = false;\r\n
            }\r\n
        }\r\n
        if (!xmlhttp && typeof XMLHttpRequest != "undefined") {\r\n
            xmlhttp = new XMLHttpRequest();\r\n
        }\r\n
        return xmlhttp;\r\n
    };\r\n
    var _applyLocalization = function () {\r\n
        try {\r\n
            for (var prop in l10n) {\r\n
                var p = prop.split(".");\r\n
                if (p && p.length > 2) {\r\n
                    var obj = window;\r\n
                    for (var i = 0; i < p.length - 1; ++i) {\r\n
                        if (obj[p[i]] === undefined) {\r\n
                            obj[p[i]] = new Object();\r\n
                        }\r\n
                        obj = obj[p[i]];\r\n
                    }\r\n
                    if (obj) {\r\n
                        obj[p[p.length - 1]] = l10n[prop];\r\n
                    }\r\n
                }\r\n
            }\r\n
        } catch(e) {}\r\n
    };\r\n
    var _get = function (prop, scope) {\r\n
        var res = "";\r\n
        if (scope && scope.name) {\r\n
            res = l10n[scope.name + "." + prop];\r\n
        }\r\n
        return res || (scope ? eval(scope.name).prototype[prop] : "");\r\n
    };\r\n
    var _getUrlParameterByName = function (name) {\r\n
        name = name.replace(/[\\[]/, "\\\\[").replace(/[\\]]/, "\\\\]");\r\n
        var regex = new RegExp("[\\\\?&]" + name + "=([^&#]*)"),\r\n
        results = regex.exec(location.search);\r\n
        return results == null ? "" : decodeURIComponent(results[1].replace(/\\+/g, " "));\r\n
    };\r\n
    try {\r\n
        var langParam = _getUrlParameterByName("lang");\r\n
        var xhrObj = _createXMLHTTPObject();\r\n
        if (xhrObj && langParam) {\r\n
            var lang = langParam.split("-")[0];\r\n
            xhrObj.open("GET", "locale/" + lang + ".json", false);\r\n
            xhrObj.send("");\r\n
            l10n = eval("(" + xhrObj.responseText + ")");\r\n
        }\r\n
    } catch(e) {}\r\n
    return {\r\n
        apply: _applyLocalization,\r\n
        get: _get\r\n
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
            <value> <int>3880</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
