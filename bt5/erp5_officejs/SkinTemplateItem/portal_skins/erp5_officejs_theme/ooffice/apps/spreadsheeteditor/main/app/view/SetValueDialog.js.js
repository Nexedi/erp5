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
            <value> <string>ts44321339.32</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>SetValueDialog.js</string> </value>
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
 define(["common/main/lib/component/Window", "common/main/lib/component/ComboBox"], function () {\r\n
    SSE.Views.SetValueDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 214,\r\n
            header: true,\r\n
            style: "min-width: 214px;",\r\n
            cls: "modal-dlg"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle\r\n
            },\r\n
            options || {});\r\n
            this.template = [\'<div class="box">\', \'<div class="input-row">\', \'<div id="id-spin-set-value"></div>\', "</div>", \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + this.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + this.cancelButtonText + "</button>", "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            this.startvalue = this.options.startvalue;\r\n
            this.maxvalue = this.options.maxvalue;\r\n
            this.defaultUnit = this.options.defaultUnit;\r\n
            this.step = this.options.step;\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.spnSize = new Common.UI.MetricSpinner({\r\n
                el: $("#id-spin-set-value"),\r\n
                width: 182,\r\n
                step: this.step,\r\n
                defaultUnit: this.defaultUnit,\r\n
                minValue: 0,\r\n
                maxValue: this.maxvalue,\r\n
                value: this.startvalue + " " + this.defaultUnit\r\n
            });\r\n
            var $window = this.getChild();\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.spnSize.on("entervalue", _.bind(this.onEnterValue, this));\r\n
            this.spnSize.on("change", _.bind(this.onChange, this));\r\n
            this.spnSize.$el.find("input").focus();\r\n
        },\r\n
        _handleInput: function (state) {\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, this, state);\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            this._handleInput(event.currentTarget.attributes["result"].value);\r\n
        },\r\n
        onEnterValue: function (event) {\r\n
            this._handleInput("ok");\r\n
        },\r\n
        onChange: function () {\r\n
            var val = this.spnSize.getNumberValue();\r\n
            val = val / this.step;\r\n
            val = (val | val) * this.step;\r\n
            this.spnSize.setValue(val, true);\r\n
        },\r\n
        getSettings: function () {\r\n
            return this.spnSize.getNumberValue();\r\n
        },\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok",\r\n
        txtMinText: "The minimum value for this field is {0}",\r\n
        txtMaxText: "The maximum value for this field is {0}"\r\n
    },\r\n
    SSE.Views.SetValueDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4610</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
