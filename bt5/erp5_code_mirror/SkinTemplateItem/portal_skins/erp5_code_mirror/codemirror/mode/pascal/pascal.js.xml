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
            <value> <string>ts21897138.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pascal.js</string> </value>
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
CodeMirror.defineMode("pascal", function() {\n
  function words(str) {\n
    var obj = {}, words = str.split(" ");\n
    for (var i = 0; i < words.length; ++i) obj[words[i]] = true;\n
    return obj;\n
  }\n
  var keywords = words("and array begin case const div do downto else end file for forward integer " +\n
                       "boolean char function goto if in label mod nil not of or packed procedure " +\n
                       "program record repeat set string then to type until var while with");\n
  var atoms = {"null": true};\n
\n
  var isOperatorChar = /[+\\-*&%=<>!?|\\/]/;\n
\n
  function tokenBase(stream, state) {\n
    var ch = stream.next();\n
    if (ch == "#" && state.startOfLine) {\n
      stream.skipToEnd();\n
      return "meta";\n
    }\n
    if (ch == \'"\' || ch == "\'") {\n
      state.tokenize = tokenString(ch);\n
      return state.tokenize(stream, state);\n
    }\n
    if (ch == "(" && stream.eat("*")) {\n
      state.tokenize = tokenComment;\n
      return tokenComment(stream, state);\n
    }\n
    if (/[\\[\\]{}\\(\\),;\\:\\.]/.test(ch)) {\n
      return null;\n
    }\n
    if (/\\d/.test(ch)) {\n
      stream.eatWhile(/[\\w\\.]/);\n
      return "number";\n
    }\n
    if (ch == "/") {\n
      if (stream.eat("/")) {\n
        stream.skipToEnd();\n
        return "comment";\n
      }\n
    }\n
    if (isOperatorChar.test(ch)) {\n
      stream.eatWhile(isOperatorChar);\n
      return "operator";\n
    }\n
    stream.eatWhile(/[\\w\\$_]/);\n
    var cur = stream.current();\n
    if (keywords.propertyIsEnumerable(cur)) return "keyword";\n
    if (atoms.propertyIsEnumerable(cur)) return "atom";\n
    return "variable";\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var escaped = false, next, end = false;\n
      while ((next = stream.next()) != null) {\n
        if (next == quote && !escaped) {end = true; break;}\n
        escaped = !escaped && next == "\\\\";\n
      }\n
      if (end || !escaped) state.tokenize = null;\n
      return "string";\n
    };\n
  }\n
\n
  function tokenComment(stream, state) {\n
    var maybeEnd = false, ch;\n
    while (ch = stream.next()) {\n
      if (ch == ")" && maybeEnd) {\n
        state.tokenize = null;\n
        break;\n
      }\n
      maybeEnd = (ch == "*");\n
    }\n
    return "comment";\n
  }\n
\n
  // Interface\n
\n
  return {\n
    startState: function() {\n
      return {tokenize: null};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace()) return null;\n
      var style = (state.tokenize || tokenBase)(stream, state);\n
      if (style == "comment" || style == "meta") return style;\n
      return style;\n
    },\n
\n
    electricChars: "{}"\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-pascal", "pascal");\n
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
            <value> <int>3055</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
