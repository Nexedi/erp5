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
            <value> <string>ts44321339.42</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ShapeSettings.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>127809</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
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
 define(["text!spreadsheeteditor/main/app/template/ShapeSettings.template", "jquery", "underscore", "backbone", "common/main/lib/component/ComboBox", "common/main/lib/component/ComboBorderSize", "common/main/lib/component/MetricSpinner", "common/main/lib/component/ThemeColorPalette", "common/main/lib/component/ColorButton", "common/main/lib/component/ComboDataView", "common/main/lib/component/Slider", "common/main/lib/component/MultiSliderGradient", "common/main/lib/view/ImageFromUrlDialog", "spreadsheeteditor/main/app/view/ShapeSettingsAdvanced"], function (menuTemplate, $, _, Backbone) {\r\n
    SSE.Views.ShapeSettings = Backbone.View.extend(_.extend({\r\n
        el: "#id-shape-settings",\r\n
        template: _.template(menuTemplate),\r\n
        events: {},\r\n
        options: {\r\n
            alias: "ShapeSettings"\r\n
        },\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            this._initSettings = true;\r\n
            this._originalProps = null;\r\n
            this._noApply = true;\r\n
            this.imgprops = null;\r\n
            this._sendUndoPoint = true;\r\n
            this._sliderChanged = false;\r\n
            this._state = {\r\n
                Transparency: null,\r\n
                FillType: c_oAscFill.FILL_TYPE_SOLID,\r\n
                ShapeColor: "transparent",\r\n
                BlipFillType: c_oAscFillBlipType.STRETCH,\r\n
                StrokeType: c_oAscStrokeType.STROKE_COLOR,\r\n
                StrokeWidth: this._pt2mm(1),\r\n
                StrokeColor: "000000",\r\n
                FGColor: "000000",\r\n
                BGColor: "ffffff",\r\n
                GradColor: "000000",\r\n
                GradFillType: c_oAscFillGradType.GRAD_LINEAR,\r\n
                DisabledFillPanels: false,\r\n
                DisabledControls: false,\r\n
                HideShapeOnlySettings: false\r\n
            };\r\n
            this.lockedControls = [];\r\n
            this._locked = false;\r\n
            this.OriginalFillType = c_oAscFill.FILL_TYPE_SOLID;\r\n
            this.ShapeColor = {\r\n
                Value: 1,\r\n
                Color: "transparent"\r\n
            };\r\n
            this.BlipFillType = c_oAscFillBlipType.STRETCH;\r\n
            this.GradFillType = c_oAscFillGradType.GRAD_LINEAR;\r\n
            this.GradColor = {\r\n
                values: [0, 100],\r\n
                colors: ["000000", "ffffff"],\r\n
                currentIdx: 0\r\n
            };\r\n
            this.GradRadialDirectionIdx = 0;\r\n
            this.GradLinearDirectionType = 0;\r\n
            this.PatternFillType = 0;\r\n
            this.FGColor = {\r\n
                Value: 1,\r\n
                Color: "000000"\r\n
            };\r\n
            this.BGColor = {\r\n
                Value: 1,\r\n
                Color: "ffffff"\r\n
            };\r\n
            this.BorderColor = {\r\n
                Value: 1,\r\n
                Color: "transparent"\r\n
            };\r\n
            this.BorderSize = 0;\r\n
            this.textureNames = [this.txtCanvas, this.txtCarton, this.txtDarkFabric, this.txtGrain, this.txtGranite, this.txtGreyPaper, this.txtKnit, this.txtLeather, this.txtBrownPaper, this.txtPapyrus, this.txtWood];\r\n
            this.fillControls = [];\r\n
            this.render();\r\n
            this._arrFillSrc = [{\r\n
                displayValue: this.textColor,\r\n
                value: c_oAscFill.FILL_TYPE_SOLID\r\n
            },\r\n
            {\r\n
                displayValue: this.textGradientFill,\r\n
                value: c_oAscFill.FILL_TYPE_GRAD\r\n
            },\r\n
            {\r\n
                displayValue: this.textImageTexture,\r\n
                value: c_oAscFill.FILL_TYPE_BLIP\r\n
            },\r\n
            {\r\n
                displayValue: this.textPatternFill,\r\n
                value: c_oAscFill.FILL_TYPE_PATT\r\n
            },\r\n
            {\r\n
                displayValue: this.textNoFill,\r\n
                value: c_oAscFill.FILL_TYPE_NOFILL\r\n
            }];\r\n
            this.cmbFillSrc = new Common.UI.ComboBox({\r\n
                el: $("#shape-combo-fill-src"),\r\n
                cls: "input-group-nr",\r\n
                style: "width: 100%;",\r\n
                menuStyle: "min-width: 180px;",\r\n
                editable: false,\r\n
                data: this._arrFillSrc\r\n
            });\r\n
            this.cmbFillSrc.setValue(this._arrFillSrc[0].value);\r\n
            this.cmbFillSrc.on("selected", _.bind(this.onFillSrcSelect, this));\r\n
            this.fillControls.push(this.cmbFillSrc);\r\n
            this.btnBackColor = new Common.UI.ColorButton({\r\n
                style: "width:45px;",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="shape-back-color-menu" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="shape-back-color-new" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnBackColor.on("render:after", function (btn) {\r\n
                me.colorsBack = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#shape-back-color-menu"),\r\n
                    dynamiccolors: 10,\r\n
                    value: "transparent",\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "transparent", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.colorsBack.on("select", _.bind(me.onColorsBackSelect, me));\r\n
            });\r\n
            this.btnBackColor.render($("#shape-back-color-btn"));\r\n
            this.btnBackColor.setColor("transparent");\r\n
            $(this.el).on("click", "#shape-back-color-new", _.bind(this.addNewColor, this, this.colorsBack, this.btnBackColor));\r\n
            this.fillControls.push(this.btnBackColor);\r\n
            this.cmbPattern = new Common.UI.ComboDataView({\r\n
                itemWidth: 28,\r\n
                itemHeight: 28,\r\n
                menuMaxHeight: 300,\r\n
                enableKeyEvents: true,\r\n
                cls: "combo-pattern"\r\n
            });\r\n
            this.cmbPattern.menuPicker.itemTemplate = this.cmbPattern.fieldPicker.itemTemplate = _.template([\'<div class="style" id="<%= id %>">\', \'<img src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" class="combo-pattern-item" \', \'width="\' + this.cmbPattern.itemWidth + \'" height="\' + this.cmbPattern.itemHeight + \'" \', \'style="background-position: -<%= offsetx %>px -<%= offsety %>px;"/>\', "</div>"].join(""));\r\n
            this.cmbPattern.render($("#shape-combo-pattern"));\r\n
            this.cmbPattern.openButton.menu.cmpEl.css({\r\n
                "min-width": 178,\r\n
                "max-width": 178\r\n
            });\r\n
            this.cmbPattern.on("click", _.bind(this.onPatternSelect, this));\r\n
            this.cmbPattern.openButton.menu.on("show:after", function () {\r\n
                me.cmbPattern.menuPicker.scroller.update({\r\n
                    alwaysVisibleY: true\r\n
                });\r\n
            });\r\n
            this.fillControls.push(this.cmbPattern);\r\n
            this.btnFGColor = new Common.UI.ColorButton({\r\n
                style: "width:45px;",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="shape-foreground-color-menu" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="shape-foreground-color-new" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnFGColor.on("render:after", function (btn) {\r\n
                me.colorsFG = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#shape-foreground-color-menu"),\r\n
                    dynamiccolors: 10,\r\n
                    value: "000000",\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "3D55FE", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.colorsFG.on("select", _.bind(me.onColorsFGSelect, me));\r\n
            });\r\n
            this.btnFGColor.render($("#shape-foreground-color-btn"));\r\n
            this.btnFGColor.setColor("000000");\r\n
            $(this.el).on("click", "#shape-foreground-color-new", _.bind(this.addNewColor, this, this.colorsFG, this.btnFGColor));\r\n
            this.fillControls.push(this.btnFGColor);\r\n
            this.btnBGColor = new Common.UI.ColorButton({\r\n
                style: "width:45px;",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="shape-background-color-menu" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="shape-background-color-new" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnBGColor.on("render:after", function (btn) {\r\n
                me.colorsBG = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#shape-background-color-menu"),\r\n
                    dynamiccolors: 10,\r\n
                    value: "ffffff",\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "3D55FE", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.colorsBG.on("select", _.bind(me.onColorsBGSelect, me));\r\n
            });\r\n
            this.btnBGColor.render($("#shape-background-color-btn"));\r\n
            this.btnBGColor.setColor("ffffff");\r\n
            $(this.el).on("click", "#shape-background-color-new", _.bind(this.addNewColor, this, this.colorsBG, this.btnBGColor));\r\n
            this.fillControls.push(this.btnBGColor);\r\n
            this.btnInsertFromFile = new Common.UI.Button({\r\n
                el: $("#shape-button-from-file")\r\n
            });\r\n
            this.fillControls.push(this.btnInsertFromFile);\r\n
            this.btnInsertFromUrl = new Common.UI.Button({\r\n
                el: $("#shape-button-from-url")\r\n
            });\r\n
            this.fillControls.push(this.btnInsertFromUrl);\r\n
            this.btnInsertFromFile.on("click", _.bind(function (btn) {\r\n
                if (this.api) {\r\n
                    this.api.asc_changeShapeImageFromFile();\r\n
                }\r\n
                Common.NotificationCenter.trigger("edit:complete", this);\r\n
            },\r\n
            this));\r\n
            this.btnInsertFromUrl.on("click", _.bind(this.insertFromUrl, this));\r\n
            this._arrFillType = [{\r\n
                displayValue: this.textStretch,\r\n
                value: c_oAscFillBlipType.STRETCH\r\n
            },\r\n
            {\r\n
                displayValue: this.textTile,\r\n
                value: c_oAscFillBlipType.TILE\r\n
            }];\r\n
            this.cmbFillType = new Common.UI.ComboBox({\r\n
                el: $("#shape-combo-fill-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 90px;",\r\n
                editable: false,\r\n
                data: this._arrFillType\r\n
            });\r\n
            this.cmbFillType.setValue(this._arrFillType[0].value);\r\n
            this.cmbFillType.on("selected", _.bind(this.onFillTypeSelect, this));\r\n
            this.fillControls.push(this.cmbFillType);\r\n
            this.btnTexture = new Common.UI.ComboBox({\r\n
                el: $("#shape-combo-fill-texture"),\r\n
                template: _.template([\'<div class="input-group combobox combo-dataview-menu input-group-nr dropdown-toggle" tabindex="0" data-toggle="dropdown">\', \'<div class="form-control text" style="width: 90px;">\' + this.textSelectTexture + "</div>", \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default"><span class="caret"></span></button>\', "</div>"].join(""))\r\n
            });\r\n
            this.textureMenu = new Common.UI.Menu({\r\n
                items: [{\r\n
                    template: _.template(\'<div id="id-shape-menu-texture" style="width: 233px; margin: 0 5px;"></div>\')\r\n
                }]\r\n
            });\r\n
            this.textureMenu.render($("#shape-combo-fill-texture"));\r\n
            this.fillControls.push(this.btnTexture);\r\n
            this.numTransparency = new Common.UI.MetricSpinner({\r\n
                el: $("#shape-spin-transparency"),\r\n
                step: 1,\r\n
                width: 60,\r\n
                value: "100 %",\r\n
                defaultUnit: "%",\r\n
                maxValue: 100,\r\n
                minValue: 0\r\n
            });\r\n
            this.numTransparency.on("change", _.bind(this.onNumTransparencyChange, this));\r\n
            this.fillControls.push(this.numTransparency);\r\n
            this.sldrTransparency = new Common.UI.SingleSlider({\r\n
                el: $("#shape-slider-transparency"),\r\n
                width: 75,\r\n
                minValue: 0,\r\n
                maxValue: 100,\r\n
                value: 100\r\n
            });\r\n
            this.sldrTransparency.on("change", _.bind(this.onTransparencyChange, this));\r\n
            this.sldrTransparency.on("changecomplete", _.bind(this.onTransparencyChangeComplete, this));\r\n
            this.fillControls.push(this.sldrTransparency);\r\n
            this.lblTransparencyStart = $(this.el).find("#shape-lbl-transparency-start");\r\n
            this.lblTransparencyEnd = $(this.el).find("#shape-lbl-transparency-end");\r\n
            this._arrGradType = [{\r\n
                displayValue: this.textLinear,\r\n
                value: c_oAscFillGradType.GRAD_LINEAR\r\n
            },\r\n
            {\r\n
                displayValue: this.textRadial,\r\n
                value: c_oAscFillGradType.GRAD_PATH\r\n
            }];\r\n
            this.cmbGradType = new Common.UI.ComboBox({\r\n
                el: $("#shape-combo-grad-type"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 90px;",\r\n
                editable: false,\r\n
                data: this._arrGradType\r\n
            });\r\n
            this.cmbGradType.setValue(this._arrGradType[0].value);\r\n
            this.cmbGradType.on("selected", _.bind(this.onGradTypeSelect, this));\r\n
            this.fillControls.push(this.cmbGradType);\r\n
            this._viewDataLinear = [{\r\n
                offsetx: 0,\r\n
                offsety: 0,\r\n
                type: 45,\r\n
                subtype: -1,\r\n
                iconcls: "gradient-left-top"\r\n
            },\r\n
            {\r\n
                offsetx: 50,\r\n
                offsety: 0,\r\n
                type: 90,\r\n
                subtype: 4,\r\n
                iconcls: "gradient-top"\r\n
            },\r\n
            {\r\n
                offsetx: 100,\r\n
                offsety: 0,\r\n
                type: 135,\r\n
                subtype: 5,\r\n
                iconcls: "gradient-right-top"\r\n
            },\r\n
            {\r\n
                offsetx: 0,\r\n
                offsety: 50,\r\n
                type: 0,\r\n
                subtype: 6,\r\n
                iconcls: "gradient-left",\r\n
                cls: "item-gradient-separator",\r\n
                selected: true\r\n
            },\r\n
            {\r\n
                offsetx: 100,\r\n
                offsety: 50,\r\n
                type: 180,\r\n
                subtype: 1,\r\n
                iconcls: "gradient-right"\r\n
            },\r\n
            {\r\n
                offsetx: 0,\r\n
                offsety: 100,\r\n
                type: 315,\r\n
                subtype: 2,\r\n
                iconcls: "gradient-left-bottom"\r\n
            },\r\n
            {\r\n
                offsetx: 50,\r\n
                offsety: 100,\r\n
                type: 270,\r\n
                subtype: 3,\r\n
                iconcls: "gradient-bottom"\r\n
            },\r\n
            {\r\n
                offsetx: 100,\r\n
                offsety: 100,\r\n
                type: 225,\r\n
                subtype: 7,\r\n
                iconcls: "gradient-right-bottom"\r\n
            }];\r\n
            this._viewDataRadial = [{\r\n
                offsetx: 100,\r\n
                offsety: 150,\r\n
                type: 2,\r\n
                subtype: 5,\r\n
                iconcls: "gradient-radial-center"\r\n
            }];\r\n
            this.btnDirection = new Common.UI.Button({\r\n
                cls: "btn-large-dataview",\r\n
                iconCls: "item-gradient gradient-left",\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "min-width: 60px;",\r\n
                    menuAlign: "tr-br",\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-shape-menu-direction" style="width: 175px; margin: 0 5px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnDirection.on("render:after", function (btn) {\r\n
                me.mnuDirectionPicker = new Common.UI.DataView({\r\n
                    el: $("#id-shape-menu-direction"),\r\n
                    parentMenu: btn.menu,\r\n
                    restoreHeight: 174,\r\n
                    store: new Common.UI.DataViewStore(me._viewDataLinear),\r\n
                    itemTemplate: _.template(\'<div id="<%= id %>" class="item-gradient" style="background-position: -<%= offsetx %>px -<%= offsety %>px;"></div>\')\r\n
                });\r\n
            });\r\n
            this.btnDirection.render($("#shape-button-direction"));\r\n
            this.mnuDirectionPicker.on("item:click", _.bind(this.onSelectGradient, this, this.btnDirection));\r\n
            this.fillControls.push(this.btnDirection);\r\n
            this.btnGradColor = new Common.UI.ColorButton({\r\n
                style: "width:45px;",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="shape-gradient-color-menu" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="shape-gradient-color-new" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnGradColor.on("render:after", function (btn) {\r\n
                me.colorsGrad = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#shape-gradient-color-menu"),\r\n
                    dynamiccolors: 10,\r\n
                    value: "000000",\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "3D55FE", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.colorsGrad.on("select", _.bind(me.onColorsGradientSelect, me));\r\n
            });\r\n
            this.btnGradColor.render($("#shape-gradient-color-btn"));\r\n
            this.btnGradColor.setColor("000000");\r\n
            $(this.el).on("click", "#shape-gradient-color-new", _.bind(this.addNewColor, this, this.colorsGrad, this.btnGradColor));\r\n
            this.fillControls.push(this.btnGradColor);\r\n
            this.sldrGradient = new Common.UI.MultiSliderGradient({\r\n
                el: $("#shape-slider-gradient"),\r\n
                width: 125,\r\n
                minValue: 0,\r\n
                maxValue: 100,\r\n
                values: [0, 100]\r\n
            });\r\n
            this.sldrGradient.on("change", _.bind(this.onGradientChange, this));\r\n
            this.sldrGradient.on("changecomplete", _.bind(this.onGradientChangeComplete, this));\r\n
            this.sldrGradient.on("thumbclick", function (cmp, index) {\r\n
                me.GradColor.currentIdx = index;\r\n
                var color = me.GradColor.colors[me.GradColor.currentIdx];\r\n
                me.btnGradColor.setColor(color);\r\n
                me.colorsGrad.select(color, false);\r\n
            });\r\n
            this.sldrGradient.on("thumbdblclick", function (cmp) {\r\n
                me.btnGradColor.cmpEl.find("button").dropdown("toggle");\r\n
            });\r\n
            this.fillControls.push(this.sldrGradient);\r\n
            this.cmbBorderSize = new Common.UI.ComboBorderSizeEditable({\r\n
                el: $("#shape-combo-border-size"),\r\n
                style: "width: 93px;",\r\n
                txtNoBorders: this.txtNoBorders\r\n
            }).on("selected", _.bind(this.onBorderSizeSelect, this)).on("changed:before", _.bind(this.onBorderSizeChanged, this, true)).on("changed:after", _.bind(this.onBorderSizeChanged, this, false)).on("combo:blur", _.bind(this.onComboBlur, this, false));\r\n
            this.BorderSize = this.cmbBorderSize.store.at(2).get("value");\r\n
            this.cmbBorderSize.setValue(this.BorderSize);\r\n
            this.lockedControls.push(this.cmbBorderSize);\r\n
            this.btnBorderColor = new Common.UI.ColorButton({\r\n
                style: "width:45px;",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="shape-border-color-menu" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="shape-border-color-new" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            });\r\n
            this.btnBorderColor.on("render:after", function (btn) {\r\n
                me.colorsBorder = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#shape-border-color-menu"),\r\n
                    dynamiccolors: 10,\r\n
                    value: "000000",\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "3D55FE", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.colorsBorder.on("select", _.bind(me.onColorsBorderSelect, me));\r\n
            });\r\n
            this.btnBorderColor.render($("#shape-border-color-btn"));\r\n
            this.btnBorderColor.setColor("000000");\r\n
            $(this.el).on("click", "#shape-border-color-new", _.bind(this.addNewColor, this, this.colorsBorder, this.btnBorderColor));\r\n
            this.lockedControls.push(this.btnBorderColor);\r\n
            this.btnChangeShape = new Common.UI.Button({\r\n
                cls: "btn-icon-default",\r\n
                iconCls: "btn-change-shape",\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tr-br",\r\n
                    cls: "menu-shapes",\r\n
                    items: []\r\n
                })\r\n
            });\r\n
            this.btnChangeShape.render($("#shape-btn-change"));\r\n
            this.lockedControls.push(this.btnChangeShape);\r\n
            $(this.el).on("click", "#shape-advanced-link", _.bind(this.openAdvancedSettings, this));\r\n
            this.FillColorContainer = $("#shape-panel-color-fill");\r\n
            this.FillImageContainer = $("#shape-panel-image-fill");\r\n
            this.FillPatternContainer = $("#shape-panel-pattern-fill");\r\n
            this.FillGradientContainer = $("#shape-panel-gradient-fill");\r\n
            this.TransparencyContainer = $("#shape-panel-transparent-fill");\r\n
            this.ShapeOnlySettings = $(".shape-only");\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.linkAdvanced = $("#shape-advanced-link");\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            if (this.api) {\r\n
                this.api.asc_setInterfaceDrawImagePlaceShape("shape-texture-img");\r\n
                this.api.asc_registerCallback("asc_onInitStandartTextures", _.bind(this.onInitStandartTextures, this));\r\n
            }\r\n
            return this;\r\n
        },\r\n
        onFillSrcSelect: function (combo, record) {\r\n
            this.ShowHideElem(record.value);\r\n
            switch (record.value) {\r\n
            case c_oAscFill.FILL_TYPE_SOLID:\r\n
                this._state.FillType = c_oAscFill.FILL_TYPE_SOLID;\r\n
                if (!this._noApply) {\r\n
                    var props = new Asc.asc_CShapeProperty();\r\n
                    var fill = new Asc.asc_CShapeFill();\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_SOLID);\r\n
                    fill.asc_putFill(new Asc.asc_CFillSolid());\r\n
                    fill.asc_getFill().asc_putColor(Common.Utils.ThemeColor.getRgbColor((this.ShapeColor.Color == "transparent") ? {\r\n
                        color: "4f81bd",\r\n
                        effectId: 24\r\n
                    } : this.ShapeColor.Color));\r\n
                    props.asc_putFill(fill);\r\n
                    this.imgprops.asc_putShapeProperties(props);\r\n
                    this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                }\r\n
                break;\r\n
            case c_oAscFill.FILL_TYPE_GRAD:\r\n
                this._state.FillType = c_oAscFill.FILL_TYPE_GRAD;\r\n
                if (!this._noApply) {\r\n
                    var props = new Asc.asc_CShapeProperty();\r\n
                    var fill = new Asc.asc_CShapeFill();\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_GRAD);\r\n
                    fill.asc_putFill(new Asc.asc_CFillGrad());\r\n
                    fill.asc_getFill().asc_putGradType(this.GradFillType);\r\n
                    if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                        fill.asc_getFill().asc_putLinearAngle(this.GradLinearDirectionType * 60000);\r\n
                        fill.asc_getFill().asc_putLinearScale(true);\r\n
                    }\r\n
                    if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_GRAD) {\r\n
                        fill.asc_getFill().asc_putPositions([this.GradColor.values[0] * 1000, this.GradColor.values[1] * 1000]);\r\n
                        fill.asc_getFill().asc_putColors([Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[0]), Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[1])]);\r\n
                    }\r\n
                    props.asc_putFill(fill);\r\n
                    this.imgprops.asc_putShapeProperties(props);\r\n
                    this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                }\r\n
                break;\r\n
            case c_oAscFill.FILL_TYPE_BLIP:\r\n
                this._state.FillType = c_oAscFill.FILL_TYPE_BLIP;\r\n
                break;\r\n
            case c_oAscFill.FILL_TYPE_PATT:\r\n
                this._state.FillType = c_oAscFill.FILL_TYPE_PATT;\r\n
                if (!this._noApply) {\r\n
                    var props = new Asc.asc_CShapeProperty();\r\n
                    var fill = new Asc.asc_CShapeFill();\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_PATT);\r\n
                    fill.asc_putFill(new Asc.asc_CFillHatch());\r\n
                    fill.asc_getFill().asc_putPatternType(this.PatternFillType);\r\n
                    var fHexColor = Common.Utils.ThemeColor.getRgbColor(this.FGColor.Color).get_color().get_hex();\r\n
                    var bHexColor = Common.Utils.ThemeColor.getRgbColor(this.BGColor.Color).get_color().get_hex();\r\n
                    if (bHexColor === "ffffff" && fHexColor === "ffffff") {\r\n
                        fHexColor = {\r\n
                            color: "4f81bd",\r\n
                            effectId: 24\r\n
                        };\r\n
                    } else {\r\n
                        fHexColor = this.FGColor.Color;\r\n
                    }\r\n
                    fill.asc_getFill().asc_putColorFg(Common.Utils.ThemeColor.getRgbColor(fHexColor));\r\n
                    fill.asc_getFill().asc_putColorBg(Common.Utils.ThemeColor.getRgbColor(this.BGColor.Color));\r\n
                    props.asc_putFill(fill);\r\n
                    this.imgprops.asc_putShapeProperties(props);\r\n
                    this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                }\r\n
                break;\r\n
            case c_oAscFill.FILL_TYPE_NOFILL:\r\n
                this._state.FillType = c_oAscFill.FILL_TYPE_NOFILL;\r\n
                if (!this._noApply) {\r\n
                    var props = new Asc.asc_CShapeProperty();\r\n
                    var fill = new Asc.asc_CShapeFill();\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_NOFILL);\r\n
                    fill.asc_putFill(null);\r\n
                    props.asc_putFill(fill);\r\n
                    this.imgprops.asc_putShapeProperties(props);\r\n
                    this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                }\r\n
                break;\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onColorsBackSelect: function (picker, color) {\r\n
            this.btnBackColor.setColor(color);\r\n
            this.ShapeColor = {\r\n
                Value: 1,\r\n
                Color: color\r\n
            };\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                if (this.ShapeColor.Color == "transparent") {\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_NOFILL);\r\n
                    fill.asc_putFill(null);\r\n
                } else {\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_SOLID);\r\n
                    fill.asc_putFill(new Asc.asc_CFillSolid());\r\n
                    fill.asc_getFill().asc_putColor(Common.Utils.ThemeColor.getRgbColor(this.ShapeColor.Color));\r\n
                }\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        addNewColor: function (picker, btn) {\r\n
            picker.addNewColor((typeof(btn.color) == "object") ? btn.color.color : btn.color);\r\n
        },\r\n
        onPatternSelect: function (combo, record) {\r\n
            if (this.api && !this._noApply) {\r\n
                this.PatternFillType = record.get("type");\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_PATT);\r\n
                fill.asc_putFill(new Asc.asc_CFillHatch());\r\n
                fill.asc_getFill().asc_putPatternType(this.PatternFillType);\r\n
                if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_PATT) {\r\n
                    fill.asc_getFill().asc_putColorFg(Common.Utils.ThemeColor.getRgbColor(this.FGColor.Color));\r\n
                    fill.asc_getFill().asc_putColorBg(Common.Utils.ThemeColor.getRgbColor(this.BGColor.Color));\r\n
                }\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onColorsFGSelect: function (picker, color) {\r\n
            this.btnFGColor.setColor(color);\r\n
            this.FGColor = {\r\n
                Value: 1,\r\n
                Color: color\r\n
            };\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_PATT);\r\n
                fill.asc_putFill(new Asc.asc_CFillHatch());\r\n
                fill.asc_getFill().asc_putColorFg(Common.Utils.ThemeColor.getRgbColor(this.FGColor.Color));\r\n
                if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_PATT) {\r\n
                    fill.asc_getFill().asc_putPatternType(this.PatternFillType);\r\n
                    fill.asc_getFill().asc_putColorBg(Common.Utils.ThemeColor.getRgbColor(this.BGColor.Color));\r\n
                }\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onColorsBGSelect: function (picker, color) {\r\n
            this.btnBGColor.setColor(color);\r\n
            this.BGColor = {\r\n
                Value: 1,\r\n
                Color: color\r\n
            };\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_PATT);\r\n
                fill.asc_putFill(new Asc.asc_CFillHatch());\r\n
                if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_PATT) {\r\n
                    fill.asc_getFill().asc_putPatternType(this.PatternFillType);\r\n
                    fill.asc_getFill().asc_putColorFg(Common.Utils.ThemeColor.getRgbColor(this.FGColor.Color));\r\n
                }\r\n
                fill.asc_getFill().asc_putColorBg(Common.Utils.ThemeColor.getRgbColor(this.BGColor.Color));\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onFillTypeSelect: function (combo, record) {\r\n
            this.BlipFillType = record.value;\r\n
            if (this.api && this._fromTextureCmb !== true && this.OriginalFillType == c_oAscFill.FILL_TYPE_BLIP) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_BLIP);\r\n
                fill.asc_putFill(new Asc.asc_CFillBlip());\r\n
                fill.asc_getFill().asc_putType(this.BlipFillType);\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onNumTransparencyChange: function (field, newValue, oldValue, eOpts) {\r\n
            this.sldrTransparency.setValue(field.getNumberValue(), true);\r\n
            if (this.api) {\r\n
                var num = field.getNumberValue();\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putTransparent(num * 2.55);\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onTransparencyChange: function (field, newValue, oldValue) {\r\n
            this._sliderChanged = newValue;\r\n
            this.numTransparency.setValue(newValue, true);\r\n
            if (this._sendUndoPoint) {\r\n
                this.api.setStartPointHistory();\r\n
                this._sendUndoPoint = false;\r\n
                this.updateslider = setInterval(_.bind(this._transparencyApplyFunc, this), 100);\r\n
            }\r\n
        },\r\n
        onTransparencyChangeComplete: function (field, newValue, oldValue) {\r\n
            clearInterval(this.updateslider);\r\n
            this._sliderChanged = newValue;\r\n
            this.api.setEndPointHistory();\r\n
            this._transparencyApplyFunc();\r\n
            this._sendUndoPoint = true;\r\n
        },\r\n
        _transparencyApplyFunc: function () {\r\n
            if (this._sliderChanged !== undefined) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putTransparent(this._sliderChanged * 2.55);\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                this._sliderChanged = undefined;\r\n
            }\r\n
        },\r\n
        onGradTypeSelect: function (combo, record) {\r\n
            this.GradFillType = record.value;\r\n
            if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                this.mnuDirectionPicker.store.reset(this._viewDataLinear);\r\n
                this.mnuDirectionPicker.cmpEl.width(175);\r\n
                this.mnuDirectionPicker.restoreHeight = 174;\r\n
                var record = this.mnuDirectionPicker.store.findWhere({\r\n
                    type: this.GradLinearDirectionType\r\n
                });\r\n
                this.mnuDirectionPicker.selectRecord(record, true);\r\n
                if (record) {\r\n
                    this.btnDirection.setIconCls("item-gradient " + record.get("iconcls"));\r\n
                } else {\r\n
                    this.btnDirection.setIconCls("");\r\n
                }\r\n
            } else {\r\n
                if (this.GradFillType == c_oAscFillGradType.GRAD_PATH) {\r\n
                    this.mnuDirectionPicker.store.reset(this._viewDataRadial);\r\n
                    this.mnuDirectionPicker.cmpEl.width(60);\r\n
                    this.mnuDirectionPicker.restoreHeight = 58;\r\n
                    this.mnuDirectionPicker.selectByIndex(this.GradRadialDirectionIdx, true);\r\n
                    if (this.GradRadialDirectionIdx >= 0) {\r\n
                        this.btnDirection.setIconCls("item-gradient " + this._viewDataRadial[this.GradRadialDirectionIdx].iconcls);\r\n
                    } else {\r\n
                        this.btnDirection.setIconCls("");\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_GRAD);\r\n
                fill.asc_putFill(new Asc.asc_CFillGrad());\r\n
                fill.asc_getFill().asc_putGradType(this.GradFillType);\r\n
                if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                    fill.asc_getFill().asc_putLinearAngle(this.GradLinearDirectionType * 60000);\r\n
                    fill.asc_getFill().asc_putLinearScale(true);\r\n
                }\r\n
                fill.asc_getFill().asc_putPositions([this.GradColor.values[0] * 1000, this.GradColor.values[1] * 1000]);\r\n
                fill.asc_getFill().asc_putColors([Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[0]), Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[1])]);\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onSelectGradient: function (btn, picker, itemView, record) {\r\n
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
            this.btnDirection.setIconCls("item-gradient " + rawData.iconcls);\r\n
            (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) ? this.GradLinearDirectionType = rawData.type : this.GradRadialDirectionIdx = 0;\r\n
            if (this.api) {\r\n
                if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                    var props = new Asc.asc_CShapeProperty();\r\n
                    var fill = new Asc.asc_CShapeFill();\r\n
                    fill.asc_putType(c_oAscFill.FILL_TYPE_GRAD);\r\n
                    fill.asc_putFill(new Asc.asc_CFillGrad());\r\n
                    fill.asc_getFill().asc_putGradType(this.GradFillType);\r\n
                    fill.asc_getFill().asc_putLinearAngle(rawData.type * 60000);\r\n
                    fill.asc_getFill().asc_putLinearScale(true);\r\n
                    if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_GRAD) {\r\n
                        fill.asc_getFill().asc_putPositions([this.GradColor.values[0] * 1000, this.GradColor.values[1] * 1000]);\r\n
                        fill.asc_getFill().asc_putColors([Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[0]), Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[1])]);\r\n
                    }\r\n
                    props.asc_putFill(fill);\r\n
                    this.imgprops.asc_putShapeProperties(props);\r\n
                    this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onColorsGradientSelect: function (picker, color) {\r\n
            this.btnGradColor.setColor(color);\r\n
            this.GradColor.colors[this.GradColor.currentIdx] = color;\r\n
            this.sldrGradient.setColorValue(Common.Utils.String.format("#{0}", (typeof(color) == "object") ? color.color : color));\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_GRAD);\r\n
                fill.asc_putFill(new Asc.asc_CFillGrad());\r\n
                fill.asc_getFill().asc_putGradType(this.GradFillType);\r\n
                fill.asc_getFill().asc_putColors([Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[0]), Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[1])]);\r\n
                if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_GRAD) {\r\n
                    if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                        fill.asc_getFill().asc_putLinearAngle(this.GradLinearDirectionType * 60000);\r\n
                        fill.asc_getFill().asc_putLinearScale(true);\r\n
                    }\r\n
                    fill.asc_getFill().asc_putPositions([this.GradColor.values[0] * 1000, this.GradColor.values[1] * 1000]);\r\n
                }\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onGradientChange: function (slider, newValue, oldValue) {\r\n
            this.GradColor.values = slider.getValues();\r\n
            this._sliderChanged = true;\r\n
            if (this.api && !this._noApply) {\r\n
                if (this._sendUndoPoint) {\r\n
                    this.api.setStartPointHistory();\r\n
                    this._sendUndoPoint = false;\r\n
                    this.updateslider = setInterval(_.bind(this._gradientApplyFunc, this), 100);\r\n
                }\r\n
            }\r\n
        },\r\n
        onGradientChangeComplete: function (slider, newValue, oldValue) {\r\n
            clearInterval(this.updateslider);\r\n
            this._sliderChanged = true;\r\n
            this.api.setEndPointHistory();\r\n
            this._gradientApplyFunc();\r\n
            this._sendUndoPoint = true;\r\n
        },\r\n
        _gradientApplyFunc: function () {\r\n
            if (this._sliderChanged) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_GRAD);\r\n
                fill.asc_putFill(new Asc.asc_CFillGrad());\r\n
                fill.asc_getFill().asc_putGradType(this.GradFillType);\r\n
                fill.asc_getFill().asc_putPositions([this.GradColor.values[0] * 1000, this.GradColor.values[1] * 1000]);\r\n
                if (this.OriginalFillType !== c_oAscFill.FILL_TYPE_GRAD) {\r\n
                    if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                        fill.asc_getFill().asc_putLinearAngle(this.GradLinearDirectionType * 60000);\r\n
                        fill.asc_getFill().asc_putLinearScale(true);\r\n
                    }\r\n
                    fill.asc_getFill().asc_putColors([Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[0]), Common.Utils.ThemeColor.getRgbColor(this.GradColor.colors[1])]);\r\n
                }\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                this._sliderChanged = false;\r\n
            }\r\n
        },\r\n
        applyBorderSize: function (value) {\r\n
            value = parseFloat(value);\r\n
            value = isNaN(value) ? 0 : Math.max(0, Math.min(1584, value));\r\n
            this.BorderSize = value;\r\n
            if (this.api && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var stroke = new Asc.asc_CStroke();\r\n
                if (this.BorderSize < 0.01) {\r\n
                    stroke.asc_putType(c_oAscStrokeType.STROKE_NONE);\r\n
                    this._state.StrokeType = this._state.StrokeWidth = -1;\r\n
                } else {\r\n
                    stroke.asc_putType(c_oAscStrokeType.STROKE_COLOR);\r\n
                    if (this.BorderColor.Color == "transparent" || this.BorderColor.Color.color == "transparent") {\r\n
                        stroke.asc_putColor(Common.Utils.ThemeColor.getRgbColor({\r\n
                            color: "000000",\r\n
                            effectId: 29\r\n
                        }));\r\n
                    } else {\r\n
                        if (this._state.StrokeType == c_oAscStrokeType.STROKE_NONE || this._state.StrokeType === null) {\r\n
                            stroke.asc_putColor(Common.Utils.ThemeColor.getRgbColor(Common.Utils.ThemeColor.colorValue2EffectId(this.BorderColor.Color)));\r\n
                        }\r\n
                    }\r\n
                    stroke.asc_putWidth(this._pt2mm(this.BorderSize));\r\n
                }\r\n
                props.asc_putStroke(stroke);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
                Common.NotificationCenter.trigger("edit:complete", this);\r\n
            }\r\n
        },\r\n
        onComboBlur: function () {\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onBorderSizeChanged: function (before, combo, record, e) {\r\n
            var me = this;\r\n
            if (before) {\r\n
                var value = parseFloat(record.value);\r\n
                if (! (/^\\s*(\\d*(\\.|,)?\\d+)\\s*(pt)?\\s*$/.exec(record.value)) || value < 0 || value > 1584) {\r\n
                    this._state.StrokeType = this._state.StrokeWidth = -1;\r\n
                    Common.UI.error({\r\n
                        msg: this.textBorderSizeErr,\r\n
                        callback: function () {\r\n
                            _.defer(function (btn) {\r\n
                                Common.NotificationCenter.trigger("edit:complete", me);\r\n
                            });\r\n
                        }\r\n
                    });\r\n
                }\r\n
            } else {\r\n
                this.applyBorderSize(record.value);\r\n
            }\r\n
        },\r\n
        onBorderSizeSelect: function (combo, record) {\r\n
            this.applyBorderSize(record.value);\r\n
        },\r\n
        onColorsBorderSelect: function (picker, color) {\r\n
            this.btnBorderColor.setColor(color);\r\n
            this.BorderColor = {\r\n
                Value: 1,\r\n
                Color: color\r\n
            };\r\n
            if (this.api && this.BorderSize > 0 && !this._noApply) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var stroke = new Asc.asc_CStroke();\r\n
                if (this.BorderSize < 0.01) {\r\n
                    stroke.asc_putType(c_oAscStrokeType.STROKE_NONE);\r\n
                } else {\r\n
                    stroke.asc_putType(c_oAscStrokeType.STROKE_COLOR);\r\n
                    stroke.asc_putColor(Common.Utils.ThemeColor.getRgbColor(this.BorderColor.Color));\r\n
                    stroke.asc_putWidth(this._pt2mm(this.BorderSize));\r\n
                }\r\n
                props.asc_putStroke(stroke);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        insertFromUrl: function () {\r\n
            var me = this;\r\n
            (new Common.Views.ImageFromUrlDialog({\r\n
                handler: function (result, value) {\r\n
                    if (result == "ok") {\r\n
                        if (me.api) {\r\n
                            var checkUrl = value.replace(/ /g, "");\r\n
                            if (!_.isEmpty(checkUrl)) {\r\n
                                if (me.BlipFillType !== null) {\r\n
                                    var props = new Asc.asc_CShapeProperty();\r\n
                                    var fill = new Asc.asc_CShapeFill();\r\n
                                    fill.asc_putType(c_oAscFill.FILL_TYPE_BLIP);\r\n
                                    fill.asc_putFill(new Asc.asc_CFillBlip());\r\n
                                    fill.asc_getFill().asc_putType(me.BlipFillType);\r\n
                                    fill.asc_getFill().asc_putUrl(checkUrl);\r\n
                                    props.asc_putFill(fill);\r\n
                                    me.imgprops.asc_putShapeProperties(props);\r\n
                                    me.api.asc_setGraphicObjectProps(me.imgprops);\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me);\r\n
                }\r\n
            })).show();\r\n
        },\r\n
        openAdvancedSettings: function (e) {\r\n
            if (this.linkAdvanced.hasClass("disabled")) {\r\n
                return;\r\n
            }\r\n
            var me = this;\r\n
            var win;\r\n
            if (me.api && !this._locked) {\r\n
                var selectedElements = me.api.asc_getGraphicObjectProps();\r\n
                if (selectedElements && selectedElements.length > 0) {\r\n
                    var elType, elValue;\r\n
                    for (var i = selectedElements.length - 1; i >= 0; i--) {\r\n
                        elType = selectedElements[i].asc_getObjectType();\r\n
                        if (c_oAscTypeSelectElement.Image == elType) {\r\n
                            elValue = selectedElements[i].asc_getObjectValue();\r\n
                            (new SSE.Views.ShapeSettingsAdvanced({\r\n
                                shapeProps: elValue,\r\n
                                handler: function (result, value) {\r\n
                                    if (result == "ok") {\r\n
                                        if (me.api) {\r\n
                                            me.api.asc_setGraphicObjectProps(value.shapeProps);\r\n
                                        }\r\n
                                    }\r\n
                                    Common.NotificationCenter.trigger("edit:complete", me);\r\n
                                }\r\n
                            })).show();\r\n
                            break;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        ChangeSettings: function (props) {\r\n
            if (this._initSettings) {\r\n
                this.createDelayedElements();\r\n
            }\r\n
            this._initSettings = false;\r\n
            if (this.imgprops == null) {\r\n
                this.imgprops = new Asc.asc_CImgProperty();\r\n
            }\r\n
            if (props && props.asc_getShapeProperties()) {\r\n
                var shapeprops = props.asc_getShapeProperties();\r\n
                this._originalProps = shapeprops;\r\n
                this._noApply = true;\r\n
                this.disableControls(this._locked, !shapeprops.asc_getCanFill());\r\n
                this.hideShapeOnlySettings(shapeprops.asc_getFromChart());\r\n
                var rec = null;\r\n
                var fill = shapeprops.asc_getFill();\r\n
                var fill_type = fill.asc_getType();\r\n
                var color = null;\r\n
                var transparency = fill.asc_getTransparent();\r\n
                if (Math.abs(this._state.Transparency - transparency) > 0.001 || Math.abs(this.numTransparency.getNumberValue() - transparency) > 0.001 || (this._state.Transparency === null || transparency === null) && (this._state.Transparency !== transparency || this.numTransparency.getNumberValue() !== transparency)) {\r\n
                    if (transparency !== undefined) {\r\n
                        this.sldrTransparency.setValue((transparency === null) ? 100 : transparency / 255 * 100, true);\r\n
                        this.numTransparency.setValue(this.sldrTransparency.getValue(), true);\r\n
                    }\r\n
                    this._state.Transparency = transparency;\r\n
                }\r\n
                if (fill === null || fill_type === null) {\r\n
                    this.OriginalFillType = null;\r\n
                } else {\r\n
                    if (fill_type == c_oAscFill.FILL_TYPE_NOFILL) {\r\n
                        this.OriginalFillType = c_oAscFill.FILL_TYPE_NOFILL;\r\n
                    } else {\r\n
                        if (fill_type == c_oAscFill.FILL_TYPE_SOLID) {\r\n
                            fill = fill.asc_getFill();\r\n
                            color = fill.asc_getColor();\r\n
                            if (color) {\r\n
                                if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                    this.ShapeColor = {\r\n
                                        Value: 1,\r\n
                                        Color: {\r\n
                                            color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                            effectValue: color.asc_getValue()\r\n
                                        }\r\n
                                    };\r\n
                                } else {\r\n
                                    this.ShapeColor = {\r\n
                                        Value: 1,\r\n
                                        Color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB())\r\n
                                    };\r\n
                                }\r\n
                            } else {\r\n
                                this.ShapeColor = {\r\n
                                    Value: 0,\r\n
                                    Color: "transparent"\r\n
                                };\r\n
                            }\r\n
                            this.OriginalFillType = c_oAscFill.FILL_TYPE_SOLID;\r\n
                            this.FGColor = (this.ShapeColor.Color !== "transparent") ? {\r\n
                                Value: 1,\r\n
                                Color: Common.Utils.ThemeColor.colorValue2EffectId(this.ShapeColor.Color)\r\n
                            } : {\r\n
                                Value: 1,\r\n
                                Color: "000000"\r\n
                            };\r\n
                            this.BGColor = {\r\n
                                Value: 1,\r\n
                                Color: "ffffff"\r\n
                            };\r\n
                        } else {\r\n
                            if (fill_type == c_oAscFill.FILL_TYPE_BLIP) {\r\n
                                fill = fill.asc_getFill();\r\n
                                this.BlipFillType = fill.asc_getType();\r\n
                                if (this._state.BlipFillType !== this.BlipFillType) {\r\n
                                    if (this.BlipFillType == c_oAscFillBlipType.STRETCH || this.BlipFillType == c_oAscFillBlipType.TILE) {\r\n
                                        this.cmbFillType.setValue(this.BlipFillType);\r\n
                                    } else {\r\n
                                        this.cmbFillType.setValue("");\r\n
                                    }\r\n
                                    this._state.BlipFillType = this.BlipFillType;\r\n
                                }\r\n
                                this.OriginalFillType = c_oAscFill.FILL_TYPE_BLIP;\r\n
                            } else {\r\n
                                if (fill_type == c_oAscFill.FILL_TYPE_PATT) {\r\n
                                    fill = fill.asc_getFill();\r\n
                                    this.PatternFillType = fill.asc_getPatternType();\r\n
                                    if (this._state.PatternFillType !== this.PatternFillType) {\r\n
                                        this.cmbPattern.suspendEvents();\r\n
                                        var rec = this.cmbPattern.menuPicker.store.findWhere({\r\n
                                            type: this.PatternFillType\r\n
                                        });\r\n
                                        this.cmbPattern.menuPicker.selectRecord(rec);\r\n
                                        this.cmbPattern.resumeEvents();\r\n
                                        this._state.PatternFillType = this.PatternFillType;\r\n
                                    }\r\n
                                    color = fill.asc_getColorFg();\r\n
                                    if (color) {\r\n
                                        if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                            this.FGColor = {\r\n
                                                Value: 1,\r\n
                                                Color: {\r\n
                                                    color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                                    effectValue: color.asc_getValue()\r\n
                                                }\r\n
                                            };\r\n
                                        } else {\r\n
                                            this.FGColor = {\r\n
                                                Value: 1,\r\n
                                                Color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB())\r\n
                                            };\r\n
                                        }\r\n
                                    } else {\r\n
                                        this.FGColor = {\r\n
                                            Value: 1,\r\n
                                            Color: "000000"\r\n
                                        };\r\n
                                    }\r\n
                                    color = fill.asc_getColorBg();\r\n
                                    if (color) {\r\n
                                        if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                            this.BGColor = {\r\n
                                                Value: 1,\r\n
                                                Color: {\r\n
                                                    color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                                    effectValue: color.asc_getValue()\r\n
                                                }\r\n
                                            };\r\n
                                        } else {\r\n
                                            this.BGColor = {\r\n
                                                Value: 1,\r\n
                                                Color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB())\r\n
                                            };\r\n
                                        }\r\n
                                    } else {\r\n
                                        this.BGColor = {\r\n
                                            Value: 1,\r\n
                                            Color: "ffffff"\r\n
                                        };\r\n
                                    }\r\n
                                    this.OriginalFillType = c_oAscFill.FILL_TYPE_PATT;\r\n
                                    this.ShapeColor = (this.FGColor.Color !== "transparent") ? {\r\n
                                        Value: 1,\r\n
                                        Color: Common.Utils.ThemeColor.colorValue2EffectId(this.FGColor.Color)\r\n
                                    } : {\r\n
                                        Value: 1,\r\n
                                        Color: "ffffff"\r\n
                                    };\r\n
                                } else {\r\n
                                    if (fill_type == c_oAscFill.FILL_TYPE_GRAD) {\r\n
                                        fill = fill.asc_getFill();\r\n
                                        var gradfilltype = fill.asc_getGradType();\r\n
                                        if (this._state.GradFillType !== gradfilltype || this.GradFillType !== gradfilltype) {\r\n
                                            this.GradFillType = gradfilltype;\r\n
                                            rec = undefined;\r\n
                                            if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR || this.GradFillType == c_oAscFillGradType.GRAD_PATH) {\r\n
                                                this.cmbGradType.setValue(this.GradFillType);\r\n
                                                rec = this.cmbGradType.store.findWhere({\r\n
                                                    value: this.GradFillType\r\n
                                                });\r\n
                                                this.onGradTypeSelect(this.cmbGradType, rec.attributes);\r\n
                                            } else {\r\n
                                                this.cmbGradType.setValue("");\r\n
                                                this.btnDirection.setIconCls("");\r\n
                                            }\r\n
                                            this._state.GradFillType = this.GradFillType;\r\n
                                        }\r\n
                                        if (this.GradFillType == c_oAscFillGradType.GRAD_LINEAR) {\r\n
                                            var value = Math.floor(fill.asc_getLinearAngle() / 60000);\r\n
                                            if (Math.abs(this.GradLinearDirectionType - value) > 0.001) {\r\n
                                                this.GradLinearDirectionType = value;\r\n
                                                var record = this.mnuDirectionPicker.store.findWhere({\r\n
                                                    type: value\r\n
                                                });\r\n
                                                this.mnuDirectionPicker.selectRecord(record, true);\r\n
                                                if (record) {\r\n
                                                    this.btnDirection.setIconCls("item-gradient " + record.get("iconcls"));\r\n
                                                } else {\r\n
                                                    this.btnDirection.setIconCls("");\r\n
                                                }\r\n
                                            }\r\n
                                        }\r\n
                                        var colors = fill.asc_getColors();\r\n
                                        if (colors && colors.length > 0) {\r\n
                                            color = colors[0];\r\n
                                            if (color) {\r\n
                                                if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                                    this.GradColor.colors[0] = {\r\n
                                                        color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                                        effectValue: color.asc_getValue()\r\n
                                                    };\r\n
                                                    Common.Utils.ThemeColor.colorValue2EffectId(this.GradColor.colors[0]);\r\n
                                                } else {\r\n
                                                    this.GradColor.colors[0] = Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB());\r\n
                                                }\r\n
                                            } else {\r\n
                                                this.GradColor.colors[0] = "000000";\r\n
                                            }\r\n
                                            color = colors[1];\r\n
                                            if (color) {\r\n
                                                if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                                    this.GradColor.colors[1] = {\r\n
                                                        color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                                        effectValue: color.asc_getValue()\r\n
                                                    };\r\n
                                                    Common.Utils.ThemeColor.colorValue2EffectId(this.GradColor.colors[1]);\r\n
                                                } else {\r\n
                                                    this.GradColor.colors[1] = Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB());\r\n
                                                }\r\n
                                            } else {\r\n
                                                this.GradColor.colors[1] = "ffffff";\r\n
                                            }\r\n
                                        }\r\n
                                        var positions = fill.asc_getPositions();\r\n
                                        if (positions && positions.length > 0) {\r\n
                                            var position = positions[0];\r\n
                                            if (position !== null) {\r\n
                                                position = position / 1000;\r\n
                                                this.GradColor.values[0] = position;\r\n
                                            }\r\n
                                            position = positions[1];\r\n
                                            if (position !== null) {\r\n
                                                position = position / 1000;\r\n
                                                this.GradColor.values[1] = position;\r\n
                                            }\r\n
                                        }\r\n
                                        this.sldrGradient.setColorValue(Common.Utils.String.format("#{0}", (typeof(this.GradColor.colors[0]) == "object") ? this.GradColor.colors[0].color : this.GradColor.colors[0]), 0);\r\n
                                        this.sldrGradient.setColorValue(Common.Utils.String.format("#{0}", (typeof(this.GradColor.colors[1]) == "object") ? this.GradColor.colors[1].color : this.GradColor.colors[1]), 1);\r\n
                                        this.sldrGradient.setValue(0, this.GradColor.values[0]);\r\n
                                        this.sldrGradient.setValue(1, this.GradColor.values[1]);\r\n
                                        this.OriginalFillType = c_oAscFill.FILL_TYPE_GRAD;\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
                if (this._state.FillType !== this.OriginalFillType) {\r\n
                    this.cmbFillSrc.setValue((this.OriginalFillType === null) ? "" : this.OriginalFillType);\r\n
                    this._state.FillType = this.OriginalFillType;\r\n
                    this.ShowHideElem(this.OriginalFillType);\r\n
                }\r\n
                $(this.btnTexture.el).find(".form-control").prop("innerHTML", this.textSelectTexture);\r\n
                var type1 = typeof(this.ShapeColor.Color),\r\n
                type2 = typeof(this._state.ShapeColor);\r\n
                if ((type1 !== type2) || (type1 == "object" && (this.ShapeColor.Color.effectValue !== this._state.ShapeColor.effectValue || this._state.ShapeColor.color.indexOf(this.ShapeColor.Color.color) < 0)) || (type1 != "object" && this._state.ShapeColor.indexOf(this.ShapeColor.Color) < 0)) {\r\n
                    this.btnBackColor.setColor(this.ShapeColor.Color);\r\n
                    if (typeof(this.ShapeColor.Color) == "object") {\r\n
                        var isselected = false;\r\n
                        for (var i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] == this.ShapeColor.Color.effectValue) {\r\n
                                this.colorsBack.select(this.ShapeColor.Color, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.colorsBack.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.colorsBack.select(this.ShapeColor.Color, true);\r\n
                    }\r\n
                    this._state.ShapeColor = this.ShapeColor.Color;\r\n
                }\r\n
                var stroke = shapeprops.asc_getStroke();\r\n
                var strokeType = stroke.asc_getType();\r\n
                if (stroke) {\r\n
                    if (strokeType == c_oAscStrokeType.STROKE_COLOR) {\r\n
                        color = stroke.asc_getColor();\r\n
                        if (color) {\r\n
                            if (color.asc_getType() == c_oAscColor.COLOR_TYPE_SCHEME) {\r\n
                                this.BorderColor = {\r\n
                                    Value: 1,\r\n
                                    Color: {\r\n
                                        color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB()),\r\n
                                        effectValue: color.asc_getValue()\r\n
                                    }\r\n
                                };\r\n
                            } else {\r\n
                                this.BorderColor = {\r\n
                                    Value: 1,\r\n
                                    Color: Common.Utils.ThemeColor.getHexColor(color.asc_getR(), color.asc_getG(), color.asc_getB())\r\n
                                };\r\n
                            }\r\n
                        } else {\r\n
                            this.BorderColor = {\r\n
                                Value: 1,\r\n
                                Color: "transparent"\r\n
                            };\r\n
                        }\r\n
                    } else {\r\n
                        this.BorderColor = {\r\n
                            Value: 1,\r\n
                            Color: "transparent"\r\n
                        };\r\n
                    }\r\n
                } else {\r\n
                    strokeType = null;\r\n
                    this.BorderColor = {\r\n
                        Value: 0,\r\n
                        Color: "transparent"\r\n
                    };\r\n
                }\r\n
                type1 = typeof(this.BorderColor.Color);\r\n
                type2 = typeof(this._state.StrokeColor);\r\n
                if ((type1 !== type2) || (type1 == "object" && (this.BorderColor.Color.effectValue !== this._state.StrokeColor.effectValue || this._state.StrokeColor.color.indexOf(this.BorderColor.Color.color) < 0)) || (type1 != "object" && (this._state.StrokeColor.indexOf(this.BorderColor.Color) < 0 || typeof(this.btnBorderColor.color) == "object"))) {\r\n
                    this.btnBorderColor.setColor(this.BorderColor.Color);\r\n
                    if (typeof(this.BorderColor.Color) == "object") {\r\n
                        var isselected = false;\r\n
                        for (var i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] == this.BorderColor.Color.effectValue) {\r\n
                                this.colorsBorder.select(this.BorderColor.Color, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.colorsBorder.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.colorsBorder.select(this.BorderColor.Color, true);\r\n
                    }\r\n
                    this._state.StrokeColor = this.BorderColor.Color;\r\n
                }\r\n
                if (this._state.StrokeType !== strokeType || strokeType == c_oAscStrokeType.STROKE_COLOR) {\r\n
                    if (strokeType == c_oAscStrokeType.STROKE_COLOR) {\r\n
                        var w = stroke.asc_getWidth();\r\n
                        var check_value = (Math.abs(this._state.StrokeWidth - w) < 0.001) && !(/pt\\s*$/.test(this.cmbBorderSize.getRawValue()));\r\n
                        if (Math.abs(this._state.StrokeWidth - w) > 0.001 || check_value || (this._state.StrokeWidth === null || w === null) && (this._state.StrokeWidth !== w)) {\r\n
                            this._state.StrokeWidth = w;\r\n
                            if (w !== null) {\r\n
                                w = this._mm2pt(w);\r\n
                            }\r\n
                            var _selectedItem = (w === null) ? w : _.find(this.cmbBorderSize.store.models, function (item) {\r\n
                                if (w < item.attributes.value + 0.01 && w > item.attributes.value - 0.01) {\r\n
                                    return true;\r\n
                                }\r\n
                            });\r\n
                            if (_selectedItem) {\r\n
                                this.cmbBorderSize.selectRecord(_selectedItem);\r\n
                            } else {\r\n
                                this.cmbBorderSize.setValue((w !== null) ? parseFloat(w.toFixed(2)) + " pt" : "");\r\n
                            }\r\n
                            this.BorderSize = w;\r\n
                        }\r\n
                    } else {\r\n
                        if (strokeType == c_oAscStrokeType.STROKE_NONE) {\r\n
                            this._state.StrokeWidth = 0;\r\n
                            this.BorderSize = this.cmbBorderSize.store.at(0).get("value");\r\n
                            this.cmbBorderSize.setValue(this.BorderSize);\r\n
                        } else {\r\n
                            this._state.StrokeWidth = null;\r\n
                            this.BorderSize = -1;\r\n
                            this.cmbBorderSize.setValue(null);\r\n
                        }\r\n
                    }\r\n
                    this._state.StrokeType = strokeType;\r\n
                }\r\n
                type1 = typeof(this.FGColor.Color);\r\n
                type2 = typeof(this._state.FGColor);\r\n
                if ((type1 !== type2) || (type1 == "object" && (this.FGColor.Color.effectValue !== this._state.FGColor.effectValue || this._state.FGColor.color.indexOf(this.FGColor.Color.color) < 0)) || (type1 != "object" && this._state.FGColor.indexOf(this.FGColor.Color) < 0)) {\r\n
                    this.btnFGColor.setColor(this.FGColor.Color);\r\n
                    if (typeof(this.FGColor.Color) == "object") {\r\n
                        var isselected = false;\r\n
                        for (var i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] == this.FGColor.Color.effectValue) {\r\n
                                this.colorsFG.select(this.FGColor.Color, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.colorsFG.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.colorsFG.select(this.FGColor.Color, true);\r\n
                    }\r\n
                    this._state.FGColor = this.FGColor.Color;\r\n
                }\r\n
                type1 = typeof(this.BGColor.Color);\r\n
                type2 = typeof(this._state.BGColor);\r\n
                if ((type1 !== type2) || (type1 == "object" && (this.BGColor.Color.effectValue !== this._state.BGColor.effectValue || this._state.BGColor.color.indexOf(this.BGColor.Color.color) < 0)) || (type1 != "object" && this._state.BGColor.indexOf(this.BGColor.Color) < 0)) {\r\n
                    this.btnBGColor.setColor(this.BGColor.Color);\r\n
                    if (typeof(this.BGColor.Color) == "object") {\r\n
                        var isselected = false;\r\n
                        for (var i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] == this.BGColor.Color.effectValue) {\r\n
                                this.colorsBG.select(this.BGColor.Color, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.colorsBG.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.colorsBG.select(this.BGColor.Color, true);\r\n
                    }\r\n
                    this._state.BGColor = this.BGColor.Color;\r\n
                }\r\n
                color = this.GradColor.colors[this.GradColor.currentIdx];\r\n
                type1 = typeof(color);\r\n
                type2 = typeof(this._state.GradColor);\r\n
                if ((type1 !== type2) || (type1 == "object" && (color.effectValue !== this._state.GradColor.effectValue || this._state.GradColor.color.indexOf(color.color) < 0)) || (type1 != "object" && this._state.GradColor.indexOf(color) < 0)) {\r\n
                    this.btnGradColor.setColor(color);\r\n
                    if (typeof(color) == "object") {\r\n
                        var isselected = false;\r\n
                        for (var i = 0; i < 10; i++) {\r\n
                            if (Common.Utils.ThemeColor.ThemeValues[i] == color.effectValue) {\r\n
                                this.colorsGrad.select(color, true);\r\n
                                isselected = true;\r\n
                                break;\r\n
                            }\r\n
                        }\r\n
                        if (!isselected) {\r\n
                            this.colorsGrad.clearSelection();\r\n
                        }\r\n
                    } else {\r\n
                        this.colorsGrad.select(color, true);\r\n
                    }\r\n
                    this._state.GradColor = color;\r\n
                }\r\n
                this._noApply = false;\r\n
            }\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            var global_hatch_menu_map = [0, 1, 3, 2, 4, 53, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 49, 50, 51, 52];\r\n
            this.patternViewData = [];\r\n
            for (var i = 0; i < 13; i++) {\r\n
                for (var j = 0; j < 4; j++) {\r\n
                    var num = i * 4 + j;\r\n
                    this.patternViewData[num] = {\r\n
                        offsetx: j * 28,\r\n
                        offsety: i * 28,\r\n
                        type: global_hatch_menu_map[num]\r\n
                    };\r\n
                }\r\n
            }\r\n
            this.patternViewData.splice(this.patternViewData.length - 2, 2);\r\n
            for (var i = 0; i < this.patternViewData.length; i++) {\r\n
                this.patternViewData[i].id = Common.UI.getId();\r\n
            }\r\n
            this.cmbPattern.menuPicker.store.add(this.patternViewData);\r\n
            if (this.cmbPattern.menuPicker.store.length > 0) {\r\n
                this.cmbPattern.fillComboView(this.cmbPattern.menuPicker.store.at(0), true);\r\n
                this.PatternFillType = this.patternViewData[0].type;\r\n
            }\r\n
            this.fillAutoShapes();\r\n
            this.UpdateThemeColors();\r\n
        },\r\n
        onInitStandartTextures: function (texture) {\r\n
            var me = this;\r\n
            if (texture && texture.length > 0) {\r\n
                var texturearray = [];\r\n
                _.each(texture, function (item) {\r\n
                    texturearray.push({\r\n
                        imageUrl: item.asc_getImage(),\r\n
                        name: me.textureNames[item.asc_getId()],\r\n
                        type: item.asc_getId(),\r\n
                        selected: false\r\n
                    });\r\n
                });\r\n
                var mnuTexturePicker = new Common.UI.DataView({\r\n
                    el: $("#id-shape-menu-texture"),\r\n
                    parentMenu: me.textureMenu,\r\n
                    restoreHeight: 174,\r\n
                    store: new Common.UI.DataViewStore(texturearray),\r\n
                    itemTemplate: _.template(\'<div class="item-shape"><img src="<%= imageUrl %>" id="<%= id %>"></div>\')\r\n
                });\r\n
                mnuTexturePicker.on("item:click", _.bind(this.onSelectTexture, this));\r\n
                me.textureMenu.on("show:after", function (btn) {\r\n
                    mnuTexturePicker.deselectAll();\r\n
                });\r\n
            }\r\n
        },\r\n
        onSelectTexture: function (picker, view, record) {\r\n
            this._fromTextureCmb = true;\r\n
            this.cmbFillType.setValue(this._arrFillType[1].value);\r\n
            this._fromTextureCmb = false;\r\n
            if (this.api) {\r\n
                var props = new Asc.asc_CShapeProperty();\r\n
                var fill = new Asc.asc_CShapeFill();\r\n
                fill.asc_putType(c_oAscFill.FILL_TYPE_BLIP);\r\n
                fill.asc_putFill(new Asc.asc_CFillBlip());\r\n
                fill.asc_getFill().asc_putType(c_oAscFillBlipType.TILE);\r\n
                fill.asc_getFill().asc_putTextureId(record.get("type"));\r\n
                props.asc_putFill(fill);\r\n
                this.imgprops.asc_putShapeProperties(props);\r\n
                this.api.asc_setGraphicObjectProps(this.imgprops);\r\n
            }\r\n
            $(this.btnTexture.el).find(".form-control").prop("innerHTML", record.get("name"));\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        fillAutoShapes: function () {\r\n
            var me = this,\r\n
            shapesStore = this.application.getCollection("ShapeGroups");\r\n
            var count = shapesStore.length;\r\n
            for (var i = 0; i < count; i++) {\r\n
                if (i == count - 2) {\r\n
                    continue;\r\n
                }\r\n
                var shapeGroup = shapesStore.at(i);\r\n
                var menuItem = new Common.UI.MenuItem({\r\n
                    caption: shapeGroup.get("groupName"),\r\n
                    menu: new Common.UI.Menu({\r\n
                        menuAlign: "tr-tl",\r\n
                        items: [{\r\n
                            template: _.template(\'<div id="id-shape-menu-shapegroup\' + i + \'" class="menu-shape" style="width: \' + (shapeGroup.get("groupWidth") - 8) + \'px; margin-left: 5px;"></div>\')\r\n
                        }]\r\n
                    })\r\n
                });\r\n
                me.btnChangeShape.menu.addItem(menuItem);\r\n
                var shapePicker = new Common.UI.DataView({\r\n
                    el: $("#id-shape-menu-shapegroup" + i),\r\n
                    store: shapeGroup.get("groupStore"),\r\n
                    itemTemplate: _.template(\'<div class="item-shape"><img src="<%= imageUrl %>" id="<%= id %>"></div>\')\r\n
                });\r\n
                shapePicker.on("item:click", function (picker, item, record) {\r\n
                    if (me.api) {\r\n
                        me.api.asc_changeShapeType(record.get("data").shapeType);\r\n
                        Common.NotificationCenter.trigger("edit:complete", me);\r\n
                    }\r\n
                });\r\n
            }\r\n
        },\r\n
        UpdateThemeColors: function () {\r\n
            this.colorsBorder.updateColors(Common.Utils.ThemeColor.getEffectColors(), Common.Utils.ThemeColor.getStandartColors());\r\n
            this.colorsBack.updateColors(Common.Utils.ThemeColor.getEffectColors(), Common.Utils.ThemeColor.getStandartColors());\r\n
            this.colorsFG.updateColors(Common.Utils.ThemeColor.getEffectColors(), Common.Utils.ThemeColor.getStandartColors());\r\n
            this.colorsBG.updateColors(Common.Utils.ThemeColor.getEffectColors(), Common.Utils.ThemeColor.getStandartColors());\r\n
            this.colorsGrad.updateColors(Common.Utils.ThemeColor.getEffectColors(), Common.Utils.ThemeColor.getStandartColors());\r\n
        },\r\n
        _pt2mm: function (value) {\r\n
            return (value * 25.4 / 72);\r\n
        },\r\n
        _mm2pt: function (value) {\r\n
            return (value * 72 / 25.4);\r\n
        },\r\n
        disableFillPanels: function (disable) {\r\n
            if (this._state.DisabledFillPanels !== disable) {\r\n
                this._state.DisabledFillPanels = disable;\r\n
                _.each(this.fillControls, function (item) {\r\n
                    item.setDisabled(disable);\r\n
                });\r\n
                this.lblTransparencyStart.toggleClass("disabled", disable);\r\n
                this.lblTransparencyEnd.toggleClass("disabled", disable);\r\n
            }\r\n
        },\r\n
        ShowHideElem: function (value) {\r\n
            this.FillColorContainer.toggleClass("settings-hidden", value !== c_oAscFill.FILL_TYPE_SOLID);\r\n
            this.FillImageContainer.toggleClass("settings-hidden", value !== c_oAscFill.FILL_TYPE_BLIP);\r\n
            this.FillPatternContainer.toggleClass("settings-hidden", value !== c_oAscFill.FILL_TYPE_PATT);\r\n
            this.FillGradientContainer.toggleClass("settings-hidden", value !== c_oAscFill.FILL_TYPE_GRAD);\r\n
            this.TransparencyContainer.toggleClass("settings-hidden", (value === c_oAscFill.FILL_TYPE_NOFILL || value === null));\r\n
        },\r\n
        setLocked: function (locked) {\r\n
            this._locked = locked;\r\n
        },\r\n
        disableControls: function (disable, disableFill) {\r\n
            this.disableFillPanels(disable || disableFill);\r\n
            if (this._state.DisabledControls !== disable) {\r\n
                this._state.DisabledControls = disable;\r\n
                _.each(this.lockedControls, function (item) {\r\n
                    item.setDisabled(disable);\r\n
                });\r\n
                this.linkAdvanced.toggleClass("disabled", disable);\r\n
            }\r\n
        },\r\n
        hideShapeOnlySettings: function (value) {\r\n
            if (this._state.HideShapeOnlySettings !== value) {\r\n
                this._state.HideShapeOnlySettings = value;\r\n
                this.ShapeOnlySettings.toggleClass("hidden", value == true);\r\n
            }\r\n
        },\r\n
        txtNoBorders: "No Line",\r\n
        strStroke: "Stroke",\r\n
        strColor: "Color",\r\n
        strSize: "Size",\r\n
        strChange: "Change Autoshape",\r\n
        strFill: "Fill",\r\n
        textColor: "Color Fill",\r\n
        textImageTexture: "Picture or Texture",\r\n
        textTexture: "From Texture",\r\n
        textFromUrl: "From URL",\r\n
        textFromFile: "From File",\r\n
        textStretch: "Stretch",\r\n
        textTile: "Tile",\r\n
        txtCanvas: "Canvas",\r\n
        txtCarton: "Carton",\r\n
        txtDarkFabric: "Dark Fabric",\r\n
        txtGrain: "Grain",\r\n
        txtGranite: "Granite",\r\n
        txtGreyPaper: "Grey Paper",\r\n
        txtKnit: "Knit",\r\n
        txtLeather: "Leather",\r\n
        txtBrownPaper: "Brown Paper",\r\n
        txtPapyrus: "Papyrus",\r\n
        txtWood: "Wood",\r\n
        textNewColor: "Add New Custom Color",\r\n
        textThemeColors: "Theme Colors",\r\n
        textStandartColors: "Standart Colors",\r\n
        textAdvanced: "Show advanced settings",\r\n
        strTransparency: "Opacity",\r\n
        textNoFill: "No Fill",\r\n
        textSelectTexture: "Select",\r\n
        textGradientFill: "Gradient Fill",\r\n
        textPatternFill: "Pattern",\r\n
        strBackground: "Background color",\r\n
        strForeground: "Foreground color",\r\n
        strPattern: "Pattern",\r\n
        textEmptyPattern: "No Pattern",\r\n
        textLinear: "Linear",\r\n
        textRadial: "Radial",\r\n
        textDirection: "Direction",\r\n
        textStyle: "Style",\r\n
        textGradient: "Gradient",\r\n
        textBorderSizeErr: "The entered value is incorrect.<br>Please enter a value between 0 pt and 1584 pt."\r\n
    },\r\n
    SSE.Views.ShapeSettings || {}));\r\n
});

]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
