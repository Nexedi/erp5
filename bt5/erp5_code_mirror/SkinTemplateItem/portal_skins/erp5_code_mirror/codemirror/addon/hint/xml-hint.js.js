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
            <value> <string>ts21897118.97</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>xml-hint.js</string> </value>
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
  var Pos = CodeMirror.Pos;\n
\n
  function getHints(cm, options) {\n
    var tags = options && options.schemaInfo;\n
    var quote = (options && options.quoteChar) || \'"\';\n
    if (!tags) return;\n
    var cur = cm.getCursor(), token = cm.getTokenAt(cur);\n
    if (token.end > cur.ch) {\n
      token.end = cur.ch;\n
      token.string = token.string.slice(0, cur.ch - token.start);\n
    }\n
    var inner = CodeMirror.innerMode(cm.getMode(), token.state);\n
    if (inner.mode.name != "xml") return;\n
    var result = [], replaceToken = false, prefix;\n
    var tag = /\\btag\\b/.test(token.type) && !/>$/.test(token.string);\n
    var tagName = tag && /^\\w/.test(token.string), tagStart;\n
\n
    if (tagName) {\n
      var before = cm.getLine(cur.line).slice(Math.max(0, token.start - 2), token.start);\n
      var tagType = /<\\/$/.test(before) ? "close" : /<$/.test(before) ? "open" : null;\n
      if (tagType) tagStart = token.start - (tagType == "close" ? 2 : 1);\n
    } else if (tag && token.string == "<") {\n
      tagType = "open";\n
    } else if (tag && token.string == "</") {\n
      tagType = "close";\n
    }\n
\n
    if (!tag && !inner.state.tagName || tagType) {\n
      if (tagName)\n
        prefix = token.string;\n
      replaceToken = tagType;\n
      var cx = inner.state.context, curTag = cx && tags[cx.tagName];\n
      var childList = cx ? curTag && curTag.children : tags["!top"];\n
      if (childList && tagType != "close") {\n
        for (var i = 0; i < childList.length; ++i) if (!prefix || childList[i].lastIndexOf(prefix, 0) == 0)\n
          result.push("<" + childList[i]);\n
      } else if (tagType != "close") {\n
        for (var name in tags)\n
          if (tags.hasOwnProperty(name) && name != "!top" && name != "!attrs" && (!prefix || name.lastIndexOf(prefix, 0) == 0))\n
            result.push("<" + name);\n
      }\n
      if (cx && (!prefix || tagType == "close" && cx.tagName.lastIndexOf(prefix, 0) == 0))\n
        result.push("</" + cx.tagName + ">");\n
    } else {\n
      // Attribute completion\n
      var curTag = tags[inner.state.tagName], attrs = curTag && curTag.attrs;\n
      var globalAttrs = tags["!attrs"];\n
      if (!attrs && !globalAttrs) return;\n
      if (!attrs) {\n
        attrs = globalAttrs;\n
      } else if (globalAttrs) { // Combine tag-local and global attributes\n
        var set = {};\n
        for (var nm in globalAttrs) if (globalAttrs.hasOwnProperty(nm)) set[nm] = globalAttrs[nm];\n
        for (var nm in attrs) if (attrs.hasOwnProperty(nm)) set[nm] = attrs[nm];\n
        attrs = set;\n
      }\n
      if (token.type == "string" || token.string == "=") { // A value\n
        var before = cm.getRange(Pos(cur.line, Math.max(0, cur.ch - 60)),\n
                                 Pos(cur.line, token.type == "string" ? token.start : token.end));\n
        var atName = before.match(/([^\\s\\u00a0=<>\\"\\\']+)=$/), atValues;\n
        if (!atName || !attrs.hasOwnProperty(atName[1]) || !(atValues = attrs[atName[1]])) return;\n
        if (typeof atValues == \'function\') atValues = atValues.call(this, cm); // Functions can be used to supply values for autocomplete widget\n
        if (token.type == "string") {\n
          prefix = token.string;\n
          var n = 0;\n
          if (/[\'"]/.test(token.string.charAt(0))) {\n
            quote = token.string.charAt(0);\n
            prefix = token.string.slice(1);\n
            n++;\n
          }\n
          var len = token.string.length;\n
          if (/[\'"]/.test(token.string.charAt(len - 1))) {\n
            quote = token.string.charAt(len - 1);\n
            prefix = token.string.substr(n, len - 2);\n
          }\n
          replaceToken = true;\n
        }\n
        for (var i = 0; i < atValues.length; ++i) if (!prefix || atValues[i].lastIndexOf(prefix, 0) == 0)\n
          result.push(quote + atValues[i] + quote);\n
      } else { // An attribute name\n
        if (token.type == "attribute") {\n
          prefix = token.string;\n
          replaceToken = true;\n
        }\n
        for (var attr in attrs) if (attrs.hasOwnProperty(attr) && (!prefix || attr.lastIndexOf(prefix, 0) == 0))\n
          result.push(attr);\n
      }\n
    }\n
    return {\n
      list: result,\n
      from: replaceToken ? Pos(cur.line, tagStart == null ? token.start : tagStart) : cur,\n
      to: replaceToken ? Pos(cur.line, token.end) : cur\n
    };\n
  }\n
\n
  CodeMirror.registerHelper("hint", "xml", getHints);\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4735</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
