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
            <value> <string>ts21897115.91</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>loadmode.js</string> </value>
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
    mod(require("../../lib/codemirror"), "cjs");\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror"], function(CM) { mod(CM, "amd"); });\n
  else // Plain browser env\n
    mod(CodeMirror, "plain");\n
})(function(CodeMirror, env) {\n
  if (!CodeMirror.modeURL) CodeMirror.modeURL = "../mode/%N/%N.js";\n
\n
  var loading = {};\n
  function splitCallback(cont, n) {\n
    var countDown = n;\n
    return function() { if (--countDown == 0) cont(); };\n
  }\n
  function ensureDeps(mode, cont) {\n
    var deps = CodeMirror.modes[mode].dependencies;\n
    if (!deps) return cont();\n
    var missing = [];\n
    for (var i = 0; i < deps.length; ++i) {\n
      if (!CodeMirror.modes.hasOwnProperty(deps[i]))\n
        missing.push(deps[i]);\n
    }\n
    if (!missing.length) return cont();\n
    var split = splitCallback(cont, missing.length);\n
    for (var i = 0; i < missing.length; ++i)\n
      CodeMirror.requireMode(missing[i], split);\n
  }\n
\n
  CodeMirror.requireMode = function(mode, cont) {\n
    if (typeof mode != "string") mode = mode.name;\n
    if (CodeMirror.modes.hasOwnProperty(mode)) return ensureDeps(mode, cont);\n
    if (loading.hasOwnProperty(mode)) return loading[mode].push(cont);\n
\n
    var file = CodeMirror.modeURL.replace(/%N/g, mode);\n
    if (env == "plain") {\n
      var script = document.createElement("script");\n
      script.src = file;\n
      var others = document.getElementsByTagName("script")[0];\n
      var list = loading[mode] = [cont];\n
      CodeMirror.on(script, "load", function() {\n
        ensureDeps(mode, function() {\n
          for (var i = 0; i < list.length; ++i) list[i]();\n
        });\n
      });\n
      others.parentNode.insertBefore(script, others);\n
    } else if (env == "cjs") {\n
      require(file);\n
      cont();\n
    } else if (env == "amd") {\n
      requirejs([file], cont);\n
    }\n
  };\n
\n
  CodeMirror.autoLoadMode = function(instance, mode) {\n
    if (!CodeMirror.modes.hasOwnProperty(mode))\n
      CodeMirror.requireMode(mode, function() {\n
        instance.setOption("mode", instance.getOption("mode"));\n
      });\n
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
            <value> <int>2277</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
