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
            <value> <string>ts21897152.14</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>sublime_test.js</string> </value>
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
  var Pos = CodeMirror.Pos;\n
  namespace = "sublime_";\n
\n
  function stTest(name) {\n
    var actions = Array.prototype.slice.call(arguments, 1);\n
    testCM(name, function(cm) {\n
      for (var i = 0; i < actions.length; i++) {\n
        var action = actions[i];\n
        if (typeof action == "string" && i == 0)\n
          cm.setValue(action);\n
        else if (typeof action == "string")\n
          cm.execCommand(action);\n
        else if (action instanceof Pos)\n
          cm.setCursor(action);\n
        else\n
          action(cm);\n
      }\n
    });\n
  }\n
\n
  function at(line, ch, msg) {\n
    return function(cm) {\n
      eq(cm.listSelections().length, 1);\n
      eqPos(cm.getCursor("head"), Pos(line, ch), msg);\n
      eqPos(cm.getCursor("anchor"), Pos(line, ch), msg);\n
    };\n
  }\n
\n
  function val(content, msg) {\n
    return function(cm) { eq(cm.getValue(), content, msg); };\n
  }\n
\n
  function argsToRanges(args) {\n
    if (args.length % 4) throw new Error("Wrong number of arguments for ranges.");\n
    var ranges = [];\n
    for (var i = 0; i < args.length; i += 4)\n
      ranges.push({anchor: Pos(args[i], args[i + 1]),\n
                   head: Pos(args[i + 2], args[i + 3])});\n
    return ranges;\n
  }\n
\n
  function setSel() {\n
    var ranges = argsToRanges(arguments);\n
    return function(cm) { cm.setSelections(ranges, 0); };\n
  }\n
\n
  function hasSel() {\n
    var ranges = argsToRanges(arguments);\n
    return function(cm) {\n
      var sels = cm.listSelections();\n
      if (sels.length != ranges.length)\n
        throw new Failure("Expected " + ranges.length + " selections, but found " + sels.length);\n
      for (var i = 0; i < sels.length; i++) {\n
        eqPos(sels[i].anchor, ranges[i].anchor, "anchor " + i);\n
        eqPos(sels[i].head, ranges[i].head, "head " + i);\n
      }\n
    };\n
  }\n
\n
  stTest("bySubword", "the foo_bar DooDahBah \\n a",\n
         "goSubwordLeft", at(0, 0),\n
         "goSubwordRight", at(0, 3),\n
         "goSubwordRight", at(0, 7),\n
         "goSubwordRight", at(0, 11),\n
         "goSubwordRight", at(0, 15),\n
         "goSubwordRight", at(0, 18),\n
         "goSubwordRight", at(0, 21),\n
         "goSubwordRight", at(0, 22),\n
         "goSubwordRight", at(1, 0),\n
         "goSubwordRight", at(1, 2),\n
         "goSubwordRight", at(1, 2),\n
         "goSubwordLeft", at(1, 1),\n
         "goSubwordLeft", at(1, 0),\n
         "goSubwordLeft", at(0, 22),\n
         "goSubwordLeft", at(0, 18),\n
         "goSubwordLeft", at(0, 15),\n
         "goSubwordLeft", at(0, 12),\n
         "goSubwordLeft", at(0, 8),\n
         "goSubwordLeft", at(0, 4),\n
         "goSubwordLeft", at(0, 0));\n
\n
  stTest("splitSelectionByLine", "abc\\ndef\\nghi",\n
         setSel(0, 1, 2, 2),\n
         "splitSelectionByLine",\n
         hasSel(0, 1, 0, 3,\n
                1, 0, 1, 3,\n
                2, 0, 2, 2));\n
