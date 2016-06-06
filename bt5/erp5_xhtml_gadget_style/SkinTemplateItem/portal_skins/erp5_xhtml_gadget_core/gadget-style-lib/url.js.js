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
            <value> <string>ts62728569.21</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>url.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * url.js v1.0.0\n
 *\n
 * Copyright 2012, Romain Courteaud\n
 * Dual licensed under the MIT or GPL Version 2 licenses.\n
 *\n
 * Date: Mon Jul 16 2012\n
 */\n
"use strict";\n
(function (window, $) {\n
\n
  var hashchangeinitialized = false,\n
    previousurl,\n
    currentcallback,\n
    getRawHash = function () {\n
      return window.location.toString().split(\'#\')[1];\n
    },\n
    callbackwrapper = function () {\n
      if (previousurl !== window.location.hash) {\n
        previousurl = window.location.hash;\n
        if (currentcallback !== undefined) {\n
          currentcallback();\n
        }\n
      }\n
    },\n
    timeoutwrapper = function () {\n
      callbackwrapper();\n
      window.setTimeout(timeoutwrapper, 500);\n
    };\n
\n
  function UrlHandler() {}\n
\n
  UrlHandler.prototype = {\n
    \'generateUrl\': function (path, options) {\n
      var pathhash,\n
        hash = \'#\',\n
        key;\n
      if (path !== undefined) {\n
        hash += encodeURIComponent(path);\n
      }\n
      hash = hash.replace(/%2F/g, \'/\');\n
      pathhash = hash;\n
      for (key in options) {\n
        if (options.hasOwnProperty(key)) {\n
          if (hash === pathhash) {\n
            hash = hash + \'?\';\n
          } else {\n
            hash = hash + \'&\';\n
          }\n
          hash += encodeURIComponent(key) +\n
            \'=\' + encodeURIComponent(options[key]);\n
        }\n
      }\n
      return hash;\n
    },\n
\n
    \'go\': function (path, options) {\n
      window.location.hash = this.generateUrl(path, options);\n
    },\n
\n
    \'redirect\': function (path, options) {\n
      var host = window.location.protocol + \'//\' +\n
                 window.location.host +\n
                 window.location.pathname +\n
                 window.location.search;\n
      window.location.replace(host + this.generateUrl(path, options));\n
//       window.location.replace(window.location.href.replace(/#.*/, ""));\n
    },\n
\n
    \'getPath\': function () {\n
      var hash = getRawHash(),\n
        result = \'\';\n
      if (hash !== undefined) {\n
        result = decodeURIComponent(hash.split(\'?\')[0]);\n
      }\n
      return result;\n
    },\n
\n
    \'getOptions\': function () {\n
      var options = {},\n
        hash = getRawHash(),\n
        subhashes,\n
        subhash,\n
        index,\n
        keyvalue;\n
      if (hash !== undefined) {\n
        hash = hash.split(\'?\')[1];\n
        if (hash !== undefined) {\n
          subhashes = hash.split(\'&\');\n
          for (index in subhashes) {\n
            if (subhashes.hasOwnProperty(index)) {\n
              subhash = subhashes[index];\n
              if (subhash !== \'\') {\n
                keyvalue = subhash.split(\'=\');\n
                if (keyvalue.length === 2) {\n
                  options[decodeURIComponent(keyvalue[0])] =\n
                    decodeURIComponent(keyvalue[1]);\n
                }\n
              }\n
            }\n
          }\n
        }\n
      }\n
      return options;\n
    },\n
\n
    \'onhashchange\': function (callback) {\n
      previousurl = undefined;\n
      currentcallback = callback;\n
\n
      if (!hashchangeinitialized) {\n
        if (window.onhashchange !== undefined) {\n
          $(window).bind(\'hashchange\', callbackwrapper);\n
          window.setTimeout(callbackwrapper);\n
        } else {\n
          timeoutwrapper();\n
        }\n
        hashchangeinitialized = true;\n
      }\n
    },\n
  };\n
\n
  // Expose to the global object\n
  $.url = new UrlHandler();\n
\n
}(window, jQuery));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3293</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>url.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
