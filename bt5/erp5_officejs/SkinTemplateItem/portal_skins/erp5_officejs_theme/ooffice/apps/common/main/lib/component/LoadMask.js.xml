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
            <value> <string>ts44308799.69</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>LoadMask.js</string> </value>
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
    Common.UI.LoadMask = Common.UI.BaseView.extend((function () {\r\n
        var ownerEl, maskeEl, loaderEl;\r\n
        return {\r\n
            options: {\r\n
                cls: "",\r\n
                style: "",\r\n
                title: "Loading...",\r\n
                owner: document.body\r\n
            },\r\n
            template: _.template([\'<div id="<%= id %>" class="asc-loadmask-body <%= cls %>" role="presentation" tabindex="-1">\', \'<div class="asc-loadmask-image"></div>\', \'<div class="asc-loadmask-title"><%= title %></div>\', "</div>"].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                this.template = this.options.template || this.template;\r\n
                this.cls = this.options.cls;\r\n
                this.style = this.options.style;\r\n
                this.title = this.options.title;\r\n
                this.owner = this.options.owner;\r\n
            },\r\n
            render: function () {\r\n
                return this;\r\n
            },\r\n
            show: function () {\r\n
                if (maskeEl || loaderEl) {\r\n
                    return;\r\n
                }\r\n
                ownerEl = (this.owner instanceof Common.UI.BaseView) ? $(this.owner.el) : $(this.owner);\r\n
                if (ownerEl.hasClass("masked")) {\r\n
                    return this;\r\n
                }\r\n
                var me = this;\r\n
                maskeEl = $(\'<div class="asc-loadmask"></div>\');\r\n
                loaderEl = $(this.template({\r\n
                    id: me.id,\r\n
                    cls: me.cls,\r\n
                    style: me.style,\r\n
                    title: me.title\r\n
                }));\r\n
                ownerEl.addClass("masked");\r\n
                ownerEl.append(maskeEl);\r\n
                ownerEl.append(loaderEl);\r\n
                loaderEl.css({\r\n
                    top: Math.round(ownerEl.height() / 2 - (loaderEl.height() + parseInt(loaderEl.css("padding-top")) + parseInt(loaderEl.css("padding-bottom"))) / 2) + "px",\r\n
                    left: Math.round(ownerEl.width() / 2 - (loaderEl.width() + parseInt(loaderEl.css("padding-left")) + parseInt(loaderEl.css("padding-right"))) / 2) + "px"\r\n
                });\r\n
                Common.util.Shortcuts.suspendEvents();\r\n
                return this;\r\n
            },\r\n
            hide: function () {\r\n
                ownerEl && ownerEl.removeClass("masked");\r\n
                maskeEl && maskeEl.remove();\r\n
                loaderEl && loaderEl.remove();\r\n
                maskeEl = null;\r\n
                loaderEl = null;\r\n
                Common.util.Shortcuts.resumeEvents();\r\n
            },\r\n
            setTitle: function (title) {\r\n
                this.title = title;\r\n
                if (ownerEl && ownerEl.hasClass("masked") && loaderEl) {\r\n
                    $(".asc-loadmask-title", loaderEl).html(title);\r\n
                }\r\n
            }\r\n
        };\r\n
    })());\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4608</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
