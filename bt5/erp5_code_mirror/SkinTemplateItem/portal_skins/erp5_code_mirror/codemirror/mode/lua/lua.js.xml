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
            <value> <string>ts21897148.96</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lua.js</string> </value>
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
// LUA mode. Ported to CodeMirror 2 from Franciszek Wawrzak\'s\n
// CodeMirror 1 mode.\n
// highlights keywords, strings, comments (no leveling supported! ("[==[")), tokens, basic indenting\n
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
CodeMirror.defineMode("lua", function(config, parserConfig) {\n
  var indentUnit = config.indentUnit;\n
\n
  function prefixRE(words) {\n
    return new RegExp("^(?:" + words.join("|") + ")", "i");\n
  }\n
  function wordRE(words) {\n
    return new RegExp("^(?:" + words.join("|") + ")$", "i");\n
  }\n
  var specials = wordRE(parserConfig.specials || []);\n
\n
  // long list of standard functions from lua manual\n
  var builtins = wordRE([\n
    "_G","_VERSION","assert","collectgarbage","dofile","error","getfenv","getmetatable","ipairs","load",\n
    "loadfile","loadstring","module","next","pairs","pcall","print","rawequal","rawget","rawset","require",\n
    "select","setfenv","setmetatable","tonumber","tostring","type","unpack","xpcall",\n
\n
    "coroutine.create","coroutine.resume","coroutine.running","coroutine.status","coroutine.wrap","coroutine.yield",\n
\n
    "debug.debug","debug.getfenv","debug.gethook","debug.getinfo","debug.getlocal","debug.getmetatable",\n
    "debug.getregistry","debug.getupvalue","debug.setfenv","debug.sethook","debug.setlocal","debug.setmetatable",\n
    "debug.setupvalue","debug.traceback",\n
\n
    "close","flush","lines","read","seek","setvbuf","write",\n
\n
    "io.close","io.flush","io.input","io.lines","io.open","io.output","io.popen","io.read","io.stderr","io.stdin",\n
    "io.stdout","io.tmpfile","io.type","io.write",\n
\n
    "math.abs","math.acos","math.asin","math.atan","math.atan2","math.ceil","math.cos","math.cosh","math.deg",\n
    "math.exp","math.floor","math.fmod","math.frexp","math.huge","math.ldexp","math.log","math.log10","math.max",\n
    "math.min","math.modf","math.pi","math.pow","math.rad","math.random","math.randomseed","math.sin","math.sinh",\n
    "math.sqrt","math.tan","math.tanh",\n
\n
    "os.clock","os.date","os.difftime","os.execute","os.exit","os.getenv","os.remove","os.rename","os.setlocale",\n
    "os.time","os.tmpname",\n
\n
    "package.cpath","package.loaded","package.loaders","package.loadlib","package.path","package.preload",\n
    "package.seeall",\n
\n
    "string.byte","string.char","string.dump","string.find","string.format","string.gmatch","string.gsub",\n
    "string.len","string.lower","string.match","string.rep","string.reverse","string.sub","string.upper",\n
\n
    "table.concat","table.insert","table.maxn","table.remove","table.sort"\n
  ]);\n
  var keywords = wordRE(["and","break","elseif","false","nil","not","or","return",\n
                         "true","function", "end", "if", "then", "else", "do",\n
                         "while", "repeat", "until", "for", "in", "local" ]);\n
\n
  var indentTokens = wordRE(["function", "if","repeat","do", "\\\\(", "{"]);\n
  var dedentTokens = wordRE(["end", "until", "\\\\)", "}"]);\n
  var dedentPartial = prefixRE(["end", "until", "\\\\)", "}", "else", "elseif"]);\n
\n
  function readBracket(stream) {\n
    var level = 0;\n
    while (stream.eat("=")) ++level;\n
    stream.eat("[");\n
    return level;\n
  }\n
\n
  function normal(stream, state) {\n
    var ch = stream.next();\n
    if (ch == "-" && stream.eat("-")) {\n
      if (stream.eat("[") && stream.eat("["))\n
        return (state.cur = bracketed(readBracket(stream), "comment"))(stream, state);\n
      stream.skipToEnd();\n
      return "comment";\n
    }\n
    if (ch == "\\"" || ch == "\'")\n
      return (state.cur = string(ch))(stream, state);\n
    if (ch == "[" && /[\\[=]/.test(stream.peek()))\n
      return (state.cur = bracketed(readBracket(stream), "string"))(stream, state);\n
    if (/\\d/.test(ch)) {\n
      stream.eatWhile(/[\\w.%]/);\n
      return "number";\n
    }\n
    if (/[\\w_]/.test(ch)) {\n
      stream.eatWhile(/[\\w\\\\\\-_.]/);\n
      return "variable";\n
    }\n
    return null;\n
  }\n
\n
  function bracketed(level, style) {\n
    return function(stream, state) {\n
      var curlev = null, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (curlev == null) {if (ch == "]") curlev = 0;}\n
        else if (ch == "=") ++curlev;\n
        else if (ch == "]" && curlev == level) { state.cur = normal; break; }\n
        else curlev = null;\n
      }\n
      return style;\n
    };\n
  }\n
\n
  function string(quote) {\n
    return function(stream, state) {\n
      var escaped = false, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (ch == quote && !escaped) break;\n
        escaped = !escaped && ch == "\\\\";\n
      }\n
      if (!escaped) state.cur = normal;\n
      return "string";\n
    };\n
  }\n
\n
  return {\n
    startState: function(basecol) {\n
      return {basecol: basecol || 0, indentDepth: 0, cur: normal};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace()) return null;\n
      var style = state.cur(stream, state);\n
      var word = stream.current();\n
      if (style == "variable") {\n
        if (keywords.test(word)) style = "keyword";\n
        else if (builtins.test(word)) style = "builtin";\n
        else if (specials.test(word)) style = "variable-2";\n
      }\n
      if ((style != "comment") && (style != "string")){\n
        if (indentTokens.test(word)) ++state.indentDepth;\n
        else if (dedentTokens.test(word)) --state.indentDepth;\n
      }\n
      return style;\n
    },\n
\n
    indent: function(state, textAfter) {\n
      var closing = dedentPartial.test(textAfter);\n
      return state.basecol + indentUnit * (state.indentDepth - (closing ? 1 : 0));\n
    },\n
\n
    lineComment: "--",\n
    blockCommentStart: "--[[",\n
    blockCommentEnd: "]]"\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-lua", "lua");\n
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
            <value> <int>5950</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
