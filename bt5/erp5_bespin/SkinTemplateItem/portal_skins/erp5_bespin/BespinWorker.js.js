<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="DTMLMethod" module="OFS.DTMLMethod"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>BespinWorker.js</string> </value>
        </item>
        <item>
            <key> <string>_vars</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>globals</string> </key>
            <value>
              <dictionary/>
            </value>
        </item>
        <item>
            <key> <string>raw</string> </key>
            <value> <string encoding="cdata"><![CDATA[

;bespin.tiki.register("::python", {\n
    name: "python",\n
    dependencies: { "syntax_manager": "0.0.0" }\n
});\n
bespin.tiki.module("python:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *  Scott Ellis (mail@scottellis.com.au)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "Python syntax highlighter",\n
    "dependencies": { "syntax_manager": "0.0.0" },\n
    "environments": { "worker": true },\n
    "provides": [\n
        {\n
            "ep": "syntax",\n
            "name": "py",\n
            "pointer": "#PySyntax",\n
            "fileexts": [ "py" ]\n
        }\n
    ]\n
});\n
"end";\n
\n
//var SC = require(\'sproutcore/runtime\').SC;\n
//var Promise = require(\'bespin:promise\').Promise;\n
//var StandardSyntax = require(\'syntax_manager:controllers/standardsyntax\').StandardSyntax;\n
var StandardSyntax = require(\'standard_syntax\').StandardSyntax;\n
\n
var states = {\n
  start: [\n
      {\n
\t  regex:  /^(?:and|as|assert|break|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|not|or|pass|print|raise|return|try|while|with|yield)(?![a-zA-Z0-9_])/,\n
\t  tag:    \'keyword\'\n
      },\n
      {\n
\t  regex:  /^[A-Za-z_][A-Za-z0-9_]*/,\n
\t  tag:    \'identifier\'\n
      },\n
      {\n
\t  regex:  /^[^\'"#\\/ \\tA-Za-z0-9_]+/,\n
\t  tag:    \'plain\'\n
      },\n
      {\n
\t  regex:  /^[ \\t]+/,\n
\t  tag:    \'plain\'\n
      },\n
      {\n
\t  regex:  /^"""/,\n
\t  tag:    \'string\',\n
\t  then:   \'qqqstring\'\n
      },\n
      {\n
\t  regex:  /^\'/,\n
\t  tag:    \'string\',\n
\t  then:   \'qstring\'\n
      },\n
      {\n
\t  regex:  /^"/,\n
\t  tag:    \'string\',\n
\t  then:   \'qqstring\'\n
      },\n
      {\n
\t  regex:  /^#.*/,\n
\t  tag:    \'comment\'\n
      },\n
      {\n
\t  regex:  /^./,\n
\t  tag:    \'plain\'\n
      }\n
  ],\n
\n
  qstring: [\n
      {\n
\t  regex:  /^\'/,\n
\t  tag:    \'string\',\n
\t  then:   \'start\'\n
      },\n
      {\n
\t  regex:  /^(?:\\\\.|[^\'\\\\])+/,\n
\t  tag:    \'string\'\n
      }\n
  ],\n
\n
  qqstring: [\n
      {\n
\t  regex:  /^"/,\n
\t  tag:    \'string\',\n
\t  then:   \'start\'\n
      },\n
      {\n
\t  regex:  /^(?:\\\\.|[^"\\\\])+/,\n
\t  tag:    \'string\'\n
      }\n
  ],\n
\n
  qqqstring: [\n
      {\n
\t  regex:  /^"""/,\n
\t  tag:    \'string\',\n
\t  then:   \'start\'\n
      },\n
      {\n
\t  regex:  /^./,\n
\t  tag:    \'string\'\n
      }\n
  ]\n
\n
};\n
\n
exports.PySyntax = new StandardSyntax(states);\n
\n
\n
\n
});\n
;bespin.tiki.register("::syntax_worker", {\n
    name: "syntax_worker",\n
    dependencies: { "syntax_directory": "0.0.0", "underscore": "0.0.0" }\n
});\n
bespin.tiki.module("syntax_worker:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "Coordinates multiple syntax engines",\n
    "environments": { "worker": true },\n
    "dependencies": { "syntax_directory": "0.0.0", "underscore": "0.0.0" }\n
});\n
"end";\n
\n
var promise = require(\'bespin:promise\');\n
var _ = require(\'underscore\')._;\n
var console = require(\'bespin:console\').console;\n
var syntaxDirectory = require(\'syntax_directory\').syntaxDirectory;\n
\n
var syntaxWorker = {\n
    engines: {},\n
\n
    annotate: function(state, lines, range) {\n
        function splitParts(str) { return str.split(":"); }\n
        function saveState() {\n
            states.push(_(stateStack).invoke(\'join\', ":").join(" "));\n
        }\n
\n
        var engines = this.engines;\n
        var states = [], attrs = [], symbols = [];\n
        var stateStack = _(state.split(" ")).map(splitParts);\n
\n
        _(lines).each(function(line, offset) {\n
            saveState();\n
\n
            var lineAttrs = [], lineSymbols = {};\n
            var col = 0;\n
            while (col < line.length) {\n
                // Check for the terminator string.\n
                // FIXME: This is wrong. It should check *inside* the token\n
                // that was just parsed as well.\n
                var curState;\n
                while (true) {\n
                    curState = _(stateStack).last();\n
                    if (curState.length < 3) {\n
                        break;\n
                    }\n
\n
                    var term = curState[2];\n
                    if (line.substring(col, col + term.length) !== term) {\n
                        break;\n
                    }\n
\n
                    stateStack.pop();\n
                }\n
\n
                var context = curState[0];\n
                var result = engines[context].get(curState, line, col);\n
                var token;\n
                if (result == null) {\n
                    token = {\n
                        state: \'plain\',\n
                        tag: \'plain\',\n
                        start: col,\n
                        end: line.length\n
                    };\n
                } else {\n
                    stateStack[stateStack.length - 1] = result.state;\n
                    if (result.hasOwnProperty(\'newContext\')) {\n
                        stateStack.push(result.newContext);\n
                    }\n
\n
                    token = result.token;\n
\n
                    var sym = result.symbol;\n
                    if (sym != null) {\n
                        lineSymbols["-" + sym[0]] = sym[1];\n
                    }\n
                }\n
\n
                lineAttrs.push(token);\n
                col = token.end;\n
            }\n
\n
            attrs.push(lineAttrs);\n
            symbols.push(lineSymbols);\n
        });\n
\n
        saveState();\n
\n
        return { states: states, attrs: attrs, symbols: symbols };\n
    },\n
\n
    loadSyntax: function(syntaxName) {\n
        var pr = new promise.Promise;\n
\n
        var engines = this.engines;\n
        if (engines.hasOwnProperty(syntaxName)) {\n
            pr.resolve();\n
            return pr;\n
        }\n
\n
        var info = syntaxDirectory.get(syntaxName);\n
        if (info == null) {\n
            throw new Error(\'No syntax engine installed for syntax "\' +\n
                syntaxName + \'".\');\n
        }\n
\n
        info.extension.load().then(function(engine) {\n
            engines[syntaxName] = engine;\n
\n
            var subsyntaxes = engine.subsyntaxes;\n
            if (subsyntaxes == null) {\n
                pr.resolve();\n
                return;\n
            }\n
\n
            var pr2 = promise.group(_(subsyntaxes).map(this.loadSyntax, this));\n
            pr2.then(_(pr.resolve).bind(pr));\n
        }.bind(this));\n
\n
        return pr;\n
    }\n
};\n
\n
exports.syntaxWorker = syntaxWorker;\n
\n
\n
});\n
;bespin.tiki.register("::stylesheet", {\n
    name: "stylesheet",\n
    dependencies: { "standard_syntax": "0.0.0" }\n
});\n
bespin.tiki.module("stylesheet:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "CSS syntax highlighter",\n
    "dependencies": {\n
        "standard_syntax": "0.0.0"\n
    },\n
    "environments": {\n
        "worker": true\n
    },\n
    "provides": [\n
        {\n
            "ep": "syntax",\n
            "name": "css",\n
            "pointer": "#CSSSyntax",\n
            "fileexts": [ "css", "less" ]\n
        }\n
    ]\n
});\n
"end";\n
\n
var Promise = require(\'bespin:promise\').Promise;\n
var StandardSyntax = require(\'standard_syntax\').StandardSyntax;\n
\n
var COMMENT_REGEXP = {\n
    regex:  /^\\/\\/.*/,\n
    tag:    \'comment\'\n
};\n
\n
var createCommentState = function(jumpBackState) {\n
    return [\n
        {\n
            regex:  /^[^*\\/]+/,\n
            tag:    \'comment\'\n
        },\n
        {\n
            regex:  /^\\*\\//,\n
            tag:    \'comment\',\n
            then:   jumpBackState\n
        },\n
        {\n
            regex:  /^[*\\/]/,\n
            tag:    \'comment\'\n
        }\n
    ];\n
};\n
\n
var states = {\n
    start: [\n
        {\n
            //style names\n
            regex:  /^([a-zA-Z-\\s]*)(?:\\:)/,\n
            tag:    \'identifier\',\n
            then:   \'style\'\n
        },\n
        {\n
            //tags\n
            regex:  /^([\\w]+)(?![a-zA-Z0-9_:])([,|{]*?)(?!;)(?!(;|%))/,\n
            tag:    \'keyword\',\n
            then:   \'header\'\n
        },\n
        {\n
            //id\n
            regex:  /^#([a-zA-Z]*)(?=.*{*?)/,\n
            tag:    \'keyword\',\n
            then:   \'header\'\n
        },\n
        {\n
            //classes\n
            regex:  /^\\.([a-zA-Z]*)(?=.*{*?)/,\n
            tag:    \'keyword\',\n
            then:   \'header\'\n
        },\n
            COMMENT_REGEXP,\n
        {\n
            regex:  /^\\/\\*/,\n
            tag:    \'comment\',\n
            then:   \'comment\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'plain\'\n
        }\n
    ],\n
\n
    header: [\n
        {\n
            regex:  /^[^{|\\/\\/|\\/\\*]*/,\n
            tag:    \'keyword\',\n
            then:   \'start\'\n
        },\n
            COMMENT_REGEXP,\n
        {\n
            regex:  /^\\/\\*/,\n
            tag:    \'comment\',\n
            then:   \'comment_header\'\n
        }\n
    ],\n
\n
    style: [\n
        {\n
            regex:  /^[^;|}|\\/\\/|\\/\\*]+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^;|}/,\n
            tag:    \'plain\',\n
            then:   \'start\'\n
        },\n
            COMMENT_REGEXP,\n
        {\n
            regex:  /^\\/\\*/,\n
            tag:    \'comment\',\n
            then:   \'comment_style\'\n
        }\n
    ],\n
\n
    comment:        createCommentState(\'start\'),\n
    comment_header: createCommentState(\'header\'),\n
    comment_style:  createCommentState(\'style\')\n
};\n
\n
exports.CSSSyntax = new StandardSyntax(states);\n
\n
});\n
;bespin.tiki.register("::html", {\n
    name: "html",\n
    dependencies: { "standard_syntax": "0.0.0" }\n
});\n
bespin.tiki.module("html:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "HTML syntax highlighter",\n
    "dependencies": { "standard_syntax": "0.0.0" },\n
    "environments": { "worker": true },\n
    "provides": [\n
        {\n
            "ep": "syntax",\n
            "name": "html",\n
            "pointer": "#HTMLSyntax",\n
            "fileexts": [ "htm", "html" ]\n
        }\n
    ]\n
});\n
"end";\n
\n
var StandardSyntax = require(\'standard_syntax\').StandardSyntax;\n
\n
var states = {};\n
\n
//\n
// This parser is modeled on the WHATWG HTML 5 specification, with some\n
// simplifications to improve performance. See the relevant spec here:\n
//\n
//     http://www.whatwg.org/specs/web-apps/current-work/\n
//\n
\n
var createTagStates = function(prefix, interiorActions) {\n
    states[prefix + \'_beforeAttrName\'] = [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   prefix + \'_selfClosingStartTag\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'keyword\',\n
            then:   prefix + \'_attrName\'\n
        }\n
    ];\n
\n
    // 10.2.4.35 Attribute name state\n
    states[prefix + \'_attrName\'] = [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\',\n
            then:   prefix + \'_afterAttrName\'\n
        },\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   prefix + \'_selfClosingStartTag\'\n
        },\n
        {\n
            regex:  /^=/,\n
            tag:    \'operator\',\n
            then:   prefix + \'_beforeAttrValue\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /^["\'<]+/,\n
            tag:    \'error\'\n
        },\n
        {\n
            regex:  /^[^ \\t\\n\\/=>"\'<]+/,\n
            tag:    \'keyword\'\n
        }\n
    ];\n
\n
    states[prefix + \'_afterAttrName\'] = [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   prefix + \'_selfClosingStartTag\'\n
        },\n
        {\n
            regex:  /^=/,\n
            tag:    \'operator\',\n
            then:   prefix + \'_beforeAttrValue\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'keyword\',\n
            then:   prefix + \'_attrName\'\n
        }\n
    ];\n
\n
    states[prefix + \'_beforeAttrValue\'] = [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   prefix + \'_attrValueQQ\'\n
        },\n
        {\n
            regex:  /^(?=&)/,\n
            tag:    \'plain\',\n
            then:   prefix + \'_attrValueU\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   prefix + \'_attrValueQ\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'string\',\n
            then:   prefix + \'_attrValueU\'\n
        }\n
    ];\n
\n
    states[prefix + \'_attrValueQQ\'] = [\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   prefix + \'_afterAttrValueQ\'\n
        },\n
        {\n
            regex:  /^[^"]+/,\n
            tag:    \'string\'\n
        }\n
    ];\n
\n
    states[prefix + \'_attrValueQ\'] = [\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   prefix + \'_afterAttrValueQ\'\n
        },\n
        {\n
            regex:  /^[^\']+/,\n
            tag:    \'string\'\n
        }\n
    ];\n
\n
    states[prefix + \'_attrValueU\'] = [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'string\',\n
            then:   prefix + \'_beforeAttrName\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /[^ \\t\\n>]+/,\n
            tag:    \'string\'\n
        }\n
    ];\n
\n
    states[prefix + \'_afterAttrValueQ\'] = [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'plain\',\n
            then:   prefix + \'_beforeAttrName\'\n
        },\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   prefix + \'_selfClosingStartTag\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   interiorActions\n
        },\n
        {\n
            regex:  /^(?=.)/,\n
            tag:    \'operator\',\n
            then:   prefix + \'_beforeAttrName\'\n
        }\n
    ];\n
\n
    // 10.2.4.43 Self-closing start tag state\n
    states[prefix + \'_selfClosingStartTag\'] = [\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   prefix + \'_beforeAttrName\'\n
        }\n
    ];\n
};\n
\n
states = {\n
    // 10.2.4.1 Data state\n
    start: [\n
        {\n
            regex:  /^[^<]+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^<!--/,\n
            tag:    \'comment\',\n
            then:   \'commentStart\'\n
        },\n
        {\n
            regex:  /^<!/,\n
            tag:    \'directive\',\n
            then:   \'markupDeclarationOpen\'\n
        },\n
        {\n
            regex:  /^<\\?/,\n
            tag:    \'comment\',\n
            then:   \'bogusComment\'\n
        },\n
        {\n
            regex:  /^</,\n
            tag:    \'operator\',\n
            then:   \'tagOpen\'\n
        }\n
    ],\n
\n
    // 10.2.4.8 Tag open state\n
    tagOpen: [\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   \'endTagOpen\'\n
        },\n
        {\n
            regex:  /^script/i,\n
            tag:    \'keyword\',\n
            then:   \'script_beforeAttrName\'\n
        },\n
        {\n
            regex:  /^[a-zA-Z]/,\n
            tag:    \'keyword\',\n
            then:   \'tagName\'\n
        },\n
        {\n
            regex:  /^(?=.)/,\n
            tag:    \'plain\',\n
            then:   \'start\'\n
        }\n
    ],\n
\n
    // 10.2.4.6 Script data state\n
    scriptData: [\n
        {\n
            regex:  /^<(?=\\/script>)/i,\n
            tag:    \'operator\',\n
            then:   \'tagOpen\'\n
        },\n
        {\n
            regex:  /^[^<]+/,\n
            tag:    \'plain\'\n
        }\n
    ],\n
\n
    // 10.2.4.9 End tag open state\n
    endTagOpen: [\n
        {\n
            regex:  /^[a-zA-Z]/,\n
            tag:    \'keyword\',\n
            then:   \'tagName\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusComment\'\n
        }\n
    ],\n
\n
    // 10.2.4.10 Tag name state\n
    tagName: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\',\n
            then:   \'normal_beforeAttrName\'\n
        },\n
        {\n
            regex:  /^\\//,\n
            tag:    \'operator\',\n
            then:   \'normal_selfClosingStartTag\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'operator\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^ \\t\\n\\/>]+/,\n
            tag:    \'keyword\'\n
        }\n
    ],\n
