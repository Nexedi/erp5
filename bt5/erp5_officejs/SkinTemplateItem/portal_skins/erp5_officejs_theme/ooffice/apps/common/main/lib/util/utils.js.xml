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
            <value> <string>ts44308804.4</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>utils.js</string> </value>
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
if (Common.Utils === undefined) {\r\n
    Common.Utils = {};\r\n
}\r\n
Common.Utils = new(function () {\r\n
    var userAgent = navigator.userAgent.toLowerCase(),\r\n
    check = function (regex) {\r\n
        return regex.test(userAgent);\r\n
    },\r\n
    isStrict = document.compatMode == "CSS1Compat",\r\n
    version = function (is, regex) {\r\n
        var m;\r\n
        return (is && (m = regex.exec(userAgent))) ? parseFloat(m[1]) : 0;\r\n
    },\r\n
    docMode = document.documentMode,\r\n
    isOpera = check(/opera/),\r\n
    isOpera10_5 = isOpera && check(/version\\/10\\.5/),\r\n
    isChrome = check(/\\bchrome\\b/),\r\n
    isWebKit = check(/webkit/),\r\n
    isSafari = !isChrome && check(/safari/),\r\n
    isSafari2 = isSafari && check(/applewebkit\\/4/),\r\n
    isSafari3 = isSafari && check(/version\\/3/),\r\n
    isSafari4 = isSafari && check(/version\\/4/),\r\n
    isSafari5_0 = isSafari && check(/version\\/5\\.0/),\r\n
    isSafari5 = isSafari && check(/version\\/5/),\r\n
    isIE = !isOpera && (check(/msie/) || check(/trident/)),\r\n
    isIE7 = isIE && ((check(/msie 7/) && docMode != 8 && docMode != 9 && docMode != 10) || docMode == 7),\r\n
    isIE8 = isIE && ((check(/msie 8/) && docMode != 7 && docMode != 9 && docMode != 10) || docMode == 8),\r\n
    isIE9 = isIE && ((check(/msie 9/) && docMode != 7 && docMode != 8 && docMode != 10) || docMode == 9),\r\n
    isIE10 = isIE && ((check(/msie 10/) && docMode != 7 && docMode != 8 && docMode != 9) || docMode == 10),\r\n
    isIE11 = isIE && ((check(/trident\\/7\\.0/) && docMode != 7 && docMode != 8 && docMode != 9 && docMode != 10) || docMode == 11),\r\n
    isIE6 = isIE && check(/msie 6/),\r\n
    isGecko = !isWebKit && !isIE && check(/gecko/),\r\n
    isGecko3 = isGecko && check(/rv:1\\.9/),\r\n
    isGecko4 = isGecko && check(/rv:2\\.0/),\r\n
    isGecko5 = isGecko && check(/rv:5\\./),\r\n
    isGecko10 = isGecko && check(/rv:10\\./),\r\n
    isFF3_0 = isGecko3 && check(/rv:1\\.9\\.0/),\r\n
    isFF3_5 = isGecko3 && check(/rv:1\\.9\\.1/),\r\n
    isFF3_6 = isGecko3 && check(/rv:1\\.9\\.2/),\r\n
    isWindows = check(/windows|win32/),\r\n
    isMac = check(/macintosh|mac os x/),\r\n
    isLinux = check(/linux/),\r\n
    chromeVersion = version(true, /\\bchrome\\/(\\d+\\.\\d+)/),\r\n
    firefoxVersion = version(true, /\\bfirefox\\/(\\d+\\.\\d+)/),\r\n
    ieVersion = version(isIE, /msie (\\d+\\.\\d+)/),\r\n
    operaVersion = version(isOpera, /version\\/(\\d+\\.\\d+)/),\r\n
    safariVersion = version(isSafari, /version\\/(\\d+\\.\\d+)/),\r\n
    webKitVersion = version(isWebKit, /webkit\\/(\\d+\\.\\d+)/),\r\n
    isSecure = /^https/i.test(window.location.protocol),\r\n
    emailRe = /^(mailto:)?([a-z0-9\\._-]+@[a-z0-9\\.-]+\\.[a-z]{2,4})([a-яё0-9\\._%+-=\\? :&]*)/i,\r\n
    ipRe = /^(((https?)|(ftps?)):\\/\\/)?([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?(((1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9])\\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))(:\\d+)?(\\/[%\\-\\wа-яё]*(\\.[\\wа-яё]{2,})?(([\\wа-яё\\-\\.\\?\\\\\\/+@&#;`~=%!,]*)(\\.[\\wа-яё]{2,})?)*)*\\/?/i,\r\n
    hostnameRe = /^(((https?)|(ftps?)):\\/\\/)?([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?(([\\-\\wа-яё]+\\.)+[\\wа-яё\\-]{2,}(:\\d+)?(\\/[%\\-\\wа-яё]*(\\.[\\wа-яё]{2,})?(([\\wа-яё\\-\\.\\?\\\\\\/+@&#;`~=%!,]*)(\\.[\\wа-яё]{2,})?)*)*\\/?)/i,\r\n
    localRe = /^(((https?)|(ftps?)):\\/\\/)([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?(([\\-\\wа-яё]+)(:\\d+)?(\\/[%\\-\\wа-яё]*(\\.[\\wа-яё]{2,})?(([\\wа-яё\\-\\.\\?\\\\\\/+@&#;`~=%!,]*)(\\.[\\wа-яё]{2,})?)*)*\\/?)/i,\r\n
    emailStrongRe = /(mailto:)([a-z0-9\\._-]+@[a-z0-9\\.-]+\\.[a-z]{2,4})([a-яё0-9\\._%+-=\\? :&]*)/ig,\r\n
    ipStrongRe = /(((https?)|(ftps?)):\\/\\/([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?)(((1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9])\\.){3}(1[0-9]{2}|2[0-4][0-9]|25[0-5]|[1-9][0-9]|[0-9]))(:\\d+)?(\\/[%\\-\\wа-яё]*(\\.[\\wа-яё]{2,})?(([\\wа-яё\\-\\.\\?\\\\\\/+@&#;`~=%!,]*)(\\.[\\wа-яё]{2,})?)*)*\\/?/ig,\r\n
    hostnameStrongRe = /((((https?)|(ftps?)):\\/\\/([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?)|(([\\-\\wа-яё]*:?[\\-\\wа-яё]*@)?www\\.))((([\\-\\wа-яё]+\\.)+[\\wа-яё\\-]{2,}|([\\-\\wа-яё]+))(:\\d+)?(\\/[%\\-\\wа-яё]*(\\.[\\wа-яё]{2,})?(([\\wа-яё\\-\\.\\?\\\\\\/+@&#;`~=%!,]*)(\\.[\\wа-яё]{2,})?)*)*\\/?)/ig;\r\n
    return {\r\n
        userAgent: userAgent,\r\n
        isStrict: isStrict,\r\n
        isIEQuirks: isIE && (!isStrict && (isIE6 || isIE7 || isIE8 || isIE9)),\r\n
        isOpera: isOpera,\r\n
        isOpera10_5: isOpera10_5,\r\n
        isWebKit: isWebKit,\r\n
        isChrome: isChrome,\r\n
        isSafari: isSafari,\r\n
        isSafari3: isSafari3,\r\n
        isSafari4: isSafari4,\r\n
        isSafari5: isSafari5,\r\n
        isSafari5_0: isSafari5_0,\r\n
        isSafari2: isSafari2,\r\n
        isIE: isIE,\r\n
        isIE6: isIE6,\r\n
        isIE7: isIE7,\r\n
        isIE7m: isIE6 || isIE7,\r\n
        isIE7p: isIE && !isIE6,\r\n
        isIE8: isIE8,\r\n
        isIE8m: isIE6 || isIE7 || isIE8,\r\n
        isIE8p: isIE && !(isIE6 || isIE7),\r\n
        isIE9: isIE9,\r\n
        isIE9m: isIE6 || isIE7 || isIE8 || isIE9,\r\n
        isIE9p: isIE && !(isIE6 || isIE7 || isIE8),\r\n
        isIE10: isIE10,\r\n
        isIE10m: isIE6 || isIE7 || isIE8 || isIE9 || isIE10,\r\n
        isIE10p: isIE && !(isIE6 || isIE7 || isIE8 || isIE9),\r\n
        isIE11: isIE11,\r\n
        isIE11m: isIE6 || isIE7 || isIE8 || isIE9 || isIE10 || isIE11,\r\n
        isIE11p: isIE && !(isIE6 || isIE7 || isIE8 || isIE9 || isIE10),\r\n
        isGecko: isGecko,\r\n
        isGecko3: isGecko3,\r\n
        isGecko4: isGecko4,\r\n
        isGecko5: isGecko5,\r\n
        isGecko10: isGecko10,\r\n
        isFF3_0: isFF3_0,\r\n
        isFF3_5: isFF3_5,\r\n
        isFF3_6: isFF3_6,\r\n
        isFF4: 4 <= firefoxVersion && firefoxVersion < 5,\r\n
        isFF5: 5 <= firefoxVersion && firefoxVersion < 6,\r\n
        isFF10: 10 <= firefoxVersion && firefoxVersion < 11,\r\n
        isLinux: isLinux,\r\n
        isWindows: isWindows,\r\n
        isMac: isMac,\r\n
        chromeVersion: chromeVersion,\r\n
        firefoxVersion: firefoxVersion,\r\n
        ieVersion: ieVersion,\r\n
        operaVersion: operaVersion,\r\n
        safariVersion: safariVersion,\r\n
        webKitVersion: webKitVersion,\r\n
        isSecure: isSecure,\r\n
        emailRe: emailRe,\r\n
        ipRe: ipRe,\r\n
        hostnameRe: hostnameRe,\r\n
        localRe: localRe,\r\n
        emailStrongRe: emailStrongRe,\r\n
        ipStrongRe: ipStrongRe,\r\n
        hostnameStrongRe: hostnameStrongRe\r\n
    };\r\n
})();\r\n
Common.Utils.ThemeColor = new(function () {\r\n
    return {\r\n
        ThemeValues: [6, 15, 7, 16, 0, 1, 2, 3, 4, 5],\r\n
        setColors: function (colors, standart_colors) {\r\n
            var i, j, item;\r\n
            if (standart_colors && standart_colors.length > 0) {\r\n
                var standartcolors = [];\r\n
                for (i = 0; i < standart_colors.length; i++) {\r\n
                    item = this.getHexColor(standart_colors[i].get_r(), standart_colors[i].get_g(), standart_colors[i].get_b());\r\n
                    standartcolors.push(item);\r\n
                }\r\n
                this.standartcolors = standartcolors;\r\n
            }\r\n
            var effectСolors = [];\r\n
            for (i = 0; i < 6; i++) {\r\n
                for (j = 0; j < 10; j++) {\r\n
                    var idx = i + j * 6;\r\n
                    item = {\r\n
                        color: this.getHexColor(colors[idx].get_r(), colors[idx].get_g(), colors[idx].get_b()),\r\n
                        effectId: idx,\r\n
                        effectValue: this.ThemeValues[j]\r\n
                    };\r\n
                    effectСolors.push(item);\r\n
                }\r\n
            }\r\n
            this.effectcolors = effectСolors;\r\n
        },\r\n
        getEffectColors: function () {\r\n
            return this.effectcolors;\r\n
        },\r\n
        getStandartColors: function () {\r\n
            return this.standartcolors;\r\n
        },\r\n
        getHexColor: function (r, g, b) {\r\n
            r = r.toString(16);\r\n
            g = g.toString(16);\r\n
            b = b.toString(16);\r\n
            if (r.length == 1) {\r\n
                r = "0" + r;\r\n
            }\r\n
            if (g.length == 1) {\r\n
                g = "0" + g;\r\n
            }\r\n
            if (b.length == 1) {\r\n
                b = "0" + b;\r\n
            }\r\n
            return r + g + b;\r\n
        },\r\n
        getRgbColor: function (clr) {\r\n
            var color = (typeof(clr) == "object") ? clr.color : clr;\r\n
            color = color.replace(/#/, "");\r\n
            if (color.length == 3) {\r\n
                color = color.replace(/(.)/g, "$1$1");\r\n
            }\r\n
            color = parseInt(color, 16);\r\n
            var c = new CAscColor();\r\n
            c.put_type((typeof(clr) == "object" && clr.effectId !== undefined) ? c_oAscColor.COLOR_TYPE_SCHEME : c_oAscColor.COLOR_TYPE_SRGB);\r\n
            c.put_r(color >> 16);\r\n
            c.put_g((color & 65280) >> 8);\r\n
            c.put_b(color & 255);\r\n
            c.put_a(255);\r\n
            if (clr.effectId !== undefined) {\r\n
                c.put_value(clr.effectId);\r\n
            }\r\n
            return c;\r\n
        },\r\n
        colorValue2EffectId: function (clr) {\r\n
            if (typeof(clr) == "object" && clr.effectValue !== undefined && this.effectcolors) {\r\n
                for (var i = 0; i < this.effectcolors.length; i++) {\r\n
                    if (this.effectcolors[i].effectValue === clr.effectValue && clr.color.toUpperCase() === this.effectcolors[i].color.toUpperCase()) {\r\n
                        clr.effectId = this.effectcolors[i].effectId;\r\n
                        break;\r\n
                    }\r\n
                }\r\n
            }\r\n
            return clr;\r\n
        }\r\n
    };\r\n
})();\r\n
Common.Utils.Metric = new(function () {\r\n
    var me = this;\r\n
    me.c_MetricUnits = {\r\n
        cm: 0,\r\n
        pt: 1\r\n
    };\r\n
    me.currentMetric = me.c_MetricUnits.pt;\r\n
    me.metricName = ["cm", "pt"];\r\n
    return {\r\n
        c_MetricUnits: me.c_MetricUnits,\r\n
        metricName: me.metricName,\r\n
        setCurrentMetric: function (value) {\r\n
            me.currentMetric = value;\r\n
        },\r\n
        getCurrentMetric: function () {\r\n
            return me.currentMetric;\r\n
        },\r\n
        fnRecalcToMM: function (value) {\r\n
            if (value !== null && value !== undefined) {\r\n
                switch (me.currentMetric) {\r\n
                case me.c_MetricUnits.cm:\r\n
                    return value * 10;\r\n
                case me.c_MetricUnits.pt:\r\n
                    return value * 25.4 / 72;\r\n
                }\r\n
            }\r\n
            return value;\r\n
        },\r\n
        fnRecalcFromMM: function (value) {\r\n
            switch (me.currentMetric) {\r\n
            case me.c_MetricUnits.cm:\r\n
                return parseFloat((value / 10).toFixed(4));\r\n
            case me.c_MetricUnits.pt:\r\n
                return parseFloat((value * 72 / 25.4).toFixed(3));\r\n
            }\r\n
            return value;\r\n
        }\r\n
    };\r\n
})();\r\n
Common.Utils.RGBColor = function (colorString) {\r\n
    var r, g, b;\r\n
    if (colorString.charAt(0) == "#") {\r\n
        colorString = colorString.substr(1, 6);\r\n
    }\r\n
    colorString = colorString.replace(/ /g, "");\r\n
    colorString = colorString.toLowerCase();\r\n
    var colorDefinitions = [{\r\n
        re: /^rgb\\((\\d{1,3}),\\s*(\\d{1,3}),\\s*(\\d{1,3})\\)$/,\r\n
        process: function (bits) {\r\n
            return [parseInt(bits[1]), parseInt(bits[2]), parseInt(bits[3])];\r\n
        }\r\n
    },\r\n
    {\r\n
        re: /^hsb\\((\\d{1,3}),\\s*(\\d{1,3}),\\s*(\\d{1,3})\\)$/,\r\n
        process: function (bits) {\r\n
            var rgb = {};\r\n
            var h = Math.round(bits[1]);\r\n
            var s = Math.round(bits[2] * 255 / 100);\r\n
            var v = Math.round(bits[3] * 255 / 100);\r\n
            if (s == 0) {\r\n
                rgb.r = rgb.g = rgb.b = v;\r\n
            } else {\r\n
                var t1 = v;\r\n
                var t2 = (255 - s) * v / 255;\r\n
                var t3 = (t1 - t2) * (h % 60) / 60;\r\n
                if (h == 360) {\r\n
                    h = 0;\r\n
                }\r\n
                if (h < 60) {\r\n
                    rgb.r = t1;\r\n
                    rgb.b = t2;\r\n
                    rgb.g = t2 + t3;\r\n
                } else {\r\n
                    if (h < 120) {\r\n
                        rgb.g = t1;\r\n
                        rgb.b = t2;\r\n
                        rgb.r = t1 - t3;\r\n
                    } else {\r\n
                        if (h < 180) {\r\n
                            rgb.g = t1;\r\n
                            rgb.r = t2;\r\n
                            rgb.b = t2 + t3;\r\n
                        } else {\r\n
                            if (h < 240) {\r\n
                                rgb.b = t1;\r\n
                                rgb.r = t2;\r\n
                                rgb.g = t1 - t3;\r\n
                            } else {\r\n
                                if (h < 300) {\r\n
                                    rgb.b = t1;\r\n
                                    rgb.g = t2;\r\n
                                    rgb.r = t2 + t3;\r\n
                                } else {\r\n
                                    if (h < 360) {\r\n
                                        rgb.r = t1;\r\n
                                        rgb.g = t2;\r\n
                                        rgb.b = t1 - t3;\r\n
                                    } else {\r\n
                                        rgb.r = 0;\r\n
                                        rgb.g = 0;\r\n
                                        rgb.b = 0;\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            return [Math.round(rgb.r), Math.round(rgb.g), Math.round(rgb.b)];\r\n
        }\r\n
    },\r\n
    {\r\n
        re: /^(\\w{2})(\\w{2})(\\w{2})$/,\r\n
        process: function (bits) {\r\n
            return [parseInt(bits[1], 16), parseInt(bits[2], 16), parseInt(bits[3], 16)];\r\n
        }\r\n
    },\r\n
    {\r\n
        re: /^(\\w{1})(\\w{1})(\\w{1})$/,\r\n
        process: function (bits) {\r\n
            return [parseInt(bits[1] + bits[1], 16), parseInt(bits[2] + bits[2], 16), parseInt(bits[3] + bits[3], 16)];\r\n
        }\r\n
    }];\r\n
    for (var i = 0; i < colorDefinitions.length; i++) {\r\n
        var re = colorDefinitions[i].re;\r\n
        var processor = colorDefinitions[i].process;\r\n
        var bits = re.exec(colorString);\r\n
        if (bits) {\r\n
            var channels = processor(bits);\r\n
            r = channels[0];\r\n
            g = channels[1];\r\n
            b = channels[2];\r\n
        }\r\n
    }\r\n
    r = (r < 0 || isNaN(r)) ? 0 : ((r > 255) ? 255 : r);\r\n
    g = (g < 0 || isNaN(g)) ? 0 : ((g > 255) ? 255 : g);\r\n
    b = (b < 0 || isNaN(b)) ? 0 : ((b > 255) ? 255 : b);\r\n
    var isEqual = function (color) {\r\n
        return ((r == color.r) && (g == color.g) && (b == color.b));\r\n
    };\r\n
    var toRGB = function () {\r\n
        return "rgb(" + r + ", " + g + ", " + b + ")";\r\n
    };\r\n
    var toRGBA = function (alfa) {\r\n
        if (alfa === undefined) {\r\n
            alfa = 1;\r\n
        }\r\n
        return "rgba(" + r + ", " + g + ", " + b + ", " + alfa + ")";\r\n
    };\r\n
    var toHex = function () {\r\n
        var _r = r.toString(16);\r\n
        var _g = g.toString(16);\r\n
        var _b = b.toString(16);\r\n
        if (_r.length == 1) {\r\n
            _r = "0" + _r;\r\n
        }\r\n
        if (_g.length == 1) {\r\n
            _g = "0" + _g;\r\n
        }\r\n
        if (_b.length == 1) {\r\n
            _b = "0" + _b;\r\n
        }\r\n
        return "#" + _r + _g + _b;\r\n
    };\r\n
    var toHSB = function () {\r\n
        var hsb = {\r\n
            h: 0,\r\n
            s: 0,\r\n
            b: 0\r\n
        };\r\n
        var min = Math.min(r, g, b);\r\n
        var max = Math.max(r, g, b);\r\n
        var delta = max - min;\r\n
        hsb.b = max;\r\n
        hsb.s = max != 0 ? 255 * delta / max : 0;\r\n
        if (hsb.s != 0) {\r\n
            if (r == max) {\r\n
                hsb.h = 0 + (g - b) / delta;\r\n
            } else {\r\n
                if (g == max) {\r\n
                    hsb.h = 2 + (b - r) / delta;\r\n
                } else {\r\n
                    hsb.h = 4 + (r - g) / delta;\r\n
                }\r\n
            }\r\n
        } else {\r\n
            hsb.h = 0;\r\n
        }\r\n
        hsb.h *= 60;\r\n
        if (hsb.h < 0) {\r\n
            hsb.h += 360;\r\n
        }\r\n
        hsb.s *= 100 / 255;\r\n
        hsb.b *= 100 / 255;\r\n
        hsb.h = parseInt(hsb.h);\r\n
        hsb.s = parseInt(hsb.s);\r\n
        hsb.b = parseInt(hsb.b);\r\n
        return hsb;\r\n
    };\r\n
    return {\r\n
        r: r,\r\n
        g: g,\r\n
        b: b,\r\n
        isEqual: isEqual,\r\n
        toRGB: toRGB,\r\n
        toRGBA: toRGBA,\r\n
        toHex: toHex,\r\n
        toHSB: toHSB\r\n
    };\r\n
};\r\n
Common.Utils.String = new(function () {\r\n
    return {\r\n
        format: function (format) {\r\n
            var args = _.toArray(arguments).slice(1);\r\n
            return format.replace(/\\{(\\d+)\\}/g, function (s, i) {\r\n
                return args[i];\r\n
            });\r\n
        },\r\n
        htmlEncode: function (string) {\r\n
            return _.escape(string);\r\n
        },\r\n
        htmlDecode: function (string) {\r\n
            return _.unescape(string);\r\n
        },\r\n
        ellipsis: function (value, len, word) {\r\n
            if (value && value.length > len) {\r\n
                if (word) {\r\n
                    var vs = value.substr(0, len - 2),\r\n
                    index = Math.max(vs.lastIndexOf(" "), vs.lastIndexOf("."), vs.lastIndexOf("!"), vs.lastIndexOf("?"));\r\n
                    if (index !== -1 && index >= (len - 15)) {\r\n
                        return vs.substr(0, index) + "...";\r\n
                    }\r\n
                }\r\n
                return value.substr(0, len - 3) + "...";\r\n
            }\r\n
            return value;\r\n
        },\r\n
        platformKey: function (string, template, hookFn) {\r\n
            if (_.isEmpty(template)) {\r\n
                template = " ({0})";\r\n
            }\r\n
            if (Common.Utils.isMac) {\r\n
                if (_.isFunction(hookFn)) {\r\n
                    string = hookFn.call(this, string);\r\n
                }\r\n
                return Common.Utils.String.format(template, string.replace(/\\+(?=\\S)/g, "").replace(/Ctrl|ctrl/g, "⌘").replace(/Alt|alt/g, "⌥").replace(/Shift|shift/g, "⇧"));\r\n
            }\r\n
            return Common.Utils.String.format(template, string);\r\n
        }\r\n
    };\r\n
})();\r\n
Common.Utils.isBrowserSupported = function () {\r\n
    return ! ((Common.Utils.ieVersion != 0 && Common.Utils.ieVersion < 9) || (Common.Utils.safariVersion != 0 && Common.Utils.safariVersion < 5) || (Common.Utils.firefoxVersion != 0 && Common.Utils.firefoxVersion < 4) || (Common.Utils.chromeVersion != 0 && Common.Utils.chromeVersion < 7) || (Common.Utils.operaVersion != 0 && Common.Utils.operaVersion < 10.5));\r\n
};\r\n
Common.Utils.showBrowserRestriction = function () {\r\n
    var editor = (window.DE ? "Document" : window.SSE ? "Spreadsheet" : window.PE ? "Presentation" : "that");\r\n
    var newDiv = document.createElement("div");\r\n
    newDiv.innerHTML = \'<div class="application-error-panel">\' + \'<div class="application-error-message-block">\' + \'<div class="application-error-message-inner">\' + \'<div class="application-error-message-title">Your browser is not supported.</div>\' + \'<div class="application-error-message-text">Sorry, \' + editor + " Editor is currently only supported in the latest versions of the Chrome, Firefox, Safari or Internet Explorer web browsers.</div>" + "</div>" + "</div>" + \'<div class="application-error-message-auxiliary"></div>\' + "</div>";\r\n
    document.body.appendChild(newDiv);\r\n
    $("#loading-mask").hide().remove();\r\n
    $("#viewport").hide().remove();\r\n
};\r\n
Common.Utils.applyCustomization = function (config, elmap) {\r\n
    for (var name in config) {\r\n
        var $el;\r\n
        if ( !! elmap[name]) {\r\n
            $el = $(elmap[name]);\r\n
            if ($el.length) {\r\n
                var item = config[name];\r\n
                if (item === false || item.visible === false) {\r\n
                    $el.hide();\r\n
                } else {\r\n
                    if ( !! item.text) {\r\n
                        $el.text(item.text);\r\n
                    }\r\n
                    if (item.visible === false) {\r\n
                        $el.hide();\r\n
                    }\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
};\r\n
String.prototype.strongMatch = function (regExp) {\r\n
    if (regExp && regExp instanceof RegExp) {\r\n
        var arr = this.toString().match(regExp);\r\n
        return !! (arr && arr.length > 0 && arr[0].length == this.length);\r\n
    }\r\n
    return false;\r\n
};

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>21684</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
