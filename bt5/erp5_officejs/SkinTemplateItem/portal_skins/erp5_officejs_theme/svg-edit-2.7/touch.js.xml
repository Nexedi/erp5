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
            <value> <string>ts40515059.58</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>touch.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// http://ross.posterous.com/2008/08/19/iphone-touch-events-in-javascript/\n
function touchHandler(event) {\'use strict\';\n
\n
\tvar simulatedEvent,\n
\t\ttouches = event.changedTouches,\n
\t\tfirst = touches[0],\n
\t\ttype = "";\n
\tswitch (event.type) {\n
\t\tcase "touchstart": type = "mousedown"; break;\n
\t\tcase "touchmove":  type = "mousemove"; break;\n
\t\tcase "touchend":   type = "mouseup"; break;\n
\t\tdefault: return;\n
\t}\n
\n
\t// initMouseEvent(type, canBubble, cancelable, view, clickCount, \n
\t//\tscreenX, screenY, clientX, clientY, ctrlKey, \n
\t//\taltKey, shiftKey, metaKey, button, relatedTarget);\n
\n
\tsimulatedEvent = document.createEvent("MouseEvent");\n
\tsimulatedEvent.initMouseEvent(type, true, true, window, 1,\n
\t\t\t\t\t\t\t\tfirst.screenX, first.screenY,\n
\t\t\t\t\t\t\t\tfirst.clientX, first.clientY, false,\n
\t\t\t\t\t\t\t\tfalse, false, false, 0/*left*/, null);\n
\tif (touches.length < 2) {\n
\t\tfirst.target.dispatchEvent(simulatedEvent);\n
\t\tevent.preventDefault();\n
\t}\n
}\n
\n
document.addEventListener(\'touchstart\', touchHandler, true);\n
document.addEventListener(\'touchmove\', touchHandler, true);\n
document.addEventListener(\'touchend\', touchHandler, true);\n
document.addEventListener(\'touchcancel\', touchHandler, true);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1161</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
