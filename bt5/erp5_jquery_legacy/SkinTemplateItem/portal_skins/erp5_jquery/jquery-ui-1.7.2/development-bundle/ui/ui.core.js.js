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
            <value> <string>ts65545394.27</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.core.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI\n
 */\n
;jQuery.ui || (function($) {\n
\n
var _remove = $.fn.remove,\n
\tisFF2 = $.browser.mozilla && (parseFloat($.browser.version) < 1.9);\n
\n
//Helper functions and ui object\n
$.ui = {\n
\tversion: "1.7.2",\n
\n
\t// $.ui.plugin is deprecated.  Use the proxy pattern instead.\n
\tplugin: {\n
\t\tadd: function(module, option, set) {\n
\t\t\tvar proto = $.ui[module].prototype;\n
\t\t\tfor(var i in set) {\n
\t\t\t\tproto.plugins[i] = proto.plugins[i] || [];\n
\t\t\t\tproto.plugins[i].push([option, set[i]]);\n
\t\t\t}\n
\t\t},\n
\t\tcall: function(instance, name, args) {\n
\t\t\tvar set = instance.plugins[name];\n
\t\t\tif(!set || !instance.element[0].parentNode) { return; }\n
\n
\t\t\tfor (var i = 0; i < set.length; i++) {\n
\t\t\t\tif (instance.options[set[i][0]]) {\n
\t\t\t\t\tset[i][1].apply(instance.element, args);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\tcontains: function(a, b) {\n
\t\treturn document.compareDocumentPosition\n
\t\t\t? a.compareDocumentPosition(b) & 16\n
\t\t\t: a !== b && a.contains(b);\n
\t},\n
\n
\thasScroll: function(el, a) {\n
\n
\t\t//If overflow is hidden, the element might have extra content, but the user wants to hide it\n
\t\tif ($(el).css(\'overflow\') == \'hidden\') { return false; }\n
\n
\t\tvar scroll = (a && a == \'left\') ? \'scrollLeft\' : \'scrollTop\',\n
\t\t\thas = false;\n
\n
\t\tif (el[scroll] > 0) { return true; }\n
\n
\t\t// TODO: determine which cases actually cause this to happen\n
\t\t// if the element doesn\'t have the scroll set, see if it\'s possible to\n
\t\t// set the scroll\n
\t\tel[scroll] = 1;\n
\t\thas = (el[scroll] > 0);\n
\t\tel[scroll] = 0;\n
\t\treturn has;\n
\t},\n
\n
\tisOverAxis: function(x, reference, size) {\n
\t\t//Determines when x coordinate is over "b" element axis\n
\t\treturn (x > reference) && (x < (reference + size));\n
\t},\n
\n
\tisOver: function(y, x, top, left, height, width) {\n
\t\t//Determines when x, y coordinates is over "b" element\n
\t\treturn $.ui.isOverAxis(y, top, height) && $.ui.isOverAxis(x, left, width);\n
\t},\n
\n
\tkeyCode: {\n
\t\tBACKSPACE: 8,\n
\t\tCAPS_LOCK: 20,\n
\t\tCOMMA: 188,\n
\t\tCONTROL: 17,\n
\t\tDELETE: 46,\n
\t\tDOWN: 40,\n
\t\tEND: 35,\n
\t\tENTER: 13,\n
\t\tESCAPE: 27,\n
\t\tHOME: 36,\n
\t\tINSERT: 45,\n
\t\tLEFT: 37,\n
\t\tNUMPAD_ADD: 107,\n
\t\tNUMPAD_DECIMAL: 110,\n
\t\tNUMPAD_DIVIDE: 111,\n
\t\tNUMPAD_ENTER: 108,\n
\t\tNUMPAD_MULTIPLY: 106,\n
\t\tNUMPAD_SUBTRACT: 109,\n
\t\tPAGE_DOWN: 34,\n
\t\tPAGE_UP: 33,\n
\t\tPERIOD: 190,\n
\t\tRIGHT: 39,\n
\t\tSHIFT: 16,\n
\t\tSPACE: 32,\n
\t\tTAB: 9,\n
\t\tUP: 38\n
\t}\n
};\n
\n
// WAI-ARIA normalization\n
if (isFF2) {\n
\tvar attr = $.attr,\n
\t\tremoveAttr = $.fn.removeAttr,\n
\t\tariaNS = "http://www.w3.org/2005/07/aaa",\n
\t\tariaState = /^aria-/,\n
\t\tariaRole = /^wairole:/;\n
\n
\t$.attr = function(elem, name, value) {\n
\t\tvar set = value !== undefined;\n
\n
\t\treturn (name == \'role\'\n
\t\t\t? (set\n
\t\t\t\t? attr.call(this, elem, name, "wairole:" + value)\n
\t\t\t\t: (attr.apply(this, arguments) || "").replace(ariaRole, ""))\n
\t\t\t: (ariaState.test(name)\n
\t\t\t\t? (set\n
\t\t\t\t\t? elem.setAttributeNS(ariaNS,\n
\t\t\t\t\t\tname.replace(ariaState, "aaa:"), value)\n
\t\t\t\t\t: attr.call(this, elem, name.replace(ariaState, "aaa:")))\n
\t\t\t\t: attr.apply(this, arguments)));\n
\t};\n
\n
\t$.fn.removeAttr = function(name) {\n
\t\treturn (ariaState.test(name)\n
\t\t\t? this.each(function() {\n
\t\t\t\tthis.removeAttributeNS(ariaNS, name.replace(ariaState, ""));\n
\t\t\t}) : removeAttr.call(this, name));\n
\t};\n
}\n
\n
//jQuery plugins\n
$.fn.extend({\n
\tremove: function() {\n
\t\t// Safari has a native remove event which actually removes DOM elements,\n
\t\t// so we have to use triggerHandler instead of trigger (#3037).\n
\t\t$("*", this).add(this).each(function() {\n
\t\t\t$(this).triggerHandler("remove");\n
\t\t});\n
\t\treturn _remove.apply(this, arguments );\n
\t},\n
\n
\tenableSelection: function() {\n
\t\treturn this\n
\t\t\t.attr(\'unselectable\', \'off\')\n
\t\t\t.css(\'MozUserSelect\', \'\')\n
\t\t\t.unbind(\'selectstart.ui\');\n
\t},\n
\n
\tdisableSelection: function() {\n
\t\treturn this\n
\t\t\t.attr(\'unselectable\', \'on\')\n
\t\t\t.css(\'MozUserSelect\', \'none\')\n
\t\t\t.bind(\'selectstart.ui\', function() { return false; });\n
\t},\n
\n
\tscrollParent: function() {\n
\t\tvar scrollParent;\n
\t\tif(($.browser.msie && (/(static|relative)/).test(this.css(\'position\'))) || (/absolute/).test(this.css(\'position\'))) {\n
\t\t\tscrollParent = this.parents().filter(function() {\n
\t\t\t\treturn (/(relative|absolute|fixed)/).test($.curCSS(this,\'position\',1)) && (/(auto|scroll)/).test($.curCSS(this,\'overflow\',1)+$.curCSS(this,\'overflow-y\',1)+$.curCSS(this,\'overflow-x\',1));\n
\t\t\t}).eq(0);\n
\t\t} else {\n
\t\t\tscrollParent = this.parents().filter(function() {\n
\t\t\t\treturn (/(auto|scroll)/).test($.curCSS(this,\'overflow\',1)+$.curCSS(this,\'overflow-y\',1)+$.curCSS(this,\'overflow-x\',1));\n
\t\t\t}).eq(0);\n
\t\t}\n
\n
\t\treturn (/fixed/).test(this.css(\'position\')) || !scrollParent.length ? $(document) : scrollParent;\n
\t}\n
});\n
\n
\n
//Additional selectors\n
$.extend($.expr[\':\'], {\n
\tdata: function(elem, i, match) {\n
\t\treturn !!$.data(elem, match[3]);\n
\t},\n
\n
\tfocusable: function(element) {\n
\t\tvar nodeName = element.nodeName.toLowerCase(),\n
\t\t\ttabIndex = $.attr(element, \'tabindex\');\n
\t\treturn (/input|select|textarea|button|object/.test(nodeName)\n
\t\t\t? !element.disabled\n
\t\t\t: \'a\' == nodeName || \'area\' == nodeName\n
\t\t\t\t? element.href || !isNaN(tabIndex)\n
\t\t\t\t: !isNaN(tabIndex))\n
\t\t\t// the element and all of its ancestors must be visible\n
\t\t\t// the browser may report that the area is hidden\n
\t\t\t&& !$(element)[\'area\' == nodeName ? \'parents\' : \'closest\'](\':hidden\').length;\n
\t},\n
\n
\ttabbable: function(element) {\n
\t\tvar tabIndex = $.attr(element, \'tabindex\');\n
\t\treturn (isNaN(tabIndex) || tabIndex >= 0) && $(element).is(\':focusable\');\n
\t}\n
});\n
\n
\n
// $.widget is a factory to create jQuery plugins\n
// taking some boilerplate code out of the plugin code\n
function getter(namespace, plugin, method, args) {\n
\tfunction getMethods(type) {\n
\t\tvar methods = $[namespace][plugin][type] || [];\n
\t\treturn (typeof methods == \'string\' ? methods.split(/,?\\s+/) : methods);\n
\t}\n
\n
\tvar methods = getMethods(\'getter\');\n
\tif (args.length == 1 && typeof args[0] == \'string\') {\n
\t\tmethods = methods.concat(getMethods(\'getterSetter\'));\n
\t}\n
\treturn ($.inArray(method, methods) != -1);\n
}\n
\n
$.widget = function(name, prototype) {\n
\tvar namespace = name.split(".")[0];\n
\tname = name.split(".")[1];\n
\n
\t// create plugin method\n
\t$.fn[name] = function(options) {\n
\t\tvar isMethodCall = (typeof options == \'string\'),\n
\t\t\targs = Array.prototype.slice.call(arguments, 1);\n
\n
\t\t// prevent calls to internal methods\n
\t\tif (isMethodCall && options.substring(0, 1) == \'_\') {\n
\t\t\treturn this;\n
\t\t}\n
\n
\t\t// handle getter methods\n
\t\tif (isMethodCall && getter(namespace, name, options, args)) {\n
\t\t\tvar instance = $.data(this[0], name);\n
\t\t\treturn (instance ? instance[options].apply(instance, args)\n
\t\t\t\t: undefined);\n
\t\t}\n
\n
\t\t// handle initialization and non-getter methods\n
\t\treturn this.each(function() {\n
\t\t\tvar instance = $.data(this, name);\n
\n
\t\t\t// constructor\n
\t\t\t(!instance && !isMethodCall &&\n
\t\t\t\t$.data(this, name, new $[namespace][name](this, options))._init());\n
\n
\t\t\t// method call\n
\t\t\t(instance && isMethodCall && $.isFunction(instance[options]) &&\n
\t\t\t\tinstance[options].apply(instance, args));\n
\t\t});\n
\t};\n
\n
\t// create widget constructor\n
\t$[namespace] = $[namespace] || {};\n
\t$[namespace][name] = function(element, options) {\n
\t\tvar self = this;\n
\n
\t\tthis.namespace = namespace;\n
\t\tthis.widgetName = name;\n
\t\tthis.widgetEventPrefix = $[namespace][name].eventPrefix || name;\n
\t\tthis.widgetBaseClass = namespace + \'-\' + name;\n
\n
\t\tthis.options = $.extend({},\n
\t\t\t$.widget.defaults,\n
\t\t\t$[namespace][name].defaults,\n
\t\t\t$.metadata && $.metadata.get(element)[name],\n
\t\t\toptions);\n
\n
\t\tthis.element = $(element)\n
\t\t\t.bind(\'setData.\' + name, function(event, key, value) {\n
\t\t\t\tif (event.target == element) {\n
\t\t\t\t\treturn self._setData(key, value);\n
\t\t\t\t}\n
\t\t\t})\n
\t\t\t.bind(\'getData.\' + name, function(event, key) {\n
\t\t\t\tif (event.target == element) {\n
\t\t\t\t\treturn self._getData(key);\n
\t\t\t\t}\n
\t\t\t})\n
\t\t\t.bind(\'remove\', function() {\n
\t\t\t\treturn self.destroy();\n
\t\t\t});\n
\t};\n
\n
\t// add widget prototype\n
\t$[namespace][name].prototype = $.extend({}, $.widget.prototype, prototype);\n
\n
\t// TODO: merge getter and getterSetter properties from widget prototype\n
\t// and plugin prototype\n
\t$[namespace][name].getterSetter = \'option\';\n
};\n
\n
$.widget.prototype = {\n
\t_init: function() {},\n
\tdestroy: function() {\n
\t\tthis.element.removeData(this.widgetName)\n
\t\t\t.removeClass(this.widgetBaseClass + \'-disabled\' + \' \' + this.namespace + \'-state-disabled\')\n
\t\t\t.removeAttr(\'aria-disabled\');\n
\t},\n
\n
\toption: function(key, value) {\n
\t\tvar options = key,\n
\t\t\tself = this;\n
\n
\t\tif (typeof key == "string") {\n
\t\t\tif (value === undefined) {\n
\t\t\t\treturn this._getData(key);\n
\t\t\t}\n
\t\t\toptions = {};\n
\t\t\toptions[key] = value;\n
\t\t}\n
\n
\t\t$.each(options, function(key, value) {\n
\t\t\tself._setData(key, value);\n
\t\t});\n
\t},\n
\t_getData: function(key) {\n
\t\treturn this.options[key];\n
\t},\n
\t_setData: function(key, value) {\n
\t\tthis.options[key] = value;\n
\n
\t\tif (key == \'disabled\') {\n
\t\t\tthis.element\n
\t\t\t\t[value ? \'addClass\' : \'removeClass\'](\n
\t\t\t\t\tthis.widgetBaseClass + \'-disabled\' + \' \' +\n
\t\t\t\t\tthis.namespace + \'-state-disabled\')\n
\t\t\t\t.attr("aria-disabled", value);\n
\t\t}\n
\t},\n
\n
\tenable: function() {\n
\t\tthis._setData(\'disabled\', false);\n
\t},\n
\tdisable: function() {\n
\t\tthis._setData(\'disabled\', true);\n
\t},\n
\n
\t_trigger: function(type, event, data) {\n
\t\tvar callback = this.options[type],\n
\t\t\teventName = (type == this.widgetEventPrefix\n
\t\t\t\t? type : this.widgetEventPrefix + type);\n
\n
\t\tevent = $.Event(event);\n
\t\tevent.type = eventName;\n
\n
\t\t// copy original event properties over to the new event\n
\t\t// this would happen if we could call $.event.fix instead of $.Event\n
\t\t// but we don\'t have a way to force an event to be fixed multiple times\n
\t\tif (event.originalEvent) {\n
\t\t\tfor (var i = $.event.props.length, prop; i;) {\n
\t\t\t\tprop = $.event.props[--i];\n
\t\t\t\tevent[prop] = event.originalEvent[prop];\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.element.trigger(event, data);\n
\n
\t\treturn !($.isFunction(callback) && callback.call(this.element[0], event, data) === false\n
\t\t\t|| event.isDefaultPrevented());\n
\t}\n
};\n
\n
$.widget.defaults = {\n
\tdisabled: false\n
};\n
\n
\n
/** Mouse Interaction Plugin **/\n
\n
$.ui.mouse = {\n
\t_mouseInit: function() {\n
\t\tvar self = this;\n
\n
\t\tthis.element\n
\t\t\t.bind(\'mousedown.\'+this.widgetName, function(event) {\n
\t\t\t\treturn self._mouseDown(event);\n
\t\t\t})\n
\t\t\t.bind(\'click.\'+this.widgetName, function(event) {\n
\t\t\t\tif(self._preventClickEvent) {\n
\t\t\t\t\tself._preventClickEvent = false;\n
\t\t\t\t\tevent.stopImmediatePropagation();\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t// Prevent text selection in IE\n
\t\tif ($.browser.msie) {\n
\t\t\tthis._mouseUnselectable = this.element.attr(\'unselectable\');\n
\t\t\tthis.element.attr(\'unselectable\', \'on\');\n
\t\t}\n
\n
\t\tthis.started = false;\n
\t},\n
\n
\t// TODO: make sure destroying one instance of mouse doesn\'t mess with\n
\t// other instances of mouse\n
\t_mouseDestroy: function() {\n
\t\tthis.element.unbind(\'.\'+this.widgetName);\n
\n
\t\t// Restore text selection in IE\n
\t\t($.browser.msie\n
\t\t\t&& this.element.attr(\'unselectable\', this._mouseUnselectable));\n
\t},\n
\n
\t_mouseDown: function(event) {\n
\t\t// don\'t let more than one widget handle mouseStart\n
\t\t// TODO: figure out why we have to use originalEvent\n
\t\tevent.originalEvent = event.originalEvent || {};\n
\t\tif (event.originalEvent.mouseHandled) { return; }\n
\n
\t\t// we may have missed mouseup (out of window)\n
\t\t(this._mouseStarted && this._mouseUp(event));\n
\n
\t\tthis._mouseDownEvent = event;\n
\n
\t\tvar self = this,\n
\t\t\tbtnIsLeft = (event.which == 1),\n
\t\t\telIsCancel = (typeof this.options.cancel == "string" ? $(event.target).parents().add(event.target).filter(this.options.cancel).length : false);\n
\t\tif (!btnIsLeft || elIsCancel || !this._mouseCapture(event)) {\n
\t\t\treturn true;\n
\t\t}\n
\n
\t\tthis.mouseDelayMet = !this.options.delay;\n
\t\tif (!this.mouseDelayMet) {\n
\t\t\tthis._mouseDelayTimer = setTimeout(function() {\n
\t\t\t\tself.mouseDelayMet = true;\n
\t\t\t}, this.options.delay);\n
\t\t}\n
\n
\t\tif (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {\n
\t\t\tthis._mouseStarted = (this._mouseStart(event) !== false);\n
\t\t\tif (!this._mouseStarted) {\n
\t\t\t\tevent.preventDefault();\n
\t\t\t\treturn true;\n
\t\t\t}\n
\t\t}\n
\n
\t\t// these delegates are required to keep context\n
\t\tthis._mouseMoveDelegate = function(event) {\n
\t\t\treturn self._mouseMove(event);\n
\t\t};\n
\t\tthis._mouseUpDelegate = function(event) {\n
\t\t\treturn self._mouseUp(event);\n
\t\t};\n
\t\t$(document)\n
\t\t\t.bind(\'mousemove.\'+this.widgetName, this._mouseMoveDelegate)\n
\t\t\t.bind(\'mouseup.\'+this.widgetName, this._mouseUpDelegate);\n
\n
\t\t// preventDefault() is used to prevent the selection of text here -\n
\t\t// however, in Safari, this causes select boxes not to be selectable\n
\t\t// anymore, so this fix is needed\n
\t\t($.browser.safari || event.preventDefault());\n
\n
\t\tevent.originalEvent.mouseHandled = true;\n
\t\treturn true;\n
\t},\n
\n
\t_mouseMove: function(event) {\n
\t\t// IE mouseup check - mouseup happened when mouse was out of window\n
\t\tif ($.browser.msie && !event.button) {\n
\t\t\treturn this._mouseUp(event);\n
\t\t}\n
\n
\t\tif (this._mouseStarted) {\n
\t\t\tthis._mouseDrag(event);\n
\t\t\treturn event.preventDefault();\n
\t\t}\n
\n
\t\tif (this._mouseDistanceMet(event) && this._mouseDelayMet(event)) {\n
\t\t\tthis._mouseStarted =\n
\t\t\t\t(this._mouseStart(this._mouseDownEvent, event) !== false);\n
\t\t\t(this._mouseStarted ? this._mouseDrag(event) : this._mouseUp(event));\n
\t\t}\n
\n
\t\treturn !this._mouseStarted;\n
\t},\n
\n
\t_mouseUp: function(event) {\n
\t\t$(document)\n
\t\t\t.unbind(\'mousemove.\'+this.widgetName, this._mouseMoveDelegate)\n
\t\t\t.unbind(\'mouseup.\'+this.widgetName, this._mouseUpDelegate);\n
\n
\t\tif (this._mouseStarted) {\n
\t\t\tthis._mouseStarted = false;\n
\t\t\tthis._preventClickEvent = (event.target == this._mouseDownEvent.target);\n
\t\t\tthis._mouseStop(event);\n
\t\t}\n
\n
\t\treturn false;\n
\t},\n
\n
\t_mouseDistanceMet: function(event) {\n
\t\treturn (Math.max(\n
\t\t\t\tMath.abs(this._mouseDownEvent.pageX - event.pageX),\n
\t\t\t\tMath.abs(this._mouseDownEvent.pageY - event.pageY)\n
\t\t\t) >= this.options.distance\n
\t\t);\n
\t},\n
\n
\t_mouseDelayMet: function(event) {\n
\t\treturn this.mouseDelayMet;\n
\t},\n
\n
\t// These are placeholder methods, to be overriden by extending plugin\n
\t_mouseStart: function(event) {},\n
\t_mouseDrag: function(event) {},\n
\t_mouseStop: function(event) {},\n
\t_mouseCapture: function(event) { return true; }\n
};\n
\n
$.ui.mouse.defaults = {\n
\tcancel: null,\n
\tdistance: 1,\n
\tdelay: 0\n
};\n
\n
})(jQuery);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <long>13932</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
