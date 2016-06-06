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
            <value> <string>ts21897122.18</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>colorize.js</string> </value>
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
    mod(require("../../lib/codemirror"), require("./runmode"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "./runmode"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  "use strict";\n
\n
  var isBlock = /^(p|li|div|h\\\\d|pre|blockquote|td)$/;\n
\n
  function textContent(node, out) {\n
    if (node.nodeType == 3) return out.push(node.nodeValue);\n
    for (var ch = node.firstChild; ch; ch = ch.nextSibling) {\n
      textContent(ch, out);\n
      if (isBlock.test(node.nodeType)) out.push("\\n");\n
    }\n
  }\n
\n
  CodeMirror.colorize = function(collection, defaultMode) {\n
    if (!collection) collection = document.body.getElementsByTagName("pre");\n
\n
    for (var i = 0; i < collection.length; ++i) {\n
      var node = collection[i];\n
      var mode = node.getAttribute("data-lang") || defaultMode;\n
      if (!mode) continue;\n
\n
      var text = [];\n
      textContent(node, text);\n
      node.innerHTML = "";\n
      CodeMirror.runMode(text.join(""), mode, node);\n
\n
      node.className += " cm-s-default";\n
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
            <value> <int>1303</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
