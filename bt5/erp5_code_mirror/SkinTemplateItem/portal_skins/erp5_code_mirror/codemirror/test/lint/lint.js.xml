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
            <value> <string>ts21897151.95</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lint.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 Simple linter, based on the Acorn [1] parser module\n
\n
 All of the existing linters either cramp my style or have huge\n
 dependencies (Closure). So here\'s a very simple, non-invasive one\n
 that only spots\n
\n
  - missing semicolons and trailing commas\n
  - variables or properties that are reserved words\n
  - assigning to a variable you didn\'t declare\n
  - access to non-whitelisted globals\n
    (use a \'// declare global: foo, bar\' comment to declare extra\n
    globals in a file)\n
\n
 [1]: https://github.com/marijnh/acorn/\n
*/\n
\n
var topAllowedGlobals = Object.create(null);\n
("Error RegExp Number String Array Function Object Math Date undefined " +\n
 "parseInt parseFloat Infinity NaN isNaN " +\n
 "window document navigator prompt alert confirm console " +\n
 "screen FileReader Worker postMessage importScripts " +\n
 "setInterval clearInterval setTimeout clearTimeout " +\n
 "CodeMirror " +\n
 "test exports require module define requirejs")\n
  .split(" ").forEach(function(n) { topAllowedGlobals[n] = true; });\n
\n
var fs = require("fs"), acorn = require("./acorn.js"), walk = require("./walk.js");\n
\n
var scopePasser = walk.make({\n
  ScopeBody: function(node, prev, c) { c(node, node.scope); }\n
});\n
\n
var cBlob = /^\\/\\/ CodeMirror, copyright \\(c\\) by Marijn Haverbeke and others\\n\\/\\/ Distributed under an MIT license: http:\\/\\/codemirror.net\\/LICENSE\\n\\n/;\n
\n
function checkFile(fileName) {\n
  var file = fs.readFileSync(fileName, "utf8"), notAllowed;\n
  if (notAllowed = file.match(/[\\x00-\\x08\\x0b\\x0c\\x0e-\\x19\\uFEFF\\t]|[ \\t]\\n/)) {\n
    var msg;\n
    if (notAllowed[0] == "\\t") msg = "Found tab character";\n
    else if (notAllowed[0].indexOf("\\n") > -1) msg = "Trailing whitespace";\n
    else msg = "Undesirable character " + notAllowed[0].charCodeAt(0);\n
    var info = acorn.getLineInfo(file, notAllowed.index);\n
    fail(msg + " at line " + info.line + ", column " + info.column, {source: fileName});\n
  }\n
\n
  if (!cBlob.test(file))\n
    fail("Missing license blob", {source: fileName});\n
  \n
  var globalsSeen = Object.create(null);\n
\n
  try {\n
    var parsed = acorn.parse(file, {\n
      locations: true,\n
      ecmaVersion: 3,\n
      strictSemicolons: true,\n
      allowTrailingCommas: false,\n
      forbidReserved: "everywhere",\n
      sourceFile: fileName\n
    });\n
  } catch (e) {\n
    fail(e.message, {source: fileName});\n
    return;\n
  }\n
\n
  var scopes = [];\n
\n
  walk.simple(parsed, {\n
    ScopeBody: function(node, scope) {\n
      node.scope = scope;\n
      scopes.push(scope);\n
    }\n
  }, walk.scopeVisitor, {vars: Object.create(null)});\n
\n
  var ignoredGlobals = Object.create(null);\n
\n
  function inScope(name, scope) {\n
    for (var cur = scope; cur; cur = cur.prev)\n
      if (name in cur.vars) return true;\n
  }\n
  function checkLHS(node, scope) {\n
    if (node.type == "Identifier" && !(node.name in ignoredGlobals) &&\n
        !inScope(node.name, scope)) {\n
      ignoredGlobals[node.name] = true;\n
      fail("Assignment to global variable", node.loc);\n
    }\n
  }\n
\n
  walk.simple(parsed, {\n
    UpdateExpression: function(node, scope) {checkLHS(node.argument, scope);},\n
    AssignmentExpression: function(node, scope) {checkLHS(node.left, scope);},\n
    Identifier: function(node, scope) {\n
      if (node.name == "arguments") return;\n
      // Mark used identifiers\n
      for (var cur = scope; cur; cur = cur.prev)\n
        if (node.name in cur.vars) {\n
          cur.vars[node.name].used = true;\n
          return;\n
        }\n
      globalsSeen[node.name] = node.loc;\n
    },\n
    FunctionExpression: function(node) {\n
      if (node.id) fail("Named function expression", node.loc);\n
    },\n
    ForStatement: function(node) {\n
      checkReusedIndex(node);\n
    },\n
    MemberExpression: function(node) {\n
      if (node.object.type == "Identifier" && node.object.name == "console" && !node.computed)\n
        fail("Found console." + node.property.name, node.loc);\n
    },\n
    DebuggerStatement: function(node) {\n
      fail("Found debugger statement", node.loc);\n
    }\n
  }, scopePasser);\n
\n
  function checkReusedIndex(node) {\n
    if (!node.init || node.init.type != "VariableDeclaration") return;\n
    var name = node.init.declarations[0].id.name;\n
    walk.recursive(node.body, null, {\n
      Function: function() {},\n
      VariableDeclaration: function(node, st, c) {\n
        for (var i = 0; i < node.declarations.length; i++)\n
          if (node.declarations[i].id.name == name)\n
            fail("redefined loop variable", node.declarations[i].id.loc);\n
        walk.base.VariableDeclaration(node, st, c);\n
      }\n
    });\n
  }\n
\n
  var allowedGlobals = Object.create(topAllowedGlobals), m;\n
  if (m = file.match(/\\/\\/ declare global:\\s+(.*)/))\n
    m[1].split(/,\\s*/g).forEach(function(n) { allowedGlobals[n] = true; });\n
  for (var glob in globalsSeen)\n
    if (!(glob in allowedGlobals))\n
      fail("Access to global variable " + glob + ". Add a \'// declare global: " + glob +\n
           "\' comment or add this variable in test/lint/lint.js.", globalsSeen[glob]);\n
\n
  for (var i = 0; i < scopes.length; ++i) {\n
    var scope = scopes[i];\n
    for (var name in scope.vars) {\n
      var info = scope.vars[name];\n
      if (!info.used && info.type != "catch clause" && info.type != "function name" && name.charAt(0) != "_")\n
        fail("Unused " + info.type + " " + name, info.node.loc);\n
    }\n
  }\n
}\n
\n
var failed = false;\n
function fail(msg, pos) {\n
  if (pos.start) msg += " (" + pos.start.line + ":" + pos.start.column + ")";\n
  console.log(pos.source + ": " + msg);\n
  failed = true;\n
}\n
\n
function checkDir(dir) {\n
  fs.readdirSync(dir).forEach(function(file) {\n
    var fname = dir + "/" + file;\n
    if (/\\.js$/.test(file)) checkFile(fname);\n
    else if (fs.lstatSync(fname).isDirectory()) checkDir(fname);\n
  });\n
}\n
\n
exports.checkDir = checkDir;\n
exports.checkFile = checkFile;\n
exports.success = function() { return !failed; };\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5742</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
