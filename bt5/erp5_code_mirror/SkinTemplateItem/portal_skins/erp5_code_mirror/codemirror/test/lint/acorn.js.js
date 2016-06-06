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
            <value> <string>ts21897152.05</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>acorn.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>69379</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// Acorn is a tiny, fast JavaScript parser written in JavaScript.\n
//\n
// Acorn was written by Marijn Haverbeke and released under an MIT\n
// license. The Unicode regexps (for identifiers and whitespace) were\n
// taken from [Esprima](http://esprima.org) by Ariya Hidayat.\n
//\n
// Git repositories for Acorn are available at\n
//\n
//     http://marijnhaverbeke.nl/git/acorn\n
//     https://github.com/marijnh/acorn.git\n
//\n
// Please use the [github bug tracker][ghbt] to report issues.\n
//\n
// [ghbt]: https://github.com/marijnh/acorn/issues\n
//\n
// This file defines the main parser interface. The library also comes\n
// with a [error-tolerant parser][dammit] and an\n
// [abstract syntax tree walker][walk], defined in other files.\n
//\n
// [dammit]: acorn_loose.js\n
// [walk]: util/walk.js\n
\n
(function(root, mod) {\n
  if (typeof exports == "object" && typeof module == "object") return mod(exports); // CommonJS\n
  if (typeof define == "function" && define.amd) return define(["exports"], mod); // AMD\n
  mod(root.acorn || (root.acorn = {})); // Plain browser env\n
})(this, function(exports) {\n
  "use strict";\n
\n
  exports.version = "0.4.1";\n
\n
  // The main exported interface (under `self.acorn` when in the\n
  // browser) is a `parse` function that takes a code string and\n
  // returns an abstract syntax tree as specified by [Mozilla parser\n
  // API][api], with the caveat that the SpiderMonkey-specific syntax\n
  // (`let`, `yield`, inline XML, etc) is not recognized.\n
  //\n
  // [api]: https://developer.mozilla.org/en-US/docs/SpiderMonkey/Parser_API\n
\n
  var options, input, inputLen, sourceFile;\n
\n
  exports.parse = function(inpt, opts) {\n
    input = String(inpt); inputLen = input.length;\n
    setOptions(opts);\n
    initTokenState();\n
    return parseTopLevel(options.program);\n
  };\n
\n
  // A second optional argument can be given to further configure\n
  // the parser process. These options are recognized:\n
\n
  var defaultOptions = exports.defaultOptions = {\n
    // `ecmaVersion` indicates the ECMAScript version to parse. Must\n
    // be either 3 or 5. This\n
    // influences support for strict mode, the set of reserved words, and\n
    // support for getters and setter.\n
    ecmaVersion: 5,\n
    // Turn on `strictSemicolons` to prevent the parser from doing\n
    // automatic semicolon insertion.\n
    strictSemicolons: false,\n
    // When `allowTrailingCommas` is false, the parser will not allow\n
    // trailing commas in array and object literals.\n
    allowTrailingCommas: true,\n
    // By default, reserved words are not enforced. Enable\n
    // `forbidReserved` to enforce them. When this option has the\n
    // value "everywhere", reserved words and keywords can also not be\n
    // used as property names.\n
    forbidReserved: false,\n
    // When enabled, a return at the top level is not considered an\n
    // error.\n
    allowReturnOutsideFunction: false,\n
    // When `locations` is on, `loc` properties holding objects with\n
    // `start` and `end` properties in `{line, column}` form (with\n
    // line being 1-based and column 0-based) will be attached to the\n
    // nodes.\n
    locations: false,\n
    // A function can be passed as `onComment` option, which will\n
    // cause Acorn to call that function with `(block, text, start,\n
    // end)` parameters whenever a comment is skipped. `block` is a\n
    // boolean indicating whether this is a block (`/* */`) comment,\n
    // `text` is the content of the comment, and `start` and `end` are\n
    // character offsets that denote the start and end of the comment.\n
    // When the `locations` option is on, two more parameters are\n
    // passed, the full `{line, column}` locations of the start and\n
    // end of the comments. Note that you are not allowed to call the\n
    // parser from the callback—that will corrupt its internal state.\n
    onComment: null,\n
    // Nodes have their start and end characters offsets recorded in\n
    // `start` and `end` properties (directly on the node, rather than\n
    // the `loc` object, which holds line/column data. To also add a\n
    // [semi-standardized][range] `range` property holding a `[start,\n
    // end]` array with the same numbers, set the `ranges` option to\n
    // `true`.\n
    //\n
    // [range]: https://bugzilla.mozilla.org/show_bug.cgi?id=745678\n
    ranges: false,\n
    // It is possible to parse multiple files into a single AST by\n
    // passing the tree produced by parsing the first file as\n
    // `program` option in subsequent parses. This will add the\n
    // toplevel forms of the parsed file to the `Program` (top) node\n
    // of an existing parse tree.\n
    program: null,\n
    // When `locations` is on, you can pass this to record the source\n
    // file in every node\'s `loc` object.\n
    sourceFile: null,\n
    // This value, if given, is stored in every node, whether\n
    // `locations` is on or off.\n
    directSourceFile: null\n
  };\n
\n
  function setOptions(opts) {\n
    options = opts || {};\n
    for (var opt in defaultOptions) if (!Object.prototype.hasOwnProperty.call(options, opt))\n
      options[opt] = defaultOptions[opt];\n
    sourceFile = options.sourceFile || null;\n
  }\n
\n
  // The `getLineInfo` function is mostly useful when the\n
  // `locations` option is off (for performance reasons) and you\n
  // want to find the line/column position for a given character\n
  // offset. `input` should be the code string that the offset refers\n
  // into.\n
\n
  var getLineInfo = exports.getLineInfo = function(input, offset) {\n
    for (var line = 1, cur = 0;;) {\n
      lineBreak.lastIndex = cur;\n
      var match = lineBreak.exec(input);\n
      if (match && match.index < offset) {\n
        ++line;\n
        cur = match.index + match[0].length;\n
      } else break;\n
    }\n
    return {line: line, column: offset - cur};\n
  };\n
\n
  // Acorn is organized as a tokenizer and a recursive-descent parser.\n
  // The `tokenize` export provides an interface to the tokenizer.\n
  // Because the tokenizer is optimized for being efficiently used by\n
  // the Acorn parser itself, this interface is somewhat crude and not\n
  // very modular. Performing another parse or call to `tokenize` will\n
  // reset the internal state, and invalidate existing tokenizers.\n
\n
  exports.tokenize = function(inpt, opts) {\n
    input = String(inpt); inputLen = input.length;\n
    setOptions(opts);\n
    initTokenState();\n
\n
    var t = {};\n
    function getToken(forceRegexp) {\n
      lastEnd = tokEnd;\n
      readToken(forceRegexp);\n
      t.start = tokStart; t.end = tokEnd;\n
      t.startLoc = tokStartLoc; t.endLoc = tokEndLoc;\n
      t.type = tokType; t.value = tokVal;\n
      return t;\n
    }\n
    getToken.jumpTo = function(pos, reAllowed) {\n
      tokPos = pos;\n
      if (options.locations) {\n
        tokCurLine = 1;\n
        tokLineStart = lineBreak.lastIndex = 0;\n
        var match;\n
        while ((match = lineBreak.exec(input)) && match.index < pos) {\n
          ++tokCurLine;\n
          tokLineStart = match.index + match[0].length;\n
        }\n
      }\n
      tokRegexpAllowed = reAllowed;\n
      skipSpace();\n
    };\n
    return getToken;\n
  };\n
\n
  // State is kept in (closure-)global variables. We already saw the\n
  // `options`, `input`, and `inputLen` variables above.\n
\n
  // The current position of the tokenizer in the input.\n
\n
  var tokPos;\n
\n
  // The start and end offsets of the current token.\n
\n
  var tokStart, tokEnd;\n
\n
  // When `options.locations` is true, these hold objects\n
  // containing the tokens start and end line/column pairs.\n
\n
  var tokStartLoc, tokEndLoc;\n
\n
  // The type and value of the current token. Token types are objects,\n
  // named by variables against which they can be compared, and\n
  // holding properties that describe them (indicating, for example,\n
  // the precedence of an infix operator, and the original name of a\n
  // keyword token). The kind of value that\'s held in `tokVal` depends\n
  // on the type of the token. For literals, it is the literal value,\n
  // for operators, the operator name, and so on.\n
\n
  var tokType, tokVal;\n
\n
  // Interal state for the tokenizer. To distinguish between division\n
  // operators and regular expressions, it remembers whether the last\n
  // token was one that is allowed to be followed by an expression.\n
  // (If it is, a slash is probably a regexp, if it isn\'t it\'s a\n
  // division operator. See the `parseStatement` function for a\n
  // caveat.)\n
\n
  var tokRegexpAllowed;\n
\n
  // When `options.locations` is true, these are used to keep\n
  // track of the current line, and know when a new line has been\n
  // entered.\n
\n
  var tokCurLine, tokLineStart;\n
\n
  // These store the position of the previous token, which is useful\n
  // when finishing a node and assigning its `end` position.\n
\n
  var lastStart, lastEnd, lastEndLoc;\n
\n
  // This is the parser\'s state. `inFunction` is used to reject\n
  // `return` statements outside of functions, `labels` to verify that\n
  // `break` and `continue` have somewhere to jump to, and `strict`\n
  // indicates whether strict mode is on.\n
\n
  var inFunction, labels, strict;\n
\n
  // This function is used to raise exceptions on parse errors. It\n
  // takes an offset integer (into the current `input`) to indicate\n
  // the location of the error, attaches the position to the end\n
  // of the error message, and then raises a `SyntaxError` with that\n
  // message.\n
\n
  function raise(pos, message) {\n
    var loc = getLineInfo(input, pos);\n
    message += " (" + loc.line + ":" + loc.column + ")";\n
    var err = new SyntaxError(message);\n
    err.pos = pos; err.loc = loc; err.raisedAt = tokPos;\n
    throw err;\n
  }\n
\n
  // Reused empty array added for node fields that are always empty.\n
\n
  var empty = [];\n
\n
  // ## Token types\n
\n
  // The assignment of fine-grained, information-carrying type objects\n
  // allows the tokenizer to store the information it has about a\n
  // token in a way that is very cheap for the parser to look up.\n
\n
  // All token type variables start with an underscore, to make them\n
  // easy to recognize.\n
\n
  // These are the general types. The `type` property is only used to\n
  // make them recognizeable when debugging.\n
\n
  var _num = {type: "num"}, _regexp = {type: "regexp"}, _string = {type: "string"};\n
  var _name = {type: "name"}, _eof = {type: "eof"};\n
\n
  // Keyword tokens. The `keyword` property (also used in keyword-like\n
  // operators) indicates that the token originated from an\n
  // identifier-like word, which is used when parsing property names.\n
  //\n
  // The `beforeExpr` property is used to disambiguate between regular\n
  // expressions and divisions. It is set on all token types that can\n
  // be followed by an expression (thus, a slash after them would be a\n
  // regular expression).\n
  //\n
  // `isLoop` marks a keyword as starting a loop, which is important\n
  // to know when parsing a label, in order to allow or disallow\n
  // continue jumps to that label.\n
\n
  var _break = {keyword: "break"}, _case = {keyword: "case", beforeExpr: true}, _catch = {keyword: "catch"};\n
  var _continue = {keyword: "continue"}, _debugger = {keyword: "debugger"}, _default = {keyword: "default"};\n
  var _do = {keyword: "do", isLoop: true}, _else = {keyword: "else", beforeExpr: true};\n
  var _finally = {keyword: "finally"}, _for = {keyword: "for", isLoop: true}, _function = {keyword: "function"};\n
  var _if = {keyword: "if"}, _return = {keyword: "return", beforeExpr: true}, _switch = {keyword: "switch"};\n
  var _throw = {keyword: "throw", beforeExpr: true}, _try = {keyword: "try"}, _var = {keyword: "var"};\n
  var _while = {keyword: "while", isLoop: true}, _with = {keyword: "with"}, _new = {keyword: "new", beforeExpr: true};\n
  var _this = {keyword: "this"};\n
\n
  // The keywords that denote values.\n
\n
  var _null = {keyword: "null", atomValue: null}, _true = {keyword: "true", atomValue: true};\n
  var _false = {keyword: "false", atomValue: false};\n
\n
  // Some keywords are treated as regular operators. `in` sometimes\n
  // (when parsing `for`) needs to be tested against specifically, so\n
  // we assign a variable name to it for quick comparing.\n
\n
  var _in = {keyword: "in", binop: 7, beforeExpr: true};\n
\n
  // Map keyword names to token types.\n
\n
  var keywordTypes = {"break": _break, "case": _case, "catch": _catch,\n
                      "continue": _continue, "debugger": _debugger, "default": _default,\n
                      "do": _do, "else": _else, "finally": _finally, "for": _for,\n
                      "function": _function, "if": _if, "return": _return, "switch": _switch,\n
                      "throw": _throw, "try": _try, "var": _var, "while": _while, "with": _with,\n
                      "null": _null, "true": _true, "false": _false, "new": _new, "in": _in,\n
                      "instanceof": {keyword: "instanceof", binop: 7, beforeExpr: true}, "this": _this,\n
                      "typeof": {keyword: "typeof", prefix: true, beforeExpr: true},\n
                      "void": {keyword: "void", prefix: true, beforeExpr: true},\n
                      "delete": {keyword: "delete", prefix: true, beforeExpr: true}};\n
\n
  // Punctuation token types. Again, the `type` property is purely for debugging.\n
\n
  var _bracketL = {type: "[", beforeExpr: true}, _bracketR = {type: "]"}, _braceL = {type: "{", beforeExpr: true};\n
  var _braceR = {type: "}"}, _parenL = {type: "(", beforeExpr: true}, _parenR = {type: ")"};\n
  var _comma = {type: ",", beforeExpr: true}, _semi = {type: ";", beforeExpr: true};\n
  var _colon = {type: ":", beforeExpr: true}, _dot = {type: "."}, _question = {type: "?", beforeExpr: true};\n
\n
  // Operators. These carry several kinds of properties to help the\n
  // parser use them properly (the presence of these properties is\n
  // what categorizes them as operators).\n
  //\n
  // `binop`, when present, specifies that this operator is a binary\n
  // operator, and will refer to its precedence.\n
  //\n
  // `prefix` and `postfix` mark the operator as a prefix or postfix\n
  // unary operator. `isUpdate` specifies that the node produced by\n
  // the operator should be of type UpdateExpression rather than\n
  // simply UnaryExpression (`++` and `--`).\n
  //\n
  // `isAssign` marks all of `=`, `+=`, `-=` etcetera, which act as\n
  // binary operators with a very low precedence, that should result\n
  // in AssignmentExpression nodes.\n
\n
  var _slash = {binop: 10, beforeExpr: true}, _eq = {isAssign: true, beforeExpr: true};\n
  var _assign = {isAssign: true, beforeExpr: true};\n
  var _incDec = {postfix: true, prefix: true, isUpdate: true}, _prefix = {prefix: true, beforeExpr: true};\n
  var _logicalOR = {binop: 1, beforeExpr: true};\n
  var _logicalAND = {binop: 2, beforeExpr: true};\n
  var _bitwiseOR = {binop: 3, beforeExpr: true};\n
  var _bitwiseXOR = {binop: 4, beforeExpr: true};\n
  var _bitwiseAND = {binop: 5, beforeExpr: true};\n
  var _equality = {binop: 6, beforeExpr: true};\n
  var _relational = {binop: 7, beforeExpr: true};\n
  var _bitShift = {binop: 8, beforeExpr: true};\n
  var _plusMin = {binop: 9, prefix: true, beforeExpr: true};\n
  var _multiplyModulo = {binop: 10, beforeExpr: true};\n
\n
  // Provide access to the token types for external users of the\n
  // tokenizer.\n
\n
  exports.tokTypes = {bracketL: _bracketL, bracketR: _bracketR, braceL: _braceL, braceR: _braceR,\n
                      parenL: _parenL, parenR: _parenR, comma: _comma, semi: _semi, colon: _colon,\n
                      dot: _dot, question: _question, slash: _slash, eq: _eq, name: _name, eof: _eof,\n
                      num: _num, regexp: _regexp, string: _string};\n
  for (var kw in keywordTypes) exports.tokTypes["_" + kw] = keywordTypes[kw];\n
\n
  // This is a trick taken from Esprima. It turns out that, on\n
  // non-Chrome browsers, to check whether a string is in a set, a\n
  // predicate containing a big ugly `switch` statement is faster than\n
  // a regular expression, and on Chrome the two are about on par.\n
  // This function uses `eval` (non-lexical) to produce such a\n
  // predicate from a space-separated string of words.\n
  //\n
  // It starts by sorting the words by length.\n
\n
  function makePredicate(words) {\n
    words = words.split(" ");\n
    var f = "", cats = [];\n
    out: for (var i = 0; i < words.length; ++i) {\n
      for (var j = 0; j < cats.length; ++j)\n
        if (cats[j][0].length == words[i].length) {\n
          cats[j].push(words[i]);\n
          continue out;\n
        }\n
      cats.push([words[i]]);\n
    }\n
    function compareTo(arr) {\n
      if (arr.length == 1) return f += "return str === " + JSON.stringify(arr[0]) + ";";\n
      f += "switch(str){";\n
      for (var i = 0; i < arr.length; ++i) f += "case " + JSON.stringify(arr[i]) + ":";\n
      f += "return true}return false;";\n
    }\n
\n
    // When there are more than three length categories, an outer\n
    // switch first dispatches on the lengths, to save on comparisons.\n
\n
    if (cats.length > 3) {\n
      cats.sort(function(a, b) {return b.length - a.length;});\n
      f += "switch(str.length){";\n
      for (var i = 0; i < cats.length; ++i) {\n
        var cat = cats[i];\n
        f += "case " + cat[0].length + ":";\n
        compareTo(cat);\n
      }\n
      f += "}";\n
\n
    // Otherwise, simply generate a flat `switch` statement.\n
\n
    } else {\n
      compareTo(words);\n
    }\n
    return new Function("str", f);\n
  }\n
\n
  // The ECMAScript 3 reserved word list.\n
\n
  var isReservedWord3 = makePredicate("abstract boolean byte char class double enum export extends final float goto implements import int interface long native package private protected public short static super synchronized throws transient volatile");\n
\n
  // ECMAScript 5 reserved words.\n
\n
  var isReservedWord5 = makePredicate("class enum extends super const export import");\n
\n
  // The additional reserved words in strict mode.\n
\n
  var isStrictReservedWord = makePredicate("implements interface let package private protected public static yield");\n
\n
  // The forbidden variable names in strict mode.\n
\n
  var isStrictBadIdWord = makePredicate("eval arguments");\n
\n
  // And the keywords.\n
\n
  var isKeyword = makePredicate("break case catch continue debugger default do else finally for function if return switch throw try var while with null true false instanceof typeof void delete new in this");\n
\n
  // ## Character categories\n
\n
  // Big ugly regular expressions that match characters in the\n
  // whitespace, identifier, and identifier-start categories. These\n
  // are only applied when a character is found to actually have a\n
  // code point above 128.\n
\n
  var nonASCIIwhitespace = /[\\u1680\\u180e\\u2000-\\u200a\\u202f\\u205f\\u3000\\ufeff]/;\n
  var nonASCIIidentifierStartChars = "\\xaa\\xb5\\xba\\xc0-\\xd6\\xd8-\\xf6\\xf8-\\u02c1\\u02c6-\\u02d1\\u02e0-\\u02e4\\u02ec\\u02ee\\u0370-\\u0374\\u0376\\u0377\\u037a-\\u037d\\u0386\\u0388-\\u038a\\u038c\\u038e-\\u03a1\\u03a3-\\u03f5\\u03f7-\\u0481\\u048a-\\u0527\\u0531-\\u0556\\u0559\\u0561-\\u0587\\u05d0-\\u05ea\\u05f0-\\u05f2\\u0620-\\u064a\\u066e\\u066f\\u0671-\\u06d3\\u06d5\\u06e5\\u06e6\\u06ee\\u06ef\\u06fa-\\u06fc\\u06ff\\u0710\\u0712-\\u072f\\u074d-\\u07a5\\u07b1\\u07ca-\\u07ea\\u07f4\\u07f5\\u07fa\\u0800-\\u0815\\u081a\\u0824\\u0828\\u0840-\\u0858\\u08a0\\u08a2-\\u08ac\\u0904-\\u0939\\u093d\\u0950\\u0958-\\u0961\\u0971-\\u0977\\u0979-\\u097f\\u0985-\\u098c\\u098f\\u0990\\u0993-\\u09a8\\u09aa-\\u09b0\\u09b2\\u09b6-\\u09b9\\u09bd\\u09ce\\u09dc\\u09dd\\u09df-\\u09e1\\u09f0\\u09f1\\u0a05-\\u0a0a\\u0a0f\\u0a10\\u0a13-\\u0a28\\u0a2a-\\u0a30\\u0a32\\u0a33\\u0a35\\u0a36\\u0a38\\u0a39\\u0a59-\\u0a5c\\u0a5e\\u0a72-\\u0a74\\u0a85-\\u0a8d\\u0a8f-\\u0a91\\u0a93-\\u0aa8\\u0aaa-\\u0ab0\\u0ab2\\u0ab3\\u0ab5-\\u0ab9\\u0abd\\u0ad0\\u0ae0\\u0ae1\\u0b05-\\u0b0c\\u0b0f\\u0b10\\u0b13-\\u0b28\\u0b2a-\\u0b30\\u0b32\\u0b33\\u0b35-\\u0b39\\u0b3d\\u0b5c\\u0b5d\\u0b5f-\\u0b61\\u0b71\\u0b83\\u0b85-\\u0b8a\\u0b8e-\\u0b90\\u0b92-\\u0b95\\u0b99\\u0b9a\\u0b9c\\u0b9e\\u0b9f\\u0ba3\\u0ba4\\u0ba8-\\u0baa\\u0bae-\\u0bb9\\u0bd0\\u0c05-\\u0c0c\\u0c0e-\\u0c10\\u0c12-\\u0c28\\u0c2a-\\u0c33\\u0c35-\\u0c39\\u0c3d\\u0c58\\u0c59\\u0c60\\u0c61\\u0c85-\\u0c8c\\u0c8e-\\u0c90\\u0c92-\\u0ca8\\u0caa-\\u0cb3\\u0cb5-\\u0cb9\\u0cbd\\u0cde\\u0ce0\\u0ce1\\u0cf1\\u0cf2\\u0d05-\\u0d0c\\u0d0e-\\u0d10\\u0d12-\\u0d3a\\u0d3d\\u0d4e\\u0d60\\u0d61\\u0d7a-\\u0d7f\\u0d85-\\u0d96\\u0d9a-\\u0db1\\u0db3-\\u0dbb\\u0dbd\\u0dc0-\\u0dc6\\u0e01-\\u0e30\\u0e32\\u0e33\\u0e40-\\u0e46\\u0e81\\u0e82\\u0e84\\u0e87\\u0e88\\u0e8a\\u0e8d\\u0e94-\\u0e97\\u0e99-\\u0e9f\\u0ea1-\\u0ea3\\u0ea5\\u0ea7\\u0eaa\\u0eab\\u0ead-\\u0eb0\\u0eb2\\u0eb3\\u0ebd\\u0ec0-\\u0ec4\\u0ec6\\u0edc-\\u0edf\\u0f00\\u0f40-\\u0f47\\u0f49-\\u0f6c\\u0f88-\\u0f8c\\u1000-\\u102a\\u103f\\u1050-\\u1055\\u105a-\\u105d\\u1061\\u1065\\u1066\\u106e-\\u1070\\u1075-\\u1081\\u108e\\u10a0-\\u10c5\\u10c7\\u10cd\\u10d0-\\u10fa\\u10fc-\\u1248\\u124a-\\u124d\\u1250-\\u1256\\u1258\\u125a-\\u125d\\u1260-\\u1288\\u128a-\\u128d\\u1290-\\u12b0\\u12b2-\\u12b5\\u12b8-\\u12be\\u12c0\\u12c2-\\u12c5\\u12c8-\\u12d6\\u12d8-\\u1310\\u1312-\\u1315\\u1318-\\u135a\\u1380-\\u138f\\u13a0-\\u13f4\\u1401-\\u166c\\u166f-\\u167f\\u1681-\\u169a\\u16a0-\\u16ea\\u16ee-\\u16f0\\u1700-\\u170c\\u170e-\\u1711\\u1720-\\u1731\\u1740-\\u1751\\u1760-\\u176c\\u176e-\\u1770\\u1780-\\u17b3\\u17d7\\u17dc\\u1820-\\u1877\\u1880-\\u18a8\\u18aa\\u18b0-\\u18f5\\u1900-\\u191c\\u1950-\\u196d\\u1970-\\u1974\\u1980-\\u19ab\\u19c1-\\u19c7\\u1a00-\\u1a16\\u1a20-\\u1a54\\u1aa7\\u1b05-\\u1b33\\u1b45-\\u1b4b\\u1b83-\\u1ba0\\u1bae\\u1baf\\u1bba-\\u1be5\\u1c00-\\u1c23\\u1c4d-\\u1c4f\\u1c5a-\\u1c7d\\u1ce9-\\u1cec\\u1cee-\\u1cf1\\u1cf5\\u1cf6\\u1d00-\\u1dbf\\u1e00-\\u1f15\\u1f18-\\u1f1d\\u1f20-\\u1f45\\u1f48-\\u1f4d\\u1f50-\\u1f57\\u1f59\\u1f5b\\u1f5d\\u1f5f-\\u1f7d\\u1f80-\\u1fb4\\u1fb6-\\u1fbc\\u1fbe\\u1fc2-\\u1fc4\\u1fc6-\\u1fcc\\u1fd0-\\u1fd3\\u1fd6-\\u1fdb\\u1fe0-\\u1fec\\u1ff2-\\u1ff4\\u1ff6-\\u1ffc\\u2071\\u207f\\u2090-\\u209c\\u2102\\u2107\\u210a-\\u2113\\u2115\\u2119-\\u211d\\u2124\\u2126\\u2128\\u212a-\\u212d\\u212f-\\u2139\\u213c-\\u213f\\u2145-\\u2149\\u214e\\u2160-\\u2188\\u2c00-\\u2c2e\\u2c30-\\u2c5e\\u2c60-\\u2ce4\\u2ceb-\\u2cee\\u2cf2\\u2cf3\\u2d00-\\u2d25\\u2d27\\u2d2d\\u2d30-\\u2d67\\u2d6f\\u2d80-\\u2d96\\u2da0-\\u2da6\\u2da8-\\u2dae\\u2db0-\\u2db6\\u2db8-\\u2dbe\\u2dc0-\\u2dc6\\u2dc8-\\u2dce\\u2dd0-\\u2dd6\\u2dd8-\\u2dde\\u2e2f\\u3005-\\u3007\\u3021-\\u3029\\u3031-\\u3035\\u3038-\\u303c\\u3041-\\u3096\\u309d-\\u309f\\u30a1-\\u30fa\\u30fc-\\u30ff\\u3105-\\u312d\\u3131-\\u318e\\u31a0-\\u31ba\\u31f0-\\u31ff\\u3400-\\u4db5\\u4e00-\\u9fcc\\ua000-\\ua48c\\ua4d0-\\ua4fd\\ua500-\\ua60c\\ua610-\\ua61f\\ua62a\\ua62b\\ua640-\\ua66e\\ua67f-\\ua697\\ua6a0-\\ua6ef\\ua717-\\ua71f\\ua722-\\ua788\\ua78b-\\ua78e\\ua790-\\ua793\\ua7a0-\\ua7aa\\ua7f8-\\ua801\\ua803-\\ua805\\ua807-\\ua80a\\ua80c-\\ua822\\ua840-\\ua873\\ua882-\\ua8b3\\ua8f2-\\ua8f7\\ua8fb\\ua90a-\\ua925\\ua930-\\ua946\\ua960-\\ua97c\\ua984-\\ua9b2\\ua9cf\\uaa00-\\uaa28\\uaa40-\\uaa42\\uaa44-\\uaa4b\\uaa60-\\uaa76\\uaa7a\\uaa80-\\uaaaf\\uaab1\\uaab5\\uaab6\\uaab9-\\uaabd\\uaac0\\uaac2\\uaadb-\\uaadd\\uaae0-\\uaaea\\uaaf2-\\uaaf4\\uab01-\\uab06\\uab09-\\uab0e\\uab11-\\uab16\\uab20-\\uab26\\uab28-\\uab2e\\uabc0-\\uabe2\\uac00-\\ud7a3\\ud7b0-\\ud7c6\\ud7cb-\\ud7fb\\uf900-\\ufa6d\\ufa70-\\ufad9\\ufb00-\\ufb06\\ufb13-\\ufb17\\ufb1d\\ufb1f-\\ufb28\\ufb2a-\\ufb36\\ufb38-\\ufb3c\\ufb3e\\ufb40\\ufb41\\ufb43\\ufb44\\ufb46-\\ufbb1\\ufbd3-\\ufd3d\\ufd50-\\ufd8f\\ufd92-\\ufdc7\\ufdf0-\\ufdfb\\ufe70-\\ufe74\\ufe76-\\ufefc\\uff21-\\uff3a\\uff41-\\uff5a\\uff66-\\uffbe\\uffc2-\\uffc7\\uffca-\\uffcf\\uffd2-\\uffd7\\uffda-\\uffdc";\n
  var nonASCIIidentifierChars = "\\u0300-\\u036f\\u0483-\\u0487\\u0591-\\u05bd\\u05bf\\u05c1\\u05c2\\u05c4\\u05c5\\u05c7\\u0610-\\u061a\\u0620-\\u0649\\u0672-\\u06d3\\u06e7-\\u06e8\\u06fb-\\u06fc\\u0730-\\u074a\\u0800-\\u0814\\u081b-\\u0823\\u0825-\\u0827\\u0829-\\u082d\\u0840-\\u0857\\u08e4-\\u08fe\\u0900-\\u0903\\u093a-\\u093c\\u093e-\\u094f\\u0951-\\u0957\\u0962-\\u0963\\u0966-\\u096f\\u0981-\\u0983\\u09bc\\u09be-\\u09c4\\u09c7\\u09c8\\u09d7\\u09df-\\u09e0\\u0a01-\\u0a03\\u0a3c\\u0a3e-\\u0a42\\u0a47\\u0a48\\u0a4b-\\u0a4d\\u0a51\\u0a66-\\u0a71\\u0a75\\u0a81-\\u0a83\\u0abc\\u0abe-\\u0ac5\\u0ac7-\\u0ac9\\u0acb-\\u0acd\\u0ae2-\\u0ae3\\u0ae6-\\u0aef\\u0b01-\\u0b03\\u0b3c\\u0b3e-\\u0b44\\u0b47\\u0b48\\u0b4b-\\u0b4d\\u0b56\\u0b57\\u0b5f-\\u0b60\\u0b66-\\u0b6f\\u0b82\\u0bbe-\\u0bc2\\u0bc6-\\u0bc8\\u0bca-\\u0bcd\\u0bd7\\u0be6-\\u0bef\\u0c01-\\u0c03\\u0c46-\\u0c48\\u0c4a-\\u0c4d\\u0c55\\u0c56\\u0c62-\\u0c63\\u0c66-\\u0c6f\\u0c82\\u0c83\\u0cbc\\u0cbe-\\u0cc4\\u0cc6-\\u0cc8\\u0cca-\\u0ccd\\u0cd5\\u0cd6\\u0ce2-\\u0ce3\\u0ce6-\\u0cef\\u0d02\\u0d03\\u0d46-\\u0d48\\u0d57\\u0d62-\\u0d63\\u0d66-\\u0d6f\\u0d82\\u0d83\\u0dca\\u0dcf-\\u0dd4\\u0dd6\\u0dd8-\\u0ddf\\u0df2\\u0df3\\u0e34-\\u0e3a\\u0e40-\\u0e45\\u0e50-\\u0e59\\u0eb4-\\u0eb9\\u0ec8-\\u0ecd\\u0ed0-\\u0ed9\\u0f18\\u0f19\\u0f20-\\u0f29\\u0f35\\u0f37\\u0f39\\u0f41-\\u0f47\\u0f71-\\u0f84\\u0f86-\\u0f87\\u0f8d-\\u0f97\\u0f99-\\u0fbc\\u0fc6\\u1000-\\u1029\\u1040-\\u1049\\u1067-\\u106d\\u1071-\\u1074\\u1082-\\u108d\\u108f-\\u109d\\u135d-\\u135f\\u170e-\\u1710\\u1720-\\u1730\\u1740-\\u1750\\u1772\\u1773\\u1780-\\u17b2\\u17dd\\u17e0-\\u17e9\\u180b-\\u180d\\u1810-\\u1819\\u1920-\\u192b\\u1930-\\u193b\\u1951-\\u196d\\u19b0-\\u19c0\\u19c8-\\u19c9\\u19d0-\\u19d9\\u1a00-\\u1a15\\u1a20-\\u1a53\\u1a60-\\u1a7c\\u1a7f-\\u1a89\\u1a90-\\u1a99\\u1b46-\\u1b4b\\u1b50-\\u1b59\\u1b6b-\\u1b73\\u1bb0-\\u1bb9\\u1be6-\\u1bf3\\u1c00-\\u1c22\\u1c40-\\u1c49\\u1c5b-\\u1c7d\\u1cd0-\\u1cd2\\u1d00-\\u1dbe\\u1e01-\\u1f15\\u200c\\u200d\\u203f\\u2040\\u2054\\u20d0-\\u20dc\\u20e1\\u20e5-\\u20f0\\u2d81-\\u2d96\\u2de0-\\u2dff\\u3021-\\u3028\\u3099\\u309a\\ua640-\\ua66d\\ua674-\\ua67d\\ua69f\\ua6f0-\\ua6f1\\ua7f8-\\ua800\\ua806\\ua80b\\ua823-\\ua827\\ua880-\\ua881\\ua8b4-\\ua8c4\\ua8d0-\\ua8d9\\ua8f3-\\ua8f7\\ua900-\\ua909\\ua926-\\ua92d\\ua930-\\ua945\\ua980-\\ua983\\ua9b3-\\ua9c0\\uaa00-\\uaa27\\uaa40-\\uaa41\\uaa4c-\\uaa4d\\uaa50-\\uaa59\\uaa7b\\uaae0-\\uaae9\\uaaf2-\\uaaf3\\uabc0-\\uabe1\\uabec\\uabed\\uabf0-\\uabf9\\ufb20-\\ufb28\\ufe00-\\ufe0f\\ufe20-\\ufe26\\ufe33\\ufe34\\ufe4d-\\ufe4f\\uff10-\\uff19\\uff3f";\n
  var nonASCIIidentifierStart = new RegExp("[" + nonASCIIidentifierStartChars + "]");\n
  var nonASCIIidentifier = new RegExp("[" + nonASCIIidentifierStartChars + nonASCIIidentifierChars + "]");\n
\n
  // Whether a single character denotes a newline.\n
\n
  var newline = /[\\n\\r\\u2028\\u2029]/;\n
\n
  // Matches a whole line break (where CRLF is considered a single\n
  // line break). Used to count lines.\n
\n
  var lineBreak = /\\r\\n|[\\n\\r\\u2028\\u2029]/g;\n
\n
  // Test whether a given character code starts an identifier.\n
\n
  var isIdentifierStart = exports.isIdentifierStart = function(code) {\n
    if (code < 65) return code === 36;\n
    if (code < 91) return true;\n
    if (code < 97) return code === 95;\n
    if (code < 123)return true;\n
    return code >= 0xaa && nonASCIIidentifierStart.test(String.fromCharCode(code));\n
  };\n
\n
  // Test whether a given character is part of an identifier.\n
\n
  var isIdentifierChar = exports.isIdentifierChar = function(code) {\n
    if (code < 48) return code === 36;\n
    if (code < 58) return true;\n
    if (code < 65) return false;\n
    if (code < 91) return true;\n
    if (code < 97) return code === 95;\n
    if (code < 123)return true;\n
    return code >= 0xaa && nonASCIIidentifier.test(String.fromCharCode(code));\n
  };\n
\n
  // ## Tokenizer\n
\n
  // These are used when `options.locations` is on, for the\n
  // `tokStartLoc` and `tokEndLoc` properties.\n
\n
  function line_loc_t() {\n
    this.line = tokCurLine;\n
    this.column = tokPos - tokLineStart;\n
  }\n
\n
  // Reset the token state. Used at the start of a parse.\n
\n
  function initTokenState() {\n
    tokCurLine = 1;\n
    tokPos = tokLineStart = 0;\n
    tokRegexpAllowed = true;\n
    skipSpace();\n
  }\n
\n
  // Called at the end of every token. Sets `tokEnd`, `tokVal`, and\n
  // `tokRegexpAllowed`, and skips the space after the token, so that\n
  // the next one\'s `tokStart` will point at the right position.\n
\n
  function finishToken(type, val) {\n
    tokEnd = tokPos;\n
    if (options.locations) tokEndLoc = new line_loc_t;\n
    tokType = type;\n
    skipSpace();\n
    tokVal = val;\n
    tokRegexpAllowed = type.beforeExpr;\n
  }\n
\n
  function skipBlockComment() {\n
    var startLoc = options.onComment && options.locations && new line_loc_t;\n
    var start = tokPos, end = input.indexOf("*/", tokPos += 2);\n
    if (end === -1) raise(tokPos - 2, "Unterminated comment");\n
    tokPos = end + 2;\n
    if (options.locations) {\n
      lineBreak.lastIndex = start;\n
      var match;\n
      while ((match = lineBreak.exec(input)) && match.index < tokPos) {\n
        ++tokCurLine;\n
        tokLineStart = match.index + match[0].length;\n
      }\n
    }\n
    if (options.onComment)\n
      options.onComment(true, input.slice(start + 2, end), start, tokPos,\n
                        startLoc, options.locations && new line_loc_t);\n
  }\n
\n
  function skipLineComment() {\n
    var start = tokPos;\n
    var startLoc = options.onComment && options.locations && new line_loc_t;\n
    var ch = input.charCodeAt(tokPos+=2);\n
    while (tokPos < inputLen && ch !== 10 && ch !== 13 && ch !== 8232 && ch !== 8233) {\n
      ++tokPos;\n
      ch = input.charCodeAt(tokPos);\n
    }\n
    if (options.onComment)\n
      options.onComment(false, input.slice(start + 2, tokPos), start, tokPos,\n
                        startLoc, options.locations && new line_loc_t);\n
  }\n
\n
  // Called at the start of the parse and after every token. Skips\n
  // whitespace and comments, and.\n
\n
  function skipSpace() {\n
    while (tokPos < inputLen) {\n
      var ch = input.charCodeAt(tokPos);\n
      if (ch === 32) { // \' \'\n
        ++tokPos;\n
      } else if (ch === 13) {\n
        ++tokPos;\n
        var next = input.charCodeAt(tokPos);\n
        if (next === 10) {\n
          ++tokPos;\n
        }\n
        if (options.locations) {\n
          ++tokCurLine;\n
          tokLineStart = tokPos;\n
        }\n
      } else if (ch === 10 || ch === 8232 || ch === 8233) {\n
        ++tokPos;\n
        if (options.locations) {\n
          ++tokCurLine;\n
          tokLineStart = tokPos;\n
        }\n
      } else if (ch > 8 && ch < 14) {\n
        ++tokPos;\n
      } else if (ch === 47) { // \'/\'\n
        var next = input.charCodeAt(tokPos + 1);\n
        if (next === 42) { // \'*\'\n
          skipBlockComment();\n
        } else if (next === 47) { // \'/\'\n
          skipLineComment();\n
        } else break;\n
      } else if (ch === 160) { // \'\\xa0\'\n
        ++tokPos;\n
      } else if (ch >= 5760 && nonASCIIwhitespace.test(String.fromCharCode(ch))) {\n
        ++tokPos;\n
      } else {\n
        break;\n
      }\n
    }\n
  }\n
\n
  // ### Token reading\n
\n
  // This is the function that is called to fetch the next token. It\n
  // is somewhat obscure, because it works in character codes rather\n
  // than characters, and because operator parsing has been inlined\n
  // into it.\n
  //\n
  // All in the name of speed.\n
  //\n
  // The `forceRegexp` parameter is used in the one case where the\n
  // `tokRegexpAllowed` trick does not work. See `parseStatement`.\n
\n
  function readToken_dot() {\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next >= 48 && next <= 57) return readNumber(true);\n
    ++tokPos;\n
    return finishToken(_dot);\n
  }\n
\n
  function readToken_slash() { // \'/\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (tokRegexpAllowed) {++tokPos; return readRegexp();}\n
    if (next === 61) return finishOp(_assign, 2);\n
    return finishOp(_slash, 1);\n
  }\n
\n
  function readToken_mult_modulo() { // \'%*\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next === 61) return finishOp(_assign, 2);\n
    return finishOp(_multiplyModulo, 1);\n
  }\n
\n
  function readToken_pipe_amp(code) { // \'|&\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next === code) return finishOp(code === 124 ? _logicalOR : _logicalAND, 2);\n
    if (next === 61) return finishOp(_assign, 2);\n
    return finishOp(code === 124 ? _bitwiseOR : _bitwiseAND, 1);\n
  }\n
\n
  function readToken_caret() { // \'^\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next === 61) return finishOp(_assign, 2);\n
    return finishOp(_bitwiseXOR, 1);\n
  }\n
\n
  function readToken_plus_min(code) { // \'+-\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next === code) {\n
      if (next == 45 && input.charCodeAt(tokPos + 2) == 62 &&\n
          newline.test(input.slice(lastEnd, tokPos))) {\n
        // A `-->` line comment\n
        tokPos += 3;\n
        skipLineComment();\n
        skipSpace();\n
        return readToken();\n
      }\n
      return finishOp(_incDec, 2);\n
    }\n
    if (next === 61) return finishOp(_assign, 2);\n
    return finishOp(_plusMin, 1);\n
  }\n
