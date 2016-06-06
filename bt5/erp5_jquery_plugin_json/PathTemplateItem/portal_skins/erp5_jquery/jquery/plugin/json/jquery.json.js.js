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
            <value> <string>ts58170054.11</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.json.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * jQuery JSON plugin 2.4.0\n
 *\n
 * @author Brantley Harris, 2009-2011\n
 * @author Timo Tijhof, 2011-2012\n
 * @source This plugin is heavily influenced by MochiKit\'s serializeJSON, which is\n
 *         copyrighted 2005 by Bob Ippolito.\n
 * @source Brantley Harris wrote this plugin. It is based somewhat on the JSON.org\n
 *         website\'s http://www.json.org/json2.js, which proclaims:\n
 *         "NO WARRANTY EXPRESSED OR IMPLIED. USE AT YOUR OWN RISK.", a sentiment that\n
 *         I uphold.\n
 * @license MIT License <http://www.opensource.org/licenses/mit-license.php>\n
 */\n
(function ($) {\n
\t\'use strict\';\n
\n
\tvar escape = /["\\\\\\x00-\\x1f\\x7f-\\x9f]/g,\n
\t\tmeta = {\n
\t\t\t\'\\b\': \'\\\\b\',\n
\t\t\t\'\\t\': \'\\\\t\',\n
\t\t\t\'\\n\': \'\\\\n\',\n
\t\t\t\'\\f\': \'\\\\f\',\n
\t\t\t\'\\r\': \'\\\\r\',\n
\t\t\t\'"\' : \'\\\\"\',\n
\t\t\t\'\\\\\': \'\\\\\\\\\'\n
\t\t},\n
\t\thasOwn = Object.prototype.hasOwnProperty;\n
\n
\t/**\n
\t * jQuery.toJSON\n
\t * Converts the given argument into a JSON representation.\n
\t *\n
\t * @param o {Mixed} The json-serializable *thing* to be converted\n
\t *\n
\t * If an object has a toJSON prototype, that will be used to get the representation.\n
\t * Non-integer/string keys are skipped in the object, as are keys that point to a\n
\t * function.\n
\t *\n
\t */\n
\t$.toJSON = typeof JSON === \'object\' && JSON.stringify ? JSON.stringify : function (o) {\n
\t\tif (o === null) {\n
\t\t\treturn \'null\';\n
\t\t}\n
\n
\t\tvar pairs, k, name, val,\n
\t\t\ttype = $.type(o);\n
\n
\t\tif (type === \'undefined\') {\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\t// Also covers instantiated Number and Boolean objects,\n
\t\t// which are typeof \'object\' but thanks to $.type, we\n
\t\t// catch them here. I don\'t know whether it is right\n
\t\t// or wrong that instantiated primitives are not\n
\t\t// exported to JSON as an {"object":..}.\n
\t\t// We choose this path because that\'s what the browsers did.\n
\t\tif (type === \'number\' || type === \'boolean\') {\n
\t\t\treturn String(o);\n
\t\t}\n
\t\tif (type === \'string\') {\n
\t\t\treturn $.quoteString(o);\n
\t\t}\n
\t\tif (typeof o.toJSON === \'function\') {\n
\t\t\treturn $.toJSON(o.toJSON());\n
\t\t}\n
\t\tif (type === \'date\') {\n
\t\t\tvar month = o.getUTCMonth() + 1,\n
\t\t\t\tday = o.getUTCDate(),\n
\t\t\t\tyear = o.getUTCFullYear(),\n
\t\t\t\thours = o.getUTCHours(),\n
\t\t\t\tminutes = o.getUTCMinutes(),\n
\t\t\t\tseconds = o.getUTCSeconds(),\n
\t\t\t\tmilli = o.getUTCMilliseconds();\n
\n
\t\t\tif (month < 10) {\n
\t\t\t\tmonth = \'0\' + month;\n
\t\t\t}\n
\t\t\tif (day < 10) {\n
\t\t\t\tday = \'0\' + day;\n
\t\t\t}\n
\t\t\tif (hours < 10) {\n
\t\t\t\thours = \'0\' + hours;\n
\t\t\t}\n
\t\t\tif (minutes < 10) {\n
\t\t\t\tminutes = \'0\' + minutes;\n
\t\t\t}\n
\t\t\tif (seconds < 10) {\n
\t\t\t\tseconds = \'0\' + seconds;\n
\t\t\t}\n
\t\t\tif (milli < 100) {\n
\t\t\t\tmilli = \'0\' + milli;\n
\t\t\t}\n
\t\t\tif (milli < 10) {\n
\t\t\t\tmilli = \'0\' + milli;\n
\t\t\t}\n
\t\t\treturn \'"\' + year + \'-\' + month + \'-\' + day + \'T\' +\n
\t\t\t\thours + \':\' + minutes + \':\' + seconds +\n
\t\t\t\t\'.\' + milli + \'Z"\';\n
\t\t}\n
\n
\t\tpairs = [];\n
\n
\t\tif ($.isArray(o)) {\n
\t\t\tfor (k = 0; k < o.length; k++) {\n
\t\t\t\tpairs.push($.toJSON(o[k]) || \'null\');\n
\t\t\t}\n
\t\t\treturn \'[\' + pairs.join(\',\') + \']\';\n
\t\t}\n
\n
\t\t// Any other object (plain object, RegExp, ..)\n
\t\t// Need to do typeof instead of $.type, because we also\n
\t\t// want to catch non-plain objects.\n
\t\tif (typeof o === \'object\') {\n
\t\t\tfor (k in o) {\n
\t\t\t\t// Only include own properties,\n
\t\t\t\t// Filter out inherited prototypes\n
\t\t\t\tif (hasOwn.call(o, k)) {\n
\t\t\t\t\t// Keys must be numerical or string. Skip others\n
\t\t\t\t\ttype = typeof k;\n
\t\t\t\t\tif (type === \'number\') {\n
\t\t\t\t\t\tname = \'"\' + k + \'"\';\n
\t\t\t\t\t} else if (type === \'string\') {\n
\t\t\t\t\t\tname = $.quoteString(k);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t}\n
\t\t\t\t\ttype = typeof o[k];\n
\n
\t\t\t\t\t// Invalid values like these return undefined\n
\t\t\t\t\t// from toJSON, however those object members\n
\t\t\t\t\t// shouldn\'t be included in the JSON string at all.\n
\t\t\t\t\tif (type !== \'function\' && type !== \'undefined\') {\n
\t\t\t\t\t\tval = $.toJSON(o[k]);\n
\t\t\t\t\t\tpairs.push(name + \':\' + val);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\treturn \'{\' + pairs.join(\',\') + \'}\';\n
\t\t}\n
\t};\n
\n
\t/**\n
\t * jQuery.evalJSON\n
\t * Evaluates a given json string.\n
\t *\n
\t * @param str {String}\n
\t */\n
\t$.evalJSON = typeof JSON === \'object\' && JSON.parse ? JSON.parse : function (str) {\n
\t\t/*jshint evil: true */\n
\t\treturn eval(\'(\' + str + \')\');\n
\t};\n
\n
\t/**\n
\t * jQuery.secureEvalJSON\n
\t * Evals JSON in a way that is *more* secure.\n
\t *\n
\t * @param str {String}\n
\t */\n
\t$.secureEvalJSON = typeof JSON === \'object\' && JSON.parse ? JSON.parse : function (str) {\n
\t\tvar filtered =\n
\t\t\tstr\n
\t\t\t.replace(/\\\\["\\\\\\/bfnrtu]/g, \'@\')\n
\t\t\t.replace(/"[^"\\\\\\n\\r]*"|true|false|null|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?/g, \']\')\n
\t\t\t.replace(/(?:^|:|,)(?:\\s*\\[)+/g, \'\');\n
\n
\t\tif (/^[\\],:{}\\s]*$/.test(filtered)) {\n
\t\t\t/*jshint evil: true */\n
\t\t\treturn eval(\'(\' + str + \')\');\n
\t\t}\n
\t\tthrow new SyntaxError(\'Error parsing JSON, source is not valid.\');\n
\t};\n
\n
\t/**\n
\t * jQuery.quoteString\n
\t * Returns a string-repr of a string, escaping quotes intelligently.\n
\t * Mostly a support function for toJSON.\n
\t * Examples:\n
\t * >>> jQuery.quoteString(\'apple\')\n
\t * "apple"\n
\t *\n
\t * >>> jQuery.quoteString(\'"Where are we going?", she asked.\')\n
\t * "\\"Where are we going?\\", she asked."\n
\t */\n
\t$.quoteString = function (str) {\n
\t\tif (str.match(escape)) {\n
\t\t\treturn \'"\' + str.replace(escape, function (a) {\n
\t\t\t\tvar c = meta[a];\n
\t\t\t\tif (typeof c === \'string\') {\n
\t\t\t\t\treturn c;\n
\t\t\t\t}\n
\t\t\t\tc = a.charCodeAt();\n
\t\t\t\treturn \'\\\\u00\' + Math.floor(c / 16).toString(16) + (c % 16).toString(16);\n
\t\t\t}) + \'"\';\n
\t\t}\n
\t\treturn \'"\' + str + \'"\';\n
\t};\n
\n
}(jQuery));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5230</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
