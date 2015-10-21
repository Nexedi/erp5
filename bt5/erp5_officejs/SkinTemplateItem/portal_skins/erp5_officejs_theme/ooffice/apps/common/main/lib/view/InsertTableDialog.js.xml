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
            <value> <string>ts44321419.26</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>InsertTableDialog.js</string> </value>
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
    Common.Views.InsertTableDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 230,\r\n
            height: 170,\r\n
            header: false,\r\n
            style: "min-width: 230px;",\r\n
            cls: "modal-dlg"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, options || {});\r\n
            this.template = [\'<div class="box">\', "<h4>" + this.txtTitle + "</h4>", \'<div class="input-row" style="margin: 10px 0;">\', \'<label class="text columns-text" style="width: 130px;">\' + this.txtColumns + \'</label><div class="columns-val" style="float: right;"></div>\', "</div>", \'<div class="input-row" style="margin: 10px 0;">\', \'<label class="text rows-text" style="width: 130px;">\' + this.txtRows + \'</label><div class="rows-val" style="float: right;"></div>\', "</div>", "</div>", \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + this.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + this.cancelButtonText + "</button>", "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var $window = this.getChild();\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.udColumns = new Common.UI.MetricSpinner({\r\n
                el: $window.find(".columns-val"),\r\n
                step: 1,\r\n
                width: 64,\r\n
                value: 2,\r\n
                defaultUnit: "",\r\n
                maxValue: 63,\r\n
                minValue: 1,\r\n
                allowDecimal: false\r\n
            });\r\n
            this.udRows = new Common.UI.MetricSpinner({\r\n
                el: $window.find(".rows-val"),\r\n
                step: 1,\r\n
                width: 64,\r\n
                value: 2,\r\n
                defaultUnit: "",\r\n
                maxValue: 100,\r\n
                minValue: 1,\r\n
                allowDecimal: false\r\n
            });\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, event.currentTarget.attributes["result"].value, {\r\n
                    columns: this.udColumns.getValue(),\r\n
                    rows: this.udRows.getValue()\r\n
                });\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onPrimary: function () {\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, "ok", {\r\n
                    columns: this.udColumns.getValue(),\r\n
                    rows: this.udRows.getValue()\r\n
                });\r\n
            }\r\n
            this.close();\r\n
            return false;\r\n
        },\r\n
        txtTitle: "Table size",\r\n
        txtColumns: "Number of Columns",\r\n
        txtRows: "Number of Rows",\r\n
        textInvalidRowsCols: "You need to specify valid rows and columns count.",\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok",\r\n
        txtMinText: "The minimum value for this field is {0}",\r\n
        txtMaxText: "The maximum value for this field is {0}"\r\n
    },\r\n
    Common.Views.InsertTableDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5010</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
