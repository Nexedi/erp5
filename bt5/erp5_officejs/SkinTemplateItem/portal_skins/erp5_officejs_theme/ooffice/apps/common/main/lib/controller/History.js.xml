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
            <value> <string>ts44308801.86</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>History.js</string> </value>
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
 define(["core", "common/main/lib/collection/HistoryVersions", "common/main/lib/view/History"], function () {\r\n
    Common.Controllers.History = Backbone.Controller.extend(_.extend({\r\n
        models: [],\r\n
        collections: ["Common.Collections.HistoryVersions"],\r\n
        views: ["Common.Views.History"],\r\n
        initialize: function () {\r\n
            this.currentChangeId = -1;\r\n
            this.currentArrColors = [];\r\n
            this.currentDocId = "";\r\n
            this.currentDocIdPrev = "";\r\n
        },\r\n
        events: {},\r\n
        onLaunch: function () {\r\n
            this.panelHistory = this.createView("Common.Views.History", {\r\n
                storeHistory: this.getApplication().getCollection("Common.Collections.HistoryVersions")\r\n
            });\r\n
            this.panelHistory.on("render:after", _.bind(this.onAfterRender, this));\r\n
            Common.Gateway.on("sethistorydata", _.bind(this.onSetHistoryData, this));\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
        },\r\n
        onAfterRender: function (historyView) {\r\n
            historyView.viewHistoryList.on("item:click", _.bind(this.onSelectRevision, this));\r\n
            historyView.btnBackToDocument.on("click", _.bind(this.onClickBackToDocument, this));\r\n
        },\r\n
        onSelectRevision: function (picker, item, record) {\r\n
            var url = record.get("url"),\r\n
            rev = record.get("revision"),\r\n
            urlGetTime = new Date();\r\n
            this.currentChangeId = record.get("changeid");\r\n
            this.currentArrColors = record.get("arrColors");\r\n
            this.currentDocId = record.get("docId");\r\n
            this.currentDocIdPrev = record.get("docIdPrev");\r\n
            if (_.isEmpty(url) || (urlGetTime - record.get("urlGetTime") > 5 * 60000)) {\r\n
                _.delay(function () {\r\n
                    Common.Gateway.requestHistoryData(rev);\r\n
                },\r\n
                10);\r\n
            } else {\r\n
                var urlDiff = record.get("urlDiff"),\r\n
                hist = new Asc.asc_CVersionHistory();\r\n
                hist.asc_setDocId(_.isEmpty(urlDiff) ? this.currentDocId : this.currentDocIdPrev);\r\n
                hist.asc_setUrl(url);\r\n
                hist.asc_setUrlChanges(urlDiff);\r\n
                hist.asc_setCurrentChangeId(this.currentChangeId);\r\n
                hist.asc_setArrColors(this.currentArrColors);\r\n
                this.api.asc_showRevision(hist);\r\n
                var commentsController = this.getApplication().getController("Common.Controllers.Comments");\r\n
                if (commentsController) {\r\n
                    commentsController.onApiHideComment();\r\n
                }\r\n
            }\r\n
        },\r\n
        onSetHistoryData: function (opts) {\r\n
            if (opts.data.error) {\r\n
                var config = {\r\n
                    closable: false,\r\n
                    title: this.notcriticalErrorTitle,\r\n
                    msg: opts.data.error,\r\n
                    iconCls: "warn",\r\n
                    buttons: ["ok"]\r\n
                };\r\n
                Common.UI.alert(config);\r\n
            } else {\r\n
                var data = opts.data;\r\n
                var historyStore = this.getApplication().getCollection("Common.Collections.HistoryVersions");\r\n
                if (historyStore && data !== null) {\r\n
                    var rev, revisions = historyStore.findRevisions(data.version),\r\n
                    urlGetTime = new Date();\r\n
                    if (revisions && revisions.length > 0) {\r\n
                        for (var i = 0; i < revisions.length; i++) {\r\n
                            rev = revisions[i];\r\n
                            rev.set("url", opts.data.url);\r\n
                            rev.set("urlDiff", opts.data.urlDiff);\r\n
                            rev.set("urlGetTime", urlGetTime);\r\n
                        }\r\n
                    }\r\n
                    var hist = new Asc.asc_CVersionHistory();\r\n
                    hist.asc_setUrl(opts.data.url);\r\n
                    hist.asc_setUrlChanges(opts.data.urlDiff);\r\n
                    hist.asc_setDocId(_.isEmpty(opts.data.urlDiff) ? this.currentDocId : this.currentDocIdPrev);\r\n
                    hist.asc_setCurrentChangeId(this.currentChangeId);\r\n
                    hist.asc_setArrColors(this.currentArrColors);\r\n
                    this.api.asc_showRevision(hist);\r\n
                    var commentsController = this.getApplication().getController("Common.Controllers.Comments");\r\n
                    if (commentsController) {\r\n
                        commentsController.onApiHideComment();\r\n
                    }\r\n
                }\r\n
            }\r\n
        },\r\n
        onClickBackToDocument: function () {\r\n
            Common.Gateway.requestHistoryClose();\r\n
        },\r\n
        notcriticalErrorTitle: "Warning"\r\n
    },\r\n
    Common.Controllers.History || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6417</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
