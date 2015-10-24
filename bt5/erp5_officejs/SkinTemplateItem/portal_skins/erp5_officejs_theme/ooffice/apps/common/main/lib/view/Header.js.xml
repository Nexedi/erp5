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
            <value> <string>ts44321418.8</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Header.js</string> </value>
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
define(["backbone", "text!common/main/lib/template/Header.template", "core"], function (Backbone, headerTemplate) {\r\n
    Common.Views.Header = Backbone.View.extend(_.extend({\r\n
        options: {\r\n
            branding: {},\r\n
            headerCaption: "Default Caption",\r\n
            documentCaption: "",\r\n
            canBack: false\r\n
        },\r\n
        el: "#header",\r\n
        template: _.template(headerTemplate),\r\n
        events: {\r\n
            "click #header-logo": function (e) {\r\n
                var _url = !!this.branding && !!this.branding.logo && !!this.branding.logo.url ? this.branding.logo.url : "http://www.onlyoffice.com";\r\n
                var newDocumentPage = window.open(_url);\r\n
                newDocumentPage && newDocumentPage.focus();\r\n
            }\r\n
        },\r\n
        initialize: function (options) {\r\n
            this.options = this.options ? _({}).extend(this.options, options) : options;\r\n
            this.headerCaption = this.options.headerCaption;\r\n
            this.documentCaption = this.options.documentCaption;\r\n
            this.canBack = this.options.canBack;\r\n
            this.branding = this.options.customization;\r\n
        },\r\n
        render: function () {\r\n
            $(this.el).html(this.template({\r\n
                headerCaption: this.headerCaption,\r\n
                documentCaption: Common.Utils.String.htmlEncode(this.documentCaption),\r\n
                canBack: this.canBack,\r\n
                textBack: this.textBack\r\n
            }));\r\n
        },\r\n
        setVisible: function (visible) {\r\n
            visible ? this.show() : this.hide();\r\n
        },\r\n
        setBranding: function (value) {\r\n
            var element;\r\n
            this.branding = value;\r\n
            if (value && value.logo && value.logo.image) {\r\n
                element = $("#header-logo");\r\n
                if (element) {\r\n
                    element.css("background-image", \'url("\' + value.logo.image + \'")\');\r\n
                }\r\n
            }\r\n
        },\r\n
        setHeaderCaption: function (value) {\r\n
            this.headerCaption = value;\r\n
            var caption = $("#header-caption > div");\r\n
            if (caption) {\r\n
                caption.html(value);\r\n
            }\r\n
            return value;\r\n
        },\r\n
        getHeaderCaption: function () {\r\n
            return this.headerCaption;\r\n
        },\r\n
        setDocumentCaption: function (value, applyOnly) {\r\n
            if (_.isUndefined(applyOnly)) {\r\n
                this.documentCaption = value;\r\n
            }\r\n
            if (!value) {\r\n
                value = "";\r\n
            }\r\n
            var dc = $("#header-documentcaption");\r\n
            if (dc) {\r\n
                dc.html(Common.Utils.String.htmlEncode(value));\r\n
            }\r\n
            return value;\r\n
        },\r\n
        getDocumentCaption: function () {\r\n
            return this.documentCaption;\r\n
        },\r\n
        setCanBack: function (value) {\r\n
            this.canBack = value;\r\n
            var back = $("#header-back");\r\n
            if (back) {\r\n
                back.off("click");\r\n
                back.css("display", value ? "table-cell" : "none");\r\n
                if (value) {\r\n
                    back.on("click", _.bind(this.onBackClick, this));\r\n
                }\r\n
            }\r\n
        },\r\n
        getCanBack: function () {\r\n
            return this.canBack;\r\n
        },\r\n
        onBackClick: function (e) {\r\n
            Common.Gateway.goBack(e.which == 2);\r\n
            Common.component.Analytics.trackEvent("Back to Folder");\r\n
        },\r\n
        textBack: "Go to Documents"\r\n
    },\r\n
    Common.Views.Header || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5243</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
