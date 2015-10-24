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
            <value> <string>ts44308802.37</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Bootstrap.js</string> </value>
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
 function onDropDownKeyDown(e) {\r\n
    var $this = $(this),\r\n
    $parent = $this.parent(),\r\n
    beforeEvent = jQuery.Event("keydown.before.bs.dropdown"),\r\n
    afterEvent = jQuery.Event("keydown.after.bs.dropdown");\r\n
    $parent.trigger(beforeEvent);\r\n
    if (beforeEvent.isDefaultPrevented()) {\r\n
        return;\r\n
    }\r\n
    patchDropDownKeyDown.call(this, e);\r\n
    e.preventDefault();\r\n
    e.stopPropagation();\r\n
    $parent.trigger(afterEvent);\r\n
}\r\n
function patchDropDownKeyDown(e) {\r\n
    if (!/(38|40|27)/.test(e.keyCode)) {\r\n
        return;\r\n
    }\r\n
    var $this = $(this);\r\n
    e.preventDefault();\r\n
    e.stopPropagation();\r\n
    if ($this.is(".disabled, :disabled")) {\r\n
        return;\r\n
    }\r\n
    var $parent = getParent($this);\r\n
    var isActive = $parent.hasClass("open");\r\n
    if (!isActive || (isActive && e.keyCode == 27)) {\r\n
        if (e.which == 27) {\r\n
            $items = $("[role=menu] li.dropdown-submenu.over:visible", $parent);\r\n
            if ($items.size()) {\r\n
                $items.eq($items.size() - 1).removeClass("over");\r\n
                return false;\r\n
            } else {\r\n
                $parent.find("[data-toggle=dropdown]").focus();\r\n
            }\r\n
        }\r\n
        return $this.click();\r\n
    }\r\n
    var $items = $("[role=menu] li:not(.divider):not(.disabled):visible", $parent).find("> a");\r\n
    if (!$items.length) {\r\n
        return;\r\n
    }\r\n
    var index = $items.index($items.filter(":focus"));\r\n
    if (e.keyCode == 38) {\r\n
        index > 0 ? index--:(index = $items.length - 1);\r\n
    } else {\r\n
        if (e.keyCode == 40) {\r\n
            index < $items.length - 1 ? index++:(index = 0);\r\n
        }\r\n
    }\r\n
    if (!~index) {\r\n
        index = 0;\r\n
    }\r\n
    $items.eq(index).focus();\r\n
}\r\n
function getParent($this) {\r\n
    var selector = $this.attr("data-target");\r\n
    if (!selector) {\r\n
        selector = $this.attr("href");\r\n
        selector = selector && /#/.test(selector) && selector.replace(/.*(?=#[^\\s]*$)/, "");\r\n
    }\r\n
    var $parent = selector && $(selector);\r\n
    return $parent && $parent.length ? $parent : $this.parent();\r\n
}\r\n
$(document).off("keydown.bs.dropdown.data-api").on("keydown.bs.dropdown.data-api", "[data-toggle=dropdown], [role=menu]", onDropDownKeyDown);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3793</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
