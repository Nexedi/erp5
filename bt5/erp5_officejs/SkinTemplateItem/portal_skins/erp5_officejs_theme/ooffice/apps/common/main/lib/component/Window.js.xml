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
            <value> <string>ts44308801.36</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Window.js</string> </value>
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
define(["common/main/lib/component/BaseView"], function () {\r\n
    Common.UI.Window = Common.UI.BaseView.extend(_.extend((function () {\r\n
        var config = {\r\n
            closable: true,\r\n
            header: true,\r\n
            modal: true,\r\n
            width: 300,\r\n
            height: "auto",\r\n
            title: "Title",\r\n
            alias: "Window",\r\n
            cls: "",\r\n
            toolclose: "close"\r\n
        };\r\n
        var template = \'<div class="asc-window<%= modal?" modal":"" %><%= cls?" "+cls:"" %>" id="<%= id %>" style="width:<%= width %>px;">\' + "<% if (header==true) { %>" + \'<div class="header">\' + "<% if (closable!==false) %>" + \'<div class="tool close"></div>\' + "<% %>" + \'<span class="title"><%= title %></span> \' + "</div>" + "<% } %>" + \'<div class="body"><%= tpl %></div>\' + "</div>";\r\n
        function _getMask() {\r\n
            var mask = $(".modals-mask");\r\n
            if (mask.length == 0) {\r\n
                mask = $("<div class=\'modals-mask\'>").appendTo(document.body).hide();\r\n
            }\r\n
            return mask;\r\n
        }\r\n
        function _keydown(event) {\r\n
            if (!this.isLocked() && this.isVisible()) {\r\n
                switch (event.keyCode) {\r\n
                case Common.UI.Keys.ESC:\r\n
                    event.preventDefault();\r\n
                    event.stopPropagation();\r\n
                    if (this.initConfig.closable !== false) {\r\n
                        this.initConfig.toolclose == "hide" ? this.hide() : this.close();\r\n
                    }\r\n
                    return false;\r\n
                    break;\r\n
                case Common.UI.Keys.RETURN:\r\n
                    if (this.$window.find(".btn.primary").length) {\r\n
                        if ((this.initConfig.onprimary || this.onPrimary).call(this) === false) {\r\n
                            event.preventDefault();\r\n
                            return false;\r\n
                        }\r\n
                    }\r\n
                    break;\r\n
                }\r\n
            }\r\n
        }\r\n
        function _centre() {\r\n
            if (window.innerHeight == undefined) {\r\n
                var main_width = document.documentElement.offsetWidth;\r\n
                var main_height = document.documentElement.offsetHeight;\r\n
            } else {\r\n
                main_width = window.innerWidth;\r\n
                main_height = window.innerHeight;\r\n
            }\r\n
            if (this.initConfig.height == "auto") {\r\n
                var win_height = parseInt(this.$window.find(".body").css("height"));\r\n
                this.initConfig.header && (win_height += parseInt(this.$window.find(".header").css("height")));\r\n
            } else {\r\n
                win_height = this.initConfig.height;\r\n
            }\r\n
            var top = Math.floor(((parseInt(main_height) - parseInt(win_height)) / 2) * 0.9);\r\n
            var left = Math.floor((parseInt(main_width) - parseInt(this.initConfig.width)) / 2);\r\n
            this.$window.css("left", left);\r\n
            this.$window.css("top", top);\r\n
        }\r\n
        function _getTransformation(end) {\r\n
            return {\r\n
                "-webkit-transition": "0.3s opacity",\r\n
                "-moz-transition": "0.3s opacity",\r\n
                "-ms-transition": "0.3s opacity",\r\n
                "-o-transition": "0.3s opacity",\r\n
                "opacity": end\r\n
            };\r\n
        }\r\n
        function _dragstart(event) {\r\n
            if ($(event.target).hasClass("close")) {\r\n
                return;\r\n
            }\r\n
            Common.UI.Menu.Manager.hideAll();\r\n
            this.dragging.enabled = true;\r\n
            this.dragging.initx = event.pageX - parseInt(this.$window.css("left"));\r\n
            this.dragging.inity = event.pageY - parseInt(this.$window.css("top"));\r\n
            if (window.innerHeight == undefined) {\r\n
                var main_width = document.documentElement.offsetWidth;\r\n
                var main_height = document.documentElement.offsetHeight;\r\n
            } else {\r\n
                main_width = window.innerWidth;\r\n
                main_height = window.innerHeight;\r\n
            }\r\n
            this.dragging.maxx = main_width - parseInt(this.$window.css("width"));\r\n
            this.dragging.maxy = main_height - parseInt(this.$window.css("height"));\r\n
            $(document).on("mousemove", this.binding.drag);\r\n
            $(document).on("mouseup", this.binding.dragStop);\r\n
            this.fireEvent("drag", [this, "start"]);\r\n
        }\r\n
        function _mouseup() {\r\n
            $(document).off("mousemove", this.binding.drag);\r\n
            $(document).off("mouseup", this.binding.dragStop);\r\n
            this.dragging.enabled = false;\r\n
            this.fireEvent("drag", [this, "end"]);\r\n
        }\r\n
        function _mousemove(event) {\r\n
            if (this.dragging.enabled) {\r\n
                var left = event.pageX - this.dragging.initx,\r\n
                top = event.pageY - this.dragging.inity;\r\n
                left < 0 ? (left = 0) : left > this.dragging.maxx && (left = this.dragging.maxx);\r\n
                top < 0 ? (top = 0) : top > this.dragging.maxy && (top = this.dragging.maxy);\r\n
                this.$window.css({\r\n
                    left: left,\r\n
                    top: top\r\n
                });\r\n
            }\r\n
        }\r\n
        Common.UI.alert = function (options) {\r\n
            var me = this.Window.prototype;\r\n
            var arrBtns = {\r\n
                ok: me.okButtonText,\r\n
                cancel: me.cancelButtonText,\r\n
                yes: me.yesButtonText,\r\n
                no: me.noButtonText,\r\n
                close: me.closeButtonText\r\n
            };\r\n
            if (!options.buttons) {\r\n
                options.buttons = {};\r\n
                options.buttons["ok"] = arrBtns["ok"];\r\n
            } else {\r\n
                if (_.isArray(options.buttons)) {\r\n
                    var newBtns = {};\r\n
                    _.each(options.buttons, function (b) {\r\n
                        newBtns[b] = arrBtns[b];\r\n
                    });\r\n
                    options.buttons = newBtns;\r\n
                }\r\n
            }\r\n
            var template = \'<div class="info-box">\' + \'<div class="icon <%= iconCls %>" />\' + \'<div class="text"><span><%= msg %></span></div>\' + "</div>" + \'<div class="footer">\' + \'<button class="btn normal dlg-btn primary" result="ok">OK</button>\' + "<% if (_.size(buttons) > 1) %>" + \'<button class="btn normal dlg-btn" result="cancel">Cancel</button>\' + "<% %>" + "</div>";\r\n
            var win = new Common.UI.Window({\r\n
                cls: "alert",\r\n
                title: options.title,\r\n
                onprimary: onKeyDown,\r\n
                tpl: _.template(template, options)\r\n
            });\r\n
            function autoSize(window) {\r\n
                var text_cnt = window.getChild(".info-box");\r\n
                var text = window.getChild(".info-box span");\r\n
                var footer = window.getChild(".footer");\r\n
                var header = window.getChild(".header");\r\n
                var body = window.getChild(".body");\r\n
                var icon = window.getChild(".icon");\r\n
                body.css("padding-bottom", "10px");\r\n
                text_cnt.height(Math.max(text.height(), icon.height()));\r\n
                body.height(parseInt(text_cnt.css("height")) + parseInt(footer.css("height")));\r\n
                window.setSize(text.position().left + text.width() + parseInt(text_cnt.css("padding-right")), parseInt(body.css("height")) + parseInt(header.css("height")));\r\n
            }\r\n
            function onBtnClick(event) {\r\n
                if (options.callback) {\r\n
                    options.callback.call(win, event.currentTarget.attributes["result"].value);\r\n
                }\r\n
                win.close(true);\r\n
            }\r\n
            function onKeyDown(event) {\r\n
                onBtnClick({\r\n
                    currentTarget: win.getChild(".footer .dlg-btn")[0]\r\n
                });\r\n
                return false;\r\n
            }\r\n
            win.on({\r\n
                "render:after": function (obj) {\r\n
                    autoSize(obj);\r\n
                },\r\n
                show: function (obj) {\r\n
                    obj.getChild(".footer .dlg-btn").focus();\r\n
                    obj.getChild(".footer .dlg-btn").on("click", onBtnClick);\r\n
                },\r\n
                close: function () {\r\n
                    options.callback && options.callback.call(win, "close");\r\n
                }\r\n
            });\r\n
            win.show();\r\n
        };\r\n
        Common.UI.warning = function (options) {\r\n
            options = options || {}; ! options.title && (options.title = this.Window.prototype.textWarning);\r\n
            Common.UI.alert(_.extend(options, {\r\n
                iconCls: "warn"\r\n
            }));\r\n
        };\r\n
        Common.UI.error = function (options) {\r\n
            options = options || {}; ! options.title && (options.title = this.Window.prototype.textError);\r\n
            Common.UI.alert(_.extend(options, {\r\n
                iconCls: "error"\r\n
            }));\r\n
        };\r\n
        Common.UI.confirm = function (options) {\r\n
            options = options || {}; ! options.title && (options.title = this.Window.prototype.textConfirmation);\r\n
            Common.UI.alert(_.extend(options, {\r\n
                iconCls: "confirm"\r\n
            }));\r\n
        };\r\n
        Common.UI.info = function (options) {\r\n
            options = options || {}; ! options.title && (options.title = this.Window.prototype.textInformation);\r\n
            Common.UI.alert(_.extend(options, {\r\n
                iconCls: "info"\r\n
            }));\r\n
        };\r\n
        return {\r\n
            $window: undefined,\r\n
            $lastmodal: undefined,\r\n
            dragging: {\r\n
                enabled: false\r\n
            },\r\n
            initialize: function (options) {\r\n
                this.initConfig = {};\r\n
                this.binding = {};\r\n
                _.extend(this.initConfig, config, options || {}); ! this.initConfig.id && (this.initConfig.id = "window-" + this.cid); ! this.initConfig.tpl && (this.initConfig.tpl = "");\r\n
                Common.UI.BaseView.prototype.initialize.call(this, this.initConfig);\r\n
            },\r\n
            render: function () {\r\n
                var renderto = this.initConfig.renderTo || document.body;\r\n
                $(renderto).append(_.template(template, this.initConfig));\r\n
                this.$window = $("#" + this.initConfig.id);\r\n
                this.binding.keydown = _.bind(_keydown, this);\r\n
                if (this.initConfig.header) {\r\n
                    this.binding.drag = _.bind(_mousemove, this);\r\n
                    this.binding.dragStop = _.bind(_mouseup, this);\r\n
                    this.binding.dragStart = _.bind(_dragstart, this);\r\n
                    var doclose = function () {\r\n
                        if (this.$window.find(".tool.close").hasClass("disabled")) {\r\n
                            return;\r\n
                        }\r\n
                        if (this.initConfig.toolcallback) {\r\n
                            this.initConfig.toolcallback.call(this);\r\n
                        } else {\r\n
                            (this.initConfig.toolclose == "hide") ? this.hide() : this.close();\r\n
                        }\r\n
                    };\r\n
                    this.$window.find(".header").on("mousedown", this.binding.dragStart);\r\n
                    this.$window.find(".tool.close").on("click", _.bind(doclose, this));\r\n
                } else {\r\n
                    this.$window.find(".body").css({\r\n
                        top: 0,\r\n
                        "border-radius": "5px"\r\n
                    });\r\n
                }\r\n
                if (this.initConfig.height == "auto") {\r\n
                    var height = parseInt(this.$window.find("> .body").css("height"));\r\n
                    this.initConfig.header && (height += parseInt(this.$window.find("> .header").css("height")));\r\n
                    this.$window.height(height);\r\n
                } else {\r\n
                    this.$window.css("height", this.initConfig.height);\r\n
                }\r\n
                this.fireEvent("render:after", this);\r\n
                return this;\r\n
            },\r\n
            show: function (x, y) {\r\n
                if (this.initConfig.modal) {\r\n
                    var mask = _getMask();\r\n
                    if (this.options.animate !== false) {\r\n
                        var opacity = mask.css("opacity");\r\n
                        mask.css("opacity", 0);\r\n
                        mask.show();\r\n
                        setTimeout(function () {\r\n
                            mask.css(_getTransformation(opacity));\r\n
                        },\r\n
                        1);\r\n
                    } else {\r\n
                        mask.show();\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("modal:show", this);\r\n
                    this.$lastmodal = $(".asc-window.modal:not(.dethrone):visible").first().addClass("dethrone");\r\n
                }\r\n
                if (!this.$window) {\r\n
                    this.render();\r\n
                    if (_.isNumber(x) && _.isNumber(y)) {\r\n
                        this.$window.css("left", Math.floor(x));\r\n
                        this.$window.css("top", Math.floor(y));\r\n
                    } else {\r\n
                        _centre.call(this);\r\n
                    }\r\n
                } else {\r\n
                    if (!this.$window.is(":visible")) {\r\n
                        this.$window.show();\r\n
                    }\r\n
                }\r\n
                $(document).on("keydown." + this.cid, this.binding.keydown);\r\n
                var me = this;\r\n
                if (this.options.animate !== false) {\r\n
                    this.$window.css({\r\n
                        "-webkit-transform": "scale(0.8)",\r\n
                        "-moz-transform": "scale(0.8)",\r\n
                        "-ms-transform": "scale(0.8)",\r\n
                        "-o-transform": "scale(0.8)",\r\n
                        opacity: 0\r\n
                    });\r\n
                    setTimeout(function () {\r\n
                        me.$window.css({\r\n
                            "-webkit-transition": "0.3s opacity, 0.3s -webkit-transform",\r\n
                            "-webkit-transform": "scale(1)",\r\n
                            "-moz-transition": "0.3s opacity, 0.3s -moz-transform",\r\n
                            "-moz-transform": "scale(1)",\r\n
                            "-ms-transition": "0.3s opacity, 0.3s -ms-transform",\r\n
                            "-ms-transform": "scale(1)",\r\n
                            "-o-transition": "0.3s opacity, 0.3s -o-transform",\r\n
                            "-o-transform": "scale(1)",\r\n
                            "opacity": "1"\r\n
                        });\r\n
                    },\r\n
                    1);\r\n
                    setTimeout(function () {\r\n
                        me.$window.css({\r\n
                            "-webkit-transform": "",\r\n
                            "-moz-transform": "",\r\n
                            "-ms-transition": "",\r\n
                            "-ms-transform": "",\r\n
                            "-o-transform": ""\r\n
                        });\r\n
                        me.fireEvent("show", me);\r\n
                    },\r\n
                    350);\r\n
                } else {\r\n
                    this.fireEvent("show", this);\r\n
                }\r\n
                Common.NotificationCenter.trigger("window:show");\r\n
            },\r\n
            close: function (suppressevent) {\r\n
                $(document).off("keydown." + this.cid);\r\n
                if (this.initConfig.header) {\r\n
                    this.$window.find(".header").off("mousedown", this.binding.dragStart);\r\n
                }\r\n
                if (this.initConfig.modal) {\r\n
                    var hide_mask = true;\r\n
                    if (this.$lastmodal.size() > 0) {\r\n
                        this.$lastmodal.removeClass("dethrone");\r\n
                        hide_mask = !this.$lastmodal.hasClass("modal");\r\n
                    }\r\n
                    if (hide_mask) {\r\n
                        var mask = $(".modals-mask");\r\n
                        if (this.options.animate !== false) {\r\n
                            var opacity = mask.css("opacity");\r\n
                            mask.css(_getTransformation(0));\r\n
                            setTimeout(function () {\r\n
                                mask.css("opacity", opacity);\r\n
                                mask.hide();\r\n
                            },\r\n
                            300);\r\n
                        } else {\r\n
                            mask.hide();\r\n
                        }\r\n
                    }\r\n
                    Common.NotificationCenter.trigger("modal:close", this);\r\n
                }\r\n
                this.$window.remove();\r\n
                suppressevent !== true && this.fireEvent("close", this);\r\n
            },\r\n
            hide: function () {\r\n
                $(document).off("keydown." + this.cid);\r\n
                if (this.$window) {\r\n
                    if (this.initConfig.modal) {\r\n
                        var hide_mask = true;\r\n
                        if (this.$lastmodal.size() > 0) {\r\n
                            this.$lastmodal.removeClass("dethrone");\r\n
                            hide_mask = !this.$lastmodal.hasClass("modal");\r\n
                        }\r\n
                        if (hide_mask) {\r\n
                            var mask = $(".modals-mask");\r\n
                            if (this.options.animate !== false) {\r\n
                                var opacity = mask.css("opacity");\r\n
                                mask.css(_getTransformation(0));\r\n
                                setTimeout(function () {\r\n
                                    mask.css("opacity", opacity);\r\n
                                    mask.hide();\r\n
                                },\r\n
                                300);\r\n
                            } else {\r\n
                                mask.hide();\r\n
                            }\r\n
                        }\r\n
                        Common.NotificationCenter.trigger("modal:hide", this);\r\n
                    }\r\n
                    this.$window.hide();\r\n
                    this.fireEvent("hide", this);\r\n
                }\r\n
            },\r\n
            isLocked: function () {\r\n
                return this.$window.hasClass("dethrone") || (!this.options.modal && this.$window.parent().find(".asc-window.modal:visible").length);\r\n
            },\r\n
            getChild: function (selector) {\r\n
                return selector ? this.$window.find(selector) : this.$window;\r\n
            },\r\n
            setWidth: function (width) {\r\n
                if (width >= 0) {\r\n
                    var min = parseInt(this.$window.css("min-width"));\r\n
                    width < min && (width = min);\r\n
                    this.$window.width(width);\r\n
                }\r\n
            },\r\n
            getWidth: function () {\r\n
                return parseInt(this.$window.css("width"));\r\n
            },\r\n
            setHeight: function (height) {\r\n
                if (height >= 0) {\r\n
                    var min = parseInt(this.$window.css("min-height"));\r\n
                    height < min && (height = min);\r\n
                    this.$window.height(height);\r\n
                    if (this.initConfig.header) {\r\n
                        height -= parseInt(this.$window.find("> .header").css("height"));\r\n
                    }\r\n
                    this.$window.find("> .body").css("height", height);\r\n
                }\r\n
            },\r\n
            getHeight: function () {\r\n
                return parseInt(this.$window.css("height"));\r\n
            },\r\n
            setSize: function (w, h) {\r\n
                this.setWidth(w);\r\n
                this.setHeight(h);\r\n
            },\r\n
            getSize: function () {\r\n
                return [this.getWidth(), this.getHeight()];\r\n
            },\r\n
            setTitle: function (title) {\r\n
                this.$window.find("> .header > .title").text(title);\r\n
            },\r\n
            getTitle: function () {\r\n
                return this.$window.find("> .header > .title").text();\r\n
            },\r\n
            isVisible: function () {\r\n
                return this.$window && this.$window.is(":visible");\r\n
            },\r\n
            onPrimary: function () {},\r\n
            cancelButtonText: "Cancel",\r\n
            okButtonText: "OK",\r\n
            yesButtonText: "Yes",\r\n
            noButtonText: "No",\r\n
            closeButtonText: "Close",\r\n
            textWarning: "Warning",\r\n
            textError: "Error",\r\n
            textConfirmation: "Confirmation",\r\n
            textInformation: "Information"\r\n
        };\r\n
    })(), Common.UI.Window || {}));\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>22226</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
