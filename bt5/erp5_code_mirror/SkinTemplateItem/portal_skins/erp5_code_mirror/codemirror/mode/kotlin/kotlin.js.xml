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
            <value> <string>ts21897145.7</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>kotlin.js</string> </value>
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
CodeMirror.defineMode("kotlin", function (config, parserConfig) {\n
  function words(str) {\n
    var obj = {}, words = str.split(" ");\n
    for (var i = 0; i < words.length; ++i) obj[words[i]] = true;\n
    return obj;\n
  }\n
\n
  var multiLineStrings = parserConfig.multiLineStrings;\n
\n
  var keywords = words(\n
          "package continue return object while break class data trait throw super" +\n
          " when type this else This try val var fun for is in if do as true false null get set");\n
  var softKeywords = words("import" +\n
      " where by get set abstract enum open annotation override private public internal" +\n
      " protected catch out vararg inline finally final ref");\n
  var blockKeywords = words("catch class do else finally for if where try while enum");\n
  var atoms = words("null true false this");\n
\n
  var curPunc;\n
\n
  function tokenBase(stream, state) {\n
    var ch = stream.next();\n
    if (ch == \'"\' || ch == "\'") {\n
      return startString(ch, stream, state);\n
    }\n
    // Wildcard import w/o trailing semicolon (import smth.*)\n
    if (ch == "." && stream.eat("*")) {\n
      return "word";\n
    }\n
    if (/[\\[\\]{}\\(\\),;\\:\\.]/.test(ch)) {\n
      curPunc = ch;\n
      return null;\n
    }\n
    if (/\\d/.test(ch)) {\n
      if (stream.eat(/eE/)) {\n
        stream.eat(/\\+\\-/);\n
        stream.eatWhile(/\\d/);\n
      }\n
      return "number";\n
    }\n
    if (ch == "/") {\n
      if (stream.eat("*")) {\n
        state.tokenize.push(tokenComment);\n
        return tokenComment(stream, state);\n
      }\n
      if (stream.eat("/")) {\n
        stream.skipToEnd();\n
        return "comment";\n
      }\n
      if (expectExpression(state.lastToken)) {\n
        return startString(ch, stream, state);\n
      }\n
    }\n
    // Commented\n
    if (ch == "-" && stream.eat(">")) {\n
      curPunc = "->";\n
      return null;\n
    }\n
    if (/[\\-+*&%=<>!?|\\/~]/.test(ch)) {\n
      stream.eatWhile(/[\\-+*&%=<>|~]/);\n
      return "operator";\n
    }\n
    stream.eatWhile(/[\\w\\$_]/);\n
\n
    var cur = stream.current();\n
    if (atoms.propertyIsEnumerable(cur)) {\n
      return "atom";\n
    }\n
    if (softKeywords.propertyIsEnumerable(cur)) {\n
      if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";\n
      return "softKeyword";\n
    }\n
\n
    if (keywords.propertyIsEnumerable(cur)) {\n
      if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";\n
      return "keyword";\n
    }\n
    return "word";\n
  }\n
\n
  tokenBase.isBase = true;\n
\n
  function startString(quote, stream, state) {\n
    var tripleQuoted = false;\n
    if (quote != "/" && stream.eat(quote)) {\n
      if (stream.eat(quote)) tripleQuoted = true;\n
      else return "string";\n
    }\n
    function t(stream, state) {\n
      var escaped = false, next, end = !tripleQuoted;\n
\n
      while ((next = stream.next()) != null) {\n
        if (next == quote && !escaped) {\n
          if (!tripleQuoted) {\n
            break;\n
          }\n
          if (stream.match(quote + quote)) {\n
            end = true;\n
            break;\n
          }\n
        }\n
\n
        if (quote == \'"\' && next == "$" && !escaped && stream.eat("{")) {\n
          state.tokenize.push(tokenBaseUntilBrace());\n
          return "string";\n
        }\n
\n
        if (next == "$" && !escaped && !stream.eat(" ")) {\n
          state.tokenize.push(tokenBaseUntilSpace());\n
          return "string";\n
        }\n
        escaped = !escaped && next == "\\\\";\n
      }\n
      if (multiLineStrings)\n
        state.tokenize.push(t);\n
      if (end) state.tokenize.pop();\n
      return "string";\n
    }\n
\n
    state.tokenize.push(t);\n
    return t(stream, state);\n
  }\n
\n
  function tokenBaseUntilBrace() {\n
    var depth = 1;\n
\n
    function t(stream, state) {\n
      if (stream.peek() == "}") {\n
        depth--;\n
        if (depth == 0) {\n
          state.tokenize.pop();\n
          return state.tokenize[state.tokenize.length - 1](stream, state);\n
        }\n
      } else if (stream.peek() == "{") {\n
        depth++;\n
      }\n
      return tokenBase(stream, state);\n
    }\n
\n
    t.isBase = true;\n
    return t;\n
  }\n
\n
  function tokenBaseUntilSpace() {\n
    function t(stream, state) {\n
      if (stream.eat(/[\\w]/)) {\n
        var isWord = stream.eatWhile(/[\\w]/);\n
        if (isWord) {\n
          state.tokenize.pop();\n
          return "word";\n
        }\n
      }\n
      state.tokenize.pop();\n
      return "string";\n
    }\n
\n
    t.isBase = true;\n
    return t;\n
  }\n
\n
  function tokenComment(stream, state) {\n
    var maybeEnd = false, ch;\n
    while (ch = stream.next()) {\n
      if (ch == "/" && maybeEnd) {\n
        state.tokenize.pop();\n
        break;\n
      }\n
      maybeEnd = (ch == "*");\n
    }\n
    return "comment";\n
  }\n
\n
  function expectExpression(last) {\n
    return !last || last == "operator" || last == "->" || /[\\.\\[\\{\\(,;:]/.test(last) ||\n
        last == "newstatement" || last == "keyword" || last == "proplabel";\n
  }\n
\n
  function Context(indented, column, type, align, prev) {\n
    this.indented = indented;\n
    this.column = column;\n
    this.type = type;\n
    this.align = align;\n
    this.prev = prev;\n
  }\n
\n
  function pushContext(state, col, type) {\n
    return state.context = new Context(state.indented, col, type, null, state.context);\n
  }\n
\n
  function popContext(state) {\n
    var t = state.context.type;\n
    if (t == ")" || t == "]" || t == "}")\n
      state.indented = state.context.indented;\n
    return state.context = state.context.prev;\n
  }\n
\n
  // Interface\n
\n
  return {\n
    startState: function (basecolumn) {\n
      return {\n
        tokenize: [tokenBase],\n
        context: new Context((basecolumn || 0) - config.indentUnit, 0, "top", false),\n
        indented: 0,\n
        startOfLine: true,\n
        lastToken: null\n
      };\n
    },\n
\n
    token: function (stream, state) {\n
      var ctx = state.context;\n
      if (stream.sol()) {\n
        if (ctx.align == null) ctx.align = false;\n
        state.indented = stream.indentation();\n
        state.startOfLine = true;\n
        // Automatic semicolon insertion\n
        if (ctx.type == "statement" && !expectExpression(state.lastToken)) {\n
          popContext(state);\n
          ctx = state.context;\n
        }\n
      }\n
      if (stream.eatSpace()) return null;\n
      curPunc = null;\n
      var style = state.tokenize[state.tokenize.length - 1](stream, state);\n
      if (style == "comment") return style;\n
      if (ctx.align == null) ctx.align = true;\n
      if ((curPunc == ";" || curPunc == ":") && ctx.type == "statement") popContext(state);\n
      // Handle indentation for {x -> \\n ... }\n
      else if (curPunc == "->" && ctx.type == "statement" && ctx.prev.type == "}") {\n
        popContext(state);\n
        state.context.align = false;\n
      }\n
      else if (curPunc == "{") pushContext(state, stream.column(), "}");\n
      else if (curPunc == "[") pushContext(state, stream.column(), "]");\n
      else if (curPunc == "(") pushContext(state, stream.column(), ")");\n
      else if (curPunc == "}") {\n
        while (ctx.type == "statement") ctx = popContext(state);\n
        if (ctx.type == "}") ctx = popContext(state);\n
        while (ctx.type == "statement") ctx = popContext(state);\n
      }\n
      else if (curPunc == ctx.type) popContext(state);\n
      else if (ctx.type == "}" || ctx.type == "top" || (ctx.type == "statement" && curPunc == "newstatement"))\n
        pushContext(state, stream.column(), "statement");\n
      state.startOfLine = false;\n
      state.lastToken = curPunc || style;\n
      return style;\n
    },\n
\n
    indent: function (state, textAfter) {\n
      if (!state.tokenize[state.tokenize.length - 1].isBase) return 0;\n
      var firstChar = textAfter && textAfter.charAt(0), ctx = state.context;\n
      if (ctx.type == "statement" && !expectExpression(state.lastToken)) ctx = ctx.prev;\n
      var closing = firstChar == ctx.type;\n
      if (ctx.type == "statement") {\n
        return ctx.indented + (firstChar == "{" ? 0 : config.indentUnit);\n
      }\n
      else if (ctx.align) return ctx.column + (closing ? 0 : 1);\n
      else return ctx.indented + (closing ? 0 : config.indentUnit);\n
    },\n
\n
    electricChars: "{}"\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-kotlin", "kotlin");\n
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
            <value> <int>8410</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
