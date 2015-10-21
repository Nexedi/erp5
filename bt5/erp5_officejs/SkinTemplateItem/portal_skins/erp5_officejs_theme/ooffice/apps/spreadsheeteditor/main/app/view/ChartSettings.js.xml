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
            <value> <string>ts44321337.93</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ChartSettings.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/ChartSettings.template", "jquery", "underscore", "backbone", "common/main/lib/component/Button", "common/main/lib/component/MetricSpinner", "spreadsheeteditor/main/app/view/ChartSettingsDlg"], function (menuTemplate, $, _, Backbone) {\r\n
    SSE.Views.ChartSettings = Backbone.View.extend(_.extend({\r\n
        el: "#id-chart-settings",\r\n
        template: _.template(menuTemplate),\r\n
        events: {},\r\n
        options: {\r\n
            alias: "ChartSettings"\r\n
        },\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            this._initSettings = true;\r\n
            this._state = {\r\n
                Width: 0,\r\n
                Height: 0,\r\n
                ChartStyle: 1,\r\n
                ChartType: -1,\r\n
                SeveralCharts: false,\r\n
                DisabledControls: false\r\n
            };\r\n
            this._nRatio = 1;\r\n
            this.spinners = [];\r\n
            this.lockedControls = [];\r\n
            this._locked = false;\r\n
            this._noApply = false;\r\n
            this._originalProps = null;\r\n
            this.render();\r\n
            this.btnChartType = new Common.UI.Button({\r\n
                cls: "btn-large-dataview",\r\n
                iconCls: "item-chartlist bar-normal",\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "width: 330px;",\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-chart-menu-type" class="menu-insertchart"  style="margin: 5px 5px 5px 10px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnChartType.on("render:after", function (btn) {\r\n
                me.mnuChartTypePicker = new Common.UI.DataView({\r\n
                    el: $("#id-chart-menu-type"),\r\n
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
            this.btnChartType.render($("#chart-button-type"));\r\n
            this.mnuChartTypePicker.on("item:click", _.bind(this.onSelectType, this, this.btnChartType));\r\n
            this.lockedControls.push(this.btnChartType);\r\n
            this.btnChartStyle = new Common.UI.Button({\r\n
                cls: "btn-large-dataview",\r\n
                iconCls: "item-wrap",\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tr-br",\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-chart-menu-style" style="width: 245px; margin: 0 5px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnChartStyle.on("render:after", function (btn) {\r\n
                me.mnuChartStylePicker = new Common.UI.DataView({\r\n
                    el: $("#id-chart-menu-style"),\r\n
                    style: "max-height: 411px;",\r\n
                    parentMenu: btn.menu,\r\n
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
            this.btnChartStyle.render($("#chart-button-style"));\r\n
            this.mnuChartStylePicker.on("item:click", _.bind(this.onSelectStyle, this, this.btnChartStyle));\r\n
            this.lockedControls.push(this.btnChartStyle);\r\n
            this.spnWidth = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-spin-width"),\r\n
                step: 0.1,\r\n
                width: 78,\r\n
                defaultUnit: "cm",\r\n
                value: "3 cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnWidth);\r\n
            this.lockedControls.push(this.spnWidth);\r\n
            this.spnHeight = new Common.UI.MetricSpinner({\r\n
                el: $("#chart-spin-height"),\r\n
                step: 0.1,\r\n
                width: 78,\r\n
                defaultUnit: "cm",\r\n
                value: "3 cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnHeight);\r\n
            this.lockedControls.push(this.spnHeight);\r\n
            this.spnWidth.on("change", _.bind(this.onWidthChange, this));\r\n
            this.spnHeight.on("change", _.bind(this.onHeightChange, this));\r\n
            this.btnRatio = new Common.UI.Button({\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "advanced-btn-ratio",\r\n
                style: "margin-bottom: 1px;",\r\n
                enableToggle: true,\r\n
                hint: this.textKeepRatio\r\n
            });\r\n
            this.btnRatio.render($("#chart-button-ratio"));\r\n
            this.lockedControls.push(this.btnRatio);\r\n
            var value = window.localStorage.getItem("sse-settings-chartratio");\r\n
            if (value !== null && parseInt(value) == 1) {\r\n
                this.btnRatio.toggle(true);\r\n
            }\r\n
            this.btnRatio.on("click", _.bind(function (btn, e) {\r\n
                if (btn.pressed && this.spnHeight.getNumberValue() > 0) {\r\n
                    this._nRatio = this.spnWidth.getNumberValue() / this.spnHeight.getNumberValue();\r\n
                }\r\n
                window.localStorage.setItem("sse-settings-chartratio", (btn.pressed) ? 1 : 0);\r\n
            },\r\n
            this));\r\n
            $(this.el).on("click", "#chart-advanced-link", _.bind(this.openAdvancedSettings, this));\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.linkAdvanced = $("#chart-advanced-link");\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            if (this.api) {\r\n
                this.api.asc_registerCallback("asc_onUpdateChartStyles", _.bind(this._onUpdateChartStyles, this));\r\n
            }\r\n
            return this;\r\n
        },\r\n
        ChangeSettings: function (props) {\r\n
            if (this._initSettings) {\r\n
                this.createDelayedElements();\r\n
                this._initSettings = false;\r\n
            }\r\n
            this.disableControls(this._locked);\r\n
            if (this.api && props && props.asc_getChartProperties()) {\r\n
                this._originalProps = new Asc.asc_CImgProperty(props);\r\n
                this._noApply = true;\r\n
                this.chartProps = props.asc_getChartProperties();\r\n
                var value = props.asc_getSeveralCharts() || this._locked;\r\n
                if (this._state.SeveralCharts !== value) {\r\n
                    this.linkAdvanced.toggleClass("disabled", value);\r\n
                    this._state.SeveralCharts = value;\r\n
                }\r\n
                value = props.asc_getSeveralChartTypes();\r\n
                if (this._state.SeveralCharts && value) {\r\n
                    this.btnChartType.setIconCls("");\r\n
                    this._state.ChartType = null;\r\n
                } else {\r\n
                    var type = this.chartProps.getType();\r\n
                    if (this._state.ChartType !== type) {\r\n
                        var record = this.mnuChartTypePicker.store.findWhere({\r\n
                            type: type\r\n
                        });\r\n
                        this.mnuChartTypePicker.selectRecord(record, true);\r\n
                        if (record) {\r\n
                            this.btnChartType.setIconCls("item-chartlist " + record.get("iconCls"));\r\n
                        }\r\n
                        this.updateChartStyles(this.api.asc_getChartPreviews(type));\r\n
                        this._state.ChartType = type;\r\n
                    }\r\n
                }\r\n
                value = props.asc_getSeveralChartStyles();\r\n
                if (this._state.SeveralCharts && value) {\r\n
                    var btnIconEl = this.btnChartStyle.cmpEl.find("span.btn-icon");\r\n
                    btnIconEl.css("background-image", "none");\r\n
                    this.mnuChartStylePicker.selectRecord(null, true);\r\n
                    this._state.ChartStyle = null;\r\n
                } else {\r\n
                    value = this.chartProps.getStyle();\r\n
                    if (this._state.ChartStyle !== value) {\r\n
                        var record = this.mnuChartStylePicker.store.findWhere({\r\n
                            data: value\r\n
                        });\r\n
                        this.mnuChartStylePicker.selectRecord(record, true);\r\n
                        if (record) {\r\n
                            var btnIconEl = this.btnChartStyle.cmpEl.find("span.btn-icon");\r\n
                            btnIconEl.css("background-image", "url(" + record.get("imageUrl") + ")");\r\n
                        }\r\n
                        this._state.ChartStyle = value;\r\n
                    }\r\n
                }\r\n
                this._noApply = false;\r\n
                value = props.asc_getWidth();\r\n
                if (Math.abs(this._state.Width - value) > 0.001 || (this._state.Width === null || value === null) && (this._state.Width !== value)) {\r\n
                    this.spnWidth.setValue((value !== null) ? Common.Utils.Metric.fnRecalcFromMM(value) : "", true);\r\n
                    this._state.Width = value;\r\n
                }\r\n
                value = props.asc_getHeight();\r\n
                if (Math.abs(this._state.Height - value) > 0.001 || (this._state.Height === null || value === null) && (this._state.Height !== value)) {\r\n
                    this.spnHeight.setValue((value !== null) ? Common.Utils.Metric.fnRecalcFromMM(value) : "", true);\r\n
                    this._state.Height = value;\r\n
                }\r\n
                if (props.asc_getHeight() > 0) {\r\n
                    this._nRatio = props.asc_getWidth() / props.asc_getHeight();\r\n
                }\r\n
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
        createDelayedElements: function () {\r\n
            this.updateMetricUnit();\r\n
        },\r\n
        onWidthChange: function (field, newValue, oldValue, eOpts) {\r\n
            var w = field.getNumberValue();\r\n
            var h = this.spnHeight.getNumberValue();\r\n
            if (this.btnRatio.pressed) {\r\n
                h = w / this._nRatio;\r\n
                if (h > this.spnHeight.options.maxValue) {\r\n
                    h = this.spnHeight.options.maxValue;\r\n
                    w = h * this._nRatio;\r\n
                    this.spnWidth.setValue(w, true);\r\n
                }\r\n
                this.spnHeight.setValue(h, true);\r\n
            }\r\n
            if (this.api) {\r\n
                var props = new Asc.asc_CImgProperty();\r\n
                props.asc_putWidth(Common.Utils.Metric.fnRecalcToMM(w));\r\n
                props.asc_putHeight(Common.Utils.Metric.fnRecalcToMM(h));\r\n
                this.api.asc_setGraphicObjectProps(props);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onHeightChange: function (field, newValue, oldValue, eOpts) {\r\n
            var h = field.getNumberValue(),\r\n
            w = this.spnWidth.getNumberValue();\r\n
            if (this.btnRatio.pressed) {\r\n
                w = h * this._nRatio;\r\n
                if (w > this.spnWidth.options.maxValue) {\r\n
                    w = this.spnWidth.options.maxValue;\r\n
                    h = w / this._nRatio;\r\n
                    this.spnHeight.setValue(h, true);\r\n
                }\r\n
                this.spnWidth.setValue(w, true);\r\n
            }\r\n
            if (this.api) {\r\n
                var props = new Asc.asc_CImgProperty();\r\n
                props.asc_putWidth(Common.Utils.Metric.fnRecalcToMM(w));\r\n
                props.asc_putHeight(Common.Utils.Metric.fnRecalcToMM(h));\r\n
                this.api.asc_setGraphicObjectProps(props);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        openAdvancedSettings: function () {\r\n
            if (this.linkAdvanced.hasClass("disabled")) {\r\n
                return;\r\n
            }\r\n
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
            this._state.ChartType = -1;\r\n
            if (this.api && !this._noApply && this.chartProps) {\r\n
                var props = new Asc.asc_CImgProperty();\r\n
                this.chartProps.changeType(rawData.type);\r\n
                props.asc_putChartProperties(this.chartProps);\r\n
                this.api.asc_setGraphicObjectProps(props);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
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
            if (this.api && !this._noApply && this.chartProps) {\r\n
                var props = new Asc.asc_CImgProperty();\r\n
                this.chartProps.putStyle(rawData.data);\r\n
                props.asc_putChartProperties(this.chartProps);\r\n
                this.api.asc_setGraphicObjectProps(props);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        _onUpdateChartStyles: function () {\r\n
            if (this.api && this._state.ChartType !== null && this._state.ChartType > -1) {\r\n
                this.updateChartStyles(this.api.asc_getChartPreviews(this._state.ChartType));\r\n
            }\r\n
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
        setLocked: function (locked) {\r\n
            this._locked = locked;\r\n
        },\r\n
        disableControls: function (disable) {\r\n
            if (this._state.DisabledControls !== disable) {\r\n
                this._state.DisabledControls = disable;\r\n
                _.each(this.lockedControls, function (item) {\r\n
                    item.setDisabled(disable);\r\n
                });\r\n
                this.linkAdvanced.toggleClass("disabled", disable);\r\n
            }\r\n
        },\r\n
        textKeepRatio: "Constant Proportions",\r\n
        textSize: "Size",\r\n
        textWidth: "Width",\r\n
        textHeight: "Height",\r\n
        textEditData: "Edit Data",\r\n
        textChartType: "Change Chart Type",\r\n
        textLine: "Line Chart",\r\n
        textColumn: "Column Chart",\r\n
        textBar: "Bar Chart",\r\n
        textArea: "Area Chart",\r\n
        textPie: "Pie Chart",\r\n
        textPoint: "Point Chart",\r\n
        textStock: "Stock Chart",\r\n
        textStyle: "Style",\r\n
        textAdvanced: "Show advanced settings"\r\n
    },\r\n
    SSE.Views.ChartSettings || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>24711</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
