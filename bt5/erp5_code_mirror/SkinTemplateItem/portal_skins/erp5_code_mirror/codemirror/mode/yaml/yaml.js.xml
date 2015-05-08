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
            <value> <string>ts21897141.76</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>yaml.js</string> </value>
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
CodeMirror.defineMode("yaml", function() {\n
\n
  var cons = [\'true\', \'false\', \'on\', \'off\', \'yes\', \'no\'];\n
  var keywordRegex = new RegExp("\\\\b(("+cons.join(")|(")+"))$", \'i\');\n
\n
  return {\n
    token: function(stream, state) {\n
      var ch = stream.peek();\n
      var esc = state.escaped;\n
      state.escaped = false;\n
      /* comments */\n
      if (ch == "#" && (stream.pos == 0 || /\\s/.test(stream.string.charAt(stream.pos - 1)))) {\n
        stream.skipToEnd();\n
        return "comment";\n
      }\n
\n
      if (stream.match(/^(\'([^\']|\\\\.)*\'?|"([^"]|\\\\.)*"?)/))\n
        return "string";\n
\n
      if (state.literal && stream.indentation() > state.keyCol) {\n
        stream.skipToEnd(); return "string";\n
      } else if (state.literal) { state.literal = false; }\n
      if (stream.sol()) {\n
        state.keyCol = 0;\n
        state.pair = false;\n
        state.pairStart = false;\n
        /* document start */\n
        if(stream.match(/---/)) { return "def"; }\n
        /* document end */\n
        if (stream.match(/\\.\\.\\./)) { return "def"; }\n
        /* array list item */\n
        if (stream.match(/\\s*-\\s+/)) { return \'meta\'; }\n
      }\n
      /* inline pairs/lists */\n
      if (stream.match(/^(\\{|\\}|\\[|\\])/)) {\n
        if (ch == \'{\')\n
          state.inlinePairs++;\n
        else if (ch == \'}\')\n
          state.inlinePairs--;\n
        else if (ch == \'[\')\n
          state.inlineList++;\n
        else\n
          state.inlineList--;\n
        return \'meta\';\n
      }\n
\n
      /* list seperator */\n
      if (state.inlineList > 0 && !esc && ch == \',\') {\n
        stream.next();\n
        return \'meta\';\n
      }\n
      /* pairs seperator */\n
      if (state.inlinePairs > 0 && !esc && ch == \',\') {\n
        state.keyCol = 0;\n
        state.pair = false;\n
        state.pairStart = false;\n
        stream.next();\n
        return \'meta\';\n
      }\n
\n
      /* start of value of a pair */\n
      if (state.pairStart) {\n
        /* block literals */\n
        if (stream.match(/^\\s*(\\||\\>)\\s*/)) { state.literal = true; return \'meta\'; };\n
        /* references */\n
        if (stream.match(/^\\s*(\\&|\\*)[a-z0-9\\._-]+\\b/i)) { return \'variable-2\'; }\n
        /* numbers */\n
        if (state.inlinePairs == 0 && stream.match(/^\\s*-?[0-9\\.\\,]+\\s?$/)) { return \'number\'; }\n
        if (state.inlinePairs > 0 && stream.match(/^\\s*-?[0-9\\.\\,]+\\s?(?=(,|}))/)) { return \'number\'; }\n
        /* keywords */\n
        if (stream.match(keywordRegex)) { return \'keyword\'; }\n
      }\n
\n
      /* pairs (associative arrays) -> key */\n
      if (!state.pair && stream.match(/^\\s*(?:[,\\[\\]{}&*!|>\'"%@`][^\\s\'":]|[^,\\[\\]{}#&*!|>\'"%@`])[^#]*?(?=\\s*:($|\\s))/)) {\n
        state.pair = true;\n
        state.keyCol = stream.indentation();\n
        return "atom";\n
      }\n
      if (state.pair && stream.match(/^:\\s*/)) { state.pairStart = true; return \'meta\'; }\n
\n
      /* nothing found, continue */\n
      state.pairStart = false;\n
      state.escaped = (ch == \'\\\\\');\n
      stream.next();\n
      return null;\n
    },\n
    startState: function() {\n
      return {\n
        pair: false,\n
        pairStart: false,\n
        keyCol: 0,\n
        inlinePairs: 0,\n
        inlineList: 0,\n
        literal: false,\n
        escaped: false\n
      };\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-yaml", "yaml");\n
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
            <value> <int>3649</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
