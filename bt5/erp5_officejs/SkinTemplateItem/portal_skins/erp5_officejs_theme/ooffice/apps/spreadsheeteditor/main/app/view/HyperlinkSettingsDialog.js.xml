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
            <value> <string>ts44321338.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>HyperlinkSettingsDialog.js</string> </value>
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
define(["common/main/lib/util/utils", "common/main/lib/component/ComboBox", "common/main/lib/component/InputField", "common/main/lib/component/Window"], function () {\r\n
    SSE.Views.HyperlinkSettingsDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 350,\r\n
            style: "min-width: 230px;",\r\n
            cls: "modal-dlg"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, {\r\n
                title: this.textTitle\r\n
            },\r\n
            options || {});\r\n
            this.template = [\'<div class="box">\', \'<div class="input-row">\', "<label>" + this.textLinkType + "</label>", "</div>", \'<div class="input-row" id="id-dlg-hyperlink-type" style="margin-bottom: 5px;">\', "</div>", \'<div id="id-dlg-hyperlink-external">\', \'<div class="input-row">\', "<label>" + this.strLinkTo + " *</label>", "</div>", \'<div id="id-dlg-hyperlink-url" class="input-row" style="margin-bottom: 5px;"></div>\', "</div>", \'<div id="id-dlg-hyperlink-internal" style="display: none;">\', \'<div class="input-row">\', \'<label style="width: 50%;">\' + this.strSheet + "</label>", \'<label style="width: 50%;">\' + this.strRange + " *</label>", "</div>", \'<div class="input-row" style="margin-bottom: 5px;">\', \'<div id="id-dlg-hyperlink-sheet" style="display: inline-block; width: 50%; padding-right: 10px; float: left;"></div>\', \'<div id="id-dlg-hyperlink-range" style="display: inline-block; width: 50%;"></div>\', "</div>", "</div>", \'<div class="input-row">\', "<label>" + this.strDisplay + "</label>", "</div>", \'<div id="id-dlg-hyperlink-display" class="input-row" style="margin-bottom: 5px;"></div>\', \'<div class="input-row">\', "<label>" + this.textTipText + "</label>", "</div>", \'<div id="id-dlg-hyperlink-tip" class="input-row" style="margin-bottom: 5px;"></div>\', "</div>", \'<div class="footer right">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + this.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + this.cancelButtonText + "</button>", "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var $window = this.getChild(),\r\n
            me = this;\r\n
            me.cmbLinkType = new Common.UI.ComboBox({\r\n
                el: $("#id-dlg-hyperlink-type"),\r\n
                cls: "input-group-nr",\r\n
                editable: false,\r\n
                menuStyle: "min-width: 100%;",\r\n
                data: [{\r\n
                    displayValue: this.textInternalLink,\r\n
                    value: c_oAscHyperlinkType.RangeLink\r\n
                },\r\n
                {\r\n
                    displayValue: this.textExternalLink,\r\n
                    value: c_oAscHyperlinkType.WebLink\r\n
                }]\r\n
            }).on("selected", function (combo, record) {\r\n
                $("#id-dlg-hyperlink-external")[record.value == c_oAscHyperlinkType.WebLink ? "show" : "hide"]();\r\n
                $("#id-dlg-hyperlink-internal")[record.value != c_oAscHyperlinkType.WebLink ? "show" : "hide"]();\r\n
            });\r\n
            me.cmbLinkType.setValue(c_oAscHyperlinkType.WebLink);\r\n
            me.cmbSheets = new Common.UI.ComboBox({\r\n
                el: $("#id-dlg-hyperlink-sheet"),\r\n
                cls: "input-group-nr",\r\n
                editable: false,\r\n
                menuStyle: "min-width: 100%;max-height: 150px;"\r\n
            });\r\n
            me.inputUrl = new Common.UI.InputField({\r\n
                el: $("#id-dlg-hyperlink-url"),\r\n
                allowBlank: false,\r\n
                blankError: me.txtEmpty,\r\n
                validateOnBlur: false,\r\n
                style: "width: 100%;",\r\n
                validation: function (value) {\r\n
                    me.isEmail = false;\r\n
                    var isvalid = value.strongMatch(Common.Utils.hostnameRe); ! isvalid && (me.isEmail = isvalid = value.strongMatch(Common.Utils.emailRe)); ! isvalid && (isvalid = value.strongMatch(Common.Utils.ipRe)); ! isvalid && (isvalid = value.strongMatch(Common.Utils.localRe));\r\n
                    if (isvalid) {\r\n
                        return true;\r\n
                    } else {\r\n
                        return me.txtNotUrl;\r\n
                    }\r\n
                }\r\n
            });\r\n
            me.inputRange = new Common.UI.InputField({\r\n
                el: $("#id-dlg-hyperlink-range"),\r\n
                allowBlank: false,\r\n
                blankError: me.txtEmpty,\r\n
                style: "width: 100%;",\r\n
                validateOnChange: true,\r\n
                validateOnBlur: false,\r\n
                validation: function (value) {\r\n
                    var isvalid = /^[A-Z]+[1-9]\\d*:[A-Z]+[1-9]\\d*$/.test(value);\r\n
                    if (!isvalid) {\r\n
                        isvalid = /^[A-Z]+[1-9]\\d*$/.test(value);\r\n
                    }\r\n
                    if (isvalid) {\r\n
                        return true;\r\n
                    } else {\r\n
                        return me.textInvalidRange;\r\n
                    }\r\n
                }\r\n
            });\r\n
            me.inputDisplay = new Common.UI.InputField({\r\n
                el: $("#id-dlg-hyperlink-display"),\r\n
                allowBlank: true,\r\n
                validateOnBlur: false,\r\n
                style: "width: 100%;"\r\n
            });\r\n
            me.inputTip = new Common.UI.InputField({\r\n
                el: $("#id-dlg-hyperlink-tip"),\r\n
                style: "width: 100%;"\r\n
            });\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            $window.find("input").on("keypress", _.bind(this.onKeyPress, this));\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.Window.prototype.show.apply(this, arguments);\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                if (me.focusedInput) {\r\n
                    me.focusedInput.focus();\r\n
                }\r\n
            },\r\n
            500);\r\n
        },\r\n
        setSettings: function (settings) {\r\n
            if (settings) {\r\n
                var me = this;\r\n
                this.cmbSheets.setData(settings.sheets);\r\n
                if (!settings.props) {\r\n
                    this.cmbLinkType.setValue(c_oAscHyperlinkType.WebLink);\r\n
                    this.cmbLinkType.setDisabled(!settings.allowInternal);\r\n
                    this.inputDisplay.setValue(settings.isLock ? this.textDefault : settings.text);\r\n
                    this.focusedInput = this.inputUrl.cmpEl.find("input");\r\n
                    this.cmbSheets.setValue(settings.currentSheet);\r\n
                } else {\r\n
                    this.cmbLinkType.setValue(settings.props.asc_getType());\r\n
                    this.cmbLinkType.setDisabled(!settings.allowInternal);\r\n
                    if (settings.props.asc_getType() == c_oAscHyperlinkType.RangeLink) {\r\n
                        $("#id-dlg-hyperlink-external").hide();\r\n
                        $("#id-dlg-hyperlink-internal").show();\r\n
                        this.cmbSheets.setValue(settings.props.asc_getSheet());\r\n
                        this.inputRange.setValue(settings.props.asc_getRange());\r\n
                        this.focusedInput = this.inputRange.cmpEl.find("input");\r\n
                    } else {\r\n
                        this.inputUrl.setValue(settings.props.asc_getHyperlinkUrl());\r\n
                        this.focusedInput = this.inputUrl.cmpEl.find("input");\r\n
                        this.cmbSheets.setValue(settings.currentSheet);\r\n
                    }\r\n
                    this.inputDisplay.setValue(settings.isLock ? this.textDefault : settings.props.asc_getText());\r\n
                    this.inputTip.setValue(settings.props.asc_getTooltip());\r\n
                }\r\n
                this.inputDisplay.setDisabled(settings.isLock);\r\n
            }\r\n
        },\r\n
        getSettings: function () {\r\n
            var props = new Asc.asc_CHyperlink(),\r\n
            def_display = "";\r\n
            props.asc_setType(this.cmbLinkType.getValue());\r\n
            if (this.cmbLinkType.getValue() == c_oAscHyperlinkType.RangeLink) {\r\n
                props.asc_setSheet(this.cmbSheets.getValue());\r\n
                props.asc_setRange(this.inputRange.getValue());\r\n
                def_display = this.cmbSheets.getValue() + "!" + this.inputRange.getValue();\r\n
            } else {\r\n
                var url = this.inputUrl.getValue().replace(/^\\s+|\\s+$/g, "");\r\n
                if (!/(((^https?)|(^ftp)):\\/\\/)|(^mailto:)/i.test(url)) {\r\n
                    url = ((this.isEmail) ? "mailto:": "http://") + url;\r\n
                }\r\n
                props.asc_setHyperlinkUrl(url);\r\n
                def_display = url;\r\n
            }\r\n
            if (this.inputDisplay.isDisabled()) {\r\n
                props.asc_setText(null);\r\n
            } else {\r\n
                if (_.isEmpty(this.inputDisplay.getValue())) {\r\n
                    this.inputDisplay.setValue(def_display);\r\n
                }\r\n
                props.asc_setText(this.inputDisplay.getValue());\r\n
            }\r\n
            props.asc_setTooltip(this.inputTip.getValue());\r\n
            return props;\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            this._handleInput(event.currentTarget.attributes["result"].value);\r\n
        },\r\n
        onKeyPress: function (event) {\r\n
            if (event.keyCode == Common.UI.Keys.RETURN) {\r\n
                this._handleInput("ok");\r\n
                return false;\r\n
            }\r\n
        },\r\n
        _handleInput: function (state) {\r\n
            if (this.options.handler) {\r\n
                if (state == "ok") {\r\n
                    var checkurl = (this.cmbLinkType.getValue() === c_oAscHyperlinkType.WebLink) ? this.inputUrl.checkValidate() : true,\r\n
                    checkrange = (this.cmbLinkType.getValue() === c_oAscHyperlinkType.RangeLink) ? this.inputRange.checkValidate() : true,\r\n
                    checkdisp = this.inputDisplay.checkValidate();\r\n
                    if (checkurl !== true) {\r\n
                        this.inputUrl.cmpEl.find("input").focus();\r\n
                        return;\r\n
                    }\r\n
                    if (checkrange !== true) {\r\n
                        this.inputRange.cmpEl.find("input").focus();\r\n
                        return;\r\n
                    }\r\n
                    if (checkdisp !== true) {\r\n
                        this.inputDisplay.cmpEl.find("input").focus();\r\n
                        return;\r\n
                    }\r\n
                }\r\n
                this.options.handler.call(this, this, state);\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        textTitle: "Hyperlink Settings",\r\n
        textInternalLink: "Internal Data Range",\r\n
        textExternalLink: "Web Link",\r\n
        textEmptyLink: "Enter link here",\r\n
        textEmptyDesc: "Enter caption here",\r\n
        textEmptyTooltip: "Enter tooltip here",\r\n
        strSheet: "Sheet",\r\n
        strRange: "Range",\r\n
        textLinkType: "Link Type",\r\n
        strDisplay: "Display",\r\n
        textTipText: "Screen Tip Text",\r\n
        strLinkTo: "Link To",\r\n
        txtEmpty: "This field is required",\r\n
        textInvalidRange: "ERROR! Invalid cells range",\r\n
        txtNotUrl: \'This field should be a URL in the format "http://www.example.com"\',\r\n
        cancelButtonText: "Cancel",\r\n
        textDefault: "Selected range"\r\n
    },\r\n
    SSE.Views.HyperlinkSettingsDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>13110</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