\n
  function readToken_lt_gt(code) { // \'<>\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    var size = 1;\n
    if (next === code) {\n
      size = code === 62 && input.charCodeAt(tokPos + 2) === 62 ? 3 : 2;\n
      if (input.charCodeAt(tokPos + size) === 61) return finishOp(_assign, size + 1);\n
      return finishOp(_bitShift, size);\n
    }\n
    if (next == 33 && code == 60 && input.charCodeAt(tokPos + 2) == 45 &&\n
        input.charCodeAt(tokPos + 3) == 45) {\n
      // `<!--`, an XML-style comment that should be interpreted as a line comment\n
      tokPos += 4;\n
      skipLineComment();\n
      skipSpace();\n
      return readToken();\n
    }\n
    if (next === 61)\n
      size = input.charCodeAt(tokPos + 2) === 61 ? 3 : 2;\n
    return finishOp(_relational, size);\n
  }\n
\n
  function readToken_eq_excl(code) { // \'=!\'\n
    var next = input.charCodeAt(tokPos + 1);\n
    if (next === 61) return finishOp(_equality, input.charCodeAt(tokPos + 2) === 61 ? 3 : 2);\n
    return finishOp(code === 61 ? _eq : _prefix, 1);\n
  }\n
\n
  function getTokenFromCode(code) {\n
    switch(code) {\n
      // The interpretation of a dot depends on whether it is followed\n
      // by a digit.\n
    case 46: // \'.\'\n
      return readToken_dot();\n
\n
      // Punctuation tokens.\n
    case 40: ++tokPos; return finishToken(_parenL);\n
    case 41: ++tokPos; return finishToken(_parenR);\n
    case 59: ++tokPos; return finishToken(_semi);\n
    case 44: ++tokPos; return finishToken(_comma);\n
    case 91: ++tokPos; return finishToken(_bracketL);\n
    case 93: ++tokPos; return finishToken(_bracketR);\n
    case 123: ++tokPos; return finishToken(_braceL);\n
    case 125: ++tokPos; return finishToken(_braceR);\n
    case 58: ++tokPos; return finishToken(_colon);\n
    case 63: ++tokPos; return finishToken(_question);\n
\n
      // \'0x\' is a hexadecimal number.\n
    case 48: // \'0\'\n
      var next = input.charCodeAt(tokPos + 1);\n
      if (next === 120 || next === 88) return readHexNumber();\n
      // Anything else beginning with a digit is an integer, octal\n
      // number, or float.\n
    case 49: case 50: case 51: case 52: case 53: case 54: case 55: case 56: case 57: // 1-9\n
      return readNumber(false);\n
\n
      // Quotes produce strings.\n
    case 34: case 39: // \'"\', "\'"\n
      return readString(code);\n
\n
    // Operators are parsed inline in tiny state machines. \'=\' (61) is\n
    // often referred to. `finishOp` simply skips the amount of\n
    // characters it is given as second argument, and returns a token\n
    // of the type given by its first argument.\n
\n
    case 47: // \'/\'\n
      return readToken_slash(code);\n
\n
    case 37: case 42: // \'%*\'\n
      return readToken_mult_modulo();\n
\n
    case 124: case 38: // \'|&\'\n
      return readToken_pipe_amp(code);\n
\n
    case 94: // \'^\'\n
      return readToken_caret();\n
\n
    case 43: case 45: // \'+-\'\n
      return readToken_plus_min(code);\n
\n
    case 60: case 62: // \'<>\'\n
      return readToken_lt_gt(code);\n
\n
    case 61: case 33: // \'=!\'\n
      return readToken_eq_excl(code);\n
\n
    case 126: // \'~\'\n
      return finishOp(_prefix, 1);\n
    }\n
\n
    return false;\n
  }\n
