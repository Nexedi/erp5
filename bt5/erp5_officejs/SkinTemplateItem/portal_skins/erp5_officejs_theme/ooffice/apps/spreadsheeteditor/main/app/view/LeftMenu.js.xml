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
            <value> <string>ts44321338.77</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>LeftMenu.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/LeftMenu.template", "jquery", "underscore", "backbone", "common/main/lib/component/Button", "common/main/lib/view/About", "common/main/lib/view/Comments", "common/main/lib/view/Chat", "common/main/lib/view/SearchDialog", "spreadsheeteditor/main/app/view/FileMenu"], function (menuTemplate, $, _, Backbone) {\r\n
    var SCALE_MIN = 40;\r\n
    var MENU_SCALE_PART = 300;\r\n
    SSE.Views.LeftMenu = Backbone.View.extend(_.extend({\r\n
        el: "#left-menu",\r\n
        template: _.template(menuTemplate),\r\n
        events: function () {\r\n
            return {\r\n
                "click #left-btn-comments": _.bind(this.onCoauthOptions, this),\r\n
                "click #left-btn-chat": _.bind(this.onCoauthOptions, this),\r\n
                "click #left-btn-support": function () {\r\n
                    var config = this.mode.customization;\r\n
                    config && !!config.feedback && !!config.feedback.url ? window.open(config.feedback.url) : window.open("http://feedback.onlyoffice.com/");\r\n
                }\r\n
            };\r\n
        },\r\n
        initialize: function () {\r\n
            this.minimizedMode = true;\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({}));\r\n
            this.btnFile = new Common.UI.Button({\r\n
                action: "file",\r\n
                el: $("#left-btn-file", this.el),\r\n
                hint: this.tipFile + Common.Utils.String.platformKey("Alt+F"),\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "leftMenuGroup"\r\n
            });\r\n
            this.btnSearch = new Common.UI.Button({\r\n
                action: "search",\r\n
                el: $("#left-btn-search", this.el),\r\n
                hint: this.tipSearch + Common.Utils.String.platformKey("Ctrl+F"),\r\n
                disabled: true,\r\n
                enableToggle: true\r\n
            });\r\n
            this.btnAbout = new Common.UI.Button({\r\n
                action: "about",\r\n
                el: $("#left-btn-about", this.el),\r\n
                hint: this.tipAbout,\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "leftMenuGroup"\r\n
            });\r\n
            this.btnSupport = new Common.UI.Button({\r\n
                action: "support",\r\n
                el: $("#left-btn-support", this.el),\r\n
                hint: this.tipSupport,\r\n
                disabled: true\r\n
            });\r\n
            this.btnComments = new Common.UI.Button({\r\n
                el: $("#left-btn-comments", this.el),\r\n
                hint: this.tipComments + Common.Utils.String.platformKey("Ctrl+Shift+H"),\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "leftMenuGroup"\r\n
            });\r\n
            this.btnChat = new Common.UI.Button({\r\n
                el: $("#left-btn-chat", this.el),\r\n
                hint: this.tipChat + Common.Utils.String.platformKey("Ctrl+Alt+Q", null, function (string) {\r\n
                    return Common.Utils.isMac ? string.replace(/Ctrl|ctrl/g, "⌃") : string;\r\n
                }),\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "leftMenuGroup"\r\n
            });\r\n
            this.btnComments.hide();\r\n
            this.btnChat.hide();\r\n
            this.btnComments.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnChat.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnSearch.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnAbout.on("toggle", _.bind(this.onBtnMenuToggle, this));\r\n
            this.btnFile.on("toggle", _.bind(this.onBtnMenuToggle, this));\r\n
            var menuFile = new SSE.Views.FileMenu({});\r\n
            menuFile.options = {\r\n
                alias: "FileMenu"\r\n
            };\r\n
            this.btnFile.panel = menuFile.render();\r\n
            this.btnAbout.panel = (new Common.Views.About({\r\n
                el: $("#about-menu-panel"),\r\n
                appName: "Spreadsheet Editor"\r\n
            })).render();\r\n
            return this;\r\n
        },\r\n
        onBtnMenuToggle: function (btn, state) {\r\n
            if (state) {\r\n
                this.btnFile.pressed && this.fireEvent("file:show", this);\r\n
                btn.panel["show"]();\r\n
                this.$el.width(SCALE_MIN);\r\n
                if (this.btnSearch.isActive()) {\r\n
                    this.btnSearch.toggle(false);\r\n
                }\r\n
            } else {\r\n
                (this.btnFile.id == btn.id) && this.fireEvent("file:hide", this);\r\n
                btn.panel["hide"]();\r\n
            }\r\n
            if (this.mode.isEdit) {\r\n
                SSE.getController("Toolbar").DisableToolbar(state == true);\r\n
            }\r\n
            Common.NotificationCenter.trigger("layout:changed", "leftmenu");\r\n
        },\r\n
        onBtnMenuClick: function (btn, e) {\r\n
            this.btnFile.toggle(false);\r\n
            this.btnAbout.toggle(false);\r\n
            if (btn.options.action == "search") {} else {\r\n
                if (btn.pressed) {\r\n
                    if (! (this.$el.width() > SCALE_MIN)) {\r\n
                        this.$el.width(localStorage.getItem("sse-mainmenu-width") || MENU_SCALE_PART);\r\n
                    }\r\n
                } else {\r\n
                    localStorage.setItem("sse-mainmenu-width", this.$el.width());\r\n
                    this.$el.width(SCALE_MIN);\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("layout:changed", "leftmenu");\r\n
        },\r\n
        onCoauthOptions: function (e) {\r\n
            if (this.mode.canCoAuthoring) {\r\n
                if (this.mode.canComments) {\r\n
                    this.panelComments[this.btnComments.pressed ? "show" : "hide"]();\r\n
                    this.fireEvent((this.btnComments.pressed) ? "comments:show": "comments:hide", this);\r\n
                }\r\n
                if (this.mode.canChat) {\r\n
                    if (this.btnChat.pressed) {\r\n
                        if (this.btnChat.$el.hasClass("notify")) {\r\n
                            this.btnChat.$el.removeClass("notify");\r\n
                        }\r\n
                        this.panelChat.show();\r\n
                        this.panelChat.focus();\r\n
                    } else {\r\n
                        this.panelChat["hide"]();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        setOptionsPanel: function (name, panel) {\r\n
            if (name == "chat") {\r\n
                this.panelChat = panel.render("#left-panel-chat");\r\n
            } else {\r\n
                if (name == "comment") {\r\n
                    this.panelComments = panel;\r\n
                }\r\n
            }\r\n
        },\r\n
        markCoauthOptions: function (opt) {\r\n
            if (this.btnChat.isVisible() && !this.btnChat.isDisabled() && !this.btnChat.pressed) {\r\n
                this.btnChat.$el.addClass("notify");\r\n
            }\r\n
        },\r\n
        close: function (menu) {\r\n
            this.btnFile.toggle(false);\r\n
            this.btnAbout.toggle(false);\r\n
            this.$el.width(SCALE_MIN);\r\n
            if (this.mode.canCoAuthoring) {\r\n
                if (this.mode.canComments) {\r\n
                    this.panelComments["hide"]();\r\n
                    if (this.btnComments.pressed) {\r\n
                        this.fireEvent("comments:hide", this);\r\n
                    }\r\n
                    this.btnComments.toggle(false, true);\r\n
                }\r\n
                if (this.mode.canChat) {\r\n
                    this.panelChat["hide"]();\r\n
                    this.btnChat.toggle(false, true);\r\n
                }\r\n
            }\r\n
        },\r\n
        isOpened: function () {\r\n
            var isopened = this.btnFile.pressed || this.btnSearch.pressed; ! isopened && (isopened = this.btnComments.pressed || this.btnChat.pressed);\r\n
            return isopened;\r\n
        },\r\n
        disableMenu: function (menu, disable) {\r\n
            this.btnFile.setDisabled(false);\r\n
            this.btnAbout.setDisabled(false);\r\n
            this.btnSupport.setDisabled(false);\r\n
            this.btnSearch.setDisabled(false);\r\n
            this.btnComments.setDisabled(false);\r\n
            this.btnChat.setDisabled(false);\r\n
        },\r\n
        showMenu: function (menu) {\r\n
            var re = /^(\\w+):?(\\w*)$/.exec(menu);\r\n
            if (re[1] == "file") {\r\n
                if (!this.btnFile.pressed) {\r\n
                    this.btnFile.toggle(true);\r\n
                    this.btnFile.$el.focus();\r\n
                }\r\n
                this.btnFile.panel.show(re[2].length ? re[2] : undefined);\r\n
            } else {\r\n
                if (menu == "chat") {\r\n
                    if (this.btnChat.isVisible() && !this.btnChat.isDisabled() && !this.btnChat.pressed) {\r\n
                        this.btnChat.toggle(true);\r\n
                        this.onBtnMenuClick(this.btnChat);\r\n
                        this.onCoauthOptions();\r\n
                        this.panelChat.focus();\r\n
                    }\r\n
                } else {\r\n
                    if (menu == "comments") {\r\n
                        if (this.btnComments.isVisible() && !this.btnComments.isDisabled() && !this.btnComments.pressed) {\r\n
                            this.btnComments.toggle(true);\r\n
                            this.onBtnMenuClick(this.btnComments);\r\n
                            this.onCoauthOptions();\r\n
                            this.btnComments.$el.focus();\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        getMenu: function (type) {\r\n
            switch (type) {\r\n
            case "file":\r\n
                return this.btnFile.panel;\r\n
            case "about":\r\n
                return this.btnAbout.panel;\r\n
            default:\r\n
                return null;\r\n
            }\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            return this;\r\n
        },\r\n
        tipComments: "Comments",\r\n
        tipChat: "Chat",\r\n
        tipAbout: "About",\r\n
        tipSupport: "Feedback & Support",\r\n
        tipFile: "File",\r\n
        tipSearch: "Search"\r\n
    },\r\n
    SSE.Views.LeftMenu || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11714</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
