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
            <value> <string>ts44308798.77</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ComboBorderSize.js</string> </value>
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
define(["common/main/lib/component/ComboBox"], function () {\r\n
    Common.UI.BordersModel = Backbone.Model.extend({\r\n
        defaults: function () {\r\n
            return {\r\n
                value: null,\r\n
                displayValue: null,\r\n
                pxValue: null,\r\n
                id: Common.UI.getId(),\r\n
                offsety: undefined\r\n
            };\r\n
        }\r\n
    });\r\n
    Common.UI.BordersStore = Backbone.Collection.extend({\r\n
        model: Common.UI.BordersModel\r\n
    });\r\n
    Common.UI.ComboBorderSize = Common.UI.ComboBox.extend(_.extend({\r\n
        template: _.template([\'<div class="input-group combobox combo-border-size input-group-nr <%= cls %>" id="<%= id %>" style="<%= style %>">\', \'<div class="form-control" style="<%= style %>"></div>\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>\', \'<ul class="dropdown-menu <%= menuCls %>" style="<%= menuStyle %>" role="menu">\', "<% _.each(items, function(item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a tabindex="-1" type="menuitem">\', "<span><%= item.displayValue %></span>", "<% if (item.offsety!==undefined) { %>", \'<img src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" align="right" style="background-position: 0 -<%= item.offsety %>px;">\', "<% } %>", "</a></li>", "<% }); %>", "</ul>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.ComboBox.prototype.initialize.call(this, _.extend({\r\n
                editable: false,\r\n
                store: new Common.UI.BordersStore(),\r\n
                data: [{\r\n
                    displayValue: this.txtNoBorders,\r\n
                    value: 0,\r\n
                    pxValue: 0\r\n
                },\r\n
                {\r\n
                    displayValue: "0.5 pt",\r\n
                    value: 0.5,\r\n
                    pxValue: 0.5,\r\n
                    offsety: 0\r\n
                },\r\n
                {\r\n
                    displayValue: "1 pt",\r\n
                    value: 1,\r\n
                    pxValue: 1,\r\n
                    offsety: 20\r\n
                },\r\n
                {\r\n
                    displayValue: "1.5 pt",\r\n
                    value: 1.5,\r\n
                    pxValue: 2,\r\n
                    offsety: 40\r\n
                },\r\n
                {\r\n
                    displayValue: "2.25 pt",\r\n
                    value: 2.25,\r\n
                    pxValue: 3,\r\n
                    offsety: 60\r\n
                },\r\n
                {\r\n
                    displayValue: "3 pt",\r\n
                    value: 3,\r\n
                    pxValue: 4,\r\n
                    offsety: 80\r\n
                },\r\n
                {\r\n
                    displayValue: "4.5 pt",\r\n
                    value: 4.5,\r\n
                    pxValue: 5,\r\n
                    offsety: 100\r\n
                },\r\n
                {\r\n
                    displayValue: "6 pt",\r\n
                    value: 6,\r\n
                    pxValue: 6,\r\n
                    offsety: 120\r\n
                }],\r\n
                menuStyle: "min-width: 150px;"\r\n
            },\r\n
            options));\r\n
        },\r\n
        render: function (parentEl) {\r\n
            Common.UI.ComboBox.prototype.render.call(this, parentEl);\r\n
            return this;\r\n
        },\r\n
        itemClicked: function (e) {\r\n
            var el = $(e.currentTarget).parent();\r\n
            this._selectedItem = this.store.findWhere({\r\n
                id: el.attr("id")\r\n
            });\r\n
            if (this._selectedItem) {\r\n
                $(".selected", $(this.el)).removeClass("selected");\r\n
                el.addClass("selected");\r\n
                this.updateFormControl(this._selectedItem);\r\n
                this.trigger("selected", this, _.extend({},\r\n
                this._selectedItem.toJSON()), e);\r\n
                e.preventDefault();\r\n
            }\r\n
        },\r\n
        updateFormControl: function (record) {\r\n
            var formcontrol = $(this.el).find(".form-control");\r\n
            if (record.get("value") > 0) {\r\n
                formcontrol[0].innerHTML = "";\r\n
                formcontrol.removeClass("text").addClass("image");\r\n
                formcontrol.css("background-position", "0 -" + record.get("offsety") + "px");\r\n
            } else {\r\n
                formcontrol[0].innerHTML = this.txtNoBorders;\r\n
                formcontrol.removeClass("image").addClass("text");\r\n
            }\r\n
        },\r\n
        setValue: function (value) {\r\n
            this._selectedItem = (value === null || value === undefined) ? undefined : _.find(this.store.models, function (item) {\r\n
                if (value < item.attributes.value + 0.01 && value > item.attributes.value - 0.01) {\r\n
                    return true;\r\n
                }\r\n
            });\r\n
            $(".selected", $(this.el)).removeClass("selected");\r\n
            if (this._selectedItem) {\r\n
                this.updateFormControl(this._selectedItem);\r\n
                $("#" + this._selectedItem.get("id"), $(this.el)).addClass("selected");\r\n
            } else {\r\n
                var formcontrol = $(this.el).find(".form-control");\r\n
                formcontrol[0].innerHTML = "";\r\n
                formcontrol.removeClass("image").addClass("text");\r\n
            }\r\n
        },\r\n
        txtNoBorders: "No Borders"\r\n
    },\r\n
    Common.UI.ComboBorderSize || {}));\r\n
    Common.UI.ComboBorderSizeEditable = Common.UI.ComboBox.extend(_.extend({\r\n
        template: _.template([\'<span class="input-group combobox combo-border-size-editable input-group-nr <%= cls %>" id="<%= id %>" style="<%= style %>">\', \'<input type="text" class="form-control">\', \'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>\', \'<ul class="dropdown-menu <%= menuCls %>" style="<%= menuStyle %>" role="menu">\', "<% _.each(items, function(item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a tabindex="-1" type="menuitem">\', "<span><%= item.displayValue %></span>", "<% if (item.offsety!==undefined) { %>", \'<img src="data:image/gif;base64,R0lGODlhAQABAID/AMDAwAAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==" align="right" style="background-position: 0 -<%= item.offsety %>px;">\', "<% } %>", "</a></li>", "<% }); %>", "</ul>", "</span>"].join("")),\r\n
        initialize: function (options) {\r\n
            this.txtNoBorders = options.txtNoBorders || this.txtNoBorders;\r\n
            Common.UI.ComboBox.prototype.initialize.call(this, _.extend({\r\n
                editable: true,\r\n
                store: new Common.UI.BordersStore(),\r\n
                data: [{\r\n
                    displayValue: this.txtNoBorders,\r\n
                    value: 0,\r\n
                    pxValue: 0\r\n
                },\r\n
                {\r\n
                    displayValue: "0.5 pt",\r\n
                    value: 0.5,\r\n
                    pxValue: 0.5,\r\n
                    offsety: 0\r\n
                },\r\n
                {\r\n
                    displayValue: "1 pt",\r\n
                    value: 1,\r\n
                    pxValue: 1,\r\n
                    offsety: 20\r\n
                },\r\n
                {\r\n
                    displayValue: "1.5 pt",\r\n
                    value: 1.5,\r\n
                    pxValue: 2,\r\n
                    offsety: 40\r\n
                },\r\n
                {\r\n
                    displayValue: "2.25 pt",\r\n
                    value: 2.25,\r\n
                    pxValue: 3,\r\n
                    offsety: 60\r\n
                },\r\n
                {\r\n
                    displayValue: "3 pt",\r\n
                    value: 3,\r\n
                    pxValue: 4,\r\n
                    offsety: 80\r\n
                },\r\n
                {\r\n
                    displayValue: "4.5 pt",\r\n
                    value: 4.5,\r\n
                    pxValue: 5,\r\n
                    offsety: 100\r\n
                },\r\n
                {\r\n
                    displayValue: "6 pt",\r\n
                    value: 6,\r\n
                    pxValue: 6,\r\n
                    offsety: 120\r\n
                }],\r\n
                menuStyle: "min-width: 150px;"\r\n
            },\r\n
            options));\r\n
        },\r\n
        render: function (parentEl) {\r\n
            Common.UI.ComboBox.prototype.render.call(this, parentEl);\r\n
            return this;\r\n
        },\r\n
        txtNoBorders: "No Borders"\r\n
    },\r\n
    Common.UI.ComboBorderSizeEditable || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10027</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
