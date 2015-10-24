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
            <value> <string>ts44308798.95</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ComboBoxFonts.js</string> </value>
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
var FONT_TYPE_RECENT = 4;\r\n
define(["common/main/lib/component/ComboBox"], function () {\r\n
    Common.UI.ComboBoxFonts = Common.UI.ComboBox.extend((function () {\r\n
        var iconWidth = 302,\r\n
        iconHeight = FONT_THUMBNAIL_HEIGHT || 26,\r\n
        isRetina = window.devicePixelRatio > 1,\r\n
        thumbCanvas = document.createElement("canvas"),\r\n
        thumbContext = thumbCanvas.getContext("2d"),\r\n
        thumbPath = "../../../sdk/Common/Images/fonts_thumbnail.png",\r\n
        thumbPath2x = "../../../sdk/Common/Images/fonts_thumbnail@2x.png",\r\n
        listItemHeight = 36;\r\n
        if (typeof window["AscDesktopEditor"] === "object") {\r\n
            thumbPath = window["AscDesktopEditor"].getFontsSprite();\r\n
            thumbPath2x = window["AscDesktopEditor"].getFontsSprite(true);\r\n
        }\r\n
        thumbCanvas.height = isRetina ? iconHeight * 2 : iconHeight;\r\n
        thumbCanvas.width = isRetina ? iconWidth * 2 : iconWidth;\r\n
        return {\r\n
            template: _.template([\'<div class="input-group combobox fonts <%= cls %>" id="<%= id %>" style="<%= style %>">\', \'<input type="text" class="form-control">\', \'<div style="display: table-cell;"></div>\', \'<button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>\', \'<ul class="dropdown-menu <%= menuCls %>" style="<%= menuStyle %>" role="menu">\', \'<li class="divider">\', "<% _.each(items, function(item) { %>", \'<li id="<%= item.id %>">\', \'<a class="font-item" tabindex="-1" type="menuitem" style="vertical-align:middle; margin: 0 0 0 -10px; height:<%=scope.getListItemHeight()%>px;"/>\', "</li>", "<% }); %>", "</ul>", "</div>"].join("")),\r\n
            initialize: function (options) {\r\n
                Common.UI.ComboBox.prototype.initialize.call(this, _.extend(options, {\r\n
                    displayField: "name"\r\n
                }));\r\n
                this.recent = _.isNumber(options.recent) ? options.recent : 3;\r\n
                this.bindUpdateVisibleFontsTiles = _.bind(this.updateVisibleFontsTiles, this);\r\n
                Common.NotificationCenter.on("fonts:change", _.bind(this.onApiChangeFont, this));\r\n
                Common.NotificationCenter.on("fonts:load", _.bind(this.fillFonts, this));\r\n
            },\r\n
            render: function (parentEl) {\r\n
                var oldRawValue = null;\r\n
                if (!_.isUndefined(this._input)) {\r\n
                    oldRawValue = this._input.val();\r\n
                }\r\n
                Common.UI.ComboBox.prototype.render.call(this, parentEl);\r\n
                this.setRawValue(oldRawValue);\r\n
                this._input.on("keyup", _.bind(this.onInputKeyUp, this));\r\n
                this._input.on("keydown", _.bind(this.onInputKeyDown, this));\r\n
                this.scroller.update({\r\n
                    alwaysVisibleY: true,\r\n
                    onChange: this.bindUpdateVisibleFontsTiles\r\n
                });\r\n
                return this;\r\n
            },\r\n
            onAfterKeydownMenu: function (e) {\r\n
                var me = this;\r\n
                if (e.keyCode == Common.UI.Keys.RETURN) {\r\n
                    if ($(e.target).closest("input").length) {\r\n
                        if (this.lastValue !== this._input.val()) {\r\n
                            this._input.trigger("change");\r\n
                        }\r\n
                    } else {\r\n
                        $(e.target).click();\r\n
                        if (this.rendered) {\r\n
                            if (Common.Utils.isIE) {\r\n
                                this._input.trigger("change", {\r\n
                                    onkeydown: true\r\n
                                });\r\n
                            } else {\r\n
                                this._input.blur();\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    return false;\r\n
                } else {\r\n
                    if (e.keyCode == Common.UI.Keys.ESC && this.isMenuOpen()) {\r\n
                        this._input.val(this.lastValue);\r\n
                        setTimeout(function () {\r\n
                            me.closeMenu();\r\n
                            me.onAfterHideMenu(e);\r\n
                        },\r\n
                        10);\r\n
                        return false;\r\n
                    } else {\r\n
                        if ((e.keyCode == Common.UI.Keys.HOME || e.keyCode == Common.UI.Keys.END || e.keyCode == Common.UI.Keys.BACKSPACE) && this.isMenuOpen()) {\r\n
                            setTimeout(function () {\r\n
                                me._input.focus();\r\n
                            },\r\n
                            10);\r\n
                        }\r\n
                    }\r\n
                }\r\n
                this.updateVisibleFontsTiles();\r\n
            },\r\n
            onInputKeyUp: function (e) {\r\n
                if (e.keyCode != Common.UI.Keys.RETURN && e.keyCode !== Common.UI.Keys.SHIFT && e.keyCode !== Common.UI.Keys.CTRL && e.keyCode !== Common.UI.Keys.ALT && e.keyCode !== Common.UI.Keys.LEFT && e.keyCode !== Common.UI.Keys.RIGHT && e.keyCode !== Common.UI.Keys.HOME && e.keyCode !== Common.UI.Keys.END && e.keyCode !== Common.UI.Keys.ESC && e.keyCode !== Common.UI.Keys.INSERT && e.keyCode !== Common.UI.Keys.TAB) {\r\n
                    e.stopPropagation();\r\n
                    this.selectCandidate(e.keyCode == Common.UI.Keys.DELETE || e.keyCode == Common.UI.Keys.BACKSPACE);\r\n
                    if (this._selectedItem) {\r\n
                        var me = this;\r\n
                        setTimeout(function () {\r\n
                            var input = me._input[0],\r\n
                            text = me._selectedItem.get(me.displayField),\r\n
                            inputVal = input.value;\r\n
                            if (me.rendered) {\r\n
                                if (document.selection) {\r\n
                                    document.selection.createRange().text = text;\r\n
                                } else {\r\n
                                    if (input.selectionStart || input.selectionStart == "0") {\r\n
                                        input.value = text;\r\n
                                        input.selectionStart = inputVal.length;\r\n
                                        input.selectionEnd = text.length;\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        },\r\n
                        10);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onInputKeyDown: function (e) {\r\n
                var me = this;\r\n
                if (e.keyCode == Common.UI.Keys.ESC) {\r\n
                    this._input.val(this.lastValue);\r\n
                    setTimeout(function () {\r\n
                        me.closeMenu();\r\n
                        me.onAfterHideMenu(e);\r\n
                    },\r\n
                    10);\r\n
                } else {\r\n
                    if (e.keyCode != Common.UI.Keys.RETURN && e.keyCode != Common.UI.Keys.CTRL && e.keyCode != Common.UI.Keys.SHIFT && e.keyCode != Common.UI.Keys.ALT) {\r\n
                        if (!this.isMenuOpen()) {\r\n
                            this.openMenu();\r\n
                        }\r\n
                        if (e.keyCode == Common.UI.Keys.UP || e.keyCode == Common.UI.Keys.DOWN) {\r\n
                            _.delay(function () {\r\n
                                var selected = me.cmpEl.find("ul li.selected a");\r\n
                                if (selected.length <= 0) {\r\n
                                    selected = me.cmpEl.find("ul li:not(.divider):first a");\r\n
                                }\r\n
                                me._skipInputChange = true;\r\n
                                selected.focus();\r\n
                                me.updateVisibleFontsTiles();\r\n
                            },\r\n
                            10);\r\n
                        } else {\r\n
                            me._skipInputChange = false;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            },\r\n
            onInputChanged: function (e, extra) {\r\n
                if (extra && extra.synthetic) {\r\n
                    return;\r\n
                }\r\n
                if (this._skipInputChange) {\r\n
                    this._skipInputChange = false;\r\n
                    return;\r\n
                }\r\n
                if (this._isMouseDownMenu) {\r\n
                    this._isMouseDownMenu = false;\r\n
                    return;\r\n
                }\r\n
                var val = $(e.target).val(),\r\n
                record = {};\r\n
                if (this.lastValue === val) {\r\n
                    if (extra && extra.onkeydown) {\r\n
                        this.trigger("combo:blur", this, e);\r\n
                    }\r\n
                    return;\r\n
                }\r\n
                record[this.valueField] = val;\r\n
                record[this.displayField] = val;\r\n
                this.trigger("changed:before", this, record, e);\r\n
                if (e.isDefaultPrevented()) {\r\n
                    return;\r\n
                }\r\n
                if (this._selectedItem) {\r\n
                    record[this.valueField] = this._selectedItem.get(this.displayField);\r\n
                    this.setRawValue(record[this.valueField]);\r\n
                    this.trigger("selected", this, _.extend({},\r\n
                    this._selectedItem.toJSON()), e);\r\n
                    this.addItemToRecent(this._selectedItem);\r\n
                    this.closeMenu();\r\n
                } else {\r\n
                    this.setRawValue(record[this.valueField]);\r\n
                    record["isNewFont"] = true;\r\n
                    this.trigger("selected", this, record, e);\r\n
                    this.closeMenu();\r\n
                }\r\n
                this.trigger("changed:after", this, record, e);\r\n
            },\r\n
            getImageUri: function (opts) {\r\n
                if (opts.cloneid) {\r\n
                    var img = $(this.el).find("ul > li#" + opts.cloneid + " img");\r\n
                    return img != null ? img[0].src : undefined;\r\n
                }\r\n
                if (isRetina) {\r\n
                    thumbContext.clearRect(0, 0, iconWidth * 2, iconHeight * 2);\r\n
                    thumbContext.drawImage(this.spriteThumbs, 0, -FONT_THUMBNAIL_HEIGHT * 2 * opts.imgidx);\r\n
                } else {\r\n
                    thumbContext.clearRect(0, 0, iconWidth, iconHeight);\r\n
                    thumbContext.drawImage(this.spriteThumbs, 0, -FONT_THUMBNAIL_HEIGHT * opts.imgidx);\r\n
                }\r\n
                return thumbCanvas.toDataURL();\r\n
            },\r\n
            getImageWidth: function () {\r\n
                return iconWidth;\r\n
            },\r\n
            getImageHeight: function () {\r\n
                return iconHeight;\r\n
            },\r\n
            getListItemHeight: function () {\r\n
                return listItemHeight;\r\n
            },\r\n
            loadSprite: function (callback) {\r\n
                if (callback) {\r\n
                    this.spriteThumbs = new Image();\r\n
                    this.spriteThumbs.onload = callback;\r\n
                    this.spriteThumbs.src = (window.devicePixelRatio > 1) ? thumbPath2x : thumbPath;\r\n
                }\r\n
            },\r\n
            fillFonts: function (store, select) {\r\n
                var me = this;\r\n
                this.loadSprite(function () {\r\n
                    me.store.set(store.toJSON());\r\n
                    me.rendered = false;\r\n
                    me.render($(me.el));\r\n
                    me._fontsArray = me.store.toJSON();\r\n
                    if (me.recent > 0) {\r\n
                        me.store.on("add", me.onInsertItem, me);\r\n
                        me.store.on("remove", me.onRemoveItem, me);\r\n
                    }\r\n
                });\r\n
            },\r\n
            onApiChangeFont: function (font) {\r\n
                var name = (_.isFunction(font.get_Name) ? font.get_Name() : font.asc_getName());\r\n
                if (this.getRawValue() !== name) {\r\n
                    var record = this.store.findWhere({\r\n
                        name: name\r\n
                    });\r\n
                    $(".selected", $(this.el)).removeClass("selected");\r\n
                    if (record) {\r\n
                        this.setRawValue(record.get(this.displayField));\r\n
                        var itemNode = $("#" + record.get("id"), $(this.el)),\r\n
                        menuNode = $("ul.dropdown-menu", this.cmpEl);\r\n
                        if (itemNode && menuNode) {\r\n
                            itemNode.addClass("selected");\r\n
                            if (this.recent <= 0) {\r\n
                                menuNode.scrollTop(itemNode.offset().top - menuNode.offset().top);\r\n
                            }\r\n
                        }\r\n
                    } else {\r\n
                        this.setRawValue(name);\r\n
                    }\r\n
                }\r\n
            },\r\n
            itemClicked: function (e) {\r\n
                var el = $(e.target).closest("li");\r\n
                var record = this.store.findWhere({\r\n
                    id: el.attr("id")\r\n
                });\r\n
                this.addItemToRecent(record);\r\n
                Common.UI.ComboBox.prototype.itemClicked.apply(this, arguments);\r\n
            },\r\n
            onInsertItem: function (item) {\r\n
                $(this.el).find("ul").prepend(_.template([\'<li id="<%= item.id %>">\', \'<a class="font-item" tabindex="-1" type="menuitem" style="vertical-align:middle; margin: 0 0 0 -10px; height:<%=scope.getListItemHeight()%>px;"/>\', "</li>"].join(""), {\r\n
                    item: item.attributes,\r\n
                    scope: this\r\n
                }));\r\n
            },\r\n
            onRemoveItem: function (item, store, opts) {\r\n
                $(this.el).find("ul > li#" + item.id).remove();\r\n
            },\r\n
            onBeforeShowMenu: function (e) {\r\n
                Common.UI.ComboBox.prototype.onBeforeShowMenu.apply(this, arguments);\r\n
                if (!this.getSelectedRecord() && !!this.getRawValue()) {\r\n
                    var record = this.store.where({\r\n
                        name: this.getRawValue()\r\n
                    });\r\n
                    if (record && record.length) {\r\n
                        this.selectRecord(record[record.length - 1]);\r\n
                    }\r\n
                }\r\n
            },\r\n
            onAfterShowMenu: function (e) {\r\n
                if (this.recent > 0) {\r\n
                    if (this.scroller && !this._scrollerIsInited) {\r\n
                        this.scroller.update();\r\n
                        this._scrollerIsInited = true;\r\n
                    }\r\n
                    $(this.el).find("ul").scrollTop(0);\r\n
                    this.trigger("show:after", this, e);\r\n
                } else {\r\n
                    Common.UI.ComboBox.prototype.onAfterShowMenu.apply(this, arguments);\r\n
                }\r\n
                this.flushVisibleFontsTiles();\r\n
                this.updateVisibleFontsTiles(null, 0);\r\n
            },\r\n
            onAfterHideMenu: function (e) {\r\n
                if (this.lastValue !== this._input.val()) {\r\n
                    this._input.val(this.lastValue);\r\n
                }\r\n
                Common.UI.ComboBox.prototype.onAfterHideMenu.apply(this, arguments);\r\n
            },\r\n
            addItemToRecent: function (record) {\r\n
                if (record.get("type") != FONT_TYPE_RECENT && !this.store.findWhere({\r\n
                    name: record.get("name"),\r\n
                    type: FONT_TYPE_RECENT\r\n
                })) {\r\n
                    var fonts = this.store.where({\r\n
                        type: FONT_TYPE_RECENT\r\n
                    });\r\n
                    if (! (fonts.length < this.recent)) {\r\n
                        this.store.remove(fonts[this.recent - 1]);\r\n
                    }\r\n
                    var new_record = record.clone();\r\n
                    new_record.set({\r\n
                        "type": FONT_TYPE_RECENT,\r\n
                        "id": Common.UI.getId(),\r\n
                        cloneid: record.id\r\n
                    });\r\n
                    this.store.add(new_record, {\r\n
                        at: 0\r\n
                    });\r\n
                }\r\n
            },\r\n
            selectCandidate: function (full) {\r\n
                var me = this,\r\n
                inputVal = this._input.val().toLowerCase();\r\n
                if (!this._fontsArray) {\r\n
                    this._fontsArray = this.store.toJSON();\r\n
                }\r\n
                var font = _.find(this._fontsArray, function (font) {\r\n
                    return (full) ? (font[me.displayField].toLowerCase() == inputVal) : (font[me.displayField].toLowerCase().indexOf(inputVal) == 0);\r\n
                });\r\n
                if (font) {\r\n
                    this._selectedItem = this.store.findWhere({\r\n
                        id: font.id\r\n
                    });\r\n
                } else {\r\n
                    this._selectedItem = null;\r\n
                }\r\n
                $(".selected", $(this.el)).removeClass("selected");\r\n
                if (this._selectedItem) {\r\n
                    var itemNode = $("#" + this._selectedItem.get("id"), $(this.el)),\r\n
                    menuEl = $("ul[role=menu]", $(this.el));\r\n
                    if (itemNode.length > 0 && menuEl.length > 0) {\r\n
                        itemNode.addClass("selected");\r\n
                        var itemTop = itemNode.position().top,\r\n
                        menuTop = menuEl.scrollTop();\r\n
                        if (itemTop != 0) {\r\n
                            menuEl.scrollTop(menuTop + itemTop);\r\n
                        }\r\n
                    }\r\n
                }\r\n
            },\r\n
            updateVisibleFontsTiles: function (e, scrollY) {\r\n
                var me = this,\r\n
                j = 0,\r\n
                storeCount = me.store.length,\r\n
                index = 0;\r\n
                if (!me.tiles) {\r\n
                    me.tiles = [];\r\n
                }\r\n
                if (storeCount !== me.tiles.length) {\r\n
                    for (j = me.tiles.length; j < storeCount; ++j) {\r\n
                        me.tiles.push(null);\r\n
                    }\r\n
                }\r\n
                if (_.isUndefined(scrollY)) {\r\n
                    scrollY = parseInt($(me.el).find(".ps-scrollbar-x-rail").css("bottom"));\r\n
                }\r\n
                var scrollH = $(me.el).find(".dropdown-menu").height(),\r\n
                count = Math.max(Math.floor(scrollH / listItemHeight) + 3, 0),\r\n
                from = Math.max(Math.floor(-(scrollY / listItemHeight)) - 1, 0),\r\n
                to = from + count;\r\n
                var listItems = $(me.el).find("a");\r\n
                for (j = 0; j < storeCount; ++j) {\r\n
                    if (from <= j && j < to) {\r\n
                        if (null === me.tiles[j]) {\r\n
                            var fontImage = document.createElement("canvas");\r\n
                            var context = fontImage.getContext("2d");\r\n
                            fontImage.height = isRetina ? iconHeight * 2 : iconHeight;\r\n
                            fontImage.width = isRetina ? iconWidth * 2 : iconWidth;\r\n
                            fontImage.style.width = iconWidth + "px";\r\n
                            fontImage.style.height = iconHeight + "px";\r\n
                            index = me.store.at(j).get("imgidx");\r\n
                            if (isRetina) {\r\n
                                context.clearRect(0, 0, iconWidth * 2, iconHeight * 2);\r\n
                                context.drawImage(me.spriteThumbs, 0, -FONT_THUMBNAIL_HEIGHT * 2 * index);\r\n
                            } else {\r\n
                                context.clearRect(0, 0, iconWidth, iconHeight);\r\n
                                context.drawImage(me.spriteThumbs, 0, -FONT_THUMBNAIL_HEIGHT * index);\r\n
                            }\r\n
                            me.tiles[j] = fontImage;\r\n
                            $(listItems[j]).get(0).appendChild(fontImage);\r\n
                        }\r\n
                    } else {\r\n
                        if (me.tiles[j]) {\r\n
                            me.tiles[j].parentNode.removeChild(me.tiles[j]);\r\n
                            me.tiles[j] = null;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            },\r\n
            flushVisibleFontsTiles: function () {\r\n
                for (var j = this.tiles.length - 1; j >= 0; --j) {\r\n
                    if (this.tiles[j]) {\r\n
                        this.tiles[j].parentNode.removeChild(this.tiles[j]);\r\n
                        this.tiles[j] = null;\r\n
                    }\r\n
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
            <value> <int>22171</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
