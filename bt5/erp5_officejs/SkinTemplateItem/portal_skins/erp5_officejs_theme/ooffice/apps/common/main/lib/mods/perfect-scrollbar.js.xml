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
            <value> <string>ts44308803.28</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>perfect-scrollbar.js</string> </value>
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
 (function (factory) {\r\n
    if (typeof define === "function" && define.amd) {\r\n
        define(["jquery"], factory);\r\n
    } else {\r\n
        if (typeof exports === "object") {\r\n
            factory(require("jquery"));\r\n
        } else {\r\n
            factory(jQuery);\r\n
        }\r\n
    }\r\n
} (function ($) {\r\n
    var defaultSettings = {\r\n
        wheelSpeed: 10,\r\n
        wheelPropagation: false,\r\n
        minScrollbarLength: null,\r\n
        useBothWheelAxes: false,\r\n
        useKeyboard: true,\r\n
        suppressScrollX: false,\r\n
        suppressScrollY: false,\r\n
        scrollXMarginOffset: 0,\r\n
        scrollYMarginOffset: 0,\r\n
        includePadding: false,\r\n
        includeMargin: true\r\n
    };\r\n
    var getEventClassName = (function () {\r\n
        var incrementingId = 0;\r\n
        return function () {\r\n
            var id = incrementingId;\r\n
            incrementingId += 1;\r\n
            return ".perfect-scrollbar-" + id;\r\n
        };\r\n
    } ());\r\n
    $.fn.perfectScrollbar = function (suppliedSettings, option) {\r\n
        return this.each(function () {\r\n
            var settings = $.extend(true, {},\r\n
            defaultSettings),\r\n
            $this = $(this);\r\n
            if (typeof suppliedSettings === "object") {\r\n
                $.extend(true, settings, suppliedSettings);\r\n
            } else {\r\n
                option = suppliedSettings;\r\n
            }\r\n
            if (option === "update") {\r\n
                if ($this.data("perfect-scrollbar-update")) {\r\n
                    $this.data("perfect-scrollbar-update")();\r\n
                }\r\n
                return $this;\r\n
            } else {\r\n
                if (option === "destroy") {\r\n
                    if ($this.data("perfect-scrollbar-destroy")) {\r\n
                        $this.data("perfect-scrollbar-destroy")();\r\n
                    }\r\n
                    return $this;\r\n
                }\r\n
            }\r\n
            if ($this.data("perfect-scrollbar")) {\r\n
                return $this.data("perfect-scrollbar");\r\n
            }\r\n
            $this.addClass("ps-container");\r\n
            var $scrollbarXRail = $("<div class=\'ps-scrollbar-x-rail\'></div>").appendTo($this),\r\n
            $scrollbarYRail = $("<div class=\'ps-scrollbar-y-rail\'></div>").appendTo($this),\r\n
            $scrollbarX = $("<div class=\'ps-scrollbar-x\'></div>").appendTo($scrollbarXRail),\r\n
            $scrollbarY = $("<div class=\'ps-scrollbar-y\'></div>").appendTo($scrollbarYRail),\r\n
            scrollbarXActive,\r\n
            scrollbarYActive,\r\n
            containerWidth,\r\n
            containerHeight,\r\n
            contentWidth,\r\n
            contentHeight,\r\n
            scrollbarXWidth,\r\n
            scrollbarXLeft,\r\n
            scrollbarXBottom = parseInt($scrollbarXRail.css("bottom"), 10),\r\n
            scrollbarYHeight,\r\n
            scrollbarYTop,\r\n
            scrollbarYRight = parseInt($scrollbarYRail.css("right"), 10),\r\n
            scrollbarYRailHeight,\r\n
            eventClassName = getEventClassName();\r\n
            var updateContentScrollTop = function (currentTop, deltaY) {\r\n
                var newTop = currentTop + deltaY,\r\n
                maxTop = scrollbarYRailHeight - scrollbarYHeight;\r\n
                if (newTop < 0) {\r\n
                    scrollbarYTop = 0;\r\n
                } else {\r\n
                    if (newTop > maxTop) {\r\n
                        scrollbarYTop = maxTop;\r\n
                    } else {\r\n
                        scrollbarYTop = newTop;\r\n
                    }\r\n
                }\r\n
                var scrollTop = parseInt(scrollbarYTop * (contentHeight - containerHeight) / (scrollbarYRailHeight - scrollbarYHeight), 10);\r\n
                $this.scrollTop(scrollTop);\r\n
                $scrollbarXRail.css({\r\n
                    bottom: scrollbarXBottom - scrollTop\r\n
                });\r\n
            };\r\n
            var updateContentScrollLeft = function (currentLeft, deltaX) {\r\n
                var newLeft = currentLeft + deltaX,\r\n
                maxLeft = containerWidth - scrollbarXWidth;\r\n
                if (newLeft < 0) {\r\n
                    scrollbarXLeft = 0;\r\n
                } else {\r\n
                    if (newLeft > maxLeft) {\r\n
                        scrollbarXLeft = maxLeft;\r\n
                    } else {\r\n
                        scrollbarXLeft = newLeft;\r\n
                    }\r\n
                }\r\n
                var scrollLeft = parseInt(scrollbarXLeft * (contentWidth - containerWidth) / (containerWidth - scrollbarXWidth), 10);\r\n
                $this.scrollLeft(scrollLeft);\r\n
                $scrollbarYRail.css({\r\n
                    right: scrollbarYRight - scrollLeft\r\n
                });\r\n
            };\r\n
            var getSettingsAdjustedThumbSize = function (thumbSize) {\r\n
                if (settings.minScrollbarLength) {\r\n
                    thumbSize = Math.max(thumbSize, settings.minScrollbarLength);\r\n
                }\r\n
                return thumbSize;\r\n
            };\r\n
            var updateScrollbarCss = function () {\r\n
                $scrollbarXRail.css({\r\n
                    left: $this.scrollLeft(),\r\n
                    bottom: scrollbarXBottom - $this.scrollTop(),\r\n
                    width: containerWidth,\r\n
                    display: scrollbarXActive ? "inherit" : "none"\r\n
                });\r\n
                if ($scrollbarYRail.hasClass("in-scrolling")) {\r\n
                    $scrollbarYRail.css({\r\n
                        right: scrollbarYRight - $this.scrollLeft(),\r\n
                        height: scrollbarYRailHeight,\r\n
                        display: scrollbarYActive ? "inherit" : "none"\r\n
                    });\r\n
                } else {\r\n
                    $scrollbarYRail.css({\r\n
                        top: $this.scrollTop(),\r\n
                        right: scrollbarYRight - $this.scrollLeft(),\r\n
                        height: scrollbarYRailHeight,\r\n
                        display: scrollbarYActive ? "inherit" : "none"\r\n
                    });\r\n
                }\r\n
                $scrollbarX.css({\r\n
                    left: scrollbarXLeft,\r\n
                    width: scrollbarXWidth\r\n
                });\r\n
                $scrollbarY.css({\r\n
                    top: scrollbarYTop,\r\n
                    height: scrollbarYHeight\r\n
                });\r\n
            };\r\n
            var updateBarSizeAndPosition = function () {\r\n
                containerWidth = settings.includePadding ? $this.innerWidth() : $this.width();\r\n
                containerHeight = settings.includePadding ? $this.innerHeight() : $this.height();\r\n
                scrollbarYRailHeight = containerHeight - (settings.includeMargin ? (parseInt($scrollbarYRail.css("margin-top")) + parseInt($scrollbarYRail.css("margin-bottom"))) : 0);\r\n
                contentWidth = $this.prop("scrollWidth");\r\n
                contentHeight = $this.prop("scrollHeight");\r\n
                if (!settings.suppressScrollX && containerWidth + settings.scrollXMarginOffset < contentWidth) {\r\n
                    scrollbarXActive = true;\r\n
                    scrollbarXWidth = getSettingsAdjustedThumbSize(parseInt(containerWidth * containerWidth / contentWidth, 10));\r\n
                    scrollbarXLeft = parseInt($this.scrollLeft() * (containerWidth - scrollbarXWidth) / (contentWidth - containerWidth), 10);\r\n
                } else {\r\n
                    scrollbarXActive = false;\r\n
                    scrollbarXWidth = 0;\r\n
                    scrollbarXLeft = 0;\r\n
                    $this.scrollLeft(0);\r\n
                }\r\n
                if (!settings.suppressScrollY && containerHeight + settings.scrollYMarginOffset < contentHeight) {\r\n
                    scrollbarYActive = true;\r\n
                    scrollbarYHeight = getSettingsAdjustedThumbSize(parseInt(scrollbarYRailHeight * containerHeight / contentHeight, 10));\r\n
                    scrollbarYTop = parseInt($this.scrollTop() * (scrollbarYRailHeight - scrollbarYHeight) / (contentHeight - containerHeight), 10);\r\n
                } else {\r\n
                    scrollbarYActive = false;\r\n
                    scrollbarYHeight = 0;\r\n
                    scrollbarYTop = 0;\r\n
                    $this.scrollTop(0);\r\n
                }\r\n
                if (scrollbarYTop >= scrollbarYRailHeight - scrollbarYHeight) {\r\n
                    scrollbarYTop = scrollbarYRailHeight - scrollbarYHeight;\r\n
                }\r\n
                if (scrollbarXLeft >= containerWidth - scrollbarXWidth) {\r\n
                    scrollbarXLeft = containerWidth - scrollbarXWidth;\r\n
                }\r\n
                updateScrollbarCss();\r\n
                if (settings.onChange) {\r\n
                    settings.onChange(this);\r\n
                }\r\n
            };\r\n
            var bindMouseScrollXHandler = function () {\r\n
                var currentLeft, currentPageX;\r\n
                $scrollbarX.bind("mousedown" + eventClassName, function (e) {\r\n
                    currentPageX = e.pageX;\r\n
                    currentLeft = $scrollbarX.position().left;\r\n
                    $scrollbarXRail.addClass("in-scrolling");\r\n
                    e.stopPropagation();\r\n
                    e.preventDefault();\r\n
                });\r\n
                $(document).bind("mousemove" + eventClassName, function (e) {\r\n
                    if ($scrollbarXRail.hasClass("in-scrolling")) {\r\n
                        updateContentScrollLeft(currentLeft, e.pageX - currentPageX);\r\n
                        e.stopPropagation();\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
                $(document).bind("mouseup" + eventClassName, function (e) {\r\n
                    if ($scrollbarXRail.hasClass("in-scrolling")) {\r\n
                        $scrollbarXRail.removeClass("in-scrolling");\r\n
                    }\r\n
                });\r\n
                currentLeft = currentPageX = null;\r\n
            };\r\n
            var bindMouseScrollYHandler = function () {\r\n
                var currentTop, currentPageY;\r\n
                $scrollbarY.bind("mousedown" + eventClassName, function (e) {\r\n
                    currentPageY = e.pageY;\r\n
                    currentTop = $scrollbarY.position().top;\r\n
                    $scrollbarYRail.addClass("in-scrolling");\r\n
                    var margin = parseInt($scrollbarYRail.css("margin-top"));\r\n
                    var rect = $scrollbarYRail[0].getBoundingClientRect();\r\n
                    $scrollbarYRail.css({\r\n
                        position: "fixed",\r\n
                        left: rect.left,\r\n
                        top: rect.top - margin\r\n
                    });\r\n
                    e.stopPropagation();\r\n
                    e.preventDefault();\r\n
                });\r\n
                $(document).bind("mousemove" + eventClassName, function (e) {\r\n
                    if ($scrollbarYRail.hasClass("in-scrolling")) {\r\n
                        updateContentScrollTop(currentTop, e.pageY - currentPageY);\r\n
                        e.stopPropagation();\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
                $(document).bind("mouseup" + eventClassName, function (e) {\r\n
                    if ($scrollbarYRail.hasClass("in-scrolling")) {\r\n
                        $scrollbarYRail.removeClass("in-scrolling");\r\n
                        $scrollbarYRail.css({\r\n
                            position: "",\r\n
                            left: "",\r\n
                            top: ""\r\n
                        });\r\n
                        updateScrollbarCss();\r\n
                    }\r\n
                });\r\n
                currentTop = currentPageY = null;\r\n
            };\r\n
            var shouldPreventDefault = function (deltaX, deltaY) {\r\n
                var scrollTop = $this.scrollTop();\r\n
                if (deltaX === 0) {\r\n
                    if (!scrollbarYActive) {\r\n
                        return false;\r\n
                    }\r\n
                    if ((scrollTop === 0 && deltaY > 0) || (scrollTop >= contentHeight - containerHeight && deltaY < 0)) {\r\n
                        return !settings.wheelPropagation;\r\n
                    }\r\n
                }\r\n
                var scrollLeft = $this.scrollLeft();\r\n
                if (deltaY === 0) {\r\n
                    if (!scrollbarXActive) {\r\n
                        return false;\r\n
                    }\r\n
                    if ((scrollLeft === 0 && deltaX < 0) || (scrollLeft >= contentWidth - containerWidth && deltaX > 0)) {\r\n
                        return !settings.wheelPropagation;\r\n
                    }\r\n
                }\r\n
                return true;\r\n
            };\r\n
            var bindMouseWheelHandler = function () {\r\n
                settings.wheelSpeed /= 10;\r\n
                var shouldPrevent = false;\r\n
                $this.bind("mousewheel" + eventClassName, function (e, deprecatedDelta, deprecatedDeltaX, deprecatedDeltaY) {\r\n
                    var deltaX = e.deltaX * e.deltaFactor || deprecatedDeltaX,\r\n
                    deltaY = e.deltaY * e.deltaFactor || deprecatedDeltaY;\r\n
                    if (e && e.target && (e.target.type === "textarea" || e.target.type === "input")) {\r\n
                        e.stopImmediatePropagation();\r\n
                        e.preventDefault();\r\n
                        var scroll = $(e.target).scrollTop(),\r\n
                        wheelDeltaY = 0;\r\n
                        if (e.originalEvent) {\r\n
                            if (e.originalEvent.wheelDelta) {\r\n
                                wheelDeltaY = e.originalEvent.wheelDelta / -40;\r\n
                            }\r\n
                            if (e.originalEvent.deltaY) {\r\n
                                wheelDeltaY = e.originalEvent.deltaY;\r\n
                            }\r\n
                            if (e.originalEvent.detail) {\r\n
                                wheelDeltaY = e.originalEvent.detail;\r\n
                            }\r\n
                        }\r\n
                        $(e.target).scrollTop(scroll - wheelDeltaY);\r\n
                        return;\r\n
                    }\r\n
                    shouldPrevent = false;\r\n
                    if (!settings.useBothWheelAxes) {\r\n
                        $this.scrollTop($this.scrollTop() - (deltaY * settings.wheelSpeed));\r\n
                        $this.scrollLeft($this.scrollLeft() + (deltaX * settings.wheelSpeed));\r\n
                    } else {\r\n
                        if (scrollbarYActive && !scrollbarXActive) {\r\n
                            if (deltaY) {\r\n
                                $this.scrollTop($this.scrollTop() - (deltaY * settings.wheelSpeed));\r\n
                            } else {\r\n
                                $this.scrollTop($this.scrollTop() + (deltaX * settings.wheelSpeed));\r\n
                            }\r\n
                            shouldPrevent = true;\r\n
                        } else {\r\n
                            if (scrollbarXActive && !scrollbarYActive) {\r\n
                                if (deltaX) {\r\n
                                    $this.scrollLeft($this.scrollLeft() + (deltaX * settings.wheelSpeed));\r\n
                                } else {\r\n
                                    $this.scrollLeft($this.scrollLeft() - (deltaY * settings.wheelSpeed));\r\n
                                }\r\n
                                shouldPrevent = true;\r\n
                            }\r\n
                        }\r\n
                    }\r\n
                    updateBarSizeAndPosition();\r\n
                    shouldPrevent = (shouldPrevent || shouldPreventDefault(deltaX, deltaY));\r\n
                    if (shouldPrevent) {\r\n
                        e.stopPropagation();\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
                $this.bind("MozMousePixelScroll" + eventClassName, function (e) {\r\n
                    if (shouldPrevent) {\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
            };\r\n
            var bindKeyboardHandler = function () {\r\n
                var hovered = false;\r\n
                $this.bind("mouseenter" + eventClassName, function (e) {\r\n
                    hovered = true;\r\n
                });\r\n
                $this.bind("mouseleave" + eventClassName, function (e) {\r\n
                    hovered = false;\r\n
                });\r\n
                var shouldPrevent = false;\r\n
                $(document).bind("keydown" + eventClassName, function (e) {\r\n
                    if (!hovered || $(document.activeElement).is(":input,[contenteditable]")) {\r\n
                        return;\r\n
                    }\r\n
                    var deltaX = 0,\r\n
                    deltaY = 0;\r\n
                    switch (e.which) {\r\n
                    case 37:\r\n
                        deltaX = -30;\r\n
                        break;\r\n
                    case 38:\r\n
                        deltaY = 30;\r\n
                        break;\r\n
                    case 39:\r\n
                        deltaX = 30;\r\n
                        break;\r\n
                    case 40:\r\n
                        deltaY = -30;\r\n
                        break;\r\n
                    case 33:\r\n
                        deltaY = 90;\r\n
                        break;\r\n
                    case 32:\r\n
                        case 34:\r\n
                        deltaY = -90;\r\n
                        break;\r\n
                    case 35:\r\n
                        deltaY = -containerHeight;\r\n
                        break;\r\n
                    case 36:\r\n
                        deltaY = containerHeight;\r\n
                        break;\r\n
                    default:\r\n
                        return;\r\n
                    }\r\n
                    $this.scrollTop($this.scrollTop() - deltaY);\r\n
                    $this.scrollLeft($this.scrollLeft() + deltaX);\r\n
                    shouldPrevent = shouldPreventDefault(deltaX, deltaY);\r\n
                    if (shouldPrevent) {\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
            };\r\n
            var bindRailClickHandler = function () {\r\n
                var stopPropagation = function (e) {\r\n
                    e.stopPropagation();\r\n
                };\r\n
                $scrollbarY.bind("click" + eventClassName, stopPropagation);\r\n
                $scrollbarYRail.bind("click" + eventClassName, function (e) {\r\n
                    var halfOfScrollbarLength = parseInt(scrollbarYHeight / 2, 10),\r\n
                    positionTop = e.pageY - $scrollbarYRail.offset().top - halfOfScrollbarLength,\r\n
                    maxPositionTop = scrollbarYRailHeight - scrollbarYHeight,\r\n
                    positionRatio = positionTop / maxPositionTop;\r\n
                    if (positionRatio < 0) {\r\n
                        positionRatio = 0;\r\n
                    } else {\r\n
                        if (positionRatio > 1) {\r\n
                            positionRatio = 1;\r\n
                        }\r\n
                    }\r\n
                    $this.scrollTop((contentHeight - containerHeight) * positionRatio);\r\n
                });\r\n
                $scrollbarX.bind("click" + eventClassName, stopPropagation);\r\n
                $scrollbarXRail.bind("click" + eventClassName, function (e) {\r\n
                    var halfOfScrollbarLength = parseInt(scrollbarXWidth / 2, 10),\r\n
                    positionLeft = e.pageX - $scrollbarXRail.offset().left - halfOfScrollbarLength,\r\n
                    maxPositionLeft = containerWidth - scrollbarXWidth,\r\n
                    positionRatio = positionLeft / maxPositionLeft;\r\n
                    if (positionRatio < 0) {\r\n
                        positionRatio = 0;\r\n
                    } else {\r\n
                        if (positionRatio > 1) {\r\n
                            positionRatio = 1;\r\n
                        }\r\n
                    }\r\n
                    $this.scrollLeft((contentWidth - containerWidth) * positionRatio);\r\n
                });\r\n
            };\r\n
            var bindMobileTouchHandler = function () {\r\n
                var applyTouchMove = function (differenceX, differenceY) {\r\n
                    $this.scrollTop($this.scrollTop() - differenceY);\r\n
                    $this.scrollLeft($this.scrollLeft() - differenceX);\r\n
                    updateBarSizeAndPosition();\r\n
                };\r\n
                var startCoords = {},\r\n
                startTime = 0,\r\n
                speed = {},\r\n
                breakingProcess = null,\r\n
                inGlobalTouch = false;\r\n
                $(window).bind("touchstart" + eventClassName, function (e) {\r\n
                    inGlobalTouch = true;\r\n
                });\r\n
                $(window).bind("touchend" + eventClassName, function (e) {\r\n
                    inGlobalTouch = false;\r\n
                });\r\n
                $this.bind("touchstart" + eventClassName, function (e) {\r\n
                    var touch = e.originalEvent.targetTouches[0];\r\n
                    startCoords.pageX = touch.pageX;\r\n
                    startCoords.pageY = touch.pageY;\r\n
                    startTime = (new Date()).getTime();\r\n
                    if (breakingProcess !== null) {\r\n
                        clearInterval(breakingProcess);\r\n
                    }\r\n
                    e.stopPropagation();\r\n
                });\r\n
                $this.bind("touchmove" + eventClassName, function (e) {\r\n
                    if (!inGlobalTouch && e.originalEvent.targetTouches.length === 1) {\r\n
                        var touch = e.originalEvent.targetTouches[0];\r\n
                        var currentCoords = {};\r\n
                        currentCoords.pageX = touch.pageX;\r\n
                        currentCoords.pageY = touch.pageY;\r\n
                        var differenceX = currentCoords.pageX - startCoords.pageX,\r\n
                        differenceY = currentCoords.pageY - startCoords.pageY;\r\n
                        applyTouchMove(differenceX, differenceY);\r\n
                        startCoords = currentCoords;\r\n
                        var currentTime = (new Date()).getTime();\r\n
                        var timeGap = currentTime - startTime;\r\n
                        if (timeGap > 0) {\r\n
                            speed.x = differenceX / timeGap;\r\n
                            speed.y = differenceY / timeGap;\r\n
                            startTime = currentTime;\r\n
                        }\r\n
                        e.preventDefault();\r\n
                    }\r\n
                });\r\n
                $this.bind("touchend" + eventClassName, function (e) {\r\n
                    clearInterval(breakingProcess);\r\n
                    breakingProcess = setInterval(function () {\r\n
                        if (Math.abs(speed.x) < 0.01 && Math.abs(speed.y) < 0.01) {\r\n
                            clearInterval(breakingProcess);\r\n
                            return;\r\n
                        }\r\n
                        applyTouchMove(speed.x * 30, speed.y * 30);\r\n
                        speed.x *= 0.8;\r\n
                        speed.y *= 0.8;\r\n
                    },\r\n
                    10);\r\n
                });\r\n
            };\r\n
            var bindScrollHandler = function () {\r\n
                $this.bind("scroll" + eventClassName, function (e) {\r\n
                    updateBarSizeAndPosition();\r\n
                });\r\n
            };\r\n
            var destroy = function () {\r\n
                $this.unbind(eventClassName);\r\n
                $(window).unbind(eventClassName);\r\n
                $(document).unbind(eventClassName);\r\n
                $this.data("perfect-scrollbar", null);\r\n
                $this.data("perfect-scrollbar-update", null);\r\n
                $this.data("perfect-scrollbar-destroy", null);\r\n
                $scrollbarX.remove();\r\n
                $scrollbarY.remove();\r\n
                $scrollbarXRail.remove();\r\n
                $scrollbarYRail.remove();\r\n
                $scrollbarX = $scrollbarY = containerWidth = containerHeight = contentWidth = contentHeight = scrollbarXWidth = scrollbarXLeft = scrollbarXBottom = scrollbarYHeight = scrollbarYTop = scrollbarYRight = null;\r\n
            };\r\n
            var ieSupport = function (version) {\r\n
                $this.addClass("ie").addClass("ie" + version);\r\n
                var bindHoverHandlers = function () {\r\n
                    var mouseenter = function () {\r\n
                        $(this).addClass("hover");\r\n
                    };\r\n
                    var mouseleave = function () {\r\n
                        $(this).removeClass("hover");\r\n
                    };\r\n
                    $this.bind("mouseenter" + eventClassName, mouseenter).bind("mouseleave" + eventClassName, mouseleave);\r\n
                    $scrollbarXRail.bind("mouseenter" + eventClassName, mouseenter).bind("mouseleave" + eventClassName, mouseleave);\r\n
                    $scrollbarYRail.bind("mouseenter" + eventClassName, mouseenter).bind("mouseleave" + eventClassName, mouseleave);\r\n
                    $scrollbarX.bind("mouseenter" + eventClassName, mouseenter).bind("mouseleave" + eventClassName, mouseleave);\r\n
                    $scrollbarY.bind("mouseenter" + eventClassName, mouseenter).bind("mouseleave" + eventClassName, mouseleave);\r\n
                };\r\n
                var fixIe6ScrollbarPosition = function () {\r\n
                    updateScrollbarCss = function () {\r\n
                        $scrollbarX.css({\r\n
                            left: scrollbarXLeft + $this.scrollLeft(),\r\n
                            bottom: scrollbarXBottom,\r\n
                            width: scrollbarXWidth\r\n
                        });\r\n
                        $scrollbarY.css({\r\n
                            top: scrollbarYTop + $this.scrollTop(),\r\n
                            right: scrollbarYRight,\r\n
                            height: scrollbarYHeight\r\n
                        });\r\n
                        $scrollbarX.hide().show();\r\n
                        $scrollbarY.hide().show();\r\n
                    };\r\n
                };\r\n
                if (version === 6) {\r\n
                    bindHoverHandlers();\r\n
                    fixIe6ScrollbarPosition();\r\n
                }\r\n
            };\r\n
            var supportsTouch = (("ontouchstart" in window) || window.DocumentTouch && document instanceof window.DocumentTouch);\r\n
            var initialize = function () {\r\n
                var ieMatch = navigator.userAgent.toLowerCase().match(/(msie) ([\\w.]+)/);\r\n
                if (ieMatch && ieMatch[1] === "msie") {\r\n
                    ieSupport(parseInt(ieMatch[2], 10));\r\n
                }\r\n
                updateBarSizeAndPosition();\r\n
                bindScrollHandler();\r\n
                bindMouseScrollXHandler();\r\n
                bindMouseScrollYHandler();\r\n
                bindRailClickHandler();\r\n
                if (supportsTouch) {\r\n
                    bindMobileTouchHandler();\r\n
                }\r\n
                if ($this.mousewheel) {\r\n
                    bindMouseWheelHandler();\r\n
                }\r\n
                if (settings.useKeyboard) {\r\n
                    bindKeyboardHandler();\r\n
                }\r\n
                $this.data("perfect-scrollbar", $this);\r\n
                $this.data("perfect-scrollbar-update", updateBarSizeAndPosition);\r\n
                $this.data("perfect-scrollbar-destroy", destroy);\r\n
            };\r\n
            initialize();\r\n
            return $this;\r\n
        });\r\n
    };\r\n
}));

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>28663</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
