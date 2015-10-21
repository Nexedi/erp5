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
            <value> <string>ts44321338.37</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>FileMenuPanels.js</string> </value>
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
 define(["common/main/lib/view/DocumentAccessDialog"], function () { ! SSE.Views.FileMenuPanels && (SSE.Views.FileMenuPanels = {});\r\n
    SSE.Views.FileMenuPanels.ViewSaveAs = Common.UI.BaseView.extend({\r\n
        el: "#panel-saveas",\r\n
        menu: undefined,\r\n
        formats: [[{\r\n
            name: "XLSX",\r\n
            imgCls: "xlsx",\r\n
            type: c_oAscFileType.XLSX\r\n
        },\r\n
        {\r\n
            name: "ODS",\r\n
            imgCls: "ods",\r\n
            type: c_oAscFileType.ODS\r\n
        }], [{\r\n
            name: "CSV",\r\n
            imgCls: "csv",\r\n
            type: c_oAscFileType.CSV\r\n
        },\r\n
        {\r\n
            name: "HTML",\r\n
            imgCls: "html",\r\n
            type: c_oAscFileType.HTML\r\n
        }]],\r\n
        template: _.template(["<table><tbody>", "<% _.each(rows, function(row) { %>", "<tr>", "<% _.each(row, function(item) { %>", \'<td><span class="btn-doc-format <%= item.imgCls %>" /></td>\', "<% }) %>", "</tr>", "<% }) %>", "</tbody></table>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template({\r\n
                rows: this.formats\r\n
            }));\r\n
            $(".btn-doc-format", this.el).on("click", _.bind(this.onFormatClick, this));\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            this.flatFormats = _.flatten(this.formats);\r\n
            return this;\r\n
        },\r\n
        onFormatClick: function (e) {\r\n
            var format = /\\s(\\w+)/.exec(e.currentTarget.className);\r\n
            if (format) {\r\n
                format = format[1];\r\n
                var item = _.findWhere(this.flatFormats, {\r\n
                    imgCls: format\r\n
                });\r\n
                if (item && this.menu) {\r\n
                    this.menu.fireEvent("saveas:format", [this.menu, item.type]);\r\n
                }\r\n
            }\r\n
        }\r\n
    });\r\n
    SSE.Views.FileMenuPanels.Settings = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#panel-settings",\r\n
        menu: undefined,\r\n
        template: _.template([\'<div style="width:100%; height:100%; position: relative;">\', \'<div id="id-settings-menu" style="position: absolute; width:200px; top: 0; bottom: 0;" class="no-padding"></div>\', \'<div id="id-settings-content" style="position: absolute; left: 200px; top: 0; right: 0; bottom: 0;" class="no-padding">\', \'<div id="panel-settings-general" style="width:100%; height:100%;" class="no-padding main-settings-panel active"></div>\', \'<div id="panel-settings-print" style="width:100%; height:100%;" class="no-padding main-settings-panel"></div>\', "</div>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.generalSettings = new SSE.Views.FileMenuPanels.MainSettingsGeneral({\r\n
                menu: this.menu\r\n
            });\r\n
            this.generalSettings.options = {\r\n
                alias: "MainSettingsGeneral"\r\n
            };\r\n
            this.generalSettings.render();\r\n
            this.printSettings = SSE.getController("Print").getView("MainSettingsPrint");\r\n
            this.printSettings.menu = this.menu;\r\n
            this.printSettings.render($("#panel-settings-print"));\r\n
            this.viewSettingsPicker = new Common.UI.DataView({\r\n
                el: $("#id-settings-menu"),\r\n
                store: new Common.UI.DataViewStore([{\r\n
                    name: this.txtGeneral,\r\n
                    panel: this.generalSettings,\r\n
                    iconCls: "mnu-settings-general",\r\n
                    selected: true\r\n
                },\r\n
                {\r\n
                    name: this.txtPrint,\r\n
                    panel: this.printSettings,\r\n
                    iconCls: "mnu-print"\r\n
                }]),\r\n
                itemTemplate: _.template([\'<div id="<%= id %>" class="settings-item-wrap">\', \'<div class="settings-icon <%= iconCls %>" style="display: inline-block;" >\', "</div><%= name %>", "</div>"].join(""))\r\n
            });\r\n
            this.viewSettingsPicker.on("item:select", _.bind(function (dataview, itemview, record) {\r\n
                var panel = record.get("panel");\r\n
                $("#id-settings-content > div").removeClass("active");\r\n
                panel.$el.addClass("active");\r\n
                panel.show();\r\n
            },\r\n
            this));\r\n
            return this;\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
            var item = this.viewSettingsPicker.getSelectedRec();\r\n
            if (item[0]) {\r\n
                item[0].get("panel").show();\r\n
            }\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            this.generalSettings && this.generalSettings.setMode(this.mode);\r\n
        },\r\n
        txtGeneral: "General",\r\n
        txtPrint: "Print"\r\n
    },\r\n
    SSE.Views.FileMenuPanels.Settings || {}));\r\n
    SSE.Views.MainSettingsPrint = Common.UI.BaseView.extend(_.extend({\r\n
        menu: undefined,\r\n
        template: _.template([\'<table class="main"><tbody>\', "<tr>", \'<td class="left"><label><%= scope.textSettings %></label></td>\', \'<td class="right"><div id="advsettings-print-combo-sheets" class="input-group-nr" /></td>\', "</tr>", \'<tr class="divider"></tr>\', \'<tr class="divider"></tr>\', "<tr>", \'<td class="left"><label><%= scope.textPageSize %></label></td>\', \'<td class="right"><div id="advsettings-print-combo-pages" class="input-group-nr" /></td>\', "</tr>", \'<tr class="divider"></tr>\', "<tr>", \'<td class="left"><label><%= scope.textPageOrientation %></label></td>\', \'<td class="right"><span id="advsettings-print-combo-orient" /></td>\', "</tr>", \'<tr class="divider"></tr>\', "<tr>", \'<td class="left" style="vertical-align: top;"><label><%= scope.strMargins %></label></td>\', \'<td class="right" style="vertical-align: top;"><div id="advsettings-margins">\', \'<table cols="2" class="no-padding">\', "<tr>", "<td><label><%= scope.strTop %></label></td>", "<td><label><%= scope.strBottom %></label></td>", "</tr>", "<tr>", \'<td><div id="advsettings-spin-margin-top"></div></td>\', \'<td><div id="advsettings-spin-margin-bottom"></div></td>\', "</tr>", "<tr>", "<td><label><%= scope.strLeft %></label></td>", "<td><label><%= scope.strRight %></label></td>", "</tr>", "<tr>", \'<td><div id="advsettings-spin-margin-left"></div></td>\', \'<td><div id="advsettings-spin-margin-right"></div></td>\', "</tr>", "</table>", "</div></td>", "</tr>", \'<tr class="divider"></tr>\', "<tr>", \'<td class="left" style="vertical-align: top;"><label><%= scope.strPrint %></label></td>\', \'<td class="right" style="vertical-align: top;"><div id="advsettings-print">\', \'<div id="advsettings-print-chb-grid" style="margin-bottom: 10px;"/>\', \'<div id="advsettings-print-chb-rows"/>\', "</div></td>", "</tr>", \'<tr class="divider"></tr>\', \'<tr class="divider"></tr>\', "<tr>", \'<td class="left"></td>\', \'<td class="right"><button id="advsettings-print-button-save" class="btn normal dlg-btn primary"><%= scope.okButtonText %></button></td>\', "</tr>", "</tbody></table>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
            this.spinners = [];\r\n
            this._initSettings = true;\r\n
        },\r\n
        render: function (parentEl) {\r\n
            if (parentEl) {\r\n
                this.setElement(parentEl, false);\r\n
            }\r\n
            $(this.el).html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.cmbSheet = new Common.UI.ComboBox({\r\n
                el: $("#advsettings-print-combo-sheets"),\r\n
                style: "width: 260px;",\r\n
                menuStyle: "min-width: 260px;max-height: 280px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: -255,\r\n
                    displayValue: this.strAllSheets\r\n
                }]\r\n
            });\r\n
            this.cmbPaperSize = new Common.UI.ComboBox({\r\n
                el: $("#advsettings-print-combo-pages"),\r\n
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
                el: $("#advsettings-print-combo-orient"),\r\n
                style: "width: 200px;",\r\n
                menuStyle: "min-width: 200px;",\r\n
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
                el: $("#advsettings-print-chb-grid"),\r\n
                labelText: this.textPrintGrid\r\n
            });\r\n
            this.chPrintRows = new Common.UI.CheckBox({\r\n
                el: $("#advsettings-print-chb-rows"),\r\n
                labelText: this.textPrintHeadings\r\n
            });\r\n
            this.spnMarginTop = new Common.UI.MetricSpinner({\r\n
                el: $("#advsettings-spin-margin-top"),\r\n
                step: 0.1,\r\n
                width: 90,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginTop);\r\n
            this.spnMarginBottom = new Common.UI.MetricSpinner({\r\n
                el: $("#advsettings-spin-margin-bottom"),\r\n
                step: 0.1,\r\n
                width: 90,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginBottom);\r\n
            this.spnMarginLeft = new Common.UI.MetricSpinner({\r\n
                el: $("#advsettings-spin-margin-left"),\r\n
                step: 0.1,\r\n
                width: 90,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginLeft);\r\n
            this.spnMarginRight = new Common.UI.MetricSpinner({\r\n
                el: $("#advsettings-spin-margin-right"),\r\n
                step: 0.1,\r\n
                width: 90,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 48.25,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnMarginRight);\r\n
            this.btnOk = new Common.UI.Button({\r\n
                el: "#advsettings-print-button-save"\r\n
            });\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            this.fireEvent("render:after", this);\r\n
            return this;\r\n
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
        applySettings: function () {\r\n
            if (this.menu) {\r\n
                this.menu.fireEvent("settings:apply", [this.menu]);\r\n
            }\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
            if (this._initSettings) {\r\n
                this.updateMetricUnit();\r\n
                this._initSettings = false;\r\n
            }\r\n
            this.fireEvent("show", this);\r\n
        },\r\n
        okButtonText: "Save",\r\n
        strPortrait: "Portrait",\r\n
        strLandscape: "Landscape",\r\n
        textPrintGrid: "Print Gridlines",\r\n
        textPrintHeadings: "Print Rows and Columns Headings",\r\n
        strLeft: "Left",\r\n
        strRight: "Right",\r\n
        strTop: "Top",\r\n
        strBottom: "Bottom",\r\n
        strMargins: "Margins",\r\n
        textPageSize: "Page Size",\r\n
        textPageOrientation: "Page Orientation",\r\n
        strPrint: "Print",\r\n
        textSettings: "Settings for"\r\n
    },\r\n
    SSE.Views.MainSettingsPrint || {}));\r\n
    SSE.Views.FileMenuPanels.MainSettingsGeneral = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#panel-settings-general",\r\n
        menu: undefined,\r\n
        template: _.template([\'<table class="main"><tbody>\', \'<tr class="coauth">\', \'<td class="left"><label><%= scope.txtLiveComment %></label></td>\', \'<td class="right"><div id="fms-chb-live-comment"/></td>\', "</tr>", \'<tr class="divider coauth"></tr>\', \'<tr class="autosave">\', \'<td class="left"><label><%= scope.textAutoSave %></label></td>\', \'<td class="right"><span id="fms-chb-autosave" /></td>\', "</tr>", \'<tr class="divider autosave"></tr>\', "<tr>", \'<td class="left"><label><%= scope.strZoom %></label></td>\', \'<td class="right"><div id="fms-cmb-zoom" class="input-group-nr" /></td>\', "</tr>", \'<tr class="divider"></tr>\', "<tr>", \'<td class="left"><label><%= scope.strFontRender %></label></td>\', \'<td class="right"><span id="fms-cmb-font-render" /></td>\', "</tr>", \'<tr class="divider"></tr>\', \'<tr class="edit">\', \'<td class="left"><label><%= scope.strUnit %></label></td>\', \'<td class="right"><span id="fms-cmb-unit" /></td>\', "</tr>", \'<tr class="divider edit"></tr>\', "<tr>", \'<td class="left"></td>\', \'<td class="right"><button id="fms-btn-apply" class="btn normal dlg-btn primary"><%= scope.okButtonText %></button></td>\', "</tr>", "</tbody></table>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.chLiveComment = new Common.UI.CheckBox({\r\n
                el: $("#fms-chb-live-comment"),\r\n
                labelText: this.strLiveComment\r\n
            });\r\n
            this.cmbZoom = new Common.UI.ComboBox({\r\n
                el: $("#fms-cmb-zoom"),\r\n
                style: "width: 160px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: 50,\r\n
                    displayValue: "50%"\r\n
                },\r\n
                {\r\n
                    value: 60,\r\n
                    displayValue: "60%"\r\n
                },\r\n
                {\r\n
                    value: 70,\r\n
                    displayValue: "70%"\r\n
                },\r\n
                {\r\n
                    value: 80,\r\n
                    displayValue: "80%"\r\n
                },\r\n
                {\r\n
                    value: 90,\r\n
                    displayValue: "90%"\r\n
                },\r\n
                {\r\n
                    value: 100,\r\n
                    displayValue: "100%"\r\n
                },\r\n
                {\r\n
                    value: 110,\r\n
                    displayValue: "110%"\r\n
                },\r\n
                {\r\n
                    value: 120,\r\n
                    displayValue: "120%"\r\n
                },\r\n
                {\r\n
                    value: 150,\r\n
                    displayValue: "150%"\r\n
                },\r\n
                {\r\n
                    value: 175,\r\n
                    displayValue: "175%"\r\n
                },\r\n
                {\r\n
                    value: 200,\r\n
                    displayValue: "200%"\r\n
                }]\r\n
            });\r\n
            this.cmbFontRender = new Common.UI.ComboBox({\r\n
                el: $("#fms-cmb-font-render"),\r\n
                style: "width: 160px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscFontRenderingModeType.hintingAndSubpixeling,\r\n
                    displayValue: this.txtWin\r\n
                },\r\n
                {\r\n
                    value: c_oAscFontRenderingModeType.noHinting,\r\n
                    displayValue: this.txtMac\r\n
                },\r\n
                {\r\n
                    value: c_oAscFontRenderingModeType.hinting,\r\n
                    displayValue: this.txtNative\r\n
                }]\r\n
            });\r\n
            this.chAutosave = new Common.UI.CheckBox({\r\n
                el: $("#fms-chb-autosave"),\r\n
                labelText: this.strAutosave\r\n
            });\r\n
            this.cmbUnit = new Common.UI.ComboBox({\r\n
                el: $("#fms-cmb-unit"),\r\n
                style: "width: 160px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: Common.Utils.Metric.c_MetricUnits["cm"],\r\n
                    displayValue: this.txtCm\r\n
                },\r\n
                {\r\n
                    value: Common.Utils.Metric.c_MetricUnits["pt"],\r\n
                    displayValue: this.txtPt\r\n
                }]\r\n
            });\r\n
            this.btnApply = new Common.UI.Button({\r\n
                el: "#fms-btn-apply"\r\n
            });\r\n
            this.btnApply.on("click", _.bind(this.applySettings, this));\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
            this.updateSettings();\r\n
        },\r\n
        setMode: function (mode) {\r\n
            $("tr.autosave", this.el)[mode.isEdit && mode.canAutosave ? "show" : "hide"]();\r\n
            $("tr.coauth", this.el)[mode.canCoAuthoring && mode.isEdit ? "show" : "hide"]();\r\n
        },\r\n
        updateSettings: function () {\r\n
            var value = window.localStorage.getItem("sse-settings-zoom");\r\n
            var item = this.cmbZoom.store.findWhere({\r\n
                value: parseInt(value)\r\n
            });\r\n
            this.cmbZoom.setValue(item ? parseInt(item.get("value")) : 100);\r\n
            value = window.localStorage.getItem("sse-settings-livecomment");\r\n
            this.chLiveComment.setValue(!(value !== null && parseInt(value) == 0));\r\n
            value = window.localStorage.getItem("sse-settings-fontrender");\r\n
            item = this.cmbFontRender.store.findWhere({\r\n
                value: parseInt(value)\r\n
            });\r\n
            this.cmbFontRender.setValue(item ? item.get("value") : (window.devicePixelRatio > 1 ? c_oAscFontRenderingModeType.noHinting : c_oAscFontRenderingModeType.hintingAndSubpixeling));\r\n
            value = window.localStorage.getItem("sse-settings-unit");\r\n
            item = this.cmbUnit.store.findWhere({\r\n
                value: parseInt(value)\r\n
            });\r\n
            this.cmbUnit.setValue(item ? parseInt(item.get("value")) : 0);\r\n
            this._oldUnits = this.cmbUnit.getValue();\r\n
            value = window.localStorage.getItem("sse-settings-autosave");\r\n
            this.chAutosave.setValue(value === null || parseInt(value) == 1);\r\n
        },\r\n
        applySettings: function () {\r\n
            window.localStorage.setItem("sse-settings-zoom", this.cmbZoom.getValue());\r\n
            window.localStorage.setItem("sse-settings-livecomment", this.chLiveComment.isChecked() ? 1 : 0);\r\n
            window.localStorage.setItem("sse-settings-fontrender", this.cmbFontRender.getValue());\r\n
            window.localStorage.setItem("sse-settings-unit", this.cmbUnit.getValue());\r\n
            window.localStorage.setItem("sse-settings-autosave", this.chAutosave.isChecked() ? 1 : 0);\r\n
            if (this.menu) {\r\n
                this.menu.fireEvent("settings:apply", [this.menu]);\r\n
                if (this._oldUnits !== this.cmbUnit.getValue()) {\r\n
                    Common.NotificationCenter.trigger("settings:unitschanged", this);\r\n
                }\r\n
            }\r\n
        },\r\n
        strLiveComment: "Turn on option",\r\n
        strZoom: "Default Zoom Value",\r\n
        okButtonText: "Apply",\r\n
        txtLiveComment: "Live Commenting",\r\n
        txtWin: "as Windows",\r\n
        txtMac: "as OS X",\r\n
        txtNative: "Native",\r\n
        strFontRender: "Font Hinting",\r\n
        strUnit: "Unit of Measurement",\r\n
        txtCm: "Centimeter",\r\n
        txtPt: "Point",\r\n
        strAutosave: "Turn on autosave",\r\n
        textAutoSave: "Autosave"\r\n
    },\r\n
    SSE.Views.FileMenuPanels.MainSettingsGeneral || {}));\r\n
    SSE.Views.FileMenuPanels.RecentFiles = Common.UI.BaseView.extend({\r\n
        el: "#panel-recentfiles",\r\n
        menu: undefined,\r\n
        template: _.template([\'<div id="id-recent-view" style="margin: 20px 0;"></div>\'].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
            this.recent = options.recent;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.viewRecentPicker = new Common.UI.DataView({\r\n
                el: $("#id-recent-view"),\r\n
                store: new Common.UI.DataViewStore(this.recent),\r\n
                itemTemplate: _.template([\'<div class="recent-wrap">\', \'<div class="recent-icon"></div>\', \'<div class="file-name"><%= Common.Utils.String.htmlEncode(title) %></div>\', \'<div class="file-info"><%= Common.Utils.String.htmlEncode(folder) %></div>\', "</div>"].join(""))\r\n
            });\r\n
            this.viewRecentPicker.on("item:click", _.bind(this.onRecentFileClick, this));\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        onRecentFileClick: function (view, itemview, record) {\r\n
            if (this.menu) {\r\n
                this.menu.fireEvent("recent:open", [this.menu, record.get("url")]);\r\n
            }\r\n
        }\r\n
    });\r\n
    SSE.Views.FileMenuPanels.CreateNew = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#panel-createnew",\r\n
        menu: undefined,\r\n
        events: function () {\r\n
            return {\r\n
                "click .blank-document-btn": _.bind(this._onBlankDocument, this),\r\n
                "click .thumb-list .thumb-wrap": _.bind(this._onDocumentTemplate, this)\r\n
            };\r\n
        },\r\n
        template: _.template([\'<h3 style="margin-top: 20px;"><%= scope.fromBlankText %></h3><hr noshade />\', \'<div class="blank-document">\', \'<div class="blank-document-btn"></div>\', \'<div class="blank-document-info">\', "<h3><%= scope.newDocumentText %></h3>", "<%= scope.newDescriptionText %>", "</div>", "</div>", "<h3><%= scope.fromTemplateText %></h3><hr noshade />", \'<div class="thumb-list">\', "<% _.each(docs, function(item) { %>", \'<div class="thumb-wrap" template="<%= item.name %>">\', \'<div class="thumb"<% if (!_.isEmpty(item.icon)) { %> style="background-image: url(<%= item.icon %>);" <% } %> />\', \'<div class="title"><%= item.name %></div>\', "</div>", "<% }) %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template({\r\n
                scope: this,\r\n
                docs: this.options[0].docs\r\n
            }));\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        _onBlankDocument: function () {\r\n
            if (this.menu) {\r\n
                this.menu.fireEvent("create:new", [this.menu, "blank"]);\r\n
            }\r\n
        },\r\n
        _onDocumentTemplate: function (e) {\r\n
            if (this.menu) {\r\n
                this.menu.fireEvent("create:new", [this.menu, e.currentTarget.attributes["template"].value]);\r\n
            }\r\n
        },\r\n
        fromBlankText: "From Blank",\r\n
        newDocumentText: "New Spreadsheet",\r\n
        newDescriptionText: "Create a new blank text document which you will be able to style and format after it is created during the editing. Or choose one of the templates to start a document of a certain type or purpose where some styles have already been pre-applied.",\r\n
        fromTemplateText: "From Template"\r\n
    },\r\n
    SSE.Views.FileMenuPanels.CreateNew || {}));\r\n
    SSE.Views.FileMenuPanels.DocumentInfo = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#panel-info",\r\n
        menu: undefined,\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.rendered = false;\r\n
            this.template = _.template([\'<table class="main">\', "<tr>", \'<td class="left"><label>\' + this.txtTitle + "</label></td>", \'<td class="right"><label id="id-info-title">-</label></td>\', "</tr>", \'<tr class="author">\', \'<td class="left"><label>\' + this.txtAuthor + "</label></td>", \'<td class="right"><span class="userLink" id="id-info-author">-</span></td>\', "</tr>", \'<tr class="placement">\', \'<td class="left"><label>\' + this.txtPlacement + "</label></td>", \'<td class="right"><label id="id-info-placement">-</label></td>\', "</tr>", \'<tr class="date">\', \'<td class="left"><label>\' + this.txtDate + "</label></td>", \'<td class="right"><label id="id-info-date">-</label></td>\', "</tr>", \'<tr class="divider date"></tr>\', "</table>"].join(""));\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.lblTitle = $("#id-info-title");\r\n
            this.lblPlacement = $("#id-info-placement");\r\n
            this.lblDate = $("#id-info-date");\r\n
            this.lblAuthor = $("#id-info-author");\r\n
            this.rendered = true;\r\n
            this.updateInfo(this.doc);\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
        },\r\n
        hide: function () {\r\n
            Common.UI.BaseView.prototype.hide.call(this, arguments);\r\n
        },\r\n
        updateInfo: function (doc) {\r\n
            this.doc = doc;\r\n
            if (!this.rendered) {\r\n
                return;\r\n
            }\r\n
            doc = doc || {};\r\n
            this.lblTitle.text((doc.title) ? doc.title : "-");\r\n
            if (doc.info) {\r\n
                if (doc.info.author) {\r\n
                    this.lblAuthor.text(doc.info.author);\r\n
                }\r\n
                this._ShowHideInfoItem("author", doc.info.author !== undefined && doc.info.author !== null);\r\n
                if (doc.info.created) {\r\n
                    this.lblDate.text(doc.info.created);\r\n
                }\r\n
                this._ShowHideInfoItem("date", doc.info.created !== undefined && doc.info.created !== null);\r\n
                if (doc.info.folder) {\r\n
                    this.lblPlacement.text(doc.info.folder);\r\n
                }\r\n
                this._ShowHideInfoItem("placement", doc.info.folder !== undefined && doc.info.folder !== null);\r\n
            } else {\r\n
                this._ShowHideDocInfo(false);\r\n
            }\r\n
        },\r\n
        _ShowHideInfoItem: function (cls, visible) {\r\n
            $("tr." + cls, this.el)[visible ? "show" : "hide"]();\r\n
        },\r\n
        _ShowHideDocInfo: function (visible) {\r\n
            this._ShowHideInfoItem("date", visible);\r\n
            this._ShowHideInfoItem("placement", visible);\r\n
            this._ShowHideInfoItem("author", visible);\r\n
        },\r\n
        setMode: function (mode) {\r\n
            return this;\r\n
        },\r\n
        txtTitle: "Document Title",\r\n
        txtAuthor: "Author",\r\n
        txtPlacement: "Placement",\r\n
        txtDate: "Creation Date"\r\n
    },\r\n
    SSE.Views.FileMenuPanels.DocumentInfo || {}));\r\n
    SSE.Views.FileMenuPanels.DocumentRights = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#panel-rights",\r\n
        menu: undefined,\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.rendered = false;\r\n
            this.template = _.template([\'<table class="main">\', \'<tr class="rights">\', \'<td class="left" style="vertical-align: top;"><label>\' + this.txtRights + "</label></td>", \'<td class="right"><div id="id-info-rights"></div></td>\', "</tr>", \'<tr class="edit-rights">\', \'<td class="left"></td><td class="right"><button id="id-info-btn-edit" class="btn normal dlg-btn primary" style="margin-right: 10px;width: auto;">\' + this.txtBtnAccessRights + "</button></td>", "</tr>", "</table>"].join(""));\r\n
            this.templateRights = _.template(["<table>", "<% _.each(users, function(item) { %>", "<tr>", \'<td><span class="userLink"><%= Common.Utils.String.htmlEncode(item.user) %></span></td>\', "<td><%= Common.Utils.String.htmlEncode(item.permissions) %></td>", "</tr>", "<% }); %>", "</table>"].join(""));\r\n
            this.menu = options.menu;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.cntRights = $("#id-info-rights");\r\n
            this.btnEditRights = new Common.UI.Button({\r\n
                el: "#id-info-btn-edit"\r\n
            });\r\n
            this.btnEditRights.on("click", _.bind(this.changeAccessRights, this));\r\n
            this.rendered = true;\r\n
            this.updateInfo(this.doc);\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el),\r\n
                    suppressScrollX: true\r\n
                });\r\n
            }\r\n
            return this;\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this, arguments);\r\n
        },\r\n
        hide: function () {\r\n
            Common.UI.BaseView.prototype.hide.call(this, arguments);\r\n
        },\r\n
        updateInfo: function (doc) {\r\n
            this.doc = doc;\r\n
            if (!this.rendered) {\r\n
                return;\r\n
            }\r\n
            doc = doc || {};\r\n
            if (doc.info) {\r\n
                if (doc.info.sharingSettings) {\r\n
                    this.cntRights.html(this.templateRights({\r\n
                        users: doc.info.sharingSettings\r\n
                    }));\r\n
                }\r\n
                this._ShowHideInfoItem("rights", doc.info.sharingSettings !== undefined && doc.info.sharingSettings !== null && doc.info.sharingSettings.length > 0);\r\n
                this._ShowHideInfoItem("edit-rights", !!this.sharingSettingsUrl && this.sharingSettingsUrl.length && this._readonlyRights !== true);\r\n
            } else {\r\n
                this._ShowHideDocInfo(false);\r\n
            }\r\n
        },\r\n
        _ShowHideInfoItem: function (cls, visible) {\r\n
            $("tr." + cls, this.el)[visible ? "show" : "hide"]();\r\n
        },\r\n
        _ShowHideDocInfo: function (visible) {\r\n
            this._ShowHideInfoItem("rights", visible);\r\n
            this._ShowHideInfoItem("edit-rights", visible);\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.sharingSettingsUrl = mode.sharingSettingsUrl;\r\n
            return this;\r\n
        },\r\n
        changeAccessRights: function (btn, event, opts) {\r\n
            if (this._docAccessDlg) {\r\n
                return;\r\n
            }\r\n
            var me = this;\r\n
            me._docAccessDlg = new Common.Views.DocumentAccessDialog({\r\n
                settingsurl: this.sharingSettingsUrl\r\n
            });\r\n
            me._docAccessDlg.on("accessrights", function (obj, rights) {\r\n
                me.doc.info.sharingSettings = rights;\r\n
                me._ShowHideInfoItem("rights", me.doc.info.sharingSettings !== undefined && me.doc.info.sharingSettings !== null && me.doc.info.sharingSettings.length > 0);\r\n
                me.cntRights.html(me.templateRights({\r\n
                    users: me.doc.info.sharingSettings\r\n
                }));\r\n
            }).on("close", function (obj) {\r\n
                me._docAccessDlg = undefined;\r\n
            });\r\n
            me._docAccessDlg.show();\r\n
        },\r\n
        onLostEditRights: function () {\r\n
            this._readonlyRights = true;\r\n
            if (!this.rendered) {\r\n
                return;\r\n
            }\r\n
            this._ShowHideInfoItem("edit-rights", false);\r\n
        },\r\n
        txtRights: "Persons who have rights",\r\n
        txtBtnAccessRights: "Change access rights"\r\n
    },\r\n
    SSE.Views.FileMenuPanels.DocumentRights || {}));\r\n
    SSE.Views.FileMenuPanels.Help = Common.UI.BaseView.extend({\r\n
        el: "#panel-help",\r\n
        menu: undefined,\r\n
        template: _.template([\'<div style="width:100%; height:100%; position: relative;">\', \'<div id="id-help-contents" style="position: absolute; width:200px; top: 0; bottom: 0;" class="no-padding"></div>\', \'<div id="id-help-frame" style="position: absolute; left: 200px; top: 0; right: 0; bottom: 0;" class="no-padding"></div>\', "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, arguments);\r\n
            this.menu = options.menu;\r\n
            this.urlPref = "resources/help/en/";\r\n
            this.itemclicked = false;\r\n
            this.en_data = [{\r\n
                src: "UsageInstructions/OpenCreateNew.htm",\r\n
                name: "Create a new spreadsheet or open an existing one",\r\n
                headername: "Usage Instructions",\r\n
                selected: true\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/ManageSheets.htm",\r\n
                name: "Manage sheets"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/InsertDeleteCells.htm",\r\n
                name: "Insert or delete cells, rows, and columns"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/CopyPasteData.htm",\r\n
                name: "Copy and paste data"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/FontTypeSizeStyle.htm",\r\n
                name: "Set font type, size, style, and colors"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/AlignText.htm",\r\n
                name: "Align data in cells"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/AddBorders.htm",\r\n
                name: "Add borders"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/MergeCells.htm",\r\n
                name: "Merge cells"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/ClearFormatting.htm",\r\n
                name: "Clear text, format in a cell"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/SortData.htm",\r\n
                name: "Sort data"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/InsertFunction.htm",\r\n
                name: "Insert function"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/ChangeNumberFormat.htm",\r\n
                name: "Change number format"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/UndoRedo.htm",\r\n
                name: "Undo/redo your actions"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/ViewDocInfo.htm",\r\n
                name: "View file information"\r\n
            },\r\n
            {\r\n
                src: "UsageInstructions/SavePrintDownload.htm",\r\n
                name: "Save/print/download your spreadsheet"\r\n
            },\r\n
            {\r\n
                src: "HelpfulHints/About.htm",\r\n
                name: "About ONLYOFFICE Spreadsheet Editor",\r\n
                headername: "Helpful Hints"\r\n
            },\r\n
            {\r\n
                src: "HelpfulHints/SupportedFormats.htm",\r\n
                name: "Supported Formats of Spreadsheets"\r\n
            },\r\n
            {\r\n
                src: "HelpfulHints/Navigation.htm",\r\n
                name: "Navigation through Your Spreadsheet"\r\n
            },\r\n
            {\r\n
                src: "HelpfulHints/Search.htm",\r\n
                name: "Search Function"\r\n
            },\r\n
            {\r\n
                src: "HelpfulHints/KeyboardShortcuts.htm",\r\n
                name: "Keyboard Shortcuts"\r\n
            }];\r\n
            if (Common.Utils.isIE) {\r\n
                window.onhelp = function () {\r\n
                    return false;\r\n
                };\r\n
            }\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.viewHelpPicker = new Common.UI.DataView({\r\n
                el: $("#id-help-contents"),\r\n
                store: new Common.UI.DataViewStore([]),\r\n
                keyMoveDirection: "vertical",\r\n
                itemTemplate: _.template([\'<div id="<%= id %>" class="help-item-wrap">\', \'<div class="caption"><%= name %></div>\', "</div>"].join(""))\r\n
            });\r\n
            this.viewHelpPicker.on("item:add", _.bind(function (dataview, itemview, record) {\r\n
                if (record.has("headername")) {\r\n
                    $(itemview.el).before(\'<div class="header-name">\' + record.get("headername") + "</div>");\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.viewHelpPicker.on("item:select", _.bind(function (dataview, itemview, record) {\r\n
                this.itemclicked = true;\r\n
                this.iFrame.src = this.urlPref + record.get("src");\r\n
            },\r\n
            this));\r\n
            this.iFrame = document.createElement("iframe");\r\n
            this.iFrame.src = "";\r\n
            this.iFrame.align = "top";\r\n
            this.iFrame.frameBorder = "0";\r\n
            this.iFrame.width = "100%";\r\n
            this.iFrame.height = "100%";\r\n
            this.iFrame.onload = _.bind(function () {\r\n
                if (!this.itemclicked) {\r\n
                    var src = arguments[0].currentTarget.contentDocument.URL;\r\n
                    var rec = this.viewHelpPicker.store.find(function (record) {\r\n
                        return (src.indexOf(record.get("src")) > 0);\r\n
                    });\r\n
                    if (rec) {\r\n
                        this.viewHelpPicker.selectRecord(rec, true);\r\n
                        this.viewHelpPicker.scrollToRecord(rec);\r\n
                    }\r\n
                }\r\n
                this.itemclicked = false;\r\n
            },\r\n
            this);\r\n
            $("#id-help-frame").append(this.iFrame);\r\n
            return this;\r\n
        },\r\n
        setLangConfig: function (lang) {\r\n
            var me = this;\r\n
            var store = this.viewHelpPicker.store;\r\n
            if (lang) {\r\n
                lang = lang.split("-")[0];\r\n
                var config = {\r\n
                    dataType: "json",\r\n
                    error: function () {\r\n
                        if (me.urlPref.indexOf("resources/help/en/") < 0) {\r\n
                            me.urlPref = "resources/help/en/";\r\n
                            store.url = "resources/help/en/Contents.json";\r\n
                            store.fetch(config);\r\n
                        } else {\r\n
                            me.urlPref = "resources/help/en/";\r\n
                            store.reset(me.en_data);\r\n
                        }\r\n
                    },\r\n
                    success: function () {\r\n
                        var rec = store.at(0);\r\n
                        me.viewHelpPicker.selectRecord(rec);\r\n
                        me.iFrame.src = me.urlPref + rec.get("src");\r\n
                    }\r\n
                };\r\n
                store.url = "resources/help/" + lang + "/Contents.json";\r\n
                store.fetch(config);\r\n
                this.urlPref = "resources/help/" + lang + "/";\r\n
            }\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.BaseView.prototype.show.call(this);\r\n
            if (!this._scrollerInited) {\r\n
                this.viewHelpPicker.scroller.update();\r\n
                this._scrollerInited = true;\r\n
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
            <value> <int>44536</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
