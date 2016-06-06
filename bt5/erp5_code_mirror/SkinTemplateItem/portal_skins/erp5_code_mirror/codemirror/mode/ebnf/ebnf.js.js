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
            <value> <string>ts21897145.81</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ebnf.js</string> </value>
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
  CodeMirror.defineMode("ebnf", function (config) {\n
    var commentType = {slash: 0, parenthesis: 1};\n
    var stateType = {comment: 0, _string: 1, characterClass: 2};\n
    var bracesMode = null;\n
\n
    if (config.bracesMode)\n
      bracesMode = CodeMirror.getMode(config, config.bracesMode);\n
\n
    return {\n
      startState: function () {\n
        return {\n
          stringType: null,\n
          commentType: null,\n
          braced: 0,\n
          lhs: true,\n
          localState: null,\n
          stack: [],\n
          inDefinition: false\n
        };\n
      },\n
      token: function (stream, state) {\n
        if (!stream) return;\n
\n
        //check for state changes\n
        if (state.stack.length === 0) {\n
          //strings\n
          if ((stream.peek() == \'"\') || (stream.peek() == "\'")) {\n
            state.stringType = stream.peek();\n
            stream.next(); // Skip quote\n
            state.stack.unshift(stateType._string);\n
          } else if (stream.match(/^\\/\\*/)) { //comments starting with /*\n
            state.stack.unshift(stateType.comment);\n
            state.commentType = commentType.slash;\n
          } else if (stream.match(/^\\(\\*/)) { //comments starting with (*\n
            state.stack.unshift(stateType.comment);\n
            state.commentType = commentType.parenthesis;\n
          }\n
        }\n
\n
        //return state\n
        //stack has\n
        switch (state.stack[0]) {\n
        case stateType._string:\n
          while (state.stack[0] === stateType._string && !stream.eol()) {\n
            if (stream.peek() === state.stringType) {\n
              stream.next(); // Skip quote\n
              state.stack.shift(); // Clear flag\n
            } else if (stream.peek() === "\\\\") {\n
              stream.next();\n
              stream.next();\n
            } else {\n
              stream.match(/^.[^\\\\\\"\\\']*/);\n
            }\n
          }\n
          return state.lhs ? "property string" : "string"; // Token style\n
\n
        case stateType.comment:\n
          while (state.stack[0] === stateType.comment && !stream.eol()) {\n
            if (state.commentType === commentType.slash && stream.match(/\\*\\//)) {\n
              state.stack.shift(); // Clear flag\n
              state.commentType = null;\n
            } else if (state.commentType === commentType.parenthesis && stream.match(/\\*\\)/)) {\n
              state.stack.shift(); // Clear flag\n
              state.commentType = null;\n
            } else {\n
              stream.match(/^.[^\\*]*/);\n
            }\n
          }\n
          return "comment";\n
\n
        case stateType.characterClass:\n
          while (state.stack[0] === stateType.characterClass && !stream.eol()) {\n
            if (!(stream.match(/^[^\\]\\\\]+/) || stream.match(/^\\\\./))) {\n
              state.stack.shift();\n
            }\n
          }\n
          return "operator";\n
        }\n
\n
        var peek = stream.peek();\n
\n
        if (bracesMode !== null && (state.braced || peek === "{")) {\n
          if (state.localState === null)\n
            state.localState = bracesMode.startState();\n
\n
          var token = bracesMode.token(stream, state.localState),\n
          text = stream.current();\n
\n
          if (!token) {\n
            for (var i = 0; i < text.length; i++) {\n
              if (text[i] === "{") {\n
                if (state.braced === 0) {\n
                  token = "matchingbracket";\n
                }\n
                state.braced++;\n
              } else if (text[i] === "}") {\n
                state.braced--;\n
                if (state.braced === 0) {\n
                  token = "matchingbracket";\n
                }\n
              }\n
            }\n
          }\n
          return token;\n
        }\n
\n
        //no stack\n
        switch (peek) {\n
        case "[":\n
          stream.next();\n
          state.stack.unshift(stateType.characterClass);\n
          return "bracket";\n
        case ":":\n
        case "|":\n
        case ";":\n
          stream.next();\n
          return "operator";\n
        case "%":\n
          if (stream.match("%%")) {\n
            return "header";\n
          } else if (stream.match(/[%][A-Za-z]+/)) {\n
            return "keyword";\n
          } else if (stream.match(/[%][}]/)) {\n
            return "matchingbracket";\n
          }\n
          break;\n
        case "/":\n
          if (stream.match(/[\\/][A-Za-z]+/)) {\n
          return "keyword";\n
        }\n
        case "\\\\":\n
          if (stream.match(/[\\][a-z]+/)) {\n
            return "string-2";\n
          }\n
        case ".":\n
          if (stream.match(".")) {\n
            return "atom";\n
          }\n
        case "*":\n
        case "-":\n
        case "+":\n
        case "^":\n
          if (stream.match(peek)) {\n
            return "atom";\n
          }\n
        case "$":\n
          if (stream.match("$$")) {\n
            return "builtin";\n
          } else if (stream.match(/[$][0-9]+/)) {\n
            return "variable-3";\n
          }\n
        case "<":\n
          if (stream.match(/<<[a-zA-Z_]+>>/)) {\n
            return "builtin";\n
          }\n
        }\n
\n
        if (stream.match(/^\\/\\//)) {\n
          stream.skipToEnd();\n
          return "comment";\n
        } else if (stream.match(/return/)) {\n
          return "operator";\n
        } else if (stream.match(/^[a-zA-Z_][a-zA-Z0-9_]*/)) {\n
          if (stream.match(/(?=[\\(.])/)) {\n
            return "variable";\n
          } else if (stream.match(/(?=[\\s\\n]*[:=])/)) {\n
            return "def";\n
          }\n
          return "variable-2";\n
        } else if (["[", "]", "(", ")"].indexOf(stream.peek()) != -1) {\n
          stream.next();\n
          return "bracket";\n
        } else if (!stream.eatSpace()) {\n
          stream.next();\n
        }\n
        return null;\n
      }\n
    };\n
  });\n
\n
  CodeMirror.defineMIME("text/x-ebnf", "ebnf");\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6075</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