\n
    // 10.2.4.44 Bogus comment state\n
    bogusComment: [\n
        {\n
            regex:  /^[^>]+/,\n
            tag:    \'comment\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'comment\',\n
            then:   \'start\'\n
        }\n
    ],\n
\n
    // 10.2.4.45 Markup declaration open state\n
    markupDeclarationOpen: [\n
        {\n
            regex:  /^doctype/i,\n
            tag:    \'directive\',\n
            then:   \'doctype\'\n
        },\n
        {\n
            regex:  /^(?=.)/,\n
            tag:    \'comment\',\n
            then:   \'bogusComment\'\n
        }\n
    ],\n
\n
    // 10.2.4.46 Comment start state\n
    commentStart: [\n
        {\n
            regex:  /^-->/,\n
            tag:    \'comment\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^-]+/,\n
            tag:    \'comment\'\n
        }\n
    ],\n
\n
    // 10.2.4.53 DOCTYPE state\n
    doctype: [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'plain\',\n
            then:   \'beforeDoctypeName\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'beforeDoctypeName\'\n
        }\n
    ],\n
\n
    // 10.2.4.54 Before DOCTYPE name state\n
    beforeDoctypeName: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'directive\',\n
            then:   \'doctypeName\'\n
        }\n
    ],\n
\n
    // 10.2.4.55 DOCTYPE name state\n
    doctypeName: [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'plain\',\n
            then:   \'afterDoctypeName\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^ \\t\\n>]+/,\n
            tag:    \'directive\'\n
        }\n
    ],\n
