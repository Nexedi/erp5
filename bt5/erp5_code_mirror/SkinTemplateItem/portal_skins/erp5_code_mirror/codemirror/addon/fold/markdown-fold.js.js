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
            <value> <string>ts21897116.73</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>markdown-fold.js</string> </value>
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
"use strict";\n
\n
CodeMirror.registerHelper("fold", "markdown", function(cm, start) {\n
  var maxDepth = 100;\n
\n
  function isHeader(lineNo) {\n
    var tokentype = cm.getTokenTypeAt(CodeMirror.Pos(lineNo, 0));\n
    return tokentype && /\\bheader\\b/.test(tokentype);\n
  }\n
\n
  function headerLevel(lineNo, line, nextLine) {\n
    var match = line && line.match(/^#+/);\n
    if (match && isHeader(lineNo)) return match[0].length;\n
    match = nextLine && nextLine.match(/^[=\\-]+\\s*$/);\n
    if (match && isHeader(lineNo + 1)) return nextLine[0] == "=" ? 1 : 2;\n
    return maxDepth;\n
  }\n
\n
  var firstLine = cm.getLine(start.line), nextLine = cm.getLine(start.line + 1);\n
  var level = headerLevel(start.line, firstLine, nextLine);\n
  if (level === maxDepth) return undefined;\n
\n
  var lastLineNo = cm.lastLine();\n
  var end = start.line, nextNextLine = cm.getLine(end + 2);\n
  while (end < lastLineNo) {\n
    if (headerLevel(end + 1, nextLine, nextNextLine) <= level) break;\n
    ++end;\n
    nextLine = nextNextLine;\n
    nextNextLine = cm.getLine(end + 2);\n
  }\n
\n
  return {\n
    from: CodeMirror.Pos(start.line, firstLine.length),\n
    to: CodeMirror.Pos(end, cm.getLine(end).length)\n
  };\n
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
            <value> <int>1605</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
