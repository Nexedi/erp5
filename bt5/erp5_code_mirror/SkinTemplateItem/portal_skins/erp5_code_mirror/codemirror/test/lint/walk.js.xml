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
            <value> <string>ts21897151.88</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>walk.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// AST walker module for Mozilla Parser API compatible trees\n
\n
(function(mod) {\n
  if (typeof exports == "object" && typeof module == "object") return mod(exports); // CommonJS\n
  if (typeof define == "function" && define.amd) return define(["exports"], mod); // AMD\n
  mod((this.acorn || (this.acorn = {})).walk = {}); // Plain browser env\n
})(function(exports) {\n
  "use strict";\n
\n
  // A simple walk is one where you simply specify callbacks to be\n
  // called on specific nodes. The last two arguments are optional. A\n
  // simple use would be\n
  //\n
  //     walk.simple(myTree, {\n
  //         Expression: function(node) { ... }\n
  //     });\n
  //\n
  // to do something with all expressions. All Parser API node types\n
  // can be used to identify node types, as well as Expression,\n
  // Statement, and ScopeBody, which denote categories of nodes.\n
  //\n
  // The base argument can be used to pass a custom (recursive)\n
  // walker, and state can be used to give this walked an initial\n
  // state.\n
  exports.simple = function(node, visitors, base, state) {\n
    if (!base) base = exports.base;\n
    function c(node, st, override) {\n
      var type = override || node.type, found = visitors[type];\n
      base[type](node, st, c);\n
      if (found) found(node, st);\n
    }\n
    c(node, state);\n
  };\n
\n
  // A recursive walk is one where your functions override the default\n
  // walkers. They can modify and replace the state parameter that\'s\n
  // threaded through the walk, and can opt how and whether to walk\n
  // their child nodes (by calling their third argument on these\n
  // nodes).\n
  exports.recursive = function(node, state, funcs, base) {\n
    var visitor = funcs ? exports.make(funcs, base) : base;\n
    function c(node, st, override) {\n
      visitor[override || node.type](node, st, c);\n
    }\n
    c(node, state);\n
  };\n
\n
  function makeTest(test) {\n
    if (typeof test == "string")\n
      return function(type) { return type == test; };\n
    else if (!test)\n
      return function() { return true; };\n
    else\n
      return test;\n
  }\n
\n
  function Found(node, state) { this.node = node; this.state = state; }\n
\n
  // Find a node with a given start, end, and type (all are optional,\n
  // null can be used as wildcard). Returns a {node, state} object, or\n
  // undefined when it doesn\'t find a matching node.\n
  exports.findNodeAt = function(node, start, end, test, base, state) {\n
    test = makeTest(test);\n
    try {\n
      if (!base) base = exports.base;\n
      var c = function(node, st, override) {\n
        var type = override || node.type;\n
        if ((start == null || node.start <= start) &&\n
            (end == null || node.end >= end))\n
          base[type](node, st, c);\n
        if (test(type, node) &&\n
            (start == null || node.start == start) &&\n
            (end == null || node.end == end))\n
          throw new Found(node, st);\n
      };\n
      c(node, state);\n
    } catch (e) {\n
      if (e instanceof Found) return e;\n
      throw e;\n
    }\n
  };\n
\n
  // Find the innermost node of a given type that contains the given\n
  // position. Interface similar to findNodeAt.\n
  exports.findNodeAround = function(node, pos, test, base, state) {\n
    test = makeTest(test);\n
    try {\n
      if (!base) base = exports.base;\n
      var c = function(node, st, override) {\n
        var type = override || node.type;\n
        if (node.start > pos || node.end < pos) return;\n
        base[type](node, st, c);\n
        if (test(type, node)) throw new Found(node, st);\n
      };\n
      c(node, state);\n
    } catch (e) {\n
      if (e instanceof Found) return e;\n
      throw e;\n
    }\n
  };\n
\n
  // Find the outermost matching node after a given position.\n
  exports.findNodeAfter = function(node, pos, test, base, state) {\n
    test = makeTest(test);\n
    try {\n
      if (!base) base = exports.base;\n
      var c = function(node, st, override) {\n
        if (node.end < pos) return;\n
        var type = override || node.type;\n
        if (node.start >= pos && test(type, node)) throw new Found(node, st);\n
        base[type](node, st, c);\n
      };\n
      c(node, state);\n
    } catch (e) {\n
      if (e instanceof Found) return e;\n
      throw e;\n
    }\n
  };\n
\n
  // Find the outermost matching node before a given position.\n
  exports.findNodeBefore = function(node, pos, test, base, state) {\n
    test = makeTest(test);\n
    if (!base) base = exports.base;\n
    var max;\n
    var c = function(node, st, override) {\n
      if (node.start > pos) return;\n
      var type = override || node.type;\n
      if (node.end <= pos && (!max || max.node.end < node.end) && test(type, node))\n
        max = new Found(node, st);\n
      base[type](node, st, c);\n
    };\n
    c(node, state);\n
    return max;\n
  };\n
\n
  // Used to create a custom walker. Will fill in all missing node\n
  // type properties with the defaults.\n
  exports.make = function(funcs, base) {\n
    if (!base) base = exports.base;\n
    var visitor = {};\n
    for (var type in base) visitor[type] = base[type];\n
    for (var type in funcs) visitor[type] = funcs[type];\n
    return visitor;\n
  };\n
\n
  function skipThrough(node, st, c) { c(node, st); }\n
  function ignore(_node, _st, _c) {}\n
\n
  // Node walkers.\n
\n
  var base = exports.base = {};\n
  base.Program = base.BlockStatement = function(node, st, c) {\n
    for (var i = 0; i < node.body.length; ++i)\n
      c(node.body[i], st, "Statement");\n
  };\n
  base.Statement = skipThrough;\n
  base.EmptyStatement = ignore;\n
  base.ExpressionStatement = function(node, st, c) {\n
    c(node.expression, st, "Expression");\n
  };\n
  base.IfStatement = function(node, st, c) {\n
    c(node.test, st, "Expression");\n
    c(node.consequent, st, "Statement");\n
    if (node.alternate) c(node.alternate, st, "Statement");\n
  };\n
  base.LabeledStatement = function(node, st, c) {\n
    c(node.body, st, "Statement");\n
  };\n
  base.BreakStatement = base.ContinueStatement = ignore;\n
  base.WithStatement = function(node, st, c) {\n
    c(node.object, st, "Expression");\n
    c(node.body, st, "Statement");\n
  };\n
  base.SwitchStatement = function(node, st, c) {\n
    c(node.discriminant, st, "Expression");\n
    for (var i = 0; i < node.cases.length; ++i) {\n
      var cs = node.cases[i];\n
      if (cs.test) c(cs.test, st, "Expression");\n
      for (var j = 0; j < cs.consequent.length; ++j)\n
        c(cs.consequent[j], st, "Statement");\n
    }\n
  };\n
  base.ReturnStatement = function(node, st, c) {\n
    if (node.argument) c(node.argument, st, "Expression");\n
  };\n
  base.ThrowStatement = function(node, st, c) {\n
    c(node.argument, st, "Expression");\n
  };\n
  base.TryStatement = function(node, st, c) {\n
    c(node.block, st, "Statement");\n
    if (node.handler) c(node.handler.body, st, "ScopeBody");\n
    if (node.finalizer) c(node.finalizer, st, "Statement");\n
  };\n
  base.WhileStatement = function(node, st, c) {\n
    c(node.test, st, "Expression");\n
    c(node.body, st, "Statement");\n
  };\n
  base.DoWhileStatement = base.WhileStatement;\n
  base.ForStatement = function(node, st, c) {\n
    if (node.init) c(node.init, st, "ForInit");\n
    if (node.test) c(node.test, st, "Expression");\n
    if (node.update) c(node.update, st, "Expression");\n
    c(node.body, st, "Statement");\n
  };\n
  base.ForInStatement = function(node, st, c) {\n
    c(node.left, st, "ForInit");\n
    c(node.right, st, "Expression");\n
    c(node.body, st, "Statement");\n
  };\n
  base.ForInit = function(node, st, c) {\n
    if (node.type == "VariableDeclaration") c(node, st);\n
    else c(node, st, "Expression");\n
  };\n
  base.DebuggerStatement = ignore;\n
\n
  base.FunctionDeclaration = function(node, st, c) {\n
    c(node, st, "Function");\n
  };\n
  base.VariableDeclaration = function(node, st, c) {\n
    for (var i = 0; i < node.declarations.length; ++i) {\n
      var decl = node.declarations[i];\n
      if (decl.init) c(decl.init, st, "Expression");\n
    }\n
  };\n
\n
  base.Function = function(node, st, c) {\n
    c(node.body, st, "ScopeBody");\n
  };\n
  base.ScopeBody = function(node, st, c) {\n
    c(node, st, "Statement");\n
  };\n
\n
  base.Expression = skipThrough;\n
  base.ThisExpression = ignore;\n
  base.ArrayExpression = function(node, st, c) {\n
    for (var i = 0; i < node.elements.length; ++i) {\n
      var elt = node.elements[i];\n
      if (elt) c(elt, st, "Expression");\n
    }\n
  };\n
  base.ObjectExpression = function(node, st, c) {\n
    for (var i = 0; i < node.properties.length; ++i)\n
      c(node.properties[i].value, st, "Expression");\n
  };\n
  base.FunctionExpression = base.FunctionDeclaration;\n
  base.SequenceExpression = function(node, st, c) {\n
    for (var i = 0; i < node.expressions.length; ++i)\n
      c(node.expressions[i], st, "Expression");\n
  };\n
  base.UnaryExpression = base.UpdateExpression = function(node, st, c) {\n
    c(node.argument, st, "Expression");\n
  };\n
  base.BinaryExpression = base.AssignmentExpression = base.LogicalExpression = function(node, st, c) {\n
    c(node.left, st, "Expression");\n
    c(node.right, st, "Expression");\n
  };\n
  base.ConditionalExpression = function(node, st, c) {\n
    c(node.test, st, "Expression");\n
    c(node.consequent, st, "Expression");\n
    c(node.alternate, st, "Expression");\n
  };\n
  base.NewExpression = base.CallExpression = function(node, st, c) {\n
    c(node.callee, st, "Expression");\n
    if (node.arguments) for (var i = 0; i < node.arguments.length; ++i)\n
      c(node.arguments[i], st, "Expression");\n
  };\n
  base.MemberExpression = function(node, st, c) {\n
    c(node.object, st, "Expression");\n
    if (node.computed) c(node.property, st, "Expression");\n
  };\n
  base.Identifier = base.Literal = ignore;\n
\n
  // A custom walker that keeps track of the scope chain and the\n
  // variables defined in it.\n
  function makeScope(prev, isCatch) {\n
    return {vars: Object.create(null), prev: prev, isCatch: isCatch};\n
  }\n
  function normalScope(scope) {\n
    while (scope.isCatch) scope = scope.prev;\n
    return scope;\n
  }\n
  exports.scopeVisitor = exports.make({\n
    Function: function(node, scope, c) {\n
      var inner = makeScope(scope);\n
      for (var i = 0; i < node.params.length; ++i)\n
        inner.vars[node.params[i].name] = {type: "argument", node: node.params[i]};\n
      if (node.id) {\n
        var decl = node.type == "FunctionDeclaration";\n
        (decl ? normalScope(scope) : inner).vars[node.id.name] =\n
          {type: decl ? "function" : "function name", node: node.id};\n
      }\n
      c(node.body, inner, "ScopeBody");\n
    },\n
    TryStatement: function(node, scope, c) {\n
      c(node.block, scope, "Statement");\n
      if (node.handler) {\n
        var inner = makeScope(scope, true);\n
        inner.vars[node.handler.param.name] = {type: "catch clause", node: node.handler.param};\n
        c(node.handler.body, inner, "ScopeBody");\n
      }\n
      if (node.finalizer) c(node.finalizer, scope, "Statement");\n
    },\n
    VariableDeclaration: function(node, scope, c) {\n
      var target = normalScope(scope);\n
      for (var i = 0; i < node.declarations.length; ++i) {\n
        var decl = node.declarations[i];\n
        target.vars[decl.id.name] = {type: "var", node: decl.id};\n
        if (decl.init) c(decl.init, scope, "Expression");\n
      }\n
    }\n
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
            <value> <int>10917</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
