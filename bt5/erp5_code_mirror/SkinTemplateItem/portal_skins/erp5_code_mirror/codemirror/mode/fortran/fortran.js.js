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
            <value> <string>ts21897144.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>fortran.js</string> </value>
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
CodeMirror.defineMode("fortran", function() {\n
  function words(array) {\n
    var keys = {};\n
    for (var i = 0; i < array.length; ++i) {\n
      keys[array[i]] = true;\n
    }\n
    return keys;\n
  }\n
\n
  var keywords = words([\n
                  "abstract", "accept", "allocatable", "allocate",\n
                  "array", "assign", "asynchronous", "backspace",\n
                  "bind", "block", "byte", "call", "case",\n
                  "class", "close", "common", "contains",\n
                  "continue", "cycle", "data", "deallocate",\n
                  "decode", "deferred", "dimension", "do",\n
                  "elemental", "else", "encode", "end",\n
                  "endif", "entry", "enumerator", "equivalence",\n
                  "exit", "external", "extrinsic", "final",\n
                  "forall", "format", "function", "generic",\n
                  "go", "goto", "if", "implicit", "import", "include",\n
                  "inquire", "intent", "interface", "intrinsic",\n
                  "module", "namelist", "non_intrinsic",\n
                  "non_overridable", "none", "nopass",\n
                  "nullify", "open", "optional", "options",\n
                  "parameter", "pass", "pause", "pointer",\n
                  "print", "private", "program", "protected",\n
                  "public", "pure", "read", "recursive", "result",\n
                  "return", "rewind", "save", "select", "sequence",\n
                  "stop", "subroutine", "target", "then", "to", "type",\n
                  "use", "value", "volatile", "where", "while",\n
                  "write"]);\n
  var builtins = words(["abort", "abs", "access", "achar", "acos",\n
                          "adjustl", "adjustr", "aimag", "aint", "alarm",\n
                          "all", "allocated", "alog", "amax", "amin",\n
                          "amod", "and", "anint", "any", "asin",\n
                          "associated", "atan", "besj", "besjn", "besy",\n
                          "besyn", "bit_size", "btest", "cabs", "ccos",\n
                          "ceiling", "cexp", "char", "chdir", "chmod",\n
                          "clog", "cmplx", "command_argument_count",\n
                          "complex", "conjg", "cos", "cosh", "count",\n
                          "cpu_time", "cshift", "csin", "csqrt", "ctime",\n
                          "c_funloc", "c_loc", "c_associated", "c_null_ptr",\n
                          "c_null_funptr", "c_f_pointer", "c_null_char",\n
                          "c_alert", "c_backspace", "c_form_feed",\n
                          "c_new_line", "c_carriage_return",\n
                          "c_horizontal_tab", "c_vertical_tab", "dabs",\n
                          "dacos", "dasin", "datan", "date_and_time",\n
                          "dbesj", "dbesj", "dbesjn", "dbesy", "dbesy",\n
                          "dbesyn", "dble", "dcos", "dcosh", "ddim", "derf",\n
                          "derfc", "dexp", "digits", "dim", "dint", "dlog",\n
                          "dlog", "dmax", "dmin", "dmod", "dnint",\n
                          "dot_product", "dprod", "dsign", "dsinh",\n
                          "dsin", "dsqrt", "dtanh", "dtan", "dtime",\n
                          "eoshift", "epsilon", "erf", "erfc", "etime",\n
                          "exit", "exp", "exponent", "extends_type_of",\n
                          "fdate", "fget", "fgetc", "float", "floor",\n
                          "flush", "fnum", "fputc", "fput", "fraction",\n
                          "fseek", "fstat", "ftell", "gerror", "getarg",\n
                          "get_command", "get_command_argument",\n
                          "get_environment_variable", "getcwd",\n
                          "getenv", "getgid", "getlog", "getpid",\n
                          "getuid", "gmtime", "hostnm", "huge", "iabs",\n
                          "iachar", "iand", "iargc", "ibclr", "ibits",\n
                          "ibset", "ichar", "idate", "idim", "idint",\n
                          "idnint", "ieor", "ierrno", "ifix", "imag",\n
                          "imagpart", "index", "int", "ior", "irand",\n
                          "isatty", "ishft", "ishftc", "isign",\n
                          "iso_c_binding", "is_iostat_end", "is_iostat_eor",\n
                          "itime", "kill", "kind", "lbound", "len", "len_trim",\n
                          "lge", "lgt", "link", "lle", "llt", "lnblnk", "loc",\n
                          "log", "logical", "long", "lshift", "lstat", "ltime",\n
                          "matmul", "max", "maxexponent", "maxloc", "maxval",\n
                          "mclock", "merge", "move_alloc", "min", "minexponent",\n
                          "minloc", "minval", "mod", "modulo", "mvbits",\n
                          "nearest", "new_line", "nint", "not", "or", "pack",\n
                          "perror", "precision", "present", "product", "radix",\n
                          "rand", "random_number", "random_seed", "range",\n
                          "real", "realpart", "rename", "repeat", "reshape",\n
                          "rrspacing", "rshift", "same_type_as", "scale",\n
                          "scan", "second", "selected_int_kind",\n
                          "selected_real_kind", "set_exponent", "shape",\n
                          "short", "sign", "signal", "sinh", "sin", "sleep",\n
                          "sngl", "spacing", "spread", "sqrt", "srand", "stat",\n
                          "sum", "symlnk", "system", "system_clock", "tan",\n
                          "tanh", "time", "tiny", "transfer", "transpose",\n
                          "trim", "ttynam", "ubound", "umask", "unlink",\n
                          "unpack", "verify", "xor", "zabs", "zcos", "zexp",\n
                          "zlog", "zsin", "zsqrt"]);\n
\n
    var dataTypes =  words(["c_bool", "c_char", "c_double", "c_double_complex",\n
                     "c_float", "c_float_complex", "c_funptr", "c_int",\n
                     "c_int16_t", "c_int32_t", "c_int64_t", "c_int8_t",\n
                     "c_int_fast16_t", "c_int_fast32_t", "c_int_fast64_t",\n
                     "c_int_fast8_t", "c_int_least16_t", "c_int_least32_t",\n
                     "c_int_least64_t", "c_int_least8_t", "c_intmax_t",\n
                     "c_intptr_t", "c_long", "c_long_double",\n
                     "c_long_double_complex", "c_long_long", "c_ptr",\n
                     "c_short", "c_signed_char", "c_size_t", "character",\n
                     "complex", "double", "integer", "logical", "real"]);\n
  var isOperatorChar = /[+\\-*&=<>\\/\\:]/;\n
  var litOperator = new RegExp("(\\.and\\.|\\.or\\.|\\.eq\\.|\\.lt\\.|\\.le\\.|\\.gt\\.|\\.ge\\.|\\.ne\\.|\\.not\\.|\\.eqv\\.|\\.neqv\\.)", "i");\n
\n
  function tokenBase(stream, state) {\n
\n
    if (stream.match(litOperator)){\n
        return \'operator\';\n
    }\n
\n
    var ch = stream.next();\n
    if (ch == "!") {\n
      stream.skipToEnd();\n
      return "comment";\n
    }\n
    if (ch == \'"\' || ch == "\'") {\n
      state.tokenize = tokenString(ch);\n
      return state.tokenize(stream, state);\n
    }\n
    if (/[\\[\\]\\(\\),]/.test(ch)) {\n
      return null;\n
    }\n
    if (/\\d/.test(ch)) {\n
      stream.eatWhile(/[\\w\\.]/);\n
      return "number";\n
    }\n
    if (isOperatorChar.test(ch)) {\n
      stream.eatWhile(isOperatorChar);\n
      return "operator";\n
    }\n
    stream.eatWhile(/[\\w\\$_]/);\n
    var word = stream.current().toLowerCase();\n
\n
    if (keywords.hasOwnProperty(word)){\n
            return \'keyword\';\n
    }\n
    if (builtins.hasOwnProperty(word) || dataTypes.hasOwnProperty(word)) {\n
            return \'builtin\';\n
    }\n
    return "variable";\n
  }\n
\n
  function tokenString(quote) {\n
    return function(stream, state) {\n
      var escaped = false, next, end = false;\n
      while ((next = stream.next()) != null) {\n
        if (next == quote && !escaped) {\n
            end = true;\n
            break;\n
        }\n
        escaped = !escaped && next == "\\\\";\n
      }\n
      if (end || !escaped) state.tokenize = null;\n
      return "string";\n
    };\n
  }\n
\n
  // Interface\n
\n
  return {\n
    startState: function() {\n
      return {tokenize: null};\n
    },\n
\n
    token: function(stream, state) {\n
      if (stream.eatSpace()) return null;\n
      var style = (state.tokenize || tokenBase)(stream, state);\n
      if (style == "comment" || style == "meta") return style;\n
      return style;\n
    }\n
  };\n
});\n
\n
CodeMirror.defineMIME("text/x-fortran", "fortran");\n
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
            <value> <int>8686</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
