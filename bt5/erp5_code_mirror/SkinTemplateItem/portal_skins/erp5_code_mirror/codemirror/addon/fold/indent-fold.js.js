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
            <value> <string>ts21897116.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>indent-fold.js</string> </value>
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
CodeMirror.registerHelper("fold", "indent", function(cm, start) {\n
  var tabSize = cm.getOption("tabSize"), firstLine = cm.getLine(start.line);\n
  if (!/\\S/.test(firstLine)) return;\n
  var getIndent = function(line) {\n
    return CodeMirror.countColumn(line, null, tabSize);\n
  };\n
  var myIndent = getIndent(firstLine);\n
  var lastLineInFold = null;\n
  // Go through lines until we find a line that definitely doesn\'t belong in\n
  // the block we\'re folding, or to the end.\n
  for (var i = start.line + 1, end = cm.lastLine(); i <= end; ++i) {\n
    var curLine = cm.getLine(i);\n
    var curIndent = getIndent(curLine);\n
    if (curIndent > myIndent) {\n
      // Lines with a greater indent are considered part of the block.\n
      lastLineInFold = i;\n
    } else if (!/\\S/.test(curLine)) {\n
      // Empty lines might be breaks within the block we\'re trying to fold.\n
    } else {\n
      // A non-empty line at an indent equal to or less than ours marks the\n
      // start of another block.\n
      break;\n
    }\n
  }\n
  if (lastLineInFold) return {\n
    from: CodeMirror.Pos(start.line, firstLine.length),\n
    to: CodeMirror.Pos(lastLineInFold, cm.getLine(lastLineInFold).length)\n
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
            <value> <int>1627</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
