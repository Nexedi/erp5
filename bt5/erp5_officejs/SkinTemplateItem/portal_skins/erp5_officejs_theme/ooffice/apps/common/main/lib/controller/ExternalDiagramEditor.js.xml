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
            <value> <string>ts44308801.68</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ExternalDiagramEditor.js</string> </value>
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
Common.Controllers = Common.Controllers || {};\r\n
define(["core", "common/main/lib/view/ExternalDiagramEditor"], function () {\r\n
    Common.Controllers.ExternalDiagramEditor = Backbone.Controller.extend(_.extend((function () {\r\n
        var appLang = "en",\r\n
        externalEditor = null;\r\n
        var createExternalEditor = function () {\r\n
            externalEditor = new DocsAPI.DocEditor("id-diagram-editor-placeholder", {\r\n
                width: "100%",\r\n
                height: "100%",\r\n
                documentType: "spreadsheet",\r\n
                document: {\r\n
                    permissions: {\r\n
                        edit: true,\r\n
                        download: false\r\n
                    }\r\n
                },\r\n
                editorConfig: {\r\n
                    mode: "editdiagram",\r\n
                    lang: appLang,\r\n
                    canCoAuthoring: false,\r\n
                    canBackToFolder: false,\r\n
                    canCreateNew: false,\r\n
                    user: {\r\n
                        id: ("uid-" + Date.now()),\r\n
                        name: this.textAnonymous\r\n
                    }\r\n
                },\r\n
                events: {\r\n
                    "onReady": function () {},\r\n
                    "onDocumentStateChange": function () {},\r\n
                    "onError": function () {},\r\n
                    "onInternalMessage": _.bind(this.onInternalMessage, this)\r\n
                }\r\n
            });\r\n
            Common.Gateway.on("processmouse", _.bind(this.onProcessMouse, this));\r\n
        };\r\n
        return {\r\n
            views: ["Common.Views.ExternalDiagramEditor"],\r\n
            initialize: function () {\r\n
                this.addListeners({\r\n
                    "Common.Views.ExternalDiagramEditor": {\r\n
                        "setchartdata": _.bind(this.setChartData, this),\r\n
                        "drag": _.bind(function (o, state) {\r\n
                            externalEditor.serviceCommand("window:drag", state == "start");\r\n
                        },\r\n
                        this),\r\n
                        "show": _.bind(function (cmp) {\r\n
                            var h = this.diagramEditorView.getHeight();\r\n
                            if (window.innerHeight > h && h < 700 || window.innerHeight < h) {\r\n
                                h = Math.min(window.innerHeight, 700);\r\n
                                this.diagramEditorView.setHeight(h);\r\n
                            }\r\n
                            if (externalEditor) {\r\n
                                externalEditor.serviceCommand("setAppDisabled", false);\r\n
                                if (this.needDisableEditing && this.diagramEditorView._isExternalDocReady) {\r\n
                                    this.onDiagrammEditingDisabled();\r\n
                                }\r\n
                                externalEditor.attachMouseEvents();\r\n
                            } else {\r\n
                                createExternalEditor.apply(this);\r\n
                            }\r\n
                            this.isExternalEditorVisible = true;\r\n
                        },\r\n
                        this),\r\n
                        "hide": _.bind(function (cmp) {\r\n
                            if (externalEditor) {\r\n
                                externalEditor.detachMouseEvents();\r\n
                                this.isExternalEditorVisible = false;\r\n
                            }\r\n
                        },\r\n
                        this)\r\n
                    }\r\n
                });\r\n
            },\r\n
            onLaunch: function () {\r\n
                this.diagramEditorView = this.createView("Common.Views.ExternalDiagramEditor", {\r\n
                    handler: _.bind(this.handler, this)\r\n
                });\r\n
            },\r\n
            setApi: function (api) {\r\n
                this.api = api;\r\n
                this.api.asc_registerCallback("asc_onCloseChartEditor", _.bind(this.onDiagrammEditingDisabled, this));\r\n
                return this;\r\n
            },\r\n
            handler: function (result, value) {\r\n
                externalEditor.serviceCommand("queryClose", {\r\n
                    mr: result\r\n
                });\r\n
                return true;\r\n
            },\r\n
            setChartData: function () {\r\n
                externalEditor && externalEditor.serviceCommand("setChartData", this.diagramEditorView._chartData);\r\n
                this.diagramEditorView._chartData = null;\r\n
            },\r\n
            loadConfig: function (data) {\r\n
                if (data && data.config && data.config.lang) {\r\n
                    appLang = data.config.lang;\r\n
                }\r\n
            },\r\n
            onDiagrammEditingDisabled: function () {\r\n
                if (!this.diagramEditorView.isVisible() || !this.diagramEditorView._isExternalDocReady) {\r\n
                    this.needDisableEditing = true;\r\n
                    return;\r\n
                }\r\n
                this.diagramEditorView.setControlsDisabled(true);\r\n
                Common.UI.alert({\r\n
                    title: this.warningTitle,\r\n
                    msg: this.warningText,\r\n
                    iconCls: "warn",\r\n
                    buttons: ["ok"],\r\n
                    callback: _.bind(function (btn) {\r\n
                        this.setControlsDisabled(false);\r\n
                        this.diagramEditorView.hide();\r\n
                    },\r\n
                    this)\r\n
                });\r\n
                this.needDisableEditing = false;\r\n
            },\r\n
            onInternalMessage: function (data) {\r\n
                var eventData = data.data;\r\n
                if (this.diagramEditorView) {\r\n
                    if (eventData.type == "documentReady") {\r\n
                        this.diagramEditorView._isExternalDocReady = true;\r\n
                        this.diagramEditorView.setControlsDisabled(false);\r\n
                        if (this.diagramEditorView._chartData) {\r\n
                            externalEditor && externalEditor.serviceCommand("setChartData", this.diagramEditorView._chartData);\r\n
                            this.diagramEditorView._chartData = null;\r\n
                        }\r\n
                        if (this.needDisableEditing) {\r\n
                            this.onDiagrammEditingDisabled();\r\n
                        }\r\n
                    } else {\r\n
                        if (eventData.type == "shortcut") {\r\n
                            if (eventData.data.key == "escape") {\r\n
                                this.diagramEditorView.hide();\r\n
                            }\r\n
                        } else {\r\n
                            if (eventData.type == "canClose") {\r\n
                                if (eventData.data.answer === true) {\r\n
                                    if (externalEditor) {\r\n
                                        externalEditor.serviceCommand("setAppDisabled", true);\r\n
                                        externalEditor.serviceCommand((eventData.data.mr == "ok") ? "getChartData" : "clearChartData");\r\n
                                    }\r\n
                                    this.diagramEditorView.hide();\r\n
                                }\r\n
                            } else {\r\n
                                if (eventData.type == "processMouse") {\r\n
                                    if (eventData.data.event == "mouse:up") {\r\n
                                        this.diagramEditorView.binding.dragStop();\r\n
                                    } else {\r\n
                                        if (eventData.data.event == "mouse:move") {\r\n
                                            var x = parseInt(this.diagramEditorView.$window.css("left")) + eventData.data.pagex,\r\n
                                            y = parseInt(this.diagramEditorView.$window.css("top")) + eventData.data.pagey + 34;\r\n
                                            this.diagramEditorView.binding.drag({\r\n
                                                pageX: x,\r\n
                                                pageY: y\r\n
                                            });\r\n
                                        }\r\n
                                    }\r\n
                                } else {\r\n
                                    this.diagramEditorView.fireEvent("internalmessage", this.diagramEditorView, eventData);\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            },\r\n
            onProcessMouse: function (data) {\r\n
                if (data.type == "mouseup" && this.isExternalEditorVisible) {\r\n
                    externalEditor && externalEditor.serviceCommand("processmouse", data);\r\n
                }\r\n
            },\r\n
            warningTitle: "Warning",\r\n
            warningText: "The object is disabled because of editing by another user.",\r\n
            textClose: "Close",\r\n
            textAnonymous: "Anonymous"\r\n
        };\r\n
    })(), Common.Controllers.ExternalDiagramEditor || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10580</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
