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
            <value> <string>ts21897148.81</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>smartymixed.js</string> </value>
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
/**\n
* @file smartymixed.js\n
* @brief Smarty Mixed Codemirror mode (Smarty + Mixed HTML)\n
* @author Ruslan Osmanov <rrosmanov at gmail dot com>\n
* @version 3.0\n
* @date 05.07.2013\n
*/\n
\n
// Warning: Don\'t base other modes on this one. This here is a\n
// terrible way to write a mixed mode.\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") // CommonJS\n
    mod(require("../../lib/codemirror"), require("../htmlmixed/htmlmixed"), require("../smarty/smarty"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../htmlmixed/htmlmixed", "../smarty/smarty"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
"use strict";\n
\n
CodeMirror.defineMode("smartymixed", function(config) {\n
  var htmlMixedMode = CodeMirror.getMode(config, "htmlmixed");\n
  var smartyMode = CodeMirror.getMode(config, "smarty");\n
\n
  var settings = {\n
    rightDelimiter: \'}\',\n
    leftDelimiter: \'{\'\n
  };\n
\n
  if (config.hasOwnProperty("leftDelimiter")) {\n
    settings.leftDelimiter = config.leftDelimiter;\n
  }\n
  if (config.hasOwnProperty("rightDelimiter")) {\n
    settings.rightDelimiter = config.rightDelimiter;\n
  }\n
\n
  function reEsc(str) { return str.replace(/[^\\s\\w]/g, "\\\\$&"); }\n
\n
  var reLeft = reEsc(settings.leftDelimiter), reRight = reEsc(settings.rightDelimiter);\n
  var regs = {\n
    smartyComment: new RegExp("^" + reRight + "\\\\*"),\n
    literalOpen: new RegExp(reLeft + "literal" + reRight),\n
    literalClose: new RegExp(reLeft + "\\/literal" + reRight),\n
    hasLeftDelimeter: new RegExp(".*" + reLeft),\n
    htmlHasLeftDelimeter: new RegExp("[^<>]*" + reLeft)\n
  };\n
\n
  var helpers = {\n
    chain: function(stream, state, parser) {\n
      state.tokenize = parser;\n
      return parser(stream, state);\n
    },\n
\n
    cleanChain: function(stream, state, parser) {\n
      state.tokenize = null;\n
      state.localState = null;\n
      state.localMode = null;\n
      return (typeof parser == "string") ? (parser ? parser : null) : parser(stream, state);\n
    },\n
\n
    maybeBackup: function(stream, pat, style) {\n
      var cur = stream.current();\n
      var close = cur.search(pat),\n
      m;\n
      if (close > - 1) stream.backUp(cur.length - close);\n
      else if (m = cur.match(/<\\/?$/)) {\n
        stream.backUp(cur.length);\n
        if (!stream.match(pat, false)) stream.match(cur[0]);\n
      }\n
      return style;\n
    }\n
  };\n
\n
  var parsers = {\n
    html: function(stream, state) {\n
      var htmlTagName = state.htmlMixedState.htmlState.context && state.htmlMixedState.htmlState.context.tagName\n
        ? state.htmlMixedState.htmlState.context.tagName\n
        : null;\n
\n
      if (!state.inLiteral && stream.match(regs.htmlHasLeftDelimeter, false) && htmlTagName === null) {\n
        state.tokenize = parsers.smarty;\n
        state.localMode = smartyMode;\n
        state.localState = smartyMode.startState(htmlMixedMode.indent(state.htmlMixedState, ""));\n
        return helpers.maybeBackup(stream, settings.leftDelimiter, smartyMode.token(stream, state.localState));\n
      } else if (!state.inLiteral && stream.match(settings.leftDelimiter, false)) {\n
        state.tokenize = parsers.smarty;\n
        state.localMode = smartyMode;\n
        state.localState = smartyMode.startState(htmlMixedMode.indent(state.htmlMixedState, ""));\n
        return helpers.maybeBackup(stream, settings.leftDelimiter, smartyMode.token(stream, state.localState));\n
      }\n
      return htmlMixedMode.token(stream, state.htmlMixedState);\n
    },\n
\n
    smarty: function(stream, state) {\n
      if (stream.match(settings.leftDelimiter, false)) {\n
        if (stream.match(regs.smartyComment, false)) {\n
          return helpers.chain(stream, state, parsers.inBlock("comment", "*" + settings.rightDelimiter));\n
        }\n
      } else if (stream.match(settings.rightDelimiter, false)) {\n
        stream.eat(settings.rightDelimiter);\n
        state.tokenize = parsers.html;\n
        state.localMode = htmlMixedMode;\n
        state.localState = state.htmlMixedState;\n
        return "tag";\n
      }\n
\n
      return helpers.maybeBackup(stream, settings.rightDelimiter, smartyMode.token(stream, state.localState));\n
    },\n
\n
    inBlock: function(style, terminator) {\n
      return function(stream, state) {\n
        while (!stream.eol()) {\n
          if (stream.match(terminator)) {\n
            helpers.cleanChain(stream, state, "");\n
            break;\n
          }\n
          stream.next();\n
        }\n
        return style;\n
      };\n
    }\n
  };\n
\n
  return {\n
    startState: function() {\n
      var state = htmlMixedMode.startState();\n
      return {\n
        token: parsers.html,\n
        localMode: null,\n
        localState: null,\n
        htmlMixedState: state,\n
        tokenize: null,\n
        inLiteral: false\n
      };\n
    },\n
\n
    copyState: function(state) {\n
      var local = null, tok = (state.tokenize || state.token);\n
      if (state.localState) {\n
        local = CodeMirror.copyState((tok != parsers.html ? smartyMode : htmlMixedMode), state.localState);\n
      }\n
      return {\n
        token: state.token,\n
        tokenize: state.tokenize,\n
        localMode: state.localMode,\n
        localState: local,\n
        htmlMixedState: CodeMirror.copyState(htmlMixedMode, state.htmlMixedState),\n
        inLiteral: state.inLiteral\n
      };\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.match(settings.leftDelimiter, false)) {\n
        if (!state.inLiteral && stream.match(regs.literalOpen, true)) {\n
          state.inLiteral = true;\n
          return "keyword";\n
        } else if (state.inLiteral && stream.match(regs.literalClose, true)) {\n
          state.inLiteral = false;\n
          return "keyword";\n
        }\n
      }\n
      if (state.inLiteral && state.localState != state.htmlMixedState) {\n
        state.tokenize = parsers.html;\n
        state.localMode = htmlMixedMode;\n
        state.localState = state.htmlMixedState;\n
      }\n
\n
      var style = (state.tokenize || state.token)(stream, state);\n
      return style;\n
    },\n
\n
    indent: function(state, textAfter) {\n
      if (state.localMode == smartyMode\n
          || (state.inLiteral && !state.localMode)\n
         || regs.hasLeftDelimeter.test(textAfter)) {\n
        return CodeMirror.Pass;\n
      }\n
      return htmlMixedMode.indent(state.htmlMixedState, textAfter);\n
    },\n
\n
    innerMode: function(state) {\n
      return {\n
        state: state.localState || state.htmlMixedState,\n
        mode: state.localMode || htmlMixedMode\n
      };\n
    }\n
  };\n
}, "htmlmixed", "smarty");\n
\n
CodeMirror.defineMIME("text/x-smarty", "smartymixed");\n
// vim: et ts=2 sts=2 sw=2\n
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
            <value> <int>6638</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
