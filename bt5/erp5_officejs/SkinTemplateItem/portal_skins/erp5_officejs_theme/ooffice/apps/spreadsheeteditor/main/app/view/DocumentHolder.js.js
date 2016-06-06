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
            <value> <string>ts44321338.16</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>DocumentHolder.js</string> </value>
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
 define(["jquery", "underscore", "backbone", "gateway", "common/main/lib/component/Menu"], function ($, _, Backbone, gateway) {\r\n
    SSE.Views.DocumentHolder = Backbone.View.extend(_.extend({\r\n
        el: "#editor_sdk",\r\n
        template: null,\r\n
        events: {},\r\n
        initialize: function () {\r\n
            var me = this;\r\n
            this.setApi = function (api) {\r\n
                me.api = api;\r\n
                return me;\r\n
            };\r\n
            var value = window.localStorage.getItem("sse-settings-livecomment");\r\n
            me.isLiveCommenting = !(value !== null && parseInt(value) == 0);\r\n
        },\r\n
        render: function () {\r\n
            this.fireEvent("render:before", this);\r\n
            this.cmpEl = $(this.el);\r\n
            this.fireEvent("render:after", this);\r\n
            return this;\r\n
        },\r\n
        focus: function () {\r\n
            var me = this;\r\n
            _.defer(function () {\r\n
                me.cmpEl.focus();\r\n
            },\r\n
            50);\r\n
        },\r\n
        createDelayedElements: function () {\r\n
            var me = this;\r\n
            me.pmiCut = new Common.UI.MenuItem({\r\n
                caption: me.txtCut,\r\n
                value: "cut"\r\n
            });\r\n
            me.pmiCopy = new Common.UI.MenuItem({\r\n
                caption: me.txtCopy,\r\n
                value: "copy"\r\n
            });\r\n
            me.pmiPaste = new Common.UI.MenuItem({\r\n
                caption: me.txtPaste,\r\n
                value: "paste"\r\n
            });\r\n
            me.pmiInsertEntire = new Common.UI.MenuItem({\r\n
                caption: me.txtInsert\r\n
            });\r\n
            me.pmiInsertCells = new Common.UI.MenuItem({\r\n
                caption: me.txtInsert,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [{\r\n
                        caption: me.txtShiftRight,\r\n
                        value: c_oAscInsertOptions.InsertCellsAndShiftRight\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtShiftDown,\r\n
                        value: c_oAscInsertOptions.InsertCellsAndShiftDown\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtRow,\r\n
                        value: c_oAscInsertOptions.InsertRows\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtColumn,\r\n
                        value: c_oAscInsertOptions.InsertColumns\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.pmiDeleteEntire = new Common.UI.MenuItem({\r\n
                caption: me.txtDelete\r\n
            });\r\n
            me.pmiDeleteCells = new Common.UI.MenuItem({\r\n
                caption: me.txtDelete,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [{\r\n
                        caption: me.txtShiftLeft,\r\n
                        value: c_oAscDeleteOptions.DeleteCellsAndShiftLeft\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtShiftUp,\r\n
                        value: c_oAscDeleteOptions.DeleteCellsAndShiftTop\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtRow,\r\n
                        value: c_oAscDeleteOptions.DeleteRows\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtColumn,\r\n
                        value: c_oAscDeleteOptions.DeleteColumns\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.pmiClear = new Common.UI.MenuItem({\r\n
                caption: me.txtClear,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [{\r\n
                        caption: me.txtClearAll,\r\n
                        value: c_oAscCleanOptions.All\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearText,\r\n
                        value: c_oAscCleanOptions.Text\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearFormat,\r\n
                        value: c_oAscCleanOptions.Format\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearComments,\r\n
                        value: c_oAscCleanOptions.Comments\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtClearHyper,\r\n
                        value: c_oAscCleanOptions.Hyperlinks\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.pmiSortCells = new Common.UI.MenuItem({\r\n
                caption: me.txtSort,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [{\r\n
                        caption: me.txtAscending,\r\n
                        value: "ascending"\r\n
                    },\r\n
                    {\r\n
                        caption: me.txtDescending,\r\n
                        value: "descending"\r\n
                    }]\r\n
                })\r\n
            });\r\n
            me.pmiInsFunction = new Common.UI.MenuItem({\r\n
                caption: me.txtFormula\r\n
            });\r\n
            me.menuAddHyperlink = new Common.UI.MenuItem({\r\n
                caption: me.txtInsHyperlink,\r\n
                inCell: true\r\n
            });\r\n
            me.menuEditHyperlink = new Common.UI.MenuItem({\r\n
                caption: me.editHyperlinkText,\r\n
                inCell: true\r\n
            });\r\n
            me.menuRemoveHyperlink = new Common.UI.MenuItem({\r\n
                caption: me.removeHyperlinkText\r\n
            });\r\n
            me.menuHyperlink = new Common.UI.MenuItem({\r\n
                caption: me.txtInsHyperlink,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [me.menuEditHyperlink, me.menuRemoveHyperlink]\r\n
                })\r\n
            });\r\n
            me.pmiRowHeight = new Common.UI.MenuItem({\r\n
                caption: me.txtRowHeight,\r\n
                action: "row-height"\r\n
            });\r\n
            me.pmiColumnWidth = new Common.UI.MenuItem({\r\n
                caption: me.txtColumnWidth,\r\n
                action: "column-width"\r\n
            });\r\n
            me.pmiEntireHide = new Common.UI.MenuItem({\r\n
                caption: me.txtHide\r\n
            });\r\n
            me.pmiEntireShow = new Common.UI.MenuItem({\r\n
                caption: me.txtShow\r\n
            });\r\n
            me.pmiAddComment = new Common.UI.MenuItem({\r\n
                id: "id-context-menu-item-add-comment",\r\n
                caption: me.txtAddComment\r\n
            });\r\n
            me.pmiCellMenuSeparator = new Common.UI.MenuItem({\r\n
                caption: "--"\r\n
            });\r\n
            me.ssMenu = new Common.UI.Menu({\r\n
                id: "id-context-menu-cell",\r\n
                items: [me.pmiCut, me.pmiCopy, me.pmiPaste, {\r\n
                    caption: "--"\r\n
                },\r\n
                me.pmiInsertEntire, me.pmiInsertCells, me.pmiDeleteEntire, me.pmiDeleteCells, me.pmiClear, me.pmiSortCells, {\r\n
                    caption: "--"\r\n
                },\r\n
                me.pmiAddComment, me.pmiCellMenuSeparator, me.pmiInsFunction, me.menuAddHyperlink, me.menuHyperlink, me.pmiRowHeight, me.pmiColumnWidth, me.pmiEntireHide, me.pmiEntireShow]\r\n
            });\r\n
            me.mnuGroupImg = new Common.UI.MenuItem({\r\n
                caption: this.txtGroup,\r\n
                iconCls: "mnu-group",\r\n
                type: "group",\r\n
                value: "grouping"\r\n
            });\r\n
            me.mnuUnGroupImg = new Common.UI.MenuItem({\r\n
                caption: this.txtUngroup,\r\n
                iconCls: "mnu-ungroup",\r\n
                type: "group",\r\n
                value: "ungrouping"\r\n
            });\r\n
            me.mnuShapeSeparator = new Common.UI.MenuItem({\r\n
                caption: "--"\r\n
            });\r\n
            me.mnuShapeAdvanced = new Common.UI.MenuItem({\r\n
                caption: me.advancedShapeText\r\n
            });\r\n
            me.mnuChartEdit = new Common.UI.MenuItem({\r\n
                caption: me.chartText\r\n
            });\r\n
            me.pmiImgCut = new Common.UI.MenuItem({\r\n
                caption: me.txtCut,\r\n
                value: "cut"\r\n
            });\r\n
            me.pmiImgCopy = new Common.UI.MenuItem({\r\n
                caption: me.txtCopy,\r\n
                value: "copy"\r\n
            });\r\n
            me.pmiImgPaste = new Common.UI.MenuItem({\r\n
                caption: me.txtPaste,\r\n
                value: "paste"\r\n
            });\r\n
            this.imgMenu = new Common.UI.Menu({\r\n
                items: [me.pmiImgCut, me.pmiImgCopy, me.pmiImgPaste, {\r\n
                    caption: "--"\r\n
                },\r\n
                {\r\n
                    caption: this.textArrangeFront,\r\n
                    iconCls: "mnu-arrange-front",\r\n
                    type: "arrange",\r\n
                    value: c_oAscDrawingLayerType.BringToFront\r\n
                },\r\n
                {\r\n
                    caption: this.textArrangeBack,\r\n
                    iconCls: "mnu-arrange-back",\r\n
                    type: "arrange",\r\n
                    value: c_oAscDrawingLayerType.SendToBack\r\n
                },\r\n
                {\r\n
                    caption: this.textArrangeForward,\r\n
                    iconCls: "mnu-arrange-forward",\r\n
                    type: "arrange",\r\n
                    value: c_oAscDrawingLayerType.BringForward\r\n
                },\r\n
                {\r\n
                    caption: this.textArrangeBackward,\r\n
                    iconCls: "mnu-arrange-backward",\r\n
                    type: "arrange",\r\n
                    value: c_oAscDrawingLayerType.SendBackward\r\n
                },\r\n
                {\r\n
                    caption: "--"\r\n
                },\r\n
                me.mnuGroupImg, me.mnuUnGroupImg, me.mnuShapeSeparator, me.mnuChartEdit, me.mnuShapeAdvanced]\r\n
            });\r\n
            this.menuParagraphVAlign = new Common.UI.MenuItem({\r\n
                caption: this.vertAlignText,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [me.menuParagraphTop = new Common.UI.MenuItem({\r\n
                        caption: me.topCellText,\r\n
                        checkable: true,\r\n
                        toggleGroup: "popupparagraphvalign",\r\n
                        value: c_oAscVerticalTextAlign.TEXT_ALIGN_TOP\r\n
                    }), me.menuParagraphCenter = new Common.UI.MenuItem({\r\n
                        caption: me.centerCellText,\r\n
                        checkable: true,\r\n
                        toggleGroup: "popupparagraphvalign",\r\n
                        value: c_oAscVerticalTextAlign.TEXT_ALIGN_CTR\r\n
                    }), this.menuParagraphBottom = new Common.UI.MenuItem({\r\n
                        caption: me.bottomCellText,\r\n
                        checkable: true,\r\n
                        toggleGroup: "popupparagraphvalign",\r\n
                        value: c_oAscVerticalTextAlign.TEXT_ALIGN_BOTTOM\r\n
                    })]\r\n
                })\r\n
            });\r\n
            me.menuAddHyperlinkShape = new Common.UI.MenuItem({\r\n
                caption: me.txtInsHyperlink\r\n
            });\r\n
            me.menuEditHyperlinkShape = new Common.UI.MenuItem({\r\n
                caption: me.editHyperlinkText\r\n
            });\r\n
            me.menuRemoveHyperlinkShape = new Common.UI.MenuItem({\r\n
                caption: me.removeHyperlinkText\r\n
            });\r\n
            me.menuHyperlinkShape = new Common.UI.MenuItem({\r\n
                caption: me.txtInsHyperlink,\r\n
                menu: new Common.UI.Menu({\r\n
                    menuAlign: "tl-tr",\r\n
                    items: [me.menuEditHyperlinkShape, me.menuRemoveHyperlinkShape]\r\n
                })\r\n
            });\r\n
            this.pmiTextAdvanced = new Common.UI.MenuItem({\r\n
                caption: me.txtTextAdvanced\r\n
            });\r\n
            me.pmiTextCut = new Common.UI.MenuItem({\r\n
                caption: me.txtCut,\r\n
                value: "cut"\r\n
            });\r\n
            me.pmiTextCopy = new Common.UI.MenuItem({\r\n
                caption: me.txtCopy,\r\n
                value: "copy"\r\n
            });\r\n
            me.pmiTextPaste = new Common.UI.MenuItem({\r\n
                caption: me.txtPaste,\r\n
                value: "paste"\r\n
            });\r\n
            this.textInShapeMenu = new Common.UI.Menu({\r\n
                items: [me.pmiTextCut, me.pmiTextCopy, me.pmiTextPaste, {\r\n
                    caption: "--"\r\n
                },\r\n
                me.menuParagraphVAlign, me.menuAddHyperlinkShape, me.menuHyperlinkShape, {\r\n
                    caption: "--"\r\n
                },\r\n
                me.pmiTextAdvanced]\r\n
            });\r\n
            this.funcMenu = new Common.UI.Menu({\r\n
                items: [{\r\n
                    caption: "item 1"\r\n
                },\r\n
                {\r\n
                    caption: "item 2"\r\n
                },\r\n
                {\r\n
                    caption: "item 3"\r\n
                },\r\n
                {\r\n
                    caption: "item 4"\r\n
                },\r\n
                {\r\n
                    caption: "item 5"\r\n
                }]\r\n
            });\r\n
            me.fireEvent("createdelayedelements", [me]);\r\n
        },\r\n
        setMenuItemCommentCaptionMode: function (edit) {\r\n
            edit ? this.pmiAddComment.setCaption(this.txtEditComment) : this.pmiAddComment.setCaption(this.txtAddComment);\r\n
        },\r\n
        setLiveCommenting: function (value) {\r\n
            this.isLiveCommenting = value;\r\n
        },\r\n
        txtSort: "Sort",\r\n
        txtAscending: "Ascending",\r\n
        txtDescending: "Descending",\r\n
        txtFormula: "Insert Function",\r\n
        txtInsHyperlink: "Hyperlink",\r\n
        txtCut: "Cut",\r\n
        txtCopy: "Copy",\r\n
        txtPaste: "Paste",\r\n
        txtInsert: "Insert",\r\n
        txtDelete: "Delete",\r\n
        txtClear: "Clear",\r\n
        txtClearAll: "All",\r\n
        txtClearText: "Text",\r\n
        txtClearFormat: "Format",\r\n
        txtClearHyper: "Hyperlink",\r\n
        txtClearComments: "Comments",\r\n
        txtShiftRight: "Shift cells right",\r\n
        txtShiftLeft: "Shift cells left",\r\n
        txtShiftUp: "Shift cells up",\r\n
        txtShiftDown: "Shift cells down",\r\n
        txtRow: "Entire Row",\r\n
        txtColumn: "Entire Column",\r\n
        txtColumnWidth: "Column Width",\r\n
        txtRowHeight: "Row Height",\r\n
        txtWidth: "Width",\r\n
        txtHide: "Hide",\r\n
        txtShow: "Show",\r\n
        textArrangeFront: "Bring To Front",\r\n
        textArrangeBack: "Send To Back",\r\n
        textArrangeForward: "Bring Forward",\r\n
        textArrangeBackward: "Send Backward",\r\n
        txtArrange: "Arrange",\r\n
        txtAddComment: "Add Comment",\r\n
        txtEditComment: "Edit Comment",\r\n
        txtUngroup: "Ungroup",\r\n
        txtGroup: "Group",\r\n
        topCellText: "Align Top",\r\n
        centerCellText: "Align Center",\r\n
        bottomCellText: "Align Bottom",\r\n
        vertAlignText: "Vertical Alignment",\r\n
        txtTextAdvanced: "Text Advanced Settings",\r\n
        editHyperlinkText: "Edit Hyperlink",\r\n
        removeHyperlinkText: "Remove Hyperlink",\r\n
        editChartText: "Edit Data",\r\n
        advancedShapeText: "Shape Advanced Settings",\r\n
        chartText: "Chart Advanced Settings"\r\n
    },\r\n
    SSE.Views.DocumentHolder || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16848</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
