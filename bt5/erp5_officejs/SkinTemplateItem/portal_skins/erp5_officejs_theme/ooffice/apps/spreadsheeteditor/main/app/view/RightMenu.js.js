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
            <value> <string>ts44321339.22</string> </value>
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
 var SCALE_MIN = 40;\r\n
var MENU_SCALE_PART = 260;\r\n
define(["text!spreadsheeteditor/main/app/template/RightMenu.template", "jquery", "underscore", "backbone", "common/main/lib/component/Button", "common/main/lib/component/MetricSpinner", "common/main/lib/component/CheckBox", "spreadsheeteditor/main/app/view/ParagraphSettings", "spreadsheeteditor/main/app/view/ImageSettings", "spreadsheeteditor/main/app/view/ChartSettings", "spreadsheeteditor/main/app/view/ShapeSettings", "common/main/lib/component/Scroller"], function (menuTemplate, $, _, Backbone) {\r\n
    SSE.Views.RightMenu = Backbone.View.extend(_.extend({\r\n
        el: "#right-menu",\r\n
        template: _.template(menuTemplate),\r\n
        events: {},\r\n
        initialize: function () {\r\n
            this.minimizedMode = true;\r\n
            this.btnText = new Common.UI.Button({\r\n
                hint: this.txtParagraphSettings,\r\n
                asctype: c_oAscTypeSelectElement.Paragraph,\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "tabpanelbtnsGroup"\r\n
            });\r\n
            this.btnImage = new Common.UI.Button({\r\n
                hint: this.txtImageSettings,\r\n
                asctype: c_oAscTypeSelectElement.Image,\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "tabpanelbtnsGroup"\r\n
            });\r\n
            this.btnChart = new Common.UI.Button({\r\n
                hint: this.txtChartSettings,\r\n
                asctype: c_oAscTypeSelectElement.Chart,\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "tabpanelbtnsGroup"\r\n
            });\r\n
            this.btnShape = new Common.UI.Button({\r\n
                hint: this.txtShapeSettings,\r\n
                asctype: c_oAscTypeSelectElement.Shape,\r\n
                enableToggle: true,\r\n
                disabled: true,\r\n
                toggleGroup: "tabpanelbtnsGroup"\r\n
            });\r\n
            this._settings = [];\r\n
            this._settings[c_oAscTypeSelectElement.Paragraph] = {\r\n
                panel: "id-paragraph-settings",\r\n
                btn: this.btnText\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Image] = {\r\n
                panel: "id-image-settings",\r\n
                btn: this.btnImage\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Shape] = {\r\n
                panel: "id-shape-settings",\r\n
                btn: this.btnShape\r\n
            };\r\n
            this._settings[c_oAscTypeSelectElement.Chart] = {\r\n
                panel: "id-chart-settings",\r\n
                btn: this.btnChart\r\n
            };\r\n
            return this;\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            this.trigger("render:before", this);\r\n
            el.css("width", "40px");\r\n
            el.css("z-index", 101);\r\n
            el.show();\r\n
            el.html(this.template({}));\r\n
            this.btnText.el = $("#id-right-menu-text");\r\n
            this.btnText.render();\r\n
            this.btnImage.el = $("#id-right-menu-image");\r\n
            this.btnImage.render();\r\n
            this.btnChart.el = $("#id-right-menu-chart");\r\n
            this.btnChart.render();\r\n
            this.btnShape.el = $("#id-right-menu-shape");\r\n
            this.btnShape.render();\r\n
            this.btnText.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnImage.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnChart.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.btnShape.on("click", _.bind(this.onBtnMenuClick, this));\r\n
            this.paragraphSettings = new SSE.Views.ParagraphSettings();\r\n
            this.imageSettings = new SSE.Views.ImageSettings();\r\n
            this.chartSettings = new SSE.Views.ChartSettings();\r\n
            this.shapeSettings = new SSE.Views.ShapeSettings();\r\n
            if (_.isUndefined(this.scroller)) {\r\n
                this.scroller = new Common.UI.Scroller({\r\n
                    el: $(this.el).find(".right-panel"),\r\n
                    suppressScrollX: true,\r\n
                    useKeyboard: false\r\n
                });\r\n
            }\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.paragraphSettings.setApi(api);\r\n
            this.imageSettings.setApi(api);\r\n
            this.chartSettings.setApi(api);\r\n
            this.shapeSettings.setApi(api);\r\n
        },\r\n
        setMode: function (mode) {},\r\n
        onBtnMenuClick: function (btn, e) {\r\n
            var target_pane = $("#" + this._settings[btn.options.asctype].panel);\r\n
            var target_pane_parent = target_pane.parent();\r\n
            if (btn.pressed) {\r\n
                if (this.minimizedMode) {\r\n
                    $(this.el).width(MENU_SCALE_PART);\r\n
                    target_pane_parent.css("display", "inline-block");\r\n
                    this.minimizedMode = false;\r\n
                    window.localStorage.setItem("sse-hidden-right-settings", 0);\r\n
                }\r\n
                target_pane_parent.find("> .active").removeClass("active");\r\n
                target_pane.addClass("active");\r\n
                if (this.scroller) {\r\n
                    this.scroller.scrollTop(0);\r\n
                }\r\n
            } else {\r\n
                target_pane_parent.css("display", "none");\r\n
                $(this.el).width(SCALE_MIN);\r\n
                this.minimizedMode = true;\r\n
                window.localStorage.setItem("sse-hidden-right-settings", 1);\r\n
            }\r\n
            this.fireEvent("rightmenuclick", [this, btn.options.asctype, this.minimizedMode]);\r\n
        },\r\n
        SetActivePane: function (type, open) {\r\n
            if (this.minimizedMode && open !== true || this._settings[type] === undefined) {\r\n
                return;\r\n
            }\r\n
            if (this.minimizedMode) {\r\n
                this._settings[type].btn.toggle(true, false);\r\n
                this._settings[type].btn.trigger("click", this._settings[type].btn);\r\n
            } else {\r\n
                var target_pane = $("#" + this._settings[type].panel);\r\n
                if (!target_pane.hasClass("active")) {\r\n
                    target_pane.parent().find("> .active").removeClass("active");\r\n
                    target_pane.addClass("active");\r\n
                    if (this.scroller) {\r\n
                        this.scroller.update();\r\n
                    }\r\n
                }\r\n
                if (!this._settings[type].btn.isActive()) {\r\n
                    this._settings[type].btn.toggle(true, false);\r\n
                }\r\n
            }\r\n
        },\r\n
        GetActivePane: function () {\r\n
            return (this.minimizedMode) ? null : $(".settings-panel.active")[0].id;\r\n
        },\r\n
        SetDisabled: function (id, disabled, all) {\r\n
            if (all) {\r\n
                this.paragraphSettings.disableControls(disabled);\r\n
                this.shapeSettings.disableControls(disabled);\r\n
                this.imageSettings.disableControls(disabled);\r\n
                this.chartSettings.disableControls(disabled);\r\n
            } else {\r\n
                var cmp = $("#" + id);\r\n
                if (disabled !== cmp.hasClass("disabled")) {\r\n
                    cmp.toggleClass("disabled", disabled);\r\n
                    (disabled) ? cmp.attr({\r\n
                        disabled: disabled\r\n
                    }) : cmp.removeAttr("disabled");\r\n
                }\r\n
            }\r\n
        },\r\n
        clearSelection: function () {\r\n
            var target_pane = $(".right-panel");\r\n
            target_pane.find("> .active").removeClass("active");\r\n
            _.each(this._settings, function (item) {\r\n
                if (item.btn.isActive()) {\r\n
                    item.btn.toggle(false, true);\r\n
                }\r\n
            });\r\n
            target_pane.css("display", "none");\r\n
            $(this.el).width(SCALE_MIN);\r\n
            this.minimizedMode = true;\r\n
            window.localStorage.setItem("sse-hidden-right-settings", 1);\r\n
            Common.NotificationCenter.trigger("layout:changed", "rightmenu");\r\n
        },\r\n
        txtParagraphSettings: "Paragraph Settings",\r\n
        txtImageSettings: "Image Settings",\r\n
        txtShapeSettings: "Shape Settings",\r\n
        txtChartSettings: "Chart Settings"\r\n
    },\r\n
    SSE.Views.RightMenu || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9942</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
