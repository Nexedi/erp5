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
            <value> <string>ts44308802.18</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>keymaster.js</string> </value>
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
 (function (global) {\r\n
    var k, _handlers = {},\r\n
    _mods = {\r\n
        16: false,\r\n
        18: false,\r\n
        17: false,\r\n
        91: false\r\n
    },\r\n
    _scope = "all",\r\n
    _MODIFIERS = {\r\n
        "⇧": 16,\r\n
        shift: 16,\r\n
        "⌥": 18,\r\n
        alt: 18,\r\n
        option: 18,\r\n
        "⌃": 17,\r\n
        ctrl: 17,\r\n
        control: 17,\r\n
        "⌘": 91,\r\n
        command: 91\r\n
    },\r\n
    _MAP = {\r\n
        backspace: 8,\r\n
        tab: 9,\r\n
        clear: 12,\r\n
        enter: 13,\r\n
        "return": 13,\r\n
        esc: 27,\r\n
        escape: 27,\r\n
        space: 32,\r\n
        left: 37,\r\n
        up: 38,\r\n
        right: 39,\r\n
        down: 40,\r\n
        del: 46,\r\n
        "delete": 46,\r\n
        home: 36,\r\n
        end: 35,\r\n
        pageup: 33,\r\n
        pagedown: 34,\r\n
        ",": 188,\r\n
        ".": 190,\r\n
        "/": 191,\r\n
        "`": 192,\r\n
        "-": 189,\r\n
        "=": 187,\r\n
        ";": 186,\r\n
        "\'": 222,\r\n
        "[": 219,\r\n
        "]": 221,\r\n
        "\\\\": 220\r\n
    },\r\n
    code = function (x) {\r\n
        return _MAP[x] || x.toUpperCase().charCodeAt(0);\r\n
    },\r\n
    _downKeys = [];\r\n
    var locked;\r\n
    for (k = 1; k < 20; k++) {\r\n
        _MAP["f" + k] = 111 + k;\r\n
    }\r\n
    function index(array, item) {\r\n
        var i = array.length;\r\n
        while (i--) {\r\n
            if (array[i] === item) {\r\n
                return i;\r\n
            }\r\n
        }\r\n
        return -1;\r\n
    }\r\n
    function compareArray(a1, a2) {\r\n
        if (a1.length != a2.length) {\r\n
            return false;\r\n
        }\r\n
        for (var i = 0; i < a1.length; i++) {\r\n
            if (a1[i] !== a2[i]) {\r\n
                return false;\r\n
            }\r\n
        }\r\n
        return true;\r\n
    }\r\n
    var modifierMap = {\r\n
        16: "shiftKey",\r\n
        18: "altKey",\r\n
        17: "ctrlKey",\r\n
        91: "metaKey"\r\n
    };\r\n
    function updateModifierKey(event) {\r\n
        for (k in _mods) {\r\n
            _mods[k] = event[modifierMap[k]];\r\n
        }\r\n
    }\r\n
    function dispatch(event) {\r\n
        var key, handler, k, i, modifiersMatch, scope;\r\n
        key = event.keyCode;\r\n
        if (index(_downKeys, key) == -1) {\r\n
            _downKeys.push(key);\r\n
        }\r\n
        if (key == 93 || key == 224) {\r\n
            key = 91;\r\n
        }\r\n
        if (key in _mods) {\r\n
            _mods[key] = true;\r\n
            for (k in _MODIFIERS) {\r\n
                if (_MODIFIERS[k] == key) {\r\n
                    assignKey[k] = true;\r\n
                }\r\n
            }\r\n
            return;\r\n
        }\r\n
        updateModifierKey(event);\r\n
        if (!assignKey.filter.call(this, event)) {\r\n
            return;\r\n
        }\r\n
        if (! (key in _handlers)) {\r\n
            return;\r\n
        }\r\n
        scope = getScope();\r\n
        for (i = 0; i < _handlers[key].length; i++) {\r\n
            handler = _handlers[key][i];\r\n
            if (handler.scope == scope || handler.scope == "all") {\r\n
                modifiersMatch = handler.mods.length > 0;\r\n
                for (k in _mods) {\r\n
                    if ((!_mods[k] && index(handler.mods, +k) > -1) || (_mods[k] && index(handler.mods, +k) == -1)) {\r\n
                        modifiersMatch = false;\r\n
                    }\r\n
                }\r\n
                if ((handler.mods.length == 0 && !_mods[16] && !_mods[18] && !_mods[17] && !_mods[91]) || modifiersMatch) {\r\n
                    if (locked === true || handler.locked || handler.method(event, handler) === false) {\r\n
                        if (event.preventDefault) {\r\n
                            event.preventDefault();\r\n
                        } else {\r\n
                            event.returnValue = false;\r\n
                        }\r\n
                        if (event.stopPropagation) {\r\n
                            event.stopPropagation();\r\n
                        }\r\n
                        if (event.cancelBubble) {\r\n
                            event.cancelBubble = true;\r\n
                        }\r\n
                    }\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function clearModifier(event) {\r\n
        var key = event.keyCode,\r\n
        k, i = index(_downKeys, key);\r\n
        if (i >= 0) {\r\n
            _downKeys.splice(i, 1);\r\n
        }\r\n
        if (key == 93 || key == 224) {\r\n
            key = 91;\r\n
        }\r\n
        if (key in _mods) {\r\n
            _mods[key] = false;\r\n
            for (k in _MODIFIERS) {\r\n
                if (_MODIFIERS[k] == key) {\r\n
                    assignKey[k] = false;\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function resetModifiers() {\r\n
        for (k in _mods) {\r\n
            _mods[k] = false;\r\n
        }\r\n
        for (k in _MODIFIERS) {\r\n
            assignKey[k] = false;\r\n
        }\r\n
    }\r\n
    function assignKey(key, scope, method) {\r\n
        var keys, mods;\r\n
        keys = getKeys(key);\r\n
        if (method === undefined) {\r\n
            method = scope;\r\n
            scope = "all";\r\n
        }\r\n
        for (var i = 0; i < keys.length; i++) {\r\n
            mods = [];\r\n
            key = keys[i].split("+");\r\n
            if (key.length > 1) {\r\n
                mods = getMods(key);\r\n
                key = [key[key.length - 1]];\r\n
            }\r\n
            key = key[0];\r\n
            key = code(key);\r\n
            if (! (key in _handlers)) {\r\n
                _handlers[key] = [];\r\n
            }\r\n
            _handlers[key].push({\r\n
                shortcut: keys[i],\r\n
                scope: scope,\r\n
                method: method,\r\n
                key: keys[i],\r\n
                mods: mods\r\n
            });\r\n
        }\r\n
    }\r\n
    function unbindKey(key, scope) {\r\n
        var multipleKeys, keys, mods = [],\r\n
        i,\r\n
        j,\r\n
        obj;\r\n
        multipleKeys = getKeys(key);\r\n
        for (j = 0; j < multipleKeys.length; j++) {\r\n
            keys = multipleKeys[j].split("+");\r\n
            if (keys.length > 1) {\r\n
                mods = getMods(keys);\r\n
                key = keys[keys.length - 1];\r\n
            }\r\n
            key = code(key);\r\n
            if (scope === undefined) {\r\n
                scope = getScope();\r\n
            }\r\n
            if (!_handlers[key]) {\r\n
                return;\r\n
            }\r\n
            for (i in _handlers[key]) {\r\n
                obj = _handlers[key][i];\r\n
                if (obj.scope === scope && compareArray(obj.mods, mods)) {\r\n
                    _handlers[key][i] = {};\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function isPressed(keyCode) {\r\n
        if (typeof(keyCode) == "string") {\r\n
            keyCode = code(keyCode);\r\n
        }\r\n
        return index(_downKeys, keyCode) != -1;\r\n
    }\r\n
    function getPressedKeyCodes() {\r\n
        return _downKeys.slice(0);\r\n
    }\r\n
    function filter(event) {\r\n
        var tagName = (event.target || event.srcElement).tagName;\r\n
        return ! (tagName == "INPUT" || tagName == "SELECT" || tagName == "TEXTAREA");\r\n
    }\r\n
    for (k in _MODIFIERS) {\r\n
        assignKey[k] = false;\r\n
    }\r\n
    function setScope(scope) {\r\n
        _scope = scope || "all";\r\n
    }\r\n
    function getScope() {\r\n
        return _scope || "all";\r\n
    }\r\n
    function deleteScope(scope) {\r\n
        var key, handlers, i;\r\n
        for (key in _handlers) {\r\n
            handlers = _handlers[key];\r\n
            for (i = 0; i < handlers.length;) {\r\n
                if (handlers[i].scope === scope) {\r\n
                    handlers.splice(i, 1);\r\n
                } else {\r\n
                    i++;\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function getKeys(key) {\r\n
        var keys;\r\n
        key = key.replace(/\\s/g, "");\r\n
        keys = key.split(",");\r\n
        if ((keys[keys.length - 1]) == "") {\r\n
            keys[keys.length - 2] += ",";\r\n
        }\r\n
        return keys;\r\n
    }\r\n
    function getMods(key) {\r\n
        var mods = key.slice(0, key.length - 1);\r\n
        for (var mi = 0; mi < mods.length; mi++) {\r\n
            mods[mi] = _MODIFIERS[mods[mi]];\r\n
        }\r\n
        return mods;\r\n
    }\r\n
    function addEvent(object, event, method) {\r\n
        if (object.addEventListener) {\r\n
            object.addEventListener(event, method, false);\r\n
        } else {\r\n
            if (object.attachEvent) {\r\n
                object.attachEvent("on" + event, function () {\r\n
                    method(window.event);\r\n
                });\r\n
            }\r\n
        }\r\n
    }\r\n
    addEvent(document, "keydown", function (event) {\r\n
        dispatch(event);\r\n
    });\r\n
    addEvent(document, "keyup", clearModifier);\r\n
    addEvent(window, "focus", resetModifiers);\r\n
    var previousKey = global.key;\r\n
    function noConflict() {\r\n
        var k = global.key;\r\n
        global.key = previousKey;\r\n
        return k;\r\n
    }\r\n
    function setKeyOptions(key, scope, option, value) {\r\n
        var keys, mods = [],\r\n
        i,\r\n
        obj;\r\n
        var multipleKeys = getKeys(key);\r\n
        for (var j = multipleKeys.length; j--;) {\r\n
            keys = multipleKeys[j].split("+");\r\n
            if (keys.length > 1) {\r\n
                mods = getMods(keys);\r\n
                key = keys[keys.length - 1];\r\n
            }\r\n
            key = code(key);\r\n
            if (scope === undefined) {\r\n
                scope = getScope();\r\n
            }\r\n
            if (_handlers[key]) {\r\n
                for (i in _handlers[key]) {\r\n
                    obj = _handlers[key][i];\r\n
                    if (obj.scope === scope && compareArray(obj.mods, mods)) {\r\n
                        _handlers[key][i][option] = value;\r\n
                    }\r\n
                }\r\n
            }\r\n
        }\r\n
    }\r\n
    function suspend(key, scope) {\r\n
        key ? setKeyOptions(key, scope, "locked", true) : (locked = true);\r\n
    }\r\n
    function resume(key, scope) {\r\n
        key ? setKeyOptions(key, scope, "locked", false) : (locked = false);\r\n
    }\r\n
    global.key = assignKey;\r\n
    global.key.setScope = setScope;\r\n
    global.key.getScope = getScope;\r\n
    global.key.deleteScope = deleteScope;\r\n
    global.key.filter = filter;\r\n
    global.key.isPressed = isPressed;\r\n
    global.key.getPressedKeyCodes = getPressedKeyCodes;\r\n
    global.key.noConflict = noConflict;\r\n
    global.key.unbind = unbindKey;\r\n
    global.key.suspend = suspend;\r\n
    global.key.resume = resume;\r\n
    if (typeof module !== "undefined") {\r\n
        module.exports = key;\r\n
    }\r\n
})(this);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11729</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
