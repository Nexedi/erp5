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
            <value> <string>ts44308800.76</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Tab.js</string> </value>
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
define(["common/main/lib/component/BaseView"], function (base) {\r\n
    var Tab = function (opts) {\r\n
        this.active = false;\r\n
        this.label = "Tab";\r\n
        this.cls = "";\r\n
        this.template = _.template([\'<li class="<% if(active){ %>active<% } %> <% if(cls.length){%><%= cls %><%}%>" data-label="<%= label %>">\', "<a><%- label %></a>", "</li>"].join(""));\r\n
        this.initialize.call(this, opts);\r\n
        return this;\r\n
    };\r\n
    _.extend(Tab.prototype, {\r\n
        initialize: function (options) {\r\n
            _.extend(this, options);\r\n
        },\r\n
        render: function () {\r\n
            var el = this.template(this);\r\n
            this.$el = $(el);\r\n
            this.rendered = true;\r\n
            this.disable(this.disabled);\r\n
            return this;\r\n
        },\r\n
        isActive: function () {\r\n
            return this.$el.hasClass("active");\r\n
        },\r\n
        activate: function () {\r\n
            if (!this.$el.hasClass("active")) {\r\n
                this.$el.addClass("active");\r\n
            }\r\n
        },\r\n
        deactivate: function () {\r\n
            this.$el.removeClass("active");\r\n
        },\r\n
        on: function () {\r\n
            this.$el.on.apply(this, arguments);\r\n
        },\r\n
        disable: function (val) {\r\n
            this.disabled = val;\r\n
            if (this.rendered) {\r\n
                if (val && !this.$el.hasClass("disabled")) {\r\n
                    this.$el.addClass("disabled");\r\n
                } else {\r\n
                    this.$el.removeClass("disabled");\r\n
                }\r\n
            }\r\n
        },\r\n
        addClass: function (cls) {\r\n
            if (cls.length && !this.$el.hasClass(cls)) {\r\n
                this.$el.addClass(cls);\r\n
            }\r\n
        },\r\n
        removeClass: function (cls) {\r\n
            if (cls.length && this.$el.hasClass(cls)) {\r\n
                this.$el.removeClass(cls);\r\n
            }\r\n
        },\r\n
        hasClass: function (cls) {\r\n
            return this.$el.hasClass(cls);\r\n
        },\r\n
        setCaption: function (text) {\r\n
            this.$el.find("> a").text(text);\r\n
        }\r\n
    });\r\n
    Common.UI.Tab = Tab;\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3744</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
