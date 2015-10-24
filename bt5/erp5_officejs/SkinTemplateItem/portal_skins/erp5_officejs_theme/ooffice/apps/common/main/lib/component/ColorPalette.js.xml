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
            <value> <string>ts44308798.67</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ColorPalette.js</string> </value>
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
    Common.UI.ColorPalette = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            allowReselect: true,\r\n
            cls: "",\r\n
            style: ""\r\n
        },\r\n
        template: _.template([\'<div class="palette-color">\', "<% _.each(colors, function(color, index) { %>", \'<span class="color-item" data-color="<%= color %>" style="background-color: #<%= color %>;"></span>\', "<% }) %>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this;\r\n
            this.id = me.options.id;\r\n
            this.cls = me.options.cls;\r\n
            this.style = me.options.style;\r\n
            this.colors = me.options.colors || [];\r\n
            this.value = me.options.value;\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            if (!me.rendered) {\r\n
                this.cmpEl = $(this.template({\r\n
                    id: this.id,\r\n
                    cls: this.cls,\r\n
                    style: this.style,\r\n
                    colors: this.colors\r\n
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
            if (!me.rendered) {\r\n
                var el = this.cmpEl;\r\n
                el.on("click", "span.color-item", _.bind(this.itemClick, this));\r\n
            }\r\n
            me.rendered = true;\r\n
            return this;\r\n
        },\r\n
        itemClick: function (e) {\r\n
            var item = $(e.target);\r\n
            this.select(item.attr("data-color"));\r\n
        },\r\n
        select: function (color, suppressEvent) {\r\n
            if (this.value != color) {\r\n
                var me = this;\r\n
                $("span.color-item", this.cmpEl).removeClass("selected");\r\n
                this.value = color;\r\n
                if (color && /#?[a-fA-F0-9]{6}/.test(color)) {\r\n
                    color = /#?([a-fA-F0-9]{6})/.exec(color)[1].toUpperCase();\r\n
                    $("span[data-color=" + color + "]", this.cmpEl).addClass("selected");\r\n
                    if (!suppressEvent) {\r\n
                        me.trigger("select", me, this.value);\r\n
                    }\r\n
                }\r\n
            }\r\n
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
            <value> <int>4221</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
