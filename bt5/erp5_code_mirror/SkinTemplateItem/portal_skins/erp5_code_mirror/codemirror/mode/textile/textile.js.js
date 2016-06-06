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
            <value> <string>ts21897140.94</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>textile.js</string> </value>
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
  if (typeof exports == "object" && typeof module == "object") { // CommonJS\n
    mod(require("../../lib/codemirror"));\n
  } else if (typeof define == "function" && define.amd) { // AMD\n
    define(["../../lib/codemirror"], mod);\n
  } else { // Plain browser env\n
    mod(CodeMirror);\n
  }\n
})(function(CodeMirror) {\n
  "use strict";\n
\n
  var TOKEN_STYLES = {\n
    addition: "positive",\n
    attributes: "attribute",\n
    bold: "strong",\n
    cite: "keyword",\n
    code: "atom",\n
    definitionList: "number",\n
    deletion: "negative",\n
    div: "punctuation",\n
    em: "em",\n
    footnote: "variable",\n
    footCite: "qualifier",\n
    header: "header",\n
    html: "comment",\n
    image: "string",\n
    italic: "em",\n
    link: "link",\n
    linkDefinition: "link",\n
    list1: "variable-2",\n
    list2: "variable-3",\n
    list3: "keyword",\n
    notextile: "string-2",\n
    pre: "operator",\n
    p: "property",\n
    quote: "bracket",\n
    span: "quote",\n
    specialChar: "tag",\n
    strong: "strong",\n
    sub: "builtin",\n
    sup: "builtin",\n
    table: "variable-3",\n
    tableHeading: "operator"\n
  };\n
\n
  function startNewLine(stream, state) {\n
    state.mode = Modes.newLayout;\n
    state.tableHeading = false;\n
\n
    if (state.layoutType === "definitionList" && state.spanningLayout &&\n
        stream.match(RE("definitionListEnd"), false))\n
      state.spanningLayout = false;\n
  }\n
\n
  function handlePhraseModifier(stream, state, ch) {\n
    if (ch === "_") {\n
      if (stream.eat("_"))\n
        return togglePhraseModifier(stream, state, "italic", /__/, 2);\n
      else\n
        return togglePhraseModifier(stream, state, "em", /_/, 1);\n
    }\n
\n
    if (ch === "*") {\n
      if (stream.eat("*")) {\n
        return togglePhraseModifier(stream, state, "bold", /\\*\\*/, 2);\n
      }\n
      return togglePhraseModifier(stream, state, "strong", /\\*/, 1);\n
    }\n
\n
    if (ch === "[") {\n
      if (stream.match(/\\d+\\]/)) state.footCite = true;\n
      return tokenStyles(state);\n
    }\n
\n
    if (ch === "(") {\n
      var spec = stream.match(/^(r|tm|c)\\)/);\n
      if (spec)\n
        return tokenStylesWith(state, TOKEN_STYLES.specialChar);\n
    }\n
\n
    if (ch === "<" && stream.match(/(\\w+)[^>]+>[^<]+<\\/\\1>/))\n
      return tokenStylesWith(state, TOKEN_STYLES.html);\n
\n
    if (ch === "?" && stream.eat("?"))\n
      return togglePhraseModifier(stream, state, "cite", /\\?\\?/, 2);\n
\n
    if (ch === "=" && stream.eat("="))\n
      return togglePhraseModifier(stream, state, "notextile", /==/, 2);\n
\n
    if (ch === "-" && !stream.eat("-"))\n
      return togglePhraseModifier(stream, state, "deletion", /-/, 1);\n
\n
    if (ch === "+")\n
      return togglePhraseModifier(stream, state, "addition", /\\+/, 1);\n
\n
    if (ch === "~")\n
      return togglePhraseModifier(stream, state, "sub", /~/, 1);\n
\n
    if (ch === "^")\n
      return togglePhraseModifier(stream, state, "sup", /\\^/, 1);\n
\n
    if (ch === "%")\n
      return togglePhraseModifier(stream, state, "span", /%/, 1);\n
\n
    if (ch === "@")\n
      return togglePhraseModifier(stream, state, "code", /@/, 1);\n
\n
    if (ch === "!") {\n
      var type = togglePhraseModifier(stream, state, "image", /(?:\\([^\\)]+\\))?!/, 1);\n
      stream.match(/^:\\S+/); // optional Url portion\n
      return type;\n
    }\n
    return tokenStyles(state);\n
  }\n
