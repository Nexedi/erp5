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
            <value> <string>ts44321419.4</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>SearchDialog.js</string> </value>
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
    Common.UI.SearchDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 550,\r\n
            title: "Search & Replace",\r\n
            modal: false,\r\n
            cls: "search",\r\n
            toolclose: "hide",\r\n
            alias: "SearchDialog"\r\n
        },\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, options || {});\r\n
            this.template = [\'<div class="box">\', \'<div class="input-row">\', \'<span class="btn-placeholder" id="search-placeholder-btn-options"></span>\', \'<input type="text" id="sd-text-search" class="form-control" maxlength="100" placeholder="\' + this.textSearchStart + \'">\', "</div>", \'<div class="input-row">\', \'<input type="text" id="sd-text-replace" class="form-control" maxlength="100" placeholder="\' + this.textReplaceDef + \'">\', "</div>", \'<div class="input-row">\', \'<label class="link" id="search-label-replace" result="replaceshow">\' + this.txtBtnReplace + "</label>", "</div>", "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer right">\', \'<button class="btn normal dlg-btn" result="replace" style="margin-right: 6px;">\' + this.txtBtnReplace + "</button>", \'<button class="btn normal dlg-btn" result="replaceall" style="margin-right: 10px;">\' + this.txtBtnReplaceAll + "</button>", \'<button class="btn normal dlg-btn iconic" result="back" style="margin-right: 6px;"><span class="icon back" /></button>\', \'<button class="btn normal dlg-btn iconic" result="next"><span class="icon next" /></button>\', "</div>"].join("");\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.miMatchCase = new Common.UI.MenuItem({\r\n
                caption: this.textMatchCase,\r\n
                checkable: true\r\n
            });\r\n
            this.miMatchWord = new Common.UI.MenuItem({\r\n
                caption: this.options.matchwordstr || this.textWholeWords,\r\n
                checkable: true\r\n
            });\r\n
            this.miHighlight = new Common.UI.MenuItem({\r\n
                caption: this.textHighlight,\r\n
                checkable: true\r\n
            });\r\n
            this.btnOptions = new Common.UI.Button({\r\n
                id: "search-btn-options",\r\n
                cls: "btn-toolbar btn-toolbar-default",\r\n
                iconCls: "btn-settings",\r\n
                menu: new Common.UI.Menu({\r\n
                    items: [this.miMatchCase, this.miMatchWord, this.miHighlight]\r\n
                })\r\n
            });\r\n
            if (this.options.extraoptions) {\r\n
                this.btnOptions.menu.addItem({\r\n
                    caption: "--"\r\n
                });\r\n
                this.options.extraoptions.forEach(function (item) {\r\n
                    this.btnOptions.menu.addItem(item);\r\n
                },\r\n
                this);\r\n
            }\r\n
            this.btnOptions.render(this.$window.find("#search-placeholder-btn-options"));\r\n
            if (!this.options.matchcase) {\r\n
                this.miMatchCase.hide();\r\n
            }\r\n
            if (!this.options.matchword) {\r\n
                this.miMatchWord.hide();\r\n
            }\r\n
            if (!this.options.markresult) {\r\n
                this.miHighlight.hide();\r\n
            } else {\r\n
                if (this.options.markresult.applied) {\r\n
                    this.miHighlight.setChecked(true, true);\r\n
                }\r\n
            }\r\n
            if (this.options.mode === "search") {\r\n
                $(this.$window.find(".input-row").get(2)).hide();\r\n
            }\r\n
            this.txtSearch = this.$window.find("#sd-text-search");\r\n
            this.txtReplace = this.$window.find("#sd-text-replace");\r\n
            this.miHighlight.on("toggle", _.bind(this.onHighlight, this));\r\n
            this.$window.find(".btn[result=back]").on("click", _.bind(this.onBtnClick, this, "back"));\r\n
            this.$window.find(".btn[result=next]").on("click", _.bind(this.onBtnClick, this, "next"));\r\n
            this.$window.find(".btn[result=replace]").on("click", _.bind(this.onBtnClick, this, "replace"));\r\n
            this.$window.find(".btn[result=replaceall]").on("click", _.bind(this.onBtnClick, this, "replaceall"));\r\n
            this.$window.find("label[result=replaceshow]").on("click", _.bind(this.onShowReplace, this));\r\n
            this.txtSearch.on("keydown", null, "search", _.bind(this.onKeyPress, this));\r\n
            this.txtReplace.on("keydown", null, "replace", _.bind(this.onKeyPress, this));\r\n
            return this;\r\n
        },\r\n
        show: function (mode) {\r\n
            Common.UI.Window.prototype.show.call(this); ! this.mode && !mode && (mode = "search");\r\n
            if (mode && this.mode != mode) {\r\n
                this.setMode(mode);\r\n
            }\r\n
            if (this.options.markresult && this.miHighlight.checked) {\r\n
                this.fireEvent("search:highlight", [this, true]);\r\n
            }\r\n
            this.focus();\r\n
        },\r\n
        focus: function () {\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                me.txtSearch.focus();\r\n
                me.txtSearch.select();\r\n
            },\r\n
            300);\r\n
        },\r\n
        onKeyPress: function (event) {\r\n
            if (!this.isLocked()) {\r\n
                if (event.keyCode == Common.UI.Keys.RETURN) {\r\n
                    if (event.data == "search") {\r\n
                        this.onBtnClick("next", event);\r\n
                    } else {\r\n
                        if (event.data == "replace" && this.mode == "replace") {\r\n
                            this.onBtnClick("replace", event);\r\n
                        }\r\n
                    }\r\n
                    event.preventDefault();\r\n
                    event.stopPropagation();\r\n
                } else {\r\n
                    if (event.keyCode == Common.UI.Keys.ESC) {\r\n
                        this.hide();\r\n
                        event.preventDefault();\r\n
                        event.stopPropagation();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onBtnClick: function (action, event) {\r\n
            var opts = {\r\n
                textsearch: this.txtSearch.val(),\r\n
                textreplace: this.txtReplace.val(),\r\n
                matchcase: this.miMatchCase.checked,\r\n
                matchword: this.miMatchWord.checked,\r\n
                highlight: this.miHighlight.checked\r\n
            };\r\n
            this.fireEvent("search:" + action, [this, opts]);\r\n
        },\r\n
        setMode: function (m) {\r\n
            this.mode = m;\r\n
            var $inputs = this.$window.find(".input-row");\r\n
            if (m === "no-replace") {\r\n
                this.setTitle(this.textTitle2);\r\n
                $inputs.eq(1).hide();\r\n
                $inputs.eq(2).hide();\r\n
                this.$window.find(".btn[result=replace]").hide();\r\n
                this.$window.find(".btn[result=replaceall]").hide();\r\n
                if (this.options.matchcase || this.options.matchword || this.options.markresult) {} else {\r\n
                    this.txtSearch.addClass("clear");\r\n
                    this.btnOptions.hide();\r\n
                }\r\n
                this.setHeight(170);\r\n
            } else {\r\n
                this.txtSearch.removeClass("clear");\r\n
                this.setTitle(this.textTitle);\r\n
                if (m === "search") {\r\n
                    $inputs.eq(2).show();\r\n
                    $inputs.eq(1).hide();\r\n
                    this.$window.find(".btn[result=replace]").hide();\r\n
                    this.$window.find(".btn[result=replaceall]").hide();\r\n
                } else {\r\n
                    $inputs.eq(2).hide();\r\n
                    $inputs.eq(1).show();\r\n
                    this.$window.find(".btn[result=replace]").show();\r\n
                    this.$window.find(".btn[result=replaceall]").show();\r\n
                }\r\n
                this.setHeight(200);\r\n
            }\r\n
        },\r\n
        onShowReplace: function (e) {\r\n
            this.setMode("replace");\r\n
            var me = this;\r\n
            _.defer(function () {\r\n
                me.txtReplace.focus();\r\n
            },\r\n
            300);\r\n
        },\r\n
        onHighlight: function (o, value) {\r\n
            this.fireEvent("search:highlight", [this, value]);\r\n
        },\r\n
        getSettings: function () {\r\n
            return {\r\n
                textsearch: this.txtSearch.val(),\r\n
                casesensitive: this.miMatchCase.checked,\r\n
                wholewords: this.miMatchWord.checked\r\n
            };\r\n
        },\r\n
        textTitle: "Search & Replace",\r\n
        textTitle2: "Search",\r\n
        txtBtnReplace: "Replace",\r\n
        txtBtnReplaceAll: "Replace All",\r\n
        textMatchCase: "Case sensitive",\r\n
        textWholeWords: "Whole words only",\r\n
        textHighlight: "Highlight results",\r\n
        textReplaceDef: "Enter the replacement text",\r\n
        textSearchStart: "Enter text for search"\r\n
    },\r\n
    Common.UI.SearchDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10647</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
