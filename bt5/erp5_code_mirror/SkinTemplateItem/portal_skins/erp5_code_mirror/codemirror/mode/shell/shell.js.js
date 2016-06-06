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
            <value> <string>ts21897142.05</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>shell.js</string> </value>
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
CodeMirror.defineMode(\'shell\', function() {\n
\n
  var words = {};\n
  function define(style, string) {\n
    var split = string.split(\' \');\n
    for(var i = 0; i < split.length; i++) {\n
      words[split[i]] = style;\n
    }\n
  };\n
\n
  // Atoms\n
  define(\'atom\', \'true false\');\n
\n
  // Keywords\n
  define(\'keyword\', \'if then do else elif while until for in esac fi fin \' +\n
    \'fil done exit set unset export function\');\n
\n
  // Commands\n
  define(\'builtin\', \'ab awk bash beep cat cc cd chown chmod chroot clear cp \' +\n
    \'curl cut diff echo find gawk gcc get git grep kill killall ln ls make \' +\n
    \'mkdir openssl mv nc node npm ping ps restart rm rmdir sed service sh \' +\n
    \'shopt shred source sort sleep ssh start stop su sudo tee telnet top \' +\n
    \'touch vi vim wall wc wget who write yes zsh\');\n
\n
  function tokenBase(stream, state) {\n
    if (stream.eatSpace()) return null;\n
\n
    var sol = stream.sol();\n
    var ch = stream.next();\n
\n
    if (ch === \'\\\\\') {\n
      stream.next();\n
      return null;\n
    }\n
    if (ch === \'\\\'\' || ch === \'"\' || ch === \'`\') {\n
      state.tokens.unshift(tokenString(ch));\n
      return tokenize(stream, state);\n
    }\n
    if (ch === \'#\') {\n
      if (sol && stream.eat(\'!\')) {\n
        stream.skipToEnd();\n
        return \'meta\'; // \'comment\'?\n
      }\n
      stream.skipToEnd();\n
      return \'comment\';\n
    }\n
    if (ch === \'$\') {\n
      state.tokens.unshift(tokenDollar);\n
      return tokenize(stream, state);\n
    }\n
    if (ch === \'+\' || ch === \'=\') {\n
      return \'operator\';\n
    }\n
    if (ch === \'-\') {\n
      stream.eat(\'-\');\n
      stream.eatWhile(/\\w/);\n
      return \'attribute\';\n
    }\n
    if (/\\d/.test(ch)) {\n
      stream.eatWhile(/\\d/);\n
      if(stream.eol() || !/\\w/.test(stream.peek())) {\n
        return \'number\';\n
      }\n
    }\n
    stream.eatWhile(/[\\w-]/);\n
    var cur = stream.current();\n
    if (stream.peek() === \'=\' && /\\w+/.test(cur)) return \'def\';\n
    return words.hasOwnProperty(cur) ? words[cur] : null;\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var next, end = false, escaped = false;\n
      while ((next = stream.next()) != null) {\n
        if (next === quote && !escaped) {\n
          end = true;\n
          break;\n
        }\n
        if (next === \'$\' && !escaped && quote !== \'\\\'\') {\n
          escaped = true;\n
          stream.backUp(1);\n
          state.tokens.unshift(tokenDollar);\n
          break;\n
        }\n
        escaped = !escaped && next === \'\\\\\';\n
      }\n
      if (end || !escaped) {\n
        state.tokens.shift();\n
      }\n
      return (quote === \'`\' || quote === \')\' ? \'quote\' : \'string\');\n
    };\n
  };\n
\n
  var tokenDollar = function(stream, state) {\n
    if (state.tokens.length > 1) stream.eat(\'$\');\n
    var ch = stream.next(), hungry = /\\w/;\n
    if (ch === \'{\') hungry = /[^}]/;\n
    if (ch === \'(\') {\n
      state.tokens[0] = tokenString(\')\');\n
      return tokenize(stream, state);\n
    }\n
    if (!/\\d/.test(ch)) {\n
      stream.eatWhile(hungry);\n
      stream.eat(\'}\');\n
    }\n
    state.tokens.shift();\n
    return \'def\';\n
  };\n
\n
  function tokenize(stream, state) {\n
    return (state.tokens[0] || tokenBase) (stream, state);\n
  };\n
\n
  return {\n
    startState: function() {return {tokens:[]};},\n
    token: function(stream, state) {\n
      return tokenize(stream, state);\n
    },\n
    lineComment: \'#\',\n
    fold: "brace"\n
  };\n
});\n
\n
CodeMirror.defineMIME(\'text/x-sh\', \'shell\');\n
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
            <value> <int>3792</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
