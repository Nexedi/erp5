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
            <value> <string>ts44321338.65</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ImageSettings.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/ImageSettings.template", "jquery", "underscore", "backbone", "common/main/lib/component/Button", "common/main/lib/component/MetricSpinner", "common/main/lib/view/ImageFromUrlDialog"], function (menuTemplate, $, _, Backbone) {\r\n
    SSE.Views.ImageSettings = Backbone.View.extend(_.extend({\r\n
        el: "#id-image-settings",\r\n
        template: _.template(menuTemplate),\r\n
        events: {},\r\n
        options: {\r\n
            alias: "ImageSettings"\r\n
        },\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            this._initSettings = true;\r\n
            this._nRatio = 1;\r\n
            this._state = {\r\n
                Width: 0,\r\n
                Height: 0,\r\n
                DisabledControls: false\r\n
            };\r\n
            this.spinners = [];\r\n
            this.lockedControls = [];\r\n
            this._locked = false;\r\n
            this._noApply = false;\r\n
            this.render();\r\n
            this.spnWidth = new Common.UI.MetricSpinner({\r\n
                el: $("#image-spin-width"),\r\n
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
                el: $("#image-spin-height"),\r\n
                step: 0.1,\r\n
                width: 78,\r\n
                defaultUnit: "cm",\r\n
                value: "3 cm",\r\n
                maxValue: 55.88,\r\n
                minValue: 0\r\n
            });\r\n
            this.spinners.push(this.spnHeight);\r\n
            this.lockedControls.push(this.spnHeight);\r\n
            this.btnRatio = new Common.UI.Button({\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "advanced-btn-ratio",\r\n
                style: "margin-bottom: 1px;",\r\n
                enableToggle: true,\r\n
                hint: this.textKeepRatio\r\n
            });\r\n
            this.btnRatio.render($("#image-button-ratio"));\r\n
            this.lockedControls.push(this.btnRatio);\r\n
            var value = window.localStorage.getItem("sse-settings-imageratio");\r\n
            if (value === null || parseInt(value) == 1) {\r\n
                this.btnRatio.toggle(true);\r\n
            }\r\n
            this.btnRatio.on("click", _.bind(function (btn, e) {\r\n
                if (btn.pressed && this.spnHeight.getNumberValue() > 0) {\r\n
                    this._nRatio = this.spnWidth.getNumberValue() / this.spnHeight.getNumberValue();\r\n
                }\r\n
                window.localStorage.setItem("sse-settings-imageratio", (btn.pressed) ? 1 : 0);\r\n
            },\r\n
            this));\r\n
            this.btnOriginalSize = new Common.UI.Button({\r\n
                el: $("#image-button-original-size")\r\n
            });\r\n
            this.lockedControls.push(this.btnOriginalSize);\r\n
            this.btnInsertFromFile = new Common.UI.Button({\r\n
                el: $("#image-button-from-file")\r\n
            });\r\n
            this.lockedControls.push(this.btnInsertFromFile);\r\n
            this.btnInsertFromUrl = new Common.UI.Button({\r\n
                el: $("#image-button-from-url")\r\n
            });\r\n
            this.lockedControls.push(this.btnInsertFromUrl);\r\n
            this.spnWidth.on("change", _.bind(this.onWidthChange, this));\r\n
            this.spnHeight.on("change", _.bind(this.onHeightChange, this));\r\n
            this.btnOriginalSize.on("click", _.bind(this.setOriginalSize, this));\r\n
            this.btnInsertFromFile.on("click", _.bind(function (btn) {\r\n
                if (this.api) {\r\n
                    this.api.asc_changeImageFromFile();\r\n
                }\r\n
                Common.NotificationCenter.trigger("edit:complete", this);\r\n
            },\r\n
            this));\r\n
            this.btnInsertFromUrl.on("click", _.bind(this.insertFromUrl, this));\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template({\r\n
                scope: this\r\n
            }));\r\n
        },\r\n
        setApi: function (api) {\r\n
            if (api == undefined) {\r\n
                return;\r\n
            }\r\n
            this.api = api;\r\n
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
        createDelayedElements: function () {\r\n
            this.updateMetricUnit();\r\n
        },\r\n
        ChangeSettings: function (props) {\r\n
            if (this._initSettings) {\r\n
                this.createDelayedElements();\r\n
                this._initSettings = false;\r\n
            }\r\n
            this.disableControls(this._locked);\r\n
            if (props) {\r\n
                var value = props.asc_getWidth();\r\n
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
                this.btnOriginalSize.setDisabled(props.asc_getImageUrl() === null || props.asc_getImageUrl() === undefined || this._locked);\r\n
            }\r\n
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
        setOriginalSize: function () {\r\n
            if (this.api) {\r\n
                var imgsize = this.api.asc_getOriginalImageSize();\r\n
                var w = imgsize.asc_getImageWidth();\r\n
                var h = imgsize.asc_getImageHeight();\r\n
                var properties = new Asc.asc_CImgProperty();\r\n
                properties.asc_putWidth(w);\r\n
                properties.asc_putHeight(h);\r\n
                this.api.asc_setGraphicObjectProps(properties);\r\n
                Common.NotificationCenter.trigger("edit:complete", this);\r\n
            }\r\n
        },\r\n
        insertFromUrl: function () {\r\n
            var me = this;\r\n
            (new Common.Views.ImageFromUrlDialog({\r\n
                handler: function (result, value) {\r\n
                    if (result == "ok") {\r\n
                        if (me.api) {\r\n
                            var checkUrl = value.replace(/ /g, "");\r\n
                            if (!_.isEmpty(checkUrl)) {\r\n
                                var props = new Asc.asc_CImgProperty();\r\n
                                props.asc_putImageUrl(checkUrl);\r\n
                                me.api.asc_setGraphicObjectProps(props);\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("edit:complete", me);\r\n
                }\r\n
            })).show();\r\n
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
            }\r\n
        },\r\n
        textKeepRatio: "Constant Proportions",\r\n
        textSize: "Size",\r\n
        textWidth: "Width",\r\n
        textHeight: "Height",\r\n
        textOriginalSize: "Default Size",\r\n
        textInsert: "Insert Image",\r\n
        textFromUrl: "From URL",\r\n
        textFromFile: "From File"\r\n
    },\r\n
    SSE.Views.ImageSettings || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11834</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
