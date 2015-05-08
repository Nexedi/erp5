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
            <value> <string>ts21897145.35</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>smalltalk.js</string> </value>
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
CodeMirror.defineMode(\'smalltalk\', function(config) {\n
\n
  var specialChars = /[+\\-\\/\\\\*~<>=@%|&?!.,:;^]/;\n
  var keywords = /true|false|nil|self|super|thisContext/;\n
\n
  var Context = function(tokenizer, parent) {\n
    this.next = tokenizer;\n
    this.parent = parent;\n
  };\n
\n
  var Token = function(name, context, eos) {\n
    this.name = name;\n
    this.context = context;\n
    this.eos = eos;\n
  };\n
\n
  var State = function() {\n
    this.context = new Context(next, null);\n
    this.expectVariable = true;\n
    this.indentation = 0;\n
    this.userIndentationDelta = 0;\n
  };\n
\n
  State.prototype.userIndent = function(indentation) {\n
    this.userIndentationDelta = indentation > 0 ? (indentation / config.indentUnit - this.indentation) : 0;\n
  };\n
\n
  var next = function(stream, context, state) {\n
    var token = new Token(null, context, false);\n
    var aChar = stream.next();\n
\n
    if (aChar === \'"\') {\n
      token = nextComment(stream, new Context(nextComment, context));\n
\n
    } else if (aChar === \'\\\'\') {\n
      token = nextString(stream, new Context(nextString, context));\n
\n
    } else if (aChar === \'#\') {\n
      if (stream.peek() === \'\\\'\') {\n
        stream.next();\n
        token = nextSymbol(stream, new Context(nextSymbol, context));\n
      } else {\n
        if (stream.eatWhile(/[^\\s.{}\\[\\]()]/))\n
          token.name = \'string-2\';\n
        else\n
          token.name = \'meta\';\n
      }\n
\n
    } else if (aChar === \'$\') {\n
      if (stream.next() === \'<\') {\n
        stream.eatWhile(/[^\\s>]/);\n
        stream.next();\n
      }\n
      token.name = \'string-2\';\n
\n
    } else if (aChar === \'|\' && state.expectVariable) {\n
      token.context = new Context(nextTemporaries, context);\n
\n
    } else if (/[\\[\\]{}()]/.test(aChar)) {\n
      token.name = \'bracket\';\n
      token.eos = /[\\[{(]/.test(aChar);\n
\n
      if (aChar === \'[\') {\n
        state.indentation++;\n
      } else if (aChar === \']\') {\n
        state.indentation = Math.max(0, state.indentation - 1);\n
      }\n
\n
    } else if (specialChars.test(aChar)) {\n
      stream.eatWhile(specialChars);\n
      token.name = \'operator\';\n
      token.eos = aChar !== \';\'; // ; cascaded message expression\n
\n
    } else if (/\\d/.test(aChar)) {\n
      stream.eatWhile(/[\\w\\d]/);\n
      token.name = \'number\';\n
\n
    } else if (/[\\w_]/.test(aChar)) {\n
      stream.eatWhile(/[\\w\\d_]/);\n
      token.name = state.expectVariable ? (keywords.test(stream.current()) ? \'keyword\' : \'variable\') : null;\n
\n
    } else {\n
      token.eos = state.expectVariable;\n
    }\n
\n
    return token;\n
  };\n
\n
  var nextComment = function(stream, context) {\n
    stream.eatWhile(/[^"]/);\n
    return new Token(\'comment\', stream.eat(\'"\') ? context.parent : context, true);\n
  };\n
\n
  var nextString = function(stream, context) {\n
    stream.eatWhile(/[^\']/);\n
    return new Token(\'string\', stream.eat(\'\\\'\') ? context.parent : context, false);\n
  };\n
\n
  var nextSymbol = function(stream, context) {\n
    stream.eatWhile(/[^\']/);\n
    return new Token(\'string-2\', stream.eat(\'\\\'\') ? context.parent : context, false);\n
  };\n
\n
  var nextTemporaries = function(stream, context) {\n
    var token = new Token(null, context, false);\n
    var aChar = stream.next();\n
\n
    if (aChar === \'|\') {\n
      token.context = context.parent;\n
      token.eos = true;\n
\n
    } else {\n
      stream.eatWhile(/[^|]/);\n
      token.name = \'variable\';\n
    }\n
\n
    return token;\n
  };\n
\n
  return {\n
    startState: function() {\n
      return new State;\n
    },\n
\n
    token: function(stream, state) {\n
      state.userIndent(stream.indentation());\n
\n
      if (stream.eatSpace()) {\n
        return null;\n
      }\n
\n
      var token = state.context.next(stream, state.context, state);\n
      state.context = token.context;\n
      state.expectVariable = token.eos;\n
\n
      return token.name;\n
    },\n
\n
    blankLine: function(state) {\n
      state.userIndent(0);\n
    },\n
\n
    indent: function(state, textAfter) {\n
      var i = state.context.next === next && textAfter && textAfter.charAt(0) === \']\' ? -1 : state.userIndentationDelta;\n
      return (state.indentation + i) * config.indentUnit;\n
    },\n
\n
    electricChars: \']\'\n
  };\n
\n
});\n
\n
CodeMirror.defineMIME(\'text/x-stsrc\', {name: \'smalltalk\'});\n
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
            <value> <int>4543</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
