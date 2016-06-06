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
            <value> <string>ts21897116.87</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>brace-fold.js</string> </value>
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
CodeMirror.registerHelper("fold", "brace", function(cm, start) {\n
  var line = start.line, lineText = cm.getLine(line);\n
  var startCh, tokenType;\n
\n
  function findOpening(openCh) {\n
    for (var at = start.ch, pass = 0;;) {\n
      var found = at <= 0 ? -1 : lineText.lastIndexOf(openCh, at - 1);\n
      if (found == -1) {\n
        if (pass == 1) break;\n
        pass = 1;\n
        at = lineText.length;\n
        continue;\n
      }\n
      if (pass == 1 && found < start.ch) break;\n
      tokenType = cm.getTokenTypeAt(CodeMirror.Pos(line, found + 1));\n
      if (!/^(comment|string)/.test(tokenType)) return found + 1;\n
      at = found - 1;\n
    }\n
  }\n
\n
  var startToken = "{", endToken = "}", startCh = findOpening("{");\n
  if (startCh == null) {\n
    startToken = "[", endToken = "]";\n
    startCh = findOpening("[");\n
  }\n
\n
  if (startCh == null) return;\n
  var count = 1, lastLine = cm.lastLine(), end, endCh;\n
  outer: for (var i = line; i <= lastLine; ++i) {\n
    var text = cm.getLine(i), pos = i == line ? startCh : 0;\n
    for (;;) {\n
      var nextOpen = text.indexOf(startToken, pos), nextClose = text.indexOf(endToken, pos);\n
      if (nextOpen < 0) nextOpen = text.length;\n
      if (nextClose < 0) nextClose = text.length;\n
      pos = Math.min(nextOpen, nextClose);\n
      if (pos == text.length) break;\n
      if (cm.getTokenTypeAt(CodeMirror.Pos(i, pos + 1)) == tokenType) {\n
        if (pos == nextOpen) ++count;\n
        else if (!--count) { end = i; endCh = pos; break outer; }\n
      }\n
      ++pos;\n
    }\n
  }\n
  if (end == null || line == end && endCh == startCh) return;\n
  return {from: CodeMirror.Pos(line, startCh),\n
          to: CodeMirror.Pos(end, endCh)};\n
});\n
\n
CodeMirror.registerHelper("fold", "import", function(cm, start) {\n
  function hasImport(line) {\n
    if (line < cm.firstLine() || line > cm.lastLine()) return null;\n
    var start = cm.getTokenAt(CodeMirror.Pos(line, 1));\n
    if (!/\\S/.test(start.string)) start = cm.getTokenAt(CodeMirror.Pos(line, start.end + 1));\n
    if (start.type != "keyword" || start.string != "import") return null;\n
    // Now find closing semicolon, return its position\n
    for (var i = line, e = Math.min(cm.lastLine(), line + 10); i <= e; ++i) {\n
      var text = cm.getLine(i), semi = text.indexOf(";");\n
      if (semi != -1) return {startCh: start.end, end: CodeMirror.Pos(i, semi)};\n
    }\n
  }\n
\n
  var start = start.line, has = hasImport(start), prev;\n
  if (!has || hasImport(start - 1) || ((prev = hasImport(start - 2)) && prev.end.line == start - 1))\n
    return null;\n
  for (var end = has.end;;) {\n
    var next = hasImport(end.line + 1);\n
    if (next == null) break;\n
    end = next.end;\n
  }\n
  return {from: cm.clipPos(CodeMirror.Pos(start, has.startCh + 1)), to: end};\n
});\n
\n
CodeMirror.registerHelper("fold", "include", function(cm, start) {\n
  function hasInclude(line) {\n
    if (line < cm.firstLine() || line > cm.lastLine()) return null;\n
    var start = cm.getTokenAt(CodeMirror.Pos(line, 1));\n
    if (!/\\S/.test(start.string)) start = cm.getTokenAt(CodeMirror.Pos(line, start.end + 1));\n
    if (start.type == "meta" && start.string.slice(0, 8) == "#include") return start.start + 8;\n
  }\n
\n
  var start = start.line, has = hasInclude(start);\n
  if (has == null || hasInclude(start - 1) != null) return null;\n
  for (var end = start;;) {\n
    var next = hasInclude(end + 1);\n
    if (next == null) break;\n
    ++end;\n
  }\n
  return {from: CodeMirror.Pos(start, has + 1),\n
          to: cm.clipPos(CodeMirror.Pos(end))};\n
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
            <value> <int>3904</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
