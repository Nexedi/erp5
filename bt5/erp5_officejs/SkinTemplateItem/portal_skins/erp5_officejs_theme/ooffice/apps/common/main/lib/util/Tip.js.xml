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
            <value> <string>ts44308804.32</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Tip.js</string> </value>
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
 (function ($) {\r\n
    var _superclass = $.fn.tooltip;\r\n
    _superclass.prototype = $.fn.tooltip.Constructor.prototype;\r\n
    $.extend($.fn.tooltip.Constructor.DEFAULTS, {\r\n
        container: "body",\r\n
        delay: {\r\n
            show: 500\r\n
        },\r\n
        arrow: false\r\n
    });\r\n
    var Tip = function (element, options) {\r\n
        this.init("tooltip", element, options);\r\n
    };\r\n
    Tip.prototype = $.extend({},\r\n
    $.fn.tooltip.Constructor.prototype, {\r\n
        constructor: Tip,\r\n
        init: function () {\r\n
            _superclass.prototype.init.apply(this, arguments);\r\n
            if (this.options.placement == "cursor") {\r\n
                if (/hover/.exec(this.options.trigger)) {\r\n
                    this.$element.on("mousemove.tooltip", this.options.selector, $.proxy(this.mousemove, this));\r\n
                }\r\n
            }\r\n
            if (this.options.zIndex) {\r\n
                this.tip().css("z-index", this.options.zIndex);\r\n
            }\r\n
            var me = this;\r\n
            Common.NotificationCenter.on({\r\n
                "layout:changed": function (e) {\r\n
                    if (!me.options.hideonclick && me.tip().is(":visible")) {\r\n
                        me.hide();\r\n
                    }\r\n
                }\r\n
            });\r\n
        },\r\n
        mousemove: function (e) {\r\n
            this.targetXY = [e.clientX, e.clientY];\r\n
        },\r\n
        leave: function (obj) {\r\n
            _superclass.prototype.leave.apply(this, arguments);\r\n
            this.dontShow = undefined;\r\n
        },\r\n
        show: function (at) {\r\n
            if (this.hasContent() && this.enabled && !this.dontShow) {\r\n
                if (!this.$element.is(":visible") && this.$element.closest("[role=menu]").length > 0) {\r\n
                    return;\r\n
                }\r\n
                var $tip = this.tip();\r\n
                var placement = typeof this.options.placement === "function" ? this.options.placement.call(this, $tip[0], this.$element[0]) : this.options.placement;\r\n
                if (this.options.arrow === false) {\r\n
                    $tip.addClass("arrow-free");\r\n
                }\r\n
                if (this.options.cls) {\r\n
                    $tip.addClass(this.options.cls);\r\n
                }\r\n
                var placementEx = /^([a-zA-Z]+)-?([a-zA-Z]*)$/.exec(placement);\r\n
                if (!at && !placementEx[2].length) {\r\n
                    _superclass.prototype.show.apply(this, arguments);\r\n
                } else {\r\n
                    var e = $.Event("show.bs.tooltip");\r\n
                    this.$element.trigger(e);\r\n
                    if (e.isDefaultPrevented()) {\r\n
                        return;\r\n
                    }\r\n
                    this.setContent();\r\n
                    if (this.options.animation) {\r\n
                        $tip.addClass("fade");\r\n
                    }\r\n
                    $tip.detach().css({\r\n
                        top: 0,\r\n
                        left: 0,\r\n
                        display: "block"\r\n
                    });\r\n
                    this.options.container ? $tip.appendTo(this.options.container) : $tip.insertAfter(this.$element);\r\n
                    if (typeof at == "object") {\r\n
                        var tp = {\r\n
                            top: at[1] + 15,\r\n
                            left: at[0] + 18\r\n
                        };\r\n
                        if (tp.left + $tip.width() > window.innerWidth) {\r\n
                            tp.left = window.innerWidth - $tip.width() - 30;\r\n
                        }\r\n
                        $tip.offset(tp).addClass("in");\r\n
                    } else {\r\n
                        var pos = this.getPosition();\r\n
                        var actualWidth = $tip[0].offsetWidth,\r\n
                        actualHeight = $tip[0].offsetHeight;\r\n
                        switch (placementEx[1]) {\r\n
                        case "bottom":\r\n
                            tp = {\r\n
                                top: pos.top + pos.height + 10\r\n
                            };\r\n
                            break;\r\n
                        case "top":\r\n
                            tp = {\r\n
                                top: pos.top - actualHeight - 10\r\n
                            };\r\n
                            break;\r\n
                        }\r\n
                        switch (placementEx[2]) {\r\n
                        case "left":\r\n
                            tp.left = pos.left;\r\n
                            if (this.$element.outerWidth() <= 18) {\r\n
                                tp.left -= 4;\r\n
                            }\r\n
                            break;\r\n
                        case "right":\r\n
                            tp.left = pos.left + pos.width - actualWidth;\r\n
                            if (this.$element.outerWidth() <= 18) {\r\n
                                tp.left += 4;\r\n
                            }\r\n
                            break;\r\n
                        }\r\n
                        this.applyPlacement(tp, placementEx[1]);\r\n
                        this.moveArrow();\r\n
                        $tip.addClass(placementEx[1]).addClass(placementEx[0]);\r\n
                    }\r\n
                    this.$element.trigger("shown.bs.tooltip");\r\n
                }\r\n
                var self = this;\r\n
                clearTimeout(self.timeout);\r\n
                self.timeout = setTimeout(function () {\r\n
                    if (self.hoverState == "in") {\r\n
                        self.hide();\r\n
                    }\r\n
                    self.dontShow = false;\r\n
                },\r\n
                5000);\r\n
            }\r\n
        },\r\n
        moveArrow: function () {\r\n
            var $arrow = this.tip().find(".tooltip-arrow, .arrow");\r\n
            var new_arrow_position = 10;\r\n
            switch (this.options.placement) {\r\n
            case "top-left":\r\n
                case "bottom-left":\r\n
                $arrow.css("left", new_arrow_position);\r\n
                break;\r\n
            case "top-right":\r\n
                case "bottom-right":\r\n
                $arrow.css("right", new_arrow_position);\r\n
                break;\r\n
            }\r\n
        },\r\n
        enter: function (obj) {\r\n
            if (obj.type !== "mouseenter") {\r\n
                return;\r\n
            }\r\n
            var $target = $(obj.target);\r\n
            if ($target.is("[role=menu]") || $target.parentsUntil(obj.currentTarget, "[role=menu]").length || this.tip().is(":visible")) {\r\n
                return;\r\n
            }\r\n
            var self = obj instanceof this.constructor ? obj : $(obj.currentTarget)[this.type](this.getDelegateOptions()).data("bs.tooltip");\r\n
            clearTimeout(self.timeout);\r\n
            self.hoverState = "in";\r\n
            if (!self.options.delay || !self.options.delay.show) {\r\n
                self.show();\r\n
            } else {\r\n
                self.timeout = setTimeout(function () {\r\n
                    if (self.hoverState == "in") {\r\n
                        self.show(self.options.placement == "cursor" ? self.targetXY : undefined);\r\n
                    }\r\n
                },\r\n
                self.options.delay.show);\r\n
            }\r\n
        },\r\n
        replaceArrow: function (delta, dimension, position) {\r\n
            this.options.arrow === false ? this.arrow().hide() : _superclass.prototype.replaceArrow.apply(this, arguments);\r\n
        },\r\n
        getCalculatedOffset: function (placement, pos, actualWidth, actualHeight) {\r\n
            var out = _superclass.prototype.getCalculatedOffset.apply(this, arguments);\r\n
            if (this.options.offset > 0 || this.options.offset < 0) {\r\n
                switch (/(bottom|top)/.exec(placement)[1]) {\r\n
                case "bottom":\r\n
                    out.top += this.options.offset;\r\n
                    break;\r\n
                case "top":\r\n
                    out.top -= this.options.offset;\r\n
                    break;\r\n
                }\r\n
            }\r\n
            return out;\r\n
        }\r\n
    });\r\n
    var old = $.fn.tooltip;\r\n
    $.fn.tooltip = function (option) {\r\n
        return this.each(function () {\r\n
            var $this = $(this),\r\n
            data = $this.data("bs.tooltip"),\r\n
            options = typeof option === "object" && option;\r\n
            if (!data) {\r\n
                $this.data("bs.tooltip", (data = new Tip(this, options)));\r\n
            }\r\n
            if (typeof option === "string") {\r\n
                data[option]();\r\n
            }\r\n
        });\r\n
    };\r\n
    $.fn.tooltip.Constructor = Tip;\r\n
    $.fn.tooltip.noConflict = function () {\r\n
        $.fn.tooltip = old;\r\n
        return this;\r\n
    };\r\n
})(window.jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10120</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
