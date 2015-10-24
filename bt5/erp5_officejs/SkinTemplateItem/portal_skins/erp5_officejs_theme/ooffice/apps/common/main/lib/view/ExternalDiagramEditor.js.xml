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
            <value> <string>ts44321418.71</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ExternalDiagramEditor.js</string> </value>
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
    Common.Views.ExternalDiagramEditor = Common.UI.Window.extend(_.extend({\r\n
        initialize: function (options) {\r\n
            var _options = {};\r\n
            _.extend(_options, {\r\n
                title: this.textTitle,\r\n
                width: 910,\r\n
                height: (window.innerHeight - 700) < 0 ? window.innerHeight : 700,\r\n
                cls: "advanced-settings-dlg",\r\n
                header: true,\r\n
                toolclose: "hide",\r\n
                toolcallback: _.bind(this.onToolClose, this)\r\n
            },\r\n
            options);\r\n
            this.template = [\'<div id="id-diagram-editor-container" class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div id="id-diagram-editor-placeholder" style="width: 100%;height: 100%;"></div>\', "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer" style="text-align: center;">\', \'<button id="id-btn-diagram-editor-apply" class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px; width: auto; min-width: 86px;">\' + this.textSave + "</button>", \'<button id="id-btn-diagram-editor-cancel" class="btn normal dlg-btn disabled" result="cancel">\' + this.textClose + "</button>", "</div>"].join("");\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            this.handler = _options.handler;\r\n
            this._chartData = null;\r\n
            this._isNewChart = true;\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.btnSave = new Common.UI.Button({\r\n
                el: $("#id-btn-diagram-editor-apply"),\r\n
                disabled: true\r\n
            });\r\n
            this.btnCancel = new Common.UI.Button({\r\n
                el: $("#id-btn-diagram-editor-cancel"),\r\n
                disabled: true\r\n
            });\r\n
            this.$window.find(".tool.close").addClass("disabled");\r\n
            this.$window.find(".dlg-btn").on("click", _.bind(this.onDlgBtnClick, this));\r\n
        },\r\n
        setChartData: function (data) {\r\n
            this._chartData = data;\r\n
            if (this._isExternalDocReady) {\r\n
                this.fireEvent("setchartdata", this);\r\n
            }\r\n
        },\r\n
        setEditMode: function (mode) {\r\n
            this._isNewChart = !mode;\r\n
        },\r\n
        isEditMode: function () {\r\n
            return !this._isNewChart;\r\n
        },\r\n
        setControlsDisabled: function (disable) {\r\n
            this.btnSave.setDisabled(disable);\r\n
            this.btnCancel.setDisabled(disable);\r\n
            (disable) ? this.$window.find(".tool.close").addClass("disabled") : this.$window.find(".tool.close").removeClass("disabled");\r\n
        },\r\n
        onDlgBtnClick: function (event) {\r\n
            var state = event.currentTarget.attributes["result"].value;\r\n
            if (this.handler && this.handler.call(this, state)) {\r\n
                return;\r\n
            }\r\n
            this.hide();\r\n
        },\r\n
        onToolClose: function () {\r\n
            if (this.handler && this.handler.call(this, "cancel")) {\r\n
                return;\r\n
            }\r\n
            this.hide();\r\n
        },\r\n
        setHeight: function (height) {\r\n
            if (height >= 0) {\r\n
                var min = parseInt(this.$window.css("min-height"));\r\n
                height < min && (height = min);\r\n
                this.$window.height(height);\r\n
                var header_height = (this.initConfig.header) ? parseInt(this.$window.find("> .header").css("height")) : 0;\r\n
                this.$window.find("> .body").css("height", height - header_height);\r\n
                this.$window.find("> .body > .box").css("height", height - 85);\r\n
                var top = ((parseInt(window.innerHeight) - parseInt(height)) / 2) * 0.9;\r\n
                var left = (parseInt(window.innerWidth) - parseInt(this.initConfig.width)) / 2;\r\n
                this.$window.css("left", left);\r\n
                this.$window.css("top", top);\r\n
            }\r\n
        },\r\n
        textSave: "Save & Exit",\r\n
        textClose: "Close",\r\n
        textTitle: "Chart Editor"\r\n
    },\r\n
    Common.Views.ExternalDiagramEditor || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5802</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
