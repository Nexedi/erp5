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
            <value> <string>ts44321338.26</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>FileMenu.js</string> </value>
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
 define(["text!spreadsheeteditor/main/app/template/FileMenu.template", "underscore", "common/main/lib/component/BaseView"], function (tpl, _) {\r\n
    SSE.Views.FileMenu = Common.UI.BaseView.extend(_.extend({\r\n
        el: "#file-menu-panel",\r\n
        template: _.template(tpl),\r\n
        events: function () {\r\n
            return {\r\n
                "click .fm-btn": _.bind(function (event) {\r\n
                    var $item = $(event.currentTarget);\r\n
                    if (!$item.hasClass("active")) {\r\n
                        $(".fm-btn", this.el).removeClass("active");\r\n
                        $item.addClass("active");\r\n
                    }\r\n
                    var item = _.findWhere(this.items, {\r\n
                        el: event.currentTarget\r\n
                    });\r\n
                    if (item) {\r\n
                        var panel = this.panels[item.options.action];\r\n
                        this.fireEvent("item:click", [this, item.options.action, !!panel]);\r\n
                        if (panel) {\r\n
                            this.$el.find(".content-box:visible").hide();\r\n
                            this.active = item.options.action;\r\n
                            panel.show();\r\n
                        }\r\n
                    }\r\n
                },\r\n
                this)\r\n
            };\r\n
        },\r\n
        initialize: function () {},\r\n
        render: function () {\r\n
            this.$el = $(this.el);\r\n
            this.$el.html(this.template());\r\n
            this.items = [];\r\n
            this.items.push(new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-return", this.el),\r\n
                action: "back",\r\n
                caption: this.btnReturnCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-save", this.el),\r\n
                action: "save",\r\n
                caption: this.btnSaveCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-edit", this.el),\r\n
                action: "edit",\r\n
                caption: this.btnToEditCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-download", this.el),\r\n
                action: "saveas",\r\n
                caption: this.btnDownloadCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-print", this.el),\r\n
                action: "print",\r\n
                caption: this.btnPrintCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-recent", this.el),\r\n
                action: "recent",\r\n
                caption: this.btnRecentFilesCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-create", this.el),\r\n
                action: "new",\r\n
                caption: this.btnCreateNewCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-info", this.el),\r\n
                action: "info",\r\n
                caption: this.btnInfoCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-rights", this.el),\r\n
                action: "rights",\r\n
                caption: this.btnRightsCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-settings", this.el),\r\n
                action: "opts",\r\n
                caption: this.btnSettingsCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-help", this.el),\r\n
                action: "help",\r\n
                caption: this.btnHelpCaption,\r\n
                canFocused: false\r\n
            }), new Common.UI.MenuItem({\r\n
                el: $("#fm-btn-back", this.el),\r\n
                action: "exit",\r\n
                caption: this.btnBackCaption,\r\n
                canFocused: false\r\n
            }));\r\n
            var me = this;\r\n
            this.panels = {};\r\n
            require(["spreadsheeteditor/main/app/view/FileMenuPanels"], function () {\r\n
                me.panels = {\r\n
                    "saveas": (new SSE.Views.FileMenuPanels.ViewSaveAs({\r\n
                        menu: me\r\n
                    })).render(),\r\n
                    "opts": (new SSE.Views.FileMenuPanels.Settings({\r\n
                        menu: me\r\n
                    })).render(),\r\n
                    "info": (new SSE.Views.FileMenuPanels.DocumentInfo({\r\n
                        menu: me\r\n
                    })).render(),\r\n
                    "rights": (new SSE.Views.FileMenuPanels.DocumentRights({\r\n
                        menu: me\r\n
                    })).render(),\r\n
                    "help": (new SSE.Views.FileMenuPanels.Help({\r\n
                        menu: me\r\n
                    })).render()\r\n
                };\r\n
                me.$el.find(".content-box").hide();\r\n
            });\r\n
            return this;\r\n
        },\r\n
        show: function (panel) {\r\n
            if (this.isVisible() && panel === undefined) {\r\n
                return;\r\n
            }\r\n
            if (!panel) {\r\n
                panel = this.active || (this.mode.canDownload ? "saveas" : "info");\r\n
            }\r\n
            this.$el.show();\r\n
            this.selectMenu(panel);\r\n
            if (this.mode.isEdit) {\r\n
                SSE.getController("Toolbar").DisableToolbar(true);\r\n
            }\r\n
            this.api.asc_enableKeyEvents(false);\r\n
        },\r\n
        hide: function () {\r\n
            this.$el.hide();\r\n
            if (this.mode.isEdit) {\r\n
                SSE.getController("Toolbar").DisableToolbar(false);\r\n
            }\r\n
            this.api.asc_enableKeyEvents(true);\r\n
        },\r\n
        applyMode: function () {\r\n
            this.items[5][this.mode.canOpenRecent ? "show" : "hide"]();\r\n
            this.items[6][this.mode.canCreateNew ? "show" : "hide"]();\r\n
            this.items[6].$el.find("+.devider")[this.mode.canCreateNew ? "show" : "hide"]();\r\n
            this.items[3][this.mode.canDownload ? "show" : "hide"]();\r\n
            this.items[1][this.mode.isEdit ? "show" : "hide"]();\r\n
            this.items[2][!this.mode.isEdit && this.mode.canEdit ? "show" : "hide"]();\r\n
            this.items[8][(this.document && this.document.info && (this.document.info.sharingSettings && this.document.info.sharingSettings.length > 0 || this.mode.sharingSettingsUrl && this.mode.sharingSettingsUrl.length)) ? "show" : "hide"]();\r\n
            this.items[9][this.mode.isEdit ? "show" : "hide"]();\r\n
            this.items[9].$el.find("+.devider")[this.mode.isEdit ? "show" : "hide"]();\r\n
            this.panels["opts"].setMode(this.mode);\r\n
            this.panels["info"].setMode(this.mode).updateInfo(this.document);\r\n
            this.panels["rights"].setMode(this.mode).updateInfo(this.document);\r\n
            if (this.mode.canCreateNew) {\r\n
                if (this.mode.templates && this.mode.templates.length) {\r\n
                    $("a", this.items[6].$el).text(this.btnCreateNewCaption + "...");\r\n
                    this.panels["new"] = ((new SSE.Views.FileMenuPanels.CreateNew({\r\n
                        menu: this,\r\n
                        docs: this.mode.templates\r\n
                    })).render());\r\n
                }\r\n
            }\r\n
            if (this.mode.canOpenRecent) {\r\n
                if (this.mode.recent) {\r\n
                    this.panels["recent"] = (new SSE.Views.FileMenuPanels.RecentFiles({\r\n
                        menu: this,\r\n
                        recent: this.mode.recent\r\n
                    })).render();\r\n
                }\r\n
            }\r\n
            this.panels["help"].setLangConfig(this.mode.lang);\r\n
        },\r\n
        setMode: function (mode, delay) {\r\n
            if (mode.isDisconnected) {\r\n
                this.mode.canEdit = this.mode.isEdit = false;\r\n
                this.mode.canOpenRecent = this.mode.canCreateNew = false;\r\n
            } else {\r\n
                this.mode = mode;\r\n
            }\r\n
            if (!delay) {\r\n
                this.applyMode();\r\n
            }\r\n
        },\r\n
        setApi: function (api) {\r\n
            this.api = api;\r\n
        },\r\n
        loadDocument: function (data) {\r\n
            this.document = data.doc;\r\n
        },\r\n
        selectMenu: function (menu) {\r\n
            if (menu) {\r\n
                var item = this._getMenuItem(menu),\r\n
                panel = this.panels[menu];\r\n
                if (item && panel) {\r\n
                    $(".fm-btn", this.el).removeClass("active");\r\n
                    item.$el.addClass("active");\r\n
                    this.$el.find(".content-box:visible").hide();\r\n
                    panel.show();\r\n
                    this.active = menu;\r\n
                }\r\n
            }\r\n
        },\r\n
        _getMenuItem: function (action) {\r\n
            return _.find(this.items, function (item) {\r\n
                return item.options.action == action;\r\n
            });\r\n
        },\r\n
        btnSaveCaption: "Save",\r\n
        btnDownloadCaption: "Download as...",\r\n
        btnInfoCaption: "Document Info...",\r\n
        btnRightsCaption: "Access Rights...",\r\n
        btnCreateNewCaption: "Create New",\r\n
        btnRecentFilesCaption: "Open Recent...",\r\n
        btnPrintCaption: "Print",\r\n
        btnHelpCaption: "Help...",\r\n
        btnReturnCaption: "Back to Document",\r\n
        btnToEditCaption: "Edit Document",\r\n
        btnBackCaption: "Maximize (Minimize)",\r\n
        btnSettingsCaption: "Advanced Settings..."\r\n
    },\r\n
    SSE.Views.FileMenu || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11156</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
