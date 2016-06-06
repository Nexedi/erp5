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
            <value> <string>ts44321339.12</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>PrintSettings.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/PrintSettings.template", "common/main/lib/view/AdvancedSettingsWindow", "common/main/lib/component/MetricSpinner", "common/main/lib/component/CheckBox", "common/main/lib/component/RadioBox", "common/main/lib/component/ListView"], function (contentTemplate) {\r\n
    SSE.Views.PrintSettings = Common.Views.AdvancedSettingsWindow.extend(_.extend({\r\n
        options: {\r\n
            alias: "PrintSettings",\r\n
            contentWidth: 280,\r\n
            height: 482\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle,\r\n
                template: [\'<div class="box" style="height:\' + (this.options.height - 85) + \'px;">\', \'<div class="menu-panel" style="overflow: hidden;">\', \'<div style="height: 90px; line-height: 90px;" class="div-category">\' + this.textPrintRange + "</div>", \'<div style="height: 55px; line-height: 55px;" class="div-category">\' + this.textPageSize + "</div>", \'<div style="height: 55px; line-height: 55px;" class="div-category">\' + this.textPageOrientation + "</div>", \'<div style="height: 122px; line-height: 122px;" class="div-category">\' + this.strMargins + "</div>", \'<div style="height: 73px; line-height: 73px;" class="div-category">\' + this.strPrint + "</div>", "</div>", \'<div class="separator"/>\', \'<div class="content-panel">\' + _.template(contentTemplate)({\r\n
                    scope: this\r\n
                }) + "</div>", "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer justify">\', \'<button id="printadv-dlg-btn-hide" class="btn btn-text-default" style="margin-right: 55px; width: 100px;">\' + this.textHideDetails + "</button>", \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;  width: 150px;">\' + this.btnPrint + "</button>", \'<button class="btn normal dlg-btn" result="cancel" style="width: 86px;">\' + this.cancelButtonText + "</button>", "</div>"].join("")\r\n
            },\r\n
            options);\r\n
            Common.Views.AdvancedSettingsWindow.prototype.initialize.call(this, this.options);\r\n
            this.spinners = [];\r\n
        },\r\n
        render: function () {\r\n
            Common.Views.AdvancedSettingsWindow.prototype.render.call(this);\r\n
            this.radioCurrent = new Common.UI.RadioBox({\r\n
                el: $("#printadv-dlg-radio-current"),\r\n
                labelText: this.textCurrentSheet,\r\n
                name: "asc-radio-printrange",\r\n
                checked: true\r\n
            });\r\n
            this.radioCurrent.on("change", _.bind(this.onRadioRangeChange, this));\r\n
            this.radioAll = new Common.UI.RadioBox({\r\n
                el: $("#printadv-dlg-radio-all"),\r\n
                labelText: this.textAllSheets,\r\n
                name: "asc-radio-printrange"\r\n
            });\r\n
            this.radioAll.on("change", _.bind(this.onRadioRangeChange, this));\r\n
            this.radioSelection = new Common.UI.RadioBox({\r\n
                el: $("#printadv-dlg-radio-selection"),\r\n
                labelText: this.textSelection,\r\n
                name: "asc-radio-printrange"\r\n
            });\r\n
            this.radioSelection.on("change", _.bind(this.onRadioRangeChange, this));\r\n
            this.cmbPaperSize = new Common.UI.ComboBox({\r\n
                el: $("#printadv-dlg-combo-pages"),\r\n
                style: "width: 260px;",\r\n
                menuStyle: "max-height: 280px; min-width: 260px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: "215.9|279.4",\r\n
                    displayValue: "US Letter (21,59cm x 27,94cm)"\r\n
                },\r\n
                {\r\n
                    value: "215.9|355.6",\r\n
                    displayValue: "US Legal (21,59cm x 35,56cm)"\r\n
                },\r\n
                {\r\n
                    value: "210|297",\r\n
                    displayValue: "A4 (21cm x 29,7cm)"\r\n
                },\r\n
                {\r\n
                    value: "148.1|209.9",\r\n
                    displayValue: "A5 (14,81cm x 20,99cm)"\r\n
                },\r\n
                {\r\n
                    value: "176|250.1",\r\n
                    displayValue: "B5 (17,6cm x 25,01cm)"\r\n
                },\r\n
                {\r\n
                    value: "104.8|241.3",\r\n
                    displayValue: "Envelope #10 (10,48cm x 24,13cm)"\r\n
                },\r\n
                {\r\n
                    value: "110.1|220.1",\r\n
                    displayValue: "Envelope DL (11,01cm x 22,01cm)"\r\n
                },\r\n
                {\r\n
                    value: "279.4|431.7",\r\n
                    displayValue: "Tabloid (27,94cm x 43,17cm)"\r\n
                },\r\n
                {\r\n
                    value: "297|420.1",\r\n
                    displayValue: "A3 (29,7cm x 42,01cm)"\r\n
                },\r\n
                {\r\n
                    value: "304.8|457.1",\r\n
                    displayValue: "Tabloid Oversize (30,48cm x 45,71cm)"\r\n
                },\r\n
                {\r\n
                    value: "196.8|273",\r\n
                    displayValue: "ROC 16K (19,68cm x 27,3cm)"\r\n
                },\r\n
                {\r\n
                    value: "119.9|234.9",\r\n
                    displayValue: "Envelope Choukei 3 (11,99cm x 23,49cm)"\r\n
                },\r\n
                {\r\n
                    value: "330.2|482.5",\r\n
                    displayValue: "Super B/A3 (33,02cm x 48,25cm)"\r\n
                }]\r\n
            });\r\n
            this.cmbPaperOrientation = new Common.UI.ComboBox({\r\n
                el: $("#printadv-dlg-combo-orient"),\r\n
                style: "width: 115px;",\r\n
                menuStyle: "min-width: 115px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscPageOrientation.PagePortrait,\r\n
                    displayValue: this.strPortrait\r\n
                },\r\n
                {\r\n
                    value: c_oAscPageOrientation.PageLandscape,\r\n
                    displayValue: this.strLandscape\r\n
                }]\r\n
            });\r\n
            this.chPrintGrid = new Common.UI.CheckBox({\r\n
                el: $("#printadv-dlg-chb-grid"),\r\n
                labelText: this.textPrintGrid\r\n
            });\r\n
            this.chPrintRows = new Common.UI.CheckBox({\r\n
                el: $("#printadv-dlg-chb-rows"),\r\n
                labelText: this.textPrintHeadings\r\n
            });\r\n
            this.spnMarginTop = new Common.UI.MetricSpinner({\r\n
                el: $("#printadv-dlg-spin-margin-top"),\r\n
                step: 0.1,\r\n
                width: 115,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginTop);\r\n
            this.spnMarginBottom = new Common.UI.MetricSpinner({\r\n
                el: $("#printadv-dlg-spin-margin-bottom"),\r\n
                step: 0.1,\r\n
                width: 115,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginBottom);\r\n
            this.spnMarginLeft = new Common.UI.MetricSpinner({\r\n
                el: $("#printadv-dlg-spin-margin-left"),\r\n
                step: 0.1,\r\n
                width: 115,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginLeft);\r\n
            this.spnMarginRight = new Common.UI.MetricSpinner({\r\n
                el: $("#printadv-dlg-spin-margin-right"),\r\n
                step: 0.1,\r\n
                width: 115,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginRight);\r\n
            this.btnHide = new Common.UI.Button({\r\n
                el: $("#printadv-dlg-btn-hide")\r\n
            });\r\n
            this.btnHide.on("click", _.bind(this.handlerShowDetails, this));\r\n
            this.panelDetails = $("#printadv-dlg-content-to-hide");\r\n
            this.updateMetricUnit();\r\n
            this.options.afterrender && this.options.afterrender.call(this);\r\n
        },\r\n
        setRange: function (value) {\r\n
            (value == c_oAscPrintType.ActiveSheets) ? this.radioCurrent.setValue(true) : ((value == c_oAscPrintType.EntireWorkbook) ? this.radioAll.setValue(true) : this.radioSelection.setValue(true));\r\n
        },\r\n
        setLayout: function (value) {},\r\n
        getRange: function () {\r\n
            return (this.radioCurrent.getValue() ? c_oAscPrintType.ActiveSheets : (this.radioAll.getValue() ? c_oAscPrintType.EntireWorkbook : c_oAscPrintType.Selection));\r\n
        },\r\n
        getLayout: function () {},\r\n
        onRadioRangeChange: function (radio, newvalue) {\r\n
            if (newvalue) {\r\n
                this.fireEvent("changerange", this);\r\n
            }\r\n
        },\r\n
        updateMetricUnit: function () {\r\n
            if (this.spinners) {\r\n
                for (var i = 0; i < this.spinners.length; i++) {\r\n
                    var spinner = this.spinners[i];\r\n
                    spinner.setDefaultUnit(Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()]);\r\n
                    spinner.setStep(Common.Utils.Metric.getCurrentMetric() == Common.Utils.Metric.c_MetricUnits.cm ? 0.1 : 1);\r\n
                }\r\n
            }\r\n
        },\r\n
        handlerShowDetails: function (btn) {\r\n
            if (!this.extended) {\r\n
                this.extended = true;\r\n
                this.panelDetails.css({\r\n
                    "display": "none"\r\n
                });\r\n
                this.setHeight(286);\r\n
                btn.setCaption(this.textShowDetails);\r\n
            } else {\r\n
                this.extended = false;\r\n
                this.panelDetails.css({\r\n
                    "display": "block"\r\n
                });\r\n
                this.setHeight(482);\r\n
                btn.setCaption(this.textHideDetails);\r\n
            }\r\n
        },\r\n
        textTitle: "Print Settings",\r\n
        strLeft: "Left",\r\n
        strRight: "Right",\r\n
        strTop: "Top",\r\n
        strBottom: "Bottom",\r\n
        strPortrait: "Portrait",\r\n
        strLandscape: "Landscape",\r\n
        textPrintGrid: "Print Gridlines",\r\n
        textPrintHeadings: "Print Rows and Columns Headings",\r\n
        textPageSize: "Page Size",\r\n
        textPageOrientation: "Page Orientation",\r\n
        strMargins: "Margins",\r\n
        strPrint: "Print",\r\n
        btnPrint: "Save & Print",\r\n
        textPrintRange: "Print Range",\r\n
        textLayout: "Layout",\r\n
        textCurrentSheet: "Current Sheet",\r\n
        textAllSheets: "All Sheets",\r\n
        textSelection: "Selection",\r\n
        textActualSize: "Actual Size",\r\n
        textFit: "Fit to width",\r\n
        textShowDetails: "Show Details",\r\n
        cancelButtonText: "Cancel",\r\n
        textHideDetails: "Hide Details"\r\n
    },\r\n
    SSE.Views.PrintSettings || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12638</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
