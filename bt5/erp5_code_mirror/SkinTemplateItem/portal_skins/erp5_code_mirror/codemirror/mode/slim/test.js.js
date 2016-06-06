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
            <value> <string>ts21897148.06</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>test.js</string> </value>
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
(function() {\n
  var mode = CodeMirror.getMode({tabSize: 4, indentUnit: 2}, "slim");\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1)); }\n
\n
  // Requires at least one media query\n
  MT("elementName",\n
     "[tag h1] Hey There");\n
\n
  MT("oneElementPerLine",\n
     "[tag h1] Hey There .h2");\n
\n
  MT("idShortcut",\n
     "[attribute&def #test] Hey There");\n
\n
  MT("tagWithIdShortcuts",\n
     "[tag h1][attribute&def #test] Hey There");\n
\n
  MT("classShortcut",\n
     "[attribute&qualifier .hello] Hey There");\n
\n
  MT("tagWithIdAndClassShortcuts",\n
     "[tag h1][attribute&def #test][attribute&qualifier .hello] Hey There");\n
\n
  MT("docType",\n
     "[keyword doctype] xml");\n
\n
  MT("comment",\n
     "[comment / Hello WORLD]");\n
\n
  MT("notComment",\n
     "[tag h1] This is not a / comment ");\n
\n
  MT("attributes",\n
     "[tag a]([attribute title]=[string \\"test\\"]) [attribute href]=[string \\"link\\"]}");\n
\n
  MT("multiLineAttributes",\n
     "[tag a]([attribute title]=[string \\"test\\"]",\n
     "  ) [attribute href]=[string \\"link\\"]}");\n
\n
  MT("htmlCode",\n
     "[tag&bracket <][tag h1][tag&bracket >]Title[tag&bracket </][tag h1][tag&bracket >]");\n
\n
  MT("rubyBlock",\n
     "[operator&special =][variable-2 @item]");\n
\n
  MT("selectorRubyBlock",\n
     "[tag a][attribute&qualifier .test][operator&special =] [variable-2 @item]");\n
\n
  MT("nestedRubyBlock",\n
      "[tag a]",\n
      "  [operator&special =][variable puts] [string \\"test\\"]");\n
\n
  MT("multilinePlaintext",\n
      "[tag p]",\n
      "  | Hello,",\n
      "    World");\n
\n
  MT("multilineRuby",\n
      "[tag p]",\n
      "  [comment /# this is a comment]",\n
      "     [comment and this is a comment too]",\n
      "  | Date/Time",\n
      "  [operator&special -] [variable now] [operator =] [tag DateTime][operator .][property now]",\n
      "  [tag strong][operator&special =] [variable now]",\n
      "  [operator&special -] [keyword if] [variable now] [operator >] [tag DateTime][operator .][property parse]([string \\"December 31, 2006\\"])",\n
      "     [operator&special =][string \\"Happy\\"]",\n
      "     [operator&special =][string \\"Belated\\"]",\n
      "     [operator&special =][string \\"Birthday\\"]");\n
\n
  MT("multilineComment",\n
      "[comment /]",\n
      "  [comment Multiline]",\n
      "  [comment Comment]");\n
\n
  MT("hamlAfterRubyTag",\n
    "[attribute&qualifier .block]",\n
    "  [tag strong][operator&special =] [variable now]",\n
    "  [attribute&qualifier .test]",\n
    "     [operator&special =][variable now]",\n
    "  [attribute&qualifier .right]");\n
\n
  MT("stretchedRuby",\n
     "[operator&special =] [variable puts] [string \\"Hello\\"],",\n
     "   [string \\"World\\"]");\n
\n
  MT("interpolationInHashAttribute",\n
     "[tag div]{[attribute id] = [string \\"]#{[variable test]}[string _]#{[variable ting]}[string \\"]} test");\n
\n
  MT("interpolationInHTMLAttribute",\n
     "[tag div]([attribute title]=[string \\"]#{[variable test]}[string _]#{[variable ting]()}[string \\"]) Test");\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3130</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
