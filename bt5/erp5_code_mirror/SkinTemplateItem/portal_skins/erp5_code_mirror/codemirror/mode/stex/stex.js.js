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
            <value> <string>ts21897146.65</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>stex.js</string> </value>
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
/*\n
 * Author: Constantin Jucovschi (c.jucovschi@jacobs-university.de)\n
 * Licence: MIT\n
 */\n
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
  CodeMirror.defineMode("stex", function() {\n
    "use strict";\n
\n
    function pushCommand(state, command) {\n
      state.cmdState.push(command);\n
    }\n
\n
    function peekCommand(state) {\n
      if (state.cmdState.length > 0) {\n
        return state.cmdState[state.cmdState.length - 1];\n
      } else {\n
        return null;\n
      }\n
    }\n
\n
    function popCommand(state) {\n
      var plug = state.cmdState.pop();\n
      if (plug) {\n
        plug.closeBracket();\n
      }\n
    }\n
\n
    // returns the non-default plugin closest to the end of the list\n
    function getMostPowerful(state) {\n
      var context = state.cmdState;\n
      for (var i = context.length - 1; i >= 0; i--) {\n
        var plug = context[i];\n
        if (plug.name == "DEFAULT") {\n
          continue;\n
        }\n
        return plug;\n
      }\n
      return { styleIdentifier: function() { return null; } };\n
    }\n
\n
    function addPluginPattern(pluginName, cmdStyle, styles) {\n
      return function () {\n
        this.name = pluginName;\n
        this.bracketNo = 0;\n
        this.style = cmdStyle;\n
        this.styles = styles;\n
        this.argument = null;   // \\begin and \\end have arguments that follow. These are stored in the plugin\n
\n
        this.styleIdentifier = function() {\n
          return this.styles[this.bracketNo - 1] || null;\n
        };\n
        this.openBracket = function() {\n
          this.bracketNo++;\n
          return "bracket";\n
        };\n
        this.closeBracket = function() {};\n
      };\n
    }\n
\n
    var plugins = {};\n
\n
    plugins["importmodule"] = addPluginPattern("importmodule", "tag", ["string", "builtin"]);\n
    plugins["documentclass"] = addPluginPattern("documentclass", "tag", ["", "atom"]);\n
    plugins["usepackage"] = addPluginPattern("usepackage", "tag", ["atom"]);\n
    plugins["begin"] = addPluginPattern("begin", "tag", ["atom"]);\n
    plugins["end"] = addPluginPattern("end", "tag", ["atom"]);\n
\n
    plugins["DEFAULT"] = function () {\n
      this.name = "DEFAULT";\n
      this.style = "tag";\n
\n
      this.styleIdentifier = this.openBracket = this.closeBracket = function() {};\n
    };\n
\n
    function setState(state, f) {\n
      state.f = f;\n
    }\n
\n
    // called when in a normal (no environment) context\n
    function normal(source, state) {\n
      var plug;\n
      // Do we look like \'\\command\' ?  If so, attempt to apply the plugin \'command\'\n
      if (source.match(/^\\\\[a-zA-Z@]+/)) {\n
        var cmdName = source.current().slice(1);\n
        plug = plugins[cmdName] || plugins["DEFAULT"];\n
        plug = new plug();\n
        pushCommand(state, plug);\n
        setState(state, beginParams);\n
        return plug.style;\n
      }\n
\n
      // escape characters\n
      if (source.match(/^\\\\[$&%#{}_]/)) {\n
        return "tag";\n
      }\n
\n
      // white space control characters\n
      if (source.match(/^\\\\[,;!\\/\\\\]/)) {\n
        return "tag";\n
      }\n
\n
      // find if we\'re starting various math modes\n
      if (source.match("\\\\[")) {\n
        setState(state, function(source, state){ return inMathMode(source, state, "\\\\]"); });\n
        return "keyword";\n
      }\n
      if (source.match("$$")) {\n
        setState(state, function(source, state){ return inMathMode(source, state, "$$"); });\n
        return "keyword";\n
      }\n
      if (source.match("$")) {\n
        setState(state, function(source, state){ return inMathMode(source, state, "$"); });\n
        return "keyword";\n
      }\n
\n
      var ch = source.next();\n
      if (ch == "%") {\n
        source.skipToEnd();\n
        return "comment";\n
      } else if (ch == \'}\' || ch == \']\') {\n
        plug = peekCommand(state);\n
        if (plug) {\n
          plug.closeBracket(ch);\n
          setState(state, beginParams);\n
        } else {\n
          return "error";\n
        }\n
        return "bracket";\n
      } else if (ch == \'{\' || ch == \'[\') {\n
        plug = plugins["DEFAULT"];\n
        plug = new plug();\n
        pushCommand(state, plug);\n
        return "bracket";\n
      } else if (/\\d/.test(ch)) {\n
        source.eatWhile(/[\\w.%]/);\n
        return "atom";\n
      } else {\n
        source.eatWhile(/[\\w\\-_]/);\n
        plug = getMostPowerful(state);\n
        if (plug.name == \'begin\') {\n
          plug.argument = source.current();\n
        }\n
        return plug.styleIdentifier();\n
      }\n
    }\n
\n
    function inMathMode(source, state, endModeSeq) {\n
      if (source.eatSpace()) {\n
        return null;\n
      }\n
      if (source.match(endModeSeq)) {\n
        setState(state, normal);\n
        return "keyword";\n
      }\n
      if (source.match(/^\\\\[a-zA-Z@]+/)) {\n
        return "tag";\n
      }\n
      if (source.match(/^[a-zA-Z]+/)) {\n
        return "variable-2";\n
      }\n
      // escape characters\n
      if (source.match(/^\\\\[$&%#{}_]/)) {\n
        return "tag";\n
      }\n
      // white space control characters\n
      if (source.match(/^\\\\[,;!\\/]/)) {\n
        return "tag";\n
      }\n
      // special math-mode characters\n
      if (source.match(/^[\\^_&]/)) {\n
        return "tag";\n
      }\n
      // non-special characters\n
      if (source.match(/^[+\\-<>|=,\\/@!*:;\'"`~#?]/)) {\n
        return null;\n
      }\n
      if (source.match(/^(\\d+\\.\\d*|\\d*\\.\\d+|\\d+)/)) {\n
        return "number";\n
      }\n
      var ch = source.next();\n
      if (ch == "{" || ch == "}" || ch == "[" || ch == "]" || ch == "(" || ch == ")") {\n
        return "bracket";\n
      }\n
\n
      if (ch == "%") {\n
        source.skipToEnd();\n
        return "comment";\n
      }\n
      return "error";\n
    }\n
\n
    function beginParams(source, state) {\n
      var ch = source.peek(), lastPlug;\n
      if (ch == \'{\' || ch == \'[\') {\n
        lastPlug = peekCommand(state);\n
        lastPlug.openBracket(ch);\n
        source.eat(ch);\n
        setState(state, normal);\n
        return "bracket";\n
      }\n
      if (/[ \\t\\r]/.test(ch)) {\n
        source.eat(ch);\n
        return null;\n
      }\n
      setState(state, normal);\n
      popCommand(state);\n
\n
      return normal(source, state);\n
    }\n
\n
    return {\n
      startState: function() {\n
        return {\n
          cmdState: [],\n
          f: normal\n
        };\n
      },\n
      copyState: function(s) {\n
        return {\n
          cmdState: s.cmdState.slice(),\n
          f: s.f\n
        };\n
      },\n
      token: function(stream, state) {\n
        return state.f(stream, state);\n
      },\n
      blankLine: function(state) {\n
        state.f = normal;\n
        state.cmdState.length = 0;\n
      },\n
      lineComment: "%"\n
    };\n
  });\n
\n
  CodeMirror.defineMIME("text/x-stex", "stex");\n
  CodeMirror.defineMIME("text/x-latex", "stex");\n
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
            <value> <int>6932</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
