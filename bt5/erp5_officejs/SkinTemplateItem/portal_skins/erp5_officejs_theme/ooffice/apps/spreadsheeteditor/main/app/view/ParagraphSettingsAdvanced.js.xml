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
            <value> <string>ts44321339.02</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ParagraphSettingsAdvanced.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/ParagraphSettingsAdvanced.template", "common/main/lib/view/AdvancedSettingsWindow", "common/main/lib/component/MetricSpinner", "common/main/lib/component/CheckBox", "common/main/lib/component/RadioBox", "common/main/lib/component/ListView"], function (contentTemplate) {\r\n
    SSE.Views.ParagraphSettingsAdvanced = Common.Views.AdvancedSettingsWindow.extend(_.extend({\r\n
        options: {\r\n
            contentWidth: 320,\r\n
            height: 390,\r\n
            toggleGroup: "paragraph-adv-settings-group"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle,\r\n
                items: [{\r\n
                    panelId: "id-adv-paragraph-indents",\r\n
                    panelCaption: this.strParagraphIndents\r\n
                },\r\n
                {\r\n
                    panelId: "id-adv-paragraph-font",\r\n
                    panelCaption: this.strParagraphFont\r\n
                },\r\n
                {\r\n
                    panelId: "id-adv-paragraph-tabs",\r\n
                    panelCaption: this.strTabs\r\n
                }],\r\n
                contentTemplate: _.template(contentTemplate)({\r\n
                    scope: this\r\n
                })\r\n
            },\r\n
            options);\r\n
            Common.Views.AdvancedSettingsWindow.prototype.initialize.call(this, this.options);\r\n
            this._changedProps = null;\r\n
            this.checkGroup = 0;\r\n
            this._noApply = true;\r\n
            this._tabListChanged = false;\r\n
            this.spinners = [];\r\n
            this.api = this.options.api;\r\n
            this._originalProps = new Asc.asc_CParagraphProperty(this.options.paragraphProps);\r\n
        },\r\n
        render: function () {\r\n
            Common.Views.AdvancedSettingsWindow.prototype.render.call(this);\r\n
            var me = this;\r\n
            this.numFirstLine = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraphadv-spin-first-line"),\r\n
                step: 0.1,\r\n
                width: 85,\r\n
                defaultUnit: "cm",\r\n
                defaultValue: 0,\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: -55.87\r\n
            });\r\n
            this.numFirstLine.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getInd() === null || this._changedProps.asc_getInd() === undefined) {\r\n
                        this._changedProps.asc_putInd(new Asc.asc_CParagraphInd());\r\n
                    }\r\n
                    this._changedProps.asc_getInd().asc_putFirstLine(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.numFirstLine);\r\n
            this.numIndentsLeft = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraphadv-spin-indent-left"),\r\n
                step: 0.1,\r\n
                width: 85,\r\n
                defaultUnit: "cm",\r\n
                defaultValue: 0,\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: -55.87\r\n
            });\r\n
            this.numIndentsLeft.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getInd() === null || this._changedProps.asc_getInd() === undefined) {\r\n
                        this._changedProps.asc_putInd(new Asc.asc_CParagraphInd());\r\n
                    }\r\n
                    this._changedProps.asc_getInd().asc_putLeft(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.numIndentsLeft);\r\n
            this.numIndentsRight = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraphadv-spin-indent-right"),\r\n
                step: 0.1,\r\n
                width: 85,\r\n
                defaultUnit: "cm",\r\n
                defaultValue: 0,\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: -55.87\r\n
            });\r\n
            this.numIndentsRight.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    if (this._changedProps.asc_getInd() === null || this._changedProps.asc_getInd() === undefined) {\r\n
                        this._changedProps.asc_putInd(new Asc.asc_CParagraphInd());\r\n
                    }\r\n
                    this._changedProps.asc_getInd().asc_putRight(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.numIndentsRight);\r\n
            this.chStrike = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-strike"),\r\n
                labelText: this.strStrike\r\n
            });\r\n
            this.chStrike.on("change", _.bind(this.onStrikeChange, this));\r\n
            this.chDoubleStrike = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-double-strike"),\r\n
                labelText: this.strDoubleStrike\r\n
            });\r\n
            this.chDoubleStrike.on("change", _.bind(this.onDoubleStrikeChange, this));\r\n
            this.chSuperscript = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-superscript"),\r\n
                labelText: this.strSuperscript\r\n
            });\r\n
            this.chSuperscript.on("change", _.bind(this.onSuperscriptChange, this));\r\n
            this.chSubscript = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-subscript"),\r\n
                labelText: this.strSubscript\r\n
            });\r\n
            this.chSubscript.on("change", _.bind(this.onSubscriptChange, this));\r\n
            this.chSmallCaps = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-small-caps"),\r\n
                labelText: this.strSmallCaps\r\n
            });\r\n
            this.chSmallCaps.on("change", _.bind(this.onSmallCapsChange, this));\r\n
            this.chAllCaps = new Common.UI.CheckBox({\r\n
                el: $("#paragraphadv-checkbox-all-caps"),\r\n
                labelText: this.strAllCaps\r\n
            });\r\n
            this.chAllCaps.on("change", _.bind(this.onAllCapsChange, this));\r\n
            this.numSpacing = new Common.UI.MetricSpinner({\r\n
                el: $("#paragraphadv-spin-spacing"),\r\n
                step: 0.01,\r\n
                width: 100,\r\n
                defaultUnit: "cm",\r\n
                defaultValue: 0,\r\n
                value: "0 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: -55.87\r\n
            });\r\n
            this.numSpacing.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putTextSpacing(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                }\r\n
                if (this.api && !this._noApply) {\r\n
                    var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                    properties.asc_putTextSpacing(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()));\r\n
                    this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.numSpacing);\r\n
            this.numTab = new Common.UI.MetricSpinner({\r\n
                el: $("#paraadv-spin-tab"),\r\n
                step: 0.1,\r\n
                width: 180,\r\n
                defaultUnit: "cm",\r\n
                value: "1.25 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.numTab);\r\n
            this.numDefaultTab = new Common.UI.MetricSpinner({\r\n
                el: $("#paraadv-spin-default-tab"),\r\n
                step: 0.1,\r\n
                width: 107,\r\n
                defaultUnit: "cm",\r\n
                value: "1.25 cm",\r\n
                maxValue: 55.87,\r\n
                minValue: 0\r\n
            });\r\n
            this.numDefaultTab.on("change", _.bind(function (field, newValue, oldValue, eOpts) {\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putDefaultTab(parseFloat(Common.Utils.Metric.fnRecalcToMM(field.getNumberValue()).toFixed(1)));\r\n
                }\r\n
            },\r\n
            this));\r\n
            this.spinners.push(this.numDefaultTab);\r\n
            this.tabList = new Common.UI.ListView({\r\n
                el: $("#paraadv-list-tabs"),\r\n
                emptyText: this.noTabs,\r\n
                store: new Common.UI.DataViewStore()\r\n
            });\r\n
            this.tabList.store.comparator = function (rec) {\r\n
                return rec.get("tabPos");\r\n
            };\r\n
            this.tabList.on("item:select", _.bind(this.onSelectTab, this));\r\n
            var storechanged = function () {\r\n
                if (!me._noApply) {\r\n
                    me._tabListChanged = true;\r\n
                }\r\n
            };\r\n
            this.listenTo(this.tabList.store, "add", storechanged);\r\n
            this.listenTo(this.tabList.store, "remove", storechanged);\r\n
            this.listenTo(this.tabList.store, "reset", storechanged);\r\n
            this.radioLeft = new Common.UI.RadioBox({\r\n
                el: $("#paragraphadv-radio-left"),\r\n
                labelText: this.textTabLeft,\r\n
                name: "asc-radio-tab",\r\n
                checked: true\r\n
            });\r\n
            this.radioCenter = new Common.UI.RadioBox({\r\n
                el: $("#paragraphadv-radio-center"),\r\n
                labelText: this.textTabCenter,\r\n
                name: "asc-radio-tab"\r\n
            });\r\n
            this.radioRight = new Common.UI.RadioBox({\r\n
                el: $("#paragraphadv-radio-right"),\r\n
                labelText: this.textTabRight,\r\n
                name: "asc-radio-tab"\r\n
            });\r\n
            this.btnAddTab = new Common.UI.Button({\r\n
                el: $("#paraadv-button-add-tab")\r\n
            });\r\n
            this.btnAddTab.on("click", _.bind(this.addTab, this));\r\n
            this.btnRemoveTab = new Common.UI.Button({\r\n
                el: $("#paraadv-button-remove-tab")\r\n
            });\r\n
            this.btnRemoveTab.on("click", _.bind(this.removeTab, this));\r\n
            this.btnRemoveAll = new Common.UI.Button({\r\n
                el: $("#paraadv-button-remove-all")\r\n
            });\r\n
            this.btnRemoveAll.on("click", _.bind(this.removeAllTabs, this));\r\n
            this.afterRender();\r\n
        },\r\n
        getSettings: function () {\r\n
            if (this._tabListChanged) {\r\n
                if (this._changedProps.asc_getTabs() === null || this._changedProps.asc_getTabs() === undefined) {\r\n
                    this._changedProps.asc_putTabs(new Asc.asc_CParagraphTabs());\r\n
                }\r\n
                this.tabList.store.each(function (item, index) {\r\n
                    var tab = new Asc.asc_CParagraphTab(Common.Utils.Metric.fnRecalcToMM(item.get("tabPos")), item.get("tabAlign"));\r\n
                    this._changedProps.asc_getTabs().add_Tab(tab);\r\n
                },\r\n
                this);\r\n
            }\r\n
            return {\r\n
                paragraphProps: this._changedProps\r\n
            };\r\n
        },\r\n
        _setDefaults: function (props) {\r\n
            if (props) {\r\n
                this._originalProps = new Asc.asc_CParagraphProperty(props);\r\n
                this.numFirstLine.setValue((props.asc_getInd() !== null && props.asc_getInd().asc_getFirstLine() !== null) ? Common.Utils.Metric.fnRecalcFromMM(props.asc_getInd().asc_getFirstLine()) : "", true);\r\n
                this.numIndentsLeft.setValue((props.asc_getInd() !== null && props.asc_getInd().asc_getLeft() !== null) ? Common.Utils.Metric.fnRecalcFromMM(props.asc_getInd().asc_getLeft()) : "", true);\r\n
                this.numIndentsRight.setValue((props.asc_getInd() !== null && props.asc_getInd().asc_getRight() !== null) ? Common.Utils.Metric.fnRecalcFromMM(props.asc_getInd().asc_getRight()) : "", true);\r\n
                this._noApply = true;\r\n
                this.chStrike.setValue((props.asc_getStrikeout() !== null && props.asc_getStrikeout() !== undefined) ? props.asc_getStrikeout() : "indeterminate", true);\r\n
                this.chDoubleStrike.setValue((props.asc_getDStrikeout() !== null && props.asc_getDStrikeout() !== undefined) ? props.asc_getDStrikeout() : "indeterminate", true);\r\n
                this.chSubscript.setValue((props.asc_getSubscript() !== null && props.asc_getSubscript() !== undefined) ? props.asc_getSubscript() : "indeterminate", true);\r\n
                this.chSuperscript.setValue((props.asc_getSuperscript() !== null && props.asc_getSuperscript() !== undefined) ? props.asc_getSuperscript() : "indeterminate", true);\r\n
                this.chSmallCaps.setValue((props.asc_getSmallCaps() !== null && props.asc_getSmallCaps() !== undefined) ? props.asc_getSmallCaps() : "indeterminate", true);\r\n
                this.chAllCaps.setValue((props.asc_getAllCaps() !== null && props.asc_getAllCaps() !== undefined) ? props.asc_getAllCaps() : "indeterminate", true);\r\n
                this.numSpacing.setValue((props.asc_getTextSpacing() !== null && props.asc_getTextSpacing() !== undefined) ? Common.Utils.Metric.fnRecalcFromMM(props.asc_getTextSpacing()) : "", true);\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", this._originalProps);\r\n
                this.numDefaultTab.setValue((props.asc_getDefaultTab() !== null && props.asc_getDefaultTab() !== undefined) ? Common.Utils.Metric.fnRecalcFromMM(parseFloat(props.asc_getDefaultTab().toFixed(1))) : "", true);\r\n
                var store = this.tabList.store;\r\n
                var tabs = props.asc_getTabs();\r\n
                if (tabs) {\r\n
                    var arr = [];\r\n
                    var count = tabs.asc_getCount();\r\n
                    for (var i = 0; i < count; i++) {\r\n
                        var tab = tabs.asc_getTab(i);\r\n
                        var pos = Common.Utils.Metric.fnRecalcFromMM(parseFloat(tab.asc_getPos().toFixed(1)));\r\n
                        var rec = new Common.UI.DataViewModel();\r\n
                        rec.set({\r\n
                            tabPos: pos,\r\n
                            value: parseFloat(pos.toFixed(3)) + " " + Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()],\r\n
                            tabAlign: tab.asc_getValue()\r\n
                        });\r\n
                        arr.push(rec);\r\n
                    }\r\n
                    store.reset(arr, {\r\n
                        silent: false\r\n
                    });\r\n
                    this.tabList.selectByIndex(0);\r\n
                }\r\n
                this._noApply = false;\r\n
                this._changedProps = new Asc.asc_CParagraphProperty();\r\n
            }\r\n
        },\r\n
        updateMetricUnit: function () {\r\n
            if (this.spinners) {\r\n
                for (var i = 0; i < this.spinners.length; i++) {\r\n
                    var spinner = this.spinners[i];\r\n
                    spinner.setDefaultUnit(Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()]);\r\n
                    if (spinner.el.id == "paragraphadv-spin-spacing" || spinner.el.id == "paragraphadv-spin-position") {\r\n
                        spinner.setStep(Common.Utils.Metric.getCurrentMetric() == Common.Utils.Metric.c_MetricUnits.cm ? 0.01 : 1);\r\n
                    } else {\r\n
                        spinner.setStep(Common.Utils.Metric.getCurrentMetric() == Common.Utils.Metric.c_MetricUnits.cm ? 0.1 : 1);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        afterRender: function () {\r\n
            this.updateMetricUnit();\r\n
            this._setDefaults(this._originalProps);\r\n
        },\r\n
        onStrikeChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 1) {\r\n
                this._changedProps.asc_putStrikeout(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 1;\r\n
                this.chDoubleStrike.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putDStrikeout(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putStrikeout(field.getValue() == "checked");\r\n
                properties.asc_putDStrikeout(this.chDoubleStrike.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        onDoubleStrikeChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 1) {\r\n
                this._changedProps.asc_putDStrikeout(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 1;\r\n
                this.chStrike.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putStrikeout(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putDStrikeout(field.getValue() == "checked");\r\n
                properties.asc_putStrikeout(this.chStrike.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        onSuperscriptChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 2) {\r\n
                this._changedProps.asc_putSuperscript(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 2;\r\n
                this.chSubscript.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putSubscript(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putSuperscript(field.getValue() == "checked");\r\n
                properties.asc_putSubscript(this.chSubscript.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        onSubscriptChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 2) {\r\n
                this._changedProps.asc_putSubscript(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 2;\r\n
                this.chSuperscript.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putSuperscript(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putSubscript(field.getValue() == "checked");\r\n
                properties.asc_putSuperscript(this.chSuperscript.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        onSmallCapsChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 3) {\r\n
                this._changedProps.asc_putSmallCaps(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 3;\r\n
                this.chAllCaps.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putAllCaps(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putSmallCaps(field.getValue() == "checked");\r\n
                properties.asc_putAllCaps(this.chAllCaps.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        onAllCapsChange: function (field, newValue, oldValue, eOpts) {\r\n
            if (this._changedProps && this.checkGroup != 3) {\r\n
                this._changedProps.asc_putAllCaps(field.getValue() == "checked");\r\n
            }\r\n
            this.checkGroup = 0;\r\n
            if (field.getValue() == "checked") {\r\n
                this.checkGroup = 3;\r\n
                this.chSmallCaps.setValue(0);\r\n
                if (this._changedProps) {\r\n
                    this._changedProps.asc_putSmallCaps(false);\r\n
                }\r\n
                this.checkGroup = 0;\r\n
            }\r\n
            if (this.api && !this._noApply) {\r\n
                var properties = (this._originalProps) ? this._originalProps : new Asc.asc_CParagraphProperty();\r\n
                properties.asc_putAllCaps(field.getValue() == "checked");\r\n
                properties.asc_putSmallCaps(this.chSmallCaps.getValue() == "checked");\r\n
                this.api.asc_setDrawImagePlaceParagraph("paragraphadv-font-img", properties);\r\n
            }\r\n
        },\r\n
        addTab: function (btn, eOpts) {\r\n
            var val = this.numTab.getNumberValue();\r\n
            var align = this.radioLeft.getValue() ? 1 : (this.radioCenter.getValue() ? 3 : 2);\r\n
            var store = this.tabList.store;\r\n
            var rec = store.find(function (record) {\r\n
                return (Math.abs(record.get("tabPos") - val) < 0.001);\r\n
            });\r\n
            if (rec) {\r\n
                rec.set("tabAlign", align);\r\n
            } else {\r\n
                rec = new Common.UI.DataViewModel();\r\n
                rec.set({\r\n
                    tabPos: val,\r\n
                    value: val + " " + Common.Utils.Metric.metricName[Common.Utils.Metric.getCurrentMetric()],\r\n
                    tabAlign: align\r\n
                });\r\n
                store.add(rec);\r\n
            }\r\n
            this.tabList.selectRecord(rec);\r\n
            this.tabList.scrollToRecord(rec);\r\n
        },\r\n
        removeTab: function (btn, eOpts) {\r\n
            var rec = this.tabList.getSelectedRec();\r\n
            if (rec.length > 0) {\r\n
                var store = this.tabList.store;\r\n
                var idx = _.indexOf(store.models, rec[0]);\r\n
                store.remove(rec[0]);\r\n
                if (idx > store.length - 1) {\r\n
                    idx = store.length - 1;\r\n
                }\r\n
                if (store.length > 0) {\r\n
                    this.tabList.selectByIndex(idx);\r\n
                    this.tabList.scrollToRecord(store.at(idx));\r\n
                }\r\n
            }\r\n
        },\r\n
        removeAllTabs: function (btn, eOpts) {\r\n
            this.tabList.store.reset();\r\n
        },\r\n
        onSelectTab: function (lisvView, itemView, record) {\r\n
            var rawData = {},\r\n
            isViewSelect = _.isFunction(record.toJSON);\r\n
            if (isViewSelect) {\r\n
                if (record.get("selected")) {\r\n
                    rawData = record.toJSON();\r\n
                } else {\r\n
                    return;\r\n
                }\r\n
            } else {\r\n
                rawData = record;\r\n
            }\r\n
            this.numTab.setValue(rawData.tabPos);\r\n
            (rawData.tabAlign == 1) ? this.radioLeft.setValue(true) : ((rawData.tabAlign == 3) ? this.radioCenter.setValue(true) : this.radioRight.setValue(true));\r\n
        },\r\n
        textTitle: "Paragraph - Advanced Settings",\r\n
        strIndentsFirstLine: "First line",\r\n
        strIndentsLeftText: "Left",\r\n
        strIndentsRightText: "Right",\r\n
        strParagraphIndents: "Indents & Placement",\r\n
        strParagraphFont: "Font",\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok",\r\n
        textEffects: "Effects",\r\n
        textCharacterSpacing: "Character Spacing",\r\n
        strDoubleStrike: "Double strikethrough",\r\n
        strStrike: "Strikethrough",\r\n
        strSuperscript: "Superscript",\r\n
        strSubscript: "Subscript",\r\n
        strSmallCaps: "Small caps",\r\n
        strAllCaps: "All caps",\r\n
        strTabs: "Tab",\r\n
        textSet: "Specify",\r\n
        textRemove: "Remove",\r\n
        textRemoveAll: "Remove All",\r\n
        textTabLeft: "Left",\r\n
        textTabRight: "Right",\r\n
        textTabCenter: "Center",\r\n
        textAlign: "Alignment",\r\n
        textTabPosition: "Tab Position",\r\n
        textDefault: "Default Tab",\r\n
        noTabs: "The specified tabs will appear in this field"\r\n
    },\r\n
    SSE.Views.ParagraphSettingsAdvanced || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>27011</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