\n
  function readToken(forceRegexp) {\n
    if (!forceRegexp) tokStart = tokPos;\n
    else tokPos = tokStart + 1;\n
    if (options.locations) tokStartLoc = new line_loc_t;\n
    if (forceRegexp) return readRegexp();\n
    if (tokPos >= inputLen) return finishToken(_eof);\n
\n
    var code = input.charCodeAt(tokPos);\n
    // Identifier or keyword. \'\\uXXXX\' sequences are allowed in\n
    // identifiers, so \'\\\' also dispatches to that.\n
    if (isIdentifierStart(code) || code === 92 /* \'\\\' */) return readWord();\n
\n
    var tok = getTokenFromCode(code);\n
\n
    if (tok === false) {\n
      // If we are here, we either found a non-ASCII identifier\n
      // character, or something that\'s entirely disallowed.\n
      var ch = String.fromCharCode(code);\n
      if (ch === "\\\\" || nonASCIIidentifierStart.test(ch)) return readWord();\n
      raise(tokPos, "Unexpected character \'" + ch + "\'");\n
    }\n
    return tok;\n
  }\n
\n
  function finishOp(type, size) {\n
    var str = input.slice(tokPos, tokPos + size);\n
    tokPos += size;\n
    finishToken(type, str);\n
  }\n
