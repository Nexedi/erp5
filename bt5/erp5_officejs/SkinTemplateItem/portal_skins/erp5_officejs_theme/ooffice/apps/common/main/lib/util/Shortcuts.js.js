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
            <value> <string>ts44308804.22</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Shortcuts.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>﻿/*\r\n
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
Common.util = Common.util || {};\r\n
define(["backbone", "keymaster"], function (Backbone) {\r\n
    var Shortcuts = function (options) {\r\n
        this.cid = _.uniqueId("shortcuts");\r\n
        this.initialize.apply(this, arguments);\r\n
        return this;\r\n
    };\r\n
    _.extend(Shortcuts.prototype, Backbone.Events, {\r\n
        initialize: function () {\r\n
            window.key.filter = function (event) {\r\n
                return true;\r\n
            };\r\n
            Common.NotificationCenter.on({\r\n
                "modal:show": function (e) {\r\n
                    window.key.suspend();\r\n
                },\r\n
                "modal:close": function (e) {\r\n
                    window.key.resume();\r\n
                },\r\n
                "modal:hide": function (e) {\r\n
                    window.key.resume();\r\n
                }\r\n
            });\r\n
        },\r\n
        delegateShortcuts: function (options) {\r\n
            if (!options || !options.shortcuts) {\r\n
                return;\r\n
            }\r\n
            this.removeShortcuts(options);\r\n
            var callback, match, method, scope, shortcut, shortcutKey;\r\n
            var _results = [];\r\n
            for (shortcut in options.shortcuts) {\r\n
                callback = options.shortcuts[shortcut];\r\n
                if (!_.isFunction(callback)) {\r\n
                    method = options[callback];\r\n
                    if (!method) {\r\n
                        throw new Error("Method " + callback + " does not exist");\r\n
                    }\r\n
                } else {\r\n
                    method = callback;\r\n
                }\r\n
                match = shortcut.match(/^(\\S+)\\s*(.*)$/);\r\n
                shortcutKey = match[1];\r\n
                scope = match[2].length ? match[2] : "all";\r\n
                method = _.bind(method, this);\r\n
                _results.push(window.key(shortcutKey, scope, method));\r\n
            }\r\n
        },\r\n
        removeShortcuts: function (options) {\r\n
            if (!options || !options.shortcuts) {\r\n
                return;\r\n
            }\r\n
            var match, scope, shortcut, shortcutKey;\r\n
            var _results = [];\r\n
            for (shortcut in options.shortcuts) {\r\n
                match = shortcut.match(/^(\\S+)\\s*(.*)$/);\r\n
                shortcutKey = match[1];\r\n
                scope = match[2].length ? match[2] : "all";\r\n
                window.key.unbind(shortcutKey, scope);\r\n
            }\r\n
        },\r\n
        suspendEvents: function (key, scope) {\r\n
            window.key.suspend(key, scope);\r\n
        },\r\n
        resumeEvents: function (key, scope) {\r\n
            window.key.resume(key, scope);\r\n
        }\r\n
    });\r\n
    Shortcuts.extend = Backbone.View.extend;\r\n
    Common.util.Shortcuts = new Shortcuts;\r\n
});</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4328</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
