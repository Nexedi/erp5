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
            <value> <string>ts31681349.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>mixin_promise.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/// FIXME: merge into the gadget using these utilities and remove this file\n
\n
/*global RSVP, FileReader */\n
/*jslint unparam: true */\n
(function(window, RSVP, FileReader) {\n
    "use strict";\n
    window.loopEventListener = function(target, type, useCapture, callback, allowDefault) {\n
        //////////////////////////\n
        // Infinite event listener (promise is never resolved)\n
        // eventListener is removed when promise is cancelled/rejected\n
        //////////////////////////\n
        var handle_event_callback, callback_promise;\n
        function cancelResolver() {\n
            if (callback_promise !== undefined && typeof callback_promise.cancel === "function") {\n
                callback_promise.cancel();\n
            }\n
        }\n
        function canceller() {\n
            if (handle_event_callback !== undefined) {\n
                target.removeEventListener(type, handle_event_callback, useCapture);\n
            }\n
            cancelResolver();\n
        }\n
        function itsANonResolvableTrap(resolve, reject) {\n
            handle_event_callback = function(evt) {\n
                evt.stopPropagation();\n
                if (allowDefault !== true) {\n
                    evt.preventDefault();\n
                }\n
                cancelResolver();\n
                callback_promise = new RSVP.Queue().push(function() {\n
                    return callback(evt);\n
                }).push(undefined, function(error) {\n
                    if (!(error instanceof RSVP.CancellationError)) {\n
                        canceller();\n
                        reject(error);\n
                    }\n
                });\n
            };\n
            target.addEventListener(type, handle_event_callback, useCapture);\n
        }\n
        return new RSVP.Promise(itsANonResolvableTrap, canceller);\n
    };\n
    window.promiseEventListener = function(target, type, useCapture) {\n
        //////////////////////////\n
        // Resolve the promise as soon as the event is triggered\n
        // eventListener is removed when promise is cancelled/resolved/rejected\n
        //////////////////////////\n
        var handle_event_callback;\n
        function canceller() {\n
            target.removeEventListener(type, handle_event_callback, useCapture);\n
        }\n
        function resolver(resolve) {\n
            handle_event_callback = function(evt) {\n
                canceller();\n
                evt.stopPropagation();\n
                evt.preventDefault();\n
                resolve(evt);\n
                return false;\n
            };\n
            target.addEventListener(type, handle_event_callback, useCapture);\n
        }\n
        return new RSVP.Promise(resolver, canceller);\n
    };\n
    window.promiseReadAsText = function(file) {\n
        return new RSVP.Promise(function(resolve, reject) {\n
            var reader = new FileReader();\n
            reader.onload = function(evt) {\n
                resolve(evt.target.result);\n
            };\n
            reader.onerror = function(evt) {\n
                reject(evt);\n
            };\n
            reader.readAsText(file);\n
        });\n
    };\n
})(window, RSVP, FileReader);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3072</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
