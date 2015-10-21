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
            <value> <string>ts44321338.05</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ChartSettingsDlg.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/ChartSettingsDlg.template", "common/main/lib/view/AdvancedSettingsWindow", "common/main/lib/component/CheckBox", "common/main/lib/component/InputField", "spreadsheeteditor/main/app/view/CellRangeDialog"], function (contentTemplate) {\r\n
    SSE.Views.ChartSettingsDlg = Common.Views.AdvancedSettingsWindow.extend(_.extend({\r\n
        options: {\r\n
            contentWidth: 320,\r\n
            height: 535,\r\n
            toggleGroup: "chart-settings-dlg-group"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle,\r\n
                items: [{\r\n
                    panelId: "id-chart-settings-dlg-style",\r\n
                    panelCaption: this.textTypeData\r\n
                },\r\n
                {\r\n
                    panelId: "id-chart-settings-dlg-layout",\r\n
                    panelCaption: this.textLayout\r\n
                },\r\n
                {\r\n
                    panelId: "id-chart-settings-dlg-vert",\r\n
                    panelCaption: this.textVertAxis\r\n
                },\r\n
                {\r\n
                    panelId: "id-chart-settings-dlg-hor",\r\n
                    panelCaption: this.textHorAxis\r\n
                }],\r\n
                contentTemplate: _.template(contentTemplate)({\r\n
                    scope: this\r\n
                })\r\n
            },\r\n
            options);\r\n
            this.options.handler = function (result, value) {\r\n
                if (result != "ok" || this.isRangeValid()) {\r\n
                    if (options.handler) {\r\n
                        options.handler.call(this, result, value);\r\n
                    }\r\n
                    return;\r\n
                }\r\n
                return true;\r\n
            };\r\n
            Common.Views.AdvancedSettingsWindow.prototype.initialize.call(this, this.options);\r\n
            this._state = {\r\n
                ChartStyle: 1,\r\n
                ChartType: c_oAscChartTypeSettings.barNormal\r\n
            };\r\n
            this._noApply = true;\r\n
            this.api = this.options.api;\r\n
            this.chartSettings = this.options.chartSettings;\r\n
            this.vertAxisProps = null;\r\n
            this.horAxisProps = null;\r\n
            this.currentAxisProps = null;\r\n
            this.dataRangeValid = "";\r\n
        },\r\n
        render: function () {\r\n
            Common.Views.AdvancedSettingsWindow.prototype.render.call(this);\r\n
            var me = this;\r\n
            var $window = this.getChild();\r\n
            this.btnChartType = new Common.UI.Button({\r\n
                cls: "btn-large-dataview",\r\n
                iconCls: "item-chartlist bar-normal",\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "width: 330px;",\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-chart-dlg-menu-type" class="menu-insertchart"  style="margin: 5px 5px 5px 10px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnChartType.on("render:after", function (btn) {\r\n
                me.mnuChartTypePicker = new Common.UI.DataView({\r\n
                    el: $("#id-chart-dlg-menu-type"),\r\n
                    parentMenu: btn.menu,\r\n
                    restoreHeight: 411,\r\n
                    groups: new Common.UI.DataViewGroupStore([{\r\n
                        id: "menu-chart-group-bar",\r\n
                        caption: me.textColumn\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-line",\r\n
                        caption: me.textLine\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-pie",\r\n
                        caption: me.textPie\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-hbar",\r\n
                        caption: me.textBar\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-area",\r\n
                        caption: me.textArea\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-scatter",\r\n
                        caption: me.textPoint\r\n
                    },\r\n
                    {\r\n
                        id: "menu-chart-group-stock",\r\n
                        caption: me.textStock\r\n
                    }]),\r\n
                    store: new Common.UI.DataViewStore([{\r\n
                        group: "menu-chart-group-bar",\r\n
                        type: c_oAscChartTypeSettings.barNormal,\r\n
                        iconCls: "column-normal",\r\n
                        selected: true\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-bar",\r\n
                        type: c_oAscChartTypeSettings.barStacked,\r\n
                        iconCls: "column-stack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-bar",\r\n
                        type: c_oAscChartTypeSettings.barStackedPer,\r\n
                        iconCls: "column-pstack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-line",\r\n
                        type: c_oAscChartTypeSettings.lineNormal,\r\n
                        iconCls: "line-normal"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-line",\r\n
                        type: c_oAscChartTypeSettings.lineStacked,\r\n
                        iconCls: "line-stack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-line",\r\n
                        type: c_oAscChartTypeSettings.lineStackedPer,\r\n
                        iconCls: "line-pstack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-pie",\r\n
                        type: c_oAscChartTypeSettings.pie,\r\n
                        iconCls: "pie-normal"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-pie",\r\n
                        type: c_oAscChartTypeSettings.doughnut,\r\n
                        iconCls: "pie-doughnut"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-hbar",\r\n
                        type: c_oAscChartTypeSettings.hBarNormal,\r\n
                        iconCls: "bar-normal"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-hbar",\r\n
                        type: c_oAscChartTypeSettings.hBarStacked,\r\n
                        iconCls: "bar-stack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-hbar",\r\n
                        type: c_oAscChartTypeSettings.hBarStackedPer,\r\n
                        iconCls: "bar-pstack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-area",\r\n
                        type: c_oAscChartTypeSettings.areaNormal,\r\n
                        iconCls: "area-normal"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-area",\r\n
                        type: c_oAscChartTypeSettings.areaStacked,\r\n
                        iconCls: "area-stack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-area",\r\n
                        type: c_oAscChartTypeSettings.areaStackedPer,\r\n
                        iconCls: "area-pstack"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-scatter",\r\n
                        type: c_oAscChartTypeSettings.scatter,\r\n
                        iconCls: "point-normal"\r\n
                    },\r\n
                    {\r\n
                        group: "menu-chart-group-stock",\r\n
                        type: c_oAscChartTypeSettings.stock,\r\n
                        iconCls: "stock-normal"\r\n
                    }]),\r\n
                    itemTemplate: _.template(\'<div id="<%= id %>" class="item-chartlist <%= iconCls %>"></div>\')\r\n
                });\r\n
            });\r\n
            this.btnChartType.render($("#chart-dlg-button-type"));\r\n
            this.mnuChartTypePicker.on("item:click", _.bind(this.onSelectType, this, this.btnChartType));\r\n
            this.btnChartStyle = new Common.UI.Button({\r\n
                cls: "btn-large-dataview",\r\n
                iconCls: "item-wrap",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-chart-dlg-menu-style" style="width: 245px; margin: 0 5px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnChartStyle.on("render:after", function (btn) {\r\n
                me.mnuChartStylePicker = new Common.UI.DataView({\r\n
                    el: $("#id-chart-dlg-menu-style"),\r\n
                    parentMenu: btn.menu,\r\n
                    style: "max-height: 411px;",\r\n
                    store: new Common.UI.DataViewStore(),\r\n
                    itemTemplate: _.template(\'<div id="<%= id %>" class="item-wrap" style="background-image: url(<%= imageUrl %>); background-position: 0 0;"></div>\')\r\n
                });\r\n
                if (me.btnChartStyle.menu) {\r\n
                    me.btnChartStyle.menu.on("show:after", function () {\r\n
                        me.mnuChartStylePicker.scroller.update({\r\n
                            alwaysVisibleY: true\r\n
                        });\r\n
                    });\r\n
                }\r\n
            });\r\n
            this.btnChartStyle.render($("#chart-dlg-button-style"));\r\n
            this.mnuChartStylePicker.on("item:click", _.bind(this.onSelectStyle, this, this.btnChartStyle));\r\n
            this.cmbDataDirect = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-range"),\r\n
                menuStyle: "min-width: 120px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: 0,\r\n
                    displayValue: this.textDataRows\r\n
                },\r\n
                {\r\n
                    value: 1,\r\n
                    displayValue: this.textDataColumns\r\n
                }]\r\n
            });\r\n
            this.txtDataRange = new Common.UI.InputField({\r\n
                el: $("#chart-dlg-txt-range"),\r\n
                name: "range",\r\n
                style: "width: 100%;",\r\n
                allowBlank: true,\r\n
                blankError: this.txtEmpty,\r\n
                validateOnChange: true\r\n
            });\r\n
            this.btnSelectData = new Common.UI.Button({\r\n
                el: $("#chart-dlg-btn-data")\r\n
            });\r\n
            this.btnSelectData.on("click", _.bind(this.onSelectData, this));\r\n
            this.cmbChartTitle = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-chart-title"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscChartTitleShowSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartTitleShowSettings.overlay,\r\n
                    displayValue: this.textOverlay\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartTitleShowSettings.noOverlay,\r\n
                    displayValue: this.textNoOverlay\r\n
                }]\r\n
            });\r\n
            this.cmbLegendPos = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-legend-pos"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscChartLegendShowSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.bottom,\r\n
                    displayValue: this.textLegendBottom\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.top,\r\n
                    displayValue: this.textLegendTop\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.right,\r\n
                    displayValue: this.textLegendRight\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.left,\r\n
                    displayValue: this.textLegendLeft\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.leftOverlay,\r\n
                    displayValue: this.textLeftOverlay\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartLegendShowSettings.rightOverlay,\r\n
                    displayValue: this.textRightOverlay\r\n
                }]\r\n
            });\r\n
            this.cmbHorTitle = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-hor-title"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscChartHorAxisLabelShowSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartHorAxisLabelShowSettings.noOverlay,\r\n
                    displayValue: this.textNoOverlay\r\n
                }]\r\n
            });\r\n
            this.cmbVertTitle = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-vert-title"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscChartVertAxisLabelShowSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartVertAxisLabelShowSettings.rotated,\r\n
                    displayValue: this.textRotated\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartVertAxisLabelShowSettings.horizontal,\r\n
                    displayValue: this.textHorizontal\r\n
                }]\r\n
            });\r\n
            this.cmbHorGrid = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-hor-grid"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscGridLinesSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.major,\r\n
                    displayValue: this.textMajor\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.minor,\r\n
                    displayValue: this.textMinor\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.majorMinor,\r\n
                    displayValue: this.textMajorMinor\r\n
                }]\r\n
            });\r\n
            this.cmbVertGrid = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-vert-grid"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscGridLinesSettings.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.major,\r\n
                    displayValue: this.textMajor\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.minor,\r\n
                    displayValue: this.textMinor\r\n
                },\r\n
                {\r\n
                    value: c_oAscGridLinesSettings.majorMinor,\r\n
                    displayValue: this.textMajorMinor\r\n
                }]\r\n
            });\r\n
            this.cmbDataLabels = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-data-labels"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: c_oAscChartDataLabelsPos.none,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartDataLabelsPos.ctr,\r\n
                    displayValue: this.textCenter\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartDataLabelsPos.inBase,\r\n
                    displayValue: this.textInnerBottom\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartDataLabelsPos.inEnd,\r\n
                    displayValue: this.textInnerTop\r\n
                },\r\n
                {\r\n
                    value: c_oAscChartDataLabelsPos.outEnd,\r\n
                    displayValue: this.textOuterTop\r\n
                }]\r\n
            });\r\n
            this.cmbDataLabels.on("selected", _.bind(me.onSelectDataLabels, this));\r\n
            this.txtSeparator = new Common.UI.InputField({\r\n
                el: $("#chart-dlg-txt-separator"),\r\n
                name: "range",\r\n
                style: "width: 100%;",\r\n
                allowBlank: true,\r\n
                blankError: this.txtEmpty\r\n
            });\r\n
            this.chSeriesName = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-series"),\r\n
                labelText: this.textSeriesName\r\n
            });\r\n
            this.chCategoryName = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-category"),\r\n
                labelText: this.textCategoryName\r\n
            });\r\n
            this.chValue = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-value"),\r\n
                labelText: this.textValue\r\n
            });\r\n
            this.cmbLines = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-lines"),\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                cls: "input-group-nr",\r\n
                data: [{\r\n
                    value: 0,\r\n
                    displayValue: this.textNone\r\n
                },\r\n
                {\r\n
                    value: 1,\r\n
                    displayValue: this.textStraight\r\n
                },\r\n
                {\r\n
                    value: 2,\r\n
                    displayValue: this.textSmooth\r\n
                }]\r\n
            });\r\n
            this.chMarkers = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-markers"),\r\n
                labelText: this.textMarkers\r\n
            });\r\n
            this.lblLines = $("#chart-dlg-label-lines");\r\n
            this.cmbMinType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-mintype"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textAuto,\r\n
                    value: c_oAscValAxisRule.auto\r\n
                },\r\n
                {\r\n
                    displayValue: this.textFixed,\r\n
                    value: c_oAscValAxisRule.fixed\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMinValRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnMinValue = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-min-value"),\r\n
                maxValue: 1000000,\r\n
                minValue: -1000000,\r\n
                step: 0.1,\r\n
                defaultUnit: "",\r\n
                defaultValue: 0,\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                this.cmbMinType.suspendEvents();\r\n
                this.cmbMinType.setValue(c_oAscValAxisRule.fixed);\r\n
                this.cmbMinType.resumeEvents();\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMinValRule(c_oAscValAxisRule.fixed);\r\n
                    this.currentAxisProps.putMinVal(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbMaxType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-maxtype"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textAuto,\r\n
                    value: c_oAscValAxisRule.auto\r\n
                },\r\n
                {\r\n
                    displayValue: this.textFixed,\r\n
                    value: c_oAscValAxisRule.fixed\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMaxValRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnMaxValue = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-max-value"),\r\n
                maxValue: 1000000,\r\n
                minValue: -1000000,\r\n
                step: 0.1,\r\n
                defaultUnit: "",\r\n
                defaultValue: 0,\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                this.cmbMaxType.suspendEvents();\r\n
                this.cmbMaxType.setValue(c_oAscValAxisRule.fixed);\r\n
                this.cmbMaxType.resumeEvents();\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMaxValRule(c_oAscValAxisRule.fixed);\r\n
                    this.currentAxisProps.putMaxVal(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbVCrossType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-v-crosstype"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textAuto,\r\n
                    value: c_oAscCrossesRule.auto\r\n
                },\r\n
                {\r\n
                    displayValue: this.textValue,\r\n
                    value: c_oAscCrossesRule.value\r\n
                },\r\n
                {\r\n
                    displayValue: this.textMinValue,\r\n
                    value: c_oAscCrossesRule.minValue\r\n
                },\r\n
                {\r\n
                    displayValue: this.textMaxValue,\r\n
                    value: c_oAscCrossesRule.maxValue\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putCrossesRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnVAxisCrosses = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-v-axis-crosses"),\r\n
                maxValue: 1000000,\r\n
                minValue: -1000000,\r\n
                step: 0.1,\r\n
                defaultUnit: "",\r\n
                defaultValue: 0,\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                this.cmbVCrossType.suspendEvents();\r\n
                this.cmbVCrossType.setValue(c_oAscCrossesRule.value);\r\n
                this.cmbVCrossType.resumeEvents();\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putCrossesRule(c_oAscCrossesRule.value);\r\n
                    this.currentAxisProps.putCrosses(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbUnits = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-units"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscValAxUnits.none\r\n
                },\r\n
                {\r\n
                    displayValue: this.textHundreds,\r\n
                    value: c_oAscValAxUnits.HUNDREDS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textThousands,\r\n
                    value: c_oAscValAxUnits.THOUSANDS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textTenThousands,\r\n
                    value: c_oAscValAxUnits.TEN_THOUSANDS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textHundredThousands,\r\n
                    value: c_oAscValAxUnits.HUNDRED_THOUSANDS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textMillions,\r\n
                    value: c_oAscValAxUnits.MILLIONS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textTenMillions,\r\n
                    value: c_oAscValAxUnits.TEN_MILLIONS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textHundredMil,\r\n
                    value: c_oAscValAxUnits.HUNDRED_MILLIONS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textBillions,\r\n
                    value: c_oAscValAxUnits.BILLIONS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textTrillions,\r\n
                    value: c_oAscValAxUnits.TRILLIONS\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putDispUnitsRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.chVReverse = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-v-reverse"),\r\n
                labelText: this.textReverse\r\n
            }).on("change", _.bind(function (checkbox, state) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putInvertValOrder(state == "checked");\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbVMajorType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-v-major-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickMark.TICK_MARK_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textCross,\r\n
                    value: c_oAscTickMark.TICK_MARK_CROSS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textIn,\r\n
                    value: c_oAscTickMark.TICK_MARK_IN\r\n
                },\r\n
                {\r\n
                    displayValue: this.textOut,\r\n
                    value: c_oAscTickMark.TICK_MARK_OUT\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMajorTickMark(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbVMinorType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-v-minor-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickMark.TICK_MARK_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textCross,\r\n
                    value: c_oAscTickMark.TICK_MARK_CROSS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textIn,\r\n
                    value: c_oAscTickMark.TICK_MARK_IN\r\n
                },\r\n
                {\r\n
                    displayValue: this.textOut,\r\n
                    value: c_oAscTickMark.TICK_MARK_OUT\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMinorTickMark(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbVLabelPos = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-v-label-pos"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textLow,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_LOW\r\n
                },\r\n
                {\r\n
                    displayValue: this.textHigh,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_HIGH\r\n
                },\r\n
                {\r\n
                    displayValue: this.textNextToAxis,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_NEXT_TO\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putTickLabelsPos(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbHCrossType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-h-crosstype"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textAuto,\r\n
                    value: c_oAscCrossesRule.auto\r\n
                },\r\n
                {\r\n
                    displayValue: this.textValue,\r\n
                    value: c_oAscCrossesRule.value\r\n
                },\r\n
                {\r\n
                    displayValue: this.textMinValue,\r\n
                    value: c_oAscCrossesRule.minValue\r\n
                },\r\n
                {\r\n
                    displayValue: this.textMaxValue,\r\n
                    value: c_oAscCrossesRule.maxValue\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putCrossesRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnHAxisCrosses = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-h-axis-crosses"),\r\n
                maxValue: 1000000,\r\n
                minValue: -1000000,\r\n
                step: 0.1,\r\n
                defaultUnit: "",\r\n
                defaultValue: 0,\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                this.cmbHCrossType.suspendEvents();\r\n
                this.cmbHCrossType.setValue(c_oAscCrossesRule.value);\r\n
                this.cmbHCrossType.resumeEvents();\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putCrossesRule(c_oAscCrossesRule.value);\r\n
                    this.currentAxisProps.putCrosses(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbAxisPos = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-axis-pos"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textOnTickMarks,\r\n
                    value: c_oAscLabelsPosition.byDivisions\r\n
                },\r\n
                {\r\n
                    displayValue: this.textBetweenTickMarks,\r\n
                    value: c_oAscLabelsPosition.betweenDivisions\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putLabelsPosition(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.chHReverse = new Common.UI.CheckBox({\r\n
                el: $("#chart-dlg-check-h-reverse"),\r\n
                labelText: this.textReverse\r\n
            }).on("change", _.bind(function (checkbox, state) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putInvertCatOrder(state == "checked");\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbHMajorType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-h-major-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickMark.TICK_MARK_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textCross,\r\n
                    value: c_oAscTickMark.TICK_MARK_CROSS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textIn,\r\n
                    value: c_oAscTickMark.TICK_MARK_IN\r\n
                },\r\n
                {\r\n
                    displayValue: this.textOut,\r\n
                    value: c_oAscTickMark.TICK_MARK_OUT\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMajorTickMark(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbHMinorType = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-h-minor-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickMark.TICK_MARK_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textCross,\r\n
                    value: c_oAscTickMark.TICK_MARK_CROSS\r\n
                },\r\n
                {\r\n
                    displayValue: this.textIn,\r\n
                    value: c_oAscTickMark.TICK_MARK_IN\r\n
                },\r\n
                {\r\n
                    displayValue: this.textOut,\r\n
                    value: c_oAscTickMark.TICK_MARK_OUT\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putMinorTickMark(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnMarksInterval = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-marks-interval"),\r\n
                width: 140,\r\n
                maxValue: 1000000,\r\n
                minValue: 1,\r\n
                step: 1,\r\n
                defaultUnit: "",\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putIntervalBetweenTick(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbHLabelPos = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-h-label-pos"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textNone,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_NONE\r\n
                },\r\n
                {\r\n
                    displayValue: this.textLow,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_LOW\r\n
                },\r\n
                {\r\n
                    displayValue: this.textHigh,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_HIGH\r\n
                },\r\n
                {\r\n
                    displayValue: this.textNextToAxis,\r\n
                    value: c_oAscTickLabelsPos.TICK_LABEL_POSITION_NEXT_TO\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putTickLabelsPos(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnLabelDist = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-label-dist"),\r\n
                width: 140,\r\n
                maxValue: 1000,\r\n
                minValue: 0,\r\n
                step: 1,\r\n
                defaultUnit: "",\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putLabelsAxisDistance(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnLabelInterval = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-dlg-input-label-int"),\r\n
                width: 140,\r\n
                maxValue: 1000000,\r\n
                minValue: 1,\r\n
                step: 1,\r\n
                defaultUnit: "",\r\n
                value: ""\r\n
            }).on("change", _.bind(function (field, newValue, oldValue) {\r\n
                this.cmbLabelInterval.suspendEvents();\r\n
                this.cmbLabelInterval.setValue(c_oAscBetweenLabelsRule.manual);\r\n
                this.cmbLabelInterval.resumeEvents();\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putIntervalBetweenLabelsRule(c_oAscBetweenLabelsRule.manual);\r\n
                    this.currentAxisProps.putIntervalBetweenLabels(field.getNumberValue());\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.cmbLabelInterval = new Common.UI.ComboBox({\r\n
                el: $("#chart-dlg-combo-label-int"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 140px;",\r\n
                editable: false,\r\n
                data: [{\r\n
                    displayValue: this.textAuto,\r\n
                    value: c_oAscBetweenLabelsRule.auto\r\n
                },\r\n
                {\r\n
                    displayValue: this.textManual,\r\n
                    value: c_oAscBetweenLabelsRule.manual\r\n
                }]\r\n
            }).on("selected", _.bind(function (combo, record) {\r\n
                if (this.currentAxisProps) {\r\n
                    this.currentAxisProps.putIntervalBetweenLabelsRule(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.btnsCategory[2].on("click", _.bind(this.onVCategoryClick, this));\r\n
            this.btnsCategory[3].on("click", _.bind(this.onHCategoryClick, this));\r\n
            this.afterRender();\r\n
        },\r\n
        afterRender: function () {\r\n
            if (this.api) {\r\n
                this.updateChartStyles(this.api.asc_getChartPreviews(this._state.ChartType));\r\n
            }\r\n
            this._setDefaults(this.chartSettings);\r\n
        },\r\n
        onSelectType: function (btn, picker, itemView, record) {\r\n
            if (this._noApply) {\r\n
                return;\r\n
            }\r\n
            var rawData = {},\r\n
            isPickerSelect = _.isFunction(record.toJSON);\r\n
            if (isPickerSelect) {\r\n
                if (record.get("selected")) {\r\n
                    rawData = record.toJSON();\r\n
                } else {\r\n
                    return;\r\n
                }\r\n
            } else {\r\n
                rawData = record;\r\n
            }\r\n
            this.btnChartType.setIconCls("item-chartlist " + rawData.iconCls);\r\n
            this.updateChartStyles(this.api.asc_getChartPreviews(rawData.type));\r\n
            this.updateAxisProps(rawData.type, true);\r\n
            this.chartSettings.changeType(rawData.type);\r\n
            this.vertAxisProps = this.chartSettings.getVertAxisProps();\r\n
            this.horAxisProps = this.chartSettings.getHorAxisProps();\r\n
        },\r\n
        updateAxisProps: function (type, isDefault) {\r\n
            var value = (type == c_oAscChartTypeSettings.lineNormal || type == c_oAscChartTypeSettings.lineStacked || type == c_oAscChartTypeSettings.lineStackedPer || type == c_oAscChartTypeSettings.scatter);\r\n
            this.chMarkers.setVisible(value);\r\n
            this.cmbLines.setVisible(value);\r\n
            this.lblLines.toggleClass("hidden", !value);\r\n
            value = (type == c_oAscChartTypeSettings.pie || type == c_oAscChartTypeSettings.doughnut);\r\n
            this.btnsCategory[2].setDisabled(value);\r\n
            this.btnsCategory[3].setDisabled(value);\r\n
            this.cmbHorTitle.setDisabled(value);\r\n
            this.cmbVertTitle.setDisabled(value);\r\n
            this.cmbHorGrid.setDisabled(value);\r\n
            this.cmbVertGrid.setDisabled(value);\r\n
            value = (type == c_oAscChartTypeSettings.hBarNormal || type == c_oAscChartTypeSettings.hBarStacked || type == c_oAscChartTypeSettings.hBarStackedPer);\r\n
            this.btnsCategory[2].options.contentTarget = (value) ? "id-chart-settings-dlg-hor" : "id-chart-settings-dlg-vert";\r\n
            this.btnsCategory[3].options.contentTarget = (value || type == c_oAscChartTypeSettings.scatter) ? "id-chart-settings-dlg-vert" : "id-chart-settings-dlg-hor";\r\n
            if (isDefault) {\r\n
                if (value) {\r\n
                    this.cmbHorGrid.setValue(c_oAscGridLinesSettings.none);\r\n
                    this.cmbVertGrid.setValue(c_oAscGridLinesSettings.major);\r\n
                } else {\r\n
                    if (type == c_oAscChartTypeSettings.scatter) {\r\n
                        this.cmbHorGrid.setValue(c_oAscGridLinesSettings.major);\r\n
                        this.cmbVertGrid.setValue(c_oAscGridLinesSettings.major);\r\n
                        this.chMarkers.setValue(true, true);\r\n
                        this.cmbLines.setValue(0);\r\n
                    } else {\r\n
                        if (type == c_oAscChartTypeSettings.barNormal || type == c_oAscChartTypeSettings.barStacked || type == c_oAscChartTypeSettings.barStackedPer || type == c_oAscChartTypeSettings.lineNormal || type == c_oAscChartTypeSettings.lineStacked || type == c_oAscChartTypeSettings.lineStackedPer || type == c_oAscChartTypeSettings.areaNormal || type == c_oAscChartTypeSettings.areaStacked || type == c_oAscChartTypeSettings.areaStackedPer || type == c_oAscChartTypeSettings.stock) {\r\n
                            this.cmbHorGrid.setValue(c_oAscGridLinesSettings.major);\r\n
                            this.cmbVertGrid.setValue(c_oAscGridLinesSettings.none);\r\n
                            if (type == c_oAscChartTypeSettings.lineNormal || type == c_oAscChartTypeSettings.lineStacked || type == c_oAscChartTypeSettings.lineStackedPer) {\r\n
                                this.chMarkers.setValue(false, true);\r\n
                                this.cmbLines.setValue(1);\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onVCategoryClick: function () {\r\n
            (this.vertAxisProps.getAxisType() == c_oAscAxisType.val) ? this.fillVProps(this.vertAxisProps) : this.fillHProps(this.vertAxisProps);\r\n
        },\r\n
        onHCategoryClick: function () {\r\n
            (this.horAxisProps.getAxisType() == c_oAscAxisType.val) ? this.fillVProps(this.horAxisProps) : this.fillHProps(this.horAxisProps);\r\n
        },\r\n
        fillVProps: function (props) {\r\n
            if (props.getAxisType() !== c_oAscAxisType.val) {\r\n
                return;\r\n
            }\r\n
            var value = props.getMinValRule();\r\n
            this.cmbMinType.setValue(value);\r\n
            this.spnMinValue.setValue((value === c_oAscValAxisRule.fixed) ? props.getMinVal() : "", true);\r\n
            value = props.getMaxValRule();\r\n
            this.cmbMaxType.setValue(value);\r\n
            this.spnMaxValue.setValue((value === c_oAscValAxisRule.fixed) ? props.getMaxVal() : "", true);\r\n
            value = props.getCrossesRule();\r\n
            this.cmbVCrossType.setValue(value);\r\n
            this.spnVAxisCrosses.setValue((value === c_oAscCrossesRule.value) ? props.getCrosses() : "", true);\r\n
            this.cmbUnits.setValue(props.getDispUnitsRule());\r\n
            this.chVReverse.setValue(props.getInvertValOrder(), true);\r\n
            this.cmbVMajorType.setValue(props.getMajorTickMark());\r\n
            this.cmbVMinorType.setValue(props.getMinorTickMark());\r\n
            this.cmbVLabelPos.setValue(props.getTickLabelsPos());\r\n
            this.currentAxisProps = props;\r\n
        },\r\n
        fillHProps: function (props) {\r\n
            if (props.getAxisType() !== c_oAscAxisType.cat) {\r\n
                return;\r\n
            }\r\n
            var value = props.getCrossesRule();\r\n
            this.cmbHCrossType.setValue(value);\r\n
            this.spnHAxisCrosses.setValue((value === c_oAscCrossesRule.value) ? props.getCrosses() : "", true);\r\n
            this.cmbAxisPos.setValue(props.getLabelsPosition());\r\n
            this.chHReverse.setValue(props.getInvertCatOrder(), true);\r\n
            this.cmbHMajorType.setValue(props.getMajorTickMark());\r\n
            this.cmbHMinorType.setValue(props.getMinorTickMark());\r\n
            this.spnMarksInterval.setValue(props.getIntervalBetweenTick(), true);\r\n
            this.cmbHLabelPos.setValue(props.getTickLabelsPos());\r\n
            this.spnLabelDist.setValue(props.getLabelsAxisDistance(), true);\r\n
            value = props.getIntervalBetweenLabelsRule();\r\n
            this.cmbLabelInterval.setValue(value);\r\n
            this.spnLabelInterval.setValue((value === c_oAscBetweenLabelsRule.manual) ? props.getIntervalBetweenLabels() : "", true);\r\n
            this.currentAxisProps = props;\r\n
        },\r\n
        onSelectStyle: function (btn, picker, itemView, record) {\r\n
            if (this._noApply) {\r\n
                return;\r\n
            }\r\n
            var rawData = {},\r\n
            isPickerSelect = _.isFunction(record.toJSON);\r\n
            if (isPickerSelect) {\r\n
                if (record.get("selected")) {\r\n
                    rawData = record.toJSON();\r\n
                } else {\r\n
                    return;\r\n
                }\r\n
            } else {\r\n
                rawData = record;\r\n
            }\r\n
            var style = "url(" + rawData.imageUrl + ")";\r\n
            var btnIconEl = this.btnChartStyle.cmpEl.find("span.btn-icon");\r\n
            btnIconEl.css("background-image", style);\r\n
            this._state.ChartStyle = rawData.data;\r\n
        },\r\n
        updateChartStyles: function (styles) {\r\n
            var me = this;\r\n
            if (styles && styles.length > 0) {\r\n
                var stylesStore = this.mnuChartStylePicker.store;\r\n
                if (stylesStore) {\r\n
                    var stylearray = [],\r\n
                    selectedIdx = -1,\r\n
                    selectedUrl;\r\n
                    _.each(styles, function (item, index) {\r\n
                        stylearray.push({\r\n
                            imageUrl: item.asc_getImageUrl(),\r\n
                            data: item.asc_getStyle(),\r\n
                            tip: me.textStyle + " " + item.asc_getStyle()\r\n
                        });\r\n
                        if (me._state.ChartStyle == item.asc_getStyle()) {\r\n
                            selectedIdx = index;\r\n
                            selectedUrl = item.asc_getImageUrl();\r\n
                        }\r\n
                    });\r\n
                    stylesStore.reset(stylearray, {\r\n
                        silent: false\r\n
                    });\r\n
                }\r\n
            }\r\n
            this.mnuChartStylePicker.selectByIndex(selectedIdx, true);\r\n
            if (selectedIdx >= 0 && this.btnChartStyle.cmpEl) {\r\n
                var style = "url(" + selectedUrl + ")";\r\n
                var btnIconEl = this.btnChartStyle.cmpEl.find("span.btn-icon");\r\n
                btnIconEl.css("background-image", style);\r\n
            }\r\n
        },\r\n
        _setDefaults: function (props) {\r\n
            var me = this;\r\n
            if (props) {\r\n
                this.chartSettings = props;\r\n
                this._state.ChartType = props.getType();\r\n
                this._noApply = true;\r\n
                var record = this.mnuChartTypePicker.store.findWhere({\r\n
                    type: this._state.ChartType\r\n
                });\r\n
                this.mnuChartTypePicker.selectRecord(record, true);\r\n
                if (record) {\r\n
                    this.btnChartType.setIconCls("item-chartlist " + record.get("iconCls"));\r\n
                }\r\n
                this.updateChartStyles(this.api.asc_getChartPreviews(this._state.ChartType));\r\n
                this._noApply = false;\r\n
                this._state.ChartStyle = props.getStyle();\r\n
                record = this.mnuChartStylePicker.store.findWhere({\r\n
                    data: this._state.ChartStyle\r\n
                });\r\n
                this.mnuChartStylePicker.selectRecord(record, true);\r\n
                if (record) {\r\n
                    var btnIconEl = this.btnChartStyle.cmpEl.find("span.btn-icon");\r\n
                    btnIconEl.css("background-image", "url(" + record.get("imageUrl") + ")");\r\n
                }\r\n
                var value = props.getRange();\r\n
                this.txtDataRange.setValue((value) ? value : "");\r\n
                this.dataRangeValid = value;\r\n
                this.txtDataRange.validation = function (value) {\r\n
                    if (_.isEmpty(value)) {\r\n
                        if (!me.cmbDataDirect.isDisabled()) {\r\n
                            me.cmbDataDirect.setDisabled(true);\r\n
                        }\r\n
                        return true;\r\n
                    }\r\n
                    if (me.cmbDataDirect.isDisabled()) {\r\n
                        me.cmbDataDirect.setDisabled(false);\r\n
                    }\r\n
                    var isvalid = me.api.asc_checkDataRange(c_oAscSelectionDialogType.Chart, value, false);\r\n
                    return (isvalid == c_oAscError.ID.DataRangeError) ? me.textInvalidRange : true;\r\n
                };\r\n
                this.cmbDataDirect.setDisabled(value === null);\r\n
                this.cmbDataDirect.setValue(props.getInColumns() ? 1 : 0);\r\n
                this.cmbChartTitle.setValue(props.getTitle());\r\n
                this.cmbLegendPos.setValue(props.getLegendPos());\r\n
                this.cmbHorTitle.setValue(props.getHorAxisLabel());\r\n
                this.cmbVertTitle.setValue(props.getVertAxisLabel());\r\n
                this.cmbHorGrid.setValue(props.getHorGridLines());\r\n
                this.cmbVertGrid.setValue(props.getVertGridLines());\r\n
                this.cmbDataLabels.setValue(props.getDataLabelsPos());\r\n
                this.onSelectDataLabels(this.cmbDataLabels, {\r\n
                    value: props.getDataLabelsPos()\r\n
                });\r\n
                this.chSeriesName.setValue(this.chartSettings.getShowSerName(), true);\r\n
                this.chCategoryName.setValue(this.chartSettings.getShowCatName(), true);\r\n
                this.chValue.setValue(this.chartSettings.getShowVal(), true);\r\n
                value = props.getSeparator();\r\n
                this.txtSeparator.setValue((value) ? value : "");\r\n
                value = (this._state.ChartType == c_oAscChartTypeSettings.lineNormal || this._state.ChartType == c_oAscChartTypeSettings.lineStacked || this._state.ChartType == c_oAscChartTypeSettings.lineStackedPer || this._state.ChartType == c_oAscChartTypeSettings.scatter);\r\n
                this.chMarkers.setVisible(value);\r\n
                this.cmbLines.setVisible(value);\r\n
                this.lblLines.toggleClass("hidden", !value);\r\n
                if (value) {\r\n
                    this.chMarkers.setValue(this.chartSettings.getShowMarker(), true);\r\n
                    this.cmbLines.setValue(props.getLine() ? (props.getSmooth() ? 2 : 1) : 0);\r\n
                }\r\n
                this.vertAxisProps = props.getVertAxisProps();\r\n
                this.horAxisProps = props.getHorAxisProps();\r\n
                this.updateAxisProps(this._state.ChartType);\r\n
            }\r\n
        },\r\n
        getSettings: function () {\r\n
            var value, type = this.mnuChartTypePicker.getSelectedRec()[0].get("type");\r\n
            this.chartSettings.putType(type);\r\n
            this.chartSettings.putStyle(this._state.ChartStyle);\r\n
            this.chartSettings.putInColumns(this.cmbDataDirect.getValue() == 1);\r\n
            this.chartSettings.putRange(this.txtDataRange.getValue());\r\n
            this.chartSettings.putTitle(this.cmbChartTitle.getValue());\r\n
            this.chartSettings.putLegendPos(this.cmbLegendPos.getValue());\r\n
            this.chartSettings.putHorAxisLabel(this.cmbHorTitle.getValue());\r\n
            this.chartSettings.putVertAxisLabel(this.cmbVertTitle.getValue());\r\n
            this.chartSettings.putHorGridLines(this.cmbHorGrid.getValue());\r\n
            this.chartSettings.putVertGridLines(this.cmbVertGrid.getValue());\r\n
            this.chartSettings.putDataLabelsPos(this.cmbDataLabels.getValue());\r\n
            this.chartSettings.putShowSerName(this.chSeriesName.getValue() == "checked");\r\n
            this.chartSettings.putShowCatName(this.chCategoryName.getValue() == "checked");\r\n
            this.chartSettings.putShowVal(this.chValue.getValue() == "checked");\r\n
            this.chartSettings.putSeparator(_.isEmpty(this.txtSeparator.getValue()) ? " " : this.txtSeparator.getValue());\r\n
            this.chartSettings.putShowMarker(this.chMarkers.getValue() == "checked");\r\n
            value = (type == c_oAscChartTypeSettings.lineNormal || type == c_oAscChartTypeSettings.lineStacked || type == c_oAscChartTypeSettings.lineStackedPer || type == c_oAscChartTypeSettings.scatter);\r\n
            if (value) {\r\n
                value = this.cmbLines.getValue();\r\n
                this.chartSettings.putLine(value !== 0);\r\n
                if (value > 0) {\r\n
                    this.chartSettings.putSmooth(value == 2);\r\n
                }\r\n
            }\r\n
            this.chartSettings.putVertAxisProps(this.vertAxisProps);\r\n
            this.chartSettings.putHorAxisProps(this.horAxisProps);\r\n
            return {\r\n
                chartSettings: this.chartSettings\r\n
            };\r\n
        },\r\n
        isRangeValid: function () {\r\n
            var isvalid;\r\n
            if (!_.isEmpty(this.txtDataRange.getValue())) {\r\n
                isvalid = this.api.asc_checkDataRange(c_oAscSelectionDialogType.Chart, this.txtDataRange.getValue(), true, this.cmbDataDirect.getValue() == 0, this.mnuChartTypePicker.getSelectedRec()[0].get("type"));\r\n
                if (isvalid == c_oAscError.ID.No) {\r\n
                    return true;\r\n
                }\r\n
            } else {\r\n
                this.txtDataRange.showError([this.txtEmpty]);\r\n
            }\r\n
            this.btnsCategory[0].toggle(true);\r\n
            this.onCategoryClick(this.btnsCategory[0]);\r\n
            if (isvalid == c_oAscError.ID.StockChartError) {\r\n
                Common.UI.warning({\r\n
                    msg: this.errorStockChart\r\n
                });\r\n
            } else {\r\n
                if (isvalid == c_oAscError.ID.MaxDataSeriesError) {\r\n
                    Common.UI.warning({\r\n
                        msg: this.errorMaxRows\r\n
                    });\r\n
                } else {\r\n
                    this.txtDataRange.cmpEl.find("input").focus();\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onSelectData: function () {\r\n
            var me = this;\r\n
            if (me.api) {\r\n
                var handlerDlg = function (dlg, result) {\r\n
                    if (result == "ok") {\r\n
                        me.dataRangeValid = dlg.getSettings();\r\n
                        me.txtDataRange.setValue(me.dataRangeValid);\r\n
                        me.txtDataRange.checkValidate();\r\n
                    }\r\n
                };\r\n
                var win = new SSE.Views.CellRangeDialog({\r\n
                    handler: handlerDlg\r\n
                }).on("close", function () {\r\n
                    me.show();\r\n
                });\r\n
                var xy = me.$window.offset();\r\n
                me.hide();\r\n
                win.show(xy.left + 160, xy.top + 125);\r\n
                win.setSettings({\r\n
                    api: me.api,\r\n
                    isRows: (me.cmbDataDirect.getValue() == 0),\r\n
                    range: (!_.isEmpty(me.txtDataRange.getValue()) && (me.txtDataRange.checkValidate() == true)) ? me.txtDataRange.getValue() : me.dataRangeValid\r\n
                });\r\n
            }\r\n
        },\r\n
        onSelectDataLabels: function (obj, rec, e) {\r\n
            var disable = rec.value == c_oAscChartDataLabelsPos.none;\r\n
            this.chSeriesName.setDisabled(disable);\r\n
            this.chCategoryName.setDisabled(disable);\r\n
            this.chValue.setDisabled(disable);\r\n
            this.txtSeparator.setDisabled(disable);\r\n
        },\r\n
        show: function () {\r\n
            Common.Views.AdvancedSettingsWindow.prototype.show.apply(this, arguments);\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                me.txtDataRange.cmpEl.find("input").focus();\r\n
            },\r\n
            50);\r\n
        },\r\n
        textTitle: "Chart - Advanced Settings",\r\n
        textShowValues: "Display chart values",\r\n
        textShowBorders: "Display chart borders",\r\n
        textLine: "Line",\r\n
        textColumn: "Column",\r\n
        textBar: "Bar",\r\n
        textArea: "Area",\r\n
        textPie: "Pie",\r\n
        textPoint: "Point",\r\n
        textStock: "Stock",\r\n
        textDataRows: "in rows",\r\n
        textDataColumns: "in columns",\r\n
        textDisplayLegend: "Display Legend",\r\n
        textLegendBottom: "Bottom",\r\n
        textLegendTop: "Top",\r\n
        textLegendRight: "Right",\r\n
        textLegendLeft: "Left",\r\n
        textShowAxis: "Display Axis",\r\n
        textShowGrid: "Grid Lines",\r\n
        textDataRange: "Data Range",\r\n
        textChartTitle: "Chart Title",\r\n
        textXAxisTitle: "X Axis Title",\r\n
        textYAxisTitle: "Y Axis Title",\r\n
        txtEmpty: "This field is required",\r\n
        textInvalidRange: "ERROR! Invalid cells range",\r\n
        cancelButtonText: "Cancel",\r\n
        textTypeStyle: "Chart Type, Style &<br/>Data Range",\r\n
        textChartElementsLegend: "Chart Elements &<br/>Chart Legend",\r\n
        textLayout: "Layout",\r\n
        textLegendPos: "Legend",\r\n
        textHorTitle: "Horizontal Axis Title",\r\n
        textVertTitle: "Vertical Axis Title",\r\n
        textDataLabels: "Data Labels",\r\n
        textSeparator: "Data Labels Separator",\r\n
        textSeriesName: "Series Name",\r\n
        textCategoryName: "Category Name",\r\n
        textValue: "Value",\r\n
        textAxisOptions: "Axis Options",\r\n
        textMinValue: "Minimum Value",\r\n
        textMaxValue: "Maximum Value",\r\n
        textAxisCrosses: "Axis Crosses",\r\n
        textUnits: "Display Units",\r\n
        textTickOptions: "Tick Options",\r\n
        textMajorType: "Major Type",\r\n
        textMinorType: "Minor Type",\r\n
        textLabelOptions: "Label Options",\r\n
        textLabelPos: "Label Position",\r\n
        textReverse: "Values in reverse order",\r\n
        textVertAxis: "Vertical Axis",\r\n
        textHorAxis: "Horizontal Axis",\r\n
        textMarksInterval: "Interval between Marks",\r\n
        textLabelDist: "Axis Label Distance",\r\n
        textLabelInterval: "Interval between Labels",\r\n
        textAxisPos: "Axis Position",\r\n
        textLeftOverlay: "Left Overlay",\r\n
        textRightOverlay: "Right Overlay",\r\n
        textOverlay: "Overlay",\r\n
        textNoOverlay: "No Overlay",\r\n
        textRotated: "Rotated",\r\n
        textHorizontal: "Horizontal",\r\n
        textInnerBottom: "Inner Bottom",\r\n
        textInnerTop: "Inner Top",\r\n
        textOuterTop: "Outer Top",\r\n
        textNone: "None",\r\n
        textCenter: "Center",\r\n
        textFixed: "Fixed",\r\n
        textAuto: "Auto",\r\n
        textCross: "Cross",\r\n
        textIn: "In",\r\n
        textOut: "Out",\r\n
        textLow: "Low",\r\n
        textHigh: "High",\r\n
        textNextToAxis: "Next to axis",\r\n
        textHundreds: "Hundreds",\r\n
        textThousands: "Thousands",\r\n
        textTenThousands: "10 000",\r\n
        textHundredThousands: "100 000",\r\n
        textMillions: "Millions",\r\n
        textTenMillions: "10 000 000",\r\n
        textHundredMil: "100 000 000",\r\n
        textBillions: "Billions",\r\n
        textTrillions: "Trillions",\r\n
        textCustom: "Custom",\r\n
        textManual: "Manual",\r\n
        textBetweenTickMarks: "Between Tick Marks",\r\n
        textOnTickMarks: "On Tick Marks",\r\n
        textHorGrid: "Horizontal Gridlines",\r\n
        textVertGrid: "Vertical Gridlines",\r\n
        textLines: "Lines",\r\n
        textMarkers: "Markers",\r\n
        textMajor: "Major",\r\n
        textMinor: "Minor",\r\n
        textMajorMinor: "Major and Minor",\r\n
        textStraight: "Straight",\r\n
        textSmooth: "Smooth",\r\n
        textType: "Type",\r\n
        textTypeData: "Type & Data",\r\n
        textStyle: "Style",\r\n
        textSelectData: "Select Data",\r\n
        textDataSeries: "Data series",\r\n
        errorMaxRows: "ERROR! The maximum number of data series per chart is 255.",\r\n
        errorStockChart: "Incorrect row order. To build a stock chart place the data on the sheet in the following order:<br> opening price, max price, min price, closing price."\r\n
    },\r\n
    SSE.Views.ChartSettingsDlg || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>62685</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