\n
  stTest("splitSelectionByLineMulti", "abc\\ndef\\nghi\\njkl",\n
         setSel(0, 1, 1, 1,\n
                1, 2, 3, 2,\n
                3, 3, 3, 3),\n
         "splitSelectionByLine",\n
         hasSel(0, 1, 0, 3,\n
                1, 0, 1, 1,\n
                1, 2, 1, 3,\n
                2, 0, 2, 3,\n
                3, 0, 3, 2,\n
                3, 3, 3, 3));\n
\n
  stTest("selectLine", "abc\\ndef\\nghi",\n
         setSel(0, 1, 0, 1,\n
                2, 0, 2, 1),\n
         "selectLine",\n
         hasSel(0, 0, 1, 0,\n
                2, 0, 2, 3),\n
         setSel(0, 1, 1, 0),\n
         "selectLine",\n
         hasSel(0, 0, 2, 0));\n
\n
  stTest("insertLineAfter", "abcde\\nfghijkl\\nmn",\n
         setSel(0, 1, 0, 1,\n
                0, 3, 0, 3,\n
                1, 2, 1, 2,\n
                1, 3, 1, 5), "insertLineAfter",\n
         hasSel(1, 0, 1, 0,\n
                3, 0, 3, 0), val("abcde\\n\\nfghijkl\\n\\nmn"));\n
\n
  stTest("insertLineBefore", "abcde\\nfghijkl\\nmn",\n
         setSel(0, 1, 0, 1,\n
                0, 3, 0, 3,\n
                1, 2, 1, 2,\n
                1, 3, 1, 5), "insertLineBefore",\n
         hasSel(0, 0, 0, 0,\n
                2, 0, 2, 0), val("\\nabcde\\n\\nfghijkl\\nmn"));\n
\n
  stTest("selectNextOccurrence", "a foo bar\\nfoobar foo",\n
         setSel(0, 2, 0, 5),\n
         "selectNextOccurrence", hasSel(0, 2, 0, 5,\n
                                        1, 0, 1, 3),\n
         "selectNextOccurrence", hasSel(0, 2, 0, 5,\n
                                        1, 0, 1, 3,\n
                                        1, 7, 1, 10),\n
         "selectNextOccurrence", hasSel(0, 2, 0, 5,\n
                                        1, 0, 1, 3,\n
                                        1, 7, 1, 10),\n
         Pos(0, 3), "selectNextOccurrence", hasSel(0, 2, 0, 5),\n
        "selectNextOccurrence", hasSel(0, 2, 0, 5,\n
                                       1, 7, 1, 10),\n
         setSel(0, 6, 0, 9),\n
         "selectNextOccurrence", hasSel(0, 6, 0, 9,\n
                                        1, 3, 1, 6));\n
\n
  stTest("selectScope", "foo(a) {\\n  bar[1, 2];\\n}",\n
         "selectScope", hasSel(0, 0, 2, 1),\n
         Pos(0, 4), "selectScope", hasSel(0, 4, 0, 5),\n
         Pos(0, 5), "selectScope", hasSel(0, 4, 0, 5),\n
         Pos(0, 6), "selectScope", hasSel(0, 0, 2, 1),\n
         Pos(0, 8), "selectScope", hasSel(0, 8, 2, 0),\n
         Pos(1, 2), "selectScope", hasSel(0, 8, 2, 0),\n
         Pos(1, 6), "selectScope", hasSel(1, 6, 1, 10),\n
         Pos(1, 9), "selectScope", hasSel(1, 6, 1, 10));\n
\n
  stTest("goToBracket", "foo(a) {\\n  bar[1, 2];\\n}",\n
         Pos(0, 0), "goToBracket", at(0, 0),\n
         Pos(0, 4), "goToBracket", at(0, 5), "goToBracket", at(0, 4),\n
         Pos(0, 8), "goToBracket", at(2, 0), "goToBracket", at(0, 8),\n
         Pos(1, 2), "goToBracket", at(2, 0),\n
         Pos(1, 7), "goToBracket", at(1, 10), "goToBracket", at(1, 6));\n
