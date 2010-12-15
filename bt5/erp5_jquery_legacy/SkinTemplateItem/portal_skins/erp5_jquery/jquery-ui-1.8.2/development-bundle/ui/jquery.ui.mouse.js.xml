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
            <value> <string>ts77895656.02</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.mouse.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * jQuery UI Mouse 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Mouse\n
 *\n
 * Depends:\n
 *\tjquery.ui.widget.js\n
 */\n
(function($) {\n
\n
$.widget("ui.mouse", {\n
\toptions: {\n
\t\tcancel: \':input,option\',\n
\t\tdistance: 1,\n
\t\tdelay: 0\n
\t},\n
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
\t\tthis.started = false;\n
\t},\n
\n
\t// TODO: make sure destroying one instance of mouse doesn\'t mess with\n
\t// other instances of mouse\n
\t_mouseDestroy: function() {\n
\t\tthis.element.unbind(\'.\'+this.widgetName);\n
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
});\n
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
            <value> <int>4058</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