\n
  // Parse a regular expression. Some context-awareness is necessary,\n
  // since a \'/\' inside a \'[]\' set does not end the expression.\n
\n
  function readRegexp() {\n
    var content = "", escaped, inClass, start = tokPos;\n
    for (;;) {\n
      if (tokPos >= inputLen) raise(start, "Unterminated regular expression");\n
      var ch = input.charAt(tokPos);\n
      if (newline.test(ch)) raise(start, "Unterminated regular expression");\n
      if (!escaped) {\n
        if (ch === "[") inClass = true;\n
        else if (ch === "]" && inClass) inClass = false;\n
        else if (ch === "/" && !inClass) break;\n
        escaped = ch === "\\\\";\n
      } else escaped = false;\n
      ++tokPos;\n
    }\n
    var content = input.slice(start, tokPos);\n
    ++tokPos;\n
    // Need to use `readWord1` because \'\\uXXXX\' sequences are allowed\n
    // here (don\'t ask).\n
    var mods = readWord1();\n
    if (mods && !/^[gmsiy]*$/.test(mods)) raise(start, "Invalid regexp flag");\n
    try {\n
      var value = new RegExp(content, mods);\n
    } catch (e) {\n
      if (e instanceof SyntaxError) raise(start, e.message);\n
      raise(e);\n
    }\n
    return finishToken(_regexp, value);\n
  }\n
