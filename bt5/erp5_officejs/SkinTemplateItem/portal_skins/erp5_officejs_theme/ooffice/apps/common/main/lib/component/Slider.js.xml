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
            <value> <string>ts44308800.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Slider.js</string> </value>
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
define(["common/main/lib/component/BaseView", "underscore"], function (base, _) {\r\n
    Common.UI.SingleSlider = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            width: 100,\r\n
            minValue: 0,\r\n
            maxValue: 100,\r\n
            step: 1,\r\n
            value: 100,\r\n
            enableKeyEvents: false\r\n
        },\r\n
        disabled: false,\r\n
        template: _.template([\'<div class="slider single-slider" style="">\', \'<div class="track">\', \'<div class="track-left"></div>\', \'<div class="track-center""></div>\', \'<div class="track-right" style=""></div>\', "</div>", \'<div class="thumb" style=""></div>\', "<% if (this.options.enableKeyEvents) { %>", \'<input type="text" style="position: absolute; top:-10px; width: 1px; height: 1px;">\', "<% } %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            me.width = me.options.width;\r\n
            me.minValue = me.options.minValue;\r\n
            me.maxValue = me.options.maxValue;\r\n
            me.delta = 100 / (me.maxValue - me.minValue);\r\n
            me.step = me.options.step;\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
            this.setValue(me.options.value);\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            if (!me.rendered) {\r\n
                this.cmpEl = $(this.template({}));\r\n
                if (parentEl) {\r\n
                    this.setElement(parentEl, false);\r\n
                    parentEl.html(this.cmpEl);\r\n
                } else {\r\n
                    $(this.el).html(this.cmpEl);\r\n
                }\r\n
            } else {\r\n
                this.cmpEl = $(this.el);\r\n
            }\r\n
            this.cmpEl.find(".track-center").width(me.options.width - 14);\r\n
            this.cmpEl.width(me.options.width);\r\n
            this.thumb = this.cmpEl.find(".thumb");\r\n
            var onMouseUp = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                var pos = Math.max(0, Math.min(100, (Math.round((e.pageX - me.cmpEl.offset().left - me._dragstart) / me.width * 100))));\r\n
                me.setThumbPosition(pos);\r\n
                me.lastValue = me.value;\r\n
                me.value = pos / me.delta + me.minValue;\r\n
                me.thumb.removeClass("active");\r\n
                $(document).off("mouseup", onMouseUp);\r\n
                $(document).off("mousemove", onMouseMove);\r\n
                me._dragstart = undefined;\r\n
                me.trigger("changecomplete", me, me.value, me.lastValue);\r\n
            };\r\n
            var onMouseMove = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                if (me._dragstart === undefined) {\r\n
                    return;\r\n
                }\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                var pos = Math.max(0, Math.min(100, (Math.round((e.pageX - me.cmpEl.offset().left - me._dragstart) / me.width * 100))));\r\n
                me.setThumbPosition(pos);\r\n
                me.lastValue = me.value;\r\n
                me.value = pos / me.delta + me.minValue;\r\n
                if (Math.abs(me.value - me.lastValue) > 0.001) {\r\n
                    me.trigger("change", me, me.value, me.lastValue);\r\n
                }\r\n
            };\r\n
            var onMouseDown = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                me._dragstart = e.pageX - me.thumb.offset().left - 7;\r\n
                me.thumb.addClass("active");\r\n
                $(document).on("mouseup", onMouseUp);\r\n
                $(document).on("mousemove", onMouseMove);\r\n
                if (me.options.enableKeyEvents) {\r\n
                    setTimeout(function () {\r\n
                        me.input.focus();\r\n
                    },\r\n
                    10);\r\n
                }\r\n
            };\r\n
            var onTrackMouseDown = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                var pos = Math.max(0, Math.min(100, (Math.round((e.pageX - me.cmpEl.offset().left) / me.width * 100))));\r\n
                me.setThumbPosition(pos);\r\n
                me.lastValue = me.value;\r\n
                me.value = pos / me.delta + me.minValue;\r\n
                me.trigger("change", me, me.value, me.lastValue);\r\n
                me.trigger("changecomplete", me, me.value, me.lastValue);\r\n
            };\r\n
            var updateslider;\r\n
            var moveThumb = function (increase) {\r\n
                me.lastValue = me.value;\r\n
                me.value = Math.max(me.minValue, Math.min(me.maxValue, me.value + ((increase) ? me.step : -me.step)));\r\n
                me.setThumbPosition(Math.round((me.value - me.minValue) * me.delta));\r\n
                me.trigger("change", me, me.value, me.lastValue);\r\n
            };\r\n
            var onKeyDown = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN || e.keyCode == Common.UI.Keys.LEFT || e.keyCode == Common.UI.Keys.RIGHT) {\r\n
                    e.preventDefault();\r\n
                    e.stopPropagation();\r\n
                    el.off("keydown", "input", onKeyDown);\r\n
                    updateslider = setInterval(_.bind(moveThumb, me, e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.RIGHT), 100);\r\n
                }\r\n
            };\r\n
            var onKeyUp = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN || Common.UI.Keys.LEFT || Common.UI.Keys.RIGHT) {\r\n
                    e.stopPropagation();\r\n
                    e.preventDefault();\r\n
                    clearInterval(updateslider);\r\n
                    moveThumb(e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.RIGHT);\r\n
                    el.on("keydown", "input", onKeyDown);\r\n
                    me.trigger("changecomplete", me, me.value, me.lastValue);\r\n
                }\r\n
            };\r\n
            if (!me.rendered) {\r\n
                var el = me.cmpEl;\r\n
                el.on("mousedown", ".thumb", onMouseDown);\r\n
                el.on("mousedown", ".track", onTrackMouseDown);\r\n
                if (this.options.enableKeyEvents) {\r\n
                    el.on("keydown", "input", onKeyDown);\r\n
                    el.on("keyup", "input", onKeyUp);\r\n
                }\r\n
            }\r\n
            me.rendered = true;\r\n
            return this;\r\n
        },\r\n
        setThumbPosition: function (x) {\r\n
            this.thumb.css({\r\n
                left: x + "%"\r\n
            });\r\n
        },\r\n
        setValue: function (value) {\r\n
            this.lastValue = this.value;\r\n
            this.value = Math.max(this.minValue, Math.min(this.maxValue, value));\r\n
            this.setThumbPosition(Math.round((value - this.minValue) * this.delta));\r\n
        },\r\n
        getValue: function () {\r\n
            return this.value;\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            if (disabled !== this.disabled) {\r\n
                this.cmpEl.toggleClass("disabled", disabled);\r\n
            }\r\n
            this.disabled = disabled;\r\n
        }\r\n
    });\r\n
    Common.UI.MultiSlider = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            width: 100,\r\n
            minValue: 0,\r\n
            maxValue: 100,\r\n
            values: [0, 100]\r\n
        },\r\n
        disabled: false,\r\n
        template: _.template([\'<div class="slider multi-slider">\', \'<div class="track">\', \'<div class="track-left"></div>\', \'<div class="track-center""></div>\', \'<div class="track-right" style=""></div>\', "</div>", "<% _.each(items, function(item) { %>", \'<div class="thumb" style=""></div>\', "<% }); %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            el = $(this.el);\r\n
            me.width = me.options.width;\r\n
            me.minValue = me.options.minValue;\r\n
            me.maxValue = me.options.maxValue;\r\n
            me.delta = 100 / (me.maxValue - me.minValue);\r\n
            me.thumbs = [];\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            if (!me.rendered) {\r\n
                this.cmpEl = $(this.template({\r\n
                    items: this.options.values\r\n
                }));\r\n
                if (parentEl) {\r\n
                    this.setElement(parentEl, false);\r\n
                    parentEl.html(this.cmpEl);\r\n
                } else {\r\n
                    $(this.el).html(this.cmpEl);\r\n
                }\r\n
            } else {\r\n
                this.cmpEl = $(this.el);\r\n
            }\r\n
            var el = this.cmpEl;\r\n
            el.find(".track-center").width(me.options.width - 14);\r\n
            el.width(me.options.width);\r\n
            var onMouseUp = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                var index = e.data,\r\n
                lastValue = me.thumbs[index].value,\r\n
                minValue = (index - 1 < 0) ? 0 : me.thumbs[index - 1].position,\r\n
                maxValue = (index + 1 < me.thumbs.length) ? me.thumbs[index + 1].position : 100,\r\n
                pos = Math.max(minValue, Math.min(maxValue, (Math.round((e.pageX - me.cmpEl.offset().left - me._dragstart) / me.width * 100)))),\r\n
                value = pos / me.delta + me.minValue;\r\n
                me.setThumbPosition(index, pos);\r\n
                me.thumbs[index].value = value;\r\n
                $(document).off("mouseup", onMouseUp);\r\n
                $(document).off("mousemove", onMouseMove);\r\n
                me._dragstart = undefined;\r\n
                me.trigger("changecomplete", me, value, lastValue);\r\n
            };\r\n
            var onMouseMove = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                if (me._dragstart === undefined) {\r\n
                    return;\r\n
                }\r\n
                e.preventDefault();\r\n
                e.stopPropagation();\r\n
                var index = e.data,\r\n
                lastValue = me.thumbs[index].value,\r\n
                minValue = (index - 1 < 0) ? 0 : me.thumbs[index - 1].position,\r\n
                maxValue = (index + 1 < me.thumbs.length) ? me.thumbs[index + 1].position : 100,\r\n
                pos = Math.max(minValue, Math.min(maxValue, (Math.round((e.pageX - me.cmpEl.offset().left - me._dragstart) / me.width * 100)))),\r\n
                value = pos / me.delta + me.minValue;\r\n
                me.setThumbPosition(index, pos);\r\n
                me.thumbs[index].value = value;\r\n
                if (Math.abs(value - lastValue) > 0.001) {\r\n
                    me.trigger("change", me, value, lastValue);\r\n
                }\r\n
            };\r\n
            var onMouseDown = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                var index = e.data,\r\n
                thumb = me.thumbs[index].thumb;\r\n
                me._dragstart = e.pageX - thumb.offset().left - thumb.width() / 2;\r\n
                me.setActiveThumb(index);\r\n
                _.each(me.thumbs, function (item, idx) {\r\n
                    (index == idx) ? item.thumb.css("z-index", 500) : item.thumb.css("z-index", "");\r\n
                });\r\n
                $(document).on("mouseup", null, index, onMouseUp);\r\n
                $(document).on("mousemove", null, index, onMouseMove);\r\n
            };\r\n
            var onTrackMouseDown = function (e) {\r\n
                if (me.disabled) {\r\n
                    return;\r\n
                }\r\n
                var pos = Math.max(0, Math.min(100, (Math.round((e.pageX - me.cmpEl.offset().left) / me.width * 100)))),\r\n
                index = findThumb(pos),\r\n
                lastValue = me.thumbs[index].value,\r\n
                value = pos / me.delta + me.minValue;\r\n
                me.setThumbPosition(index, pos);\r\n
                me.thumbs[index].value = value;\r\n
                me.trigger("change", me, value, lastValue);\r\n
                me.trigger("changecomplete", me, value, lastValue);\r\n
            };\r\n
            var findThumb = function (pos) {\r\n
                var nearest = 100,\r\n
                index = 0,\r\n
                len = me.thumbs.length,\r\n
                dist;\r\n
                for (var i = 0; i < len; i++) {\r\n
                    dist = Math.abs(me.thumbs[i].position - pos);\r\n
                    if (Math.abs(dist <= nearest)) {\r\n
                        var above = me.thumbs[i + 1];\r\n
                        var below = me.thumbs[i - 1];\r\n
                        if (below !== undefined && pos < below.position) {\r\n
                            continue;\r\n
                        }\r\n
                        if (above !== undefined && pos > above.position) {\r\n
                            continue;\r\n
                        }\r\n
                        index = i;\r\n
                        nearest = dist;\r\n
                    }\r\n
                }\r\n
                return index;\r\n
            };\r\n
            this.$thumbs = el.find(".thumb");\r\n
            _.each(this.$thumbs, function (item, index) {\r\n
                var thumb = $(item);\r\n
                me.thumbs.push({\r\n
                    thumb: thumb,\r\n
                    index: index\r\n
                });\r\n
                me.setValue(index, me.options.values[index]);\r\n
                thumb.on("mousedown", null, index, onMouseDown);\r\n
            });\r\n
            me.setActiveThumb(0, true);\r\n
            if (!me.rendered) {\r\n
                el.on("mousedown", ".track", onTrackMouseDown);\r\n
            }\r\n
            me.rendered = true;\r\n
            return this;\r\n
        },\r\n
        setActiveThumb: function (index, suspend) {\r\n
            this.currentThumb = index;\r\n
            this.$thumbs.removeClass("active");\r\n
            this.thumbs[index].thumb.addClass("active");\r\n
            if (suspend !== true) {\r\n
                this.trigger("thumbclick", this, index);\r\n
            }\r\n
        },\r\n
        setThumbPosition: function (index, x) {\r\n
            this.thumbs[index].position = x;\r\n
            this.thumbs[index].thumb.css({\r\n
                left: x + "%"\r\n
            });\r\n
        },\r\n
        setValue: function (index, value) {\r\n
            this.thumbs[index].value = Math.max(this.minValue, Math.min(this.maxValue, value));\r\n
            this.setThumbPosition(index, Math.round((value - this.minValue) * this.delta));\r\n
        },\r\n
        getValue: function (index) {\r\n
            return this.thumbs[index].value;\r\n
        },\r\n
        getValues: function () {\r\n
            var values = [];\r\n
            _.each(this.thumbs, function (thumb) {\r\n
                values.push(thumb.value);\r\n
            });\r\n
            return values;\r\n
        },\r\n
        setDisabled: function (disabled) {\r\n
            if (disabled !== this.disabled) {\r\n
                this.cmpEl.toggleClass("disabled", disabled);\r\n
            }\r\n
            this.disabled = disabled;\r\n
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
            <value> <int>17107</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
