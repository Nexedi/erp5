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
            <value> <string>ts44321339.53</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ShapeSettingsAdvanced.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/ShapeSettingsAdvanced.template", "common/main/lib/view/AdvancedSettingsWindow", "common/main/lib/component/ComboBox", "common/main/lib/component/MetricSpinner"], function (contentTemplate) {\r\n
    SSE.Views.ShapeSettingsAdvanced = Common.Views.AdvancedSettingsWindow.extend(_.extend({\r\n
        options: {\r\n
            contentWidth: 300,\r\n
            height: 332,\r\n
            toggleGroup: "shape-adv-settings-group",\r\n
            sizeOriginal: {\r\n
                width: 0,\r\n
                height: 0\r\n
            },\r\n
            sizeMax: {\r\n
                width: 55.88,\r\n
                height: 55.88\r\n
            },\r\n
            properties: null\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle,\r\n
                items: [{\r\n
                    panelId: "id-adv-shape-width",\r\n
                    panelCaption: this.textSize\r\n
                },\r\n
                {\r\n
                    panelId: "id-adv-shape-shape",\r\n
                    panelCaption: this.textWeightArrows\r\n
                },\r\n
                {\r\n
                    panelId: "id-adv-shape-margins",\r\n
                    panelCaption: this.strMargins\r\n
                }],\r\n
                contentTemplate: _.template(contentTemplate)({\r\n
                    scope: this\r\n
                })\r\n
            },\r\n
            options);\r\n
            Common.Views.AdvancedSettingsWindow.prototype.initialize.call(this, this.options);\r\n
            this.spinners = [];\r\n
            this.Margins = undefined;\r\n
            this._nRatio = 1;\r\n
            this._originalProps = this.options.shapeProps;\r\n
            this._changedProps = null;\r\n
        },\r\n
        render: function () {\r\n
            Common.Views.AdvancedSettingsWindow.prototype.render.call(this);\r\n
            var me = this;\r\n
            this.spnWidth = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-advanced-spin-width"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "3 cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnWidth.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this.btnRatio.pressed) {\r\n
                    var w = field.getNumberValue();\r\n
                    var h = w / this._nRatio;\r\n
                    if (h > this.spnHeight.options.maxValue) {\r\n
                        h = this.spnHeight.options.maxValue;\r\n
                        w = h * this._nRatio;\r\n
                        this.spnWidth.setValue(w, true);\r\n
                    }\r\n
                    this.spnHeight.setValue(h, true);\r\n
                }\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putWidth(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                    this._changedProps.asc_putHeight(Common.Utils.Metric.fnRecalcToMM(this.spnHeight.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnWidth);\r\n
            this.spnHeight = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-advanced-spin-height"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "3 cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnHeight.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                var h = field.getNumberValue(),\r\n
                w = null;\r\n
                if (this.btnRatio.pressed) {\r\n
                    w = h * this._nRatio;\r\n
                    if (w > this.spnWidth.options.maxValue) {\r\n
                        w = this.spnWidth.options.maxValue;\r\n
                        h = w / this._nRatio;\r\n
                        this.spnHeight.setValue(h, true);\r\n
                    }\r\n
                    this.spnWidth.setValue(w, true);\r\n
                }\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putHeight(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                    this._changedProps.asc_putWidth(Common.Utils.Metric.fnRecalcToMM(this.spnWidth.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnHeight);\r\n
            this.btnRatio = new Common.UI.Button({\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "advanced-btn-ratio",\r\n
                style: "margin-bottom: 1px;",\r\n
                enableToggle: true,\r\n
                hint: this.textKeepRatio\r\n
            });\r\n
            this.btnRatio.render($("#shape-advanced-button-ratio"));\r\n
            this.btnRatio.on("click", _.bind(function (btn, e) {\r\n
                if (btn.pressed && this.spnHeight.getNumberValue() > 0) {\r\n
                    this._nRatio = this.spnWidth.getNumberValue() / this.spnHeight.getNumberValue();\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spnMarginTop = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-margin-top"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnMarginTop.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getPaddings() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putPaddings(new Asc.asc_CPaddings());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getPaddings().asc_putTop(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnMarginTop);\r\n
            this.spnMarginBottom = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-margin-bottom"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnMarginBottom.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getPaddings() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putPaddings(new Asc.asc_CPaddings());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getPaddings().asc_putBottom(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnMarginBottom);\r\n
            this.spnMarginLeft = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-margin-left"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 9.34,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnMarginLeft.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getPaddings() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putPaddings(new Asc.asc_CPaddings());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getPaddings().asc_putLeft(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnMarginLeft);\r\n
            this.spnMarginRight = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-margin-right"),\r\n
                step: 0.1,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                value: "0.19 cm",\r\n
                maxValue: 9.34,\r\n
                minValue: 0\r\n
            });\r\n
            this.spnMarginRight.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getPaddings() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putPaddings(new Asc.asc_CPaddings());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getPaddings().asc_putRight(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.spnMarginRight);\r\n
            this._arrCapType = [{\r\n
                displayValue: this.textFlat,\r\n
                value: c_oAscLineCapType.Flat\r\n
            },\r\n
            {\r\n
                displayValue: this.textRound,\r\n
                value: c_oAscLineCapType.Round\r\n
            },\r\n
            {\r\n
                displayValue: this.textSquare,\r\n
                value: c_oAscLineCapType.Square\r\n
            }];\r\n
            this.cmbCapType = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-cap-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: this._arrCapType\r\n
            });\r\n
            this.cmbCapType.setValue(c_oAscLineCapType.Flat);\r\n
            this.cmbCapType.on("selected", _.bind(function (combo, record) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLinecap(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this._arrJoinType = [{\r\n
                displayValue: this.textRound,\r\n
                value: c_oAscLineJoinType.Round\r\n
            },\r\n
            {\r\n
                displayValue: this.textBevel,\r\n
                value: c_oAscLineJoinType.Bevel\r\n
            },\r\n
            {\r\n
                displayValue: this.textMiter,\r\n
                value: c_oAscLineJoinType.Miter\r\n
            }];\r\n
            this.cmbJoinType = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-join-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 100px;",\r\n
                editable: false,\r\n
                data: this._arrJoinType\r\n
            });\r\n
            this.cmbJoinType.setValue(c_oAscLineJoinType.Round);\r\n
            this.cmbJoinType.on("selected", _.bind(function (combo, record) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                        this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                    }\r\n
                    if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                        this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                    }\r\n
                    this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLinejoin(record.value);\r\n
                }\r\n
            },\r\n
            this));\r\n
            var _arrStyles = [],\r\n
            _arrSize = [];\r\n
            for (var i = 0; i < 6; i++) {\r\n
                _arrStyles.push({\r\n
                    value: i,\r\n
                    offsetx: 80 * i + 10,\r\n
                    offsety: 0\r\n
                });\r\n
            }\r\n
            _arrStyles[0].type = c_oAscLineBeginType.None;\r\n
            _arrStyles[1].type = c_oAscLineBeginType.Triangle;\r\n
            _arrStyles[2].type = c_oAscLineBeginType.Arrow;\r\n
            _arrStyles[3].type = c_oAscLineBeginType.Stealth;\r\n
            _arrStyles[4].type = c_oAscLineBeginType.Diamond;\r\n
            _arrStyles[5].type = c_oAscLineBeginType.Oval;\r\n
            for (i = 0; i < 9; i++) {\r\n
                _arrSize.push({\r\n
                    value: i,\r\n
                    offsetx: 80 + 10,\r\n
                    offsety: 20 * (i + 1)\r\n
                });\r\n
            }\r\n
            _arrSize[0].type = c_oAscLineBeginSize.small_small;\r\n
            _arrSize[1].type = c_oAscLineBeginSize.small_mid;\r\n
            _arrSize[2].type = c_oAscLineBeginSize.small_large;\r\n
            _arrSize[3].type = c_oAscLineBeginSize.mid_small;\r\n
            _arrSize[4].type = c_oAscLineBeginSize.mid_mid;\r\n
            _arrSize[5].type = c_oAscLineBeginSize.mid_large;\r\n
            _arrSize[6].type = c_oAscLineBeginSize.large_small;\r\n
            _arrSize[7].type = c_oAscLineBeginSize.large_mid;\r\n
            _arrSize[8].type = c_oAscLineBeginSize.large_large;\r\n
            this.btnBeginStyle = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-begin-style"),\r\n
                template: _.template([\'<div class="input-group combobox combo-dataview-menu input-group-nr dropdown-toggle combo-arrow-style"  data-toggle="dropdown">\', \'<div class="form-control image" style="width: 100px;"></div>\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default"><span class="caret"></span></button>\', "</div>"].join(""))\r\n
            });\r\n
            (new Common.UI.Menu({\r\n
                style: "min-width: 105px;",\r\n
                items: [{\r\n
                    template: _.template(\'<div id="shape-advanced-menu-begin-style" style="width: 105px; margin: 0 5px;"></div>\')\r\n
                }]\r\n
            })).render($("#shape-advanced-begin-style"));\r\n
            this.mnuBeginStylePicker = new Common.UI.DataView({\r\n
                el: $("#shape-advanced-menu-begin-style"),\r\n
                parentMenu: me.btnBeginStyle.menu,\r\n
                store: new Common.UI.DataViewStore(_arrStyles),\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="item-arrow" style="background-position: -<%= offsetx %>px -<%= offsety %>px;"></div>\')\r\n
            });\r\n
            this.mnuBeginStylePicker.on("item:click", _.bind(this.onSelectBeginStyle, this));\r\n
            this._selectStyleItem(this.btnBeginStyle, null);\r\n
            this.btnBeginSize = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-begin-size"),\r\n
                template: _.template([\'<div class="input-group combobox combo-dataview-menu input-group-nr dropdown-toggle combo-arrow-style"  data-toggle="dropdown">\', \'<div class="form-control image" style="width: 100px;"></div>\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default"><span class="caret"></span></button>\', "</div>"].join(""))\r\n
            });\r\n
            (new Common.UI.Menu({\r\n
                style: "min-width: 160px;",\r\n
                items: [{\r\n
                    template: _.template(\'<div id="shape-advanced-menu-begin-size" style="width: 160px; margin: 0 5px;"></div>\')\r\n
                }]\r\n
            })).render($("#shape-advanced-begin-size"));\r\n
            this.mnuBeginSizePicker = new Common.UI.DataView({\r\n
                el: $("#shape-advanced-menu-begin-size"),\r\n
                parentMenu: me.btnBeginSize.menu,\r\n
                store: new Common.UI.DataViewStore(_arrSize),\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="item-arrow" style="background-position: -<%= offsetx %>px -<%= offsety %>px;"></div>\')\r\n
            });\r\n
            this.mnuBeginSizePicker.on("item:click", _.bind(this.onSelectBeginSize, this));\r\n
            this._selectStyleItem(this.btnBeginSize, null);\r\n
            for (i = 0; i < _arrStyles.length; i++) {\r\n
                _arrStyles[i].offsety += 200;\r\n
            }\r\n
            for (i = 0; i < _arrSize.length; i++) {\r\n
                _arrSize[i].offsety += 200;\r\n
            }\r\n
            this.btnEndStyle = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-end-style"),\r\n
                template: _.template([\'<div class="input-group combobox combo-dataview-menu input-group-nr dropdown-toggle combo-arrow-style"  data-toggle="dropdown">\', \'<div class="form-control image" style="width: 100px;"></div>\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default"><span class="caret"></span></button>\', "</div>"].join(""))\r\n
            });\r\n
            (new Common.UI.Menu({\r\n
                style: "min-width: 105px;",\r\n
                items: [{\r\n
                    template: _.template(\'<div id="shape-advanced-menu-end-style" style="width: 105px; margin: 0 5px;"></div>\')\r\n
                }]\r\n
            })).render($("#shape-advanced-end-style"));\r\n
            this.mnuEndStylePicker = new Common.UI.DataView({\r\n
                el: $("#shape-advanced-menu-end-style"),\r\n
                parentMenu: me.btnEndStyle.menu,\r\n
                store: new Common.UI.DataViewStore(_arrStyles),\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="item-arrow" style="background-position: -<%= offsetx %>px -<%= offsety %>px;"></div>\')\r\n
            });\r\n
            this.mnuEndStylePicker.on("item:click", _.bind(this.onSelectEndStyle, this));\r\n
            this._selectStyleItem(this.btnEndStyle, null);\r\n
            this.btnEndSize = new Common.UI.ComboBox({\r\n
                el: $("#shape-advanced-end-size"),\r\n
                template: _.template([\'<div class="input-group combobox combo-dataview-menu input-group-nr dropdown-toggle combo-arrow-style"  data-toggle="dropdown">\', \'<div class="form-control image" style="width: 100px;"></div>\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default"><span class="caret"></span></button>\', "</div>"].join(""))\r\n
            });\r\n
            (new Common.UI.Menu({\r\n
                style: "min-width: 160px;",\r\n
                items: [{\r\n
                    template: _.template(\'<div id="shape-advanced-menu-end-size" style="width: 160px; margin: 0 5px;"></div>\')\r\n
                }]\r\n
            })).render($("#shape-advanced-end-size"));\r\n
            this.mnuEndSizePicker = new Common.UI.DataView({\r\n
                el: $("#shape-advanced-menu-end-size"),\r\n
                parentMenu: me.btnEndSize.menu,\r\n
                store: new Common.UI.DataViewStore(_arrSize),\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="item-arrow" style="background-position: -<%= offsetx %>px -<%= offsety %>px;"></div>\')\r\n
            });\r\n
            this.mnuEndSizePicker.on("item:click", _.bind(this.onSelectEndSize, this));\r\n
            this._selectStyleItem(this.btnEndSize, null);\r\n
            this.afterRender();\r\n
        },\r\n
        afterRender: function () {\r\n
            this.updateMetricUnit();\r\n
            this._setDefaults(this._originalProps);\r\n
        },\r\n
        _setDefaults: function (props) {\r\n
            if (props && props.asc_getShapeProperties()) {\r\n
                var shapeprops = props.asc_getShapeProperties();\r\n
                this.spnWidth.setValue(Common.Utils.Metric.fnRecalcFromMM(props.asc_getWidth()).toFixed(2), true);\r\n
                this.spnHeight.setValue(Common.Utils.Metric.fnRecalcFromMM(props.asc_getHeight()).toFixed(2), true);\r\n
                if (props.asc_getHeight() > 0) {\r\n
                    this._nRatio = props.asc_getWidth() / props.asc_getHeight();\r\n
                }\r\n
                var value = window.localStorage.getItem("sse-settings-shaperatio");\r\n
                if (value !== null && parseInt(value) == 1) {\r\n
                    this.btnRatio.toggle(true);\r\n
                }\r\n
                this._setShapeDefaults(shapeprops);\r\n
                var margins = shapeprops.asc_getPaddings();\r\n
                if (margins) {\r\n
                    var val = margins.asc_getLeft();\r\n
                    this.spnMarginLeft.setValue((null !== val && undefined !== val) ? Common.Utils.Metric.fnRecalcFromMM(val) : "", true);\r\n
                    val = margins.asc_getTop();\r\n
                    this.spnMarginTop.setValue((null !== val && undefined !== val) ? Common.Utils.Metric.fnRecalcFromMM(val) : "", true);\r\n
                    val = margins.asc_getRight();\r\n
                    this.spnMarginRight.setValue((null !== val && undefined !== val) ? Common.Utils.Metric.fnRecalcFromMM(val) : "", true);\r\n
                    val = margins.asc_getBottom();\r\n
                    this.spnMarginBottom.setValue((null !== val && undefined !== val) ? Common.Utils.Metric.fnRecalcFromMM(val) : "", true);\r\n
                }\r\n
                this.btnsCategory[2].setDisabled(null === margins);\r\n
                this._changedProps = new Asc.asc_CImgProperty();\r\n
            }\r\n
        },\r\n
        getSettings: function () {\r\n
            window.localStorage.setItem("sse-settings-shaperatio", (this.btnRatio.pressed) ? 1 : 0);\r\n
            return {\r\n
                shapeProps: this._changedProps\r\n
            };\r\n
        },\r\n
        _setShapeDefaults: function (props) {\r\n
            if (props) {\r\n
                var stroke = props.asc_getStroke();\r\n
                if (stroke) {\r\n
                    var value = stroke.asc_getLinejoin();\r\n
                    for (var i = 0; i < this._arrJoinType.length; i++) {\r\n
                        if (value == this._arrJoinType[i].value) {\r\n
                            this.cmbJoinType.setValue(value);\r\n
                            break;\r\n
                        }\r\n
                    }\r\n
                    value = stroke.asc_getLinecap();\r\n
                    for (i = 0; i < this._arrCapType.length; i++) {\r\n
                        if (value == this._arrCapType[i].value) {\r\n
                            this.cmbCapType.setValue(value);\r\n
                            break;\r\n
                        }\r\n
                    }\r\n
                    var canchange = stroke.asc_getCanChangeArrows();\r\n
                    this.btnBeginStyle.setDisabled(!canchange);\r\n
                    this.btnEndStyle.setDisabled(!canchange);\r\n
                    this.btnBeginSize.setDisabled(!canchange);\r\n
                    this.btnEndSize.setDisabled(!canchange);\r\n
                    if (canchange) {\r\n
                        value = stroke.asc_getLinebeginsize();\r\n
                        var rec = this.mnuBeginSizePicker.store.findWhere({\r\n
                            type: value\r\n
                        });\r\n
                        if (rec) {\r\n
                            this._beginSizeIdx = rec.get("value");\r\n
                        } else {\r\n
                            this._beginSizeIdx = null;\r\n
                            this._selectStyleItem(this.btnBeginSize, null);\r\n
                        }\r\n
                        value = stroke.asc_getLinebeginstyle();\r\n
                        rec = this.mnuBeginStylePicker.store.findWhere({\r\n
                            type: value\r\n
                        });\r\n
                        if (rec) {\r\n
                            this.mnuBeginStylePicker.selectRecord(rec, true);\r\n
                            this._updateSizeArr(this.btnBeginSize, this.mnuBeginSizePicker, rec, this._beginSizeIdx);\r\n
                            this._selectStyleItem(this.btnBeginStyle, rec);\r\n
                        } else {\r\n
                            this._selectStyleItem(this.btnBeginStyle, null);\r\n
                        }\r\n
                        value = stroke.asc_getLineendsize();\r\n
                        rec = this.mnuEndSizePicker.store.findWhere({\r\n
                            type: value\r\n
                        });\r\n
                        if (rec) {\r\n
                            this._endSizeIdx = rec.get("value");\r\n
                        } else {\r\n
                            this._endSizeIdx = null;\r\n
                            this._selectStyleItem(this.btnEndSize, null);\r\n
                        }\r\n
                        value = stroke.asc_getLineendstyle();\r\n
                        rec = this.mnuEndStylePicker.store.findWhere({\r\n
                            type: value\r\n
                        });\r\n
                        if (rec) {\r\n
                            this.mnuEndStylePicker.selectRecord(rec, true);\r\n
                            this._updateSizeArr(this.btnEndSize, this.mnuEndSizePicker, rec, this._endSizeIdx);\r\n
                            this._selectStyleItem(this.btnEndStyle, rec);\r\n
                        } else {\r\n
                            this._selectStyleItem(this.btnEndStyle, null);\r\n
                        }\r\n
                    } else {\r\n
                        this._selectStyleItem(this.btnBeginStyle);\r\n
                        this._selectStyleItem(this.btnEndStyle);\r\n
                        this._selectStyleItem(this.btnBeginSize);\r\n
                        this._selectStyleItem(this.btnEndSize);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        updateMetricUnit: function () {\r\n
            if (this.spinners) {\r\n
                for (var i = 0; i < this.spinners.length; i++) {\r\n
                    var spinner = this.spinners[i];\r\n
                    spinner.setDefaultUnit(Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()]);\r\n
                    spinner.setStep(Common.Utils.Metric.getCurrentMetric() == Common.Utils.Metric.c_MetricUnits.cm ? 0.01 : 1);\r\n
                }\r\n
            }\r\n
            this.sizeMax = {\r\n
                width: Common.Utils.Metric.fnRecalcFromMM(this.options.sizeMax.width * 10),\r\n
                height: Common.Utils.Metric.fnRecalcFromMM(this.options.sizeMax.height * 10)\r\n
            };\r\n
            if (this.options.sizeOriginal) {\r\n
                this.sizeOriginal = {\r\n
                    width: Common.Utils.Metric.fnRecalcFromMM(this.options.sizeOriginal.width),\r\n
                    height: Common.Utils.Metric.fnRecalcFromMM(this.options.sizeOriginal.height)\r\n
                };\r\n
            }\r\n
        },\r\n
        _updateSizeArr: function (combo, picker, record, sizeidx) {\r\n
            if (record.get("value") > 0) {\r\n
                picker.store.each(function (rec) {\r\n
                    rec.set({\r\n
                        offsetx: record.get("value") * 80 + 10\r\n
                    });\r\n
                },\r\n
                this);\r\n
                combo.setDisabled(false);\r\n
                if (sizeidx !== null) {\r\n
                    picker.selectByIndex(sizeidx, true);\r\n
                    this._selectStyleItem(combo, picker.store.at(sizeidx));\r\n
                } else {\r\n
                    this._selectStyleItem(combo, null);\r\n
                }\r\n
            } else {\r\n
                this._selectStyleItem(combo, null);\r\n
                combo.setDisabled(true);\r\n
            }\r\n
        },\r\n
        _selectStyleItem: function (combo, record) {\r\n
            var formcontrol = $(combo.el).find(".form-control");\r\n
            formcontrol.css("background-position", ((record) ? (-record.get("offsetx") + 20) + "px" : "0") + " " + ((record) ? "-" + record.get("offsety") + "px" : "-30px"));\r\n
        },\r\n
        onSelectBeginStyle: function (picker, view, record) {\r\n
            if (this._changedProps) {\r\n
                if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                    this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                }\r\n
                if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                    this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                }\r\n
                this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLinebeginstyle(record.get("type"));\r\n
            }\r\n
            if (this._beginSizeIdx === null || this._beginSizeIdx === undefined) {\r\n
                this._beginSizeIdx = 4;\r\n
            }\r\n
            this._updateSizeArr(this.btnBeginSize, this.mnuBeginSizePicker, record, this._beginSizeIdx);\r\n
            this._selectStyleItem(this.btnBeginStyle, record);\r\n
        },\r\n
        onSelectBeginSize: function (picker, view, record) {\r\n
            if (this._changedProps) {\r\n
                if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                    this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                }\r\n
                if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                    this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                }\r\n
                this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLinebeginsize(record.get("type"));\r\n
            }\r\n
            this._beginSizeIdx = record.get("value");\r\n
            this._selectStyleItem(this.btnBeginSize, record);\r\n
        },\r\n
        onSelectEndStyle: function (picker, view, record) {\r\n
            if (this._changedProps) {\r\n
                if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                    this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                }\r\n
                if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                    this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                }\r\n
                this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLineendstyle(record.get("type"));\r\n
            }\r\n
            if (this._endSizeIdx === null || this._endSizeIdx === undefined) {\r\n
                this._endSizeIdx = 4;\r\n
            }\r\n
            this._updateSizeArr(this.btnEndSize, this.mnuEndSizePicker, record, this._endSizeIdx);\r\n
            this._selectStyleItem(this.btnEndStyle, record);\r\n
        },\r\n
        onSelectEndSize: function (picker, view, record) {\r\n
            if (this._changedProps) {\r\n
                if (this._changedProps.asc_getShapeProperties() === null || this._changedProps.asc_getShapeProperties() === undefined) {\r\n
                    this._changedProps.asc_putShapeProperties(new Asc.asc_CShapeProperty());\r\n
                }\r\n
                if (this._changedProps.asc_getShapeProperties().asc_getStroke() === null) {\r\n
                    this._changedProps.asc_getShapeProperties().asc_putStroke(new Asc.asc_CStroke());\r\n
                }\r\n
                this._changedProps.asc_getShapeProperties().asc_getStroke().asc_putLineendsize(record.get("type"));\r\n
            }\r\n
            this._endSizeIdx = record.get("value");\r\n
            this._selectStyleItem(this.btnEndSize, record);\r\n
        },\r\n
        textTop: "Top",\r\n
        textLeft: "Left",\r\n
        textBottom: "Bottom",\r\n
        textRight: "Right",\r\n
        textSize: "Size",\r\n
        textWidth: "Width",\r\n
        textHeight: "Height",\r\n
        textKeepRatio: "Constant Proportions",\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok",\r\n
        textTitle: "Shape - Advanced Settings",\r\n
        strMargins: "Text Padding",\r\n
        textRound: "Round",\r\n
        textMiter: "Miter",\r\n
        textSquare: "Square",\r\n
        textFlat: "Flat",\r\n
        textBevel: "Bevel",\r\n
        textArrows: "Arrows",\r\n
        textLineStyle: "Line Style",\r\n
        textCapType: "Cap Type",\r\n
        textJoinType: "Join Type",\r\n
        textBeginStyle: "Begin Style",\r\n
        textBeginSize: "Begin Size",\r\n
        textEndStyle: "End Style",\r\n
        textEndSize: "End Size",\r\n
        textWeightArrows: "Weights & Arrows"\r\n
    },\r\n
    SSE.Views.ShapeSettingsAdvanced || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>34764</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
