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
            <value> <string>ts44314544.61</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.mousewheel.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*! Copyright (c) 2013 Brandon Aaron (http://brandon.aaron.sh)\n
 * Licensed under the MIT License (LICENSE.txt).\n
 *\n
 * Version: 3.1.9\n
 *\n
 * Requires: jQuery 1.2.2+\n
 */\n
\n
(function (factory) {\n
    if ( typeof define === \'function\' && define.amd ) {\n
        // AMD. Register as an anonymous module.\n
        define([\'jquery\'], factory);\n
    } else if (typeof exports === \'object\') {\n
        // Node/CommonJS style for Browserify\n
        module.exports = factory;\n
    } else {\n
        // Browser globals\n
        factory(jQuery);\n
    }\n
}(function ($) {\n
\n
    var toFix  = [\'wheel\', \'mousewheel\', \'DOMMouseScroll\', \'MozMousePixelScroll\'],\n
        toBind = ( \'onwheel\' in document || document.documentMode >= 9 ) ?\n
                    [\'wheel\'] : [\'mousewheel\', \'DomMouseScroll\', \'MozMousePixelScroll\'],\n
        slice  = Array.prototype.slice,\n
        nullLowestDeltaTimeout, lowestDelta;\n
\n
    if ( $.event.fixHooks ) {\n
        for ( var i = toFix.length; i; ) {\n
            $.event.fixHooks[ toFix[--i] ] = $.event.mouseHooks;\n
        }\n
    }\n
\n
    var special = $.event.special.mousewheel = {\n
        version: \'3.1.9\',\n
\n
        setup: function() {\n
            if ( this.addEventListener ) {\n
                for ( var i = toBind.length; i; ) {\n
                    this.addEventListener( toBind[--i], handler, false );\n
                }\n
            } else {\n
                this.onmousewheel = handler;\n
            }\n
            // Store the line height and page height for this particular element\n
            $.data(this, \'mousewheel-line-height\', special.getLineHeight(this));\n
            $.data(this, \'mousewheel-page-height\', special.getPageHeight(this));\n
        },\n
\n
        teardown: function() {\n
            if ( this.removeEventListener ) {\n
                for ( var i = toBind.length; i; ) {\n
                    this.removeEventListener( toBind[--i], handler, false );\n
                }\n
            } else {\n
                this.onmousewheel = null;\n
            }\n
        },\n
\n
        getLineHeight: function(elem) {\n
            return parseInt($(elem)[\'offsetParent\' in $.fn ? \'offsetParent\' : \'parent\']().css(\'fontSize\'), 10);\n
        },\n
\n
        getPageHeight: function(elem) {\n
            return $(elem).height();\n
        },\n
\n
        settings: {\n
            adjustOldDeltas: true\n
        }\n
    };\n
\n
    $.fn.extend({\n
        mousewheel: function(fn) {\n
            return fn ? this.bind(\'mousewheel\', fn) : this.trigger(\'mousewheel\');\n
        },\n
\n
        unmousewheel: function(fn) {\n
            return this.unbind(\'mousewheel\', fn);\n
        }\n
    });\n
\n
\n
    function handler(event) {\n
        var orgEvent   = event || window.event,\n
            args       = slice.call(arguments, 1),\n
            delta      = 0,\n
            deltaX     = 0,\n
            deltaY     = 0,\n
            absDelta   = 0;\n
        event = $.event.fix(orgEvent);\n
        event.type = \'mousewheel\';\n
\n
        // Old school scrollwheel delta\n
        if ( \'detail\'      in orgEvent ) { deltaY = orgEvent.detail * -1;      }\n
        if ( \'wheelDelta\'  in orgEvent ) { deltaY = orgEvent.wheelDelta;       }\n
        if ( \'wheelDeltaY\' in orgEvent ) { deltaY = orgEvent.wheelDeltaY;      }\n
        if ( \'wheelDeltaX\' in orgEvent ) { deltaX = orgEvent.wheelDeltaX * -1; }\n
\n
        // Firefox < 17 horizontal scrolling related to DOMMouseScroll event\n
        if ( \'axis\' in orgEvent && orgEvent.axis === orgEvent.HORIZONTAL_AXIS ) {\n
            deltaX = deltaY * -1;\n
            deltaY = 0;\n
        }\n
\n
        // Set delta to be deltaY or deltaX if deltaY is 0 for backwards compatabilitiy\n
        delta = deltaY === 0 ? deltaX : deltaY;\n
\n
        // New school wheel delta (wheel event)\n
        if ( \'deltaY\' in orgEvent ) {\n
            deltaY = orgEvent.deltaY * -1;\n
            delta  = deltaY;\n
        }\n
        if ( \'deltaX\' in orgEvent ) {\n
            deltaX = orgEvent.deltaX;\n
            if ( deltaY === 0 ) { delta  = deltaX * -1; }\n
        }\n
\n
        // No change actually happened, no reason to go any further\n
        if ( deltaY === 0 && deltaX === 0 ) { return; }\n
\n
        // Need to convert lines and pages to pixels if we aren\'t already in pixels\n
        // There are three delta modes:\n
        //   * deltaMode 0 is by pixels, nothing to do\n
        //   * deltaMode 1 is by lines\n
        //   * deltaMode 2 is by pages\n
        if ( orgEvent.deltaMode === 1 ) {\n
            var lineHeight = $.data(this, \'mousewheel-line-height\');\n
            delta  *= lineHeight;\n
            deltaY *= lineHeight;\n
            deltaX *= lineHeight;\n
        } else if ( orgEvent.deltaMode === 2 ) {\n
            var pageHeight = $.data(this, \'mousewheel-page-height\');\n
            delta  *= pageHeight;\n
            deltaY *= pageHeight;\n
            deltaX *= pageHeight;\n
        }\n
\n
        // Store lowest absolute delta to normalize the delta values\n
        absDelta = Math.max( Math.abs(deltaY), Math.abs(deltaX) );\n
\n
        if ( !lowestDelta || absDelta < lowestDelta ) {\n
            lowestDelta = absDelta;\n
\n
            // Adjust older deltas if necessary\n
            if ( shouldAdjustOldDeltas(orgEvent, absDelta) ) {\n
                lowestDelta /= 40;\n
            }\n
        }\n
\n
        // Adjust older deltas if necessary\n
        if ( shouldAdjustOldDeltas(orgEvent, absDelta) ) {\n
            // Divide all the things by 40!\n
            delta  /= 40;\n
            deltaX /= 40;\n
            deltaY /= 40;\n
        }\n
\n
        // Get a whole, normalized value for the deltas\n
        delta  = Math[ delta  >= 1 ? \'floor\' : \'ceil\' ](delta  / lowestDelta);\n
        deltaX = Math[ deltaX >= 1 ? \'floor\' : \'ceil\' ](deltaX / lowestDelta);\n
        deltaY = Math[ deltaY >= 1 ? \'floor\' : \'ceil\' ](deltaY / lowestDelta);\n
\n
        // Add information to the event object\n
        event.deltaX = deltaX;\n
        event.deltaY = deltaY;\n
        event.deltaFactor = lowestDelta;\n
        // Go ahead and set deltaMode to 0 since we converted to pixels\n
        // Although this is a little odd since we overwrite the deltaX/Y\n
        // properties with normalized deltas.\n
        event.deltaMode = 0;\n
\n
        // Add event and delta to the front of the arguments\n
        args.unshift(event, delta, deltaX, deltaY);\n
\n
        // Clearout lowestDelta after sometime to better\n
        // handle multiple device types that give different\n
        // a different lowestDelta\n
        // Ex: trackpad = 3 and mouse wheel = 120\n
        if (nullLowestDeltaTimeout) { clearTimeout(nullLowestDeltaTimeout); }\n
        nullLowestDeltaTimeout = setTimeout(nullLowestDelta, 200);\n
\n
        return ($.event.dispatch || $.event.handle).apply(this, args);\n
    }\n
\n
    function nullLowestDelta() {\n
        lowestDelta = null;\n
    }\n
\n
    function shouldAdjustOldDeltas(orgEvent, absDelta) {\n
        // If this is an older event and the delta is divisable by 120,\n
        // then we are assuming that the browser is treating this as an\n
        // older mouse wheel event and that we should divide the deltas\n
        // by 40 to try and get a more usable deltaFactor.\n
        // Side note, this actually impacts the reported scroll distance\n
        // in older browsers and can cause scrolling to be slower than native.\n
        // Turn this off by setting $.event.special.mousewheel.settings.adjustOldDeltas to false.\n
        return special.settings.adjustOldDeltas && orgEvent.type === \'mousewheel\' && absDelta % 120 === 0;\n
    }\n
\n
}));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>7349</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
