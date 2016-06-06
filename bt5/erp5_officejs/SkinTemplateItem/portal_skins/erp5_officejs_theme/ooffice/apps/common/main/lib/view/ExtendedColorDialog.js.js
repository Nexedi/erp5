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
            <value> <string>ts44321418.61</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ExtendedColorDialog.js</string> </value>
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
define(["text!common/main/lib/template/ExtendedColorDialog.template", "common/main/lib/component/HSBColorPicker", "common/main/lib/component/MetricSpinner", "common/main/lib/component/MaskedField", "common/main/lib/component/Window"], function (dlgTemplate) {\r\n
    Common.UI.ExtendedColorDialog = Common.UI.Window.extend(_.extend({\r\n
        tpl: _.template(dlgTemplate),\r\n
        options: {},\r\n
        rendered: false,\r\n
        initialize: function (options) {\r\n
            Common.UI.Window.prototype.initialize.call(this, {\r\n
                cls: "extended-color-dlg",\r\n
                tpl: this.tpl({\r\n
                    txtNew: this.textNew,\r\n
                    txtCurrent: this.textCurrent,\r\n
                    txtAdd: this.addButtonText,\r\n
                    txtCancel: this.cancelButtonText\r\n
                }),\r\n
                header: false,\r\n
                width: 340,\r\n
                height: 272\r\n
            });\r\n
            this.hexRe = /\\s*#?([0-9a-fA-F][0-9a-fA-F]?)([0-9a-fA-F][0-9a-fA-F]?)([0-9a-fA-F][0-9a-fA-F]?)\\s*/;\r\n
        },\r\n
        render: function () {\r\n
            var me = this;\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.colorsPicker = new Common.UI.HSBColorPicker({\r\n
                el: $("#id-hsb-colorpicker"),\r\n
                showCurrentColor: false\r\n
            });\r\n
            this.colorsPicker.on("changecolor", _.bind(this.onChangeColor, this));\r\n
            this.colorNew = $("#field-new-color");\r\n
            this.colorSaved = $("#field-start-color");\r\n
            this.spinR = new Common.UI.MetricSpinner({\r\n
                el: $("#extended-spin-r"),\r\n
                step: 1,\r\n
                width: 63,\r\n
                value: "0",\r\n
                defaultUnit: "",\r\n
                maxValue: 255,\r\n
                minValue: 0,\r\n
                tabindex: 1,\r\n
                maskExp: /[0-9]/,\r\n
                allowDecimal: false\r\n
            });\r\n
            this.spinG = new Common.UI.MetricSpinner({\r\n
                el: $("#extended-spin-g"),\r\n
                step: 1,\r\n
                width: 63,\r\n
                value: "0",\r\n
                defaultUnit: "",\r\n
                maxValue: 255,\r\n
                minValue: 0,\r\n
                tabindex: 2,\r\n
                maskExp: /[0-9]/,\r\n
                allowDecimal: false\r\n
            });\r\n
            this.spinB = new Common.UI.MetricSpinner({\r\n
                el: $("#extended-spin-b"),\r\n
                step: 1,\r\n
                width: 63,\r\n
                value: "0",\r\n
                defaultUnit: "",\r\n
                maxValue: 255,\r\n
                minValue: 0,\r\n
                tabindex: 3,\r\n
                maskExp: /[0-9]/,\r\n
                allowDecimal: false\r\n
            });\r\n
            this.textColor = new Common.UI.MaskedField({\r\n
                el: $("#extended-text-color"),\r\n
                width: 55,\r\n
                maskExp: /[a-fA-F0-9]/,\r\n
                maxLength: 6\r\n
            });\r\n
            this.spinR.on("change", _.bind(this.showColor, this, null, true)).on("changing", _.bind(this.onChangingRGB, this, 1));\r\n
            this.spinG.on("change", _.bind(this.showColor, this, null, true)).on("changing", _.bind(this.onChangingRGB, this, 2));\r\n
            this.spinB.on("change", _.bind(this.showColor, this, null, true)).on("changing", _.bind(this.onChangingRGB, this, 3));\r\n
            this.textColor.on("change", _.bind(this.onChangeMaskedField, this));\r\n
            this.textColor.on("changed", _.bind(this.onChangedMaskedField, this));\r\n
            this.textColor.$el.attr("tabindex", 4);\r\n
            this.spinR.$el.find("input").attr("maxlength", 3);\r\n
            this.spinG.$el.find("input").attr("maxlength", 3);\r\n
            this.spinB.$el.find("input").attr("maxlength", 3);\r\n
            this.on("close", function () {\r\n
                me.trigger("onmodalresult", 0);\r\n
            });\r\n
            function onBtnClick(event) {\r\n
                me.trigger("onmodalresult", parseInt(event.currentTarget.attributes["result"].value));\r\n
                me.close(true);\r\n
            }\r\n
            $(this)[0].getChild(".footer .dlg-btn").on("click", onBtnClick);\r\n
            this.rendered = true;\r\n
            if (this.color !== undefined) {\r\n
                this.setColor(this.color);\r\n
            }\r\n
            return this;\r\n
        },\r\n
        onChangeColor: function (o, color) {\r\n
            this.colorNew.css({\r\n
                "background-color": color\r\n
            });\r\n
            this.stopevents = true;\r\n
            var values = color.match(this.hexRe);\r\n
            this.spinR.setValue(parseInt(values[1], 16));\r\n
            this.spinG.setValue(parseInt(values[2], 16));\r\n
            this.spinB.setValue(parseInt(values[3], 16));\r\n
            this.textColor.setValue((values[1] + values[2] + values[3]).toUpperCase());\r\n
            this.stopevents = false;\r\n
        },\r\n
        showColor: function (exlude, validate) {\r\n
            if (!this.stopevents) {\r\n
                var val = this.spinR.getNumberValue();\r\n
                var r = (val == null || val < 0) ? 0 : (val > 255 ? 255 : val);\r\n
                if (validate) {\r\n
                    this.spinR.setValue(r, true);\r\n
                }\r\n
                r = r.toString(16);\r\n
                val = this.spinG.getNumberValue();\r\n
                var g = (val == null || val < 0) ? 0 : (val > 255 ? 255 : val);\r\n
                if (validate) {\r\n
                    this.spinG.setValue(g, true);\r\n
                }\r\n
                g = g.toString(16);\r\n
                val = this.spinB.getNumberValue();\r\n
                var b = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val));\r\n
                if (validate) {\r\n
                    this.spinB.setValue(b, true);\r\n
                }\r\n
                b = b.toString(16);\r\n
                var color = (r.length == 1 ? "0" + r : r) + (g.length == 1 ? "0" + g : g) + (b.length == 1 ? "0" + b : b);\r\n
                this.colorsPicker.setColor("#" + color);\r\n
                if (exlude != "hex") {\r\n
                    this.textColor.setValue(color.toUpperCase());\r\n
                }\r\n
                this.colorNew.css("background-color", "#" + color);\r\n
            }\r\n
        },\r\n
        onChangingRGB: function (type, cmp, newValue, e) {\r\n
            if (!this.stopevents) {\r\n
                var r, g, b, val;\r\n
                newValue = (_.isEmpty(newValue) || isNaN(parseInt(newValue))) ? parseInt(cmp.getValue()) : parseInt(newValue);\r\n
                switch (type) {\r\n
                case 1:\r\n
                    r = ((newValue == null || isNaN(newValue) || newValue < 0) ? 0 : (newValue > 255 ? 255 : newValue)).toString(16);\r\n
                    val = this.spinG.getNumberValue();\r\n
                    g = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    val = this.spinB.getNumberValue();\r\n
                    b = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    break;\r\n
                case 2:\r\n
                    val = this.spinR.getNumberValue();\r\n
                    r = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    g = ((newValue == null || isNaN(newValue) || newValue < 0) ? 0 : (newValue > 255 ? 255 : newValue)).toString(16);\r\n
                    val = this.spinB.getNumberValue();\r\n
                    b = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    break;\r\n
                case 3:\r\n
                    val = this.spinR.getNumberValue();\r\n
                    r = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    val = this.spinG.getNumberValue();\r\n
                    g = ((val == null || val < 0) ? 0 : (val > 255 ? 255 : val)).toString(16);\r\n
                    b = ((newValue == null || isNaN(newValue) || newValue < 0) ? 0 : (newValue > 255 ? 255 : newValue)).toString(16);\r\n
                    break;\r\n
                }\r\n
                var color = (r.length == 1 ? "0" + r : r) + (g.length == 1 ? "0" + g : g) + (b.length == 1 ? "0" + b : b);\r\n
                this.colorsPicker.setColor("#" + color);\r\n
                this.textColor.setValue(color.toUpperCase());\r\n
                this.colorNew.css("background-color", "#" + color);\r\n
            }\r\n
        },\r\n
        onChangeMaskedField: function (field, newValue) {\r\n
            newValue = ((/^[a-fA-F0-9]{0,6}$/.test(newValue))) ? newValue : "000000";\r\n
            newValue = "000000" + newValue;\r\n
            var colors = newValue.match(/([a-fA-F0-9]{2})([a-fA-F0-9]{2})([a-fA-F0-9]{2})$/i);\r\n
            this.stopevents = true;\r\n
            this.spinR.setValue(parseInt(colors[1], 16));\r\n
            this.spinG.setValue(parseInt(colors[2], 16));\r\n
            this.spinB.setValue(parseInt(colors[3], 16));\r\n
            this.stopevents = false;\r\n
            if (this.rendered) {\r\n
                this.showColor("hex");\r\n
            }\r\n
        },\r\n
        onChangedMaskedField: function (field, newValue) {\r\n
            var me = this;\r\n
            if (!/^[a-fA-F0-9]{0,6}$/.test(newValue) || _.isEmpty(newValue)) {\r\n
                field.setValue("000000");\r\n
            }\r\n
            if (this.rendered) {\r\n
                this.showColor("", true);\r\n
            }\r\n
        },\r\n
        getColor: function () {\r\n
            var color = /#?([a-fA-F0-9]{6})/.exec(this.colorsPicker.getColor());\r\n
            return color ? color[1] : null;\r\n
        },\r\n
        setColor: function (cl) {\r\n
            var me = this;\r\n
            if (this.rendered !== true) {\r\n
                this.color = cl;\r\n
                return;\r\n
            }\r\n
            var color = /#?([a-fA-F0-9]{6})/.test(cl) ? cl : "ff0000";\r\n
            me.colorsPicker.setColor("#" + color);\r\n
            function keepcolor() {\r\n
                if (cl == "transparent") {\r\n
                    me.colorSaved.addClass("color-transparent");\r\n
                } else {\r\n
                    me.colorSaved.removeClass("color-transparent");\r\n
                    me.colorSaved.css("background-color", "#" + cl);\r\n
                }\r\n
                me.colorNew.css("background-color", "#" + color);\r\n
            }\r\n
            keepcolor();\r\n
            me.stopevents = true;\r\n
            var values = me.hexRe.exec(color);\r\n
            me.spinR.setValue(parseInt(values[1], 16));\r\n
            me.spinG.setValue(parseInt(values[2], 16));\r\n
            me.spinB.setValue(parseInt(values[3], 16));\r\n
            me.textColor.setValue((values[1] + values[2] + values[3]).toUpperCase());\r\n
            me.stopevents = false;\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.Window.prototype.show.apply(this, arguments);\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                me.getChild("#extended-text-color").focus();\r\n
            },\r\n
            50);\r\n
        },\r\n
        cancelButtonText: "Cancel",\r\n
        addButtonText: "Add",\r\n
        textNew: "New",\r\n
        textCurrent: "Current",\r\n
        textRGBErr: "The entered value is incorrect.<br>Please enter a numeric value between 0 and 255.",\r\n
        textHexErr: "The entered value is incorrect.<br>Please enter a value between 000000 and FFFFFF."\r\n
    },\r\n
    Common.UI.ExtendedColorDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12867</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
