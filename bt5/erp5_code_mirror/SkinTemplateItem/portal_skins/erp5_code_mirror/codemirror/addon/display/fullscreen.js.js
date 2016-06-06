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
            <value> <string>ts21897117.34</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>fullscreen.js</string> </value>
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
  CodeMirror.defineOption("fullScreen", false, function(cm, val, old) {\n
    if (old == CodeMirror.Init) old = false;\n
    if (!old == !val) return;\n
    if (val) setFullscreen(cm);\n
    else setNormal(cm);\n
  });\n
\n
  function setFullscreen(cm) {\n
    var wrap = cm.getWrapperElement();\n
    cm.state.fullScreenRestore = {scrollTop: window.pageYOffset, scrollLeft: window.pageXOffset,\n
                                  width: wrap.style.width, height: wrap.style.height};\n
    wrap.style.width = "";\n
    wrap.style.height = "auto";\n
    wrap.className += " CodeMirror-fullscreen";\n
    document.documentElement.style.overflow = "hidden";\n
    cm.refresh();\n
  }\n
\n
  function setNormal(cm) {\n
    var wrap = cm.getWrapperElement();\n
    wrap.className = wrap.className.replace(/\\s*CodeMirror-fullscreen\\b/, "");\n
    document.documentElement.style.overflow = "";\n
    var info = cm.state.fullScreenRestore;\n
    wrap.style.width = info.width; wrap.style.height = info.height;\n
    window.scrollTo(info.scrollLeft, info.scrollTop);\n
    cm.refresh();\n
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
            <value> <int>1494</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
