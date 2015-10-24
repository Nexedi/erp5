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
            <value> <string>ts44308425.68</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Statusbar.js</string> </value>
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
 define(["core", "spreadsheeteditor/main/app/view/Statusbar"], function () {\r\n
    SSE.Controllers.Statusbar = Backbone.Controller.extend(_.extend({\r\n
        models: [],\r\n
        collections: [],\r\n
        views: ["Statusbar"],\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "Statusbar": {\r\n
                    "show:hidden": _.bind(function (obj, index) {\r\n
                        this.hideWorksheet(false, index);\r\n
                    },\r\n
                    this),\r\n
                    "sheet:changename": _.bind(function () {\r\n
                        this.api.asc_closeCellEditor();\r\n
                        this.renameWorksheet();\r\n
                    },\r\n
                    this),\r\n
                    "sheet:setcolor": _.bind(this.setWorksheetColor, this),\r\n
                    "sheet:updateColors": _.bind(this.updateTabsColors, this),\r\n
                    "sheet:move": _.bind(this.moveWorksheet, this)\r\n
                }\r\n
            });\r\n
            var me = this;\r\n
            Common.util.Shortcuts.delegateShortcuts({\r\n
                shortcuts: {\r\n
                    "alt+pageup": function (e) {\r\n
                        me.moveCurrentTab(-1);\r\n
                        e.preventDefault();\r\n
                        e.stopPropagation();\r\n
                    },\r\n
                    "alt+pagedown": function (e) {\r\n
                        me.moveCurrentTab(1);\r\n
                        e.preventDefault();\r\n
                        e.stopPropagation();\r\n
                    }\r\n
                }\r\n
            });\r\n
        },\r\n
        events: function () {\r\n
            return {\r\n
                "click #status-btn-zoomdown": _.bind(this.zoomDocument, this, "down"),\r\n
                "click #status-btn-zoomup": _.bind(this.zoomDocument, this, "up"),\r\n
                "click .cnt-zoom": _.bind(this.onZoomShow, this)\r\n
            };\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.statusbar = this.createView("Statusbar").render();\r\n
            this.statusbar.$el.css("z-index", 10);\r\n
            this.statusbar.labelZoom.css("min-width", 70);\r\n
            this.statusbar.zoomMenu.on("item:click", _.bind(this.menuZoomClick, this));\r\n
            this.bindViewEvents(this.statusbar, this.events);\r\n
            $("#id-tab-menu-new-color").on("click", _.bind(this.onNewBorderColor, this));\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.asc_registerCallback("asc_onZoomChanged", _.bind(this.onZoomChange, this));\r\n
            this.api.asc_registerCallback("asc_onSelectionMathChanged", _.bind(this.onApiMathChanged, this));\r\n
            this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onApiDisconnect, this));\r\n
            Common.NotificationCenter.on("api:disconnect", _.bind(this.onApiDisconnect, this));\r\n
            this.api.asc_registerCallback("asc_onUpdateTabColor", _.bind(this.onApiUpdateTabColor, this));\r\n
            this.api.asc_registerCallback("asc_onEditCell", _.bind(this.onApiEditCell, this));\r\n
            this.api.asc_registerCallback("asc_onWorkbookLocked", _.bind(this.onWorkbookLocked, this));\r\n
            this.api.asc_registerCallback("asc_onWorksheetLocked", _.bind(this.onWorksheetLocked, this));\r\n
            this.api.asc_registerCallback("asc_onAuthParticipantsChanged", _.bind(this.onApiUsersChanged, this));\r\n
            this.api.asc_registerCallback("asc_onParticipantsChanged", _.bind(this.onApiUsersChanged, this));\r\n
            this.api.asc_coAuthoringGetUsers();\r\n
            this.statusbar.setApi(api);\r\n
        },\r\n
        zoomDocument: function (d, e) {\r\n
            switch (d) {\r\n
            case "up":\r\n
                var f = this.api.asc_getZoom() + 0.1; ! (f > 2) && this.api.asc_setZoom(f);\r\n
                break;\r\n
            case "down":\r\n
                f = this.api.asc_getZoom() - 0.1; ! (f < 0.5) && this.api.asc_setZoom(f);\r\n
                break;\r\n
            }\r\n
        },\r\n
        menuZoomClick: function (menu, item) {\r\n
            this.api.asc_setZoom(item.value / 100);\r\n
        },\r\n
        onZoomChange: function (percent, type) {\r\n
            this.statusbar.labelZoom.text(Common.Utils.String.format(this.zoomText, Math.floor((percent + 0.005) * 100)));\r\n
        },\r\n
        onApiDisconnect: function () {\r\n
            this.statusbar.setMode({\r\n
                isDisconnected: true\r\n
            });\r\n
            this.statusbar.update();\r\n
        },\r\n
        onWorkbookLocked: function (locked) {\r\n
            this.statusbar.tabbar[locked ? "addClass" : "removeClass"]("coauth-locked");\r\n
            this.statusbar.btnAddWorksheet.setDisabled(locked || this.statusbar.rangeSelectionMode == c_oAscSelectionDialogType.Chart || this.statusbar.rangeSelectionMode == c_oAscSelectionDialogType.FormatTable);\r\n
            var item, i = this.statusbar.tabbar.getCount();\r\n
            while (i-->0) {\r\n
                item = this.statusbar.tabbar.getAt(i);\r\n
                if (item.sheetindex >= 0) {} else {\r\n
                    item.disable(locked);\r\n
                }\r\n
            }\r\n
        },\r\n
        onWorksheetLocked: function (index, locked) {\r\n
            var count = this.statusbar.tabbar.getCount(),\r\n
            tab;\r\n
            for (var i = count; i-->0;) {\r\n
                tab = this.statusbar.tabbar.getAt(i);\r\n
                if (index == tab.sheetindex) {\r\n
                    tab[locked ? "addClass" : "removeClass"]("coauth-locked");\r\n
                    tab.isLockTheDrag = locked || (this.statusbar.rangeSelectionMode == c_oAscSelectionDialogType.FormatTable);\r\n
                    break;\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiUsersChanged: function (users) {\r\n
            var editusers = [];\r\n
            _.each(users, function (item) {\r\n
                if (!item.asc_getView()) {\r\n
                    editusers.push(item);\r\n
                }\r\n
            });\r\n
            var length = _.size(editusers);\r\n
            var panel = this.statusbar.panelUsers;\r\n
            panel[length > 1 ? "show" : "hide"]();\r\n
            this.statusbar.updateTabbarBorders();\r\n
            var ttblock = panel.find("#status-users-block");\r\n
            if (ttblock.data("bs.tooltip")) {\r\n
                ttblock.removeData("bs.tooltip");\r\n
            }\r\n
            if (length > 1) {\r\n
                panel.find("#status-users-count").text(length);\r\n
                var tip = this.tipUsers + "<br/><br/>",\r\n
                i = 0;\r\n
                for (var n in editusers) {\r\n
                    tip += "\\n" + Common.Utils.String.htmlEncode(editusers[n].asc_getUserName());\r\n
                    if (++i > 3) {\r\n
                        break;\r\n
                    }\r\n
                }\r\n
                if (length > 4) {\r\n
                    tip += "<br/>" + this.tipMoreUsers.replace("%1", length - 4);\r\n
                    tip += "<br/><br/>" + this.tipShowUsers;\r\n
                }\r\n
                ttblock.tooltip({\r\n
                    title: tip,\r\n
                    html: true,\r\n
                    placement: "top"\r\n
                });\r\n
            }\r\n
        },\r\n
        onApiMathChanged: function (info) {\r\n
            this.statusbar.setMathInfo({\r\n
                count: info.asc_getCount(),\r\n
                average: info.asc_getAverage(),\r\n
                sum: info.asc_getSum()\r\n
            });\r\n
            this.statusbar.updateTabbarBorders();\r\n
        },\r\n
        onApiEditCell: function (state) {\r\n
            var disable = state != c_oAscCellEditorState.editEnd;\r\n
            this.statusbar.btnZoomUp.setDisabled(disable);\r\n
            this.statusbar.btnZoomDown.setDisabled(disable);\r\n
            this.statusbar.labelZoom[disable ? "addClass" : "removeClass"]("disabled");\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            this.statusbar.$el.css("z-index", "");\r\n
            this.statusbar.tabMenu.on("item:click", _.bind(this.onTabMenu, this));\r\n
            this.statusbar.btnAddWorksheet.on("click", _.bind(this.onAddWorksheetClick, this));\r\n
            Common.NotificationCenter.on("window:resize", _.bind(this.onWindowResize, this));\r\n
            Common.NotificationCenter.on("cells:range", _.bind(this.onRangeDialogMode, this));\r\n
        },\r\n
        onWindowResize: function (area) {\r\n
            this.statusbar.onTabInvisible(undefined, this.statusbar.tabbar.checkInvisible(true));\r\n
        },\r\n
        onRangeDialogMode: function (mode) {\r\n
            var islocked = this.statusbar.tabbar.hasClass("coauth-locked"),\r\n
            currentIdx = this.api.asc_getActiveWorksheetIndex();\r\n
            this.statusbar.btnAddWorksheet.setDisabled(islocked || mode != c_oAscSelectionDialogType.None);\r\n
            var item, i = this.statusbar.tabbar.getCount();\r\n
            while (i-->0) {\r\n
                item = this.statusbar.tabbar.getAt(i);\r\n
                if (item.sheetindex !== currentIdx) {\r\n
                    item.disable(mode == c_oAscSelectionDialogType.FormatTable);\r\n
                }\r\n
                item.isLockTheDrag = (item.hasClass("coauth-locked") || (mode != c_oAscSelectionDialogType.None));\r\n
            }\r\n
            this.statusbar.rangeSelectionMode = mode;\r\n
        },\r\n
        onTabMenu: function (obj, item, e) {\r\n
            switch (item.value) {\r\n
            case "ins":\r\n
                this.api.asc_insertWorksheet(this.createSheetName());\r\n
                break;\r\n
            case "del":\r\n
                this.deleteWorksheet();\r\n
                break;\r\n
            case "ren":\r\n
                this.renameWorksheet();\r\n
                break;\r\n
            case "copy":\r\n
                this.moveWorksheet(false);\r\n
                break;\r\n
            case "move":\r\n
                this.moveWorksheet(true);\r\n
                break;\r\n
            case "hide":\r\n
                this.hideWorksheet(true);\r\n
                break;\r\n
            }\r\n
        },\r\n
        createSheetName: function () {\r\n
            var items = [],\r\n
            wc = this.api.asc_getWorksheetsCount();\r\n
            while (wc--) {\r\n
                items.push(this.api.asc_getWorksheetName(wc).toLowerCase());\r\n
            }\r\n
            var index = 0,\r\n
            name;\r\n
            while (++index < 1000) {\r\n
                name = this.strSheet + index;\r\n
                if (items.indexOf(name.toLowerCase()) < 0) {\r\n
                    break;\r\n
                }\r\n
            }\r\n
            return name;\r\n
        },\r\n
        createCopyName: function (orig) {\r\n
            var wc = this.api.asc_getWorksheetsCount(),\r\n
            names = [];\r\n
            while (wc--) {\r\n
                names.push(this.api.asc_getWorksheetName(wc).toLowerCase());\r\n
            }\r\n
            var re = /^(.*)\\((\\d)\\)$/.exec(orig);\r\n
            var first = re ? re[1] : orig + " ";\r\n
            var index = 1,\r\n
            name;\r\n
            while (++index < 1000) {\r\n
                name = first + "(" + index + ")";\r\n
                if (names.indexOf(name.toLowerCase()) < 0) {\r\n
                    break;\r\n
                }\r\n
            }\r\n
            return name;\r\n
        },\r\n
        deleteWorksheet: function () {\r\n
            var me = this;\r\n
            if (this.statusbar.tabbar.tabs.length == 1) {\r\n
                Common.UI.warning({\r\n
                    msg: this.errorLastSheet\r\n
                });\r\n
            } else {\r\n
                Common.UI.warning({\r\n
                    msg: this.warnDeleteSheet,\r\n
                    buttons: ["ok", "cancel"],\r\n
                    callback: function (btn) {\r\n
                        if (btn == "ok" && !me.api.asc_deleteWorksheet()) {\r\n
                            _.delay(function () {\r\n
                                Common.UI.error({\r\n
                                    msg: me.errorRemoveSheet\r\n
                                });\r\n
                            },\r\n
                            10);\r\n
                        }\r\n
                    }\r\n
                });\r\n
            }\r\n
        },\r\n
        hideWorksheet: function (hide, index) {\r\n
            if (hide) {\r\n
                this.statusbar.tabbar.tabs.length == 1 ? Common.UI.warning({\r\n
                    msg: this.errorLastSheet\r\n
                }) : this.api["asc_hideWorksheet"](index);\r\n
            } else {\r\n
                this.api["asc_showWorksheet"](index);\r\n
                this.loadTabColor(index);\r\n
            }\r\n
        },\r\n
        renameWorksheet: function () {\r\n
            var me = this;\r\n
            var wc = me.api.asc_getWorksheetsCount(),\r\n
            items = [];\r\n
            if (wc > 0) {\r\n
                var sindex = me.api.asc_getActiveWorksheetIndex();\r\n
                if (me.api.asc_isWorksheetLockedOrDeleted(sindex)) {\r\n
                    return;\r\n
                }\r\n
                while (wc--) {\r\n
                    if (sindex !== wc) {\r\n
                        items.push(me.api.asc_getWorksheetName(wc).toLowerCase());\r\n
                    }\r\n
                }\r\n
                var tab = me.statusbar.tabbar.tabs[this.statusbar.tabbar.getActive()];\r\n
                var top = me.statusbar.$el.position().top - 115,\r\n
                left = tab.$el.offset().left;\r\n
                var current = me.api.asc_getWorksheetName(me.api.asc_getActiveWorksheetIndex());\r\n
                (new SSE.Views.Statusbar.RenameDialog({\r\n
                    current: current,\r\n
                    names: items,\r\n
                    handler: function (btn, s) {\r\n
                        if (btn == "ok" && s != current) {\r\n
                            me.api.asc_renameWorksheet(s);\r\n
                            tab.setCaption(s);\r\n
                            me.statusbar.fireEvent("updatesheetsinfo", me.statusbar);\r\n
                        }\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                    }\r\n
                })).show(left, top);\r\n
            }\r\n
        },\r\n
        moveWorksheet: function (cut, silent, index, destPos) {\r\n
            var me = this;\r\n
            var wc = me.api.asc_getWorksheetsCount(),\r\n
            items = [],\r\n
            i = -1;\r\n
            while (++i < wc) {\r\n
                if (!this.api.asc_isWorksheetHidden(i)) {\r\n
                    items.push({\r\n
                        value: me.api.asc_getWorksheetName(i),\r\n
                        inindex: i\r\n
                    });\r\n
                }\r\n
            }\r\n
            if (!_.isUndefined(silent)) {\r\n
                me.api.asc_showWorksheet(items[index].inindex);\r\n
                Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                    property: "uid",\r\n
                    value: new RegExp("^(doc_|sheet" + this.api.asc_getActiveWorksheetId() + "_)")\r\n
                });\r\n
                if (!_.isUndefined(destPos)) {\r\n
                    me.api.asc_moveWorksheet(items.length === destPos ? wc : items[destPos].inindex);\r\n
                }\r\n
                return;\r\n
            } (new SSE.Views.Statusbar.CopyDialog({\r\n
                title: cut ? me.statusbar.itemMove : me.statusbar.itemCopy,\r\n
                ismove: cut,\r\n
                names: items,\r\n
                handler: function (btn, i) {\r\n
                    if (btn == "ok") {\r\n
                        if (cut) {\r\n
                            me.api.asc_moveWorksheet(i == -255 ? wc : i);\r\n
                        } else {\r\n
                            var new_text = me.createCopyName(me.api.asc_getWorksheetName(me.api.asc_getActiveWorksheetIndex()));\r\n
                            me.api.asc_copyWorksheet(i == -255 ? wc : i, new_text);\r\n
                        }\r\n
                    }\r\n
                    me.api.asc_enableKeyEvents(true);\r\n
                }\r\n
            })).show();\r\n
        },\r\n
        onAddWorksheetClick: function (o, index, opts) {\r\n
            if (this.api) {\r\n
                this.api.asc_closeCellEditor();\r\n
                this.api.asc_addWorksheet(this.createSheetName());\r\n
                Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                    property: "uid",\r\n
                    value: new RegExp("^(doc_|sheet" + this.api.asc_getActiveWorksheetId() + "_)")\r\n
                },\r\n
                false);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this.statusbar);\r\n
        },\r\n
        selectTab: function (sheetindex) {\r\n
            if (this.api) {\r\n
                var hidden = this.api.asc_isWorksheetHidden(sheetindex);\r\n
                if (!hidden) {\r\n
                    var tab = _.findWhere(this.statusbar.tabbar.tabs, {\r\n
                        sheetindex: sheetindex\r\n
                    });\r\n
                    if (tab) {\r\n
                        this.statusbar.tabbar.setActive(tab);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        moveCurrentTab: function (direction) {\r\n
            if (this.api) {\r\n
                var indTab = 0,\r\n
                tabBar = this.statusbar.tabbar,\r\n
                index = this.api.asc_getActiveWorksheetIndex(),\r\n
                length = tabBar.tabs.length;\r\n
                this.statusbar.tabMenu.hide();\r\n
                this.api.asc_closeCellEditor();\r\n
                for (var i = 0; i < length; ++i) {\r\n
                    if (tabBar.tabs[i].sheetindex === index) {\r\n
                        indTab = i;\r\n
                        if (direction > 0) {\r\n
                            indTab++;\r\n
                            if (indTab >= length) {\r\n
                                indTab = 0;\r\n
                            }\r\n
                        } else {\r\n
                            indTab--;\r\n
                            if (indTab < 0) {\r\n
                                indTab = length - 1;\r\n
                            }\r\n
                        }\r\n
                        tabBar.setActive(indTab);\r\n
                        this.api.asc_showWorksheet(tabBar.getAt(indTab).sheetindex);\r\n
                        break;\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiUpdateTabColor: function (index) {\r\n
            this.loadTabColor(index);\r\n
        },\r\n
        setWorksheetColor: function (color) {\r\n
            if (this.api) {\r\n
                var sindex = this.api.asc_getActiveWorksheetIndex();\r\n
                var tab = _.findWhere(this.statusbar.tabbar.tabs, {\r\n
                    sheetindex: sindex\r\n
                });\r\n
                if (tab) {\r\n
                    if ("transparent" === color) {\r\n
                        this.api.asc_setWorksheetTabColor(sindex, null);\r\n
                        tab.$el.find("a").css("box-shadow", "");\r\n
                    } else {\r\n
                        var asc_clr = Common.Utils.ThemeColor.getRgbColor(color);\r\n
                        if (asc_clr) {\r\n
                            this.api.asc_setWorksheetTabColor(sindex, asc_clr);\r\n
                            this.setTabLineColor(tab, asc_clr);\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        updateThemeColors: function () {\r\n
            var updateColors = function (picker, defaultColorIndex) {\r\n
                if (picker) {\r\n
                    var clr, effectcolors = Common.Utils.ThemeColor.getEffectColors();\r\n
                    for (var i = 0; i < effectcolors.length; ++i) {\r\n
                        if (typeof(picker.currentColor) == "object" && clr === undefined && picker.currentColor.effectId == effectcolors[i].effectId) {\r\n
                            clr = effectcolors[i];\r\n
                        }\r\n
                    }\r\n
                    picker.updateColors(effectcolors, Common.Utils.ThemeColor.getStandartColors());\r\n
                    if (picker.currentColor === undefined) {\r\n
                        picker.currentColor = effectcolors[defaultColorIndex];\r\n
                    } else {\r\n
                        if (clr !== undefined) {\r\n
                            picker.currentColor = clr;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            };\r\n
            if (this.statusbar) {\r\n
                updateColors(this.statusbar.mnuTabColor, 1);\r\n
            }\r\n
        },\r\n
        onNewBorderColor: function () {\r\n
            if (this.statusbar && this.statusbar.mnuTabColor) {\r\n
                this.statusbar.mnuTabColor.addNewColor();\r\n
            }\r\n
        },\r\n
        updateTabsColors: function (updateCurrentColor) {\r\n
            var i = -1,\r\n
            tabind = -1,\r\n
            color = null,\r\n
            clr = null,\r\n
            ishidden = false,\r\n
            wc = this.api.asc_getWorksheetsCount(),\r\n
            sindex = this.api.asc_getActiveWorksheetIndex();\r\n
            if (!_.isUndefined(updateCurrentColor)) {\r\n
                var toolbarController = this.application.getController("Toolbar");\r\n
                if (toolbarController) {\r\n
                    this.statusbar.mnuTabColor.updateCustomColors();\r\n
                    color = this.api.asc_getWorksheetTabColor(sindex);\r\n
                    if (color) {\r\n
                        if (color.get_type() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                            clr = {\r\n
                                color: Common.Utils.ThemeColor.getHexColor(color.get_r(), color.get_g(), color.get_b()),\r\n
                                effectValue: color.get_value()\r\n
                            };\r\n
                        } else {\r\n
                            clr = Common.Utils.ThemeColor.getHexColor(color.get_r(), color.get_g(), color.get_b());\r\n
                        }\r\n
                    }\r\n
                    if (_.isObject(clr)) {\r\n
                        var isselected = false;\r\n
                        for (i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] === clr.effectValue) {\r\n
                                this.statusbar.mnuTabColor.select(clr, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.statusbar.mnuTabColor.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.statusbar.mnuTabColor.select(clr || "transparent", true);\r\n
                    }\r\n
                }\r\n
            }\r\n
            i = -1;\r\n
            while (++i < wc) {\r\n
                ++tabind;\r\n
                ishidden = this.api.asc_isWorksheetHidden(i);\r\n
                if (ishidden) {\r\n
                    --tabind;\r\n
                }\r\n
                if (!ishidden) {\r\n
                    this.setTabLineColor(this.statusbar.tabbar.getAt(tabind), this.api.asc_getWorksheetTabColor(i));\r\n
                }\r\n
            }\r\n
        },\r\n
        loadTabColor: function (sheetindex) {\r\n
            if (this.api) {\r\n
                if (!this.api.asc_isWorksheetHidden(sheetindex)) {\r\n
                    var tab = _.findWhere(this.statusbar.tabbar.tabs, {\r\n
                        sheetindex: sheetindex\r\n
                    });\r\n
                    if (tab) {\r\n
                        this.setTabLineColor(tab, this.api.asc_getWorksheetTabColor(sheetindex));\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        setTabLineColor: function (tab, color) {\r\n
            if (tab) {\r\n
                if (null !== color) {\r\n
                    color = "#" + Common.Utils.ThemeColor.getHexColor(color.get_r(), color.get_g(), color.get_b());\r\n
                } else {\r\n
                    color = "";\r\n
                }\r\n
                if (color.length) {\r\n
                    if (!tab.isActive()) {\r\n
                        color = "0px 3px 0 " + Common.Utils.RGBColor(color).toRGBA(0.7) + " inset";\r\n
                    } else {\r\n
                        color = "0px 3px 0 " + color + " inset";\r\n
                    }\r\n
                    tab.$el.find("a").css("box-shadow", color);\r\n
                } else {\r\n
                    tab.$el.find("a").css("box-shadow", "");\r\n
                }\r\n
            }\r\n
        },\r\n
        onZoomShow: function (e) {\r\n
            if (e.target.classList.contains("disabled")) {\r\n
                return false;\r\n
            }\r\n
        },\r\n
        tipUsers: "Document is in the collaborative editing mode.",\r\n
        tipMoreUsers: "and %1 users.",\r\n
        tipShowUsers: "To see all users click the icon below.",\r\n
        zoomText: "Zoom {0}%",\r\n
        errorLastSheet: "Workbook must have at least one visible worksheet.",\r\n
        errorRemoveSheet: "Can\'t delete the worksheet.",\r\n
        warnDeleteSheet: "The worksheet maybe has data. Proceed operation?",\r\n
        strSheet : "Sheet"\r\n
    },\r\n
    SSE.Controllers.Statusbar || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>26124</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
