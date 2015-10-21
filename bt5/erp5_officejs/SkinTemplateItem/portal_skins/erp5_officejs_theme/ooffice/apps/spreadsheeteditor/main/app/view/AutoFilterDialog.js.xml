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
            <value> <string>ts44321337.51</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>AutoFilterDialog.js</string> </value>
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
    SSE.Views.DigitalFilterDialog = Common.UI.Window.extend(_.extend({\r\n
        initialize: function (options) {\r\n
            var t = this,\r\n
            _options = {};\r\n
            _.extend(_options, {\r\n
                width: 500,\r\n
                height: 230,\r\n
                contentWidth: 180,\r\n
                header: true,\r\n
                cls: "filter-dlg",\r\n
                contentTemplate: "",\r\n
                title: t.txtTitle,\r\n
                items: []\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div class="content-panel" >\', \'<label class="header">\', t.textShowRows, "</label>", \'<div style="margin-top:15px;">\', \'<div id="id-search-begin-digital-combo" class="input-group-nr" style="vertical-align:top;width:225px;display:inline-block;"></div>\', \'<div id="id-sd-cell-search-begin" class="" style="width:225px;display:inline-block;margin-left:18px;"></div>\', "</div>", "<div>", \'<div id="id-and-radio" class="padding-small" style="display: inline-block; margin-top:10px;"></div>\', \'<div id="id-or-radio" class="padding-small" style="display: inline-block; margin-left:25px;"></div>\', "</div>", \'<div style="margin-top:10px;">\', \'<div id="id-search-end-digital-combo" class="input-group-nr" style="vertical-align:top;width:225px;display:inline-block;"></div>\', \'<div id="id-sd-cell-search-end" class="" style="width:225px;display:inline-block;margin-left:18px;"></div>\', "</div>", "</div>", "</div>", \'<div class="separator horizontal" style="width:100%"></div>\', \'<div class="footer right" style="margin-left:-15px;">\', \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right:10px;">\', t.okButtonText, "</button>", \'<button class="btn normal dlg-btn" result="cancel">\', t.cancelButtonText, "</button>", "</div>"].join("");\r\n
            this.api = options.api;\r\n
            this.handler = options.handler;\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var conditions = [{\r\n
                value: c_oAscCustomAutoFilter.equals,\r\n
                displayValue: this.capCondition1\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.doesNotEqual,\r\n
                displayValue: this.capCondition2\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.isGreaterThan,\r\n
                displayValue: this.capCondition3\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.isGreaterThanOrEqualTo,\r\n
                displayValue: this.capCondition4\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.isLessThan,\r\n
                displayValue: this.capCondition5\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.isLessThanOrEqualTo,\r\n
                displayValue: this.capCondition6\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.beginsWith,\r\n
                displayValue: this.capCondition7\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.doesNotBeginWith,\r\n
                displayValue: this.capCondition8\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.endsWith,\r\n
                displayValue: this.capCondition9\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.doesNotEndWith,\r\n
                displayValue: this.capCondition10\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.contains,\r\n
                displayValue: this.capCondition11\r\n
            },\r\n
            {\r\n
                value: c_oAscCustomAutoFilter.doesNotContain,\r\n
                displayValue: this.capCondition12\r\n
            }];\r\n
            this.cmbCondition1 = new Common.UI.ComboBox({\r\n
                el: $("#id-search-begin-digital-combo", this.$window),\r\n
                menuStyle: "min-width: 225px;",\r\n
                cls: "input-group-nr",\r\n
                data: conditions,\r\n
                editable: false\r\n
            });\r\n
            this.cmbCondition1.setValue(c_oAscCustomAutoFilter.equals);\r\n
            conditions.splice(0, 0, {\r\n
                value: 0,\r\n
                displayValue: this.textNoFilter\r\n
            });\r\n
            this.cmbCondition2 = new Common.UI.ComboBox({\r\n
                el: $("#id-search-end-digital-combo", this.$window),\r\n
                menuStyle: "min-width: 225px;",\r\n
                cls: "input-group-nr",\r\n
                data: conditions,\r\n
                editable: false\r\n
            });\r\n
            this.cmbCondition2.setValue(0);\r\n
            this.rbAnd = new Common.UI.RadioBox({\r\n
                el: $("#id-and-radio", this.$window),\r\n
                labelText: this.capAnd,\r\n
                name: "asc-radio-filter-tab",\r\n
                checked: true\r\n
            });\r\n
            this.rbOr = new Common.UI.RadioBox({\r\n
                el: $("#id-or-radio", this.$window),\r\n
                labelText: this.capOr,\r\n
                name: "asc-radio-filter-tab"\r\n
            });\r\n
            this.txtValue1 = new Common.UI.InputField({\r\n
                el: $("#id-sd-cell-search-begin", this.$window),\r\n
                template: _.template([\'<div class="input-field" style="<%= style %>">\', "<input ", \'type="<%= type %>" \', \'name="<%= name %>" \', \'class="form-control <%= cls %>" style="float:none" \', \'placeholder="<%= placeHolder %>" \', \'value="<%= value %>"\', ">", "</div>"].join("")),\r\n
                allowBlank: true,\r\n
                validation: function () {\r\n
                    return true;\r\n
                }\r\n
            });\r\n
            this.txtValue2 = new Common.UI.InputField({\r\n
                el: $("#id-sd-cell-search-end", this.$window),\r\n
                template: _.template([\'<div class="input-field" style="<%= style %>">\', "<input ", \'type="<%= type %>" \', \'name="<%= name %>" \', \'class="form-control <%= cls %>" style="float:none" \', \'placeholder="<%= placeHolder %>" \', \'value="<%= value %>"\', ">", "</div>"].join("")),\r\n
                allowBlank: true,\r\n
                validation: function () {\r\n
                    return true;\r\n
                }\r\n
            });\r\n
            this.$window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.loadDefaults();\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.Window.prototype.show.call(this);\r\n
            var me = this;\r\n
            _.defer(function () {\r\n
                if (me.txtValue1) {\r\n
                    me.txtValue1.focus();\r\n
                }\r\n
            },\r\n
            500);\r\n
        },\r\n
        close: function () {\r\n
            if (this.api) {\r\n
                this.api.asc_enableKeyEvents(true);\r\n
            }\r\n
            Common.UI.Window.prototype.close.call(this);\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if (event.currentTarget.attributes && event.currentTarget.attributes.result) {\r\n
                if ("ok" === event.currentTarget.attributes.result.value) {\r\n
                    this.save();\r\n
                }\r\n
                this.close();\r\n
            }\r\n
        },\r\n
        setSettings: function (properties) {\r\n
            this.properties = properties;\r\n
        },\r\n
        loadDefaults: function () {\r\n
            if (this.properties && this.rbOr && this.rbAnd && this.cmbCondition1 && this.cmbCondition2 && this.txtValue1 && this.txtValue2) {\r\n
                (this.properties.asc_getIsChecked()) ? this.rbOr.setValue(true) : this.rbAnd.setValue(true);\r\n
                this.cmbCondition1.setValue(this.properties.asc_getFilter1() || c_oAscCustomAutoFilter.equals);\r\n
                this.cmbCondition2.setValue(this.properties.asc_getFilter2() || 0);\r\n
                this.txtValue1.setValue(null === this.properties.asc_getValFilter1() ? "" : this.properties.asc_getValFilter1());\r\n
                this.txtValue2.setValue(null === this.properties.asc_getValFilter2() ? "" : this.properties.asc_getValFilter2());\r\n
            }\r\n
        },\r\n
        save: function () {\r\n
            if (this.api && this.properties && this.rbOr && this.rbAnd && this.cmbCondition1 && this.cmbCondition2 && this.txtValue1 && this.txtValue2) {\r\n
                var options = new Asc.AutoFiltersOptions();\r\n
                if (options) {\r\n
                    options.asc_setCellId(this.properties.asc_getCellId());\r\n
                    options.asc_setIsChecked(this.rbOr.getValue());\r\n
                    options.asc_setFilter1(this.cmbCondition1.getValue());\r\n
                    options.asc_setFilter2(this.cmbCondition2.getValue() || undefined);\r\n
                    options.asc_setValFilter1(this.txtValue1.getValue());\r\n
                    options.asc_setValFilter2(this.txtValue2.getValue());\r\n
                    this.api.asc_applyAutoFilter("digitalFilter", options);\r\n
                }\r\n
            }\r\n
        },\r\n
        onPrimary: function () {\r\n
            this.save();\r\n
            this.close();\r\n
            return false;\r\n
        },\r\n
        cancelButtonText: "Cancel",\r\n
        capAnd: "And",\r\n
        capCondition1: "equals",\r\n
        capCondition10: "does not end with",\r\n
        capCondition11: "contains",\r\n
        capCondition12: "does not contain",\r\n
        capCondition2: "does not equal",\r\n
        capCondition3: "is greater than",\r\n
        capCondition4: "is greater than or equal to",\r\n
        capCondition5: "is less than",\r\n
        capCondition6: "is less than or equal to",\r\n
        capCondition7: "begins with",\r\n
        capCondition8: "does not begin with",\r\n
        capCondition9: "ends with",\r\n
        capOr: "Or",\r\n
        textNoFilter: "no filter",\r\n
        textShowRows: "Show rows where",\r\n
        textUse1: "Use ? to present any single character",\r\n
        textUse2 : "Use * to present any series of character",\r\n
        txtTitle: "Custom Filter"\r\n
    },\r\n
    SSE.Views.DigitalFilterDialog || {}));\r\n
    SSE.Views.AutoFilterDialog = Common.UI.Window.extend(_.extend({\r\n
        initialize: function (options) {\r\n
            var t = this,\r\n
            _options = {};\r\n
            _.extend(_options, {\r\n
                width: 270,\r\n
                height: 450,\r\n
                contentWidth: 400,\r\n
                header: true,\r\n
                cls: "filter-dlg",\r\n
                contentTemplate: "",\r\n
                title: t.txtTitle,\r\n
                items: []\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box" style="height:\' + (_options.height - 85) + \'px;">\', \'<div class="content-panel">\', \'<div class="">\', \'<div id="id-btn-sort-down" class="btn-placeholder border"></div>\', \'<div id="id-btn-sort-up" class="btn-placeholder border"></div>\', \'<div id="id-checkbox-custom-filter" style="max-width:50px;margin-left:50px;display:inline-block;"></div>\', \'<button class="btn normal dlg-btn primary" result="custom" id="id-btn-custom-filter" style="min-width:120px;">\', t.btnCustomFilter, "</button>", \'<div id="id-sd-cell-search" class="input-row" style="margin-bottom:10px;"></div>\', \'<div class="border-values" style="margin-top:45px;">\', \'<div id="id-dlg-filter-values" class="combo-values"/>\', "</div>", "</div>", "</div>", "</div>", \'<div class="separator horizontal"></div>\', \'<div class="footer center">\', \'<div id="id-apply-filter" style="display: inline-block;"></div>\', \'<button class="btn normal dlg-btn" result="cancel">\', t.cancelButtonText, "</button>", "</div>"].join("");\r\n
            this.api = options.api;\r\n
            this.handler = options.handler;\r\n
            this.throughIndexes = [];\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            var me = this;\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            this.$window.find(".btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.btnOk = new Common.UI.Button({\r\n
                cls: "btn normal dlg-btn primary",\r\n
                caption: this.okButtonText,\r\n
                style: "margin-right:10px;",\r\n
                enableToggle: false,\r\n
                allowDepress: false\r\n
            });\r\n
            if (this.btnOk) {\r\n
                this.btnOk.render($("#id-apply-filter", this.$window));\r\n
                this.btnOk.on("click", _.bind(this.onApplyFilter, this));\r\n
            }\r\n
            this.btnSortDown = new Common.UI.Button({\r\n
                cls: "btn-toolbar btn-toolbar-default border",\r\n
                iconCls: "btn-icon btn-sort-down",\r\n
                pressed: true,\r\n
                enableToggle: true,\r\n
                allowDepress: false\r\n
            });\r\n
            if (this.btnSortDown) {\r\n
                this.btnSortDown.render($("#id-btn-sort-down", this.$window));\r\n
                this.btnSortDown.on("click", _.bind(this.onSortType, this, "ascending"));\r\n
            }\r\n
            this.btnSortUp = new Common.UI.Button({\r\n
                cls: "btn-toolbar btn-toolbar-default border",\r\n
                iconCls: "btn-icon btn-sort-up",\r\n
                pressed: true,\r\n
                enableToggle: true,\r\n
                allowDepress: false\r\n
            });\r\n
            if (this.btnSortUp) {\r\n
                this.btnSortUp.render($("#id-btn-sort-up", this.$window));\r\n
                this.btnSortUp.on("click", _.bind(this.onSortType, this, "descending"));\r\n
            }\r\n
            this.chCustomFilter = new Common.UI.CheckBox({\r\n
                el: $("#id-checkbox-custom-filter", this.$window)\r\n
            });\r\n
            this.chCustomFilter.setDisabled(true);\r\n
            this.btnCustomFilter = new Common.UI.Button({\r\n
                el: $("#id-btn-custom-filter", this.$window)\r\n
            }).on("click", _.bind(this.onShowCustomFilterDialog, this));\r\n
            this.input = new Common.UI.InputField({\r\n
                el: $("#id-sd-cell-search", this.$window),\r\n
                allowBlank: true,\r\n
                placeHolder: this.txtEmpty,\r\n
                style: "margin-top: 10px;",\r\n
                validateOnChange: true,\r\n
                validation: function () {\r\n
                    return true;\r\n
                }\r\n
            }).on("changing", function (input, value) {\r\n
                if (value.length) {\r\n
                    value = value.replace(/([.?*+^$[\\]\\\\(){}|-])/g, "\\\\$1");\r\n
                    me.filter = new RegExp(value, "ig");\r\n
                } else {\r\n
                    me.filter = undefined;\r\n
                }\r\n
                me.setupDataCells();\r\n
            });\r\n
            this.cells = new Common.UI.DataViewStore();\r\n
            this.filterExcludeCells = new Common.UI.DataViewStore();\r\n
            if (this.cells) {\r\n
                this.cellsList = new Common.UI.ListView({\r\n
                    el: $("#id-dlg-filter-values", this.$window),\r\n
                    store: this.cells,\r\n
                    template: _.template([\'<div class="listview inner" style="border:none;"></div>\'].join("")),\r\n
                    itemTemplate: _.template(["<div>", \'<label class="checkbox-indeterminate" style="position:absolute;">\', "<% if (!check) { %>", \'<input type="button"/>\', "<% } else { %>", \'<input type="button" class="checked"/>\', "<% } %>", "</label>", \'<div id="<%= id %>" class="list-item" style="pointer-events:none;margin-left:20px;display:inline-block;"><%= value %></div>\', "</div>"].join(""))\r\n
                });\r\n
                this.cellsList.on("item:select", _.bind(this.onCellCheck, this));\r\n
                this.cellsList.onKeyDown = _.bind(this.onListKeyDown, this);\r\n
            }\r\n
            this.setupListCells();\r\n
        },\r\n
        show: function () {\r\n
            Common.UI.Window.prototype.show.call(this);\r\n
            var me = this;\r\n
            if (this.input) {\r\n
                _.delay(function () {\r\n
                    me.input.$el.find("input").focus();\r\n
                },\r\n
                500, this);\r\n
            }\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            if (event.currentTarget.attributes && event.currentTarget.attributes.result) {\r\n
                if ("cancel" === event.currentTarget.attributes.result.value) {\r\n
                    this.close();\r\n
                }\r\n
            }\r\n
        },\r\n
        onApplyFilter: function () {\r\n
            if (this.testFilter()) {\r\n
                this.save();\r\n
                this.close();\r\n
            }\r\n
        },\r\n
        onSortType: function (type) {\r\n
            if (this.api && this.configTo) {\r\n
                this.api.asc_sortColFilter(type, this.configTo.asc_getCellId());\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onShowCustomFilterDialog: function () {\r\n
            var me = this,\r\n
            dlgDigitalFilter = new SSE.Views.DigitalFilterDialog({\r\n
                api: this.api\r\n
            }).on({\r\n
                "close": function () {\r\n
                    me.close();\r\n
                }\r\n
            });\r\n
            dlgDigitalFilter.setSettings(this.configTo);\r\n
            dlgDigitalFilter.show();\r\n
            this.close();\r\n
        },\r\n
        onCellCheck: function (listView, itemView, record) {\r\n
            if (this.checkCellTrigerBlock) {\r\n
                return;\r\n
            }\r\n
            var target = "",\r\n
            type = "",\r\n
            isLabel = false,\r\n
            bound = null;\r\n
            var event = window.event ? window.event : window._event;\r\n
            if (event) {\r\n
                type = event.target.type;\r\n
                target = $(event.currentTarget).find(".list-item");\r\n
                if (target.length) {\r\n
                    bound = target.get(0).getBoundingClientRect();\r\n
                    if (bound.left < event.clientX && event.clientX < bound.right && bound.top < event.clientY && event.clientY < bound.bottom) {\r\n
                        isLabel = true;\r\n
                    }\r\n
                }\r\n
                if (type === "button" || isLabel) {\r\n
                    this.updateCellCheck(listView, record);\r\n
                    _.delay(function () {\r\n
                        listView.$el.find(".listview").focus();\r\n
                    },\r\n
                    100, this);\r\n
                }\r\n
            }\r\n
        },\r\n
        onListKeyDown: function (e, data) {\r\n
            var record = null,\r\n
            listView = this.cellsList;\r\n
            if (listView.disabled) {\r\n
                return;\r\n
            }\r\n
            if (_.isUndefined(undefined)) {\r\n
                data = e;\r\n
            }\r\n
            if (data.keyCode == Common.UI.Keys.SPACE) {\r\n
                data.preventDefault();\r\n
                data.stopPropagation();\r\n
                this.updateCellCheck(listView, listView.getSelectedRec()[0]);\r\n
            } else {\r\n
                Common.UI.DataView.prototype.onKeyDown.call(this.cellsList, e, data);\r\n
            }\r\n
        },\r\n
        updateCellCheck: function (listView, record) {\r\n
            if (record && listView) {\r\n
                listView.isSuspendEvents = true;\r\n
                if ("1" !== record.get("groupid")) {\r\n
                    var check = !record.get("check");\r\n
                    this.cells.each(function (cell) {\r\n
                        cell.set("check", check);\r\n
                    });\r\n
                } else {\r\n
                    record.set("check", !record.get("check"));\r\n
                }\r\n
                this.chCustomFilter.setValue(false);\r\n
                this.btnOk.setDisabled(false);\r\n
                listView.isSuspendEvents = false;\r\n
                listView.scroller.update({\r\n
                    minScrollbarLength: 40,\r\n
                    alwaysVisibleY: true\r\n
                });\r\n
            }\r\n
        },\r\n
        setSettings: function (config) {\r\n
            this.config = config;\r\n
            this.configTo = config;\r\n
        },\r\n
        setupListCells: function () {\r\n
            function isNumeric(value) {\r\n
                return !isNaN(parseFloat(value)) && isFinite(value);\r\n
            }\r\n
            var me = this,\r\n
            isnumber, value, index = 0,\r\n
            haveUnselectedCell = false,\r\n
            throughIndex = 1,\r\n
            isCustomFilter = (this.configTo.asc_getIsCustomFilter() === true);\r\n
            if (_.isUndefined(this.config)) {\r\n
                return;\r\n
            }\r\n
            this.cells.reset();\r\n
            this.filterExcludeCells.reset();\r\n
            me.cells.push(new Common.UI.DataViewModel({\r\n
                id: ++index,\r\n
                selected: false,\r\n
                allowSelected: true,\r\n
                value: this.textSelectAll,\r\n
                groupid: "0",\r\n
                check: true,\r\n
                throughIndex: 0\r\n
            }));\r\n
            this.throughIndexes.push(true);\r\n
            this.config.asc_getResult().forEach(function (item) {\r\n
                value = item.asc_getVal();\r\n
                isnumber = isNumeric(value);\r\n
                if ("hidden" !== item.asc_getVisible()) {\r\n
                    me.cells.push(new Common.UI.DataViewModel({\r\n
                        id: ++index,\r\n
                        selected: false,\r\n
                        allowSelected: true,\r\n
                        cellvalue: value,\r\n
                        value: isnumber ? value : (value.length > 0 ? value : me.textEmptyItem),\r\n
                        rowvisible: item.asc_getVisible(),\r\n
                        intval: isnumber ? parseFloat(value) : undefined,\r\n
                        strval: !isnumber ? value : "",\r\n
                        groupid: "1",\r\n
                        check: item.asc_getVisible(),\r\n
                        throughIndex: throughIndex\r\n
                    }));\r\n
                    if (!item.asc_getVisible()) {\r\n
                        haveUnselectedCell = true;\r\n
                    }\r\n
                    me.throughIndexes.push(item.asc_getVisible());\r\n
                    ++throughIndex;\r\n
                }\r\n
            });\r\n
            this.checkCellTrigerBlock = true;\r\n
            this.cells.at(0).set("check", !haveUnselectedCell);\r\n
            this.checkCellTrigerBlock = undefined;\r\n
            this.btnSortDown.toggle(false, false);\r\n
            this.btnSortUp.toggle(false, false);\r\n
            var sort = this.config.asc_getSortState();\r\n
            if (sort) {\r\n
                if ("ascending" === sort) {\r\n
                    this.btnSortDown.toggle(true, false);\r\n
                } else {\r\n
                    this.btnSortUp.toggle(true, false);\r\n
                }\r\n
            }\r\n
            this.chCustomFilter.setValue(isCustomFilter);\r\n
            this.btnOk.setDisabled(isCustomFilter);\r\n
            this.cellsList.scroller.update({\r\n
                minScrollbarLength: 40,\r\n
                alwaysVisibleY: true\r\n
            });\r\n
            this.config = undefined;\r\n
        },\r\n
        setupDataCells: function () {\r\n
            function isNumeric(value) {\r\n
                return !isNaN(parseFloat(value)) && isFinite(value);\r\n
            }\r\n
            var me = this,\r\n
            isnumber, value, index = 0,\r\n
            applyfilter = true,\r\n
            throughIndex = 1;\r\n
            this.cells.forEach(function (item) {\r\n
                value = item.get("check");\r\n
                if (_.isUndefined(value)) {\r\n
                    value = false;\r\n
                }\r\n
                me.throughIndexes[parseInt(item.get("throughIndex"))] = item.get("check");\r\n
            });\r\n
            this.cells.reset();\r\n
            this.filterExcludeCells.reset();\r\n
            if (!me.filter) {\r\n
                me.cells.push(new Common.UI.DataViewModel({\r\n
                    id: ++index,\r\n
                    selected: false,\r\n
                    allowSelected: true,\r\n
                    value: this.textSelectAll,\r\n
                    groupid: "0",\r\n
                    check: me.throughIndexes[0],\r\n
                    throughIndex: 0\r\n
                }));\r\n
            }\r\n
            this.configTo.asc_getResult().forEach(function (item) {\r\n
                value = item.asc_getVal();\r\n
                isnumber = isNumeric(value);\r\n
                applyfilter = true;\r\n
                if (me.filter) {\r\n
                    if (null === value.match(me.filter)) {\r\n
                        applyfilter = false;\r\n
                    }\r\n
                }\r\n
                if ("hidden" !== item.asc_getVisible()) {\r\n
                    if (applyfilter) {\r\n
                        me.cells.push(new Common.UI.DataViewModel({\r\n
                            id: ++index,\r\n
                            selected: false,\r\n
                            allowSelected: true,\r\n
                            cellvalue: value,\r\n
                            value: isnumber ? value : (value.length > 0 ? value : me.textEmptyItem),\r\n
                            rowvisible: item.asc_getVisible(),\r\n
                            intval: isnumber ? parseFloat(value) : undefined,\r\n
                            strval: !isnumber ? value : "",\r\n
                            groupid: "1",\r\n
                            check: me.throughIndexes[throughIndex],\r\n
                            throughIndex: throughIndex\r\n
                        }));\r\n
                    } else {\r\n
                        me.filterExcludeCells.push(new Common.UI.DataViewModel({\r\n
                            cellvalue: value\r\n
                        }));\r\n
                    }++throughIndex;\r\n
                }\r\n
            });\r\n
            if (this.cells.length) {\r\n
                this.chCustomFilter.setValue(this.configTo.asc_getIsCustomFilter() === true);\r\n
            }\r\n
            this.cellsList.scroller.update({\r\n
                minScrollbarLength: 40,\r\n
                alwaysVisibleY: true\r\n
            });\r\n
        },\r\n
        testFilter: function () {\r\n
            var me = this,\r\n
            isValid = false;\r\n
            if (this.cells) {\r\n
                this.cells.forEach(function (item) {\r\n
                    if ("1" === item.get("groupid")) {\r\n
                        if (item.get("check")) {\r\n
                            isValid = true;\r\n
                        }\r\n
                    }\r\n
                });\r\n
            }\r\n
            if (!isValid) {\r\n
                Common.UI.warning({\r\n
                    title: this.textWarning,\r\n
                    msg: this.warnNoSelected,\r\n
                    callback: function () {\r\n
                        _.delay(function () {\r\n
                            me.input.$el.find("input").focus();\r\n
                        },\r\n
                        100, this);\r\n
                    }\r\n
                });\r\n
            }\r\n
            return isValid;\r\n
        },\r\n
        save: function () {\r\n
            if (this.api && this.configTo && this.cells && this.filterExcludeCells) {\r\n
                var options = new Asc.AutoFiltersOptions();\r\n
                if (options) {\r\n
                    options.asc_setCellId(this.configTo.asc_getCellId());\r\n
                    var me = this,\r\n
                    result_arr = [],\r\n
                    visibility;\r\n
                    this.cells.forEach(function (item) {\r\n
                        if ("1" === item.get("groupid")) {\r\n
                            if ((visibility = item.get("rowvisible")) !== "hidden") {\r\n
                                visibility = item.get("check");\r\n
                                result_arr.push(new Asc.AutoFiltersOptionsElements(item.get("cellvalue"), visibility));\r\n
                            }\r\n
                        }\r\n
                    });\r\n
                    this.filterExcludeCells.forEach(function (item) {\r\n
                        result_arr.push(new Asc.AutoFiltersOptionsElements(item.get("cellvalue"), false));\r\n
                    });\r\n
                    options.asc_setResult(result_arr);\r\n
                    options.sortState = this.configTo.asc_getSortState();\r\n
                    this.api.asc_applyAutoFilter("mainFilter", options);\r\n
                }\r\n
            }\r\n
        },\r\n
        onPrimary: function () {\r\n
            this.save();\r\n
            this.close();\r\n
            return false;\r\n
        },\r\n
        okButtonText: "Ok",\r\n
        btnCustomFilter: "Custom Filter",\r\n
        textSelectAll: "Select All",\r\n
        txtTitle: "Filter",\r\n
        warnNoSelected: "You must choose at least one value",\r\n
        textWarning: "Warning",\r\n
        cancelButtonText: "Cancel",\r\n
        textEmptyItem: "{Blanks}",\r\n
        txtEmpty: "Enter cell\'s filter"\r\n
    },\r\n
    SSE.Views.AutoFilterDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>30217</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
