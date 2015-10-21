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
            <value> <string>ts44308425.42</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Main.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>68315</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
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
 define(["core", "irregularstack", "common/main/lib/component/Window", "common/main/lib/component/LoadMask", "common/main/lib/component/Tooltip", "common/main/lib/controller/Fonts", "spreadsheeteditor/main/app/collection/ShapeGroups", "spreadsheeteditor/main/app/collection/TableTemplates", "spreadsheeteditor/main/app/controller/FormulaDialog", "spreadsheeteditor/main/app/view/OpenDialog"], function () {\r\n
    SSE.Controllers.Main = Backbone.Controller.extend(_.extend((function () {\r\n
        var InitApplication = -254;\r\n
        var ApplyEditRights = -255;\r\n
        var LoadingDocument = -256;\r\n
        var mapCustomizationElements = {\r\n
            about: "button#left-btn-about",\r\n
            feedback: "button#left-btn-support",\r\n
            goback: "#fm-btn-back > a, #header-back > div"\r\n
        };\r\n
        return {\r\n
            models: [],\r\n
            collections: ["ShapeGroups", "TableTemplates"],\r\n
            views: [],\r\n
            initialize: function () {},\r\n
            onLaunch: function () {\r\n
                window.asc_CCommentData = window.Asc.asc_CCommentData || window.asc_CCommentData;\r\n
                window.storagename = "table";\r\n
                this._state = {};\r\n
                if (!Common.Utils.isBrowserSupported()) {\r\n
                    Common.Utils.showBrowserRestriction();\r\n
                    Common.Gateway.reportError(undefined, this.unsupportedBrowserErrorText);\r\n
                    return;\r\n
                } else {}\r\n
                var value = window.localStorage.getItem("sse-settings-fontrender");\r\n
                if (value === null) {\r\n
                    value = window.devicePixelRatio > 1 ? "1" : "3";\r\n
                }\r\n
                this.api = new Asc.spreadsheet_api("editor_sdk", "ce-cell-content");\r\n
                this.api.asc_setFontRenderingMode(parseInt(value));\r\n
                this.api.asc_Init("../../../sdk/Fonts/");\r\n
                this.api.asc_registerCallback("asc_onOpenDocumentProgress", _.bind(this.onOpenDocument, this));\r\n
                this.api.asc_registerCallback("asc_onEndAction", _.bind(this.onLongActionEnd, this));\r\n
                this.api.asc_registerCallback("asc_onError", _.bind(this.onError, this));\r\n
                this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onCoAuthoringDisconnect, this));\r\n
                this.api.asc_registerCallback("asc_onAdvancedOptions", _.bind(this.onAdvancedOptions, this));\r\n
                this.api.asc_registerCallback("asc_onDocumentUpdateVersion", _.bind(this.onUpdateVersion, this));\r\n
                Common.NotificationCenter.on("api:disconnect", _.bind(this.onCoAuthoringDisconnect, this));\r\n
                this.stackLongActions = new Common.IrregularStack({\r\n
                    strongCompare: this._compareActionStrong,\r\n
                    weakCompare: this._compareActionWeak\r\n
                });\r\n
                this.stackLongActions.push({\r\n
                    id: InitApplication,\r\n
                    type: c_oAscAsyncActionType.BlockInteraction\r\n
                });\r\n
                this.isShowOpenDialog = false;\r\n
                this.editorConfig = {};\r\n
                Common.Gateway.on("init", _.bind(this.loadConfig, this));\r\n
                Common.Gateway.on("showmessage", _.bind(this.onExternalMessage, this));\r\n
                Common.Gateway.on("opendocument", _.bind(this.loadDocument, this));\r\n
                Common.Gateway.on("internalcommand", _.bind(this.onInternalCommand, this));\r\n
                Common.Gateway.ready();\r\n
                this.getApplication().getController("Viewport").setApi(this.api);\r\n
                var me = this;\r\n
                $(document.body).on("focus", "input, textarea:not(#ce-cell-content)", function (e) {\r\n
                    if (e && e.target && e.target.id && e.target.id === "clipboard-helper-text") {\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                        return;\r\n
                    }\r\n
                    if (this.isAppDisabled === true) {\r\n
                        return;\r\n
                    }\r\n
                    me.api.asc_enableKeyEvents(false);\r\n
                });\r\n
                $("#editor_sdk").focus(function (e) {\r\n
                    if (this.isAppDisabled === true) {\r\n
                        return;\r\n
                    }\r\n
                    if (!me.isModalShowed) {\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                    }\r\n
                });\r\n
                $(document.body).on("blur", "input, textarea", function (e) {\r\n
                    if (this.isAppDisabled === true) {\r\n
                        return;\r\n
                    }\r\n
                    if (!me.isModalShowed) {\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                    }\r\n
                });\r\n
                Common.NotificationCenter.on({\r\n
                    "modal:show": function (e) {\r\n
                        me.isModalShowed = true;\r\n
                        me.api.asc_enableKeyEvents(false);\r\n
                    },\r\n
                    "modal:close": function (dlg) {\r\n
                        if (dlg && dlg.$lastmodal && dlg.$lastmodal.size() < 1) {\r\n
                            me.isModalShowed = false;\r\n
                            me.api.asc_enableKeyEvents(true);\r\n
                        }\r\n
                    },\r\n
                    "modal:hide": function (dlg) {\r\n
                        if (dlg && dlg.$lastmodal && dlg.$lastmodal.size() < 1) {\r\n
                            me.isModalShowed = false;\r\n
                            me.api.asc_enableKeyEvents(true);\r\n
                        }\r\n
                    },\r\n
                    "edit:complete": _.bind(this.onEditComplete, this),\r\n
                    "settings:unitschanged": _.bind(this.unitsChanged, this)\r\n
                });\r\n
                this.initNames();\r\n
                Common.util.Shortcuts.delegateShortcuts({\r\n
                    shortcuts: {\r\n
                        "command+s,ctrl+s": _.bind(function (e) {\r\n
                            e.preventDefault();\r\n
                            e.stopPropagation();\r\n
                        },\r\n
                        this)\r\n
                    }\r\n
                });\r\n
            },\r\n
            loadConfig: function (data) {\r\n
                this.editorConfig = $.extend(this.editorConfig, data.config);\r\n
                if ((this.editorConfig.user === undefined || this.editorConfig.user === null)) {\r\n
                    this.editorConfig.user = {};\r\n
                    if (this.editorConfig.users) {\r\n
                        this.editorConfig.userId = this.editorConfig.userId || 0;\r\n
                        for (var i = 0; i < this.editorConfig.users.length; i++) {\r\n
                            if (this.editorConfig.users[i].id === this.editorConfig.userId) {\r\n
                                this.editorConfig.user = {\r\n
                                    id: this.editorConfig.users[i].id,\r\n
                                    name: this.editorConfig.users[i].username\r\n
                                };\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
                this.editorConfig.user.id = this.editorConfig.user.id || ("uid-" + Date.now());\r\n
                this.editorConfig.user.name = this.editorConfig.user.name || this.textAnonymous;\r\n
                this.appOptions = {};\r\n
                this.appOptions.user = this.editorConfig.user;\r\n
                this.appOptions.canBack = this.editorConfig.nativeApp !== true && this.editorConfig.canBackToFolder === true;\r\n
                this.appOptions.nativeApp = this.editorConfig.nativeApp === true;\r\n
                this.appOptions.isDesktopApp = this.editorConfig.targetApp == "desktop";\r\n
                this.appOptions.canCreateNew = !_.isEmpty(this.editorConfig.createUrl) && !this.appOptions.isDesktopApp;\r\n
                this.appOptions.canOpenRecent = this.editorConfig.nativeApp !== true && this.editorConfig.recent !== undefined && !this.appOptions.isDesktopApp;\r\n
                this.appOptions.templates = this.editorConfig.templates;\r\n
                this.appOptions.recent = this.editorConfig.recent;\r\n
                this.appOptions.createUrl = this.editorConfig.createUrl;\r\n
                this.appOptions.lang = this.editorConfig.lang;\r\n
                this.appOptions.canAutosave = -1;\r\n
                this.appOptions.canAnalytics = false;\r\n
                this.appOptions.sharingSettingsUrl = this.editorConfig.sharingSettingsUrl;\r\n
                this.appOptions.isEditDiagram = this.editorConfig.mode == "editdiagram";\r\n
                this.appOptions.customization = this.editorConfig.customization;\r\n
                this.headerView = this.getApplication().getController("Viewport").getView("Common.Views.Header");\r\n
                this.headerView.setCanBack(this.editorConfig.canBackToFolder === true);\r\n
                if (this.editorConfig.lang) {\r\n
                    this.api.asc_setLocale(this.editorConfig.lang);\r\n
                }\r\n
            },\r\n
            loadDocument: function (data) {\r\n
                this.appOptions.spreadsheet = data.doc;\r\n
                this.permissions = {};\r\n
                var docInfo = {};\r\n
                if (data.doc) {\r\n
                    this.permissions = _.extend(this.permissions, data.doc.permissions);\r\n
                    docInfo.Id = data.doc.key;\r\n
                    docInfo.Url = data.doc.url;\r\n
                    docInfo.Data = data.doc.data;\r\n
                    docInfo.Title = data.doc.title;\r\n
                    docInfo.Format = data.doc.fileType;\r\n
                    docInfo.Options = data.doc.options;\r\n
                    docInfo.UserId = this.editorConfig.user.id;\r\n
                    docInfo.UserName = this.editorConfig.user.name;\r\n
                    docInfo.VKey = data.doc.vkey;\r\n
                    docInfo.Origin = data.doc.origin;\r\n
                    docInfo.CallbackUrl = this.editorConfig.callbackUrl;\r\n
                    this.headerView.setDocumentCaption(data.doc.title);\r\n
                }\r\n
                if (this.appOptions.isEditDiagram) {\r\n
                    this.onEditorPermissions(undefined);\r\n
                } else {\r\n
                    this.api.asc_registerCallback("asc_onGetEditorPermissions", _.bind(this.onEditorPermissions, this));\r\n
                    this.api.asc_setDocInfo(docInfo);\r\n
                    this.api.asc_getEditorPermissions();\r\n
                }\r\n
            },\r\n
            onProcessSaveResult: function (data) {\r\n
                //XXX\r\n
                //this.api.asc_OnSaveEnd(data.result);\r\n
                if (data && data.result === false) {\r\n
                    Common.UI.error({\r\n
                        title: this.criticalErrorTitle,\r\n
                        msg: _.isEmpty(data.message) ? this.errorProcessSaveResult : data.message\r\n
                    });\r\n
                }\r\n
            },\r\n
            onProcessRightsChange: function (data) {\r\n
                if (data && data.enabled === false) {\r\n
                    this.api.asc_coAuthoringDisconnect();\r\n
                    this.getApplication().getController("LeftMenu").leftMenu.getMenu("file").panels["rights"].onLostEditRights();\r\n
                    Common.UI.warning({\r\n
                        title: this.notcriticalErrorTitle,\r\n
                        msg: _.isEmpty(data.message) ? this.warnProcessRightsChange : data.message\r\n
                    });\r\n
                }\r\n
            },\r\n
            onProcessMouse: function (data) {\r\n
                if (data.type == "mouseup") {\r\n
                    var editor = document.getElementById("editor_sdk");\r\n
                    if (editor) {\r\n
                        var rect = editor.getBoundingClientRect();\r\n
                        var event = window.event || arguments.callee.caller.arguments[0];\r\n
                        this.api.asc_onMouseUp(event, data.x - rect.left, data.y - rect.top);\r\n
                    }\r\n
                }\r\n
            },\r\n
            goBack: function () {\r\n
                Common.Gateway.goBack();\r\n
            },\r\n
            onEditComplete: function (cmp, opts) {\r\n
                if (opts && opts.restorefocus && this.api.isCEditorFocused) {\r\n
                    this.formulaInput.blur();\r\n
                    this.formulaInput.focus();\r\n
                } else {\r\n
                    this.getApplication().getController("DocumentHolder").getView("DocumentHolder").focus();\r\n
                    this.api.isCEditorFocused = false;\r\n
                }\r\n
            },\r\n
            onLongActionBegin: function (type, id) {\r\n
                var action = {\r\n
                    id: id,\r\n
                    type: type\r\n
                };\r\n
                this.stackLongActions.push(action);\r\n
                this.setLongActionView(action);\r\n
            },\r\n
            onLongActionEnd: function (type, id) {\r\n
                var action = {\r\n
                    id: id,\r\n
                    type: type\r\n
                };\r\n
                this.stackLongActions.pop(action);\r\n
                this.headerView.setDocumentCaption(this.api.asc_getDocumentName());\r\n
                this.updateWindowTitle(this.api.asc_isDocumentModified(), true);\r\n
                if (type === c_oAscAsyncActionType.BlockInteraction && id == c_oAscAsyncAction.Open) {\r\n
                    Common.Gateway.internalMessage("documentReady", {});\r\n
                    this.onDocumentReady();\r\n
                }\r\n
                action = this.stackLongActions.get({\r\n
                    type: c_oAscAsyncActionType.Information\r\n
                });\r\n
                action && this.setLongActionView(action);\r\n
                if (id == c_oAscAsyncAction.Save) {\r\n
                    this.toolbarView.synchronizeChanges();\r\n
                }\r\n
                action = this.stackLongActions.get({\r\n
                    type: c_oAscAsyncActionType.BlockInteraction\r\n
                });\r\n
                if (action) {\r\n
                    this.setLongActionView(action);\r\n
                } else {\r\n
                    this.loadMask && this.loadMask.hide();\r\n
                    if (type == c_oAscAsyncActionType.BlockInteraction) {\r\n
                        this.onEditComplete(this.loadMask, {\r\n
                            restorefocus: true\r\n
                        });\r\n
                    }\r\n
                }\r\n
            },\r\n
            setLongActionView: function (action) {\r\n
                var title = "";\r\n
                switch (action.id) {\r\n
                case c_oAscAsyncAction.Open:\r\n
                    title = this.openTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.Save:\r\n
                    title = this.saveTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.LoadDocumentFonts:\r\n
                    title = this.loadFontsTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.LoadDocumentImages:\r\n
                    title = this.loadImagesTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.LoadFont:\r\n
                    title = this.loadFontTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.LoadImage:\r\n
                    title = this.loadImageTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.DownloadAs:\r\n
                    title = this.downloadTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.Print:\r\n
                    title = this.printTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.UploadImage:\r\n
                    title = this.uploadImageTitleText;\r\n
                    break;\r\n
                case c_oAscAsyncAction.Recalc:\r\n
                    title = this.titleRecalcFormulas;\r\n
                    break;\r\n
                case c_oAscAsyncAction.SlowOperation:\r\n
                    title = this.textPleaseWait;\r\n
                    break;\r\n
                case c_oAscAsyncAction["PrepareToSave"]:\r\n
                    title = this.savePreparingText;\r\n
                    break;\r\n
                case ApplyEditRights:\r\n
                    title = this.txtEditingMode;\r\n
                    break;\r\n
                case LoadingDocument:\r\n
                    title = this.loadingDocumentTitleText;\r\n
                    break;\r\n
                }\r\n
                if (action.type == c_oAscAsyncActionType.BlockInteraction) { ! this.loadMask && (this.loadMask = new Common.UI.LoadMask({\r\n
                        owner: $("#viewport")\r\n
                    }));\r\n
                    this.loadMask.setTitle(title);\r\n
                    if (!this.isShowOpenDialog) {\r\n
                        this.loadMask.show();\r\n
                    }\r\n
                }\r\n
            },\r\n
            onApplyEditRights: function (data) {\r\n
                if (data) {\r\n
                    if (data.allowed) {\r\n
                        this.onLongActionBegin(c_oAscAsyncActionType["BlockInteraction"], ApplyEditRights);\r\n
                        this.appOptions.isEdit = true;\r\n
                        var me = this;\r\n
                        setTimeout(function () {\r\n
                            me.applyModeCommonElements();\r\n
                            me.applyModeEditorElements("view");\r\n
                            me.api.asc_setViewerMode(false);\r\n
                            var application = me.getApplication();\r\n
                            var documentHolderController = application.getController("DocumentHolder");\r\n
                            application.getController("LeftMenu").setMode(me.appOptions).createDelayedElements();\r\n
                            Common.NotificationCenter.trigger("layout:changed", "main");\r\n
                            var timer_sl = setInterval(function () {\r\n
                                if (window.styles_loaded) {\r\n
                                    clearInterval(timer_sl);\r\n
                                    documentHolderController.getView("DocumentHolder").createDelayedElements();\r\n
                                    documentHolderController.resetApi();\r\n
                                    application.getController("Toolbar").createDelayedElements();\r\n
                                    application.getController("RightMenu").createDelayedElements();\r\n
                                    application.getController("Statusbar").getView("Statusbar").update();\r\n
                                    application.getController("CellEditor").setMode(me.appOptions);\r\n
                                    me.api.asc_registerCallback("asc_onInitEditorShapes", _.bind(me.fillAutoShapes, me));\r\n
                                    me.api.asc_registerCallback("asc_onSaveUrl", _.bind(me.onSaveUrl, me));\r\n
                                    me.api.asc_registerCallback("asc_onDocumentModifiedChanged", _.bind(me.onDocumentModifiedChanged, me));\r\n
                                    me.api.asc_registerCallback("asc_onDocumentCanSaveChanged", _.bind(me.onDocumentCanSaveChanged, me));\r\n
                                    me.updateThemeColors();\r\n
                                    application.getController("FormulaDialog").setApi(me.api);\r\n
                                }\r\n
                            },\r\n
                            50);\r\n
                        },\r\n
                        50);\r\n
                    } else {\r\n
                        Common.UI.info({\r\n
                            title: this.requestEditFailedTitleText,\r\n
                            msg: data.message || this.requestEditFailedMessageText\r\n
                        });\r\n
                    }\r\n
                }\r\n
            },\r\n
            onDocumentReady: function () {\r\n
                if (this._isDocReady) {\r\n
                    return;\r\n
                }\r\n
                var me = this,\r\n
                value, tips = [];\r\n
                me._isDocReady = true;\r\n
                me.hidePreloader();\r\n
                me.onLongActionEnd(c_oAscAsyncActionType["BlockInteraction"], LoadingDocument);\r\n
                value = this.appOptions.isEditDiagram ? 100 : window.localStorage.getItem("sse-settings-zoom");\r\n
                this.api.asc_setZoom(!value ? 1 : parseInt(value) / 100);\r\n
                value = window.localStorage.getItem("sse-settings-livecomment");\r\n
                this.isLiveCommenting = !(value !== null && parseInt(value) == 0);\r\n
                this.isLiveCommenting ? this.api.asc_showComments() : this.api.asc_hideComments();\r\n
                me.api.asc_registerCallback("asc_onStartAction", _.bind(me.onLongActionBegin, me));\r\n
                me.api.asc_registerCallback("asc_onConfirmAction", _.bind(me.onConfirmAction, me));\r\n
                me.api.asc_registerCallback("asc_onActiveSheetChanged", _.bind(me.onActiveSheetChanged, me));\r\n
                var application = me.getApplication();\r\n
                me.headerView.setDocumentCaption(me.api.asc_getDocumentName());\r\n
                me.updateWindowTitle(me.api.asc_isDocumentModified(), true);\r\n
                var toolbarController = application.getController("Toolbar"),\r\n
                statusbarController = application.getController("Statusbar"),\r\n
                documentHolderController = application.getController("DocumentHolder"),\r\n
                rightmenuController = application.getController("RightMenu"),\r\n
                leftmenuController = application.getController("LeftMenu"),\r\n
                celleditorController = application.getController("CellEditor"),\r\n
                statusbarView = statusbarController.getView("Statusbar"),\r\n
                leftMenuView = leftmenuController.getView("LeftMenu"),\r\n
                documentHolderView = documentHolderController.getView("DocumentHolder"),\r\n
                chatController = application.getController("Common.Controllers.Chat");\r\n
                leftMenuView.getMenu("file").loadDocument({\r\n
                    doc: me.appOptions.spreadsheet\r\n
                });\r\n
                leftmenuController.setMode(me.appOptions).createDelayedElements().setApi(me.api);\r\n
                leftMenuView.disableMenu("all", false);\r\n
                if (!me.appOptions.isEditDiagram && me.appOptions.canBranding) {\r\n
                    me.getApplication().getController("LeftMenu").leftMenu.getMenu("about").setLicInfo(me.editorConfig.customization);\r\n
                }\r\n
                documentHolderController.setApi(me.api).loadConfig({\r\n
                    config: me.editorConfig\r\n
                });\r\n
                celleditorController.setApi(me.api).setMode(this.appOptions);\r\n
                celleditorController.onApiCellSelection(me.api.asc_getCellInfo());\r\n
                chatController.setApi(this.api).setMode(this.appOptions);\r\n
                statusbarController.createDelayedElements();\r\n
                statusbarController.setApi(me.api);\r\n
                documentHolderView.setApi(me.api);\r\n
                statusbarView.update();\r\n
                this.formulaInput = celleditorController.getView("CellEditor").$el.find("textarea");\r\n
                if (me.appOptions.isEdit) {\r\n
                    if (me.needToUpdateVersion) {\r\n
                        Common.NotificationCenter.trigger("api:disconnect");\r\n
                        toolbarController.onApiCoAuthoringDisconnect();\r\n
                    }\r\n
                    var timer_sl = setInterval(function () {\r\n
                        if (window.styles_loaded || me.appOptions.isEditDiagram) {\r\n
                            clearInterval(timer_sl);\r\n
                            Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                                property: "uid",\r\n
                                value: new RegExp("^(doc_|sheet" + me.api.asc_getActiveWorksheetId() + "_)")\r\n
                            });\r\n
                            documentHolderView.createDelayedElements();\r\n
                            toolbarController.createDelayedElements();\r\n
                            rightmenuController.createDelayedElements();\r\n
                            if (!me.appOptions.isEditDiagram) {\r\n
                                me.api.asc_registerCallback("asc_onInitEditorShapes", _.bind(me.fillAutoShapes, me));\r\n
                                me.updateThemeColors();\r\n
                            }\r\n
                            me.api.asc_registerCallback("asc_onSaveUrl", _.bind(me.onSaveUrl, me));\r\n
                            me.api.asc_registerCallback("asc_onDocumentModifiedChanged", _.bind(me.onDocumentModifiedChanged, me));\r\n
                            me.api.asc_registerCallback("asc_onDocumentCanSaveChanged", _.bind(me.onDocumentCanSaveChanged, me));\r\n
                            var formulasDlgController = application.getController("FormulaDialog");\r\n
                            if (formulasDlgController) {\r\n
                                formulasDlgController.setApi(me.api);\r\n
                            }\r\n
                            if (me.needToUpdateVersion) {\r\n
                                toolbarController.onApiCoAuthoringDisconnect();\r\n
                            }\r\n
                        }\r\n
                    },\r\n
                    50);\r\n
                }\r\n
                if (me.appOptions.canAutosave) {\r\n
                    value = window.localStorage.getItem("sse-settings-autosave");\r\n
                    value = (value !== null) ? parseInt(value) : 1;\r\n
                } else {\r\n
                    value = 0;\r\n
                }\r\n
                me.api.asc_setAutoSaveGap(value);\r\n
                if (me.appOptions.canAnalytics) {\r\n
                    Common.component.Analytics.initialize("UA-12442749-13", "Spreadsheet Editor");\r\n
                }\r\n
                Common.Gateway.on("applyeditrights", _.bind(me.onApplyEditRights, me));\r\n
                Common.Gateway.on("processsaveresult", _.bind(me.onProcessSaveResult, me));\r\n
                Common.Gateway.on("processrightschange", _.bind(me.onProcessRightsChange, me));\r\n
                Common.Gateway.on("processmouse", _.bind(me.onProcessMouse, me));\r\n
                $(document).on("contextmenu", _.bind(me.onContextMenu, me));\r\n
                if ( !! window["AscDesktopEditor"]) {\r\n
                    Common.Utils.isIE9m && tips.push(me.warnBrowserIE9); ! Common.Utils.isGecko && !me.appOptions.isEditDiagram && !me.appOptions.nativeApp && (Math.abs(me.getBrowseZoomLevel() - 1) > 0.1) && tips.push(Common.Utils.String.platformKey(me.warnBrowserZoom, "{0}"));\r\n
                    if (tips.length) {\r\n
                        me.showTips(tips);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onOpenDocument: function (progress) {\r\n
                var elem = document.getElementById("loadmask-text");\r\n
                var proc = (progress.CurrentFont + progress.CurrentImage) / (progress.FontsCount + progress.ImagesCount);\r\n
                proc = this.textLoadingDocument + ": " + Math.round(proc * 100) + "%";\r\n
                elem ? elem.innerHTML = proc : this.loadMask.setTitle(proc);\r\n
            },\r\n
            onEditorPermissions: function (params) {\r\n
                if (params) {\r\n
                    this.permissions.edit !== false && (this.permissions.edit = params.asc_getCanEdit());\r\n
                    this.permissions.download !== false && (this.permissions.download = params.asc_getCanDownload());\r\n
                    this.appOptions.canAutosave = this.editorConfig.canAutosave !== false && params.asc_getIsAutosaveEnable();\r\n
                    this.appOptions.canAnalytics = params.asc_getIsAnalyticsEnable();\r\n
                    this.appOptions.canCoAuthoring = true;\r\n
                    this.appOptions.canLicense = params.asc_getCanLicense ? params.asc_getCanLicense() : false;\r\n
                    this.appOptions.canComments = this.appOptions.canLicense && !((typeof(this.editorConfig.customization) == "object") && this.editorConfig.customization.comments === false);\r\n
                    this.appOptions.canChat = this.appOptions.canLicense && !((typeof(this.editorConfig.customization) == "object") && this.editorConfig.customization.chat === false);\r\n
                    this.appOptions.canBranding = params.asc_getCanBranding() && (typeof(this.editorConfig.customization) == "object");\r\n
                    if (this.appOptions.canBranding) {\r\n
                        this.headerView.setBranding(this.editorConfig.customization);\r\n
                    }\r\n
                }\r\n
                this.appOptions.canEdit = this.permissions.edit === true;\r\n
                this.appOptions.isEdit = this.permissions.edit === true && this.editorConfig.mode !== "view";\r\n
                this.appOptions.canDownload = !this.appOptions.nativeApp && (this.permissions.download !== undefined ? this.permissions.download : true);\r\n
                this.applyModeCommonElements();\r\n
                this.applyModeEditorElements();\r\n
                this.api.asc_setViewerMode(!this.appOptions.isEdit);\r\n
                this.appOptions.isEditDiagram ? this.api.asc_LoadEmptyDocument() : this.api.asc_LoadDocument();\r\n
                if (!this.appOptions.isEdit) {\r\n
                    this.hidePreloader();\r\n
                    this.onLongActionBegin(c_oAscAsyncActionType.BlockInteraction, LoadingDocument);\r\n
                }\r\n
            },\r\n
            applyModeCommonElements: function () {\r\n
                window.editor_elements_prepared = true;\r\n
                var value = window.localStorage.getItem("sse-hidden-title");\r\n
                value = this.appOptions.isEdit && (value !== null && parseInt(value) == 1);\r\n
                var app = this.getApplication(),\r\n
                viewport = app.getController("Viewport").getView("Viewport"),\r\n
                statusbarView = app.getController("Statusbar").getView("Statusbar");\r\n
                if (this.headerView) {\r\n
                    this.headerView.setHeaderCaption(this.appOptions.isEdit ? "Spreadsheet Editor" : "Spreadsheet Viewer");\r\n
                    this.headerView.setVisible(!this.appOptions.nativeApp && !value && !this.appOptions.isDesktopApp && !this.appOptions.isEditDiagram);\r\n
                }\r\n
                viewport && viewport.setMode(this.appOptions, true);\r\n
                statusbarView && statusbarView.setMode(this.appOptions);\r\n
                app.getController("DocumentHolder").setMode(this.appOptions);\r\n
                if (this.appOptions.isEditDiagram) {\r\n
                    statusbarView.hide();\r\n
                    app.getController("LeftMenu").getView("LeftMenu").hide();\r\n
                    $(window).mouseup(function (e) {\r\n
                        Common.Gateway.internalMessage("processMouse", {\r\n
                            event: "mouse:up"\r\n
                        });\r\n
                    }).mousemove($.proxy(function (e) {\r\n
                        if (this.isDiagramDrag) {\r\n
                            Common.Gateway.internalMessage("processMouse", {\r\n
                                event: "mouse:move",\r\n
                                pagex: e.pageX,\r\n
                                pagey: e.pageY\r\n
                            });\r\n
                        }\r\n
                    },\r\n
                    this));\r\n
                }\r\n
                if (this.api) {\r\n
                    var translateChart = new Asc.asc_CChartTranslate();\r\n
                    translateChart.asc_setTitle(this.txtDiagramTitle);\r\n
                    translateChart.asc_setXAxis(this.txtXAxis);\r\n
                    translateChart.asc_setYAxis(this.txtYAxis);\r\n
                    translateChart.asc_setSeries(this.txtSeries);\r\n
                    this.api.asc_setChartTranslate(translateChart);\r\n
                }\r\n
                if (!this.appOptions.isEditDiagram) {\r\n
                    this.api.asc_registerCallback("asc_onSendThemeColors", _.bind(this.onSendThemeColors, this));\r\n
                }\r\n
            },\r\n
            applyModeEditorElements: function (prevmode) {\r\n
                if (this.appOptions.isEdit) {\r\n
                    var me = this,\r\n
                    application = this.getApplication(),\r\n
                    toolbarController = application.getController("Toolbar"),\r\n
                    statusbarController = application.getController("Statusbar"),\r\n
                    rightmenuController = application.getController("RightMenu"),\r\n
                    printController = application.getController("Print"),\r\n
                    commentsController = application.getController("Common.Controllers.Comments"),\r\n
                    fontsControllers = application.getController("Common.Controllers.Fonts");\r\n
                    fontsControllers && fontsControllers.setApi(me.api);\r\n
                    toolbarController && toolbarController.setApi(me.api);\r\n
                    if (commentsController) {\r\n
                        commentsController.setMode(this.appOptions);\r\n
                        commentsController.setConfig({\r\n
                            config: me.editorConfig,\r\n
                            sdkviewname: "#ws-canvas-outer",\r\n
                            hintmode: true\r\n
                        },\r\n
                        me.api);\r\n
                    }\r\n
                    rightmenuController && rightmenuController.setApi(me.api);\r\n
                    printController && printController.setApi(me.api);\r\n
                    if (statusbarController) {\r\n
                        statusbarController.getView("Statusbar").changeViewMode(true);\r\n
                    }\r\n
                    if (prevmode == "view") {\r\n
                        if (commentsController) {\r\n
                            Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                                property: "uid",\r\n
                                value: new RegExp("^(doc_|sheet" + this.api.asc_getActiveWorksheetId() + "_)")\r\n
                            });\r\n
                        }\r\n
                    }\r\n
                    var viewport = this.getApplication().getController("Viewport").getView("Viewport");\r\n
                    viewport.applyEditorMode();\r\n
                    this.toolbarView = toolbarController.getView("Toolbar");\r\n
                    _.each([this.toolbarView, rightmenuController.getView("RightMenu")], function (view) {\r\n
                        if (view) {\r\n
                            view.setMode(me.appOptions);\r\n
                            view.setApi(me.api);\r\n
                        }\r\n
                    });\r\n
                    if (this.toolbarView) {\r\n
                        this.toolbarView.on("insertimage", _.bind(me.onInsertImage, me));\r\n
                        this.toolbarView.on("insertshape", _.bind(me.onInsertShape, me));\r\n
                        this.toolbarView.on("insertchart", _.bind(me.onInsertChart, me));\r\n
                    }\r\n
                    var value = window.localStorage.getItem("sse-settings-unit");\r\n
                    Common.Utils.Metric.setCurrentMetric((value !== null) ? parseInt(value) : Common.Utils.Metric.c_MetricUnits.cm);\r\n
                    if (!me.appOptions.isEditDiagram) {\r\n
                        var options = {};\r\n
                        JSON.parse(window.localStorage.getItem("sse-hidden-title")) && (options.title = true);\r\n
                        JSON.parse(window.localStorage.getItem("sse-hidden-formula")) && (options.formula = true);\r\n
                        JSON.parse(window.localStorage.getItem("sse-hidden-headings")) && (options.headings = true);\r\n
                        application.getController("Toolbar").hideElements(options);\r\n
                    } else {\r\n
                        rightmenuController.getView("RightMenu").hide();\r\n
                    }\r\n
                    if (me.stackLongActions.exist({\r\n
                        id: ApplyEditRights,\r\n
                        type: c_oAscAsyncActionType["BlockInteraction"]\r\n
                    })) {\r\n
                        me.onLongActionEnd(c_oAscAsyncActionType["BlockInteraction"], ApplyEditRights);\r\n
                    } else {\r\n
                        if (!this._isDocReady) {\r\n
                            me.hidePreloader();\r\n
                            me.onLongActionBegin(c_oAscAsyncActionType["BlockInteraction"], LoadingDocument);\r\n
                        }\r\n
                    }\r\n
                    window.onbeforeunload = _.bind(me.onBeforeUnload, me);\r\n
                }\r\n
            },\r\n
            onExternalMessage: function (msg) {\r\n
                if (msg) {\r\n
                    var tip = msg.msg.charAt(0).toUpperCase() + msg.msg.substring(1),\r\n
                    title = (msg.severity.indexOf("error") >= 0) ? this.criticalErrorTitle : this.notcriticalErrorTitle;\r\n
                    this.showTips([tip], false, title);\r\n
                    Common.component.Analytics.trackEvent("External Error", msg.title);\r\n
                }\r\n
            },\r\n
            onError: function (id, level, errData) {\r\n
                this.hidePreloader();\r\n
                this.onLongActionEnd(c_oAscAsyncActionType.BlockInteraction, LoadingDocument);\r\n
                var config = {\r\n
                    closable: false\r\n
                };\r\n
                switch (id) {\r\n
                case c_oAscError.ID.Unknown:\r\n
                    config.msg = this.unknownErrorText;\r\n
                    break;\r\n
                case c_oAscError.ID.ConvertationTimeout:\r\n
                    config.msg = this.convertationTimeoutText;\r\n
                    break;\r\n
                case c_oAscError.ID.ConvertationError:\r\n
                    config.msg = this.convertationErrorText;\r\n
                    break;\r\n
                case c_oAscError.ID.DownloadError:\r\n
                    config.msg = this.downloadErrorText;\r\n
                    break;\r\n
                case c_oAscError.ID.UplImageSize:\r\n
                    config.msg = this.uploadImageSizeMessage;\r\n
                    break;\r\n
                case c_oAscError.ID.UplImageExt:\r\n
                    config.msg = this.uploadImageExtMessage;\r\n
                    break;\r\n
                case c_oAscError.ID.UplImageFileCount:\r\n
                    config.msg = this.uploadImageFileCountMessage;\r\n
                    break;\r\n
                case c_oAscError.ID.PastInMergeAreaError:\r\n
                    config.msg = this.pastInMergeAreaError;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongCountParentheses:\r\n
                    config.msg = this.errorWrongBracketsCount;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongOperator:\r\n
                    config.msg = this.errorWrongOperator;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongMaxArgument:\r\n
                    config.msg = this.errorCountArgExceed;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongCountArgument:\r\n
                    config.msg = this.errorCountArg;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongFunctionName:\r\n
                    config.msg = this.errorFormulaName;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlAnotherParsingError:\r\n
                    config.msg = this.errorFormulaParsing;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlWrongArgumentRange:\r\n
                    config.msg = this.errorArgsRange;\r\n
                    break;\r\n
                case c_oAscError.ID.UnexpectedGuid:\r\n
                    config.msg = this.errorUnexpectedGuid;\r\n
                    break;\r\n
                case c_oAscError.ID.Database:\r\n
                    config.msg = this.errorDatabaseConnection;\r\n
                    break;\r\n
                case c_oAscError.ID.FileRequest:\r\n
                    config.msg = this.errorFileRequest;\r\n
                    break;\r\n
                case c_oAscError.ID.FileVKey:\r\n
                    config.msg = this.errorFileVKey;\r\n
                    break;\r\n
                case c_oAscError.ID.StockChartError:\r\n
                    config.msg = this.errorStockChart;\r\n
                    break;\r\n
                case c_oAscError.ID.DataRangeError:\r\n
                    config.msg = this.errorDataRange;\r\n
                    break;\r\n
                case c_oAscError.ID.FrmlOperandExpected:\r\n
                    config.msg = this.errorOperandExpected;\r\n
                    break;\r\n
                case c_oAscError.ID.VKeyEncrypt:\r\n
                    config.msg = this.errorKeyEncrypt;\r\n
                    break;\r\n
                case c_oAscError.ID.KeyExpire:\r\n
                    config.msg = this.errorKeyExpire;\r\n
                    break;\r\n
                case c_oAscError.ID.UserCountExceed:\r\n
                    config.msg = this.errorUsersExceed;\r\n
                    break;\r\n
                case c_oAscError.ID.CannotMoveRange:\r\n
                    config.msg = this.errorMoveRange;\r\n
                    break;\r\n
                case c_oAscError.ID.UplImageUrl:\r\n
                    config.msg = this.errorBadImageUrl;\r\n
                    break;\r\n
                case c_oAscError.ID.CoAuthoringDisconnect:\r\n
                    config.msg = this.errorCoAuthoringDisconnect;\r\n
                    break;\r\n
                case c_oAscError.ID.ConvertationPassword:\r\n
                    config.msg = this.errorFilePassProtect;\r\n
                    break;\r\n
                case c_oAscError.ID.AutoFilterDataRangeError:\r\n
                    config.msg = this.errorAutoFilterDataRange;\r\n
                    break;\r\n
                case c_oAscError.ID.AutoFilterChangeFormatTableError:\r\n
                    config.msg = this.errorAutoFilterChangeFormatTable;\r\n
                    break;\r\n
                case c_oAscError.ID.AutoFilterChangeError:\r\n
                    config.msg = this.errorAutoFilterChange;\r\n
                    break;\r\n
                case c_oAscError.ID.CannotFillRange:\r\n
                    config.msg = this.errorFillRange;\r\n
                    break;\r\n
                case c_oAscError.ID.UserDrop:\r\n
                    config.msg = this.errorUserDrop;\r\n
                    break;\r\n
                default:\r\n
                    config.msg = this.errorDefaultMessage.replace("%1", id);\r\n
                    break;\r\n
                }\r\n
                if (level == c_oAscError.Level.Critical) {\r\n
                    Common.Gateway.reportError(id, config.msg);\r\n
                    config.title = this.criticalErrorTitle;\r\n
                    config.iconCls = "error";\r\n
                    if (this.editorConfig.canBackToFolder) {\r\n
                        config.msg += "<br/><br/>" + this.criticalErrorExtText;\r\n
                        config.callback = function (btn) {\r\n
                            if (btn == "ok") {\r\n
                                Common.Gateway.goBack();\r\n
                            }\r\n
                        };\r\n
                    }\r\n
                } else {\r\n
                    config.title = this.notcriticalErrorTitle;\r\n
                    config.iconCls = "warn";\r\n
                    config.buttons = ["ok"];\r\n
                    config.callback = _.bind(function (btn) {\r\n
                        this.onEditComplete();\r\n
                    },\r\n
                    this);\r\n
                }\r\n
                if ($(".asc-window.modal.alert:visible").length < 1) {\r\n
                    Common.UI.alert(config);\r\n
                    Common.component.Analytics.trackEvent("Internal Error", id.toString());\r\n
                }\r\n
            },\r\n
            onCoAuthoringDisconnect: function () {\r\n
                this.getApplication().getController("Viewport").getView("Viewport").setMode({\r\n
                    isDisconnected: true\r\n
                });\r\n
            },\r\n
            getBrowseZoomLevel: function () {\r\n
                if (Common.Utils.isIE) {\r\n
                    return screen.logicalXDPI / screen.deviceXDPI;\r\n
                } else {\r\n
                    var zoom = window.outerWidth / document.documentElement.clientWidth;\r\n
                    if (Common.Utils.isSafari) {\r\n
                        zoom = Math.floor(zoom * 10) / 10;\r\n
                    }\r\n
                    return zoom;\r\n
                }\r\n
            },\r\n
            showTips: function (strings, autohide, title) {\r\n
                var me = this;\r\n
                if (!strings.length) {\r\n
                    return;\r\n
                }\r\n
                if (typeof(strings) != "object") {\r\n
                    strings = [strings];\r\n
                }\r\n
                function showNextTip() {\r\n
                    var str_tip = strings.shift();\r\n
                    if (str_tip) {\r\n
                        str_tip += me.textCloseTip;\r\n
                        tooltip.setTitle(str_tip);\r\n
                        tooltip.show();\r\n
                    }\r\n
                }\r\n
                if (!this.tooltip) {\r\n
                    this.tooltip = new Common.UI.Tooltip({\r\n
                        owner: this.toolbarView,\r\n
                        hideonclick: true,\r\n
                        placement: "bottom",\r\n
                        cls: "main-info",\r\n
                        offset: 30\r\n
                    });\r\n
                }\r\n
                var tooltip = this.tooltip;\r\n
                tooltip.on("tooltip:hide", function () {\r\n
                    setTimeout(showNextTip, 300);\r\n
                });\r\n
                showNextTip();\r\n
            },\r\n
            updateWindowTitle: function (change, force) {\r\n
                if (this._state.isDocModified !== change || force) {\r\n
                    var title = this.defaultTitleText;\r\n
                    if (!_.isEmpty(this.headerView.getDocumentCaption())) {\r\n
                        title = this.headerView.getDocumentCaption() + " - " + title;\r\n
                    }\r\n
                    if (change) {\r\n
                        if (!_.isUndefined(title)) {\r\n
                            title = "* " + title;\r\n
                            this.headerView.setDocumentCaption(this.headerView.getDocumentCaption() + "*", true);\r\n
                        }\r\n
                    } else {\r\n
                        this.headerView.setDocumentCaption(this.headerView.getDocumentCaption());\r\n
                    }\r\n
                    if (window.document.title != title) {\r\n
                        window.document.title = title;\r\n
                    }\r\n
                    this._state.isDocModified = change;\r\n
                }\r\n
            },\r\n
            onDocumentChanged: function () {},\r\n
            onDocumentModifiedChanged: function (change) {\r\n
                this.updateWindowTitle(change);\r\n
                Common.Gateway.setDocumentModified(change);\r\n
                if (this.toolbarView && this.api) {\r\n
                    var isSyncButton = $(".btn-icon", this.toolbarView.btnSave.cmpEl).hasClass("btn-synch");\r\n
                    var cansave = this.api.asc_isDocumentCanSave();\r\n
                    if (this.toolbarView.btnSave.isDisabled() !== (!cansave && !isSyncButton)) {\r\n
                        this.toolbarView.btnSave.setDisabled(!cansave);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onDocumentCanSaveChanged: function (isCanSave) {\r\n
                if (this.toolbarView) {\r\n
                    var isSyncButton = $(".btn-icon", this.toolbarView.btnSave.cmpEl).hasClass("btn-synch");\r\n
                    if (this.toolbarView.btnSave.isDisabled() !== (!isCanSave && !isSyncButton)) {\r\n
                        this.toolbarView.btnSave.setDisabled(!isCanSave && !isSyncButton);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onBeforeUnload: function () {\r\n
                var isEdit = this.permissions.edit === true && this.editorConfig.mode !== "view" && this.editorConfig.mode !== "editdiagram";\r\n
                if (isEdit && this.api.asc_isDocumentModified()) {\r\n
                    return this.leavePageText;\r\n
                }\r\n
            },\r\n
            hidePreloader: function () {\r\n
                if ( !! this.appOptions.customization && !this.appOptions.customization.done) {\r\n
                    this.appOptions.customization.done = true;\r\n
                    Common.Utils.applyCustomization(this.appOptions.customization, mapCustomizationElements);\r\n
                }\r\n
                this.stackLongActions.pop({\r\n
                    id: InitApplication,\r\n
                    type: c_oAscAsyncActionType.BlockInteraction\r\n
                });\r\n
                Common.NotificationCenter.trigger("layout:changed", "main");\r\n
                $("#loading-mask").hide().remove();\r\n
            },\r\n
            onSaveUrl: function (url) {\r\n
                Common.Gateway.save(url);\r\n
            },\r\n
            onUpdateVersion: function (callback) {\r\n
                var me = this;\r\n
                me.needToUpdateVersion = true;\r\n
                me.onLongActionEnd(c_oAscAsyncActionType["BlockInteraction"], LoadingDocument);\r\n
                Common.UI.error({\r\n
                    msg: this.errorUpdateVersion,\r\n
                    callback: function () {\r\n
                        _.defer(function () {\r\n
                            Common.Gateway.updateVersion();\r\n
                            if (callback) {\r\n
                                callback.call(me);\r\n
                            }\r\n
                            me.onLongActionBegin(c_oAscAsyncActionType["BlockInteraction"], LoadingDocument);\r\n
                        });\r\n
                    }\r\n
                });\r\n
            },\r\n
            onAdvancedOptions: function (advOptions) {\r\n
                if (advOptions.asc_getOptionId() == c_oAscAdvancedOptionsID.CSV) {\r\n
                    var me = this;\r\n
                    var dlg = new SSE.Views.OpenDialog({\r\n
                        codepages: advOptions.asc_getOptions().asc_getCodePages(),\r\n
                        settings: advOptions.asc_getOptions().asc_getRecommendedSettings(),\r\n
                        handler: function (encoding, delimiter) {\r\n
                            me.isShowOpenDialog = false;\r\n
                            if (me && me.api) {\r\n
                                me.api.asc_setAdvancedOptions(c_oAscAdvancedOptionsID.CSV, new Asc.asc_CCSVAdvancedOptions(encoding, delimiter));\r\n
                                me.loadMask && me.loadMask.show();\r\n
                            }\r\n
                        }\r\n
                    });\r\n
                    this.isShowOpenDialog = true;\r\n
                    this.loadMask && this.loadMask.hide();\r\n
                    this.onLongActionEnd(c_oAscAsyncActionType.BlockInteraction, LoadingDocument);\r\n
                    dlg.show();\r\n
                }\r\n
            },\r\n
            onActiveSheetChanged: function (index) {\r\n
                if (!this.appOptions.isEditDiagram && window.editor_elements_prepared) {\r\n
                    this.application.getController("Statusbar").selectTab(index);\r\n
                    if (this.appOptions.isEdit) {\r\n
                        Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                            property: "uid",\r\n
                            value: new RegExp("^(doc_|sheet" + this.api.asc_getWorksheetId(index) + "_)")\r\n
                        },\r\n
                        false);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onConfirmAction: function (id, apiCallback) {\r\n
                if (id == c_oAscConfirm.ConfirmReplaceRange) {\r\n
                    var me = this;\r\n
                    Common.UI.warning({\r\n
                        closable: false,\r\n
                        title: this.notcriticalErrorTitle,\r\n
                        msg: this.confirmMoveCellRange,\r\n
                        buttons: ["yes", "no"],\r\n
                        callback: _.bind(function (btn) {\r\n
                            if (apiCallback) {\r\n
                                apiCallback(btn === "ok");\r\n
                            }\r\n
                            if (btn == "ok") {\r\n
                                me.onEditComplete(me.application.getController("DocumentHolder").getView("DocumentHolder"));\r\n
                            }\r\n
                        },\r\n
                        this)\r\n
                    });\r\n
                }\r\n
            },\r\n
            initNames: function () {\r\n
                this.shapeGroupNames = [this.txtBasicShapes, this.txtFiguredArrows, this.txtMath, this.txtCharts, this.txtStarsRibbons, this.txtCallouts, this.txtButtons, this.txtRectangles, this.txtLines];\r\n
            },\r\n
            fillAutoShapes: function (groupNames, shapes) {\r\n
                if (_.isEmpty(shapes) || _.isEmpty(groupNames) || shapes.length != groupNames.length) {\r\n
                    return;\r\n
                }\r\n
                var me = this,\r\n
                shapegrouparray = [],\r\n
                shapeStore = this.getCollection("ShapeGroups");\r\n
                shapeStore.reset();\r\n
                var groupscount = groupNames.length;\r\n
                _.each(groupNames, function (groupName, index) {\r\n
                    var store = new Backbone.Collection([], {\r\n
                        model: SSE.Models.ShapeModel\r\n
                    });\r\n
                    var cols = (shapes[index].length) > 18 ? 7 : 6,\r\n
                    height = Math.ceil(shapes[index].length / cols) * 35 + 3,\r\n
                    width = 30 * cols;\r\n
                    _.each(shapes[index], function (shape, idx) {\r\n
                        store.add({\r\n
                            imageUrl: shape.Image,\r\n
                            data: {\r\n
                                shapeType: shape.Type\r\n
                            },\r\n
                            tip: me.textShape + " " + (idx + 1),\r\n
                            allowSelected: false,\r\n
                            selected: false\r\n
                        });\r\n
                    });\r\n
                    shapegrouparray.push({\r\n
                        groupName: me.shapeGroupNames[index],\r\n
                        groupStore: store,\r\n
                        groupWidth: width,\r\n
                        groupHeight: height\r\n
                    });\r\n
                });\r\n
                if (groupscount > 0) {\r\n
                    var store = new Backbone.Collection([], {\r\n
                        model: SSE.Models.ShapeModel\r\n
                    });\r\n
                    var cols = (shapes[groupscount - 1].length - 3) > 18 ? 7 : 6,\r\n
                    height = Math.ceil((shapes[groupscount - 1].length - 3) / cols) * 35 + 3,\r\n
                    width = 30 * cols;\r\n
                    for (var i = 0; i < shapes[groupscount - 1].length - 3; i++) {\r\n
                        var shape = shapes[groupscount - 1][i];\r\n
                        store.add({\r\n
                            imageUrl: shape.Image,\r\n
                            data: {\r\n
                                shapeType: shape.Type\r\n
                            },\r\n
                            allowSelected: false,\r\n
                            selected: false\r\n
                        });\r\n
                    }\r\n
                    shapegrouparray.push({\r\n
                        groupName: me.shapeGroupNames[groupscount - 1],\r\n
                        groupStore: store,\r\n
                        groupWidth: width,\r\n
                        groupHeight: height\r\n
                    });\r\n
                }\r\n
                shapeStore.add(shapegrouparray);\r\n
                setTimeout(function () {\r\n
                    me.getApplication().getController("Toolbar").fillAutoShapes();\r\n
                },\r\n
                50);\r\n
            },\r\n
            updateThemeColors: function () {\r\n
                var me = this;\r\n
                setTimeout(function () {\r\n
                    me.getApplication().getController("RightMenu").UpdateThemeColors();\r\n
                },\r\n
                50);\r\n
                setTimeout(function () {\r\n
                    me.getApplication().getController("Toolbar").updateThemeColors();\r\n
                },\r\n
                50);\r\n
                setTimeout(function () {\r\n
                    me.getApplication().getController("Statusbar").updateThemeColors();\r\n
                },\r\n
                50);\r\n
            },\r\n
            onSendThemeColors: function (colors, standart_colors) {\r\n
                Common.Utils.ThemeColor.setColors(colors, standart_colors);\r\n
                if (window.styles_loaded && !this.appOptions.isEditDiagram) {\r\n
                    this.updateThemeColors();\r\n
                }\r\n
            },\r\n
            loadLanguages: function () {},\r\n
            onInsertImage: function () {\r\n
                this.getApplication().getController("RightMenu").onInsertImage();\r\n
            },\r\n
            onInsertChart: function () {\r\n
                this.getApplication().getController("RightMenu").onInsertChart();\r\n
            },\r\n
            onInsertShape: function () {\r\n
                this.getApplication().getController("RightMenu").onInsertShape();\r\n
            },\r\n
            onInternalCommand: function (data) {\r\n
                if (data) {\r\n
                    switch (data.command) {\r\n
                    case "setChartData":\r\n
                        this.setChartData(data.data);\r\n
                        break;\r\n
                    case "getChartData":\r\n
                        this.getChartData();\r\n
                        break;\r\n
                    case "clearChartData":\r\n
                        this.clearChartData();\r\n
                        break;\r\n
                    case "setAppDisabled":\r\n
                        this.isAppDisabled = data.data;\r\n
                        this.api.asc_enableKeyEvents(false);\r\n
                        break;\r\n
                    case "queryClose":\r\n
                        if ($("body .asc-window:visible").length === 0) {\r\n
                            Common.Gateway.internalMessage("canClose", {\r\n
                                mr: data.data.mr,\r\n
                                answer: true\r\n
                            });\r\n
                        }\r\n
                        break;\r\n
                    case "window:drag":\r\n
                        this.isDiagramDrag = data.data;\r\n
                        break;\r\n
                    case "processmouse":\r\n
                        this.onProcessMouse(data.data);\r\n
                        break;\r\n
                    }\r\n
                }\r\n
            },\r\n
            setChartData: function (chart) {\r\n
                if (typeof chart === "object" && this.api) {\r\n
                    this.api.asc_addChartDrawingObject(chart);\r\n
                }\r\n
            },\r\n
            getChartData: function () {\r\n
                if (this.api) {\r\n
                    var chartData = this.api.asc_getWordChartObject();\r\n
                    if (typeof chartData === "object") {\r\n
                        Common.Gateway.internalMessage("chartData", {\r\n
                            data: chartData\r\n
                        });\r\n
                    }\r\n
                }\r\n
            },\r\n
            clearChartData: function () {\r\n
                this.api && this.api.asc_cleanWorksheet();\r\n
            },\r\n
            unitsChanged: function (m) {\r\n
                var value = window.localStorage.getItem("sse-settings-unit");\r\n
                Common.Utils.Metric.setCurrentMetric((value !== null) ? parseInt(value) : Common.Utils.Metric.c_MetricUnits.cm);\r\n
                this.getApplication().getController("RightMenu").updateMetricUnit();\r\n
                this.getApplication().getController("Print").getView("MainSettingsPrint").updateMetricUnit();\r\n
            },\r\n
            _compareActionStrong: function (obj1, obj2) {\r\n
                return obj1.id === obj2.id && obj1.type === obj2.type;\r\n
            },\r\n
            _compareActionWeak: function (obj1, obj2) {\r\n
                return obj1.type === obj2.type;\r\n
            },\r\n
            onContextMenu: function (event) {\r\n
                var canCopyAttr = event.target.getAttribute("data-can-copy"),\r\n
                isInputEl = (event.target instanceof HTMLInputElement) || (event.target instanceof HTMLTextAreaElement);\r\n
                if ((isInputEl && canCopyAttr === "false") || (!isInputEl && canCopyAttr !== "true")) {\r\n
                    event.stopPropagation();\r\n
                    event.preventDefault();\r\n
                    return false;\r\n
                }\r\n
            },\r\n
            leavePageText: "You have unsaved changes in this document. Click \'Stay on this Page\' then \'Save\' to save them. Click \'Leave this Page\' to discard all the unsaved changes.",\r\n
            criticalErrorTitle: "Error",\r\n
            notcriticalErrorTitle: "Warning",\r\n
            errorDefaultMessage: "Error code: %1",\r\n
            criticalErrorExtText: \'Press "Ok" to to back to document list.\',\r\n
            openTitleText: "Opening Document",\r\n
            openTextText: "Opening document...",\r\n
            saveTitleText: "Saving Document",\r\n
            saveTextText: "Saving document...",\r\n
            loadFontsTitleText: "Loading Data",\r\n
            loadFontsTextText: "Loading data...",\r\n
            loadImagesTitleText: "Loading Images",\r\n
            loadImagesTextText: "Loading images...",\r\n
            loadFontTitleText: "Loading Data",\r\n
            loadFontTextText: "Loading data...",\r\n
            loadImageTitleText: "Loading Image",\r\n
            loadImageTextText: "Loading image...",\r\n
            downloadTitleText: "Downloading Document",\r\n
            downloadTextText: "Downloading document...",\r\n
            printTitleText: "Printing Document",\r\n
            printTextText: "Printing document...",\r\n
            uploadImageTitleText: "Uploading Image",\r\n
            uploadImageTextText: "Uploading image...",\r\n
            savePreparingText: "Preparing to save",\r\n
            savePreparingTitle: "Preparing to save. Please wait...",\r\n
            loadingDocumentTitleText: "Loading Document",\r\n
            uploadImageSizeMessage: "Maximium image size limit exceeded.",\r\n
            uploadImageExtMessage: "Unknown image format.",\r\n
            uploadImageFileCountMessage: "No images uploaded.",\r\n
            reloadButtonText: "Reload Page",\r\n
            unknownErrorText: "Unknown error.",\r\n
            convertationTimeoutText: "Convertation timeout exceeded.",\r\n
            convertationErrorText: "Convertation failed.",\r\n
            downloadErrorText: "Download failed.",\r\n
            unsupportedBrowserErrorText: "Your browser is not supported.",\r\n
            requestEditFailedTitleText: "Access denied",\r\n
            requestEditFailedMessageText: "Someone is editing this document right now. Please try again later.",\r\n
            warnBrowserZoom: "Your browser\'s current zoom setting is not fully supported. Please reset to the default zoom by pressing Ctrl+0.",\r\n
            warnBrowserIE9: "The application has low capabilities on IE9. Use IE10 or higher",\r\n
            pastInMergeAreaError: "Cannot change part of a merged cell",\r\n
            titleRecalcFormulas: "Calculating formulas...",\r\n
            textRecalcFormulas: "Calculating formulas...",\r\n
            textPleaseWait: "It\'s working hard. Please wait...",\r\n
            errorWrongBracketsCount: "Found an error in the formula entered.<br>Wrong cout of brackets.",\r\n
            errorWrongOperator: "Found an error in the formula entered.<br>Wrong operator.",\r\n
            errorCountArgExceed: "Found an error in the formula entered.<br>Count of arguments exceeded.",\r\n
            errorCountArg: "Found an error in the formula entered.<br>Invalid number of arguments.",\r\n
            errorFormulaName: "Found an error in the formula entered.<br>Incorrect formula name.",\r\n
            errorFormulaParsing: "Internal error while the formula parsing.",\r\n
            errorArgsRange: "Found an error in the formula entered.<br>Incorrect arguments range.",\r\n
            errorUnexpectedGuid: "External error.<br>Unexpected Guid. Please, contact support.",\r\n
            errorDatabaseConnection: "External error.<br>Database connection error. Please, contact support.",\r\n
            errorFileRequest: "External error.<br>File Request. Please, contact support.",\r\n
            errorFileVKey: "External error.<br>Incorrect securety key. Please, contact support.",\r\n
            errorStockChart: "Incorrect row order. To build a stock chart place the data on the sheet in the following order:<br> opening price, max price, min price, closing price.",\r\n
            errorDataRange: "Incorrect data range.",\r\n
            errorOperandExpected: "Operand expected",\r\n
            errorKeyEncrypt: "Unknown key descriptor",\r\n
            errorKeyExpire: "Key descriptor expired",\r\n
            errorUsersExceed: "Count of users was exceed",\r\n
            errorMoveRange: "Cann\'t change a part of merged cell",\r\n
            errorBadImageUrl: "Image url is incorrect",\r\n
            errorCoAuthoringDisconnect: "Server connection lost. You can\'t edit anymore.",\r\n
            errorFilePassProtect: "The document is password protected.",\r\n
            txtEditingMode: "Set editing mode...",\r\n
            textLoadingDocument: "LOADING DOCUMENT",\r\n
            textConfirm: "Confirmation",\r\n
            confirmMoveCellRange: "The destination cell\'s range can contain data. Continue the operation?",\r\n
            textYes : "Yes",\r\n
            textNo: "No",\r\n
            textAnonymous: "Anonymous",\r\n
            txtBasicShapes: "Basic Shapes",\r\n
            txtFiguredArrows: "Figured Arrows",\r\n
            txtMath: "Math",\r\n
            txtCharts: "Charts",\r\n
            txtStarsRibbons: "Stars & Ribbons",\r\n
            txtCallouts: "Callouts",\r\n
            txtButtons: "Buttons",\r\n
            txtRectangles: "Rectangles",\r\n
            txtLines: "Lines",\r\n
            txtDiagramTitle: "Diagram Title",\r\n
            txtXAxis: "X Axis",\r\n
            txtYAxis: "Y Axis",\r\n
            txtSeries: "Seria",\r\n
            warnProcessRightsChange: "You have been denied the right to edit the file.",\r\n
            errorProcessSaveResult: "Saving is failed.",\r\n
            errorAutoFilterDataRange: "The operation could not be done for the selected range of cells.<br>Select a uniform data range inside or outside the table and try again.",\r\n
            errorAutoFilterChangeFormatTable: "The operation could not be done for the selected cells as you cannot move a part of the table.<br>Select another data range so that the whole table was shifted and try again.",\r\n
            errorAutoFilterChange: "The operation is not allowed, as it is attempting to shift cells in a table on your worksheet.",\r\n
            textCloseTip: "\\nClick to close the tip.",\r\n
            textShape: "Shape",\r\n
            errorFillRange: "Could not fill the selected range of cells.<br>All the merged cells need to be the same size.",\r\n
            errorUpdateVersion: "The file version has been changed. The page will be reloaded.",\r\n
            defaultTitleText: "ONLYOFFICE Spreadsheet Editor",\r\n
            errorUserDrop: "The file cannot be accessed right now."\r\n
        };\r\n
    })(), SSE.Controllers.Main || {}));\r\n
});

]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
