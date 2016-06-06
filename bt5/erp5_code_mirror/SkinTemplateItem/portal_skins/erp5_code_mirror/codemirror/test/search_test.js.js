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
            <value> <string>ts21897150.82</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>search_test.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function() {\n
  "use strict";\n
\n
  function test(name) {\n
    var text = Array.prototype.slice.call(arguments, 1, arguments.length - 1).join("\\n");\n
    var body = arguments[arguments.length - 1];\n
    return window.test("search_" + name, function() {\n
      body(new CodeMirror.Doc(text));\n
    });\n
  }\n
\n
  function run(doc, query, insensitive) {\n
    var cursor = doc.getSearchCursor(query, null, insensitive);\n
    for (var i = 3; i < arguments.length; i += 4) {\n
      var found = cursor.findNext();\n
      is(found, "not enough results (forward)");\n
      eqPos(Pos(arguments[i], arguments[i + 1]), cursor.from(), "from, forward, " + (i - 3) / 4);\n
      eqPos(Pos(arguments[i + 2], arguments[i + 3]), cursor.to(), "to, forward, " + (i - 3) / 4);\n
    }\n
    is(!cursor.findNext(), "too many matches (forward)");\n
    for (var i = arguments.length - 4; i >= 3; i -= 4) {\n
      var found = cursor.findPrevious();\n
      is(found, "not enough results (backwards)");\n
      eqPos(Pos(arguments[i], arguments[i + 1]), cursor.from(), "from, backwards, " + (i - 3) / 4);\n
      eqPos(Pos(arguments[i + 2], arguments[i + 3]), cursor.to(), "to, backwards, " + (i - 3) / 4);\n
    }\n
    is(!cursor.findPrevious(), "too many matches (backwards)");\n
  }\n
\n
  test("simple", "abcdefg", "abcdefg", function(doc) {\n
    run(doc, "cde", false, 0, 2, 0, 5, 1, 2, 1, 5);\n
  });\n
\n
  test("multiline", "hallo", "goodbye", function(doc) {\n
    run(doc, "llo\\ngoo", false, 0, 2, 1, 3);\n
    run(doc, "blah\\nhall", false);\n
    run(doc, "bye\\neye", false);\n
  });\n
\n
  test("regexp", "abcde", "abcde", function(doc) {\n
    run(doc, /bcd/, false, 0, 1, 0, 4, 1, 1, 1, 4);\n
    run(doc, /BCD/, false);\n
    run(doc, /BCD/i, false, 0, 1, 0, 4, 1, 1, 1, 4);\n
  });\n
\n
  test("insensitive", "hallo", "HALLO", "oink", "hAllO", function(doc) {\n
    run(doc, "All", false, 3, 1, 3, 4);\n
    run(doc, "All", true, 0, 1, 0, 4, 1, 1, 1, 4, 3, 1, 3, 4);\n
  });\n
\n
  test("multilineInsensitive", "zie ginds komT", "De Stoomboot", "uit Spanje weer aan", function(doc) {\n
    run(doc, "komt\\nde stoomboot\\nuit", false);\n
    run(doc, "komt\\nde stoomboot\\nuit", true, 0, 10, 2, 3);\n
    run(doc, "kOMt\\ndE stOOmboot\\nuiT", true, 0, 10, 2, 3);\n
  });\n
\n
  test("expandingCaseFold", "<b>İİ İİ</b>", "<b>uu uu</b>", function(doc) {\n
    if (phantom) return; // A Phantom bug makes this hang\n
    run(doc, "</b>", true, 0, 8, 0, 12, 1, 8, 1, 12);\n
    run(doc, "İİ", true, 0, 3, 0, 5, 0, 6, 0, 8);\n
  });\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2425</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
