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
            <value> <string>ts44308800.97</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>TableStyler.js</string> </value>
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
define(["common/main/lib/component/BaseView"], function () {\r\n
    Common.UI.CellStyler = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            clickOffset: 10,\r\n
            overwriteStyle: true,\r\n
            maxBorderSize: 6,\r\n
            halfBorderSize: false,\r\n
            defaultBorderSize: 1,\r\n
            defaultBorderColor: "#ccc"\r\n
        },\r\n
        template: _.template([\'<div id="<%=id%>" class="tablestyler-cell" style="">\', \'<div class="cell-content" style="">\', \'<div class="content-text"></div>\', "</div>", "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            divContent = undefined,\r\n
            virtualBorderSize, virtualBorderColor, borderSize = {},\r\n
            borderColor = {},\r\n
            borderAlfa = {};\r\n
            me.id = me.options.id || Common.UI.getId();\r\n
            me.clickOffset = me.options.clickOffset;\r\n
            me.overwriteStyle = me.options.overwriteStyle;\r\n
            me.maxBorderSize = me.options.maxBorderSize;\r\n
            me.halfBorderSize = me.options.halfBorderSize;\r\n
            me.defaultBorderSize = me.options.defaultBorderSize;\r\n
            me.defaultBorderColor = me.options.defaultBorderColor;\r\n
            me.col = me.options.col;\r\n
            me.row = me.options.row;\r\n
            virtualBorderSize = me.defaultBorderSize;\r\n
            virtualBorderColor = new Common.Utils.RGBColor(me.defaultBorderColor);\r\n
            borderSize = {\r\n
                top: virtualBorderSize,\r\n
                right: virtualBorderSize,\r\n
                bottom: virtualBorderSize,\r\n
                left: virtualBorderSize\r\n
            };\r\n
            borderColor = {\r\n
                top: virtualBorderColor,\r\n
                right: virtualBorderColor,\r\n
                bottom: virtualBorderColor,\r\n
                left: virtualBorderColor\r\n
            };\r\n
            borderAlfa = {\r\n
                top: 1,\r\n
                right: 1,\r\n
                bottom: 1,\r\n
                left: 1\r\n
            };\r\n
            me.rendered = false;\r\n
            var applyStyle = function () {\r\n
                if (!_.isUndefined(divContent)) {\r\n
                    var brd = (borderSize.left > 0.1 && borderSize.left < 1) ? 1 : borderSize.left;\r\n
                    var drawLeftSize = Math.abs((me.halfBorderSize) ? ((brd % 2) ? brd - 1 : brd) * 0.5 : brd);\r\n
                    brd = (borderSize.right > 0.1 && borderSize.right < 1) ? 1 : borderSize.right;\r\n
                    var drawRightSize = Math.abs((me.halfBorderSize) ? ((brd % 2) ? brd + 1 : brd) * 0.5 : brd);\r\n
                    brd = (borderSize.top > 0.1 && borderSize.top < 1) ? 1 : borderSize.top;\r\n
                    var drawTopSize = Math.abs((me.halfBorderSize) ? ((brd % 2) ? brd - 1 : brd) * 0.5 : brd);\r\n
                    brd = (borderSize.bottom > 0.1 && borderSize.bottom < 1) ? 1 : borderSize.bottom;\r\n
                    var drawBottomSize = Math.abs((me.halfBorderSize) ? ((brd % 2) ? brd + 1 : brd) * 0.5 : brd);\r\n
                    var value = "inset " + ((drawLeftSize > 0.1 && drawLeftSize < 1) ? 1 : drawLeftSize) + "px" + " 0" + " 0 " + borderColor.left.toRGBA(borderAlfa.left) + ", " + "inset " + -1 * ((drawRightSize > 0.1 && drawRightSize < 1) ? 1 : drawRightSize) + "px" + " 0" + " 0 " + borderColor.right.toRGBA(borderAlfa.right) + ", " + "inset " + "0 " + ((drawTopSize > 0.1 && drawTopSize < 1) ? 1 : drawTopSize) + "px" + " 0 " + borderColor.top.toRGBA(borderAlfa.top) + ", " + "inset " + "0 " + -1 * ((drawBottomSize > 0.1 && drawBottomSize < 1) ? 1 : drawBottomSize) + "px" + " 0 " + borderColor.bottom.toRGBA(borderAlfa.bottom);\r\n
                    divContent.css("box-shadow", value);\r\n
                }\r\n
            };\r\n
            me.on("render:after", function (cmp) {\r\n
                if (this.cmpEl) {\r\n
                    divContent = this.cmpEl.find(".cell-content");\r\n
                    applyStyle();\r\n
                }\r\n
                this.cmpEl.on("click", function (event) {\r\n
                    var pos = {\r\n
                        x: event.pageX - me.cmpEl.offset().left,\r\n
                        y: event.pageY - me.cmpEl.offset().top\r\n
                    };\r\n
                    var ptInPoly = function (npol, xp, yp, x, y) {\r\n
                        var i, j, c = 0;\r\n
                        for (i = 0, j = npol - 1; i < npol; j = i++) {\r\n
                            if ((((yp[i] <= y) && (y < yp[j])) || ((yp[j] <= y) && (y < yp[i]))) && (x < (xp[j] - xp[i]) * (y - yp[i]) / (yp[j] - yp[i]) + xp[i])) {\r\n
                                c = !c;\r\n
                            }\r\n
                        }\r\n
                        return c;\r\n
                    };\r\n
                    var meWidth = me.cmpEl.outerWidth();\r\n
                    var meHeight = me.cmpEl.outerHeight();\r\n
                    if (ptInPoly(4, [0, meWidth, meWidth - me.clickOffset, me.clickOffset], [0, 0, me.clickOffset, me.clickOffset], pos.x, pos.y)) {\r\n
                        if (me.overwriteStyle) {\r\n
                            if (borderSize.top != virtualBorderSize || !borderColor.top.isEqual(virtualBorderColor)) {\r\n
                                borderSize.top = virtualBorderSize;\r\n
                                borderColor.top = virtualBorderColor;\r\n
                                borderAlfa.top = (virtualBorderSize < 1) ? 0.3 : 1;\r\n
                            } else {\r\n
                                borderSize.top = 0;\r\n
                            }\r\n
                        } else {\r\n
                            borderSize.top = (borderSize.top > 0) ? 0 : virtualBorderSize;\r\n
                            borderColor.top = virtualBorderColor;\r\n
                        }\r\n
                        me.fireEvent("borderclick", me, "t", borderSize.top, borderColor.top.toHex());\r\n
                    } else {\r\n
                        if (ptInPoly(4, [meWidth, meWidth, meWidth - me.clickOffset, meWidth - me.clickOffset], [0, meHeight, meHeight - me.clickOffset, me.clickOffset], pos.x, pos.y)) {\r\n
                            if (me.overwriteStyle) {\r\n
                                if (borderSize.right != virtualBorderSize || !borderColor.right.isEqual(virtualBorderColor)) {\r\n
                                    borderSize.right = virtualBorderSize;\r\n
                                    borderColor.right = virtualBorderColor;\r\n
                                    borderAlfa.right = (virtualBorderSize < 1) ? 0.3 : 1;\r\n
                                } else {\r\n
                                    borderSize.right = 0;\r\n
                                }\r\n
                            } else {\r\n
                                borderSize.right = (borderSize.right > 0) ? 0 : virtualBorderSize;\r\n
                                borderColor.right = virtualBorderColor;\r\n
                            }\r\n
                            me.fireEvent("borderclick", me, "r", borderSize.right, borderColor.right.toHex());\r\n
                        } else {\r\n
                            if (ptInPoly(4, [0, me.clickOffset, meWidth - me.clickOffset, meWidth], [meHeight, meHeight - me.clickOffset, meHeight - me.clickOffset, meHeight], pos.x, pos.y)) {\r\n
                                if (me.overwriteStyle) {\r\n
                                    if (borderSize.bottom != virtualBorderSize || !borderColor.bottom.isEqual(virtualBorderColor)) {\r\n
                                        borderSize.bottom = virtualBorderSize;\r\n
                                        borderColor.bottom = virtualBorderColor;\r\n
                                        borderAlfa.bottom = (virtualBorderSize < 1) ? 0.3 : 1;\r\n
                                    } else {\r\n
                                        borderSize.bottom = 0;\r\n
                                    }\r\n
                                } else {\r\n
                                    borderSize.bottom = (borderSize.bottom > 0) ? 0 : virtualBorderSize;\r\n
                                    borderColor.bottom = virtualBorderColor;\r\n
                                }\r\n
                                me.fireEvent("borderclick", me, "b", borderSize.bottom, borderColor.bottom.toHex());\r\n
                            } else {\r\n
                                if (ptInPoly(4, [0, me.clickOffset, me.clickOffset, 0], [0, me.clickOffset, meHeight - me.clickOffset, meHeight], pos.x, pos.y)) {\r\n
                                    if (me.overwriteStyle) {\r\n
                                        if (borderSize.left != virtualBorderSize || !borderColor.left.isEqual(virtualBorderColor)) {\r\n
                                            borderSize.left = virtualBorderSize;\r\n
                                            borderColor.left = virtualBorderColor;\r\n
                                            borderAlfa.left = (virtualBorderSize < 1) ? 0.3 : 1;\r\n
                                        } else {\r\n
                                            borderSize.left = 0;\r\n
                                        }\r\n
                                    } else {\r\n
                                        borderSize.left = (borderSize.left > 0) ? 0 : virtualBorderSize;\r\n
                                        borderColor.left = virtualBorderColor;\r\n
                                    }\r\n
                                    me.fireEvent("borderclick", me, "l", borderSize.left, borderColor.left.toHex());\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    applyStyle();\r\n
                });\r\n
            });\r\n
            me.setBordersSize = function (borders, size) {\r\n
                size = (size > this.maxBorderSize) ? this.maxBorderSize : size;\r\n
                if (borders.indexOf("t") > -1) {\r\n
                    borderSize.top = size;\r\n
                    borderAlfa.top = (size < 1) ? 0.3 : 1;\r\n
                }\r\n
                if (borders.indexOf("r") > -1) {\r\n
                    borderSize.right = size;\r\n
                    borderAlfa.right = (size < 1) ? 0.3 : 1;\r\n
                }\r\n
                if (borders.indexOf("b") > -1) {\r\n
                    borderSize.bottom = size;\r\n
                    borderAlfa.bottom = (size < 1) ? 0.3 : 1;\r\n
                }\r\n
                if (borders.indexOf("l") > -1) {\r\n
                    borderSize.left = size;\r\n
                    borderAlfa.left = (size < 1) ? 0.3 : 1;\r\n
                }\r\n
                applyStyle();\r\n
            };\r\n
            me.setBordersColor = function (borders, color) {\r\n
                var newColor = new Common.Utils.RGBColor(color);\r\n
                if (borders.indexOf("t") > -1) {\r\n
                    borderColor.top = newColor;\r\n
                }\r\n
                if (borders.indexOf("r") > -1) {\r\n
                    borderColor.right = newColor;\r\n
                }\r\n
                if (borders.indexOf("b") > -1) {\r\n
                    borderColor.bottom = newColor;\r\n
                }\r\n
                if (borders.indexOf("l") > -1) {\r\n
                    borderColor.left = newColor;\r\n
                }\r\n
                applyStyle();\r\n
            };\r\n
            me.getBorderSize = function (border) {\r\n
                switch (border) {\r\n
                case "t":\r\n
                    return borderSize.top;\r\n
                case "r":\r\n
                    return borderSize.right;\r\n
                case "b":\r\n
                    return borderSize.bottom;\r\n
                case "l":\r\n
                    return borderSize.left;\r\n
                }\r\n
                return null;\r\n
            };\r\n
            me.getBorderColor = function (border) {\r\n
                switch (border) {\r\n
                case "t":\r\n
                    return borderColor.top.toHex();\r\n
                case "r":\r\n
                    return borderColor.right.toHex();\r\n
                case "b":\r\n
                    return borderColor.bottom.toHex();\r\n
                case "l":\r\n
                    return borderColor.left.toHex();\r\n
                }\r\n
                return null;\r\n
            };\r\n
            me.setVirtualBorderSize = function (size) {\r\n
                virtualBorderSize = (size > this.maxBorderSize) ? this.maxBorderSize : size;\r\n
            };\r\n
            me.setVirtualBorderColor = function (color) {\r\n
                var newColor = new Common.Utils.RGBColor(color);\r\n
                if (virtualBorderColor.isEqual(newColor)) {\r\n
                    return;\r\n
                }\r\n
                virtualBorderColor = newColor;\r\n
            };\r\n
            me.getVirtualBorderSize = function () {\r\n
                return virtualBorderSize;\r\n
            };\r\n
            me.getVirtualBorderColor = function () {\r\n
                return virtualBorderColor.toHex();\r\n
            };\r\n
            if (me.options.el) {\r\n
                me.render();\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this;\r\n
            this.trigger("render:before", this);\r\n
            if (!me.rendered) {\r\n
                this.cmpEl = $(this.template({\r\n
                    id: this.id\r\n
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
            me.rendered = true;\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        }\r\n
    });\r\n
    Common.UI.TableStyler = Common.UI.BaseView.extend({\r\n
        options: {\r\n
            width: 200,\r\n
            height: 200,\r\n
            rows: 2,\r\n
            columns: 2,\r\n
            cellPadding: 10,\r\n
            tablePadding: 10,\r\n
            overwriteStyle: true,\r\n
            maxBorderSize: 6,\r\n
            spacingMode: false,\r\n
            defaultBorderSize: 1,\r\n
            defaultBorderColor: "#ccc"\r\n
        },\r\n
        template: _.template([\'<div id="<%=scope.id%>" class="table-styler" style="position: relative; width: <%=scope.width%>px; height:<%=scope.height%>px;">\', \'<div style="position: absolute; left: 0; top: 0; width: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px; border-bottom: 1px dotted gray; border-right: 1px dotted gray;"></div>\', \'<div style="position: absolute; left: <%=scope.tablePadding%>px; top: 0; right: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px;">\', \'<div id="<%=scope.id%>-table-top-border-selector" style="position: absolute; z-index: 1; height: <%=scope.tablePadding%>px; left: 0; right: 0; top:  <%=scope.tablePadding * .5%>px;">\', \'<table width="100%" height="100%">\', "<tr>", \'<td id="<%=scope.id%>-table-top-border" style="height:50%; border-bottom: <%=borderSize.top%>px solid <%borderColor.top.toHex()%>;"></td>\', "</tr>", "<tr>", "<td></td>", "</tr>", "</table>", "</div>", "</div>", \'<div style="position: absolute; top: 0; right: 0; width: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px; border-bottom: 1px dotted gray; border-left: 1px dotted gray;"></div>\', \'<div style="position: absolute; left: 0; top: <%=scope.tablePadding%>px; width: <%=scope.tablePadding%>px; height: <%=scope.height - 2 * scope.tablePadding%>px;">\', \'<div id="<%=scope.id%>-table-left-border-selector" style="position: absolute; z-index: 1; left: <%=scope.tablePadding * .5%>px; top: 0; bottom: 0; width: <%=scope.tablePadding%>px;">\', \'<table width="100%" height="100%">\', "<tr>", \'<td id="<%=scope.id%>-table-left-border" style="border-right: <%=borderSize.left%>px solid <%=borderColor.left.toHex()%>;"></td>\', \'<td width="50%"></td>\', "</tr>", "</table>", "</div>", "</div>", \'<div style="position: absolute; left: <%=scope.tablePadding%>px; top: <%=scope.tablePadding%>px; right: <%=scope.tablePadding%>px; bottom: <%=scope.tablePadding%>px;">\', \'<table cols="<%=scope.columns%>" width="100%" height="100%" style="border-collapse: inherit; border-spacing: <%= scope.spacingMode ? scope.cellPadding : 0 %>px;">\', "<% for (var row = 0; row < scope.rows; row++) { %>", "<tr>", "<% for (var col = 0; col < scope.columns; col++) { %>", \'<td id="<%=scope.id%>-cell-container-<%=col%>-<%=row%>" class="content-box"></td>\', "<% } %>", "</tr>", "<% } %>", "</table>", "</div>", \'<div style="position: absolute; right: 0; top: <%=scope.tablePadding%>px; width: <%=scope.tablePadding%>px; height: <%=scope.height - 2 * scope.tablePadding%>px;">\', \'<div id="<%=scope.id%>-table-right-border-selector" style="position: absolute; z-index: 1; right: <%=scope.tablePadding * .5%>px; top: 0; bottom: 0; width: <%=scope.tablePadding%>px;">\', \'<table width="100%" height="100%">\', "<tr>", \'<td id="<%=scope.id%>-table-right-border" style="border-right: <%=borderSize.right%>px solid <%=borderColor.right.toHex()%>;"></td>\', \'<td width="50%"></td>\', "</tr>", "</table>", "</div>", "</div>", \'<div style="position: absolute; left: 0; bottom: 0; width: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px; border-top: 1pt dotted gray; border-right: 1pt dotted gray;"></div>\', \'<div style="position: absolute; left: <%=scope.tablePadding%>px; bottom: 0; right: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px;">\', \'<div id="<%=scope.id%>-table-bottom-border-selector" style="position: absolute; z-index: 1; height: <%=scope.tablePadding%>px; left: 0; right: 0; bottom:  <%=scope.tablePadding * .5%>px;">\', \'<table width="100%" height="100%">\', "<tr>", \'<td id="<%=scope.id%>-table-bottom-border" style="height:50%; border-bottom: <%=borderSize.bottom%>px solid <%=borderColor.bottom.toHex()%>;"></td>\', "</tr>", "<tr>", "<td></td>", "</tr>", "</table>", "</div>", "</div>", \'<div style="position: absolute; bottom: 0; right: 0; width: <%=scope.tablePadding%>px; height: <%=scope.tablePadding%>px; border-top: 1pt dotted gray; border-left: 1pt dotted gray;"></div>\', "</div>"].join("")),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            var me = this,\r\n
            topBorder, rightBorder, bottomBorder, leftBorder, topBorderSelector, rightBorderSelector, bottomBorderSelector, leftBorderSelector, virtualBorderSize, virtualBorderColor;\r\n
            me.id = me.options.id || Common.UI.getId();\r\n
            me.width = me.options.width;\r\n
            me.height = me.options.height;\r\n
            me.rows = me.options.rows;\r\n
            me.columns = me.options.columns;\r\n
            me.cellPadding = me.options.cellPadding;\r\n
            me.tablePadding = me.options.tablePadding;\r\n
            me.overwriteStyle = me.options.overwriteStyle;\r\n
            me.maxBorderSize = me.options.maxBorderSize;\r\n
            me.spacingMode = me.options.spacingMode;\r\n
            me.defaultBorderSize = me.options.defaultBorderSize;\r\n
            me.defaultBorderColor = me.options.defaultBorderColor;\r\n
            virtualBorderSize = (me.defaultBorderSize > me.maxBorderSize) ? me.maxBorderSize : me.defaultBorderSize;\r\n
            virtualBorderColor = new Common.Utils.RGBColor(me.defaultBorderColor);\r\n
            var borderSize = {\r\n
                top: virtualBorderSize,\r\n
                right: virtualBorderSize,\r\n
                bottom: virtualBorderSize,\r\n
                left: virtualBorderSize\r\n
            };\r\n
            var borderColor = {\r\n
                top: virtualBorderColor,\r\n
                right: virtualBorderColor,\r\n
                bottom: virtualBorderColor,\r\n
                left: virtualBorderColor\r\n
            };\r\n
            me.rendered = false;\r\n
            var applyStyles = function () {\r\n
                topBorder && topBorder.css("border-bottom", ((borderSize.top > 0.1 && borderSize.top < 1) ? 1 : borderSize.top) + "px solid " + borderColor.top.toRGBA((borderSize.top < 1) ? 0.2 : 1));\r\n
                rightBorder && rightBorder.css("border-right", ((borderSize.right > 0.1 && borderSize.right < 1) ? 1 : borderSize.right) + "px solid " + borderColor.right.toRGBA((borderSize.right < 1) ? 0.2 : 1));\r\n
                bottomBorder && bottomBorder.css("border-bottom", ((borderSize.bottom > 0.1 && borderSize.bottom < 1) ? 1 : borderSize.bottom) + "px solid " + borderColor.bottom.toRGBA((borderSize.bottom < 1) ? 0.2 : 1));\r\n
                leftBorder && leftBorder.css("border-right", ((borderSize.left > 0.1 && borderSize.left < 1) ? 1 : borderSize.left) + "px solid " + borderColor.left.toRGBA((borderSize.left < 1) ? 0.2 : 1));\r\n
                redraw(topBorderSelector);\r\n
                redraw(rightBorderSelector);\r\n
                redraw(bottomBorderSelector);\r\n
                redraw(leftBorderSelector);\r\n
            };\r\n
            var redraw = function (el) {\r\n
                return el.hide(0, function () {\r\n
                    $(this).show();\r\n
                });\r\n
            };\r\n
            me.on("render:after", function (cmp) {\r\n
                var meId = me.id;\r\n
                topBorder = $("#" + meId + "-table-top-border");\r\n
                rightBorder = $("#" + meId + "-table-right-border");\r\n
                bottomBorder = $("#" + meId + "-table-bottom-border");\r\n
                leftBorder = $("#" + meId + "-table-left-border");\r\n
                topBorderSelector = $("#" + meId + "-table-top-border-selector");\r\n
                rightBorderSelector = $("#" + meId + "-table-right-border-selector");\r\n
                bottomBorderSelector = $("#" + meId + "-table-bottom-border-selector");\r\n
                leftBorderSelector = $("#" + meId + "-table-left-border-selector");\r\n
                topBorderSelector.on("click", function (e) {\r\n
                    if (me.overwriteStyle) {\r\n
                        if (borderSize.top != virtualBorderSize || !borderColor.top.isEqual(virtualBorderColor)) {\r\n
                            borderSize.top = virtualBorderSize;\r\n
                            borderColor.top = virtualBorderColor;\r\n
                        } else {\r\n
                            borderSize.top = 0;\r\n
                        }\r\n
                    } else {\r\n
                        borderSize.top = (borderSize.top > 0) ? 0 : virtualBorderSize;\r\n
                        borderColor.top = virtualBorderColor;\r\n
                    }\r\n
                    topBorder.css("border-bottom", ((borderSize.top > 0.1 && borderSize.top < 1) ? 1 : borderSize.top) + "px solid " + borderColor.top.toRGBA((borderSize.top < 1) ? 0.2 : 1));\r\n
                    redraw(topBorderSelector);\r\n
                    me.fireEvent("borderclick", me, "t", borderSize.top, borderColor.top.toHex());\r\n
                });\r\n
                rightBorderSelector.on("click", function (e) {\r\n
                    if (me.overwriteStyle) {\r\n
                        if (borderSize.right != virtualBorderSize || !borderColor.right.isEqual(virtualBorderColor)) {\r\n
                            borderSize.right = virtualBorderSize;\r\n
                            borderColor.right = virtualBorderColor;\r\n
                        } else {\r\n
                            borderSize.right = 0;\r\n
                        }\r\n
                    } else {\r\n
                        borderSize.right = (borderSize.right > 0) ? 0 : virtualBorderSize;\r\n
                        borderColor.right = virtualBorderColor;\r\n
                    }\r\n
                    rightBorder.css("border-right", ((borderSize.right > 0.1 && borderSize.right < 1) ? 1 : borderSize.right) + "px solid " + borderColor.right.toRGBA((borderSize.right < 1) ? 0.2 : 1));\r\n
                    redraw(rightBorderSelector);\r\n
                    me.fireEvent("borderclick", me, "r", borderSize.right, borderColor.right.toHex());\r\n
                });\r\n
                bottomBorderSelector.on("click", function (e) {\r\n
                    if (me.overwriteStyle) {\r\n
                        if (borderSize.bottom != virtualBorderSize || !borderColor.bottom.isEqual(virtualBorderColor)) {\r\n
                            borderSize.bottom = virtualBorderSize;\r\n
                            borderColor.bottom = virtualBorderColor;\r\n
                        } else {\r\n
                            borderSize.bottom = 0;\r\n
                        }\r\n
                    } else {\r\n
                        borderSize.bottom = (borderSize.bottom > 0) ? 0 : virtualBorderSize;\r\n
                        borderColor.bottom = virtualBorderColor;\r\n
                    }\r\n
                    bottomBorder.css("border-bottom", ((borderSize.bottom > 0.1 && borderSize.bottom < 1) ? 1 : borderSize.bottom) + "px solid " + borderColor.bottom.toRGBA((borderSize.bottom < 1) ? 0.2 : 1));\r\n
                    redraw(bottomBorderSelector);\r\n
                    me.fireEvent("borderclick", me, "b", borderSize.bottom, borderColor.bottom.toHex());\r\n
                });\r\n
                leftBorderSelector.on("click", function (e) {\r\n
                    if (me.overwriteStyle) {\r\n
                        if (borderSize.left != virtualBorderSize || !borderColor.left.isEqual(virtualBorderColor)) {\r\n
                            borderSize.left = virtualBorderSize;\r\n
                            borderColor.left = virtualBorderColor;\r\n
                        } else {\r\n
                            borderSize.left = 0;\r\n
                        }\r\n
                    } else {\r\n
                        borderSize.left = (borderSize.left > 0) ? 0 : virtualBorderSize;\r\n
                        borderColor.left = virtualBorderColor;\r\n
                    }\r\n
                    leftBorder.css("border-right", ((borderSize.left > 0.1 && borderSize.left < 1) ? 1 : borderSize.left) + "px solid " + borderColor.left.toRGBA((borderSize.left < 1) ? 0.2 : 1));\r\n
                    redraw(leftBorderSelector);\r\n
                    me.fireEvent("borderclick", me, "l", borderSize.left, borderColor.left.toHex());\r\n
                });\r\n
            });\r\n
            me.getVirtualBorderSize = function () {\r\n
                return virtualBorderSize;\r\n
            };\r\n
            me.getVirtualBorderColor = function () {\r\n
                return virtualBorderColor.toHex();\r\n
            };\r\n
            me.setVirtualBorderSize = function (size) {\r\n
                size = (size > me.maxBorderSize) ? me.maxBorderSize : size;\r\n
                virtualBorderSize = size;\r\n
                for (var row = 0; row < me.rows; row++) {\r\n
                    for (var col = 0; col < me.columns; col++) {\r\n
                        var cell = me.getCell(col, row);\r\n
                        cell.setVirtualBorderSize(size);\r\n
                    }\r\n
                }\r\n
            };\r\n
            me.setVirtualBorderColor = function (color) {\r\n
                var newColor = new Common.Utils.RGBColor(color);\r\n
                if (virtualBorderColor.isEqual(newColor)) {\r\n
                    return;\r\n
                }\r\n
                virtualBorderColor = newColor;\r\n
                for (var row = 0; row < me.rows; row++) {\r\n
                    for (var col = 0; col < me.columns; col++) {\r\n
                        var cell = me.getCell(col, row);\r\n
                        cell.setVirtualBorderColor(virtualBorderColor.toHex());\r\n
                    }\r\n
                }\r\n
            };\r\n
            me.setBordersSize = function (borders, size) {\r\n
                size = (size > me.maxBorderSize) ? me.maxBorderSize : size;\r\n
                if (borders.indexOf("t") > -1) {\r\n
                    borderSize.top = size;\r\n
                }\r\n
                if (borders.indexOf("r") > -1) {\r\n
                    borderSize.right = size;\r\n
                }\r\n
                if (borders.indexOf("b") > -1) {\r\n
                    borderSize.bottom = size;\r\n
                }\r\n
                if (borders.indexOf("l") > -1) {\r\n
                    borderSize.left = size;\r\n
                }\r\n
                applyStyles();\r\n
            };\r\n
            me.setBordersColor = function (borders, color) {\r\n
                var newColor = new Common.Utils.RGBColor(color);\r\n
                if (borders.indexOf("t") > -1) {\r\n
                    borderColor.top = newColor;\r\n
                }\r\n
                if (borders.indexOf("r") > -1) {\r\n
                    borderColor.right = newColor;\r\n
                }\r\n
                if (borders.indexOf("b") > -1) {\r\n
                    borderColor.bottom = newColor;\r\n
                }\r\n
                if (borders.indexOf("l") > -1) {\r\n
                    borderColor.left = newColor;\r\n
                }\r\n
                applyStyles();\r\n
            };\r\n
            me.getBorderSize = function (border) {\r\n
                switch (border) {\r\n
                case "t":\r\n
                    return borderSize.top;\r\n
                case "r":\r\n
                    return borderSize.right;\r\n
                case "b":\r\n
                    return borderSize.bottom;\r\n
                case "l":\r\n
                    return borderSize.left;\r\n
                }\r\n
                return null;\r\n
            };\r\n
            me.getBorderColor = function (border) {\r\n
                switch (border) {\r\n
                case "t":\r\n
                    return borderColor.top.toHex();\r\n
                case "r":\r\n
                    return borderColor.right.toHex();\r\n
                case "b":\r\n
                    return borderColor.bottom.toHex();\r\n
                case "l":\r\n
                    return borderColor.left.toHex();\r\n
                }\r\n
                return null;\r\n
            };\r\n
            if (me.options.el) {\r\n
                me.render(null, {\r\n
                    borderSize: borderSize,\r\n
                    borderColor: borderColor,\r\n
                    virtualBorderSize: virtualBorderSize,\r\n
                    virtualBorderColor: virtualBorderColor\r\n
                });\r\n
            }\r\n
        },\r\n
        render: function (parentEl) {\r\n
            var me = this,\r\n
            cfg = arguments[1];\r\n
            this.trigger("render:before", this);\r\n
            if (!me.rendered) {\r\n
                this.cmpEl = $(this.template(_.extend({\r\n
                    scope: me\r\n
                },\r\n
                cfg)));\r\n
                if (parentEl) {\r\n
                    this.setElement(parentEl, false);\r\n
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
                this._cells = [];\r\n
                for (var row = 0; row < me.rows; row++) {\r\n
                    for (var col = 0; col < me.columns; col++) {\r\n
                        var cellStyler = new Common.UI.CellStyler({\r\n
                            el: $("#" + me.id + "-cell-container-" + col + "-" + row),\r\n
                            overwriteStyle: me.overwriteStyle,\r\n
                            halfBorderSize: !me.spacingMode,\r\n
                            defaultBorderSize: me.spacingMode ? cfg.virtualBorderSize : 0,\r\n
                            defaultBorderColor: cfg.virtualBorderColor.toHex(),\r\n
                            id: me.id + "-cell-" + col + "-" + row,\r\n
                            col: col,\r\n
                            row: row\r\n
                        });\r\n
                        this._cells.push(cellStyler);\r\n
                        cellStyler.on("borderclick", function (cell, type, size, color) {\r\n
                            var cellCol, cellRow, curCell;\r\n
                            if (type == "t") {\r\n
                                if (cell.row > 0) {\r\n
                                    for (cellCol = 0; cellCol < me.columns; cellCol++) {\r\n
                                        curCell = me.getCell(cellCol, cell.row - 1);\r\n
                                        curCell.setBordersSize("b", size);\r\n
                                        curCell.setBordersColor("b", color);\r\n
                                    }\r\n
                                }\r\n
                                for (cellCol = 0; cellCol < me.columns; cellCol++) {\r\n
                                    curCell = me.getCell(cellCol, cell.row);\r\n
                                    if (cell.halfBorderSize && cell.row < 1) {\r\n
                                        curCell.setBordersSize("t", 0);\r\n
                                    } else {\r\n
                                        curCell.setBordersSize("t", size);\r\n
                                    }\r\n
                                    curCell.setBordersColor("t", color);\r\n
                                }\r\n
                            } else {\r\n
                                if (type == "b") {\r\n
                                    if (cell.row < me.rows - 1) {\r\n
                                        for (cellCol = 0; cellCol < me.columns; cellCol++) {\r\n
                                            curCell = me.getCell(cellCol, cell.row + 1);\r\n
                                            curCell.setBordersSize("t", size);\r\n
                                            curCell.setBordersColor("t", color);\r\n
                                        }\r\n
                                    }\r\n
                                    for (cellCol = 0; cellCol < me.columns; cellCol++) {\r\n
                                        curCell = me.getCell(cellCol, cell.row);\r\n
                                        if (cell.halfBorderSize && cell.row >= me.rows - 1) {\r\n
                                            curCell.setBordersSize("b", 0);\r\n
                                        } else {\r\n
                                            curCell.setBordersSize("b", size);\r\n
                                        }\r\n
                                        curCell.setBordersColor("b", color);\r\n
                                    }\r\n
                                } else {\r\n
                                    if (type == "l") {\r\n
                                        if (cell.col > 0) {\r\n
                                            for (cellRow = 0; cellRow < me.rows; cellRow++) {\r\n
                                                curCell = me.getCell(cell.col - 1, cellRow);\r\n
                                                curCell.setBordersSize("r", size);\r\n
                                                curCell.setBordersColor("r", color);\r\n
                                            }\r\n
                                        }\r\n
                                        for (cellRow = 0; cellRow < me.rows; cellRow++) {\r\n
                                            curCell = me.getCell(cell.col, cellRow);\r\n
                                            if (cell.halfBorderSize && cell.col < 1) {\r\n
                                                curCell.setBordersSize("l", 0);\r\n
                                            } else {\r\n
                                                curCell.setBordersSize("l", size);\r\n
                                            }\r\n
                                            curCell.setBordersColor("l", color);\r\n
                                        }\r\n
                                    } else {\r\n
                                        if (type == "r") {\r\n
                                            if (cell.col < me.columns - 1) {\r\n
                                                for (cellRow = 0; cellRow < me.rows; cellRow++) {\r\n
                                                    curCell = me.getCell(cell.col + 1, cellRow);\r\n
                                                    curCell.setBordersSize("l", size);\r\n
                                                    curCell.setBordersColor("l", color);\r\n
                                                }\r\n
                                            }\r\n
                                            for (cellRow = 0; cellRow < me.rows; cellRow++) {\r\n
                                                curCell = me.getCell(cell.col, cellRow);\r\n
                                                if (cell.halfBorderSize && cell.col >= me.columns - 1) {\r\n
                                                    curCell.setBordersSize("r", 0);\r\n
                                                } else {\r\n
                                                    curCell.setBordersSize("r", size);\r\n
                                                }\r\n
                                                curCell.setBordersColor("r", color);\r\n
                                            }\r\n
                                        }\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        });\r\n
                    }\r\n
                }\r\n
            }\r\n
            me.rendered = true;\r\n
            this.trigger("render:after", this);\r\n
            return this;\r\n
        },\r\n
        getCell: function (col, row) {\r\n
            return _.findWhere(this._cells, {\r\n
                id: this.id + "-cell-" + col + "-" + row\r\n
            });\r\n
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
            <value> <int>38485</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
