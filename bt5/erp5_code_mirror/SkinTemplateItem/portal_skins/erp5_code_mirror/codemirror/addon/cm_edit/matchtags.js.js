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
            <value> <string>ts21897296.03</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>matchtags.js</string> </value>
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
    mod(require("../../lib/codemirror"), require("../fold/xml-fold"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../fold/xml-fold"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  "use strict";\n
\n
  CodeMirror.defineOption("matchTags", false, function(cm, val, old) {\n
    if (old && old != CodeMirror.Init) {\n
      cm.off("cursorActivity", doMatchTags);\n
      cm.off("viewportChange", maybeUpdateMatch);\n
      clear(cm);\n
    }\n
    if (val) {\n
      cm.state.matchBothTags = typeof val == "object" && val.bothTags;\n
      cm.on("cursorActivity", doMatchTags);\n
      cm.on("viewportChange", maybeUpdateMatch);\n
      doMatchTags(cm);\n
    }\n
  });\n
\n
  function clear(cm) {\n
    if (cm.state.tagHit) cm.state.tagHit.clear();\n
    if (cm.state.tagOther) cm.state.tagOther.clear();\n
    cm.state.tagHit = cm.state.tagOther = null;\n
  }\n
\n
  function doMatchTags(cm) {\n
    cm.state.failedTagMatch = false;\n
    cm.operation(function() {\n
      clear(cm);\n
      if (cm.somethingSelected()) return;\n
      var cur = cm.getCursor(), range = cm.getViewport();\n
      range.from = Math.min(range.from, cur.line); range.to = Math.max(cur.line + 1, range.to);\n
      var match = CodeMirror.findMatchingTag(cm, cur, range);\n
      if (!match) return;\n
      if (cm.state.matchBothTags) {\n
        var hit = match.at == "open" ? match.open : match.close;\n
        if (hit) cm.state.tagHit = cm.markText(hit.from, hit.to, {className: "CodeMirror-matchingtag"});\n
      }\n
      var other = match.at == "close" ? match.open : match.close;\n
      if (other)\n
        cm.state.tagOther = cm.markText(other.from, other.to, {className: "CodeMirror-matchingtag"});\n
      else\n
        cm.state.failedTagMatch = true;\n
    });\n
  }\n
\n
  function maybeUpdateMatch(cm) {\n
    if (cm.state.failedTagMatch) doMatchTags(cm);\n
  }\n
\n
  CodeMirror.commands.toMatchingTag = function(cm) {\n
    var found = CodeMirror.findMatchingTag(cm, cm.getCursor());\n
    if (found) {\n
      var other = found.at == "close" ? found.open : found.close;\n
      if (other) cm.extendSelection(other.to, other.from);\n
    }\n
  };\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2355</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
