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
            <value> <string>ts44308425.12</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DocumentHolder.js</string> </value>
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
 define(["core", "common/main/lib/util/utils", "common/main/lib/view/CopyWarningDialog", "spreadsheeteditor/main/app/view/DocumentHolder", "spreadsheeteditor/main/app/view/HyperlinkSettingsDialog", "spreadsheeteditor/main/app/view/ParagraphSettingsAdvanced", "spreadsheeteditor/main/app/view/SetValueDialog", "spreadsheeteditor/main/app/view/AutoFilterDialog"], function () {\r\n
    SSE.Controllers.DocumentHolder = Backbone.Controller.extend(_.extend({\r\n
        models: [],\r\n
        collections: [],\r\n
        views: ["DocumentHolder"],\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            me.tooltips = {\r\n
                hyperlink: {},\r\n
                comment: {},\r\n
                coauth: {\r\n
                    ttHeight: 20\r\n
                },\r\n
                row_column: {\r\n
                    ttHeight: 20\r\n
                }\r\n
            };\r\n
            me.mouse = {};\r\n
            me.popupmenu = false;\r\n
            me.rangeSelectionMode = false;\r\n
            me.show_copywarning = true;\r\n
            this.wrapEvents = {\r\n
                apiHideComment: _.bind(this.onApiHideComment, this)\r\n
            };\r\n
            this.addListeners({\r\n
                "DocumentHolder": {\r\n
                    "createdelayedelements": this.onCreateDelayedElements\r\n
                }\r\n
            });\r\n
            var keymap = {};\r\n
            this.hkComments = "command+alt+h,ctrl+alt+h";\r\n
            keymap[this.hkComments] = function () {\r\n
                me.onAddComment();\r\n
            };\r\n
            Common.util.Shortcuts.delegateShortcuts({\r\n
                shortcuts: keymap\r\n
            });\r\n
        },\r\n
        onLaunch: function () {\r\n
            var me = this;\r\n
            me.documentHolder = this.createView("DocumentHolder");\r\n
            me.documentHolder.render();\r\n
            me.documentHolder.el.tabIndex = -1;\r\n
            $(document).on("mousewheel", _.bind(me.onDocumentWheel, me));\r\n
            $(document).on("mousedown", _.bind(me.onDocumentRightDown, me));\r\n
            $(document).on("mouseup", _.bind(me.onDocumentRightUp, me));\r\n
            $(document).on("keydown", _.bind(me.onDocumentKeyDown, me));\r\n
            $(window).on("resize", _.bind(me.onDocumentResize, me));\r\n
            var viewport = SSE.getController("Viewport").getView("Viewport");\r\n
            viewport.hlayout.on("layout:resizedrag", _.bind(me.onDocumentResize, me));\r\n
            Common.NotificationCenter.on({\r\n
                "window:show": function (e) {\r\n
                    me.hideHyperlinkTip();\r\n
                },\r\n
                "modal:show": function (e) {\r\n
                    me.hideCoAuthTips();\r\n
                },\r\n
                "layout:changed": function (e) {\r\n
                    me.hideHyperlinkTip();\r\n
                    me.hideCoAuthTips();\r\n
                    me.onDocumentResize();\r\n
                },\r\n
                "cells:range": function (status) {\r\n
                    me.onCellsRange(status);\r\n
                },\r\n
                "copywarning:show": function () {\r\n
                    me.show_copywarning = false;\r\n
                }\r\n
            });\r\n
        },\r\n
        onCreateDelayedElements: function (view) {\r\n
            var me = this;\r\n
            view.pmiCut.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiCopy.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiPaste.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiImgCut.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiImgCopy.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiImgPaste.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiTextCut.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiTextCopy.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiTextPaste.on("click", _.bind(me.onCopyPaste, me));\r\n
            view.pmiInsertEntire.on("click", _.bind(me.onInsertEntire, me));\r\n
            view.pmiDeleteEntire.on("click", _.bind(me.onDeleteEntire, me));\r\n
            view.pmiInsertCells.menu.on("item:click", _.bind(me.onInsertCells, me));\r\n
            view.pmiDeleteCells.menu.on("item:click", _.bind(me.onDeleteCells, me));\r\n
            view.pmiSortCells.menu.on("item:click", _.bind(me.onSortCells, me));\r\n
            view.pmiClear.menu.on("item:click", _.bind(me.onClear, me));\r\n
            view.pmiInsFunction.on("click", _.bind(me.onInsFunction, me));\r\n
            view.menuAddHyperlink.on("click", _.bind(me.onInsHyperlink, me));\r\n
            view.menuEditHyperlink.on("click", _.bind(me.onInsHyperlink, me));\r\n
            view.menuRemoveHyperlink.on("click", _.bind(me.onDelHyperlink, me));\r\n
            view.pmiRowHeight.on("click", _.bind(me.onSetSize, me));\r\n
            view.pmiColumnWidth.on("click", _.bind(me.onSetSize, me));\r\n
            view.pmiEntireHide.on("click", _.bind(me.onEntireHide, me));\r\n
            view.pmiEntireShow.on("click", _.bind(me.onEntireShow, me));\r\n
            view.pmiAddComment.on("click", _.bind(me.onAddComment, me));\r\n
            view.imgMenu.on("item:click", _.bind(me.onImgMenu, me));\r\n
            view.menuParagraphVAlign.menu.on("item:click", _.bind(me.onParagraphVAlign, me));\r\n
            view.menuAddHyperlinkShape.on("click", _.bind(me.onInsHyperlink, me));\r\n
            view.menuEditHyperlinkShape.on("click", _.bind(me.onInsHyperlink, me));\r\n
            view.menuRemoveHyperlinkShape.on("click", _.bind(me.onRemoveHyperlinkShape, me));\r\n
            view.pmiTextAdvanced.on("click", _.bind(me.onTextAdvanced, me));\r\n
            view.mnuShapeAdvanced.on("click", _.bind(me.onShapeAdvanced, me));\r\n
            view.mnuChartEdit.on("click", _.bind(me.onChartEdit, me));\r\n
            var documentHolderEl = view.cmpEl;\r\n
            if (documentHolderEl) {\r\n
                documentHolderEl.on({\r\n
                    keydown: function (e) {\r\n
                        if (e.keyCode == e.F10 && e.shiftKey) {\r\n
                            e.stopEvent();\r\n
                            me.showObjectMenu(e);\r\n
                        }\r\n
                    },\r\n
                    mousedown: function (e) {\r\n
                        if (e.target.localName == "canvas" && e.button != 2) {\r\n
                            Common.UI.Menu.Manager.hideAll();\r\n
                        }\r\n
                    },\r\n
                    click: function (e) {\r\n
                        if (me.api) {\r\n
                            me.api.isTextAreaBlur = false;\r\n
                            if (e.target.localName == "canvas") {\r\n
                                documentHolderEl.focus();\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                });\r\n
                var addEvent = function (elem, type, fn) {\r\n
                    elem.addEventListener ? elem.addEventListener(type, fn, false) : elem.attachEvent("on" + type, fn);\r\n
                };\r\n
                var eventname = (/Firefox/i.test(navigator.userAgent)) ? "DOMMouseScroll" : "mousewheel";\r\n
                addEvent(view.el, eventname, _.bind(this.onDocumentWheel, this));\r\n
            }\r\n
        },\r\n
        loadConfig: function (data) {\r\n
            this.editorConfig = data.config;\r\n
        },\r\n
        setMode: function (permissions) {\r\n
            this.permissions = permissions; ! (this.permissions.canCoAuthoring && this.permissions.isEdit && this.permissions.canComments) ? Common.util.Shortcuts.suspendEvents(this.hkComments) : Common.util.Shortcuts.resumeEvents(this.hkComments);\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.asc_registerCallback("asc_onContextMenu", _.bind(this.onApiContextMenu, this));\r\n
            this.api.asc_registerCallback("asc_onMouseMove", _.bind(this.onApiMouseMove, this));\r\n
            this.api.asc_registerCallback("asc_onHideComment", this.wrapEvents.apiHideComment);\r\n
            this.api.asc_registerCallback("asc_onHyperlinkClick", _.bind(this.onApiHyperlinkClick, this));\r\n
            this.api.asc_registerCallback("asc_onSetAFDialog", _.bind(this.onApiAutofilter, this));\r\n
            this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onApiCoAuthoringDisconnect, this));\r\n
            Common.NotificationCenter.on("api:disconnect", _.bind(this.onApiCoAuthoringDisconnect, this));\r\n
            return this;\r\n
        },\r\n
        resetApi: function (api) {\r\n
            this.api.asc_unregisterCallback("asc_onHideComment", this.wrapEvents.apiHideComment);\r\n
            this.api.asc_registerCallback("asc_onHideComment", this.wrapEvents.apiHideComment);\r\n
        },\r\n
        onCopyPaste: function (item) {\r\n
            var me = this;\r\n
            if (me.api) {\r\n
                if (typeof window["AscDesktopEditor"] === "object") {\r\n
                    (item.value == "cut") ? me.api.asc_Cut() : ((item.value == "copy") ? me.api.asc_Copy() : me.api.asc_Paste());\r\n
                } else {\r\n
                    var value = window.localStorage.getItem("sse-hide-copywarning");\r\n
                    if (! (value && parseInt(value) == 1) && me.show_copywarning) {\r\n
                        (new Common.Views.CopyWarningDialog({\r\n
                            handler: function (dontshow) {\r\n
                                (item.value == "cut") ? me.api.asc_Cut() : ((item.value == "copy") ? me.api.asc_Copy() : me.api.asc_Paste());\r\n
                                if (dontshow) {\r\n
                                    window.localStorage.setItem("sse-hide-copywarning", 1);\r\n
                                }\r\n
                                Common.NotificationCenter.trigger("edit:complete", me.documentHolder);\r\n
                            }\r\n
                        })).show();\r\n
                    } else {\r\n
                        (item.value == "cut") ? me.api.asc_Cut() : ((item.value == "copy") ? me.api.asc_Copy() : me.api.asc_Paste());\r\n
                        Common.NotificationCenter.trigger("edit:complete", me.documentHolder);\r\n
                    }\r\n
                    Common.component.Analytics.trackEvent("ToolBar", "Copy Warning");\r\n
                }\r\n
            }\r\n
        },\r\n
        onInsertEntire: function (item) {\r\n
            if (this.api) {\r\n
                switch (this.api.asc_getCellInfo().asc_getFlags().asc_getSelectionType()) {\r\n
                case c_oAscSelectionType.RangeRow:\r\n
                    this.api.asc_insertCells(c_oAscInsertOptions.InsertRows);\r\n
                    break;\r\n
                case c_oAscSelectionType.RangeCol:\r\n
                    this.api.asc_insertCells(c_oAscInsertOptions.InsertColumns);\r\n
                    break;\r\n
                }\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Insert Entire");\r\n
            }\r\n
        },\r\n
        onInsertCells: function (menu, item) {\r\n
            if (this.api) {\r\n
                this.api.asc_insertCells(item.value);\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Insert Cells");\r\n
            }\r\n
        },\r\n
        onDeleteEntire: function (item) {\r\n
            if (this.api) {\r\n
                switch (this.api.asc_getCellInfo().asc_getFlags().asc_getSelectionType()) {\r\n
                case c_oAscSelectionType.RangeRow:\r\n
                    this.api.asc_deleteCells(c_oAscDeleteOptions.DeleteRows);\r\n
                    break;\r\n
                case c_oAscSelectionType.RangeCol:\r\n
                    this.api.asc_deleteCells(c_oAscDeleteOptions.DeleteColumns);\r\n
                    break;\r\n
                }\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Delete Entire");\r\n
            }\r\n
        },\r\n
        onDeleteCells: function (menu, item) {\r\n
            if (this.api) {\r\n
                this.api.asc_deleteCells(item.value);\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Delete Cells");\r\n
            }\r\n
        },\r\n
        onSortCells: function (menu, item) {\r\n
            if (this.api) {\r\n
                this.api.asc_sortColFilter(item.value, "");\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Sort Cells");\r\n
            }\r\n
        },\r\n
        onClear: function (menu, item) {\r\n
            if (this.api) {\r\n
                this.api.asc_emptyCells(item.value);\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Clear");\r\n
            }\r\n
        },\r\n
        onInsFunction: function (item) {\r\n
            var controller = this.getApplication().getController("FormulaDialog");\r\n
            if (controller && this.api) {\r\n
                this.api.asc_enableKeyEvents(false);\r\n
                controller.showDialog();\r\n
            }\r\n
        },\r\n
        onInsHyperlink: function (item) {\r\n
            var me = this;\r\n
            var win, props;\r\n
            if (me.api) {\r\n
                var wc = me.api.asc_getWorksheetsCount(),\r\n
                i = -1,\r\n
                items = [];\r\n
                while (++i < wc) {\r\n
                    if (!this.api.asc_isWorksheetHidden(i)) {\r\n
                        items.push({\r\n
                            displayValue: me.api.asc_getWorksheetName(i),\r\n
                            value: me.api.asc_getWorksheetName(i)\r\n
                        });\r\n
                    }\r\n
                }\r\n
                var handlerDlg = function (dlg, result) {\r\n
                    if (result == "ok") {\r\n
                        props = dlg.getSettings();\r\n
                        me.api.asc_insertHyperlink(props);\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me.documentHolder);\r\n
                };\r\n
                var cell = me.api.asc_getCellInfo();\r\n
                props = cell.asc_getHyperlink();\r\n
                win = new SSE.Views.HyperlinkSettingsDialog({\r\n
                    handler: handlerDlg\r\n
                });\r\n
                win.show();\r\n
                win.setSettings({\r\n
                    sheets: items,\r\n
                    currentSheet: me.api.asc_getWorksheetName(me.api.asc_getActiveWorksheetIndex()),\r\n
                    props: props,\r\n
                    text: cell.asc_getText(),\r\n
                    isLock: cell.asc_getFlags().asc_getLockText(),\r\n
                    allowInternal: item.options.inCell\r\n
                });\r\n
            }\r\n
            Common.component.Analytics.trackEvent("DocumentHolder", "Add Hyperlink");\r\n
        },\r\n
        onDelHyperlink: function (item) {\r\n
            if (this.api) {\r\n
                this.api.asc_removeHyperlink();\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Remove Hyperlink");\r\n
            }\r\n
        },\r\n
        onSetSize: function (item) {\r\n
            var me = this;\r\n
            (new SSE.Views.SetValueDialog({\r\n
                title: item.caption,\r\n
                startvalue: item.options.action == "row-height" ? me.api.asc_getRowHeight() : me.api.asc_getColumnWidth(),\r\n
                maxvalue: 409,\r\n
                step: item.options.action == "row-height" ? 0.75 : 1,\r\n
                defaultUnit: item.options.action == "row-height" ? "pt" : "sym",\r\n
                handler: function (dlg, result) {\r\n
                    if (result == "ok") {\r\n
                        var val = dlg.getSettings();\r\n
                        (item.options.action == "row-height") ? me.api.asc_setRowHeight(val) : me.api.asc_setColumnWidth(val);\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me.documentHolder);\r\n
                }\r\n
            })).show();\r\n
        },\r\n
        onEntireHide: function (item) {\r\n
            if (this.api) {\r\n
                this.api[item.isrowmenu ? "asc_hideRows" : "asc_hideColumns"]();\r\n
            }\r\n
        },\r\n
        onEntireShow: function (item) {\r\n
            if (this.api) {\r\n
                this.api[item.isrowmenu ? "asc_showRows" : "asc_showColumns"]();\r\n
            }\r\n
        },\r\n
        onAddComment: function (item) {\r\n
            if (this.api && this.permissions.canCoAuthoring && this.permissions.isEdit && this.permissions.canComments) {\r\n
                this.api.asc_enableKeyEvents(false);\r\n
                var controller = SSE.getController("Common.Controllers.Comments"),\r\n
                cellinfo = this.api.asc_getCellInfo();\r\n
                if (controller) {\r\n
                    var comments = cellinfo.asc_getComments();\r\n
                    if (comments.length) {\r\n
                        controller.onEditComments(comments);\r\n
                    } else {\r\n
                        controller.addDummyComment();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onImgMenu: function (menu, item) {\r\n
            if (this.api) {\r\n
                if (item.options.type == "arrange") {\r\n
                    this.api.asc_setSelectedDrawingObjectLayer(item.value);\r\n
                    Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                    Common.component.Analytics.trackEvent("DocumentHolder", "Arrange");\r\n
                } else {\r\n
                    if (item.options.type == "group") {\r\n
                        this.api[(item.value == "grouping") ? "asc_groupGraphicsObjects" : "asc_unGroupGraphicsObjects"]();\r\n
                        Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                        Common.component.Analytics.trackEvent("DocumentHolder", (item.value == "grouping") ? "Grouping" : "Ungrouping");\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onParagraphVAlign: function (menu, item) {\r\n
            if (this.api) {\r\n
                var properties = new Asc.asc_CImgProperty();\r\n
                properties.asc_putVerticalTextAlign(item.value);\r\n
                this.api.asc_setGraphicObjectProps(properties);\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Paragraph Vertical Align");\r\n
            }\r\n
        },\r\n
        onRemoveHyperlinkShape: function (item) {\r\n
            if (this.api) {\r\n
                this.api.asc_removeHyperlink();\r\n
                Common.NotificationCenter.trigger("edit:complete", this.documentHolder);\r\n
                Common.component.Analytics.trackEvent("DocumentHolder", "Remove Hyperlink");\r\n
            }\r\n
        },\r\n
        onTextAdvanced: function (item) {\r\n
            var me = this;\r\n
            (new SSE.Views.ParagraphSettingsAdvanced({\r\n
                paragraphProps: item.textInfo,\r\n
                api: me.api,\r\n
                handler: function (result, value) {\r\n
                    if (result == "ok") {\r\n
                        if (me.api) {\r\n
                            me.api.asc_setGraphicObjectProps(value.paragraphProps);\r\n
                            Common.component.Analytics.trackEvent("DocumentHolder", "Apply advanced paragraph settings");\r\n
                        }\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me);\r\n
                }\r\n
            })).show();\r\n
        },\r\n
        onShapeAdvanced: function (item) {\r\n
            var me = this;\r\n
            (new SSE.Views.ShapeSettingsAdvanced({\r\n
                shapeProps: item.shapeInfo,\r\n
                api: me.api,\r\n
                handler: function (result, value) {\r\n
                    if (result == "ok") {\r\n
                        if (me.api) {\r\n
                            me.api.asc_setGraphicObjectProps(value.shapeProps);\r\n
                            Common.component.Analytics.trackEvent("DocumentHolder", "Apply advanced shape settings");\r\n
                        }\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me);\r\n
                }\r\n
            })).show();\r\n
        },\r\n
        onChartEdit: function (item) {\r\n
            var me = this;\r\n
            var win, props;\r\n
            if (me.api) {\r\n
                props = me.api.asc_getChartObject();\r\n
                if (props) {\r\n
                    (new SSE.Views.ChartSettingsDlg({\r\n
                        chartSettings: props,\r\n
                        api: me.api,\r\n
                        handler: function (result, value) {\r\n
                            if (result == "ok") {\r\n
                                if (me.api) {\r\n
                                    me.api.asc_editChartDrawingObject(value.chartSettings);\r\n
                                }\r\n
                            }\r\n
                            Common.NotificationCenter.trigger("edit:complete", me);\r\n
                        }\r\n
                    })).show();\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiCoAuthoringDisconnect: function () {\r\n
            this.permissions.isEdit = false;\r\n
        },\r\n
        hideCoAuthTips: function () {\r\n
            if (this.tooltips.coauth.ref) {\r\n
                $(this.tooltips.coauth.ref).remove();\r\n
                this.tooltips.coauth.ref = undefined;\r\n
                this.tooltips.coauth.x_point = undefined;\r\n
                this.tooltips.coauth.y_point = undefined;\r\n
            }\r\n
        },\r\n
        hideHyperlinkTip: function () {\r\n
            if (!this.tooltips.hyperlink.isHidden && this.tooltips.hyperlink.ref) {\r\n
                this.tooltips.hyperlink.ref.hide();\r\n
                this.tooltips.hyperlink.isHidden = true;\r\n
            }\r\n
        },\r\n
        onApiMouseMove: function (dataarray) {\r\n
            if (!this._isFullscreenMenu && dataarray.length) {\r\n
                var index_hyperlink, index_comments, index_locked, index_column, index_row;\r\n
                for (var i = dataarray.length; i > 0; i--) {\r\n
                    switch (dataarray[i - 1].asc_getType()) {\r\n
                    case c_oAscMouseMoveType.Hyperlink:\r\n
                        index_hyperlink = i;\r\n
                        break;\r\n
                    case c_oAscMouseMoveType.Comment:\r\n
                        index_comments = i;\r\n
                        break;\r\n
                    case c_oAscMouseMoveType.LockedObject:\r\n
                        index_locked = i;\r\n
                        break;\r\n
                    case c_oAscMouseMoveType.ResizeColumn:\r\n
                        index_column = i;\r\n
                        break;\r\n
                    case c_oAscMouseMoveType.ResizeRow:\r\n
                        index_row = i;\r\n
                        break;\r\n
                    }\r\n
                }\r\n
                var me = this,\r\n
                showPoint = [0, 0],\r\n
                coAuthTip = me.tooltips.coauth,\r\n
                commentTip = me.tooltips.comment,\r\n
                hyperlinkTip = me.tooltips.hyperlink,\r\n
                row_columnTip = me.tooltips.row_column,\r\n
                pos = [me.documentHolder.cmpEl.offset().left - $(window).scrollLeft(), me.documentHolder.cmpEl.offset().top - $(window).scrollTop()];\r\n
                hyperlinkTip.isHidden = false;\r\n
                row_columnTip.isHidden = false;\r\n
                var getUserName = function (id) {\r\n
                    var usersStore = SSE.getCollection("Common.Collections.Users");\r\n
                    if (usersStore) {\r\n
                        var rec = usersStore.findUser(id);\r\n
                        if (rec) {\r\n
                            return rec.get("username");\r\n
                        }\r\n
                    }\r\n
                    return me.guestText;\r\n
                };\r\n
                if (index_hyperlink) {\r\n
                    var data = dataarray[index_hyperlink - 1],\r\n
                    props = data.asc_getHyperlink();\r\n
                    if (props.asc_getType() == c_oAscHyperlinkType.WebLink) {\r\n
                        var linkstr = props.asc_getTooltip();\r\n
                        if (linkstr) {\r\n
                            linkstr = Common.Utils.String.htmlEncode(linkstr) + "<br><b>" + me.textCtrlClick + "</b>";\r\n
                        } else {\r\n
                            linkstr = props.asc_getHyperlinkUrl() + "<br><b>" + me.textCtrlClick + "</b>";\r\n
                        }\r\n
                    } else {\r\n
                        linkstr = props.asc_getTooltip() || (props.asc_getSheet() + "!" + props.asc_getRange());\r\n
                    }\r\n
                    if (hyperlinkTip.ref && hyperlinkTip.ref.isVisible()) {\r\n
                        if (hyperlinkTip.text != linkstr) {\r\n
                            hyperlinkTip.ref.hide();\r\n
                            hyperlinkTip.isHidden = true;\r\n
                        }\r\n
                    }\r\n
                    if (!hyperlinkTip.ref || !hyperlinkTip.ref.isVisible()) {\r\n
                        hyperlinkTip.text = linkstr;\r\n
                        hyperlinkTip.ref = new Common.UI.Tooltip({\r\n
                            owner: me.documentHolder,\r\n
                            html: true,\r\n
                            title: linkstr\r\n
                        }).on("tooltip:hide", function (tip) {\r\n
                            hyperlinkTip.ref = undefined;\r\n
                            hyperlinkTip.text = "";\r\n
                        });\r\n
                        hyperlinkTip.ref.show([-10000, -10000]);\r\n
                        hyperlinkTip.isHidden = false;\r\n
                    }\r\n
                    showPoint = [data.asc_getX(), data.asc_getY()];\r\n
                    showPoint[0] += (pos[0] + 6);\r\n
                    showPoint[1] += (pos[1] - 20);\r\n
                    showPoint[1] -= hyperlinkTip.ref.getBSTip().$tip.height();\r\n
                    var tipwidth = hyperlinkTip.ref.getBSTip().$tip.width();\r\n
                    if (showPoint[0] + tipwidth > me.tooltips.coauth.bodyWidth) {\r\n
                        showPoint[0] = me.tooltips.coauth.bodyWidth - tipwidth;\r\n
                    }\r\n
                    hyperlinkTip.ref.getBSTip().$tip.css({\r\n
                        top: showPoint[1] + "px",\r\n
                        left: showPoint[0] + "px"\r\n
                    });\r\n
                } else {\r\n
                    me.hideHyperlinkTip();\r\n
                }\r\n
                if (index_column !== undefined || index_row !== undefined) {\r\n
                    var data = dataarray[(index_column !== undefined) ? (index_column - 1) : (index_row - 1)];\r\n
                    var str = Common.Utils.String.format((index_column !== undefined) ? this.textChangeColumnWidth : this.textChangeRowHeight, data.asc_getSizeCCOrPt().toFixed(2), data.asc_getSizePx());\r\n
                    if (row_columnTip.ref && row_columnTip.ref.isVisible()) {\r\n
                        if (row_columnTip.text != str) {\r\n
                            row_columnTip.text = str;\r\n
                            row_columnTip.ref.setTitle(str);\r\n
                            row_columnTip.ref.updateTitle();\r\n
                        }\r\n
                    }\r\n
                    if (!row_columnTip.ref || !row_columnTip.ref.isVisible()) {\r\n
                        row_columnTip.text = str;\r\n
                        row_columnTip.ref = new Common.UI.Tooltip({\r\n
                            owner: me.documentHolder,\r\n
                            html: true,\r\n
                            title: str\r\n
                        }).on("tooltip:hide", function (tip) {\r\n
                            row_columnTip.ref = undefined;\r\n
                            row_columnTip.text = "";\r\n
                        });\r\n
                        row_columnTip.ref.show([-10000, -10000]);\r\n
                        row_columnTip.isHidden = false;\r\n
                        showPoint = [data.asc_getX(), data.asc_getY()];\r\n
                        showPoint[0] += (pos[0] + 6);\r\n
                        showPoint[1] += (pos[1] - 20 - row_columnTip.ttHeight);\r\n
                        var tipwidth = row_columnTip.ref.getBSTip().$tip.width();\r\n
                        if (showPoint[0] + tipwidth > me.tooltips.coauth.bodyWidth) {\r\n
                            showPoint[0] = me.tooltips.coauth.bodyWidth - tipwidth - 20;\r\n
                        }\r\n
                        row_columnTip.ref.getBSTip().$tip.css({\r\n
                            top: showPoint[1] + "px",\r\n
                            left: showPoint[0] + "px"\r\n
                        });\r\n
                    }\r\n
                } else {\r\n
                    if (!row_columnTip.isHidden && row_columnTip.ref) {\r\n
                        row_columnTip.ref.hide();\r\n
                        row_columnTip.isHidden = true;\r\n
                    }\r\n
                }\r\n
                if (me.permissions.isEdit) {\r\n
                    if (index_comments && !this.popupmenu) {\r\n
                        data = dataarray[index_comments - 1];\r\n
                        if (!commentTip.editCommentId && commentTip.moveCommentId != data.asc_getCommentIndexes()[0]) {\r\n
                            commentTip.moveCommentId = data.asc_getCommentIndexes()[0];\r\n
                            if (commentTip.moveCommentTimer) {\r\n
                                clearTimeout(commentTip.moveCommentTimer);\r\n
                            }\r\n
                            var idxs = data.asc_getCommentIndexes(),\r\n
                            x = data.asc_getX(),\r\n
                            y = data.asc_getY(),\r\n
                            leftx = data.asc_getReverseX();\r\n
                            commentTip.moveCommentTimer = setTimeout(function () {\r\n
                                if (commentTip.moveCommentId && !commentTip.editCommentId) {\r\n
                                    commentTip.viewCommentId = commentTip.moveCommentId;\r\n
                                    var commentsController = me.getApplication().getController("Common.Controllers.Comments");\r\n
                                    if (commentsController) {\r\n
                                        if (!commentsController.isSelectedComment) {\r\n
                                            commentsController.onApiShowComment(idxs, x, y, leftx, false, true);\r\n
                                        }\r\n
                                    }\r\n
                                }\r\n
                            },\r\n
                            400);\r\n
                        }\r\n
                    } else {\r\n
                        commentTip.moveCommentId = undefined;\r\n
                        if (commentTip.viewCommentId != undefined) {\r\n
                            commentTip = {};\r\n
                            var commentsController = this.getApplication().getController("Common.Controllers.Comments");\r\n
                            if (commentsController) {\r\n
                                commentsController.onApiHideComment(true);\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    if (index_locked) {\r\n
                        data = dataarray[index_locked - 1];\r\n
                        if (!coAuthTip.XY) {\r\n
                            me.onDocumentResize();\r\n
                        }\r\n
                        if (coAuthTip.x_point != data.asc_getX() || coAuthTip.y_point != data.asc_getY()) {\r\n
                            me.hideCoAuthTips();\r\n
                            coAuthTip.x_point = data.asc_getX();\r\n
                            coAuthTip.y_point = data.asc_getY();\r\n
                            var src = $(document.createElement("div")),\r\n
                            is_sheet_lock = data.asc_getLockedObjectType() == c_oAscMouseMoveLockedObjectType.Sheet || data.asc_getLockedObjectType() == c_oAscMouseMoveLockedObjectType.TableProperties;\r\n
                            coAuthTip.ref = src;\r\n
                            src.addClass("username-tip");\r\n
                            src.css({\r\n
                                height: coAuthTip.ttHeight + "px",\r\n
                                position: "absolute",\r\n
                                zIndex: "900",\r\n
                                visibility: "visible"\r\n
                            });\r\n
                            $(document.body).append(src);\r\n
                            showPoint = [coAuthTip.x_point + coAuthTip.XY[0], coAuthTip.y_point + coAuthTip.XY[1]]; ! is_sheet_lock && (showPoint[0] = coAuthTip.bodyWidth - showPoint[0]);\r\n
                            if (showPoint[1] > coAuthTip.XY[1] && showPoint[1] + coAuthTip.ttHeight < coAuthTip.XY[1] + coAuthTip.apiHeight) {\r\n
                                src.text(getUserName(data.asc_getUserId()));\r\n
                                if (coAuthTip.bodyWidth - showPoint[0] < coAuthTip.ref.width()) {\r\n
                                    src.css({\r\n
                                        visibility: "visible",\r\n
                                        left: "0px",\r\n
                                        top: (showPoint[1] - coAuthTip.ttHeight) + "px"\r\n
                                    });\r\n
                                } else {\r\n
                                    src.css({\r\n
                                        visibility: "visible",\r\n
                                        right: showPoint[0] + "px",\r\n
                                        top: showPoint[1] + "px"\r\n
                                    });\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    } else {\r\n
                        me.hideCoAuthTips();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiHideComment: function () {\r\n
            this.tooltips.comment.viewCommentId = this.tooltips.comment.editCommentId = this.tooltips.comment.moveCommentId = undefined;\r\n
        },\r\n
        onApiHyperlinkClick: function (url) {\r\n
            if (url) {\r\n
                var isvalid = url.strongMatch(Common.Utils.hostnameRe); ! isvalid && (isvalid = url.strongMatch(Common.Utils.emailRe)); ! isvalid && (isvalid = url.strongMatch(Common.Utils.ipRe)); ! isvalid && (isvalid = url.strongMatch(Common.Utils.localRe));\r\n
                if (isvalid) {\r\n
                    var newDocumentPage = window.open(url, "_blank");\r\n
                    if (newDocumentPage) {\r\n
                        newDocumentPage.focus();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiAutofilter: function (config) {\r\n
            var me = this;\r\n
            if (me.permissions.isEdit) {\r\n
                var dlgFilter = new SSE.Views.AutoFilterDialog({\r\n
                    api: this.api\r\n
                }).on({\r\n
                    "close": function () {\r\n
                        if (me.api) {\r\n
                            me.api.asc_enableKeyEvents(true);\r\n
                        }\r\n
                    }\r\n
                });\r\n
                if (me.api) {\r\n
                    me.api.asc_enableKeyEvents(false);\r\n
                }\r\n
                Common.UI.Menu.Manager.hideAll();\r\n
                dlgFilter.setSettings(config);\r\n
                dlgFilter.show();\r\n
            }\r\n
        },\r\n
        onApiContextMenu: function (event) {\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                me.showObjectMenu.call(me, event);\r\n
            },\r\n
            10);\r\n
        },\r\n
        onAfterRender: function (view) {},\r\n
        onDocumentResize: function (e) {\r\n
            var me = this;\r\n
            if (me.documentHolder) {\r\n
                me.tooltips.coauth.XY = [me.documentHolder.cmpEl.offset().left - $(window).scrollLeft(), me.documentHolder.cmpEl.offset().top - $(window).scrollTop()];\r\n
                me.tooltips.coauth.apiHeight = me.documentHolder.cmpEl.height();\r\n
                me.tooltips.coauth.bodyWidth = $(window).width();\r\n
            }\r\n
        },\r\n
        onDocumentWheel: function (e) {\r\n
            if (this.api) {\r\n
                var delta = (_.isUndefined(e.originalEvent)) ? e.wheelDelta : e.originalEvent.wheelDelta;\r\n
                if (_.isUndefined(delta)) {\r\n
                    delta = e.deltaY;\r\n
                }\r\n
                if (e.ctrlKey || e.metaKey) {\r\n
                    var factor = this.api.asc_getZoom();\r\n
                    if (delta < 0) {\r\n
                        factor -= 0.1;\r\n
                        if (! (factor < 0.5)) {\r\n
                            this.api.asc_setZoom(factor);\r\n
                        }\r\n
                    } else {\r\n
                        if (delta > 0) {\r\n
                            factor += 0.1;\r\n
                            if (factor > 0 && !(factor > 2)) {\r\n
                                this.api.asc_setZoom(factor);\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                }\r\n
            }\r\n
        },\r\n
        onDocumentKeyDown: function (event) {\r\n
            if (this.api) {\r\n
                var key = event.keyCode;\r\n
                if ((event.ctrlKey || event.metaKey) && !event.shiftKey) {\r\n
                    if (key === Common.UI.Keys.NUM_PLUS || key === Common.UI.Keys.EQUALITY || (Common.Utils.isOpera && key == 43)) {\r\n
                        if (!this.api.isCellEdited) {\r\n
                            var factor = this.api.asc_getZoom() + 0.1;\r\n
                            if (factor > 0 && !(factor > 2)) {\r\n
                                this.api.asc_setZoom(factor);\r\n
                            }\r\n
                            event.preventDefault();\r\n
                            event.stopPropagation();\r\n
                            return false;\r\n
                        }\r\n
                    } else {\r\n
                        if (key === Common.UI.Keys.NUM_MINUS || key === Common.UI.Keys.MINUS || (Common.Utils.isOpera && key == 45)) {\r\n
                            if (!this.api.isCellEdited) {\r\n
                                factor = this.api.asc_getZoom() - 0.1;\r\n
                                if (! (factor < 0.5)) {\r\n
                                    this.api.asc_setZoom(factor);\r\n
                                }\r\n
                                event.preventDefault();\r\n
                                event.stopPropagation();\r\n
                                return false;\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                } else {\r\n
                    if (key == Common.UI.Keys.F10 && event.shiftKey) {\r\n
                        this.showObjectMenu(event);\r\n
                        event.preventDefault();\r\n
                        event.stopPropagation();\r\n
                        return false;\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onDocumentRightDown: function (event) {\r\n
            event.button == 0 && (this.mouse.isLeftButtonDown = true);\r\n
        },\r\n
        onDocumentRightUp: function (event) {\r\n
            event.button == 0 && (this.mouse.isLeftButtonDown = false);\r\n
        },\r\n
        showObjectMenu: function (event) {\r\n
            if (this.api && this.permissions.isEdit && !this.mouse.isLeftButtonDown && !this.rangeSelectionMode) {\r\n
                var iscellmenu, isrowmenu, iscolmenu, isallmenu, ischartmenu, isimagemenu, istextshapemenu, isshapemenu, istextchartmenu, documentHolder = this.documentHolder,\r\n
                cellinfo = this.api.asc_getCellInfo(),\r\n
                seltype = cellinfo.asc_getFlags().asc_getSelectionType(),\r\n
                isCellLocked = cellinfo.asc_getLocked(),\r\n
                isObjLocked = false,\r\n
                commentsController = this.getApplication().getController("Common.Controllers.Comments");\r\n
                if (!this.permissions.isEditDiagram) {\r\n
                    switch (seltype) {\r\n
                    case c_oAscSelectionType.RangeCells:\r\n
                        iscellmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeRow:\r\n
                        isrowmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeCol:\r\n
                        iscolmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeMax:\r\n
                        isallmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeImage:\r\n
                        isimagemenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeShape:\r\n
                        isshapemenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeChart:\r\n
                        ischartmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeChartText:\r\n
                        istextchartmenu = true;\r\n
                        break;\r\n
                    case c_oAscSelectionType.RangeShapeText:\r\n
                        istextshapemenu = true;\r\n
                        break;\r\n
                    }\r\n
                } else {\r\n
                    var insfunc = (seltype == c_oAscSelectionType.RangeCells);\r\n
                }\r\n
                if (isimagemenu || isshapemenu || ischartmenu) {\r\n
                    isimagemenu = isshapemenu = ischartmenu = false;\r\n
                    var has_chartprops = false;\r\n
                    var selectedObjects = this.api.asc_getGraphicObjectProps();\r\n
                    for (var i = 0; i < selectedObjects.length; i++) {\r\n
                        if (selectedObjects[i].asc_getObjectType() == c_oAscTypeSelectElement.Image) {\r\n
                            var elValue = selectedObjects[i].asc_getObjectValue();\r\n
                            isObjLocked = isObjLocked || elValue.asc_getLocked();\r\n
                            var shapeprops = elValue.asc_getShapeProperties();\r\n
                            if (shapeprops) {\r\n
                                if (shapeprops.asc_getFromChart()) {\r\n
                                    ischartmenu = true;\r\n
                                } else {\r\n
                                    documentHolder.mnuShapeAdvanced.shapeInfo = elValue;\r\n
                                    isshapemenu = true;\r\n
                                }\r\n
                            } else {\r\n
                                if (elValue.asc_getChartProperties()) {\r\n
                                    ischartmenu = true;\r\n
                                    has_chartprops = true;\r\n
                                } else {\r\n
                                    isimagemenu = true;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    documentHolder.mnuUnGroupImg.setDisabled(isObjLocked || !this.api.asc_canUnGroupGraphicsObjects());\r\n
                    documentHolder.mnuGroupImg.setDisabled(isObjLocked || !this.api.asc_canGroupGraphicsObjects());\r\n
                    documentHolder.mnuShapeAdvanced.setVisible(isshapemenu && !isimagemenu && !ischartmenu);\r\n
                    documentHolder.mnuShapeAdvanced.setDisabled(isObjLocked);\r\n
                    documentHolder.mnuChartEdit.setVisible(ischartmenu && !isimagemenu && !isshapemenu && has_chartprops);\r\n
                    documentHolder.mnuChartEdit.setDisabled(isObjLocked);\r\n
                    documentHolder.pmiImgCut.setDisabled(isObjLocked);\r\n
                    documentHolder.pmiImgPaste.setDisabled(isObjLocked);\r\n
                    this.showPopupMenu(documentHolder.imgMenu, {},\r\n
                    event);\r\n
                    documentHolder.mnuShapeSeparator.setVisible(documentHolder.mnuShapeAdvanced.isVisible() || documentHolder.mnuChartEdit.isVisible());\r\n
                } else {\r\n
                    if (istextshapemenu || istextchartmenu) {\r\n
                        documentHolder.pmiTextAdvanced.textInfo = undefined;\r\n
                        var selectedObjects = this.api.asc_getGraphicObjectProps();\r\n
                        for (var i = 0; i < selectedObjects.length; i++) {\r\n
                            var elType = selectedObjects[i].asc_getObjectType();\r\n
                            if (elType == c_oAscTypeSelectElement.Image) {\r\n
                                var value = selectedObjects[i].asc_getObjectValue(),\r\n
                                align = value.asc_getVerticalTextAlign();\r\n
                                isObjLocked = isObjLocked || value.asc_getLocked();\r\n
                                documentHolder.menuParagraphTop.setChecked(align == c_oAscVerticalTextAlign.TEXT_ALIGN_TOP);\r\n
                                documentHolder.menuParagraphCenter.setChecked(align == c_oAscVerticalTextAlign.TEXT_ALIGN_CTR);\r\n
                                documentHolder.menuParagraphBottom.setChecked(align == c_oAscVerticalTextAlign.TEXT_ALIGN_BOTTOM);\r\n
                            } else {\r\n
                                if (elType == c_oAscTypeSelectElement.Paragraph) {\r\n
                                    documentHolder.pmiTextAdvanced.textInfo = selectedObjects[i].asc_getObjectValue();\r\n
                                    isObjLocked = isObjLocked || documentHolder.pmiTextAdvanced.textInfo.asc_getLocked();\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                        var hyperinfo = cellinfo.asc_getHyperlink(),\r\n
                        can_add_hyperlink = this.api.asc_canAddShapeHyperlink();\r\n
                        documentHolder.menuHyperlinkShape.setVisible(istextshapemenu && can_add_hyperlink !== false && hyperinfo);\r\n
                        documentHolder.menuAddHyperlinkShape.setVisible(istextshapemenu && can_add_hyperlink !== false && !hyperinfo);\r\n
                        documentHolder.menuParagraphVAlign.setVisible(istextchartmenu !== true);\r\n
                        documentHolder.pmiTextAdvanced.setVisible(documentHolder.pmiTextAdvanced.textInfo !== undefined);\r\n
                        _.each(documentHolder.textInShapeMenu.items, function (item) {\r\n
                            item.setDisabled(isObjLocked);\r\n
                        });\r\n
                        documentHolder.pmiTextCopy.setDisabled(false);\r\n
                        this.showPopupMenu(documentHolder.textInShapeMenu, {},\r\n
                        event);\r\n
                        documentHolder.textInShapeMenu.items[3].setVisible(documentHolder.menuHyperlinkShape.isVisible() || documentHolder.menuAddHyperlinkShape.isVisible() || documentHolder.menuParagraphVAlign.isVisible());\r\n
                    } else {\r\n
                        if (!this.permissions.isEditDiagram || (seltype !== c_oAscSelectionType.RangeImage && seltype !== c_oAscSelectionType.RangeShape && seltype !== c_oAscSelectionType.RangeChart && seltype !== c_oAscSelectionType.RangeChartText && seltype !== c_oAscSelectionType.RangeShapeText)) {\r\n
                            var iscelledit = this.api.isCellEdited;\r\n
                            documentHolder.pmiInsertEntire.setVisible(isrowmenu || iscolmenu);\r\n
                            documentHolder.pmiDeleteEntire.setVisible(isrowmenu || iscolmenu);\r\n
                            documentHolder.pmiInsertCells.setVisible(iscellmenu && !iscelledit);\r\n
                            documentHolder.pmiDeleteCells.setVisible(iscellmenu && !iscelledit);\r\n
                            documentHolder.pmiSortCells.setVisible((iscellmenu || isallmenu) && !iscelledit);\r\n
                            documentHolder.pmiInsFunction.setVisible(iscellmenu || insfunc);\r\n
                            var hyperinfo = cellinfo.asc_getHyperlink();\r\n
                            documentHolder.menuHyperlink.setVisible(iscellmenu && hyperinfo && !iscelledit);\r\n
                            documentHolder.menuAddHyperlink.setVisible(iscellmenu && !hyperinfo && !iscelledit);\r\n
                            documentHolder.pmiRowHeight.setVisible(isrowmenu || isallmenu);\r\n
                            documentHolder.pmiColumnWidth.setVisible(iscolmenu || isallmenu);\r\n
                            documentHolder.pmiEntireHide.setVisible(iscolmenu || isrowmenu);\r\n
                            documentHolder.pmiEntireShow.setVisible(iscolmenu || isrowmenu);\r\n
                            documentHolder.ssMenu.items[10].setVisible(iscellmenu && !iscelledit && this.permissions.canCoAuthoring && this.permissions.canComments);\r\n
                            documentHolder.pmiAddComment.setVisible(iscellmenu && !iscelledit && this.permissions.canCoAuthoring && this.permissions.canComments);\r\n
                            documentHolder.pmiCellMenuSeparator.setVisible(iscellmenu || isrowmenu || iscolmenu || isallmenu || insfunc);\r\n
                            documentHolder.pmiEntireHide.isrowmenu = isrowmenu;\r\n
                            documentHolder.pmiEntireShow.isrowmenu = isrowmenu;\r\n
                            documentHolder.setMenuItemCommentCaptionMode(cellinfo.asc_getComments().length > 0);\r\n
                            commentsController && commentsController.blockPopover(true);\r\n
                            documentHolder.pmiClear.menu.items[1].setDisabled(iscelledit);\r\n
                            documentHolder.pmiClear.menu.items[2].setDisabled(iscelledit);\r\n
                            documentHolder.pmiClear.menu.items[3].setDisabled(iscelledit);\r\n
                            documentHolder.pmiClear.menu.items[4].setDisabled(iscelledit);\r\n
                            _.each(documentHolder.ssMenu.items, function (item) {\r\n
                                item.setDisabled(isCellLocked);\r\n
                            });\r\n
                            documentHolder.pmiCopy.setDisabled(false);\r\n
                            this.showPopupMenu(documentHolder.ssMenu, {},\r\n
                            event);\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        showPopupMenu: function (menu, value, event) {\r\n
            if (!_.isUndefined(menu) && menu !== null) {\r\n
                Common.UI.Menu.Manager.hideAll();\r\n
                var me = this,\r\n
                documentHolderView = me.documentHolder,\r\n
                showPoint = [event.pageX - documentHolderView.cmpEl.offset().left, event.pageY - documentHolderView.cmpEl.offset().top],\r\n
                menuContainer = documentHolderView.cmpEl.find(Common.Utils.String.format("#menu-container-{0}", menu.id));\r\n
                if (!menu.rendered) {\r\n
                    if (menuContainer.length < 1) {\r\n
                        menuContainer = $(Common.Utils.String.format(\'<div id="menu-container-{0}" style="position: absolute; z-index: 10000;"><div class="dropdown-toggle" data-toggle="dropdown"></div></div>\', menu.id));\r\n
                        documentHolderView.cmpEl.append(menuContainer);\r\n
                    }\r\n
                    menu.render(menuContainer);\r\n
                    menu.cmpEl.attr({\r\n
                        tabindex: "-1"\r\n
                    });\r\n
                }\r\n
                if (\r\n
                /*this.mouse.isRightButtonDown &&*/\r\n
                event.button !== 2) {\r\n
                    var coord = me.api.asc_getActiveCellCoord(),\r\n
                    offset = {\r\n
                        left: 0,\r\n
                        top: 0\r\n
                    };\r\n
                    showPoint[0] = coord.asc_getX() + coord.asc_getWidth() + offset.left;\r\n
                    showPoint[1] = (coord.asc_getY() < 0 ? 0 : coord.asc_getY()) + coord.asc_getHeight() + offset.top;\r\n
                }\r\n
                menuContainer.css({\r\n
                    left: showPoint[0],\r\n
                    top: showPoint[1]\r\n
                });\r\n
                if (_.isFunction(menu.options.initMenu)) {\r\n
                    menu.options.initMenu(value);\r\n
                    menu.alignPosition();\r\n
                }\r\n
                _.delay(function () {\r\n
                    menu.cmpEl.focus();\r\n
                },\r\n
                10);\r\n
                menu.show();\r\n
            }\r\n
        },\r\n
        onCellsRange: function (status) {\r\n
            this.rangeSelectionMode = (status != c_oAscSelectionDialogType.None);\r\n
        },\r\n
        guestText: "Guest",\r\n
        textCtrlClick: "Press CTRL and click link",\r\n
        txtRowHeight: "Row Height",\r\n
        txtHeight: "Height",\r\n
        txtWidth: "Width",\r\n
        tipIsLocked: "This element is being edited by another user.",\r\n
        textChangeColumnWidth: "Column Width {0} symbols ({1} pixels)",\r\n
        textChangeRowHeight: "Row Height {0} points ({1} pixels)"\r\n
    },\r\n
    SSE.Controllers.DocumentHolder || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>54201</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
