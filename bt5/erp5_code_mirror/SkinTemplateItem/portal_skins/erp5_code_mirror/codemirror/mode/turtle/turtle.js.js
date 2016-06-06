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
            <value> <string>ts21897132.95</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>turtle.js</string> </value>
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
CodeMirror.defineMode("turtle", function(config) {\n
  var indentUnit = config.indentUnit;\n
  var curPunc;\n
\n
  function wordRegexp(words) {\n
    return new RegExp("^(?:" + words.join("|") + ")$", "i");\n
  }\n
  var ops = wordRegexp([]);\n
  var keywords = wordRegexp(["@prefix", "@base", "a"]);\n
  var operatorChars = /[*+\\-<>=&|]/;\n
\n
  function tokenBase(stream, state) {\n
    var ch = stream.next();\n
    curPunc = null;\n
    if (ch == "<" && !stream.match(/^[\\s\\u00a0=]/, false)) {\n
      stream.match(/^[^\\s\\u00a0>]*>?/);\n
      return "atom";\n
    }\n
    else if (ch == "\\"" || ch == "\'") {\n
      state.tokenize = tokenLiteral(ch);\n
      return state.tokenize(stream, state);\n
    }\n
    else if (/[{}\\(\\),\\.;\\[\\]]/.test(ch)) {\n
      curPunc = ch;\n
      return null;\n
    }\n
    else if (ch == "#") {\n
      stream.skipToEnd();\n
      return "comment";\n
    }\n
    else if (operatorChars.test(ch)) {\n
      stream.eatWhile(operatorChars);\n
      return null;\n
    }\n
    else if (ch == ":") {\n
          return "operator";\n
        } else {\n
      stream.eatWhile(/[_\\w\\d]/);\n
      if(stream.peek() == ":") {\n
        return "variable-3";\n
      } else {\n
             var word = stream.current();\n
\n
             if(keywords.test(word)) {\n
                        return "meta";\n
             }\n
\n
             if(ch >= "A" && ch <= "Z") {\n
                    return "comment";\n
                 } else {\n
                        return "keyword";\n
                 }\n
      }\n
      var word = stream.current();\n
      if (ops.test(word))\n
        return null;\n
      else if (keywords.test(word))\n
        return "meta";\n
      else\n
        return "variable";\n
    }\n
  }\n
\n
  function tokenLiteral(quote) {\n
    return function(stream, state) {\n
      var escaped = false, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (ch == quote && !escaped) {\n
          state.tokenize = tokenBase;\n
          break;\n
        }\n
        escaped = !escaped && ch == "\\\\";\n
      }\n
      return "string";\n
    };\n
  }\n
\n
  function pushContext(state, type, col) {\n
    state.context = {prev: state.context, indent: state.indent, col: col, type: type};\n
  }\n
  function popContext(state) {\n
    state.indent = state.context.indent;\n
    state.context = state.context.prev;\n
  }\n
\n
  return {\n
    startState: function() {\n
      return {tokenize: tokenBase,\n
              context: null,\n
              indent: 0,\n
              col: 0};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.sol()) {\n
        if (state.context && state.context.align == null) state.context.align = false;\n
        state.indent = stream.indentation();\n
      }\n
      if (stream.eatSpace()) return null;\n
      var style = state.tokenize(stream, state);\n
\n
      if (style != "comment" && state.context && state.context.align == null && state.context.type != "pattern") {\n
        state.context.align = true;\n
      }\n
\n
      if (curPunc == "(") pushContext(state, ")", stream.column());\n
      else if (curPunc == "[") pushContext(state, "]", stream.column());\n
      else if (curPunc == "{") pushContext(state, "}", stream.column());\n
      else if (/[\\]\\}\\)]/.test(curPunc)) {\n
        while (state.context && state.context.type == "pattern") popContext(state);\n
        if (state.context && curPunc == state.context.type) popContext(state);\n
      }\n
      else if (curPunc == "." && state.context && state.context.type == "pattern") popContext(state);\n
      else if (/atom|string|variable/.test(style) && state.context) {\n
        if (/[\\}\\]]/.test(state.context.type))\n
          pushContext(state, "pattern", stream.column());\n
        else if (state.context.type == "pattern" && !state.context.align) {\n
          state.context.align = true;\n
          state.context.col = stream.column();\n
        }\n
      }\n
\n
      return style;\n
    },\n
\n
    indent: function(state, textAfter) {\n
      var firstChar = textAfter && textAfter.charAt(0);\n
      var context = state.context;\n
      if (/[\\]\\}]/.test(firstChar))\n
        while (context && context.type == "pattern") context = context.prev;\n
\n
      var closing = context && firstChar == context.type;\n
      if (!context)\n
        return 0;\n
      else if (context.type == "pattern")\n
        return context.col;\n
      else if (context.align)\n
        return context.col + (closing ? 0 : 1);\n
      else\n
        return context.indent + (closing ? 0 : indentUnit);\n
    },\n
\n
    lineComment: "#"\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/turtle", "turtle");\n
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
            <value> <int>4849</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