\n
  function togglePhraseModifier(stream, state, phraseModifier, closeRE, openSize) {\n
    var charBefore = stream.pos > openSize ? stream.string.charAt(stream.pos - openSize - 1) : null;\n
    var charAfter = stream.peek();\n
    if (state[phraseModifier]) {\n
      if ((!charAfter || /\\W/.test(charAfter)) && charBefore && /\\S/.test(charBefore)) {\n
        var type = tokenStyles(state);\n
        state[phraseModifier] = false;\n
        return type;\n
      }\n
    } else if ((!charBefore || /\\W/.test(charBefore)) && charAfter && /\\S/.test(charAfter) &&\n
               stream.match(new RegExp("^.*\\\\S" + closeRE.source + "(?:\\\\W|$)"), false)) {\n
      state[phraseModifier] = true;\n
      state.mode = Modes.attributes;\n
    }\n
    return tokenStyles(state);\n
  };\n
\n
  function tokenStyles(state) {\n
    var disabled = textileDisabled(state);\n
    if (disabled) return disabled;\n
\n
    var styles = [];\n
    if (state.layoutType) styles.push(TOKEN_STYLES[state.layoutType]);\n
\n
    styles = styles.concat(activeStyles(\n
      state, "addition", "bold", "cite", "code", "deletion", "em", "footCite",\n
      "image", "italic", "link", "span", "strong", "sub", "sup", "table", "tableHeading"));\n
\n
    if (state.layoutType === "header")\n
      styles.push(TOKEN_STYLES.header + "-" + state.header);\n
\n
    return styles.length ? styles.join(" ") : null;\n
  }\n
\n
  function textileDisabled(state) {\n
    var type = state.layoutType;\n
\n
    switch(type) {\n
    case "notextile":\n
    case "code":\n
    case "pre":\n
      return TOKEN_STYLES[type];\n
    default:\n
      if (state.notextile)\n
        return TOKEN_STYLES.notextile + (type ? (" " + TOKEN_STYLES[type]) : "");\n
      return null;\n
    }\n
  }\n
\n
  function tokenStylesWith(state, extraStyles) {\n
    var disabled = textileDisabled(state);\n
    if (disabled) return disabled;\n
\n
    var type = tokenStyles(state);\n
    if (extraStyles)\n
      return type ? (type + " " + extraStyles) : extraStyles;\n
    else\n
      return type;\n
  }\n
\n
  function activeStyles(state) {\n
    var styles = [];\n
    for (var i = 1; i < arguments.length; ++i) {\n
      if (state[arguments[i]])\n
        styles.push(TOKEN_STYLES[arguments[i]]);\n
    }\n
    return styles;\n
  }\n
\n
  function blankLine(state) {\n
    var spanningLayout = state.spanningLayout, type = state.layoutType;\n
\n
    for (var key in state) if (state.hasOwnProperty(key))\n
      delete state[key];\n
\n
    state.mode = Modes.newLayout;\n
    if (spanningLayout) {\n
      state.layoutType = type;\n
      state.spanningLayout = true;\n
    }\n
  }\n
