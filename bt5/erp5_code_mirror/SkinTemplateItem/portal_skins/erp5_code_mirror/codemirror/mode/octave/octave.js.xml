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
            <value> <string>ts21897134.53</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>octave.js</string> </value>
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
CodeMirror.defineMode("octave", function() {\n
  function wordRegexp(words) {\n
    return new RegExp("^((" + words.join(")|(") + "))\\\\b");\n
  }\n
\n
  var singleOperators = new RegExp("^[\\\\+\\\\-\\\\*/&|\\\\^~<>!@\'\\\\\\\\]");\n
  var singleDelimiters = new RegExp(\'^[\\\\(\\\\[\\\\{\\\\},:=;]\');\n
  var doubleOperators = new RegExp("^((==)|(~=)|(<=)|(>=)|(<<)|(>>)|(\\\\.[\\\\+\\\\-\\\\*/\\\\^\\\\\\\\]))");\n
  var doubleDelimiters = new RegExp("^((!=)|(\\\\+=)|(\\\\-=)|(\\\\*=)|(/=)|(&=)|(\\\\|=)|(\\\\^=))");\n
  var tripleDelimiters = new RegExp("^((>>=)|(<<=))");\n
  var expressionEnd = new RegExp("^[\\\\]\\\\)]");\n
  var identifiers = new RegExp("^[_A-Za-z\\xa1-\\uffff][_A-Za-z0-9\\xa1-\\uffff]*");\n
\n
  var builtins = wordRegexp([\n
    \'error\', \'eval\', \'function\', \'abs\', \'acos\', \'atan\', \'asin\', \'cos\',\n
    \'cosh\', \'exp\', \'log\', \'prod\', \'sum\', \'log10\', \'max\', \'min\', \'sign\', \'sin\', \'sinh\',\n
    \'sqrt\', \'tan\', \'reshape\', \'break\', \'zeros\', \'default\', \'margin\', \'round\', \'ones\',\n
    \'rand\', \'syn\', \'ceil\', \'floor\', \'size\', \'clear\', \'zeros\', \'eye\', \'mean\', \'std\', \'cov\',\n
    \'det\', \'eig\', \'inv\', \'norm\', \'rank\', \'trace\', \'expm\', \'logm\', \'sqrtm\', \'linspace\', \'plot\',\n
    \'title\', \'xlabel\', \'ylabel\', \'legend\', \'text\', \'grid\', \'meshgrid\', \'mesh\', \'num2str\',\n
    \'fft\', \'ifft\', \'arrayfun\', \'cellfun\', \'input\', \'fliplr\', \'flipud\', \'ismember\'\n
  ]);\n
\n
  var keywords = wordRegexp([\n
    \'return\', \'case\', \'switch\', \'else\', \'elseif\', \'end\', \'endif\', \'endfunction\',\n
    \'if\', \'otherwise\', \'do\', \'for\', \'while\', \'try\', \'catch\', \'classdef\', \'properties\', \'events\',\n
    \'methods\', \'global\', \'persistent\', \'endfor\', \'endwhile\', \'printf\', \'sprintf\', \'disp\', \'until\',\n
    \'continue\', \'pkg\'\n
  ]);\n
\n
\n
  // tokenizers\n
  function tokenTranspose(stream, state) {\n
    if (!stream.sol() && stream.peek() === \'\\\'\') {\n
      stream.next();\n
      state.tokenize = tokenBase;\n
      return \'operator\';\n
    }\n
    state.tokenize = tokenBase;\n
    return tokenBase(stream, state);\n
  }\n
\n
\n
  function tokenComment(stream, state) {\n
    if (stream.match(/^.*%}/)) {\n
      state.tokenize = tokenBase;\n
      return \'comment\';\n
    };\n
    stream.skipToEnd();\n
    return \'comment\';\n
  }\n
\n
  function tokenBase(stream, state) {\n
    // whitespaces\n
    if (stream.eatSpace()) return null;\n
\n
    // Handle one line Comments\n
    if (stream.match(\'%{\')){\n
      state.tokenize = tokenComment;\n
      stream.skipToEnd();\n
      return \'comment\';\n
    }\n
\n
    if (stream.match(/^[%#]/)){\n
      stream.skipToEnd();\n
      return \'comment\';\n
    }\n
\n
    // Handle Number Literals\n
    if (stream.match(/^[0-9\\.+-]/, false)) {\n
      if (stream.match(/^[+-]?0x[0-9a-fA-F]+[ij]?/)) {\n
        stream.tokenize = tokenBase;\n
        return \'number\'; };\n
      if (stream.match(/^[+-]?\\d*\\.\\d+([EeDd][+-]?\\d+)?[ij]?/)) { return \'number\'; };\n
      if (stream.match(/^[+-]?\\d+([EeDd][+-]?\\d+)?[ij]?/)) { return \'number\'; };\n
    }\n
    if (stream.match(wordRegexp([\'nan\',\'NaN\',\'inf\',\'Inf\']))) { return \'number\'; };\n
\n
    // Handle Strings\n
    if (stream.match(/^"([^"]|(""))*"/)) { return \'string\'; } ;\n
    if (stream.match(/^\'([^\']|(\'\'))*\'/)) { return \'string\'; } ;\n
\n
    // Handle words\n
    if (stream.match(keywords)) { return \'keyword\'; } ;\n
    if (stream.match(builtins)) { return \'builtin\'; } ;\n
    if (stream.match(identifiers)) { return \'variable\'; } ;\n
\n
    if (stream.match(singleOperators) || stream.match(doubleOperators)) { return \'operator\'; };\n
    if (stream.match(singleDelimiters) || stream.match(doubleDelimiters) || stream.match(tripleDelimiters)) { return null; };\n
\n
    if (stream.match(expressionEnd)) {\n
      state.tokenize = tokenTranspose;\n
      return null;\n
    };\n
\n
\n
    // Handle non-detected items\n
    stream.next();\n
    return \'error\';\n
  };\n
\n
\n
  return {\n
    startState: function() {\n
      return {\n
        tokenize: tokenBase\n
      };\n
    },\n
\n
    token: function(stream, state) {\n
      var style = state.tokenize(stream, state);\n
      if (style === \'number\' || style === \'variable\'){\n
        state.tokenize = tokenTranspose;\n
      }\n
      return style;\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-octave", "octave");\n
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
            <value> <int>4463</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
