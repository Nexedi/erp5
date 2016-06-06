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
            <value> <string>ts44321418.31</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Comments.js</string> </value>
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
Common.Views = Common.Views || {};\r\n
define(["text!common/main/lib/template/Comments.template", "text!common/main/lib/template/CommentsPanel.template", "text!common/main/lib/template/CommentsPopover.template", "common/main/lib/util/utils", "common/main/lib/component/Button", "common/main/lib/component/ComboBox", "common/main/lib/component/DataView", "common/main/lib/component/Window"], function (commentsTemplate, panelTemplate, popoverTemplate) {\r\n
    function replaceWords(template, words) {\r\n
        var word, value, tpl = template;\r\n
        for (word in words) {\r\n
            if (undefined !== word) {\r\n
                value = words[word];\r\n
                tpl = tpl.replace(new RegExp(word, "g"), value);\r\n
            }\r\n
        }\r\n
        return tpl;\r\n
    }\r\n
    Common.Views.CommentsPopover = Common.UI.Window.extend({\r\n
        initialize: function (options) {\r\n
            var _options = {};\r\n
            _.extend(_options, {\r\n
                closable: false,\r\n
                width: 265,\r\n
                height: 120,\r\n
                header: false,\r\n
                modal: false\r\n
            },\r\n
            options);\r\n
            this.template = options.template || [\'<div class="box">\', \'<div id="id-comments-popover" class="comments-popover"></div>\', \'<div id="id-comments-arrow" class="comments-arrow-left"></div>\', "</div>"].join("");\r\n
            this.store = options.store;\r\n
            this.delegate = options.delegate;\r\n
            _options.tpl = _.template(this.template, _options);\r\n
            this.arrow = {\r\n
                margin: 20,\r\n
                width: 12,\r\n
                height: 34\r\n
            };\r\n
            this.sdkBounds = {\r\n
                width: 0,\r\n
                height: 0,\r\n
                padding: 5,\r\n
                paddingTop: 20\r\n
            };\r\n
            Common.UI.Window.prototype.initialize.call(this, _options);\r\n
        },\r\n
        render: function () {\r\n
            Common.UI.Window.prototype.render.call(this);\r\n
            var me = this,\r\n
            t = this.delegate,\r\n
            window = this.$window;\r\n
            window.css({\r\n
                height: "",\r\n
                minHeight: "",\r\n
                overflow: "hidden",\r\n
                position: "absolute",\r\n
                zIndex: "990"\r\n
            });\r\n
            var body = window.find(".body");\r\n
            if (body) {\r\n
                body.css("position", "relative");\r\n
            }\r\n
            var PopoverDataView = Common.UI.DataView.extend((function () {\r\n
                var parentView = me;\r\n
                return {\r\n
                    options: {\r\n
                        handleSelect: false,\r\n
                        scrollable: true,\r\n
                        template: _.template(\'<div class="dataview-ct inner" style="overflow-y: hidden;"></div>\')\r\n
                    },\r\n
                    getTextBox: function () {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        return (text && text.length) ? text : undefined;\r\n
                    },\r\n
                    setFocusToTextBox: function (blur) {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        if (blur) {\r\n
                            text.blur();\r\n
                        } else {\r\n
                            if (text && text.length) {\r\n
                                var val = text.val();\r\n
                                text.focus();\r\n
                                text.val("");\r\n
                                text.val(val);\r\n
                            }\r\n
                        }\r\n
                    },\r\n
                    getActiveTextBoxVal: function () {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        return (text && text.length) ? text.val().trim() : "";\r\n
                    },\r\n
                    autoHeightTextBox: function () {\r\n
                        var view = this,\r\n
                        textBox = this.$el.find("textarea"),\r\n
                        domTextBox = null,\r\n
                        minHeight = 50,\r\n
                        lineHeight = 0,\r\n
                        scrollPos = 0,\r\n
                        oldHeight = 0,\r\n
                        newHeight = 0;\r\n
                        function updateTextBoxHeight() {\r\n
                            scrollPos = $(view.scroller.el).scrollTop();\r\n
                            if (domTextBox.scrollHeight > domTextBox.clientHeight) {\r\n
                                textBox.css({\r\n
                                    height: (domTextBox.scrollHeight + lineHeight) + "px"\r\n
                                });\r\n
                                parentView.calculateSizeOfContent();\r\n
                            } else {\r\n
                                oldHeight = domTextBox.clientHeight;\r\n
                                if (oldHeight >= minHeight) {\r\n
                                    textBox.css({\r\n
                                        height: minHeight + "px"\r\n
                                    });\r\n
                                    if (domTextBox.scrollHeight > domTextBox.clientHeight) {\r\n
                                        newHeight = Math.max(domTextBox.scrollHeight + lineHeight, minHeight);\r\n
                                        textBox.css({\r\n
                                            height: newHeight + "px"\r\n
                                        });\r\n
                                    }\r\n
                                    parentView.calculateSizeOfContent();\r\n
                                    parentView.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                    parentView.calculateSizeOfContent();\r\n
                                }\r\n
                            }\r\n
                            view.scroller.scrollTop(scrollPos);\r\n
                            view.autoScrollToEditButtons();\r\n
                        }\r\n
                        if (textBox && textBox.length) {\r\n
                            domTextBox = textBox.get(0);\r\n
                            if (domTextBox) {\r\n
                                lineHeight = parseInt(textBox.css("lineHeight"), 10) * 0.25;\r\n
                                updateTextBoxHeight();\r\n
                                textBox.bind("input propertychange", updateTextBoxHeight);\r\n
                            }\r\n
                        }\r\n
                        this.textBox = textBox;\r\n
                    },\r\n
                    clearTextBoxBind: function () {\r\n
                        if (this.textBox) {\r\n
                            this.textBox.unbind("input propertychange");\r\n
                            this.textBox = undefined;\r\n
                        }\r\n
                    },\r\n
                    autoScrollToEditButtons: function () {\r\n
                        var button = $("#id-comments-change-popover"),\r\n
                        btnBounds = null,\r\n
                        contentBounds = this.el.getBoundingClientRect(),\r\n
                        moveY = 0,\r\n
                        padding = 7;\r\n
                        if (button.length) {\r\n
                            btnBounds = button.get(0).getBoundingClientRect();\r\n
                            if (btnBounds && contentBounds) {\r\n
                                moveY = contentBounds.bottom - (btnBounds.bottom + padding);\r\n
                                if (moveY < 0) {\r\n
                                    this.scroller.scrollTop(this.scroller.getScrollTop() - moveY);\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                };\r\n
            })());\r\n
            if (PopoverDataView) {\r\n
                if (this.commentsView) {\r\n
                    this.commentsView.render($("#id-comments-popover"));\r\n
                    this.commentsView.onResetItems();\r\n
                } else {\r\n
                    this.commentsView = new PopoverDataView({\r\n
                        el: $("#id-comments-popover"),\r\n
                        store: me.store,\r\n
                        itemTemplate: _.template(replaceWords(popoverTemplate, {\r\n
                            textAddReply: t.textAddReply,\r\n
                            textAdd: t.textAdd,\r\n
                            textCancel: t.textCancel,\r\n
                            textEdit: t.textEdit,\r\n
                            textReply: t.textReply,\r\n
                            textClose: t.textClose,\r\n
                            textResolved: t.textResolved,\r\n
                            textResolve: t.textResolve\r\n
                        }))\r\n
                    });\r\n
                    this.commentsView.on("item:click", function (picker, item, record, e) {\r\n
                        var btn, showEditBox, showReplyBox, commentId, replyId, hideAddReply;\r\n
                        function readdresolves() {\r\n
                            me.renderResolvedComboButtons();\r\n
                            t.renderResolvedComboButtons();\r\n
                            me.update();\r\n
                        }\r\n
                        btn = $(e.target);\r\n
                        if (btn) {\r\n
                            showEditBox = record.get("editTextInPopover");\r\n
                            showReplyBox = record.get("showReplyInPopover");\r\n
                            hideAddReply = record.get("hideAddReply");\r\n
                            commentId = record.get("uid");\r\n
                            replyId = btn.attr("data-value");\r\n
                            if (record.get("hint")) {\r\n
                                t.fireEvent("comment:disableHint", [record]);\r\n
                                return;\r\n
                            }\r\n
                            if (btn.hasClass("btn-edit")) {\r\n
                                if (!_.isUndefined(replyId)) {\r\n
                                    t.fireEvent("comment:closeEditing", [commentId]);\r\n
                                    t.fireEvent("comment:editReply", [commentId, replyId, true]);\r\n
                                    this.replyId = replyId;\r\n
                                    this.autoHeightTextBox();\r\n
                                    me.calculateSizeOfContent();\r\n
                                    me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                    me.calculateSizeOfContent();\r\n
                                    readdresolves();\r\n
                                    me.hookTextBox();\r\n
                                    this.autoScrollToEditButtons();\r\n
                                    this.setFocusToTextBox();\r\n
                                } else {\r\n
                                    if (!showEditBox) {\r\n
                                        t.fireEvent("comment:closeEditing");\r\n
                                        record.set("editTextInPopover", true);\r\n
                                        t.fireEvent("comment:show", [commentId]);\r\n
                                        this.autoHeightTextBox();\r\n
                                        me.calculateSizeOfContent();\r\n
                                        me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                        me.calculateSizeOfContent();\r\n
                                        readdresolves();\r\n
                                        me.hookTextBox();\r\n
                                        this.autoScrollToEditButtons();\r\n
                                        this.setFocusToTextBox();\r\n
                                    }\r\n
                                }\r\n
                            } else {\r\n
                                if (btn.hasClass("btn-delete")) {\r\n
                                    if (!_.isUndefined(replyId)) {\r\n
                                        t.fireEvent("comment:removeReply", [commentId, replyId]);\r\n
                                        me.calculateSizeOfContent();\r\n
                                        me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                        me.calculateSizeOfContent();\r\n
                                    } else {\r\n
                                        t.fireEvent("comment:remove", [commentId]);\r\n
                                    }\r\n
                                    t.fireEvent("comment:closeEditing");\r\n
                                    readdresolves();\r\n
                                } else {\r\n
                                    if (btn.hasClass("user-reply")) {\r\n
                                        t.fireEvent("comment:closeEditing");\r\n
                                        record.set("showReplyInPopover", true);\r\n
                                        me.calculateSizeOfContent();\r\n
                                        me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                        me.calculateSizeOfContent();\r\n
                                        readdresolves();\r\n
                                        this.autoHeightTextBox();\r\n
                                        me.hookTextBox();\r\n
                                        this.autoScrollToEditButtons();\r\n
                                        this.setFocusToTextBox();\r\n
                                    } else {\r\n
                                        if (btn.hasClass("btn-reply", false)) {\r\n
                                            if (showReplyBox) {\r\n
                                                this.clearTextBoxBind();\r\n
                                                t.fireEvent("comment:addReply", [commentId, this.getActiveTextBoxVal()]);\r\n
                                                t.fireEvent("comment:closeEditing");\r\n
                                                readdresolves();\r\n
                                            }\r\n
                                        } else {\r\n
                                            if (btn.hasClass("btn-close", false)) {\r\n
                                                t.fireEvent("comment:closeEditing", [commentId]);\r\n
                                                me.calculateSizeOfContent();\r\n
                                                t.fireEvent("comment:show", [commentId]);\r\n
                                                readdresolves();\r\n
                                            } else {\r\n
                                                if (btn.hasClass("btn-inner-edit", false)) {\r\n
                                                    if (record.get("dummy")) {\r\n
                                                        t.fireEvent("comment:addDummyComment", [this.getActiveTextBoxVal()]);\r\n
                                                        return;\r\n
                                                    }\r\n
                                                    this.clearTextBoxBind();\r\n
                                                    if (!_.isUndefined(this.replyId)) {\r\n
                                                        t.fireEvent("comment:changeReply", [commentId, this.replyId, this.getActiveTextBoxVal()]);\r\n
                                                        this.replyId = undefined;\r\n
                                                        t.fireEvent("comment:closeEditing");\r\n
                                                    } else {\r\n
                                                        if (showEditBox) {\r\n
                                                            t.fireEvent("comment:change", [commentId, this.getActiveTextBoxVal()]);\r\n
                                                            t.fireEvent("comment:closeEditing");\r\n
                                                            me.calculateSizeOfContent();\r\n
                                                        }\r\n
                                                    }\r\n
                                                    readdresolves();\r\n
                                                } else {\r\n
                                                    if (btn.hasClass("btn-inner-close", false)) {\r\n
                                                        if (record.get("dummy")) {\r\n
                                                            me.hide();\r\n
                                                            return;\r\n
                                                        }\r\n
                                                        if (hideAddReply && this.getActiveTextBoxVal().length > 0) {\r\n
                                                            me.saveText();\r\n
                                                            record.set("hideAddReply", false);\r\n
                                                            this.getTextBox().val(me.textVal);\r\n
                                                            this.autoHeightTextBox();\r\n
                                                        } else {\r\n
                                                            this.clearTextBoxBind();\r\n
                                                            t.fireEvent("comment:closeEditing", [commentId]);\r\n
                                                        }\r\n
                                                        this.replyId = undefined;\r\n
                                                        me.calculateSizeOfContent();\r\n
                                                        me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);\r\n
                                                        me.calculateSizeOfContent();\r\n
                                                        readdresolves();\r\n
                                                    } else {\r\n
                                                        if (btn.hasClass("btn-resolve", false)) {\r\n
                                                            t.fireEvent("comment:resolve", [commentId]);\r\n
                                                            readdresolves();\r\n
                                                        }\r\n
                                                    }\r\n
                                                }\r\n
                                            }\r\n
                                        }\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    });\r\n
                    me.on({\r\n
                        "show": function () {\r\n
                            me.commentsView.autoHeightTextBox();\r\n
                            var text = me.$window.find("textarea");\r\n
                            if (text && text.length) {\r\n
                                text.focus();\r\n
                            }\r\n
                            text.keydown(function (event) {\r\n
                                if (event.keyCode == Common.UI.Keys.ESC) {\r\n
                                    me.hide();\r\n
                                }\r\n
                            });\r\n
                        }\r\n
                    });\r\n
                }\r\n
            }\r\n
        },\r\n
        show: function (animate, loadText, focus, showText) {\r\n
            this.options.animate = animate;\r\n
            var me = this,\r\n
            textBox = this.commentsView.getTextBox();\r\n
            if (loadText && this.textVal) {\r\n
                textBox && textBox.val(this.textVal);\r\n
            }\r\n
            if (showText && showText.length) {\r\n
                textBox && textBox.val(showText);\r\n
            }\r\n
            Common.UI.Window.prototype.show.call(this);\r\n
            this.renderResolvedComboButtons();\r\n
            if (this.commentsView.scroller) {\r\n
                this.commentsView.scroller.update({\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
            this.hookTextBox();\r\n
        },\r\n
        hide: function () {\r\n
            if (this.handlerHide) {\r\n
                this.handlerHide();\r\n
            }\r\n
            Common.UI.Window.prototype.hide.call(this);\r\n
            if (!_.isUndefined(this.e) && this.e.keyCode == Common.UI.Keys.ESC) {\r\n
                this.e.preventDefault();\r\n
                this.e.stopImmediatePropagation();\r\n
                this.e = undefined;\r\n
            }\r\n
        },\r\n
        update: function () {\r\n
            if (this.commentsView && this.commentsView.scroller) {\r\n
                this.commentsView.scroller.update({\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
        },\r\n
        isVisible: function () {\r\n
            return (this.$window && this.$window.is(":visible"));\r\n
        },\r\n
        setLeftTop: function (posX, posY, leftX, loadInnerValues) {\r\n
            if (!this.$window) {\r\n
                this.render();\r\n
            }\r\n
            if (loadInnerValues) {\r\n
                posX = this.arrowPosX;\r\n
                posY = this.arrowPosY;\r\n
                leftX = this.leftX;\r\n
            }\r\n
            if (_.isUndefined(posX) && _.isUndefined(posY)) {\r\n
                return;\r\n
            }\r\n
            this.arrowPosX = posX;\r\n
            this.arrowPosY = posY;\r\n
            this.leftX = leftX;\r\n
            var commentsView = $("#id-comments-popover"),\r\n
            arrowView = $("#id-comments-arrow"),\r\n
            editorView = $("#editor_sdk"),\r\n
            editorBounds = null,\r\n
            sdkBoundsHeight = 0,\r\n
            sdkBoundsTop = 0,\r\n
            sdkBoundsLeft = 0,\r\n
            sdkPanelRight = "",\r\n
            sdkPanelRightWidth = 0,\r\n
            sdkPanelLeft = "",\r\n
            sdkPanelLeftWidth = 0,\r\n
            sdkPanelThumbs = "",\r\n
            sdkPanelThumbsWidth = 0,\r\n
            sdkPanelTop = "",\r\n
            sdkPanelHeight = 0,\r\n
            leftPos = 0,\r\n
            windowWidth = 0,\r\n
            outerHeight = 0,\r\n
            topPos = 0,\r\n
            sdkBoundsTopPos = 0;\r\n
            if (commentsView && arrowView && editorView && editorView.get(0)) {\r\n
                editorBounds = editorView.get(0).getBoundingClientRect();\r\n
                if (editorBounds) {\r\n
                    sdkBoundsHeight = editorBounds.height - this.sdkBounds.padding * 2;\r\n
                    this.$window.css({\r\n
                        maxHeight: sdkBoundsHeight + "px"\r\n
                    });\r\n
                    this.sdkBounds.width = editorBounds.width;\r\n
                    this.sdkBounds.height = editorBounds.height;\r\n
                    if (!_.isUndefined(posX)) {\r\n
                        sdkPanelRight = $("#id_vertical_scroll");\r\n
                        if (sdkPanelRight.length) {\r\n
                            sdkPanelRightWidth = (sdkPanelRight.css("display") !== "none") ? sdkPanelRight.width() : 0;\r\n
                        } else {\r\n
                            sdkPanelRight = $("#ws-v-scrollbar");\r\n
                            if (sdkPanelRight.length) {\r\n
                                sdkPanelRightWidth = (sdkPanelRight.css("display") !== "none") ? sdkPanelRight.width() : 0;\r\n
                            }\r\n
                        }\r\n
                        this.sdkBounds.width -= sdkPanelRightWidth;\r\n
                        sdkPanelLeft = $("#id_panel_left");\r\n
                        if (sdkPanelLeft.length) {\r\n
                            sdkPanelLeftWidth = (sdkPanelLeft.css("display") !== "none") ? sdkPanelLeft.width() : 0;\r\n
                        }\r\n
                        sdkPanelThumbs = $("#id_panel_thumbnails");\r\n
                        if (sdkPanelThumbs.length) {\r\n
                            sdkPanelThumbsWidth = (sdkPanelThumbs.css("display") !== "none") ? sdkPanelThumbs.width() : 0;\r\n
                            this.sdkBounds.width -= sdkPanelThumbsWidth;\r\n
                        }\r\n
                        leftPos = Math.min(sdkBoundsLeft + posX + this.arrow.width, sdkBoundsLeft + this.sdkBounds.width - this.$window.outerWidth());\r\n
                        leftPos = Math.max(sdkBoundsLeft + sdkPanelLeftWidth + this.arrow.width, leftPos);\r\n
                        arrowView.attr("class", "comments-arrow-left");\r\n
                        if (!_.isUndefined(leftX)) {\r\n
                            windowWidth = this.$window.outerWidth();\r\n
                            if (windowWidth) {\r\n
                                if ((posX + windowWidth > this.sdkBounds.width - this.arrow.width + 5) && (this.leftX > windowWidth)) {\r\n
                                    leftPos = this.leftX - windowWidth + sdkBoundsLeft - this.arrow.width;\r\n
                                    arrowView.attr("class", "comments-arrow-right");\r\n
                                } else {\r\n
                                    arrowView.attr("class", "comments-arrow-left");\r\n
                                    leftPos = sdkBoundsLeft + posX + this.arrow.width;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                        this.$window.css("left", leftPos + "px");\r\n
                    }\r\n
                    if (!_.isUndefined(posY)) {\r\n
                        sdkPanelTop = $("#id_panel_top");\r\n
                        sdkBoundsTopPos = sdkBoundsTop;\r\n
                        if (sdkPanelTop.length) {\r\n
                            sdkPanelHeight = (sdkPanelTop.css("display") !== "none") ? sdkPanelTop.height() : 0;\r\n
                            sdkBoundsTopPos += this.sdkBounds.paddingTop;\r\n
                        } else {\r\n
                            sdkPanelTop = $("#ws-h-scrollbar");\r\n
                            if (sdkPanelTop.length) {\r\n
                                sdkPanelHeight = (sdkPanelTop.css("display") !== "none") ? sdkPanelTop.height() : 0;\r\n
                                sdkBoundsTopPos -= this.sdkBounds.paddingTop;\r\n
                            }\r\n
                        }\r\n
                        this.sdkBounds.height -= sdkPanelHeight;\r\n
                        outerHeight = this.$window.outerHeight();\r\n
                        topPos = Math.min(sdkBoundsTop + sdkBoundsHeight - outerHeight, this.arrowPosY + sdkBoundsTop - this.arrow.height);\r\n
                        topPos = Math.max(topPos, sdkBoundsTopPos);\r\n
                        this.$window.css("top", topPos + "px");\r\n
                    }\r\n
                }\r\n
            }\r\n
            this.calculateSizeOfContent();\r\n
        },\r\n
        calculateSizeOfContent: function (testVisible) {\r\n
            if (testVisible && !this.$window.is(":visible")) {\r\n
                return;\r\n
            }\r\n
            this.$window.css({\r\n
                overflow: "hidden"\r\n
            });\r\n
            var arrowView = $("#id-comments-arrow"),\r\n
            commentsView = $("#id-comments-popover"),\r\n
            contentBounds = null,\r\n
            editorView = null,\r\n
            editorBounds = null,\r\n
            sdkBoundsHeight = 0,\r\n
            sdkBoundsTop = 0,\r\n
            sdkBoundsLeft = 0,\r\n
            sdkPanelTop = "",\r\n
            sdkPanelHeight = 0,\r\n
            arrowPosY = 0,\r\n
            windowHeight = 0,\r\n
            outerHeight = 0,\r\n
            topPos = 0,\r\n
            sdkBoundsTopPos = 0;\r\n
            if (commentsView && arrowView && commentsView.get(0)) {\r\n
                commentsView.css({\r\n
                    height: "100%"\r\n
                });\r\n
                contentBounds = commentsView.get(0).getBoundingClientRect();\r\n
                if (contentBounds) {\r\n
                    editorView = $("#editor_sdk");\r\n
                    if (editorView && editorView.get(0)) {\r\n
                        editorBounds = editorView.get(0).getBoundingClientRect();\r\n
                        if (editorBounds) {\r\n
                            sdkBoundsHeight = editorBounds.height - this.sdkBounds.padding * 2;\r\n
                            sdkBoundsTopPos = sdkBoundsTop;\r\n
                            windowHeight = this.$window.outerHeight();\r\n
                            sdkPanelTop = $("#id_panel_top");\r\n
                            if (sdkPanelTop.length) {\r\n
                                sdkPanelHeight = (sdkPanelTop.css("display") !== "none") ? sdkPanelTop.height() : 0;\r\n
                                sdkBoundsTopPos += this.sdkBounds.paddingTop;\r\n
                            } else {\r\n
                                sdkPanelTop = $("#ws-h-scrollbar");\r\n
                                if (sdkPanelTop.length) {\r\n
                                    sdkPanelHeight = (sdkPanelTop.css("display") !== "none") ? sdkPanelTop.height() : 0;\r\n
                                    sdkBoundsTopPos -= this.sdkBounds.paddingTop;\r\n
                                }\r\n
                            }\r\n
                            outerHeight = Math.max(commentsView.outerHeight(), this.$window.outerHeight());\r\n
                            if (sdkBoundsHeight < outerHeight) {\r\n
                                this.$window.css({\r\n
                                    maxHeight: sdkBoundsHeight - sdkPanelHeight + "px",\r\n
                                    top: sdkBoundsTop + sdkPanelHeight + "px"\r\n
                                });\r\n
                                commentsView.css({\r\n
                                    height: sdkBoundsHeight - sdkPanelHeight + "px"\r\n
                                });\r\n
                                arrowPosY = Math.min(arrowPosY, sdkBoundsHeight - (sdkPanelHeight + this.arrow.margin + this.arrow.width));\r\n
                                arrowView.css({\r\n
                                    top: arrowPosY + "px"\r\n
                                });\r\n
                            } else {\r\n
                                outerHeight = windowHeight;\r\n
                                if (outerHeight > 0) {\r\n
                                    if (contentBounds.top + outerHeight > sdkBoundsHeight + sdkBoundsTop || contentBounds.height === 0) {\r\n
                                        topPos = Math.min(sdkBoundsTop + sdkBoundsHeight - outerHeight, this.arrowPosY + sdkBoundsTop - this.arrow.height);\r\n
                                        topPos = Math.max(topPos, sdkBoundsTopPos);\r\n
                                        this.$window.css({\r\n
                                            top: topPos + "px"\r\n
                                        });\r\n
                                    }\r\n
                                }\r\n
                                arrowPosY = Math.max(this.arrow.margin, this.arrowPosY - (sdkBoundsHeight - outerHeight) - this.arrow.width);\r\n
                                arrowPosY = Math.min(arrowPosY, outerHeight - this.arrow.margin - this.arrow.width);\r\n
                                arrowView.css({\r\n
                                    top: arrowPosY + "px"\r\n
                                });\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            this.$window.css({\r\n
                overflow: ""\r\n
            });\r\n
        },\r\n
        saveText: function (clear) {\r\n
            this.textVal = undefined;\r\n
            if (this.commentsView) {\r\n
                if (!clear) {\r\n
                    this.textVal = this.commentsView.getActiveTextBoxVal();\r\n
                } else {\r\n
                    this.commentsView.clearTextBoxBind();\r\n
                }\r\n
            }\r\n
        },\r\n
        getEditText: function () {\r\n
            if (this.commentsView) {\r\n
                return this.commentsView.getActiveTextBoxVal();\r\n
            }\r\n
            return undefined;\r\n
        },\r\n
        renderResolvedComboButtons: function () {\r\n
            if (_.isUndefined(this.openComboBoxes)) {\r\n
                this.openComboBoxes = [];\r\n
            }\r\n
            var me = this,\r\n
            i = 0,\r\n
            openCombo, buttons, j = this.openComboBoxes.length - 1;\r\n
            function onSelectResolveComment(comboBox) {\r\n
                if ($(comboBox.el).parent() && $(comboBox.el).parent().parent()) {\r\n
                    var id = ($(comboBox.el).parent().parent()).attr("id");\r\n
                    if (id) {\r\n
                        me.delegate.fireEvent("comment:resolve", [undefined, id]);\r\n
                        me.delegate.renderResolvedComboButtons();\r\n
                        me.renderResolvedComboButtons();\r\n
                    }\r\n
                }\r\n
            }\r\n
            for (; j >= 0; --j) {\r\n
                this.openComboBoxes[j].off();\r\n
                this.openComboBoxes[j].stopListening();\r\n
            }\r\n
            this.openComboBoxes = [];\r\n
            if (this.commentsView) {\r\n
                buttons = $(this.commentsView.el).find(".resolve-ct-check");\r\n
                for (i = buttons.length - 1; i >= 0; --i) {\r\n
                    openCombo = new Common.UI.ComboBox({\r\n
                        template: _.template(["<div>", \'<div class="resolved"></div>\', \'<div class="btn-resolve-check dropdown-toggle" data-toggle="dropdown">\', this.delegate.textResolved, "</div>", \'<span class="comments-caret"></span>\', \'<ul class="dropdown-menu <%= menuCls %>" style="<%= menuStyle %>" role="menu">\', "<% _.each(items, function (item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a href="#"><%= scope.getDisplayValue(item) %></a></li>\', "<% }); %>", "</ul>", "</div>", ].join("")),\r\n
                        menuStyle: "min-width: 55px; margin-top: -7px; margin-left: -2px; padding: 0 0; right: 6px; left: auto;",\r\n
                        data: [{\r\n
                            value: 1,\r\n
                            displayValue: this.delegate.textOpenAgain\r\n
                        }]\r\n
                    });\r\n
                    openCombo.render($(buttons[i]));\r\n
                    openCombo.on("selected", onSelectResolveComment);\r\n
                    this.openComboBoxes.push(openCombo);\r\n
                }\r\n
            }\r\n
        },\r\n
        hookTextBox: function () {\r\n
            var me = this,\r\n
            textBox = this.commentsView.getTextBox();\r\n
            textBox && textBox.keydown(function (event) {\r\n
                if ((event.ctrlKey || event.metaKey) && event.keyCode === Common.UI.Keys.RETURN) {\r\n
                    var buttonChangeComment = $("#id-comments-change-popover");\r\n
                    if (buttonChangeComment && buttonChangeComment.length) {\r\n
                        buttonChangeComment.click();\r\n
                    }\r\n
                    event.stopImmediatePropagation();\r\n
                } else {\r\n
                    if (event.keyCode === Common.UI.Keys.TAB) {\r\n
                        var $this, end, start;\r\n
                        start = this.selectionStart;\r\n
                        end = this.selectionEnd;\r\n
                        $this = $(this);\r\n
                        $this.val($this.val().substring(0, start) + "\\t" + $this.val().substring(end));\r\n
                        this.selectionStart = this.selectionEnd = start + 1;\r\n
                        event.stopImmediatePropagation();\r\n
                        event.preventDefault();\r\n
                    }\r\n
                }\r\n
                me.e = event;\r\n
            });\r\n
        }\r\n
    });\r\n
    Common.Views.Comments = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#left-panel-comments",\r\n
        template: _.template(panelTemplate),\r\n
        initialize: function (options) {\r\n
            Common.UI.BaseView.prototype.initialize.call(this, options);\r\n
            this.store = this.options.store;\r\n
            this.popoverComments = this.options.popoverComments;\r\n
        },\r\n
        render: function () {\r\n
            var me = this;\r\n
            $(this.el).html(this.template({\r\n
                textAddCommentToDoc: me.textAddCommentToDoc,\r\n
                textAddComment: me.textAddComment,\r\n
                textCancel: me.textCancel,\r\n
                textEnterCommentHint: me.textEnterCommentHint\r\n
            }));\r\n
            this.buttonAddCommentToDoc = new Common.UI.Button({\r\n
                el: $("#comment-btn-new"),\r\n
                enableToggle: false\r\n
            });\r\n
            this.buttonAdd = new Common.UI.Button({\r\n
                action: "add",\r\n
                el: $("#comment-btn-add"),\r\n
                enableToggle: false\r\n
            });\r\n
            this.buttonCancel = new Common.UI.Button({\r\n
                el: $("#comment-btn-cancel"),\r\n
                enableToggle: false\r\n
            });\r\n
            this.buttonAddCommentToDoc.on("click", _.bind(this.onClickShowBoxDocumentComment, this));\r\n
            this.buttonAdd.on("click", _.bind(this.onClickAddDocumentComment, this));\r\n
            this.buttonCancel.on("click", _.bind(this.onClickCancelDocumentComment, this));\r\n
            this.txtComment = $("#comment-msg-new", this.el);\r\n
            this.txtComment.keydown(function (event) {\r\n
                if ((event.ctrlKey || event.metaKey) && event.keyCode == Common.UI.Keys.RETURN) {\r\n
                    me.onClickAddDocumentComment();\r\n
                    event.stopImmediatePropagation();\r\n
                } else {\r\n
                    if (event.keyCode === Common.UI.Keys.TAB) {\r\n
                        var $this, end, start;\r\n
                        start = this.selectionStart;\r\n
                        end = this.selectionEnd;\r\n
                        $this = $(this);\r\n
                        $this.val($this.val().substring(0, start) + "\\t" + $this.val().substring(end));\r\n
                        this.selectionStart = this.selectionEnd = start + 1;\r\n
                        event.stopImmediatePropagation();\r\n
                        event.preventDefault();\r\n
                    }\r\n
                }\r\n
            });\r\n
            var CommentsPanelDataView = Common.UI.DataView.extend((function () {\r\n
                var parentView = me;\r\n
                return {\r\n
                    options: {\r\n
                        handleSelect: false,\r\n
                        scrollable: true,\r\n
                        listenStoreEvents: false,\r\n
                        template: _.template(\'<div class="dataview-ct inner"></div>\')\r\n
                    },\r\n
                    getTextBox: function () {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        return (text && text.length) ? text : undefined;\r\n
                    },\r\n
                    setFocusToTextBox: function () {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        if (text && text.length) {\r\n
                            var val = text.val();\r\n
                            text.focus();\r\n
                            text.val("");\r\n
                            text.val(val);\r\n
                        }\r\n
                    },\r\n
                    getActiveTextBoxVal: function () {\r\n
                        var text = $(this.el).find("textarea");\r\n
                        return (text && text.length) ? text.val().trim() : "";\r\n
                    },\r\n
                    autoHeightTextBox: function () {\r\n
                        var view = this,\r\n
                        textBox = $(this.el).find("textarea"),\r\n
                        domTextBox = null,\r\n
                        minHeight = 50,\r\n
                        lineHeight = 0,\r\n
                        scrollPos = 0,\r\n
                        oldHeight = 0,\r\n
                        newHeight = 0;\r\n
                        function updateTextBoxHeight() {\r\n
                            if (domTextBox.scrollHeight > domTextBox.clientHeight) {\r\n
                                textBox.css({\r\n
                                    height: (domTextBox.scrollHeight + lineHeight) + "px"\r\n
                                });\r\n
                            } else {\r\n
                                oldHeight = domTextBox.clientHeight;\r\n
                                if (oldHeight >= minHeight) {\r\n
                                    textBox.css({\r\n
                                        height: minHeight + "px"\r\n
                                    });\r\n
                                    if (domTextBox.scrollHeight > domTextBox.clientHeight) {\r\n
                                        newHeight = Math.max(domTextBox.scrollHeight + lineHeight, minHeight);\r\n
                                        textBox.css({\r\n
                                            height: newHeight + "px"\r\n
                                        });\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                            view.autoScrollToEditButtons();\r\n
                        }\r\n
                        if (textBox && textBox.length) {\r\n
                            domTextBox = textBox.get(0);\r\n
                            if (domTextBox) {\r\n
                                lineHeight = parseInt(textBox.css("lineHeight"), 10) * 0.25;\r\n
                                updateTextBoxHeight();\r\n
                                textBox.bind("input propertychange", updateTextBoxHeight);\r\n
                            }\r\n
                        }\r\n
                        this.textBox = textBox;\r\n
                    },\r\n
                    clearTextBoxBind: function () {\r\n
                        if (this.textBox) {\r\n
                            this.textBox.unbind("input propertychange");\r\n
                            this.textBox = undefined;\r\n
                        }\r\n
                    },\r\n
                    autoScrollToEditButtons: function () {\r\n
                        var button = $("#id-comments-change"),\r\n
                        btnBounds = null,\r\n
                        contentBounds = this.el.getBoundingClientRect(),\r\n
                        moveY = 0,\r\n
                        padding = 7;\r\n
                        if (button.length) {\r\n
                            btnBounds = button.get(0).getBoundingClientRect();\r\n
                            if (btnBounds && contentBounds) {\r\n
                                moveY = contentBounds.bottom - (btnBounds.bottom + padding);\r\n
                                if (moveY < 0) {\r\n
                                    this.scroller.scrollTop(this.scroller.getScrollTop() - moveY);\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                };\r\n
            })());\r\n
            if (CommentsPanelDataView) {\r\n
                if (this.commentsView) {\r\n
                    this.commentsView.render($("#comments-messages"));\r\n
                    this.commentsView.onResetItems();\r\n
                } else {\r\n
                    this.commentsView = new CommentsPanelDataView({\r\n
                        el: $("#comments-messages"),\r\n
                        store: me.store,\r\n
                        itemTemplate: _.template(replaceWords(commentsTemplate, {\r\n
                            textAddReply: me.textAddReply,\r\n
                            textAdd: me.textAdd,\r\n
                            textCancel: me.textCancel,\r\n
                            textEdit: me.textEdit,\r\n
                            textReply: me.textReply,\r\n
                            textClose: me.textClose,\r\n
                            textResolved: me.textResolved,\r\n
                            textResolve: me.textResolve\r\n
                        }))\r\n
                    });\r\n
                    this.commentsView.on("item:click", function (picker, item, record, e) {\r\n
                        var btn, showEditBox, showReplyBox, commentId, replyId, hideAddReply;\r\n
                        function readdresolves() {\r\n
                            if (me.popover) {\r\n
                                me.popover.renderResolvedComboButtons();\r\n
                            }\r\n
                            me.renderResolvedComboButtons();\r\n
                            me.update();\r\n
                        }\r\n
                        btn = $(e.target);\r\n
                        if (btn) {\r\n
                            showEditBox = record.get("editText");\r\n
                            showReplyBox = record.get("showReply");\r\n
                            commentId = record.get("uid");\r\n
                            replyId = btn.attr("data-value");\r\n
                            if (btn.hasClass("btn-edit")) {\r\n
                                if (!_.isUndefined(replyId)) {\r\n
                                    me.fireEvent("comment:closeEditing", [commentId]);\r\n
                                    me.fireEvent("comment:editReply", [commentId, replyId]);\r\n
                                    me.commentsView.reply = replyId;\r\n
                                    this.autoHeightTextBox();\r\n
                                    readdresolves();\r\n
                                    me.hookTextBox();\r\n
                                    this.autoScrollToEditButtons();\r\n
                                    this.setFocusToTextBox();\r\n
                                } else {\r\n
                                    if (!showEditBox) {\r\n
                                        me.fireEvent("comment:closeEditing");\r\n
                                        record.set("editText", true);\r\n
                                        this.autoHeightTextBox();\r\n
                                        readdresolves();\r\n
                                        this.setFocusToTextBox();\r\n
                                        me.hookTextBox();\r\n
                                    }\r\n
                                }\r\n
                            } else {\r\n
                                if (btn.hasClass("btn-delete")) {\r\n
                                    if (!_.isUndefined(replyId)) {\r\n
                                        me.fireEvent("comment:removeReply", [commentId, replyId]);\r\n
                                    } else {\r\n
                                        me.fireEvent("comment:remove", [commentId]);\r\n
                                    }\r\n
                                    me.fireEvent("comment:closeEditing");\r\n
                                    readdresolves();\r\n
                                } else {\r\n
                                    if (btn.hasClass("user-reply")) {\r\n
                                        me.fireEvent("comment:closeEditing");\r\n
                                        record.set("showReply", true);\r\n
                                        readdresolves();\r\n
                                        this.autoHeightTextBox();\r\n
                                        me.hookTextBox();\r\n
                                        this.autoScrollToEditButtons();\r\n
                                        this.setFocusToTextBox();\r\n
                                    } else {\r\n
                                        if (btn.hasClass("btn-reply", false)) {\r\n
                                            if (showReplyBox) {\r\n
                                                me.fireEvent("comment:addReply", [commentId, this.getActiveTextBoxVal()]);\r\n
                                                me.fireEvent("comment:closeEditing");\r\n
                                                readdresolves();\r\n
                                            }\r\n
                                        } else {\r\n
                                            if (btn.hasClass("btn-close", false)) {\r\n
                                                me.fireEvent("comment:closeEditing", [commentId]);\r\n
                                                me.renderResolvedComboButtons();\r\n
                                            } else {\r\n
                                                if (btn.hasClass("btn-inner-edit", false)) {\r\n
                                                    if (!_.isUndefined(me.commentsView.reply)) {\r\n
                                                        me.fireEvent("comment:changeReply", [commentId, me.commentsView.reply, this.getActiveTextBoxVal()]);\r\n
                                                        me.commentsView.reply = undefined;\r\n
                                                    } else {\r\n
                                                        if (showEditBox) {\r\n
                                                            me.fireEvent("comment:change", [commentId, this.getActiveTextBoxVal()]);\r\n
                                                        }\r\n
                                                    }\r\n
                                                    me.fireEvent("comment:closeEditing");\r\n
                                                    readdresolves();\r\n
                                                } else {\r\n
                                                    if (btn.hasClass("btn-inner-close", false)) {\r\n
                                                        me.fireEvent("comment:closeEditing");\r\n
                                                        me.commentsView.reply = undefined;\r\n
                                                        readdresolves();\r\n
                                                    } else {\r\n
                                                        if (btn.hasClass("btn-resolve", false)) {\r\n
                                                            me.fireEvent("comment:resolve", [commentId]);\r\n
                                                            readdresolves();\r\n
                                                        } else {\r\n
                                                            if (!btn.hasClass("msg-reply") && !btn.hasClass("btn-resolve-check") && !btn.hasClass("btn-resolve")) {\r\n
                                                                me.fireEvent("comment:show", [commentId, false]);\r\n
                                                            }\r\n
                                                        }\r\n
                                                    }\r\n
                                                }\r\n
                                            }\r\n
                                        }\r\n
                                    }\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    });\r\n
                }\r\n
            }\r\n
            this.update();\r\n
            return this;\r\n
        },\r\n
        update: function () {\r\n
            if (this.commentsView && this.commentsView.scroller) {\r\n
                this.commentsView.scroller.update({\r\n
                    minScrollbarLength: 40\r\n
                });\r\n
            }\r\n
        },\r\n
        getPopover: function (sdkViewName) {\r\n
            if (_.isUndefined(this.popover)) {\r\n
                this.popover = new Common.Views.CommentsPopover({\r\n
                    store: this.popoverComments,\r\n
                    delegate: this,\r\n
                    renderTo: sdkViewName\r\n
                });\r\n
            }\r\n
            return this.popover;\r\n
        },\r\n
        showEditContainer: function (show) {\r\n
            var addCommentLink = $("#comments-add-link-ct", this.el),\r\n
            newCommentBlock = $("#comments-new-comment-ct", this.el),\r\n
            commentMsgBlock = $("#comments-messages", this.el);\r\n
            if (!show) {\r\n
                commentMsgBlock.css("bottom", 45);\r\n
                addCommentLink.css({\r\n
                    display: "table-row"\r\n
                });\r\n
                newCommentBlock.css({\r\n
                    display: "none"\r\n
                });\r\n
            } else {\r\n
                commentMsgBlock.css("bottom", 110);\r\n
                addCommentLink.css({\r\n
                    display: "none"\r\n
                });\r\n
                newCommentBlock.css({\r\n
                    display: "table-row"\r\n
                });\r\n
                this.txtComment.val("");\r\n
                this.txtComment.focus();\r\n
            }\r\n
        },\r\n
        onClickShowBoxDocumentComment: function () {\r\n
            this.fireEvent("comment:closeEditing");\r\n
            this.showEditContainer(true);\r\n
        },\r\n
        onClickAddDocumentComment: function () {\r\n
            this.fireEvent("comment:add", [this, this.txtComment.val().trim(), undefined, false, true]);\r\n
            this.txtComment.val("");\r\n
        },\r\n
        onClickCancelDocumentComment: function () {\r\n
            this.showEditContainer(false);\r\n
        },\r\n
        renderResolvedComboButtons: function () {\r\n
            if (_.isUndefined(this.openComboBoxes)) {\r\n
                this.openComboBoxes = [];\r\n
            }\r\n
            var me = this,\r\n
            i, openCombo, j = this.openComboBoxes.length - 1,\r\n
            buttons = $(this.commentsView.el).find(".resolve-ct-check");\r\n
            function onSelectResolveComment(comboBox) {\r\n
                if ($(comboBox.el).parent() && $(comboBox.el).parent().parent()) {\r\n
                    var id = ($(comboBox.el).parent().parent()).attr("id");\r\n
                    if (id) {\r\n
                        if (arguments[2]) {\r\n
                            arguments[2].stopImmediatePropagation();\r\n
                        }\r\n
                        me.fireEvent("comment:resolve", [undefined, id]);\r\n
                        me.renderResolvedComboButtons();\r\n
                        if (me.popover) {\r\n
                            me.popover.renderResolvedComboButtons();\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            for (j = this.openComboBoxes.length - 1; j >= 0; --j) {\r\n
                this.openComboBoxes[j].off();\r\n
                this.openComboBoxes[j].stopListening();\r\n
            }\r\n
            this.openComboBoxes = [];\r\n
            for (i = buttons.length - 1; i >= 0; --i) {\r\n
                openCombo = new Common.UI.ComboBox({\r\n
                    template: _.template(["<div>", \'<div class="resolved"></div>\', \'<div class="btn-resolve-check dropdown-toggle" data-toggle="dropdown">\', this.textResolved, "</div>", \'<span class="comments-caret"></span>\', \'<ul class="dropdown-menu <%= menuCls %>" style="\', "<%= menuStyle %>", \' role="menu">\', "<% _.each(items, function (item) { %>", \'<li id="<%= item.id %>" data-value="<%= item.value %>"><a href="#"><%= scope.getDisplayValue(item) %></a></li>\', "<% }); %>", "</ul>", "</div>"].join("")),\r\n
                    menuStyle: "min-width: 55px; margin-top: -7px; margin-left: -2px; padding: 0 0; right: 6px; left: auto;",\r\n
                    data: [{\r\n
                        value: 1,\r\n
                        displayValue: this.textOpenAgain\r\n
                    }]\r\n
                });\r\n
                openCombo.render($(buttons[i]));\r\n
                openCombo.on("selected", onSelectResolveComment);\r\n
                this.openComboBoxes.push(openCombo);\r\n
            }\r\n
        },\r\n
        hookTextBox: function () {\r\n
            var me = this,\r\n
            textBox = this.commentsView.getTextBox();\r\n
            textBox && textBox.keydown(function (event) {\r\n
                if ((event.ctrlKey || event.metaKey) && event.keyCode == Common.UI.Keys.RETURN) {\r\n
                    var buttonChangeComment = $("#id-comments-change");\r\n
                    if (buttonChangeComment && buttonChangeComment.length) {\r\n
                        buttonChangeComment.click();\r\n
                    }\r\n
                    event.stopImmediatePropagation();\r\n
                } else {\r\n
                    if (event.keyCode === Common.UI.Keys.TAB) {\r\n
                        var $this, end, start;\r\n
                        start = this.selectionStart;\r\n
                        end = this.selectionEnd;\r\n
                        $this = $(this);\r\n
                        $this.val($this.val().substring(0, start) + "\\t" + $this.val().substring(end));\r\n
                        this.selectionStart = this.selectionEnd = start + 1;\r\n
                        event.stopImmediatePropagation();\r\n
                        event.preventDefault();\r\n
                    }\r\n
                }\r\n
            });\r\n
        },\r\n
        getFixedQuote: function (quote) {\r\n
            return Common.Utils.String.ellipsis(Common.Utils.String.htmlEncode(quote), 120, true);\r\n
        },\r\n
        getUserName: function (username) {\r\n
            return Common.Utils.String.ellipsis(Common.Utils.String.htmlEncode(username), 15, true);\r\n
        },\r\n
        pickLink: function (message) {\r\n
            var arr = [],\r\n
            offset,\r\n
            len;\r\n
            message = Common.Utils.String.htmlEncode(message);\r\n
            message.replace(Common.Utils.emailStrongRe, function (subStr) {\r\n
                offset = arguments[arguments.length - 2];\r\n
                arr.push({\r\n
                    start: offset,\r\n
                    end: subStr.length + offset,\r\n
                    str: \'<a href="\' + subStr + \'">\' + subStr + "</a>"\r\n
                });\r\n
                return "";\r\n
            });\r\n
            message.replace(Common.Utils.ipStrongRe, function (subStr) {\r\n
                offset = arguments[arguments.length - 2];\r\n
                len = subStr.length;\r\n
                var elem = _.find(arr, function (item) {\r\n
                    return ((offset >= item.start) && (offset < item.end) || (offset <= item.start) && (offset + len > item.start));\r\n
                });\r\n
                if (!elem) {\r\n
                    arr.push({\r\n
                        start: offset,\r\n
                        end: len + offset,\r\n
                        str: \'<a href="\' + subStr + \'" target="_blank" data-can-copy="true">\' + subStr + "</a>"\r\n
                    });\r\n
                }\r\n
                return "";\r\n
            });\r\n
            message.replace(Common.Utils.hostnameStrongRe, function (subStr) {\r\n
                var ref = (!/(((^https?)|(^ftp)):\\/\\/)/i.test(subStr)) ? ("http://" + subStr) : subStr;\r\n
                offset = arguments[arguments.length - 2];\r\n
                len = subStr.length;\r\n
                var elem = _.find(arr, function (item) {\r\n
                    return ((offset >= item.start) && (offset < item.end) || (offset <= item.start) && (offset + len > item.start));\r\n
                });\r\n
                if (!elem) {\r\n
                    arr.push({\r\n
                        start: offset,\r\n
                        end: len + offset,\r\n
                        str: \'<a href="\' + ref + \'" target="_blank" data-can-copy="true">\' + subStr + "</a>"\r\n
                    });\r\n
                }\r\n
                return "";\r\n
            });\r\n
            arr = _.sortBy(arr, function (item) {\r\n
                return item.start;\r\n
            });\r\n
            var str_res = (arr.length > 0) ? (message.substring(0, arr[0].start) + arr[0].str) : message;\r\n
            for (var i = 1; i < arr.length; i++) {\r\n
                str_res += (message.substring(arr[i - 1].end, arr[i].start) + arr[i].str);\r\n
            }\r\n
            if (arr.length > 0) {\r\n
                str_res += message.substring(arr[i - 1].end, message.length);\r\n
            }\r\n
            return str_res;\r\n
        },\r\n
        textComments: "Comments",\r\n
        textAnonym: "Guest",\r\n
        textAddCommentToDoc: "Add Comment to Document",\r\n
        textAddComment: "Add Comment",\r\n
        textCancel: "Cancel",\r\n
        textAddReply: "Add Reply",\r\n
        textReply: "Reply",\r\n
        textClose: "Close",\r\n
        textResolved: "Resolved",\r\n
        textResolve: "Resolve",\r\n
        textEnterCommentHint: "Enter your comment here",\r\n
        textEdit: "Edit",\r\n
        textAdd: "Add",\r\n
        textOpenAgain: "Open Again"\r\n
    },\r\n
    Common.Views.Comments || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>60456</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
