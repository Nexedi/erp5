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
            <value> <string>ts44321337.8</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>CellRangeDialog.js</string> </value>
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
define(["common/main/lib/component/InputField", "common/main/lib/component/Window"], function () {\r\n
    SSE.Views.CellRangeDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 350,\r\n
            cls: "modal-dlg",\r\n
            modal: false\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.txtTitle\r\n
            },\r\n
            options);\r\n
            this.template = [\'<div class="box">\', \'<div id="id-dlg-cell-range" class="input-row" style="margin-bottom: 5px;"></div>\', "</div>", \'<div class="footer right">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + this.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + this.cancelButtonText + "</button>", "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var $window = this.getChild(),\r\n
            me = this;\r\n
            me.inputRange = new Common.UI.InputField({\r\n
                el: $("#id-dlg-cell-range"),\r\n
                name: "range",\r\n
                style: "width: 100%;",\r\n
                allowBlank: false,\r\n
                blankError: this.txtEmpty,\r\n
                validateOnChange: true\r\n
            });\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            me.inputRange.cmpEl.find("input").on("keypress", _.bind(this.onKeyPress, this));\r\n
            this.on("close", _.bind(this.onClose, this));\r\n
        },\r\n
        onPrimary: function () {\r\n
            this._handleInput("ok");\r\n
            return false;\r\n
        },\r\n
        setSettings: function (settings) {\r\n
            var me = this;\r\n
            this.inputRange.setValue(settings.range ? settings.range : "");\r\n
            if (settings.api) {\r\n
                me.api = settings.api;\r\n
                me.api.asc_setSelectionDialogMode(c_oAscSelectionDialogType.Chart, settings.range ? settings.range : "");\r\n
                me.api.asc_registerCallback("asc_onSelectionRangeChanged", _.bind(me.onApiRangeChanged, me));\r\n
                Common.NotificationCenter.trigger("cells:range", c_oAscSelectionDialogType.Chart);\r\n
            }\r\n
            me.inputRange.validation = function (value) {\r\n
                var isvalid = me.api.asc_checkDataRange(c_oAscSelectionDialogType.Chart, value, false);\r\n
                return (isvalid == c_oAscError.ID.DataRangeError) ? me.txtInvalidRange : true;\r\n
            };\r\n
        },\r\n
        getSettings: function () {\r\n
            return this.inputRange.getValue();\r\n
        },\r\n
        onApiRangeChanged: function (info) {\r\n
            this.inputRange.setValue(info);\r\n
            if (this.inputRange.cmpEl.hasClass("error")) {\r\n
                this.inputRange.cmpEl.removeClass("error");\r\n
            }\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            this._handleInput(event.currentTarget.attributes["result"].value);\r\n
        },\r\n
        onClose: function (event) {\r\n
            if (this.api) {\r\n
                this.api.asc_setSelectionDialogMode(c_oAscSelectionDialogType.None);\r\n
            }\r\n
            Common.NotificationCenter.trigger("cells:range", c_oAscSelectionDialogType.None);\r\n
        },\r\n
        onKeyPress: function (event) {\r\n
            if (event.keyCode == Common.UI.Keys.RETURN) {\r\n
                this._handleInput("ok");\r\n
            }\r\n
        },\r\n
        _handleInput: function (state) {\r\n
            if (this.options.handler) {\r\n
                if (state == "ok") {\r\n
                    if (this.inputRange.checkValidate() !== true) {\r\n
                        return;\r\n
                    }\r\n
                }\r\n
                this.options.handler.call(this, this, state);\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        txtTitle: "Select Data Range",\r\n
        textCancel: "Cancel",\r\n
        txtEmpty: "This field is required",\r\n
        txtInvalidRange: "ERROR! Invalid cells range",\r\n
        errorMaxRows: "ERROR! The maximum number of data series per chart is 255."\r\n
    },\r\n
    SSE.Views.CellRangeDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5923</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
