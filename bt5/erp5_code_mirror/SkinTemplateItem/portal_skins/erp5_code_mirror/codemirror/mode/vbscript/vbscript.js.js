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
            <value> <string>ts21897135.33</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>vbscript.js</string> </value>
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
/*\n
For extra ASP classic objects, initialize CodeMirror instance with this option:\n
    isASP: true\n
\n
E.G.:\n
    var editor = CodeMirror.fromTextArea(document.getElementById("code"), {\n
        lineNumbers: true,\n
        isASP: true\n
      });\n
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
CodeMirror.defineMode("vbscript", function(conf, parserConf) {\n
    var ERRORCLASS = \'error\';\n
\n
    function wordRegexp(words) {\n
        return new RegExp("^((" + words.join(")|(") + "))\\\\b", "i");\n
    }\n
\n
    var singleOperators = new RegExp("^[\\\\+\\\\-\\\\*/&\\\\\\\\\\\\^<>=]");\n
    var doubleOperators = new RegExp("^((<>)|(<=)|(>=))");\n
    var singleDelimiters = new RegExp(\'^[\\\\.,]\');\n
    var brakets = new RegExp(\'^[\\\\(\\\\)]\');\n
    var identifiers = new RegExp("^[A-Za-z][_A-Za-z0-9]*");\n
\n
    var openingKeywords = [\'class\',\'sub\',\'select\',\'while\',\'if\',\'function\', \'property\', \'with\', \'for\'];\n
    var middleKeywords = [\'else\',\'elseif\',\'case\'];\n
    var endKeywords = [\'next\',\'loop\',\'wend\'];\n
\n
    var wordOperators = wordRegexp([\'and\', \'or\', \'not\', \'xor\', \'is\', \'mod\', \'eqv\', \'imp\']);\n
    var commonkeywords = [\'dim\', \'redim\', \'then\',  \'until\', \'randomize\',\n
                          \'byval\',\'byref\',\'new\',\'property\', \'exit\', \'in\',\n
                          \'const\',\'private\', \'public\',\n
                          \'get\',\'set\',\'let\', \'stop\', \'on error resume next\', \'on error goto 0\', \'option explicit\', \'call\', \'me\'];\n
\n
    //This list was from: http://msdn.microsoft.com/en-us/library/f8tbc79x(v=vs.84).aspx\n
    var atomWords = [\'true\', \'false\', \'nothing\', \'empty\', \'null\'];\n
    //This list was from: http://msdn.microsoft.com/en-us/library/3ca8tfek(v=vs.84).aspx\n
    var builtinFuncsWords = [\'abs\', \'array\', \'asc\', \'atn\', \'cbool\', \'cbyte\', \'ccur\', \'cdate\', \'cdbl\', \'chr\', \'cint\', \'clng\', \'cos\', \'csng\', \'cstr\', \'date\', \'dateadd\', \'datediff\', \'datepart\',\n
                        \'dateserial\', \'datevalue\', \'day\', \'escape\', \'eval\', \'execute\', \'exp\', \'filter\', \'formatcurrency\', \'formatdatetime\', \'formatnumber\', \'formatpercent\', \'getlocale\', \'getobject\',\n
                        \'getref\', \'hex\', \'hour\', \'inputbox\', \'instr\', \'instrrev\', \'int\', \'fix\', \'isarray\', \'isdate\', \'isempty\', \'isnull\', \'isnumeric\', \'isobject\', \'join\', \'lbound\', \'lcase\', \'left\',\n
                        \'len\', \'loadpicture\', \'log\', \'ltrim\', \'rtrim\', \'trim\', \'maths\', \'mid\', \'minute\', \'month\', \'monthname\', \'msgbox\', \'now\', \'oct\', \'replace\', \'rgb\', \'right\', \'rnd\', \'round\',\n
                        \'scriptengine\', \'scriptenginebuildversion\', \'scriptenginemajorversion\', \'scriptengineminorversion\', \'second\', \'setlocale\', \'sgn\', \'sin\', \'space\', \'split\', \'sqr\', \'strcomp\',\n
                        \'string\', \'strreverse\', \'tan\', \'time\', \'timer\', \'timeserial\', \'timevalue\', \'typename\', \'ubound\', \'ucase\', \'unescape\', \'vartype\', \'weekday\', \'weekdayname\', \'year\'];\n
\n
    //This list was from: http://msdn.microsoft.com/en-us/library/ydz4cfk3(v=vs.84).aspx\n
    var builtinConsts = [\'vbBlack\', \'vbRed\', \'vbGreen\', \'vbYellow\', \'vbBlue\', \'vbMagenta\', \'vbCyan\', \'vbWhite\', \'vbBinaryCompare\', \'vbTextCompare\',\n
                         \'vbSunday\', \'vbMonday\', \'vbTuesday\', \'vbWednesday\', \'vbThursday\', \'vbFriday\', \'vbSaturday\', \'vbUseSystemDayOfWeek\', \'vbFirstJan1\', \'vbFirstFourDays\', \'vbFirstFullWeek\',\n
                         \'vbGeneralDate\', \'vbLongDate\', \'vbShortDate\', \'vbLongTime\', \'vbShortTime\', \'vbObjectError\',\n
                         \'vbOKOnly\', \'vbOKCancel\', \'vbAbortRetryIgnore\', \'vbYesNoCancel\', \'vbYesNo\', \'vbRetryCancel\', \'vbCritical\', \'vbQuestion\', \'vbExclamation\', \'vbInformation\', \'vbDefaultButton1\', \'vbDefaultButton2\',\n
                         \'vbDefaultButton3\', \'vbDefaultButton4\', \'vbApplicationModal\', \'vbSystemModal\', \'vbOK\', \'vbCancel\', \'vbAbort\', \'vbRetry\', \'vbIgnore\', \'vbYes\', \'vbNo\',\n
                         \'vbCr\', \'VbCrLf\', \'vbFormFeed\', \'vbLf\', \'vbNewLine\', \'vbNullChar\', \'vbNullString\', \'vbTab\', \'vbVerticalTab\', \'vbUseDefault\', \'vbTrue\', \'vbFalse\',\n
                         \'vbEmpty\', \'vbNull\', \'vbInteger\', \'vbLong\', \'vbSingle\', \'vbDouble\', \'vbCurrency\', \'vbDate\', \'vbString\', \'vbObject\', \'vbError\', \'vbBoolean\', \'vbVariant\', \'vbDataObject\', \'vbDecimal\', \'vbByte\', \'vbArray\'];\n
    //This list was from: http://msdn.microsoft.com/en-us/library/hkc375ea(v=vs.84).aspx\n
    var builtinObjsWords = [\'WScript\', \'err\', \'debug\', \'RegExp\'];\n
    var knownProperties = [\'description\', \'firstindex\', \'global\', \'helpcontext\', \'helpfile\', \'ignorecase\', \'length\', \'number\', \'pattern\', \'source\', \'value\', \'count\'];\n
    var knownMethods = [\'clear\', \'execute\', \'raise\', \'replace\', \'test\', \'write\', \'writeline\', \'close\', \'open\', \'state\', \'eof\', \'update\', \'addnew\', \'end\', \'createobject\', \'quit\'];\n
\n
    var aspBuiltinObjsWords = [\'server\', \'response\', \'request\', \'session\', \'application\'];\n
    var aspKnownProperties = [\'buffer\', \'cachecontrol\', \'charset\', \'contenttype\', \'expires\', \'expiresabsolute\', \'isclientconnected\', \'pics\', \'status\', //response\n
                              \'clientcertificate\', \'cookies\', \'form\', \'querystring\', \'servervariables\', \'totalbytes\', //request\n
                              \'contents\', \'staticobjects\', //application\n
                              \'codepage\', \'lcid\', \'sessionid\', \'timeout\', //session\n
                              \'scripttimeout\']; //server\n
    var aspKnownMethods = [\'addheader\', \'appendtolog\', \'binarywrite\', \'end\', \'flush\', \'redirect\', //response\n
                           \'binaryread\', //request\n
                           \'remove\', \'removeall\', \'lock\', \'unlock\', //application\n
                           \'abandon\', //session\n
                           \'getlasterror\', \'htmlencode\', \'mappath\', \'transfer\', \'urlencode\']; //server\n
\n
    var knownWords = knownMethods.concat(knownProperties);\n
\n
    builtinObjsWords = builtinObjsWords.concat(builtinConsts);\n
\n
    if (conf.isASP){\n
        builtinObjsWords = builtinObjsWords.concat(aspBuiltinObjsWords);\n
        knownWords = knownWords.concat(aspKnownMethods, aspKnownProperties);\n
    };\n
\n
    var keywords = wordRegexp(commonkeywords);\n
    var atoms = wordRegexp(atomWords);\n
    var builtinFuncs = wordRegexp(builtinFuncsWords);\n
    var builtinObjs = wordRegexp(builtinObjsWords);\n
    var known = wordRegexp(knownWords);\n
    var stringPrefixes = \'"\';\n
\n
    var opening = wordRegexp(openingKeywords);\n
    var middle = wordRegexp(middleKeywords);\n
    var closing = wordRegexp(endKeywords);\n
    var doubleClosing = wordRegexp([\'end\']);\n
    var doOpening = wordRegexp([\'do\']);\n
    var noIndentWords = wordRegexp([\'on error resume next\', \'exit\']);\n
    var comment = wordRegexp([\'rem\']);\n
\n
\n
    function indent(_stream, state) {\n
      state.currentIndent++;\n
    }\n
\n
    function dedent(_stream, state) {\n
      state.currentIndent--;\n
    }\n
    // tokenizers\n
    function tokenBase(stream, state) {\n
        if (stream.eatSpace()) {\n
            return \'space\';\n
            //return null;\n
        }\n
\n
        var ch = stream.peek();\n
\n
        // Handle Comments\n
        if (ch === "\'") {\n
            stream.skipToEnd();\n
            return \'comment\';\n
        }\n
        if (stream.match(comment)){\n
            stream.skipToEnd();\n
            return \'comment\';\n
        }\n
\n
\n
        // Handle Number Literals\n
        if (stream.match(/^((&H)|(&O))?[0-9\\.]/i, false) && !stream.match(/^((&H)|(&O))?[0-9\\.]+[a-z_]/i, false)) {\n
            var floatLiteral = false;\n
            // Floats\n
            if (stream.match(/^\\d*\\.\\d+/i)) { floatLiteral = true; }\n
            else if (stream.match(/^\\d+\\.\\d*/)) { floatLiteral = true; }\n
            else if (stream.match(/^\\.\\d+/)) { floatLiteral = true; }\n
\n
            if (floatLiteral) {\n
                // Float literals may be "imaginary"\n
                stream.eat(/J/i);\n
                return \'number\';\n
            }\n
            // Integers\n
            var intLiteral = false;\n
            // Hex\n
            if (stream.match(/^&H[0-9a-f]+/i)) { intLiteral = true; }\n
            // Octal\n
            else if (stream.match(/^&O[0-7]+/i)) { intLiteral = true; }\n
            // Decimal\n
            else if (stream.match(/^[1-9]\\d*F?/)) {\n
                // Decimal literals may be "imaginary"\n
                stream.eat(/J/i);\n
                // TODO - Can you have imaginary longs?\n
                intLiteral = true;\n
            }\n
            // Zero by itself with no other piece of number.\n
            else if (stream.match(/^0(?![\\dx])/i)) { intLiteral = true; }\n
            if (intLiteral) {\n
                // Integer literals may be "long"\n
                stream.eat(/L/i);\n
                return \'number\';\n
            }\n
        }\n
\n
        // Handle Strings\n
        if (stream.match(stringPrefixes)) {\n
            state.tokenize = tokenStringFactory(stream.current());\n
            return state.tokenize(stream, state);\n
        }\n
\n
        // Handle operators and Delimiters\n
        if (stream.match(doubleOperators)\n
            || stream.match(singleOperators)\n
            || stream.match(wordOperators)) {\n
            return \'operator\';\n
        }\n
        if (stream.match(singleDelimiters)) {\n
            return null;\n
        }\n
\n
        if (stream.match(brakets)) {\n
            return "bracket";\n
        }\n
\n
        if (stream.match(noIndentWords)) {\n
            state.doInCurrentLine = true;\n
\n
            return \'keyword\';\n
        }\n
\n
        if (stream.match(doOpening)) {\n
            indent(stream,state);\n
            state.doInCurrentLine = true;\n
\n
            return \'keyword\';\n
        }\n
        if (stream.match(opening)) {\n
            if (! state.doInCurrentLine)\n
              indent(stream,state);\n
            else\n
              state.doInCurrentLine = false;\n
\n
            return \'keyword\';\n
        }\n
        if (stream.match(middle)) {\n
            return \'keyword\';\n
        }\n
\n
\n
        if (stream.match(doubleClosing)) {\n
            dedent(stream,state);\n
            dedent(stream,state);\n
\n
            return \'keyword\';\n
        }\n
        if (stream.match(closing)) {\n
            if (! state.doInCurrentLine)\n
              dedent(stream,state);\n
            else\n
              state.doInCurrentLine = false;\n
\n
            return \'keyword\';\n
        }\n
\n
        if (stream.match(keywords)) {\n
            return \'keyword\';\n
        }\n
\n
        if (stream.match(atoms)) {\n
            return \'atom\';\n
        }\n
\n
        if (stream.match(known)) {\n
            return \'variable-2\';\n
        }\n
\n
        if (stream.match(builtinFuncs)) {\n
            return \'builtin\';\n
        }\n
\n
        if (stream.match(builtinObjs)){\n
            return \'variable-2\';\n
        }\n
\n
        if (stream.match(identifiers)) {\n
            return \'variable\';\n
        }\n
\n
        // Handle non-detected items\n
        stream.next();\n
        return ERRORCLASS;\n
    }\n
\n
    function tokenStringFactory(delimiter) {\n
        var singleline = delimiter.length == 1;\n
        var OUTCLASS = \'string\';\n
\n
        return function(stream, state) {\n
            while (!stream.eol()) {\n
                stream.eatWhile(/[^\'"]/);\n
                if (stream.match(delimiter)) {\n
                    state.tokenize = tokenBase;\n
                    return OUTCLASS;\n
                } else {\n
                    stream.eat(/[\'"]/);\n
                }\n
            }\n
            if (singleline) {\n
                if (parserConf.singleLineStringErrors) {\n
                    return ERRORCLASS;\n
                } else {\n
                    state.tokenize = tokenBase;\n
                }\n
            }\n
            return OUTCLASS;\n
        };\n
    }\n
\n
\n
    function tokenLexer(stream, state) {\n
        var style = state.tokenize(stream, state);\n
        var current = stream.current();\n
\n
        // Handle \'.\' connected identifiers\n
        if (current === \'.\') {\n
            style = state.tokenize(stream, state);\n
\n
            current = stream.current();\n
            if (style && (style.substr(0, 8) === \'variable\' || style===\'builtin\' || style===\'keyword\')){//|| knownWords.indexOf(current.substring(1)) > -1) {\n
                if (style === \'builtin\' || style === \'keyword\') style=\'variable\';\n
                if (knownWords.indexOf(current.substr(1)) > -1) style=\'variable-2\';\n
\n
                return style;\n
            } else {\n
                return ERRORCLASS;\n
            }\n
        }\n
\n
        return style;\n
    }\n
\n
    var external = {\n
        electricChars:"dDpPtTfFeE ",\n
        startState: function() {\n
            return {\n
              tokenize: tokenBase,\n
              lastToken: null,\n
              currentIndent: 0,\n
              nextLineIndent: 0,\n
              doInCurrentLine: false,\n
              ignoreKeyword: false\n
\n
\n
          };\n
        },\n
\n
        token: function(stream, state) {\n
            if (stream.sol()) {\n
              state.currentIndent += state.nextLineIndent;\n
              state.nextLineIndent = 0;\n
              state.doInCurrentLine = 0;\n
            }\n
            var style = tokenLexer(stream, state);\n
\n
            state.lastToken = {style:style, content: stream.current()};\n
\n
            if (style===\'space\') style=null;\n
\n
            return style;\n
        },\n
\n
        indent: function(state, textAfter) {\n
            var trueText = textAfter.replace(/^\\s+|\\s+$/g, \'\') ;\n
            if (trueText.match(closing) || trueText.match(doubleClosing) || trueText.match(middle)) return conf.indentUnit*(state.currentIndent-1);\n
            if(state.currentIndent < 0) return 0;\n
            return state.currentIndent * conf.indentUnit;\n
        }\n
\n
    };\n
    return external;\n
});\n
\n
CodeMirror.defineMIME("text/vbscript", "vbscript");\n
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
            <value> <int>13793</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
