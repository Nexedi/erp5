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
            <value> <string>ts44321418.42</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>CopyWarningDialog.js</string> </value>
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
define(["common/main/lib/component/Window"], function () {\r\n
    Common.Views.CopyWarningDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 500,\r\n
            height: 325,\r\n
            cls: "modal-dlg copy-warning"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle\r\n
            },\r\n
            options || {});\r\n
            this.template = [\'<div class="box">\', \'<p class="message">\' + this.textMsg + "</p>", \'<div class="hotkeys">\', "<div>", \'<p class="hotkey">\' + Common.Utils.String.platformKey("Ctrl+C", "{0}") + "</p>", \'<p class="message">\' + this.textToCopy + "</p>", "</div>", "<div>", \'<p class="hotkey">\' + Common.Utils.String.platformKey("Ctrl+X", "{0}") + "</p>", \'<p class="message">\' + this.textToCut + "</p>", "</div>", "<div>", \'<p class="hotkey">\' + Common.Utils.String.platformKey("Ctrl+V", "{0}") + "</p>", \'<p class="message">\' + this.textToPaste + "</p>", "</div>", "</div>", \'<div id="copy-warning-checkbox" style="margin-top: 20px; text-align: left;"></div>\', "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary">\' + this.okButtonText + "</button>", "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.chDontShow = new Common.UI.CheckBox({\r\n
                el: $("#copy-warning-checkbox"),\r\n
                labelText: this.textDontShow\r\n
            });\r\n
            this.getChild().find(".btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.autoSize();\r\n
            Common.NotificationCenter.trigger("copywarning:show");\r\n
        },\r\n
        autoSize: function () {\r\n
            var text_cnt = this.getChild(".box"),\r\n
            footer = this.getChild(".footer"),\r\n
            header = this.getChild(".header"),\r\n
            body = this.getChild(".body");\r\n
            body.height(parseInt(text_cnt.height()) + parseInt(footer.css("height")));\r\n
            this.setHeight(parseInt(body.css("height")) + parseInt(header.css("height")));\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, this.chDontShow.getValue() == "checked");\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onKeyPress: function (event) {\r\n
            if (event.keyCode == Common.UI.Keys.RETURN) {\r\n
                if (this.options.handler) {\r\n
                    this.options.handler.call(this, this.chDontShow.getValue() == "checked");\r\n
                }\r\n
                this.close();\r\n
            }\r\n
        },\r\n
        getSettings: function () {\r\n
            return (this.chDontShow.getValue() == "checked");\r\n
        },\r\n
        textTitle: "Copy, Cut and Paste Actions",\r\n
        textMsg: "Copy, cut and paste actions using the editor toolbar buttons and context menu actions will be performed within this editor tab only.<br><br>.To copy or paste to or from applications outside the editor tab use the following keyboard combinations:",\r\n
        textToCopy: "for Copy",\r\n
        textToPaste: "for Paste",\r\n
        textToCut: "for Cut",\r\n
        textDontShow: "Don\'t show this message again"\r\n
    },\r\n
    Common.Views.CopyWarningDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5119</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
