<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts32886612.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>handsontable.full.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * Handsontable 0.15.0-beta3\n
 * Handsontable is a JavaScript library for editable tables with basic copy-paste compatibility with Excel and Google Docs\n
 *\n
 * Copyright (c) 2012-2014 Marcin Warpechowski\n
 * Copyright 2015 Handsoncode sp. z o.o. <hello@handsontable.com>\n
 * Licensed under the MIT license.\n
 * http://handsontable.com/\n
 *\n
 * Date: Thu May 21 2015 12:12:59 GMT+0200 (CEST)\n
 */\n
/*jslint white: true, browser: true, plusplus: true, indent: 4, maxerr: 50 */\n
\n
window.Handsontable = {\n
  version: \'0.15.0-beta3\'\n
};\n
require=(function outer (modules, cache, entry) {\n
  // Save the require from previous bundle to this closure if any\n
  var previousRequire = typeof require == "function" && require;\n
  var globalNS = JSON.parse(\'{"zeroclipboard":"ZeroClipboard","moment":"moment","numeral":"numeral","pikaday":"Pikaday"}\') || {};\n
\n
  function newRequire(name, jumped){\n
    if(!cache[name]) {\n
\n
      if(!modules[name]) {\n
        // if we cannot find the the module within our internal map or\n
        // cache jump to the current global require ie. the last bundle\n
        // that was added to the page.\n
        var currentRequire = typeof require == "function" && require;\n
        if (!jumped && currentRequire) return currentRequire(name, true);\n
\n
        // If there are other bundles on this page the require from the\n
        // previous one is saved to \'previousRequire\'. Repeat this as\n
        // many times as there are bundles until the module is found or\n
        // we exhaust the require chain.\n
        if (previousRequire) return previousRequire(name, true);\n
\n
        // Try find module from global scope\n
        if (globalNS[name] && typeof window[globalNS[name]] !== \'undefined\') {\n
          return window[globalNS[name]];\n
        }\n
\n
        var err = new Error(\'Cannot find module \\\'\' + name + \'\\\'\');\n
        err.code = \'MODULE_NOT_FOUND\';\n
        throw err;\n
      }\n
      var m = cache[name] = {exports:{}};\n
      modules[name][0].call(m.exports, function(x){\n
        var id = modules[name][1][x];\n
        return newRequire(id ? id : x);\n
      },m,m.exports,outer,modules,cache,entry);\n
    }\n
    return cache[name].exports;\n
  }\n
  for(var i=0;i<entry.length;i++) newRequire(entry[i]);\n
\n
  // Override the current require with this new one\n
  return newRequire;\n
})\n
({1:[function(require,module,exports){\n
"use strict";\n
if (window.jQuery) {\n
  (function(window, $, Handsontable) {\n
    $.fn.handsontable = function(action) {\n
      var i,\n
          ilen,\n
          args,\n
          output,\n
          userSettings,\n
          $this = this.first(),\n
          instance = $this.data(\'handsontable\');\n
      if (typeof action !== \'string\') {\n
        userSettings = action || {};\n
        if (instance) {\n
          instance.updateSettings(userSettings);\n
        } else {\n
          instance = new Handsontable.Core($this[0], userSettings);\n
          $this.data(\'handsontable\', instance);\n
          instance.init();\n
        }\n
        return $this;\n
      } else {\n
        args = [];\n
        if (arguments.length > 1) {\n
          for (i = 1, ilen = arguments.length; i < ilen; i++) {\n
            args.push(arguments[i]);\n
          }\n
        }\n
        if (instance) {\n
          if (typeof instance[action] !== \'undefined\') {\n
            output = instance[action].apply(instance, args);\n
            if (action === \'destroy\') {\n
              $this.removeData();\n
            }\n
          } else {\n
            throw new Error(\'Handsontable do not provide action: \' + action);\n
          }\n
        }\n
        return output;\n
      }\n
    };\n
  })(window, jQuery, Handsontable);\n
}\n
\n
\n
//# \n
},{}],2:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  autoResize: {get: function() {\n
      return autoResize;\n
    }},\n
  __esModule: {value: true}\n
});\n
;\n
function autoResize() {\n
  var defaults = {\n
    minHeight: 200,\n
    maxHeight: 300,\n
    minWidth: 100,\n
    maxWidth: 300\n
  },\n
      el,\n
      body = document.body,\n
      text = document.createTextNode(\'\'),\n
      span = document.createElement(\'SPAN\'),\n
      observe = function(element, event, handler) {\n
        if (window.attachEvent) {\n
          element.attachEvent(\'on\' + event, handler);\n
        } else {\n
          element.addEventListener(event, handler, false);\n
        }\n
      },\n
      unObserve = function(element, event, handler) {\n
        if (window.removeEventListener) {\n
          element.removeEventListener(event, handler, false);\n
        } else {\n
          element.detachEvent(\'on\' + event, handler);\n
        }\n
      },\n
      resize = function(newChar) {\n
        var width,\n
            scrollHeight;\n
        if (!newChar) {\n
          newChar = "";\n
        } else if (!/^[a-zA-Z \\.,\\\\\\/\\|0-9]$/.test(newChar)) {\n
          newChar = ".";\n
        }\n
        if (text.textContent !== void 0) {\n
          text.textContent = el.value + newChar;\n
        } else {\n
          text.data = el.value + newChar;\n
        }\n
        span.style.fontSize = Handsontable.Dom.getComputedStyle(el).fontSize;\n
        span.style.fontFamily = Handsontable.Dom.getComputedStyle(el).fontFamily;\n
        span.style.whiteSpace = "pre";\n
        body.appendChild(span);\n
        width = span.clientWidth + 2;\n
        body.removeChild(span);\n
        el.style.height = defaults.minHeight + \'px\';\n
        if (defaults.minWidth > width) {\n
          el.style.width = defaults.minWidth + \'px\';\n
        } else if (width > defaults.maxWidth) {\n
          el.style.width = defaults.maxWidth + \'px\';\n
        } else {\n
          el.style.width = width + \'px\';\n
        }\n
        scrollHeight = el.scrollHeight ? el.scrollHeight - 1 : 0;\n
        if (defaults.minHeight > scrollHeight) {\n
          el.style.height = defaults.minHeight + \'px\';\n
        } else if (defaults.maxHeight < scrollHeight) {\n
          el.style.height = defaults.maxHeight + \'px\';\n
          el.style.overflowY = \'visible\';\n
        } else {\n
          el.style.height = scrollHeight + \'px\';\n
        }\n
      },\n
      delayedResize = function() {\n
        window.setTimeout(resize, 0);\n
      },\n
      extendDefaults = function(config) {\n
        if (config && config.minHeight) {\n
          if (config.minHeight == \'inherit\') {\n
            defaults.minHeight = el.clientHeight;\n
          } else {\n
            var minHeight = parseInt(config.minHeight);\n
            if (!isNaN(minHeight)) {\n
              defaults.minHeight = minHeight;\n
            }\n
          }\n
        }\n
        if (config && config.maxHeight) {\n
          if (config.maxHeight == \'inherit\') {\n
            defaults.maxHeight = el.clientHeight;\n
          } else {\n
            var maxHeight = parseInt(config.maxHeight);\n
            if (!isNaN(maxHeight)) {\n
              defaults.maxHeight = maxHeight;\n
            }\n
          }\n
        }\n
        if (config && config.minWidth) {\n
          if (config.minWidth == \'inherit\') {\n
            defaults.minWidth = el.clientWidth;\n
          } else {\n
            var minWidth = parseInt(config.minWidth);\n
            if (!isNaN(minWidth)) {\n
              defaults.minWidth = minWidth;\n
            }\n
          }\n
        }\n
        if (config && config.maxWidth) {\n
          if (config.maxWidth == \'inherit\') {\n
            defaults.maxWidth = el.clientWidth;\n
          } else {\n
            var maxWidth = parseInt(config.maxWidth);\n
            if (!isNaN(maxWidth)) {\n
              defaults.maxWidth = maxWidth;\n
            }\n
          }\n
        }\n
        if (!span.firstChild) {\n
          span.className = "autoResize";\n
          span.style.display = \'inline-block\';\n
          span.appendChild(text);\n
        }\n
      },\n
      init = function(el_, config, doObserve) {\n
        el = el_;\n
        extendDefaults(config);\n
        if (el.nodeName == \'TEXTAREA\') {\n
          el.style.resize = \'none\';\n
          el.style.overflowY = \'\';\n
          el.style.height = defaults.minHeight + \'px\';\n
          el.style.minWidth = defaults.minWidth + \'px\';\n
          el.style.maxWidth = defaults.maxWidth + \'px\';\n
          el.style.overflowY = \'hidden\';\n
        }\n
        if (doObserve) {\n
          observe(el, \'change\', resize);\n
          observe(el, \'cut\', delayedResize);\n
          observe(el, \'paste\', delayedResize);\n
          observe(el, \'drop\', delayedResize);\n
          observe(el, \'keydown\', delayedResize);\n
        }\n
        resize();\n
      };\n
  return {\n
    init: function(el_, config, doObserve) {\n
      init(el_, config, doObserve);\n
    },\n
    unObserve: function() {\n
      unObserve(el, \'change\', resize);\n
      unObserve(el, \'cut\', delayedResize);\n
      unObserve(el, \'paste\', delayedResize);\n
      unObserve(el, \'drop\', delayedResize);\n
      unObserve(el, \'keydown\', delayedResize);\n
    },\n
    resize: resize\n
  };\n
}\n
\n
\n
//# \n
},{}],3:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  copyPasteManager: {get: function() {\n
      return copyPasteManager;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_eventManager_46_js__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
;\n
var instance;\n
function copyPasteManager() {\n
  if (!instance) {\n
    instance = new CopyPasteClass();\n
  } else if (instance.hasBeenDestroyed()) {\n
    instance.init();\n
  }\n
  instance.refCounter++;\n
  return instance;\n
}\n
function CopyPasteClass() {\n
  this.refCounter = 0;\n
  this.init();\n
}\n
CopyPasteClass.prototype.init = function() {\n
  var style,\n
      parent;\n
  this.copyCallbacks = [];\n
  this.cutCallbacks = [];\n
  this.pasteCallbacks = [];\n
  this._eventManager = eventManagerObject(this);\n
  parent = document.body;\n
  if (document.getElementById(\'CopyPasteDiv\')) {\n
    this.elDiv = document.getElementById(\'CopyPasteDiv\');\n
    this.elTextarea = this.elDiv.firstChild;\n
  } else {\n
    this.elDiv = document.createElement(\'div\');\n
    this.elDiv.id = \'CopyPasteDiv\';\n
    style = this.elDiv.style;\n
    style.position = \'fixed\';\n
    style.top = \'-10000px\';\n
    style.left = \'-10000px\';\n
    parent.appendChild(this.elDiv);\n
    this.elTextarea = document.createElement(\'textarea\');\n
    this.elTextarea.className = \'copyPaste\';\n
    this.elTextarea.onpaste = function(event) {\n
      if (\'WebkitAppearance\' in document.documentElement.style) {\n
        this.value = event.clipboardData.getData("Text");\n
        return false;\n
      }\n
    };\n
    style = this.elTextarea.style;\n
    style.width = \'10000px\';\n
    style.height = \'10000px\';\n
    style.overflow = \'hidden\';\n
    this.elDiv.appendChild(this.elTextarea);\n
    if (typeof style.opacity !== \'undefined\') {\n
      style.opacity = 0;\n
    }\n
  }\n
  this.keyDownRemoveEvent = this._eventManager.addEventListener(document.documentElement, \'keydown\', this.onKeyDown.bind(this), false);\n
};\n
CopyPasteClass.prototype.onKeyDown = function(event) {\n
  var _this = this,\n
      isCtrlDown = false;\n
  function isActiveElementEditable() {\n
    var element = document.activeElement;\n
    if (element.shadowRoot && element.shadowRoot.activeElement) {\n
      element = element.shadowRoot.activeElement;\n
    }\n
    return [\'INPUT\', \'SELECT\', \'TEXTAREA\'].indexOf(element.nodeName) > -1 || element.contentEditable === \'true\';\n
  }\n
  if (event.metaKey) {\n
    isCtrlDown = true;\n
  } else if (event.ctrlKey && navigator.userAgent.indexOf(\'Mac\') === -1) {\n
    isCtrlDown = true;\n
  }\n
  if (isCtrlDown) {\n
    if (document.activeElement !== this.elTextarea && (this.getSelectionText() !== \'\' || isActiveElementEditable())) {\n
      return;\n
    }\n
    this.selectNodeText(this.elTextarea);\n
    setTimeout(function() {\n
      _this.selectNodeText(_this.elTextarea);\n
    }, 0);\n
  }\n
  if (isCtrlDown && (event.keyCode === helper.keyCode.C || event.keyCode === helper.keyCode.V || event.keyCode === helper.keyCode.X)) {\n
    if (event.keyCode === 88) {\n
      setTimeout(function() {\n
        _this.triggerCut(event);\n
      }, 0);\n
    } else if (event.keyCode === 86) {\n
      setTimeout(function() {\n
        _this.triggerPaste(event);\n
      }, 0);\n
    }\n
  }\n
};\n
CopyPasteClass.prototype.selectNodeText = function(element) {\n
  if (element) {\n
    element.select();\n
  }\n
};\n
CopyPasteClass.prototype.getSelectionText = function() {\n
  var text = \'\';\n
  if (window.getSelection) {\n
    text = window.getSelection().toString();\n
  } else if (document.selection && document.selection.type !== \'Control\') {\n
    text = document.selection.createRange().text;\n
  }\n
  return text;\n
};\n
CopyPasteClass.prototype.copyable = function(string) {\n
  if (typeof string !== \'string\' && string.toString === void 0) {\n
    throw new Error(\'copyable requires string parameter\');\n
  }\n
  this.elTextarea.value = string;\n
};\n
CopyPasteClass.prototype.onCut = function(callback) {\n
  this.cutCallbacks.push(callback);\n
};\n
CopyPasteClass.prototype.onPaste = function(callback) {\n
  this.pasteCallbacks.push(callback);\n
};\n
CopyPasteClass.prototype.removeCallback = function(callback) {\n
  var i,\n
      len;\n
  for (i = 0, len = this.copyCallbacks.length; i < len; i++) {\n
    if (this.copyCallbacks[i] === callback) {\n
      this.copyCallbacks.splice(i, 1);\n
      return true;\n
    }\n
  }\n
  for (i = 0, len = this.cutCallbacks.length; i < len; i++) {\n
    if (this.cutCallbacks[i] === callback) {\n
      this.cutCallbacks.splice(i, 1);\n
      return true;\n
    }\n
  }\n
  for (i = 0, len = this.pasteCallbacks.length; i < len; i++) {\n
    if (this.pasteCallbacks[i] === callback) {\n
      this.pasteCallbacks.splice(i, 1);\n
      return true;\n
    }\n
  }\n
  return false;\n
};\n
CopyPasteClass.prototype.triggerCut = function(event) {\n
  var _this = this;\n
  if (_this.cutCallbacks) {\n
    setTimeout(function() {\n
      for (var i = 0,\n
          len = _this.cutCallbacks.length; i < len; i++) {\n
        _this.cutCallbacks[i](event);\n
      }\n
    }, 50);\n
  }\n
};\n
CopyPasteClass.prototype.triggerPaste = function(event, string) {\n
  var _this = this;\n
  if (_this.pasteCallbacks) {\n
    setTimeout(function() {\n
      var val = string || _this.elTextarea.value;\n
      for (var i = 0,\n
          len = _this.pasteCallbacks.length; i < len; i++) {\n
        _this.pasteCallbacks[i](val, event);\n
      }\n
    }, 50);\n
  }\n
};\n
CopyPasteClass.prototype.destroy = function() {\n
  if (!this.hasBeenDestroyed() && --this.refCounter === 0) {\n
    if (this.elDiv && this.elDiv.parentNode) {\n
      this.elDiv.parentNode.removeChild(this.elDiv);\n
      this.elDiv = null;\n
      this.elTextarea = null;\n
    }\n
    this.keyDownRemoveEvent();\n
  }\n
};\n
CopyPasteClass.prototype.hasBeenDestroyed = function() {\n
  return !this.refCounter;\n
};\n
\n
\n
//# \n
},{"./../eventManager.js":45,"./../helpers.js":46}],4:[function(require,module,exports){\n
"use strict";\n
var jsonpatch;\n
(function(jsonpatch) {\n
  var objOps = {\n
    add: function(obj, key) {\n
      obj[key] = this.value;\n
      return true;\n
    },\n
    remove: function(obj, key) {\n
      delete obj[key];\n
      return true;\n
    },\n
    replace: function(obj, key) {\n
      obj[key] = this.value;\n
      return true;\n
    },\n
    move: function(obj, key, tree) {\n
      var temp = {\n
        op: "_get",\n
        path: this.from\n
      };\n
      apply(tree, [temp]);\n
      apply(tree, [{\n
        op: "remove",\n
        path: this.from\n
      }]);\n
      apply(tree, [{\n
        op: "add",\n
        path: this.path,\n
        value: temp.value\n
      }]);\n
      return true;\n
    },\n
    copy: function(obj, key, tree) {\n
      var temp = {\n
        op: "_get",\n
        path: this.from\n
      };\n
      apply(tree, [temp]);\n
      apply(tree, [{\n
        op: "add",\n
        path: this.path,\n
        value: temp.value\n
      }]);\n
      return true;\n
    },\n
    test: function(obj, key) {\n
      return (JSON.stringify(obj[key]) === JSON.stringify(this.value));\n
    },\n
    _get: function(obj, key) {\n
      this.value = obj[key];\n
    }\n
  };\n
  var arrOps = {\n
    add: function(arr, i) {\n
      arr.splice(i, 0, this.value);\n
      return true;\n
    },\n
    remove: function(arr, i) {\n
      arr.splice(i, 1);\n
      return true;\n
    },\n
    replace: function(arr, i) {\n
      arr[i] = this.value;\n
      return true;\n
    },\n
    move: objOps.move,\n
    copy: objOps.copy,\n
    test: objOps.test,\n
    _get: objOps._get\n
  };\n
  var observeOps = {\n
    add: function(patches, path) {\n
      var patch = {\n
        op: "add",\n
        path: path + escapePathComponent(this.name),\n
        value: this.object[this.name]\n
      };\n
      patches.push(patch);\n
    },\n
    \'delete\': function(patches, path) {\n
      var patch = {\n
        op: "remove",\n
        path: path + escapePathComponent(this.name)\n
      };\n
      patches.push(patch);\n
    },\n
    update: function(patches, path) {\n
      var patch = {\n
        op: "replace",\n
        path: path + escapePathComponent(this.name),\n
        value: this.object[this.name]\n
      };\n
      patches.push(patch);\n
    }\n
  };\n
  function escapePathComponent(str) {\n
    if (str.indexOf(\'/\') === -1 && str.indexOf(\'~\') === -1) {\n
      return str;\n
    }\n
    return str.replace(/~/g, \'~0\').replace(/\\//g, \'~1\');\n
  }\n
  function _getPathRecursive(root, obj) {\n
    var found;\n
    for (var key in root) {\n
      if (root.hasOwnProperty(key)) {\n
        if (root[key] === obj) {\n
          return escapePathComponent(key) + \'/\';\n
        } else if (typeof root[key] === \'object\') {\n
          found = _getPathRecursive(root[key], obj);\n
          if (found != \'\') {\n
            return escapePathComponent(key) + \'/\' + found;\n
          }\n
        }\n
      }\n
    }\n
    return \'\';\n
  }\n
  function getPath(root, obj) {\n
    if (root === obj) {\n
      return \'/\';\n
    }\n
    var path = _getPathRecursive(root, obj);\n
    if (path === \'\') {\n
      throw new Error("Object not found in root");\n
    }\n
    return \'/\' + path;\n
  }\n
  var beforeDict = [];\n
  jsonpatch.intervals;\n
  var Mirror = (function() {\n
    function Mirror(obj) {\n
      this.observers = [];\n
      this.obj = obj;\n
    }\n
    return Mirror;\n
  })();\n
  var ObserverInfo = (function() {\n
    function ObserverInfo(callback, observer) {\n
      this.callback = callback;\n
      this.observer = observer;\n
    }\n
    return ObserverInfo;\n
  })();\n
  function getMirror(obj) {\n
    for (var i = 0,\n
        ilen = beforeDict.length; i < ilen; i++) {\n
      if (beforeDict[i].obj === obj) {\n
        return beforeDict[i];\n
      }\n
    }\n
  }\n
  function getObserverFromMirror(mirror, callback) {\n
    for (var j = 0,\n
        jlen = mirror.observers.length; j < jlen; j++) {\n
      if (mirror.observers[j].callback === callback) {\n
        return mirror.observers[j].observer;\n
      }\n
    }\n
  }\n
  function removeObserverFromMirror(mirror, observer) {\n
    for (var j = 0,\n
        jlen = mirror.observers.length; j < jlen; j++) {\n
      if (mirror.observers[j].observer === observer) {\n
        mirror.observers.splice(j, 1);\n
        return;\n
      }\n
    }\n
  }\n
  function unobserve(root, observer) {\n
    generate(observer);\n
    if (Object.observe) {\n
      _unobserve(observer, root);\n
    } else {\n
      clearTimeout(observer.next);\n
    }\n
    var mirror = getMirror(root);\n
    removeObserverFromMirror(mirror, observer);\n
  }\n
  jsonpatch.unobserve = unobserve;\n
  function observe(obj, callback) {\n
    var patches = [];\n
    var root = obj;\n
    var observer;\n
    var mirror = getMirror(obj);\n
    if (!mirror) {\n
      mirror = new Mirror(obj);\n
      beforeDict.push(mirror);\n
    } else {\n
      observer = getObserverFromMirror(mirror, callback);\n
    }\n
    if (observer) {\n
      return observer;\n
    }\n
    if (Object.observe) {\n
      observer = function(arr) {\n
        _unobserve(observer, obj);\n
        _observe(observer, obj);\n
        var a = 0,\n
            alen = arr.length;\n
        while (a < alen) {\n
          if (!(arr[a].name === \'length\' && _isArray(arr[a].object)) && !(arr[a].name === \'__Jasmine_been_here_before__\')) {\n
            var type = arr[a].type;\n
            switch (type) {\n
              case \'new\':\n
                type = \'add\';\n
                break;\n
              case \'deleted\':\n
                type = \'delete\';\n
                break;\n
              case \'updated\':\n
                type = \'update\';\n
                break;\n
            }\n
            observeOps[type].call(arr[a], patches, getPath(root, arr[a].object));\n
          }\n
          a++;\n
        }\n
        if (patches) {\n
          if (callback) {\n
            callback(patches);\n
          }\n
        }\n
        observer.patches = patches;\n
        patches = [];\n
      };\n
    } else {\n
      observer = {};\n
      mirror.value = JSON.parse(JSON.stringify(obj));\n
      if (callback) {\n
        observer.callback = callback;\n
        observer.next = null;\n
        var intervals = this.intervals || [100, 1000, 10000, 60000];\n
        var currentInterval = 0;\n
        var dirtyCheck = function() {\n
          generate(observer);\n
        };\n
        var fastCheck = function() {\n
          clearTimeout(observer.next);\n
          observer.next = setTimeout(function() {\n
            dirtyCheck();\n
            currentInterval = 0;\n
            observer.next = setTimeout(slowCheck, intervals[currentInterval++]);\n
          }, 0);\n
        };\n
        var slowCheck = function() {\n
          dirtyCheck();\n
          if (currentInterval == intervals.length) {\n
            currentInterval = intervals.length - 1;\n
          }\n
          observer.next = setTimeout(slowCheck, intervals[currentInterval++]);\n
        };\n
        if (typeof window !== \'undefined\') {\n
          if (window.addEventListener) {\n
            window.addEventListener(\'mousedown\', fastCheck);\n
            window.addEventListener(\'mouseup\', fastCheck);\n
            window.addEventListener(\'keydown\', fastCheck);\n
          } else {\n
            window.attachEvent(\'onmousedown\', fastCheck);\n
            window.attachEvent(\'onmouseup\', fastCheck);\n
            window.attachEvent(\'onkeydown\', fastCheck);\n
          }\n
        }\n
        observer.next = setTimeout(slowCheck, intervals[currentInterval++]);\n
      }\n
    }\n
    observer.patches = patches;\n
    observer.object = obj;\n
    mirror.observers.push(new ObserverInfo(callback, observer));\n
    return _observe(observer, obj);\n
  }\n
  jsonpatch.observe = observe;\n
  function _observe(observer, obj) {\n
    if (Object.observe) {\n
      Object.observe(obj, observer);\n
      for (var key in obj) {\n
        if (obj.hasOwnProperty(key)) {\n
          var v = obj[key];\n
          if (v && typeof(v) === "object") {\n
            _observe(observer, v);\n
          }\n
        }\n
      }\n
    }\n
    return observer;\n
  }\n
  function _unobserve(observer, obj) {\n
    if (Object.observe) {\n
      Object.unobserve(obj, observer);\n
      for (var key in obj) {\n
        if (obj.hasOwnProperty(key)) {\n
          var v = obj[key];\n
          if (v && typeof(v) === "object") {\n
            _unobserve(observer, v);\n
          }\n
        }\n
      }\n
    }\n
    return observer;\n
  }\n
  function generate(observer) {\n
    if (Object.observe) {\n
      Object.deliverChangeRecords(observer);\n
    } else {\n
      var mirror;\n
      for (var i = 0,\n
          ilen = beforeDict.length; i < ilen; i++) {\n
        if (beforeDict[i].obj === observer.object) {\n
          mirror = beforeDict[i];\n
          break;\n
        }\n
      }\n
      _generate(mirror.value, observer.object, observer.patches, "");\n
    }\n
    var temp = observer.patches;\n
    if (temp.length > 0) {\n
      observer.patches = [];\n
      if (observer.callback) {\n
        observer.callback(temp);\n
      }\n
    }\n
    return temp;\n
  }\n
  jsonpatch.generate = generate;\n
  var _objectKeys;\n
  if (Object.keys) {\n
    _objectKeys = Object.keys;\n
  } else {\n
    _objectKeys = function(obj) {\n
      var keys = [];\n
      for (var o in obj) {\n
        if (obj.hasOwnProperty(o)) {\n
          keys.push(o);\n
        }\n
      }\n
      return keys;\n
    };\n
  }\n
  function _generate(mirror, obj, patches, path) {\n
    var newKeys = _objectKeys(obj);\n
    var oldKeys = _objectKeys(mirror);\n
    var changed = false;\n
    var deleted = false;\n
    for (var t = oldKeys.length - 1; t >= 0; t--) {\n
      var key = oldKeys[t];\n
      var oldVal = mirror[key];\n
      if (obj.hasOwnProperty(key)) {\n
        var newVal = obj[key];\n
        if (oldVal instanceof Object) {\n
          _generate(oldVal, newVal, patches, path + "/" + escapePathComponent(key));\n
        } else {\n
          if (oldVal != newVal) {\n
            changed = true;\n
            patches.push({\n
              op: "replace",\n
              path: path + "/" + escapePathComponent(key),\n
              value: newVal\n
            });\n
            mirror[key] = newVal;\n
          }\n
        }\n
      } else {\n
        patches.push({\n
          op: "remove",\n
          path: path + "/" + escapePathComponent(key)\n
        });\n
        delete mirror[key];\n
        deleted = true;\n
      }\n
    }\n
    if (!deleted && newKeys.length == oldKeys.length) {\n
      return;\n
    }\n
    for (var t = 0; t < newKeys.length; t++) {\n
      var key = newKeys[t];\n
      if (!mirror.hasOwnProperty(key)) {\n
        patches.push({\n
          op: "add",\n
          path: path + "/" + escapePathComponent(key),\n
          value: obj[key]\n
        });\n
        mirror[key] = JSON.parse(JSON.stringify(obj[key]));\n
      }\n
    }\n
  }\n
  var _isArray;\n
  if (Array.isArray) {\n
    _isArray = Array.isArray;\n
  } else {\n
    _isArray = function(obj) {\n
      return obj.push && typeof obj.length === \'number\';\n
    };\n
  }\n
  function apply(tree, patches) {\n
    var result = false,\n
        p = 0,\n
        plen = patches.length,\n
        patch;\n
    while (p < plen) {\n
      patch = patches[p];\n
      var keys = patch.path.split(\'/\');\n
      var obj = tree;\n
      var t = 1;\n
      var len = keys.length;\n
      while (true) {\n
        if (_isArray(obj)) {\n
          var index = parseInt(keys[t], 10);\n
          t++;\n
          if (t >= len) {\n
            result = arrOps[patch.op].call(patch, obj, index, tree);\n
            break;\n
          }\n
          obj = obj[index];\n
        } else {\n
          var key = keys[t];\n
          if (key.indexOf(\'~\') != -1) {\n
            key = key.replace(/~1/g, \'/\').replace(/~0/g, \'~\');\n
          }\n
          t++;\n
          if (t >= len) {\n
            result = objOps[patch.op].call(patch, obj, key, tree);\n
            break;\n
          }\n
          obj = obj[key];\n
        }\n
      }\n
      p++;\n
    }\n
    return result;\n
  }\n
  jsonpatch.apply = apply;\n
})(jsonpatch || (jsonpatch = {}));\n
if (typeof exports !== "undefined") {\n
  exports.apply = jsonpatch.apply;\n
  exports.observe = jsonpatch.observe;\n
  exports.unobserve = jsonpatch.unobserve;\n
  exports.generate = jsonpatch.generate;\n
}\n
\n
\n
//# \n
},{}],5:[function(require,module,exports){\n
"use strict";\n
(function(global) {\n
  "use strict";\n
  function countQuotes(str) {\n
    return str.split(\'"\').length - 1;\n
  }\n
  var SheetClip = {\n
    parse: function(str) {\n
      var r,\n
          rLen,\n
          rows,\n
          arr = [],\n
          a = 0,\n
          c,\n
          cLen,\n
          multiline,\n
          last;\n
      rows = str.split(\'\\n\');\n
      if (rows.length > 1 && rows[rows.length - 1] === \'\') {\n
        rows.pop();\n
      }\n
      for (r = 0, rLen = rows.length; r < rLen; r += 1) {\n
        rows[r] = rows[r].split(\'\\t\');\n
        for (c = 0, cLen = rows[r].length; c < cLen; c += 1) {\n
          if (!arr[a]) {\n
            arr[a] = [];\n
          }\n
          if (multiline && c === 0) {\n
            last = arr[a].length - 1;\n
            arr[a][last] = arr[a][last] + \'\\n\' + rows[r][0];\n
            if (multiline && (countQuotes(rows[r][0]) & 1)) {\n
              multiline = false;\n
              arr[a][last] = arr[a][last].substring(0, arr[a][last].length - 1).replace(/""/g, \'"\');\n
            }\n
          } else {\n
            if (c === cLen - 1 && rows[r][c].indexOf(\'"\') === 0 && (countQuotes(rows[r][c]) & 1)) {\n
              arr[a].push(rows[r][c].substring(1).replace(/""/g, \'"\'));\n
              multiline = true;\n
            } else {\n
              arr[a].push(rows[r][c].replace(/""/g, \'"\'));\n
              multiline = false;\n
            }\n
          }\n
        }\n
        if (!multiline) {\n
          a += 1;\n
        }\n
      }\n
      return arr;\n
    },\n
    stringify: function(arr) {\n
      var r,\n
          rLen,\n
          c,\n
          cLen,\n
          str = \'\',\n
          val;\n
      for (r = 0, rLen = arr.length; r < rLen; r += 1) {\n
        cLen = arr[r].length;\n
        for (c = 0; c < cLen; c += 1) {\n
          if (c > 0) {\n
            str += \'\\t\';\n
          }\n
          val = arr[r][c];\n
          if (typeof val === \'string\') {\n
            if (val.indexOf(\'\\n\') > -1) {\n
              str += \'"\' + val.replace(/"/g, \'""\') + \'"\';\n
            } else {\n
              str += val;\n
            }\n
          } else if (val === null || val === void 0) {\n
            str += \'\';\n
          } else {\n
            str += val;\n
          }\n
        }\n
        str += \'\\n\';\n
      }\n
      return str;\n
    }\n
  };\n
  if (typeof exports !== \'undefined\') {\n
    exports.parse = SheetClip.parse;\n
    exports.stringify = SheetClip.stringify;\n
  } else {\n
    global.SheetClip = SheetClip;\n
  }\n
}(window));\n
\n
\n
//# \n
},{}],6:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableBorder: {get: function() {\n
      return WalkontableBorder;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47_eventManager_46_js__,\n
    $__cell_47_coords_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47__46__46__47_eventManager_46_js__ = require("./../../../eventManager.js"), $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var WalkontableCellCoords = ($__cell_47_coords_46_js__ = require("./cell/coords.js"), $__cell_47_coords_46_js__ && $__cell_47_coords_46_js__.__esModule && $__cell_47_coords_46_js__ || {default: $__cell_47_coords_46_js__}).WalkontableCellCoords;\n
function WalkontableBorder(instance, settings) {\n
  var style;\n
  var createMultipleSelectorHandles = function() {\n
    this.selectionHandles = {\n
      topLeft: document.createElement(\'DIV\'),\n
      topLeftHitArea: document.createElement(\'DIV\'),\n
      bottomRight: document.createElement(\'DIV\'),\n
      bottomRightHitArea: document.createElement(\'DIV\')\n
    };\n
    var width = 10,\n
        hitAreaWidth = 40;\n
    this.selectionHandles.topLeft.className = \'topLeftSelectionHandle\';\n
    this.selectionHandles.topLeftHitArea.className = \'topLeftSelectionHandle-HitArea\';\n
    this.selectionHandles.bottomRight.className = \'bottomRightSelectionHandle\';\n
    this.selectionHandles.bottomRightHitArea.className = \'bottomRightSelectionHandle-HitArea\';\n
    this.selectionHandles.styles = {\n
      topLeft: this.selectionHandles.topLeft.style,\n
      topLeftHitArea: this.selectionHandles.topLeftHitArea.style,\n
      bottomRight: this.selectionHandles.bottomRight.style,\n
      bottomRightHitArea: this.selectionHandles.bottomRightHitArea.style\n
    };\n
    var hitAreaStyle = {\n
      \'position\': \'absolute\',\n
      \'height\': hitAreaWidth + \'px\',\n
      \'width\': hitAreaWidth + \'px\',\n
      \'border-radius\': parseInt(hitAreaWidth / 1.5, 10) + \'px\'\n
    };\n
    for (var prop in hitAreaStyle) {\n
      if (hitAreaStyle.hasOwnProperty(prop)) {\n
        this.selectionHandles.styles.bottomRightHitArea[prop] = hitAreaStyle[prop];\n
        this.selectionHandles.styles.topLeftHitArea[prop] = hitAreaStyle[prop];\n
      }\n
    }\n
    var handleStyle = {\n
      \'position\': \'absolute\',\n
      \'height\': width + \'px\',\n
      \'width\': width + \'px\',\n
      \'border-radius\': parseInt(width / 1.5, 10) + \'px\',\n
      \'background\': \'#F5F5FF\',\n
      \'border\': \'1px solid #4285c8\'\n
    };\n
    for (var prop in handleStyle) {\n
      if (handleStyle.hasOwnProperty(prop)) {\n
        this.selectionHandles.styles.bottomRight[prop] = handleStyle[prop];\n
        this.selectionHandles.styles.topLeft[prop] = handleStyle[prop];\n
      }\n
    }\n
    this.main.appendChild(this.selectionHandles.topLeft);\n
    this.main.appendChild(this.selectionHandles.bottomRight);\n
    this.main.appendChild(this.selectionHandles.topLeftHitArea);\n
    this.main.appendChild(this.selectionHandles.bottomRightHitArea);\n
  };\n
  if (!settings) {\n
    return;\n
  }\n
  var eventManager = eventManagerObject(instance);\n
  this.instance = instance;\n
  this.settings = settings;\n
  this.main = document.createElement("div");\n
  style = this.main.style;\n
  style.position = \'absolute\';\n
  style.top = 0;\n
  style.left = 0;\n
  var borderDivs = [\'top\', \'left\', \'bottom\', \'right\', \'corner\'];\n
  for (var i = 0; i < 5; i++) {\n
    var position = borderDivs[i];\n
    var DIV = document.createElement(\'DIV\');\n
    DIV.className = \'wtBorder \' + (this.settings.className || \'\');\n
    if (this.settings[position] && this.settings[position].hide) {\n
      DIV.className += " hidden";\n
    }\n
    style = DIV.style;\n
    style.backgroundColor = (this.settings[position] && this.settings[position].color) ? this.settings[position].color : settings.border.color;\n
    style.height = (this.settings[position] && this.settings[position].width) ? this.settings[position].width + \'px\' : settings.border.width + \'px\';\n
    style.width = (this.settings[position] && this.settings[position].width) ? this.settings[position].width + \'px\' : settings.border.width + \'px\';\n
    this.main.appendChild(DIV);\n
  }\n
  this.top = this.main.childNodes[0];\n
  this.left = this.main.childNodes[1];\n
  this.bottom = this.main.childNodes[2];\n
  this.right = this.main.childNodes[3];\n
  this.topStyle = this.top.style;\n
  this.leftStyle = this.left.style;\n
  this.bottomStyle = this.bottom.style;\n
  this.rightStyle = this.right.style;\n
  this.cornerDefaultStyle = {\n
    width: \'5px\',\n
    height: \'5px\',\n
    borderWidth: \'2px\',\n
    borderStyle: \'solid\',\n
    borderColor: \'#FFF\'\n
  };\n
  this.corner = this.main.childNodes[4];\n
  this.corner.className += \' corner\';\n
  this.cornerStyle = this.corner.style;\n
  this.cornerStyle.width = this.cornerDefaultStyle.width;\n
  this.cornerStyle.height = this.cornerDefaultStyle.height;\n
  this.cornerStyle.border = [this.cornerDefaultStyle.borderWidth, this.cornerDefaultStyle.borderStyle, this.cornerDefaultStyle.borderColor].join(\' \');\n
  if (Handsontable.mobileBrowser) {\n
    createMultipleSelectorHandles.call(this);\n
  }\n
  this.disappear();\n
  if (!instance.wtTable.bordersHolder) {\n
    instance.wtTable.bordersHolder = document.createElement(\'div\');\n
    instance.wtTable.bordersHolder.className = \'htBorders\';\n
    instance.wtTable.spreader.appendChild(instance.wtTable.bordersHolder);\n
  }\n
  instance.wtTable.bordersHolder.insertBefore(this.main, instance.wtTable.bordersHolder.firstChild);\n
  var down = false;\n
  eventManager.addEventListener(document.body, \'mousedown\', function() {\n
    down = true;\n
  });\n
  eventManager.addEventListener(document.body, \'mouseup\', function() {\n
    down = false;\n
  });\n
  for (var c = 0,\n
      len = this.main.childNodes.length; c < len; c++) {\n
    eventManager.addEventListener(this.main.childNodes[c], \'mouseenter\', function(event) {\n
      if (!down || !instance.getSetting(\'hideBorderOnMouseDownOver\')) {\n
        return;\n
      }\n
      event.preventDefault();\n
      event.stopImmediatePropagation();\n
      var bounds = this.getBoundingClientRect();\n
      this.style.display = \'none\';\n
      var isOutside = function(event) {\n
        if (event.clientY < Math.floor(bounds.top)) {\n
          return true;\n
        }\n
        if (event.clientY > Math.ceil(bounds.top + bounds.height)) {\n
          return true;\n
        }\n
        if (event.clientX < Math.floor(bounds.left)) {\n
          return true;\n
        }\n
        if (event.clientX > Math.ceil(bounds.left + bounds.width)) {\n
          return true;\n
        }\n
      };\n
      var handler = function(event) {\n
        if (isOutside(event)) {\n
          eventManager.removeEventListener(document.body, \'mousemove\', handler);\n
          this.style.display = \'block\';\n
        }\n
      };\n
      eventManager.addEventListener(document.body, \'mousemove\', handler);\n
    });\n
  }\n
}\n
WalkontableBorder.prototype.appear = function(corners) {\n
  if (this.disabled) {\n
    return;\n
  }\n
  var instance = this.instance;\n
  var isMultiple,\n
      fromTD,\n
      toTD,\n
      fromOffset,\n
      toOffset,\n
      containerOffset,\n
      top,\n
      minTop,\n
      left,\n
      minLeft,\n
      height,\n
      width,\n
      fromRow,\n
      fromColumn,\n
      toRow,\n
      toColumn,\n
      i,\n
      ilen,\n
      s;\n
  var isPartRange = function() {\n
    if (this.instance.selections.area.cellRange) {\n
      if (toRow != this.instance.selections.area.cellRange.to.row || toColumn != this.instance.selections.area.cellRange.to.col) {\n
        return true;\n
      }\n
    }\n
    return false;\n
  };\n
  var updateMultipleSelectionHandlesPosition = function(top, left, width, height) {\n
    var handleWidth = parseInt(this.selectionHandles.styles.topLeft.width, 10),\n
        hitAreaWidth = parseInt(this.selectionHandles.styles.topLeftHitArea.width, 10);\n
    this.selectionHandles.styles.topLeft.top = parseInt(top - handleWidth, 10) + "px";\n
    this.selectionHandles.styles.topLeft.left = parseInt(left - handleWidth, 10) + "px";\n
    this.selectionHandles.styles.topLeftHitArea.top = parseInt(top - (hitAreaWidth / 4) * 3, 10) + "px";\n
    this.selectionHandles.styles.topLeftHitArea.left = parseInt(left - (hitAreaWidth / 4) * 3, 10) + "px";\n
    this.selectionHandles.styles.bottomRight.top = parseInt(top + height, 10) + "px";\n
    this.selectionHandles.styles.bottomRight.left = parseInt(left + width, 10) + "px";\n
    this.selectionHandles.styles.bottomRightHitArea.top = parseInt(top + height - hitAreaWidth / 4, 10) + "px";\n
    this.selectionHandles.styles.bottomRightHitArea.left = parseInt(left + width - hitAreaWidth / 4, 10) + "px";\n
    if (this.settings.border.multipleSelectionHandlesVisible && this.settings.border.multipleSelectionHandlesVisible()) {\n
      this.selectionHandles.styles.topLeft.display = "block";\n
      this.selectionHandles.styles.topLeftHitArea.display = "block";\n
      if (!isPartRange.call(this)) {\n
        this.selectionHandles.styles.bottomRight.display = "block";\n
        this.selectionHandles.styles.bottomRightHitArea.display = "block";\n
      } else {\n
        this.selectionHandles.styles.bottomRight.display = "none";\n
        this.selectionHandles.styles.bottomRightHitArea.display = "none";\n
      }\n
    } else {\n
      this.selectionHandles.styles.topLeft.display = "none";\n
      this.selectionHandles.styles.bottomRight.display = "none";\n
      this.selectionHandles.styles.topLeftHitArea.display = "none";\n
      this.selectionHandles.styles.bottomRightHitArea.display = "none";\n
    }\n
    if (fromRow == this.instance.wtSettings.getSetting(\'fixedRowsTop\') || fromColumn == this.instance.wtSettings.getSetting(\'fixedColumnsLeft\')) {\n
      this.selectionHandles.styles.topLeft.zIndex = "9999";\n
      this.selectionHandles.styles.topLeftHitArea.zIndex = "9999";\n
    } else {\n
      this.selectionHandles.styles.topLeft.zIndex = "";\n
      this.selectionHandles.styles.topLeftHitArea.zIndex = "";\n
    }\n
  };\n
  if (instance.cloneOverlay instanceof WalkontableTopOverlay || instance.cloneOverlay instanceof WalkontableCornerOverlay) {\n
    ilen = instance.getSetting(\'fixedRowsTop\');\n
  } else {\n
    ilen = instance.wtTable.getRenderedRowsCount();\n
  }\n
  for (i = 0; i < ilen; i++) {\n
    s = instance.wtTable.rowFilter.renderedToSource(i);\n
    if (s >= corners[0] && s <= corners[2]) {\n
      fromRow = s;\n
      break;\n
    }\n
  }\n
  for (i = ilen - 1; i >= 0; i--) {\n
    s = instance.wtTable.rowFilter.renderedToSource(i);\n
    if (s >= corners[0] && s <= corners[2]) {\n
      toRow = s;\n
      break;\n
    }\n
  }\n
  ilen = instance.wtTable.getRenderedColumnsCount();\n
  for (i = 0; i < ilen; i++) {\n
    s = instance.wtTable.columnFilter.renderedToSource(i);\n
    if (s >= corners[1] && s <= corners[3]) {\n
      fromColumn = s;\n
      break;\n
    }\n
  }\n
  for (i = ilen - 1; i >= 0; i--) {\n
    s = instance.wtTable.columnFilter.renderedToSource(i);\n
    if (s >= corners[1] && s <= corners[3]) {\n
      toColumn = s;\n
      break;\n
    }\n
  }\n
  if (fromRow !== void 0 && fromColumn !== void 0) {\n
    isMultiple = (fromRow !== toRow || fromColumn !== toColumn);\n
    fromTD = instance.wtTable.getCell(new WalkontableCellCoords(fromRow, fromColumn));\n
    toTD = isMultiple ? instance.wtTable.getCell(new WalkontableCellCoords(toRow, toColumn)) : fromTD;\n
    fromOffset = dom.offset(fromTD);\n
    toOffset = isMultiple ? dom.offset(toTD) : fromOffset;\n
    containerOffset = dom.offset(instance.wtTable.TABLE);\n
    minTop = fromOffset.top;\n
    height = toOffset.top + dom.outerHeight(toTD) - minTop;\n
    minLeft = fromOffset.left;\n
    width = toOffset.left + dom.outerWidth(toTD) - minLeft;\n
    top = minTop - containerOffset.top - 1;\n
    left = minLeft - containerOffset.left - 1;\n
    var style = dom.getComputedStyle(fromTD);\n
    if (parseInt(style[\'borderTopWidth\'], 10) > 0) {\n
      top += 1;\n
      height = height > 0 ? height - 1 : 0;\n
    }\n
    if (parseInt(style[\'borderLeftWidth\'], 10) > 0) {\n
      left += 1;\n
      width = width > 0 ? width - 1 : 0;\n
    }\n
  } else {\n
    this.disappear();\n
    return;\n
  }\n
  this.topStyle.top = top + \'px\';\n
  this.topStyle.left = left + \'px\';\n
  this.topStyle.width = width + \'px\';\n
  this.topStyle.display = \'block\';\n
  this.leftStyle.top = top + \'px\';\n
  this.leftStyle.left = left + \'px\';\n
  this.leftStyle.height = height + \'px\';\n
  this.leftStyle.display = \'block\';\n
  var delta = Math.floor(this.settings.border.width / 2);\n
  this.bottomStyle.top = top + height - delta + \'px\';\n
  this.bottomStyle.left = left + \'px\';\n
  this.bottomStyle.width = width + \'px\';\n
  this.bottomStyle.display = \'block\';\n
  this.rightStyle.top = top + \'px\';\n
  this.rightStyle.left = left + width - delta + \'px\';\n
  this.rightStyle.height = height + 1 + \'px\';\n
  this.rightStyle.display = \'block\';\n
  if (Handsontable.mobileBrowser || (!this.hasSetting(this.settings.border.cornerVisible) || isPartRange.call(this))) {\n
    this.cornerStyle.display = \'none\';\n
  } else {\n
    this.cornerStyle.top = top + height - 4 + \'px\';\n
    this.cornerStyle.left = left + width - 4 + \'px\';\n
    this.cornerStyle.borderRightWidth = this.cornerDefaultStyle.borderWidth;\n
    this.cornerStyle.width = this.cornerDefaultStyle.width;\n
    this.cornerStyle.display = \'block\';\n
    if (toColumn === this.instance.getSetting(\'totalColumns\') - 1) {\n
      var trimmingContainer = dom.getTrimmingContainer(instance.wtTable.TABLE),\n
          cornerOverlappingContainer = toTD.offsetLeft + dom.outerWidth(toTD) >= dom.innerWidth(trimmingContainer);\n
      if (cornerOverlappingContainer) {\n
        this.cornerStyle.left = Math.floor(left + width - 3 - parseInt(this.cornerDefaultStyle.width) / 2) + "px";\n
        this.cornerStyle.borderRightWidth = 0;\n
      }\n
    }\n
  }\n
  if (Handsontable.mobileBrowser) {\n
    updateMultipleSelectionHandlesPosition.call(this, top, left, width, height);\n
  }\n
};\n
WalkontableBorder.prototype.disappear = function() {\n
  this.topStyle.display = \'none\';\n
  this.leftStyle.display = \'none\';\n
  this.bottomStyle.display = \'none\';\n
  this.rightStyle.display = \'none\';\n
  this.cornerStyle.display = \'none\';\n
  if (Handsontable.mobileBrowser) {\n
    this.selectionHandles.styles.topLeft.display = \'none\';\n
    this.selectionHandles.styles.bottomRight.display = \'none\';\n
  }\n
};\n
WalkontableBorder.prototype.hasSetting = function(setting) {\n
  if (typeof setting === \'function\') {\n
    return setting();\n
  }\n
  return !!setting;\n
};\n
;\n
window.WalkontableBorder = WalkontableBorder;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./../../../eventManager.js":45,"./cell/coords.js":9}],7:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableViewportColumnsCalculator: {get: function() {\n
      return WalkontableViewportColumnsCalculator;\n
    }},\n
  __esModule: {value: true}\n
});\n
var privatePool = new WeakMap();\n
var WalkontableViewportColumnsCalculator = function WalkontableViewportColumnsCalculator(viewportWidth, scrollOffset, totalColumns, columnWidthFn, overrideFn, onlyFullyVisible, stretchH) {\n
  privatePool.set(this, {\n
    viewportWidth: viewportWidth,\n
    scrollOffset: scrollOffset,\n
    totalColumns: totalColumns,\n
    columnWidthFn: columnWidthFn,\n
    overrideFn: overrideFn,\n
    onlyFullyVisible: onlyFullyVisible\n
  });\n
  this.count = 0;\n
  this.startColumn = null;\n
  this.endColumn = null;\n
  this.startPosition = null;\n
  this.stretchAllRatio = 0;\n
  this.stretchLastWidth = 0;\n
  this.stretch = stretchH;\n
  this.totalTargetWidth = 0;\n
  this.needVerifyLastColumnWidth = true;\n
  this.stretchAllColumnsWidth = [];\n
  this.calculate();\n
};\n
var $WalkontableViewportColumnsCalculator = WalkontableViewportColumnsCalculator;\n
($traceurRuntime.createClass)(WalkontableViewportColumnsCalculator, {\n
  calculate: function() {\n
    var sum = 0;\n
    var needReverse = true;\n
    var startPositions = [];\n
    var columnWidth;\n
    var priv = privatePool.get(this);\n
    var onlyFullyVisible = priv.onlyFullyVisible;\n
    var overrideFn = priv.overrideFn;\n
    var scrollOffset = priv.scrollOffset;\n
    var totalColumns = priv.totalColumns;\n
    var viewportWidth = priv.viewportWidth;\n
    for (var i = 0; i < totalColumns; i++) {\n
      columnWidth = this._getColumnWidth(i);\n
      if (sum <= scrollOffset && !onlyFullyVisible) {\n
        this.startColumn = i;\n
      }\n
      if (sum >= scrollOffset && sum + columnWidth <= scrollOffset + viewportWidth) {\n
        if (this.startColumn == null) {\n
          this.startColumn = i;\n
        }\n
        this.endColumn = i;\n
      }\n
      startPositions.push(sum);\n
      sum += columnWidth;\n
      if (!onlyFullyVisible) {\n
        this.endColumn = i;\n
      }\n
      if (sum >= scrollOffset + viewportWidth) {\n
        needReverse = false;\n
        break;\n
      }\n
    }\n
    if (this.endColumn === totalColumns - 1 && needReverse) {\n
      this.startColumn = this.endColumn;\n
      while (this.startColumn > 0) {\n
        var viewportSum = startPositions[this.endColumn] + columnWidth - startPositions[this.startColumn - 1];\n
        if (viewportSum <= viewportWidth || !onlyFullyVisible) {\n
          this.startColumn--;\n
        }\n
        if (viewportSum > viewportWidth) {\n
          break;\n
        }\n
      }\n
    }\n
    if (this.startColumn !== null && overrideFn) {\n
      overrideFn(this);\n
    }\n
    this.startPosition = startPositions[this.startColumn];\n
    if (this.startPosition == void 0) {\n
      this.startPosition = null;\n
    }\n
    if (this.startColumn !== null) {\n
      this.count = this.endColumn - this.startColumn + 1;\n
    }\n
  },\n
  refreshStretching: function(totalWidth) {\n
    var sumAll = 0;\n
    var columnWidth;\n
    var remainingSize;\n
    var priv = privatePool.get(this);\n
    var totalColumns = priv.totalColumns;\n
    for (var i = 0; i < totalColumns; i++) {\n
      columnWidth = this._getColumnWidth(i);\n
      sumAll += columnWidth;\n
    }\n
    this.totalTargetWidth = totalWidth;\n
    remainingSize = sumAll - totalWidth;\n
    if (this.stretch === \'all\' && remainingSize < 0) {\n
      this.stretchAllRatio = totalWidth / sumAll;\n
      this.stretchAllColumnsWidth = [];\n
      this.needVerifyLastColumnWidth = true;\n
    } else if (this.stretch === \'last\' && totalWidth !== Infinity) {\n
      this.stretchLastWidth = -remainingSize + this._getColumnWidth(totalColumns - 1);\n
    }\n
  },\n
  getStretchedColumnWidth: function(column, baseWidth) {\n
    var result = null;\n
    if (this.stretch === \'all\' && this.stretchAllRatio !== 0) {\n
      result = this._getStretchedAllColumnWidth(column, baseWidth);\n
    } else if (this.stretch === \'last\' && this.stretchLastWidth !== 0) {\n
      result = this._getStretchedLastColumnWidth(column);\n
    }\n
    return result;\n
  },\n
  _getStretchedAllColumnWidth: function(column, baseWidth) {\n
    var sumRatioWidth = 0;\n
    var priv = privatePool.get(this);\n
    var totalColumns = priv.totalColumns;\n
    if (!this.stretchAllColumnsWidth[column]) {\n
      this.stretchAllColumnsWidth[column] = Math.round(baseWidth * this.stretchAllRatio);\n
    }\n
    if (this.stretchAllColumnsWidth.length === totalColumns && this.needVerifyLastColumnWidth) {\n
      this.needVerifyLastColumnWidth = false;\n
      for (var i = 0; i < this.stretchAllColumnsWidth.length; i++) {\n
        sumRatioWidth += this.stretchAllColumnsWidth[i];\n
      }\n
      if (sumRatioWidth !== this.totalTargetWidth) {\n
        this.stretchAllColumnsWidth[this.stretchAllColumnsWidth.length - 1] += this.totalTargetWidth - sumRatioWidth;\n
      }\n
    }\n
    return this.stretchAllColumnsWidth[column];\n
  },\n
  _getStretchedLastColumnWidth: function(column) {\n
    var priv = privatePool.get(this);\n
    var totalColumns = priv.totalColumns;\n
    if (column === totalColumns - 1) {\n
      return this.stretchLastWidth;\n
    }\n
    return null;\n
  },\n
  _getColumnWidth: function(column) {\n
    var width = privatePool.get(this).columnWidthFn(column);\n
    if (width === undefined) {\n
      width = $WalkontableViewportColumnsCalculator.DEFAULT_WIDTH;\n
    }\n
    return width;\n
  }\n
}, {get DEFAULT_WIDTH() {\n
    return 50;\n
  }});\n
;\n
window.WalkontableViewportColumnsCalculator = WalkontableViewportColumnsCalculator;\n
\n
\n
//# \n
},{}],8:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableViewportRowsCalculator: {get: function() {\n
      return WalkontableViewportRowsCalculator;\n
    }},\n
  __esModule: {value: true}\n
});\n
var privatePool = new WeakMap();\n
var WalkontableViewportRowsCalculator = function WalkontableViewportRowsCalculator(viewportHeight, scrollOffset, totalRows, rowHeightFn, overrideFn, onlyFullyVisible) {\n
  privatePool.set(this, {\n
    viewportHeight: viewportHeight,\n
    scrollOffset: scrollOffset,\n
    totalRows: totalRows,\n
    rowHeightFn: rowHeightFn,\n
    overrideFn: overrideFn,\n
    onlyFullyVisible: onlyFullyVisible\n
  });\n
  this.count = 0;\n
  this.startRow = null;\n
  this.endRow = null;\n
  this.startPosition = null;\n
  this.calculate();\n
};\n
var $WalkontableViewportRowsCalculator = WalkontableViewportRowsCalculator;\n
($traceurRuntime.createClass)(WalkontableViewportRowsCalculator, {calculate: function() {\n
    var sum = 0;\n
    var needReverse = true;\n
    var startPositions = [];\n
    var priv = privatePool.get(this);\n
    var onlyFullyVisible = priv.onlyFullyVisible;\n
    var overrideFn = priv.overrideFn;\n
    var rowHeightFn = priv.rowHeightFn;\n
    var scrollOffset = priv.scrollOffset;\n
    var totalRows = priv.totalRows;\n
    var viewportHeight = priv.viewportHeight;\n
    for (var i = 0; i < totalRows; i++) {\n
      var rowHeight = rowHeightFn(i);\n
      if (rowHeight === undefined) {\n
        rowHeight = $WalkontableViewportRowsCalculator.DEFAULT_HEIGHT;\n
      }\n
      if (sum <= scrollOffset && !onlyFullyVisible) {\n
        this.startRow = i;\n
      }\n
      if (sum >= scrollOffset && sum + rowHeight <= scrollOffset + viewportHeight) {\n
        if (this.startRow === null) {\n
          this.startRow = i;\n
        }\n
        this.endRow = i;\n
      }\n
      startPositions.push(sum);\n
      sum += rowHeight;\n
      if (!onlyFullyVisible) {\n
        this.endRow = i;\n
      }\n
      if (sum >= scrollOffset + viewportHeight) {\n
        needReverse = false;\n
        break;\n
      }\n
    }\n
    if (this.endRow === totalRows - 1 && needReverse) {\n
      this.startRow = this.endRow;\n
      while (this.startRow > 0) {\n
        var viewportSum = startPositions[this.endRow] + rowHeight - startPositions[this.startRow - 1];\n
        if (viewportSum <= viewportHeight || !onlyFullyVisible) {\n
          this.startRow--;\n
        }\n
        if (viewportSum >= viewportHeight) {\n
          break;\n
        }\n
      }\n
    }\n
    if (this.startRow !== null && overrideFn) {\n
      overrideFn(this);\n
    }\n
    this.startPosition = startPositions[this.startRow];\n
    if (this.startPosition == void 0) {\n
      this.startPosition = null;\n
    }\n
    if (this.startRow !== null) {\n
      this.count = this.endRow - this.startRow + 1;\n
    }\n
  }}, {get DEFAULT_HEIGHT() {\n
    return 23;\n
  }});\n
;\n
window.WalkontableViewportRowsCalculator = WalkontableViewportRowsCalculator;\n
\n
\n
//# \n
},{}],9:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableCellCoords: {get: function() {\n
      return WalkontableCellCoords;\n
    }},\n
  __esModule: {value: true}\n
});\n
var WalkontableCellCoords = function WalkontableCellCoords(row, col) {\n
  if (typeof row !== \'undefined\' && typeof col !== \'undefined\') {\n
    this.row = row;\n
    this.col = col;\n
  } else {\n
    this.row = null;\n
    this.col = null;\n
  }\n
};\n
($traceurRuntime.createClass)(WalkontableCellCoords, {\n
  isValid: function(wotInstance) {\n
    if (this.row < 0 || this.col < 0) {\n
      return false;\n
    }\n
    if (this.row >= wotInstance.getSetting(\'totalRows\') || this.col >= wotInstance.getSetting(\'totalColumns\')) {\n
      return false;\n
    }\n
    return true;\n
  },\n
  isEqual: function(cellCoords) {\n
    if (cellCoords === this) {\n
      return true;\n
    }\n
    return this.row === cellCoords.row && this.col === cellCoords.col;\n
  },\n
  isSouthEastOf: function(testedCoords) {\n
    return this.row >= testedCoords.row && this.col >= testedCoords.col;\n
  },\n
  isNorthWestOf: function(testedCoords) {\n
    return this.row <= testedCoords.row && this.col <= testedCoords.col;\n
  },\n
  isSouthWestOf: function(testedCoords) {\n
    return this.row >= testedCoords.row && this.col <= testedCoords.col;\n
  },\n
  isNorthEastOf: function(testedCoords) {\n
    return this.row <= testedCoords.row && this.col >= testedCoords.col;\n
  }\n
}, {});\n
;\n
window.WalkontableCellCoords = WalkontableCellCoords;\n
\n
\n
//# \n
},{}],10:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableCellRange: {get: function() {\n
      return WalkontableCellRange;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_cell_47_coords_46_js__;\n
var WalkontableCellCoords = ($___46__46__47_cell_47_coords_46_js__ = require("./../cell/coords.js"), $___46__46__47_cell_47_coords_46_js__ && $___46__46__47_cell_47_coords_46_js__.__esModule && $___46__46__47_cell_47_coords_46_js__ || {default: $___46__46__47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = function WalkontableCellRange(highlight, from, to) {\n
  this.highlight = highlight;\n
  this.from = from;\n
  this.to = to;\n
};\n
var $WalkontableCellRange = WalkontableCellRange;\n
($traceurRuntime.createClass)(WalkontableCellRange, {\n
  isValid: function(wotInstance) {\n
    return this.from.isValid(wotInstance) && this.to.isValid(wotInstance);\n
  },\n
  isSingle: function() {\n
    return this.from.row === this.to.row && this.from.col === this.to.col;\n
  },\n
  getHeight: function() {\n
    return Math.max(this.from.row, this.to.row) - Math.min(this.from.row, this.to.row) + 1;\n
  },\n
  getWidth: function() {\n
    return Math.max(this.from.col, this.to.col) - Math.min(this.from.col, this.to.col) + 1;\n
  },\n
  includes: function(cellCoords) {\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    if (cellCoords.row < 0) {\n
      cellCoords.row = 0;\n
    }\n
    if (cellCoords.col < 0) {\n
      cellCoords.col = 0;\n
    }\n
    return topLeft.row <= cellCoords.row && bottomRight.row >= cellCoords.row && topLeft.col <= cellCoords.col && bottomRight.col >= cellCoords.col;\n
  },\n
  includesRange: function(testedRange) {\n
    return this.includes(testedRange.getTopLeftCorner()) && this.includes(testedRange.getBottomRightCorner());\n
  },\n
  isEqual: function(testedRange) {\n
    return (Math.min(this.from.row, this.to.row) == Math.min(testedRange.from.row, testedRange.to.row)) && (Math.max(this.from.row, this.to.row) == Math.max(testedRange.from.row, testedRange.to.row)) && (Math.min(this.from.col, this.to.col) == Math.min(testedRange.from.col, testedRange.to.col)) && (Math.max(this.from.col, this.to.col) == Math.max(testedRange.from.col, testedRange.to.col));\n
  },\n
  overlaps: function(testedRange) {\n
    return testedRange.isSouthEastOf(this.getTopLeftCorner()) && testedRange.isNorthWestOf(this.getBottomRightCorner());\n
  },\n
  isSouthEastOf: function(testedCoords) {\n
    return this.getTopLeftCorner().isSouthEastOf(testedCoords) || this.getBottomRightCorner().isSouthEastOf(testedCoords);\n
  },\n
  isNorthWestOf: function(testedCoords) {\n
    return this.getTopLeftCorner().isNorthWestOf(testedCoords) || this.getBottomRightCorner().isNorthWestOf(testedCoords);\n
  },\n
  expand: function(cellCoords) {\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    if (cellCoords.row < topLeft.row || cellCoords.col < topLeft.col || cellCoords.row > bottomRight.row || cellCoords.col > bottomRight.col) {\n
      this.from = new WalkontableCellCoords(Math.min(topLeft.row, cellCoords.row), Math.min(topLeft.col, cellCoords.col));\n
      this.to = new WalkontableCellCoords(Math.max(bottomRight.row, cellCoords.row), Math.max(bottomRight.col, cellCoords.col));\n
      return true;\n
    }\n
    return false;\n
  },\n
  expandByRange: function(expandingRange) {\n
    if (this.includesRange(expandingRange) || !this.overlaps(expandingRange)) {\n
      return false;\n
    }\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    var topRight = this.getTopRightCorner();\n
    var bottomLeft = this.getBottomLeftCorner();\n
    var expandingTopLeft = expandingRange.getTopLeftCorner();\n
    var expandingBottomRight = expandingRange.getBottomRightCorner();\n
    var resultTopRow = Math.min(topLeft.row, expandingTopLeft.row);\n
    var resultTopCol = Math.min(topLeft.col, expandingTopLeft.col);\n
    var resultBottomRow = Math.max(bottomRight.row, expandingBottomRight.row);\n
    var resultBottomCol = Math.max(bottomRight.col, expandingBottomRight.col);\n
    var finalFrom = new WalkontableCellCoords(resultTopRow, resultTopCol),\n
        finalTo = new WalkontableCellCoords(resultBottomRow, resultBottomCol);\n
    var isCorner = new $WalkontableCellRange(finalFrom, finalFrom, finalTo).isCorner(this.from, expandingRange),\n
        onlyMerge = expandingRange.isEqual(new $WalkontableCellRange(finalFrom, finalFrom, finalTo));\n
    if (isCorner && !onlyMerge) {\n
      if (this.from.col > finalFrom.col) {\n
        finalFrom.col = resultBottomCol;\n
        finalTo.col = resultTopCol;\n
      }\n
      if (this.from.row > finalFrom.row) {\n
        finalFrom.row = resultBottomRow;\n
        finalTo.row = resultTopRow;\n
      }\n
    }\n
    this.from = finalFrom;\n
    this.to = finalTo;\n
    return true;\n
  },\n
  getDirection: function() {\n
    if (this.from.isNorthWestOf(this.to)) {\n
      return \'NW-SE\';\n
    } else if (this.from.isNorthEastOf(this.to)) {\n
      return \'NE-SW\';\n
    } else if (this.from.isSouthEastOf(this.to)) {\n
      return \'SE-NW\';\n
    } else if (this.from.isSouthWestOf(this.to)) {\n
      return \'SW-NE\';\n
    }\n
  },\n
  setDirection: function(direction) {\n
    switch (direction) {\n
      case \'NW-SE\':\n
        this.from = this.getTopLeftCorner();\n
        this.to = this.getBottomRightCorner();\n
        break;\n
      case \'NE-SW\':\n
        this.from = this.getTopRightCorner();\n
        this.to = this.getBottomLeftCorner();\n
        break;\n
      case \'SE-NW\':\n
        this.from = this.getBottomRightCorner();\n
        this.to = this.getTopLeftCorner();\n
        break;\n
      case \'SW-NE\':\n
        this.from = this.getBottomLeftCorner();\n
        this.to = this.getTopRightCorner();\n
        break;\n
    }\n
  },\n
  getTopLeftCorner: function() {\n
    return new WalkontableCellCoords(Math.min(this.from.row, this.to.row), Math.min(this.from.col, this.to.col));\n
  },\n
  getBottomRightCorner: function() {\n
    return new WalkontableCellCoords(Math.max(this.from.row, this.to.row), Math.max(this.from.col, this.to.col));\n
  },\n
  getTopRightCorner: function() {\n
    return new WalkontableCellCoords(Math.min(this.from.row, this.to.row), Math.max(this.from.col, this.to.col));\n
  },\n
  getBottomLeftCorner: function() {\n
    return new WalkontableCellCoords(Math.max(this.from.row, this.to.row), Math.min(this.from.col, this.to.col));\n
  },\n
  isCorner: function(coords, expandedRange) {\n
    if (expandedRange) {\n
      if (expandedRange.includes(coords)) {\n
        if (this.getTopLeftCorner().isEqual(new WalkontableCellCoords(expandedRange.from.row, expandedRange.from.col)) || this.getTopRightCorner().isEqual(new WalkontableCellCoords(expandedRange.from.row, expandedRange.to.col)) || this.getBottomLeftCorner().isEqual(new WalkontableCellCoords(expandedRange.to.row, expandedRange.from.col)) || this.getBottomRightCorner().isEqual(new WalkontableCellCoords(expandedRange.to.row, expandedRange.to.col))) {\n
          return true;\n
        }\n
      }\n
    }\n
    return coords.isEqual(this.getTopLeftCorner()) || coords.isEqual(this.getTopRightCorner()) || coords.isEqual(this.getBottomLeftCorner()) || coords.isEqual(this.getBottomRightCorner());\n
  },\n
  getOppositeCorner: function(coords, expandedRange) {\n
    if (!(coords instanceof WalkontableCellCoords)) {\n
      return false;\n
    }\n
    if (expandedRange) {\n
      if (expandedRange.includes(coords)) {\n
        if (this.getTopLeftCorner().isEqual(new WalkontableCellCoords(expandedRange.from.row, expandedRange.from.col))) {\n
          return this.getBottomRightCorner();\n
        }\n
        if (this.getTopRightCorner().isEqual(new WalkontableCellCoords(expandedRange.from.row, expandedRange.to.col))) {\n
          return this.getBottomLeftCorner();\n
        }\n
        if (this.getBottomLeftCorner().isEqual(new WalkontableCellCoords(expandedRange.to.row, expandedRange.from.col))) {\n
          return this.getTopRightCorner();\n
        }\n
        if (this.getBottomRightCorner().isEqual(new WalkontableCellCoords(expandedRange.to.row, expandedRange.to.col))) {\n
          return this.getTopLeftCorner();\n
        }\n
      }\n
    }\n
    if (coords.isEqual(this.getBottomRightCorner())) {\n
      return this.getTopLeftCorner();\n
    } else if (coords.isEqual(this.getTopLeftCorner())) {\n
      return this.getBottomRightCorner();\n
    } else if (coords.isEqual(this.getTopRightCorner())) {\n
      return this.getBottomLeftCorner();\n
    } else if (coords.isEqual(this.getBottomLeftCorner())) {\n
      return this.getTopRightCorner();\n
    }\n
  },\n
  getBordersSharedWith: function(range) {\n
    if (!this.includesRange(range)) {\n
      return [];\n
    }\n
    var thisBorders = {\n
      top: Math.min(this.from.row, this.to.row),\n
      bottom: Math.max(this.from.row, this.to.row),\n
      left: Math.min(this.from.col, this.to.col),\n
      right: Math.max(this.from.col, this.to.col)\n
    };\n
    var rangeBorders = {\n
      top: Math.min(range.from.row, range.to.row),\n
      bottom: Math.max(range.from.row, range.to.row),\n
      left: Math.min(range.from.col, range.to.col),\n
      right: Math.max(range.from.col, range.to.col)\n
    };\n
    var result = [];\n
    if (thisBorders.top == rangeBorders.top) {\n
      result.push(\'top\');\n
    }\n
    if (thisBorders.right == rangeBorders.right) {\n
      result.push(\'right\');\n
    }\n
    if (thisBorders.bottom == rangeBorders.bottom) {\n
      result.push(\'bottom\');\n
    }\n
    if (thisBorders.left == rangeBorders.left) {\n
      result.push(\'left\');\n
    }\n
    return result;\n
  },\n
  getInner: function() {\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    var out = [];\n
    for (var r = topLeft.row; r <= bottomRight.row; r++) {\n
      for (var c = topLeft.col; c <= bottomRight.col; c++) {\n
        if (!(this.from.row === r && this.from.col === c) && !(this.to.row === r && this.to.col === c)) {\n
          out.push(new WalkontableCellCoords(r, c));\n
        }\n
      }\n
    }\n
    return out;\n
  },\n
  getAll: function() {\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    var out = [];\n
    for (var r = topLeft.row; r <= bottomRight.row; r++) {\n
      for (var c = topLeft.col; c <= bottomRight.col; c++) {\n
        if (topLeft.row === r && topLeft.col === c) {\n
          out.push(topLeft);\n
        } else if (bottomRight.row === r && bottomRight.col === c) {\n
          out.push(bottomRight);\n
        } else {\n
          out.push(new WalkontableCellCoords(r, c));\n
        }\n
      }\n
    }\n
    return out;\n
  },\n
  forAll: function(callback) {\n
    var topLeft = this.getTopLeftCorner();\n
    var bottomRight = this.getBottomRightCorner();\n
    for (var r = topLeft.row; r <= bottomRight.row; r++) {\n
      for (var c = topLeft.col; c <= bottomRight.col; c++) {\n
        var breakIteration = callback(r, c);\n
        if (breakIteration === false) {\n
          return;\n
        }\n
      }\n
    }\n
  }\n
}, {});\n
;\n
window.WalkontableCellRange = WalkontableCellRange;\n
\n
\n
//# \n
},{"./../cell/coords.js":9}],11:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  Walkontable: {get: function() {\n
      return Walkontable;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47_helpers_46_js__,\n
    $__event_46_js__,\n
    $__overlays_46_js__,\n
    $__scroll_46_js__,\n
    $__settings_46_js__,\n
    $__table_46_js__,\n
    $__viewport_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var randomString = ($___46__46__47__46__46__47__46__46__47_helpers_46_js__ = require("./../../../helpers.js"), $___46__46__47__46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_helpers_46_js__}).randomString;\n
var WalkontableEvent = ($__event_46_js__ = require("./event.js"), $__event_46_js__ && $__event_46_js__.__esModule && $__event_46_js__ || {default: $__event_46_js__}).WalkontableEvent;\n
var WalkontableOverlays = ($__overlays_46_js__ = require("./overlays.js"), $__overlays_46_js__ && $__overlays_46_js__.__esModule && $__overlays_46_js__ || {default: $__overlays_46_js__}).WalkontableOverlays;\n
var WalkontableScroll = ($__scroll_46_js__ = require("./scroll.js"), $__scroll_46_js__ && $__scroll_46_js__.__esModule && $__scroll_46_js__ || {default: $__scroll_46_js__}).WalkontableScroll;\n
var WalkontableSettings = ($__settings_46_js__ = require("./settings.js"), $__settings_46_js__ && $__settings_46_js__.__esModule && $__settings_46_js__ || {default: $__settings_46_js__}).WalkontableSettings;\n
var WalkontableTable = ($__table_46_js__ = require("./table.js"), $__table_46_js__ && $__table_46_js__.__esModule && $__table_46_js__ || {default: $__table_46_js__}).WalkontableTable;\n
var WalkontableViewport = ($__viewport_46_js__ = require("./viewport.js"), $__viewport_46_js__ && $__viewport_46_js__.__esModule && $__viewport_46_js__ || {default: $__viewport_46_js__}).WalkontableViewport;\n
var Walkontable = function Walkontable(settings) {\n
  var originalHeaders = [];\n
  this.guid = \'wt_\' + randomString();\n
  if (settings.cloneSource) {\n
    this.cloneSource = settings.cloneSource;\n
    this.cloneOverlay = settings.cloneOverlay;\n
    this.wtSettings = settings.cloneSource.wtSettings;\n
    this.wtTable = new WalkontableTable(this, settings.table, settings.wtRootElement);\n
    this.wtScroll = new WalkontableScroll(this);\n
    this.wtViewport = settings.cloneSource.wtViewport;\n
    this.wtEvent = new WalkontableEvent(this);\n
    this.selections = this.cloneSource.selections;\n
  } else {\n
    this.wtSettings = new WalkontableSettings(this, settings);\n
    this.wtTable = new WalkontableTable(this, settings.table);\n
    this.wtScroll = new WalkontableScroll(this);\n
    this.wtViewport = new WalkontableViewport(this);\n
    this.wtEvent = new WalkontableEvent(this);\n
    this.selections = this.getSetting(\'selections\');\n
    this.wtOverlays = new WalkontableOverlays(this);\n
  }\n
  if (this.wtTable.THEAD.childNodes.length && this.wtTable.THEAD.childNodes[0].childNodes.length) {\n
    for (var c = 0,\n
        clen = this.wtTable.THEAD.childNodes[0].childNodes.length; c < clen; c++) {\n
      originalHeaders.push(this.wtTable.THEAD.childNodes[0].childNodes[c].innerHTML);\n
    }\n
    if (!this.getSetting(\'columnHeaders\').length) {\n
      this.update(\'columnHeaders\', [function(column, TH) {\n
        dom.fastInnerText(TH, originalHeaders[column]);\n
      }]);\n
    }\n
  }\n
  this.drawn = false;\n
  this.drawInterrupted = false;\n
};\n
($traceurRuntime.createClass)(Walkontable, {\n
  draw: function() {\n
    var fastDraw = arguments[0] !== (void 0) ? arguments[0] : false;\n
    this.drawInterrupted = false;\n
    if (!fastDraw && !dom.isVisible(this.wtTable.TABLE)) {\n
      this.drawInterrupted = true;\n
    } else {\n
      this.wtTable.draw(fastDraw);\n
    }\n
    return this;\n
  },\n
  getCell: function(coords) {\n
    var topmost = arguments[1] !== (void 0) ? arguments[1] : false;\n
    if (!topmost) {\n
      return this.wtTable.getCell(coords);\n
    }\n
    var fixedRows = this.wtSettings.getSetting(\'fixedRowsTop\');\n
    var fixedColumns = this.wtSettings.getSetting(\'fixedColumnsLeft\');\n
    if (coords.row < fixedRows && coords.col < fixedColumns) {\n
      return this.wtOverlays.topLeftCornerOverlay.clone.wtTable.getCell(coords);\n
    } else if (coords.row < fixedRows) {\n
      return this.wtOverlays.topOverlay.clone.wtTable.getCell(coords);\n
    } else if (coords.col < fixedColumns) {\n
      return this.wtOverlays.leftOverlay.clone.wtTable.getCell(coords);\n
    }\n
    return this.wtTable.getCell(coords);\n
  },\n
  update: function(settings, value) {\n
    return this.wtSettings.update(settings, value);\n
  },\n
  scrollVertical: function(row) {\n
    this.wtOverlays.topOverlay.scrollTo(row);\n
    this.getSetting(\'onScrollVertically\');\n
    return this;\n
  },\n
  scrollHorizontal: function(column) {\n
    this.wtOverlays.leftOverlay.scrollTo(column);\n
    this.getSetting(\'onScrollHorizontally\');\n
    return this;\n
  },\n
  scrollViewport: function(coords) {\n
    this.wtScroll.scrollViewport(coords);\n
    return this;\n
  },\n
  getViewport: function() {\n
    return [this.wtTable.getFirstVisibleRow(), this.wtTable.getFirstVisibleColumn(), this.wtTable.getLastVisibleRow(), this.wtTable.getLastVisibleColumn()];\n
  },\n
  getOverlayName: function() {\n
    return this.cloneOverlay ? this.cloneOverlay.type : \'master\';\n
  },\n
  getSetting: function(key, param1, param2, param3, param4) {\n
    return this.wtSettings.getSetting(key, param1, param2, param3, param4);\n
  },\n
  hasSetting: function(key) {\n
    return this.wtSettings.has(key);\n
  },\n
  destroy: function() {\n
    this.wtOverlays.destroy();\n
    if (this.wtEvent) {\n
      this.wtEvent.destroy();\n
    }\n
  }\n
}, {});\n
;\n
window.Walkontable = Walkontable;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./../../../helpers.js":46,"./event.js":12,"./overlays.js":20,"./scroll.js":21,"./settings.js":23,"./table.js":24,"./viewport.js":26}],12:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableEvent: {get: function() {\n
      return WalkontableEvent;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47_eventManager_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47__46__46__47_eventManager_46_js__ = require("./../../../eventManager.js"), $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
function WalkontableEvent(instance) {\n
  var that = this;\n
  var eventManager = eventManagerObject(instance);\n
  this.instance = instance;\n
  var dblClickOrigin = [null, null];\n
  this.dblClickTimeout = [null, null];\n
  var onMouseDown = function(event) {\n
    var cell = that.parentCell(event.realTarget);\n
    if (dom.hasClass(event.realTarget, \'corner\')) {\n
      that.instance.getSetting(\'onCellCornerMouseDown\', event, event.realTarget);\n
    } else if (cell.TD) {\n
      if (that.instance.hasSetting(\'onCellMouseDown\')) {\n
        that.instance.getSetting(\'onCellMouseDown\', event, cell.coords, cell.TD, that.instance);\n
      }\n
    }\n
    if (event.button !== 2) {\n
      if (cell.TD) {\n
        dblClickOrigin[0] = cell.TD;\n
        clearTimeout(that.dblClickTimeout[0]);\n
        that.dblClickTimeout[0] = setTimeout(function() {\n
          dblClickOrigin[0] = null;\n
        }, 1000);\n
      }\n
    }\n
  };\n
  var onTouchMove = function(event) {\n
    that.instance.touchMoving = true;\n
  };\n
  var longTouchTimeout;\n
  var onTouchStart = function(event) {\n
    var container = this;\n
    eventManager.addEventListener(this, \'touchmove\', onTouchMove);\n
    that.checkIfTouchMove = setTimeout(function() {\n
      if (that.instance.touchMoving === true) {\n
        that.instance.touchMoving = void 0;\n
        eventManager.removeEventListener("touchmove", onTouchMove, false);\n
        return;\n
      } else {\n
        onMouseDown(event);\n
      }\n
    }, 30);\n
  };\n
  var lastMouseOver;\n
  var onMouseOver = function(event) {\n
    var table,\n
        td;\n
    if (that.instance.hasSetting(\'onCellMouseOver\')) {\n
      table = that.instance.wtTable.TABLE;\n
      td = dom.closest(event.realTarget, [\'TD\', \'TH\'], table);\n
      if (td && td !== lastMouseOver && dom.isChildOf(td, table)) {\n
        lastMouseOver = td;\n
        that.instance.getSetting(\'onCellMouseOver\', event, that.instance.wtTable.getCoords(td), td, that.instance);\n
      }\n
    }\n
  };\n
  var onMouseUp = function(event) {\n
    if (event.button !== 2) {\n
      var cell = that.parentCell(event.realTarget);\n
      if (cell.TD === dblClickOrigin[0] && cell.TD === dblClickOrigin[1]) {\n
        if (dom.hasClass(event.realTarget, \'corner\')) {\n
          that.instance.getSetting(\'onCellCornerDblClick\', event, cell.coords, cell.TD, that.instance);\n
        } else {\n
          that.instance.getSetting(\'onCellDblClick\', event, cell.coords, cell.TD, that.instance);\n
        }\n
        dblClickOrigin[0] = null;\n
        dblClickOrigin[1] = null;\n
      } else if (cell.TD === dblClickOrigin[0]) {\n
        dblClickOrigin[1] = cell.TD;\n
        clearTimeout(that.dblClickTimeout[1]);\n
        that.dblClickTimeout[1] = setTimeout(function() {\n
          dblClickOrigin[1] = null;\n
        }, 500);\n
      }\n
    }\n
  };\n
  var onTouchEnd = function(event) {\n
    clearTimeout(longTouchTimeout);\n
    event.preventDefault();\n
    onMouseUp(event);\n
  };\n
  eventManager.addEventListener(this.instance.wtTable.holder, \'mousedown\', onMouseDown);\n
  eventManager.addEventListener(this.instance.wtTable.TABLE, \'mouseover\', onMouseOver);\n
  eventManager.addEventListener(this.instance.wtTable.holder, \'mouseup\', onMouseUp);\n
  if (this.instance.wtTable.holder.parentNode.parentNode && Handsontable.mobileBrowser && !that.instance.wtTable.isWorkingOnClone()) {\n
    var classSelector = "." + this.instance.wtTable.holder.parentNode.className.split(" ").join(".");\n
    eventManager.addEventListener(this.instance.wtTable.holder, \'touchstart\', function(event) {\n
      that.instance.touchApplied = true;\n
      if (dom.isChildOf(event.target, classSelector)) {\n
        onTouchStart.call(event.target, event);\n
      }\n
    });\n
    eventManager.addEventListener(this.instance.wtTable.holder, \'touchend\', function(event) {\n
      that.instance.touchApplied = false;\n
      if (dom.isChildOf(event.target, classSelector)) {\n
        onTouchEnd.call(event.target, event);\n
      }\n
    });\n
    if (!that.instance.momentumScrolling) {\n
      that.instance.momentumScrolling = {};\n
    }\n
    eventManager.addEventListener(this.instance.wtTable.holder, \'scroll\', function(event) {\n
      clearTimeout(that.instance.momentumScrolling._timeout);\n
      if (!that.instance.momentumScrolling.ongoing) {\n
        that.instance.getSetting(\'onBeforeTouchScroll\');\n
      }\n
      that.instance.momentumScrolling.ongoing = true;\n
      that.instance.momentumScrolling._timeout = setTimeout(function() {\n
        if (!that.instance.touchApplied) {\n
          that.instance.momentumScrolling.ongoing = false;\n
          that.instance.getSetting(\'onAfterMomentumScroll\');\n
        }\n
      }, 200);\n
    });\n
  }\n
  eventManager.addEventListener(window, \'resize\', function() {\n
    that.instance.draw();\n
  });\n
  this.destroy = function() {\n
    clearTimeout(this.dblClickTimeout[0]);\n
    clearTimeout(this.dblClickTimeout[1]);\n
    eventManager.clear();\n
  };\n
}\n
WalkontableEvent.prototype.parentCell = function(elem) {\n
  var cell = {};\n
  var TABLE = this.instance.wtTable.TABLE;\n
  var TD = dom.closest(elem, [\'TD\', \'TH\'], TABLE);\n
  if (TD && dom.isChildOf(TD, TABLE)) {\n
    cell.coords = this.instance.wtTable.getCoords(TD);\n
    cell.TD = TD;\n
  } else if (dom.hasClass(elem, \'wtBorder\') && dom.hasClass(elem, \'current\')) {\n
    cell.coords = this.instance.selections.current.cellRange.highlight;\n
    cell.TD = this.instance.wtTable.getCell(cell.coords);\n
  } else if (dom.hasClass(elem, \'wtBorder\') && dom.hasClass(elem, \'area\')) {\n
    if (this.instance.selections.area.cellRange) {\n
      cell.coords = this.instance.selections.area.cellRange.to;\n
      cell.TD = this.instance.wtTable.getCell(cell.coords);\n
    }\n
  }\n
  return cell;\n
};\n
;\n
window.WalkontableEvent = WalkontableEvent;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./../../../eventManager.js":45}],13:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableColumnFilter: {get: function() {\n
      return WalkontableColumnFilter;\n
    }},\n
  __esModule: {value: true}\n
});\n
var WalkontableColumnFilter = function WalkontableColumnFilter(offset, total, countTH) {\n
  this.offset = offset;\n
  this.total = total;\n
  this.countTH = countTH;\n
};\n
($traceurRuntime.createClass)(WalkontableColumnFilter, {\n
  offsetted: function(index) {\n
    return index + this.offset;\n
  },\n
  unOffsetted: function(index) {\n
    return index - this.offset;\n
  },\n
  renderedToSource: function(index) {\n
    return this.offsetted(index);\n
  },\n
  sourceToRendered: function(index) {\n
    return this.unOffsetted(index);\n
  },\n
  offsettedTH: function(index) {\n
    return index - this.countTH;\n
  },\n
  unOffsettedTH: function(index) {\n
    return index + this.countTH;\n
  },\n
  visibleRowHeadedColumnToSourceColumn: function(index) {\n
    return this.renderedToSource(this.offsettedTH(index));\n
  },\n
  sourceColumnToVisibleRowHeadedColumn: function(index) {\n
    return this.unOffsettedTH(this.sourceToRendered(index));\n
  }\n
}, {});\n
;\n
window.WalkontableColumnFilter = WalkontableColumnFilter;\n
\n
\n
//# \n
},{}],14:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableRowFilter: {get: function() {\n
      return WalkontableRowFilter;\n
    }},\n
  __esModule: {value: true}\n
});\n
var WalkontableRowFilter = function WalkontableRowFilter(offset, total, countTH) {\n
  this.offset = offset;\n
  this.total = total;\n
  this.countTH = countTH;\n
};\n
($traceurRuntime.createClass)(WalkontableRowFilter, {\n
  offsetted: function(index) {\n
    return index + this.offset;\n
  },\n
  unOffsetted: function(index) {\n
    return index - this.offset;\n
  },\n
  renderedToSource: function(index) {\n
    return this.offsetted(index);\n
  },\n
  sourceToRendered: function(index) {\n
    return this.unOffsetted(index);\n
  },\n
  offsettedTH: function(index) {\n
    return index - this.countTH;\n
  },\n
  unOffsettedTH: function(index) {\n
    return index + this.countTH;\n
  },\n
  visibleColHeadedRowToSourceRow: function(index) {\n
    return this.renderedToSource(this.offsettedTH(index));\n
  },\n
  sourceRowToVisibleColHeadedRow: function(index) {\n
    return this.unOffsettedTH(this.sourceToRendered(index));\n
  }\n
}, {});\n
;\n
window.WalkontableRowFilter = WalkontableRowFilter;\n
\n
\n
//# \n
},{}],15:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableOverlay: {get: function() {\n
      return WalkontableOverlay;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../../dom.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var defineGetter = ($___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__ = require("./../../../../helpers.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_helpers_46_js__}).defineGetter;\n
var eventManagerObject = ($___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__ = require("./../../../../eventManager.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var WalkontableOverlay = function WalkontableOverlay(wotInstance) {\n
  defineGetter(this, \'wot\', wotInstance, {writable: false});\n
  this.instance = this.wot;\n
  this.type = \'\';\n
  this.TABLE = this.wot.wtTable.TABLE;\n
  this.hider = this.wot.wtTable.hider;\n
  this.spreader = this.wot.wtTable.spreader;\n
  this.holder = this.wot.wtTable.holder;\n
  this.wtRootElement = this.wot.wtTable.wtRootElement;\n
  this.trimmingContainer = dom.getTrimmingContainer(this.hider.parentNode.parentNode);\n
  this.mainTableScrollableElement = dom.getScrollableElement(this.wot.wtTable.TABLE);\n
  this.needFullRender = this.isShouldBeFullyRendered();\n
};\n
var $WalkontableOverlay = WalkontableOverlay;\n
($traceurRuntime.createClass)(WalkontableOverlay, {\n
  isShouldBeFullyRendered: function() {\n
    return true;\n
  },\n
  makeClone: function(direction) {\n
    if ($WalkontableOverlay.CLONE_TYPES.indexOf(direction) === -1) {\n
      throw new Error(\'Clone type "\' + direction + \'" is not supported.\');\n
    }\n
    var clone = document.createElement(\'DIV\');\n
    var clonedTable = document.createElement(\'TABLE\');\n
    clone.className = \'ht_clone_\' + direction + \' handsontable\';\n
    clone.style.position = \'absolute\';\n
    clone.style.top = 0;\n
    clone.style.left = 0;\n
    clone.style.overflow = \'hidden\';\n
    clonedTable.className = this.wot.wtTable.TABLE.className;\n
    clone.appendChild(clonedTable);\n
    this.type = direction;\n
    this.wot.wtTable.wtRootElement.parentNode.appendChild(clone);\n
    return new Walkontable({\n
      cloneSource: this.wot,\n
      cloneOverlay: this,\n
      table: clonedTable\n
    });\n
  },\n
  refresh: function() {\n
    var fastDraw = arguments[0] !== (void 0) ? arguments[0] : false;\n
    var nextCycleRenderFlag = this.isShouldBeFullyRendered();\n
    if (this.needFullRender || nextCycleRenderFlag) {\n
      if (this.applyToDOM) {\n
        this.applyToDOM();\n
      }\n
      if (this.clone) {\n
        this.clone.draw(fastDraw);\n
      }\n
    }\n
    this.needFullRender = nextCycleRenderFlag;\n
  },\n
  destroy: function() {\n
    eventManagerObject(this.clone).clear();\n
  }\n
}, {\n
  get CLONE_TOP() {\n
    return \'top\';\n
  },\n
  get CLONE_LEFT() {\n
    return \'left\';\n
  },\n
  get CLONE_CORNER() {\n
    return \'corner\';\n
  },\n
  get CLONE_DEBUG() {\n
    return \'debug\';\n
  },\n
  get CLONE_TYPES() {\n
    return [$WalkontableOverlay.CLONE_TOP, $WalkontableOverlay.CLONE_LEFT, $WalkontableOverlay.CLONE_CORNER, $WalkontableOverlay.CLONE_DEBUG];\n
  }\n
});\n
;\n
window.WalkontableOverlay = WalkontableOverlay;\n
\n
\n
//# \n
},{"./../../../../dom.js":31,"./../../../../eventManager.js":45,"./../../../../helpers.js":46}],16:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableCornerOverlay: {get: function() {\n
      return WalkontableCornerOverlay;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___95_base_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../../dom.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableOverlay = ($___95_base_46_js__ = require("./_base.js"), $___95_base_46_js__ && $___95_base_46_js__.__esModule && $___95_base_46_js__ || {default: $___95_base_46_js__}).WalkontableOverlay;\n
var WalkontableCornerOverlay = function WalkontableCornerOverlay(wotInstance) {\n
  $traceurRuntime.superConstructor($WalkontableCornerOverlay).call(this, wotInstance);\n
  this.clone = this.makeClone(WalkontableOverlay.CLONE_CORNER);\n
};\n
var $WalkontableCornerOverlay = WalkontableCornerOverlay;\n
($traceurRuntime.createClass)(WalkontableCornerOverlay, {resetFixedPosition: function() {\n
    if (!this.wot.wtTable.holder.parentNode) {\n
      return;\n
    }\n
    var elem = this.clone.wtTable.holder.parentNode;\n
    var tableHeight;\n
    var tableWidth;\n
    if (this.trimmingContainer === window) {\n
      var box = this.wot.wtTable.hider.getBoundingClientRect();\n
      var top = Math.ceil(box.top);\n
      var left = Math.ceil(box.left);\n
      var bottom = Math.ceil(box.bottom);\n
      var right = Math.ceil(box.right);\n
      var finalLeft;\n
      var finalTop;\n
      if (left < 0 && (right - elem.offsetWidth) > 0) {\n
        finalLeft = -left + \'px\';\n
      } else {\n
        finalLeft = \'0\';\n
      }\n
      if (top < 0 && (bottom - elem.offsetHeight) > 0) {\n
        finalTop = -top + \'px\';\n
      } else {\n
        finalTop = \'0\';\n
      }\n
      dom.setOverlayPosition(elem, finalLeft, finalTop);\n
    }\n
    tableHeight = dom.outerHeight(this.clone.wtTable.TABLE);\n
    tableWidth = dom.outerWidth(this.clone.wtTable.TABLE);\n
    elem.style.height = (tableHeight === 0 ? tableHeight : tableHeight + 4) + \'px\';\n
    elem.style.width = (tableWidth === 0 ? tableWidth : tableWidth + 4) + \'px\';\n
  }}, {}, WalkontableOverlay);\n
;\n
window.WalkontableCornerOverlay = WalkontableCornerOverlay;\n
\n
\n
//# \n
},{"./../../../../dom.js":31,"./_base.js":15}],17:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableDebugOverlay: {get: function() {\n
      return WalkontableDebugOverlay;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___95_base_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../../dom.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableOverlay = ($___95_base_46_js__ = require("./_base.js"), $___95_base_46_js__ && $___95_base_46_js__.__esModule && $___95_base_46_js__ || {default: $___95_base_46_js__}).WalkontableOverlay;\n
var WalkontableDebugOverlay = function WalkontableDebugOverlay(wotInstance) {\n
  $traceurRuntime.superConstructor($WalkontableDebugOverlay).call(this, wotInstance);\n
  this.clone = this.makeClone(WalkontableOverlay.CLONE_DEBUG);\n
  this.clone.wtTable.holder.style.opacity = 0.4;\n
  this.clone.wtTable.holder.style.textShadow = \'0 0 2px #ff0000\';\n
  dom.addClass(this.clone.wtTable.holder.parentNode, \'wtDebugVisible\');\n
};\n
var $WalkontableDebugOverlay = WalkontableDebugOverlay;\n
($traceurRuntime.createClass)(WalkontableDebugOverlay, {}, {}, WalkontableOverlay);\n
;\n
window.WalkontableDebugOverlay = WalkontableDebugOverlay;\n
\n
\n
//# \n
},{"./../../../../dom.js":31,"./_base.js":15}],18:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableLeftOverlay: {get: function() {\n
      return WalkontableLeftOverlay;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___95_base_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../../dom.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableOverlay = ($___95_base_46_js__ = require("./_base.js"), $___95_base_46_js__ && $___95_base_46_js__.__esModule && $___95_base_46_js__ || {default: $___95_base_46_js__}).WalkontableOverlay;\n
var WalkontableLeftOverlay = function WalkontableLeftOverlay(wotInstance) {\n
  $traceurRuntime.superConstructor($WalkontableLeftOverlay).call(this, wotInstance);\n
  this.clone = this.makeClone(WalkontableOverlay.CLONE_LEFT);\n
};\n
var $WalkontableLeftOverlay = WalkontableLeftOverlay;\n
($traceurRuntime.createClass)(WalkontableLeftOverlay, {\n
  isShouldBeFullyRendered: function() {\n
    return this.wot.getSetting(\'fixedColumnsLeft\') || this.wot.getSetting(\'rowHeaders\').length ? true : false;\n
  },\n
  resetFixedPosition: function() {\n
    if (!this.wot.wtTable.holder.parentNode) {\n
      return;\n
    }\n
    this._hideBorderOnInitialPosition();\n
    if (!this.needFullRender) {\n
      return;\n
    }\n
    var elem = this.clone.wtTable.holder.parentNode;\n
    var scrollbarHeight = this.wot.wtTable.holder.clientHeight !== this.wot.wtTable.holder.offsetHeight ? dom.getScrollbarWidth() : 0;\n
    var scrollbarWidth = this.wot.wtTable.holder.clientWidth !== this.wot.wtTable.holder.offsetWidth ? dom.getScrollbarWidth() : 0;\n
    var tableWidth;\n
    var elemWidth;\n
    if (this.wot.wtOverlays.leftOverlay.trimmingContainer !== window) {\n
      elem.style.height = this.wot.wtViewport.getWorkspaceHeight() - scrollbarHeight + \'px\';\n
    } else {\n
      var box = this.wot.wtTable.hider.getBoundingClientRect();\n
      var left = Math.ceil(box.left);\n
      var right = Math.ceil(box.right);\n
      var finalLeft;\n
      var finalTop;\n
      if (left < 0 && (right - elem.offsetWidth) > 0) {\n
        finalLeft = -left + \'px\';\n
      } else {\n
        finalLeft = \'0\';\n
      }\n
      finalTop = this.wot.wtTable.hider.style.top;\n
      finalTop = finalTop === \'\' ? 0 : finalTop;\n
      dom.setOverlayPosition(elem, finalLeft, finalTop);\n
    }\n
    tableWidth = dom.outerWidth(this.clone.wtTable.TABLE);\n
    elemWidth = (tableWidth === 0 ? tableWidth : tableWidth + 4);\n
    elem.style.width = elemWidth + \'px\';\n
    if (scrollbarWidth === 0) {\n
      scrollbarWidth = 30;\n
    }\n
    this.clone.wtTable.holder.style.width = elemWidth + scrollbarWidth + \'px\';\n
  },\n
  setScrollPosition: function(pos) {\n
    if (this.mainTableScrollableElement === window) {\n
      window.scrollTo(pos, dom.getWindowScrollTop());\n
    } else {\n
      this.mainTableScrollableElement.scrollLeft = pos;\n
    }\n
  },\n
  onScroll: function() {\n
    this.wot.getSetting(\'onScrollHorizontally\');\n
  },\n
  sumCellSizes: function(from, to) {\n
    var sum = 0;\n
    var defaultColumnWidth = this.wot.wtSettings.defaultColumnWidth;\n
    while (from < to) {\n
      sum += this.wot.wtTable.getStretchedColumnWidth(from) || defaultColumnWidth;\n
      from++;\n
    }\n
    return sum;\n
  },\n
  applyToDOM: function() {\n
    var total = this.wot.getSetting(\'totalColumns\');\n
    var headerSize = this.wot.wtViewport.getRowHeaderWidth();\n
    var masterHider = this.hider;\n
    var masterHideWidth = masterHider.style.width;\n
    var newMasterHiderWidth = headerSize + this.sumCellSizes(0, total) + \'px\';\n
    if (masterHideWidth !== newMasterHiderWidth) {\n
      masterHider.style.width = newMasterHiderWidth;\n
    }\n
    if (this.needFullRender) {\n
      var cloneHolder = this.clone.wtTable.holder;\n
      var cloneHider = this.clone.wtTable.hider;\n
      var cloneHolderParent = cloneHolder.parentNode;\n
      var scrollbarWidth = dom.getScrollbarWidth();\n
      var masterHiderHeight = masterHider.style.height;\n
      var cloneHolderParentWidth = cloneHolderParent.style.width;\n
      var cloneHolderParentHeight = cloneHolderParent.style.height;\n
      var cloneHolderWidth = cloneHolder.style.width;\n
      var cloneHolderHeight = cloneHolder.style.height;\n
      var cloneHiderHeight = cloneHider.style.height;\n
      var newCloneHolderWidth = parseInt(cloneHolderParentWidth, 10) + scrollbarWidth + \'px\';\n
      if (cloneHolderWidth !== newCloneHolderWidth) {\n
        cloneHolder.style.width = newCloneHolderWidth;\n
      }\n
      if (cloneHolderHeight !== cloneHolderParentHeight) {\n
        cloneHolder.style.height = cloneHolderParentHeight;\n
      }\n
      if (cloneHiderHeight !== masterHiderHeight) {\n
        cloneHider.style.height = masterHiderHeight;\n
      }\n
    }\n
    if (typeof this.wot.wtViewport.columnsRenderCalculator.startPosition === \'number\') {\n
      this.spreader.style.left = this.wot.wtViewport.columnsRenderCalculator.startPosition + \'px\';\n
    } else if (total === 0) {\n
      this.spreader.style.left = \'0\';\n
    } else {\n
      throw new Error(\'Incorrect value of the columnsRenderCalculator\');\n
    }\n
    this.spreader.style.right = \'\';\n
    if (this.needFullRender) {\n
      this.syncOverlayOffset();\n
    }\n
  },\n
  syncOverlayOffset: function() {\n
    if (typeof this.wot.wtViewport.rowsRenderCalculator.startPosition === \'number\') {\n
      this.clone.wtTable.spreader.style.top = this.wot.wtViewport.rowsRenderCalculator.startPosition + \'px\';\n
    } else {\n
      this.clone.wtTable.spreader.style.top = \'\';\n
    }\n
  },\n
  scrollTo: function(sourceCol, beyondRendered) {\n
    var newX = this.getTableParentOffset();\n
    var sourceInstance = this.wot.cloneSource ? this.wot.cloneSource : this.wot;\n
    var mainHolder = sourceInstance.wtTable.holder;\n
    var scrollbarCompensation = 0;\n
    if (beyondRendered && mainHolder.offsetWidth !== mainHolder.clientWidth) {\n
      scrollbarCompensation = dom.getScrollbarWidth();\n
    }\n
    if (beyondRendered) {\n
      newX += this.sumCellSizes(0, sourceCol + 1);\n
      newX -= this.wot.wtViewport.getViewportWidth();\n
    } else {\n
      newX += this.sumCellSizes(this.wot.getSetting(\'fixedColumnsLeft\'), sourceCol);\n
    }\n
    newX += scrollbarCompensation;\n
    this.setScrollPosition(newX);\n
  },\n
  getTableParentOffset: function() {\n
    if (this.trimmingContainer === window) {\n
      return this.wot.wtTable.holderOffset.left;\n
    } else {\n
      return 0;\n
    }\n
  },\n
  getScrollPosition: function() {\n
    return dom.getScrollLeft(this.mainTableScrollableElement);\n
  },\n
  _hideBorderOnInitialPosition: function() {\n
    if (this.wot.getSetting(\'fixedColumnsLeft\') === 0 && this.wot.getSetting(\'rowHeaders\').length > 0) {\n
      var masterParent = this.wot.wtTable.holder.parentNode;\n
      if (this.getScrollPosition() === 0) {\n
        dom.removeClass(masterParent, \'innerBorderLeft\');\n
      } else {\n
        dom.addClass(masterParent, \'innerBorderLeft\');\n
      }\n
    }\n
  }\n
}, {}, WalkontableOverlay);\n
;\n
window.WalkontableLeftOverlay = WalkontableLeftOverlay;\n
\n
\n
//# \n
},{"./../../../../dom.js":31,"./_base.js":15}],19:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableTopOverlay: {get: function() {\n
      return WalkontableTopOverlay;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___95_base_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../../dom.js"), $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableOverlay = ($___95_base_46_js__ = require("./_base.js"), $___95_base_46_js__ && $___95_base_46_js__.__esModule && $___95_base_46_js__ || {default: $___95_base_46_js__}).WalkontableOverlay;\n
var WalkontableTopOverlay = function WalkontableTopOverlay(wotInstance) {\n
  $traceurRuntime.superConstructor($WalkontableTopOverlay).call(this, wotInstance);\n
  this.clone = this.makeClone(WalkontableOverlay.CLONE_TOP);\n
};\n
var $WalkontableTopOverlay = WalkontableTopOverlay;\n
($traceurRuntime.createClass)(WalkontableTopOverlay, {\n
  isShouldBeFullyRendered: function() {\n
    return this.wot.getSetting(\'fixedRowsTop\') || this.wot.getSetting(\'columnHeaders\').length ? true : false;\n
  },\n
  resetFixedPosition: function() {\n
    if (!this.wot.wtTable.holder.parentNode) {\n
      return;\n
    }\n
    this._hideBorderOnInitialPosition();\n
    if (!this.needFullRender) {\n
      return;\n
    }\n
    var elem = this.clone.wtTable.holder.parentNode;\n
    var scrollbarWidth = this.wot.wtTable.holder.clientWidth !== this.wot.wtTable.holder.offsetWidth ? dom.getScrollbarWidth() : 0;\n
    var tableHeight;\n
    if (this.wot.wtOverlays.leftOverlay.trimmingContainer !== window) {\n
      elem.style.width = this.wot.wtViewport.getWorkspaceWidth() - scrollbarWidth + \'px\';\n
    } else {\n
      var box = this.wot.wtTable.hider.getBoundingClientRect();\n
      var top = Math.ceil(box.top);\n
      var bottom = Math.ceil(box.bottom);\n
      var finalLeft;\n
      var finalTop;\n
      finalLeft = this.wot.wtTable.hider.style.left;\n
      finalLeft = finalLeft === \'\' ? 0 : finalLeft;\n
      if (top < 0 && (bottom - elem.offsetHeight) > 0) {\n
        finalTop = -top + \'px\';\n
      } else {\n
        finalTop = \'0\';\n
      }\n
      dom.setOverlayPosition(elem, finalLeft, finalTop);\n
    }\n
    this.clone.wtTable.holder.style.width = elem.style.width;\n
    tableHeight = dom.outerHeight(this.clone.wtTable.TABLE);\n
    elem.style.height = (tableHeight === 0 ? tableHeight : tableHeight + 4) + \'px\';\n
  },\n
  setScrollPosition: function(pos) {\n
    if (this.mainTableScrollableElement === window) {\n
      window.scrollTo(dom.getWindowScrollLeft(), pos);\n
    } else {\n
      this.mainTableScrollableElement.scrollTop = pos;\n
    }\n
  },\n
  onScroll: function() {\n
    this.wot.getSetting(\'onScrollVertically\');\n
  },\n
  sumCellSizes: function(from, to) {\n
    var sum = 0;\n
    var defaultRowHeight = this.wot.wtSettings.settings.defaultRowHeight;\n
    while (from < to) {\n
      sum += this.wot.wtTable.getRowHeight(from) || defaultRowHeight;\n
      from++;\n
    }\n
    return sum;\n
  },\n
  applyToDOM: function() {\n
    var total = this.wot.getSetting(\'totalRows\');\n
    var headerSize = this.wot.wtViewport.getColumnHeaderHeight();\n
    this.hider.style.height = (headerSize + this.sumCellSizes(0, total) + 1) + \'px\';\n
    if (this.needFullRender) {\n
      var scrollbarWidth = dom.getScrollbarWidth();\n
      this.clone.wtTable.hider.style.width = this.hider.style.width;\n
      this.clone.wtTable.holder.style.width = this.clone.wtTable.holder.parentNode.style.width;\n
      if (scrollbarWidth === 0) {\n
        scrollbarWidth = 30;\n
      }\n
      this.clone.wtTable.holder.style.height = parseInt(this.clone.wtTable.holder.parentNode.style.height, 10) + scrollbarWidth + \'px\';\n
    }\n
    if (typeof this.wot.wtViewport.rowsRenderCalculator.startPosition === \'number\') {\n
      this.spreader.style.top = this.wot.wtViewport.rowsRenderCalculator.startPosition + \'px\';\n
    } else if (total === 0) {\n
      this.spreader.style.top = \'0\';\n
    } else {\n
      throw new Error("Incorrect value of the rowsRenderCalculator");\n
    }\n
    this.spreader.style.bottom = \'\';\n
    if (this.needFullRender) {\n
      this.syncOverlayOffset();\n
    }\n
  },\n
  syncOverlayOffset: function() {\n
    if (typeof this.wot.wtViewport.columnsRenderCalculator.startPosition === \'number\') {\n
      this.clone.wtTable.spreader.style.left = this.wot.wtViewport.columnsRenderCalculator.startPosition + \'px\';\n
    } else {\n
      this.clone.wtTable.spreader.style.left = \'\';\n
    }\n
  },\n
  scrollTo: function(sourceRow, bottomEdge) {\n
    var newY = this.getTableParentOffset();\n
    var sourceInstance = this.wot.cloneSource ? this.wot.cloneSource : this.wot;\n
    var mainHolder = sourceInstance.wtTable.holder;\n
    var scrollbarCompensation = 0;\n
    if (bottomEdge && mainHolder.offsetHeight !== mainHolder.clientHeight) {\n
      scrollbarCompensation = dom.getScrollbarWidth();\n
    }\n
    if (bottomEdge) {\n
      newY += this.sumCellSizes(0, sourceRow + 1);\n
      newY -= this.wot.wtViewport.getViewportHeight();\n
      newY += 1;\n
    } else {\n
      newY += this.sumCellSizes(this.wot.getSetting(\'fixedRowsTop\'), sourceRow);\n
    }\n
    newY += scrollbarCompensation;\n
    this.setScrollPosition(newY);\n
  },\n
  getTableParentOffset: function() {\n
    if (this.mainTableScrollableElement === window) {\n
      return this.wot.wtTable.holderOffset.top;\n
    } else {\n
      return 0;\n
    }\n
  },\n
  getScrollPosition: function() {\n
    return dom.getScrollTop(this.mainTableScrollableElement);\n
  },\n
  _hideBorderOnInitialPosition: function() {\n
    if (this.wot.getSetting(\'fixedRowsTop\') === 0 && this.wot.getSetting(\'columnHeaders\').length > 0) {\n
      var masterParent = this.wot.wtTable.holder.parentNode;\n
      if (this.getScrollPosition() === 0) {\n
        dom.removeClass(masterParent, \'innerBorderTop\');\n
      } else {\n
        dom.addClass(masterParent, \'innerBorderTop\');\n
      }\n
    }\n
    if (this.wot.getSetting(\'rowHeaders\').length === 0) {\n
      var secondHeaderCell = this.clone.wtTable.THEAD.querySelector(\'th:nth-of-type(2)\');\n
      if (secondHeaderCell) {\n
        secondHeaderCell.style[\'border-left-width\'] = 0;\n
      }\n
    }\n
  }\n
}, {}, WalkontableOverlay);\n
;\n
window.WalkontableTopOverlay = WalkontableTopOverlay;\n
\n
\n
//# \n
},{"./../../../../dom.js":31,"./_base.js":15}],20:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableOverlays: {get: function() {\n
      return WalkontableOverlays;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47_eventManager_46_js__,\n
    $__overlay_47_corner_46_js__,\n
    $__overlay_47_debug_46_js__,\n
    $__overlay_47_left_46_js__,\n
    $__overlay_47_top_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47__46__46__47_eventManager_46_js__ = require("./../../../eventManager.js"), $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var WalkontableCornerOverlay = ($__overlay_47_corner_46_js__ = require("./overlay/corner.js"), $__overlay_47_corner_46_js__ && $__overlay_47_corner_46_js__.__esModule && $__overlay_47_corner_46_js__ || {default: $__overlay_47_corner_46_js__}).WalkontableCornerOverlay;\n
var WalkontableDebugOverlay = ($__overlay_47_debug_46_js__ = require("./overlay/debug.js"), $__overlay_47_debug_46_js__ && $__overlay_47_debug_46_js__.__esModule && $__overlay_47_debug_46_js__ || {default: $__overlay_47_debug_46_js__}).WalkontableDebugOverlay;\n
var WalkontableLeftOverlay = ($__overlay_47_left_46_js__ = require("./overlay/left.js"), $__overlay_47_left_46_js__ && $__overlay_47_left_46_js__.__esModule && $__overlay_47_left_46_js__ || {default: $__overlay_47_left_46_js__}).WalkontableLeftOverlay;\n
var WalkontableTopOverlay = ($__overlay_47_top_46_js__ = require("./overlay/top.js"), $__overlay_47_top_46_js__ && $__overlay_47_top_46_js__.__esModule && $__overlay_47_top_46_js__ || {default: $__overlay_47_top_46_js__}).WalkontableTopOverlay;\n
var WalkontableOverlays = function WalkontableOverlays(wotInstance) {\n
  this.wot = wotInstance;\n
  this.instance = this.wot;\n
  this.wot.update(\'scrollbarWidth\', dom.getScrollbarWidth());\n
  this.wot.update(\'scrollbarHeight\', dom.getScrollbarWidth());\n
  this.mainTableScrollableElement = dom.getScrollableElement(this.wot.wtTable.TABLE);\n
  this.topOverlay = new WalkontableTopOverlay(this.wot);\n
  this.leftOverlay = new WalkontableLeftOverlay(this.wot);\n
  if (this.topOverlay.needFullRender && this.leftOverlay.needFullRender) {\n
    this.topLeftCornerOverlay = new WalkontableCornerOverlay(this.wot);\n
  }\n
  if (this.wot.getSetting(\'debug\')) {\n
    this.debug = new WalkontableDebugOverlay(this.wot);\n
  }\n
  this.destroyed = false;\n
  this.overlayScrollPositions = {\n
    \'master\': {\n
      top: 0,\n
      left: 0\n
    },\n
    \'top\': {\n
      top: null,\n
      left: 0\n
    },\n
    \'left\': {\n
      top: 0,\n
      left: null\n
    }\n
  };\n
  this.registerListeners();\n
};\n
($traceurRuntime.createClass)(WalkontableOverlays, {\n
  refreshAll: function() {\n
    if (!this.wot.drawn) {\n
      return;\n
    }\n
    if (!this.wot.wtTable.holder.parentNode) {\n
      this.destroy();\n
      return;\n
    }\n
    this.wot.draw(true);\n
    this.topOverlay.onScroll();\n
    this.leftOverlay.onScroll();\n
  },\n
  registerListeners: function() {\n
    var $__5 = this;\n
    var eventManager = eventManagerObject(this.wot);\n
    eventManager.addEventListener(this.mainTableScrollableElement, \'scroll\', (function(event) {\n
      return $__5.onTableScroll(event);\n
    }));\n
    if (this.topOverlay.needFullRender) {\n
      eventManager.addEventListener(this.topOverlay.clone.wtTable.holder, \'scroll\', (function(event) {\n
        return $__5.onTableScroll(event);\n
      }));\n
      eventManager.addEventListener(this.topOverlay.clone.wtTable.holder, \'wheel\', (function(event) {\n
        return $__5.onTableScroll(event);\n
      }));\n
    }\n
    if (this.leftOverlay.needFullRender) {\n
      eventManager.addEventListener(this.leftOverlay.clone.wtTable.holder, \'scroll\', (function(event) {\n
        return $__5.onTableScroll(event);\n
      }));\n
      eventManager.addEventListener(this.leftOverlay.clone.wtTable.holder, \'wheel\', (function(event) {\n
        return $__5.onTableScroll(event);\n
      }));\n
    }\n
    if (this.topOverlay.trimmingContainer !== window && this.leftOverlay.trimmingContainer !== window) {\n
      eventManager.addEventListener(window, \'wheel\', (function(event) {\n
        var overlay;\n
        var deltaY = event.wheelDeltaY || event.deltaY;\n
        var deltaX = event.wheelDeltaX || event.deltaX;\n
        if ($__5.topOverlay.clone.wtTable.holder.contains(event.target)) {\n
          overlay = \'top\';\n
        } else if ($__5.leftOverlay.clone.wtTable.holder.contains(event.target)) {\n
          overlay = \'left\';\n
        }\n
        if (overlay == \'top\' && deltaY !== 0) {\n
          event.preventDefault();\n
        } else if (overlay == \'left\' && deltaX !== 0) {\n
          event.preventDefault();\n
        }\n
      }));\n
    }\n
  },\n
  onTableScroll: function(event) {\n
    if (Handsontable.mobileBrowser) {\n
      return;\n
    }\n
    if (event.type === \'scroll\') {\n
      this.syncScrollPositions(event);\n
    } else {\n
      this.translateMouseWheelToScroll(event);\n
    }\n
  },\n
  translateMouseWheelToScroll: function(event) {\n
    var topOverlay = this.topOverlay.clone.wtTable.holder;\n
    var leftOverlay = this.leftOverlay.clone.wtTable.holder;\n
    var eventMockup = {type: \'wheel\'};\n
    var tempElem = event.target;\n
    var deltaY = event.wheelDeltaY || (-1) * event.deltaY;\n
    var deltaX = event.wheelDeltaX || (-1) * event.deltaX;\n
    var parentHolder;\n
    while (tempElem != document && tempElem != null) {\n
      if (tempElem.className.indexOf(\'wtHolder\') > -1) {\n
        parentHolder = tempElem;\n
        break;\n
      }\n
      tempElem = tempElem.parentNode;\n
    }\n
    eventMockup.target = parentHolder;\n
    if (parentHolder == topOverlay) {\n
      this.syncScrollPositions(eventMockup, (-0.2) * deltaY);\n
    } else if (parentHolder == leftOverlay) {\n
      this.syncScrollPositions(eventMockup, (-0.2) * deltaX);\n
    }\n
    return false;\n
  },\n
  syncScrollPositions: function(event) {\n
    var fakeScrollValue = arguments[1] !== (void 0) ? arguments[1] : null;\n
    if (this.destroyed) {\n
      return;\n
    }\n
    if (arguments.length === 0) {\n
      this.syncScrollWithMaster();\n
      return;\n
    }\n
    var master = this.mainTableScrollableElement;\n
    var target = event.target;\n
    var tempScrollValue = 0;\n
    var scrollValueChanged = false;\n
    var topOverlay;\n
    var leftOverlay;\n
    if (this.topOverlay.needFullRender) {\n
      topOverlay = this.topOverlay.clone.wtTable.holder;\n
    }\n
    if (this.leftOverlay.needFullRender) {\n
      leftOverlay = this.leftOverlay.clone.wtTable.holder;\n
    }\n
    if (target === document) {\n
      target = window;\n
    }\n
    if (target === master) {\n
      tempScrollValue = dom.getScrollLeft(target);\n
      if (this.overlayScrollPositions.master.left !== tempScrollValue) {\n
        this.overlayScrollPositions.master.left = tempScrollValue;\n
        scrollValueChanged = true;\n
        if (topOverlay) {\n
          topOverlay.scrollLeft = tempScrollValue;\n
        }\n
      }\n
      tempScrollValue = dom.getScrollTop(target);\n
      if (this.overlayScrollPositions.master.top !== tempScrollValue) {\n
        this.overlayScrollPositions.master.top = tempScrollValue;\n
        scrollValueChanged = true;\n
        if (leftOverlay) {\n
          leftOverlay.scrollTop = tempScrollValue;\n
        }\n
      }\n
    } else if (target === topOverlay) {\n
      tempScrollValue = dom.getScrollLeft(target);\n
      if (this.overlayScrollPositions.top.left !== tempScrollValue) {\n
        this.overlayScrollPositions.top.left = tempScrollValue;\n
        scrollValueChanged = true;\n
        master.scrollLeft = tempScrollValue;\n
      }\n
      if (fakeScrollValue !== null) {\n
        scrollValueChanged = true;\n
        master.scrollTop += fakeScrollValue;\n
      }\n
    } else if (target === leftOverlay) {\n
      tempScrollValue = dom.getScrollTop(target);\n
      if (this.overlayScrollPositions.left.top !== tempScrollValue) {\n
        this.overlayScrollPositions.left.top = tempScrollValue;\n
        scrollValueChanged = true;\n
        master.scrollTop = tempScrollValue;\n
      }\n
      if (fakeScrollValue !== null) {\n
        scrollValueChanged = true;\n
        master.scrollLeft += fakeScrollValue;\n
      }\n
    }\n
    if (scrollValueChanged && event.type === \'scroll\') {\n
      this.refreshAll();\n
    }\n
  },\n
  syncScrollWithMaster: function() {\n
    var master = this.topOverlay.mainTableScrollableElement;\n
    if (this.topOverlay.needFullRender) {\n
      this.topOverlay.clone.wtTable.holder.scrollLeft = master.scrollLeft;\n
    }\n
    if (this.leftOverlay.needFullRender) {\n
      this.leftOverlay.clone.wtTable.holder.scrollTop = master.scrollTop;\n
    }\n
  },\n
  destroy: function() {\n
    eventManagerObject(this.wot).clear();\n
    this.topOverlay.destroy();\n
    this.leftOverlay.destroy();\n
    if (this.topLeftCornerOverlay) {\n
      this.topLeftCornerOverlay.destroy();\n
    }\n
    if (this.debug) {\n
      this.debug.destroy();\n
    }\n
    this.destroyed = true;\n
  },\n
  refresh: function() {\n
    var fastDraw = arguments[0] !== (void 0) ? arguments[0] : false;\n
    this.leftOverlay.refresh(fastDraw);\n
    this.topOverlay.refresh(fastDraw);\n
    if (this.topLeftCornerOverlay) {\n
      this.topLeftCornerOverlay.refresh(fastDraw);\n
    }\n
    if (this.debug) {\n
      this.debug.refresh(fastDraw);\n
    }\n
  },\n
  applyToDOM: function() {\n
    this.leftOverlay.applyToDOM();\n
    this.topOverlay.applyToDOM();\n
  }\n
}, {});\n
;\n
window.WalkontableOverlays = WalkontableOverlays;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./../../../eventManager.js":45,"./overlay/corner.js":16,"./overlay/debug.js":17,"./overlay/left.js":18,"./overlay/top.js":19}],21:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableScroll: {get: function() {\n
      return WalkontableScroll;\n
    }},\n
  __esModule: {value: true}\n
});\n
var WalkontableScroll = function WalkontableScroll(wotInstance) {\n
  this.wot = wotInstance;\n
  this.instance = wotInstance;\n
};\n
($traceurRuntime.createClass)(WalkontableScroll, {scrollViewport: function(coords) {\n
    if (!this.wot.drawn) {\n
      return;\n
    }\n
    var totalRows = this.wot.getSetting(\'totalRows\');\n
    var totalColumns = this.wot.getSetting(\'totalColumns\');\n
    if (coords.row < 0 || coords.row > totalRows - 1) {\n
      throw new Error(\'row \' + coords.row + \' does not exist\');\n
    }\n
    if (coords.col < 0 || coords.col > totalColumns - 1) {\n
      throw new Error(\'column \' + coords.col + \' does not exist\');\n
    }\n
    if (coords.row > this.instance.wtTable.getLastVisibleRow()) {\n
      this.wot.wtOverlays.topOverlay.scrollTo(coords.row, true);\n
    } else if (coords.row >= this.instance.getSetting(\'fixedRowsTop\') && coords.row < this.instance.wtTable.getFirstVisibleRow()) {\n
      this.wot.wtOverlays.topOverlay.scrollTo(coords.row);\n
    }\n
    if (coords.col > this.instance.wtTable.getLastVisibleColumn()) {\n
      this.wot.wtOverlays.leftOverlay.scrollTo(coords.col, true);\n
    } else if (coords.col >= this.instance.getSetting(\'fixedColumnsLeft\') && coords.col < this.instance.wtTable.getFirstVisibleColumn()) {\n
      this.wot.wtOverlays.leftOverlay.scrollTo(coords.col);\n
    }\n
  }}, {});\n
;\n
window.WalkontableScroll = WalkontableScroll;\n
\n
\n
//# \n
},{}],22:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableSelection: {get: function() {\n
      return WalkontableSelection;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $__border_46_js__,\n
    $__cell_47_coords_46_js__,\n
    $__cell_47_range_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableBorder = ($__border_46_js__ = require("./border.js"), $__border_46_js__ && $__border_46_js__.__esModule && $__border_46_js__ || {default: $__border_46_js__}).WalkontableBorder;\n
var WalkontableCellCoords = ($__cell_47_coords_46_js__ = require("./cell/coords.js"), $__cell_47_coords_46_js__ && $__cell_47_coords_46_js__.__esModule && $__cell_47_coords_46_js__ || {default: $__cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = ($__cell_47_range_46_js__ = require("./cell/range.js"), $__cell_47_range_46_js__ && $__cell_47_range_46_js__.__esModule && $__cell_47_range_46_js__ || {default: $__cell_47_range_46_js__}).WalkontableCellRange;\n
var WalkontableSelection = function WalkontableSelection(settings, cellRange) {\n
  this.settings = settings;\n
  this.cellRange = cellRange || null;\n
  this.instanceBorders = {};\n
};\n
($traceurRuntime.createClass)(WalkontableSelection, {\n
  getBorder: function(wotInstance) {\n
    if (this.instanceBorders[wotInstance.guid]) {\n
      return this.instanceBorders[wotInstance.guid];\n
    }\n
    this.instanceBorders[wotInstance.guid] = new WalkontableBorder(wotInstance, this.settings);\n
  },\n
  isEmpty: function() {\n
    return this.cellRange === null;\n
  },\n
  add: function(coords) {\n
    if (this.isEmpty()) {\n
      this.cellRange = new WalkontableCellRange(coords, coords, coords);\n
    } else {\n
      this.cellRange.expand(coords);\n
    }\n
  },\n
  replace: function(oldCoords, newCoords) {\n
    if (!this.isEmpty()) {\n
      if (this.cellRange.from.isEqual(oldCoords)) {\n
        this.cellRange.from = newCoords;\n
        return true;\n
      }\n
      if (this.cellRange.to.isEqual(oldCoords)) {\n
        this.cellRange.to = newCoords;\n
        return true;\n
      }\n
    }\n
    return false;\n
  },\n
  clear: function() {\n
    this.cellRange = null;\n
  },\n
  getCorners: function() {\n
    var topLeft = this.cellRange.getTopLeftCorner();\n
    var bottomRight = this.cellRange.getBottomRightCorner();\n
    return [topLeft.row, topLeft.col, bottomRight.row, bottomRight.col];\n
  },\n
  addClassAtCoords: function(wotInstance, sourceRow, sourceColumn, className) {\n
    var TD = wotInstance.wtTable.getCell(new WalkontableCellCoords(sourceRow, sourceColumn));\n
    if (typeof TD === \'object\') {\n
      dom.addClass(TD, className);\n
    }\n
  },\n
  draw: function(wotInstance) {\n
    if (this.isEmpty()) {\n
      if (this.settings.border) {\n
        var border = this.getBorder(wotInstance);\n
        if (border) {\n
          border.disappear();\n
        }\n
      }\n
      return;\n
    }\n
    var renderedRows = wotInstance.wtTable.getRenderedRowsCount();\n
    var renderedColumns = wotInstance.wtTable.getRenderedColumnsCount();\n
    var corners = this.getCorners();\n
    var sourceRow,\n
        sourceCol,\n
        TH;\n
    for (var column = 0; column < renderedColumns; column++) {\n
      sourceCol = wotInstance.wtTable.columnFilter.renderedToSource(column);\n
      if (sourceCol >= corners[1] && sourceCol <= corners[3]) {\n
        TH = wotInstance.wtTable.getColumnHeader(sourceCol);\n
        if (TH && this.settings.highlightColumnClassName) {\n
          dom.addClass(TH, this.settings.highlightColumnClassName);\n
        }\n
      }\n
    }\n
    for (var row = 0; row < renderedRows; row++) {\n
      sourceRow = wotInstance.wtTable.rowFilter.renderedToSource(row);\n
      if (sourceRow >= corners[0] && sourceRow <= corners[2]) {\n
        TH = wotInstance.wtTable.getRowHeader(sourceRow);\n
        if (TH && this.settings.highlightRowClassName) {\n
          dom.addClass(TH, this.settings.highlightRowClassName);\n
        }\n
      }\n
      for (var column$__4 = 0; column$__4 < renderedColumns; column$__4++) {\n
        sourceCol = wotInstance.wtTable.columnFilter.renderedToSource(column$__4);\n
        if (sourceRow >= corners[0] && sourceRow <= corners[2] && sourceCol >= corners[1] && sourceCol <= corners[3]) {\n
          if (this.settings.className) {\n
            this.addClassAtCoords(wotInstance, sourceRow, sourceCol, this.settings.className);\n
          }\n
        } else if (sourceRow >= corners[0] && sourceRow <= corners[2]) {\n
          if (this.settings.highlightRowClassName) {\n
            this.addClassAtCoords(wotInstance, sourceRow, sourceCol, this.settings.highlightRowClassName);\n
          }\n
        } else if (sourceCol >= corners[1] && sourceCol <= corners[3]) {\n
          if (this.settings.highlightColumnClassName) {\n
            this.addClassAtCoords(wotInstance, sourceRow, sourceCol, this.settings.highlightColumnClassName);\n
          }\n
        }\n
      }\n
    }\n
    wotInstance.getSetting(\'onBeforeDrawBorders\', corners, this.settings.className);\n
    if (this.settings.border) {\n
      var border$__5 = this.getBorder(wotInstance);\n
      if (border$__5) {\n
        border$__5.appear(corners);\n
      }\n
    }\n
  }\n
}, {});\n
;\n
window.WalkontableSelection = WalkontableSelection;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./border.js":6,"./cell/coords.js":9,"./cell/range.js":10}],23:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableSettings: {get: function() {\n
      return WalkontableSettings;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableSettings = function WalkontableSettings(wotInstance, settings) {\n
  var $__0 = this;\n
  this.wot = wotInstance;\n
  this.instance = wotInstance;\n
  this.defaults = {\n
    table: void 0,\n
    debug: false,\n
    stretchH: \'none\',\n
    currentRowClassName: null,\n
    currentColumnClassName: null,\n
    data: void 0,\n
    fixedColumnsLeft: 0,\n
    fixedRowsTop: 0,\n
    rowHeaders: function() {\n
      return [];\n
    },\n
    columnHeaders: function() {\n
      return [];\n
    },\n
    totalRows: void 0,\n
    totalColumns: void 0,\n
    cellRenderer: (function(row, column, TD) {\n
      var cellData = $__0.getSetting(\'data\', row, column);\n
      dom.fastInnerText(TD, cellData === void 0 || cellData === null ? \'\' : cellData);\n
    }),\n
    columnWidth: function(col) {\n
      return;\n
    },\n
    rowHeight: function(row) {\n
      return;\n
    },\n
    defaultRowHeight: 23,\n
    defaultColumnWidth: 50,\n
    selections: null,\n
    hideBorderOnMouseDownOver: false,\n
    viewportRowCalculatorOverride: null,\n
    viewportColumnCalculatorOverride: null,\n
    onCellMouseDown: null,\n
    onCellMouseOver: null,\n
    onCellDblClick: null,\n
    onCellCornerMouseDown: null,\n
    onCellCornerDblClick: null,\n
    beforeDraw: null,\n
    onDraw: null,\n
    onBeforeDrawBorders: null,\n
    onScrollVertically: null,\n
    onScrollHorizontally: null,\n
    onBeforeTouchScroll: null,\n
    onAfterMomentumScroll: null,\n
    scrollbarWidth: 10,\n
    scrollbarHeight: 10,\n
    renderAllRows: false,\n
    groups: false\n
  };\n
  this.settings = {};\n
  for (var i in this.defaults) {\n
    if (this.defaults.hasOwnProperty(i)) {\n
      if (settings[i] !== void 0) {\n
        this.settings[i] = settings[i];\n
      } else if (this.defaults[i] === void 0) {\n
        throw new Error(\'A required setting "\' + i + \'" was not provided\');\n
      } else {\n
        this.settings[i] = this.defaults[i];\n
      }\n
    }\n
  }\n
};\n
($traceurRuntime.createClass)(WalkontableSettings, {\n
  update: function(settings, value) {\n
    if (value === void 0) {\n
      for (var i in settings) {\n
        if (settings.hasOwnProperty(i)) {\n
          this.settings[i] = settings[i];\n
        }\n
      }\n
    } else {\n
      this.settings[settings] = value;\n
    }\n
    return this.wot;\n
  },\n
  getSetting: function(key, param1, param2, param3, param4) {\n
    if (typeof this.settings[key] === \'function\') {\n
      return this.settings[key](param1, param2, param3, param4);\n
    } else if (param1 !== void 0 && Array.isArray(this.settings[key])) {\n
      return this.settings[key][param1];\n
    } else {\n
      return this.settings[key];\n
    }\n
  },\n
  has: function(key) {\n
    return !!this.settings[key];\n
  }\n
}, {});\n
;\n
window.WalkontableSettings = WalkontableSettings;\n
\n
\n
//# \n
},{"./../../../dom.js":31}],24:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableTable: {get: function() {\n
      return WalkontableTable;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $__cell_47_coords_46_js__,\n
    $__cell_47_range_46_js__,\n
    $__filter_47_column_46_js__,\n
    $__overlay_47_corner_46_js__,\n
    $__overlay_47_debug_46_js__,\n
    $__overlay_47_left_46_js__,\n
    $__filter_47_row_46_js__,\n
    $__tableRenderer_46_js__,\n
    $__overlay_47_top_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var WalkontableCellCoords = ($__cell_47_coords_46_js__ = require("./cell/coords.js"), $__cell_47_coords_46_js__ && $__cell_47_coords_46_js__.__esModule && $__cell_47_coords_46_js__ || {default: $__cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = ($__cell_47_range_46_js__ = require("./cell/range.js"), $__cell_47_range_46_js__ && $__cell_47_range_46_js__.__esModule && $__cell_47_range_46_js__ || {default: $__cell_47_range_46_js__}).WalkontableCellRange;\n
var WalkontableColumnFilter = ($__filter_47_column_46_js__ = require("./filter/column.js"), $__filter_47_column_46_js__ && $__filter_47_column_46_js__.__esModule && $__filter_47_column_46_js__ || {default: $__filter_47_column_46_js__}).WalkontableColumnFilter;\n
var WalkontableCornerOverlay = ($__overlay_47_corner_46_js__ = require("./overlay/corner.js"), $__overlay_47_corner_46_js__ && $__overlay_47_corner_46_js__.__esModule && $__overlay_47_corner_46_js__ || {default: $__overlay_47_corner_46_js__}).WalkontableCornerOverlay;\n
var WalkontableDebugOverlay = ($__overlay_47_debug_46_js__ = require("./overlay/debug.js"), $__overlay_47_debug_46_js__ && $__overlay_47_debug_46_js__.__esModule && $__overlay_47_debug_46_js__ || {default: $__overlay_47_debug_46_js__}).WalkontableDebugOverlay;\n
var WalkontableLeftOverlay = ($__overlay_47_left_46_js__ = require("./overlay/left.js"), $__overlay_47_left_46_js__ && $__overlay_47_left_46_js__.__esModule && $__overlay_47_left_46_js__ || {default: $__overlay_47_left_46_js__}).WalkontableLeftOverlay;\n
var WalkontableRowFilter = ($__filter_47_row_46_js__ = require("./filter/row.js"), $__filter_47_row_46_js__ && $__filter_47_row_46_js__.__esModule && $__filter_47_row_46_js__ || {default: $__filter_47_row_46_js__}).WalkontableRowFilter;\n
var WalkontableTableRenderer = ($__tableRenderer_46_js__ = require("./tableRenderer.js"), $__tableRenderer_46_js__ && $__tableRenderer_46_js__.__esModule && $__tableRenderer_46_js__ || {default: $__tableRenderer_46_js__}).WalkontableTableRenderer;\n
var WalkontableTopOverlay = ($__overlay_47_top_46_js__ = require("./overlay/top.js"), $__overlay_47_top_46_js__ && $__overlay_47_top_46_js__.__esModule && $__overlay_47_top_46_js__ || {default: $__overlay_47_top_46_js__}).WalkontableTopOverlay;\n
function WalkontableTable(instance, table) {\n
  this.instance = instance;\n
  this.TABLE = table;\n
  dom.removeTextNodes(this.TABLE);\n
  var parent = this.TABLE.parentNode;\n
  if (!parent || parent.nodeType !== 1 || !dom.hasClass(parent, \'wtHolder\')) {\n
    var spreader = document.createElement(\'DIV\');\n
    spreader.className = \'wtSpreader\';\n
    if (parent) {\n
      parent.insertBefore(spreader, this.TABLE);\n
    }\n
    spreader.appendChild(this.TABLE);\n
  }\n
  this.spreader = this.TABLE.parentNode;\n
  this.spreader.style.position = \'relative\';\n
  parent = this.spreader.parentNode;\n
  if (!parent || parent.nodeType !== 1 || !dom.hasClass(parent, \'wtHolder\')) {\n
    var hider = document.createElement(\'DIV\');\n
    hider.className = \'wtHider\';\n
    if (parent) {\n
      parent.insertBefore(hider, this.spreader);\n
    }\n
    hider.appendChild(this.spreader);\n
  }\n
  this.hider = this.spreader.parentNode;\n
  parent = this.hider.parentNode;\n
  if (!parent || parent.nodeType !== 1 || !dom.hasClass(parent, \'wtHolder\')) {\n
    var holder = document.createElement(\'DIV\');\n
    holder.style.position = \'relative\';\n
    holder.className = \'wtHolder\';\n
    if (parent) {\n
      parent.insertBefore(holder, this.hider);\n
    }\n
    if (!instance.cloneSource) {\n
      holder.parentNode.className += \'ht_master handsontable\';\n
    }\n
    holder.appendChild(this.hider);\n
  }\n
  this.holder = this.hider.parentNode;\n
  this.wtRootElement = this.holder.parentNode;\n
  this.alignOverlaysWithTrimmingContainer();\n
  this.TBODY = this.TABLE.getElementsByTagName(\'TBODY\')[0];\n
  if (!this.TBODY) {\n
    this.TBODY = document.createElement(\'TBODY\');\n
    this.TABLE.appendChild(this.TBODY);\n
  }\n
  this.THEAD = this.TABLE.getElementsByTagName(\'THEAD\')[0];\n
  if (!this.THEAD) {\n
    this.THEAD = document.createElement(\'THEAD\');\n
    this.TABLE.insertBefore(this.THEAD, this.TBODY);\n
  }\n
  this.COLGROUP = this.TABLE.getElementsByTagName(\'COLGROUP\')[0];\n
  if (!this.COLGROUP) {\n
    this.COLGROUP = document.createElement(\'COLGROUP\');\n
    this.TABLE.insertBefore(this.COLGROUP, this.THEAD);\n
  }\n
  if (this.instance.getSetting(\'columnHeaders\').length) {\n
    if (!this.THEAD.childNodes.length) {\n
      var TR = document.createElement(\'TR\');\n
      this.THEAD.appendChild(TR);\n
    }\n
  }\n
  this.colgroupChildrenLength = this.COLGROUP.childNodes.length;\n
  this.theadChildrenLength = this.THEAD.firstChild ? this.THEAD.firstChild.childNodes.length : 0;\n
  this.tbodyChildrenLength = this.TBODY.childNodes.length;\n
  this.rowFilter = null;\n
  this.columnFilter = null;\n
}\n
WalkontableTable.prototype.alignOverlaysWithTrimmingContainer = function() {\n
  var trimmingElement = dom.getTrimmingContainer(this.wtRootElement);\n
  if (!this.isWorkingOnClone()) {\n
    this.holder.parentNode.style.position = \'relative\';\n
    if (trimmingElement !== window) {\n
      this.holder.style.width = dom.getStyle(trimmingElement, \'width\');\n
      this.holder.style.height = dom.getStyle(trimmingElement, \'height\');\n
      this.holder.style.overflow = \'\';\n
    } else {\n
      this.holder.style.overflow = \'visible\';\n
      this.wtRootElement.style.overflow = \'visible\';\n
    }\n
  }\n
};\n
WalkontableTable.prototype.isWorkingOnClone = function() {\n
  return !!this.instance.cloneSource;\n
};\n
WalkontableTable.prototype.draw = function(fastDraw) {\n
  if (!this.isWorkingOnClone()) {\n
    this.holderOffset = dom.offset(this.holder);\n
    fastDraw = this.instance.wtViewport.createRenderCalculators(fastDraw);\n
  }\n
  if (!fastDraw) {\n
    if (this.isWorkingOnClone()) {\n
      this.tableOffset = this.instance.cloneSource.wtTable.tableOffset;\n
    } else {\n
      this.tableOffset = dom.offset(this.TABLE);\n
    }\n
    var startRow;\n
    if (this.instance.cloneOverlay instanceof WalkontableDebugOverlay || this.instance.cloneOverlay instanceof WalkontableTopOverlay || this.instance.cloneOverlay instanceof WalkontableCornerOverlay) {\n
      startRow = 0;\n
    } else {\n
      startRow = this.instance.wtViewport.rowsRenderCalculator.startRow;\n
    }\n
    var startColumn;\n
    if (this.instance.cloneOverlay instanceof WalkontableDebugOverlay || this.instance.cloneOverlay instanceof WalkontableLeftOverlay || this.instance.cloneOverlay instanceof WalkontableCornerOverlay) {\n
      startColumn = 0;\n
    } else {\n
      startColumn = this.instance.wtViewport.columnsRenderCalculator.startColumn;\n
    }\n
    this.rowFilter = new WalkontableRowFilter(startRow, this.instance.getSetting(\'totalRows\'), this.instance.getSetting(\'columnHeaders\').length);\n
    this.columnFilter = new WalkontableColumnFilter(startColumn, this.instance.getSetting(\'totalColumns\'), this.instance.getSetting(\'rowHeaders\').length);\n
    this._doDraw();\n
    this.alignOverlaysWithTrimmingContainer();\n
  } else {\n
    if (!this.isWorkingOnClone()) {\n
      this.instance.wtViewport.createVisibleCalculators();\n
    }\n
    if (this.instance.wtOverlays) {\n
      this.instance.wtOverlays.refresh(true);\n
    }\n
  }\n
  this.refreshSelections(fastDraw);\n
  if (!this.isWorkingOnClone()) {\n
    this.instance.wtOverlays.topOverlay.resetFixedPosition();\n
    this.instance.wtOverlays.leftOverlay.resetFixedPosition();\n
    if (this.instance.wtOverlays.topLeftCornerOverlay) {\n
      this.instance.wtOverlays.topLeftCornerOverlay.resetFixedPosition();\n
    }\n
  }\n
  this.instance.drawn = true;\n
  return this;\n
};\n
WalkontableTable.prototype._doDraw = function() {\n
  var wtRenderer = new WalkontableTableRenderer(this);\n
  wtRenderer.render();\n
};\n
WalkontableTable.prototype.removeClassFromCells = function(className) {\n
  var nodes = this.TABLE.querySelectorAll(\'.\' + className);\n
  for (var i = 0,\n
      ilen = nodes.length; i < ilen; i++) {\n
    dom.removeClass(nodes[i], className);\n
  }\n
};\n
WalkontableTable.prototype.refreshSelections = function(fastDraw) {\n
  var i,\n
      len;\n
  if (!this.instance.selections) {\n
    return;\n
  }\n
  len = this.instance.selections.length;\n
  if (fastDraw) {\n
    for (i = 0; i < len; i++) {\n
      if (this.instance.selections[i].settings.className) {\n
        this.removeClassFromCells(this.instance.selections[i].settings.className);\n
      }\n
      if (this.instance.selections[i].settings.highlightRowClassName) {\n
        this.removeClassFromCells(this.instance.selections[i].settings.highlightRowClassName);\n
      }\n
      if (this.instance.selections[i].settings.highlightColumnClassName) {\n
        this.removeClassFromCells(this.instance.selections[i].settings.highlightColumnClassName);\n
      }\n
    }\n
  }\n
  for (i = 0; i < len; i++) {\n
    this.instance.selections[i].draw(this.instance, fastDraw);\n
  }\n
};\n
WalkontableTable.prototype.getCell = function(coords) {\n
  if (this.isRowBeforeRenderedRows(coords.row)) {\n
    return -1;\n
  } else if (this.isRowAfterRenderedRows(coords.row)) {\n
    return -2;\n
  }\n
  var TR = this.TBODY.childNodes[this.rowFilter.sourceToRendered(coords.row)];\n
  if (TR) {\n
    return TR.childNodes[this.columnFilter.sourceColumnToVisibleRowHeadedColumn(coords.col)];\n
  }\n
};\n
WalkontableTable.prototype.getColumnHeader = function(col, level) {\n
  if (!level) {\n
    level = 0;\n
  }\n
  var TR = this.THEAD.childNodes[level];\n
  if (TR) {\n
    return TR.childNodes[this.columnFilter.sourceColumnToVisibleRowHeadedColumn(col)];\n
  }\n
};\n
WalkontableTable.prototype.getRowHeader = function(row) {\n
  if (this.columnFilter.sourceColumnToVisibleRowHeadedColumn(0) === 0) {\n
    return null;\n
  }\n
  var TR = this.TBODY.childNodes[this.rowFilter.sourceToRendered(row)];\n
  if (TR) {\n
    return TR.childNodes[0];\n
  }\n
};\n
WalkontableTable.prototype.getCoords = function(TD) {\n
  var TR = TD.parentNode;\n
  var row = dom.index(TR);\n
  if (TR.parentNode === this.THEAD) {\n
    row = this.rowFilter.visibleColHeadedRowToSourceRow(row);\n
  } else {\n
    row = this.rowFilter.renderedToSource(row);\n
  }\n
  return new WalkontableCellCoords(row, this.columnFilter.visibleRowHeadedColumnToSourceColumn(TD.cellIndex));\n
};\n
WalkontableTable.prototype.getTrForRow = function(row) {\n
  return this.TBODY.childNodes[this.rowFilter.sourceToRendered(row)];\n
};\n
WalkontableTable.prototype.getFirstRenderedRow = function() {\n
  return this.instance.wtViewport.rowsRenderCalculator.startRow;\n
};\n
WalkontableTable.prototype.getFirstVisibleRow = function() {\n
  return this.instance.wtViewport.rowsVisibleCalculator.startRow;\n
};\n
WalkontableTable.prototype.getFirstRenderedColumn = function() {\n
  return this.instance.wtViewport.columnsRenderCalculator.startColumn;\n
};\n
WalkontableTable.prototype.getFirstVisibleColumn = function() {\n
  return this.instance.wtViewport.columnsVisibleCalculator.startColumn;\n
};\n
WalkontableTable.prototype.getLastRenderedRow = function() {\n
  return this.instance.wtViewport.rowsRenderCalculator.endRow;\n
};\n
WalkontableTable.prototype.getLastVisibleRow = function() {\n
  return this.instance.wtViewport.rowsVisibleCalculator.endRow;\n
};\n
WalkontableTable.prototype.getLastRenderedColumn = function() {\n
  return this.instance.wtViewport.columnsRenderCalculator.endColumn;\n
};\n
WalkontableTable.prototype.getLastVisibleColumn = function() {\n
  return this.instance.wtViewport.columnsVisibleCalculator.endColumn;\n
};\n
WalkontableTable.prototype.isRowBeforeRenderedRows = function(r) {\n
  return (this.rowFilter.sourceToRendered(r) < 0 && r >= 0);\n
};\n
WalkontableTable.prototype.isRowAfterViewport = function(r) {\n
  return (r > this.getLastVisibleRow());\n
};\n
WalkontableTable.prototype.isRowAfterRenderedRows = function(r) {\n
  return (r > this.getLastRenderedRow());\n
};\n
WalkontableTable.prototype.isColumnBeforeViewport = function(c) {\n
  return (this.columnFilter.sourceToRendered(c) < 0 && c >= 0);\n
};\n
WalkontableTable.prototype.isColumnAfterViewport = function(c) {\n
  return (c > this.getLastVisibleColumn());\n
};\n
WalkontableTable.prototype.isLastRowFullyVisible = function() {\n
  return (this.getLastVisibleRow() === this.getLastRenderedRow());\n
};\n
WalkontableTable.prototype.isLastColumnFullyVisible = function() {\n
  return (this.getLastVisibleColumn() === this.getLastRenderedColumn);\n
};\n
WalkontableTable.prototype.getRenderedColumnsCount = function() {\n
  if (this.instance.cloneOverlay instanceof WalkontableDebugOverlay) {\n
    return this.instance.getSetting(\'totalColumns\');\n
  } else if (this.instance.cloneOverlay instanceof WalkontableLeftOverlay || this.instance.cloneOverlay instanceof WalkontableCornerOverlay) {\n
    return this.instance.getSetting(\'fixedColumnsLeft\');\n
  } else {\n
    return this.instance.wtViewport.columnsRenderCalculator.count;\n
  }\n
};\n
WalkontableTable.prototype.getRenderedRowsCount = function() {\n
  if (this.instance.cloneOverlay instanceof WalkontableDebugOverlay) {\n
    return this.instance.getSetting(\'totalRows\');\n
  } else if (this.instance.cloneOverlay instanceof WalkontableTopOverlay || this.instance.cloneOverlay instanceof WalkontableCornerOverlay) {\n
    return this.instance.getSetting(\'fixedRowsTop\');\n
  }\n
  return this.instance.wtViewport.rowsRenderCalculator.count;\n
};\n
WalkontableTable.prototype.getVisibleRowsCount = function() {\n
  return this.instance.wtViewport.rowsVisibleCalculator.count;\n
};\n
WalkontableTable.prototype.allRowsInViewport = function() {\n
  return this.instance.getSetting(\'totalRows\') == this.getVisibleRowsCount();\n
};\n
WalkontableTable.prototype.getRowHeight = function(sourceRow) {\n
  var height = this.instance.wtSettings.settings.rowHeight(sourceRow),\n
      oversizedHeight = this.instance.wtViewport.oversizedRows[sourceRow];\n
  if (oversizedHeight !== void 0) {\n
    height = height ? Math.max(height, oversizedHeight) : oversizedHeight;\n
  }\n
  return height;\n
};\n
WalkontableTable.prototype.getColumnHeaderHeight = function(level) {\n
  var height = this.instance.wtSettings.settings.defaultRowHeight,\n
      oversizedHeight = this.instance.wtViewport.oversizedColumnHeaders[level];\n
  if (oversizedHeight !== void 0) {\n
    height = height ? Math.max(height, oversizedHeight) : oversizedHeight;\n
  }\n
  return height;\n
};\n
WalkontableTable.prototype.getVisibleColumnsCount = function() {\n
  return this.instance.wtViewport.columnsVisibleCalculator.count;\n
};\n
WalkontableTable.prototype.allColumnsInViewport = function() {\n
  return this.instance.getSetting(\'totalColumns\') == this.getVisibleColumnsCount();\n
};\n
WalkontableTable.prototype.getColumnWidth = function(sourceColumn) {\n
  var width = this.instance.wtSettings.settings.columnWidth;\n
  if (typeof width === \'function\') {\n
    width = width(sourceColumn);\n
  } else if (typeof width === \'object\') {\n
    width = width[sourceColumn];\n
  }\n
  var oversizedWidth = this.instance.wtViewport.oversizedCols[sourceColumn];\n
  if (oversizedWidth !== void 0) {\n
    width = width ? Math.max(width, oversizedWidth) : oversizedWidth;\n
  }\n
  return width;\n
};\n
WalkontableTable.prototype.getStretchedColumnWidth = function(sourceColumn) {\n
  var width = this.getColumnWidth(sourceColumn) || this.instance.wtSettings.settings.defaultColumnWidth,\n
      calculator = this.instance.wtViewport.columnsRenderCalculator,\n
      stretchedWidth;\n
  if (calculator) {\n
    stretchedWidth = calculator.getStretchedColumnWidth(sourceColumn, width);\n
    if (stretchedWidth) {\n
      width = stretchedWidth;\n
    }\n
  }\n
  return width;\n
};\n
;\n
window.WalkontableTable = WalkontableTable;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./cell/coords.js":9,"./cell/range.js":10,"./filter/column.js":13,"./filter/row.js":14,"./overlay/corner.js":16,"./overlay/debug.js":17,"./overlay/left.js":18,"./overlay/top.js":19,"./tableRenderer.js":25}],25:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableTableRenderer: {get: function() {\n
      return WalkontableTableRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var isRenderedColumnHeaders = {};\n
var WalkontableTableRenderer = function WalkontableTableRenderer(wtTable) {\n
  this.wtTable = wtTable;\n
  this.wot = wtTable.instance;\n
  this.instance = wtTable.instance;\n
  this.rowFilter = wtTable.rowFilter;\n
  this.columnFilter = wtTable.columnFilter;\n
  this.TABLE = wtTable.TABLE;\n
  this.THEAD = wtTable.THEAD;\n
  this.TBODY = wtTable.TBODY;\n
  this.COLGROUP = wtTable.COLGROUP;\n
  this.rowHeaders = [];\n
  this.rowHeaderCount = 0;\n
  this.columnHeaders = [];\n
  this.columnHeaderCount = 0;\n
  this.fixedRowsTop = 0;\n
  this.block = false;\n
};\n
($traceurRuntime.createClass)(WalkontableTableRenderer, {\n
  render: function() {\n
    if (!this.wtTable.isWorkingOnClone()) {\n
      this.wot.getSetting(\'beforeDraw\', true);\n
    }\n
    this.rowHeaders = this.wot.getSetting(\'rowHeaders\');\n
    this.rowHeaderCount = this.rowHeaders.length;\n
    this.fixedRowsTop = this.wot.getSetting(\'fixedRowsTop\');\n
    this.columnHeaders = this.wot.getSetting(\'columnHeaders\');\n
    this.columnHeaderCount = this.columnHeaders.length;\n
    var columnsToRender = this.wtTable.getRenderedColumnsCount();\n
    var rowsToRender = this.wtTable.getRenderedRowsCount();\n
    var totalColumns = this.wot.getSetting(\'totalColumns\');\n
    var totalRows = this.wot.getSetting(\'totalRows\');\n
    var workspaceWidth;\n
    var adjusted = false;\n
    if (totalColumns > 0) {\n
      this.adjustAvailableNodes();\n
      adjusted = true;\n
      this.renderColGroups();\n
      this.renderColumnHeaders();\n
      this.renderRows(totalRows, rowsToRender, columnsToRender);\n
      if (!this.wtTable.isWorkingOnClone()) {\n
        workspaceWidth = this.wot.wtViewport.getWorkspaceWidth();\n
        this.wot.wtViewport.containerWidth = null;\n
      } else {\n
        this.adjustColumnHeaderHeights();\n
      }\n
      this.adjustColumnWidths(columnsToRender);\n
    }\n
    if (!adjusted) {\n
      this.adjustAvailableNodes();\n
    }\n
    this.removeRedundantRows(rowsToRender);\n
    if (!this.wtTable.isWorkingOnClone()) {\n
      this.markOversizedRows();\n
      this.wot.wtViewport.createVisibleCalculators();\n
      this.wot.wtOverlays.applyToDOM();\n
      this.wot.wtOverlays.refresh(false);\n
      if (workspaceWidth !== this.wot.wtViewport.getWorkspaceWidth()) {\n
        this.wot.wtViewport.containerWidth = null;\n
        var firstRendered = this.wtTable.getFirstRenderedColumn();\n
        var lastRendered = this.wtTable.getLastRenderedColumn();\n
        for (var i = firstRendered; i < lastRendered; i++) {\n
          var width = this.wtTable.getStretchedColumnWidth(i);\n
          var renderedIndex = this.columnFilter.sourceToRendered(i);\n
          this.COLGROUP.childNodes[renderedIndex + this.rowHeaderCount].style.width = width + \'px\';\n
        }\n
      }\n
      this.wot.getSetting(\'onDraw\', true);\n
    }\n
  },\n
  removeRedundantRows: function(renderedRowsCount) {\n
    while (this.wtTable.tbodyChildrenLength > renderedRowsCount) {\n
      this.TBODY.removeChild(this.TBODY.lastChild);\n
      this.wtTable.tbodyChildrenLength--;\n
    }\n
  },\n
  renderRows: function(totalRows, rowsToRender, columnsToRender) {\n
    var lastTD,\n
        TR;\n
    var visibleRowIndex = 0;\n
    var sourceRowIndex = this.rowFilter.renderedToSource(visibleRowIndex);\n
    var isWorkingOnClone = this.wtTable.isWorkingOnClone();\n
    while (sourceRowIndex < totalRows && sourceRowIndex >= 0) {\n
      if (visibleRowIndex > 1000) {\n
        throw new Error(\'Security brake: Too much TRs. Please define height for your table, which will enforce scrollbars.\');\n
      }\n
      if (rowsToRender !== void 0 && visibleRowIndex === rowsToRender) {\n
        break;\n
      }\n
      TR = this.getOrCreateTrForRow(visibleRowIndex, TR);\n
      this.renderRowHeaders(sourceRowIndex, TR);\n
      this.adjustColumns(TR, columnsToRender + this.rowHeaderCount);\n
      lastTD = this.renderCells(sourceRowIndex, TR, columnsToRender);\n
      if (!isWorkingOnClone) {\n
        this.resetOversizedRow(sourceRowIndex);\n
      }\n
      if (TR.firstChild) {\n
        var height = this.wot.wtTable.getRowHeight(sourceRowIndex);\n
        if (height) {\n
          TR.firstChild.style.height = height + \'px\';\n
        } else {\n
          TR.firstChild.style.height = \'\';\n
        }\n
      }\n
      visibleRowIndex++;\n
      sourceRowIndex = this.rowFilter.renderedToSource(visibleRowIndex);\n
    }\n
  },\n
  resetOversizedRow: function(sourceRow) {\n
    if (this.wot.wtViewport.oversizedRows && this.wot.wtViewport.oversizedRows[sourceRow]) {\n
      this.wot.wtViewport.oversizedRows[sourceRow] = void 0;\n
    }\n
  },\n
  markOversizedRows: function() {\n
    var rowCount = this.instance.wtTable.TBODY.childNodes.length;\n
    var expectedTableHeight = rowCount * this.instance.wtSettings.settings.defaultRowHeight;\n
    var actualTableHeight = dom.innerHeight(this.instance.wtTable.TBODY) - 1;\n
    var previousRowHeight;\n
    var rowInnerHeight;\n
    var sourceRowIndex;\n
    var currentTr;\n
    var rowHeader;\n
    if (expectedTableHeight === actualTableHeight) {\n
      return;\n
    }\n
    while (rowCount) {\n
      rowCount--;\n
      sourceRowIndex = this.instance.wtTable.rowFilter.renderedToSource(rowCount);\n
      previousRowHeight = this.instance.wtTable.getRowHeight(sourceRowIndex);\n
      currentTr = this.instance.wtTable.getTrForRow(sourceRowIndex);\n
      rowHeader = currentTr.querySelector(\'th\');\n
      if (rowHeader) {\n
        rowInnerHeight = dom.innerHeight(rowHeader);\n
      } else {\n
        rowInnerHeight = dom.innerHeight(currentTr) - 1;\n
      }\n
      if ((!previousRowHeight && this.instance.wtSettings.settings.defaultRowHeight < rowInnerHeight || previousRowHeight < rowInnerHeight)) {\n
        this.instance.wtViewport.oversizedRows[sourceRowIndex] = rowInnerHeight;\n
      }\n
    }\n
  },\n
  adjustColumnHeaderHeights: function() {\n
    var columnHeaders = this.wot.getSetting(\'columnHeaders\');\n
    var childs = this.wot.wtTable.THEAD.childNodes;\n
    var oversizedCols = this.wot.wtViewport.oversizedColumnHeaders;\n
    for (var i = 0,\n
        len = columnHeaders.length; i < len; i++) {\n
      if (oversizedCols[i]) {\n
        if (childs[i].childNodes.length === 0) {\n
          return;\n
        }\n
        childs[i].childNodes[0].style.height = oversizedCols[i] + \'px\';\n
      }\n
    }\n
  },\n
  markIfOversizedColumnHeader: function(col) {\n
    var level = this.wot.getSetting(\'columnHeaders\').length;\n
    var defaultRowHeight = this.wot.wtSettings.settings.defaultRowHeight;\n
    var sourceColIndex;\n
    var previousColHeaderHeight;\n
    var currentHeader;\n
    var currentHeaderHeight;\n
    sourceColIndex = this.wot.wtTable.columnFilter.renderedToSource(col);\n
    while (level) {\n
      level--;\n
      previousColHeaderHeight = this.wot.wtTable.getColumnHeaderHeight(level);\n
      currentHeader = this.wot.wtTable.getColumnHeader(sourceColIndex, level);\n
      if (!currentHeader) {\n
        continue;\n
      }\n
      currentHeaderHeight = dom.innerHeight(currentHeader);\n
      if (!previousColHeaderHeight && defaultRowHeight < currentHeaderHeight || previousColHeaderHeight < currentHeaderHeight) {\n
        this.wot.wtViewport.oversizedColumnHeaders[level] = currentHeaderHeight;\n
      }\n
    }\n
  },\n
  renderCells: function(sourceRowIndex, TR, columnsToRender) {\n
    var TD;\n
    var sourceColIndex;\n
    for (var visibleColIndex = 0; visibleColIndex < columnsToRender; visibleColIndex++) {\n
      sourceColIndex = this.columnFilter.renderedToSource(visibleColIndex);\n
      if (visibleColIndex === 0) {\n
        TD = TR.childNodes[this.columnFilter.sourceColumnToVisibleRowHeadedColumn(sourceColIndex)];\n
      } else {\n
        TD = TD.nextSibling;\n
      }\n
      if (TD.nodeName == \'TH\') {\n
        TD = replaceThWithTd(TD, TR);\n
      }\n
      if (!dom.hasClass(TD, \'hide\')) {\n
        TD.className = \'\';\n
      }\n
      TD.removeAttribute(\'style\');\n
      this.wot.wtSettings.settings.cellRenderer(sourceRowIndex, sourceColIndex, TD);\n
    }\n
    return TD;\n
  },\n
  adjustColumnWidths: function(columnsToRender) {\n
    var scrollbarCompensation = 0;\n
    var sourceInstance = this.wot.cloneSource ? this.wot.cloneSource : this.wot;\n
    var mainHolder = sourceInstance.wtTable.holder;\n
    if (mainHolder.offsetHeight < mainHolder.scrollHeight) {\n
      scrollbarCompensation = dom.getScrollbarWidth();\n
    }\n
    this.wot.wtViewport.columnsRenderCalculator.refreshStretching(this.wot.wtViewport.getViewportWidth() - scrollbarCompensation);\n
    for (var renderedColIndex = 0; renderedColIndex < columnsToRender; renderedColIndex++) {\n
      var width = this.wtTable.getStretchedColumnWidth(this.columnFilter.renderedToSource(renderedColIndex));\n
      this.COLGROUP.childNodes[renderedColIndex + this.rowHeaderCount].style.width = width + \'px\';\n
    }\n
  },\n
  appendToTbody: function(TR) {\n
    this.TBODY.appendChild(TR);\n
    this.wtTable.tbodyChildrenLength++;\n
  },\n
  getOrCreateTrForRow: function(rowIndex, currentTr) {\n
    var TR;\n
    if (rowIndex >= this.wtTable.tbodyChildrenLength) {\n
      TR = this.createRow();\n
      this.appendToTbody(TR);\n
    } else if (rowIndex === 0) {\n
      TR = this.TBODY.firstChild;\n
    } else {\n
      TR = currentTr.nextSibling;\n
    }\n
    return TR;\n
  },\n
  createRow: function() {\n
    var TR = document.createElement(\'TR\');\n
    for (var visibleColIndex = 0; visibleColIndex < this.rowHeaderCount; visibleColIndex++) {\n
      TR.appendChild(document.createElement(\'TH\'));\n
    }\n
    return TR;\n
  },\n
  renderRowHeader: function(row, col, TH) {\n
    TH.className = \'\';\n
    TH.removeAttribute(\'style\');\n
    this.rowHeaders[col](row, TH, col);\n
  },\n
  renderRowHeaders: function(row, TR) {\n
    for (var TH = TR.firstChild,\n
        visibleColIndex = 0; visibleColIndex < this.rowHeaderCount; visibleColIndex++) {\n
      if (!TH) {\n
        TH = document.createElement(\'TH\');\n
        TR.appendChild(TH);\n
      } else if (TH.nodeName == \'TD\') {\n
        TH = replaceTdWithTh(TH, TR);\n
      }\n
      this.renderRowHeader(row, visibleColIndex, TH);\n
      TH = TH.nextSibling;\n
    }\n
  },\n
  adjustAvailableNodes: function() {\n
    this.adjustColGroups();\n
    this.adjustThead();\n
  },\n
  renderColumnHeaders: function() {\n
    var overlayName = this.wot.getOverlayName();\n
    if (!this.columnHeaderCount) {\n
      return;\n
    }\n
    var columnCount = this.wtTable.getRenderedColumnsCount();\n
    for (var i = 0; i < this.columnHeaderCount; i++) {\n
      var TR = this.getTrForColumnHeaders(i);\n
      for (var renderedColumnIndex = (-1) * this.rowHeaderCount; renderedColumnIndex < columnCount; renderedColumnIndex++) {\n
        var sourceCol = this.columnFilter.renderedToSource(renderedColumnIndex);\n
        this.renderColumnHeader(i, sourceCol, TR.childNodes[renderedColumnIndex + this.rowHeaderCount]);\n
        if (!isRenderedColumnHeaders[overlayName] && !this.wtTable.isWorkingOnClone()) {\n
          this.markIfOversizedColumnHeader(renderedColumnIndex);\n
        }\n
      }\n
    }\n
    isRenderedColumnHeaders[overlayName] = true;\n
  },\n
  adjustColGroups: function() {\n
    var columnCount = this.wtTable.getRenderedColumnsCount();\n
    while (this.wtTable.colgroupChildrenLength < columnCount + this.rowHeaderCount) {\n
      this.COLGROUP.appendChild(document.createElement(\'COL\'));\n
      this.wtTable.colgroupChildrenLength++;\n
    }\n
    while (this.wtTable.colgroupChildrenLength > columnCount + this.rowHeaderCount) {\n
      this.COLGROUP.removeChild(this.COLGROUP.lastChild);\n
      this.wtTable.colgroupChildrenLength--;\n
    }\n
  },\n
  adjustThead: function() {\n
    var columnCount = this.wtTable.getRenderedColumnsCount();\n
    var TR = this.THEAD.firstChild;\n
    if (this.columnHeaders.length) {\n
      for (var i = 0,\n
          len = this.columnHeaders.length; i < len; i++) {\n
        TR = this.THEAD.childNodes[i];\n
        if (!TR) {\n
          TR = document.createElement(\'TR\');\n
          this.THEAD.appendChild(TR);\n
        }\n
        this.theadChildrenLength = TR.childNodes.length;\n
        while (this.theadChildrenLength < columnCount + this.rowHeaderCount) {\n
          TR.appendChild(document.createElement(\'TH\'));\n
          this.theadChildrenLength++;\n
        }\n
        while (this.theadChildrenLength > columnCount + this.rowHeaderCount) {\n
          TR.removeChild(TR.lastChild);\n
          this.theadChildrenLength--;\n
        }\n
      }\n
      var theadChildrenLength = this.THEAD.childNodes.length;\n
      if (theadChildrenLength > this.columnHeaders.length) {\n
        for (var i$__1 = this.columnHeaders.length; i$__1 < theadChildrenLength; i$__1++) {\n
          this.THEAD.removeChild(this.THEAD.lastChild);\n
        }\n
      }\n
    } else if (TR) {\n
      dom.empty(TR);\n
    }\n
  },\n
  getTrForColumnHeaders: function(index) {\n
    return this.THEAD.childNodes[index];\n
  },\n
  renderColumnHeader: function(row, col, TH) {\n
    TH.className = \'\';\n
    TH.removeAttribute(\'style\');\n
    return this.columnHeaders[row](col, TH, row);\n
  },\n
  renderColGroups: function() {\n
    for (var colIndex = 0; colIndex < this.wtTable.colgroupChildrenLength; colIndex++) {\n
      if (colIndex < this.rowHeaderCount) {\n
        dom.addClass(this.COLGROUP.childNodes[colIndex], \'rowHeader\');\n
      } else {\n
        dom.removeClass(this.COLGROUP.childNodes[colIndex], \'rowHeader\');\n
      }\n
    }\n
  },\n
  adjustColumns: function(TR, desiredCount) {\n
    var count = TR.childNodes.length;\n
    while (count < desiredCount) {\n
      var TD = document.createElement(\'TD\');\n
      TR.appendChild(TD);\n
      count++;\n
    }\n
    while (count > desiredCount) {\n
      TR.removeChild(TR.lastChild);\n
      count--;\n
    }\n
  },\n
  removeRedundantColumns: function(columnsToRender) {\n
    while (this.wtTable.tbodyChildrenLength > columnsToRender) {\n
      this.TBODY.removeChild(this.TBODY.lastChild);\n
      this.wtTable.tbodyChildrenLength--;\n
    }\n
  }\n
}, {});\n
function replaceTdWithTh(TD, TR) {\n
  var TH = document.createElement(\'TH\');\n
  TR.insertBefore(TH, TD);\n
  TR.removeChild(TD);\n
  return TH;\n
}\n
function replaceThWithTd(TH, TR) {\n
  var TD = document.createElement(\'TD\');\n
  TR.insertBefore(TD, TH);\n
  TR.removeChild(TH);\n
  return TD;\n
}\n
;\n
window.WalkontableTableRenderer = WalkontableTableRenderer;\n
\n
\n
//# \n
},{"./../../../dom.js":31}],26:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  WalkontableViewport: {get: function() {\n
      return WalkontableViewport;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47__46__46__47_eventManager_46_js__,\n
    $__calculator_47_viewportColumns_46_js__,\n
    $__calculator_47_viewportRows_46_js__;\n
var dom = ($___46__46__47__46__46__47__46__46__47_dom_46_js__ = require("./../../../dom.js"), $___46__46__47__46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47__46__46__47_eventManager_46_js__ = require("./../../../eventManager.js"), $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var WalkontableViewportColumnsCalculator = ($__calculator_47_viewportColumns_46_js__ = require("./calculator/viewportColumns.js"), $__calculator_47_viewportColumns_46_js__ && $__calculator_47_viewportColumns_46_js__.__esModule && $__calculator_47_viewportColumns_46_js__ || {default: $__calculator_47_viewportColumns_46_js__}).WalkontableViewportColumnsCalculator;\n
var WalkontableViewportRowsCalculator = ($__calculator_47_viewportRows_46_js__ = require("./calculator/viewportRows.js"), $__calculator_47_viewportRows_46_js__ && $__calculator_47_viewportRows_46_js__.__esModule && $__calculator_47_viewportRows_46_js__ || {default: $__calculator_47_viewportRows_46_js__}).WalkontableViewportRowsCalculator;\n
var WalkontableViewport = function WalkontableViewport(wotInstance) {\n
  var $__3 = this;\n
  this.wot = wotInstance;\n
  this.instance = this.wot;\n
  this.oversizedRows = [];\n
  this.oversizedCols = [];\n
  this.oversizedColumnHeaders = [];\n
  this.clientHeight = 0;\n
  this.containerWidth = NaN;\n
  this.rowHeaderWidth = NaN;\n
  this.rowsVisibleCalculator = null;\n
  this.columnsVisibleCalculator = null;\n
  var eventManager = eventManagerObject(wotInstance);\n
  eventManager.addEventListener(window, \'resize\', (function() {\n
    $__3.clientHeight = $__3.getWorkspaceHeight();\n
  }));\n
};\n
($traceurRuntime.createClass)(WalkontableViewport, {\n
  getWorkspaceHeight: function() {\n
    var trimmingContainer = this.instance.wtOverlays.topOverlay.trimmingContainer;\n
    var elemHeight;\n
    var height = 0;\n
    if (trimmingContainer === window) {\n
      height = document.documentElement.clientHeight;\n
    } else {\n
      elemHeight = dom.outerHeight(trimmingContainer);\n
      height = (elemHeight > 0 && trimmingContainer.clientHeight > 0) ? trimmingContainer.clientHeight : Infinity;\n
    }\n
    return height;\n
  },\n
  getWorkspaceWidth: function() {\n
    var width;\n
    var totalColumns = this.instance.getSetting("totalColumns");\n
    var trimmingContainer = this.instance.wtOverlays.leftOverlay.trimmingContainer;\n
    var overflow;\n
    var stretchSetting = this.instance.getSetting(\'stretchH\');\n
    var docOffsetWidth = document.documentElement.offsetWidth;\n
    if (Handsontable.freezeOverlays) {\n
      width = Math.min(docOffsetWidth - this.getWorkspaceOffset().left, docOffsetWidth);\n
    } else {\n
      width = Math.min(this.getContainerFillWidth(), docOffsetWidth - this.getWorkspaceOffset().left, docOffsetWidth);\n
    }\n
    if (trimmingContainer === window && totalColumns > 0 && this.sumColumnWidths(0, totalColumns - 1) > width) {\n
      return document.documentElement.clientWidth;\n
    }\n
    if (trimmingContainer !== window) {\n
      overflow = dom.getStyle(this.instance.wtOverlays.leftOverlay.trimmingContainer, \'overflow\');\n
      if (overflow == "scroll" || overflow == "hidden" || overflow == "auto") {\n
        return Math.max(width, trimmingContainer.clientWidth);\n
      }\n
    }\n
    if (stretchSetting === \'none\' || !stretchSetting) {\n
      return Math.max(width, dom.outerWidth(this.instance.wtTable.TABLE));\n
    } else {\n
      return width;\n
    }\n
  },\n
  sumColumnWidths: function(from, length) {\n
    var sum = 0;\n
    var defaultColumnWidth = this.instance.wtSettings.defaultColumnWidth;\n
    while (from < length) {\n
      sum += this.wot.wtTable.getColumnWidth(from) || defaultColumnWidth;\n
      from++;\n
    }\n
    return sum;\n
  },\n
  getContainerFillWidth: function() {\n
    if (this.containerWidth) {\n
      return this.containerWidth;\n
    }\n
    var mainContainer = this.instance.wtTable.holder;\n
    var fillWidth;\n
    var dummyElement;\n
    dummyElement = document.createElement("DIV");\n
    dummyElement.style.width = "100%";\n
    dummyElement.style.height = "1px";\n
    mainContainer.appendChild(dummyElement);\n
    fillWidth = dummyElement.offsetWidth;\n
    this.containerWidth = fillWidth;\n
    mainContainer.removeChild(dummyElement);\n
    return fillWidth;\n
  },\n
  getWorkspaceOffset: function() {\n
    return dom.offset(this.wot.wtTable.TABLE);\n
  },\n
  getWorkspaceActualHeight: function() {\n
    return dom.outerHeight(this.wot.wtTable.TABLE);\n
  },\n
  getWorkspaceActualWidth: function() {\n
    return dom.outerWidth(this.wot.wtTable.TABLE) || dom.outerWidth(this.wot.wtTable.TBODY) || dom.outerWidth(this.wot.wtTable.THEAD);\n
  },\n
  getColumnHeaderHeight: function() {\n
    if (isNaN(this.columnHeaderHeight)) {\n
      this.columnHeaderHeight = dom.outerHeight(this.wot.wtTable.THEAD);\n
    }\n
    return this.columnHeaderHeight;\n
  },\n
  getViewportHeight: function() {\n
    var containerHeight = this.getWorkspaceHeight();\n
    var columnHeaderHeight;\n
    if (containerHeight === Infinity) {\n
      return containerHeight;\n
    }\n
    columnHeaderHeight = this.getColumnHeaderHeight();\n
    if (columnHeaderHeight > 0) {\n
      containerHeight -= columnHeaderHeight;\n
    }\n
    return containerHeight;\n
  },\n
  getRowHeaderWidth: function() {\n
    if (this.wot.cloneSource) {\n
      return this.wot.cloneSource.wtViewport.getRowHeaderWidth();\n
    }\n
    if (isNaN(this.rowHeaderWidth)) {\n
      var rowHeaders = this.instance.getSetting(\'rowHeaders\');\n
      if (rowHeaders.length) {\n
        var TH = this.instance.wtTable.TABLE.querySelector(\'TH\');\n
        this.rowHeaderWidth = 0;\n
        for (var i = 0,\n
            len = rowHeaders.length; i < len; i++) {\n
          if (TH) {\n
            this.rowHeaderWidth += dom.outerWidth(TH);\n
            TH = TH.nextSibling;\n
          } else {\n
            this.rowHeaderWidth += 50;\n
          }\n
        }\n
      } else {\n
        this.rowHeaderWidth = 0;\n
      }\n
    }\n
    return this.rowHeaderWidth;\n
  },\n
  getViewportWidth: function() {\n
    var containerWidth = this.getWorkspaceWidth();\n
    var rowHeaderWidth;\n
    if (containerWidth === Infinity) {\n
      return containerWidth;\n
    }\n
    rowHeaderWidth = this.getRowHeaderWidth();\n
    if (rowHeaderWidth > 0) {\n
      return containerWidth - rowHeaderWidth;\n
    }\n
    return containerWidth;\n
  },\n
  createRowsCalculator: function() {\n
    var visible = arguments[0] !== (void 0) ? arguments[0] : false;\n
    var $__3 = this;\n
    var height;\n
    var pos;\n
    var fixedRowsTop;\n
    this.rowHeaderWidth = NaN;\n
    if (this.wot.wtSettings.settings.renderAllRows) {\n
      height = Infinity;\n
    } else {\n
      height = this.getViewportHeight();\n
    }\n
    pos = dom.getScrollTop(this.wot.wtOverlays.mainTableScrollableElement) - this.wot.wtOverlays.topOverlay.getTableParentOffset();\n
    if (pos < 0) {\n
      pos = 0;\n
    }\n
    fixedRowsTop = this.wot.getSetting(\'fixedRowsTop\');\n
    if (fixedRowsTop) {\n
      var fixedRowsHeight = this.wot.wtOverlays.topOverlay.sumCellSizes(0, fixedRowsTop);\n
      pos += fixedRowsHeight;\n
      height -= fixedRowsHeight;\n
    }\n
    return new WalkontableViewportRowsCalculator(height, pos, this.wot.getSetting(\'totalRows\'), (function(sourceRow) {\n
      return $__3.wot.wtTable.getRowHeight(sourceRow);\n
    }), visible ? null : this.wot.wtSettings.settings.viewportRowCalculatorOverride, visible);\n
  },\n
  createColumnsCalculator: function() {\n
    var visible = arguments[0] !== (void 0) ? arguments[0] : false;\n
    var $__3 = this;\n
    var width = this.getViewportWidth();\n
    var pos;\n
    var fixedColumnsLeft;\n
    this.columnHeaderHeight = NaN;\n
    pos = this.wot.wtOverlays.leftOverlay.getScrollPosition() - this.wot.wtOverlays.topOverlay.getTableParentOffset();\n
    if (pos < 0) {\n
      pos = 0;\n
    }\n
    fixedColumnsLeft = this.wot.getSetting(\'fixedColumnsLeft\');\n
    if (fixedColumnsLeft) {\n
      var fixedColumnsWidth = this.wot.wtOverlays.leftOverlay.sumCellSizes(0, fixedColumnsLeft);\n
      pos += fixedColumnsWidth;\n
      width -= fixedColumnsWidth;\n
    }\n
    if (this.wot.wtTable.holder.clientWidth !== this.wot.wtTable.holder.offsetWidth) {\n
      width -= dom.getScrollbarWidth();\n
    }\n
    return new WalkontableViewportColumnsCalculator(width, pos, this.wot.getSetting(\'totalColumns\'), (function(sourceCol) {\n
      return $__3.wot.wtTable.getColumnWidth(sourceCol);\n
    }), visible ? null : this.wot.wtSettings.settings.viewportColumnCalculatorOverride, visible, this.wot.getSetting(\'stretchH\'));\n
  },\n
  createRenderCalculators: function() {\n
    var fastDraw = arguments[0] !== (void 0) ? arguments[0] : false;\n
    if (fastDraw) {\n
      var proposedRowsVisibleCalculator = this.createRowsCalculator(true);\n
      var proposedColumnsVisibleCalculator = this.createColumnsCalculator(true);\n
      if (!(this.areAllProposedVisibleRowsAlreadyRendered(proposedRowsVisibleCalculator) && this.areAllProposedVisibleColumnsAlreadyRendered(proposedColumnsVisibleCalculator))) {\n
        fastDraw = false;\n
      }\n
    }\n
    if (!fastDraw) {\n
      this.rowsRenderCalculator = this.createRowsCalculator();\n
      this.columnsRenderCalculator = this.createColumnsCalculator();\n
    }\n
    this.rowsVisibleCalculator = null;\n
    this.columnsVisibleCalculator = null;\n
    return fastDraw;\n
  },\n
  createVisibleCalculators: function() {\n
    this.rowsVisibleCalculator = this.createRowsCalculator(true);\n
    this.columnsVisibleCalculator = this.createColumnsCalculator(true);\n
  },\n
  areAllProposedVisibleRowsAlreadyRendered: function(proposedRowsVisibleCalculator) {\n
    if (this.rowsVisibleCalculator) {\n
      if (proposedRowsVisibleCalculator.startRow < this.rowsRenderCalculator.startRow || (proposedRowsVisibleCalculator.startRow === this.rowsRenderCalculator.startRow && proposedRowsVisibleCalculator.startRow > 0)) {\n
        return false;\n
      } else if (proposedRowsVisibleCalculator.endRow > this.rowsRenderCalculator.endRow || (proposedRowsVisibleCalculator.endRow === this.rowsRenderCalculator.endRow && proposedRowsVisibleCalculator.endRow < this.wot.getSetting(\'totalRows\') - 1)) {\n
        return false;\n
      } else {\n
        return true;\n
      }\n
    }\n
    return false;\n
  },\n
  areAllProposedVisibleColumnsAlreadyRendered: function(proposedColumnsVisibleCalculator) {\n
    if (this.columnsVisibleCalculator) {\n
      if (proposedColumnsVisibleCalculator.startColumn < this.columnsRenderCalculator.startColumn || (proposedColumnsVisibleCalculator.startColumn === this.columnsRenderCalculator.startColumn && proposedColumnsVisibleCalculator.startColumn > 0)) {\n
        return false;\n
      } else if (proposedColumnsVisibleCalculator.endColumn > this.columnsRenderCalculator.endColumn || (proposedColumnsVisibleCalculator.endColumn === this.columnsRenderCalculator.endColumn && proposedColumnsVisibleCalculator.endColumn < this.wot.getSetting(\'totalColumns\') - 1)) {\n
        return false;\n
      } else {\n
        return true;\n
      }\n
    }\n
    return false;\n
  }\n
}, {});\n
;\n
window.WalkontableViewport = WalkontableViewport;\n
\n
\n
//# \n
},{"./../../../dom.js":31,"./../../../eventManager.js":45,"./calculator/viewportColumns.js":7,"./calculator/viewportRows.js":8}],27:[function(require,module,exports){\n
"use strict";\n
var $__shims_47_array_46_filter_46_js__,\n
    $__shims_47_array_46_indexOf_46_js__,\n
    $__shims_47_array_46_isArray_46_js__,\n
    $__shims_47_classes_46_js__,\n
    $__shims_47_object_46_keys_46_js__,\n
    $__shims_47_string_46_trim_46_js__,\n
    $__shims_47_weakmap_46_js__,\n
    $__pluginHooks_46_js__,\n
    $__core_46_js__,\n
    $__renderers_47__95_cellDecorator_46_js__,\n
    $__cellTypes_46_js__,\n
    $___46__46__47_plugins_47_jqueryHandsontable_46_js__;\n
var version = Handsontable.version;\n
window.Handsontable = function(rootElement, userSettings) {\n
  var instance = new Handsontable.Core(rootElement, userSettings || {});\n
  instance.init();\n
  return instance;\n
};\n
Handsontable.version = version;\n
($__shims_47_array_46_filter_46_js__ = require("./shims/array.filter.js"), $__shims_47_array_46_filter_46_js__ && $__shims_47_array_46_filter_46_js__.__esModule && $__shims_47_array_46_filter_46_js__ || {default: $__shims_47_array_46_filter_46_js__});\n
($__shims_47_array_46_indexOf_46_js__ = require("./shims/array.indexOf.js"), $__shims_47_array_46_indexOf_46_js__ && $__shims_47_array_46_indexOf_46_js__.__esModule && $__shims_47_array_46_indexOf_46_js__ || {default: $__shims_47_array_46_indexOf_46_js__});\n
($__shims_47_array_46_isArray_46_js__ = require("./shims/array.isArray.js"), $__shims_47_array_46_isArray_46_js__ && $__shims_47_array_46_isArray_46_js__.__esModule && $__shims_47_array_46_isArray_46_js__ || {default: $__shims_47_array_46_isArray_46_js__});\n
($__shims_47_classes_46_js__ = require("./shims/classes.js"), $__shims_47_classes_46_js__ && $__shims_47_classes_46_js__.__esModule && $__shims_47_classes_46_js__ || {default: $__shims_47_classes_46_js__});\n
($__shims_47_object_46_keys_46_js__ = require("./shims/object.keys.js"), $__shims_47_object_46_keys_46_js__ && $__shims_47_object_46_keys_46_js__.__esModule && $__shims_47_object_46_keys_46_js__ || {default: $__shims_47_object_46_keys_46_js__});\n
($__shims_47_string_46_trim_46_js__ = require("./shims/string.trim.js"), $__shims_47_string_46_trim_46_js__ && $__shims_47_string_46_trim_46_js__.__esModule && $__shims_47_string_46_trim_46_js__ || {default: $__shims_47_string_46_trim_46_js__});\n
($__shims_47_weakmap_46_js__ = require("./shims/weakmap.js"), $__shims_47_weakmap_46_js__ && $__shims_47_weakmap_46_js__.__esModule && $__shims_47_weakmap_46_js__ || {default: $__shims_47_weakmap_46_js__});\n
Handsontable.plugins = {};\n
var PluginHook = ($__pluginHooks_46_js__ = require("./pluginHooks.js"), $__pluginHooks_46_js__ && $__pluginHooks_46_js__.__esModule && $__pluginHooks_46_js__ || {default: $__pluginHooks_46_js__}).PluginHook;\n
if (!Handsontable.hooks) {\n
  Handsontable.hooks = new PluginHook();\n
}\n
($__core_46_js__ = require("./core.js"), $__core_46_js__ && $__core_46_js__.__esModule && $__core_46_js__ || {default: $__core_46_js__});\n
($__renderers_47__95_cellDecorator_46_js__ = require("./renderers/_cellDecorator.js"), $__renderers_47__95_cellDecorator_46_js__ && $__renderers_47__95_cellDecorator_46_js__.__esModule && $__renderers_47__95_cellDecorator_46_js__ || {default: $__renderers_47__95_cellDecorator_46_js__});\n
($__cellTypes_46_js__ = require("./cellTypes.js"), $__cellTypes_46_js__ && $__cellTypes_46_js__.__esModule && $__cellTypes_46_js__ || {default: $__cellTypes_46_js__});\n
($___46__46__47_plugins_47_jqueryHandsontable_46_js__ = require("./../plugins/jqueryHandsontable.js"), $___46__46__47_plugins_47_jqueryHandsontable_46_js__ && $___46__46__47_plugins_47_jqueryHandsontable_46_js__.__esModule && $___46__46__47_plugins_47_jqueryHandsontable_46_js__ || {default: $___46__46__47_plugins_47_jqueryHandsontable_46_js__});\n
\n
\n
//# \n
},{"./../plugins/jqueryHandsontable.js":1,"./cellTypes.js":28,"./core.js":29,"./pluginHooks.js":48,"./renderers/_cellDecorator.js":74,"./shims/array.filter.js":81,"./shims/array.indexOf.js":82,"./shims/array.isArray.js":83,"./shims/classes.js":84,"./shims/object.keys.js":85,"./shims/string.trim.js":86,"./shims/weakmap.js":87}],28:[function(require,module,exports){\n
"use strict";\n
var $__helpers_46_js__,\n
    $__editors_46_js__,\n
    $__renderers_46_js__,\n
    $__editors_47_autocompleteEditor_46_js__,\n
    $__editors_47_checkboxEditor_46_js__,\n
    $__editors_47_dateEditor_46_js__,\n
    $__editors_47_dropdownEditor_46_js__,\n
    $__editors_47_handsontableEditor_46_js__,\n
    $__editors_47_mobileTextEditor_46_js__,\n
    $__editors_47_numericEditor_46_js__,\n
    $__editors_47_passwordEditor_46_js__,\n
    $__editors_47_selectEditor_46_js__,\n
    $__editors_47_textEditor_46_js__,\n
    $__renderers_47_autocompleteRenderer_46_js__,\n
    $__renderers_47_checkboxRenderer_46_js__,\n
    $__renderers_47_htmlRenderer_46_js__,\n
    $__renderers_47_numericRenderer_46_js__,\n
    $__renderers_47_passwordRenderer_46_js__,\n
    $__renderers_47_textRenderer_46_js__,\n
    $__validators_47_autocompleteValidator_46_js__,\n
    $__validators_47_dateValidator_46_js__,\n
    $__validators_47_numericValidator_46_js__;\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
var getEditorConstructor = ($__editors_46_js__ = require("./editors.js"), $__editors_46_js__ && $__editors_46_js__.__esModule && $__editors_46_js__ || {default: $__editors_46_js__}).getEditorConstructor;\n
var getRenderer = ($__renderers_46_js__ = require("./renderers.js"), $__renderers_46_js__ && $__renderers_46_js__.__esModule && $__renderers_46_js__ || {default: $__renderers_46_js__}).getRenderer;\n
var AutocompleteEditor = ($__editors_47_autocompleteEditor_46_js__ = require("./editors/autocompleteEditor.js"), $__editors_47_autocompleteEditor_46_js__ && $__editors_47_autocompleteEditor_46_js__.__esModule && $__editors_47_autocompleteEditor_46_js__ || {default: $__editors_47_autocompleteEditor_46_js__}).AutocompleteEditor;\n
var CheckboxEditor = ($__editors_47_checkboxEditor_46_js__ = require("./editors/checkboxEditor.js"), $__editors_47_checkboxEditor_46_js__ && $__editors_47_checkboxEditor_46_js__.__esModule && $__editors_47_checkboxEditor_46_js__ || {default: $__editors_47_checkboxEditor_46_js__}).CheckboxEditor;\n
var DateEditor = ($__editors_47_dateEditor_46_js__ = require("./editors/dateEditor.js"), $__editors_47_dateEditor_46_js__ && $__editors_47_dateEditor_46_js__.__esModule && $__editors_47_dateEditor_46_js__ || {default: $__editors_47_dateEditor_46_js__}).DateEditor;\n
var DropdownEditor = ($__editors_47_dropdownEditor_46_js__ = require("./editors/dropdownEditor.js"), $__editors_47_dropdownEditor_46_js__ && $__editors_47_dropdownEditor_46_js__.__esModule && $__editors_47_dropdownEditor_46_js__ || {default: $__editors_47_dropdownEditor_46_js__}).DropdownEditor;\n
var HandsontableEditor = ($__editors_47_handsontableEditor_46_js__ = require("./editors/handsontableEditor.js"), $__editors_47_handsontableEditor_46_js__ && $__editors_47_handsontableEditor_46_js__.__esModule && $__editors_47_handsontableEditor_46_js__ || {default: $__editors_47_handsontableEditor_46_js__}).HandsontableEditor;\n
var MobileTextEditor = ($__editors_47_mobileTextEditor_46_js__ = require("./editors/mobileTextEditor.js"), $__editors_47_mobileTextEditor_46_js__ && $__editors_47_mobileTextEditor_46_js__.__esModule && $__editors_47_mobileTextEditor_46_js__ || {default: $__editors_47_mobileTextEditor_46_js__}).MobileTextEditor;\n
var NumericEditor = ($__editors_47_numericEditor_46_js__ = require("./editors/numericEditor.js"), $__editors_47_numericEditor_46_js__ && $__editors_47_numericEditor_46_js__.__esModule && $__editors_47_numericEditor_46_js__ || {default: $__editors_47_numericEditor_46_js__}).NumericEditor;\n
var PasswordEditor = ($__editors_47_passwordEditor_46_js__ = require("./editors/passwordEditor.js"), $__editors_47_passwordEditor_46_js__ && $__editors_47_passwordEditor_46_js__.__esModule && $__editors_47_passwordEditor_46_js__ || {default: $__editors_47_passwordEditor_46_js__}).PasswordEditor;\n
var SelectEditor = ($__editors_47_selectEditor_46_js__ = require("./editors/selectEditor.js"), $__editors_47_selectEditor_46_js__ && $__editors_47_selectEditor_46_js__.__esModule && $__editors_47_selectEditor_46_js__ || {default: $__editors_47_selectEditor_46_js__}).SelectEditor;\n
var TextEditor = ($__editors_47_textEditor_46_js__ = require("./editors/textEditor.js"), $__editors_47_textEditor_46_js__ && $__editors_47_textEditor_46_js__.__esModule && $__editors_47_textEditor_46_js__ || {default: $__editors_47_textEditor_46_js__}).TextEditor;\n
var AutocompleteRenderer = ($__renderers_47_autocompleteRenderer_46_js__ = require("./renderers/autocompleteRenderer.js"), $__renderers_47_autocompleteRenderer_46_js__ && $__renderers_47_autocompleteRenderer_46_js__.__esModule && $__renderers_47_autocompleteRenderer_46_js__ || {default: $__renderers_47_autocompleteRenderer_46_js__}).AutocompleteRenderer;\n
var CheckboxRenderer = ($__renderers_47_checkboxRenderer_46_js__ = require("./renderers/checkboxRenderer.js"), $__renderers_47_checkboxRenderer_46_js__ && $__renderers_47_checkboxRenderer_46_js__.__esModule && $__renderers_47_checkboxRenderer_46_js__ || {default: $__renderers_47_checkboxRenderer_46_js__}).CheckboxRenderer;\n
var HtmlRenderer = ($__renderers_47_htmlRenderer_46_js__ = require("./renderers/htmlRenderer.js"), $__renderers_47_htmlRenderer_46_js__ && $__renderers_47_htmlRenderer_46_js__.__esModule && $__renderers_47_htmlRenderer_46_js__ || {default: $__renderers_47_htmlRenderer_46_js__}).HtmlRenderer;\n
var NumericRenderer = ($__renderers_47_numericRenderer_46_js__ = require("./renderers/numericRenderer.js"), $__renderers_47_numericRenderer_46_js__ && $__renderers_47_numericRenderer_46_js__.__esModule && $__renderers_47_numericRenderer_46_js__ || {default: $__renderers_47_numericRenderer_46_js__}).NumericRenderer;\n
var PasswordRenderer = ($__renderers_47_passwordRenderer_46_js__ = require("./renderers/passwordRenderer.js"), $__renderers_47_passwordRenderer_46_js__ && $__renderers_47_passwordRenderer_46_js__.__esModule && $__renderers_47_passwordRenderer_46_js__ || {default: $__renderers_47_passwordRenderer_46_js__}).PasswordRenderer;\n
var TextRenderer = ($__renderers_47_textRenderer_46_js__ = require("./renderers/textRenderer.js"), $__renderers_47_textRenderer_46_js__ && $__renderers_47_textRenderer_46_js__.__esModule && $__renderers_47_textRenderer_46_js__ || {default: $__renderers_47_textRenderer_46_js__}).TextRenderer;\n
var AutocompleteValidator = ($__validators_47_autocompleteValidator_46_js__ = require("./validators/autocompleteValidator.js"), $__validators_47_autocompleteValidator_46_js__ && $__validators_47_autocompleteValidator_46_js__.__esModule && $__validators_47_autocompleteValidator_46_js__ || {default: $__validators_47_autocompleteValidator_46_js__}).AutocompleteValidator;\n
var DateValidator = ($__validators_47_dateValidator_46_js__ = require("./validators/dateValidator.js"), $__validators_47_dateValidator_46_js__ && $__validators_47_dateValidator_46_js__.__esModule && $__validators_47_dateValidator_46_js__ || {default: $__validators_47_dateValidator_46_js__}).DateValidator;\n
var NumericValidator = ($__validators_47_numericValidator_46_js__ = require("./validators/numericValidator.js"), $__validators_47_numericValidator_46_js__ && $__validators_47_numericValidator_46_js__.__esModule && $__validators_47_numericValidator_46_js__ || {default: $__validators_47_numericValidator_46_js__}).NumericValidator;\n
Handsontable.mobileBrowser = helper.isMobileBrowser();\n
Handsontable.AutocompleteCell = {\n
  editor: getEditorConstructor(\'autocomplete\'),\n
  renderer: getRenderer(\'autocomplete\'),\n
  validator: Handsontable.AutocompleteValidator\n
};\n
Handsontable.CheckboxCell = {\n
  editor: getEditorConstructor(\'checkbox\'),\n
  renderer: getRenderer(\'checkbox\')\n
};\n
Handsontable.TextCell = {\n
  editor: Handsontable.mobileBrowser ? getEditorConstructor(\'mobile\') : getEditorConstructor(\'text\'),\n
  renderer: getRenderer(\'text\')\n
};\n
Handsontable.NumericCell = {\n
  editor: getEditorConstructor(\'numeric\'),\n
  renderer: getRenderer(\'numeric\'),\n
  validator: Handsontable.NumericValidator,\n
  dataType: \'number\'\n
};\n
Handsontable.DateCell = {\n
  editor: getEditorConstructor(\'date\'),\n
  validator: Handsontable.DateValidator,\n
  renderer: getRenderer(\'autocomplete\')\n
};\n
Handsontable.HandsontableCell = {\n
  editor: getEditorConstructor(\'handsontable\'),\n
  renderer: getRenderer(\'autocomplete\')\n
};\n
Handsontable.PasswordCell = {\n
  editor: getEditorConstructor(\'password\'),\n
  renderer: getRenderer(\'password\'),\n
  copyable: false\n
};\n
Handsontable.DropdownCell = {\n
  editor: getEditorConstructor(\'dropdown\'),\n
  renderer: getRenderer(\'autocomplete\'),\n
  validator: Handsontable.AutocompleteValidator\n
};\n
Handsontable.cellTypes = {\n
  text: Handsontable.TextCell,\n
  date: Handsontable.DateCell,\n
  numeric: Handsontable.NumericCell,\n
  checkbox: Handsontable.CheckboxCell,\n
  autocomplete: Handsontable.AutocompleteCell,\n
  handsontable: Handsontable.HandsontableCell,\n
  password: Handsontable.PasswordCell,\n
  dropdown: Handsontable.DropdownCell\n
};\n
Handsontable.cellLookup = {validator: {\n
    numeric: Handsontable.NumericValidator,\n
    autocomplete: Handsontable.AutocompleteValidator\n
  }};\n
\n
\n
//# \n
},{"./editors.js":33,"./editors/autocompleteEditor.js":35,"./editors/checkboxEditor.js":36,"./editors/dateEditor.js":37,"./editors/dropdownEditor.js":38,"./editors/handsontableEditor.js":39,"./editors/mobileTextEditor.js":40,"./editors/numericEditor.js":41,"./editors/passwordEditor.js":42,"./editors/selectEditor.js":43,"./editors/textEditor.js":44,"./helpers.js":46,"./renderers.js":73,"./renderers/autocompleteRenderer.js":75,"./renderers/checkboxRenderer.js":76,"./renderers/htmlRenderer.js":77,"./renderers/numericRenderer.js":78,"./renderers/passwordRenderer.js":79,"./renderers/textRenderer.js":80,"./validators/autocompleteValidator.js":89,"./validators/dateValidator.js":90,"./validators/numericValidator.js":91}],29:[function(require,module,exports){\n
"use strict";\n
var $__dom_46_js__,\n
    $__helpers_46_js__,\n
    $__numeral__,\n
    $__dataMap_46_js__,\n
    $__editorManager_46_js__,\n
    $__eventManager_46_js__,\n
    $__plugins_46_js__,\n
    $__renderers_46_js__,\n
    $__pluginHooks_46_js__,\n
    $__tableView_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_selection_46_js__;\n
var dom = ($__dom_46_js__ = require("./dom.js"), $__dom_46_js__ && $__dom_46_js__.__esModule && $__dom_46_js__ || {default: $__dom_46_js__});\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
var numeral = ($__numeral__ = require("numeral"), $__numeral__ && $__numeral__.__esModule && $__numeral__ || {default: $__numeral__}).default;\n
var DataMap = ($__dataMap_46_js__ = require("./dataMap.js"), $__dataMap_46_js__ && $__dataMap_46_js__.__esModule && $__dataMap_46_js__ || {default: $__dataMap_46_js__}).DataMap;\n
var EditorManager = ($__editorManager_46_js__ = require("./editorManager.js"), $__editorManager_46_js__ && $__editorManager_46_js__.__esModule && $__editorManager_46_js__ || {default: $__editorManager_46_js__}).EditorManager;\n
var eventManagerObject = ($__eventManager_46_js__ = require("./eventManager.js"), $__eventManager_46_js__ && $__eventManager_46_js__.__esModule && $__eventManager_46_js__ || {default: $__eventManager_46_js__}).eventManager;\n
var getPlugin = ($__plugins_46_js__ = require("./plugins.js"), $__plugins_46_js__ && $__plugins_46_js__.__esModule && $__plugins_46_js__ || {default: $__plugins_46_js__}).getPlugin;\n
var getRenderer = ($__renderers_46_js__ = require("./renderers.js"), $__renderers_46_js__ && $__renderers_46_js__.__esModule && $__renderers_46_js__ || {default: $__renderers_46_js__}).getRenderer;\n
var PluginHook = ($__pluginHooks_46_js__ = require("./pluginHooks.js"), $__pluginHooks_46_js__ && $__pluginHooks_46_js__.__esModule && $__pluginHooks_46_js__ || {default: $__pluginHooks_46_js__}).PluginHook;\n
var TableView = ($__tableView_46_js__ = require("./tableView.js"), $__tableView_46_js__ && $__tableView_46_js__.__esModule && $__tableView_46_js__ || {default: $__tableView_46_js__}).TableView;\n
var WalkontableCellCoords = ($__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./3rdparty/walkontable/src/cell/coords.js"), $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = ($__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ = require("./3rdparty/walkontable/src/cell/range.js"), $__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ && $__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__}).WalkontableCellRange;\n
var WalkontableSelection = ($__3rdparty_47_walkontable_47_src_47_selection_46_js__ = require("./3rdparty/walkontable/src/selection.js"), $__3rdparty_47_walkontable_47_src_47_selection_46_js__ && $__3rdparty_47_walkontable_47_src_47_selection_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_selection_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_selection_46_js__}).WalkontableSelection;\n
Handsontable.activeGuid = null;\n
Handsontable.Core = function Core(rootElement, userSettings) {\n
  var priv,\n
      datamap,\n
      grid,\n
      selection,\n
      editorManager,\n
      instance = this,\n
      GridSettings = function() {},\n
      eventManager = eventManagerObject(instance);\n
  helper.extend(GridSettings.prototype, DefaultSettings.prototype);\n
  helper.extend(GridSettings.prototype, userSettings);\n
  helper.extend(GridSettings.prototype, expandType(userSettings));\n
  this.rootElement = rootElement;\n
  this.isHotTableEnv = dom.isChildOfWebComponentTable(this.rootElement);\n
  Handsontable.eventManager.isHotTableEnv = this.isHotTableEnv;\n
  this.container = document.createElement(\'DIV\');\n
  rootElement.insertBefore(this.container, rootElement.firstChild);\n
  this.guid = \'ht_\' + helper.randomString();\n
  if (!this.rootElement.id || this.rootElement.id.substring(0, 3) === "ht_") {\n
    this.rootElement.id = this.guid;\n
  }\n
  priv = {\n
    cellSettings: [],\n
    columnSettings: [],\n
    columnsSettingConflicts: [\'data\', \'width\'],\n
    settings: new GridSettings(),\n
    selRange: null,\n
    isPopulated: null,\n
    scrollable: null,\n
    firstRun: true\n
  };\n
  grid = {\n
    alter: function(action, index, amount, source, keepEmptyRows) {\n
      var delta;\n
      amount = amount || 1;\n
      switch (action) {\n
        case "insert_row":\n
          if (instance.getSettings().maxRows === instance.countRows()) {\n
            return;\n
          }\n
          delta = datamap.createRow(index, amount);\n
          if (delta) {\n
            if (selection.isSelected() && priv.selRange.from.row >= index) {\n
              priv.selRange.from.row = priv.selRange.from.row + delta;\n
              selection.transformEnd(delta, 0);\n
            } else {\n
              selection.refreshBorders();\n
            }\n
          }\n
          break;\n
        case "insert_col":\n
          delta = datamap.createCol(index, amount);\n
          if (delta) {\n
            if (Array.isArray(instance.getSettings().colHeaders)) {\n
              var spliceArray = [index, 0];\n
              spliceArray.length += delta;\n
              Array.prototype.splice.apply(instance.getSettings().colHeaders, spliceArray);\n
            }\n
            if (selection.isSelected() && priv.selRange.from.col >= index) {\n
              priv.selRange.from.col = priv.selRange.from.col + delta;\n
              selection.transformEnd(0, delta);\n
            } else {\n
              selection.refreshBorders();\n
            }\n
          }\n
          break;\n
        case "remove_row":\n
          index = instance.runHooks(\'modifyCol\', index);\n
          datamap.removeRow(index, amount);\n
          priv.cellSettings.splice(index, amount);\n
          var fixedRowsTop = instance.getSettings().fixedRowsTop;\n
          if (fixedRowsTop >= index + 1) {\n
            instance.getSettings().fixedRowsTop -= Math.min(amount, fixedRowsTop - index);\n
          }\n
          grid.adjustRowsAndCols();\n
          selection.refreshBorders();\n
          break;\n
        case "remove_col":\n
          datamap.removeCol(index, amount);\n
          for (var row = 0,\n
              len = datamap.getAll().length; row < len; row++) {\n
            if (row in priv.cellSettings) {\n
              priv.cellSettings[row].splice(index, amount);\n
            }\n
          }\n
          var fixedColumnsLeft = instance.getSettings().fixedColumnsLeft;\n
          if (fixedColumnsLeft >= index + 1) {\n
            instance.getSettings().fixedColumnsLeft -= Math.min(amount, fixedColumnsLeft - index);\n
          }\n
          if (Array.isArray(instance.getSettings().colHeaders)) {\n
            if (typeof index == \'undefined\') {\n
              index = -1;\n
            }\n
            instance.getSettings().colHeaders.splice(index, amount);\n
          }\n
          grid.adjustRowsAndCols();\n
          selection.refreshBorders();\n
          break;\n
        default:\n
          throw new Error(\'There is no such action "\' + action + \'"\');\n
          break;\n
      }\n
      if (!keepEmptyRows) {\n
        grid.adjustRowsAndCols();\n
      }\n
    },\n
    adjustRowsAndCols: function() {\n
      var r,\n
          rlen,\n
          emptyRows,\n
          emptyCols;\n
      rlen = instance.countRows();\n
      if (rlen < priv.settings.minRows) {\n
        for (r = 0; r < priv.settings.minRows - rlen; r++) {\n
          datamap.createRow(instance.countRows(), 1, true);\n
        }\n
      }\n
      emptyRows = instance.countEmptyRows(true);\n
      if (emptyRows < priv.settings.minSpareRows) {\n
        for (; emptyRows < priv.settings.minSpareRows && instance.countRows() < priv.settings.maxRows; emptyRows++) {\n
          datamap.createRow(instance.countRows(), 1, true);\n
        }\n
      }\n
      emptyCols = instance.countEmptyCols(true);\n
      if (!priv.settings.columns && instance.countCols() < priv.settings.minCols) {\n
        for (; instance.countCols() < priv.settings.minCols; emptyCols++) {\n
          datamap.createCol(instance.countCols(), 1, true);\n
        }\n
      }\n
      if (!priv.settings.columns && instance.dataType === \'array\' && emptyCols < priv.settings.minSpareCols) {\n
        for (; emptyCols < priv.settings.minSpareCols && instance.countCols() < priv.settings.maxCols; emptyCols++) {\n
          datamap.createCol(instance.countCols(), 1, true);\n
        }\n
      }\n
      var rowCount = instance.countRows();\n
      var colCount = instance.countCols();\n
      if (rowCount === 0 || colCount === 0) {\n
        selection.deselect();\n
      }\n
      if (selection.isSelected()) {\n
        var selectionChanged;\n
        var fromRow = priv.selRange.from.row;\n
        var fromCol = priv.selRange.from.col;\n
        var toRow = priv.selRange.to.row;\n
        var toCol = priv.selRange.to.col;\n
        if (fromRow > rowCount - 1) {\n
          fromRow = rowCount - 1;\n
          selectionChanged = true;\n
          if (toRow > fromRow) {\n
            toRow = fromRow;\n
          }\n
        } else if (toRow > rowCount - 1) {\n
          toRow = rowCount - 1;\n
          selectionChanged = true;\n
          if (fromRow > toRow) {\n
            fromRow = toRow;\n
          }\n
        }\n
        if (fromCol > colCount - 1) {\n
          fromCol = colCount - 1;\n
          selectionChanged = true;\n
          if (toCol > fromCol) {\n
            toCol = fromCol;\n
          }\n
        } else if (toCol > colCount - 1) {\n
          toCol = colCount - 1;\n
          selectionChanged = true;\n
          if (fromCol > toCol) {\n
            fromCol = toCol;\n
          }\n
        }\n
        if (selectionChanged) {\n
          instance.selectCell(fromRow, fromCol, toRow, toCol);\n
        }\n
      }\n
    },\n
    populateFromArray: function(start, input, end, source, method, direction, deltas) {\n
      var r,\n
          rlen,\n
          c,\n
          clen,\n
          setData = [],\n
          current = {};\n
      rlen = input.length;\n
      if (rlen === 0) {\n
        return false;\n
      }\n
      var repeatCol,\n
          repeatRow,\n
          cmax,\n
          rmax;\n
      switch (method) {\n
        case \'shift_down\':\n
          repeatCol = end ? end.col - start.col + 1 : 0;\n
          repeatRow = end ? end.row - start.row + 1 : 0;\n
          input = helper.translateRowsToColumns(input);\n
          for (c = 0, clen = input.length, cmax = Math.max(clen, repeatCol); c < cmax; c++) {\n
            if (c < clen) {\n
              for (r = 0, rlen = input[c].length; r < repeatRow - rlen; r++) {\n
                input[c].push(input[c][r % rlen]);\n
              }\n
              input[c].unshift(start.col + c, start.row, 0);\n
              instance.spliceCol.apply(instance, input[c]);\n
            } else {\n
              input[c % clen][0] = start.col + c;\n
              instance.spliceCol.apply(instance, input[c % clen]);\n
            }\n
          }\n
          break;\n
        case \'shift_right\':\n
          repeatCol = end ? end.col - start.col + 1 : 0;\n
          repeatRow = end ? end.row - start.row + 1 : 0;\n
          for (r = 0, rlen = input.length, rmax = Math.max(rlen, repeatRow); r < rmax; r++) {\n
            if (r < rlen) {\n
              for (c = 0, clen = input[r].length; c < repeatCol - clen; c++) {\n
                input[r].push(input[r][c % clen]);\n
              }\n
              input[r].unshift(start.row + r, start.col, 0);\n
              instance.spliceRow.apply(instance, input[r]);\n
            } else {\n
              input[r % rlen][0] = start.row + r;\n
              instance.spliceRow.apply(instance, input[r % rlen]);\n
            }\n
          }\n
          break;\n
        case \'overwrite\':\n
        default:\n
          current.row = start.row;\n
          current.col = start.col;\n
          var iterators = {\n
            row: 0,\n
            col: 0\n
          },\n
              selected = {\n
                row: (end && start) ? (end.row - start.row + 1) : 1,\n
                col: (end && start) ? (end.col - start.col + 1) : 1\n
              },\n
              pushData = true;\n
          if ([\'up\', \'left\'].indexOf(direction) !== -1) {\n
            iterators = {\n
              row: Math.ceil(selected.row / rlen) || 1,\n
              col: Math.ceil(selected.col / input[0].length) || 1\n
            };\n
          } else if ([\'down\', \'right\'].indexOf(direction) !== -1) {\n
            iterators = {\n
              row: 1,\n
              col: 1\n
            };\n
          }\n
          for (r = 0; r < rlen; r++) {\n
            if ((end && current.row > end.row) || (!priv.settings.allowInsertRow && current.row > instance.countRows() - 1) || (current.row >= priv.settings.maxRows)) {\n
              break;\n
            }\n
            current.col = start.col;\n
            clen = input[r] ? input[r].length : 0;\n
            for (c = 0; c < clen; c++) {\n
              if ((end && current.col > end.col) || (!priv.settings.allowInsertColumn && current.col > instance.countCols() - 1) || (current.col >= priv.settings.maxCols)) {\n
                break;\n
              }\n
              if (!instance.getCellMeta(current.row, current.col).readOnly) {\n
                var result,\n
                    value = input[r][c],\n
                    orgValue = instance.getDataAtCell(current.row, current.col),\n
                    index = {\n
                      row: r,\n
                      col: c\n
                    },\n
                    valueSchema,\n
                    orgValueSchema;\n
                if (source === \'autofill\') {\n
                  result = instance.runHooks(\'beforeAutofillInsidePopulate\', index, direction, input, deltas, iterators, selected);\n
                  if (result) {\n
                    iterators = typeof(result.iterators) !== \'undefined\' ? result.iterators : iterators;\n
                    value = typeof(result.value) !== \'undefined\' ? result.value : value;\n
                  }\n
                }\n
                if (value !== null && typeof value === \'object\') {\n
                  if (orgValue === null || typeof orgValue !== \'object\') {\n
                    pushData = false;\n
                  } else {\n
                    orgValueSchema = Handsontable.helper.duckSchema(orgValue[0] || orgValue);\n
                    valueSchema = Handsontable.helper.duckSchema(value[0] || value);\n
                    if (Handsontable.helper.isObjectEquals(orgValueSchema, valueSchema)) {\n
                      value = Handsontable.helper.deepClone(value);\n
                    } else {\n
                      pushData = false;\n
                    }\n
                  }\n
                } else if (orgValue !== null && typeof orgValue === \'object\') {\n
                  pushData = false;\n
                }\n
                if (pushData) {\n
                  setData.push([current.row, current.col, value]);\n
                }\n
                pushData = true;\n
              }\n
              current.col++;\n
              if (end && c === clen - 1) {\n
                c = -1;\n
                if ([\'down\', \'right\'].indexOf(direction) !== -1) {\n
                  iterators.col++;\n
                } else if ([\'up\', \'left\'].indexOf(direction) !== -1) {\n
                  if (iterators.col > 1) {\n
                    iterators.col--;\n
                  }\n
                }\n
              }\n
            }\n
            current.row++;\n
            iterators.col = 1;\n
            if (end && r === rlen - 1) {\n
              r = -1;\n
              if ([\'down\', \'right\'].indexOf(direction) !== -1) {\n
                iterators.row++;\n
              } else if ([\'up\', \'left\'].indexOf(direction) !== -1) {\n
                if (iterators.row > 1) {\n
                  iterators.row--;\n
                }\n
              }\n
            }\n
          }\n
          instance.setDataAtCell(setData, null, null, source || \'populateFromArray\');\n
          break;\n
      }\n
    }\n
  };\n
  this.selection = selection = {\n
    inProgress: false,\n
    selectedHeader: {\n
      cols: false,\n
      rows: false\n
    },\n
    setSelectedHeaders: function(rows, cols) {\n
      instance.selection.selectedHeader.rows = rows;\n
      instance.selection.selectedHeader.cols = cols;\n
    },\n
    begin: function() {\n
      instance.selection.inProgress = true;\n
    },\n
    finish: function() {\n
      var sel = instance.getSelected();\n
      Handsontable.hooks.run(instance, "afterSelectionEnd", sel[0], sel[1], sel[2], sel[3]);\n
      Handsontable.hooks.run(instance, "afterSelectionEndByProp", sel[0], instance.colToProp(sel[1]), sel[2], instance.colToProp(sel[3]));\n
      instance.selection.inProgress = false;\n
    },\n
    isInProgress: function() {\n
      return instance.selection.inProgress;\n
    },\n
    setRangeStart: function(coords, keepEditorOpened) {\n
      Handsontable.hooks.run(instance, "beforeSetRangeStart", coords);\n
      priv.selRange = new WalkontableCellRange(coords, coords, coords);\n
      selection.setRangeEnd(coords, null, keepEditorOpened);\n
    },\n
    setRangeEnd: function(coords, scrollToCell, keepEditorOpened) {\n
      if (priv.selRange === null) {\n
        return;\n
      }\n
      var disableVisualSelection;\n
      Handsontable.hooks.run(instance, "beforeSetRangeEnd", coords);\n
      instance.selection.begin();\n
      priv.selRange.to = new WalkontableCellCoords(coords.row, coords.col);\n
      if (!priv.settings.multiSelect) {\n
        priv.selRange.from = coords;\n
      }\n
      instance.view.wt.selections.current.clear();\n
      disableVisualSelection = instance.getCellMeta(priv.selRange.highlight.row, priv.selRange.highlight.col).disableVisualSelection;\n
      if (typeof disableVisualSelection === \'string\') {\n
        disableVisualSelection = [disableVisualSelection];\n
      }\n
      if (disableVisualSelection === false || Array.isArray(disableVisualSelection) && disableVisualSelection.indexOf(\'current\') === -1) {\n
        instance.view.wt.selections.current.add(priv.selRange.highlight);\n
      }\n
      instance.view.wt.selections.area.clear();\n
      if ((disableVisualSelection === false || Array.isArray(disableVisualSelection) && disableVisualSelection.indexOf(\'area\') === -1) && selection.isMultiple()) {\n
        instance.view.wt.selections.area.add(priv.selRange.from);\n
        instance.view.wt.selections.area.add(priv.selRange.to);\n
      }\n
      if (priv.settings.currentRowClassName || priv.settings.currentColClassName) {\n
        instance.view.wt.selections.highlight.clear();\n
        instance.view.wt.selections.highlight.add(priv.selRange.from);\n
        instance.view.wt.selections.highlight.add(priv.selRange.to);\n
      }\n
      Handsontable.hooks.run(instance, "afterSelection", priv.selRange.from.row, priv.selRange.from.col, priv.selRange.to.row, priv.selRange.to.col);\n
      Handsontable.hooks.run(instance, "afterSelectionByProp", priv.selRange.from.row, datamap.colToProp(priv.selRange.from.col), priv.selRange.to.row, datamap.colToProp(priv.selRange.to.col));\n
      if (scrollToCell !== false && instance.view.mainViewIsActive()) {\n
        if (priv.selRange.from && !selection.isMultiple()) {\n
          instance.view.scrollViewport(priv.selRange.from);\n
        } else {\n
          instance.view.scrollViewport(coords);\n
        }\n
      }\n
      selection.refreshBorders(null, keepEditorOpened);\n
    },\n
    refreshBorders: function(revertOriginal, keepEditor) {\n
      if (!keepEditor) {\n
        editorManager.destroyEditor(revertOriginal);\n
      }\n
      instance.view.render();\n
      if (selection.isSelected() && !keepEditor) {\n
        editorManager.prepareEditor();\n
      }\n
    },\n
    isMultiple: function() {\n
      var isMultiple = !(priv.selRange.to.col === priv.selRange.from.col && priv.selRange.to.row === priv.selRange.from.row),\n
          modifier = Handsontable.hooks.run(instance, \'afterIsMultipleSelection\', isMultiple);\n
      if (isMultiple) {\n
        return modifier;\n
      }\n
    },\n
    transformStart: function(rowDelta, colDelta, force, keepEditorOpened) {\n
      var delta = new WalkontableCellCoords(rowDelta, colDelta),\n
          rowTransformDir = 0,\n
          colTransformDir = 0,\n
          totalRows,\n
          totalCols,\n
          coords;\n
      instance.runHooks(\'modifyTransformStart\', delta);\n
      totalRows = instance.countRows();\n
      totalCols = instance.countCols();\n
      if (priv.selRange.highlight.row + rowDelta > totalRows - 1) {\n
        if (force && priv.settings.minSpareRows > 0) {\n
          instance.alter("insert_row", totalRows);\n
          totalRows = instance.countRows();\n
        } else if (priv.settings.autoWrapCol) {\n
          delta.row = 1 - totalRows;\n
          delta.col = priv.selRange.highlight.col + delta.col == totalCols - 1 ? 1 - totalCols : 1;\n
        }\n
      } else if (priv.settings.autoWrapCol && priv.selRange.highlight.row + delta.row < 0 && priv.selRange.highlight.col + delta.col >= 0) {\n
        delta.row = totalRows - 1;\n
        delta.col = priv.selRange.highlight.col + delta.col == 0 ? totalCols - 1 : -1;\n
      }\n
      if (priv.selRange.highlight.col + delta.col > totalCols - 1) {\n
        if (force && priv.settings.minSpareCols > 0) {\n
          instance.alter("insert_col", totalCols);\n
          totalCols = instance.countCols();\n
        } else if (priv.settings.autoWrapRow) {\n
          delta.row = priv.selRange.highlight.row + delta.row == totalRows - 1 ? 1 - totalRows : 1;\n
          delta.col = 1 - totalCols;\n
        }\n
      } else if (priv.settings.autoWrapRow && priv.selRange.highlight.col + delta.col < 0 && priv.selRange.highlight.row + delta.row >= 0) {\n
        delta.row = priv.selRange.highlight.row + delta.row == 0 ? totalRows - 1 : -1;\n
        delta.col = totalCols - 1;\n
      }\n
      coords = new WalkontableCellCoords(priv.selRange.highlight.row + delta.row, priv.selRange.highlight.col + delta.col);\n
      if (coords.row < 0) {\n
        rowTransformDir = -1;\n
        coords.row = 0;\n
      } else if (coords.row > 0 && coords.row >= totalRows) {\n
        rowTransformDir = 1;\n
        coords.row = totalRows - 1;\n
      }\n
      if (coords.col < 0) {\n
        colTransformDir = -1;\n
        coords.col = 0;\n
      } else if (coords.col > 0 && coords.col >= totalCols) {\n
        colTransformDir = 1;\n
        coords.col = totalCols - 1;\n
      }\n
      instance.runHooks(\'afterModifyTransformStart\', coords, rowTransformDir, colTransformDir);\n
      selection.setRangeStart(coords, keepEditorOpened);\n
    },\n
    transformEnd: function(rowDelta, colDelta) {\n
      var delta = new WalkontableCellCoords(rowDelta, colDelta),\n
          rowTransformDir = 0,\n
          colTransformDir = 0,\n
          totalRows,\n
          totalCols,\n
          coords;\n
      instance.runHooks(\'modifyTransformEnd\', delta);\n
      totalRows = instance.countRows();\n
      totalCols = instance.countCols();\n
      coords = new WalkontableCellCoords(priv.selRange.to.row + delta.row, priv.selRange.to.col + delta.col);\n
      if (coords.row < 0) {\n
        rowTransformDir = -1;\n
        coords.row = 0;\n
      } else if (coords.row > 0 && coords.row >= totalRows) {\n
        rowTransformDir = 1;\n
        coords.row = totalRows - 1;\n
      }\n
      if (coords.col < 0) {\n
        colTransformDir = -1;\n
        coords.col = 0;\n
      } else if (coords.col > 0 && coords.col >= totalCols) {\n
        colTransformDir = 1;\n
        coords.col = totalCols - 1;\n
      }\n
      instance.runHooks(\'afterModifyTransformEnd\', coords, rowTransformDir, colTransformDir);\n
      selection.setRangeEnd(coords, true);\n
    },\n
    isSelected: function() {\n
      return (priv.selRange !== null);\n
    },\n
    inInSelection: function(coords) {\n
      if (!selection.isSelected()) {\n
        return false;\n
      }\n
      return priv.selRange.includes(coords);\n
    },\n
    deselect: function() {\n
      if (!selection.isSelected()) {\n
        return;\n
      }\n
      instance.selection.inProgress = false;\n
      priv.selRange = null;\n
      instance.view.wt.selections.current.clear();\n
      instance.view.wt.selections.area.clear();\n
      if (priv.settings.currentRowClassName || priv.settings.currentColClassName) {\n
        instance.view.wt.selections.highlight.clear();\n
      }\n
      editorManager.destroyEditor();\n
      selection.refreshBorders();\n
      Handsontable.hooks.run(instance, \'afterDeselect\');\n
    },\n
    selectAll: function() {\n
      if (!priv.settings.multiSelect) {\n
        return;\n
      }\n
      selection.setRangeStart(new WalkontableCellCoords(0, 0));\n
      selection.setRangeEnd(new WalkontableCellCoords(instance.countRows() - 1, instance.countCols() - 1), false);\n
    },\n
    empty: function() {\n
      if (!selection.isSelected()) {\n
        return;\n
      }\n
      var topLeft = priv.selRange.getTopLeftCorner();\n
      var bottomRight = priv.selRange.getBottomRightCorner();\n
      var r,\n
          c,\n
          changes = [];\n
      for (r = topLeft.row; r <= bottomRight.row; r++) {\n
        for (c = topLeft.col; c <= bottomRight.col; c++) {\n
          if (!instance.getCellMeta(r, c).readOnly) {\n
            changes.push([r, c, \'\']);\n
          }\n
        }\n
      }\n
      instance.setDataAtCell(changes);\n
    }\n
  };\n
  this.init = function() {\n
    Handsontable.hooks.run(instance, \'beforeInit\');\n
    if (Handsontable.mobileBrowser) {\n
      dom.addClass(instance.rootElement, \'mobile\');\n
    }\n
    this.updateSettings(priv.settings, true);\n
    this.view = new TableView(this);\n
    editorManager = new EditorManager(instance, priv, selection, datamap);\n
    this.forceFullRender = true;\n
    this.view.render();\n
    if (typeof priv.firstRun === \'object\') {\n
      Handsontable.hooks.run(instance, \'afterChange\', priv.firstRun[0], priv.firstRun[1]);\n
      priv.firstRun = false;\n
    }\n
    Handsontable.hooks.run(instance, \'afterInit\');\n
  };\n
  function ValidatorsQueue() {\n
    var resolved = false;\n
    return {\n
      validatorsInQueue: 0,\n
      addValidatorToQueue: function() {\n
        this.validatorsInQueue++;\n
        resolved = false;\n
      },\n
      removeValidatorFormQueue: function() {\n
        this.validatorsInQueue = this.validatorsInQueue - 1 < 0 ? 0 : this.validatorsInQueue - 1;\n
        this.checkIfQueueIsEmpty();\n
      },\n
      onQueueEmpty: function() {},\n
      checkIfQueueIsEmpty: function() {\n
        if (this.validatorsInQueue == 0 && resolved == false) {\n
          resolved = true;\n
          this.onQueueEmpty();\n
        }\n
      }\n
    };\n
  }\n
  function validateChanges(changes, source, callback) {\n
    var waitingForValidator = new ValidatorsQueue();\n
    waitingForValidator.onQueueEmpty = resolve;\n
    for (var i = changes.length - 1; i >= 0; i--) {\n
      if (changes[i] === null) {\n
        changes.splice(i, 1);\n
      } else {\n
        var row = changes[i][0];\n
        var col = datamap.propToCol(changes[i][1]);\n
        var logicalCol = instance.runHooks(\'modifyCol\', col);\n
        var cellProperties = instance.getCellMeta(row, logicalCol);\n
        if (cellProperties.type === \'numeric\' && typeof changes[i][3] === \'string\') {\n
          if (changes[i][3].length > 0 && (/^-?[\\d\\s]*(\\.|\\,)?\\d*$/.test(changes[i][3]) || cellProperties.format)) {\n
            var len = changes[i][3].length;\n
            if (typeof cellProperties.language == \'undefined\') {\n
              numeral.language(\'en\');\n
            } else if (changes[i][3].indexOf(".") === len - 3 && changes[i][3].indexOf(",") === -1) {\n
              numeral.language(\'en\');\n
            } else {\n
              numeral.language(cellProperties.language);\n
            }\n
            if (numeral.validate(changes[i][3])) {\n
              changes[i][3] = numeral().unformat(changes[i][3]);\n
            }\n
          }\n
        }\n
        if (instance.getCellValidator(cellProperties)) {\n
          waitingForValidator.addValidatorToQueue();\n
          instance.validateCell(changes[i][3], cellProperties, (function(i, cellProperties) {\n
            return function(result) {\n
              if (typeof result !== \'boolean\') {\n
                throw new Error("Validation error: result is not boolean");\n
              }\n
              if (result === false && cellProperties.allowInvalid === false) {\n
                changes.splice(i, 1);\n
                cellProperties.valid = true;\n
                --i;\n
              }\n
              waitingForValidator.removeValidatorFormQueue();\n
            };\n
          })(i, cellProperties), source);\n
        }\n
      }\n
    }\n
    waitingForValidator.checkIfQueueIsEmpty();\n
    function resolve() {\n
      var beforeChangeResult;\n
      if (changes.length) {\n
        beforeChangeResult = Handsontable.hooks.run(instance, "beforeChange", changes, source);\n
        if (typeof beforeChangeResult === \'function\') {\n
          console.warn("Your beforeChange callback returns a function. It\'s not supported since Handsontable 0.12.1 (and the returned function will not be executed).");\n
        } else if (beforeChangeResult === false) {\n
          changes.splice(0, changes.length);\n
        }\n
      }\n
      callback();\n
    }\n
  }\n
  function applyChanges(changes, source) {\n
    var i = changes.length - 1;\n
    if (i < 0) {\n
      return;\n
    }\n
    for (; 0 <= i; i--) {\n
      if (changes[i] === null) {\n
        changes.splice(i, 1);\n
        continue;\n
      }\n
      if (changes[i][2] == null && changes[i][3] == null) {\n
        continue;\n
      }\n
      if (priv.settings.allowInsertRow) {\n
        while (changes[i][0] > instance.countRows() - 1) {\n
          datamap.createRow();\n
        }\n
      }\n
      if (instance.dataType === \'array\' && priv.settings.allowInsertColumn) {\n
        while (datamap.propToCol(changes[i][1]) > instance.countCols() - 1) {\n
          datamap.createCol();\n
        }\n
      }\n
      datamap.set(changes[i][0], changes[i][1], changes[i][3]);\n
    }\n
    instance.forceFullRender = true;\n
    grid.adjustRowsAndCols();\n
    Handsontable.hooks.run(instance, \'beforeChangeRender\', changes, source);\n
    selection.refreshBorders(null, true);\n
    Handsontable.hooks.run(instance, \'afterChange\', changes, source || \'edit\');\n
  }\n
  this.validateCell = function(value, cellProperties, callback, source) {\n
    var validator = instance.getCellValidator(cellProperties);\n
    function done(valid) {\n
      var col = cellProperties.col,\n
          row = cellProperties.row,\n
          td = instance.getCell(row, col, true);\n
      if (td) {\n
        instance.view.wt.wtSettings.settings.cellRenderer(row, col, td);\n
      }\n
      callback(valid);\n
    }\n
    if (Object.prototype.toString.call(validator) === \'[object RegExp]\') {\n
      validator = (function(validator) {\n
        return function(value, callback) {\n
          callback(validator.test(value));\n
        };\n
      })(validator);\n
    }\n
    if (typeof validator == \'function\') {\n
      value = Handsontable.hooks.run(instance, "beforeValidate", value, cellProperties.row, cellProperties.prop, source);\n
      instance._registerTimeout(setTimeout(function() {\n
        validator.call(cellProperties, value, function(valid) {\n
          valid = Handsontable.hooks.run(instance, "afterValidate", valid, value, cellProperties.row, cellProperties.prop, source);\n
          cellProperties.valid = valid;\n
          done(valid);\n
          Handsontable.hooks.run(instance, "postAfterValidate", valid, value, cellProperties.row, cellProperties.prop, source);\n
        });\n
      }, 0));\n
    } else {\n
      cellProperties.valid = true;\n
      done(cellProperties.valid);\n
    }\n
  };\n
  function setDataInputToArray(row, propOrCol, value) {\n
    if (typeof row === "object") {\n
      return row;\n
    } else {\n
      return [[row, propOrCol, value]];\n
    }\n
  }\n
  this.setDataAtCell = function(row, col, value, source) {\n
    var input = setDataInputToArray(row, col, value),\n
        i,\n
        ilen,\n
        changes = [],\n
        prop;\n
    for (i = 0, ilen = input.length; i < ilen; i++) {\n
      if (typeof input[i] !== \'object\') {\n
        throw new Error(\'Method `setDataAtCell` accepts row number or changes array of arrays as its first parameter\');\n
      }\n
      if (typeof input[i][1] !== \'number\') {\n
        throw new Error(\'Method `setDataAtCell` accepts row and column number as its parameters. If you want to use object property name, use method `setDataAtRowProp`\');\n
      }\n
      prop = datamap.colToProp(input[i][1]);\n
      changes.push([input[i][0], prop, datamap.get(input[i][0], prop), input[i][2]]);\n
    }\n
    if (!source && typeof row === "object") {\n
      source = col;\n
    }\n
    validateChanges(changes, source, function() {\n
      applyChanges(changes, source);\n
    });\n
  };\n
  this.setDataAtRowProp = function(row, prop, value, source) {\n
    var input = setDataInputToArray(row, prop, value),\n
        i,\n
        ilen,\n
        changes = [];\n
    for (i = 0, ilen = input.length; i < ilen; i++) {\n
      changes.push([input[i][0], input[i][1], datamap.get(input[i][0], input[i][1]), input[i][2]]);\n
    }\n
    if (!source && typeof row === "object") {\n
      source = prop;\n
    }\n
    validateChanges(changes, source, function() {\n
      applyChanges(changes, source);\n
    });\n
  };\n
  this.listen = function() {\n
    Handsontable.activeGuid = instance.guid;\n
    if (document.activeElement && document.activeElement !== document.body) {\n
      document.activeElement.blur();\n
    } else if (!document.activeElement) {\n
      document.body.focus();\n
    }\n
  };\n
  this.unlisten = function() {\n
    Handsontable.activeGuid = null;\n
  };\n
  this.isListening = function() {\n
    return Handsontable.activeGuid === instance.guid;\n
  };\n
  this.destroyEditor = function(revertOriginal) {\n
    selection.refreshBorders(revertOriginal);\n
  };\n
  this.populateFromArray = function(row, col, input, endRow, endCol, source, method, direction, deltas) {\n
    var c;\n
    if (!(typeof input === \'object\' && typeof input[0] === \'object\')) {\n
      throw new Error("populateFromArray parameter `input` must be an array of arrays");\n
    }\n
    c = typeof endRow === \'number\' ? new WalkontableCellCoords(endRow, endCol) : null;\n
    return grid.populateFromArray(new WalkontableCellCoords(row, col), input, c, source, method, direction, deltas);\n
  };\n
  this.spliceCol = function(col, index, amount) {\n
    return datamap.spliceCol.apply(datamap, arguments);\n
  };\n
  this.spliceRow = function(row, index, amount) {\n
    return datamap.spliceRow.apply(datamap, arguments);\n
  };\n
  this.getSelected = function() {\n
    if (selection.isSelected()) {\n
      return [priv.selRange.from.row, priv.selRange.from.col, priv.selRange.to.row, priv.selRange.to.col];\n
    }\n
  };\n
  this.getSelectedRange = function() {\n
    if (selection.isSelected()) {\n
      return priv.selRange;\n
    }\n
  };\n
  this.render = function() {\n
    if (instance.view) {\n
      instance.forceFullRender = true;\n
      selection.refreshBorders(null, true);\n
    }\n
  };\n
  this.loadData = function(data) {\n
    if (typeof data === \'object\' && data !== null) {\n
      if (!(data.push && data.splice)) {\n
        data = [data];\n
      }\n
    } else if (data === null) {\n
      data = [];\n
      var row;\n
      for (var r = 0,\n
          rlen = priv.settings.startRows; r < rlen; r++) {\n
        row = [];\n
        for (var c = 0,\n
            clen = priv.settings.startCols; c < clen; c++) {\n
          row.push(null);\n
        }\n
        data.push(row);\n
      }\n
    } else {\n
      throw new Error("loadData only accepts array of objects or array of arrays (" + typeof data + " given)");\n
    }\n
    priv.isPopulated = false;\n
    GridSettings.prototype.data = data;\n
    if (Array.isArray(priv.settings.dataSchema) || Array.isArray(data[0])) {\n
      instance.dataType = \'array\';\n
    } else if (typeof priv.settings.dataSchema === \'function\') {\n
      instance.dataType = \'function\';\n
    } else {\n
      instance.dataType = \'object\';\n
    }\n
    datamap = new DataMap(instance, priv, GridSettings);\n
    clearCellSettingCache();\n
    grid.adjustRowsAndCols();\n
    Handsontable.hooks.run(instance, \'afterLoadData\');\n
    if (priv.firstRun) {\n
      priv.firstRun = [null, \'loadData\'];\n
    } else {\n
      Handsontable.hooks.run(instance, \'afterChange\', null, \'loadData\');\n
      instance.render();\n
    }\n
    priv.isPopulated = true;\n
    function clearCellSettingCache() {\n
      priv.cellSettings.length = 0;\n
    }\n
  };\n
  this.getData = function(r, c, r2, c2) {\n
    if (typeof r === \'undefined\') {\n
      return datamap.getAll();\n
    } else {\n
      return datamap.getRange(new WalkontableCellCoords(r, c), new WalkontableCellCoords(r2, c2), datamap.DESTINATION_RENDERER);\n
    }\n
  };\n
  this.getCopyableData = function(startRow, startCol, endRow, endCol) {\n
    return datamap.getCopyableText(new WalkontableCellCoords(startRow, startCol), new WalkontableCellCoords(endRow, endCol));\n
  };\n
  this.getSchema = function() {\n
    return datamap.getSchema();\n
  };\n
  this.updateSettings = function(settings, init) {\n
    var i,\n
        clen;\n
    if (typeof settings.rows !== "undefined") {\n
      throw new Error("\'rows\' setting is no longer supported. do you mean startRows, minRows or maxRows?");\n
    }\n
    if (typeof settings.cols !== "undefined") {\n
      throw new Error("\'cols\' setting is no longer supported. do you mean startCols, minCols or maxCols?");\n
    }\n
    for (i in settings) {\n
      if (i === \'data\') {\n
        continue;\n
      } else {\n
        if (Handsontable.hooks.hooks[i] !== void 0) {\n
          if (typeof settings[i] === \'function\' || Array.isArray(settings[i])) {\n
            instance.addHook(i, settings[i]);\n
          }\n
        } else {\n
          if (!init && settings.hasOwnProperty(i)) {\n
            GridSettings.prototype[i] = settings[i];\n
          }\n
        }\n
      }\n
    }\n
    if (settings.data === void 0 && priv.settings.data === void 0) {\n
      instance.loadData(null);\n
    } else if (settings.data !== void 0) {\n
      instance.loadData(settings.data);\n
    } else if (settings.columns !== void 0) {\n
      datamap.createMap();\n
    }\n
    clen = instance.countCols();\n
    priv.cellSettings.length = 0;\n
    if (clen > 0) {\n
      var proto,\n
          column;\n
      for (i = 0; i < clen; i++) {\n
        priv.columnSettings[i] = helper.columnFactory(GridSettings, priv.columnsSettingConflicts);\n
        proto = priv.columnSettings[i].prototype;\n
        if (GridSettings.prototype.columns) {\n
          column = GridSettings.prototype.columns[i];\n
          helper.extend(proto, column);\n
          helper.extend(proto, expandType(column));\n
        }\n
      }\n
    }\n
    if (typeof settings.cell !== \'undefined\') {\n
      for (i in settings.cell) {\n
        if (settings.cell.hasOwnProperty(i)) {\n
          var cell = settings.cell[i];\n
          instance.setCellMetaObject(cell.row, cell.col, cell);\n
        }\n
      }\n
    }\n
    Handsontable.hooks.run(instance, \'afterCellMetaReset\');\n
    if (typeof settings.className !== "undefined") {\n
      if (GridSettings.prototype.className) {\n
        dom.removeClass(instance.rootElement, GridSettings.prototype.className);\n
      }\n
      if (settings.className) {\n
        dom.addClass(instance.rootElement, settings.className);\n
      }\n
    }\n
    if (typeof settings.height != \'undefined\') {\n
      var height = settings.height;\n
      if (typeof height == \'function\') {\n
        height = height();\n
      }\n
      instance.rootElement.style.height = height + \'px\';\n
    }\n
    if (typeof settings.width != \'undefined\') {\n
      var width = settings.width;\n
      if (typeof width == \'function\') {\n
        width = width();\n
      }\n
      instance.rootElement.style.width = width + \'px\';\n
    }\n
    if (height) {\n
      instance.rootElement.style.overflow = \'hidden\';\n
    }\n
    if (!init) {\n
      Handsontable.hooks.run(instance, \'afterUpdateSettings\');\n
    }\n
    grid.adjustRowsAndCols();\n
    if (instance.view && !priv.firstRun) {\n
      instance.forceFullRender = true;\n
      selection.refreshBorders(null, true);\n
    }\n
  };\n
  this.getValue = function() {\n
    var sel = instance.getSelected();\n
    if (GridSettings.prototype.getValue) {\n
      if (typeof GridSettings.prototype.getValue === \'function\') {\n
        return GridSettings.prototype.getValue.call(instance);\n
      } else if (sel) {\n
        return instance.getData()[sel[0]][GridSettings.prototype.getValue];\n
      }\n
    } else if (sel) {\n
      return instance.getDataAtCell(sel[0], sel[1]);\n
    }\n
  };\n
  function expandType(obj) {\n
    if (!obj.hasOwnProperty(\'type\')) {\n
      return;\n
    }\n
    var type,\n
        expandedType = {};\n
    if (typeof obj.type === \'object\') {\n
      type = obj.type;\n
    } else if (typeof obj.type === \'string\') {\n
      type = Handsontable.cellTypes[obj.type];\n
      if (type === void 0) {\n
        throw new Error(\'You declared cell type "\' + obj.type + \'" as a string that is not mapped to a known object. Cell type must be an object or a string mapped to an object in Handsontable.cellTypes\');\n
      }\n
    }\n
    for (var i in type) {\n
      if (type.hasOwnProperty(i) && !obj.hasOwnProperty(i)) {\n
        expandedType[i] = type[i];\n
      }\n
    }\n
    return expandedType;\n
  }\n
  this.getSettings = function() {\n
    return priv.settings;\n
  };\n
  this.clear = function() {\n
    selection.selectAll();\n
    selection.empty();\n
  };\n
  this.alter = function(action, index, amount, source, keepEmptyRows) {\n
    grid.alter(action, index, amount, source, keepEmptyRows);\n
  };\n
  this.getCell = function(row, col, topmost) {\n
    return instance.view.getCellAtCoords(new WalkontableCellCoords(row, col), topmost);\n
  };\n
  this.getCoords = function(elem) {\n
    return this.view.wt.wtTable.getCoords.call(this.view.wt.wtTable, elem);\n
  };\n
  this.colToProp = function(col) {\n
    return datamap.colToProp(col);\n
  };\n
  this.propToCol = function(prop) {\n
    return datamap.propToCol(prop);\n
  };\n
  this.getDataAtCell = function(row, col) {\n
    return datamap.get(row, datamap.colToProp(col));\n
  };\n
  this.getDataAtRowProp = function(row, prop) {\n
    return datamap.get(row, prop);\n
  };\n
  this.getDataAtCol = function(col) {\n
    var out = [];\n
    return out.concat.apply(out, datamap.getRange(new WalkontableCellCoords(0, col), new WalkontableCellCoords(priv.settings.data.length - 1, col), datamap.DESTINATION_RENDERER));\n
  };\n
  this.getDataAtProp = function(prop) {\n
    var out = [],\n
        range;\n
    range = datamap.getRange(new WalkontableCellCoords(0, datamap.propToCol(prop)), new WalkontableCellCoords(priv.settings.data.length - 1, datamap.propToCol(prop)), datamap.DESTINATION_RENDERER);\n
    return out.concat.apply(out, range);\n
  };\n
  this.getSourceDataAtCol = function(col) {\n
    var out = [],\n
        data = priv.settings.data;\n
    for (var i = 0; i < data.length; i++) {\n
      out.push(data[i][col]);\n
    }\n
    return out;\n
  };\n
  this.getSourceDataAtRow = function(row) {\n
    return priv.settings.data[row];\n
  };\n
  this.getDataAtRow = function(row) {\n
    var data = datamap.getRange(new WalkontableCellCoords(row, 0), new WalkontableCellCoords(row, this.countCols() - 1), datamap.DESTINATION_RENDERER);\n
    return data[0];\n
  };\n
  this.removeCellMeta = function(row, col, key) {\n
    var cellMeta = instance.getCellMeta(row, col);\n
    if (cellMeta[key] != undefined) {\n
      delete priv.cellSettings[row][col][key];\n
    }\n
  };\n
  this.setCellMetaObject = function(row, col, prop) {\n
    if (typeof prop === \'object\') {\n
      for (var key in prop) {\n
        if (prop.hasOwnProperty(key)) {\n
          var value = prop[key];\n
          this.setCellMeta(row, col, key, value);\n
        }\n
      }\n
    }\n
  };\n
  this.setCellMeta = function(row, col, key, val) {\n
    if (!priv.cellSettings[row]) {\n
      priv.cellSettings[row] = [];\n
    }\n
    if (!priv.cellSettings[row][col]) {\n
      priv.cellSettings[row][col] = new priv.columnSettings[col]();\n
    }\n
    priv.cellSettings[row][col][key] = val;\n
    Handsontable.hooks.run(instance, \'afterSetCellMeta\', row, col, key, val);\n
  };\n
  this.getCellMeta = function(row, col) {\n
    var prop = datamap.colToProp(col),\n
        cellProperties;\n
    row = translateRowIndex(row);\n
    col = translateColIndex(col);\n
    if (!priv.columnSettings[col]) {\n
      priv.columnSettings[col] = helper.columnFactory(GridSettings, priv.columnsSettingConflicts);\n
    }\n
    if (!priv.cellSettings[row]) {\n
      priv.cellSettings[row] = [];\n
    }\n
    if (!priv.cellSettings[row][col]) {\n
      priv.cellSettings[row][col] = new priv.columnSettings[col]();\n
    }\n
    cellProperties = priv.cellSettings[row][col];\n
    cellProperties.row = row;\n
    cellProperties.col = col;\n
    cellProperties.prop = prop;\n
    cellProperties.instance = instance;\n
    Handsontable.hooks.run(instance, \'beforeGetCellMeta\', row, col, cellProperties);\n
    helper.extend(cellProperties, expandType(cellProperties));\n
    if (cellProperties.cells) {\n
      var settings = cellProperties.cells.call(cellProperties, row, col, prop);\n
      if (settings) {\n
        helper.extend(cellProperties, settings);\n
        helper.extend(cellProperties, expandType(settings));\n
      }\n
    }\n
    Handsontable.hooks.run(instance, \'afterGetCellMeta\', row, col, cellProperties);\n
    return cellProperties;\n
  };\n
  this.isColumnModificationAllowed = function() {\n
    return !(instance.dataType === \'object\' || instance.getSettings().columns);\n
  };\n
  function translateRowIndex(row) {\n
    return Handsontable.hooks.run(instance, \'modifyRow\', row);\n
  }\n
  function translateColIndex(col) {\n
    return Handsontable.hooks.run(instance, \'modifyCol\', col);\n
  }\n
  var rendererLookup = helper.cellMethodLookupFactory(\'renderer\');\n
  this.getCellRenderer = function(row, col) {\n
    var renderer = rendererLookup.call(this, row, col);\n
    return getRenderer(renderer);\n
  };\n
  this.getCellEditor = helper.cellMethodLookupFactory(\'editor\');\n
  this.getCellValidator = helper.cellMethodLookupFactory(\'validator\');\n
  this.validateCells = function(callback) {\n
    var waitingForValidator = new ValidatorsQueue();\n
    waitingForValidator.onQueueEmpty = callback;\n
    var i = instance.countRows() - 1;\n
    while (i >= 0) {\n
      var j = instance.countCols() - 1;\n
      while (j >= 0) {\n
        waitingForValidator.addValidatorToQueue();\n
        instance.validateCell(instance.getDataAtCell(i, j), instance.getCellMeta(i, j), function() {\n
          waitingForValidator.removeValidatorFormQueue();\n
        }, \'validateCells\');\n
        j--;\n
      }\n
      i--;\n
    }\n
    waitingForValidator.checkIfQueueIsEmpty();\n
  };\n
  this.getRowHeader = function(row) {\n
    if (row === void 0) {\n
      var out = [];\n
      for (var i = 0,\n
          ilen = instance.countRows(); i < ilen; i++) {\n
        out.push(instance.getRowHeader(i));\n
      }\n
      return out;\n
    } else if (Array.isArray(priv.settings.rowHeaders) && priv.settings.rowHeaders[row] !== void 0) {\n
      return priv.settings.rowHeaders[row];\n
    } else if (typeof priv.settings.rowHeaders === \'function\') {\n
      return priv.settings.rowHeaders(row);\n
    } else if (priv.settings.rowHeaders && typeof priv.settings.rowHeaders !== \'string\' && typeof priv.settings.rowHeaders !== \'number\') {\n
      return row + 1;\n
    } else {\n
      return priv.settings.rowHeaders;\n
    }\n
  };\n
  this.hasRowHeaders = function() {\n
    return !!priv.settings.rowHeaders;\n
  };\n
  this.hasColHeaders = function() {\n
    if (priv.settings.colHeaders !== void 0 && priv.settings.colHeaders !== null) {\n
      return !!priv.settings.colHeaders;\n
    }\n
    for (var i = 0,\n
        ilen = instance.countCols(); i < ilen; i++) {\n
      if (instance.getColHeader(i)) {\n
        return true;\n
      }\n
    }\n
    return false;\n
  };\n
  this.getColHeader = function(col) {\n
    if (col === void 0) {\n
      var out = [];\n
      for (var i = 0,\n
          ilen = instance.countCols(); i < ilen; i++) {\n
        out.push(instance.getColHeader(i));\n
      }\n
      return out;\n
    } else {\n
      var baseCol = col;\n
      col = Handsontable.hooks.run(instance, \'modifyCol\', col);\n
      if (priv.settings.columns && priv.settings.columns[col] && priv.settings.columns[col].title) {\n
        return priv.settings.columns[col].title;\n
      } else if (Array.isArray(priv.settings.colHeaders) && priv.settings.colHeaders[col] !== void 0) {\n
        return priv.settings.colHeaders[col];\n
      } else if (typeof priv.settings.colHeaders === \'function\') {\n
        return priv.settings.colHeaders(col);\n
      } else if (priv.settings.colHeaders && typeof priv.settings.colHeaders !== \'string\' && typeof priv.settings.colHeaders !== \'number\') {\n
        return helper.spreadsheetColumnLabel(baseCol);\n
      } else {\n
        return priv.settings.colHeaders;\n
      }\n
    }\n
  };\n
  this._getColWidthFromSettings = function(col) {\n
    var cellProperties = instance.getCellMeta(0, col);\n
    var width = cellProperties.width;\n
    if (width === void 0 || width === priv.settings.width) {\n
      width = cellProperties.colWidths;\n
    }\n
    if (width !== void 0 && width !== null) {\n
      switch (typeof width) {\n
        case \'object\':\n
          width = width[col];\n
          break;\n
        case \'function\':\n
          width = width(col);\n
          break;\n
      }\n
      if (typeof width === \'string\') {\n
        width = parseInt(width, 10);\n
      }\n
    }\n
    return width;\n
  };\n
  this.getColWidth = function(col) {\n
    var width = instance._getColWidthFromSettings(col);\n
    if (!width) {\n
      width = 50;\n
    }\n
    width = Handsontable.hooks.run(instance, \'modifyColWidth\', width, col);\n
    return width;\n
  };\n
  this._getRowHeightFromSettings = function(row) {\n
    var height = priv.settings.rowHeights;\n
    if (height !== void 0 && height !== null) {\n
      switch (typeof height) {\n
        case \'object\':\n
          height = height[row];\n
          break;\n
        case \'function\':\n
          height = height(row);\n
          break;\n
      }\n
      if (typeof height === \'string\') {\n
        height = parseInt(height, 10);\n
      }\n
    }\n
    return height;\n
  };\n
  this.getRowHeight = function(row) {\n
    var height = instance._getRowHeightFromSettings(row);\n
    height = Handsontable.hooks.run(instance, \'modifyRowHeight\', height, row);\n
    return height;\n
  };\n
  this.countRows = function() {\n
    return priv.settings.data.length;\n
  };\n
  this.countCols = function() {\n
    if (instance.dataType === \'object\' || instance.dataType === \'function\') {\n
      if (priv.settings.columns && priv.settings.columns.length) {\n
        return priv.settings.columns.length;\n
      } else {\n
        return datamap.colToPropCache.length;\n
      }\n
    } else if (instance.dataType === \'array\') {\n
      if (priv.settings.columns && priv.settings.columns.length) {\n
        return priv.settings.columns.length;\n
      } else if (priv.settings.data && priv.settings.data[0] && priv.settings.data[0].length) {\n
        return priv.settings.data[0].length;\n
      } else {\n
        return 0;\n
      }\n
    }\n
  };\n
  this.rowOffset = function() {\n
    return instance.view.wt.wtTable.getFirstRenderedRow();\n
  };\n
  this.colOffset = function() {\n
    return instance.view.wt.wtTable.getFirstRenderedColumn();\n
  };\n
  this.countRenderedRows = function() {\n
    return instance.view.wt.drawn ? instance.view.wt.wtTable.getRenderedRowsCount() : -1;\n
  };\n
  this.countVisibleRows = function() {\n
    return instance.view.wt.drawn ? instance.view.wt.wtTable.getVisibleRowsCount() : -1;\n
  };\n
  this.countRenderedCols = function() {\n
    return instance.view.wt.drawn ? instance.view.wt.wtTable.getRenderedColumnsCount() : -1;\n
  };\n
  this.countVisibleCols = function() {\n
    return instance.view.wt.drawn ? instance.view.wt.wtTable.getVisibleColumnsCount() : -1;\n
  };\n
  this.countEmptyRows = function(ending) {\n
    var i = instance.countRows() - 1,\n
        empty = 0,\n
        row;\n
    while (i >= 0) {\n
      row = Handsontable.hooks.run(this, \'modifyRow\', i);\n
      if (instance.isEmptyRow(row)) {\n
        empty++;\n
      } else if (ending) {\n
        break;\n
      }\n
      i--;\n
    }\n
    return empty;\n
  };\n
  this.countEmptyCols = function(ending) {\n
    if (instance.countRows() < 1) {\n
      return 0;\n
    }\n
    var i = instance.countCols() - 1,\n
        empty = 0;\n
    while (i >= 0) {\n
      if (instance.isEmptyCol(i)) {\n
        empty++;\n
      } else if (ending) {\n
        break;\n
      }\n
      i--;\n
    }\n
    return empty;\n
  };\n
  this.isEmptyRow = function(row) {\n
    return priv.settings.isEmptyRow.call(instance, row);\n
  };\n
  this.isEmptyCol = function(col) {\n
    return priv.settings.isEmptyCol.call(instance, col);\n
  };\n
  this.selectCell = function(row, col, endRow, endCol, scrollToCell, changeListener) {\n
    var coords;\n
    changeListener = typeof changeListener === \'undefined\' || changeListener === true;\n
    if (typeof row !== \'number\' || row < 0 || row >= instance.countRows()) {\n
      return false;\n
    }\n
    if (typeof col !== \'number\' || col < 0 || col >= instance.countCols()) {\n
      return false;\n
    }\n
    if (typeof endRow !== \'undefined\') {\n
      if (typeof endRow !== \'number\' || endRow < 0 || endRow >= instance.countRows()) {\n
        return false;\n
      }\n
      if (typeof endCol !== \'number\' || endCol < 0 || endCol >= instance.countCols()) {\n
        return false;\n
      }\n
    }\n
    coords = new WalkontableCellCoords(row, col);\n
    priv.selRange = new WalkontableCellRange(coords, coords, coords);\n
    if (document.activeElement && document.activeElement !== document.documentElement && document.activeElement !== document.body) {\n
      document.activeElement.blur();\n
    }\n
    if (changeListener) {\n
      instance.listen();\n
    }\n
    if (typeof endRow === \'undefined\') {\n
      selection.setRangeEnd(priv.selRange.from, scrollToCell);\n
    } else {\n
      selection.setRangeEnd(new WalkontableCellCoords(endRow, endCol), scrollToCell);\n
    }\n
    instance.selection.finish();\n
    return true;\n
  };\n
  this.selectCellByProp = function(row, prop, endRow, endProp, scrollToCell) {\n
    arguments[1] = datamap.propToCol(arguments[1]);\n
    if (typeof arguments[3] !== "undefined") {\n
      arguments[3] = datamap.propToCol(arguments[3]);\n
    }\n
    return instance.selectCell.apply(instance, arguments);\n
  };\n
  this.deselectCell = function() {\n
    selection.deselect();\n
  };\n
  this.destroy = function() {\n
    instance._clearTimeouts();\n
    if (instance.view) {\n
      instance.view.destroy();\n
    }\n
    dom.empty(instance.rootElement);\n
    eventManager.clear();\n
    Handsontable.hooks.run(instance, \'afterDestroy\');\n
    Handsontable.hooks.destroy(instance);\n
    for (var i in instance) {\n
      if (instance.hasOwnProperty(i)) {\n
        if (typeof instance[i] === "function") {\n
          if (i !== "runHooks") {\n
            instance[i] = postMortem;\n
          }\n
        } else if (i !== "guid") {\n
          instance[i] = null;\n
        }\n
      }\n
    }\n
    priv = null;\n
    datamap = null;\n
    grid = null;\n
    selection = null;\n
    editorManager = null;\n
    instance = null;\n
    GridSettings = null;\n
  };\n
  function postMortem() {\n
    throw new Error("This method cannot be called because this Handsontable instance has been destroyed");\n
  }\n
  this.getActiveEditor = function() {\n
    return editorManager.getActiveEditor();\n
  };\n
  this.getPlugin = function(pluginName) {\n
    return getPlugin(this, pluginName);\n
  };\n
  this.getInstance = function() {\n
    return instance;\n
  };\n
  this.addHook = function(key, callback) {\n
    Handsontable.hooks.add(key, callback, instance);\n
  };\n
  this.addHookOnce = function(key, callback) {\n
    Handsontable.hooks.once(key, callback, instance);\n
  };\n
  this.removeHook = function(key, callback) {\n
    Handsontable.hooks.remove(key, callback, instance);\n
  };\n
  this.runHooks = function(key, p1, p2, p3, p4, p5, p6) {\n
    return Handsontable.hooks.run(instance, key, p1, p2, p3, p4, p5, p6);\n
  };\n
  this.timeouts = [];\n
  this._registerTimeout = function(handle) {\n
    this.timeouts.push(handle);\n
  };\n
  this._clearTimeouts = function() {\n
    for (var i = 0,\n
        ilen = this.timeouts.length; i < ilen; i++) {\n
      clearTimeout(this.timeouts[i]);\n
    }\n
  };\n
  this.version = Handsontable.version;\n
};\n
var DefaultSettings = function() {};\n
DefaultSettings.prototype = {\n
  data: void 0,\n
  dataSchema: void 0,\n
  width: void 0,\n
  height: void 0,\n
  startRows: 5,\n
  startCols: 5,\n
  rowHeaders: null,\n
  colHeaders: null,\n
  colWidths: void 0,\n
  columns: void 0,\n
  cells: void 0,\n
  cell: [],\n
  comments: false,\n
  customBorders: false,\n
  minRows: 0,\n
  minCols: 0,\n
  maxRows: Infinity,\n
  maxCols: Infinity,\n
  minSpareRows: 0,\n
  minSpareCols: 0,\n
  allowInsertRow: true,\n
  allowInsertColumn: true,\n
  allowRemoveRow: true,\n
  allowRemoveColumn: true,\n
  multiSelect: true,\n
  fillHandle: true,\n
  fixedRowsTop: 0,\n
  fixedColumnsLeft: 0,\n
  outsideClickDeselects: true,\n
  enterBeginsEditing: true,\n
  enterMoves: {\n
    row: 1,\n
    col: 0\n
  },\n
  tabMoves: {\n
    row: 0,\n
    col: 1\n
  },\n
  autoWrapRow: false,\n
  autoWrapCol: false,\n
  copyRowsLimit: 1000,\n
  copyColsLimit: 1000,\n
  pasteMode: \'overwrite\',\n
  persistentState: false,\n
  currentRowClassName: void 0,\n
  currentColClassName: void 0,\n
  stretchH: \'none\',\n
  isEmptyRow: function(row) {\n
    var col,\n
        colLen,\n
        value,\n
        meta;\n
    for (col = 0, colLen = this.countCols(); col < colLen; col++) {\n
      value = this.getDataAtCell(row, col);\n
      if (value !== \'\' && value !== null && typeof value !== \'undefined\') {\n
        if (typeof value === \'object\') {\n
          meta = this.getCellMeta(row, col);\n
          return helper.isObjectEquals(this.getSchema()[meta.prop], value);\n
        }\n
        return false;\n
      }\n
    }\n
    return true;\n
  },\n
  isEmptyCol: function(col) {\n
    var row,\n
        rowLen,\n
        value;\n
    for (row = 0, rowLen = this.countRows(); row < rowLen; row++) {\n
      value = this.getDataAtCell(row, col);\n
      if (value !== \'\' && value !== null && typeof value !== \'undefined\') {\n
        return false;\n
      }\n
    }\n
    return true;\n
  },\n
  observeDOMVisibility: true,\n
  allowInvalid: true,\n
  invalidCellClassName: \'htInvalid\',\n
  placeholder: false,\n
  placeholderCellClassName: \'htPlaceholder\',\n
  readOnlyCellClassName: \'htDimmed\',\n
  renderer: void 0,\n
  commentedCellClassName: \'htCommentCell\',\n
  fragmentSelection: false,\n
  readOnly: false,\n
  search: false,\n
  type: \'text\',\n
  copyable: true,\n
  editor: void 0,\n
  autoComplete: void 0,\n
  debug: false,\n
  wordWrap: true,\n
  noWordWrapClassName: \'htNoWrap\',\n
  contextMenu: void 0,\n
  undo: void 0,\n
  columnSorting: void 0,\n
  manualColumnMove: void 0,\n
  manualColumnResize: void 0,\n
  manualRowMove: void 0,\n
  manualRowResize: void 0,\n
  mergeCells: false,\n
  viewportRowRenderingOffset: 10,\n
  viewportColumnRenderingOffset: 10,\n
  groups: void 0,\n
  validator: void 0,\n
  disableVisualSelection: false,\n
  manualColumnFreeze: void 0,\n
  trimWhitespace: true,\n
  settings: void 0,\n
  source: void 0,\n
  title: void 0,\n
  checkedTemplate: void 0,\n
  uncheckedTemplate: void 0,\n
  format: void 0,\n
  className: void 0\n
};\n
Handsontable.DefaultSettings = DefaultSettings;\n
\n
\n
//# \n
},{"./3rdparty/walkontable/src/cell/coords.js":9,"./3rdparty/walkontable/src/cell/range.js":10,"./3rdparty/walkontable/src/selection.js":22,"./dataMap.js":30,"./dom.js":31,"./editorManager.js":32,"./eventManager.js":45,"./helpers.js":46,"./pluginHooks.js":48,"./plugins.js":49,"./renderers.js":73,"./tableView.js":88,"numeral":"numeral"}],30:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  DataMap: {get: function() {\n
      return DataMap;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__helpers_46_js__,\n
    $__multiMap_46_js__,\n
    $__3rdparty_47_sheetclip_46_js__;\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
var MultiMap = ($__multiMap_46_js__ = require("./multiMap.js"), $__multiMap_46_js__ && $__multiMap_46_js__.__esModule && $__multiMap_46_js__ || {default: $__multiMap_46_js__}).MultiMap;\n
var SheetClip = ($__3rdparty_47_sheetclip_46_js__ = require("./3rdparty/sheetclip.js"), $__3rdparty_47_sheetclip_46_js__ && $__3rdparty_47_sheetclip_46_js__.__esModule && $__3rdparty_47_sheetclip_46_js__ || {default: $__3rdparty_47_sheetclip_46_js__}).default;\n
;\n
Handsontable.DataMap = DataMap;\n
function DataMap(instance, priv, GridSettings) {\n
  this.instance = instance;\n
  this.priv = priv;\n
  this.GridSettings = GridSettings;\n
  this.dataSource = this.instance.getSettings().data;\n
  if (this.dataSource[0]) {\n
    this.duckSchema = this.recursiveDuckSchema(this.dataSource[0]);\n
  } else {\n
    this.duckSchema = {};\n
  }\n
  this.createMap();\n
}\n
DataMap.prototype.DESTINATION_RENDERER = 1;\n
DataMap.prototype.DESTINATION_CLIPBOARD_GENERATOR = 2;\n
DataMap.prototype.recursiveDuckSchema = function(object) {\n
  return Handsontable.helper.duckSchema(object);\n
};\n
DataMap.prototype.recursiveDuckColumns = function(schema, lastCol, parent) {\n
  var prop,\n
      i;\n
  if (typeof lastCol === \'undefined\') {\n
    lastCol = 0;\n
    parent = \'\';\n
  }\n
  if (typeof schema === "object" && !Array.isArray(schema)) {\n
    for (i in schema) {\n
      if (schema.hasOwnProperty(i)) {\n
        if (schema[i] === null) {\n
          prop = parent + i;\n
          this.colToPropCache.push(prop);\n
          this.propToColCache.set(prop, lastCol);\n
          lastCol++;\n
        } else {\n
          lastCol = this.recursiveDuckColumns(schema[i], lastCol, i + \'.\');\n
        }\n
      }\n
    }\n
  }\n
  return lastCol;\n
};\n
DataMap.prototype.createMap = function() {\n
  var i,\n
      ilen,\n
      schema = this.getSchema();\n
  if (typeof schema === "undefined") {\n
    throw new Error("trying to create `columns` definition but you didnt\' provide `schema` nor `data`");\n
  }\n
  this.colToPropCache = [];\n
  this.propToColCache = new MultiMap();\n
  var columns = this.instance.getSettings().columns;\n
  if (columns) {\n
    for (i = 0, ilen = columns.length; i < ilen; i++) {\n
      if (typeof columns[i].data != \'undefined\') {\n
        this.colToPropCache[i] = columns[i].data;\n
        this.propToColCache.set(columns[i].data, i);\n
      }\n
    }\n
  } else {\n
    this.recursiveDuckColumns(schema);\n
  }\n
};\n
DataMap.prototype.colToProp = function(col) {\n
  col = Handsontable.hooks.run(this.instance, \'modifyCol\', col);\n
  if (this.colToPropCache && typeof this.colToPropCache[col] !== \'undefined\') {\n
    return this.colToPropCache[col];\n
  }\n
  return col;\n
};\n
DataMap.prototype.propToCol = function(prop) {\n
  var col;\n
  if (typeof this.propToColCache.get(prop) !== \'undefined\') {\n
    col = this.propToColCache.get(prop);\n
  } else {\n
    col = prop;\n
  }\n
  col = Handsontable.hooks.run(this.instance, \'modifyCol\', col);\n
  return col;\n
};\n
DataMap.prototype.getSchema = function() {\n
  var schema = this.instance.getSettings().dataSchema;\n
  if (schema) {\n
    if (typeof schema === \'function\') {\n
      return schema();\n
    }\n
    return schema;\n
  }\n
  return this.duckSchema;\n
};\n
DataMap.prototype.createRow = function(index, amount, createdAutomatically) {\n
  var row,\n
      colCount = this.instance.countCols(),\n
      numberOfCreatedRows = 0,\n
      currentIndex;\n
  if (!amount) {\n
    amount = 1;\n
  }\n
  if (typeof index !== \'number\' || index >= this.instance.countRows()) {\n
    index = this.instance.countRows();\n
  }\n
  currentIndex = index;\n
  var maxRows = this.instance.getSettings().maxRows;\n
  while (numberOfCreatedRows < amount && this.instance.countRows() < maxRows) {\n
    if (this.instance.dataType === \'array\') {\n
      row = [];\n
      for (var c = 0; c < colCount; c++) {\n
        row.push(null);\n
      }\n
    } else if (this.instance.dataType === \'function\') {\n
      row = this.instance.getSettings().dataSchema(index);\n
    } else {\n
      row = {};\n
      helper.deepExtend(row, this.getSchema());\n
    }\n
    if (index === this.instance.countRows()) {\n
      this.dataSource.push(row);\n
    } else {\n
      this.dataSource.splice(index, 0, row);\n
    }\n
    numberOfCreatedRows++;\n
    currentIndex++;\n
  }\n
  Handsontable.hooks.run(this.instance, \'afterCreateRow\', index, numberOfCreatedRows, createdAutomatically);\n
  this.instance.forceFullRender = true;\n
  return numberOfCreatedRows;\n
};\n
DataMap.prototype.createCol = function(index, amount, createdAutomatically) {\n
  if (!this.instance.isColumnModificationAllowed()) {\n
    throw new Error("Cannot create new column. When data source in an object, " + "you can only have as much columns as defined in first data row, data schema or in the \'columns\' setting." + "If you want to be able to add new columns, you have to use array datasource.");\n
  }\n
  var rlen = this.instance.countRows(),\n
      data = this.dataSource,\n
      constructor,\n
      numberOfCreatedCols = 0,\n
      currentIndex;\n
  if (!amount) {\n
    amount = 1;\n
  }\n
  currentIndex = index;\n
  var maxCols = this.instance.getSettings().maxCols;\n
  while (numberOfCreatedCols < amount && this.instance.countCols() < maxCols) {\n
    constructor = helper.columnFactory(this.GridSettings, this.priv.columnsSettingConflicts);\n
    if (typeof index !== \'number\' || index >= this.instance.countCols()) {\n
      for (var r = 0; r < rlen; r++) {\n
        if (typeof data[r] === \'undefined\') {\n
          data[r] = [];\n
        }\n
        data[r].push(null);\n
      }\n
      this.priv.columnSettings.push(constructor);\n
    } else {\n
      for (var r = 0; r < rlen; r++) {\n
        data[r].splice(currentIndex, 0, null);\n
      }\n
      this.priv.columnSettings.splice(currentIndex, 0, constructor);\n
    }\n
    numberOfCreatedCols++;\n
    currentIndex++;\n
  }\n
  Handsontable.hooks.run(this.instance, \'afterCreateCol\', index, numberOfCreatedCols, createdAutomatically);\n
  this.instance.forceFullRender = true;\n
  return numberOfCreatedCols;\n
};\n
DataMap.prototype.removeRow = function(index, amount) {\n
  if (!amount) {\n
    amount = 1;\n
  }\n
  if (typeof index !== \'number\') {\n
    index = -amount;\n
  }\n
  index = (this.instance.countRows() + index) % this.instance.countRows();\n
  var logicRows = this.physicalRowsToLogical(index, amount);\n
  var actionWasNotCancelled = Handsontable.hooks.run(this.instance, \'beforeRemoveRow\', index, amount);\n
  if (actionWasNotCancelled === false) {\n
    return;\n
  }\n
  var data = this.dataSource;\n
  var newData = data.filter(function(row, index) {\n
    return logicRows.indexOf(index) == -1;\n
  });\n
  data.length = 0;\n
  Array.prototype.push.apply(data, newData);\n
  Handsontable.hooks.run(this.instance, \'afterRemoveRow\', index, amount);\n
  this.instance.forceFullRender = true;\n
};\n
DataMap.prototype.removeCol = function(index, amount) {\n
  if (this.instance.dataType === \'object\' || this.instance.getSettings().columns) {\n
    throw new Error("cannot remove column with object data source or columns option specified");\n
  }\n
  if (!amount) {\n
    amount = 1;\n
  }\n
  if (typeof index !== \'number\') {\n
    index = -amount;\n
  }\n
  index = (this.instance.countCols() + index) % this.instance.countCols();\n
  var actionWasNotCancelled = Handsontable.hooks.run(this.instance, \'beforeRemoveCol\', index, amount);\n
  if (actionWasNotCancelled === false) {\n
    return;\n
  }\n
  var data = this.dataSource;\n
  for (var r = 0,\n
      rlen = this.instance.countRows(); r < rlen; r++) {\n
    data[r].splice(index, amount);\n
  }\n
  this.priv.columnSettings.splice(index, amount);\n
  Handsontable.hooks.run(this.instance, \'afterRemoveCol\', index, amount);\n
  this.instance.forceFullRender = true;\n
};\n
DataMap.prototype.spliceCol = function(col, index, amount) {\n
  var elements = 4 <= arguments.length ? [].slice.call(arguments, 3) : [];\n
  var colData = this.instance.getDataAtCol(col);\n
  var removed = colData.slice(index, index + amount);\n
  var after = colData.slice(index + amount);\n
  helper.extendArray(elements, after);\n
  var i = 0;\n
  while (i < amount) {\n
    elements.push(null);\n
    i++;\n
  }\n
  helper.to2dArray(elements);\n
  this.instance.populateFromArray(index, col, elements, null, null, \'spliceCol\');\n
  return removed;\n
};\n
DataMap.prototype.spliceRow = function(row, index, amount) {\n
  var elements = 4 <= arguments.length ? [].slice.call(arguments, 3) : [];\n
  var rowData = this.instance.getSourceDataAtRow(row);\n
  var removed = rowData.slice(index, index + amount);\n
  var after = rowData.slice(index + amount);\n
  helper.extendArray(elements, after);\n
  var i = 0;\n
  while (i < amount) {\n
    elements.push(null);\n
    i++;\n
  }\n
  this.instance.populateFromArray(row, index, [elements], null, null, \'spliceRow\');\n
  return removed;\n
};\n
DataMap.prototype.get = function(row, prop) {\n
  row = Handsontable.hooks.run(this.instance, \'modifyRow\', row);\n
  if (typeof prop === \'string\' && prop.indexOf(\'.\') > -1) {\n
    var sliced = prop.split(".");\n
    var out = this.dataSource[row];\n
    if (!out) {\n
      return null;\n
    }\n
    for (var i = 0,\n
        ilen = sliced.length; i < ilen; i++) {\n
      out = out[sliced[i]];\n
      if (typeof out === \'undefined\') {\n
        return null;\n
      }\n
    }\n
    return out;\n
  } else if (typeof prop === \'function\') {\n
    return prop(this.dataSource.slice(row, row + 1)[0]);\n
  } else {\n
    return this.dataSource[row] ? this.dataSource[row][prop] : null;\n
  }\n
};\n
var copyableLookup = helper.cellMethodLookupFactory(\'copyable\', false);\n
DataMap.prototype.getCopyable = function(row, prop) {\n
  if (copyableLookup.call(this.instance, row, this.propToCol(prop))) {\n
    return this.get(row, prop);\n
  }\n
  return \'\';\n
};\n
DataMap.prototype.set = function(row, prop, value, source) {\n
  row = Handsontable.hooks.run(this.instance, \'modifyRow\', row, source || "datamapGet");\n
  if (typeof prop === \'string\' && prop.indexOf(\'.\') > -1) {\n
    var sliced = prop.split(".");\n
    var out = this.dataSource[row];\n
    for (var i = 0,\n
        ilen = sliced.length - 1; i < ilen; i++) {\n
      if (typeof out[sliced[i]] === \'undefined\') {\n
        out[sliced[i]] = {};\n
      }\n
      out = out[sliced[i]];\n
    }\n
    out[sliced[i]] = value;\n
  } else if (typeof prop === \'function\') {\n
    prop(this.dataSource.slice(row, row + 1)[0], value);\n
  } else {\n
    this.dataSource[row][prop] = value;\n
  }\n
};\n
DataMap.prototype.physicalRowsToLogical = function(index, amount) {\n
  var totalRows = this.instance.countRows();\n
  var physicRow = (totalRows + index) % totalRows;\n
  var logicRows = [];\n
  var rowsToRemove = amount;\n
  var row;\n
  while (physicRow < totalRows && rowsToRemove) {\n
    row = Handsontable.hooks.run(this.instance, \'modifyRow\', physicRow);\n
    logicRows.push(row);\n
    rowsToRemove--;\n
    physicRow++;\n
  }\n
  return logicRows;\n
};\n
DataMap.prototype.clear = function() {\n
  for (var r = 0; r < this.instance.countRows(); r++) {\n
    for (var c = 0; c < this.instance.countCols(); c++) {\n
      this.set(r, this.colToProp(c), \'\');\n
    }\n
  }\n
};\n
DataMap.prototype.getAll = function() {\n
  return this.dataSource;\n
};\n
DataMap.prototype.getRange = function(start, end, destination) {\n
  var r,\n
      rlen,\n
      c,\n
      clen,\n
      output = [],\n
      row;\n
  var getFn = destination === this.DESTINATION_CLIPBOARD_GENERATOR ? this.getCopyable : this.get;\n
  rlen = Math.max(start.row, end.row);\n
  clen = Math.max(start.col, end.col);\n
  for (r = Math.min(start.row, end.row); r <= rlen; r++) {\n
    row = [];\n
    for (c = Math.min(start.col, end.col); c <= clen; c++) {\n
      row.push(getFn.call(this, r, this.colToProp(c)));\n
    }\n
    output.push(row);\n
  }\n
  return output;\n
};\n
DataMap.prototype.getText = function(start, end) {\n
  return SheetClip.stringify(this.getRange(start, end, this.DESTINATION_RENDERER));\n
};\n
DataMap.prototype.getCopyableText = function(start, end) {\n
  return SheetClip.stringify(this.getRange(start, end, this.DESTINATION_CLIPBOARD_GENERATOR));\n
};\n
\n
\n
//# \n
},{"./3rdparty/sheetclip.js":5,"./helpers.js":46,"./multiMap.js":47}],31:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  enableImmediatePropagation: {get: function() {\n
      return enableImmediatePropagation;\n
    }},\n
  closest: {get: function() {\n
      return closest;\n
    }},\n
  isChildOf: {get: function() {\n
      return isChildOf;\n
    }},\n
  isChildOfWebComponentTable: {get: function() {\n
      return isChildOfWebComponentTable;\n
    }},\n
  polymerWrap: {get: function() {\n
      return polymerWrap;\n
    }},\n
  polymerUnwrap: {get: function() {\n
      return polymerUnwrap;\n
    }},\n
  isWebComponentSupportedNatively: {get: function() {\n
      return isWebComponentSupportedNatively;\n
    }},\n
  index: {get: function() {\n
      return index;\n
    }},\n
  hasClass: {get: function() {\n
      return hasClass;\n
    }},\n
  addClass: {get: function() {\n
      return addClass;\n
    }},\n
  removeClass: {get: function() {\n
      return removeClass;\n
    }},\n
  removeTextNodes: {get: function() {\n
      return removeTextNodes;\n
    }},\n
  empty: {get: function() {\n
      return empty;\n
    }},\n
  HTML_CHARACTERS: {get: function() {\n
      return HTML_CHARACTERS;\n
    }},\n
  fastInnerHTML: {get: function() {\n
      return fastInnerHTML;\n
    }},\n
  fastInnerText: {get: function() {\n
      return fastInnerText;\n
    }},\n
  isVisible: {get: function() {\n
      return isVisible;\n
    }},\n
  offset: {get: function() {\n
      return offset;\n
    }},\n
  getWindowScrollTop: {get: function() {\n
      return getWindowScrollTop;\n
    }},\n
  getWindowScrollLeft: {get: function() {\n
      return getWindowScrollLeft;\n
    }},\n
  getScrollTop: {get: function() {\n
      return getScrollTop;\n
    }},\n
  getScrollLeft: {get: function() {\n
      return getScrollLeft;\n
    }},\n
  getScrollableElement: {get: function() {\n
      return getScrollableElement;\n
    }},\n
  getTrimmingContainer: {get: function() {\n
      return getTrimmingContainer;\n
    }},\n
  getStyle: {get: function() {\n
      return getStyle;\n
    }},\n
  getComputedStyle: {get: function() {\n
      return getComputedStyle;\n
    }},\n
  outerWidth: {get: function() {\n
      return outerWidth;\n
    }},\n
  outerHeight: {get: function() {\n
      return outerHeight;\n
    }},\n
  innerHeight: {get: function() {\n
      return innerHeight;\n
    }},\n
  innerWidth: {get: function() {\n
      return innerWidth;\n
    }},\n
  addEvent: {get: function() {\n
      return addEvent;\n
    }},\n
  removeEvent: {get: function() {\n
      return removeEvent;\n
    }},\n
  hasCaptionProblem: {get: function() {\n
      return hasCaptionProblem;\n
    }},\n
  getCaretPosition: {get: function() {\n
      return getCaretPosition;\n
    }},\n
  getSelectionEndPosition: {get: function() {\n
      return getSelectionEndPosition;\n
    }},\n
  setCaretPosition: {get: function() {\n
      return setCaretPosition;\n
    }},\n
  getScrollbarWidth: {get: function() {\n
      return getScrollbarWidth;\n
    }},\n
  isIE8: {get: function() {\n
      return isIE8;\n
    }},\n
  isIE9: {get: function() {\n
      return isIE9;\n
    }},\n
  isSafari: {get: function() {\n
      return isSafari;\n
    }},\n
  setOverlayPosition: {get: function() {\n
      return setOverlayPosition;\n
    }},\n
  getCssTransform: {get: function() {\n
      return getCssTransform;\n
    }},\n
  resetCssTransform: {get: function() {\n
      return resetCssTransform;\n
    }},\n
  __esModule: {value: true}\n
});\n
function enableImmediatePropagation(event) {\n
  if (event != null && event.isImmediatePropagationEnabled == null) {\n
    event.stopImmediatePropagation = function() {\n
      this.isImmediatePropagationEnabled = false;\n
      this.cancelBubble = true;\n
    };\n
    event.isImmediatePropagationEnabled = true;\n
    event.isImmediatePropagationStopped = function() {\n
      return !this.isImmediatePropagationEnabled;\n
    };\n
  }\n
}\n
function closest(element, nodes, until) {\n
  while (element != null && element !== until) {\n
    if (element.nodeType === Node.ELEMENT_NODE && (nodes.indexOf(element.nodeName) > -1 || nodes.indexOf(element) > -1)) {\n
      return element;\n
    }\n
    if (element.host && element.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {\n
      element = element.host;\n
    } else {\n
      element = element.parentNode;\n
    }\n
  }\n
  return null;\n
}\n
function isChildOf(child, parent) {\n
  var node = child.parentNode;\n
  var queriedParents = [];\n
  if (typeof parent === "string") {\n
    queriedParents = Array.prototype.slice.call(document.querySelectorAll(parent), 0);\n
  } else {\n
    queriedParents.push(parent);\n
  }\n
  while (node != null) {\n
    if (queriedParents.indexOf(node) > -1) {\n
      return true;\n
    }\n
    node = node.parentNode;\n
  }\n
  return false;\n
}\n
function isChildOfWebComponentTable(element) {\n
  var hotTableName = \'hot-table\',\n
      result = false,\n
      parentNode;\n
  parentNode = polymerWrap(element);\n
  function isHotTable(element) {\n
    return element.nodeType === Node.ELEMENT_NODE && element.nodeName === hotTableName.toUpperCase();\n
  }\n
  while (parentNode != null) {\n
    if (isHotTable(parentNode)) {\n
      result = true;\n
      break;\n
    } else if (parentNode.host && parentNode.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {\n
      result = isHotTable(parentNode.host);\n
      if (result) {\n
        break;\n
      }\n
      parentNode = parentNode.host;\n
    }\n
    parentNode = parentNode.parentNode;\n
  }\n
  return result;\n
}\n
function polymerWrap(element) {\n
  return typeof Polymer !== \'undefined\' && typeof wrap === \'function\' ? wrap(element) : element;\n
}\n
function polymerUnwrap(element) {\n
  return typeof Polymer !== \'undefined\' && typeof unwrap === \'function\' ? unwrap(element) : element;\n
}\n
function isWebComponentSupportedNatively() {\n
  var test = document.createElement(\'div\');\n
  return test.createShadowRoot && test.createShadowRoot.toString().match(/\\[native code\\]/) ? true : false;\n
}\n
function index(elem) {\n
  var i = 0;\n
  if (elem.previousSibling) {\n
    while (elem = elem.previousSibling) {\n
      ++i;\n
    }\n
  }\n
  return i;\n
}\n
var classListSupport = document.documentElement.classList ? true : false;\n
var _hasClass,\n
    _addClass,\n
    _removeClass;\n
function filterEmptyClassNames(classNames) {\n
  var len = 0,\n
      result = [];\n
  if (!classNames || !classNames.length) {\n
    return result;\n
  }\n
  while (classNames[len]) {\n
    result.push(classNames[len]);\n
    len++;\n
  }\n
  return result;\n
}\n
if (classListSupport) {\n
  var isSupportMultipleClassesArg = (function() {\n
    var element = document.createElement(\'div\');\n
    element.classList.add(\'test\', \'test2\');\n
    return element.classList.contains(\'test2\');\n
  }());\n
  _hasClass = function _hasClass(element, className) {\n
    if (className === \'\') {\n
      return false;\n
    }\n
    return element.classList.contains(className);\n
  };\n
  _addClass = function _addClass(element, className) {\n
    var len = 0;\n
    if (typeof className === \'string\') {\n
      className = className.split(\' \');\n
    }\n
    className = filterEmptyClassNames(className);\n
    if (isSupportMultipleClassesArg) {\n
      element.classList.add.apply(element.classList, className);\n
    } else {\n
      while (className && className[len]) {\n
        element.classList.add(className[len]);\n
        len++;\n
      }\n
    }\n
  };\n
  _removeClass = function _removeClass(element, className) {\n
    var len = 0;\n
    if (typeof className === \'string\') {\n
      className = className.split(\' \');\n
    }\n
    className = filterEmptyClassNames(className);\n
    if (isSupportMultipleClassesArg) {\n
      element.classList.remove.apply(element.classList, className);\n
    } else {\n
      while (className && className[len]) {\n
        element.classList.remove(className[len]);\n
        len++;\n
      }\n
    }\n
  };\n
} else {\n
  var createClassNameRegExp = function createClassNameRegExp(className) {\n
    return new RegExp(\'(\\\\s|^)\' + className + \'(\\\\s|$)\');\n
  };\n
  _hasClass = function _hasClass(element, className) {\n
    return element.className.match(createClassNameRegExp(className)) ? true : false;\n
  };\n
  _addClass = function _addClass(element, className) {\n
    var len = 0,\n
        _className = element.className;\n
    if (typeof className === \'string\') {\n
      className = className.split(\' \');\n
    }\n
    if (_className === \'\') {\n
      _className = className.join(\' \');\n
    } else {\n
      while (className && className[len]) {\n
        if (!createClassNameRegExp(className[len]).test(_className)) {\n
          _className += \' \' + className[len];\n
        }\n
        len++;\n
      }\n
    }\n
    element.className = _className;\n
  };\n
  _removeClass = function _removeClass(element, className) {\n
    var len = 0,\n
        _className = element.className;\n
    if (typeof className === \'string\') {\n
      className = className.split(\' \');\n
    }\n
    while (className && className[len]) {\n
      _className = _className.replace(createClassNameRegExp(className[len]), \' \').trim();\n
      len++;\n
    }\n
    if (element.className !== _className) {\n
      element.className = _className;\n
    }\n
  };\n
}\n
function hasClass(element, className) {\n
  return _hasClass(element, className);\n
}\n
function addClass(element, className) {\n
  return _addClass(element, className);\n
}\n
function removeClass(element, className) {\n
  return _removeClass(element, className);\n
}\n
function removeTextNodes(elem, parent) {\n
  if (elem.nodeType === 3) {\n
    parent.removeChild(elem);\n
  } else if ([\'TABLE\', \'THEAD\', \'TBODY\', \'TFOOT\', \'TR\'].indexOf(elem.nodeName) > -1) {\n
    var childs = elem.childNodes;\n
    for (var i = childs.length - 1; i >= 0; i--) {\n
      removeTextNodes(childs[i], elem);\n
    }\n
  }\n
}\n
function empty(element) {\n
  var child;\n
  while (child = element.lastChild) {\n
    element.removeChild(child);\n
  }\n
}\n
var HTML_CHARACTERS = /(<(.*)>|&(.*);)/;\n
function fastInnerHTML(element, content) {\n
  if (HTML_CHARACTERS.test(content)) {\n
    element.innerHTML = content;\n
  } else {\n
    fastInnerText(element, content);\n
  }\n
}\n
var textContextSupport = document.createTextNode(\'test\').textContent ? true : false;\n
function fastInnerText(element, content) {\n
  var child = element.firstChild;\n
  if (child && child.nodeType === 3 && child.nextSibling === null) {\n
    if (textContextSupport) {\n
      child.textContent = content;\n
    } else {\n
      child.data = content;\n
    }\n
  } else {\n
    empty(element);\n
    element.appendChild(document.createTextNode(content));\n
  }\n
}\n
function isVisible(elem) {\n
  var next = elem;\n
  while (polymerUnwrap(next) !== document.documentElement) {\n
    if (next === null) {\n
      return false;\n
    } else if (next.nodeType === Node.DOCUMENT_FRAGMENT_NODE) {\n
      if (next.host) {\n
        if (next.host.impl) {\n
          return isVisible(next.host.impl);\n
        } else if (next.host) {\n
          return isVisible(next.host);\n
        } else {\n
          throw new Error("Lost in Web Components world");\n
        }\n
      } else {\n
        return false;\n
      }\n
    } else if (next.style.display === \'none\') {\n
      return false;\n
    }\n
    next = next.parentNode;\n
  }\n
  return true;\n
}\n
function offset(elem) {\n
  var offsetLeft,\n
      offsetTop,\n
      lastElem,\n
      docElem,\n
      box;\n
  docElem = document.documentElement;\n
  if (hasCaptionProblem() && elem.firstChild && elem.firstChild.nodeName === \'CAPTION\') {\n
    box = elem.getBoundingClientRect();\n
    return {\n
      top: box.top + (window.pageYOffset || docElem.scrollTop) - (docElem.clientTop || 0),\n
      left: box.left + (window.pageXOffset || docElem.scrollLeft) - (docElem.clientLeft || 0)\n
    };\n
  }\n
  offsetLeft = elem.offsetLeft;\n
  offsetTop = elem.offsetTop;\n
  lastElem = elem;\n
  while (elem = elem.offsetParent) {\n
    if (elem === document.body) {\n
      break;\n
    }\n
    offsetLeft += elem.offsetLeft;\n
    offsetTop += elem.offsetTop;\n
    lastElem = elem;\n
  }\n
  if (lastElem && lastElem.style.position === \'fixed\') {\n
    offsetLeft += window.pageXOffset || docElem.scrollLeft;\n
    offsetTop += window.pageYOffset || docElem.scrollTop;\n
  }\n
  return {\n
    left: offsetLeft,\n
    top: offsetTop\n
  };\n
}\n
function getWindowScrollTop() {\n
  var res = window.scrollY;\n
  if (res == void 0) {\n
    res = document.documentElement.scrollTop;\n
  }\n
  return res;\n
}\n
function getWindowScrollLeft() {\n
  var res = window.scrollX;\n
  if (res == void 0) {\n
    res = document.documentElement.scrollLeft;\n
  }\n
  return res;\n
}\n
function getScrollTop(elem) {\n
  if (elem === window) {\n
    return getWindowScrollTop(elem);\n
  } else {\n
    return elem.scrollTop;\n
  }\n
}\n
function getScrollLeft(elem) {\n
  if (elem === window) {\n
    return getWindowScrollLeft(elem);\n
  } else {\n
    return elem.scrollLeft;\n
  }\n
}\n
function getScrollableElement(element) {\n
  var el = element.parentNode,\n
      props = [\'auto\', \'scroll\'],\n
      overflow,\n
      overflowX,\n
      overflowY,\n
      computedStyle = \'\',\n
      computedOverflow = \'\',\n
      computedOverflowY = \'\',\n
      computedOverflowX = \'\';\n
  while (el && el.style && document.body !== el) {\n
    overflow = el.style.overflow;\n
    overflowX = el.style.overflowX;\n
    overflowY = el.style.overflowY;\n
    if (overflow == \'scroll\' || overflowX == \'scroll\' || overflowY == \'scroll\') {\n
      return el;\n
    } else if (window.getComputedStyle) {\n
      computedStyle = window.getComputedStyle(el);\n
      computedOverflow = computedStyle.getPropertyValue(\'overflow\');\n
      computedOverflowY = computedStyle.getPropertyValue(\'overflow-y\');\n
      computedOverflowX = computedStyle.getPropertyValue(\'overflow-x\');\n
      if (computedOverflow === \'scroll\' || computedOverflowX === \'scroll\' || computedOverflowY === \'scroll\') {\n
        return el;\n
      }\n
    }\n
    if (el.clientHeight <= el.scrollHeight && (props.indexOf(overflowY) !== -1 || props.indexOf(overflow) !== -1 || props.indexOf(computedOverflow) !== -1 || props.indexOf(computedOverflowY) !== -1)) {\n
      return el;\n
    }\n
    if (el.clientWidth <= el.scrollWidth && (props.indexOf(overflowX) !== -1 || props.indexOf(overflow) !== -1 || props.indexOf(computedOverflow) !== -1 || props.indexOf(computedOverflowX) !== -1)) {\n
      return el;\n
    }\n
    el = el.parentNode;\n
  }\n
  return window;\n
}\n
function getTrimmingContainer(base) {\n
  var el = base.parentNode;\n
  while (el && el.style && document.body !== el) {\n
    if (el.style.overflow !== \'visible\' && el.style.overflow !== \'\') {\n
      return el;\n
    } else if (window.getComputedStyle) {\n
      var computedStyle = window.getComputedStyle(el);\n
      if (computedStyle.getPropertyValue(\'overflow\') !== \'visible\' && computedStyle.getPropertyValue(\'overflow\') !== \'\') {\n
        return el;\n
      }\n
    }\n
    el = el.parentNode;\n
  }\n
  return window;\n
}\n
function getStyle(elem, prop) {\n
  if (!elem) {\n
    return;\n
  } else if (elem === window) {\n
    if (prop === \'width\') {\n
      return window.innerWidth + \'px\';\n
    } else if (prop === \'height\') {\n
      return window.innerHeight + \'px\';\n
    }\n
    return;\n
  }\n
  var styleProp = elem.style[prop],\n
      computedStyle;\n
  if (styleProp !== "" && styleProp !== void 0) {\n
    return styleProp;\n
  } else {\n
    computedStyle = getComputedStyle(elem);\n
    if (computedStyle[prop] !== "" && computedStyle[prop] !== void 0) {\n
      return computedStyle[prop];\n
    }\n
    return void 0;\n
  }\n
}\n
function getComputedStyle(elem) {\n
  return elem.currentStyle || document.defaultView.getComputedStyle(elem);\n
}\n
function outerWidth(elem) {\n
  return elem.offsetWidth;\n
}\n
function outerHeight(elem) {\n
  if (hasCaptionProblem() && elem.firstChild && elem.firstChild.nodeName === \'CAPTION\') {\n
    return elem.offsetHeight + elem.firstChild.offsetHeight;\n
  } else {\n
    return elem.offsetHeight;\n
  }\n
}\n
function innerHeight(elem) {\n
  return elem.clientHeight || elem.innerHeight;\n
}\n
function innerWidth(elem) {\n
  return elem.clientWidth || elem.innerWidth;\n
}\n
function addEvent(element, event, callback) {\n
  if (window.addEventListener) {\n
    element.addEventListener(event, callback, false);\n
  } else {\n
    element.attachEvent(\'on\' + event, callback);\n
  }\n
}\n
function removeEvent(element, event, callback) {\n
  if (window.removeEventListener) {\n
    element.removeEventListener(event, callback, false);\n
  } else {\n
    element.detachEvent(\'on\' + event, callback);\n
  }\n
}\n
var _hasCaptionProblem;\n
function detectCaptionProblem() {\n
  var TABLE = document.createElement(\'TABLE\');\n
  TABLE.style.borderSpacing = 0;\n
  TABLE.style.borderWidth = 0;\n
  TABLE.style.padding = 0;\n
  var TBODY = document.createElement(\'TBODY\');\n
  TABLE.appendChild(TBODY);\n
  TBODY.appendChild(document.createElement(\'TR\'));\n
  TBODY.firstChild.appendChild(document.createElement(\'TD\'));\n
  TBODY.firstChild.firstChild.innerHTML = \'<tr><td>t<br>t</td></tr>\';\n
  var CAPTION = document.createElement(\'CAPTION\');\n
  CAPTION.innerHTML = \'c<br>c<br>c<br>c\';\n
  CAPTION.style.padding = 0;\n
  CAPTION.style.margin = 0;\n
  TABLE.insertBefore(CAPTION, TBODY);\n
  document.body.appendChild(TABLE);\n
  _hasCaptionProblem = (TABLE.offsetHeight < 2 * TABLE.lastChild.offsetHeight);\n
  document.body.removeChild(TABLE);\n
}\n
function hasCaptionProblem() {\n
  if (_hasCaptionProblem === void 0) {\n
    detectCaptionProblem();\n
  }\n
  return _hasCaptionProblem;\n
}\n
function getCaretPosition(el) {\n
  if (el.selectionStart) {\n
    return el.selectionStart;\n
  } else if (document.selection) {\n
    el.focus();\n
    var r = document.selection.createRange();\n
    if (r == null) {\n
      return 0;\n
    }\n
    var re = el.createTextRange(),\n
        rc = re.duplicate();\n
    re.moveToBookmark(r.getBookmark());\n
    rc.setEndPoint(\'EndToStart\', re);\n
    return rc.text.length;\n
  }\n
  return 0;\n
}\n
function getSelectionEndPosition(el) {\n
  if (el.selectionEnd) {\n
    return el.selectionEnd;\n
  } else if (document.selection) {\n
    var r = document.selection.createRange();\n
    if (r == null) {\n
      return 0;\n
    }\n
    var re = el.createTextRange();\n
    return re.text.indexOf(r.text) + r.text.length;\n
  }\n
}\n
function setCaretPosition(el, pos, endPos) {\n
  if (endPos === void 0) {\n
    endPos = pos;\n
  }\n
  if (el.setSelectionRange) {\n
    el.focus();\n
    el.setSelectionRange(pos, endPos);\n
  } else if (el.createTextRange) {\n
    var range = el.createTextRange();\n
    range.collapse(true);\n
    range.moveEnd(\'character\', endPos);\n
    range.moveStart(\'character\', pos);\n
    range.select();\n
  }\n
}\n
var cachedScrollbarWidth;\n
function walkontableCalculateScrollbarWidth() {\n
  var inner = document.createElement(\'p\');\n
  inner.style.width = "100%";\n
  inner.style.height = "200px";\n
  var outer = document.createElement(\'div\');\n
  outer.style.position = "absolute";\n
  outer.style.top = "0px";\n
  outer.style.left = "0px";\n
  outer.style.visibility = "hidden";\n
  outer.style.width = "200px";\n
  outer.style.height = "150px";\n
  outer.style.overflow = "hidden";\n
  outer.appendChild(inner);\n
  (document.body || document.documentElement).appendChild(outer);\n
  var w1 = inner.offsetWidth;\n
  outer.style.overflow = \'scroll\';\n
  var w2 = inner.offsetWidth;\n
  if (w1 == w2) {\n
    w2 = outer.clientWidth;\n
  }\n
  (document.body || document.documentElement).removeChild(outer);\n
  return (w1 - w2);\n
}\n
function getScrollbarWidth() {\n
  if (cachedScrollbarWidth === void 0) {\n
    cachedScrollbarWidth = walkontableCalculateScrollbarWidth();\n
  }\n
  return cachedScrollbarWidth;\n
}\n
var _isIE8 = !(document.createTextNode(\'test\').textContent);\n
function isIE8() {\n
  return isIE8;\n
}\n
var _isIE9 = !!(document.documentMode);\n
function isIE9() {\n
  return _isIE9;\n
}\n
var _isSafari = (/Safari/.test(navigator.userAgent) && /Apple Computer/.test(navigator.vendor));\n
function isSafari() {\n
  return _isSafari;\n
}\n
function setOverlayPosition(overlayElem, left, top) {\n
  if (_isIE8 || _isIE9) {\n
    overlayElem.style.top = top;\n
    overlayElem.style.left = left;\n
  } else if (_isSafari) {\n
    overlayElem.style[\'-webkit-transform\'] = \'translate3d(\' + left + \',\' + top + \',0)\';\n
  } else {\n
    overlayElem.style[\'transform\'] = \'translate3d(\' + left + \',\' + top + \',0)\';\n
  }\n
}\n
function getCssTransform(elem) {\n
  var transform;\n
  if (elem.style[\'transform\'] && (transform = elem.style[\'transform\']) != "") {\n
    return [\'transform\', transform];\n
  } else if (elem.style[\'-webkit-transform\'] && (transform = elem.style[\'-webkit-transform\']) != "") {\n
    return [\'-webkit-transform\', transform];\n
  } else {\n
    return -1;\n
  }\n
}\n
function resetCssTransform(elem) {\n
  if (elem[\'transform\'] && elem[\'transform\'] != "") {\n
    elem[\'transform\'] = "";\n
  } else if (elem[\'-webkit-transform\'] && elem[\'-webkit-transform\'] != "") {\n
    elem[\'-webkit-transform\'] = "";\n
  }\n
}\n
window.Handsontable = window.Handsontable || {};\n
Handsontable.Dom = {\n
  addClass: addClass,\n
  addEvent: addEvent,\n
  closest: closest,\n
  empty: empty,\n
  enableImmediatePropagation: enableImmediatePropagation,\n
  fastInnerHTML: fastInnerHTML,\n
  fastInnerText: fastInnerText,\n
  getCaretPosition: getCaretPosition,\n
  getComputedStyle: getComputedStyle,\n
  getCssTransform: getCssTransform,\n
  getScrollableElement: getScrollableElement,\n
  getScrollbarWidth: getScrollbarWidth,\n
  getScrollLeft: getScrollLeft,\n
  getScrollTop: getScrollTop,\n
  getStyle: getStyle,\n
  getSelectionEndPosition: getSelectionEndPosition,\n
  getTrimmingContainer: getTrimmingContainer,\n
  getWindowScrollLeft: getWindowScrollLeft,\n
  getWindowScrollTop: getWindowScrollTop,\n
  hasCaptionProblem: hasCaptionProblem,\n
  hasClass: hasClass,\n
  HTML_CHARACTERS: HTML_CHARACTERS,\n
  index: index,\n
  innerHeight: innerHeight,\n
  innerWidth: innerWidth,\n
  isChildOf: isChildOf,\n
  isChildOfWebComponentTable: isChildOfWebComponentTable,\n
  isIE8: isIE8,\n
  isIE9: isIE9,\n
  isSafari: isSafari,\n
  isVisible: isVisible,\n
  isWebComponentSupportedNatively: isWebComponentSupportedNatively,\n
  offset: offset,\n
  outerHeight: outerHeight,\n
  outerWidth: outerWidth,\n
  polymerUnwrap: polymerUnwrap,\n
  polymerWrap: polymerWrap,\n
  removeClass: removeClass,\n
  removeEvent: removeEvent,\n
  removeTextNodes: removeTextNodes,\n
  resetCssTransform: resetCssTransform,\n
  setCaretPosition: setCaretPosition,\n
  setOverlayPosition: setOverlayPosition\n
};\n
\n
\n
//# \n
},{}],32:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  EditorManager: {get: function() {\n
      return EditorManager;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__,\n
    $__helpers_46_js__,\n
    $__dom_46_js__,\n
    $__editors_46_js__,\n
    $__eventManager_46_js__;\n
var WalkontableCellCoords = ($__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./3rdparty/walkontable/src/cell/coords.js"), $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
var dom = ($__dom_46_js__ = require("./dom.js"), $__dom_46_js__ && $__dom_46_js__.__esModule && $__dom_46_js__ || {default: $__dom_46_js__});\n
var getEditor = ($__editors_46_js__ = require("./editors.js"), $__editors_46_js__ && $__editors_46_js__.__esModule && $__editors_46_js__ || {default: $__editors_46_js__}).getEditor;\n
var eventManagerObject = ($__eventManager_46_js__ = require("./eventManager.js"), $__eventManager_46_js__ && $__eventManager_46_js__.__esModule && $__eventManager_46_js__ || {default: $__eventManager_46_js__}).eventManager;\n
;\n
Handsontable.EditorManager = EditorManager;\n
function EditorManager(instance, priv, selection) {\n
  var _this = this,\n
      keyCodes = helper.keyCode,\n
      destroyed = false,\n
      eventManager,\n
      activeEditor;\n
  eventManager = eventManagerObject(instance);\n
  function moveSelectionAfterEnter(shiftKey) {\n
    var enterMoves = typeof priv.settings.enterMoves === \'function\' ? priv.settings.enterMoves(event) : priv.settings.enterMoves;\n
    if (shiftKey) {\n
      selection.transformStart(-enterMoves.row, -enterMoves.col);\n
    } else {\n
      selection.transformStart(enterMoves.row, enterMoves.col, true);\n
    }\n
  }\n
  function moveSelectionUp(shiftKey) {\n
    if (shiftKey) {\n
      selection.transformEnd(-1, 0);\n
    } else {\n
      selection.transformStart(-1, 0);\n
    }\n
  }\n
  function moveSelectionDown(shiftKey) {\n
    if (shiftKey) {\n
      selection.transformEnd(1, 0);\n
    } else {\n
      selection.transformStart(1, 0);\n
    }\n
  }\n
  function moveSelectionRight(shiftKey) {\n
    if (shiftKey) {\n
      selection.transformEnd(0, 1);\n
    } else {\n
      selection.transformStart(0, 1);\n
    }\n
  }\n
  function moveSelectionLeft(shiftKey) {\n
    if (shiftKey) {\n
      selection.transformEnd(0, -1);\n
    } else {\n
      selection.transformStart(0, -1);\n
    }\n
  }\n
  function onKeyDown(event) {\n
    var ctrlDown,\n
        rangeModifier;\n
    if (!instance.isListening()) {\n
      return;\n
    }\n
    Handsontable.hooks.run(instance, \'beforeKeyDown\', event);\n
    if (destroyed) {\n
      return;\n
    }\n
    dom.enableImmediatePropagation(event);\n
    if (event.isImmediatePropagationStopped()) {\n
      return;\n
    }\n
    priv.lastKeyCode = event.keyCode;\n
    if (!selection.isSelected()) {\n
      return;\n
    }\n
    ctrlDown = (event.ctrlKey || event.metaKey) && !event.altKey;\n
    if (activeEditor && !activeEditor.isWaiting()) {\n
      if (!helper.isMetaKey(event.keyCode) && !ctrlDown && !_this.isEditorOpened()) {\n
        _this.openEditor("", event);\n
        return;\n
      }\n
    }\n
    rangeModifier = event.shiftKey ? selection.setRangeEnd : selection.setRangeStart;\n
    switch (event.keyCode) {\n
      case keyCodes.A:\n
        if (ctrlDown) {\n
          selection.selectAll();\n
          event.preventDefault();\n
          helper.stopPropagation(event);\n
        }\n
        break;\n
      case keyCodes.ARROW_UP:\n
        if (_this.isEditorOpened() && activeEditor && !activeEditor.isWaiting()) {\n
          _this.closeEditorAndSaveChanges(ctrlDown);\n
        }\n
        moveSelectionUp(event.shiftKey);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.ARROW_DOWN:\n
        if (_this.isEditorOpened() && activeEditor && !activeEditor.isWaiting()) {\n
          _this.closeEditorAndSaveChanges(ctrlDown);\n
        }\n
        moveSelectionDown(event.shiftKey);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.ARROW_RIGHT:\n
        if (_this.isEditorOpened() && activeEditor && !activeEditor.isWaiting()) {\n
          _this.closeEditorAndSaveChanges(ctrlDown);\n
        }\n
        moveSelectionRight(event.shiftKey);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.ARROW_LEFT:\n
        if (_this.isEditorOpened() && activeEditor && !activeEditor.isWaiting()) {\n
          _this.closeEditorAndSaveChanges(ctrlDown);\n
        }\n
        moveSelectionLeft(event.shiftKey);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.TAB:\n
        var tabMoves = typeof priv.settings.tabMoves === \'function\' ? priv.settings.tabMoves(event) : priv.settings.tabMoves;\n
        if (event.shiftKey) {\n
          selection.transformStart(-tabMoves.row, -tabMoves.col);\n
        } else {\n
          selection.transformStart(tabMoves.row, tabMoves.col, true);\n
        }\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.BACKSPACE:\n
      case keyCodes.DELETE:\n
        selection.empty(event);\n
        _this.prepareEditor();\n
        event.preventDefault();\n
        break;\n
      case keyCodes.F2:\n
        _this.openEditor(null, event);\n
        event.preventDefault();\n
        break;\n
      case keyCodes.ENTER:\n
        if (_this.isEditorOpened()) {\n
          if (activeEditor && activeEditor.state !== Handsontable.EditorState.WAITING) {\n
            _this.closeEditorAndSaveChanges(ctrlDown);\n
          }\n
          moveSelectionAfterEnter(event.shiftKey);\n
        } else {\n
          if (instance.getSettings().enterBeginsEditing) {\n
            _this.openEditor(null, event);\n
          } else {\n
            moveSelectionAfterEnter(event.shiftKey);\n
          }\n
        }\n
        event.preventDefault();\n
        event.stopImmediatePropagation();\n
        break;\n
      case keyCodes.ESCAPE:\n
        if (_this.isEditorOpened()) {\n
          _this.closeEditorAndRestoreOriginalValue(ctrlDown);\n
        }\n
        event.preventDefault();\n
        break;\n
      case keyCodes.HOME:\n
        if (event.ctrlKey || event.metaKey) {\n
          rangeModifier(new WalkontableCellCoords(0, priv.selRange.from.col));\n
        } else {\n
          rangeModifier(new WalkontableCellCoords(priv.selRange.from.row, 0));\n
        }\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.END:\n
        if (event.ctrlKey || event.metaKey) {\n
          rangeModifier(new WalkontableCellCoords(instance.countRows() - 1, priv.selRange.from.col));\n
        } else {\n
          rangeModifier(new WalkontableCellCoords(priv.selRange.from.row, instance.countCols() - 1));\n
        }\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.PAGE_UP:\n
        selection.transformStart(-instance.countVisibleRows(), 0);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
      case keyCodes.PAGE_DOWN:\n
        selection.transformStart(instance.countVisibleRows(), 0);\n
        event.preventDefault();\n
        helper.stopPropagation(event);\n
        break;\n
    }\n
  }\n
  function init() {\n
    instance.addHook(\'afterDocumentKeyDown\', onKeyDown);\n
    eventManager.addEventListener(document.documentElement, \'keydown\', function(event) {\n
      instance.runHooks(\'afterDocumentKeyDown\', event);\n
    });\n
    function onDblClick(event, coords, elem) {\n
      if (elem.nodeName == "TD") {\n
        _this.openEditor();\n
      }\n
    }\n
    instance.view.wt.update(\'onCellDblClick\', onDblClick);\n
    instance.addHook(\'afterDestroy\', function() {\n
      destroyed = true;\n
    });\n
  }\n
  this.destroyEditor = function(revertOriginal) {\n
    this.closeEditor(revertOriginal);\n
  };\n
  this.getActiveEditor = function() {\n
    return activeEditor;\n
  };\n
  this.prepareEditor = function() {\n
    var row,\n
        col,\n
        prop,\n
        td,\n
        originalValue,\n
        cellProperties,\n
        editorClass;\n
    if (activeEditor && activeEditor.isWaiting()) {\n
      this.closeEditor(false, false, function(dataSaved) {\n
        if (dataSaved) {\n
          _this.prepareEditor();\n
        }\n
      });\n
      return;\n
    }\n
    row = priv.selRange.highlight.row;\n
    col = priv.selRange.highlight.col;\n
    prop = instance.colToProp(col);\n
    td = instance.getCell(row, col);\n
    originalValue = instance.getDataAtCell(row, col);\n
    cellProperties = instance.getCellMeta(row, col);\n
    editorClass = instance.getCellEditor(cellProperties);\n
    if (editorClass) {\n
      activeEditor = Handsontable.editors.getEditor(editorClass, instance);\n
      activeEditor.prepare(row, col, prop, td, originalValue, cellProperties);\n
    } else {\n
      activeEditor = void 0;\n
    }\n
  };\n
  this.isEditorOpened = function() {\n
    return activeEditor && activeEditor.isOpened();\n
  };\n
  this.openEditor = function(initialValue, event) {\n
    if (activeEditor && !activeEditor.cellProperties.readOnly) {\n
      activeEditor.beginEditing(initialValue, event);\n
    } else if (activeEditor && activeEditor.cellProperties.readOnly) {\n
      if (event && event.keyCode === helper.keyCode.ENTER) {\n
        moveSelectionAfterEnter();\n
      }\n
    }\n
  };\n
  this.closeEditor = function(restoreOriginalValue, ctrlDown, callback) {\n
    if (!activeEditor) {\n
      if (callback) {\n
        callback(false);\n
      }\n
    } else {\n
      activeEditor.finishEditing(restoreOriginalValue, ctrlDown, callback);\n
    }\n
  };\n
  this.closeEditorAndSaveChanges = function(ctrlDown) {\n
    return this.closeEditor(false, ctrlDown);\n
  };\n
  this.closeEditorAndRestoreOriginalValue = function(ctrlDown) {\n
    return this.closeEditor(true, ctrlDown);\n
  };\n
  init();\n
}\n
\n
\n
//# \n
},{"./3rdparty/walkontable/src/cell/coords.js":9,"./dom.js":31,"./editors.js":33,"./eventManager.js":45,"./helpers.js":46}],33:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  registerEditor: {get: function() {\n
      return registerEditor;\n
    }},\n
  getEditor: {get: function() {\n
      return getEditor;\n
    }},\n
  hasEditor: {get: function() {\n
      return hasEditor;\n
    }},\n
  getEditorConstructor: {get: function() {\n
      return getEditorConstructor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__helpers_46_js__;\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
;\n
var registeredEditorNames = {},\n
    registeredEditorClasses = new WeakMap();\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.registerEditor = registerEditor;\n
Handsontable.editors.getEditor = getEditor;\n
function RegisteredEditor(editorClass) {\n
  var Clazz,\n
      instances;\n
  instances = {};\n
  Clazz = editorClass;\n
  this.getConstructor = function() {\n
    return editorClass;\n
  };\n
  this.getInstance = function(hotInstance) {\n
    if (!(hotInstance.guid in instances)) {\n
      instances[hotInstance.guid] = new Clazz(hotInstance);\n
    }\n
    return instances[hotInstance.guid];\n
  };\n
}\n
function registerEditor(editorName, editorClass) {\n
  var editor = new RegisteredEditor(editorClass);\n
  if (typeof editorName === "string") {\n
    registeredEditorNames[editorName] = editor;\n
  }\n
  registeredEditorClasses.set(editorClass, editor);\n
}\n
function getEditor(editorName, hotInstance) {\n
  var editor;\n
  if (typeof editorName == \'function\') {\n
    if (!(registeredEditorClasses.get(editorName))) {\n
      registerEditor(null, editorName);\n
    }\n
    editor = registeredEditorClasses.get(editorName);\n
  } else if (typeof editorName == \'string\') {\n
    editor = registeredEditorNames[editorName];\n
  } else {\n
    throw Error(\'Only strings and functions can be passed as "editor" parameter \');\n
  }\n
  if (!editor) {\n
    throw Error(\'No editor registered under name "\' + editorName + \'"\');\n
  }\n
  return editor.getInstance(hotInstance);\n
}\n
function getEditorConstructor(editorName) {\n
  var editor;\n
  if (typeof editorName == \'string\') {\n
    editor = registeredEditorNames[editorName];\n
  } else {\n
    throw Error(\'Only strings and functions can be passed as "editor" parameter \');\n
  }\n
  if (!editor) {\n
    throw Error(\'No editor registered under name "\' + editorName + \'"\');\n
  }\n
  return editor.getConstructor();\n
}\n
function hasEditor(editorName) {\n
  return registeredEditorNames[editorName] ? true : false;\n
}\n
\n
\n
//# \n
},{"./helpers.js":46}],34:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  BaseEditor: {get: function() {\n
      return BaseEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var WalkontableCellCoords = ($___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.BaseEditor = BaseEditor;\n
Handsontable.EditorState = {\n
  VIRGIN: \'STATE_VIRGIN\',\n
  EDITING: \'STATE_EDITING\',\n
  WAITING: \'STATE_WAITING\',\n
  FINISHED: \'STATE_FINISHED\'\n
};\n
function BaseEditor(instance) {\n
  this.instance = instance;\n
  this.state = Handsontable.EditorState.VIRGIN;\n
  this._opened = false;\n
  this._closeCallback = null;\n
  this.init();\n
}\n
BaseEditor.prototype._fireCallbacks = function(result) {\n
  if (this._closeCallback) {\n
    this._closeCallback(result);\n
    this._closeCallback = null;\n
  }\n
};\n
BaseEditor.prototype.init = function() {};\n
BaseEditor.prototype.getValue = function() {\n
  throw Error(\'Editor getValue() method unimplemented\');\n
};\n
BaseEditor.prototype.setValue = function(newValue) {\n
  throw Error(\'Editor setValue() method unimplemented\');\n
};\n
BaseEditor.prototype.open = function() {\n
  throw Error(\'Editor open() method unimplemented\');\n
};\n
BaseEditor.prototype.close = function() {\n
  throw Error(\'Editor close() method unimplemented\');\n
};\n
BaseEditor.prototype.prepare = function(row, col, prop, td, originalValue, cellProperties) {\n
  this.TD = td;\n
  this.row = row;\n
  this.col = col;\n
  this.prop = prop;\n
  this.originalValue = originalValue;\n
  this.cellProperties = cellProperties;\n
  this.state = Handsontable.EditorState.VIRGIN;\n
};\n
BaseEditor.prototype.extend = function() {\n
  var baseClass = this.constructor;\n
  function Editor() {\n
    baseClass.apply(this, arguments);\n
  }\n
  function inherit(Child, Parent) {\n
    function Bridge() {}\n
    Bridge.prototype = Parent.prototype;\n
    Child.prototype = new Bridge();\n
    Child.prototype.constructor = Child;\n
    return Child;\n
  }\n
  return inherit(Editor, baseClass);\n
};\n
BaseEditor.prototype.saveValue = function(val, ctrlDown) {\n
  var sel,\n
      tmp;\n
  if (ctrlDown) {\n
    sel = this.instance.getSelected();\n
    if (sel[0] > sel[2]) {\n
      tmp = sel[0];\n
      sel[0] = sel[2];\n
      sel[2] = tmp;\n
    }\n
    if (sel[1] > sel[3]) {\n
      tmp = sel[1];\n
      sel[1] = sel[3];\n
      sel[3] = tmp;\n
    }\n
    this.instance.populateFromArray(sel[0], sel[1], val, sel[2], sel[3], \'edit\');\n
  } else {\n
    this.instance.populateFromArray(this.row, this.col, val, null, null, \'edit\');\n
  }\n
};\n
BaseEditor.prototype.beginEditing = function(initialValue, event) {\n
  if (this.state != Handsontable.EditorState.VIRGIN) {\n
    return;\n
  }\n
  this.instance.view.scrollViewport(new WalkontableCellCoords(this.row, this.col));\n
  this.instance.view.render();\n
  this.state = Handsontable.EditorState.EDITING;\n
  initialValue = typeof initialValue == \'string\' ? initialValue : this.originalValue;\n
  this.setValue(helper.stringify(initialValue));\n
  this.open(event);\n
  this._opened = true;\n
  this.focus();\n
  this.instance.view.render();\n
};\n
BaseEditor.prototype.finishEditing = function(restoreOriginalValue, ctrlDown, callback) {\n
  var _this = this,\n
      val;\n
  if (callback) {\n
    var previousCloseCallback = this._closeCallback;\n
    this._closeCallback = function(result) {\n
      if (previousCloseCallback) {\n
        previousCloseCallback(result);\n
      }\n
      callback(result);\n
    };\n
  }\n
  if (this.isWaiting()) {\n
    return;\n
  }\n
  if (this.state == Handsontable.EditorState.VIRGIN) {\n
    this.instance._registerTimeout(setTimeout(function() {\n
      _this._fireCallbacks(true);\n
    }, 0));\n
    return;\n
  }\n
  if (this.state == Handsontable.EditorState.EDITING) {\n
    if (restoreOriginalValue) {\n
      this.cancelChanges();\n
      this.instance.view.render();\n
      return;\n
    }\n
    if (this.instance.getSettings().trimWhitespace) {\n
      val = [[typeof this.getValue() === \'string\' ? String.prototype.trim.call(this.getValue() || \'\') : this.getValue()]];\n
    } else {\n
      val = [[this.getValue()]];\n
    }\n
    this.state = Handsontable.EditorState.WAITING;\n
    this.saveValue(val, ctrlDown);\n
    if (this.instance.getCellValidator(this.cellProperties)) {\n
      this.instance.addHookOnce(\'postAfterValidate\', function(result) {\n
        _this.state = Handsontable.EditorState.FINISHED;\n
        _this.discardEditor(result);\n
      });\n
    } else {\n
      this.state = Handsontable.EditorState.FINISHED;\n
      this.discardEditor(true);\n
    }\n
  }\n
};\n
BaseEditor.prototype.cancelChanges = function() {\n
  this.state = Handsontable.EditorState.FINISHED;\n
  this.discardEditor();\n
};\n
BaseEditor.prototype.discardEditor = function(result) {\n
  if (this.state !== Handsontable.EditorState.FINISHED) {\n
    return;\n
  }\n
  if (result === false && this.cellProperties.allowInvalid !== true) {\n
    this.instance.selectCell(this.row, this.col);\n
    this.focus();\n
    this.state = Handsontable.EditorState.EDITING;\n
    this._fireCallbacks(false);\n
  } else {\n
    this.close();\n
    this._opened = false;\n
    this.state = Handsontable.EditorState.VIRGIN;\n
    this._fireCallbacks(true);\n
  }\n
};\n
BaseEditor.prototype.isOpened = function() {\n
  return this._opened;\n
};\n
BaseEditor.prototype.isWaiting = function() {\n
  return this.state === Handsontable.EditorState.WAITING;\n
};\n
\n
\n
//# \n
},{"./../3rdparty/walkontable/src/cell/coords.js":9,"./../helpers.js":46}],35:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  AutocompleteEditor: {get: function() {\n
      return AutocompleteEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_dom_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $__handsontableEditor_46_js__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditorConstructor = $__0.getEditorConstructor,\n
    registerEditor = $__0.registerEditor;\n
var HandsontableEditor = ($__handsontableEditor_46_js__ = require("./handsontableEditor.js"), $__handsontableEditor_46_js__ && $__handsontableEditor_46_js__.__esModule && $__handsontableEditor_46_js__ || {default: $__handsontableEditor_46_js__}).HandsontableEditor;\n
var AutocompleteEditor = HandsontableEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.AutocompleteEditor = AutocompleteEditor;\n
AutocompleteEditor.prototype.init = function() {\n
  HandsontableEditor.prototype.init.apply(this, arguments);\n
  this.query = null;\n
  this.choices = [];\n
};\n
AutocompleteEditor.prototype.createElements = function() {\n
  HandsontableEditor.prototype.createElements.apply(this, arguments);\n
  dom.addClass(this.htContainer, \'autocompleteEditor\');\n
  dom.addClass(this.htContainer, window.navigator.platform.indexOf(\'Mac\') !== -1 ? \'htMacScroll\' : \'\');\n
};\n
var skipOne = false;\n
function onBeforeKeyDown(event) {\n
  skipOne = false;\n
  var editor = this.getActiveEditor();\n
  var keyCodes = helper.keyCode;\n
  if (helper.isPrintableChar(event.keyCode) || event.keyCode === keyCodes.BACKSPACE || event.keyCode === keyCodes.DELETE || event.keyCode === keyCodes.INSERT) {\n
    var timeOffset = 0;\n
    if (event.keyCode === keyCodes.C && (event.ctrlKey || event.metaKey)) {\n
      return;\n
    }\n
    if (!editor.isOpened()) {\n
      timeOffset += 10;\n
    }\n
    editor.instance._registerTimeout(setTimeout(function() {\n
      editor.queryChoices(editor.TEXTAREA.value);\n
      skipOne = true;\n
    }, timeOffset));\n
  }\n
}\n
AutocompleteEditor.prototype.prepare = function() {\n
  this.instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  HandsontableEditor.prototype.prepare.apply(this, arguments);\n
};\n
AutocompleteEditor.prototype.open = function() {\n
  HandsontableEditor.prototype.open.apply(this, arguments);\n
  var choicesListHot = this.htEditor.getInstance();\n
  var that = this;\n
  this.TEXTAREA.style.visibility = \'visible\';\n
  this.focus();\n
  choicesListHot.updateSettings({\n
    \'colWidths\': [dom.outerWidth(this.TEXTAREA) - 2],\n
    width: dom.outerWidth(this.TEXTAREA) + dom.getScrollbarWidth() + 2,\n
    afterRenderer: function(TD, row, col, prop, value) {\n
      var caseSensitive = this.getCellMeta(row, col).filteringCaseSensitive === true,\n
          indexOfMatch,\n
          match;\n
      if (value) {\n
        indexOfMatch = caseSensitive ? value.indexOf(this.query) : value.toLowerCase().indexOf(that.query.toLowerCase());\n
        if (indexOfMatch != -1) {\n
          match = value.substr(indexOfMatch, that.query.length);\n
          TD.innerHTML = value.replace(match, \'<strong>\' + match + \'</strong>\');\n
        }\n
      }\n
    }\n
  });\n
  this.htEditor.view.wt.wtTable.holder.parentNode.style[\'padding-right\'] = dom.getScrollbarWidth() + 2 + \'px\';\n
  if (skipOne) {\n
    skipOne = false;\n
  }\n
  that.instance._registerTimeout(setTimeout(function() {\n
    that.queryChoices(that.TEXTAREA.value);\n
  }, 0));\n
};\n
AutocompleteEditor.prototype.close = function() {\n
  HandsontableEditor.prototype.close.apply(this, arguments);\n
};\n
AutocompleteEditor.prototype.queryChoices = function(query) {\n
  this.query = query;\n
  if (typeof this.cellProperties.source == \'function\') {\n
    var that = this;\n
    this.cellProperties.source(query, function(choices) {\n
      that.updateChoicesList(choices);\n
    });\n
  } else if (Array.isArray(this.cellProperties.source)) {\n
    var choices;\n
    if (!query || this.cellProperties.filter === false) {\n
      choices = this.cellProperties.source;\n
    } else {\n
      var filteringCaseSensitive = this.cellProperties.filteringCaseSensitive === true;\n
      var lowerCaseQuery = query.toLowerCase();\n
      choices = this.cellProperties.source.filter(function(choice) {\n
        if (filteringCaseSensitive) {\n
          return choice.indexOf(query) != -1;\n
        } else {\n
          return choice.toLowerCase().indexOf(lowerCaseQuery) != -1;\n
        }\n
      });\n
    }\n
    this.updateChoicesList(choices);\n
  } else {\n
    this.updateChoicesList([]);\n
  }\n
};\n
AutocompleteEditor.prototype.updateChoicesList = function(choices) {\n
  var pos = dom.getCaretPosition(this.TEXTAREA),\n
      endPos = dom.getSelectionEndPosition(this.TEXTAREA);\n
  var orderByRelevance = AutocompleteEditor.sortByRelevance(this.getValue(), choices, this.cellProperties.filteringCaseSensitive);\n
  var highlightIndex;\n
  if (this.cellProperties.filter != false) {\n
    var sorted = [];\n
    for (var i = 0,\n
        choicesCount = orderByRelevance.length; i < choicesCount; i++) {\n
      sorted.push(choices[orderByRelevance[i]]);\n
    }\n
    highlightIndex = 0;\n
    choices = sorted;\n
  } else {\n
    highlightIndex = orderByRelevance[0];\n
  }\n
  this.choices = choices;\n
  this.htEditor.loadData(helper.pivot([choices]));\n
  this.updateDropdownHeight();\n
  if (this.cellProperties.strict === true) {\n
    this.highlightBestMatchingChoice(highlightIndex);\n
  }\n
  this.instance.listen();\n
  this.TEXTAREA.focus();\n
  dom.setCaretPosition(this.TEXTAREA, pos, (pos != endPos ? endPos : void 0));\n
};\n
AutocompleteEditor.prototype.updateDropdownHeight = function() {\n
  this.htEditor.updateSettings({height: this.getDropdownHeight()});\n
  this.htEditor.view.wt.wtTable.alignOverlaysWithTrimmingContainer();\n
};\n
AutocompleteEditor.prototype.finishEditing = function(restoreOriginalValue) {\n
  if (!restoreOriginalValue) {\n
    this.instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  }\n
  HandsontableEditor.prototype.finishEditing.apply(this, arguments);\n
};\n
AutocompleteEditor.prototype.highlightBestMatchingChoice = function(index) {\n
  if (typeof index === "number") {\n
    this.htEditor.selectCell(index, 0);\n
  } else {\n
    this.htEditor.deselectCell();\n
  }\n
};\n
AutocompleteEditor.sortByRelevance = function(value, choices, caseSensitive) {\n
  var choicesRelevance = [],\n
      currentItem,\n
      valueLength = value.length,\n
      valueIndex,\n
      charsLeft,\n
      result = [],\n
      i,\n
      choicesCount;\n
  if (valueLength === 0) {\n
    for (i = 0, choicesCount = choices.length; i < choicesCount; i++) {\n
      result.push(i);\n
    }\n
    return result;\n
  }\n
  for (i = 0, choicesCount = choices.length; i < choicesCount; i++) {\n
    currentItem = choices[i];\n
    if (caseSensitive) {\n
      valueIndex = currentItem.indexOf(value);\n
    } else {\n
      valueIndex = currentItem.toLowerCase().indexOf(value.toLowerCase());\n
    }\n
    if (valueIndex == -1) {\n
      continue;\n
    }\n
    charsLeft = currentItem.length - valueIndex - valueLength;\n
    choicesRelevance.push({\n
      baseIndex: i,\n
      index: valueIndex,\n
      charsLeft: charsLeft,\n
      value: currentItem\n
    });\n
  }\n
  choicesRelevance.sort(function(a, b) {\n
    if (b.index === -1) {\n
      return -1;\n
    }\n
    if (a.index === -1) {\n
      return 1;\n
    }\n
    if (a.index < b.index) {\n
      return -1;\n
    } else if (b.index < a.index) {\n
      return 1;\n
    } else if (a.index === b.index) {\n
      if (a.charsLeft < b.charsLeft) {\n
        return -1;\n
      } else if (a.charsLeft > b.charsLeft) {\n
        return 1;\n
      } else {\n
        return 0;\n
      }\n
    }\n
  });\n
  for (i = 0, choicesCount = choicesRelevance.length; i < choicesCount; i++) {\n
    result.push(choicesRelevance[i].baseIndex);\n
  }\n
  return result;\n
};\n
AutocompleteEditor.prototype.getDropdownHeight = function() {\n
  var firstRowHeight = this.htEditor.getInstance().getRowHeight(0) || 23;\n
  return this.choices.length >= 10 ? 10 * firstRowHeight : this.choices.length * firstRowHeight + 8;\n
};\n
registerEditor(\'autocomplete\', AutocompleteEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./../helpers.js":46,"./handsontableEditor.js":39}],36:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  CheckboxEditor: {get: function() {\n
      return CheckboxEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_editors_46_js__,\n
    $___95_baseEditor_46_js__;\n
var registerEditor = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}).registerEditor;\n
var BaseEditor = ($___95_baseEditor_46_js__ = require("./_baseEditor.js"), $___95_baseEditor_46_js__ && $___95_baseEditor_46_js__.__esModule && $___95_baseEditor_46_js__ || {default: $___95_baseEditor_46_js__}).BaseEditor;\n
var CheckboxEditor = BaseEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.CheckboxEditor = CheckboxEditor;\n
CheckboxEditor.prototype.beginEditing = function() {\n
  var checkbox = this.TD.querySelector(\'input[type="checkbox"]\');\n
  if (checkbox) {\n
    checkbox.click();\n
  }\n
};\n
CheckboxEditor.prototype.finishEditing = function() {};\n
CheckboxEditor.prototype.init = function() {};\n
CheckboxEditor.prototype.open = function() {};\n
CheckboxEditor.prototype.close = function() {};\n
CheckboxEditor.prototype.getValue = function() {};\n
CheckboxEditor.prototype.setValue = function() {};\n
CheckboxEditor.prototype.focus = function() {};\n
registerEditor(\'checkbox\', CheckboxEditor);\n
\n
\n
//# \n
},{"./../editors.js":33,"./_baseEditor.js":34}],37:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  DateEditor: {get: function() {\n
      return DateEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_dom_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $__textEditor_46_js__,\n
    $___46__46__47_eventManager_46_js__,\n
    $__moment__,\n
    $__pikaday__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var TextEditor = ($__textEditor_46_js__ = require("./textEditor.js"), $__textEditor_46_js__ && $__textEditor_46_js__.__esModule && $__textEditor_46_js__ || {default: $__textEditor_46_js__}).TextEditor;\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
var moment = ($__moment__ = require("moment"), $__moment__ && $__moment__.__esModule && $__moment__ || {default: $__moment__}).default;\n
var Pikaday = ($__pikaday__ = require("pikaday"), $__pikaday__ && $__pikaday__.__esModule && $__pikaday__ || {default: $__pikaday__}).default;\n
var DateEditor = TextEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.DateEditor = DateEditor;\n
DateEditor.prototype.init = function() {\n
  if (typeof moment !== \'function\') {\n
    throw new Error("You need to include moment.js to your project.");\n
  }\n
  if (typeof Pikaday !== \'function\') {\n
    throw new Error("You need to include Pikaday to your project.");\n
  }\n
  TextEditor.prototype.init.apply(this, arguments);\n
  this.isCellEdited = false;\n
  var that = this;\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    that.parentDestroyed = true;\n
    that.destroyElements();\n
  });\n
};\n
DateEditor.prototype.createElements = function() {\n
  var that = this;\n
  TextEditor.prototype.createElements.apply(this, arguments);\n
  this.defaultDateFormat = \'DD/MM/YYYY\';\n
  this.datePicker = document.createElement(\'DIV\');\n
  this.datePickerStyle = this.datePicker.style;\n
  this.datePickerStyle.position = \'absolute\';\n
  this.datePickerStyle.top = 0;\n
  this.datePickerStyle.left = 0;\n
  this.datePickerStyle.zIndex = 9999;\n
  dom.addClass(this.datePicker, \'htDatepickerHolder\');\n
  document.body.appendChild(this.datePicker);\n
  var htInput = this.TEXTAREA;\n
  var defaultOptions = {\n
    format: that.defaultDateFormat,\n
    field: htInput,\n
    trigger: htInput,\n
    container: that.datePicker,\n
    reposition: false,\n
    bound: false,\n
    onSelect: function(dateStr) {\n
      if (!isNaN(dateStr.getTime())) {\n
        dateStr = moment(dateStr).format(that.cellProperties.dateFormat || that.defaultDateFormat);\n
      }\n
      that.setValue(dateStr);\n
      that.hideDatepicker();\n
    },\n
    onClose: function() {\n
      if (!that.parentDestroyed) {\n
        that.finishEditing(false);\n
      }\n
    }\n
  };\n
  this.$datePicker = new Pikaday(defaultOptions);\n
  var eventManager = eventManagerObject(this);\n
  eventManager.addEventListener(this.datePicker, \'mousedown\', function(event) {\n
    helper.stopPropagation(event);\n
  });\n
  this.hideDatepicker();\n
};\n
DateEditor.prototype.destroyElements = function() {\n
  this.$datePicker.destroy();\n
};\n
DateEditor.prototype.prepare = function() {\n
  this._opened = false;\n
  TextEditor.prototype.prepare.apply(this, arguments);\n
};\n
DateEditor.prototype.open = function(event) {\n
  TextEditor.prototype.open.call(this);\n
  this.showDatepicker(event);\n
};\n
DateEditor.prototype.close = function() {\n
  var that = this;\n
  this._opened = false;\n
  this.instance._registerTimeout(setTimeout(function() {\n
    that.instance.selection.refreshBorders();\n
  }, 0));\n
  TextEditor.prototype.close.apply(this, arguments);\n
};\n
DateEditor.prototype.finishEditing = function(isCancelled, ctrlDown) {\n
  if (isCancelled) {\n
    var value = this.originalValue;\n
    if (value !== void 0) {\n
      this.setValue(value);\n
    }\n
  }\n
  this.hideDatepicker();\n
  TextEditor.prototype.finishEditing.apply(this, arguments);\n
};\n
DateEditor.prototype.showDatepicker = function(event) {\n
  var offset = this.TD.getBoundingClientRect(),\n
      dateFormat = this.cellProperties.dateFormat || this.defaultDateFormat,\n
      datePickerConfig = this.$datePicker.config(),\n
      dateStr,\n
      isMouseDown = this.instance.view.isMouseDown(),\n
      isMeta = event ? helper.isMetaKey(event.keyCode) : false;\n
  this.datePickerStyle.top = (window.pageYOffset + offset.top + dom.outerHeight(this.TD)) + \'px\';\n
  this.datePickerStyle.left = (window.pageXOffset + offset.left) + \'px\';\n
  this.$datePicker._onInputFocus = function() {};\n
  datePickerConfig.format = dateFormat;\n
  if (this.originalValue) {\n
    dateStr = this.originalValue;\n
    if (moment(dateStr, dateFormat, true).isValid()) {\n
      this.$datePicker.setMoment(moment(dateStr, dateFormat), true);\n
    }\n
    if (!isMeta) {\n
      if (!isMouseDown) {\n
        this.setValue(\'\');\n
      }\n
    }\n
  } else {\n
    if (this.cellProperties.defaultDate) {\n
      dateStr = this.cellProperties.defaultDate;\n
      datePickerConfig.defaultDate = dateStr;\n
      if (moment(dateStr, dateFormat, true).isValid()) {\n
        this.$datePicker.setMoment(moment(dateStr, dateFormat), true);\n
      }\n
      if (!isMeta) {\n
        if (!isMouseDown) {\n
          this.setValue(\'\');\n
        }\n
      }\n
    }\n
  }\n
  this.datePickerStyle.display = \'block\';\n
  this.$datePicker.show();\n
};\n
DateEditor.prototype.hideDatepicker = function() {\n
  this.datePickerStyle.display = \'none\';\n
  this.$datePicker.hide();\n
};\n
registerEditor(\'date\', DateEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./../eventManager.js":45,"./../helpers.js":46,"./textEditor.js":44,"moment":"moment","pikaday":"pikaday"}],38:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  DropdownEditor: {get: function() {\n
      return DropdownEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_editors_46_js__,\n
    $__autocompleteEditor_46_js__;\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var AutocompleteEditor = ($__autocompleteEditor_46_js__ = require("./autocompleteEditor.js"), $__autocompleteEditor_46_js__ && $__autocompleteEditor_46_js__.__esModule && $__autocompleteEditor_46_js__ || {default: $__autocompleteEditor_46_js__}).AutocompleteEditor;\n
var DropdownEditor = AutocompleteEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.DropdownEditor = DropdownEditor;\n
DropdownEditor.prototype.prepare = function() {\n
  AutocompleteEditor.prototype.prepare.apply(this, arguments);\n
  this.cellProperties.filter = false;\n
  this.cellProperties.strict = true;\n
};\n
registerEditor(\'dropdown\', DropdownEditor);\n
\n
\n
//# \n
},{"./../editors.js":33,"./autocompleteEditor.js":35}],39:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  HandsontableEditor: {get: function() {\n
      return HandsontableEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_dom_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $__textEditor_46_js__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var TextEditor = ($__textEditor_46_js__ = require("./textEditor.js"), $__textEditor_46_js__ && $__textEditor_46_js__.__esModule && $__textEditor_46_js__ || {default: $__textEditor_46_js__}).TextEditor;\n
var HandsontableEditor = TextEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.HandsontableEditor = HandsontableEditor;\n
HandsontableEditor.prototype.createElements = function() {\n
  TextEditor.prototype.createElements.apply(this, arguments);\n
  var DIV = document.createElement(\'DIV\');\n
  DIV.className = \'handsontableEditor\';\n
  this.TEXTAREA_PARENT.appendChild(DIV);\n
  this.htContainer = DIV;\n
  this.htEditor = new Handsontable(DIV);\n
  this.assignHooks();\n
};\n
HandsontableEditor.prototype.prepare = function(td, row, col, prop, value, cellProperties) {\n
  TextEditor.prototype.prepare.apply(this, arguments);\n
  var parent = this;\n
  var options = {\n
    startRows: 0,\n
    startCols: 0,\n
    minRows: 0,\n
    minCols: 0,\n
    className: \'listbox\',\n
    copyPaste: false,\n
    cells: function() {\n
      return {readOnly: true};\n
    },\n
    fillHandle: false,\n
    afterOnCellMouseDown: function() {\n
      var value = this.getValue();\n
      if (value !== void 0) {\n
        parent.setValue(value);\n
      }\n
      parent.instance.destroyEditor();\n
    }\n
  };\n
  if (this.cellProperties.handsontable) {\n
    helper.extend(options, cellProperties.handsontable);\n
  }\n
  if (this.htEditor) {\n
    this.htEditor.destroy();\n
  }\n
  this.htEditor = new Handsontable(this.htContainer, options);\n
};\n
var onBeforeKeyDown = function(event) {\n
  if (event != null && event.isImmediatePropagationEnabled == null) {\n
    event.stopImmediatePropagation = function() {\n
      this.isImmediatePropagationEnabled = false;\n
      this.cancelBubble = true;\n
    };\n
    event.isImmediatePropagationEnabled = true;\n
    event.isImmediatePropagationStopped = function() {\n
      return !this.isImmediatePropagationEnabled;\n
    };\n
  }\n
  if (event.isImmediatePropagationStopped()) {\n
    return;\n
  }\n
  var editor = this.getActiveEditor();\n
  var innerHOT = editor.htEditor.getInstance();\n
  var rowToSelect;\n
  if (event.keyCode == helper.keyCode.ARROW_DOWN) {\n
    if (!innerHOT.getSelected()) {\n
      rowToSelect = 0;\n
    } else {\n
      var selectedRow = innerHOT.getSelected()[0];\n
      var lastRow = innerHOT.countRows() - 1;\n
      rowToSelect = Math.min(lastRow, selectedRow + 1);\n
    }\n
  } else if (event.keyCode == helper.keyCode.ARROW_UP) {\n
    if (innerHOT.getSelected()) {\n
      var selectedRow = innerHOT.getSelected()[0];\n
      rowToSelect = selectedRow - 1;\n
    }\n
  }\n
  if (rowToSelect !== void 0) {\n
    if (rowToSelect < 0) {\n
      innerHOT.deselectCell();\n
    } else {\n
      innerHOT.selectCell(rowToSelect, 0);\n
    }\n
    event.preventDefault();\n
    event.stopImmediatePropagation();\n
    editor.instance.listen();\n
    editor.TEXTAREA.focus();\n
  }\n
};\n
HandsontableEditor.prototype.open = function() {\n
  this.instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  TextEditor.prototype.open.apply(this, arguments);\n
  this.htEditor.render();\n
  if (this.cellProperties.strict) {\n
    this.htEditor.selectCell(0, 0);\n
    this.TEXTAREA.style.visibility = \'hidden\';\n
  } else {\n
    this.htEditor.deselectCell();\n
    this.TEXTAREA.style.visibility = \'visible\';\n
  }\n
  dom.setCaretPosition(this.TEXTAREA, 0, this.TEXTAREA.value.length);\n
};\n
HandsontableEditor.prototype.close = function() {\n
  this.instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  this.instance.listen();\n
  TextEditor.prototype.close.apply(this, arguments);\n
};\n
HandsontableEditor.prototype.focus = function() {\n
  this.instance.listen();\n
  TextEditor.prototype.focus.apply(this, arguments);\n
};\n
HandsontableEditor.prototype.beginEditing = function(initialValue) {\n
  var onBeginEditing = this.instance.getSettings().onBeginEditing;\n
  if (onBeginEditing && onBeginEditing() === false) {\n
    return;\n
  }\n
  TextEditor.prototype.beginEditing.apply(this, arguments);\n
};\n
HandsontableEditor.prototype.finishEditing = function(isCancelled, ctrlDown) {\n
  if (this.htEditor.isListening()) {\n
    this.instance.listen();\n
  }\n
  if (this.htEditor.getSelected()) {\n
    var value = this.htEditor.getInstance().getValue();\n
    if (value !== void 0) {\n
      this.setValue(value);\n
    }\n
  }\n
  return TextEditor.prototype.finishEditing.apply(this, arguments);\n
};\n
HandsontableEditor.prototype.assignHooks = function() {\n
  var _this = this;\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    if (_this.htEditor) {\n
      _this.htEditor.destroy();\n
    }\n
  });\n
};\n
registerEditor(\'handsontable\', HandsontableEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./../helpers.js":46,"./textEditor.js":44}],40:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  MobileTextEditor: {get: function() {\n
      return MobileTextEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__,\n
    $___46__46__47_dom_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $___95_baseEditor_46_js__,\n
    $___46__46__47_eventManager_46_js__;\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var BaseEditor = ($___95_baseEditor_46_js__ = require("./_baseEditor.js"), $___95_baseEditor_46_js__ && $___95_baseEditor_46_js__.__esModule && $___95_baseEditor_46_js__ || {default: $___95_baseEditor_46_js__}).BaseEditor;\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
var MobileTextEditor = BaseEditor.prototype.extend(),\n
    domDimensionsCache = {};\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.MobileTextEditor = MobileTextEditor;\n
var createControls = function() {\n
  this.controls = {};\n
  this.controls.leftButton = document.createElement(\'DIV\');\n
  this.controls.leftButton.className = \'leftButton\';\n
  this.controls.rightButton = document.createElement(\'DIV\');\n
  this.controls.rightButton.className = \'rightButton\';\n
  this.controls.upButton = document.createElement(\'DIV\');\n
  this.controls.upButton.className = \'upButton\';\n
  this.controls.downButton = document.createElement(\'DIV\');\n
  this.controls.downButton.className = \'downButton\';\n
  for (var button in this.controls) {\n
    if (this.controls.hasOwnProperty(button)) {\n
      this.positionControls.appendChild(this.controls[button]);\n
    }\n
  }\n
};\n
MobileTextEditor.prototype.valueChanged = function() {\n
  return this.initValue != this.getValue();\n
};\n
MobileTextEditor.prototype.init = function() {\n
  var that = this;\n
  this.eventManager = eventManagerObject(this.instance);\n
  this.createElements();\n
  this.bindEvents();\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    that.destroy();\n
  });\n
};\n
MobileTextEditor.prototype.getValue = function() {\n
  return this.TEXTAREA.value;\n
};\n
MobileTextEditor.prototype.setValue = function(newValue) {\n
  this.initValue = newValue;\n
  this.TEXTAREA.value = newValue;\n
};\n
MobileTextEditor.prototype.createElements = function() {\n
  this.editorContainer = document.createElement(\'DIV\');\n
  this.editorContainer.className = "htMobileEditorContainer";\n
  this.cellPointer = document.createElement(\'DIV\');\n
  this.cellPointer.className = "cellPointer";\n
  this.moveHandle = document.createElement(\'DIV\');\n
  this.moveHandle.className = "moveHandle";\n
  this.inputPane = document.createElement(\'DIV\');\n
  this.inputPane.className = "inputs";\n
  this.positionControls = document.createElement(\'DIV\');\n
  this.positionControls.className = "positionControls";\n
  this.TEXTAREA = document.createElement(\'TEXTAREA\');\n
  dom.addClass(this.TEXTAREA, \'handsontableInput\');\n
  this.inputPane.appendChild(this.TEXTAREA);\n
  this.editorContainer.appendChild(this.cellPointer);\n
  this.editorContainer.appendChild(this.moveHandle);\n
  this.editorContainer.appendChild(this.inputPane);\n
  this.editorContainer.appendChild(this.positionControls);\n
  createControls.call(this);\n
  document.body.appendChild(this.editorContainer);\n
};\n
MobileTextEditor.prototype.onBeforeKeyDown = function(event) {\n
  var instance = this;\n
  var that = instance.getActiveEditor();\n
  dom.enableImmediatePropagation(event);\n
  if (event.target !== that.TEXTAREA || event.isImmediatePropagationStopped()) {\n
    return;\n
  }\n
  var keyCodes = helper.keyCode;\n
  switch (event.keyCode) {\n
    case keyCodes.ENTER:\n
      that.close();\n
      event.preventDefault();\n
      break;\n
    case keyCodes.BACKSPACE:\n
      event.stopImmediatePropagation();\n
      break;\n
  }\n
};\n
MobileTextEditor.prototype.open = function() {\n
  this.instance.addHook(\'beforeKeyDown\', this.onBeforeKeyDown);\n
  dom.addClass(this.editorContainer, \'active\');\n
  dom.removeClass(this.cellPointer, \'hidden\');\n
  this.updateEditorPosition();\n
};\n
MobileTextEditor.prototype.focus = function() {\n
  this.TEXTAREA.focus();\n
  dom.setCaretPosition(this.TEXTAREA, this.TEXTAREA.value.length);\n
};\n
MobileTextEditor.prototype.close = function() {\n
  this.TEXTAREA.blur();\n
  this.instance.removeHook(\'beforeKeyDown\', this.onBeforeKeyDown);\n
  dom.removeClass(this.editorContainer, \'active\');\n
};\n
MobileTextEditor.prototype.scrollToView = function() {\n
  var coords = this.instance.getSelectedRange().highlight;\n
  this.instance.view.scrollViewport(coords);\n
};\n
MobileTextEditor.prototype.hideCellPointer = function() {\n
  if (!dom.hasClass(this.cellPointer, \'hidden\')) {\n
    dom.addClass(this.cellPointer, \'hidden\');\n
  }\n
};\n
MobileTextEditor.prototype.updateEditorPosition = function(x, y) {\n
  if (x && y) {\n
    x = parseInt(x, 10);\n
    y = parseInt(y, 10);\n
    this.editorContainer.style.top = y + "px";\n
    this.editorContainer.style.left = x + "px";\n
  } else {\n
    var selection = this.instance.getSelected(),\n
        selectedCell = this.instance.getCell(selection[0], selection[1]);\n
    if (!domDimensionsCache.cellPointer) {\n
      domDimensionsCache.cellPointer = {\n
        height: dom.outerHeight(this.cellPointer),\n
        width: dom.outerWidth(this.cellPointer)\n
      };\n
    }\n
    if (!domDimensionsCache.editorContainer) {\n
      domDimensionsCache.editorContainer = {width: dom.outerWidth(this.editorContainer)};\n
    }\n
    if (selectedCell !== undefined) {\n
      var scrollLeft = this.instance.view.wt.wtOverlays.leftOverlay.trimmingContainer == window ? 0 : dom.getScrollLeft(this.instance.view.wt.wtOverlays.leftOverlay.holder);\n
      var scrollTop = this.instance.view.wt.wtOverlays.topOverlay.trimmingContainer == window ? 0 : dom.getScrollTop(this.instance.view.wt.wtOverlays.topOverlay.holder);\n
      var selectedCellOffset = dom.offset(selectedCell),\n
          selectedCellWidth = dom.outerWidth(selectedCell),\n
          currentScrollPosition = {\n
            x: scrollLeft,\n
            y: scrollTop\n
          };\n
      this.editorContainer.style.top = parseInt(selectedCellOffset.top + dom.outerHeight(selectedCell) - currentScrollPosition.y + domDimensionsCache.cellPointer.height, 10) + "px";\n
      this.editorContainer.style.left = parseInt((window.innerWidth / 2) - (domDimensionsCache.editorContainer.width / 2), 10) + "px";\n
      if (selectedCellOffset.left + selectedCellWidth / 2 > parseInt(this.editorContainer.style.left, 10) + domDimensionsCache.editorContainer.width) {\n
        this.editorContainer.style.left = window.innerWidth - domDimensionsCache.editorContainer.width + "px";\n
      } else if (selectedCellOffset.left + selectedCellWidth / 2 < parseInt(this.editorContainer.style.left, 10) + 20) {\n
        this.editorContainer.style.left = 0 + "px";\n
      }\n
      this.cellPointer.style.left = parseInt(selectedCellOffset.left - (domDimensionsCache.cellPointer.width / 2) - dom.offset(this.editorContainer).left + (selectedCellWidth / 2) - currentScrollPosition.x, 10) + "px";\n
    }\n
  }\n
};\n
MobileTextEditor.prototype.updateEditorData = function() {\n
  var selected = this.instance.getSelected(),\n
      selectedValue = this.instance.getDataAtCell(selected[0], selected[1]);\n
  this.row = selected[0];\n
  this.col = selected[1];\n
  this.setValue(selectedValue);\n
  this.updateEditorPosition();\n
};\n
MobileTextEditor.prototype.prepareAndSave = function() {\n
  var val;\n
  if (!this.valueChanged()) {\n
    return true;\n
  }\n
  if (this.instance.getSettings().trimWhitespace) {\n
    val = [[String.prototype.trim.call(this.getValue())]];\n
  } else {\n
    val = [[this.getValue()]];\n
  }\n
  this.saveValue(val);\n
};\n
MobileTextEditor.prototype.bindEvents = function() {\n
  var that = this;\n
  this.eventManager.addEventListener(this.controls.leftButton, "touchend", function(event) {\n
    that.prepareAndSave();\n
    that.instance.selection.transformStart(0, -1, null, true);\n
    that.updateEditorData();\n
    event.preventDefault();\n
  });\n
  this.eventManager.addEventListener(this.controls.rightButton, "touchend", function(event) {\n
    that.prepareAndSave();\n
    that.instance.selection.transformStart(0, 1, null, true);\n
    that.updateEditorData();\n
    event.preventDefault();\n
  });\n
  this.eventManager.addEventListener(this.controls.upButton, "touchend", function(event) {\n
    that.prepareAndSave();\n
    that.instance.selection.transformStart(-1, 0, null, true);\n
    that.updateEditorData();\n
    event.preventDefault();\n
  });\n
  this.eventManager.addEventListener(this.controls.downButton, "touchend", function(event) {\n
    that.prepareAndSave();\n
    that.instance.selection.transformStart(1, 0, null, true);\n
    that.updateEditorData();\n
    event.preventDefault();\n
  });\n
  this.eventManager.addEventListener(this.moveHandle, "touchstart", function(event) {\n
    if (event.touches.length == 1) {\n
      var touch = event.touches[0],\n
          onTouchPosition = {\n
            x: that.editorContainer.offsetLeft,\n
            y: that.editorContainer.offsetTop\n
          },\n
          onTouchOffset = {\n
            x: touch.pageX - onTouchPosition.x,\n
            y: touch.pageY - onTouchPosition.y\n
          };\n
      that.eventManager.addEventListener(this, "touchmove", function(event) {\n
        var touch = event.touches[0];\n
        that.updateEditorPosition(touch.pageX - onTouchOffset.x, touch.pageY - onTouchOffset.y);\n
        that.hideCellPointer();\n
        event.preventDefault();\n
      });\n
    }\n
  });\n
  this.eventManager.addEventListener(document.body, "touchend", function(event) {\n
    if (!dom.isChildOf(event.target, that.editorContainer) && !dom.isChildOf(event.target, that.instance.rootElement)) {\n
      that.close();\n
    }\n
  });\n
  this.eventManager.addEventListener(this.instance.view.wt.wtOverlays.leftOverlay.holder, "scroll", function(event) {\n
    if (that.instance.view.wt.wtOverlays.leftOverlay.trimmingContainer != window) {\n
      that.hideCellPointer();\n
    }\n
  });\n
  this.eventManager.addEventListener(this.instance.view.wt.wtOverlays.topOverlay.holder, "scroll", function(event) {\n
    if (that.instance.view.wt.wtOverlays.topOverlay.trimmingContainer != window) {\n
      that.hideCellPointer();\n
    }\n
  });\n
};\n
MobileTextEditor.prototype.destroy = function() {\n
  this.eventManager.clear();\n
  this.editorContainer.parentNode.removeChild(this.editorContainer);\n
};\n
registerEditor(\'mobile\', MobileTextEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./../eventManager.js":45,"./../helpers.js":46,"./_baseEditor.js":34}],41:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  NumericEditor: {get: function() {\n
      return NumericEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__numeral__,\n
    $___46__46__47_editors_46_js__,\n
    $__textEditor_46_js__;\n
var numeral = ($__numeral__ = require("numeral"), $__numeral__ && $__numeral__.__esModule && $__numeral__ || {default: $__numeral__}).default;\n
var $__1 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__1.getEditor,\n
    registerEditor = $__1.registerEditor;\n
var TextEditor = ($__textEditor_46_js__ = require("./textEditor.js"), $__textEditor_46_js__ && $__textEditor_46_js__.__esModule && $__textEditor_46_js__ || {default: $__textEditor_46_js__}).TextEditor;\n
var NumericEditor = TextEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.NumericEditor = NumericEditor;\n
NumericEditor.prototype.beginEditing = function(initialValue) {\n
  var BaseEditor = TextEditor.prototype;\n
  if (typeof(initialValue) === \'undefined\' && this.originalValue) {\n
    var value = \'\' + this.originalValue;\n
    if (typeof this.cellProperties.language !== \'undefined\') {\n
      numeral.language(this.cellProperties.language);\n
    }\n
    var decimalDelimiter = numeral.languageData().delimiters.decimal;\n
    value = value.replace(\'.\', decimalDelimiter);\n
    BaseEditor.beginEditing.apply(this, [value]);\n
  } else {\n
    BaseEditor.beginEditing.apply(this, arguments);\n
  }\n
};\n
registerEditor(\'numeric\', NumericEditor);\n
\n
\n
//# \n
},{"./../editors.js":33,"./textEditor.js":44,"numeral":"numeral"}],42:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  PasswordEditor: {get: function() {\n
      return PasswordEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $__textEditor_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var TextEditor = ($__textEditor_46_js__ = require("./textEditor.js"), $__textEditor_46_js__ && $__textEditor_46_js__.__esModule && $__textEditor_46_js__ || {default: $__textEditor_46_js__}).TextEditor;\n
var PasswordEditor = TextEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.PasswordEditor = PasswordEditor;\n
PasswordEditor.prototype.createElements = function() {\n
  TextEditor.prototype.createElements.apply(this, arguments);\n
  this.TEXTAREA = document.createElement(\'input\');\n
  this.TEXTAREA.setAttribute(\'type\', \'password\');\n
  this.TEXTAREA.className = \'handsontableInput\';\n
  this.textareaStyle = this.TEXTAREA.style;\n
  this.textareaStyle.width = 0;\n
  this.textareaStyle.height = 0;\n
  dom.empty(this.TEXTAREA_PARENT);\n
  this.TEXTAREA_PARENT.appendChild(this.TEXTAREA);\n
};\n
registerEditor(\'password\', PasswordEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./textEditor.js":44}],43:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  SelectEditor: {get: function() {\n
      return SelectEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_helpers_46_js__,\n
    $___46__46__47_editors_46_js__,\n
    $___95_baseEditor_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var $__0 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__0.getEditor,\n
    registerEditor = $__0.registerEditor;\n
var BaseEditor = ($___95_baseEditor_46_js__ = require("./_baseEditor.js"), $___95_baseEditor_46_js__ && $___95_baseEditor_46_js__.__esModule && $___95_baseEditor_46_js__ || {default: $___95_baseEditor_46_js__}).BaseEditor;\n
var SelectEditor = BaseEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.SelectEditor = SelectEditor;\n
SelectEditor.prototype.init = function() {\n
  this.select = document.createElement(\'SELECT\');\n
  dom.addClass(this.select, \'htSelectEditor\');\n
  this.select.style.display = \'none\';\n
  this.instance.rootElement.appendChild(this.select);\n
};\n
SelectEditor.prototype.prepare = function() {\n
  BaseEditor.prototype.prepare.apply(this, arguments);\n
  var selectOptions = this.cellProperties.selectOptions;\n
  var options;\n
  if (typeof selectOptions == \'function\') {\n
    options = this.prepareOptions(selectOptions(this.row, this.col, this.prop));\n
  } else {\n
    options = this.prepareOptions(selectOptions);\n
  }\n
  dom.empty(this.select);\n
  for (var option in options) {\n
    if (options.hasOwnProperty(option)) {\n
      var optionElement = document.createElement(\'OPTION\');\n
      optionElement.value = option;\n
      dom.fastInnerHTML(optionElement, options[option]);\n
      this.select.appendChild(optionElement);\n
    }\n
  }\n
};\n
SelectEditor.prototype.prepareOptions = function(optionsToPrepare) {\n
  var preparedOptions = {};\n
  if (Array.isArray(optionsToPrepare)) {\n
    for (var i = 0,\n
        len = optionsToPrepare.length; i < len; i++) {\n
      preparedOptions[optionsToPrepare[i]] = optionsToPrepare[i];\n
    }\n
  } else if (typeof optionsToPrepare == \'object\') {\n
    preparedOptions = optionsToPrepare;\n
  }\n
  return preparedOptions;\n
};\n
SelectEditor.prototype.getValue = function() {\n
  return this.select.value;\n
};\n
SelectEditor.prototype.setValue = function(value) {\n
  this.select.value = value;\n
};\n
var onBeforeKeyDown = function(event) {\n
  var instance = this;\n
  var editor = instance.getActiveEditor();\n
  if (event != null && event.isImmediatePropagationEnabled == null) {\n
    event.stopImmediatePropagation = function() {\n
      this.isImmediatePropagationEnabled = false;\n
    };\n
    event.isImmediatePropagationEnabled = true;\n
    event.isImmediatePropagationStopped = function() {\n
      return !this.isImmediatePropagationEnabled;\n
    };\n
  }\n
  switch (event.keyCode) {\n
    case helper.keyCode.ARROW_UP:\n
      var previousOptionIndex = editor.select.selectedIndex - 1;\n
      if (previousOptionIndex >= 0) {\n
        editor.select[previousOptionIndex].selected = true;\n
      }\n
      event.stopImmediatePropagation();\n
      event.preventDefault();\n
      break;\n
    case helper.keyCode.ARROW_DOWN:\n
      var nextOptionIndex = editor.select.selectedIndex + 1;\n
      if (nextOptionIndex <= editor.select.length - 1) {\n
        editor.select[nextOptionIndex].selected = true;\n
      }\n
      event.stopImmediatePropagation();\n
      event.preventDefault();\n
      break;\n
  }\n
};\n
SelectEditor.prototype.checkEditorSection = function() {\n
  if (this.row < this.instance.getSettings().fixedRowsTop) {\n
    if (this.col < this.instance.getSettings().fixedColumnsLeft) {\n
      return \'corner\';\n
    } else {\n
      return \'top\';\n
    }\n
  } else {\n
    if (this.col < this.instance.getSettings().fixedColumnsLeft) {\n
      return \'left\';\n
    }\n
  }\n
};\n
SelectEditor.prototype.open = function() {\n
  var width = dom.outerWidth(this.TD);\n
  var height = dom.outerHeight(this.TD);\n
  var rootOffset = dom.offset(this.instance.rootElement);\n
  var tdOffset = dom.offset(this.TD);\n
  var editorSection = this.checkEditorSection();\n
  var cssTransformOffset;\n
  switch (editorSection) {\n
    case \'top\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.topOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
    case \'left\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.leftOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
    case \'corner\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.topLeftCornerOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
  }\n
  var selectStyle = this.select.style;\n
  if (cssTransformOffset && cssTransformOffset != -1) {\n
    selectStyle[cssTransformOffset[0]] = cssTransformOffset[1];\n
  } else {\n
    dom.resetCssTransform(this.select);\n
  }\n
  selectStyle.height = height + \'px\';\n
  selectStyle.minWidth = width + \'px\';\n
  selectStyle.top = tdOffset.top - rootOffset.top + \'px\';\n
  selectStyle.left = tdOffset.left - rootOffset.left + \'px\';\n
  selectStyle.margin = \'0px\';\n
  selectStyle.display = \'\';\n
  this.instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
};\n
SelectEditor.prototype.close = function() {\n
  this.select.style.display = \'none\';\n
  this.instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
};\n
SelectEditor.prototype.focus = function() {\n
  this.select.focus();\n
};\n
registerEditor(\'select\', SelectEditor);\n
\n
\n
//# \n
},{"./../dom.js":31,"./../editors.js":33,"./../helpers.js":46,"./_baseEditor.js":34}],44:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  TextEditor: {get: function() {\n
      return TextEditor;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_helpers_46_js__,\n
    $___46__46__47_3rdparty_47_autoResize_46_js__,\n
    $___95_baseEditor_46_js__,\n
    $___46__46__47_eventManager_46_js__,\n
    $___46__46__47_editors_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var autoResize = ($___46__46__47_3rdparty_47_autoResize_46_js__ = require("./../3rdparty/autoResize.js"), $___46__46__47_3rdparty_47_autoResize_46_js__ && $___46__46__47_3rdparty_47_autoResize_46_js__.__esModule && $___46__46__47_3rdparty_47_autoResize_46_js__ || {default: $___46__46__47_3rdparty_47_autoResize_46_js__}).autoResize;\n
var BaseEditor = ($___95_baseEditor_46_js__ = require("./_baseEditor.js"), $___95_baseEditor_46_js__ && $___95_baseEditor_46_js__.__esModule && $___95_baseEditor_46_js__ || {default: $___95_baseEditor_46_js__}).BaseEditor;\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
var $__3 = ($___46__46__47_editors_46_js__ = require("./../editors.js"), $___46__46__47_editors_46_js__ && $___46__46__47_editors_46_js__.__esModule && $___46__46__47_editors_46_js__ || {default: $___46__46__47_editors_46_js__}),\n
    getEditor = $__3.getEditor,\n
    registerEditor = $__3.registerEditor;\n
var TextEditor = BaseEditor.prototype.extend();\n
;\n
Handsontable.editors = Handsontable.editors || {};\n
Handsontable.editors.TextEditor = TextEditor;\n
TextEditor.prototype.init = function() {\n
  var that = this;\n
  this.createElements();\n
  this.eventManager = eventManagerObject(this);\n
  this.bindEvents();\n
  this.autoResize = autoResize();\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    that.destroy();\n
  });\n
};\n
TextEditor.prototype.getValue = function() {\n
  return this.TEXTAREA.value;\n
};\n
TextEditor.prototype.setValue = function(newValue) {\n
  this.TEXTAREA.value = newValue;\n
};\n
var onBeforeKeyDown = function onBeforeKeyDown(event) {\n
  var instance = this,\n
      that = instance.getActiveEditor(),\n
      keyCodes,\n
      ctrlDown;\n
  keyCodes = helper.keyCode;\n
  ctrlDown = (event.ctrlKey || event.metaKey) && !event.altKey;\n
  dom.enableImmediatePropagation(event);\n
  if (event.target !== that.TEXTAREA || event.isImmediatePropagationStopped()) {\n
    return;\n
  }\n
  if (event.keyCode === 17 || event.keyCode === 224 || event.keyCode === 91 || event.keyCode === 93) {\n
    event.stopImmediatePropagation();\n
    return;\n
  }\n
  switch (event.keyCode) {\n
    case keyCodes.ARROW_RIGHT:\n
      if (dom.getCaretPosition(that.TEXTAREA) !== that.TEXTAREA.value.length) {\n
        event.stopImmediatePropagation();\n
      }\n
      break;\n
    case keyCodes.ARROW_LEFT:\n
      if (dom.getCaretPosition(that.TEXTAREA) !== 0) {\n
        event.stopImmediatePropagation();\n
      }\n
      break;\n
    case keyCodes.ENTER:\n
      var selected = that.instance.getSelected();\n
      var isMultipleSelection = !(selected[0] === selected[2] && selected[1] === selected[3]);\n
      if ((ctrlDown && !isMultipleSelection) || event.altKey) {\n
        if (that.isOpened()) {\n
          var caretPosition = dom.getCaretPosition(that.TEXTAREA),\n
              value = that.getValue();\n
          var newValue = value.slice(0, caretPosition) + \'\\n\' + value.slice(caretPosition);\n
          that.setValue(newValue);\n
          dom.setCaretPosition(that.TEXTAREA, caretPosition + 1);\n
        } else {\n
          that.beginEditing(that.originalValue + \'\\n\');\n
        }\n
        event.stopImmediatePropagation();\n
      }\n
      event.preventDefault();\n
      break;\n
    case keyCodes.A:\n
    case keyCodes.X:\n
    case keyCodes.C:\n
    case keyCodes.V:\n
      if (ctrlDown) {\n
        event.stopImmediatePropagation();\n
      }\n
      break;\n
    case keyCodes.BACKSPACE:\n
    case keyCodes.DELETE:\n
    case keyCodes.HOME:\n
    case keyCodes.END:\n
      event.stopImmediatePropagation();\n
      break;\n
  }\n
  that.autoResize.resize(String.fromCharCode(event.keyCode));\n
};\n
TextEditor.prototype.open = function() {\n
  this.refreshDimensions();\n
  this.instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
};\n
TextEditor.prototype.close = function() {\n
  this.textareaParentStyle.display = \'none\';\n
  this.autoResize.unObserve();\n
  if (document.activeElement === this.TEXTAREA) {\n
    this.instance.listen();\n
  }\n
  this.instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
};\n
TextEditor.prototype.focus = function() {\n
  this.TEXTAREA.focus();\n
  dom.setCaretPosition(this.TEXTAREA, this.TEXTAREA.value.length);\n
};\n
TextEditor.prototype.createElements = function() {\n
  this.TEXTAREA = document.createElement(\'TEXTAREA\');\n
  dom.addClass(this.TEXTAREA, \'handsontableInput\');\n
  this.textareaStyle = this.TEXTAREA.style;\n
  this.textareaStyle.width = 0;\n
  this.textareaStyle.height = 0;\n
  this.TEXTAREA_PARENT = document.createElement(\'DIV\');\n
  dom.addClass(this.TEXTAREA_PARENT, \'handsontableInputHolder\');\n
  this.textareaParentStyle = this.TEXTAREA_PARENT.style;\n
  this.textareaParentStyle.top = 0;\n
  this.textareaParentStyle.left = 0;\n
  this.textareaParentStyle.display = \'none\';\n
  this.TEXTAREA_PARENT.appendChild(this.TEXTAREA);\n
  this.instance.rootElement.appendChild(this.TEXTAREA_PARENT);\n
  var that = this;\n
  this.instance._registerTimeout(setTimeout(function() {\n
    that.refreshDimensions();\n
  }, 0));\n
};\n
TextEditor.prototype.checkEditorSection = function() {\n
  if (this.row < this.instance.getSettings().fixedRowsTop) {\n
    if (this.col < this.instance.getSettings().fixedColumnsLeft) {\n
      return \'corner\';\n
    } else {\n
      return \'top\';\n
    }\n
  } else {\n
    if (this.col < this.instance.getSettings().fixedColumnsLeft) {\n
      return \'left\';\n
    }\n
  }\n
};\n
TextEditor.prototype.getEditedCell = function() {\n
  var editorSection = this.checkEditorSection(),\n
      editedCell;\n
  switch (editorSection) {\n
    case \'top\':\n
      editedCell = this.instance.view.wt.wtOverlays.topOverlay.clone.wtTable.getCell({\n
        row: this.row,\n
        col: this.col\n
      });\n
      this.textareaParentStyle.zIndex = 101;\n
      break;\n
    case \'corner\':\n
      editedCell = this.instance.view.wt.wtOverlays.topLeftCornerOverlay.clone.wtTable.getCell({\n
        row: this.row,\n
        col: this.col\n
      });\n
      this.textareaParentStyle.zIndex = 103;\n
      break;\n
    case \'left\':\n
      editedCell = this.instance.view.wt.wtOverlays.leftOverlay.clone.wtTable.getCell({\n
        row: this.row,\n
        col: this.col\n
      });\n
      this.textareaParentStyle.zIndex = 102;\n
      break;\n
    default:\n
      editedCell = this.instance.getCell(this.row, this.col);\n
      this.textareaParentStyle.zIndex = "";\n
      break;\n
  }\n
  return editedCell != -1 && editedCell != -2 ? editedCell : void 0;\n
};\n
TextEditor.prototype.refreshDimensions = function() {\n
  if (this.state !== Handsontable.EditorState.EDITING) {\n
    return;\n
  }\n
  this.TD = this.getEditedCell();\n
  if (!this.TD) {\n
    return;\n
  }\n
  var currentOffset = dom.offset(this.TD),\n
      containerOffset = dom.offset(this.instance.rootElement),\n
      scrollableContainer = dom.getScrollableElement(this.TD),\n
      editTop = currentOffset.top - containerOffset.top - 1 - (scrollableContainer.scrollTop || 0),\n
      editLeft = currentOffset.left - containerOffset.left - 1 - (scrollableContainer.scrollLeft || 0),\n
      settings = this.instance.getSettings(),\n
      rowHeadersCount = settings.rowHeaders ? 1 : 0,\n
      colHeadersCount = settings.colHeaders ? 1 : 0,\n
      editorSection = this.checkEditorSection(),\n
      backgroundColor = this.TD.style.backgroundColor,\n
      cssTransformOffset;\n
  switch (editorSection) {\n
    case \'top\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.topOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
    case \'left\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.leftOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
    case \'corner\':\n
      cssTransformOffset = dom.getCssTransform(this.instance.view.wt.wtOverlays.topLeftCornerOverlay.clone.wtTable.holder.parentNode);\n
      break;\n
  }\n
  if (editTop < 0) {\n
    editTop = 0;\n
  }\n
  if (editLeft < 0) {\n
    editLeft = 0;\n
  }\n
  if (colHeadersCount && this.instance.getSelected()[0] === 0) {\n
    editTop += 1;\n
  }\n
  if (rowHeadersCount && this.instance.getSelected()[1] === 0) {\n
    editLeft += 1;\n
  }\n
  if (cssTransformOffset && cssTransformOffset != -1) {\n
    this.textareaParentStyle[cssTransformOffset[0]] = cssTransformOffset[1];\n
  } else {\n
    dom.resetCssTransform(this.textareaParentStyle);\n
  }\n
  this.textareaParentStyle.top = editTop + \'px\';\n
  this.textareaParentStyle.left = editLeft + \'px\';\n
  var cellTopOffset = this.TD.offsetTop - this.instance.view.wt.wtOverlays.topOverlay.getScrollPosition(),\n
      cellLeftOffset = this.TD.offsetLeft - this.instance.view.wt.wtOverlays.leftOverlay.getScrollPosition();\n
  var width = dom.innerWidth(this.TD) - 8,\n
      maxWidth = this.instance.view.maximumVisibleElementWidth(cellLeftOffset) - 10,\n
      height = this.TD.scrollHeight + 1,\n
      maxHeight = this.instance.view.maximumVisibleElementHeight(cellTopOffset) - 2;\n
  if (parseInt(this.TD.style.borderTopWidth, 10) > 0) {\n
    height -= 1;\n
  }\n
  if (parseInt(this.TD.style.borderLeftWidth, 10) > 0) {\n
    if (rowHeadersCount > 0) {\n
      width -= 1;\n
    }\n
  }\n
  this.TEXTAREA.style.fontSize = dom.getComputedStyle(this.TD).fontSize;\n
  this.TEXTAREA.style.fontFamily = dom.getComputedStyle(this.TD).fontFamily;\n
  this.TEXTAREA.style.backgroundColor = \'\';\n
  this.TEXTAREA.style.backgroundColor = backgroundColor ? backgroundColor : dom.getComputedStyle(this.TEXTAREA).backgroundColor;\n
  this.autoResize.init(this.TEXTAREA, {\n
    minHeight: Math.min(height, maxHeight),\n
    maxHeight: maxHeight,\n
    minWidth: Math.min(width, maxWidth),\n
    maxWidth: maxWidth\n
  }, true);\n
  this.textareaParentStyle.display = \'block\';\n
};\n
TextEditor.prototype.bindEvents = function() {\n
  var editor = this;\n
  this.eventManager.addEventListener(this.TEXTAREA, \'cut\', function(event) {\n
    helper.stopPropagation(event);\n
  });\n
  this.eventManager.addEventListener(this.TEXTAREA, \'paste\', function(event) {\n
    helper.stopPropagation(event);\n
  });\n
  this.instance.addHook(\'afterScrollVertically\', function() {\n
    editor.refreshDimensions();\n
  });\n
  this.instance.addHook(\'afterColumnResize\', function() {\n
    editor.refreshDimensions();\n
    editor.focus();\n
  });\n
  this.instance.addHook(\'afterRowResize\', function() {\n
    editor.refreshDimensions();\n
    editor.focus();\n
  });\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    editor.eventManager.clear();\n
  });\n
};\n
TextEditor.prototype.destroy = function() {\n
  this.eventManager.clear();\n
};\n
registerEditor(\'text\', TextEditor);\n
\n
\n
//# \n
},{"./../3rdparty/autoResize.js":2,"./../dom.js":31,"./../editors.js":33,"./../eventManager.js":45,"./../helpers.js":46,"./_baseEditor.js":34}],45:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  EventManager: {get: function() {\n
      return EventManager;\n
    }},\n
  eventManager: {get: function() {\n
      return eventManager;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__dom_46_js__;\n
var dom = ($__dom_46_js__ = require("./dom.js"), $__dom_46_js__ && $__dom_46_js__.__esModule && $__dom_46_js__ || {default: $__dom_46_js__});\n
var EventManager = function EventManager() {\n
  var context = arguments[0] !== (void 0) ? arguments[0] : null;\n
  this.context = context || this;\n
  if (!this.context.eventListeners) {\n
    this.context.eventListeners = [];\n
  }\n
};\n
($traceurRuntime.createClass)(EventManager, {\n
  addEventListener: function(element, eventName, callback) {\n
    var $__0 = this;\n
    var context = this.context;\n
    function callbackProxy(event) {\n
      if (event.target == void 0 && event.srcElement != void 0) {\n
        if (event.definePoperty) {\n
          event.definePoperty(\'target\', {value: event.srcElement});\n
        } else {\n
          event.target = event.srcElement;\n
        }\n
      }\n
      if (event.preventDefault == void 0) {\n
        if (event.definePoperty) {\n
          event.definePoperty(\'preventDefault\', {value: function() {\n
              this.returnValue = false;\n
            }});\n
        } else {\n
          event.preventDefault = function() {\n
            this.returnValue = false;\n
          };\n
        }\n
      }\n
      event = extendEvent(context, event);\n
      callback.call(this, event);\n
    }\n
    this.context.eventListeners.push({\n
      element: element,\n
      event: eventName,\n
      callback: callback,\n
      callbackProxy: callbackProxy\n
    });\n
    if (window.addEventListener) {\n
      element.addEventListener(eventName, callbackProxy, false);\n
    } else {\n
      element.attachEvent(\'on\' + eventName, callbackProxy);\n
    }\n
    Handsontable.countEventManagerListeners++;\n
    return (function() {\n
      $__0.removeEventListener(element, eventName, callback);\n
    });\n
  },\n
  removeEventListener: function(element, eventName, callback) {\n
    var len = this.context.eventListeners.length;\n
    var tmpEvent;\n
    while (len--) {\n
      tmpEvent = this.context.eventListeners[len];\n
      if (tmpEvent.event == eventName && tmpEvent.element == element) {\n
        if (callback && callback != tmpEvent.callback) {\n
          continue;\n
        }\n
        this.context.eventListeners.splice(len, 1);\n
        if (tmpEvent.element.removeEventListener) {\n
          tmpEvent.element.removeEventListener(tmpEvent.event, tmpEvent.callbackProxy, false);\n
        } else {\n
          tmpEvent.element.detachEvent(\'on\' + tmpEvent.event, tmpEvent.callbackProxy);\n
        }\n
        Handsontable.countEventManagerListeners--;\n
      }\n
    }\n
  },\n
  clearEvents: function() {\n
    var len = this.context.eventListeners.length;\n
    while (len--) {\n
      var event = this.context.eventListeners[len];\n
      if (event) {\n
        this.removeEventListener(event.element, event.event, event.callback);\n
      }\n
    }\n
  },\n
  clear: function() {\n
    this.clearEvents();\n
  },\n
  fireEvent: function(element, eventName) {\n
    var options = {\n
      bubbles: true,\n
      cancelable: (eventName !== \'mousemove\'),\n
      view: window,\n
      detail: 0,\n
      screenX: 0,\n
      screenY: 0,\n
      clientX: 1,\n
      clientY: 1,\n
      ctrlKey: false,\n
      altKey: false,\n
      shiftKey: false,\n
      metaKey: false,\n
      button: 0,\n
      relatedTarget: undefined\n
    };\n
    var event;\n
    if (document.createEvent) {\n
      event = document.createEvent(\'MouseEvents\');\n
      event.initMouseEvent(eventName, options.bubbles, options.cancelable, options.view, options.detail, options.screenX, options.screenY, options.clientX, options.clientY, options.ctrlKey, options.altKey, options.shiftKey, options.metaKey, options.button, options.relatedTarget || document.body.parentNode);\n
    } else {\n
      event = document.createEventObject();\n
    }\n
    if (element.dispatchEvent) {\n
      element.dispatchEvent(event);\n
    } else {\n
      element.fireEvent(\'on\' + eventName, event);\n
    }\n
  }\n
}, {});\n
function extendEvent(context, event) {\n
  var componentName = \'HOT-TABLE\';\n
  var isHotTableSpotted;\n
  var fromElement;\n
  var realTarget;\n
  var target;\n
  var len;\n
  event.isTargetWebComponent = false;\n
  event.realTarget = event.target;\n
  if (!Handsontable.eventManager.isHotTableEnv) {\n
    return event;\n
  }\n
  event = dom.polymerWrap(event);\n
  len = event.path.length;\n
  while (len--) {\n
    if (event.path[len].nodeName === componentName) {\n
      isHotTableSpotted = true;\n
    } else if (isHotTableSpotted && event.path[len].shadowRoot) {\n
      target = event.path[len];\n
      break;\n
    }\n
    if (len === 0 && !target) {\n
      target = event.path[len];\n
    }\n
  }\n
  if (!target) {\n
    target = event.target;\n
  }\n
  event.isTargetWebComponent = true;\n
  if (dom.isWebComponentSupportedNatively()) {\n
    event.realTarget = event.srcElement || event.toElement;\n
  } else if (context instanceof Handsontable.Core || context instanceof Walkontable) {\n
    if (context instanceof Handsontable.Core) {\n
      fromElement = context.view.wt.wtTable.TABLE;\n
    } else if (context instanceof Walkontable) {\n
      fromElement = context.wtTable.TABLE.parentNode.parentNode;\n
    }\n
    realTarget = dom.closest(event.target, [componentName], fromElement);\n
    if (realTarget) {\n
      event.realTarget = fromElement.querySelector(componentName) || event.target;\n
    } else {\n
      event.realTarget = event.target;\n
    }\n
  }\n
  Object.defineProperty(event, \'target\', {\n
    get: function() {\n
      return dom.polymerWrap(target);\n
    },\n
    enumerable: true,\n
    configurable: true\n
  });\n
  return event;\n
}\n
;\n
window.Handsontable = window.Handsontable || {};\n
Handsontable.countEventManagerListeners = 0;\n
Handsontable.eventManager = eventManager;\n
function eventManager(context) {\n
  return new EventManager(context);\n
}\n
\n
\n
//# \n
},{"./dom.js":31}],46:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  isPrintableChar: {get: function() {\n
      return isPrintableChar;\n
    }},\n
  isMetaKey: {get: function() {\n
      return isMetaKey;\n
    }},\n
  isCtrlKey: {get: function() {\n
      return isCtrlKey;\n
    }},\n
  stringify: {get: function() {\n
      return stringify;\n
    }},\n
  toUpperCaseFirst: {get: function() {\n
      return toUpperCaseFirst;\n
    }},\n
  duckSchema: {get: function() {\n
      return duckSchema;\n
    }},\n
  spreadsheetColumnLabel: {get: function() {\n
      return spreadsheetColumnLabel;\n
    }},\n
  createSpreadsheetData: {get: function() {\n
      return createSpreadsheetData;\n
    }},\n
  createSpreadsheetObjectData: {get: function() {\n
      return createSpreadsheetObjectData;\n
    }},\n
  isNumeric: {get: function() {\n
      return isNumeric;\n
    }},\n
  randomString: {get: function() {\n
      return randomString;\n
    }},\n
  inherit: {get: function() {\n
      return inherit;\n
    }},\n
  extend: {get: function() {\n
      return extend;\n
    }},\n
  deepExtend: {get: function() {\n
      return deepExtend;\n
    }},\n
  deepClone: {get: function() {\n
      return deepClone;\n
    }},\n
  isObjectEquals: {get: function() {\n
      return isObjectEquals;\n
    }},\n
  getPrototypeOf: {get: function() {\n
      return getPrototypeOf;\n
    }},\n
  columnFactory: {get: function() {\n
      return columnFactory;\n
    }},\n
  translateRowsToColumns: {get: function() {\n
      return translateRowsToColumns;\n
    }},\n
  to2dArray: {get: function() {\n
      return to2dArray;\n
    }},\n
  extendArray: {get: function() {\n
      return extendArray;\n
    }},\n
  isInput: {get: function() {\n
      return isInput;\n
    }},\n
  isOutsideInput: {get: function() {\n
      return isOutsideInput;\n
    }},\n
  keyCode: {get: function() {\n
      return keyCode;\n
    }},\n
  isObject: {get: function() {\n
      return isObject;\n
    }},\n
  pivot: {get: function() {\n
      return pivot;\n
    }},\n
  proxy: {get: function() {\n
      return proxy;\n
    }},\n
  cellMethodLookupFactory: {get: function() {\n
      return cellMethodLookupFactory;\n
    }},\n
  isMobileBrowser: {get: function() {\n
      return isMobileBrowser;\n
    }},\n
  isTouchSupported: {get: function() {\n
      return isTouchSupported;\n
    }},\n
  stopPropagation: {get: function() {\n
      return stopPropagation;\n
    }},\n
  pageX: {get: function() {\n
      return pageX;\n
    }},\n
  pageY: {get: function() {\n
      return pageY;\n
    }},\n
  defineGetter: {get: function() {\n
      return defineGetter;\n
    }},\n
  requestAnimationFrame: {get: function() {\n
      return requestAnimationFrame;\n
    }},\n
  cancelAnimationFrame: {get: function() {\n
      return cancelAnimationFrame;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__dom_46_js__;\n
var dom = ($__dom_46_js__ = require("./dom.js"), $__dom_46_js__ && $__dom_46_js__.__esModule && $__dom_46_js__ || {default: $__dom_46_js__});\n
function isPrintableChar(keyCode) {\n
  return ((keyCode == 32) || (keyCode >= 48 && keyCode <= 57) || (keyCode >= 96 && keyCode <= 111) || (keyCode >= 186 && keyCode <= 192) || (keyCode >= 219 && keyCode <= 222) || keyCode >= 226 || (keyCode >= 65 && keyCode <= 90));\n
}\n
function isMetaKey(_keyCode) {\n
  var metaKeys = [keyCode.ARROW_DOWN, keyCode.ARROW_UP, keyCode.ARROW_LEFT, keyCode.ARROW_RIGHT, keyCode.HOME, keyCode.END, keyCode.DELETE, keyCode.BACKSPACE, keyCode.F1, keyCode.F2, keyCode.F3, keyCode.F4, keyCode.F5, keyCode.F6, keyCode.F7, keyCode.F8, keyCode.F9, keyCode.F10, keyCode.F11, keyCode.F12, keyCode.TAB, keyCode.PAGE_DOWN, keyCode.PAGE_UP, keyCode.ENTER, keyCode.ESCAPE, keyCode.SHIFT, keyCode.CAPS_LOCK, keyCode.ALT];\n
  return metaKeys.indexOf(_keyCode) != -1;\n
}\n
function isCtrlKey(_keyCode) {\n
  return [keyCode.CONTROL_LEFT, 224, keyCode.COMMAND_LEFT, keyCode.COMMAND_RIGHT].indexOf(_keyCode) != -1;\n
}\n
function stringify(value) {\n
  switch (typeof value) {\n
    case \'string\':\n
    case \'number\':\n
      return value + \'\';\n
    case \'object\':\n
      if (value === null) {\n
        return \'\';\n
      } else {\n
        return value.toString();\n
      }\n
      break;\n
    case \'undefined\':\n
      return \'\';\n
    default:\n
      return value.toString();\n
  }\n
}\n
function toUpperCaseFirst(string) {\n
  return string[0].toUpperCase() + string.substr(1);\n
}\n
function duckSchema(object) {\n
  var schema;\n
  if (Array.isArray(object)) {\n
    schema = [];\n
  } else {\n
    schema = {};\n
    for (var i in object) {\n
      if (object.hasOwnProperty(i)) {\n
        if (object[i] && typeof object[i] === \'object\' && !Array.isArray(object[i])) {\n
          schema[i] = duckSchema(object[i]);\n
        } else if (Array.isArray(object[i])) {\n
          if (object[i].length && typeof object[i][0] === \'object\' && !Array.isArray(object[i][0])) {\n
            schema[i] = [duckSchema(object[i][0])];\n
          } else {\n
            schema[i] = [];\n
          }\n
        } else {\n
          schema[i] = null;\n
        }\n
      }\n
    }\n
  }\n
  return schema;\n
}\n
function spreadsheetColumnLabel(index) {\n
  var dividend = index + 1;\n
  var columnLabel = \'\';\n
  var modulo;\n
  while (dividend > 0) {\n
    modulo = (dividend - 1) % 26;\n
    columnLabel = String.fromCharCode(65 + modulo) + columnLabel;\n
    dividend = parseInt((dividend - modulo) / 26, 10);\n
  }\n
  return columnLabel;\n
}\n
function createSpreadsheetData(rowCount, colCount) {\n
  rowCount = typeof rowCount === \'number\' ? rowCount : 100;\n
  colCount = typeof colCount === \'number\' ? colCount : 4;\n
  var rows = [],\n
      i,\n
      j;\n
  for (i = 0; i < rowCount; i++) {\n
    var row = [];\n
    for (j = 0; j < colCount; j++) {\n
      row.push(spreadsheetColumnLabel(j) + (i + 1));\n
    }\n
    rows.push(row);\n
  }\n
  return rows;\n
}\n
function createSpreadsheetObjectData(rowCount, colCount) {\n
  rowCount = typeof rowCount === \'number\' ? rowCount : 100;\n
  colCount = typeof colCount === \'number\' ? colCount : 4;\n
  var rows = [],\n
      i,\n
      j;\n
  for (i = 0; i < rowCount; i++) {\n
    var row = {};\n
    for (j = 0; j < colCount; j++) {\n
      row[\'prop\' + j] = spreadsheetColumnLabel(j) + (i + 1);\n
    }\n
    rows.push(row);\n
  }\n
  return rows;\n
}\n
function isNumeric(n) {\n
  var t = typeof n;\n
  return t == \'number\' ? !isNaN(n) && isFinite(n) : t == \'string\' ? !n.length ? false : n.length == 1 ? /\\d/.test(n) : /^\\s*[+-]?\\s*(?:(?:\\d+(?:\\.\\d+)?(?:e[+-]?\\d+)?)|(?:0x[a-f\\d]+))\\s*$/i.test(n) : t == \'object\' ? !!n && typeof n.valueOf() == "number" && !(n instanceof Date) : false;\n
}\n
function randomString() {\n
  function s4() {\n
    return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);\n
  }\n
  return s4() + s4() + s4() + s4();\n
}\n
function inherit(Child, Parent) {\n
  Parent.prototype.constructor = Parent;\n
  Child.prototype = new Parent();\n
  Child.prototype.constructor = Child;\n
  return Child;\n
}\n
function extend(target, extension) {\n
  for (var i in extension) {\n
    if (extension.hasOwnProperty(i)) {\n
      target[i] = extension[i];\n
    }\n
  }\n
}\n
function deepExtend(target, extension) {\n
  for (var key in extension) {\n
    if (extension.hasOwnProperty(key)) {\n
      if (extension[key] && typeof extension[key] === \'object\') {\n
        if (!target[key]) {\n
          if (Array.isArray(extension[key])) {\n
            target[key] = [];\n
          } else {\n
            target[key] = {};\n
          }\n
        }\n
        deepExtend(target[key], extension[key]);\n
      } else {\n
        target[key] = extension[key];\n
      }\n
    }\n
  }\n
}\n
function deepClone(obj) {\n
  if (typeof obj === "object") {\n
    return JSON.parse(JSON.stringify(obj));\n
  } else {\n
    return obj;\n
  }\n
}\n
function isObjectEquals(object1, object2) {\n
  return JSON.stringify(object1) === JSON.stringify(object2);\n
}\n
function getPrototypeOf(obj) {\n
  var prototype;\n
  if (typeof obj.__proto__ == "object") {\n
    prototype = obj.__proto__;\n
  } else {\n
    var oldConstructor,\n
        constructor = obj.constructor;\n
    if (typeof obj.constructor == "function") {\n
      oldConstructor = constructor;\n
      if (delete obj.constructor) {\n
        constructor = obj.constructor;\n
        obj.constructor = oldConstructor;\n
      }\n
    }\n
    prototype = constructor ? constructor.prototype : null;\n
  }\n
  return prototype;\n
}\n
function columnFactory(GridSettings, conflictList) {\n
  function ColumnSettings() {}\n
  inherit(ColumnSettings, GridSettings);\n
  for (var i = 0,\n
      len = conflictList.length; i < len; i++) {\n
    ColumnSettings.prototype[conflictList[i]] = void 0;\n
  }\n
  return ColumnSettings;\n
}\n
function translateRowsToColumns(input) {\n
  var i,\n
      ilen,\n
      j,\n
      jlen,\n
      output = [],\n
      olen = 0;\n
  for (i = 0, ilen = input.length; i < ilen; i++) {\n
    for (j = 0, jlen = input[i].length; j < jlen; j++) {\n
      if (j == olen) {\n
        output.push([]);\n
        olen++;\n
      }\n
      output[j].push(input[i][j]);\n
    }\n
  }\n
  return output;\n
}\n
function to2dArray(arr) {\n
  var i = 0,\n
      ilen = arr.length;\n
  while (i < ilen) {\n
    arr[i] = [arr[i]];\n
    i++;\n
  }\n
}\n
function extendArray(arr, extension) {\n
  var i = 0,\n
      ilen = extension.length;\n
  while (i < ilen) {\n
    arr.push(extension[i]);\n
    i++;\n
  }\n
}\n
function isInput(element) {\n
  var inputs = [\'INPUT\', \'SELECT\', \'TEXTAREA\'];\n
  return inputs.indexOf(element.nodeName) > -1;\n
}\n
function isOutsideInput(element) {\n
  return isInput(element) && element.className.indexOf(\'handsontableInput\') == -1;\n
}\n
var keyCode = {\n
  MOUSE_LEFT: 1,\n
  MOUSE_RIGHT: 3,\n
  MOUSE_MIDDLE: 2,\n
  BACKSPACE: 8,\n
  COMMA: 188,\n
  INSERT: 45,\n
  DELETE: 46,\n
  END: 35,\n
  ENTER: 13,\n
  ESCAPE: 27,\n
  CONTROL_LEFT: 91,\n
  COMMAND_LEFT: 17,\n
  COMMAND_RIGHT: 93,\n
  ALT: 18,\n
  HOME: 36,\n
  PAGE_DOWN: 34,\n
  PAGE_UP: 33,\n
  PERIOD: 190,\n
  SPACE: 32,\n
  SHIFT: 16,\n
  CAPS_LOCK: 20,\n
  TAB: 9,\n
  ARROW_RIGHT: 39,\n
  ARROW_LEFT: 37,\n
  ARROW_UP: 38,\n
  ARROW_DOWN: 40,\n
  F1: 112,\n
  F2: 113,\n
  F3: 114,\n
  F4: 115,\n
  F5: 116,\n
  F6: 117,\n
  F7: 118,\n
  F8: 119,\n
  F9: 120,\n
  F10: 121,\n
  F11: 122,\n
  F12: 123,\n
  A: 65,\n
  X: 88,\n
  C: 67,\n
  V: 86\n
};\n
function isObject(obj) {\n
  return Object.prototype.toString.call(obj) == \'[object Object]\';\n
}\n
function pivot(arr) {\n
  var pivotedArr = [];\n
  if (!arr || arr.length === 0 || !arr[0] || arr[0].length === 0) {\n
    return pivotedArr;\n
  }\n
  var rowCount = arr.length;\n
  var colCount = arr[0].length;\n
  for (var i = 0; i < rowCount; i++) {\n
    for (var j = 0; j < colCount; j++) {\n
      if (!pivotedArr[j]) {\n
        pivotedArr[j] = [];\n
      }\n
      pivotedArr[j][i] = arr[i][j];\n
    }\n
  }\n
  return pivotedArr;\n
}\n
function proxy(fun, context) {\n
  return function() {\n
    return fun.apply(context, arguments);\n
  };\n
}\n
function cellMethodLookupFactory(methodName, allowUndefined) {\n
  allowUndefined = typeof allowUndefined == \'undefined\' ? true : allowUndefined;\n
  return function cellMethodLookup(row, col) {\n
    return (function getMethodFromProperties(properties) {\n
      if (!properties) {\n
        return;\n
      } else if (properties.hasOwnProperty(methodName) && properties[methodName] !== void 0) {\n
        return properties[methodName];\n
      } else if (properties.hasOwnProperty(\'type\') && properties.type) {\n
        var type;\n
        if (typeof properties.type != \'string\') {\n
          throw new Error(\'Cell type must be a string \');\n
        }\n
        type = translateTypeNameToObject(properties.type);\n
        if (type.hasOwnProperty(methodName)) {\n
          return type[methodName];\n
        } else if (allowUndefined) {\n
          return;\n
        }\n
      }\n
      return getMethodFromProperties(getPrototypeOf(properties));\n
    })(typeof row == \'number\' ? this.getCellMeta(row, col) : row);\n
  };\n
  function translateTypeNameToObject(typeName) {\n
    var type = Handsontable.cellTypes[typeName];\n
    if (typeof type == \'undefined\') {\n
      throw new Error(\'You declared cell type "\' + typeName + \'" as a string that is not mapped to a known object. \' + \'Cell type must be an object or a string mapped to an object in Handsontable.cellTypes\');\n
    }\n
    return type;\n
  }\n
}\n
function isMobileBrowser(userAgent) {\n
  if (!userAgent) {\n
    userAgent = navigator.userAgent;\n
  }\n
  return (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent));\n
}\n
function isTouchSupported() {\n
  return (\'ontouchstart\' in window);\n
}\n
function stopPropagation(event) {\n
  if (typeof(event.stopPropagation) === \'function\') {\n
    event.stopPropagation();\n
  } else {\n
    event.cancelBubble = true;\n
  }\n
}\n
function pageX(event) {\n
  if (event.pageX) {\n
    return event.pageX;\n
  }\n
  var scrollLeft = dom.getWindowScrollLeft();\n
  var cursorX = event.clientX + scrollLeft;\n
  return cursorX;\n
}\n
function pageY(event) {\n
  if (event.pageY) {\n
    return event.pageY;\n
  }\n
  var scrollTop = dom.getWindowScrollTop();\n
  var cursorY = event.clientY + scrollTop;\n
  return cursorY;\n
}\n
function defineGetter(object, property, value, options) {\n
  options.value = value;\n
  options.writable = options.writable === false ? false : true;\n
  options.enumerable = options.enumerable === false ? false : true;\n
  options.configurable = options.configurable === false ? false : true;\n
  Object.defineProperty(object, property, options);\n
}\n
var lastTime = 0;\n
var vendors = [\'ms\', \'moz\', \'webkit\', \'o\'];\n
var _requestAnimationFrame = window.requestAnimationFrame;\n
var _cancelAnimationFrame = window.cancelAnimationFrame;\n
for (var x = 0; x < vendors.length && !_requestAnimationFrame; ++x) {\n
  _requestAnimationFrame = window[vendors[x] + \'RequestAnimationFrame\'];\n
  _cancelAnimationFrame = window[vendors[x] + \'CancelAnimationFrame\'] || window[vendors[x] + \'CancelRequestAnimationFrame\'];\n
}\n
if (!_requestAnimationFrame) {\n
  _requestAnimationFrame = function(callback) {\n
    var currTime = new Date().getTime();\n
    var timeToCall = Math.max(0, 16 - (currTime - lastTime));\n
    var id = window.setTimeout(function() {\n
      callback(currTime + timeToCall);\n
    }, timeToCall);\n
    lastTime = currTime + timeToCall;\n
    return id;\n
  };\n
}\n
if (!_cancelAnimationFrame) {\n
  _cancelAnimationFrame = function(id) {\n
    clearTimeout(id);\n
  };\n
}\n
function requestAnimationFrame(callback) {\n
  return _requestAnimationFrame.call(window, callback);\n
}\n
function cancelAnimationFrame(id) {\n
  _cancelAnimationFrame.call(window, id);\n
}\n
window.Handsontable = window.Handsontable || {};\n
Handsontable.helper = {\n
  cancelAnimationFrame: cancelAnimationFrame,\n
  cellMethodLookupFactory: cellMethodLookupFactory,\n
  columnFactory: columnFactory,\n
  createSpreadsheetData: createSpreadsheetData,\n
  createSpreadsheetObjectData: createSpreadsheetObjectData,\n
  duckSchema: duckSchema,\n
  deepClone: deepClone,\n
  deepExtend: deepExtend,\n
  defineGetter: defineGetter,\n
  extend: extend,\n
  extendArray: extendArray,\n
  getPrototypeOf: getPrototypeOf,\n
  inherit: inherit,\n
  isCtrlKey: isCtrlKey,\n
  isInput: isInput,\n
  isMetaKey: isMetaKey,\n
  isMobileBrowser: isMobileBrowser,\n
  isNumeric: isNumeric,\n
  isObject: isObject,\n
  isObjectEquals: isObjectEquals,\n
  isOutsideInput: isOutsideInput,\n
  isPrintableChar: isPrintableChar,\n
  isTouchSupported: isTouchSupported,\n
  keyCode: keyCode,\n
  pageX: pageX,\n
  pageY: pageY,\n
  pivot: pivot,\n
  proxy: proxy,\n
  randomString: randomString,\n
  requestAnimationFrame: requestAnimationFrame,\n
  spreadsheetColumnLabel: spreadsheetColumnLabel,\n
  stopPropagation: stopPropagation,\n
  stringify: stringify,\n
  to2dArray: to2dArray,\n
  toUpperCaseFirst: toUpperCaseFirst,\n
  translateRowsToColumns: translateRowsToColumns\n
};\n
\n
\n
//# \n
},{"./dom.js":31}],47:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  MultiMap: {get: function() {\n
      return MultiMap;\n
    }},\n
  __esModule: {value: true}\n
});\n
;\n
window.MultiMap = MultiMap;\n
function MultiMap() {\n
  var map = {\n
    arrayMap: [],\n
    weakMap: new WeakMap()\n
  };\n
  return {\n
    \'get\': function(key) {\n
      if (canBeAnArrayMapKey(key)) {\n
        return map.arrayMap[key];\n
      } else if (canBeAWeakMapKey(key)) {\n
        return map.weakMap.get(key);\n
      }\n
    },\n
    \'set\': function(key, value) {\n
      if (canBeAnArrayMapKey(key)) {\n
        map.arrayMap[key] = value;\n
      } else if (canBeAWeakMapKey(key)) {\n
        map.weakMap.set(key, value);\n
      } else {\n
        throw new Error(\'Invalid key type\');\n
      }\n
    },\n
    \'delete\': function(key) {\n
      if (canBeAnArrayMapKey(key)) {\n
        delete map.arrayMap[key];\n
      } else if (canBeAWeakMapKey(key)) {\n
        map.weakMap[\'delete\'](key);\n
      }\n
    }\n
  };\n
  function canBeAnArrayMapKey(obj) {\n
    return obj !== null && !isNaNSymbol(obj) && (typeof obj == \'string\' || typeof obj == \'number\');\n
  }\n
  function canBeAWeakMapKey(obj) {\n
    return obj !== null && (typeof obj == \'object\' || typeof obj == \'function\');\n
  }\n
  function isNaNSymbol(obj) {\n
    return obj !== obj;\n
  }\n
}\n
\n
\n
//# \n
},{}],48:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  PluginHook: {get: function() {\n
      return PluginHook;\n
    }},\n
  __esModule: {value: true}\n
});\n
var PluginHook = function PluginHook() {\n
  this.hooks = {\n
    beforeInitWalkontable: [],\n
    beforeInit: [],\n
    beforeRender: [],\n
    beforeSetRangeEnd: [],\n
    beforeDrawBorders: [],\n
    beforeChange: [],\n
    beforeChangeRender: [],\n
    beforeRemoveCol: [],\n
    beforeRemoveRow: [],\n
    beforeValidate: [],\n
    beforeGetCellMeta: [],\n
    beforeAutofill: [],\n
    beforeKeyDown: [],\n
    beforeOnCellMouseDown: [],\n
    beforeTouchScroll: [],\n
    afterInit: [],\n
    afterLoadData: [],\n
    afterUpdateSettings: [],\n
    afterRender: [],\n
    afterRenderer: [],\n
    afterChange: [],\n
    afterValidate: [],\n
    afterGetCellMeta: [],\n
    afterSetCellMeta: [],\n
    afterGetColHeader: [],\n
    afterGetRowHeader: [],\n
    afterDestroy: [],\n
    afterRemoveRow: [],\n
    afterCreateRow: [],\n
    afterRemoveCol: [],\n
    afterCreateCol: [],\n
    afterDeselect: [],\n
    afterSelection: [],\n
    afterSelectionByProp: [],\n
    afterSelectionEnd: [],\n
    afterSelectionEndByProp: [],\n
    afterOnCellMouseDown: [],\n
    afterOnCellMouseOver: [],\n
    afterOnCellCornerMouseDown: [],\n
    afterScrollVertically: [],\n
    afterScrollHorizontally: [],\n
    afterCellMetaReset: [],\n
    afterIsMultipleSelectionCheck: [],\n
    afterDocumentKeyDown: [],\n
    afterMomentumScroll: [],\n
    beforeCellAlignment: [],\n
    modifyColWidth: [],\n
    modifyRowHeight: [],\n
    modifyRow: [],\n
    modifyCol: []\n
  };\n
  this.globalBucket = {};\n
};\n
($traceurRuntime.createClass)(PluginHook, {\n
  getBucket: function() {\n
    var context = arguments[0] !== (void 0) ? arguments[0] : null;\n
    if (context) {\n
      if (!context.pluginHookBucket) {\n
        context.pluginHookBucket = {};\n
      }\n
      return context.pluginHookBucket;\n
    }\n
    return this.globalBucket;\n
  },\n
  add: function(key, callback) {\n
    var context = arguments[2] !== (void 0) ? arguments[2] : null;\n
    if (Array.isArray(callback)) {\n
      for (var i = 0,\n
          len = callback.length; i < len; i++) {\n
        this.add(key, callback[i]);\n
      }\n
    } else {\n
      var bucket = this.getBucket(context);\n
      if (typeof bucket[key] === \'undefined\') {\n
        bucket[key] = [];\n
      }\n
      callback.skip = false;\n
      if (bucket[key].indexOf(callback) === -1) {\n
        bucket[key].push(callback);\n
      }\n
    }\n
    return this;\n
  },\n
  once: function(key, callback) {\n
    var context = arguments[2] !== (void 0) ? arguments[2] : null;\n
    if (Array.isArray(callback)) {\n
      for (var i = 0,\n
          len = callback.length; i < len; i++) {\n
        callback[i].runOnce = true;\n
        this.add(key, callback[i], context);\n
      }\n
    } else {\n
      callback.runOnce = true;\n
      this.add(key, callback, context);\n
    }\n
  },\n
  remove: function(key, callback) {\n
    var context = arguments[2] !== (void 0) ? arguments[2] : null;\n
    var status = false;\n
    var bucket = this.getBucket(context);\n
    if (typeof bucket[key] !== \'undefined\') {\n
      for (var i = 0,\n
          len = bucket[key].length; i < len; i++) {\n
        if (bucket[key][i] === callback) {\n
          bucket[key][i].skip = true;\n
          status = true;\n
          break;\n
        }\n
      }\n
    }\n
    return status;\n
  },\n
  run: function(context, key, p1, p2, p3, p4, p5, p6) {\n
    p1 = this._runBucket(this.globalBucket, context, key, p1, p2, p3, p4, p5, p6);\n
    p1 = this._runBucket(this.getBucket(context), context, key, p1, p2, p3, p4, p5, p6);\n
    return p1;\n
  },\n
  _runBucket: function(bucket, context, key, p1, p2, p3, p4, p5, p6) {\n
    var handlers = bucket[key];\n
    if (handlers) {\n
      for (var i = 0,\n
          len = handlers.length; i < len; i++) {\n
        if (!handlers[i].skip) {\n
          var res = handlers[i].call(context, p1, p2, p3, p4, p5, p6);\n
          if (res !== void 0) {\n
            p1 = res;\n
          }\n
          if (handlers[i].runOnce) {\n
            this.remove(key, handlers[i], bucket === this.globalBucket ? null : context);\n
          }\n
        }\n
      }\n
    }\n
    return p1;\n
  },\n
  destroy: function() {\n
    var context = arguments[0] !== (void 0) ? arguments[0] : null;\n
    var bucket = this.getBucket(context);\n
    for (var key in bucket) {\n
      if (bucket.hasOwnProperty(key)) {\n
        for (var i = 0,\n
            len = bucket[key].length; i < len; i++) {\n
          this.remove(key, bucket[key], context);\n
        }\n
      }\n
    }\n
  },\n
  register: function(key) {\n
    if (!this.isRegistered(key)) {\n
      this.hooks[key] = [];\n
    }\n
  },\n
  deregister: function(key) {\n
    delete this.hooks[key];\n
  },\n
  isRegistered: function(key) {\n
    return typeof this.hooks[key] !== \'undefined\';\n
  },\n
  getRegistered: function() {\n
    return Object.keys(this.hooks);\n
  }\n
}, {});\n
;\n
\n
\n
//# \n
},{}],49:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  registerPlugin: {get: function() {\n
      return registerPlugin;\n
    }},\n
  getPlugin: {get: function() {\n
      return getPlugin;\n
    }},\n
  __esModule: {value: true}\n
});\n
;\n
var registeredPlugins = new WeakMap();\n
function registerPlugin(pluginName, PluginClass) {\n
  Handsontable.hooks.add(\'beforeInit\', function() {\n
    var holder;\n
    if (!registeredPlugins.has(this)) {\n
      registeredPlugins.set(this, {});\n
    }\n
    holder = registeredPlugins.get(this);\n
    if (!holder[pluginName]) {\n
      holder[pluginName] = new PluginClass(this);\n
    }\n
  });\n
  Handsontable.hooks.add(\'afterDestroy\', function() {\n
    var i,\n
        pluginsHolder;\n
    if (registeredPlugins.has(this)) {\n
      pluginsHolder = registeredPlugins.get(this);\n
      for (i in pluginsHolder) {\n
        if (pluginsHolder.hasOwnProperty(i) && pluginsHolder[i].destroy) {\n
          pluginsHolder[i].destroy();\n
        }\n
      }\n
      registeredPlugins.delete(this);\n
    }\n
  });\n
}\n
function getPlugin(instance, pluginName) {\n
  if (typeof pluginName != \'string\') {\n
    throw Error(\'Only strings can be passed as "plugin" parameter\');\n
  }\n
  if (!registeredPlugins.has(instance) || !registeredPlugins.get(instance)[pluginName]) {\n
    throw Error(\'No plugin registered under name "\' + pluginName + \'"\');\n
  }\n
  return registeredPlugins.get(instance)[pluginName];\n
}\n
\n
\n
//# \n
},{}],50:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  default: {get: function() {\n
      return $__default;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_helpers_46_js__;\n
var defineGetter = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__}).defineGetter;\n
var BasePlugin = function BasePlugin(hotInstance) {\n
  defineGetter(this, \'hot\', hotInstance, {writable: false});\n
};\n
($traceurRuntime.createClass)(BasePlugin, {destroy: function() {\n
    delete this.hot;\n
  }}, {});\n
var $__default = BasePlugin;\n
\n
\n
//# \n
},{"./../helpers.js":46}],51:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  AutoColumnSize: {get: function() {\n
      return AutoColumnSize;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function AutoColumnSize() {\n
  var plugin = this,\n
      sampleCount = 5;\n
  this.beforeInit = function() {\n
    var instance = this;\n
    instance.autoColumnWidths = [];\n
    if (instance.getSettings().autoColumnSize !== false) {\n
      if (!instance.autoColumnSizeTmp) {\n
        instance.autoColumnSizeTmp = {\n
          table: null,\n
          tableStyle: null,\n
          theadTh: null,\n
          tbody: null,\n
          container: null,\n
          containerStyle: null,\n
          determineBeforeNextRender: true\n
        };\n
        instance.addHook(\'beforeRender\', htAutoColumnSize.determineIfChanged);\n
        instance.addHook(\'modifyColWidth\', htAutoColumnSize.modifyColWidth);\n
        instance.addHook(\'afterDestroy\', htAutoColumnSize.afterDestroy);\n
        instance.determineColumnWidth = plugin.determineColumnWidth;\n
      }\n
    } else {\n
      if (instance.autoColumnSizeTmp) {\n
        instance.removeHook(\'beforeRender\', htAutoColumnSize.determineIfChanged);\n
        instance.removeHook(\'modifyColWidth\', htAutoColumnSize.modifyColWidth);\n
        instance.removeHook(\'afterDestroy\', htAutoColumnSize.afterDestroy);\n
        delete instance.determineColumnWidth;\n
        plugin.afterDestroy.call(instance);\n
      }\n
    }\n
  };\n
  this.determineIfChanged = function(force) {\n
    if (force) {\n
      htAutoColumnSize.determineColumnsWidth.apply(this, arguments);\n
    }\n
  };\n
  this.determineColumnWidth = function(col) {\n
    var instance = this,\n
        tmp = instance.autoColumnSizeTmp;\n
    if (!tmp.container) {\n
      createTmpContainer.call(tmp, instance);\n
    }\n
    tmp.container.className = instance.rootElement.className + \' htAutoColumnSize\';\n
    tmp.table.className = instance.table.className;\n
    var rows = instance.countRows();\n
    var samples = {};\n
    for (var r = 0; r < rows; r++) {\n
      var value = instance.getDataAtCell(r, col);\n
      if (!Array.isArray(value)) {\n
        value = helper.stringify(value);\n
      }\n
      var len = value.length;\n
      if (!samples[len]) {\n
        samples[len] = {\n
          needed: sampleCount,\n
          strings: []\n
        };\n
      }\n
      if (samples[len].needed) {\n
        samples[len].strings.push({\n
          value: value,\n
          row: r\n
        });\n
        samples[len].needed--;\n
      }\n
    }\n
    var settings = instance.getSettings();\n
    if (settings.colHeaders) {\n
      instance.view.appendColHeader(col, tmp.theadTh);\n
    }\n
    dom.empty(tmp.tbody);\n
    for (var i in samples) {\n
      if (samples.hasOwnProperty(i)) {\n
        for (var j = 0,\n
            jlen = samples[i].strings.length; j < jlen; j++) {\n
          var row = samples[i].strings[j].row;\n
          var cellProperties = instance.getCellMeta(row, col);\n
          cellProperties.col = col;\n
          cellProperties.row = row;\n
          var renderer = instance.getCellRenderer(cellProperties);\n
          var tr = document.createElement(\'tr\');\n
          var td = document.createElement(\'td\');\n
          renderer(instance, td, row, col, instance.colToProp(col), samples[i].strings[j].value, cellProperties);\n
          r++;\n
          tr.appendChild(td);\n
          tmp.tbody.appendChild(tr);\n
        }\n
      }\n
    }\n
    var parent = instance.rootElement.parentNode;\n
    parent.appendChild(tmp.container);\n
    var width = dom.outerWidth(tmp.table);\n
    parent.removeChild(tmp.container);\n
    return width;\n
  };\n
  this.determineColumnsWidth = function() {\n
    var instance = this;\n
    var settings = this.getSettings();\n
    if (settings.autoColumnSize || !settings.colWidths) {\n
      var cols = this.countCols();\n
      for (var c = 0; c < cols; c++) {\n
        if (!instance._getColWidthFromSettings(c)) {\n
          this.autoColumnWidths[c] = plugin.determineColumnWidth.call(instance, c);\n
        }\n
      }\n
    }\n
  };\n
  this.modifyColWidth = function(width, col) {\n
    if (this.autoColumnWidths[col] && this.autoColumnWidths[col] > width) {\n
      return this.autoColumnWidths[col];\n
    }\n
    return width;\n
  };\n
  this.afterDestroy = function() {\n
    var instance = this;\n
    if (instance.autoColumnSizeTmp && instance.autoColumnSizeTmp.container && instance.autoColumnSizeTmp.container.parentNode) {\n
      instance.autoColumnSizeTmp.container.parentNode.removeChild(instance.autoColumnSizeTmp.container);\n
    }\n
    instance.autoColumnSizeTmp = null;\n
  };\n
  function createTmpContainer(instance) {\n
    var d = document,\n
        tmp = this;\n
    tmp.table = d.createElement(\'table\');\n
    tmp.theadTh = d.createElement(\'th\');\n
    tmp.table.appendChild(d.createElement(\'thead\')).appendChild(d.createElement(\'tr\')).appendChild(tmp.theadTh);\n
    tmp.tableStyle = tmp.table.style;\n
    tmp.tableStyle.tableLayout = \'auto\';\n
    tmp.tableStyle.width = \'auto\';\n
    tmp.tbody = d.createElement(\'tbody\');\n
    tmp.table.appendChild(tmp.tbody);\n
    tmp.container = d.createElement(\'div\');\n
    tmp.container.className = instance.rootElement.className + \' hidden\';\n
    tmp.containerStyle = tmp.container.style;\n
    tmp.container.appendChild(tmp.table);\n
  }\n
}\n
var htAutoColumnSize = new AutoColumnSize();\n
Handsontable.hooks.add(\'beforeInit\', htAutoColumnSize.beforeInit);\n
Handsontable.hooks.add(\'afterUpdateSettings\', htAutoColumnSize.beforeInit);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../helpers.js":46,"./../../plugins.js":49}],52:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  Autofill: {get: function() {\n
      return Autofill;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var WalkontableCellCoords = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
;\n
function getDeltas(start, end, data, direction) {\n
  var rlength = data.length,\n
      clength = data ? data[0].length : 0,\n
      deltas = [],\n
      arr = [],\n
      diffRow,\n
      diffCol,\n
      startValue,\n
      endValue,\n
      delta;\n
  diffRow = end.row - start.row;\n
  diffCol = end.col - start.col;\n
  if ([\'down\', \'up\'].indexOf(direction) !== -1) {\n
    for (var col = 0; col <= diffCol; col++) {\n
      startValue = parseInt(data[0][col], 10);\n
      endValue = parseInt(data[rlength - 1][col], 10);\n
      delta = (direction === \'down\' ? (endValue - startValue) : (startValue - endValue)) / (rlength - 1) || 0;\n
      arr.push(delta);\n
    }\n
    deltas.push(arr);\n
  }\n
  if ([\'right\', \'left\'].indexOf(direction) !== -1) {\n
    for (var row = 0; row <= diffRow; row++) {\n
      startValue = parseInt(data[row][0], 10);\n
      endValue = parseInt(data[row][clength - 1], 10);\n
      delta = (direction === \'right\' ? (endValue - startValue) : (startValue - endValue)) / (clength - 1) || 0;\n
      arr = [];\n
      arr.push(delta);\n
      deltas.push(arr);\n
    }\n
  }\n
  return deltas;\n
}\n
function Autofill(instance) {\n
  var _this = this,\n
      mouseDownOnCellCorner = false,\n
      wtOnCellCornerMouseDown,\n
      wtOnCellMouseOver,\n
      eventManager;\n
  this.instance = instance;\n
  this.addingStarted = false;\n
  eventManager = eventManagerObject(instance);\n
  function mouseUpCallback(event) {\n
    if (!instance.autofill) {\n
      return true;\n
    }\n
    if (instance.autofill.handle && instance.autofill.handle.isDragged) {\n
      if (instance.autofill.handle.isDragged > 1) {\n
        instance.autofill.apply();\n
      }\n
      instance.autofill.handle.isDragged = 0;\n
      mouseDownOnCellCorner = false;\n
    }\n
  }\n
  function mouseMoveCallback(event) {\n
    var tableBottom,\n
        tableRight;\n
    if (!_this.instance.autofill) {\n
      return false;\n
    }\n
    tableBottom = dom.offset(_this.instance.table).top - (window.pageYOffset || document.documentElement.scrollTop) + dom.outerHeight(_this.instance.table);\n
    tableRight = dom.offset(_this.instance.table).left - (window.pageXOffset || document.documentElement.scrollLeft) + dom.outerWidth(_this.instance.table);\n
    if (_this.addingStarted === false && _this.instance.autofill.handle.isDragged > 0 && event.clientY > tableBottom && event.clientX <= tableRight) {\n
      _this.instance.mouseDragOutside = true;\n
      _this.addingStarted = true;\n
    } else {\n
      _this.instance.mouseDragOutside = false;\n
    }\n
    if (_this.instance.mouseDragOutside) {\n
      setTimeout(function() {\n
        _this.addingStarted = false;\n
        _this.instance.alter(\'insert_row\');\n
      }, 200);\n
    }\n
  }\n
  eventManager.addEventListener(document, \'mouseup\', mouseUpCallback);\n
  eventManager.addEventListener(document, \'mousemove\', mouseMoveCallback);\n
  wtOnCellCornerMouseDown = this.instance.view.wt.wtSettings.settings.onCellCornerMouseDown;\n
  this.instance.view.wt.wtSettings.settings.onCellCornerMouseDown = function(event) {\n
    instance.autofill.handle.isDragged = 1;\n
    mouseDownOnCellCorner = true;\n
    wtOnCellCornerMouseDown(event);\n
  };\n
  wtOnCellMouseOver = this.instance.view.wt.wtSettings.settings.onCellMouseOver;\n
  this.instance.view.wt.wtSettings.settings.onCellMouseOver = function(event, coords, TD, wt) {\n
    if (instance.autofill && mouseDownOnCellCorner && !instance.view.isMouseDown() && instance.autofill.handle && instance.autofill.handle.isDragged) {\n
      instance.autofill.handle.isDragged++;\n
      instance.autofill.showBorder(coords);\n
      instance.autofill.checkIfNewRowNeeded();\n
    }\n
    wtOnCellMouseOver(event, coords, TD, wt);\n
  };\n
  this.instance.view.wt.wtSettings.settings.onCellCornerDblClick = function() {\n
    instance.autofill.selectAdjacent();\n
  };\n
}\n
Autofill.prototype.init = function() {\n
  this.handle = {};\n
};\n
Autofill.prototype.disable = function() {\n
  this.handle.disabled = true;\n
};\n
Autofill.prototype.selectAdjacent = function() {\n
  var select,\n
      data,\n
      r,\n
      maxR,\n
      c;\n
  if (this.instance.selection.isMultiple()) {\n
    select = this.instance.view.wt.selections.area.getCorners();\n
  } else {\n
    select = this.instance.view.wt.selections.current.getCorners();\n
  }\n
  data = this.instance.getData();\n
  rows: for (r = select[2] + 1; r < this.instance.countRows(); r++) {\n
    for (c = select[1]; c <= select[3]; c++) {\n
      if (data[r][c]) {\n
        break rows;\n
      }\n
    }\n
    if (!!data[r][select[1] - 1] || !!data[r][select[3] + 1]) {\n
      maxR = r;\n
    }\n
  }\n
  if (maxR) {\n
    this.instance.view.wt.selections.fill.clear();\n
    this.instance.view.wt.selections.fill.add(new WalkontableCellCoords(select[0], select[1]));\n
    this.instance.view.wt.selections.fill.add(new WalkontableCellCoords(maxR, select[3]));\n
    this.apply();\n
  }\n
};\n
Autofill.prototype.apply = function() {\n
  var drag,\n
      select,\n
      start,\n
      end,\n
      _data,\n
      direction,\n
      deltas,\n
      selRange;\n
  this.handle.isDragged = 0;\n
  drag = this.instance.view.wt.selections.fill.getCorners();\n
  if (!drag) {\n
    return;\n
  }\n
  this.instance.view.wt.selections.fill.clear();\n
  if (this.instance.selection.isMultiple()) {\n
    select = this.instance.view.wt.selections.area.getCorners();\n
  } else {\n
    select = this.instance.view.wt.selections.current.getCorners();\n
  }\n
  if (drag[0] === select[0] && drag[1] < select[1]) {\n
    direction = \'left\';\n
    start = new WalkontableCellCoords(drag[0], drag[1]);\n
    end = new WalkontableCellCoords(drag[2], select[1] - 1);\n
  } else if (drag[0] === select[0] && drag[3] > select[3]) {\n
    direction = \'right\';\n
    start = new WalkontableCellCoords(drag[0], select[3] + 1);\n
    end = new WalkontableCellCoords(drag[2], drag[3]);\n
  } else if (drag[0] < select[0] && drag[1] === select[1]) {\n
    direction = \'up\';\n
    start = new WalkontableCellCoords(drag[0], drag[1]);\n
    end = new WalkontableCellCoords(select[0] - 1, drag[3]);\n
  } else if (drag[2] > select[2] && drag[1] === select[1]) {\n
    direction = \'down\';\n
    start = new WalkontableCellCoords(select[2] + 1, drag[1]);\n
    end = new WalkontableCellCoords(drag[2], drag[3]);\n
  }\n
  if (start && start.row > -1 && start.col > -1) {\n
    selRange = {\n
      from: this.instance.getSelectedRange().from,\n
      to: this.instance.getSelectedRange().to\n
    };\n
    _data = this.instance.getData(selRange.from.row, selRange.from.col, selRange.to.row, selRange.to.col);\n
    deltas = getDeltas(start, end, _data, direction);\n
    Handsontable.hooks.run(this.instance, \'beforeAutofill\', start, end, _data);\n
    this.instance.populateFromArray(start.row, start.col, _data, end.row, end.col, \'autofill\', null, direction, deltas);\n
    this.instance.selection.setRangeStart(new WalkontableCellCoords(drag[0], drag[1]));\n
    this.instance.selection.setRangeEnd(new WalkontableCellCoords(drag[2], drag[3]));\n
  } else {\n
    this.instance.selection.refreshBorders();\n
  }\n
};\n
Autofill.prototype.showBorder = function(coords) {\n
  var topLeft = this.instance.getSelectedRange().getTopLeftCorner(),\n
      bottomRight = this.instance.getSelectedRange().getBottomRightCorner();\n
  if (this.instance.getSettings().fillHandle !== \'horizontal\' && (bottomRight.row < coords.row || topLeft.row > coords.row)) {\n
    coords = new WalkontableCellCoords(coords.row, bottomRight.col);\n
  } else if (this.instance.getSettings().fillHandle !== \'vertical\') {\n
    coords = new WalkontableCellCoords(bottomRight.row, coords.col);\n
  } else {\n
    return;\n
  }\n
  this.instance.view.wt.selections.fill.clear();\n
  this.instance.view.wt.selections.fill.add(this.instance.getSelectedRange().from);\n
  this.instance.view.wt.selections.fill.add(this.instance.getSelectedRange().to);\n
  this.instance.view.wt.selections.fill.add(coords);\n
  this.instance.view.render();\n
};\n
Autofill.prototype.checkIfNewRowNeeded = function() {\n
  var fillCorners,\n
      selection,\n
      tableRows = this.instance.countRows(),\n
      that = this;\n
  if (this.instance.view.wt.selections.fill.cellRange && this.addingStarted === false) {\n
    selection = this.instance.getSelected();\n
    fillCorners = this.instance.view.wt.selections.fill.getCorners();\n
    if (selection[2] < tableRows - 1 && fillCorners[2] === tableRows - 1) {\n
      this.addingStarted = true;\n
      this.instance._registerTimeout(setTimeout(function() {\n
        that.instance.alter(\'insert_row\');\n
        that.addingStarted = false;\n
      }, 200));\n
    }\n
  }\n
};\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  var autofill = new Autofill(this);\n
  if (typeof this.getSettings().fillHandle !== \'undefined\') {\n
    if (autofill.handle && this.getSettings().fillHandle === false) {\n
      autofill.disable();\n
    } else if (!autofill.handle && this.getSettings().fillHandle !== false) {\n
      this.autofill = autofill;\n
      this.autofill.init();\n
    }\n
  }\n
});\n
Handsontable.Autofill = Autofill;\n
\n
\n
//# \n
},{"./../../3rdparty/walkontable/src/cell/coords.js":9,"./../../dom.js":31,"./../../eventManager.js":45,"./../../plugins.js":49}],53:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  default: {get: function() {\n
      return $__default;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__95_base_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var BasePlugin = ($___46__46__47__95_base_46_js__ = require("./../_base.js"), $___46__46__47__95_base_46_js__ && $___46__46__47__95_base_46_js__.__esModule && $___46__46__47__95_base_46_js__ || {default: $___46__46__47__95_base_46_js__}).default;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var ColumnSorting = function ColumnSorting(hotInstance) {\n
  var $__3 = this;\n
  $traceurRuntime.superConstructor($ColumnSorting).call(this, hotInstance);\n
  var _this = this;\n
  this.hot.addHook(\'afterInit\', (function() {\n
    return $__3.init.call($__3, \'afterInit\');\n
  }));\n
  this.hot.addHook(\'afterUpdateSettings\', (function() {\n
    return $__3.init.call($__3, \'afterUpdateSettings\');\n
  }));\n
  this.hot.addHook(\'modifyRow\', function() {\n
    return _this.translateRow.apply(_this, arguments);\n
  });\n
  this.hot.addHook(\'afterGetColHeader\', function() {\n
    return _this.getColHeader.apply(_this, arguments);\n
  });\n
  Handsontable.hooks.register(\'beforeColumnSort\');\n
  Handsontable.hooks.register(\'afterColumnSort\');\n
};\n
var $ColumnSorting = ColumnSorting;\n
($traceurRuntime.createClass)(ColumnSorting, {\n
  init: function(source) {\n
    var sortingSettings = this.hot.getSettings().columnSorting,\n
        _this = this;\n
    this.hot.sortingEnabled = !!(sortingSettings);\n
    if (this.hot.sortingEnabled) {\n
      this.hot.sortIndex = [];\n
      var loadedSortingState = this.loadSortingState(),\n
          sortingColumn,\n
          sortingOrder;\n
      if (typeof loadedSortingState != \'undefined\') {\n
        sortingColumn = loadedSortingState.sortColumn;\n
        sortingOrder = loadedSortingState.sortOrder;\n
      } else {\n
        sortingColumn = sortingSettings.column;\n
        sortingOrder = sortingSettings.sortOrder;\n
      }\n
      this.sortByColumn(sortingColumn, sortingOrder);\n
      this.hot.sort = function() {\n
        var args = Array.prototype.slice.call(arguments);\n
        return _this.sortByColumn.apply(_this, args);\n
      };\n
      if (typeof this.hot.getSettings().observeChanges == \'undefined\') {\n
        this.enableObserveChangesPlugin();\n
      }\n
      if (source == \'afterInit\') {\n
        this.bindColumnSortingAfterClick();\n
        this.hot.addHook(\'afterCreateRow\', function() {\n
          _this.afterCreateRow.apply(_this, arguments);\n
        });\n
        this.hot.addHook(\'afterRemoveRow\', function() {\n
          _this.afterRemoveRow.apply(_this, arguments);\n
        });\n
        this.hot.addHook(\'afterLoadData\', function() {\n
          _this.init.apply(_this, arguments);\n
        });\n
      }\n
    } else {\n
      this.hot.sort = void 0;\n
      this.hot.removeHook(\'afterCreateRow\', this.afterCreateRow);\n
      this.hot.removeHook(\'afterRemoveRow\', this.afterRemoveRow);\n
      this.hot.removeHook(\'afterLoadData\', this.init);\n
    }\n
  },\n
  setSortingColumn: function(col, order) {\n
    if (typeof col == \'undefined\') {\n
      this.hot.sortColumn = void 0;\n
      this.hot.sortOrder = void 0;\n
      return;\n
    } else if (this.hot.sortColumn === col && typeof order == \'undefined\') {\n
      if (this.hot.sortOrder === false) {\n
        this.hot.sortOrder = void 0;\n
      } else {\n
        this.hot.sortOrder = !this.hot.sortOrder;\n
      }\n
    } else {\n
      this.hot.sortOrder = typeof order != \'undefined\' ? order : true;\n
    }\n
    this.hot.sortColumn = col;\n
  },\n
  sortByColumn: function(col, order) {\n
    this.setSortingColumn(col, order);\n
    if (typeof this.hot.sortColumn == \'undefined\') {\n
      return;\n
    }\n
    Handsontable.hooks.run(this.hot, \'beforeColumnSort\', this.hot.sortColumn, this.hot.sortOrder);\n
    this.sort();\n
    this.hot.render();\n
    this.saveSortingState();\n
    Handsontable.hooks.run(this.hot, \'afterColumnSort\', this.hot.sortColumn, this.hot.sortOrder);\n
  },\n
  saveSortingState: function() {\n
    var sortingState = {};\n
    if (typeof this.hot.sortColumn != \'undefined\') {\n
      sortingState.sortColumn = this.hot.sortColumn;\n
    }\n
    if (typeof this.hot.sortOrder != \'undefined\') {\n
      sortingState.sortOrder = this.hot.sortOrder;\n
    }\n
    if (sortingState.hasOwnProperty(\'sortColumn\') || sortingState.hasOwnProperty(\'sortOrder\')) {\n
      Handsontable.hooks.run(this.hot, \'persistentStateSave\', \'columnSorting\', sortingState);\n
    }\n
  },\n
  loadSortingState: function() {\n
    var storedState = {};\n
    Handsontable.hooks.run(this.hot, \'persistentStateLoad\', \'columnSorting\', storedState);\n
    return storedState.value;\n
  },\n
  bindColumnSortingAfterClick: function() {\n
    var eventManager = eventManagerObject(this.hot),\n
        _this = this;\n
    eventManager.addEventListener(this.hot.rootElement, \'click\', function(e) {\n
      if (dom.hasClass(e.target, \'columnSorting\')) {\n
        var col = getColumn(e.target);\n
        if (col !== this.lastSortedColumn) {\n
          _this.sortOrderClass = \'ascending\';\n
        } else {\n
          switch (_this.hot.sortOrder) {\n
            case void 0:\n
              _this.sortOrderClass = \'ascending\';\n
              break;\n
            case true:\n
              _this.sortOrderClass = \'descending\';\n
              break;\n
            case false:\n
              _this.sortOrderClass = void 0;\n
          }\n
        }\n
        this.lastSortedColumn = col;\n
        _this.sortByColumn(col);\n
      }\n
    });\n
    function countRowHeaders() {\n
      var THs = _this.hot.view.TBODY.querySelector(\'tr\').querySelectorAll(\'th\');\n
      return THs.length;\n
    }\n
    function getColumn(target) {\n
      var TH = dom.closest(target, \'TH\');\n
      return dom.index(TH) - countRowHeaders();\n
    }\n
  },\n
  enableObserveChangesPlugin: function() {\n
    var _this = this;\n
    this.hot._registerTimeout(setTimeout(function() {\n
      _this.hot.updateSettings({observeChanges: true});\n
    }, 0));\n
  },\n
  defaultSort: function(sortOrder) {\n
    return function(a, b) {\n
      if (typeof a[1] == "string") {\n
        a[1] = a[1].toLowerCase();\n
      }\n
      if (typeof b[1] == "string") {\n
        b[1] = b[1].toLowerCase();\n
      }\n
      if (a[1] === b[1]) {\n
        return 0;\n
      }\n
      if (a[1] === null || a[1] === "") {\n
        return 1;\n
      }\n
      if (b[1] === null || b[1] === "") {\n
        return -1;\n
      }\n
      if (a[1] < b[1]) {\n
        return sortOrder ? -1 : 1;\n
      }\n
      if (a[1] > b[1]) {\n
        return sortOrder ? 1 : -1;\n
      }\n
      return 0;\n
    };\n
  },\n
  dateSort: function(sortOrder) {\n
    return function(a, b) {\n
      if (a[1] === b[1]) {\n
        return 0;\n
      }\n
      if (a[1] === null) {\n
        return 1;\n
      }\n
      if (b[1] === null) {\n
        return -1;\n
      }\n
      var aDate = new Date(a[1]);\n
      var bDate = new Date(b[1]);\n
      if (aDate < bDate) {\n
        return sortOrder ? -1 : 1;\n
      }\n
      if (aDate > bDate) {\n
        return sortOrder ? 1 : -1;\n
      }\n
      return 0;\n
    };\n
  },\n
  sort: function() {\n
    if (typeof this.hot.sortOrder == \'undefined\') {\n
      return;\n
    }\n
    var colMeta,\n
        sortFunction;\n
    this.hot.sortingEnabled = false;\n
    this.hot.sortIndex.length = 0;\n
    var colOffset = this.hot.colOffset();\n
    for (var i = 0,\n
        ilen = this.hot.countRows() - this.hot.getSettings()[\'minSpareRows\']; i < ilen; i++) {\n
      this.hot.sortIndex.push([i, this.hot.getDataAtCell(i, this.hot.sortColumn + colOffset)]);\n
    }\n
    colMeta = this.hot.getCellMeta(0, this.hot.sortColumn);\n
    switch (colMeta.type) {\n
      case \'date\':\n
        sortFunction = this.dateSort;\n
        break;\n
      default:\n
        sortFunction = this.defaultSort;\n
    }\n
    this.hot.sortIndex.sort(sortFunction(this.hot.sortOrder));\n
    for (var i = this.hot.sortIndex.length; i < this.hot.countRows(); i++) {\n
      this.hot.sortIndex.push([i, this.hot.getDataAtCell(i, this.hot.sortColumn + colOffset)]);\n
    }\n
    this.hot.sortingEnabled = true;\n
  },\n
  translateRow: function(row) {\n
    if (this.hot.sortingEnabled && (typeof this.hot.sortOrder !== \'undefined\') && this.hot.sortIndex && this.hot.sortIndex.length && this.hot.sortIndex[row]) {\n
      return this.hot.sortIndex[row][0];\n
    }\n
    return row;\n
  },\n
  untranslateRow: function(row) {\n
    if (this.hot.sortingEnabled && this.hot.sortIndex && this.hot.sortIndex.length) {\n
      for (var i = 0; i < this.hot.sortIndex.length; i++) {\n
        if (this.hot.sortIndex[i][0] == row) {\n
          return i;\n
        }\n
      }\n
    }\n
  },\n
  getColHeader: function(col, TH) {\n
    var headerLink = TH.querySelector(\'.colHeader\');\n
    if (this.hot.getSettings().columnSorting && col >= 0) {\n
      dom.addClass(headerLink, \'columnSorting\');\n
    }\n
    if (col === this.hot.sortColumn) {\n
      if (this.sortOrderClass === \'ascending\') {\n
        dom.addClass(headerLink, \'ascending\');\n
      } else if (this.sortOrderClass === \'descending\') {\n
        dom.addClass(headerLink, \'descending\');\n
      }\n
    }\n
  },\n
  isSorted: function() {\n
    return typeof this.hot.sortColumn != \'undefined\';\n
  },\n
  afterCreateRow: function(index, amount) {\n
    if (!this.isSorted()) {\n
      return;\n
    }\n
    for (var i = 0; i < this.hot.sortIndex.length; i++) {\n
      if (this.hot.sortIndex[i][0] >= index) {\n
        this.hot.sortIndex[i][0] += amount;\n
      }\n
    }\n
    for (var i = 0; i < amount; i++) {\n
      this.hot.sortIndex.splice(index + i, 0, [index + i, this.hot.getData()[index + i][this.hot.sortColumn + this.hot.colOffset()]]);\n
    }\n
    this.saveSortingState();\n
  },\n
  afterRemoveRow: function(index, amount) {\n
    if (!this.isSorted()) {\n
      return;\n
    }\n
    var physicalRemovedIndex = this.translateRow(index);\n
    this.hot.sortIndex.splice(index, amount);\n
    for (var i = 0; i < this.hot.sortIndex.length; i++) {\n
      if (this.hot.sortIndex[i][0] > physicalRemovedIndex) {\n
        this.hot.sortIndex[i][0] -= amount;\n
      }\n
    }\n
    this.saveSortingState();\n
  }\n
}, {}, BasePlugin);\n
var $__default = ColumnSorting;\n
registerPlugin(\'columnSorting\', ColumnSorting);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../plugins.js":49,"./../_base.js":50}],54:[function(require,module,exports){\n
"use strict";\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var WalkontableCellCoords = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
function Comments(instance) {\n
  var eventManager = eventManagerObject(instance),\n
      doSaveComment = function(row, col, comment, instance) {\n
        instance.setCellMeta(row, col, \'comment\', comment);\n
        instance.render();\n
      },\n
      saveComment = function(range, comment, instance) {\n
        doSaveComment(range.from.row, range.from.col, comment, instance);\n
      },\n
      hideCommentTextArea = function() {\n
        var commentBox = createCommentBox();\n
        commentBox.style.display = \'none\';\n
        commentBox.value = \'\';\n
      },\n
      bindMouseEvent = function(range) {\n
        function commentsListener(event) {\n
          eventManager.removeEventListener(document, \'mouseover\');\n
          if (!(event.target.className == \'htCommentTextArea\' || event.target.innerHTML.indexOf(\'Comment\') != -1)) {\n
            var value = document.querySelector(\'.htCommentTextArea\').value;\n
            if (value.trim().length > 1) {\n
              saveComment(range, value, instance);\n
            }\n
            unBindMouseEvent();\n
            hideCommentTextArea();\n
          }\n
        }\n
        eventManager.addEventListener(document, \'mousedown\', helper.proxy(commentsListener));\n
      },\n
      unBindMouseEvent = function() {\n
        eventManager.removeEventListener(document, \'mousedown\');\n
        eventManager.addEventListener(document, \'mousedown\', helper.proxy(commentsMouseOverListener));\n
      },\n
      placeCommentBox = function(range, commentBox) {\n
        var TD = instance.view.wt.wtTable.getCell(range.from),\n
            offset = dom.offset(TD),\n
            lastColWidth = instance.getColWidth(range.from.col);\n
        commentBox.style.position = \'absolute\';\n
        commentBox.style.left = offset.left + lastColWidth + \'px\';\n
        commentBox.style.top = offset.top + \'px\';\n
        commentBox.style.zIndex = 2;\n
        bindMouseEvent(range, commentBox);\n
      },\n
      createCommentBox = function(value) {\n
        var comments = document.querySelector(\'.htComments\');\n
        if (!comments) {\n
          comments = document.createElement(\'DIV\');\n
          var textArea = document.createElement(\'TEXTAREA\');\n
          dom.addClass(textArea, \'htCommentTextArea\');\n
          comments.appendChild(textArea);\n
          dom.addClass(comments, \'htComments\');\n
          document.getElementsByTagName(\'body\')[0].appendChild(comments);\n
        }\n
        value = value || \'\';\n
        document.querySelector(\'.htCommentTextArea\').value = value;\n
        return comments;\n
      },\n
      commentsMouseOverListener = function(event) {\n
        if (event.target.className.indexOf(\'htCommentCell\') != -1) {\n
          unBindMouseEvent();\n
          var coords = instance.view.wt.wtTable.getCoords(event.target);\n
          var range = {from: new WalkontableCellCoords(coords.row, coords.col)};\n
          Handsontable.Comments.showComment(range);\n
        } else if (event.target.className != \'htCommentTextArea\') {\n
          hideCommentTextArea();\n
        }\n
      };\n
  return {\n
    init: function() {\n
      eventManager.addEventListener(document, \'mouseover\', helper.proxy(commentsMouseOverListener));\n
    },\n
    showComment: function(range) {\n
      var meta = instance.getCellMeta(range.from.row, range.from.col),\n
          value = \'\';\n
      if (meta.comment) {\n
        value = meta.comment;\n
      }\n
      var commentBox = createCommentBox(value);\n
      commentBox.style.display = \'block\';\n
      placeCommentBox(range, commentBox);\n
    },\n
    removeComment: function(row, col) {\n
      instance.removeCellMeta(row, col, \'comment\');\n
      instance.render();\n
    },\n
    checkSelectionCommentsConsistency: function() {\n
      var hasComment = false;\n
      var cell = instance.getSelectedRange().from;\n
      if (instance.getCellMeta(cell.row, cell.col).comment) {\n
        hasComment = true;\n
      }\n
      return hasComment;\n
    }\n
  };\n
}\n
var init = function() {\n
  var instance = this;\n
  var commentsSetting = instance.getSettings().comments;\n
  if (commentsSetting) {\n
    Handsontable.Comments = new Comments(instance);\n
    Handsontable.Comments.init();\n
  }\n
},\n
    afterRenderer = function(TD, row, col, prop, value, cellProperties) {\n
      if (cellProperties.comment) {\n
        dom.addClass(TD, cellProperties.commentedCellClassName);\n
      }\n
    },\n
    addCommentsActionsToContextMenu = function(defaultOptions) {\n
      var instance = this;\n
      if (!instance.getSettings().comments) {\n
        return;\n
      }\n
      defaultOptions.items.push(Handsontable.ContextMenu.SEPARATOR);\n
      defaultOptions.items.push({\n
        key: \'commentsAddEdit\',\n
        name: function() {\n
          var hasComment = Handsontable.Comments.checkSelectionCommentsConsistency();\n
          return hasComment ? "Edit Comment" : "Add Comment";\n
        },\n
        callback: function(key, selection, event) {\n
          Handsontable.Comments.showComment(this.getSelectedRange());\n
        },\n
        disabled: function() {\n
          return false;\n
        }\n
      });\n
      defaultOptions.items.push({\n
        key: \'commentsRemove\',\n
        name: function() {\n
          return "Delete Comment";\n
        },\n
        callback: function(key, selection, event) {\n
          Handsontable.Comments.removeComment(selection.start.row, selection.start.col);\n
        },\n
        disabled: function() {\n
          var hasComment = Handsontable.Comments.checkSelectionCommentsConsistency();\n
          return !hasComment;\n
        }\n
      });\n
    };\n
Handsontable.hooks.add(\'beforeInit\', init);\n
Handsontable.hooks.add(\'afterContextMenuDefaultOptions\', addCommentsActionsToContextMenu);\n
Handsontable.hooks.add(\'afterRenderer\', afterRenderer);\n
\n
\n
//# \n
},{"./../../3rdparty/walkontable/src/cell/coords.js":9,"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46}],55:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ContextMenu: {get: function() {\n
      return ContextMenu;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ContextMenu(instance, customOptions) {\n
  this.instance = instance;\n
  var contextMenu = this;\n
  contextMenu.menus = [];\n
  contextMenu.htMenus = {};\n
  contextMenu.triggerRows = [];\n
  contextMenu.eventManager = eventManagerObject(contextMenu);\n
  this.enabled = true;\n
  this.instance.addHook(\'afterDestroy\', function() {\n
    contextMenu.destroy();\n
  });\n
  this.defaultOptions = {items: [{\n
      key: \'row_above\',\n
      name: \'Insert row above\',\n
      callback: function(key, selection) {\n
        this.alter("insert_row", selection.start.row);\n
      },\n
      disabled: function() {\n
        var selected = this.getSelected(),\n
            entireColumnSelection = [0, selected[1], this.countRows() - 1, selected[1]],\n
            columnSelected = entireColumnSelection.join(\',\') == selected.join(\',\');\n
        return selected[0] < 0 || this.countRows() >= this.getSettings().maxRows || columnSelected;\n
      }\n
    }, {\n
      key: \'row_below\',\n
      name: \'Insert row below\',\n
      callback: function(key, selection) {\n
        this.alter("insert_row", selection.end.row + 1);\n
      },\n
      disabled: function() {\n
        var selected = this.getSelected(),\n
            entireColumnSelection = [0, selected[1], this.countRows() - 1, selected[1]],\n
            columnSelected = entireColumnSelection.join(\',\') == selected.join(\',\');\n
        return this.getSelected()[0] < 0 || this.countRows() >= this.getSettings().maxRows || columnSelected;\n
      }\n
    }, ContextMenu.SEPARATOR, {\n
      key: \'col_left\',\n
      name: \'Insert column on the left\',\n
      callback: function(key, selection) {\n
        this.alter("insert_col", selection.start.col);\n
      },\n
      disabled: function() {\n
        if (!this.isColumnModificationAllowed()) {\n
          return true;\n
        }\n
        var selected = this.getSelected(),\n
            entireRowSelection = [selected[0], 0, selected[0], this.countCols() - 1],\n
            rowSelected = entireRowSelection.join(\',\') == selected.join(\',\');\n
        return this.getSelected()[1] < 0 || this.countCols() >= this.getSettings().maxCols || rowSelected;\n
      }\n
    }, {\n
      key: \'col_right\',\n
      name: \'Insert column on the right\',\n
      callback: function(key, selection) {\n
        this.alter("insert_col", selection.end.col + 1);\n
      },\n
      disabled: function() {\n
        if (!this.isColumnModificationAllowed()) {\n
          return true;\n
        }\n
        var selected = this.getSelected(),\n
            entireRowSelection = [selected[0], 0, selected[0], this.countCols() - 1],\n
            rowSelected = entireRowSelection.join(\',\') == selected.join(\',\');\n
        return selected[1] < 0 || this.countCols() >= this.getSettings().maxCols || rowSelected;\n
      }\n
    }, ContextMenu.SEPARATOR, {\n
      key: \'remove_row\',\n
      name: \'Remove row\',\n
      callback: function(key, selection) {\n
        var amount = selection.end.row - selection.start.row + 1;\n
        this.alter("remove_row", selection.start.row, amount);\n
      },\n
      disabled: function() {\n
        var selected = this.getSelected(),\n
            entireColumnSelection = [0, selected[1], this.countRows() - 1, selected[1]],\n
            columnSelected = entireColumnSelection.join(\',\') == selected.join(\',\');\n
        return (selected[0] < 0 || columnSelected);\n
      }\n
    }, {\n
      key: \'remove_col\',\n
      name: \'Remove column\',\n
      callback: function(key, selection) {\n
        var amount = selection.end.col - selection.start.col + 1;\n
        this.alter("remove_col", selection.start.col, amount);\n
      },\n
      disabled: function() {\n
        if (!this.isColumnModificationAllowed()) {\n
          return true;\n
        }\n
        var selected = this.getSelected(),\n
            entireRowSelection = [selected[0], 0, selected[0], this.countCols() - 1],\n
            rowSelected = entireRowSelection.join(\',\') == selected.join(\',\');\n
        return (selected[1] < 0 || rowSelected);\n
      }\n
    }, ContextMenu.SEPARATOR, {\n
      key: \'undo\',\n
      name: \'Undo\',\n
      callback: function() {\n
        this.undo();\n
      },\n
      disabled: function() {\n
        return this.undoRedo && !this.undoRedo.isUndoAvailable();\n
      }\n
    }, {\n
      key: \'redo\',\n
      name: \'Redo\',\n
      callback: function() {\n
        this.redo();\n
      },\n
      disabled: function() {\n
        return this.undoRedo && !this.undoRedo.isRedoAvailable();\n
      }\n
    }, ContextMenu.SEPARATOR, {\n
      key: \'make_read_only\',\n
      name: function() {\n
        var label = "Read only";\n
        var atLeastOneReadOnly = contextMenu.checkSelectionReadOnlyConsistency(this);\n
        if (atLeastOneReadOnly) {\n
          label = contextMenu.markSelected(label);\n
        }\n
        return label;\n
      },\n
      callback: function() {\n
        var atLeastOneReadOnly = contextMenu.checkSelectionReadOnlyConsistency(this);\n
        var that = this;\n
        this.getSelectedRange().forAll(function(r, c) {\n
          that.getCellMeta(r, c).readOnly = atLeastOneReadOnly ? false : true;\n
        });\n
        this.render();\n
      }\n
    }, ContextMenu.SEPARATOR, {\n
      key: \'alignment\',\n
      name: \'Alignment\',\n
      submenu: {items: [{\n
          name: function() {\n
            var label = "Left";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htLeft\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'horizontal\', \'htLeft\');\n
          },\n
          disabled: false\n
        }, {\n
          name: function() {\n
            var label = "Center";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htCenter\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'horizontal\', \'htCenter\');\n
          },\n
          disabled: false\n
        }, {\n
          name: function() {\n
            var label = "Right";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htRight\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'horizontal\', \'htRight\');\n
          },\n
          disabled: false\n
        }, {\n
          name: function() {\n
            var label = "Justify";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htJustify\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'horizontal\', \'htJustify\');\n
          },\n
          disabled: false\n
        }, ContextMenu.SEPARATOR, {\n
          name: function() {\n
            var label = "Top";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htTop\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'vertical\', \'htTop\');\n
          },\n
          disabled: false\n
        }, {\n
          name: function() {\n
            var label = "Middle";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htMiddle\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'vertical\', \'htMiddle\');\n
          },\n
          disabled: false\n
        }, {\n
          name: function() {\n
            var label = "Bottom";\n
            var hasClass = contextMenu.checkSelectionAlignment(this, \'htBottom\');\n
            if (hasClass) {\n
              label = contextMenu.markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            align.call(this, this.getSelectedRange(), \'vertical\', \'htBottom\');\n
          },\n
          disabled: false\n
        }]}\n
    }]};\n
  contextMenu.options = {};\n
  helper.extend(contextMenu.options, this.options);\n
  this.bindMouseEvents();\n
  this.markSelected = function(label) {\n
    return "<span class=\'selected\'>" + String.fromCharCode(10003) + "</span>" + label;\n
  };\n
  this.checkSelectionAlignment = function(hot, className) {\n
    var hasAlignment = false;\n
    hot.getSelectedRange().forAll(function(r, c) {\n
      var metaClassName = hot.getCellMeta(r, c).className;\n
      if (metaClassName && metaClassName.indexOf(className) != -1) {\n
        hasAlignment = true;\n
        return false;\n
      }\n
    });\n
    return hasAlignment;\n
  };\n
  if (!this.instance.getSettings().allowInsertRow) {\n
    var rowAboveIndex = findIndexByKey(this.defaultOptions.items, \'row_above\');\n
    this.defaultOptions.items.splice(rowAboveIndex, 1);\n
    var rowBelowIndex = findIndexByKey(this.defaultOptions.items, \'row_above\');\n
    this.defaultOptions.items.splice(rowBelowIndex, 1);\n
    this.defaultOptions.items.splice(rowBelowIndex, 1);\n
  }\n
  if (!this.instance.getSettings().allowInsertColumn) {\n
    var colLeftIndex = findIndexByKey(this.defaultOptions.items, \'col_left\');\n
    this.defaultOptions.items.splice(colLeftIndex, 1);\n
    var colRightIndex = findIndexByKey(this.defaultOptions.items, \'col_right\');\n
    this.defaultOptions.items.splice(colRightIndex, 1);\n
    this.defaultOptions.items.splice(colRightIndex, 1);\n
  }\n
  var removeRow = false;\n
  var removeCol = false;\n
  var removeRowIndex,\n
      removeColumnIndex;\n
  if (!this.instance.getSettings().allowRemoveRow) {\n
    removeRowIndex = findIndexByKey(this.defaultOptions.items, \'remove_row\');\n
    this.defaultOptions.items.splice(removeRowIndex, 1);\n
    removeRow = true;\n
  }\n
  if (!this.instance.getSettings().allowRemoveColumn) {\n
    removeColumnIndex = findIndexByKey(this.defaultOptions.items, \'remove_col\');\n
    this.defaultOptions.items.splice(removeColumnIndex, 1);\n
    removeCol = true;\n
  }\n
  if (removeRow && removeCol) {\n
    this.defaultOptions.items.splice(removeColumnIndex, 1);\n
  }\n
  this.checkSelectionReadOnlyConsistency = function(hot) {\n
    var atLeastOneReadOnly = false;\n
    hot.getSelectedRange().forAll(function(r, c) {\n
      if (hot.getCellMeta(r, c).readOnly) {\n
        atLeastOneReadOnly = true;\n
        return false;\n
      }\n
    });\n
    return atLeastOneReadOnly;\n
  };\n
  Handsontable.hooks.run(instance, \'afterContextMenuDefaultOptions\', this.defaultOptions);\n
}\n
ContextMenu.prototype.createMenu = function(menuName, row) {\n
  if (menuName) {\n
    menuName = menuName.replace(/ /g, \'_\');\n
    menuName = \'htContextSubMenu_\' + menuName;\n
  }\n
  var menu;\n
  if (menuName) {\n
    menu = document.querySelector(\'.htContextMenu.\' + menuName);\n
  } else {\n
    menu = document.querySelector(\'.htContextMenu\');\n
  }\n
  if (!menu) {\n
    menu = document.createElement(\'DIV\');\n
    dom.addClass(menu, \'htContextMenu\');\n
    if (menuName) {\n
      dom.addClass(menu, menuName);\n
    }\n
    document.getElementsByTagName(\'body\')[0].appendChild(menu);\n
  }\n
  if (this.menus.indexOf(menu) < 0) {\n
    this.menus.push(menu);\n
    row = row || 0;\n
    this.triggerRows.push(row);\n
  }\n
  return menu;\n
};\n
ContextMenu.prototype.bindMouseEvents = function() {\n
  function contextMenuOpenListener(event) {\n
    var settings = this.instance.getSettings(),\n
        showRowHeaders = this.instance.getSettings().rowHeaders,\n
        showColHeaders = this.instance.getSettings().colHeaders,\n
        containsCornerHeader,\n
        element,\n
        items,\n
        menu;\n
    function isValidElement(element) {\n
      return element.nodeName === \'TD\' || element.parentNode.nodeName === \'TD\';\n
    }\n
    element = event.realTarget;\n
    this.closeAll();\n
    event.preventDefault();\n
    helper.stopPropagation(event);\n
    if (!(showRowHeaders || showColHeaders)) {\n
      if (!isValidElement(element) && !(dom.hasClass(element, \'current\') && dom.hasClass(element, \'wtBorder\'))) {\n
        return;\n
      }\n
    } else if (showRowHeaders && showColHeaders) {\n
      containsCornerHeader = element.parentNode.querySelectorAll(\'.cornerHeader\').length > 0;\n
      if (containsCornerHeader) {\n
        return;\n
      }\n
    }\n
    menu = this.createMenu();\n
    items = this.getItems(settings.contextMenu);\n
    this.show(menu, items);\n
    this.setMenuPosition(event, menu);\n
    this.eventManager.addEventListener(document.documentElement, \'mousedown\', helper.proxy(ContextMenu.prototype.closeAll, this));\n
  }\n
  var eventManager = eventManagerObject(this.instance);\n
  eventManager.addEventListener(this.instance.rootElement, \'contextmenu\', helper.proxy(contextMenuOpenListener, this));\n
};\n
ContextMenu.prototype.bindTableEvents = function() {\n
  this._afterScrollCallback = function() {};\n
  this.instance.addHook(\'afterScrollVertically\', this._afterScrollCallback);\n
  this.instance.addHook(\'afterScrollHorizontally\', this._afterScrollCallback);\n
};\n
ContextMenu.prototype.unbindTableEvents = function() {\n
  if (this._afterScrollCallback) {\n
    this.instance.removeHook(\'afterScrollVertically\', this._afterScrollCallback);\n
    this.instance.removeHook(\'afterScrollHorizontally\', this._afterScrollCallback);\n
    this._afterScrollCallback = null;\n
  }\n
};\n
ContextMenu.prototype.performAction = function(event, hot) {\n
  var contextMenu = this;\n
  var selectedItemIndex = hot.getSelected()[0];\n
  var selectedItem = hot.getData()[selectedItemIndex];\n
  if (selectedItem.disabled === true || (typeof selectedItem.disabled == \'function\' && selectedItem.disabled.call(this.instance) === true)) {\n
    return;\n
  }\n
  if (!selectedItem.hasOwnProperty(\'submenu\')) {\n
    if (typeof selectedItem.callback != \'function\') {\n
      return;\n
    }\n
    var selRange = this.instance.getSelectedRange();\n
    var normalizedSelection = ContextMenu.utils.normalizeSelection(selRange);\n
    selectedItem.callback.call(this.instance, selectedItem.key, normalizedSelection, event);\n
    contextMenu.closeAll();\n
  }\n
};\n
ContextMenu.prototype.unbindMouseEvents = function() {\n
  this.eventManager.clear();\n
  var eventManager = eventManagerObject(this.instance);\n
  eventManager.removeEventListener(this.instance.rootElement, \'contextmenu\');\n
};\n
ContextMenu.prototype.show = function(menu, items) {\n
  var that = this;\n
  menu.removeAttribute(\'style\');\n
  menu.style.display = \'block\';\n
  var settings = {\n
    data: items,\n
    colHeaders: false,\n
    colWidths: [200],\n
    readOnly: true,\n
    copyPaste: false,\n
    columns: [{\n
      data: \'name\',\n
      renderer: helper.proxy(this.renderer, this)\n
    }],\n
    renderAllRows: true,\n
    beforeKeyDown: function(event) {\n
      that.onBeforeKeyDown(event, htContextMenu);\n
    },\n
    afterOnCellMouseOver: function(event, coords, TD) {\n
      that.onCellMouseOver(event, coords, TD, htContextMenu);\n
    }\n
  };\n
  var htContextMenu = new Handsontable(menu, settings);\n
  htContextMenu.isHotTableEnv = this.instance.isHotTableEnv;\n
  Handsontable.eventManager.isHotTableEnv = this.instance.isHotTableEnv;\n
  this.eventManager.removeEventListener(menu, \'mousedown\');\n
  this.eventManager.addEventListener(menu, \'mousedown\', function(event) {\n
    that.performAction(event, htContextMenu);\n
  });\n
  this.bindTableEvents();\n
  htContextMenu.listen();\n
  this.htMenus[htContextMenu.guid] = htContextMenu;\n
  Handsontable.hooks.run(this.instance, \'afterContextMenuShow\', htContextMenu);\n
};\n
ContextMenu.prototype.close = function(menu) {\n
  this.hide(menu);\n
  this.eventManager.clear();\n
  this.unbindTableEvents();\n
  this.instance.listen();\n
};\n
ContextMenu.prototype.closeAll = function() {\n
  while (this.menus.length > 0) {\n
    var menu = this.menus.pop();\n
    if (menu) {\n
      this.close(menu);\n
    }\n
  }\n
  this.triggerRows = [];\n
};\n
ContextMenu.prototype.closeLastOpenedSubMenu = function() {\n
  var menu = this.menus.pop();\n
  if (menu) {\n
    this.hide(menu);\n
  }\n
};\n
ContextMenu.prototype.hide = function(menu) {\n
  menu.style.display = \'none\';\n
  var instance = this.htMenus[menu.id];\n
  Handsontable.hooks.run(this.instance, \'afterContextMenuHide\', instance);\n
  instance.destroy();\n
  delete this.htMenus[menu.id];\n
};\n
ContextMenu.prototype.renderer = function(instance, TD, row, col, prop, value) {\n
  var contextMenu = this;\n
  var item = instance.getData()[row];\n
  var wrapper = document.createElement(\'DIV\');\n
  if (typeof value === \'function\') {\n
    value = value.call(this.instance);\n
  }\n
  dom.empty(TD);\n
  TD.appendChild(wrapper);\n
  if (itemIsSeparator(item)) {\n
    dom.addClass(TD, \'htSeparator\');\n
  } else {\n
    dom.fastInnerHTML(wrapper, value);\n
  }\n
  if (itemIsDisabled(item)) {\n
    dom.addClass(TD, \'htDisabled\');\n
    this.eventManager.addEventListener(wrapper, \'mouseenter\', function() {\n
      instance.deselectCell();\n
    });\n
  } else {\n
    if (isSubMenu(item)) {\n
      dom.addClass(TD, \'htSubmenu\');\n
      this.eventManager.addEventListener(wrapper, \'mouseenter\', function() {\n
        instance.selectCell(row, col);\n
      });\n
    } else {\n
      dom.removeClass(TD, \'htSubmenu\');\n
      dom.removeClass(TD, \'htDisabled\');\n
      this.eventManager.addEventListener(wrapper, \'mouseenter\', function() {\n
        instance.selectCell(row, col);\n
      });\n
    }\n
  }\n
  function isSubMenu(item) {\n
    return item.hasOwnProperty(\'submenu\');\n
  }\n
  function itemIsSeparator(item) {\n
    return new RegExp(ContextMenu.SEPARATOR.name, \'i\').test(item.name);\n
  }\n
  function itemIsDisabled(item) {\n
    return item.disabled === true || (typeof item.disabled == \'function\' && item.disabled.call(contextMenu.instance) === true);\n
  }\n
};\n
ContextMenu.prototype.onCellMouseOver = function(event, coords, TD, hot) {\n
  var menusLength = this.menus.length;\n
  if (menusLength > 0) {\n
    var lastMenu = this.menus[menusLength - 1];\n
    if (lastMenu.id != hot.guid) {\n
      this.closeLastOpenedSubMenu();\n
    }\n
  } else {\n
    this.closeLastOpenedSubMenu();\n
  }\n
  if (TD.className.indexOf(\'htSubmenu\') != -1) {\n
    var selectedItem = hot.getData()[coords.row];\n
    var items = this.getItems(selectedItem.submenu);\n
    var subMenu = this.createMenu(selectedItem.name, coords.row);\n
    var tdCoords = TD.getBoundingClientRect();\n
    this.show(subMenu, items);\n
    this.setSubMenuPosition(tdCoords, subMenu);\n
  }\n
};\n
ContextMenu.prototype.onBeforeKeyDown = function(event, instance) {\n
  dom.enableImmediatePropagation(event);\n
  var contextMenu = this;\n
  var selection = instance.getSelected();\n
  switch (event.keyCode) {\n
    case helper.keyCode.ESCAPE:\n
      contextMenu.closeAll();\n
      event.preventDefault();\n
      event.stopImmediatePropagation();\n
      break;\n
    case helper.keyCode.ENTER:\n
      if (selection) {\n
        contextMenu.performAction(event, instance);\n
      }\n
      break;\n
    case helper.keyCode.ARROW_DOWN:\n
      if (!selection) {\n
        selectFirstCell(instance, contextMenu);\n
      } else {\n
        selectNextCell(selection[0], selection[1], instance, contextMenu);\n
      }\n
      event.preventDefault();\n
      event.stopImmediatePropagation();\n
      break;\n
    case helper.keyCode.ARROW_UP:\n
      if (!selection) {\n
        selectLastCell(instance, contextMenu);\n
      } else {\n
        selectPrevCell(selection[0], selection[1], instance, contextMenu);\n
      }\n
      event.preventDefault();\n
      event.stopImmediatePropagation();\n
      break;\n
    case helper.keyCode.ARROW_RIGHT:\n
      if (selection) {\n
        var row = selection[0];\n
        var cell = instance.getCell(selection[0], 0);\n
        if (ContextMenu.utils.hasSubMenu(cell)) {\n
          openSubMenu(instance, contextMenu, cell, row);\n
        }\n
      }\n
      event.preventDefault();\n
      event.stopImmediatePropagation();\n
      break;\n
    case helper.keyCode.ARROW_LEFT:\n
      if (selection) {\n
        if (instance.rootElement.className.indexOf(\'htContextSubMenu_\') != -1) {\n
          contextMenu.closeLastOpenedSubMenu();\n
          var index = contextMenu.menus.length;\n
          if (index > 0) {\n
            var menu = contextMenu.menus[index - 1];\n
            var triggerRow = contextMenu.triggerRows.pop();\n
            instance = this.htMenus[menu.id];\n
            instance.selectCell(triggerRow, 0);\n
          }\n
        }\n
        event.preventDefault();\n
        event.stopImmediatePropagation();\n
      }\n
      break;\n
  }\n
  function selectFirstCell(instance) {\n
    var firstCell = instance.getCell(0, 0);\n
    if (ContextMenu.utils.isSeparator(firstCell) || ContextMenu.utils.isDisabled(firstCell)) {\n
      selectNextCell(0, 0, instance);\n
    } else {\n
      instance.selectCell(0, 0);\n
    }\n
  }\n
  function selectLastCell(instance) {\n
    var lastRow = instance.countRows() - 1;\n
    var lastCell = instance.getCell(lastRow, 0);\n
    if (ContextMenu.utils.isSeparator(lastCell) || ContextMenu.utils.isDisabled(lastCell)) {\n
      selectPrevCell(lastRow, 0, instance);\n
    } else {\n
      instance.selectCell(lastRow, 0);\n
    }\n
  }\n
  function selectNextCell(row, col, instance) {\n
    var nextRow = row + 1;\n
    var nextCell = nextRow < instance.countRows() ? instance.getCell(nextRow, col) : null;\n
    if (!nextCell) {\n
      return;\n
    }\n
    if (ContextMenu.utils.isSeparator(nextCell) || ContextMenu.utils.isDisabled(nextCell)) {\n
      selectNextCell(nextRow, col, instance);\n
    } else {\n
      instance.selectCell(nextRow, col);\n
    }\n
  }\n
  function selectPrevCell(row, col, instance) {\n
    var prevRow = row - 1;\n
    var prevCell = prevRow >= 0 ? instance.getCell(prevRow, col) : null;\n
    if (!prevCell) {\n
      return;\n
    }\n
    if (ContextMenu.utils.isSeparator(prevCell) || ContextMenu.utils.isDisabled(prevCell)) {\n
      selectPrevCell(prevRow, col, instance);\n
    } else {\n
      instance.selectCell(prevRow, col);\n
    }\n
  }\n
  function openSubMenu(instance, contextMenu, cell, row) {\n
    var selectedItem = instance.getData()[row];\n
    var items = contextMenu.getItems(selectedItem.submenu);\n
    var subMenu = contextMenu.createMenu(selectedItem.name, row);\n
    var coords = cell.getBoundingClientRect();\n
    var subMenuInstance = contextMenu.show(subMenu, items);\n
    contextMenu.setSubMenuPosition(coords, subMenu);\n
    subMenuInstance.selectCell(0, 0);\n
  }\n
};\n
function findByKey(items, key) {\n
  for (var i = 0,\n
      ilen = items.length; i < ilen; i++) {\n
    if (items[i].key === key) {\n
      return items[i];\n
    }\n
  }\n
}\n
function findIndexByKey(items, key) {\n
  for (var i = 0,\n
      ilen = items.length; i < ilen; i++) {\n
    if (items[i].key === key) {\n
      return i;\n
    }\n
  }\n
}\n
ContextMenu.prototype.getItems = function(items) {\n
  var menu,\n
      item;\n
  function ContextMenuItem(rawItem) {\n
    if (typeof rawItem == \'string\') {\n
      this.name = rawItem;\n
    } else {\n
      helper.extend(this, rawItem);\n
    }\n
  }\n
  ContextMenuItem.prototype = items;\n
  if (items && items.items) {\n
    items = items.items;\n
  }\n
  if (items === true) {\n
    items = this.defaultOptions.items;\n
  }\n
  if (1 == 1) {\n
    menu = [];\n
    for (var key in items) {\n
      if (items.hasOwnProperty(key)) {\n
        if (typeof items[key] === \'string\') {\n
          item = findByKey(this.defaultOptions.items, items[key]);\n
        } else {\n
          item = findByKey(this.defaultOptions.items, key);\n
        }\n
        if (!item) {\n
          item = items[key];\n
        }\n
        item = new ContextMenuItem(item);\n
        if (typeof items[key] === \'object\') {\n
          helper.extend(item, items[key]);\n
        }\n
        if (!item.key) {\n
          item.key = key;\n
        }\n
        menu.push(item);\n
      }\n
    }\n
  }\n
  return menu;\n
};\n
ContextMenu.prototype.setSubMenuPosition = function(coords, menu) {\n
  var scrollTop = dom.getWindowScrollTop();\n
  var scrollLeft = dom.getWindowScrollLeft();\n
  var cursor = {\n
    top: scrollTop + coords.top,\n
    topRelative: coords.top,\n
    left: coords.left,\n
    leftRelative: coords.left - scrollLeft,\n
    scrollTop: scrollTop,\n
    scrollLeft: scrollLeft,\n
    cellHeight: coords.height,\n
    cellWidth: coords.width\n
  };\n
  if (this.menuFitsBelowCursor(cursor, menu, document.body.clientWidth)) {\n
    this.positionMenuBelowCursor(cursor, menu, true);\n
  } else {\n
    if (this.menuFitsAboveCursor(cursor, menu)) {\n
      this.positionMenuAboveCursor(cursor, menu, true);\n
    } else {\n
      this.positionMenuBelowCursor(cursor, menu, true);\n
    }\n
  }\n
  if (this.menuFitsOnRightOfCursor(cursor, menu, document.body.clientWidth)) {\n
    this.positionMenuOnRightOfCursor(cursor, menu, true);\n
  } else {\n
    this.positionMenuOnLeftOfCursor(cursor, menu, true);\n
  }\n
};\n
ContextMenu.prototype.setMenuPosition = function(event, menu) {\n
  var scrollTop = dom.getWindowScrollTop();\n
  var scrollLeft = dom.getWindowScrollLeft();\n
  var cursorY = event.pageY || (event.clientY + scrollTop);\n
  var cursorX = event.pageX || (event.clientX + scrollLeft);\n
  var cursor = {\n
    top: cursorY,\n
    topRelative: cursorY - scrollTop,\n
    left: cursorX,\n
    leftRelative: cursorX - scrollLeft,\n
    scrollTop: scrollTop,\n
    scrollLeft: scrollLeft,\n
    cellHeight: event.target.clientHeight,\n
    cellWidth: event.target.clientWidth\n
  };\n
  if (this.menuFitsBelowCursor(cursor, menu, document.body.clientHeight)) {\n
    this.positionMenuBelowCursor(cursor, menu);\n
  } else {\n
    if (this.menuFitsAboveCursor(cursor, menu)) {\n
      this.positionMenuAboveCursor(cursor, menu);\n
    } else {\n
      this.positionMenuBelowCursor(cursor, menu);\n
    }\n
  }\n
  if (this.menuFitsOnRightOfCursor(cursor, menu, document.body.clientWidth)) {\n
    this.positionMenuOnRightOfCursor(cursor, menu);\n
  } else {\n
    this.positionMenuOnLeftOfCursor(cursor, menu);\n
  }\n
};\n
ContextMenu.prototype.menuFitsAboveCursor = function(cursor, menu) {\n
  return cursor.topRelative >= menu.offsetHeight;\n
};\n
ContextMenu.prototype.menuFitsBelowCursor = function(cursor, menu, viewportHeight) {\n
  return cursor.topRelative + menu.offsetHeight <= viewportHeight;\n
};\n
ContextMenu.prototype.menuFitsOnRightOfCursor = function(cursor, menu, viewportHeight) {\n
  return cursor.leftRelative + menu.offsetWidth <= viewportHeight;\n
};\n
ContextMenu.prototype.positionMenuBelowCursor = function(cursor, menu) {\n
  menu.style.top = cursor.top + \'px\';\n
};\n
ContextMenu.prototype.positionMenuAboveCursor = function(cursor, menu, subMenu) {\n
  if (subMenu) {\n
    menu.style.top = (cursor.top + cursor.cellHeight - menu.offsetHeight) + \'px\';\n
  } else {\n
    menu.style.top = (cursor.top - menu.offsetHeight) + \'px\';\n
  }\n
};\n
ContextMenu.prototype.positionMenuOnRightOfCursor = function(cursor, menu, subMenu) {\n
  if (subMenu) {\n
    menu.style.left = 1 + cursor.left + cursor.cellWidth + \'px\';\n
  } else {\n
    menu.style.left = 1 + cursor.left + \'px\';\n
  }\n
};\n
ContextMenu.prototype.positionMenuOnLeftOfCursor = function(cursor, menu, subMenu) {\n
  if (subMenu) {\n
    menu.style.left = (cursor.left - menu.offsetWidth) + \'px\';\n
  } else {\n
    menu.style.left = (cursor.left - menu.offsetWidth) + \'px\';\n
  }\n
};\n
ContextMenu.utils = {};\n
ContextMenu.utils.normalizeSelection = function(selRange) {\n
  return {\n
    start: selRange.getTopLeftCorner(),\n
    end: selRange.getBottomRightCorner()\n
  };\n
};\n
ContextMenu.utils.isSeparator = function(cell) {\n
  return dom.hasClass(cell, \'htSeparator\');\n
};\n
ContextMenu.utils.hasSubMenu = function(cell) {\n
  return dom.hasClass(cell, \'htSubmenu\');\n
};\n
ContextMenu.utils.isDisabled = function(cell) {\n
  return dom.hasClass(cell, \'htDisabled\');\n
};\n
ContextMenu.prototype.enable = function() {\n
  if (!this.enabled) {\n
    this.enabled = true;\n
    this.bindMouseEvents();\n
  }\n
};\n
ContextMenu.prototype.disable = function() {\n
  if (this.enabled) {\n
    this.enabled = false;\n
    this.closeAll();\n
    this.unbindMouseEvents();\n
    this.unbindTableEvents();\n
  }\n
};\n
ContextMenu.prototype.destroy = function() {\n
  this.closeAll();\n
  while (this.menus.length > 0) {\n
    var menu = this.menus.pop();\n
    this.triggerRows.pop();\n
    if (menu) {\n
      this.close(menu);\n
      if (!this.isMenuEnabledByOtherHotInstance()) {\n
        this.removeMenu(menu);\n
      }\n
    }\n
  }\n
  this.unbindMouseEvents();\n
  this.unbindTableEvents();\n
};\n
ContextMenu.prototype.isMenuEnabledByOtherHotInstance = function() {\n
  var hotContainers = document.querySelectorAll(\'.handsontable\');\n
  var menuEnabled = false;\n
  for (var i = 0,\n
      len = hotContainers.length; i < len; i++) {\n
    var instance = this.htMenus[hotContainers[i].id];\n
    if (instance && instance.getSettings().contextMenu) {\n
      menuEnabled = true;\n
      break;\n
    }\n
  }\n
  return menuEnabled;\n
};\n
ContextMenu.prototype.removeMenu = function(menu) {\n
  if (menu.parentNode) {\n
    this.menu.parentNode.removeChild(menu);\n
  }\n
};\n
ContextMenu.prototype.align = function(range, type, alignment) {\n
  align.call(this, range, type, alignment);\n
};\n
ContextMenu.SEPARATOR = {name: "---------"};\n
function updateHeight() {\n
  if (this.rootElement.className.indexOf(\'htContextMenu\')) {\n
    return;\n
  }\n
  var realSeparatorHeight = 0,\n
      realEntrySize = 0,\n
      dataSize = this.getSettings().data.length,\n
      currentHiderWidth = parseInt(this.view.wt.wtTable.hider.style.width, 10);\n
  for (var i = 0; i < dataSize; i++) {\n
    if (this.getSettings().data[i].name == ContextMenu.SEPARATOR.name) {\n
      realSeparatorHeight += 1;\n
    } else {\n
      realEntrySize += 26;\n
    }\n
  }\n
  this.view.wt.wtTable.holder.style.width = currentHiderWidth + 22 + "px";\n
  this.view.wt.wtTable.holder.style.height = realEntrySize + realSeparatorHeight + 4 + "px";\n
}\n
function prepareVerticalAlignClass(className, alignment) {\n
  if (className.indexOf(alignment) != -1) {\n
    return className;\n
  }\n
  className = className.replace(\'htTop\', \'\').replace(\'htMiddle\', \'\').replace(\'htBottom\', \'\').replace(\'  \', \'\');\n
  className += " " + alignment;\n
  return className;\n
}\n
function prepareHorizontalAlignClass(className, alignment) {\n
  if (className.indexOf(alignment) != -1) {\n
    return className;\n
  }\n
  className = className.replace(\'htLeft\', \'\').replace(\'htCenter\', \'\').replace(\'htRight\', \'\').replace(\'htJustify\', \'\').replace(\'  \', \'\');\n
  className += " " + alignment;\n
  return className;\n
}\n
function getAlignmentClasses(range) {\n
  var classesArray = {};\n
  for (var row = range.from.row; row <= range.to.row; row++) {\n
    for (var col = range.from.col; col <= range.to.col; col++) {\n
      if (!classesArray[row]) {\n
        classesArray[row] = [];\n
      }\n
      classesArray[row][col] = this.getCellMeta(row, col).className;\n
    }\n
  }\n
  return classesArray;\n
}\n
function doAlign(row, col, type, alignment) {\n
  var cellMeta = this.getCellMeta(row, col),\n
      className = alignment;\n
  if (cellMeta.className) {\n
    if (type === \'vertical\') {\n
      className = prepareVerticalAlignClass(cellMeta.className, alignment);\n
    } else {\n
      className = prepareHorizontalAlignClass(cellMeta.className, alignment);\n
    }\n
  }\n
  this.setCellMeta(row, col, \'className\', className);\n
}\n
function align(range, type, alignment) {\n
  var stateBefore = getAlignmentClasses.call(this, range);\n
  this.runHooks(\'beforeCellAlignment\', stateBefore, range, type, alignment);\n
  if (range.from.row == range.to.row && range.from.col == range.to.col) {\n
    doAlign.call(this, range.from.row, range.from.col, type, alignment);\n
  } else {\n
    for (var row = range.from.row; row <= range.to.row; row++) {\n
      for (var col = range.from.col; col <= range.to.col; col++) {\n
        doAlign.call(this, row, col, type, alignment);\n
      }\n
    }\n
  }\n
  this.render();\n
}\n
function init() {\n
  var instance = this;\n
  var contextMenuSetting = instance.getSettings().contextMenu;\n
  var customOptions = helper.isObject(contextMenuSetting) ? contextMenuSetting : {};\n
  if (contextMenuSetting) {\n
    if (!instance.contextMenu) {\n
      instance.contextMenu = new ContextMenu(instance, customOptions);\n
    }\n
    instance.contextMenu.enable();\n
  } else if (instance.contextMenu) {\n
    instance.contextMenu.destroy();\n
    delete instance.contextMenu;\n
  }\n
}\n
Handsontable.hooks.add(\'afterInit\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', init);\n
Handsontable.hooks.add(\'afterInit\', updateHeight);\n
Handsontable.hooks.register(\'afterContextMenuDefaultOptions\');\n
Handsontable.hooks.register(\'afterContextMenuShow\');\n
Handsontable.hooks.register(\'afterContextMenuHide\');\n
Handsontable.ContextMenu = ContextMenu;\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46,"./../../plugins.js":49}],56:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ContextMenuCopyPaste: {get: function() {\n
      return ContextMenuCopyPaste;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__95_base_46_js__,\n
    $__zeroclipboard__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var BasePlugin = ($___46__46__47__95_base_46_js__ = require("./../_base.js"), $___46__46__47__95_base_46_js__ && $___46__46__47__95_base_46_js__.__esModule && $___46__46__47__95_base_46_js__ || {default: $___46__46__47__95_base_46_js__}).default;\n
var ZeroClipboard = ($__zeroclipboard__ = require("zeroclipboard"), $__zeroclipboard__ && $__zeroclipboard__.__esModule && $__zeroclipboard__ || {default: $__zeroclipboard__}).default;\n
var ContextMenuCopyPaste = function ContextMenuCopyPaste(hotInstance) {\n
  var $__4 = this;\n
  $traceurRuntime.superConstructor($ContextMenuCopyPaste).call(this, hotInstance);\n
  this.swfPath = null;\n
  this.hotContextMenu = null;\n
  this.outsideClickDeselectsCache = null;\n
  this.hot.addHook(\'afterContextMenuShow\', (function(htContextMenu) {\n
    return $__4.setupZeroClipboard(htContextMenu);\n
  }));\n
  this.hot.addHook(\'afterInit\', (function() {\n
    return $__4.afterInit();\n
  }));\n
  this.hot.addHook(\'afterContextMenuDefaultOptions\', (function(options) {\n
    return $__4.addToContextMenu(options);\n
  }));\n
};\n
var $ContextMenuCopyPaste = ContextMenuCopyPaste;\n
($traceurRuntime.createClass)(ContextMenuCopyPaste, {\n
  afterInit: function() {\n
    if (!this.hot.getSettings().contextMenuCopyPaste) {\n
      return;\n
    } else if (typeof this.hot.getSettings().contextMenuCopyPaste == \'object\') {\n
      this.swfPath = this.hot.getSettings().contextMenuCopyPaste.swfPath;\n
    }\n
    if (typeof ZeroClipboard === \'undefined\') {\n
      throw new Error("To be able to use the Copy/Paste feature from the context menu, you need to manualy include ZeroClipboard.js file to your website.");\n
    }\n
    try {\n
      new ActiveXObject(\'ShockwaveFlash.ShockwaveFlash\');\n
    } catch (exception) {\n
      if (\'undefined\' == typeof navigator.mimeTypes[\'application/x-shockwave-flash\']) {\n
        throw new Error("To be able to use the Copy/Paste feature from the context menu, your browser needs to have Flash Plugin installed.");\n
      }\n
    }\n
    this.prepareZeroClipboard();\n
  },\n
  prepareZeroClipboard: function() {\n
    if (this.swfPath) {\n
      ZeroClipboard.config({swfPath: this.swfPath});\n
    }\n
  },\n
  getCopyValue: function() {\n
    this.hot.copyPaste.setCopyableText();\n
    return this.hot.copyPaste.copyPasteInstance.elTextarea.value;\n
  },\n
  addToContextMenu: function(defaultOptions) {\n
    if (!this.hot.getSettings().contextMenuCopyPaste) {\n
      return;\n
    }\n
    defaultOptions.items.unshift({\n
      key: \'copy\',\n
      name: \'Copy\'\n
    }, {\n
      key: \'paste\',\n
      name: \'Paste\',\n
      callback: function() {\n
        this.copyPaste.triggerPaste();\n
      }\n
    }, Handsontable.ContextMenu.SEPARATOR);\n
  },\n
  setupZeroClipboard: function(hotContextMenu) {\n
    var $__4 = this;\n
    var data,\n
        zeroClipboardInstance;\n
    if (!this.hot.getSettings().contextMenuCopyPaste) {\n
      return;\n
    }\n
    this.hotContextMenu = hotContextMenu;\n
    data = this.hotContextMenu.getData();\n
    for (var i = 0,\n
        ilen = data.length; i < ilen; i++) {\n
      if (data[i].key === \'copy\') {\n
        zeroClipboardInstance = new ZeroClipboard(this.hotContextMenu.getCell(i, 0));\n
        zeroClipboardInstance.off();\n
        zeroClipboardInstance.on(\'copy\', (function(event) {\n
          var clipboard = event.clipboardData;\n
          clipboard.setData(\'text/plain\', $__4.getCopyValue());\n
          $__4.hot.getSettings().outsideClickDeselects = $__4.outsideClickDeselectsCache;\n
        }));\n
        this.bindEvents();\n
        break;\n
      }\n
    }\n
  },\n
  removeCurrentClass: function() {\n
    if (this.hotContextMenu.rootElement) {\n
      var element = this.hotContextMenu.rootElement.querySelector(\'td.current\');\n
      if (element) {\n
        dom.removeClass(element, \'current\');\n
      }\n
    }\n
    this.outsideClickDeselectsCache = this.hot.getSettings().outsideClickDeselects;\n
    this.hot.getSettings().outsideClickDeselects = false;\n
  },\n
  removeZeroClipboardClass: function() {\n
    if (this.hotContextMenu.rootElement) {\n
      var element = this.hotContextMenu.rootElement.querySelector(\'td.zeroclipboard-is-hover\');\n
      if (element) {\n
        dom.removeClass(element, \'zeroclipboard-is-hover\');\n
      }\n
    }\n
    this.hot.getSettings().outsideClickDeselects = this.outsideClickDeselectsCache;\n
  },\n
  bindEvents: function() {\n
    var $__4 = this;\n
    var eventManager = eventManagerObject(this.hotContextMenu);\n
    eventManager.addEventListener(document, \'mouseenter\', (function() {\n
      return $__4.removeCurrentClass();\n
    }));\n
    eventManager.addEventListener(document, \'mouseleave\', (function() {\n
      return $__4.removeZeroClipboardClass();\n
    }));\n
  }\n
}, {}, BasePlugin);\n
;\n
registerPlugin(\'contextMenuCopyPaste\', ContextMenuCopyPaste);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../plugins.js":49,"./../_base.js":50,"zeroclipboard":"zeroclipboard"}],57:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  CopyPaste: {get: function() {\n
      return CopyPaste;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var SheetClip = ($___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__ = require("./../../3rdparty/sheetclip.js"), $___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__ && $___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_sheetclip_46_js__}).default;\n
var copyPasteManager = ($___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__ = require("./../../3rdparty/copypaste.js"), $___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__ && $___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_copypaste_46_js__}).copyPasteManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var WalkontableCellCoords = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ = require("./../../3rdparty/walkontable/src/cell/range.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__}).WalkontableCellRange;\n
;\n
function CopyPastePlugin(instance) {\n
  var _this = this;\n
  this.copyPasteInstance = copyPasteManager();\n
  this.copyPasteInstance.onCut(onCut);\n
  this.copyPasteInstance.onPaste(onPaste);\n
  instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  function onCut() {\n
    if (!instance.isListening()) {\n
      return;\n
    }\n
    instance.selection.empty();\n
  }\n
  function onPaste(str) {\n
    var input,\n
        inputArray,\n
        selected,\n
        coordsFrom,\n
        coordsTo,\n
        cellRange,\n
        topLeftCorner,\n
        bottomRightCorner,\n
        areaStart,\n
        areaEnd;\n
    if (!instance.isListening() || !instance.selection.isSelected()) {\n
      return;\n
    }\n
    input = str;\n
    inputArray = SheetClip.parse(input);\n
    selected = instance.getSelected();\n
    coordsFrom = new WalkontableCellCoords(selected[0], selected[1]);\n
    coordsTo = new WalkontableCellCoords(selected[2], selected[3]);\n
    cellRange = new WalkontableCellRange(coordsFrom, coordsFrom, coordsTo);\n
    topLeftCorner = cellRange.getTopLeftCorner();\n
    bottomRightCorner = cellRange.getBottomRightCorner();\n
    areaStart = topLeftCorner;\n
    areaEnd = new WalkontableCellCoords(Math.max(bottomRightCorner.row, inputArray.length - 1 + topLeftCorner.row), Math.max(bottomRightCorner.col, inputArray[0].length - 1 + topLeftCorner.col));\n
    instance.addHookOnce(\'afterChange\', function(changes, source) {\n
      if (changes && changes.length) {\n
        this.selectCell(areaStart.row, areaStart.col, areaEnd.row, areaEnd.col);\n
      }\n
    });\n
    instance.populateFromArray(areaStart.row, areaStart.col, inputArray, areaEnd.row, areaEnd.col, \'paste\', instance.getSettings().pasteMode);\n
  }\n
  function onBeforeKeyDown(event) {\n
    var ctrlDown;\n
    if (instance.getSelected()) {\n
      if (helper.isCtrlKey(event.keyCode)) {\n
        _this.setCopyableText();\n
        event.stopImmediatePropagation();\n
        return;\n
      }\n
      ctrlDown = (event.ctrlKey || event.metaKey) && !event.altKey;\n
      if (event.keyCode == helper.keyCode.A && ctrlDown) {\n
        instance._registerTimeout(setTimeout(helper.proxy(_this.setCopyableText, _this), 0));\n
      }\n
    }\n
  }\n
  this.destroy = function() {\n
    this.copyPasteInstance.removeCallback(onCut);\n
    this.copyPasteInstance.removeCallback(onPaste);\n
    this.copyPasteInstance.destroy();\n
    instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
  };\n
  instance.addHook(\'afterDestroy\', helper.proxy(this.destroy, this));\n
  this.triggerPaste = helper.proxy(this.copyPasteInstance.triggerPaste, this.copyPasteInstance);\n
  this.triggerCut = helper.proxy(this.copyPasteInstance.triggerCut, this.copyPasteInstance);\n
  this.setCopyableText = function() {\n
    var settings = instance.getSettings();\n
    var copyRowsLimit = settings.copyRowsLimit;\n
    var copyColsLimit = settings.copyColsLimit;\n
    var selRange = instance.getSelectedRange();\n
    var topLeft = selRange.getTopLeftCorner();\n
    var bottomRight = selRange.getBottomRightCorner();\n
    var startRow = topLeft.row;\n
    var startCol = topLeft.col;\n
    var endRow = bottomRight.row;\n
    var endCol = bottomRight.col;\n
    var finalEndRow = Math.min(endRow, startRow + copyRowsLimit - 1);\n
    var finalEndCol = Math.min(endCol, startCol + copyColsLimit - 1);\n
    instance.copyPaste.copyPasteInstance.copyable(instance.getCopyableData(startRow, startCol, finalEndRow, finalEndCol));\n
    if (endRow !== finalEndRow || endCol !== finalEndCol) {\n
      Handsontable.hooks.run(instance, "afterCopyLimit", endRow - startRow + 1, endCol - startCol + 1, copyRowsLimit, copyColsLimit);\n
    }\n
  };\n
}\n
function init() {\n
  var instance = this,\n
      pluginEnabled = instance.getSettings().copyPaste !== false;\n
  if (pluginEnabled && !instance.copyPaste) {\n
    instance.copyPaste = new CopyPastePlugin(instance);\n
  } else if (!pluginEnabled && instance.copyPaste) {\n
    instance.copyPaste.destroy();\n
    delete instance.copyPaste;\n
  }\n
}\n
Handsontable.hooks.add(\'afterInit\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', init);\n
Handsontable.hooks.register(\'afterCopyLimit\');\n
\n
\n
//# \n
},{"./../../3rdparty/copypaste.js":3,"./../../3rdparty/sheetclip.js":5,"./../../3rdparty/walkontable/src/cell/coords.js":9,"./../../3rdparty/walkontable/src/cell/range.js":10,"./../../helpers.js":46,"./../../plugins.js":49}],58:[function(require,module,exports){\n
"use strict";\n
var $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var WalkontableCellRange = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ = require("./../../3rdparty/walkontable/src/cell/range.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__}).WalkontableCellRange;\n
var WalkontableSelection = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__ = require("./../../3rdparty/walkontable/src/selection.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_selection_46_js__}).WalkontableSelection;\n
function CustomBorders() {}\n
var instance;\n
var checkEnable = function(customBorders) {\n
  if (typeof customBorders === "boolean") {\n
    if (customBorders === true) {\n
      return true;\n
    }\n
  }\n
  if (typeof customBorders === "object") {\n
    if (customBorders.length > 0) {\n
      return true;\n
    }\n
  }\n
  return false;\n
};\n
var init = function() {\n
  if (checkEnable(this.getSettings().customBorders)) {\n
    if (!this.customBorders) {\n
      instance = this;\n
      this.customBorders = new CustomBorders();\n
    }\n
  }\n
};\n
var getSettingIndex = function(className) {\n
  for (var i = 0; i < instance.view.wt.selections.length; i++) {\n
    if (instance.view.wt.selections[i].settings.className == className) {\n
      return i;\n
    }\n
  }\n
  return -1;\n
};\n
var insertBorderIntoSettings = function(border) {\n
  var coordinates = {\n
    row: border.row,\n
    col: border.col\n
  };\n
  var selection = new WalkontableSelection(border, new WalkontableCellRange(coordinates, coordinates, coordinates));\n
  var index = getSettingIndex(border.className);\n
  if (index >= 0) {\n
    instance.view.wt.selections[index] = selection;\n
  } else {\n
    instance.view.wt.selections.push(selection);\n
  }\n
};\n
var prepareBorderFromCustomAdded = function(row, col, borderObj) {\n
  var border = createEmptyBorders(row, col);\n
  border = extendDefaultBorder(border, borderObj);\n
  this.setCellMeta(row, col, \'borders\', border);\n
  insertBorderIntoSettings(border);\n
};\n
var prepareBorderFromCustomAddedRange = function(rowObj) {\n
  var range = rowObj.range;\n
  for (var row = range.from.row; row <= range.to.row; row++) {\n
    for (var col = range.from.col; col <= range.to.col; col++) {\n
      var border = createEmptyBorders(row, col);\n
      var add = 0;\n
      if (row == range.from.row) {\n
        add++;\n
        if (rowObj.hasOwnProperty(\'top\')) {\n
          border.top = rowObj.top;\n
        }\n
      }\n
      if (row == range.to.row) {\n
        add++;\n
        if (rowObj.hasOwnProperty(\'bottom\')) {\n
          border.bottom = rowObj.bottom;\n
        }\n
      }\n
      if (col == range.from.col) {\n
        add++;\n
        if (rowObj.hasOwnProperty(\'left\')) {\n
          border.left = rowObj.left;\n
        }\n
      }\n
      if (col == range.to.col) {\n
        add++;\n
        if (rowObj.hasOwnProperty(\'right\')) {\n
          border.right = rowObj.right;\n
        }\n
      }\n
      if (add > 0) {\n
        this.setCellMeta(row, col, \'borders\', border);\n
        insertBorderIntoSettings(border);\n
      }\n
    }\n
  }\n
};\n
var createClassName = function(row, col) {\n
  return "border_row" + row + "col" + col;\n
};\n
var createDefaultCustomBorder = function() {\n
  return {\n
    width: 1,\n
    color: \'#000\'\n
  };\n
};\n
var createSingleEmptyBorder = function() {\n
  return {hide: true};\n
};\n
var createDefaultHtBorder = function() {\n
  return {\n
    width: 1,\n
    color: \'#000\',\n
    cornerVisible: false\n
  };\n
};\n
var createEmptyBorders = function(row, col) {\n
  return {\n
    className: createClassName(row, col),\n
    border: createDefaultHtBorder(),\n
    row: row,\n
    col: col,\n
    top: createSingleEmptyBorder(),\n
    right: createSingleEmptyBorder(),\n
    bottom: createSingleEmptyBorder(),\n
    left: createSingleEmptyBorder()\n
  };\n
};\n
var extendDefaultBorder = function(defaultBorder, customBorder) {\n
  if (customBorder.hasOwnProperty(\'border\')) {\n
    defaultBorder.border = customBorder.border;\n
  }\n
  if (customBorder.hasOwnProperty(\'top\')) {\n
    defaultBorder.top = customBorder.top;\n
  }\n
  if (customBorder.hasOwnProperty(\'right\')) {\n
    defaultBorder.right = customBorder.right;\n
  }\n
  if (customBorder.hasOwnProperty(\'bottom\')) {\n
    defaultBorder.bottom = customBorder.bottom;\n
  }\n
  if (customBorder.hasOwnProperty(\'left\')) {\n
    defaultBorder.left = customBorder.left;\n
  }\n
  return defaultBorder;\n
};\n
var removeBordersFromDom = function(borderClassName) {\n
  var borders = document.querySelectorAll("." + borderClassName);\n
  for (var i = 0; i < borders.length; i++) {\n
    if (borders[i]) {\n
      if (borders[i].nodeName != \'TD\') {\n
        var parent = borders[i].parentNode;\n
        if (parent.parentNode) {\n
          parent.parentNode.removeChild(parent);\n
        }\n
      }\n
    }\n
  }\n
};\n
var removeAllBorders = function(row, col) {\n
  var borderClassName = createClassName(row, col);\n
  removeBordersFromDom(borderClassName);\n
  this.removeCellMeta(row, col, \'borders\');\n
};\n
var setBorder = function(row, col, place, remove) {\n
  var bordersMeta = this.getCellMeta(row, col).borders;\n
  if (!bordersMeta || bordersMeta.border == undefined) {\n
    bordersMeta = createEmptyBorders(row, col);\n
  }\n
  if (remove) {\n
    bordersMeta[place] = createSingleEmptyBorder();\n
  } else {\n
    bordersMeta[place] = createDefaultCustomBorder();\n
  }\n
  this.setCellMeta(row, col, \'borders\', bordersMeta);\n
  var borderClassName = createClassName(row, col);\n
  removeBordersFromDom(borderClassName);\n
  insertBorderIntoSettings(bordersMeta);\n
  this.render();\n
};\n
var prepareBorder = function(range, place, remove) {\n
  if (range.from.row == range.to.row && range.from.col == range.to.col) {\n
    if (place == "noBorders") {\n
      removeAllBorders.call(this, range.from.row, range.from.col);\n
    } else {\n
      setBorder.call(this, range.from.row, range.from.col, place, remove);\n
    }\n
  } else {\n
    switch (place) {\n
      case "noBorders":\n
        for (var column = range.from.col; column <= range.to.col; column++) {\n
          for (var row = range.from.row; row <= range.to.row; row++) {\n
            removeAllBorders.call(this, row, column);\n
          }\n
        }\n
        break;\n
      case "top":\n
        for (var topCol = range.from.col; topCol <= range.to.col; topCol++) {\n
          setBorder.call(this, range.from.row, topCol, place, remove);\n
        }\n
        break;\n
      case "right":\n
        for (var rowRight = range.from.row; rowRight <= range.to.row; rowRight++) {\n
          setBorder.call(this, rowRight, range.to.col, place);\n
        }\n
        break;\n
      case "bottom":\n
        for (var bottomCol = range.from.col; bottomCol <= range.to.col; bottomCol++) {\n
          setBorder.call(this, range.to.row, bottomCol, place);\n
        }\n
        break;\n
      case "left":\n
        for (var rowLeft = range.from.row; rowLeft <= range.to.row; rowLeft++) {\n
          setBorder.call(this, rowLeft, range.from.col, place);\n
        }\n
        break;\n
    }\n
  }\n
};\n
var checkSelectionBorders = function(hot, direction) {\n
  var atLeastOneHasBorder = false;\n
  hot.getSelectedRange().forAll(function(r, c) {\n
    var metaBorders = hot.getCellMeta(r, c).borders;\n
    if (metaBorders) {\n
      if (direction) {\n
        if (!metaBorders[direction].hasOwnProperty(\'hide\')) {\n
          atLeastOneHasBorder = true;\n
          return false;\n
        }\n
      } else {\n
        atLeastOneHasBorder = true;\n
        return false;\n
      }\n
    }\n
  });\n
  return atLeastOneHasBorder;\n
};\n
var markSelected = function(label) {\n
  return "<span class=\'selected\'>" + String.fromCharCode(10003) + "</span>" + label;\n
};\n
var addBordersOptionsToContextMenu = function(defaultOptions) {\n
  if (!this.getSettings().customBorders) {\n
    return;\n
  }\n
  defaultOptions.items.push(Handsontable.ContextMenu.SEPARATOR);\n
  defaultOptions.items.push({\n
    key: \'borders\',\n
    name: \'Borders\',\n
    submenu: {items: {\n
        top: {\n
          name: function() {\n
            var label = "Top";\n
            var hasBorder = checkSelectionBorders(this, \'top\');\n
            if (hasBorder) {\n
              label = markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            var hasBorder = checkSelectionBorders(this, \'top\');\n
            prepareBorder.call(this, this.getSelectedRange(), \'top\', hasBorder);\n
          },\n
          disabled: false\n
        },\n
        right: {\n
          name: function() {\n
            var label = \'Right\';\n
            var hasBorder = checkSelectionBorders(this, \'right\');\n
            if (hasBorder) {\n
              label = markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            var hasBorder = checkSelectionBorders(this, \'right\');\n
            prepareBorder.call(this, this.getSelectedRange(), \'right\', hasBorder);\n
          },\n
          disabled: false\n
        },\n
        bottom: {\n
          name: function() {\n
            var label = \'Bottom\';\n
            var hasBorder = checkSelectionBorders(this, \'bottom\');\n
            if (hasBorder) {\n
              label = markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            var hasBorder = checkSelectionBorders(this, \'bottom\');\n
            prepareBorder.call(this, this.getSelectedRange(), \'bottom\', hasBorder);\n
          },\n
          disabled: false\n
        },\n
        left: {\n
          name: function() {\n
            var label = \'Left\';\n
            var hasBorder = checkSelectionBorders(this, \'left\');\n
            if (hasBorder) {\n
              label = markSelected(label);\n
            }\n
            return label;\n
          },\n
          callback: function() {\n
            var hasBorder = checkSelectionBorders(this, \'left\');\n
            prepareBorder.call(this, this.getSelectedRange(), \'left\', hasBorder);\n
          },\n
          disabled: false\n
        },\n
        remove: {\n
          name: \'Remove border(s)\',\n
          callback: function() {\n
            prepareBorder.call(this, this.getSelectedRange(), \'noBorders\');\n
          },\n
          disabled: function() {\n
            return !checkSelectionBorders(this);\n
          }\n
        }\n
      }}\n
  });\n
};\n
Handsontable.hooks.add(\'beforeInit\', init);\n
Handsontable.hooks.add(\'afterContextMenuDefaultOptions\', addBordersOptionsToContextMenu);\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  var customBorders = this.getSettings().customBorders;\n
  if (customBorders) {\n
    for (var i = 0; i < customBorders.length; i++) {\n
      if (customBorders[i].range) {\n
        prepareBorderFromCustomAddedRange.call(this, customBorders[i]);\n
      } else {\n
        prepareBorderFromCustomAdded.call(this, customBorders[i].row, customBorders[i].col, customBorders[i]);\n
      }\n
    }\n
    this.render();\n
    this.view.wt.draw(true);\n
  }\n
});\n
Handsontable.CustomBorders = CustomBorders;\n
\n
\n
//# \n
},{"./../../3rdparty/walkontable/src/cell/range.js":10,"./../../3rdparty/walkontable/src/selection.js":22,"./../../plugins.js":49}],59:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  DragToScroll: {get: function() {\n
      return DragToScroll;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
Handsontable.plugins.DragToScroll = DragToScroll;\n
function DragToScroll() {\n
  this.boundaries = null;\n
  this.callback = null;\n
}\n
DragToScroll.prototype.setBoundaries = function(boundaries) {\n
  this.boundaries = boundaries;\n
};\n
DragToScroll.prototype.setCallback = function(callback) {\n
  this.callback = callback;\n
};\n
DragToScroll.prototype.check = function(x, y) {\n
  var diffX = 0;\n
  var diffY = 0;\n
  if (y < this.boundaries.top) {\n
    diffY = y - this.boundaries.top;\n
  } else if (y > this.boundaries.bottom) {\n
    diffY = y - this.boundaries.bottom;\n
  }\n
  if (x < this.boundaries.left) {\n
    diffX = x - this.boundaries.left;\n
  } else if (x > this.boundaries.right) {\n
    diffX = x - this.boundaries.right;\n
  }\n
  this.callback(diffX, diffY);\n
};\n
var dragToScroll;\n
var instance;\n
if (typeof Handsontable !== \'undefined\') {\n
  var setupListening = function(instance) {\n
    instance.dragToScrollListening = false;\n
    var scrollHandler = instance.view.wt.wtTable.holder;\n
    dragToScroll = new DragToScroll();\n
    if (scrollHandler === window) {\n
      return;\n
    } else {\n
      dragToScroll.setBoundaries(scrollHandler.getBoundingClientRect());\n
    }\n
    dragToScroll.setCallback(function(scrollX, scrollY) {\n
      if (scrollX < 0) {\n
        scrollHandler.scrollLeft -= 50;\n
      } else if (scrollX > 0) {\n
        scrollHandler.scrollLeft += 50;\n
      }\n
      if (scrollY < 0) {\n
        scrollHandler.scrollTop -= 20;\n
      } else if (scrollY > 0) {\n
        scrollHandler.scrollTop += 20;\n
      }\n
    });\n
    instance.dragToScrollListening = true;\n
  };\n
}\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  var instance = this;\n
  var eventManager = eventManagerObject(this);\n
  eventManager.addEventListener(document, \'mouseup\', function() {\n
    instance.dragToScrollListening = false;\n
  });\n
  eventManager.addEventListener(document, \'mousemove\', function(event) {\n
    if (instance.dragToScrollListening) {\n
      dragToScroll.check(event.clientX, event.clientY);\n
    }\n
  });\n
});\n
Handsontable.hooks.add(\'afterDestroy\', function() {\n
  eventManagerObject(this).clear();\n
});\n
Handsontable.hooks.add(\'afterOnCellMouseDown\', function() {\n
  setupListening(this);\n
});\n
Handsontable.hooks.add(\'afterOnCellCornerMouseDown\', function() {\n
  setupListening(this);\n
});\n
Handsontable.plugins.DragToScroll = DragToScroll;\n
\n
\n
//# \n
},{"./../../eventManager.js":45,"./../../plugins.js":49}],60:[function(require,module,exports){\n
"use strict";\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
function Grouping(instance) {\n
  var groups = [];\n
  var item = {\n
    id: \'\',\n
    level: 0,\n
    hidden: 0,\n
    rows: [],\n
    cols: []\n
  };\n
  var counters = {\n
    rows: 0,\n
    cols: 0\n
  };\n
  var levels = {\n
    rows: 0,\n
    cols: 0\n
  };\n
  var hiddenRows = [];\n
  var hiddenCols = [];\n
  var classes = {\n
    \'groupIndicatorContainer\': \'htGroupIndicatorContainer\',\n
    \'groupIndicator\': function(direction) {\n
      return \'ht\' + direction + \'Group\';\n
    },\n
    \'groupStart\': \'htGroupStart\',\n
    \'collapseButton\': \'htCollapseButton\',\n
    \'expandButton\': \'htExpandButton\',\n
    \'collapseGroupId\': function(id) {\n
      return \'htCollapse-\' + id;\n
    },\n
    \'collapseFromLevel\': function(direction, level) {\n
      return \'htCollapse\' + direction + \'FromLevel-\' + level;\n
    },\n
    \'clickable\': \'clickable\',\n
    \'levelTrigger\': \'htGroupLevelTrigger\'\n
  };\n
  var compare = function(property, orderDirection) {\n
    return function(item1, item2) {\n
      return typeof(orderDirection) === \'undefined\' || orderDirection === \'asc\' ? item1[property] - item2[property] : item2[property] - item1[property];\n
    };\n
  };\n
  var range = function(from, to) {\n
    var arr = [];\n
    while (from <= to) {\n
      arr.push(from++);\n
    }\n
    return arr;\n
  };\n
  var getRangeGroups = function(dataType, from, to) {\n
    var cells = [],\n
        cell = {\n
          row: null,\n
          col: null\n
        };\n
    if (dataType == "cols") {\n
      while (from <= to) {\n
        cell = {\n
          row: -1,\n
          col: from++\n
        };\n
        cells.push(cell);\n
      }\n
    } else {\n
      while (from <= to) {\n
        cell = {\n
          row: from++,\n
          col: -1\n
        };\n
        cells.push(cell);\n
      }\n
    }\n
    var cellsGroups = getCellsGroups(cells),\n
        totalRows = 0,\n
        totalCols = 0;\n
    for (var i = 0; i < cellsGroups.length; i++) {\n
      totalRows += cellsGroups[i].filter(function(item) {\n
        return item[\'rows\'];\n
      }).length;\n
      totalCols += cellsGroups[i].filter(function(item) {\n
        return item[\'cols\'];\n
      }).length;\n
    }\n
    return {\n
      total: {\n
        rows: totalRows,\n
        cols: totalCols\n
      },\n
      groups: cellsGroups\n
    };\n
  };\n
  var getCellsGroups = function(cells) {\n
    var _groups = [];\n
    for (var i = 0; i < cells.length; i++) {\n
      _groups.push(getCellGroups(cells[i]));\n
    }\n
    return _groups;\n
  };\n
  var getCellGroups = function(coords, groupLevel, groupType) {\n
    var row = coords.row,\n
        col = coords.col;\n
    var tmpRow = (row === -1 ? 0 : row),\n
        tmpCol = (col === -1 ? 0 : col);\n
    var _groups = [];\n
    for (var i = 0; i < groups.length; i++) {\n
      var group = groups[i],\n
          id = group[\'id\'],\n
          level = group[\'level\'],\n
          rows = group[\'rows\'] || [],\n
          cols = group[\'cols\'] || [];\n
      if (_groups.indexOf(id) === -1) {\n
        if (rows.indexOf(tmpRow) !== -1 || cols.indexOf(tmpCol) !== -1) {\n
          _groups.push(group);\n
        }\n
      }\n
    }\n
    if (col === -1) {\n
      _groups = _groups.concat(getColGroups());\n
    } else if (row === -1) {\n
      _groups = _groups.concat(getRowGroups());\n
    }\n
    if (groupLevel) {\n
      _groups = _groups.filter(function(item) {\n
        return item[\'level\'] === groupLevel;\n
      });\n
    }\n
    if (groupType) {\n
      if (groupType === \'cols\') {\n
        _groups = _groups.filter(function(item) {\n
          return item[\'cols\'];\n
        });\n
      } else if (groupType === \'rows\') {\n
        _groups = _groups.filter(function(item) {\n
          return item[\'rows\'];\n
        });\n
      }\n
    }\n
    var tmp = [];\n
    return _groups.filter(function(item) {\n
      if (tmp.indexOf(item.id) === -1) {\n
        tmp.push(item.id);\n
        return item;\n
      }\n
    });\n
  };\n
  var getGroupById = function(id) {\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (groups[i].id == id) {\n
        return groups[i];\n
      }\n
    }\n
    return false;\n
  };\n
  var getGroupByRowAndLevel = function(row, level) {\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (groups[i].level == level && groups[i].rows && groups[i].rows.indexOf(row) > -1) {\n
        return groups[i];\n
      }\n
    }\n
    return false;\n
  };\n
  var getGroupByColAndLevel = function(col, level) {\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (groups[i].level == level && groups[i].cols && groups[i].cols.indexOf(col) > -1) {\n
        return groups[i];\n
      }\n
    }\n
    return false;\n
  };\n
  var getColGroups = function() {\n
    var result = [];\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (Array.isArray(groups[i][\'cols\'])) {\n
        result.push(groups[i]);\n
      }\n
    }\n
    return result;\n
  };\n
  var getColGroupsByLevel = function(level) {\n
    var result = [];\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (groups[i][\'cols\'] && groups[i][\'level\'] === level) {\n
        result.push(groups[i]);\n
      }\n
    }\n
    return result;\n
  };\n
  var getRowGroups = function() {\n
    var result = [];\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (Array.isArray(groups[i][\'rows\'])) {\n
        result.push(groups[i]);\n
      }\n
    }\n
    return result;\n
  };\n
  var getRowGroupsByLevel = function(level) {\n
    var result = [];\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      if (groups[i][\'rows\'] && groups[i][\'level\'] === level) {\n
        result.push(groups[i]);\n
      }\n
    }\n
    return result;\n
  };\n
  var getLastLevelColsInRange = function(rangeGroups) {\n
    var level = 0;\n
    if (rangeGroups.length) {\n
      rangeGroups.forEach(function(items) {\n
        items = items.filter(function(item) {\n
          return item[\'cols\'];\n
        });\n
        if (items.length) {\n
          var sortedGroup = items.sort(compare(\'level\', \'desc\')),\n
              lastLevel = sortedGroup[0].level;\n
          if (level < lastLevel) {\n
            level = lastLevel;\n
          }\n
        }\n
      });\n
    }\n
    return level;\n
  };\n
  var getLastLevelRowsInRange = function(rangeGroups) {\n
    var level = 0;\n
    if (rangeGroups.length) {\n
      rangeGroups.forEach(function(items) {\n
        items = items.filter(function(item) {\n
          return item[\'rows\'];\n
        });\n
        if (items.length) {\n
          var sortedGroup = items.sort(compare(\'level\', \'desc\')),\n
              lastLevel = sortedGroup[0].level;\n
          if (level < lastLevel) {\n
            level = lastLevel;\n
          }\n
        }\n
      });\n
    }\n
    return level;\n
  };\n
  var groupCols = function(from, to) {\n
    var rangeGroups = getRangeGroups("cols", from, to),\n
        lastLevel = getLastLevelColsInRange(rangeGroups.groups);\n
    if (lastLevel === levels.cols) {\n
      levels.cols++;\n
    } else if (lastLevel > levels.cols) {\n
      levels.cols = lastLevel + 1;\n
    }\n
    if (!counters.cols) {\n
      counters.cols = getColGroups().length;\n
    }\n
    counters.cols++;\n
    groups.push({\n
      id: \'c\' + counters.cols,\n
      level: lastLevel + 1,\n
      cols: range(from, to),\n
      hidden: 0\n
    });\n
  };\n
  var groupRows = function(from, to) {\n
    var rangeGroups = getRangeGroups("rows", from, to),\n
        lastLevel = getLastLevelRowsInRange(rangeGroups.groups);\n
    levels.rows = Math.max(levels.rows, lastLevel + 1);\n
    if (!counters.rows) {\n
      counters.rows = getRowGroups().length;\n
    }\n
    counters.rows++;\n
    groups.push({\n
      id: \'r\' + counters.rows,\n
      level: lastLevel + 1,\n
      rows: range(from, to),\n
      hidden: 0\n
    });\n
  };\n
  var showHideGroups = function(hidden, groups) {\n
    var level;\n
    for (var i = 0,\n
        groupsLength = groups.length; i < groupsLength; i++) {\n
      groups[i].hidden = hidden;\n
      level = groups[i].level;\n
      if (!hiddenRows[level]) {\n
        hiddenRows[level] = [];\n
      }\n
      if (!hiddenCols[level]) {\n
        hiddenCols[level] = [];\n
      }\n
      if (groups[i].rows) {\n
        for (var j = 0,\n
            rowsLength = groups[i].rows.length; j < rowsLength; j++) {\n
          if (hidden > 0) {\n
            hiddenRows[level][groups[i].rows[j]] = true;\n
          } else {\n
            hiddenRows[level][groups[i].rows[j]] = void 0;\n
          }\n
        }\n
      } else if (groups[i].cols) {\n
        for (var j = 0,\n
            colsLength = groups[i].cols.length; j < colsLength; j++) {\n
          if (hidden > 0) {\n
            hiddenCols[level][groups[i].cols[j]] = true;\n
          } else {\n
            hiddenCols[level][groups[i].cols[j]] = void 0;\n
          }\n
        }\n
      }\n
    }\n
  };\n
  var nextIndexSharesLevel = function(dimension, currentPosition, level, currentGroupId) {\n
    var nextCellGroupId,\n
        levelsByOrder;\n
    switch (dimension) {\n
      case \'rows\':\n
        nextCellGroupId = getGroupByRowAndLevel(currentPosition + 1, level).id;\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByRows();\n
        break;\n
      case \'cols\':\n
        nextCellGroupId = getGroupByColAndLevel(currentPosition + 1, level).id;\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByCols();\n
        break;\n
    }\n
    return !!(levelsByOrder[currentPosition + 1] && levelsByOrder[currentPosition + 1].indexOf(level) > -1 && currentGroupId == nextCellGroupId);\n
  };\n
  var previousIndexSharesLevel = function(dimension, currentPosition, level, currentGroupId) {\n
    var previousCellGroupId,\n
        levelsByOrder;\n
    switch (dimension) {\n
      case \'rows\':\n
        previousCellGroupId = getGroupByRowAndLevel(currentPosition - 1, level).id;\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByRows();\n
        break;\n
      case \'cols\':\n
        previousCellGroupId = getGroupByColAndLevel(currentPosition - 1, level).id;\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByCols();\n
        break;\n
    }\n
    return !!(levelsByOrder[currentPosition - 1] && levelsByOrder[currentPosition - 1].indexOf(level) > -1 && currentGroupId == previousCellGroupId);\n
  };\n
  var isLastIndexOfTheLine = function(dimension, index, level, currentGroupId) {\n
    if (index === 0) {\n
      return false;\n
    }\n
    var levelsByOrder,\n
        entriesLength,\n
        previousSharesLevel = previousIndexSharesLevel(dimension, index, level, currentGroupId),\n
        nextSharesLevel = nextIndexSharesLevel(dimension, index, level, currentGroupId),\n
        nextIsHidden = false;\n
    switch (dimension) {\n
      case \'rows\':\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByRows();\n
        entriesLength = instance.countRows();\n
        for (var i = 0; i <= levels.rows; i++) {\n
          if (hiddenRows[i] && hiddenRows[i][index + 1]) {\n
            nextIsHidden = true;\n
            break;\n
          }\n
        }\n
        break;\n
      case \'cols\':\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByCols();\n
        entriesLength = instance.countCols();\n
        for (var i = 0; i <= levels.cols; i++) {\n
          if (hiddenCols[i] && hiddenCols[i][index + 1]) {\n
            nextIsHidden = true;\n
            break;\n
          }\n
        }\n
        break;\n
    }\n
    if (previousSharesLevel) {\n
      if (index == entriesLength - 1) {\n
        return true;\n
      } else if (!nextSharesLevel || (nextSharesLevel && nextIsHidden)) {\n
        return true;\n
      } else if (!levelsByOrder[index + 1]) {\n
        return true;\n
      }\n
    }\n
    return false;\n
  };\n
  var isLastHidden = function(dataType) {\n
    var levelAmount;\n
    switch (dataType) {\n
      case \'rows\':\n
        levelAmount = levels.rows;\n
        for (var j = 0; j <= levelAmount; j++) {\n
          if (hiddenRows[j] && hiddenRows[j][instance.countRows() - 1]) {\n
            return true;\n
          }\n
        }\n
        break;\n
      case \'cols\':\n
        levelAmount = levels.cols;\n
        for (var j = 0; j <= levelAmount; j++) {\n
          if (hiddenCols[j] && hiddenCols[j][instance.countCols() - 1]) {\n
            return true;\n
          }\n
        }\n
        break;\n
    }\n
    return false;\n
  };\n
  var isFirstIndexOfTheLine = function(dimension, index, level, currentGroupId) {\n
    var levelsByOrder,\n
        entriesLength,\n
        currentGroup = getGroupById(currentGroupId),\n
        previousAreHidden = false,\n
        arePreviousHidden = function(dimension) {\n
          var hidden = false,\n
              hiddenArr = dimension == \'rows\' ? hiddenRows : hiddenCols;\n
          for (var i = 0; i <= levels[dimension]; i++) {\n
            tempInd = index;\n
            while (currentGroup[dimension].indexOf(tempInd) > -1) {\n
              hidden = !!(hiddenArr[i] && hiddenArr[i][tempInd]);\n
              tempInd--;\n
            }\n
            if (hidden) {\n
              break;\n
            }\n
          }\n
          return hidden;\n
        },\n
        previousSharesLevel = previousIndexSharesLevel(dimension, index, level, currentGroupId),\n
        nextSharesLevel = nextIndexSharesLevel(dimension, index, level, currentGroupId),\n
        tempInd;\n
    switch (dimension) {\n
      case \'rows\':\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByRows();\n
        entriesLength = instance.countRows();\n
        previousAreHidden = arePreviousHidden(dimension);\n
        break;\n
      case \'cols\':\n
        levelsByOrder = Handsontable.Grouping.getGroupLevelsByCols();\n
        entriesLength = instance.countCols();\n
        previousAreHidden = arePreviousHidden(dimension);\n
        break;\n
    }\n
    if (index == entriesLength - 1) {\n
      return false;\n
    } else if (index === 0) {\n
      if (nextSharesLevel) {\n
        return true;\n
      }\n
    } else if (!previousSharesLevel || (previousSharesLevel && previousAreHidden)) {\n
      if (nextSharesLevel) {\n
        return true;\n
      }\n
    } else if (!levelsByOrder[index - 1]) {\n
      if (nextSharesLevel) {\n
        return true;\n
      }\n
    }\n
    return false;\n
  };\n
  var addGroupExpander = function(dataType, index, level, id, elem) {\n
    var previousIndexGroupId;\n
    switch (dataType) {\n
      case \'rows\':\n
        previousIndexGroupId = getGroupByRowAndLevel(index - 1, level).id;\n
        break;\n
      case \'cols\':\n
        previousIndexGroupId = getGroupByColAndLevel(index - 1, level).id;\n
        break;\n
    }\n
    if (!previousIndexGroupId) {\n
      return null;\n
    }\n
    if (index > 0) {\n
      if (previousIndexSharesLevel(dataType, index - 1, level, previousIndexGroupId) && previousIndexGroupId != id) {\n
        var expanderButton = document.createElement(\'DIV\');\n
        dom.addClass(expanderButton, classes.expandButton);\n
        expanderButton.id = \'htExpand-\' + previousIndexGroupId;\n
        expanderButton.appendChild(document.createTextNode(\'+\'));\n
        expanderButton.setAttribute(\'data-level\', level);\n
        expanderButton.setAttribute(\'data-type\', dataType);\n
        expanderButton.setAttribute(\'data-hidden\', "1");\n
        elem.appendChild(expanderButton);\n
        return expanderButton;\n
      }\n
    }\n
    return null;\n
  };\n
  var isCollapsed = function(currentPosition) {\n
    var rowGroups = getRowGroups(),\n
        colGroups = getColGroups();\n
    for (var i = 0,\n
        rowGroupsCount = rowGroups.length; i < rowGroupsCount; i++) {\n
      if (rowGroups[i].rows.indexOf(currentPosition.row) > -1 && rowGroups[i].hidden) {\n
        return true;\n
      }\n
    }\n
    if (currentPosition.col === null) {\n
      return false;\n
    }\n
    for (var i = 0,\n
        colGroupsCount = colGroups.length; i < colGroupsCount; i++) {\n
      if (colGroups[i].cols.indexOf(currentPosition.col) > -1 && colGroups[i].hidden) {\n
        return true;\n
      }\n
    }\n
    return false;\n
  };\n
  return {\n
    getGroups: function() {\n
      return groups;\n
    },\n
    getLevels: function() {\n
      return levels;\n
    },\n
    instance: instance,\n
    baseSpareRows: instance.getSettings().minSpareRows,\n
    baseSpareCols: instance.getSettings().minSpareCols,\n
    getRowGroups: getRowGroups,\n
    getColGroups: getColGroups,\n
    init: function() {\n
      var groupsSetting = instance.getSettings().groups;\n
      if (groupsSetting) {\n
        if (Array.isArray(groupsSetting)) {\n
          Handsontable.Grouping.initGroups(groupsSetting);\n
        }\n
      }\n
    },\n
    initGroups: function(initialGroups) {\n
      var that = this;\n
      groups = [];\n
      initialGroups.forEach(function(item) {\n
        var _group = [],\n
            isRow = false,\n
            isCol = false;\n
        if (Array.isArray(item.rows)) {\n
          _group = item.rows;\n
          isRow = true;\n
        } else if (Array.isArray(item.cols)) {\n
          _group = item.cols;\n
          isCol = true;\n
        }\n
        var from = _group[0],\n
            to = _group[_group.length - 1];\n
        if (isRow) {\n
          groupRows(from, to);\n
        } else if (isCol) {\n
          groupCols(from, to);\n
        }\n
      });\n
    },\n
    resetGroups: function() {\n
      groups = [];\n
      counters = {\n
        rows: 0,\n
        cols: 0\n
      };\n
      levels = {\n
        rows: 0,\n
        cols: 0\n
      };\n
      var allOccurrences;\n
      for (var i in classes) {\n
        if (typeof classes[i] != \'function\') {\n
          allOccurrences = document.querySelectorAll(\'.\' + classes[i]);\n
          for (var j = 0,\n
              occurrencesLength = allOccurrences.length; j < occurrencesLength; j++) {\n
            dom.removeClass(allOccurrences[j], classes[i]);\n
          }\n
        }\n
      }\n
      var otherClasses = [\'htGroupColClosest\', \'htGroupCol\'];\n
      for (var i = 0,\n
          otherClassesLength = otherClasses.length; i < otherClassesLength; i++) {\n
        allOccurrences = document.querySelectorAll(\'.\' + otherClasses[i]);\n
        for (var j = 0,\n
            occurrencesLength = allOccurrences.length; j < occurrencesLength; j++) {\n
          dom.removeClass(allOccurrences[j], otherClasses[i]);\n
        }\n
      }\n
    },\n
    updateGroups: function() {\n
      var groupSettings = this.getSettings().groups;\n
      Handsontable.Grouping.resetGroups();\n
      Handsontable.Grouping.initGroups(groupSettings);\n
    },\n
    afterGetRowHeader: function(row, TH) {\n
      var currentRowHidden = false;\n
      for (var i = 0,\n
          levels = hiddenRows.length; i < levels; i++) {\n
        if (hiddenRows[i] && hiddenRows[i][row] === true) {\n
          currentRowHidden = true;\n
        }\n
      }\n
      if (currentRowHidden) {\n
        dom.addClass(TH.parentNode, \'hidden\');\n
      } else if (!currentRowHidden && dom.hasClass(TH.parentNode, \'hidden\')) {\n
        dom.removeClass(TH.parentNode, \'hidden\');\n
      }\n
    },\n
    afterGetColHeader: function(col, TH) {\n
      var rowHeaders = this.view.wt.wtSettings.getSetting(\'rowHeaders\').length,\n
          thisColgroup = instance.rootElement.querySelectorAll(\'colgroup col:nth-child(\' + parseInt(col + rowHeaders + 1, 10) + \')\');\n
      if (thisColgroup.length === 0) {\n
        return;\n
      }\n
      var currentColHidden = false;\n
      for (var i = 0,\n
          levels = hiddenCols.length; i < levels; i++) {\n
        if (hiddenCols[i] && hiddenCols[i][col] === true) {\n
          currentColHidden = true;\n
        }\n
      }\n
      if (currentColHidden) {\n
        for (var i = 0,\n
            colsAmount = thisColgroup.length; i < colsAmount; i++) {\n
          dom.addClass(thisColgroup[i], \'hidden\');\n
        }\n
      } else if (!currentColHidden && dom.hasClass(thisColgroup[0], \'hidden\')) {\n
        for (var i = 0,\n
            colsAmount = thisColgroup.length; i < colsAmount; i++) {\n
          dom.removeClass(thisColgroup[i], \'hidden\');\n
        }\n
      }\n
    },\n
    groupIndicatorsFactory: function(renderersArr, direction) {\n
      var groupsLevelsList,\n
          getCurrentLevel,\n
          getCurrentGroupId,\n
          dataType,\n
          getGroupByIndexAndLevel,\n
          headersType,\n
          currentHeaderModifier,\n
          createLevelTriggers;\n
      switch (direction) {\n
        case \'horizontal\':\n
          groupsLevelsList = Handsontable.Grouping.getGroupLevelsByCols();\n
          getCurrentLevel = function(elem) {\n
            return Array.prototype.indexOf.call(elem.parentNode.parentNode.childNodes, elem.parentNode) + 1;\n
          };\n
          getCurrentGroupId = function(col, level) {\n
            return getGroupByColAndLevel(col, level).id;\n
          };\n
          dataType = \'cols\';\n
          getGroupByIndexAndLevel = function(col, level) {\n
            return getGroupByColAndLevel(col - 1, level);\n
          };\n
          headersType = "columnHeaders";\n
          currentHeaderModifier = function(headerRenderers) {\n
            if (headerRenderers.length === 1) {\n
              var oldFn = headerRenderers[0];\n
              headerRenderers[0] = function(index, elem, level) {\n
                if (index < -1) {\n
                  makeGroupIndicatorsForLevel()(index, elem, level);\n
                } else {\n
                  dom.removeClass(elem, classes.groupIndicatorContainer);\n
                  oldFn(index, elem, level);\n
                }\n
              };\n
            }\n
            return function() {\n
              return headerRenderers;\n
            };\n
          };\n
          createLevelTriggers = true;\n
          break;\n
        case \'vertical\':\n
          groupsLevelsList = Handsontable.Grouping.getGroupLevelsByRows();\n
          getCurrentLevel = function(elem) {\n
            return dom.index(elem) + 1;\n
          };\n
          getCurrentGroupId = function(row, level) {\n
            return getGroupByRowAndLevel(row, level).id;\n
          };\n
          dataType = \'rows\';\n
          getGroupByIndexAndLevel = function(row, level) {\n
            return getGroupByRowAndLevel(row - 1, level);\n
          };\n
          headersType = "rowHeaders";\n
          currentHeaderModifier = function(headerRenderers) {\n
            return headerRenderers;\n
          };\n
          break;\n
      }\n
      var createButton = function(parent) {\n
        var button = document.createElement(\'div\');\n
        parent.appendChild(button);\n
        return {\n
          button: button,\n
          addClass: function(className) {\n
            dom.addClass(button, className);\n
          }\n
        };\n
      };\n
      var makeGroupIndicatorsForLevel = function() {\n
        var directionClassname = direction.charAt(0).toUpperCase() + direction.slice(1);\n
        return function(index, elem, level) {\n
          level++;\n
          var child,\n
              collapseButton;\n
          while (child = elem.lastChild) {\n
            elem.removeChild(child);\n
          }\n
          dom.addClass(elem, classes.groupIndicatorContainer);\n
          var currentGroupId = getCurrentGroupId(index, level);\n
          if (index > -1 && (groupsLevelsList[index] && groupsLevelsList[index].indexOf(level) > -1)) {\n
            collapseButton = createButton(elem);\n
            collapseButton.addClass(classes.groupIndicator(directionClassname));\n
            if (isFirstIndexOfTheLine(dataType, index, level, currentGroupId)) {\n
              collapseButton.addClass(classes.groupStart);\n
            }\n
            if (isLastIndexOfTheLine(dataType, index, level, currentGroupId)) {\n
              collapseButton.button.appendChild(document.createTextNode(\'-\'));\n
              collapseButton.addClass(classes.collapseButton);\n
              collapseButton.button.id = classes.collapseGroupId(currentGroupId);\n
              collapseButton.button.setAttribute(\'data-level\', level);\n
              collapseButton.button.setAttribute(\'data-type\', dataType);\n
            }\n
          }\n
          if (createLevelTriggers) {\n
            var rowInd = dom.index(elem.parentNode);\n
            if (index === -1 || (index < -1 && rowInd === Handsontable.Grouping.getLevels().cols + 1) || (rowInd === 0 && Handsontable.Grouping.getLevels().cols === 0)) {\n
              collapseButton = createButton(elem);\n
              collapseButton.addClass(classes.levelTrigger);\n
              if (index === -1) {\n
                collapseButton.button.id = classes.collapseFromLevel("Cols", level);\n
                collapseButton.button.appendChild(document.createTextNode(level));\n
              } else if (index < -1 && rowInd === Handsontable.Grouping.getLevels().cols + 1 || (rowInd === 0 && Handsontable.Grouping.getLevels().cols === 0)) {\n
                var colInd = dom.index(elem) + 1;\n
                collapseButton.button.id = classes.collapseFromLevel("Rows", colInd);\n
                collapseButton.button.appendChild(document.createTextNode(colInd));\n
              }\n
            }\n
          }\n
          var expanderButton = addGroupExpander(dataType, index, level, currentGroupId, elem);\n
          if (index > 0) {\n
            var previousGroupObj = getGroupByIndexAndLevel(index - 1, level);\n
            if (expanderButton && previousGroupObj.hidden) {\n
              dom.addClass(expanderButton, classes.clickable);\n
            }\n
          }\n
          updateHeaderWidths();\n
        };\n
      };\n
      renderersArr = currentHeaderModifier(renderersArr);\n
      if (counters[dataType] > 0) {\n
        for (var i = 0; i < levels[dataType] + 1; i++) {\n
          if (!Array.isArray(renderersArr)) {\n
            renderersArr = typeof renderersArr === \'function\' ? renderersArr() : new Array(renderersArr);\n
          }\n
          renderersArr.unshift(makeGroupIndicatorsForLevel());\n
        }\n
      }\n
    },\n
    getGroupLevelsByRows: function() {\n
      var rowGroups = getRowGroups(),\n
          result = [];\n
      for (var i = 0,\n
          groupsLength = rowGroups.length; i < groupsLength; i++) {\n
        if (rowGroups[i].rows) {\n
          for (var j = 0,\n
              groupRowsLength = rowGroups[i].rows.length; j < groupRowsLength; j++) {\n
            if (!result[rowGroups[i].rows[j]]) {\n
              result[rowGroups[i].rows[j]] = [];\n
            }\n
            result[rowGroups[i].rows[j]].push(rowGroups[i].level);\n
          }\n
        }\n
      }\n
      return result;\n
    },\n
    getGroupLevelsByCols: function() {\n
      var colGroups = getColGroups(),\n
          result = [];\n
      for (var i = 0,\n
          groupsLength = colGroups.length; i < groupsLength; i++) {\n
        if (colGroups[i].cols) {\n
          for (var j = 0,\n
              groupColsLength = colGroups[i].cols.length; j < groupColsLength; j++) {\n
            if (!result[colGroups[i].cols[j]]) {\n
              result[colGroups[i].cols[j]] = [];\n
            }\n
            result[colGroups[i].cols[j]].push(colGroups[i].level);\n
          }\n
        }\n
      }\n
      return result;\n
    },\n
    toggleGroupVisibility: function(event, coords, TD) {\n
      if (dom.hasClass(event.target, classes.expandButton) || dom.hasClass(event.target, classes.collapseButton) || dom.hasClass(event.target, classes.levelTrigger)) {\n
        var element = event.target,\n
            elemIdSplit = element.id.split(\'-\');\n
        var groups = [],\n
            id,\n
            level,\n
            type,\n
            hidden;\n
        var prepareGroupData = function(componentElement) {\n
          if (componentElement) {\n
            element = componentElement;\n
          }\n
          elemIdSplit = element.id.split(\'-\');\n
          id = elemIdSplit[1];\n
          level = parseInt(element.getAttribute(\'data-level\'), 10);\n
          type = element.getAttribute(\'data-type\');\n
          hidden = parseInt(element.getAttribute(\'data-hidden\'));\n
          if (isNaN(hidden)) {\n
            hidden = 1;\n
          } else {\n
            hidden = (hidden ? 0 : 1);\n
          }\n
          element.setAttribute(\'data-hidden\', hidden.toString());\n
          groups.push(getGroupById(id));\n
        };\n
        if (element.className.indexOf(classes.levelTrigger) > -1) {\n
          var groupsInLevel,\n
              groupsToExpand = [],\n
              groupsToCollapse = [],\n
              levelType = element.id.indexOf("Rows") > -1 ? "rows" : "cols";\n
          for (var i = 1,\n
              levelsCount = levels[levelType]; i <= levelsCount; i++) {\n
            groupsInLevel = levelType == "rows" ? getRowGroupsByLevel(i) : getColGroupsByLevel(i);\n
            if (i >= parseInt(elemIdSplit[1], 10)) {\n
              for (var j = 0,\n
                  groupCount = groupsInLevel.length; j < groupCount; j++) {\n
                groupsToCollapse.push(groupsInLevel[j]);\n
              }\n
            } else {\n
              for (var j = 0,\n
                  groupCount = groupsInLevel.length; j < groupCount; j++) {\n
                groupsToExpand.push(groupsInLevel[j]);\n
              }\n
            }\n
          }\n
          showHideGroups(true, groupsToCollapse);\n
          showHideGroups(false, groupsToExpand);\n
        } else {\n
          prepareGroupData();\n
          showHideGroups(hidden, groups);\n
        }\n
        type = type || levelType;\n
        var lastHidden = isLastHidden(type),\n
            typeUppercase = type.charAt(0).toUpperCase() + type.slice(1),\n
            spareElements = Handsontable.Grouping[\'baseSpare\' + typeUppercase];\n
        if (lastHidden) {\n
          if (spareElements == 0) {\n
            instance.alter(\'insert_\' + type.slice(0, -1), instance[\'count\' + typeUppercase]());\n
            Handsontable.Grouping["dummy" + type.slice(0, -1)] = true;\n
          }\n
        } else {\n
          if (spareElements == 0) {\n
            if (Handsontable.Grouping["dummy" + type.slice(0, -1)]) {\n
              instance.alter(\'remove_\' + type.slice(0, -1), instance[\'count\' + typeUppercase]() - 1);\n
              Handsontable.Grouping["dummy" + type.slice(0, -1)] = false;\n
            }\n
          }\n
        }\n
        instance.render();\n
        event.stopImmediatePropagation();\n
      }\n
    },\n
    modifySelectionFactory: function(position) {\n
      var instance = this.instance;\n
      var currentlySelected,\n
          nextPosition = new WalkontableCellCoords(0, 0),\n
          nextVisible = function(direction, currentPosition) {\n
            var updateDelta = 0;\n
            switch (direction) {\n
              case \'down\':\n
                while (isCollapsed(currentPosition)) {\n
                  updateDelta++;\n
                  currentPosition.row += 1;\n
                }\n
                break;\n
              case \'up\':\n
                while (isCollapsed(currentPosition)) {\n
                  updateDelta--;\n
                  currentPosition.row -= 1;\n
                }\n
                break;\n
              case \'right\':\n
                while (isCollapsed(currentPosition)) {\n
                  updateDelta++;\n
                  currentPosition.col += 1;\n
                }\n
                break;\n
              case \'left\':\n
                while (isCollapsed(currentPosition)) {\n
                  updateDelta--;\n
                  currentPosition.col -= 1;\n
                }\n
                break;\n
            }\n
            return updateDelta;\n
          },\n
          updateDelta = function(delta, nextPosition) {\n
            if (delta.row > 0) {\n
              if (isCollapsed(nextPosition)) {\n
                delta.row += nextVisible(\'down\', nextPosition);\n
              }\n
            } else if (delta.row < 0) {\n
              if (isCollapsed(nextPosition)) {\n
                delta.row += nextVisible(\'up\', nextPosition);\n
              }\n
            }\n
            if (delta.col > 0) {\n
              if (isCollapsed(nextPosition)) {\n
                delta.col += nextVisible(\'right\', nextPosition);\n
              }\n
            } else if (delta.col < 0) {\n
              if (isCollapsed(nextPosition)) {\n
                delta.col += nextVisible(\'left\', nextPosition);\n
              }\n
            }\n
          };\n
      switch (position) {\n
        case \'start\':\n
          return function(delta) {\n
            currentlySelected = instance.getSelected();\n
            nextPosition.row = currentlySelected[0] + delta.row;\n
            nextPosition.col = currentlySelected[1] + delta.col;\n
            updateDelta(delta, nextPosition);\n
          };\n
          break;\n
        case \'end\':\n
          return function(delta) {\n
            currentlySelected = instance.getSelected();\n
            nextPosition.row = currentlySelected[2] + delta.row;\n
            nextPosition.col = currentlySelected[3] + delta.col;\n
            updateDelta(delta, nextPosition);\n
          };\n
          break;\n
      }\n
    },\n
    modifyRowHeight: function(height, row) {\n
      if (instance.view.wt.wtTable.rowFilter && isCollapsed({\n
        row: row,\n
        col: null\n
      })) {\n
        return 0;\n
      }\n
    },\n
    validateGroups: function() {\n
      var areRangesOverlapping = function(a, b) {\n
        if ((a[0] < b[0] && a[1] < b[1] && b[0] <= a[1]) || (a[0] > b[0] && b[1] < a[1] && a[0] <= b[1])) {\n
          return true;\n
        }\n
      };\n
      var configGroups = instance.getSettings().groups,\n
          cols = [],\n
          rows = [];\n
      for (var i = 0,\n
          groupsLength = configGroups.length; i < groupsLength; i++) {\n
        if (configGroups[i].rows) {\n
          if (configGroups[i].rows.length === 1) {\n
            throw new Error("Grouping error:  Group {" + configGroups[i].rows[0] + "} is invalid. Cannot define single-entry groups.");\n
            return false;\n
          } else if (configGroups[i].rows.length === 0) {\n
            throw new Error("Grouping error:  Cannot define empty groups.");\n
            return false;\n
          }\n
          rows.push(configGroups[i].rows);\n
          for (var j = 0,\n
              rowsLength = rows.length; j < rowsLength; j++) {\n
            if (areRangesOverlapping(configGroups[i].rows, rows[j])) {\n
              throw new Error("Grouping error:  ranges {" + configGroups[i].rows[0] + ", " + configGroups[i].rows[1] + "} and {" + rows[j][0] + ", " + rows[j][1] + "} are overlapping.");\n
              return false;\n
            }\n
          }\n
        } else if (configGroups[i].cols) {\n
          if (configGroups[i].cols.length === 1) {\n
            throw new Error("Grouping error:  Group {" + configGroups[i].cols[0] + "} is invalid. Cannot define single-entry groups.");\n
            return false;\n
          } else if (configGroups[i].cols.length === 0) {\n
            throw new Error("Grouping error:  Cannot define empty groups.");\n
            return false;\n
          }\n
          cols.push(configGroups[i].cols);\n
          for (var j = 0,\n
              colsLength = cols.length; j < colsLength; j++) {\n
            if (areRangesOverlapping(configGroups[i].cols, cols[j])) {\n
              throw new Error("Grouping error:  ranges {" + configGroups[i].cols[0] + ", " + configGroups[i].cols[1] + "} and {" + cols[j][0] + ", " + cols[j][1] + "} are overlapping.");\n
              return false;\n
            }\n
          }\n
        }\n
      }\n
      return true;\n
    },\n
    afterGetRowHeaderRenderers: function(arr) {\n
      Handsontable.Grouping.groupIndicatorsFactory(arr, \'vertical\');\n
    },\n
    afterGetColumnHeaderRenderers: function(arr) {\n
      Handsontable.Grouping.groupIndicatorsFactory(arr, \'horizontal\');\n
    },\n
    hookProxy: function(fn, arg) {\n
      return function() {\n
        if (instance.getSettings().groups) {\n
          return arg ? Handsontable.Grouping[fn](arg).apply(this, arguments) : Handsontable.Grouping[fn].apply(this, arguments);\n
        } else {\n
          return void 0;\n
        }\n
      };\n
    }\n
  };\n
}\n
Grouping.prototype.beforeInit = function() {};\n
var init = function() {\n
  var instance = this,\n
      groupingSetting = !!(instance.getSettings().groups);\n
  if (groupingSetting) {\n
    var headerUpdates = {};\n
    Handsontable.Grouping = new Grouping(instance);\n
    if (!instance.getSettings().rowHeaders) {\n
      headerUpdates.rowHeaders = true;\n
    }\n
    if (!instance.getSettings().colHeaders) {\n
      headerUpdates.colHeaders = true;\n
    }\n
    if (headerUpdates.colHeaders || headerUpdates.rowHeaders) {\n
      instance.updateSettings(headerUpdates);\n
    }\n
    var groupConfigValid = Handsontable.Grouping.validateGroups();\n
    if (!groupConfigValid) {\n
      return;\n
    }\n
    instance.addHook(\'beforeInit\', Handsontable.Grouping.hookProxy(\'init\'));\n
    instance.addHook(\'afterUpdateSettings\', Handsontable.Grouping.hookProxy(\'updateGroups\'));\n
    instance.addHook(\'afterGetColumnHeaderRenderers\', Handsontable.Grouping.hookProxy(\'afterGetColumnHeaderRenderers\'));\n
    instance.addHook(\'afterGetRowHeaderRenderers\', Handsontable.Grouping.hookProxy(\'afterGetRowHeaderRenderers\'));\n
    instance.addHook(\'afterGetRowHeader\', Handsontable.Grouping.hookProxy(\'afterGetRowHeader\'));\n
    instance.addHook(\'afterGetColHeader\', Handsontable.Grouping.hookProxy(\'afterGetColHeader\'));\n
    instance.addHook(\'beforeOnCellMouseDown\', Handsontable.Grouping.hookProxy(\'toggleGroupVisibility\'));\n
    instance.addHook(\'modifyTransformStart\', Handsontable.Grouping.hookProxy(\'modifySelectionFactory\', \'start\'));\n
    instance.addHook(\'modifyTransformEnd\', Handsontable.Grouping.hookProxy(\'modifySelectionFactory\', \'end\'));\n
    instance.addHook(\'modifyRowHeight\', Handsontable.Grouping.hookProxy(\'modifyRowHeight\'));\n
  }\n
};\n
var updateHeaderWidths = function() {\n
  var colgroups = document.querySelectorAll(\'colgroup\');\n
  for (var i = 0,\n
      colgroupsLength = colgroups.length; i < colgroupsLength; i++) {\n
    var rowHeaders = colgroups[i].querySelectorAll(\'col.rowHeader\');\n
    if (rowHeaders.length === 0) {\n
      return;\n
    }\n
    for (var j = 0,\n
        rowHeadersLength = rowHeaders.length + 1; j < rowHeadersLength; j++) {\n
      if (rowHeadersLength == 2) {\n
        return;\n
      }\n
      if (j < Handsontable.Grouping.getLevels().rows + 1) {\n
        if (j == Handsontable.Grouping.getLevels().rows) {\n
          dom.addClass(rowHeaders[j], \'htGroupColClosest\');\n
        } else {\n
          dom.addClass(rowHeaders[j], \'htGroupCol\');\n
        }\n
      }\n
    }\n
  }\n
};\n
Handsontable.hooks.add(\'beforeInit\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', function() {\n
  if (this.getSettings().groups && !Handsontable.Grouping) {\n
    init.call(this, arguments);\n
  } else if (!this.getSettings().groups && Handsontable.Grouping) {\n
    Handsontable.Grouping.resetGroups();\n
    Handsontable.Grouping = void 0;\n
  }\n
});\n
Handsontable.plugins.Grouping = Grouping;\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../plugins.js":49}],61:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ManualColumnFreeze: {get: function() {\n
      return ManualColumnFreeze;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_plugins_46_js__;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ManualColumnFreeze(instance) {\n
  var fixedColumnsCount = instance.getSettings().fixedColumnsLeft;\n
  var init = function() {\n
    if (typeof instance.manualColumnPositionsPluginUsages !== \'undefined\') {\n
      instance.manualColumnPositionsPluginUsages.push(\'manualColumnFreeze\');\n
    } else {\n
      instance.manualColumnPositionsPluginUsages = [\'manualColumnFreeze\'];\n
    }\n
    bindHooks();\n
  };\n
  function addContextMenuEntry(defaultOptions) {\n
    defaultOptions.items.push(Handsontable.ContextMenu.SEPARATOR, {\n
      key: \'freeze_column\',\n
      name: function() {\n
        var selectedColumn = instance.getSelected()[1];\n
        if (selectedColumn > fixedColumnsCount - 1) {\n
          return \'Freeze this column\';\n
        } else {\n
          return \'Unfreeze this column\';\n
        }\n
      },\n
      disabled: function() {\n
        var selection = instance.getSelected();\n
        return selection[1] !== selection[3];\n
      },\n
      callback: function() {\n
        var selectedColumn = instance.getSelected()[1];\n
        if (selectedColumn > fixedColumnsCount - 1) {\n
          freezeColumn(selectedColumn);\n
        } else {\n
          unfreezeColumn(selectedColumn);\n
        }\n
      }\n
    });\n
  }\n
  function addFixedColumn() {\n
    instance.updateSettings({fixedColumnsLeft: fixedColumnsCount + 1});\n
    fixedColumnsCount++;\n
  }\n
  function removeFixedColumn() {\n
    instance.updateSettings({fixedColumnsLeft: fixedColumnsCount - 1});\n
    fixedColumnsCount--;\n
  }\n
  function checkPositionData(col) {\n
    if (!instance.manualColumnPositions || instance.manualColumnPositions.length === 0) {\n
      if (!instance.manualColumnPositions) {\n
        instance.manualColumnPositions = [];\n
      }\n
    }\n
    if (col) {\n
      if (!instance.manualColumnPositions[col]) {\n
        createPositionData(col + 1);\n
      }\n
    } else {\n
      createPositionData(instance.countCols());\n
    }\n
  }\n
  function createPositionData(len) {\n
    if (instance.manualColumnPositions.length < len) {\n
      for (var i = instance.manualColumnPositions.length; i < len; i++) {\n
        instance.manualColumnPositions[i] = i;\n
      }\n
    }\n
  }\n
  function modifyColumnOrder(col, actualCol, returnCol, action) {\n
    if (returnCol == null) {\n
      returnCol = col;\n
    }\n
    if (action === \'freeze\') {\n
      instance.manualColumnPositions.splice(fixedColumnsCount, 0, instance.manualColumnPositions.splice(actualCol, 1)[0]);\n
    } else if (action === \'unfreeze\') {\n
      instance.manualColumnPositions.splice(returnCol, 0, instance.manualColumnPositions.splice(actualCol, 1)[0]);\n
    }\n
  }\n
  function getBestColumnReturnPosition(col) {\n
    var i = fixedColumnsCount,\n
        j = getModifiedColumnIndex(i),\n
        initialCol = getModifiedColumnIndex(col);\n
    while (j < initialCol) {\n
      i++;\n
      j = getModifiedColumnIndex(i);\n
    }\n
    return i - 1;\n
  }\n
  function freezeColumn(col) {\n
    if (col <= fixedColumnsCount - 1) {\n
      return;\n
    }\n
    var modifiedColumn = getModifiedColumnIndex(col) || col;\n
    checkPositionData(modifiedColumn);\n
    modifyColumnOrder(modifiedColumn, col, null, \'freeze\');\n
    addFixedColumn();\n
    instance.view.wt.wtOverlays.leftOverlay.refresh();\n
  }\n
  function unfreezeColumn(col) {\n
    if (col > fixedColumnsCount - 1) {\n
      return;\n
    }\n
    var returnCol = getBestColumnReturnPosition(col);\n
    var modifiedColumn = getModifiedColumnIndex(col) || col;\n
    checkPositionData(modifiedColumn);\n
    modifyColumnOrder(modifiedColumn, col, returnCol, \'unfreeze\');\n
    removeFixedColumn();\n
    instance.view.wt.wtOverlays.leftOverlay.refresh();\n
  }\n
  function getModifiedColumnIndex(col) {\n
    return instance.manualColumnPositions[col];\n
  }\n
  function onModifyCol(col) {\n
    if (this.manualColumnPositionsPluginUsages.length > 1) {\n
      return col;\n
    }\n
    return getModifiedColumnIndex(col);\n
  }\n
  function bindHooks() {\n
    instance.addHook(\'modifyCol\', onModifyCol);\n
    instance.addHook(\'afterContextMenuDefaultOptions\', addContextMenuEntry);\n
  }\n
  return {\n
    init: init,\n
    freezeColumn: freezeColumn,\n
    unfreezeColumn: unfreezeColumn,\n
    helpers: {\n
      addFixedColumn: addFixedColumn,\n
      removeFixedColumn: removeFixedColumn,\n
      checkPositionData: checkPositionData,\n
      modifyColumnOrder: modifyColumnOrder,\n
      getBestColumnReturnPosition: getBestColumnReturnPosition\n
    }\n
  };\n
}\n
var init = function init() {\n
  if (!this.getSettings().manualColumnFreeze) {\n
    return;\n
  }\n
  var mcfPlugin;\n
  Handsontable.plugins.manualColumnFreeze = ManualColumnFreeze;\n
  this.manualColumnFreeze = new ManualColumnFreeze(this);\n
  mcfPlugin = this.manualColumnFreeze;\n
  mcfPlugin.init.call(this);\n
};\n
Handsontable.hooks.add(\'beforeInit\', init);\n
\n
\n
//# \n
},{"./../../plugins.js":49}],62:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ManualColumnMove: {get: function() {\n
      return ManualColumnMove;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ManualColumnMove() {\n
  var startCol,\n
      endCol,\n
      startX,\n
      startOffset,\n
      currentCol,\n
      instance,\n
      currentTH,\n
      handle = document.createElement(\'DIV\'),\n
      guide = document.createElement(\'DIV\'),\n
      eventManager = eventManagerObject(this);\n
  handle.className = \'manualColumnMover\';\n
  guide.className = \'manualColumnMoverGuide\';\n
  var saveManualColumnPositions = function() {\n
    var instance = this;\n
    Handsontable.hooks.run(instance, \'persistentStateSave\', \'manualColumnPositions\', instance.manualColumnPositions);\n
  };\n
  var loadManualColumnPositions = function() {\n
    var instance = this;\n
    var storedState = {};\n
    Handsontable.hooks.run(instance, \'persistentStateLoad\', \'manualColumnPositions\', storedState);\n
    return storedState.value;\n
  };\n
  function setupHandlePosition(TH) {\n
    instance = this;\n
    currentTH = TH;\n
    var col = this.view.wt.wtTable.getCoords(TH).col;\n
    if (col >= 0) {\n
      currentCol = col;\n
      var box = currentTH.getBoundingClientRect();\n
      startOffset = box.left;\n
      handle.style.top = box.top + \'px\';\n
      handle.style.left = startOffset + \'px\';\n
      instance.rootElement.appendChild(handle);\n
    }\n
  }\n
  function refreshHandlePosition(TH, delta) {\n
    var box = TH.getBoundingClientRect();\n
    var handleWidth = 6;\n
    if (delta > 0) {\n
      handle.style.left = (box.left + box.width - handleWidth) + \'px\';\n
    } else {\n
      handle.style.left = box.left + \'px\';\n
    }\n
  }\n
  function setupGuidePosition() {\n
    var instance = this;\n
    dom.addClass(handle, \'active\');\n
    dom.addClass(guide, \'active\');\n
    var box = currentTH.getBoundingClientRect();\n
    guide.style.width = box.width + \'px\';\n
    guide.style.height = instance.view.maximumVisibleElementHeight(0) + \'px\';\n
    guide.style.top = handle.style.top;\n
    guide.style.left = startOffset + \'px\';\n
    instance.rootElement.appendChild(guide);\n
  }\n
  function refreshGuidePosition(diff) {\n
    guide.style.left = startOffset + diff + \'px\';\n
  }\n
  function hideHandleAndGuide() {\n
    dom.removeClass(handle, \'active\');\n
    dom.removeClass(guide, \'active\');\n
  }\n
  var checkColumnHeader = function(element) {\n
    if (element.tagName != \'BODY\') {\n
      if (element.parentNode.tagName == \'THEAD\') {\n
        return true;\n
      } else {\n
        element = element.parentNode;\n
        return checkColumnHeader(element);\n
      }\n
    }\n
    return false;\n
  };\n
  var getTHFromTargetElement = function(element) {\n
    if (element.tagName != \'TABLE\') {\n
      if (element.tagName == \'TH\') {\n
        return element;\n
      } else {\n
        return getTHFromTargetElement(element.parentNode);\n
      }\n
    }\n
    return null;\n
  };\n
  var bindEvents = function() {\n
    var instance = this;\n
    var pressed;\n
    eventManager.addEventListener(instance.rootElement, \'mouseover\', function(e) {\n
      if (checkColumnHeader(e.target)) {\n
        var th = getTHFromTargetElement(e.target);\n
        if (th) {\n
          if (pressed) {\n
            var col = instance.view.wt.wtTable.getCoords(th).col;\n
            if (col >= 0) {\n
              endCol = col;\n
              refreshHandlePosition(e.target, endCol - startCol);\n
            }\n
          } else {\n
            setupHandlePosition.call(instance, th);\n
          }\n
        }\n
      }\n
    });\n
    eventManager.addEventListener(instance.rootElement, \'mousedown\', function(e) {\n
      if (dom.hasClass(e.target, \'manualColumnMover\')) {\n
        startX = helper.pageX(e);\n
        setupGuidePosition.call(instance);\n
        pressed = instance;\n
        startCol = currentCol;\n
        endCol = currentCol;\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mousemove\', function(e) {\n
      if (pressed) {\n
        refreshGuidePosition(helper.pageX(e) - startX);\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mouseup\', function(e) {\n
      if (pressed) {\n
        hideHandleAndGuide();\n
        pressed = false;\n
        createPositionData(instance.manualColumnPositions, instance.countCols());\n
        instance.manualColumnPositions.splice(endCol, 0, instance.manualColumnPositions.splice(startCol, 1)[0]);\n
        instance.forceFullRender = true;\n
        instance.view.render();\n
        saveManualColumnPositions.call(instance);\n
        Handsontable.hooks.run(instance, \'afterColumnMove\', startCol, endCol);\n
        setupHandlePosition.call(instance, currentTH);\n
      }\n
    });\n
    instance.addHook(\'afterDestroy\', unbindEvents);\n
  };\n
  var unbindEvents = function() {\n
    eventManager.clear();\n
  };\n
  var createPositionData = function(positionArr, len) {\n
    if (positionArr.length < len) {\n
      for (var i = positionArr.length; i < len; i++) {\n
        positionArr[i] = i;\n
      }\n
    }\n
  };\n
  this.beforeInit = function() {\n
    this.manualColumnPositions = [];\n
  };\n
  this.init = function(source) {\n
    var instance = this;\n
    var manualColMoveEnabled = !!(this.getSettings().manualColumnMove);\n
    if (manualColMoveEnabled) {\n
      var initialManualColumnPositions = this.getSettings().manualColumnMove;\n
      var loadedManualColumnPositions = loadManualColumnPositions.call(instance);\n
      if (typeof loadedManualColumnPositions != \'undefined\') {\n
        this.manualColumnPositions = loadedManualColumnPositions;\n
      } else if (Array.isArray(initialManualColumnPositions)) {\n
        this.manualColumnPositions = initialManualColumnPositions;\n
      } else {\n
        this.manualColumnPositions = [];\n
      }\n
      if (source == \'afterInit\') {\n
        if (typeof instance.manualColumnPositionsPluginUsages != \'undefined\') {\n
          instance.manualColumnPositionsPluginUsages.push(\'manualColumnMove\');\n
        } else {\n
          instance.manualColumnPositionsPluginUsages = [\'manualColumnMove\'];\n
        }\n
        bindEvents.call(this);\n
        if (this.manualColumnPositions.length > 0) {\n
          this.forceFullRender = true;\n
          this.render();\n
        }\n
      }\n
    } else {\n
      var pluginUsagesIndex = instance.manualColumnPositionsPluginUsages ? instance.manualColumnPositionsPluginUsages.indexOf(\'manualColumnMove\') : -1;\n
      if (pluginUsagesIndex > -1) {\n
        unbindEvents.call(this);\n
        this.manualColumnPositions = [];\n
        instance.manualColumnPositionsPluginUsages[pluginUsagesIndex] = void 0;\n
      }\n
    }\n
  };\n
  this.modifyCol = function(col) {\n
    if (this.getSettings().manualColumnMove) {\n
      if (typeof this.manualColumnPositions[col] === \'undefined\') {\n
        createPositionData(this.manualColumnPositions, col + 1);\n
      }\n
      return this.manualColumnPositions[col];\n
    }\n
    return col;\n
  };\n
  this.afterRemoveCol = function(index, amount) {\n
    if (!this.getSettings().manualColumnMove) {\n
      return;\n
    }\n
    var rmindx,\n
        colpos = this.manualColumnPositions;\n
    rmindx = colpos.splice(index, amount);\n
    colpos = colpos.map(function(colpos) {\n
      var i,\n
          newpos = colpos;\n
      for (i = 0; i < rmindx.length; i++) {\n
        if (colpos > rmindx[i]) {\n
          newpos--;\n
        }\n
      }\n
      return newpos;\n
    });\n
    this.manualColumnPositions = colpos;\n
  };\n
  this.afterCreateCol = function(index, amount) {\n
    if (!this.getSettings().manualColumnMove) {\n
      return;\n
    }\n
    var colpos = this.manualColumnPositions;\n
    if (!colpos.length) {\n
      return;\n
    }\n
    var addindx = [];\n
    for (var i = 0; i < amount; i++) {\n
      addindx.push(index + i);\n
    }\n
    if (index >= colpos.length) {\n
      colpos.concat(addindx);\n
    } else {\n
      colpos = colpos.map(function(colpos) {\n
        return (colpos >= index) ? (colpos + amount) : colpos;\n
      });\n
      colpos.splice.apply(colpos, [index, 0].concat(addindx));\n
    }\n
    this.manualColumnPositions = colpos;\n
  };\n
}\n
var htManualColumnMove = new ManualColumnMove();\n
Handsontable.hooks.add(\'beforeInit\', htManualColumnMove.beforeInit);\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  htManualColumnMove.init.call(this, \'afterInit\');\n
});\n
Handsontable.hooks.add(\'afterUpdateSettings\', function() {\n
  htManualColumnMove.init.call(this, \'afterUpdateSettings\');\n
});\n
Handsontable.hooks.add(\'modifyCol\', htManualColumnMove.modifyCol);\n
Handsontable.hooks.add(\'afterRemoveCol\', htManualColumnMove.afterRemoveCol);\n
Handsontable.hooks.add(\'afterCreateCol\', htManualColumnMove.afterCreateCol);\n
Handsontable.hooks.register(\'afterColumnMove\');\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46,"./../../plugins.js":49}],63:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ManualColumnResize: {get: function() {\n
      return ManualColumnResize;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ManualColumnResize() {\n
  var currentTH,\n
      currentCol,\n
      currentWidth,\n
      instance,\n
      newSize,\n
      startX,\n
      startWidth,\n
      startOffset,\n
      handle = document.createElement(\'DIV\'),\n
      guide = document.createElement(\'DIV\'),\n
      eventManager = eventManagerObject(this);\n
  handle.className = \'manualColumnResizer\';\n
  guide.className = \'manualColumnResizerGuide\';\n
  var saveManualColumnWidths = function() {\n
    var instance = this;\n
    Handsontable.hooks.run(instance, \'persistentStateSave\', \'manualColumnWidths\', instance.manualColumnWidths);\n
  };\n
  var loadManualColumnWidths = function() {\n
    var instance = this;\n
    var storedState = {};\n
    Handsontable.hooks.run(instance, \'persistentStateLoad\', \'manualColumnWidths\', storedState);\n
    return storedState.value;\n
  };\n
  function setupHandlePosition(TH) {\n
    instance = this;\n
    currentTH = TH;\n
    var col = this.view.wt.wtTable.getCoords(TH).col;\n
    if (col >= 0) {\n
      currentCol = col;\n
      var box = currentTH.getBoundingClientRect();\n
      startOffset = box.left - 6;\n
      startWidth = parseInt(box.width, 10);\n
      handle.style.top = box.top + \'px\';\n
      handle.style.left = startOffset + startWidth + \'px\';\n
      instance.rootElement.appendChild(handle);\n
    }\n
  }\n
  function refreshHandlePosition() {\n
    handle.style.left = startOffset + currentWidth + \'px\';\n
  }\n
  function setupGuidePosition() {\n
    var instance = this;\n
    dom.addClass(handle, \'active\');\n
    dom.addClass(guide, \'active\');\n
    guide.style.top = handle.style.top;\n
    guide.style.left = handle.style.left;\n
    guide.style.height = instance.view.maximumVisibleElementHeight(0) + \'px\';\n
    instance.rootElement.appendChild(guide);\n
  }\n
  function refreshGuidePosition() {\n
    guide.style.left = handle.style.left;\n
  }\n
  function hideHandleAndGuide() {\n
    dom.removeClass(handle, \'active\');\n
    dom.removeClass(guide, \'active\');\n
  }\n
  var checkColumnHeader = function(element) {\n
    if (element.tagName != \'BODY\') {\n
      if (element.parentNode.tagName == \'THEAD\') {\n
        return true;\n
      } else {\n
        element = element.parentNode;\n
        return checkColumnHeader(element);\n
      }\n
    }\n
    return false;\n
  };\n
  var getTHFromTargetElement = function(element) {\n
    if (element.tagName != \'TABLE\') {\n
      if (element.tagName == \'TH\') {\n
        return element;\n
      } else {\n
        return getTHFromTargetElement(element.parentNode);\n
      }\n
    }\n
    return null;\n
  };\n
  var bindEvents = function() {\n
    var instance = this;\n
    var pressed;\n
    var dblclick = 0;\n
    var autoresizeTimeout = null;\n
    eventManager.addEventListener(instance.rootElement, \'mouseover\', function(e) {\n
      if (checkColumnHeader(e.target)) {\n
        var th = getTHFromTargetElement(e.target);\n
        if (th) {\n
          if (!pressed) {\n
            setupHandlePosition.call(instance, th);\n
          }\n
        }\n
      }\n
    });\n
    eventManager.addEventListener(instance.rootElement, \'mousedown\', function(e) {\n
      if (dom.hasClass(e.target, \'manualColumnResizer\')) {\n
        setupGuidePosition.call(instance);\n
        pressed = instance;\n
        if (autoresizeTimeout == null) {\n
          autoresizeTimeout = setTimeout(function() {\n
            if (dblclick >= 2) {\n
              newSize = instance.determineColumnWidth.call(instance, currentCol);\n
              setManualSize(currentCol, newSize);\n
              instance.forceFullRender = true;\n
              instance.view.render();\n
              Handsontable.hooks.run(instance, \'afterColumnResize\', currentCol, newSize);\n
            }\n
            dblclick = 0;\n
            autoresizeTimeout = null;\n
          }, 500);\n
          instance._registerTimeout(autoresizeTimeout);\n
        }\n
        dblclick++;\n
        startX = helper.pageX(e);\n
        newSize = startWidth;\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mousemove\', function(e) {\n
      if (pressed) {\n
        currentWidth = startWidth + (helper.pageX(e) - startX);\n
        newSize = setManualSize(currentCol, currentWidth);\n
        refreshHandlePosition();\n
        refreshGuidePosition();\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mouseup\', function() {\n
      if (pressed) {\n
        hideHandleAndGuide();\n
        pressed = false;\n
        if (newSize != startWidth) {\n
          instance.forceFullRender = true;\n
          instance.view.render();\n
          saveManualColumnWidths.call(instance);\n
          Handsontable.hooks.run(instance, \'afterColumnResize\', currentCol, newSize);\n
        }\n
        setupHandlePosition.call(instance, currentTH);\n
      }\n
    });\n
    instance.addHook(\'afterDestroy\', unbindEvents);\n
  };\n
  var unbindEvents = function() {\n
    eventManager.clear();\n
  };\n
  this.beforeInit = function() {\n
    this.manualColumnWidths = [];\n
  };\n
  this.init = function(source) {\n
    var instance = this;\n
    var manualColumnWidthEnabled = !!(this.getSettings().manualColumnResize);\n
    if (manualColumnWidthEnabled) {\n
      var initialColumnWidths = this.getSettings().manualColumnResize;\n
      var loadedManualColumnWidths = loadManualColumnWidths.call(instance);\n
      if (typeof instance.manualColumnWidthsPluginUsages != \'undefined\') {\n
        instance.manualColumnWidthsPluginUsages.push(\'manualColumnResize\');\n
      } else {\n
        instance.manualColumnWidthsPluginUsages = [\'manualColumnResize\'];\n
      }\n
      if (typeof loadedManualColumnWidths != \'undefined\') {\n
        this.manualColumnWidths = loadedManualColumnWidths;\n
      } else if (Array.isArray(initialColumnWidths)) {\n
        this.manualColumnWidths = initialColumnWidths;\n
      } else {\n
        this.manualColumnWidths = [];\n
      }\n
      if (source == \'afterInit\') {\n
        bindEvents.call(this);\n
        if (this.manualColumnWidths.length > 0) {\n
          this.forceFullRender = true;\n
          this.render();\n
        }\n
      }\n
    } else {\n
      var pluginUsagesIndex = instance.manualColumnWidthsPluginUsages ? instance.manualColumnWidthsPluginUsages.indexOf(\'manualColumnResize\') : -1;\n
      if (pluginUsagesIndex > -1) {\n
        unbindEvents.call(this);\n
        this.manualColumnWidths = [];\n
      }\n
    }\n
  };\n
  var setManualSize = function(col, width) {\n
    width = Math.max(width, 20);\n
    col = Handsontable.hooks.run(instance, \'modifyCol\', col);\n
    instance.manualColumnWidths[col] = width;\n
    return width;\n
  };\n
  this.modifyColWidth = function(width, col) {\n
    col = this.runHooks(\'modifyCol\', col);\n
    if (this.getSettings().manualColumnResize && this.manualColumnWidths[col]) {\n
      return this.manualColumnWidths[col];\n
    }\n
    return width;\n
  };\n
}\n
var htManualColumnResize = new ManualColumnResize();\n
Handsontable.hooks.add(\'beforeInit\', htManualColumnResize.beforeInit);\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  htManualColumnResize.init.call(this, \'afterInit\');\n
});\n
Handsontable.hooks.add(\'afterUpdateSettings\', function() {\n
  htManualColumnResize.init.call(this, \'afterUpdateSettings\');\n
});\n
Handsontable.hooks.add(\'modifyColWidth\', htManualColumnResize.modifyColWidth);\n
Handsontable.hooks.register(\'afterColumnResize\');\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46,"./../../plugins.js":49}],64:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ManualRowMove: {get: function() {\n
      return ManualRowMove;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ManualRowMove() {\n
  var startRow,\n
      endRow,\n
      startY,\n
      startOffset,\n
      currentRow,\n
      currentTH,\n
      handle = document.createElement(\'DIV\'),\n
      guide = document.createElement(\'DIV\'),\n
      eventManager = eventManagerObject(this);\n
  handle.className = \'manualRowMover\';\n
  guide.className = \'manualRowMoverGuide\';\n
  var saveManualRowPositions = function() {\n
    var instance = this;\n
    Handsontable.hooks.run(instance, \'persistentStateSave\', \'manualRowPositions\', instance.manualRowPositions);\n
  };\n
  var loadManualRowPositions = function() {\n
    var instance = this,\n
        storedState = {};\n
    Handsontable.hooks.run(instance, \'persistentStateLoad\', \'manualRowPositions\', storedState);\n
    return storedState.value;\n
  };\n
  function setupHandlePosition(TH) {\n
    var instance = this;\n
    currentTH = TH;\n
    var row = this.view.wt.wtTable.getCoords(TH).row;\n
    if (row >= 0) {\n
      currentRow = row;\n
      var box = currentTH.getBoundingClientRect();\n
      startOffset = box.top;\n
      handle.style.top = startOffset + \'px\';\n
      handle.style.left = box.left + \'px\';\n
      instance.rootElement.appendChild(handle);\n
    }\n
  }\n
  function refreshHandlePosition(TH, delta) {\n
    var box = TH.getBoundingClientRect();\n
    var handleHeight = 6;\n
    if (delta > 0) {\n
      handle.style.top = (box.top + box.height - handleHeight) + \'px\';\n
    } else {\n
      handle.style.top = box.top + \'px\';\n
    }\n
  }\n
  function setupGuidePosition() {\n
    var instance = this;\n
    dom.addClass(handle, \'active\');\n
    dom.addClass(guide, \'active\');\n
    var box = currentTH.getBoundingClientRect();\n
    guide.style.width = instance.view.maximumVisibleElementWidth(0) + \'px\';\n
    guide.style.height = box.height + \'px\';\n
    guide.style.top = startOffset + \'px\';\n
    guide.style.left = handle.style.left;\n
    instance.rootElement.appendChild(guide);\n
  }\n
  function refreshGuidePosition(diff) {\n
    guide.style.top = startOffset + diff + \'px\';\n
  }\n
  function hideHandleAndGuide() {\n
    dom.removeClass(handle, \'active\');\n
    dom.removeClass(guide, \'active\');\n
  }\n
  var checkRowHeader = function(element) {\n
    if (element.tagName != \'BODY\') {\n
      if (element.parentNode.tagName == \'TBODY\') {\n
        return true;\n
      } else {\n
        element = element.parentNode;\n
        return checkRowHeader(element);\n
      }\n
    }\n
    return false;\n
  };\n
  var getTHFromTargetElement = function(element) {\n
    if (element.tagName != \'TABLE\') {\n
      if (element.tagName == \'TH\') {\n
        return element;\n
      } else {\n
        return getTHFromTargetElement(element.parentNode);\n
      }\n
    }\n
    return null;\n
  };\n
  var bindEvents = function() {\n
    var instance = this;\n
    var pressed;\n
    eventManager.addEventListener(instance.rootElement, \'mouseover\', function(e) {\n
      if (checkRowHeader(e.target)) {\n
        var th = getTHFromTargetElement(e.target);\n
        if (th) {\n
          if (pressed) {\n
            endRow = instance.view.wt.wtTable.getCoords(th).row;\n
            refreshHandlePosition(th, endRow - startRow);\n
          } else {\n
            setupHandlePosition.call(instance, th);\n
          }\n
        }\n
      }\n
    });\n
    eventManager.addEventListener(instance.rootElement, \'mousedown\', function(e) {\n
      if (dom.hasClass(e.target, \'manualRowMover\')) {\n
        startY = helper.pageY(e);\n
        setupGuidePosition.call(instance);\n
        pressed = instance;\n
        startRow = currentRow;\n
        endRow = currentRow;\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mousemove\', function(e) {\n
      if (pressed) {\n
        refreshGuidePosition(helper.pageY(e) - startY);\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mouseup\', function(e) {\n
      if (pressed) {\n
        hideHandleAndGuide();\n
        pressed = false;\n
        createPositionData(instance.manualRowPositions, instance.countRows());\n
        instance.manualRowPositions.splice(endRow, 0, instance.manualRowPositions.splice(startRow, 1)[0]);\n
        instance.forceFullRender = true;\n
        instance.view.render();\n
        saveManualRowPositions.call(instance);\n
        Handsontable.hooks.run(instance, \'afterRowMove\', startRow, endRow);\n
        setupHandlePosition.call(instance, currentTH);\n
      }\n
    });\n
    instance.addHook(\'afterDestroy\', unbindEvents);\n
  };\n
  var unbindEvents = function() {\n
    eventManager.clear();\n
  };\n
  var createPositionData = function(positionArr, len) {\n
    if (positionArr.length < len) {\n
      for (var i = positionArr.length; i < len; i++) {\n
        positionArr[i] = i;\n
      }\n
    }\n
  };\n
  this.beforeInit = function() {\n
    this.manualRowPositions = [];\n
  };\n
  this.init = function(source) {\n
    var instance = this;\n
    var manualRowMoveEnabled = !!(instance.getSettings().manualRowMove);\n
    if (manualRowMoveEnabled) {\n
      var initialManualRowPositions = instance.getSettings().manualRowMove;\n
      var loadedManualRowPostions = loadManualRowPositions.call(instance);\n
      if (typeof instance.manualRowPositionsPluginUsages != \'undefined\') {\n
        instance.manualRowPositionsPluginUsages.push(\'manualColumnMove\');\n
      } else {\n
        instance.manualRowPositionsPluginUsages = [\'manualColumnMove\'];\n
      }\n
      if (typeof loadedManualRowPostions != \'undefined\') {\n
        this.manualRowPositions = loadedManualRowPostions;\n
      } else if (Array.isArray(initialManualRowPositions)) {\n
        this.manualRowPositions = initialManualRowPositions;\n
      } else {\n
        this.manualRowPositions = [];\n
      }\n
      if (source === \'afterInit\') {\n
        bindEvents.call(this);\n
        if (this.manualRowPositions.length > 0) {\n
          instance.forceFullRender = true;\n
          instance.render();\n
        }\n
      }\n
    } else {\n
      var pluginUsagesIndex = instance.manualRowPositionsPluginUsages ? instance.manualRowPositionsPluginUsages.indexOf(\'manualColumnMove\') : -1;\n
      if (pluginUsagesIndex > -1) {\n
        unbindEvents.call(this);\n
        instance.manualRowPositions = [];\n
        instance.manualRowPositionsPluginUsages[pluginUsagesIndex] = void 0;\n
      }\n
    }\n
  };\n
  this.modifyRow = function(row) {\n
    var instance = this;\n
    if (instance.getSettings().manualRowMove) {\n
      if (typeof instance.manualRowPositions[row] === \'undefined\') {\n
        createPositionData(this.manualRowPositions, row + 1);\n
      }\n
      return instance.manualRowPositions[row];\n
    }\n
    return row;\n
  };\n
}\n
var htManualRowMove = new ManualRowMove();\n
Handsontable.hooks.add(\'beforeInit\', htManualRowMove.beforeInit);\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  htManualRowMove.init.call(this, \'afterInit\');\n
});\n
Handsontable.hooks.add(\'afterUpdateSettings\', function() {\n
  htManualRowMove.init.call(this, \'afterUpdateSettings\');\n
});\n
Handsontable.hooks.add(\'modifyRow\', htManualRowMove.modifyRow);\n
Handsontable.hooks.register(\'afterRowMove\');\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46,"./../../plugins.js":49}],65:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ManualRowResize: {get: function() {\n
      return ManualRowResize;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_helpers_46_js__,\n
    $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function ManualRowResize() {\n
  var currentTH,\n
      currentRow,\n
      currentHeight,\n
      instance,\n
      newSize,\n
      startY,\n
      startHeight,\n
      startOffset,\n
      handle = document.createElement(\'DIV\'),\n
      guide = document.createElement(\'DIV\'),\n
      eventManager = eventManagerObject(this);\n
  handle.className = \'manualRowResizer\';\n
  guide.className = \'manualRowResizerGuide\';\n
  var saveManualRowHeights = function() {\n
    var instance = this;\n
    Handsontable.hooks.run(instance, \'persistentStateSave\', \'manualRowHeights\', instance.manualRowHeights);\n
  };\n
  var loadManualRowHeights = function() {\n
    var instance = this,\n
        storedState = {};\n
    Handsontable.hooks.run(instance, \'persistentStateLoad\', \'manualRowHeights\', storedState);\n
    return storedState.value;\n
  };\n
  function setupHandlePosition(TH) {\n
    instance = this;\n
    currentTH = TH;\n
    var row = this.view.wt.wtTable.getCoords(TH).row;\n
    if (row >= 0) {\n
      currentRow = row;\n
      var box = currentTH.getBoundingClientRect();\n
      startOffset = box.top - 6;\n
      startHeight = parseInt(box.height, 10);\n
      handle.style.left = box.left + \'px\';\n
      handle.style.top = startOffset + startHeight + \'px\';\n
      instance.rootElement.appendChild(handle);\n
    }\n
  }\n
  function refreshHandlePosition() {\n
    handle.style.top = startOffset + currentHeight + \'px\';\n
  }\n
  function setupGuidePosition() {\n
    var instance = this;\n
    dom.addClass(handle, \'active\');\n
    dom.addClass(guide, \'active\');\n
    guide.style.top = handle.style.top;\n
    guide.style.left = handle.style.left;\n
    guide.style.width = instance.view.maximumVisibleElementWidth(0) + \'px\';\n
    instance.rootElement.appendChild(guide);\n
  }\n
  function refreshGuidePosition() {\n
    guide.style.top = handle.style.top;\n
  }\n
  function hideHandleAndGuide() {\n
    dom.removeClass(handle, \'active\');\n
    dom.removeClass(guide, \'active\');\n
  }\n
  var checkRowHeader = function(element) {\n
    if (element.tagName != \'BODY\') {\n
      if (element.parentNode.tagName == \'TBODY\') {\n
        return true;\n
      } else {\n
        element = element.parentNode;\n
        return checkRowHeader(element);\n
      }\n
    }\n
    return false;\n
  };\n
  var getTHFromTargetElement = function(element) {\n
    if (element.tagName != \'TABLE\') {\n
      if (element.tagName == \'TH\') {\n
        return element;\n
      } else {\n
        return getTHFromTargetElement(element.parentNode);\n
      }\n
    }\n
    return null;\n
  };\n
  var bindEvents = function() {\n
    var instance = this;\n
    var pressed;\n
    var dblclick = 0;\n
    var autoresizeTimeout = null;\n
    eventManager.addEventListener(instance.rootElement, \'mouseover\', function(e) {\n
      if (checkRowHeader(e.target)) {\n
        var th = getTHFromTargetElement(e.target);\n
        if (th) {\n
          if (!pressed) {\n
            setupHandlePosition.call(instance, th);\n
          }\n
        }\n
      }\n
    });\n
    eventManager.addEventListener(instance.rootElement, \'mousedown\', function(e) {\n
      if (dom.hasClass(e.target, \'manualRowResizer\')) {\n
        setupGuidePosition.call(instance);\n
        pressed = instance;\n
        if (autoresizeTimeout == null) {\n
          autoresizeTimeout = setTimeout(function() {\n
            if (dblclick >= 2) {\n
              setManualSize(currentRow, null);\n
              instance.forceFullRender = true;\n
              instance.view.render();\n
              Handsontable.hooks.run(instance, \'afterRowResize\', currentRow, newSize);\n
            }\n
            dblclick = 0;\n
            autoresizeTimeout = null;\n
          }, 500);\n
          instance._registerTimeout(autoresizeTimeout);\n
        }\n
        dblclick++;\n
        startY = helper.pageY(e);\n
        newSize = startHeight;\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mousemove\', function(e) {\n
      if (pressed) {\n
        currentHeight = startHeight + (helper.pageY(e) - startY);\n
        newSize = setManualSize(currentRow, currentHeight);\n
        refreshHandlePosition();\n
        refreshGuidePosition();\n
      }\n
    });\n
    eventManager.addEventListener(window, \'mouseup\', function(e) {\n
      if (pressed) {\n
        hideHandleAndGuide();\n
        pressed = false;\n
        if (newSize != startHeight) {\n
          instance.forceFullRender = true;\n
          instance.view.render();\n
          saveManualRowHeights.call(instance);\n
          Handsontable.hooks.run(instance, \'afterRowResize\', currentRow, newSize);\n
        }\n
        setupHandlePosition.call(instance, currentTH);\n
      }\n
    });\n
    instance.addHook(\'afterDestroy\', unbindEvents);\n
  };\n
  var unbindEvents = function() {\n
    eventManager.clear();\n
  };\n
  this.beforeInit = function() {\n
    this.manualRowHeights = [];\n
  };\n
  this.init = function(source) {\n
    var instance = this;\n
    var manualColumnHeightEnabled = !!(this.getSettings().manualRowResize);\n
    if (manualColumnHeightEnabled) {\n
      var initialRowHeights = this.getSettings().manualRowResize;\n
      var loadedManualRowHeights = loadManualRowHeights.call(instance);\n
      if (typeof instance.manualRowHeightsPluginUsages != \'undefined\') {\n
        instance.manualRowHeightsPluginUsages.push(\'manualRowResize\');\n
      } else {\n
        instance.manualRowHeightsPluginUsages = [\'manualRowResize\'];\n
      }\n
      if (typeof loadedManualRowHeights != \'undefined\') {\n
        this.manualRowHeights = loadedManualRowHeights;\n
      } else if (Array.isArray(initialRowHeights)) {\n
        this.manualRowHeights = initialRowHeights;\n
      } else {\n
        this.manualRowHeights = [];\n
      }\n
      if (source === \'afterInit\') {\n
        bindEvents.call(this);\n
        if (this.manualRowHeights.length > 0) {\n
          this.forceFullRender = true;\n
          this.render();\n
        }\n
      } else {\n
        this.forceFullRender = true;\n
        this.render();\n
      }\n
    } else {\n
      var pluginUsagesIndex = instance.manualRowHeightsPluginUsages ? instance.manualRowHeightsPluginUsages.indexOf(\'manualRowResize\') : -1;\n
      if (pluginUsagesIndex > -1) {\n
        unbindEvents.call(this);\n
        this.manualRowHeights = [];\n
        instance.manualRowHeightsPluginUsages[pluginUsagesIndex] = void 0;\n
      }\n
    }\n
  };\n
  var setManualSize = function(row, height) {\n
    row = Handsontable.hooks.run(instance, \'modifyRow\', row);\n
    instance.manualRowHeights[row] = height;\n
    return height;\n
  };\n
  this.modifyRowHeight = function(height, row) {\n
    if (this.getSettings().manualRowResize) {\n
      row = this.runHooks(\'modifyRow\', row);\n
      if (this.manualRowHeights[row] !== void 0) {\n
        return this.manualRowHeights[row];\n
      }\n
    }\n
    return height;\n
  };\n
}\n
var htManualRowResize = new ManualRowResize();\n
Handsontable.hooks.add(\'beforeInit\', htManualRowResize.beforeInit);\n
Handsontable.hooks.add(\'afterInit\', function() {\n
  htManualRowResize.init.call(this, \'afterInit\');\n
});\n
Handsontable.hooks.add(\'afterUpdateSettings\', function() {\n
  htManualRowResize.init.call(this, \'afterUpdateSettings\');\n
});\n
Handsontable.hooks.add(\'modifyRowHeight\', htManualRowResize.modifyRowHeight);\n
Handsontable.hooks.register(\'afterRowResize\');\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../helpers.js":46,"./../../plugins.js":49}],66:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  MergeCells: {get: function() {\n
      return MergeCells;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var WalkontableCellCoords = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableCellRange = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ = require("./../../3rdparty/walkontable/src/cell/range.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_range_46_js__}).WalkontableCellRange;\n
var WalkontableTable = ($___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__ = require("./../../3rdparty/walkontable/src/table.js"), $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__ && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_walkontable_47_src_47_table_46_js__}).WalkontableTable;\n
;\n
function CellInfoCollection() {\n
  var collection = [];\n
  collection.getInfo = function(row, col) {\n
    for (var i = 0,\n
        ilen = this.length; i < ilen; i++) {\n
      if (this[i].row <= row && this[i].row + this[i].rowspan - 1 >= row && this[i].col <= col && this[i].col + this[i].colspan - 1 >= col) {\n
        return this[i];\n
      }\n
    }\n
  };\n
  collection.setInfo = function(info) {\n
    for (var i = 0,\n
        ilen = this.length; i < ilen; i++) {\n
      if (this[i].row === info.row && this[i].col === info.col) {\n
        this[i] = info;\n
        return;\n
      }\n
    }\n
    this.push(info);\n
  };\n
  collection.removeInfo = function(row, col) {\n
    for (var i = 0,\n
        ilen = this.length; i < ilen; i++) {\n
      if (this[i].row === row && this[i].col === col) {\n
        this.splice(i, 1);\n
        break;\n
      }\n
    }\n
  };\n
  return collection;\n
}\n
function MergeCells(mergeCellsSetting) {\n
  this.mergedCellInfoCollection = new CellInfoCollection();\n
  if (Array.isArray(mergeCellsSetting)) {\n
    for (var i = 0,\n
        ilen = mergeCellsSetting.length; i < ilen; i++) {\n
      this.mergedCellInfoCollection.setInfo(mergeCellsSetting[i]);\n
    }\n
  }\n
}\n
MergeCells.prototype.canMergeRange = function(cellRange) {\n
  return !cellRange.isSingle();\n
};\n
MergeCells.prototype.mergeRange = function(cellRange) {\n
  if (!this.canMergeRange(cellRange)) {\n
    return;\n
  }\n
  var topLeft = cellRange.getTopLeftCorner();\n
  var bottomRight = cellRange.getBottomRightCorner();\n
  var mergeParent = {};\n
  mergeParent.row = topLeft.row;\n
  mergeParent.col = topLeft.col;\n
  mergeParent.rowspan = bottomRight.row - topLeft.row + 1;\n
  mergeParent.colspan = bottomRight.col - topLeft.col + 1;\n
  this.mergedCellInfoCollection.setInfo(mergeParent);\n
};\n
MergeCells.prototype.mergeOrUnmergeSelection = function(cellRange) {\n
  var info = this.mergedCellInfoCollection.getInfo(cellRange.from.row, cellRange.from.col);\n
  if (info) {\n
    this.unmergeSelection(cellRange.from);\n
  } else {\n
    this.mergeSelection(cellRange);\n
  }\n
};\n
MergeCells.prototype.mergeSelection = function(cellRange) {\n
  this.mergeRange(cellRange);\n
};\n
MergeCells.prototype.unmergeSelection = function(cellRange) {\n
  var info = this.mergedCellInfoCollection.getInfo(cellRange.row, cellRange.col);\n
  this.mergedCellInfoCollection.removeInfo(info.row, info.col);\n
};\n
MergeCells.prototype.applySpanProperties = function(TD, row, col) {\n
  var info = this.mergedCellInfoCollection.getInfo(row, col);\n
  if (info) {\n
    if (info.row === row && info.col === col) {\n
      TD.setAttribute(\'rowspan\', info.rowspan);\n
      TD.setAttribute(\'colspan\', info.colspan);\n
    } else {\n
      TD.removeAttribute(\'rowspan\');\n
      TD.removeAttribute(\'colspan\');\n
      TD.style.display = "none";\n
    }\n
  } else {\n
    TD.removeAttribute(\'rowspan\');\n
    TD.removeAttribute(\'colspan\');\n
  }\n
};\n
MergeCells.prototype.modifyTransform = function(hook, currentSelectedRange, delta) {\n
  var sameRowspan = function(merged, coords) {\n
    if (coords.row >= merged.row && coords.row <= (merged.row + merged.rowspan - 1)) {\n
      return true;\n
    }\n
    return false;\n
  },\n
      sameColspan = function(merged, coords) {\n
        if (coords.col >= merged.col && coords.col <= (merged.col + merged.colspan - 1)) {\n
          return true;\n
        }\n
        return false;\n
      },\n
      getNextPosition = function(newDelta) {\n
        return new WalkontableCellCoords(currentSelectedRange.to.row + newDelta.row, currentSelectedRange.to.col + newDelta.col);\n
      };\n
  var newDelta = {\n
    row: delta.row,\n
    col: delta.col\n
  };\n
  if (hook == \'modifyTransformStart\') {\n
    if (!this.lastDesiredCoords) {\n
      this.lastDesiredCoords = new WalkontableCellCoords(null, null);\n
    }\n
    var currentPosition = new WalkontableCellCoords(currentSelectedRange.highlight.row, currentSelectedRange.highlight.col),\n
        mergedParent = this.mergedCellInfoCollection.getInfo(currentPosition.row, currentPosition.col),\n
        currentRangeContainsMerge;\n
    for (var i = 0,\n
        mergesLength = this.mergedCellInfoCollection.length; i < mergesLength; i++) {\n
      var range = this.mergedCellInfoCollection[i];\n
      range = new WalkontableCellCoords(range.row + range.rowspan - 1, range.col + range.colspan - 1);\n
      if (currentSelectedRange.includes(range)) {\n
        currentRangeContainsMerge = true;\n
        break;\n
      }\n
    }\n
    if (mergedParent) {\n
      var mergeTopLeft = new WalkontableCellCoords(mergedParent.row, mergedParent.col),\n
          mergeBottomRight = new WalkontableCellCoords(mergedParent.row + mergedParent.rowspan - 1, mergedParent.col + mergedParent.colspan - 1),\n
          mergeRange = new WalkontableCellRange(mergeTopLeft, mergeTopLeft, mergeBottomRight);\n
      if (!mergeRange.includes(this.lastDesiredCoords)) {\n
        this.lastDesiredCoords = new WalkontableCellCoords(null, null);\n
      }\n
      newDelta.row = this.lastDesiredCoords.row ? this.lastDesiredCoords.row - currentPosition.row : newDelta.row;\n
      newDelta.col = this.lastDesiredCoords.col ? this.lastDesiredCoords.col - currentPosition.col : newDelta.col;\n
      if (delta.row > 0) {\n
        newDelta.row = mergedParent.row + mergedParent.rowspan - 1 - currentPosition.row + delta.row;\n
      } else if (delta.row < 0) {\n
        newDelta.row = currentPosition.row - mergedParent.row + delta.row;\n
      }\n
      if (delta.col > 0) {\n
        newDelta.col = mergedParent.col + mergedParent.colspan - 1 - currentPosition.col + delta.col;\n
      } else if (delta.col < 0) {\n
        newDelta.col = currentPosition.col - mergedParent.col + delta.col;\n
      }\n
    }\n
    var nextPosition = new WalkontableCellCoords(currentSelectedRange.highlight.row + newDelta.row, currentSelectedRange.highlight.col + newDelta.col),\n
        nextParentIsMerged = this.mergedCellInfoCollection.getInfo(nextPosition.row, nextPosition.col);\n
    if (nextParentIsMerged) {\n
      this.lastDesiredCoords = nextPosition;\n
      newDelta = {\n
        row: nextParentIsMerged.row - currentPosition.row,\n
        col: nextParentIsMerged.col - currentPosition.col\n
      };\n
    }\n
  } else if (hook == \'modifyTransformEnd\') {\n
    for (var i = 0,\n
        mergesLength = this.mergedCellInfoCollection.length; i < mergesLength; i++) {\n
      var currentMerge = this.mergedCellInfoCollection[i],\n
          mergeTopLeft = new WalkontableCellCoords(currentMerge.row, currentMerge.col),\n
          mergeBottomRight = new WalkontableCellCoords(currentMerge.row + currentMerge.rowspan - 1, currentMerge.col + currentMerge.colspan - 1),\n
          mergedRange = new WalkontableCellRange(mergeTopLeft, mergeTopLeft, mergeBottomRight),\n
          sharedBorders = currentSelectedRange.getBordersSharedWith(mergedRange);\n
      if (mergedRange.isEqual(currentSelectedRange)) {\n
        currentSelectedRange.setDirection("NW-SE");\n
      } else if (sharedBorders.length > 0) {\n
        var mergeHighlighted = (currentSelectedRange.highlight.isEqual(mergedRange.from));\n
        if (sharedBorders.indexOf(\'top\') > -1) {\n
          if (currentSelectedRange.to.isSouthEastOf(mergedRange.from) && mergeHighlighted) {\n
            currentSelectedRange.setDirection("NW-SE");\n
          } else if (currentSelectedRange.to.isSouthWestOf(mergedRange.from) && mergeHighlighted) {\n
            currentSelectedRange.setDirection("NE-SW");\n
          }\n
        } else if (sharedBorders.indexOf(\'bottom\') > -1) {\n
          if (currentSelectedRange.to.isNorthEastOf(mergedRange.from) && mergeHighlighted) {\n
            currentSelectedRange.setDirection("SW-NE");\n
          } else if (currentSelectedRange.to.isNorthWestOf(mergedRange.from) && mergeHighlighted) {\n
            currentSelectedRange.setDirection("SE-NW");\n
          }\n
        }\n
      }\n
      var nextPosition = getNextPosition(newDelta),\n
          withinRowspan = sameRowspan(currentMerge, nextPosition),\n
          withinColspan = sameColspan(currentMerge, nextPosition);\n
      if (currentSelectedRange.includesRange(mergedRange) && (mergedRange.includes(nextPosition) || withinRowspan || withinColspan)) {\n
        if (withinRowspan) {\n
          if (newDelta.row < 0) {\n
            newDelta.row -= currentMerge.rowspan - 1;\n
          } else if (newDelta.row > 0) {\n
            newDelta.row += currentMerge.rowspan - 1;\n
          }\n
        }\n
        if (withinColspan) {\n
          if (newDelta.col < 0) {\n
            newDelta.col -= currentMerge.colspan - 1;\n
          } else if (newDelta.col > 0) {\n
            newDelta.col += currentMerge.colspan - 1;\n
          }\n
        }\n
      }\n
    }\n
  }\n
  if (newDelta.row !== 0) {\n
    delta.row = newDelta.row;\n
  }\n
  if (newDelta.col !== 0) {\n
    delta.col = newDelta.col;\n
  }\n
};\n
var beforeInit = function() {\n
  var instance = this;\n
  var mergeCellsSetting = instance.getSettings().mergeCells;\n
  if (mergeCellsSetting) {\n
    if (!instance.mergeCells) {\n
      instance.mergeCells = new MergeCells(mergeCellsSetting);\n
    }\n
  }\n
};\n
var afterInit = function() {\n
  var instance = this;\n
  if (instance.mergeCells) {\n
    instance.view.wt.wtTable.getCell = function(coords) {\n
      if (instance.getSettings().mergeCells) {\n
        var mergeParent = instance.mergeCells.mergedCellInfoCollection.getInfo(coords.row, coords.col);\n
        if (mergeParent) {\n
          coords = mergeParent;\n
        }\n
      }\n
      return WalkontableTable.prototype.getCell.call(this, coords);\n
    };\n
  }\n
};\n
var onBeforeKeyDown = function(event) {\n
  if (!this.mergeCells) {\n
    return;\n
  }\n
  var ctrlDown = (event.ctrlKey || event.metaKey) && !event.altKey;\n
  if (ctrlDown) {\n
    if (event.keyCode === 77) {\n
      this.mergeCells.mergeOrUnmergeSelection(this.getSelectedRange());\n
      this.render();\n
      event.stopImmediatePropagation();\n
    }\n
  }\n
};\n
var addMergeActionsToContextMenu = function(defaultOptions) {\n
  if (!this.getSettings().mergeCells) {\n
    return;\n
  }\n
  defaultOptions.items.push(Handsontable.ContextMenu.SEPARATOR);\n
  defaultOptions.items.push({\n
    key: \'mergeCells\',\n
    name: function() {\n
      var sel = this.getSelected();\n
      var info = this.mergeCells.mergedCellInfoCollection.getInfo(sel[0], sel[1]);\n
      if (info) {\n
        return \'Unmerge cells\';\n
      } else {\n
        return \'Merge cells\';\n
      }\n
    },\n
    callback: function() {\n
      this.mergeCells.mergeOrUnmergeSelection(this.getSelectedRange());\n
      this.render();\n
    },\n
    disabled: function() {\n
      return false;\n
    }\n
  });\n
};\n
var afterRenderer = function(TD, row, col, prop, value, cellProperties) {\n
  if (this.mergeCells) {\n
    this.mergeCells.applySpanProperties(TD, row, col);\n
  }\n
};\n
var modifyTransformFactory = function(hook) {\n
  return function(delta) {\n
    var mergeCellsSetting = this.getSettings().mergeCells;\n
    if (mergeCellsSetting) {\n
      var currentSelectedRange = this.getSelectedRange();\n
      this.mergeCells.modifyTransform(hook, currentSelectedRange, delta);\n
      if (hook === "modifyTransformEnd") {\n
        var totalRows = this.countRows();\n
        var totalCols = this.countCols();\n
        if (currentSelectedRange.from.row < 0) {\n
          currentSelectedRange.from.row = 0;\n
        } else if (currentSelectedRange.from.row > 0 && currentSelectedRange.from.row >= totalRows) {\n
          currentSelectedRange.from.row = currentSelectedRange.from - 1;\n
        }\n
        if (currentSelectedRange.from.col < 0) {\n
          currentSelectedRange.from.col = 0;\n
        } else if (currentSelectedRange.from.col > 0 && currentSelectedRange.from.col >= totalCols) {\n
          currentSelectedRange.from.col = totalCols - 1;\n
        }\n
      }\n
    }\n
  };\n
};\n
var beforeSetRangeEnd = function(coords) {\n
  this.lastDesiredCoords = null;\n
  var mergeCellsSetting = this.getSettings().mergeCells;\n
  if (mergeCellsSetting) {\n
    var selRange = this.getSelectedRange();\n
    selRange.highlight = new WalkontableCellCoords(selRange.highlight.row, selRange.highlight.col);\n
    selRange.to = coords;\n
    var rangeExpanded = false;\n
    do {\n
      rangeExpanded = false;\n
      for (var i = 0,\n
          ilen = this.mergeCells.mergedCellInfoCollection.length; i < ilen; i++) {\n
        var cellInfo = this.mergeCells.mergedCellInfoCollection[i];\n
        var mergedCellTopLeft = new WalkontableCellCoords(cellInfo.row, cellInfo.col);\n
        var mergedCellBottomRight = new WalkontableCellCoords(cellInfo.row + cellInfo.rowspan - 1, cellInfo.col + cellInfo.colspan - 1);\n
        var mergedCellRange = new WalkontableCellRange(mergedCellTopLeft, mergedCellTopLeft, mergedCellBottomRight);\n
        if (selRange.expandByRange(mergedCellRange)) {\n
          coords.row = selRange.to.row;\n
          coords.col = selRange.to.col;\n
          rangeExpanded = true;\n
        }\n
      }\n
    } while (rangeExpanded);\n
  }\n
};\n
var beforeDrawAreaBorders = function(corners, className) {\n
  if (className && className == \'area\') {\n
    var mergeCellsSetting = this.getSettings().mergeCells;\n
    if (mergeCellsSetting) {\n
      var selRange = this.getSelectedRange();\n
      var startRange = new WalkontableCellRange(selRange.from, selRange.from, selRange.from);\n
      var stopRange = new WalkontableCellRange(selRange.to, selRange.to, selRange.to);\n
      for (var i = 0,\n
          ilen = this.mergeCells.mergedCellInfoCollection.length; i < ilen; i++) {\n
        var cellInfo = this.mergeCells.mergedCellInfoCollection[i];\n
        var mergedCellTopLeft = new WalkontableCellCoords(cellInfo.row, cellInfo.col);\n
        var mergedCellBottomRight = new WalkontableCellCoords(cellInfo.row + cellInfo.rowspan - 1, cellInfo.col + cellInfo.colspan - 1);\n
        var mergedCellRange = new WalkontableCellRange(mergedCellTopLeft, mergedCellTopLeft, mergedCellBottomRight);\n
        if (startRange.expandByRange(mergedCellRange)) {\n
          corners[0] = startRange.from.row;\n
          corners[1] = startRange.from.col;\n
        }\n
        if (stopRange.expandByRange(mergedCellRange)) {\n
          corners[2] = stopRange.from.row;\n
          corners[3] = stopRange.from.col;\n
        }\n
      }\n
    }\n
  }\n
};\n
var afterGetCellMeta = function(row, col, cellProperties) {\n
  var mergeCellsSetting = this.getSettings().mergeCells;\n
  if (mergeCellsSetting) {\n
    var mergeParent = this.mergeCells.mergedCellInfoCollection.getInfo(row, col);\n
    if (mergeParent && (mergeParent.row != row || mergeParent.col != col)) {\n
      cellProperties.copyable = false;\n
    }\n
  }\n
};\n
var afterViewportRowCalculatorOverride = function(calc) {\n
  var mergeCellsSetting = this.getSettings().mergeCells;\n
  if (mergeCellsSetting) {\n
    var colCount = this.countCols();\n
    var mergeParent;\n
    for (var c = 0; c < colCount; c++) {\n
      mergeParent = this.mergeCells.mergedCellInfoCollection.getInfo(calc.startRow, c);\n
      if (mergeParent) {\n
        if (mergeParent.row < calc.startRow) {\n
          calc.startRow = mergeParent.row;\n
          return afterViewportRowCalculatorOverride.call(this, calc);\n
        }\n
      }\n
      mergeParent = this.mergeCells.mergedCellInfoCollection.getInfo(calc.endRow, c);\n
      if (mergeParent) {\n
        var mergeEnd = mergeParent.row + mergeParent.rowspan - 1;\n
        if (mergeEnd > calc.endRow) {\n
          calc.endRow = mergeEnd;\n
          return afterViewportRowCalculatorOverride.call(this, calc);\n
        }\n
      }\n
    }\n
  }\n
};\n
var afterViewportColumnCalculatorOverride = function(calc) {\n
  var mergeCellsSetting = this.getSettings().mergeCells;\n
  if (mergeCellsSetting) {\n
    var rowCount = this.countRows();\n
    var mergeParent;\n
    for (var r = 0; r < rowCount; r++) {\n
      mergeParent = this.mergeCells.mergedCellInfoCollection.getInfo(r, calc.startColumn);\n
      if (mergeParent) {\n
        if (mergeParent.col < calc.startColumn) {\n
          calc.startColumn = mergeParent.col;\n
          return afterViewportColumnCalculatorOverride.call(this, calc);\n
        }\n
      }\n
      mergeParent = this.mergeCells.mergedCellInfoCollection.getInfo(r, calc.endColumn);\n
      if (mergeParent) {\n
        var mergeEnd = mergeParent.col + mergeParent.colspan - 1;\n
        if (mergeEnd > calc.endColumn) {\n
          calc.endColumn = mergeEnd;\n
          return afterViewportColumnCalculatorOverride.call(this, calc);\n
        }\n
      }\n
    }\n
  }\n
};\n
var isMultipleSelection = function(isMultiple) {\n
  if (isMultiple && this.mergeCells) {\n
    var mergedCells = this.mergeCells.mergedCellInfoCollection,\n
        selectionRange = this.getSelectedRange();\n
    for (var group in mergedCells) {\n
      if (selectionRange.highlight.row == mergedCells[group].row && selectionRange.highlight.col == mergedCells[group].col && selectionRange.to.row == mergedCells[group].row + mergedCells[group].rowspan - 1 && selectionRange.to.col == mergedCells[group].col + mergedCells[group].colspan - 1) {\n
        return false;\n
      }\n
    }\n
  }\n
  return isMultiple;\n
};\n
Handsontable.hooks.add(\'beforeInit\', beforeInit);\n
Handsontable.hooks.add(\'afterInit\', afterInit);\n
Handsontable.hooks.add(\'beforeKeyDown\', onBeforeKeyDown);\n
Handsontable.hooks.add(\'modifyTransformStart\', modifyTransformFactory(\'modifyTransformStart\'));\n
Handsontable.hooks.add(\'modifyTransformEnd\', modifyTransformFactory(\'modifyTransformEnd\'));\n
Handsontable.hooks.add(\'beforeSetRangeEnd\', beforeSetRangeEnd);\n
Handsontable.hooks.add(\'beforeDrawBorders\', beforeDrawAreaBorders);\n
Handsontable.hooks.add(\'afterIsMultipleSelection\', isMultipleSelection);\n
Handsontable.hooks.add(\'afterRenderer\', afterRenderer);\n
Handsontable.hooks.add(\'afterContextMenuDefaultOptions\', addMergeActionsToContextMenu);\n
Handsontable.hooks.add(\'afterGetCellMeta\', afterGetCellMeta);\n
Handsontable.hooks.add(\'afterViewportRowCalculatorOverride\', afterViewportRowCalculatorOverride);\n
Handsontable.hooks.add(\'afterViewportColumnCalculatorOverride\', afterViewportColumnCalculatorOverride);\n
Handsontable.MergeCells = MergeCells;\n
\n
\n
//# \n
},{"./../../3rdparty/walkontable/src/cell/coords.js":9,"./../../3rdparty/walkontable/src/cell/range.js":10,"./../../3rdparty/walkontable/src/table.js":24,"./../../plugins.js":49}],67:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  default: {get: function() {\n
      return $__default;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__95_base_46_js__,\n
    $___46__46__47__46__46__47_eventManager_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var BasePlugin = ($___46__46__47__95_base_46_js__ = require("./../_base.js"), $___46__46__47__95_base_46_js__ && $___46__46__47__95_base_46_js__.__esModule && $___46__46__47__95_base_46_js__ || {default: $___46__46__47__95_base_46_js__}).default;\n
var eventManagerObject = ($___46__46__47__46__46__47_eventManager_46_js__ = require("./../../eventManager.js"), $___46__46__47__46__46__47_eventManager_46_js__ && $___46__46__47__46__46__47_eventManager_46_js__.__esModule && $___46__46__47__46__46__47_eventManager_46_js__ || {default: $___46__46__47__46__46__47_eventManager_46_js__}).eventManager;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var MultipleSelectionHandles = function MultipleSelectionHandles(hotInstance) {\n
  var $__3 = this;\n
  $traceurRuntime.superConstructor($MultipleSelectionHandles).call(this, hotInstance);\n
  this.dragged = [];\n
  this.eventManager = eventManagerObject(this.hot);\n
  this.bindTouchEvents();\n
  this.hot.addHook(\'afterInit\', (function() {\n
    return $__3.init();\n
  }));\n
};\n
var $MultipleSelectionHandles = MultipleSelectionHandles;\n
($traceurRuntime.createClass)(MultipleSelectionHandles, {\n
  init: function() {\n
    this.lastSetCell = null;\n
    Handsontable.plugins.multipleSelectionHandles = new $MultipleSelectionHandles(this.hot);\n
  },\n
  bindTouchEvents: function() {\n
    var _this = this;\n
    function removeFromDragged(query) {\n
      if (_this.dragged.length === 1) {\n
        _this.dragged.splice(0, _this.dragged.length);\n
        return true;\n
      }\n
      var entryPosition = _this.dragged.indexOf(query);\n
      if (entryPosition == -1) {\n
        return false;\n
      } else if (entryPosition === 0) {\n
        _this.dragged = _this.dragged.slice(0, 1);\n
      } else if (entryPosition == 1) {\n
        _this.dragged = _this.dragged.slice(-1);\n
      }\n
    }\n
    this.eventManager.addEventListener(this.hot.rootElement, \'touchstart\', function(event) {\n
      var selectedRange;\n
      if (dom.hasClass(event.target, "topLeftSelectionHandle-HitArea")) {\n
        selectedRange = _this.hot.getSelectedRange();\n
        _this.dragged.push("topLeft");\n
        _this.touchStartRange = {\n
          width: selectedRange.getWidth(),\n
          height: selectedRange.getHeight(),\n
          direction: selectedRange.getDirection()\n
        };\n
        event.preventDefault();\n
        return false;\n
      } else if (dom.hasClass(event.target, "bottomRightSelectionHandle-HitArea")) {\n
        selectedRange = _this.hot.getSelectedRange();\n
        _this.dragged.push("bottomRight");\n
        _this.touchStartRange = {\n
          width: selectedRange.getWidth(),\n
          height: selectedRange.getHeight(),\n
          direction: selectedRange.getDirection()\n
        };\n
        event.preventDefault();\n
        return false;\n
      }\n
    });\n
    this.eventManager.addEventListener(this.hot.rootElement, \'touchend\', function(event) {\n
      if (dom.hasClass(event.target, "topLeftSelectionHandle-HitArea")) {\n
        removeFromDragged.call(_this, "topLeft");\n
        _this.touchStartRange = void 0;\n
        event.preventDefault();\n
        return false;\n
      } else if (dom.hasClass(event.target, "bottomRightSelectionHandle-HitArea")) {\n
        removeFromDragged.call(_this, "bottomRight");\n
        _this.touchStartRange = void 0;\n
        event.preventDefault();\n
        return false;\n
      }\n
    });\n
    this.eventManager.addEventListener(this.hot.rootElement, \'touchmove\', function(event) {\n
      var scrollTop = dom.getWindowScrollTop(),\n
          scrollLeft = dom.getWindowScrollLeft(),\n
          endTarget,\n
          targetCoords,\n
          selectedRange,\n
          rangeWidth,\n
          rangeHeight,\n
          rangeDirection,\n
          newRangeCoords;\n
      if (_this.dragged.length === 0) {\n
        return;\n
      }\n
      endTarget = document.elementFromPoint(event.touches[0].screenX - scrollLeft, event.touches[0].screenY - scrollTop);\n
      if (!endTarget || endTarget === _this.lastSetCell) {\n
        return;\n
      }\n
      if (endTarget.nodeName == "TD" || endTarget.nodeName == "TH") {\n
        targetCoords = _this.hot.getCoords(endTarget);\n
        if (targetCoords.col == -1) {\n
          targetCoords.col = 0;\n
        }\n
        selectedRange = _this.hot.getSelectedRange();\n
        rangeWidth = selectedRange.getWidth();\n
        rangeHeight = selectedRange.getHeight();\n
        rangeDirection = selectedRange.getDirection();\n
        if (rangeWidth == 1 && rangeHeight == 1) {\n
          _this.hot.selection.setRangeEnd(targetCoords);\n
        }\n
        newRangeCoords = _this.getCurrentRangeCoords(selectedRange, targetCoords, _this.touchStartRange.direction, rangeDirection, _this.dragged[0]);\n
        if (newRangeCoords.start !== null) {\n
          _this.hot.selection.setRangeStart(newRangeCoords.start);\n
        }\n
        _this.hot.selection.setRangeEnd(newRangeCoords.end);\n
        _this.lastSetCell = endTarget;\n
      }\n
      event.preventDefault();\n
    });\n
  },\n
  getCurrentRangeCoords: function(selectedRange, currentTouch, touchStartDirection, currentDirection, draggedHandle) {\n
    var topLeftCorner = selectedRange.getTopLeftCorner(),\n
        bottomRightCorner = selectedRange.getBottomRightCorner(),\n
        bottomLeftCorner = selectedRange.getBottomLeftCorner(),\n
        topRightCorner = selectedRange.getTopRightCorner();\n
    var newCoords = {\n
      start: null,\n
      end: null\n
    };\n
    switch (touchStartDirection) {\n
      case "NE-SW":\n
        switch (currentDirection) {\n
          case "NE-SW":\n
          case "NW-SE":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: new WalkontableCellCoords(currentTouch.row, selectedRange.highlight.col),\n
                end: new WalkontableCellCoords(bottomLeftCorner.row, currentTouch.col)\n
              };\n
            } else {\n
              newCoords = {\n
                start: new WalkontableCellCoords(selectedRange.highlight.row, currentTouch.col),\n
                end: new WalkontableCellCoords(currentTouch.row, topLeftCorner.col)\n
              };\n
            }\n
            break;\n
          case "SE-NW":\n
            if (draggedHandle == "bottomRight") {\n
              newCoords = {\n
                start: new WalkontableCellCoords(bottomRightCorner.row, currentTouch.col),\n
                end: new WalkontableCellCoords(currentTouch.row, topLeftCorner.col)\n
              };\n
            }\n
            break;\n
        }\n
        break;\n
      case "NW-SE":\n
        switch (currentDirection) {\n
          case "NE-SW":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: currentTouch,\n
                end: bottomLeftCorner\n
              };\n
            } else {\n
              newCoords.end = currentTouch;\n
            }\n
            break;\n
          case "NW-SE":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: currentTouch,\n
                end: bottomRightCorner\n
              };\n
            } else {\n
              newCoords.end = currentTouch;\n
            }\n
            break;\n
          case "SE-NW":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: currentTouch,\n
                end: topLeftCorner\n
              };\n
            } else {\n
              newCoords.end = currentTouch;\n
            }\n
            break;\n
          case "SW-NE":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: currentTouch,\n
                end: topRightCorner\n
              };\n
            } else {\n
              newCoords.end = currentTouch;\n
            }\n
            break;\n
        }\n
        break;\n
      case "SW-NE":\n
        switch (currentDirection) {\n
          case "NW-SE":\n
            if (draggedHandle == "bottomRight") {\n
              newCoords = {\n
                start: new WalkontableCellCoords(currentTouch.row, topLeftCorner.col),\n
                end: new WalkontableCellCoords(bottomLeftCorner.row, currentTouch.col)\n
              };\n
            } else {\n
              newCoords = {\n
                start: new WalkontableCellCoords(topLeftCorner.row, currentTouch.col),\n
                end: new WalkontableCellCoords(currentTouch.row, bottomRightCorner.col)\n
              };\n
            }\n
            break;\n
          case "SW-NE":\n
            if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: new WalkontableCellCoords(selectedRange.highlight.row, currentTouch.col),\n
                end: new WalkontableCellCoords(currentTouch.row, bottomRightCorner.col)\n
              };\n
            } else {\n
              newCoords = {\n
                start: new WalkontableCellCoords(currentTouch.row, topLeftCorner.col),\n
                end: new WalkontableCellCoords(topLeftCorner.row, currentTouch.col)\n
              };\n
            }\n
            break;\n
          case "SE-NW":\n
            if (draggedHandle == "bottomRight") {\n
              newCoords = {\n
                start: new WalkontableCellCoords(currentTouch.row, topRightCorner.col),\n
                end: new WalkontableCellCoords(topLeftCorner.row, currentTouch.col)\n
              };\n
            } else if (draggedHandle == "topLeft") {\n
              newCoords = {\n
                start: bottomLeftCorner,\n
                end: currentTouch\n
              };\n
            }\n
            break;\n
        }\n
        break;\n
      case "SE-NW":\n
        switch (currentDirection) {\n
          case "NW-SE":\n
          case "NE-SW":\n
          case "SW-NE":\n
            if (draggedHandle == "topLeft") {\n
              newCoords.end = currentTouch;\n
            }\n
            break;\n
          case "SE-NW":\n
            if (draggedHandle == "topLeft") {\n
              newCoords.end = currentTouch;\n
            } else {\n
              newCoords = {\n
                start: currentTouch,\n
                end: topLeftCorner\n
              };\n
            }\n
            break;\n
        }\n
        break;\n
    }\n
    return newCoords;\n
  },\n
  isDragged: function() {\n
    return this.dragged.length > 0;\n
  }\n
}, {}, BasePlugin);\n
var $__default = MultipleSelectionHandles;\n
registerPlugin(\'multipleSelectionHandles\', MultipleSelectionHandles);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../eventManager.js":45,"./../../plugins.js":49,"./../_base.js":50}],68:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  ObserveChanges: {get: function() {\n
      return ObserveChanges;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_plugins_46_js__,\n
    $___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var jsonPatch = ($___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__ = require("./../../3rdparty/json-patch-duplex.js"), $___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__ && $___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__.__esModule && $___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__ || {default: $___46__46__47__46__46__47_3rdparty_47_json_45_patch_45_duplex_46_js__}).default;\n
;\n
function ObserveChanges() {}\n
Handsontable.hooks.add(\'afterLoadData\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', init);\n
Handsontable.hooks.register(\'afterChangesObserved\');\n
function init() {\n
  var instance = this;\n
  var pluginEnabled = instance.getSettings().observeChanges;\n
  if (pluginEnabled) {\n
    if (instance.observer) {\n
      destroy.call(instance);\n
    }\n
    createObserver.call(instance);\n
    bindEvents.call(instance);\n
  } else if (!pluginEnabled) {\n
    destroy.call(instance);\n
  }\n
}\n
function createObserver() {\n
  var instance = this;\n
  instance.observeChangesActive = true;\n
  instance.pauseObservingChanges = function() {\n
    instance.observeChangesActive = false;\n
  };\n
  instance.resumeObservingChanges = function() {\n
    instance.observeChangesActive = true;\n
  };\n
  instance.observedData = instance.getData();\n
  instance.observer = jsonPatch.observe(instance.observedData, function(patches) {\n
    if (instance.observeChangesActive) {\n
      runHookForOperation.call(instance, patches);\n
      instance.render();\n
    }\n
    instance.runHooks(\'afterChangesObserved\');\n
  });\n
}\n
function runHookForOperation(rawPatches) {\n
  var instance = this;\n
  var patches = cleanPatches(rawPatches);\n
  for (var i = 0,\n
      len = patches.length; i < len; i++) {\n
    var patch = patches[i];\n
    var parsedPath = parsePath(patch.path);\n
    switch (patch.op) {\n
      case \'add\':\n
        if (isNaN(parsedPath.col)) {\n
          instance.runHooks(\'afterCreateRow\', parsedPath.row);\n
        } else {\n
          instance.runHooks(\'afterCreateCol\', parsedPath.col);\n
        }\n
        break;\n
      case \'remove\':\n
        if (isNaN(parsedPath.col)) {\n
          instance.runHooks(\'afterRemoveRow\', parsedPath.row, 1);\n
        } else {\n
          instance.runHooks(\'afterRemoveCol\', parsedPath.col, 1);\n
        }\n
        break;\n
      case \'replace\':\n
        instance.runHooks(\'afterChange\', [parsedPath.row, parsedPath.col, null, patch.value], \'external\');\n
        break;\n
    }\n
  }\n
  function cleanPatches(rawPatches) {\n
    var patches;\n
    patches = removeLengthRelatedPatches(rawPatches);\n
    patches = removeMultipleAddOrRemoveColPatches(patches);\n
    return patches;\n
  }\n
  function removeMultipleAddOrRemoveColPatches(rawPatches) {\n
    var newOrRemovedColumns = [];\n
    return rawPatches.filter(function(patch) {\n
      var parsedPath = parsePath(patch.path);\n
      if ([\'add\', \'remove\'].indexOf(patch.op) != -1 && !isNaN(parsedPath.col)) {\n
        if (newOrRemovedColumns.indexOf(parsedPath.col) != -1) {\n
          return false;\n
        } else {\n
          newOrRemovedColumns.push(parsedPath.col);\n
        }\n
      }\n
      return true;\n
    });\n
  }\n
  function removeLengthRelatedPatches(rawPatches) {\n
    return rawPatches.filter(function(patch) {\n
      return !/[/]length/ig.test(patch.path);\n
    });\n
  }\n
  function parsePath(path) {\n
    var match = path.match(/^\\/(\\d+)\\/?(.*)?$/);\n
    return {\n
      row: parseInt(match[1], 10),\n
      col: /^\\d*$/.test(match[2]) ? parseInt(match[2], 10) : match[2]\n
    };\n
  }\n
}\n
function destroy() {\n
  var instance = this;\n
  if (instance.observer) {\n
    destroyObserver.call(instance);\n
    unbindEvents.call(instance);\n
  }\n
}\n
function destroyObserver() {\n
  var instance = this;\n
  jsonPatch.unobserve(instance.observedData, instance.observer);\n
  delete instance.observeChangesActive;\n
  delete instance.pauseObservingChanges;\n
  delete instance.resumeObservingChanges;\n
}\n
function bindEvents() {\n
  var instance = this;\n
  instance.addHook(\'afterDestroy\', destroy);\n
  instance.addHook(\'afterCreateRow\', afterTableAlter);\n
  instance.addHook(\'afterRemoveRow\', afterTableAlter);\n
  instance.addHook(\'afterCreateCol\', afterTableAlter);\n
  instance.addHook(\'afterRemoveCol\', afterTableAlter);\n
  instance.addHook(\'afterChange\', function(changes, source) {\n
    if (source != \'loadData\') {\n
      afterTableAlter.call(this);\n
    }\n
  });\n
}\n
function unbindEvents() {\n
  var instance = this;\n
  instance.removeHook(\'afterDestroy\', destroy);\n
  instance.removeHook(\'afterCreateRow\', afterTableAlter);\n
  instance.removeHook(\'afterRemoveRow\', afterTableAlter);\n
  instance.removeHook(\'afterCreateCol\', afterTableAlter);\n
  instance.removeHook(\'afterRemoveCol\', afterTableAlter);\n
  instance.removeHook(\'afterChange\', afterTableAlter);\n
}\n
function afterTableAlter() {\n
  var instance = this;\n
  instance.pauseObservingChanges();\n
  instance.addHookOnce(\'afterChangesObserved\', function() {\n
    instance.resumeObservingChanges();\n
  });\n
}\n
\n
\n
//# \n
},{"./../../3rdparty/json-patch-duplex.js":4,"./../../plugins.js":49}],69:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  HandsontablePersistentState: {get: function() {\n
      return HandsontablePersistentState;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_plugins_46_js__;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
;\n
function Storage(prefix) {\n
  var savedKeys;\n
  var saveSavedKeys = function() {\n
    window.localStorage[prefix + \'__\' + \'persistentStateKeys\'] = JSON.stringify(savedKeys);\n
  };\n
  var loadSavedKeys = function() {\n
    var keysJSON = window.localStorage[prefix + \'__\' + \'persistentStateKeys\'];\n
    var keys = typeof keysJSON == \'string\' ? JSON.parse(keysJSON) : void 0;\n
    savedKeys = keys ? keys : [];\n
  };\n
  var clearSavedKeys = function() {\n
    savedKeys = [];\n
    saveSavedKeys();\n
  };\n
  loadSavedKeys();\n
  this.saveValue = function(key, value) {\n
    window.localStorage[prefix + \'_\' + key] = JSON.stringify(value);\n
    if (savedKeys.indexOf(key) == -1) {\n
      savedKeys.push(key);\n
      saveSavedKeys();\n
    }\n
  };\n
  this.loadValue = function(key, defaultValue) {\n
    key = typeof key != \'undefined\' ? key : defaultValue;\n
    var value = window.localStorage[prefix + \'_\' + key];\n
    return typeof value == "undefined" ? void 0 : JSON.parse(value);\n
  };\n
  this.reset = function(key) {\n
    window.localStorage.removeItem(prefix + \'_\' + key);\n
  };\n
  this.resetAll = function() {\n
    for (var index = 0; index < savedKeys.length; index++) {\n
      window.localStorage.removeItem(prefix + \'_\' + savedKeys[index]);\n
    }\n
    clearSavedKeys();\n
  };\n
}\n
function HandsontablePersistentState() {\n
  var plugin = this;\n
  this.init = function() {\n
    var instance = this,\n
        pluginSettings = instance.getSettings()[\'persistentState\'];\n
    plugin.enabled = !!(pluginSettings);\n
    if (!plugin.enabled) {\n
      removeHooks.call(instance);\n
      return;\n
    }\n
    if (!instance.storage) {\n
      instance.storage = new Storage(instance.rootElement.id);\n
    }\n
    instance.resetState = plugin.resetValue;\n
    addHooks.call(instance);\n
  };\n
  this.saveValue = function(key, value) {\n
    var instance = this;\n
    instance.storage.saveValue(key, value);\n
  };\n
  this.loadValue = function(key, saveTo) {\n
    var instance = this;\n
    saveTo.value = instance.storage.loadValue(key);\n
  };\n
  this.resetValue = function(key) {\n
    var instance = this;\n
    if (typeof key != \'undefined\') {\n
      instance.storage.reset(key);\n
    } else {\n
      instance.storage.resetAll();\n
    }\n
  };\n
  var hooks = {\n
    \'persistentStateSave\': plugin.saveValue,\n
    \'persistentStateLoad\': plugin.loadValue,\n
    \'persistentStateReset\': plugin.resetValue\n
  };\n
  for (var hookName in hooks) {\n
    if (hooks.hasOwnProperty(hookName)) {\n
      Handsontable.hooks.register(hookName);\n
    }\n
  }\n
  function addHooks() {\n
    var instance = this;\n
    for (var hookName in hooks) {\n
      if (hooks.hasOwnProperty(hookName)) {\n
        instance.addHook(hookName, hooks[hookName]);\n
      }\n
    }\n
  }\n
  function removeHooks() {\n
    var instance = this;\n
    for (var hookName in hooks) {\n
      if (hooks.hasOwnProperty(hookName)) {\n
        instance.removeHook(hookName, hooks[hookName]);\n
      }\n
    }\n
  }\n
}\n
var htPersistentState = new HandsontablePersistentState();\n
Handsontable.hooks.add(\'beforeInit\', htPersistentState.init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', htPersistentState.init);\n
\n
\n
//# \n
},{"./../../plugins.js":49}],70:[function(require,module,exports){\n
"use strict";\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47__46__46__47_renderers_46_js__ = require("./../../renderers.js"), $___46__46__47__46__46__47_renderers_46_js__ && $___46__46__47__46__46__47_renderers_46_js__.__esModule && $___46__46__47__46__46__47_renderers_46_js__ || {default: $___46__46__47__46__46__47_renderers_46_js__}),\n
    registerRenderer = $__0.registerRenderer,\n
    getRenderer = $__0.getRenderer;\n
Handsontable.Search = function Search(instance) {\n
  this.query = function(queryStr, callback, queryMethod) {\n
    var rowCount = instance.countRows();\n
    var colCount = instance.countCols();\n
    var queryResult = [];\n
    if (!callback) {\n
      callback = Handsontable.Search.global.getDefaultCallback();\n
    }\n
    if (!queryMethod) {\n
      queryMethod = Handsontable.Search.global.getDefaultQueryMethod();\n
    }\n
    for (var rowIndex = 0; rowIndex < rowCount; rowIndex++) {\n
      for (var colIndex = 0; colIndex < colCount; colIndex++) {\n
        var cellData = instance.getDataAtCell(rowIndex, colIndex);\n
        var cellProperties = instance.getCellMeta(rowIndex, colIndex);\n
        var cellCallback = cellProperties.search.callback || callback;\n
        var cellQueryMethod = cellProperties.search.queryMethod || queryMethod;\n
        var testResult = cellQueryMethod(queryStr, cellData);\n
        if (testResult) {\n
          var singleResult = {\n
            row: rowIndex,\n
            col: colIndex,\n
            data: cellData\n
          };\n
          queryResult.push(singleResult);\n
        }\n
        if (cellCallback) {\n
          cellCallback(instance, rowIndex, colIndex, cellData, testResult);\n
        }\n
      }\n
    }\n
    return queryResult;\n
  };\n
};\n
Handsontable.Search.DEFAULT_CALLBACK = function(instance, row, col, data, testResult) {\n
  instance.getCellMeta(row, col).isSearchResult = testResult;\n
};\n
Handsontable.Search.DEFAULT_QUERY_METHOD = function(query, value) {\n
  if (typeof query == \'undefined\' || query == null || !query.toLowerCase || query.length === 0) {\n
    return false;\n
  }\n
  if (typeof value == \'undefined\' || value == null) {\n
    return false;\n
  }\n
  return value.toString().toLowerCase().indexOf(query.toLowerCase()) != -1;\n
};\n
Handsontable.Search.DEFAULT_SEARCH_RESULT_CLASS = \'htSearchResult\';\n
Handsontable.Search.global = (function() {\n
  var defaultCallback = Handsontable.Search.DEFAULT_CALLBACK;\n
  var defaultQueryMethod = Handsontable.Search.DEFAULT_QUERY_METHOD;\n
  var defaultSearchResultClass = Handsontable.Search.DEFAULT_SEARCH_RESULT_CLASS;\n
  return {\n
    getDefaultCallback: function() {\n
      return defaultCallback;\n
    },\n
    setDefaultCallback: function(newDefaultCallback) {\n
      defaultCallback = newDefaultCallback;\n
    },\n
    getDefaultQueryMethod: function() {\n
      return defaultQueryMethod;\n
    },\n
    setDefaultQueryMethod: function(newDefaultQueryMethod) {\n
      defaultQueryMethod = newDefaultQueryMethod;\n
    },\n
    getDefaultSearchResultClass: function() {\n
      return defaultSearchResultClass;\n
    },\n
    setDefaultSearchResultClass: function(newSearchResultClass) {\n
      defaultSearchResultClass = newSearchResultClass;\n
    }\n
  };\n
})();\n
Handsontable.SearchCellDecorator = function(instance, TD, row, col, prop, value, cellProperties) {\n
  var searchResultClass = (cellProperties.search !== null && typeof cellProperties.search == \'object\' && cellProperties.search.searchResultClass) || Handsontable.Search.global.getDefaultSearchResultClass();\n
  if (cellProperties.isSearchResult) {\n
    dom.addClass(TD, searchResultClass);\n
  } else {\n
    dom.removeClass(TD, searchResultClass);\n
  }\n
};\n
var originalBaseRenderer = getRenderer(\'base\');\n
registerRenderer(\'base\', function(instance, TD, row, col, prop, value, cellProperties) {\n
  originalBaseRenderer.apply(this, arguments);\n
  Handsontable.SearchCellDecorator.apply(this, arguments);\n
});\n
function init() {\n
  var instance = this;\n
  var pluginEnabled = !!instance.getSettings().search;\n
  if (pluginEnabled) {\n
    instance.search = new Handsontable.Search(instance);\n
  } else {\n
    delete instance.search;\n
  }\n
}\n
Handsontable.hooks.add(\'afterInit\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', init);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../renderers.js":73}],71:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  TouchScroll: {get: function() {\n
      return TouchScroll;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47__46__46__47_dom_46_js__,\n
    $___46__46__47__95_base_46_js__,\n
    $___46__46__47__46__46__47_plugins_46_js__;\n
var dom = ($___46__46__47__46__46__47_dom_46_js__ = require("./../../dom.js"), $___46__46__47__46__46__47_dom_46_js__ && $___46__46__47__46__46__47_dom_46_js__.__esModule && $___46__46__47__46__46__47_dom_46_js__ || {default: $___46__46__47__46__46__47_dom_46_js__});\n
var BasePlugin = ($___46__46__47__95_base_46_js__ = require("./../_base.js"), $___46__46__47__95_base_46_js__ && $___46__46__47__95_base_46_js__.__esModule && $___46__46__47__95_base_46_js__ || {default: $___46__46__47__95_base_46_js__}).default;\n
var registerPlugin = ($___46__46__47__46__46__47_plugins_46_js__ = require("./../../plugins.js"), $___46__46__47__46__46__47_plugins_46_js__ && $___46__46__47__46__46__47_plugins_46_js__.__esModule && $___46__46__47__46__46__47_plugins_46_js__ || {default: $___46__46__47__46__46__47_plugins_46_js__}).registerPlugin;\n
var TouchScroll = function TouchScroll(hotInstance) {\n
  var $__2 = this;\n
  $traceurRuntime.superConstructor($TouchScroll).call(this, hotInstance);\n
  this.hot.addHook(\'afterInit\', (function() {\n
    return $__2.init();\n
  }));\n
  this.scrollbars = [];\n
  this.clones = [];\n
};\n
var $TouchScroll = TouchScroll;\n
($traceurRuntime.createClass)(TouchScroll, {\n
  init: function() {\n
    this.registerEvents();\n
    this.scrollbars.push(this.hot.view.wt.wtOverlays.topOverlay);\n
    this.scrollbars.push(this.hot.view.wt.wtOverlays.leftOverlay);\n
    if (this.hot.view.wt.wtOverlays.topLeftCornerOverlay) {\n
      this.scrollbars.push(this.hot.view.wt.wtOverlays.topLeftCornerOverlay);\n
    }\n
    if (this.hot.view.wt.wtOverlays.topOverlay.needFullRender) {\n
      this.clones.push(this.hot.view.wt.wtOverlays.topOverlay.clone.wtTable.holder.parentNode);\n
    }\n
    if (this.hot.view.wt.wtOverlays.leftOverlay.needFullRender) {\n
      this.clones.push(this.hot.view.wt.wtOverlays.leftOverlay.clone.wtTable.holder.parentNode);\n
    }\n
    if (this.hot.view.wt.wtOverlays.topLeftCornerOverlay) {\n
      this.clones.push(this.hot.view.wt.wtOverlays.topLeftCornerOverlay.clone.wtTable.holder.parentNode);\n
    }\n
  },\n
  registerEvents: function() {\n
    var $__2 = this;\n
    this.hot.addHook(\'beforeTouchScroll\', (function() {\n
      return $__2.onBeforeTouchScroll();\n
    }));\n
    this.hot.addHook(\'afterMomentumScroll\', (function() {\n
      return $__2.onAfterMomentumScroll();\n
    }));\n
  },\n
  onBeforeTouchScroll: function() {\n
    Handsontable.freezeOverlays = true;\n
    for (var i = 0,\n
        cloneCount = this.clones.length; i < cloneCount; i++) {\n
      dom.addClass(this.clones[i], \'hide-tween\');\n
    }\n
  },\n
  onAfterMomentumScroll: function() {\n
    Handsontable.freezeOverlays = false;\n
    for (var i = 0,\n
        cloneCount = this.clones.length; i < cloneCount; i++) {\n
      dom.removeClass(this.clones[i], \'hide-tween\');\n
    }\n
    for (var i$__4 = 0,\n
        cloneCount$__5 = this.clones.length; i$__4 < cloneCount$__5; i$__4++) {\n
      dom.addClass(this.clones[i$__4], \'show-tween\');\n
    }\n
    setTimeout(function() {\n
      for (var i = 0,\n
          cloneCount = this.clones.length; i < cloneCount; i++) {\n
        dom.removeClass(this.clones[i], \'show-tween\');\n
      }\n
    }, 400);\n
    for (var i$__6 = 0,\n
        cloneCount$__7 = this.scrollbars.length; i$__6 < cloneCount$__7; i$__6++) {\n
      this.scrollbars[i$__6].refresh();\n
      this.scrollbars[i$__6].resetFixedPosition();\n
    }\n
    this.hot.view.wt.wtOverlays.syncScrollWithMaster();\n
  }\n
}, {}, BasePlugin);\n
;\n
registerPlugin(\'touchScroll\', TouchScroll);\n
\n
\n
//# \n
},{"./../../dom.js":31,"./../../plugins.js":49,"./../_base.js":50}],72:[function(require,module,exports){\n
"use strict";\n
var $___46__46__47__46__46__47_helpers_46_js__;\n
var helper = ($___46__46__47__46__46__47_helpers_46_js__ = require("./../../helpers.js"), $___46__46__47__46__46__47_helpers_46_js__ && $___46__46__47__46__46__47_helpers_46_js__.__esModule && $___46__46__47__46__46__47_helpers_46_js__ || {default: $___46__46__47__46__46__47_helpers_46_js__});\n
Handsontable.UndoRedo = function(instance) {\n
  var plugin = this;\n
  this.instance = instance;\n
  this.doneActions = [];\n
  this.undoneActions = [];\n
  this.ignoreNewActions = false;\n
  instance.addHook("afterChange", function(changes, origin) {\n
    if (changes) {\n
      var action = new Handsontable.UndoRedo.ChangeAction(changes);\n
      plugin.done(action);\n
    }\n
  });\n
  instance.addHook("afterCreateRow", function(index, amount, createdAutomatically) {\n
    if (createdAutomatically) {\n
      return;\n
    }\n
    var action = new Handsontable.UndoRedo.CreateRowAction(index, amount);\n
    plugin.done(action);\n
  });\n
  instance.addHook("beforeRemoveRow", function(index, amount) {\n
    var originalData = plugin.instance.getData();\n
    index = (originalData.length + index) % originalData.length;\n
    var removedData = originalData.slice(index, index + amount);\n
    var action = new Handsontable.UndoRedo.RemoveRowAction(index, removedData);\n
    plugin.done(action);\n
  });\n
  instance.addHook("afterCreateCol", function(index, amount, createdAutomatically) {\n
    if (createdAutomatically) {\n
      return;\n
    }\n
    var action = new Handsontable.UndoRedo.CreateColumnAction(index, amount);\n
    plugin.done(action);\n
  });\n
  instance.addHook("beforeRemoveCol", function(index, amount) {\n
    var originalData = plugin.instance.getData();\n
    index = (plugin.instance.countCols() + index) % plugin.instance.countCols();\n
    var removedData = [];\n
    for (var i = 0,\n
        len = originalData.length; i < len; i++) {\n
      removedData[i] = originalData[i].slice(index, index + amount);\n
    }\n
    var headers;\n
    if (Array.isArray(instance.getSettings().colHeaders)) {\n
      headers = instance.getSettings().colHeaders.slice(index, index + removedData.length);\n
    }\n
    var action = new Handsontable.UndoRedo.RemoveColumnAction(index, removedData, headers);\n
    plugin.done(action);\n
  });\n
  instance.addHook("beforeCellAlignment", function(stateBefore, range, type, alignment) {\n
    var action = new Handsontable.UndoRedo.CellAlignmentAction(stateBefore, range, type, alignment);\n
    plugin.done(action);\n
  });\n
};\n
Handsontable.UndoRedo.prototype.done = function(action) {\n
  if (!this.ignoreNewActions) {\n
    this.doneActions.push(action);\n
    this.undoneActions.length = 0;\n
  }\n
};\n
Handsontable.UndoRedo.prototype.undo = function() {\n
  if (this.isUndoAvailable()) {\n
    var action = this.doneActions.pop();\n
    this.ignoreNewActions = true;\n
    var that = this;\n
    action.undo(this.instance, function() {\n
      that.ignoreNewActions = false;\n
      that.undoneActions.push(action);\n
    });\n
  }\n
};\n
Handsontable.UndoRedo.prototype.redo = function() {\n
  if (this.isRedoAvailable()) {\n
    var action = this.undoneActions.pop();\n
    this.ignoreNewActions = true;\n
    var that = this;\n
    action.redo(this.instance, function() {\n
      that.ignoreNewActions = false;\n
      that.doneActions.push(action);\n
    });\n
  }\n
};\n
Handsontable.UndoRedo.prototype.isUndoAvailable = function() {\n
  return this.doneActions.length > 0;\n
};\n
Handsontable.UndoRedo.prototype.isRedoAvailable = function() {\n
  return this.undoneActions.length > 0;\n
};\n
Handsontable.UndoRedo.prototype.clear = function() {\n
  this.doneActions.length = 0;\n
  this.undoneActions.length = 0;\n
};\n
Handsontable.UndoRedo.Action = function() {};\n
Handsontable.UndoRedo.Action.prototype.undo = function() {};\n
Handsontable.UndoRedo.Action.prototype.redo = function() {};\n
Handsontable.UndoRedo.ChangeAction = function(changes) {\n
  this.changes = changes;\n
};\n
helper.inherit(Handsontable.UndoRedo.ChangeAction, Handsontable.UndoRedo.Action);\n
Handsontable.UndoRedo.ChangeAction.prototype.undo = function(instance, undoneCallback) {\n
  var data = helper.deepClone(this.changes),\n
      emptyRowsAtTheEnd = instance.countEmptyRows(true),\n
      emptyColsAtTheEnd = instance.countEmptyCols(true);\n
  for (var i = 0,\n
      len = data.length; i < len; i++) {\n
    data[i].splice(3, 1);\n
  }\n
  instance.addHookOnce(\'afterChange\', undoneCallback);\n
  instance.setDataAtRowProp(data, null, null, \'undo\');\n
  for (var i = 0,\n
      len = data.length; i < len; i++) {\n
    if (instance.getSettings().minSpareRows && data[i][0] + 1 + instance.getSettings().minSpareRows === instance.countRows() && emptyRowsAtTheEnd == instance.getSettings().minSpareRows) {\n
      instance.alter(\'remove_row\', parseInt(data[i][0] + 1, 10), instance.getSettings().minSpareRows);\n
      instance.undoRedo.doneActions.pop();\n
    }\n
    if (instance.getSettings().minSpareCols && data[i][1] + 1 + instance.getSettings().minSpareCols === instance.countCols() && emptyColsAtTheEnd == instance.getSettings().minSpareCols) {\n
      instance.alter(\'remove_col\', parseInt(data[i][1] + 1, 10), instance.getSettings().minSpareCols);\n
      instance.undoRedo.doneActions.pop();\n
    }\n
  }\n
};\n
Handsontable.UndoRedo.ChangeAction.prototype.redo = function(instance, onFinishCallback) {\n
  var data = helper.deepClone(this.changes);\n
  for (var i = 0,\n
      len = data.length; i < len; i++) {\n
    data[i].splice(2, 1);\n
  }\n
  instance.addHookOnce(\'afterChange\', onFinishCallback);\n
  instance.setDataAtRowProp(data, null, null, \'redo\');\n
};\n
Handsontable.UndoRedo.CreateRowAction = function(index, amount) {\n
  this.index = index;\n
  this.amount = amount;\n
};\n
helper.inherit(Handsontable.UndoRedo.CreateRowAction, Handsontable.UndoRedo.Action);\n
Handsontable.UndoRedo.CreateRowAction.prototype.undo = function(instance, undoneCallback) {\n
  var rowCount = instance.countRows(),\n
      minSpareRows = instance.getSettings().minSpareRows;\n
  if (this.index >= rowCount && this.index - minSpareRows < rowCount) {\n
    this.index -= minSpareRows;\n
  }\n
  instance.addHookOnce(\'afterRemoveRow\', undoneCallback);\n
  instance.alter(\'remove_row\', this.index, this.amount);\n
};\n
Handsontable.UndoRedo.CreateRowAction.prototype.redo = function(instance, redoneCallback) {\n
  instance.addHookOnce(\'afterCreateRow\', redoneCallback);\n
  instance.alter(\'insert_row\', this.index + 1, this.amount);\n
};\n
Handsontable.UndoRedo.RemoveRowAction = function(index, data) {\n
  this.index = index;\n
  this.data = data;\n
};\n
helper.inherit(Handsontable.UndoRedo.RemoveRowAction, Handsontable.UndoRedo.Action);\n
Handsontable.UndoRedo.RemoveRowAction.prototype.undo = function(instance, undoneCallback) {\n
  var spliceArgs = [this.index, 0];\n
  Array.prototype.push.apply(spliceArgs, this.data);\n
  Array.prototype.splice.apply(instance.getData(), spliceArgs);\n
  instance.addHookOnce(\'afterRender\', undoneCallback);\n
  instance.render();\n
};\n
Handsontable.UndoRedo.RemoveRowAction.prototype.redo = function(instance, redoneCallback) {\n
  instance.addHookOnce(\'afterRemoveRow\', redoneCallback);\n
  instance.alter(\'remove_row\', this.index, this.data.length);\n
};\n
Handsontable.UndoRedo.CreateColumnAction = function(index, amount) {\n
  this.index = index;\n
  this.amount = amount;\n
};\n
helper.inherit(Handsontable.UndoRedo.CreateColumnAction, Handsontable.UndoRedo.Action);\n
Handsontable.UndoRedo.CreateColumnAction.prototype.undo = function(instance, undoneCallback) {\n
  instance.addHookOnce(\'afterRemoveCol\', undoneCallback);\n
  instance.alter(\'remove_col\', this.index, this.amount);\n
};\n
Handsontable.UndoRedo.CreateColumnAction.prototype.redo = function(instance, redoneCallback) {\n
  instance.addHookOnce(\'afterCreateCol\', redoneCallback);\n
  instance.alter(\'insert_col\', this.index + 1, this.amount);\n
};\n
Handsontable.UndoRedo.CellAlignmentAction = function(stateBefore, range, type, alignment) {\n
  this.stateBefore = stateBefore;\n
  this.range = range;\n
  this.type = type;\n
  this.alignment = alignment;\n
};\n
Handsontable.UndoRedo.CellAlignmentAction.prototype.undo = function(instance, undoneCallback) {\n
  if (!instance.contextMenu) {\n
    return;\n
  }\n
  for (var row = this.range.from.row; row <= this.range.to.row; row++) {\n
    for (var col = this.range.from.col; col <= this.range.to.col; col++) {\n
      instance.setCellMeta(row, col, \'className\', this.stateBefore[row][col] || \' htLeft\');\n
    }\n
  }\n
  instance.addHookOnce(\'afterRender\', undoneCallback);\n
  instance.render();\n
};\n
Handsontable.UndoRedo.CellAlignmentAction.prototype.redo = function(instance, undoneCallback) {\n
  if (!instance.contextMenu) {\n
    return;\n
  }\n
  for (var row = this.range.from.row; row <= this.range.to.row; row++) {\n
    for (var col = this.range.from.col; col <= this.range.to.col; col++) {\n
      instance.contextMenu.align.call(instance, this.range, this.type, this.alignment);\n
    }\n
  }\n
  instance.addHookOnce(\'afterRender\', undoneCallback);\n
  instance.render();\n
};\n
Handsontable.UndoRedo.RemoveColumnAction = function(index, data, headers) {\n
  this.index = index;\n
  this.data = data;\n
  this.amount = this.data[0].length;\n
  this.headers = headers;\n
};\n
helper.inherit(Handsontable.UndoRedo.RemoveColumnAction, Handsontable.UndoRedo.Action);\n
Handsontable.UndoRedo.RemoveColumnAction.prototype.undo = function(instance, undoneCallback) {\n
  var row,\n
      spliceArgs;\n
  for (var i = 0,\n
      len = instance.getData().length; i < len; i++) {\n
    row = instance.getSourceDataAtRow(i);\n
    spliceArgs = [this.index, 0];\n
    Array.prototype.push.apply(spliceArgs, this.data[i]);\n
    Array.prototype.splice.apply(row, spliceArgs);\n
  }\n
  if (typeof this.headers != \'undefined\') {\n
    spliceArgs = [this.index, 0];\n
    Array.prototype.push.apply(spliceArgs, this.headers);\n
    Array.prototype.splice.apply(instance.getSettings().colHeaders, spliceArgs);\n
  }\n
  instance.addHookOnce(\'afterRender\', undoneCallback);\n
  instance.render();\n
};\n
Handsontable.UndoRedo.RemoveColumnAction.prototype.redo = function(instance, redoneCallback) {\n
  instance.addHookOnce(\'afterRemoveCol\', redoneCallback);\n
  instance.alter(\'remove_col\', this.index, this.amount);\n
};\n
function init() {\n
  var instance = this;\n
  var pluginEnabled = typeof instance.getSettings().undo == \'undefined\' || instance.getSettings().undo;\n
  if (pluginEnabled) {\n
    if (!instance.undoRedo) {\n
      instance.undoRedo = new Handsontable.UndoRedo(instance);\n
      exposeUndoRedoMethods(instance);\n
      instance.addHook(\'beforeKeyDown\', onBeforeKeyDown);\n
      instance.addHook(\'afterChange\', onAfterChange);\n
    }\n
  } else {\n
    if (instance.undoRedo) {\n
      delete instance.undoRedo;\n
      removeExposedUndoRedoMethods(instance);\n
      instance.removeHook(\'beforeKeyDown\', onBeforeKeyDown);\n
      instance.removeHook(\'afterChange\', onAfterChange);\n
    }\n
  }\n
}\n
function onBeforeKeyDown(event) {\n
  var instance = this;\n
  var ctrlDown = (event.ctrlKey || event.metaKey) && !event.altKey;\n
  if (ctrlDown) {\n
    if (event.keyCode === 89 || (event.shiftKey && event.keyCode === 90)) {\n
      instance.undoRedo.redo();\n
      event.stopImmediatePropagation();\n
    } else if (event.keyCode === 90) {\n
      instance.undoRedo.undo();\n
      event.stopImmediatePropagation();\n
    }\n
  }\n
}\n
function onAfterChange(changes, source) {\n
  var instance = this;\n
  if (source == \'loadData\') {\n
    return instance.undoRedo.clear();\n
  }\n
}\n
function exposeUndoRedoMethods(instance) {\n
  instance.undo = function() {\n
    return instance.undoRedo.undo();\n
  };\n
  instance.redo = function() {\n
    return instance.undoRedo.redo();\n
  };\n
  instance.isUndoAvailable = function() {\n
    return instance.undoRedo.isUndoAvailable();\n
  };\n
  instance.isRedoAvailable = function() {\n
    return instance.undoRedo.isRedoAvailable();\n
  };\n
  instance.clearUndo = function() {\n
    return instance.undoRedo.clear();\n
  };\n
}\n
function removeExposedUndoRedoMethods(instance) {\n
  delete instance.undo;\n
  delete instance.redo;\n
  delete instance.isUndoAvailable;\n
  delete instance.isRedoAvailable;\n
  delete instance.clearUndo;\n
}\n
Handsontable.hooks.add(\'afterInit\', init);\n
Handsontable.hooks.add(\'afterUpdateSettings\', init);\n
\n
\n
//# \n
},{"./../../helpers.js":46}],73:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  registerRenderer: {get: function() {\n
      return registerRenderer;\n
    }},\n
  getRenderer: {get: function() {\n
      return getRenderer;\n
    }},\n
  hasRenderer: {get: function() {\n
      return hasRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__helpers_46_js__;\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
;\n
var registeredRenderers = {};\n
Handsontable.renderers = Handsontable.renderers || {};\n
Handsontable.renderers.registerRenderer = registerRenderer;\n
Handsontable.renderers.getRenderer = getRenderer;\n
function registerRenderer(rendererName, rendererFunction) {\n
  var registerName;\n
  registeredRenderers[rendererName] = rendererFunction;\n
  registerName = helper.toUpperCaseFirst(rendererName) + \'Renderer\';\n
  Handsontable.renderers[registerName] = rendererFunction;\n
  Handsontable[registerName] = rendererFunction;\n
}\n
function getRenderer(rendererName) {\n
  if (typeof rendererName == \'function\') {\n
    return rendererName;\n
  }\n
  if (typeof rendererName != \'string\') {\n
    throw Error(\'Only strings and functions can be passed as "renderer" parameter\');\n
  }\n
  if (!(rendererName in registeredRenderers)) {\n
    throw Error(\'No editor registered under name "\' + rendererName + \'"\');\n
  }\n
  return registeredRenderers[rendererName];\n
}\n
function hasRenderer(rendererName) {\n
  return rendererName in registeredRenderers;\n
}\n
\n
\n
//# \n
},{"./helpers.js":46}],74:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  cellDecorator: {get: function() {\n
      return cellDecorator;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var registerRenderer = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}).registerRenderer;\n
;\n
registerRenderer(\'base\', cellDecorator);\n
Handsontable.renderers.cellDecorator = cellDecorator;\n
function cellDecorator(instance, TD, row, col, prop, value, cellProperties) {\n
  if (cellProperties.className) {\n
    if (TD.className) {\n
      TD.className = TD.className + " " + cellProperties.className;\n
    } else {\n
      TD.className = cellProperties.className;\n
    }\n
  }\n
  if (cellProperties.readOnly) {\n
    dom.addClass(TD, cellProperties.readOnlyCellClassName);\n
  }\n
  if (cellProperties.valid === false && cellProperties.invalidCellClassName) {\n
    dom.addClass(TD, cellProperties.invalidCellClassName);\n
  } else {\n
    dom.removeClass(TD, cellProperties.invalidCellClassName);\n
  }\n
  if (cellProperties.wordWrap === false && cellProperties.noWordWrapClassName) {\n
    dom.addClass(TD, cellProperties.noWordWrapClassName);\n
  }\n
  if (!value && cellProperties.placeholder) {\n
    dom.addClass(TD, cellProperties.placeholderCellClassName);\n
  }\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../renderers.js":73}],75:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  autocompleteRenderer: {get: function() {\n
      return autocompleteRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_eventManager_46_js__,\n
    $___46__46__47_renderers_46_js__,\n
    $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
var $__1 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__1.getRenderer,\n
    registerRenderer = $__1.registerRenderer;\n
var WalkontableCellCoords = ($___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./../3rdparty/walkontable/src/cell/coords.js"), $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $___46__46__47_3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
;\n
var clonableWRAPPER = document.createElement(\'DIV\');\n
clonableWRAPPER.className = \'htAutocompleteWrapper\';\n
var clonableARROW = document.createElement(\'DIV\');\n
clonableARROW.className = \'htAutocompleteArrow\';\n
clonableARROW.appendChild(document.createTextNode(String.fromCharCode(9660)));\n
var wrapTdContentWithWrapper = function(TD, WRAPPER) {\n
  WRAPPER.innerHTML = TD.innerHTML;\n
  dom.empty(TD);\n
  TD.appendChild(WRAPPER);\n
};\n
registerRenderer(\'autocomplete\', autocompleteRenderer);\n
function autocompleteRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  var WRAPPER = clonableWRAPPER.cloneNode(true);\n
  var ARROW = clonableARROW.cloneNode(true);\n
  getRenderer(\'text\')(instance, TD, row, col, prop, value, cellProperties);\n
  TD.appendChild(ARROW);\n
  dom.addClass(TD, \'htAutocomplete\');\n
  if (!TD.firstChild) {\n
    TD.appendChild(document.createTextNode(String.fromCharCode(160)));\n
  }\n
  if (!instance.acArrowListener) {\n
    var eventManager = eventManagerObject(instance);\n
    instance.acArrowListener = function(event) {\n
      if (dom.hasClass(event.target, \'htAutocompleteArrow\')) {\n
        instance.view.wt.getSetting(\'onCellDblClick\', null, new WalkontableCellCoords(row, col), TD);\n
      }\n
    };\n
    eventManager.addEventListener(instance.rootElement, \'mousedown\', instance.acArrowListener);\n
    instance.addHookOnce(\'afterDestroy\', function() {\n
      eventManager.clear();\n
    });\n
  }\n
}\n
\n
\n
//# \n
},{"./../3rdparty/walkontable/src/cell/coords.js":9,"./../dom.js":31,"./../eventManager.js":45,"./../renderers.js":73}],76:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  checkboxRenderer: {get: function() {\n
      return checkboxRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_helpers_46_js__,\n
    $___46__46__47_eventManager_46_js__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var eventManagerObject = ($___46__46__47_eventManager_46_js__ = require("./../eventManager.js"), $___46__46__47_eventManager_46_js__ && $___46__46__47_eventManager_46_js__.__esModule && $___46__46__47_eventManager_46_js__ || {default: $___46__46__47_eventManager_46_js__}).eventManager;\n
var $__1 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__1.getRenderer,\n
    registerRenderer = $__1.registerRenderer;\n
;\n
registerRenderer(\'checkbox\', checkboxRenderer);\n
var clonableINPUT = document.createElement(\'INPUT\');\n
clonableINPUT.className = \'htCheckboxRendererInput\';\n
clonableINPUT.type = \'checkbox\';\n
clonableINPUT.setAttribute(\'autocomplete\', \'off\');\n
function checkboxRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  var eventManager = eventManagerObject(instance);\n
  if (typeof cellProperties.checkedTemplate === "undefined") {\n
    cellProperties.checkedTemplate = true;\n
  }\n
  if (typeof cellProperties.uncheckedTemplate === "undefined") {\n
    cellProperties.uncheckedTemplate = false;\n
  }\n
  dom.empty(TD);\n
  var INPUT = clonableINPUT.cloneNode(false);\n
  if (value === cellProperties.checkedTemplate || value === helper.stringify(cellProperties.checkedTemplate)) {\n
    INPUT.checked = true;\n
    TD.appendChild(INPUT);\n
  } else if (value === cellProperties.uncheckedTemplate || value === helper.stringify(cellProperties.uncheckedTemplate)) {\n
    TD.appendChild(INPUT);\n
  } else if (value === null) {\n
    INPUT.className += \' noValue\';\n
    TD.appendChild(INPUT);\n
  } else {\n
    dom.fastInnerText(TD, \'#bad value#\');\n
  }\n
  if (cellProperties.readOnly) {\n
    eventManager.addEventListener(INPUT, \'click\', function(event) {\n
      event.preventDefault();\n
    });\n
  } else {\n
    eventManager.addEventListener(INPUT, \'mousedown\', function(event) {\n
      helper.stopPropagation(event);\n
    });\n
    eventManager.addEventListener(INPUT, \'mouseup\', function(event) {\n
      helper.stopPropagation(event);\n
    });\n
    eventManager.addEventListener(INPUT, \'change\', function() {\n
      if (this.checked) {\n
        instance.setDataAtRowProp(row, prop, cellProperties.checkedTemplate);\n
      } else {\n
        instance.setDataAtRowProp(row, prop, cellProperties.uncheckedTemplate);\n
      }\n
    });\n
  }\n
  if (!instance.CheckboxRenderer || !instance.CheckboxRenderer.beforeKeyDownHookBound) {\n
    instance.CheckboxRenderer = {beforeKeyDownHookBound: true};\n
    instance.addHook(\'beforeKeyDown\', function(event) {\n
      dom.enableImmediatePropagation(event);\n
      if (event.keyCode == helper.keyCode.SPACE || event.keyCode == helper.keyCode.ENTER) {\n
        var cell,\n
            checkbox,\n
            cellProperties;\n
        var selRange = instance.getSelectedRange();\n
        var topLeft = selRange.getTopLeftCorner();\n
        var bottomRight = selRange.getBottomRightCorner();\n
        for (var row = topLeft.row; row <= bottomRight.row; row++) {\n
          for (var col = topLeft.col; col <= bottomRight.col; col++) {\n
            cell = instance.getCell(row, col);\n
            cellProperties = instance.getCellMeta(row, col);\n
            checkbox = cell.querySelectorAll(\'input[type=checkbox]\');\n
            if (checkbox.length > 0 && !cellProperties.readOnly) {\n
              if (!event.isImmediatePropagationStopped()) {\n
                event.stopImmediatePropagation();\n
                event.preventDefault();\n
              }\n
              for (var i = 0,\n
                  len = checkbox.length; i < len; i++) {\n
                checkbox[i].checked = !checkbox[i].checked;\n
                eventManager.fireEvent(checkbox[i], \'change\');\n
              }\n
            }\n
          }\n
        }\n
      }\n
    });\n
  }\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../eventManager.js":45,"./../helpers.js":46,"./../renderers.js":73}],77:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  htmlRenderer: {get: function() {\n
      return htmlRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__0.getRenderer,\n
    registerRenderer = $__0.registerRenderer;\n
;\n
registerRenderer(\'html\', htmlRenderer);\n
function htmlRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  getRenderer(\'base\').apply(this, arguments);\n
  dom.fastInnerHTML(TD, value);\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../renderers.js":73}],78:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  numericRenderer: {get: function() {\n
      return numericRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_helpers_46_js__,\n
    $__numeral__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var numeral = ($__numeral__ = require("numeral"), $__numeral__ && $__numeral__.__esModule && $__numeral__ || {default: $__numeral__}).default;\n
var $__1 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__1.getRenderer,\n
    registerRenderer = $__1.registerRenderer;\n
;\n
registerRenderer(\'numeric\', numericRenderer);\n
function numericRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  if (helper.isNumeric(value)) {\n
    if (typeof cellProperties.language !== \'undefined\') {\n
      numeral.language(cellProperties.language);\n
    }\n
    value = numeral(value).format(cellProperties.format || \'0\');\n
    dom.addClass(TD, \'htNumeric\');\n
  }\n
  getRenderer(\'text\')(instance, TD, row, col, prop, value, cellProperties);\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../helpers.js":46,"./../renderers.js":73,"numeral":"numeral"}],79:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  passwordRenderer: {get: function() {\n
      return passwordRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var $__0 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__0.getRenderer,\n
    registerRenderer = $__0.registerRenderer;\n
;\n
registerRenderer(\'password\', passwordRenderer);\n
function passwordRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  getRenderer(\'text\').apply(this, arguments);\n
  value = TD.innerHTML;\n
  var hash;\n
  var hashLength = cellProperties.hashLength || value.length;\n
  var hashSymbol = cellProperties.hashSymbol || \'*\';\n
  for (hash = \'\'; hash.split(hashSymbol).length - 1 < hashLength; hash += hashSymbol) {}\n
  dom.fastInnerHTML(TD, hash);\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../renderers.js":73}],80:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  textRenderer: {get: function() {\n
      return textRenderer;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $___46__46__47_dom_46_js__,\n
    $___46__46__47_helpers_46_js__,\n
    $___46__46__47_renderers_46_js__;\n
var dom = ($___46__46__47_dom_46_js__ = require("./../dom.js"), $___46__46__47_dom_46_js__ && $___46__46__47_dom_46_js__.__esModule && $___46__46__47_dom_46_js__ || {default: $___46__46__47_dom_46_js__});\n
var helper = ($___46__46__47_helpers_46_js__ = require("./../helpers.js"), $___46__46__47_helpers_46_js__ && $___46__46__47_helpers_46_js__.__esModule && $___46__46__47_helpers_46_js__ || {default: $___46__46__47_helpers_46_js__});\n
var $__0 = ($___46__46__47_renderers_46_js__ = require("./../renderers.js"), $___46__46__47_renderers_46_js__ && $___46__46__47_renderers_46_js__.__esModule && $___46__46__47_renderers_46_js__ || {default: $___46__46__47_renderers_46_js__}),\n
    getRenderer = $__0.getRenderer,\n
    registerRenderer = $__0.registerRenderer;\n
;\n
registerRenderer(\'text\', textRenderer);\n
function textRenderer(instance, TD, row, col, prop, value, cellProperties) {\n
  getRenderer(\'base\').apply(this, arguments);\n
  if (!value && cellProperties.placeholder) {\n
    value = cellProperties.placeholder;\n
  }\n
  var escaped = helper.stringify(value);\n
  if (!instance.getSettings().trimWhitespace) {\n
    escaped = escaped.replace(/ /g, String.fromCharCode(160));\n
  }\n
  if (cellProperties.rendererTemplate) {\n
    dom.empty(TD);\n
    var TEMPLATE = document.createElement(\'TEMPLATE\');\n
    TEMPLATE.setAttribute(\'bind\', \'{{}}\');\n
    TEMPLATE.innerHTML = cellProperties.rendererTemplate;\n
    HTMLTemplateElement.decorate(TEMPLATE);\n
    TEMPLATE.model = instance.getSourceDataAtRow(row);\n
    TD.appendChild(TEMPLATE);\n
  } else {\n
    dom.fastInnerText(TD, escaped);\n
  }\n
}\n
\n
\n
//# \n
},{"./../dom.js":31,"./../helpers.js":46,"./../renderers.js":73}],81:[function(require,module,exports){\n
"use strict";\n
if (!Array.prototype.filter) {\n
  Array.prototype.filter = function(fun, thisp) {\n
    "use strict";\n
    if (typeof this === "undefined" || this === null) {\n
      throw new TypeError();\n
    }\n
    if (typeof fun !== "function") {\n
      throw new TypeError();\n
    }\n
    thisp = thisp || this;\n
    if (isNodeList(thisp)) {\n
      thisp = convertNodeListToArray(thisp);\n
    }\n
    var len = thisp.length,\n
        res = [],\n
        i,\n
        val;\n
    for (i = 0; i < len; i += 1) {\n
      if (thisp.hasOwnProperty(i)) {\n
        val = thisp[i];\n
        if (fun.call(thisp, val, i, thisp)) {\n
          res.push(val);\n
        }\n
      }\n
    }\n
    return res;\n
    function isNodeList(object) {\n
      return /NodeList/i.test(object.item);\n
    }\n
    function convertNodeListToArray(nodeList) {\n
      var array = [];\n
      for (var i = 0,\n
          len = nodeList.length; i < len; i++) {\n
        array[i] = nodeList[i];\n
      }\n
      return array;\n
    }\n
  };\n
}\n
\n
\n
//# \n
},{}],82:[function(require,module,exports){\n
"use strict";\n
if (!Array.prototype.indexOf) {\n
  Array.prototype.indexOf = function(elt) {\n
    var len = this.length >>> 0;\n
    var from = Number(arguments[1]) || 0;\n
    from = (from < 0) ? Math.ceil(from) : Math.floor(from);\n
    if (from < 0) {\n
      from += len;\n
    }\n
    for (; from < len; from++) {\n
      if (from in this && this[from] === elt) {\n
        return from;\n
      }\n
    }\n
    return -1;\n
  };\n
}\n
\n
\n
//# \n
},{}],83:[function(require,module,exports){\n
"use strict";\n
if (!Array.isArray) {\n
  Array.isArray = function(obj) {\n
    return Object.prototype.toString.call(obj) == \'[object Array]\';\n
  };\n
}\n
\n
\n
//# \n
},{}],84:[function(require,module,exports){\n
"use strict";\n
(function(global) {\n
  \'use strict\';\n
  if (global.$traceurRuntime) {\n
    return;\n
  }\n
  var $Object = Object;\n
  var $TypeError = TypeError;\n
  var $create = $Object.create;\n
  var $defineProperties = $Object.defineProperties;\n
  var $defineProperty = $Object.defineProperty;\n
  var $freeze = $Object.freeze;\n
  var $getOwnPropertyDescriptor = $Object.getOwnPropertyDescriptor;\n
  var $getOwnPropertyNames = $Object.getOwnPropertyNames;\n
  var $keys = $Object.keys;\n
  var $hasOwnProperty = $Object.prototype.hasOwnProperty;\n
  var $toString = $Object.prototype.toString;\n
  var $preventExtensions = Object.preventExtensions;\n
  var $seal = Object.seal;\n
  var $isExtensible = Object.isExtensible;\n
  function nonEnum(value) {\n
    return {\n
      configurable: true,\n
      enumerable: false,\n
      value: value,\n
      writable: true\n
    };\n
  }\n
  var method = nonEnum;\n
  var counter = 0;\n
  function newUniqueString() {\n
    return \'__$\' + Math.floor(Math.random() * 1e9) + \'$\' + ++counter + \'$__\';\n
  }\n
  var symbolInternalProperty = newUniqueString();\n
  var symbolDescriptionProperty = newUniqueString();\n
  var symbolDataProperty = newUniqueString();\n
  var symbolValues = $create(null);\n
  var privateNames = $create(null);\n
  function isPrivateName(s) {\n
    return privateNames[s];\n
  }\n
  function createPrivateName() {\n
    var s = newUniqueString();\n
    privateNames[s] = true;\n
    return s;\n
  }\n
  function isShimSymbol(symbol) {\n
    return typeof symbol === \'object\' && symbol instanceof SymbolValue;\n
  }\n
  function typeOf(v) {\n
    if (isShimSymbol(v))\n
      return \'symbol\';\n
    return typeof v;\n
  }\n
  function Symbol(description) {\n
    var value = new SymbolValue(description);\n
    if (!(this instanceof Symbol))\n
      return value;\n
    throw new TypeError(\'Symbol cannot be new\\\'ed\');\n
  }\n
  $defineProperty(Symbol.prototype, \'constructor\', nonEnum(Symbol));\n
  $defineProperty(Symbol.prototype, \'toString\', method(function() {\n
    var symbolValue = this[symbolDataProperty];\n
    if (!getOption(\'symbols\'))\n
      return symbolValue[symbolInternalProperty];\n
    if (!symbolValue)\n
      throw TypeError(\'Conversion from symbol to string\');\n
    var desc = symbolValue[symbolDescriptionProperty];\n
    if (desc === undefined)\n
      desc = \'\';\n
    return \'Symbol(\' + desc + \')\';\n
  }));\n
  $defineProperty(Symbol.prototype, \'valueOf\', method(function() {\n
    var symbolValue = this[symbolDataProperty];\n
    if (!symbolValue)\n
      throw TypeError(\'Conversion from symbol to string\');\n
    if (!getOption(\'symbols\'))\n
      return symbolValue[symbolInternalProperty];\n
    return symbolValue;\n
  }));\n
  function SymbolValue(description) {\n
    var key = newUniqueString();\n
    $defineProperty(this, symbolDataProperty, {value: this});\n
    $defineProperty(this, symbolInternalProperty, {value: key});\n
    $defineProperty(this, symbolDescriptionProperty, {value: description});\n
    freeze(this);\n
    symbolValues[key] = this;\n
  }\n
  $defineProperty(SymbolValue.prototype, \'constructor\', nonEnum(Symbol));\n
  $defineProperty(SymbolValue.prototype, \'toString\', {\n
    value: Symbol.prototype.toString,\n
    enumerable: false\n
  });\n
  $defineProperty(SymbolValue.prototype, \'valueOf\', {\n
    value: Symbol.prototype.valueOf,\n
    enumerable: false\n
  });\n
  var hashProperty = createPrivateName();\n
  var hashPropertyDescriptor = {value: undefined};\n
  var hashObjectProperties = {\n
    hash: {value: undefined},\n
    self: {value: undefined}\n
  };\n
  var hashCounter = 0;\n
  function getOwnHashObject(object) {\n
    var hashObject = object[hashProperty];\n
    if (hashObject && hashObject.self === object)\n
      return hashObject;\n
    if ($isExtensible(object)) {\n
      hashObjectProperties.hash.value = hashCounter++;\n
      hashObjectProperties.self.value = object;\n
      hashPropertyDescriptor.value = $create(null, hashObjectProperties);\n
      $defineProperty(object, hashProperty, hashPropertyDescriptor);\n
      return hashPropertyDescriptor.value;\n
    }\n
    return undefined;\n
  }\n
  function freeze(object) {\n
    getOwnHashObject(object);\n
    return $freeze.apply(this, arguments);\n
  }\n
  function preventExtensions(object) {\n
    getOwnHashObject(object);\n
    return $preventExtensions.apply(this, arguments);\n
  }\n
  function seal(object) {\n
    getOwnHashObject(object);\n
    return $seal.apply(this, arguments);\n
  }\n
  freeze(SymbolValue.prototype);\n
  function isSymbolString(s) {\n
    return symbolValues[s] || privateNames[s];\n
  }\n
  function toProperty(name) {\n
    if (isShimSymbol(name))\n
      return name[symbolInternalProperty];\n
    return name;\n
  }\n
  function removeSymbolKeys(array) {\n
    var rv = [];\n
    for (var i = 0; i < array.length; i++) {\n
      if (!isSymbolString(array[i])) {\n
        rv.push(array[i]);\n
      }\n
    }\n
    return rv;\n
  }\n
  function getOwnPropertyNames(object) {\n
    return removeSymbolKeys($getOwnPropertyNames(object));\n
  }\n
  function keys(object) {\n
    return removeSymbolKeys($keys(object));\n
  }\n
  function getOwnPropertySymbols(object) {\n
    var rv = [];\n
    var names = $getOwnPropertyNames(object);\n
    for (var i = 0; i < names.length; i++) {\n
      var symbol = symbolValues[names[i]];\n
      if (symbol) {\n
        rv.push(symbol);\n
      }\n
    }\n
    return rv;\n
  }\n
  function getOwnPropertyDescriptor(object, name) {\n
    return $getOwnPropertyDescriptor(object, toProperty(name));\n
  }\n
  function hasOwnProperty(name) {\n
    return $hasOwnProperty.call(this, toProperty(name));\n
  }\n
  function getOption(name) {\n
    return global.traceur && global.traceur.options[name];\n
  }\n
  function defineProperty(object, name, descriptor) {\n
    if (isShimSymbol(name)) {\n
      name = name[symbolInternalProperty];\n
    }\n
    $defineProperty(object, name, descriptor);\n
    return object;\n
  }\n
  function polyfillObject(Object) {\n
    $defineProperty(Object, \'defineProperty\', {value: defineProperty});\n
    $defineProperty(Object, \'getOwnPropertyNames\', {value: getOwnPropertyNames});\n
    $defineProperty(Object, \'getOwnPropertyDescriptor\', {value: getOwnPropertyDescriptor});\n
    $defineProperty(Object.prototype, \'hasOwnProperty\', {value: hasOwnProperty});\n
    $defineProperty(Object, \'freeze\', {value: freeze});\n
    $defineProperty(Object, \'preventExtensions\', {value: preventExtensions});\n
    $defineProperty(Object, \'seal\', {value: seal});\n
    $defineProperty(Object, \'keys\', {value: keys});\n
  }\n
  function exportStar(object) {\n
    for (var i = 1; i < arguments.length; i++) {\n
      var names = $getOwnPropertyNames(arguments[i]);\n
      for (var j = 0; j < names.length; j++) {\n
        var name = names[j];\n
        if (isSymbolString(name))\n
          continue;\n
        (function(mod, name) {\n
          $defineProperty(object, name, {\n
            get: function() {\n
              return mod[name];\n
            },\n
            enumerable: true\n
          });\n
        })(arguments[i], names[j]);\n
      }\n
    }\n
    return object;\n
  }\n
  function isObject(x) {\n
    return x != null && (typeof x === \'object\' || typeof x === \'function\');\n
  }\n
  function toObject(x) {\n
    if (x == null)\n
      throw $TypeError();\n
    return $Object(x);\n
  }\n
  function checkObjectCoercible(argument) {\n
    if (argument == null) {\n
      throw new TypeError(\'Value cannot be converted to an Object\');\n
    }\n
    return argument;\n
  }\n
  function polyfillSymbol(global, Symbol) {\n
    if (!global.Symbol) {\n
      global.Symbol = Symbol;\n
      Object.getOwnPropertySymbols = getOwnPropertySymbols;\n
    }\n
    if (!global.Symbol.iterator) {\n
      global.Symbol.iterator = Symbol(\'Symbol.iterator\');\n
    }\n
  }\n
  function setupGlobals(global) {\n
    polyfillSymbol(global, Symbol);\n
    global.Reflect = global.Reflect || {};\n
    global.Reflect.global = global.Reflect.global || global;\n
    polyfillObject(global.Object);\n
  }\n
  setupGlobals(global);\n
  global.$traceurRuntime = {\n
    checkObjectCoercible: checkObjectCoercible,\n
    createPrivateName: createPrivateName,\n
    defineProperties: $defineProperties,\n
    defineProperty: $defineProperty,\n
    exportStar: exportStar,\n
    getOwnHashObject: getOwnHashObject,\n
    getOwnPropertyDescriptor: $getOwnPropertyDescriptor,\n
    getOwnPropertyNames: $getOwnPropertyNames,\n
    isObject: isObject,\n
    isPrivateName: isPrivateName,\n
    isSymbolString: isSymbolString,\n
    keys: $keys,\n
    setupGlobals: setupGlobals,\n
    toObject: toObject,\n
    toProperty: toProperty,\n
    typeof: typeOf\n
  };\n
})(window);\n
(function() {\n
  \'use strict\';\n
  var path;\n
  function relativeRequire(callerPath, requiredPath) {\n
    path = path || typeof require !== \'undefined\' && require(\'path\');\n
    function isDirectory(path) {\n
      return path.slice(-1) === \'/\';\n
    }\n
    function isAbsolute(path) {\n
      return path[0] === \'/\';\n
    }\n
    function isRelative(path) {\n
      return path[0] === \'.\';\n
    }\n
    if (isDirectory(requiredPath) || isAbsolute(requiredPath))\n
      return;\n
    return isRelative(requiredPath) ? require(path.resolve(path.dirname(callerPath), requiredPath)) : require(requiredPath);\n
  }\n
  $traceurRuntime.require = relativeRequire;\n
})();\n
(function() {\n
  \'use strict\';\n
  function spread() {\n
    var rv = [],\n
        j = 0,\n
        iterResult;\n
    for (var i = 0; i < arguments.length; i++) {\n
      var valueToSpread = $traceurRuntime.checkObjectCoercible(arguments[i]);\n
      if (typeof valueToSpread[$traceurRuntime.toProperty(Symbol.iterator)] !== \'function\') {\n
        throw new TypeError(\'Cannot spread non-iterable object.\');\n
      }\n
      var iter = valueToSpread[$traceurRuntime.toProperty(Symbol.iterator)]();\n
      while (!(iterResult = iter.next()).done) {\n
        rv[j++] = iterResult.value;\n
      }\n
    }\n
    return rv;\n
  }\n
  $traceurRuntime.spread = spread;\n
})();\n
(function() {\n
  \'use strict\';\n
  var $Object = Object;\n
  var $TypeError = TypeError;\n
  var $create = $Object.create;\n
  var $defineProperties = $traceurRuntime.defineProperties;\n
  var $defineProperty = $traceurRuntime.defineProperty;\n
  var $getOwnPropertyDescriptor = $traceurRuntime.getOwnPropertyDescriptor;\n
  var $getOwnPropertyNames = $traceurRuntime.getOwnPropertyNames;\n
  var $getPrototypeOf = Object.getPrototypeOf;\n
  var $__0 = Object,\n
      getOwnPropertyNames = $__0.getOwnPropertyNames,\n
      getOwnPropertySymbols = $__0.getOwnPropertySymbols;\n
  function superDescriptor(homeObject, name) {\n
    var proto = $getPrototypeOf(homeObject);\n
    do {\n
      var result = $getOwnPropertyDescriptor(proto, name);\n
      if (result)\n
        return result;\n
      proto = $getPrototypeOf(proto);\n
    } while (proto);\n
    return undefined;\n
  }\n
  function superConstructor(ctor) {\n
    return ctor.__proto__;\n
  }\n
  function superCall(self, homeObject, name, args) {\n
    return superGet(self, homeObject, name).apply(self, args);\n
  }\n
  function superGet(self, homeObject, name) {\n
    var descriptor = superDescriptor(homeObject, name);\n
    if (descriptor) {\n
      if (!descriptor.get)\n
        return descriptor.value;\n
      return descriptor.get.call(self);\n
    }\n
    return undefined;\n
  }\n
  function superSet(self, homeObject, name, value) {\n
    var descriptor = superDescriptor(homeObject, name);\n
    if (descriptor && descriptor.set) {\n
      descriptor.set.call(self, value);\n
      return value;\n
    }\n
    throw $TypeError(("super has no setter \'" + name + "\'."));\n
  }\n
  function getDescriptors(object) {\n
    var descriptors = {};\n
    var names = getOwnPropertyNames(object);\n
    for (var i = 0; i < names.length; i++) {\n
      var name = names[i];\n
      descriptors[name] = $getOwnPropertyDescriptor(object, name);\n
    }\n
    var symbols = getOwnPropertySymbols(object);\n
    for (var i = 0; i < symbols.length; i++) {\n
      var symbol = symbols[i];\n
      descriptors[$traceurRuntime.toProperty(symbol)] = $getOwnPropertyDescriptor(object, $traceurRuntime.toProperty(symbol));\n
    }\n
    return descriptors;\n
  }\n
  function createClass(ctor, object, staticObject, superClass) {\n
    $defineProperty(object, \'constructor\', {\n
      value: ctor,\n
      configurable: true,\n
      enumerable: false,\n
      writable: true\n
    });\n
    if (arguments.length > 3) {\n
      if (typeof superClass === \'function\')\n
        ctor.__proto__ = superClass;\n
      ctor.prototype = $create(getProtoParent(superClass), getDescriptors(object));\n
    } else {\n
      ctor.prototype = object;\n
    }\n
    $defineProperty(ctor, \'prototype\', {\n
      configurable: false,\n
      writable: false\n
    });\n
    return $defineProperties(ctor, getDescriptors(staticObject));\n
  }\n
  function getProtoParent(superClass) {\n
    if (typeof superClass === \'function\') {\n
      var prototype = superClass.prototype;\n
      if ($Object(prototype) === prototype || prototype === null)\n
        return superClass.prototype;\n
      throw new $TypeError(\'super prototype must be an Object or null\');\n
    }\n
    if (superClass === null)\n
      return null;\n
    throw new $TypeError(("Super expression must either be null or a function, not " + typeof superClass + "."));\n
  }\n
  function defaultSuperCall(self, homeObject, args) {\n
    if ($getPrototypeOf(homeObject) !== null)\n
      superCall(self, homeObject, \'constructor\', args);\n
  }\n
  $traceurRuntime.createClass = createClass;\n
  $traceurRuntime.defaultSuperCall = defaultSuperCall;\n
  $traceurRuntime.superCall = superCall;\n
  $traceurRuntime.superConstructor = superConstructor;\n
  $traceurRuntime.superGet = superGet;\n
  $traceurRuntime.superSet = superSet;\n
})();\n
\n
\n
//# \n
},{"path":undefined}],85:[function(require,module,exports){\n
"use strict";\n
if (!Object.keys) {\n
  Object.keys = (function() {\n
    \'use strict\';\n
    var hasOwnProperty = Object.prototype.hasOwnProperty,\n
        hasDontEnumBug = !({toString: null}).propertyIsEnumerable(\'toString\'),\n
        dontEnums = [\'toString\', \'toLocaleString\', \'valueOf\', \'hasOwnProperty\', \'isPrototypeOf\', \'propertyIsEnumerable\', \'constructor\'],\n
        dontEnumsLength = dontEnums.length;\n
    return function(obj) {\n
      if (typeof obj !== \'object\' && (typeof obj !== \'function\' || obj === null)) {\n
        throw new TypeError(\'Object.keys called on non-object\');\n
      }\n
      var result = [],\n
          prop,\n
          i;\n
      for (prop in obj) {\n
        if (hasOwnProperty.call(obj, prop)) {\n
          result.push(prop);\n
        }\n
      }\n
      if (hasDontEnumBug) {\n
        for (i = 0; i < dontEnumsLength; i++) {\n
          if (hasOwnProperty.call(obj, dontEnums[i])) {\n
            result.push(dontEnums[i]);\n
          }\n
        }\n
      }\n
      return result;\n
    };\n
  }());\n
}\n
\n
\n
//# \n
},{}],86:[function(require,module,exports){\n
"use strict";\n
if (!String.prototype.trim) {\n
  var trimRegex = /^\\s+|\\s+$/g;\n
  String.prototype.trim = function() {\n
    return this.replace(trimRegex, \'\');\n
  };\n
}\n
\n
\n
//# \n
},{}],87:[function(require,module,exports){\n
"use strict";\n
if (typeof WeakMap === \'undefined\') {\n
  (function() {\n
    var defineProperty = Object.defineProperty;\n
    try {\n
      var properDefineProperty = true;\n
      defineProperty(function() {}, \'foo\', {});\n
    } catch (e) {\n
      properDefineProperty = false;\n
    }\n
    var counter = +(new Date) % 1e9;\n
    var WeakMap = function() {\n
      this.name = \'__st\' + (Math.random() * 1e9 >>> 0) + (counter++ + \'__\');\n
      if (!properDefineProperty) {\n
        this._wmCache = [];\n
      }\n
    };\n
    if (properDefineProperty) {\n
      WeakMap.prototype = {\n
        set: function(key, value) {\n
          var entry = key[this.name];\n
          if (entry && entry[0] === key)\n
            entry[1] = value;\n
          else\n
            defineProperty(key, this.name, {\n
              value: [key, value],\n
              writable: true\n
            });\n
        },\n
        get: function(key) {\n
          var entry;\n
          return (entry = key[this.name]) && entry[0] === key ? entry[1] : undefined;\n
        },\n
        has: function(key) {\n
          this.get(key) ? true : false;\n
        },\n
        \'delete\': function(key) {\n
          this.set(key, undefined);\n
        }\n
      };\n
    } else {\n
      WeakMap.prototype = {\n
        set: function(key, value) {\n
          if (typeof key == \'undefined\' || typeof value == \'undefined\')\n
            return;\n
          for (var i = 0,\n
              len = this._wmCache.length; i < len; i++) {\n
            if (this._wmCache[i].key == key) {\n
              this._wmCache[i].value = value;\n
              return;\n
            }\n
          }\n
          this._wmCache.push({\n
            key: key,\n
            value: value\n
          });\n
        },\n
        get: function(key) {\n
          if (typeof key == \'undefined\')\n
            return;\n
          for (var i = 0,\n
              len = this._wmCache.length; i < len; i++) {\n
            if (this._wmCache[i].key == key) {\n
              return this._wmCache[i].value;\n
            }\n
          }\n
          return;\n
        },\n
        has: function(key) {\n
          this.get(key) ? true : false;\n
        },\n
        \'delete\': function(key) {\n
          if (typeof key == \'undefined\')\n
            return;\n
          for (var i = 0,\n
              len = this._wmCache.length; i < len; i++) {\n
            if (this._wmCache[i].key == key) {\n
              Array.prototype.slice.call(this._wmCache, i, 1);\n
            }\n
          }\n
        }\n
      };\n
    }\n
    window.WeakMap = WeakMap;\n
  })();\n
}\n
\n
\n
//# \n
},{}],88:[function(require,module,exports){\n
"use strict";\n
Object.defineProperties(exports, {\n
  TableView: {get: function() {\n
      return TableView;\n
    }},\n
  __esModule: {value: true}\n
});\n
var $__dom_46_js__,\n
    $__helpers_46_js__,\n
    $__eventManager_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_selection_46_js__,\n
    $__3rdparty_47_walkontable_47_src_47_core_46_js__;\n
var dom = ($__dom_46_js__ = require("./dom.js"), $__dom_46_js__ && $__dom_46_js__.__esModule && $__dom_46_js__ || {default: $__dom_46_js__});\n
var helper = ($__helpers_46_js__ = require("./helpers.js"), $__helpers_46_js__ && $__helpers_46_js__.__esModule && $__helpers_46_js__ || {default: $__helpers_46_js__});\n
var eventManagerObject = ($__eventManager_46_js__ = require("./eventManager.js"), $__eventManager_46_js__ && $__eventManager_46_js__.__esModule && $__eventManager_46_js__ || {default: $__eventManager_46_js__}).eventManager;\n
var WalkontableCellCoords = ($__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ = require("./3rdparty/walkontable/src/cell/coords.js"), $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_cell_47_coords_46_js__}).WalkontableCellCoords;\n
var WalkontableSelection = ($__3rdparty_47_walkontable_47_src_47_selection_46_js__ = require("./3rdparty/walkontable/src/selection.js"), $__3rdparty_47_walkontable_47_src_47_selection_46_js__ && $__3rdparty_47_walkontable_47_src_47_selection_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_selection_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_selection_46_js__}).WalkontableSelection;\n
var Walkontable = ($__3rdparty_47_walkontable_47_src_47_core_46_js__ = require("./3rdparty/walkontable/src/core.js"), $__3rdparty_47_walkontable_47_src_47_core_46_js__ && $__3rdparty_47_walkontable_47_src_47_core_46_js__.__esModule && $__3rdparty_47_walkontable_47_src_47_core_46_js__ || {default: $__3rdparty_47_walkontable_47_src_47_core_46_js__}).Walkontable;\n
Handsontable.TableView = TableView;\n
function TableView(instance) {\n
  var that = this;\n
  this.eventManager = eventManagerObject(instance);\n
  this.instance = instance;\n
  this.settings = instance.getSettings();\n
  var originalStyle = instance.rootElement.getAttribute(\'style\');\n
  if (originalStyle) {\n
    instance.rootElement.setAttribute(\'data-originalstyle\', originalStyle);\n
  }\n
  dom.addClass(instance.rootElement, \'handsontable\');\n
  var table = document.createElement(\'TABLE\');\n
  table.className = \'htCore\';\n
  this.THEAD = document.createElement(\'THEAD\');\n
  table.appendChild(this.THEAD);\n
  this.TBODY = document.createElement(\'TBODY\');\n
  table.appendChild(this.TBODY);\n
  instance.table = table;\n
  instance.container.insertBefore(table, instance.container.firstChild);\n
  this.eventManager.addEventListener(instance.rootElement, \'mousedown\', function(event) {\n
    if (!that.isTextSelectionAllowed(event.target)) {\n
      clearTextSelection();\n
      event.preventDefault();\n
      window.focus();\n
    }\n
  });\n
  this.eventManager.addEventListener(document.documentElement, \'keyup\', function(event) {\n
    if (instance.selection.isInProgress() && !event.shiftKey) {\n
      instance.selection.finish();\n
    }\n
  });\n
  var isMouseDown;\n
  this.isMouseDown = function() {\n
    return isMouseDown;\n
  };\n
  this.eventManager.addEventListener(document.documentElement, \'mouseup\', function(event) {\n
    if (instance.selection.isInProgress() && event.which === 1) {\n
      instance.selection.finish();\n
    }\n
    isMouseDown = false;\n
    if (helper.isOutsideInput(document.activeElement)) {\n
      instance.unlisten();\n
    }\n
  });\n
  this.eventManager.addEventListener(document.documentElement, \'mousedown\', function(event) {\n
    var next = event.target;\n
    if (isMouseDown) {\n
      return;\n
    }\n
    if (next !== instance.view.wt.wtTable.holder) {\n
      while (next !== document.documentElement) {\n
        if (next === null) {\n
          if (event.isTargetWebComponent) {\n
            break;\n
          }\n
          return;\n
        }\n
        if (next === instance.rootElement) {\n
          return;\n
        }\n
        next = next.parentNode;\n
      }\n
    } else {\n
      var scrollbarWidth = Handsontable.Dom.getScrollbarWidth();\n
      if (document.elementFromPoint(event.x + scrollbarWidth, event.y) !== instance.view.wt.wtTable.holder || document.elementFromPoint(event.x, event.y + scrollbarWidth) !== instance.view.wt.wtTable.holder) {\n
        return;\n
      }\n
    }\n
    if (that.settings.outsideClickDeselects) {\n
      instance.deselectCell();\n
    } else {\n
      instance.destroyEditor();\n
    }\n
  });\n
  this.eventManager.addEventListener(table, \'selectstart\', function(event) {\n
    if (that.settings.fragmentSelection) {\n
      return;\n
    }\n
    event.preventDefault();\n
  });\n
  var clearTextSelection = function() {\n
    if (window.getSelection) {\n
      if (window.getSelection().empty) {\n
        window.getSelection().empty();\n
      } else if (window.getSelection().removeAllRanges) {\n
        window.getSelection().removeAllRanges();\n
      }\n
    } else if (document.selection) {\n
      document.selection.empty();\n
    }\n
  };\n
  var selections = [new WalkontableSelection({\n
    className: \'current\',\n
    border: {\n
      width: 2,\n
      color: \'#5292F7\',\n
      cornerVisible: function() {\n
        return that.settings.fillHandle && !that.isCellEdited() && !instance.selection.isMultiple();\n
      },\n
      multipleSelectionHandlesVisible: function() {\n
        return !that.isCellEdited() && !instance.selection.isMultiple();\n
      }\n
    }\n
  }), new WalkontableSelection({\n
    className: \'area\',\n
    border: {\n
      width: 1,\n
      color: \'#89AFF9\',\n
      cornerVisible: function() {\n
        return that.settings.fillHandle && !that.isCellEdited() && instance.selection.isMultiple();\n
      },\n
      multipleSelectionHandlesVisible: function() {\n
        return !that.isCellEdited() && instance.selection.isMultiple();\n
      }\n
    }\n
  }), new WalkontableSelection({\n
    className: \'highlight\',\n
    highlightRowClassName: that.settings.currentRowClassName,\n
    highlightColumnClassName: that.settings.currentColClassName\n
  }), new WalkontableSelection({\n
    className: \'fill\',\n
    border: {\n
      width: 1,\n
      color: \'red\'\n
    }\n
  })];\n
  selections.current = selections[0];\n
  selections.area = selections[1];\n
  selections.highlight = selections[2];\n
  selections.fill = selections[3];\n
  var walkontableConfig = {\n
    debug: function() {\n
      return that.settings.debug;\n
    },\n
    table: table,\n
    stretchH: this.settings.stretchH,\n
    data: instance.getDataAtCell,\n
    totalRows: instance.countRows,\n
    totalColumns: instance.countCols,\n
    fixedColumnsLeft: function() {\n
      return that.settings.fixedColumnsLeft;\n
    },\n
    fixedRowsTop: function() {\n
      return that.settings.fixedRowsTop;\n
    },\n
    renderAllRows: that.settings.renderAllRows,\n
    rowHeaders: function() {\n
      var arr = [];\n
      if (instance.hasRowHeaders()) {\n
        arr.push(function(index, TH) {\n
          that.appendRowHeader(index, TH);\n
        });\n
      }\n
      Handsontable.hooks.run(instance, \'afterGetRowHeaderRenderers\', arr);\n
      return arr;\n
    },\n
    columnHeaders: function() {\n
      var arr = [];\n
      if (instance.hasColHeaders()) {\n
        arr.push(function(index, TH) {\n
          that.appendColHeader(index, TH);\n
        });\n
      }\n
      Handsontable.hooks.run(instance, \'afterGetColumnHeaderRenderers\', arr);\n
      return arr;\n
    },\n
    columnWidth: instance.getColWidth,\n
    rowHeight: instance.getRowHeight,\n
    cellRenderer: function(row, col, TD) {\n
      var prop = that.instance.colToProp(col),\n
          cellProperties = that.instance.getCellMeta(row, col),\n
          renderer = that.instance.getCellRenderer(cellProperties);\n
      var value = that.instance.getDataAtRowProp(row, prop);\n
      renderer(that.instance, TD, row, col, prop, value, cellProperties);\n
      Handsontable.hooks.run(that.instance, \'afterRenderer\', TD, row, col, prop, value, cellProperties);\n
    },\n
    selections: selections,\n
    hideBorderOnMouseDownOver: function() {\n
      return that.settings.fragmentSelection;\n
    },\n
    onCellMouseDown: function(event, coords, TD, wt) {\n
      instance.listen();\n
      that.activeWt = wt;\n
      isMouseDown = true;\n
      dom.enableImmediatePropagation(event);\n
      Handsontable.hooks.run(instance, \'beforeOnCellMouseDown\', event, coords, TD);\n
      if (!event.isImmediatePropagationStopped()) {\n
        if (event.button === 2 && instance.selection.inInSelection(coords)) {} else if (event.shiftKey) {\n
          if (coords.row >= 0 && coords.col >= 0) {\n
            instance.selection.setRangeEnd(coords);\n
          }\n
        } else {\n
          if ((coords.row < 0 || coords.col < 0) && (coords.row >= 0 || coords.col >= 0)) {\n
            if (coords.row < 0) {\n
              instance.selectCell(0, coords.col, instance.countRows() - 1, coords.col);\n
              instance.selection.setSelectedHeaders(false, true);\n
            }\n
            if (coords.col < 0) {\n
              instance.selectCell(coords.row, 0, coords.row, instance.countCols() - 1);\n
              instance.selection.setSelectedHeaders(true, false);\n
            }\n
          } else {\n
            coords.row = coords.row < 0 ? 0 : coords.row;\n
            coords.col = coords.col < 0 ? 0 : coords.col;\n
            instance.selection.setRangeStart(coords);\n
          }\n
        }\n
        Handsontable.hooks.run(instance, \'afterOnCellMouseDown\', event, coords, TD);\n
        that.activeWt = that.wt;\n
      }\n
    },\n
    onCellMouseOver: function(event, coords, TD, wt) {\n
      that.activeWt = wt;\n
      if (coords.row >= 0 && coords.col >= 0) {\n
        if (isMouseDown) {\n
          instance.selection.setRangeEnd(coords);\n
        }\n
      } else {\n
        if (isMouseDown) {\n
          if (coords.row < 0) {\n
            instance.selection.setRangeEnd(new WalkontableCellCoords(instance.countRows() - 1, coords.col));\n
            instance.selection.setSelectedHeaders(false, true);\n
          }\n
          if (coords.col < 0) {\n
            instance.selection.setRangeEnd(new WalkontableCellCoords(coords.row, instance.countCols() - 1));\n
            instance.selection.setSelectedHeaders(true, false);\n
          }\n
        }\n
      }\n
      Handsontable.hooks.run(instance, \'afterOnCellMouseOver\', event, coords, TD);\n
      that.activeWt = that.wt;\n
    },\n
    onCellCornerMouseDown: function(event) {\n
      event.preventDefault();\n
      Handsontable.hooks.run(instance, \'afterOnCellCornerMouseDown\', event);\n
    },\n
    beforeDraw: function(force) {\n
      that.beforeRender(force);\n
    },\n
    onDraw: function(force) {\n
      that.onDraw(force);\n
    },\n
    onScrollVertically: function() {\n
      instance.runHooks(\'afterScrollVertically\');\n
    },\n
    onScrollHorizontally: function() {\n
      instance.runHooks(\'afterScrollHorizontally\');\n
    },\n
    onBeforeDrawBorders: function(corners, borderClassName) {\n
      instance.runHooks(\'beforeDrawBorders\', corners, borderClassName);\n
    },\n
    onBeforeTouchScroll: function() {\n
      instance.runHooks(\'beforeTouchScroll\');\n
    },\n
    onAfterMomentumScroll: function() {\n
      instance.runHooks(\'afterMomentumScroll\');\n
    },\n
    viewportRowCalculatorOverride: function(calc) {\n
      if (that.settings.viewportRowRenderingOffset) {\n
        calc.startRow = Math.max(calc.startRow - that.settings.viewportRowRenderingOffset, 0);\n
        calc.endRow = Math.min(calc.endRow + that.settings.viewportRowRenderingOffset, instance.countRows() - 1);\n
      }\n
      instance.runHooks(\'afterViewportRowCalculatorOverride\', calc);\n
    },\n
    viewportColumnCalculatorOverride: function(calc) {\n
      if (that.settings.viewportColumnRenderingOffset) {\n
        calc.startColumn = Math.max(calc.startColumn - that.settings.viewportColumnRenderingOffset, 0);\n
        calc.endColumn = Math.min(calc.endColumn + that.settings.viewportColumnRenderingOffset, instance.countCols() - 1);\n
      }\n
      instance.runHooks(\'afterViewportColumnCalculatorOverride\', calc);\n
    }\n
  };\n
  Handsontable.hooks.run(instance, \'beforeInitWalkontable\', walkontableConfig);\n
  this.wt = new Walkontable(walkontableConfig);\n
  this.activeWt = this.wt;\n
  this.eventManager.addEventListener(that.wt.wtTable.spreader, \'mousedown\', function(event) {\n
    if (event.target === that.wt.wtTable.spreader && event.which === 3) {\n
      helper.stopPropagation(event);\n
    }\n
  });\n
  this.eventManager.addEventListener(that.wt.wtTable.spreader, \'contextmenu\', function(event) {\n
    if (event.target === that.wt.wtTable.spreader && event.which === 3) {\n
      helper.stopPropagation(event);\n
    }\n
  });\n
  this.eventManager.addEventListener(document.documentElement, \'click\', function() {\n
    if (that.settings.observeDOMVisibility) {\n
      if (that.wt.drawInterrupted) {\n
        that.instance.forceFullRender = true;\n
        that.render();\n
      }\n
    }\n
  });\n
}\n
TableView.prototype.isTextSelectionAllowed = function(el) {\n
  if (helper.isInput(el)) {\n
    return true;\n
  }\n
  if (this.settings.fragmentSelection && dom.isChildOf(el, this.TBODY)) {\n
    return true;\n
  }\n
  return false;\n
};\n
TableView.prototype.isCellEdited = function() {\n
  var activeEditor = this.instance.getActiveEditor();\n
  return activeEditor && activeEditor.isOpened();\n
};\n
TableView.prototype.beforeRender = function(force) {\n
  if (force) {\n
    Handsontable.hooks.run(this.instance, \'beforeRender\', this.instance.forceFullRender);\n
  }\n
};\n
TableView.prototype.onDraw = function(force) {\n
  if (force) {\n
    Handsontable.hooks.run(this.instance, \'afterRender\', this.instance.forceFullRender);\n
  }\n
};\n
TableView.prototype.render = function() {\n
  this.wt.draw(!this.instance.forceFullRender);\n
  this.instance.forceFullRender = false;\n
};\n
TableView.prototype.getCellAtCoords = function(coords, topmost) {\n
  var td = this.wt.getCell(coords, topmost);\n
  if (td < 0) {\n
    return null;\n
  } else {\n
    return td;\n
  }\n
};\n
TableView.prototype.scrollViewport = function(coords) {\n
  this.wt.scrollViewport(coords);\n
};\n
TableView.prototype.appendRowHeader = function(row, TH) {\n
  var DIV = document.createElement(\'DIV\'),\n
      SPAN = document.createElement(\'SPAN\');\n
  DIV.className = \'relative\';\n
  SPAN.className = \'rowHeader\';\n
  if (row > -1) {\n
    dom.fastInnerHTML(SPAN, this.instance.getRowHeader(row));\n
  } else {\n
    dom.fastInnerText(SPAN, String.fromCharCode(160));\n
  }\n
  DIV.appendChild(SPAN);\n
  dom.empty(TH);\n
  TH.appendChild(DIV);\n
  Handsontable.hooks.run(this.instance, \'afterGetRowHeader\', row, TH);\n
};\n
TableView.prototype.appendColHeader = function(col, TH) {\n
  var DIV = document.createElement(\'DIV\'),\n
      SPAN = document.createElement(\'SPAN\');\n
  DIV.className = \'relative\';\n
  SPAN.className = \'colHeader\';\n
  if (col > -1) {\n
    dom.fastInnerHTML(SPAN, this.instance.getColHeader(col));\n
  } else {\n
    dom.fastInnerText(SPAN, String.fromCharCode(160));\n
    dom.addClass(SPAN, \'cornerHeader\');\n
  }\n
  DIV.appendChild(SPAN);\n
  dom.empty(TH);\n
  TH.appendChild(DIV);\n
  Handsontable.hooks.run(this.instance, \'afterGetColHeader\', col, TH);\n
};\n
TableView.prototype.maximumVisibleElementWidth = function(leftOffset) {\n
  var workspaceWidth = this.wt.wtViewport.getWorkspaceWidth();\n
  var maxWidth = workspaceWidth - leftOffset;\n
  return maxWidth > 0 ? maxWidth : 0;\n
};\n
TableView.prototype.maximumVisibleElementHeight = function(topOffset) {\n
  var workspaceHeight = this.wt.wtViewport.getWorkspaceHeight();\n
  var maxHeight = workspaceHeight - topOffset;\n
  return maxHeight > 0 ? maxHeight : 0;\n
};\n
TableView.prototype.mainViewIsActive = function() {\n
  return this.wt === this.activeWt;\n
};\n
TableView.prototype.destroy = function() {\n
  this.wt.destroy();\n
  this.eventManager.clear();\n
};\n
;\n
\n
\n
//# \n
},{"./3rdparty/walkontable/src/cell/coords.js":9,"./3rdparty/walkontable/src/core.js":11,"./3rdparty/walkontable/src/selection.js":22,"./dom.js":31,"./eventManager.js":45,"./helpers.js":46}],89:[function(require,module,exports){\n
"use strict";\n
var process = function(value, callback) {\n
  var originalVal = value;\n
  var lowercaseVal = typeof originalVal === \'string\' ? originalVal.toLowerCase() : null;\n
  return function(source) {\n
    var found = false;\n
    for (var s = 0,\n
        slen = source.length; s < slen; s++) {\n
      if (originalVal === source[s]) {\n
        found = true;\n
        break;\n
      } else if (lowercaseVal === source[s].toLowerCase()) {\n
        found = true;\n
        break;\n
      }\n
    }\n
    callback(found);\n
  };\n
};\n
Handsontable.AutocompleteValidator = function(value, callback) {\n
  if (this.strict && this.source) {\n
    if (typeof this.source === \'function\') {\n
      this.source(value, process(value, callback));\n
    } else {\n
      process(value, callback)(this.source);\n
    }\n
  } else {\n
    callback(true);\n
  }\n
};\n
\n
\n
//# \n
},{}],90:[function(require,module,exports){\n
"use strict";\n
var $__moment__;\n
var moment = ($__moment__ = require("moment"), $__moment__ && $__moment__.__esModule && $__moment__ || {default: $__moment__}).default;\n
Handsontable.DateValidator = function(value, callback) {\n
  var correctedValue = null,\n
      valid = true,\n
      dateEditor = Handsontable.editors.getEditor(\'date\', this.instance);\n
  if (value === null) {\n
    value = \'\';\n
  }\n
  var isValidDate = moment(new Date(value)).isValid(),\n
      isValidFormat = moment(value, this.dateFormat || dateEditor.defaultDateFormat, true).isValid();\n
  if (!isValidDate) {\n
    valid = false;\n
  }\n
  if (!isValidDate && isValidFormat) {\n
    valid = true;\n
  }\n
  if (isValidDate && !isValidFormat) {\n
    if (this.correctFormat === true) {\n
      correctedValue = correctFormat(value, this.dateFormat);\n
      this.instance.setDataAtCell(this.row, this.col, correctedValue, \'dateValidator\');\n
      valid = true;\n
    } else {\n
      valid = false;\n
    }\n
  }\n
  callback(valid);\n
};\n
var correctFormat = function(value, dateFormat) {\n
  value = moment(new Date(value)).format(dateFormat);\n
  return value;\n
};\n
\n
\n
//# \n
},{"moment":"moment"}],91:[function(require,module,exports){\n
"use strict";\n
Handsontable.NumericValidator = function(value, callback) {\n
  if (value === null) {\n
    value = \'\';\n
  }\n
  callback(/^-?\\d*(\\.|\\,)?\\d*$/.test(value));\n
};\n
\n
\n
//# \n
},{}],"moment":[function(require,module,exports){\n
//! moment.js\n
//! version : 2.10.2\n
//! authors : Tim Wood, Iskren Chernev, Moment.js contributors\n
//! license : MIT\n
//! momentjs.com\n
\n
(function (global, factory) {\n
    typeof exports === \'object\' && typeof module !== \'undefined\' ? module.exports = factory() :\n
    typeof define === \'function\' && define.amd ? define(factory) :\n
    global.moment = factory()\n
}(this, function () { \'use strict\';\n
\n
    var hookCallback;\n
\n
    function utils_hooks__hooks () {\n
        return hookCallback.apply(null, arguments);\n
    }\n
\n
    // This is done to register the method called with moment()\n
    // without creating circular dependencies.\n
    function setHookCallback (callback) {\n
        hookCallback = callback;\n
    }\n
\n
    function defaultParsingFlags() {\n
        // We need to deep clone this object.\n
        return {\n
            empty           : false,\n
            unusedTokens    : [],\n
            unusedInput     : [],\n
            overflow        : -2,\n
            charsLeftOver   : 0,\n
            nullInput       : false,\n
            invalidMonth    : null,\n
            invalidFormat   : false,\n
            userInvalidated : false,\n
            iso             : false\n
        };\n
    }\n
\n
    function isArray(input) {\n
        return Object.prototype.toString.call(input) === \'[object Array]\';\n
    }\n
\n
    function isDate(input) {\n
        return Object.prototype.toString.call(input) === \'[object Date]\' || input instanceof Date;\n
    }\n
\n
    function map(arr, fn) {\n
        var res = [], i;\n
        for (i = 0; i < arr.length; ++i) {\n
            res.push(fn(arr[i], i));\n
        }\n
        return res;\n
    }\n
\n
    function hasOwnProp(a, b) {\n
        return Object.prototype.hasOwnProperty.call(a, b);\n
    }\n
\n
    function extend(a, b) {\n
        for (var i in b) {\n
            if (hasOwnProp(b, i)) {\n
                a[i] = b[i];\n
            }\n
        }\n
\n
        if (hasOwnProp(b, \'toString\')) {\n
            a.toString = b.toString;\n
        }\n
\n
        if (hasOwnProp(b, \'valueOf\')) {\n
            a.valueOf = b.valueOf;\n
        }\n
\n
        return a;\n
    }\n
\n
    function create_utc__createUTC (input, format, locale, strict) {\n
        return createLocalOrUTC(input, format, locale, strict, true).utc();\n
    }\n
\n
    function valid__isValid(m) {\n
        if (m._isValid == null) {\n
            m._isValid = !isNaN(m._d.getTime()) &&\n
                m._pf.overflow < 0 &&\n
                !m._pf.empty &&\n
                !m._pf.invalidMonth &&\n
                !m._pf.nullInput &&\n
                !m._pf.invalidFormat &&\n
                !m._pf.userInvalidated;\n
\n
            if (m._strict) {\n
                m._isValid = m._isValid &&\n
                    m._pf.charsLeftOver === 0 &&\n
                    m._pf.unusedTokens.length === 0 &&\n
                    m._pf.bigHour === undefined;\n
            }\n
        }\n
        return m._isValid;\n
    }\n
\n
    function valid__createInvalid (flags) {\n
        var m = create_utc__createUTC(NaN);\n
        if (flags != null) {\n
            extend(m._pf, flags);\n
        }\n
        else {\n
            m._pf.userInvalidated = true;\n
        }\n
\n
        return m;\n
    }\n
\n
    var momentProperties = utils_hooks__hooks.momentProperties = [];\n
\n
    function copyConfig(to, from) {\n
        var i, prop, val;\n
\n
        if (typeof from._isAMomentObject !== \'undefined\') {\n
            to._isAMomentObject = from._isAMomentObject;\n
        }\n
        if (typeof from._i !== \'undefined\') {\n
            to._i = from._i;\n
        }\n
        if (typeof from._f !== \'undefined\') {\n
            to._f = from._f;\n
        }\n
        if (typeof from._l !== \'undefined\') {\n
            to._l = from._l;\n
        }\n
        if (typeof from._strict !== \'undefined\') {\n
            to._strict = from._strict;\n
        }\n
        if (typeof from._tzm !== \'undefined\') {\n
            to._tzm = from._tzm;\n
        }\n
        if (typeof from._isUTC !== \'undefined\') {\n
            to._isUTC = from._isUTC;\n
        }\n
        if (typeof from._offset !== \'undefined\') {\n
            to._offset = from._offset;\n
        }\n
        if (typeof from._pf !== \'undefined\') {\n
            to._pf = from._pf;\n
        }\n
        if (typeof from._locale !== \'undefined\') {\n
            to._locale = from._locale;\n
        }\n
\n
        if (momentProperties.length > 0) {\n
            for (i in momentProperties) {\n
                prop = momentProperties[i];\n
                val = from[prop];\n
                if (typeof val !== \'undefined\') {\n
                    to[prop] = val;\n
                }\n
            }\n
        }\n
\n
        return to;\n
    }\n
\n
    var updateInProgress = false;\n
\n
    // Moment prototype object\n
    function Moment(config) {\n
        copyConfig(this, config);\n
        this._d = new Date(+config._d);\n
        // Prevent infinite loop in case updateOffset creates new moment\n
        // objects.\n
        if (updateInProgress === false) {\n
            updateInProgress = true;\n
            utils_hooks__hooks.updateOffset(this);\n
            updateInProgress = false;\n
        }\n
    }\n
\n
    function isMoment (obj) {\n
        return obj instanceof Moment || (obj != null && hasOwnProp(obj, \'_isAMomentObject\'));\n
    }\n
\n
    function toInt(argumentForCoercion) {\n
        var coercedNumber = +argumentForCoercion,\n
            value = 0;\n
\n
        if (coercedNumber !== 0 && isFinite(coercedNumber)) {\n
            if (coercedNumber >= 0) {\n
                value = Math.floor(coercedNumber);\n
            } else {\n
                value = Math.ceil(coercedNumber);\n
            }\n
        }\n
\n
        return value;\n
    }\n
\n
    function compareArrays(array1, array2, dontConvert) {\n
        var len = Math.min(array1.length, array2.length),\n
            lengthDiff = Math.abs(array1.length - array2.length),\n
            diffs = 0,\n
            i;\n
        for (i = 0; i < len; i++) {\n
            if ((dontConvert && array1[i] !== array2[i]) ||\n
                (!dontConvert && toInt(array1[i]) !== toInt(array2[i]))) {\n
                diffs++;\n
            }\n
        }\n
        return diffs + lengthDiff;\n
    }\n
\n
    function Locale() {\n
    }\n
\n
    var locales = {};\n
    var globalLocale;\n
\n
    function normalizeLocale(key) {\n
        return key ? key.toLowerCase().replace(\'_\', \'-\') : key;\n
    }\n
\n
    // pick the locale from the array\n
    // try [\'en-au\', \'en-gb\'] as \'en-au\', \'en-gb\', \'en\', as in move through the list trying each\n
    // substring from most specific to least, but move to the next array item if it\'s a more specific variant than the current root\n
    function chooseLocale(names) {\n
        var i = 0, j, next, locale, split;\n
\n
        while (i < names.length) {\n
            split = normalizeLocale(names[i]).split(\'-\');\n
            j = split.length;\n
            next = normalizeLocale(names[i + 1]);\n
            next = next ? next.split(\'-\') : null;\n
            while (j > 0) {\n
                locale = loadLocale(split.slice(0, j).join(\'-\'));\n
                if (locale) {\n
                    return locale;\n
                }\n
                if (next && next.length >= j && compareArrays(split, next, true) >= j - 1) {\n
                    //the next array item is better than a shallower substring of this one\n
                    break;\n
                }\n
                j--;\n
            }\n
            i++;\n
        }\n
        return null;\n
    }\n
\n
    function loadLocale(name) {\n
        var oldLocale = null;\n
        // TODO: Find a better way to register and load all the locales in Node\n
        if (!locales[name] && typeof module !== \'undefined\' &&\n
                module && module.exports) {\n
            try {\n
                oldLocale = globalLocale._abbr;\n
                require(\'./locale/\' + name);\n
                // because defineLocale currently also sets the global locale, we\n
                // want to undo that for lazy loaded locales\n
                locale_locales__getSetGlobalLocale(oldLocale);\n
            } catch (e) { }\n
        }\n
        return locales[name];\n
    }\n
\n
    // This function will load locale and then set the global locale.  If\n
    // no arguments are passed in, it will simply return the current global\n
    // locale key.\n
    function locale_locales__getSetGlobalLocale (key, values) {\n
        var data;\n
        if (key) {\n
            if (typeof values === \'undefined\') {\n
                data = locale_locales__getLocale(key);\n
            }\n
            else {\n
                data = defineLocale(key, values);\n
            }\n
\n
            if (data) {\n
                // moment.duration._locale = moment._locale = data;\n
                globalLocale = data;\n
            }\n
        }\n
\n
        return globalLocale._abbr;\n
    }\n
\n
    function defineLocale (name, values) {\n
        if (values !== null) {\n
            values.abbr = name;\n
            if (!locales[name]) {\n
                locales[name] = new Locale();\n
            }\n
            locales[name].set(values);\n
\n
            // backwards compat for now: also set the locale\n
            locale_locales__getSetGlobalLocale(name);\n
\n
            return locales[name];\n
        } else {\n
            // useful for testing\n
            delete locales[name];\n
            return null;\n
        }\n
    }\n
\n
    // returns locale data\n
    function locale_locales__getLocale (key) {\n
        var locale;\n
\n
        if (key && key._locale && key._locale._abbr) {\n
            key = key._locale._abbr;\n
        }\n
\n
        if (!key) {\n
            return globalLocale;\n
        }\n
\n
        if (!isArray(key)) {\n
            //short-circuit everything else\n
            locale = loadLocale(key);\n
            if (locale) {\n
                return locale;\n
            }\n
            key = [key];\n
        }\n
\n
        return chooseLocale(key);\n
    }\n
\n
    var aliases = {};\n
\n
    function addUnitAlias (unit, shorthand) {\n
        var lowerCase = unit.toLowerCase();\n
        aliases[lowerCase] = aliases[lowerCase + \'s\'] = aliases[shorthand] = unit;\n
    }\n
\n
    function normalizeUnits(units) {\n
        return typeof units === \'string\' ? aliases[units] || aliases[units.toLowerCase()] : undefined;\n
    }\n
\n
    function normalizeObjectUnits(inputObject) {\n
        var normalizedInput = {},\n
            normalizedProp,\n
            prop;\n
\n
        for (prop in inputObject) {\n
            if (hasOwnProp(inputObject, prop)) {\n
                normalizedProp = normalizeUnits(prop);\n
                if (normalizedProp) {\n
                    normalizedInput[normalizedProp] = inputObject[prop];\n
                }\n
            }\n
        }\n
\n
        return normalizedInput;\n
    }\n
\n
    function makeGetSet (unit, keepTime) {\n
        return function (value) {\n
            if (value != null) {\n
                get_set__set(this, unit, value);\n
                utils_hooks__hooks.updateOffset(this, keepTime);\n
                return this;\n
            } else {\n
                return get_set__get(this, unit);\n
            }\n
        };\n
    }\n
\n
    function get_set__get (mom, unit) {\n
        return mom._d[\'get\' + (mom._isUTC ? \'UTC\' : \'\') + unit]();\n
    }\n
\n
    function get_set__set (mom, unit, value) {\n
        return mom._d[\'set\' + (mom._isUTC ? \'UTC\' : \'\') + unit](value);\n
    }\n
\n
    // MOMENTS\n
\n
    function getSet (units, value) {\n
        var unit;\n
        if (typeof units === \'object\') {\n
            for (unit in units) {\n
                this.set(unit, units[unit]);\n
            }\n
        } else {\n
            units = normalizeUnits(units);\n
            if (typeof this[units] === \'function\') {\n
                return this[units](value);\n
            }\n
        }\n
        return this;\n
    }\n
\n
    function zeroFill(number, targetLength, forceSign) {\n
        var output = \'\' + Math.abs(number),\n
            sign = number >= 0;\n
\n
        while (output.length < targetLength) {\n
            output = \'0\' + output;\n
        }\n
        return (sign ? (forceSign ? \'+\' : \'\') : \'-\') + output;\n
    }\n
\n
    var formattingTokens = /(\\[[^\\[]*\\])|(\\\\)?(Mo|MM?M?M?|Do|DDDo|DD?D?D?|ddd?d?|do?|w[o|w]?|W[o|W]?|Q|YYYYYY|YYYYY|YYYY|YY|gg(ggg?)?|GG(GGG?)?|e|E|a|A|hh?|HH?|mm?|ss?|S{1,4}|x|X|zz?|ZZ?|.)/g;\n
\n
    var localFormattingTokens = /(\\[[^\\[]*\\])|(\\\\)?(LTS|LT|LL?L?L?|l{1,4})/g;\n
\n
    var formatFunctions = {};\n
\n
    var formatTokenFunctions = {};\n
\n
    // token:    \'M\'\n
    // padded:   [\'MM\', 2]\n
    // ordinal:  \'Mo\'\n
    // callback: function () { this.month() + 1 }\n
    function addFormatToken (token, padded, ordinal, callback) {\n
        var func = callback;\n
        if (typeof callback === \'string\') {\n
            func = function () {\n
                return this[callback]();\n
            };\n
        }\n
        if (token) {\n
            formatTokenFunctions[token] = func;\n
        }\n
        if (padded) {\n
            formatTokenFunctions[padded[0]] = function () {\n
                return zeroFill(func.apply(this, arguments), padded[1], padded[2]);\n
            };\n
        }\n
        if (ordinal) {\n
            formatTokenFunctions[ordinal] = function () {\n
                return this.localeData().ordinal(func.apply(this, arguments), token);\n
            };\n
        }\n
    }\n
\n
    function removeFormattingTokens(input) {\n
        if (input.match(/\\[[\\s\\S]/)) {\n
            return input.replace(/^\\[|\\]$/g, \'\');\n
        }\n
        return input.replace(/\\\\/g, \'\');\n
    }\n
\n
    function makeFormatFunction(format) {\n
        var array = format.match(formattingTokens), i, length;\n
\n
        for (i = 0, length = array.length; i < length; i++) {\n
            if (formatTokenFunctions[array[i]]) {\n
                array[i] = formatTokenFunctions[array[i]];\n
            } else {\n
                array[i] = removeFormattingTokens(array[i]);\n
            }\n
        }\n
\n
        return function (mom) {\n
            var output = \'\';\n
            for (i = 0; i < length; i++) {\n
                output += array[i] instanceof Function ? array[i].call(mom, format) : array[i];\n
            }\n
            return output;\n
        };\n
    }\n
\n
    // format date using native date object\n
    function formatMoment(m, format) {\n
        if (!m.isValid()) {\n
            return m.localeData().invalidDate();\n
        }\n
\n
        format = expandFormat(format, m.localeData());\n
\n
        if (!formatFunctions[format]) {\n
            formatFunctions[format] = makeFormatFunction(format);\n
        }\n
\n
        return formatFunctions[format](m);\n
    }\n
\n
    function expandFormat(format, locale) {\n
        var i = 5;\n
\n
        function replaceLongDateFormatTokens(input) {\n
            return locale.longDateFormat(input) || input;\n
        }\n
\n
        localFormattingTokens.lastIndex = 0;\n
        while (i >= 0 && localFormattingTokens.test(format)) {\n
            format = format.replace(localFormattingTokens, replaceLongDateFormatTokens);\n
            localFormattingTokens.lastIndex = 0;\n
            i -= 1;\n
        }\n
\n
        return format;\n
    }\n
\n
    var match1         = /\\d/;            //       0 - 9\n
    var match2         = /\\d\\d/;          //      00 - 99\n
    var match3         = /\\d{3}/;         //     000 - 999\n
    var match4         = /\\d{4}/;         //    0000 - 9999\n
    var match6         = /[+-]?\\d{6}/;    // -999999 - 999999\n
    var match1to2      = /\\d\\d?/;         //       0 - 99\n
    var match1to3      = /\\d{1,3}/;       //       0 - 999\n
    var match1to4      = /\\d{1,4}/;       //       0 - 9999\n
    var match1to6      = /[+-]?\\d{1,6}/;  // -999999 - 999999\n
\n
    var matchUnsigned  = /\\d+/;           //       0 - inf\n
    var matchSigned    = /[+-]?\\d+/;      //    -inf - inf\n
\n
    var matchOffset    = /Z|[+-]\\d\\d:?\\d\\d/gi; // +00:00 -00:00 +0000 -0000 or Z\n
\n
    var matchTimestamp = /[+-]?\\d+(\\.\\d{1,3})?/; // 123456789 123456789.123\n
\n
    // any word (or two) characters or numbers including two/three word month in arabic.\n
    var matchWord = /[0-9]*[\'a-z\\u00A0-\\u05FF\\u0700-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF]+|[\\u0600-\\u06FF\\/]+(\\s*?[\\u0600-\\u06FF]+){1,2}/i;\n
\n
    var regexes = {};\n
\n
    function addRegexToken (token, regex, strictRegex) {\n
        regexes[token] = typeof regex === \'function\' ? regex : function (isStrict) {\n
            return (isStrict && strictRegex) ? strictRegex : regex;\n
        };\n
    }\n
\n
    function getParseRegexForToken (token, config) {\n
        if (!hasOwnProp(regexes, token)) {\n
            return new RegExp(unescapeFormat(token));\n
        }\n
\n
        return regexes[token](config._strict, config._locale);\n
    }\n
\n
    // Code from http://stackoverflow.com/questions/3561493/is-there-a-regexp-escape-function-in-javascript\n
    function unescapeFormat(s) {\n
        return s.replace(\'\\\\\', \'\').replace(/\\\\(\\[)|\\\\(\\])|\\[([^\\]\\[]*)\\]|\\\\(.)/g, function (matched, p1, p2, p3, p4) {\n
            return p1 || p2 || p3 || p4;\n
        }).replace(/[-\\/\\\\^$*+?.()|[\\]{}]/g, \'\\\\$&\');\n
    }\n
\n
    var tokens = {};\n
\n
    function addParseToken (token, callback) {\n
        var i, func = callback;\n
        if (typeof token === \'string\') {\n
            token = [token];\n
        }\n
        if (typeof callback === \'number\') {\n
            func = function (input, array) {\n
                array[callback] = toInt(input);\n
            };\n
        }\n
        for (i = 0; i < token.length; i++) {\n
            tokens[token[i]] = func;\n
        }\n
    }\n
\n
    function addWeekParseToken (token, callback) {\n
        addParseToken(token, function (input, array, config, token) {\n
            config._w = config._w || {};\n
            callback(input, config._w, config, token);\n
        });\n
    }\n
\n
    function addTimeToArrayFromToken(token, input, config) {\n
        if (input != null && hasOwnProp(tokens, token)) {\n
            tokens[token](input, config._a, config, token);\n
        }\n
    }\n
\n
    var YEAR = 0;\n
    var MONTH = 1;\n
    var DATE = 2;\n
    var HOUR = 3;\n
    var MINUTE = 4;\n
    var SECOND = 5;\n
    var MILLISECOND = 6;\n
\n
    function daysInMonth(year, month) {\n
        return new Date(Date.UTC(year, month + 1, 0)).getUTCDate();\n
    }\n
\n
    // FORMATTING\n
\n
    addFormatToken(\'M\', [\'MM\', 2], \'Mo\', function () {\n
        return this.month() + 1;\n
    });\n
\n
    addFormatToken(\'MMM\', 0, 0, function (format) {\n
        return this.localeData().monthsShort(this, format);\n
    });\n
\n
    addFormatToken(\'MMMM\', 0, 0, function (format) {\n
        return this.localeData().months(this, format);\n
    });\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'month\', \'M\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'M\',    match1to2);\n
    addRegexToken(\'MM\',   match1to2, match2);\n
    addRegexToken(\'MMM\',  matchWord);\n
    addRegexToken(\'MMMM\', matchWord);\n
\n
    addParseToken([\'M\', \'MM\'], function (input, array) {\n
        array[MONTH] = toInt(input) - 1;\n
    });\n
\n
    addParseToken([\'MMM\', \'MMMM\'], function (input, array, config, token) {\n
        var month = config._locale.monthsParse(input, token, config._strict);\n
        // if we didn\'t find a month name, mark the date as invalid.\n
        if (month != null) {\n
            array[MONTH] = month;\n
        } else {\n
            config._pf.invalidMonth = input;\n
        }\n
    });\n
\n
    // LOCALES\n
\n
    var defaultLocaleMonths = \'January_February_March_April_May_June_July_August_September_October_November_December\'.split(\'_\');\n
    function localeMonths (m) {\n
        return this._months[m.month()];\n
    }\n
\n
    var defaultLocaleMonthsShort = \'Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec\'.split(\'_\');\n
    function localeMonthsShort (m) {\n
        return this._monthsShort[m.month()];\n
    }\n
\n
    function localeMonthsParse (monthName, format, strict) {\n
        var i, mom, regex;\n
\n
        if (!this._monthsParse) {\n
            this._monthsParse = [];\n
            this._longMonthsParse = [];\n
            this._shortMonthsParse = [];\n
        }\n
\n
        for (i = 0; i < 12; i++) {\n
            // make the regex if we don\'t have it already\n
            mom = create_utc__createUTC([2000, i]);\n
            if (strict && !this._longMonthsParse[i]) {\n
                this._longMonthsParse[i] = new RegExp(\'^\' + this.months(mom, \'\').replace(\'.\', \'\') + \'$\', \'i\');\n
                this._shortMonthsParse[i] = new RegExp(\'^\' + this.monthsShort(mom, \'\').replace(\'.\', \'\') + \'$\', \'i\');\n
            }\n
            if (!strict && !this._monthsParse[i]) {\n
                regex = \'^\' + this.months(mom, \'\') + \'|^\' + this.monthsShort(mom, \'\');\n
                this._monthsParse[i] = new RegExp(regex.replace(\'.\', \'\'), \'i\');\n
            }\n
            // test the regex\n
            if (strict && format === \'MMMM\' && this._longMonthsParse[i].test(monthName)) {\n
                return i;\n
            } else if (strict && format === \'MMM\' && this._shortMonthsParse[i].test(monthName)) {\n
                return i;\n
            } else if (!strict && this._monthsParse[i].test(monthName)) {\n
                return i;\n
            }\n
        }\n
    }\n
\n
    // MOMENTS\n
\n
    function setMonth (mom, value) {\n
        var dayOfMonth;\n
\n
        // TODO: Move this out of here!\n
        if (typeof value === \'string\') {\n
            value = mom.localeData().monthsParse(value);\n
            // TODO: Another silent failure?\n
            if (typeof value !== \'number\') {\n
                return mom;\n
            }\n
        }\n
\n
        dayOfMonth = Math.min(mom.date(), daysInMonth(mom.year(), value));\n
        mom._d[\'set\' + (mom._isUTC ? \'UTC\' : \'\') + \'Month\'](value, dayOfMonth);\n
        return mom;\n
    }\n
\n
    function getSetMonth (value) {\n
        if (value != null) {\n
            setMonth(this, value);\n
            utils_hooks__hooks.updateOffset(this, true);\n
            return this;\n
        } else {\n
            return get_set__get(this, \'Month\');\n
        }\n
    }\n
\n
    function getDaysInMonth () {\n
        return daysInMonth(this.year(), this.month());\n
    }\n
\n
    function checkOverflow (m) {\n
        var overflow;\n
        var a = m._a;\n
\n
        if (a && m._pf.overflow === -2) {\n
            overflow =\n
                a[MONTH]       < 0 || a[MONTH]       > 11  ? MONTH :\n
                a[DATE]        < 1 || a[DATE]        > daysInMonth(a[YEAR], a[MONTH]) ? DATE :\n
                a[HOUR]        < 0 || a[HOUR]        > 24 || (a[HOUR] === 24 && (a[MINUTE] !== 0 || a[SECOND] !== 0 || a[MILLISECOND] !== 0)) ? HOUR :\n
                a[MINUTE]      < 0 || a[MINUTE]      > 59  ? MINUTE :\n
                a[SECOND]      < 0 || a[SECOND]      > 59  ? SECOND :\n
                a[MILLISECOND] < 0 || a[MILLISECOND] > 999 ? MILLISECOND :\n
                -1;\n
\n
            if (m._pf._overflowDayOfYear && (overflow < YEAR || overflow > DATE)) {\n
                overflow = DATE;\n
            }\n
\n
            m._pf.overflow = overflow;\n
        }\n
\n
        return m;\n
    }\n
\n
    function warn(msg) {\n
        if (utils_hooks__hooks.suppressDeprecationWarnings === false && typeof console !== \'undefined\' && console.warn) {\n
            console.warn(\'Deprecation warning: \' + msg);\n
        }\n
    }\n
\n
    function deprecate(msg, fn) {\n
        var firstTime = true;\n
        return extend(function () {\n
            if (firstTime) {\n
                warn(msg);\n
                firstTime = false;\n
            }\n
            return fn.apply(this, arguments);\n
        }, fn);\n
    }\n
\n
    var deprecations = {};\n
\n
    function deprecateSimple(name, msg) {\n
        if (!deprecations[name]) {\n
            warn(msg);\n
            deprecations[name] = true;\n
        }\n
    }\n
\n
    utils_hooks__hooks.suppressDeprecationWarnings = false;\n
\n
    var from_string__isoRegex = /^\\s*(?:[+-]\\d{6}|\\d{4})-(?:(\\d\\d-\\d\\d)|(W\\d\\d$)|(W\\d\\d-\\d)|(\\d\\d\\d))((T| )(\\d\\d(:\\d\\d(:\\d\\d(\\.\\d+)?)?)?)?([\\+\\-]\\d\\d(?::?\\d\\d)?|\\s*Z)?)?$/;\n
\n
    var isoDates = [\n
        [\'YYYYYY-MM-DD\', /[+-]\\d{6}-\\d{2}-\\d{2}/],\n
        [\'YYYY-MM-DD\', /\\d{4}-\\d{2}-\\d{2}/],\n
        [\'GGGG-[W]WW-E\', /\\d{4}-W\\d{2}-\\d/],\n
        [\'GGGG-[W]WW\', /\\d{4}-W\\d{2}/],\n
        [\'YYYY-DDD\', /\\d{4}-\\d{3}/]\n
    ];\n
\n
    // iso time formats and regexes\n
    var isoTimes = [\n
        [\'HH:mm:ss.SSSS\', /(T| )\\d\\d:\\d\\d:\\d\\d\\.\\d+/],\n
        [\'HH:mm:ss\', /(T| )\\d\\d:\\d\\d:\\d\\d/],\n
        [\'HH:mm\', /(T| )\\d\\d:\\d\\d/],\n
        [\'HH\', /(T| )\\d\\d/]\n
    ];\n
\n
    var aspNetJsonRegex = /^\\/?Date\\((\\-?\\d+)/i;\n
\n
    // date from iso format\n
    function configFromISO(config) {\n
        var i, l,\n
            string = config._i,\n
            match = from_string__isoRegex.exec(string);\n
\n
        if (match) {\n
            config._pf.iso = true;\n
            for (i = 0, l = isoDates.length; i < l; i++) {\n
                if (isoDates[i][1].exec(string)) {\n
                    // match[5] should be \'T\' or undefined\n
                    config._f = isoDates[i][0] + (match[6] || \' \');\n
                    break;\n
                }\n
            }\n
            for (i = 0, l = isoTimes.length; i < l; i++) {\n
                if (isoTimes[i][1].exec(string)) {\n
                    config._f += isoTimes[i][0];\n
                    break;\n
                }\n
            }\n
            if (string.match(matchOffset)) {\n
                config._f += \'Z\';\n
            }\n
            configFromStringAndFormat(config);\n
        } else {\n
            config._isValid = false;\n
        }\n
    }\n
\n
    // date from iso format or fallback\n
    function configFromString(config) {\n
        var matched = aspNetJsonRegex.exec(config._i);\n
\n
        if (matched !== null) {\n
            config._d = new Date(+matched[1]);\n
            return;\n
        }\n
\n
        configFromISO(config);\n
        if (config._isValid === false) {\n
            delete config._isValid;\n
            utils_hooks__hooks.createFromInputFallback(config);\n
        }\n
    }\n
\n
    utils_hooks__hooks.createFromInputFallback = deprecate(\n
        \'moment construction falls back to js Date. This is \' +\n
        \'discouraged and will be removed in upcoming major \' +\n
        \'release. Please refer to \' +\n
        \'https://github.com/moment/moment/issues/1407 for more info.\',\n
        function (config) {\n
            config._d = new Date(config._i + (config._useUTC ? \' UTC\' : \'\'));\n
        }\n
    );\n
\n
    function createDate (y, m, d, h, M, s, ms) {\n
        //can\'t just apply() to create a date:\n
        //http://stackoverflow.com/questions/181348/instantiating-a-javascript-object-by-calling-prototype-constructor-apply\n
        var date = new Date(y, m, d, h, M, s, ms);\n
\n
        //the date constructor doesn\'t accept years < 1970\n
        if (y < 1970) {\n
            date.setFullYear(y);\n
        }\n
        return date;\n
    }\n
\n
    function createUTCDate (y) {\n
        var date = new Date(Date.UTC.apply(null, arguments));\n
        if (y < 1970) {\n
            date.setUTCFullYear(y);\n
        }\n
        return date;\n
    }\n
\n
    addFormatToken(0, [\'YY\', 2], 0, function () {\n
        return this.year() % 100;\n
    });\n
\n
    addFormatToken(0, [\'YYYY\',   4],       0, \'year\');\n
    addFormatToken(0, [\'YYYYY\',  5],       0, \'year\');\n
    addFormatToken(0, [\'YYYYYY\', 6, true], 0, \'year\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'year\', \'y\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'Y\',      matchSigned);\n
    addRegexToken(\'YY\',     match1to2, match2);\n
    addRegexToken(\'YYYY\',   match1to4, match4);\n
    addRegexToken(\'YYYYY\',  match1to6, match6);\n
    addRegexToken(\'YYYYYY\', match1to6, match6);\n
\n
    addParseToken([\'YYYY\', \'YYYYY\', \'YYYYYY\'], YEAR);\n
    addParseToken(\'YY\', function (input, array) {\n
        array[YEAR] = utils_hooks__hooks.parseTwoDigitYear(input);\n
    });\n
\n
    // HELPERS\n
\n
    function daysInYear(year) {\n
        return isLeapYear(year) ? 366 : 365;\n
    }\n
\n
    function isLeapYear(year) {\n
        return (year % 4 === 0 && year % 100 !== 0) || year % 400 === 0;\n
    }\n
\n
    // HOOKS\n
\n
    utils_hooks__hooks.parseTwoDigitYear = function (input) {\n
        return toInt(input) + (toInt(input) > 68 ? 1900 : 2000);\n
    };\n
\n
    // MOMENTS\n
\n
    var getSetYear = makeGetSet(\'FullYear\', false);\n
\n
    function getIsLeapYear () {\n
        return isLeapYear(this.year());\n
    }\n
\n
    addFormatToken(\'w\', [\'ww\', 2], \'wo\', \'week\');\n
    addFormatToken(\'W\', [\'WW\', 2], \'Wo\', \'isoWeek\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'week\', \'w\');\n
    addUnitAlias(\'isoWeek\', \'W\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'w\',  match1to2);\n
    addRegexToken(\'ww\', match1to2, match2);\n
    addRegexToken(\'W\',  match1to2);\n
    addRegexToken(\'WW\', match1to2, match2);\n
\n
    addWeekParseToken([\'w\', \'ww\', \'W\', \'WW\'], function (input, week, config, token) {\n
        week[token.substr(0, 1)] = toInt(input);\n
    });\n
\n
    // HELPERS\n
\n
    // firstDayOfWeek       0 = sun, 6 = sat\n
    //                      the day of the week that starts the week\n
    //                      (usually sunday or monday)\n
    // firstDayOfWeekOfYear 0 = sun, 6 = sat\n
    //                      the first week is the week that contains the first\n
    //                      of this day of the week\n
    //                      (eg. ISO weeks use thursday (4))\n
    function weekOfYear(mom, firstDayOfWeek, firstDayOfWeekOfYear) {\n
        var end = firstDayOfWeekOfYear - firstDayOfWeek,\n
            daysToDayOfWeek = firstDayOfWeekOfYear - mom.day(),\n
            adjustedMoment;\n
\n
\n
        if (daysToDayOfWeek > end) {\n
            daysToDayOfWeek -= 7;\n
        }\n
\n
        if (daysToDayOfWeek < end - 7) {\n
            daysToDayOfWeek += 7;\n
        }\n
\n
        adjustedMoment = local__createLocal(mom).add(daysToDayOfWeek, \'d\');\n
        return {\n
            week: Math.ceil(adjustedMoment.dayOfYear() / 7),\n
            year: adjustedMoment.year()\n
        };\n
    }\n
\n
    // LOCALES\n
\n
    function localeWeek (mom) {\n
        return weekOfYear(mom, this._week.dow, this._week.doy).week;\n
    }\n
\n
    var defaultLocaleWeek = {\n
        dow : 0, // Sunday is the first day of the week.\n
        doy : 6  // The week that contains Jan 1st is the first week of the year.\n
    };\n
\n
    function localeFirstDayOfWeek () {\n
        return this._week.dow;\n
    }\n
\n
    function localeFirstDayOfYear () {\n
        return this._week.doy;\n
    }\n
\n
    // MOMENTS\n
\n
    function getSetWeek (input) {\n
        var week = this.localeData().week(this);\n
        return input == null ? week : this.add((input - week) * 7, \'d\');\n
    }\n
\n
    function getSetISOWeek (input) {\n
        var week = weekOfYear(this, 1, 4).week;\n
        return input == null ? week : this.add((input - week) * 7, \'d\');\n
    }\n
\n
    addFormatToken(\'DDD\', [\'DDDD\', 3], \'DDDo\', \'dayOfYear\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'dayOfYear\', \'DDD\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'DDD\',  match1to3);\n
    addRegexToken(\'DDDD\', match3);\n
    addParseToken([\'DDD\', \'DDDD\'], function (input, array, config) {\n
        config._dayOfYear = toInt(input);\n
    });\n
\n
    // HELPERS\n
\n
    //http://en.wikipedia.org/wiki/ISO_week_date#Calculating_a_date_given_the_year.2C_week_number_and_weekday\n
    function dayOfYearFromWeeks(year, week, weekday, firstDayOfWeekOfYear, firstDayOfWeek) {\n
        var d = createUTCDate(year, 0, 1).getUTCDay();\n
        var daysToAdd;\n
        var dayOfYear;\n
\n
        d = d === 0 ? 7 : d;\n
        weekday = weekday != null ? weekday : firstDayOfWeek;\n
        daysToAdd = firstDayOfWeek - d + (d > firstDayOfWeekOfYear ? 7 : 0) - (d < firstDayOfWeek ? 7 : 0);\n
        dayOfYear = 7 * (week - 1) + (weekday - firstDayOfWeek) + daysToAdd + 1;\n
\n
        return {\n
            year      : dayOfYear > 0 ? year      : year - 1,\n
            dayOfYear : dayOfYear > 0 ? dayOfYear : daysInYear(year - 1) + dayOfYear\n
        };\n
    }\n
\n
    // MOMENTS\n
\n
    function getSetDayOfYear (input) {\n
        var dayOfYear = Math.round((this.clone().startOf(\'day\') - this.clone().startOf(\'year\')) / 864e5) + 1;\n
        return input == null ? dayOfYear : this.add((input - dayOfYear), \'d\');\n
    }\n
\n
    // Pick the first defined of two or three arguments.\n
    function defaults(a, b, c) {\n
        if (a != null) {\n
            return a;\n
        }\n
        if (b != null) {\n
            return b;\n
        }\n
        return c;\n
    }\n
\n
    function currentDateArray(config) {\n
        var now = new Date();\n
        if (config._useUTC) {\n
            return [now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate()];\n
        }\n
        return [now.getFullYear(), now.getMonth(), now.getDate()];\n
    }\n
\n
    // convert an array to a date.\n
    // the array should mirror the parameters below\n
    // note: all values past the year are optional and will default to the lowest possible value.\n
    // [year, month, day , hour, minute, second, millisecond]\n
    function configFromArray (config) {\n
        var i, date, input = [], currentDate, yearToUse;\n
\n
        if (config._d) {\n
            return;\n
        }\n
\n
        currentDate = currentDateArray(config);\n
\n
        //compute day of the year from weeks and weekdays\n
        if (config._w && config._a[DATE] == null && config._a[MONTH] == null) {\n
            dayOfYearFromWeekInfo(config);\n
        }\n
\n
        //if the day of the year is set, figure out what it is\n
        if (config._dayOfYear) {\n
            yearToUse = defaults(config._a[YEAR], currentDate[YEAR]);\n
\n
            if (config._dayOfYear > daysInYear(yearToUse)) {\n
                config._pf._overflowDayOfYear = true;\n
            }\n
\n
            date = createUTCDate(yearToUse, 0, config._dayOfYear);\n
            config._a[MONTH] = date.getUTCMonth();\n
            config._a[DATE] = date.getUTCDate();\n
        }\n
\n
        // Default to current date.\n
        // * if no year, month, day of month are given, default to today\n
        // * if day of month is given, default month and year\n
        // * if month is given, default only year\n
        // * if year is given, don\'t default anything\n
        for (i = 0; i < 3 && config._a[i] == null; ++i) {\n
            config._a[i] = input[i] = currentDate[i];\n
        }\n
\n
        // Zero out whatever was not defaulted, including time\n
        for (; i < 7; i++) {\n
            config._a[i] = input[i] = (config._a[i] == null) ? (i === 2 ? 1 : 0) : config._a[i];\n
        }\n
\n
        // Check for 24:00:00.000\n
        if (config._a[HOUR] === 24 &&\n
                config._a[MINUTE] === 0 &&\n
                config._a[SECOND] === 0 &&\n
                config._a[MILLISECOND] === 0) {\n
            config._nextDay = true;\n
            config._a[HOUR] = 0;\n
        }\n
\n
        config._d = (config._useUTC ? createUTCDate : createDate).apply(null, input);\n
        // Apply timezone offset from input. The actual utcOffset can be changed\n
        // with parseZone.\n
        if (config._tzm != null) {\n
            config._d.setUTCMinutes(config._d.getUTCMinutes() - config._tzm);\n
        }\n
\n
        if (config._nextDay) {\n
            config._a[HOUR] = 24;\n
        }\n
    }\n
\n
    function dayOfYearFromWeekInfo(config) {\n
        var w, weekYear, week, weekday, dow, doy, temp;\n
\n
        w = config._w;\n
        if (w.GG != null || w.W != null || w.E != null) {\n
            dow = 1;\n
            doy = 4;\n
\n
            // TODO: We need to take the current isoWeekYear, but that depends on\n
            // how we interpret now (local, utc, fixed offset). So create\n
            // a now version of current config (take local/utc/offset flags, and\n
            // create now).\n
            weekYear = defaults(w.GG, config._a[YEAR], weekOfYear(local__createLocal(), 1, 4).year);\n
            week = defaults(w.W, 1);\n
            weekday = defaults(w.E, 1);\n
        } else {\n
            dow = config._locale._week.dow;\n
            doy = config._locale._week.doy;\n
\n
            weekYear = defaults(w.gg, config._a[YEAR], weekOfYear(local__createLocal(), dow, doy).year);\n
            week = defaults(w.w, 1);\n
\n
            if (w.d != null) {\n
                // weekday -- low day numbers are considered next week\n
                weekday = w.d;\n
                if (weekday < dow) {\n
                    ++week;\n
                }\n
            } else if (w.e != null) {\n
                // local weekday -- counting starts from begining of week\n
                weekday = w.e + dow;\n
            } else {\n
                // default to begining of week\n
                weekday = dow;\n
            }\n
        }\n
        temp = dayOfYearFromWeeks(weekYear, week, weekday, doy, dow);\n
\n
        config._a[YEAR] = temp.year;\n
        config._dayOfYear = temp.dayOfYear;\n
    }\n
\n
    utils_hooks__hooks.ISO_8601 = function () {};\n
\n
    // date from string and format string\n
    function configFromStringAndFormat(config) {\n
        // TODO: Move this to another part of the creation flow to prevent circular deps\n
        if (config._f === utils_hooks__hooks.ISO_8601) {\n
            configFromISO(config);\n
            return;\n
        }\n
\n
        config._a = [];\n
        config._pf.empty = true;\n
\n
        // This array is used to make a Date, either with `new Date` or `Date.UTC`\n
        var string = \'\' + config._i,\n
            i, parsedInput, tokens, token, skipped,\n
            stringLength = string.length,\n
            totalParsedInputLength = 0;\n
\n
        tokens = expandFormat(config._f, config._locale).match(formattingTokens) || [];\n
\n
        for (i = 0; i < tokens.length; i++) {\n
            token = tokens[i];\n
            parsedInput = (string.match(getParseRegexForToken(token, config)) || [])[0];\n
            if (parsedInput) {\n
                skipped = string.substr(0, string.indexOf(parsedInput));\n
                if (skipped.length > 0) {\n
                    config._pf.unusedInput.push(skipped);\n
                }\n
                string = string.slice(string.indexOf(parsedInput) + parsedInput.length);\n
                totalParsedInputLength += parsedInput.length;\n
            }\n
            // don\'t parse if it\'s not a known token\n
            if (formatTokenFunctions[token]) {\n
                if (parsedInput) {\n
                    config._pf.empty = false;\n
                }\n
                else {\n
                    config._pf.unusedTokens.push(token);\n
                }\n
                addTimeToArrayFromToken(token, parsedInput, config);\n
            }\n
            else if (config._strict && !parsedInput) {\n
                config._pf.unusedTokens.push(token);\n
            }\n
        }\n
\n
        // add remaining unparsed input length to the string\n
        config._pf.charsLeftOver = stringLength - totalParsedInputLength;\n
        if (string.length > 0) {\n
            config._pf.unusedInput.push(string);\n
        }\n
\n
        // clear _12h flag if hour is <= 12\n
        if (config._pf.bigHour === true && config._a[HOUR] <= 12) {\n
            config._pf.bigHour = undefined;\n
        }\n
        // handle meridiem\n
        config._a[HOUR] = meridiemFixWrap(config._locale, config._a[HOUR], config._meridiem);\n
\n
        configFromArray(config);\n
        checkOverflow(config);\n
    }\n
\n
\n
    function meridiemFixWrap (locale, hour, meridiem) {\n
        var isPm;\n
\n
        if (meridiem == null) {\n
            // nothing to do\n
            return hour;\n
        }\n
        if (locale.meridiemHour != null) {\n
            return locale.meridiemHour(hour, meridiem);\n
        } else if (locale.isPM != null) {\n
            // Fallback\n
            isPm = locale.isPM(meridiem);\n
            if (isPm && hour < 12) {\n
                hour += 12;\n
            }\n
            if (!isPm && hour === 12) {\n
                hour = 0;\n
            }\n
            return hour;\n
        } else {\n
            // this is not supposed to happen\n
            return hour;\n
        }\n
    }\n
\n
    function configFromStringAndArray(config) {\n
        var tempConfig,\n
            bestMoment,\n
\n
            scoreToBeat,\n
            i,\n
            currentScore;\n
\n
        if (config._f.length === 0) {\n
            config._pf.invalidFormat = true;\n
            config._d = new Date(NaN);\n
            return;\n
        }\n
\n
        for (i = 0; i < config._f.length; i++) {\n
            currentScore = 0;\n
            tempConfig = copyConfig({}, config);\n
            if (config._useUTC != null) {\n
                tempConfig._useUTC = config._useUTC;\n
            }\n
            tempConfig._pf = defaultParsingFlags();\n
            tempConfig._f = config._f[i];\n
            configFromStringAndFormat(tempConfig);\n
\n
            if (!valid__isValid(tempConfig)) {\n
                continue;\n
            }\n
\n
            // if there is any input that was not parsed add a penalty for that format\n
            currentScore += tempConfig._pf.charsLeftOver;\n
\n
            //or tokens\n
            currentScore += tempConfig._pf.unusedTokens.length * 10;\n
\n
            tempConfig._pf.score = currentScore;\n
\n
            if (scoreToBeat == null || currentScore < scoreToBeat) {\n
                scoreToBeat = currentScore;\n
                bestMoment = tempConfig;\n
            }\n
        }\n
\n
        extend(config, bestMoment || tempConfig);\n
    }\n
\n
    function configFromObject(config) {\n
        if (config._d) {\n
            return;\n
        }\n
\n
        var i = normalizeObjectUnits(config._i);\n
        config._a = [i.year, i.month, i.day || i.date, i.hour, i.minute, i.second, i.millisecond];\n
\n
        configFromArray(config);\n
    }\n
\n
    function createFromConfig (config) {\n
        var input = config._i,\n
            format = config._f,\n
            res;\n
\n
        config._locale = config._locale || locale_locales__getLocale(config._l);\n
\n
        if (input === null || (format === undefined && input === \'\')) {\n
            return valid__createInvalid({nullInput: true});\n
        }\n
\n
        if (typeof input === \'string\') {\n
            config._i = input = config._locale.preparse(input);\n
        }\n
\n
        if (isMoment(input)) {\n
            return new Moment(checkOverflow(input));\n
        } else if (isArray(format)) {\n
            configFromStringAndArray(config);\n
        } else if (format) {\n
            configFromStringAndFormat(config);\n
        } else {\n
            configFromInput(config);\n
        }\n
\n
        res = new Moment(checkOverflow(config));\n
        if (res._nextDay) {\n
            // Adding is smart enough around DST\n
            res.add(1, \'d\');\n
            res._nextDay = undefined;\n
        }\n
\n
        return res;\n
    }\n
\n
    function configFromInput(config) {\n
        var input = config._i;\n
        if (input === undefined) {\n
            config._d = new Date();\n
        } else if (isDate(input)) {\n
            config._d = new Date(+input);\n
        } else if (typeof input === \'string\') {\n
            configFromString(config);\n
        } else if (isArray(input)) {\n
            config._a = map(input.slice(0), function (obj) {\n
                return parseInt(obj, 10);\n
            });\n
            configFromArray(config);\n
        } else if (typeof(input) === \'object\') {\n
            configFromObject(config);\n
        } else if (typeof(input) === \'number\') {\n
            // from milliseconds\n
            config._d = new Date(input);\n
        } else {\n
            utils_hooks__hooks.createFromInputFallback(config);\n
        }\n
    }\n
\n
    function createLocalOrUTC (input, format, locale, strict, isUTC) {\n
        var c = {};\n
\n
        if (typeof(locale) === \'boolean\') {\n
            strict = locale;\n
            locale = undefined;\n
        }\n
        // object construction must be done this way.\n
        // https://github.com/moment/moment/issues/1423\n
        c._isAMomentObject = true;\n
        c._useUTC = c._isUTC = isUTC;\n
        c._l = locale;\n
        c._i = input;\n
        c._f = format;\n
        c._strict = strict;\n
        c._pf = defaultParsingFlags();\n
\n
        return createFromConfig(c);\n
    }\n
\n
    function local__createLocal (input, format, locale, strict) {\n
        return createLocalOrUTC(input, format, locale, strict, false);\n
    }\n
\n
    var prototypeMin = deprecate(\n
         \'moment().min is deprecated, use moment.min instead. https://github.com/moment/moment/issues/1548\',\n
         function () {\n
             var other = local__createLocal.apply(null, arguments);\n
             return other < this ? this : other;\n
         }\n
     );\n
\n
    var prototypeMax = deprecate(\n
        \'moment().max is deprecated, use moment.max instead. https://github.com/moment/moment/issues/1548\',\n
        function () {\n
            var other = local__createLocal.apply(null, arguments);\n
            return other > this ? this : other;\n
        }\n
    );\n
\n
    // Pick a moment m from moments so that m[fn](other) is true for all\n
    // other. This relies on the function fn to be transitive.\n
    //\n
    // moments should either be an array of moment objects or an array, whose\n
    // first element is an array of moment objects.\n
    function pickBy(fn, moments) {\n
        var res, i;\n
        if (moments.length === 1 && isArray(moments[0])) {\n
            moments = moments[0];\n
        }\n
        if (!moments.length) {\n
            return local__createLocal();\n
        }\n
        res = moments[0];\n
        for (i = 1; i < moments.length; ++i) {\n
            if (moments[i][fn](res)) {\n
                res = moments[i];\n
            }\n
        }\n
        return res;\n
    }\n
\n
    // TODO: Use [].sort instead?\n
    function min () {\n
        var args = [].slice.call(arguments, 0);\n
\n
        return pickBy(\'isBefore\', args);\n
    }\n
\n
    function max () {\n
        var args = [].slice.call(arguments, 0);\n
\n
        return pickBy(\'isAfter\', args);\n
    }\n
\n
    function Duration (duration) {\n
        var normalizedInput = normalizeObjectUnits(duration),\n
            years = normalizedInput.year || 0,\n
            quarters = normalizedInput.quarter || 0,\n
            months = normalizedInput.month || 0,\n
            weeks = normalizedInput.week || 0,\n
            days = normalizedInput.day || 0,\n
            hours = normalizedInput.hour || 0,\n
            minutes = normalizedInput.minute || 0,\n
            seconds = normalizedInput.second || 0,\n
            milliseconds = normalizedInput.millisecond || 0;\n
\n
        // representation for dateAddRemove\n
        this._milliseconds = +milliseconds +\n
            seconds * 1e3 + // 1000\n
            minutes * 6e4 + // 1000 * 60\n
            hours * 36e5; // 1000 * 60 * 60\n
        // Because of dateAddRemove treats 24 hours as different from a\n
        // day when working around DST, we need to store them separately\n
        this._days = +days +\n
            weeks * 7;\n
        // It is impossible translate months into days without knowing\n
        // which months you are are talking about, so we have to store\n
        // it separately.\n
        this._months = +months +\n
            quarters * 3 +\n
            years * 12;\n
\n
        this._data = {};\n
\n
        this._locale = locale_locales__getLocale();\n
\n
        this._bubble();\n
    }\n
\n
    function isDuration (obj) {\n
        return obj instanceof Duration;\n
    }\n
\n
    function offset (token, separator) {\n
        addFormatToken(token, 0, 0, function () {\n
            var offset = this.utcOffset();\n
            var sign = \'+\';\n
            if (offset < 0) {\n
                offset = -offset;\n
                sign = \'-\';\n
            }\n
            return sign + zeroFill(~~(offset / 60), 2) + separator + zeroFill(~~(offset) % 60, 2);\n
        });\n
    }\n
\n
    offset(\'Z\', \':\');\n
    offset(\'ZZ\', \'\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'Z\',  matchOffset);\n
    addRegexToken(\'ZZ\', matchOffset);\n
    addParseToken([\'Z\', \'ZZ\'], function (input, array, config) {\n
        config._useUTC = true;\n
        config._tzm = offsetFromString(input);\n
    });\n
\n
    // HELPERS\n
\n
    // timezone chunker\n
    // \'+10:00\' > [\'10\',  \'00\']\n
    // \'-1530\'  > [\'-15\', \'30\']\n
    var chunkOffset = /([\\+\\-]|\\d\\d)/gi;\n
\n
    function offsetFromString(string) {\n
        var matches = ((string || \'\').match(matchOffset) || []);\n
        var chunk   = matches[matches.length - 1] || [];\n
        var parts   = (chunk + \'\').match(chunkOffset) || [\'-\', 0, 0];\n
        var minutes = +(parts[1] * 60) + toInt(parts[2]);\n
\n
        return parts[0] === \'+\' ? minutes : -minutes;\n
    }\n
\n
    // Return a moment from input, that is local/utc/zone equivalent to model.\n
    function cloneWithOffset(input, model) {\n
        var res, diff;\n
        if (model._isUTC) {\n
            res = model.clone();\n
            diff = (isMoment(input) || isDate(input) ? +input : +local__createLocal(input)) - (+res);\n
            // Use low-level api, because this fn is low-level api.\n
            res._d.setTime(+res._d + diff);\n
            utils_hooks__hooks.updateOffset(res, false);\n
            return res;\n
        } else {\n
            return local__createLocal(input).local();\n
        }\n
        return model._isUTC ? local__createLocal(input).zone(model._offset || 0) : local__createLocal(input).local();\n
    }\n
\n
    function getDateOffset (m) {\n
        // On Firefox.24 Date#getTimezoneOffset returns a floating point.\n
        // https://github.com/moment/moment/pull/1871\n
        return -Math.round(m._d.getTimezoneOffset() / 15) * 15;\n
    }\n
\n
    // HOOKS\n
\n
    // This function will be called whenever a moment is mutated.\n
    // It is intended to keep the offset in sync with the timezone.\n
    utils_hooks__hooks.updateOffset = function () {};\n
\n
    // MOMENTS\n
\n
    // keepLocalTime = true means only change the timezone, without\n
    // affecting the local hour. So 5:31:26 +0300 --[utcOffset(2, true)]-->\n
    // 5:31:26 +0200 It is possible that 5:31:26 doesn\'t exist with offset\n
    // +0200, so we adjust the time as needed, to be valid.\n
    //\n
    // Keeping the time actually adds/subtracts (one hour)\n
    // from the actual represented time. That is why we call updateOffset\n
    // a second time. In case it wants us to change the offset again\n
    // _changeInProgress == true case, then we have to adjust, because\n
    // there is no such time in the given timezone.\n
    function getSetOffset (input, keepLocalTime) {\n
        var offset = this._offset || 0,\n
            localAdjust;\n
        if (input != null) {\n
            if (typeof input === \'string\') {\n
                input = offsetFromString(input);\n
            }\n
            if (Math.abs(input) < 16) {\n
                input = input * 60;\n
            }\n
            if (!this._isUTC && keepLocalTime) {\n
                localAdjust = getDateOffset(this);\n
            }\n
            this._offset = input;\n
            this._isUTC = true;\n
            if (localAdjust != null) {\n
                this.add(localAdjust, \'m\');\n
            }\n
            if (offset !== input) {\n
                if (!keepLocalTime || this._changeInProgress) {\n
                    add_subtract__addSubtract(this, create__createDuration(input - offset, \'m\'), 1, false);\n
                } else if (!this._changeInProgress) {\n
                    this._changeInProgress = true;\n
                    utils_hooks__hooks.updateOffset(this, true);\n
                    this._changeInProgress = null;\n
                }\n
            }\n
            return this;\n
        } else {\n
            return this._isUTC ? offset : getDateOffset(this);\n
        }\n
    }\n
\n
    function getSetZone (input, keepLocalTime) {\n
        if (input != null) {\n
            if (typeof input !== \'string\') {\n
                input = -input;\n
            }\n
\n
            this.utcOffset(input, keepLocalTime);\n
\n
            return this;\n
        } else {\n
            return -this.utcOffset();\n
        }\n
    }\n
\n
    function setOffsetToUTC (keepLocalTime) {\n
        return this.utcOffset(0, keepLocalTime);\n
    }\n
\n
    function setOffsetToLocal (keepLocalTime) {\n
        if (this._isUTC) {\n
            this.utcOffset(0, keepLocalTime);\n
            this._isUTC = false;\n
\n
            if (keepLocalTime) {\n
                this.subtract(getDateOffset(this), \'m\');\n
            }\n
        }\n
        return this;\n
    }\n
\n
    function setOffsetToParsedOffset () {\n
        if (this._tzm) {\n
            this.utcOffset(this._tzm);\n
        } else if (typeof this._i === \'string\') {\n
            this.utcOffset(offsetFromString(this._i));\n
        }\n
        return this;\n
    }\n
\n
    function hasAlignedHourOffset (input) {\n
        if (!input) {\n
            input = 0;\n
        }\n
        else {\n
            input = local__createLocal(input).utcOffset();\n
        }\n
\n
        return (this.utcOffset() - input) % 60 === 0;\n
    }\n
\n
    function isDaylightSavingTime () {\n
        return (\n
            this.utcOffset() > this.clone().month(0).utcOffset() ||\n
            this.utcOffset() > this.clone().month(5).utcOffset()\n
        );\n
    }\n
\n
    function isDaylightSavingTimeShifted () {\n
        if (this._a) {\n
            var other = this._isUTC ? create_utc__createUTC(this._a) : local__createLocal(this._a);\n
            return this.isValid() && compareArrays(this._a, other.toArray()) > 0;\n
        }\n
\n
        return false;\n
    }\n
\n
    function isLocal () {\n
        return !this._isUTC;\n
    }\n
\n
    function isUtcOffset () {\n
        return this._isUTC;\n
    }\n
\n
    function isUtc () {\n
        return this._isUTC && this._offset === 0;\n
    }\n
\n
    var aspNetRegex = /(\\-)?(?:(\\d*)\\.)?(\\d+)\\:(\\d+)(?:\\:(\\d+)\\.?(\\d{3})?)?/;\n
\n
    // from http://docs.closure-library.googlecode.com/git/closure_goog_date_date.js.source.html\n
    // somewhat more in line with 4.4.3.2 2004 spec, but allows decimal anywhere\n
    var create__isoRegex = /^(-)?P(?:(?:([0-9,.]*)Y)?(?:([0-9,.]*)M)?(?:([0-9,.]*)D)?(?:T(?:([0-9,.]*)H)?(?:([0-9,.]*)M)?(?:([0-9,.]*)S)?)?|([0-9,.]*)W)$/;\n
\n
    function create__createDuration (input, key) {\n
        var duration = input,\n
            // matching against regexp is expensive, do it on demand\n
            match = null,\n
            sign,\n
            ret,\n
            diffRes;\n
\n
        if (isDuration(input)) {\n
            duration = {\n
                ms : input._milliseconds,\n
                d  : input._days,\n
                M  : input._months\n
            };\n
        } else if (typeof input === \'number\') {\n
            duration = {};\n
            if (key) {\n
                duration[key] = input;\n
            } else {\n
                duration.milliseconds = input;\n
            }\n
        } else if (!!(match = aspNetRegex.exec(input))) {\n
            sign = (match[1] === \'-\') ? -1 : 1;\n
            duration = {\n
                y  : 0,\n
                d  : toInt(match[DATE])        * sign,\n
                h  : toInt(match[HOUR])        * sign,\n
                m  : toInt(match[MINUTE])      * sign,\n
                s  : toInt(match[SECOND])      * sign,\n
                ms : toInt(match[MILLISECOND]) * sign\n
            };\n
        } else if (!!(match = create__isoRegex.exec(input))) {\n
            sign = (match[1] === \'-\') ? -1 : 1;\n
            duration = {\n
                y : parseIso(match[2], sign),\n
                M : parseIso(match[3], sign),\n
                d : parseIso(match[4], sign),\n
                h : parseIso(match[5], sign),\n
                m : parseIso(match[6], sign),\n
                s : parseIso(match[7], sign),\n
                w : parseIso(match[8], sign)\n
            };\n
        } else if (duration == null) {// checks for null or undefined\n
            duration = {};\n
        } else if (typeof duration === \'object\' && (\'from\' in duration || \'to\' in duration)) {\n
            diffRes = momentsDifference(local__createLocal(duration.from), local__createLocal(duration.to));\n
\n
            duration = {};\n
            duration.ms = diffRes.milliseconds;\n
            duration.M = diffRes.months;\n
        }\n
\n
        ret = new Duration(duration);\n
\n
        if (isDuration(input) && hasOwnProp(input, \'_locale\')) {\n
            ret._locale = input._locale;\n
        }\n
\n
        return ret;\n
    }\n
\n
    create__createDuration.fn = Duration.prototype;\n
\n
    function parseIso (inp, sign) {\n
        // We\'d normally use ~~inp for this, but unfortunately it also\n
        // converts floats to ints.\n
        // inp may be undefined, so careful calling replace on it.\n
        var res = inp && parseFloat(inp.replace(\',\', \'.\'));\n
        // apply sign while we\'re at it\n
        return (isNaN(res) ? 0 : res) * sign;\n
    }\n
\n
    function positiveMomentsDifference(base, other) {\n
        var res = {milliseconds: 0, months: 0};\n
\n
        res.months = other.month() - base.month() +\n
            (other.year() - base.year()) * 12;\n
        if (base.clone().add(res.months, \'M\').isAfter(other)) {\n
            --res.months;\n
        }\n
\n
        res.milliseconds = +other - +(base.clone().add(res.months, \'M\'));\n
\n
        return res;\n
    }\n
\n
    function momentsDifference(base, other) {\n
        var res;\n
        other = cloneWithOffset(other, base);\n
        if (base.isBefore(other)) {\n
            res = positiveMomentsDifference(base, other);\n
        } else {\n
            res = positiveMomentsDifference(other, base);\n
            res.milliseconds = -res.milliseconds;\n
            res.months = -res.months;\n
        }\n
\n
        return res;\n
    }\n
\n
    function createAdder(direction, name) {\n
        return function (val, period) {\n
            var dur, tmp;\n
            //invert the arguments, but complain about it\n
            if (period !== null && !isNaN(+period)) {\n
                deprecateSimple(name, \'moment().\' + name  + \'(period, number) is deprecated. Please use moment().\' + name + \'(number, period).\');\n
                tmp = val; val = period; period = tmp;\n
            }\n
\n
            val = typeof val === \'string\' ? +val : val;\n
            dur = create__createDuration(val, period);\n
            add_subtract__addSubtract(this, dur, direction);\n
            return this;\n
        };\n
    }\n
\n
    function add_subtract__addSubtract (mom, duration, isAdding, updateOffset) {\n
        var milliseconds = duration._milliseconds,\n
            days = duration._days,\n
            months = duration._months;\n
        updateOffset = updateOffset == null ? true : updateOffset;\n
\n
        if (milliseconds) {\n
            mom._d.setTime(+mom._d + milliseconds * isAdding);\n
        }\n
        if (days) {\n
            get_set__set(mom, \'Date\', get_set__get(mom, \'Date\') + days * isAdding);\n
        }\n
        if (months) {\n
            setMonth(mom, get_set__get(mom, \'Month\') + months * isAdding);\n
        }\n
        if (updateOffset) {\n
            utils_hooks__hooks.updateOffset(mom, days || months);\n
        }\n
    }\n
\n
    var add_subtract__add      = createAdder(1, \'add\');\n
    var add_subtract__subtract = createAdder(-1, \'subtract\');\n
\n
    function moment_calendar__calendar (time) {\n
        // We want to compare the start of today, vs this.\n
        // Getting start-of-today depends on whether we\'re local/utc/offset or not.\n
        var now = time || local__createLocal(),\n
            sod = cloneWithOffset(now, this).startOf(\'day\'),\n
            diff = this.diff(sod, \'days\', true),\n
            format = diff < -6 ? \'sameElse\' :\n
                diff < -1 ? \'lastWeek\' :\n
                diff < 0 ? \'lastDay\' :\n
                diff < 1 ? \'sameDay\' :\n
                diff < 2 ? \'nextDay\' :\n
                diff < 7 ? \'nextWeek\' : \'sameElse\';\n
        return this.format(this.localeData().calendar(format, this, local__createLocal(now)));\n
    }\n
\n
    function clone () {\n
        return new Moment(this);\n
    }\n
\n
    function isAfter (input, units) {\n
        var inputMs;\n
        units = normalizeUnits(typeof units !== \'undefined\' ? units : \'millisecond\');\n
        if (units === \'millisecond\') {\n
            input = isMoment(input) ? input : local__createLocal(input);\n
            return +this > +input;\n
        } else {\n
            inputMs = isMoment(input) ? +input : +local__createLocal(input);\n
            return inputMs < +this.clone().startOf(units);\n
        }\n
    }\n
\n
    function isBefore (input, units) {\n
        var inputMs;\n
        units = normalizeUnits(typeof units !== \'undefined\' ? units : \'millisecond\');\n
        if (units === \'millisecond\') {\n
            input = isMoment(input) ? input : local__createLocal(input);\n
            return +this < +input;\n
        } else {\n
            inputMs = isMoment(input) ? +input : +local__createLocal(input);\n
            return +this.clone().endOf(units) < inputMs;\n
        }\n
    }\n
\n
    function isBetween (from, to, units) {\n
        return this.isAfter(from, units) && this.isBefore(to, units);\n
    }\n
\n
    function isSame (input, units) {\n
        var inputMs;\n
        units = normalizeUnits(units || \'millisecond\');\n
        if (units === \'millisecond\') {\n
            input = isMoment(input) ? input : local__createLocal(input);\n
            return +this === +input;\n
        } else {\n
            inputMs = +local__createLocal(input);\n
            return +(this.clone().startOf(units)) <= inputMs && inputMs <= +(this.clone().endOf(units));\n
        }\n
    }\n
\n
    function absFloor (number) {\n
        if (number < 0) {\n
            return Math.ceil(number);\n
        } else {\n
            return Math.floor(number);\n
        }\n
    }\n
\n
    function diff (input, units, asFloat) {\n
        var that = cloneWithOffset(input, this),\n
            zoneDelta = (that.utcOffset() - this.utcOffset()) * 6e4,\n
            delta, output;\n
\n
        units = normalizeUnits(units);\n
\n
        if (units === \'year\' || units === \'month\' || units === \'quarter\') {\n
            output = monthDiff(this, that);\n
            if (units === \'quarter\') {\n
                output = output / 3;\n
            } else if (units === \'year\') {\n
                output = output / 12;\n
            }\n
        } else {\n
            delta = this - that;\n
            output = units === \'second\' ? delta / 1e3 : // 1000\n
                units === \'minute\' ? delta / 6e4 : // 1000 * 60\n
                units === \'hour\' ? delta / 36e5 : // 1000 * 60 * 60\n
                units === \'day\' ? (delta - zoneDelta) / 864e5 : // 1000 * 60 * 60 * 24, negate dst\n
                units === \'week\' ? (delta - zoneDelta) / 6048e5 : // 1000 * 60 * 60 * 24 * 7, negate dst\n
                delta;\n
        }\n
        return asFloat ? output : absFloor(output);\n
    }\n
\n
    function monthDiff (a, b) {\n
        // difference in months\n
        var wholeMonthDiff = ((b.year() - a.year()) * 12) + (b.month() - a.month()),\n
            // b is in (anchor - 1 month, anchor + 1 month)\n
            anchor = a.clone().add(wholeMonthDiff, \'months\'),\n
            anchor2, adjust;\n
\n
        if (b - anchor < 0) {\n
            anchor2 = a.clone().add(wholeMonthDiff - 1, \'months\');\n
            // linear across the month\n
            adjust = (b - anchor) / (anchor - anchor2);\n
        } else {\n
            anchor2 = a.clone().add(wholeMonthDiff + 1, \'months\');\n
            // linear across the month\n
            adjust = (b - anchor) / (anchor2 - anchor);\n
        }\n
\n
        return -(wholeMonthDiff + adjust);\n
    }\n
\n
    utils_hooks__hooks.defaultFormat = \'YYYY-MM-DDTHH:mm:ssZ\';\n
\n
    function toString () {\n
        return this.clone().locale(\'en\').format(\'ddd MMM DD YYYY HH:mm:ss [GMT]ZZ\');\n
    }\n
\n
    function moment_format__toISOString () {\n
        var m = this.clone().utc();\n
        if (0 < m.year() && m.year() <= 9999) {\n
            if (\'function\' === typeof Date.prototype.toISOString) {\n
                // native implementation is ~50x faster, use it when we can\n
                return this.toDate().toISOString();\n
            } else {\n
                return formatMoment(m, \'YYYY-MM-DD[T]HH:mm:ss.SSS[Z]\');\n
            }\n
        } else {\n
            return formatMoment(m, \'YYYYYY-MM-DD[T]HH:mm:ss.SSS[Z]\');\n
        }\n
    }\n
\n
    function format (inputString) {\n
        var output = formatMoment(this, inputString || utils_hooks__hooks.defaultFormat);\n
        return this.localeData().postformat(output);\n
    }\n
\n
    function from (time, withoutSuffix) {\n
        return create__createDuration({to: this, from: time}).locale(this.locale()).humanize(!withoutSuffix);\n
    }\n
\n
    function fromNow (withoutSuffix) {\n
        return this.from(local__createLocal(), withoutSuffix);\n
    }\n
\n
    function locale (key) {\n
        var newLocaleData;\n
\n
        if (key === undefined) {\n
            return this._locale._abbr;\n
        } else {\n
            newLocaleData = locale_locales__getLocale(key);\n
            if (newLocaleData != null) {\n
                this._locale = newLocaleData;\n
            }\n
            return this;\n
        }\n
    }\n
\n
    var lang = deprecate(\n
        \'moment().lang() is deprecated. Instead, use moment().localeData() to get the language configuration. Use moment().locale() to change languages.\',\n
        function (key) {\n
            if (key === undefined) {\n
                return this.localeData();\n
            } else {\n
                return this.locale(key);\n
            }\n
        }\n
    );\n
\n
    function localeData () {\n
        return this._locale;\n
    }\n
\n
    function startOf (units) {\n
        units = normalizeUnits(units);\n
        // the following switch intentionally omits break keywords\n
        // to utilize falling through the cases.\n
        switch (units) {\n
        case \'year\':\n
            this.month(0);\n
            /* falls through */\n
        case \'quarter\':\n
        case \'month\':\n
            this.date(1);\n
            /* falls through */\n
        case \'week\':\n
        case \'isoWeek\':\n
        case \'day\':\n
            this.hours(0);\n
            /* falls through */\n
        case \'hour\':\n
            this.minutes(0);\n
            /* falls through */\n
        case \'minute\':\n
            this.seconds(0);\n
            /* falls through */\n
        case \'second\':\n
            this.milliseconds(0);\n
        }\n
\n
        // weeks are a special case\n
        if (units === \'week\') {\n
            this.weekday(0);\n
        }\n
        if (units === \'isoWeek\') {\n
            this.isoWeekday(1);\n
        }\n
\n
        // quarters are also special\n
        if (units === \'quarter\') {\n
            this.month(Math.floor(this.month() / 3) * 3);\n
        }\n
\n
        return this;\n
    }\n
\n
    function endOf (units) {\n
        units = normalizeUnits(units);\n
        if (units === undefined || units === \'millisecond\') {\n
            return this;\n
        }\n
        return this.startOf(units).add(1, (units === \'isoWeek\' ? \'week\' : units)).subtract(1, \'ms\');\n
    }\n
\n
    function to_type__valueOf () {\n
        return +this._d - ((this._offset || 0) * 60000);\n
    }\n
\n
    function unix () {\n
        return Math.floor(+this / 1000);\n
    }\n
\n
    function toDate () {\n
        return this._offset ? new Date(+this) : this._d;\n
    }\n
\n
    function toArray () {\n
        var m = this;\n
        return [m.year(), m.month(), m.date(), m.hour(), m.minute(), m.second(), m.millisecond()];\n
    }\n
\n
    function moment_valid__isValid () {\n
        return valid__isValid(this);\n
    }\n
\n
    function parsingFlags () {\n
        return extend({}, this._pf);\n
    }\n
\n
    function invalidAt () {\n
        return this._pf.overflow;\n
    }\n
\n
    addFormatToken(0, [\'gg\', 2], 0, function () {\n
        return this.weekYear() % 100;\n
    });\n
\n
    addFormatToken(0, [\'GG\', 2], 0, function () {\n
        return this.isoWeekYear() % 100;\n
    });\n
\n
    function addWeekYearFormatToken (token, getter) {\n
        addFormatToken(0, [token, token.length], 0, getter);\n
    }\n
\n
    addWeekYearFormatToken(\'gggg\',     \'weekYear\');\n
    addWeekYearFormatToken(\'ggggg\',    \'weekYear\');\n
    addWeekYearFormatToken(\'GGGG\',  \'isoWeekYear\');\n
    addWeekYearFormatToken(\'GGGGG\', \'isoWeekYear\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'weekYear\', \'gg\');\n
    addUnitAlias(\'isoWeekYear\', \'GG\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'G\',      matchSigned);\n
    addRegexToken(\'g\',      matchSigned);\n
    addRegexToken(\'GG\',     match1to2, match2);\n
    addRegexToken(\'gg\',     match1to2, match2);\n
    addRegexToken(\'GGGG\',   match1to4, match4);\n
    addRegexToken(\'gggg\',   match1to4, match4);\n
    addRegexToken(\'GGGGG\',  match1to6, match6);\n
    addRegexToken(\'ggggg\',  match1to6, match6);\n
\n
    addWeekParseToken([\'gggg\', \'ggggg\', \'GGGG\', \'GGGGG\'], function (input, week, config, token) {\n
        week[token.substr(0, 2)] = toInt(input);\n
    });\n
\n
    addWeekParseToken([\'gg\', \'GG\'], function (input, week, config, token) {\n
        week[token] = utils_hooks__hooks.parseTwoDigitYear(input);\n
    });\n
\n
    // HELPERS\n
\n
    function weeksInYear(year, dow, doy) {\n
        return weekOfYear(local__createLocal([year, 11, 31 + dow - doy]), dow, doy).week;\n
    }\n
\n
    // MOMENTS\n
\n
    function getSetWeekYear (input) {\n
        var year = weekOfYear(this, this.localeData()._week.dow, this.localeData()._week.doy).year;\n
        return input == null ? year : this.add((input - year), \'y\');\n
    }\n
\n
    function getSetISOWeekYear (input) {\n
        var year = weekOfYear(this, 1, 4).year;\n
        return input == null ? year : this.add((input - year), \'y\');\n
    }\n
\n
    function getISOWeeksInYear () {\n
        return weeksInYear(this.year(), 1, 4);\n
    }\n
\n
    function getWeeksInYear () {\n
        var weekInfo = this.localeData()._week;\n
        return weeksInYear(this.year(), weekInfo.dow, weekInfo.doy);\n
    }\n
\n
    addFormatToken(\'Q\', 0, 0, \'quarter\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'quarter\', \'Q\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'Q\', match1);\n
    addParseToken(\'Q\', function (input, array) {\n
        array[MONTH] = (toInt(input) - 1) * 3;\n
    });\n
\n
    // MOMENTS\n
\n
    function getSetQuarter (input) {\n
        return input == null ? Math.ceil((this.month() + 1) / 3) : this.month((input - 1) * 3 + this.month() % 3);\n
    }\n
\n
    addFormatToken(\'D\', [\'DD\', 2], \'Do\', \'date\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'date\', \'D\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'D\',  match1to2);\n
    addRegexToken(\'DD\', match1to2, match2);\n
    addRegexToken(\'Do\', function (isStrict, locale) {\n
        return isStrict ? locale._ordinalParse : locale._ordinalParseLenient;\n
    });\n
\n
    addParseToken([\'D\', \'DD\'], DATE);\n
    addParseToken(\'Do\', function (input, array) {\n
        array[DATE] = toInt(input.match(match1to2)[0], 10);\n
    });\n
\n
    // MOMENTS\n
\n
    var getSetDayOfMonth = makeGetSet(\'Date\', true);\n
\n
    addFormatToken(\'d\', 0, \'do\', \'day\');\n
\n
    addFormatToken(\'dd\', 0, 0, function (format) {\n
        return this.localeData().weekdaysMin(this, format);\n
    });\n
\n
    addFormatToken(\'ddd\', 0, 0, function (format) {\n
        return this.localeData().weekdaysShort(this, format);\n
    });\n
\n
    addFormatToken(\'dddd\', 0, 0, function (format) {\n
        return this.localeData().weekdays(this, format);\n
    });\n
\n
    addFormatToken(\'e\', 0, 0, \'weekday\');\n
    addFormatToken(\'E\', 0, 0, \'isoWeekday\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'day\', \'d\');\n
    addUnitAlias(\'weekday\', \'e\');\n
    addUnitAlias(\'isoWeekday\', \'E\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'d\',    match1to2);\n
    addRegexToken(\'e\',    match1to2);\n
    addRegexToken(\'E\',    match1to2);\n
    addRegexToken(\'dd\',   matchWord);\n
    addRegexToken(\'ddd\',  matchWord);\n
    addRegexToken(\'dddd\', matchWord);\n
\n
    addWeekParseToken([\'dd\', \'ddd\', \'dddd\'], function (input, week, config) {\n
        var weekday = config._locale.weekdaysParse(input);\n
        // if we didn\'t get a weekday name, mark the date as invalid\n
        if (weekday != null) {\n
            week.d = weekday;\n
        } else {\n
            config._pf.invalidWeekday = input;\n
        }\n
    });\n
\n
    addWeekParseToken([\'d\', \'e\', \'E\'], function (input, week, config, token) {\n
        week[token] = toInt(input);\n
    });\n
\n
    // HELPERS\n
\n
    function parseWeekday(input, locale) {\n
        if (typeof input === \'string\') {\n
            if (!isNaN(input)) {\n
                input = parseInt(input, 10);\n
            }\n
            else {\n
                input = locale.weekdaysParse(input);\n
                if (typeof input !== \'number\') {\n
                    return null;\n
                }\n
            }\n
        }\n
        return input;\n
    }\n
\n
    // LOCALES\n
\n
    var defaultLocaleWeekdays = \'Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday\'.split(\'_\');\n
    function localeWeekdays (m) {\n
        return this._weekdays[m.day()];\n
    }\n
\n
    var defaultLocaleWeekdaysShort = \'Sun_Mon_Tue_Wed_Thu_Fri_Sat\'.split(\'_\');\n
    function localeWeekdaysShort (m) {\n
        return this._weekdaysShort[m.day()];\n
    }\n
\n
    var defaultLocaleWeekdaysMin = \'Su_Mo_Tu_We_Th_Fr_Sa\'.split(\'_\');\n
    function localeWeekdaysMin (m) {\n
        return this._weekdaysMin[m.day()];\n
    }\n
\n
    function localeWeekdaysParse (weekdayName) {\n
        var i, mom, regex;\n
\n
        if (!this._weekdaysParse) {\n
            this._weekdaysParse = [];\n
        }\n
\n
        for (i = 0; i < 7; i++) {\n
            // make the regex if we don\'t have it already\n
            if (!this._weekdaysParse[i]) {\n
                mom = local__createLocal([2000, 1]).day(i);\n
                regex = \'^\' + this.weekdays(mom, \'\') + \'|^\' + this.weekdaysShort(mom, \'\') + \'|^\' + this.weekdaysMin(mom, \'\');\n
                this._weekdaysParse[i] = new RegExp(regex.replace(\'.\', \'\'), \'i\');\n
            }\n
            // test the regex\n
            if (this._weekdaysParse[i].test(weekdayName)) {\n
                return i;\n
            }\n
        }\n
    }\n
\n
    // MOMENTS\n
\n
    function getSetDayOfWeek (input) {\n
        var day = this._isUTC ? this._d.getUTCDay() : this._d.getDay();\n
        if (input != null) {\n
            input = parseWeekday(input, this.localeData());\n
            return this.add(input - day, \'d\');\n
        } else {\n
            return day;\n
        }\n
    }\n
\n
    function getSetLocaleDayOfWeek (input) {\n
        var weekday = (this.day() + 7 - this.localeData()._week.dow) % 7;\n
        return input == null ? weekday : this.add(input - weekday, \'d\');\n
    }\n
\n
    function getSetISODayOfWeek (input) {\n
        // behaves the same as moment#day except\n
        // as a getter, returns 7 instead of 0 (1-7 range instead of 0-6)\n
        // as a setter, sunday should belong to the previous week.\n
        return input == null ? this.day() || 7 : this.day(this.day() % 7 ? input : input - 7);\n
    }\n
\n
    addFormatToken(\'H\', [\'HH\', 2], 0, \'hour\');\n
    addFormatToken(\'h\', [\'hh\', 2], 0, function () {\n
        return this.hours() % 12 || 12;\n
    });\n
\n
    function meridiem (token, lowercase) {\n
        addFormatToken(token, 0, 0, function () {\n
            return this.localeData().meridiem(this.hours(), this.minutes(), lowercase);\n
        });\n
    }\n
\n
    meridiem(\'a\', true);\n
    meridiem(\'A\', false);\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'hour\', \'h\');\n
\n
    // PARSING\n
\n
    function matchMeridiem (isStrict, locale) {\n
        return locale._meridiemParse;\n
    }\n
\n
    addRegexToken(\'a\',  matchMeridiem);\n
    addRegexToken(\'A\',  matchMeridiem);\n
    addRegexToken(\'H\',  match1to2);\n
    addRegexToken(\'h\',  match1to2);\n
    addRegexToken(\'HH\', match1to2, match2);\n
    addRegexToken(\'hh\', match1to2, match2);\n
\n
    addParseToken([\'H\', \'HH\'], HOUR);\n
    addParseToken([\'a\', \'A\'], function (input, array, config) {\n
        config._isPm = config._locale.isPM(input);\n
        config._meridiem = input;\n
    });\n
    addParseToken([\'h\', \'hh\'], function (input, array, config) {\n
        array[HOUR] = toInt(input);\n
        config._pf.bigHour = true;\n
    });\n
\n
    // LOCALES\n
\n
    function localeIsPM (input) {\n
        // IE8 Quirks Mode & IE7 Standards Mode do not allow accessing strings like arrays\n
        // Using charAt should be more compatible.\n
        return ((input + \'\').toLowerCase().charAt(0) === \'p\');\n
    }\n
\n
    var defaultLocaleMeridiemParse = /[ap]\\.?m?\\.?/i;\n
    function localeMeridiem (hours, minutes, isLower) {\n
        if (hours > 11) {\n
            return isLower ? \'pm\' : \'PM\';\n
        } else {\n
            return isLower ? \'am\' : \'AM\';\n
        }\n
    }\n
\n
\n
    // MOMENTS\n
\n
    // Setting the hour should keep the time, because the user explicitly\n
    // specified which hour he wants. So trying to maintain the same hour (in\n
    // a new timezone) makes sense. Adding/subtracting hours does not follow\n
    // this rule.\n
    var getSetHour = makeGetSet(\'Hours\', true);\n
\n
    addFormatToken(\'m\', [\'mm\', 2], 0, \'minute\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'minute\', \'m\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'m\',  match1to2);\n
    addRegexToken(\'mm\', match1to2, match2);\n
    addParseToken([\'m\', \'mm\'], MINUTE);\n
\n
    // MOMENTS\n
\n
    var getSetMinute = makeGetSet(\'Minutes\', false);\n
\n
    addFormatToken(\'s\', [\'ss\', 2], 0, \'second\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'second\', \'s\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'s\',  match1to2);\n
    addRegexToken(\'ss\', match1to2, match2);\n
    addParseToken([\'s\', \'ss\'], SECOND);\n
\n
    // MOMENTS\n
\n
    var getSetSecond = makeGetSet(\'Seconds\', false);\n
\n
    addFormatToken(\'S\', 0, 0, function () {\n
        return ~~(this.millisecond() / 100);\n
    });\n
\n
    addFormatToken(0, [\'SS\', 2], 0, function () {\n
        return ~~(this.millisecond() / 10);\n
    });\n
\n
    function millisecond__milliseconds (token) {\n
        addFormatToken(0, [token, 3], 0, \'millisecond\');\n
    }\n
\n
    millisecond__milliseconds(\'SSS\');\n
    millisecond__milliseconds(\'SSSS\');\n
\n
    // ALIASES\n
\n
    addUnitAlias(\'millisecond\', \'ms\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'S\',    match1to3, match1);\n
    addRegexToken(\'SS\',   match1to3, match2);\n
    addRegexToken(\'SSS\',  match1to3, match3);\n
    addRegexToken(\'SSSS\', matchUnsigned);\n
    addParseToken([\'S\', \'SS\', \'SSS\', \'SSSS\'], function (input, array) {\n
        array[MILLISECOND] = toInt((\'0.\' + input) * 1000);\n
    });\n
\n
    // MOMENTS\n
\n
    var getSetMillisecond = makeGetSet(\'Milliseconds\', false);\n
\n
    addFormatToken(\'z\',  0, 0, \'zoneAbbr\');\n
    addFormatToken(\'zz\', 0, 0, \'zoneName\');\n
\n
    // MOMENTS\n
\n
    function getZoneAbbr () {\n
        return this._isUTC ? \'UTC\' : \'\';\n
    }\n
\n
    function getZoneName () {\n
        return this._isUTC ? \'Coordinated Universal Time\' : \'\';\n
    }\n
\n
    var momentPrototype__proto = Moment.prototype;\n
\n
    momentPrototype__proto.add          = add_subtract__add;\n
    momentPrototype__proto.calendar     = moment_calendar__calendar;\n
    momentPrototype__proto.clone        = clone;\n
    momentPrototype__proto.diff         = diff;\n
    momentPrototype__proto.endOf        = endOf;\n
    momentPrototype__proto.format       = format;\n
    momentPrototype__proto.from         = from;\n
    momentPrototype__proto.fromNow      = fromNow;\n
    momentPrototype__proto.get          = getSet;\n
    momentPrototype__proto.invalidAt    = invalidAt;\n
    momentPrototype__proto.isAfter      = isAfter;\n
    momentPrototype__proto.isBefore     = isBefore;\n
    momentPrototype__proto.isBetween    = isBetween;\n
    momentPrototype__proto.isSame       = isSame;\n
    momentPrototype__proto.isValid      = moment_valid__isValid;\n
    momentPrototype__proto.lang         = lang;\n
    momentPrototype__proto.locale       = locale;\n
    momentPrototype__proto.localeData   = localeData;\n
    momentPrototype__proto.max          = prototypeMax;\n
    momentPrototype__proto.min          = prototypeMin;\n
    momentPrototype__proto.parsingFlags = parsingFlags;\n
    momentPrototype__proto.set          = getSet;\n
    momentPrototype__proto.startOf      = startOf;\n
    momentPrototype__proto.subtract     = add_subtract__subtract;\n
    momentPrototype__proto.toArray      = toArray;\n
    momentPrototype__proto.toDate       = toDate;\n
    momentPrototype__proto.toISOString  = moment_format__toISOString;\n
    momentPrototype__proto.toJSON       = moment_format__toISOString;\n
    momentPrototype__proto.toString     = toString;\n
    momentPrototype__proto.unix         = unix;\n
    momentPrototype__proto.valueOf      = to_type__valueOf;\n
\n
    // Year\n
    momentPrototype__proto.year       = getSetYear;\n
    momentPrototype__proto.isLeapYear = getIsLeapYear;\n
\n
    // Week Year\n
    momentPrototype__proto.weekYear    = getSetWeekYear;\n
    momentPrototype__proto.isoWeekYear = getSetISOWeekYear;\n
\n
    // Quarter\n
    momentPrototype__proto.quarter = momentPrototype__proto.quarters = getSetQuarter;\n
\n
    // Month\n
    momentPrototype__proto.month       = getSetMonth;\n
    momentPrototype__proto.daysInMonth = getDaysInMonth;\n
\n
    // Week\n
    momentPrototype__proto.week           = momentPrototype__proto.weeks        = getSetWeek;\n
    momentPrototype__proto.isoWeek        = momentPrototype__proto.isoWeeks     = getSetISOWeek;\n
    momentPrototype__proto.weeksInYear    = getWeeksInYear;\n
    momentPrototype__proto.isoWeeksInYear = getISOWeeksInYear;\n
\n
    // Day\n
    momentPrototype__proto.date       = getSetDayOfMonth;\n
    momentPrototype__proto.day        = momentPrototype__proto.days             = getSetDayOfWeek;\n
    momentPrototype__proto.weekday    = getSetLocaleDayOfWeek;\n
    momentPrototype__proto.isoWeekday = getSetISODayOfWeek;\n
    momentPrototype__proto.dayOfYear  = getSetDayOfYear;\n
\n
    // Hour\n
    momentPrototype__proto.hour = momentPrototype__proto.hours = getSetHour;\n
\n
    // Minute\n
    momentPrototype__proto.minute = momentPrototype__proto.minutes = getSetMinute;\n
\n
    // Second\n
    momentPrototype__proto.second = momentPrototype__proto.seconds = getSetSecond;\n
\n
    // Millisecond\n
    momentPrototype__proto.millisecond = momentPrototype__proto.milliseconds = getSetMillisecond;\n
\n
    // Offset\n
    momentPrototype__proto.utcOffset            = getSetOffset;\n
    momentPrototype__proto.utc                  = setOffsetToUTC;\n
    momentPrototype__proto.local                = setOffsetToLocal;\n
    momentPrototype__proto.parseZone            = setOffsetToParsedOffset;\n
    momentPrototype__proto.hasAlignedHourOffset = hasAlignedHourOffset;\n
    momentPrototype__proto.isDST                = isDaylightSavingTime;\n
    momentPrototype__proto.isDSTShifted         = isDaylightSavingTimeShifted;\n
    momentPrototype__proto.isLocal              = isLocal;\n
    momentPrototype__proto.isUtcOffset          = isUtcOffset;\n
    momentPrototype__proto.isUtc                = isUtc;\n
    momentPrototype__proto.isUTC                = isUtc;\n
\n
    // Timezone\n
    momentPrototype__proto.zoneAbbr = getZoneAbbr;\n
    momentPrototype__proto.zoneName = getZoneName;\n
\n
    // Deprecations\n
    momentPrototype__proto.dates  = deprecate(\'dates accessor is deprecated. Use date instead.\', getSetDayOfMonth);\n
    momentPrototype__proto.months = deprecate(\'months accessor is deprecated. Use month instead\', getSetMonth);\n
    momentPrototype__proto.years  = deprecate(\'years accessor is deprecated. Use year instead\', getSetYear);\n
    momentPrototype__proto.zone   = deprecate(\'moment().zone is deprecated, use moment().utcOffset instead. https://github.com/moment/moment/issues/1779\', getSetZone);\n
\n
    var momentPrototype = momentPrototype__proto;\n
\n
    function moment__createUnix (input) {\n
        return local__createLocal(input * 1000);\n
    }\n
\n
    function moment__createInZone () {\n
        return local__createLocal.apply(null, arguments).parseZone();\n
    }\n
\n
    var defaultCalendar = {\n
        sameDay : \'[Today at] LT\',\n
        nextDay : \'[Tomorrow at] LT\',\n
        nextWeek : \'dddd [at] LT\',\n
        lastDay : \'[Yesterday at] LT\',\n
        lastWeek : \'[Last] dddd [at] LT\',\n
        sameElse : \'L\'\n
    };\n
\n
    function locale_calendar__calendar (key, mom, now) {\n
        var output = this._calendar[key];\n
        return typeof output === \'function\' ? output.call(mom, now) : output;\n
    }\n
\n
    var defaultLongDateFormat = {\n
        LTS  : \'h:mm:ss A\',\n
        LT   : \'h:mm A\',\n
        L    : \'MM/DD/YYYY\',\n
        LL   : \'MMMM D, YYYY\',\n
        LLL  : \'MMMM D, YYYY LT\',\n
        LLLL : \'dddd, MMMM D, YYYY LT\'\n
    };\n
\n
    function longDateFormat (key) {\n
        var output = this._longDateFormat[key];\n
        if (!output && this._longDateFormat[key.toUpperCase()]) {\n
            output = this._longDateFormat[key.toUpperCase()].replace(/MMMM|MM|DD|dddd/g, function (val) {\n
                return val.slice(1);\n
            });\n
            this._longDateFormat[key] = output;\n
        }\n
        return output;\n
    }\n
\n
    var defaultInvalidDate = \'Invalid date\';\n
\n
    function invalidDate () {\n
        return this._invalidDate;\n
    }\n
\n
    var defaultOrdinal = \'%d\';\n
    var defaultOrdinalParse = /\\d{1,2}/;\n
\n
    function ordinal (number) {\n
        return this._ordinal.replace(\'%d\', number);\n
    }\n
\n
    function preParsePostFormat (string) {\n
        return string;\n
    }\n
\n
    var defaultRelativeTime = {\n
        future : \'in %s\',\n
        past   : \'%s ago\',\n
        s  : \'a few seconds\',\n
        m  : \'a minute\',\n
        mm : \'%d minutes\',\n
        h  : \'an hour\',\n
        hh : \'%d hours\',\n
        d  : \'a day\',\n
        dd : \'%d days\',\n
        M  : \'a month\',\n
        MM : \'%d months\',\n
        y  : \'a year\',\n
        yy : \'%d years\'\n
    };\n
\n
    function relative__relativeTime (number, withoutSuffix, string, isFuture) {\n
        var output = this._relativeTime[string];\n
        return (typeof output === \'function\') ?\n
            output(number, withoutSuffix, string, isFuture) :\n
            output.replace(/%d/i, number);\n
    }\n
\n
    function pastFuture (diff, output) {\n
        var format = this._relativeTime[diff > 0 ? \'future\' : \'past\'];\n
        return typeof format === \'function\' ? format(output) : format.replace(/%s/i, output);\n
    }\n
\n
    function locale_set__set (config) {\n
        var prop, i;\n
        for (i in config) {\n
            prop = config[i];\n
            if (typeof prop === \'function\') {\n
                this[i] = prop;\n
            } else {\n
                this[\'_\' + i] = prop;\n
            }\n
        }\n
        // Lenient ordinal parsing accepts just a number in addition to\n
        // number + (possibly) stuff coming from _ordinalParseLenient.\n
        this._ordinalParseLenient = new RegExp(this._ordinalParse.source + \'|\' + /\\d{1,2}/.source);\n
    }\n
\n
    var prototype__proto = Locale.prototype;\n
\n
    prototype__proto._calendar       = defaultCalendar;\n
    prototype__proto.calendar        = locale_calendar__calendar;\n
    prototype__proto._longDateFormat = defaultLongDateFormat;\n
    prototype__proto.longDateFormat  = longDateFormat;\n
    prototype__proto._invalidDate    = defaultInvalidDate;\n
    prototype__proto.invalidDate     = invalidDate;\n
    prototype__proto._ordinal        = defaultOrdinal;\n
    prototype__proto.ordinal         = ordinal;\n
    prototype__proto._ordinalParse   = defaultOrdinalParse;\n
    prototype__proto.preparse        = preParsePostFormat;\n
    prototype__proto.postformat      = preParsePostFormat;\n
    prototype__proto._relativeTime   = defaultRelativeTime;\n
    prototype__proto.relativeTime    = relative__relativeTime;\n
    prototype__proto.pastFuture      = pastFuture;\n
    prototype__proto.set             = locale_set__set;\n
\n
    // Month\n
    prototype__proto.months       =        localeMonths;\n
    prototype__proto._months      = defaultLocaleMonths;\n
    prototype__proto.monthsShort  =        localeMonthsShort;\n
    prototype__proto._monthsShort = defaultLocaleMonthsShort;\n
    prototype__proto.monthsParse  =        localeMonthsParse;\n
\n
    // Week\n
    prototype__proto.week = localeWeek;\n
    prototype__proto._week = defaultLocaleWeek;\n
    prototype__proto.firstDayOfYear = localeFirstDayOfYear;\n
    prototype__proto.firstDayOfWeek = localeFirstDayOfWeek;\n
\n
    // Day of Week\n
    prototype__proto.weekdays       =        localeWeekdays;\n
    prototype__proto._weekdays      = defaultLocaleWeekdays;\n
    prototype__proto.weekdaysMin    =        localeWeekdaysMin;\n
    prototype__proto._weekdaysMin   = defaultLocaleWeekdaysMin;\n
    prototype__proto.weekdaysShort  =        localeWeekdaysShort;\n
    prototype__proto._weekdaysShort = defaultLocaleWeekdaysShort;\n
    prototype__proto.weekdaysParse  =        localeWeekdaysParse;\n
\n
    // Hours\n
    prototype__proto.isPM = localeIsPM;\n
    prototype__proto._meridiemParse = defaultLocaleMeridiemParse;\n
    prototype__proto.meridiem = localeMeridiem;\n
\n
    function lists__get (format, index, field, setter) {\n
        var locale = locale_locales__getLocale();\n
        var utc = create_utc__createUTC().set(setter, index);\n
        return locale[field](utc, format);\n
    }\n
\n
    function list (format, index, field, count, setter) {\n
        if (typeof format === \'number\') {\n
            index = format;\n
            format = undefined;\n
        }\n
\n
        format = format || \'\';\n
\n
        if (index != null) {\n
            return lists__get(format, index, field, setter);\n
        }\n
\n
        var i;\n
        var out = [];\n
        for (i = 0; i < count; i++) {\n
            out[i] = lists__get(format, i, field, setter);\n
        }\n
        return out;\n
    }\n
\n
    function lists__listMonths (format, index) {\n
        return list(format, index, \'months\', 12, \'month\');\n
    }\n
\n
    function lists__listMonthsShort (format, index) {\n
        return list(format, index, \'monthsShort\', 12, \'month\');\n
    }\n
\n
    function lists__listWeekdays (format, index) {\n
        return list(format, index, \'weekdays\', 7, \'day\');\n
    }\n
\n
    function lists__listWeekdaysShort (format, index) {\n
        return list(format, index, \'weekdaysShort\', 7, \'day\');\n
    }\n
\n
    function lists__listWeekdaysMin (format, index) {\n
        return list(format, index, \'weekdaysMin\', 7, \'day\');\n
    }\n
\n
    locale_locales__getSetGlobalLocale(\'en\', {\n
        ordinalParse: /\\d{1,2}(th|st|nd|rd)/,\n
        ordinal : function (number) {\n
            var b = number % 10,\n
                output = (toInt(number % 100 / 10) === 1) ? \'th\' :\n
                (b === 1) ? \'st\' :\n
                (b === 2) ? \'nd\' :\n
                (b === 3) ? \'rd\' : \'th\';\n
            return number + output;\n
        }\n
    });\n
\n
    // Side effect imports\n
    utils_hooks__hooks.lang = deprecate(\'moment.lang is deprecated. Use moment.locale instead.\', locale_locales__getSetGlobalLocale);\n
    utils_hooks__hooks.langData = deprecate(\'moment.langData is deprecated. Use moment.localeData instead.\', locale_locales__getLocale);\n
\n
    var mathAbs = Math.abs;\n
\n
    function duration_abs__abs () {\n
        var data           = this._data;\n
\n
        this._milliseconds = mathAbs(this._milliseconds);\n
        this._days         = mathAbs(this._days);\n
        this._months       = mathAbs(this._months);\n
\n
        data.milliseconds  = mathAbs(data.milliseconds);\n
        data.seconds       = mathAbs(data.seconds);\n
        data.minutes       = mathAbs(data.minutes);\n
        data.hours         = mathAbs(data.hours);\n
        data.months        = mathAbs(data.months);\n
        data.years         = mathAbs(data.years);\n
\n
        return this;\n
    }\n
\n
    function duration_add_subtract__addSubtract (duration, input, value, direction) {\n
        var other = create__createDuration(input, value);\n
\n
        duration._milliseconds += direction * other._milliseconds;\n
        duration._days         += direction * other._days;\n
        duration._months       += direction * other._months;\n
\n
        return duration._bubble();\n
    }\n
\n
    // supports only 2.0-style add(1, \'s\') or add(duration)\n
    function duration_add_subtract__add (input, value) {\n
        return duration_add_subtract__addSubtract(this, input, value, 1);\n
    }\n
\n
    // supports only 2.0-style subtract(1, \'s\') or subtract(duration)\n
    function duration_add_subtract__subtract (input, value) {\n
        return duration_add_subtract__addSubtract(this, input, value, -1);\n
    }\n
\n
    function bubble () {\n
        var milliseconds = this._milliseconds;\n
        var days         = this._days;\n
        var months       = this._months;\n
        var data         = this._data;\n
        var seconds, minutes, hours, years = 0;\n
\n
        // The following code bubbles up values, see the tests for\n
        // examples of what that means.\n
        data.milliseconds = milliseconds % 1000;\n
\n
        seconds           = absFloor(milliseconds / 1000);\n
        data.seconds      = seconds % 60;\n
\n
        minutes           = absFloor(seconds / 60);\n
        data.minutes      = minutes % 60;\n
\n
        hours             = absFloor(minutes / 60);\n
        data.hours        = hours % 24;\n
\n
        days += absFloor(hours / 24);\n
\n
        // Accurately convert days to years, assume start from year 0.\n
        years = absFloor(daysToYears(days));\n
        days -= absFloor(yearsToDays(years));\n
\n
        // 30 days to a month\n
        // TODO (iskren): Use anchor date (like 1st Jan) to compute this.\n
        months += absFloor(days / 30);\n
        days   %= 30;\n
\n
        // 12 months -> 1 year\n
        years  += absFloor(months / 12);\n
        months %= 12;\n
\n
        data.days   = days;\n
        data.months = months;\n
        data.years  = years;\n
\n
        return this;\n
    }\n
\n
    function daysToYears (days) {\n
        // 400 years have 146097 days (taking into account leap year rules)\n
        return days * 400 / 146097;\n
    }\n
\n
    function yearsToDays (years) {\n
        // years * 365 + absFloor(years / 4) -\n
        //     absFloor(years / 100) + absFloor(years / 400);\n
        return years * 146097 / 400;\n
    }\n
\n
    function as (units) {\n
        var days;\n
        var months;\n
        var milliseconds = this._milliseconds;\n
\n
        units = normalizeUnits(units);\n
\n
        if (units === \'month\' || units === \'year\') {\n
            days   = this._days   + milliseconds / 864e5;\n
            months = this._months + daysToYears(days) * 12;\n
            return units === \'month\' ? months : months / 12;\n
        } else {\n
            // handle milliseconds separately because of floating point math errors (issue #1867)\n
            days = this._days + Math.round(yearsToDays(this._months / 12));\n
            switch (units) {\n
                case \'week\'   : return days / 7            + milliseconds / 6048e5;\n
                case \'day\'    : return days                + milliseconds / 864e5;\n
                case \'hour\'   : return days * 24           + milliseconds / 36e5;\n
                case \'minute\' : return days * 24 * 60      + milliseconds / 6e4;\n
                case \'second\' : return days * 24 * 60 * 60 + milliseconds / 1000;\n
                // Math.floor prevents floating point math errors here\n
                case \'millisecond\': return Math.floor(days * 24 * 60 * 60 * 1000) + milliseconds;\n
                default: throw new Error(\'Unknown unit \' + units);\n
            }\n
        }\n
    }\n
\n
    // TODO: Use this.as(\'ms\')?\n
    function duration_as__valueOf () {\n
        return (\n
            this._milliseconds +\n
            this._days * 864e5 +\n
            (this._months % 12) * 2592e6 +\n
            toInt(this._months / 12) * 31536e6\n
        );\n
    }\n
\n
    function makeAs (alias) {\n
        return function () {\n
            return this.as(alias);\n
        };\n
    }\n
\n
    var asMilliseconds = makeAs(\'ms\');\n
    var asSeconds      = makeAs(\'s\');\n
    var asMinutes      = makeAs(\'m\');\n
    var asHours        = makeAs(\'h\');\n
    var asDays         = makeAs(\'d\');\n
    var asWeeks        = makeAs(\'w\');\n
    var asMonths       = makeAs(\'M\');\n
    var asYears        = makeAs(\'y\');\n
\n
    function duration_get__get (units) {\n
        units = normalizeUnits(units);\n
        return this[units + \'s\']();\n
    }\n
\n
    function makeGetter(name) {\n
        return function () {\n
            return this._data[name];\n
        };\n
    }\n
\n
    var duration_get__milliseconds = makeGetter(\'milliseconds\');\n
    var seconds      = makeGetter(\'seconds\');\n
    var minutes      = makeGetter(\'minutes\');\n
    var hours        = makeGetter(\'hours\');\n
    var days         = makeGetter(\'days\');\n
    var months       = makeGetter(\'months\');\n
    var years        = makeGetter(\'years\');\n
\n
    function weeks () {\n
        return absFloor(this.days() / 7);\n
    }\n
\n
    var round = Math.round;\n
    var thresholds = {\n
        s: 45,  // seconds to minute\n
        m: 45,  // minutes to hour\n
        h: 22,  // hours to day\n
        d: 26,  // days to month\n
        M: 11   // months to year\n
    };\n
\n
    // helper function for moment.fn.from, moment.fn.fromNow, and moment.duration.fn.humanize\n
    function substituteTimeAgo(string, number, withoutSuffix, isFuture, locale) {\n
        return locale.relativeTime(number || 1, !!withoutSuffix, string, isFuture);\n
    }\n
\n
    function duration_humanize__relativeTime (posNegDuration, withoutSuffix, locale) {\n
        var duration = create__createDuration(posNegDuration).abs();\n
        var seconds  = round(duration.as(\'s\'));\n
        var minutes  = round(duration.as(\'m\'));\n
        var hours    = round(duration.as(\'h\'));\n
        var days     = round(duration.as(\'d\'));\n
        var months   = round(duration.as(\'M\'));\n
        var years    = round(duration.as(\'y\'));\n
\n
        var a = seconds < thresholds.s && [\'s\', seconds]  ||\n
                minutes === 1          && [\'m\']           ||\n
                minutes < thresholds.m && [\'mm\', minutes] ||\n
                hours   === 1          && [\'h\']           ||\n
                hours   < thresholds.h && [\'hh\', hours]   ||\n
                days    === 1          && [\'d\']           ||\n
                days    < thresholds.d && [\'dd\', days]    ||\n
                months  === 1          && [\'M\']           ||\n
                months  < thresholds.M && [\'MM\', months]  ||\n
                years   === 1          && [\'y\']           || [\'yy\', years];\n
\n
        a[2] = withoutSuffix;\n
        a[3] = +posNegDuration > 0;\n
        a[4] = locale;\n
        return substituteTimeAgo.apply(null, a);\n
    }\n
\n
    // This function allows you to set a threshold for relative time strings\n
    function duration_humanize__getSetRelativeTimeThreshold (threshold, limit) {\n
        if (thresholds[threshold] === undefined) {\n
            return false;\n
        }\n
        if (limit === undefined) {\n
            return thresholds[threshold];\n
        }\n
        thresholds[threshold] = limit;\n
        return true;\n
    }\n
\n
    function humanize (withSuffix) {\n
        var locale = this.localeData();\n
        var output = duration_humanize__relativeTime(this, !withSuffix, locale);\n
\n
        if (withSuffix) {\n
            output = locale.pastFuture(+this, output);\n
        }\n
\n
        return locale.postformat(output);\n
    }\n
\n
    var iso_string__abs = Math.abs;\n
\n
    function iso_string__toISOString() {\n
        // inspired by https://github.com/dordille/moment-isoduration/blob/master/moment.isoduration.js\n
        var Y = iso_string__abs(this.years());\n
        var M = iso_string__abs(this.months());\n
        var D = iso_string__abs(this.days());\n
        var h = iso_string__abs(this.hours());\n
        var m = iso_string__abs(this.minutes());\n
        var s = iso_string__abs(this.seconds() + this.milliseconds() / 1000);\n
        var total = this.asSeconds();\n
\n
        if (!total) {\n
            // this is the same as C#\'s (Noda) and python (isodate)...\n
            // but not other JS (goog.date)\n
            return \'P0D\';\n
        }\n
\n
        return (total < 0 ? \'-\' : \'\') +\n
            \'P\' +\n
            (Y ? Y + \'Y\' : \'\') +\n
            (M ? M + \'M\' : \'\') +\n
            (D ? D + \'D\' : \'\') +\n
            ((h || m || s) ? \'T\' : \'\') +\n
            (h ? h + \'H\' : \'\') +\n
            (m ? m + \'M\' : \'\') +\n
            (s ? s + \'S\' : \'\');\n
    }\n
\n
    var duration_prototype__proto = Duration.prototype;\n
\n
    duration_prototype__proto.abs            = duration_abs__abs;\n
    duration_prototype__proto.add            = duration_add_subtract__add;\n
    duration_prototype__proto.subtract       = duration_add_subtract__subtract;\n
    duration_prototype__proto.as             = as;\n
    duration_prototype__proto.asMilliseconds = asMilliseconds;\n
    duration_prototype__proto.asSeconds      = asSeconds;\n
    duration_prototype__proto.asMinutes      = asMinutes;\n
    duration_prototype__proto.asHours        = asHours;\n
    duration_prototype__proto.asDays         = asDays;\n
    duration_prototype__proto.asWeeks        = asWeeks;\n
    duration_prototype__proto.asMonths       = asMonths;\n
    duration_prototype__proto.asYears        = asYears;\n
    duration_prototype__proto.valueOf        = duration_as__valueOf;\n
    duration_prototype__proto._bubble        = bubble;\n
    duration_prototype__proto.get            = duration_get__get;\n
    duration_prototype__proto.milliseconds   = duration_get__milliseconds;\n
    duration_prototype__proto.seconds        = seconds;\n
    duration_prototype__proto.minutes        = minutes;\n
    duration_prototype__proto.hours          = hours;\n
    duration_prototype__proto.days           = days;\n
    duration_prototype__proto.weeks          = weeks;\n
    duration_prototype__proto.months         = months;\n
    duration_prototype__proto.years          = years;\n
    duration_prototype__proto.humanize       = humanize;\n
    duration_prototype__proto.toISOString    = iso_string__toISOString;\n
    duration_prototype__proto.toString       = iso_string__toISOString;\n
    duration_prototype__proto.toJSON         = iso_string__toISOString;\n
    duration_prototype__proto.locale         = locale;\n
    duration_prototype__proto.localeData     = localeData;\n
\n
    // Deprecations\n
    duration_prototype__proto.toIsoString = deprecate(\'toIsoString() is deprecated. Please use toISOString() instead (notice the capitals)\', iso_string__toISOString);\n
    duration_prototype__proto.lang = lang;\n
\n
    // Side effect imports\n
\n
    addFormatToken(\'X\', 0, 0, \'unix\');\n
    addFormatToken(\'x\', 0, 0, \'valueOf\');\n
\n
    // PARSING\n
\n
    addRegexToken(\'x\', matchSigned);\n
    addRegexToken(\'X\', matchTimestamp);\n
    addParseToken(\'X\', function (input, array, config) {\n
        config._d = new Date(parseFloat(input, 10) * 1000);\n
    });\n
    addParseToken(\'x\', function (input, array, config) {\n
        config._d = new Date(toInt(input));\n
    });\n
\n
    // Side effect imports\n
\n
\n
    utils_hooks__hooks.version = \'2.10.2\';\n
\n
    setHookCallback(local__createLocal);\n
\n
    utils_hooks__hooks.fn                    = momentPrototype;\n
    utils_hooks__hooks.min                   = min;\n
    utils_hooks__hooks.max                   = max;\n
    utils_hooks__hooks.utc                   = create_utc__createUTC;\n
    utils_hooks__hooks.unix                  = moment__createUnix;\n
    utils_hooks__hooks.months                = lists__listMonths;\n
    utils_hooks__hooks.isDate                = isDate;\n
    utils_hooks__hooks.locale                = locale_locales__getSetGlobalLocale;\n
    utils_hooks__hooks.invalid               = valid__createInvalid;\n
    utils_hooks__hooks.duration              = create__createDuration;\n
    utils_hooks__hooks.isMoment              = isMoment;\n
    utils_hooks__hooks.weekdays              = lists__listWeekdays;\n
    utils_hooks__hooks.parseZone             = moment__createInZone;\n
    utils_hooks__hooks.localeData            = locale_locales__getLocale;\n
    utils_hooks__hooks.isDuration            = isDuration;\n
    utils_hooks__hooks.monthsShort           = lists__listMonthsShort;\n
    utils_hooks__hooks.weekdaysMin           = lists__listWeekdaysMin;\n
    utils_hooks__hooks.defineLocale          = defineLocale;\n
    utils_hooks__hooks.weekdaysShort         = lists__listWeekdaysShort;\n
    utils_hooks__hooks.normalizeUnits        = normalizeUnits;\n
    utils_hooks__hooks.relativeTimeThreshold = duration_humanize__getSetRelativeTimeThreshold;\n
\n
    var _moment = utils_hooks__hooks;\n
\n
    return _moment;\n
\n
}));\n
},{}],"numeral":[function(require,module,exports){\n
"use strict";\n
(function() {\n
  var numeral,\n
      VERSION = \'1.5.3\',\n
      languages = {},\n
      currentLanguage = \'en\',\n
      zeroFormat = null,\n
      defaultFormat = \'0,0\',\n
      hasModule = (typeof module !== \'undefined\' && module.exports);\n
  function Numeral(number) {\n
    this._value = number;\n
  }\n
  function toFixed(value, precision, roundingFunction, optionals) {\n
    var power = Math.pow(10, precision),\n
        optionalsRegExp,\n
        output;\n
    output = (roundingFunction(value * power) / power).toFixed(precision);\n
    if (optionals) {\n
      optionalsRegExp = new RegExp(\'0{1,\' + optionals + \'}$\');\n
      output = output.replace(optionalsRegExp, \'\');\n
    }\n
    return output;\n
  }\n
  function formatNumeral(n, format, roundingFunction) {\n
    var output;\n
    if (format.indexOf(\'$\') > -1) {\n
      output = formatCurrency(n, format, roundingFunction);\n
    } else if (format.indexOf(\'%\') > -1) {\n
      output = formatPercentage(n, format, roundingFunction);\n
    } else if (format.indexOf(\':\') > -1) {\n
      output = formatTime(n, format);\n
    } else {\n
      output = formatNumber(n._value, format, roundingFunction);\n
    }\n
    return output;\n
  }\n
  function unformatNumeral(n, string) {\n
    var stringOriginal = string,\n
        thousandRegExp,\n
        millionRegExp,\n
        billionRegExp,\n
        trillionRegExp,\n
        suffixes = [\'KB\', \'MB\', \'GB\', \'TB\', \'PB\', \'EB\', \'ZB\', \'YB\'],\n
        bytesMultiplier = false,\n
        power;\n
    if (string.indexOf(\':\') > -1) {\n
      n._value = unformatTime(string);\n
    } else {\n
      if (string === zeroFormat) {\n
        n._value = 0;\n
      } else {\n
        if (languages[currentLanguage].delimiters.decimal !== \'.\') {\n
          string = string.replace(/\\./g, \'\').replace(languages[currentLanguage].delimiters.decimal, \'.\');\n
        }\n
        thousandRegExp = new RegExp(\'[^a-zA-Z]\' + languages[currentLanguage].abbreviations.thousand + \'(?:\\\\)|(\\\\\' + languages[currentLanguage].currency.symbol + \')?(?:\\\\))?)?$\');\n
        millionRegExp = new RegExp(\'[^a-zA-Z]\' + languages[currentLanguage].abbreviations.million + \'(?:\\\\)|(\\\\\' + languages[currentLanguage].currency.symbol + \')?(?:\\\\))?)?$\');\n
        billionRegExp = new RegExp(\'[^a-zA-Z]\' + languages[currentLanguage].abbreviations.billion + \'(?:\\\\)|(\\\\\' + languages[currentLanguage].currency.symbol + \')?(?:\\\\))?)?$\');\n
        trillionRegExp = new RegExp(\'[^a-zA-Z]\' + languages[currentLanguage].abbreviations.trillion + \'(?:\\\\)|(\\\\\' + languages[currentLanguage].currency.symbol + \')?(?:\\\\))?)?$\');\n
        for (power = 0; power <= suffixes.length; power++) {\n
          bytesMultiplier = (string.indexOf(suffixes[power]) > -1) ? Math.pow(1024, power + 1) : false;\n
          if (bytesMultiplier) {\n
            break;\n
          }\n
        }\n
        n._value = ((bytesMultiplier) ? bytesMultiplier : 1) * ((stringOriginal.match(thousandRegExp)) ? Math.pow(10, 3) : 1) * ((stringOriginal.match(millionRegExp)) ? Math.pow(10, 6) : 1) * ((stringOriginal.match(billionRegExp)) ? Math.pow(10, 9) : 1) * ((stringOriginal.match(trillionRegExp)) ? Math.pow(10, 12) : 1) * ((string.indexOf(\'%\') > -1) ? 0.01 : 1) * (((string.split(\'-\').length + Math.min(string.split(\'(\').length - 1, string.split(\')\').length - 1)) % 2) ? 1 : -1) * Number(string.replace(/[^0-9\\.]+/g, \'\'));\n
        n._value = (bytesMultiplier) ? Math.ceil(n._value) : n._value;\n
      }\n
    }\n
    return n._value;\n
  }\n
  function formatCurrency(n, format, roundingFunction) {\n
    var symbolIndex = format.indexOf(\'$\'),\n
        openParenIndex = format.indexOf(\'(\'),\n
        minusSignIndex = format.indexOf(\'-\'),\n
        space = \'\',\n
        spliceIndex,\n
        output;\n
    if (format.indexOf(\' $\') > -1) {\n
      space = \' \';\n
      format = format.replace(\' $\', \'\');\n
    } else if (format.indexOf(\'$ \') > -1) {\n
      space = \' \';\n
      format = format.replace(\'$ \', \'\');\n
    } else {\n
      format = format.replace(\'$\', \'\');\n
    }\n
    output = formatNumber(n._value, format, roundingFunction);\n
    if (symbolIndex <= 1) {\n
      if (output.indexOf(\'(\') > -1 || output.indexOf(\'-\') > -1) {\n
        output = output.split(\'\');\n
        spliceIndex = 1;\n
        if (symbolIndex < openParenIndex || symbolIndex < minusSignIndex) {\n
          spliceIndex = 0;\n
        }\n
        output.splice(spliceIndex, 0, languages[currentLanguage].currency.symbol + space);\n
        output = output.join(\'\');\n
      } else {\n
        output = languages[currentLanguage].currency.symbol + space + output;\n
      }\n
    } else {\n
      if (output.indexOf(\')\') > -1) {\n
        output = output.split(\'\');\n
        output.splice(-1, 0, space + languages[currentLanguage].currency.symbol);\n
        output = output.join(\'\');\n
      } else {\n
        output = output + space + languages[currentLanguage].currency.symbol;\n
      }\n
    }\n
    return output;\n
  }\n
  function formatPercentage(n, format, roundingFunction) {\n
    var space = \'\',\n
        output,\n
        value = n._value * 100;\n
    if (format.indexOf(\' %\') > -1) {\n
      space = \' \';\n
      format = format.replace(\' %\', \'\');\n
    } else {\n
      format = format.replace(\'%\', \'\');\n
    }\n
    output = formatNumber(value, format, roundingFunction);\n
    if (output.indexOf(\')\') > -1) {\n
      output = output.split(\'\');\n
      output.splice(-1, 0, space + \'%\');\n
      output = output.join(\'\');\n
    } else {\n
      output = output + space + \'%\';\n
    }\n
    return output;\n
  }\n
  function formatTime(n) {\n
    var hours = Math.floor(n._value / 60 / 60),\n
        minutes = Math.floor((n._value - (hours * 60 * 60)) / 60),\n
        seconds = Math.round(n._value - (hours * 60 * 60) - (minutes * 60));\n
    return hours + \':\' + ((minutes < 10) ? \'0\' + minutes : minutes) + \':\' + ((seconds < 10) ? \'0\' + seconds : seconds);\n
  }\n
  function unformatTime(string) {\n
    var timeArray = string.split(\':\'),\n
        seconds = 0;\n
    if (timeArray.length === 3) {\n
      seconds = seconds + (Number(timeArray[0]) * 60 * 60);\n
      seconds = seconds + (Number(timeArray[1]) * 60);\n
      seconds = seconds + Number(timeArray[2]);\n
    } else if (timeArray.length === 2) {\n
      seconds = seconds + (Number(timeArray[0]) * 60);\n
      seconds = seconds + Number(timeArray[1]);\n
    }\n
    return Number(seconds);\n
  }\n
  function formatNumber(value, format, roundingFunction) {\n
    var negP = false,\n
        signed = false,\n
        optDec = false,\n
        abbr = \'\',\n
        abbrK = false,\n
        abbrM = false,\n
        abbrB = false,\n
        abbrT = false,\n
        abbrForce = false,\n
        bytes = \'\',\n
        ord = \'\',\n
        abs = Math.abs(value),\n
        suffixes = [\'B\', \'KB\', \'MB\', \'GB\', \'TB\', \'PB\', \'EB\', \'ZB\', \'YB\'],\n
        min,\n
        max,\n
        power,\n
        w,\n
        precision,\n
        thousands,\n
        d = \'\',\n
        neg = false;\n
    if (value === 0 && zeroFormat !== null) {\n
      return zeroFormat;\n
    } else {\n
      if (format.indexOf(\'(\') > -1) {\n
        negP = true;\n
        format = format.slice(1, -1);\n
      } else if (format.indexOf(\'+\') > -1) {\n
        signed = true;\n
        format = format.replace(/\\+/g, \'\');\n
      }\n
      if (format.indexOf(\'a\') > -1) {\n
        abbrK = format.indexOf(\'aK\') >= 0;\n
        abbrM = format.indexOf(\'aM\') >= 0;\n
        abbrB = format.indexOf(\'aB\') >= 0;\n
        abbrT = format.indexOf(\'aT\') >= 0;\n
        abbrForce = abbrK || abbrM || abbrB || abbrT;\n
        if (format.indexOf(\' a\') > -1) {\n
          abbr = \' \';\n
          format = format.replace(\' a\', \'\');\n
        } else {\n
          format = format.replace(\'a\', \'\');\n
        }\n
        if (abs >= Math.pow(10, 12) && !abbrForce || abbrT) {\n
          abbr = abbr + languages[currentLanguage].abbreviations.trillion;\n
          value = value / Math.pow(10, 12);\n
        } else if (abs < Math.pow(10, 12) && abs >= Math.pow(10, 9) && !abbrForce || abbrB) {\n
          abbr = abbr + languages[currentLanguage].abbreviations.billion;\n
          value = value / Math.pow(10, 9);\n
        } else if (abs < Math.pow(10, 9) && abs >= Math.pow(10, 6) && !abbrForce || abbrM) {\n
          abbr = abbr + languages[currentLanguage].abbreviations.million;\n
          value = value / Math.pow(10, 6);\n
        } else if (abs < Math.pow(10, 6) && abs >= Math.pow(10, 3) && !abbrForce || abbrK) {\n
          abbr = abbr + languages[currentLanguage].abbreviations.thousand;\n
          value = value / Math.pow(10, 3);\n
        }\n
      }\n
      if (format.indexOf(\'b\') > -1) {\n
        if (format.indexOf(\' b\') > -1) {\n
          bytes = \' \';\n
          format = format.replace(\' b\', \'\');\n
        } else {\n
          format = format.replace(\'b\', \'\');\n
        }\n
        for (power = 0; power <= suffixes.length; power++) {\n
          min = Math.pow(1024, power);\n
          max = Math.pow(1024, power + 1);\n
          if (value >= min && value < max) {\n
            bytes = bytes + suffixes[power];\n
            if (min > 0) {\n
              value = value / min;\n
            }\n
            break;\n
          }\n
        }\n
      }\n
      if (format.indexOf(\'o\') > -1) {\n
        if (format.indexOf(\' o\') > -1) {\n
          ord = \' \';\n
          format = format.replace(\' o\', \'\');\n
        } else {\n
          format = format.replace(\'o\', \'\');\n
        }\n
        ord = ord + languages[currentLanguage].ordinal(value);\n
      }\n
      if (format.indexOf(\'[.]\') > -1) {\n
        optDec = true;\n
        format = format.replace(\'[.]\', \'.\');\n
      }\n
      w = value.toString().split(\'.\')[0];\n
      precision = format.split(\'.\')[1];\n
      thousands = format.indexOf(\',\');\n
      if (precision) {\n
        if (precision.indexOf(\'[\') > -1) {\n
          precision = precision.replace(\']\', \'\');\n
          precision = precision.split(\'[\');\n
          d = toFixed(value, (precision[0].length + precision[1].length), roundingFunction, precision[1].length);\n
        } else {\n
          d = toFixed(value, precision.length, roundingFunction);\n
        }\n
        w = d.split(\'.\')[0];\n
        if (d.split(\'.\')[1].length) {\n
          d = languages[currentLanguage].delimiters.decimal + d.split(\'.\')[1];\n
        } else {\n
          d = \'\';\n
        }\n
        if (optDec && Number(d.slice(1)) === 0) {\n
          d = \'\';\n
        }\n
      } else {\n
        w = toFixed(value, null, roundingFunction);\n
      }\n
      if (w.indexOf(\'-\') > -1) {\n
        w = w.slice(1);\n
        neg = true;\n
      }\n
      if (thousands > -1) {\n
        w = w.toString().replace(/(\\d)(?=(\\d{3})+(?!\\d))/g, \'$1\' + languages[currentLanguage].delimiters.thousands);\n
      }\n
      if (format.indexOf(\'.\') === 0) {\n
        w = \'\';\n
      }\n
      return ((negP && neg) ? \'(\' : \'\') + ((!negP && neg) ? \'-\' : \'\') + ((!neg && signed) ? \'+\' : \'\') + w + d + ((ord) ? ord : \'\') + ((abbr) ? abbr : \'\') + ((bytes) ? bytes : \'\') + ((negP && neg) ? \')\' : \'\');\n
    }\n
  }\n
  numeral = function(input) {\n
    if (numeral.isNumeral(input)) {\n
      input = input.value();\n
    } else if (input === 0 || typeof input === \'undefined\') {\n
      input = 0;\n
    } else if (!Number(input)) {\n
      input = numeral.fn.unformat(input);\n
    }\n
    return new Numeral(Number(input));\n
  };\n
  numeral.version = VERSION;\n
  numeral.isNumeral = function(obj) {\n
    return obj instanceof Numeral;\n
  };\n
  numeral.language = function(key, values) {\n
    if (!key) {\n
      return currentLanguage;\n
    }\n
    if (key && !values) {\n
      if (!languages[key]) {\n
        throw new Error(\'Unknown language : \' + key);\n
      }\n
      currentLanguage = key;\n
    }\n
    if (values || !languages[key]) {\n
      loadLanguage(key, values);\n
    }\n
    return numeral;\n
  };\n
  numeral.languageData = function(key) {\n
    if (!key) {\n
      return languages[currentLanguage];\n
    }\n
    if (!languages[key]) {\n
      throw new Error(\'Unknown language : \' + key);\n
    }\n
    return languages[key];\n
  };\n
  numeral.language(\'en\', {\n
    delimiters: {\n
      thousands: \',\',\n
      decimal: \'.\'\n
    },\n
    abbreviations: {\n
      thousand: \'k\',\n
      million: \'m\',\n
      billion: \'b\',\n
      trillion: \'t\'\n
    },\n
    ordinal: function(number) {\n
      var b = number % 10;\n
      return (~~(number % 100 / 10) === 1) ? \'th\' : (b === 1) ? \'st\' : (b === 2) ? \'nd\' : (b === 3) ? \'rd\' : \'th\';\n
    },\n
    currency: {symbol: \'$\'}\n
  });\n
  numeral.zeroFormat = function(format) {\n
    zeroFormat = typeof(format) === \'string\' ? format : null;\n
  };\n
  numeral.defaultFormat = function(format) {\n
    defaultFormat = typeof(format) === \'string\' ? format : \'0.0\';\n
  };\n
  numeral.validate = function(val, culture) {\n
    var _decimalSep,\n
        _thousandSep,\n
        _currSymbol,\n
        _valArray,\n
        _abbrObj,\n
        _thousandRegEx,\n
        languageData,\n
        temp;\n
    if (typeof val !== \'string\') {\n
      val += \'\';\n
      if (console.warn) {\n
        console.warn(\'Numeral.js: Value is not string. It has been co-erced to: \', val);\n
      }\n
    }\n
    val = val.trim();\n
    if (val === \'\') {\n
      return false;\n
    }\n
    val = val.replace(/^[+-]?/, \'\');\n
    try {\n
      languageData = numeral.languageData(culture);\n
    } catch (e) {\n
      languageData = numeral.languageData(numeral.language());\n
    }\n
    _currSymbol = languageData.currency.symbol;\n
    _abbrObj = languageData.abbreviations;\n
    _decimalSep = languageData.delimiters.decimal;\n
    if (languageData.delimiters.thousands === \'.\') {\n
      _thousandSep = \'\\\\.\';\n
    } else {\n
      _thousandSep = languageData.delimiters.thousands;\n
    }\n
    temp = val.match(/^[^\\d]+/);\n
    if (temp !== null) {\n
      val = val.substr(1);\n
      if (temp[0] !== _currSymbol) {\n
        return false;\n
      }\n
    }\n
    temp = val.match(/[^\\d]+$/);\n
    if (temp !== null) {\n
      val = val.slice(0, -1);\n
      if (temp[0] !== _abbrObj.thousand && temp[0] !== _abbrObj.million && temp[0] !== _abbrObj.billion && temp[0] !== _abbrObj.trillion) {\n
        return false;\n
      }\n
    }\n
    if (!!val.match(/^\\d+$/)) {\n
      return true;\n
    }\n
    _thousandRegEx = new RegExp(_thousandSep + \'{2}\');\n
    if (!val.match(/[^\\d.,]/g)) {\n
      _valArray = val.split(_decimalSep);\n
      if (_valArray.length > 2) {\n
        return false;\n
      } else {\n
        if (_valArray.length < 2) {\n
          return (!!_valArray[0].match(/^\\d+.*\\d$/) && !_valArray[0].match(_thousandRegEx));\n
        } else {\n
          if (_valArray[0].length === 1) {\n
            return (!!_valArray[0].match(/^\\d+$/) && !_valArray[0].match(_thousandRegEx) && !!_valArray[1].match(/^\\d+$/));\n
          } else {\n
            return (!!_valArray[0].match(/^\\d+.*\\d$/) && !_valArray[0].match(_thousandRegEx) && !!_valArray[1].match(/^\\d+$/));\n
          }\n
        }\n
      }\n
    }\n
    return false;\n
  };\n
  function loadLanguage(key, values) {\n
    languages[key] = values;\n
  }\n
  if (\'function\' !== typeof Array.prototype.reduce) {\n
    Array.prototype.reduce = function(callback, opt_initialValue) {\n
      \'use strict\';\n
      if (null === this || \'undefined\' === typeof this) {\n
        throw new TypeError(\'Array.prototype.reduce called on null or undefined\');\n
      }\n
      if (\'function\' !== typeof callback) {\n
        throw new TypeError(callback + \' is not a function\');\n
      }\n
      var index,\n
          value,\n
          length = this.length >>> 0,\n
          isValueSet = false;\n
      if (1 < arguments.length) {\n
        value = opt_initialValue;\n
        isValueSet = true;\n
      }\n
      for (index = 0; length > index; ++index) {\n
        if (this.hasOwnProperty(index)) {\n
          if (isValueSet) {\n
            value = callback(value, this[index], index, this);\n
          } else {\n
            value = this[index];\n
            isValueSet = true;\n
          }\n
        }\n
      }\n
      if (!isValueSet) {\n
        throw new TypeError(\'Reduce of empty array with no initial value\');\n
      }\n
      return value;\n
    };\n
  }\n
  function multiplier(x) {\n
    var parts = x.toString().split(\'.\');\n
    if (parts.length < 2) {\n
      return 1;\n
    }\n
    return Math.pow(10, parts[1].length);\n
  }\n
  function correctionFactor() {\n
    var args = Array.prototype.slice.call(arguments);\n
    return args.reduce(function(prev, next) {\n
      var mp = multiplier(prev),\n
          mn = multiplier(next);\n
      return mp > mn ? mp : mn;\n
    }, -Infinity);\n
  }\n
  numeral.fn = Numeral.prototype = {\n
    clone: function() {\n
      return numeral(this);\n
    },\n
    format: function(inputString, roundingFunction) {\n
      return formatNumeral(this, inputString ? inputString : defaultFormat, (roundingFunction !== undefined) ? roundingFunction : Math.round);\n
    },\n
    unformat: function(inputString) {\n
      if (Object.prototype.toString.call(inputString) === \'[object Number]\') {\n
        return inputString;\n
      }\n
      return unformatNumeral(this, inputString ? inputString : defaultFormat);\n
    },\n
    value: function() {\n
      return this._value;\n
    },\n
    valueOf: function() {\n
      return this._value;\n
    },\n
    set: function(value) {\n
      this._value = Number(value);\n
      return this;\n
    },\n
    add: function(value) {\n
      var corrFactor = correctionFactor.call(null, this._value, value);\n
      function cback(accum, curr, currI, O) {\n
        return accum + corrFactor * curr;\n
      }\n
      this._value = [this._value, value].reduce(cback, 0) / corrFactor;\n
      return this;\n
    },\n
    subtract: function(value) {\n
      var corrFactor = correctionFactor.call(null, this._value, value);\n
      function cback(accum, curr, currI, O) {\n
        return accum - corrFactor * curr;\n
      }\n
      this._value = [value].reduce(cback, this._value * corrFactor) / corrFactor;\n
      return this;\n
    },\n
    multiply: function(value) {\n
      function cback(accum, curr, currI, O) {\n
        var corrFactor = correctionFactor(accum, curr);\n
        return (accum * corrFactor) * (curr * corrFactor) / (corrFactor * corrFactor);\n
      }\n
      this._value = [this._value, value].reduce(cback, 1);\n
      return this;\n
    },\n
    divide: function(value) {\n
      function cback(accum, curr, currI, O) {\n
        var corrFactor = correctionFactor(accum, curr);\n
        return (accum * corrFactor) / (curr * corrFactor);\n
      }\n
      this._value = [this._value, value].reduce(cback);\n
      return this;\n
    },\n
    difference: function(value) {\n
      return Math.abs(numeral(this._value).subtract(value).value());\n
    }\n
  };\n
  if (hasModule) {\n
    module.exports = numeral;\n
  }\n
  if (typeof ender === \'undefined\') {\n
    this[\'numeral\'] = numeral;\n
  }\n
  if (typeof define === \'function\' && define.amd) {\n
    define([], function() {\n
      return numeral;\n
    });\n
  }\n
}).call(window);\n
\n
\n
//# \n
},{}],"pikaday":[function(require,module,exports){\n
/*!\n
 * Pikaday\n
 *\n
 * Copyright Â© 2014 David Bushell | BSD & MIT license | https://github.com/dbushell/Pikaday\n
 */\n
\n
(function (root, factory)\n
{\n
    \'use strict\';\n
\n
    var moment;\n
    if (typeof exports === \'object\') {\n
        // CommonJS module\n
        // Load moment.js as an optional dependency\n
        try { moment = require(\'moment\'); } catch (e) {}\n
        module.exports = factory(moment);\n
    } else if (typeof define === \'function\' && define.amd) {\n
        // AMD. Register as an anonymous module.\n
        define(function (req)\n
        {\n
            // Load moment.js as an optional dependency\n
            var id = \'moment\';\n
            try { moment = req(id); } catch (e) {}\n
            return factory(moment);\n
        });\n
    } else {\n
        root.Pikaday = factory(root.moment);\n
    }\n
}(this, function (moment)\n
{\n
    \'use strict\';\n
\n
    /**\n
     * feature detection and helper functions\n
     */\n
    var hasMoment = typeof moment === \'function\',\n
\n
    hasEventListeners = !!window.addEventListener,\n
\n
    document = window.document,\n
\n
    sto = window.setTimeout,\n
\n
    addEvent = function(el, e, callback, capture)\n
    {\n
        if (hasEventListeners) {\n
            el.addEventListener(e, callback, !!capture);\n
        } else {\n
            el.attachEvent(\'on\' + e, callback);\n
        }\n
    },\n
\n
    removeEvent = function(el, e, callback, capture)\n
    {\n
        if (hasEventListeners) {\n
            el.removeEventListener(e, callback, !!capture);\n
        } else {\n
            el.detachEvent(\'on\' + e, callback);\n
        }\n
    },\n
\n
    fireEvent = function(el, eventName, data)\n
    {\n
        var ev;\n
\n
        if (document.createEvent) {\n
            ev = document.createEvent(\'HTMLEvents\');\n
            ev.initEvent(eventName, true, false);\n
            ev = extend(ev, data);\n
            el.dispatchEvent(ev);\n
        } else if (document.createEventObject) {\n
            ev = document.createEventObject();\n
            ev = extend(ev, data);\n
            el.fireEvent(\'on\' + eventName, ev);\n
        }\n
    },\n
\n
    trim = function(str)\n
    {\n
        return str.trim ? str.trim() : str.replace(/^\\s+|\\s+$/g,\'\');\n
    },\n
\n
    hasClass = function(el, cn)\n
    {\n
        return (\' \' + el.className + \' \').indexOf(\' \' + cn + \' \') !== -1;\n
    },\n
\n
    addClass = function(el, cn)\n
    {\n
        if (!hasClass(el, cn)) {\n
            el.className = (el.className === \'\') ? cn : el.className + \' \' + cn;\n
        }\n
    },\n
\n
    removeClass = function(el, cn)\n
    {\n
        el.className = trim((\' \' + el.className + \' \').replace(\' \' + cn + \' \', \' \'));\n
    },\n
\n
    isArray = function(obj)\n
    {\n
        return (/Array/).test(Object.prototype.toString.call(obj));\n
    },\n
\n
    isDate = function(obj)\n
    {\n
        return (/Date/).test(Object.prototype.toString.call(obj)) && !isNaN(obj.getTime());\n
    },\n
\n
    isWeekend = function(date)\n
    {\n
        var day = date.getDay();\n
        return day === 0 || day === 6;\n
    },\n
\n
    isLeapYear = function(year)\n
    {\n
        // solution by Matti Virkkunen: http://stackoverflow.com/a/4881951\n
        return year % 4 === 0 && year % 100 !== 0 || year % 400 === 0;\n
    },\n
\n
    getDaysInMonth = function(year, month)\n
    {\n
        return [31, isLeapYear(year) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month];\n
    },\n
\n
    setToStartOfDay = function(date)\n
    {\n
        if (isDate(date)) date.setHours(0,0,0,0);\n
    },\n
\n
    compareDates = function(a,b)\n
    {\n
        // weak date comparison (use setToStartOfDay(date) to ensure correct result)\n
        return a.getTime() === b.getTime();\n
    },\n
\n
    extend = function(to, from, overwrite)\n
    {\n
        var prop, hasProp;\n
        for (prop in from) {\n
            hasProp = to[prop] !== undefined;\n
            if (hasProp && typeof from[prop] === \'object\' && from[prop] !== null && from[prop].nodeName === undefined) {\n
                if (isDate(from[prop])) {\n
                    if (overwrite) {\n
                        to[prop] = new Date(from[prop].getTime());\n
                    }\n
                }\n
                else if (isArray(from[prop])) {\n
                    if (overwrite) {\n
                        to[prop] = from[prop].slice(0);\n
                    }\n
                } else {\n
                    to[prop] = extend({}, from[prop], overwrite);\n
                }\n
            } else if (overwrite || !hasProp) {\n
                to[prop] = from[prop];\n
            }\n
        }\n
        return to;\n
    },\n
\n
    adjustCalendar = function(calendar) {\n
        if (calendar.month < 0) {\n
            calendar.year -= Math.ceil(Math.abs(calendar.month)/12);\n
            calendar.month += 12;\n
        }\n
        if (calendar.month > 11) {\n
            calendar.year += Math.floor(Math.abs(calendar.month)/12);\n
            calendar.month -= 12;\n
        }\n
        return calendar;\n
    },\n
\n
    /**\n
     * defaults and localisation\n
     */\n
    defaults = {\n
\n
        // bind the picker to a form field\n
        field: null,\n
\n
        // automatically show/hide the picker on `field` focus (default `true` if `field` is set)\n
        bound: undefined,\n
\n
        // position of the datepicker, relative to the field (default to bottom & left)\n
        // (\'bottom\' & \'left\' keywords are not used, \'top\' & \'right\' are modifier on the bottom/left position)\n
        position: \'bottom left\',\n
\n
        // automatically fit in the viewport even if it means repositioning from the position option\n
        reposition: true,\n
\n
        // the default output format for `.toString()` and `field` value\n
        format: \'YYYY-MM-DD\',\n
\n
        // the initial date to view when first opened\n
        defaultDate: null,\n
\n
        // make the `defaultDate` the initial selected value\n
        setDefaultDate: false,\n
\n
        // first day of week (0: Sunday, 1: Monday etc)\n
        firstDay: 0,\n
\n
        // the minimum/earliest date that can be selected\n
        minDate: null,\n
        // the maximum/latest date that can be selected\n
        maxDate: null,\n
\n
        // number of years either side, or array of upper/lower range\n
        yearRange: 10,\n
\n
        // show week numbers at head of row\n
        showWeekNumber: false,\n
\n
        // used internally (don\'t config outside)\n
        minYear: 0,\n
        maxYear: 9999,\n
        minMonth: undefined,\n
        maxMonth: undefined,\n
\n
        isRTL: false,\n
\n
        // Additional text to append to the year in the calendar title\n
        yearSuffix: \'\',\n
\n
        // Render the month after year in the calendar title\n
        showMonthAfterYear: false,\n
\n
        // how many months are visible\n
        numberOfMonths: 1,\n
\n
        // when numberOfMonths is used, this will help you to choose where the main calendar will be (default `left`, can be set to `right`)\n
        // only used for the first display or when a selected date is not visible\n
        mainCalendar: \'left\',\n
\n
        // Specify a DOM element to render the calendar in\n
        container: undefined,\n
\n
        // internationalization\n
        i18n: {\n
            previousMonth : \'Previous Month\',\n
            nextMonth     : \'Next Month\',\n
            months        : [\'January\',\'February\',\'March\',\'April\',\'May\',\'June\',\'July\',\'August\',\'September\',\'October\',\'November\',\'December\'],\n
            weekdays      : [\'Sunday\',\'Monday\',\'Tuesday\',\'Wednesday\',\'Thursday\',\'Friday\',\'Saturday\'],\n
            weekdaysShort : [\'Sun\',\'Mon\',\'Tue\',\'Wed\',\'Thu\',\'Fri\',\'Sat\']\n
        },\n
\n
        // callback function\n
        onSelect: null,\n
        onOpen: null,\n
        onClose: null,\n
        onDraw: null\n
    },\n
\n
\n
    /**\n
     * templating functions to abstract HTML rendering\n
     */\n
    renderDayName = function(opts, day, abbr)\n
    {\n
        day += opts.firstDay;\n
        while (day >= 7) {\n
            day -= 7;\n
        }\n
        return abbr ? opts.i18n.weekdaysShort[day] : opts.i18n.weekdays[day];\n
    },\n
\n
    renderDay = function(d, m, y, isSelected, isToday, isDisabled, isEmpty)\n
    {\n
        if (isEmpty) {\n
            return \'<td class="is-empty"></td>\';\n
        }\n
        var arr = [];\n
        if (isDisabled) {\n
            arr.push(\'is-disabled\');\n
        }\n
        if (isToday) {\n
            arr.push(\'is-today\');\n
        }\n
        if (isSelected) {\n
            arr.push(\'is-selected\');\n
        }\n
        return \'<td data-day="\' + d + \'" class="\' + arr.join(\' \') + \'">\' +\n
                 \'<button class="pika-button pika-day" type="button" \' +\n
                    \'data-pika-year="\' + y + \'" data-pika-month="\' + m + \'" data-pika-day="\' + d + \'">\' +\n
                        d +\n
                 \'</button>\' +\n
               \'</td>\';\n
    },\n
\n
    renderWeek = function (d, m, y) {\n
        // Lifted from http://javascript.about.com/library/blweekyear.htm, lightly modified.\n
        var onejan = new Date(y, 0, 1),\n
            weekNum = Math.ceil((((new Date(y, m, d) - onejan) / 86400000) + onejan.getDay()+1)/7);\n
        return \'<td class="pika-week">\' + weekNum + \'</td>\';\n
    },\n
\n
    renderRow = function(days, isRTL)\n
    {\n
        return \'<tr>\' + (isRTL ? days.reverse() : days).join(\'\') + \'</tr>\';\n
    },\n
\n
    renderBody = function(rows)\n
    {\n
        return \'<tbody>\' + rows.join(\'\') + \'</tbody>\';\n
    },\n
\n
    renderHead = function(opts)\n
    {\n
        var i, arr = [];\n
        if (opts.showWeekNumber) {\n
            arr.push(\'<th></th>\');\n
        }\n
        for (i = 0; i < 7; i++) {\n
            arr.push(\'<th scope="col"><abbr title="\' + renderDayName(opts, i) + \'">\' + renderDayName(opts, i, true) + \'</abbr></th>\');\n
        }\n
        return \'<thead>\' + (opts.isRTL ? arr.reverse() : arr).join(\'\') + \'</thead>\';\n
    },\n
\n
    renderTitle = function(instance, c, year, month, refYear)\n
    {\n
        var i, j, arr,\n
            opts = instance._o,\n
            isMinYear = year === opts.minYear,\n
            isMaxYear = year === opts.maxYear,\n
            html = \'<div class="pika-title">\',\n
            monthHtml,\n
            yearHtml,\n
            prev = true,\n
            next = true;\n
\n
        for (arr = [], i = 0; i < 12; i++) {\n
            arr.push(\'<option value="\' + (year === refYear ? i - c : 12 + i - c) + \'"\' +\n
                (i === month ? \' selected\': \'\') +\n
                ((isMinYear && i < opts.minMonth) || (isMaxYear && i > opts.maxMonth) ? \'disabled\' : \'\') + \'>\' +\n
                opts.i18n.months[i] + \'</option>\');\n
        }\n
        monthHtml = \'<div class="pika-label">\' + opts.i18n.months[month] + \'<select class="pika-select pika-select-month">\' + arr.join(\'\') + \'</select></div>\';\n
\n
        if (isArray(opts.yearRange)) {\n
            i = opts.yearRange[0];\n
            j = opts.yearRange[1] + 1;\n
        } else {\n
            i = year - opts.yearRange;\n
            j = 1 + year + opts.yearRange;\n
        }\n
\n
        for (arr = []; i < j && i <= opts.maxYear; i++) {\n
            if (i >= opts.minYear) {\n
                arr.push(\'<option value="\' + i + \'"\' + (i === year ? \' selected\': \'\') + \'>\' + (i) + \'</option>\');\n
            }\n
        }\n
        yearHtml = \'<div class="pika-label">\' + year + opts.yearSuffix + \'<select class="pika-select pika-select-year">\' + arr.join(\'\') + \'</select></div>\';\n
\n
        if (opts.showMonthAfterYear) {\n
            html += yearHtml + monthHtml;\n
        } else {\n
            html += monthHtml + yearHtml;\n
        }\n
\n
        if (isMinYear && (month === 0 || opts.minMonth >= month)) {\n
            prev = false;\n
        }\n
\n
        if (isMaxYear && (month === 11 || opts.maxMonth <= month)) {\n
            next = false;\n
        }\n
\n
        if (c === 0) {\n
            html += \'<button class="pika-prev\' + (prev ? \'\' : \' is-disabled\') + \'" type="button">\' + opts.i18n.previousMonth + \'</button>\';\n
        }\n
        if (c === (instance._o.numberOfMonths - 1) ) {\n
            html += \'<button class="pika-next\' + (next ? \'\' : \' is-disabled\') + \'" type="button">\' + opts.i18n.nextMonth + \'</button>\';\n
        }\n
\n
        return html += \'</div>\';\n
    },\n
\n
    renderTable = function(opts, data)\n
    {\n
        return \'<table cellpadding="0" cellspacing="0" class="pika-table">\' + renderHead(opts) + renderBody(data) + \'</table>\';\n
    },\n
\n
\n
    /**\n
     * Pikaday constructor\n
     */\n
    Pikaday = function(options)\n
    {\n
        var self = this,\n
            opts = self.config(options);\n
\n
        self._onMouseDown = function(e)\n
        {\n
            if (!self._v) {\n
                return;\n
            }\n
            e = e || window.event;\n
            var target = e.target || e.srcElement;\n
            if (!target) {\n
                return;\n
            }\n
\n
            if (!hasClass(target, \'is-disabled\')) {\n
                if (hasClass(target, \'pika-button\') && !hasClass(target, \'is-empty\')) {\n
                    self.setDate(new Date(target.getAttribute(\'data-pika-year\'), target.getAttribute(\'data-pika-month\'), target.getAttribute(\'data-pika-day\')));\n
                    if (opts.bound) {\n
                        sto(function() {\n
                            self.hide();\n
                            if (opts.field) {\n
                                opts.field.blur();\n
                            }\n
                        }, 100);\n
                    }\n
                    return;\n
                }\n
                else if (hasClass(target, \'pika-prev\')) {\n
                    self.prevMonth();\n
                }\n
                else if (hasClass(target, \'pika-next\')) {\n
                    self.nextMonth();\n
                }\n
            }\n
            if (!hasClass(target, \'pika-select\')) {\n
                if (e.preventDefault) {\n
                    e.preventDefault();\n
                } else {\n
                    e.returnValue = false;\n
                    return false;\n
                }\n
            } else {\n
                self._c = true;\n
            }\n
        };\n
\n
        self._onChange = function(e)\n
        {\n
            e = e || window.event;\n
            var target = e.target || e.srcElement;\n
            if (!target) {\n
                return;\n
            }\n
            if (hasClass(target, \'pika-select-month\')) {\n
                self.gotoMonth(target.value);\n
            }\n
            else if (hasClass(target, \'pika-select-year\')) {\n
                self.gotoYear(target.value);\n
            }\n
        };\n
\n
        self._onInputChange = function(e)\n
        {\n
            var date;\n
\n
            if (e.firedBy === self) {\n
                return;\n
            }\n
            if (hasMoment) {\n
                date = moment(opts.field.value, opts.format);\n
                date = (date && date.isValid()) ? date.toDate() : null;\n
            }\n
            else {\n
                date = new Date(Date.parse(opts.field.value));\n
            }\n
            self.setDate(isDate(date) ? date : null);\n
            if (!self._v) {\n
                self.show();\n
            }\n
        };\n
\n
        self._onInputFocus = function()\n
        {\n
            self.show();\n
        };\n
\n
        self._onInputClick = function()\n
        {\n
            self.show();\n
        };\n
\n
        self._onInputBlur = function()\n
        {\n
            // IE allows pika div to gain focus; catch blur the input field\n
            var pEl = document.activeElement;\n
            do {\n
                if (hasClass(pEl, \'pika-single\')) {\n
                    return;\n
                }\n
            }\n
            while ((pEl = pEl.parentNode));\n
            \n
            if (!self._c) {\n
                self._b = sto(function() {\n
                    self.hide();\n
                }, 50);\n
            }\n
            self._c = false;\n
        };\n
\n
        self._onClick = function(e)\n
        {\n
            e = e || window.event;\n
            var target = e.target || e.srcElement,\n
                pEl = target;\n
            if (!target) {\n
                return;\n
            }\n
            if (!hasEventListeners && hasClass(target, \'pika-select\')) {\n
                if (!target.onchange) {\n
                    target.setAttribute(\'onchange\', \'return;\');\n
                    addEvent(target, \'change\', self._onChange);\n
                }\n
            }\n
            do {\n
                if (hasClass(pEl, \'pika-single\') || pEl === opts.trigger) {\n
                    return;\n
                }\n
            }\n
            while ((pEl = pEl.parentNode));\n
            if (self._v && target !== opts.trigger && pEl !== opts.trigger) {\n
                self.hide();\n
            }\n
        };\n
\n
        self.el = document.createElement(\'div\');\n
        self.el.className = \'pika-single\' + (opts.isRTL ? \' is-rtl\' : \'\');\n
\n
        addEvent(self.el, \'mousedown\', self._onMouseDown, true);\n
        addEvent(self.el, \'change\', self._onChange);\n
\n
        if (opts.field) {\n
            if (opts.container) {\n
                opts.container.appendChild(self.el);\n
            } else if (opts.bound) {\n
                document.body.appendChild(self.el);\n
            } else {\n
                opts.field.parentNode.insertBefore(self.el, opts.field.nextSibling);\n
            }\n
            addEvent(opts.field, \'change\', self._onInputChange);\n
\n
            if (!opts.defaultDate) {\n
                if (hasMoment && opts.field.value) {\n
                    opts.defaultDate = moment(opts.field.value, opts.format).toDate();\n
                } else {\n
                    opts.defaultDate = new Date(Date.parse(opts.field.value));\n
                }\n
                opts.setDefaultDate = true;\n
            }\n
        }\n
\n
        var defDate = opts.defaultDate;\n
\n
        if (isDate(defDate)) {\n
            if (opts.setDefaultDate) {\n
                self.setDate(defDate, true);\n
            } else {\n
                self.gotoDate(defDate);\n
            }\n
        } else {\n
            self.gotoDate(new Date());\n
        }\n
\n
        if (opts.bound) {\n
            this.hide();\n
            self.el.className += \' is-bound\';\n
            addEvent(opts.trigger, \'click\', self._onInputClick);\n
            addEvent(opts.trigger, \'focus\', self._onInputFocus);\n
            addEvent(opts.trigger, \'blur\', self._onInputBlur);\n
        } else {\n
            this.show();\n
        }\n
    };\n
\n
\n
    /**\n
     * public Pikaday API\n
     */\n
    Pikaday.prototype = {\n
\n
\n
        /**\n
         * configure functionality\n
         */\n
        config: function(options)\n
        {\n
            if (!this._o) {\n
                this._o = extend({}, defaults, true);\n
            }\n
\n
            var opts = extend(this._o, options, true);\n
\n
            opts.isRTL = !!opts.isRTL;\n
\n
            opts.field = (opts.field && opts.field.nodeName) ? opts.field : null;\n
\n
            opts.bound = !!(opts.bound !== undefined ? opts.field && opts.bound : opts.field);\n
\n
            opts.trigger = (opts.trigger && opts.trigger.nodeName) ? opts.trigger : opts.field;\n
\n
            opts.disableWeekends = !!opts.disableWeekends;\n
\n
            opts.disableDayFn = (typeof opts.disableDayFn) == "function" ? opts.disableDayFn : null;\n
\n
            var nom = parseInt(opts.numberOfMonths, 10) || 1;\n
            opts.numberOfMonths = nom > 4 ? 4 : nom;\n
\n
            if (!isDate(opts.minDate)) {\n
                opts.minDate = false;\n
            }\n
            if (!isDate(opts.maxDate)) {\n
                opts.maxDate = false;\n
            }\n
            if ((opts.minDate && opts.maxDate) && opts.maxDate < opts.minDate) {\n
                opts.maxDate = opts.minDate = false;\n
            }\n
            if (opts.minDate) {\n
                setToStartOfDay(opts.minDate);\n
                opts.minYear  = opts.minDate.getFullYear();\n
                opts.minMonth = opts.minDate.getMonth();\n
            }\n
            if (opts.maxDate) {\n
                setToStartOfDay(opts.maxDate);\n
                opts.maxYear  = opts.maxDate.getFullYear();\n
                opts.maxMonth = opts.maxDate.getMonth();\n
            }\n
\n
            if (isArray(opts.yearRange)) {\n
                var fallback = new Date().getFullYear() - 10;\n
                opts.yearRange[0] = parseInt(opts.yearRange[0], 10) || fallback;\n
                opts.yearRange[1] = parseInt(opts.yearRange[1], 10) || fallback;\n
            } else {\n
                opts.yearRange = Math.abs(parseInt(opts.yearRange, 10)) || defaults.yearRange;\n
                if (opts.yearRange > 100) {\n
                    opts.yearRange = 100;\n
                }\n
            }\n
\n
            return opts;\n
        },\n
\n
        /**\n
         * return a formatted string of the current selection (using Moment.js if available)\n
         */\n
        toString: function(format)\n
        {\n
            return !isDate(this._d) ? \'\' : hasMoment ? moment(this._d).format(format || this._o.format) : this._d.toDateString();\n
        },\n
\n
        /**\n
         * return a Moment.js object of the current selection (if available)\n
         */\n
        getMoment: function()\n
        {\n
            return hasMoment ? moment(this._d) : null;\n
        },\n
\n
        /**\n
         * set the current selection from a Moment.js object (if available)\n
         */\n
        setMoment: function(date, preventOnSelect)\n
        {\n
            if (hasMoment && moment.isMoment(date)) {\n
                this.setDate(date.toDate(), preventOnSelect);\n
            }\n
        },\n
\n
        /**\n
         * return a Date object of the current selection\n
         */\n
        getDate: function()\n
        {\n
            return isDate(this._d) ? new Date(this._d.getTime()) : null;\n
        },\n
\n
        /**\n
         * set the current selection\n
         */\n
        setDate: function(date, preventOnSelect)\n
        {\n
            if (!date) {\n
                this._d = null;\n
\n
                if (this._o.field) {\n
                    this._o.field.value = \'\';\n
                    fireEvent(this._o.field, \'change\', { firedBy: this });\n
                }\n
\n
                return this.draw();\n
            }\n
            if (typeof date === \'string\') {\n
                date = new Date(Date.parse(date));\n
            }\n
            if (!isDate(date)) {\n
                return;\n
            }\n
\n
            var min = this._o.minDate,\n
                max = this._o.maxDate;\n
\n
            if (isDate(min) && date < min) {\n
                date = min;\n
            } else if (isDate(max) && date > max) {\n
                date = max;\n
            }\n
\n
            this._d = new Date(date.getTime());\n
            setToStartOfDay(this._d);\n
            this.gotoDate(this._d);\n
\n
            if (this._o.field) {\n
                this._o.field.value = this.toString();\n
                fireEvent(this._o.field, \'change\', { firedBy: this });\n
            }\n
            if (!preventOnSelect && typeof this._o.onSelect === \'function\') {\n
                this._o.onSelect.call(this, this.getDate());\n
            }\n
        },\n
\n
        /**\n
         * change view to a specific date\n
         */\n
        gotoDate: function(date)\n
        {\n
            var newCalendar = true;\n
\n
            if (!isDate(date)) {\n
                return;\n
            }\n
\n
            if (this.calendars) {\n
                var firstVisibleDate = new Date(this.calendars[0].year, this.calendars[0].month, 1),\n
                    lastVisibleDate = new Date(this.calendars[this.calendars.length-1].year, this.calendars[this.calendars.length-1].month, 1),\n
                    visibleDate = date.getTime();\n
                // get the end of the month\n
                lastVisibleDate.setMonth(lastVisibleDate.getMonth()+1);\n
                lastVisibleDate.setDate(lastVisibleDate.getDate()-1);\n
                newCalendar = (visibleDate < firstVisibleDate.getTime() || lastVisibleDate.getTime() < visibleDate);\n
            }\n
\n
            if (newCalendar) {\n
                this.calendars = [{\n
                    month: date.getMonth(),\n
                    year: date.getFullYear()\n
                }];\n
                if (this._o.mainCalendar === \'right\') {\n
                    this.calendars[0].month += 1 - this._o.numberOfMonths;\n
                }\n
            }\n
\n
            this.adjustCalendars();\n
        },\n
\n
        adjustCalendars: function() {\n
            this.calendars[0] = adjustCalendar(this.calendars[0]);\n
            for (var c = 1; c < this._o.numberOfMonths; c++) {\n
                this.calendars[c] = adjustCalendar({\n
                    month: this.calendars[0].month + c,\n
                    year: this.calendars[0].year\n
                });\n
            }\n
            this.draw();\n
        },\n
\n
        gotoToday: function()\n
        {\n
            this.gotoDate(new Date());\n
        },\n
\n
        /**\n
         * change view to a specific month (zero-index, e.g. 0: January)\n
         */\n
        gotoMonth: function(month)\n
        {\n
            if (!isNaN(month)) {\n
                this.calendars[0].month = parseInt(month, 10);\n
                this.adjustCalendars();\n
            }\n
        },\n
\n
        nextMonth: function()\n
        {\n
            this.calendars[0].month++;\n
            this.adjustCalendars();\n
        },\n
\n
        prevMonth: function()\n
        {\n
            this.calendars[0].month--;\n
            this.adjustCalendars();\n
        },\n
\n
        /**\n
         * change view to a specific full year (e.g. "2012")\n
         */\n
        gotoYear: function(year)\n
        {\n
            if (!isNaN(year)) {\n
                this.calendars[0].year = parseInt(year, 10);\n
                this.adjustCalendars();\n
            }\n
        },\n
\n
        /**\n
         * change the minDate\n
         */\n
        setMinDate: function(value)\n
        {\n
            this._o.minDate = value;\n
        },\n
\n
        /**\n
         * change the maxDate\n
         */\n
        setMaxDate: function(value)\n
        {\n
            this._o.maxDate = value;\n
        },\n
\n
        /**\n
         * refresh the HTML\n
         */\n
        draw: function(force)\n
        {\n
            if (!this._v && !force) {\n
                return;\n
            }\n
            var opts = this._o,\n
                minYear = opts.minYear,\n
                maxYear = opts.maxYear,\n
                minMonth = opts.minMonth,\n
                maxMonth = opts.maxMonth,\n
                html = \'\';\n
\n
            if (this._y <= minYear) {\n
                this._y = minYear;\n
                if (!isNaN(minMonth) && this._m < minMonth) {\n
                    this._m = minMonth;\n
                }\n
            }\n
            if (this._y >= maxYear) {\n
                this._y = maxYear;\n
                if (!isNaN(maxMonth) && this._m > maxMonth) {\n
                    this._m = maxMonth;\n
                }\n
            }\n
\n
            for (var c = 0; c < opts.numberOfMonths; c++) {\n
                html += \'<div class="pika-lendar">\' + renderTitle(this, c, this.calendars[c].year, this.calendars[c].month, this.calendars[0].year) + this.render(this.calendars[c].year, this.calendars[c].month) + \'</div>\';\n
            }\n
\n
            this.el.innerHTML = html;\n
\n
            if (opts.bound) {\n
                if(opts.field.type !== \'hidden\') {\n
                    sto(function() {\n
                        opts.trigger.focus();\n
                    }, 1);\n
                }\n
            }\n
\n
            if (typeof this._o.onDraw === \'function\') {\n
                var self = this;\n
                sto(function() {\n
                    self._o.onDraw.call(self);\n
                }, 0);\n
            }\n
        },\n
\n
        adjustPosition: function()\n
        {\n
            if (this._o.container) return;\n
            var field = this._o.trigger, pEl = field,\n
            width = this.el.offsetWidth, height = this.el.offsetHeight,\n
            viewportWidth = window.innerWidth || document.documentElement.clientWidth,\n
            viewportHeight = window.innerHeight || document.documentElement.clientHeight,\n
            scrollTop = window.pageYOffset || document.body.scrollTop || document.documentElement.scrollTop,\n
            left, top, clientRect;\n
\n
            if (typeof field.getBoundingClientRect === \'function\') {\n
                clientRect = field.getBoundingClientRect();\n
                left = clientRect.left + window.pageXOffset;\n
                top = clientRect.bottom + window.pageYOffset;\n
            } else {\n
                left = pEl.offsetLeft;\n
                top  = pEl.offsetTop + pEl.offsetHeight;\n
                while((pEl = pEl.offsetParent)) {\n
                    left += pEl.offsetLeft;\n
                    top  += pEl.offsetTop;\n
                }\n
            }\n
\n
            // default position is bottom & left\n
            if ((this._o.reposition && left + width > viewportWidth) ||\n
                (\n
                    this._o.position.indexOf(\'right\') > -1 &&\n
                    left - width + field.offsetWidth > 0\n
                )\n
            ) {\n
                left = left - width + field.offsetWidth;\n
            }\n
            if ((this._o.reposition && top + height > viewportHeight + scrollTop) ||\n
                (\n
                    this._o.position.indexOf(\'top\') > -1 &&\n
                    top - height - field.offsetHeight > 0\n
                )\n
            ) {\n
                top = top - height - field.offsetHeight;\n
            }\n
\n
            this.el.style.cssText = [\n
                \'position: absolute\',\n
                \'left: \' + left + \'px\',\n
                \'top: \' + top + \'px\'\n
            ].join(\';\');\n
        },\n
\n
        /**\n
         * render HTML for a particular month\n
         */\n
        render: function(year, month)\n
        {\n
            var opts   = this._o,\n
                now    = new Date(),\n
                days   = getDaysInMonth(year, month),\n
                before = new Date(year, month, 1).getDay(),\n
                data   = [],\n
                row    = [];\n
            setToStartOfDay(now);\n
            if (opts.firstDay > 0) {\n
                before -= opts.firstDay;\n
                if (before < 0) {\n
                    before += 7;\n
                }\n
            }\n
            var cells = days + before,\n
                after = cells;\n
            while(after > 7) {\n
                after -= 7;\n
            }\n
            cells += 7 - after;\n
            for (var i = 0, r = 0; i < cells; i++)\n
            {\n
                var day = new Date(year, month, 1 + (i - before)),\n
                    isSelected = isDate(this._d) ? compareDates(day, this._d) : false,\n
                    isToday = compareDates(day, now),\n
                    isEmpty = i < before || i >= (days + before),\n
                    isDisabled = (opts.minDate && day < opts.minDate) ||\n
                                 (opts.maxDate && day > opts.maxDate) ||\n
                                 (opts.disableWeekends && isWeekend(day)) ||\n
                                 (opts.disableDayFn && opts.disableDayFn(day));\n
\n
                row.push(renderDay(1 + (i - before), month, year, isSelected, isToday, isDisabled, isEmpty));\n
\n
                if (++r === 7) {\n
                    if (opts.showWeekNumber) {\n
                        row.unshift(renderWeek(i - before, month, year));\n
                    }\n
                    data.push(renderRow(row, opts.isRTL));\n
                    row = [];\n
                    r = 0;\n
                }\n
            }\n
            return renderTable(opts, data);\n
        },\n
\n
        isVisible: function()\n
        {\n
            return this._v;\n
        },\n
\n
        show: function()\n
        {\n
            if (!this._v) {\n
                removeClass(this.el, \'is-hidden\');\n
                this._v = true;\n
                this.draw();\n
                if (this._o.bound) {\n
                    addEvent(document, \'click\', this._onClick);\n
                    this.adjustPosition();\n
                }\n
                if (typeof this._o.onOpen === \'function\') {\n
                    this._o.onOpen.call(this);\n
                }\n
            }\n
        },\n
\n
        hide: function()\n
        {\n
            var v = this._v;\n
            if (v !== false) {\n
                if (this._o.bound) {\n
                    removeEvent(document, \'click\', this._onClick);\n
                }\n
                this.el.style.cssText = \'\';\n
                addClass(this.el, \'is-hidden\');\n
                this._v = false;\n
                if (v !== undefined && typeof this._o.onClose === \'function\') {\n
                    this._o.onClose.call(this);\n
                }\n
            }\n
        },\n
\n
        /**\n
         * GAME OVER\n
         */\n
        destroy: function()\n
        {\n
            this.hide();\n
            removeEvent(this.el, \'mousedown\', this._onMouseDown, true);\n
            removeEvent(this.el, \'change\', this._onChange);\n
            if (this._o.field) {\n
                removeEvent(this._o.field, \'change\', this._onInputChange);\n
                if (this._o.bound) {\n
                    removeEvent(this._o.trigger, \'click\', this._onInputClick);\n
                    removeEvent(this._o.trigger, \'focus\', this._onInputFocus);\n
                    removeEvent(this._o.trigger, \'blur\', this._onInputBlur);\n
                }\n
            }\n
            if (this.el.parentNode) {\n
                this.el.parentNode.removeChild(this.el);\n
            }\n
        }\n
\n
    };\n
\n
    return Pikaday;\n
\n
}));\n
\n
},{"moment":"moment"}],"zeroclipboard":[function(require,module,exports){\n
/*!\n
 * ZeroClipboard\n
 * The ZeroClipboard library provides an easy way to copy text to the clipboard using an invisible Adobe Flash movie and a JavaScript interface.\n
 * Copyright (c) 2009-2014 Jon Rohan, James M. Greene\n
 * Licensed MIT\n
 * http://zeroclipboard.org/\n
 * v2.2.0\n
 */\n
(function(window, undefined) {\n
  "use strict";\n
  /**\n
 * Store references to critically important global functions that may be\n
 * overridden on certain web pages.\n
 */\n
  var _window = window, _document = _window.document, _navigator = _window.navigator, _setTimeout = _window.setTimeout, _clearTimeout = _window.clearTimeout, _setInterval = _window.setInterval, _clearInterval = _window.clearInterval, _getComputedStyle = _window.getComputedStyle, _encodeURIComponent = _window.encodeURIComponent, _ActiveXObject = _window.ActiveXObject, _Error = _window.Error, _parseInt = _window.Number.parseInt || _window.parseInt, _parseFloat = _window.Number.parseFloat || _window.parseFloat, _isNaN = _window.Number.isNaN || _window.isNaN, _now = _window.Date.now, _keys = _window.Object.keys, _defineProperty = _window.Object.defineProperty, _hasOwn = _window.Object.prototype.hasOwnProperty, _slice = _window.Array.prototype.slice, _unwrap = function() {\n
    var unwrapper = function(el) {\n
      return el;\n
    };\n
    if (typeof _window.wrap === "function" && typeof _window.unwrap === "function") {\n
      try {\n
        var div = _document.createElement("div");\n
        var unwrappedDiv = _window.unwrap(div);\n
        if (div.nodeType === 1 && unwrappedDiv && unwrappedDiv.nodeType === 1) {\n
          unwrapper = _window.unwrap;\n
        }\n
      } catch (e) {}\n
    }\n
    return unwrapper;\n
  }();\n
  /**\n
 * Convert an `arguments` object into an Array.\n
 *\n
 * @returns The arguments as an Array\n
 * @private\n
 */\n
  var _args = function(argumentsObj) {\n
    return _slice.call(argumentsObj, 0);\n
  };\n
  /**\n
 * Shallow-copy the owned, enumerable properties of one object over to another, similar to jQuery\'s `$.extend`.\n
 *\n
 * @returns The target object, augmented\n
 * @private\n
 */\n
  var _extend = function() {\n
    var i, len, arg, prop, src, copy, args = _args(arguments), target = args[0] || {};\n
    for (i = 1, len = args.length; i < len; i++) {\n
      if ((arg = args[i]) != null) {\n
        for (prop in arg) {\n
          if (_hasOwn.call(arg, prop)) {\n
            src = target[prop];\n
            copy = arg[prop];\n
            if (target !== copy && copy !== undefined) {\n
              target[prop] = copy;\n
            }\n
          }\n
        }\n
      }\n
    }\n
    return target;\n
  };\n
  /**\n
 * Return a deep copy of the source object or array.\n
 *\n
 * @returns Object or Array\n
 * @private\n
 */\n
  var _deepCopy = function(source) {\n
    var copy, i, len, prop;\n
    if (typeof source !== "object" || source == null || typeof source.nodeType === "number") {\n
      copy = source;\n
    } else if (typeof source.length === "number") {\n
      copy = [];\n
      for (i = 0, len = source.length; i < len; i++) {\n
        if (_hasOwn.call(source, i)) {\n
          copy[i] = _deepCopy(source[i]);\n
        }\n
      }\n
    } else {\n
      copy = {};\n
      for (prop in source) {\n
        if (_hasOwn.call(source, prop)) {\n
          copy[prop] = _deepCopy(source[prop]);\n
        }\n
      }\n
    }\n
    return copy;\n
  };\n
  /**\n
 * Makes a shallow copy of `obj` (like `_extend`) but filters its properties based on a list of `keys` to keep.\n
 * The inverse of `_omit`, mostly. The big difference is that these properties do NOT need to be enumerable to\n
 * be kept.\n
 *\n
 * @returns A new filtered object.\n
 * @private\n
 */\n
  var _pick = function(obj, keys) {\n
    var newObj = {};\n
    for (var i = 0, len = keys.length; i < len; i++) {\n
      if (keys[i] in obj) {\n
        newObj[keys[i]] = obj[keys[i]];\n
      }\n
    }\n
    return newObj;\n
  };\n
  /**\n
 * Makes a shallow copy of `obj` (like `_extend`) but filters its properties based on a list of `keys` to omit.\n
 * The inverse of `_pick`.\n
 *\n
 * @returns A new filtered object.\n
 * @private\n
 */\n
  var _omit = function(obj, keys) {\n
    var newObj = {};\n
    for (var prop in obj) {\n
      if (keys.indexOf(prop) === -1) {\n
        newObj[prop] = obj[prop];\n
      }\n
    }\n
    return newObj;\n
  };\n
  /**\n
 * Remove all owned, enumerable properties from an object.\n
 *\n
 * @returns The original object without its owned, enumerable properties.\n
 * @private\n
 */\n
  var _deleteOwnProperties = function(obj) {\n
    if (obj) {\n
      for (var prop in obj) {\n
        if (_hasOwn.call(obj, prop)) {\n
          delete obj[prop];\n
        }\n
      }\n
    }\n
    return obj;\n
  };\n
  /**\n
 * Determine if an element is contained within another element.\n
 *\n
 * @returns Boolean\n
 * @private\n
 */\n
  var _containedBy = function(el, ancestorEl) {\n
    if (el && el.nodeType === 1 && el.ownerDocument && ancestorEl && (ancestorEl.nodeType === 1 && ancestorEl.ownerDocument && ancestorEl.ownerDocument === el.ownerDocument || ancestorEl.nodeType === 9 && !ancestorEl.ownerDocument && ancestorEl === el.ownerDocument)) {\n
      do {\n
        if (el === ancestorEl) {\n
          return true;\n
        }\n
        el = el.parentNode;\n
      } while (el);\n
    }\n
    return false;\n
  };\n
  /**\n
 * Get the URL path\'s parent directory.\n
 *\n
 * @returns String or `undefined`\n
 * @private\n
 */\n
  var _getDirPathOfUrl = function(url) {\n
    var dir;\n
    if (typeof url === "string" && url) {\n
      dir = url.split("#")[0].split("?")[0];\n
      dir = url.slice(0, url.lastIndexOf("/") + 1);\n
    }\n
    return dir;\n
  };\n
  /**\n
 * Get the current script\'s URL by throwing an `Error` and analyzing it.\n
 *\n
 * @returns String or `undefined`\n
 * @private\n
 */\n
  var _getCurrentScriptUrlFromErrorStack = function(stack) {\n
    var url, matches;\n
    if (typeof stack === "string" && stack) {\n
      matches = stack.match(/^(?:|[^:@]*@|.+\\)@(?=http[s]?|file)|.+?\\s+(?: at |@)(?:[^:\\(]+ )*[\\(]?)((?:http[s]?|file):\\/\\/[\\/]?.+?\\/[^:\\)]*?)(?::\\d+)(?::\\d+)?/);\n
      if (matches && matches[1]) {\n
        url = matches[1];\n
      } else {\n
        matches = stack.match(/\\)@((?:http[s]?|file):\\/\\/[\\/]?.+?\\/[^:\\)]*?)(?::\\d+)(?::\\d+)?/);\n
        if (matches && matches[1]) {\n
          url = matches[1];\n
        }\n
      }\n
    }\n
    return url;\n
  };\n
  /**\n
 * Get the current script\'s URL by throwing an `Error` and analyzing it.\n
 *\n
 * @returns String or `undefined`\n
 * @private\n
 */\n
  var _getCurrentScriptUrlFromError = function() {\n
    var url, err;\n
    try {\n
      throw new _Error();\n
    } catch (e) {\n
      err = e;\n
    }\n
    if (err) {\n
      url = err.sourceURL || err.fileName || _getCurrentScriptUrlFromErrorStack(err.stack);\n
    }\n
    return url;\n
  };\n
  /**\n
 * Get the current script\'s URL.\n
 *\n
 * @returns String or `undefined`\n
 * @private\n
 */\n
  var _getCurrentScriptUrl = function() {\n
    var jsPath, scripts, i;\n
    if (_document.currentScript && (jsPath = _document.currentScript.src)) {\n
      return jsPath;\n
    }\n
    scripts = _document.getElementsByTagName("script");\n
    if (scripts.length === 1) {\n
      return scripts[0].src || undefined;\n
    }\n
    if ("readyState" in scripts[0]) {\n
      for (i = scripts.length; i--; ) {\n
        if (scripts[i].readyState === "interactive" && (jsPath = scripts[i].src)) {\n
          return jsPath;\n
        }\n
      }\n
    }\n
    if (_document.readyState === "loading" && (jsPath = scripts[scripts.length - 1].src)) {\n
      return jsPath;\n
    }\n
    if (jsPath = _getCurrentScriptUrlFromError()) {\n
      return jsPath;\n
    }\n
    return undefined;\n
  };\n
  /**\n
 * Get the unanimous parent directory of ALL script tags.\n
 * If any script tags are either (a) inline or (b) from differing parent\n
 * directories, this method must return `undefined`.\n
 *\n
 * @returns String or `undefined`\n
 * @private\n
 */\n
  var _getUnanimousScriptParentDir = function() {\n
    var i, jsDir, jsPath, scripts = _document.getElementsByTagName("script");\n
    for (i = scripts.length; i--; ) {\n
      if (!(jsPath = scripts[i].src)) {\n
        jsDir = null;\n
        break;\n
      }\n
      jsPath = _getDirPathOfUrl(jsPath);\n
      if (jsDir == null) {\n
        jsDir = jsPath;\n
      } else if (jsDir !== jsPath) {\n
        jsDir = null;\n
        break;\n
      }\n
    }\n
    return jsDir || undefined;\n
  };\n
  /**\n
 * Get the presumed location of the "ZeroClipboard.swf" file, based on the location\n
 * of the executing JavaScript file (e.g. "ZeroClipboard.js", etc.).\n
 *\n
 * @returns String\n
 * @private\n
 */\n
  var _getDefaultSwfPath = function() {\n
    var jsDir = _getDirPathOfUrl(_getCurrentScriptUrl()) || _getUnanimousScriptParentDir() || "";\n
    return jsDir + "ZeroClipboard.swf";\n
  };\n
  /**\n
 * Keep track of if the page is framed (in an `iframe`). This can never change.\n
 * @private\n
 */\n
  var _pageIsFramed = function() {\n
    return window.opener == null && (!!window.top && window != window.top || !!window.parent && window != window.parent);\n
  }();\n
  /**\n
 * Keep track of the state of the Flash object.\n
 * @private\n
 */\n
  var _flashState = {\n
    bridge: null,\n
    version: "0.0.0",\n
    pluginType: "unknown",\n
    disabled: null,\n
    outdated: null,\n
    sandboxed: null,\n
    unavailable: null,\n
    degraded: null,\n
    deactivated: null,\n
    overdue: null,\n
    ready: null\n
  };\n
  /**\n
 * The minimum Flash Player version required to use ZeroClipboard completely.\n
 * @readonly\n
 * @private\n
 */\n
  var _minimumFlashVersion = "11.0.0";\n
  /**\n
 * The ZeroClipboard library version number, as reported by Flash, at the time the SWF was compiled.\n
 */\n
  var _zcSwfVersion;\n
  /**\n
 * Keep track of all event listener registrations.\n
 * @private\n
 */\n
  var _handlers = {};\n
  /**\n
 * Keep track of the currently activated element.\n
 * @private\n
 */\n
  var _currentElement;\n
  /**\n
 * Keep track of the element that was activated when a `copy` process started.\n
 * @private\n
 */\n
  var _copyTarget;\n
  /**\n
 * Keep track of data for the pending clipboard transaction.\n
 * @private\n
 */\n
  var _clipData = {};\n
  /**\n
 * Keep track of data formats for the pending clipboard transaction.\n
 * @private\n
 */\n
  var _clipDataFormatMap = null;\n
  /**\n
 * Keep track of the Flash availability check timeout.\n
 * @private\n
 */\n
  var _flashCheckTimeout = 0;\n
  /**\n
 * Keep track of SWF network errors interval polling.\n
 * @private\n
 */\n
  var _swfFallbackCheckInterval = 0;\n
  /**\n
 * The `message` store for events\n
 * @private\n
 */\n
  var _eventMessages = {\n
    ready: "Flash communication is established",\n
    error: {\n
      "flash-disabled": "Flash is disabled or not installed. May also be attempting to run Flash in a sandboxed iframe, which is impossible.",\n
      "flash-outdated": "Flash is too outdated to support ZeroClipboard",\n
      "flash-sandboxed": "Attempting to run Flash in a sandboxed iframe, which is impossible",\n
      "flash-unavailable": "Flash is unable to communicate bidirectionally with JavaScript",\n
      "flash-degraded": "Flash is unable to preserve data fidelity when communicating with JavaScript",\n
      "flash-deactivated": "Flash is too outdated for your browser and/or is configured as click-to-activate.\\nThis may also mean that the ZeroClipboard SWF object could not be loaded, so please check your `swfPath` configuration and/or network connectivity.\\nMay also be attempting to run Flash in a sandboxed iframe, which is impossible.",\n
      "flash-overdue": "Flash communication was established but NOT within the acceptable time limit",\n
      "version-mismatch": "ZeroClipboard JS version number does not match ZeroClipboard SWF version number",\n
      "clipboard-error": "At least one error was thrown while ZeroClipboard was attempting to inject your data into the clipboard",\n
      "config-mismatch": "ZeroClipboard configuration does not match Flash\'s reality",\n
      "swf-not-found": "The ZeroClipboard SWF object could not be loaded, so please check your `swfPath` configuration and/or network connectivity"\n
    }\n
  };\n
  /**\n
 * The `name`s of `error` events that can only occur is Flash has at least\n
 * been able to load the SWF successfully.\n
 * @private\n
 */\n
  var _errorsThatOnlyOccurAfterFlashLoads = [ "flash-unavailable", "flash-degraded", "flash-overdue", "version-mismatch", "config-mismatch", "clipboard-error" ];\n
  /**\n
 * The `name`s of `error` events that should likely result in the `_flashState`\n
 * variable\'s property values being updated.\n
 * @private\n
 */\n
  var _flashStateErrorNames = [ "flash-disabled", "flash-outdated", "flash-sandboxed", "flash-unavailable", "flash-degraded", "flash-deactivated", "flash-overdue" ];\n
  /**\n
 * A RegExp to match the `name` property of `error` events related to Flash.\n
 * @private\n
 */\n
  var _flashStateErrorNameMatchingRegex = new RegExp("^flash-(" + _flashStateErrorNames.map(function(errorName) {\n
    return errorName.replace(/^flash-/, "");\n
  }).join("|") + ")$");\n
  /**\n
 * A RegExp to match the `name` property of `error` events related to Flash,\n
 * which is enabled.\n
 * @private\n
 */\n
  var _flashStateEnabledErrorNameMatchingRegex = new RegExp("^flash-(" + _flashStateErrorNames.slice(1).map(function(errorName) {\n
    return errorName.replace(/^flash-/, "");\n
  }).join("|") + ")$");\n
  /**\n
 * ZeroClipboard configuration defaults for the Core module.\n
 * @private\n
 */\n
  var _globalConfig = {\n
    swfPath: _getDefaultSwfPath(),\n
    trustedDomains: window.location.host ? [ window.location.host ] : [],\n
    cacheBust: true,\n
    forceEnhancedClipboard: false,\n
    flashLoadTimeout: 3e4,\n
    autoActivate: true,\n
    bubbleEvents: true,\n
    containerId: "global-zeroclipboard-html-bridge",\n
    containerClass: "global-zeroclipboard-container",\n
    swfObjectId: "global-zeroclipboard-flash-bridge",\n
    hoverClass: "zeroclipboard-is-hover",\n
    activeClass: "zeroclipboard-is-active",\n
    forceHandCursor: false,\n
    title: null,\n
    zIndex: 999999999\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.config`.\n
 * @private\n
 */\n
  var _config = function(options) {\n
    if (typeof options === "object" && options !== null) {\n
      for (var prop in options) {\n
        if (_hasOwn.call(options, prop)) {\n
          if (/^(?:forceHandCursor|title|zIndex|bubbleEvents)$/.test(prop)) {\n
            _globalConfig[prop] = options[prop];\n
          } else if (_flashState.bridge == null) {\n
            if (prop === "containerId" || prop === "swfObjectId") {\n
              if (_isValidHtml4Id(options[prop])) {\n
                _globalConfig[prop] = options[prop];\n
              } else {\n
                throw new Error("The specified `" + prop + "` value is not valid as an HTML4 Element ID");\n
              }\n
            } else {\n
              _globalConfig[prop] = options[prop];\n
            }\n
          }\n
        }\n
      }\n
    }\n
    if (typeof options === "string" && options) {\n
      if (_hasOwn.call(_globalConfig, options)) {\n
        return _globalConfig[options];\n
      }\n
      return;\n
    }\n
    return _deepCopy(_globalConfig);\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.state`.\n
 * @private\n
 */\n
  var _state = function() {\n
    _detectSandbox();\n
    return {\n
      browser: _pick(_navigator, [ "userAgent", "platform", "appName" ]),\n
      flash: _omit(_flashState, [ "bridge" ]),\n
      zeroclipboard: {\n
        version: ZeroClipboard.version,\n
        config: ZeroClipboard.config()\n
      }\n
    };\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.isFlashUnusable`.\n
 * @private\n
 */\n
  var _isFlashUnusable = function() {\n
    return !!(_flashState.disabled || _flashState.outdated || _flashState.sandboxed || _flashState.unavailable || _flashState.degraded || _flashState.deactivated);\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.on`.\n
 * @private\n
 */\n
  var _on = function(eventType, listener) {\n
    var i, len, events, added = {};\n
    if (typeof eventType === "string" && eventType) {\n
      events = eventType.toLowerCase().split(/\\s+/);\n
    } else if (typeof eventType === "object" && eventType && typeof listener === "undefined") {\n
      for (i in eventType) {\n
        if (_hasOwn.call(eventType, i) && typeof i === "string" && i && typeof eventType[i] === "function") {\n
          ZeroClipboard.on(i, eventType[i]);\n
        }\n
      }\n
    }\n
    if (events && events.length) {\n
      for (i = 0, len = events.length; i < len; i++) {\n
        eventType = events[i].replace(/^on/, "");\n
        added[eventType] = true;\n
        if (!_handlers[eventType]) {\n
          _handlers[eventType] = [];\n
        }\n
        _handlers[eventType].push(listener);\n
      }\n
      if (added.ready && _flashState.ready) {\n
        ZeroClipboard.emit({\n
          type: "ready"\n
        });\n
      }\n
      if (added.error) {\n
        for (i = 0, len = _flashStateErrorNames.length; i < len; i++) {\n
          if (_flashState[_flashStateErrorNames[i].replace(/^flash-/, "")] === true) {\n
            ZeroClipboard.emit({\n
              type: "error",\n
              name: _flashStateErrorNames[i]\n
            });\n
            break;\n
          }\n
        }\n
        if (_zcSwfVersion !== undefined && ZeroClipboard.version !== _zcSwfVersion) {\n
          ZeroClipboard.emit({\n
            type: "error",\n
            name: "version-mismatch",\n
            jsVersion: ZeroClipboard.version,\n
            swfVersion: _zcSwfVersion\n
          });\n
        }\n
      }\n
    }\n
    return ZeroClipboard;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.off`.\n
 * @private\n
 */\n
  var _off = function(eventType, listener) {\n
    var i, len, foundIndex, events, perEventHandlers;\n
    if (arguments.length === 0) {\n
      events = _keys(_handlers);\n
    } else if (typeof eventType === "string" && eventType) {\n
      events = eventType.split(/\\s+/);\n
    } else if (typeof eventType === "object" && eventType && typeof listener === "undefined") {\n
      for (i in eventType) {\n
        if (_hasOwn.call(eventType, i) && typeof i === "string" && i && typeof eventType[i] === "function") {\n
          ZeroClipboard.off(i, eventType[i]);\n
        }\n
      }\n
    }\n
    if (events && events.length) {\n
      for (i = 0, len = events.length; i < len; i++) {\n
        eventType = events[i].toLowerCase().replace(/^on/, "");\n
        perEventHandlers = _handlers[eventType];\n
        if (perEventHandlers && perEventHandlers.length) {\n
          if (listener) {\n
            foundIndex = perEventHandlers.indexOf(listener);\n
            while (foundIndex !== -1) {\n
              perEventHandlers.splice(foundIndex, 1);\n
              foundIndex = perEventHandlers.indexOf(listener, foundIndex);\n
            }\n
          } else {\n
            perEventHandlers.length = 0;\n
          }\n
        }\n
      }\n
    }\n
    return ZeroClipboard;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.handlers`.\n
 * @private\n
 */\n
  var _listeners = function(eventType) {\n
    var copy;\n
    if (typeof eventType === "string" && eventType) {\n
      copy = _deepCopy(_handlers[eventType]) || null;\n
    } else {\n
      copy = _deepCopy(_handlers);\n
    }\n
    return copy;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.emit`.\n
 * @private\n
 */\n
  var _emit = function(event) {\n
    var eventCopy, returnVal, tmp;\n
    event = _createEvent(event);\n
    if (!event) {\n
      return;\n
    }\n
    if (_preprocessEvent(event)) {\n
      return;\n
    }\n
    if (event.type === "ready" && _flashState.overdue === true) {\n
      return ZeroClipboard.emit({\n
        type: "error",\n
        name: "flash-overdue"\n
      });\n
    }\n
    eventCopy = _extend({}, event);\n
    _dispatchCallbacks.call(this, eventCopy);\n
    if (event.type === "copy") {\n
      tmp = _mapClipDataToFlash(_clipData);\n
      returnVal = tmp.data;\n
      _clipDataFormatMap = tmp.formatMap;\n
    }\n
    return returnVal;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.create`.\n
 * @private\n
 */\n
  var _create = function() {\n
    var previousState = _flashState.sandboxed;\n
    _detectSandbox();\n
    if (typeof _flashState.ready !== "boolean") {\n
      _flashState.ready = false;\n
    }\n
    if (_flashState.sandboxed !== previousState && _flashState.sandboxed === true) {\n
      _flashState.ready = false;\n
      ZeroClipboard.emit({\n
        type: "error",\n
        name: "flash-sandboxed"\n
      });\n
    } else if (!ZeroClipboard.isFlashUnusable() && _flashState.bridge === null) {\n
      var maxWait = _globalConfig.flashLoadTimeout;\n
      if (typeof maxWait === "number" && maxWait >= 0) {\n
        _flashCheckTimeout = _setTimeout(function() {\n
          if (typeof _flashState.deactivated !== "boolean") {\n
            _flashState.deactivated = true;\n
          }\n
          if (_flashState.deactivated === true) {\n
            ZeroClipboard.emit({\n
              type: "error",\n
              name: "flash-deactivated"\n
            });\n
          }\n
        }, maxWait);\n
      }\n
      _flashState.overdue = false;\n
      _embedSwf();\n
    }\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.destroy`.\n
 * @private\n
 */\n
  var _destroy = function() {\n
    ZeroClipboard.clearData();\n
    ZeroClipboard.blur();\n
    ZeroClipboard.emit("destroy");\n
    _unembedSwf();\n
    ZeroClipboard.off();\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.setData`.\n
 * @private\n
 */\n
  var _setData = function(format, data) {\n
    var dataObj;\n
    if (typeof format === "object" && format && typeof data === "undefined") {\n
      dataObj = format;\n
      ZeroClipboard.clearData();\n
    } else if (typeof format === "string" && format) {\n
      dataObj = {};\n
      dataObj[format] = data;\n
    } else {\n
      return;\n
    }\n
    for (var dataFormat in dataObj) {\n
      if (typeof dataFormat === "string" && dataFormat && _hasOwn.call(dataObj, dataFormat) && typeof dataObj[dataFormat] === "string" && dataObj[dataFormat]) {\n
        _clipData[dataFormat] = dataObj[dataFormat];\n
      }\n
    }\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.clearData`.\n
 * @private\n
 */\n
  var _clearData = function(format) {\n
    if (typeof format === "undefined") {\n
      _deleteOwnProperties(_clipData);\n
      _clipDataFormatMap = null;\n
    } else if (typeof format === "string" && _hasOwn.call(_clipData, format)) {\n
      delete _clipData[format];\n
    }\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.getData`.\n
 * @private\n
 */\n
  var _getData = function(format) {\n
    if (typeof format === "undefined") {\n
      return _deepCopy(_clipData);\n
    } else if (typeof format === "string" && _hasOwn.call(_clipData, format)) {\n
      return _clipData[format];\n
    }\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.focus`/`ZeroClipboard.activate`.\n
 * @private\n
 */\n
  var _focus = function(element) {\n
    if (!(element && element.nodeType === 1)) {\n
      return;\n
    }\n
    if (_currentElement) {\n
      _removeClass(_currentElement, _globalConfig.activeClass);\n
      if (_currentElement !== element) {\n
        _removeClass(_currentElement, _globalConfig.hoverClass);\n
      }\n
    }\n
    _currentElement = element;\n
    _addClass(element, _globalConfig.hoverClass);\n
    var newTitle = element.getAttribute("title") || _globalConfig.title;\n
    if (typeof newTitle === "string" && newTitle) {\n
      var htmlBridge = _getHtmlBridge(_flashState.bridge);\n
      if (htmlBridge) {\n
        htmlBridge.setAttribute("title", newTitle);\n
      }\n
    }\n
    var useHandCursor = _globalConfig.forceHandCursor === true || _getStyle(element, "cursor") === "pointer";\n
    _setHandCursor(useHandCursor);\n
    _reposition();\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.blur`/`ZeroClipboard.deactivate`.\n
 * @private\n
 */\n
  var _blur = function() {\n
    var htmlBridge = _getHtmlBridge(_flashState.bridge);\n
    if (htmlBridge) {\n
      htmlBridge.removeAttribute("title");\n
      htmlBridge.style.left = "0px";\n
      htmlBridge.style.top = "-9999px";\n
      htmlBridge.style.width = "1px";\n
      htmlBridge.style.height = "1px";\n
    }\n
    if (_currentElement) {\n
      _removeClass(_currentElement, _globalConfig.hoverClass);\n
      _removeClass(_currentElement, _globalConfig.activeClass);\n
      _currentElement = null;\n
    }\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.activeElement`.\n
 * @private\n
 */\n
  var _activeElement = function() {\n
    return _currentElement || null;\n
  };\n
  /**\n
 * Check if a value is a valid HTML4 `ID` or `Name` token.\n
 * @private\n
 */\n
  var _isValidHtml4Id = function(id) {\n
    return typeof id === "string" && id && /^[A-Za-z][A-Za-z0-9_:\\-\\.]*$/.test(id);\n
  };\n
  /**\n
 * Create or update an `event` object, based on the `eventType`.\n
 * @private\n
 */\n
  var _createEvent = function(event) {\n
    var eventType;\n
    if (typeof event === "string" && event) {\n
      eventType = event;\n
      event = {};\n
    } else if (typeof event === "object" && event && typeof event.type === "string" && event.type) {\n
      eventType = event.type;\n
    }\n
    if (!eventType) {\n
      return;\n
    }\n
    eventType = eventType.toLowerCase();\n
    if (!event.target && (/^(copy|aftercopy|_click)$/.test(eventType) || eventType === "error" && event.name === "clipboard-error")) {\n
      event.target = _copyTarget;\n
    }\n
    _extend(event, {\n
      type: eventType,\n
      target: event.target || _currentElement || null,\n
      relatedTarget: event.relatedTarget || null,\n
      currentTarget: _flashState && _flashState.bridge || null,\n
      timeStamp: event.timeStamp || _now() || null\n
    });\n
    var msg = _eventMessages[event.type];\n
    if (event.type === "error" && event.name && msg) {\n
      msg = msg[event.name];\n
    }\n
    if (msg) {\n
      event.message = msg;\n
    }\n
    if (event.type === "ready") {\n
      _extend(event, {\n
        target: null,\n
        version: _flashState.version\n
      });\n
    }\n
    if (event.type === "error") {\n
      if (_flashStateErrorNameMatchingRegex.test(event.name)) {\n
        _extend(event, {\n
          target: null,\n
          minimumVersion: _minimumFlashVersion\n
        });\n
      }\n
      if (_flashStateEnabledErrorNameMatchingRegex.test(event.name)) {\n
        _extend(event, {\n
          version: _flashState.version\n
        });\n
      }\n
    }\n
    if (event.type === "copy") {\n
      event.clipboardData = {\n
        setData: ZeroClipboard.setData,\n
        clearData: ZeroClipboard.clearData\n
      };\n
    }\n
    if (event.type === "aftercopy") {\n
      event = _mapClipResultsFromFlash(event, _clipDataFormatMap);\n
    }\n
    if (event.target && !event.relatedTarget) {\n
      event.relatedTarget = _getRelatedTarget(event.target);\n
    }\n
    return _addMouseData(event);\n
  };\n
  /**\n
 * Get a relatedTarget from the target\'s `data-clipboard-target` attribute\n
 * @private\n
 */\n
  var _getRelatedTarget = function(targetEl) {\n
    var relatedTargetId = targetEl && targetEl.getAttribute && targetEl.getAttribute("data-clipboard-target");\n
    return relatedTargetId ? _document.getElementById(relatedTargetId) : null;\n
  };\n
  /**\n
 * Add element and position data to `MouseEvent` instances\n
 * @private\n
 */\n
  var _addMouseData = function(event) {\n
    if (event && /^_(?:click|mouse(?:over|out|down|up|move))$/.test(event.type)) {\n
      var srcElement = event.target;\n
      var fromElement = event.type === "_mouseover" && event.relatedTarget ? event.relatedTarget : undefined;\n
      var toElement = event.type === "_mouseout" && event.relatedTarget ? event.relatedTarget : undefined;\n
      var pos = _getElementPosition(srcElement);\n
      var screenLeft = _window.screenLeft || _window.screenX || 0;\n
      var screenTop = _window.screenTop || _window.screenY || 0;\n
      var scrollLeft = _document.body.scrollLeft + _document.documentElement.scrollLeft;\n
      var scrollTop = _document.body.scrollTop + _document.documentElement.scrollTop;\n
      var pageX = pos.left + (typeof event._stageX === "number" ? event._stageX : 0);\n
      var pageY = pos.top + (typeof event._stageY === "number" ? event._stageY : 0);\n
      var clientX = pageX - scrollLeft;\n
      var clientY = pageY - scrollTop;\n
      var screenX = screenLeft + clientX;\n
      var screenY = screenTop + clientY;\n
      var moveX = typeof event.movementX === "number" ? event.movementX : 0;\n
      var moveY = typeof event.movementY === "number" ? event.movementY : 0;\n
      delete event._stageX;\n
      delete event._stageY;\n
      _extend(event, {\n
        srcElement: srcElement,\n
        fromElement: fromElement,\n
        toElement: toElement,\n
        screenX: screenX,\n
        screenY: screenY,\n
        pageX: pageX,\n
        pageY: pageY,\n
        clientX: clientX,\n
        clientY: clientY,\n
        x: clientX,\n
        y: clientY,\n
        movementX: moveX,\n
        movementY: moveY,\n
        offsetX: 0,\n
        offsetY: 0,\n
        layerX: 0,\n
        layerY: 0\n
      });\n
    }\n
    return event;\n
  };\n
  /**\n
 * Determine if an event\'s registered handlers should be execute synchronously or asynchronously.\n
 *\n
 * @returns {boolean}\n
 * @private\n
 */\n
  var _shouldPerformAsync = function(event) {\n
    var eventType = event && typeof event.type === "string" && event.type || "";\n
    return !/^(?:(?:before)?copy|destroy)$/.test(eventType);\n
  };\n
  /**\n
 * Control if a callback should be executed asynchronously or not.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _dispatchCallback = function(func, context, args, async) {\n
    if (async) {\n
      _setTimeout(function() {\n
        func.apply(context, args);\n
      }, 0);\n
    } else {\n
      func.apply(context, args);\n
    }\n
  };\n
  /**\n
 * Handle the actual dispatching of events to client instances.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _dispatchCallbacks = function(event) {\n
    if (!(typeof event === "object" && event && event.type)) {\n
      return;\n
    }\n
    var async = _shouldPerformAsync(event);\n
    var wildcardTypeHandlers = _handlers["*"] || [];\n
    var specificTypeHandlers = _handlers[event.type] || [];\n
    var handlers = wildcardTypeHandlers.concat(specificTypeHandlers);\n
    if (handlers && handlers.length) {\n
      var i, len, func, context, eventCopy, originalContext = this;\n
      for (i = 0, len = handlers.length; i < len; i++) {\n
        func = handlers[i];\n
        context = originalContext;\n
        if (typeof func === "string" && typeof _window[func] === "function") {\n
          func = _window[func];\n
        }\n
        if (typeof func === "object" && func && typeof func.handleEvent === "function") {\n
          context = func;\n
          func = func.handleEvent;\n
        }\n
        if (typeof func === "function") {\n
          eventCopy = _extend({}, event);\n
          _dispatchCallback(func, context, [ eventCopy ], async);\n
        }\n
      }\n
    }\n
    return this;\n
  };\n
  /**\n
 * Check an `error` event\'s `name` property to see if Flash has\n
 * already loaded, which rules out possible `iframe` sandboxing.\n
 * @private\n
 */\n
  var _getSandboxStatusFromErrorEvent = function(event) {\n
    var isSandboxed = null;\n
    if (_pageIsFramed === false || event && event.type === "error" && event.name && _errorsThatOnlyOccurAfterFlashLoads.indexOf(event.name) !== -1) {\n
      isSandboxed = false;\n
    }\n
    return isSandboxed;\n
  };\n
  /**\n
 * Preprocess any special behaviors, reactions, or state changes after receiving this event.\n
 * Executes only once per event emitted, NOT once per client.\n
 * @private\n
 */\n
  var _preprocessEvent = function(event) {\n
    var element = event.target || _currentElement || null;\n
    var sourceIsSwf = event._source === "swf";\n
    delete event._source;\n
    switch (event.type) {\n
     case "error":\n
      var isSandboxed = event.name === "flash-sandboxed" || _getSandboxStatusFromErrorEvent(event);\n
      if (typeof isSandboxed === "boolean") {\n
        _flashState.sandboxed = isSandboxed;\n
      }\n
      if (_flashStateErrorNames.indexOf(event.name) !== -1) {\n
        _extend(_flashState, {\n
          disabled: event.name === "flash-disabled",\n
          outdated: event.name === "flash-outdated",\n
          unavailable: event.name === "flash-unavailable",\n
          degraded: event.name === "flash-degraded",\n
          deactivated: event.name === "flash-deactivated",\n
          overdue: event.name === "flash-overdue",\n
          ready: false\n
        });\n
      } else if (event.name === "version-mismatch") {\n
        _zcSwfVersion = event.swfVersion;\n
        _extend(_flashState, {\n
          disabled: false,\n
          outdated: false,\n
          unavailable: false,\n
          degraded: false,\n
          deactivated: false,\n
          overdue: false,\n
          ready: false\n
        });\n
      }\n
      _clearTimeoutsAndPolling();\n
      break;\n
\n
     case "ready":\n
      _zcSwfVersion = event.swfVersion;\n
      var wasDeactivated = _flashState.deactivated === true;\n
      _extend(_flashState, {\n
        disabled: false,\n
        outdated: false,\n
        sandboxed: false,\n
        unavailable: false,\n
        degraded: false,\n
        deactivated: false,\n
        overdue: wasDeactivated,\n
        ready: !wasDeactivated\n
      });\n
      _clearTimeoutsAndPolling();\n
      break;\n
\n
     case "beforecopy":\n
      _copyTarget = element;\n
      break;\n
\n
     case "copy":\n
      var textContent, htmlContent, targetEl = event.relatedTarget;\n
      if (!(_clipData["text/html"] || _clipData["text/plain"]) && targetEl && (htmlContent = targetEl.value || targetEl.outerHTML || targetEl.innerHTML) && (textContent = targetEl.value || targetEl.textContent || targetEl.innerText)) {\n
        event.clipboardData.clearData();\n
        event.clipboardData.setData("text/plain", textContent);\n
        if (htmlContent !== textContent) {\n
          event.clipboardData.setData("text/html", htmlContent);\n
        }\n
      } else if (!_clipData["text/plain"] && event.target && (textContent = event.target.getAttribute("data-clipboard-text"))) {\n
        event.clipboardData.clearData();\n
        event.clipboardData.setData("text/plain", textContent);\n
      }\n
      break;\n
\n
     case "aftercopy":\n
      _queueEmitClipboardErrors(event);\n
      ZeroClipboard.clearData();\n
      if (element && element !== _safeActiveElement() && element.focus) {\n
        element.focus();\n
      }\n
      break;\n
\n
     case "_mouseover":\n
      ZeroClipboard.focus(element);\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        if (element && element !== event.relatedTarget && !_containedBy(event.relatedTarget, element)) {\n
          _fireMouseEvent(_extend({}, event, {\n
            type: "mouseenter",\n
            bubbles: false,\n
            cancelable: false\n
          }));\n
        }\n
        _fireMouseEvent(_extend({}, event, {\n
          type: "mouseover"\n
        }));\n
      }\n
      break;\n
\n
     case "_mouseout":\n
      ZeroClipboard.blur();\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        if (element && element !== event.relatedTarget && !_containedBy(event.relatedTarget, element)) {\n
          _fireMouseEvent(_extend({}, event, {\n
            type: "mouseleave",\n
            bubbles: false,\n
            cancelable: false\n
          }));\n
        }\n
        _fireMouseEvent(_extend({}, event, {\n
          type: "mouseout"\n
        }));\n
      }\n
      break;\n
\n
     case "_mousedown":\n
      _addClass(element, _globalConfig.activeClass);\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        _fireMouseEvent(_extend({}, event, {\n
          type: event.type.slice(1)\n
        }));\n
      }\n
      break;\n
\n
     case "_mouseup":\n
      _removeClass(element, _globalConfig.activeClass);\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        _fireMouseEvent(_extend({}, event, {\n
          type: event.type.slice(1)\n
        }));\n
      }\n
      break;\n
\n
     case "_click":\n
      _copyTarget = null;\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        _fireMouseEvent(_extend({}, event, {\n
          type: event.type.slice(1)\n
        }));\n
      }\n
      break;\n
\n
     case "_mousemove":\n
      if (_globalConfig.bubbleEvents === true && sourceIsSwf) {\n
        _fireMouseEvent(_extend({}, event, {\n
          type: event.type.slice(1)\n
        }));\n
      }\n
      break;\n
    }\n
    if (/^_(?:click|mouse(?:over|out|down|up|move))$/.test(event.type)) {\n
      return true;\n
    }\n
  };\n
  /**\n
 * Check an "aftercopy" event for clipboard errors and emit a corresponding "error" event.\n
 * @private\n
 */\n
  var _queueEmitClipboardErrors = function(aftercopyEvent) {\n
    if (aftercopyEvent.errors && aftercopyEvent.errors.length > 0) {\n
      var errorEvent = _deepCopy(aftercopyEvent);\n
      _extend(errorEvent, {\n
        type: "error",\n
        name: "clipboard-error"\n
      });\n
      delete errorEvent.success;\n
      _setTimeout(function() {\n
        ZeroClipboard.emit(errorEvent);\n
      }, 0);\n
    }\n
  };\n
  /**\n
 * Dispatch a synthetic MouseEvent.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _fireMouseEvent = function(event) {\n
    if (!(event && typeof event.type === "string" && event)) {\n
      return;\n
    }\n
    var e, target = event.target || null, doc = target && target.ownerDocument || _document, defaults = {\n
      view: doc.defaultView || _window,\n
      canBubble: true,\n
      cancelable: true,\n
      detail: event.type === "click" ? 1 : 0,\n
      button: typeof event.which === "number" ? event.which - 1 : typeof event.button === "number" ? event.button : doc.createEvent ? 0 : 1\n
    }, args = _extend(defaults, event);\n
    if (!target) {\n
      return;\n
    }\n
    if (doc.createEvent && target.dispatchEvent) {\n
      args = [ args.type, args.canBubble, args.cancelable, args.view, args.detail, args.screenX, args.screenY, args.clientX, args.clientY, args.ctrlKey, args.altKey, args.shiftKey, args.metaKey, args.button, args.relatedTarget ];\n
      e = doc.createEvent("MouseEvents");\n
      if (e.initMouseEvent) {\n
        e.initMouseEvent.apply(e, args);\n
        e._source = "js";\n
        target.dispatchEvent(e);\n
      }\n
    }\n
  };\n
  /**\n
 * Continuously poll the DOM until either:\n
 *  (a) the fallback content becomes visible, or\n
 *  (b) we receive an event from SWF (handled elsewhere)\n
 *\n
 * IMPORTANT:\n
 * This is NOT a necessary check but it can result in significantly faster\n
 * detection of bad `swfPath` configuration and/or network/server issues [in\n
 * supported browsers] than waiting for the entire `flashLoadTimeout` duration\n
 * to elapse before detecting that the SWF cannot be loaded. The detection\n
 * duration can be anywhere from 10-30 times faster [in supported browsers] by\n
 * using this approach.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _watchForSwfFallbackContent = function() {\n
    var maxWait = _globalConfig.flashLoadTimeout;\n
    if (typeof maxWait === "number" && maxWait >= 0) {\n
      var pollWait = Math.min(1e3, maxWait / 10);\n
      var fallbackContentId = _globalConfig.swfObjectId + "_fallbackContent";\n
      _swfFallbackCheckInterval = _setInterval(function() {\n
        var el = _document.getElementById(fallbackContentId);\n
        if (_isElementVisible(el)) {\n
          _clearTimeoutsAndPolling();\n
          _flashState.deactivated = null;\n
          ZeroClipboard.emit({\n
            type: "error",\n
            name: "swf-not-found"\n
          });\n
        }\n
      }, pollWait);\n
    }\n
  };\n
  /**\n
 * Create the HTML bridge element to embed the Flash object into.\n
 * @private\n
 */\n
  var _createHtmlBridge = function() {\n
    var container = _document.createElement("div");\n
    container.id = _globalConfig.containerId;\n
    container.className = _globalConfig.containerClass;\n
    container.style.position = "absolute";\n
    container.style.left = "0px";\n
    container.style.top = "-9999px";\n
    container.style.width = "1px";\n
    container.style.height = "1px";\n
    container.style.zIndex = "" + _getSafeZIndex(_globalConfig.zIndex);\n
    return container;\n
  };\n
  /**\n
 * Get the HTML element container that wraps the Flash bridge object/element.\n
 * @private\n
 */\n
  var _getHtmlBridge = function(flashBridge) {\n
    var htmlBridge = flashBridge && flashBridge.parentNode;\n
    while (htmlBridge && htmlBridge.nodeName === "OBJECT" && htmlBridge.parentNode) {\n
      htmlBridge = htmlBridge.parentNode;\n
    }\n
    return htmlBridge || null;\n
  };\n
  /**\n
 * Create the SWF object.\n
 *\n
 * @returns The SWF object reference.\n
 * @private\n
 */\n
  var _embedSwf = function() {\n
    var len, flashBridge = _flashState.bridge, container = _getHtmlBridge(flashBridge);\n
    if (!flashBridge) {\n
      var allowScriptAccess = _determineScriptAccess(_window.location.host, _globalConfig);\n
      var allowNetworking = allowScriptAccess === "never" ? "none" : "all";\n
      var flashvars = _vars(_extend({\n
        jsVersion: ZeroClipboard.version\n
      }, _globalConfig));\n
      var swfUrl = _globalConfig.swfPath + _cacheBust(_globalConfig.swfPath, _globalConfig);\n
      container = _createHtmlBridge();\n
      var divToBeReplaced = _document.createElement("div");\n
      container.appendChild(divToBeReplaced);\n
      _document.body.appendChild(container);\n
      var tmpDiv = _document.createElement("div");\n
      var usingActiveX = _flashState.pluginType === "activex";\n
      tmpDiv.innerHTML = \'<object id="\' + _globalConfig.swfObjectId + \'" name="\' + _globalConfig.swfObjectId + \'" \' + \'width="100%" height="100%" \' + (usingActiveX ? \'classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000"\' : \'type="application/x-shockwave-flash" data="\' + swfUrl + \'"\') + ">" + (usingActiveX ? \'<param name="movie" value="\' + swfUrl + \'"/>\' : "") + \'<param name="allowScriptAccess" value="\' + allowScriptAccess + \'"/>\' + \'<param name="allowNetworking" value="\' + allowNetworking + \'"/>\' + \'<param name="menu" value="false"/>\' + \'<param name="wmode" value="transparent"/>\' + \'<param name="flashvars" value="\' + flashvars + \'"/>\' + \'<div id="\' + _globalConfig.swfObjectId + \'_fallbackContent">&nbsp;</div>\' + "</object>";\n
      flashBridge = tmpDiv.firstChild;\n
      tmpDiv = null;\n
      _unwrap(flashBridge).ZeroClipboard = ZeroClipboard;\n
      container.replaceChild(flashBridge, divToBeReplaced);\n
      _watchForSwfFallbackContent();\n
    }\n
    if (!flashBridge) {\n
      flashBridge = _document[_globalConfig.swfObjectId];\n
      if (flashBridge && (len = flashBridge.length)) {\n
        flashBridge = flashBridge[len - 1];\n
      }\n
      if (!flashBridge && container) {\n
        flashBridge = container.firstChild;\n
      }\n
    }\n
    _flashState.bridge = flashBridge || null;\n
    return flashBridge;\n
  };\n
  /**\n
 * Destroy the SWF object.\n
 * @private\n
 */\n
  var _unembedSwf = function() {\n
    var flashBridge = _flashState.bridge;\n
    if (flashBridge) {\n
      var htmlBridge = _getHtmlBridge(flashBridge);\n
      if (htmlBridge) {\n
        if (_flashState.pluginType === "activex" && "readyState" in flashBridge) {\n
          flashBridge.style.display = "none";\n
          (function removeSwfFromIE() {\n
            if (flashBridge.readyState === 4) {\n
              for (var prop in flashBridge) {\n
                if (typeof flashBridge[prop] === "function") {\n
                  flashBridge[prop] = null;\n
                }\n
              }\n
              if (flashBridge.parentNode) {\n
                flashBridge.parentNode.removeChild(flashBridge);\n
              }\n
              if (htmlBridge.parentNode) {\n
                htmlBridge.parentNode.removeChild(htmlBridge);\n
              }\n
            } else {\n
              _setTimeout(removeSwfFromIE, 10);\n
            }\n
          })();\n
        } else {\n
          if (flashBridge.parentNode) {\n
            flashBridge.parentNode.removeChild(flashBridge);\n
          }\n
          if (htmlBridge.parentNode) {\n
            htmlBridge.parentNode.removeChild(htmlBridge);\n
          }\n
        }\n
      }\n
      _clearTimeoutsAndPolling();\n
      _flashState.ready = null;\n
      _flashState.bridge = null;\n
      _flashState.deactivated = null;\n
      _zcSwfVersion = undefined;\n
    }\n
  };\n
  /**\n
 * Map the data format names of the "clipData" to Flash-friendly names.\n
 *\n
 * @returns A new transformed object.\n
 * @private\n
 */\n
  var _mapClipDataToFlash = function(clipData) {\n
    var newClipData = {}, formatMap = {};\n
    if (!(typeof clipData === "object" && clipData)) {\n
      return;\n
    }\n
    for (var dataFormat in clipData) {\n
      if (dataFormat && _hasOwn.call(clipData, dataFormat) && typeof clipData[dataFormat] === "string" && clipData[dataFormat]) {\n
        switch (dataFormat.toLowerCase()) {\n
         case "text/plain":\n
         case "text":\n
         case "air:text":\n
         case "flash:text":\n
          newClipData.text = clipData[dataFormat];\n
          formatMap.text = dataFormat;\n
          break;\n
\n
         case "text/html":\n
         case "html":\n
         case "air:html":\n
         case "flash:html":\n
          newClipData.html = clipData[dataFormat];\n
          formatMap.html = dataFormat;\n
          break;\n
\n
         case "application/rtf":\n
         case "text/rtf":\n
         case "rtf":\n
         case "richtext":\n
         case "air:rtf":\n
         case "flash:rtf":\n
          newClipData.rtf = clipData[dataFormat];\n
          formatMap.rtf = dataFormat;\n
          break;\n
\n
         default:\n
          break;\n
        }\n
      }\n
    }\n
    return {\n
      data: newClipData,\n
      formatMap: formatMap\n
    };\n
  };\n
  /**\n
 * Map the data format names from Flash-friendly names back to their original "clipData" names (via a format mapping).\n
 *\n
 * @returns A new transformed object.\n
 * @private\n
 */\n
  var _mapClipResultsFromFlash = function(clipResults, formatMap) {\n
    if (!(typeof clipResults === "object" && clipResults && typeof formatMap === "object" && formatMap)) {\n
      return clipResults;\n
    }\n
    var newResults = {};\n
    for (var prop in clipResults) {\n
      if (_hasOwn.call(clipResults, prop)) {\n
        if (prop === "errors") {\n
          newResults[prop] = clipResults[prop] ? clipResults[prop].slice() : [];\n
          for (var i = 0, len = newResults[prop].length; i < len; i++) {\n
            newResults[prop][i].format = formatMap[newResults[prop][i].format];\n
          }\n
        } else if (prop !== "success" && prop !== "data") {\n
          newResults[prop] = clipResults[prop];\n
        } else {\n
          newResults[prop] = {};\n
          var tmpHash = clipResults[prop];\n
          for (var dataFormat in tmpHash) {\n
            if (dataFormat && _hasOwn.call(tmpHash, dataFormat) && _hasOwn.call(formatMap, dataFormat)) {\n
              newResults[prop][formatMap[dataFormat]] = tmpHash[dataFormat];\n
            }\n
          }\n
        }\n
      }\n
    }\n
    return newResults;\n
  };\n
  /**\n
 * Will look at a path, and will create a "?noCache={time}" or "&noCache={time}"\n
 * query param string to return. Does NOT append that string to the original path.\n
 * This is useful because ExternalInterface often breaks when a Flash SWF is cached.\n
 *\n
 * @returns The `noCache` query param with necessary "?"/"&" prefix.\n
 * @private\n
 */\n
  var _cacheBust = function(path, options) {\n
    var cacheBust = options == null || options && options.cacheBust === true;\n
    if (cacheBust) {\n
      return (path.indexOf("?") === -1 ? "?" : "&") + "noCache=" + _now();\n
    } else {\n
      return "";\n
    }\n
  };\n
  /**\n
 * Creates a query string for the FlashVars param.\n
 * Does NOT include the cache-busting query param.\n
 *\n
 * @returns FlashVars query string\n
 * @private\n
 */\n
  var _vars = function(options) {\n
    var i, len, domain, domains, str = "", trustedOriginsExpanded = [];\n
    if (options.trustedDomains) {\n
      if (typeof options.trustedDomains === "string") {\n
        domains = [ options.trustedDomains ];\n
      } else if (typeof options.trustedDomains === "object" && "length" in options.trustedDomains) {\n
        domains = options.trustedDomains;\n
      }\n
    }\n
    if (domains && domains.length) {\n
      for (i = 0, len = domains.length; i < len; i++) {\n
        if (_hasOwn.call(domains, i) && domains[i] && typeof domains[i] === "string") {\n
          domain = _extractDomain(domains[i]);\n
          if (!domain) {\n
            continue;\n
          }\n
          if (domain === "*") {\n
            trustedOriginsExpanded.length = 0;\n
            trustedOriginsExpanded.push(domain);\n
            break;\n
          }\n
          trustedOriginsExpanded.push.apply(trustedOriginsExpanded, [ domain, "//" + domain, _window.location.protocol + "//" + domain ]);\n
        }\n
      }\n
    }\n
    if (trustedOriginsExpanded.length) {\n
      str += "trustedOrigins=" + _encodeURIComponent(trustedOriginsExpanded.join(","));\n
    }\n
    if (options.forceEnhancedClipboard === true) {\n
      str += (str ? "&" : "") + "forceEnhancedClipboard=true";\n
    }\n
    if (typeof options.swfObjectId === "string" && options.swfObjectId) {\n
      str += (str ? "&" : "") + "swfObjectId=" + _encodeURIComponent(options.swfObjectId);\n
    }\n
    if (typeof options.jsVersion === "string" && options.jsVersion) {\n
      str += (str ? "&" : "") + "jsVersion=" + _encodeURIComponent(options.jsVersion);\n
    }\n
    return str;\n
  };\n
  /**\n
 * Extract the domain (e.g. "github.com") from an origin (e.g. "https://github.com") or\n
 * URL (e.g. "https://github.com/zeroclipboard/zeroclipboard/").\n
 *\n
 * @returns the domain\n
 * @private\n
 */\n
  var _extractDomain = function(originOrUrl) {\n
    if (originOrUrl == null || originOrUrl === "") {\n
      return null;\n
    }\n
    originOrUrl = originOrUrl.replace(/^\\s+|\\s+$/g, "");\n
    if (originOrUrl === "") {\n
      return null;\n
    }\n
    var protocolIndex = originOrUrl.indexOf("//");\n
    originOrUrl = protocolIndex === -1 ? originOrUrl : originOrUrl.slice(protocolIndex + 2);\n
    var pathIndex = originOrUrl.indexOf("/");\n
    originOrUrl = pathIndex === -1 ? originOrUrl : protocolIndex === -1 || pathIndex === 0 ? null : originOrUrl.slice(0, pathIndex);\n
    if (originOrUrl && originOrUrl.slice(-4).toLowerCase() === ".swf") {\n
      return null;\n
    }\n
    return originOrUrl || null;\n
  };\n
  /**\n
 * Set `allowScriptAccess` based on `trustedDomains` and `window.location.host` vs. `swfPath`.\n
 *\n
 * @returns The appropriate script access level.\n
 * @private\n
 */\n
  var _determineScriptAccess = function() {\n
    var _extractAllDomains = function(origins) {\n
      var i, len, tmp, resultsArray = [];\n
      if (typeof origins === "string") {\n
        origins = [ origins ];\n
      }\n
      if (!(typeof origins === "object" && origins && typeof origins.length === "number")) {\n
        return resultsArray;\n
      }\n
      for (i = 0, len = origins.length; i < len; i++) {\n
        if (_hasOwn.call(origins, i) && (tmp = _extractDomain(origins[i]))) {\n
          if (tmp === "*") {\n
            resultsArray.length = 0;\n
            resultsArray.push("*");\n
            break;\n
          }\n
          if (resultsArray.indexOf(tmp) === -1) {\n
            resultsArray.push(tmp);\n
          }\n
        }\n
      }\n
      return resultsArray;\n
    };\n
    return function(currentDomain, configOptions) {\n
      var swfDomain = _extractDomain(configOptions.swfPath);\n
      if (swfDomain === null) {\n
        swfDomain = currentDomain;\n
      }\n
      var trustedDomains = _extractAllDomains(configOptions.trustedDomains);\n
      var len = trustedDomains.length;\n
      if (len > 0) {\n
        if (len === 1 && trustedDomains[0] === "*") {\n
          return "always";\n
        }\n
        if (trustedDomains.indexOf(currentDomain) !== -1) {\n
          if (len === 1 && currentDomain === swfDomain) {\n
            return "sameDomain";\n
          }\n
          return "always";\n
        }\n
      }\n
      return "never";\n
    };\n
  }();\n
  /**\n
 * Get the currently active/focused DOM element.\n
 *\n
 * @returns the currently active/focused element, or `null`\n
 * @private\n
 */\n
  var _safeActiveElement = function() {\n
    try {\n
      return _document.activeElement;\n
    } catch (err) {\n
      return null;\n
    }\n
  };\n
  /**\n
 * Add a class to an element, if it doesn\'t already have it.\n
 *\n
 * @returns The element, with its new class added.\n
 * @private\n
 */\n
  var _addClass = function(element, value) {\n
    var c, cl, className, classNames = [];\n
    if (typeof value === "string" && value) {\n
      classNames = value.split(/\\s+/);\n
    }\n
    if (element && element.nodeType === 1 && classNames.length > 0) {\n
      if (element.classList) {\n
        for (c = 0, cl = classNames.length; c < cl; c++) {\n
          element.classList.add(classNames[c]);\n
        }\n
      } else if (element.hasOwnProperty("className")) {\n
        className = " " + element.className + " ";\n
        for (c = 0, cl = classNames.length; c < cl; c++) {\n
          if (className.indexOf(" " + classNames[c] + " ") === -1) {\n
            className += classNames[c] + " ";\n
          }\n
        }\n
        element.className = className.replace(/^\\s+|\\s+$/g, "");\n
      }\n
    }\n
    return element;\n
  };\n
  /**\n
 * Remove a class from an element, if it has it.\n
 *\n
 * @returns The element, with its class removed.\n
 * @private\n
 */\n
  var _removeClass = function(element, value) {\n
    var c, cl, className, classNames = [];\n
    if (typeof value === "string" && value) {\n
      classNames = value.split(/\\s+/);\n
    }\n
    if (element && element.nodeType === 1 && classNames.length > 0) {\n
      if (element.classList && element.classList.length > 0) {\n
        for (c = 0, cl = classNames.length; c < cl; c++) {\n
          element.classList.remove(classNames[c]);\n
        }\n
      } else if (element.className) {\n
        className = (" " + element.className + " ").replace(/[\\r\\n\\t]/g, " ");\n
        for (c = 0, cl = classNames.length; c < cl; c++) {\n
          className = className.replace(" " + classNames[c] + " ", " ");\n
        }\n
        element.className = className.replace(/^\\s+|\\s+$/g, "");\n
      }\n
    }\n
    return element;\n
  };\n
  /**\n
 * Attempt to interpret the element\'s CSS styling. If `prop` is `"cursor"`,\n
 * then we assume that it should be a hand ("pointer") cursor if the element\n
 * is an anchor element ("a" tag).\n
 *\n
 * @returns The computed style property.\n
 * @private\n
 */\n
  var _getStyle = function(el, prop) {\n
    var value = _getComputedStyle(el, null).getPropertyValue(prop);\n
    if (prop === "cursor") {\n
      if (!value || value === "auto") {\n
        if (el.nodeName === "A") {\n
          return "pointer";\n
        }\n
      }\n
    }\n
    return value;\n
  };\n
  /**\n
 * Get the absolutely positioned coordinates of a DOM element.\n
 *\n
 * @returns Object containing the element\'s position, width, and height.\n
 * @private\n
 */\n
  var _getElementPosition = function(el) {\n
    var pos = {\n
      left: 0,\n
      top: 0,\n
      width: 0,\n
      height: 0\n
    };\n
    if (el.getBoundingClientRect) {\n
      var elRect = el.getBoundingClientRect();\n
      var pageXOffset = _window.pageXOffset;\n
      var pageYOffset = _window.pageYOffset;\n
      var leftBorderWidth = _document.documentElement.clientLeft || 0;\n
      var topBorderWidth = _document.documentElement.clientTop || 0;\n
      var leftBodyOffset = 0;\n
      var topBodyOffset = 0;\n
      if (_getStyle(_document.body, "position") === "relative") {\n
        var bodyRect = _document.body.getBoundingClientRect();\n
        var htmlRect = _document.documentElement.getBoundingClientRect();\n
        leftBodyOffset = bodyRect.left - htmlRect.left || 0;\n
        topBodyOffset = bodyRect.top - htmlRect.top || 0;\n
      }\n
      pos.left = elRect.left + pageXOffset - leftBorderWidth - leftBodyOffset;\n
      pos.top = elRect.top + pageYOffset - topBorderWidth - topBodyOffset;\n
      pos.width = "width" in elRect ? elRect.width : elRect.right - elRect.left;\n
      pos.height = "height" in elRect ? elRect.height : elRect.bottom - elRect.top;\n
    }\n
    return pos;\n
  };\n
  /**\n
 * Determine is an element is visible somewhere within the document (page).\n
 *\n
 * @returns Boolean\n
 * @private\n
 */\n
  var _isElementVisible = function(el) {\n
    if (!el) {\n
      return false;\n
    }\n
    var styles = _getComputedStyle(el, null);\n
    var hasCssHeight = _parseFloat(styles.height) > 0;\n
    var hasCssWidth = _parseFloat(styles.width) > 0;\n
    var hasCssTop = _parseFloat(styles.top) >= 0;\n
    var hasCssLeft = _parseFloat(styles.left) >= 0;\n
    var cssKnows = hasCssHeight && hasCssWidth && hasCssTop && hasCssLeft;\n
    var rect = cssKnows ? null : _getElementPosition(el);\n
    var isVisible = styles.display !== "none" && styles.visibility !== "collapse" && (cssKnows || !!rect && (hasCssHeight || rect.height > 0) && (hasCssWidth || rect.width > 0) && (hasCssTop || rect.top >= 0) && (hasCssLeft || rect.left >= 0));\n
    return isVisible;\n
  };\n
  /**\n
 * Clear all existing timeouts and interval polling delegates.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _clearTimeoutsAndPolling = function() {\n
    _clearTimeout(_flashCheckTimeout);\n
    _flashCheckTimeout = 0;\n
    _clearInterval(_swfFallbackCheckInterval);\n
    _swfFallbackCheckInterval = 0;\n
  };\n
  /**\n
 * Reposition the Flash object to cover the currently activated element.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _reposition = function() {\n
    var htmlBridge;\n
    if (_currentElement && (htmlBridge = _getHtmlBridge(_flashState.bridge))) {\n
      var pos = _getElementPosition(_currentElement);\n
      _extend(htmlBridge.style, {\n
        width: pos.width + "px",\n
        height: pos.height + "px",\n
        top: pos.top + "px",\n
        left: pos.left + "px",\n
        zIndex: "" + _getSafeZIndex(_globalConfig.zIndex)\n
      });\n
    }\n
  };\n
  /**\n
 * Sends a signal to the Flash object to display the hand cursor if `true`.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _setHandCursor = function(enabled) {\n
    if (_flashState.ready === true) {\n
      if (_flashState.bridge && typeof _flashState.bridge.setHandCursor === "function") {\n
        _flashState.bridge.setHandCursor(enabled);\n
      } else {\n
        _flashState.ready = false;\n
      }\n
    }\n
  };\n
  /**\n
 * Get a safe value for `zIndex`\n
 *\n
 * @returns an integer, or "auto"\n
 * @private\n
 */\n
  var _getSafeZIndex = function(val) {\n
    if (/^(?:auto|inherit)$/.test(val)) {\n
      return val;\n
    }\n
    var zIndex;\n
    if (typeof val === "number" && !_isNaN(val)) {\n
      zIndex = val;\n
    } else if (typeof val === "string") {\n
      zIndex = _getSafeZIndex(_parseInt(val, 10));\n
    }\n
    return typeof zIndex === "number" ? zIndex : "auto";\n
  };\n
  /**\n
 * Attempt to detect if ZeroClipboard is executing inside of a sandboxed iframe.\n
 * If it is, Flash Player cannot be used, so ZeroClipboard is dead in the water.\n
 *\n
 * @see {@link http://lists.w3.org/Archives/Public/public-whatwg-archive/2014Dec/0002.html}\n
 * @see {@link https://github.com/zeroclipboard/zeroclipboard/issues/511}\n
 * @see {@link http://zeroclipboard.org/test-iframes.html}\n
 *\n
 * @returns `true` (is sandboxed), `false` (is not sandboxed), or `null` (uncertain) \n
 * @private\n
 */\n
  var _detectSandbox = function(doNotReassessFlashSupport) {\n
    var effectiveScriptOrigin, frame, frameError, previousState = _flashState.sandboxed, isSandboxed = null;\n
    doNotReassessFlashSupport = doNotReassessFlashSupport === true;\n
    if (_pageIsFramed === false) {\n
      isSandboxed = false;\n
    } else {\n
      try {\n
        frame = window.frameElement || null;\n
      } catch (e) {\n
        frameError = {\n
          name: e.name,\n
          message: e.message\n
        };\n
      }\n
      if (frame && frame.nodeType === 1 && frame.nodeName === "IFRAME") {\n
        try {\n
          isSandboxed = frame.hasAttribute("sandbox");\n
        } catch (e) {\n
          isSandboxed = null;\n
        }\n
      } else {\n
        try {\n
          effectiveScriptOrigin = document.domain || null;\n
        } catch (e) {\n
          effectiveScriptOrigin = null;\n
        }\n
        if (effectiveScriptOrigin === null || frameError && frameError.name === "SecurityError" && /(^|[\\s\\(\\[@])sandbox(es|ed|ing|[\\s\\.,!\\)\\]@]|$)/.test(frameError.message.toLowerCase())) {\n
          isSandboxed = true;\n
        }\n
      }\n
    }\n
    _flashState.sandboxed = isSandboxed;\n
    if (previousState !== isSandboxed && !doNotReassessFlashSupport) {\n
      _detectFlashSupport(_ActiveXObject);\n
    }\n
    return isSandboxed;\n
  };\n
  /**\n
 * Detect the Flash Player status, version, and plugin type.\n
 *\n
 * @see {@link https://code.google.com/p/doctype-mirror/wiki/ArticleDetectFlash#The_code}\n
 * @see {@link http://stackoverflow.com/questions/12866060/detecting-pepper-ppapi-flash-with-javascript}\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _detectFlashSupport = function(ActiveXObject) {\n
    var plugin, ax, mimeType, hasFlash = false, isActiveX = false, isPPAPI = false, flashVersion = "";\n
    /**\n
   * Derived from Apple\'s suggested sniffer.\n
   * @param {String} desc e.g. "Shockwave Flash 7.0 r61"\n
   * @returns {String} "7.0.61"\n
   * @private\n
   */\n
    function parseFlashVersion(desc) {\n
      var matches = desc.match(/[\\d]+/g);\n
      matches.length = 3;\n
      return matches.join(".");\n
    }\n
    function isPepperFlash(flashPlayerFileName) {\n
      return !!flashPlayerFileName && (flashPlayerFileName = flashPlayerFileName.toLowerCase()) && (/^(pepflashplayer\\.dll|libpepflashplayer\\.so|pepperflashplayer\\.plugin)$/.test(flashPlayerFileName) || flashPlayerFileName.slice(-13) === "chrome.plugin");\n
    }\n
    function inspectPlugin(plugin) {\n
      if (plugin) {\n
        hasFlash = true;\n
        if (plugin.version) {\n
          flashVersion = parseFlashVersion(plugin.version);\n
        }\n
        if (!flashVersion && plugin.description) {\n
          flashVersion = parseFlashVersion(plugin.description);\n
        }\n
        if (plugin.filename) {\n
          isPPAPI = isPepperFlash(plugin.filename);\n
        }\n
      }\n
    }\n
    if (_navigator.plugins && _navigator.plugins.length) {\n
      plugin = _navigator.plugins["Shockwave Flash"];\n
      inspectPlugin(plugin);\n
      if (_navigator.plugins["Shockwave Flash 2.0"]) {\n
        hasFlash = true;\n
        flashVersion = "2.0.0.11";\n
      }\n
    } else if (_navigator.mimeTypes && _navigator.mimeTypes.length) {\n
      mimeType = _navigator.mimeTypes["application/x-shockwave-flash"];\n
      plugin = mimeType && mimeType.enabledPlugin;\n
      inspectPlugin(plugin);\n
    } else if (typeof ActiveXObject !== "undefined") {\n
      isActiveX = true;\n
      try {\n
        ax = new ActiveXObject("ShockwaveFlash.ShockwaveFlash.7");\n
        hasFlash = true;\n
        flashVersion = parseFlashVersion(ax.GetVariable("$version"));\n
      } catch (e1) {\n
        try {\n
          ax = new ActiveXObject("ShockwaveFlash.ShockwaveFlash.6");\n
          hasFlash = true;\n
          flashVersion = "6.0.21";\n
        } catch (e2) {\n
          try {\n
            ax = new ActiveXObject("ShockwaveFlash.ShockwaveFlash");\n
            hasFlash = true;\n
            flashVersion = parseFlashVersion(ax.GetVariable("$version"));\n
          } catch (e3) {\n
            isActiveX = false;\n
          }\n
        }\n
      }\n
    }\n
    _flashState.disabled = hasFlash !== true;\n
    _flashState.outdated = flashVersion && _parseFloat(flashVersion) < _parseFloat(_minimumFlashVersion);\n
    _flashState.version = flashVersion || "0.0.0";\n
    _flashState.pluginType = isPPAPI ? "pepper" : isActiveX ? "activex" : hasFlash ? "netscape" : "unknown";\n
  };\n
  /**\n
 * Invoke the Flash detection algorithms immediately upon inclusion so we\'re not waiting later.\n
 */\n
  _detectFlashSupport(_ActiveXObject);\n
  /**\n
 * Always assess the `sandboxed` state of the page at important Flash-related moments.\n
 */\n
  _detectSandbox(true);\n
  /**\n
 * A shell constructor for `ZeroClipboard` client instances.\n
 *\n
 * @constructor\n
 */\n
  var ZeroClipboard = function() {\n
    if (!(this instanceof ZeroClipboard)) {\n
      return new ZeroClipboard();\n
    }\n
    if (typeof ZeroClipboard._createClient === "function") {\n
      ZeroClipboard._createClient.apply(this, _args(arguments));\n
    }\n
  };\n
  /**\n
 * The ZeroClipboard library\'s version number.\n
 *\n
 * @static\n
 * @readonly\n
 * @property {string}\n
 */\n
  _defineProperty(ZeroClipboard, "version", {\n
    value: "2.2.0",\n
    writable: false,\n
    configurable: true,\n
    enumerable: true\n
  });\n
  /**\n
 * Update or get a copy of the ZeroClipboard global configuration.\n
 * Returns a copy of the current/updated configuration.\n
 *\n
 * @returns Object\n
 * @static\n
 */\n
  ZeroClipboard.config = function() {\n
    return _config.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Diagnostic method that describes the state of the browser, Flash Player, and ZeroClipboard.\n
 *\n
 * @returns Object\n
 * @static\n
 */\n
  ZeroClipboard.state = function() {\n
    return _state.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Check if Flash is unusable for any reason: disabled, outdated, deactivated, etc.\n
 *\n
 * @returns Boolean\n
 * @static\n
 */\n
  ZeroClipboard.isFlashUnusable = function() {\n
    return _isFlashUnusable.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Register an event listener.\n
 *\n
 * @returns `ZeroClipboard`\n
 * @static\n
 */\n
  ZeroClipboard.on = function() {\n
    return _on.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Unregister an event listener.\n
 * If no `listener` function/object is provided, it will unregister all listeners for the provided `eventType`.\n
 * If no `eventType` is provided, it will unregister all listeners for every event type.\n
 *\n
 * @returns `ZeroClipboard`\n
 * @static\n
 */\n
  ZeroClipboard.off = function() {\n
    return _off.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Retrieve event listeners for an `eventType`.\n
 * If no `eventType` is provided, it will retrieve all listeners for every event type.\n
 *\n
 * @returns array of listeners for the `eventType`; if no `eventType`, then a map/hash object of listeners for all event types; or `null`\n
 */\n
  ZeroClipboard.handlers = function() {\n
    return _listeners.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Event emission receiver from the Flash object, forwarding to any registered JavaScript event listeners.\n
 *\n
 * @returns For the "copy" event, returns the Flash-friendly "clipData" object; otherwise `undefined`.\n
 * @static\n
 */\n
  ZeroClipboard.emit = function() {\n
    return _emit.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Create and embed the Flash object.\n
 *\n
 * @returns The Flash object\n
 * @static\n
 */\n
  ZeroClipboard.create = function() {\n
    return _create.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Self-destruct and clean up everything, including the embedded Flash object.\n
 *\n
 * @returns `undefined`\n
 * @static\n
 */\n
  ZeroClipboard.destroy = function() {\n
    return _destroy.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Set the pending data for clipboard injection.\n
 *\n
 * @returns `undefined`\n
 * @static\n
 */\n
  ZeroClipboard.setData = function() {\n
    return _setData.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Clear the pending data for clipboard injection.\n
 * If no `format` is provided, all pending data formats will be cleared.\n
 *\n
 * @returns `undefined`\n
 * @static\n
 */\n
  ZeroClipboard.clearData = function() {\n
    return _clearData.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Get a copy of the pending data for clipboard injection.\n
 * If no `format` is provided, a copy of ALL pending data formats will be returned.\n
 *\n
 * @returns `String` or `Object`\n
 * @static\n
 */\n
  ZeroClipboard.getData = function() {\n
    return _getData.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Sets the current HTML object that the Flash object should overlay. This will put the global\n
 * Flash object on top of the current element; depending on the setup, this may also set the\n
 * pending clipboard text data as well as the Flash object\'s wrapping element\'s title attribute\n
 * based on the underlying HTML element and ZeroClipboard configuration.\n
 *\n
 * @returns `undefined`\n
 * @static\n
 */\n
  ZeroClipboard.focus = ZeroClipboard.activate = function() {\n
    return _focus.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Un-overlays the Flash object. This will put the global Flash object off-screen; depending on\n
 * the setup, this may also unset the Flash object\'s wrapping element\'s title attribute based on\n
 * the underlying HTML element and ZeroClipboard configuration.\n
 *\n
 * @returns `undefined`\n
 * @static\n
 */\n
  ZeroClipboard.blur = ZeroClipboard.deactivate = function() {\n
    return _blur.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Returns the currently focused/"activated" HTML element that the Flash object is wrapping.\n
 *\n
 * @returns `HTMLElement` or `null`\n
 * @static\n
 */\n
  ZeroClipboard.activeElement = function() {\n
    return _activeElement.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Keep track of the ZeroClipboard client instance counter.\n
 */\n
  var _clientIdCounter = 0;\n
  /**\n
 * Keep track of the state of the client instances.\n
 *\n
 * Entry structure:\n
 *   _clientMeta[client.id] = {\n
 *     instance: client,\n
 *     elements: [],\n
 *     handlers: {}\n
 *   };\n
 */\n
  var _clientMeta = {};\n
  /**\n
 * Keep track of the ZeroClipboard clipped elements counter.\n
 */\n
  var _elementIdCounter = 0;\n
  /**\n
 * Keep track of the state of the clipped element relationships to clients.\n
 *\n
 * Entry structure:\n
 *   _elementMeta[element.zcClippingId] = [client1.id, client2.id];\n
 */\n
  var _elementMeta = {};\n
  /**\n
 * Keep track of the state of the mouse event handlers for clipped elements.\n
 *\n
 * Entry structure:\n
 *   _mouseHandlers[element.zcClippingId] = {\n
 *     mouseover:  function(event) {},\n
 *     mouseout:   function(event) {},\n
 *     mouseenter: function(event) {},\n
 *     mouseleave: function(event) {},\n
 *     mousemove:  function(event) {}\n
 *   };\n
 */\n
  var _mouseHandlers = {};\n
  /**\n
 * Extending the ZeroClipboard configuration defaults for the Client module.\n
 */\n
  _extend(_globalConfig, {\n
    autoActivate: true\n
  });\n
  /**\n
 * The real constructor for `ZeroClipboard` client instances.\n
 * @private\n
 */\n
  var _clientConstructor = function(elements) {\n
    var client = this;\n
    client.id = "" + _clientIdCounter++;\n
    _clientMeta[client.id] = {\n
      instance: client,\n
      elements: [],\n
      handlers: {}\n
    };\n
    if (elements) {\n
      client.clip(elements);\n
    }\n
    ZeroClipboard.on("*", function(event) {\n
      return client.emit(event);\n
    });\n
    ZeroClipboard.on("destroy", function() {\n
      client.destroy();\n
    });\n
    ZeroClipboard.create();\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.on`.\n
 * @private\n
 */\n
  var _clientOn = function(eventType, listener) {\n
    var i, len, events, added = {}, meta = _clientMeta[this.id], handlers = meta && meta.handlers;\n
    if (!meta) {\n
      throw new Error("Attempted to add new listener(s) to a destroyed ZeroClipboard client instance");\n
    }\n
    if (typeof eventType === "string" && eventType) {\n
      events = eventType.toLowerCase().split(/\\s+/);\n
    } else if (typeof eventType === "object" && eventType && typeof listener === "undefined") {\n
      for (i in eventType) {\n
        if (_hasOwn.call(eventType, i) && typeof i === "string" && i && typeof eventType[i] === "function") {\n
          this.on(i, eventType[i]);\n
        }\n
      }\n
    }\n
    if (events && events.length) {\n
      for (i = 0, len = events.length; i < len; i++) {\n
        eventType = events[i].replace(/^on/, "");\n
        added[eventType] = true;\n
        if (!handlers[eventType]) {\n
          handlers[eventType] = [];\n
        }\n
        handlers[eventType].push(listener);\n
      }\n
      if (added.ready && _flashState.ready) {\n
        this.emit({\n
          type: "ready",\n
          client: this\n
        });\n
      }\n
      if (added.error) {\n
        for (i = 0, len = _flashStateErrorNames.length; i < len; i++) {\n
          if (_flashState[_flashStateErrorNames[i].replace(/^flash-/, "")]) {\n
            this.emit({\n
              type: "error",\n
              name: _flashStateErrorNames[i],\n
              client: this\n
            });\n
            break;\n
          }\n
        }\n
        if (_zcSwfVersion !== undefined && ZeroClipboard.version !== _zcSwfVersion) {\n
          this.emit({\n
            type: "error",\n
            name: "version-mismatch",\n
            jsVersion: ZeroClipboard.version,\n
            swfVersion: _zcSwfVersion\n
          });\n
        }\n
      }\n
    }\n
    return this;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.off`.\n
 * @private\n
 */\n
  var _clientOff = function(eventType, listener) {\n
    var i, len, foundIndex, events, perEventHandlers, meta = _clientMeta[this.id], handlers = meta && meta.handlers;\n
    if (!handlers) {\n
      return this;\n
    }\n
    if (arguments.length === 0) {\n
      events = _keys(handlers);\n
    } else if (typeof eventType === "string" && eventType) {\n
      events = eventType.split(/\\s+/);\n
    } else if (typeof eventType === "object" && eventType && typeof listener === "undefined") {\n
      for (i in eventType) {\n
        if (_hasOwn.call(eventType, i) && typeof i === "string" && i && typeof eventType[i] === "function") {\n
          this.off(i, eventType[i]);\n
        }\n
      }\n
    }\n
    if (events && events.length) {\n
      for (i = 0, len = events.length; i < len; i++) {\n
        eventType = events[i].toLowerCase().replace(/^on/, "");\n
        perEventHandlers = handlers[eventType];\n
        if (perEventHandlers && perEventHandlers.length) {\n
          if (listener) {\n
            foundIndex = perEventHandlers.indexOf(listener);\n
            while (foundIndex !== -1) {\n
              perEventHandlers.splice(foundIndex, 1);\n
              foundIndex = perEventHandlers.indexOf(listener, foundIndex);\n
            }\n
          } else {\n
            perEventHandlers.length = 0;\n
          }\n
        }\n
      }\n
    }\n
    return this;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.handlers`.\n
 * @private\n
 */\n
  var _clientListeners = function(eventType) {\n
    var copy = null, handlers = _clientMeta[this.id] && _clientMeta[this.id].handlers;\n
    if (handlers) {\n
      if (typeof eventType === "string" && eventType) {\n
        copy = handlers[eventType] ? handlers[eventType].slice(0) : [];\n
      } else {\n
        copy = _deepCopy(handlers);\n
      }\n
    }\n
    return copy;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.emit`.\n
 * @private\n
 */\n
  var _clientEmit = function(event) {\n
    if (_clientShouldEmit.call(this, event)) {\n
      if (typeof event === "object" && event && typeof event.type === "string" && event.type) {\n
        event = _extend({}, event);\n
      }\n
      var eventCopy = _extend({}, _createEvent(event), {\n
        client: this\n
      });\n
      _clientDispatchCallbacks.call(this, eventCopy);\n
    }\n
    return this;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.clip`.\n
 * @private\n
 */\n
  var _clientClip = function(elements) {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to clip element(s) to a destroyed ZeroClipboard client instance");\n
    }\n
    elements = _prepClip(elements);\n
    for (var i = 0; i < elements.length; i++) {\n
      if (_hasOwn.call(elements, i) && elements[i] && elements[i].nodeType === 1) {\n
        if (!elements[i].zcClippingId) {\n
          elements[i].zcClippingId = "zcClippingId_" + _elementIdCounter++;\n
          _elementMeta[elements[i].zcClippingId] = [ this.id ];\n
          if (_globalConfig.autoActivate === true) {\n
            _addMouseHandlers(elements[i]);\n
          }\n
        } else if (_elementMeta[elements[i].zcClippingId].indexOf(this.id) === -1) {\n
          _elementMeta[elements[i].zcClippingId].push(this.id);\n
        }\n
        var clippedElements = _clientMeta[this.id] && _clientMeta[this.id].elements;\n
        if (clippedElements.indexOf(elements[i]) === -1) {\n
          clippedElements.push(elements[i]);\n
        }\n
      }\n
    }\n
    return this;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.unclip`.\n
 * @private\n
 */\n
  var _clientUnclip = function(elements) {\n
    var meta = _clientMeta[this.id];\n
    if (!meta) {\n
      return this;\n
    }\n
    var clippedElements = meta.elements;\n
    var arrayIndex;\n
    if (typeof elements === "undefined") {\n
      elements = clippedElements.slice(0);\n
    } else {\n
      elements = _prepClip(elements);\n
    }\n
    for (var i = elements.length; i--; ) {\n
      if (_hasOwn.call(elements, i) && elements[i] && elements[i].nodeType === 1) {\n
        arrayIndex = 0;\n
        while ((arrayIndex = clippedElements.indexOf(elements[i], arrayIndex)) !== -1) {\n
          clippedElements.splice(arrayIndex, 1);\n
        }\n
        var clientIds = _elementMeta[elements[i].zcClippingId];\n
        if (clientIds) {\n
          arrayIndex = 0;\n
          while ((arrayIndex = clientIds.indexOf(this.id, arrayIndex)) !== -1) {\n
            clientIds.splice(arrayIndex, 1);\n
          }\n
          if (clientIds.length === 0) {\n
            if (_globalConfig.autoActivate === true) {\n
              _removeMouseHandlers(elements[i]);\n
            }\n
            delete elements[i].zcClippingId;\n
          }\n
        }\n
      }\n
    }\n
    return this;\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.elements`.\n
 * @private\n
 */\n
  var _clientElements = function() {\n
    var meta = _clientMeta[this.id];\n
    return meta && meta.elements ? meta.elements.slice(0) : [];\n
  };\n
  /**\n
 * The underlying implementation of `ZeroClipboard.Client.prototype.destroy`.\n
 * @private\n
 */\n
  var _clientDestroy = function() {\n
    if (!_clientMeta[this.id]) {\n
      return;\n
    }\n
    this.unclip();\n
    this.off();\n
    delete _clientMeta[this.id];\n
  };\n
  /**\n
 * Inspect an Event to see if the Client (`this`) should honor it for emission.\n
 * @private\n
 */\n
  var _clientShouldEmit = function(event) {\n
    if (!(event && event.type)) {\n
      return false;\n
    }\n
    if (event.client && event.client !== this) {\n
      return false;\n
    }\n
    var meta = _clientMeta[this.id];\n
    var clippedEls = meta && meta.elements;\n
    var hasClippedEls = !!clippedEls && clippedEls.length > 0;\n
    var goodTarget = !event.target || hasClippedEls && clippedEls.indexOf(event.target) !== -1;\n
    var goodRelTarget = event.relatedTarget && hasClippedEls && clippedEls.indexOf(event.relatedTarget) !== -1;\n
    var goodClient = event.client && event.client === this;\n
    if (!meta || !(goodTarget || goodRelTarget || goodClient)) {\n
      return false;\n
    }\n
    return true;\n
  };\n
  /**\n
 * Handle the actual dispatching of events to a client instance.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _clientDispatchCallbacks = function(event) {\n
    var meta = _clientMeta[this.id];\n
    if (!(typeof event === "object" && event && event.type && meta)) {\n
      return;\n
    }\n
    var async = _shouldPerformAsync(event);\n
    var wildcardTypeHandlers = meta && meta.handlers["*"] || [];\n
    var specificTypeHandlers = meta && meta.handlers[event.type] || [];\n
    var handlers = wildcardTypeHandlers.concat(specificTypeHandlers);\n
    if (handlers && handlers.length) {\n
      var i, len, func, context, eventCopy, originalContext = this;\n
      for (i = 0, len = handlers.length; i < len; i++) {\n
        func = handlers[i];\n
        context = originalContext;\n
        if (typeof func === "string" && typeof _window[func] === "function") {\n
          func = _window[func];\n
        }\n
        if (typeof func === "object" && func && typeof func.handleEvent === "function") {\n
          context = func;\n
          func = func.handleEvent;\n
        }\n
        if (typeof func === "function") {\n
          eventCopy = _extend({}, event);\n
          _dispatchCallback(func, context, [ eventCopy ], async);\n
        }\n
      }\n
    }\n
  };\n
  /**\n
 * Prepares the elements for clipping/unclipping.\n
 *\n
 * @returns An Array of elements.\n
 * @private\n
 */\n
  var _prepClip = function(elements) {\n
    if (typeof elements === "string") {\n
      elements = [];\n
    }\n
    return typeof elements.length !== "number" ? [ elements ] : elements;\n
  };\n
  /**\n
 * Add a `mouseover` handler function for a clipped element.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _addMouseHandlers = function(element) {\n
    if (!(element && element.nodeType === 1)) {\n
      return;\n
    }\n
    var _suppressMouseEvents = function(event) {\n
      if (!(event || (event = _window.event))) {\n
        return;\n
      }\n
      if (event._source !== "js") {\n
        event.stopImmediatePropagation();\n
        event.preventDefault();\n
      }\n
      delete event._source;\n
    };\n
    var _elementMouseOver = function(event) {\n
      if (!(event || (event = _window.event))) {\n
        return;\n
      }\n
      _suppressMouseEvents(event);\n
      ZeroClipboard.focus(element);\n
    };\n
    element.addEventListener("mouseover", _elementMouseOver, false);\n
    element.addEventListener("mouseout", _suppressMouseEvents, false);\n
    element.addEventListener("mouseenter", _suppressMouseEvents, false);\n
    element.addEventListener("mouseleave", _suppressMouseEvents, false);\n
    element.addEventListener("mousemove", _suppressMouseEvents, false);\n
    _mouseHandlers[element.zcClippingId] = {\n
      mouseover: _elementMouseOver,\n
      mouseout: _suppressMouseEvents,\n
      mouseenter: _suppressMouseEvents,\n
      mouseleave: _suppressMouseEvents,\n
      mousemove: _suppressMouseEvents\n
    };\n
  };\n
  /**\n
 * Remove a `mouseover` handler function for a clipped element.\n
 *\n
 * @returns `undefined`\n
 * @private\n
 */\n
  var _removeMouseHandlers = function(element) {\n
    if (!(element && element.nodeType === 1)) {\n
      return;\n
    }\n
    var mouseHandlers = _mouseHandlers[element.zcClippingId];\n
    if (!(typeof mouseHandlers === "object" && mouseHandlers)) {\n
      return;\n
    }\n
    var key, val, mouseEvents = [ "move", "leave", "enter", "out", "over" ];\n
    for (var i = 0, len = mouseEvents.length; i < len; i++) {\n
      key = "mouse" + mouseEvents[i];\n
      val = mouseHandlers[key];\n
      if (typeof val === "function") {\n
        element.removeEventListener(key, val, false);\n
      }\n
    }\n
    delete _mouseHandlers[element.zcClippingId];\n
  };\n
  /**\n
 * Creates a new ZeroClipboard client instance.\n
 * Optionally, auto-`clip` an element or collection of elements.\n
 *\n
 * @constructor\n
 */\n
  ZeroClipboard._createClient = function() {\n
    _clientConstructor.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Register an event listener to the client.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.on = function() {\n
    return _clientOn.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Unregister an event handler from the client.\n
 * If no `listener` function/object is provided, it will unregister all handlers for the provided `eventType`.\n
 * If no `eventType` is provided, it will unregister all handlers for every event type.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.off = function() {\n
    return _clientOff.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Retrieve event listeners for an `eventType` from the client.\n
 * If no `eventType` is provided, it will retrieve all listeners for every event type.\n
 *\n
 * @returns array of listeners for the `eventType`; if no `eventType`, then a map/hash object of listeners for all event types; or `null`\n
 */\n
  ZeroClipboard.prototype.handlers = function() {\n
    return _clientListeners.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Event emission receiver from the Flash object for this client\'s registered JavaScript event listeners.\n
 *\n
 * @returns For the "copy" event, returns the Flash-friendly "clipData" object; otherwise `undefined`.\n
 */\n
  ZeroClipboard.prototype.emit = function() {\n
    return _clientEmit.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Register clipboard actions for new element(s) to the client.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.clip = function() {\n
    return _clientClip.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Unregister the clipboard actions of previously registered element(s) on the page.\n
 * If no elements are provided, ALL registered elements will be unregistered.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.unclip = function() {\n
    return _clientUnclip.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Get all of the elements to which this client is clipped.\n
 *\n
 * @returns array of clipped elements\n
 */\n
  ZeroClipboard.prototype.elements = function() {\n
    return _clientElements.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Self-destruct and clean up everything for a single client.\n
 * This will NOT destroy the embedded Flash object.\n
 *\n
 * @returns `undefined`\n
 */\n
  ZeroClipboard.prototype.destroy = function() {\n
    return _clientDestroy.apply(this, _args(arguments));\n
  };\n
  /**\n
 * Stores the pending plain text to inject into the clipboard.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.setText = function(text) {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to set pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    ZeroClipboard.setData("text/plain", text);\n
    return this;\n
  };\n
  /**\n
 * Stores the pending HTML text to inject into the clipboard.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.setHtml = function(html) {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to set pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    ZeroClipboard.setData("text/html", html);\n
    return this;\n
  };\n
  /**\n
 * Stores the pending rich text (RTF) to inject into the clipboard.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.setRichText = function(richText) {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to set pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    ZeroClipboard.setData("application/rtf", richText);\n
    return this;\n
  };\n
  /**\n
 * Stores the pending data to inject into the clipboard.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.setData = function() {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to set pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    ZeroClipboard.setData.apply(this, _args(arguments));\n
    return this;\n
  };\n
  /**\n
 * Clears the pending data to inject into the clipboard.\n
 * If no `format` is provided, all pending data formats will be cleared.\n
 *\n
 * @returns `this`\n
 */\n
  ZeroClipboard.prototype.clearData = function() {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to clear pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    ZeroClipboard.clearData.apply(this, _args(arguments));\n
    return this;\n
  };\n
  /**\n
 * Gets a copy of the pending data to inject into the clipboard.\n
 * If no `format` is provided, a copy of ALL pending data formats will be returned.\n
 *\n
 * @returns `String` or `Object`\n
 */\n
  ZeroClipboard.prototype.getData = function() {\n
    if (!_clientMeta[this.id]) {\n
      throw new Error("Attempted to get pending clipboard data from a destroyed ZeroClipboard client instance");\n
    }\n
    return ZeroClipboard.getData.apply(this, _args(arguments));\n
  };\n
  if (typeof define === "function" && define.amd) {\n
    define(function() {\n
      return ZeroClipboard;\n
    });\n
  } else if (typeof module === "object" && module && typeof module.exports === "object" && module.exports) {\n
    module.exports = ZeroClipboard;\n
  } else {\n
    window.ZeroClipboard = ZeroClipboard;\n
  }\n
})(function() {\n
  return this || window;\n
}());\n
},{}]},{},[27,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,89,90,91,75,76,77,78,79,80,35,39,44,36,37,38,40,41,42,43]);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>905518</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
