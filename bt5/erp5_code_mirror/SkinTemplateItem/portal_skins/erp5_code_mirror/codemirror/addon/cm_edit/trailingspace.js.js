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
            <value> <string>ts21897285.4</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>trailingspace.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  CodeMirror.defineOption("showTrailingSpace", false, function(cm, val, prev) {\n
    if (prev == CodeMirror.Init) prev = false;\n
    if (prev && !val)\n
      cm.removeOverlay("trailingspace");\n
    else if (!prev && val)\n
      cm.addOverlay({\n
        token: function(stream) {\n
          for (var l = stream.string.length, i = l; i && /\\s/.test(stream.string.charAt(i - 1)); --i) {}\n
          if (i > stream.pos) { stream.pos = i; return null; }\n
          stream.pos = l;\n
          return "trailingspace";\n
        },\n
        name: "trailingspace"\n
      });\n
  });\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1003</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
