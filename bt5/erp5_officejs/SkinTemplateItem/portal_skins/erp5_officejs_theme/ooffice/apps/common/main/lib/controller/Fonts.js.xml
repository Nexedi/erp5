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
            <value> <string>ts44308801.77</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Fonts.js</string> </value>
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
define(["core", "common/main/lib/collection/Fonts"], function () {\r\n
    Common.Controllers.Fonts = Backbone.Controller.extend((function () {\r\n
        var FONT_TYPE_USERUSED = 4;\r\n
        function isFontSaved(store, rec) {\r\n
            var out = rec.get("type") == FONT_TYPE_USERUSED,\r\n
            i = -1,\r\n
            c = store.length,\r\n
            su,\r\n
            n = rec.get("name");\r\n
            while (!out && ++i < c) {\r\n
                su = store.at(i);\r\n
                if (su.get("type") != FONT_TYPE_USERUSED) {\r\n
                    break;\r\n
                }\r\n
                out = su.get("name") == n;\r\n
            }\r\n
            return out;\r\n
        }\r\n
        function onSelectFont(combo, record) {\r\n
            if (combo.showlastused && !isFontSaved(combo.store, record)) {}\r\n
        }\r\n
        function onApiFontChange(fontobj) {\r\n
            Common.NotificationCenter.trigger("fonts:change", fontobj);\r\n
        }\r\n
        function onApiLoadFonts(fonts, select) {\r\n
            var fontsArray = [];\r\n
            _.each(fonts, function (font) {\r\n
                var fontId = font.asc_getFontId();\r\n
                fontsArray.push({\r\n
                    id: _.isEmpty(fontId) ? Common.UI.getId() : fontId,\r\n
                    name: font.asc_getFontName(),\r\n
                    imgidx: font.asc_getFontThumbnail(),\r\n
                    type: font.asc_getFontType()\r\n
                });\r\n
            });\r\n
            var store = this.getCollection("Common.Collections.Fonts");\r\n
            if (store) {\r\n
                store.add(fontsArray);\r\n
            }\r\n
            Common.NotificationCenter.trigger("fonts:load", store, select);\r\n
        }\r\n
        return {\r\n
            models: ["Common.Models.Fonts"],\r\n
            collections: ["Common.Collections.Fonts"],\r\n
            views: [],\r\n
            initialize: function () {\r\n
                Common.NotificationCenter.on("fonts:select", _.bind(onSelectFont, this));\r\n
            },\r\n
            onLaunch: function () {},\r\n
            setApi: function (api) {\r\n
                this.api = api;\r\n
                this.api.asc_registerCallback("asc_onInitEditorFonts", _.bind(onApiLoadFonts, this));\r\n
                this.api.asc_registerCallback("asc_onFontFamily", _.bind(onApiFontChange, this));\r\n
            },\r\n
            loadFonts: function (select) {\r\n
                if (this.api) {\r\n
                    var fonts = this.api.get_PropertyEditorFonts();\r\n
                    if (fonts) {\r\n
                        onApiLoadFonts.call(this, fonts, select);\r\n
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
            <value> <int>4284</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
