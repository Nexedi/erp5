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
            <value> <string>ts21897141.27</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pegjs.js</string> </value>
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
    mod(require("../../lib/codemirror"), require("../javascript/javascript"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../javascript/javascript"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
"use strict";\n
\n
CodeMirror.defineMode("pegjs", function (config) {\n
  var jsMode = CodeMirror.getMode(config, "javascript");\n
\n
  function identifier(stream) {\n
    return stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*/);\n
  }\n
\n
  return {\n
    startState: function () {\n
      return {\n
        inString: false,\n
        stringType: null,\n
        inComment: false,\n
        inChracterClass: false,\n
        braced: 0,\n
        lhs: true,\n
        localState: null\n
      };\n
    },\n
    token: function (stream, state) {\n
      if (stream)\n
\n
      //check for state changes\n
      if (!state.inString && !state.inComment && ((stream.peek() == \'"\') || (stream.peek() == "\'"))) {\n
        state.stringType = stream.peek();\n
        stream.next(); // Skip quote\n
        state.inString = true; // Update state\n
      }\n
      if (!state.inString && !state.inComment && stream.match(/^\\/\\*/)) {\n
        state.inComment = true;\n
      }\n
\n
      //return state\n
      if (state.inString) {\n
        while (state.inString && !stream.eol()) {\n
          if (stream.peek() === state.stringType) {\n
            stream.next(); // Skip quote\n
            state.inString = false; // Clear flag\n
          } else if (stream.peek() === \'\\\\\') {\n
            stream.next();\n
            stream.next();\n
          } else {\n
            stream.match(/^.[^\\\\\\"\\\']*/);\n
          }\n
        }\n
        return state.lhs ? "property string" : "string"; // Token style\n
      } else if (state.inComment) {\n
        while (state.inComment && !stream.eol()) {\n
          if (stream.match(/\\*\\//)) {\n
            state.inComment = false; // Clear flag\n
          } else {\n
            stream.match(/^.[^\\*]*/);\n
          }\n
        }\n
        return "comment";\n
      } else if (state.inChracterClass) {\n
          while (state.inChracterClass && !stream.eol()) {\n
            if (!(stream.match(/^[^\\]\\\\]+/) || stream.match(/^\\\\./))) {\n
              state.inChracterClass = false;\n
            }\n
          }\n
      } else if (stream.peek() === \'[\') {\n
        stream.next();\n
        state.inChracterClass = true;\n
        return \'bracket\';\n
      } else if (stream.match(/^\\/\\//)) {\n
        stream.skipToEnd();\n
        return "comment";\n
      } else if (state.braced || stream.peek() === \'{\') {\n
        if (state.localState === null) {\n
          state.localState = jsMode.startState();\n
        }\n
        var token = jsMode.token(stream, state.localState);\n
        var text = stream.current();\n
        if (!token) {\n
          for (var i = 0; i < text.length; i++) {\n
            if (text[i] === \'{\') {\n
              state.braced++;\n
            } else if (text[i] === \'}\') {\n
              state.braced--;\n
            }\n
          };\n
        }\n
        return token;\n
      } else if (identifier(stream)) {\n
        if (stream.peek() === \':\') {\n
          return \'variable\';\n
        }\n
        return \'variable-2\';\n
      } else if ([\'[\', \']\', \'(\', \')\'].indexOf(stream.peek()) != -1) {\n
        stream.next();\n
        return \'bracket\';\n
      } else if (!stream.eatSpace()) {\n
        stream.next();\n
      }\n
      return null;\n
    }\n
  };\n
}, "javascript");\n
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
            <value> <int>3562</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
