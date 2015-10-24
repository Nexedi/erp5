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
            <value> <string>ts44308425.03</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>CellEditor.js</string> </value>
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
 define(["core", "spreadsheeteditor/main/app/view/CellEditor"], function (Viewport) {\r\n
    SSE.Controllers.CellEditor = Backbone.Controller.extend({\r\n
        views: ["CellEditor"],\r\n
        events: function () {\r\n
            return {\r\n
                "keyup input#ce-cell-name": _.bind(this.onCellName, this),\r\n
                "keyup textarea#ce-cell-content": _.bind(this.onKeyupCellEditor, this),\r\n
                "blur textarea#ce-cell-content": _.bind(this.onBlurCellEditor, this),\r\n
                "click button#ce-btn-expand": _.bind(this.expandEditorField, this),\r\n
                "click button#ce-func-label": _.bind(this.onInsertFunction, this)\r\n
            };\r\n
        },\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "CellEditor": {},\r\n
                "Viewport": {\r\n
                    "layout:resizedrag": _.bind(this.onLayoutResize, this)\r\n
                }\r\n
            });\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.isCEditorFocused = false;\r\n
            this.api.asc_registerCallback("asc_onSelectionNameChanged", _.bind(this.onApiCellSelection, this));\r\n
            this.api.asc_registerCallback("asc_onEditCell", _.bind(this.onApiEditCell, this));\r\n
            this.api.asc_registerCallback("asc_onСoAuthoringDisconnect", _.bind(this.onApiDisconnect, this));\r\n
            Common.NotificationCenter.on("api:disconnect", _.bind(this.onApiDisconnect, this));\r\n
            Common.NotificationCenter.on("cells:range", _.bind(this.onCellsRange, this));\r\n
            return this;\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            this.editor.$btnfunc[this.mode.isEdit ? "removeClass" : "addClass"]("disabled");\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.editor = this.createView("CellEditor", {\r\n
                el: "#cell-editing-box"\r\n
            }).render();\r\n
            this.bindViewEvents(this.editor, this.events);\r\n
            this.editor.$el.parent().find(".after").css({\r\n
                zIndex: "4"\r\n
            });\r\n
            var me = this;\r\n
            $("#ce-cell-content").keydown(function (e) {\r\n
                if (Common.UI.Keys.RETURN === e.keyCode || Common.UI.Keys.ESC === e.keyCode) {\r\n
                    me.api.asc_enableKeyEvents(true);\r\n
                }\r\n
            });\r\n
        },\r\n
        onApiEditCell: function (state) {\r\n
            if (state == c_oAscCellEditorState.editStart) {\r\n
                this.api.isCellEdited = true;\r\n
            } else {\r\n
                if (state == c_oAscCellEditorState.editEnd) {\r\n
                    this.api.isCellEdited = false;\r\n
                    this.api.isCEditorFocused = false;\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiCellSelection: function (info) {\r\n
            this.editor.updateCellInfo(info);\r\n
        },\r\n
        onApiDisconnect: function () {\r\n
            this.mode.isEdit = false;\r\n
            var controller = this.getApplication().getController("FormulaDialog");\r\n
            if (controller) {\r\n
                controller.hideDialog();\r\n
            }\r\n
            if (!this.mode.isEdit) {\r\n
                $("#ce-func-label", this.editor.el).addClass("disabled");\r\n
            }\r\n
        },\r\n
        onCellsRange: function (status) {\r\n
            var isRangeSelection = (status != c_oAscSelectionDialogType.None);\r\n
            if (isRangeSelection) {\r\n
                this.editor.$cellname.attr("disabled", "disabled");\r\n
                this.editor.$btnfunc["addClass"]("disabled");\r\n
            } else {\r\n
                this.editor.$cellname.removeAttr("disabled");\r\n
                this.editor.$btnfunc["removeClass"]("disabled");\r\n
            }\r\n
        },\r\n
        onLayoutResize: function (o, r) {\r\n
            if (r == "cell:edit") {\r\n
                if (this.editor.$el.height() > 19) {\r\n
                    if (!this.editor.$btnexpand.hasClass("btn-collapse")) {\r\n
                        this.editor.$btnexpand["addClass"]("btn-collapse");\r\n
                    }\r\n
                } else {\r\n
                    this.editor.$btnexpand["removeClass"]("btn-collapse");\r\n
                }\r\n
            }\r\n
        },\r\n
        onCellName: function (e) {\r\n
            if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                var name = this.editor.$cellname.val();\r\n
                if (name && name.length) {\r\n
                    this.api.asc_findCell(name);\r\n
                }\r\n
                Common.NotificationCenter.trigger("edit:complete", this.editor);\r\n
            }\r\n
        },\r\n
        onBlurCellEditor: function () {\r\n
            if (this.api.isCEditorFocused == "clear") {\r\n
                this.api.isCEditorFocused = undefined;\r\n
            } else {\r\n
                if (this.api.isCellEdited) {\r\n
                    this.api.isCEditorFocused = true;\r\n
                }\r\n
            }\r\n
        },\r\n
        onKeyupCellEditor: function (e) {\r\n
            if (e.keyCode == Common.UI.Keys.RETURN && !e.altKey) {\r\n
                this.api.isCEditorFocused = "clear";\r\n
            }\r\n
        },\r\n
        expandEditorField: function () {\r\n
            if (this.editor.$el.height() > 19) {\r\n
                this.editor.keep_height = this.editor.$el.height();\r\n
                this.editor.$el.height(19);\r\n
                this.editor.$btnexpand["removeClass"]("btn-collapse");\r\n
            } else {\r\n
                this.editor.$el.height(this.editor.keep_height || 74);\r\n
                this.editor.$btnexpand["addClass"]("btn-collapse");\r\n
            }\r\n
            Common.NotificationCenter.trigger("layout:changed", "celleditor");\r\n
            Common.NotificationCenter.trigger("edit:complete", this.editor, {\r\n
                restorefocus: true\r\n
            });\r\n
        },\r\n
        onInsertFunction: function () {\r\n
            if (this.mode.isEdit && !this.editor.$btnfunc["hasClass"]("disabled")) {\r\n
                var controller = this.getApplication().getController("FormulaDialog");\r\n
                if (controller) {\r\n
                    $("#ce-func-label", this.editor.el).blur();\r\n
                    this.api.asc_enableKeyEvents(false);\r\n
                    controller.showDialog();\r\n
                }\r\n
            }\r\n
        }\r\n
    });\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>7812</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
