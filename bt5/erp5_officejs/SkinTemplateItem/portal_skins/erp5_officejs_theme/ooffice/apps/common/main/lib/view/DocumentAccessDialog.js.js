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
            <value> <string>ts44321418.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DocumentAccessDialog.js</string> </value>
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
 define(["common/main/lib/component/Window", "common/main/lib/component/LoadMask"], function () {\r\n
    Common.Views.DocumentAccessDialog = Common.UI.Window.extend(_.extend({\r\n
        initialize: function (options) {\r\n
            var _options = {};\r\n
            _.extend(_options, {\r\n
                title: this.textTitle,\r\n
                width: 850,\r\n
                height: 534,\r\n
                header: true\r\n
            },\r\n
            options);\r\n
            this.template = [\'<div id="id-sharing-placeholder"></div>\'].join("");\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            this.settingsurl = options.settingsurl || "";\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.$window.find("> .body").css({\r\n
                height: "auto",\r\n
                overflow: "hidden"\r\n
            });\r\n
            var iframe = document.createElement("iframe");\r\n
            iframe.width = "100%";\r\n
            iframe.height = 500;\r\n
            iframe.align = "top";\r\n
            iframe.frameBorder = 0;\r\n
            iframe.scrolling = "no";\r\n
            iframe.onload = _.bind(this._onLoad, this);\r\n
            $("#id-sharing-placeholder").append(iframe);\r\n
            this.loadMask = new Common.UI.LoadMask({\r\n
                owner: $("#id-sharing-placeholder")\r\n
            });\r\n
            this.loadMask.setTitle(this.textLoading);\r\n
            this.loadMask.show();\r\n
            iframe.src = this.settingsurl;\r\n
            this._bindWindowEvents.call(this);\r\n
        },\r\n
        _bindWindowEvents: function () {\r\n
            var me = this;\r\n
            if (window.addEventListener) {\r\n
                window.addEventListener("message", function (msg) {\r\n
                    me._onWindowMessage(msg);\r\n
                },\r\n
                false);\r\n
            } else {\r\n
                if (window.attachEvent) {\r\n
                    window.attachEvent("onmessage", function (msg) {\r\n
                        me._onWindowMessage(msg);\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        _onWindowMessage: function (msg) {\r\n
            if (msg && window.JSON) {\r\n
                try {\r\n
                    this._onMessage.call(this, window.JSON.parse(msg.data));\r\n
                } catch(e) {}\r\n
            }\r\n
        },\r\n
        _onMessage: function (msg) {\r\n
            if (msg && msg.needUpdate) {\r\n
                this.trigger("accessrights", this, msg.sharingSettings);\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        _onLoad: function () {\r\n
            if (this.loadMask) {\r\n
                this.loadMask.hide();\r\n
            }\r\n
        },\r\n
        textTitle: "Sharing Settings",\r\n
        textLoading: "Loading"\r\n
    },\r\n
    Common.Views.DocumentAccessDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4459</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
