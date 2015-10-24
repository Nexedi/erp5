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
            <value> <string>ts44321338.44</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>FormulaDialog.js</string> </value>
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
 define(["common/main/lib/component/Window", "spreadsheeteditor/main/app/collection/FormulaGroups"], function () {\r\n
    SSE.Views = SSE.Views || {};\r\n
    SSE.Views.FormulaDialog = Common.UI.Window.extend(_.extend({\r\n
        applyFunction: undefined,\r\n
        initialize: function (options) {\r\n
            var t = this,\r\n
            _options = {};\r\n
            _.extend(_options, {\r\n
                width: 300,\r\n
                height: 490,\r\n
                contentWidth: 390,\r\n
                header: true,\r\n
                cls: "formula-dlg",\r\n
                contentTemplate: "",\r\n
                title: t.txtTitle,\r\n
                items: []\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div class="content-panel" >\', \'<label class="header">\' + t.textGroupDescription + "</label>", \'<div id="formula-dlg-combo-group" class="input-group-nr" style="margin-top: 10px"/>\', \'<label class="header" style="margin-top:10px">\' + t.textListDescription + "</label>", \'<div id="formula-dlg-combo-functions" class="combo-functions"/>\', \'<label id="formula-dlg-args" style="margin-top: 10px">\' + "</label>", "</div>", "</div>", \'<div class="separator horizontal"/>\', \'<div class="footer center">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;">\' + t.okButtonText + "</button>", \'<button class="btn normal dlg-btn" result="cancel">\' + t.cancelButtonText + "</button>", "</div>"].join("");\r\n
            this.api = options.api;\r\n
            this.formulasGroups = options.formulasGroups;\r\n
            this.handler = options.handler;\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.$window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.syntaxLabel = $("#formula-dlg-args");\r\n
            this.fillFormulasGroups();\r\n
            this.fillFunctions("All");\r\n
        },\r\n
        show: function () {\r\n
            if (this.$window) {\r\n
                var main_width, main_height, top, left, win_height = this.initConfig.height;\r\n
                if (window.innerHeight === undefined) {\r\n
                    main_width = document.documentElement.offsetWidth;\r\n
                    main_height = document.documentElement.offsetHeight;\r\n
                } else {\r\n
                    main_width = window.innerWidth;\r\n
                    main_height = window.innerHeight;\r\n
                }\r\n
                top = ((parseInt(main_height, 10) - parseInt(win_height, 10)) / 2) * 0.9;\r\n
                left = (parseInt(main_width, 10) - parseInt(this.initConfig.width, 10)) / 2;\r\n
                this.$window.css("left", Math.floor(left));\r\n
                this.$window.css("top", Math.floor(top));\r\n
            }\r\n
            Common.UI.Window.prototype.show.call(this);\r\n
            this.mask = $(".modals-mask");\r\n
            this.mask.on("mousedown", _.bind(this.onUpdateFocus, this));\r\n
            this.$window.on("mousedown", _.bind(this.onUpdateFocus, this));\r\n
            if (this.cmbListFunctions) {\r\n
                _.delay(function (me) {\r\n
                    me.cmbListFunctions.$el.find(".listview").focus();\r\n
                },\r\n
                100, this);\r\n
            }\r\n
        },\r\n
        hide: function () {\r\n
            this.mask.off("mousedown", _.bind(this.onUpdateFocus, this));\r\n
            this.$window.off("mousedown", _.bind(this.onUpdateFocus, this));\r\n
            Common.UI.Window.prototype.hide.call(this);\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if ("ok" === event.currentTarget.attributes["result"].value) {\r\n
                if (this.handler) {\r\n
                    this.handler.call(this, this.applyFunction);\r\n
                }\r\n
            }\r\n
            this.hide();\r\n
        },\r\n
        onDblClickFunction: function () {\r\n
            if (this.handler) {\r\n
                this.handler.call(this, this.applyFunction);\r\n
            }\r\n
            this.hide();\r\n
        },\r\n
        onSelectGroup: function (combo, record) {\r\n
            if (!_.isUndefined(record) && !_.isUndefined(record.value)) {\r\n
                if (record.value < this.formulasGroups.length) {\r\n
                    this.fillFunctions(this.formulasGroups.at(record.value).get("name"));\r\n
                }\r\n
            }\r\n
            this.onUpdateFocus();\r\n
        },\r\n
        onSelectFunction: function (listView, itemView, record) {\r\n
            var funcId, functions, func;\r\n
            if (this.formulasGroups) {\r\n
                funcId = record.get("id");\r\n
                if (!_.isUndefined(funcId)) {\r\n
                    functions = this.formulasGroups.at(0).get("functions");\r\n
                    if (functions) {\r\n
                        func = _.find(functions, function (f) {\r\n
                            if (f.get("index") === funcId) {\r\n
                                return f;\r\n
                            }\r\n
                            return null;\r\n
                        });\r\n
                        if (func) {\r\n
                            this.applyFunction = func.get("name");\r\n
                            this.syntaxLabel.text(this.syntaxText + ": " + this.applyFunction + func.get("args"));\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onPrimary: function (list, record, event) {\r\n
            if (this.handler) {\r\n
                this.handler.call(this, this.applyFunction);\r\n
            }\r\n
            this.hide();\r\n
        },\r\n
        onUpdateFocus: function () {\r\n
            _.delay(function (me) {\r\n
                me.cmbListFunctions.$el.find(".listview").focus();\r\n
            },\r\n
            100, this);\r\n
        },\r\n
        fillFormulasGroups: function () {\r\n
            if (this.formulasGroups) {\r\n
                var descriptions = {\r\n
                    "All": this.sCategoryAll,\r\n
                    "Cube": this.sCategoryCube,\r\n
                    "Database": this.sCategoryDatabase,\r\n
                    "DateAndTime": this.sCategoryDateTime,\r\n
                    "Engineering": this.sCategoryEngineering,\r\n
                    "Financial": this.sCategoryFinancial,\r\n
                    "Information": this.sCategoryInformation,\r\n
                    "Logical": this.sCategoryLogical,\r\n
                    "LookupAndReference": this.sCategoryLookupAndReference,\r\n
                    "Mathematic": this.sCategoryMathematics,\r\n
                    "Statistical": this.sCategoryStatistical,\r\n
                    "TextAndData": this.sCategoryTextData\r\n
                };\r\n
                var i, groupsListItems = [],\r\n
                length = this.formulasGroups.length;\r\n
                for (i = 0; i < length; ++i) {\r\n
                    if (this.formulasGroups.at(i).get("functions").length) {\r\n
                        groupsListItems.push({\r\n
                            value: this.formulasGroups.at(i).get("index"),\r\n
                            displayValue: descriptions[this.formulasGroups.at(i).get("name")]\r\n
                        });\r\n
                    }\r\n
                }\r\n
                if (!this.cmbFuncGroup) {\r\n
                    this.cmbFuncGroup = new Common.UI.ComboBox({\r\n
                        el: $("#formula-dlg-combo-group"),\r\n
                        menuStyle: "min-width: 268px;",\r\n
                        cls: "input-group-nr",\r\n
                        data: groupsListItems,\r\n
                        editable: false\r\n
                    });\r\n
                    this.cmbFuncGroup.setValue(0);\r\n
                    this.cmbFuncGroup.on("selected", _.bind(this.onSelectGroup, this));\r\n
                } else {\r\n
                    this.cmbFuncGroup.setData(groupsListItems);\r\n
                }\r\n
            }\r\n
        },\r\n
        fillFunctions: function (name) {\r\n
            if (this.formulasGroups) {\r\n
                if (!this.cmbListFunctions && !this.functions) {\r\n
                    this.functions = new Common.UI.DataViewStore();\r\n
                    this.cmbListFunctions = new Common.UI.ListView({\r\n
                        el: $("#formula-dlg-combo-functions"),\r\n
                        store: this.functions,\r\n
                        itemTemplate: _.template(\'<div id="<%= id %>" class="list-item" style="pointer-events:none;"><%= value %></div>\')\r\n
                    });\r\n
                    this.cmbListFunctions.on("item:select", _.bind(this.onSelectFunction, this));\r\n
                    this.cmbListFunctions.on("item:dblclick", _.bind(this.onDblClickFunction, this));\r\n
                    this.cmbListFunctions.on("entervalue", _.bind(this.onPrimary, this));\r\n
                    this.cmbListFunctions.onKeyDown = _.bind(this.onKeyDown, this.cmbListFunctions);\r\n
                    this.cmbListFunctions.$el.find(".listview").focus();\r\n
                    this.cmbListFunctions.scrollToRecord = _.bind(this.onScrollToRecordCustom, this.cmbListFunctions);\r\n
                }\r\n
                if (this.functions) {\r\n
                    this.functions.reset();\r\n
                    var i = 0,\r\n
                    length = 0,\r\n
                    functions = null,\r\n
                    group = this.formulasGroups.findWhere({\r\n
                        name: name\r\n
                    });\r\n
                    if (group) {\r\n
                        functions = group.get("functions");\r\n
                        if (functions && functions.length) {\r\n
                            length = functions.length;\r\n
                            for (i = 0; i < length; ++i) {\r\n
                                this.functions.push(new Common.UI.DataViewModel({\r\n
                                    id: functions[i].get("index"),\r\n
                                    selected: i < 1,\r\n
                                    allowSelected: true,\r\n
                                    value: functions[i].get("name")\r\n
                                }));\r\n
                            }\r\n
                            this.applyFunction = functions[0].get("name");\r\n
                            this.syntaxLabel.text(this.syntaxText + ": " + this.applyFunction + functions[0].get("args"));\r\n
                            this.cmbListFunctions.scroller.update({\r\n
                                minScrollbarLength: 40,\r\n
                                alwaysVisibleY: true\r\n
                            });\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onKeyDown: function (e, event) {\r\n
            var i = 0,\r\n
            record = null,\r\n
            me = this,\r\n
            charVal = "",\r\n
            value = "",\r\n
            firstRecord = null,\r\n
            recSelect = false,\r\n
            innerEl = null,\r\n
            isEqualSelectRecord = false,\r\n
            selectRecord = null,\r\n
            needNextRecord = false;\r\n
            if (this.disabled) {\r\n
                return;\r\n
            }\r\n
            if (_.isUndefined(undefined)) {\r\n
                event = e;\r\n
            }\r\n
            function selectItem(item) {\r\n
                me.selectRecord(item);\r\n
                me.scrollToRecord(item);\r\n
                innerEl = $(me.el).find(".inner");\r\n
                me.scroller.scrollTop(innerEl.scrollTop(), 0);\r\n
                event.preventDefault();\r\n
                event.stopPropagation();\r\n
            }\r\n
            charVal = String.fromCharCode(e.keyCode);\r\n
            if (e.keyCode > 64 && e.keyCode < 91 && charVal && charVal.length) {\r\n
                selectRecord = this.store.findWhere({\r\n
                    selected: true\r\n
                });\r\n
                if (selectRecord) {\r\n
                    value = selectRecord.get("value");\r\n
                    isEqualSelectRecord = (value && value.length && value[0] === charVal);\r\n
                }\r\n
                for (i = 0; i < this.store.length; ++i) {\r\n
                    record = this.store.at(i);\r\n
                    value = record.get("value");\r\n
                    if (value[0] === charVal) {\r\n
                        if (null === firstRecord) {\r\n
                            firstRecord = record;\r\n
                        }\r\n
                        if (isEqualSelectRecord) {\r\n
                            if (selectRecord === record) {\r\n
                                isEqualSelectRecord = false;\r\n
                            }\r\n
                            continue;\r\n
                        }\r\n
                        if (record.get("selected")) {\r\n
                            continue;\r\n
                        }\r\n
                        selectItem(record);\r\n
                        return;\r\n
                    }\r\n
                }\r\n
                if (firstRecord) {\r\n
                    selectItem(firstRecord);\r\n
                    return;\r\n
                }\r\n
            }\r\n
            Common.UI.DataView.prototype.onKeyDown.call(this, e, event);\r\n
        },\r\n
        onScrollToRecordCustom: function (record) {\r\n
            var innerEl = $(this.el).find(".inner");\r\n
            var inner_top = innerEl.offset().top;\r\n
            var div = innerEl.find("#" + record.get("id")).parent();\r\n
            var div_top = div.offset().top;\r\n
            if (div_top < inner_top || div_top + div.height() > inner_top + innerEl.height()) {\r\n
                if (this.scroller) {\r\n
                    this.scroller.scrollTop(innerEl.scrollTop() + div_top - inner_top, 0);\r\n
                } else {\r\n
                    innerEl.scrollTop(innerEl.scrollTop() + div_top - inner_top);\r\n
                }\r\n
            }\r\n
        },\r\n
        cancelButtonText: "Cancel",\r\n
        okButtonText: "Ok",\r\n
        sCategoryAll: "All",\r\n
        sCategoryLogical: "Logical",\r\n
        sCategoryCube: "Cube",\r\n
        sCategoryDatabase: "Database",\r\n
        sCategoryDateTime: "Date and time",\r\n
        sCategoryEngineering: "Engineering",\r\n
        sCategoryFinancial: "Financial",\r\n
        sCategoryInformation: "Information",\r\n
        sCategoryLookupAndReference: "LookupAndReference",\r\n
        sCategoryMathematics: "Math and trigonometry",\r\n
        sCategoryStatistical: "Statistical",\r\n
        sCategoryTextData: "Text and data",\r\n
        textGroupDescription: "Select Function Group",\r\n
        textListDescription: "Select Function",\r\n
        sDescription: "Description",\r\n
        txtTitle: "Insert Function",\r\n
        syntaxText: "Syntax"\r\n
    },\r\n
    SSE.Views.FormulaDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16091</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