\n
  var REs = {\n
    cache: {},\n
    single: {\n
      bc: "bc",\n
      bq: "bq",\n
      definitionList: /- [^(?::=)]+:=+/,\n
      definitionListEnd: /.*=:\\s*$/,\n
      div: "div",\n
      drawTable: /\\|.*\\|/,\n
      foot: /fn\\d+/,\n
      header: /h[1-6]/,\n
      html: /\\s*<(?:\\/)?(\\w+)(?:[^>]+)?>(?:[^<]+<\\/\\1>)?/,\n
      link: /[^"]+":\\S/,\n
      linkDefinition: /\\[[^\\s\\]]+\\]\\S+/,\n
      list: /(?:#+|\\*+)/,\n
      notextile: "notextile",\n
      para: "p",\n
      pre: "pre",\n
      table: "table",\n
      tableCellAttributes: /[\\/\\\\]\\d+/,\n
      tableHeading: /\\|_\\./,\n
      tableText: /[^"_\\*\\[\\(\\?\\+~\\^%@|-]+/,\n
      text: /[^!"_=\\*\\[\\(<\\?\\+~\\^%@-]+/\n
    },\n
    attributes: {\n
      align: /(?:<>|<|>|=)/,\n
      selector: /\\([^\\(][^\\)]+\\)/,\n
      lang: /\\[[^\\[\\]]+\\]/,\n
      pad: /(?:\\(+|\\)+){1,2}/,\n
      css: /\\{[^\\}]+\\}/\n
    },\n
    createRe: function(name) {\n
      switch (name) {\n
      case "drawTable":\n
        return REs.makeRe("^", REs.single.drawTable, "$");\n
      case "html":\n
        return REs.makeRe("^", REs.single.html, "(?:", REs.single.html, ")*", "$");\n
      case "linkDefinition":\n
        return REs.makeRe("^", REs.single.linkDefinition, "$");\n
      case "listLayout":\n
        return REs.makeRe("^", REs.single.list, RE("allAttributes"), "*\\\\s+");\n
      case "tableCellAttributes":\n
        return REs.makeRe("^", REs.choiceRe(REs.single.tableCellAttributes,\n
                                            RE("allAttributes")), "+\\\\.");\n
      case "type":\n
        return REs.makeRe("^", RE("allTypes"));\n
      case "typeLayout":\n
        return REs.makeRe("^", RE("allTypes"), RE("allAttributes"),\n
                          "*\\\\.\\\\.?", "(\\\\s+|$)");\n
      case "attributes":\n
        return REs.makeRe("^", RE("allAttributes"), "+");\n
\n
      case "allTypes":\n
        return REs.choiceRe(REs.single.div, REs.single.foot,\n
                            REs.single.header, REs.single.bc, REs.single.bq,\n
                            REs.single.notextile, REs.single.pre, REs.single.table,\n
                            REs.single.para);\n
\n
      case "allAttributes":\n
        return REs.choiceRe(REs.attributes.selector, REs.attributes.css,\n
                            REs.attributes.lang, REs.attributes.align, REs.attributes.pad);\n
\n
      default:\n
        return REs.makeRe("^", REs.single[name]);\n
      }\n
    },\n
    makeRe: function() {\n
      var pattern = "";\n
      for (var i = 0; i < arguments.length; ++i) {\n
        var arg = arguments[i];\n
        pattern += (typeof arg === "string") ? arg : arg.source;\n
      }\n
      return new RegExp(pattern);\n
    },\n
    choiceRe: function() {\n
      var parts = [arguments[0]];\n
      for (var i = 1; i < arguments.length; ++i) {\n
        parts[i * 2 - 1] = "|";\n
        parts[i * 2] = arguments[i];\n
      }\n
\n
      parts.unshift("(?:");\n
      parts.push(")");\n
      return REs.makeRe.apply(null, parts);\n
    }\n
  };\n
\n
  function RE(name) {\n
    return (REs.cache[name] || (REs.cache[name] = REs.createRe(name)));\n
  }\n
\n
  var Modes = {\n
    newLayout: function(stream, state) {\n
      if (stream.match(RE("typeLayout"), false)) {\n
        state.spanningLayout = false;\n
        return (state.mode = Modes.blockType)(stream, state);\n
      }\n
      var newMode;\n
      if (!textileDisabled(state)) {\n
        if (stream.match(RE("listLayout"), false))\n
          newMode = Modes.list;\n
        else if (stream.match(RE("drawTable"), false))\n
          newMode = Modes.table;\n
        else if (stream.match(RE("linkDefinition"), false))\n
          newMode = Modes.linkDefinition;\n
        else if (stream.match(RE("definitionList")))\n
          newMode = Modes.definitionList;\n
        else if (stream.match(RE("html"), false))\n
          newMode = Modes.html;\n
      }\n
      return (state.mode = (newMode || Modes.text))(stream, state);\n
    },\n
\n
    blockType: function(stream, state) {\n
      var match, type;\n
      state.layoutType = null;\n
\n
      if (match = stream.match(RE("type")))\n
        type = match[0];\n
      else\n
        return (state.mode = Modes.text)(stream, state);\n
\n
      if (match = type.match(RE("header"))) {\n
        state.layoutType = "header";\n
        state.header = parseInt(match[0][1]);\n
      } else if (type.match(RE("bq"))) {\n
        state.layoutType = "quote";\n
      } else if (type.match(RE("bc"))) {\n
        state.layoutType = "code";\n
      } else if (type.match(RE("foot"))) {\n
        state.layoutType = "footnote";\n
      } else if (type.match(RE("notextile"))) {\n
        state.layoutType = "notextile";\n
      } else if (type.match(RE("pre"))) {\n
        state.layoutType = "pre";\n
      } else if (type.match(RE("div"))) {\n
        state.layoutType = "div";\n
      } else if (type.match(RE("table"))) {\n
        state.layoutType = "table";\n
      }\n
\n
      state.mode = Modes.attributes;\n
      return tokenStyles(state);\n
    },\n
\n
    text: function(stream, state) {\n
      if (stream.match(RE("text"))) return tokenStyles(state);\n
\n
      var ch = stream.next();\n
      if (ch === \'"\')\n
        return (state.mode = Modes.link)(stream, state);\n
      return handlePhraseModifier(stream, state, ch);\n
    },\n
\n
    attributes: function(stream, state) {\n
      state.mode = Modes.layoutLength;\n
\n
      if (stream.match(RE("attributes")))\n
        return tokenStylesWith(state, TOKEN_STYLES.attributes);\n
      else\n
        return tokenStyles(state);\n
    },\n
\n
    layoutLength: function(stream, state) {\n
      if (stream.eat(".") && stream.eat("."))\n
        state.spanningLayout = true;\n
\n
      state.mode = Modes.text;\n
      return tokenStyles(state);\n
    },\n
\n
    list: function(stream, state) {\n
      var match = stream.match(RE("list"));\n
      state.listDepth = match[0].length;\n
      var listMod = (state.listDepth - 1) % 3;\n
      if (!listMod)\n
        state.layoutType = "list1";\n
      else if (listMod === 1)\n
        state.layoutType = "list2";\n
      else\n
        state.layoutType = "list3";\n
\n
      state.mode = Modes.attributes;\n
      return tokenStyles(state);\n
    },\n
\n
    link: function(stream, state) {\n
      state.mode = Modes.text;\n
      if (stream.match(RE("link"))) {\n
        stream.match(/\\S+/);\n
        return tokenStylesWith(state, TOKEN_STYLES.link);\n
      }\n
      return tokenStyles(state);\n
    },\n
\n
    linkDefinition: function(stream, state) {\n
      stream.skipToEnd();\n
      return tokenStylesWith(state, TOKEN_STYLES.linkDefinition);\n
    },\n
\n
    definitionList: function(stream, state) {\n
      stream.match(RE("definitionList"));\n
\n
      state.layoutType = "definitionList";\n
\n
      if (stream.match(/\\s*$/))\n
        state.spanningLayout = true;\n
      else\n
        state.mode = Modes.attributes;\n
\n
      return tokenStyles(state);\n
    },\n
\n
    html: function(stream, state) {\n
      stream.skipToEnd();\n
      return tokenStylesWith(state, TOKEN_STYLES.html);\n
    },\n
\n
    table: function(stream, state) {\n
      state.layoutType = "table";\n
      return (state.mode = Modes.tableCell)(stream, state);\n
    },\n
\n
    tableCell: function(stream, state) {\n
      if (stream.match(RE("tableHeading")))\n
        state.tableHeading = true;\n
      else\n
        stream.eat("|");\n
\n
      state.mode = Modes.tableCellAttributes;\n
      return tokenStyles(state);\n
    },\n
\n
    tableCellAttributes: function(stream, state) {\n
      state.mode = Modes.tableText;\n
\n
      if (stream.match(RE("tableCellAttributes")))\n
        return tokenStylesWith(state, TOKEN_STYLES.attributes);\n
      else\n
        return tokenStyles(state);\n
    },\n
\n
    tableText: function(stream, state) {\n
      if (stream.match(RE("tableText")))\n
        return tokenStyles(state);\n
\n
      if (stream.peek() === "|") { // end of cell\n
        state.mode = Modes.tableCell;\n
        return tokenStyles(state);\n
      }\n
      return handlePhraseModifier(stream, state, stream.next());\n
    }\n
  };\n
\n
  CodeMirror.defineMode("textile", function() {\n
    return {\n
      startState: function() {\n
        return { mode: Modes.newLayout };\n
      },\n
      token: function(stream, state) {\n
        if (stream.sol()) startNewLine(stream, state);\n
        return state.mode(stream, state);\n
      },\n
      blankLine: blankLine\n
    };\n
  });\n
\n
  CodeMirror.defineMIME("text/x-textile", "textile");\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>13842</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