\n
  // Read an integer in the given radix. Return null if zero digits\n
  // were read, the integer value otherwise. When `len` is given, this\n
  // will return `null` unless the integer has exactly `len` digits.\n
\n
  function readInt(radix, len) {\n
    var start = tokPos, total = 0;\n
    for (var i = 0, e = len == null ? Infinity : len; i < e; ++i) {\n
      var code = input.charCodeAt(tokPos), val;\n
      if (code >= 97) val = code - 97 + 10; // a\n
      else if (code >= 65) val = code - 65 + 10; // A\n
      else if (code >= 48 && code <= 57) val = code - 48; // 0-9\n
      else val = Infinity;\n
      if (val >= radix) break;\n
      ++tokPos;\n
      total = total * radix + val;\n
    }\n
    if (tokPos === start || len != null && tokPos - start !== len) return null;\n
\n
    return total;\n
  }\n
\n
  function readHexNumber() {\n
    tokPos += 2; // 0x\n
    var val = readInt(16);\n
    if (val == null) raise(tokStart + 2, "Expected hexadecimal number");\n
    if (isIdentifierStart(input.charCodeAt(tokPos))) raise(tokPos, "Identifier directly after number");\n
    return finishToken(_num, val);\n
  }\n
\n
  // Read an integer, octal integer, or floating-point number.\n
\n
  function readNumber(startsWithDot) {\n
    var start = tokPos, isFloat = false, octal = input.charCodeAt(tokPos) === 48;\n
    if (!startsWithDot && readInt(10) === null) raise(start, "Invalid number");\n
    if (input.charCodeAt(tokPos) === 46) {\n
      ++tokPos;\n
      readInt(10);\n
      isFloat = true;\n
    }\n
    var next = input.charCodeAt(tokPos);\n
    if (next === 69 || next === 101) { // \'eE\'\n
      next = input.charCodeAt(++tokPos);\n
      if (next === 43 || next === 45) ++tokPos; // \'+-\'\n
      if (readInt(10) === null) raise(start, "Invalid number");\n
      isFloat = true;\n
    }\n
    if (isIdentifierStart(input.charCodeAt(tokPos))) raise(tokPos, "Identifier directly after number");\n
\n
    var str = input.slice(start, tokPos), val;\n
    if (isFloat) val = parseFloat(str);\n
    else if (!octal || str.length === 1) val = parseInt(str, 10);\n
    else if (/[89]/.test(str) || strict) raise(start, "Invalid number");\n
    else val = parseInt(str, 8);\n
    return finishToken(_num, val);\n
  }\n
\n
  // Read a string value, interpreting backslash-escapes.\n
\n
  function readString(quote) {\n
    tokPos++;\n
    var out = "";\n
    for (;;) {\n
      if (tokPos >= inputLen) raise(tokStart, "Unterminated string constant");\n
      var ch = input.charCodeAt(tokPos);\n
      if (ch === quote) {\n
        ++tokPos;\n
        return finishToken(_string, out);\n
      }\n
      if (ch === 92) { // \'\\\'\n
        ch = input.charCodeAt(++tokPos);\n
        var octal = /^[0-7]+/.exec(input.slice(tokPos, tokPos + 3));\n
        if (octal) octal = octal[0];\n
        while (octal && parseInt(octal, 8) > 255) octal = octal.slice(0, -1);\n
        if (octal === "0") octal = null;\n
        ++tokPos;\n
        if (octal) {\n
          if (strict) raise(tokPos - 2, "Octal literal in strict mode");\n
          out += String.fromCharCode(parseInt(octal, 8));\n
          tokPos += octal.length - 1;\n
        } else {\n
          switch (ch) {\n
          case 110: out += "\\n"; break; // \'n\' -> \'\\n\'\n
          case 114: out += "\\r"; break; // \'r\' -> \'\\r\'\n
          case 120: out += String.fromCharCode(readHexChar(2)); break; // \'x\'\n
          case 117: out += String.fromCharCode(readHexChar(4)); break; // \'u\'\n
          case 85: out += String.fromCharCode(readHexChar(8)); break; // \'U\'\n
          case 116: out += "\\t"; break; // \'t\' -> \'\\t\'\n
          case 98: out += "\\b"; break; // \'b\' -> \'\\b\'\n
          case 118: out += "\\u000b"; break; // \'v\' -> \'\\u000b\'\n
          case 102: out += "\\f"; break; // \'f\' -> \'\\f\'\n
          case 48: out += "\\0"; break; // 0 -> \'\\0\'\n
          case 13: if (input.charCodeAt(tokPos) === 10) ++tokPos; // \'\\r\\n\'\n
          case 10: // \' \\n\'\n
            if (options.locations) { tokLineStart = tokPos; ++tokCurLine; }\n
            break;\n
          default: out += String.fromCharCode(ch); break;\n
          }\n
        }\n
      } else {\n
        if (ch === 13 || ch === 10 || ch === 8232 || ch === 8233) raise(tokStart, "Unterminated string constant");\n
        out += String.fromCharCode(ch); // \'\\\'\n
        ++tokPos;\n
      }\n
    }\n
  }\n
