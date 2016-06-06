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
            <value> <string>ts44308800.25</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>MultiSliderGradient.js</string> </value>
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
define(["common/main/lib/component/Slider", "underscore"], function (base, _) {\r\n
    Common.UI.MultiSliderGradient = Common.UI.MultiSlider.extend({\r\n
        options: {\r\n
            width: 100,\r\n
            minValue: 0,\r\n
            maxValue: 100,\r\n
            values: [0, 100],\r\n
            colorValues: ["#000000", "#ffffff"],\r\n
            currentThumb: 0\r\n
        },\r\n
        disabled: false,\r\n
        template: _.template([\'<div class="slider multi-slider-gradient">\', \'<div class="track"></div>\', "<% _.each(items, function(item) { %>", \'<div class="thumb" style=""></div>\', "<% }); %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            this.styleStr = "";\r\n
            if (Common.Utils.isChrome && Common.Utils.chromeVersion < 10 || Common.Utils.isSafari && Common.Utils.safariVersion < 5.1) {\r\n
                this.styleStr = "-webkit-gradient(linear, left top, right top, color-stop({1}%,{0}), color-stop({3}%,{2})); /* Chrome,Safari4+ */";\r\n
            } else {\r\n
                if (Common.Utils.isChrome || Common.Utils.isSafari) {\r\n
                    this.styleStr = "-webkit-linear-gradient(left, {0} {1}%, {2} {3}%)";\r\n
                } else {\r\n
                    if (Common.Utils.isGecko) {\r\n
                        this.styleStr = "-moz-linear-gradient(left, {0} {1}%, {2} {3}%)";\r\n
                    } else {\r\n
                        if (Common.Utils.isOpera && Common.Utils.operaVersion > 11) {\r\n
                            this.styleStr = "-o-linear-gradient(left, {0} {1}%, {2} {3}%)";\r\n
                        } else {\r\n
                            if (Common.Utils.isIE) {\r\n
                                this.styleStr = "-ms-linear-gradient(left, {0} {1}%, {2} {3}%)";\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            this.colorValues = this.options.colorValues;\r\n
            Common.UI.MultiSlider.prototype.initialize.call(this, options);\r\n
        },\r\n
        render: function (parentEl) {\r\n
            Common.UI.MultiSlider.prototype.render.call(this, parentEl);\r\n
            var me = this,\r\n
            style = "";\r\n
            me.trackEl = me.cmpEl.find(".track");\r\n
            for (var i = 0; i < me.thumbs.length; i++) {\r\n
                me.thumbs[i].thumb.on("dblclick", null, function () {\r\n
                    me.trigger("thumbdblclick", me);\r\n
                });\r\n
            }\r\n
            if (me.styleStr !== "") {\r\n
                style = Common.Utils.String.format(me.styleStr, me.colorValues[0], 0, me.colorValues[1], 100);\r\n
                me.trackEl.css("background", style);\r\n
            }\r\n
            if (Common.Utils.isIE) {\r\n
                style = Common.Utils.String.format("progid:DXImageTransform.Microsoft.gradient( startColorstr={0}, endColorstr={1},GradientType=1 )", me.colorValues[0], me.colorValues[1]);\r\n
                me.trackEl.css("filter", style);\r\n
            }\r\n
            style = Common.Utils.String.format("linear-gradient(to right, {0} {1}%, {2} {3}%)", me.colorValues[0], 0, me.colorValues[1], 100);\r\n
            me.trackEl.css("background", style);\r\n
            me.on("change", _.bind(me.changeGradientStyle, me));\r\n
        },\r\n
        setColorValue: function (color, index) {\r\n
            var ind = (index !== undefined) ? index : this.currentThumb;\r\n
            this.colorValues[ind] = color;\r\n
            this.changeGradientStyle();\r\n
        },\r\n
        getColorValue: function (index) {\r\n
            var ind = (index !== undefined) ? index : this.currentThumb;\r\n
            return this.colorValues[ind];\r\n
        },\r\n
        setValue: function (index, value) {\r\n
            Common.UI.MultiSlider.prototype.setValue.call(this, index, value);\r\n
            this.changeGradientStyle();\r\n
        },\r\n
        changeGradientStyle: function () {\r\n
            if (!this.rendered) {\r\n
                return;\r\n
            }\r\n
            var style;\r\n
            if (this.styleStr !== "") {\r\n
                style = Common.Utils.String.format(this.styleStr, this.colorValues[0], this.getValue(0), this.colorValues[1], this.getValue(1));\r\n
                this.trackEl.css("background", style);\r\n
            }\r\n
            if (Common.Utils.isIE) {\r\n
                style = Common.Utils.String.format("progid:DXImageTransform.Microsoft.gradient( startColorstr={0}, endColorstr={1},GradientType=1 )", this.colorValues[0], this.colorValues[1]);\r\n
                this.trackEl.css("filter", style);\r\n
            }\r\n
            style = Common.Utils.String.format("linear-gradient(to right, {0} {1}%, {2} {3}%)", this.colorValues[0], this.getValue(0), this.colorValues[1], this.getValue(1));\r\n
            this.trackEl.css("background", style);\r\n
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
            <value> <int>6355</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
