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
            <value> <string>ts53452908.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>handlebars.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
\n
 handlebars v4.0.5\n
\n
Copyright (C) 2011-2015 by Yehuda Katz\n
\n
Permission is hereby granted, free of charge, to any person obtaining a copy\n
of this software and associated documentation files (the "Software"), to deal\n
in the Software without restriction, including without limitation the rights\n
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n
copies of the Software, and to permit persons to whom the Software is\n
furnished to do so, subject to the following conditions:\n
\n
The above copyright notice and this permission notice shall be included in\n
all copies or substantial portions of the Software.\n
\n
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n
THE SOFTWARE.\n
\n
@license\n
*/\n
(function webpackUniversalModuleDefinition(root, factory) {\n
\tif(typeof exports === \'object\' && typeof module === \'object\')\n
\t\tmodule.exports = factory();\n
\telse if(typeof define === \'function\' && define.amd)\n
\t\tdefine([], factory);\n
\telse if(typeof exports === \'object\')\n
\t\texports["Handlebars"] = factory();\n
\telse\n
\t\troot["Handlebars"] = factory();\n
})(this, function() {\n
return /******/ (function(modules) { // webpackBootstrap\n
/******/ \t// The module cache\n
/******/ \tvar installedModules = {};\n
\n
/******/ \t// The require function\n
/******/ \tfunction __webpack_require__(moduleId) {\n
\n
/******/ \t\t// Check if module is in cache\n
/******/ \t\tif(installedModules[moduleId])\n
/******/ \t\t\treturn installedModules[moduleId].exports;\n
\n
/******/ \t\t// Create a new module (and put it into the cache)\n
/******/ \t\tvar module = installedModules[moduleId] = {\n
/******/ \t\t\texports: {},\n
/******/ \t\t\tid: moduleId,\n
/******/ \t\t\tloaded: false\n
/******/ \t\t};\n
\n
/******/ \t\t// Execute the module function\n
/******/ \t\tmodules[moduleId].call(module.exports, module, module.exports, __webpack_require__);\n
\n
/******/ \t\t// Flag the module as loaded\n
/******/ \t\tmodule.loaded = true;\n
\n
/******/ \t\t// Return the exports of the module\n
/******/ \t\treturn module.exports;\n
/******/ \t}\n
\n
\n
/******/ \t// expose the modules object (__webpack_modules__)\n
/******/ \t__webpack_require__.m = modules;\n
\n
/******/ \t// expose the module cache\n
/******/ \t__webpack_require__.c = installedModules;\n
\n
/******/ \t// __webpack_public_path__\n
/******/ \t__webpack_require__.p = "";\n
\n
/******/ \t// Load entry module and return exports\n
/******/ \treturn __webpack_require__(0);\n
/******/ })\n
/************************************************************************/\n
/******/ ([\n
/* 0 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _handlebarsRuntime = __webpack_require__(2);\n
\n
\tvar _handlebarsRuntime2 = _interopRequireDefault(_handlebarsRuntime);\n
\n
\t// Compiler imports\n
\n
\tvar _handlebarsCompilerAst = __webpack_require__(21);\n
\n
\tvar _handlebarsCompilerAst2 = _interopRequireDefault(_handlebarsCompilerAst);\n
\n
\tvar _handlebarsCompilerBase = __webpack_require__(22);\n
\n
\tvar _handlebarsCompilerCompiler = __webpack_require__(27);\n
\n
\tvar _handlebarsCompilerJavascriptCompiler = __webpack_require__(28);\n
\n
\tvar _handlebarsCompilerJavascriptCompiler2 = _interopRequireDefault(_handlebarsCompilerJavascriptCompiler);\n
\n
\tvar _handlebarsCompilerVisitor = __webpack_require__(25);\n
\n
\tvar _handlebarsCompilerVisitor2 = _interopRequireDefault(_handlebarsCompilerVisitor);\n
\n
\tvar _handlebarsNoConflict = __webpack_require__(20);\n
\n
\tvar _handlebarsNoConflict2 = _interopRequireDefault(_handlebarsNoConflict);\n
\n
\tvar _create = _handlebarsRuntime2[\'default\'].create;\n
\tfunction create() {\n
\t  var hb = _create();\n
\n
\t  hb.compile = function (input, options) {\n
\t    return _handlebarsCompilerCompiler.compile(input, options, hb);\n
\t  };\n
\t  hb.precompile = function (input, options) {\n
\t    return _handlebarsCompilerCompiler.precompile(input, options, hb);\n
\t  };\n
\n
\t  hb.AST = _handlebarsCompilerAst2[\'default\'];\n
\t  hb.Compiler = _handlebarsCompilerCompiler.Compiler;\n
\t  hb.JavaScriptCompiler = _handlebarsCompilerJavascriptCompiler2[\'default\'];\n
\t  hb.Parser = _handlebarsCompilerBase.parser;\n
\t  hb.parse = _handlebarsCompilerBase.parse;\n
\n
\t  return hb;\n
\t}\n
\n
\tvar inst = create();\n
\tinst.create = create;\n
\n
\t_handlebarsNoConflict2[\'default\'](inst);\n
\n
\tinst.Visitor = _handlebarsCompilerVisitor2[\'default\'];\n
\n
\tinst[\'default\'] = inst;\n
\n
\texports[\'default\'] = inst;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 1 */\n
/***/ function(module, exports) {\n
\n
\t"use strict";\n
\n
\texports["default"] = function (obj) {\n
\t  return obj && obj.__esModule ? obj : {\n
\t    "default": obj\n
\t  };\n
\t};\n
\n
\texports.__esModule = true;\n
\n
/***/ },\n
/* 2 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireWildcard = __webpack_require__(3)[\'default\'];\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _handlebarsBase = __webpack_require__(4);\n
\n
\tvar base = _interopRequireWildcard(_handlebarsBase);\n
\n
\t// Each of these augment the Handlebars object. No need to setup here.\n
\t// (This is done to easily share code between commonjs and browse envs)\n
\n
\tvar _handlebarsSafeString = __webpack_require__(18);\n
\n
\tvar _handlebarsSafeString2 = _interopRequireDefault(_handlebarsSafeString);\n
\n
\tvar _handlebarsException = __webpack_require__(6);\n
\n
\tvar _handlebarsException2 = _interopRequireDefault(_handlebarsException);\n
\n
\tvar _handlebarsUtils = __webpack_require__(5);\n
\n
\tvar Utils = _interopRequireWildcard(_handlebarsUtils);\n
\n
\tvar _handlebarsRuntime = __webpack_require__(19);\n
\n
\tvar runtime = _interopRequireWildcard(_handlebarsRuntime);\n
\n
\tvar _handlebarsNoConflict = __webpack_require__(20);\n
\n
\tvar _handlebarsNoConflict2 = _interopRequireDefault(_handlebarsNoConflict);\n
\n
\t// For compatibility and usage outside of module systems, make the Handlebars object a namespace\n
\tfunction create() {\n
\t  var hb = new base.HandlebarsEnvironment();\n
\n
\t  Utils.extend(hb, base);\n
\t  hb.SafeString = _handlebarsSafeString2[\'default\'];\n
\t  hb.Exception = _handlebarsException2[\'default\'];\n
\t  hb.Utils = Utils;\n
\t  hb.escapeExpression = Utils.escapeExpression;\n
\n
\t  hb.VM = runtime;\n
\t  hb.template = function (spec) {\n
\t    return runtime.template(spec, hb);\n
\t  };\n
\n
\t  return hb;\n
\t}\n
\n
\tvar inst = create();\n
\tinst.create = create;\n
\n
\t_handlebarsNoConflict2[\'default\'](inst);\n
\n
\tinst[\'default\'] = inst;\n
\n
\texports[\'default\'] = inst;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 3 */\n
/***/ function(module, exports) {\n
\n
\t"use strict";\n
\n
\texports["default"] = function (obj) {\n
\t  if (obj && obj.__esModule) {\n
\t    return obj;\n
\t  } else {\n
\t    var newObj = {};\n
\n
\t    if (obj != null) {\n
\t      for (var key in obj) {\n
\t        if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key];\n
\t      }\n
\t    }\n
\n
\t    newObj["default"] = obj;\n
\t    return newObj;\n
\t  }\n
\t};\n
\n
\texports.__esModule = true;\n
\n
/***/ },\n
/* 4 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.HandlebarsEnvironment = HandlebarsEnvironment;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tvar _helpers = __webpack_require__(7);\n
\n
\tvar _decorators = __webpack_require__(15);\n
\n
\tvar _logger = __webpack_require__(17);\n
\n
\tvar _logger2 = _interopRequireDefault(_logger);\n
\n
\tvar VERSION = \'4.0.5\';\n
\texports.VERSION = VERSION;\n
\tvar COMPILER_REVISION = 7;\n
\n
\texports.COMPILER_REVISION = COMPILER_REVISION;\n
\tvar REVISION_CHANGES = {\n
\t  1: \'<= 1.0.rc.2\', // 1.0.rc.2 is actually rev2 but doesn\'t report it\n
\t  2: \'== 1.0.0-rc.3\',\n
\t  3: \'== 1.0.0-rc.4\',\n
\t  4: \'== 1.x.x\',\n
\t  5: \'== 2.0.0-alpha.x\',\n
\t  6: \'>= 2.0.0-beta.1\',\n
\t  7: \'>= 4.0.0\'\n
\t};\n
\n
\texports.REVISION_CHANGES = REVISION_CHANGES;\n
\tvar objectType = \'[object Object]\';\n
\n
\tfunction HandlebarsEnvironment(helpers, partials, decorators) {\n
\t  this.helpers = helpers || {};\n
\t  this.partials = partials || {};\n
\t  this.decorators = decorators || {};\n
\n
\t  _helpers.registerDefaultHelpers(this);\n
\t  _decorators.registerDefaultDecorators(this);\n
\t}\n
\n
\tHandlebarsEnvironment.prototype = {\n
\t  constructor: HandlebarsEnvironment,\n
\n
\t  logger: _logger2[\'default\'],\n
\t  log: _logger2[\'default\'].log,\n
\n
\t  registerHelper: function registerHelper(name, fn) {\n
\t    if (_utils.toString.call(name) === objectType) {\n
\t      if (fn) {\n
\t        throw new _exception2[\'default\'](\'Arg not supported with multiple helpers\');\n
\t      }\n
\t      _utils.extend(this.helpers, name);\n
\t    } else {\n
\t      this.helpers[name] = fn;\n
\t    }\n
\t  },\n
\t  unregisterHelper: function unregisterHelper(name) {\n
\t    delete this.helpers[name];\n
\t  },\n
\n
\t  registerPartial: function registerPartial(name, partial) {\n
\t    if (_utils.toString.call(name) === objectType) {\n
\t      _utils.extend(this.partials, name);\n
\t    } else {\n
\t      if (typeof partial === \'undefined\') {\n
\t        throw new _exception2[\'default\'](\'Attempting to register a partial called "\' + name + \'" as undefined\');\n
\t      }\n
\t      this.partials[name] = partial;\n
\t    }\n
\t  },\n
\t  unregisterPartial: function unregisterPartial(name) {\n
\t    delete this.partials[name];\n
\t  },\n
\n
\t  registerDecorator: function registerDecorator(name, fn) {\n
\t    if (_utils.toString.call(name) === objectType) {\n
\t      if (fn) {\n
\t        throw new _exception2[\'default\'](\'Arg not supported with multiple decorators\');\n
\t      }\n
\t      _utils.extend(this.decorators, name);\n
\t    } else {\n
\t      this.decorators[name] = fn;\n
\t    }\n
\t  },\n
\t  unregisterDecorator: function unregisterDecorator(name) {\n
\t    delete this.decorators[name];\n
\t  }\n
\t};\n
\n
\tvar log = _logger2[\'default\'].log;\n
\n
\texports.log = log;\n
\texports.createFrame = _utils.createFrame;\n
\texports.logger = _logger2[\'default\'];\n
\n
/***/ },\n
/* 5 */\n
/***/ function(module, exports) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\texports.extend = extend;\n
\texports.indexOf = indexOf;\n
\texports.escapeExpression = escapeExpression;\n
\texports.isEmpty = isEmpty;\n
\texports.createFrame = createFrame;\n
\texports.blockParams = blockParams;\n
\texports.appendContextPath = appendContextPath;\n
\tvar escape = {\n
\t  \'&\': \'&amp;\',\n
\t  \'<\': \'&lt;\',\n
\t  \'>\': \'&gt;\',\n
\t  \'"\': \'&quot;\',\n
\t  "\'": \'&#x27;\',\n
\t  \'`\': \'&#x60;\',\n
\t  \'=\': \'&#x3D;\'\n
\t};\n
\n
\tvar badChars = /[&<>"\'`=]/g,\n
\t    possible = /[&<>"\'`=]/;\n
\n
\tfunction escapeChar(chr) {\n
\t  return escape[chr];\n
\t}\n
\n
\tfunction extend(obj /* , ...source */) {\n
\t  for (var i = 1; i < arguments.length; i++) {\n
\t    for (var key in arguments[i]) {\n
\t      if (Object.prototype.hasOwnProperty.call(arguments[i], key)) {\n
\t        obj[key] = arguments[i][key];\n
\t      }\n
\t    }\n
\t  }\n
\n
\t  return obj;\n
\t}\n
\n
\tvar toString = Object.prototype.toString;\n
\n
\texports.toString = toString;\n
\t// Sourced from lodash\n
\t// https://github.com/bestiejs/lodash/blob/master/LICENSE.txt\n
\t/* eslint-disable func-style */\n
\tvar isFunction = function isFunction(value) {\n
\t  return typeof value === \'function\';\n
\t};\n
\t// fallback for older versions of Chrome and Safari\n
\t/* istanbul ignore next */\n
\tif (isFunction(/x/)) {\n
\t  exports.isFunction = isFunction = function (value) {\n
\t    return typeof value === \'function\' && toString.call(value) === \'[object Function]\';\n
\t  };\n
\t}\n
\texports.isFunction = isFunction;\n
\n
\t/* eslint-enable func-style */\n
\n
\t/* istanbul ignore next */\n
\tvar isArray = Array.isArray || function (value) {\n
\t  return value && typeof value === \'object\' ? toString.call(value) === \'[object Array]\' : false;\n
\t};\n
\n
\texports.isArray = isArray;\n
\t// Older IE versions do not directly support indexOf so we must implement our own, sadly.\n
\n
\tfunction indexOf(array, value) {\n
\t  for (var i = 0, len = array.length; i < len; i++) {\n
\t    if (array[i] === value) {\n
\t      return i;\n
\t    }\n
\t  }\n
\t  return -1;\n
\t}\n
\n
\tfunction escapeExpression(string) {\n
\t  if (typeof string !== \'string\') {\n
\t    // don\'t escape SafeStrings, since they\'re already safe\n
\t    if (string && string.toHTML) {\n
\t      return string.toHTML();\n
\t    } else if (string == null) {\n
\t      return \'\';\n
\t    } else if (!string) {\n
\t      return string + \'\';\n
\t    }\n
\n
\t    // Force a string conversion as this will be done by the append regardless and\n
\t    // the regex test will do this transparently behind the scenes, causing issues if\n
\t    // an object\'s to string has escaped characters in it.\n
\t    string = \'\' + string;\n
\t  }\n
\n
\t  if (!possible.test(string)) {\n
\t    return string;\n
\t  }\n
\t  return string.replace(badChars, escapeChar);\n
\t}\n
\n
\tfunction isEmpty(value) {\n
\t  if (!value && value !== 0) {\n
\t    return true;\n
\t  } else if (isArray(value) && value.length === 0) {\n
\t    return true;\n
\t  } else {\n
\t    return false;\n
\t  }\n
\t}\n
\n
\tfunction createFrame(object) {\n
\t  var frame = extend({}, object);\n
\t  frame._parent = object;\n
\t  return frame;\n
\t}\n
\n
\tfunction blockParams(params, ids) {\n
\t  params.path = ids;\n
\t  return params;\n
\t}\n
\n
\tfunction appendContextPath(contextPath, id) {\n
\t  return (contextPath ? contextPath + \'.\' : \'\') + id;\n
\t}\n
\n
/***/ },\n
/* 6 */\n
/***/ function(module, exports) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar errorProps = [\'description\', \'fileName\', \'lineNumber\', \'message\', \'name\', \'number\', \'stack\'];\n
\n
\tfunction Exception(message, node) {\n
\t  var loc = node && node.loc,\n
\t      line = undefined,\n
\t      column = undefined;\n
\t  if (loc) {\n
\t    line = loc.start.line;\n
\t    column = loc.start.column;\n
\n
\t    message += \' - \' + line + \':\' + column;\n
\t  }\n
\n
\t  var tmp = Error.prototype.constructor.call(this, message);\n
\n
\t  // Unfortunately errors are not enumerable in Chrome (at least), so `for prop in tmp` doesn\'t work.\n
\t  for (var idx = 0; idx < errorProps.length; idx++) {\n
\t    this[errorProps[idx]] = tmp[errorProps[idx]];\n
\t  }\n
\n
\t  /* istanbul ignore else */\n
\t  if (Error.captureStackTrace) {\n
\t    Error.captureStackTrace(this, Exception);\n
\t  }\n
\n
\t  if (loc) {\n
\t    this.lineNumber = line;\n
\t    this.column = column;\n
\t  }\n
\t}\n
\n
\tException.prototype = new Error();\n
\n
\texports[\'default\'] = Exception;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 7 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.registerDefaultHelpers = registerDefaultHelpers;\n
\n
\tvar _helpersBlockHelperMissing = __webpack_require__(8);\n
\n
\tvar _helpersBlockHelperMissing2 = _interopRequireDefault(_helpersBlockHelperMissing);\n
\n
\tvar _helpersEach = __webpack_require__(9);\n
\n
\tvar _helpersEach2 = _interopRequireDefault(_helpersEach);\n
\n
\tvar _helpersHelperMissing = __webpack_require__(10);\n
\n
\tvar _helpersHelperMissing2 = _interopRequireDefault(_helpersHelperMissing);\n
\n
\tvar _helpersIf = __webpack_require__(11);\n
\n
\tvar _helpersIf2 = _interopRequireDefault(_helpersIf);\n
\n
\tvar _helpersLog = __webpack_require__(12);\n
\n
\tvar _helpersLog2 = _interopRequireDefault(_helpersLog);\n
\n
\tvar _helpersLookup = __webpack_require__(13);\n
\n
\tvar _helpersLookup2 = _interopRequireDefault(_helpersLookup);\n
\n
\tvar _helpersWith = __webpack_require__(14);\n
\n
\tvar _helpersWith2 = _interopRequireDefault(_helpersWith);\n
\n
\tfunction registerDefaultHelpers(instance) {\n
\t  _helpersBlockHelperMissing2[\'default\'](instance);\n
\t  _helpersEach2[\'default\'](instance);\n
\t  _helpersHelperMissing2[\'default\'](instance);\n
\t  _helpersIf2[\'default\'](instance);\n
\t  _helpersLog2[\'default\'](instance);\n
\t  _helpersLookup2[\'default\'](instance);\n
\t  _helpersWith2[\'default\'](instance);\n
\t}\n
\n
/***/ },\n
/* 8 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'blockHelperMissing\', function (context, options) {\n
\t    var inverse = options.inverse,\n
\t        fn = options.fn;\n
\n
\t    if (context === true) {\n
\t      return fn(this);\n
\t    } else if (context === false || context == null) {\n
\t      return inverse(this);\n
\t    } else if (_utils.isArray(context)) {\n
\t      if (context.length > 0) {\n
\t        if (options.ids) {\n
\t          options.ids = [options.name];\n
\t        }\n
\n
\t        return instance.helpers.each(context, options);\n
\t      } else {\n
\t        return inverse(this);\n
\t      }\n
\t    } else {\n
\t      if (options.data && options.ids) {\n
\t        var data = _utils.createFrame(options.data);\n
\t        data.contextPath = _utils.appendContextPath(options.data.contextPath, options.name);\n
\t        options = { data: data };\n
\t      }\n
\n
\t      return fn(context, options);\n
\t    }\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 9 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'each\', function (context, options) {\n
\t    if (!options) {\n
\t      throw new _exception2[\'default\'](\'Must pass iterator to #each\');\n
\t    }\n
\n
\t    var fn = options.fn,\n
\t        inverse = options.inverse,\n
\t        i = 0,\n
\t        ret = \'\',\n
\t        data = undefined,\n
\t        contextPath = undefined;\n
\n
\t    if (options.data && options.ids) {\n
\t      contextPath = _utils.appendContextPath(options.data.contextPath, options.ids[0]) + \'.\';\n
\t    }\n
\n
\t    if (_utils.isFunction(context)) {\n
\t      context = context.call(this);\n
\t    }\n
\n
\t    if (options.data) {\n
\t      data = _utils.createFrame(options.data);\n
\t    }\n
\n
\t    function execIteration(field, index, last) {\n
\t      if (data) {\n
\t        data.key = field;\n
\t        data.index = index;\n
\t        data.first = index === 0;\n
\t        data.last = !!last;\n
\n
\t        if (contextPath) {\n
\t          data.contextPath = contextPath + field;\n
\t        }\n
\t      }\n
\n
\t      ret = ret + fn(context[field], {\n
\t        data: data,\n
\t        blockParams: _utils.blockParams([context[field], field], [contextPath + field, null])\n
\t      });\n
\t    }\n
\n
\t    if (context && typeof context === \'object\') {\n
\t      if (_utils.isArray(context)) {\n
\t        for (var j = context.length; i < j; i++) {\n
\t          if (i in context) {\n
\t            execIteration(i, i, i === context.length - 1);\n
\t          }\n
\t        }\n
\t      } else {\n
\t        var priorKey = undefined;\n
\n
\t        for (var key in context) {\n
\t          if (context.hasOwnProperty(key)) {\n
\t            // We\'re running the iterations one step out of sync so we can detect\n
\t            // the last iteration without have to scan the object twice and create\n
\t            // an itermediate keys array.\n
\t            if (priorKey !== undefined) {\n
\t              execIteration(priorKey, i - 1);\n
\t            }\n
\t            priorKey = key;\n
\t            i++;\n
\t          }\n
\t        }\n
\t        if (priorKey !== undefined) {\n
\t          execIteration(priorKey, i - 1, true);\n
\t        }\n
\t      }\n
\t    }\n
\n
\t    if (i === 0) {\n
\t      ret = inverse(this);\n
\t    }\n
\n
\t    return ret;\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 10 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'helperMissing\', function () /* [args, ]options */{\n
\t    if (arguments.length === 1) {\n
\t      // A missing field in a {{foo}} construct.\n
\t      return undefined;\n
\t    } else {\n
\t      // Someone is actually trying to call something, blow up.\n
\t      throw new _exception2[\'default\'](\'Missing helper: "\' + arguments[arguments.length - 1].name + \'"\');\n
\t    }\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 11 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'if\', function (conditional, options) {\n
\t    if (_utils.isFunction(conditional)) {\n
\t      conditional = conditional.call(this);\n
\t    }\n
\n
\t    // Default behavior is to render the positive path if the value is truthy and not empty.\n
\t    // The `includeZero` option may be set to treat the condtional as purely not empty based on the\n
\t    // behavior of isEmpty. Effectively this determines if 0 is handled by the positive path or negative.\n
\t    if (!options.hash.includeZero && !conditional || _utils.isEmpty(conditional)) {\n
\t      return options.inverse(this);\n
\t    } else {\n
\t      return options.fn(this);\n
\t    }\n
\t  });\n
\n
\t  instance.registerHelper(\'unless\', function (conditional, options) {\n
\t    return instance.helpers[\'if\'].call(this, conditional, { fn: options.inverse, inverse: options.fn, hash: options.hash });\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 12 */\n
/***/ function(module, exports) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'log\', function () /* message, options */{\n
\t    var args = [undefined],\n
\t        options = arguments[arguments.length - 1];\n
\t    for (var i = 0; i < arguments.length - 1; i++) {\n
\t      args.push(arguments[i]);\n
\t    }\n
\n
\t    var level = 1;\n
\t    if (options.hash.level != null) {\n
\t      level = options.hash.level;\n
\t    } else if (options.data && options.data.level != null) {\n
\t      level = options.data.level;\n
\t    }\n
\t    args[0] = level;\n
\n
\t    instance.log.apply(instance, args);\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 13 */\n
/***/ function(module, exports) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'lookup\', function (obj, field) {\n
\t    return obj && obj[field];\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 14 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerHelper(\'with\', function (context, options) {\n
\t    if (_utils.isFunction(context)) {\n
\t      context = context.call(this);\n
\t    }\n
\n
\t    var fn = options.fn;\n
\n
\t    if (!_utils.isEmpty(context)) {\n
\t      var data = options.data;\n
\t      if (options.data && options.ids) {\n
\t        data = _utils.createFrame(options.data);\n
\t        data.contextPath = _utils.appendContextPath(options.data.contextPath, options.ids[0]);\n
\t      }\n
\n
\t      return fn(context, {\n
\t        data: data,\n
\t        blockParams: _utils.blockParams([context], [data && data.contextPath])\n
\t      });\n
\t    } else {\n
\t      return options.inverse(this);\n
\t    }\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 15 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.registerDefaultDecorators = registerDefaultDecorators;\n
\n
\tvar _decoratorsInline = __webpack_require__(16);\n
\n
\tvar _decoratorsInline2 = _interopRequireDefault(_decoratorsInline);\n
\n
\tfunction registerDefaultDecorators(instance) {\n
\t  _decoratorsInline2[\'default\'](instance);\n
\t}\n
\n
/***/ },\n
/* 16 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\texports[\'default\'] = function (instance) {\n
\t  instance.registerDecorator(\'inline\', function (fn, props, container, options) {\n
\t    var ret = fn;\n
\t    if (!props.partials) {\n
\t      props.partials = {};\n
\t      ret = function (context, options) {\n
\t        // Create a new partials stack frame prior to exec.\n
\t        var original = container.partials;\n
\t        container.partials = _utils.extend({}, original, props.partials);\n
\t        var ret = fn(context, options);\n
\t        container.partials = original;\n
\t        return ret;\n
\t      };\n
\t    }\n
\n
\t    props.partials[options.args[0]] = options.fn;\n
\n
\t    return ret;\n
\t  });\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 17 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar logger = {\n
\t  methodMap: [\'debug\', \'info\', \'warn\', \'error\'],\n
\t  level: \'info\',\n
\n
\t  // Maps a given level value to the `methodMap` indexes above.\n
\t  lookupLevel: function lookupLevel(level) {\n
\t    if (typeof level === \'string\') {\n
\t      var levelMap = _utils.indexOf(logger.methodMap, level.toLowerCase());\n
\t      if (levelMap >= 0) {\n
\t        level = levelMap;\n
\t      } else {\n
\t        level = parseInt(level, 10);\n
\t      }\n
\t    }\n
\n
\t    return level;\n
\t  },\n
\n
\t  // Can be overridden in the host environment\n
\t  log: function log(level) {\n
\t    level = logger.lookupLevel(level);\n
\n
\t    if (typeof console !== \'undefined\' && logger.lookupLevel(logger.level) <= level) {\n
\t      var method = logger.methodMap[level];\n
\t      if (!console[method]) {\n
\t        // eslint-disable-line no-console\n
\t        method = \'log\';\n
\t      }\n
\n
\t      for (var _len = arguments.length, message = Array(_len > 1 ? _len - 1 : 0), _key = 1; _key < _len; _key++) {\n
\t        message[_key - 1] = arguments[_key];\n
\t      }\n
\n
\t      console[method].apply(console, message); // eslint-disable-line no-console\n
\t    }\n
\t  }\n
\t};\n
\n
\texports[\'default\'] = logger;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 18 */\n
/***/ function(module, exports) {\n
\n
\t// Build out our basic SafeString type\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\tfunction SafeString(string) {\n
\t  this.string = string;\n
\t}\n
\n
\tSafeString.prototype.toString = SafeString.prototype.toHTML = function () {\n
\t  return \'\' + this.string;\n
\t};\n
\n
\texports[\'default\'] = SafeString;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 19 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireWildcard = __webpack_require__(3)[\'default\'];\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.checkRevision = checkRevision;\n
\texports.template = template;\n
\texports.wrapProgram = wrapProgram;\n
\texports.resolvePartial = resolvePartial;\n
\texports.invokePartial = invokePartial;\n
\texports.noop = noop;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar Utils = _interopRequireWildcard(_utils);\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tvar _base = __webpack_require__(4);\n
\n
\tfunction checkRevision(compilerInfo) {\n
\t  var compilerRevision = compilerInfo && compilerInfo[0] || 1,\n
\t      currentRevision = _base.COMPILER_REVISION;\n
\n
\t  if (compilerRevision !== currentRevision) {\n
\t    if (compilerRevision < currentRevision) {\n
\t      var runtimeVersions = _base.REVISION_CHANGES[currentRevision],\n
\t          compilerVersions = _base.REVISION_CHANGES[compilerRevision];\n
\t      throw new _exception2[\'default\'](\'Template was precompiled with an older version of Handlebars than the current runtime. \' + \'Please update your precompiler to a newer version (\' + runtimeVersions + \') or downgrade your runtime to an older version (\' + compilerVersions + \').\');\n
\t    } else {\n
\t      // Use the embedded version info since the runtime doesn\'t know about this revision yet\n
\t      throw new _exception2[\'default\'](\'Template was precompiled with a newer version of Handlebars than the current runtime. \' + \'Please update your runtime to a newer version (\' + compilerInfo[1] + \').\');\n
\t    }\n
\t  }\n
\t}\n
\n
\tfunction template(templateSpec, env) {\n
\t  /* istanbul ignore next */\n
\t  if (!env) {\n
\t    throw new _exception2[\'default\'](\'No environment passed to template\');\n
\t  }\n
\t  if (!templateSpec || !templateSpec.main) {\n
\t    throw new _exception2[\'default\'](\'Unknown template object: \' + typeof templateSpec);\n
\t  }\n
\n
\t  templateSpec.main.decorator = templateSpec.main_d;\n
\n
\t  // Note: Using env.VM references rather than local var references throughout this section to allow\n
\t  // for external users to override these as psuedo-supported APIs.\n
\t  env.VM.checkRevision(templateSpec.compiler);\n
\n
\t  function invokePartialWrapper(partial, context, options) {\n
\t    if (options.hash) {\n
\t      context = Utils.extend({}, context, options.hash);\n
\t      if (options.ids) {\n
\t        options.ids[0] = true;\n
\t      }\n
\t    }\n
\n
\t    partial = env.VM.resolvePartial.call(this, partial, context, options);\n
\t    var result = env.VM.invokePartial.call(this, partial, context, options);\n
\n
\t    if (result == null && env.compile) {\n
\t      options.partials[options.name] = env.compile(partial, templateSpec.compilerOptions, env);\n
\t      result = options.partials[options.name](context, options);\n
\t    }\n
\t    if (result != null) {\n
\t      if (options.indent) {\n
\t        var lines = result.split(\'\\n\');\n
\t        for (var i = 0, l = lines.length; i < l; i++) {\n
\t          if (!lines[i] && i + 1 === l) {\n
\t            break;\n
\t          }\n
\n
\t          lines[i] = options.indent + lines[i];\n
\t        }\n
\t        result = lines.join(\'\\n\');\n
\t      }\n
\t      return result;\n
\t    } else {\n
\t      throw new _exception2[\'default\'](\'The partial \' + options.name + \' could not be compiled when running in runtime-only mode\');\n
\t    }\n
\t  }\n
\n
\t  // Just add water\n
\t  var container = {\n
\t    strict: function strict(obj, name) {\n
\t      if (!(name in obj)) {\n
\t        throw new _exception2[\'default\'](\'"\' + name + \'" not defined in \' + obj);\n
\t      }\n
\t      return obj[name];\n
\t    },\n
\t    lookup: function lookup(depths, name) {\n
\t      var len = depths.length;\n
\t      for (var i = 0; i < len; i++) {\n
\t        if (depths[i] && depths[i][name] != null) {\n
\t          return depths[i][name];\n
\t        }\n
\t      }\n
\t    },\n
\t    lambda: function lambda(current, context) {\n
\t      return typeof current === \'function\' ? current.call(context) : current;\n
\t    },\n
\n
\t    escapeExpression: Utils.escapeExpression,\n
\t    invokePartial: invokePartialWrapper,\n
\n
\t    fn: function fn(i) {\n
\t      var ret = templateSpec[i];\n
\t      ret.decorator = templateSpec[i + \'_d\'];\n
\t      return ret;\n
\t    },\n
\n
\t    programs: [],\n
\t    program: function program(i, data, declaredBlockParams, blockParams, depths) {\n
\t      var programWrapper = this.programs[i],\n
\t          fn = this.fn(i);\n
\t      if (data || depths || blockParams || declaredBlockParams) {\n
\t        programWrapper = wrapProgram(this, i, fn, data, declaredBlockParams, blockParams, depths);\n
\t      } else if (!programWrapper) {\n
\t        programWrapper = this.programs[i] = wrapProgram(this, i, fn);\n
\t      }\n
\t      return programWrapper;\n
\t    },\n
\n
\t    data: function data(value, depth) {\n
\t      while (value && depth--) {\n
\t        value = value._parent;\n
\t      }\n
\t      return value;\n
\t    },\n
\t    merge: function merge(param, common) {\n
\t      var obj = param || common;\n
\n
\t      if (param && common && param !== common) {\n
\t        obj = Utils.extend({}, common, param);\n
\t      }\n
\n
\t      return obj;\n
\t    },\n
\n
\t    noop: env.VM.noop,\n
\t    compilerInfo: templateSpec.compiler\n
\t  };\n
\n
\t  function ret(context) {\n
\t    var options = arguments.length <= 1 || arguments[1] === undefined ? {} : arguments[1];\n
\n
\t    var data = options.data;\n
\n
\t    ret._setup(options);\n
\t    if (!options.partial && templateSpec.useData) {\n
\t      data = initData(context, data);\n
\t    }\n
\t    var depths = undefined,\n
\t        blockParams = templateSpec.useBlockParams ? [] : undefined;\n
\t    if (templateSpec.useDepths) {\n
\t      if (options.depths) {\n
\t        depths = context !== options.depths[0] ? [context].concat(options.depths) : options.depths;\n
\t      } else {\n
\t        depths = [context];\n
\t      }\n
\t    }\n
\n
\t    function main(context /*, options*/) {\n
\t      return \'\' + templateSpec.main(container, context, container.helpers, container.partials, data, blockParams, depths);\n
\t    }\n
\t    main = executeDecorators(templateSpec.main, main, container, options.depths || [], data, blockParams);\n
\t    return main(context, options);\n
\t  }\n
\t  ret.isTop = true;\n
\n
\t  ret._setup = function (options) {\n
\t    if (!options.partial) {\n
\t      container.helpers = container.merge(options.helpers, env.helpers);\n
\n
\t      if (templateSpec.usePartial) {\n
\t        container.partials = container.merge(options.partials, env.partials);\n
\t      }\n
\t      if (templateSpec.usePartial || templateSpec.useDecorators) {\n
\t        container.decorators = container.merge(options.decorators, env.decorators);\n
\t      }\n
\t    } else {\n
\t      container.helpers = options.helpers;\n
\t      container.partials = options.partials;\n
\t      container.decorators = options.decorators;\n
\t    }\n
\t  };\n
\n
\t  ret._child = function (i, data, blockParams, depths) {\n
\t    if (templateSpec.useBlockParams && !blockParams) {\n
\t      throw new _exception2[\'default\'](\'must pass block params\');\n
\t    }\n
\t    if (templateSpec.useDepths && !depths) {\n
\t      throw new _exception2[\'default\'](\'must pass parent depths\');\n
\t    }\n
\n
\t    return wrapProgram(container, i, templateSpec[i], data, 0, blockParams, depths);\n
\t  };\n
\t  return ret;\n
\t}\n
\n
\tfunction wrapProgram(container, i, fn, data, declaredBlockParams, blockParams, depths) {\n
\t  function prog(context) {\n
\t    var options = arguments.length <= 1 || arguments[1] === undefined ? {} : arguments[1];\n
\n
\t    var currentDepths = depths;\n
\t    if (depths && context !== depths[0]) {\n
\t      currentDepths = [context].concat(depths);\n
\t    }\n
\n
\t    return fn(container, context, container.helpers, container.partials, options.data || data, blockParams && [options.blockParams].concat(blockParams), currentDepths);\n
\t  }\n
\n
\t  prog = executeDecorators(fn, prog, container, depths, data, blockParams);\n
\n
\t  prog.program = i;\n
\t  prog.depth = depths ? depths.length : 0;\n
\t  prog.blockParams = declaredBlockParams || 0;\n
\t  return prog;\n
\t}\n
\n
\tfunction resolvePartial(partial, context, options) {\n
\t  if (!partial) {\n
\t    if (options.name === \'@partial-block\') {\n
\t      partial = options.data[\'partial-block\'];\n
\t    } else {\n
\t      partial = options.partials[options.name];\n
\t    }\n
\t  } else if (!partial.call && !options.name) {\n
\t    // This is a dynamic partial that returned a string\n
\t    options.name = partial;\n
\t    partial = options.partials[partial];\n
\t  }\n
\t  return partial;\n
\t}\n
\n
\tfunction invokePartial(partial, context, options) {\n
\t  options.partial = true;\n
\t  if (options.ids) {\n
\t    options.data.contextPath = options.ids[0] || options.data.contextPath;\n
\t  }\n
\n
\t  var partialBlock = undefined;\n
\t  if (options.fn && options.fn !== noop) {\n
\t    options.data = _base.createFrame(options.data);\n
\t    partialBlock = options.data[\'partial-block\'] = options.fn;\n
\n
\t    if (partialBlock.partials) {\n
\t      options.partials = Utils.extend({}, options.partials, partialBlock.partials);\n
\t    }\n
\t  }\n
\n
\t  if (partial === undefined && partialBlock) {\n
\t    partial = partialBlock;\n
\t  }\n
\n
\t  if (partial === undefined) {\n
\t    throw new _exception2[\'default\'](\'The partial \' + options.name + \' could not be found\');\n
\t  } else if (partial instanceof Function) {\n
\t    return partial(context, options);\n
\t  }\n
\t}\n
\n
\tfunction noop() {\n
\t  return \'\';\n
\t}\n
\n
\tfunction initData(context, data) {\n
\t  if (!data || !(\'root\' in data)) {\n
\t    data = data ? _base.createFrame(data) : {};\n
\t    data.root = context;\n
\t  }\n
\t  return data;\n
\t}\n
\n
\tfunction executeDecorators(fn, prog, container, depths, data, blockParams) {\n
\t  if (fn.decorator) {\n
\t    var props = {};\n
\t    prog = fn.decorator(prog, props, container, depths && depths[0], data, blockParams, depths);\n
\t    Utils.extend(prog, props);\n
\t  }\n
\t  return prog;\n
\t}\n
\n
/***/ },\n
/* 20 */\n
/***/ function(module, exports) {\n
\n
\t/* WEBPACK VAR INJECTION */(function(global) {/* global window */\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\texports[\'default\'] = function (Handlebars) {\n
\t  /* istanbul ignore next */\n
\t  var root = typeof global !== \'undefined\' ? global : window,\n
\t      $Handlebars = root.Handlebars;\n
\t  /* istanbul ignore next */\n
\t  Handlebars.noConflict = function () {\n
\t    if (root.Handlebars === Handlebars) {\n
\t      root.Handlebars = $Handlebars;\n
\t    }\n
\t    return Handlebars;\n
\t  };\n
\t};\n
\n
\tmodule.exports = exports[\'default\'];\n
\t/* WEBPACK VAR INJECTION */}.call(exports, (function() { return this; }())))\n
\n
/***/ },\n
/* 21 */\n
/***/ function(module, exports) {\n
\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\tvar AST = {\n
\t  // Public API used to evaluate derived attributes regarding AST nodes\n
\t  helpers: {\n
\t    // a mustache is definitely a helper if:\n
\t    // * it is an eligible helper, and\n
\t    // * it has at least one parameter or hash segment\n
\t    helperExpression: function helperExpression(node) {\n
\t      return node.type === \'SubExpression\' || (node.type === \'MustacheStatement\' || node.type === \'BlockStatement\') && !!(node.params && node.params.length || node.hash);\n
\t    },\n
\n
\t    scopedId: function scopedId(path) {\n
\t      return (/^\\.|this\\b/.test(path.original)\n
\t      );\n
\t    },\n
\n
\t    // an ID is simple if it only has one part, and that part is not\n
\t    // `..` or `this`.\n
\t    simpleId: function simpleId(path) {\n
\t      return path.parts.length === 1 && !AST.helpers.scopedId(path) && !path.depth;\n
\t    }\n
\t  }\n
\t};\n
\n
\t// Must be exported as an object rather than the root of the module as the jison lexer\n
\t// must modify the object to operate properly.\n
\texports[\'default\'] = AST;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 22 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\tvar _interopRequireWildcard = __webpack_require__(3)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.parse = parse;\n
\n
\tvar _parser = __webpack_require__(23);\n
\n
\tvar _parser2 = _interopRequireDefault(_parser);\n
\n
\tvar _whitespaceControl = __webpack_require__(24);\n
\n
\tvar _whitespaceControl2 = _interopRequireDefault(_whitespaceControl);\n
\n
\tvar _helpers = __webpack_require__(26);\n
\n
\tvar Helpers = _interopRequireWildcard(_helpers);\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\texports.parser = _parser2[\'default\'];\n
\n
\tvar yy = {};\n
\t_utils.extend(yy, Helpers);\n
\n
\tfunction parse(input, options) {\n
\t  // Just return if an already-compiled AST was passed in.\n
\t  if (input.type === \'Program\') {\n
\t    return input;\n
\t  }\n
\n
\t  _parser2[\'default\'].yy = yy;\n
\n
\t  // Altering the shared object here, but this is ok as parser is a sync operation\n
\t  yy.locInfo = function (locInfo) {\n
\t    return new yy.SourceLocation(options && options.srcName, locInfo);\n
\t  };\n
\n
\t  var strip = new _whitespaceControl2[\'default\'](options);\n
\t  return strip.accept(_parser2[\'default\'].parse(input));\n
\t}\n
\n
/***/ },\n
/* 23 */\n
/***/ function(module, exports) {\n
\n
\t/* istanbul ignore next */\n
\t/* Jison generated parser */\n
\t"use strict";\n
\n
\tvar handlebars = (function () {\n
\t    var parser = { trace: function trace() {},\n
\t        yy: {},\n
\t        symbols_: { "error": 2, "root": 3, "program": 4, "EOF": 5, "program_repetition0": 6, "statement": 7, "mustache": 8, "block": 9, "rawBlock": 10, "partial": 11, "partialBlock": 12, "content": 13, "COMMENT": 14, "CONTENT": 15, "openRawBlock": 16, "rawBlock_repetition_plus0": 17, "END_RAW_BLOCK": 18, "OPEN_RAW_BLOCK": 19, "helperName": 20, "openRawBlock_repetition0": 21, "openRawBlock_option0": 22, "CLOSE_RAW_BLOCK": 23, "openBlock": 24, "block_option0": 25, "closeBlock": 26, "openInverse": 27, "block_option1": 28, "OPEN_BLOCK": 29, "openBlock_repetition0": 30, "openBlock_option0": 31, "openBlock_option1": 32, "CLOSE": 33, "OPEN_INVERSE": 34, "openInverse_repetition0": 35, "openInverse_option0": 36, "openInverse_option1": 37, "openInverseChain": 38, "OPEN_INVERSE_CHAIN": 39, "openInverseChain_repetition0": 40, "openInverseChain_option0": 41, "openInverseChain_option1": 42, "inverseAndProgram": 43, "INVERSE": 44, "inverseChain": 45, "inverseChain_option0": 46, "OPEN_ENDBLOCK": 47, "OPEN": 48, "mustache_repetition0": 49, "mustache_option0": 50, "OPEN_UNESCAPED": 51, "mustache_repetition1": 52, "mustache_option1": 53, "CLOSE_UNESCAPED": 54, "OPEN_PARTIAL": 55, "partialName": 56, "partial_repetition0": 57, "partial_option0": 58, "openPartialBlock": 59, "OPEN_PARTIAL_BLOCK": 60, "openPartialBlock_repetition0": 61, "openPartialBlock_option0": 62, "param": 63, "sexpr": 64, "OPEN_SEXPR": 65, "sexpr_repetition0": 66, "sexpr_option0": 67, "CLOSE_SEXPR": 68, "hash": 69, "hash_repetition_plus0": 70, "hashSegment": 71, "ID": 72, "EQUALS": 73, "blockParams": 74, "OPEN_BLOCK_PARAMS": 75, "blockParams_repetition_plus0": 76, "CLOSE_BLOCK_PARAMS": 77, "path": 78, "dataName": 79, "STRING": 80, "NUMBER": 81, "BOOLEAN": 82, "UNDEFINED": 83, "NULL": 84, "DATA": 85, "pathSegments": 86, "SEP": 87, "$accept": 0, "$end": 1 },\n
\t        terminals_: { 2: "error", 5: "EOF", 14: "COMMENT", 15: "CONTENT", 18: "END_RAW_BLOCK", 19: "OPEN_RAW_BLOCK", 23: "CLOSE_RAW_BLOCK", 29: "OPEN_BLOCK", 33: "CLOSE", 34: "OPEN_INVERSE", 39: "OPEN_INVERSE_CHAIN", 44: "INVERSE", 47: "OPEN_ENDBLOCK", 48: "OPEN", 51: "OPEN_UNESCAPED", 54: "CLOSE_UNESCAPED", 55: "OPEN_PARTIAL", 60: "OPEN_PARTIAL_BLOCK", 65: "OPEN_SEXPR", 68: "CLOSE_SEXPR", 72: "ID", 73: "EQUALS", 75: "OPEN_BLOCK_PARAMS", 77: "CLOSE_BLOCK_PARAMS", 80: "STRING", 81: "NUMBER", 82: "BOOLEAN", 83: "UNDEFINED", 84: "NULL", 85: "DATA", 87: "SEP" },\n
\t        productions_: [0, [3, 2], [4, 1], [7, 1], [7, 1], [7, 1], [7, 1], [7, 1], [7, 1], [7, 1], [13, 1], [10, 3], [16, 5], [9, 4], [9, 4], [24, 6], [27, 6], [38, 6], [43, 2], [45, 3], [45, 1], [26, 3], [8, 5], [8, 5], [11, 5], [12, 3], [59, 5], [63, 1], [63, 1], [64, 5], [69, 1], [71, 3], [74, 3], [20, 1], [20, 1], [20, 1], [20, 1], [20, 1], [20, 1], [20, 1], [56, 1], [56, 1], [79, 2], [78, 1], [86, 3], [86, 1], [6, 0], [6, 2], [17, 1], [17, 2], [21, 0], [21, 2], [22, 0], [22, 1], [25, 0], [25, 1], [28, 0], [28, 1], [30, 0], [30, 2], [31, 0], [31, 1], [32, 0], [32, 1], [35, 0], [35, 2], [36, 0], [36, 1], [37, 0], [37, 1], [40, 0], [40, 2], [41, 0], [41, 1], [42, 0], [42, 1], [46, 0], [46, 1], [49, 0], [49, 2], [50, 0], [50, 1], [52, 0], [52, 2], [53, 0], [53, 1], [57, 0], [57, 2], [58, 0], [58, 1], [61, 0], [61, 2], [62, 0], [62, 1], [66, 0], [66, 2], [67, 0], [67, 1], [70, 1], [70, 2], [76, 1], [76, 2]],\n
\t        performAction: function anonymous(yytext, yyleng, yylineno, yy, yystate, $$, _$\n
\t        /**/) {\n
\n
\t            var $0 = $$.length - 1;\n
\t            switch (yystate) {\n
\t                case 1:\n
\t                    return $$[$0 - 1];\n
\t                    break;\n
\t                case 2:\n
\t                    this.$ = yy.prepareProgram($$[$0]);\n
\t                    break;\n
\t                case 3:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 4:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 5:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 6:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 7:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 8:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 9:\n
\t                    this.$ = {\n
\t                        type: \'CommentStatement\',\n
\t                        value: yy.stripComment($$[$0]),\n
\t                        strip: yy.stripFlags($$[$0], $$[$0]),\n
\t                        loc: yy.locInfo(this._$)\n
\t                    };\n
\n
\t                    break;\n
\t                case 10:\n
\t                    this.$ = {\n
\t                        type: \'ContentStatement\',\n
\t                        original: $$[$0],\n
\t                        value: $$[$0],\n
\t                        loc: yy.locInfo(this._$)\n
\t                    };\n
\n
\t                    break;\n
\t                case 11:\n
\t                    this.$ = yy.prepareRawBlock($$[$0 - 2], $$[$0 - 1], $$[$0], this._$);\n
\t                    break;\n
\t                case 12:\n
\t                    this.$ = { path: $$[$0 - 3], params: $$[$0 - 2], hash: $$[$0 - 1] };\n
\t                    break;\n
\t                case 13:\n
\t                    this.$ = yy.prepareBlock($$[$0 - 3], $$[$0 - 2], $$[$0 - 1], $$[$0], false, this._$);\n
\t                    break;\n
\t                case 14:\n
\t                    this.$ = yy.prepareBlock($$[$0 - 3], $$[$0 - 2], $$[$0 - 1], $$[$0], true, this._$);\n
\t                    break;\n
\t                case 15:\n
\t                    this.$ = { open: $$[$0 - 5], path: $$[$0 - 4], params: $$[$0 - 3], hash: $$[$0 - 2], blockParams: $$[$0 - 1], strip: yy.stripFlags($$[$0 - 5], $$[$0]) };\n
\t                    break;\n
\t                case 16:\n
\t                    this.$ = { path: $$[$0 - 4], params: $$[$0 - 3], hash: $$[$0 - 2], blockParams: $$[$0 - 1], strip: yy.stripFlags($$[$0 - 5], $$[$0]) };\n
\t                    break;\n
\t                case 17:\n
\t                    this.$ = { path: $$[$0 - 4], params: $$[$0 - 3], hash: $$[$0 - 2], blockParams: $$[$0 - 1], strip: yy.stripFlags($$[$0 - 5], $$[$0]) };\n
\t                    break;\n
\t                case 18:\n
\t                    this.$ = { strip: yy.stripFlags($$[$0 - 1], $$[$0 - 1]), program: $$[$0] };\n
\t                    break;\n
\t                case 19:\n
\t                    var inverse = yy.prepareBlock($$[$0 - 2], $$[$0 - 1], $$[$0], $$[$0], false, this._$),\n
\t                        program = yy.prepareProgram([inverse], $$[$0 - 1].loc);\n
\t                    program.chained = true;\n
\n
\t                    this.$ = { strip: $$[$0 - 2].strip, program: program, chain: true };\n
\n
\t                    break;\n
\t                case 20:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 21:\n
\t                    this.$ = { path: $$[$0 - 1], strip: yy.stripFlags($$[$0 - 2], $$[$0]) };\n
\t                    break;\n
\t                case 22:\n
\t                    this.$ = yy.prepareMustache($$[$0 - 3], $$[$0 - 2], $$[$0 - 1], $$[$0 - 4], yy.stripFlags($$[$0 - 4], $$[$0]), this._$);\n
\t                    break;\n
\t                case 23:\n
\t                    this.$ = yy.prepareMustache($$[$0 - 3], $$[$0 - 2], $$[$0 - 1], $$[$0 - 4], yy.stripFlags($$[$0 - 4], $$[$0]), this._$);\n
\t                    break;\n
\t                case 24:\n
\t                    this.$ = {\n
\t                        type: \'PartialStatement\',\n
\t                        name: $$[$0 - 3],\n
\t                        params: $$[$0 - 2],\n
\t                        hash: $$[$0 - 1],\n
\t                        indent: \'\',\n
\t                        strip: yy.stripFlags($$[$0 - 4], $$[$0]),\n
\t                        loc: yy.locInfo(this._$)\n
\t                    };\n
\n
\t                    break;\n
\t                case 25:\n
\t                    this.$ = yy.preparePartialBlock($$[$0 - 2], $$[$0 - 1], $$[$0], this._$);\n
\t                    break;\n
\t                case 26:\n
\t                    this.$ = { path: $$[$0 - 3], params: $$[$0 - 2], hash: $$[$0 - 1], strip: yy.stripFlags($$[$0 - 4], $$[$0]) };\n
\t                    break;\n
\t                case 27:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 28:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 29:\n
\t                    this.$ = {\n
\t                        type: \'SubExpression\',\n
\t                        path: $$[$0 - 3],\n
\t                        params: $$[$0 - 2],\n
\t                        hash: $$[$0 - 1],\n
\t                        loc: yy.locInfo(this._$)\n
\t                    };\n
\n
\t                    break;\n
\t                case 30:\n
\t                    this.$ = { type: \'Hash\', pairs: $$[$0], loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 31:\n
\t                    this.$ = { type: \'HashPair\', key: yy.id($$[$0 - 2]), value: $$[$0], loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 32:\n
\t                    this.$ = yy.id($$[$0 - 1]);\n
\t                    break;\n
\t                case 33:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 34:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 35:\n
\t                    this.$ = { type: \'StringLiteral\', value: $$[$0], original: $$[$0], loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 36:\n
\t                    this.$ = { type: \'NumberLiteral\', value: Number($$[$0]), original: Number($$[$0]), loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 37:\n
\t                    this.$ = { type: \'BooleanLiteral\', value: $$[$0] === \'true\', original: $$[$0] === \'true\', loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 38:\n
\t                    this.$ = { type: \'UndefinedLiteral\', original: undefined, value: undefined, loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 39:\n
\t                    this.$ = { type: \'NullLiteral\', original: null, value: null, loc: yy.locInfo(this._$) };\n
\t                    break;\n
\t                case 40:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 41:\n
\t                    this.$ = $$[$0];\n
\t                    break;\n
\t                case 42:\n
\t                    this.$ = yy.preparePath(true, $$[$0], this._$);\n
\t                    break;\n
\t                case 43:\n
\t                    this.$ = yy.preparePath(false, $$[$0], this._$);\n
\t                    break;\n
\t                case 44:\n
\t                    $$[$0 - 2].push({ part: yy.id($$[$0]), original: $$[$0], separator: $$[$0 - 1] });this.$ = $$[$0 - 2];\n
\t                    break;\n
\t                case 45:\n
\t                    this.$ = [{ part: yy.id($$[$0]), original: $$[$0] }];\n
\t                    break;\n
\t                case 46:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 47:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 48:\n
\t                    this.$ = [$$[$0]];\n
\t                    break;\n
\t                case 49:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 50:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 51:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 58:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 59:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 64:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 65:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 70:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 71:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 78:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 79:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 82:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 83:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 86:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 87:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 90:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 91:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 94:\n
\t                    this.$ = [];\n
\t                    break;\n
\t                case 95:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 98:\n
\t                    this.$ = [$$[$0]];\n
\t                    break;\n
\t                case 99:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t                case 100:\n
\t                    this.$ = [$$[$0]];\n
\t                    break;\n
\t                case 101:\n
\t                    $$[$0 - 1].push($$[$0]);\n
\t                    break;\n
\t            }\n
\t        },\n
\t        table: [{ 3: 1, 4: 2, 5: [2, 46], 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 1: [3] }, { 5: [1, 4] }, { 5: [2, 2], 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11, 14: [1, 12], 15: [1, 20], 16: 17, 19: [1, 23], 24: 15, 27: 16, 29: [1, 21], 34: [1, 22], 39: [2, 2], 44: [2, 2], 47: [2, 2], 48: [1, 13], 51: [1, 14], 55: [1, 18], 59: 19, 60: [1, 24] }, { 1: [2, 1] }, { 5: [2, 47], 14: [2, 47], 15: [2, 47], 19: [2, 47], 29: [2, 47], 34: [2, 47], 39: [2, 47], 44: [2, 47], 47: [2, 47], 48: [2, 47], 51: [2, 47], 55: [2, 47], 60: [2, 47] }, { 5: [2, 3], 14: [2, 3], 15: [2, 3], 19: [2, 3], 29: [2, 3], 34: [2, 3], 39: [2, 3], 44: [2, 3], 47: [2, 3], 48: [2, 3], 51: [2, 3], 55: [2, 3], 60: [2, 3] }, { 5: [2, 4], 14: [2, 4], 15: [2, 4], 19: [2, 4], 29: [2, 4], 34: [2, 4], 39: [2, 4], 44: [2, 4], 47: [2, 4], 48: [2, 4], 51: [2, 4], 55: [2, 4], 60: [2, 4] }, { 5: [2, 5], 14: [2, 5], 15: [2, 5], 19: [2, 5], 29: [2, 5], 34: [2, 5], 39: [2, 5], 44: [2, 5], 47: [2, 5], 48: [2, 5], 51: [2, 5], 55: [2, 5], 60: [2, 5] }, { 5: [2, 6], 14: [2, 6], 15: [2, 6], 19: [2, 6], 29: [2, 6], 34: [2, 6], 39: [2, 6], 44: [2, 6], 47: [2, 6], 48: [2, 6], 51: [2, 6], 55: [2, 6], 60: [2, 6] }, { 5: [2, 7], 14: [2, 7], 15: [2, 7], 19: [2, 7], 29: [2, 7], 34: [2, 7], 39: [2, 7], 44: [2, 7], 47: [2, 7], 48: [2, 7], 51: [2, 7], 55: [2, 7], 60: [2, 7] }, { 5: [2, 8], 14: [2, 8], 15: [2, 8], 19: [2, 8], 29: [2, 8], 34: [2, 8], 39: [2, 8], 44: [2, 8], 47: [2, 8], 48: [2, 8], 51: [2, 8], 55: [2, 8], 60: [2, 8] }, { 5: [2, 9], 14: [2, 9], 15: [2, 9], 19: [2, 9], 29: [2, 9], 34: [2, 9], 39: [2, 9], 44: [2, 9], 47: [2, 9], 48: [2, 9], 51: [2, 9], 55: [2, 9], 60: [2, 9] }, { 20: 25, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 36, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 4: 37, 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 39: [2, 46], 44: [2, 46], 47: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 4: 38, 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 44: [2, 46], 47: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 13: 40, 15: [1, 20], 17: 39 }, { 20: 42, 56: 41, 64: 43, 65: [1, 44], 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 4: 45, 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 47: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 5: [2, 10], 14: [2, 10], 15: [2, 10], 18: [2, 10], 19: [2, 10], 29: [2, 10], 34: [2, 10], 39: [2, 10], 44: [2, 10], 47: [2, 10], 48: [2, 10], 51: [2, 10], 55: [2, 10], 60: [2, 10] }, { 20: 46, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 47, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 48, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 42, 56: 49, 64: 43, 65: [1, 44], 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 33: [2, 78], 49: 50, 65: [2, 78], 72: [2, 78], 80: [2, 78], 81: [2, 78], 82: [2, 78], 83: [2, 78], 84: [2, 78], 85: [2, 78] }, { 23: [2, 33], 33: [2, 33], 54: [2, 33], 65: [2, 33], 68: [2, 33], 72: [2, 33], 75: [2, 33], 80: [2, 33], 81: [2, 33], 82: [2, 33], 83: [2, 33], 84: [2, 33], 85: [2, 33] }, { 23: [2, 34], 33: [2, 34], 54: [2, 34], 65: [2, 34], 68: [2, 34], 72: [2, 34], 75: [2, 34], 80: [2, 34], 81: [2, 34], 82: [2, 34], 83: [2, 34], 84: [2, 34], 85: [2, 34] }, { 23: [2, 35], 33: [2, 35], 54: [2, 35], 65: [2, 35], 68: [2, 35], 72: [2, 35], 75: [2, 35], 80: [2, 35], 81: [2, 35], 82: [2, 35], 83: [2, 35], 84: [2, 35], 85: [2, 35] }, { 23: [2, 36], 33: [2, 36], 54: [2, 36], 65: [2, 36], 68: [2, 36], 72: [2, 36], 75: [2, 36], 80: [2, 36], 81: [2, 36], 82: [2, 36], 83: [2, 36], 84: [2, 36], 85: [2, 36] }, { 23: [2, 37], 33: [2, 37], 54: [2, 37], 65: [2, 37], 68: [2, 37], 72: [2, 37], 75: [2, 37], 80: [2, 37], 81: [2, 37], 82: [2, 37], 83: [2, 37], 84: [2, 37], 85: [2, 37] }, { 23: [2, 38], 33: [2, 38], 54: [2, 38], 65: [2, 38], 68: [2, 38], 72: [2, 38], 75: [2, 38], 80: [2, 38], 81: [2, 38], 82: [2, 38], 83: [2, 38], 84: [2, 38], 85: [2, 38] }, { 23: [2, 39], 33: [2, 39], 54: [2, 39], 65: [2, 39], 68: [2, 39], 72: [2, 39], 75: [2, 39], 80: [2, 39], 81: [2, 39], 82: [2, 39], 83: [2, 39], 84: [2, 39], 85: [2, 39] }, { 23: [2, 43], 33: [2, 43], 54: [2, 43], 65: [2, 43], 68: [2, 43], 72: [2, 43], 75: [2, 43], 80: [2, 43], 81: [2, 43], 82: [2, 43], 83: [2, 43], 84: [2, 43], 85: [2, 43], 87: [1, 51] }, { 72: [1, 35], 86: 52 }, { 23: [2, 45], 33: [2, 45], 54: [2, 45], 65: [2, 45], 68: [2, 45], 72: [2, 45], 75: [2, 45], 80: [2, 45], 81: [2, 45], 82: [2, 45], 83: [2, 45], 84: [2, 45], 85: [2, 45], 87: [2, 45] }, { 52: 53, 54: [2, 82], 65: [2, 82], 72: [2, 82], 80: [2, 82], 81: [2, 82], 82: [2, 82], 83: [2, 82], 84: [2, 82], 85: [2, 82] }, { 25: 54, 38: 56, 39: [1, 58], 43: 57, 44: [1, 59], 45: 55, 47: [2, 54] }, { 28: 60, 43: 61, 44: [1, 59], 47: [2, 56] }, { 13: 63, 15: [1, 20], 18: [1, 62] }, { 15: [2, 48], 18: [2, 48] }, { 33: [2, 86], 57: 64, 65: [2, 86], 72: [2, 86], 80: [2, 86], 81: [2, 86], 82: [2, 86], 83: [2, 86], 84: [2, 86], 85: [2, 86] }, { 33: [2, 40], 65: [2, 40], 72: [2, 40], 80: [2, 40], 81: [2, 40], 82: [2, 40], 83: [2, 40], 84: [2, 40], 85: [2, 40] }, { 33: [2, 41], 65: [2, 41], 72: [2, 41], 80: [2, 41], 81: [2, 41], 82: [2, 41], 83: [2, 41], 84: [2, 41], 85: [2, 41] }, { 20: 65, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 26: 66, 47: [1, 67] }, { 30: 68, 33: [2, 58], 65: [2, 58], 72: [2, 58], 75: [2, 58], 80: [2, 58], 81: [2, 58], 82: [2, 58], 83: [2, 58], 84: [2, 58], 85: [2, 58] }, { 33: [2, 64], 35: 69, 65: [2, 64], 72: [2, 64], 75: [2, 64], 80: [2, 64], 81: [2, 64], 82: [2, 64], 83: [2, 64], 84: [2, 64], 85: [2, 64] }, { 21: 70, 23: [2, 50], 65: [2, 50], 72: [2, 50], 80: [2, 50], 81: [2, 50], 82: [2, 50], 83: [2, 50], 84: [2, 50], 85: [2, 50] }, { 33: [2, 90], 61: 71, 65: [2, 90], 72: [2, 90], 80: [2, 90], 81: [2, 90], 82: [2, 90], 83: [2, 90], 84: [2, 90], 85: [2, 90] }, { 20: 75, 33: [2, 80], 50: 72, 63: 73, 64: 76, 65: [1, 44], 69: 74, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 72: [1, 80] }, { 23: [2, 42], 33: [2, 42], 54: [2, 42], 65: [2, 42], 68: [2, 42], 72: [2, 42], 75: [2, 42], 80: [2, 42], 81: [2, 42], 82: [2, 42], 83: [2, 42], 84: [2, 42], 85: [2, 42], 87: [1, 51] }, { 20: 75, 53: 81, 54: [2, 84], 63: 82, 64: 76, 65: [1, 44], 69: 83, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 26: 84, 47: [1, 67] }, { 47: [2, 55] }, { 4: 85, 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 39: [2, 46], 44: [2, 46], 47: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 47: [2, 20] }, { 20: 86, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 4: 87, 6: 3, 14: [2, 46], 15: [2, 46], 19: [2, 46], 29: [2, 46], 34: [2, 46], 47: [2, 46], 48: [2, 46], 51: [2, 46], 55: [2, 46], 60: [2, 46] }, { 26: 88, 47: [1, 67] }, { 47: [2, 57] }, { 5: [2, 11], 14: [2, 11], 15: [2, 11], 19: [2, 11], 29: [2, 11], 34: [2, 11], 39: [2, 11], 44: [2, 11], 47: [2, 11], 48: [2, 11], 51: [2, 11], 55: [2, 11], 60: [2, 11] }, { 15: [2, 49], 18: [2, 49] }, { 20: 75, 33: [2, 88], 58: 89, 63: 90, 64: 76, 65: [1, 44], 69: 91, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 65: [2, 94], 66: 92, 68: [2, 94], 72: [2, 94], 80: [2, 94], 81: [2, 94], 82: [2, 94], 83: [2, 94], 84: [2, 94], 85: [2, 94] }, { 5: [2, 25], 14: [2, 25], 15: [2, 25], 19: [2, 25], 29: [2, 25], 34: [2, 25], 39: [2, 25], 44: [2, 25], 47: [2, 25], 48: [2, 25], 51: [2, 25], 55: [2, 25], 60: [2, 25] }, { 20: 93, 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 75, 31: 94, 33: [2, 60], 63: 95, 64: 76, 65: [1, 44], 69: 96, 70: 77, 71: 78, 72: [1, 79], 75: [2, 60], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 75, 33: [2, 66], 36: 97, 63: 98, 64: 76, 65: [1, 44], 69: 99, 70: 77, 71: 78, 72: [1, 79], 75: [2, 66], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 75, 22: 100, 23: [2, 52], 63: 101, 64: 76, 65: [1, 44], 69: 102, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 20: 75, 33: [2, 92], 62: 103, 63: 104, 64: 76, 65: [1, 44], 69: 105, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 33: [1, 106] }, { 33: [2, 79], 65: [2, 79], 72: [2, 79], 80: [2, 79], 81: [2, 79], 82: [2, 79], 83: [2, 79], 84: [2, 79], 85: [2, 79] }, { 33: [2, 81] }, { 23: [2, 27], 33: [2, 27], 54: [2, 27], 65: [2, 27], 68: [2, 27], 72: [2, 27], 75: [2, 27], 80: [2, 27], 81: [2, 27], 82: [2, 27], 83: [2, 27], 84: [2, 27], 85: [2, 27] }, { 23: [2, 28], 33: [2, 28], 54: [2, 28], 65: [2, 28], 68: [2, 28], 72: [2, 28], 75: [2, 28], 80: [2, 28], 81: [2, 28], 82: [2, 28], 83: [2, 28], 84: [2, 28], 85: [2, 28] }, { 23: [2, 30], 33: [2, 30], 54: [2, 30], 68: [2, 30], 71: 107, 72: [1, 108], 75: [2, 30] }, { 23: [2, 98], 33: [2, 98], 54: [2, 98], 68: [2, 98], 72: [2, 98], 75: [2, 98] }, { 23: [2, 45], 33: [2, 45], 54: [2, 45], 65: [2, 45], 68: [2, 45], 72: [2, 45], 73: [1, 109], 75: [2, 45], 80: [2, 45], 81: [2, 45], 82: [2, 45], 83: [2, 45], 84: [2, 45], 85: [2, 45], 87: [2, 45] }, { 23: [2, 44], 33: [2, 44], 54: [2, 44], 65: [2, 44], 68: [2, 44], 72: [2, 44], 75: [2, 44], 80: [2, 44], 81: [2, 44], 82: [2, 44], 83: [2, 44], 84: [2, 44], 85: [2, 44], 87: [2, 44] }, { 54: [1, 110] }, { 54: [2, 83], 65: [2, 83], 72: [2, 83], 80: [2, 83], 81: [2, 83], 82: [2, 83], 83: [2, 83], 84: [2, 83], 85: [2, 83] }, { 54: [2, 85] }, { 5: [2, 13], 14: [2, 13], 15: [2, 13], 19: [2, 13], 29: [2, 13], 34: [2, 13], 39: [2, 13], 44: [2, 13], 47: [2, 13], 48: [2, 13], 51: [2, 13], 55: [2, 13], 60: [2, 13] }, { 38: 56, 39: [1, 58], 43: 57, 44: [1, 59], 45: 112, 46: 111, 47: [2, 76] }, { 33: [2, 70], 40: 113, 65: [2, 70], 72: [2, 70], 75: [2, 70], 80: [2, 70], 81: [2, 70], 82: [2, 70], 83: [2, 70], 84: [2, 70], 85: [2, 70] }, { 47: [2, 18] }, { 5: [2, 14], 14: [2, 14], 15: [2, 14], 19: [2, 14], 29: [2, 14], 34: [2, 14], 39: [2, 14], 44: [2, 14], 47: [2, 14], 48: [2, 14], 51: [2, 14], 55: [2, 14], 60: [2, 14] }, { 33: [1, 114] }, { 33: [2, 87], 65: [2, 87], 72: [2, 87], 80: [2, 87], 81: [2, 87], 82: [2, 87], 83: [2, 87], 84: [2, 87], 85: [2, 87] }, { 33: [2, 89] }, { 20: 75, 63: 116, 64: 76, 65: [1, 44], 67: 115, 68: [2, 96], 69: 117, 70: 77, 71: 78, 72: [1, 79], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 33: [1, 118] }, { 32: 119, 33: [2, 62], 74: 120, 75: [1, 121] }, { 33: [2, 59], 65: [2, 59], 72: [2, 59], 75: [2, 59], 80: [2, 59], 81: [2, 59], 82: [2, 59], 83: [2, 59], 84: [2, 59], 85: [2, 59] }, { 33: [2, 61], 75: [2, 61] }, { 33: [2, 68], 37: 122, 74: 123, 75: [1, 121] }, { 33: [2, 65], 65: [2, 65], 72: [2, 65], 75: [2, 65], 80: [2, 65], 81: [2, 65], 82: [2, 65], 83: [2, 65], 84: [2, 65], 85: [2, 65] }, { 33: [2, 67], 75: [2, 67] }, { 23: [1, 124] }, { 23: [2, 51], 65: [2, 51], 72: [2, 51], 80: [2, 51], 81: [2, 51], 82: [2, 51], 83: [2, 51], 84: [2, 51], 85: [2, 51] }, { 23: [2, 53] }, { 33: [1, 125] }, { 33: [2, 91], 65: [2, 91], 72: [2, 91], 80: [2, 91], 81: [2, 91], 82: [2, 91], 83: [2, 91], 84: [2, 91], 85: [2, 91] }, { 33: [2, 93] }, { 5: [2, 22], 14: [2, 22], 15: [2, 22], 19: [2, 22], 29: [2, 22], 34: [2, 22], 39: [2, 22], 44: [2, 22], 47: [2, 22], 48: [2, 22], 51: [2, 22], 55: [2, 22], 60: [2, 22] }, { 23: [2, 99], 33: [2, 99], 54: [2, 99], 68: [2, 99], 72: [2, 99], 75: [2, 99] }, { 73: [1, 109] }, { 20: 75, 63: 126, 64: 76, 65: [1, 44], 72: [1, 35], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 5: [2, 23], 14: [2, 23], 15: [2, 23], 19: [2, 23], 29: [2, 23], 34: [2, 23], 39: [2, 23], 44: [2, 23], 47: [2, 23], 48: [2, 23], 51: [2, 23], 55: [2, 23], 60: [2, 23] }, { 47: [2, 19] }, { 47: [2, 77] }, { 20: 75, 33: [2, 72], 41: 127, 63: 128, 64: 76, 65: [1, 44], 69: 129, 70: 77, 71: 78, 72: [1, 79], 75: [2, 72], 78: 26, 79: 27, 80: [1, 28], 81: [1, 29], 82: [1, 30], 83: [1, 31], 84: [1, 32], 85: [1, 34], 86: 33 }, { 5: [2, 24], 14: [2, 24], 15: [2, 24], 19: [2, 24], 29: [2, 24], 34: [2, 24], 39: [2, 24], 44: [2, 24], 47: [2, 24], 48: [2, 24], 51: [2, 24], 55: [2, 24], 60: [2, 24] }, { 68: [1, 130] }, { 65: [2, 95], 68: [2, 95], 72: [2, 95], 80: [2, 95], 81: [2, 95], 82: [2, 95], 83: [2, 95], 84: [2, 95], 85: [2, 95] }, { 68: [2, 97] }, { 5: [2, 21], 14: [2, 21], 15: [2, 21], 19: [2, 21], 29: [2, 21], 34: [2, 21], 39: [2, 21], 44: [2, 21], 47: [2, 21], 48: [2, 21], 51: [2, 21], 55: [2, 21], 60: [2, 21] }, { 33: [1, 131] }, { 33: [2, 63] }, { 72: [1, 133], 76: 132 }, { 33: [1, 134] }, { 33: [2, 69] }, { 15: [2, 12] }, { 14: [2, 26], 15: [2, 26], 19: [2, 26], 29: [2, 26], 34: [2, 26], 47: [2, 26], 48: [2, 26], 51: [2, 26], 55: [2, 26], 60: [2, 26] }, { 23: [2, 31], 33: [2, 31], 54: [2, 31], 68: [2, 31], 72: [2, 31], 75: [2, 31] }, { 33: [2, 74], 42: 135, 74: 136, 75: [1, 121] }, { 33: [2, 71], 65: [2, 71], 72: [2, 71], 75: [2, 71], 80: [2, 71], 81: [2, 71], 82: [2, 71], 83: [2, 71], 84: [2, 71], 85: [2, 71] }, { 33: [2, 73], 75: [2, 73] }, { 23: [2, 29], 33: [2, 29], 54: [2, 29], 65: [2, 29], 68: [2, 29], 72: [2, 29], 75: [2, 29], 80: [2, 29], 81: [2, 29], 82: [2, 29], 83: [2, 29], 84: [2, 29], 85: [2, 29] }, { 14: [2, 15], 15: [2, 15], 19: [2, 15], 29: [2, 15], 34: [2, 15], 39: [2, 15], 44: [2, 15], 47: [2, 15], 48: [2, 15], 51: [2, 15], 55: [2, 15], 60: [2, 15] }, { 72: [1, 138], 77: [1, 137] }, { 72: [2, 100], 77: [2, 100] }, { 14: [2, 16], 15: [2, 16], 19: [2, 16], 29: [2, 16], 34: [2, 16], 44: [2, 16], 47: [2, 16], 48: [2, 16], 51: [2, 16], 55: [2, 16], 60: [2, 16] }, { 33: [1, 139] }, { 33: [2, 75] }, { 33: [2, 32] }, { 72: [2, 101], 77: [2, 101] }, { 14: [2, 17], 15: [2, 17], 19: [2, 17], 29: [2, 17], 34: [2, 17], 39: [2, 17], 44: [2, 17], 47: [2, 17], 48: [2, 17], 51: [2, 17], 55: [2, 17], 60: [2, 17] }],\n
\t        defaultActions: { 4: [2, 1], 55: [2, 55], 57: [2, 20], 61: [2, 57], 74: [2, 81], 83: [2, 85], 87: [2, 18], 91: [2, 89], 102: [2, 53], 105: [2, 93], 111: [2, 19], 112: [2, 77], 117: [2, 97], 120: [2, 63], 123: [2, 69], 124: [2, 12], 136: [2, 75], 137: [2, 32] },\n
\t        parseError: function parseError(str, hash) {\n
\t            throw new Error(str);\n
\t        },\n
\t        parse: function parse(input) {\n
\t            var self = this,\n
\t                stack = [0],\n
\t                vstack = [null],\n
\t                lstack = [],\n
\t                table = this.table,\n
\t                yytext = "",\n
\t                yylineno = 0,\n
\t                yyleng = 0,\n
\t                recovering = 0,\n
\t                TERROR = 2,\n
\t                EOF = 1;\n
\t            this.lexer.setInput(input);\n
\t            this.lexer.yy = this.yy;\n
\t            this.yy.lexer = this.lexer;\n
\t            this.yy.parser = this;\n
\t            if (typeof this.lexer.yylloc == "undefined") this.lexer.yylloc = {};\n
\t            var yyloc = this.lexer.yylloc;\n
\t            lstack.push(yyloc);\n
\t            var ranges = this.lexer.options && this.lexer.options.ranges;\n
\t            if (typeof this.yy.parseError === "function") this.parseError = this.yy.parseError;\n
\t            function popStack(n) {\n
\t                stack.length = stack.length - 2 * n;\n
\t                vstack.length = vstack.length - n;\n
\t                lstack.length = lstack.length - n;\n
\t            }\n
\t            function lex() {\n
\t                var token;\n
\t                token = self.lexer.lex() || 1;\n
\t                if (typeof token !== "number") {\n
\t                    token = self.symbols_[token] || token;\n
\t                }\n
\t                return token;\n
\t            }\n
\t            var symbol,\n
\t                preErrorSymbol,\n
\t                state,\n
\t                action,\n
\t                a,\n
\t                r,\n
\t                yyval = {},\n
\t                p,\n
\t                len,\n
\t                newState,\n
\t                expected;\n
\t            while (true) {\n
\t                state = stack[stack.length - 1];\n
\t                if (this.defaultActions[state]) {\n
\t                    action = this.defaultActions[state];\n
\t                } else {\n
\t                    if (symbol === null || typeof symbol == "undefined") {\n
\t                        symbol = lex();\n
\t                    }\n
\t                    action = table[state] && table[state][symbol];\n
\t                }\n
\t                if (typeof action === "undefined" || !action.length || !action[0]) {\n
\t                    var errStr = "";\n
\t                    if (!recovering) {\n
\t                        expected = [];\n
\t                        for (p in table[state]) if (this.terminals_[p] && p > 2) {\n
\t                            expected.push("\'" + this.terminals_[p] + "\'");\n
\t                        }\n
\t                        if (this.lexer.showPosition) {\n
\t                            errStr = "Parse error on line " + (yylineno + 1) + ":\\n" + this.lexer.showPosition() + "\\nExpecting " + expected.join(", ") + ", got \'" + (this.terminals_[symbol] || symbol) + "\'";\n
\t                        } else {\n
\t                            errStr = "Parse error on line " + (yylineno + 1) + ": Unexpected " + (symbol == 1 ? "end of input" : "\'" + (this.terminals_[symbol] || symbol) + "\'");\n
\t                        }\n
\t                        this.parseError(errStr, { text: this.lexer.match, token: this.terminals_[symbol] || symbol, line: this.lexer.yylineno, loc: yyloc, expected: expected });\n
\t                    }\n
\t                }\n
\t                if (action[0] instanceof Array && action.length > 1) {\n
\t                    throw new Error("Parse Error: multiple actions possible at state: " + state + ", token: " + symbol);\n
\t                }\n
\t                switch (action[0]) {\n
\t                    case 1:\n
\t                        stack.push(symbol);\n
\t                        vstack.push(this.lexer.yytext);\n
\t                        lstack.push(this.lexer.yylloc);\n
\t                        stack.push(action[1]);\n
\t                        symbol = null;\n
\t                        if (!preErrorSymbol) {\n
\t                            yyleng = this.lexer.yyleng;\n
\t                            yytext = this.lexer.yytext;\n
\t                            yylineno = this.lexer.yylineno;\n
\t                            yyloc = this.lexer.yylloc;\n
\t                            if (recovering > 0) recovering--;\n
\t                        } else {\n
\t                            symbol = preErrorSymbol;\n
\t                            preErrorSymbol = null;\n
\t                        }\n
\t                        break;\n
\t                    case 2:\n
\t                        len = this.productions_[action[1]][1];\n
\t                        yyval.$ = vstack[vstack.length - len];\n
\t                        yyval._$ = { first_line: lstack[lstack.length - (len || 1)].first_line, last_line: lstack[lstack.length - 1].last_line, first_column: lstack[lstack.length - (len || 1)].first_column, last_column: lstack[lstack.length - 1].last_column };\n
\t                        if (ranges) {\n
\t                            yyval._$.range = [lstack[lstack.length - (len || 1)].range[0], lstack[lstack.length - 1].range[1]];\n
\t                        }\n
\t                        r = this.performAction.call(yyval, yytext, yyleng, yylineno, this.yy, action[1], vstack, lstack);\n
\t                        if (typeof r !== "undefined") {\n
\t                            return r;\n
\t                        }\n
\t                        if (len) {\n
\t                            stack = stack.slice(0, -1 * len * 2);\n
\t                            vstack = vstack.slice(0, -1 * len);\n
\t                            lstack = lstack.slice(0, -1 * len);\n
\t                        }\n
\t                        stack.push(this.productions_[action[1]][0]);\n
\t                        vstack.push(yyval.$);\n
\t                        lstack.push(yyval._$);\n
\t                        newState = table[stack[stack.length - 2]][stack[stack.length - 1]];\n
\t                        stack.push(newState);\n
\t                        break;\n
\t                    case 3:\n
\t                        return true;\n
\t                }\n
\t            }\n
\t            return true;\n
\t        }\n
\t    };\n
\t    /* Jison generated lexer */\n
\t    var lexer = (function () {\n
\t        var lexer = { EOF: 1,\n
\t            parseError: function parseError(str, hash) {\n
\t                if (this.yy.parser) {\n
\t                    this.yy.parser.parseError(str, hash);\n
\t                } else {\n
\t                    throw new Error(str);\n
\t                }\n
\t            },\n
\t            setInput: function setInput(input) {\n
\t                this._input = input;\n
\t                this._more = this._less = this.done = false;\n
\t                this.yylineno = this.yyleng = 0;\n
\t                this.yytext = this.matched = this.match = \'\';\n
\t                this.conditionStack = [\'INITIAL\'];\n
\t                this.yylloc = { first_line: 1, first_column: 0, last_line: 1, last_column: 0 };\n
\t                if (this.options.ranges) this.yylloc.range = [0, 0];\n
\t                this.offset = 0;\n
\t                return this;\n
\t            },\n
\t            input: function input() {\n
\t                var ch = this._input[0];\n
\t                this.yytext += ch;\n
\t                this.yyleng++;\n
\t                this.offset++;\n
\t                this.match += ch;\n
\t                this.matched += ch;\n
\t                var lines = ch.match(/(?:\\r\\n?|\\n).*/g);\n
\t                if (lines) {\n
\t                    this.yylineno++;\n
\t                    this.yylloc.last_line++;\n
\t                } else {\n
\t                    this.yylloc.last_column++;\n
\t                }\n
\t                if (this.options.ranges) this.yylloc.range[1]++;\n
\n
\t                this._input = this._input.slice(1);\n
\t                return ch;\n
\t            },\n
\t            unput: function unput(ch) {\n
\t                var len = ch.length;\n
\t                var lines = ch.split(/(?:\\r\\n?|\\n)/g);\n
\n
\t                this._input = ch + this._input;\n
\t                this.yytext = this.yytext.substr(0, this.yytext.length - len - 1);\n
\t                //this.yyleng -= len;\n
\t                this.offset -= len;\n
\t                var oldLines = this.match.split(/(?:\\r\\n?|\\n)/g);\n
\t                this.match = this.match.substr(0, this.match.length - 1);\n
\t                this.matched = this.matched.substr(0, this.matched.length - 1);\n
\n
\t                if (lines.length - 1) this.yylineno -= lines.length - 1;\n
\t                var r = this.yylloc.range;\n
\n
\t                this.yylloc = { first_line: this.yylloc.first_line,\n
\t                    last_line: this.yylineno + 1,\n
\t                    first_column: this.yylloc.first_column,\n
\t                    last_column: lines ? (lines.length === oldLines.length ? this.yylloc.first_column : 0) + oldLines[oldLines.length - lines.length].length - lines[0].length : this.yylloc.first_column - len\n
\t                };\n
\n
\t                if (this.options.ranges) {\n
\t                    this.yylloc.range = [r[0], r[0] + this.yyleng - len];\n
\t                }\n
\t                return this;\n
\t            },\n
\t            more: function more() {\n
\t                this._more = true;\n
\t                return this;\n
\t            },\n
\t            less: function less(n) {\n
\t                this.unput(this.match.slice(n));\n
\t            },\n
\t            pastInput: function pastInput() {\n
\t                var past = this.matched.substr(0, this.matched.length - this.match.length);\n
\t                return (past.length > 20 ? \'...\' : \'\') + past.substr(-20).replace(/\\n/g, "");\n
\t            },\n
\t            upcomingInput: function upcomingInput() {\n
\t                var next = this.match;\n
\t                if (next.length < 20) {\n
\t                    next += this._input.substr(0, 20 - next.length);\n
\t                }\n
\t                return (next.substr(0, 20) + (next.length > 20 ? \'...\' : \'\')).replace(/\\n/g, "");\n
\t            },\n
\t            showPosition: function showPosition() {\n
\t                var pre = this.pastInput();\n
\t                var c = new Array(pre.length + 1).join("-");\n
\t                return pre + this.upcomingInput() + "\\n" + c + "^";\n
\t            },\n
\t            next: function next() {\n
\t                if (this.done) {\n
\t                    return this.EOF;\n
\t                }\n
\t                if (!this._input) this.done = true;\n
\n
\t                var token, match, tempMatch, index, col, lines;\n
\t                if (!this._more) {\n
\t                    this.yytext = \'\';\n
\t                    this.match = \'\';\n
\t                }\n
\t                var rules = this._currentRules();\n
\t                for (var i = 0; i < rules.length; i++) {\n
\t                    tempMatch = this._input.match(this.rules[rules[i]]);\n
\t                    if (tempMatch && (!match || tempMatch[0].length > match[0].length)) {\n
\t                        match = tempMatch;\n
\t                        index = i;\n
\t                        if (!this.options.flex) break;\n
\t                    }\n
\t                }\n
\t                if (match) {\n
\t                    lines = match[0].match(/(?:\\r\\n?|\\n).*/g);\n
\t                    if (lines) this.yylineno += lines.length;\n
\t                    this.yylloc = { first_line: this.yylloc.last_line,\n
\t                        last_line: this.yylineno + 1,\n
\t                        first_column: this.yylloc.last_column,\n
\t                        last_column: lines ? lines[lines.length - 1].length - lines[lines.length - 1].match(/\\r?\\n?/)[0].length : this.yylloc.last_column + match[0].length };\n
\t                    this.yytext += match[0];\n
\t                    this.match += match[0];\n
\t                    this.matches = match;\n
\t                    this.yyleng = this.yytext.length;\n
\t                    if (this.options.ranges) {\n
\t                        this.yylloc.range = [this.offset, this.offset += this.yyleng];\n
\t                    }\n
\t                    this._more = false;\n
\t                    this._input = this._input.slice(match[0].length);\n
\t                    this.matched += match[0];\n
\t                    token = this.performAction.call(this, this.yy, this, rules[index], this.conditionStack[this.conditionStack.length - 1]);\n
\t                    if (this.done && this._input) this.done = false;\n
\t                    if (token) return token;else return;\n
\t                }\n
\t                if (this._input === "") {\n
\t                    return this.EOF;\n
\t                } else {\n
\t                    return this.parseError(\'Lexical error on line \' + (this.yylineno + 1) + \'. Unrecognized text.\\n\' + this.showPosition(), { text: "", token: null, line: this.yylineno });\n
\t                }\n
\t            },\n
\t            lex: function lex() {\n
\t                var r = this.next();\n
\t                if (typeof r !== \'undefined\') {\n
\t                    return r;\n
\t                } else {\n
\t                    return this.lex();\n
\t                }\n
\t            },\n
\t            begin: function begin(condition) {\n
\t                this.conditionStack.push(condition);\n
\t            },\n
\t            popState: function popState() {\n
\t                return this.conditionStack.pop();\n
\t            },\n
\t            _currentRules: function _currentRules() {\n
\t                return this.conditions[this.conditionStack[this.conditionStack.length - 1]].rules;\n
\t            },\n
\t            topState: function topState() {\n
\t                return this.conditionStack[this.conditionStack.length - 2];\n
\t            },\n
\t            pushState: function begin(condition) {\n
\t                this.begin(condition);\n
\t            } };\n
\t        lexer.options = {};\n
\t        lexer.performAction = function anonymous(yy, yy_, $avoiding_name_collisions, YY_START\n
\t        /**/) {\n
\n
\t            function strip(start, end) {\n
\t                return yy_.yytext = yy_.yytext.substr(start, yy_.yyleng - end);\n
\t            }\n
\n
\t            var YYSTATE = YY_START;\n
\t            switch ($avoiding_name_collisions) {\n
\t                case 0:\n
\t                    if (yy_.yytext.slice(-2) === "\\\\\\\\") {\n
\t                        strip(0, 1);\n
\t                        this.begin("mu");\n
\t                    } else if (yy_.yytext.slice(-1) === "\\\\") {\n
\t                        strip(0, 1);\n
\t                        this.begin("emu");\n
\t                    } else {\n
\t                        this.begin("mu");\n
\t                    }\n
\t                    if (yy_.yytext) return 15;\n
\n
\t                    break;\n
\t                case 1:\n
\t                    return 15;\n
\t                    break;\n
\t                case 2:\n
\t                    this.popState();\n
\t                    return 15;\n
\n
\t                    break;\n
\t                case 3:\n
\t                    this.begin(\'raw\');return 15;\n
\t                    break;\n
\t                case 4:\n
\t                    this.popState();\n
\t                    // Should be using `this.topState()` below, but it currently\n
\t                    // returns the second top instead of the first top. Opened an\n
\t                    // issue about it at https://github.com/zaach/jison/issues/291\n
\t                    if (this.conditionStack[this.conditionStack.length - 1] === \'raw\') {\n
\t                        return 15;\n
\t                    } else {\n
\t                        yy_.yytext = yy_.yytext.substr(5, yy_.yyleng - 9);\n
\t                        return \'END_RAW_BLOCK\';\n
\t                    }\n
\n
\t                    break;\n
\t                case 5:\n
\t                    return 15;\n
\t                    break;\n
\t                case 6:\n
\t                    this.popState();\n
\t                    return 14;\n
\n
\t                    break;\n
\t                case 7:\n
\t                    return 65;\n
\t                    break;\n
\t                case 8:\n
\t                    return 68;\n
\t                    break;\n
\t                case 9:\n
\t                    return 19;\n
\t                    break;\n
\t                case 10:\n
\t                    this.popState();\n
\t                    this.begin(\'raw\');\n
\t                    return 23;\n
\n
\t                    break;\n
\t                case 11:\n
\t                    return 55;\n
\t                    break;\n
\t                case 12:\n
\t                    return 60;\n
\t                    break;\n
\t                case 13:\n
\t                    return 29;\n
\t                    break;\n
\t                case 14:\n
\t                    return 47;\n
\t                    break;\n
\t                case 15:\n
\t                    this.popState();return 44;\n
\t                    break;\n
\t                case 16:\n
\t                    this.popState();return 44;\n
\t                    break;\n
\t                case 17:\n
\t                    return 34;\n
\t                    break;\n
\t                case 18:\n
\t                    return 39;\n
\t                    break;\n
\t                case 19:\n
\t                    return 51;\n
\t                    break;\n
\t                case 20:\n
\t                    return 48;\n
\t                    break;\n
\t                case 21:\n
\t                    this.unput(yy_.yytext);\n
\t                    this.popState();\n
\t                    this.begin(\'com\');\n
\n
\t                    break;\n
\t                case 22:\n
\t                    this.popState();\n
\t                    return 14;\n
\n
\t                    break;\n
\t                case 23:\n
\t                    return 48;\n
\t                    break;\n
\t                case 24:\n
\t                    return 73;\n
\t                    break;\n
\t                case 25:\n
\t                    return 72;\n
\t                    break;\n
\t                case 26:\n
\t                    return 72;\n
\t                    break;\n
\t                case 27:\n
\t                    return 87;\n
\t                    break;\n
\t                case 28:\n
\t                    // ignore whitespace\n
\t                    break;\n
\t                case 29:\n
\t                    this.popState();return 54;\n
\t                    break;\n
\t                case 30:\n
\t                    this.popState();return 33;\n
\t                    break;\n
\t                case 31:\n
\t                    yy_.yytext = strip(1, 2).replace(/\\\\"/g, \'"\');return 80;\n
\t                    break;\n
\t                case 32:\n
\t                    yy_.yytext = strip(1, 2).replace(/\\\\\'/g, "\'");return 80;\n
\t                    break;\n
\t                case 33:\n
\t                    return 85;\n
\t                    break;\n
\t                case 34:\n
\t                    return 82;\n
\t                    break;\n
\t                case 35:\n
\t                    return 82;\n
\t                    break;\n
\t                case 36:\n
\t                    return 83;\n
\t                    break;\n
\t                case 37:\n
\t                    return 84;\n
\t                    break;\n
\t                case 38:\n
\t                    return 81;\n
\t                    break;\n
\t                case 39:\n
\t                    return 75;\n
\t                    break;\n
\t                case 40:\n
\t                    return 77;\n
\t                    break;\n
\t                case 41:\n
\t                    return 72;\n
\t                    break;\n
\t                case 42:\n
\t                    yy_.yytext = yy_.yytext.replace(/\\\\([\\\\\\]])/g, \'$1\');return 72;\n
\t                    break;\n
\t                case 43:\n
\t                    return \'INVALID\';\n
\t                    break;\n
\t                case 44:\n
\t                    return 5;\n
\t                    break;\n
\t            }\n
\t        };\n
\t        lexer.rules = [/^(?:[^\\x00]*?(?=(\\{\\{)))/, /^(?:[^\\x00]+)/, /^(?:[^\\x00]{2,}?(?=(\\{\\{|\\\\\\{\\{|\\\\\\\\\\{\\{|$)))/, /^(?:\\{\\{\\{\\{(?=[^/]))/, /^(?:\\{\\{\\{\\{\\/[^\\s!"#%-,\\.\\/;->@\\[-\\^`\\{-~]+(?=[=}\\s\\/.])\\}\\}\\}\\})/, /^(?:[^\\x00]*?(?=(\\{\\{\\{\\{)))/, /^(?:[\\s\\S]*?--(~)?\\}\\})/, /^(?:\\()/, /^(?:\\))/, /^(?:\\{\\{\\{\\{)/, /^(?:\\}\\}\\}\\})/, /^(?:\\{\\{(~)?>)/, /^(?:\\{\\{(~)?#>)/, /^(?:\\{\\{(~)?#\\*?)/, /^(?:\\{\\{(~)?\\/)/, /^(?:\\{\\{(~)?\\^\\s*(~)?\\}\\})/, /^(?:\\{\\{(~)?\\s*else\\s*(~)?\\}\\})/, /^(?:\\{\\{(~)?\\^)/, /^(?:\\{\\{(~)?\\s*else\\b)/, /^(?:\\{\\{(~)?\\{)/, /^(?:\\{\\{(~)?&)/, /^(?:\\{\\{(~)?!--)/, /^(?:\\{\\{(~)?![\\s\\S]*?\\}\\})/, /^(?:\\{\\{(~)?\\*?)/, /^(?:=)/, /^(?:\\.\\.)/, /^(?:\\.(?=([=~}\\s\\/.)|])))/, /^(?:[\\/.])/, /^(?:\\s+)/, /^(?:\\}(~)?\\}\\})/, /^(?:(~)?\\}\\})/, /^(?:"(\\\\["]|[^"])*")/, /^(?:\'(\\\\[\']|[^\'])*\')/, /^(?:@)/, /^(?:true(?=([~}\\s)])))/, /^(?:false(?=([~}\\s)])))/, /^(?:undefined(?=([~}\\s)])))/, /^(?:null(?=([~}\\s)])))/, /^(?:-?[0-9]+(?:\\.[0-9]+)?(?=([~}\\s)])))/, /^(?:as\\s+\\|)/, /^(?:\\|)/, /^(?:([^\\s!"#%-,\\.\\/;->@\\[-\\^`\\{-~]+(?=([=~}\\s\\/.)|]))))/, /^(?:\\[(\\\\\\]|[^\\]])*\\])/, /^(?:.)/, /^(?:$)/];\n
\t        lexer.conditions = { "mu": { "rules": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44], "inclusive": false }, "emu": { "rules": [2], "inclusive": false }, "com": { "rules": [6], "inclusive": false }, "raw": { "rules": [3, 4, 5], "inclusive": false }, "INITIAL": { "rules": [0, 1, 44], "inclusive": true } };\n
\t        return lexer;\n
\t    })();\n
\t    parser.lexer = lexer;\n
\t    function Parser() {\n
\t        this.yy = {};\n
\t    }Parser.prototype = parser;parser.Parser = Parser;\n
\t    return new Parser();\n
\t})();exports.__esModule = true;\n
\texports[\'default\'] = handlebars;\n
\n
/***/ },\n
/* 24 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _visitor = __webpack_require__(25);\n
\n
\tvar _visitor2 = _interopRequireDefault(_visitor);\n
\n
\tfunction WhitespaceControl() {\n
\t  var options = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];\n
\n
\t  this.options = options;\n
\t}\n
\tWhitespaceControl.prototype = new _visitor2[\'default\']();\n
\n
\tWhitespaceControl.prototype.Program = function (program) {\n
\t  var doStandalone = !this.options.ignoreStandalone;\n
\n
\t  var isRoot = !this.isRootSeen;\n
\t  this.isRootSeen = true;\n
\n
\t  var body = program.body;\n
\t  for (var i = 0, l = body.length; i < l; i++) {\n
\t    var current = body[i],\n
\t        strip = this.accept(current);\n
\n
\t    if (!strip) {\n
\t      continue;\n
\t    }\n
\n
\t    var _isPrevWhitespace = isPrevWhitespace(body, i, isRoot),\n
\t        _isNextWhitespace = isNextWhitespace(body, i, isRoot),\n
\t        openStandalone = strip.openStandalone && _isPrevWhitespace,\n
\t        closeStandalone = strip.closeStandalone && _isNextWhitespace,\n
\t        inlineStandalone = strip.inlineStandalone && _isPrevWhitespace && _isNextWhitespace;\n
\n
\t    if (strip.close) {\n
\t      omitRight(body, i, true);\n
\t    }\n
\t    if (strip.open) {\n
\t      omitLeft(body, i, true);\n
\t    }\n
\n
\t    if (doStandalone && inlineStandalone) {\n
\t      omitRight(body, i);\n
\n
\t      if (omitLeft(body, i)) {\n
\t        // If we are on a standalone node, save the indent info for partials\n
\t        if (current.type === \'PartialStatement\') {\n
\t          // Pull out the whitespace from the final line\n
\t          current.indent = /([ \\t]+$)/.exec(body[i - 1].original)[1];\n
\t        }\n
\t      }\n
\t    }\n
\t    if (doStandalone && openStandalone) {\n
\t      omitRight((current.program || current.inverse).body);\n
\n
\t      // Strip out the previous content node if it\'s whitespace only\n
\t      omitLeft(body, i);\n
\t    }\n
\t    if (doStandalone && closeStandalone) {\n
\t      // Always strip the next node\n
\t      omitRight(body, i);\n
\n
\t      omitLeft((current.inverse || current.program).body);\n
\t    }\n
\t  }\n
\n
\t  return program;\n
\t};\n
\n
\tWhitespaceControl.prototype.BlockStatement = WhitespaceControl.prototype.DecoratorBlock = WhitespaceControl.prototype.PartialBlockStatement = function (block) {\n
\t  this.accept(block.program);\n
\t  this.accept(block.inverse);\n
\n
\t  // Find the inverse program that is involed with whitespace stripping.\n
\t  var program = block.program || block.inverse,\n
\t      inverse = block.program && block.inverse,\n
\t      firstInverse = inverse,\n
\t      lastInverse = inverse;\n
\n
\t  if (inverse && inverse.chained) {\n
\t    firstInverse = inverse.body[0].program;\n
\n
\t    // Walk the inverse chain to find the last inverse that is actually in the chain.\n
\t    while (lastInverse.chained) {\n
\t      lastInverse = lastInverse.body[lastInverse.body.length - 1].program;\n
\t    }\n
\t  }\n
\n
\t  var strip = {\n
\t    open: block.openStrip.open,\n
\t    close: block.closeStrip.close,\n
\n
\t    // Determine the standalone candiacy. Basically flag our content as being possibly standalone\n
\t    // so our parent can determine if we actually are standalone\n
\t    openStandalone: isNextWhitespace(program.body),\n
\t    closeStandalone: isPrevWhitespace((firstInverse || program).body)\n
\t  };\n
\n
\t  if (block.openStrip.close) {\n
\t    omitRight(program.body, null, true);\n
\t  }\n
\n
\t  if (inverse) {\n
\t    var inverseStrip = block.inverseStrip;\n
\n
\t    if (inverseStrip.open) {\n
\t      omitLeft(program.body, null, true);\n
\t    }\n
\n
\t    if (inverseStrip.close) {\n
\t      omitRight(firstInverse.body, null, true);\n
\t    }\n
\t    if (block.closeStrip.open) {\n
\t      omitLeft(lastInverse.body, null, true);\n
\t    }\n
\n
\t    // Find standalone else statments\n
\t    if (!this.options.ignoreStandalone && isPrevWhitespace(program.body) && isNextWhitespace(firstInverse.body)) {\n
\t      omitLeft(program.body);\n
\t      omitRight(firstInverse.body);\n
\t    }\n
\t  } else if (block.closeStrip.open) {\n
\t    omitLeft(program.body, null, true);\n
\t  }\n
\n
\t  return strip;\n
\t};\n
\n
\tWhitespaceControl.prototype.Decorator = WhitespaceControl.prototype.MustacheStatement = function (mustache) {\n
\t  return mustache.strip;\n
\t};\n
\n
\tWhitespaceControl.prototype.PartialStatement = WhitespaceControl.prototype.CommentStatement = function (node) {\n
\t  /* istanbul ignore next */\n
\t  var strip = node.strip || {};\n
\t  return {\n
\t    inlineStandalone: true,\n
\t    open: strip.open,\n
\t    close: strip.close\n
\t  };\n
\t};\n
\n
\tfunction isPrevWhitespace(body, i, isRoot) {\n
\t  if (i === undefined) {\n
\t    i = body.length;\n
\t  }\n
\n
\t  // Nodes that end with newlines are considered whitespace (but are special\n
\t  // cased for strip operations)\n
\t  var prev = body[i - 1],\n
\t      sibling = body[i - 2];\n
\t  if (!prev) {\n
\t    return isRoot;\n
\t  }\n
\n
\t  if (prev.type === \'ContentStatement\') {\n
\t    return (sibling || !isRoot ? /\\r?\\n\\s*?$/ : /(^|\\r?\\n)\\s*?$/).test(prev.original);\n
\t  }\n
\t}\n
\tfunction isNextWhitespace(body, i, isRoot) {\n
\t  if (i === undefined) {\n
\t    i = -1;\n
\t  }\n
\n
\t  var next = body[i + 1],\n
\t      sibling = body[i + 2];\n
\t  if (!next) {\n
\t    return isRoot;\n
\t  }\n
\n
\t  if (next.type === \'ContentStatement\') {\n
\t    return (sibling || !isRoot ? /^\\s*?\\r?\\n/ : /^\\s*?(\\r?\\n|$)/).test(next.original);\n
\t  }\n
\t}\n
\n
\t// Marks the node to the right of the position as omitted.\n
\t// I.e. {{foo}}\' \' will mark the \' \' node as omitted.\n
\t//\n
\t// If i is undefined, then the first child will be marked as such.\n
\t//\n
\t// If mulitple is truthy then all whitespace will be stripped out until non-whitespace\n
\t// content is met.\n
\tfunction omitRight(body, i, multiple) {\n
\t  var current = body[i == null ? 0 : i + 1];\n
\t  if (!current || current.type !== \'ContentStatement\' || !multiple && current.rightStripped) {\n
\t    return;\n
\t  }\n
\n
\t  var original = current.value;\n
\t  current.value = current.value.replace(multiple ? /^\\s+/ : /^[ \\t]*\\r?\\n?/, \'\');\n
\t  current.rightStripped = current.value !== original;\n
\t}\n
\n
\t// Marks the node to the left of the position as omitted.\n
\t// I.e. \' \'{{foo}} will mark the \' \' node as omitted.\n
\t//\n
\t// If i is undefined then the last child will be marked as such.\n
\t//\n
\t// If mulitple is truthy then all whitespace will be stripped out until non-whitespace\n
\t// content is met.\n
\tfunction omitLeft(body, i, multiple) {\n
\t  var current = body[i == null ? body.length - 1 : i - 1];\n
\t  if (!current || current.type !== \'ContentStatement\' || !multiple && current.leftStripped) {\n
\t    return;\n
\t  }\n
\n
\t  // We omit the last node if it\'s whitespace only and not preceeded by a non-content node.\n
\t  var original = current.value;\n
\t  current.value = current.value.replace(multiple ? /\\s+$/ : /[ \\t]+$/, \'\');\n
\t  current.leftStripped = current.value !== original;\n
\t  return current.leftStripped;\n
\t}\n
\n
\texports[\'default\'] = WhitespaceControl;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 25 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tfunction Visitor() {\n
\t  this.parents = [];\n
\t}\n
\n
\tVisitor.prototype = {\n
\t  constructor: Visitor,\n
\t  mutating: false,\n
\n
\t  // Visits a given value. If mutating, will replace the value if necessary.\n
\t  acceptKey: function acceptKey(node, name) {\n
\t    var value = this.accept(node[name]);\n
\t    if (this.mutating) {\n
\t      // Hacky sanity check: This may have a few false positives for type for the helper\n
\t      // methods but will generally do the right thing without a lot of overhead.\n
\t      if (value && !Visitor.prototype[value.type]) {\n
\t        throw new _exception2[\'default\'](\'Unexpected node type "\' + value.type + \'" found when accepting \' + name + \' on \' + node.type);\n
\t      }\n
\t      node[name] = value;\n
\t    }\n
\t  },\n
\n
\t  // Performs an accept operation with added sanity check to ensure\n
\t  // required keys are not removed.\n
\t  acceptRequired: function acceptRequired(node, name) {\n
\t    this.acceptKey(node, name);\n
\n
\t    if (!node[name]) {\n
\t      throw new _exception2[\'default\'](node.type + \' requires \' + name);\n
\t    }\n
\t  },\n
\n
\t  // Traverses a given array. If mutating, empty respnses will be removed\n
\t  // for child elements.\n
\t  acceptArray: function acceptArray(array) {\n
\t    for (var i = 0, l = array.length; i < l; i++) {\n
\t      this.acceptKey(array, i);\n
\n
\t      if (!array[i]) {\n
\t        array.splice(i, 1);\n
\t        i--;\n
\t        l--;\n
\t      }\n
\t    }\n
\t  },\n
\n
\t  accept: function accept(object) {\n
\t    if (!object) {\n
\t      return;\n
\t    }\n
\n
\t    /* istanbul ignore next: Sanity code */\n
\t    if (!this[object.type]) {\n
\t      throw new _exception2[\'default\'](\'Unknown type: \' + object.type, object);\n
\t    }\n
\n
\t    if (this.current) {\n
\t      this.parents.unshift(this.current);\n
\t    }\n
\t    this.current = object;\n
\n
\t    var ret = this[object.type](object);\n
\n
\t    this.current = this.parents.shift();\n
\n
\t    if (!this.mutating || ret) {\n
\t      return ret;\n
\t    } else if (ret !== false) {\n
\t      return object;\n
\t    }\n
\t  },\n
\n
\t  Program: function Program(program) {\n
\t    this.acceptArray(program.body);\n
\t  },\n
\n
\t  MustacheStatement: visitSubExpression,\n
\t  Decorator: visitSubExpression,\n
\n
\t  BlockStatement: visitBlock,\n
\t  DecoratorBlock: visitBlock,\n
\n
\t  PartialStatement: visitPartial,\n
\t  PartialBlockStatement: function PartialBlockStatement(partial) {\n
\t    visitPartial.call(this, partial);\n
\n
\t    this.acceptKey(partial, \'program\');\n
\t  },\n
\n
\t  ContentStatement: function ContentStatement() /* content */{},\n
\t  CommentStatement: function CommentStatement() /* comment */{},\n
\n
\t  SubExpression: visitSubExpression,\n
\n
\t  PathExpression: function PathExpression() /* path */{},\n
\n
\t  StringLiteral: function StringLiteral() /* string */{},\n
\t  NumberLiteral: function NumberLiteral() /* number */{},\n
\t  BooleanLiteral: function BooleanLiteral() /* bool */{},\n
\t  UndefinedLiteral: function UndefinedLiteral() /* literal */{},\n
\t  NullLiteral: function NullLiteral() /* literal */{},\n
\n
\t  Hash: function Hash(hash) {\n
\t    this.acceptArray(hash.pairs);\n
\t  },\n
\t  HashPair: function HashPair(pair) {\n
\t    this.acceptRequired(pair, \'value\');\n
\t  }\n
\t};\n
\n
\tfunction visitSubExpression(mustache) {\n
\t  this.acceptRequired(mustache, \'path\');\n
\t  this.acceptArray(mustache.params);\n
\t  this.acceptKey(mustache, \'hash\');\n
\t}\n
\tfunction visitBlock(block) {\n
\t  visitSubExpression.call(this, block);\n
\n
\t  this.acceptKey(block, \'program\');\n
\t  this.acceptKey(block, \'inverse\');\n
\t}\n
\tfunction visitPartial(partial) {\n
\t  this.acceptRequired(partial, \'name\');\n
\t  this.acceptArray(partial.params);\n
\t  this.acceptKey(partial, \'hash\');\n
\t}\n
\n
\texports[\'default\'] = Visitor;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 26 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.SourceLocation = SourceLocation;\n
\texports.id = id;\n
\texports.stripFlags = stripFlags;\n
\texports.stripComment = stripComment;\n
\texports.preparePath = preparePath;\n
\texports.prepareMustache = prepareMustache;\n
\texports.prepareRawBlock = prepareRawBlock;\n
\texports.prepareBlock = prepareBlock;\n
\texports.prepareProgram = prepareProgram;\n
\texports.preparePartialBlock = preparePartialBlock;\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tfunction validateClose(open, close) {\n
\t  close = close.path ? close.path.original : close;\n
\n
\t  if (open.path.original !== close) {\n
\t    var errorNode = { loc: open.path.loc };\n
\n
\t    throw new _exception2[\'default\'](open.path.original + " doesn\'t match " + close, errorNode);\n
\t  }\n
\t}\n
\n
\tfunction SourceLocation(source, locInfo) {\n
\t  this.source = source;\n
\t  this.start = {\n
\t    line: locInfo.first_line,\n
\t    column: locInfo.first_column\n
\t  };\n
\t  this.end = {\n
\t    line: locInfo.last_line,\n
\t    column: locInfo.last_column\n
\t  };\n
\t}\n
\n
\tfunction id(token) {\n
\t  if (/^\\[.*\\]$/.test(token)) {\n
\t    return token.substr(1, token.length - 2);\n
\t  } else {\n
\t    return token;\n
\t  }\n
\t}\n
\n
\tfunction stripFlags(open, close) {\n
\t  return {\n
\t    open: open.charAt(2) === \'~\',\n
\t    close: close.charAt(close.length - 3) === \'~\'\n
\t  };\n
\t}\n
\n
\tfunction stripComment(comment) {\n
\t  return comment.replace(/^\\{\\{~?\\!-?-?/, \'\').replace(/-?-?~?\\}\\}$/, \'\');\n
\t}\n
\n
\tfunction preparePath(data, parts, loc) {\n
\t  loc = this.locInfo(loc);\n
\n
\t  var original = data ? \'@\' : \'\',\n
\t      dig = [],\n
\t      depth = 0,\n
\t      depthString = \'\';\n
\n
\t  for (var i = 0, l = parts.length; i < l; i++) {\n
\t    var part = parts[i].part,\n
\n
\t    // If we have [] syntax then we do not treat path references as operators,\n
\t    // i.e. foo.[this] resolves to approximately context.foo[\'this\']\n
\t    isLiteral = parts[i].original !== part;\n
\t    original += (parts[i].separator || \'\') + part;\n
\n
\t    if (!isLiteral && (part === \'..\' || part === \'.\' || part === \'this\')) {\n
\t      if (dig.length > 0) {\n
\t        throw new _exception2[\'default\'](\'Invalid path: \' + original, { loc: loc });\n
\t      } else if (part === \'..\') {\n
\t        depth++;\n
\t        depthString += \'../\';\n
\t      }\n
\t    } else {\n
\t      dig.push(part);\n
\t    }\n
\t  }\n
\n
\t  return {\n
\t    type: \'PathExpression\',\n
\t    data: data,\n
\t    depth: depth,\n
\t    parts: dig,\n
\t    original: original,\n
\t    loc: loc\n
\t  };\n
\t}\n
\n
\tfunction prepareMustache(path, params, hash, open, strip, locInfo) {\n
\t  // Must use charAt to support IE pre-10\n
\t  var escapeFlag = open.charAt(3) || open.charAt(2),\n
\t      escaped = escapeFlag !== \'{\' && escapeFlag !== \'&\';\n
\n
\t  var decorator = /\\*/.test(open);\n
\t  return {\n
\t    type: decorator ? \'Decorator\' : \'MustacheStatement\',\n
\t    path: path,\n
\t    params: params,\n
\t    hash: hash,\n
\t    escaped: escaped,\n
\t    strip: strip,\n
\t    loc: this.locInfo(locInfo)\n
\t  };\n
\t}\n
\n
\tfunction prepareRawBlock(openRawBlock, contents, close, locInfo) {\n
\t  validateClose(openRawBlock, close);\n
\n
\t  locInfo = this.locInfo(locInfo);\n
\t  var program = {\n
\t    type: \'Program\',\n
\t    body: contents,\n
\t    strip: {},\n
\t    loc: locInfo\n
\t  };\n
\n
\t  return {\n
\t    type: \'BlockStatement\',\n
\t    path: openRawBlock.path,\n
\t    params: openRawBlock.params,\n
\t    hash: openRawBlock.hash,\n
\t    program: program,\n
\t    openStrip: {},\n
\t    inverseStrip: {},\n
\t    closeStrip: {},\n
\t    loc: locInfo\n
\t  };\n
\t}\n
\n
\tfunction prepareBlock(openBlock, program, inverseAndProgram, close, inverted, locInfo) {\n
\t  if (close && close.path) {\n
\t    validateClose(openBlock, close);\n
\t  }\n
\n
\t  var decorator = /\\*/.test(openBlock.open);\n
\n
\t  program.blockParams = openBlock.blockParams;\n
\n
\t  var inverse = undefined,\n
\t      inverseStrip = undefined;\n
\n
\t  if (inverseAndProgram) {\n
\t    if (decorator) {\n
\t      throw new _exception2[\'default\'](\'Unexpected inverse block on decorator\', inverseAndProgram);\n
\t    }\n
\n
\t    if (inverseAndProgram.chain) {\n
\t      inverseAndProgram.program.body[0].closeStrip = close.strip;\n
\t    }\n
\n
\t    inverseStrip = inverseAndProgram.strip;\n
\t    inverse = inverseAndProgram.program;\n
\t  }\n
\n
\t  if (inverted) {\n
\t    inverted = inverse;\n
\t    inverse = program;\n
\t    program = inverted;\n
\t  }\n
\n
\t  return {\n
\t    type: decorator ? \'DecoratorBlock\' : \'BlockStatement\',\n
\t    path: openBlock.path,\n
\t    params: openBlock.params,\n
\t    hash: openBlock.hash,\n
\t    program: program,\n
\t    inverse: inverse,\n
\t    openStrip: openBlock.strip,\n
\t    inverseStrip: inverseStrip,\n
\t    closeStrip: close && close.strip,\n
\t    loc: this.locInfo(locInfo)\n
\t  };\n
\t}\n
\n
\tfunction prepareProgram(statements, loc) {\n
\t  if (!loc && statements.length) {\n
\t    var firstLoc = statements[0].loc,\n
\t        lastLoc = statements[statements.length - 1].loc;\n
\n
\t    /* istanbul ignore else */\n
\t    if (firstLoc && lastLoc) {\n
\t      loc = {\n
\t        source: firstLoc.source,\n
\t        start: {\n
\t          line: firstLoc.start.line,\n
\t          column: firstLoc.start.column\n
\t        },\n
\t        end: {\n
\t          line: lastLoc.end.line,\n
\t          column: lastLoc.end.column\n
\t        }\n
\t      };\n
\t    }\n
\t  }\n
\n
\t  return {\n
\t    type: \'Program\',\n
\t    body: statements,\n
\t    strip: {},\n
\t    loc: loc\n
\t  };\n
\t}\n
\n
\tfunction preparePartialBlock(open, program, close, locInfo) {\n
\t  validateClose(open, close);\n
\n
\t  return {\n
\t    type: \'PartialBlockStatement\',\n
\t    name: open.path,\n
\t    params: open.params,\n
\t    hash: open.hash,\n
\t    program: program,\n
\t    openStrip: open.strip,\n
\t    closeStrip: close && close.strip,\n
\t    loc: this.locInfo(locInfo)\n
\t  };\n
\t}\n
\n
/***/ },\n
/* 27 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t/* eslint-disable new-cap */\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\texports.Compiler = Compiler;\n
\texports.precompile = precompile;\n
\texports.compile = compile;\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar _ast = __webpack_require__(21);\n
\n
\tvar _ast2 = _interopRequireDefault(_ast);\n
\n
\tvar slice = [].slice;\n
\n
\tfunction Compiler() {}\n
\n
\t// the foundHelper register will disambiguate helper lookup from finding a\n
\t// function in a context. This is necessary for mustache compatibility, which\n
\t// requires that context functions in blocks are evaluated by blockHelperMissing,\n
\t// and then proceed as if the resulting value was provided to blockHelperMissing.\n
\n
\tCompiler.prototype = {\n
\t  compiler: Compiler,\n
\n
\t  equals: function equals(other) {\n
\t    var len = this.opcodes.length;\n
\t    if (other.opcodes.length !== len) {\n
\t      return false;\n
\t    }\n
\n
\t    for (var i = 0; i < len; i++) {\n
\t      var opcode = this.opcodes[i],\n
\t          otherOpcode = other.opcodes[i];\n
\t      if (opcode.opcode !== otherOpcode.opcode || !argEquals(opcode.args, otherOpcode.args)) {\n
\t        return false;\n
\t      }\n
\t    }\n
\n
\t    // We know that length is the same between the two arrays because they are directly tied\n
\t    // to the opcode behavior above.\n
\t    len = this.children.length;\n
\t    for (var i = 0; i < len; i++) {\n
\t      if (!this.children[i].equals(other.children[i])) {\n
\t        return false;\n
\t      }\n
\t    }\n
\n
\t    return true;\n
\t  },\n
\n
\t  guid: 0,\n
\n
\t  compile: function compile(program, options) {\n
\t    this.sourceNode = [];\n
\t    this.opcodes = [];\n
\t    this.children = [];\n
\t    this.options = options;\n
\t    this.stringParams = options.stringParams;\n
\t    this.trackIds = options.trackIds;\n
\n
\t    options.blockParams = options.blockParams || [];\n
\n
\t    // These changes will propagate to the other compiler components\n
\t    var knownHelpers = options.knownHelpers;\n
\t    options.knownHelpers = {\n
\t      \'helperMissing\': true,\n
\t      \'blockHelperMissing\': true,\n
\t      \'each\': true,\n
\t      \'if\': true,\n
\t      \'unless\': true,\n
\t      \'with\': true,\n
\t      \'log\': true,\n
\t      \'lookup\': true\n
\t    };\n
\t    if (knownHelpers) {\n
\t      for (var _name in knownHelpers) {\n
\t        /* istanbul ignore else */\n
\t        if (_name in knownHelpers) {\n
\t          options.knownHelpers[_name] = knownHelpers[_name];\n
\t        }\n
\t      }\n
\t    }\n
\n
\t    return this.accept(program);\n
\t  },\n
\n
\t  compileProgram: function compileProgram(program) {\n
\t    var childCompiler = new this.compiler(),\n
\t        // eslint-disable-line new-cap\n
\t    result = childCompiler.compile(program, this.options),\n
\t        guid = this.guid++;\n
\n
\t    this.usePartial = this.usePartial || result.usePartial;\n
\n
\t    this.children[guid] = result;\n
\t    this.useDepths = this.useDepths || result.useDepths;\n
\n
\t    return guid;\n
\t  },\n
\n
\t  accept: function accept(node) {\n
\t    /* istanbul ignore next: Sanity code */\n
\t    if (!this[node.type]) {\n
\t      throw new _exception2[\'default\'](\'Unknown type: \' + node.type, node);\n
\t    }\n
\n
\t    this.sourceNode.unshift(node);\n
\t    var ret = this[node.type](node);\n
\t    this.sourceNode.shift();\n
\t    return ret;\n
\t  },\n
\n
\t  Program: function Program(program) {\n
\t    this.options.blockParams.unshift(program.blockParams);\n
\n
\t    var body = program.body,\n
\t        bodyLength = body.length;\n
\t    for (var i = 0; i < bodyLength; i++) {\n
\t      this.accept(body[i]);\n
\t    }\n
\n
\t    this.options.blockParams.shift();\n
\n
\t    this.isSimple = bodyLength === 1;\n
\t    this.blockParams = program.blockParams ? program.blockParams.length : 0;\n
\n
\t    return this;\n
\t  },\n
\n
\t  BlockStatement: function BlockStatement(block) {\n
\t    transformLiteralToPath(block);\n
\n
\t    var program = block.program,\n
\t        inverse = block.inverse;\n
\n
\t    program = program && this.compileProgram(program);\n
\t    inverse = inverse && this.compileProgram(inverse);\n
\n
\t    var type = this.classifySexpr(block);\n
\n
\t    if (type === \'helper\') {\n
\t      this.helperSexpr(block, program, inverse);\n
\t    } else if (type === \'simple\') {\n
\t      this.simpleSexpr(block);\n
\n
\t      // now that the simple mustache is resolved, we need to\n
\t      // evaluate it by executing `blockHelperMissing`\n
\t      this.opcode(\'pushProgram\', program);\n
\t      this.opcode(\'pushProgram\', inverse);\n
\t      this.opcode(\'emptyHash\');\n
\t      this.opcode(\'blockValue\', block.path.original);\n
\t    } else {\n
\t      this.ambiguousSexpr(block, program, inverse);\n
\n
\t      // now that the simple mustache is resolved, we need to\n
\t      // evaluate it by executing `blockHelperMissing`\n
\t      this.opcode(\'pushProgram\', program);\n
\t      this.opcode(\'pushProgram\', inverse);\n
\t      this.opcode(\'emptyHash\');\n
\t      this.opcode(\'ambiguousBlockValue\');\n
\t    }\n
\n
\t    this.opcode(\'append\');\n
\t  },\n
\n
\t  DecoratorBlock: function DecoratorBlock(decorator) {\n
\t    var program = decorator.program && this.compileProgram(decorator.program);\n
\t    var params = this.setupFullMustacheParams(decorator, program, undefined),\n
\t        path = decorator.path;\n
\n
\t    this.useDecorators = true;\n
\t    this.opcode(\'registerDecorator\', params.length, path.original);\n
\t  },\n
\n
\t  PartialStatement: function PartialStatement(partial) {\n
\t    this.usePartial = true;\n
\n
\t    var program = partial.program;\n
\t    if (program) {\n
\t      program = this.compileProgram(partial.program);\n
\t    }\n
\n
\t    var params = partial.params;\n
\t    if (params.length > 1) {\n
\t      throw new _exception2[\'default\'](\'Unsupported number of partial arguments: \' + params.length, partial);\n
\t    } else if (!params.length) {\n
\t      if (this.options.explicitPartialContext) {\n
\t        this.opcode(\'pushLiteral\', \'undefined\');\n
\t      } else {\n
\t        params.push({ type: \'PathExpression\', parts: [], depth: 0 });\n
\t      }\n
\t    }\n
\n
\t    var partialName = partial.name.original,\n
\t        isDynamic = partial.name.type === \'SubExpression\';\n
\t    if (isDynamic) {\n
\t      this.accept(partial.name);\n
\t    }\n
\n
\t    this.setupFullMustacheParams(partial, program, undefined, true);\n
\n
\t    var indent = partial.indent || \'\';\n
\t    if (this.options.preventIndent && indent) {\n
\t      this.opcode(\'appendContent\', indent);\n
\t      indent = \'\';\n
\t    }\n
\n
\t    this.opcode(\'invokePartial\', isDynamic, partialName, indent);\n
\t    this.opcode(\'append\');\n
\t  },\n
\t  PartialBlockStatement: function PartialBlockStatement(partialBlock) {\n
\t    this.PartialStatement(partialBlock);\n
\t  },\n
\n
\t  MustacheStatement: function MustacheStatement(mustache) {\n
\t    this.SubExpression(mustache);\n
\n
\t    if (mustache.escaped && !this.options.noEscape) {\n
\t      this.opcode(\'appendEscaped\');\n
\t    } else {\n
\t      this.opcode(\'append\');\n
\t    }\n
\t  },\n
\t  Decorator: function Decorator(decorator) {\n
\t    this.DecoratorBlock(decorator);\n
\t  },\n
\n
\t  ContentStatement: function ContentStatement(content) {\n
\t    if (content.value) {\n
\t      this.opcode(\'appendContent\', content.value);\n
\t    }\n
\t  },\n
\n
\t  CommentStatement: function CommentStatement() {},\n
\n
\t  SubExpression: function SubExpression(sexpr) {\n
\t    transformLiteralToPath(sexpr);\n
\t    var type = this.classifySexpr(sexpr);\n
\n
\t    if (type === \'simple\') {\n
\t      this.simpleSexpr(sexpr);\n
\t    } else if (type === \'helper\') {\n
\t      this.helperSexpr(sexpr);\n
\t    } else {\n
\t      this.ambiguousSexpr(sexpr);\n
\t    }\n
\t  },\n
\t  ambiguousSexpr: function ambiguousSexpr(sexpr, program, inverse) {\n
\t    var path = sexpr.path,\n
\t        name = path.parts[0],\n
\t        isBlock = program != null || inverse != null;\n
\n
\t    this.opcode(\'getContext\', path.depth);\n
\n
\t    this.opcode(\'pushProgram\', program);\n
\t    this.opcode(\'pushProgram\', inverse);\n
\n
\t    path.strict = true;\n
\t    this.accept(path);\n
\n
\t    this.opcode(\'invokeAmbiguous\', name, isBlock);\n
\t  },\n
\n
\t  simpleSexpr: function simpleSexpr(sexpr) {\n
\t    var path = sexpr.path;\n
\t    path.strict = true;\n
\t    this.accept(path);\n
\t    this.opcode(\'resolvePossibleLambda\');\n
\t  },\n
\n
\t  helperSexpr: function helperSexpr(sexpr, program, inverse) {\n
\t    var params = this.setupFullMustacheParams(sexpr, program, inverse),\n
\t        path = sexpr.path,\n
\t        name = path.parts[0];\n
\n
\t    if (this.options.knownHelpers[name]) {\n
\t      this.opcode(\'invokeKnownHelper\', params.length, name);\n
\t    } else if (this.options.knownHelpersOnly) {\n
\t      throw new _exception2[\'default\'](\'You specified knownHelpersOnly, but used the unknown helper \' + name, sexpr);\n
\t    } else {\n
\t      path.strict = true;\n
\t      path.falsy = true;\n
\n
\t      this.accept(path);\n
\t      this.opcode(\'invokeHelper\', params.length, path.original, _ast2[\'default\'].helpers.simpleId(path));\n
\t    }\n
\t  },\n
\n
\t  PathExpression: function PathExpression(path) {\n
\t    this.addDepth(path.depth);\n
\t    this.opcode(\'getContext\', path.depth);\n
\n
\t    var name = path.parts[0],\n
\t        scoped = _ast2[\'default\'].helpers.scopedId(path),\n
\t        blockParamId = !path.depth && !scoped && this.blockParamIndex(name);\n
\n
\t    if (blockParamId) {\n
\t      this.opcode(\'lookupBlockParam\', blockParamId, path.parts);\n
\t    } else if (!name) {\n
\t      // Context reference, i.e. `{{foo .}}` or `{{foo ..}}`\n
\t      this.opcode(\'pushContext\');\n
\t    } else if (path.data) {\n
\t      this.options.data = true;\n
\t      this.opcode(\'lookupData\', path.depth, path.parts, path.strict);\n
\t    } else {\n
\t      this.opcode(\'lookupOnContext\', path.parts, path.falsy, path.strict, scoped);\n
\t    }\n
\t  },\n
\n
\t  StringLiteral: function StringLiteral(string) {\n
\t    this.opcode(\'pushString\', string.value);\n
\t  },\n
\n
\t  NumberLiteral: function NumberLiteral(number) {\n
\t    this.opcode(\'pushLiteral\', number.value);\n
\t  },\n
\n
\t  BooleanLiteral: function BooleanLiteral(bool) {\n
\t    this.opcode(\'pushLiteral\', bool.value);\n
\t  },\n
\n
\t  UndefinedLiteral: function UndefinedLiteral() {\n
\t    this.opcode(\'pushLiteral\', \'undefined\');\n
\t  },\n
\n
\t  NullLiteral: function NullLiteral() {\n
\t    this.opcode(\'pushLiteral\', \'null\');\n
\t  },\n
\n
\t  Hash: function Hash(hash) {\n
\t    var pairs = hash.pairs,\n
\t        i = 0,\n
\t        l = pairs.length;\n
\n
\t    this.opcode(\'pushHash\');\n
\n
\t    for (; i < l; i++) {\n
\t      this.pushParam(pairs[i].value);\n
\t    }\n
\t    while (i--) {\n
\t      this.opcode(\'assignToHash\', pairs[i].key);\n
\t    }\n
\t    this.opcode(\'popHash\');\n
\t  },\n
\n
\t  // HELPERS\n
\t  opcode: function opcode(name) {\n
\t    this.opcodes.push({ opcode: name, args: slice.call(arguments, 1), loc: this.sourceNode[0].loc });\n
\t  },\n
\n
\t  addDepth: function addDepth(depth) {\n
\t    if (!depth) {\n
\t      return;\n
\t    }\n
\n
\t    this.useDepths = true;\n
\t  },\n
\n
\t  classifySexpr: function classifySexpr(sexpr) {\n
\t    var isSimple = _ast2[\'default\'].helpers.simpleId(sexpr.path);\n
\n
\t    var isBlockParam = isSimple && !!this.blockParamIndex(sexpr.path.parts[0]);\n
\n
\t    // a mustache is an eligible helper if:\n
\t    // * its id is simple (a single part, not `this` or `..`)\n
\t    var isHelper = !isBlockParam && _ast2[\'default\'].helpers.helperExpression(sexpr);\n
\n
\t    // if a mustache is an eligible helper but not a definite\n
\t    // helper, it is ambiguous, and will be resolved in a later\n
\t    // pass or at runtime.\n
\t    var isEligible = !isBlockParam && (isHelper || isSimple);\n
\n
\t    // if ambiguous, we can possibly resolve the ambiguity now\n
\t    // An eligible helper is one that does not have a complex path, i.e. `this.foo`, `../foo` etc.\n
\t    if (isEligible && !isHelper) {\n
\t      var _name2 = sexpr.path.parts[0],\n
\t          options = this.options;\n
\n
\t      if (options.knownHelpers[_name2]) {\n
\t        isHelper = true;\n
\t      } else if (options.knownHelpersOnly) {\n
\t        isEligible = false;\n
\t      }\n
\t    }\n
\n
\t    if (isHelper) {\n
\t      return \'helper\';\n
\t    } else if (isEligible) {\n
\t      return \'ambiguous\';\n
\t    } else {\n
\t      return \'simple\';\n
\t    }\n
\t  },\n
\n
\t  pushParams: function pushParams(params) {\n
\t    for (var i = 0, l = params.length; i < l; i++) {\n
\t      this.pushParam(params[i]);\n
\t    }\n
\t  },\n
\n
\t  pushParam: function pushParam(val) {\n
\t    var value = val.value != null ? val.value : val.original || \'\';\n
\n
\t    if (this.stringParams) {\n
\t      if (value.replace) {\n
\t        value = value.replace(/^(\\.?\\.\\/)*/g, \'\').replace(/\\//g, \'.\');\n
\t      }\n
\n
\t      if (val.depth) {\n
\t        this.addDepth(val.depth);\n
\t      }\n
\t      this.opcode(\'getContext\', val.depth || 0);\n
\t      this.opcode(\'pushStringParam\', value, val.type);\n
\n
\t      if (val.type === \'SubExpression\') {\n
\t        // SubExpressions get evaluated and passed in\n
\t        // in string params mode.\n
\t        this.accept(val);\n
\t      }\n
\t    } else {\n
\t      if (this.trackIds) {\n
\t        var blockParamIndex = undefined;\n
\t        if (val.parts && !_ast2[\'default\'].helpers.scopedId(val) && !val.depth) {\n
\t          blockParamIndex = this.blockParamIndex(val.parts[0]);\n
\t        }\n
\t        if (blockParamIndex) {\n
\t          var blockParamChild = val.parts.slice(1).join(\'.\');\n
\t          this.opcode(\'pushId\', \'BlockParam\', blockParamIndex, blockParamChild);\n
\t        } else {\n
\t          value = val.original || value;\n
\t          if (value.replace) {\n
\t            value = value.replace(/^this(?:\\.|$)/, \'\').replace(/^\\.\\//, \'\').replace(/^\\.$/, \'\');\n
\t          }\n
\n
\t          this.opcode(\'pushId\', val.type, value);\n
\t        }\n
\t      }\n
\t      this.accept(val);\n
\t    }\n
\t  },\n
\n
\t  setupFullMustacheParams: function setupFullMustacheParams(sexpr, program, inverse, omitEmpty) {\n
\t    var params = sexpr.params;\n
\t    this.pushParams(params);\n
\n
\t    this.opcode(\'pushProgram\', program);\n
\t    this.opcode(\'pushProgram\', inverse);\n
\n
\t    if (sexpr.hash) {\n
\t      this.accept(sexpr.hash);\n
\t    } else {\n
\t      this.opcode(\'emptyHash\', omitEmpty);\n
\t    }\n
\n
\t    return params;\n
\t  },\n
\n
\t  blockParamIndex: function blockParamIndex(name) {\n
\t    for (var depth = 0, len = this.options.blockParams.length; depth < len; depth++) {\n
\t      var blockParams = this.options.blockParams[depth],\n
\t          param = blockParams && _utils.indexOf(blockParams, name);\n
\t      if (blockParams && param >= 0) {\n
\t        return [depth, param];\n
\t      }\n
\t    }\n
\t  }\n
\t};\n
\n
\tfunction precompile(input, options, env) {\n
\t  if (input == null || typeof input !== \'string\' && input.type !== \'Program\') {\n
\t    throw new _exception2[\'default\'](\'You must pass a string or Handlebars AST to Handlebars.precompile. You passed \' + input);\n
\t  }\n
\n
\t  options = options || {};\n
\t  if (!(\'data\' in options)) {\n
\t    options.data = true;\n
\t  }\n
\t  if (options.compat) {\n
\t    options.useDepths = true;\n
\t  }\n
\n
\t  var ast = env.parse(input, options),\n
\t      environment = new env.Compiler().compile(ast, options);\n
\t  return new env.JavaScriptCompiler().compile(environment, options);\n
\t}\n
\n
\tfunction compile(input, options, env) {\n
\t  if (options === undefined) options = {};\n
\n
\t  if (input == null || typeof input !== \'string\' && input.type !== \'Program\') {\n
\t    throw new _exception2[\'default\'](\'You must pass a string or Handlebars AST to Handlebars.compile. You passed \' + input);\n
\t  }\n
\n
\t  if (!(\'data\' in options)) {\n
\t    options.data = true;\n
\t  }\n
\t  if (options.compat) {\n
\t    options.useDepths = true;\n
\t  }\n
\n
\t  var compiled = undefined;\n
\n
\t  function compileInput() {\n
\t    var ast = env.parse(input, options),\n
\t        environment = new env.Compiler().compile(ast, options),\n
\t        templateSpec = new env.JavaScriptCompiler().compile(environment, options, undefined, true);\n
\t    return env.template(templateSpec);\n
\t  }\n
\n
\t  // Template is only compiled on first use and cached after that point.\n
\t  function ret(context, execOptions) {\n
\t    if (!compiled) {\n
\t      compiled = compileInput();\n
\t    }\n
\t    return compiled.call(this, context, execOptions);\n
\t  }\n
\t  ret._setup = function (setupOptions) {\n
\t    if (!compiled) {\n
\t      compiled = compileInput();\n
\t    }\n
\t    return compiled._setup(setupOptions);\n
\t  };\n
\t  ret._child = function (i, data, blockParams, depths) {\n
\t    if (!compiled) {\n
\t      compiled = compileInput();\n
\t    }\n
\t    return compiled._child(i, data, blockParams, depths);\n
\t  };\n
\t  return ret;\n
\t}\n
\n
\tfunction argEquals(a, b) {\n
\t  if (a === b) {\n
\t    return true;\n
\t  }\n
\n
\t  if (_utils.isArray(a) && _utils.isArray(b) && a.length === b.length) {\n
\t    for (var i = 0; i < a.length; i++) {\n
\t      if (!argEquals(a[i], b[i])) {\n
\t        return false;\n
\t      }\n
\t    }\n
\t    return true;\n
\t  }\n
\t}\n
\n
\tfunction transformLiteralToPath(sexpr) {\n
\t  if (!sexpr.path.parts) {\n
\t    var literal = sexpr.path;\n
\t    // Casting to string here to make false and 0 literal values play nicely with the rest\n
\t    // of the system.\n
\t    sexpr.path = {\n
\t      type: \'PathExpression\',\n
\t      data: false,\n
\t      depth: 0,\n
\t      parts: [literal.original + \'\'],\n
\t      original: literal.original + \'\',\n
\t      loc: literal.loc\n
\t    };\n
\t  }\n
\t}\n
\n
/***/ },\n
/* 28 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t\'use strict\';\n
\n
\tvar _interopRequireDefault = __webpack_require__(1)[\'default\'];\n
\n
\texports.__esModule = true;\n
\n
\tvar _base = __webpack_require__(4);\n
\n
\tvar _exception = __webpack_require__(6);\n
\n
\tvar _exception2 = _interopRequireDefault(_exception);\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar _codeGen = __webpack_require__(29);\n
\n
\tvar _codeGen2 = _interopRequireDefault(_codeGen);\n
\n
\tfunction Literal(value) {\n
\t  this.value = value;\n
\t}\n
\n
\tfunction JavaScriptCompiler() {}\n
\n
\tJavaScriptCompiler.prototype = {\n
\t  // PUBLIC API: You can override these methods in a subclass to provide\n
\t  // alternative compiled forms for name lookup and buffering semantics\n
\t  nameLookup: function nameLookup(parent, name /* , type*/) {\n
\t    if (JavaScriptCompiler.isValidJavaScriptVariableName(name)) {\n
\t      return [parent, \'.\', name];\n
\t    } else {\n
\t      return [parent, \'[\', JSON.stringify(name), \']\'];\n
\t    }\n
\t  },\n
\t  depthedLookup: function depthedLookup(name) {\n
\t    return [this.aliasable(\'container.lookup\'), \'(depths, "\', name, \'")\'];\n
\t  },\n
\n
\t  compilerInfo: function compilerInfo() {\n
\t    var revision = _base.COMPILER_REVISION,\n
\t        versions = _base.REVISION_CHANGES[revision];\n
\t    return [revision, versions];\n
\t  },\n
\n
\t  appendToBuffer: function appendToBuffer(source, location, explicit) {\n
\t    // Force a source as this simplifies the merge logic.\n
\t    if (!_utils.isArray(source)) {\n
\t      source = [source];\n
\t    }\n
\t    source = this.source.wrap(source, location);\n
\n
\t    if (this.environment.isSimple) {\n
\t      return [\'return \', source, \';\'];\n
\t    } else if (explicit) {\n
\t      // This is a case where the buffer operation occurs as a child of another\n
\t      // construct, generally braces. We have to explicitly output these buffer\n
\t      // operations to ensure that the emitted code goes in the correct location.\n
\t      return [\'buffer += \', source, \';\'];\n
\t    } else {\n
\t      source.appendToBuffer = true;\n
\t      return source;\n
\t    }\n
\t  },\n
\n
\t  initializeBuffer: function initializeBuffer() {\n
\t    return this.quotedString(\'\');\n
\t  },\n
\t  // END PUBLIC API\n
\n
\t  compile: function compile(environment, options, context, asObject) {\n
\t    this.environment = environment;\n
\t    this.options = options;\n
\t    this.stringParams = this.options.stringParams;\n
\t    this.trackIds = this.options.trackIds;\n
\t    this.precompile = !asObject;\n
\n
\t    this.name = this.environment.name;\n
\t    this.isChild = !!context;\n
\t    this.context = context || {\n
\t      decorators: [],\n
\t      programs: [],\n
\t      environments: []\n
\t    };\n
\n
\t    this.preamble();\n
\n
\t    this.stackSlot = 0;\n
\t    this.stackVars = [];\n
\t    this.aliases = {};\n
\t    this.registers = { list: [] };\n
\t    this.hashes = [];\n
\t    this.compileStack = [];\n
\t    this.inlineStack = [];\n
\t    this.blockParams = [];\n
\n
\t    this.compileChildren(environment, options);\n
\n
\t    this.useDepths = this.useDepths || environment.useDepths || environment.useDecorators || this.options.compat;\n
\t    this.useBlockParams = this.useBlockParams || environment.useBlockParams;\n
\n
\t    var opcodes = environment.opcodes,\n
\t        opcode = undefined,\n
\t        firstLoc = undefined,\n
\t        i = undefined,\n
\t        l = undefined;\n
\n
\t    for (i = 0, l = opcodes.length; i < l; i++) {\n
\t      opcode = opcodes[i];\n
\n
\t      this.source.currentLocation = opcode.loc;\n
\t      firstLoc = firstLoc || opcode.loc;\n
\t      this[opcode.opcode].apply(this, opcode.args);\n
\t    }\n
\n
\t    // Flush any trailing content that might be pending.\n
\t    this.source.currentLocation = firstLoc;\n
\t    this.pushSource(\'\');\n
\n
\t    /* istanbul ignore next */\n
\t    if (this.stackSlot || this.inlineStack.length || this.compileStack.length) {\n
\t      throw new _exception2[\'default\'](\'Compile completed with content left on stack\');\n
\t    }\n
\n
\t    if (!this.decorators.isEmpty()) {\n
\t      this.useDecorators = true;\n
\n
\t      this.decorators.prepend(\'var decorators = container.decorators;\\n\');\n
\t      this.decorators.push(\'return fn;\');\n
\n
\t      if (asObject) {\n
\t        this.decorators = Function.apply(this, [\'fn\', \'props\', \'container\', \'depth0\', \'data\', \'blockParams\', \'depths\', this.decorators.merge()]);\n
\t      } else {\n
\t        this.decorators.prepend(\'function(fn, props, container, depth0, data, blockParams, depths) {\\n\');\n
\t        this.decorators.push(\'}\\n\');\n
\t        this.decorators = this.decorators.merge();\n
\t      }\n
\t    } else {\n
\t      this.decorators = undefined;\n
\t    }\n
\n
\t    var fn = this.createFunctionContext(asObject);\n
\t    if (!this.isChild) {\n
\t      var ret = {\n
\t        compiler: this.compilerInfo(),\n
\t        main: fn\n
\t      };\n
\n
\t      if (this.decorators) {\n
\t        ret.main_d = this.decorators; // eslint-disable-line camelcase\n
\t        ret.useDecorators = true;\n
\t      }\n
\n
\t      var _context = this.context;\n
\t      var programs = _context.programs;\n
\t      var decorators = _context.decorators;\n
\n
\t      for (i = 0, l = programs.length; i < l; i++) {\n
\t        if (programs[i]) {\n
\t          ret[i] = programs[i];\n
\t          if (decorators[i]) {\n
\t            ret[i + \'_d\'] = decorators[i];\n
\t            ret.useDecorators = true;\n
\t          }\n
\t        }\n
\t      }\n
\n
\t      if (this.environment.usePartial) {\n
\t        ret.usePartial = true;\n
\t      }\n
\t      if (this.options.data) {\n
\t        ret.useData = true;\n
\t      }\n
\t      if (this.useDepths) {\n
\t        ret.useDepths = true;\n
\t      }\n
\t      if (this.useBlockParams) {\n
\t        ret.useBlockParams = true;\n
\t      }\n
\t      if (this.options.compat) {\n
\t        ret.compat = true;\n
\t      }\n
\n
\t      if (!asObject) {\n
\t        ret.compiler = JSON.stringify(ret.compiler);\n
\n
\t        this.source.currentLocation = { start: { line: 1, column: 0 } };\n
\t        ret = this.objectLiteral(ret);\n
\n
\t        if (options.srcName) {\n
\t          ret = ret.toStringWithSourceMap({ file: options.destName });\n
\t          ret.map = ret.map && ret.map.toString();\n
\t        } else {\n
\t          ret = ret.toString();\n
\t        }\n
\t      } else {\n
\t        ret.compilerOptions = this.options;\n
\t      }\n
\n
\t      return ret;\n
\t    } else {\n
\t      return fn;\n
\t    }\n
\t  },\n
\n
\t  preamble: function preamble() {\n
\t    // track the last context pushed into place to allow skipping the\n
\t    // getContext opcode when it would be a noop\n
\t    this.lastContext = 0;\n
\t    this.source = new _codeGen2[\'default\'](this.options.srcName);\n
\t    this.decorators = new _codeGen2[\'default\'](this.options.srcName);\n
\t  },\n
\n
\t  createFunctionContext: function createFunctionContext(asObject) {\n
\t    var varDeclarations = \'\';\n
\n
\t    var locals = this.stackVars.concat(this.registers.list);\n
\t    if (locals.length > 0) {\n
\t      varDeclarations += \', \' + locals.join(\', \');\n
\t    }\n
\n
\t    // Generate minimizer alias mappings\n
\t    //\n
\t    // When using true SourceNodes, this will update all references to the given alias\n
\t    // as the source nodes are reused in situ. For the non-source node compilation mode,\n
\t    // aliases will not be used, but this case is already being run on the client and\n
\t    // we aren\'t concern about minimizing the template size.\n
\t    var aliasCount = 0;\n
\t    for (var alias in this.aliases) {\n
\t      // eslint-disable-line guard-for-in\n
\t      var node = this.aliases[alias];\n
\n
\t      if (this.aliases.hasOwnProperty(alias) && node.children && node.referenceCount > 1) {\n
\t        varDeclarations += \', alias\' + ++aliasCount + \'=\' + alias;\n
\t        node.children[0] = \'alias\' + aliasCount;\n
\t      }\n
\t    }\n
\n
\t    var params = [\'container\', \'depth0\', \'helpers\', \'partials\', \'data\'];\n
\n
\t    if (this.useBlockParams || this.useDepths) {\n
\t      params.push(\'blockParams\');\n
\t    }\n
\t    if (this.useDepths) {\n
\t      params.push(\'depths\');\n
\t    }\n
\n
\t    // Perform a second pass over the output to merge content when possible\n
\t    var source = this.mergeSource(varDeclarations);\n
\n
\t    if (asObject) {\n
\t      params.push(source);\n
\n
\t      return Function.apply(this, params);\n
\t    } else {\n
\t      return this.source.wrap([\'function(\', params.join(\',\'), \') {\\n  \', source, \'}\']);\n
\t    }\n
\t  },\n
\t  mergeSource: function mergeSource(varDeclarations) {\n
\t    var isSimple = this.environment.isSimple,\n
\t        appendOnly = !this.forceBuffer,\n
\t        appendFirst = undefined,\n
\t        sourceSeen = undefined,\n
\t        bufferStart = undefined,\n
\t        bufferEnd = undefined;\n
\t    this.source.each(function (line) {\n
\t      if (line.appendToBuffer) {\n
\t        if (bufferStart) {\n
\t          line.prepend(\'  + \');\n
\t        } else {\n
\t          bufferStart = line;\n
\t        }\n
\t        bufferEnd = line;\n
\t      } else {\n
\t        if (bufferStart) {\n
\t          if (!sourceSeen) {\n
\t            appendFirst = true;\n
\t          } else {\n
\t            bufferStart.prepend(\'buffer += \');\n
\t          }\n
\t          bufferEnd.add(\';\');\n
\t          bufferStart = bufferEnd = undefined;\n
\t        }\n
\n
\t        sourceSeen = true;\n
\t        if (!isSimple) {\n
\t          appendOnly = false;\n
\t        }\n
\t      }\n
\t    });\n
\n
\t    if (appendOnly) {\n
\t      if (bufferStart) {\n
\t        bufferStart.prepend(\'return \');\n
\t        bufferEnd.add(\';\');\n
\t      } else if (!sourceSeen) {\n
\t        this.source.push(\'return "";\');\n
\t      }\n
\t    } else {\n
\t      varDeclarations += \', buffer = \' + (appendFirst ? \'\' : this.initializeBuffer());\n
\n
\t      if (bufferStart) {\n
\t        bufferStart.prepend(\'return buffer + \');\n
\t        bufferEnd.add(\';\');\n
\t      } else {\n
\t        this.source.push(\'return buffer;\');\n
\t      }\n
\t    }\n
\n
\t    if (varDeclarations) {\n
\t      this.source.prepend(\'var \' + varDeclarations.substring(2) + (appendFirst ? \'\' : \';\\n\'));\n
\t    }\n
\n
\t    return this.source.merge();\n
\t  },\n
\n
\t  // [blockValue]\n
\t  //\n
\t  // On stack, before: hash, inverse, program, value\n
\t  // On stack, after: return value of blockHelperMissing\n
\t  //\n
\t  // The purpose of this opcode is to take a block of the form\n
\t  // `{{#this.foo}}...{{/this.foo}}`, resolve the value of `foo`, and\n
\t  // replace it on the stack with the result of properly\n
\t  // invoking blockHelperMissing.\n
\t  blockValue: function blockValue(name) {\n
\t    var blockHelperMissing = this.aliasable(\'helpers.blockHelperMissing\'),\n
\t        params = [this.contextName(0)];\n
\t    this.setupHelperArgs(name, 0, params);\n
\n
\t    var blockName = this.popStack();\n
\t    params.splice(1, 0, blockName);\n
\n
\t    this.push(this.source.functionCall(blockHelperMissing, \'call\', params));\n
\t  },\n
\n
\t  // [ambiguousBlockValue]\n
\t  //\n
\t  // On stack, before: hash, inverse, program, value\n
\t  // Compiler value, before: lastHelper=value of last found helper, if any\n
\t  // On stack, after, if no lastHelper: same as [blockValue]\n
\t  // On stack, after, if lastHelper: value\n
\t  ambiguousBlockValue: function ambiguousBlockValue() {\n
\t    // We\'re being a bit cheeky and reusing the options value from the prior exec\n
\t    var blockHelperMissing = this.aliasable(\'helpers.blockHelperMissing\'),\n
\t        params = [this.contextName(0)];\n
\t    this.setupHelperArgs(\'\', 0, params, true);\n
\n
\t    this.flushInline();\n
\n
\t    var current = this.topStack();\n
\t    params.splice(1, 0, current);\n
\n
\t    this.pushSource([\'if (!\', this.lastHelper, \') { \', current, \' = \', this.source.functionCall(blockHelperMissing, \'call\', params), \'}\']);\n
\t  },\n
\n
\t  // [appendContent]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: ...\n
\t  //\n
\t  // Appends the string value of `content` to the current buffer\n
\t  appendContent: function appendContent(content) {\n
\t    if (this.pendingContent) {\n
\t      content = this.pendingContent + content;\n
\t    } else {\n
\t      this.pendingLocation = this.source.currentLocation;\n
\t    }\n
\n
\t    this.pendingContent = content;\n
\t  },\n
\n
\t  // [append]\n
\t  //\n
\t  // On stack, before: value, ...\n
\t  // On stack, after: ...\n
\t  //\n
\t  // Coerces `value` to a String and appends it to the current buffer.\n
\t  //\n
\t  // If `value` is truthy, or 0, it is coerced into a string and appended\n
\t  // Otherwise, the empty string is appended\n
\t  append: function append() {\n
\t    if (this.isInline()) {\n
\t      this.replaceStack(function (current) {\n
\t        return [\' != null ? \', current, \' : ""\'];\n
\t      });\n
\n
\t      this.pushSource(this.appendToBuffer(this.popStack()));\n
\t    } else {\n
\t      var local = this.popStack();\n
\t      this.pushSource([\'if (\', local, \' != null) { \', this.appendToBuffer(local, undefined, true), \' }\']);\n
\t      if (this.environment.isSimple) {\n
\t        this.pushSource([\'else { \', this.appendToBuffer("\'\'", undefined, true), \' }\']);\n
\t      }\n
\t    }\n
\t  },\n
\n
\t  // [appendEscaped]\n
\t  //\n
\t  // On stack, before: value, ...\n
\t  // On stack, after: ...\n
\t  //\n
\t  // Escape `value` and append it to the buffer\n
\t  appendEscaped: function appendEscaped() {\n
\t    this.pushSource(this.appendToBuffer([this.aliasable(\'container.escapeExpression\'), \'(\', this.popStack(), \')\']));\n
\t  },\n
\n
\t  // [getContext]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: ...\n
\t  // Compiler value, after: lastContext=depth\n
\t  //\n
\t  // Set the value of the `lastContext` compiler value to the depth\n
\t  getContext: function getContext(depth) {\n
\t    this.lastContext = depth;\n
\t  },\n
\n
\t  // [pushContext]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: currentContext, ...\n
\t  //\n
\t  // Pushes the value of the current context onto the stack.\n
\t  pushContext: function pushContext() {\n
\t    this.pushStackLiteral(this.contextName(this.lastContext));\n
\t  },\n
\n
\t  // [lookupOnContext]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: currentContext[name], ...\n
\t  //\n
\t  // Looks up the value of `name` on the current context and pushes\n
\t  // it onto the stack.\n
\t  lookupOnContext: function lookupOnContext(parts, falsy, strict, scoped) {\n
\t    var i = 0;\n
\n
\t    if (!scoped && this.options.compat && !this.lastContext) {\n
\t      // The depthed query is expected to handle the undefined logic for the root level that\n
\t      // is implemented below, so we evaluate that directly in compat mode\n
\t      this.push(this.depthedLookup(parts[i++]));\n
\t    } else {\n
\t      this.pushContext();\n
\t    }\n
\n
\t    this.resolvePath(\'context\', parts, i, falsy, strict);\n
\t  },\n
\n
\t  // [lookupBlockParam]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: blockParam[name], ...\n
\t  //\n
\t  // Looks up the value of `parts` on the given block param and pushes\n
\t  // it onto the stack.\n
\t  lookupBlockParam: function lookupBlockParam(blockParamId, parts) {\n
\t    this.useBlockParams = true;\n
\n
\t    this.push([\'blockParams[\', blockParamId[0], \'][\', blockParamId[1], \']\']);\n
\t    this.resolvePath(\'context\', parts, 1);\n
\t  },\n
\n
\t  // [lookupData]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: data, ...\n
\t  //\n
\t  // Push the data lookup operator\n
\t  lookupData: function lookupData(depth, parts, strict) {\n
\t    if (!depth) {\n
\t      this.pushStackLiteral(\'data\');\n
\t    } else {\n
\t      this.pushStackLiteral(\'container.data(data, \' + depth + \')\');\n
\t    }\n
\n
\t    this.resolvePath(\'data\', parts, 0, true, strict);\n
\t  },\n
\n
\t  resolvePath: function resolvePath(type, parts, i, falsy, strict) {\n
\t    // istanbul ignore next\n
\n
\t    var _this = this;\n
\n
\t    if (this.options.strict || this.options.assumeObjects) {\n
\t      this.push(strictLookup(this.options.strict && strict, this, parts, type));\n
\t      return;\n
\t    }\n
\n
\t    var len = parts.length;\n
\t    for (; i < len; i++) {\n
\t      /* eslint-disable no-loop-func */\n
\t      this.replaceStack(function (current) {\n
\t        var lookup = _this.nameLookup(current, parts[i], type);\n
\t        // We want to ensure that zero and false are handled properly if the context (falsy flag)\n
\t        // needs to have the special handling for these values.\n
\t        if (!falsy) {\n
\t          return [\' != null ? \', lookup, \' : \', current];\n
\t        } else {\n
\t          // Otherwise we can use generic falsy handling\n
\t          return [\' && \', lookup];\n
\t        }\n
\t      });\n
\t      /* eslint-enable no-loop-func */\n
\t    }\n
\t  },\n
\n
\t  // [resolvePossibleLambda]\n
\t  //\n
\t  // On stack, before: value, ...\n
\t  // On stack, after: resolved value, ...\n
\t  //\n
\t  // If the `value` is a lambda, replace it on the stack by\n
\t  // the return value of the lambda\n
\t  resolvePossibleLambda: function resolvePossibleLambda() {\n
\t    this.push([this.aliasable(\'container.lambda\'), \'(\', this.popStack(), \', \', this.contextName(0), \')\']);\n
\t  },\n
\n
\t  // [pushStringParam]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: string, currentContext, ...\n
\t  //\n
\t  // This opcode is designed for use in string mode, which\n
\t  // provides the string value of a parameter along with its\n
\t  // depth rather than resolving it immediately.\n
\t  pushStringParam: function pushStringParam(string, type) {\n
\t    this.pushContext();\n
\t    this.pushString(type);\n
\n
\t    // If it\'s a subexpression, the string result\n
\t    // will be pushed after this opcode.\n
\t    if (type !== \'SubExpression\') {\n
\t      if (typeof string === \'string\') {\n
\t        this.pushString(string);\n
\t      } else {\n
\t        this.pushStackLiteral(string);\n
\t      }\n
\t    }\n
\t  },\n
\n
\t  emptyHash: function emptyHash(omitEmpty) {\n
\t    if (this.trackIds) {\n
\t      this.push(\'{}\'); // hashIds\n
\t    }\n
\t    if (this.stringParams) {\n
\t      this.push(\'{}\'); // hashContexts\n
\t      this.push(\'{}\'); // hashTypes\n
\t    }\n
\t    this.pushStackLiteral(omitEmpty ? \'undefined\' : \'{}\');\n
\t  },\n
\t  pushHash: function pushHash() {\n
\t    if (this.hash) {\n
\t      this.hashes.push(this.hash);\n
\t    }\n
\t    this.hash = { values: [], types: [], contexts: [], ids: [] };\n
\t  },\n
\t  popHash: function popHash() {\n
\t    var hash = this.hash;\n
\t    this.hash = this.hashes.pop();\n
\n
\t    if (this.trackIds) {\n
\t      this.push(this.objectLiteral(hash.ids));\n
\t    }\n
\t    if (this.stringParams) {\n
\t      this.push(this.objectLiteral(hash.contexts));\n
\t      this.push(this.objectLiteral(hash.types));\n
\t    }\n
\n
\t    this.push(this.objectLiteral(hash.values));\n
\t  },\n
\n
\t  // [pushString]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: quotedString(string), ...\n
\t  //\n
\t  // Push a quoted version of `string` onto the stack\n
\t  pushString: function pushString(string) {\n
\t    this.pushStackLiteral(this.quotedString(string));\n
\t  },\n
\n
\t  // [pushLiteral]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: value, ...\n
\t  //\n
\t  // Pushes a value onto the stack. This operation prevents\n
\t  // the compiler from creating a temporary variable to hold\n
\t  // it.\n
\t  pushLiteral: function pushLiteral(value) {\n
\t    this.pushStackLiteral(value);\n
\t  },\n
\n
\t  // [pushProgram]\n
\t  //\n
\t  // On stack, before: ...\n
\t  // On stack, after: program(guid), ...\n
\t  //\n
\t  // Push a program expression onto the stack. This takes\n
\t  // a compile-time guid and converts it into a runtime-accessible\n
\t  // expression.\n
\t  pushProgram: function pushProgram(guid) {\n
\t    if (guid != null) {\n
\t      this.pushStackLiteral(this.programExpression(guid));\n
\t    } else {\n
\t      this.pushStackLiteral(null);\n
\t    }\n
\t  },\n
\n
\t  // [registerDecorator]\n
\t  //\n
\t  // On stack, before: hash, program, params..., ...\n
\t  // On stack, after: ...\n
\t  //\n
\t  // Pops off the decorator\'s parameters, invokes the decorator,\n
\t  // and inserts the decorator into the decorators list.\n
\t  registerDecorator: function registerDecorator(paramSize, name) {\n
\t    var foundDecorator = this.nameLookup(\'decorators\', name, \'decorator\'),\n
\t        options = this.setupHelperArgs(name, paramSize);\n
\n
\t    this.decorators.push([\'fn = \', this.decorators.functionCall(foundDecorator, \'\', [\'fn\', \'props\', \'container\', options]), \' || fn;\']);\n
\t  },\n
\n
\t  // [invokeHelper]\n
\t  //\n
\t  // On stack, before: hash, inverse, program, params..., ...\n
\t  // On stack, after: result of helper invocation\n
\t  //\n
\t  // Pops off the helper\'s parameters, invokes the helper,\n
\t  // and pushes the helper\'s return value onto the stack.\n
\t  //\n
\t  // If the helper is not found, `helperMissing` is called.\n
\t  invokeHelper: function invokeHelper(paramSize, name, isSimple) {\n
\t    var nonHelper = this.popStack(),\n
\t        helper = this.setupHelper(paramSize, name),\n
\t        simple = isSimple ? [helper.name, \' || \'] : \'\';\n
\n
\t    var lookup = [\'(\'].concat(simple, nonHelper);\n
\t    if (!this.options.strict) {\n
\t      lookup.push(\' || \', this.aliasable(\'helpers.helperMissing\'));\n
\t    }\n
\t    lookup.push(\')\');\n
\n
\t    this.push(this.source.functionCall(lookup, \'call\', helper.callParams));\n
\t  },\n
\n
\t  // [invokeKnownHelper]\n
\t  //\n
\t  // On stack, before: hash, inverse, program, params..., ...\n
\t  // On stack, after: result of helper invocation\n
\t  //\n
\t  // This operation is used when the helper is known to exist,\n
\t  // so a `helperMissing` fallback is not required.\n
\t  invokeKnownHelper: function invokeKnownHelper(paramSize, name) {\n
\t    var helper = this.setupHelper(paramSize, name);\n
\t    this.push(this.source.functionCall(helper.name, \'call\', helper.callParams));\n
\t  },\n
\n
\t  // [invokeAmbiguous]\n
\t  //\n
\t  // On stack, before: hash, inverse, program, params..., ...\n
\t  // On stack, after: result of disambiguation\n
\t  //\n
\t  // This operation is used when an expression like `{{foo}}`\n
\t  // is provided, but we don\'t know at compile-time whether it\n
\t  // is a helper or a path.\n
\t  //\n
\t  // This operation emits more code than the other options,\n
\t  // and can be avoided by passing the `knownHelpers` and\n
\t  // `knownHelpersOnly` flags at compile-time.\n
\t  invokeAmbiguous: function invokeAmbiguous(name, helperCall) {\n
\t    this.useRegister(\'helper\');\n
\n
\t    var nonHelper = this.popStack();\n
\n
\t    this.emptyHash();\n
\t    var helper = this.setupHelper(0, name, helperCall);\n
\n
\t    var helperName = this.lastHelper = this.nameLookup(\'helpers\', name, \'helper\');\n
\n
\t    var lookup = [\'(\', \'(helper = \', helperName, \' || \', nonHelper, \')\'];\n
\t    if (!this.options.strict) {\n
\t      lookup[0] = \'(helper = \';\n
\t      lookup.push(\' != null ? helper : \', this.aliasable(\'helpers.helperMissing\'));\n
\t    }\n
\n
\t    this.push([\'(\', lookup, helper.paramsInit ? [\'),(\', helper.paramsInit] : [], \'),\', \'(typeof helper === \', this.aliasable(\'"function"\'), \' ? \', this.source.functionCall(\'helper\', \'call\', helper.callParams), \' : helper))\']);\n
\t  },\n
\n
\t  // [invokePartial]\n
\t  //\n
\t  // On stack, before: context, ...\n
\t  // On stack after: result of partial invocation\n
\t  //\n
\t  // This operation pops off a context, invokes a partial with that context,\n
\t  // and pushes the result of the invocation back.\n
\t  invokePartial: function invokePartial(isDynamic, name, indent) {\n
\t    var params = [],\n
\t        options = this.setupParams(name, 1, params);\n
\n
\t    if (isDynamic) {\n
\t      name = this.popStack();\n
\t      delete options.name;\n
\t    }\n
\n
\t    if (indent) {\n
\t      options.indent = JSON.stringify(indent);\n
\t    }\n
\t    options.helpers = \'helpers\';\n
\t    options.partials = \'partials\';\n
\t    options.decorators = \'container.decorators\';\n
\n
\t    if (!isDynamic) {\n
\t      params.unshift(this.nameLookup(\'partials\', name, \'partial\'));\n
\t    } else {\n
\t      params.unshift(name);\n
\t    }\n
\n
\t    if (this.options.compat) {\n
\t      options.depths = \'depths\';\n
\t    }\n
\t    options = this.objectLiteral(options);\n
\t    params.push(options);\n
\n
\t    this.push(this.source.functionCall(\'container.invokePartial\', \'\', params));\n
\t  },\n
\n
\t  // [assignToHash]\n
\t  //\n
\t  // On stack, before: value, ..., hash, ...\n
\t  // On stack, after: ..., hash, ...\n
\t  //\n
\t  // Pops a value off the stack and assigns it to the current hash\n
\t  assignToHash: function assignToHash(key) {\n
\t    var value = this.popStack(),\n
\t        context = undefined,\n
\t        type = undefined,\n
\t        id = undefined;\n
\n
\t    if (this.trackIds) {\n
\t      id = this.popStack();\n
\t    }\n
\t    if (this.stringParams) {\n
\t      type = this.popStack();\n
\t      context = this.popStack();\n
\t    }\n
\n
\t    var hash = this.hash;\n
\t    if (context) {\n
\t      hash.contexts[key] = context;\n
\t    }\n
\t    if (type) {\n
\t      hash.types[key] = type;\n
\t    }\n
\t    if (id) {\n
\t      hash.ids[key] = id;\n
\t    }\n
\t    hash.values[key] = value;\n
\t  },\n
\n
\t  pushId: function pushId(type, name, child) {\n
\t    if (type === \'BlockParam\') {\n
\t      this.pushStackLiteral(\'blockParams[\' + name[0] + \'].path[\' + name[1] + \']\' + (child ? \' + \' + JSON.stringify(\'.\' + child) : \'\'));\n
\t    } else if (type === \'PathExpression\') {\n
\t      this.pushString(name);\n
\t    } else if (type === \'SubExpression\') {\n
\t      this.pushStackLiteral(\'true\');\n
\t    } else {\n
\t      this.pushStackLiteral(\'null\');\n
\t    }\n
\t  },\n
\n
\t  // HELPERS\n
\n
\t  compiler: JavaScriptCompiler,\n
\n
\t  compileChildren: function compileChildren(environment, options) {\n
\t    var children = environment.children,\n
\t        child = undefined,\n
\t        compiler = undefined;\n
\n
\t    for (var i = 0, l = children.length; i < l; i++) {\n
\t      child = children[i];\n
\t      compiler = new this.compiler(); // eslint-disable-line new-cap\n
\n
\t      var index = this.matchExistingProgram(child);\n
\n
\t      if (index == null) {\n
\t        this.context.programs.push(\'\'); // Placeholder to prevent name conflicts for nested children\n
\t        index = this.context.programs.length;\n
\t        child.index = index;\n
\t        child.name = \'program\' + index;\n
\t        this.context.programs[index] = compiler.compile(child, options, this.context, !this.precompile);\n
\t        this.context.decorators[index] = compiler.decorators;\n
\t        this.context.environments[index] = child;\n
\n
\t        this.useDepths = this.useDepths || compiler.useDepths;\n
\t        this.useBlockParams = this.useBlockParams || compiler.useBlockParams;\n
\t      } else {\n
\t        child.index = index;\n
\t        child.name = \'program\' + index;\n
\n
\t        this.useDepths = this.useDepths || child.useDepths;\n
\t        this.useBlockParams = this.useBlockParams || child.useBlockParams;\n
\t      }\n
\t    }\n
\t  },\n
\t  matchExistingProgram: function matchExistingProgram(child) {\n
\t    for (var i = 0, len = this.context.environments.length; i < len; i++) {\n
\t      var environment = this.context.environments[i];\n
\t      if (environment && environment.equals(child)) {\n
\t        return i;\n
\t      }\n
\t    }\n
\t  },\n
\n
\t  programExpression: function programExpression(guid) {\n
\t    var child = this.environment.children[guid],\n
\t        programParams = [child.index, \'data\', child.blockParams];\n
\n
\t    if (this.useBlockParams || this.useDepths) {\n
\t      programParams.push(\'blockParams\');\n
\t    }\n
\t    if (this.useDepths) {\n
\t      programParams.push(\'depths\');\n
\t    }\n
\n
\t    return \'container.program(\' + programParams.join(\', \') + \')\';\n
\t  },\n
\n
\t  useRegister: function useRegister(name) {\n
\t    if (!this.registers[name]) {\n
\t      this.registers[name] = true;\n
\t      this.registers.list.push(name);\n
\t    }\n
\t  },\n
\n
\t  push: function push(expr) {\n
\t    if (!(expr instanceof Literal)) {\n
\t      expr = this.source.wrap(expr);\n
\t    }\n
\n
\t    this.inlineStack.push(expr);\n
\t    return expr;\n
\t  },\n
\n
\t  pushStackLiteral: function pushStackLiteral(item) {\n
\t    this.push(new Literal(item));\n
\t  },\n
\n
\t  pushSource: function pushSource(source) {\n
\t    if (this.pendingContent) {\n
\t      this.source.push(this.appendToBuffer(this.source.quotedString(this.pendingContent), this.pendingLocation));\n
\t      this.pendingContent = undefined;\n
\t    }\n
\n
\t    if (source) {\n
\t      this.source.push(source);\n
\t    }\n
\t  },\n
\n
\t  replaceStack: function replaceStack(callback) {\n
\t    var prefix = [\'(\'],\n
\t        stack = undefined,\n
\t        createdStack = undefined,\n
\t        usedLiteral = undefined;\n
\n
\t    /* istanbul ignore next */\n
\t    if (!this.isInline()) {\n
\t      throw new _exception2[\'default\'](\'replaceStack on non-inline\');\n
\t    }\n
\n
\t    // We want to merge the inline statement into the replacement statement via \',\'\n
\t    var top = this.popStack(true);\n
\n
\t    if (top instanceof Literal) {\n
\t      // Literals do not need to be inlined\n
\t      stack = [top.value];\n
\t      prefix = [\'(\', stack];\n
\t      usedLiteral = true;\n
\t    } else {\n
\t      // Get or create the current stack name for use by the inline\n
\t      createdStack = true;\n
\t      var _name = this.incrStack();\n
\n
\t      prefix = [\'((\', this.push(_name), \' = \', top, \')\'];\n
\t      stack = this.topStack();\n
\t    }\n
\n
\t    var item = callback.call(this, stack);\n
\n
\t    if (!usedLiteral) {\n
\t      this.popStack();\n
\t    }\n
\t    if (createdStack) {\n
\t      this.stackSlot--;\n
\t    }\n
\t    this.push(prefix.concat(item, \')\'));\n
\t  },\n
\n
\t  incrStack: function incrStack() {\n
\t    this.stackSlot++;\n
\t    if (this.stackSlot > this.stackVars.length) {\n
\t      this.stackVars.push(\'stack\' + this.stackSlot);\n
\t    }\n
\t    return this.topStackName();\n
\t  },\n
\t  topStackName: function topStackName() {\n
\t    return \'stack\' + this.stackSlot;\n
\t  },\n
\t  flushInline: function flushInline() {\n
\t    var inlineStack = this.inlineStack;\n
\t    this.inlineStack = [];\n
\t    for (var i = 0, len = inlineStack.length; i < len; i++) {\n
\t      var entry = inlineStack[i];\n
\t      /* istanbul ignore if */\n
\t      if (entry instanceof Literal) {\n
\t        this.compileStack.push(entry);\n
\t      } else {\n
\t        var stack = this.incrStack();\n
\t        this.pushSource([stack, \' = \', entry, \';\']);\n
\t        this.compileStack.push(stack);\n
\t      }\n
\t    }\n
\t  },\n
\t  isInline: function isInline() {\n
\t    return this.inlineStack.length;\n
\t  },\n
\n
\t  popStack: function popStack(wrapped) {\n
\t    var inline = this.isInline(),\n
\t        item = (inline ? this.inlineStack : this.compileStack).pop();\n
\n
\t    if (!wrapped && item instanceof Literal) {\n
\t      return item.value;\n
\t    } else {\n
\t      if (!inline) {\n
\t        /* istanbul ignore next */\n
\t        if (!this.stackSlot) {\n
\t          throw new _exception2[\'default\'](\'Invalid stack pop\');\n
\t        }\n
\t        this.stackSlot--;\n
\t      }\n
\t      return item;\n
\t    }\n
\t  },\n
\n
\t  topStack: function topStack() {\n
\t    var stack = this.isInline() ? this.inlineStack : this.compileStack,\n
\t        item = stack[stack.length - 1];\n
\n
\t    /* istanbul ignore if */\n
\t    if (item instanceof Literal) {\n
\t      return item.value;\n
\t    } else {\n
\t      return item;\n
\t    }\n
\t  },\n
\n
\t  contextName: function contextName(context) {\n
\t    if (this.useDepths && context) {\n
\t      return \'depths[\' + context + \']\';\n
\t    } else {\n
\t      return \'depth\' + context;\n
\t    }\n
\t  },\n
\n
\t  quotedString: function quotedString(str) {\n
\t    return this.source.quotedString(str);\n
\t  },\n
\n
\t  objectLiteral: function objectLiteral(obj) {\n
\t    return this.source.objectLiteral(obj);\n
\t  },\n
\n
\t  aliasable: function aliasable(name) {\n
\t    var ret = this.aliases[name];\n
\t    if (ret) {\n
\t      ret.referenceCount++;\n
\t      return ret;\n
\t    }\n
\n
\t    ret = this.aliases[name] = this.source.wrap(name);\n
\t    ret.aliasable = true;\n
\t    ret.referenceCount = 1;\n
\n
\t    return ret;\n
\t  },\n
\n
\t  setupHelper: function setupHelper(paramSize, name, blockHelper) {\n
\t    var params = [],\n
\t        paramsInit = this.setupHelperArgs(name, paramSize, params, blockHelper);\n
\t    var foundHelper = this.nameLookup(\'helpers\', name, \'helper\'),\n
\t        callContext = this.aliasable(this.contextName(0) + \' != null ? \' + this.contextName(0) + \' : {}\');\n
\n
\t    return {\n
\t      params: params,\n
\t      paramsInit: paramsInit,\n
\t      name: foundHelper,\n
\t      callParams: [callContext].concat(params)\n
\t    };\n
\t  },\n
\n
\t  setupParams: function setupParams(helper, paramSize, params) {\n
\t    var options = {},\n
\t        contexts = [],\n
\t        types = [],\n
\t        ids = [],\n
\t        objectArgs = !params,\n
\t        param = undefined;\n
\n
\t    if (objectArgs) {\n
\t      params = [];\n
\t    }\n
\n
\t    options.name = this.quotedString(helper);\n
\t    options.hash = this.popStack();\n
\n
\t    if (this.trackIds) {\n
\t      options.hashIds = this.popStack();\n
\t    }\n
\t    if (this.stringParams) {\n
\t      options.hashTypes = this.popStack();\n
\t      options.hashContexts = this.popStack();\n
\t    }\n
\n
\t    var inverse = this.popStack(),\n
\t        program = this.popStack();\n
\n
\t    // Avoid setting fn and inverse if neither are set. This allows\n
\t    // helpers to do a check for `if (options.fn)`\n
\t    if (program || inverse) {\n
\t      options.fn = program || \'container.noop\';\n
\t      options.inverse = inverse || \'container.noop\';\n
\t    }\n
\n
\t    // The parameters go on to the stack in order (making sure that they are evaluated in order)\n
\t    // so we need to pop them off the stack in reverse order\n
\t    var i = paramSize;\n
\t    while (i--) {\n
\t      param = this.popStack();\n
\t      params[i] = param;\n
\n
\t      if (this.trackIds) {\n
\t        ids[i] = this.popStack();\n
\t      }\n
\t      if (this.stringParams) {\n
\t        types[i] = this.popStack();\n
\t        contexts[i] = this.popStack();\n
\t      }\n
\t    }\n
\n
\t    if (objectArgs) {\n
\t      options.args = this.source.generateArray(params);\n
\t    }\n
\n
\t    if (this.trackIds) {\n
\t      options.ids = this.source.generateArray(ids);\n
\t    }\n
\t    if (this.stringParams) {\n
\t      options.types = this.source.generateArray(types);\n
\t      options.contexts = this.source.generateArray(contexts);\n
\t    }\n
\n
\t    if (this.options.data) {\n
\t      options.data = \'data\';\n
\t    }\n
\t    if (this.useBlockParams) {\n
\t      options.blockParams = \'blockParams\';\n
\t    }\n
\t    return options;\n
\t  },\n
\n
\t  setupHelperArgs: function setupHelperArgs(helper, paramSize, params, useRegister) {\n
\t    var options = this.setupParams(helper, paramSize, params);\n
\t    options = this.objectLiteral(options);\n
\t    if (useRegister) {\n
\t      this.useRegister(\'options\');\n
\t      params.push(\'options\');\n
\t      return [\'options=\', options];\n
\t    } else if (params) {\n
\t      params.push(options);\n
\t      return \'\';\n
\t    } else {\n
\t      return options;\n
\t    }\n
\t  }\n
\t};\n
\n
\t(function () {\n
\t  var reservedWords = (\'break else new var\' + \' case finally return void\' + \' catch for switch while\' + \' continue function this with\' + \' default if throw\' + \' delete in try\' + \' do instanceof typeof\' + \' abstract enum int short\' + \' boolean export interface static\' + \' byte extends long super\' + \' char final native synchronized\' + \' class float package throws\' + \' const goto private transient\' + \' debugger implements protected volatile\' + \' double import public let yield await\' + \' null true false\').split(\' \');\n
\n
\t  var compilerWords = JavaScriptCompiler.RESERVED_WORDS = {};\n
\n
\t  for (var i = 0, l = reservedWords.length; i < l; i++) {\n
\t    compilerWords[reservedWords[i]] = true;\n
\t  }\n
\t})();\n
\n
\tJavaScriptCompiler.isValidJavaScriptVariableName = function (name) {\n
\t  return !JavaScriptCompiler.RESERVED_WORDS[name] && /^[a-zA-Z_$][0-9a-zA-Z_$]*$/.test(name);\n
\t};\n
\n
\tfunction strictLookup(requireTerminal, compiler, parts, type) {\n
\t  var stack = compiler.popStack(),\n
\t      i = 0,\n
\t      len = parts.length;\n
\t  if (requireTerminal) {\n
\t    len--;\n
\t  }\n
\n
\t  for (; i < len; i++) {\n
\t    stack = compiler.nameLookup(stack, parts[i], type);\n
\t  }\n
\n
\t  if (requireTerminal) {\n
\t    return [compiler.aliasable(\'container.strict\'), \'(\', stack, \', \', compiler.quotedString(parts[i]), \')\'];\n
\t  } else {\n
\t    return stack;\n
\t  }\n
\t}\n
\n
\texports[\'default\'] = JavaScriptCompiler;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ },\n
/* 29 */\n
/***/ function(module, exports, __webpack_require__) {\n
\n
\t/* global define */\n
\t\'use strict\';\n
\n
\texports.__esModule = true;\n
\n
\tvar _utils = __webpack_require__(5);\n
\n
\tvar SourceNode = undefined;\n
\n
\ttry {\n
\t  /* istanbul ignore next */\n
\t  if (false) {\n
\t    // We don\'t support this in AMD environments. For these environments, we asusme that\n
\t    // they are running on the browser and thus have no need for the source-map library.\n
\t    var SourceMap = require(\'source-map\');\n
\t    SourceNode = SourceMap.SourceNode;\n
\t  }\n
\t} catch (err) {}\n
\t/* NOP */\n
\n
\t/* istanbul ignore if: tested but not covered in istanbul due to dist build  */\n
\tif (!SourceNode) {\n
\t  SourceNode = function (line, column, srcFile, chunks) {\n
\t    this.src = \'\';\n
\t    if (chunks) {\n
\t      this.add(chunks);\n
\t    }\n
\t  };\n
\t  /* istanbul ignore next */\n
\t  SourceNode.prototype = {\n
\t    add: function add(chunks) {\n
\t      if (_utils.isArray(chunks)) {\n
\t        chunks = chunks.join(\'\');\n
\t      }\n
\t      this.src += chunks;\n
\t    },\n
\t    prepend: function prepend(chunks) {\n
\t      if (_utils.isArray(chunks)) {\n
\t        chunks = chunks.join(\'\');\n
\t      }\n
\t      this.src = chunks + this.src;\n
\t    },\n
\t    toStringWithSourceMap: function toStringWithSourceMap() {\n
\t      return { code: this.toString() };\n
\t    },\n
\t    toString: function toString() {\n
\t      return this.src;\n
\t    }\n
\t  };\n
\t}\n
\n
\tfunction castChunk(chunk, codeGen, loc) {\n
\t  if (_utils.isArray(chunk)) {\n
\t    var ret = [];\n
\n
\t    for (var i = 0, len = chunk.length; i < len; i++) {\n
\t      ret.push(codeGen.wrap(chunk[i], loc));\n
\t    }\n
\t    return ret;\n
\t  } else if (typeof chunk === \'boolean\' || typeof chunk === \'number\') {\n
\t    // Handle primitives that the SourceNode will throw up on\n
\t    return chunk + \'\';\n
\t  }\n
\t  return chunk;\n
\t}\n
\n
\tfunction CodeGen(srcFile) {\n
\t  this.srcFile = srcFile;\n
\t  this.source = [];\n
\t}\n
\n
\tCodeGen.prototype = {\n
\t  isEmpty: function isEmpty() {\n
\t    return !this.source.length;\n
\t  },\n
\t  prepend: function prepend(source, loc) {\n
\t    this.source.unshift(this.wrap(source, loc));\n
\t  },\n
\t  push: function push(source, loc) {\n
\t    this.source.push(this.wrap(source, loc));\n
\t  },\n
\n
\t  merge: function merge() {\n
\t    var source = this.empty();\n
\t    this.each(function (line) {\n
\t      source.add([\'  \', line, \'\\n\']);\n
\t    });\n
\t    return source;\n
\t  },\n
\n
\t  each: function each(iter) {\n
\t    for (var i = 0, len = this.source.length; i < len; i++) {\n
\t      iter(this.source[i]);\n
\t    }\n
\t  },\n
\n
\t  empty: function empty() {\n
\t    var loc = this.currentLocation || { start: {} };\n
\t    return new SourceNode(loc.start.line, loc.start.column, this.srcFile);\n
\t  },\n
\t  wrap: function wrap(chunk) {\n
\t    var loc = arguments.length <= 1 || arguments[1] === undefined ? this.currentLocation || { start: {} } : arguments[1];\n
\n
\t    if (chunk instanceof SourceNode) {\n
\t      return chunk;\n
\t    }\n
\n
\t    chunk = castChunk(chunk, this, loc);\n
\n
\t    return new SourceNode(loc.start.line, loc.start.column, this.srcFile, chunk);\n
\t  },\n
\n
\t  functionCall: function functionCall(fn, type, params) {\n
\t    params = this.generateList(params);\n
\t    return this.wrap([fn, type ? \'.\' + type + \'(\' : \'(\', params, \')\']);\n
\t  },\n
\n
\t  quotedString: function quotedString(str) {\n
\t    return \'"\' + (str + \'\').replace(/\\\\/g, \'\\\\\\\\\').replace(/"/g, \'\\\\"\').replace(/\\n/g, \'\\\\n\').replace(/\\r/g, \'\\\\r\').replace(/\\u2028/g, \'\\\\u2028\') // Per Ecma-262 7.3 + 7.8.4\n
\t    .replace(/\\u2029/g, \'\\\\u2029\') + \'"\';\n
\t  },\n
\n
\t  objectLiteral: function objectLiteral(obj) {\n
\t    var pairs = [];\n
\n
\t    for (var key in obj) {\n
\t      if (obj.hasOwnProperty(key)) {\n
\t        var value = castChunk(obj[key], this);\n
\t        if (value !== \'undefined\') {\n
\t          pairs.push([this.quotedString(key), \':\', value]);\n
\t        }\n
\t      }\n
\t    }\n
\n
\t    var ret = this.generateList(pairs);\n
\t    ret.prepend(\'{\');\n
\t    ret.add(\'}\');\n
\t    return ret;\n
\t  },\n
\n
\t  generateList: function generateList(entries) {\n
\t    var ret = this.empty();\n
\n
\t    for (var i = 0, len = entries.length; i < len; i++) {\n
\t      if (i) {\n
\t        ret.add(\',\');\n
\t      }\n
\n
\t      ret.add(castChunk(entries[i], this));\n
\t    }\n
\n
\t    return ret;\n
\t  },\n
\n
\t  generateArray: function generateArray(entries) {\n
\t    var ret = this.generateList(entries);\n
\t    ret.prepend(\'[\');\n
\t    ret.add(\']\');\n
\n
\t    return ret;\n
\t  }\n
\t};\n
\n
\texports[\'default\'] = CodeGen;\n
\tmodule.exports = exports[\'default\'];\n
\n
/***/ }\n
/******/ ])\n
});\n
;

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>159586</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
