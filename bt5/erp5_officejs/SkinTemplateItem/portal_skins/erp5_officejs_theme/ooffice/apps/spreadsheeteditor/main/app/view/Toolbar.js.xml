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
            <value> <string>ts44321339.8</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Toolbar.js</string> </value>
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
            <value> <int>113312</int> </value>
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
 define(["jquery", "underscore", "backbone", "text!spreadsheeteditor/main/app/template/Toolbar.template", "common/main/lib/collection/Fonts", "common/main/lib/component/Button", "common/main/lib/component/ComboBox", "common/main/lib/component/DataView", "common/main/lib/component/ColorPalette", "common/main/lib/component/ThemeColorPalette", "common/main/lib/component/Menu", "common/main/lib/component/DimensionPicker", "common/main/lib/component/Window", "common/main/lib/component/ComboBoxFonts", "common/main/lib/component/ComboDataView", "common/main/lib/component/SynchronizeTip"], function ($, _, Backbone, toolbarTemplate) {\r\n
    SSE.enumLock = {\r\n
        editCell: "cell-editing",\r\n
        editFormula: "is-formula",\r\n
        editText: "is-text",\r\n
        selImage: "sel-image",\r\n
        selShape: "sel-shape",\r\n
        selShapeText: "sel-shape-txt",\r\n
        selChart: "sel-chart",\r\n
        selChartText: "sel-chart-txt",\r\n
        selRange: "sel-range",\r\n
        lostConnect: "disconnect",\r\n
        coAuth: "co-auth",\r\n
        ruleMerge: "rule-btn-merge",\r\n
        ruleFilter: "rule-filter",\r\n
        ruleDelFilter: "rule-clear-filter",\r\n
        menuFileOpen: "menu-file-open"\r\n
    };\r\n
    SSE.Views.Toolbar = Backbone.View.extend(_.extend({\r\n
        el: "#toolbar",\r\n
        template: _.template(toolbarTemplate),\r\n
        events: {},\r\n
        initialize: function () {\r\n
            var me = this,\r\n
            options = {};\r\n
            JSON.parse(window.localStorage.getItem("sse-hidden-title")) && (options.title = true);\r\n
            JSON.parse(window.localStorage.getItem("sse-hidden-formula")) && (options.formula = true);\r\n
            JSON.parse(window.localStorage.getItem("sse-hidden-headings")) && (options.headings = true);\r\n
            me.isCompactView = !!JSON.parse(window.localStorage.getItem("sse-toolbar-compact"));\r\n
            me.SchemeNames = [me.txtScheme1, me.txtScheme2, me.txtScheme3, me.txtScheme4, me.txtScheme5, me.txtScheme6, me.txtScheme7, me.txtScheme8, me.txtScheme9, me.txtScheme10, me.txtScheme11, me.txtScheme12, me.txtScheme13, me.txtScheme14, me.txtScheme15, me.txtScheme16, me.txtScheme17, me.txtScheme18, me.txtScheme19, me.txtScheme20, me.txtScheme21];\r\n
            me._state = {\r\n
                hasCollaborativeChanges: undefined\r\n
            };\r\n
            me.btnSaveCls = "btn-save";\r\n
            me.btnSaveTip = this.tipSave + Common.Utils.String.platformKey("Ctrl+S");\r\n
            me.ascFormatOptions = {\r\n
                General: "General",\r\n
                Number: "0.00",\r\n
                Currency: "$#,##0.00",\r\n
                Accounting: \'_($* #,##0.00_);_($* (#,##0.00);_($* "-"??_);_(@_)\',\r\n
                DateShort: "m/d/yyyy",\r\n
                DateLong: "[$-F800]dddd, mmmm dd, yyyy",\r\n
                Time: "[$-F400]h:mm:ss AM/PM",\r\n
                Percentage: "0.00%",\r\n
                Percent: "0%",\r\n
                Fraction: "# ?/?",\r\n
                Scientific : "0.00E+00",\r\n
                Text : "@"\r\n
            };\r\n
            me.numFormatTypes = {};\r\n
            me.numFormatTypes[c_oAscNumFormatType.General] = me.txtGeneral;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Custom] = me.txtCustom;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Text] = me.txtText;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Number] = me.txtNumber;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Integer] = me.txtInteger;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Scientific] = me.txtScientific;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Currency] = me.txtCurrency;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Accounting] = me.txtAccounting;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Date] = me.txtDate;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Time] = me.txtTime;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Percent] = me.txtPercentage;\r\n
            me.numFormatTypes[c_oAscNumFormatType.Fraction] = "Fraction";\r\n
            function dummyCmp() {\r\n
                return {\r\n
                    isDummy: true,\r\n
                    on: function () {}\r\n
                };\r\n
            }\r\n
            var _set = SSE.enumLock;\r\n
            me.cmbFontSize = new Common.UI.ComboBox({\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 55px;",\r\n
                hint: me.tipFontSize,\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                data: [{\r\n
                    value: 8,\r\n
                    displayValue: "8"\r\n
                },\r\n
                {\r\n
                    value: 9,\r\n
                    displayValue: "9"\r\n
                },\r\n
                {\r\n
                    value: 10,\r\n
                    displayValue: "10"\r\n
                },\r\n
                {\r\n
                    value: 11,\r\n
                    displayValue: "11"\r\n
                },\r\n
                {\r\n
                    value: 12,\r\n
                    displayValue: "12"\r\n
                },\r\n
                {\r\n
                    value: 14,\r\n
                    displayValue: "14"\r\n
                },\r\n
                {\r\n
                    value: 16,\r\n
                    displayValue: "16"\r\n
                },\r\n
                {\r\n
                    value: 18,\r\n
                    displayValue: "18"\r\n
                },\r\n
                {\r\n
                    value: 20,\r\n
                    displayValue: "20"\r\n
                },\r\n
                {\r\n
                    value: 22,\r\n
                    displayValue: "22"\r\n
                },\r\n
                {\r\n
                    value: 24,\r\n
                    displayValue: "24"\r\n
                },\r\n
                {\r\n
                    value: 26,\r\n
                    displayValue: "26"\r\n
                },\r\n
                {\r\n
                    value: 28,\r\n
                    displayValue: "28"\r\n
                },\r\n
                {\r\n
                    value: 36,\r\n
                    displayValue: "36"\r\n
                },\r\n
                {\r\n
                    value: 48,\r\n
                    displayValue: "48"\r\n
                },\r\n
                {\r\n
                    value: 72,\r\n
                    displayValue: "72"\r\n
                }]\r\n
            });\r\n
            me.btnNewDocument = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-newdocument",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-newdocument",\r\n
                lock: [_set.lostConnect],\r\n
                hint: me.tipNewDocument\r\n
            });\r\n
            me.btnOpenDocument = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-opendocument",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-opendocument",\r\n
                lock: [_set.lostConnect],\r\n
                hint: me.tipOpenDocument\r\n
            });\r\n
            me.cmbFontName = new Common.UI.ComboBoxFonts({\r\n
                cls: "input-group-nr",\r\n
                menuCls: "scrollable-menu",\r\n
                menuStyle: "min-width: 325px;",\r\n
                hint: me.tipFontName,\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                store: new Common.Collections.Fonts()\r\n
            });\r\n
            me.btnPrint = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-print",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-print",\r\n
                split: true,\r\n
                hint: me.tipPrint + Common.Utils.String.platformKey("Ctrl+P"),\r\n
                lock: [_set.editCell],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.textPrint,\r\n
                        value: "print"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textPrintOptions,\r\n
                        value: "options"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnSave = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-save",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: me.btnSaveCls,\r\n
                hint: me.btnSaveTip\r\n
            });\r\n
            me.btnCopy = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-copy",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-copy",\r\n
                hint: me.tipCopy + Common.Utils.String.platformKey("Ctrl+C")\r\n
            });\r\n
            me.btnPaste = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-paste",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-paste",\r\n
                lock: [_set.coAuth, _set.lostConnect],\r\n
                hint: me.tipPaste + Common.Utils.String.platformKey("Ctrl+V")\r\n
            });\r\n
            me.btnUndo = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-undo",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-undo",\r\n
                disabled: true,\r\n
                lock: [_set.lostConnect],\r\n
                hint: me.tipUndo + Common.Utils.String.platformKey("Ctrl+Z")\r\n
            });\r\n
            me.btnRedo = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-redo",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-redo",\r\n
                disabled: true,\r\n
                lock: [_set.lostConnect],\r\n
                hint: me.tipRedo + Common.Utils.String.platformKey("Ctrl+Y")\r\n
            });\r\n
            me.btnIncFontSize = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-incfont",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-incfont",\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                hint: me.tipIncFont\r\n
            });\r\n
            me.btnDecFontSize = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-decfont",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-decfont",\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                hint: me.tipDecFont\r\n
            });\r\n
            me.btnBold = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-bold",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-bold",\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                hint: me.textBold + Common.Utils.String.platformKey("Ctrl+B"),\r\n
                enableToggle: true\r\n
            });\r\n
            me.btnItalic = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-italic",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-italic",\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                hint: me.textItalic + Common.Utils.String.platformKey("Ctrl+I"),\r\n
                enableToggle: true\r\n
            });\r\n
            me.btnUnderline = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-underline",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-underline",\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                hint: me.textUnderline + Common.Utils.String.platformKey("Ctrl+U"),\r\n
                enableToggle: true\r\n
            });\r\n
            me.mnuTextColorPicker = dummyCmp();\r\n
            me.btnTextColor = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-fontcolor",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-fontcolor",\r\n
                hint: me.tipFontColor,\r\n
                split: true,\r\n
                lock: [_set.selImage, _set.editFormula, _set.selRange, _set.coAuth, _set.lostConnect],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-toolbar-menu-fontcolor" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="id-toolbar-menu-new-fontcolor" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            }).on("render:after", function (btn) {\r\n
                var colorVal = $(\'<div class="btn-color-value-line"></div>\');\r\n
                $("button:first-child", btn.cmpEl).append(colorVal);\r\n
                colorVal.css("background-color", btn.currentColor || "transparent");\r\n
                me.mnuTextColorPicker = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#id-toolbar-menu-fontcolor"),\r\n
                    dynamiccolors: 10,\r\n
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
            });\r\n
            me.mnuBackColorPicker = dummyCmp();\r\n
            me.btnBackColor = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-fillparag",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-fillparag",\r\n
                hint: me.tipPrColor,\r\n
                split: true,\r\n
                lock: [_set.selImage, _set.editCell, _set.coAuth, _set.lostConnect],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-toolbar-menu-paracolor" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                    },\r\n
                    {\r\n
                        template: _.template(\'<a id="id-toolbar-menu-new-paracolor" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                    }]\r\n
                })\r\n
            }).on("render:after", function (btn) {\r\n
                var colorVal = $(\'<div class="btn-color-value-line"></div>\');\r\n
                $("button:first-child", btn.cmpEl).append(colorVal);\r\n
                colorVal.css("background-color", btn.currentColor || "transparent");\r\n
                me.mnuBackColorPicker = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#id-toolbar-menu-paracolor"),\r\n
                    dynamiccolors: 10,\r\n
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
            });\r\n
            me.mnuBorderColorPicker = dummyCmp();\r\n
            me.btnBorders = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-borders",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-border-out",\r\n
                icls: "btn-border-out",\r\n
                borderId: "outer",\r\n
                borderswidth: "thin",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                hint: me.tipBorders,\r\n
                split: true,\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.textOutBorders,\r\n
                        iconCls: "mnu-border-out",\r\n
                        icls: "btn-border-out",\r\n
                        borderId: "outer"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textAllBorders,\r\n
                        iconCls: "mnu-border-all",\r\n
                        icls: "btn-border-all",\r\n
                        borderId: "all"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textTopBorders,\r\n
                        iconCls: "mnu-border-top",\r\n
                        icls: "btn-border-top",\r\n
                        borderId: c_oAscBorderOptions.Top\r\n
                    },\r\n
                    {\r\n
                        caption: me.textBottomBorders,\r\n
                        iconCls: "mnu-border-bottom",\r\n
                        icls: "btn-border-bottom",\r\n
                        borderId: c_oAscBorderOptions.Bottom\r\n
                    },\r\n
                    {\r\n
                        caption: me.textLeftBorders,\r\n
                        iconCls: "mnu-border-left",\r\n
                        icls: "btn-border-left",\r\n
                        borderId: c_oAscBorderOptions.Left\r\n
                    },\r\n
                    {\r\n
                        caption: me.textRightBorders,\r\n
                        iconCls: "mnu-border-right",\r\n
                        icls: "btn-border-right",\r\n
                        borderId: c_oAscBorderOptions.Right\r\n
                    },\r\n
                    {\r\n
                        caption: me.textNoBorders,\r\n
                        iconCls: "mnu-border-no",\r\n
                        icls: "btn-border-no",\r\n
                        borderId: "none"\r\n
                    },\r\n
                    {\r\n
                        caption: "--"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textInsideBorders,\r\n
                        iconCls: "mnu-border-center",\r\n
                        icls: "btn-border-center",\r\n
                        borderId: "inner"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textCenterBorders,\r\n
                        iconCls: "mnu-border-vmiddle",\r\n
                        icls: "btn-border-vmiddle",\r\n
                        borderId: c_oAscBorderOptions.InnerV\r\n
                    },\r\n
                    {\r\n
                        caption: me.textMiddleBorders,\r\n
                        iconCls: "mnu-border-hmiddle",\r\n
                        icls: "btn-border-hmiddle",\r\n
                        borderId: c_oAscBorderOptions.InnerH\r\n
                    },\r\n
                    {\r\n
                        caption: me.textDiagUpBorder,\r\n
                        iconCls: "mnu-border-diagup",\r\n
                        icls: "btn-border-diagup",\r\n
                        borderId: c_oAscBorderOptions.DiagU\r\n
                    },\r\n
                    {\r\n
                        caption: me.textDiagDownBorder,\r\n
                        iconCls: "mnu-border-diagdown",\r\n
                        icls: "btn-border-diagdown",\r\n
                        borderId: c_oAscBorderOptions.DiagD\r\n
                    },\r\n
                    {\r\n
                        caption: "--"\r\n
                    },\r\n
                    {\r\n
                        id: "id-toolbar-mnu-item-border-width",\r\n
                        caption: me.textBordersWidth,\r\n
                        iconCls: "mnu-icon-item mnu-border-width",\r\n
                        template: _.template(\'<a id="<%= id %>" tabindex="-1" type="menuitem"><span class="menu-item-icon" style="background-image: none; width: 11px; height: 11px; margin: 2px 7px 0 -9px; border-style: solid; border-width: 1px; border-color: #000;"></span><%= caption %></a>\'),\r\n
                        menu: (function () {\r\n
                            var itemTemplate = _.template(\'<a id="<%= id %>" tabindex="-1" type="menuitem"><div class="border-size-item" style="background-position: 0 -<%= options.offsety %>px;"></div></a>\');\r\n
                            me.mnuBorderWidth = new Common.UI.Menu({\r\n
                                style: "min-width: 100px;",\r\n
                                menuAlign: "tl-tr",\r\n
                                id: "toolbar-menu-borders-width",\r\n
                                items: [{\r\n
                                    template: itemTemplate,\r\n
                                    stopPropagation: true,\r\n
                                    checkable: true,\r\n
                                    toggleGroup: "border-width",\r\n
                                    value: "thin",\r\n
                                    offsety: 0,\r\n
                                    checked: true\r\n
                                },\r\n
                                {\r\n
                                    template: itemTemplate,\r\n
                                    stopPropagation: true,\r\n
                                    checkable: true,\r\n
                                    toggleGroup: "border-width",\r\n
                                    value: "medium",\r\n
                                    offsety: 20\r\n
                                },\r\n
                                {\r\n
                                    template: itemTemplate,\r\n
                                    stopPropagation: true,\r\n
                                    checkable: true,\r\n
                                    toggleGroup: "border-width",\r\n
                                    value: "thick",\r\n
                                    offsety: 40\r\n
                                }]\r\n
                            });\r\n
                            return me.mnuBorderWidth;\r\n
                        })()\r\n
                    },\r\n
                    {\r\n
                        id: "id-toolbar-mnu-item-border-color",\r\n
                        caption: me.textBordersColor,\r\n
                        iconCls: "mnu-icon-item mnu-border-color",\r\n
                        template: _.template(\'<a id="<%= id %>"tabindex="-1" type="menuitem"><span class="menu-item-icon" style="background-image: none; width: 11px; height: 11px; margin: 2px 7px 0 -9px; border-style: solid; border-width: 3px; border-color: #000;"></span><%= caption %></a>\'),\r\n
                        menu: new Common.UI.Menu({\r\n
                            menuAlign: "tl-tr",\r\n
                            items: [{\r\n
                                template: _.template(\'<div id="id-toolbar-menu-bordercolor" style="width: 165px; height: 220px; margin: 10px;"></div>\'),\r\n
                                stopPropagation: true\r\n
                            },\r\n
                            {\r\n
                                template: _.template(\'<a id="id-toolbar-menu-new-bordercolor" style="padding-left:12px;">\' + me.textNewColor + "</a>"),\r\n
                                stopPropagation: true\r\n
                            }]\r\n
                        })\r\n
                    }]\r\n
                })\r\n
            }).on("render:after", function (btn) {\r\n
                var colorVal = $(\'<div class="btn-color-value-line"></div>\');\r\n
                $("button:first-child", btn.cmpEl).append(colorVal);\r\n
                colorVal.css("background-color", btn.currentColor || "transparent");\r\n
                me.mnuBorderColorPicker = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#id-toolbar-menu-bordercolor"),\r\n
                    dynamiccolors: 10,\r\n
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
            });\r\n
            me.btnAlignLeft = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-align-left",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-align-left",\r\n
                hint: me.tipAlignLeft,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                toggleGroup: "alignGroup"\r\n
            });\r\n
            me.btnAlignCenter = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-align-center",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-align-center",\r\n
                hint: me.tipAlignCenter,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                toggleGroup: "alignGroup"\r\n
            });\r\n
            me.btnAlignRight = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-align-right",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-align-right",\r\n
                hint: me.tipAlignRight,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                toggleGroup: "alignGroup"\r\n
            });\r\n
            me.btnAlignJust = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-align-just",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-align-just",\r\n
                hint: me.tipAlignJust,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                toggleGroup: "alignGroup"\r\n
            });\r\n
            me.btnMerge = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-merge",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-merge",\r\n
                hint: me.tipMerge,\r\n
                enableToggle: true,\r\n
                allowDepress: true,\r\n
                split: true,\r\n
                lock: [_set.editCell, _set.selShape, _set.selShapeText, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleMerge],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.txtMergeCenter,\r\n
                        value: c_oAscMergeOptions.MergeCenter\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtMergeAcross,\r\n
                        value: c_oAscMergeOptions.MergeAcross\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtMergeCells,\r\n
                        value: c_oAscMergeOptions.Merge\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtUnmerge,\r\n
                        value: c_oAscMergeOptions.Unmerge\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnAlignTop = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-valign-top",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-valign-top",\r\n
                hint: me.tipAlignTop,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                enableToggle: true,\r\n
                toggleGroup: "vAlignGroup"\r\n
            });\r\n
            me.btnAlignMiddle = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-valign-middle",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-valign-middle",\r\n
                hint: me.tipAlignMiddle,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                toggleGroup: "vAlignGroup"\r\n
            });\r\n
            me.btnAlignBottom = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-valign-bottom",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-valign-bottom",\r\n
                hint: me.tipAlignBottom,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                enableToggle: true,\r\n
                toggleGroup: "vAlignGroup"\r\n
            });\r\n
            me.btnWrap = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-wrap",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-wrap",\r\n
                hint: me.tipWrap,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                enableToggle: true,\r\n
                allowDepress: true\r\n
            });\r\n
            me.btnTextOrient = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-textorient",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-text-orient",\r\n
                hint: me.tipTextOrientation,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.textHorizontal,\r\n
                        iconCls: "mnu-direct-horiz",\r\n
                        checkable: true,\r\n
                        toggleGroup: "textorientgroup",\r\n
                        value: "horiz"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textCounterCw,\r\n
                        iconCls: "mnu-direct-ccw",\r\n
                        checkable: true,\r\n
                        toggleGroup: "textorientgroup",\r\n
                        value: "countcw"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textClockwise,\r\n
                        iconCls: "mnu-direct-cw",\r\n
                        checkable: true,\r\n
                        toggleGroup: "textorientgroup",\r\n
                        value: "clockwise"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textRotateUp,\r\n
                        iconCls: "mnu-direct-rup",\r\n
                        checkable: true,\r\n
                        toggleGroup: "textorientgroup",\r\n
                        value: "rotateup"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textRotateDown,\r\n
                        iconCls: "mnu-direct-rdown",\r\n
                        checkable: true,\r\n
                        toggleGroup: "textorientgroup",\r\n
                        value: "rotatedown"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnInsertImage = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-insertimage",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-insertimage",\r\n
                hint: me.tipInsertImage,\r\n
                lock: [_set.editCell, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.mniImageFromFile,\r\n
                        value: "file"\r\n
                    },\r\n
                    {\r\n
                        caption: me.mniImageFromUrl,\r\n
                        value: "url"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnInsertHyperlink = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-inserthyperlink",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-inserthyperlink",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selImage, _set.selShape, _set.lostConnect, _set.coAuth],\r\n
                hint: me.tipInsertHyperlink + Common.Utils.String.platformKey("Ctrl+K")\r\n
            });\r\n
            me.btnInsertChart = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-insertchart",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-insertchart",\r\n
                lock: [_set.editCell, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                hint: me.tipInsertChart\r\n
            });\r\n
            me.btnEditChart = new Common.UI.Button({\r\n
                id: "id-toolbar-rtn-edit-chart",\r\n
                cls: "btn-toolbar btn-toolbar-default btn-text-value",\r\n
                caption: me.tipEditChart,\r\n
                lock: [_set.lostConnect],\r\n
                style: "width: 120px;"\r\n
            });\r\n
            me.btnInsertShape = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-insertshape",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-insertshape",\r\n
                hint: me.tipInsertShape,\r\n
                enableToggle: true,\r\n
                lock: [_set.editCell, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    cls: "menu-shapes"\r\n
                })\r\n
            });\r\n
            me.btnInsertText = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-inserttext",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-text",\r\n
                hint: me.tipInsertText,\r\n
                lock: [_set.editCell, _set.selChartText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                enableToggle: true\r\n
            });\r\n
            me.btnSortDown = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-sort-down",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-sort-down",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleFilter],\r\n
                hint: me.txtSortAZ\r\n
            });\r\n
            me.btnSortUp = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-sort-up",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-sort-up",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleFilter],\r\n
                hint: me.txtSortZA\r\n
            });\r\n
            me.btnSetAutofilter = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-setautofilter",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-autofilter",\r\n
                hint: me.txtFilter + " (Ctrl+Shift+L)",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleFilter],\r\n
                enableToggle: true\r\n
            });\r\n
            me.btnClearAutofilter = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-clearfilter",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-clear-filter",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleDelFilter],\r\n
                hint: me.txtClearFilter\r\n
            });\r\n
            me.btnTableTemplate = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-ttempl",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-ttempl",\r\n
                hint: me.txtTableTemplate,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleFilter],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        template: _.template(\'<div id="id-toolbar-menu-table-templates" style="width: 285px; height: 300px; margin: 3px 10px;"></div>\')\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.listStyles = new Common.UI.ComboDataView({\r\n
                cls: "combo-styles",\r\n
                enableKeyEvents: true,\r\n
                itemWidth: 104,\r\n
                itemHeight: 38,\r\n
                hint: this.tipCellStyle,\r\n
                menuMaxHeight: 226,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                beforeOpenHandler: function (e) {\r\n
                    var cmp = this,\r\n
                    menu = cmp.openButton.menu,\r\n
                    minMenuColumn = 6;\r\n
                    if (menu.cmpEl) {\r\n
                        var itemEl = $(cmp.cmpEl.find(".dataview.inner .style").get(0)).parent();\r\n
                        var itemMargin = -1;\r\n
                        var itemWidth = itemEl.is(":visible") ? parseInt(itemEl.css("width")) : 112;\r\n
                        var minCount = cmp.menuPicker.store.length >= minMenuColumn ? minMenuColumn : cmp.menuPicker.store.length,\r\n
                        columnCount = Math.min(cmp.menuPicker.store.length, Math.round($(".dataview", $(cmp.fieldPicker.el)).width() / (itemMargin + itemWidth) + 0.5));\r\n
                        columnCount = columnCount < minCount ? minCount : columnCount;\r\n
                        menu.menuAlignEl = cmp.cmpEl;\r\n
                        menu.menuAlign = "tl-tl";\r\n
                        menu.setOffset(cmp.cmpEl.width() - cmp.openButton.$el.width() - columnCount * (itemMargin + itemWidth) - 1);\r\n
                        menu.cmpEl.css({\r\n
                            "width": columnCount * (itemWidth + itemMargin),\r\n
                            "min-height": cmp.cmpEl.height()\r\n
                        });\r\n
                    }\r\n
                }\r\n
            });\r\n
            var formatTemplate = _.template(\'<a id="<%= id %>" style="white-space: normal;"><%= caption %><span style="float: right; color: silver;"><%= options.tplval ? options.tplval : options.value %></span></a>\');\r\n
            me.btnNumberFormat = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-num-format",\r\n
                cls: "btn-toolbar btn-toolbar-default btn-text-value",\r\n
                hint: me.tipNumFormat,\r\n
                caption: me.txtGeneral,\r\n
                style: "width: 100%;",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.selRange, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "margin-left: -1px;",\r\n
                    items: [{\r\n
                        caption: me.txtGeneral,\r\n
                        value: me.ascFormatOptions.General\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtNumber,\r\n
                        value: me.ascFormatOptions.Number\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtInteger,\r\n
                        value: "#0"\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtScientific,\r\n
                        value: me.ascFormatOptions.Scientific\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtAccounting,\r\n
                        menu: new Common.UI.Menu({\r\n
                            style: "min-width: 120px;",\r\n
                            menuAlign: "tl-tr",\r\n
                            items: [{\r\n
                                caption: me.txtDollar,\r\n
                                value: me.ascFormatOptions.Accounting\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtEuro,\r\n
                                value: \'_(€* #,##0.00_);_(€* (#,##0.00);_(€* "-"??_);_(@_)\'\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtPound,\r\n
                                value: \'_(£* #,##0.00_);_(£* (#,##0.00);_(£* "-"??_);_(@_)\'\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtRouble,\r\n
                                value: \'_-* #,##0.00[$р.-419]_-;-* #,##0.00[$р.-419]_-;_-* "-"??[$р.-419]_-;_-@_-\'\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtYen,\r\n
                                value: \'_(¥* #,##0.00_);_(¥* (#,##0.00);_(¥* "-"??_);_(@_)\'\r\n
                            }]\r\n
                        })\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtCurrency,\r\n
                        menu: new Common.UI.Menu({\r\n
                            style: "min-width: 120px;",\r\n
                            menuAlign: "tl-tr",\r\n
                            items: [{\r\n
                                caption: me.txtDollar,\r\n
                                value: me.ascFormatOptions.Currency\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtEuro,\r\n
                                value: "€#,##0.00"\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtPound,\r\n
                                value: "£#,##0.00"\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtRouble,\r\n
                                value: "#,##0.00р."\r\n
                            },\r\n
                            {\r\n
                                caption: me.txtYen,\r\n
                                value: "¥#,##0.00"\r\n
                            }]\r\n
                        })\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtDate,\r\n
                        menu: new Common.UI.Menu({\r\n
                            style: "min-width: 200px;",\r\n
                            menuAlign: "tl-tr",\r\n
                            items: [{\r\n
                                caption: "07-24-88",\r\n
                                value: "MM-dd-yy",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "07-24-1988",\r\n
                                value: "MM-dd-yyyy",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "24-07-88",\r\n
                                value: "dd-MM-yy",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "24-07-1988",\r\n
                                value: "dd-MM-yyyy",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "24-Jul-1988",\r\n
                                value: "dd-MMM-yyyy",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "24-Jul",\r\n
                                value: "dd-MMM",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "Jul-88",\r\n
                                value: "MMM-yy",\r\n
                                template: formatTemplate\r\n
                            }]\r\n
                        })\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtTime,\r\n
                        menu: new Common.UI.Menu({\r\n
                            style: "min-width: 200px;",\r\n
                            menuAlign: "tl-tr",\r\n
                            showSeparator: false,\r\n
                            items: [{\r\n
                                caption: "10:56",\r\n
                                value: "HH:mm",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "21:56:00",\r\n
                                value: "HH:MM:ss",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "05:56 AM",\r\n
                                tplval: "hh:mm tt",\r\n
                                value: "hh:mm AM/PM",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "05:56:00 AM",\r\n
                                tplval: "hh:mm:ss tt",\r\n
                                value: "hh:mm:ss AM/PM",\r\n
                                template: formatTemplate\r\n
                            },\r\n
                            {\r\n
                                caption: "38:56:00",\r\n
                                value: "[h]:mm:ss",\r\n
                                template: formatTemplate\r\n
                            }]\r\n
                        })\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtPercentage,\r\n
                        value: me.ascFormatOptions.Percentage\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtText,\r\n
                        value: me.ascFormatOptions.Text\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnPercentStyle = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-percent-style",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-percent-style",\r\n
                hint: me.tipDigStylePercent,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                formatId: me.ascFormatOptions.Percent\r\n
            });\r\n
            me.btnCurrencyStyle = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-accounting-style",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-currency-style",\r\n
                hint: me.tipDigStyleAccounting,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                formatId: me.ascFormatOptions.Accounting,\r\n
                split: true,\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "min-width: 120px;",\r\n
                    items: [{\r\n
                        caption: me.txtDollar,\r\n
                        value: me.ascFormatOptions.Accounting\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtEuro,\r\n
                        value: \'_(€* #,##0.00_);_(€* (#,##0.00);_(€* "-"??_);_(@_)\'\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtPound,\r\n
                        value: \'_(£* #,##0.00_);_(£* (#,##0.00);_(£* "-"??_);_(@_)\'\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtRouble,\r\n
                        value: \'_-* #,##0.00[$р.-419]_-;-* #,##0.00[$р.-419]_-;_-* "-"??[$р.-419]_-;_-@_-\'\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtYen,\r\n
                        value: \'_(¥* #,##0.00_);_(¥* (#,##0.00);_(¥* "-"??_);_(@_)\'\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnDecDecimal = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-decdecimal",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-decdecimal",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                hint: me.tipDecDecimal\r\n
            });\r\n
            me.btnIncDecimal = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-incdecimal",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-incdecimal",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                hint: me.tipIncDecimal\r\n
            });\r\n
            me.btnInsertFormula = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-insertformula",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-formula",\r\n
                hint: me.txtFormula,\r\n
                split: true,\r\n
                lock: [_set.editText, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.selRange, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "min-width: 110px",\r\n
                    items: [{\r\n
                        caption: "SUM",\r\n
                        value: "SUM"\r\n
                    },\r\n
                    {\r\n
                        caption: "MIN",\r\n
                        value: "MIN"\r\n
                    },\r\n
                    {\r\n
                        caption: "MAX",\r\n
                        value: "MAX"\r\n
                    },\r\n
                    {\r\n
                        caption: "COUNT",\r\n
                        value: "COUNT"\r\n
                    },\r\n
                    {\r\n
                        caption: "--"\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtAdditional,\r\n
                        value: "more"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnClearStyle = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-clear",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-clearstyle",\r\n
                hint: me.tipClearStyle,\r\n
                lock: [_set.lostConnect, _set.coAuth, _set.selRange],\r\n
                menu: new Common.UI.Menu({\r\n
                    style: "min-width: 110px",\r\n
                    items: [{\r\n
                        caption: me.txtClearAll,\r\n
                        value: c_oAscCleanOptions.All\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearText,\r\n
                        lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth],\r\n
                        value: c_oAscCleanOptions.Text\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearFormat,\r\n
                        lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth],\r\n
                        value: c_oAscCleanOptions.Format\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearComments,\r\n
                        lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth],\r\n
                        value: c_oAscCleanOptions.Comments\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearHyper,\r\n
                        lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth],\r\n
                        value: c_oAscCleanOptions.Hyperlinks\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnCopyStyle = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-copystyle",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-copystyle",\r\n
                hint: this.tipCopyStyle,\r\n
                lock: [_set.editCell, _set.lostConnect, _set.coAuth, _set.selChart],\r\n
                enableToggle: true\r\n
            });\r\n
            me.btnAddCell = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-addcell",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-addcell",\r\n
                hint: me.tipInsertOpt,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.textInsRight,\r\n
                        value: c_oAscInsertOptions.InsertCellsAndShiftRight\r\n
                    },\r\n
                    {\r\n
                        caption: me.textInsDown,\r\n
                        value: c_oAscInsertOptions.InsertCellsAndShiftDown\r\n
                    },\r\n
                    {\r\n
                        caption: me.textEntireRow,\r\n
                        value: c_oAscInsertOptions.InsertRows\r\n
                    },\r\n
                    {\r\n
                        caption: me.textEntireCol,\r\n
                        value: c_oAscInsertOptions.InsertColumns\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnDeleteCell = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-delcell",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-delcell",\r\n
                hint: me.tipDeleteOpt,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.textDelLeft,\r\n
                        value: c_oAscDeleteOptions.DeleteCellsAndShiftLeft\r\n
                    },\r\n
                    {\r\n
                        caption: me.textDelUp,\r\n
                        value: c_oAscDeleteOptions.DeleteCellsAndShiftTop\r\n
                    },\r\n
                    {\r\n
                        caption: me.textEntireRow,\r\n
                        value: c_oAscDeleteOptions.DeleteRows\r\n
                    },\r\n
                    {\r\n
                        caption: me.textEntireCol,\r\n
                        value: c_oAscDeleteOptions.DeleteColumns\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnColorSchemas = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-colorschemas",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-colorschemas",\r\n
                hint: me.tipColorSchemas,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [],\r\n
                    maxHeight: 600,\r\n
                    restoreHeight: 600\r\n
                }).on("render:after", function (mnu) {\r\n
                    this.scroller = new Common.UI.Scroller({\r\n
                        el: $(this.el).find(".dropdown-menu "),\r\n
                        useKeyboard: this.enableKeyEvents && !this.handleSelect,\r\n
                        minScrollbarLength: 40,\r\n
                        alwaysVisibleY: true\r\n
                    });\r\n
                }).on("show:after", function (btn, e) {\r\n
                    var mnu = $(this.el).find(".dropdown-menu "),\r\n
                    docH = $(document).height(),\r\n
                    menuH = mnu.outerHeight(),\r\n
                    top = parseInt(mnu.css("top"));\r\n
                    if (menuH > docH) {\r\n
                        mnu.css("max-height", (docH - parseInt(mnu.css("padding-top")) - parseInt(mnu.css("padding-bottom")) - 5) + "px");\r\n
                        this.scroller.update({\r\n
                            minScrollbarLength: 40\r\n
                        });\r\n
                    } else {\r\n
                        if (mnu.height() < this.options.restoreHeight) {\r\n
                            mnu.css("max-height", (Math.min(docH - parseInt(mnu.css("padding-top")) - parseInt(mnu.css("padding-bottom")) - 5, this.options.restoreHeight)) + "px");\r\n
                            menuH = mnu.outerHeight();\r\n
                            if (top + menuH > docH) {\r\n
                                mnu.css("top", 0);\r\n
                            }\r\n
                            this.scroller.update({\r\n
                                minScrollbarLength: 40\r\n
                            });\r\n
                        }\r\n
                    }\r\n
                })\r\n
            });\r\n
            me.mnuZoomIn = dummyCmp();\r\n
            me.mnuZoomOut = dummyCmp();\r\n
            me.btnShowMode = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-showmode",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-showmode",\r\n
                hint: me.tipViewSettings,\r\n
                lock: [_set.menuFileOpen, _set.editCell],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [me.mnuitemCompactToolbar = new Common.UI.MenuItem({\r\n
                        caption: me.textCompactToolbar,\r\n
                        checkable: true,\r\n
                        checked: me.isCompactView,\r\n
                        value: "compact"\r\n
                    }), me.mnuitemHideTitleBar = new Common.UI.MenuItem({\r\n
                        caption: me.textHideTBar,\r\n
                        checkable: true,\r\n
                        checked: !!options.title,\r\n
                        value: "title"\r\n
                    }), {\r\n
                        caption: me.textHideFBar,\r\n
                        checkable: true,\r\n
                        checked: !!options.formula,\r\n
                        value: "formula"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textHideHeadings,\r\n
                        checkable: true,\r\n
                        checked: !!options.headings,\r\n
                        value: "headings"\r\n
                    },\r\n
                    {\r\n
                        caption: me.textHideGridlines,\r\n
                        checkable: true,\r\n
                        checked: false,\r\n
                        value: "gridlines"\r\n
                    },\r\n
                    {\r\n
                        caption: this.textFreezePanes,\r\n
                        checkable: true,\r\n
                        checked: false,\r\n
                        value: "freezepanes"\r\n
                    },\r\n
                    {\r\n
                        caption: "--"\r\n
                    },\r\n
                    (new Common.UI.MenuItem({\r\n
                        template: _.template([\'<div id="id-toolbar-menu-zoom" class="menu-zoom" style="height: 25px;" \', "<% if(!_.isUndefined(options.stopPropagation)) { %>", \'data-stopPropagation="true"\', "<% } %>", ">", \'<label class="title">\' + me.textZoom + "</label>", \'<button id="id-menu-zoom-in" type="button" style="float:right; margin: 2px 5px 0 0;" class="btn small btn-toolbar btn-toolbar-default"><span class="btn-icon btn-zoomin">&nbsp;</span></button>\', \'<label class="zoom">100%</label>\', \'<button id="id-menu-zoom-out" type="button" style="float:right; margin-top: 2px;" class="btn small btn-toolbar btn-toolbar-default"><span class="btn-icon btn-zoomout">&nbsp;</span></button>\', "</div>"].join("")),\r\n
                        stopPropagation: true\r\n
                    }))]\r\n
                })\r\n
            }).on("render:after", _.bind(function (cmp) {\r\n
                me.mnuZoomOut = new Common.UI.Button({\r\n
                    el: $("#id-menu-zoom-out"),\r\n
                    cls: "btn-toolbar btn-toolbar-default"\r\n
                });\r\n
                me.mnuZoomIn = new Common.UI.Button({\r\n
                    el: $("#id-menu-zoom-in"),\r\n
                    cls: "btn-toolbar btn-toolbar-default"\r\n
                });\r\n
            }), me);\r\n
            me.btnSettings = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-settings",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-settings",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth],\r\n
                hint: me.tipAdvSettings\r\n
            });\r\n
            me.btnHorizontalAlign = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-halign",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-align-left",\r\n
                hint: me.tipHAligh,\r\n
                icls: "btn-align-left",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.tipAlignLeft,\r\n
                        iconCls: "mnu-align-left",\r\n
                        icls: "btn-align-left",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "halignGroup",\r\n
                        checked: true,\r\n
                        value: "left"\r\n
                    },\r\n
                    {\r\n
                        caption: me.tipAlignCenter,\r\n
                        iconCls: "mnu-align-center",\r\n
                        icls: "btn-align-center",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "halignGroup",\r\n
                        value: "center"\r\n
                    },\r\n
                    {\r\n
                        caption: me.tipAlignRight,\r\n
                        iconCls: "mnu-align-right",\r\n
                        icls: "btn-align-right",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "halignGroup",\r\n
                        value: "right"\r\n
                    },\r\n
                    {\r\n
                        caption: me.tipAlignJust,\r\n
                        iconCls: "mnu-align-just",\r\n
                        icls: "btn-align-just",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "halignGroup",\r\n
                        value: "justify"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnVerticalAlign = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-valign",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-valign-bottom",\r\n
                hint: me.tipVAligh,\r\n
                icls: "btn-valign-bottom",\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.lostConnect, _set.coAuth],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [{\r\n
                        caption: me.tipAlignTop,\r\n
                        iconCls: "mnu-valign-top",\r\n
                        icls: "btn-valign-top",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "valignGroup",\r\n
                        value: "top"\r\n
                    },\r\n
                    {\r\n
                        caption: me.tipAlignCenter,\r\n
                        iconCls: "mnu-valign-middle",\r\n
                        icls: "btn-valign-middle",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        toggleGroup: "valignGroup",\r\n
                        value: "center"\r\n
                    },\r\n
                    {\r\n
                        caption: me.tipAlignBottom,\r\n
                        iconCls: "mnu-valign-bottom",\r\n
                        icls: "btn-valign-bottom",\r\n
                        checkable: true,\r\n
                        allowDepress: true,\r\n
                        checked: true,\r\n
                        toggleGroup: "valignGroup",\r\n
                        value: "bottom"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.btnAutofilter = new Common.UI.Button({\r\n
                id: "id-toolbar-btn-autofilter",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-autofilter",\r\n
                hint: me.tipAutofilter,\r\n
                lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.lostConnect, _set.coAuth, _set.ruleFilter],\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [me.mnuitemSortAZ = new Common.UI.MenuItem({\r\n
                        caption: me.txtSortAZ,\r\n
                        iconCls: "mnu-sort-asc",\r\n
                        lock: [_set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth, _set.ruleFilter],\r\n
                        value: "ascending"\r\n
                    }), me.mnuitemSortZA = new Common.UI.MenuItem({\r\n
                        caption: me.txtSortZA,\r\n
                        iconCls: "mnu-sort-desc",\r\n
                        lock: [_set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth, _set.ruleFilter],\r\n
                        value: "descending"\r\n
                    }), me.mnuitemAutoFilter = new Common.UI.MenuItem({\r\n
                        caption: me.txtFilter,\r\n
                        iconCls: "mnu-filter-add",\r\n
                        checkable: true,\r\n
                        lock: [_set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth, _set.ruleFilter],\r\n
                        value: "set-filter"\r\n
                    }), me.mnuitemClearFilter = new Common.UI.MenuItem({\r\n
                        caption: me.txtClearFilter,\r\n
                        iconCls: "mnu-filter-clear",\r\n
                        lock: [_set.editCell, _set.selChart, _set.selChartText, _set.selShape, _set.selShapeText, _set.selImage, _set.coAuth, _set.ruleDelFilter],\r\n
                        value: "clear-filter"\r\n
                    })]\r\n
                })\r\n
            });\r\n
            me.mnuPrint = me.btnPrint.menu;\r\n
            me.lockControls = [me.cmbFontName, me.cmbFontSize, me.btnIncFontSize, me.btnDecFontSize, me.btnBold, me.btnItalic, me.btnUnderline, me.btnTextColor, me.btnHorizontalAlign, me.btnAlignLeft, me.btnAlignCenter, me.btnAlignRight, me.btnAlignJust, me.btnVerticalAlign, me.btnAlignTop, me.btnAlignMiddle, me.btnAlignBottom, me.btnWrap, me.btnTextOrient, me.btnBackColor, me.btnMerge, me.btnInsertFormula, me.btnIncDecimal, me.btnInsertShape, me.btnInsertText, me.btnSortUp, me.btnSortDown, me.btnSetAutofilter, me.btnClearAutofilter, me.btnTableTemplate, me.btnPercentStyle, me.btnCurrencyStyle, me.btnDecDecimal, me.btnAddCell, me.btnDeleteCell, me.btnNumberFormat, me.btnBorders, me.btnInsertImage, me.btnInsertHyperlink, me.btnInsertChart, me.btnColorSchemas, me.btnAutofilter, me.btnCopy, me.btnPaste, me.btnSettings, me.listStyles, me.btnPrint, me.btnShowMode, me.btnClearStyle, me.btnCopyStyle];\r\n
            var hidetip = window.localStorage.getItem("sse-hide-synch");\r\n
            me.showSynchTip = !(hidetip && parseInt(hidetip) == 1);\r\n
            me.needShowSynchTip = false;\r\n
            var _temp_array = [me.cmbFontName, me.cmbFontSize, me.btnAlignLeft, me.btnAlignCenter, me.btnAlignRight, me.btnAlignJust, me.btnAlignTop, me.btnAlignMiddle, me.btnAlignBottom, me.btnHorizontalAlign, me.btnVerticalAlign, me.btnInsertImage, me.btnInsertText, me.btnInsertShape, me.btnIncFontSize, me.btnDecFontSize, me.btnBold, me.btnItalic, me.btnUnderline, me.btnTextColor, me.btnBackColor, me.btnInsertHyperlink, me.btnBorders, me.btnTextOrient, me.btnPercentStyle, me.btnCurrencyStyle, me.btnColorSchemas, me.btnSettings, me.btnInsertFormula, me.btnDecDecimal, me.btnIncDecimal, me.btnNumberFormat, me.btnWrap, me.btnInsertChart, me.btnMerge, me.btnAddCell, me.btnDeleteCell, me.btnShowMode, me.btnPrint, me.btnAutofilter, me.btnSortUp, me.btnSortDown, me.btnTableTemplate, me.btnSetAutofilter, me.btnClearAutofilter, me.btnSave, me.btnClearStyle, me.btnCopyStyle, me.btnCopy, me.btnPaste];\r\n
            _.each(_temp_array, function (cmp) {\r\n
                if (cmp && _.isFunction(cmp.setDisabled)) {\r\n
                    cmp.setDisabled(true);\r\n
                }\r\n
            });\r\n
            return this;\r\n
        },\r\n
        lockToolbar: function (causes, lock, opts) { ! opts && (opts = {});\r\n
            var controls = opts.array || this.lockControls;\r\n
            opts.merge && (controls = _.union(this.lockControls, controls));\r\n
            function doLock(cmp, cause) {\r\n
                if (_.contains(cmp.options.lock, cause)) {\r\n
                    var index = cmp.keepState.indexOf(cause);\r\n
                    if (lock) {\r\n
                        if (index < 0) {\r\n
                            cmp.keepState.push(cause);\r\n
                        }\r\n
                    } else {\r\n
                        if (! (index < 0)) {\r\n
                            cmp.keepState.splice(index, 1);\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            _.each(controls, function (item) {\r\n
                if (_.isFunction(item.setDisabled)) { ! item.keepState && (item.keepState = []);\r\n
                    if (opts.clear && opts.clear.length > 0 && item.keepState.length > 0) {\r\n
                        item.keepState = _.difference(item.keepState, opts.clear);\r\n
                    }\r\n
                    _.isArray(causes) ? _.each(causes, function (c) {\r\n
                        doLock(item, c);\r\n
                    }) : doLock(item, causes);\r\n
                    if (! (item.keepState.length > 0)) {\r\n
                        item.isDisabled() && item.setDisabled(false);\r\n
                    } else { ! item.isDisabled() && item.setDisabled(true);\r\n
                    }\r\n
                }\r\n
            });\r\n
        },\r\n
        render: function (isEditDiagram) {\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            this.trigger("render:before", this);\r\n
            el.html(this.template({\r\n
                isEditDiagram: isEditDiagram,\r\n
                isCompactView: this.isCompactView\r\n
            }));\r\n
            me.rendererComponents(isEditDiagram ? "diagram" : this.isCompactView ? "short" : "full");\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        rendererComponents: function (mode) {\r\n
            var replacePlacholder = function (id, cmp) {\r\n
                var placeholderEl = $(id),\r\n
                placeholderDom = placeholderEl.get(0);\r\n
                if (placeholderDom) {\r\n
                    if (cmp.rendered) {\r\n
                        cmp.el = document.getElementById(cmp.id);\r\n
                        placeholderDom.appendChild(document.getElementById(cmp.id));\r\n
                    } else {\r\n
                        cmp.render(placeholderEl);\r\n
                    }\r\n
                }\r\n
            };\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-field-fontname", this.cmbFontName);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-field-fontsize", this.cmbFontSize);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-newdocument", this.btnNewDocument);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-opendocument", this.btnOpenDocument);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-print", this.btnPrint);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-save", this.btnSave);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-undo", this.btnUndo);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-redo", this.btnRedo);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-copy", this.btnCopy);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-paste", this.btnPaste);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-incfont", this.btnIncFontSize);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-decfont", this.btnDecFontSize);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-bold", this.btnBold);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-italic", this.btnItalic);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-underline", this.btnUnderline);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-fontcolor", this.btnTextColor);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-fillparag", this.btnBackColor);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-borders", this.btnBorders);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-align-left", this.btnAlignLeft);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-align-center", this.btnAlignCenter);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-align-right", this.btnAlignRight);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-align-just", this.btnAlignJust);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-merge", this.btnMerge);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-top", this.btnAlignTop);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-middle", this.btnAlignMiddle);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-bottom", this.btnAlignBottom);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-wrap", this.btnWrap);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-text-orient", this.btnTextOrient);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-insertimage", this.btnInsertImage);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-inserthyperlink", this.btnInsertHyperlink);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-insertshape", this.btnInsertShape);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-text", this.btnInsertText);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-sortdesc", this.btnSortDown);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-sortasc", this.btnSortUp);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-setfilter", this.btnSetAutofilter);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-clear-filter", this.btnClearAutofilter);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-table-tpl", this.btnTableTemplate);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-format", this.btnNumberFormat);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-percents", this.btnPercentStyle);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-currency", this.btnCurrencyStyle);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-digit-dec", this.btnDecDecimal);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-digit-inc", this.btnIncDecimal);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-formula", this.btnInsertFormula);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-clear", this.btnClearStyle);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-copystyle", this.btnCopyStyle);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-cell-ins", this.btnAddCell);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-cell-del", this.btnDeleteCell);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-colorschemas", this.btnColorSchemas);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-hidebars", this.btnShowMode);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-settings", this.btnSettings);\r\n
            replacePlacholder("#id-toolbar-" + mode + "-placeholder-btn-insertchart", this.btnInsertChart);\r\n
            replacePlacholder("#id-toolbar-diagram-placeholder-btn-chart", this.btnEditChart);\r\n
            replacePlacholder("#id-toolbar-short-placeholder-btn-halign", this.btnHorizontalAlign);\r\n
            replacePlacholder("#id-toolbar-short-placeholder-btn-valign", this.btnVerticalAlign);\r\n
            replacePlacholder("#id-toolbar-short-placeholder-btn-filter", this.btnAutofilter);\r\n
            replacePlacholder("#id-toolbar-full-placeholder-field-styles", this.listStyles);\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            if (!this.mode.isEditDiagram) {\r\n
                this.api.asc_registerCallback("asc_onCollaborativeChanges", _.bind(this.onApiCollaborativeChanges, this));\r\n
                this.api.asc_registerCallback("asc_onSendThemeColorSchemes", _.bind(this.onApiSendThemeColorSchemes, this));\r\n
                this.api.asc_registerCallback("asc_onAuthParticipantsChanged", _.bind(this.onApiUsersChanged, this));\r\n
                this.api.asc_registerCallback("asc_onParticipantsChanged", _.bind(this.onApiUsersChanged, this));\r\n
            }\r\n
            return this;\r\n
        },\r\n
        setMode: function (mode) {\r\n
            if (mode.isDisconnected) {\r\n
                this.lockToolbar(SSE.enumLock.lostConnect, true);\r\n
                this.lockToolbar(SSE.enumLock.lostConnect, true, {\r\n
                    array: [this.btnEditChart, this.btnUndo, this.btnRedo, this.btnOpenDocument, this.btnNewDocument, this.btnSave]\r\n
                });\r\n
            } else {\r\n
                this.mode = mode;\r\n
                if (!mode.nativeApp) {\r\n
                    var nativeBtnGroup = $(".toolbar-group-native");\r\n
                    if (nativeBtnGroup) {\r\n
                        nativeBtnGroup.hide();\r\n
                    }\r\n
                }\r\n
                if (mode.isDesktopApp) {\r\n
                    $(".toolbar-group-native").hide();\r\n
                    this.mnuitemHideTitleBar.hide();\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiSendThemeColorSchemes: function (schemas) {\r\n
            var me = this;\r\n
            this.mnuColorSchema = this.btnColorSchemas.menu;\r\n
            if (this.mnuColorSchema && this.mnuColorSchema.items.length > 0) {\r\n
                _.each(this.mnuColorSchema.items, function (item) {\r\n
                    item.remove();\r\n
                });\r\n
            }\r\n
            if (this.mnuColorSchema == null) {\r\n
                this.mnuColorSchema = new Common.UI.Menu({\r\n
                    maxHeight: 600,\r\n
                    restoreHeight: 600\r\n
                }).on("render:after", function (mnu) {\r\n
                    this.scroller = new Common.UI.Scroller({\r\n
                        el: $(this.el).find(".dropdown-menu "),\r\n
                        useKeyboard: this.enableKeyEvents && !this.handleSelect,\r\n
                        minScrollbarLength: 40\r\n
                    });\r\n
                });\r\n
            }\r\n
            this.mnuColorSchema.items = [];\r\n
            var itemTemplate = _.template([\'<a id="<%= id %>" class="<%= options.cls %>" tabindex="-1" type="menuitem">\', \'<span class="colors">\', "<% _.each(options.colors, function(color) { %>", \'<span class="color" style="background: <%= color %>;"></span>\', "<% }) %>", "</span>", \'<span class="text"><%= caption %></span>\', "</a>"].join(""));\r\n
            _.each(schemas, function (schema, index) {\r\n
                var colors = schema.get_colors();\r\n
                var schemecolors = [];\r\n
                for (var j = 2; j < 7; j++) {\r\n
                    var clr = "#" + Common.Utils.ThemeColor.getHexColor(colors[j].get_r(), colors[j].get_g(), colors[j].get_b());\r\n
                    schemecolors.push(clr);\r\n
                }\r\n
                if (index == 21) {\r\n
                    this.mnuColorSchema.addItem({\r\n
                        caption: "--"\r\n
                    });\r\n
                } else {\r\n
                    this.mnuColorSchema.addItem({\r\n
                        template: itemTemplate,\r\n
                        cls: "color-schemas-menu",\r\n
                        colors: schemecolors,\r\n
                        caption: (index < 21) ? (me.SchemeNames[index] || schema.get_name()) : schema.get_name(),\r\n
                        value: index\r\n
                    });\r\n
                }\r\n
            },\r\n
            this);\r\n
        },\r\n
        onApiCollaborativeChanges: function () {\r\n
            if (this._state.hasCollaborativeChanges) {\r\n
                return;\r\n
            }\r\n
            if (!this.btnSave.rendered) {\r\n
                this.needShowSynchTip = true;\r\n
                return;\r\n
            }\r\n
            this._state.hasCollaborativeChanges = true;\r\n
            var iconEl = $(".btn-icon", this.btnSave.cmpEl);\r\n
            iconEl.removeClass(this.btnSaveCls);\r\n
            iconEl.addClass("btn-synch");\r\n
            if (this.showSynchTip) {\r\n
                this.btnSave.updateHint("");\r\n
                if (this.synchTooltip === undefined) {\r\n
                    this.createSynchTip();\r\n
                }\r\n
                this.synchTooltip.show();\r\n
            } else {\r\n
                this.btnSave.updateHint(this.tipSynchronize + Common.Utils.String.platformKey("Ctrl+S"));\r\n
            }\r\n
            this.btnSave.setDisabled(false);\r\n
        },\r\n
        createSynchTip: function () {\r\n
            this.synchTooltip = new Common.UI.SynchronizeTip({\r\n
                target: $("#id-toolbar-btn-save")\r\n
            });\r\n
            this.synchTooltip.on("dontshowclick", function () {\r\n
                this.showSynchTip = false;\r\n
                this.synchTooltip.hide();\r\n
                this.btnSave.updateHint(this.tipSynchronize + Common.Utils.String.platformKey("Ctrl+S"));\r\n
                window.localStorage.setItem("sse-hide-synch", 1);\r\n
            },\r\n
            this);\r\n
            this.synchTooltip.on("closeclick", function () {\r\n
                this.synchTooltip.hide();\r\n
                this.btnSave.updateHint(this.tipSynchronize + Common.Utils.String.platformKey("Ctrl+S"));\r\n
            },\r\n
            this);\r\n
        },\r\n
        synchronizeChanges: function () {\r\n
            if (this.btnSave.rendered) {\r\n
                var iconEl = $(".btn-icon", this.btnSave.cmpEl);\r\n
                if (iconEl.hasClass("btn-synch")) {\r\n
                    iconEl.removeClass("btn-synch");\r\n
                    iconEl.addClass(this.btnSaveCls);\r\n
                    if (this.synchTooltip) {\r\n
                        this.synchTooltip.hide();\r\n
                    }\r\n
                    this.btnSave.updateHint(this.btnSaveTip);\r\n
                    this.btnSave.setDisabled(true);\r\n
                    this._state.hasCollaborativeChanges = false;\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiUsersChanged: function (users) {\r\n
            var length = _.size(users);\r\n
            var cls = (length > 1) ? "btn-save-coauth" : "btn-save";\r\n
            if (cls !== this.btnSaveCls && this.btnSave.rendered) {\r\n
                this.btnSaveTip = ((length > 1) ? this.tipSaveCoauth : this.tipSave) + Common.Utils.String.platformKey("Ctrl+S");\r\n
                var iconEl = $(".btn-icon", this.btnSave.cmpEl);\r\n
                if (!iconEl.hasClass("btn-synch")) {\r\n
                    iconEl.removeClass(this.btnSaveCls);\r\n
                    iconEl.addClass(cls);\r\n
                    this.btnSave.updateHint(this.btnSaveTip);\r\n
                }\r\n
                this.btnSaveCls = cls;\r\n
            }\r\n
        },\r\n
        textBold: "Bold",\r\n
        textItalic: "Italic",\r\n
        textUnderline: "Underline",\r\n
        tipFontName: "Font Name",\r\n
        tipFontSize: "Font Size",\r\n
        tipCellStyle: "Cell Style",\r\n
        tipCopy: "Copy",\r\n
        tipPaste: "Paste",\r\n
        tipUndo: "Undo",\r\n
        tipRedo: "Redo",\r\n
        tipPrint: "Print",\r\n
        tipSave: "Save",\r\n
        tipFontColor: "Font color",\r\n
        tipPrColor: "Background color",\r\n
        tipClearStyle: "Clear",\r\n
        tipCopyStyle: "Copy Style",\r\n
        tipBack: "Back",\r\n
        tipHAligh: "Horizontal Align",\r\n
        tipVAligh: "Vertical Align",\r\n
        tipAlignLeft: "Align Left",\r\n
        tipAlignRight: "Align Right",\r\n
        tipAlignCenter: "Align Center",\r\n
        tipAlignJust: "Justified",\r\n
        textAlignTop: "Align text to the top",\r\n
        textAlignMiddle: "Align text to the middle",\r\n
        textAlignBottom: "Align text to the bottom",\r\n
        tipNumFormat: "Number Format",\r\n
        txtNumber: "Number",\r\n
        txtInteger: "Integer",\r\n
        txtGeneral: "General",\r\n
        txtCustom: "Custom",\r\n
        txtCurrency: "Currency",\r\n
        txtDollar: "$ Dollar",\r\n
        txtEuro: "€ Euro",\r\n
        txtRouble: "р. Rouble",\r\n
        txtPound: "£ Pound",\r\n
        txtYen: "¥ Yen",\r\n
        txtAccounting: "Accounting",\r\n
        txtDate: "Date",\r\n
        txtTime: "Time",\r\n
        txtDateTime: "Date & Time",\r\n
        txtPercentage: "Percentage",\r\n
        txtScientific: "Scientific",\r\n
        txtText: "Text",\r\n
        tipBorders: "Borders",\r\n
        textOutBorders: "Outside Borders",\r\n
        textAllBorders: "All Borders",\r\n
        textTopBorders: "Top Borders",\r\n
        textBottomBorders: "Bottom Borders",\r\n
        textLeftBorders: "Left Borders",\r\n
        textRightBorders: "Right Borders",\r\n
        textNoBorders: "No Borders",\r\n
        textInsideBorders: "Inside Borders",\r\n
        textMiddleBorders: "Inside Horizontal Borders",\r\n
        textCenterBorders: "Inside Vertical Borders",\r\n
        textDiagDownBorder: "Diagonal Down Border",\r\n
        textDiagUpBorder: "Diagonal Up Border",\r\n
        tipWrap: "Wrap Text",\r\n
        txtClearAll: "All",\r\n
        txtClearText: "Text",\r\n
        txtClearFormat: "Format",\r\n
        txtClearFormula: "Formula",\r\n
        txtClearHyper: "Hyperlink",\r\n
        txtClearComments: "Comments",\r\n
        tipMerge: "Merge",\r\n
        txtMergeCenter: "Merge Center",\r\n
        txtMergeAcross: "Merge Across",\r\n
        txtMergeCells: "Merge Cells",\r\n
        txtUnmerge: "Unmerge Cells",\r\n
        tipIncDecimal: "Increase Decimal",\r\n
        tipDecDecimal: "Decrease Decimal",\r\n
        tipAutofilter: "Set Autofilter",\r\n
        tipInsertImage: "Insert Picture",\r\n
        tipInsertHyperlink: "Add Hyperlink",\r\n
        tipSynchronize: "The document has been changed by another user. Please click to save your changes and reload the updates.",\r\n
        tipIncFont: "Increment font size",\r\n
        tipDecFont: "Decrement font size",\r\n
        tipInsertText: "Insert Text",\r\n
        tipInsertShape: "Insert Autoshape",\r\n
        tipDigStylePercent: "Percent Style",\r\n
        tipDigStyleAccounting: "Accounting Style",\r\n
        tipViewSettings: "View Settings",\r\n
        tipAdvSettings: "Advanced Settings",\r\n
        tipTextOrientation: "Orientation",\r\n
        tipInsertOpt: "Insert Cells",\r\n
        tipDeleteOpt: "Delete Cells",\r\n
        tipAlignTop: "Align Top",\r\n
        tipAlignMiddle: "Align Middle",\r\n
        tipAlignBottom: "Align Bottom",\r\n
        textBordersWidth: "Borders Width",\r\n
        textBordersColor: "Borders Color",\r\n
        textAlignLeft: "Left align text",\r\n
        textAlignRight: "Right align text",\r\n
        textAlignCenter: "Center text",\r\n
        textAlignJust: "Justify",\r\n
        txtSort: "Sort",\r\n
        txtFormula: "Insert Function",\r\n
        txtNoBorders: "No borders",\r\n
        txtAdditional: "Additional",\r\n
        mniImageFromFile: "Picture from file",\r\n
        mniImageFromUrl: "Picture from url",\r\n
        textNewColor: "Add New Custom Color",\r\n
        tipInsertChart: "Insert Chart",\r\n
        tipEditChart: "Edit Chart",\r\n
        textPrint: "Print",\r\n
        textPrintOptions: "Print Options",\r\n
        textThemeColors: "Theme Colors",\r\n
        textStandartColors: "Standart Colors",\r\n
        tipColorSchemas: "Change Color Scheme",\r\n
        tipNewDocument: "New Document",\r\n
        tipOpenDocument: "Open Document",\r\n
        txtSortAZ: "Sort A to Z",\r\n
        txtSortZA: "Sort Z to A",\r\n
        txtFilter: "Filter",\r\n
        txtTableTemplate: "Format As Table Template",\r\n
        textHorizontal: "Horizontal Text",\r\n
        textCounterCw: "Angle Counterclockwise",\r\n
        textClockwise: "Angle Clockwise",\r\n
        textRotateUp: "Rotate Text Up",\r\n
        textRotateDown: "Rotate Text Down",\r\n
        textInsRight: "Shift Cells Right",\r\n
        textInsDown: "Shift Cells Down",\r\n
        textEntireRow: "Entire Row",\r\n
        textEntireCol: "Entire Column",\r\n
        textDelLeft: "Shift Cells Left",\r\n
        textDelUp: "Shift Cells Up",\r\n
        textZoom: "Zoom",\r\n
        textCompactToolbar: "Compact Toolbar",\r\n
        textHideTBar: "Hide Title Bar",\r\n
        textHideFBar: "Hide Formula Bar",\r\n
        textHideHeadings: "Hide Headings",\r\n
        textHideGridlines: "Hide Gridlines",\r\n
        textFreezePanes: "Freeze Panes",\r\n
        txtScheme1: "Office",\r\n
        txtScheme2: "Grayscale",\r\n
        txtScheme3: "Apex",\r\n
        txtScheme4: "Aspect",\r\n
        txtScheme5: "Civic",\r\n
        txtScheme6: "Concourse",\r\n
        txtScheme7: "Equity",\r\n
        txtScheme8: "Flow",\r\n
        txtScheme9: "Foundry",\r\n
        txtScheme10: "Median",\r\n
        txtScheme11: "Metro",\r\n
        txtScheme12: "Module",\r\n
        txtScheme13: "Opulent",\r\n
        txtScheme14: "Oriel",\r\n
        txtScheme15: "Origin",\r\n
        txtScheme16: "Paper",\r\n
        txtScheme17: "Solstice",\r\n
        txtScheme18: "Technic",\r\n
        txtScheme19: "Trek",\r\n
        txtScheme20: "Urban",\r\n
        txtScheme21: "Verve",\r\n
        txtClearFilter: "Clear Filter",\r\n
        tipSaveCoauth: "Save your changes for the other users to see them."\r\n
    },\r\n
    SSE.Views.Toolbar || {}));\r\n
});

]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
