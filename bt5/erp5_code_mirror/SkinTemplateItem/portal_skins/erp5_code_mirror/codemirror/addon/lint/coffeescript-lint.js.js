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
            <value> <string>ts21897121.01</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>coffeescript-lint.js</string> </value>
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
// Depends on coffeelint.js from http://www.coffeelint.org/js/coffeelint.js\n
\n
// declare global: coffeelint\n
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
CodeMirror.registerHelper("lint", "coffeescript", function(text) {\n
  var found = [];\n
  var parseError = function(err) {\n
    var loc = err.lineNumber;\n
    found.push({from: CodeMirror.Pos(loc-1, 0),\n
                to: CodeMirror.Pos(loc, 0),\n
                severity: err.level,\n
                message: err.message});\n
  };\n
  try {\n
    var res = coffeelint.lint(text);\n
    for(var i = 0; i < res.length; i++) {\n
      parseError(res[i]);\n
    }\n
  } catch(e) {\n
    found.push({from: CodeMirror.Pos(e.location.first_line, 0),\n
                to: CodeMirror.Pos(e.location.last_line, e.location.last_column),\n
                severity: \'error\',\n
                message: e.message});\n
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
            <value> <int>1270</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
