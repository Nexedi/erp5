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
            <value> <string>ts44308800.14</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>MetricSpinner.js</string> </value>
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
 if (Common === undefined) {\r\n
    var Common = {};\r\n
}\r\n
define(["common/main/lib/component/BaseView"], function () {\r\n
    Common.UI.MetricSpinner = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            minValue: 0,\r\n
            maxValue: 100,\r\n
            step: 1,\r\n
            defaultUnit: "px",\r\n
            allowAuto: false,\r\n
            autoText: "Auto",\r\n
            hold: true,\r\n
            speed: "medium",\r\n
            width: 90,\r\n
            allowDecimal: true\r\n
        },\r\n
        disabled: false,\r\n
        value: "0 px",\r\n
        rendered: false,\r\n
        template: \'<input type="text" class="form-control">\' + \'<div class="spinner-buttons">\' + \'<button type="button" class="spinner-up"><i></i></button>\' + \'<button type="button" class="spinner-down"><i></i></button>\' + "</div>",\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            el.addClass("spinner");\r\n
            el.on("mousedown", ".spinner-up", _.bind(this.onMouseDown, this, true));\r\n
            el.on("mousedown", ".spinner-down", _.bind(this.onMouseDown, this, false));\r\n
            el.on("mouseup", ".spinner-up", _.bind(this.onMouseUp, this, true));\r\n
            el.on("mouseup", ".spinner-down", _.bind(this.onMouseUp, this, false));\r\n
            el.on("mouseover", ".spinner-up, .spinner-down", _.bind(this.onMouseOver, this));\r\n
            el.on("mouseout", ".spinner-up, .spinner-down", _.bind(this.onMouseOut, this));\r\n
            el.on("keydown", ".form-control", _.bind(this.onKeyDown, this));\r\n
            el.on("keyup", ".form-control", _.bind(this.onKeyUp, this));\r\n
            el.on("blur", ".form-control", _.bind(this.onBlur, this));\r\n
            el.on("input", ".form-control", _.bind(this.onInput, this));\r\n
            if (!this.options.allowDecimal) {\r\n
                el.on("keypress", ".form-control", _.bind(this.onKeyPress, this));\r\n
            }\r\n
            this.switches = {\r\n
                count: 1,\r\n
                enabled: true,\r\n
                fromKeyDown: false\r\n
            };\r\n
            if (this.options.speed === "medium") {\r\n
                this.switches.speed = 300;\r\n
            } else {\r\n
                if (this.options.speed === "fast") {\r\n
                    this.switches.speed = 100;\r\n
                } else {\r\n
                    this.switches.speed = 500;\r\n
                }\r\n
            }\r\n
            this.render();\r\n
            if (this.options.disabled) {\r\n
                this.setDisabled(this.options.disabled);\r\n
            }\r\n
            if (this.options.value !== undefined) {\r\n
                this.value = this.options.value;\r\n
            }\r\n
            this.setRawValue(this.value);\r\n
            if (this.options.width) {\r\n
                $(this.el).width(this.options.width);\r\n
            }\r\n
            if (this.options.defaultValue === undefined) {\r\n
                this.options.defaultValue = this.options.minValue;\r\n
            }\r\n
            this.oldValue = this.options.minValue;\r\n
            this.lastValue = null;\r\n
        },\r\n
        render: function () {\r\n
            var el = $(this.el);\r\n
            el.html(this.template);\r\n
            this.$input = el.find(".form-control");\r\n
            this.rendered = true;\r\n
            if (this.options.tabindex != undefined) {\r\n
                this.$input.attr("tabindex", this.options.tabindex);\r\n
            }\r\n
            return this;\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            var el = $(this.el);\r\n
            if (disabled !== this.disabled) {\r\n
                el.find("button").toggleClass("disabled", disabled);\r\n
                el.toggleClass("disabled", disabled);\r\n
                (disabled) ? this.$input.attr({\r\n
                    disabled: disabled\r\n
                }) : this.$input.removeAttr("disabled");\r\n
            }\r\n
            this.disabled = disabled;\r\n
        },\r\n
        isDisabled: function () {\r\n
            return this.disabled;\r\n
        },\r\n
        setDefaultUnit: function (unit) {\r\n
            if (this.options.defaultUnit != unit) {\r\n
                var oldUnit = this.options.defaultUnit;\r\n
                this.options.defaultUnit = unit;\r\n
                this.setMinValue(this._recalcUnits(this.options.minValue, oldUnit));\r\n
                this.setMaxValue(this._recalcUnits(this.options.maxValue, oldUnit));\r\n
                this.setValue(this._recalcUnits(this.getNumberValue(), oldUnit), true);\r\n
            }\r\n
        },\r\n
        setMinValue: function (unit) {\r\n
            this.options.minValue = unit;\r\n
        },\r\n
        setMaxValue: function (unit) {\r\n
            this.options.maxValue = unit;\r\n
        },\r\n
        setStep: function (step) {\r\n
            this.options.step = step;\r\n
        },\r\n
        getNumberValue: function () {\r\n
            if (this.options.allowAuto && this.value == this.options.autoText) {\r\n
                return -1;\r\n
            } else {\r\n
                return parseFloat(this.value);\r\n
            }\r\n
        },\r\n
        getUnitValue: function () {\r\n
            return this.options.defaultUnit;\r\n
        },\r\n
        getValue: function () {\r\n
            return this.value;\r\n
        },\r\n
        setRawValue: function (value) {\r\n
            if (this.$input) {\r\n
                this.$input.val(value);\r\n
            }\r\n
        },\r\n
        setValue: function (value, suspendchange) {\r\n
            var showError = false;\r\n
            this._fromKeyDown = false;\r\n
            this.lastValue = this.value;\r\n
            if (typeof value === "undefined" || value === "") {\r\n
                this.value = "";\r\n
            } else {\r\n
                if (this.options.allowAuto && (Math.abs(parseFloat(value) + 1) < 0.0001 || value == this.options.autoText)) {\r\n
                    this.value = this.options.autoText;\r\n
                } else {\r\n
                    var number = this._add(parseFloat(value), 0, (this.options.allowDecimal) ? 3 : 0);\r\n
                    if (typeof value === "undefined" || isNaN(number)) {\r\n
                        number = this.oldValue;\r\n
                        showError = true;\r\n
                    }\r\n
                    var units = this.options.defaultUnit;\r\n
                    if (typeof value.match !== "undefined") {\r\n
                        var searchUnits = value.match(/(px|em|%|en|ex|pt|in|cm|mm|pc|s|ms)$/i);\r\n
                        if (null !== searchUnits && searchUnits[0] !== "undefined") {\r\n
                            units = searchUnits[0].toLowerCase();\r\n
                        }\r\n
                    }\r\n
                    if (this.options.defaultUnit !== units) {\r\n
                        number = this._recalcUnits(number, units);\r\n
                    }\r\n
                    if (number > this.options.maxValue) {\r\n
                        number = this.options.maxValue;\r\n
                        showError = true;\r\n
                    }\r\n
                    if (number < this.options.minValue) {\r\n
                        number = this.options.minValue;\r\n
                        showError = true;\r\n
                    }\r\n
                    this.value = (number + " " + this.options.defaultUnit).trim();\r\n
                    this.oldValue = number;\r\n
                }\r\n
            }\r\n
            if (suspendchange !== true && this.lastValue !== this.value) {\r\n
                this.trigger("change", this, this.value, this.lastValue);\r\n
            }\r\n
            if (suspendchange !== true && showError) {\r\n
                this.trigger("inputerror", this, this.value);\r\n
            }\r\n
            if (this.rendered) {\r\n
                this.setRawValue(this.value);\r\n
            } else {\r\n
                this.options.value = this.value;\r\n
            }\r\n
        },\r\n
        onMouseDown: function (type, e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (e) {\r\n
                $(e.currentTarget).addClass("active");\r\n
            }\r\n
            if (this.options.hold) {\r\n
                this.switches.fromKeyDown = false;\r\n
                this._startSpin(type, e);\r\n
            }\r\n
        },\r\n
        onMouseUp: function (type, e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            $(e.currentTarget).removeClass("active");\r\n
            if (this.options.hold) {\r\n
                this._stopSpin();\r\n
            } else {\r\n
                this._step(type);\r\n
            }\r\n
        },\r\n
        onMouseOver: function (e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            $(e.currentTarget).addClass("over");\r\n
        },\r\n
        onMouseOut: function (e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            $(e.currentTarget).removeClass("active over");\r\n
            if (this.options.hold) {\r\n
                this._stopSpin();\r\n
            }\r\n
        },\r\n
        onKeyDown: function (e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (this.options.hold && (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN)) {\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                if (this.switches.timeout === undefined) {\r\n
                    this.switches.fromKeyDown = true;\r\n
                    this._startSpin(e.keyCode == Common.UI.Keys.UP, e);\r\n
                }\r\n
            } else {\r\n
                if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                    if (this.options.defaultUnit && this.options.defaultUnit.length) {\r\n
                        var value = this.$input.val();\r\n
                        if (this.value != value) {\r\n
                            this.onEnterValue();\r\n
                            return false;\r\n
                        }\r\n
                    } else {\r\n
                        this.onEnterValue();\r\n
                    }\r\n
                } else {\r\n
                    this._fromKeyDown = true;\r\n
                }\r\n
            }\r\n
        },\r\n
        onKeyUp: function (e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN) {\r\n
                e.stopPropagation();\r\n
                e.preventDefault();\r\n
                (this.options.hold) ? this._stopSpin() : this._step(e.keyCode == Common.UI.Keys.UP);\r\n
            }\r\n
        },\r\n
        onKeyPress: function (e) {\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            var charCode = String.fromCharCode(e.charCode);\r\n
            if (charCode == "." || charCode == ",") {\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
            } else {\r\n
                if (this.options.maskExp && !this.options.maskExp.test(charCode) && !e.ctrlKey && e.keyCode !== Common.UI.Keys.DELETE && e.keyCode !== Common.UI.Keys.BACKSPACE && e.keyCode !== Common.UI.Keys.LEFT && e.keyCode !== Common.UI.Keys.RIGHT && e.keyCode !== Common.UI.Keys.HOME && e.keyCode !== Common.UI.Keys.END && e.keyCode !== Common.UI.Keys.ESC && e.keyCode !== Common.UI.Keys.RETURN && e.keyCode !== Common.UI.Keys.INSERT && e.keyCode !== Common.UI.Keys.TAB) {\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                }\r\n
            }\r\n
        },\r\n
        onInput: function (e, extra) {\r\n
            if (this.disabled || e.isDefaultPrevented()) {\r\n
                return;\r\n
            }\r\n
            this.trigger("changing", this, $(e.target).val(), e);\r\n
        },\r\n
        onEnterValue: function () {\r\n
            if (this.$input) {\r\n
                var val = this.$input.val();\r\n
                this.setValue((val === "") ? this.value : val);\r\n
                this.trigger("entervalue", this);\r\n
            }\r\n
        },\r\n
        onBlur: function (e) {\r\n
            if (this.$input) {\r\n
                var val = this.$input.val();\r\n
                this.setValue((val === "") ? this.value : val);\r\n
                if (this.options.hold && this.switches.fromKeyDown) {\r\n
                    this._stopSpin();\r\n
                }\r\n
            }\r\n
        },\r\n
        _startSpin: function (type, e) {\r\n
            if (!this.disabled) {\r\n
                var divisor = this.switches.count;\r\n
                if (divisor === 1) {\r\n
                    this._step(type, true);\r\n
                    divisor = 1;\r\n
                } else {\r\n
                    if (divisor < 3) {\r\n
                        divisor = 1.5;\r\n
                    } else {\r\n
                        if (divisor < 8) {\r\n
                            divisor = 2.5;\r\n
                        } else {\r\n
                            divisor = 6;\r\n
                        }\r\n
                    }\r\n
                }\r\n
                this.switches.timeout = setTimeout($.proxy(function () {\r\n
                    this._step(type, true);\r\n
                    this._startSpin(type);\r\n
                },\r\n
                this), this.switches.speed / divisor);\r\n
                this.switches.count++;\r\n
            }\r\n
        },\r\n
        _stopSpin: function (e) {\r\n
            if (this.switches.timeout !== undefined) {\r\n
                clearTimeout(this.switches.timeout);\r\n
                this.switches.timeout = undefined;\r\n
                this.switches.count = 1;\r\n
                this.trigger("change", this, this.value, this.lastValue);\r\n
            }\r\n
        },\r\n
        _increase: function (suspend) {\r\n
            var me = this;\r\n
            if (!me.readOnly) {\r\n
                var val = me.options.step;\r\n
                if (me._fromKeyDown) {\r\n
                    val = this.$input.val();\r\n
                    val = _.isEmpty(val) ? me.oldValue : parseFloat(val);\r\n
                } else {\r\n
                    if (me.getValue() !== "") {\r\n
                        if (me.options.allowAuto && me.getValue() == me.options.autoText) {\r\n
                            val = me.options.minValue - me.options.step;\r\n
                        } else {\r\n
                            val = parseFloat(me.getValue());\r\n
                        }\r\n
                        if (isNaN(val)) {\r\n
                            val = this.oldValue;\r\n
                        }\r\n
                    } else {\r\n
                        val = me.options.defaultValue;\r\n
                    }\r\n
                }\r\n
                me.setValue((this._add(val, me.options.step, (me.options.allowDecimal) ? 3 : 0) + " " + this.options.defaultUnit).trim(), suspend);\r\n
            }\r\n
        },\r\n
        _decrease: function (suspend) {\r\n
            var me = this;\r\n
            if (!me.readOnly) {\r\n
                var val = me.options.step;\r\n
                if (me._fromKeyDown) {\r\n
                    val = this.$input.val();\r\n
                    val = _.isEmpty(val) ? me.oldValue : parseFloat(val);\r\n
                } else {\r\n
                    if (me.getValue() !== "") {\r\n
                        if (me.options.allowAuto && me.getValue() == me.options.autoText) {\r\n
                            val = me.options.minValue;\r\n
                        } else {\r\n
                            val = parseFloat(me.getValue());\r\n
                        }\r\n
                        if (isNaN(val)) {\r\n
                            val = this.oldValue;\r\n
                        }\r\n
                        if (me.options.allowAuto && this._add(val, -me.options.step, (me.options.allowDecimal) ? 3 : 0) < me.options.minValue) {\r\n
                            me.setValue(me.options.autoText, true);\r\n
                            return;\r\n
                        }\r\n
                    } else {\r\n
                        val = me.options.defaultValue;\r\n
                    }\r\n
                }\r\n
                me.setValue((this._add(val, -me.options.step, (me.options.allowDecimal) ? 3 : 0) + " " + this.options.defaultUnit).trim(), suspend);\r\n
            }\r\n
        },\r\n
        _step: function (type, suspend) {\r\n
            (type) ? this._increase(suspend) : this._decrease(suspend);\r\n
        },\r\n
        _add: function (a, b, precision) {\r\n
            var x = Math.pow(10, precision || (this.options.allowDecimal) ? 2 : 0);\r\n
            return (Math.round(a * x) + Math.round(b * x)) / x;\r\n
        },\r\n
        _recalcUnits: function (value, fromUnit) {\r\n
            if (fromUnit.match(/(s|ms)$/i) && this.options.defaultUnit.match(/(s|ms)$/i)) {\r\n
                var v_out = value;\r\n
                if (fromUnit == "ms") {\r\n
                    v_out = v_out / 1000;\r\n
                }\r\n
                if (this.options.defaultUnit == "ms") {\r\n
                    v_out = v_out * 1000;\r\n
                }\r\n
                return v_out;\r\n
            }\r\n
            if (fromUnit.match(/(pt|in|cm|mm|pc)$/i) === null || this.options.defaultUnit.match(/(pt|in|cm|mm|pc)$/i) === null) {\r\n
                return value;\r\n
            }\r\n
            var v_out = value;\r\n
            if (fromUnit == "cm") {\r\n
                v_out = v_out * 10;\r\n
            } else {\r\n
                if (fromUnit == "pt") {\r\n
                    v_out = v_out * 25.4 / 72;\r\n
                } else {\r\n
                    if (fromUnit == "in") {\r\n
                        v_out = v_out * 25.4;\r\n
                    } else {\r\n
                        if (fromUnit == "pc") {\r\n
                            v_out = v_out * 25.4 / 6;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (this.options.defaultUnit == "cm") {\r\n
                v_out = v_out / 10;\r\n
            } else {\r\n
                if (this.options.defaultUnit == "pt") {\r\n
                    v_out = parseFloat((v_out * 72 / 25.4).toFixed(3));\r\n
                } else {\r\n
                    if (this.options.defaultUnit == "in") {\r\n
                        v_out = v_out / 25.4;\r\n
                    } else {\r\n
                        if (this.options.defaultUnit == "pc") {\r\n
                            v_out = v_out * 6 / 25.4;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            return v_out;\r\n
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
            <value> <int>19584</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
