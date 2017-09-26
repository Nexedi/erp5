/*
 *
 * (c) Copyright Ascensio System Limited 2010-2017
 *
 * This program is a free software product. You can redistribute it and/or
 * modify it under the terms of the GNU Affero General Public License (AGPL)
 * version 3 as published by the Free Software Foundation. In accordance with
 * Section 7(a) of the GNU AGPL its Section 15 shall be amended to the effect
 * that Ascensio System SIA expressly excludes the warranty of non-infringement
 * of any third-party rights.
 *
 * This program is distributed WITHOUT ANY WARRANTY; without even the implied
 * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE. For
 * details, see the GNU AGPL at: http://www.gnu.org/licenses/agpl-3.0.html
 *
 * You can contact Ascensio System SIA at Lubanas st. 125a-25, Riga, Latvia,
 * EU, LV-1021.
 *
 * The  interactive user interfaces in modified source and object code versions
 * of the Program must display Appropriate Legal Notices, as required under
 * Section 5 of the GNU AGPL version 3.
 *
 * Pursuant to Section 7(b) of the License you must retain the original Product
 * logo when distributing the program. Pursuant to Section 7(e) we decline to
 * grant you any rights under trademark law for use of our trademarks.
 *
 * All the Product's GUI elements, including illustrations and icon sets, as
 * well as technical writing content are licensed under the terms of the
 * Creative Commons Attribution-ShareAlike 4.0 International. See the License
 * terms at http://creativecommons.org/licenses/by-sa/4.0/legalcode
 *
*/
/**
 *  Comments.js
 *
 *  View
 *
 *  Created by Alexey Musinov on 16.01.14
 *  Copyright (c) 2014 Ascensio System SIA. All rights reserved.
 *
 */

if (Common === undefined)
    var Common = {};

Common.Views = Common.Views || {};

