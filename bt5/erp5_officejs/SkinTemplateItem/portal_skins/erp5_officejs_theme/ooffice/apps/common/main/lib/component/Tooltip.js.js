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
            <value> <string>ts44308801.26</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Tooltip.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>﻿/*\r\n
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
 define(["tip", "backbone"], function () {\r\n
    var Tooltip = function (options) {\r\n
        this.$element = this.placement = undefined;\r\n
        this.init.call(this, options);\r\n
    };\r\n
    _.extend(Tooltip.prototype, Backbone.Events, {\r\n
        init: function (opts) {\r\n
            this.$element = opts.owner instanceof Backbone.View ? opts.owner.$el : $(opts.owner);\r\n
            this.placement = opts.placement;\r\n
            if (this.$element.data("bs.tooltip")) {\r\n
                this.$element.removeData("bs.tooltip");\r\n
            }\r\n
            this.$element.tooltip({\r\n
                title: opts.title,\r\n
                trigger: "manual",\r\n
                placement: opts.placement,\r\n
                offset: opts.offset,\r\n
                cls: opts.cls,\r\n
                html: opts.html,\r\n
                hideonclick: opts.hideonclick\r\n
            });\r\n
            if (opts.hideonclick) {\r\n
                var tip = this.$element.data("bs.tooltip");\r\n
                tip.tip().on("click", function () {\r\n
                    tip.hide();\r\n
                });\r\n
            }\r\n
            this.$element.on("shown.bs.tooltip", _.bind(this.onTipShown, this));\r\n
            this.$element.on("hidden.bs.tooltip", _.bind(this.onTipHidden, this));\r\n
        },\r\n
        show: function (at) {\r\n
            this.getBSTip().show(at);\r\n
        },\r\n
        hide: function () {\r\n
            this.getBSTip().hide();\r\n
        },\r\n
        setTitle: function (title) {\r\n
            var tip = this.getBSTip();\r\n
            tip.options.title = title;\r\n
        },\r\n
        updateTitle: function () {\r\n
            var tip = this.getBSTip();\r\n
            tip.$tip.find(".tooltip-inner")[tip.options.html ? "html" : "text"](tip.options.title);\r\n
        },\r\n
        getBSTip: function () {\r\n
            return this.$element.data("bs.tooltip");\r\n
        },\r\n
        onTipShown: function () {\r\n
            this.trigger("tooltip:show", this);\r\n
        },\r\n
        onTipHidden: function () {\r\n
            this.trigger("tooltip:hide", this);\r\n
        },\r\n
        isVisible: function () {\r\n
            return this.getBSTip().tip().is(":visible");\r\n
        }\r\n
    });\r\n
    Common.UI = Common.UI || {};\r\n
    Common.UI.Tooltip = Tooltip;\r\n
});</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3787</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
