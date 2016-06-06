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
            <value> <string>ts44308796.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Gateway.js</string> </value>
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
Common.Gateway = new(function () {\r\n
    var me = this,\r\n
    $me = $(me);\r\n
    var commandMap = {\r\n
        "init": function (data) {\r\n
            $me.trigger("init", data);\r\n
        },\r\n
        "openDocument": function (data) {\r\n
            $me.trigger("opendocument", data);\r\n
        },\r\n
        "showMessage": function (data) {\r\n
            $me.trigger("showmessage", data);\r\n
        },\r\n
        "applyEditRights": function (data) {\r\n
            $me.trigger("applyeditrights", data);\r\n
        },\r\n
        "processSaveResult": function (data) {\r\n
            $me.trigger("processsaveresult", data);\r\n
        },\r\n
        "processRightsChange": function (data) {\r\n
            $me.trigger("processrightschange", data);\r\n
        },\r\n
        "refreshHistory": function (data) {\r\n
            $me.trigger("refreshhistory", data);\r\n
        },\r\n
        "setHistoryData": function (data) {\r\n
            $me.trigger("sethistorydata", data);\r\n
        },\r\n
        "processMouse": function (data) {\r\n
            $me.trigger("processmouse", data);\r\n
        },\r\n
        "internalCommand": function (data) {\r\n
            $me.trigger("internalcommand", data);\r\n
        },\r\n
        "resetFocus": function (data) {\r\n
            $me.trigger("resetfocus", data);\r\n
        }\r\n
    };\r\n
    var _postMessage = function (msg) {\r\n
        if (window.parent && window.JSON) {\r\n
            window.parent.postMessage(window.JSON.stringify(msg), "*");\r\n
        }\r\n
    };\r\n
    var _onMessage = function (msg) {\r\n
        var data = msg.data;\r\n
        if (Object.prototype.toString.apply(data) !== "[object String]" || !window.JSON) {\r\n
            return;\r\n
        }\r\n
        var cmd, handler;\r\n
        try {\r\n
            cmd = window.JSON.parse(data);\r\n
        } catch(e) {\r\n
            cmd = "";\r\n
        }\r\n
        if (cmd) {\r\n
            handler = commandMap[cmd.command];\r\n
            if (handler) {\r\n
                handler.call(this, cmd.data);\r\n
            }\r\n
        }\r\n
    };\r\n
    var fn = function (e) {\r\n
        _onMessage(e);\r\n
    };\r\n
    if (window.attachEvent) {\r\n
        window.attachEvent("onmessage", fn);\r\n
    } else {\r\n
        window.addEventListener("message", fn, false);\r\n
    }\r\n
    return {\r\n
        ready: function () {\r\n
            _postMessage({\r\n
                event: "onReady"\r\n
            });\r\n
        },\r\n
        goBack: function (new_window) {\r\n
            _postMessage({\r\n
                event: "onBack",\r\n
                data: (new_window == true)\r\n
            });\r\n
        },\r\n
        save: function (url) {\r\n
            _postMessage({\r\n
                event: "onSave",\r\n
                data: url\r\n
            });\r\n
        },\r\n
        requestEditRights: function () {\r\n
            _postMessage({\r\n
                event: "onRequestEditRights"\r\n
            });\r\n
        },\r\n
        requestHistory: function () {\r\n
            _postMessage({\r\n
                event: "onRequestHistory"\r\n
            });\r\n
        },\r\n
        requestHistoryData: function (revision) {\r\n
            _postMessage({\r\n
                event: "onRequestHistoryData",\r\n
                data: revision\r\n
            });\r\n
        },\r\n
        requestHistoryClose: function (revision) {\r\n
            _postMessage({\r\n
                event: "onRequestHistoryClose"\r\n
            });\r\n
        },\r\n
        reportError: function (code, description) {\r\n
            _postMessage({\r\n
                event: "onError",\r\n
                data: {\r\n
                    errorCode: code,\r\n
                    errorDescription: description\r\n
                }\r\n
            });\r\n
        },\r\n
        setDocumentModified: function (modified) {\r\n
            _postMessage({\r\n
                event: "onDocumentStateChange",\r\n
                data: modified\r\n
            });\r\n
        },\r\n
        internalMessage: function (type, data) {\r\n
            _postMessage({\r\n
                event: "onInternalMessage",\r\n
                data: {\r\n
                    type: type,\r\n
                    data: data\r\n
                }\r\n
            });\r\n
        },\r\n
        updateVersion: function () {\r\n
            _postMessage({\r\n
                event: "onOutdatedVersion"\r\n
            });\r\n
        },\r\n
        on: function (event, handler) {\r\n
            var localHandler = function (event, data) {\r\n
                handler.call(me, data);\r\n
            };\r\n
            $me.on(event, localHandler);\r\n
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
            <value> <int>5973</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
