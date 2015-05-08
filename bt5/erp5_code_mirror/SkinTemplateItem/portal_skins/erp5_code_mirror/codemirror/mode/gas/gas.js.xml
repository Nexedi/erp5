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
            <value> <string>ts21897137.99</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>gas.js</string> </value>
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
CodeMirror.defineMode("gas", function(_config, parserConfig) {\n
  \'use strict\';\n
\n
  // If an architecture is specified, its initialization function may\n
  // populate this array with custom parsing functions which will be\n
  // tried in the event that the standard functions do not find a match.\n
  var custom = [];\n
\n
  // The symbol used to start a line comment changes based on the target\n
  // architecture.\n
  // If no architecture is pased in "parserConfig" then only multiline\n
  // comments will have syntax support.\n
  var lineCommentStartSymbol = "";\n
\n
  // These directives are architecture independent.\n
  // Machine specific directives should go in their respective\n
  // architecture initialization function.\n
  // Reference:\n
  // http://sourceware.org/binutils/docs/as/Pseudo-Ops.html#Pseudo-Ops\n
  var directives = {\n
    ".abort" : "builtin",\n
    ".align" : "builtin",\n
    ".altmacro" : "builtin",\n
    ".ascii" : "builtin",\n
    ".asciz" : "builtin",\n
    ".balign" : "builtin",\n
    ".balignw" : "builtin",\n
    ".balignl" : "builtin",\n
    ".bundle_align_mode" : "builtin",\n
    ".bundle_lock" : "builtin",\n
    ".bundle_unlock" : "builtin",\n
    ".byte" : "builtin",\n
    ".cfi_startproc" : "builtin",\n
    ".comm" : "builtin",\n
    ".data" : "builtin",\n
    ".def" : "builtin",\n
    ".desc" : "builtin",\n
    ".dim" : "builtin",\n
    ".double" : "builtin",\n
    ".eject" : "builtin",\n
    ".else" : "builtin",\n
    ".elseif" : "builtin",\n
    ".end" : "builtin",\n
    ".endef" : "builtin",\n
    ".endfunc" : "builtin",\n
    ".endif" : "builtin",\n
    ".equ" : "builtin",\n
    ".equiv" : "builtin",\n
    ".eqv" : "builtin",\n
    ".err" : "builtin",\n
    ".error" : "builtin",\n
    ".exitm" : "builtin",\n
    ".extern" : "builtin",\n
    ".fail" : "builtin",\n
    ".file" : "builtin",\n
    ".fill" : "builtin",\n
    ".float" : "builtin",\n
    ".func" : "builtin",\n
    ".global" : "builtin",\n
    ".gnu_attribute" : "builtin",\n
    ".hidden" : "builtin",\n
    ".hword" : "builtin",\n
    ".ident" : "builtin",\n
    ".if" : "builtin",\n
    ".incbin" : "builtin",\n
    ".include" : "builtin",\n
    ".int" : "builtin",\n
    ".internal" : "builtin",\n
    ".irp" : "builtin",\n
    ".irpc" : "builtin",\n
    ".lcomm" : "builtin",\n
    ".lflags" : "builtin",\n
    ".line" : "builtin",\n
    ".linkonce" : "builtin",\n
    ".list" : "builtin",\n
    ".ln" : "builtin",\n
    ".loc" : "builtin",\n
    ".loc_mark_labels" : "builtin",\n
    ".local" : "builtin",\n
    ".long" : "builtin",\n
    ".macro" : "builtin",\n
    ".mri" : "builtin",\n
    ".noaltmacro" : "builtin",\n
    ".nolist" : "builtin",\n
    ".octa" : "builtin",\n
    ".offset" : "builtin",\n
    ".org" : "builtin",\n
    ".p2align" : "builtin",\n
    ".popsection" : "builtin",\n
    ".previous" : "builtin",\n
    ".print" : "builtin",\n
    ".protected" : "builtin",\n
    ".psize" : "builtin",\n
    ".purgem" : "builtin",\n
    ".pushsection" : "builtin",\n
    ".quad" : "builtin",\n
    ".reloc" : "builtin",\n
    ".rept" : "builtin",\n
    ".sbttl" : "builtin",\n
    ".scl" : "builtin",\n
    ".section" : "builtin",\n
    ".set" : "builtin",\n
    ".short" : "builtin",\n
    ".single" : "builtin",\n
    ".size" : "builtin",\n
    ".skip" : "builtin",\n
    ".sleb128" : "builtin",\n
    ".space" : "builtin",\n
    ".stab" : "builtin",\n
    ".string" : "builtin",\n
    ".struct" : "builtin",\n
    ".subsection" : "builtin",\n
    ".symver" : "builtin",\n
    ".tag" : "builtin",\n
    ".text" : "builtin",\n
    ".title" : "builtin",\n
    ".type" : "builtin",\n
    ".uleb128" : "builtin",\n
    ".val" : "builtin",\n
    ".version" : "builtin",\n
    ".vtable_entry" : "builtin",\n
    ".vtable_inherit" : "builtin",\n
    ".warning" : "builtin",\n
    ".weak" : "builtin",\n
    ".weakref" : "builtin",\n
    ".word" : "builtin"\n
  };\n
\n
  var registers = {};\n
\n
  function x86(_parserConfig) {\n
    lineCommentStartSymbol = "#";\n
\n
    registers.ax  = "variable";\n
    registers.eax = "variable-2";\n
    registers.rax = "variable-3";\n
\n
    registers.bx  = "variable";\n
    registers.ebx = "variable-2";\n
    registers.rbx = "variable-3";\n
\n
    registers.cx  = "variable";\n
    registers.ecx = "variable-2";\n
    registers.rcx = "variable-3";\n
\n
    registers.dx  = "variable";\n
    registers.edx = "variable-2";\n
    registers.rdx = "variable-3";\n
\n
    registers.si  = "variable";\n
    registers.esi = "variable-2";\n
    registers.rsi = "variable-3";\n
\n
    registers.di  = "variable";\n
    registers.edi = "variable-2";\n
    registers.rdi = "variable-3";\n
\n
    registers.sp  = "variable";\n
    registers.esp = "variable-2";\n
    registers.rsp = "variable-3";\n
\n
    registers.bp  = "variable";\n
    registers.ebp = "variable-2";\n
    registers.rbp = "variable-3";\n
\n
    registers.ip  = "variable";\n
    registers.eip = "variable-2";\n
    registers.rip = "variable-3";\n
\n
    registers.cs  = "keyword";\n
    registers.ds  = "keyword";\n
    registers.ss  = "keyword";\n
    registers.es  = "keyword";\n
    registers.fs  = "keyword";\n
    registers.gs  = "keyword";\n
  }\n
\n
  function armv6(_parserConfig) {\n
    // Reference:\n
    // http://infocenter.arm.com/help/topic/com.arm.doc.qrc0001l/QRC0001_UAL.pdf\n
    // http://infocenter.arm.com/help/topic/com.arm.doc.ddi0301h/DDI0301H_arm1176jzfs_r0p7_trm.pdf\n
    lineCommentStartSymbol = "@";\n
    directives.syntax = "builtin";\n
\n
    registers.r0  = "variable";\n
    registers.r1  = "variable";\n
    registers.r2  = "variable";\n
    registers.r3  = "variable";\n
    registers.r4  = "variable";\n
    registers.r5  = "variable";\n
    registers.r6  = "variable";\n
    registers.r7  = "variable";\n
    registers.r8  = "variable";\n
    registers.r9  = "variable";\n
    registers.r10 = "variable";\n
    registers.r11 = "variable";\n
    registers.r12 = "variable";\n
\n
    registers.sp  = "variable-2";\n
    registers.lr  = "variable-2";\n
    registers.pc  = "variable-2";\n
    registers.r13 = registers.sp;\n
    registers.r14 = registers.lr;\n
    registers.r15 = registers.pc;\n
\n
    custom.push(function(ch, stream) {\n
      if (ch === \'#\') {\n
        stream.eatWhile(/\\w/);\n
        return "number";\n
      }\n
    });\n
  }\n
\n
  var arch = (parserConfig.architecture || "x86").toLowerCase();\n
  if (arch === "x86") {\n
    x86(parserConfig);\n
  } else if (arch === "arm" || arch === "armv6") {\n
    armv6(parserConfig);\n
  }\n
\n
  function nextUntilUnescaped(stream, end) {\n
    var escaped = false, next;\n
    while ((next = stream.next()) != null) {\n
      if (next === end && !escaped) {\n
        return false;\n
      }\n
      escaped = !escaped && next === "\\\\";\n
    }\n
    return escaped;\n
  }\n
\n
  function clikeComment(stream, state) {\n
    var maybeEnd = false, ch;\n
    while ((ch = stream.next()) != null) {\n
      if (ch === "/" && maybeEnd) {\n
        state.tokenize = null;\n
        break;\n
      }\n
      maybeEnd = (ch === "*");\n
    }\n
    return "comment";\n
  }\n
\n
  return {\n
    startState: function() {\n
      return {\n
        tokenize: null\n
      };\n
    },\n
\n
    token: function(stream, state) {\n
      if (state.tokenize) {\n
        return state.tokenize(stream, state);\n
      }\n
\n
      if (stream.eatSpace()) {\n
        return null;\n
      }\n
\n
      var style, cur, ch = stream.next();\n
\n
      if (ch === "/") {\n
        if (stream.eat("*")) {\n
          state.tokenize = clikeComment;\n
          return clikeComment(stream, state);\n
        }\n
      }\n
\n
      if (ch === lineCommentStartSymbol) {\n
        stream.skipToEnd();\n
        return "comment";\n
      }\n
\n
      if (ch === \'"\') {\n
        nextUntilUnescaped(stream, \'"\');\n
        return "string";\n
      }\n
\n
      if (ch === \'.\') {\n
        stream.eatWhile(/\\w/);\n
        cur = stream.current().toLowerCase();\n
        style = directives[cur];\n
        return style || null;\n
      }\n
\n
      if (ch === \'=\') {\n
        stream.eatWhile(/\\w/);\n
        return "tag";\n
      }\n
\n
      if (ch === \'{\') {\n
        return "braket";\n
      }\n
\n
      if (ch === \'}\') {\n
        return "braket";\n
      }\n
\n
      if (/\\d/.test(ch)) {\n
        if (ch === "0" && stream.eat("x")) {\n
          stream.eatWhile(/[0-9a-fA-F]/);\n
          return "number";\n
        }\n
        stream.eatWhile(/\\d/);\n
        return "number";\n
      }\n
\n
      if (/\\w/.test(ch)) {\n
        stream.eatWhile(/\\w/);\n
        if (stream.eat(":")) {\n
          return \'tag\';\n
        }\n
        cur = stream.current().toLowerCase();\n
        style = registers[cur];\n
        return style || null;\n
      }\n
\n
      for (var i = 0; i < custom.length; i++) {\n
        style = custom[i](ch, stream, state);\n
        if (style) {\n
          return style;\n
        }\n
      }\n
    },\n
\n
    lineComment: lineCommentStartSymbol,\n
    blockCommentStart: "/*",\n
    blockCommentEnd: "*/"\n
  };\n
});\n
\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>8886</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
