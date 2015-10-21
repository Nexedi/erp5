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
            <value> <string>ts44308796.64</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>IrregularStack.js</string> </value>
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
Common.IrregularStack = function (config) {\r\n
    var _stack = [];\r\n
    var _compare = function (obj1, obj2) {\r\n
        if (typeof obj1 === "object" && typeof obj2 === "object" && window.JSON) {\r\n
            return window.JSON.stringify(obj1) === window.JSON.stringify(obj2);\r\n
        }\r\n
        return obj1 === obj2;\r\n
    };\r\n
    config = config || {};\r\n
    var _strongCompare = config.strongCompare || _compare;\r\n
    var _weakCompare = config.weakCompare || _compare;\r\n
    var _indexOf = function (obj, compare) {\r\n
        for (var i = _stack.length - 1; i >= 0; i--) {\r\n
            if (compare(_stack[i], obj)) {\r\n
                return i;\r\n
            }\r\n
        }\r\n
        return -1;\r\n
    };\r\n
    var _push = function (obj) {\r\n
        _stack.push(obj);\r\n
    };\r\n
    var _pop = function (obj) {\r\n
        var index = _indexOf(obj, _strongCompare);\r\n
        if (index != -1) {\r\n
            var removed = _stack.splice(index, 1);\r\n
            return removed[0];\r\n
        }\r\n
        return undefined;\r\n
    };\r\n
    var _get = function (obj) {\r\n
        var index = _indexOf(obj, _weakCompare);\r\n
        if (index != -1) {\r\n
            return _stack[index];\r\n
        }\r\n
        return undefined;\r\n
    };\r\n
    var _exist = function (obj) {\r\n
        return ! (_indexOf(obj, _strongCompare) < 0);\r\n
    };\r\n
    return {\r\n
        push: _push,\r\n
        pop: _pop,\r\n
        get: _get,\r\n
        exist: _exist\r\n
    };\r\n
};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3037</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
