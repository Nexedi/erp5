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
            <value> <string>ts21897147.29</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>sieve.js</string> </value>
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
CodeMirror.defineMode("sieve", function(config) {\n
  function words(str) {\n
    var obj = {}, words = str.split(" ");\n
    for (var i = 0; i < words.length; ++i) obj[words[i]] = true;\n
    return obj;\n
  }\n
\n
  var keywords = words("if elsif else stop require");\n
  var atoms = words("true false not");\n
  var indentUnit = config.indentUnit;\n
\n
  function tokenBase(stream, state) {\n
\n
    var ch = stream.next();\n
    if (ch == "/" && stream.eat("*")) {\n
      state.tokenize = tokenCComment;\n
      return tokenCComment(stream, state);\n
    }\n
\n
    if (ch === \'#\') {\n
      stream.skipToEnd();\n
      return "comment";\n
    }\n
\n
    if (ch == "\\"") {\n
      state.tokenize = tokenString(ch);\n
      return state.tokenize(stream, state);\n
    }\n
\n
    if (ch == "(") {\n
      state._indent.push("(");\n
      // add virtual angel wings so that editor behaves...\n
      // ...more sane incase of broken brackets\n
      state._indent.push("{");\n
      return null;\n
    }\n
\n
    if (ch === "{") {\n
      state._indent.push("{");\n
      return null;\n
    }\n
\n
    if (ch == ")")  {\n
      state._indent.pop();\n
      state._indent.pop();\n
    }\n
\n
    if (ch === "}") {\n
      state._indent.pop();\n
      return null;\n
    }\n
\n
    if (ch == ",")\n
      return null;\n
\n
    if (ch == ";")\n
      return null;\n
\n
\n
    if (/[{}\\(\\),;]/.test(ch))\n
      return null;\n
\n
    // 1*DIGIT "K" / "M" / "G"\n
    if (/\\d/.test(ch)) {\n
      stream.eatWhile(/[\\d]/);\n
      stream.eat(/[KkMmGg]/);\n
      return "number";\n
    }\n
\n
    // ":" (ALPHA / "_") *(ALPHA / DIGIT / "_")\n
    if (ch == ":") {\n
      stream.eatWhile(/[a-zA-Z_]/);\n
      stream.eatWhile(/[a-zA-Z0-9_]/);\n
\n
      return "operator";\n
    }\n
\n
    stream.eatWhile(/\\w/);\n
    var cur = stream.current();\n
\n
    // "text:" *(SP / HTAB) (hash-comment / CRLF)\n
    // *(multiline-literal / multiline-dotstart)\n
    // "." CRLF\n
    if ((cur == "text") && stream.eat(":"))\n
    {\n
      state.tokenize = tokenMultiLineString;\n
      return "string";\n
    }\n
\n
    if (keywords.propertyIsEnumerable(cur))\n
      return "keyword";\n
\n
    if (atoms.propertyIsEnumerable(cur))\n
      return "atom";\n
\n
    return null;\n
  }\n
\n
  function tokenMultiLineString(stream, state)\n
  {\n
    state._multiLineString = true;\n
    // the first line is special it may contain a comment\n
    if (!stream.sol()) {\n
      stream.eatSpace();\n
\n
      if (stream.peek() == "#") {\n
        stream.skipToEnd();\n
        return "comment";\n
      }\n
\n
      stream.skipToEnd();\n
      return "string";\n
    }\n
\n
    if ((stream.next() == ".")  && (stream.eol()))\n
    {\n
      state._multiLineString = false;\n
      state.tokenize = tokenBase;\n
    }\n
\n
    return "string";\n
  }\n
\n
  function tokenCComment(stream, state) {\n
    var maybeEnd = false, ch;\n
    while ((ch = stream.next()) != null) {\n
      if (maybeEnd && ch == "/") {\n
        state.tokenize = tokenBase;\n
        break;\n
      }\n
      maybeEnd = (ch == "*");\n
    }\n
    return "comment";\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var escaped = false, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (ch == quote && !escaped)\n
          break;\n
        escaped = !escaped && ch == "\\\\";\n
      }\n
      if (!escaped) state.tokenize = tokenBase;\n
      return "string";\n
    };\n
  }\n
\n
  return {\n
    startState: function(base) {\n
      return {tokenize: tokenBase,\n
              baseIndent: base || 0,\n
              _indent: []};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace())\n
        return null;\n
\n
      return (state.tokenize || tokenBase)(stream, state);;\n
    },\n
\n
    indent: function(state, _textAfter) {\n
      var length = state._indent.length;\n
      if (_textAfter && (_textAfter[0] == "}"))\n
        length--;\n
\n
      if (length <0)\n
        length = 0;\n
\n
      return length * indentUnit;\n
    },\n
\n
    electricChars: "}"\n
  };\n
});\n
\n
CodeMirror.defineMIME("application/sieve", "sieve");\n
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
            <value> <int>4285</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
