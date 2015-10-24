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
            <value> <string>ts44308801.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Chat.js</string> </value>
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
 define(["core", "common/main/lib/collection/Users", "common/main/lib/collection/ChatMessages", "common/main/lib/view/Chat"], function () {\r\n
    Common.Controllers.Chat = Backbone.Controller.extend(_.extend({\r\n
        models: [],\r\n
        collections: ["Common.Collections.Users", "Common.Collections.ChatMessages"],\r\n
        views: ["Common.Views.Chat"],\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "Common.Views.Chat": {\r\n
                    "message:add": _.bind(this.onSendMessage, this)\r\n
                }\r\n
            });\r\n
        },\r\n
        events: {},\r\n
        onLaunch: function () {\r\n
            this.panelChat = this.createView("Common.Views.Chat", {\r\n
                storeUsers: this.getApplication().getCollection("Common.Collections.Users"),\r\n
                storeMessages: this.getApplication().getCollection("Common.Collections.ChatMessages")\r\n
            });\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            if (this.api) {\r\n
                if (this.mode.canCoAuthoring && this.mode.canChat) {\r\n
                    this.api.asc_registerCallback("asc_onCoAuthoringChatReceiveMessage", _.bind(this.onReceiveMessage, this));\r\n
                }\r\n
                this.api.asc_registerCallback("asc_onAuthParticipantsChanged", _.bind(this.onUsersChanged, this));\r\n
                this.api.asc_registerCallback("asc_onConnectionStateChanged", _.bind(this.onUserConnection, this));\r\n
                this.api.asc_coAuthoringGetUsers();\r\n
                if (this.mode.canCoAuthoring && this.mode.canChat) {\r\n
                    this.api.asc_coAuthoringChatGetMessages();\r\n
                }\r\n
            }\r\n
            return this;\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            return this;\r\n
        },\r\n
        onUsersChanged: function (users) {\r\n
            if (!this.mode.canCoAuthoring) {\r\n
                var len = 0;\r\n
                for (name in users) {\r\n
                    if (undefined !== name) {\r\n
                        len++;\r\n
                    }\r\n
                }\r\n
                if (len > 2 && this._isCoAuthoringStopped == undefined) {\r\n
                    this._isCoAuthoringStopped = true;\r\n
                    this.api.asc_coAuthoringDisconnect();\r\n
                    Common.NotificationCenter.trigger("api:disconnect");\r\n
                    setTimeout(_.bind(function () {\r\n
                        Common.UI.alert({\r\n
                            closable: false,\r\n
                            title: this.notcriticalErrorTitle,\r\n
                            msg: this.textUserLimit,\r\n
                            iconCls: "warn",\r\n
                            buttons: ["ok"]\r\n
                        });\r\n
                    },\r\n
                    this), 100);\r\n
                    return;\r\n
                }\r\n
            }\r\n
            var usersStore = this.getApplication().getCollection("Common.Collections.Users");\r\n
            if (usersStore) {\r\n
                var arrUsers = [],\r\n
                name,\r\n
                user;\r\n
                for (name in users) {\r\n
                    if (undefined !== name) {\r\n
                        user = users[name];\r\n
                        if (user) {\r\n
                            arrUsers.push(new Common.Models.User({\r\n
                                id: user.asc_getId(),\r\n
                                username: user.asc_getUserName(),\r\n
                                online: true,\r\n
                                color: user.asc_getColor()\r\n
                            }));\r\n
                        }\r\n
                    }\r\n
                }\r\n
                usersStore[usersStore.size() > 0 ? "add" : "reset"](arrUsers);\r\n
            }\r\n
        },\r\n
        onUserConnection: function (change) {\r\n
            var usersStore = this.getApplication().getCollection("Common.Collections.Users");\r\n
            if (usersStore) {\r\n
                var user = usersStore.findUser(change.asc_getId());\r\n
                if (!user) {\r\n
                    usersStore.add(new Common.Models.User({\r\n
                        id: change.asc_getId(),\r\n
                        username: change.asc_getUserName(),\r\n
                        online: change.asc_getState(),\r\n
                        color: change.asc_getColor()\r\n
                    }));\r\n
                } else {\r\n
                    user.set({\r\n
                        online: change.asc_getState()\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        onReceiveMessage: function (messages) {\r\n
            var msgStore = this.getApplication().getCollection("Common.Collections.ChatMessages");\r\n
            if (msgStore) {\r\n
                var array = [];\r\n
                messages.forEach(function (msg) {\r\n
                    array.push(new Common.Models.ChatMessage({\r\n
                        userid: msg.user,\r\n
                        message: msg.message,\r\n
                        username: msg.username\r\n
                    }));\r\n
                });\r\n
                msgStore[msgStore.size() > 0 ? "add" : "reset"](array);\r\n
            }\r\n
        },\r\n
        onSendMessage: function (panel, text) {\r\n
            if (text.length > 0) {\r\n
                var splitString = function (string, chunkSize) {\r\n
                    var chunks = [];\r\n
                    while (string) {\r\n
                        if (string.length < chunkSize) {\r\n
                            chunks.push(string);\r\n
                            break;\r\n
                        } else {\r\n
                            chunks.push(string.substr(0, chunkSize));\r\n
                            string = string.substr(chunkSize);\r\n
                        }\r\n
                    }\r\n
                    return chunks;\r\n
                };\r\n
                var me = this;\r\n
                splitString(text, 2048).forEach(function (message) {\r\n
                    me.api.asc_coAuthoringChatSendMessage(message);\r\n
                });\r\n
            }\r\n
        },\r\n
        notcriticalErrorTitle: "Warning",\r\n
        textUserLimit: \'You are using ONLYOFFICE Editors free version.<br>Only two users can co-edit the document simultaneously.<br>Want more? Consider buying ONLYOFFICE Editors Pro version.<br><a href="http://www.onlyoffice.com" target="_blank">Read more</a>\'\r\n
    },\r\n
    Common.Controllers.Chat || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>7933</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
