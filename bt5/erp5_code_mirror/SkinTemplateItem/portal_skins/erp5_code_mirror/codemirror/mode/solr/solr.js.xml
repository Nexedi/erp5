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
            <value> <string>ts21897143.74</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>solr.js</string> </value>
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
CodeMirror.defineMode("solr", function() {\n
  "use strict";\n
\n
  var isStringChar = /[^\\s\\|\\!\\+\\-\\*\\?\\~\\^\\&\\:\\(\\)\\[\\]\\{\\}\\^\\"\\\\]/;\n
  var isOperatorChar = /[\\|\\!\\+\\-\\*\\?\\~\\^\\&]/;\n
  var isOperatorString = /^(OR|AND|NOT|TO)$/i;\n
\n
  function isNumber(word) {\n
    return parseFloat(word, 10).toString() === word;\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var escaped = false, next;\n
      while ((next = stream.next()) != null) {\n
        if (next == quote && !escaped) break;\n
        escaped = !escaped && next == "\\\\";\n
      }\n
\n
      if (!escaped) state.tokenize = tokenBase;\n
      return "string";\n
    };\n
  }\n
\n
  function tokenOperator(operator) {\n
    return function(stream, state) {\n
      var style = "operator";\n
      if (operator == "+")\n
        style += " positive";\n
      else if (operator == "-")\n
        style += " negative";\n
      else if (operator == "|")\n
        stream.eat(/\\|/);\n
      else if (operator == "&")\n
        stream.eat(/\\&/);\n
      else if (operator == "^")\n
        style += " boost";\n
\n
      state.tokenize = tokenBase;\n
      return style;\n
    };\n
  }\n
\n
  function tokenWord(ch) {\n
    return function(stream, state) {\n
      var word = ch;\n
      while ((ch = stream.peek()) && ch.match(isStringChar) != null) {\n
        word += stream.next();\n
      }\n
\n
      state.tokenize = tokenBase;\n
      if (isOperatorString.test(word))\n
        return "operator";\n
      else if (isNumber(word))\n
        return "number";\n
      else if (stream.peek() == ":")\n
        return "field";\n
      else\n
        return "string";\n
    };\n
  }\n
\n
  function tokenBase(stream, state) {\n
    var ch = stream.next();\n
    if (ch == \'"\')\n
      state.tokenize = tokenString(ch);\n
    else if (isOperatorChar.test(ch))\n
      state.tokenize = tokenOperator(ch);\n
    else if (isStringChar.test(ch))\n
      state.tokenize = tokenWord(ch);\n
\n
    return (state.tokenize != tokenBase) ? state.tokenize(stream, state) : null;\n
  }\n
\n
  return {\n
    startState: function() {\n
      return {\n
        tokenize: tokenBase\n
      };\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace()) return null;\n
      return state.tokenize(stream, state);\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-solr", "solr");\n
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
            <value> <int>2678</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
