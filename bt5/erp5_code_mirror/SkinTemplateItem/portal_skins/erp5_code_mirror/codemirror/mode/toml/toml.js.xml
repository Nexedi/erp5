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
            <value> <string>ts21897149.11</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>toml.js</string> </value>
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
CodeMirror.defineMode("toml", function () {\n
  return {\n
    startState: function () {\n
      return {\n
        inString: false,\n
        stringType: "",\n
        lhs: true,\n
        inArray: 0\n
      };\n
    },\n
    token: function (stream, state) {\n
      //check for state changes\n
      if (!state.inString && ((stream.peek() == \'"\') || (stream.peek() == "\'"))) {\n
        state.stringType = stream.peek();\n
        stream.next(); // Skip quote\n
        state.inString = true; // Update state\n
      }\n
      if (stream.sol() && state.inArray === 0) {\n
        state.lhs = true;\n
      }\n
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
      } else if (state.inArray && stream.peek() === \']\') {\n
        stream.next();\n
        state.inArray--;\n
        return \'bracket\';\n
      } else if (state.lhs && stream.peek() === \'[\' && stream.skipTo(\']\')) {\n
        stream.next();//skip closing ]\n
        // array of objects has an extra open & close []\n
        if (stream.peek() === \']\') stream.next();\n
        return "atom";\n
      } else if (stream.peek() === "#") {\n
        stream.skipToEnd();\n
        return "comment";\n
      } else if (stream.eatSpace()) {\n
        return null;\n
      } else if (state.lhs && stream.eatWhile(function (c) { return c != \'=\' && c != \' \'; })) {\n
        return "property";\n
      } else if (state.lhs && stream.peek() === "=") {\n
        stream.next();\n
        state.lhs = false;\n
        return null;\n
      } else if (!state.lhs && stream.match(/^\\d\\d\\d\\d[\\d\\-\\:\\.T]*Z/)) {\n
        return \'atom\'; //date\n
      } else if (!state.lhs && (stream.match(\'true\') || stream.match(\'false\'))) {\n
        return \'atom\';\n
      } else if (!state.lhs && stream.peek() === \'[\') {\n
        state.inArray++;\n
        stream.next();\n
        return \'bracket\';\n
      } else if (!state.lhs && stream.match(/^\\-?\\d+(?:\\.\\d+)?/)) {\n
        return \'number\';\n
      } else if (!stream.eatSpace()) {\n
        stream.next();\n
      }\n
      return null;\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME(\'text/x-toml\', \'toml\');\n
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
            <value> <int>2897</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
