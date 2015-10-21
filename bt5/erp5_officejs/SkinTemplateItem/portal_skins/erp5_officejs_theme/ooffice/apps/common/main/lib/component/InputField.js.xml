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
            <value> <string>ts44308799.4</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>InputField.js</string> </value>
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
define(["common/main/lib/component/BaseView", "common/main/lib/component/Tooltip"], function () {\r\n
    Common.UI.InputField = Common.UI.BaseView.extend((function () {\r\n
        return {\r\n
            options: {\r\n
                id: null,\r\n
                cls: "",\r\n
                style: "",\r\n
                value: "",\r\n
                type: "text",\r\n
                name: "",\r\n
                validation: null,\r\n
                allowBlank: true,\r\n
                placeHolder: "",\r\n
                blankError: null,\r\n
                spellcheck: false,\r\n
                maskExp: "",\r\n
                validateOnChange: false,\r\n
                validateOnBlur: true,\r\n
                disabled: false\r\n
            },\r\n
            template: _.template([\'<div class="input-field" style="<%= style %>">\', "<input ", \'type="<%= type %>" \', \'name="<%= name %>" \', \'spellcheck="<%= spellcheck %>" \', \'class="form-control <%= cls %>" \', \'placeholder="<%= placeHolder %>" \', \'value="<%= value %>"\', ">", \'<span class="input-error"/>\', "</div>"].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
                var me = this,\r\n
                el = $(this.el);\r\n
                this.id = me.options.id || Common.UI.getId();\r\n
                this.cls = me.options.cls;\r\n
                this.style = me.options.style;\r\n
                this.value = me.options.value;\r\n
                this.type = me.options.type;\r\n
                this.name = me.options.name;\r\n
                this.validation = me.options.validation;\r\n
                this.allowBlank = me.options.allowBlank;\r\n
                this.placeHolder = me.options.placeHolder;\r\n
                this.template = me.options.template || me.template;\r\n
                this.editable = me.options.editable || true;\r\n
                this.disabled = me.options.disabled;\r\n
                this.spellcheck = me.options.spellcheck;\r\n
                this.blankError = me.options.blankError || "This field is required";\r\n
                this.validateOnChange = me.options.validateOnChange;\r\n
                this.validateOnBlur = me.options.validateOnBlur;\r\n
                me.rendered = me.options.rendered || false;\r\n
                if (me.options.el) {\r\n
                    me.render();\r\n
                }\r\n
            },\r\n
            render: function (parentEl) {\r\n
                var me = this;\r\n
                if (!me.rendered) {\r\n
                    this.cmpEl = $(this.template({\r\n
                        id: this.id,\r\n
                        cls: this.cls,\r\n
                        style: this.style,\r\n
                        value: this.value,\r\n
                        type: this.type,\r\n
                        name: this.name,\r\n
                        placeHolder: this.placeHolder,\r\n
                        spellcheck: this.spellcheck,\r\n
                        scope: me\r\n
                    }));\r\n
                    if (parentEl) {\r\n
                        this.setElement(parentEl, false);\r\n
                        parentEl.html(this.cmpEl);\r\n
                    } else {\r\n
                        $(this.el).html(this.cmpEl);\r\n
                    }\r\n
                } else {\r\n
                    this.cmpEl = $(this.el);\r\n
                }\r\n
                if (!me.rendered) {\r\n
                    var el = this.cmpEl;\r\n
                    this._input = this.cmpEl.find("input").andSelf().filter("input");\r\n
                    if (this.editable) {\r\n
                        this._input.on("blur", _.bind(this.onInputChanged, this));\r\n
                        this._input.on("keypress", _.bind(this.onKeyPress, this));\r\n
                        this._input.on("keyup", _.bind(this.onKeyUp, this));\r\n
                        if (this.validateOnChange) {\r\n
                            this._input.on("input", _.bind(this.onInputChanging, this));\r\n
                        }\r\n
                    }\r\n
                    this.setEditable(this.editable);\r\n
                    if (this.disabled) {\r\n
                        this.setDisabled(this.disabled);\r\n
                    }\r\n
                }\r\n
                me.rendered = true;\r\n
                return this;\r\n
            },\r\n
            _doChange: function (e, extra) {\r\n
                if (extra && extra.synthetic) {\r\n
                    return;\r\n
                }\r\n
                var newValue = $(e.target).val(),\r\n
                oldValue = this.value;\r\n
                this.trigger("changed:before", this, newValue, oldValue, e);\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                this.value = newValue;\r\n
                if (this.validateOnBlur) {\r\n
                    this.checkValidate();\r\n
                }\r\n
                this.trigger("changed:after", this, newValue, oldValue, e);\r\n
            },\r\n
            onInputChanged: function (e, extra) {\r\n
                this._doChange(e, extra);\r\n
            },\r\n
            onInputChanging: function (e, extra) {\r\n
                var newValue = $(e.target).val(),\r\n
                oldValue = this.value;\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                this.value = newValue;\r\n
                if (this.validateOnBlur) {\r\n
                    this.checkValidate();\r\n
                }\r\n
                this.trigger("changing", this, newValue, oldValue, e);\r\n
            },\r\n
            onKeyPress: function (e) {\r\n
                this.trigger("keypress:before", this, e);\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                if (e.keyCode === Common.UI.Keys.RETURN) {\r\n
                    this._doChange(e);\r\n
                } else {\r\n
                    if (this.options.maskExp && !_.isEmpty(this.options.maskExp.source)) {\r\n
                        var charCode = String.fromCharCode(e.which);\r\n
                        if (!this.options.maskExp.test(charCode) && !e.ctrlKey && e.keyCode !== Common.UI.Keys.DELETE && e.keyCode !== Common.UI.Keys.BACKSPACE && e.keyCode !== Common.UI.Keys.LEFT && e.keyCode !== Common.UI.Keys.RIGHT && e.keyCode !== Common.UI.Keys.HOME && e.keyCode !== Common.UI.Keys.END && e.keyCode !== Common.UI.Keys.ESC && e.keyCode !== Common.UI.Keys.INSERT) {\r\n
                            e.preventDefault();\r\n
                            e.stopPropagation();\r\n
                        }\r\n
                    }\r\n
                }\r\n
                this.trigger("keypress:after", this, e);\r\n
            },\r\n
            onKeyUp: function (e) {\r\n
                this.trigger("keyup:before", this, e);\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                this.trigger("keyup:after", this, e);\r\n
            },\r\n
            setEditable: function (editable) {\r\n
                var input = this._input;\r\n
                this.editable = editable;\r\n
                if (editable && input) {\r\n
                    input.removeAttr("readonly");\r\n
                    input.removeAttr("data-can-copy");\r\n
                } else {\r\n
                    input.attr("readonly", "readonly");\r\n
                    input.attr("data-can-copy", false);\r\n
                }\r\n
            },\r\n
            isEditable: function () {\r\n
                return this.editable;\r\n
            },\r\n
            setDisabled: function (disabled) {\r\n
                this.disabled = disabled;\r\n
                $(this.el).toggleClass("disabled", disabled);\r\n
                disabled ? this._input.attr("disabled", true) : this._input.removeAttr("disabled");\r\n
            },\r\n
            isDisabled: function () {\r\n
                return this.disabled;\r\n
            },\r\n
            setValue: function (value) {\r\n
                this.value = value;\r\n
                if (this.rendered) {\r\n
                    this._input.val(value);\r\n
                }\r\n
            },\r\n
            getValue: function () {\r\n
                return this.value;\r\n
            },\r\n
            focus: function () {\r\n
                this._input.focus();\r\n
            },\r\n
            checkValidate: function () {\r\n
                var me = this,\r\n
                errors = [];\r\n
                if (!me.allowBlank && _.isEmpty(me.value)) {\r\n
                    errors.push(me.blankError);\r\n
                }\r\n
                if (_.isFunction(me.validation)) {\r\n
                    var res = me.validation.call(me, me.value);\r\n
                    if (res !== true) {\r\n
                        errors = _.flatten(errors.concat(res));\r\n
                    }\r\n
                }\r\n
                if (!_.isEmpty(errors)) {\r\n
                    me.cmpEl.addClass("error");\r\n
                    var errorBadge = me.cmpEl.find(".input-error"),\r\n
                    modalParents = errorBadge.closest(".asc-window");\r\n
                    errorBadge.attr("data-toggle", "tooltip");\r\n
                    errorBadge.removeData("bs.tooltip");\r\n
                    errorBadge.tooltip({\r\n
                        title: errors.join("\\n"),\r\n
                        placement: "cursor"\r\n
                    });\r\n
                    if (modalParents.length > 0) {\r\n
                        errorBadge.data("bs.tooltip").tip().css("z-index", parseInt(modalParents.css("z-index")) + 10);\r\n
                    }\r\n
                    return errors;\r\n
                } else {\r\n
                    me.cmpEl.removeClass("error");\r\n
                }\r\n
                return true;\r\n
            },\r\n
            showError: function (errors) {\r\n
                var me = this;\r\n
                if (!_.isEmpty(errors)) {\r\n
                    me.cmpEl.addClass("error");\r\n
                    var errorBadge = me.cmpEl.find(".input-error"),\r\n
                    modalParents = errorBadge.closest(".asc-window");\r\n
                    errorBadge.attr("data-toggle", "tooltip");\r\n
                    errorBadge.removeData("bs.tooltip");\r\n
                    errorBadge.tooltip({\r\n
                        title: errors.join("\\n"),\r\n
                        placement: "cursor"\r\n
                    });\r\n
                    if (modalParents.length > 0) {\r\n
                        errorBadge.data("bs.tooltip").tip().css("z-index", parseInt(modalParents.css("z-index")) + 10);\r\n
                    }\r\n
                } else {\r\n
                    me.cmpEl.removeClass("error");\r\n
                }\r\n
            }\r\n
        };\r\n
    })());\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12031</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
