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
            <value> <string>ts44321338.87</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>OpenDialog.js</string> </value>
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
    SSE.Views = SSE.Views || {};\r\n
    SSE.Views.OpenDialog = Common.UI.Window.extend(_.extend({\r\n
        applyFunction: undefined,\r\n
        initialize: function (options) {\r\n
            var t = this,\r\n
            _options = {};\r\n
            _.extend(_options, {\r\n
                width: 250,\r\n
                height: 220,\r\n
                contentWidth: 390,\r\n
                header: true,\r\n
                cls: "open-dlg",\r\n
                contentTemplate: "",\r\n
                title: t.txtTitle\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div class="content-panel" >\', \'<label class="header">\' + t.txtEncoding + "</label>", \'<div id="id-codepages-combo" class="input-group-nr" style="margin-top:10px;margin-bottom:10px;"></div>\', \'<label class="header">\' + t.txtDelimiter + "</label>", \'<div id="id-delimiters-combo" class="input-group-nr" style="margin-top:10px;max-width: 110px;"></div>\', "</div>", "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right:10px;">\' + t.okButtonText + "</button>", "</div>"].join("");\r\n
            this.handler = options.handler;\r\n
            this.codepages = options.codepages;\r\n
            this.settings = options.settings;\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            if (this.$window) {\r\n
                this.$window.find(".tool").hide();\r\n
                this.$window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
                this.initCodePages();\r\n
            }\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if (this.handler && this.cmbEncoding && this.cmbDelimiter) {\r\n
                this.handler.call(this, this.cmbEncoding.getValue(), this.cmbDelimiter.getValue());\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        initCodePages: function () {\r\n
            var i, c, codepage, encodedata = [],\r\n
            listItems = [],\r\n
            length = 0;\r\n
            if (this.codepages) {\r\n
                encodedata = [];\r\n
                for (i = 0; i < this.codepages.length; ++i) {\r\n
                    codepage = this.codepages[i];\r\n
                    c = [];\r\n
                    c[0] = codepage.asc_getCodePage();\r\n
                    c[1] = codepage.asc_getCodePageName();\r\n
                    encodedata.push(c);\r\n
                }\r\n
            } else {\r\n
                encodedata = [[37, "IBM EBCDIC (US-Canada)"], [437, "OEM United States"], [500, "IBM EBCDIC (International)"], [708, "Arabic (ASMO 708)"], [720, "Arabic (DOS)"], [737, "Greek (DOS)"], [775, "Baltic (DOS)"], [850, "Western European (DOS)"], [852, "Central European (DOS)"], [855, "OEM Cyrillic"], [857, "Turkish (DOS)"], [858, "OEM Multilingual Latin I"], [860, "Portuguese (DOS)"], [861, "Icelandic (DOS)"], [862, "Hebrew (DOS)"], [863, "French Canadian (DOS)"], [864, "Arabic (864) "], [865, "Nordic (DOS)"], [866, "Cyrillic (DOS)"], [869, "Greek, Modern (DOS)"], [870, "IBM EBCDIC (Multilingual Latin-2)"], [874, "Thai (Windows)"], [875, "IBM EBCDIC (Greek Modern)"], [932, "Japanese (Shift-JIS)"], [936, "Chinese Simplified (GB2312)"], [949, "Korean"], [950, "Chinese Traditional (Big5)"], [1026, "IBM EBCDIC (Turkish Latin-5)"], [1047, "IBM Latin-1"], [1140, "IBM EBCDIC (US-Canada-Euro)"], [1141, "IBM EBCDIC (Germany-Euro)"], [1142, "IBM EBCDIC (Denmark-Norway-Euro)"], [1143, "IBM EBCDIC (Finland-Sweden-Euro)"], [1144, "IBM EBCDIC (Italy-Euro)"], [1145, "IBM EBCDIC (Spain-Euro)"], [1146, "IBM EBCDIC (UK-Euro)"], [1147, "IBM EBCDIC (France-Euro)"], [1148, "IBM EBCDIC (International-Euro)"], [1149, "IBM EBCDIC (Icelandic-Euro)"], [1200, "Unicode"], [1201, "Unicode (Big-Endian)"], [1250, "Central European (Windows)"], [1251, "Cyrillic (Windows)"], [1252, "Western European (Windows)"], [1253, "Greek (Windows)"], [1254, "Turkish (Windows)"], [1255, "Hebrew (Windows) "], [1256, "Arabic (Windows) "], [1257, "Baltic (Windows)"], [1258, "Vietnamese (Windows)"], [1361, "Korean (Johab)"], [10000, "Western European (Mac)"], [10001, "Japanese (Mac)"], [10002, "Chinese Traditional (Mac)"], [10003, "Korean (Mac)"], [10004, "Arabic (Mac) "], [10005, "Hebrew (Mac)"], [10006, "Greek (Mac) "], [10007, "Cyrillic (Mac)"], [10008, "Chinese Simplified (Mac)"], [10010, "Romanian (Mac)"], [10017, "Ukrainian (Mac)"], [10021, "Thai (Mac)"], [10029, "Central European (Mac) "], [10079, "Icelandic (Mac)"], [10081, "Turkish (Mac)"], [10082, "Croatian (Mac)"], [12000, "Unicode (UTF-32)"], [12001, "Unicode (UTF-32 Big-Endian)"], [20000, "Chinese Traditional (CNS)"], [20001, "TCA Taiwan"], [20002, "Chinese Traditional (Eten)"], [20003, "IBM5550 Taiwan"], [20004, "TeleText Taiwan"], [20005, "Wang Taiwan"], [20105, "Western European (IA5)"], [20106, "German (IA5)"], [20107, "Swedish (IA5) "], [20108, "Norwegian (IA5) "], [20127, "US-ASCII"], [20261, "T.61 "], [20269, "ISO-6937"], [20273, "IBM EBCDIC (Germany)"], [20277, "IBM EBCDIC (Denmark-Norway) "], [20278, "IBM EBCDIC (Finland-Sweden)"], [20280, "IBM EBCDIC (Italy)"], [20284, "IBM EBCDIC (Spain)"], [20285, "IBM EBCDIC (UK)"], [20290, "IBM EBCDIC (Japanese katakana)"], [20297, "IBM EBCDIC (France)"], [20420, "IBM EBCDIC (Arabic)"], [20423, "IBM EBCDIC (Greek)"], [20424, "IBM EBCDIC (Hebrew)"], [20833, "IBM EBCDIC (Korean Extended)"], [20838, "IBM EBCDIC (Thai)"], [20866, "Cyrillic (KOI8-R)"], [20871, "IBM EBCDIC (Icelandic) "], [20880, "IBM EBCDIC (Cyrillic Russian)"], [20905, "IBM EBCDIC (Turkish)"], [20924, "IBM Latin-1 "], [20932, "Japanese (JIS 0208-1990 and 0212-1990)"], [20936, "Chinese Simplified (GB2312-80) "], [20949, "Korean Wansung "], [21025, "IBM EBCDIC (Cyrillic Serbian-Bulgarian)"], [21866, "Cyrillic (KOI8-U)"], [28591, "Western European (ISO) "], [28592, "Central European (ISO)"], [28593, "Latin 3 (ISO)"], [28594, "Baltic (ISO)"], [28595, "Cyrillic (ISO) "], [28596, "Arabic (ISO)"], [28597, "Greek (ISO) "], [28598, "Hebrew (ISO-Visual)"], [28599, "Turkish (ISO)"], [28603, "Estonian (ISO)"], [28605, "Latin 9 (ISO)"], [29001, "Europa"], [38598, "Hebrew (ISO-Logical)"], [50220, "Japanese (JIS)"], [50221, "Japanese (JIS-Allow 1 byte Kana) "], [50222, "Japanese (JIS-Allow 1 byte Kana - SO/SI)"], [50225, "Korean (ISO)"], [50227, "Chinese Simplified (ISO-2022)"], [51932, "Japanese (EUC)"], [51936, "Chinese Simplified (EUC) "], [51949, "Korean (EUC)"], [52936, "Chinese Simplified (HZ)"], [54936, "Chinese Simplified (GB18030)"], [57002, "ISCII Devanagari "], [57003, "ISCII Bengali "], [57004, "ISCII Tamil"], [57005, "ISCII Telugu "], [57006, "ISCII Assamese "], [57007, "ISCII Oriya"], [57008, "ISCII Kannada"], [57009, "ISCII Malayalam "], [57010, "ISCII Gujarati"], [57011, "ISCII Punjabi"], [65000, "Unicode (UTF-7)"], [65001, "Unicode (UTF-8)"]];\r\n
            }\r\n
            length = encodedata.length;\r\n
            if (length) {\r\n
                for (i = 0; i < length; ++i) {\r\n
                    listItems.push({\r\n
                        value: encodedata[i][0],\r\n
                        displayValue: encodedata[i][1]\r\n
                    });\r\n
                }\r\n
                this.cmbEncoding = new Common.UI.ComboBox({\r\n
                    el: $("#id-codepages-combo", this.$window),\r\n
                    menuStyle: "min-width: 220px;",\r\n
                    cls: "input-group-nr",\r\n
                    menuCls: "scrollable-menu",\r\n
                    data: listItems,\r\n
                    editable: false\r\n
                });\r\n
                this.cmbDelimiter = new Common.UI.ComboBox({\r\n
                    el: $("#id-delimiters-combo", this.$window),\r\n
                    menuStyle: "min-width: 110px;",\r\n
                    cls: "input-group-nr",\r\n
                    data: [{\r\n
                        value: 4,\r\n
                        displayValue: ","\r\n
                    },\r\n
                    {\r\n
                        value: 2,\r\n
                        displayValue: ";"\r\n
                    },\r\n
                    {\r\n
                        value: 3,\r\n
                        displayValue: ":"\r\n
                    },\r\n
                    {\r\n
                        value: 1,\r\n
                        displayValue: this.txtTab\r\n
                    },\r\n
                    {\r\n
                        value: 5,\r\n
                        displayValue: this.txtSpace\r\n
                    }],\r\n
                    editable: false\r\n
                });\r\n
                this.cmbDelimiter.setValue(4);\r\n
                if (encodedata.length) {\r\n
                    this.cmbEncoding.setValue(encodedata[0][0]);\r\n
                    if (this.settings && this.settings.asc_getCodePage()) {\r\n
                        this.cmbEncoding.setValue(this.settings.asc_getCodePage());\r\n
                    }\r\n
                    if (this.settings && this.settings.asc_getDelimiter()) {\r\n
                        this.cmbDelimiter.setValue(this.settings.asc_getDelimiter());\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        okButtonText: "OK",\r\n
        cancelButtonText: "Cancel",\r\n
        txtDelimiter: "Delimiter",\r\n
        txtEncoding: "Encoding ",\r\n
        txtSpace: "Space",\r\n
        txtTab: "Tab",\r\n
        txtTitle: "Choose CSV options"\r\n
    },\r\n
    SSE.Views.OpenDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11147</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
