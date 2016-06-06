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
            <value> <string>ts21897140.19</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>http.js</string> </value>
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
CodeMirror.defineMode("http", function() {\n
  function failFirstLine(stream, state) {\n
    stream.skipToEnd();\n
    state.cur = header;\n
    return "error";\n
  }\n
\n
  function start(stream, state) {\n
    if (stream.match(/^HTTP\\/\\d\\.\\d/)) {\n
      state.cur = responseStatusCode;\n
      return "keyword";\n
    } else if (stream.match(/^[A-Z]+/) && /[ \\t]/.test(stream.peek())) {\n
      state.cur = requestPath;\n
      return "keyword";\n
    } else {\n
      return failFirstLine(stream, state);\n
    }\n
  }\n
\n
  function responseStatusCode(stream, state) {\n
    var code = stream.match(/^\\d+/);\n
    if (!code) return failFirstLine(stream, state);\n
\n
    state.cur = responseStatusText;\n
    var status = Number(code[0]);\n
    if (status >= 100 && status < 200) {\n
      return "positive informational";\n
    } else if (status >= 200 && status < 300) {\n
      return "positive success";\n
    } else if (status >= 300 && status < 400) {\n
      return "positive redirect";\n
    } else if (status >= 400 && status < 500) {\n
      return "negative client-error";\n
    } else if (status >= 500 && status < 600) {\n
      return "negative server-error";\n
    } else {\n
      return "error";\n
    }\n
  }\n
\n
  function responseStatusText(stream, state) {\n
    stream.skipToEnd();\n
    state.cur = header;\n
    return null;\n
  }\n
\n
  function requestPath(stream, state) {\n
    stream.eatWhile(/\\S/);\n
    state.cur = requestProtocol;\n
    return "string-2";\n
  }\n
\n
  function requestProtocol(stream, state) {\n
    if (stream.match(/^HTTP\\/\\d\\.\\d$/)) {\n
      state.cur = header;\n
      return "keyword";\n
    } else {\n
      return failFirstLine(stream, state);\n
    }\n
  }\n
\n
  function header(stream) {\n
    if (stream.sol() && !stream.eat(/[ \\t]/)) {\n
      if (stream.match(/^.*?:/)) {\n
        return "atom";\n
      } else {\n
        stream.skipToEnd();\n
        return "error";\n
      }\n
    } else {\n
      stream.skipToEnd();\n
      return "string";\n
    }\n
  }\n
\n
  function body(stream) {\n
    stream.skipToEnd();\n
    return null;\n
  }\n
\n
  return {\n
    token: function(stream, state) {\n
      var cur = state.cur;\n
      if (cur != header && cur != body && stream.eatSpace()) return null;\n
      return cur(stream, state);\n
    },\n
\n
    blankLine: function(state) {\n
      state.cur = body;\n
    },\n
\n
    startState: function() {\n
      return {cur: start};\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("message/http", "http");\n
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
            <value> <int>2795</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
