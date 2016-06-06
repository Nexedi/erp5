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
            <value> <string>ts21897136.69</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>modelica.js</string> </value>
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
// Modelica support for CodeMirror, copyright (c) by Lennart Ochel\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})\n
\n
(function(CodeMirror) {\n
  "use strict";\n
\n
  CodeMirror.defineMode("modelica", function(config, parserConfig) {\n
\n
    var indentUnit = config.indentUnit;\n
    var keywords = parserConfig.keywords || {};\n
    var builtin = parserConfig.builtin || {};\n
    var atoms = parserConfig.atoms || {};\n
\n
    var isSingleOperatorChar = /[;=\\(:\\),{}.*<>+\\-\\/^\\[\\]]/;\n
    var isDoubleOperatorChar = /(:=|<=|>=|==|<>|\\.\\+|\\.\\-|\\.\\*|\\.\\/|\\.\\^)/;\n
    var isDigit = /[0-9]/;\n
    var isNonDigit = /[_a-zA-Z]/;\n
\n
    function tokenLineComment(stream, state) {\n
      stream.skipToEnd();\n
      state.tokenize = null;\n
      return "comment";\n
    }\n
\n
    function tokenBlockComment(stream, state) {\n
      var maybeEnd = false, ch;\n
      while (ch = stream.next()) {\n
        if (maybeEnd && ch == "/") {\n
          state.tokenize = null;\n
          break;\n
        }\n
        maybeEnd = (ch == "*");\n
      }\n
      return "comment";\n
    }\n
\n
    function tokenString(stream, state) {\n
      var escaped = false, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (ch == \'"\' && !escaped) {\n
          state.tokenize = null;\n
          state.sol = false;\n
          break;\n
        }\n
        escaped = !escaped && ch == "\\\\";\n
      }\n
\n
      return "string";\n
    }\n
\n
    function tokenIdent(stream, state) {\n
      stream.eatWhile(isDigit);\n
      while (stream.eat(isDigit) || stream.eat(isNonDigit)) { }\n
\n
\n
      var cur = stream.current();\n
\n
      if(state.sol && (cur == "package" || cur == "model" || cur == "when" || cur == "connector")) state.level++;\n
      else if(state.sol && cur == "end" && state.level > 0) state.level--;\n
\n
      state.tokenize = null;\n
      state.sol = false;\n
\n
      if (keywords.propertyIsEnumerable(cur)) return "keyword";\n
      else if (builtin.propertyIsEnumerable(cur)) return "builtin";\n
      else if (atoms.propertyIsEnumerable(cur)) return "atom";\n
      else return "variable";\n
    }\n
\n
    function tokenQIdent(stream, state) {\n
      while (stream.eat(/[^\']/)) { }\n
\n
      state.tokenize = null;\n
      state.sol = false;\n
\n
      if(stream.eat("\'"))\n
        return "variable";\n
      else\n
        return "error";\n
    }\n
\n
    function tokenUnsignedNuber(stream, state) {\n
      stream.eatWhile(isDigit);\n
      if (stream.eat(\'.\')) {\n
        stream.eatWhile(isDigit);\n
      }\n
      if (stream.eat(\'e\') || stream.eat(\'E\')) {\n
        if (!stream.eat(\'-\'))\n
          stream.eat(\'+\');\n
        stream.eatWhile(isDigit);\n
      }\n
\n
      state.tokenize = null;\n
      state.sol = false;\n
      return "number";\n
    }\n
\n
    // Interface\n
    return {\n
      startState: function() {\n
        return {\n
          tokenize: null,\n
          level: 0,\n
          sol: true\n
        };\n
      },\n
\n
      token: function(stream, state) {\n
        if(state.tokenize != null) {\n
          return state.tokenize(stream, state);\n
        }\n
\n
        if(stream.sol()) {\n
          state.sol = true;\n
        }\n
\n
        // WHITESPACE\n
        if(stream.eatSpace()) {\n
          state.tokenize = null;\n
          return null;\n
        }\n
\n
        var ch = stream.next();\n
\n
        // LINECOMMENT\n
        if(ch == \'/\' && stream.eat(\'/\')) {\n
          state.tokenize = tokenLineComment;\n
        }\n
        // BLOCKCOMMENT\n
        else if(ch == \'/\' && stream.eat(\'*\')) {\n
          state.tokenize = tokenBlockComment;\n
        }\n
        // TWO SYMBOL TOKENS\n
        else if(isDoubleOperatorChar.test(ch+stream.peek())) {\n
          stream.next();\n
          state.tokenize = null;\n
          return "operator";\n
        }\n
        // SINGLE SYMBOL TOKENS\n
        else if(isSingleOperatorChar.test(ch)) {\n
          state.tokenize = null;\n
          return "operator";\n
        }\n
        // IDENT\n
        else if(isNonDigit.test(ch)) {\n
          state.tokenize = tokenIdent;\n
        }\n
        // Q-IDENT\n
        else if(ch == "\'" && stream.peek() && stream.peek() != "\'") {\n
          state.tokenize = tokenQIdent;\n
        }\n
        // STRING\n
        else if(ch == \'"\') {\n
          state.tokenize = tokenString;\n
        }\n
        // UNSIGNED_NUBER\n
        else if(isDigit.test(ch)) {\n
          state.tokenize = tokenUnsignedNuber;\n
        }\n
        // ERROR\n
        else {\n
          state.tokenize = null;\n
          return "error";\n
        }\n
\n
        return state.tokenize(stream, state);\n
      },\n
\n
      indent: function(state, textAfter) {\n
        if (state.tokenize != null) return CodeMirror.Pass;\n
\n
        var level = state.level;\n
        if(/(algorithm)/.test(textAfter)) level--;\n
        if(/(equation)/.test(textAfter)) level--;\n
        if(/(initial algorithm)/.test(textAfter)) level--;\n
        if(/(initial equation)/.test(textAfter)) level--;\n
        if(/(end)/.test(textAfter)) level--;\n
\n
        if(level > 0)\n
          return indentUnit*level;\n
        else\n
          return 0;\n
      },\n
\n
      blockCommentStart: "/*",\n
      blockCommentEnd: "*/",\n
      lineComment: "//"\n
    };\n
  });\n
\n
  function words(str) {\n
    var obj = {}, words = str.split(" ");\n
    for (var i=0; i<words.length; ++i)\n
      obj[words[i]] = true;\n
    return obj;\n
  }\n
\n
  var modelicaKeywords = "algorithm and annotation assert block break class connect connector constant constrainedby der discrete each else elseif elsewhen encapsulated end enumeration equation expandable extends external false final flow for function if import impure in initial inner input loop model not operator or outer output package parameter partial protected public pure record redeclare replaceable return stream then true type when while within";\n
  var modelicaBuiltin = "abs acos actualStream asin atan atan2 cardinality ceil cos cosh delay div edge exp floor getInstanceName homotopy inStream integer log log10 mod pre reinit rem semiLinear sign sin sinh spatialDistribution sqrt tan tanh";\n
  var modelicaAtoms = "Real Boolean Integer String";\n
\n
  function def(mimes, mode) {\n
    if (typeof mimes == "string")\n
      mimes = [mimes];\n
\n
    var words = [];\n
\n
    function add(obj) {\n
      if (obj)\n
        for (var prop in obj)\n
          if (obj.hasOwnProperty(prop))\n
            words.push(prop);\n
    }\n
\n
    add(mode.keywords);\n
    add(mode.builtin);\n
    add(mode.atoms);\n
\n
    if (words.length) {\n
      mode.helperType = mimes[0];\n
      CodeMirror.registerHelper("hintWords", mimes[0], words);\n
    }\n
\n
    for (var i=0; i<mimes.length; ++i)\n
      CodeMirror.defineMIME(mimes[i], mode);\n
  }\n
\n
  def(["text/x-modelica"], {\n
    name: "modelica",\n
    keywords: words(modelicaKeywords),\n
    builtin: words(modelicaBuiltin),\n
    atoms: words(modelicaAtoms)\n
  });\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6930</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
