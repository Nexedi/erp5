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
            <value> <string>ts21897147.65</string> </value>
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
// Don\'t take these too seriously -- the expected results appear to be\n
// based on the results of actual runs without any serious manual\n
// verification. If a change you made causes them to fail, the test is\n
// as likely to wrong as the code.\n
\n
(function() {\n
  var mode = CodeMirror.getMode({tabSize: 4}, "xquery");\n
  function MT(name) { test.mode(name, mode, Array.prototype.slice.call(arguments, 1)); }\n
\n
  MT("eviltest",\n
     "[keyword xquery] [keyword version] [variable &quot;1][keyword .][atom 0][keyword -][variable ml&quot;][def&variable ;]      [comment (: this is       : a          \\"comment\\" :)]",\n
     "      [keyword let] [variable $let] [keyword :=] [variable &lt;x] [variable attr][keyword =][variable &quot;value&quot;&gt;&quot;test&quot;&lt;func&gt][def&variable ;function]() [variable $var] {[keyword function]()} {[variable $var]}[variable &lt;][keyword /][variable func&gt;&lt;][keyword /][variable x&gt;]",\n
     "      [keyword let] [variable $joe][keyword :=][atom 1]",\n
     "      [keyword return] [keyword element] [variable element] {",\n
     "          [keyword attribute] [variable attribute] { [atom 1] },",\n
     "          [keyword element] [variable test] { [variable &#39;a&#39;] },           [keyword attribute] [variable foo] { [variable &quot;bar&quot;] },",\n
     "          [def&variable fn:doc]()[[ [variable foo][keyword /][variable @bar] [keyword eq] [variable $let] ]],",\n
     "          [keyword //][variable x] }                 [comment (: a more \'evil\' test :)]",\n
     "      [comment (: Modified Blakeley example (: with nested comment :) ... :)]",\n
     "      [keyword declare] [keyword private] [keyword function] [def&variable local:declare]() {()}[variable ;]",\n
     "      [keyword declare] [keyword private] [keyword function] [def&variable local:private]() {()}[variable ;]",\n
     "      [keyword declare] [keyword private] [keyword function] [def&variable local:function]() {()}[variable ;]",\n
     "      [keyword declare] [keyword private] [keyword function] [def&variable local:local]() {()}[variable ;]",\n
     "      [keyword let] [variable $let] [keyword :=] [variable &lt;let&gt;let] [variable $let] [keyword :=] [variable &quot;let&quot;&lt;][keyword /let][variable &gt;]",\n
     "      [keyword return] [keyword element] [variable element] {",\n
     "          [keyword attribute] [variable attribute] { [keyword try] { [def&variable xdmp:version]() } [keyword catch]([variable $e]) { [def&variable xdmp:log]([variable $e]) } },",\n
     "          [keyword attribute] [variable fn:doc] { [variable &quot;bar&quot;] [variable castable] [keyword as] [atom xs:string] },",\n
     "          [keyword element] [variable text] { [keyword text] { [variable &quot;text&quot;] } },",\n
     "          [def&variable fn:doc]()[[ [qualifier child::][variable eq][keyword /]([variable @bar] [keyword |] [qualifier attribute::][variable attribute]) [keyword eq] [variable $let] ]],",\n
     "          [keyword //][variable fn:doc]",\n
     "      }");\n
\n
  MT("testEmptySequenceKeyword",\n
     "[string \\"foo\\"] [keyword instance] [keyword of] [keyword empty-sequence]()");\n
\n
  MT("testMultiAttr",\n
     "[tag <p ][attribute a1]=[string \\"foo\\"] [attribute a2]=[string \\"bar\\"][tag >][variable hello] [variable world][tag </p>]");\n
\n
  MT("test namespaced variable",\n
     "[keyword declare] [keyword namespace] [variable e] [keyword =] [string \\"http://example.com/ANamespace\\"][variable ;declare] [keyword variable] [variable $e:exampleComThisVarIsNotRecognized] [keyword as] [keyword element]([keyword *]) [variable external;]");\n
\n
  MT("test EQName variable",\n
     "[keyword declare] [keyword variable] [variable $\\"http://www.example.com/ns/my\\":var] [keyword :=] [atom 12][variable ;]",\n
     "[tag <out>]{[variable $\\"http://www.example.com/ns/my\\":var]}[tag </out>]");\n
\n
  MT("test EQName function",\n
     "[keyword declare] [keyword function] [def&variable \\"http://www.example.com/ns/my\\":fn] ([variable $a] [keyword as] [atom xs:integer]) [keyword as] [atom xs:integer] {",\n
     "   [variable $a] [keyword +] [atom 2]",\n
     "}[variable ;]",\n
     "[tag <out>]{[def&variable \\"http://www.example.com/ns/my\\":fn]([atom 12])}[tag </out>]");\n
\n
  MT("test EQName function with single quotes",\n
     "[keyword declare] [keyword function] [def&variable \'http://www.example.com/ns/my\':fn] ([variable $a] [keyword as] [atom xs:integer]) [keyword as] [atom xs:integer] {",\n
     "   [variable $a] [keyword +] [atom 2]",\n
     "}[variable ;]",\n
     "[tag <out>]{[def&variable \'http://www.example.com/ns/my\':fn]([atom 12])}[tag </out>]");\n
\n
  MT("testProcessingInstructions",\n
     "[def&variable data]([comment&meta <?target content?>]) [keyword instance] [keyword of] [atom xs:string]");\n
\n
  MT("testQuoteEscapeDouble",\n
     "[keyword let] [variable $rootfolder] [keyword :=] [string \\"c:\\\\builds\\\\winnt\\\\HEAD\\\\qa\\\\scripts\\\\\\"]",\n
     "[keyword let] [variable $keysfolder] [keyword :=] [def&variable concat]([variable $rootfolder], [string \\"keys\\\\\\"])");\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5108</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
