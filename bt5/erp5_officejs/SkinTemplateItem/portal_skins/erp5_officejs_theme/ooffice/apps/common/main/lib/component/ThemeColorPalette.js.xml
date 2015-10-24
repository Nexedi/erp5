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
            <value> <string>ts44308801.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ThemeColorPalette.js</string> </value>
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
define(["common/main/lib/component/BaseView", "common/main/lib/view/ExtendedColorDialog"], function () {\r\n
    Common.UI.ThemeColorPalette = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            dynamiccolors: 10,\r\n
            allowReselect: true,\r\n
            value: "000000"\r\n
        },\r\n
        template: _.template(\'<div style="padding: 12px;">\' + "<% var me = this; %>" + "<% $(colors).each(function(num, item) { %>" + \'<% if (me.isBlankSeparator(item)) { %> <div class="palette-color-spacer" style="width:100%;height:8px;float:left;"></div>\' + \'<% } else if (me.isSeparator(item)) { %> </div><div class="palette-color-separator" style="width:100%;height:1px;float:left;border-bottom: 1px solid #E0E0E0"></div><div style="padding: 12px;">\' + "<% } else if (me.isColor(item)) { %> " + \'<a class="palette-color color-<%=item%>" style="background:#<%=item%>" hidefocus="on">\' + \'<em><span style="background:#<%=item%>;" unselectable="on">&#160;</span></em>\' + "</a>" + "<% } else if (me.isTransparent(item)) { %>" + \'<a class="color-<%=item%>" hidefocus="on">\' + \'<em><span unselectable="on">&#160;</span></em>\' + "</a>" + "<% } else if (me.isEffect(item)) { %>" + \'<a effectid="<%=item.effectId%>" effectvalue="<%=item.effectValue%>" class="palette-color-effect color-<%=item.color%>" style="background:#<%=item.color%>" hidefocus="on">\' + \'<em><span style="background:#<%=item.color%>;" unselectable="on">&#160;</span></em>\' + "</a>" + "<% } else if (me.isCaption(item)) { %>" + \'<div class="palette-color-caption" style="width:100%;float:left;font-size: 11px;"><%=item%></div>\' + "<% } %>" + "<% }); %>" + "</div>" + "<% if (me.options.dynamiccolors!==undefined) { %>" + \'<div class="palette-color-spacer" style="width:100%;height:8px;float:left;"></div><div style="padding: 12px;">\' + "<% for (var i=0; i<me.options.dynamiccolors; i++) { %>" + \'<a class="color-dynamic-<%=i%> dynamic-empty-color" style="background:#ffffff" color="" hidefocus="on">\' + \'<em><span unselectable="on">&#160;</span></em></a>\' + "<% } %>" + "<% } %>" + "</div>"),\r\n
        colorRe: /(?:^|\\s)color-(.{6})(?:\\s|$)/,\r\n
        selectedCls: "selected",\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            this.colors = me.options.colors || [{\r\n
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
            "-", "--", "-", "000000", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39"];\r\n
            el.addClass("theme-colorpalette");\r\n
            this.render();\r\n
            if (this.options.updateColorsArr) {\r\n
                this.updateColors(this.options.updateColorsArr[0], this.options.updateColorsArr[1]);\r\n
            }\r\n
            if (this.options.value) {\r\n
                this.select(this.options.value, true);\r\n
            }\r\n
            this.updateCustomColors();\r\n
            el.closest(".btn-group").on("show.bs.dropdown", _.bind(this.updateCustomColors, this));\r\n
            el.closest(".dropdown-submenu").on("show.bs.dropdown", _.bind(this.updateCustomColors, this));\r\n
            el.on("click", _.bind(this.handleClick, this));\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template({\r\n
                colors: this.colors\r\n
            }));\r\n
            return this;\r\n
        },\r\n
        isBlankSeparator: function (v) {\r\n
            return typeof(v) == "string" && v == "-";\r\n
        },\r\n
        isSeparator: function (v) {\r\n
            return typeof(v) == "string" && v == "--";\r\n
        },\r\n
        isColor: function (v) {\r\n
            return typeof(v) == "string" && (/[0-9A-F]{6}/).test(v);\r\n
        },\r\n
        isTransparent: function (v) {\r\n
            return typeof(v) == "string" && (v == "transparent");\r\n
        },\r\n
        isCaption: function (v) {\r\n
            return (typeof(v) == "string" && v != "-" && v != "--" && !(/[0-9A-F]{6}|transparent/).test(v));\r\n
        },\r\n
        isEffect: function (v) {\r\n
            return (typeof(v) == "object" && v.effectId !== undefined);\r\n
        },\r\n
        getColor: function () {\r\n
            return this.value;\r\n
        },\r\n
        updateCustomColors: function () {\r\n
            var el = $(this.el);\r\n
            if (el) {\r\n
                var colors = localStorage["asc." + window.storagename + ".colors.custom"];\r\n
                colors = colors ? colors.split(",") : [];\r\n
                var i = -1,\r\n
                colorEl, c = colors.length < this.options.dynamiccolors ? colors.length : this.options.dynamiccolors;\r\n
                while (++i < c) {\r\n
                    colorEl = el.find(".color-dynamic-" + i);\r\n
                    colorEl.removeClass("dynamic-empty-color").attr("color", colors[i]);\r\n
                    colorEl.find("span").css({\r\n
                        "background-color": "#" + colors[i]\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        handleClick: function (e) {\r\n
            var me = this;\r\n
            var target = $(e.target).closest("a");\r\n
            var color, cmp;\r\n
            if (target.length == 0) {\r\n
                return;\r\n
            }\r\n
            if (target.hasClass("color-transparent")) {\r\n
                $(me.el).find("a." + me.selectedCls).removeClass(me.selectedCls);\r\n
                target.addClass(me.selectedCls);\r\n
                me.value = "transparent";\r\n
                me.trigger("select", me, "transparent");\r\n
            } else {\r\n
                if (! (target[0].className.search("color-dynamic") < 0)) {\r\n
                    if (!/dynamic-empty-color/.test(target[0].className)) {\r\n
                        $(me.el).find("a." + me.selectedCls).removeClass(me.selectedCls);\r\n
                        target.addClass(me.selectedCls);\r\n
                        color = target.attr("color");\r\n
                        if (color) {\r\n
                            me.trigger("select", me, color);\r\n
                        }\r\n
                        me.value = color.toUpperCase();\r\n
                    } else {\r\n
                        setTimeout(function () {\r\n
                            me.addNewColor();\r\n
                        },\r\n
                        10);\r\n
                    }\r\n
                } else {\r\n
                    if (!/^[a-fA-F0-9]{6}$/.test(me.value) || _.indexOf(me.colors, me.value) < 0) {\r\n
                        me.value = false;\r\n
                    }\r\n
                    $(me.el).find("a." + me.selectedCls).removeClass(me.selectedCls);\r\n
                    target.addClass(me.selectedCls);\r\n
                    color = target[0].className.match(me.colorRe)[1];\r\n
                    if (target.hasClass("palette-color-effect")) {\r\n
                        var effectId = parseInt(target.attr("effectid"));\r\n
                        if (color) {\r\n
                            me.value = color.toUpperCase();\r\n
                            me.trigger("select", me, {\r\n
                                color: color,\r\n
                                effectId: effectId\r\n
                            });\r\n
                        }\r\n
                    } else {\r\n
                        if (/#?[a-fA-F0-9]{6}/.test(color)) {\r\n
                            color = /#?([a-fA-F0-9]{6})/.exec(color)[1].toUpperCase();\r\n
                            me.value = color;\r\n
                            me.trigger("select", me, color);\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        setCustomColor: function (color) {\r\n
            var el = $(this.el);\r\n
            color = /#?([a-fA-F0-9]{6})/.exec(color);\r\n
            if (color) {\r\n
                this.saveCustomColor(color[1]);\r\n
                el.find("a." + this.selectedCls).removeClass(this.selectedCls);\r\n
                var child = el.find(".dynamic-empty-color");\r\n
                if (child.length == 0) {\r\n
                    this.updateCustomColors();\r\n
                    child = el.find(".color-dynamic-" + (this.options.dynamiccolors - 1));\r\n
                }\r\n
                child.first().removeClass("dynamic-empty-color").addClass(this.selectedCls).attr("color", color[1]);\r\n
                child.first().find("span").css({\r\n
                    "background-color": "#" + color[1]\r\n
                });\r\n
                this.select(color[1], true);\r\n
            }\r\n
        },\r\n
        saveCustomColor: function (color) {\r\n
            var colors = localStorage["asc." + window.storagename + ".colors.custom"];\r\n
            colors = colors ? colors.split(",") : [];\r\n
            if (colors.push(color) > this.options.dynamiccolors) {\r\n
                colors.shift();\r\n
            }\r\n
            localStorage["asc." + window.storagename + ".colors.custom"] = colors.join().toUpperCase();\r\n
        },\r\n
        addNewColor: function (defcolor) {\r\n
            var me = this;\r\n
            var win = new Common.UI.ExtendedColorDialog({});\r\n
            win.on("onmodalresult", function (mr) {\r\n
                me._isdlgopen = false;\r\n
                if (mr == 1) {\r\n
                    me.setCustomColor(win.getColor());\r\n
                    me.fireEvent("select", me, win.getColor());\r\n
                }\r\n
            });\r\n
            me._isdlgopen = true;\r\n
            win.setColor((me.value !== undefined && me.value !== false) ? me.value : ((defcolor !== undefined) ? defcolor : "000000"));\r\n
            win.show();\r\n
        },\r\n
        isDialogOpen: function () {\r\n
            return this._isdlgopen == true;\r\n
        },\r\n
        select: function (color, suppressEvent) {\r\n
            var el = $(this.el);\r\n
            el.find("a." + this.selectedCls).removeClass(this.selectedCls);\r\n
            if (typeof(color) == "object") {\r\n
                var effectEl;\r\n
                if (color.effectId !== undefined) {\r\n
                    effectEl = el.find(\'a[effectid="\' + color.effectId + \'"]\').first();\r\n
                    if (effectEl.length > 0) {\r\n
                        effectEl.addClass(this.selectedCls);\r\n
                        this.value = effectEl[0].className.match(this.colorRe)[1].toUpperCase();\r\n
                    } else {\r\n
                        this.value = false;\r\n
                    }\r\n
                } else {\r\n
                    if (color.effectValue !== undefined) {\r\n
                        effectEl = el.find(\'a[effectvalue="\' + color.effectValue + \'"].color-\' + color.color.toUpperCase()).first();\r\n
                        if (effectEl.length > 0) {\r\n
                            effectEl.addClass(this.selectedCls);\r\n
                            this.value = effectEl[0].className.match(this.colorRe)[1].toUpperCase();\r\n
                        } else {\r\n
                            this.value = false;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            } else {\r\n
                if (/#?[a-fA-F0-9]{6}/.test(color)) {\r\n
                    color = /#?([a-fA-F0-9]{6})/.exec(color)[1].toUpperCase();\r\n
                    this.value = color;\r\n
                }\r\n
                if (/^[a-fA-F0-9]{6}|transparent$/.test(color) && _.indexOf(this.colors, color) >= 0) {\r\n
                    if (_.indexOf(this.colors, this.value) < 0) {\r\n
                        this.value = false;\r\n
                    }\r\n
                    if (color != this.value || this.options.allowReselect) {\r\n
                        (color == "transparent") ? el.find("a.color-transparent").addClass(this.selectedCls) : el.find("a.palette-color.color-" + color).first().addClass(this.selectedCls);\r\n
                        this.value = color;\r\n
                        if (suppressEvent !== true) {\r\n
                            this.fireEvent("select", this, color);\r\n
                        }\r\n
                    }\r\n
                } else {\r\n
                    var co = el.find("#" + color).first();\r\n
                    if (co.length == 0) {\r\n
                        co = el.find(\'a[color="\' + color + \'"]\').first();\r\n
                    }\r\n
                    if (co.length > 0) {\r\n
                        co.addClass(this.selectedCls);\r\n
                        this.value = color.toUpperCase();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        updateColors: function (effectcolors, standartcolors) {\r\n
            if (effectcolors === undefined || standartcolors === undefined) {\r\n
                return;\r\n
            }\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            if (me.aColorElements === undefined) {\r\n
                me.aColorElements = el.find("a.palette-color");\r\n
            }\r\n
            if (me.aEffectElements === undefined) {\r\n
                me.aEffectElements = el.find("a.palette-color-effect");\r\n
            }\r\n
            var aEl;\r\n
            var aColorIdx = 0,\r\n
            aEffectIdx = 0;\r\n
            for (var i = 0; i < me.colors.length; i++) {\r\n
                if (typeof(me.colors[i]) == "string" && (/[0-9A-F]{6}/).test(me.colors[i])) {\r\n
                    if (aColorIdx >= standartcolors.length) {\r\n
                        continue;\r\n
                    }\r\n
                    aEl = $(me.aColorElements[aColorIdx]);\r\n
                    aEl.removeClass("color-" + me.colors[i]);\r\n
                    me.colors[i] = standartcolors[aColorIdx].toUpperCase();\r\n
                    aEl.addClass("color-" + me.colors[i]);\r\n
                    aEl.css({\r\n
                        background: "#" + me.colors[i]\r\n
                    });\r\n
                    aEl.find("span").first().css({\r\n
                        background: "#" + me.colors[i]\r\n
                    });\r\n
                    aColorIdx++;\r\n
                } else {\r\n
                    if (typeof(me.colors[i]) == "object" && me.colors[i].effectId !== undefined) {\r\n
                        if (aEffectIdx >= effectcolors.length) {\r\n
                            continue;\r\n
                        }\r\n
                        aEl = $(me.aEffectElements[aEffectIdx]);\r\n
                        effectcolors[aEffectIdx].color = effectcolors[aEffectIdx].color.toUpperCase();\r\n
                        if (me.colors[i].color !== effectcolors[aEffectIdx].color) {\r\n
                            aEl.removeClass("color-" + me.colors[i].color);\r\n
                            aEl.addClass("color-" + effectcolors[aEffectIdx].color);\r\n
                            aEl.css({\r\n
                                background: "#" + effectcolors[aEffectIdx].color\r\n
                            });\r\n
                            aEl.find("span").first().css({\r\n
                                background: "#" + effectcolors[aEffectIdx].color\r\n
                            });\r\n
                        }\r\n
                        if (me.colors[i].effectId !== effectcolors[aEffectIdx].effectId) {\r\n
                            aEl.attr("effectid", "" + effectcolors[aEffectIdx].effectId);\r\n
                        }\r\n
                        if (me.colors[i].effectValue !== effectcolors[aEffectIdx].effectValue) {\r\n
                            aEl.attr("effectvalue", "" + effectcolors[aEffectIdx].effectValue);\r\n
                        }\r\n
                        me.colors[i] = effectcolors[aEffectIdx];\r\n
                        aEffectIdx++;\r\n
                    }\r\n
                }\r\n
            }\r\n
            this.options.updateColorsArr = undefined;\r\n
        },\r\n
        clearSelection: function (suppressEvent) {\r\n
            $(this.el).find("a." + this.selectedCls).removeClass(this.selectedCls);\r\n
            this.value = undefined;\r\n
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
            <value> <int>17980</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
