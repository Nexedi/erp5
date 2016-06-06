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
            <value> <string>ts21897151.16</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>doc_test.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function() {\n
  // A minilanguage for instantiating linked CodeMirror instances and Docs\n
  function instantiateSpec(spec, place, opts) {\n
    var names = {}, pos = 0, l = spec.length, editors = [];\n
    while (spec) {\n
      var m = spec.match(/^(\\w+)(\\*?)(?:=\'([^\\\']*)\'|<(~?)(\\w+)(?:\\/(\\d+)-(\\d+))?)\\s*/);\n
      var name = m[1], isDoc = m[2], cur;\n
      if (m[3]) {\n
        cur = isDoc ? CodeMirror.Doc(m[3]) : CodeMirror(place, clone(opts, {value: m[3]}));\n
      } else {\n
        var other = m[5];\n
        if (!names.hasOwnProperty(other)) {\n
          names[other] = editors.length;\n
          editors.push(CodeMirror(place, opts));\n
        }\n
        var doc = editors[names[other]].linkedDoc({\n
          sharedHist: !m[4],\n
          from: m[6] ? Number(m[6]) : null,\n
          to: m[7] ? Number(m[7]) : null\n
        });\n
        cur = isDoc ? doc : CodeMirror(place, clone(opts, {value: doc}));\n
      }\n
      names[name] = editors.length;\n
      editors.push(cur);\n
      spec = spec.slice(m[0].length);\n
    }\n
    return editors;\n
  }\n
\n
  function clone(obj, props) {\n
    if (!obj) return;\n
    clone.prototype = obj;\n
    var inst = new clone();\n
    if (props) for (var n in props) if (props.hasOwnProperty(n))\n
      inst[n] = props[n];\n
    return inst;\n
  }\n
\n
  function eqAll(val) {\n
    var end = arguments.length, msg = null;\n
    if (typeof arguments[end-1] == "string")\n
      msg = arguments[--end];\n
    if (i == end) throw new Error("No editors provided to eqAll");\n
    for (var i = 1; i < end; ++i)\n
      eq(arguments[i].getValue(), val, msg)\n
  }\n
\n
  function testDoc(name, spec, run, opts, expectFail) {\n
    if (!opts) opts = {};\n
\n
    return test("doc_" + name, function() {\n
      var place = document.getElementById("testground");\n
      var editors = instantiateSpec(spec, place, opts);\n
      var successful = false;\n
\n
      try {\n
        run.apply(null, editors);\n
        successful = true;\n
      } finally {\n
        if (!successful || verbose) {\n
          place.style.visibility = "visible";\n
        } else {\n
          for (var i = 0; i < editors.length; ++i)\n
            if (editors[i] instanceof CodeMirror)\n
              place.removeChild(editors[i].getWrapperElement());\n
        }\n
      }\n
    }, expectFail);\n
  }\n
\n
  var ie_lt8 = /MSIE [1-7]\\b/.test(navigator.userAgent);\n
\n
  function testBasic(a, b) {\n
    eqAll("x", a, b);\n
    a.setValue("hey");\n
    eqAll("hey", a, b);\n
    b.setValue("wow");\n
    eqAll("wow", a, b);\n
    a.replaceRange("u\\nv\\nw", Pos(0, 3));\n
    b.replaceRange("i", Pos(0, 4));\n
    b.replaceRange("j", Pos(2, 1));\n
    eqAll("wowui\\nv\\nwj", a, b);\n
  }\n
\n
  testDoc("basic", "A=\'x\' B<A", testBasic);\n
  testDoc("basicSeparate", "A=\'x\' B<~A", testBasic);\n
\n
  testDoc("sharedHist", "A=\'ab\\ncd\\nef\' B<A", function(a, b) {\n
    a.replaceRange("x", Pos(0));\n
    b.replaceRange("y", Pos(1));\n
    a.replaceRange("z", Pos(2));\n
    eqAll("abx\\ncdy\\nefz", a, b);\n
    a.undo();\n
    a.undo();\n
    eqAll("abx\\ncd\\nef", a, b);\n
    a.redo();\n
    eqAll("abx\\ncdy\\nef", a, b);\n
    b.redo();\n
    eqAll("abx\\ncdy\\nefz", a, b);\n
    a.undo(); b.undo(); a.undo(); a.undo();\n
    eqAll("ab\\ncd\\nef", a, b);\n
  }, null, ie_lt8);\n
\n
  testDoc("undoIntact", "A=\'ab\\ncd\\nef\' B<~A", function(a, b) {\n
    a.replaceRange("x", Pos(0));\n
    b.replaceRange("y", Pos(1));\n
    a.replaceRange("z", Pos(2));\n
    a.replaceRange("q", Pos(0));\n
    eqAll("abxq\\ncdy\\nefz", a, b);\n
    a.undo();\n
    a.undo();\n
    eqAll("abx\\ncdy\\nef", a, b);\n
    b.undo();\n
    eqAll("abx\\ncd\\nef", a, b);\n
    a.redo();\n
    eqAll("abx\\ncd\\nefz", a, b);\n
    a.redo();\n
    eqAll("abxq\\ncd\\nefz", a, b);\n
    a.undo(); a.undo(); a.undo(); a.undo();\n
    eqAll("ab\\ncd\\nef", a, b);\n
    b.redo();\n
    eqAll("ab\\ncdy\\nef", a, b);\n
  });\n
\n
  testDoc("undoConflict", "A=\'ab\\ncd\\nef\' B<~A", function(a, b) {\n
    a.replaceRange("x", Pos(0));\n
    a.replaceRange("z", Pos(2));\n
    // This should clear the first undo event in a, but not the second\n
    b.replaceRange("y", Pos(0));\n
    a.undo(); a.undo();\n
    eqAll("abxy\\ncd\\nef", a, b);\n
    a.replaceRange("u", Pos(2));\n
    a.replaceRange("v", Pos(0));\n
    // This should clear both events in a\n
    b.replaceRange("w", Pos(0));\n
    a.undo(); a.undo();\n
    eqAll("abxyvw\\ncd\\nefu", a, b);\n
  });\n
\n
  testDoc("doubleRebase", "A=\'ab\\ncd\\nef\\ng\' B<~A C<B", function(a, b, c) {\n
    c.replaceRange("u", Pos(3));\n
    a.replaceRange("", Pos(0, 0), Pos(1, 0));\n
    c.undo();\n
    eqAll("cd\\nef\\ng", a, b, c);\n
  });\n
\n
  testDoc("undoUpdate", "A=\'ab\\ncd\\nef\' B<~A", function(a, b) {\n
    a.replaceRange("x", Pos(2));\n
    b.replaceRange("u\\nv\\nw\\n", Pos(0, 0));\n
    a.undo();\n
    eqAll("u\\nv\\nw\\nab\\ncd\\nef", a, b);\n
    a.redo();\n
    eqAll("u\\nv\\nw\\nab\\ncd\\nefx", a, b);\n
    a.undo();\n
    eqAll("u\\nv\\nw\\nab\\ncd\\nef", a, b);\n
    b.undo();\n
    a.redo();\n
    eqAll("ab\\ncd\\nefx", a, b);\n
    a.undo();\n
    eqAll("ab\\ncd\\nef", a, b);\n
  });\n
\n
  testDoc("undoKeepRanges", "A=\'abcdefg\' B<A", function(a, b) {\n
    var m = a.markText(Pos(0, 1), Pos(0, 3), {className: "foo"});\n
    b.replaceRange("x", Pos(0, 0));\n
    eqPos(m.find().from, Pos(0, 2));\n
    b.replaceRange("yzzy", Pos(0, 1), Pos(0));\n
    eq(m.find(), null);\n
    b.undo();\n
    eqPos(m.find().from, Pos(0, 2));\n
    b.undo();\n
    eqPos(m.find().from, Pos(0, 1));\n
  });\n
\n
  testDoc("longChain", "A=\'uv\' B<A C<B D<C", function(a, b, c, d) {\n
    a.replaceSelection("X");\n
    eqAll("Xuv", a, b, c, d);\n
    d.replaceRange("Y", Pos(0));\n
    eqAll("XuvY", a, b, c, d);\n
  });\n
\n
  testDoc("broadCast", "B<A C<A D<A E<A", function(a, b, c, d, e) {\n
    b.setValue("uu");\n
    eqAll("uu", a, b, c, d, e);\n
    a.replaceRange("v", Pos(0, 1));\n
    eqAll("uvu", a, b, c, d, e);\n
  });\n
\n
  // A and B share a history, C and D share a separate one\n
  testDoc("islands", "A=\'x\\ny\\nz\' B<A C<~A D<C", function(a, b, c, d) {\n
    a.replaceRange("u", Pos(0));\n
    d.replaceRange("v", Pos(2));\n
    b.undo();\n
    eqAll("x\\ny\\nzv", a, b, c, d);\n
    c.undo();\n
    eqAll("x\\ny\\nz", a, b, c, d);\n
    a.redo();\n
    eqAll("xu\\ny\\nz", a, b, c, d);\n
    d.redo();\n
    eqAll("xu\\ny\\nzv", a, b, c, d);\n
  });\n
\n
  testDoc("unlink", "B<A C<A D<B", function(a, b, c, d) {\n
    a.setValue("hi");\n
    b.unlinkDoc(a);\n
    d.setValue("aye");\n
    eqAll("hi", a, c);\n
    eqAll("aye", b, d);\n
    a.setValue("oo");\n
    eqAll("oo", a, c);\n
    eqAll("aye", b, d);\n
  });\n
\n
  testDoc("bareDoc", "A*=\'foo\' B*<A C<B", function(a, b, c) {\n
    is(a instanceof CodeMirror.Doc);\n
    is(b instanceof CodeMirror.Doc);\n
    is(c instanceof CodeMirror);\n
    eqAll("foo", a, b, c);\n
    a.replaceRange("hey", Pos(0, 0), Pos(0));\n
    c.replaceRange("!", Pos(0));\n
    eqAll("hey!", a, b, c);\n
    b.unlinkDoc(a);\n
    b.setValue("x");\n
    eqAll("x", b, c);\n
    eqAll("hey!", a);\n
  });\n
\n
  testDoc("swapDoc", "A=\'a\' B*=\'b\' C<A", function(a, b, c) {\n
    var d = a.swapDoc(b);\n
    d.setValue("x");\n
    eqAll("x", c, d);\n
    eqAll("b", a, b);\n
  });\n
\n
  testDoc("docKeepsScroll", "A=\'x\' B*=\'y\'", function(a, b) {\n
    addDoc(a, 200, 200);\n
    a.scrollIntoView(Pos(199, 200));\n
    var c = a.swapDoc(b);\n
    a.swapDoc(c);\n
    var pos = a.getScrollInfo();\n
    is(pos.left > 0, "not at left");\n
    is(pos.top > 0, "not at top");\n
  });\n
\n
  testDoc("copyDoc", "A=\'u\'", function(a) {\n
    var copy = a.getDoc().copy(true);\n
    a.setValue("foo");\n
    copy.setValue("bar");\n
    var old = a.swapDoc(copy);\n
    eq(a.getValue(), "bar");\n
    a.undo();\n
    eq(a.getValue(), "u");\n
    a.swapDoc(old);\n
    eq(a.getValue(), "foo");\n
    eq(old.historySize().undo, 1);\n
    eq(old.copy(false).historySize().undo, 0);\n
  });\n
\n
  testDoc("docKeepsMode", "A=\'1+1\'", function(a) {\n
    var other = CodeMirror.Doc("hi", "text/x-markdown");\n
    a.setOption("mode", "text/javascript");\n
    var old = a.swapDoc(other);\n
    eq(a.getOption("mode"), "text/x-markdown");\n
    eq(a.getMode().name, "markdown");\n
    a.swapDoc(old);\n
    eq(a.getOption("mode"), "text/javascript");\n
    eq(a.getMode().name, "javascript");\n
  });\n
\n
  testDoc("subview", "A=\'1\\n2\\n3\\n4\\n5\' B<~A/1-3", function(a, b) {\n
    eq(b.getValue(), "2\\n3");\n
    eq(b.firstLine(), 1);\n
    b.setCursor(Pos(4));\n
    eqPos(b.getCursor(), Pos(2, 1));\n
    a.replaceRange("-1\\n0\\n", Pos(0, 0));\n
    eq(b.firstLine(), 3);\n
    eqPos(b.getCursor(), Pos(4, 1));\n
    a.undo();\n
    eqPos(b.getCursor(), Pos(2, 1));\n
    b.replaceRange("oyoy\\n", Pos(2, 0));\n
    eq(a.getValue(), "1\\n2\\noyoy\\n3\\n4\\n5");\n
    b.undo();\n
    eq(a.getValue(), "1\\n2\\n3\\n4\\n5");\n
  });\n
\n
  testDoc("subviewEditOnBoundary", "A=\'11\\n22\\n33\\n44\\n55\' B<~A/1-4", function(a, b) {\n
    a.replaceRange("x\\nyy\\nz", Pos(0, 1), Pos(2, 1));\n
    eq(b.firstLine(), 2);\n
    eq(b.lineCount(), 2);\n
    eq(b.getValue(), "z3\\n44");\n
    a.replaceRange("q\\nrr\\ns", Pos(3, 1), Pos(4, 1));\n
    eq(b.firstLine(), 2);\n
    eq(b.getValue(), "z3\\n4q");\n
    eq(a.getValue(), "1x\\nyy\\nz3\\n4q\\nrr\\ns5");\n
    a.execCommand("selectAll");\n
    a.replaceSelection("!");\n
    eqAll("!", a, b);\n
  });\n
\n
\n
  testDoc("sharedMarker", "A=\'ab\\ncd\\nef\\ngh\' B<A C<~A/1-2", function(a, b, c) {\n
    var mark = b.markText(Pos(0, 1), Pos(3, 1),\n
                          {className: "cm-searching", shared: true});\n
    var found = a.findMarksAt(Pos(0, 2));\n
    eq(found.length, 1);\n
    eq(found[0], mark);\n
    eq(c.findMarksAt(Pos(1, 1)).length, 1);\n
    eqPos(mark.find().from, Pos(0, 1));\n
    eqPos(mark.find().to, Pos(3, 1));\n
    b.replaceRange("x\\ny\\n", Pos(0, 0));\n
    eqPos(mark.find().from, Pos(2, 1));\n
    eqPos(mark.find().to, Pos(5, 1));\n
    var cleared = 0;\n
    CodeMirror.on(mark, "clear", function() {++cleared;});\n
    b.operation(function(){mark.clear();});\n
    eq(a.findMarksAt(Pos(3, 1)).length, 0);\n
    eq(b.findMarksAt(Pos(3, 1)).length, 0);\n
    eq(c.findMarksAt(Pos(3, 1)).length, 0);\n
    eq(mark.find(), null);\n
    eq(cleared, 1);\n
  });\n
\n
  testDoc("sharedMarkerCopy", "A=\'abcde\'", function(a) {\n
    var shared = a.markText(Pos(0, 1), Pos(0, 3), {shared: true});\n
    var b = a.linkedDoc();\n
    var found = b.findMarksAt(Pos(0, 2));\n
    eq(found.length, 1);\n
    eq(found[0], shared);\n
    shared.clear();\n
    eq(b.findMarksAt(Pos(0, 2)), 0);\n
  });\n
\n
  testDoc("sharedMarkerDetach", "A=\'abcde\' B<A C<B", function(a, b, c) {\n
    var shared = a.markText(Pos(0, 1), Pos(0, 3), {shared: true});\n
    a.unlinkDoc(b);\n
    var inB = b.findMarksAt(Pos(0, 2));\n
    eq(inB.length, 1);\n
    is(inB[0] != shared);\n
    var inC = c.findMarksAt(Pos(0, 2));\n
    eq(inC.length, 1);\n
    is(inC[0] != shared);\n
    inC[0].clear();\n
    is(shared.find());\n
  });\n
\n
  testDoc("sharedBookmark", "A=\'ab\\ncd\\nef\\ngh\' B<A C<~A/1-2", function(a, b, c) {\n
    var mark = b.setBookmark(Pos(1, 1), {shared: true});\n
    var found = a.findMarksAt(Pos(1, 1));\n
    eq(found.length, 1);\n
    eq(found[0], mark);\n
    eq(c.findMarksAt(Pos(1, 1)).length, 1);\n
    eqPos(mark.find(), Pos(1, 1));\n
    b.replaceRange("x\\ny\\n", Pos(0, 0));\n
    eqPos(mark.find(), Pos(3, 1));\n
    var cleared = 0;\n
    CodeMirror.on(mark, "clear", function() {++cleared;});\n
    b.operation(function() {mark.clear();});\n
    eq(a.findMarks(Pos(0, 0), Pos(5)).length, 0);\n
    eq(b.findMarks(Pos(0, 0), Pos(5)).length, 0);\n
    eq(c.findMarks(Pos(0, 0), Pos(5)).length, 0);\n
    eq(mark.find(), null);\n
    eq(cleared, 1);\n
  });\n
\n
  testDoc("undoInSubview", "A=\'line 0\\nline 1\\nline 2\\nline 3\\nline 4\' B<A/1-4", function(a, b) {\n
    b.replaceRange("x", Pos(2, 0));\n
    a.undo();\n
    eq(a.getValue(), "line 0\\nline 1\\nline 2\\nline 3\\nline 4");\n
    eq(b.getValue(), "line 1\\nline 2\\nline 3");\n
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
            <value> <int>11305</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
