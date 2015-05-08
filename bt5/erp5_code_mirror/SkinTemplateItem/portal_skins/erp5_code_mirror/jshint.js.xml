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
            <value> <string>ts29784793.18</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jshint.js</string> </value>
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
            <value> <int>163537</int> </value>
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

/*!\n
 * JSHint, by JSHint Community.\n
 *\n
 * Licensed under the same slightly modified MIT license that JSLint is.\n
 * It stops evil-doers everywhere.\n
 *\n
 * JSHint is a derivative work of JSLint:\n
 *\n
 *   Copyright (c) 2002 Douglas Crockford  (www.JSLint.com)\n
 *\n
 *   Permission is hereby granted, free of charge, to any person obtaining\n
 *   a copy of this software and associated documentation files (the "Software"),\n
 *   to deal in the Software without restriction, including without limitation\n
 *   the rights to use, copy, modify, merge, publish, distribute, sublicense,\n
 *   and/or sell copies of the Software, and to permit persons to whom\n
 *   the Software is furnished to do so, subject to the following conditions:\n
 *\n
 *   The above copyright notice and this permission notice shall be included\n
 *   in all copies or substantial portions of the Software.\n
 *\n
 *   The Software shall be used for Good, not Evil.\n
 *\n
 *   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n
 *   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n
 *   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n
 *   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n
 *   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING\n
 *   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER\n
 *   DEALINGS IN THE SOFTWARE.\n
 *\n
 * JSHint was forked from 2010-12-16 edition of JSLint.\n
 *\n
 */\n
\n
/*\n
 JSHINT is a global function. It takes two parameters.\n
\n
     var myResult = JSHINT(source, option);\n
\n
 The first parameter is either a string or an array of strings. If it is a\n
 string, it will be split on \'\\n\' or \'\\r\'. If it is an array of strings, it\n
 is assumed that each string represents one line. The source can be a\n
 JavaScript text or a JSON text.\n
\n
 The second parameter is an optional object of options which control the\n
 operation of JSHINT. Most of the options are booleans: They are all\n
 optional and have a default value of false. One of the options, predef,\n
 can be an array of names, which will be used to declare global variables,\n
 or an object whose keys are used as global names, with a boolean value\n
 that determines if they are assignable.\n
\n
 If it checks out, JSHINT returns true. Otherwise, it returns false.\n
\n
 If false, you can inspect JSHINT.errors to find out the problems.\n
 JSHINT.errors is an array of objects containing these members:\n
\n
 {\n
     line      : The line (relative to 0) at which the lint was found\n
     character : The character (relative to 0) at which the lint was found\n
     reason    : The problem\n
     evidence  : The text line in which the problem occurred\n
     raw       : The raw message before the details were inserted\n
     a         : The first detail\n
     b         : The second detail\n
     c         : The third detail\n
     d         : The fourth detail\n
 }\n
\n
 If a fatal error was found, a null will be the last element of the\n
 JSHINT.errors array.\n
\n
 You can request a Function Report, which shows all of the functions\n
 and the parameters and vars that they use. This can be used to find\n
 implied global variables and other problems. The report is in HTML and\n
 can be inserted in an HTML <body>.\n
\n
     var myReport = JSHINT.report(limited);\n
\n
 If limited is true, then the report will be limited to only errors.\n
\n
 You can request a data structure which contains JSHint\'s results.\n
\n
     var myData = JSHINT.data();\n
\n
 It returns a structure with this form:\n
\n
 {\n
     errors: [\n
         {\n
             line: NUMBER,\n
             character: NUMBER,\n
             reason: STRING,\n
             evidence: STRING\n
         }\n
     ],\n
     functions: [\n
         name: STRING,\n
         line: NUMBER,\n
         last: NUMBER,\n
         param: [\n
             STRING\n
         ],\n
         closure: [\n
             STRING\n
         ],\n
         var: [\n
             STRING\n
         ],\n
         exception: [\n
             STRING\n
         ],\n
         outer: [\n
             STRING\n
         ],\n
         unused: [\n
             STRING\n
         ],\n
         global: [\n
             STRING\n
         ],\n
         label: [\n
             STRING\n
         ]\n
     ],\n
     globals: [\n
         STRING\n
     ],\n
     member: {\n
         STRING: NUMBER\n
     },\n
     unused: [\n
         {\n
             name: STRING,\n
             line: NUMBER\n
         }\n
     ],\n
     implieds: [\n
         {\n
             name: STRING,\n
             line: NUMBER\n
         }\n
     ],\n
     urls: [\n
         STRING\n
     ],\n
     json: BOOLEAN\n
 }\n
\n
 Empty arrays will not be included.\n
\n
*/\n
\n
/*jshint\n
 evil: true, nomen: false, onevar: false, regexp: false, strict: true, boss: true,\n
 undef: true, maxlen: 100, indent:4\n
*/\n
\n
/*members "\\b", "\\t", "\\n", "\\f", "\\r", "!=", "!==", "\\"", "%", "(begin)",\n
 "(breakage)", "(context)", "(error)", "(global)", "(identifier)", "(last)",\n
 "(line)", "(loopage)", "(name)", "(onevar)", "(params)", "(scope)",\n
 "(statement)", "(verb)", "*", "+", "++", "-", "--", "\\/", "<", "<=", "==",\n
 "===", ">", ">=", $, $$, $A, $F, $H, $R, $break, $continue, $w, Abstract, Ajax,\n
 __filename, __dirname, ActiveXObject, Array, ArrayBuffer, ArrayBufferView, Audio,\n
 Autocompleter, Assets, Boolean, Builder, Buffer, Browser, COM, CScript, Canvas,\n
 CustomAnimation, Class, Control, Chain, Color, Cookie, Core, DataView, Date,\n
 Debug, Draggable, Draggables, Droppables, Document, DomReady, DOMReady, DOMParser, Drag,\n
 E, Enumerator, Enumerable, Element, Elements, Error, Effect, EvalError, Event,\n
 Events, FadeAnimation, Field, Flash, Float32Array, Float64Array, Form,\n
 FormField, Frame, FormData, Function, Fx, GetObject, Group, Hash, HotKey,\n
 HTMLElement, HTMLAnchorElement, HTMLBaseElement, HTMLBlockquoteElement,\n
 HTMLBodyElement, HTMLBRElement, HTMLButtonElement, HTMLCanvasElement, HTMLDirectoryElement,\n
 HTMLDivElement, HTMLDListElement, HTMLFieldSetElement,\n
 HTMLFontElement, HTMLFormElement, HTMLFrameElement, HTMLFrameSetElement,\n
 HTMLHeadElement, HTMLHeadingElement, HTMLHRElement, HTMLHtmlElement,\n
 HTMLIFrameElement, HTMLImageElement, HTMLInputElement, HTMLIsIndexElement,\n
 HTMLLabelElement, HTMLLayerElement, HTMLLegendElement, HTMLLIElement,\n
 HTMLLinkElement, HTMLMapElement, HTMLMenuElement, HTMLMetaElement,\n
 HTMLModElement, HTMLObjectElement, HTMLOListElement, HTMLOptGroupElement,\n
 HTMLOptionElement, HTMLParagraphElement, HTMLParamElement, HTMLPreElement,\n
 HTMLQuoteElement, HTMLScriptElement, HTMLSelectElement, HTMLStyleElement,\n
 HtmlTable, HTMLTableCaptionElement, HTMLTableCellElement, HTMLTableColElement,\n
 HTMLTableElement, HTMLTableRowElement, HTMLTableSectionElement,\n
 HTMLTextAreaElement, HTMLTitleElement, HTMLUListElement, HTMLVideoElement,\n
 Iframe, IframeShim, Image, Int16Array, Int32Array, Int8Array,\n
 Insertion, InputValidator, JSON, Keyboard, Locale, LN10, LN2, LOG10E, LOG2E,\n
 MAX_VALUE, MIN_VALUE, Mask, Math, MenuItem, MessageChannel, MessageEvent, MessagePort,\n
 MoveAnimation, MooTools, Native, NEGATIVE_INFINITY, Number, Object, ObjectRange, Option,\n
 Options, OverText, PI, POSITIVE_INFINITY, PeriodicalExecuter, Point, Position, Prototype,\n
 RangeError, Rectangle, ReferenceError, RegExp, ResizeAnimation, Request, RotateAnimation,\n
 SQRT1_2, SQRT2, ScrollBar, ScriptEngine, ScriptEngineBuildVersion,\n
 ScriptEngineMajorVersion, ScriptEngineMinorVersion, Scriptaculous, Scroller,\n
 Slick, Slider, Selector, SharedWorker, String, Style, SyntaxError, Sortable, Sortables,\n
 SortableObserver, Sound, Spinner, System, Swiff, Text, TextArea, Template,\n
 Timer, Tips, Type, TypeError, Toggle, Try, "use strict", unescape, URI, URIError, URL,\n
 VBArray, WSH, WScript, XDomainRequest, Web, Window, XMLDOM, XMLHttpRequest, XMLSerializer,\n
 XPathEvaluator, XPathException, XPathExpression, XPathNamespace, XPathNSResolver, XPathResult,\n
 "\\\\", a, addEventListener, address, alert, apply, applicationCache, arguments, arity, asi, atob,\n
 b, basic, basicToken, bitwise, block, blur, boolOptions, boss, browser, btoa, c, call, callee,\n
 caller, cases, charAt, charCodeAt, character, clearInterval, clearTimeout,\n
 close, closed, closure, comment, condition, confirm, console, constructor,\n
 content, couch, create, css, curly, d, data, datalist, dd, debug, decodeURI,\n
 decodeURIComponent, defaultStatus, defineClass, deserialize, devel, document,\n
 dojo, dijit, dojox, define, else, emit, encodeURI, encodeURIComponent,\n
 entityify, eqeq, eqeqeq, eqnull, errors, es5, escape, esnext, eval, event, evidence, evil,\n
 ex, exception, exec, exps, expr, exports, FileReader, first, floor, focus,\n
 forin, fragment, frames, from, fromCharCode, fud, funcscope, funct, function, functions,\n
 g, gc, getComputedStyle, getRow, getter, getterToken, GLOBAL, global, globals, globalstrict,\n
 hasOwnProperty, help, history, i, id, identifier, immed, implieds, importPackage, include,\n
 indent, indexOf, init, ins, instanceOf, isAlpha, isApplicationRunning, isArray,\n
 isDigit, isFinite, isNaN, iterator, java, join, jshint,\n
 JSHINT, json, jquery, jQuery, keys, label, labelled, last, lastsemic, laxbreak, laxcomma,\n
 latedef, lbp, led, left, length, line, load, loadClass, localStorage, location,\n
 log, loopfunc, m, match, maxerr, maxlen, member,message, meta, module, moveBy,\n
 moveTo, mootools, multistr, name, navigator, new, newcap, noarg, node, noempty, nomen,\n
 nonew, nonstandard, nud, onbeforeunload, onblur, onerror, onevar, onecase, onfocus,\n
 onload, onresize, onunload, open, openDatabase, openURL, opener, opera, options, outer, param,\n
 parent, parseFloat, parseInt, passfail, plusplus, predef, print, process, prompt,\n
 proto, prototype, prototypejs, provides, push, quit, range, raw, reach, reason, regexp,\n
 readFile, readUrl, regexdash, removeEventListener, replace, report, require,\n
 reserved, resizeBy, resizeTo, resolvePath, resumeUpdates, respond, rhino, right,\n
 runCommand, scroll, screen, scripturl, scrollBy, scrollTo, scrollbar, search, seal,\n
 send, serialize, sessionStorage, setInterval, setTimeout, setter, setterToken, shift, slice,\n
 smarttabs, sort, spawn, split, stack, status, start, strict, sub, substr, supernew, shadow,\n
 supplant, sum, sync, test, toLowerCase, toString, toUpperCase, toint32, token, top, trailing,\n
 type, typeOf, Uint16Array, Uint32Array, Uint8Array, undef, undefs, unused, urls, validthis,\n
 value, valueOf, var, vars, version, WebSocket, withstmt, white, window, windows, Worker, wsh*/\n