\n
  // Used to read character escape sequences (\'\\x\', \'\\u\', \'\\U\').\n
\n
  function readHexChar(len) {\n
    var n = readInt(16, len);\n
    if (n === null) raise(tokStart, "Bad character escape sequence");\n
    return n;\n
  }\n
\n
  // Used to signal to callers of `readWord1` whether the word\n
  // contained any escape sequences. This is needed because words with\n
  // escape sequences must not be interpreted as keywords.\n
\n
  var containsEsc;\n
\n
  // Read an identifier, and return it as a string. Sets `containsEsc`\n
  // to whether the word contained a \'\\u\' escape.\n
  //\n
  // Only builds up the word character-by-character when it actually\n
  // containeds an escape, as a micro-optimization.\n
\n
  function readWord1() {\n
    containsEsc = false;\n
    var word, first = true, start = tokPos;\n
    for (;;) {\n
      var ch = input.charCodeAt(tokPos);\n
      if (isIdentifierChar(ch)) {\n
        if (containsEsc) word += input.charAt(tokPos);\n
        ++tokPos;\n
      } else if (ch === 92) { // "\\"\n
        if (!containsEsc) word = input.slice(start, tokPos);\n
        containsEsc = true;\n
        if (input.charCodeAt(++tokPos) != 117) // "u"\n
          raise(tokPos, "Expecting Unicode escape sequence \\\\uXXXX");\n
        ++tokPos;\n
        var esc = readHexChar(4);\n
        var escStr = String.fromCharCode(esc);\n
        if (!escStr) raise(tokPos - 1, "Invalid Unicode escape");\n
        if (!(first ? isIdentifierStart(esc) : isIdentifierChar(esc)))\n
          raise(tokPos - 4, "Invalid Unicode escape");\n
        word += escStr;\n
      } else {\n
        break;\n
      }\n
      first = false;\n
    }\n
    return containsEsc ? word : input.slice(start, tokPos);\n
  }\n
\n
  // Read an identifier or keyword token. Will check for reserved\n
  // words when necessary.\n
\n
  function readWord() {\n
    var word = readWord1();\n
    var type = _name;\n
    if (!containsEsc && isKeyword(word))\n
      type = keywordTypes[word];\n
    return finishToken(type, word);\n
  }\n
\n
  // ## Parser\n
\n
  // A recursive descent parser operates by defining functions for all\n
  // syntactic elements, and recursively calling those, each function\n
  // advancing the input stream and returning an AST node. Precedence\n
  // of constructs (for example, the fact that `!x[1]` means `!(x[1])`\n
  // instead of `(!x)[1]` is handled by the fact that the parser\n
  // function that parses unary prefix operators is called first, and\n
  // in turn calls the function that parses `[]` subscripts — that\n
  // way, it\'ll receive the node for `x[1]` already parsed, and wraps\n
  // *that* in the unary operator node.\n
  //\n
  // Acorn uses an [operator precedence parser][opp] to handle binary\n
  // operator precedence, because it is much more compact than using\n
  // the technique outlined above, which uses different, nesting\n
  // functions to specify precedence, for all of the ten binary\n
  // precedence levels that JavaScript defines.\n
  //\n
  // [opp]: http://en.wikipedia.org/wiki/Operator-precedence_parser\n
\n
  // ### Parser utilities\n
\n
  // Continue to the next token.\n
\n
  function next() {\n
    lastStart = tokStart;\n
    lastEnd = tokEnd;\n
    lastEndLoc = tokEndLoc;\n
    readToken();\n
  }\n
\n
  // Enter strict mode. Re-reads the next token to please pedantic\n
  // tests ("use strict"; 010; -- should fail).\n
\n
  function setStrict(strct) {\n
    strict = strct;\n
    tokPos = tokStart;\n
    if (options.locations) {\n
      while (tokPos < tokLineStart) {\n
        tokLineStart = input.lastIndexOf("\\n", tokLineStart - 2) + 1;\n
        --tokCurLine;\n
      }\n
    }\n
    skipSpace();\n
    readToken();\n
  }\n
\n
  // Start an AST node, attaching a start offset.\n
\n
  function node_t() {\n
    this.type = null;\n
    this.start = tokStart;\n
    this.end = null;\n
  }\n
\n
  function node_loc_t() {\n
    this.start = tokStartLoc;\n
    this.end = null;\n
    if (sourceFile !== null) this.source = sourceFile;\n
  }\n
\n
  function startNode() {\n
    var node = new node_t();\n
    if (options.locations)\n
      node.loc = new node_loc_t();\n
    if (options.directSourceFile)\n
      node.sourceFile = options.directSourceFile;\n
    if (options.ranges)\n
      node.range = [tokStart, 0];\n
    return node;\n
  }\n
\n
  // Start a node whose start offset information should be based on\n
  // the start of another node. For example, a binary operator node is\n
  // only started after its left-hand side has already been parsed.\n
\n
  function startNodeFrom(other) {\n
    var node = new node_t();\n
    node.start = other.start;\n
    if (options.locations) {\n
      node.loc = new node_loc_t();\n
      node.loc.start = other.loc.start;\n
    }\n
    if (options.ranges)\n
      node.range = [other.range[0], 0];\n
\n
    return node;\n
  }\n
\n
  // Finish an AST node, adding `type` and `end` properties.\n
\n
  function finishNode(node, type) {\n
    node.type = type;\n
    node.end = lastEnd;\n
    if (options.locations)\n
      node.loc.end = lastEndLoc;\n
    if (options.ranges)\n
      node.range[1] = lastEnd;\n
    return node;\n
  }\n
\n
  // Test whether a statement node is the string literal `"use strict"`.\n
\n
  function isUseStrict(stmt) {\n
    return options.ecmaVersion >= 5 && stmt.type === "ExpressionStatement" &&\n
      stmt.expression.type === "Literal" && stmt.expression.value === "use strict";\n
  }\n
\n
  // Predicate that tests whether the next token is of the given\n
  // type, and if yes, consumes it as a side effect.\n
\n
  function eat(type) {\n
    if (tokType === type) {\n
      next();\n
      return true;\n
    }\n
  }\n
\n
  // Test whether a semicolon can be inserted at the current position.\n
\n
  function canInsertSemicolon() {\n
    return !options.strictSemicolons &&\n
      (tokType === _eof || tokType === _braceR || newline.test(input.slice(lastEnd, tokStart)));\n
  }\n
\n
  // Consume a semicolon, or, failing that, see if we are allowed to\n
  // pretend that there is a semicolon at this position.\n
\n
  function semicolon() {\n
    if (!eat(_semi) && !canInsertSemicolon()) unexpected();\n
  }\n
\n
  // Expect a token of a given type. If found, consume it, otherwise,\n
  // raise an unexpected token error.\n
\n
  function expect(type) {\n
    if (tokType === type) next();\n
    else unexpected();\n
  }\n
\n
  // Raise an unexpected token error.\n
\n
  function unexpected() {\n
    raise(tokStart, "Unexpected token");\n
  }\n
\n
  // Verify that a node is an lval — something that can be assigned\n
  // to.\n
\n
  function checkLVal(expr) {\n
    if (expr.type !== "Identifier" && expr.type !== "MemberExpression")\n
      raise(expr.start, "Assigning to rvalue");\n
    if (strict && expr.type === "Identifier" && isStrictBadIdWord(expr.name))\n
      raise(expr.start, "Assigning to " + expr.name + " in strict mode");\n
  }\n
\n
  // ### Statement parsing\n
\n
  // Parse a program. Initializes the parser, reads any number of\n
  // statements, and wraps them in a Program node.  Optionally takes a\n
  // `program` argument.  If present, the statements will be appended\n
  // to its body instead of creating a new node.\n
\n
  function parseTopLevel(program) {\n
    lastStart = lastEnd = tokPos;\n
    if (options.locations) lastEndLoc = new line_loc_t;\n
    inFunction = strict = null;\n
    labels = [];\n
    readToken();\n
\n
    var node = program || startNode(), first = true;\n
    if (!program) node.body = [];\n
    while (tokType !== _eof) {\n
      var stmt = parseStatement();\n
      node.body.push(stmt);\n
      if (first && isUseStrict(stmt)) setStrict(true);\n
      first = false;\n
    }\n
    return finishNode(node, "Program");\n
  }\n
\n
  var loopLabel = {kind: "loop"}, switchLabel = {kind: "switch"};\n
\n
  // Parse a single statement.\n
  //\n
  // If expecting a statement and finding a slash operator, parse a\n
  // regular expression literal. This is to handle cases like\n
  // `if (foo) /blah/.exec(foo);`, where looking at the previous token\n
  // does not help.\n
