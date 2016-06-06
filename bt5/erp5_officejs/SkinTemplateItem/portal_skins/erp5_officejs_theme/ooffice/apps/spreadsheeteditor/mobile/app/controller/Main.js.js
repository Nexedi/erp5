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
            <value> <string>ts44308767.37</string> </value>
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
 Ext.define("SSE.controller.Main", {\r\n
    extend: "Ext.app.Controller",\r\n
    editMode: false,\r\n
    requires: ["Ext.Anim", "Ext.MessageBox", "SSE.controller.ApiEvents", "SSE.view.OpenCsvPanel"],\r\n
    config: {\r\n
        refs: {\r\n
            mainView: "semainview"\r\n
        }\r\n
    },\r\n
    launch: function () {\r\n
        if (!this._isSupport()) {\r\n
            Common.Gateway.reportError(undefined, this.unsupportedBrowserErrorText);\r\n
            return;\r\n
        }\r\n
        this.initControl();\r\n
        Common.component.Analytics.initialize("UA-12442749-13", "Spreadsheet Mobile");\r\n
        var app = this.getApplication();\r\n
        this.api = new Asc.spreadsheet_api("id-sdkeditor", "", SSE.controller.ApiEvents, {},\r\n
        {});\r\n
        this.api.asc_Init("../../../sdk/Fonts/");\r\n
        this.api.asc_setMobileVersion(true);\r\n
        this.api.asc_registerCallback("asc_onAdvancedOptions", Ext.bind(this.onAdvancedOptions, this));\r\n
        this.api.asc_registerCallback("asc_onOpenDocumentProgress", Ext.bind(this.onOpenDocumentProgress, this));\r\n
        this.api.asc_registerCallback("asc_onEndAction", Ext.bind(this.onLongActionEnd, this));\r\n
        this.api.asc_registerCallback("asc_onError", Ext.bind(this.onError, this));\r\n
        this.api.asc_registerCallback("asc_onSaveUrl", Ext.bind(this.onSaveUrl, this));\r\n
        this.api.asc_registerCallback("asc_onGetEditorPermissions", Ext.bind(this.onEditorPermissions, this));\r\n
        Ext.each(app.getControllers(), function (controllerName) {\r\n
            var controller = app.getController(controllerName);\r\n
            controller && Ext.isFunction(controller.setApi) && controller.setApi(this.api);\r\n
        },\r\n
        this);\r\n
        this.initApi();\r\n
        this.editorConfig = {};\r\n
        Common.Gateway.on("init", Ext.bind(this.loadConfig, this));\r\n
        Common.Gateway.on("opendocument", Ext.bind(this.loadDocument, this));\r\n
        Common.Gateway.on("showmessage", Ext.bind(this.onExternalMessage, this));\r\n
        Common.Gateway.on("processsaveresult", Ext.bind(this.onProcessSaveResult, this));\r\n
        Common.Gateway.ready();\r\n
    },\r\n
    initControl: function () {},\r\n
    initApi: function () {},\r\n
    loadConfig: function (data) {\r\n
        this.editorConfig = Ext.merge(this.editorConfig, data.config);\r\n
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
        this.editorConfig.user.id = this.editorConfig.user.id || ("uid-" + Ext.Date.now());\r\n
        this.editorConfig.user.name = this.editorConfig.user.name || this.textAnonymous;\r\n
    },\r\n
    loadDocument: function (data) {\r\n
        if (data.doc) {\r\n
            this.permissions = data.doc.permissions;\r\n
            var docInfo = {\r\n
                Id: data.doc.key,\r\n
                Url: data.doc.url,\r\n
                Title: data.doc.title,\r\n
                Format: data.doc.fileType,\r\n
                Options: data.doc.options,\r\n
                VKey: data.doc.vkey,\r\n
                Origin: data.doc.origin,\r\n
                UserId: this.editorConfig.user.id,\r\n
                UserName: this.editorConfig.user.name\r\n
            };\r\n
            this.api.asc_setDocInfo(docInfo);\r\n
            this.api.asc_getEditorPermissions();\r\n
            Common.component.Analytics.trackEvent("Load", "Start");\r\n
        }\r\n
    },\r\n
    onEditorPermissions: function (params) {\r\n
        this.permissions.edit !== false && (this.permissions.edit = params.asc_getCanEdit());\r\n
        var modeEdit = false;\r\n
        this.api.asc_setViewerMode(!modeEdit);\r\n
        this.api.asc_LoadDocument();\r\n
        var profileName = this.getApplication().getCurrentProfile().getName();\r\n
        this.getApplication().getController(profileName + ".Main").setMode(modeEdit);\r\n
    },\r\n
    goBack: function () {\r\n
        Common.Gateway.goBack();\r\n
    },\r\n
    onError: function (id, level) {\r\n
        this._hideLoadSplash();\r\n
        var config = {\r\n
            closable: false\r\n
        };\r\n
        switch (id) {\r\n
        case c_oAscError.ID.Unknown:\r\n
            config.message = this.unknownErrorText;\r\n
            break;\r\n
        case c_oAscError.ID.ConvertationTimeout:\r\n
            config.message = this.convertationTimeoutText;\r\n
            break;\r\n
        case c_oAscError.ID.ConvertationError:\r\n
            config.message = this.convertationErrorText;\r\n
            break;\r\n
        case c_oAscError.ID.DownloadError:\r\n
            config.message = this.downloadErrorText;\r\n
            break;\r\n
        case c_oAscError.ID.UplImageSize:\r\n
            config.message = this.uploadImageSizeMessage;\r\n
            break;\r\n
        case c_oAscError.ID.UplImageExt:\r\n
            config.message = this.uploadImageExtMessage;\r\n
            break;\r\n
        case c_oAscError.ID.UplImageFileCount:\r\n
            config.message = this.uploadImageFileCountMessage;\r\n
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
        default:\r\n
            config.message = this.errorDefaultMessage.replace("%1", id);\r\n
            break;\r\n
        }\r\n
        if (level == c_oAscError.Level.Critical) {\r\n
            Common.Gateway.reportError(id, config.message);\r\n
            config.title = this.criticalErrorTitle;\r\n
            config.message += "<br/>" + this.criticalErrorExtText;\r\n
            config.buttons = Ext.Msg.OK;\r\n
            config.fn = function (btn) {\r\n
                if (btn == "ok") {\r\n
                    window.location.reload();\r\n
                }\r\n
            };\r\n
        } else {\r\n
            config.title = this.notcriticalErrorTitle;\r\n
            config.buttons = Ext.Msg.OK;\r\n
            config.fn = Ext.emptyFn;\r\n
        }\r\n
        Ext.Msg.show(config);\r\n
    },\r\n
    onSaveUrl: function (url) {\r\n
        Common.Gateway.save(url);\r\n
    },\r\n
    onExternalMessage: function (msg) {\r\n
        if (msg) {\r\n
            this._hideLoadSplash();\r\n
            Ext.Msg.show({\r\n
                title: msg.title,\r\n
                msg: "<br/>" + msg.msg,\r\n
                icon: Ext.Msg[msg.severity.toUpperCase()],\r\n
                buttons: Ext.Msg.OK\r\n
            });\r\n
            Common.component.Analytics.trackEvent("External Error", msg.title);\r\n
        }\r\n
    },\r\n
    onAdvancedOptions: function (advOptions) {\r\n
        if (advOptions.asc_getOptionId() == c_oAscAdvancedOptionsID["CSV"]) {\r\n
            var preloader = Ext.get("loading-mask"),\r\n
            me = this;\r\n
            Ext.Anim.run(preloader, "slide", {\r\n
                out: true,\r\n
                direction: "up",\r\n
                duration: 250,\r\n
                after: function () {\r\n
                    preloader.hide();\r\n
                }\r\n
            });\r\n
            var viewAdvOptionsCsv = Ext.Viewport.add({\r\n
                xtype: "seopencsvpanel",\r\n
                left: 0,\r\n
                top: 0,\r\n
                width: "100%",\r\n
                height: "100%"\r\n
            });\r\n
            Ext.Anim.run(viewAdvOptionsCsv, "slide", {\r\n
                out: false,\r\n
                direction: "up",\r\n
                duration: 1000\r\n
            });\r\n
            viewAdvOptionsCsv.on("close", Ext.bind(function (panel, result) {\r\n
                preloader.show();\r\n
                Ext.Anim.run(preloader, "slide", {\r\n
                    out: false,\r\n
                    direction: "down",\r\n
                    duration: 1000\r\n
                });\r\n
                Ext.Anim.run(viewAdvOptionsCsv, "slide", {\r\n
                    out: true,\r\n
                    direction: "down",\r\n
                    duration: 1000,\r\n
                    after: function () {\r\n
                        Ext.Viewport.remove(viewAdvOptionsCsv);\r\n
                        if (me.api) {\r\n
                            me.api.asc_setAdvancedOptions(c_oAscAdvancedOptionsID["CSV"], new Asc.asc_CCSVAdvancedOptions(result.encoding, result.delimiter));\r\n
                        }\r\n
                    }\r\n
                });\r\n
            },\r\n
            this));\r\n
        }\r\n
    },\r\n
    onOpenDocumentProgress: function (progress) {\r\n
        var elem = document.getElementById("loadmask-text");\r\n
        if (elem) {\r\n
            var proc = (progress["CurrentFont"] + progress["CurrentImage"]) / (progress["FontsCount"] + progress["ImagesCount"]);\r\n
            elem.innerHTML = this.textLoadingDocument + ": " + Math.round(proc * 100) + "%";\r\n
        }\r\n
    },\r\n
    onOpenDocument: function () {\r\n
        this._hideLoadSplash();\r\n
        this.api.asc_Resize();\r\n
        if (this.api) {\r\n
            this.api.asc_cleanSelection();\r\n
        }\r\n
    },\r\n
    onLongActionEnd: function (type, id) {\r\n
        if (type === c_oAscAsyncActionType["BlockInteraction"]) {\r\n
            switch (id) {\r\n
            case c_oAscAsyncAction["Open"]:\r\n
                this.onOpenDocument();\r\n
                break;\r\n
            }\r\n
        }\r\n
    },\r\n
    _hideLoadSplash: function () {\r\n
        var preloader = Ext.get("loading-mask");\r\n
        if (preloader) {\r\n
            Ext.Anim.run(preloader, "fade", {\r\n
                out: true,\r\n
                duration: 1000,\r\n
                after: function () {\r\n
                    preloader.destroy();\r\n
                }\r\n
            });\r\n
        }\r\n
    },\r\n
    _isSupport: function () {\r\n
        return (Ext.browser.is.WebKit && (Ext.os.is.iOS || Ext.os.is.Android || Ext.os.is.Desktop));\r\n
    },\r\n
    printText: "Printing...",\r\n
    criticalErrorTitle: "Error",\r\n
    notcriticalErrorTitle: "Warning",\r\n
    errorDefaultMessage: "Error code: %1",\r\n
    criticalErrorExtText: \'Press "Ok" to reload view page.\',\r\n
    uploadImageSizeMessage: "Maximium image size limit exceeded.",\r\n
    uploadImageExtMessage: "Unknown image format.",\r\n
    uploadImageFileCountMessage: "No images uploaded.",\r\n
    unknownErrorText: "Unknown error.",\r\n
    convertationTimeoutText: "Convertation timeout exceeded.",\r\n
    convertationErrorText: "Convertation failed.",\r\n
    downloadErrorText: "Download failed.",\r\n
    unsupportedBrowserErrorText: "Your browser is not supported.",\r\n
    errorKeyEncrypt: "Unknown key descriptor",\r\n
    errorKeyExpire: "Key descriptor expired",\r\n
    errorUsersExceed: "Count of users was exceed",\r\n
    textAnonymous: "Anonymous",\r\n
    textLoadingDocument: "LOADING DOCUMENT"\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12591</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
