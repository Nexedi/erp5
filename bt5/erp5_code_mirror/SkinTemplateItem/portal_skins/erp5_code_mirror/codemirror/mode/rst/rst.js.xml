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
            <value> <string>ts21897146.34</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>rst.js</string> </value>
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
    mod(require("../../lib/codemirror"), require("../python/python"), require("../stex/stex"), require("../../addon/mode/overlay"));\n
  else if (typeof define == "function" && define.amd) // AMD\n
    define(["../../lib/codemirror", "../python/python", "../stex/stex", "../../addon/mode/overlay"], mod);\n
  else // Plain browser env\n
    mod(CodeMirror);\n
})(function(CodeMirror) {\n
"use strict";\n
\n
CodeMirror.defineMode(\'rst\', function (config, options) {\n
\n
  var rx_strong = /^\\*\\*[^\\*\\s](?:[^\\*]*[^\\*\\s])?\\*\\*/;\n
  var rx_emphasis = /^\\*[^\\*\\s](?:[^\\*]*[^\\*\\s])?\\*/;\n
  var rx_literal = /^``[^`\\s](?:[^`]*[^`\\s])``/;\n
\n
  var rx_number = /^(?:[\\d]+(?:[\\.,]\\d+)*)/;\n
  var rx_positive = /^(?:\\s\\+[\\d]+(?:[\\.,]\\d+)*)/;\n
  var rx_negative = /^(?:\\s\\-[\\d]+(?:[\\.,]\\d+)*)/;\n
\n
  var rx_uri_protocol = "[Hh][Tt][Tt][Pp][Ss]?://";\n
  var rx_uri_domain = "(?:[\\\\d\\\\w.-]+)\\\\.(?:\\\\w{2,6})";\n
  var rx_uri_path = "(?:/[\\\\d\\\\w\\\\#\\\\%\\\\&\\\\-\\\\.\\\\,\\\\/\\\\:\\\\=\\\\?\\\\~]+)*";\n
  var rx_uri = new RegExp("^" + rx_uri_protocol + rx_uri_domain + rx_uri_path);\n
\n
  var overlay = {\n
    token: function (stream) {\n
\n
      if (stream.match(rx_strong) && stream.match (/\\W+|$/, false))\n
        return \'strong\';\n
      if (stream.match(rx_emphasis) && stream.match (/\\W+|$/, false))\n
        return \'em\';\n
      if (stream.match(rx_literal) && stream.match (/\\W+|$/, false))\n
        return \'string-2\';\n
      if (stream.match(rx_number))\n
        return \'number\';\n
      if (stream.match(rx_positive))\n
        return \'positive\';\n
      if (stream.match(rx_negative))\n
        return \'negative\';\n
      if (stream.match(rx_uri))\n
        return \'link\';\n
\n
      while (stream.next() != null) {\n
        if (stream.match(rx_strong, false)) break;\n
        if (stream.match(rx_emphasis, false)) break;\n
        if (stream.match(rx_literal, false)) break;\n
        if (stream.match(rx_number, false)) break;\n
        if (stream.match(rx_positive, false)) break;\n
        if (stream.match(rx_negative, false)) break;\n
        if (stream.match(rx_uri, false)) break;\n
      }\n
\n
      return null;\n
    }\n
  };\n
\n
  var mode = CodeMirror.getMode(\n
    config, options.backdrop || \'rst-base\'\n
  );\n
\n
  return CodeMirror.overlayMode(mode, overlay, true); // combine\n
}, \'python\', \'stex\');\n
\n
///////////////////////////////////////////////////////////////////////////////\n
///////////////////////////////////////////////////////////////////////////////\n
\n
CodeMirror.defineMode(\'rst-base\', function (config) {\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function format(string) {\n
    var args = Array.prototype.slice.call(arguments, 1);\n
    return string.replace(/{(\\d+)}/g, function (match, n) {\n
      return typeof args[n] != \'undefined\' ? args[n] : match;\n
    });\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  var mode_python = CodeMirror.getMode(config, \'python\');\n
  var mode_stex = CodeMirror.getMode(config, \'stex\');\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  var SEPA = "\\\\s+";\n
  var TAIL = "(?:\\\\s*|\\\\W|$)",\n
  rx_TAIL = new RegExp(format(\'^{0}\', TAIL));\n
\n
  var NAME =\n
    "(?:[^\\\\W\\\\d_](?:[\\\\w!\\"#$%&\'()\\\\*\\\\+,\\\\-\\\\.\\/:;<=>\\\\?]*[^\\\\W_])?)",\n
  rx_NAME = new RegExp(format(\'^{0}\', NAME));\n
  var NAME_WWS =\n
    "(?:[^\\\\W\\\\d_](?:[\\\\w\\\\s!\\"#$%&\'()\\\\*\\\\+,\\\\-\\\\.\\/:;<=>\\\\?]*[^\\\\W_])?)";\n
  var REF_NAME = format(\'(?:{0}|`{1}`)\', NAME, NAME_WWS);\n
\n
  var TEXT1 = "(?:[^\\\\s\\\\|](?:[^\\\\|]*[^\\\\s\\\\|])?)";\n
  var TEXT2 = "(?:[^\\\\`]+)",\n
  rx_TEXT2 = new RegExp(format(\'^{0}\', TEXT2));\n
\n
  var rx_section = new RegExp(\n
    "^([!\'#$%&\\"()*+,-./:;<=>?@\\\\[\\\\\\\\\\\\]^_`{|}~])\\\\1{3,}\\\\s*$");\n
  var rx_explicit = new RegExp(\n
    format(\'^\\\\.\\\\.{0}\', SEPA));\n
  var rx_link = new RegExp(\n
    format(\'^_{0}:{1}|^__:{1}\', REF_NAME, TAIL));\n
  var rx_directive = new RegExp(\n
    format(\'^{0}::{1}\', REF_NAME, TAIL));\n
  var rx_substitution = new RegExp(\n
    format(\'^\\\\|{0}\\\\|{1}{2}::{3}\', TEXT1, SEPA, REF_NAME, TAIL));\n
  var rx_footnote = new RegExp(\n
    format(\'^\\\\[(?:\\\\d+|#{0}?|\\\\*)]{1}\', REF_NAME, TAIL));\n
  var rx_citation = new RegExp(\n
    format(\'^\\\\[{0}\\\\]{1}\', REF_NAME, TAIL));\n
\n
  var rx_substitution_ref = new RegExp(\n
    format(\'^\\\\|{0}\\\\|\', TEXT1));\n
  var rx_footnote_ref = new RegExp(\n
    format(\'^\\\\[(?:\\\\d+|#{0}?|\\\\*)]_\', REF_NAME));\n
  var rx_citation_ref = new RegExp(\n
    format(\'^\\\\[{0}\\\\]_\', REF_NAME));\n
  var rx_link_ref1 = new RegExp(\n
    format(\'^{0}__?\', REF_NAME));\n
  var rx_link_ref2 = new RegExp(\n
    format(\'^`{0}`_\', TEXT2));\n
\n
  var rx_role_pre = new RegExp(\n
    format(\'^:{0}:`{1}`{2}\', NAME, TEXT2, TAIL));\n
  var rx_role_suf = new RegExp(\n
    format(\'^`{1}`:{0}:{2}\', NAME, TEXT2, TAIL));\n
  var rx_role = new RegExp(\n
    format(\'^:{0}:{1}\', NAME, TAIL));\n
\n
  var rx_directive_name = new RegExp(format(\'^{0}\', REF_NAME));\n
  var rx_directive_tail = new RegExp(format(\'^::{0}\', TAIL));\n
  var rx_substitution_text = new RegExp(format(\'^\\\\|{0}\\\\|\', TEXT1));\n
  var rx_substitution_sepa = new RegExp(format(\'^{0}\', SEPA));\n
  var rx_substitution_name = new RegExp(format(\'^{0}\', REF_NAME));\n
  var rx_substitution_tail = new RegExp(format(\'^::{0}\', TAIL));\n
  var rx_link_head = new RegExp("^_");\n
  var rx_link_name = new RegExp(format(\'^{0}|_\', REF_NAME));\n
  var rx_link_tail = new RegExp(format(\'^:{0}\', TAIL));\n
\n
  var rx_verbatim = new RegExp(\'^::\\\\s*$\');\n
  var rx_examples = new RegExp(\'^\\\\s+(?:>>>|In \\\\[\\\\d+\\\\]:)\\\\s\');\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function to_normal(stream, state) {\n
    var token = null;\n
\n
    if (stream.sol() && stream.match(rx_examples, false)) {\n
      change(state, to_mode, {\n
        mode: mode_python, local: CodeMirror.startState(mode_python)\n
      });\n
    } else if (stream.sol() && stream.match(rx_explicit)) {\n
      change(state, to_explicit);\n
      token = \'meta\';\n
    } else if (stream.sol() && stream.match(rx_section)) {\n
      change(state, to_normal);\n
      token = \'header\';\n
    } else if (phase(state) == rx_role_pre ||\n
               stream.match(rx_role_pre, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_normal, context(rx_role_pre, 1));\n
        stream.match(/^:/);\n
        token = \'meta\';\n
        break;\n
      case 1:\n
        change(state, to_normal, context(rx_role_pre, 2));\n
        stream.match(rx_NAME);\n
        token = \'keyword\';\n
\n
        if (stream.current().match(/^(?:math|latex)/)) {\n
          state.tmp_stex = true;\n
        }\n
        break;\n
      case 2:\n
        change(state, to_normal, context(rx_role_pre, 3));\n
        stream.match(/^:`/);\n
        token = \'meta\';\n
        break;\n
      case 3:\n
        if (state.tmp_stex) {\n
          state.tmp_stex = undefined; state.tmp = {\n
            mode: mode_stex, local: CodeMirror.startState(mode_stex)\n
          };\n
        }\n
\n
        if (state.tmp) {\n
          if (stream.peek() == \'`\') {\n
            change(state, to_normal, context(rx_role_pre, 4));\n
            state.tmp = undefined;\n
            break;\n
          }\n
\n
          token = state.tmp.mode.token(stream, state.tmp.local);\n
          break;\n
        }\n
\n
        change(state, to_normal, context(rx_role_pre, 4));\n
        stream.match(rx_TEXT2);\n
        token = \'string\';\n
        break;\n
      case 4:\n
        change(state, to_normal, context(rx_role_pre, 5));\n
        stream.match(/^`/);\n
        token = \'meta\';\n
        break;\n
      case 5:\n
        change(state, to_normal, context(rx_role_pre, 6));\n
        stream.match(rx_TAIL);\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (phase(state) == rx_role_suf ||\n
               stream.match(rx_role_suf, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_normal, context(rx_role_suf, 1));\n
        stream.match(/^`/);\n
        token = \'meta\';\n
        break;\n
      case 1:\n
        change(state, to_normal, context(rx_role_suf, 2));\n
        stream.match(rx_TEXT2);\n
        token = \'string\';\n
        break;\n
      case 2:\n
        change(state, to_normal, context(rx_role_suf, 3));\n
        stream.match(/^`:/);\n
        token = \'meta\';\n
        break;\n
      case 3:\n
        change(state, to_normal, context(rx_role_suf, 4));\n
        stream.match(rx_NAME);\n
        token = \'keyword\';\n
        break;\n
      case 4:\n
        change(state, to_normal, context(rx_role_suf, 5));\n
        stream.match(/^:/);\n
        token = \'meta\';\n
        break;\n
      case 5:\n
        change(state, to_normal, context(rx_role_suf, 6));\n
        stream.match(rx_TAIL);\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (phase(state) == rx_role || stream.match(rx_role, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_normal, context(rx_role, 1));\n
        stream.match(/^:/);\n
        token = \'meta\';\n
        break;\n
      case 1:\n
        change(state, to_normal, context(rx_role, 2));\n
        stream.match(rx_NAME);\n
        token = \'keyword\';\n
        break;\n
      case 2:\n
        change(state, to_normal, context(rx_role, 3));\n
        stream.match(/^:/);\n
        token = \'meta\';\n
        break;\n
      case 3:\n
        change(state, to_normal, context(rx_role, 4));\n
        stream.match(rx_TAIL);\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (phase(state) == rx_substitution_ref ||\n
               stream.match(rx_substitution_ref, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_normal, context(rx_substitution_ref, 1));\n
        stream.match(rx_substitution_text);\n
        token = \'variable-2\';\n
        break;\n
      case 1:\n
        change(state, to_normal, context(rx_substitution_ref, 2));\n
        if (stream.match(/^_?_?/)) token = \'link\';\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (stream.match(rx_footnote_ref)) {\n
      change(state, to_normal);\n
      token = \'quote\';\n
    } else if (stream.match(rx_citation_ref)) {\n
      change(state, to_normal);\n
      token = \'quote\';\n
    } else if (stream.match(rx_link_ref1)) {\n
      change(state, to_normal);\n
      if (!stream.peek() || stream.peek().match(/^\\W$/)) {\n
        token = \'link\';\n
      }\n
    } else if (phase(state) == rx_link_ref2 ||\n
               stream.match(rx_link_ref2, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        if (!stream.peek() || stream.peek().match(/^\\W$/)) {\n
          change(state, to_normal, context(rx_link_ref2, 1));\n
        } else {\n
          stream.match(rx_link_ref2);\n
        }\n
        break;\n
      case 1:\n
        change(state, to_normal, context(rx_link_ref2, 2));\n
        stream.match(/^`/);\n
        token = \'link\';\n
        break;\n
      case 2:\n
        change(state, to_normal, context(rx_link_ref2, 3));\n
        stream.match(rx_TEXT2);\n
        break;\n
      case 3:\n
        change(state, to_normal, context(rx_link_ref2, 4));\n
        stream.match(/^`_/);\n
        token = \'link\';\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (stream.match(rx_verbatim)) {\n
      change(state, to_verbatim);\n
    }\n
\n
    else {\n
      if (stream.next()) change(state, to_normal);\n
    }\n
\n
    return token;\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function to_explicit(stream, state) {\n
    var token = null;\n
\n
    if (phase(state) == rx_substitution ||\n
        stream.match(rx_substitution, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_explicit, context(rx_substitution, 1));\n
        stream.match(rx_substitution_text);\n
        token = \'variable-2\';\n
        break;\n
      case 1:\n
        change(state, to_explicit, context(rx_substitution, 2));\n
        stream.match(rx_substitution_sepa);\n
        break;\n
      case 2:\n
        change(state, to_explicit, context(rx_substitution, 3));\n
        stream.match(rx_substitution_name);\n
        token = \'keyword\';\n
        break;\n
      case 3:\n
        change(state, to_explicit, context(rx_substitution, 4));\n
        stream.match(rx_substitution_tail);\n
        token = \'meta\';\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (phase(state) == rx_directive ||\n
               stream.match(rx_directive, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_explicit, context(rx_directive, 1));\n
        stream.match(rx_directive_name);\n
        token = \'keyword\';\n
\n
        if (stream.current().match(/^(?:math|latex)/))\n
          state.tmp_stex = true;\n
        else if (stream.current().match(/^python/))\n
          state.tmp_py = true;\n
        break;\n
      case 1:\n
        change(state, to_explicit, context(rx_directive, 2));\n
        stream.match(rx_directive_tail);\n
        token = \'meta\';\n
\n
        if (stream.match(/^latex\\s*$/) || state.tmp_stex) {\n
          state.tmp_stex = undefined; change(state, to_mode, {\n
            mode: mode_stex, local: CodeMirror.startState(mode_stex)\n
          });\n
        }\n
        break;\n
      case 2:\n
        change(state, to_explicit, context(rx_directive, 3));\n
        if (stream.match(/^python\\s*$/) || state.tmp_py) {\n
          state.tmp_py = undefined; change(state, to_mode, {\n
            mode: mode_python, local: CodeMirror.startState(mode_python)\n
          });\n
        }\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (phase(state) == rx_link || stream.match(rx_link, false)) {\n
\n
      switch (stage(state)) {\n
      case 0:\n
        change(state, to_explicit, context(rx_link, 1));\n
        stream.match(rx_link_head);\n
        stream.match(rx_link_name);\n
        token = \'link\';\n
        break;\n
      case 1:\n
        change(state, to_explicit, context(rx_link, 2));\n
        stream.match(rx_link_tail);\n
        token = \'meta\';\n
        break;\n
      default:\n
        change(state, to_normal);\n
      }\n
    } else if (stream.match(rx_footnote)) {\n
      change(state, to_normal);\n
      token = \'quote\';\n
    } else if (stream.match(rx_citation)) {\n
      change(state, to_normal);\n
      token = \'quote\';\n
    }\n
\n
    else {\n
      stream.eatSpace();\n
      if (stream.eol()) {\n
        change(state, to_normal);\n
      } else {\n
        stream.skipToEnd();\n
        change(state, to_comment);\n
        token = \'comment\';\n
      }\n
    }\n
\n
    return token;\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function to_comment(stream, state) {\n
    return as_block(stream, state, \'comment\');\n
  }\n
\n
  function to_verbatim(stream, state) {\n
    return as_block(stream, state, \'meta\');\n
  }\n
\n
  function as_block(stream, state, token) {\n
    if (stream.eol() || stream.eatSpace()) {\n
      stream.skipToEnd();\n
      return token;\n
    } else {\n
      change(state, to_normal);\n
      return null;\n
    }\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function to_mode(stream, state) {\n
\n
    if (state.ctx.mode && state.ctx.local) {\n
\n
      if (stream.sol()) {\n
        if (!stream.eatSpace()) change(state, to_normal);\n
        return null;\n
      }\n
\n
      return state.ctx.mode.token(stream, state.ctx.local);\n
    }\n
\n
    change(state, to_normal);\n
    return null;\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  function context(phase, stage, mode, local) {\n
    return {phase: phase, stage: stage, mode: mode, local: local};\n
  }\n
\n
  function change(state, tok, ctx) {\n
    state.tok = tok;\n
    state.ctx = ctx || {};\n
  }\n
\n
  function stage(state) {\n
    return state.ctx.stage || 0;\n
  }\n
\n
  function phase(state) {\n
    return state.ctx.phase;\n
  }\n
\n
  ///////////////////////////////////////////////////////////////////////////\n
  ///////////////////////////////////////////////////////////////////////////\n
\n
  return {\n
    startState: function () {\n
      return {tok: to_normal, ctx: context(undefined, 0)};\n
    },\n
\n
    copyState: function (state) {\n
      var ctx = state.ctx, tmp = state.tmp;\n
      if (ctx.local)\n
        ctx = {mode: ctx.mode, local: CodeMirror.copyState(ctx.mode, ctx.local)};\n
      if (tmp)\n
        tmp = {mode: tmp.mode, local: CodeMirror.copyState(tmp.mode, tmp.local)};\n
      return {tok: state.tok, ctx: ctx, tmp: tmp};\n
    },\n
\n
    innerMode: function (state) {\n
      return state.tmp      ? {state: state.tmp.local, mode: state.tmp.mode}\n
      : state.ctx.mode ? {state: state.ctx.local, mode: state.ctx.mode}\n
      : null;\n
    },\n
\n
    token: function (stream, state) {\n
      return state.tok(stream, state);\n
    }\n
  };\n
}, \'python\', \'stex\');\n
\n
///////////////////////////////////////////////////////////////////////////////\n
///////////////////////////////////////////////////////////////////////////////\n
\n
CodeMirror.defineMIME(\'text/x-rst\', \'rst\');\n
\n
///////////////////////////////////////////////////////////////////////////////\n
///////////////////////////////////////////////////////////////////////////////\n
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
            <value> <int>17547</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
