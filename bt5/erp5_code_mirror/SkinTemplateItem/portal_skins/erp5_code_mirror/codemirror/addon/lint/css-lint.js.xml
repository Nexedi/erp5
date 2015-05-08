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
            <value> <string>ts21898625.13</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>css-lint.js</string> </value>
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
// Depends on csslint.js from https://github.com/stubbornella/csslint\n
\n
// declare global: CSSLint\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
"use strict";\n
\n
CodeMirror.registerHelper("lint", "css", function(text) {\n
  var found = [];\n
  if (!window.CSSLint) return found;\n
  var results = CSSLint.verify(text), messages = results.messages, message = null;\n
  for ( var i = 0; i < messages.length; i++) {\n
    message = messages[i];\n
    var startLine = message.line -1, endLine = message.line -1, startCol = message.col -1, endCol = message.col;\n
    found.push({\n
      from: CodeMirror.Pos(startLine, startCol),\n
      to: CodeMirror.Pos(endLine, endCol),\n
      message: message.message,\n
      severity : message.type\n
    });\n
  }\n
  return found;\n
});\n
\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1146</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
