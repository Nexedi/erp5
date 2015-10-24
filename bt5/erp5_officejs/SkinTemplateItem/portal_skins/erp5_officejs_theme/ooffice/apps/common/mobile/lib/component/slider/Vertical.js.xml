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
            <value> <string>ts44308812.67</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Vertical.js</string> </value>
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
 Ext.define("Common.component.slider.Vertical", {\r\n
    extend: "Ext.slider.Slider",\r\n
    xtype: "verticalslider",\r\n
    config: {\r\n
        baseCls: "x-slider-vertical",\r\n
        thumbConfig: {\r\n
            draggable: {\r\n
                direction: "vertical"\r\n
            }\r\n
        }\r\n
    },\r\n
    refreshOffsetValueRatio: function () {\r\n
        var valueRange = this.getMaxValue() - this.getMinValue(),\r\n
        trackHeight = this.elementHeight - this.thumbHeight;\r\n
        this.offsetValueRatio = trackHeight / valueRange;\r\n
    },\r\n
    refreshElementHeight: function () {\r\n
        this.elementHeight = this.element.dom.offsetHeight;\r\n
        var thumb = this.getThumb(0);\r\n
        if (thumb) {\r\n
            this.thumbHeight = thumb.getElementWidth();\r\n
        }\r\n
    },\r\n
    refresh: function () {\r\n
        this.refreshElementHeight();\r\n
        this.refreshValue();\r\n
    },\r\n
    onThumbDragStart: function (thumb, e) {\r\n
        if (e.absDeltaY <= e.absDeltaX) {\r\n
            return false;\r\n
        } else {\r\n
            e.stopPropagation();\r\n
        }\r\n
        if (this.getAllowThumbsOverlapping()) {\r\n
            this.setActiveThumb(thumb);\r\n
        }\r\n
        this.dragStartValue = this.getValue()[this.getThumbIndex(thumb)];\r\n
        this.fireEvent("dragstart", this, thumb, this.dragStartValue, e);\r\n
    },\r\n
    onThumbDrag: function (thumb, e, offsetX, offsetY) {\r\n
        var index = this.getThumbIndex(thumb),\r\n
        offsetValueRatio = this.offsetValueRatio,\r\n
        constrainedValue = this.constrainValue(offsetY / offsetValueRatio);\r\n
        e.stopPropagation();\r\n
        this.setIndexValue(index, constrainedValue);\r\n
        this.fireEvent("drag", this, thumb, this.getValue(), e);\r\n
        return false;\r\n
    },\r\n
    setIndexValue: function (index, value, animation) {\r\n
        var thumb = this.getThumb(index),\r\n
        values = this.getValue(),\r\n
        offsetValueRatio = this.offsetValueRatio,\r\n
        draggable = thumb.getDraggable();\r\n
        draggable.setOffset(null, value * offsetValueRatio, animation);\r\n
        values[index] = this.constrainValue(draggable.getOffset().y / offsetValueRatio);\r\n
    },\r\n
    updateValue: function (newValue, oldValue) {\r\n
        var thumbs = this.getThumbs(),\r\n
        ln = newValue.length,\r\n
        i;\r\n
        this.setThumbsCount(ln);\r\n
        for (i = 0; i < ln; i++) {\r\n
            thumbs[i].getDraggable().setExtraConstraint(null).setOffset(0, newValue[i] * this.offsetValueRatio);\r\n
        }\r\n
        for (i = 0; i < ln; i++) {\r\n
            this.refreshThumbConstraints(thumbs[i]);\r\n
        }\r\n
    },\r\n
    refreshThumbConstraints: function (thumb) {\r\n
        var allowThumbsOverlapping = this.getAllowThumbsOverlapping(),\r\n
        offsetY = thumb.getDraggable().getOffset().y,\r\n
        thumbs = this.getThumbs(),\r\n
        index = this.getThumbIndex(thumb),\r\n
        previousThumb = thumbs[index - 1],\r\n
        nextThumb = thumbs[index + 1],\r\n
        thumbHeight = this.thumbHeight;\r\n
        if (previousThumb) {\r\n
            previousThumb.getDraggable().addExtraConstraint({\r\n
                max: {\r\n
                    y: offsetY - ((allowThumbsOverlapping) ? 0 : thumbHeight)\r\n
                }\r\n
            });\r\n
        }\r\n
        if (nextThumb) {\r\n
            nextThumb.getDraggable().addExtraConstraint({\r\n
                min: {\r\n
                    y: offsetY + ((allowThumbsOverlapping) ? 0 : thumbHeight)\r\n
                }\r\n
            });\r\n
        }\r\n
    },\r\n
    onTap: function (e) {\r\n
        if (this.isDisabled()) {\r\n
            return;\r\n
        }\r\n
        var targetElement = Ext.get(e.target);\r\n
        if (!targetElement || targetElement.hasCls("x-thumb")) {\r\n
            return;\r\n
        }\r\n
        var touchPointY = e.touch.point.y,\r\n
        element = this.element,\r\n
        elementY = element.getY(),\r\n
        offset = touchPointY - elementY - (this.thumbHeight / 2),\r\n
        value = this.constrainValue(offset / this.offsetValueRatio),\r\n
        values = this.getValue(),\r\n
        minDistance = Infinity,\r\n
        ln = values.length,\r\n
        i,\r\n
        absDistance,\r\n
        testValue,\r\n
        closestIndex,\r\n
        oldValue,\r\n
        thumb;\r\n
        if (ln === 1) {\r\n
            closestIndex = 0;\r\n
        } else {\r\n
            for (i = 0; i < ln; i++) {\r\n
                testValue = values[i];\r\n
                absDistance = Math.abs(testValue - value);\r\n
                if (absDistance < minDistance) {\r\n
                    minDistance = absDistance;\r\n
                    closestIndex = i;\r\n
                }\r\n
            }\r\n
        }\r\n
        oldValue = values[closestIndex];\r\n
        thumb = this.getThumb(closestIndex);\r\n
        this.setIndexValue(closestIndex, value, this.getAnimation());\r\n
        this.refreshThumbConstraints(thumb);\r\n
        if (oldValue !== value) {\r\n
            this.fireEvent("change", this, thumb, value, oldValue);\r\n
        }\r\n
    }\r\n
},\r\n
function () {\r\n
    Ext.deprecateProperty(this, "animationDuration", null, "Ext.slider.Slider.animationDuration has been removed");\r\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6565</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