define([
    'text!common/main/lib/template/Comments.template',
    'text!common/main/lib/template/CommentsPanel.template',
    'text!common/main/lib/template/CommentsPopover.template',
    'common/main/lib/util/utils',
    'common/main/lib/component/Button',
    'common/main/lib/component/ComboBox',
    'common/main/lib/component/DataView',
    'common/main/lib/component/Layout',
    'common/main/lib/component/Window'
], function (commentsTemplate, panelTemplate, popoverTemplate) {
    'use strict';

    function replaceWords (template, words) {
        var word,
            value,
            tpl = template;

        for (word in words) {
            if (undefined !== word) {
                value = words[word];
                tpl = tpl.replace(new RegExp(word,'g'), value);
            }
        }

        return tpl;
    }

    Common.Views.CommentsPopover = Common.UI.Window.extend({

        // Window

        initialize : function (options) {
            var _options = {};

            _.extend(_options, {
                closable : false,
                width    : 265,
                height   : 120,
                header   : false,
                modal    : false
            }, options);

            this.template = options.template || [
                '<div class="box">',
                    '<div id="id-comments-popover" class="comments-popover"></div>',
                    '<div id="id-comments-arrow" class="comments-arrow"></div>',
                '</div>'
            ].join('');

            this.store      = options.store;
            this.delegate   = options.delegate;

            _options.tpl    = _.template(this.template, _options);

            this.arrow      = {margin: 20, width: 12, height: 34};
            this.sdkBounds  = {width: 0, height: 0, padding: 10, paddingTop: 20};

            Common.UI.Window.prototype.initialize.call(this, _options);
        },
        render: function () {
            Common.UI.Window.prototype.render.call(this);

            var me = this,
                t = this.delegate,
                window = this.$window;

            window.css({
                height: '',
                minHeight: '',
                overflow: 'hidden',
                position: 'absolute',
                zIndex: '990'
            });

            // for spreadsheets - bug 23127

//            if ($('#ws-h-scrollbar').length) {
//                window.css({zIndex: '5'});
//            }

            var body = window.find('.body');
            if (body) {
                body.css('position', 'relative');
            }

            window.on('click', _.bind(function() {
                window.css({zIndex: '991'});
                Common.NotificationCenter.trigger('comments:click');
            }, this));
            Common.NotificationCenter.on('review:click', function() {
                window.css({zIndex: '990'});
            });

            var PopoverDataView = Common.UI.DataView.extend((function() {

                var parentView = me;

                return {

                    options : {
                        handleSelect: false,
                        scrollable: true,
                        template: _.template('<div class="dataview-ct inner" style="overflow-y: hidden;"></div>')
                    },

                    getTextBox: function () {
                        var text = $(this.el).find('textarea');
                        return (text && text.length) ? text : undefined;
                    },
                    setFocusToTextBox: function (blur) {
                        var text = $(this.el).find('textarea');
                        if (blur) {
                            text.blur();
                        } else {
                            if (text && text.length) {
                                var val = text.val();
                                text.focus();
                                text.val('');
                                text.val(val);
                            }
                        }
                    },
                    getActiveTextBoxVal: function () {
                        var text = $(this.el).find('textarea');
                        return (text && text.length) ? text.val().trim() : '';
                    },
                    autoHeightTextBox: function () {
                        var view = this,
                            textBox = this.$el.find('textarea'),
                            domTextBox = null,
                            minHeight = 50,
                            lineHeight = 0,
                            scrollPos = 0,
                            oldHeight = 0,
                            newHeight = 0;

                        function updateTextBoxHeight() {
                            scrollPos = $(view.scroller.el).scrollTop();

                            if (domTextBox.scrollHeight > domTextBox.clientHeight) {
                                textBox.css({height: (domTextBox.scrollHeight + lineHeight) + 'px'});

                                parentView.calculateSizeOfContent();
                            } else {
                                oldHeight = domTextBox.clientHeight;
                                if (oldHeight >= minHeight) {
                                    textBox.css({height: minHeight + 'px'});

                                    if (domTextBox.scrollHeight > domTextBox.clientHeight) {
                                        newHeight = Math.max(domTextBox.scrollHeight + lineHeight, minHeight);
                                        textBox.css({height: newHeight + 'px'});
                                    }

                                    parentView.calculateSizeOfContent();
                                    parentView.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                    parentView.calculateSizeOfContent();
                                }
                            }

                            view.scroller.scrollTop(scrollPos);
                            view.autoScrollToEditButtons();
                        }

                        if (textBox && textBox.length) {
                            domTextBox = textBox.get(0);

                            if (domTextBox) {
                                lineHeight = parseInt(textBox.css('lineHeight'), 10) * 0.25;
                                updateTextBoxHeight();
                                textBox.bind('input propertychange', updateTextBoxHeight)
                            }
                        }

                        this.textBox = textBox;
                    },
                    clearTextBoxBind: function () {
                        if (this.textBox) {
                            this.textBox.unbind('input propertychange');
                            this.textBox = undefined;
                        }
                    },
                    autoScrollToEditButtons: function () {
                        var button = $('#id-comments-change-popover'),  // TODO: add to cache
                            btnBounds = null,
                            contentBounds = this.el.getBoundingClientRect(),
                            moveY = 0,
                            padding = 7;

                        if (button.length) {
                            btnBounds = button.get(0).getBoundingClientRect();
                            if (btnBounds && contentBounds) {
                                moveY = contentBounds.bottom - (btnBounds.bottom + padding);
                                if (moveY < 0) {
                                    this.scroller.scrollTop(this.scroller.getScrollTop() - moveY);
                                }
                            }
                        }
                    }
                }
            })());
            if (PopoverDataView) {
                if (this.commentsView) {
                    this.commentsView.render($('#id-comments-popover'));
                    this.commentsView.onResetItems();
                } else {
                    this.commentsView = new PopoverDataView({
                        el: $('#id-comments-popover'),
                        store: me.store,
                        itemTemplate: _.template(replaceWords(popoverTemplate, {
                                textAddReply: t.textAddReply,
                                textAdd: t.textAdd,
                                textCancel: t.textCancel,
                                textEdit: t.textEdit,
                                textReply: t.textReply,
                                textClose: t.textClose,
                                maxCommLength: Asc.c_oAscMaxCellOrCommentLength
                            })
                        )
                    });

                    var addtooltip = function (dataview, view, record) {
                        if (view.tipsArray) {
                            view.tipsArray.forEach(function(item){
                                item.remove();
                            });
                        }

                        var arr = [],
                            btns = $(view.el).find('.btn-resolve');
                        btns.tooltip({title: t.textResolve, placement: 'cursor'});
                        btns.each(function(idx, item){
                            arr.push($(item).data('bs.tooltip').tip());
                        });
                        btns = $(view.el).find('.btn-resolve-check');
                        btns.tooltip({title: t.textOpenAgain, placement: 'cursor'});
                        btns.each(function(idx, item){
                            arr.push($(item).data('bs.tooltip').tip());
                        });
                        view.tipsArray = arr;
                    };

                    var onCommentsViewMouseOver = function() {
                        me._isMouseOver = true;
                    };

                    var onCommentsViewMouseOut = function() {
                        me._isMouseOver = false;
                    };

                    this.commentsView.on('item:add', addtooltip);
                    this.commentsView.on('item:remove', addtooltip);
                    this.commentsView.on('item:change', addtooltip);
                    this.commentsView.cmpEl.on('mouseover', onCommentsViewMouseOver).on('mouseout',  onCommentsViewMouseOut);

                    this.commentsView.on('item:click', function (picker, item, record, e) {
                        var btn, showEditBox, showReplyBox, commentId, replyId, hideAddReply;

                        function readdresolves() {
                            me.update();
                        }

                        btn = $(e.target);
                        if (btn) {
                            showEditBox = record.get('editTextInPopover');
                            showReplyBox = record.get('showReplyInPopover');
                            hideAddReply = record.get('hideAddReply');
                            commentId = record.get('uid');
                            replyId = btn.attr('data-value');

                            if (record.get('hint')) {
                                t.fireEvent('comment:disableHint', [record]);
                                return;
                            }

                            if (btn.hasClass('btn-edit')) {
                                if (!_.isUndefined(replyId)) {
                                    t.fireEvent('comment:closeEditing', [commentId]);
                                    t.fireEvent('comment:editReply', [commentId, replyId, true]);

                                    this.replyId = replyId;

                                    this.autoHeightTextBox();

                                    me.calculateSizeOfContent();
                                    me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                    me.calculateSizeOfContent();

                                    readdresolves();

                                    me.hookTextBox();

                                    this.autoScrollToEditButtons();
                                    this.setFocusToTextBox();
                                } else {
                                    if (!showEditBox) {
                                        t.fireEvent('comment:closeEditing');
                                        record.set('editTextInPopover', true);

                                        t.fireEvent('comment:show', [commentId]);

                                        this.autoHeightTextBox();

                                        me.calculateSizeOfContent();
                                        me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                        me.calculateSizeOfContent();

                                        readdresolves();

                                        me.hookTextBox();

                                        this.autoScrollToEditButtons();
                                        this.setFocusToTextBox();
                                    }
                                }
                            } else if (btn.hasClass('btn-delete')) {
                                if (!_.isUndefined(replyId)) {
                                    t.fireEvent('comment:removeReply', [commentId, replyId]);

                                    me.calculateSizeOfContent();
                                    me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                    me.calculateSizeOfContent();

                                } else {
                                    t.fireEvent('comment:remove', [commentId]);
                                }

                                t.fireEvent('comment:closeEditing');

                                readdresolves();

                            } else if (btn.hasClass('user-reply')) {
                                t.fireEvent('comment:closeEditing');
                                record.set('showReplyInPopover', true);

                                me.calculateSizeOfContent();
                                me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                me.calculateSizeOfContent();

                                readdresolves();

                                this.autoHeightTextBox();
                                me.hookTextBox();

                                this.autoScrollToEditButtons();
                                this.setFocusToTextBox();
                            } else if (btn.hasClass('btn-reply', false)) {
                                if (showReplyBox) {
                                    this.clearTextBoxBind();

                                    t.fireEvent('comment:addReply', [commentId, this.getActiveTextBoxVal()]);
                                    t.fireEvent('comment:closeEditing');

                                    readdresolves();
                                }
                            } else if (btn.hasClass('btn-close', false)) {
                                t.fireEvent('comment:closeEditing', [commentId]);
                                me.calculateSizeOfContent();
                                t.fireEvent('comment:show', [commentId]);

                                readdresolves();

                            } else if (btn.hasClass('btn-inner-edit', false)) {

                                if (record.get('dummy')) {
                                    t.fireEvent('comment:addDummyComment', [this.getActiveTextBoxVal()]);
                                    return;
                                }

                                this.clearTextBoxBind();

                                if (!_.isUndefined(this.replyId)) {
                                    t.fireEvent('comment:changeReply', [commentId, this.replyId, this.getActiveTextBoxVal()]);
                                    this.replyId = undefined;
                                    t.fireEvent('comment:closeEditing');
                                } else if (showEditBox) {
                                    t.fireEvent('comment:change', [commentId, this.getActiveTextBoxVal()]);
                                    t.fireEvent('comment:closeEditing');
                                    me.calculateSizeOfContent();
                                }

                                readdresolves();

                            } else if (btn.hasClass('btn-inner-close', false)) {
                                if (record.get('dummy')) {
                                    me.hide();
                                    return;
                                }

                                if (hideAddReply && this.getActiveTextBoxVal().length > 0) {
                                    me.saveText();
                                    record.set('hideAddReply', false);
                                    this.getTextBox().val(me.textVal);
                                    this.autoHeightTextBox();
                                } else {

                                    this.clearTextBoxBind();

                                    t.fireEvent('comment:closeEditing', [commentId]);
                                }

                                this.replyId = undefined;

                                me.calculateSizeOfContent();
                                me.setLeftTop(me.arrowPosX, me.arrowPosY, me.leftX);
                                me.calculateSizeOfContent();

                                readdresolves();

                            } else if (btn.hasClass('btn-resolve', false)) {
                                var tip = btn.data('bs.tooltip');
                                if (tip) tip.dontShow = true;

                                t.fireEvent('comment:resolve', [commentId]);

                                readdresolves();
                            } else if (btn.hasClass('btn-resolve-check', false)) {
                                var tip = btn.data('bs.tooltip');
                                if (tip) tip.dontShow = true;

                                t.fireEvent('comment:resolve', [commentId]);

                                readdresolves();
                            }
                        }
                    });
                    me.on({
                        'show': function () {
                            me.commentsView.autoHeightTextBox();
                            me.$window.find('textarea').keydown(function (event) {
                                if (event.keyCode == Common.UI.Keys.ESC) {
                                    me.hide();
                                }
                            });
                        },
                        'animate:before': function () {
                            var text = me.$window.find('textarea');
                            if (text && text.length)
                                text.focus();
                        }
                    });
                }
            }
        },
        show: function (animate, loadText, focus, showText) {
            this.options.animate = animate;

            var me = this,textBox = this.commentsView.getTextBox();

            if (loadText && this.textVal) {
                textBox && textBox.val(this.textVal);
            }

            if (showText && showText.length) {
                textBox && textBox.val(showText);
            }

//            this.calculateSizeOfContent();
//            this.commentsView.autoHeightTextBox();

            Common.UI.Window.prototype.show.call(this);

            if (this.commentsView.scroller) {
                this.commentsView.scroller.update({minScrollbarLength: 40, alwaysVisibleY: true});
            }

            this.hookTextBox();
        },
        hide: function () {
            if (this.handlerHide) {
                this.handlerHide ();
            }

            Common.UI.Window.prototype.hide.call(this);

            if (!_.isUndefined(this.e) && this.e.keyCode == Common.UI.Keys.ESC) {
                this.e.preventDefault();
                this.e.stopImmediatePropagation();
                this.e = undefined;
            }
        },

        // CommentsPopover

        update: function () {
            if (this.commentsView && this.commentsView.scroller) {
                this.commentsView.scroller.update({minScrollbarLength: 40, alwaysVisibleY: true});
            }
        },

        isVisible: function () {
            return (this.$window && this.$window.is(':visible'));
        },
        setLeftTop: function (posX, posY, leftX, loadInnerValues, retainContent) {
            if (!this.$window)
                this.render();

            if (loadInnerValues) {
                posX = this.arrowPosX;
                posY = this.arrowPosY;
                leftX = this.leftX;
            }

            if (_.isUndefined(posX) && _.isUndefined(posY))
                return;

            this.arrowPosX = posX;
            this.arrowPosY = posY;
            this.leftX = leftX;

            var commentsView = $('#id-comments-popover'),
                arrowView = $('#id-comments-arrow'),
                editorView = $('#editor_sdk'),
                editorBounds = null,
                sdkBoundsHeight = 0,
                sdkBoundsTop = 0,
                sdkBoundsLeft = 0,
                sdkPanelRight = '',
                sdkPanelRightWidth = 0,
                sdkPanelLeft = '',
                sdkPanelLeftWidth = 0,
                sdkPanelThumbs = '', // for PE
                sdkPanelThumbsWidth = 0, // for PE
                sdkPanelTop = '',
                sdkPanelHeight = 0,
                leftPos = 0,
                windowWidth = 0,
                outerHeight = 0,
                topPos = 0,
                sdkBoundsTopPos = 0;

            if (commentsView && arrowView && editorView && editorView.get(0)) {
                editorBounds = editorView.get(0).getBoundingClientRect();
                if (editorBounds) {
                    sdkBoundsHeight = editorBounds.height - this.sdkBounds.padding * 2;

                    this.$window.css({maxHeight: sdkBoundsHeight + 'px'});

                    this.sdkBounds.width = editorBounds.width;
                    this.sdkBounds.height = editorBounds.height;

                    // LEFT CORNER

                    if (!_.isUndefined(posX)) {

                        sdkPanelRight = $('#id_vertical_scroll');
                        if (sdkPanelRight.length) {
                            sdkPanelRightWidth = (sdkPanelRight.css('display') !== 'none') ? sdkPanelRight.width() : 0;
                        } else {
                            sdkPanelRight = $('#ws-v-scrollbar');
                            if (sdkPanelRight.length) {
                                sdkPanelRightWidth = (sdkPanelRight.css('display') !== 'none') ? sdkPanelRight.width() : 0;
                            }
                        }

                        this.sdkBounds.width -= sdkPanelRightWidth;

                        sdkPanelLeft = $('#id_panel_left');
                        if (sdkPanelLeft.length) {
                            sdkPanelLeftWidth = (sdkPanelLeft.css('display') !== 'none') ? sdkPanelLeft.width() : 0;
                        }
                        sdkPanelThumbs = $('#id_panel_thumbnails');
                        if (sdkPanelThumbs.length) {
                            sdkPanelThumbsWidth = (sdkPanelThumbs.css('display') !== 'none') ? sdkPanelThumbs.width() : 0;
                            this.sdkBounds.width -= sdkPanelThumbsWidth;
                        }

                        leftPos = Math.min(sdkBoundsLeft + posX + this.arrow.width, sdkBoundsLeft + this.sdkBounds.width - this.$window.outerWidth() - 25);
                        leftPos = Math.max(sdkBoundsLeft + sdkPanelLeftWidth + this.arrow.width, leftPos);

                        arrowView.removeClass('right').addClass('left');
                        
                        if (!_.isUndefined(leftX)) {
                            windowWidth = this.$window.outerWidth();
                            if (windowWidth) {
                                if ((posX + windowWidth > this.sdkBounds.width - this.arrow.width + 5) && (this.leftX > windowWidth)) {
                                    leftPos = this.leftX - windowWidth + sdkBoundsLeft - this.arrow.width;
                                    arrowView.removeClass('left').addClass('right');
                                } else {
                                    leftPos = sdkBoundsLeft + posX + this.arrow.width;
                                }
                            }
                        }

                        this.$window.css('left', leftPos + 'px');
                    }

                    // TOP CORNER

                    if (!_.isUndefined(posY)) {
                        sdkPanelTop = $('#id_panel_top');
                        sdkBoundsTopPos = sdkBoundsTop;
                        if (sdkPanelTop.length) {
                            sdkPanelHeight = (sdkPanelTop.css('display') !== 'none') ? sdkPanelTop.height() : 0;
                            sdkBoundsTopPos += this.sdkBounds.paddingTop;
                        } else {
                            sdkPanelTop = $('#ws-h-scrollbar');
                            if (sdkPanelTop.length) {
                                sdkPanelHeight = (sdkPanelTop.css('display') !== 'none') ? sdkPanelTop.height() : 0;
                            }
                        }

                        this.sdkBounds.height -= sdkPanelHeight;

                        outerHeight = this.$window.outerHeight();

                        topPos = Math.min(sdkBoundsTop + sdkBoundsHeight - outerHeight, this.arrowPosY + sdkBoundsTop - this.arrow.height);
                        topPos = Math.max(topPos, sdkBoundsTopPos);

                        this.$window.css('top', topPos + 'px');
                    }
                }
            }
            if (!retainContent)
                this.calculateSizeOfContent();
        },
        calculateSizeOfContent: function (testVisible) {
            if (testVisible && !this.$window.is(':visible'))
                return;

            this.$window.css({overflow: 'hidden'});

            var arrowView = $('#id-comments-arrow'),
                commentsView = $('#id-comments-popover'),
                contentBounds = null,
                editorView = null,
                editorBounds = null,
                sdkBoundsHeight = 0,
                sdkBoundsTop = 0,
                sdkBoundsLeft = 0,
                sdkPanelTop  = '',
                sdkPanelHeight = 0,
                arrowPosY = 0,
                windowHeight = 0,
                outerHeight = 0,
                topPos = 0,
                sdkBoundsTopPos = 0;

            if (commentsView && arrowView && commentsView.get(0)) {
                commentsView.css({height: '100%'});

                contentBounds = commentsView.get(0).getBoundingClientRect();
                if (contentBounds) {
                    editorView = $('#editor_sdk');
                    if (editorView && editorView.get(0)) {
                        editorBounds = editorView.get(0).getBoundingClientRect();
                        if (editorBounds) {
                            sdkBoundsHeight = editorBounds.height - this.sdkBounds.padding * 2;
                            sdkBoundsTopPos = sdkBoundsTop;
                            windowHeight = this.$window.outerHeight();

                            // TOP CORNER

                            sdkPanelTop = $('#id_panel_top');
                            if (sdkPanelTop.length) {
                                sdkPanelHeight = (sdkPanelTop.css('display') !== 'none') ? sdkPanelTop.height() : 0;
                                sdkBoundsTopPos += this.sdkBounds.paddingTop;
                            } else {
                                sdkPanelTop = $('#ws-h-scrollbar');
                                if (sdkPanelTop.length) {
                                    sdkPanelHeight = (sdkPanelTop.css('display') !== 'none') ? sdkPanelTop.height() : 0;
                                }
                            }

                            outerHeight = Math.max(commentsView.outerHeight(), this.$window.outerHeight());

                            if (sdkBoundsHeight <= outerHeight) {
                                this.$window.css({
                                    maxHeight: sdkBoundsHeight - sdkPanelHeight + 'px',
                                    top: sdkBoundsTop + sdkPanelHeight + 'px'});

                                commentsView.css({height: sdkBoundsHeight - sdkPanelHeight - 3 + 'px'});

                               // arrowPosY = Math.max(this.arrow.margin, this.arrowPosY - sdkPanelHeight - this.arrow.width);
                                arrowPosY = Math.min(arrowPosY, sdkBoundsHeight - (sdkPanelHeight + this.arrow.margin + this.arrow.width));

                                arrowView.css({top: arrowPosY + 'px'});
                            } else {

                                outerHeight = windowHeight;

                                if (outerHeight > 0) {
                                    if (contentBounds.top + outerHeight > sdkBoundsHeight + sdkBoundsTop || contentBounds.height === 0) {
                                        topPos = Math.min(sdkBoundsTop + sdkBoundsHeight - outerHeight, this.arrowPosY + sdkBoundsTop - this.arrow.height);
                                        topPos = Math.max(topPos, sdkBoundsTopPos);

                                        this.$window.css({top: topPos + 'px'});
                                    }
                                }

                                arrowPosY = Math.max(this.arrow.margin, this.arrowPosY - (sdkBoundsHeight - outerHeight) - this.arrow.width);
                                arrowPosY = Math.min(arrowPosY, outerHeight - this.arrow.margin - this.arrow.width);

                                arrowView.css({top: arrowPosY + 'px'});
                            }
                        }
                    }
                }
            }

            this.$window.css({overflow: ''});
        },
        saveText: function (clear) {
            if (this.commentsView && this.commentsView.cmpEl.find('.lock-area').length<1) {
                this.textVal = undefined;
                if (!clear) {
                    this.textVal = this.commentsView.getActiveTextBoxVal();
                } else {
                    this.commentsView.clearTextBoxBind();
                }
            }
        },
        loadText: function () {
            if (this.textVal && this.commentsView) {
                this.commentsView.getTextBox().val(this.textVal);
            }
        },
        getEditText: function () {
            if (this.commentsView) {
                return this.commentsView.getActiveTextBoxVal();
            }

            return undefined;
        },

        hookTextBox: function () {
            var me = this, textBox = this.commentsView.getTextBox();

            textBox && textBox.keydown(function (event) {
                if ((event.ctrlKey || event.metaKey) && !event.altKey && event.keyCode === Common.UI.Keys.RETURN) {
                    var buttonChangeComment = $('#id-comments-change-popover');
                    if (buttonChangeComment && buttonChangeComment.length) {
                        buttonChangeComment.click();
                    }

                    event.stopImmediatePropagation();
                } else if (event.keyCode === Common.UI.Keys.TAB) {
                    var $this, end, start;
                    start = this.selectionStart;
                    end = this.selectionEnd;
                    $this = $(this);
                    $this.val($this.val().substring(0, start) + '\t' + $this.val().substring(end));
                    this.selectionStart = this.selectionEnd = start + 1;

                    event.stopImmediatePropagation();
                    event.preventDefault();
                }

                me.e = event;
            });
        },

        hideTips: function() {
            if (this.commentsView)
                _.each(this.commentsView.dataViewItems, function(item) {
                    if (item.tipsArray) {
                        item.tipsArray.forEach(function(item){
                            item.hide();
                        });
                    }
                }, this);
        },

        isCommentsViewMouseOver: function() {
            return this._isMouseOver;
        }
    });

    Common.Views.Comments = Common.UI.BaseView.extend(_.extend({
        el: '#left-panel-comments',
        template: _.template(panelTemplate),

        addCommentHeight: 45,
        newCommentHeight: 110,
        textBoxAutoSizeLocked: undefined, // disable autosize textbox

        initialize: function (options) {
            Common.UI.BaseView.prototype.initialize.call(this, options);

            this.store = this.options.store;
            this.popoverComments = this.options.popoverComments;
        },
        render: function () {
            var me = this;

            this.$el.html(this.template({
                textAddCommentToDoc: me.textAddCommentToDoc,
                textAddComment: me.textAddComment,
                textCancel: me.textCancel,
                textEnterCommentHint: me.textEnterCommentHint,
                maxCommLength: Asc.c_oAscMaxCellOrCommentLength
            }));

            this.buttonAddCommentToDoc = new Common.UI.Button({
                el: $('.btn.new',this.$el),
                enableToggle: false
            });
            this.buttonAdd = new Common.UI.Button({
                action: 'add',
                el: $('.btn.add', this.$el),
                enableToggle: false
            });
            this.buttonCancel = new Common.UI.Button({
                el: $('.btn.cancel', this.$el),
                enableToggle: false
            });

            this.buttonAddCommentToDoc.on('click', _.bind(this.onClickShowBoxDocumentComment, this));
            this.buttonAdd.on('click', _.bind(this.onClickAddDocumentComment, this));
            this.buttonCancel.on('click', _.bind(this.onClickCancelDocumentComment, this));

            this.txtComment = $('#comment-msg-new', this.el);
            this.txtComment.keydown(function (event) {
                if ((event.ctrlKey || event.metaKey) && !event.altKey && event.keyCode == Common.UI.Keys.RETURN) {
                    me.onClickAddDocumentComment();
                    event.stopImmediatePropagation();
                } else if (event.keyCode === Common.UI.Keys.TAB) {
                    var $this, end, start;
                    start = this.selectionStart;
                    end = this.selectionEnd;
                    $this = $(this);
                    $this.val($this.val().substring(0, start) + '\t' + $this.val().substring(end));
                    this.selectionStart = this.selectionEnd = start + 1;

                    event.stopImmediatePropagation();
                    event.preventDefault();
                }
            });

            var CommentsPanelDataView = Common.UI.DataView.extend((function() {

                var parentView = me;

                return {

                    options : {
                        handleSelect: false,
                        scrollable: true,
                        listenStoreEvents: false,
                        template: _.template('<div class="dataview-ct inner"></div>')
                    },

                    getTextBox: function () {
                        var text = $(this.el).find('textarea');
                        return (text && text.length) ? text : undefined;
                    },
                    setFocusToTextBox: function () {
                        var text = $(this.el).find('textarea');
                        if (text && text.length) {
                            var val = text.val();
                            text.focus();
                            text.val('');
                            text.val(val);
                        }
                    },
                    getActiveTextBoxVal: function () {
                        var text = $(this.el).find('textarea');
                        return (text && text.length) ? text.val().trim() : '';
                    },
                    autoHeightTextBox: function () {
                        var view = this,
                            textBox = $(this.el).find('textarea'),
                            domTextBox = null,
                            minHeight = 50,
                            lineHeight = 0,
                            scrollPos = 0,
                            oldHeight = 0,
                            newHeight = 0;

                        function updateTextBoxHeight() {
                            if (domTextBox.scrollHeight > domTextBox.clientHeight) {
                                textBox.css({height: (domTextBox.scrollHeight + lineHeight) + 'px'});
                            } else {
                                oldHeight = domTextBox.clientHeight;
                                if (oldHeight >= minHeight) {

                                    textBox.css({height: minHeight + 'px'});

                                    if (domTextBox.scrollHeight > domTextBox.clientHeight) {
                                        newHeight = Math.max(domTextBox.scrollHeight + lineHeight, minHeight);
                                        textBox.css({height: newHeight + 'px'});
                                    }
                                }
                            }

                            view.autoScrollToEditButtons();
                        }

                        if (textBox && textBox.length) {
                            domTextBox = textBox.get(0);

                            if (domTextBox) {
                                lineHeight = parseInt(textBox.css('lineHeight'), 10) * 0.25;
                                updateTextBoxHeight();
                                textBox.bind('input propertychange', updateTextBoxHeight)
                            }
                        }

                        this.textBox = textBox;
                    },
                    clearTextBoxBind: function () {
                        if (this.textBox) {
                            this.textBox.unbind('input propertychange');
                            this.textBox = undefined;
                        }
                    },
                    autoScrollToEditButtons: function () {
                        var button = $('#id-comments-change'),  // TODO: add to cache
                            btnBounds = null,
                            contentBounds = this.el.getBoundingClientRect(),
                            moveY = 0,
                            padding = 7;

                        if (button.length) {
                            btnBounds = button.get(0).getBoundingClientRect();
                            if (btnBounds && contentBounds) {
                                moveY = contentBounds.bottom - (btnBounds.bottom + padding);
                                if (moveY < 0) {
                                    this.scroller.scrollTop(this.scroller.getScrollTop() - moveY);
                                }
                            }
                        }
                    }
                }
            })());
            if (CommentsPanelDataView) {
                if (this.commentsView) {
                    this.commentsView.render($('.messages-ct',me.el));
                    this.commentsView.onResetItems();
                } else {
                    this.commentsView = new CommentsPanelDataView({
                        el: $('.messages-ct',me.el),
                        store: me.store,
                        itemTemplate: _.template(replaceWords(commentsTemplate, {
                            textAddReply: me.textAddReply,
                            textAdd: me.textAdd,
                            textCancel: me.textCancel,
                            textEdit: me.textEdit,
                            textReply: me.textReply,
                            textClose: me.textClose,
                            maxCommLength: Asc.c_oAscMaxCellOrCommentLength
                        }))
                    });

                    var addtooltip = function (dataview, view, record) {
                        if (view.tipsArray) {
                            view.tipsArray.forEach(function(item){
                                item.remove();
                            });
                        }

                        var arr = [],
                            btns = $(view.el).find('.btn-resolve');
                        btns.tooltip({title: me.textResolve, placement: 'cursor'});
                        btns.each(function(idx, item){
                            arr.push($(item).data('bs.tooltip').tip());
                        });
                        btns = $(view.el).find('.btn-resolve-check');
                        btns.tooltip({title: me.textOpenAgain, placement: 'cursor'});
                        btns.each(function(idx, item){
                            arr.push($(item).data('bs.tooltip').tip());
                        });
                        view.tipsArray = arr;
                    };
                    this.commentsView.on('item:add', addtooltip);
                    this.commentsView.on('item:remove', addtooltip);
                    this.commentsView.on('item:change', addtooltip);

                    this.commentsView.on('item:click', function (picker, item, record, e) {
                        var btn, showEditBox, showReplyBox, commentId, replyId, hideAddReply;

                        function readdresolves() {
                            me.update();
                        }

                        btn = $(e.target);
                        if (btn) {
                            showEditBox = record.get('editText');
                            showReplyBox = record.get('showReply');
                            commentId = record.get('uid');
                            replyId =  btn.attr('data-value');

                            if (btn.hasClass('btn-edit')) {
                                if (!_.isUndefined(replyId)) {
                                    me.fireEvent('comment:closeEditing', [commentId]);
                                    me.fireEvent('comment:editReply', [commentId, replyId]);

                                    me.commentsView.reply = replyId;

                                    this.autoHeightTextBox();

                                    readdresolves();

                                    me.hookTextBox();

                                    this.autoScrollToEditButtons();
                                    this.setFocusToTextBox();
                                } else {

                                    if (!showEditBox) {
                                        me.fireEvent('comment:closeEditing');
                                        record.set('editText', true);

                                        this.autoHeightTextBox();
                                        readdresolves();
                                        this.setFocusToTextBox();
                                        me.hookTextBox();
                                    }
                                }
                            } else if (btn.hasClass('btn-delete')) {
                                if (!_.isUndefined(replyId)) {
                                    me.fireEvent('comment:removeReply', [commentId, replyId]);
                                } else {
                                    me.fireEvent('comment:remove', [commentId]);
                                }

                                me.fireEvent('comment:closeEditing');
                                readdresolves();
                            } else if (btn.hasClass('user-reply')) {
                                me.fireEvent('comment:closeEditing');
                                record.set('showReply', true);

                                readdresolves();

                                this.autoHeightTextBox();
                                me.hookTextBox();

                                this.autoScrollToEditButtons();
                                this.setFocusToTextBox();
                            } else if (btn.hasClass('btn-reply', false)) {
                                if (showReplyBox) {
                                    me.fireEvent('comment:addReply', [commentId, this.getActiveTextBoxVal()]);
                                    me.fireEvent('comment:closeEditing');

                                    readdresolves();
                                }
                            } else if (btn.hasClass('btn-close', false)) {

                                me.fireEvent('comment:closeEditing', [commentId]);

                            } else if (btn.hasClass('btn-inner-edit', false)) {
                                if (!_.isUndefined(me.commentsView.reply)) {
                                    me.fireEvent('comment:changeReply', [commentId, me.commentsView.reply, this.getActiveTextBoxVal()]);
                                    me.commentsView.reply = undefined;
                                } else if (showEditBox) {
                                    me.fireEvent('comment:change', [commentId, this.getActiveTextBoxVal()]);
                                }

                                me.fireEvent('comment:closeEditing');

                                readdresolves();

                            } else if (btn.hasClass('btn-inner-close', false)) {
                                me.fireEvent('comment:closeEditing');

                                me.commentsView.reply = undefined;

                                readdresolves();
                            } else if (btn.hasClass('btn-resolve', false)) {
                                var tip = btn.data('bs.tooltip');
                                if (tip) tip.dontShow = true;

                                me.fireEvent('comment:resolve', [commentId]);

                                readdresolves();
                            } else if (btn.hasClass('btn-resolve-check', false)) {
                                var tip = btn.data('bs.tooltip');
                                if (tip) tip.dontShow = true;

                                me.fireEvent('comment:resolve', [commentId]);

                                readdresolves();
                            } else if (!btn.hasClass('msg-reply') &&
                                !btn.hasClass('btn-resolve-check') &&
                                !btn.hasClass('btn-resolve')) {
                                me.fireEvent('comment:show', [commentId, false]);
                            }
                        }
                    });
                }
            }

            this.setupLayout();
            this.update();

            return this;
        },
        update: function () {
            this.updateLayout();
            this.updateScrolls();
        },
        updateScrolls: function () {
            if (this.commentsView && this.commentsView.scroller) {
                this.commentsView.scroller.update({minScrollbarLength: 40, alwaysVisibleY: true});
            }
        },

        getPopover: function (sdkViewName) {

            if (_.isUndefined(this.popover)) {
                this.popover = new Common.Views.CommentsPopover({
                    store    : this.popoverComments,
                    delegate : this,
                    renderTo : sdkViewName
                });
            }

            return this.popover;
        },

        showEditContainer: function (show) {
            var addCommentLink  = $('.add-link-ct', this.el),
                newCommentBlock = $('.new-comment-ct', this.el),
                commentMsgBlock = $('.messages-ct', this.el),
                container = $('#comments-box', this.el);

            this.layout.freezePanels(!show);

            if (!show) {
                addCommentLink.css({display: 'table-row'});
                newCommentBlock.css({display: 'none'});
            } else {
                addCommentLink.css({display: 'none'});
                newCommentBlock.css({display: 'table-row'});

                this.txtComment.val('');
                this.txtComment.focus();

                this.textBoxAutoSizeLocked = undefined;
            }

            this.updateLayout();
            this.updateScrolls();
        },

        onClickShowBoxDocumentComment: function () {
            this.fireEvent('comment:closeEditing');
            this.showEditContainer(true);
        },
        onClickAddDocumentComment: function () {
            this.fireEvent('comment:add', [this, this.txtComment.val().trim(), undefined, false, true]);
            this.txtComment.val('');
        },
        onClickCancelDocumentComment: function () {
            this.showEditContainer(false);
        },

        hookTextBox: function () {
            var me = this,
                textBox = this.commentsView.getTextBox();

            textBox && textBox.keydown(function (event) {
                if ((event.ctrlKey || event.metaKey) && !event.altKey && event.keyCode == Common.UI.Keys.RETURN) {
                    var buttonChangeComment = $('#id-comments-change');
                    if (buttonChangeComment && buttonChangeComment.length) {
                        buttonChangeComment.click();
                    }

                    event.stopImmediatePropagation();
                } else if (event.keyCode === Common.UI.Keys.TAB) {
                    var $this, end, start;
                    start = this.selectionStart;
                    end = this.selectionEnd;
                    $this = $(this);
                    $this.val($this.val().substring(0, start) + '\t' + $this.val().substring(end));
                    this.selectionStart = this.selectionEnd = start + 1;

                    event.stopImmediatePropagation();
                    event.preventDefault();
                }
            });
        },

        setupLayout: function () {
            var me = this, parent = $(me.el);

            var add = $('.new-comment-ct', me.el),
                to = $('.add-link-ct', me.el),
                container = $('#comments-box', me.el),
                items = container.find(' > .layout-item');

            me.layout = new Common.UI.VBoxLayout({
                box: container,
                freeze: true,
                items: [
                    {el: items[0], rely: true,
                        resize: {
                            hidden: false,
                            autohide: false,
                            fmin: (function () {

                                var height = container.height();

                                if (add.css('display') !== 'none') {
                                    if (height * 0.5 < me.newCommentHeight)
                                        return height - me.newCommentHeight;
                                }

                                return height * 0.5;
                            }),
                            fmax: (function () {

                                if (add.css('display') !== 'none')
                                    return container.height() - me.newCommentHeight;

                                return container.height() - me.addCommentHeight;
                            })
                        }},
                    {el: items[1], stretch: true},
                    {el: items[2], stretch: true}
                ]
            });
            me.layout.on('layout:resizedrag', function() {
                me.updateScrolls();
                me.textBoxAutoSizeLocked = true;
            }, this);

            $(window).on('resize', function() {
                if (parent.css('display') !== 'none') {

                   var height = $('#comments-box', me.el).height();
                   var addcmt = $('.new-comment-ct', me.el);
                   var tocmt = $('.add-link-ct', me.el);

                   if (addcmt.css('display') !== 'none') {
                        me.layout.setResizeValue(0,
                            Math.max(-me.newCommentHeight,
                                Math.min(height - (addcmt.height() + 4), height - me.newCommentHeight)));
                    }
                    else {
                        me.layout.setResizeValue(0,
                            Math.max(-me.addCommentHeight,
                                Math.min(height - (tocmt.height()), height - me.addCommentHeight)));
                    }

                    me.updateScrolls();
                }
            });

            this.autoHeightTextBox();
        },

        updateLayout: function () {
            var container = $('#comments-box', this.el), add = $('.new-comment-ct', this.el);
            if (add.css('display') !== 'none') {
                this.layout.setResizeValue(0, container.height() - this.newCommentHeight);
            } else {
                this.layout.setResizeValue(0, container.height() - this.addCommentHeight);
            }
        },

        autoHeightTextBox: function () {
            var me = this, domTextBox = null, lineHeight = 0, minHeight = 44;
            var textBox = $('#comment-msg-new', this.el);

            function updateTextBoxHeight() {

                var textBox, controlHeight, contentHeight, height, oldHeight,
                    textBoxMinHeightIndent = 44 + 4;    // 4px - autosize line height + big around border

                textBox = $('#comment-msg-new', me.el);
                height = $('#comments-box', me.el).height();

                if (0 == textBox.val().length) {
                    me.layout.setResizeValue(0, Math.max(-me.newCommentHeight, height - me.newCommentHeight));
                    me.textBoxAutoSizeLocked = undefined;
                    return;
                }

                if (!_.isUndefined(me.textBoxAutoSizeLocked))
                    return;

                controlHeight = textBox.height();
                contentHeight = textBox.get(0).scrollHeight;

                // calculate text content height

                textBox.css({height: minHeight + 'px'});

                controlHeight = textBox.height();
                contentHeight = Math.max(textBox.get(0).scrollHeight + lineHeight, textBoxMinHeightIndent);

                textBox.css({height: '100%'});

                height = $('#comments-box', me.el).height();

                me.layout.setResizeValue(0,
                    Math.max(-me.newCommentHeight,
                        Math.min(height - contentHeight - textBoxMinHeightIndent, height - me.newCommentHeight)));
            }

            lineHeight = parseInt(textBox.css('lineHeight'), 10) * 0.25;
            updateTextBoxHeight();
            textBox.bind('input propertychange', updateTextBoxHeight);

            this.textBox = textBox;
        },

        getFixedQuote: function (quote) {
            return Common.Utils.String.ellipsis(Common.Utils.String.htmlEncode(quote), 120, true);
        },
        getUserName: function (username) {
            return Common.Utils.String.ellipsis(Common.Utils.String.htmlEncode(username), 22, true);
        },

        pickLink: function (message) {
            var arr = [], offset, len;
            message = Common.Utils.String.htmlEncode(message);

            message.replace(Common.Utils.ipStrongRe, function(subStr) {
                offset = arguments[arguments.length-2];
                arr.push({start: offset, end: subStr.length+offset, str: '<a href="' + subStr + '" target="_blank" data-can-copy="true">' + subStr + '</a>'});
                return '';
            });

            if (message.length<1000 || message.search(/\S{255,}/)<0)
                message.replace(Common.Utils.hostnameStrongRe, function(subStr) {
                    var ref = (! /(((^https?)|(^ftp)):\/\/)/i.test(subStr) ) ? ('http://' + subStr) : subStr;
                    offset = arguments[arguments.length-2];
                    len = subStr.length;
                    var elem = _.find(arr, function(item){
                        return ( (offset>=item.start) && (offset<item.end) ||
                            (offset<=item.start) && (offset+len>item.start));
                    });
                    if (!elem)
                        arr.push({start: offset, end: len+offset, str: '<a href="' + ref + '" target="_blank" data-can-copy="true">' + subStr + '</a>'});
                    return '';
                });

            message.replace(Common.Utils.emailStrongRe, function(subStr) {
                var ref = (! /((^mailto:)\/\/)/i.test(subStr) ) ? ('mailto:' + subStr) : subStr;
                offset = arguments[arguments.length-2];
                len = subStr.length;
                var elem = _.find(arr, function(item){
                    return ( (offset>=item.start) && (offset<item.end) ||
                             (offset<=item.start) && (offset+len>item.start));
                });
                if (!elem)
                    arr.push({start: offset, end: len+offset, str: '<a href="' + ref + '">' + subStr + '</a>'});
                return '';
            });

            arr = _.sortBy(arr, function(item){ return item.start; });

            var str_res = (arr.length>0) ? ( message.substring(0, arr[0].start) + arr[0].str) : message;
            for (var i=1; i<arr.length; i++) {
                str_res += (message.substring(arr[i-1].end, arr[i].start) + arr[i].str);
            }
            if (arr.length>0) {
                str_res += message.substring(arr[i-1].end, message.length);
            }

            return str_res;
        },

        textComments            : 'Comments',
        textAnonym              : 'Guest',
        textAddCommentToDoc     : 'Add Comment to Document',
        textAddComment          : 'Add Comment',
        textCancel              : 'Cancel',
        textAddReply            : 'Add Reply',
        textReply               : 'Reply',
        textClose               : 'Close',
        textResolved            : 'Resolved',
        textResolve             : 'Resolve',
        textEnterCommentHint    : 'Enter your comment here',
        textEdit                : 'Edit',
        textAdd                 : "Add",
        textOpenAgain           : "Open Again"
    }, Common.Views.Comments || {}))
});