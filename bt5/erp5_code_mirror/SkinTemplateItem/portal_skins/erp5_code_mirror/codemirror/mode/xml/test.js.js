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
            <value> <string>ts21897135.48</string> </value>
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
            <value> <string>// CodeMirror, copyright (c) by Marijn Haverbeke and others\n
// Distributed under an MIT license: http://codemirror.net/LICENSE\n
\n
(function() {\n
  var mode = CodeMirror.getMode({indentUnit: 2}, "xml"), mname = "xml";\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1), mname); }\n
\n
  MT("matching",\n
     "[tag\046bracket \074][tag top][tag\046bracket \076]",\n
     "  text",\n
     "  [tag\046bracket \074][tag inner][tag\046bracket /\076]",\n
     "[tag\046bracket \074/][tag top][tag\046bracket \076]");\n
\n
  MT("nonmatching",\n
     "[tag\046bracket \074][tag top][tag\046bracket \076]",\n
     "  [tag\046bracket \074][tag inner][tag\046bracket /\076]",\n
     "  [tag\046bracket \074/][tag\046error tip][tag\046bracket\046error \076]");\n
\n
  MT("doctype",\n
     "[meta \074!doctype foobar\076]",\n
     "[tag\046bracket \074][tag top][tag\046bracket /\076]");\n
\n
  MT("cdata",\n
     "[tag\046bracket \074][tag top][tag\046bracket \076]",\n
     "  [atom \074![CDATA[foo]",\n
     "[atom barbazguh]]]]\076]",\n
     "[tag\046bracket \074/][tag top][tag\046bracket \076]");\n
\n
  // HTML tests\n
  mode = CodeMirror.getMode({indentUnit: 2}, "text/html");\n
\n
  MT("selfclose",\n
     "[tag\046bracket \074][tag html][tag\046bracket \076]",\n
     "  [tag\046bracket \074][tag link] [attribute rel]=[string stylesheet] [attribute href]=[string \\"/foobar\\"][tag\046bracket \076]",\n
     "[tag\046bracket \074/][tag html][tag\046bracket \076]");\n
\n
  MT("list",\n
     "[tag\046bracket \074][tag ol][tag\046bracket \076]",\n
     "  [tag\046bracket \074][tag li][tag\046bracket \076]one",\n
     "  [tag\046bracket \074][tag li][tag\046bracket \076]two",\n
     "[tag\046bracket \074/][tag ol][tag\046bracket \076]");\n
\n
  MT("valueless",\n
     "[tag\046bracket \074][tag input] [attribute type]=[string checkbox] [attribute checked][tag\046bracket /\076]");\n
\n
  MT("pThenArticle",\n
     "[tag\046bracket \074][tag p][tag\046bracket \076]",\n
     "  foo",\n
     "[tag\046bracket \074][tag article][tag\046bracket \076]bar");\n
\n
})();\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1758</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
