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
            <value> <string>ts21897119.62</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>mark-selection.js</string> </value>
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
// Because sometimes you need to mark the selected *text*.\n
//\n
// Adds an option \'styleSelectedText\' which, when enabled, gives\n
// selected text the CSS class given as option value, or\n
// "CodeMirror-selectedtext" when the value is not a string.\n
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
  CodeMirror.defineOption("styleSelectedText", false, function(cm, val, old) {\n
    var prev = old && old != CodeMirror.Init;\n
    if (val && !prev) {\n
      cm.state.markedSelection = [];\n
      cm.state.markedSelectionStyle = typeof val == "string" ? val : "CodeMirror-selectedtext";\n
      reset(cm);\n
      cm.on("cursorActivity", onCursorActivity);\n
      cm.on("change", onChange);\n
    } else if (!val && prev) {\n
      cm.off("cursorActivity", onCursorActivity);\n
      cm.off("change", onChange);\n
      clear(cm);\n
      cm.state.markedSelection = cm.state.markedSelectionStyle = null;\n
    }\n
  });\n
\n
  function onCursorActivity(cm) {\n
    cm.operation(function() { update(cm); });\n
  }\n
\n
  function onChange(cm) {\n
    if (cm.state.markedSelection.length)\n
      cm.operation(function() { clear(cm); });\n
  }\n
\n
  var CHUNK_SIZE = 8;\n
  var Pos = CodeMirror.Pos;\n
  var cmp = CodeMirror.cmpPos;\n
\n
  function coverRange(cm, from, to, addAt) {\n
    if (cmp(from, to) == 0) return;\n
    var array = cm.state.markedSelection;\n
    var cls = cm.state.markedSelectionStyle;\n
    for (var line = from.line;;) {\n
      var start = line == from.line ? from : Pos(line, 0);\n
      var endLine = line + CHUNK_SIZE, atEnd = endLine >= to.line;\n
      var end = atEnd ? to : Pos(endLine, 0);\n
      var mark = cm.markText(start, end, {className: cls});\n
      if (addAt == null) array.push(mark);\n
      else array.splice(addAt++, 0, mark);\n
      if (atEnd) break;\n
      line = endLine;\n
    }\n
  }\n
\n
  function clear(cm) {\n
    var array = cm.state.markedSelection;\n
    for (var i = 0; i < array.length; ++i) array[i].clear();\n
    array.length = 0;\n
  }\n
\n
  function reset(cm) {\n
    clear(cm);\n
    var ranges = cm.listSelections();\n
    for (var i = 0; i < ranges.length; i++)\n
      coverRange(cm, ranges[i].from(), ranges[i].to());\n
  }\n
\n
  function update(cm) {\n
    if (!cm.somethingSelected()) return clear(cm);\n
    if (cm.listSelections().length > 1) return reset(cm);\n
\n
    var from = cm.getCursor("start"), to = cm.getCursor("end");\n
\n
    var array = cm.state.markedSelection;\n
    if (!array.length) return coverRange(cm, from, to);\n
\n
    var coverStart = array[0].find(), coverEnd = array[array.length - 1].find();\n
    if (!coverStart || !coverEnd || to.line - from.line < CHUNK_SIZE ||\n
        cmp(from, coverEnd.to) >= 0 || cmp(to, coverStart.from) <= 0)\n
      return reset(cm);\n
\n
    while (cmp(from, coverStart.from) > 0) {\n
      array.shift().clear();\n
      coverStart = array[0].find();\n
    }\n
    if (cmp(from, coverStart.from) < 0) {\n
      if (coverStart.to.line - from.line < CHUNK_SIZE) {\n
        array.shift().clear();\n
        coverRange(cm, from, coverStart.to, 0);\n
      } else {\n
        coverRange(cm, from, coverStart.from, 0);\n
      }\n
    }\n
\n
    while (cmp(to, coverEnd.to) < 0) {\n
      array.pop().clear();\n
      coverEnd = array[array.length - 1].find();\n
    }\n
    if (cmp(to, coverEnd.to) > 0) {\n
      if (to.line - coverEnd.from.line < CHUNK_SIZE) {\n
        array.pop().clear();\n
        coverRange(cm, coverEnd.from, to);\n
      } else {\n
        coverRange(cm, coverEnd.to, to);\n
      }\n
    }\n
  }\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3781</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
