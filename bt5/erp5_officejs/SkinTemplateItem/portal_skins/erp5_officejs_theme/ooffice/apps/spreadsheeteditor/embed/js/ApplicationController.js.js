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
            <value> <string>ts44308423.35</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ApplicationController.js</string> </value>
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
 var ApplicationController = new(function () {\r\n
    var me, api, config = {},\r\n
    docConfig = {},\r\n
    embedConfig = {},\r\n
    permissions = {},\r\n
    maxPages = 0,\r\n
    minToolbarWidth = 550,\r\n
    minEmbedWidth = 400,\r\n
    minEmbedHeight = 600,\r\n
    embedCode = \'<iframe allowtransparency="true" frameborder="0" scrolling="no" src="{embed-url}" width="{width}" height="{height}"></iframe>\',\r\n
    maxZIndex = 9090,\r\n
    created = false;\r\n
    Common.Analytics.initialize("UA-12442749-13", "Embedded ONLYOFFICE Spreadsheet");\r\n
    if (typeof isBrowserSupported !== "undefined" && !isBrowserSupported()) {\r\n
        Common.Gateway.reportError(undefined, "Your browser is not supported.");\r\n
        return;\r\n
    }\r\n
    ZeroClipboard.setMoviePath("../../../vendor/ZeroClipboard/ZeroClipboard10.swf");\r\n
    var clipShortUrl = new ZeroClipboard.Client();\r\n
    var clipEmbedObj = new ZeroClipboard.Client();\r\n
    clipShortUrl.zIndex = maxZIndex;\r\n
    clipEmbedObj.zIndex = maxZIndex;\r\n
    function emptyFn() {}\r\n
    function createBuffered(fn, buffer, scope, args) {\r\n
        return function () {\r\n
            var timerId;\r\n
            return function () {\r\n
                var me = this;\r\n
                if (timerId) {\r\n
                    clearTimeout(timerId);\r\n
                    timerId = null;\r\n
                }\r\n
                timerId = setTimeout(function () {\r\n
                    fn.apply(scope || me, args || arguments);\r\n
                },\r\n
                buffer);\r\n
            };\r\n
        } ();\r\n
    }\r\n
    function updateSocial() {\r\n
        var $socialPanel = $("#id-popover-social-container");\r\n
        if ($socialPanel.length > 0) {\r\n
            if ($socialPanel.attr("data-loaded") == "false") {\r\n
                typeof FB !== "undefined" && FB.XFBML && FB.XFBML.parse();\r\n
                typeof twttr !== "undefined" && twttr.widgets && twttr.widgets.load();\r\n
                $socialPanel.attr("data-loaded", "true");\r\n
            }\r\n
        }\r\n
    }\r\n
    function loadConfig(data) {\r\n
        config = $.extend(config, data.config);\r\n
        embedConfig = $.extend(embedConfig, data.config.embedded);\r\n
        $("#id-short-url").val(embedConfig.shareUrl || "Unavailable");\r\n
        $("#id-textarea-embed").text(embedCode.replace("{embed-url}", embedConfig.embedUrl).replace("{width}", minEmbedWidth).replace("{height}", minEmbedHeight));\r\n
        if (typeof embedConfig.shareUrl !== "undefined" && embedConfig.shareUrl != "") {\r\n
            if ($("#id-popover-social-container ul")) {\r\n
                $("#id-popover-social-container ul").append(\'<li><div class="fb-like" data-href="\' + embedConfig.shareUrl + \'" data-send="false" data-layout="button_count" data-width="450" data-show-faces="false"></div></li>\');\r\n
                $("#id-popover-social-container ul").append(\'<li class="share-twitter"><a href="https://twitter.com/share" class="twitter-share-button" data-url="\' + embedConfig.shareUrl + \'">Tweet</a></li>\');\r\n
                $("#id-popover-social-container ul").append(\'<li class="share-mail"><a class="btn btn-xs btn-default" href="mailto:?subject=I have shared a document with you: \' + embedConfig.docTitle + "&body=I have shared a document with you: " + encodeURIComponent(embedConfig.shareUrl) + \'"><span class="glyphicon glyphicon-envelope">Email</a></li>\');\r\n
            }\r\n
        }\r\n
        if (typeof embedConfig.shareUrl === "undefined") {\r\n
            $("#id-btn-share").hide();\r\n
        }\r\n
        if (typeof embedConfig.embedUrl === "undefined") {\r\n
            $("#id-btn-embed").hide();\r\n
        }\r\n
        if (typeof embedConfig.fullscreenUrl === "undefined") {\r\n
            $("#id-btn-fullscreen").hide();\r\n
        }\r\n
        if (typeof config.canBackToFolder === "undefined" || !config.canBackToFolder) {\r\n
            $("#id-btn-close").hide();\r\n
        }\r\n
        if (embedConfig.toolbarDocked === "top") {\r\n
            $("#toolbar").addClass("top");\r\n
            $(".viewer").addClass("top");\r\n
        } else {\r\n
            $("#toolbar").addClass("bottom");\r\n
            $(".viewer").addClass("bottom");\r\n
        }\r\n
    }\r\n
    function loadDocument(data) {\r\n
        docConfig = data.doc;\r\n
        if (docConfig) {\r\n
            permissions = $.extend(permissions, docConfig.permissions);\r\n
            var docInfo = {};\r\n
            docInfo.Id = docConfig.key;\r\n
            docInfo.Url = docConfig.url;\r\n
            docInfo.Data = docConfig.data;\r\n
            docInfo.Title = docConfig.title;\r\n
            docInfo.Format = docConfig.fileType;\r\n
            docInfo.VKey = docConfig.vkey;\r\n
            docInfo.Origin = docConfig.origin;\r\n
            if (api) {\r\n
                api.asc_registerCallback("asc_onGetEditorPermissions", onEditorPermissions);\r\n
                api.asc_getEditorPermissions();\r\n
                api.asc_enableKeyEvents(true);\r\n
                api.asc_setViewerMode(true);\r\n
                api.asc_LoadDocument(docInfo);\r\n
                Common.Analytics.trackEvent("Load", "Start");\r\n
            }\r\n
            if (docConfig.title && !embedConfig.docTitle) {\r\n
                var el = $("#id-popover-social-container ul .share-mail > a");\r\n
                if (el.length) {\r\n
                    el.attr("href", el.attr("href").replace(/:\\sundefined&/, ": " + docConfig.title + "&"));\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function onSheetsChanged() {\r\n
        if (api) {\r\n
            maxPages = api.asc_getWorksheetsCount();\r\n
            var setActiveWorkSheet = function (index) {\r\n
                $.each($("#worksheets").children("li"), function () {\r\n
                    $(this).removeClass("active");\r\n
                });\r\n
                $("#worksheet-" + index).addClass("active");\r\n
                api.asc_showWorksheet(index);\r\n
            };\r\n
            var handleWorksheet = function (e) {\r\n
                var $worksheet = $(this);\r\n
                var index = $worksheet.attr("id").match(/\\d+/);\r\n
                if (index.length > 0) {\r\n
                    index = parseInt(index[0]);\r\n
                    if (index > -1 && index < maxPages) {\r\n
                        setActiveWorkSheet(index);\r\n
                    }\r\n
                }\r\n
            };\r\n
            $.each($("#worksheets").children("li"), function () {\r\n
                $(this).unbind("click");\r\n
                $(this).remove();\r\n
            });\r\n
            for (var i = 0; i < maxPages; i++) {\r\n
                $("#worksheets").append(\'<li id="worksheet-\' + i + \'">\' + api.asc_getWorksheetName(i).replace(/\\s/g, "&nbsp;") + "</li>");\r\n
                var $worksheet = $("#worksheet-" + i);\r\n
                $worksheet && $worksheet.bind("click", handleWorksheet);\r\n
            }\r\n
            setActiveWorkSheet(api.asc_getActiveWorksheetIndex());\r\n
        }\r\n
    }\r\n
    function onHyperlinkClick(url) {\r\n
        if (url) {\r\n
            var newDocumentPage = window.open(url, "_blank");\r\n
            if (newDocumentPage) {\r\n
                newDocumentPage.focus();\r\n
            }\r\n
        }\r\n
    }\r\n
    function hidePreloader() {\r\n
        $("#loading-mask").fadeOut("slow");\r\n
    }\r\n
    function onDocumentContentReady() {\r\n
        setVisiblePopover($("#id-popover-share"), false);\r\n
        setVisiblePopover($("#id-popover-embed"), false);\r\n
        handlerToolbarSize();\r\n
        hidePreloader();\r\n
        Common.Analytics.trackEvent("Load", "Complete");\r\n
    }\r\n
    function onEditorPermissions(params) {\r\n
        if (params.asc_getCanBranding() && (typeof config.customization == "object") && config.customization && config.customization.logo) {\r\n
            var logo = $("#header-logo");\r\n
            if (config.customization.logo.imageEmbedded) {\r\n
                logo.css({\r\n
                    "background-image": \'url("\' + config.customization.logo.imageEmbedded + \'")\',\r\n
                    "background-position": "0 center",\r\n
                    "background-repeat": "no-repeat"\r\n
                });\r\n
            }\r\n
            if (config.customization.logo.url) {\r\n
                logo.attr("href", config.customization.logo.url);\r\n
            }\r\n
        }\r\n
    }\r\n
    function showMask() {\r\n
        $("#id-loadmask").modal({\r\n
            backdrop: "static",\r\n
            keyboard: false\r\n
        });\r\n
    }\r\n
    function hideMask() {\r\n
        $("#id-loadmask").modal("hide");\r\n
    }\r\n
    function onOpenDocument(progress) {\r\n
        var proc = (progress.CurrentFont + progress.CurrentImage) / (progress.FontsCount + progress.ImagesCount);\r\n
        $("#loadmask-text").html("LOADING DOCUMENT: " + Math.round(proc * 100) + "%");\r\n
    }\r\n
    function onLongActionBegin(type, id) {\r\n
        var text = "";\r\n
        switch (id) {\r\n
        case c_oAscAsyncAction["Print"]:\r\n
            text = "Downloading document...";\r\n
            break;\r\n
        default:\r\n
            text = "Please wait...";\r\n
            break;\r\n
        }\r\n
        if (type == c_oAscAsyncActionType["BlockInteraction"]) {\r\n
            $("#id-loadmask .cmd-loader-title").html(text);\r\n
            showMask();\r\n
        }\r\n
    }\r\n
    function onLongActionEnd(type, id) {\r\n
        if (type === c_oAscAsyncActionType.BlockInteraction) {\r\n
            switch (id) {\r\n
            case c_oAscAsyncAction.Open:\r\n
                if (api) {\r\n
                    api.asc_Resize();\r\n
                }\r\n
                onDocumentContentReady();\r\n
                onSheetsChanged();\r\n
                break;\r\n
            }\r\n
            hideMask();\r\n
        }\r\n
    }\r\n
    function onError(id, level, errData) {\r\n
        hidePreloader();\r\n
        var message;\r\n
        switch (id) {\r\n
        case c_oAscError.ID.Unknown:\r\n
            message = me.unknownErrorText;\r\n
            break;\r\n
        case c_oAscError.ID.ConvertationTimeout:\r\n
            message = me.convertationTimeoutText;\r\n
            break;\r\n
        case c_oAscError.ID.ConvertationError:\r\n
            message = me.convertationErrorText;\r\n
            break;\r\n
        case c_oAscError.ID.DownloadError:\r\n
            message = me.downloadErrorText;\r\n
            break;\r\n
        default:\r\n
            message = me.errorDefaultMessage.replace("%1", id);\r\n
            break;\r\n
        }\r\n
        if (level == c_oAscError.Level.Critical) {\r\n
            Common.Gateway.reportError(id, message);\r\n
            $("#id-critical-error-title").text(me.criticalErrorTitle);\r\n
            $("#id-critical-error-message").text(message);\r\n
            $("#id-critical-error-close").off();\r\n
            $("#id-critical-error-close").on("click", function () {\r\n
                window.location.reload();\r\n
            });\r\n
        } else {\r\n
            $("#id-critical-error-title").text(me.notcriticalErrorTitle);\r\n
            $("#id-critical-error-message").text(message);\r\n
            $("#id-critical-error-close").off();\r\n
            $("#id-critical-error-close").on("click", function () {\r\n
                $("#id-critical-error-dialog").modal("hide");\r\n
            });\r\n
        }\r\n
        $("#id-critical-error-dialog").modal("show");\r\n
        Common.Analytics.trackEvent("Internal Error", id.toString());\r\n
    }\r\n
    function onExternalError(error) {\r\n
        if (error) {\r\n
            hidePreloader();\r\n
            $("#id-error-mask-title").text(error.title);\r\n
            $("#id-error-mask-text").text(error.msg);\r\n
            $("#id-error-mask").css("display", "block");\r\n
            Common.Analytics.trackEvent("External Error", error.title);\r\n
        }\r\n
    }\r\n
    var handlerToolbarSize = createBuffered(function (size) {\r\n
        var visibleCaption = function (btn, visible) {\r\n
            if (visible) {\r\n
                $(btn + " button").addClass("no-caption");\r\n
                $(btn + " button span").css("display", "none");\r\n
            } else {\r\n
                $(btn + " button").removeClass("no-caption");\r\n
                $(btn + " button span").css("display", "inline");\r\n
            }\r\n
        };\r\n
        var isMinimize = $("#toolbar").width() < minToolbarWidth;\r\n
        visibleCaption("#id-btn-copy", isMinimize);\r\n
        visibleCaption("#id-btn-share", isMinimize);\r\n
        visibleCaption("#id-btn-embed", isMinimize);\r\n
    },\r\n
    10);\r\n
    function onDocumentResize() {\r\n
        if (api) {\r\n
            api.asc_Resize();\r\n
        }\r\n
        handlerToolbarSize();\r\n
    }\r\n
    function isVisiblePopover(popover) {\r\n
        return popover.hasClass("in");\r\n
    }\r\n
    function setVisiblePopover(popover, visible, owner) {\r\n
        api && api.asc_enableKeyEvents(!visible);\r\n
        if (visible) {\r\n
            if (owner) {\r\n
                popover.css("display", "block");\r\n
                var popoverData = owner.data("bs.popover"),\r\n
                $tip = popoverData.tip(),\r\n
                pos = popoverData.getPosition(false),\r\n
                actualHeight = $tip[0].offsetHeight,\r\n
                placement = (embedConfig.toolbarDocked === "top") ? "bottom" : "top",\r\n
                tp;\r\n
                $tip.removeClass("fade in top bottom left right");\r\n
                switch (placement) {\r\n
                case "bottom":\r\n
                    tp = {\r\n
                        top: pos.top + pos.height,\r\n
                        left: owner.position().left + (owner.width() - popover.width()) * 0.5\r\n
                    };\r\n
                    break;\r\n
                default:\r\n
                    case "top":\r\n
                    tp = {\r\n
                        top: pos.top - actualHeight,\r\n
                        left: owner.position().left + (owner.width() - popover.width()) * 0.5\r\n
                    };\r\n
                    break;\r\n
                }\r\n
                $tip.css(tp).addClass(placement).addClass("in");\r\n
            }\r\n
            if (popover.hasClass("embed")) {\r\n
                clipEmbedObj.show();\r\n
            }\r\n
            if (popover.hasClass("share")) {\r\n
                clipShortUrl.show();\r\n
                updateSocial();\r\n
            }\r\n
        } else {\r\n
            popover.removeClass("in");\r\n
            popover.css("display", "none");\r\n
            popover.hasClass("embed") && clipEmbedObj.hide();\r\n
            popover.hasClass("share") && clipShortUrl.hide();\r\n
        }\r\n
    }\r\n
    function updateEmbedCode() {\r\n
        var newWidth = parseInt($("#id-input-embed-width").val()),\r\n
        newHeight = parseInt($("#id-input-embed-height").val());\r\n
        if (newWidth < minEmbedWidth) {\r\n
            newWidth = minEmbedWidth;\r\n
        }\r\n
        if (newHeight < minEmbedHeight) {\r\n
            newHeight = minEmbedHeight;\r\n
        }\r\n
        $("#id-textarea-embed").text(embedCode.replace("{embed-url}", embedConfig.embedUrl).replace("{width}", newWidth).replace("{height}", newHeight));\r\n
        $("#id-input-embed-width").val(newWidth + "px");\r\n
        $("#id-input-embed-height").val(newHeight + "px");\r\n
    }\r\n
    function openLink(url) {\r\n
        var newDocumentPage = window.open(url);\r\n
        if (newDocumentPage) {\r\n
            newDocumentPage.focus();\r\n
        }\r\n
    }\r\n
    function createController() {\r\n
        if (created) {\r\n
            return me;\r\n
        }\r\n
        me = this;\r\n
        created = true;\r\n
        var documentMoveTimer;\r\n
        clipShortUrl.addEventListener("mousedown", function () {\r\n
            if ($("#id-btn-copy-short").hasClass("copied")) {\r\n
                return;\r\n
            }\r\n
            $("#id-btn-copy-short").button("copied");\r\n
            $("#id-btn-copy-short").addClass("copied");\r\n
            clipShortUrl.setText($("#id-short-url").val());\r\n
            setTimeout(function () {\r\n
                $("#id-btn-copy-short").button("reset");\r\n
                $("#id-btn-copy-short").removeClass("copied");\r\n
            },\r\n
            2000);\r\n
        });\r\n
        clipEmbedObj.addEventListener("mousedown", function () {\r\n
            if ($("#id-btn-copy-embed").hasClass("copied")) {\r\n
                return;\r\n
            }\r\n
            $("#id-btn-copy-embed").button("copied");\r\n
            $("#id-btn-copy-embed").addClass("copied");\r\n
            clipEmbedObj.setText($("#id-textarea-embed").text());\r\n
            setTimeout(function () {\r\n
                $("#id-btn-copy-embed").button("reset");\r\n
                $("#id-btn-copy-embed").removeClass("copied");\r\n
            },\r\n
            2000);\r\n
        });\r\n
        clipShortUrl.glue("id-btn-copy-short");\r\n
        clipEmbedObj.glue("id-btn-copy-embed");\r\n
        $("#id-btn-copy").on("click", function () {\r\n
            var saveUrl = embedConfig.saveUrl;\r\n
            if (typeof saveUrl !== "undefined" && saveUrl.length > 0) {\r\n
                openLink(saveUrl);\r\n
            } else {\r\n
                if (api) {\r\n
                    api.asc_Print();\r\n
                }\r\n
            }\r\n
            Common.Analytics.trackEvent("Save");\r\n
        });\r\n
        $("#id-btn-share").on("click", function (event) {\r\n
            setVisiblePopover($("#id-popover-share"), !isVisiblePopover($("#id-popover-share")), $("#id-btn-share"));\r\n
            setVisiblePopover($("#id-popover-embed"), false);\r\n
            event.preventDefault();\r\n
            event.stopPropagation();\r\n
        });\r\n
        $("#id-btn-embed").on("click", function (event) {\r\n
            setVisiblePopover($("#id-popover-embed"), !isVisiblePopover($("#id-popover-embed")), $("#id-btn-embed"));\r\n
            setVisiblePopover($("#id-popover-share"), false);\r\n
            event.preventDefault();\r\n
            event.stopPropagation();\r\n
        });\r\n
        $("#id-input-embed-width").on("keypress", function (e) {\r\n
            if (e.keyCode == 13) {\r\n
                updateEmbedCode();\r\n
            }\r\n
        });\r\n
        $("#id-input-embed-height").on("keypress", function (e) {\r\n
            if (e.keyCode == 13) {\r\n
                updateEmbedCode();\r\n
            }\r\n
        });\r\n
        $("#id-input-embed-width").on("focusin", function (e) {\r\n
            api && api.asc_enableKeyEvents(false);\r\n
        });\r\n
        $("#id-input-embed-height").on("focusin", function (e) {\r\n
            api && api.asc_enableKeyEvents(false);\r\n
        });\r\n
        $("#id-input-embed-width").on("focusout", function (e) {\r\n
            updateEmbedCode();\r\n
            api && api.asc_enableKeyEvents(true);\r\n
        });\r\n
        $("#id-input-embed-height").on("focusout", function (e) {\r\n
            updateEmbedCode();\r\n
            api && api.asc_enableKeyEvents(true);\r\n
        });\r\n
        $("#id-btn-fullscreen").on("click", function () {\r\n
            openLink(embedConfig.fullscreenUrl);\r\n
        });\r\n
        $("#id-btn-close").on("click", function () {\r\n
            Common.Gateway.goBack();\r\n
        });\r\n
        $("#id-btn-zoom-in").on("click", function () {\r\n
            if (api) {\r\n
                var f = api.asc_getZoom() + 0.1;\r\n
                f > 0 && !(f > 2) && api.asc_setZoom(f);\r\n
            }\r\n
        });\r\n
        $("#id-btn-zoom-out").on("click", function () {\r\n
            if (api) {\r\n
                var f = api.asc_getZoom() - 0.1; ! (f < 0.5) && api.asc_setZoom(f);\r\n
            }\r\n
        });\r\n
        $(window).resize(function () {\r\n
            onDocumentResize();\r\n
        });\r\n
        $(document).click(function (event) {\r\n
            if (event && event.target && $(event.target).closest(".popover").length > 0) {\r\n
                return;\r\n
            }\r\n
            setVisiblePopover($("#id-popover-share"), false);\r\n
            setVisiblePopover($("#id-popover-embed"), false);\r\n
        });\r\n
        $(document).mousemove(function (event) {\r\n
            $("#id-btn-zoom-in").fadeIn();\r\n
            $("#id-btn-zoom-out").fadeIn();\r\n
            clearTimeout(documentMoveTimer);\r\n
            documentMoveTimer = setTimeout(function () {\r\n
                $("#id-btn-zoom-in").fadeOut();\r\n
                $("#id-btn-zoom-out").fadeOut();\r\n
            },\r\n
            2000);\r\n
        });\r\n
        api = new Asc.spreadsheet_api("editor_sdk");\r\n
        if (api) {\r\n
            api.asc_Init("../../../sdk/Fonts/");\r\n
            api.asc_registerCallback("asc_onStartAction", onLongActionBegin);\r\n
            api.asc_registerCallback("asc_onEndAction", onLongActionEnd);\r\n
            api.asc_registerCallback("asc_onError", onError);\r\n
            api.asc_registerCallback("asc_onOpenDocumentProgress", onOpenDocument);\r\n
            api.asc_registerCallback("asc_onSheetsChanged", onSheetsChanged);\r\n
            api.asc_registerCallback("asc_onHyperlinkClick", onHyperlinkClick);\r\n
            Common.Gateway.on("init", loadConfig);\r\n
            Common.Gateway.on("opendocument", loadDocument);\r\n
            Common.Gateway.on("showerror", onExternalError);\r\n
            Common.Gateway.ready();\r\n
        }\r\n
        return me;\r\n
    }\r\n
    return {\r\n
        create: createController,\r\n
        errorDefaultMessage: "Error code: %1",\r\n
        unknownErrorText: "Unknown error.",\r\n
        convertationTimeoutText: "Convertation timeout exceeded.",\r\n
        convertationErrorText: "Convertation failed.",\r\n
        downloadErrorText: "Download failed.",\r\n
        criticalErrorTitle: "Error",\r\n
        notcriticalErrorTitle: "Warning"\r\n
    };\r\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>22425</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
