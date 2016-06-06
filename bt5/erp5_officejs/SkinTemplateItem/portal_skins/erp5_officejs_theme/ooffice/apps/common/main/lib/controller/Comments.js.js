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
            <value> <string>ts44308801.63</string> </value>
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
Common.Controllers = Common.Controllers || {};\r\n
define(["core", "common/main/lib/model/Comment", "common/main/lib/collection/Comments", "common/main/lib/view/Comments"], function () {\r\n
    function buildCommentData() {\r\n
        if (typeof asc_CCommentDataWord !== "undefined") {\r\n
            return new asc_CCommentDataWord(null);\r\n
        }\r\n
        return new asc_CCommentData(null);\r\n
    }\r\n
    Common.Controllers.Comments = Backbone.Controller.extend(_.extend({\r\n
        models: [],\r\n
        collections: ["Common.Collections.Comments"],\r\n
        views: ["Common.Views.Comments", "Common.Views.CommentsPopover"],\r\n
        sdkViewName: "#id_main",\r\n
        subEditStrings: {},\r\n
        filter: undefined,\r\n
        hintmode: false,\r\n
        isSelectedComment: false,\r\n
        uids: [],\r\n
        oldUids: [],\r\n
        isDummyComment: false,\r\n
        initialize: function () {\r\n
            this.addListeners({\r\n
                "Common.Views.Comments": {\r\n
                    "comment:add": _.bind(this.onCreateComment, this),\r\n
                    "comment:change": _.bind(this.onChangeComment, this),\r\n
                    "comment:remove": _.bind(this.onRemoveComment, this),\r\n
                    "comment:resolve": _.bind(this.onResolveComment, this),\r\n
                    "comment:show": _.bind(this.onShowComment, this),\r\n
                    "comment:addReply": _.bind(this.onAddReplyComment, this),\r\n
                    "comment:changeReply": _.bind(this.onChangeReplyComment, this),\r\n
                    "comment:removeReply": _.bind(this.onRemoveReplyComment, this),\r\n
                    "comment:editReply": _.bind(this.onShowEditReplyComment, this),\r\n
                    "comment:closeEditing": _.bind(this.closeEditing, this),\r\n
                    "comment:disableHint": _.bind(this.disableHint, this),\r\n
                    "comment:addDummyComment": _.bind(this.onAddDummyComment, this)\r\n
                }\r\n
            });\r\n
            Common.NotificationCenter.on("comments:updatefilter", _.bind(this.onUpdateFilter, this));\r\n
        },\r\n
        onLaunch: function () {\r\n
            this.collection = this.getApplication().getCollection("Common.Collections.Comments");\r\n
            if (this.collection) {\r\n
                this.collection.comparator = function (collection) {\r\n
                    return -collection.get("time");\r\n
                };\r\n
            }\r\n
            this.popoverComments = new Common.Collections.Comments();\r\n
            if (this.popoverComments) {\r\n
                this.popoverComments.comparator = function (collection) {\r\n
                    return -collection.get("time");\r\n
                };\r\n
            }\r\n
            this.view = this.createView("Common.Views.Comments", {\r\n
                store: this.collection,\r\n
                popoverComments: this.popoverComments\r\n
            });\r\n
            this.view.render();\r\n
            this.bindViewEvents(this.view, this.events);\r\n
        },\r\n
        setConfig: function (data, api) {\r\n
            this.setApi(api);\r\n
            if (data) {\r\n
                this.currentUserId = data.config.user.id;\r\n
                this.currentUserName = data.config.user.name;\r\n
                this.sdkViewName = data["sdkviewname"] || this.sdkViewName;\r\n
                this.hintmode = data["hintmode"] || false;\r\n
            }\r\n
        },\r\n
        setApi: function (api) {\r\n
            if (api) {\r\n
                this.api = api;\r\n
                this.api.asc_registerCallback("asc_onAddComment", _.bind(this.onApiAddComment, this));\r\n
                this.api.asc_registerCallback("asc_onAddComments", _.bind(this.onApiAddComments, this));\r\n
                this.api.asc_registerCallback("asc_onRemoveComment", _.bind(this.onApiRemoveComment, this));\r\n
                this.api.asc_registerCallback("asc_onChangeComments", _.bind(this.onChangeComments, this));\r\n
                this.api.asc_registerCallback("asc_onRemoveComments", _.bind(this.onRemoveComments, this));\r\n
                this.api.asc_registerCallback("asc_onChangeCommentData", _.bind(this.onApiChangeCommentData, this));\r\n
                this.api.asc_registerCallback("asc_onLockComment", _.bind(this.onApiLockComment, this));\r\n
                this.api.asc_registerCallback("asc_onUnLockComment", _.bind(this.onApiUnLockComment, this));\r\n
                this.api.asc_registerCallback("asc_onShowComment", _.bind(this.onApiShowComment, this));\r\n
                this.api.asc_registerCallback("asc_onHideComment", _.bind(this.onApiHideComment, this));\r\n
                this.api.asc_registerCallback("asc_onUpdateCommentPosition", _.bind(this.onApiUpdateCommentPosition, this));\r\n
                this.api.asc_registerCallback("asc_onDocumentPlaceChanged", _.bind(this.onDocumentPlaceChanged, this));\r\n
            }\r\n
        },\r\n
        setMode: function (mode) {\r\n
            this.mode = mode;\r\n
            return this;\r\n
        },\r\n
        onCreateComment: function (panel, commentVal, editMode, hidereply, documentFlag) {\r\n
            if (this.api && commentVal && commentVal.length > 0) {\r\n
                var comment = buildCommentData();\r\n
                if (comment) {\r\n
                    this.showPopover = true;\r\n
                    this.editPopover = editMode ? true : false;\r\n
                    this.hidereply = hidereply;\r\n
                    this.isSelectedComment = false;\r\n
                    this.uids = [];\r\n
                    comment.asc_putText(commentVal);\r\n
                    comment.asc_putTime(this.utcDateToString(new Date()));\r\n
                    comment.asc_putUserId(this.currentUserId);\r\n
                    comment.asc_putUserName(this.currentUserName);\r\n
                    comment.asc_putSolved(false);\r\n
                    if (!_.isUndefined(comment.asc_putDocumentFlag)) {\r\n
                        comment.asc_putDocumentFlag(documentFlag);\r\n
                    }\r\n
                    this.api.asc_addComment(comment);\r\n
                    this.view.showEditContainer(false);\r\n
                }\r\n
            }\r\n
            this.view.txtComment.focus();\r\n
        },\r\n
        onRemoveComment: function (id) {\r\n
            if (this.api && id) {\r\n
                this.api.asc_removeComment(id);\r\n
            }\r\n
        },\r\n
        onResolveComment: function (uid, id) {\r\n
            var t = this,\r\n
            reply = null,\r\n
            addReply = null,\r\n
            ascComment = buildCommentData(),\r\n
            comment = t.findComment(uid, id);\r\n
            if (_.isUndefined(uid)) {\r\n
                uid = comment.get("uid");\r\n
            }\r\n
            if (ascComment && comment) {\r\n
                ascComment.asc_putText(comment.get("comment"));\r\n
                ascComment.asc_putQuoteText(comment.get("quote"));\r\n
                ascComment.asc_putTime(t.utcDateToString(new Date(comment.get("time"))));\r\n
                ascComment.asc_putUserId(t.currentUserId);\r\n
                ascComment.asc_putUserName(t.currentUserName);\r\n
                ascComment.asc_putSolved(!comment.get("resolved"));\r\n
                if (!_.isUndefined(ascComment.asc_putDocumentFlag)) {\r\n
                    ascComment.asc_putDocumentFlag(comment.get("unattached"));\r\n
                }\r\n
                reply = comment.get("replys");\r\n
                if (reply && reply.length) {\r\n
                    reply.forEach(function (reply) {\r\n
                        addReply = buildCommentData();\r\n
                        if (addReply) {\r\n
                            addReply.asc_putText(reply.get("reply"));\r\n
                            addReply.asc_putTime(t.utcDateToString(new Date(reply.get("time"))));\r\n
                            addReply.asc_putUserId(reply.get("userid"));\r\n
                            addReply.asc_putUserName(reply.get("username"));\r\n
                            ascComment.asc_addReply(addReply);\r\n
                        }\r\n
                    });\r\n
                }\r\n
                t.api.asc_changeComment(uid, ascComment);\r\n
                return true;\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onShowComment: function (id, selected) {\r\n
            var comment = this.findComment(id, undefined);\r\n
            if (comment) {\r\n
                if (null !== comment.get("quote")) {\r\n
                    if (this.api) {\r\n
                        if (this.hintmode) {\r\n
                            this.animate = true;\r\n
                            if (comment.get("unattached")) {\r\n
                                if (this.getPopover()) {\r\n
                                    this.getPopover().hide();\r\n
                                    return;\r\n
                                }\r\n
                            }\r\n
                        } else {\r\n
                            var model = this.popoverComments.findWhere({\r\n
                                uid: id\r\n
                            });\r\n
                            if (model) {\r\n
                                return;\r\n
                            }\r\n
                        }\r\n
                        if (!_.isUndefined(selected) && this.hintmode) {\r\n
                            this.isSelectedComment = selected;\r\n
                        }\r\n
                        this.api.asc_selectComment(id);\r\n
                        this.api.asc_showComment(id, false);\r\n
                    }\r\n
                } else {\r\n
                    if (this.hintmode) {\r\n
                        this.api.asc_selectComment(id);\r\n
                    }\r\n
                    if (this.getPopover()) {\r\n
                        this.getPopover().hide();\r\n
                    }\r\n
                    this.isSelectedComment = false;\r\n
                    this.uids = [];\r\n
                }\r\n
            }\r\n
        },\r\n
        onChangeComment: function (id, commentVal) {\r\n
            if (commentVal && commentVal.length > 0) {\r\n
                var t = this,\r\n
                comment2 = null,\r\n
                reply = null,\r\n
                addReply = null,\r\n
                ascComment = buildCommentData(),\r\n
                comment = t.findComment(id);\r\n
                if (comment && ascComment) {\r\n
                    ascComment.asc_putText(commentVal);\r\n
                    ascComment.asc_putQuoteText(comment.get("quote"));\r\n
                    ascComment.asc_putTime(t.utcDateToString(new Date(comment.get("time"))));\r\n
                    ascComment.asc_putUserId(t.currentUserId);\r\n
                    ascComment.asc_putUserName(t.currentUserName);\r\n
                    ascComment.asc_putSolved(comment.get("resolved"));\r\n
                    if (!_.isUndefined(ascComment.asc_putDocumentFlag)) {\r\n
                        ascComment.asc_putDocumentFlag(comment.get("unattached"));\r\n
                    }\r\n
                    comment.set("editTextInPopover", false);\r\n
                    comment2 = t.findPopupComment(id);\r\n
                    if (comment2) {\r\n
                        comment2.set("editTextInPopover", false);\r\n
                    }\r\n
                    if (t.subEditStrings[id]) {\r\n
                        delete t.subEditStrings[id];\r\n
                    }\r\n
                    if (t.subEditStrings[id + "-R"]) {\r\n
                        delete t.subEditStrings[id + "-R"];\r\n
                    }\r\n
                    reply = comment.get("replys");\r\n
                    if (reply && reply.length) {\r\n
                        reply.forEach(function (reply) {\r\n
                            addReply = buildCommentData();\r\n
                            if (addReply) {\r\n
                                addReply.asc_putText(reply.get("reply"));\r\n
                                addReply.asc_putTime(t.utcDateToString(new Date(reply.get("time"))));\r\n
                                addReply.asc_putUserId(reply.get("userid"));\r\n
                                addReply.asc_putUserName(reply.get("username"));\r\n
                                ascComment.asc_addReply(addReply);\r\n
                            }\r\n
                        });\r\n
                    }\r\n
                    t.api.asc_changeComment(id, ascComment);\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onChangeReplyComment: function (id, replyId, replyVal) {\r\n
            if (replyVal && replyVal.length > 0) {\r\n
                var me = this,\r\n
                reply = null,\r\n
                addReply = null,\r\n
                ascComment = buildCommentData(),\r\n
                comment = me.findComment(id);\r\n
                if (ascComment && comment) {\r\n
                    ascComment.asc_putText(comment.get("comment"));\r\n
                    ascComment.asc_putQuoteText(comment.get("quote"));\r\n
                    ascComment.asc_putTime(me.utcDateToString(new Date(comment.get("time"))));\r\n
                    ascComment.asc_putUserId(comment.get("userid"));\r\n
                    ascComment.asc_putUserName(comment.get("username"));\r\n
                    ascComment.asc_putSolved(comment.get("resolved"));\r\n
                    if (!_.isUndefined(ascComment.asc_putDocumentFlag)) {\r\n
                        ascComment.asc_putDocumentFlag(comment.get("unattached"));\r\n
                    }\r\n
                    reply = comment.get("replys");\r\n
                    if (reply && reply.length) {\r\n
                        reply.forEach(function (reply) {\r\n
                            addReply = buildCommentData();\r\n
                            if (addReply) {\r\n
                                if (reply.get("id") === replyId && !_.isUndefined(replyVal)) {\r\n
                                    addReply.asc_putText(replyVal);\r\n
                                    addReply.asc_putUserId(me.currentUserId);\r\n
                                    addReply.asc_putUserName(me.currentUserName);\r\n
                                } else {\r\n
                                    addReply.asc_putText(reply.get("reply"));\r\n
                                    addReply.asc_putUserId(reply.get("userid"));\r\n
                                    addReply.asc_putUserName(reply.get("username"));\r\n
                                }\r\n
                                addReply.asc_putTime(me.utcDateToString(new Date(reply.get("time"))));\r\n
                                ascComment.asc_addReply(addReply);\r\n
                            }\r\n
                        });\r\n
                    }\r\n
                    me.api.asc_changeComment(id, ascComment);\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onAddReplyComment: function (id, replyVal) {\r\n
            if (replyVal.length > 0) {\r\n
                var me = this,\r\n
                uid = null,\r\n
                reply = null,\r\n
                addReply = null,\r\n
                ascComment = buildCommentData(),\r\n
                comment = me.findComment(id);\r\n
                if (ascComment && comment) {\r\n
                    uid = comment.get("uid");\r\n
                    if (uid) {\r\n
                        if (me.subEditStrings[uid]) {\r\n
                            delete me.subEditStrings[uid];\r\n
                        }\r\n
                        if (me.subEditStrings[uid + "-R"]) {\r\n
                            delete me.subEditStrings[uid + "-R"];\r\n
                        }\r\n
                        comment.set("showReplyInPopover", false);\r\n
                    }\r\n
                    ascComment.asc_putText(comment.get("comment"));\r\n
                    ascComment.asc_putQuoteText(comment.get("quote"));\r\n
                    ascComment.asc_putTime(me.utcDateToString(new Date(comment.get("time"))));\r\n
                    ascComment.asc_putUserId(comment.get("userid"));\r\n
                    ascComment.asc_putUserName(comment.get("username"));\r\n
                    ascComment.asc_putSolved(comment.get("resolved"));\r\n
                    if (!_.isUndefined(ascComment.asc_putDocumentFlag)) {\r\n
                        ascComment.asc_putDocumentFlag(comment.get("unattached"));\r\n
                    }\r\n
                    reply = comment.get("replys");\r\n
                    if (reply && reply.length) {\r\n
                        reply.forEach(function (reply) {\r\n
                            addReply = buildCommentData();\r\n
                            if (addReply) {\r\n
                                addReply.asc_putText(reply.get("reply"));\r\n
                                addReply.asc_putTime(me.utcDateToString(new Date(reply.get("time"))));\r\n
                                addReply.asc_putUserId(reply.get("userid"));\r\n
                                addReply.asc_putUserName(reply.get("username"));\r\n
                                ascComment.asc_addReply(addReply);\r\n
                            }\r\n
                        });\r\n
                    }\r\n
                    addReply = buildCommentData();\r\n
                    if (addReply) {\r\n
                        addReply.asc_putText(replyVal);\r\n
                        addReply.asc_putTime(me.utcDateToString(new Date()));\r\n
                        addReply.asc_putUserId(me.currentUserId);\r\n
                        addReply.asc_putUserName(me.currentUserName);\r\n
                        ascComment.asc_addReply(addReply);\r\n
                        me.api.asc_changeComment(id, ascComment);\r\n
                        return true;\r\n
                    }\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onRemoveReplyComment: function (id, replyId) {\r\n
            if (!_.isUndefined(id) && !_.isUndefined(replyId)) {\r\n
                var me = this,\r\n
                replies = null,\r\n
                addReply = null,\r\n
                ascComment = buildCommentData(),\r\n
                comment = me.findComment(id);\r\n
                if (ascComment && comment) {\r\n
                    ascComment.asc_putText(comment.get("comment"));\r\n
                    ascComment.asc_putQuoteText(comment.get("quote"));\r\n
                    ascComment.asc_putTime(me.utcDateToString(new Date(comment.get("time"))));\r\n
                    ascComment.asc_putUserId(comment.get("userid"));\r\n
                    ascComment.asc_putUserName(comment.get("username"));\r\n
                    ascComment.asc_putSolved(comment.get("resolved"));\r\n
                    if (!_.isUndefined(ascComment.asc_putDocumentFlag)) {\r\n
                        ascComment.asc_putDocumentFlag(comment.get("unattached"));\r\n
                    }\r\n
                    replies = comment.get("replys");\r\n
                    if (replies && replies.length) {\r\n
                        replies.forEach(function (reply) {\r\n
                            if (reply.get("id") !== replyId) {\r\n
                                addReply = buildCommentData();\r\n
                                if (addReply) {\r\n
                                    addReply.asc_putText(reply.get("reply"));\r\n
                                    addReply.asc_putTime(me.utcDateToString(new Date(reply.get("time"))));\r\n
                                    addReply.asc_putUserId(reply.get("userid"));\r\n
                                    addReply.asc_putUserName(reply.get("username"));\r\n
                                    ascComment.asc_addReply(addReply);\r\n
                                }\r\n
                            }\r\n
                        });\r\n
                    }\r\n
                    me.api.asc_changeComment(id, ascComment);\r\n
                    return true;\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onShowEditReplyComment: function (id, replyId, inpopover) {\r\n
            var i, model, repliesSrc, repliesCopy;\r\n
            if (!_.isUndefined(id) && !_.isUndefined(replyId)) {\r\n
                if (inpopover) {\r\n
                    model = this.popoverComments.findWhere({\r\n
                        uid: id\r\n
                    });\r\n
                    if (model) {\r\n
                        repliesSrc = model.get("replys");\r\n
                        repliesCopy = _.clone(model.get("replys"));\r\n
                        if (repliesCopy) {\r\n
                            for (i = 0; i < repliesCopy.length; ++i) {\r\n
                                if (replyId === repliesCopy[i].get("id")) {\r\n
                                    repliesCopy[i].set("editTextInPopover", true);\r\n
                                    repliesSrc.length = 0;\r\n
                                    model.set("replys", repliesCopy);\r\n
                                    return true;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                } else {\r\n
                    model = this.collection.findWhere({\r\n
                        uid: id\r\n
                    });\r\n
                    if (model) {\r\n
                        repliesSrc = model.get("replys");\r\n
                        repliesCopy = _.clone(model.get("replys"));\r\n
                        if (repliesCopy) {\r\n
                            for (i = 0; i < repliesCopy.length; ++i) {\r\n
                                if (replyId === repliesCopy[i].get("id")) {\r\n
                                    repliesCopy[i].set("editText", true);\r\n
                                    repliesSrc.length = 0;\r\n
                                    model.set("replys", repliesCopy);\r\n
                                    return true;\r\n
                                }\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
            return false;\r\n
        },\r\n
        onUpdateFilter: function (filter, applyOnly) {\r\n
            if (filter) {\r\n
                this.filter = {\r\n
                    property: filter.property,\r\n
                    value: filter.value\r\n
                };\r\n
                if (!applyOnly) {\r\n
                    if (this.getPopover()) {\r\n
                        this.getPopover().hide();\r\n
                    }\r\n
                }\r\n
                var t = this,\r\n
                endComment = null;\r\n
                this.collection.each(function (model) {\r\n
                    var prop = model.get(t.filter.property);\r\n
                    if (prop) {\r\n
                        model.set("hide", (null === prop.match(t.filter.value)));\r\n
                    }\r\n
                    if (model.get("last")) {\r\n
                        model.set("last", false);\r\n
                    }\r\n
                    if (!model.get("hide")) {\r\n
                        endComment = model;\r\n
                    }\r\n
                });\r\n
                if (endComment) {\r\n
                    endComment.set("last", true);\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiAddComment: function (id, data) {\r\n
            var comment = this.readSDKComment(id, data);\r\n
            if (comment) {\r\n
                this.collection.push(comment);\r\n
                this.updateComments(true);\r\n
                if (this.showPopover) {\r\n
                    if (null !== data.asc_getQuoteText()) {\r\n
                        this.api.asc_selectComment(id);\r\n
                        this.api.asc_showComment(id, true);\r\n
                    }\r\n
                    this.showPopover = undefined;\r\n
                    this.editPopover = false;\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiAddComments: function (data) {\r\n
            for (var i = 0; i < data.length; ++i) {\r\n
                var comment = this.readSDKComment(data[i].Id, data[i].Comment);\r\n
                this.collection.push(comment);\r\n
            }\r\n
            this.updateComments(true);\r\n
        },\r\n
        onApiRemoveComment: function (id, silentUpdate) {\r\n
            if (this.collection.length) {\r\n
                var model = this.collection.findWhere({\r\n
                    uid: id\r\n
                });\r\n
                if (model) {\r\n
                    this.collection.remove(model);\r\n
                    if (!silentUpdate) {\r\n
                        this.updateComments(true);\r\n
                    }\r\n
                }\r\n
                if (this.popoverComments.length) {\r\n
                    model = this.popoverComments.findWhere({\r\n
                        uid: id\r\n
                    });\r\n
                    if (model) {\r\n
                        this.popoverComments.remove(model);\r\n
                        if (0 === this.popoverComments.length) {\r\n
                            if (this.getPopover()) {\r\n
                                this.getPopover().hide();\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onChangeComments: function (data) {\r\n
            for (var i = 0; i < data.length; ++i) {\r\n
                this.onApiChangeCommentData(data[i].Comment.Id, data[i].Comment, true);\r\n
            }\r\n
            this.updateComments(true);\r\n
        },\r\n
        onRemoveComments: function (data) {\r\n
            for (var i = 0; i < data.length; ++i) {\r\n
                this.onApiRemoveComment(data[i], true);\r\n
            }\r\n
            this.updateComments(true);\r\n
        },\r\n
        onApiChangeCommentData: function (id, data, silentUpdate) {\r\n
            var t = this,\r\n
            i = 0,\r\n
            date = null,\r\n
            replies = null,\r\n
            repliesCount = 0,\r\n
            dateReply = null,\r\n
            comment = this.findComment(id);\r\n
            if (comment) {\r\n
                t = this;\r\n
                date = (data.asc_getTime() == "") ? new Date() : new Date(this.stringUtcToLocalDate(data.asc_getTime()));\r\n
                comment.set("comment", data.asc_getText());\r\n
                comment.set("userid", data.asc_getUserId());\r\n
                comment.set("username", data.asc_getUserName());\r\n
                comment.set("resolved", data.asc_getSolved());\r\n
                comment.set("quote", data.asc_getQuoteText());\r\n
                comment.set("time", date.getTime());\r\n
                comment.set("date", t.dateToLocaleTimeString(date));\r\n
                replies = _.clone(comment.get("replys"));\r\n
                replies.length = 0;\r\n
                repliesCount = data.asc_getRepliesCount();\r\n
                for (i = 0; i < repliesCount; ++i) {\r\n
                    dateReply = (data.asc_getReply(i).asc_getTime() == "") ? new Date() : new Date(this.stringUtcToLocalDate(data.asc_getReply(i).asc_getTime()));\r\n
                    replies.push(new Common.Models.Reply({\r\n
                        id: Common.UI.getId(),\r\n
                        userid: data.asc_getReply(i).asc_getUserId(),\r\n
                        username: data.asc_getReply(i).asc_getUserName(),\r\n
                        date: t.dateToLocaleTimeString(dateReply),\r\n
                        reply: data.asc_getReply(i).asc_getText(),\r\n
                        time: dateReply.getTime(),\r\n
                        editText: false,\r\n
                        editTextInPopover: false,\r\n
                        showReplyInPopover: false,\r\n
                        scope: t.view\r\n
                    }));\r\n
                }\r\n
                replies.sort(function (a, b) {\r\n
                    return a.get("time") - b.get("time");\r\n
                });\r\n
                comment.set("replys", replies);\r\n
                if (!silentUpdate) {\r\n
                    this.updateComments(false, true);\r\n
                    if (this.getPopover() && this.getPopover().isVisible()) {\r\n
                        this.api.asc_showComment(id, true);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiLockComment: function (id, userId) {\r\n
            var cur = this.findComment(id),\r\n
            usersStore = null,\r\n
            user = null;\r\n
            if (cur) {\r\n
                usersStore = this.getApplication().getCollection("Common.Collections.Users");\r\n
                if (usersStore) {\r\n
                    user = usersStore.findWhere({\r\n
                        id: userId\r\n
                    });\r\n
                    if (user) {\r\n
                        cur.set("lock", true);\r\n
                        cur.set("lockuserid", this.view.getUserName(user.get("username")));\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onApiUnLockComment: function (id) {\r\n
            var cur = this.findComment(id);\r\n
            if (cur) {\r\n
                cur.set("lock", false);\r\n
            }\r\n
        },\r\n
        onApiShowComment: function (uids, posX, posY, leftX, opts, hint) {\r\n
            if (hint && this.isSelectedComment && (0 === _.difference(this.uids, uids).length)) {\r\n
                return;\r\n
            }\r\n
            if (this.mode && !this.mode.canComments) {\r\n
                hint = true;\r\n
            }\r\n
            if (this.getPopover()) {\r\n
                this.clearDummyComment();\r\n
                if (this.isSelectedComment && (0 === _.difference(this.uids, uids).length)) {\r\n
                    if (this.api) {\r\n
                        this.getPopover().commentsView.setFocusToTextBox(true);\r\n
                        this.api.asc_enableKeyEvents(true);\r\n
                    }\r\n
                    return;\r\n
                }\r\n
                var i = 0,\r\n
                saveTxtId = "",\r\n
                saveTxtReplyId = "",\r\n
                comment = null,\r\n
                text = "",\r\n
                animate = true;\r\n
                this.popoverComments.reset();\r\n
                for (i = 0; i < uids.length; ++i) {\r\n
                    saveTxtId = uids[i];\r\n
                    saveTxtReplyId = uids[i] + "-R";\r\n
                    comment = this.findComment(saveTxtId);\r\n
                    if (this.subEditStrings[saveTxtId]) {\r\n
                        comment.set("editTextInPopover", true);\r\n
                        text = this.subEditStrings[saveTxtId];\r\n
                    } else {\r\n
                        if (this.subEditStrings[saveTxtReplyId]) {\r\n
                            comment.set("showReplyInPopover", true);\r\n
                            text = this.subEditStrings[saveTxtReplyId];\r\n
                        }\r\n
                    }\r\n
                    comment.set("hint", !_.isUndefined(hint) ? hint : false);\r\n
                    if (!hint && this.hintmode) {\r\n
                        if (0 === _.difference(this.uids, uids).length && (this.uids.length === 0)) {\r\n
                            animate = false;\r\n
                        }\r\n
                        if (this.oldUids.length && (0 === _.difference(this.oldUids, uids).length)) {\r\n
                            animate = false;\r\n
                            this.oldUids = [];\r\n
                        }\r\n
                    }\r\n
                    if (this.animate) {\r\n
                        animate = this.animate;\r\n
                        this.animate = false;\r\n
                    }\r\n
                    this.isSelectedComment = !hint;\r\n
                    this.uids = _.clone(uids);\r\n
                    this.popoverComments.push(comment);\r\n
                }\r\n
                if (this.getPopover().isVisible()) {\r\n
                    this.getPopover().hide();\r\n
                }\r\n
                this.getPopover().setLeftTop(posX, posY, leftX);\r\n
                this.getPopover().show(animate, false, true, text);\r\n
            }\r\n
        },\r\n
        onApiHideComment: function (hint) {\r\n
            var t = this;\r\n
            if (this.getPopover()) {\r\n
                if (this.isSelectedComment && hint) {\r\n
                    return;\r\n
                }\r\n
                this.popoverComments.each(function (model) {\r\n
                    if (model.get("editTextInPopover")) {\r\n
                        t.subEditStrings[model.get("uid")] = t.getPopover().getEditText();\r\n
                    }\r\n
                    if (model.get("showReplyInPopover")) {\r\n
                        t.subEditStrings[model.get("uid") + "-R"] = t.getPopover().getEditText();\r\n
                    }\r\n
                });\r\n
                this.getPopover().saveText(true);\r\n
                this.getPopover().hide();\r\n
                this.collection.clearEditing();\r\n
                this.popoverComments.clearEditing();\r\n
                this.oldUids = _.clone(this.uids);\r\n
                this.isSelectedComment = false;\r\n
                this.uids = [];\r\n
                this.popoverComments.reset();\r\n
            }\r\n
        },\r\n
        onApiUpdateCommentPosition: function (uids, posX, posY, leftX) {\r\n
            var i, useAnimation = false,\r\n
            comment = null,\r\n
            text = undefined,\r\n
            saveTxtId = "",\r\n
            saveTxtReplyId = "";\r\n
            if (this.getPopover()) {\r\n
                this.getPopover().saveText();\r\n
                if (posY < 0 || this.getPopover().sdkBounds.height < posY || (!_.isUndefined(leftX) && this.getPopover().sdkBounds.width < leftX)) {\r\n
                    this.getPopover().hide();\r\n
                } else {\r\n
                    if (0 === this.popoverComments.length) {\r\n
                        this.popoverComments.reset();\r\n
                        for (i = 0; i < uids.length; ++i) {\r\n
                            saveTxtId = uids[i];\r\n
                            saveTxtReplyId = uids[i] + "-R";\r\n
                            comment = this.findComment(saveTxtId);\r\n
                            if (this.subEditStrings[saveTxtId]) {\r\n
                                comment.set("editTextInPopover", true);\r\n
                                text = this.subEditStrings[saveTxtId];\r\n
                            } else {\r\n
                                if (this.subEditStrings[saveTxtReplyId]) {\r\n
                                    comment.set("showReplyInPopover", true);\r\n
                                    text = this.subEditStrings[saveTxtReplyId];\r\n
                                }\r\n
                            }\r\n
                            this.popoverComments.push(comment);\r\n
                        }\r\n
                        useAnimation = true;\r\n
                        this.getPopover().show(useAnimation, undefined, undefined, text);\r\n
                    } else {\r\n
                        if (!this.getPopover().isVisible()) {\r\n
                            this.getPopover().show(false, undefined, undefined, text);\r\n
                        }\r\n
                    }\r\n
                    this.getPopover().setLeftTop(posX, posY, leftX);\r\n
                }\r\n
            }\r\n
        },\r\n
        onDocumentPlaceChanged: function () {\r\n
            if (this.isDummyComment && this.getPopover()) {\r\n
                if (this.getPopover().isVisible()) {\r\n
                    var anchor = this.api.asc_getAnchorPosition();\r\n
                    if (anchor) {\r\n
                        this.getPopover().setLeftTop(anchor.asc_getX() + anchor.asc_getWidth(), anchor.asc_getY(), this.hintmode ? anchor.asc_getX() : undefined);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        updateComments: function (needRender, disableSort) {\r\n
            var i, end = true;\r\n
            if (_.isUndefined(disableSort)) {\r\n
                this.collection.sort();\r\n
            }\r\n
            if (needRender) {\r\n
                for (i = this.collection.length - 1; i >= 0; --i) {\r\n
                    if (end) {\r\n
                        this.collection.at(i).set("last", true, {\r\n
                            silent: true\r\n
                        });\r\n
                    } else {\r\n
                        if (this.collection.at(i).get("last")) {\r\n
                            this.collection.at(i).set("last", false, {\r\n
                                silent: true\r\n
                            });\r\n
                        }\r\n
                    }\r\n
                    end = false;\r\n
                }\r\n
                this.onUpdateFilter(this.filter, true);\r\n
                this.view.render();\r\n
            }\r\n
            this.view.renderResolvedComboButtons();\r\n
            this.view.update();\r\n
        },\r\n
        findComment: function (uid, id) {\r\n
            if (_.isUndefined(uid)) {\r\n
                return this.collection.findWhere({\r\n
                    id: id\r\n
                });\r\n
            }\r\n
            return this.collection.findWhere({\r\n
                uid: uid\r\n
            });\r\n
        },\r\n
        findPopupComment: function (id) {\r\n
            return this.popoverComments.findWhere({\r\n
                id: id\r\n
            });\r\n
        },\r\n
        closeEditing: function (id) {\r\n
            var t = this;\r\n
            if (!_.isUndefined(id)) {\r\n
                var comment2 = this.findPopupComment(id);\r\n
                if (comment2) {\r\n
                    comment2.set("editTextInPopover", false);\r\n
                    comment2.set("showReplyInPopover", false);\r\n
                }\r\n
                if (this.subEditStrings[id]) {\r\n
                    delete this.subEditStrings[id];\r\n
                }\r\n
                if (this.subEditStrings[id + "-R"]) {\r\n
                    delete this.subEditStrings[id + "-R"];\r\n
                }\r\n
            }\r\n
            this.collection.clearEditing();\r\n
            this.collection.each(function (model) {\r\n
                var replies = _.clone(model.get("replys"));\r\n
                model.get("replys").length = 0;\r\n
                replies.forEach(function (reply) {\r\n
                    if (reply.get("editText")) {\r\n
                        reply.set("editText", false);\r\n
                    }\r\n
                    if (reply.get("editTextInPopover")) {\r\n
                        reply.set("editTextInPopover", false);\r\n
                    }\r\n
                });\r\n
                model.set("replys", replies);\r\n
            });\r\n
            this.view.showEditContainer(false);\r\n
            this.view.update();\r\n
        },\r\n
        disableHint: function (comment) {\r\n
            if (comment && this.mode.canComments) {\r\n
                comment.set("hint", false);\r\n
                this.isSelectedComment = true;\r\n
            }\r\n
        },\r\n
        blockPopover: function (flag) {\r\n
            this.isSelectedComment = flag;\r\n
            if (flag) {\r\n
                if (this.getPopover().isVisible()) {\r\n
                    this.getPopover().hide();\r\n
                }\r\n
            }\r\n
        },\r\n
        getPopover: function () {\r\n
            return this.view.getPopover(this.sdkViewName);\r\n
        },\r\n
        readSDKComment: function (id, data) {\r\n
            var date = (data.asc_getTime() == "") ? new Date() : new Date(this.stringUtcToLocalDate(data.asc_getTime()));\r\n
            var comment = new Common.Models.Comment({\r\n
                uid: id,\r\n
                userid: data.asc_getUserId(),\r\n
                username: data.asc_getUserName(),\r\n
                date: this.dateToLocaleTimeString(date),\r\n
                quote: data.asc_getQuoteText(),\r\n
                comment: data.asc_getText(),\r\n
                resolved: data.asc_getSolved(),\r\n
                unattached: !_.isUndefined(data.asc_getDocumentFlag) ? data.asc_getDocumentFlag() : false,\r\n
                id: Common.UI.getId(),\r\n
                time: date.getTime(),\r\n
                showReply: false,\r\n
                editText: false,\r\n
                last: undefined,\r\n
                editTextInPopover: (this.editPopover ? true : false),\r\n
                showReplyInPopover: false,\r\n
                hideAddReply: !_.isUndefined(this.hidereply) ? this.hidereply : (this.showPopover ? true : false),\r\n
                scope: this.view\r\n
            });\r\n
            if (comment) {\r\n
                var replies = this.readSDKReplies(data);\r\n
                if (replies.length) {\r\n
                    comment.set("replys", replies);\r\n
                }\r\n
            }\r\n
            return comment;\r\n
        },\r\n
        readSDKReplies: function (data) {\r\n
            var i = 0,\r\n
            replies = [],\r\n
            date = null;\r\n
            var repliesCount = data.asc_getRepliesCount();\r\n
            if (repliesCount) {\r\n
                for (i = 0; i < repliesCount; ++i) {\r\n
                    date = (data.asc_getReply(i).asc_getTime() == "") ? new Date() : new Date(this.stringUtcToLocalDate(data.asc_getReply(i).asc_getTime()));\r\n
                    replies.push(new Common.Models.Reply({\r\n
                        id: Common.UI.getId(),\r\n
                        userid: data.asc_getReply(i).asc_getUserId(),\r\n
                        username: data.asc_getReply(i).asc_getUserName(),\r\n
                        date: this.dateToLocaleTimeString(date),\r\n
                        reply: data.asc_getReply(i).asc_getText(),\r\n
                        time: date.getTime(),\r\n
                        editText: false,\r\n
                        editTextInPopover: false,\r\n
                        showReplyInPopover: false,\r\n
                        scope: this.view\r\n
                    }));\r\n
                }\r\n
                replies.sort(function (a, b) {\r\n
                    return a.get("time") - b.get("time");\r\n
                });\r\n
            }\r\n
            return replies;\r\n
        },\r\n
        addDummyComment: function () {\r\n
            if (this.api) {\r\n
                var me = this,\r\n
                anchor = null,\r\n
                date = new Date(),\r\n
                dialog = this.getPopover();\r\n
                if (dialog) {\r\n
                    if (this.popoverComments.length) {\r\n
                        _.delay(function () {\r\n
                            me.api.asc_enableKeyEvents(false);\r\n
                            dialog.commentsView.setFocusToTextBox();\r\n
                        },\r\n
                        200);\r\n
                        return;\r\n
                    }\r\n
                    var comment = new Common.Models.Comment({\r\n
                        id: -1,\r\n
                        time: date.getTime(),\r\n
                        date: this.dateToLocaleTimeString(date),\r\n
                        userid: this.currentUserId,\r\n
                        username: this.currentUserName,\r\n
                        editTextInPopover: true,\r\n
                        showReplyInPopover: false,\r\n
                        hideAddReply: true,\r\n
                        scope: this.view,\r\n
                        dummy: true\r\n
                    });\r\n
                    this.popoverComments.reset();\r\n
                    this.popoverComments.push(comment);\r\n
                    this.uids = [];\r\n
                    this.isSelectedComment = true;\r\n
                    this.isDummyComment = true;\r\n
                    if (!_.isUndefined(this.api.asc_SetDocumentPlaceChangedEnabled)) {\r\n
                        me.api.asc_SetDocumentPlaceChangedEnabled(true);\r\n
                    }\r\n
                    dialog.handlerHide = (function () {});\r\n
                    if (dialog.isVisible()) {\r\n
                        dialog.hide();\r\n
                    }\r\n
                    dialog.handlerHide = (function () {\r\n
                        me.clearDummyComment();\r\n
                    });\r\n
                    anchor = this.api.asc_getAnchorPosition();\r\n
                    if (anchor) {\r\n
                        dialog.setLeftTop(anchor.asc_getX() + anchor.asc_getWidth(), anchor.asc_getY(), this.hintmode ? anchor.asc_getX() : undefined);\r\n
                        dialog.show(true, false, true);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onAddDummyComment: function (commentVal) {\r\n
            if (this.api && commentVal && commentVal.length > 0) {\r\n
                var comment = buildCommentData();\r\n
                if (comment) {\r\n
                    this.showPopover = true;\r\n
                    this.editPopover = false;\r\n
                    this.hidereply = false;\r\n
                    this.isSelectedComment = false;\r\n
                    this.uids = [];\r\n
                    this.isDummyComment = false;\r\n
                    this.popoverComments.reset();\r\n
                    comment.asc_putText(commentVal);\r\n
                    comment.asc_putTime(this.utcDateToString(new Date()));\r\n
                    comment.asc_putUserId(this.currentUserId);\r\n
                    comment.asc_putUserName(this.currentUserName);\r\n
                    comment.asc_putSolved(false);\r\n
                    if (!_.isUndefined(comment.asc_putDocumentFlag)) {\r\n
                        comment.asc_putDocumentFlag(false);\r\n
                    }\r\n
                    this.api.asc_addComment(comment);\r\n
                    this.view.showEditContainer(false);\r\n
                    if (!_.isUndefined(this.api.asc_SetDocumentPlaceChangedEnabled)) {\r\n
                        this.api.asc_SetDocumentPlaceChangedEnabled(false);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        clearDummyComment: function () {\r\n
            if (this.isDummyComment) {\r\n
                this.isDummyComment = false;\r\n
                this.showPopover = true;\r\n
                this.editPopover = false;\r\n
                this.hidereply = false;\r\n
                this.isSelectedComment = false;\r\n
                this.uids = [];\r\n
                var dialog = this.getPopover();\r\n
                if (dialog) {\r\n
                    dialog.handlerHide = (function () {});\r\n
                    if (dialog.isVisible()) {\r\n
                        dialog.hide();\r\n
                    }\r\n
                }\r\n
                this.popoverComments.reset();\r\n
                if (!_.isUndefined(this.api.asc_SetDocumentPlaceChangedEnabled)) {\r\n
                    this.api.asc_SetDocumentPlaceChangedEnabled(false);\r\n
                }\r\n
            }\r\n
        },\r\n
        onEditComments: function (comments) {\r\n
            if (this.api) {\r\n
                var i = 0,\r\n
                t = this,\r\n
                comment = null;\r\n
                var anchor = this.api.asc_getAnchorPosition();\r\n
                if (anchor) {\r\n
                    this.isSelectedComment = true;\r\n
                    this.popoverComments.reset();\r\n
                    for (i = 0; i < comments.length; ++i) {\r\n
                        comment = this.findComment(comments[i].asc_getId());\r\n
                        comment.set("editTextInPopover", true);\r\n
                        comment.set("hint", false);\r\n
                        this.popoverComments.push(comment);\r\n
                    }\r\n
                    if (this.getPopover()) {\r\n
                        if (this.getPopover().isVisible()) {\r\n
                            this.getPopover().hide();\r\n
                        }\r\n
                        this.getPopover().setLeftTop(anchor.asc_getX() + anchor.asc_getWidth(), anchor.asc_getY(), this.hintmode ? anchor.asc_getX() : undefined);\r\n
                        this.getPopover().show(true, false, true);\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        focusOnInput: function () {\r\n
            if (this.view && this.api) {\r\n
                var panel = $("#comments-new-comment-ct", this.view.el);\r\n
                if (panel && panel.length) {\r\n
                    if ("none" !== panel.css("display")) {\r\n
                        this.api.asc_enableKeyEvents(false);\r\n
                        this.view.txtComment.focus();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        timeZoneOffsetInMs: (new Date()).getTimezoneOffset() * 60000,\r\n
        stringUtcToLocalDate: function (date) {\r\n
            if (typeof date === "string") {\r\n
                return parseInt(date) + this.timeZoneOffsetInMs;\r\n
            }\r\n
            return 0;\r\n
        },\r\n
        utcDateToString: function (date) {\r\n
            if (Object.prototype.toString.call(date) === "[object Date]") {\r\n
                return (date.getTime() - this.timeZoneOffsetInMs).toString();\r\n
            }\r\n
            return "";\r\n
        },\r\n
        dateToLocaleTimeString: function (date) {\r\n
            function format(date) {\r\n
                var strTime, hours = date.getHours(),\r\n
                minutes = date.getMinutes(),\r\n
                ampm = hours >= 12 ? "pm" : "am";\r\n
                hours = hours % 12;\r\n
                hours = hours ? hours : 12;\r\n
                minutes = minutes < 10 ? "0" + minutes : minutes;\r\n
                strTime = hours + ":" + minutes + " " + ampm;\r\n
                return strTime;\r\n
            }\r\n
            return (date.getMonth() + 1) + "/" + (date.getDate()) + "/" + date.getFullYear() + " " + format(date);\r\n
        }\r\n
    },\r\n
    Common.Controllers.Comments || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>49508</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
