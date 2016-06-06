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
            <value> <string>ts21897140.35</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>tornado.js</string> </value>
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
    mod(require("../../lib/codemirror"), require("../htmlmixed/htmlmixed"),\n
        require("../../addon/mode/overlay"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../htmlmixed/htmlmixed",\n
            "../../addon/mode/overlay"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
  "use strict";\n
\n
  CodeMirror.defineMode("tornado:inner", function() {\n
    var keywords = ["and","as","assert","autoescape","block","break","class","comment","context",\n
                    "continue","datetime","def","del","elif","else","end","escape","except",\n
                    "exec","extends","false","finally","for","from","global","if","import","in",\n
                    "include","is","json_encode","lambda","length","linkify","load","module",\n
                    "none","not","or","pass","print","put","raise","raw","return","self","set",\n
                    "squeeze","super","true","try","url_escape","while","with","without","xhtml_escape","yield"];\n
    keywords = new RegExp("^((" + keywords.join(")|(") + "))\\\\b");\n
\n
    function tokenBase (stream, state) {\n
      stream.eatWhile(/[^\\{]/);\n
      var ch = stream.next();\n
      if (ch == "{") {\n
        if (ch = stream.eat(/\\{|%|#/)) {\n
          state.tokenize = inTag(ch);\n
          return "tag";\n
        }\n
      }\n
    }\n
    function inTag (close) {\n
      if (close == "{") {\n
        close = "}";\n
      }\n
      return function (stream, state) {\n
        var ch = stream.next();\n
        if ((ch == close) && stream.eat("}")) {\n
          state.tokenize = tokenBase;\n
          return "tag";\n
        }\n
        if (stream.match(keywords)) {\n
          return "keyword";\n
        }\n
        return close == "#" ? "comment" : "string";\n
      };\n
    }\n
    return {\n
      startState: function () {\n
        return {tokenize: tokenBase};\n
      },\n
      token: function (stream, state) {\n
        return state.tokenize(stream, state);\n
      }\n
    };\n
  });\n
\n
  CodeMirror.defineMode("tornado", function(config) {\n
    var htmlBase = CodeMirror.getMode(config, "text/html");\n
    var tornadoInner = CodeMirror.getMode(config, "tornado:inner");\n
    return CodeMirror.overlayMode(htmlBase, tornadoInner);\n
  });\n
\n
  CodeMirror.defineMIME("text/x-tornado", "tornado");\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2496</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
