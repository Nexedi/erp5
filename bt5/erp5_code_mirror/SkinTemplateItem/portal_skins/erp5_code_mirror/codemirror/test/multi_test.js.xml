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
            <value> <string>ts21897150.92</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>multi_test.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function() {\n
  namespace = "multi_";\n
\n
  function hasSelections(cm) {\n
    var sels = cm.listSelections();\n
    var given = (arguments.length - 1) / 4;\n
    if (sels.length != given)\n
      throw new Failure("expected " + given + " selections, found " + sels.length);\n
    for (var i = 0, p = 1; i < given; i++, p += 4) {\n
      var anchor = Pos(arguments[p], arguments[p + 1]);\n
      var head = Pos(arguments[p + 2], arguments[p + 3]);\n
      eqPos(sels[i].anchor, anchor, "anchor of selection " + i);\n
      eqPos(sels[i].head, head, "head of selection " + i);\n
    }\n
  }\n
  function hasCursors(cm) {\n
    var sels = cm.listSelections();\n
    var given = (arguments.length - 1) / 2;\n
    if (sels.length != given)\n
      throw new Failure("expected " + given + " selections, found " + sels.length);\n
    for (var i = 0, p = 1; i < given; i++, p += 2) {\n
      eqPos(sels[i].anchor, sels[i].head, "something selected for " + i);\n
      var head = Pos(arguments[p], arguments[p + 1]);\n
      eqPos(sels[i].head, head, "selection " + i);\n
    }\n
  }\n
\n
  testCM("getSelection", function(cm) {\n
    select(cm, {anchor: Pos(0, 0), head: Pos(1, 2)}, {anchor: Pos(2, 2), head: Pos(2, 0)});\n
    eq(cm.getSelection(), "1234\\n56\\n90");\n
    eq(cm.getSelection(false).join("|"), "1234|56|90");\n
    eq(cm.getSelections().join("|"), "1234\\n56|90");\n
  }, {value: "1234\\n5678\\n90"});\n
\n
  testCM("setSelection", function(cm) {\n
    select(cm, Pos(3, 0), Pos(0, 0), {anchor: Pos(2, 5), head: Pos(1, 0)});\n
    hasSelections(cm, 0, 0, 0, 0,\n
                  2, 5, 1, 0,\n
                  3, 0, 3, 0);\n
    cm.setSelection(Pos(1, 2), Pos(1, 1));\n
    hasSelections(cm, 1, 2, 1, 1);\n
    select(cm, {anchor: Pos(1, 1), head: Pos(2, 4)},\n
           {anchor: Pos(0, 0), head: Pos(1, 3)},\n
           Pos(3, 0), Pos(2, 2));\n
    hasSelections(cm, 0, 0, 2, 4,\n
                  3, 0, 3, 0);\n
    cm.setSelections([{anchor: Pos(0, 1), head: Pos(0, 2)},\n
                      {anchor: Pos(1, 1), head: Pos(1, 2)},\n
                      {anchor: Pos(2, 1), head: Pos(2, 2)}], 1);\n
    eqPos(cm.getCursor("head"), Pos(1, 2));\n
    eqPos(cm.getCursor("anchor"), Pos(1, 1));\n
    eqPos(cm.getCursor("from"), Pos(1, 1));\n
    eqPos(cm.getCursor("to"), Pos(1, 2));\n
    cm.setCursor(Pos(1, 1));\n
    hasCursors(cm, 1, 1);\n
  }, {value: "abcde\\nabcde\\nabcde\\n"});\n
\n
  testCM("somethingSelected", function(cm) {\n
    select(cm, Pos(0, 1), {anchor: Pos(0, 3), head: Pos(0, 5)});\n
    eq(cm.somethingSelected(), true);\n
    select(cm, Pos(0, 1), Pos(0, 3), Pos(0, 5));\n
    eq(cm.somethingSelected(), false);\n
  }, {value: "123456789"});\n
\n
  testCM("extendSelection", function(cm) {\n
    select(cm, Pos(0, 1), Pos(1, 1), Pos(2, 1));\n
    cm.setExtending(true);\n
    cm.extendSelections([Pos(0, 2), Pos(1, 0), Pos(2, 3)]);\n
    hasSelections(cm, 0, 1, 0, 2,\n
                  1, 1, 1, 0,\n
                  2, 1, 2, 3);\n
    cm.extendSelection(Pos(2, 4), Pos(2, 0));\n
    hasSelections(cm, 2, 4, 2, 0);\n
  }, {value: "1234\\n1234\\n1234"});\n
\n
  testCM("addSelection", function(cm) {\n
    select(cm, Pos(0, 1), Pos(1, 1));\n
    cm.addSelection(Pos(0, 0), Pos(0, 4));\n
    hasSelections(cm, 0, 0, 0, 4,\n
                  1, 1, 1, 1);\n
    cm.addSelection(Pos(2, 2));\n
    hasSelections(cm, 0, 0, 0, 4,\n
                  1, 1, 1, 1,\n
                  2, 2, 2, 2);\n
  }, {value: "1234\\n1234\\n1234"});\n
\n
  testCM("replaceSelection", function(cm) {\n
    var selections = [{anchor: Pos(0, 0), head: Pos(0, 1)},\n
                      {anchor: Pos(0, 2), head: Pos(0, 3)},\n
                      {anchor: Pos(0, 4), head: Pos(0, 5)},\n
                      {anchor: Pos(2, 1), head: Pos(2, 4)},\n
                      {anchor: Pos(2, 5), head: Pos(2, 6)}];\n
    var val = "123456\\n123456\\n123456";\n
    cm.setValue(val);\n
    cm.setSelections(selections);\n
    cm.replaceSelection("ab", "around");\n
    eq(cm.getValue(), "ab2ab4ab6\\n123456\\n1ab5ab");\n
    hasSelections(cm, 0, 0, 0, 2,\n
                  0, 3, 0, 5,\n
                  0, 6, 0, 8,\n
                  2, 1, 2, 3,\n
                  2, 4, 2, 6);\n
    cm.setValue(val);\n
    cm.setSelections(selections);\n
    cm.replaceSelection("", "around");\n
    eq(cm.getValue(), "246\\n123456\\n15");\n
    hasSelections(cm, 0, 0, 0, 0,\n
                  0, 1, 0, 1,\n
                  0, 2, 0, 2,\n
                  2, 1, 2, 1,\n
                  2, 2, 2, 2);\n
    cm.setValue(val);\n
    cm.setSelections(selections);\n
    cm.replaceSelection("X\\nY\\nZ", "around");\n
    hasSelections(cm, 0, 0, 2, 1,\n
                  2, 2, 4, 1,\n
                  4, 2, 6, 1,\n
                  8, 1, 10, 1,\n
                  10, 2, 12, 1);\n
    cm.replaceSelection("a", "around");\n
    hasSelections(cm, 0, 0, 0, 1,\n
                  0, 2, 0, 3,\n
                  0, 4, 0, 5,\n
                  2, 1, 2, 2,\n
                  2, 3, 2, 4);\n
    cm.replaceSelection("xy", "start");\n
    hasSelections(cm, 0, 0, 0, 0,\n
                  0, 3, 0, 3,\n
                  0, 6, 0, 6,\n
                  2, 1, 2, 1,\n
                  2, 4, 2, 4);\n
    cm.replaceSelection("z\\nf");\n
    hasSelections(cm, 1, 1, 1, 1,\n
                  2, 1, 2, 1,\n
                  3, 1, 3, 1,\n
                  6, 1, 6, 1,\n
                  7, 1, 7, 1);\n
    eq(cm.getValue(), "z\\nfxy2z\\nfxy4z\\nfxy6\\n123456\\n1z\\nfxy5z\\nfxy");\n
  });\n
\n
  function select(cm) {\n
    var sels = [];\n
    for (var i = 1; i < arguments.length; i++) {\n
      var arg = arguments[i];\n
      if (arg.head) sels.push(arg);\n
      else sels.push({head: arg, anchor: arg});\n
    }\n
    cm.setSelections(sels, sels.length - 1);\n
  }\n
\n
  testCM("indentSelection", function(cm) {\n
    select(cm, Pos(0, 1), Pos(1, 1));\n
    cm.indentSelection(4);\n
    eq(cm.getValue(), "    foo\\n    bar\\nbaz");\n
\n
    select(cm, Pos(0, 2), Pos(0, 3), Pos(0, 4));\n
    cm.indentSelection(-2);\n
    eq(cm.getValue(), "  foo\\n    bar\\nbaz");\n
\n
    select(cm, {anchor: Pos(0, 0), head: Pos(1, 2)},\n
           {anchor: Pos(1, 3), head: Pos(2, 0)});\n
    cm.indentSelection(-2);\n
    eq(cm.getValue(), "foo\\n  bar\\nbaz");\n
  }, {value: "foo\\nbar\\nbaz"});\n
\n
  testCM("killLine", function(cm) {\n
    select(cm, Pos(0, 1), Pos(0, 2), Pos(1, 1));\n
    cm.execCommand("killLine");\n
    eq(cm.getValue(), "f\\nb\\nbaz");\n
    cm.execCommand("killLine");\n
    eq(cm.getValue(), "fbbaz");\n
    cm.setValue("foo\\nbar\\nbaz");\n
    select(cm, Pos(0, 1), {anchor: Pos(0, 2), head: Pos(2, 1)});\n
    cm.execCommand("killLine");\n
    eq(cm.getValue(), "faz");\n
  }, {value: "foo\\nbar\\nbaz"});\n
\n
  testCM("deleteLine", function(cm) {\n
    select(cm, Pos(0, 0),\n
           {head: Pos(0, 1), anchor: Pos(2, 0)},\n
           Pos(4, 0));\n
    cm.execCommand("deleteLine");\n
    eq(cm.getValue(), "4\\n6\\n7");\n
    select(cm, Pos(2, 1));\n
    cm.execCommand("deleteLine");\n
    eq(cm.getValue(), "4\\n6\\n");\n
  }, {value: "1\\n2\\n3\\n4\\n5\\n6\\n7"});\n
\n
  testCM("deleteH", function(cm) {\n
    select(cm, Pos(0, 4), {anchor: Pos(1, 4), head: Pos(1, 5)});\n
    cm.execCommand("delWordAfter");\n
    eq(cm.getValue(), "foo bar baz\\nabc ef ghi\\n");\n
    cm.execCommand("delWordAfter");\n
    eq(cm.getValue(), "foo  baz\\nabc  ghi\\n");\n
    cm.execCommand("delCharBefore");\n
    cm.execCommand("delCharBefore");\n
    eq(cm.getValue(), "fo baz\\nab ghi\\n");\n
    select(cm, Pos(0, 3), Pos(0, 4), Pos(0, 5));\n
    cm.execCommand("delWordAfter");\n
    eq(cm.getValue(), "fo \\nab ghi\\n");\n
  }, {value: "foo bar baz\\nabc def ghi\\n"});\n
\n
  testCM("goLineStart", function(cm) {\n
    select(cm, Pos(0, 2), Pos(0, 3), Pos(1, 1));\n
    cm.execCommand("goLineStart");\n
    hasCursors(cm, 0, 0, 1, 0);\n
    select(cm, Pos(1, 1), Pos(0, 1));\n
    cm.setExtending(true);\n
    cm.execCommand("goLineStart");\n
    hasSelections(cm, 0, 1, 0, 0,\n
                  1, 1, 1, 0);\n
  }, {value: "foo\\nbar\\nbaz"});\n
\n
  testCM("moveV", function(cm) {\n
    select(cm, Pos(0, 2), Pos(1, 2));\n
    cm.execCommand("goLineDown");\n
    hasCursors(cm, 1, 2, 2, 2);\n
    cm.execCommand("goLineUp");\n
    hasCursors(cm, 0, 2, 1, 2);\n
    cm.execCommand("goLineUp");\n
    hasCursors(cm, 0, 0, 0, 2);\n
    cm.execCommand("goLineUp");\n
    hasCursors(cm, 0, 0);\n
    select(cm, Pos(0, 2), Pos(1, 2));\n
    cm.setExtending(true);\n
    cm.execCommand("goLineDown");\n
    hasSelections(cm, 0, 2, 2, 2);\n
  }, {value: "12345\\n12345\\n12345"});\n
\n
  testCM("moveH", function(cm) {\n
    select(cm, Pos(0, 1), Pos(0, 3), Pos(0, 5), Pos(2, 3));\n
    cm.execCommand("goCharRight");\n
    hasCursors(cm, 0, 2, 0, 4, 1, 0, 2, 4);\n
    cm.execCommand("goCharLeft");\n
    hasCursors(cm, 0, 1, 0, 3, 0, 5, 2, 3);\n
    for (var i = 0; i < 15; i++)\n
      cm.execCommand("goCharRight");\n
    hasCursors(cm, 2, 4, 2, 5);\n
  }, {value: "12345\\n12345\\n12345"});\n
\n
  testCM("newlineAndIndent", function(cm) {\n
    select(cm, Pos(0, 5), Pos(1, 5));\n
    cm.execCommand("newlineAndIndent");\n
    hasCursors(cm, 1, 2, 3, 2);\n
    eq(cm.getValue(), "x = [\\n  1];\\ny = [\\n  2];");\n
    cm.undo();\n
    eq(cm.getValue(), "x = [1];\\ny = [2];");\n
    hasCursors(cm, 0, 5, 1, 5);\n
    select(cm, Pos(0, 5), Pos(0, 6));\n
    cm.execCommand("newlineAndIndent");\n
    hasCursors(cm, 1, 2, 2, 0);\n
    eq(cm.getValue(), "x = [\\n  1\\n];\\ny = [2];");\n
  }, {value: "x = [1];\\ny = [2];", mode: "javascript"});\n
\n
  testCM("goDocStartEnd", function(cm) {\n
    select(cm, Pos(0, 1), Pos(1, 1));\n
    cm.execCommand("goDocStart");\n
    hasCursors(cm, 0, 0);\n
    select(cm, Pos(0, 1), Pos(1, 1));\n
    cm.execCommand("goDocEnd");\n
    hasCursors(cm, 1, 3);\n
    select(cm, Pos(0, 1), Pos(1, 1));\n
    cm.setExtending(true);\n
    cm.execCommand("goDocEnd");\n
    hasSelections(cm, 1, 1, 1, 3);\n
  }, {value: "abc\\ndef"});\n
\n
  testCM("selectionHistory", function(cm) {\n
    for (var i = 0; i < 3; ++i)\n
      cm.addSelection(Pos(0, i * 2), Pos(0, i * 2 + 1));\n
    cm.execCommand("undoSelection");\n
    eq(cm.getSelection(), "1\\n2");\n
    cm.execCommand("undoSelection");\n
    eq(cm.getSelection(), "1");\n
    cm.execCommand("undoSelection");\n
    eq(cm.getSelection(), "");\n
    eqPos(cm.getCursor(), Pos(0, 0));\n
    cm.execCommand("redoSelection");\n
    eq(cm.getSelection(), "1");\n
    cm.execCommand("redoSelection");\n
    eq(cm.getSelection(), "1\\n2");\n
    cm.execCommand("redoSelection");\n
    eq(cm.getSelection(), "1\\n2\\n3");\n
  }, {value: "1 2 3"});\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10033</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