\n
  stTest("swapLine", "1\\n2\\n3---\\n4\\n5",\n
         "swapLineDown", val("2\\n1\\n3---\\n4\\n5"),\n
         "swapLineUp", val("1\\n2\\n3---\\n4\\n5"),\n
         "swapLineUp", val("1\\n2\\n3---\\n4\\n5"),\n
         Pos(4, 1), "swapLineDown", val("1\\n2\\n3---\\n4\\n5"),\n
         setSel(0, 1, 0, 1,\n
                1, 0, 2, 0,\n
                2, 2, 2, 2),\n
         "swapLineDown", val("4\\n1\\n2\\n3---\\n5"),\n
         hasSel(1, 1, 1, 1,\n
                2, 0, 3, 0,\n
                3, 2, 3, 2),\n
         "swapLineUp", val("1\\n2\\n3---\\n4\\n5"),\n
         hasSel(0, 1, 0, 1,\n
                1, 0, 2, 0,\n
                2, 2, 2, 2));\n
\n
  stTest("swapLineEmptyBottomSel", "1\\n2\\n3",\n
         setSel(0, 1, 1, 0),\n
         "swapLineDown", val("2\\n1\\n3"), hasSel(1, 1, 2, 0),\n
         "swapLineUp", val("1\\n2\\n3"), hasSel(0, 1, 1, 0),\n
         "swapLineUp", val("1\\n2\\n3"), hasSel(0, 0, 0, 0));\n
\n
  stTest("swapLineUpFromEnd", "a\\nb\\nc",\n
         Pos(2, 1), "swapLineUp",\n
         hasSel(1, 1, 1, 1), val("a\\nc\\nb"));\n
\n
  stTest("joinLines", "abc\\ndef\\nghi\\njkl",\n
         "joinLines", val("abc def\\nghi\\njkl"), at(0, 4),\n
         "undo",\n
         setSel(0, 2, 1, 1), "joinLines",\n
         val("abc def ghi\\njkl"), hasSel(0, 2, 0, 8),\n
         "undo",\n
         setSel(0, 1, 0, 1,\n
                1, 1, 1, 1,\n
                3, 1, 3, 1), "joinLines",\n
         val("abc def ghi\\njkl"), hasSel(0, 4, 0, 4,\n
                                         0, 8, 0, 8,\n
                                         1, 3, 1, 3));\n
\n
  stTest("duplicateLine", "abc\\ndef\\nghi",\n
         Pos(1, 0), "duplicateLine", val("abc\\ndef\\ndef\\nghi"), at(2, 0),\n
         "undo",\n
         setSel(0, 1, 0, 1,\n
                1, 1, 1, 1,\n
                2, 1, 2, 1), "duplicateLine",\n
         val("abc\\nabc\\ndef\\ndef\\nghi\\nghi"), hasSel(1, 1, 1, 1,\n
                                                     3, 1, 3, 1,\n
                                                     5, 1, 5, 1));\n
  stTest("duplicateLineSelection", "abcdef",\n
         setSel(0, 1, 0, 1,\n
                0, 2, 0, 4,\n
                0, 5, 0, 5),\n
         "duplicateLine",\n
         val("abcdef\\nabcdcdef\\nabcdcdef"), hasSel(2, 1, 2, 1,\n
                                                   2, 4, 2, 6,\n
                                                   2, 7, 2, 7));\n
\n
  stTest("selectLinesUpward", "123\\n345\\n789\\n012",\n
         setSel(0, 1, 0, 1,\n
                1, 1, 1, 3,\n
                2, 0, 2, 0,\n
                3, 0, 3, 0),\n
         "selectLinesUpward",\n
         hasSel(0, 1, 0, 1,\n
                0, 3, 0, 3,\n
                1, 0, 1, 0,\n
                1, 1, 1, 3,\n
                2, 0, 2, 0,\n
                3, 0, 3, 0));\n
