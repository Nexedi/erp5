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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts52852179.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>mousewheel.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*! Copyright (c) 2011 Brandon Aaron (http://brandonaaron.net)\n
 * Licensed under the MIT License (LICENSE.txt).\n
 *\n
 * Thanks to: http://adomas.org/javascript-mouse-wheel/ for some pointers.\n
 * Thanks to: Mathias Bank(http://www.mathias-bank.de) for a scope bug fix.\n
 * Thanks to: Seamus Leahy for adding deltaX and deltaY\n
 *\n
 * Version: 3.0.6\n
 * \n
 * Requires: 1.2.2+\n
 */\n
\n
(function($) {\n
\n
var types = [\'DOMMouseScroll\', \'mousewheel\'];\n
\n
if ($.event.fixHooks) {\n
    for ( var i=types.length; i; ) {\n
        $.event.fixHooks[ types[--i] ] = $.event.mouseHooks;\n
    }\n
}\n
\n
$.event.special.mousewheel = {\n
    setup: function() {\n
        if ( this.addEventListener ) {\n
            for ( var i=types.length; i; ) {\n
                this.addEventListener( types[--i], handler, false );\n
            }\n
        } else {\n
            this.onmousewheel = handler;\n
        }\n
    },\n
    \n
    teardown: function() {\n
        if ( this.removeEventListener ) {\n
            for ( var i=types.length; i; ) {\n
                this.removeEventListener( types[--i], handler, false );\n
            }\n
        } else {\n
            this.onmousewheel = null;\n
        }\n
    }\n
};\n
\n
$.fn.extend({\n
    mousewheel: function(fn) {\n
        return fn ? this.bind("mousewheel", fn) : this.trigger("mousewheel");\n
    },\n
    \n
    unmousewheel: function(fn) {\n
        return this.unbind("mousewheel", fn);\n
    }\n
});\n
\n
\n
function handler(event) {\n
    var orgEvent = event || window.event, args = [].slice.call( arguments, 1 ), delta = 0, returnValue = true, deltaX = 0, deltaY = 0;\n
    event = $.event.fix(orgEvent);\n
    event.type = "mousewheel";\n
    \n
    // Old school scrollwheel delta\n
    if ( orgEvent.wheelDelta ) { delta = orgEvent.wheelDelta/120; }\n
    if ( orgEvent.detail     ) { delta = -orgEvent.detail/3; }\n
    \n
    // New school multidimensional scroll (touchpads) deltas\n
    deltaY = delta;\n
    \n
    // Gecko\n
    if ( orgEvent.axis !== undefined && orgEvent.axis === orgEvent.HORIZONTAL_AXIS ) {\n
        deltaY = 0;\n
        deltaX = -1*delta;\n
    }\n
    \n
    // Webkit\n
    if ( orgEvent.wheelDeltaY !== undefined ) { deltaY = orgEvent.wheelDeltaY/120; }\n
    if ( orgEvent.wheelDeltaX !== undefined ) { deltaX = -1*orgEvent.wheelDeltaX/120; }\n
    \n
    // Add event and delta to the front of the arguments\n
    args.unshift(event, delta, deltaX, deltaY);\n
    \n
    return ($.event.dispatch || $.event.handle).apply(this, args);\n
}\n
\n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2400</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
