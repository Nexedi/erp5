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
            <value> <string>ts44308425.32</string> </value>
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
 define(["core", "common/main/lib/util/Shortcuts", "spreadsheeteditor/main/app/view/LeftMenu", "spreadsheeteditor/main/app/view/FileMenu"], function () {\r\n
    SSE.Controllers.LeftMenu = Backbone.Controller.extend(_.extend({\r\n
        views: ["LeftMenu", "FileMenu"],\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "Common.Views.Chat": {\r\n
                    "hide": _.bind(this.onHideChat, this)\r\n
                },\r\n
                "Statusbar": {\r\n
                    "click:users": _.bind(this.clickStatusbarUsers, this)\r\n
                },\r\n
                "LeftMenu": {\r\n
                    "file:show": _.bind(this.fileShowHide, this, true),\r\n
                    "file:hide": _.bind(this.fileShowHide, this, false),\r\n
                    "comments:show": _.bind(this.commentsShowHide, this, true),\r\n
                    "comments:hide": _.bind(this.commentsShowHide, this, false),\r\n
                },\r\n
                "Common.Views.About": {\r\n
                    "show": _.bind(this.aboutShowHide, this, true),\r\n
                    "hide": _.bind(this.aboutShowHide, this, false)\r\n
                },\r\n
                "FileMenu": {\r\n
                    "item:click": _.bind(this.clickMenuFileItem, this),\r\n
                    "saveas:format": _.bind(this.clickSaveAsFormat, this),\r\n
                    "settings:apply": _.bind(this.applySettings, this),\r\n
                    "create:new": _.bind(this.onCreateNew, this),\r\n
                    "recent:open": _.bind(this.onOpenRecent, this)\r\n
                },\r\n
                "Toolbar": {\r\n
                    "file:settings": _.bind(this.clickToolbarSettings, this)\r\n
                },\r\n
                "SearchDialog": {\r\n
                    "hide": _.bind(this.onSearchDlgHide, this),\r\n
                    "search:back": _.bind(this.onQuerySearch, this, "back"),\r\n
                    "search:next": _.bind(this.onQuerySearch, this, "next"),\r\n
                    "search:replace": _.bind(this.onQueryReplace, this),\r\n
                    "search:replaceall": _.bind(this.onQueryReplaceAll, this)\r\n
                }\r\n
            });\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.leftMenu = this.createView("LeftMenu").render();\r\n
            this.leftMenu.btnSearch.on("toggle", _.bind(this.onMenuSearch, this));\r\n
            Common.util.Shortcuts.delegateShortcuts({\r\n
                shortcuts: {\r\n
                    "command+shift+s,ctrl+shift+s": _.bind(this.onShortcut, this, "save"),\r\n
                    "command+f,ctrl+f": _.bind(this.onShortcut, this, "search"),\r\n
                    "command+h,ctrl+h": _.bind(this.onShortcut, this, "replace"),\r\n
                    "alt+f": _.bind(this.onShortcut, this, "file"),\r\n
                    "esc": _.bind(this.onShortcut, this, "escape"),\r\n
                    "ctrl+alt+q": _.bind(this.onShortcut, this, "chat"),\r\n
                    "command+shift+h,ctrl+shift+h": _.bind(this.onShortcut, this, "comments"),\r\n
                    "f1": _.bind(this.onShortcut, this, "help")\r\n
                }\r\n
            });\r\n
            Common.util.Shortcuts.suspendEvents();\r\n
            var me = this;\r\n
            this.leftMenu.$el.find("button").each(function () {\r\n
                $(this).on("keydown", function (e) {\r\n
                    if (Common.UI.Keys.RETURN === e.keyCode || Common.UI.Keys.SPACE === e.keyCode) {\r\n
                        me.leftMenu.btnFile.toggle(false);\r\n
                        me.leftMenu.btnAbout.toggle(false);\r\n
                        this.blur();\r\n
                        e.preventDefault();\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                    }\r\n
                });\r\n
            });\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.asc_registerCallback("asc_onRenameCellTextEnd", _.bind(this.onRenameText, this));\r\n
            this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onApiServerDisconnect, this));\r\n
            Common.NotificationCenter.on("api:disconnect", _.bind(this.onApiServerDisconnect, this));\r\n
            if (this.mode.canCoAuthoring && this.mode.canChat) {\r\n
                this.api.asc_registerCallback("asc_onCoAuthoringChatReceiveMessage", _.bind(this.onApiChatMessage, this));\r\n
            }\r\n
            if (!this.mode.isEditDiagram) {\r\n
                this.api.asc_registerCallback("asc_onEditCell", _.bind(this.onApiEditCell, this));\r\n
            }\r\n
            this.leftMenu.getMenu("file").setApi(api);\r\n
            return this;\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            this.leftMenu.setMode(mode);\r\n
            this.leftMenu.getMenu("file").setMode(mode);\r\n
            return this;\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            if (this.mode.canCoAuthoring) {\r\n
                this.leftMenu.btnComments[this.mode.isEdit && this.mode.canComments ? "show" : "hide"]();\r\n
                if (this.mode.canComments) {\r\n
                    this.leftMenu.setOptionsPanel("comment", this.getApplication().getController("Common.Controllers.Comments").getView("Common.Views.Comments"));\r\n
                }\r\n
                this.leftMenu.btnChat[this.mode.canChat ? "show" : "hide"]();\r\n
                if (this.mode.canChat) {\r\n
                    this.leftMenu.setOptionsPanel("chat", this.getApplication().getController("Common.Controllers.Chat").getView("Common.Views.Chat"));\r\n
                }\r\n
            } else {\r\n
                this.leftMenu.btnChat.hide();\r\n
                this.leftMenu.btnComments.hide();\r\n
            }\r\n
            Common.util.Shortcuts.resumeEvents();\r\n
            if (!this.mode.isEditDiagram) {\r\n
                Common.NotificationCenter.on("cells:range", _.bind(this.onCellsRange, this));\r\n
            }\r\n
            return this;\r\n
        },\r\n
        clickMenuFileItem: function (menu, action, isopts) {\r\n
            var close_menu = true;\r\n
            switch (action) {\r\n
            case "back":\r\n
                break;\r\n
            case "save":\r\n
                this.api.asc_Save();\r\n
                break;\r\n
            case "print":\r\n
                this.api.asc_Print();\r\n
                break;\r\n
            case "exit":\r\n
                Common.Gateway.goBack();\r\n
                break;\r\n
            case "edit":\r\n
                Common.Gateway.requestEditRights();\r\n
                break;\r\n
            case "new":\r\n
                if (isopts) {\r\n
                    close_menu = false;\r\n
                } else {\r\n
                    this.onCreateNew(undefined, "blank");\r\n
                }\r\n
                break;\r\n
            default:\r\n
                close_menu = false;\r\n
            }\r\n
            if (close_menu) {\r\n
                menu.hide();\r\n
                this.leftMenu.btnFile.toggle(false, true);\r\n
            }\r\n
        },\r\n
        clickSaveAsFormat: function (menu, format) {\r\n
            if (format == c_oAscFileType.CSV || format != c_oAscFileType.XLSX && this.api.asc_drawingObjectsExist()) {\r\n
                Common.UI.warning({\r\n
                    closable: false,\r\n
                    title: this.textWarning,\r\n
                    msg: this.warnDownloadAs,\r\n
                    buttons: ["ok", "cancel"],\r\n
                    callback: _.bind(function (btn) {\r\n
                        if (btn == "ok") {\r\n
                            this.api.asc_DownloadAs(format);\r\n
                            menu.hide();\r\n
                            this.leftMenu.btnFile.toggle(false, true);\r\n
                        }\r\n
                    },\r\n
                    this)\r\n
                });\r\n
            } else {\r\n
                this.api.asc_DownloadAs(format);\r\n
                menu.hide();\r\n
                this.leftMenu.btnFile.toggle(false, true);\r\n
            }\r\n
        },\r\n
        applySettings: function (menu) {\r\n
            this.api.asc_setFontRenderingMode(parseInt(window.localStorage.getItem("sse-settings-fontrender")));\r\n
            var value = window.localStorage.getItem("sse-settings-livecomment");\r\n
            (!(value !== null && parseInt(value) == 0)) ? this.api.asc_showComments() : this.api.asc_hideComments();\r\n
            if (this.mode.canAutosave) {\r\n
                value = window.localStorage.getItem("sse-settings-autosave");\r\n
                this.api.asc_setAutoSaveGap(parseInt(value));\r\n
            }\r\n
            menu.hide();\r\n
            this.leftMenu.btnFile.toggle(false, true);\r\n
        },\r\n
        onCreateNew: function (menu, type) {\r\n
            if (this.mode.nativeApp === true) {\r\n
                this.api.asc_openNewDocument(type == "blank" ? "" : type);\r\n
            } else {\r\n
                var newDocumentPage = window.open(_.template("<%= url %>?title=<%= title %>" + \'<% if (doctype != "blank") { %>&template=<%= doctype %><% } %>\' + "&action=create&doctype=spreadsheet", {\r\n
                    url: this.mode.createUrl,\r\n
                    title: this.newDocumentTitle,\r\n
                    doctype: type\r\n
                }));\r\n
                if (newDocumentPage) {\r\n
                    newDocumentPage.focus();\r\n
                }\r\n
            }\r\n
            if (menu) {\r\n
                menu.hide();\r\n
                this.leftMenu.btnFile.toggle(false, true);\r\n
            }\r\n
        },\r\n
        onOpenRecent: function (menu, url) {\r\n
            if (menu) {\r\n
                menu.hide();\r\n
                this.leftMenu.btnFile.toggle(false, true);\r\n
            }\r\n
            var recentDocPage = window.open(url);\r\n
            if (recentDocPage) {\r\n
                recentDocPage.focus();\r\n
            }\r\n
            Common.component.Analytics.trackEvent("Open Recent");\r\n
        },\r\n
        clickToolbarSettings: function (obj) {\r\n
            if (this.leftMenu.btnFile.pressed && this.leftMenu.btnFile.panel.active == "opts") {\r\n
                this.leftMenu.close();\r\n
            } else {\r\n
                this.leftMenu.showMenu("file:opts");\r\n
            }\r\n
        },\r\n
        clickStatusbarUsers: function () {\r\n
            if (this.mode.canCoAuthoring && this.mode.canChat) {\r\n
                if (this.leftMenu.btnChat.pressed) {\r\n
                    this.leftMenu.close();\r\n
                } else {\r\n
                    this.leftMenu.showMenu("chat");\r\n
                }\r\n
            }\r\n
        },\r\n
        onHideChat: function () {\r\n
            $(this.leftMenu.btnChat.el).blur();\r\n
            Common.NotificationCenter.trigger("layout:changed", "leftmenu");\r\n
        },\r\n
        onQuerySearch: function (d, w, opts) {\r\n
            if (opts.textsearch && opts.textsearch.length) {\r\n
                var options = this.dlgSearch.findOptions;\r\n
                options.asc_setFindWhat(opts.textsearch);\r\n
                options.asc_setScanForward(d != "back");\r\n
                options.asc_setIsMatchCase(opts.matchcase);\r\n
                options.asc_setIsWholeCell(opts.matchword);\r\n
                options.asc_setScanOnOnlySheet(this.dlgSearch.menuWithin.menu.items[0].checked);\r\n
                options.asc_setScanByRows(this.dlgSearch.menuSearch.menu.items[0].checked);\r\n
                options.asc_setLookIn(this.dlgSearch.menuLookin.menu.items[0].checked ? c_oAscFindLookIn.Formulas : c_oAscFindLookIn.Value);\r\n
                if (!this.api.asc_findText(options)) {\r\n
                    var me = this;\r\n
                    Common.UI.info({\r\n
                        msg: this.textNoTextFound,\r\n
                        callback: function () {\r\n
                            me.dlgSearch.focus();\r\n
                        }\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        onQueryReplace: function (w, opts) {\r\n
            if (!_.isEmpty(opts.textsearch) && !_.isEmpty(opts.textreplace)) {\r\n
                this.api.isReplaceAll = false;\r\n
                var options = this.dlgSearch.findOptions;\r\n
                options.asc_setFindWhat(opts.textsearch);\r\n
                options.asc_setReplaceWith(opts.textreplace);\r\n
                options.asc_setIsMatchCase(opts.matchcase);\r\n
                options.asc_setIsWholeCell(opts.matchword);\r\n
                options.asc_setScanOnOnlySheet(this.dlgSearch.menuWithin.menu.items[0].checked);\r\n
                options.asc_setScanByRows(this.dlgSearch.menuSearch.menu.items[0].checked);\r\n
                options.asc_setLookIn(this.dlgSearch.menuLookin.menu.items[0].checked ? c_oAscFindLookIn.Formulas : c_oAscFindLookIn.Value);\r\n
                options.asc_setIsReplaceAll(false);\r\n
                this.api.asc_replaceText(options);\r\n
            }\r\n
        },\r\n
        onQueryReplaceAll: function (w, opts) {\r\n
            if (!_.isEmpty(opts.textsearch) && !_.isEmpty(opts.textreplace)) {\r\n
                this.api.isReplaceAll = true;\r\n
                var options = this.dlgSearch.findOptions;\r\n
                options.asc_setFindWhat(opts.textsearch);\r\n
                options.asc_setReplaceWith(opts.textreplace);\r\n
                options.asc_setIsMatchCase(opts.matchcase);\r\n
                options.asc_setIsWholeCell(opts.matchword);\r\n
                options.asc_setScanOnOnlySheet(this.dlgSearch.menuWithin.menu.items[0].checked);\r\n
                options.asc_setScanByRows(this.dlgSearch.menuSearch.menu.items[0].checked);\r\n
                options.asc_setLookIn(this.dlgSearch.menuLookin.menu.items[0].checked ? c_oAscFindLookIn.Formulas : c_oAscFindLookIn.Value);\r\n
                options.asc_setIsReplaceAll(true);\r\n
                this.api.asc_replaceText(options);\r\n
            }\r\n
        },\r\n
        showSearchDlg: function (show, action) {\r\n
            if (!this.dlgSearch) {\r\n
                var menuWithin = new Common.UI.MenuItem({\r\n
                    caption: this.textWithin,\r\n
                    menu: new Common.UI.Menu({\r\n
                        menuAlign: "tl-tr",\r\n
                        items: [{\r\n
                            caption: this.textSheet,\r\n
                            toggleGroup: "searchWithih",\r\n
                            checkable: true,\r\n
                            checked: true\r\n
                        },\r\n
                        {\r\n
                            caption: this.textWorkbook,\r\n
                            toggleGroup: "searchWithih",\r\n
                            checkable: true,\r\n
                            checked: false\r\n
                        }]\r\n
                    })\r\n
                });\r\n
                var menuSearch = new Common.UI.MenuItem({\r\n
                    caption: this.textSearch,\r\n
                    menu: new Common.UI.Menu({\r\n
                        menuAlign: "tl-tr",\r\n
                        items: [{\r\n
                            caption: this.textByRows,\r\n
                            toggleGroup: "searchByrows",\r\n
                            checkable: true,\r\n
                            checked: true\r\n
                        },\r\n
                        {\r\n
                            caption: this.textByColumns,\r\n
                            toggleGroup: "searchByrows",\r\n
                            checkable: true,\r\n
                            checked: false\r\n
                        }]\r\n
                    })\r\n
                });\r\n
                var menuLookin = new Common.UI.MenuItem({\r\n
                    caption: this.textLookin,\r\n
                    menu: new Common.UI.Menu({\r\n
                        menuAlign: "tl-tr",\r\n
                        items: [{\r\n
                            caption: this.textFormulas,\r\n
                            toggleGroup: "searchLookin",\r\n
                            checkable: true,\r\n
                            checked: true\r\n
                        },\r\n
                        {\r\n
                            caption: this.textValues,\r\n
                            toggleGroup: "searchLookin",\r\n
                            checkable: true,\r\n
                            checked: false\r\n
                        }]\r\n
                    })\r\n
                });\r\n
                this.dlgSearch = (new Common.UI.SearchDialog({\r\n
                    matchcase: true,\r\n
                    matchword: true,\r\n
                    matchwordstr: this.textItemEntireCell,\r\n
                    markresult: false,\r\n
                    extraoptions: [menuWithin, menuSearch, menuLookin]\r\n
                }));\r\n
                this.dlgSearch.menuWithin = menuWithin;\r\n
                this.dlgSearch.menuSearch = menuSearch;\r\n
                this.dlgSearch.menuLookin = menuLookin;\r\n
                this.dlgSearch.findOptions = new Asc.asc_CFindOptions();\r\n
            }\r\n
            if (show) {\r\n
                var mode = this.mode.isEdit ? (action || undefined) : "no-replace";\r\n
                if (this.dlgSearch.isVisible()) {\r\n
                    this.dlgSearch.setMode(mode);\r\n
                    this.dlgSearch.focus();\r\n
                } else {\r\n
                    this.dlgSearch.show(mode);\r\n
                }\r\n
                this.api.asc_closeCellEditor();\r\n
            } else {\r\n
                this.dlgSearch["hide"]();\r\n
            }\r\n
        },\r\n
        onMenuSearch: function (obj, show) {\r\n
            this.showSearchDlg(show);\r\n
        },\r\n
        onSearchDlgHide: function () {\r\n
            this.leftMenu.btnSearch.toggle(false, true);\r\n
            $(this.leftMenu.btnSearch.el).blur();\r\n
            this.api.asc_enableKeyEvents(true);\r\n
        },\r\n
        onRenameText: function (found, replaced) {\r\n
            var me = this;\r\n
            if (this.api.isReplaceAll) {\r\n
                Common.UI.info({\r\n
                    msg: (found) ? ((!found - replaced) ? Common.Utils.String.format(this.textReplaceSuccess, replaced) : Common.Utils.String.format(this.textReplaceSkipped, found - replaced)) : this.textNoTextFound,\r\n
                    callback: function () {\r\n
                        me.dlgSearch.focus();\r\n
                    }\r\n
                });\r\n
            } else {\r\n
                var sett = this.dlgSearch.getSettings();\r\n
                var options = this.dlgSearch.findOptions;\r\n
                options.asc_setFindWhat(sett.textsearch);\r\n
                options.asc_setScanForward(true);\r\n
                options.asc_setIsMatchCase(sett.matchcase);\r\n
                options.asc_setIsWholeCell(sett.matchword);\r\n
                options.asc_setScanOnOnlySheet(this.dlgSearch.menuWithin.menu.items[0].checked);\r\n
                options.asc_setScanByRows(this.dlgSearch.menuSearch.menu.items[0].checked);\r\n
                options.asc_setLookIn(this.dlgSearch.menuLookin.menu.items[0].checked ? c_oAscFindLookIn.Formulas : c_oAscFindLookIn.Value);\r\n
                if (!me.api.asc_findText(options)) {\r\n
                    Common.UI.info({\r\n
                        msg: this.textNoTextFound,\r\n
                        callback: function () {\r\n
                            me.dlgSearch.focus();\r\n
                        }\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiServerDisconnect: function () {\r\n
            this.mode.isEdit = false;\r\n
            this.leftMenu.close();\r\n
            this.leftMenu.btnComments.setDisabled(true);\r\n
            this.leftMenu.btnChat.setDisabled(true);\r\n
            this.leftMenu.getMenu("file").setMode({\r\n
                isDisconnected: true\r\n
            });\r\n
            if (this.dlgSearch) {\r\n
                this.leftMenu.btnSearch.toggle(false, true);\r\n
                this.dlgSearch["hide"]();\r\n
            }\r\n
        },\r\n
        onApiChatMessage: function () {\r\n
            this.leftMenu.markCoauthOptions();\r\n
        },\r\n
        commentsShowHide: function (state) {\r\n
            if (this.api) {\r\n
                var value = window.localStorage.getItem("sse-settings-livecomment");\r\n
                if (value !== null && parseInt(value) == 0) {\r\n
                    (state) ? this.api.asc_showComments() : this.api.asc_hideComments();\r\n
                }\r\n
                if (state) {\r\n
                    this.getApplication().getController("Common.Controllers.Comments").focusOnInput();\r\n
                }\r\n
                this.api.asc_enableKeyEvents(!state);\r\n
                if (!state) {\r\n
                    $(this.leftMenu.btnComments.el).blur();\r\n
                }\r\n
            }\r\n
        },\r\n
        fileShowHide: function (state) {\r\n
            if (this.api) {\r\n
                this.api.asc_closeCellEditor();\r\n
                this.api.asc_enableKeyEvents(!state);\r\n
                if (!state) {\r\n
                    $(this.leftMenu.btnFile.el).blur();\r\n
                }\r\n
            }\r\n
        },\r\n
        aboutShowHide: function (state) {\r\n
            if (this.api) {\r\n
                this.api.asc_closeCellEditor();\r\n
                this.api.asc_enableKeyEvents(!state);\r\n
                if (!state) {\r\n
                    $(this.leftMenu.btnAbout.el).blur();\r\n
                }\r\n
            }\r\n
        },\r\n
        onShortcut: function (s, e) {\r\n
            if (this.mode.isEditDiagram && s != "escape") {\r\n
                return false;\r\n
            }\r\n
            switch (s) {\r\n
            case "replace":\r\n
                case "search":\r\n
                if (!this.leftMenu.btnSearch.isDisabled()) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.showSearchDlg(true, s);\r\n
                    this.leftMenu.btnSearch.toggle(true, true);\r\n
                    this.leftMenu.btnFile.toggle(false);\r\n
                    this.leftMenu.btnAbout.toggle(false);\r\n
                }\r\n
                return false;\r\n
            case "save":\r\n
                if (this.mode.canDownload && !this.leftMenu.btnFile.isDisabled()) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.leftMenu.showMenu("file:saveas");\r\n
                }\r\n
                return false;\r\n
            case "help":\r\n
                if (!this.leftMenu.btnFile.isDisabled()) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.api.asc_closeCellEditor();\r\n
                    this.leftMenu.showMenu("file:help");\r\n
                }\r\n
                return false;\r\n
            case "file":\r\n
                if (!this.leftMenu.btnFile.isDisabled()) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.leftMenu.showMenu("file");\r\n
                }\r\n
                return false;\r\n
            case "escape":\r\n
                var statusbar = SSE.getController("Statusbar");\r\n
                var menu_opened = statusbar.statusbar.$el.find(\'.open > [data-toggle="dropdown"]\');\r\n
                if (menu_opened.length) {\r\n
                    $.fn.dropdown.Constructor.prototype.keydown.call(menu_opened[0], e);\r\n
                    return false;\r\n
                }\r\n
                if (this.leftMenu.btnFile.pressed || this.leftMenu.btnAbout.pressed || $(e.target).parents("#left-menu").length && this.api.isCellEdited !== true) {\r\n
                    this.leftMenu.close();\r\n
                    Common.NotificationCenter.trigger("layout:changed", "leftmenu");\r\n
                    return false;\r\n
                }\r\n
                if (this.mode.isEditDiagram) {\r\n
                    menu_opened = $(document.body).find(".open > .dropdown-menu");\r\n
                    if (!this.api.isCellEdited && !menu_opened.length) {\r\n
                        Common.Gateway.internalMessage("shortcut", {\r\n
                            key: "escape"\r\n
                        });\r\n
                        return false;\r\n
                    }\r\n
                }\r\n
                break;\r\n
            case "chat":\r\n
                if (this.mode.canCoAuthoring && this.mode.canChat) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.leftMenu.showMenu("chat");\r\n
                }\r\n
                return false;\r\n
            case "comments":\r\n
                if (this.mode.canCoAuthoring && this.mode.isEdit && this.mode.canComments) {\r\n
                    Common.UI.Menu.Manager.hideAll();\r\n
                    this.leftMenu.showMenu("comments");\r\n
                    this.getApplication().getController("Common.Controllers.Comments").focusOnInput();\r\n
                }\r\n
                return false;\r\n
            }\r\n
        },\r\n
        onCellsRange: function (status) {\r\n
            var isRangeSelection = (status != c_oAscSelectionDialogType.None);\r\n
            this.leftMenu.btnFile.setDisabled(isRangeSelection);\r\n
            this.leftMenu.btnAbout.setDisabled(isRangeSelection);\r\n
            this.leftMenu.btnSearch.setDisabled(isRangeSelection);\r\n
        },\r\n
        onApiEditCell: function (state) {\r\n
            var isEditFormula = (state == c_oAscCellEditorState.editFormula);\r\n
            this.leftMenu.btnFile.setDisabled(isEditFormula);\r\n
            this.leftMenu.btnAbout.setDisabled(isEditFormula);\r\n
            this.leftMenu.btnSearch.setDisabled(isEditFormula);\r\n
        },\r\n
        textNoTextFound: "Text not found",\r\n
        newDocumentTitle: "Unnamed document",\r\n
        textItemEntireCell: "Entire cell contents",\r\n
        requestEditRightsText: "Requesting editing rights...",\r\n
        textReplaceSuccess: "Search has been done. {0} occurrences have been replaced",\r\n
        textReplaceSkipped: "The replacement has been made. {0} occurrences were skipped.",\r\n
        warnDownloadAs: "If you continue saving in this format all features except the text will be lost.<br>Are you sure you want to continue?",\r\n
        textWarning : "Warning",\r\n
        textSheet: "Sheet",\r\n
        textWorkbook: "Workbook",\r\n
        textByColumns: "By columns",\r\n
        textByRows: "By rows",\r\n
        textFormulas: "Formulas",\r\n
        textValues: "Values",\r\n
        textWithin: "Within",\r\n
        textSearch: "Search",\r\n
        textLookin: "Look in"\r\n
    },\r\n
    SSE.Controllers.LeftMenu || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>27176</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