\n
    // 10.2.4.56 After DOCTYPE name state\n
    afterDoctypeName: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'directive\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^public/i,\n
            tag:    \'directive\',\n
            then:   \'afterDoctypePublicKeyword\'\n
        },\n
        {\n
            regex:  /^system/i,\n
            tag:    \'directive\',\n
            then:   \'afterDoctypeSystemKeyword\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.57 After DOCTYPE public keyword state\n
    afterDoctypePublicKeyword: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\',\n
            then:   \'beforeDoctypePublicId\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'error\',\n
            then:   \'doctypePublicIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'error\',\n
            then:   \'doctypePublicIdQ\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.58 Before DOCTYPE public identifier\n
    beforeDoctypePublicId: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   \'doctypePublicIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   \'doctypePublicIdQ\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.59 DOCTYPE public identifier (double-quoted) state\n
    doctypePublicIdQQ: [\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   \'afterDoctypePublicId\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^>"]+/,\n
            tag:    \'string\'\n
        }\n
    ],\n
\n
    // 10.2.4.60 DOCTYPE public identifier (single-quoted) state\n
    doctypePublicIdQ: [\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   \'afterDoctypePublicId\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^>\']+/,\n
            tag:    \'string\'\n
        }\n
    ],\n
\n
    // 10.2.4.61 After DOCTYPE public identifier state\n
    afterDoctypePublicId: [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'plain\',\n
            then:   \'betweenDoctypePublicAndSystemIds\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'error\',\n
            then:   \'doctypeSystemIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'error\',\n
            then:   \'doctypeSystemIdQ\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.62 Between DOCTYPE public and system identifiers state\n
    betweenDoctypePublicAndSystemIds: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\',\n
            then:   \'betweenDoctypePublicAndSystemIds\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   \'doctypeSystemIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   \'doctypeSystemIdQ\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.63 After DOCTYPE system keyword state\n
    afterDoctypeSystemKeyword: [\n
        {\n
            regex:  /^\\s/,\n
            tag:    \'plain\',\n
            then:   \'beforeDoctypeSystemId\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'error\',\n
            then:   \'doctypeSystemIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'error\',\n
            then:   \'doctypeSystemIdQ\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.64 Before DOCTYPE system identifier state\n
    beforeDoctypeSystemId: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\',\n
            then:   \'beforeDoctypeSystemId\'\n
        },\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   \'doctypeSystemIdQQ\'\n
        },\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   \'doctypeSystemIdQ\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.65 DOCTYPE system identifier (double-quoted) state\n
    doctypeSystemIdQQ: [\n
        {\n
            regex:  /^"/,\n
            tag:    \'string\',\n
            then:   \'afterDoctypeSystemId\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^">]+/,\n
            tag:    \'string\'\n
        }\n
    ],\n
\n
    // 10.2.4.66 DOCTYPE system identifier (single-quoted) state\n
    doctypeSystemIdQ: [\n
        {\n
            regex:  /^\'/,\n
            tag:    \'string\',\n
            then:   \'afterDoctypeSystemId\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'error\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^\'>]+/,\n
            tag:    \'string\'\n
        }\n
    ],\n
\n
    // 10.2.4.67 After DOCTYPE system identifier state\n
    afterDoctypeSystemId: [\n
        {\n
            regex:  /^\\s+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'error\',\n
            then:   \'bogusDoctype\'\n
        }\n
    ],\n
\n
    // 10.2.4.68 Bogus DOCTYPE state\n
    bogusDoctype: [\n
        {\n
            regex:  /^>/,\n
            tag:    \'directive\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[^>]+/,\n
            tag:    \'directive\'\n
        }\n
    ]\n
};\n
\n
createTagStates(\'normal\', \'start\');\n
createTagStates(\'script\', \'start js:start:</script>\');\n
\n
/**\n
 * This syntax engine exposes an HTML parser modeled on the WHATWG HTML 5\n
 * specification.\n
 */\n
exports.HTMLSyntax = new StandardSyntax(states, [ \'js\' ]);\n
\n
\n
});\n
;bespin.tiki.register("::js_syntax", {\n
    name: "js_syntax",\n
    dependencies: { "standard_syntax": "0.0.0" }\n
});\n
bespin.tiki.module("js_syntax:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "JavaScript syntax highlighter",\n
    "dependencies": { "standard_syntax": "0.0.0" },\n
    "environments": { "worker": true },\n
    "provides": [\n
        {\n
            "ep": "syntax",\n
            "name": "js",\n
            "pointer": "#JSSyntax",\n
            "fileexts": [ "js", "json" ]\n
        }\n
    ]\n
});\n
"end";\n
\n
var StandardSyntax = require(\'standard_syntax\').StandardSyntax;\n
\n
var states = {\n
    start: [\n
        {\n
            regex:  /^var(?=\\s*([A-Za-z_$][A-Za-z0-9_$]*)\\s*=\\s*require\\s*\\(\\s*[\'"]([^\'"]*)[\'"]\\s*\\)\\s*[;,])/,\n
            tag:    \'keyword\',\n
            symbol: \'$1:$2\'\n
        },\n
        {\n
            regex:  /^(?:break|case|catch|continue|default|delete|do|else|false|finally|for|function|if|in|instanceof|let|new|null|return|switch|this|throw|true|try|typeof|var|void|while|with)(?![a-zA-Z0-9_])/,\n
            tag:    \'keyword\'\n
        },\n
        {\n
            regex:  /^[A-Za-z_][A-Za-z0-9_]*/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^[^\'"\\/ \\tA-Za-z0-9_]+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^[ \\t]+/,\n
            tag:    \'plain\'\n
        },\n
        {\n
            regex:  /^\'(?=.)/,\n
            tag:    \'string\',\n
            then:   \'qstring\'\n
        },\n
        {\n
            regex:  /^"(?=.)/,\n
            tag:    \'string\',\n
            then:   \'qqstring\'\n
        },\n
        {\n
            regex:  /^\\/\\/.*/,\n
            tag:    \'comment\'\n
        },\n
        {\n
            regex:  /^\\/\\*/,\n
            tag:    \'comment\',\n
            then:   \'comment\'\n
        },\n
        {\n
            regex:  /^./,\n
            tag:    \'plain\'\n
        }\n
    ],\n
\n
    qstring: [\n
        {\n
            regex:  /^(?:\\\\.|[^\'\\\\])*\'?/,\n
            tag:    \'string\',\n
            then:   \'start\'\n
        }\n
    ],\n
\n
    qqstring: [\n
        {\n
            regex:  /^(?:\\\\.|[^"\\\\])*"?/,\n
            tag:    \'string\',\n
            then:   \'start\'\n
        }\n
    ],\n
\n
    comment: [\n
        {\n
            regex:  /^[^*\\/]+/,\n
            tag:    \'comment\'\n
        },\n
        {\n
            regex:  /^\\*\\//,\n
            tag:    \'comment\',\n
            then:   \'start\'\n
        },\n
        {\n
            regex:  /^[*\\/]/,\n
            tag:    \'comment\'\n
        }\n
    ]\n
};\n
\n
exports.JSSyntax = new StandardSyntax(states);\n
\n
});\n
;bespin.tiki.register("::standard_syntax", {\n
    name: "standard_syntax",\n
    dependencies: { "syntax_worker": "0.0.0", "syntax_directory": "0.0.0", "underscore": "0.0.0" }\n
});\n
bespin.tiki.module("standard_syntax:index",function(require,exports,module) {\n
/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
"define metadata";\n
({\n
    "description": "Easy-to-use basis for syntax engines",\n
    "environments": { "worker": true },\n
    "dependencies": { \n
        "syntax_directory": "0.0.0", \n
        "underscore": "0.0.0",\n
        "syntax_worker": "0.0.0"\n
    }\n
});\n
"end";\n
\n
var promise = require(\'bespin:promise\');\n
var _ = require(\'underscore\')._;\n
var console = require(\'bespin:console\').console;\n
var syntaxDirectory = require(\'syntax_directory\').syntaxDirectory;\n
\n
exports.StandardSyntax = function(states, subsyntaxes) {\n
    this.states = states;\n
    this.subsyntaxes = subsyntaxes;\n
};\n
\n
/** This syntax controller exposes a simple regex- and line-based parser. */\n
exports.StandardSyntax.prototype = {\n
    get: function(fullState, line, col) {\n
        var context = fullState[0], state = fullState[1];\n
\n
        if (!this.states.hasOwnProperty(state)) {\n
            throw new Error(\'StandardSyntax: no such state "\' + state + \'"\');\n
        }\n
\n
        var str = line.substring(col);  // TODO: sticky flag where available\n
        var token = { start: col, state: fullState };\n
\n
        var result = null;\n
        _(this.states[state]).each(function(alt) {\n
            var regex = alt.regex;\n
            var match = regex.exec(str);\n
            if (match == null) {\n
                return;\n
            }\n
\n
            var len = match[0].length;\n
            token.end = col + len;\n
            token.tag = alt.tag;\n
\n
            var newSymbol = null;\n
            if (alt.hasOwnProperty(\'symbol\')) {\n
                var replace = function(_, n) { return match[n]; };\n
                var symspec = alt.symbol.replace(/\\$([0-9]+)/g, replace);\n
                var symMatch = /^([^:]+):(.*)/.exec(symspec);\n
                newSymbol = [ symMatch[1], symMatch[2] ];\n
            }\n
\n
            var nextState, newContext = null;\n
            if (alt.hasOwnProperty(\'then\')) {\n
                var then = alt.then.split(" ");\n
                nextState = [ context, then[0] ];\n
                if (then.length > 1) {\n
                    newContext = then[1].split(":");\n
                }\n
            } else if (len === 0) {\n
                throw new Error("StandardSyntax: Infinite loop detected: " +\n
                    "zero-length match that didn\'t change state");\n
            } else {\n
                nextState = fullState;\n
            }\n
\n
            result = { state: nextState, token: token, symbol: newSymbol };\n
            if (newContext != null) {\n
                result.newContext = newContext;\n
            }\n
\n
            _.breakLoop();\n
        });\n
\n
        return result;\n
    }\n
};\n
\n
\n
});\n
bespin.metadata = {"python": {"resourceURL": "resources/python/", "name": "python", "environments": {"worker": true}, "dependencies": {"syntax_manager": "0.0.0"}, "testmodules": [], "provides": [{"pointer": "#PySyntax", "ep": "syntax", "fileexts": ["py"], "name": "py"}], "type": "plugins/thirdparty", "description": "Python syntax highlighter"}, "syntax_worker": {"resourceURL": "resources/syntax_worker/", "description": "Coordinates multiple syntax engines", "environments": {"worker": true}, "dependencies": {"syntax_directory": "0.0.0", "underscore": "0.0.0"}, "testmodules": [], "type": "plugins/supported", "name": "syntax_worker"}, "stylesheet": {"resourceURL": "resources/stylesheet/", "name": "stylesheet", "environments": {"worker": true}, "dependencies": {"standard_syntax": "0.0.0"}, "testmodules": [], "provides": [{"pointer": "#CSSSyntax", "ep": "syntax", "fileexts": ["css", "less"], "name": "css"}], "type": "plugins/supported", "description": "CSS syntax highlighter"}, "html": {"resourceURL": "resources/html/", "name": "html", "environments": {"worker": true}, "dependencies": {"standard_syntax": "0.0.0"}, "testmodules": [], "provides": [{"pointer": "#HTMLSyntax", "ep": "syntax", "fileexts": ["htm", "html"], "name": "html"}], "type": "plugins/supported", "description": "HTML syntax highlighter"}, "js_syntax": {"resourceURL": "resources/js_syntax/", "name": "js_syntax", "environments": {"worker": true}, "dependencies": {"standard_syntax": "0.0.0"}, "testmodules": [], "provides": [{"pointer": "#JSSyntax", "ep": "syntax", "fileexts": ["js", "json"], "name": "js"}], "type": "plugins/supported", "description": "JavaScript syntax highlighter"}, "standard_syntax": {"resourceURL": "resources/standard_syntax/", "description": "Easy-to-use basis for syntax engines", "environments": {"worker": true}, "dependencies": {"syntax_worker": "0.0.0", "syntax_directory": "0.0.0", "underscore": "0.0.0"}, "testmodules": [], "type": "plugins/supported", "name": "standard_syntax"}};/* ***** BEGIN LICENSE BLOCK *****\n
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1\n
 *\n
 * The contents of this file are subject to the Mozilla Public License Version\n
 * 1.1 (the "License"); you may not use this file except in compliance with\n
 * the License. You may obtain a copy of the License at\n
 * http://www.mozilla.org/MPL/\n
 *\n
 * Software distributed under the License is distributed on an "AS IS" basis,\n
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License\n
 * for the specific language governing rights and limitations under the\n
 * License.\n
 *\n
 * The Original Code is Bespin.\n
 *\n
 * The Initial Developer of the Original Code is\n
 * Mozilla.\n
 * Portions created by the Initial Developer are Copyright (C) 2009\n
 * the Initial Developer. All Rights Reserved.\n
 *\n
 * Contributor(s):\n
 *   Bespin Team (bespin@mozilla.com)\n
 *\n
 * Alternatively, the contents of this file may be used under the terms of\n
 * either the GNU General Public License Version 2 or later (the "GPL"), or\n
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),\n
 * in which case the provisions of the GPL or the LGPL are applicable instead\n
 * of those above. If you wish to allow use of your version of this file only\n
 * under the terms of either the GPL or the LGPL, and not to allow others to\n
 * use your version of this file under the terms of the MPL, indicate your\n
 * decision by deleting the provisions above and replace them with the notice\n
 * and other provisions required by the GPL or the LGPL. If you do not delete\n
 * the provisions above, a recipient may use your version of this file under\n
 * the terms of any one of the MPL, the GPL or the LGPL.\n
 *\n
 * ***** END LICENSE BLOCK ***** */\n
\n
if (typeof(window) !== \'undefined\') {\n
    throw new Error(\'"worker.js can only be loaded in a web worker. Use the \' +\n
        \'"worker_manager" plugin to instantiate web workers.\');\n
}\n
\n
var messageQueue = [];\n
var target = null;\n
\n
if (typeof(bespin) === \'undefined\') {\n
    bespin = {};\n
}\n
\n
function pump() {\n
    if (messageQueue.length === 0) {\n
        return;\n
    }\n
\n
    var msg = messageQueue[0];\n
    switch (msg.op) {\n
    case \'load\':\n
        var base = msg.base;\n
        bespin.base = base;\n
        if (!bespin.hasOwnProperty(\'tiki\')) {\n
            importScripts(base + "tiki.js");\n
        }\n
        if (!bespin.bootLoaded) {\n
            importScripts(base + "plugin/register/boot");\n
            bespin.bootLoaded = true;\n
        }\n
\n
        var require = bespin.tiki.require;\n
        require.loader.sources[0].xhr = true;\n
        require.ensurePackage(\'::bespin\', function() {\n
            var catalog = require(\'bespin:plugins\').catalog;\n
            var Promise = require(\'bespin:promise\').Promise;\n
\n
            var pr;\n
            if (!bespin.hasOwnProperty(\'metadata\')) {\n
                pr = catalog.loadMetadataFromURL("plugin/register/worker");\n
            } else {\n
                catalog.registerMetadata(bespin.metadata);\n
                pr = new Promise();\n
                pr.resolve();\n
            }\n
\n
            pr.then(function() {\n
                require.ensurePackage(msg.pkg, function() {\n
                    var module = require(msg.module);\n
                    target = module[msg.target];\n
                    messageQueue.shift();\n
                    pump();\n
                });\n
            });\n
        });\n
        break;\n
\n
    case \'invoke\':\n
        function finish(result) {\n
            var resp = { op: \'finish\', id: msg.id, result: result };\n
            postMessage(JSON.stringify(resp));\n
            messageQueue.shift();\n
            pump();\n
        }\n
\n
        if (!target.hasOwnProperty(msg.method)) {\n
            throw new Error("No such method: " + msg.method);\n
        }\n
\n
        var rv = target[msg.method].apply(target, msg.args);\n
        if (typeof(rv) === \'object\' && rv.isPromise) {\n
            rv.then(finish, function(e) { throw e; });\n
        } else {\n
            finish(rv);\n
        }\n
\n
        break;\n
    }\n
}\n
\n
onmessage = function(ev) {\n
    messageQueue.push(JSON.parse(ev.data));\n
    if (messageQueue.length === 1) {\n
        pump();\n
    }\n
};\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
