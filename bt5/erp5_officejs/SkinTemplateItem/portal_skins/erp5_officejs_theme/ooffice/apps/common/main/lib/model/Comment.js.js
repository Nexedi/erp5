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
            <value> <string>ts44308802.63</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Comment.js</string> </value>
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
Common.Models = Common.Models || {};\r\n
define(["underscore", "backbone", "common/main/lib/component/BaseView"], function (_, Backbone) {\r\n
    Common.Models.Comment = Backbone.Model.extend({\r\n
        defaults: {\r\n
            uid: 0,\r\n
            userid: 0,\r\n
            username: "Guest",\r\n
            date: undefined,\r\n
            quote: "",\r\n
            comment: "",\r\n
            resolved: false,\r\n
            lock: false,\r\n
            lockuserid: "",\r\n
            unattached: false,\r\n
            id: Common.UI.getId(),\r\n
            time: 0,\r\n
            showReply: false,\r\n
            showReplyInPopover: false,\r\n
            editText: false,\r\n
            editTextInPopover: false,\r\n
            last: undefined,\r\n
            replys: [],\r\n
            hideAddReply: false,\r\n
            scope: null,\r\n
            hide: false,\r\n
            hint: false,\r\n
            dummy: undefined\r\n
        }\r\n
    });\r\n
    Common.Models.Reply = Backbone.Model.extend({\r\n
        defaults: {\r\n
            time: 0,\r\n
            userid: 0,\r\n
            username: "Guest",\r\n
            reply: "",\r\n
            date: undefined,\r\n
            id: Common.UI.getId(),\r\n
            editText: false,\r\n
            editTextInPopover: false,\r\n
            scope: null\r\n
        }\r\n
    });\r\n
});</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2886</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
