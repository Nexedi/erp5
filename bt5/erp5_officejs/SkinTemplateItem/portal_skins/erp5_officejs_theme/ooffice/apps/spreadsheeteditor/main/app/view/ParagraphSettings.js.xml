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
            <value> <string>ts44321338.92</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ParagraphSettings.js</string> </value>
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
 var c_paragraphLinerule = {\r\n
    LINERULE_LEAST: 0,\r\n
    LINERULE_AUTO: 1,\r\n
    LINERULE_EXACT: 2\r\n
};\r\n
define(["text!spreadsheeteditor/main/app/template/ParagraphSettings.template", "jquery", "underscore", "backbone", "common/main/lib/component/ComboBox", "common/main/lib/component/MetricSpinner", "spreadsheeteditor/main/app/view/ParagraphSettingsAdvanced"], function (menuTemplate, $, _, Backbone) {\r\n
    SSE.Views.ParagraphSettings = Backbone.View.extend(_.extend({\r\n
        el: "#id-paragraph-settings",\r\n
        template: _.template(menuTemplate),\r\n
        events: {},\r\n
        options: {\r\n
            alias: "ParagraphSettings"\r\n
        },\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            this._initSettings = true;\r\n
            this._state = {\r\n
                LineRuleIdx: 1,\r\n
                LineHeight: 1.5,\r\n
                LineSpacingBefore: 0,\r\n
                LineSpacingAfter: 0.35,\r\n
                DisabledControls: false\r\n
            };\r\n
            this.spinners = [];\r\n
            this.lockedControls = [];\r\n
            this._locked = false;\r\n
            this.render();\r\n
            this._arrLineRule = [{\r\n
                displayValue: this.textAtLeast,\r\n
                defaultValue: 5,\r\n
                value: c_paragraphLinerule.LINERULE_LEAST,\r\n
                minValue: 0.03,\r\n
                step: 0.01,\r\n
                defaultUnit: "cm"\r\n
            },\r\n
            {\r\n
                displayValue: this.textAuto,\r\n
                defaultValue: 1,\r\n
                value: c_paragraphLinerule.LINERULE_AUTO,\r\n
                minValue: 0.5,\r\n
                step: 0.01,\r\n
                defaultUnit: ""\r\n
            },\r\n
            {\r\n
                displayValue: this.textExact,\r\n
                defaultValue: 5,\r\n
                value: c_paragraphLinerule.LINERULE_EXACT,\r\n
                minValue: 0.03,\r\n
                step: 0.01,\r\n
                defaultUnit: "cm"\r\n
            }];\r\n
            this.cmbLineRule = new Common.UI.ComboBox({\r\n
                el: $("#paragraph-combo-line-rule"),\r\n
                cls: "input-group-nr",\r\n
                menuStyle: "min-width: 85px;",\r\n
                editable: false,\r\n
                data: this._arrLineRule\r\n
            });\r\n
            this.cmbLineRule.setValue(this._arrLineRule[this._state.LineRuleIdx].value);\r\n
            this.lockedControls.push(this.cmbLineRule);\r\n
            this.numLineHeight = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraph-spin-line-height"),\r\n
                step: 0.01,\r\n
                width: 85,\r\n
                value: "1.5",\r\n
                defaultUnit: "",\r\n
                maxValue: 132,\r\n
                minValue: 0.5\r\n
            });\r\n
            this.lockedControls.push(this.numLineHeight);\r\n
            this.numSpacingBefore = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraph-spin-spacing-before"),\r\n
                step: 0.1,\r\n
                width: 85,\r\n
                value: "0 cm",\r\n
                defaultUnit: "cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0,\r\n
                allowAuto: true,\r\n
                autoText: this.txtAutoText\r\n
            });\r\n
            this.spinners.push(this.numSpacingBefore);\r\n
            this.lockedControls.push(this.numSpacingBefore);\r\n
            this.numSpacingAfter = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraph-spin-spacing-after"),\r\n
                step: 0.1,\r\n
                width: 85,\r\n
                value: "0.35 cm",\r\n
                defaultUnit: "cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0,\r\n
                allowAuto: true,\r\n
                autoText: this.txtAutoText\r\n
            });\r\n
            this.spinners.push(this.numSpacingAfter);\r\n
            this.lockedControls.push(this.numSpacingAfter);\r\n
            this.numLineHeight.on("change", _.bind(this.onNumLineHeightChange, this));\r\n
            this.numSpacingBefore.on("change", _.bind(this.onNumSpacingBeforeChange, this));\r\n
            this.numSpacingAfter.on("change", _.bind(this.onNumSpacingAfterChange, this));\r\n
            this.cmbLineRule.on("selected", _.bind(this.onLineRuleSelect, this));\r\n
            this.cmbLineRule.on("hide:after", _.bind(this.onHideMenus, this));\r\n
            $(this.el).on("click", "#paragraph-advanced-link", _.bind(this.openAdvancedSettings, this));\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({\r\n
                scope: this\r\n
            }));\r\n
            this.linkAdvanced = $("#paragraph-advanced-link");\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            if (this.api) {\r\n
                this.api.asc_registerCallback("asc_onParaSpacingLine", _.bind(this._onLineSpacing, this));\r\n
            }\r\n
            return this;\r\n
        },\r\n
        onNumLineHeightChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this.cmbLineRule.getRawValue() === "") {\r\n
                return;\r\n
            }\r\n
            var type = c_paragraphLinerule.LINERULE_AUTO;\r\n
            if (this.api) {\r\n
                this.api.asc_putPrLineSpacing(this.cmbLineRule.getValue(), (this.cmbLineRule.getValue() == c_paragraphLinerule.LINERULE_AUTO) ? field.getNumberValue() : Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onNumSpacingBeforeChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this.api) {\r\n
                var num = field.getNumberValue();\r\n
                if (num < 0) {\r\n
                    this.api.asc_putLineSpacingBeforeAfter(0, -1);\r\n
                } else {\r\n
                    this.api.asc_putLineSpacingBeforeAfter(0, Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onNumSpacingAfterChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this.api) {\r\n
                var num = field.getNumberValue();\r\n
                if (num < 0) {\r\n
                    this.api.asc_putLineSpacingBeforeAfter(1, -1);\r\n
                } else {\r\n
                    this.api.asc_putLineSpacingBeforeAfter(1, Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            }\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        onLineRuleSelect: function (combo, record) {\r\n
            if (this.api) {\r\n
                this.api.asc_putPrLineSpacing(record.value, record.defaultValue);\r\n
            }\r\n
            this.numLineHeight.setDefaultUnit(this._arrLineRule[record.value].defaultUnit);\r\n
            this.numLineHeight.setMinValue(this._arrLineRule[record.value].minValue);\r\n
            this.numLineHeight.setStep(this._arrLineRule[record.value].step);\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
        },\r\n
        _onLineSpacing: function (value) {\r\n
            var linerule = value.asc_getLineRule();\r\n
            var line = value.asc_getLine();\r\n
            if (this._state.LineRuleIdx !== linerule) {\r\n
                this.cmbLineRule.setValue((linerule !== null) ? this._arrLineRule[linerule].value : "");\r\n
                this.numLineHeight.setMinValue(this._arrLineRule[(linerule !== null) ? linerule : 1].minValue);\r\n
                this.numLineHeight.setDefaultUnit(this._arrLineRule[(linerule !== null) ? linerule : 1].defaultUnit);\r\n
                this.numLineHeight.setStep(this._arrLineRule[(linerule !== null) ? linerule : 1].step);\r\n
                this._state.LineRuleIdx = linerule;\r\n
            }\r\n
            if (Math.abs(this._state.LineHeight - line) > 0.001 || (this._state.LineHeight === null || line === null) && (this._state.LineHeight !== line)) {\r\n
                var val = "";\r\n
                if (linerule == c_paragraphLinerule.LINERULE_AUTO) {\r\n
                    val = line;\r\n
                } else {\r\n
                    if (linerule !== null && line !== null) {\r\n
                        val = Common.Utils.Metric.fnRecalcFromMM(line);\r\n
                    }\r\n
                }\r\n
                this.numLineHeight.setValue((val !== null) ? val : "", true);\r\n
                this._state.LineHeight = line;\r\n
            }\r\n
        },\r\n
        ChangeSettings: function (prop) {\r\n
            if (this._initSettings) {\r\n
                this.createDelayedElements();\r\n
                this._initSettings = false;\r\n
            }\r\n
            this.disableControls(this._locked);\r\n
            if (prop) {\r\n
                var Spacing = {\r\n
                    Line: prop.asc_getSpacing().asc_getLine(),\r\n
                    Before: prop.asc_getSpacing().asc_getBefore(),\r\n
                    After: prop.asc_getSpacing().asc_getAfter(),\r\n
                    LineRule: prop.asc_getSpacing().asc_getLineRule()\r\n
                };\r\n
                if (this._state.LineRuleIdx !== Spacing.LineRule) {\r\n
                    this.cmbLineRule.setValue((Spacing.LineRule !== null) ? this._arrLineRule[Spacing.LineRule].value : "");\r\n
                    this.numLineHeight.setMinValue(this._arrLineRule[(Spacing.LineRule !== null) ? Spacing.LineRule : 1].minValue);\r\n
                    this.numLineHeight.setDefaultUnit(this._arrLineRule[(Spacing.LineRule !== null) ? Spacing.LineRule : 1].defaultUnit);\r\n
                    this.numLineHeight.setStep(this._arrLineRule[(Spacing.LineRule !== null) ? Spacing.LineRule : 1].step);\r\n
                    this._state.LineRuleIdx = Spacing.LineRule;\r\n
                }\r\n
                if (Math.abs(this._state.LineHeight - Spacing.Line) > 0.001 || (this._state.LineHeight === null || Spacing.Line === null) && (this._state.LineHeight !== Spacing.Line)) {\r\n
                    var val = "";\r\n
                    if (Spacing.LineRule == c_paragraphLinerule.LINERULE_AUTO) {\r\n
                        val = Spacing.Line;\r\n
                    } else {\r\n
                        if (Spacing.LineRule !== null && Spacing.Line !== null) {\r\n
                            val = Common.Utils.Metric.fnRecalcFromMM(Spacing.Line);\r\n
                        }\r\n
                    }\r\n
                    this.numLineHeight.setValue((val !== null) ? val : "", true);\r\n
                    this._state.LineHeight = Spacing.Line;\r\n
                }\r\n
                if (Math.abs(this._state.LineSpacingBefore - Spacing.Before) > 0.001 || (this._state.LineSpacingBefore === null || Spacing.Before === null) && (this._state.LineSpacingBefore !== Spacing.Before)) {\r\n
                    this.numSpacingBefore.setValue((Spacing.Before !== null) ? ((Spacing.Before < 0) ? Spacing.Before : Common.Utils.Metric.fnRecalcFromMM(Spacing.Before)) : "", true);\r\n
                    this._state.LineSpacingBefore = Spacing.Before;\r\n
                }\r\n
                if (Math.abs(this._state.LineSpacingAfter - Spacing.After) > 0.001 || (this._state.LineSpacingAfter === null || Spacing.After === null) && (this._state.LineSpacingAfter !== Spacing.After)) {\r\n
                    this.numSpacingAfter.setValue((Spacing.After !== null) ? ((Spacing.After < 0) ? Spacing.After : Common.Utils.Metric.fnRecalcFromMM(Spacing.After)) : "", true);\r\n
                    this._state.LineSpacingAfter = Spacing.After;\r\n
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
            this._arrLineRule[2].defaultUnit = this._arrLineRule[0].defaultUnit = Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()];\r\n
            this._arrLineRule[2].minValue = this._arrLineRule[0].minValue = parseFloat(Common.Utils.Metric.fnRecalcFromMM(0.3).toFixed(2));\r\n
            this._arrLineRule[2].step = this._arrLineRule[0].step = (Common.Utils.Metric.getCurrentMetric() == Common.Utils.Metric.c_MetricUnits.cm) ? 0.01 : 1;\r\n
            if (this._state.LineRuleIdx !== null) {\r\n
                this.numLineHeight.setDefaultUnit(this._arrLineRule[this._state.LineRuleIdx].defaultUnit);\r\n
                this.numLineHeight.setStep(this._arrLineRule[this._state.LineRuleIdx].step);\r\n
            }\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            this.updateMetricUnit();\r\n
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
                        elValue = selectedElements[i].asc_getObjectValue();\r\n
                        if (c_oAscTypeSelectElement.Paragraph == elType) {\r\n
                            (new SSE.Views.ParagraphSettingsAdvanced({\r\n
                                paragraphProps: elValue,\r\n
                                api: me.api,\r\n
                                handler: function (result, value) {\r\n
                                    if (result == "ok") {\r\n
                                        if (me.api) {\r\n
                                            me.borderAdvancedProps = value.borderProps;\r\n
                                            me.api.asc_setGraphicObjectProps(value.paragraphProps);\r\n
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
        onHideMenus: function (e) {\r\n
            Common.NotificationCenter.trigger("edit:complete", this);\r\n
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
        strParagraphSpacing: "Spacing",\r\n
        strLineHeight: "Line Spacing",\r\n
        strSpacingBefore: "Before",\r\n
        strSpacingAfter: "After",\r\n
        textAuto: "Multiple",\r\n
        textAtLeast: "At least",\r\n
        textExact: "Exactly",\r\n
        textAdvanced: "Show advanced settings",\r\n
        textAt: "At",\r\n
        txtAutoText: "Auto"\r\n
    },\r\n
    SSE.Views.ParagraphSettings || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16939</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