\n
  function parseStatement() {\n
    if (tokType === _slash || tokType === _assign && tokVal == "/=")\n
      readToken(true);\n
\n
    var starttype = tokType, node = startNode();\n
\n
    // Most types of statements are recognized by the keyword they\n
    // start with. Many are trivial to parse, some require a bit of\n
    // complexity.\n
\n
    switch (starttype) {\n
    case _break: case _continue:\n
      next();\n
      var isBreak = starttype === _break;\n
      if (eat(_semi) || canInsertSemicolon()) node.label = null;\n
      else if (tokType !== _name) unexpected();\n
      else {\n
        node.label = parseIdent();\n
        semicolon();\n
      }\n
\n
      // Verify that there is an actual destination to break or\n
      // continue to.\n
      for (var i = 0; i < labels.length; ++i) {\n
        var lab = labels[i];\n
        if (node.label == null || lab.name === node.label.name) {\n
          if (lab.kind != null && (isBreak || lab.kind === "loop")) break;\n
          if (node.label && isBreak) break;\n
        }\n
      }\n
      if (i === labels.length) raise(node.start, "Unsyntactic " + starttype.keyword);\n
      return finishNode(node, isBreak ? "BreakStatement" : "ContinueStatement");\n
\n
    case _debugger:\n
      next();\n
      semicolon();\n
      return finishNode(node, "DebuggerStatement");\n
\n
    case _do:\n
      next();\n
      labels.push(loopLabel);\n
      node.body = parseStatement();\n
      labels.pop();\n
      expect(_while);\n
      node.test = parseParenExpression();\n
      semicolon();\n
      return finishNode(node, "DoWhileStatement");\n
\n
      // Disambiguating between a `for` and a `for`/`in` loop is\n
      // non-trivial. Basically, we have to parse the init `var`\n
      // statement or expression, disallowing the `in` operator (see\n
      // the second parameter to `parseExpression`), and then check\n
      // whether the next token is `in`. When there is no init part\n
      // (semicolon immediately after the opening parenthesis), it is\n
      // a regular `for` loop.\n
\n
    case _for:\n
      next();\n
      labels.push(loopLabel);\n
      expect(_parenL);\n
      if (tokType === _semi) return parseFor(node, null);\n
      if (tokType === _var) {\n
        var init = startNode();\n
        next();\n
        parseVar(init, true);\n
        finishNode(init, "VariableDeclaration");\n
        if (init.declarations.length === 1 && eat(_in))\n
          return parseForIn(node, init);\n
        return parseFor(node, init);\n
      }\n
      var init = parseExpression(false, true);\n
      if (eat(_in)) {checkLVal(init); return parseForIn(node, init);}\n
      return parseFor(node, init);\n
\n
    case _function:\n
      next();\n
      return parseFunction(node, true);\n
\n
    case _if:\n
      next();\n
      node.test = parseParenExpression();\n
      node.consequent = parseStatement();\n
      node.alternate = eat(_else) ? parseStatement() : null;\n
      return finishNode(node, "IfStatement");\n
\n
    case _return:\n
      if (!inFunction && !options.allowReturnOutsideFunction)\n
        raise(tokStart, "\'return\' outside of function");\n
      next();\n
\n
      // In `return` (and `break`/`continue`), the keywords with\n
      // optional arguments, we eagerly look for a semicolon or the\n
      // possibility to insert one.\n
\n
      if (eat(_semi) || canInsertSemicolon()) node.argument = null;\n
      else { node.argument = parseExpression(); semicolon(); }\n
      return finishNode(node, "ReturnStatement");\n
\n
    case _switch:\n
      next();\n
      node.discriminant = parseParenExpression();\n
      node.cases = [];\n
      expect(_braceL);\n
      labels.push(switchLabel);\n
\n
      // Statements under must be grouped (by label) in SwitchCase\n
      // nodes. `cur` is used to keep the node that we are currently\n
      // adding statements to.\n
\n
      for (var cur, sawDefault; tokType != _braceR;) {\n
        if (tokType === _case || tokType === _default) {\n
          var isCase = tokType === _case;\n
          if (cur) finishNode(cur, "SwitchCase");\n
          node.cases.push(cur = startNode());\n
          cur.consequent = [];\n
          next();\n
          if (isCase) cur.test = parseExpression();\n
          else {\n
            if (sawDefault) raise(lastStart, "Multiple default clauses"); sawDefault = true;\n
            cur.test = null;\n
          }\n
          expect(_colon);\n
        } else {\n
          if (!cur) unexpected();\n
          cur.consequent.push(parseStatement());\n
        }\n
      }\n
      if (cur) finishNode(cur, "SwitchCase");\n
      next(); // Closing brace\n
      labels.pop();\n
      return finishNode(node, "SwitchStatement");\n
\n
    case _throw:\n
      next();\n
      if (newline.test(input.slice(lastEnd, tokStart)))\n
        raise(lastEnd, "Illegal newline after throw");\n
      node.argument = parseExpression();\n
      semicolon();\n
      return finishNode(node, "ThrowStatement");\n
\n
    case _try:\n
      next();\n
      node.block = parseBlock();\n
      node.handler = null;\n
      if (tokType === _catch) {\n
        var clause = startNode();\n
        next();\n
        expect(_parenL);\n
        clause.param = parseIdent();\n
        if (strict && isStrictBadIdWord(clause.param.name))\n
          raise(clause.param.start, "Binding " + clause.param.name + " in strict mode");\n
        expect(_parenR);\n
        clause.guard = null;\n
        clause.body = parseBlock();\n
        node.handler = finishNode(clause, "CatchClause");\n
      }\n
      node.guardedHandlers = empty;\n
      node.finalizer = eat(_finally) ? parseBlock() : null;\n
      if (!node.handler && !node.finalizer)\n
        raise(node.start, "Missing catch or finally clause");\n
      return finishNode(node, "TryStatement");\n
\n
    case _var:\n
      next();\n
      parseVar(node);\n
      semicolon();\n
      return finishNode(node, "VariableDeclaration");\n
\n
    case _while:\n
      next();\n
      node.test = parseParenExpression();\n
      labels.push(loopLabel);\n
      node.body = parseStatement();\n
      labels.pop();\n
      return finishNode(node, "WhileStatement");\n
\n
    case _with:\n
      if (strict) raise(tokStart, "\'with\' in strict mode");\n
      next();\n
      node.object = parseParenExpression();\n
      node.body = parseStatement();\n
      return finishNode(node, "WithStatement");\n
\n
    case _braceL:\n
      return parseBlock();\n
\n
    case _semi:\n
      next();\n
      return finishNode(node, "EmptyStatement");\n
\n
      // If the statement does not start with a statement keyword or a\n
      // brace, it\'s an ExpressionStatement or LabeledStatement. We\n
      // simply start parsing an expression, and afterwards, if the\n
      // next token is a colon and the expression was a simple\n
      // Identifier node, we switch to interpreting it as a label.\n
\n
    default:\n
      var maybeName = tokVal, expr = parseExpression();\n
      if (starttype === _name && expr.type === "Identifier" && eat(_colon)) {\n
        for (var i = 0; i < labels.length; ++i)\n
          if (labels[i].name === maybeName) raise(expr.start, "Label \'" + maybeName + "\' is already declared");\n
        var kind = tokType.isLoop ? "loop" : tokType === _switch ? "switch" : null;\n
        labels.push({name: maybeName, kind: kind});\n
        node.body = parseStatement();\n
        labels.pop();\n
        node.label = expr;\n
        return finishNode(node, "LabeledStatement");\n
      } else {\n
        node.expression = expr;\n
        semicolon();\n
        return finishNode(node, "ExpressionStatement");\n
      }\n
    }\n
  }\n
\n
  // Used for constructs like `switch` and `if` that insist on\n
  // parentheses around their expression.\n
\n
  function parseParenExpression() {\n
    expect(_parenL);\n
    var val = parseExpression();\n
    expect(_parenR);\n
    return val;\n
  }\n
\n
  // Parse a semicolon-enclosed block of statements, handling `"use\n
  // strict"` declarations when `allowStrict` is true (used for\n
  // function bodies).\n
\n
  function parseBlock(allowStrict) {\n
    var node = startNode(), first = true, strict = false, oldStrict;\n
    node.body = [];\n
    expect(_braceL);\n
    while (!eat(_braceR)) {\n
      var stmt = parseStatement();\n
      node.body.push(stmt);\n
      if (first && allowStrict && isUseStrict(stmt)) {\n
        oldStrict = strict;\n
        setStrict(strict = true);\n
      }\n
      first = false;\n
    }\n
    if (strict && !oldStrict) setStrict(false);\n
    return finishNode(node, "BlockStatement");\n
  }\n
\n
  // Parse a regular `for` loop. The disambiguation code in\n
  // `parseStatement` will already have parsed the init statement or\n
  // expression.\n
\n
  function parseFor(node, init) {\n
    node.init = init;\n
    expect(_semi);\n
    node.test = tokType === _semi ? null : parseExpression();\n
    expect(_semi);\n
    node.update = tokType === _parenR ? null : parseExpression();\n
    expect(_parenR);\n
    node.body = parseStatement();\n
    labels.pop();\n
    return finishNode(node, "ForStatement");\n
  }\n
\n
  // Parse a `for`/`in` loop.\n
\n
  function parseForIn(node, init) {\n
    node.left = init;\n
    node.right = parseExpression();\n
    expect(_parenR);\n
    node.body = parseStatement();\n
    labels.pop();\n
    return finishNode(node, "ForInStatement");\n
  }\n
\n
  // Parse a list of variable declarations.\n
\n
  function parseVar(node, noIn) {\n
    node.declarations = [];\n
    node.kind = "var";\n
    for (;;) {\n
      var decl = startNode();\n
      decl.id = parseIdent();\n
      if (strict && isStrictBadIdWord(decl.id.name))\n
        raise(decl.id.start, "Binding " + decl.id.name + " in strict mode");\n
      decl.init = eat(_eq) ? parseExpression(true, noIn) : null;\n
      node.declarations.push(finishNode(decl, "VariableDeclarator"));\n
      if (!eat(_comma)) break;\n
    }\n
    return node;\n
  }\n
\n
  // ### Expression parsing\n
\n
  // These nest, from the most general expression type at the top to\n
  // \'atomic\', nondivisible expression types at the bottom. Most of\n
  // the functions will simply let the function(s) below them parse,\n
  // and, *if* the syntactic construct they handle is present, wrap\n
  // the AST node that the inner parser gave them in another node.\n
\n
  // Parse a full expression. The arguments are used to forbid comma\n
  // sequences (in argument lists, array literals, or object literals)\n
  // or the `in` operator (in for loops initalization expressions).\n
\n
  function parseExpression(noComma, noIn) {\n
    var expr = parseMaybeAssign(noIn);\n
    if (!noComma && tokType === _comma) {\n
      var node = startNodeFrom(expr);\n
      node.expressions = [expr];\n
      while (eat(_comma)) node.expressions.push(parseMaybeAssign(noIn));\n
      return finishNode(node, "SequenceExpression");\n
    }\n
    return expr;\n
  }\n
\n
  // Parse an assignment expression. This includes applications of\n
  // operators like `+=`.\n
\n
  function parseMaybeAssign(noIn) {\n
    var left = parseMaybeConditional(noIn);\n
    if (tokType.isAssign) {\n
      var node = startNodeFrom(left);\n
      node.operator = tokVal;\n
      node.left = left;\n
      next();\n
      node.right = parseMaybeAssign(noIn);\n
      checkLVal(left);\n
      return finishNode(node, "AssignmentExpression");\n
    }\n
    return left;\n
  }\n
\n
  // Parse a ternary conditional (`?:`) operator.\n
\n
  function parseMaybeConditional(noIn) {\n
    var expr = parseExprOps(noIn);\n
    if (eat(_question)) {\n
      var node = startNodeFrom(expr);\n
      node.test = expr;\n
      node.consequent = parseExpression(true);\n
      expect(_colon);\n
      node.alternate = parseExpression(true, noIn);\n
      return finishNode(node, "ConditionalExpression");\n
    }\n
    return expr;\n
  }\n
\n
  // Start the precedence parser.\n
\n
  function parseExprOps(noIn) {\n
    return parseExprOp(parseMaybeUnary(), -1, noIn);\n
  }\n
\n
  // Parse binary operators with the operator precedence parsing\n
  // algorithm. `left` is the left-hand side of the operator.\n
  // `minPrec` provides context that allows the function to stop and\n
  // defer further parser to one of its callers when it encounters an\n
  // operator that has a lower precedence than the set it is parsing.\n
