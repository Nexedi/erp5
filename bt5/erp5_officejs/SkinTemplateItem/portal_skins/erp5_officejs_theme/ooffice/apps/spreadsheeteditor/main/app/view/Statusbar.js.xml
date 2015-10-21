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
            <value> <string>ts44321339.63</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Statusbar.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/StatusBar.template", "tip", "common/main/lib/component/TabBar", "common/main/lib/component/Menu", "common/main/lib/component/Window", "common/main/lib/component/ThemeColorPalette"], function (template) {\r\n
    if (SSE.Views.Statusbar) {\r\n
        var RenameDialog = SSE.Views.Statusbar.RenameDialog;\r\n
        var CopyDialog = SSE.Views.Statusbar.CopyDialog;\r\n
    }\r\n
    SSE.Views.Statusbar = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#statusbar",\r\n
        template: _.template(template),\r\n
        events: function () {\r\n
            return {\r\n
                "click #status-btn-tabfirst": _.bind(this.onBtnTabScroll, this, "first"),\r\n
                "click #status-btn-tabback": _.bind(this.onBtnTabScroll, this, "backward"),\r\n
                "click #status-btn-tabnext": _.bind(this.onBtnTabScroll, this, "forward"),\r\n
                "click #status-btn-tablast": _.bind(this.onBtnTabScroll, this, "last")\r\n
            };\r\n
        },\r\n
        api: undefined,\r\n
        initialize: function () {},\r\n
        render: function () {\r\n
            $(this.el).html(this.template());\r\n
            var me = this;\r\n
            this.editMode = false;\r\n
            this.btnZoomDown = new Common.UI.Button({\r\n
                el: $("#status-btn-zoomdown", this.el),\r\n
                hint: this.tipZoomOut + " (Ctrl+-)",\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.btnZoomUp = new Common.UI.Button({\r\n
                el: $("#status-btn-zoomup", this.el),\r\n
                hint: this.tipZoomIn + " (Ctrl++)",\r\n
                hintAnchor: "top-right"\r\n
            });\r\n
            this.btnScrollFirst = new Common.UI.Button({\r\n
                el: $("#status-btn-tabfirst", this.el),\r\n
                hint: this.tipFirst,\r\n
                disabled: true,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.btnScrollBack = new Common.UI.Button({\r\n
                el: $("#status-btn-tabback", this.el),\r\n
                hint: this.tipPrev,\r\n
                disabled: true,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.btnScrollNext = new Common.UI.Button({\r\n
                el: $("#status-btn-tabnext", this.el),\r\n
                hint: this.tipNext,\r\n
                disabled: true,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.btnScrollLast = new Common.UI.Button({\r\n
                el: $("#status-btn-tablast", this.el),\r\n
                hint: this.tipLast,\r\n
                disabled: true,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.btnAddWorksheet = new Common.UI.Button({\r\n
                el: $("#status-btn-addtab", this.el),\r\n
                hint: this.tipAddTab,\r\n
                disabled: true,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.cntZoom = new Common.UI.Button({\r\n
                el: $(".cnt-zoom", this.el),\r\n
                hint: this.tipZoomFactor,\r\n
                hintAnchor: "top"\r\n
            });\r\n
            this.cntZoom.cmpEl.on({\r\n
                "show.bs.dropdown": function () {\r\n
                    _.defer(function () {\r\n
                        me.api.asc_enableKeyEvents(false);\r\n
                        me.cntZoom.cmpEl.find("ul").focus();\r\n
                    },\r\n
                    100);\r\n
                },\r\n
                "hide.bs.dropdown": function () {\r\n
                    _.defer(function () {\r\n
                        me.api.asc_enableKeyEvents(true);\r\n
                    },\r\n
                    100);\r\n
                }\r\n
            });\r\n
            this.zoomMenu = new Common.UI.Menu({\r\n
                style: "margin-top:-5px;",\r\n
                menuAlign: "bl-tl",\r\n
                items: [{\r\n
                    caption: "50%",\r\n
                    value: 50\r\n
                },\r\n
                {\r\n
                    caption: "75%",\r\n
                    value: 75\r\n
                },\r\n
                {\r\n
                    caption: "100%",\r\n
                    value: 100\r\n
                },\r\n
                {\r\n
                    caption: "125%",\r\n
                    value: 125\r\n
                },\r\n
                {\r\n
                    caption: "150%",\r\n
                    value: 150\r\n
                },\r\n
                {\r\n
                    caption: "175%",\r\n
                    value: 175\r\n
                },\r\n
                {\r\n
                    caption: "200%",\r\n
                    value: 200\r\n
                }]\r\n
            });\r\n
            this.zoomMenu.render($(".cnt-zoom", this.el));\r\n
            this.zoomMenu.cmpEl.attr({\r\n
                tabindex: -1\r\n
            });\r\n
            this.labelZoom = $("#status-label-zoom", this.$el);\r\n
            this.panelUsers = $("#status-users-box", this.el);\r\n
            this.panelUsers.find("#status-users-block").on("click", _.bind(this.onUsersClick, this));\r\n
            this.tabBarBox = $("#status-sheets-bar-box", this.el);\r\n
            this.tabbar = new Common.UI.TabBar({\r\n
                el: "#status-sheets-bar",\r\n
                placement: "bottom",\r\n
                draggable: false\r\n
            }).render();\r\n
            this.tabbar.on({\r\n
                "tab:invisible": _.bind(this.onTabInvisible, this),\r\n
                "tab:changed": _.bind(this.onSheetChanged, this),\r\n
                "tab:contextmenu": _.bind(this.onTabMenu, this),\r\n
                "tab:dblclick": _.bind(function () {\r\n
                    if (me.editMode && (me.rangeSelectionMode !== c_oAscSelectionDialogType.Chart) && (me.rangeSelectionMode !== c_oAscSelectionDialogType.FormatTable)) {\r\n
                        me.fireEvent("sheet:changename");\r\n
                    }\r\n
                },\r\n
                this),\r\n
                "tab:move": _.bind(function (tabIndex, index) {\r\n
                    me.tabBarScroll = {\r\n
                        scrollLeft: me.tabbar.scrollX\r\n
                    };\r\n
                    if (_.isUndefined(index) || tabIndex === index) {\r\n
                        return;\r\n
                    }\r\n
                    if (tabIndex < index) {\r\n
                        ++index;\r\n
                    }\r\n
                    me.fireEvent("sheet:move", [false, true, tabIndex, index]);\r\n
                },\r\n
                this)\r\n
            });\r\n
            var menuHiddenItems = new Common.UI.Menu({\r\n
                menuAlign: "tl-tr"\r\n
            });\r\n
            menuHiddenItems.on("item:click", function (obj, item, e) {\r\n
                me.fireEvent("show:hidden", [me, item.value]);\r\n
            });\r\n
            var menuColorItems = new Common.UI.Menu({\r\n
                menuAlign: "tl-tr",\r\n
                cls: "color-tab",\r\n
                items: [{\r\n
                    template: _.template(\'<div id="id-tab-menu-color" style="width: 165px; height: 220px; margin: 10px;"></div>\')\r\n
                },\r\n
                {\r\n
                    template: _.template(\'<a id="id-tab-menu-new-color" style="padding-left:12px;">\' + me.textNewColor + "</a>")\r\n
                }]\r\n
            });\r\n
            function dummyCmp() {\r\n
                return {\r\n
                    isDummy: true,\r\n
                    on: function () {}\r\n
                };\r\n
            }\r\n
            me.mnuTabColor = dummyCmp();\r\n
            this.tabMenu = new Common.UI.Menu({\r\n
                menuAlign: "bl-tl",\r\n
                items: [{\r\n
                    caption: this.itemInsert,\r\n
                    value: "ins"\r\n
                },\r\n
                {\r\n
                    caption: this.itemDelete,\r\n
                    value: "del"\r\n
                },\r\n
                {\r\n
                    caption: this.itemRename,\r\n
                    value: "ren"\r\n
                },\r\n
                {\r\n
                    caption: this.itemCopy,\r\n
                    value: "copy"\r\n
                },\r\n
                {\r\n
                    caption: this.itemMove,\r\n
                    value: "move"\r\n
                },\r\n
                {\r\n
                    caption: this.itemHide,\r\n
                    value: "hide"\r\n
                },\r\n
                {\r\n
                    caption: this.itemHidden,\r\n
                    menu: menuHiddenItems\r\n
                },\r\n
                {\r\n
                    caption: this.itemTabColor,\r\n
                    menu: menuColorItems\r\n
                }]\r\n
            }).on("render:after", function (btn) {\r\n
                var colorVal = $(\'<div class="btn-color-value-line"></div>\');\r\n
                $("button:first-child", btn.cmpEl).append(colorVal);\r\n
                colorVal.css("background-color", btn.currentColor || "transparent");\r\n
                me.mnuTabColor = new Common.UI.ThemeColorPalette({\r\n
                    el: $("#id-tab-menu-color"),\r\n
                    dynamiccolors: 10,\r\n
                    colors: [me.textThemeColors, "-", {\r\n
                        color: "3366FF",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "0000FF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000090",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "660066",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "800000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "FF0000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FF6600",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFF00",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "CCFFCC",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "008000",\r\n
                        effectId: 4\r\n
                    },\r\n
                    "-", {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 3\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 4\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 5\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    {\r\n
                        color: "FFFFFF",\r\n
                        effectId: 2\r\n
                    },\r\n
                    {\r\n
                        color: "000000",\r\n
                        effectId: 1\r\n
                    },\r\n
                    "-", "--", "-", me.textStandartColors, "-", "transparent", "5301B3", "980ABD", "B2275F", "F83D26", "F86A1D", "F7AC16", "F7CA12", "FAFF44", "D6EF39", "-", "--"]\r\n
                });\r\n
                me.mnuTabColor.on("select", function (picker, color) {\r\n
                    me.fireEvent("sheet:setcolor", [color]);\r\n
                });\r\n
            });\r\n
            this.tabbar.$el.append(\'<div class="menu-backdrop" data-toggle="dropdown" style="width:0; height:0;"/>\');\r\n
            this.tabMenu.render(this.tabbar.$el);\r\n
            this.tabMenu.on("show:after", _.bind(this.onTabMenuAfterShow, this));\r\n
            this.tabMenu.on("hide:after", _.bind(this.onTabMenuAfterHide, this));\r\n
            this.tabMenu.on("item:click", _.bind(this.onTabMenuClick, this));\r\n
            this.boxMath = $("#status-math-box", this.el);\r\n
            this.labelSum = $("#status-math-sum", this.boxMath);\r\n
            this.labelCount = $("#status-math-count", this.boxMath);\r\n
            this.labelAverage = $("#status-math-average", this.boxMath);\r\n
            this.boxMath.hide();\r\n
            this.boxZoom = $("#status-zoom-box", this.el);\r\n
            this.boxZoom.find(".separator").css("border-left-color", "transparent");\r\n
            return this;\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
            this.api.asc_registerCallback("asc_onSheetsChanged", _.bind(this.update, this));\r\n
            return this;\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = _.extend({},\r\n
            this.mode, mode);\r\n
            this.btnAddWorksheet.setVisible(this.mode.isEdit);\r\n
            this.btnAddWorksheet.setDisabled(this.mode.isDisconnected);\r\n
        },\r\n
        setVisible: function (visible) {\r\n
            visible ? this.show() : this.hide();\r\n
        },\r\n
        update: function () {\r\n
            var me = this;\r\n
            this.fireEvent("updatesheetsinfo", this);\r\n
            this.tabbar.empty(true);\r\n
            this.tabMenu.items[6].menu.removeAll();\r\n
            this.tabMenu.items[6].hide();\r\n
            this.btnAddWorksheet.setDisabled(true);\r\n
            if (this.api) {\r\n
                var wc = this.api.asc_getWorksheetsCount(),\r\n
                i = -1;\r\n
                var hidentems = [],\r\n
                items = [],\r\n
                tab,\r\n
                locked;\r\n
                var sindex = this.api.asc_getActiveWorksheetIndex();\r\n
                while (++i < wc) {\r\n
                    locked = me.api.asc_isWorksheetLockedOrDeleted(i);\r\n
                    tab = {\r\n
                        sheetindex: i,\r\n
                        active: sindex == i,\r\n
                        label: me.api.asc_getWorksheetName(i),\r\n
                        cls: locked ? "coauth-locked" : "",\r\n
                        isLockTheDrag: locked\r\n
                    };\r\n
                    this.api.asc_isWorksheetHidden(i) ? hidentems.push(tab) : items.push(tab);\r\n
                }\r\n
                if (hidentems.length) {\r\n
                    hidentems.forEach(function (item) {\r\n
                        me.tabMenu.items[6].menu.addItem(new Common.UI.MenuItem({\r\n
                            style: "white-space: pre-wrap",\r\n
                            caption: Common.Utils.String.htmlEncode(item.label),\r\n
                            value: item.sheetindex\r\n
                        }));\r\n
                    });\r\n
                    this.tabMenu.items[6].show();\r\n
                }\r\n
                this.tabbar.add(items);\r\n
                if (!_.isUndefined(this.tabBarScroll)) {\r\n
                    this.tabbar.$bar.scrollLeft(this.tabBarScroll.scrollLeft);\r\n
                    this.tabBarScroll = undefined;\r\n
                } else {\r\n
                    this.tabbar.setTabVisible("last");\r\n
                }\r\n
                this.btnAddWorksheet.setDisabled(me.mode.isDisconnected || me.api.asc_isWorkbookLocked());\r\n
                $("#status-label-zoom").text(Common.Utils.String.format(this.zoomText, Math.floor((this.api.asc_getZoom() + 0.005) * 100)));\r\n
                me.fireEvent("sheet:updateColors", [true]);\r\n
            }\r\n
        },\r\n
        setMathInfo: function (info) {\r\n
            if (info.count > 1) {\r\n
                if (!this.boxMath.is(":visible")) {\r\n
                    this.boxMath.show();\r\n
                }\r\n
                this.labelCount.text(this.textCount + ": " + info.count);\r\n
                this.labelSum.text((info.sum && info.sum.length) ? (this.textSum + ": " + info.sum) : "");\r\n
                this.labelAverage.text((info.average && info.average.length) ? (this.textAverage + ": " + info.average) : "");\r\n
            } else {\r\n
                if (this.boxMath.is(":visible")) {\r\n
                    this.boxMath.hide();\r\n
                }\r\n
            }\r\n
            var me = this;\r\n
            _.delay(function () {\r\n
                me.onTabInvisible(undefined, me.tabbar.checkInvisible(true));\r\n
            },\r\n
            30);\r\n
        },\r\n
        onUsersClick: function () {\r\n
            this.fireEvent("click:users", this);\r\n
        },\r\n
        onSheetChanged: function (o, index, tab) {\r\n
            this.api.asc_showWorksheet(tab.sheetindex);\r\n
            if (this.hasTabInvisible && !this.tabbar.isTabVisible(index)) {\r\n
                this.tabbar.setTabVisible(index);\r\n
            }\r\n
            this.fireEvent("sheet:changed", [this, tab.sheetindex]);\r\n
            this.fireEvent("sheet:updateColors", [true]);\r\n
            Common.NotificationCenter.trigger("comments:updatefilter", {\r\n
                property: "uid",\r\n
                value: new RegExp("^(doc_|sheet" + this.api.asc_getActiveWorksheetId() + "_)")\r\n
            },\r\n
            false);\r\n
        },\r\n
        onTabMenu: function (o, index, tab) {\r\n
            if (this.mode.isEdit && (this.rangeSelectionMode !== c_oAscSelectionDialogType.Chart) && (this.rangeSelectionMode !== c_oAscSelectionDialogType.FormatTable)) {\r\n
                if (tab && tab.sheetindex >= 0) {\r\n
                    var rect = tab.$el.get(0).getBoundingClientRect(),\r\n
                    childPos = tab.$el.offset(),\r\n
                    parentPos = tab.$el.parent().offset();\r\n
                    if (!tab.isActive()) {\r\n
                        this.tabbar.setActive(tab);\r\n
                    }\r\n
                    var issheetlocked = this.api.asc_isWorksheetLockedOrDeleted(tab.sheetindex),\r\n
                    isdoclocked = this.api.asc_isWorkbookLocked();\r\n
                    this.tabMenu.items[0].setDisabled(isdoclocked);\r\n
                    this.tabMenu.items[1].setDisabled(issheetlocked);\r\n
                    this.tabMenu.items[2].setDisabled(issheetlocked);\r\n
                    this.tabMenu.items[3].setDisabled(issheetlocked);\r\n
                    this.tabMenu.items[4].setDisabled(issheetlocked);\r\n
                    this.tabMenu.items[5].setDisabled(issheetlocked);\r\n
                    this.tabMenu.items[6].setDisabled(isdoclocked);\r\n
                    this.tabMenu.items[7].setDisabled(issheetlocked);\r\n
                    this.api.asc_closeCellEditor();\r\n
                    this.api.asc_enableKeyEvents(false);\r\n
                    this.tabMenu.atposition = (function () {\r\n
                        return {\r\n
                            top: rect.top,\r\n
                            left: rect.left - parentPos.left - 2\r\n
                        };\r\n
                    })();\r\n
                    this.tabMenu.hide();\r\n
                    this.tabMenu.show();\r\n
                }\r\n
            }\r\n
        },\r\n
        onTabMenuAfterShow: function (obj) {\r\n
            if (obj.atposition) {\r\n
                obj.setOffset(obj.atposition.left);\r\n
            }\r\n
            this.enableKeyEvents = true;\r\n
        },\r\n
        onTabMenuAfterHide: function () {\r\n
            if (!_.isUndefined(this.enableKeyEvents)) {\r\n
                if (this.api) {\r\n
                    this.api.asc_enableKeyEvents(this.enableKeyEvents);\r\n
                }\r\n
                this.enableKeyEvents = undefined;\r\n
            }\r\n
        },\r\n
        onTabMenuClick: function (o, item) {\r\n
            if (item && this.api) {\r\n
                this.enableKeyEvents = (item.value === "ins" || item.value === "hide");\r\n
            }\r\n
        },\r\n
        onTabInvisible: function (obj, opts) {\r\n
            if (this.btnScrollFirst.isDisabled() !== (!opts.first)) {\r\n
                this.btnScrollFirst.setDisabled(!opts.first);\r\n
                this.btnScrollBack.setDisabled(!opts.first);\r\n
            }\r\n
            if (this.btnScrollNext.isDisabled() !== (!opts.last)) {\r\n
                this.btnScrollNext.setDisabled(!opts.last);\r\n
                this.btnScrollLast.setDisabled(!opts.last);\r\n
            }\r\n
            this.hasTabInvisible = opts.first || opts.last;\r\n
        },\r\n
        onBtnTabScroll: function (action, e) {\r\n
            this.tabbar.setTabVisible(action);\r\n
        },\r\n
        updateTabbarBorders: function () {\r\n
            var right = parseInt(this.boxZoom.css("width")),\r\n
            visible = false;\r\n
            if (this.boxMath.is(":visible")) {\r\n
                right += parseInt(this.boxMath.css("width"));\r\n
                visible = true;\r\n
            }\r\n
            if (this.panelUsers.is(":visible")) {\r\n
                right += parseInt(this.panelUsers.css("width"));\r\n
                visible = true;\r\n
            }\r\n
            this.boxZoom.find(".separator").css("border-left-color", visible ? "" : "transparent");\r\n
            this.tabBarBox.css("right", right + "px");\r\n
        },\r\n
        changeViewMode: function (edit) {\r\n
            if (edit) {\r\n
                this.tabBarBox.css("left", "152px");\r\n
            } else {\r\n
                this.tabBarBox.css("left", "");\r\n
            }\r\n
            this.tabbar.options.draggable = edit;\r\n
            this.editMode = edit;\r\n
        },\r\n
        tipZoomIn: "Zoom In",\r\n
        tipZoomOut: "Zoom Out",\r\n
        tipZoomFactor: "Magnification",\r\n
        tipFirst: "First Sheet",\r\n
        tipLast: "Last Sheet",\r\n
        tipPrev: "Previous Sheet",\r\n
        tipNext: "Next Sheet",\r\n
        tipAddTab: "Add Worksheet",\r\n
        itemInsert: "Insert",\r\n
        itemDelete: "Delete",\r\n
        itemRename: "Rename",\r\n
        itemCopy: "Copy",\r\n
        itemMove: "Move",\r\n
        itemHide: "Hide",\r\n
        itemHidden: "Hidden",\r\n
        itemTabColor: "Tab Color",\r\n
        textThemeColors: "Theme Colors",\r\n
        textStandartColors: "Standart Colors",\r\n
        textNoColor: "No Color",\r\n
        textNewColor: "Add New Custom Color",\r\n
        zoomText: "Zoom {0}%",\r\n
        textSum: "SUM",\r\n
        textCount: "COUNT",\r\n
        textAverage: "AVERAGE"\r\n
    },\r\n
    SSE.Views.Statusbar || {}));\r\n
    SSE.Views.Statusbar.RenameDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            header: false,\r\n
            width: 280,\r\n
            cls: "modal-dlg"\r\n
        },\r\n
        template: \'<div class="box">\' + \'<div class="input-row">\' + "<label><%= label %></label>" + "</div>" + \'<div class="input-row" id="txt-sheet-name" />\' + "</div>" + \'<div class="footer right">\' + \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;"><%= btns.ok %></button>\' + \'<button class="btn normal dlg-btn" result="cancel"><%= btns.cancel %></button>\' + "</div>",\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, options || {},\r\n
            {\r\n
                label: this.labelSheetName,\r\n
                btns: {\r\n
                    ok: this.okButtonText,\r\n
                    cancel: this.cancelButtonText\r\n
                }\r\n
            });\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var $window = this.getChild();\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            this.txtName = new Common.UI.InputField({\r\n
                el: $window.find("#txt-sheet-name"),\r\n
                style: "width:100%;",\r\n
                value: this.options.current,\r\n
                allowBlank: false,\r\n
                validation: _.bind(this.nameValidator, this)\r\n
            });\r\n
            if (this.txtName) {\r\n
                this.txtName.$el.find("input").attr("maxlength", 31);\r\n
                this.txtName.$el.on("keypress", "input[type=text]", _.bind(this.onNameKeyPress, this));\r\n
            }\r\n
        },\r\n
        show: function (x, y) {\r\n
            Common.UI.Window.prototype.show.apply(this, arguments);\r\n
            var edit = this.txtName.$el.find("input");\r\n
            _.delay(function (me) {\r\n
                edit.focus();\r\n
                edit.select();\r\n
            },\r\n
            100, this);\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            this.doClose(event.currentTarget.attributes["result"].value);\r\n
        },\r\n
        doClose: function (res) {\r\n
            if (res == "ok") {\r\n
                if (this.txtName.checkValidate() !== true) {\r\n
                    _.delay(function (me) {\r\n
                        me.txtName.focus();\r\n
                    },\r\n
                    100, this);\r\n
                    return;\r\n
                }\r\n
            }\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, res, this.txtName.getValue());\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onNameKeyPress: function (e) {\r\n
            if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                this.doClose("ok");\r\n
            }\r\n
        },\r\n
        nameValidator: function (value) {\r\n
            if (this.options.names) {\r\n
                var testval = value.toLowerCase();\r\n
                for (var i = this.options.names.length - 1; i >= 0; --i) {\r\n
                    if (this.options.names[i] === testval) {\r\n
                        return this.errNameExists;\r\n
                    }\r\n
                }\r\n
            }\r\n
            if (value.length > 2 && value[0] == \'"\' && value[value.length - 1] == \'"\') {\r\n
                return true;\r\n
            }\r\n
            if (!/[:\\\\\\/\\*\\?\\[\\]\\\']/.test(value)) {\r\n
                return true;\r\n
            }\r\n
            return this.errNameWrongChar;\r\n
        },\r\n
        errNameExists: "Worksheet with such name already exist.",\r\n
        errNameWrongChar: "A sheet name cannot contains characters: \\\\, /, *, ?, [, ], :",\r\n
        labelSheetName: "Sheet Name"\r\n
    },\r\n
    RenameDialog || {}));\r\n
    SSE.Views.Statusbar.CopyDialog = Common.UI.Window.extend(_.extend({\r\n
        options: {\r\n
            width: 270,\r\n
            height: 300,\r\n
            cls: "modal-dlg"\r\n
        },\r\n
        template: \'<div class="box">\' + \'<div class="input-row">\' + "<label><%= label %></label>" + "</div>" + \'<div id="status-list-names" style="height: 170px;"/>\' + "</div>" + \'<div class="footer center">\' + \'<button class="btn normal dlg-btn primary" result="ok" style="margin-right: 10px;"><%= btns.ok %></button>\' + \'<button class="btn normal dlg-btn" result="cancel"><%= btns.cancel %></button>\' + "</div>",\r\n
        initialize: function (options) {\r\n
            _.extend(this.options, options || {},\r\n
            {\r\n
                label: options.ismove ? this.textMoveBefore : this.textCopyBefore,\r\n
                btns: {\r\n
                    ok: this.okButtonText,\r\n
                    cancel: this.cancelButtonText\r\n
                }\r\n
            });\r\n
            this.options.tpl = _.template(this.template, this.options);\r\n
            Common.UI.Window.prototype.initialize.call(this, this.options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var $window = this.getChild();\r\n
            $window.find(".dlg-btn").on("click", _.bind(this.onBtnClick, this));\r\n
            var pages = [];\r\n
            this.options.names.forEach(function (item) {\r\n
                pages.push(new Common.UI.DataViewModel(item));\r\n
            },\r\n
            this);\r\n
            if (pages.length) {\r\n
                pages.push(new Common.UI.DataViewModel({\r\n
                    value: this.options.ismove ? this.itemMoveToEnd : this.itemCopyToEnd,\r\n
                    inindex: -255\r\n
                }));\r\n
            }\r\n
            this.listNames = new Common.UI.ListView({\r\n
                el: $("#status-list-names", $window),\r\n
                store: new Common.UI.DataViewStore(pages),\r\n
                itemTemplate: _.template(\'<div id="<%= id %>" class="list-item" style="pointer-events:none;"><%= Common.Utils.String.htmlEncode(value) %></div>\')\r\n
            });\r\n
            this.listNames.selectByIndex(0);\r\n
            this.listNames.on("entervalue", _.bind(this.onPrimary, this));\r\n
            this.listNames.on("item:dblclick", _.bind(this.onPrimary, this));\r\n
            this.mask = $(".modals-mask");\r\n
            this.mask.on("mousedown", _.bind(this.onUpdateFocus, this));\r\n
        },\r\n
        show: function (x, y) {\r\n
            Common.UI.Window.prototype.show.apply(this, arguments);\r\n
            _.delay(function (me) {\r\n
                me.listNames.$el.find(".listview").focus();\r\n
            },\r\n
            100, this);\r\n
        },\r\n
        hide: function () {\r\n
            Common.UI.Window.prototype.hide.apply(this, arguments);\r\n
            this.mask.off("mousedown", _.bind(this.onUpdateFocus, this));\r\n
        },\r\n
        onBtnClick: function (event) {\r\n
            var active = this.listNames.getSelectedRec();\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, event.currentTarget.attributes["result"].value, active[0].get("inindex"));\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onPrimary: function () {\r\n
            if (this.options.handler) {\r\n
                this.options.handler.call(this, "ok", this.listNames.getSelectedRec()[0].get("inindex"));\r\n
            }\r\n
            this.close();\r\n
        },\r\n
        onUpdateFocus: function () {\r\n
            _.delay(function (me) {\r\n
                me.listNames.$el.find(".listview").focus();\r\n
            },\r\n
            100, this);\r\n
        },\r\n
        itemCopyToEnd: "(Copy to end)",\r\n
        itemMoveToEnd: "(Move to end)",\r\n
        textCopyBefore: "Copy before sheet",\r\n
        textMoveBefore: "Move before sheet"\r\n
    },\r\n
    CopyDialog || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>36243</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
