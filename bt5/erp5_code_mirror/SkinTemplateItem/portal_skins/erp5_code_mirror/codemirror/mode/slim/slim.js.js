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
            <value> <string>ts21897147.93</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>slim.js</string> </value>
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
// Slim Highlighting for CodeMirror copyright (c) HicknHack Software Gmbh\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"), require("../htmlmixed/htmlmixed"), require("../ruby/ruby"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../htmlmixed/htmlmixed", "../ruby/ruby"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
"use strict";\n
\n
  CodeMirror.defineMode("slim", function(config) {\n
    var htmlMode = CodeMirror.getMode(config, {name: "htmlmixed"});\n
    var rubyMode = CodeMirror.getMode(config, "ruby");\n
    var modes = { html: htmlMode, ruby: rubyMode };\n
    var embedded = {\n
      ruby: "ruby",\n
      javascript: "javascript",\n
      css: "text/css",\n
      sass: "text/x-sass",\n
      scss: "text/x-scss",\n
      less: "text/x-less",\n
      styl: "text/x-styl", // no highlighting so far\n
      coffee: "coffeescript",\n
      asciidoc: "text/x-asciidoc",\n
      markdown: "text/x-markdown",\n
      textile: "text/x-textile", // no highlighting so far\n
      creole: "text/x-creole", // no highlighting so far\n
      wiki: "text/x-wiki", // no highlighting so far\n
      mediawiki: "text/x-mediawiki", // no highlighting so far\n
      rdoc: "text/x-rdoc", // no highlighting so far\n
      builder: "text/x-builder", // no highlighting so far\n
      nokogiri: "text/x-nokogiri", // no highlighting so far\n
      erb: "application/x-erb"\n
    };\n
    var embeddedRegexp = function(map){\n
      var arr = [];\n
      for(var key in map) arr.push(key);\n
      return new RegExp("^("+arr.join(\'|\')+"):");\n
    }(embedded);\n
\n
    var styleMap = {\n
      "commentLine": "comment",\n
      "slimSwitch": "operator special",\n
      "slimTag": "tag",\n
      "slimId": "attribute def",\n
      "slimClass": "attribute qualifier",\n
      "slimAttribute": "attribute",\n
      "slimSubmode": "keyword special",\n
      "closeAttributeTag": null,\n
      "slimDoctype": null,\n
      "lineContinuation": null\n
    };\n
    var closing = {\n
      "{": "}",\n
      "[": "]",\n
      "(": ")"\n
    };\n
\n
    var nameStartChar = "_a-zA-Z\\xC0-\\xD6\\xD8-\\xF6\\xF8-\\u02FF\\u0370-\\u037D\\u037F-\\u1FFF\\u200C-\\u200D\\u2070-\\u218F\\u2C00-\\u2FEF\\u3001-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFFD";\n
    var nameChar = nameStartChar + "\\\\-0-9\\xB7\\u0300-\\u036F\\u203F-\\u2040";\n
    var nameRegexp = new RegExp("^[:"+nameStartChar+"](?::["+nameChar+"]|["+nameChar+"]*)");\n
    var attributeNameRegexp = new RegExp("^[:"+nameStartChar+"][:\\\\."+nameChar+"]*(?=\\\\s*=)");\n
    var wrappedAttributeNameRegexp = new RegExp("^[:"+nameStartChar+"][:\\\\."+nameChar+"]*");\n
    var classNameRegexp = /^\\.-?[_a-zA-Z]+[\\w\\-]*/;\n
    var classIdRegexp = /^#[_a-zA-Z]+[\\w\\-]*/;\n
\n
    function backup(pos, tokenize, style) {\n
      var restore = function(stream, state) {\n
        state.tokenize = tokenize;\n
        if (stream.pos < pos) {\n
          stream.pos = pos;\n
          return style;\n
        }\n
        return state.tokenize(stream, state);\n
      };\n
      return function(stream, state) {\n
        state.tokenize = restore;\n
        return tokenize(stream, state);\n
      };\n
    }\n
\n
    function maybeBackup(stream, state, pat, offset, style) {\n
      var cur = stream.current();\n
      var idx = cur.search(pat);\n
      if (idx > -1) {\n
        state.tokenize = backup(stream.pos, state.tokenize, style);\n
        stream.backUp(cur.length - idx - offset);\n
      }\n
      return style;\n
    }\n
\n
    function continueLine(state, column) {\n
      state.stack = {\n
        parent: state.stack,\n
        style: "continuation",\n
        indented: column,\n
        tokenize: state.line\n
      };\n
      state.line = state.tokenize;\n
    }\n
    function finishContinue(state) {\n
      if (state.line == state.tokenize) {\n
        state.line = state.stack.tokenize;\n
        state.stack = state.stack.parent;\n
      }\n
    }\n
\n
    function lineContinuable(column, tokenize) {\n
      return function(stream, state) {\n
        finishContinue(state);\n
        if (stream.match(/^\\\\$/)) {\n
          continueLine(state, column);\n
          return "lineContinuation";\n
        }\n
        var style = tokenize(stream, state);\n
        if (stream.eol() && stream.current().match(/(?:^|[^\\\\])(?:\\\\\\\\)*\\\\$/)) {\n
          stream.backUp(1);\n
        }\n
        return style;\n
      };\n
    }\n
    function commaContinuable(column, tokenize) {\n
      return function(stream, state) {\n
        finishContinue(state);\n
        var style = tokenize(stream, state);\n
        if (stream.eol() && stream.current().match(/,$/)) {\n
          continueLine(state, column);\n
        }\n
        return style;\n
      };\n
    }\n
\n
    function rubyInQuote(endQuote, tokenize) {\n
      // TODO: add multi line support\n
      return function(stream, state) {\n
        var ch = stream.peek();\n
        if (ch == endQuote && state.rubyState.tokenize.length == 1) {\n
          // step out of ruby context as it seems to complete processing all the braces\n
          stream.next();\n
          state.tokenize = tokenize;\n
          return "closeAttributeTag";\n
        } else {\n
          return ruby(stream, state);\n
        }\n
      };\n
    }\n
    function startRubySplat(tokenize) {\n
      var rubyState;\n
      var runSplat = function(stream, state) {\n
        if (state.rubyState.tokenize.length == 1 && !state.rubyState.context.prev) {\n
          stream.backUp(1);\n
          if (stream.eatSpace()) {\n
            state.rubyState = rubyState;\n
            state.tokenize = tokenize;\n
            return tokenize(stream, state);\n
          }\n
          stream.next();\n
        }\n
        return ruby(stream, state);\n
      };\n
      return function(stream, state) {\n
        rubyState = state.rubyState;\n
        state.rubyState = rubyMode.startState();\n
        state.tokenize = runSplat;\n
        return ruby(stream, state);\n
      };\n
    }\n
\n
    function ruby(stream, state) {\n
      return rubyMode.token(stream, state.rubyState);\n
    }\n
\n
    function htmlLine(stream, state) {\n
      if (stream.match(/^\\\\$/)) {\n
        return "lineContinuation";\n
      }\n
      return html(stream, state);\n
    }\n
    function html(stream, state) {\n
      if (stream.match(/^#\\{/)) {\n
        state.tokenize = rubyInQuote("}", state.tokenize);\n
        return null;\n
      }\n
      return maybeBackup(stream, state, /[^\\\\]#\\{/, 1, htmlMode.token(stream, state.htmlState));\n
    }\n
\n
    function startHtmlLine(lastTokenize) {\n
      return function(stream, state) {\n
        var style = htmlLine(stream, state);\n
        if (stream.eol()) state.tokenize = lastTokenize;\n
        return style;\n
      };\n
    }\n
\n
    function startHtmlMode(stream, state, offset) {\n
      state.stack = {\n
        parent: state.stack,\n
        style: "html",\n
        indented: stream.column() + offset, // pipe + space\n
        tokenize: state.line\n
      };\n
      state.line = state.tokenize = html;\n
      return null;\n
    }\n
\n
    function comment(stream, state) {\n
      stream.skipToEnd();\n
      return state.stack.style;\n
    }\n
\n
    function commentMode(stream, state) {\n
      state.stack = {\n
        parent: state.stack,\n
        style: "comment",\n
        indented: state.indented + 1,\n
        tokenize: state.line\n
      };\n
      state.line = comment;\n
      return comment(stream, state);\n
    }\n
\n
    function attributeWrapper(stream, state) {\n
      if (stream.eat(state.stack.endQuote)) {\n
        state.line = state.stack.line;\n
        state.tokenize = state.stack.tokenize;\n
        state.stack = state.stack.parent;\n
        return null;\n
      }\n
      if (stream.match(wrappedAttributeNameRegexp)) {\n
        state.tokenize = attributeWrapperAssign;\n
        return "slimAttribute";\n
      }\n
      stream.next();\n
      return null;\n
    }\n
    function attributeWrapperAssign(stream, state) {\n
      if (stream.match(/^==?/)) {\n
        state.tokenize = attributeWrapperValue;\n
        return null;\n
      }\n
      return attributeWrapper(stream, state);\n
    }\n
    function attributeWrapperValue(stream, state) {\n
      var ch = stream.peek();\n
      if (ch == \'"\' || ch == "\\\'") {\n
        state.tokenize = readQuoted(ch, "string", true, false, attributeWrapper);\n
        stream.next();\n
        return state.tokenize(stream, state);\n
      }\n
      if (ch == \'[\') {\n
        return startRubySplat(attributeWrapper)(stream, state);\n
      }\n
      if (stream.match(/^(true|false|nil)\\b/)) {\n
        state.tokenize = attributeWrapper;\n
        return "keyword";\n
      }\n
      return startRubySplat(attributeWrapper)(stream, state);\n
    }\n
\n
    function startAttributeWrapperMode(state, endQuote, tokenize) {\n
      state.stack = {\n
        parent: state.stack,\n
        style: "wrapper",\n
        indented: state.indented + 1,\n
        tokenize: tokenize,\n
        line: state.line,\n
        endQuote: endQuote\n
      };\n
      state.line = state.tokenize = attributeWrapper;\n
      return null;\n
    }\n
\n
    function sub(stream, state) {\n
      if (stream.match(/^#\\{/)) {\n
        state.tokenize = rubyInQuote("}", state.tokenize);\n
        return null;\n
      }\n
      var subStream = new CodeMirror.StringStream(stream.string.slice(state.stack.indented), stream.tabSize);\n
      subStream.pos = stream.pos - state.stack.indented;\n
      subStream.start = stream.start - state.stack.indented;\n
      subStream.lastColumnPos = stream.lastColumnPos - state.stack.indented;\n
      subStream.lastColumnValue = stream.lastColumnValue - state.stack.indented;\n
      var style = state.subMode.token(subStream, state.subState);\n
      stream.pos = subStream.pos + state.stack.indented;\n
      return style;\n
    }\n
    function firstSub(stream, state) {\n
      state.stack.indented = stream.column();\n
      state.line = state.tokenize = sub;\n
      return state.tokenize(stream, state);\n
    }\n
\n
    function createMode(mode) {\n
      var query = embedded[mode];\n
      var spec = CodeMirror.mimeModes[query];\n
      if (spec) {\n
        return CodeMirror.getMode(config, spec);\n
      }\n
      var factory = CodeMirror.modes[query];\n
      if (factory) {\n
        return factory(config, {name: query});\n
      }\n
      return CodeMirror.getMode(config, "null");\n
    }\n
\n
    function getMode(mode) {\n
      if (!modes.hasOwnProperty(mode)) {\n
        return modes[mode] = createMode(mode);\n
      }\n
      return modes[mode];\n
    }\n
\n
    function startSubMode(mode, state) {\n
      var subMode = getMode(mode);\n
      var subState = subMode.startState && subMode.startState();\n
\n
      state.subMode = subMode;\n
      state.subState = subState;\n
\n
      state.stack = {\n
        parent: state.stack,\n
        style: "sub",\n
        indented: state.indented + 1,\n
        tokenize: state.line\n
      };\n
      state.line = state.tokenize = firstSub;\n
      return "slimSubmode";\n
    }\n
\n
    function doctypeLine(stream, _state) {\n
      stream.skipToEnd();\n
      return "slimDoctype";\n
    }\n
\n
    function startLine(stream, state) {\n
      var ch = stream.peek();\n
      if (ch == \'<\') {\n
        return (state.tokenize = startHtmlLine(state.tokenize))(stream, state);\n
      }\n
      if (stream.match(/^[|\']/)) {\n
        return startHtmlMode(stream, state, 1);\n
      }\n
      if (stream.match(/^\\/(!|\\[\\w+])?/)) {\n
        return commentMode(stream, state);\n
      }\n
      if (stream.match(/^(-|==?[<>]?)/)) {\n
        state.tokenize = lineContinuable(stream.column(), commaContinuable(stream.column(), ruby));\n
        return "slimSwitch";\n
      }\n
      if (stream.match(/^doctype\\b/)) {\n
        state.tokenize = doctypeLine;\n
        return "keyword";\n
      }\n
\n
      var m = stream.match(embeddedRegexp);\n
      if (m) {\n
        return startSubMode(m[1], state);\n
      }\n
\n
      return slimTag(stream, state);\n
    }\n
\n
    function slim(stream, state) {\n
      if (state.startOfLine) {\n
        return startLine(stream, state);\n
      }\n
      return slimTag(stream, state);\n
    }\n
\n
    function slimTag(stream, state) {\n
      if (stream.eat(\'*\')) {\n
        state.tokenize = startRubySplat(slimTagExtras);\n
        return null;\n
      }\n
      if (stream.match(nameRegexp)) {\n
        state.tokenize = slimTagExtras;\n
        return "slimTag";\n
      }\n
      return slimClass(stream, state);\n
    }\n
    function slimTagExtras(stream, state) {\n
      if (stream.match(/^(<>?|><?)/)) {\n
        state.tokenize = slimClass;\n
        return null;\n
      }\n
      return slimClass(stream, state);\n
    }\n
    function slimClass(stream, state) {\n
      if (stream.match(classIdRegexp)) {\n
        state.tokenize = slimClass;\n
        return "slimId";\n
      }\n
      if (stream.match(classNameRegexp)) {\n
        state.tokenize = slimClass;\n
        return "slimClass";\n
      }\n
      return slimAttribute(stream, state);\n
    }\n
    function slimAttribute(stream, state) {\n
      if (stream.match(/^([\\[\\{\\(])/)) {\n
        return startAttributeWrapperMode(state, closing[RegExp.$1], slimAttribute);\n
      }\n
      if (stream.match(attributeNameRegexp)) {\n
        state.tokenize = slimAttributeAssign;\n
        return "slimAttribute";\n
      }\n
      if (stream.peek() == \'*\') {\n
        stream.next();\n
        state.tokenize = startRubySplat(slimContent);\n
        return null;\n
      }\n
      return slimContent(stream, state);\n
    }\n
    function slimAttributeAssign(stream, state) {\n
      if (stream.match(/^==?/)) {\n
        state.tokenize = slimAttributeValue;\n
        return null;\n
      }\n
      // should never happen, because of forward lookup\n
      return slimAttribute(stream, state);\n
    }\n
\n
    function slimAttributeValue(stream, state) {\n
      var ch = stream.peek();\n
      if (ch == \'"\' || ch == "\\\'") {\n
        state.tokenize = readQuoted(ch, "string", true, false, slimAttribute);\n
        stream.next();\n
        return state.tokenize(stream, state);\n
      }\n
      if (ch == \'[\') {\n
        return startRubySplat(slimAttribute)(stream, state);\n
      }\n
      if (ch == \':\') {\n
        return startRubySplat(slimAttributeSymbols)(stream, state);\n
      }\n
      if (stream.match(/^(true|false|nil)\\b/)) {\n
        state.tokenize = slimAttribute;\n
        return "keyword";\n
      }\n
      return startRubySplat(slimAttribute)(stream, state);\n
    }\n
    function slimAttributeSymbols(stream, state) {\n
      stream.backUp(1);\n
      if (stream.match(/^[^\\s],(?=:)/)) {\n
        state.tokenize = startRubySplat(slimAttributeSymbols);\n
        return null;\n
      }\n
      stream.next();\n
      return slimAttribute(stream, state);\n
    }\n
    function readQuoted(quote, style, embed, unescaped, nextTokenize) {\n
      return function(stream, state) {\n
        finishContinue(state);\n
        var fresh = stream.current().length == 0;\n
        if (stream.match(/^\\\\$/, fresh)) {\n
          if (!fresh) return style;\n
          continueLine(state, state.indented);\n
          return "lineContinuation";\n
        }\n
        if (stream.match(/^#\\{/, fresh)) {\n
          if (!fresh) return style;\n
          state.tokenize = rubyInQuote("}", state.tokenize);\n
          return null;\n
        }\n
        var escaped = false, ch;\n
        while ((ch = stream.next()) != null) {\n
          if (ch == quote && (unescaped || !escaped)) {\n
            state.tokenize = nextTokenize;\n
            break;\n
          }\n
          if (embed && ch == "#" && !escaped) {\n
            if (stream.eat("{")) {\n
              stream.backUp(2);\n
              break;\n
            }\n
          }\n
          escaped = !escaped && ch == "\\\\";\n
        }\n
        if (stream.eol() && escaped) {\n
          stream.backUp(1);\n
        }\n
        return style;\n
      };\n
    }\n
    function slimContent(stream, state) {\n
      if (stream.match(/^==?/)) {\n
        state.tokenize = ruby;\n
        return "slimSwitch";\n
      }\n
      if (stream.match(/^\\/$/)) { // tag close hint\n
        state.tokenize = slim;\n
        return null;\n
      }\n
      if (stream.match(/^:/)) { // inline tag\n
        state.tokenize = slimTag;\n
        return "slimSwitch";\n
      }\n
      startHtmlMode(stream, state, 0);\n
      return state.tokenize(stream, state);\n
    }\n
\n
    var mode = {\n
      // default to html mode\n
      startState: function() {\n
        var htmlState = htmlMode.startState();\n
        var rubyState = rubyMode.startState();\n
        return {\n
          htmlState: htmlState,\n
          rubyState: rubyState,\n
          stack: null,\n
          last: null,\n
          tokenize: slim,\n
          line: slim,\n
          indented: 0\n
        };\n
      },\n
\n
      copyState: function(state) {\n
        return {\n
          htmlState : CodeMirror.copyState(htmlMode, state.htmlState),\n
          rubyState: CodeMirror.copyState(rubyMode, state.rubyState),\n
          subMode: state.subMode,\n
          subState: state.subMode && CodeMirror.copyState(state.subMode, state.subState),\n
          stack: state.stack,\n
          last: state.last,\n
          tokenize: state.tokenize,\n
          line: state.line\n
        };\n
      },\n
\n
      token: function(stream, state) {\n
        if (stream.sol()) {\n
          state.indented = stream.indentation();\n
          state.startOfLine = true;\n
          state.tokenize = state.line;\n
          while (state.stack && state.stack.indented > state.indented && state.last != "slimSubmode") {\n
            state.line = state.tokenize = state.stack.tokenize;\n
            state.stack = state.stack.parent;\n
            state.subMode = null;\n
            state.subState = null;\n
          }\n
        }\n
        if (stream.eatSpace()) return null;\n
        var style = state.tokenize(stream, state);\n
        state.startOfLine = false;\n
        if (style) state.last = style;\n
        return styleMap.hasOwnProperty(style) ? styleMap[style] : style;\n
      },\n
\n
      blankLine: function(state) {\n
        if (state.subMode && state.subMode.blankLine) {\n
          return state.subMode.blankLine(state.subState);\n
        }\n
      },\n
\n
      innerMode: function(state) {\n
        if (state.subMode) return {state: state.subState, mode: state.subMode};\n
        return {state: state, mode: mode};\n
      }\n
\n
      //indent: function(state) {\n
      //  return state.indented;\n
      //}\n
    };\n
    return mode;\n
  }, "htmlmixed", "ruby");\n
\n
  CodeMirror.defineMIME("text/x-slim", "slim");\n
  CodeMirror.defineMIME("application/x-slim", "slim");\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>18008</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
