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
            <value> <string>ts44308768.11</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>View.js</string> </value>
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
 Ext.define("SSE.controller.toolbar.View", {\r\n
    extend: "Ext.app.Controller",\r\n
    config: {\r\n
        refs: {\r\n
            viewToolbar: "viewtoolbar",\r\n
            searchToolbar: "searchtoolbar",\r\n
            worksheetPanel: "#id-worksheets-panel",\r\n
            doneButton: "#id-tb-btn-view-done",\r\n
            searchButton: "#id-tb-btn-search",\r\n
            fullscreenButton: "#id-tb-btn-fullscreen",\r\n
            shareButton: "#id-tb-btn-view-share",\r\n
            worksheetsButton: "#id-tb-btn-pages"\r\n
        },\r\n
        control: {\r\n
            doneButton: {\r\n
                tap: "onTapDoneButton"\r\n
            },\r\n
            searchButton: {\r\n
                tap: "onTapSearchButton"\r\n
            },\r\n
            fullscreenButton: {\r\n
                tap: "onTapFullscreenButton"\r\n
            },\r\n
            shareButton: {\r\n
                tap: "onTapShareButton"\r\n
            },\r\n
            worksheetsButton: {\r\n
                tap: "onTapWorksheets"\r\n
            },\r\n
            "#id-worksheets-panel seworksheetlist list": {\r\n
                itemtap: "onSelectWorksheet"\r\n
            }\r\n
        },\r\n
        searchMode: false,\r\n
        fullscreenMode: false\r\n
    },\r\n
    launch: function () {\r\n
        this.callParent(arguments);\r\n
        Common.Gateway.on("init", Ext.bind(this.loadConfig, this));\r\n
    },\r\n
    initControl: function () {\r\n
        this.callParent(arguments);\r\n
    },\r\n
    initApi: function () {},\r\n
    setApi: function (o) {\r\n
        this.api = o;\r\n
        if (this.api) {\r\n
            this.api.asc_registerCallback("asc_onTapEvent", Ext.bind(this.onSingleTapDocument, this));\r\n
        }\r\n
    },\r\n
    loadConfig: function (data) {\r\n
        var doneButton = this.getDoneButton();\r\n
        if (doneButton && data && data.config && data.config.canBackToFolder === true) {\r\n
            doneButton.show();\r\n
        }\r\n
    },\r\n
    applySearchMode: function (search) {\r\n
        if (!Ext.isBoolean(search)) {\r\n
            Ext.Logger.error("Invalid parameters.");\r\n
        } else {\r\n
            var me = this,\r\n
            searchToolbar = me.getSearchToolbar(),\r\n
            searchButton = me.getSearchButton();\r\n
            if (searchToolbar) {\r\n
                if (search) {\r\n
                    searchButton && searchButton.addCls("x-button-pressing");\r\n
                    if (me.getFullscreenMode()) {\r\n
                        searchToolbar.show({\r\n
                            easing: "ease-out",\r\n
                            preserveEndState: true,\r\n
                            autoClear: false,\r\n
                            from: {\r\n
                                top: "22px",\r\n
                                opacity: 0.3\r\n
                            },\r\n
                            to: {\r\n
                                top: "44px",\r\n
                                opacity: 0.9\r\n
                            }\r\n
                        });\r\n
                    } else {\r\n
                        searchToolbar.show();\r\n
                    }\r\n
                } else {\r\n
                    if (me.getFullscreenMode()) {\r\n
                        searchToolbar.hide({\r\n
                            easing: "ease-in",\r\n
                            to: {\r\n
                                top: "22px",\r\n
                                opacity: 0.3\r\n
                            }\r\n
                        });\r\n
                    } else {\r\n
                        searchToolbar.hide();\r\n
                    }\r\n
                }\r\n
            }\r\n
            return search;\r\n
        }\r\n
    },\r\n
    applyFullscreenMode: function (fullscreen) {\r\n
        if (!Ext.isBoolean(fullscreen)) {\r\n
            Ext.Logger.error("Invalid parameters.");\r\n
        } else {\r\n
            var viewToolbar = this.getViewToolbar(),\r\n
            searchToolbar = this.getSearchToolbar(),\r\n
            fullscreenButton = this.getFullscreenButton(),\r\n
            popClipCmp = Ext.ComponentQuery.query("popclip");\r\n
            if (popClipCmp.length > 0) {\r\n
                popClipCmp[0].hide();\r\n
            }\r\n
            if (viewToolbar && searchToolbar) {\r\n
                if (fullscreen) {\r\n
                    fullscreenButton && fullscreenButton.addCls("x-button-pressing");\r\n
                    viewToolbar.setStyle({\r\n
                        position: "absolute",\r\n
                        left: 0,\r\n
                        top: 0,\r\n
                        right: 0,\r\n
                        opacity: 0.9,\r\n
                        "z-index": 17\r\n
                    });\r\n
                    searchToolbar.setStyle({\r\n
                        position: "absolute",\r\n
                        left: 0,\r\n
                        top: "44px",\r\n
                        right: 0,\r\n
                        opacity: 0.9,\r\n
                        "z-index": 16\r\n
                    });\r\n
                    this.setHiddenToolbars(true);\r\n
                } else {\r\n
                    viewToolbar.setStyle({\r\n
                        position: "initial",\r\n
                        opacity: 1\r\n
                    });\r\n
                    searchToolbar.setStyle({\r\n
                        position: "initial",\r\n
                        opacity: 1\r\n
                    });\r\n
                    viewToolbar.setDocked("top");\r\n
                    searchToolbar.setDocked("top");\r\n
                }\r\n
            }\r\n
            return fullscreen;\r\n
        }\r\n
    },\r\n
    setHiddenToolbars: function (hide) {\r\n
        var viewToolbar = this.getViewToolbar(),\r\n
        searchToolbar = this.getSearchToolbar();\r\n
        if (viewToolbar && searchToolbar) {\r\n
            if (hide) {\r\n
                viewToolbar.hide({\r\n
                    easing: "ease-out",\r\n
                    from: {\r\n
                        opacity: 0.9\r\n
                    },\r\n
                    to: {\r\n
                        opacity: 0\r\n
                    }\r\n
                });\r\n
                searchToolbar.hide({\r\n
                    easing: "ease-out",\r\n
                    from: {\r\n
                        opacity: 0.9\r\n
                    },\r\n
                    to: {\r\n
                        opacity: 0\r\n
                    }\r\n
                });\r\n
            } else {\r\n
                viewToolbar.show({\r\n
                    preserveEndState: true,\r\n
                    easing: "ease-in",\r\n
                    from: {\r\n
                        opacity: 0\r\n
                    },\r\n
                    to: {\r\n
                        opacity: 0.9\r\n
                    }\r\n
                });\r\n
                this.getSearchMode() && searchToolbar.show({\r\n
                    preserveEndState: true,\r\n
                    easing: "ease-in",\r\n
                    from: {\r\n
                        opacity: 0\r\n
                    },\r\n
                    to: {\r\n
                        opacity: 0.9\r\n
                    }\r\n
                });\r\n
            }\r\n
        }\r\n
    },\r\n
    onTapDoneButton: function () {\r\n
        Common.Gateway.goBack();\r\n
    },\r\n
    onTapSearchButton: function (btn) {\r\n
        this.setSearchMode(!this.getSearchMode());\r\n
    },\r\n
    onTapFullscreenButton: function (btn) {\r\n
        this.setFullscreenMode(!this.getFullscreenMode());\r\n
        if (this.api) {\r\n
            this.api.asc_Resize();\r\n
        }\r\n
    },\r\n
    onTapShareButton: function () {\r\n
        this.api && this.api.asc_Print();\r\n
        Common.component.Analytics.trackEvent("ToolBar View", "Share");\r\n
    },\r\n
    onSingleTapDocument: function () {\r\n
        var viewToolbar = this.getViewToolbar();\r\n
        if (viewToolbar && this.getFullscreenMode()) {\r\n
            this.setHiddenToolbars(!viewToolbar.isHidden());\r\n
        }\r\n
    },\r\n
    onTapWorksheets: function () {\r\n
        var worksheetPanel = this.getWorksheetPanel(),\r\n
        worksheetsButton = this.getWorksheetsButton();\r\n
        if (worksheetPanel) {\r\n
            worksheetPanel.showBy(worksheetsButton);\r\n
        }\r\n
    },\r\n
    onSelectWorksheet: function (dataview, index, target, record, event, eOpts) {\r\n
        var worksheetPanel = this.getWorksheetPanel();\r\n
        if (worksheetPanel) {\r\n
            worksheetPanel.hide();\r\n
        }\r\n
    }\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9629</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
