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
            <value> <string>ts44321418.14</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>AdvancedSettingsWindow.js</string> </value>
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
 define(["common/main/lib/component/Window"], function () {\r\n
    Common.Views.AdvancedSettingsWindow = Common.UI.Window.extend(_.extend({\r\n
        initialize: function (options) {\r\n
            var _options = {};\r\n
            _.extend(_options, {\r\n
                height: 200,\r\n
                header: true,\r\n
                cls: "advanced-settings-dlg",\r\n
                toggleGroup: "advanced-settings-group",\r\n
                contentTemplate: "",\r\n
                items: []\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div class="menu-panel">\', "<% _.each(items, function(item) { %>", \'<button class="btn btn-category" style="margin-bottom: 2px;" content-target="<%= item.panelId %>"><span class=""><%= item.panelCaption %></span></button>\', "<% }); %>", "</div>", \'<div class="separator"/>\', \'<div class="content-panel" >\' + _options.contentTemplate + "</div>", "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + this.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + this.cancelButtonText + "</button>", "</div>"].join("");\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            this.handler = _options.handler;\r\n
            this.toggleGroup = _options.toggleGroup;\r\n
            this.contentWidth = _options.contentWidth;\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var me = this;\r\n
            var $window = this.getChild();\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onDlgBtnClick, this));\r\n
            this.btnsCategory = [];\r\n
            _.each($window.find(".btn-category"), function (item, index) {\r\n
                var btnEl = $(item);\r\n
                var btn = new Common.UI.Button({\r\n
                    el: btnEl,\r\n
                    enableToggle: true,\r\n
                    toggleGroup: me.toggleGroup,\r\n
                    allowDepress: false,\r\n
                    contentTarget: btnEl.attr("content-target")\r\n
                });\r\n
                btn.on("click", _.bind(me.onCategoryClick, me));\r\n
                me.btnsCategory.push(btn);\r\n
            });\r\n
            var cnt_panel = $window.find(".content-panel");\r\n
            cnt_panel.width(this.contentWidth);\r\n
            $window.width($window.find(".menu-panel").width() + cnt_panel.outerWidth() + 1);\r\n
            this.content_panels = $window.find(".settings-panel");\r\n
            if (this.btnsCategory.length > 0) {\r\n
                this.btnsCategory[0].toggle(true, true);\r\n
            }\r\n
        },\r\n
        setHeight: function (height) {\r\n
            Common.UI.Window.prototype.setHeight.call(this, height);\r\n
            var $window = this.getChild();\r\n
            var boxEl = $window.find(".body > .box");\r\n
            boxEl.css("height", height - 85);\r\n
        },\r\n
        onDlgBtnClick: function (event) {\r\n
            var state = event.currentTarget.attributes["result"].value;\r\n
            if (this.handler && this.handler.call(this, state, (state == "ok") ? this.getSettings() : undefined)) {\r\n
                return;\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onCategoryClick: function (btn, event) {\r\n
            this.content_panels.filter(".active").removeClass("active");\r\n
            $("#" + btn.options.contentTarget).addClass("active");\r\n
        },\r\n
        getSettings: function () {\r\n
            return;\r\n
        },\r\n
        onPrimary: function () {\r\n
            if (this.handler && this.handler.call(this, "ok", this.getSettings())) {\r\n
                return;\r\n
            }\r\n
            this.close();\r\n
            return false;\r\n
        },\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok"\r\n
    },\r\n
    Common.Views.AdvancedSettingsWindow || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5613</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
