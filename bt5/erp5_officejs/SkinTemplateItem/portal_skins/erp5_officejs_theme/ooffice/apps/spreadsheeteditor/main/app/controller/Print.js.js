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
            <value> <string>ts44308425.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Print.js</string> </value>
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
 define(["core", "spreadsheeteditor/main/app/view/FileMenuPanels", "spreadsheeteditor/main/app/view/PrintSettings"], function () {\r\n
    SSE.Controllers.Print = Backbone.Controller.extend(_.extend({\r\n
        views: ["MainSettingsPrint"],\r\n
        initialize: function () {\r\n
            this.adjPrintParams = new Asc.asc_CAdjustPrint();\r\n
            this.adjPrintParams.asc_setPrintType(c_oAscPrintType.ActiveSheets);\r\n
            this.adjPrintParams.asc_setLayoutPageType(c_oAscLayoutPageType.ActualSize);\r\n
            this.diffParams = {};\r\n
            this.addListeners({\r\n
                "MainSettingsPrint": {\r\n
                    "show": _.bind(this.onShowMainSettingsPrint, this),\r\n
                    "render:after": _.bind(this.onAfterRender, this)\r\n
                },\r\n
                "Statusbar": {\r\n
                    "updatesheetsinfo": _.bind(function () {\r\n
                        if (this.printSettings.isVisible()) {\r\n
                            this.updateSettings();\r\n
                        } else {\r\n
                            this.isFillSheets = false;\r\n
                            this.diffParams = {};\r\n
                        }\r\n
                    },\r\n
                    this)\r\n
                },\r\n
                "PrintSettings": {\r\n
                    "changerange": _.bind(this.onChangeRange, this)\r\n
                }\r\n
            });\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.printSettings = this.createView("MainSettingsPrint");\r\n
        },\r\n
        onAfterRender: function (view) {\r\n
            this.printSettings.cmbSheet.on("selected", _.bind(this.comboSheetsChange, this));\r\n
            this.printSettings.btnOk.on("click", _.bind(this.querySavePrintSettings, this));\r\n
            var toolbar = SSE.getController("Toolbar").getView("Toolbar");\r\n
            if (toolbar) {\r\n
                toolbar.mnuPrint.on("item:click", _.bind(this.openPrintSettings, this));\r\n
            }\r\n
        },\r\n
        setApi: function (o) {\r\n
            this.api = o;\r\n
        },\r\n
        updateSettings: function () {\r\n
            var wc = this.api.asc_getWorksheetsCount(),\r\n
            i = -1;\r\n
            var items = [{\r\n
                displayValue: this.strAllSheets,\r\n
                value: -255\r\n
            }];\r\n
            while (++i < wc) {\r\n
                if (!this.api.asc_isWorksheetHidden(i)) {\r\n
                    items.push({\r\n
                        displayValue: this.api.asc_getWorksheetName(i),\r\n
                        value: i\r\n
                    });\r\n
                }\r\n
            }\r\n
            this.printSettings.cmbSheet.store.reset(items);\r\n
            var item = this.printSettings.cmbSheet.store.findWhere({\r\n
                value: this.printSettings.cmbSheet.getValue()\r\n
            }) || this.printSettings.cmbSheet.store.findWhere({\r\n
                value: this.api.asc_getActiveWorksheetIndex()\r\n
            });\r\n
            if (item) {\r\n
                this.printSettings.cmbSheet.setValue(item.get("value"));\r\n
            }\r\n
        },\r\n
        comboSheetsChange: function (combo, record) {\r\n
            var newvalue = record.value;\r\n
            if (newvalue == -255) {\r\n
                this.indeterminatePageOptions(this.printSettings);\r\n
            } else {\r\n
                this.fillPageOptions(this.printSettings, this.api.asc_getPageOptions(newvalue));\r\n
            }\r\n
        },\r\n
        isDiffRefill: function () {\r\n
            for (var item in this.diffParams) {\r\n
                if (this.diffParams[item] == undefined) {\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            return item == undefined;\r\n
        },\r\n
        indeterminatePageOptions: function (panel) {\r\n
            if (this.isDiffRefill()) {\r\n
                var wc = this.api.asc_getWorksheetsCount();\r\n
                if (wc == 1) {\r\n
                    this.diffParams.orientation = false;\r\n
                    this.diffParams.size = false;\r\n
                    this.diffParams.headings = false;\r\n
                    this.diffParams.grid = false;\r\n
                    this.diffParams.margintop = false;\r\n
                    this.diffParams.marginright = false;\r\n
                    this.diffParams.marginbottom = false;\r\n
                    this.diffParams.marginleft = false;\r\n
                } else {\r\n
                    var index = 0;\r\n
                    var opts = this.api.asc_getPageOptions(index),\r\n
                    opts_next;\r\n
                    while (++index < wc) {\r\n
                        opts_next = this.api.asc_getPageOptions(index);\r\n
                        if (this.diffParams.orientation == undefined) {\r\n
                            this.diffParams.orientation = opts.asc_getPageSetup().asc_getOrientation() != opts_next.asc_getPageSetup().asc_getOrientation();\r\n
                        }\r\n
                        if (this.diffParams.size == undefined) {\r\n
                            this.diffParams.size = (opts.asc_getPageSetup().asc_getWidth() != opts_next.asc_getPageSetup().asc_getWidth() || opts.asc_getPageSetup().asc_getHeight() != opts_next.asc_getPageSetup().asc_getHeight());\r\n
                        }\r\n
                        if (this.diffParams.headings == undefined) {\r\n
                            this.diffParams.headings = opts.asc_getHeadings() != opts_next.asc_getHeadings();\r\n
                        }\r\n
                        if (this.diffParams.grid == undefined) {\r\n
                            this.diffParams.grid = opts.asc_getGridLines() != opts_next.asc_getGridLines();\r\n
                        }\r\n
                        if (this.diffParams.margintop == undefined) {\r\n
                            this.diffParams.margintop = Math.abs(opts.asc_getPageMargins().asc_getTop() - opts_next.asc_getPageMargins().asc_getTop()) > 0.001;\r\n
                        }\r\n
                        if (this.diffParams.marginright == undefined) {\r\n
                            this.diffParams.marginright = Math.abs(opts.asc_getPageMargins().asc_getRight() - opts_next.asc_getPageMargins().asc_getRight()) > 0.001;\r\n
                        }\r\n
                        if (this.diffParams.marginbottom == undefined) {\r\n
                            this.diffParams.marginbottom = Math.abs(opts.asc_getPageMargins().asc_getBottom() - opts_next.asc_getPageMargins().asc_getBottom()) > 0.001;\r\n
                        }\r\n
                        if (this.diffParams.marginleft == undefined) {\r\n
                            this.diffParams.marginleft = Math.abs(opts.asc_getPageMargins().asc_getLeft() - opts_next.asc_getPageMargins().asc_getLeft()) > 0.001;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (this.diffParams.orientation) {\r\n
                panel.cmbPaperOrientation.setValue("-");\r\n
            }\r\n
            if (this.diffParams.size) {\r\n
                panel.cmbPaperSize.setValue("-");\r\n
            }\r\n
            if (this.diffParams.margintop) {\r\n
                panel.spnMarginTop.setValue("-");\r\n
            }\r\n
            if (this.diffParams.marginright) {\r\n
                panel.spnMarginRight.setValue("-");\r\n
            }\r\n
            if (this.diffParams.marginbottom) {\r\n
                panel.spnMarginBottom.setValue("-");\r\n
            }\r\n
            if (this.diffParams.marginleft) {\r\n
                panel.spnMarginLeft.setValue("-");\r\n
            }\r\n
            if (this.diffParams.grid) {\r\n
                panel.chPrintGrid.setValue("indeterminate");\r\n
            }\r\n
            if (this.diffParams.headings) {\r\n
                panel.chPrintRows.setValue("indeterminate");\r\n
            }\r\n
        },\r\n
        fillPageOptions: function (panel, props) {\r\n
            var opt = props.asc_getPageSetup();\r\n
            var item = panel.cmbPaperOrientation.store.findWhere({\r\n
                value: opt.asc_getOrientation()\r\n
            });\r\n
            if (item) {\r\n
                panel.cmbPaperOrientation.setValue(item.get("value"));\r\n
            }\r\n
            var w = opt.asc_getWidth();\r\n
            var h = opt.asc_getHeight();\r\n
            item = panel.cmbPaperSize.store.findWhere({\r\n
                value: w + "|" + h\r\n
            });\r\n
            if (item) {\r\n
                panel.cmbPaperSize.setValue(item.get("value"));\r\n
            } else {\r\n
                panel.cmbPaperSize.setValue("Custom (" + w + " x " + h);\r\n
            }\r\n
            opt = props.asc_getPageMargins();\r\n
            panel.spnMarginLeft.setValue(Common.Utils.Metric.fnRecalcFromMM(opt.asc_getLeft()));\r\n
            panel.spnMarginTop.setValue(Common.Utils.Metric.fnRecalcFromMM(opt.asc_getTop()));\r\n
            panel.spnMarginRight.setValue(Common.Utils.Metric.fnRecalcFromMM(opt.asc_getRight()));\r\n
            panel.spnMarginBottom.setValue(Common.Utils.Metric.fnRecalcFromMM(opt.asc_getBottom()));\r\n
            panel.chPrintGrid.setValue(props.asc_getGridLines());\r\n
            panel.chPrintRows.setValue(props.asc_getHeadings());\r\n
        },\r\n
        fillPrintOptions: function (panel, props) {\r\n
            panel.setRange(props.asc_getPrintType());\r\n
        },\r\n
        getPageOptions: function (panel) {\r\n
            var props = new Asc.asc_CPageOptions();\r\n
            props.asc_setGridLines(panel.chPrintGrid.getValue() == "indeterminate" ? undefined : panel.chPrintGrid.getValue() == "checked" ? 1 : 0);\r\n
            props.asc_setHeadings(panel.chPrintRows.getValue() == "indeterminate" ? undefined : panel.chPrintRows.getValue() == "checked" ? 1 : 0);\r\n
            var opt = new Asc.asc_CPageSetup();\r\n
            opt.asc_setOrientation(panel.cmbPaperOrientation.getValue() == "-" ? undefined : panel.cmbPaperOrientation.getValue());\r\n
            var pagew = /^\\d{3}\\.?\\d*/.exec(panel.cmbPaperSize.getValue());\r\n
            var pageh = /\\d{3}\\.?\\d*$/.exec(panel.cmbPaperSize.getValue());\r\n
            opt.asc_setWidth(!pagew ? undefined : parseFloat(pagew[0]));\r\n
            opt.asc_setHeight(!pageh ? undefined : parseFloat(pageh[0]));\r\n
            props.asc_setPageSetup(opt);\r\n
            opt = new Asc.asc_CPageMargins();\r\n
            opt.asc_setLeft(panel.spnMarginLeft.getValue() == "-" ? undefined : Common.Utils.Metric.fnRecalcToMM(panel.spnMarginLeft.getNumberValue()));\r\n
            opt.asc_setTop(panel.spnMarginTop.getValue() == "-" ? undefined : Common.Utils.Metric.fnRecalcToMM(panel.spnMarginTop.getNumberValue()));\r\n
            opt.asc_setRight(panel.spnMarginRight.getValue() == "-" ? undefined : Common.Utils.Metric.fnRecalcToMM(panel.spnMarginRight.getNumberValue()));\r\n
            opt.asc_setBottom(panel.spnMarginBottom.getValue() == "-" ? undefined : Common.Utils.Metric.fnRecalcToMM(panel.spnMarginBottom.getNumberValue()));\r\n
            props.asc_setPageMargins(opt);\r\n
            return props;\r\n
        },\r\n
        savePageOptions: function (panel, index) {\r\n
            var opts = this.getPageOptions(panel);\r\n
            if (index == -255) {\r\n
                var wc = this.api.asc_getWorksheetsCount();\r\n
                index = -1;\r\n
                while (++index < wc) {\r\n
                    this.api.asc_setPageOptions(opts, index);\r\n
                }\r\n
                if (this.diffParams.orientation) {\r\n
                    this.diffParams.orientation = opts.asc_getPageSetup().asc_getOrientation() == undefined;\r\n
                }\r\n
                if (this.diffParams.size) {\r\n
                    this.diffParams.size = (opts.asc_getPageSetup().asc_getWidth() == undefined || opts.asc_getPageSetup().asc_getHeight() == undefined);\r\n
                }\r\n
                if (this.diffParams.headings) {\r\n
                    this.diffParams.headings = opts.asc_getHeadings() == undefined;\r\n
                }\r\n
                if (this.diffParams.grid) {\r\n
                    this.diffParams.grid = opts.asc_getGridLines() == undefined;\r\n
                }\r\n
                if (this.diffParams.margintop) {\r\n
                    this.diffParams.margintop = opts.asc_getPageMargins().asc_getTop() == undefined;\r\n
                }\r\n
                if (this.diffParams.marginright) {\r\n
                    this.diffParams.marginright = opts.asc_getPageMargins().asc_getRight() == undefined;\r\n
                }\r\n
                if (this.diffParams.marginbottom) {\r\n
                    this.diffParams.marginbottom = opts.asc_getPageMargins().asc_getBottom() == undefined;\r\n
                }\r\n
                if (this.diffParams.marginleft) {\r\n
                    this.diffParams.marginleft = opts.asc_getPageMargins().asc_getLeft() == undefined;\r\n
                }\r\n
            } else {\r\n
                this.api.asc_setPageOptions(opts, index);\r\n
                this.diffParams = {};\r\n
            }\r\n
        },\r\n
        onShowMainSettingsPrint: function () {\r\n
            if (!this.isFillSheets) {\r\n
                this.isFillSheets = true;\r\n
                this.updateSettings();\r\n
            }\r\n
            if (!this.isUpdatedSettings) {\r\n
                this.isUpdatedSettings = true;\r\n
                var item = this.printSettings.cmbSheet.store.findWhere({\r\n
                    value: this.api.asc_getActiveWorksheetIndex()\r\n
                });\r\n
                if (item) {\r\n
                    this.printSettings.cmbSheet.setValue(item.get("value"));\r\n
                    this.comboSheetsChange(this.printSettings.cmbSheet, item.toJSON());\r\n
                }\r\n
            }\r\n
        },\r\n
        openPrintSettings: function (menu, item) {\r\n
            if (item.value === "options" && this.api) {\r\n
                this.printSettingsDlg = (new SSE.Views.PrintSettings({\r\n
                    handler: _.bind(this.resultPrintSettings, this),\r\n
                    afterrender: _.bind(function () {\r\n
                        this.fillPageOptions(this.printSettingsDlg, this.api.asc_getPageOptions());\r\n
                        this.fillPrintOptions(this.printSettingsDlg, this.adjPrintParams);\r\n
                    },\r\n
                    this)\r\n
                }));\r\n
                this.printSettingsDlg.show();\r\n
            }\r\n
        },\r\n
        resultPrintSettings: function (result, value) {\r\n
            var view = SSE.getController("Toolbar").getView("Toolbar");\r\n
            if (result == "ok") {\r\n
                if (this.checkMargins(this.printSettingsDlg)) {\r\n
                    this.savePageOptions(this.printSettingsDlg, this.printSettingsDlg.getRange() == c_oAscPrintType.EntireWorkbook ? -255 : undefined);\r\n
                    this.adjPrintParams.asc_setPrintType(this.printSettingsDlg.getRange());\r\n
                    this.api.asc_Print(this.adjPrintParams);\r\n
                    this.isUpdatedSettings = false;\r\n
                } else {\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", view);\r\n
        },\r\n
        onChangeRange: function () {\r\n
            var newvalue = this.printSettingsDlg.getRange();\r\n
            if (newvalue == c_oAscPrintType.EntireWorkbook) {\r\n
                this.indeterminatePageOptions(this.printSettingsDlg);\r\n
            } else {\r\n
                if (this.lastCheckedRange == c_oAscPrintType.EntireWorkbook) {\r\n
                    this.fillPageOptions(this.printSettingsDlg, this.api.asc_getPageOptions());\r\n
                }\r\n
            }\r\n
            this.lastCheckedRange = newvalue;\r\n
        },\r\n
        querySavePrintSettings: function () {\r\n
            if (this.checkMargins(this.printSettings)) {\r\n
                this.savePageOptions(this.printSettings, this.printSettings.cmbSheet.getValue());\r\n
                this.printSettings.applySettings();\r\n
            }\r\n
        },\r\n
        checkMargins: function (panel) {\r\n
            if (panel.cmbPaperOrientation.getValue() == c_oAscPageOrientation.PagePortrait) {\r\n
                var pagewidth = /^\\d{3}\\.?\\d*/.exec(panel.cmbPaperSize.getValue());\r\n
                var pageheight = /\\d{3}\\.?\\d*$/.exec(panel.cmbPaperSize.getValue());\r\n
            } else {\r\n
                pageheight = /^\\d{3}\\.?\\d*/.exec(panel.cmbPaperSize.getValue());\r\n
                pagewidth = /\\d{3}\\.?\\d*$/.exec(panel.cmbPaperSize.getValue());\r\n
            }\r\n
            pagewidth = parseFloat(pagewidth[0]);\r\n
            pageheight = parseFloat(pageheight[0]);\r\n
            var ml = Common.Utils.Metric.fnRecalcToMM(panel.spnMarginLeft.getNumberValue());\r\n
            var mr = Common.Utils.Metric.fnRecalcToMM(panel.spnMarginRight.getNumberValue());\r\n
            var mt = Common.Utils.Metric.fnRecalcToMM(panel.spnMarginTop.getNumberValue());\r\n
            var mb = Common.Utils.Metric.fnRecalcToMM(panel.spnMarginBottom.getNumberValue());\r\n
            var result = false;\r\n
            if (ml > pagewidth) {\r\n
                result = "left";\r\n
            } else {\r\n
                if (mr > pagewidth - ml) {\r\n
                    result = "right";\r\n
                } else {\r\n
                    if (mt > pageheight) {\r\n
                        result = "top";\r\n
                    } else {\r\n
                        if (mb > pageheight - mt) {\r\n
                            result = "bottom";\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (result) {\r\n
                Common.UI.warning({\r\n
                    title: this.textWarning,\r\n
                    msg: this.warnCheckMargings,\r\n
                    callback: function (btn, text) {\r\n
                        switch (result) {\r\n
                        case "left":\r\n
                            panel.spnMarginLeft.$el.focus();\r\n
                            return;\r\n
                        case "right":\r\n
                            panel.spnMarginRight.$el.focus();\r\n
                            return;\r\n
                        case "top":\r\n
                            panel.spnMarginTop.$el.focus();\r\n
                            return;\r\n
                        case "bottom":\r\n
                            panel.spnMarginBottom.$el.focus();\r\n
                            return;\r\n
                        }\r\n
                    }\r\n
                });\r\n
                return false;\r\n
            }\r\n
            return true;\r\n
        },\r\n
        warnCheckMargings: "Margins are incorrect",\r\n
        strAllSheets: "All Sheets",\r\n
        textWarning: "Warning"\r\n
    },\r\n
    SSE.Controllers.Print || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>19746</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