\n
  function parseExprOp(left, minPrec, noIn) {\n
    var prec = tokType.binop;\n
    if (prec != null && (!noIn || tokType !== _in)) {\n
      if (prec > minPrec) {\n
        var node = startNodeFrom(left);\n
        node.left = left;\n
        node.operator = tokVal;\n
        var op = tokType;\n
        next();\n
        node.right = parseExprOp(parseMaybeUnary(), prec, noIn);\n
        var exprNode = finishNode(node, (op === _logicalOR || op === _logicalAND) ? "LogicalExpression" : "BinaryExpression");\n
        return parseExprOp(exprNode, minPrec, noIn);\n
      }\n
    }\n
    return left;\n
  }\n
\n
  // Parse unary operators, both prefix and postfix.\n
\n
  function parseMaybeUnary() {\n
    if (tokType.prefix) {\n
      var node = startNode(), update = tokType.isUpdate;\n
      node.operator = tokVal;\n
      node.prefix = true;\n
      tokRegexpAllowed = true;\n
      next();\n
      node.argument = parseMaybeUnary();\n
      if (update) checkLVal(node.argument);\n
      else if (strict && node.operator === "delete" &&\n
               node.argument.type === "Identifier")\n
        raise(node.start, "Deleting local variable in strict mode");\n
      return finishNode(node, update ? "UpdateExpression" : "UnaryExpression");\n
    }\n
    var expr = parseExprSubscripts();\n
    while (tokType.postfix && !canInsertSemicolon()) {\n
      var node = startNodeFrom(expr);\n
      node.operator = tokVal;\n
      node.prefix = false;\n
      node.argument = expr;\n
      checkLVal(expr);\n
      next();\n
      expr = finishNode(node, "UpdateExpression");\n
    }\n
    return expr;\n
  }\n
\n
  // Parse call, dot, and `[]`-subscript expressions.\n
\n
  function parseExprSubscripts() {\n
    return parseSubscripts(parseExprAtom());\n
  }\n
\n
  function parseSubscripts(base, noCalls) {\n
    if (eat(_dot)) {\n
      var node = startNodeFrom(base);\n
      node.object = base;\n
      node.property = parseIdent(true);\n
      node.computed = false;\n
      return parseSubscripts(finishNode(node, "MemberExpression"), noCalls);\n
    } else if (eat(_bracketL)) {\n
      var node = startNodeFrom(base);\n
      node.object = base;\n
      node.property = parseExpression();\n
      node.computed = true;\n
      expect(_bracketR);\n
      return parseSubscripts(finishNode(node, "MemberExpression"), noCalls);\n
    } else if (!noCalls && eat(_parenL)) {\n
      var node = startNodeFrom(base);\n
      node.callee = base;\n
      node.arguments = parseExprList(_parenR, false);\n
      return parseSubscripts(finishNode(node, "CallExpression"), noCalls);\n
    } else return base;\n
  }\n
\n
  // Parse an atomic expression — either a single token that is an\n
  // expression, an expression started by a keyword like `function` or\n
  // `new`, or an expression wrapped in punctuation like `()`, `[]`,\n
  // or `{}`.\n
\n
  function parseExprAtom() {\n
    switch (tokType) {\n
    case _this:\n
      var node = startNode();\n
      next();\n
      return finishNode(node, "ThisExpression");\n
    case _name:\n
      return parseIdent();\n
    case _num: case _string: case _regexp:\n
      var node = startNode();\n
      node.value = tokVal;\n
      node.raw = input.slice(tokStart, tokEnd);\n
      next();\n
      return finishNode(node, "Literal");\n
\n
    case _null: case _true: case _false:\n
      var node = startNode();\n
      node.value = tokType.atomValue;\n
      node.raw = tokType.keyword;\n
      next();\n
      return finishNode(node, "Literal");\n
\n
    case _parenL:\n
      var tokStartLoc1 = tokStartLoc, tokStart1 = tokStart;\n
      next();\n
      var val = parseExpression();\n
      val.start = tokStart1;\n
      val.end = tokEnd;\n
      if (options.locations) {\n
        val.loc.start = tokStartLoc1;\n
        val.loc.end = tokEndLoc;\n
      }\n
      if (options.ranges)\n
        val.range = [tokStart1, tokEnd];\n
      expect(_parenR);\n
      return val;\n
\n
    case _bracketL:\n
      var node = startNode();\n
      next();\n
      node.elements = parseExprList(_bracketR, true, true);\n
      return finishNode(node, "ArrayExpression");\n
\n
    case _braceL:\n
      return parseObj();\n
\n
    case _function:\n
      var node = startNode();\n
      next();\n
      return parseFunction(node, false);\n
\n
    case _new:\n
      return parseNew();\n
\n
    default:\n
      unexpected();\n
    }\n
  }\n
\n
  // New\'s precedence is slightly tricky. It must allow its argument\n
  // to be a `[]` or dot subscript expression, but not a call — at\n
  // least, not without wrapping it in parentheses. Thus, it uses the\n
\n
  function parseNew() {\n
    var node = startNode();\n
    next();\n
    node.callee = parseSubscripts(parseExprAtom(), true);\n
    if (eat(_parenL)) node.arguments = parseExprList(_parenR, false);\n
    else node.arguments = empty;\n
    return finishNode(node, "NewExpression");\n
  }\n
\n
  // Parse an object literal.\n
\n
  function parseObj() {\n
    var node = startNode(), first = true, sawGetSet = false;\n
    node.properties = [];\n
    next();\n
    while (!eat(_braceR)) {\n
      if (!first) {\n
        expect(_comma);\n
        if (options.allowTrailingCommas && eat(_braceR)) break;\n
      } else first = false;\n
\n
      var prop = {key: parsePropertyName()}, isGetSet = false, kind;\n
      if (eat(_colon)) {\n
        prop.value = parseExpression(true);\n
        kind = prop.kind = "init";\n
      } else if (options.ecmaVersion >= 5 && prop.key.type === "Identifier" &&\n
                 (prop.key.name === "get" || prop.key.name === "set")) {\n
        isGetSet = sawGetSet = true;\n
        kind = prop.kind = prop.key.name;\n
        prop.key = parsePropertyName();\n
        if (tokType !== _parenL) unexpected();\n
        prop.value = parseFunction(startNode(), false);\n
      } else unexpected();\n
\n
      // getters and setters are not allowed to clash — either with\n
      // each other or with an init property — and in strict mode,\n
      // init properties are also not allowed to be repeated.\n
\n
      if (prop.key.type === "Identifier" && (strict || sawGetSet)) {\n
        for (var i = 0; i < node.properties.length; ++i) {\n
          var other = node.properties[i];\n
          if (other.key.name === prop.key.name) {\n
            var conflict = kind == other.kind || isGetSet && other.kind === "init" ||\n
              kind === "init" && (other.kind === "get" || other.kind === "set");\n
            if (conflict && !strict && kind === "init" && other.kind === "init") conflict = false;\n
            if (conflict) raise(prop.key.start, "Redefinition of property");\n
          }\n
        }\n
      }\n
      node.properties.push(prop);\n
    }\n
    return finishNode(node, "ObjectExpression");\n
  }\n
\n
  function parsePropertyName() {\n
    if (tokType === _num || tokType === _string) return parseExprAtom();\n
    return parseIdent(true);\n
  }\n
\n
  // Parse a function declaration or literal (depending on the\n
  // `isStatement` parameter).\n
\n
  function parseFunction(node, isStatement) {\n
    if (tokType === _name) node.id = parseIdent();\n
    else if (isStatement) unexpected();\n
    else node.id = null;\n
    node.params = [];\n
    var first = true;\n
    expect(_parenL);\n
    while (!eat(_parenR)) {\n
      if (!first) expect(_comma); else first = false;\n
      node.params.push(parseIdent());\n
    }\n
\n
    // Start a new scope with regard to labels and the `inFunction`\n
    // flag (restore them to their old value afterwards).\n
    var oldInFunc = inFunction, oldLabels = labels;\n
    inFunction = true; labels = [];\n
    node.body = parseBlock(true);\n
    inFunction = oldInFunc; labels = oldLabels;\n
\n
    // If this is a strict mode function, verify that argument names\n
    // are not repeated, and it does not try to bind the words `eval`\n
    // or `arguments`.\n
    if (strict || node.body.body.length && isUseStrict(node.body.body[0])) {\n
      for (var i = node.id ? -1 : 0; i < node.params.length; ++i) {\n
        var id = i < 0 ? node.id : node.params[i];\n
        if (isStrictReservedWord(id.name) || isStrictBadIdWord(id.name))\n
          raise(id.start, "Defining \'" + id.name + "\' in strict mode");\n
        if (i >= 0) for (var j = 0; j < i; ++j) if (id.name === node.params[j].name)\n
          raise(id.start, "Argument name clash in strict mode");\n
      }\n
    }\n
\n
    return finishNode(node, isStatement ? "FunctionDeclaration" : "FunctionExpression");\n
  }\n
\n
  // Parses a comma-separated list of expressions, and returns them as\n
  // an array. `close` is the token type that ends the list, and\n
  // `allowEmpty` can be turned on to allow subsequent commas with\n
  // nothing in between them to be parsed as `null` (which is needed\n
  // for array literals).\n
\n
  function parseExprList(close, allowTrailingComma, allowEmpty) {\n
    var elts = [], first = true;\n
    while (!eat(close)) {\n
      if (!first) {\n
        expect(_comma);\n
        if (allowTrailingComma && options.allowTrailingCommas && eat(close)) break;\n
      } else first = false;\n
\n
      if (allowEmpty && tokType === _comma) elts.push(null);\n
      else elts.push(parseExpression(true));\n
    }\n
    return elts;\n
  }\n
\n
  // Parse the next token as an identifier. If `liberal` is true (used\n
  // when parsing properties), it will also convert keywords into\n
  // identifiers.\n
\n
  function parseIdent(liberal) {\n
    var node = startNode();\n
    if (liberal && options.forbidReserved == "everywhere") liberal = false;\n
    if (tokType === _name) {\n
      if (!liberal &&\n
          (options.forbidReserved &&\n
           (options.ecmaVersion === 3 ? isReservedWord3 : isReservedWord5)(tokVal) ||\n
           strict && isStrictReservedWord(tokVal)) &&\n
          input.slice(tokStart, tokEnd).indexOf("\\\\") == -1)\n
        raise(tokStart, "The keyword \'" + tokVal + "\' is reserved");\n
      node.name = tokVal;\n
    } else if (liberal && tokType.keyword) {\n
      node.name = tokType.keyword;\n
    } else {\n
      unexpected();\n
    }\n
    tokRegexpAllowed = false;\n
    next();\n
    return finishNode(node, "Identifier");\n
  }\n
\n
});\n


]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
