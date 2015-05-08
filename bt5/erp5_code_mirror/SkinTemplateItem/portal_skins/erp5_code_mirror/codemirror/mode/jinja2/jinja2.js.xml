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
            <value> <string>ts21897145.11</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jinja2.js</string> </value>
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
  CodeMirror.defineMode("jinja2", function() {\n
    var keywords = ["and", "as", "block", "endblock", "by", "cycle", "debug", "else", "elif",\n
      "extends", "filter", "endfilter", "firstof", "for",\n
      "endfor", "if", "endif", "ifchanged", "endifchanged",\n
      "ifequal", "endifequal", "ifnotequal",\n
      "endifnotequal", "in", "include", "load", "not", "now", "or",\n
      "parsed", "regroup", "reversed", "spaceless",\n
      "endspaceless", "ssi", "templatetag", "openblock",\n
      "closeblock", "openvariable", "closevariable",\n
      "openbrace", "closebrace", "opencomment",\n
      "closecomment", "widthratio", "url", "with", "endwith",\n
      "get_current_language", "trans", "endtrans", "noop", "blocktrans",\n
      "endblocktrans", "get_available_languages",\n
      "get_current_language_bidi", "plural"],\n
    operator = /^[+\\-*&%=<>!?|~^]/,\n
    sign = /^[:\\[\\(\\{]/,\n
    atom = ["true", "false"],\n
    number = /^(\\d[+\\-\\*\\/])?\\d+(\\.\\d+)?/;\n
\n
    keywords = new RegExp("((" + keywords.join(")|(") + "))\\\\b");\n
    atom = new RegExp("((" + atom.join(")|(") + "))\\\\b");\n
\n
    function tokenBase (stream, state) {\n
      var ch = stream.peek();\n
\n
      //Comment\n
      if (state.incomment) {\n
        if(!stream.skipTo("#}")) {\n
          stream.skipToEnd();\n
        } else {\n
          stream.eatWhile(/\\#|}/);\n
          state.incomment = false;\n
        }\n
        return "comment";\n
      //Tag\n
      } else if (state.intag) {\n
        //After operator\n
        if(state.operator) {\n
          state.operator = false;\n
          if(stream.match(atom)) {\n
            return "atom";\n
          }\n
          if(stream.match(number)) {\n
            return "number";\n
          }\n
        }\n
        //After sign\n
        if(state.sign) {\n
          state.sign = false;\n
          if(stream.match(atom)) {\n
            return "atom";\n
          }\n
          if(stream.match(number)) {\n
            return "number";\n
          }\n
        }\n
\n
        if(state.instring) {\n
          if(ch == state.instring) {\n
            state.instring = false;\n
          }\n
          stream.next();\n
          return "string";\n
        } else if(ch == "\'" || ch == \'"\') {\n
          state.instring = ch;\n
          stream.next();\n
          return "string";\n
        } else if(stream.match(state.intag + "}") || stream.eat("-") && stream.match(state.intag + "}")) {\n
          state.intag = false;\n
          return "tag";\n
        } else if(stream.match(operator)) {\n
          state.operator = true;\n
          return "operator";\n
        } else if(stream.match(sign)) {\n
          state.sign = true;\n
        } else {\n
          if(stream.eat(" ") || stream.sol()) {\n
            if(stream.match(keywords)) {\n
              return "keyword";\n
            }\n
            if(stream.match(atom)) {\n
              return "atom";\n
            }\n
            if(stream.match(number)) {\n
              return "number";\n
            }\n
            if(stream.sol()) {\n
              stream.next();\n
            }\n
          } else {\n
            stream.next();\n
          }\n
\n
        }\n
        return "variable";\n
      } else if (stream.eat("{")) {\n
        if (ch = stream.eat("#")) {\n
          state.incomment = true;\n
          if(!stream.skipTo("#}")) {\n
            stream.skipToEnd();\n
          } else {\n
            stream.eatWhile(/\\#|}/);\n
            state.incomment = false;\n
          }\n
          return "comment";\n
        //Open tag\n
        } else if (ch = stream.eat(/\\{|%/)) {\n
          //Cache close tag\n
          state.intag = ch;\n
          if(ch == "{") {\n
            state.intag = "}";\n
          }\n
          stream.eat("-");\n
          return "tag";\n
        }\n
      }\n
      stream.next();\n
    };\n
\n
    return {\n
      startState: function () {\n
        return {tokenize: tokenBase};\n
      },\n
      token: function (stream, state) {\n
        return state.tokenize(stream, state);\n
      }\n
    };\n
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
            <value> <int>4284</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
