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
            <value> <string>ts21897146.96</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ntriples.js</string> </value>
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
/**********************************************************\n
* This script provides syntax highlighting support for\n
* the Ntriples format.\n
* Ntriples format specification:\n
*     http://www.w3.org/TR/rdf-testcases/#ntriples\n
***********************************************************/\n
\n
/*\n
    The following expression defines the defined ASF grammar transitions.\n
\n
    pre_subject ->\n
        {\n
        ( writing_subject_uri | writing_bnode_uri )\n
            -> pre_predicate\n
                -> writing_predicate_uri\n
                    -> pre_object\n
                        -> writing_object_uri | writing_object_bnode |\n
                          (\n
                            writing_object_literal\n
                                -> writing_literal_lang | writing_literal_type\n
                          )\n
                            -> post_object\n
                                -> BEGIN\n
         } otherwise {\n
             -> ERROR\n
         }\n
*/\n
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
CodeMirror.defineMode("ntriples", function() {\n
\n
  var Location = {\n
    PRE_SUBJECT         : 0,\n
    WRITING_SUB_URI     : 1,\n
    WRITING_BNODE_URI   : 2,\n
    PRE_PRED            : 3,\n
    WRITING_PRED_URI    : 4,\n
    PRE_OBJ             : 5,\n
    WRITING_OBJ_URI     : 6,\n
    WRITING_OBJ_BNODE   : 7,\n
    WRITING_OBJ_LITERAL : 8,\n
    WRITING_LIT_LANG    : 9,\n
    WRITING_LIT_TYPE    : 10,\n
    POST_OBJ            : 11,\n
    ERROR               : 12\n
  };\n
  function transitState(currState, c) {\n
    var currLocation = currState.location;\n
    var ret;\n
\n
    // Opening.\n
    if     (currLocation == Location.PRE_SUBJECT && c == \'<\') ret = Location.WRITING_SUB_URI;\n
    else if(currLocation == Location.PRE_SUBJECT && c == \'_\') ret = Location.WRITING_BNODE_URI;\n
    else if(currLocation == Location.PRE_PRED    && c == \'<\') ret = Location.WRITING_PRED_URI;\n
    else if(currLocation == Location.PRE_OBJ     && c == \'<\') ret = Location.WRITING_OBJ_URI;\n
    else if(currLocation == Location.PRE_OBJ     && c == \'_\') ret = Location.WRITING_OBJ_BNODE;\n
    else if(currLocation == Location.PRE_OBJ     && c == \'"\') ret = Location.WRITING_OBJ_LITERAL;\n
\n
    // Closing.\n
    else if(currLocation == Location.WRITING_SUB_URI     && c == \'>\') ret = Location.PRE_PRED;\n
    else if(currLocation == Location.WRITING_BNODE_URI   && c == \' \') ret = Location.PRE_PRED;\n
    else if(currLocation == Location.WRITING_PRED_URI    && c == \'>\') ret = Location.PRE_OBJ;\n
    else if(currLocation == Location.WRITING_OBJ_URI     && c == \'>\') ret = Location.POST_OBJ;\n
    else if(currLocation == Location.WRITING_OBJ_BNODE   && c == \' \') ret = Location.POST_OBJ;\n
    else if(currLocation == Location.WRITING_OBJ_LITERAL && c == \'"\') ret = Location.POST_OBJ;\n
    else if(currLocation == Location.WRITING_LIT_LANG && c == \' \') ret = Location.POST_OBJ;\n
    else if(currLocation == Location.WRITING_LIT_TYPE && c == \'>\') ret = Location.POST_OBJ;\n
\n
    // Closing typed and language literal.\n
    else if(currLocation == Location.WRITING_OBJ_LITERAL && c == \'@\') ret = Location.WRITING_LIT_LANG;\n
    else if(currLocation == Location.WRITING_OBJ_LITERAL && c == \'^\') ret = Location.WRITING_LIT_TYPE;\n
\n
    // Spaces.\n
    else if( c == \' \' &&\n
             (\n
               currLocation == Location.PRE_SUBJECT ||\n
               currLocation == Location.PRE_PRED    ||\n
               currLocation == Location.PRE_OBJ     ||\n
               currLocation == Location.POST_OBJ\n
             )\n
           ) ret = currLocation;\n
\n
    // Reset.\n
    else if(currLocation == Location.POST_OBJ && c == \'.\') ret = Location.PRE_SUBJECT;\n
\n
    // Error\n
    else ret = Location.ERROR;\n
\n
    currState.location=ret;\n
  }\n
\n
  return {\n
    startState: function() {\n
       return {\n
           location : Location.PRE_SUBJECT,\n
           uris     : [],\n
           anchors  : [],\n
           bnodes   : [],\n
           langs    : [],\n
           types    : []\n
       };\n
    },\n
    token: function(stream, state) {\n
      var ch = stream.next();\n
      if(ch == \'<\') {\n
         transitState(state, ch);\n
         var parsedURI = \'\';\n
         stream.eatWhile( function(c) { if( c != \'#\' && c != \'>\' ) { parsedURI += c; return true; } return false;} );\n
         state.uris.push(parsedURI);\n
         if( stream.match(\'#\', false) ) return \'variable\';\n
         stream.next();\n
         transitState(state, \'>\');\n
         return \'variable\';\n
      }\n
      if(ch == \'#\') {\n
        var parsedAnchor = \'\';\n
        stream.eatWhile(function(c) { if(c != \'>\' && c != \' \') { parsedAnchor+= c; return true; } return false;});\n
        state.anchors.push(parsedAnchor);\n
        return \'variable-2\';\n
      }\n
      if(ch == \'>\') {\n
          transitState(state, \'>\');\n
          return \'variable\';\n
      }\n
      if(ch == \'_\') {\n
          transitState(state, ch);\n
          var parsedBNode = \'\';\n
          stream.eatWhile(function(c) { if( c != \' \' ) { parsedBNode += c; return true; } return false;});\n
          state.bnodes.push(parsedBNode);\n
          stream.next();\n
          transitState(state, \' \');\n
          return \'builtin\';\n
      }\n
      if(ch == \'"\') {\n
          transitState(state, ch);\n
          stream.eatWhile( function(c) { return c != \'"\'; } );\n
          stream.next();\n
          if( stream.peek() != \'@\' && stream.peek() != \'^\' ) {\n
              transitState(state, \'"\');\n
          }\n
          return \'string\';\n
      }\n
      if( ch == \'@\' ) {\n
          transitState(state, \'@\');\n
          var parsedLang = \'\';\n
          stream.eatWhile(function(c) { if( c != \' \' ) { parsedLang += c; return true; } return false;});\n
          state.langs.push(parsedLang);\n
          stream.next();\n
          transitState(state, \' \');\n
          return \'string-2\';\n
      }\n
      if( ch == \'^\' ) {\n
          stream.next();\n
          transitState(state, \'^\');\n
          var parsedType = \'\';\n
          stream.eatWhile(function(c) { if( c != \'>\' ) { parsedType += c; return true; } return false;} );\n
          state.types.push(parsedType);\n
          stream.next();\n
          transitState(state, \'>\');\n
          return \'variable\';\n
      }\n
      if( ch == \' \' ) {\n
          transitState(state, ch);\n
      }\n
      if( ch == \'.\' ) {\n
          transitState(state, ch);\n
      }\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/n-triples", "ntriples");\n
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
            <value> <int>6643</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
