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
            <value> <string>ts21897118.22</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>scrollpastend.js</string> </value>
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
  CodeMirror.defineOption("scrollPastEnd", false, function(cm, val, old) {\n
    if (old && old != CodeMirror.Init) {\n
      cm.off("change", onChange);\n
      cm.off("refresh", updateBottomMargin);\n
      cm.display.lineSpace.parentNode.style.paddingBottom = "";\n
      cm.state.scrollPastEndPadding = null;\n
    }\n
    if (val) {\n
      cm.on("change", onChange);\n
      cm.on("refresh", updateBottomMargin);\n
      updateBottomMargin(cm);\n
    }\n
  });\n
\n
  function onChange(cm, change) {\n
    if (CodeMirror.changeEnd(change).line == cm.lastLine())\n
      updateBottomMargin(cm);\n
  }\n
\n
  function updateBottomMargin(cm) {\n
    var padding = "";\n
    if (cm.lineCount() > 1) {\n
      var totalH = cm.display.scroller.clientHeight - 30,\n
          lastLineH = cm.getLineHandle(cm.lastLine()).height;\n
      padding = (totalH - lastLineH) + "px";\n
    }\n
    if (cm.state.scrollPastEndPadding != padding) {\n
      cm.state.scrollPastEndPadding = padding;\n
      cm.display.lineSpace.parentNode.style.paddingBottom = padding;\n
      cm.setSize();\n
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
            <value> <int>1492</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