\n
/*global exports: false */\n
\n
// We build the application inside a function so that we produce only a single\n
// global variable. That function will be invoked immediately, and its return\n
// value is the JSHINT function itself.\n
\n
var JSHINT = (function () {\n
    "use strict";\n
\n
    var anonname,       // The guessed name for anonymous functions.\n
\n
// These are operators that should not be used with the ! operator.\n
\n
        bang = {\n
            \'<\'  : true,\n
            \'<=\' : true,\n
            \'==\' : true,\n
            \'===\': true,\n
            \'!==\': true,\n
            \'!=\' : true,\n
            \'>\'  : true,\n
            \'>=\' : true,\n
            \'+\'  : true,\n
            \'-\'  : true,\n
            \'*\'  : true,\n
            \'/\'  : true,\n
            \'%\'  : true\n
        },\n
\n
        // These are the JSHint boolean options.\n
        boolOptions = {\n
            asi         : true, // if automatic semicolon insertion should be tolerated\n
            bitwise     : true, // if bitwise operators should not be allowed\n
            boss        : true, // if advanced usage of assignments should be allowed\n
            browser     : true, // if the standard browser globals should be predefined\n
            couch       : true, // if CouchDB globals should be predefined\n
            curly       : true, // if curly braces around all blocks should be required\n
            debug       : true, // if debugger statements should be allowed\n
            devel       : true, // if logging globals should be predefined (console,\n
                                // alert, etc.)\n
            dojo        : true, // if Dojo Toolkit globals should be predefined\n
            eqeqeq      : true, // if === should be required\n
            eqnull      : true, // if == null comparisons should be tolerated\n
            es5         : true, // if ES5 syntax should be allowed\n
            esnext      : true, // if es.next specific syntax should be allowed\n
            evil        : true, // if eval should be allowed\n
            expr        : true, // if ExpressionStatement should be allowed as Programs\n
            forin       : true, // if for in statements must filter\n
            funcscope   : true, // if only function scope should be used for scope tests\n
            globalstrict: true, // if global "use strict"; should be allowed (also\n
                                // enables \'strict\')\n
            immed       : true, // if immediate invocations must be wrapped in parens\n
            iterator    : true, // if the `__iterator__` property should be allowed\n
            jquery      : true, // if jQuery globals should be predefined\n
            lastsemic   : true, // if semicolons may be ommitted for the trailing\n
                                // statements inside of a one-line blocks.\n
            latedef     : true, // if the use before definition should not be tolerated\n
            laxbreak    : true, // if line breaks should not be checked\n
            laxcomma    : true, // if line breaks should not be checked around commas\n
            loopfunc    : true, // if functions should be allowed to be defined within\n
                                // loops\n
            mootools    : true, // if MooTools globals should be predefined\n
            multistr    : true, // allow multiline strings\n
            newcap      : true, // if constructor names must be capitalized\n
            noarg       : true, // if arguments.caller and arguments.callee should be\n
                                // disallowed\n
            node        : true, // if the Node.js environment globals should be\n
                                // predefined\n
            noempty     : true, // if empty blocks should be disallowed\n
            nonew       : true, // if using `new` for side-effects should be disallowed\n
            nonstandard : true, // if non-standard (but widely adopted) globals should\n
                                // be predefined\n
            nomen       : true, // if names should be checked\n
            onevar      : true, // if only one var statement per function should be\n
                                // allowed\n
            onecase     : true, // if one case switch statements should be allowed\n
            passfail    : true, // if the scan should stop on first error\n
            plusplus    : true, // if increment/decrement should not be allowed\n
            proto       : true, // if the `__proto__` property should be allowed\n
            prototypejs : true, // if Prototype and Scriptaculous globals should be\n
                                // predefined\n
            regexdash   : true, // if unescaped first/last dash (-) inside brackets\n
                                // should be tolerated\n
            regexp      : true, // if the . should not be allowed in regexp literals\n
            rhino       : true, // if the Rhino environment globals should be predefined\n
            undef       : true, // if variables should be declared before used\n
            scripturl   : true, // if script-targeted URLs should be tolerated\n
            shadow      : true, // if variable shadowing should be tolerated\n
            smarttabs   : true, // if smarttabs should be tolerated\n
                                // (http://www.emacswiki.org/emacs/SmartTabs)\n
            strict      : true, // require the "use strict"; pragma\n
            sub         : true, // if all forms of subscript notation are tolerated\n
            supernew    : true, // if `new function () { ... };` and `new Object;`\n
                                // should be tolerated\n
            trailing    : true, // if trailing whitespace rules apply\n
            validthis   : true, // if \'this\' inside a non-constructor function is valid.\n
                                // This is a function scoped option only.\n
            withstmt    : true, // if with statements should be allowed\n
            white       : true, // if strict whitespace rules apply\n
            wsh         : true  // if the Windows Scripting Host environment globals\n
                                // should be predefined\n
        },\n
\n
        // These are the JSHint options that can take any value\n
        // (we use this object to detect invalid options)\n
        valOptions = {\n
            maxlen: false,\n
            indent: false,\n
            maxerr: false,\n
            predef: false\n
        },\n
\n
        // These are JSHint boolean options which are shared with JSLint\n
        // where the definition in JSHint is opposite JSLint\n
        invertedOptions = {\n
            bitwise     : true,\n
            forin       : true,\n
            newcap      : true,\n
            nomen       : true,\n
            plusplus    : true,\n
            regexp      : true,\n
            undef       : true,\n
            white       : true,\n
\n
            // Inverted and renamed, use JSHint name here\n
            eqeqeq      : true,\n
            onevar      : true\n
        },\n
\n
        // These are JSHint boolean options which are shared with JSLint\n
        // where the name has been changed but the effect is unchanged\n
        renamedOptions = {\n
            eqeq        : "eqeqeq",\n
            vars        : "onevar",\n
            windows     : "wsh"\n
        },\n
\n
\n
        // browser contains a set of global names which are commonly provided by a\n
        // web browser environment.\n
        browser = {\n
            ArrayBuffer              :  false,\n
            ArrayBufferView          :  false,\n
            Audio                    :  false,\n
            addEventListener         :  false,\n
            applicationCache         :  false,\n
            atob                     :  false,\n
            blur                     :  false,\n
            btoa                     :  false,\n
            clearInterval            :  false,\n
            clearTimeout             :  false,\n
            close                    :  false,\n
            closed                   :  false,\n
            DataView                 :  false,\n
            DOMParser                :  false,\n
            defaultStatus            :  false,\n
            document                 :  false,\n
            event                    :  false,\n
            FileReader               :  false,\n
            Float32Array             :  false,\n
            Float64Array             :  false,\n
            FormData                 :  false,\n
            focus                    :  false,\n
            frames                   :  false,\n
            getComputedStyle         :  false,\n
            HTMLElement              :  false,\n
            HTMLAnchorElement        :  false,\n
            HTMLBaseElement          :  false,\n
            HTMLBlockquoteElement    :  false,\n
            HTMLBodyElement          :  false,\n
            HTMLBRElement            :  false,\n
            HTMLButtonElement        :  false,\n
            HTMLCanvasElement        :  false,\n
            HTMLDirectoryElement     :  false,\n
            HTMLDivElement           :  false,\n
            HTMLDListElement         :  false,\n
            HTMLFieldSetElement      :  false,\n
            HTMLFontElement          :  false,\n
            HTMLFormElement          :  false,\n
            HTMLFrameElement         :  false,\n
            HTMLFrameSetElement      :  false,\n
            HTMLHeadElement          :  false,\n
            HTMLHeadingElement       :  false,\n
            HTMLHRElement            :  false,\n
            HTMLHtmlElement          :  false,\n
            HTMLIFrameElement        :  false,\n
            HTMLImageElement         :  false,\n
            HTMLInputElement         :  false,\n
            HTMLIsIndexElement       :  false,\n
            HTMLLabelElement         :  false,\n
            HTMLLayerElement         :  false,\n
            HTMLLegendElement        :  false,\n
            HTMLLIElement            :  false,\n
            HTMLLinkElement          :  false,\n
            HTMLMapElement           :  false,\n
            HTMLMenuElement          :  false,\n
            HTMLMetaElement          :  false,\n
            HTMLModElement           :  false,\n
            HTMLObjectElement        :  false,\n
            HTMLOListElement         :  false,\n
            HTMLOptGroupElement      :  false,\n
            HTMLOptionElement        :  false,\n
            HTMLParagraphElement     :  false,\n
            HTMLParamElement         :  false,\n
            HTMLPreElement           :  false,\n
            HTMLQuoteElement         :  false,\n
            HTMLScriptElement        :  false,\n
            HTMLSelectElement        :  false,\n
            HTMLStyleElement         :  false,\n
            HTMLTableCaptionElement  :  false,\n
            HTMLTableCellElement     :  false,\n
            HTMLTableColElement      :  false,\n
            HTMLTableElement         :  false,\n
            HTMLTableRowElement      :  false,\n
            HTMLTableSectionElement  :  false,\n
            HTMLTextAreaElement      :  false,\n
            HTMLTitleElement         :  false,\n
            HTMLUListElement         :  false,\n
            HTMLVideoElement         :  false,\n
            history                  :  false,\n
            Int16Array               :  false,\n
            Int32Array               :  false,\n
            Int8Array                :  false,\n
            Image                    :  false,\n
            length                   :  false,\n
            localStorage             :  false,\n
            location                 :  false,\n
            MessageChannel           :  false,\n
            MessageEvent             :  false,\n
            MessagePort              :  false,\n
            moveBy                   :  false,\n
            moveTo                   :  false,\n
            name                     :  false,\n
            navigator                :  false,\n
            onbeforeunload           :  true,\n
            onblur                   :  true,\n
            onerror                  :  true,\n
            onfocus                  :  true,\n
            onload                   :  true,\n
            onresize                 :  true,\n
            onunload                 :  true,\n
            open                     :  false,\n
            openDatabase             :  false,\n
            opener                   :  false,\n
            Option                   :  false,\n
            parent                   :  false,\n
            print                    :  false,\n
            removeEventListener      :  false,\n
            resizeBy                 :  false,\n
            resizeTo                 :  false,\n
            screen                   :  false,\n
            scroll                   :  false,\n
            scrollBy                 :  false,\n
            scrollTo                 :  false,\n
            sessionStorage           :  false,\n
            setInterval              :  false,\n
            setTimeout               :  false,\n
            SharedWorker             :  false,\n
            status                   :  false,\n
            top                      :  false,\n
            Uint16Array              :  false,\n
            Uint32Array              :  false,\n
            Uint8Array               :  false,\n
            WebSocket                :  false,\n
            window                   :  false,\n
            Worker                   :  false,\n
            XMLHttpRequest           :  false,\n
            XMLSerializer            :  false,\n
            XPathEvaluator           :  false,\n
            XPathException           :  false,\n
            XPathExpression          :  false,\n
            XPathNamespace           :  false,\n
            XPathNSResolver          :  false,\n
            XPathResult              :  false\n
        },\n
\n
        couch = {\n
            "require" : false,\n
            respond   : false,\n
            getRow    : false,\n
            emit      : false,\n
            send      : false,\n
            start     : false,\n
            sum       : false,\n
            log       : false,\n
            exports   : false,\n
            module    : false,\n
            provides  : false\n
        },\n
\n
        devel = {\n
            alert   : false,\n
            confirm : false,\n
            console : false,\n
            Debug   : false,\n
            opera   : false,\n
            prompt  : false\n
        },\n
\n
        dojo = {\n
            dojo      : false,\n
            dijit     : false,\n
            dojox     : false,\n
            define    : false,\n
            "require" : false\n
        },\n
\n
        escapes = {\n
            \'\\b\': \'\\\\b\',\n
            \'\\t\': \'\\\\t\',\n
            \'\\n\': \'\\\\n\',\n
            \'\\f\': \'\\\\f\',\n
            \'\\r\': \'\\\\r\',\n
            \'"\' : \'\\\\"\',\n
            \'/\' : \'\\\\/\',\n
            \'\\\\\': \'\\\\\\\\\'\n
        },\n
\n
        funct,          // The current function\n
\n
        functionicity = [\n
            \'closure\', \'exception\', \'global\', \'label\',\n
            \'outer\', \'unused\', \'var\'\n
        ],\n
\n
        functions,      // All of the functions\n
\n
        global,         // The global scope\n
        implied,        // Implied globals\n
        inblock,\n
        indent,\n
        jsonmode,\n
\n
        jquery = {\n
            \'$\'    : false,\n
            jQuery : false\n
        },\n
\n
        lines,\n
        lookahead,\n
        member,\n
        membersOnly,\n
\n
        mootools = {\n
            \'$\'             : false,\n
            \'$$\'            : false,\n
            Assets          : false,\n
            Browser         : false,\n
            Chain           : false,\n
            Class           : false,\n
            Color           : false,\n
            Cookie          : false,\n
            Core            : false,\n
            Document        : false,\n
            DomReady        : false,\n
            DOMReady        : false,\n
            Drag            : false,\n
            Element         : false,\n
            Elements        : false,\n
            Event           : false,\n
            Events          : false,\n
            Fx              : false,\n
            Group           : false,\n
            Hash            : false,\n
            HtmlTable       : false,\n
            Iframe          : false,\n
            IframeShim      : false,\n
            InputValidator  : false,\n
            instanceOf      : false,\n
            Keyboard        : false,\n
            Locale          : false,\n
            Mask            : false,\n
            MooTools        : false,\n
            Native          : false,\n
            Options         : false,\n
            OverText        : false,\n
            Request         : false,\n
            Scroller        : false,\n
            Slick           : false,\n
            Slider          : false,\n
            Sortables       : false,\n
            Spinner         : false,\n
            Swiff           : false,\n
            Tips            : false,\n
            Type            : false,\n
            typeOf          : false,\n
            URI             : false,\n
            Window          : false\n
        },\n
\n
        nexttoken,\n
\n
        node = {\n
            __filename    : false,\n
            __dirname     : false,\n
            Buffer        : false,\n
            console       : false,\n
            exports       : false,\n
            GLOBAL        : false,\n
            global        : false,\n
            module        : false,\n
            process       : false,\n
            require       : false,\n
            setTimeout    : false,\n
            clearTimeout  : false,\n
            setInterval   : false,\n
            clearInterval : false\n
        },\n
\n
        noreach,\n
        option,\n
        predefined,     // Global variables defined by option\n
        prereg,\n
        prevtoken,\n
\n
        prototypejs = {\n
            \'$\'               : false,\n
            \'$$\'              : false,\n
            \'$A\'              : false,\n
            \'$F\'              : false,\n
            \'$H\'              : false,\n
            \'$R\'              : false,\n
            \'$break\'          : false,\n
            \'$continue\'       : false,\n
            \'$w\'              : false,\n
            Abstract          : false,\n
            Ajax              : false,\n
            Class             : false,\n
            Enumerable        : false,\n
            Element           : false,\n
            Event             : false,\n
            Field             : false,\n
            Form              : false,\n
            Hash              : false,\n
            Insertion         : false,\n
            ObjectRange       : false,\n
            PeriodicalExecuter: false,\n
            Position          : false,\n
            Prototype         : false,\n
            Selector          : false,\n
            Template          : false,\n
            Toggle            : false,\n
            Try               : false,\n
            Autocompleter     : false,\n
            Builder           : false,\n
            Control           : false,\n
            Draggable         : false,\n
            Draggables        : false,\n
            Droppables        : false,\n
            Effect            : false,\n
            Sortable          : false,\n
            SortableObserver  : false,\n
            Sound             : false,\n
            Scriptaculous     : false\n
        },\n
\n
        rhino = {\n
            defineClass  : false,\n
            deserialize  : false,\n
            gc           : false,\n
            help         : false,\n
            importPackage: false,\n
            "java"       : false,\n
            load         : false,\n
            loadClass    : false,\n
            print        : false,\n
            quit         : false,\n
            readFile     : false,\n
            readUrl      : false,\n
            runCommand   : false,\n
            seal         : false,\n
            serialize    : false,\n
            spawn        : false,\n
            sync         : false,\n
            toint32      : false,\n
            version      : false\n
        },\n
\n
        scope,      // The current scope\n
        stack,\n
\n
        // standard contains the global names that are provided by the\n
        // ECMAScript standard.\n
        standard = {\n
            Array               : false,\n
            Boolean             : false,\n
            Date                : false,\n
            decodeURI           : false,\n
            decodeURIComponent  : false,\n
            encodeURI           : false,\n
            encodeURIComponent  : false,\n
            Error               : false,\n
            \'eval\'              : false,\n
            EvalError           : false,\n
            Function            : false,\n
            hasOwnProperty      : false,\n
            isFinite            : false,\n
            isNaN               : false,\n
            JSON                : false,\n
            Math                : false,\n
            Number              : false,\n
            Object              : false,\n
            parseInt            : false,\n
            parseFloat          : false,\n
            RangeError          : false,\n
            ReferenceError      : false,\n
            RegExp              : false,\n
            String              : false,\n
            SyntaxError         : false,\n
            TypeError           : false,\n
            URIError            : false\n
        },\n
\n
        // widely adopted global names that are not part of ECMAScript standard\n
        nonstandard = {\n
            escape              : false,\n
            unescape            : false\n
        },\n
\n
        standard_member = {\n
            E                   : true,\n
            LN2                 : true,\n
            LN10                : true,\n
            LOG2E               : true,\n
            LOG10E              : true,\n
            MAX_VALUE           : true,\n
            MIN_VALUE           : true,\n
            NEGATIVE_INFINITY   : true,\n
            PI                  : true,\n
            POSITIVE_INFINITY   : true,\n
            SQRT1_2             : true,\n
            SQRT2               : true\n
        },\n
\n
        directive,\n
        syntax = {},\n
        tab,\n
        token,\n
        urls,\n
        useESNextSyntax,\n
        warnings,\n
\n
        wsh = {\n
            ActiveXObject             : true,\n
            Enumerator                : true,\n
            GetObject                 : true,\n
            ScriptEngine              : true,\n
            ScriptEngineBuildVersion  : true,\n
            ScriptEngineMajorVersion  : true,\n
            ScriptEngineMinorVersion  : true,\n
            VBArray                   : true,\n
            WSH                       : true,\n
            WScript                   : true,\n
            XDomainRequest            : true\n
        };\n
\n
    // Regular expressions. Some of these are stupidly long.\n
    var ax, cx, tx, nx, nxg, lx, ix, jx, ft;\n
    (function () {\n
        /*jshint maxlen:300 */\n
\n
        // unsafe comment or string\n
        ax = /@cc|<\\/?|script|\\]\\s*\\]|<\\s*!|&lt/i;\n
\n
        // unsafe characters that are silently deleted by one or more browsers\n
        cx = /[\\u0000-\\u001f\\u007f-\\u009f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/;\n
\n
        // token\n
        tx = /^\\s*([(){}\\[.,:;\'"~\\?\\]#@]|==?=?|\\/(\\*(jshint|jslint|members?|global)?|=|\\/)?|\\*[\\/=]?|\\+(?:=|\\++)?|-(?:=|-+)?|%=?|&[&=]?|\\|[|=]?|>>?>?=?|<([\\/=!]|\\!(\\[|--)?|<=?)?|\\^=?|\\!=?=?|[a-zA-Z_$][a-zA-Z0-9_$]*|[0-9]+([xX][0-9a-fA-F]+|\\.[0-9]*)?([eE][+\\-]?[0-9]+)?)/;\n
\n
        // characters in strings that need escapement\n
        nx = /[\\u0000-\\u001f&<"\\/\\\\\\u007f-\\u009f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/;\n
        nxg = /[\\u0000-\\u001f&<"\\/\\\\\\u007f-\\u009f\\u00ad\\u0600-\\u0604\\u070f\\u17b4\\u17b5\\u200c-\\u200f\\u2028-\\u202f\\u2060-\\u206f\\ufeff\\ufff0-\\uffff]/g;\n
\n
        // star slash\n
        lx = /\\*\\/|\\/\\*/;\n
\n
        // identifier\n
        ix = /^([a-zA-Z_$][a-zA-Z0-9_$]*)$/;\n
\n
        // javascript url\n
        jx = /^(?:javascript|jscript|ecmascript|vbscript|mocha|livescript)\\s*:/i;\n
\n
        // catches /* falls through */ comments\n
        ft = /^\\s*\\/\\*\\s*falls\\sthrough\\s*\\*\\/\\s*$/;\n
    }());\n
\n
    function F() {}     // Used by Object.create\n
\n
    function is_own(object, name) {\n
\n
// The object.hasOwnProperty method fails when the property under consideration\n
// is named \'hasOwnProperty\'. So we have to use this more convoluted form.\n
\n
        return Object.prototype.hasOwnProperty.call(object, name);\n
    }\n
\n
    function checkOption(name, t) {\n
        if (valOptions[name] === undefined && boolOptions[name] === undefined) {\n
            warning("Bad option: \'" + name + "\'.", t);\n
        }\n
    }\n
\n
// Provide critical ES5 functions to ES3.\n
\n
    if (typeof Array.isArray !== \'function\') {\n
        Array.isArray = function (o) {\n
            return Object.prototype.toString.apply(o) === \'[object Array]\';\n
        };\n
    }\n
\n
    if (typeof Object.create !== \'function\') {\n
        Object.create = function (o) {\n
            F.prototype = o;\n
            return new F();\n
        };\n
    }\n
\n
    if (typeof Object.keys !== \'function\') {\n
        Object.keys = function (o) {\n
            var a = [], k;\n
            for (k in o) {\n
                if (is_own(o, k)) {\n
                    a.push(k);\n
                }\n
            }\n
            return a;\n
        };\n
    }\n
\n
// Non standard methods\n
\n
    if (typeof String.prototype.entityify !== \'function\') {\n
        String.prototype.entityify = function () {\n
            return this\n
                .replace(/&/g, \'&amp;\')\n
                .replace(/</g, \'&lt;\')\n
                .replace(/>/g, \'&gt;\');\n
        };\n
    }\n
\n
    if (typeof String.prototype.isAlpha !== \'function\') {\n
        String.prototype.isAlpha = function () {\n
            return (this >= \'a\' && this <= \'z\\uffff\') ||\n
                (this >= \'A\' && this <= \'Z\\uffff\');\n
        };\n
    }\n
\n
    if (typeof String.prototype.isDigit !== \'function\') {\n
        String.prototype.isDigit = function () {\n
            return (this >= \'0\' && this <= \'9\');\n
        };\n
    }\n
\n
    if (typeof String.prototype.supplant !== \'function\') {\n
        String.prototype.supplant = function (o) {\n
            return this.replace(/\\{([^{}]*)\\}/g, function (a, b) {\n
                var r = o[b];\n
                return typeof r === \'string\' || typeof r === \'number\' ? r : a;\n
            });\n
        };\n
    }\n
\n
    if (typeof String.prototype.name !== \'function\') {\n
        String.prototype.name = function () {\n
\n
// If the string looks like an identifier, then we can return it as is.\n
// If the string contains no control characters, no quote characters, and no\n
// backslash characters, then we can simply slap some quotes around it.\n
// Otherwise we must also replace the offending characters with safe\n
// sequences.\n
\n
            if (ix.test(this)) {\n
                return this;\n
            }\n
            if (nx.test(this)) {\n
                return \'"\' + this.replace(nxg, function (a) {\n
                    var c = escapes[a];\n
                    if (c) {\n
                        return c;\n
                    }\n
                    return \'\\\\u\' + (\'0000\' + a.charCodeAt().toString(16)).slice(-4);\n
                }) + \'"\';\n
            }\n
            return \'"\' + this + \'"\';\n
        };\n
    }\n
\n
\n
    function combine(t, o) {\n
        var n;\n
        for (n in o) {\n
            if (is_own(o, n)) {\n
                t[n] = o[n];\n
            }\n
        }\n
    }\n
\n
    function assume() {\n
        if (option.couch) {\n
            combine(predefined, couch);\n
        }\n
\n
        if (option.rhino) {\n
            combine(predefined, rhino);\n
        }\n
\n
        if (option.prototypejs) {\n
            combine(predefined, prototypejs);\n
        }\n
\n
        if (option.node) {\n
            combine(predefined, node);\n
            option.globalstrict = true;\n
        }\n
\n
        if (option.devel) {\n
            combine(predefined, devel);\n
        }\n
\n
        if (option.dojo) {\n
            combine(predefined, dojo);\n
        }\n
\n
        if (option.browser) {\n
            combine(predefined, browser);\n
        }\n
\n
        if (option.nonstandard) {\n
            combine(predefined, nonstandard);\n
        }\n
\n
        if (option.jquery) {\n
            combine(predefined, jquery);\n
        }\n
\n
        if (option.mootools) {\n
            combine(predefined, mootools);\n
        }\n
\n
        if (option.wsh) {\n
            combine(predefined, wsh);\n
        }\n
\n
        if (option.esnext) {\n
            useESNextSyntax();\n
        }\n
\n
        if (option.globalstrict && option.strict !== false) {\n
            option.strict = true;\n
        }\n
    }\n
\n
\n
    // Produce an error warning.\n
    function quit(message, line, chr) {\n
        var percentage = Math.floor((line / lines.length) * 100);\n
\n
        throw {\n
            name: \'JSHintError\',\n
            line: line,\n
            character: chr,\n
            message: message + " (" + percentage + "% scanned).",\n
            raw: message\n
        };\n
    }\n
\n
    function isundef(scope, m, t, a) {\n
        return JSHINT.undefs.push([scope, m, t, a]);\n
    }\n
\n
    function warning(m, t, a, b, c, d) {\n
        var ch, l, w;\n
        t = t || nexttoken;\n
        if (t.id === \'(end)\') {  // `~\n
            t = token;\n
        }\n
        l = t.line || 0;\n
        ch = t.from || 0;\n
        w = {\n
            id: \'(error)\',\n
            raw: m,\n
            evidence: lines[l - 1] || \'\',\n
            line: l,\n
            character: ch,\n
            a: a,\n
            b: b,\n
            c: c,\n
            d: d\n
        };\n
        w.reason = m.supplant(w);\n
        JSHINT.errors.push(w);\n
        if (option.passfail) {\n
            quit(\'Stopping. \', l, ch);\n
        }\n
        warnings += 1;\n
        if (warnings >= option.maxerr) {\n
            quit("Too many errors.", l, ch);\n
        }\n
        return w;\n
    }\n
\n
    function warningAt(m, l, ch, a, b, c, d) {\n
        return warning(m, {\n
            line: l,\n
            from: ch\n
        }, a, b, c, d);\n
    }\n
\n
    function error(m, t, a, b, c, d) {\n
        var w = warning(m, t, a, b, c, d);\n
    }\n
\n
    function errorAt(m, l, ch, a, b, c, d) {\n
        return error(m, {\n
            line: l,\n
            from: ch\n
        }, a, b, c, d);\n
    }\n
\n
\n
\n
// lexical analysis and token construction\n
\n
    var lex = (function lex() {\n
        var character, from, line, s;\n
\n
// Private lex methods\n
\n
        function nextLine() {\n
            var at,\n
                tw; // trailing whitespace check\n
\n
            if (line >= lines.length)\n
                return false;\n
\n
            character = 1;\n
            s = lines[line];\n
            line += 1;\n
\n
            // If smarttabs option is used check for spaces followed by tabs only.\n
            // Otherwise check for any occurence of mixed tabs and spaces.\n
            if (option.smarttabs)\n
                at = s.search(/ \\t/);\n
            else\n
                at = s.search(/ \\t|\\t /);\n
\n
            if (at >= 0)\n
                warningAt("Mixed spaces and tabs.", line, at + 1);\n
\n
            s = s.replace(/\\t/g, tab);\n
            at = s.search(cx);\n
\n
            if (at >= 0)\n
                warningAt("Unsafe character.", line, at);\n
\n
            if (option.maxlen && option.maxlen < s.length)\n
                warningAt("Line too long.", line, s.length);\n
\n
            // Check for trailing whitespaces\n
            tw = option.trailing && s.match(/^(.*?)\\s+$/);\n
            if (tw && !/^\\s+$/.test(s)) {\n
                warningAt("Trailing whitespace.", line, tw[1].length + 1);\n
            }\n
            return true;\n
        }\n
\n
// Produce a token object.  The token inherits from a syntax symbol.\n
\n
        function it(type, value) {\n
            var i, t;\n
            if (type === \'(color)\' || type === \'(range)\') {\n
                t = {type: type};\n
            } else if (type === \'(punctuator)\' ||\n
                    (type === \'(identifier)\' && is_own(syntax, value))) {\n
                t = syntax[value] || syntax[\'(error)\'];\n
            } else {\n
                t = syntax[type];\n
            }\n
            t = Object.create(t);\n
            if (type === \'(string)\' || type === \'(range)\') {\n
                if (!option.scripturl && jx.test(value)) {\n
                    warningAt("Script URL.", line, from);\n
                }\n
            }\n
            if (type === \'(identifier)\') {\n
                t.identifier = true;\n
                if (value === \'__proto__\' && !option.proto) {\n
                    warningAt("The \'{a}\' property is deprecated.",\n
                        line, from, value);\n
                } else if (value === \'__iterator__\' && !option.iterator) {\n
                    warningAt("\'{a}\' is only available in JavaScript 1.7.",\n
                        line, from, value);\n
                } else if (option.nomen && (value.charAt(0) === \'_\' ||\n
                         value.charAt(value.length - 1) === \'_\')) {\n
                    if (!option.node || token.id === \'.\' ||\n
                            (value !== \'__dirname\' && value !== \'__filename\')) {\n
                        warningAt("Unexpected {a} in \'{b}\'.", line, from, "dangling \'_\'", value);\n
                    }\n
                }\n
            }\n
            t.value = value;\n
            t.line = line;\n
            t.character = character;\n
            t.from = from;\n
            i = t.id;\n
            if (i !== \'(endline)\') {\n
                prereg = i &&\n
                    ((\'(,=:[!&|?{};\'.indexOf(i.charAt(i.length - 1)) >= 0) ||\n
                    i === \'return\' ||\n
                    i === \'case\');\n
            }\n
            return t;\n
        }\n
\n
        // Public lex methods\n
        return {\n
            init: function (source) {\n
                if (typeof source === \'string\') {\n
                    lines = source\n
                        .replace(/\\r\\n/g, \'\\n\')\n
                        .replace(/\\r/g, \'\\n\')\n
                        .split(\'\\n\');\n
                } else {\n
                    lines = source;\n
                }\n
\n
                // If the first line is a shebang (#!), make it a blank and move on.\n
                // Shebangs are used by Node scripts.\n
                if (lines[0] && lines[0].substr(0, 2) === \'#!\')\n
                    lines[0] = \'\';\n
\n
                line = 0;\n
                nextLine();\n
                from = 1;\n
            },\n
\n
            range: function (begin, end) {\n
                var c, value = \'\';\n
                from = character;\n
                if (s.charAt(0) !== begin) {\n
                    errorAt("Expected \'{a}\' and instead saw \'{b}\'.",\n
                            line, character, begin, s.charAt(0));\n
                }\n
                for (;;) {\n
                    s = s.slice(1);\n
                    character += 1;\n
                    c = s.charAt(0);\n
                    switch (c) {\n
                    case \'\':\n
                        errorAt("Missing \'{a}\'.", line, character, c);\n
                        break;\n
                    case end:\n
                        s = s.slice(1);\n
                        character += 1;\n
                        return it(\'(range)\', value);\n
                    case \'\\\\\':\n
                        warningAt("Unexpected \'{a}\'.", line, character, c);\n
                    }\n
                    value += c;\n
                }\n
\n
            },\n
\n
\n
            // token -- this is called by advance to get the next token\n
            token: function () {\n
                var b, c, captures, d, depth, high, i, l, low, q, t, isLiteral, isInRange, n;\n
\n
                function match(x) {\n
                    var r = x.exec(s), r1;\n
                    if (r) {\n
                        l = r[0].length;\n
                        r1 = r[1];\n
                        c = r1.charAt(0);\n
                        s = s.substr(l);\n
                        from = character + l - r1.length;\n
                        character += l;\n
                        return r1;\n
                    }\n
                }\n
\n
                function string(x) {\n
                    var c, j, r = \'\', allowNewLine = false;\n
\n
                    if (jsonmode && x !== \'"\') {\n
                        warningAt("Strings must use doublequote.",\n
                                line, character);\n
                    }\n
\n
                    function esc(n) {\n
                        var i = parseInt(s.substr(j + 1, n), 16);\n
                        j += n;\n
                        if (i >= 32 && i <= 126 &&\n
                                i !== 34 && i !== 92 && i !== 39) {\n
                            warningAt("Unnecessary escapement.", line, character);\n
                        }\n
                        character += n;\n
                        c = String.fromCharCode(i);\n
                    }\n
                    j = 0;\n
unclosedString:     for (;;) {\n
                        while (j >= s.length) {\n
                            j = 0;\n
\n
                            var cl = line, cf = from;\n
                            if (!nextLine()) {\n
                                errorAt("Unclosed string.", cl, cf);\n
                                break unclosedString;\n
                            }\n
\n
                            if (allowNewLine) {\n
                                allowNewLine = false;\n
                            } else {\n
                                warningAt("Unclosed string.", cl, cf);\n
                            }\n
                        }\n
                        c = s.charAt(j);\n
                        if (c === x) {\n
                            character += 1;\n
                            s = s.substr(j + 1);\n
                            return it(\'(string)\', r, x);\n
                        }\n
                        if (c < \' \') {\n
                            if (c === \'\\n\' || c === \'\\r\') {\n
                                break;\n
                            }\n
                            warningAt("Control character in string: {a}.",\n
                                    line, character + j, s.slice(0, j));\n
                        } else if (c === \'\\\\\') {\n
                            j += 1;\n
                            character += 1;\n
                            c = s.charAt(j);\n
                            n = s.charAt(j + 1);\n
                            switch (c) {\n
                            case \'\\\\\':\n
                            case \'"\':\n
                            case \'/\':\n
                                break;\n
                            case \'\\\'\':\n
                                if (jsonmode) {\n
                                    warningAt("Avoid \\\\\'.", line, character);\n
                                }\n
                                break;\n
                            case \'b\':\n
                                c = \'\\b\';\n
                                break;\n
                            case \'f\':\n
                                c = \'\\f\';\n
                                break;\n
                            case \'n\':\n
                                c = \'\\n\';\n
                                break;\n
                            case \'r\':\n
                                c = \'\\r\';\n
                                break;\n
                            case \'t\':\n
                                c = \'\\t\';\n
                                break;\n
                            case \'0\':\n
                                c = \'\\0\';\n
                                // Octal literals fail in strict mode\n
                                // check if the number is between 00 and 07\n
                                // where \'n\' is the token next to \'c\'\n
                                if (n >= 0 && n <= 7 && directive["use strict"]) {\n
                                    warningAt(\n
                                    "Octal literals are not allowed in strict mode.",\n
                                    line, character);\n
                                }\n
                                break;\n
                            case \'u\':\n
                                esc(4);\n
                                break;\n
                            case \'v\':\n
                                if (jsonmode) {\n
                                    warningAt("Avoid \\\\v.", line, character);\n
                                }\n
                                c = \'\\v\';\n
                                break;\n
                            case \'x\':\n
                                if (jsonmode) {\n
                                    warningAt("Avoid \\\\x-.", line, character);\n
                                }\n
                                esc(2);\n
                                break;\n
                            case \'\':\n
                                // last character is escape character\n
                                // always allow new line if escaped, but show\n
                                // warning if option is not set\n
                                allowNewLine = true;\n
                                if (option.multistr) {\n
                                    if (jsonmode) {\n
                                        warningAt("Avoid EOL escapement.", line, character);\n
                                    }\n
                                    c = \'\';\n
                                    character -= 1;\n
                                    break;\n
                                }\n
                                warningAt("Bad escapement of EOL. Use option multistr if needed.",\n
                                    line, character);\n
                                break;\n
                            default:\n
                                warningAt("Bad escapement.", line, character);\n
                            }\n
                        }\n
                        r += c;\n
                        character += 1;\n
                        j += 1;\n
                    }\n
                }\n
\n
                for (;;) {\n
                    if (!s) {\n
                        return it(nextLine() ? \'(endline)\' : \'(end)\', \'\');\n
                    }\n
                    t = match(tx);\n
                    if (!t) {\n
                        t = \'\';\n
                        c = \'\';\n
                        while (s && s < \'!\') {\n
                            s = s.substr(1);\n
                        }\n
                        if (s) {\n
                            errorAt("Unexpected \'{a}\'.", line, character, s.substr(0, 1));\n
                            s = \'\';\n
                        }\n
                    } else {\n
\n
    //      identifier\n
\n
                        if (c.isAlpha() || c === \'_\' || c === \'$\') {\n
                            return it(\'(identifier)\', t);\n
                        }\n
\n
    //      number\n
\n
                        if (c.isDigit()) {\n
                            if (!isFinite(Number(t))) {\n
                                warningAt("Bad number \'{a}\'.",\n
                                    line, character, t);\n
                            }\n
                            if (s.substr(0, 1).isAlpha()) {\n
                                warningAt("Missing space after \'{a}\'.",\n
                                        line, character, t);\n
                            }\n
                            if (c === \'0\') {\n
                                d = t.substr(1, 1);\n
                                if (d.isDigit()) {\n
                                    if (token.id !== \'.\') {\n
                                        warningAt("Don\'t use extra leading zeros \'{a}\'.",\n
                                            line, character, t);\n
                                    }\n
                                } else if (jsonmode && (d === \'x\' || d === \'X\')) {\n
                                    warningAt("Avoid 0x-. \'{a}\'.",\n
                                            line, character, t);\n
                                }\n
                            }\n
                            if (t.substr(t.length - 1) === \'.\') {\n
                                warningAt(\n
"A trailing decimal point can be confused with a dot \'{a}\'.", line, character, t);\n
                            }\n
                            return it(\'(number)\', t);\n
                        }\n
                        switch (t) {\n
\n
    //      string\n
\n
                        case \'"\':\n
                        case "\'":\n
                            return string(t);\n
\n
    //      // comment\n
\n
                        case \'//\':\n
                            s = \'\';\n
                            token.comment = true;\n
                            break;\n
\n
    //      /* comment\n
\n
                        case \'/*\':\n
                            for (;;) {\n
                                i = s.search(lx);\n
                                if (i >= 0) {\n
                                    break;\n
                                }\n
                                if (!nextLine()) {\n
                                    errorAt("Unclosed comment.", line, character);\n
                                }\n
                            }\n
                            character += i + 2;\n
                            if (s.substr(i, 1) === \'/\') {\n
                                errorAt("Nested comment.", line, character);\n
                            }\n
                            s = s.substr(i + 2);\n
                            token.comment = true;\n
                            break;\n
\n
    //      /*members /*jshint /*global\n
\n
                        case \'/*members\':\n
                        case \'/*member\':\n
                        case \'/*jshint\':\n
                        case \'/*jslint\':\n
                        case \'/*global\':\n
                        case \'*/\':\n
                            return {\n
                                value: t,\n
                                type: \'special\',\n
                                line: line,\n
                                character: character,\n
                                from: from\n
                            };\n
\n
                        case \'\':\n
                            break;\n
    //      /\n
                        case \'/\':\n
                            if (token.id === \'/=\') {\n
                                errorAt("A regular expression literal can be confused with \'/=\'.",\n
                                    line, from);\n
                            }\n
                            if (prereg) {\n
                                depth = 0;\n
                                captures = 0;\n
                                l = 0;\n
                                for (;;) {\n
                                    b = true;\n
                                    c = s.charAt(l);\n
                                    l += 1;\n
                                    switch (c) {\n
                                    case \'\':\n
                                        errorAt("Unclosed regular expression.", line, from);\n
                                        return quit(\'Stopping.\', line, from);\n
                                    case \'/\':\n
                                        if (depth > 0) {\n
                                            warningAt("{a} unterminated regular expression " +\n
                                                "group(s).", line, from + l, depth);\n
                                        }\n
                                        c = s.substr(0, l - 1);\n
                                        q = {\n
                                            g: true,\n
                                            i: true,\n
                                            m: true\n
                                        };\n
                                        while (q[s.charAt(l)] === true) {\n
                                            q[s.charAt(l)] = false;\n
                                            l += 1;\n
                                        }\n
                                        character += l;\n
                                        s = s.substr(l);\n
                                        q = s.charAt(0);\n
                                        if (q === \'/\' || q === \'*\') {\n
                                            errorAt("Confusing regular expression.",\n
                                                    line, from);\n
                                        }\n
                                        return it(\'(regexp)\', c);\n
                                    case \'\\\\\':\n
                                        c = s.charAt(l);\n
                                        if (c < \' \') {\n
                                            warningAt(\n
"Unexpected control character in regular expression.", line, from + l);\n
                                        } else if (c === \'<\') {\n
                                            warningAt(\n
"Unexpected escaped character \'{a}\' in regular expression.", line, from + l, c);\n
                                        }\n
                                        l += 1;\n
                                        break;\n
                                    case \'(\':\n
                                        depth += 1;\n
                                        b = false;\n
                                        if (s.charAt(l) === \'?\') {\n
                                            l += 1;\n
                                            switch (s.charAt(l)) {\n
                                            case \':\':\n
                                            case \'=\':\n
                                            case \'!\':\n
                                                l += 1;\n
                                                break;\n
                                            default:\n
                                                warningAt(\n
"Expected \'{a}\' and instead saw \'{b}\'.", line, from + l, \':\', s.charAt(l));\n
                                            }\n
                                        } else {\n
                                            captures += 1;\n
                                        }\n
                                        break;\n
                                    case \'|\':\n
                                        b = false;\n
                                        break;\n
                                    case \')\':\n
                                        if (depth === 0) {\n
                                            warningAt("Unescaped \'{a}\'.",\n
                                                    line, from + l, \')\');\n
                                        } else {\n
                                            depth -= 1;\n
                                        }\n
                                        break;\n
                                    case \' \':\n
                                        q = 1;\n
                                        while (s.charAt(l) === \' \') {\n
                                            l += 1;\n
                                            q += 1;\n
                                        }\n
                                        if (q > 1) {\n
                                            warningAt(\n
"Spaces are hard to count. Use {{a}}.", line, from + l, q);\n
                                        }\n
                                        break;\n
                                    case \'[\':\n
                                        c = s.charAt(l);\n
                                        if (c === \'^\') {\n
                                            l += 1;\n
                                            if (option.regexp) {\n
                                                warningAt("Insecure \'{a}\'.",\n
                                                        line, from + l, c);\n
                                            } else if (s.charAt(l) === \']\') {\n
                                                errorAt("Unescaped \'{a}\'.",\n
                                                    line, from + l, \'^\');\n
                                            }\n
                                        }\n
                                        if (c === \']\') {\n
                                            warningAt("Empty class.", line,\n
                                                    from + l - 1);\n
                                        }\n
                                        isLiteral = false;\n
                                        isInRange = false;\n
klass:                                  do {\n
                                            c = s.charAt(l);\n
                                            l += 1;\n
                                            switch (c) {\n
                                            case \'[\':\n
                                            case \'^\':\n
                                                warningAt("Unescaped \'{a}\'.",\n
                                                        line, from + l, c);\n
                                                if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else {\n
                                                    isLiteral = true;\n
                                                }\n
                                                break;\n
                                            case \'-\':\n
                                                if (isLiteral && !isInRange) {\n
                                                    isLiteral = false;\n
                                                    isInRange = true;\n
                                                } else if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else if (s.charAt(l) === \']\') {\n
                                                    isInRange = true;\n
                                                } else {\n
                                                    if (option.regexdash !== (l === 2 || (l === 3 &&\n
                                                        s.charAt(1) === \'^\'))) {\n
                                                        warningAt("Unescaped \'{a}\'.",\n
                                                            line, from + l - 1, \'-\');\n
                                                    }\n
                                                    isLiteral = true;\n
                                                }\n
                                                break;\n
                                            case \']\':\n
                                                if (isInRange && !option.regexdash) {\n
                                                    warningAt("Unescaped \'{a}\'.",\n
                                                            line, from + l - 1, \'-\');\n
                                                }\n
                                                break klass;\n
                                            case \'\\\\\':\n
                                                c = s.charAt(l);\n
                                                if (c < \' \') {\n
                                                    warningAt(\n
"Unexpected control character in regular expression.", line, from + l);\n
                                                } else if (c === \'<\') {\n
                                                    warningAt(\n
"Unexpected escaped character \'{a}\' in regular expression.", line, from + l, c);\n
                                                }\n
                                                l += 1;\n
\n
                                                // \\w, \\s and \\d are never part of a character range\n
                                                if (/[wsd]/i.test(c)) {\n
                                                    if (isInRange) {\n
                                                        warningAt("Unescaped \'{a}\'.",\n
                                                            line, from + l, \'-\');\n
                                                        isInRange = false;\n
                                                    }\n
                                                    isLiteral = false;\n
                                                } else if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else {\n
                                                    isLiteral = true;\n
                                                }\n
                                                break;\n
                                            case \'/\':\n
                                                warningAt("Unescaped \'{a}\'.",\n
                                                        line, from + l - 1, \'/\');\n
\n
                                                if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else {\n
                                                    isLiteral = true;\n
                                                }\n
                                                break;\n
                                            case \'<\':\n
                                                if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else {\n
                                                    isLiteral = true;\n
                                                }\n
                                                break;\n
                                            default:\n
                                                if (isInRange) {\n
                                                    isInRange = false;\n
                                                } else {\n
                                                    isLiteral = true;\n
                                                }\n
                                            }\n
                                        } while (c);\n
                                        break;\n
                                    case \'.\':\n
                                        if (option.regexp) {\n
                                            warningAt("Insecure \'{a}\'.", line,\n
                                                    from + l, c);\n
                                        }\n
                                        break;\n
                                    case \']\':\n
                                    case \'?\':\n
                                    case \'{\':\n
                                    case \'}\':\n
                                    case \'+\':\n
                                    case \'*\':\n
                                        warningAt("Unescaped \'{a}\'.", line,\n
                                                from + l, c);\n
                                    }\n
                                    if (b) {\n
                                        switch (s.charAt(l)) {\n
                                        case \'?\':\n
                                        case \'+\':\n
                                        case \'*\':\n
                                            l += 1;\n
                                            if (s.charAt(l) === \'?\') {\n
                                                l += 1;\n
                                            }\n
                                            break;\n
                                        case \'{\':\n
                                            l += 1;\n
                                            c = s.charAt(l);\n
                                            if (c < \'0\' || c > \'9\') {\n
                                                warningAt(\n
"Expected a number and instead saw \'{a}\'.", line, from + l, c);\n
                                            }\n
                                            l += 1;\n
                                            low = +c;\n
                                            for (;;) {\n
                                                c = s.charAt(l);\n
                                                if (c < \'0\' || c > \'9\') {\n
                                                    break;\n
                                                }\n
                                                l += 1;\n
                                                low = +c + (low * 10);\n
                                            }\n
                                            high = low;\n
                                            if (c === \',\') {\n
                                                l += 1;\n
                                                high = Infinity;\n
                                                c = s.charAt(l);\n
                                                if (c >= \'0\' && c <= \'9\') {\n
                                                    l += 1;\n
                                                    high = +c;\n
                                                    for (;;) {\n
                                                        c = s.charAt(l);\n
                                                        if (c < \'0\' || c > \'9\') {\n
                                                            break;\n
                                                        }\n
                                                        l += 1;\n
                                                        high = +c + (high * 10);\n
                                                    }\n
                                                }\n
                                            }\n
                                            if (s.charAt(l) !== \'}\') {\n
                                                warningAt(\n
"Expected \'{a}\' and instead saw \'{b}\'.", line, from + l, \'}\', c);\n
                                            } else {\n
                                                l += 1;\n
                                            }\n
                                            if (s.charAt(l) === \'?\') {\n
                                                l += 1;\n
                                            }\n
                                            if (low > high) {\n
                                                warningAt(\n
"\'{a}\' should not be greater than \'{b}\'.", line, from + l, low, high);\n
                                            }\n
                                        }\n
                                    }\n
                                }\n
                                c = s.substr(0, l - 1);\n
                                character += l;\n
                                s = s.substr(l);\n
                                return it(\'(regexp)\', c);\n
                            }\n
                            return it(\'(punctuator)\', t);\n
\n
    //      punctuator\n
\n
                        case \'#\':\n
                            return it(\'(punctuator)\', t);\n
                        default:\n
                            return it(\'(punctuator)\', t);\n
                        }\n
                    }\n
                }\n
            }\n
        };\n
    }());\n
\n
\n
    function addlabel(t, type) {\n
\n
        if (t === \'hasOwnProperty\') {\n
            warning("\'hasOwnProperty\' is a really bad name.");\n
        }\n
\n
// Define t in the current function in the current scope.\n
        if (is_own(funct, t) && !funct[\'(global)\']) {\n
            if (funct[t] === true) {\n
                if (option.latedef)\n
                    warning("\'{a}\' was used before it was defined.", nexttoken, t);\n
            } else {\n
                if (!option.shadow && type !== "exception")\n
                    warning("\'{a}\' is already defined.", nexttoken, t);\n
            }\n
        }\n
\n
        funct[t] = type;\n
        if (funct[\'(global)\']) {\n
            global[t] = funct;\n
            if (is_own(implied, t)) {\n
                if (option.latedef)\n
                    warning("\'{a}\' was used before it was defined.", nexttoken, t);\n
                delete implied[t];\n
            }\n
        } else {\n
            scope[t] = funct;\n
        }\n
    }\n
\n
\n
    function doOption() {\n
        var b, obj, filter, o = nexttoken.value, t, tn, v;\n
\n
        switch (o) {\n
        case \'*/\':\n
            error("Unbegun comment.");\n
            break;\n
        case \'/*members\':\n
        case \'/*member\':\n
            o = \'/*members\';\n
            if (!membersOnly) {\n
                membersOnly = {};\n
            }\n
            obj = membersOnly;\n
            break;\n
        case \'/*jshint\':\n
        case \'/*jslint\':\n
            obj = option;\n
            filter = boolOptions;\n
            break;\n
        case \'/*global\':\n
            obj = predefined;\n
            break;\n
        default:\n
            error("What?");\n
        }\n
\n
        t = lex.token();\n
loop:   for (;;) {\n
            for (;;) {\n
                if (t.type === \'special\' && t.value === \'*/\') {\n
                    break loop;\n
                }\n
                if (t.id !== \'(endline)\' && t.id !== \',\') {\n
                    break;\n
                }\n
                t = lex.token();\n
            }\n
            if (t.type !== \'(string)\' && t.type !== \'(identifier)\' &&\n
                    o !== \'/*members\') {\n
                error("Bad option.", t);\n
            }\n
\n
            v = lex.token();\n
            if (v.id === \':\') {\n
                v = lex.token();\n
\n
                if (obj === membersOnly) {\n
                    error("Expected \'{a}\' and instead saw \'{b}\'.",\n
                            t, \'*/\', \':\');\n
                }\n
\n
                if (o === \'/*jshint\') {\n
                    checkOption(t.value, t);\n
                }\n
\n
                if (t.value === \'indent\' && (o === \'/*jshint\' || o === \'/*jslint\')) {\n
                    b = +v.value;\n
                    if (typeof b !== \'number\' || !isFinite(b) || b <= 0 ||\n
                            Math.floor(b) !== b) {\n
                        error("Expected a small integer and instead saw \'{a}\'.",\n
                                v, v.value);\n
                    }\n
                    obj.white = true;\n
                    obj.indent = b;\n
                } else if (t.value === \'maxerr\' && (o === \'/*jshint\' || o === \'/*jslint\')) {\n
                    b = +v.value;\n
                    if (typeof b !== \'number\' || !isFinite(b) || b <= 0 ||\n
                            Math.floor(b) !== b) {\n
                        error("Expected a small integer and instead saw \'{a}\'.",\n
                                v, v.value);\n
                    }\n
                    obj.maxerr = b;\n
                } else if (t.value === \'maxlen\' && (o === \'/*jshint\' || o === \'/*jslint\')) {\n
                    b = +v.value;\n
                    if (typeof b !== \'number\' || !isFinite(b) || b <= 0 ||\n
                            Math.floor(b) !== b) {\n
                        error("Expected a small integer and instead saw \'{a}\'.",\n
                                v, v.value);\n
                    }\n
                    obj.maxlen = b;\n
                } else if (t.value === \'validthis\') {\n
                    if (funct[\'(global)\']) {\n
                        error("Option \'validthis\' can\'t be used in a global scope.");\n
                    } else {\n
                        if (v.value === \'true\' || v.value === \'false\')\n
                            obj[t.value] = v.value === \'true\';\n
                        else\n
                            error("Bad option value.", v);\n
                    }\n
                } else if (v.value === \'true\' || v.value === \'false\') {\n
                    if (o === \'/*jslint\') {\n
                        tn = renamedOptions[t.value] || t.value;\n
                        obj[tn] = v.value === \'true\';\n
                        if (invertedOptions[tn] !== undefined) {\n
                            obj[tn] = !obj[tn];\n
                        }\n
                    } else {\n
                        obj[t.value] = v.value === \'true\';\n
                    }\n
                } else {\n
                    error("Bad option value.", v);\n
                }\n
                t = lex.token();\n
            } else {\n
                if (o === \'/*jshint\' || o === \'/*jslint\') {\n
                    error("Missing option value.", t);\n
                }\n
                obj[t.value] = false;\n
                t = v;\n
            }\n
        }\n
        if (filter) {\n
            assume();\n
        }\n
    }\n
\n
\n
// We need a peek function. If it has an argument, it peeks that much farther\n
// ahead. It is used to distinguish\n
//     for ( var i in ...\n
// from\n
//     for ( var i = ...\n
\n
    function peek(p) {\n
        var i = p || 0, j = 0, t;\n
\n
        while (j <= i) {\n
            t = lookahead[j];\n
            if (!t) {\n
                t = lookahead[j] = lex.token();\n
            }\n
            j += 1;\n
        }\n
        return t;\n
    }\n
\n
\n
\n
// Produce the next token. It looks for programming errors.\n
\n
    function advance(id, t) {\n
        switch (token.id) {\n
        case \'(number)\':\n
            if (nexttoken.id === \'.\') {\n
                warning("A dot following a number can be confused with a decimal point.", token);\n
            }\n
            break;\n
        case \'-\':\n
            if (nexttoken.id === \'-\' || nexttoken.id === \'--\') {\n
                warning("Confusing minusses.");\n
            }\n
            break;\n
        case \'+\':\n
            if (nexttoken.id === \'+\' || nexttoken.id === \'++\') {\n
                warning("Confusing plusses.");\n
            }\n
            break;\n
        }\n
\n
        if (token.type === \'(string)\' || token.identifier) {\n
            anonname = token.value;\n
        }\n
\n
        if (id && nexttoken.id !== id) {\n
            if (t) {\n
                if (nexttoken.id === \'(end)\') {\n
                    warning("Unmatched \'{a}\'.", t, t.id);\n
                } else {\n
                    warning("Expected \'{a}\' to match \'{b}\' from line {c} and instead saw \'{d}\'.",\n
                            nexttoken, id, t.id, t.line, nexttoken.value);\n
                }\n
            } else if (nexttoken.type !== \'(identifier)\' ||\n
                            nexttoken.value !== id) {\n
                warning("Expected \'{a}\' and instead saw \'{b}\'.",\n
                        nexttoken, id, nexttoken.value);\n
            }\n
        }\n
\n
        prevtoken = token;\n
        token = nexttoken;\n
        for (;;) {\n
            nexttoken = lookahead.shift() || lex.token();\n
            if (nexttoken.id === \'(end)\' || nexttoken.id === \'(error)\') {\n
                return;\n
            }\n
            if (nexttoken.type === \'special\') {\n
                doOption();\n
            } else {\n
                if (nexttoken.id !== \'(endline)\') {\n
                    break;\n
                }\n
            }\n
        }\n
    }\n
\n
\n
// This is the heart of JSHINT, the Pratt parser. In addition to parsing, it\n
// is looking for ad hoc lint patterns. We add .fud to Pratt\'s model, which is\n
// like .nud except that it is only used on the first token of a statement.\n
// Having .fud makes it much easier to define statement-oriented languages like\n
// JavaScript. I retained Pratt\'s nomenclature.\n
\n
// .nud     Null denotation\n
// .fud     First null denotation\n
// .led     Left denotation\n
//  lbp     Left binding power\n
//  rbp     Right binding power\n
\n
// They are elements of the parsing method called Top Down Operator Precedence.\n
\n
    function expression(rbp, initial) {\n
        var left, isArray = false, isObject = false;\n
\n
        if (nexttoken.id === \'(end)\')\n
            error("Unexpected early end of program.", token);\n
\n
        advance();\n
        if (initial) {\n
            anonname = \'anonymous\';\n
            funct[\'(verb)\'] = token.value;\n
        }\n
        if (initial === true && token.fud) {\n
            left = token.fud();\n
        } else {\n
            if (token.nud) {\n
                left = token.nud();\n
            } else {\n
                if (nexttoken.type === \'(number)\' && token.id === \'.\') {\n
                    warning("A leading decimal point can be confused with a dot: \'.{a}\'.",\n
                            token, nexttoken.value);\n
                    advance();\n
                    return token;\n
                } else {\n
                    error("Expected an identifier and instead saw \'{a}\'.",\n
                            token, token.id);\n
                }\n
            }\n
            while (rbp < nexttoken.lbp) {\n
                isArray = token.value === \'Array\';\n
                isObject = token.value === \'Object\';\n
\n
                // #527, new Foo.Array(), Foo.Array(), new Foo.Object(), Foo.Object()\n
                // Line breaks in IfStatement heads exist to satisfy the checkJSHint\n
                // "Line too long." error.\n
                if (left && (left.value || (left.first && left.first.value))) {\n
                    // If the left.value is not "new", or the left.first.value is a "."\n
                    // then safely assume that this is not "new Array()" and possibly\n
                    // not "new Object()"...\n
                    if (left.value !== \'new\' ||\n
                      (left.first && left.first.value && left.first.value === \'.\')) {\n
                        isArray = false;\n
                        // ...In the case of Object, if the left.value and token.value\n
                        // are not equal, then safely assume that this not "new Object()"\n
                        if (left.value !== token.value) {\n
                            isObject = false;\n
                        }\n
                    }\n
                }\n
\n
                advance();\n
                if (isArray && token.id === \'(\' && nexttoken.id === \')\')\n
                    warning("Use the array literal notation [].", token);\n
                if (isObject && token.id === \'(\' && nexttoken.id === \')\')\n
                    warning("Use the object literal notation {}.", token);\n
                if (token.led) {\n
                    left = token.led(left);\n
                } else {\n
                    error("Expected an operator and instead saw \'{a}\'.",\n
                        token, token.id);\n
                }\n
            }\n
        }\n
        return left;\n
    }\n
\n
\n
// Functions for conformance of style.\n
\n
    function adjacent(left, right) {\n
        left = left || token;\n
        right = right || nexttoken;\n
        if (option.white) {\n
            if (left.character !== right.from && left.line === right.line) {\n
                left.from += (left.character - left.from);\n
                warning("Unexpected space after \'{a}\'.", left, left.value);\n
            }\n
        }\n
    }\n
\n
    function nobreak(left, right) {\n
        left = left || token;\n
        right = right || nexttoken;\n
        if (option.white && (left.character !== right.from || left.line !== right.line)) {\n
            warning("Unexpected space before \'{a}\'.", right, right.value);\n
        }\n
    }\n
\n
    function nospace(left, right) {\n
        left = left || token;\n
        right = right || nexttoken;\n
        if (option.white && !left.comment) {\n
            if (left.line === right.line) {\n
                adjacent(left, right);\n
            }\n
        }\n
    }\n
\n
    function nonadjacent(left, right) {\n
        if (option.white) {\n
            left = left || token;\n
            right = right || nexttoken;\n
            if (left.line === right.line && left.character === right.from) {\n
                left.from += (left.character - left.from);\n
                warning("Missing space after \'{a}\'.",\n
                        left, left.value);\n
            }\n
        }\n
    }\n
\n
    function nobreaknonadjacent(left, right) {\n
        left = left || token;\n
        right = right || nexttoken;\n
        if (!option.laxbreak && left.line !== right.line) {\n
            warning("Bad line breaking before \'{a}\'.", right, right.id);\n
        } else if (option.white) {\n
            left = left || token;\n
            right = right || nexttoken;\n
            if (left.character === right.from) {\n
                left.from += (left.character - left.from);\n
                warning("Missing space after \'{a}\'.",\n
                        left, left.value);\n
            }\n
        }\n
    }\n
\n
    function indentation(bias) {\n
        var i;\n
        if (option.white && nexttoken.id !== \'(end)\') {\n
            i = indent + (bias || 0);\n
            if (nexttoken.from !== i) {\n
                warning(\n
"Expected \'{a}\' to have an indentation at {b} instead at {c}.",\n
                        nexttoken, nexttoken.value, i, nexttoken.from);\n
            }\n
        }\n
    }\n
\n
    function nolinebreak(t) {\n
        t = t || token;\n
        if (t.line !== nexttoken.line) {\n
            warning("Line breaking error \'{a}\'.", t, t.value);\n
        }\n
    }\n
\n
\n
    function comma() {\n
        if (token.line !== nexttoken.line) {\n
            if (!option.laxcomma) {\n
                if (comma.first) {\n
                    warning("Comma warnings can be turned off with \'laxcomma\'");\n
                    comma.first = false;\n
                }\n
                warning("Bad line breaking before \'{a}\'.", token, nexttoken.id);\n
            }\n
        } else if (!token.comment && token.character !== nexttoken.from && option.white) {\n
            token.from += (token.character - token.from);\n
            warning("Unexpected space after \'{a}\'.", token, token.value);\n
        }\n
        advance(\',\');\n
        nonadjacent(token, nexttoken);\n
    }\n
\n
\n
// Functional constructors for making the symbols that will be inherited by\n
// tokens.\n
\n
    function symbol(s, p) {\n
        var x = syntax[s];\n
        if (!x || typeof x !== \'object\') {\n
            syntax[s] = x = {\n
                id: s,\n
                lbp: p,\n
                value: s\n
            };\n
        }\n
        return x;\n
    }\n
\n
\n
    function delim(s) {\n
        return symbol(s, 0);\n
    }\n
\n
\n
    function stmt(s, f) {\n
        var x = delim(s);\n
        x.identifier = x.reserved = true;\n
        x.fud = f;\n
        return x;\n
    }\n
\n
\n
    function blockstmt(s, f) {\n
        var x = stmt(s, f);\n
        x.block = true;\n
        return x;\n
    }\n
\n
\n
    function reserveName(x) {\n
        var c = x.id.charAt(0);\n
        if ((c >= \'a\' && c <= \'z\') || (c >= \'A\' && c <= \'Z\')) {\n
            x.identifier = x.reserved = true;\n
        }\n
        return x;\n
    }\n
\n
\n
    function prefix(s, f) {\n
        var x = symbol(s, 150);\n
        reserveName(x);\n
        x.nud = (typeof f === \'function\') ? f : function () {\n
            this.right = expression(150);\n
            this.arity = \'unary\';\n
            if (this.id === \'++\' || this.id === \'--\') {\n
                if (option.plusplus) {\n
                    warning("Unexpected use of \'{a}\'.", this, this.id);\n
                } else if ((!this.right.identifier || this.right.reserved) &&\n
                        this.right.id !== \'.\' && this.right.id !== \'[\') {\n
                    warning("Bad operand.", this);\n
                }\n
            }\n
            return this;\n
        };\n
        return x;\n
    }\n
\n
\n
    function type(s, f) {\n
        var x = delim(s);\n
        x.type = s;\n
        x.nud = f;\n
        return x;\n
    }\n
\n
\n
    function reserve(s, f) {\n
        var x = type(s, f);\n
        x.identifier = x.reserved = true;\n
        return x;\n
    }\n
\n
\n
    function reservevar(s, v) {\n
        return reserve(s, function () {\n
            if (typeof v === \'function\') {\n
                v(this);\n
            }\n
            return this;\n
        });\n
    }\n
\n
\n
    function infix(s, f, p, w) {\n
        var x = symbol(s, p);\n
        reserveName(x);\n
        x.led = function (left) {\n
            if (!w) {\n
                nobreaknonadjacent(prevtoken, token);\n
                nonadjacent(token, nexttoken);\n
            }\n
            if (s === "in" && left.id === "!") {\n
                warning("Confusing use of \'{a}\'.", left, \'!\');\n
            }\n
            if (typeof f === \'function\') {\n
                return f(left, this);\n
            } else {\n
                this.left = left;\n
                this.right = expression(p);\n
                return this;\n
            }\n
        };\n
        return x;\n
    }\n
\n
\n
    function relation(s, f) {\n
        var x = symbol(s, 100);\n
        x.led = function (left) {\n
            nobreaknonadjacent(prevtoken, token);\n
            nonadjacent(token, nexttoken);\n
            var right = expression(100);\n
            if ((left && left.id === \'NaN\') || (right && right.id === \'NaN\')) {\n
                warning("Use the isNaN function to compare with NaN.", this);\n
            } else if (f) {\n
                f.apply(this, [left, right]);\n
            }\n
            if (left.id === \'!\') {\n
                warning("Confusing use of \'{a}\'.", left, \'!\');\n
            }\n
            if (right.id === \'!\') {\n
                warning("Confusing use of \'{a}\'.", right, \'!\');\n
            }\n
            this.left = left;\n
            this.right = right;\n
            return this;\n
        };\n
        return x;\n
    }\n
\n
\n
    function isPoorRelation(node) {\n
        return node &&\n
              ((node.type === \'(number)\' && +node.value === 0) ||\n
               (node.type === \'(string)\' && node.value === \'\') ||\n
               (node.type === \'null\' && !option.eqnull) ||\n
                node.type === \'true\' ||\n
                node.type === \'false\' ||\n
                node.type === \'undefined\');\n
    }\n
\n
\n
    function assignop(s, f) {\n
        symbol(s, 20).exps = true;\n
        return infix(s, function (left, that) {\n
            var l;\n
            that.left = left;\n
            if (predefined[left.value] === false &&\n
                    scope[left.value][\'(global)\'] === true) {\n
                warning("Read only.", left);\n
            } else if (left[\'function\']) {\n
                warning("\'{a}\' is a function.", left, left.value);\n
            }\n
            if (left) {\n
                if (option.esnext && funct[left.value] === \'const\') {\n
                    warning("Attempting to override \'{a}\' which is a constant", left, left.value);\n
                }\n
                if (left.id === \'.\' || left.id === \'[\') {\n
                    if (!left.left || left.left.value === \'arguments\') {\n
                        warning(\'Bad assignment.\', that);\n
                    }\n
                    that.right = expression(19);\n
                    return that;\n
                } else if (left.identifier && !left.reserved) {\n
                    if (funct[left.value] === \'exception\') {\n
                        warning("Do not assign to the exception parameter.", left);\n
                    }\n
                    that.right = expression(19);\n
                    return that;\n
                }\n
                if (left === syntax[\'function\']) {\n
                    warning(\n
"Expected an identifier in an assignment and instead saw a function invocation.",\n
                                token);\n
                }\n
            }\n
            error("Bad assignment.", that);\n
        }, 20);\n
    }\n
\n
\n
    function bitwise(s, f, p) {\n
        var x = symbol(s, p);\n
        reserveName(x);\n
        x.led = (typeof f === \'function\') ? f : function (left) {\n
            if (option.bitwise) {\n
                warning("Unexpected use of \'{a}\'.", this, this.id);\n
            }\n
            this.left = left;\n
            this.right = expression(p);\n
            return this;\n
        };\n
        return x;\n
    }\n
\n
\n
    function bitwiseassignop(s) {\n
        symbol(s, 20).exps = true;\n
        return infix(s, function (left, that) {\n
            if (option.bitwise) {\n
                warning("Unexpected use of \'{a}\'.", that, that.id);\n
            }\n
            nonadjacent(prevtoken, token);\n
            nonadjacent(token, nexttoken);\n
            if (left) {\n
                if (left.id === \'.\' || left.id === \'[\' ||\n
                        (left.identifier && !left.reserved)) {\n
                    expression(19);\n
                    return that;\n
                }\n
                if (left === syntax[\'function\']) {\n
                    warning(\n
"Expected an identifier in an assignment, and instead saw a function invocation.",\n
                                token);\n
                }\n
                return that;\n
            }\n
            error("Bad assignment.", that);\n
        }, 20);\n
    }\n
\n
\n
    function suffix(s, f) {\n
        var x = symbol(s, 150);\n
        x.led = function (left) {\n
            if (option.plusplus) {\n
                warning("Unexpected use of \'{a}\'.", this, this.id);\n
            } else if ((!left.identifier || left.reserved) &&\n
                    left.id !== \'.\' && left.id !== \'[\') {\n
                warning("Bad operand.", this);\n
            }\n
            this.left = left;\n
            return this;\n
        };\n
        return x;\n
    }\n
\n
\n
    // fnparam means that this identifier is being defined as a function\n
    // argument (see identifier())\n
    function optionalidentifier(fnparam) {\n
        if (nexttoken.identifier) {\n
            advance();\n
            if (token.reserved && !option.es5) {\n
                // `undefined` as a function param is a common pattern to protect\n
                // against the case when somebody does `undefined = true` and\n
                // help with minification. More info: https://gist.github.com/315916\n
                if (!fnparam || token.value !== \'undefined\') {\n
                    warning("Expected an identifier and instead saw \'{a}\' (a reserved word).",\n
                            token, token.id);\n
                }\n
            }\n
            return token.value;\n
        }\n
    }\n
\n
    // fnparam means that this identifier is being defined as a function\n
    // argument\n
    function identifier(fnparam) {\n
        var i = optionalidentifier(fnparam);\n
        if (i) {\n
            return i;\n
        }\n
        if (token.id === \'function\' && nexttoken.id === \'(\') {\n
            warning("Missing name in function declaration.");\n
        } else {\n
            error("Expected an identifier and instead saw \'{a}\'.",\n
                    nexttoken, nexttoken.value);\n
        }\n
    }\n
\n
\n
    function reachable(s) {\n
        var i = 0, t;\n
        if (nexttoken.id !== \';\' || noreach) {\n
            return;\n
        }\n
        for (;;) {\n
            t = peek(i);\n
            if (t.reach) {\n
                return;\n
            }\n
            if (t.id !== \'(endline)\') {\n
                if (t.id === \'function\') {\n
                    if (!option.latedef) {\n
                        break;\n
                    }\n
                    warning(\n
"Inner functions should be listed at the top of the outer function.", t);\n
                    break;\n
                }\n
                warning("Unreachable \'{a}\' after \'{b}\'.", t, t.value, s);\n
                break;\n
            }\n
            i += 1;\n
        }\n
    }\n
\n
\n
    function statement(noindent) {\n
        var i = indent, r, s = scope, t = nexttoken;\n
\n
        if (t.id === ";") {\n
            advance(";");\n
            return;\n
        }\n
\n
// Is this a labelled statement?\n
\n
        if (t.identifier && !t.reserved && peek().id === \':\') {\n
            advance();\n
            advance(\':\');\n
            scope = Object.create(s);\n
            addlabel(t.value, \'label\');\n
            if (!nexttoken.labelled) {\n
                warning("Label \'{a}\' on {b} statement.",\n
                        nexttoken, t.value, nexttoken.value);\n
            }\n
            if (jx.test(t.value + \':\')) {\n
                warning("Label \'{a}\' looks like a javascript url.",\n
                        t, t.value);\n
            }\n
            nexttoken.label = t.value;\n
            t = nexttoken;\n
        }\n
\n
// Parse the statement.\n
\n
        if (!noindent) {\n
            indentation();\n
        }\n
        r = expression(0, true);\n
\n
        // Look for the final semicolon.\n
        if (!t.block) {\n
            if (!option.expr && (!r || !r.exps)) {\n
                warning("Expected an assignment or function call and instead saw an expression.",\n
                    token);\n
            } else if (option.nonew && r.id === \'(\' && r.left.id === \'new\') {\n
                warning("Do not use \'new\' for side effects.");\n
            }\n
\n
            if (nexttoken.id === \',\') {\n
                return comma();\n
            }\n
\n
            if (nexttoken.id !== \';\') {\n
                if (!option.asi) {\n
                    // If this is the last statement in a block that ends on\n
                    // the same line *and* option lastsemic is on, ignore the warning.\n
                    // Otherwise, complain about missing semicolon.\n
                    if (!option.lastsemic || nexttoken.id !== \'}\' ||\n
                            nexttoken.line !== token.line) {\n
                        warningAt("Missing semicolon.", token.line, token.character);\n
                    }\n
                }\n
            } else {\n
                adjacent(token, nexttoken);\n
                advance(\';\');\n
                nonadjacent(token, nexttoken);\n
            }\n
        }\n
\n
// Restore the indentation.\n
\n
        indent = i;\n
        scope = s;\n
        return r;\n
    }\n
\n
\n
    function statements(startLine) {\n
        var a = [], f, p;\n
\n
        while (!nexttoken.reach && nexttoken.id !== \'(end)\') {\n
            if (nexttoken.id === \';\') {\n
                p = peek();\n
                if (!p || p.id !== "(") {\n
                    warning("Unnecessary semicolon.");\n
                }\n
                advance(\';\');\n
            } el

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

se {\n
                a.push(statement(startLine === nexttoken.line));\n
            }\n
        }\n
        return a;\n
    }\n
\n
\n
    /*\n
     * read all directives\n
     * recognizes a simple form of asi, but always\n
     * warns, if it is used\n
     */\n
    function directives() {\n
        var i, p, pn;\n
\n
        for (;;) {\n
            if (nexttoken.id === "(string)") {\n
                p = peek(0);\n
                if (p.id === "(endline)") {\n
                    i = 1;\n
                    do {\n
                        pn = peek(i);\n
                        i = i + 1;\n
                    } while (pn.id === "(endline)");\n
\n
                    if (pn.id !== ";") {\n
                        if (pn.id !== "(string)" && pn.id !== "(number)" &&\n
                            pn.id !== "(regexp)" && pn.identifier !== true &&\n
                            pn.id !== "}") {\n
                            break;\n
                        }\n
                        warning("Missing semicolon.", nexttoken);\n
                    } else {\n
                        p = pn;\n
                    }\n
                } else if (p.id === "}") {\n
                    // directive with no other statements, warn about missing semicolon\n
                    warning("Missing semicolon.", p);\n
                } else if (p.id !== ";") {\n
                    break;\n
                }\n
\n
                indentation();\n
                advance();\n
                if (directive[token.value]) {\n
                    warning("Unnecessary directive \\"{a}\\".", token, token.value);\n
                }\n
\n
                if (token.value === "use strict") {\n
                    option.newcap = true;\n
                    option.undef = true;\n
                }\n
\n
                // there\'s no directive negation, so always set to true\n
                directive[token.value] = true;\n
\n
                if (p.id === ";") {\n
                    advance(";");\n
                }\n
                continue;\n
            }\n
            break;\n
        }\n
    }\n
\n
\n
    /*\n
     * Parses a single block. A block is a sequence of statements wrapped in\n
     * braces.\n
     *\n
     * ordinary - true for everything but function bodies and try blocks.\n
     * stmt     - true if block can be a single statement (e.g. in if/for/while).\n
     * isfunc   - true if block is a function body\n
     */\n
    function block(ordinary, stmt, isfunc) {\n
        var a,\n
            b = inblock,\n
            old_indent = indent,\n
            m,\n
            s = scope,\n
            t,\n
            line,\n
            d;\n
\n
        inblock = ordinary;\n
        if (!ordinary || !option.funcscope) scope = Object.create(scope);\n
        nonadjacent(token, nexttoken);\n
        t = nexttoken;\n
\n
        if (nexttoken.id === \'{\') {\n
            advance(\'{\');\n
            line = token.line;\n
            if (nexttoken.id !== \'}\') {\n
                indent += option.indent;\n
                while (!ordinary && nexttoken.from > indent) {\n
                    indent += option.indent;\n
                }\n
\n
                if (isfunc) {\n
                    m = {};\n
                    for (d in directive) {\n
                        if (is_own(directive, d)) {\n
                            m[d] = directive[d];\n
                        }\n
                    }\n
                    directives();\n
\n
                    if (option.strict && funct[\'(context)\'][\'(global)\']) {\n
                        if (!m["use strict"] && !directive["use strict"]) {\n
                            warning("Missing \\"use strict\\" statement.");\n
                        }\n
                    }\n
                }\n
\n
                a = statements(line);\n
\n
                if (isfunc) {\n
                    directive = m;\n
                }\n
\n
                indent -= option.indent;\n
                if (line !== nexttoken.line) {\n
                    indentation();\n
                }\n
            } else if (line !== nexttoken.line) {\n
                indentation();\n
            }\n
            advance(\'}\', t);\n
            indent = old_indent;\n
        } else if (!ordinary) {\n
            error("Expected \'{a}\' and instead saw \'{b}\'.",\n
                  nexttoken, \'{\', nexttoken.value);\n
        } else {\n
            if (!stmt || option.curly)\n
                warning("Expected \'{a}\' and instead saw \'{b}\'.",\n
                        nexttoken, \'{\', nexttoken.value);\n
\n
            noreach = true;\n
            indent += option.indent;\n
            // test indentation only if statement is in new line\n
            a = [statement(nexttoken.line === token.line)];\n
            indent -= option.indent;\n
            noreach = false;\n
        }\n
        funct[\'(verb)\'] = null;\n
        if (!ordinary || !option.funcscope) scope = s;\n
        inblock = b;\n
        if (ordinary && option.noempty && (!a || a.length === 0)) {\n
            warning("Empty block.");\n
        }\n
        return a;\n
    }\n
\n
\n
    function countMember(m) {\n
        if (membersOnly && typeof membersOnly[m] !== \'boolean\') {\n
            warning("Unexpected /*member \'{a}\'.", token, m);\n
        }\n
        if (typeof member[m] === \'number\') {\n
            member[m] += 1;\n
        } else {\n
            member[m] = 1;\n
        }\n
    }\n
\n
\n
    function note_implied(token) {\n
        var name = token.value, line = token.line, a = implied[name];\n
        if (typeof a === \'function\') {\n
            a = false;\n
        }\n
\n
        if (!a) {\n
            a = [line];\n
            implied[name] = a;\n
        } else if (a[a.length - 1] !== line) {\n
            a.push(line);\n
        }\n
    }\n
\n
\n
    // Build the syntax table by declaring the syntactic elements of the language.\n
\n
    type(\'(number)\', function () {\n
        return this;\n
    });\n
\n
    type(\'(string)\', function () {\n
        return this;\n
    });\n
\n
    syntax[\'(identifier)\'] = {\n
        type: \'(identifier)\',\n
        lbp: 0,\n
        identifier: true,\n
        nud: function () {\n
            var v = this.value,\n
                s = scope[v],\n
                f;\n
\n
            if (typeof s === \'function\') {\n
                // Protection against accidental inheritance.\n
                s = undefined;\n
            } else if (typeof s === \'boolean\') {\n
                f = funct;\n
                funct = functions[0];\n
                addlabel(v, \'var\');\n
                s = funct;\n
                funct = f;\n
            }\n
\n
            // The name is in scope and defined in the current function.\n
            if (funct === s) {\n
                // Change \'unused\' to \'var\', and reject labels.\n
                switch (funct[v]) {\n
                case \'unused\':\n
                    funct[v] = \'var\';\n
                    break;\n
                case \'unction\':\n
                    funct[v] = \'function\';\n
                    this[\'function\'] = true;\n
                    break;\n
                case \'function\':\n
                    this[\'function\'] = true;\n
                    break;\n
                case \'label\':\n
                    warning("\'{a}\' is a statement label.", token, v);\n
                    break;\n
                }\n
            } else if (funct[\'(global)\']) {\n
                // The name is not defined in the function.  If we are in the global\n
                // scope, then we have an undefined variable.\n
                //\n
                // Operators typeof and delete do not raise runtime errors even if\n
                // the base object of a reference is null so no need to display warning\n
                // if we\'re inside of typeof or delete.\n
\n
                if (option.undef && typeof predefined[v] !== \'boolean\') {\n
                    // Attempting to subscript a null reference will throw an\n
                    // error, even within the typeof and delete operators\n
                    if (!(anonname === \'typeof\' || anonname === \'delete\') ||\n
                        (nexttoken && (nexttoken.value === \'.\' || nexttoken.value === \'[\'))) {\n
\n
                        isundef(funct, "\'{a}\' is not defined.", token, v);\n
                    }\n
                }\n
                note_implied(token);\n
            } else {\n
                // If the name is already defined in the current\n
                // function, but not as outer, then there is a scope error.\n
\n
                switch (funct[v]) {\n
                case \'closure\':\n
                case \'function\':\n
                case \'var\':\n
                case \'unused\':\n
                    warning("\'{a}\' used out of scope.", token, v);\n
                    break;\n
                case \'label\':\n
                    warning("\'{a}\' is a statement label.", token, v);\n
                    break;\n
                case \'outer\':\n
                case \'global\':\n
                    break;\n
                default:\n
                    // If the name is defined in an outer function, make an outer entry,\n
                    // and if it was unused, make it var.\n
                    if (s === true) {\n
                        funct[v] = true;\n
                    } else if (s === null) {\n
                        warning("\'{a}\' is not allowed.", token, v);\n
                        note_implied(token);\n
                    } else if (typeof s !== \'object\') {\n
                        // Operators typeof and delete do not raise runtime errors even\n
                        // if the base object of a reference is null so no need to\n
                        // display warning if we\'re inside of typeof or delete.\n
                        if (option.undef) {\n
                            // Attempting to subscript a null reference will throw an\n
                            // error, even within the typeof and delete operators\n
                            if (!(anonname === \'typeof\' || anonname === \'delete\') ||\n
                                (nexttoken &&\n
                                    (nexttoken.value === \'.\' || nexttoken.value === \'[\'))) {\n
\n
                                isundef(funct, "\'{a}\' is not defined.", token, v);\n
                            }\n
                        }\n
                        funct[v] = true;\n
                        note_implied(token);\n
                    } else {\n
                        switch (s[v]) {\n
                        case \'function\':\n
                        case \'unction\':\n
                            this[\'function\'] = true;\n
                            s[v] = \'closure\';\n
                            funct[v] = s[\'(global)\'] ? \'global\' : \'outer\';\n
                            break;\n
                        case \'var\':\n
                        case \'unused\':\n
                            s[v] = \'closure\';\n
                            funct[v] = s[\'(global)\'] ? \'global\' : \'outer\';\n
                            break;\n
                        case \'closure\':\n
                        case \'parameter\':\n
                            funct[v] = s[\'(global)\'] ? \'global\' : \'outer\';\n
                            break;\n
                        case \'label\':\n
                            warning("\'{a}\' is a statement label.", token, v);\n
                        }\n
                    }\n
                }\n
            }\n
            return this;\n
        },\n
        led: function () {\n
            error("Expected an operator and instead saw \'{a}\'.",\n
                nexttoken, nexttoken.value);\n
        }\n
    };\n
\n
    type(\'(regexp)\', function () {\n
        return this;\n
    });\n
\n
\n
// ECMAScript parser\n
\n
    delim(\'(endline)\');\n
    delim(\'(begin)\');\n
    delim(\'(end)\').reach = true;\n
    delim(\'</\').reach = true;\n
    delim(\'<!\');\n
    delim(\'<!--\');\n
    delim(\'-->\');\n
    delim(\'(error)\').reach = true;\n
    delim(\'}\').reach = true;\n
    delim(\')\');\n
    delim(\']\');\n
    delim(\'"\').reach = true;\n
    delim("\'").reach = true;\n
    delim(\';\');\n
    delim(\':\').reach = true;\n
    delim(\',\');\n
    delim(\'#\');\n
    delim(\'@\');\n
    reserve(\'else\');\n
    reserve(\'case\').reach = true;\n
    reserve(\'catch\');\n
    reserve(\'default\').reach = true;\n
    reserve(\'finally\');\n
    reservevar(\'arguments\', function (x) {\n
        if (directive[\'use strict\'] && funct[\'(global)\']) {\n
            warning("Strict violation.", x);\n
        }\n
    });\n
    reservevar(\'eval\');\n
    reservevar(\'false\');\n
    reservevar(\'Infinity\');\n
    reservevar(\'NaN\');\n
    reservevar(\'null\');\n
    reservevar(\'this\', function (x) {\n
        if (directive[\'use strict\'] && !option.validthis && ((funct[\'(statement)\'] &&\n
                funct[\'(name)\'].charAt(0) > \'Z\') || funct[\'(global)\'])) {\n
            warning("Possible strict violation.", x);\n
        }\n
    });\n
    reservevar(\'true\');\n
    reservevar(\'undefined\');\n
    assignop(\'=\', \'assign\', 20);\n
    assignop(\'+=\', \'assignadd\', 20);\n
    assignop(\'-=\', \'assignsub\', 20);\n
    assignop(\'*=\', \'assignmult\', 20);\n
    assignop(\'/=\', \'assigndiv\', 20).nud = function () {\n
        error("A regular expression literal can be confused with \'/=\'.");\n
    };\n
    assignop(\'%=\', \'assignmod\', 20);\n
    bitwiseassignop(\'&=\', \'assignbitand\', 20);\n
    bitwiseassignop(\'|=\', \'assignbitor\', 20);\n
    bitwiseassignop(\'^=\', \'assignbitxor\', 20);\n
    bitwiseassignop(\'<<=\', \'assignshiftleft\', 20);\n
    bitwiseassignop(\'>>=\', \'assignshiftright\', 20);\n
    bitwiseassignop(\'>>>=\', \'assignshiftrightunsigned\', 20);\n
    infix(\'?\', function (left, that) {\n
        that.left = left;\n
        that.right = expression(10);\n
        advance(\':\');\n
        that[\'else\'] = expression(10);\n
        return that;\n
    }, 30);\n
\n
    infix(\'||\', \'or\', 40);\n
    infix(\'&&\', \'and\', 50);\n
    bitwise(\'|\', \'bitor\', 70);\n
    bitwise(\'^\', \'bitxor\', 80);\n
    bitwise(\'&\', \'bitand\', 90);\n
    relation(\'==\', function (left, right) {\n
        var eqnull = option.eqnull && (left.value === \'null\' || right.value === \'null\');\n
\n
        if (!eqnull && option.eqeqeq)\n
            warning("Expected \'{a}\' and instead saw \'{b}\'.", this, \'===\', \'==\');\n
        else if (isPoorRelation(left))\n
            warning("Use \'{a}\' to compare with \'{b}\'.", this, \'===\', left.value);\n
        else if (isPoorRelation(right))\n
            warning("Use \'{a}\' to compare with \'{b}\'.", this, \'===\', right.value);\n
\n
        return this;\n
    });\n
    relation(\'===\');\n
    relation(\'!=\', function (left, right) {\n
        var eqnull = option.eqnull &&\n
                (left.value === \'null\' || right.value === \'null\');\n
\n
        if (!eqnull && option.eqeqeq) {\n
            warning("Expected \'{a}\' and instead saw \'{b}\'.",\n
                    this, \'!==\', \'!=\');\n
        } else if (isPoorRelation(left)) {\n
            warning("Use \'{a}\' to compare with \'{b}\'.",\n
                    this, \'!==\', left.value);\n
        } else if (isPoorRelation(right)) {\n
            warning("Use \'{a}\' to compare with \'{b}\'.",\n
                    this, \'!==\', right.value);\n
        }\n
        return this;\n
    });\n
    relation(\'!==\');\n
    relation(\'<\');\n
    relation(\'>\');\n
    relation(\'<=\');\n
    relation(\'>=\');\n
    bitwise(\'<<\', \'shiftleft\', 120);\n
    bitwise(\'>>\', \'shiftright\', 120);\n
    bitwise(\'>>>\', \'shiftrightunsigned\', 120);\n
    infix(\'in\', \'in\', 120);\n
    infix(\'instanceof\', \'instanceof\', 120);\n
    infix(\'+\', function (left, that) {\n
        var right = expression(130);\n
        if (left && right && left.id === \'(string)\' && right.id === \'(string)\') {\n
            left.value += right.value;\n
            left.character = right.character;\n
            if (!option.scripturl && jx.test(left.value)) {\n
                warning("JavaScript URL.", left);\n
            }\n
            return left;\n
        }\n
        that.left = left;\n
        that.right = right;\n
        return that;\n
    }, 130);\n
    prefix(\'+\', \'num\');\n
    prefix(\'+++\', function () {\n
        warning("Confusing pluses.");\n
        this.right = expression(150);\n
        this.arity = \'unary\';\n
        return this;\n
    });\n
    infix(\'+++\', function (left) {\n
        warning("Confusing pluses.");\n
        this.left = left;\n
        this.right = expression(130);\n
        return this;\n
    }, 130);\n
    infix(\'-\', \'sub\', 130);\n
    prefix(\'-\', \'neg\');\n
    prefix(\'---\', function () {\n
        warning("Confusing minuses.");\n
        this.right = expression(150);\n
        this.arity = \'unary\';\n
        return this;\n
    });\n
    infix(\'---\', function (left) {\n
        warning("Confusing minuses.");\n
        this.left = left;\n
        this.right = expression(130);\n
        return this;\n
    }, 130);\n
    infix(\'*\', \'mult\', 140);\n
    infix(\'/\', \'div\', 140);\n
    infix(\'%\', \'mod\', 140);\n
\n
    suffix(\'++\', \'postinc\');\n
    prefix(\'++\', \'preinc\');\n
    syntax[\'++\'].exps = true;\n
\n
    suffix(\'--\', \'postdec\');\n
    prefix(\'--\', \'predec\');\n
    syntax[\'--\'].exps = true;\n
    prefix(\'delete\', function () {\n
        var p = expression(0);\n
        if (!p || (p.id !== \'.\' && p.id !== \'[\')) {\n
            warning("Variables should not be deleted.");\n
        }\n
        this.first = p;\n
        return this;\n
    }).exps = true;\n
\n
    prefix(\'~\', function () {\n
        if (option.bitwise) {\n
            warning("Unexpected \'{a}\'.", this, \'~\');\n
        }\n
        expression(150);\n
        return this;\n
    });\n
\n
    prefix(\'!\', function () {\n
        this.right = expression(150);\n
        this.arity = \'unary\';\n
        if (bang[this.right.id] === true) {\n
            warning("Confusing use of \'{a}\'.", this, \'!\');\n
        }\n
        return this;\n
    });\n
    prefix(\'typeof\', \'typeof\');\n
    prefix(\'new\', function () {\n
        var c = expression(155), i;\n
        if (c && c.id !== \'function\') {\n
            if (c.identifier) {\n
                c[\'new\'] = true;\n
                switch (c.value) {\n
                case \'Number\':\n
                case \'String\':\n
                case \'Boolean\':\n
                case \'Math\':\n
                case \'JSON\':\n
                    warning("Do not use {a} as a constructor.", token, c.value);\n
                    break;\n
                case \'Function\':\n
                    if (!option.evil) {\n
                        warning("The Function constructor is eval.");\n
                    }\n
                    break;\n
                case \'Date\':\n
                case \'RegExp\':\n
                    break;\n
                default:\n
                    if (c.id !== \'function\') {\n
                        i = c.value.substr(0, 1);\n
                        if (option.newcap && (i < \'A\' || i > \'Z\')) {\n
                            warning("A constructor name should start with an uppercase letter.",\n
                                token);\n
                        }\n
                    }\n
                }\n
            } else {\n
                if (c.id !== \'.\' && c.id !== \'[\' && c.id !== \'(\') {\n
                    warning("Bad constructor.", token);\n
                }\n
            }\n
        } else {\n
            if (!option.supernew)\n
                warning("Weird construction. Delete \'new\'.", this);\n
        }\n
        adjacent(token, nexttoken);\n
        if (nexttoken.id !== \'(\' && !option.supernew) {\n
            warning("Missing \'()\' invoking a constructor.");\n
        }\n
        this.first = c;\n
        return this;\n
    });\n
    syntax[\'new\'].exps = true;\n
\n
    prefix(\'void\').exps = true;\n
\n
    infix(\'.\', function (left, that) {\n
        adjacent(prevtoken, token);\n
        nobreak();\n
        var m = identifier();\n
        if (typeof m === \'string\') {\n
            countMember(m);\n
        }\n
        that.left = left;\n
        that.right = m;\n
        if (left && left.value === \'arguments\' && (m === \'callee\' || m === \'caller\')) {\n
            if (option.noarg)\n
                warning("Avoid arguments.{a}.", left, m);\n
            else if (directive[\'use strict\'])\n
                error(\'Strict violation.\');\n
        } else if (!option.evil && left && left.value === \'document\' &&\n
                (m === \'write\' || m === \'writeln\')) {\n
            warning("document.write can be a form of eval.", left);\n
        }\n
        if (!option.evil && (m === \'eval\' || m === \'execScript\')) {\n
            warning(\'eval is evil.\');\n
        }\n
        return that;\n
    }, 160, true);\n
\n
    infix(\'(\', function (left, that) {\n
        if (prevtoken.id !== \'}\' && prevtoken.id !== \')\') {\n
            nobreak(prevtoken, token);\n
        }\n
        nospace();\n
        if (option.immed && !left.immed && left.id === \'function\') {\n
            warning("Wrap an immediate function invocation in parentheses " +\n
                "to assist the reader in understanding that the expression " +\n
                "is the result of a function, and not the function itself.");\n
        }\n
        var n = 0,\n
            p = [];\n
        if (left) {\n
            if (left.type === \'(identifier)\') {\n
                if (left.value.match(/^[A-Z]([A-Z0-9_$]*[a-z][A-Za-z0-9_$]*)?$/)) {\n
                    if (left.value !== \'Number\' && left.value !== \'String\' &&\n
                            left.value !== \'Boolean\' &&\n
                            left.value !== \'Date\') {\n
                        if (left.value === \'Math\') {\n
                            warning("Math is not a function.", left);\n
                        } else if (option.newcap) {\n
                            warning(\n
"Missing \'new\' prefix when invoking a constructor.", left);\n
                        }\n
                    }\n
                }\n
            }\n
        }\n
        if (nexttoken.id !== \')\') {\n
            for (;;) {\n
                p[p.length] = expression(10);\n
                n += 1;\n
                if (nexttoken.id !== \',\') {\n
                    break;\n
                }\n
                comma();\n
            }\n
        }\n
        advance(\')\');\n
        nospace(prevtoken, token);\n
        if (typeof left === \'object\') {\n
            if (left.value === \'parseInt\' && n === 1) {\n
                warning("Missing radix parameter.", left);\n
            }\n
            if (!option.evil) {\n
                if (left.value === \'eval\' || left.value === \'Function\' ||\n
                        left.value === \'execScript\') {\n
                    warning("eval is evil.", left);\n
                } else if (p[0] && p[0].id === \'(string)\' &&\n
                       (left.value === \'setTimeout\' ||\n
                        left.value === \'setInterval\')) {\n
                    warning(\n
    "Implied eval is evil. Pass a function instead of a string.", left);\n
                }\n
            }\n
            if (!left.identifier && left.id !== \'.\' && left.id !== \'[\' &&\n
                    left.id !== \'(\' && left.id !== \'&&\' && left.id !== \'||\' &&\n
                    left.id !== \'?\') {\n
                warning("Bad invocation.", left);\n
            }\n
        }\n
        that.left = left;\n
        return that;\n
    }, 155, true).exps = true;\n
\n
    prefix(\'(\', function () {\n
        nospace();\n
        if (nexttoken.id === \'function\') {\n
            nexttoken.immed = true;\n
        }\n
        var v = expression(0);\n
        advance(\')\', this);\n
        nospace(prevtoken, token);\n
        if (option.immed && v.id === \'function\') {\n
            if (nexttoken.id === \'(\' ||\n
              (nexttoken.id === \'.\' && (peek().value === \'call\' || peek().value === \'apply\'))) {\n
                warning(\n
"Move the invocation into the parens that contain the function.", nexttoken);\n
            } else {\n
                warning(\n
"Do not wrap function literals in parens unless they are to be immediately invoked.",\n
                        this);\n
            }\n
        }\n
        return v;\n
    });\n
\n
    infix(\'[\', function (left, that) {\n
        nobreak(prevtoken, token);\n
        nospace();\n
        var e = expression(0), s;\n
        if (e && e.type === \'(string)\') {\n
            if (!option.evil && (e.value === \'eval\' || e.value === \'execScript\')) {\n
                warning("eval is evil.", that);\n
            }\n
            countMember(e.value);\n
            if (!option.sub && ix.test(e.value)) {\n
                s = syntax[e.value];\n
                if (!s || !s.reserved) {\n
                    warning("[\'{a}\'] is better written in dot notation.",\n
                            e, e.value);\n
                }\n
            }\n
        }\n
        advance(\']\', that);\n
        nospace(prevtoken, token);\n
        that.left = left;\n
        that.right = e;\n
        return that;\n
    }, 160, true);\n
\n
    prefix(\'[\', function () {\n
        var b = token.line !== nexttoken.line;\n
        this.first = [];\n
        if (b) {\n
            indent += option.indent;\n
            if (nexttoken.from === indent + option.indent) {\n
                indent += option.indent;\n
            }\n
        }\n
        while (nexttoken.id !== \'(end)\') {\n
            while (nexttoken.id === \',\') {\n
                warning("Extra comma.");\n
                advance(\',\');\n
            }\n
            if (nexttoken.id === \']\') {\n
                break;\n
            }\n
            if (b && token.line !== nexttoken.line) {\n
                indentation();\n
            }\n
            this.first.push(expression(10));\n
            if (nexttoken.id === \',\') {\n
                comma();\n
                if (nexttoken.id === \']\' && !option.es5) {\n
                    warning("Extra comma.", token);\n
                    break;\n
                }\n
            } else {\n
                break;\n
            }\n
        }\n
        if (b) {\n
            indent -= option.indent;\n
            indentation();\n
        }\n
        advance(\']\', this);\n
        return this;\n
    }, 160);\n
\n
\n
    function property_name() {\n
        var id = optionalidentifier(true);\n
        if (!id) {\n
            if (nexttoken.id === \'(string)\') {\n
                id = nexttoken.value;\n
                advance();\n
            } else if (nexttoken.id === \'(number)\') {\n
                id = nexttoken.value.toString();\n
                advance();\n
            }\n
        }\n
        return id;\n
    }\n
\n
\n
    function functionparams() {\n
        var i, t = nexttoken, p = [];\n
        advance(\'(\');\n
        nospace();\n
        if (nexttoken.id === \')\') {\n
            advance(\')\');\n
            return;\n
        }\n
        for (;;) {\n
            i = identifier(true);\n
            p.push(i);\n
            addlabel(i, \'parameter\');\n
            if (nexttoken.id === \',\') {\n
                comma();\n
            } else {\n
                advance(\')\', t);\n
                nospace(prevtoken, token);\n
                return p;\n
            }\n
        }\n
    }\n
\n
\n
    function doFunction(i, statement) {\n
        var f,\n
            oldOption = option,\n
            oldScope  = scope;\n
\n
        option = Object.create(option);\n
        scope = Object.create(scope);\n
\n
        funct = {\n
            \'(name)\'     : i || \'"\' + anonname + \'"\',\n
            \'(line)\'     : nexttoken.line,\n
            \'(context)\'  : funct,\n
            \'(breakage)\' : 0,\n
            \'(loopage)\'  : 0,\n
            \'(scope)\'    : scope,\n
            \'(statement)\': statement\n
        };\n
        f = funct;\n
        token.funct = funct;\n
        functions.push(funct);\n
        if (i) {\n
            addlabel(i, \'function\');\n
        }\n
        funct[\'(params)\'] = functionparams();\n
\n
        block(false, false, true);\n
        scope = oldScope;\n
        option = oldOption;\n
        funct[\'(last)\'] = token.line;\n
        funct = funct[\'(context)\'];\n
        return f;\n
    }\n
\n
\n
    (function (x) {\n
        x.nud = function () {\n
            var b, f, i, j, p, t;\n
            var props = {}; // All properties, including accessors\n
\n
            function saveProperty(name, token) {\n
                if (props[name] && is_own(props, name))\n
                    warning("Duplicate member \'{a}\'.", nexttoken, i);\n
                else\n
                    props[name] = {};\n
\n
                props[name].basic = true;\n
                props[name].basicToken = token;\n
            }\n
\n
            function saveSetter(name, token) {\n
                if (props[name] && is_own(props, name)) {\n
                    if (props[name].basic || props[name].setter)\n
                        warning("Duplicate member \'{a}\'.", nexttoken, i);\n
                } else {\n
                    props[name] = {};\n
                }\n
\n
                props[name].setter = true;\n
                props[name].setterToken = token;\n
            }\n
\n
            function saveGetter(name) {\n
                if (props[name] && is_own(props, name)) {\n
                    if (props[name].basic || props[name].getter)\n
                        warning("Duplicate member \'{a}\'.", nexttoken, i);\n
                } else {\n
                    props[name] = {};\n
                }\n
\n
                props[name].getter = true;\n
                props[name].getterToken = token;\n
            }\n
\n
            b = token.line !== nexttoken.line;\n
            if (b) {\n
                indent += option.indent;\n
                if (nexttoken.from === indent + option.indent) {\n
                    indent += option.indent;\n
                }\n
            }\n
            for (;;) {\n
                if (nexttoken.id === \'}\') {\n
                    break;\n
                }\n
                if (b) {\n
                    indentation();\n
                }\n
                if (nexttoken.value === \'get\' && peek().id !== \':\') {\n
                    advance(\'get\');\n
                    if (!option.es5) {\n
                        error("get/set are ES5 features.");\n
                    }\n
                    i = property_name();\n
                    if (!i) {\n
                        error("Missing property name.");\n
                    }\n
                    saveGetter(i);\n
                    t = nexttoken;\n
                    adjacent(token, nexttoken);\n
                    f = doFunction();\n
                    p = f[\'(params)\'];\n
                    if (p) {\n
                        warning("Unexpected parameter \'{a}\' in get {b} function.", t, p[0], i);\n
                    }\n
                    adjacent(token, nexttoken);\n
                } else if (nexttoken.value === \'set\' && peek().id !== \':\') {\n
                    advance(\'set\');\n
                    if (!option.es5) {\n
                        error("get/set are ES5 features.");\n
                    }\n
                    i = property_name();\n
                    if (!i) {\n
                        error("Missing property name.");\n
                    }\n
                    saveSetter(i, nexttoken);\n
                    t = nexttoken;\n
                    adjacent(token, nexttoken);\n
                    f = doFunction();\n
                    p = f[\'(params)\'];\n
                    if (!p || p.length !== 1) {\n
                        warning("Expected a single parameter in set {a} function.", t, i);\n
                    }\n
                } else {\n
                    i = property_name();\n
                    saveProperty(i, nexttoken);\n
                    if (typeof i !== \'string\') {\n
                        break;\n
                    }\n
                    advance(\':\');\n
                    nonadjacent(token, nexttoken);\n
                    expression(10);\n
                }\n
\n
                countMember(i);\n
                if (nexttoken.id === \',\') {\n
                    comma();\n
                    if (nexttoken.id === \',\') {\n
                        warning("Extra comma.", token);\n
                    } else if (nexttoken.id === \'}\' && !option.es5) {\n
                        warning("Extra comma.", token);\n
                    }\n
                } else {\n
                    break;\n
                }\n
            }\n
            if (b) {\n
                indent -= option.indent;\n
                indentation();\n
            }\n
            advance(\'}\', this);\n
\n
            // Check for lonely setters if in the ES5 mode.\n
            if (option.es5) {\n
                for (var name in props) {\n
                    if (is_own(props, name) && props[name].setter && !props[name].getter) {\n
                        warning("Setter is defined without getter.", props[name].setterToken);\n
                    }\n
                }\n
            }\n
            return this;\n
        };\n
        x.fud = function () {\n
            error("Expected to see a statement and instead saw a block.", token);\n
        };\n
    }(delim(\'{\')));\n
\n
// This Function is called when esnext option is set to true\n
// it adds the `const` statement to JSHINT\n
\n
    useESNextSyntax = function () {\n
        var conststatement = stmt(\'const\', function (prefix) {\n
            var id, name, value;\n
\n
            this.first = [];\n
            for (;;) {\n
                nonadjacent(token, nexttoken);\n
                id = identifier();\n
                if (funct[id] === "const") {\n
                    warning("const \'" + id + "\' has already been declared");\n
                }\n
                if (funct[\'(global)\'] && predefined[id] === false) {\n
                    warning("Redefinition of \'{a}\'.", token, id);\n
                }\n
                addlabel(id, \'const\');\n
                if (prefix) {\n
                    break;\n
                }\n
                name = token;\n
                this.first.push(token);\n
\n
                if (nexttoken.id !== "=") {\n
                    warning("const " +\n
                      "\'{a}\' is initialized to \'undefined\'.", token, id);\n
                }\n
\n
                if (nexttoken.id === \'=\') {\n
                    nonadjacent(token, nexttoken);\n
                    advance(\'=\');\n
                    nonadjacent(token, nexttoken);\n
                    if (nexttoken.id === \'undefined\') {\n
                        warning("It is not necessary to initialize " +\n
                          "\'{a}\' to \'undefined\'.", token, id);\n
                    }\n
                    if (peek(0).id === \'=\' && nexttoken.identifier) {\n
                        error("Constant {a} was not declared correctly.",\n
                                nexttoken, nexttoken.value);\n
                    }\n
                    value = expression(0);\n
                    name.first = value;\n
                }\n
\n
                if (nexttoken.id !== \',\') {\n
                    break;\n
                }\n
                comma();\n
            }\n
            return this;\n
        });\n
        conststatement.exps = true;\n
    };\n
\n
    var varstatement = stmt(\'var\', function (prefix) {\n
        // JavaScript does not have block scope. It only has function scope. So,\n
        // declaring a variable in a block can have unexpected consequences.\n
        var id, name, value;\n
\n
        if (funct[\'(onevar)\'] && option.onevar) {\n
            warning("Too many var statements.");\n
        } else if (!funct[\'(global)\']) {\n
            funct[\'(onevar)\'] = true;\n
        }\n
        this.first = [];\n
        for (;;) {\n
            nonadjacent(token, nexttoken);\n
            id = identifier();\n
            if (option.esnext && funct[id] === "const") {\n
                warning("const \'" + id + "\' has already been declared");\n
            }\n
            if (funct[\'(global)\'] && predefined[id] === false) {\n
                warning("Redefinition of \'{a}\'.", token, id);\n
            }\n
            addlabel(id, \'unused\');\n
            if (prefix) {\n
                break;\n
            }\n
            name = token;\n
            this.first.push(token);\n
            if (nexttoken.id === \'=\') {\n
                nonadjacent(token, nexttoken);\n
                advance(\'=\');\n
                nonadjacent(token, nexttoken);\n
                if (nexttoken.id === \'undefined\') {\n
                    warning("It is not necessary to initialize \'{a}\' to \'undefined\'.", token, id);\n
                }\n
                if (peek(0).id === \'=\' && nexttoken.identifier) {\n
                    error("Variable {a} was not declared correctly.",\n
                            nexttoken, nexttoken.value);\n
                }\n
                value = expression(0);\n
                name.first = value;\n
            }\n
            if (nexttoken.id !== \',\') {\n
                break;\n
            }\n
            comma();\n
        }\n
        return this;\n
    });\n
    varstatement.exps = true;\n
\n
    blockstmt(\'function\', function () {\n
        if (inblock) {\n
            warning("Function declarations should not be placed in blocks. " +\n
                "Use a function expression or move the statement to the top of " +\n
                "the outer function.", token);\n
\n
        }\n
        var i = identifier();\n
        if (option.esnext && funct[i] === "const") {\n
            warning("const \'" + i + "\' has already been declared");\n
        }\n
        adjacent(token, nexttoken);\n
        addlabel(i, \'unction\');\n
        doFunction(i, true);\n
        if (nexttoken.id === \'(\' && nexttoken.line === token.line) {\n
            error(\n
"Function declarations are not invocable. Wrap the whole function invocation in parens.");\n
        }\n
        return this;\n
    });\n
\n
    prefix(\'function\', function () {\n
        var i = optionalidentifier();\n
        if (i) {\n
            adjacent(token, nexttoken);\n
        } else {\n
            nonadjacent(token, nexttoken);\n
        }\n
        doFunction(i);\n
        if (!option.loopfunc && funct[\'(loopage)\']) {\n
            warning("Don\'t make functions within a loop.");\n
        }\n
        return this;\n
    });\n
\n
    blockstmt(\'if\', function () {\n
        var t = nexttoken;\n
        advance(\'(\');\n
        nonadjacent(this, t);\n
        nospace();\n
        expression(20);\n
        if (nexttoken.id === \'=\') {\n
            if (!option.boss)\n
                warning("Expected a conditional expression and instead saw an assignment.");\n
            advance(\'=\');\n
            expression(20);\n
        }\n
        advance(\')\', t);\n
        nospace(prevtoken, token);\n
        block(true, true);\n
        if (nexttoken.id === \'else\') {\n
            nonadjacent(token, nexttoken);\n
            advance(\'else\');\n
            if (nexttoken.id === \'if\' || nexttoken.id === \'switch\') {\n
                statement(true);\n
            } else {\n
                block(true, true);\n
            }\n
        }\n
        return this;\n
    });\n
\n
    blockstmt(\'try\', function () {\n
        var b, e, s;\n
\n
        block(false);\n
        if (nexttoken.id === \'catch\') {\n
            advance(\'catch\');\n
            nonadjacent(token, nexttoken);\n
            advance(\'(\');\n
            s = scope;\n
            scope = Object.create(s);\n
            e = nexttoken.value;\n
            if (nexttoken.type !== \'(identifier)\') {\n
                warning("Expected an identifier and instead saw \'{a}\'.",\n
                    nexttoken, e);\n
            } else {\n
                addlabel(e, \'exception\');\n
            }\n
            advance();\n
            advance(\')\');\n
            block(false);\n
            b = true;\n
            scope = s;\n
        }\n
        if (nexttoken.id === \'finally\') {\n
            advance(\'finally\');\n
            block(false);\n
            return;\n
        } else if (!b) {\n
            error("Expected \'{a}\' and instead saw \'{b}\'.",\n
                    nexttoken, \'catch\', nexttoken.value);\n
        }\n
        return this;\n
    });\n
\n
    blockstmt(\'while\', function () {\n
        var t = nexttoken;\n
        funct[\'(breakage)\'] += 1;\n
        funct[\'(loopage)\'] += 1;\n
        advance(\'(\');\n
        nonadjacent(this, t);\n
        nospace();\n
        expression(20);\n
        if (nexttoken.id === \'=\') {\n
            if (!option.boss)\n
                warning("Expected a conditional expression and instead saw an assignment.");\n
            advance(\'=\');\n
            expression(20);\n
        }\n
        advance(\')\', t);\n
        nospace(prevtoken, token);\n
        block(true, true);\n
        funct[\'(breakage)\'] -= 1;\n
        funct[\'(loopage)\'] -= 1;\n
        return this;\n
    }).labelled = true;\n
\n
    blockstmt(\'with\', function () {\n
        var t = nexttoken;\n
        if (directive[\'use strict\']) {\n
            error("\'with\' is not allowed in strict mode.", token);\n
        } else if (!option.withstmt) {\n
            warning("Don\'t use \'with\'.", token);\n
        }\n
\n
        advance(\'(\');\n
        nonadjacent(this, t);\n
        nospace();\n
        expression(0);\n
        advance(\')\', t);\n
        nospace(prevtoken, token);\n
        block(true, true);\n
\n
        return this;\n
    });\n
\n
    blockstmt(\'switch\', function () {\n
        var t = nexttoken,\n
            g = false;\n
        funct[\'(breakage)\'] += 1;\n
        advance(\'(\');\n
        nonadjacent(this, t);\n
        nospace();\n
        this.condition = expression(20);\n
        advance(\')\', t);\n
        nospace(prevtoken, token);\n
        nonadjacent(token, nexttoken);\n
        t = nexttoken;\n
        advance(\'{\');\n
        nonadjacent(token, nexttoken);\n
        indent += option.indent;\n
        this.cases = [];\n
        for (;;) {\n
            switch (nexttoken.id) {\n
            case \'case\':\n
                switch (funct[\'(verb)\']) {\n
                case \'break\':\n
                case \'case\':\n
                case \'continue\':\n
                case \'return\':\n
                case \'switch\':\n
                case \'throw\':\n
                    break;\n
                default:\n
                    // You can tell JSHint that you don\'t use break intentionally by\n
                    // adding a comment /* falls through */ on a line just before\n
                    // the next `case`.\n
                    if (!ft.test(lines[nexttoken.line - 2])) {\n
                        warning(\n
                            "Expected a \'break\' statement before \'case\'.",\n
                            token);\n
                    }\n
                }\n
                indentation(-option.indent);\n
                advance(\'case\');\n
                this.cases.push(expression(20));\n
                g = true;\n
                advance(\':\');\n
                funct[\'(verb)\'] = \'case\';\n
                break;\n
            case \'default\':\n
                switch (funct[\'(verb)\']) {\n
                case \'break\':\n
                case \'continue\':\n
                case \'return\':\n
                case \'throw\':\n
                    break;\n
                default:\n
                    if (!ft.test(lines[nexttoken.line - 2])) {\n
                        warning(\n
                            "Expected a \'break\' statement before \'default\'.",\n
                            token);\n
                    }\n
                }\n
                indentation(-option.indent);\n
                advance(\'default\');\n
                g = true;\n
                advance(\':\');\n
                break;\n
            case \'}\':\n
                indent -= option.indent;\n
                indentation();\n
                advance(\'}\', t);\n
                if (this.cases.length === 1 || this.condition.id === \'true\' ||\n
                        this.condition.id === \'false\') {\n
                    if (!option.onecase)\n
                        warning("This \'switch\' should be an \'if\'.", this);\n
                }\n
                funct[\'(breakage)\'] -= 1;\n
                funct[\'(verb)\'] = undefined;\n
                return;\n
            case \'(end)\':\n
                error("Missing \'{a}\'.", nexttoken, \'}\');\n
                return;\n
            default:\n
                if (g) {\n
                    switch (token.id) {\n
                    case \',\':\n
                        error("Each value should have its own case label.");\n
                        return;\n
                    case \':\':\n
                        g = false;\n
                        statements();\n
                        break;\n
                    default:\n
                        error("Missing \':\' on a case clause.", token);\n
                        return;\n
                    }\n
                } else {\n
                    if (token.id === \':\') {\n
                        advance(\':\');\n
                        error("Unexpected \'{a}\'.", token, \':\');\n
                        statements();\n
                    } else {\n
                        error("Expected \'{a}\' and instead saw \'{b}\'.",\n
                            nexttoken, \'case\', nexttoken.value);\n
                        return;\n
                    }\n
                }\n
            }\n
        }\n
    }).labelled = true;\n
\n
    stmt(\'debugger\', function () {\n
        if (!option.debug) {\n
            warning("All \'debugger\' statements should be removed.");\n
        }\n
        return this;\n
    }).exps = true;\n
\n
    (function () {\n
        var x = stmt(\'do\', function () {\n
            funct[\'(breakage)\'] += 1;\n
            funct[\'(loopage)\'] += 1;\n
            this.first = block(true);\n
            advance(\'while\');\n
            var t = nexttoken;\n
            nonadjacent(token, t);\n
            advance(\'(\');\n
            nospace();\n
            expression(20);\n
            if (nexttoken.id === \'=\') {\n
                if (!option.boss)\n
                    warning("Expected a conditional expression and instead saw an assignment.");\n
                advance(\'=\');\n
                expression(20);\n
            }\n
            advance(\')\', t);\n
            nospace(prevtoken, token);\n
            funct[\'(breakage)\'] -= 1;\n
            funct[\'(loopage)\'] -= 1;\n
            return this;\n
        });\n
        x.labelled = true;\n
        x.exps = true;\n
    }());\n
\n
    blockstmt(\'for\', function () {\n
        var s, t = nexttoken;\n
        funct[\'(breakage)\'] += 1;\n
        funct[\'(loopage)\'] += 1;\n
        advance(\'(\');\n
        nonadjacent(this, t);\n
        nospace();\n
        if (peek(nexttoken.id === \'var\' ? 1 : 0).id === \'in\') {\n
            if (nexttoken.id === \'var\') {\n
                advance(\'var\');\n
                varstatement.fud.call(varstatement, true);\n
            } else {\n
                switch (funct[nexttoken.value]) {\n
                case \'unused\':\n
                    funct[nexttoken.value] = \'var\';\n
                    break;\n
                case \'var\':\n
                    break;\n
                default:\n
                    warning("Bad for in variable \'{a}\'.",\n
                            nexttoken, nexttoken.value);\n
                }\n
                advance();\n
            }\n
            advance(\'in\');\n
            expression(20);\n
            advance(\')\', t);\n
            s = block(true, true);\n
            if (option.forin && s && (s.length > 1 || typeof s[0] !== \'object\' ||\n
                    s[0].value !== \'if\')) {\n
                warning("The body of a for in should be wrapped in an if statement to filter " +\n
                        "unwanted properties from the prototype.", this);\n
            }\n
            funct[\'(breakage)\'] -= 1;\n
            funct[\'(loopage)\'] -= 1;\n
            return this;\n
        } else {\n
            if (nexttoken.id !== \';\') {\n
                if (nexttoken.id === \'var\') {\n
                    advance(\'var\');\n
                    varstatement.fud.call(varstatement);\n
                } else {\n
                    for (;;) {\n
                        expression(0, \'for\');\n
                        if (nexttoken.id !== \',\') {\n
                            break;\n
                        }\n
                        comma();\n
                    }\n
                }\n
            }\n
            nolinebreak(token);\n
            advance(\';\');\n
            if (nexttoken.id !== \';\') {\n
                expression(20);\n
                if (nexttoken.id === \'=\') {\n
                    if (!option.boss)\n
                        warning("Expected a conditional expression and instead saw an assignment.");\n
                    advance(\'=\');\n
                    expression(20);\n
                }\n
            }\n
            nolinebreak(token);\n
            advance(\';\');\n
            if (nexttoken.id === \';\') {\n
                error("Expected \'{a}\' and instead saw \'{b}\'.",\n
                        nexttoken, \')\', \';\');\n
            }\n
            if (nexttoken.id !== \')\') {\n
                for (;;) {\n
                    expression(0, \'for\');\n
                    if (nexttoken.id !== \',\') {\n
                        break;\n
                    }\n
                    comma();\n
                }\n
            }\n
            advance(\')\', t);\n
            nospace(prevtoken, token);\n
            block(true, true);\n
            funct[\'(breakage)\'] -= 1;\n
            funct[\'(loopage)\'] -= 1;\n
            return this;\n
        }\n
    }).labelled = true;\n
\n
\n
    stmt(\'break\', function () {\n
        var v = nexttoken.value;\n
\n
        if (funct[\'(breakage)\'] === 0)\n
            warning("Unexpected \'{a}\'.", nexttoken, this.value);\n
\n
        if (!option.asi)\n
            nolinebreak(this);\n
\n
        if (nexttoken.id !== \';\') {\n
            if (token.line === nexttoken.line) {\n
                if (funct[v] !== \'label\') {\n
                    warning("\'{a}\' is not a statement label.", nexttoken, v);\n
                } else if (scope[v] !== funct) {\n
                    warning("\'{a}\' is out of scope.", nexttoken, v);\n
                }\n
                this.first = nexttoken;\n
                advance();\n
            }\n
        }\n
        reachable(\'break\');\n
        return this;\n
    }).exps = true;\n
\n
\n
    stmt(\'continue\', function () {\n
        var v = nexttoken.value;\n
\n
        if (funct[\'(breakage)\'] === 0)\n
            warning("Unexpected \'{a}\'.", nexttoken, this.value);\n
\n
        if (!option.asi)\n
            nolinebreak(this);\n
\n
        if (nexttoken.id !== \';\') {\n
            if (token.line === nexttoken.line) {\n
                if (funct[v] !== \'label\') {\n
                    warning("\'{a}\' is not a statement label.", nexttoken, v);\n
                } else if (scope[v] !== funct) {\n
                    warning("\'{a}\' is out of scope.", nexttoken, v);\n
                }\n
                this.first = nexttoken;\n
                advance();\n
            }\n
        } else if (!funct[\'(loopage)\']) {\n
            warning("Unexpected \'{a}\'.", nexttoken, this.value);\n
        }\n
        reachable(\'continue\');\n
        return this;\n
    }).exps = true;\n
\n
\n
    stmt(\'return\', function () {\n
        if (this.line === nexttoken.line) {\n
            if (nexttoken.id === \'(regexp)\')\n
                warning("Wrap the /regexp/ literal in parens to disambiguate the slash operator.");\n
\n
            if (nexttoken.id !== \';\' && !nexttoken.reach) {\n
                nonadjacent(token, nexttoken);\n
                if (peek().value === "=" && !option.boss) {\n
                    warningAt("Did you mean to return a conditional instead of an assignment?",\n
                              token.line, token.character + 1);\n
                }\n
                this.first = expression(0);\n
            }\n
        } else if (!option.asi) {\n
            nolinebreak(this); // always warn (Line breaking error)\n
        }\n
        reachable(\'return\');\n
        return this;\n
    }).exps = true;\n
\n
\n
    stmt(\'throw\', function () {\n
        nolinebreak(this);\n
        nonadjacent(token, nexttoken);\n
        this.first = expression(20);\n
        reachable(\'throw\');\n
        return this;\n
    }).exps = true;\n
\n
//  Superfluous reserved words\n
\n
    reserve(\'class\');\n
    reserve(\'const\');\n
    reserve(\'enum\');\n
    reserve(\'export\');\n
    reserve(\'extends\');\n
    reserve(\'import\');\n
    reserve(\'super\');\n
\n
    reserve(\'let\');\n
    reserve(\'yield\');\n
    reserve(\'implements\');\n
    reserve(\'interface\');\n
    reserve(\'package\');\n
    reserve(\'private\');\n
    reserve(\'protected\');\n
    reserve(\'public\');\n
    reserve(\'static\');\n
\n
\n
// Parse JSON\n
\n
    function jsonValue() {\n
\n
        function jsonObject() {\n
            var o = {}, t = nexttoken;\n
            advance(\'{\');\n
            if (nexttoken.id !== \'}\') {\n
                for (;;) {\n
                    if (nexttoken.id === \'(end)\') {\n
                        error("Missing \'}\' to match \'{\' from line {a}.",\n
                                nexttoken, t.line);\n
                    } else if (nexttoken.id === \'}\') {\n
                        warning("Unexpected comma.", token);\n
                        break;\n
                    } else if (nexttoken.id === \',\') {\n
                        error("Unexpected comma.", nexttoken);\n
                    } else if (nexttoken.id !== \'(string)\') {\n
                        warning("Expected a string and instead saw {a}.",\n
                                nexttoken, nexttoken.value);\n
                    }\n
                    if (o[nexttoken.value] === true) {\n
                        warning("Duplicate key \'{a}\'.",\n
                                nexttoken, nexttoken.value);\n
                    } else if ((nexttoken.value === \'__proto__\' &&\n
                        !option.proto) || (nexttoken.value === \'__iterator__\' &&\n
                        !option.iterator)) {\n
                        warning("The \'{a}\' key may produce unexpected results.",\n
                            nexttoken, nexttoken.value);\n
                    } else {\n
                        o[nexttoken.value] = true;\n
                    }\n
                    advance();\n
                    advance(\':\');\n
                    jsonValue();\n
                    if (nexttoken.id !== \',\') {\n
                        break;\n
                    }\n
                    advance(\',\');\n
                }\n
            }\n
            advance(\'}\');\n
        }\n
\n
        function jsonArray() {\n
            var t = nexttoken;\n
            advance(\'[\');\n
            if (nexttoken.id !== \']\') {\n
                for (;;) {\n
                    if (nexttoken.id === \'(end)\') {\n
                        error("Missing \']\' to match \'[\' from line {a}.",\n
                                nexttoken, t.line);\n
                    } else if (nexttoken.id === \']\') {\n
                        warning("Unexpected comma.", token);\n
                        break;\n
                    } else if (nexttoken.id === \',\') {\n
                        error("Unexpected comma.", nexttoken);\n
                    }\n
                    jsonValue();\n
                    if (nexttoken.id !== \',\') {\n
                        break;\n
                    }\n
                    advance(\',\');\n
                }\n
            }\n
            advance(\']\');\n
        }\n
\n
        switch (nexttoken.id) {\n
        case \'{\':\n
            jsonObject();\n
            break;\n
        case \'[\':\n
            jsonArray();\n
            break;\n
        case \'true\':\n
        case \'false\':\n
        case \'null\':\n
        case \'(number)\':\n
        case \'(string)\':\n
            advance();\n
            break;\n
        case \'-\':\n
            advance(\'-\');\n
            if (token.character !== nexttoken.from) {\n
                warning("Unexpected space after \'-\'.", token);\n
            }\n
            adjacent(token, nexttoken);\n
            advance(\'(number)\');\n
            break;\n
        default:\n
            error("Expected a JSON value.", nexttoken);\n
        }\n
    }\n
\n
\n
// The actual JSHINT function itself.\n
\n
    var itself = function (s, o, g) {\n
        var a, i, k, x,\n
            optionKeys,\n
            newOptionObj = {};\n
\n
        JSHINT.errors = [];\n
        JSHINT.undefs = [];\n
        predefined = Object.create(standard);\n
        combine(predefined, g || {});\n
        if (o) {\n
            a = o.predef;\n
            if (a) {\n
                if (Array.isArray(a)) {\n
                    for (i = 0; i < a.length; i += 1) {\n
                        predefined[a[i]] = true;\n
                    }\n
                } else if (typeof a === \'object\') {\n
                    k = Object.keys(a);\n
                    for (i = 0; i < k.length; i += 1) {\n
                        predefined[k[i]] = !!a[k[i]];\n
                    }\n
                }\n
            }\n
            optionKeys = Object.keys(o);\n
            for (x = 0; x < optionKeys.length; x++) {\n
                newOptionObj[optionKeys[x]] = o[optionKeys[x]];\n
            }\n
        }\n
\n
        option = newOptionObj;\n
\n
        option.indent = option.indent || 4;\n
        option.maxerr = option.maxerr || 50;\n
\n
        tab = \'\';\n
        for (i = 0; i < option.indent; i += 1) {\n
            tab += \' \';\n
        }\n
        indent = 1;\n
        global = Object.create(predefined);\n
        scope = global;\n
        funct = {\n
            \'(global)\': true,\n
            \'(name)\': \'(global)\',\n
            \'(scope)\': scope,\n
            \'(breakage)\': 0,\n
            \'(loopage)\': 0\n
        };\n
        functions = [funct];\n
        urls = [];\n
        stack = null;\n
        member = {};\n
        membersOnly = null;\n
        implied = {};\n
        inblock = false;\n
        lookahead = [];\n
        jsonmode = false;\n
        warnings = 0;\n
        lex.init(s);\n
        prereg = true;\n
        directive = {};\n
\n
        prevtoken = token = nexttoken = syntax[\'(begin)\'];\n
\n
        // Check options\n
        for (var name in o) {\n
            if (is_own(o, name)) {\n
                checkOption(name, token);\n
            }\n
        }\n
\n
        assume();\n
\n
        // combine the passed globals after we\'ve assumed all our options\n
        combine(predefined, g || {});\n
\n
        //reset values\n
        comma.first = true;\n
\n
        try {\n
            advance();\n
            switch (nexttoken.id) {\n
            case \'{\':\n
            case \'[\':\n
                option.laxbreak = true;\n
                jsonmode = true;\n
                jsonValue();\n
                break;\n
            default:\n
                directives();\n
                if (directive["use strict"] && !option.globalstrict) {\n
                    warning("Use the function form of \\"use strict\\".", prevtoken);\n
                }\n
\n
                statements();\n
            }\n
            advance(\'(end)\');\n
\n
            var markDefined = function (name, context) {\n
                do {\n
                    if (typeof context[name] === \'string\') {\n
                        // JSHINT marks unused variables as \'unused\' and\n
                        // unused function declaration as \'unction\'. This\n
                        // code changes such instances back \'var\' and\n
                        // \'closure\' so that the code in JSHINT.data()\n
                        // doesn\'t think they\'re unused.\n
\n
                        if (context[name] === \'unused\')\n
                            context[name] = \'var\';\n
                        else if (context[name] === \'unction\')\n
                            context[name] = \'closure\';\n
\n
                        return true;\n
                    }\n
\n
                    context = context[\'(context)\'];\n
                } while (context);\n
\n
                return false;\n
            };\n
\n
            var clearImplied = function (name, line) {\n
                if (!implied[name])\n
                    return;\n
\n
                var newImplied = [];\n
                for (var i = 0; i < implied[name].length; i += 1) {\n
                    if (implied[name][i] !== line)\n
                        newImplied.push(implied[name][i]);\n
                }\n
\n
                if (newImplied.length === 0)\n
                    delete implied[name];\n
                else\n
                    implied[name] = newImplied;\n
            };\n
\n
            // Check queued \'x is not defined\' instances to see if they\'re still undefined.\n
            for (i = 0; i < JSHINT.undefs.length; i += 1) {\n
                k = JSHINT.undefs[i].slice(0);\n
\n
                if (markDefined(k[2].value, k[0])) {\n
                    clearImplied(k[2].value, k[2].line);\n
                } else {\n
                    warning.apply(warning, k.slice(1));\n
                }\n
            }\n
        } catch (e) {\n
            if (e) {\n
                var nt = nexttoken || {};\n
                JSHINT.errors.push({\n
                    raw       : e.raw,\n
                    reason    : e.message,\n
                    line      : e.line || nt.line,\n
                    character : e.character || nt.from\n
                }, null);\n
            }\n
        }\n
\n
        return JSHINT.errors.length === 0;\n
    };\n
\n
    // Data summary.\n
    itself.data = function () {\n
\n
        var data = { functions: [], options: option }, fu, globals, implieds = [], f, i, j,\n
            members = [], n, unused = [], v;\n
        if (itself.errors.length) {\n
            data.errors = itself.errors;\n
        }\n
\n
        if (jsonmode) {\n
            data.json = true;\n
        }\n
\n
        for (n in implied) {\n
            if (is_own(implied, n)) {\n
                implieds.push({\n
                    name: n,\n
                    line: implied[n]\n
                });\n
            }\n
        }\n
        if (implieds.length > 0) {\n
            data.implieds = implieds;\n
        }\n
\n
        if (urls.length > 0) {\n
            data.urls = urls;\n
        }\n
\n
        globals = Object.keys(scope);\n
        if (globals.length > 0) {\n
            data.globals = globals;\n
        }\n
        for (i = 1; i < functions.length; i += 1) {\n
            f = functions[i];\n
            fu = {};\n
            for (j = 0; j < functionicity.length; j += 1) {\n
                fu[functionicity[j]] = [];\n
            }\n
            for (n in f) {\n
                if (is_own(f, n) && n.charAt(0) !== \'(\') {\n
                    v = f[n];\n
                    if (v === \'unction\') {\n
                        v = \'unused\';\n
                    }\n
                    if (Array.isArray(fu[v])) {\n
                        fu[v].push(n);\n
                        if (v === \'unused\') {\n
                            unused.push({\n
                                name: n,\n
                                line: f[\'(line)\'],\n
                                \'function\': f[\'(name)\']\n
                            });\n
                        }\n
                    }\n
                }\n
            }\n
            for (j = 0; j < functionicity.length; j += 1) {\n
                if (fu[functionicity[j]].length === 0) {\n
                    delete fu[functionicity[j]];\n
                }\n
            }\n
            fu.name = f[\'(name)\'];\n
            fu.param = f[\'(params)\'];\n
            fu.line = f[\'(line)\'];\n
            fu.last = f[\'(last)\'];\n
            data.functions.push(fu);\n
        }\n
\n
        if (unused.length > 0) {\n
            data.unused = unused;\n
        }\n
\n
        members = [];\n
        for (n in member) {\n
            if (typeof member[n] === \'number\') {\n
                data.member = member;\n
                break;\n
            }\n
        }\n
\n
        return data;\n
    };\n
\n
    itself.report = function (option) {\n
        var data = itself.data();\n
\n
        var a = [], c, e, err, f, i, k, l, m = \'\', n, o = [], s;\n
\n
        function detail(h, array) {\n
            var b, i, singularity;\n
            if (array) {\n
                o.push(\'<div><i>\' + h + \'</i> \');\n
                array = array.sort();\n
                for (i = 0; i < array.length; i += 1) {\n
                    if (array[i] !== singularity) {\n
                        singularity = array[i];\n
                        o.push((b ? \', \' : \'\') + singularity);\n
                        b = true;\n
                    }\n
                }\n
                o.push(\'</div>\');\n
            }\n
        }\n
\n
\n
        if (data.errors || data.implieds || data.unused) {\n
            err = true;\n
            o.push(\'<div id=errors><i>Error:</i>\');\n
            if (data.errors) {\n
                for (i = 0; i < data.errors.length; i += 1) {\n
                    c = data.errors[i];\n
                    if (c) {\n
                        e = c.evidence || \'\';\n
                        o.push(\'<p>Problem\' + (isFinite(c.line) ? \' at line \' +\n
                                c.line + \' character \' + c.character : \'\') +\n
                                \': \' + c.reason.entityify() +\n
                                \'</p><p class=evidence>\' +\n
                                (e && (e.length > 80 ? e.slice(0, 77) + \'...\' :\n
                                e).entityify()) + \'</p>\');\n
                    }\n
                }\n
            }\n
\n
            if (data.implieds) {\n
                s = [];\n
                for (i = 0; i < data.implieds.length; i += 1) {\n
                    s[i] = \'<code>\' + data.implieds[i].name + \'</code>&nbsp;<i>\' +\n
                        data.implieds[i].line + \'</i>\';\n
                }\n
                o.push(\'<p><i>Implied global:</i> \' + s.join(\', \') + \'</p>\');\n
            }\n
\n
            if (data.unused) {\n
                s = [];\n
                for (i = 0; i < data.unused.length; i += 1) {\n
                    s[i] = \'<code><u>\' + data.unused[i].name + \'</u></code>&nbsp;<i>\' +\n
                        data.unused[i].line + \'</i> <code>\' +\n
                        data.unused[i][\'function\'] + \'</code>\';\n
                }\n
                o.push(\'<p><i>Unused variable:</i> \' + s.join(\', \') + \'</p>\');\n
            }\n
            if (data.json) {\n
                o.push(\'<p>JSON: bad.</p>\');\n
            }\n
            o.push(\'</div>\');\n
        }\n
\n
        if (!option) {\n
\n
            o.push(\'<br><div id=functions>\');\n
\n
            if (data.urls) {\n
                detail("URLs<br>", data.urls, \'<br>\');\n
            }\n
\n
            if (data.json && !err) {\n
                o.push(\'<p>JSON: good.</p>\');\n
            } else if (data.globals) {\n
                o.push(\'<div><i>Global</i> \' +\n
                        data.globals.sort().join(\', \') + \'</div>\');\n
            } else {\n
                o.push(\'<div><i>No new global variables introduced.</i></div>\');\n
            }\n
\n
            for (i = 0; i < data.functions.length; i += 1) {\n
                f = data.functions[i];\n
\n
                o.push(\'<br><div class=function><i>\' + f.line + \'-\' +\n
                        f.last + \'</i> \' + (f.name || \'\') + \'(\' +\n
                        (f.param ? f.param.join(\', \') : \'\') + \')</div>\');\n
                detail(\'<big><b>Unused</b></big>\', f.unused);\n
                detail(\'Closure\', f.closure);\n
                detail(\'Variable\', f[\'var\']);\n
                detail(\'Exception\', f.exception);\n
                detail(\'Outer\', f.outer);\n
                detail(\'Global\', f.global);\n
                detail(\'Label\', f.label);\n
            }\n
\n
            if (data.member) {\n
                a = Object.keys(data.member);\n
                if (a.length) {\n
                    a = a.sort();\n
                    m = \'<br><pre id=members>/*members \';\n
                    l = 10;\n
                    for (i = 0; i < a.length; i += 1) {\n
                        k = a[i];\n
                        n = k.name();\n
                        if (l + n.length > 72) {\n
                            o.push(m + \'<br>\');\n
                            m = \'    \';\n
                            l = 1;\n
                        }\n
                        l += n.length + 2;\n
                        if (data.member[k] === 1) {\n
                            n = \'<i>\' + n + \'</i>\';\n
                        }\n
                        if (i < a.length - 1) {\n
                            n += \', \';\n
                        }\n
                        m += n;\n
                    }\n
                    o.push(m + \'<br>*/</pre>\');\n
                }\n
                o.push(\'</div>\');\n
            }\n
        }\n
        return o.join(\'\');\n
    };\n
\n
    itself.jshint = itself;\n
\n
    return itself;\n
}());\n
\n
// Make JSHINT a Node module, if possible.\n
if (typeof exports === \'object\' && exports)\n
    exports.JSHINT = JSHINT;\n


]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <none/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
