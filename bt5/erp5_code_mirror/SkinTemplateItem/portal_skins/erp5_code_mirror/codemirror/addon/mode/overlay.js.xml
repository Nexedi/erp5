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
            <value> <string>ts21897115.72</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>overlay.js</string> </value>
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
// Utility function that allows modes to be combined. The mode given\n
// as the base argument takes care of most of the normal mode\n
// functionality, but a second (typically simple) mode is used, which\n
// can override the style of text. Both modes get to parse all of the\n
// text, but when both assign a non-null style to a piece of code, the\n
// overlay wins, unless the combine argument was true and not overridden,\n
// or state.overlay.combineTokens was true, in which case the styles are\n
// combined.\n
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
CodeMirror.overlayMode = function(base, overlay, combine) {\n
  return {\n
    startState: function() {\n
      return {\n
        base: CodeMirror.startState(base),\n
        overlay: CodeMirror.startState(overlay),\n
        basePos: 0, baseCur: null,\n
        overlayPos: 0, overlayCur: null,\n
        streamSeen: null\n
      };\n
    },\n
    copyState: function(state) {\n
      return {\n
        base: CodeMirror.copyState(base, state.base),\n
        overlay: CodeMirror.copyState(overlay, state.overlay),\n
        basePos: state.basePos, baseCur: null,\n
        overlayPos: state.overlayPos, overlayCur: null\n
      };\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream != state.streamSeen ||\n
          Math.min(state.basePos, state.overlayPos) < stream.start) {\n
        state.streamSeen = stream;\n
        state.basePos = state.overlayPos = stream.start;\n
      }\n
\n
      if (stream.start == state.basePos) {\n
        state.baseCur = base.token(stream, state.base);\n
        state.basePos = stream.pos;\n
      }\n
      if (stream.start == state.overlayPos) {\n
        stream.pos = stream.start;\n
        state.overlayCur = overlay.token(stream, state.overlay);\n
        state.overlayPos = stream.pos;\n
      }\n
      stream.pos = Math.min(state.basePos, state.overlayPos);\n
\n
      // state.overlay.combineTokens always takes precedence over combine,\n
      // unless set to null\n
      if (state.overlayCur == null) return state.baseCur;\n
      else if (state.baseCur != null &&\n
               state.overlay.combineTokens ||\n
               combine && state.overlay.combineTokens == null)\n
        return state.baseCur + " " + state.overlayCur;\n
      else return state.overlayCur;\n
    },\n
\n
    indent: base.indent && function(state, textAfter) {\n
      return base.indent(state.base, textAfter);\n
    },\n
    electricChars: base.electricChars,\n
\n
    innerMode: function(state) { return {state: state.base, mode: base}; },\n
\n
    blankLine: function(state) {\n
      if (base.blankLine) base.blankLine(state.base);\n
      if (overlay.blankLine) overlay.blankLine(state.overlay);\n
    }\n
  };\n
};\n
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
            <value> <int>3021</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
