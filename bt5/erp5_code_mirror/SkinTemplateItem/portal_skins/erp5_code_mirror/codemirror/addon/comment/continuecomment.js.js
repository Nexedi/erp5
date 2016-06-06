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
            <value> <string>ts21897117.72</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>continuecomment.js</string> </value>
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
  var modes = ["clike", "css", "javascript"];\n
\n
  for (var i = 0; i < modes.length; ++i)\n
    CodeMirror.extendMode(modes[i], {blockCommentContinue: " * "});\n
\n
  function continueComment(cm) {\n
    if (cm.getOption("disableInput")) return CodeMirror.Pass;\n
    var ranges = cm.listSelections(), mode, inserts = [];\n
    for (var i = 0; i < ranges.length; i++) {\n
      var pos = ranges[i].head, token = cm.getTokenAt(pos);\n
      if (token.type != "comment") return CodeMirror.Pass;\n
      var modeHere = CodeMirror.innerMode(cm.getMode(), token.state).mode;\n
      if (!mode) mode = modeHere;\n
      else if (mode != modeHere) return CodeMirror.Pass;\n
\n
      var insert = null;\n
      if (mode.blockCommentStart && mode.blockCommentContinue) {\n
        var end = token.string.indexOf(mode.blockCommentEnd);\n
        var full = cm.getRange(CodeMirror.Pos(pos.line, 0), CodeMirror.Pos(pos.line, token.end)), found;\n
        if (end != -1 && end == token.string.length - mode.blockCommentEnd.length && pos.ch >= end) {\n
          // Comment ended, don\'t continue it\n
        } else if (token.string.indexOf(mode.blockCommentStart) == 0) {\n
          insert = full.slice(0, token.start);\n
          if (!/^\\s*$/.test(insert)) {\n
            insert = "";\n
            for (var j = 0; j < token.start; ++j) insert += " ";\n
          }\n
        } else if ((found = full.indexOf(mode.blockCommentContinue)) != -1 &&\n
                   found + mode.blockCommentContinue.length > token.start &&\n
                   /^\\s*$/.test(full.slice(0, found))) {\n
          insert = full.slice(0, found);\n
        }\n
        if (insert != null) insert += mode.blockCommentContinue;\n
      }\n
      if (insert == null && mode.lineComment && continueLineCommentEnabled(cm)) {\n
        var line = cm.getLine(pos.line), found = line.indexOf(mode.lineComment);\n
        if (found > -1) {\n
          insert = line.slice(0, found);\n
          if (/\\S/.test(insert)) insert = null;\n
          else insert += mode.lineComment + line.slice(found + mode.lineComment.length).match(/^\\s*/)[0];\n
        }\n
      }\n
      if (insert == null) return CodeMirror.Pass;\n
      inserts[i] = "\\n" + insert;\n
    }\n
\n
    cm.operation(function() {\n
      for (var i = ranges.length - 1; i >= 0; i--)\n
        cm.replaceRange(inserts[i], ranges[i].from(), ranges[i].to(), "+insert");\n
    });\n
  }\n
\n
  function continueLineCommentEnabled(cm) {\n
    var opt = cm.getOption("continueComments");\n
    if (opt && typeof opt == "object")\n
      return opt.continueLineComment !== false;\n
    return true;\n
  }\n
\n
  CodeMirror.defineOption("continueComments", null, function(cm, val, prev) {\n
    if (prev && prev != CodeMirror.Init)\n
      cm.removeKeyMap("continueComment");\n
    if (val) {\n
      var key = "Enter";\n
      if (typeof val == "string")\n
        key = val;\n
      else if (typeof val == "object" && val.key)\n
        key = val.key;\n
      var map = {name: "continueComment"};\n
      map[key] = continueComment;\n
      cm.addKeyMap(map);\n
    }\n
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
            <value> <int>3399</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