\n
  stTest("selectLinesDownward", "123\\n345\\n789\\n012",\n
         setSel(0, 1, 0, 1,\n
                1, 1, 1, 3,\n
                2, 0, 2, 0,\n
                3, 0, 3, 0),\n
         "selectLinesDownward",\n
         hasSel(0, 1, 0, 1,\n
                1, 1, 1, 3,\n
                2, 0, 2, 0,\n
                2, 3, 2, 3,\n
                3, 0, 3, 0));\n
\n
  stTest("sortLines", "c\\nb\\na\\nC\\nB\\nA",\n
         "sortLines", val("A\\nB\\nC\\na\\nb\\nc"),\n
         "undo",\n
         setSel(0, 0, 2, 0,\n
                3, 0, 5, 0),\n
         "sortLines", val("a\\nb\\nc\\nA\\nB\\nC"),\n
         hasSel(0, 0, 2, 1,\n
                3, 0, 5, 1),\n
         "undo",\n
         setSel(1, 0, 4, 0), "sortLinesInsensitive", val("c\\na\\nB\\nb\\nC\\nA"));\n
\n
  stTest("bookmarks", "abc\\ndef\\nghi\\njkl",\n
         Pos(0, 1), "toggleBookmark",\n
         setSel(1, 1, 1, 2), "toggleBookmark",\n
         setSel(2, 1, 2, 2), "toggleBookmark",\n
         "nextBookmark", hasSel(0, 1, 0, 1),\n
         "nextBookmark", hasSel(1, 1, 1, 2),\n
         "nextBookmark", hasSel(2, 1, 2, 2),\n
         "prevBookmark", hasSel(1, 1, 1, 2),\n
         "prevBookmark", hasSel(0, 1, 0, 1),\n
         "prevBookmark", hasSel(2, 1, 2, 2),\n
         "prevBookmark", hasSel(1, 1, 1, 2),\n
         "toggleBookmark",\n
         "prevBookmark", hasSel(2, 1, 2, 2),\n
         "prevBookmark", hasSel(0, 1, 0, 1),\n
         "selectBookmarks", hasSel(0, 1, 0, 1,\n
                                   2, 1, 2, 2),\n
         "clearBookmarks",\n
         Pos(0, 0), "selectBookmarks", at(0, 0));\n
\n
  stTest("upAndDowncaseAtCursor", "abc\\ndef  x\\nghI",\n
         setSel(0, 1, 0, 3,\n
                1, 1, 1, 1,\n
                1, 4, 1, 4), "upcaseAtCursor",\n
         val("aBC\\nDEF  x\\nghI"), hasSel(0, 1, 0, 3,\n
                                         1, 3, 1, 3,\n
                                         1, 4, 1, 4),\n
         "downcaseAtCursor",\n
         val("abc\\ndef  x\\nghI"), hasSel(0, 1, 0, 3,\n
                                         1, 3, 1, 3,\n
                                         1, 4, 1, 4));\n
\n
  stTest("mark", "abc\\ndef\\nghi",\n
         Pos(1, 1), "setSublimeMark",\n
         Pos(2, 1), "selectToSublimeMark", hasSel(2, 1, 1, 1),\n
         Pos(0, 1), "swapWithSublimeMark", at(1, 1), "swapWithSublimeMark", at(0, 1),\n
         "deleteToSublimeMark", val("aef\\nghi"),\n
         "sublimeYank", val("abc\\ndef\\nghi"), at(1, 1));\n
\n
  stTest("findUnder", "foo foobar  a",\n
         "findUnder", hasSel(0, 4, 0, 7),\n
         "findUnder", hasSel(0, 0, 0, 3),\n
         "findUnderPrevious", hasSel(0, 4, 0, 7),\n
         "findUnderPrevious", hasSel(0, 0, 0, 3),\n
         Pos(0, 4), "findUnder", hasSel(0, 4, 0, 10),\n
         Pos(0, 11), "findUnder", hasSel(0, 11, 0, 11));\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10876</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
