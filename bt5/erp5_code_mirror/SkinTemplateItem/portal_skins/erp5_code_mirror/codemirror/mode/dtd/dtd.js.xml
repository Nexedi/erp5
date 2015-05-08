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
            <value> <string>ts21897150.03</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>dtd.js</string> </value>
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
  DTD mode\n
  Ported to CodeMirror by Peter Kroon <plakroon@gmail.com>\n
  Report bugs/issues here: https://github.com/codemirror/CodeMirror/issues\n
  GitHub: @peterkroon\n
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
CodeMirror.defineMode("dtd", function(config) {\n
  var indentUnit = config.indentUnit, type;\n
  function ret(style, tp) {type = tp; return style;}\n
\n
  function tokenBase(stream, state) {\n
    var ch = stream.next();\n
\n
    if (ch == "<" && stream.eat("!") ) {\n
      if (stream.eatWhile(/[\\-]/)) {\n
        state.tokenize = tokenSGMLComment;\n
        return tokenSGMLComment(stream, state);\n
      } else if (stream.eatWhile(/[\\w]/)) return ret("keyword", "doindent");\n
    } else if (ch == "<" && stream.eat("?")) { //xml declaration\n
      state.tokenize = inBlock("meta", "?>");\n
      return ret("meta", ch);\n
    } else if (ch == "#" && stream.eatWhile(/[\\w]/)) return ret("atom", "tag");\n
    else if (ch == "|") return ret("keyword", "seperator");\n
    else if (ch.match(/[\\(\\)\\[\\]\\-\\.,\\+\\?>]/)) return ret(null, ch);//if(ch === ">") return ret(null, "endtag"); else\n
    else if (ch.match(/[\\[\\]]/)) return ret("rule", ch);\n
    else if (ch == "\\"" || ch == "\'") {\n
      state.tokenize = tokenString(ch);\n
      return state.tokenize(stream, state);\n
    } else if (stream.eatWhile(/[a-zA-Z\\?\\+\\d]/)) {\n
      var sc = stream.current();\n
      if( sc.substr(sc.length-1,sc.length).match(/\\?|\\+/) !== null )stream.backUp(1);\n
      return ret("tag", "tag");\n
    } else if (ch == "%" || ch == "*" ) return ret("number", "number");\n
    else {\n
      stream.eatWhile(/[\\w\\\\\\-_%.{,]/);\n
      return ret(null, null);\n
    }\n
  }\n
\n
  function tokenSGMLComment(stream, state) {\n
    var dashes = 0, ch;\n
    while ((ch = stream.next()) != null) {\n
      if (dashes >= 2 && ch == ">") {\n
        state.tokenize = tokenBase;\n
        break;\n
      }\n
      dashes = (ch == "-") ? dashes + 1 : 0;\n
    }\n
    return ret("comment", "comment");\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var escaped = false, ch;\n
      while ((ch = stream.next()) != null) {\n
        if (ch == quote && !escaped) {\n
          state.tokenize = tokenBase;\n
          break;\n
        }\n
        escaped = !escaped && ch == "\\\\";\n
      }\n
      return ret("string", "tag");\n
    };\n
  }\n
\n
  function inBlock(style, terminator) {\n
    return function(stream, state) {\n
      while (!stream.eol()) {\n
        if (stream.match(terminator)) {\n
          state.tokenize = tokenBase;\n
          break;\n
        }\n
        stream.next();\n
      }\n
      return style;\n
    };\n
  }\n
\n
  return {\n
    startState: function(base) {\n
      return {tokenize: tokenBase,\n
              baseIndent: base || 0,\n
              stack: []};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace()) return null;\n
      var style = state.tokenize(stream, state);\n
\n
      var context = state.stack[state.stack.length-1];\n
      if (stream.current() == "[" || type === "doindent" || type == "[") state.stack.push("rule");\n
      else if (type === "endtag") state.stack[state.stack.length-1] = "endtag";\n
      else if (stream.current() == "]" || type == "]" || (type == ">" && context == "rule")) state.stack.pop();\n
      else if (type == "[") state.stack.push("[");\n
      return style;\n
    },\n
\n
    indent: function(state, textAfter) {\n
      var n = state.stack.length;\n
\n
      if( textAfter.match(/\\]\\s+|\\]/) )n=n-1;\n
      else if(textAfter.substr(textAfter.length-1, textAfter.length) === ">"){\n
        if(textAfter.substr(0,1) === "<")n;\n
        else if( type == "doindent" && textAfter.length > 1 )n;\n
        else if( type == "doindent")n--;\n
        else if( type == ">" && textAfter.length > 1)n;\n
        else if( type == "tag" && textAfter !== ">")n;\n
        else if( type == "tag" && state.stack[state.stack.length-1] == "rule")n--;\n
        else if( type == "tag")n++;\n
        else if( textAfter === ">" && state.stack[state.stack.length-1] == "rule" && type === ">")n--;\n
        else if( textAfter === ">" && state.stack[state.stack.length-1] == "rule")n;\n
        else if( textAfter.substr(0,1) !== "<" && textAfter.substr(0,1) === ">" )n=n-1;\n
        else if( textAfter === ">")n;\n
        else n=n-1;\n
        //over rule them all\n
        if(type == null || type == "]")n--;\n
      }\n
\n
      return state.baseIndent + n * indentUnit;\n
    },\n
\n
    electricChars: "]>"\n
  };\n
});\n
\n
CodeMirror.defineMIME("application/xml-dtd", "dtd");\n
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
            <value> <int>4808</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
