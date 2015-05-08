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
            <value> <string>ts21897119.08</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>javascript-hint.js</string> </value>
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
  var Pos = CodeMirror.Pos;\n
\n
  function forEach(arr, f) {\n
    for (var i = 0, e = arr.length; i < e; ++i) f(arr[i]);\n
  }\n
\n
  function arrayContains(arr, item) {\n
    if (!Array.prototype.indexOf) {\n
      var i = arr.length;\n
      while (i--) {\n
        if (arr[i] === item) {\n
          return true;\n
        }\n
      }\n
      return false;\n
    }\n
    return arr.indexOf(item) != -1;\n
  }\n
\n
  function scriptHint(editor, keywords, getToken, options) {\n
    // Find the token at the cursor\n
    var cur = editor.getCursor(), token = getToken(editor, cur);\n
    if (/\\b(?:string|comment)\\b/.test(token.type)) return;\n
    token.state = CodeMirror.innerMode(editor.getMode(), token.state).state;\n
\n
    // If it\'s not a \'word-style\' token, ignore the token.\n
    if (!/^[\\w$_]*$/.test(token.string)) {\n
      token = {start: cur.ch, end: cur.ch, string: "", state: token.state,\n
               type: token.string == "." ? "property" : null};\n
    } else if (token.end > cur.ch) {\n
      token.end = cur.ch;\n
      token.string = token.string.slice(0, cur.ch - token.start);\n
    }\n
\n
    var tprop = token;\n
    // If it is a property, find out what it is a property of.\n
    while (tprop.type == "property") {\n
      tprop = getToken(editor, Pos(cur.line, tprop.start));\n
      if (tprop.string != ".") return;\n
      tprop = getToken(editor, Pos(cur.line, tprop.start));\n
      if (!context) var context = [];\n
      context.push(tprop);\n
    }\n
    return {list: getCompletions(token, context, keywords, options),\n
            from: Pos(cur.line, token.start),\n
            to: Pos(cur.line, token.end)};\n
  }\n
\n
  function javascriptHint(editor, options) {\n
    return scriptHint(editor, javascriptKeywords,\n
                      function (e, cur) {return e.getTokenAt(cur);},\n
                      options);\n
  };\n
  CodeMirror.registerHelper("hint", "javascript", javascriptHint);\n
\n
  function getCoffeeScriptToken(editor, cur) {\n
  // This getToken, it is for coffeescript, imitates the behavior of\n
  // getTokenAt method in javascript.js, that is, returning "property"\n
  // type and treat "." as indepenent token.\n
    var token = editor.getTokenAt(cur);\n
    if (cur.ch == token.start + 1 && token.string.charAt(0) == \'.\') {\n
      token.end = token.start;\n
      token.string = \'.\';\n
      token.type = "property";\n
    }\n
    else if (/^\\.[\\w$_]*$/.test(token.string)) {\n
      token.type = "property";\n
      token.start++;\n
      token.string = token.string.replace(/\\./, \'\');\n
    }\n
    return token;\n
  }\n
\n
  function coffeescriptHint(editor, options) {\n
    return scriptHint(editor, coffeescriptKeywords, getCoffeeScriptToken, options);\n
  }\n
  CodeMirror.registerHelper("hint", "coffeescript", coffeescriptHint);\n
\n
  var stringProps = ("charAt charCodeAt indexOf lastIndexOf substring substr slice trim trimLeft trimRight " +\n
                     "toUpperCase toLowerCase split concat match replace search").split(" ");\n
  var arrayProps = ("length concat join splice push pop shift unshift slice reverse sort indexOf " +\n
                    "lastIndexOf every some filter forEach map reduce reduceRight ").split(" ");\n
  var funcProps = "prototype apply call bind".split(" ");\n
  var javascriptKeywords = ("break case catch continue debugger default delete do else false finally for function " +\n
                  "if in instanceof new null return switch throw true try typeof var void while with").split(" ");\n
  var coffeescriptKeywords = ("and break catch class continue delete do else extends false finally for " +\n
                  "if in instanceof isnt new no not null of off on or return switch then throw true try typeof until void while with yes").split(" ");\n
\n
  function getCompletions(token, context, keywords, options) {\n
    var found = [], start = token.string, global = options && options.globalScope || window;\n
    function maybeAdd(str) {\n
      if (str.lastIndexOf(start, 0) == 0 && !arrayContains(found, str)) found.push(str);\n
    }\n
    function gatherCompletions(obj) {\n
      if (typeof obj == "string") forEach(stringProps, maybeAdd);\n
      else if (obj instanceof Array) forEach(arrayProps, maybeAdd);\n
      else if (obj instanceof Function) forEach(funcProps, maybeAdd);\n
      for (var name in obj) maybeAdd(name);\n
    }\n
\n
    if (context && context.length) {\n
      // If this is a property, see if it belongs to some object we can\n
      // find in the current environment.\n
      var obj = context.pop(), base;\n
      if (obj.type && obj.type.indexOf("variable") === 0) {\n
        if (options && options.additionalContext)\n
          base = options.additionalContext[obj.string];\n
        if (!options || options.useGlobalScope !== false)\n
          base = base || global[obj.string];\n
      } else if (obj.type == "string") {\n
        base = "";\n
      } else if (obj.type == "atom") {\n
        base = 1;\n
      } else if (obj.type == "function") {\n
        if (global.jQuery != null && (obj.string == \'$\' || obj.string == \'jQuery\') &&\n
            (typeof global.jQuery == \'function\'))\n
          base = global.jQuery();\n
        else if (global._ != null && (obj.string == \'_\') && (typeof global._ == \'function\'))\n
          base = global._();\n
      }\n
      while (base != null && context.length)\n
        base = base[context.pop().string];\n
      if (base != null) gatherCompletions(base);\n
    } else {\n
      // If not, just look in the global object and any local scope\n
      // (reading into JS mode internals to get at the local and global variables)\n
      for (var v = token.state.localVars; v; v = v.next) maybeAdd(v.name);\n
      for (var v = token.state.globalVars; v; v = v.next) maybeAdd(v.name);\n
      if (!options || options.useGlobalScope !== false)\n
        gatherCompletions(global);\n
      forEach(keywords, maybeAdd);\n
    }\n
    return found;\n
  }\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6163</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
