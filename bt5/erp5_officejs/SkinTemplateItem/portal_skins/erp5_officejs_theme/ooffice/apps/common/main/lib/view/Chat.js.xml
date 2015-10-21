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
            <value> <string>ts44321418.21</string> </value>
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
 if (Common === undefined) {\r\n
    var Common = {};\r\n
}\r\n
Common.Views = Common.Views || {};\r\n
define(["text!common/main/lib/template/Chat.template", "common/main/lib/util/utils", "common/main/lib/component/BaseView"], function (template) {\r\n
    Common.Views.Chat = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#left-panel-chat",\r\n
        template: _.template(template),\r\n
        storeUsers: undefined,\r\n
        storeMessages: undefined,\r\n
        tplUser: [\'<li id="chat-user-<%= user.get("id") %>"<% if (!user.get("online")) { %> class="offline"<% } %>>\', \'<div class="color" style="background-color: <%= user.get("color") %>;" >\', \'<label class="name"><%= scope.getUserName(user.get("username")) %></label>\', "</div>", "</li>"].join(""),\r\n
        templateUserList: _.template("<ul>" + "<% _.each(users, function(item) { %>" + "<%= _.template(usertpl, {user: item, scope: scope}) %>" + "<% }); %>" + "</ul>"),\r\n
        tplMsg: ["<li>", \'<% if (msg.get("type")==1) { %>\', \'<div class="message service" data-can-copy="true"><%= msg.get("message") %></div>\', "<% } else { %>", \'<div class="user" data-can-copy="true" style="color: <%= msg.get("usercolor") %>;"><%= scope.getUserName(msg.get("username")) %></div>\', \'<label class="message" data-can-copy="true"><%= msg.get("message") %></label>\', "<% } %>", "</li>"].join(""),\r\n
        templateMsgList: _.template("<ul>" + "<% _.each(messages, function(item) { %>" + "<%= _.template(msgtpl, {msg: item, scope: scope}) %>" + "<% }); %>" + "</ul>"),\r\n
        events: {},\r\n
        initialize: function (options) {\r\n
            _.extend(this, options);\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.storeUsers.bind({\r\n
                add: _.bind(this._onAddUser, this),\r\n
                change: _.bind(this._onUsersChanged, this),\r\n
                reset: _.bind(this._onResetUsers, this)\r\n
            });\r\n
            this.storeMessages.bind({\r\n
                add: _.bind(this._onAddMessage, this),\r\n
                reset: _.bind(this._onResetMessages, this)\r\n
            });\r\n
        },\r\n
        render: function (el) {\r\n
            el = el || this.el;\r\n
            $(el).html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.panelUsers = $("#chat-users", this.el);\r\n
            this.panelMessages = $("#chat-messages", this.el);\r\n
            this.txtMessage = $("#chat-msg-text", this.el);\r\n
            this.panelUsers.scroller = new Common.UI.Scroller({\r\n
                el: $("#chat-users"),\r\n
                useKeyboard: true,\r\n
                minScrollbarLength: 25\r\n
            });\r\n
            this.panelMessages.scroller = new Common.UI.Scroller({\r\n
                el: $("#chat-messages"),\r\n
                includePadding: true,\r\n
                useKeyboard: true,\r\n
                minScrollbarLength: 40\r\n
            });\r\n
            $("#chat-msg-btn-add", this.el).on("click", _.bind(this._onBtnAddMessage, this));\r\n
            this.txtMessage.on("keydown", _.bind(this._onKeyDown, this));\r\n
            return this;\r\n
        },\r\n
        focus: function () {\r\n
            var me = this;\r\n
            _.defer(function () {\r\n
                me.txtMessage.focus();\r\n
            },\r\n
            100);\r\n
        },\r\n
        _onKeyDown: function (event) {\r\n
            if (event.keyCode == Common.UI.Keys.RETURN) {\r\n
                if (event.ctrlKey || event.metaKey) {\r\n
                    this._onBtnAddMessage(event);\r\n
                }\r\n
            } else {\r\n
                if (event.keyCode == Common.UI.Keys.ESC) {\r\n
                    this.hide();\r\n
                }\r\n
            }\r\n
        },\r\n
        _onAddUser: function (m, c, opts) {\r\n
            if (this.panelUsers) {\r\n
                this.panelUsers.find("ul").append(_.template(this.tplUser, {\r\n
                    user: m,\r\n
                    scope: this\r\n
                }));\r\n
                this.panelUsers.scroller.update({\r\n
                    minScrollbarLength: 25\r\n
                });\r\n
            }\r\n
        },\r\n
        _onUsersChanged: function (m) {\r\n
            if (m.changed.online != undefined && this.panelUsers) {\r\n
                this.panelUsers.find("#chat-user-" + m.get("id"))[m.changed.online ? "removeClass" : "addClass"]("offline");\r\n
                this.panelUsers.scroller.update({\r\n
                    minScrollbarLength: 25\r\n
                });\r\n
            }\r\n
        },\r\n
        _onResetUsers: function (c, opts) {\r\n
            if (this.panelUsers) {\r\n
                this.panelUsers.html(this.templateUserList({\r\n
                    users: c.models,\r\n
                    usertpl: this.tplUser,\r\n
                    scope: this\r\n
                }));\r\n
                this.panelUsers.scroller.update({\r\n
                    minScrollbarLength: 25\r\n
                });\r\n
            }\r\n
        },\r\n
        _onAddMessage: function (m, c, opts) {\r\n
            if (this.panelMessages) {\r\n
                var content = this.panelMessages.find("ul");\r\n
                if (content && content.length) {\r\n
                    this._prepareMessage(m);\r\n
                    content.append(_.template(this.tplMsg, {\r\n
                        msg: m,\r\n
                        scope: this\r\n
                    }));\r\n
                    this.panelMessages.scroller.update({\r\n
                        minScrollbarLength: 40\r\n
                    });\r\n
                    this.panelMessages.scroller.scrollTop(content.get(0).getBoundingClientRect().height);\r\n
                }\r\n
            }\r\n
        },\r\n
        _onResetMessages: function (c, opts) {\r\n
            if (this.panelMessages) {\r\n
                var user, color;\r\n
                c.each(function (msg) {\r\n
                    this._prepareMessage(msg);\r\n
                },\r\n
                this);\r\n
                this.panelMessages.html(this.templateMsgList({\r\n
                    messages: c.models,\r\n
                    msgtpl: this.tplMsg,\r\n
                    scope: this\r\n
                }));\r\n
                this.panelMessages.scroller.update({\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
        },\r\n
        _onBtnAddMessage: function (e) {\r\n
            if (this.txtMessage) {\r\n
                this.fireEvent("message:add", [this, this.txtMessage.val().trim()]);\r\n
                this.txtMessage.val("");\r\n
                this.focus();\r\n
            }\r\n
        },\r\n
        _prepareMessage: function (m) {\r\n
            var user = this.storeUsers.findUser(m.get("userid"));\r\n
            m.set({\r\n
                usercolor: user ? user.get("color") : "#000",\r\n
                message: this._pickLink(Common.Utils.String.htmlEncode(m.get("message")))\r\n
            },\r\n
            {\r\n
                silent: true\r\n
            });\r\n
        },\r\n
        _pickLink: function (message) {\r\n
            var arr = [],\r\n
            offset,\r\n
            len;\r\n
            message.replace(Common.Utils.emailStrongRe, function (subStr) {\r\n
                offset = arguments[arguments.length - 2];\r\n
                arr.push({\r\n
                    start: offset,\r\n
                    end: subStr.length + offset,\r\n
                    str: \'<a href="\' + subStr + \'">\' + subStr + "</a>"\r\n
                });\r\n
                return "";\r\n
            });\r\n
            message.replace(Common.Utils.ipStrongRe, function (subStr) {\r\n
                offset = arguments[arguments.length - 2];\r\n
                len = subStr.length;\r\n
                var elem = _.find(arr, function (item) {\r\n
                    return ((offset >= item.start) && (offset < item.end) || (offset <= item.start) && (offset + len > item.start));\r\n
                });\r\n
                if (!elem) {\r\n
                    arr.push({\r\n
                        start: offset,\r\n
                        end: len + offset,\r\n
                        str: \'<a href="\' + subStr + \'" target="_blank" data-can-copy="true">\' + subStr + "</a>"\r\n
                    });\r\n
                }\r\n
                return "";\r\n
            });\r\n
            message.replace(Common.Utils.hostnameStrongRe, function (subStr) {\r\n
                var ref = (!/(((^https?)|(^ftp)):\\/\\/)/i.test(subStr)) ? ("http://" + subStr) : subStr;\r\n
                offset = arguments[arguments.length - 2];\r\n
                len = subStr.length;\r\n
                var elem = _.find(arr, function (item) {\r\n
                    return ((offset >= item.start) && (offset < item.end) || (offset <= item.start) && (offset + len > item.start));\r\n
                });\r\n
                if (!elem) {\r\n
                    arr.push({\r\n
                        start: offset,\r\n
                        end: len + offset,\r\n
                        str: \'<a href="\' + ref + \'" target="_blank" data-can-copy="true">\' + subStr + "</a>"\r\n
                    });\r\n
                }\r\n
                return "";\r\n
            });\r\n
            arr = _.sortBy(arr, function (item) {\r\n
                return item.start;\r\n
            });\r\n
            var str_res = (arr.length > 0) ? (message.substring(0, arr[0].start) + arr[0].str) : message;\r\n
            for (var i = 1; i < arr.length; i++) {\r\n
                str_res += (message.substring(arr[i - 1].end, arr[i].start) + arr[i].str);\r\n
            }\r\n
            if (arr.length > 0) {\r\n
                str_res += message.substring(arr[i - 1].end, message.length);\r\n
            }\r\n
            return str_res;\r\n
        },\r\n
        getUserName: function (username) {\r\n
            return Common.Utils.String.htmlEncode(username);\r\n
        },\r\n
        hide: function () {\r\n
            Common.UI.BaseView.prototype.hide.call(this, arguments);\r\n
            this.fireEvent("hide", this);\r\n
        },\r\n
        textSend: "Send"\r\n
    },\r\n
    Common.Views.Chat || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11269</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
