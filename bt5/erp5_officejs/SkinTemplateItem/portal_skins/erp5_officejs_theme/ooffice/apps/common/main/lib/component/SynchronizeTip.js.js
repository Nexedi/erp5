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
            <value> <string>ts44308800.66</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>SynchronizeTip.js</string> </value>
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
    Common.UI.SynchronizeTip = Common.UI.BaseView.extend(_.extend((function () {\r\n
        var tipEl;\r\n
        return {\r\n
            options: {\r\n
                target: $(document.body)\r\n
            },\r\n
            template: _.template([\'<div class="synch-tip-root">\', \'<div class="asc-synchronizetip">\', \'<div class="tip-arrow"></div>\', "<div>", \'<div style="width: 260px;"><%= scope.textSynchronize %></div>\', \'<div class="close"></div>\', "</div>", \'<div class="show-link"><label><%= scope.textDontShow %></label></div>\', "</div>", "</div>"].join("")),\r\n
            initialize: function (options) {\r\n
                this.textSynchronize += Common.Utils.String.platformKey("Ctrl+S");\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                this.target = this.options.target;\r\n
            },\r\n
            render: function () {\r\n
                tipEl = $(this.template({\r\n
                    scope: this\r\n
                }));\r\n
                tipEl.find(".close").on("click", _.bind(function () {\r\n
                    this.trigger("closeclick");\r\n
                },\r\n
                this));\r\n
                tipEl.find(".show-link label").on("click", _.bind(function () {\r\n
                    this.trigger("dontshowclick");\r\n
                },\r\n
                this));\r\n
                $(document.body).append(tipEl);\r\n
                this.applyPlacement();\r\n
                return this;\r\n
            },\r\n
            show: function () {\r\n
                if (tipEl) {\r\n
                    this.applyPlacement();\r\n
                    tipEl.show();\r\n
                } else {\r\n
                    this.render();\r\n
                }\r\n
            },\r\n
            hide: function () {\r\n
                if (tipEl) {\r\n
                    tipEl.hide();\r\n
                }\r\n
            },\r\n
            applyPlacement: function () {\r\n
                var showxy = this.target.offset();\r\n
                tipEl.css({\r\n
                    top: showxy.top + this.target.height() / 2 + "px",\r\n
                    left: showxy.left + this.target.width() + "px"\r\n
                });\r\n
            },\r\n
            textDontShow: "Don\'t show this message again",\r\n
            textSynchronize: "The document has been changed by another user.<br/>Please click to save your changes and reload the updates."\r\n
        };\r\n
    })(), Common.UI.SynchronizeTip || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4067</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
