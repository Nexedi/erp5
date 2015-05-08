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
            <value> <string>ts21897146.81</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>diff.js</string> </value>
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
CodeMirror.defineMode("diff", function() {\n
\n
  var TOKEN_NAMES = {\n
    \'+\': \'positive\',\n
    \'-\': \'negative\',\n
    \'@\': \'meta\'\n
  };\n
\n
  return {\n
    token: function(stream) {\n
      var tw_pos = stream.string.search(/[\\t ]+?$/);\n
\n
      if (!stream.sol() || tw_pos === 0) {\n
        stream.skipToEnd();\n
        return ("error " + (\n
          TOKEN_NAMES[stream.string.charAt(0)] || \'\')).replace(/ $/, \'\');\n
      }\n
\n
      var token_name = TOKEN_NAMES[stream.peek()] || stream.skipToEnd();\n
\n
      if (tw_pos === -1) {\n
        stream.skipToEnd();\n
      } else {\n
        stream.pos = tw_pos;\n
      }\n
\n
      return token_name;\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-diff", "diff");\n
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
            <value> <int>1138</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
