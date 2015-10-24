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
            <value> <string>ts44308425.58</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>RightMenu.js</string> </value>
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
 define(["core", "spreadsheeteditor/main/app/view/RightMenu"], function () {\r\n
    SSE.Controllers.RightMenu = Backbone.Controller.extend({\r\n
        models: [],\r\n
        collections: [],\r\n
        views: ["RightMenu"],\r\n
        initialize: function () {\r\n
            this.editMode = true;\r\n
            this._state = {};\r\n
            this.addListeners({\r\n
                "RightMenu": {\r\n
                    "rightmenuclick": this.onRightMenuClick\r\n
                }\r\n
            });\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.rightmenu = this.createView("RightMenu");\r\n
            this.rightmenu.on("render:after", _.bind(this.onRightMenuAfterRender, this));\r\n
        },\r\n
        onRightMenuAfterRender: function (rightMenu) {\r\n
            rightMenu.shapeSettings.application = this.getApplication();\r\n
            this._settings = [];\r\n
            this._settings[c_oAscTypeSelectElement.Paragraph] = {\r\n
                panelId: "id-paragraph-settings",\r\n
                panel: rightMenu.paragraphSettings,\r\n
                btn: rightMenu.btnText,\r\n
                hidden: 1,\r\n
                locked: false\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Image] = {\r\n
                panelId: "id-image-settings",\r\n
                panel: rightMenu.imageSettings,\r\n
                btn: rightMenu.btnImage,\r\n
                hidden: 1,\r\n
                locked: false\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Shape] = {\r\n
                panelId: "id-shape-settings",\r\n
                panel: rightMenu.shapeSettings,\r\n
                btn: rightMenu.btnShape,\r\n
                hidden: 1,\r\n
                locked: false\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Chart] = {\r\n
                panelId: "id-chart-settings",\r\n
                panel: rightMenu.chartSettings,\r\n
                btn: rightMenu.btnChart,\r\n
                hidden: 1,\r\n
                locked: false\r\n
            };\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onCoAuthoringDisconnect, this));\r\n
            Common.NotificationCenter.on("api:disconnect", _.bind(this.onCoAuthoringDisconnect, this));\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.editMode = mode.isEdit;\r\n
        },\r\n
        onRightMenuClick: function (menu, type, minimized) {\r\n
            if (!minimized && this.editMode) {\r\n
                var panel = this._settings[type].panel;\r\n
                var props = this._settings[type].props;\r\n
                if (props && panel) {\r\n
                    panel.ChangeSettings.call(panel, props);\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("layout:changed", "rightmenu");\r\n
            Common.NotificationCenter.trigger("edit:complete", this.rightmenu);\r\n
        },\r\n
        onSelectionChanged: function (info) {\r\n
            var SelectedObjects = [],\r\n
            selectType = info.asc_getFlags().asc_getSelectionType();\r\n
            if (selectType == c_oAscSelectionType.RangeImage || selectType == c_oAscSelectionType.RangeShape || selectType == c_oAscSelectionType.RangeChart || selectType == c_oAscSelectionType.RangeChartText || selectType == c_oAscSelectionType.RangeShapeText) {\r\n
                SelectedObjects = this.api.asc_getGraphicObjectProps();\r\n
            }\r\n
            if (SelectedObjects.length <= 0 && !this.rightmenu.minimizedMode) {\r\n
                this.rightmenu.clearSelection();\r\n
            }\r\n
            this.onFocusObject(SelectedObjects);\r\n
            var need_disable = info.asc_getLocked(),\r\n
            me = this;\r\n
            if (this._state.prevDisabled != need_disable) {\r\n
                this._state.prevDisabled = need_disable;\r\n
                _.each(this._settings, function (item) {\r\n
                    item.panel.setLocked(need_disable);\r\n
                });\r\n
            }\r\n
        },\r\n
        onFocusObject: function (SelectedObjects) {\r\n
            if (!this.editMode) {\r\n
                return;\r\n
            }\r\n
            for (var i = 0; i < this._settings.length; ++i) {\r\n
                if (this._settings[i]) {\r\n
                    this._settings[i].hidden = 1;\r\n
                    this._settings[i].locked = false;\r\n
                }\r\n
            }\r\n
            for (i = 0; i < SelectedObjects.length; ++i) {\r\n
                var type = SelectedObjects[i].asc_getObjectType();\r\n
                if (type >= this._settings.length || this._settings[type] === undefined) {\r\n
                    continue;\r\n
                }\r\n
                var value = SelectedObjects[i].asc_getObjectValue();\r\n
                if (type == c_oAscTypeSelectElement.Image) {\r\n
                    if (value.asc_getChartProperties() !== null) {\r\n
                        type = c_oAscTypeSelectElement.Chart;\r\n
                    } else {\r\n
                        if (value.asc_getShapeProperties() !== null) {\r\n
                            type = c_oAscTypeSelectElement.Shape;\r\n
                        }\r\n
                    }\r\n
                }\r\n
                this._settings[type].props = value;\r\n
                this._settings[type].hidden = 0;\r\n
                this._settings[type].locked = value.asc_getLocked();\r\n
            }\r\n
            var lastactive = -1,\r\n
            currentactive, priorityactive = -1;\r\n
            for (i = 0; i < this._settings.length; ++i) {\r\n
                var pnl = this._settings[i];\r\n
                if (pnl === undefined) {\r\n
                    continue;\r\n
                }\r\n
                if (pnl.hidden) {\r\n
                    if (!pnl.btn.isDisabled()) {\r\n
                        pnl.btn.setDisabled(true);\r\n
                    }\r\n
                    if (this.rightmenu.GetActivePane() == pnl.panelId) {\r\n
                        currentactive = -1;\r\n
                    }\r\n
                } else {\r\n
                    if (pnl.btn.isDisabled()) {\r\n
                        pnl.btn.setDisabled(false);\r\n
                    }\r\n
                    lastactive = i;\r\n
                    if (pnl.needShow) {\r\n
                        pnl.needShow = false;\r\n
                        priorityactive = i;\r\n
                    } else {\r\n
                        if (this.rightmenu.GetActivePane() == pnl.panelId) {\r\n
                            currentactive = i;\r\n
                        }\r\n
                    }\r\n
                    pnl.panel.setLocked(pnl.locked);\r\n
                }\r\n
            }\r\n
            if (!this.rightmenu.minimizedMode) {\r\n
                var active;\r\n
                if (priorityactive > -1) {\r\n
                    active = priorityactive;\r\n
                } else {\r\n
                    if (lastactive >= 0 && currentactive < 0) {\r\n
                        active = lastactive;\r\n
                    } else {\r\n
                        if (currentactive >= 0) {\r\n
                            active = currentactive;\r\n
                        }\r\n
                    }\r\n
                }\r\n
                if (active !== undefined) {\r\n
                    this.rightmenu.SetActivePane(active);\r\n
                    this._settings[active].panel.ChangeSettings.call(this._settings[active].panel, this._settings[active].props);\r\n
                }\r\n
            }\r\n
            this._settings[c_oAscTypeSelectElement.Image].needShow = false;\r\n
            this._settings[c_oAscTypeSelectElement.Chart].needShow = false;\r\n
        },\r\n
        onCoAuthoringDisconnect: function () {\r\n
            if (this.rightmenu) {\r\n
                this.rightmenu.SetDisabled("", true, true);\r\n
            }\r\n
            this.setMode({\r\n
                isEdit: false\r\n
            });\r\n
        },\r\n
        onInsertImage: function () {\r\n
            this._settings[c_oAscTypeSelectElement.Image].needShow = true;\r\n
        },\r\n
        onInsertChart: function () {\r\n
            this._settings[c_oAscTypeSelectElement.Chart].needShow = true;\r\n
        },\r\n
        onInsertShape: function () {\r\n
            this._settings[c_oAscTypeSelectElement.Shape].needShow = true;\r\n
        },\r\n
        UpdateThemeColors: function () {\r\n
            this.rightmenu.shapeSettings.UpdateThemeColors();\r\n
        },\r\n
        updateMetricUnit: function () {\r\n
            this.rightmenu.paragraphSettings.updateMetricUnit();\r\n
            this.rightmenu.chartSettings.updateMetricUnit();\r\n
            this.rightmenu.imageSettings.updateMetricUnit();\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            var me = this;\r\n
            if (this.api) {\r\n
                this.api.asc_registerCallback("asc_onFocusObject", _.bind(this.onFocusObject, this));\r\n
                this.api.asc_registerCallback("asc_onSelectionChanged", _.bind(this.onSelectionChanged, this));\r\n
                this.api.asc_registerCallback("asc_doubleClickOnObject", _.bind(this.onDoubleClickOnObject, this));\r\n
            }\r\n
        },\r\n
        onDoubleClickOnObject: function (obj) {\r\n
            if (!this.editMode) {\r\n
                return;\r\n
            }\r\n
            var type = obj.asc_getObjectType();\r\n
            if (type >= this._settings.length || this._settings[type] === undefined) {\r\n
                return;\r\n
            }\r\n
            var value = obj.asc_getObjectValue();\r\n
            if (type == c_oAscTypeSelectElement.Image) {\r\n
                if (value.asc_getChartProperties() !== null) {\r\n
                    type = c_oAscTypeSelectElement.Chart;\r\n
                } else {\r\n
                    if (value.asc_getShapeProperties() !== null) {\r\n
                        type = c_oAscTypeSelectElement.Shape;\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (type !== c_oAscTypeSelectElement.Paragraph) {\r\n
                this.rightmenu.SetActivePane(type, true);\r\n
                this._settings[type].panel.ChangeSettings.call(this._settings[type].panel, this._settings[type].props);\r\n
            }\r\n
        }\r\n
    });\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11489</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
