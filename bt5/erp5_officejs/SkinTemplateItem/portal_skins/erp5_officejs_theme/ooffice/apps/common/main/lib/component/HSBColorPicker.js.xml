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
            <value> <string>ts44308799.3</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>HSBColorPicker.js</string> </value>
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
define(["common/main/lib/component/BaseView", "common/main/lib/util/utils"], function () {\r\n
    Common.UI.HSBColorPicker = Common.UI.BaseView.extend({\r\n
        template: _.template(\'<div class="hsb-colorpicker">\' + "<% if (this.showCurrentColor) { %>" + \'<div class="top-panel">\' + \'<span class="color-value">\' + \'<span class="transparent-color"></span>\' + "</span>" + \'<div class="color-text"></div>\' + "</div>" + "<% } %>" + "<div>" + \'<div class="cnt-hb">\' + \'<div class="cnt-hb-arrow"></div>\' + "</div>" + "<% if (this.changeSaturation) { %>" + \'<div class="cnt-root">\' + \'<div class="cnt-sat">\' + \'<div class="cnt-sat-arrow"></div>\' + "</div>" + "</div>" + "<% } %>" + "</div>" + "<% if (this.allowEmptyColor) { %>" + \'<div class="empty-color"><%= this.textNoColor %></div>\' + "<% } %>" + "</div>"),\r\n
        color: "#ff0000",\r\n
        options: {\r\n
            allowEmptyColor: false,\r\n
            changeSaturation: true,\r\n
            showCurrentColor: true\r\n
        },\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el),\r\n
            arrowSatBrightness,\r\n
            arrowHue,\r\n
            areaSatBrightness,\r\n
            areaHue,\r\n
            previewColor,\r\n
            previewTransparentColor,\r\n
            previewColorText,\r\n
            btnNoColor,\r\n
            hueVal = 0,\r\n
            saturationVal = 100,\r\n
            brightnessVal = 100;\r\n
            me.allowEmptyColor = me.options.allowEmptyColor;\r\n
            me.changeSaturation = me.options.changeSaturation;\r\n
            me.showCurrentColor = me.options.showCurrentColor;\r\n
            var onUpdateColor = function (hsb, transparent) {\r\n
                var rgbColor = new Common.Utils.RGBColor("hsb(" + hsb.h + "," + hsb.s + "," + hsb.b + ")"),\r\n
                hexColor = rgbColor.toHex();\r\n
                me.color = transparent ? "transparent" : hexColor;\r\n
                refreshUI();\r\n
                me.trigger("changecolor", me, me.color);\r\n
            };\r\n
            var refreshUI = function () {\r\n
                if (previewColor.length > 0 && previewTransparentColor.length > 0) {\r\n
                    if (me.color == "transparent") {\r\n
                        previewTransparentColor.show();\r\n
                    } else {\r\n
                        previewColor.css("background-color", me.color);\r\n
                        previewTransparentColor.hide();\r\n
                    }\r\n
                }\r\n
                if (areaSatBrightness.length > 0) {\r\n
                    areaSatBrightness.css("background-color", new Common.Utils.RGBColor("hsb(" + hueVal + ", 100, 100)").toHex());\r\n
                }\r\n
                if (previewColorText.length > 0) {\r\n
                    previewColorText[0].innerHTML = (me.color == "transparent") ? me.textNoColor : me.color.toUpperCase();\r\n
                }\r\n
                if (arrowSatBrightness.length > 0 && arrowHue.length > 0) {\r\n
                    arrowSatBrightness.css("left", saturationVal + "%");\r\n
                    arrowSatBrightness.css("top", 100 - brightnessVal + "%");\r\n
                    arrowHue.css("top", parseInt(hueVal * 100 / 360) + "%");\r\n
                }\r\n
            };\r\n
            var onSBAreaMouseMove = function (event, element, eOpts) {\r\n
                if (arrowSatBrightness.length > 0 && areaSatBrightness.length > 0) {\r\n
                    var pos = [Math.max(0, Math.min(100, (parseInt((event.pageX - areaSatBrightness.offset().left) / areaSatBrightness.width() * 100)))), Math.max(0, Math.min(100, (parseInt((event.pageY - areaSatBrightness.offset().top) / areaSatBrightness.height() * 100))))];\r\n
                    arrowSatBrightness.css("left", pos[0] + "%");\r\n
                    arrowSatBrightness.css("top", pos[1] + "%");\r\n
                    saturationVal = pos[0];\r\n
                    brightnessVal = 100 - pos[1];\r\n
                    onUpdateColor({\r\n
                        h: hueVal,\r\n
                        s: saturationVal,\r\n
                        b: brightnessVal\r\n
                    });\r\n
                }\r\n
            };\r\n
            var onHueAreaMouseMove = function (event, element, eOpts) {\r\n
                if (arrowHue && areaHue) {\r\n
                    var pos = Math.max(0, Math.min(100, (parseInt((event.pageY - areaHue.offset().top) / areaHue.height() * 100))));\r\n
                    arrowHue.css("top", pos + "%");\r\n
                    hueVal = parseInt(360 * pos / 100);\r\n
                    onUpdateColor({\r\n
                        h: hueVal,\r\n
                        s: saturationVal,\r\n
                        b: brightnessVal\r\n
                    });\r\n
                }\r\n
            };\r\n
            var onSBAreaMouseDown = function (event, element, eOpts) {\r\n
                $(document).on("mouseup", onSBAreaMouseUp);\r\n
                $(document).on("mousemove", onSBAreaMouseMove);\r\n
            };\r\n
            var onSBAreaMouseUp = function (event, element, eOpts) {\r\n
                $(document).off("mouseup", onSBAreaMouseUp);\r\n
                $(document).off("mousemove", onSBAreaMouseMove);\r\n
                onSBAreaMouseMove(event, element, eOpts);\r\n
            };\r\n
            var onHueAreaMouseDown = function (event, element, eOpts) {\r\n
                $(document).on("mouseup", onHueAreaMouseUp);\r\n
                $(document).on("mousemove", onHueAreaMouseMove);\r\n
                onHueAreaMouseMove(event, element, eOpts);\r\n
            };\r\n
            var onHueAreaMouseUp = function (event, element, eOpts) {\r\n
                $(document).off("mouseup", onHueAreaMouseUp);\r\n
                $(document).off("mousemove", onHueAreaMouseMove);\r\n
            };\r\n
            var onNoColorClick = function (cnt) {\r\n
                var hsbColor = new Common.util.RGBColor(me.color).toHSB();\r\n
                onUpdateColor(hsbColor, true);\r\n
            };\r\n
            var onAfterRender = function (ct) {\r\n
                var rootEl = $(me.el),\r\n
                hsbColor;\r\n
                if (rootEl) {\r\n
                    arrowSatBrightness = rootEl.find(".cnt-hb-arrow");\r\n
                    arrowHue = rootEl.find(".cnt-sat-arrow");\r\n
                    areaSatBrightness = rootEl.find(".cnt-hb");\r\n
                    areaHue = rootEl.find(".cnt-sat");\r\n
                    previewColor = rootEl.find(".color-value");\r\n
                    previewColorText = rootEl.find(".color-text");\r\n
                    btnNoColor = rootEl.find(".empty-color");\r\n
                    if (previewColor.length > 0) {\r\n
                        previewTransparentColor = previewColor.find(".transparent-color");\r\n
                    }\r\n
                    if (areaSatBrightness.length > 0) {\r\n
                        areaSatBrightness.off("mousedown");\r\n
                        areaSatBrightness.on("mousedown", onSBAreaMouseDown);\r\n
                    }\r\n
                    if (areaHue.length > 0) {\r\n
                        areaHue.off("mousedown");\r\n
                        areaHue.on("mousedown", onHueAreaMouseDown);\r\n
                    }\r\n
                    if (btnNoColor.length > 0) {\r\n
                        btnNoColor.off("click");\r\n
                        btnNoColor.on("click", onNoColorClick);\r\n
                    }\r\n
                    if (me.color == "transparent") {\r\n
                        hsbColor = {\r\n
                            h: 0,\r\n
                            s: 100,\r\n
                            b: 100\r\n
                        };\r\n
                    } else {\r\n
                        hsbColor = new Common.Utils.RGBColor(me.color).toHSB();\r\n
                    }\r\n
                    hueVal = hsbColor.h;\r\n
                    saturationVal = hsbColor.s;\r\n
                    brightnessVal = hsbColor.b;\r\n
                    if (hueVal == saturationVal && hueVal == brightnessVal && hueVal == 0) {\r\n
                        saturationVal = 100;\r\n
                    }\r\n
                    refreshUI();\r\n
                }\r\n
            };\r\n
            me.setColor = function (value) {\r\n
                if (me.color == value) {\r\n
                    return;\r\n
                }\r\n
                var hsbColor;\r\n
                if (value == "transparent") {\r\n
                    hsbColor = {\r\n
                        h: 0,\r\n
                        s: 100,\r\n
                        b: 100\r\n
                    };\r\n
                } else {\r\n
                    hsbColor = new Common.Utils.RGBColor(value).toHSB();\r\n
                }\r\n
                hueVal = hsbColor.h;\r\n
                saturationVal = hsbColor.s;\r\n
                brightnessVal = hsbColor.b;\r\n
                if (hueVal == saturationVal && hueVal == brightnessVal && hueVal == 0) {\r\n
                    saturationVal = 100;\r\n
                }\r\n
                me.color = value;\r\n
                refreshUI();\r\n
            };\r\n
            me.getColor = function () {\r\n
                return me.color;\r\n
            };\r\n
            me.on("render:after", onAfterRender);\r\n
            me.render();\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        textNoColor: "No Color"\r\n
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
            <value> <int>10837</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
