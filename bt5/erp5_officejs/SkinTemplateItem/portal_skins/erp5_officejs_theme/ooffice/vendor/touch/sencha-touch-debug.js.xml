<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44314688.66</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>sencha-touch-debug.js</string> </value>
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
            <value> <int>505784</int> </value>
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

/*\n
This file is part of Sencha Touch 2.1\n
\n
Copyright (c) 2011-2012 Sencha Inc\n
\n
Contact:  http://www.sencha.com/contact\n
\n
GNU General Public License Usage\n
This file may be used under the terms of the GNU General Public License version 3.0 as\n
published by the Free Software Foundation and appearing in the file LICENSE included in the\n
packaging of this file.\n
\n
Please review the following information to ensure the GNU General Public License version 3.0\n
requirements will be met: http://www.gnu.org/copyleft/gpl.html.\n
\n
If you are unsure which license is appropriate for your use, please contact the sales department\n
at http://www.sencha.com/contact.\n
\n
Build date: 2012-11-05 22:31:29 (08c91901ae8449841ff23e5d3fb404d6128d3b0b)\n
*/\n
//@tag foundation,core\n
//@define Ext\n
\n
/**\n
 * @class Ext\n
 * @singleton\n
 */\n
(function() {\n
    var global = this,\n
        objectPrototype = Object.prototype,\n
        toString = objectPrototype.toString,\n
        enumerables = true,\n
        enumerablesTest = { toString: 1 },\n
        emptyFn = function(){},\n
        i;\n
\n
    if (typeof Ext === \'undefined\') {\n
        global.Ext = {};\n
    }\n
\n
    Ext.global = global;\n
\n
    for (i in enumerablesTest) {\n
        enumerables = null;\n
    }\n
\n
    if (enumerables) {\n
        enumerables = [\'hasOwnProperty\', \'valueOf\', \'isPrototypeOf\', \'propertyIsEnumerable\',\n
                       \'toLocaleString\', \'toString\', \'constructor\'];\n
    }\n
\n
    /**\n
     * An array containing extra enumerables for old browsers.\n
     * @property {String[]}\n
     */\n
    Ext.enumerables = enumerables;\n
\n
    /**\n
     * Copies all the properties of config to the specified object.\n
     * Note that if recursive merging and cloning without referencing the original objects / arrays is needed, use\n
     * {@link Ext.Object#merge} instead.\n
     * @param {Object} object The receiver of the properties.\n
     * @param {Object} config The source of the properties.\n
     * @param {Object} [defaults] A different object that will also be applied for default values.\n
     * @return {Object} returns obj\n
     */\n
    Ext.apply = function(object, config, defaults) {\n
        if (defaults) {\n
            Ext.apply(object, defaults);\n
        }\n
\n
        if (object && config && typeof config === \'object\') {\n
            var i, j, k;\n
\n
            for (i in config) {\n
                object[i] = config[i];\n
            }\n
\n
            if (enumerables) {\n
                for (j = enumerables.length; j--;) {\n
                    k = enumerables[j];\n
                    if (config.hasOwnProperty(k)) {\n
                        object[k] = config[k];\n
                    }\n
                }\n
            }\n
        }\n
\n
        return object;\n
    };\n
\n
    Ext.buildSettings = Ext.apply({\n
        baseCSSPrefix: \'x-\',\n
        scopeResetCSS: false\n
    }, Ext.buildSettings || {});\n
\n
    Ext.apply(Ext, {\n
        /**\n
         * @property {Function}\n
         * A reusable empty function\n
         */\n
        emptyFn: emptyFn,\n
\n
        baseCSSPrefix: Ext.buildSettings.baseCSSPrefix,\n
\n
        /**\n
         * Copies all the properties of config to object if they don\'t already exist.\n
         * @param {Object} object The receiver of the properties.\n
         * @param {Object} config The source of the properties.\n
         * @return {Object} returns obj\n
         */\n
        applyIf: function(object, config) {\n
            var property;\n
\n
            if (object) {\n
                for (property in config) {\n
                    if (object[property] === undefined) {\n
                        object[property] = config[property];\n
                    }\n
                }\n
            }\n
\n
            return object;\n
        },\n
\n
        /**\n
         * Iterates either an array or an object. This method delegates to\n
         * {@link Ext.Array#each Ext.Array.each} if the given value is iterable, and {@link Ext.Object#each Ext.Object.each} otherwise.\n
         *\n
         * @param {Object/Array} object The object or array to be iterated.\n
         * @param {Function} fn The function to be called for each iteration. See and {@link Ext.Array#each Ext.Array.each} and\n
         * {@link Ext.Object#each Ext.Object.each} for detailed lists of arguments passed to this function depending on the given object\n
         * type that is being iterated.\n
         * @param {Object} scope (Optional) The scope (`this` reference) in which the specified function is executed.\n
         * Defaults to the object being iterated itself.\n
         */\n
        iterate: function(object, fn, scope) {\n
            if (Ext.isEmpty(object)) {\n
                return;\n
            }\n
\n
            if (scope === undefined) {\n
                scope = object;\n
            }\n
\n
            if (Ext.isIterable(object)) {\n
                Ext.Array.each.call(Ext.Array, object, fn, scope);\n
            }\n
            else {\n
                Ext.Object.each.call(Ext.Object, object, fn, scope);\n
            }\n
        }\n
    });\n
\n
    Ext.apply(Ext, {\n
\n
        /**\n
         * This method deprecated. Use {@link Ext#define Ext.define} instead.\n
         * @method\n
         * @param {Function} superclass\n
         * @param {Object} overrides\n
         * @return {Function} The subclass constructor from the `overrides` parameter, or a generated one if not provided.\n
         * @deprecated 4.0.0 Please use {@link Ext#define Ext.define} instead\n
         */\n
        extend: function() {\n
            // inline overrides\n
            var objectConstructor = objectPrototype.constructor,\n
                inlineOverrides = function(o) {\n
                for (var m in o) {\n
                    if (!o.hasOwnProperty(m)) {\n
                        continue;\n
                    }\n
                    this[m] = o[m];\n
                }\n
            };\n
\n
            return function(subclass, superclass, overrides) {\n
                // First we check if the user passed in just the superClass with overrides\n
                if (Ext.isObject(superclass)) {\n
                    overrides = superclass;\n
                    superclass = subclass;\n
                    subclass = overrides.constructor !== objectConstructor ? overrides.constructor : function() {\n
                        superclass.apply(this, arguments);\n
                    };\n
                }\n
\n
                //<debug>\n
                if (!superclass) {\n
                    Ext.Error.raise({\n
                        sourceClass: \'Ext\',\n
                        sourceMethod: \'extend\',\n
                        msg: \'Attempting to extend from a class which has not been loaded on the page.\'\n
                    });\n
                }\n
                //</debug>\n
\n
                // We create a new temporary class\n
                var F = function() {},\n
                    subclassProto, superclassProto = superclass.prototype;\n
\n
                F.prototype = superclassProto;\n
                subclassProto = subclass.prototype = new F();\n
                subclassProto.constructor = subclass;\n
                subclass.superclass = superclassProto;\n
\n
                if (superclassProto.constructor === objectConstructor) {\n
                    superclassProto.constructor = superclass;\n
                }\n
\n
                subclass.override = function(overrides) {\n
                    Ext.override(subclass, overrides);\n
                };\n
\n
                subclassProto.override = inlineOverrides;\n
                subclassProto.proto = subclassProto;\n
\n
                subclass.override(overrides);\n
                subclass.extend = function(o) {\n
                    return Ext.extend(subclass, o);\n
                };\n
\n
                return subclass;\n
            };\n
        }(),\n
\n
        /**\n
         * Proxy to {@link Ext.Base#override}. Please refer {@link Ext.Base#override} for further details.\n
         *\n
         * @param {Object} cls The class to override\n
         * @param {Object} overrides The properties to add to `origClass`. This should be specified as an object literal\n
         * containing one or more properties.\n
         * @method override\n
         * @deprecated 4.1.0 Please use {@link Ext#define Ext.define} instead.\n
         */\n
        override: function(cls, overrides) {\n
            if (cls.$isClass) {\n
                return cls.override(overrides);\n
            }\n
            else {\n
                Ext.apply(cls.prototype, overrides);\n
            }\n
        }\n
    });\n
\n
    // A full set of static methods to do type checking\n
    Ext.apply(Ext, {\n
\n
        /**\n
         * Returns the given value itself if it\'s not empty, as described in {@link Ext#isEmpty}; returns the default\n
         * value (second argument) otherwise.\n
         *\n
         * @param {Object} value The value to test.\n
         * @param {Object} defaultValue The value to return if the original value is empty.\n
         * @param {Boolean} [allowBlank=false] (optional) `true` to allow zero length strings to qualify as non-empty.\n
         * @return {Object} `value`, if non-empty, else `defaultValue`.\n
         */\n
        valueFrom: function(value, defaultValue, allowBlank){\n
            return Ext.isEmpty(value, allowBlank) ? defaultValue : value;\n
        },\n
\n
        /**\n
         * Returns the type of the given variable in string format. List of possible values are:\n
         *\n
         * - `undefined`: If the given value is `undefined`\n
         * - `null`: If the given value is `null`\n
         * - `string`: If the given value is a string\n
         * - `number`: If the given value is a number\n
         * - `boolean`: If the given value is a boolean value\n
         * - `date`: If the given value is a `Date` object\n
         * - `function`: If the given value is a function reference\n
         * - `object`: If the given value is an object\n
         * - `array`: If the given value is an array\n
         * - `regexp`: If the given value is a regular expression\n
         * - `element`: If the given value is a DOM Element\n
         * - `textnode`: If the given value is a DOM text node and contains something other than whitespace\n
         * - `whitespace`: If the given value is a DOM text node and contains only whitespace\n
         *\n
         * @param {Object} value\n
         * @return {String}\n
         */\n
        typeOf: function(value) {\n
            if (value === null) {\n
                return \'null\';\n
            }\n
\n
            var type = typeof value;\n
\n
            if (type === \'undefined\' || type === \'string\' || type === \'number\' || type === \'boolean\') {\n
                return type;\n
            }\n
\n
            var typeToString = toString.call(value);\n
\n
            switch(typeToString) {\n
                case \'[object Array]\':\n
                    return \'array\';\n
                case \'[object Date]\':\n
                    return \'date\';\n
                case \'[object Boolean]\':\n
                    return \'boolean\';\n
                case \'[object Number]\':\n
                    return \'number\';\n
                case \'[object RegExp]\':\n
                    return \'regexp\';\n
            }\n
\n
            if (type === \'function\') {\n
                return \'function\';\n
            }\n
\n
            if (type === \'object\') {\n
                if (value.nodeType !== undefined) {\n
                    if (value.nodeType === 3) {\n
                        return (/\\S/).test(value.nodeValue) ? \'textnode\' : \'whitespace\';\n
                    }\n
                    else {\n
                        return \'element\';\n
                    }\n
                }\n
\n
                return \'object\';\n
            }\n
\n
            //<debug error>\n
            Ext.Error.raise({\n
                sourceClass: \'Ext\',\n
                sourceMethod: \'typeOf\',\n
                msg: \'Failed to determine the type of the specified value "\' + value + \'". This is most likely a bug.\'\n
            });\n
            //</debug>\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is empty, `false` otherwise. The value is deemed to be empty if it is either:\n
         *\n
         * - `null`\n
         * - `undefined`\n
         * - a zero-length array.\n
         * - a zero-length string (Unless the `allowEmptyString` parameter is set to `true`).\n
         *\n
         * @param {Object} value The value to test.\n
         * @param {Boolean} [allowEmptyString=false] (optional) `true` to allow empty strings.\n
         * @return {Boolean}\n
         */\n
        isEmpty: function(value, allowEmptyString) {\n
            return (value === null) || (value === undefined) || (!allowEmptyString ? value === \'\' : false) || (Ext.isArray(value) && value.length === 0);\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a JavaScript Array, `false` otherwise.\n
         *\n
         * @param {Object} target The target to test.\n
         * @return {Boolean}\n
         * @method\n
         */\n
        isArray: (\'isArray\' in Array) ? Array.isArray : function(value) {\n
            return toString.call(value) === \'[object Array]\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a JavaScript Date object, `false` otherwise.\n
         * @param {Object} object The object to test.\n
         * @return {Boolean}\n
         */\n
        isDate: function(value) {\n
            return toString.call(value) === \'[object Date]\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a JavaScript Object, `false` otherwise.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         * @method\n
         */\n
        isObject: (toString.call(null) === \'[object Object]\') ?\n
        function(value) {\n
            // check ownerDocument here as well to exclude DOM nodes\n
            return value !== null && value !== undefined && toString.call(value) === \'[object Object]\' && value.ownerDocument === undefined;\n
        } :\n
        function(value) {\n
            return toString.call(value) === \'[object Object]\';\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        isSimpleObject: function(value) {\n
            return value instanceof Object && value.constructor === Object;\n
        },\n
        /**\n
         * Returns `true` if the passed value is a JavaScript \'primitive\', a string, number or Boolean.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isPrimitive: function(value) {\n
            var type = typeof value;\n
\n
            return type === \'string\' || type === \'number\' || type === \'boolean\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a JavaScript Function, `false` otherwise.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         * @method\n
         */\n
        isFunction:\n
        // Safari 3.x and 4.x returns \'function\' for typeof <NodeList>, hence we need to fall back to using\n
        // Object.prorotype.toString (slower)\n
        (typeof document !== \'undefined\' && typeof document.getElementsByTagName(\'body\') === \'function\') ? function(value) {\n
            return toString.call(value) === \'[object Function]\';\n
        } : function(value) {\n
            return typeof value === \'function\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a number. Returns `false` for non-finite numbers.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isNumber: function(value) {\n
            return typeof value === \'number\' && isFinite(value);\n
        },\n
\n
        /**\n
         * Validates that a value is numeric.\n
         * @param {Object} value Examples: 1, \'1\', \'2.34\'\n
         * @return {Boolean} `true` if numeric, `false` otherwise.\n
         */\n
        isNumeric: function(value) {\n
            return !isNaN(parseFloat(value)) && isFinite(value);\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a string.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isString: function(value) {\n
            return typeof value === \'string\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a Boolean.\n
         *\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isBoolean: function(value) {\n
            return typeof value === \'boolean\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is an HTMLElement.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isElement: function(value) {\n
            return value ? value.nodeType === 1 : false;\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is a TextNode.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isTextNode: function(value) {\n
            return value ? value.nodeName === "#text" : false;\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is defined.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isDefined: function(value) {\n
            return typeof value !== \'undefined\';\n
        },\n
\n
        /**\n
         * Returns `true` if the passed value is iterable, `false` otherwise.\n
         * @param {Object} value The value to test.\n
         * @return {Boolean}\n
         */\n
        isIterable: function(value) {\n
            return (value && typeof value !== \'string\') ? value.length !== undefined : false;\n
        }\n
    });\n
\n
    Ext.apply(Ext, {\n
\n
        /**\n
         * Clone almost any type of variable including array, object, DOM nodes and Date without keeping the old reference.\n
         * @param {Object} item The variable to clone.\n
         * @return {Object} clone\n
         */\n
        clone: function(item) {\n
            if (item === null || item === undefined) {\n
                return item;\n
            }\n
\n
            // DOM nodes\n
            if (item.nodeType && item.cloneNode) {\n
                return item.cloneNode(true);\n
            }\n
\n
            // Strings\n
            var type = toString.call(item);\n
\n
            // Dates\n
            if (type === \'[object Date]\') {\n
                return new Date(item.getTime());\n
            }\n
\n
            var i, j, k, clone, key;\n
\n
            // Arrays\n
            if (type === \'[object Array]\') {\n
                i = item.length;\n
\n
                clone = [];\n
\n
                while (i--) {\n
                    clone[i] = Ext.clone(item[i]);\n
                }\n
            }\n
            // Objects\n
            else if (type === \'[object Object]\' && item.constructor === Object) {\n
                clone = {};\n
\n
                for (key in item) {\n
                    clone[key] = Ext.clone(item[key]);\n
                }\n
\n
                if (enumerables) {\n
                    for (j = enumerables.length; j--;) {\n
                        k = enumerables[j];\n
                        clone[k] = item[k];\n
                    }\n
                }\n
            }\n
\n
            return clone || item;\n
        },\n
\n
        /**\n
         * @private\n
         * Generate a unique reference of Ext in the global scope, useful for sandboxing.\n
         */\n
        getUniqueGlobalNamespace: function() {\n
            var uniqueGlobalNamespace = this.uniqueGlobalNamespace;\n
\n
            if (uniqueGlobalNamespace === undefined) {\n
                var i = 0;\n
\n
                do {\n
                    uniqueGlobalNamespace = \'ExtBox\' + (++i);\n
                } while (Ext.global[uniqueGlobalNamespace] !== undefined);\n
\n
                Ext.global[uniqueGlobalNamespace] = Ext;\n
                this.uniqueGlobalNamespace = uniqueGlobalNamespace;\n
            }\n
\n
            return uniqueGlobalNamespace;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        functionFactory: function() {\n
            var args = Array.prototype.slice.call(arguments),\n
                ln = args.length;\n
\n
            if (ln > 0) {\n
                args[ln - 1] = \'var Ext=window.\' + this.getUniqueGlobalNamespace() + \';\' + args[ln - 1];\n
            }\n
\n
            return Function.prototype.constructor.apply(Function.prototype, args);\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        globalEval: (\'execScript\' in global) ? function(code) {\n
            global.execScript(code)\n
        } : function(code) {\n
            (function(){\n
                eval(code);\n
            })();\n
        }\n
\n
        //<feature logger>\n
        /**\n
         * @private\n
         * @property\n
         */\n
        ,Logger: {\n
            log: function(message, priority) {\n
                if (\'console\' in global) {\n
                    if (!priority || !(priority in global.console)) {\n
                        priority = \'log\';\n
                    }\n
                    message = \'[\' + priority.toUpperCase() + \'] \' + message;\n
                    global.console[priority](message);\n
                }\n
            },\n
            verbose: function(message) {\n
                this.log(message, \'verbose\');\n
            },\n
            info: function(message) {\n
                this.log(message, \'info\');\n
            },\n
            warn: function(message) {\n
                this.log(message, \'warn\');\n
            },\n
            error: function(message) {\n
                throw new Error(message);\n
            },\n
            deprecate: function(message) {\n
                this.log(message, \'warn\');\n
            }\n
        }\n
        //</feature>\n
    });\n
\n
    /**\n
     * Old alias to {@link Ext#typeOf}.\n
     * @deprecated 4.0.0 Please use {@link Ext#typeOf} instead.\n
     * @method\n
     * @alias Ext#typeOf\n
     */\n
    Ext.type = Ext.typeOf;\n
\n
})();\n
\n
//@tag foundation,core\n
//@define Ext.Version\n
//@require Ext\n
\n
/**\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @docauthor Jacky Nguyen <jacky@sencha.com>\n
 * @class Ext.Version\n
 *\n
 * A utility class that wrap around a string version number and provide convenient\n
 * method to perform comparison. See also: {@link Ext.Version#compare compare}. Example:\n
 *\n
 *     var version = new Ext.Version(\'1.0.2beta\');\n
 *     console.log("Version is " + version); // Version is 1.0.2beta\n
 *\n
 *     console.log(version.getMajor()); // 1\n
 *     console.log(version.getMinor()); // 0\n
 *     console.log(version.getPatch()); // 2\n
 *     console.log(version.getBuild()); // 0\n
 *     console.log(version.getRelease()); // beta\n
 *\n
 *     console.log(version.isGreaterThan(\'1.0.1\')); // true\n
 *     console.log(version.isGreaterThan(\'1.0.2alpha\')); // true\n
 *     console.log(version.isGreaterThan(\'1.0.2RC\')); // false\n
 *     console.log(version.isGreaterThan(\'1.0.2\')); // false\n
 *     console.log(version.isLessThan(\'1.0.2\')); // true\n
 *\n
 *     console.log(version.match(1.0)); // true\n
 *     console.log(version.match(\'1.0.2\')); // true\n
 */\n
(function() {\n
\n
// Current core version\n
var version = \'4.1.0\', Version;\n
    Ext.Version = Version = Ext.extend(Object, {\n
\n
        /**\n
         * Creates new Version object.\n
         * @param {String/Number} version The version number in the follow standard format: major[.minor[.patch[.build[release]]]]\n
         * Examples: 1.0 or 1.2.3beta or 1.2.3.4RC\n
         * @return {Ext.Version} this\n
         */\n
        constructor: function(version) {\n
            var toNumber = this.toNumber,\n
                parts, releaseStartIndex;\n
\n
            if (version instanceof Version) {\n
                return version;\n
            }\n
\n
            this.version = this.shortVersion = String(version).toLowerCase().replace(/_/g, \'.\').replace(/[\\-+]/g, \'\');\n
\n
            releaseStartIndex = this.version.search(/([^\\d\\.])/);\n
\n
            if (releaseStartIndex !== -1) {\n
                this.release = this.version.substr(releaseStartIndex, version.length);\n
                this.shortVersion = this.version.substr(0, releaseStartIndex);\n
            }\n
\n
            this.shortVersion = this.shortVersion.replace(/[^\\d]/g, \'\');\n
\n
            parts = this.version.split(\'.\');\n
\n
            this.major = toNumber(parts.shift());\n
            this.minor = toNumber(parts.shift());\n
            this.patch = toNumber(parts.shift());\n
            this.build = toNumber(parts.shift());\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @param value\n
         * @return {Number}\n
         */\n
        toNumber: function(value) {\n
            value = parseInt(value || 0, 10);\n
\n
            if (isNaN(value)) {\n
                value = 0;\n
            }\n
\n
            return value;\n
        },\n
\n
        /**\n
         * Override the native `toString()` method.\n
         * @private\n
         * @return {String} version\n
         */\n
        toString: function() {\n
            return this.version;\n
        },\n
\n
        /**\n
         * Override the native `valueOf()` method.\n
         * @private\n
         * @return {String} version\n
         */\n
        valueOf: function() {\n
            return this.version;\n
        },\n
\n
        /**\n
         * Returns the major component value.\n
         * @return {Number} major\n
         */\n
        getMajor: function() {\n
            return this.major || 0;\n
        },\n
\n
        /**\n
         * Returns the minor component value.\n
         * @return {Number} minor\n
         */\n
        getMinor: function() {\n
            return this.minor || 0;\n
        },\n
\n
        /**\n
         * Returns the patch component value.\n
         * @return {Number} patch\n
         */\n
        getPatch: function() {\n
            return this.patch || 0;\n
        },\n
\n
        /**\n
         * Returns the build component value.\n
         * @return {Number} build\n
         */\n
        getBuild: function() {\n
            return this.build || 0;\n
        },\n
\n
        /**\n
         * Returns the release component value.\n
         * @return {Number} release\n
         */\n
        getRelease: function() {\n
            return this.release || \'\';\n
        },\n
\n
        /**\n
         * Returns whether this version if greater than the supplied argument.\n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version if greater than the target, `false` otherwise.\n
         */\n
        isGreaterThan: function(target) {\n
            return Version.compare(this.version, target) === 1;\n
        },\n
\n
        /**\n
         * Returns whether this version if greater than or equal to the supplied argument.\n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version if greater than or equal to the target, `false` otherwise.\n
         */\n
        isGreaterThanOrEqual: function(target) {\n
            return Version.compare(this.version, target) >= 0;\n
        },\n
\n
        /**\n
         * Returns whether this version if smaller than the supplied argument.\n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version if smaller than the target, `false` otherwise.\n
         */\n
        isLessThan: function(target) {\n
            return Version.compare(this.version, target) === -1;\n
        },\n
\n
        /**\n
         * Returns whether this version if less than or equal to the supplied argument.\n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version if less than or equal to the target, `false` otherwise.\n
         */\n
        isLessThanOrEqual: function(target) {\n
            return Version.compare(this.version, target) <= 0;\n
        },\n
\n
        /**\n
         * Returns whether this version equals to the supplied argument.\n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version equals to the target, `false` otherwise.\n
         */\n
        equals: function(target) {\n
            return Version.compare(this.version, target) === 0;\n
        },\n
\n
        /**\n
         * Returns whether this version matches the supplied argument. Example:\n
         * \n
         *     var version = new Ext.Version(\'1.0.2beta\');\n
         *     console.log(version.match(1)); // true\n
         *     console.log(version.match(1.0)); // true\n
         *     console.log(version.match(\'1.0.2\')); // true\n
         *     console.log(version.match(\'1.0.2RC\')); // false\n
         * \n
         * @param {String/Number} target The version to compare with.\n
         * @return {Boolean} `true` if this version matches the target, `false` otherwise.\n
         */\n
        match: function(target) {\n
            target = String(target);\n
            return this.version.substr(0, target.length) === target;\n
        },\n
\n
        /**\n
         * Returns this format: [major, minor, patch, build, release]. Useful for comparison.\n
         * @return {Number[]}\n
         */\n
        toArray: function() {\n
            return [this.getMajor(), this.getMinor(), this.getPatch(), this.getBuild(), this.getRelease()];\n
        },\n
\n
        /**\n
         * Returns shortVersion version without dots and release.\n
         * @return {String}\n
         */\n
        getShortVersion: function() {\n
            return this.shortVersion;\n
        },\n
\n
        /**\n
         * Convenient alias to {@link Ext.Version#isGreaterThan isGreaterThan}\n
         * @param {String/Number} target\n
         * @return {Boolean}\n
         */\n
        gt: function() {\n
            return this.isGreaterThan.apply(this, arguments);\n
        },\n
\n
        /**\n
         * Convenient alias to {@link Ext.Version#isLessThan isLessThan}\n
         * @param {String/Number} target\n
         * @return {Boolean}\n
         */\n
        lt: function() {\n
            return this.isLessThan.apply(this, arguments);\n
        },\n
\n
        /**\n
         * Convenient alias to {@link Ext.Version#isGreaterThanOrEqual isGreaterThanOrEqual}\n
         * @param {String/Number} target\n
         * @return {Boolean}\n
         */\n
        gtEq: function() {\n
            return this.isGreaterThanOrEqual.apply(this, arguments);\n
        },\n
\n
        /**\n
         * Convenient alias to {@link Ext.Version#isLessThanOrEqual isLessThanOrEqual}\n
         * @param {String/Number} target\n
         * @return {Boolean}\n
         */\n
        ltEq: function() {\n
            return this.isLessThanOrEqual.apply(this, arguments);\n
        }\n
    });\n
\n
    Ext.apply(Version, {\n
        // @private\n
        releaseValueMap: {\n
            \'dev\': -6,\n
            \'alpha\': -5,\n
            \'a\': -5,\n
            \'beta\': -4,\n
            \'b\': -4,\n
            \'rc\': -3,\n
            \'#\': -2,\n
            \'p\': -1,\n
            \'pl\': -1\n
        },\n
\n
        /**\n
         * Converts a version component to a comparable value.\n
         *\n
         * @static\n
         * @param {Object} value The value to convert\n
         * @return {Object}\n
         */\n
        getComponentValue: function(value) {\n
            return !value ? 0 : (isNaN(value) ? this.releaseValueMap[value] || value : parseInt(value, 10));\n
        },\n
\n
        /**\n
         * Compare 2 specified versions, starting from left to right. If a part contains special version strings,\n
         * they are handled in the following order:\n
         * \'dev\' < \'alpha\' = \'a\' < \'beta\' = \'b\' < \'RC\' = \'rc\' < \'#\' < \'pl\' = \'p\' < \'anything else\'\n
         *\n
         * @static\n
         * @param {String} current The current version to compare to.\n
         * @param {String} target The target version to compare to.\n
         * @return {Number} Returns -1 if the current version is smaller than the target version, 1 if greater, and 0 if they\'re equivalent.\n
         */\n
        compare: function(current, target) {\n
            var currentValue, targetValue, i;\n
\n
            current = new Version(current).toArray();\n
            target = new Version(target).toArray();\n
\n
            for (i = 0; i < Math.max(current.length, target.length); i++) {\n
                currentValue = this.getComponentValue(current[i]);\n
                targetValue = this.getComponentValue(target[i]);\n
\n
                if (currentValue < targetValue) {\n
                    return -1;\n
                } else if (currentValue > targetValue) {\n
                    return 1;\n
                }\n
            }\n
\n
            return 0;\n
        }\n
    });\n
\n
    Ext.apply(Ext, {\n
        /**\n
         * @private\n
         */\n
        versions: {},\n
\n
        /**\n
         * @private\n
         */\n
        lastRegisteredVersion: null,\n
\n
        /**\n
         * Set version number for the given package name.\n
         *\n
         * @param {String} packageName The package name, for example: \'core\', \'touch\', \'extjs\'.\n
         * @param {String/Ext.Version} version The version, for example: \'1.2.3alpha\', \'2.4.0-dev\'.\n
         * @return {Ext}\n
         */\n
        setVersion: function(packageName, version) {\n
            Ext.versions[packageName] = new Version(version);\n
            Ext.lastRegisteredVersion = Ext.versions[packageName];\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Get the version number of the supplied package name; will return the last registered version\n
         * (last `Ext.setVersion()` call) if there\'s no package name given.\n
         *\n
         * @param {String} packageName (Optional) The package name, for example: \'core\', \'touch\', \'extjs\'.\n
         * @return {Ext.Version} The version.\n
         */\n
        getVersion: function(packageName) {\n
            if (packageName === undefined) {\n
                return Ext.lastRegisteredVersion;\n
            }\n
\n
            return Ext.versions[packageName];\n
        },\n
\n
        /**\n
         * Create a closure for deprecated code.\n
         *\n
         *     // This means Ext.oldMethod is only supported in 4.0.0beta and older.\n
         *     // If Ext.getVersion(\'extjs\') returns a version that is later than \'4.0.0beta\', for example \'4.0.0RC\',\n
         *     // the closure will not be invoked\n
         *     Ext.deprecate(\'extjs\', \'4.0.0beta\', function() {\n
         *         Ext.oldMethod = Ext.newMethod;\n
         *         // ...\n
         *     });\n
         *\n
         * @param {String} packageName The package name.\n
         * @param {String} since The last version before it\'s deprecated.\n
         * @param {Function} closure The callback function to be executed with the specified version is less than the current version.\n
         * @param {Object} scope The execution scope (`this`) if the closure\n
         */\n
        deprecate: function(packageName, since, closure, scope) {\n
            if (Version.compare(Ext.getVersion(packageName), since) < 1) {\n
                closure.call(scope);\n
            }\n
        }\n
    }); // End Versioning\n
\n
    Ext.setVersion(\'core\', version);\n
\n
})();\n
\n
//@tag foundation,core\n
//@define Ext.String\n
//@require Ext.Version\n
\n
/**\n
 * @class Ext.String\n
 *\n
 * A collection of useful static methods to deal with strings.\n
 * @singleton\n
 */\n
\n
Ext.String = {\n
    trimRegex: /^[\\x09\\x0a\\x0b\\x0c\\x0d\\x20\\xa0\\u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\u2007\\u2008\\u2009\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]+|[\\x09\\x0a\\x0b\\x0c\\x0d\\x20\\xa0\\u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\u2007\\u2008\\u2009\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]+$/g,\n
    escapeRe: /(\'|\\\\)/g,\n
    formatRe: /\\{(\\d+)\\}/g,\n
    escapeRegexRe: /([-.*+?^${}()|[\\]\\/\\\\])/g,\n
\n
    /**\n
     * Convert certain characters (&, <, >, and ") to their HTML character equivalents for literal display in web pages.\n
     * @param {String} value The string to encode.\n
     * @return {String} The encoded text.\n
     * @method\n
     */\n
    htmlEncode: (function() {\n
        var entities = {\n
            \'&\': \'&amp;\',\n
            \'>\': \'&gt;\',\n
            \'<\': \'&lt;\',\n
            \'"\': \'&quot;\'\n
        }, keys = [], p, regex;\n
\n
        for (p in entities) {\n
            keys.push(p);\n
        }\n
\n
        regex = new RegExp(\'(\' + keys.join(\'|\') + \')\', \'g\');\n
\n
        return function(value) {\n
            return (!value) ? value : String(value).replace(regex, function(match, capture) {\n
                return entities[capture];\n
            });\n
        };\n
    })(),\n
\n
    /**\n
     * Convert certain characters (&, <, >, and ") from their HTML character equivalents.\n
     * @param {String} value The string to decode.\n
     * @return {String} The decoded text.\n
     * @method\n
     */\n
    htmlDecode: (function() {\n
        var entities = {\n
            \'&amp;\': \'&\',\n
            \'&gt;\': \'>\',\n
            \'&lt;\': \'<\',\n
            \'&quot;\': \'"\'\n
        }, keys = [], p, regex;\n
\n
        for (p in entities) {\n
            keys.push(p);\n
        }\n
\n
        regex = new RegExp(\'(\' + keys.join(\'|\') + \'|&#[0-9]{1,5};\' + \')\', \'g\');\n
\n
        return function(value) {\n
            return (!value) ? value : String(value).replace(regex, function(match, capture) {\n
                if (capture in entities) {\n
                    return entities[capture];\n
                } else {\n
                    return String.fromCharCode(parseInt(capture.substr(2), 10));\n
                }\n
            });\n
        };\n
    })(),\n
\n
    /**\n
     * Appends content to the query string of a URL, handling logic for whether to place\n
     * a question mark or ampersand.\n
     * @param {String} url The URL to append to.\n
     * @param {String} string The content to append to the URL.\n
     * @return {String} The resulting URL.\n
     */\n
    urlAppend : function(url, string) {\n
        if (!Ext.isEmpty(string)) {\n
            return url + (url.indexOf(\'?\') === -1 ? \'?\' : \'&\') + string;\n
        }\n
\n
        return url;\n
    },\n
\n
    /**\n
     * Trims whitespace from either end of a string, leaving spaces within the string intact.  Example:\n
     *\n
     *     @example\n
     *     var s = \'  foo bar  \';\n
     *     alert(\'-\' + s + \'-\'); // alerts "-  foo bar  -"\n
     *     alert(\'-\' + Ext.String.trim(s) + \'-\'); // alerts "-foo bar-"\n
     *\n
     * @param {String} string The string to escape\n
     * @return {String} The trimmed string\n
     */\n
    trim: function(string) {\n
        return string.replace(Ext.String.trimRegex, "");\n
    },\n
\n
    /**\n
     * Capitalize the given string.\n
     * @param {String} string\n
     * @return {String}\n
     */\n
    capitalize: function(string) {\n
        return string.charAt(0).toUpperCase() + string.substr(1);\n
    },\n
\n
    /**\n
     * Truncate a string and add an ellipsis (\'...\') to the end if it exceeds the specified length.\n
     * @param {String} value The string to truncate.\n
     * @param {Number} length The maximum length to allow before truncating.\n
     * @param {Boolean} word `true` to try to find a common word break.\n
     * @return {String} The converted text.\n
     */\n
    ellipsis: function(value, len, word) {\n
        if (value && value.length > len) {\n
            if (word) {\n
                var vs = value.substr(0, len - 2),\n
                index = Math.max(vs.lastIndexOf(\' \'), vs.lastIndexOf(\'.\'), vs.lastIndexOf(\'!\'), vs.lastIndexOf(\'?\'));\n
                if (index !== -1 && index >= (len - 15)) {\n
                    return vs.substr(0, index) + "...";\n
                }\n
            }\n
            return value.substr(0, len - 3) + "...";\n
        }\n
        return value;\n
    },\n
\n
    /**\n
     * Escapes the passed string for use in a regular expression.\n
     * @param {String} string\n
     * @return {String}\n
     */\n
    escapeRegex: function(string) {\n
        return string.replace(Ext.String.escapeRegexRe, "\\\\$1");\n
    },\n
\n
    /**\n
     * Escapes the passed string for \' and \\.\n
     * @param {String} string The string to escape.\n
     * @return {String} The escaped string.\n
     */\n
    escape: function(string) {\n
        return string.replace(Ext.String.escapeRe, "\\\\$1");\n
    },\n
\n
    /**\n
     * Utility function that allows you to easily switch a string between two alternating values.  The passed value\n
     * is compared to the current string, and if they are equal, the other value that was passed in is returned.  If\n
     * they are already different, the first value passed in is returned.  Note that this method returns the new value\n
     * but does not change the current string.\n
     *\n
     *     // alternate sort directions\n
     *     sort = Ext.String.toggle(sort, \'ASC\', \'DESC\');\n
     *\n
     *     // instead of conditional logic:\n
     *     sort = (sort == \'ASC\' ? \'DESC\' : \'ASC\');\n
     *\n
     * @param {String} string The current string.\n
     * @param {String} value The value to compare to the current string.\n
     * @param {String} other The new value to use if the string already equals the first value passed in.\n
     * @return {String} The new value.\n
     */\n
    toggle: function(string, value, other) {\n
        return string === value ? other : value;\n
    },\n
\n
    /**\n
     * Pads the left side of a string with a specified character.  This is especially useful\n
     * for normalizing number and date strings.  Example usage:\n
     *\n
     *     var s = Ext.String.leftPad(\'123\', 5, \'0\');\n
     *     alert(s); // \'00123\'\n
     *\n
     * @param {String} string The original string.\n
     * @param {Number} size The total length of the output string.\n
     * @param {String} [character= ] (optional) The character with which to pad the original string (defaults to empty string " ").\n
     * @return {String} The padded string.\n
     */\n
    leftPad: function(string, size, character) {\n
        var result = String(string);\n
        character = character || " ";\n
        while (result.length < size) {\n
            result = character + result;\n
        }\n
        return result;\n
    },\n
\n
    /**\n
     * Allows you to define a tokenized string and pass an arbitrary number of arguments to replace the tokens.  Each\n
     * token must be unique, and must increment in the format {0}, {1}, etc.  Example usage:\n
     *\n
     *     var cls = \'my-class\',\n
     *         text = \'Some text\';\n
     *     var s = Ext.String.format(\'<div class="{0}">{1}</div>\', cls, text);\n
     *     alert(s); // \'<div class="my-class">Some text</div>\'\n
     *\n
     * @param {String} string The tokenized string to be formatted.\n
     * @param {String} value1 The value to replace token {0}.\n
     * @param {String} value2 Etc...\n
     * @return {String} The formatted string.\n
     */\n
    format: function(format) {\n
        var args = Ext.Array.toArray(arguments, 1);\n
        return format.replace(Ext.String.formatRe, function(m, i) {\n
            return args[i];\n
        });\n
    },\n
\n
    /**\n
     * Returns a string with a specified number of repetitions a given string pattern.\n
     * The pattern be separated by a different string.\n
     *\n
     *     var s = Ext.String.repeat(\'---\', 4); // \'------------\'\n
     *     var t = Ext.String.repeat(\'--\', 3, \'/\'); // \'--/--/--\'\n
     *\n
     * @param {String} pattern The pattern to repeat.\n
     * @param {Number} count The number of times to repeat the pattern (may be 0).\n
     * @param {String} sep An option string to separate each pattern.\n
     */\n
    repeat: function(pattern, count, sep) {\n
        for (var buf = [], i = count; i--; ) {\n
            buf.push(pattern);\n
        }\n
        return buf.join(sep || \'\');\n
    }\n
};\n
\n
/**\n
 * Old alias to {@link Ext.String#htmlEncode}.\n
 * @deprecated Use {@link Ext.String#htmlEncode} instead.\n
 * @method\n
 * @member Ext\n
 * @alias Ext.String#htmlEncode\n
 */\n
Ext.htmlEncode = Ext.String.htmlEncode;\n
\n
\n
/**\n
 * Old alias to {@link Ext.String#htmlDecode}.\n
 * @deprecated Use {@link Ext.String#htmlDecode} instead.\n
 * @method\n
 * @member Ext\n
 * @alias Ext.String#htmlDecode\n
 */\n
Ext.htmlDecode = Ext.String.htmlDecode;\n
\n
/**\n
 * Old alias to {@link Ext.String#urlAppend}.\n
 * @deprecated Use {@link Ext.String#urlAppend} instead.\n
 * @method\n
 * @member Ext\n
 * @alias Ext.String#urlAppend\n
 */\n
Ext.urlAppend = Ext.String.urlAppend;\n
\n
//@tag foundation,core\n
//@define Ext.Array\n
//@require Ext.String\n
\n
/**\n
 * @class Ext.Array\n
 * @singleton\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @docauthor Jacky Nguyen <jacky@sencha.com>\n
 *\n
 * A set of useful static methods to deal with arrays; provide missing methods for older browsers.\n
 */\n
(function() {\n
\n
    var arrayPrototype = Array.prototype,\n
        slice = arrayPrototype.slice,\n
        supportsSplice = function () {\n
            var array = [],\n
                lengthBefore,\n
                j = 20;\n
\n
            if (!array.splice) {\n
                return false;\n
            }\n
\n
            // This detects a bug in IE8 splice method:\n
            // see http://social.msdn.microsoft.com/Forums/en-US/iewebdevelopment/thread/6e946d03-e09f-4b22-a4dd-cd5e276bf05a/\n
\n
            while (j--) {\n
                array.push("A");\n
            }\n
\n
            array.splice(15, 0, "F", "F", "F", "F", "F","F","F","F","F","F","F","F","F","F","F","F","F","F","F","F","F");\n
\n
            lengthBefore = array.length; //41\n
            array.splice(13, 0, "XXX"); // add one element\n
\n
            if (lengthBefore+1 != array.length) {\n
                return false;\n
            }\n
            // end IE8 bug\n
\n
            return true;\n
        }(),\n
        supportsForEach = \'forEach\' in arrayPrototype,\n
        supportsMap = \'map\' in arrayPrototype,\n
        supportsIndexOf = \'indexOf\' in arrayPrototype,\n
        supportsEvery = \'every\' in arrayPrototype,\n
        supportsSome = \'some\' in arrayPrototype,\n
        supportsFilter = \'filter\' in arrayPrototype,\n
        supportsSort = function() {\n
            var a = [1,2,3,4,5].sort(function(){ return 0; });\n
            return a[0] === 1 && a[1] === 2 && a[2] === 3 && a[3] === 4 && a[4] === 5;\n
        }(),\n
        supportsSliceOnNodeList = true,\n
        ExtArray;\n
\n
    try {\n
        // IE 6 - 8 will throw an error when using Array.prototype.slice on NodeList\n
        if (typeof document !== \'undefined\') {\n
            slice.call(document.getElementsByTagName(\'body\'));\n
        }\n
    } catch (e) {\n
        supportsSliceOnNodeList = false;\n
    }\n
\n
    function fixArrayIndex (array, index) {\n
        return (index < 0) ? Math.max(0, array.length + index)\n
                           : Math.min(array.length, index);\n
    }\n
\n
    /*\n
    Does the same work as splice, but with a slightly more convenient signature. The splice\n
    method has bugs in IE8, so this is the implementation we use on that platform.\n
\n
    The rippling of items in the array can be tricky. Consider two use cases:\n
\n
                  index=2\n
                  removeCount=2\n
                 /=====\\\n
        +---+---+---+---+---+---+---+---+\n
        | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |\n
        +---+---+---+---+---+---+---+---+\n
                         /  \\/  \\/  \\/  \\\n
                        /   /\\  /\\  /\\   \\\n
                       /   /  \\/  \\/  \\   +--------------------------+\n
                      /   /   /\\  /\\   +--------------------------+   \\\n
                     /   /   /  \\/  +--------------------------+   \\   \\\n
                    /   /   /   /+--------------------------+   \\   \\   \\\n
                   /   /   /   /                             \\   \\   \\   \\\n
                  v   v   v   v                               v   v   v   v\n
        +---+---+---+---+---+---+       +---+---+---+---+---+---+---+---+---+\n
        | 0 | 1 | 4 | 5 | 6 | 7 |       | 0 | 1 | a | b | c | 4 | 5 | 6 | 7 |\n
        +---+---+---+---+---+---+       +---+---+---+---+---+---+---+---+---+\n
        A                               B        \\=========/\n
                                                 insert=[a,b,c]\n
\n
    In case A, it is obvious that copying of [4,5,6,7] must be left-to-right so\n
    that we don\'t end up with [0,1,6,7,6,7]. In case B, we have the opposite; we\n
    must go right-to-left or else we would end up with [0,1,a,b,c,4,4,4,4].\n
    */\n
    function replaceSim (array, index, removeCount, insert) {\n
        var add = insert ? insert.length : 0,\n
            length = array.length,\n
            pos = fixArrayIndex(array, index);\n
\n
        // we try to use Array.push when we can for efficiency...\n
        if (pos === length) {\n
            if (add) {\n
                array.push.apply(array, insert);\n
            }\n
        } else {\n
            var remove = Math.min(removeCount, length - pos),\n
                tailOldPos = pos + remove,\n
                tailNewPos = tailOldPos + add - remove,\n
                tailCount = length - tailOldPos,\n
                lengthAfterRemove = length - remove,\n
                i;\n
\n
            if (tailNewPos < tailOldPos) { // case A\n
                for (i = 0; i < tailCount; ++i) {\n
                    array[tailNewPos+i] = array[tailOldPos+i];\n
                }\n
            } else if (tailNewPos > tailOldPos) { // case B\n
                for (i = tailCount; i--; ) {\n
                    array[tailNewPos+i] = array[tailOldPos+i];\n
                }\n
            } // else, add == remove (nothing to do)\n
\n
            if (add && pos === lengthAfterRemove) {\n
                array.length = lengthAfterRemove; // truncate array\n
                array.push.apply(array, insert);\n
            } else {\n
                array.length = lengthAfterRemove + add; // reserves space\n
                for (i = 0; i < add; ++i) {\n
                    array[pos+i] = insert[i];\n
                }\n
            }\n
        }\n
\n
        return array;\n
    }\n
\n
    function replaceNative (array, index, removeCount, insert) {\n
        if (insert && insert.length) {\n
            if (index < array.length) {\n
                array.splice.apply(array, [index, removeCount].concat(insert));\n
            } else {\n
                array.push.apply(array, insert);\n
            }\n
        } else {\n
            array.splice(index, removeCount);\n
        }\n
        return array;\n
    }\n
\n
    function eraseSim (array, index, removeCount) {\n
        return replaceSim(array, index, removeCount);\n
    }\n
\n
    function eraseNative (array, index, removeCount) {\n
        array.splice(index, removeCount);\n
        return array;\n
    }\n
\n
    function spliceSim (array, index, removeCount) {\n
        var pos = fixArrayIndex(array, index),\n
            removed = array.slice(index, fixArrayIndex(array, pos+removeCount));\n
\n
        if (arguments.length < 4) {\n
            replaceSim(array, pos, removeCount);\n
        } else {\n
            replaceSim(array, pos, removeCount, slice.call(arguments, 3));\n
        }\n
\n
        return removed;\n
    }\n
\n
    function spliceNative (array) {\n
        return array.splice.apply(array, slice.call(arguments, 1));\n
    }\n
\n
    var erase = supportsSplice ? eraseNative : eraseSim,\n
        replace = supportsSplice ? replaceNative : replaceSim,\n
        splice = supportsSplice ? spliceNative : spliceSim;\n
\n
    // NOTE: from here on, use erase, replace or splice (not native methods)...\n
    ExtArray = Ext.Array = {\n
        /**\n
         * Iterates an array or an iterable value and invoke the given callback function for each item.\n
         *\n
         *     var countries = [\'Vietnam\', \'Singapore\', \'United States\', \'Russia\'];\n
         *\n
         *     Ext.Array.each(countries, function(name, index, countriesItSelf) {\n
         *         console.log(name);\n
         *     });\n
         *\n
         *     var sum = function() {\n
         *         var sum = 0;\n
         *\n
         *         Ext.Array.each(arguments, function(value) {\n
         *             sum += value;\n
         *         });\n
         *\n
         *         return sum;\n
         *     };\n
         *\n
         *     sum(1, 2, 3); // returns 6\n
         *\n
         * The iteration can be stopped by returning false in the function callback.\n
         *\n
         *     Ext.Array.each(countries, function(name, index, countriesItSelf) {\n
         *         if (name === \'Singapore\') {\n
         *             return false; // break here\n
         *         }\n
         *     });\n
         *\n
         * {@link Ext#each Ext.each} is alias for {@link Ext.Array#each Ext.Array.each}\n
         *\n
         * @param {Array/NodeList/Object} iterable The value to be iterated. If this\n
         * argument is not iterable, the callback function is called once.\n
         * @param {Function} fn The callback function. If it returns `false`, the iteration stops and this method returns\n
         * the current `index`.\n
         * @param {Object} fn.item The item at the current `index` in the passed `array`\n
         * @param {Number} fn.index The current `index` within the `array`\n
         * @param {Array} fn.allItems The `array` itself which was passed as the first argument\n
         * @param {Boolean} fn.return Return false to stop iteration.\n
         * @param {Object} scope (Optional) The scope (`this` reference) in which the specified function is executed.\n
         * @param {Boolean} [reverse=false] (Optional) Reverse the iteration order (loop from the end to the beginning).\n
         * @return {Boolean} See description for the `fn` parameter.\n
         */\n
        each: function(array, fn, scope, reverse) {\n
            array = ExtArray.from(array);\n
\n
            var i,\n
                ln = array.length;\n
\n
            if (reverse !== true) {\n
                for (i = 0; i < ln; i++) {\n
                    if (fn.call(scope || array[i], array[i], i, array) === false) {\n
                        return i;\n
                    }\n
                }\n
            }\n
            else {\n
                for (i = ln - 1; i > -1; i--) {\n
                    if (fn.call(scope || array[i], array[i], i, array) === false) {\n
                        return i;\n
                    }\n
                }\n
            }\n
\n
            return true;\n
        },\n
\n
        /**\n
         * Iterates an array and invoke the given callback function for each item. Note that this will simply\n
         * delegate to the native `Array.prototype.forEach` method if supported. It doesn\'t support stopping the\n
         * iteration by returning `false` in the callback function like {@link Ext.Array#each}. However, performance\n
         * could be much better in modern browsers comparing with {@link Ext.Array#each}\n
         *\n
         * @param {Array} array The array to iterate.\n
         * @param {Function} fn The callback function.\n
         * @param {Object} fn.item The item at the current `index` in the passed `array`.\n
         * @param {Number} fn.index The current `index` within the `array`.\n
         * @param {Array}  fn.allItems The `array` itself which was passed as the first argument.\n
         * @param {Object} scope (Optional) The execution scope (`this`) in which the specified function is executed.\n
         */\n
        forEach: supportsForEach ? function(array, fn, scope) {\n
                return array.forEach(fn, scope);\n
        } : function(array, fn, scope) {\n
            var i = 0,\n
                ln = array.length;\n
\n
            for (; i < ln; i++) {\n
                fn.call(scope, array[i], i, array);\n
            }\n
        },\n
\n
        /**\n
         * Get the index of the provided `item` in the given `array`, a supplement for the\n
         * missing arrayPrototype.indexOf in Internet Explorer.\n
         *\n
         * @param {Array} array The array to check.\n
         * @param {Object} item The item to look for.\n
         * @param {Number} from (Optional) The index at which to begin the search.\n
         * @return {Number} The index of item in the array (or -1 if it is not found).\n
         */\n
        indexOf: (supportsIndexOf) ? function(array, item, from) {\n
            return array.indexOf(item, from);\n
        } : function(array, item, from) {\n
            var i, length = array.length;\n
\n
            for (i = (from < 0) ? Math.max(0, length + from) : from || 0; i < length; i++) {\n
                if (array[i] === item) {\n
                    return i;\n
                }\n
            }\n
\n
            return -1;\n
        },\n
\n
        /**\n
         * Checks whether or not the given `array` contains the specified `item`.\n
         *\n
         * @param {Array} array The array to check.\n
         * @param {Object} item The item to look for.\n
         * @return {Boolean} `true` if the array contains the item, `false` otherwise.\n
         */\n
        contains: supportsIndexOf ? function(array, item) {\n
            return array.indexOf(item) !== -1;\n
        } : function(array, item) {\n
            var i, ln;\n
\n
            for (i = 0, ln = array.length; i < ln; i++) {\n
                if (array[i] === item) {\n
                    return true;\n
                }\n
            }\n
\n
            return false;\n
        },\n
\n
        /**\n
         * Converts any iterable (numeric indices and a length property) into a true array.\n
         *\n
         *     function test() {\n
         *         var args = Ext.Array.toArray(arguments),\n
         *             fromSecondToLastArgs = Ext.Array.toArray(arguments, 1);\n
         *\n
         *         alert(args.join(\' \'));\n
         *         alert(fromSecondToLastArgs.join(\' \'));\n
         *     }\n
         *\n
         *     test(\'just\', \'testing\', \'here\'); // alerts \'just testing here\';\n
         *                                      // alerts \'testing here\';\n
         *\n
         *     Ext.Array.toArray(document.getElementsByTagName(\'div\')); // will convert the NodeList into an array\n
         *     Ext.Array.toArray(\'splitted\'); // returns [\'s\', \'p\', \'l\', \'i\', \'t\', \'t\', \'e\', \'d\']\n
         *     Ext.Array.toArray(\'splitted\', 0, 3); // returns [\'s\', \'p\', \'l\', \'i\']\n
         *\n
         * {@link Ext#toArray Ext.toArray} is alias for {@link Ext.Array#toArray Ext.Array.toArray}\n
         *\n
         * @param {Object} iterable the iterable object to be turned into a true Array.\n
         * @param {Number} [start=0] (Optional) a zero-based index that specifies the start of extraction.\n
         * @param {Number} [end=-1] (Optional) a zero-based index that specifies the end of extraction.\n
         * @return {Array}\n
         */\n
        toArray: function(iterable, start, end){\n
            if (!iterable || !iterable.length) {\n
                return [];\n
            }\n
\n
            if (typeof iterable === \'string\') {\n
                iterable = iterable.split(\'\');\n
            }\n
\n
            if (supportsSliceOnNodeList) {\n
                return slice.call(iterable, start || 0, end || iterable.length);\n
            }\n
\n
            var array = [],\n
                i;\n
\n
            start = start || 0;\n
            end = end ? ((end < 0) ? iterable.length + end : end) : iterable.length;\n
\n
            for (i = start; i < end; i++) {\n
                array.push(iterable[i]);\n
            }\n
\n
            return array;\n
        },\n
\n
        /**\n
         * Plucks the value of a property from each item in the Array. Example:\n
         *\n
         *     Ext.Array.pluck(Ext.query("p"), "className"); // [el1.className, el2.className, ..., elN.className]\n
         *\n
         * @param {Array/NodeList} array The Array of items to pluck the value from.\n
         * @param {String} propertyName The property name to pluck from each element.\n
         * @return {Array} The value from each item in the Array.\n
         */\n
        pluck: function(array, propertyName) {\n
            var ret = [],\n
                i, ln, item;\n
\n
            for (i = 0, ln = array.length; i < ln; i++) {\n
                item = array[i];\n
\n
                ret.push(item[propertyName]);\n
            }\n
\n
            return ret;\n
        },\n
\n
        /**\n
         * Creates a new array with the results of calling a provided function on every element in this array.\n
         *\n
         * @param {Array} array\n
         * @param {Function} fn Callback function for each item.\n
         * @param {Object} scope Callback function scope.\n
         * @return {Array} results\n
         */\n
        map: supportsMap ? function(array, fn, scope) {\n
            return array.map(fn, scope);\n
        } : function(array, fn, scope) {\n
            var results = [],\n
                i = 0,\n
                len = array.length;\n
\n
            for (; i < len; i++) {\n
                results[i] = fn.call(scope, array[i], i, array);\n
            }\n
\n
            return results;\n
        },\n
\n
        /**\n
         * Executes the specified function for each array element until the function returns a falsy value.\n
         * If such an item is found, the function will return `false` immediately.\n
         * Otherwise, it will return `true`.\n
         *\n
         * @param {Array} array\n
         * @param {Function} fn Callback function for each item.\n
         * @param {Object} scope Callback function scope.\n
         * @return {Boolean} `true` if no `false` value is returned by the callback function.\n
         */\n
        every: function(array, fn, scope) {\n
            //<debug>\n
            if (!fn) {\n
                Ext.Error.raise(\'Ext.Array.every must have a callback function passed as second argument.\');\n
            }\n
            //</debug>\n
            if (supportsEvery) {\n
                return array.every(fn, scope);\n
            }\n
\n
            var i = 0,\n
                ln = array.length;\n
\n
            for (; i < ln; ++i) {\n
                if (!fn.call(scope, array[i], i, array)) {\n
                    return false;\n
                }\n
            }\n
\n
            return true;\n
        },\n
\n
        /**\n
         * Executes the specified function for each array element until the function returns a truthy value.\n
         * If such an item is found, the function will return `true` immediately. Otherwise, it will return `false`.\n
         *\n
         * @param {Array} array\n
         * @param {Function} fn Callback function for each item.\n
         * @param {Object} scope Callback function scope.\n
         * @return {Boolean} `true` if the callback function returns a truthy value.\n
         */\n
        some: function(array, fn, scope) {\n
            //<debug>\n
            if (!fn) {\n
                Ext.Error.raise(\'Ext.Array.some must have a callback function passed as second argument.\');\n
            }\n
            //</debug>\n
            if (supportsSome) {\n
                return array.some(fn, scope);\n
            }\n
\n
            var i = 0,\n
                ln = array.length;\n
\n
            for (; i < ln; ++i) {\n
                if (fn.call(scope, array[i], i, array)) {\n
                    return true;\n
                }\n
            }\n
\n
            return false;\n
        },\n
\n
        /**\n
         * Filter through an array and remove empty item as defined in {@link Ext#isEmpty Ext.isEmpty}.\n
         *\n
         * See {@link Ext.Array#filter}\n
         *\n
         * @param {Array} array\n
         * @return {Array} results\n
         */\n
        clean: function(array) {\n
            var results = [],\n
                i = 0,\n
                ln = array.length,\n
                item;\n
\n
            for (; i < ln; i++) {\n
                item = array[i];\n
\n
                if (!Ext.isEmpty(item)) {\n
                    results.push(item);\n
                }\n
            }\n
\n
            return results;\n
        },\n
\n
        /**\n
         * Returns a new array with unique items.\n
         *\n
         * @param {Array} array\n
         * @return {Array} results\n
         */\n
        unique: function(array) {\n
            var clone = [],\n
                i = 0,\n
                ln = array.length,\n
                item;\n
\n
            for (; i < ln; i++) {\n
                item = array[i];\n
\n
                if (ExtArray.indexOf(clone, item) === -1) {\n
                    clone.push(item);\n
                }\n
            }\n
\n
            return clone;\n
        },\n
\n
        /**\n
         * Creates a new array with all of the elements of this array for which\n
         * the provided filtering function returns `true`.\n
         *\n
         * @param {Array} array\n
         * @param {Function} fn Callback function for each item.\n
         * @param {Object} scope Callback function scope.\n
         * @return {Array} results\n
         */\n
        filter: function(array, fn, scope) {\n
            if (supportsFilter) {\n
                return array.filter(fn, scope);\n
            }\n
\n
            var results = [],\n
                i = 0,\n
                ln = array.length;\n
\n
            for (; i < ln; i++) {\n
                if (fn.call(scope, array[i], i, array)) {\n
                    results.push(array[i]);\n
                }\n
            }\n
\n
            return results;\n
        },\n
\n
        /**\n
         * Converts a value to an array if it\'s not already an array; returns:\n
         *\n
         * - An empty array if given value is `undefined` or `null`\n
         * - Itself if given value is already an array\n
         * - An array copy if given value is {@link Ext#isIterable iterable} (arguments, NodeList and alike)\n
         * - An array with one item which is the given value, otherwise\n
         *\n
         * @param {Object} value The value to convert to an array if it\'s not already is an array.\n
         * @param {Boolean} [newReference=false] (Optional) `true` to clone the given array and return a new reference if necessary.\n
         * @return {Array} array\n
         */\n
        from: function(value, newReference) {\n
            if (value === undefined || value === null) {\n
                return [];\n
            }\n
\n
            if (Ext.isArray(value)) {\n
                return (newReference) ? slice.call(value) : value;\n
            }\n
\n
            if (value && value.length !== undefined && typeof value !== \'string\') {\n
                return ExtArray.toArray(value);\n
            }\n
\n
            return [value];\n
        },\n
\n
        /**\n
         * Removes the specified item from the array if it exists.\n
         *\n
         * @param {Array} array The array.\n
         * @param {Object} item The item to remove.\n
         * @return {Array} The passed array itself.\n
         */\n
        remove: function(array, item) {\n
            var index = ExtArray.indexOf(array, item);\n
\n
            if (index !== -1) {\n
                erase(array, index, 1);\n
            }\n
\n
            return array;\n
        },\n
\n
        /**\n
         * Push an item into the array only if the array doesn\'t contain it yet.\n
         *\n
         * @param {Array} array The array.\n
         * @param {Object} item The item to include.\n
         */\n
        include: function(array, item) {\n
            if (!ExtArray.contains(array, item)) {\n
                array.push(item);\n
            }\n
        },\n
\n
        /**\n
         * Clone a flat array without referencing the previous one. Note that this is different\n
         * from `Ext.clone` since it doesn\'t handle recursive cloning. It\'s simply a convenient, easy-to-remember method\n
         * for `Array.prototype.slice.call(array)`.\n
         *\n
         * @param {Array} array The array\n
         * @return {Array} The clone array\n
         */\n
        clone: function(array) {\n
            return slice.call(array);\n
        },\n
\n
        /**\n
         * Merge multiple arrays into one with unique items.\n
         *\n
         * {@link Ext.Array#union} is alias for {@link Ext.Array#merge}\n
         *\n
         * @param {Array} array1\n
         * @param {Array} array2\n
         * @param {Array} etc\n
         * @return {Array} merged\n
         */\n
        merge: function() {\n
            var args = slice.call(arguments),\n
                array = [],\n
                i, ln;\n
\n
            for (i = 0, ln = args.length; i < ln; i++) {\n
                array = array.concat(args[i]);\n
            }\n
\n
            return ExtArray.unique(array);\n
        },\n
\n
        /**\n
         * Merge multiple arrays into one with unique items that exist in all of the arrays.\n
         *\n
         * @param {Array} array1\n
         * @param {Array} array2\n
         * @param {Array} etc\n
         * @return {Array} intersect\n
         */\n
        intersect: function() {\n
            var intersect = [],\n
                arrays = slice.call(arguments),\n
                i, j, k, minArray, array, x, y, ln, arraysLn, arrayLn;\n
\n
            if (!arrays.length) {\n
                return intersect;\n
            }\n
\n
            // Find the smallest array\n
            for (i = x = 0,ln = arrays.length; i < ln,array = arrays[i]; i++) {\n
                if (!minArray || array.length < minArray.length) {\n
                    minArray = array;\n
                    x = i;\n
                }\n
            }\n
\n
            minArray = ExtArray.unique(minArray);\n
            erase(arrays, x, 1);\n
\n
            // Use the smallest unique\'d array as the anchor loop. If the other array(s) do contain\n
            // an item in the small array, we\'re likely to find it before reaching the end\n
            // of the inner loop and can terminate the search early.\n
            for (i = 0,ln = minArray.length; i < ln,x = minArray[i]; i++) {\n
                var count = 0;\n
\n
                for (j = 0,arraysLn = arrays.length; j < arraysLn,array = arrays[j]; j++) {\n
                    for (k = 0,arrayLn = array.length; k < arrayLn,y = array[k]; k++) {\n
                        if (x === y) {\n
                            count++;\n
                            break;\n
                        }\n
                    }\n
                }\n
\n
                if (count === arraysLn) {\n
                    intersect.push(x);\n
                }\n
            }\n
\n
            return intersect;\n
        },\n
\n
        /**\n
         * Perform a set difference A-B by subtracting all items in array B from array A.\n
         *\n
         * @param {Array} arrayA\n
         * @param {Array} arrayB\n
         * @return {Array} difference\n
         */\n
        difference: function(arrayA, arrayB) {\n
            var clone = slice.call(arrayA),\n
                ln = clone.length,\n
                i, j, lnB;\n
\n
            for (i = 0,lnB = arrayB.length; i < lnB; i++) {\n
                for (j = 0; j < ln; j++) {\n
                    if (clone[j] === arrayB[i]) {\n
                        erase(clone, j, 1);\n
                        j--;\n
                        ln--;\n
                    }\n
                }\n
            }\n
\n
            return clone;\n
        },\n
\n
        /**\n
         * Returns a shallow copy of a part of an array. This is equivalent to the native\n
         * call `Array.prototype.slice.call(array, begin, end)`. This is often used when "array"\n
         * is "arguments" since the arguments object does not supply a slice method but can\n
         * be the context object to `Array.prototype.slice()`.\n
         *\n
         * @param {Array} array The array (or arguments object).\n
         * @param {Number} begin The index at which to begin. Negative values are offsets from\n
         * the end of the array.\n
         * @param {Number} end The index at which to end. The copied items do not include\n
         * end. Negative values are offsets from the end of the array. If end is omitted,\n
         * all items up to the end of the array are copied.\n
         * @return {Array} The copied piece of the array.\n
         */\n
        slice: function(array, begin, end) {\n
            return slice.call(array, begin, end);\n
        },\n
\n
        /**\n
         * Sorts the elements of an Array.\n
         * By default, this method sorts the elements alphabetically and ascending.\n
         *\n
         * @param {Array} array The array to sort.\n
         * @param {Function} sortFn (optional) The comparison function.\n
         * @return {Array} The sorted array.\n
         */\n
        sort: function(array, sortFn) {\n
            if (supportsSort) {\n
                if (sortFn) {\n
                    return array.sort(sortFn);\n
                } else {\n
                    return array.sort();\n
                }\n
            }\n
\n
            var length = array.length,\n
                i = 0,\n
                comparison,\n
                j, min, tmp;\n
\n
            for (; i < length; i++) {\n
                min = i;\n
                for (j = i + 1; j < length; j++) {\n
                    if (sortFn) {\n
                        comparison = sortFn(array[j], array[min]);\n
                        if (comparison < 0) {\n
                            min = j;\n
                        }\n
                    } else if (array[j] < array[min]) {\n
                        min = j;\n
                    }\n
                }\n
                if (min !== i) {\n
                    tmp = array[i];\n
                    array[i] = array[min];\n
                    array[min] = tmp;\n
                }\n
            }\n
\n
            return array;\n
        },\n
\n
        /**\n
         * Recursively flattens into 1-d Array. Injects Arrays inline.\n
         *\n
         * @param {Array} array The array to flatten\n
         * @return {Array} The 1-d array.\n
         */\n
        flatten: function(array) {\n
            var worker = [];\n
\n
            function rFlatten(a) {\n
                var i, ln, v;\n
\n
                for (i = 0, ln = a.length; i < ln; i++) {\n
                    v = a[i];\n
\n
                    if (Ext.isArray(v)) {\n
                        rFlatten(v);\n
                    } else {\n
                        worker.push(v);\n
                    }\n
                }\n
\n
                return worker;\n
            }\n
\n
            return rFlatten(array);\n
        },\n
\n
        /**\n
         * Returns the minimum value in the Array.\n
         *\n
         * @param {Array/NodeList} array The Array from which to select the minimum value.\n
         * @param {Function} comparisonFn (optional) a function to perform the comparison which determines minimization.\n
         * If omitted the "<" operator will be used.\n
         * __Note:__ gt = 1; eq = 0; lt = -1\n
         * @return {Object} minValue The minimum value.\n
         */\n
        min: function(array, comparisonFn) {\n
            var min = array[0],\n
                i, ln, item;\n
\n
            for (i = 0, ln = array.length; i < ln; i++) {\n
                item = array[i];\n
\n
                if (comparisonFn) {\n
                    if (comparisonFn(min, item) === 1) {\n
                        min = item;\n
                    }\n
                }\n
                else {\n
                    if (item < min) {\n
                        min = item;\n
                    }\n
                }\n
            }\n
\n
            return min;\n
        },\n
\n
        /**\n
         * Returns the maximum value in the Array.\n
         *\n
         * @param {Array/NodeList} array The Array from which to select the maximum value.\n
         * @param {Function} comparisonFn (optional) a function to perform the comparison which determines maximization.\n
         * If omitted the ">" operator will be used.\n
         * __Note:__ gt = 1; eq = 0; lt = -1\n
         * @return {Object} maxValue The maximum value\n
         */\n
        max: function(array, comparisonFn) {\n
            var max = array[0],\n
                i, ln, item;\n
\n
            for (i = 0, ln = array.length; i < ln; i++) {\n
                item = array[i];\n
\n
                if (comparisonFn) {\n
                    if (comparisonFn(max, item) === -1) {\n
                        max = item;\n
                    }\n
                }\n
                else {\n
                    if (item > max) {\n
                        max = item;\n
                    }\n
                }\n
            }\n
\n
            return max;\n
        },\n
\n
        /**\n
         * Calculates the mean of all items in the array.\n
         *\n
         * @param {Array} array The Array to calculate the mean value of.\n
         * @return {Number} The mean.\n
         */\n
        mean: function(array) {\n
            return array.length > 0 ? ExtArray.sum(array) / array.length : undefined;\n
        },\n
\n
        /**\n
         * Calculates the sum of all items in the given array.\n
         *\n
         * @param {Array} array The Array to calculate the sum value of.\n
         * @return {Number} The sum.\n
         */\n
        sum: function(array) {\n
            var sum = 0,\n
                i, ln, item;\n
\n
            for (i = 0,ln = array.length; i < ln; i++) {\n
                item = array[i];\n
\n
                sum += item;\n
            }\n
\n
            return sum;\n
        },\n
\n
        //<debug>\n
        _replaceSim: replaceSim, // for unit testing\n
        _spliceSim: spliceSim,\n
        //</debug>\n
\n
        /**\n
         * Removes items from an array. This is functionally equivalent to the splice method\n
         * of Array, but works around bugs in IE8\'s splice method and does not copy the\n
         * removed elements in order to return them (because very often they are ignored).\n
         *\n
         * @param {Array} array The Array on which to replace.\n
         * @param {Number} index The index in the array at which to operate.\n
         * @param {Number} removeCount The number of items to remove at index.\n
         * @return {Array} The array passed.\n
         * @method\n
         */\n
        erase: erase,\n
\n
        /**\n
         * Inserts items in to an array.\n
         *\n
         * @param {Array} array The Array on which to replace.\n
         * @param {Number} index The index in the array at which to operate.\n
         * @param {Array} items The array of items to insert at index.\n
         * @return {Array} The array passed.\n
         */\n
        insert: function (array, index, items) {\n
            return replace(array, index, 0, items);\n
        },\n
\n
        /**\n
         * Replaces items in an array. This is functionally equivalent to the splice method\n
         * of Array, but works around bugs in IE8\'s splice method and is often more convenient\n
         * to call because it accepts an array of items to insert rather than use a variadic\n
         * argument list.\n
         *\n
         * @param {Array} array The Array on which to replace.\n
         * @param {Number} index The index in the array at which to operate.\n
         * @param {Number} removeCount The number of items to remove at index (can be 0).\n
         * @param {Array} insert (optional) An array of items to insert at index.\n
         * @return {Array} The array passed.\n
         * @method\n
         */\n
        replace: replace,\n
\n
        /**\n
         * Replaces items in an array. This is equivalent to the splice method of Array, but\n
         * works around bugs in IE8\'s splice method. The signature is exactly the same as the\n
         * splice method except that the array is the first argument. All arguments following\n
         * removeCount are inserted in the array at index.\n
         *\n
         * @param {Array} array The Array on which to replace.\n
         * @param {Number} index The index in the array at which to operate.\n
         * @param {Number} removeCount The number of items to remove at index (can be 0).\n
         * @return {Array} An array containing the removed items.\n
         * @method\n
         */\n
        splice: splice\n
    };\n
\n
    /**\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#each\n
     */\n
    Ext.each = ExtArray.each;\n
\n
    /**\n
     * @method\n
     * @member Ext.Array\n
     * @alias Ext.Array#merge\n
     */\n
    ExtArray.union = ExtArray.merge;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#min}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#min} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#min\n
     */\n
    Ext.min = ExtArray.min;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#max}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#max} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#max\n
     */\n
    Ext.max = ExtArray.max;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#sum}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#sum} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#sum\n
     */\n
    Ext.sum = ExtArray.sum;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#mean}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#mean} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#mean\n
     */\n
    Ext.mean = ExtArray.mean;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#flatten}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#flatten} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#flatten\n
     */\n
    Ext.flatten = ExtArray.flatten;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#clean}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#clean} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#clean\n
     */\n
    Ext.clean = ExtArray.clean;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#unique}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#unique} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#unique\n
     */\n
    Ext.unique = ExtArray.unique;\n
\n
    /**\n
     * Old alias to {@link Ext.Array#pluck Ext.Array.pluck}\n
     * @deprecated 4.0.0 Please use {@link Ext.Array#pluck Ext.Array.pluck} instead\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#pluck\n
     */\n
    Ext.pluck = ExtArray.pluck;\n
\n
    /**\n
     * @method\n
     * @member Ext\n
     * @alias Ext.Array#toArray\n
     */\n
    Ext.toArray = function() {\n
        return ExtArray.toArray.apply(ExtArray, arguments);\n
    };\n
})();\n
\n
//@tag foundation,core\n
//@define Ext.Number\n
//@require Ext.Array\n
\n
/**\n
 * @class Ext.Number\n
 *\n
 * A collection of useful static methods to deal with numbers\n
 * @singleton\n
 */\n
\n
(function() {\n
\n
var isToFixedBroken = (0.9).toFixed() !== \'1\';\n
\n
Ext.Number = {\n
    /**\n
     * Checks whether or not the passed number is within a desired range.  If the number is already within the\n
     * range it is returned, otherwise the min or max value is returned depending on which side of the range is\n
     * exceeded. Note that this method returns the constrained value but does not change the current number.\n
     * @param {Number} number The number to check\n
     * @param {Number} min The minimum number in the range\n
     * @param {Number} max The maximum number in the range\n
     * @return {Number} The constrained value if outside the range, otherwise the current value\n
     */\n
    constrain: function(number, min, max) {\n
        number = parseFloat(number);\n
\n
        if (!isNaN(min)) {\n
            number = Math.max(number, min);\n
        }\n
        if (!isNaN(max)) {\n
            number = Math.min(number, max);\n
        }\n
        return number;\n
    },\n
\n
    /**\n
     * Snaps the passed number between stopping points based upon a passed increment value.\n
     * @param {Number} value The unsnapped value.\n
     * @param {Number} increment The increment by which the value must move.\n
     * @param {Number} minValue The minimum value to which the returned value must be constrained. Overrides the increment..\n
     * @param {Number} maxValue The maximum value to which the returned value must be constrained. Overrides the increment..\n
     * @return {Number} The value of the nearest snap target.\n
     */\n
    snap : function(value, increment, minValue, maxValue) {\n
        var newValue = value,\n
            m;\n
\n
        if (!(increment && value)) {\n
            return value;\n
        }\n
        m = value % increment;\n
        if (m !== 0) {\n
            newValue -= m;\n
            if (m * 2 >= increment) {\n
                newValue += increment;\n
            } else if (m * 2 < -increment) {\n
                newValue -= increment;\n
            }\n
        }\n
        return Ext.Number.constrain(newValue, minValue,  maxValue);\n
    },\n
\n
    /**\n
     * Formats a number using fixed-point notation\n
     * @param {Number} value The number to format\n
     * @param {Number} precision The number of digits to show after the decimal point\n
     */\n
    toFixed: function(value, precision) {\n
        if (isToFixedBroken) {\n
            precision = precision || 0;\n
            var pow = Math.pow(10, precision);\n
            return (Math.round(value * pow) / pow).toFixed(precision);\n
        }\n
\n
        return value.toFixed(precision);\n
    },\n
\n
    /**\n
     * Validate that a value is numeric and convert it to a number if necessary. Returns the specified default value if\n
     * it is not.\n
\n
Ext.Number.from(\'1.23\', 1); // returns 1.23\n
Ext.Number.from(\'abc\', 1); // returns 1\n
\n
     * @param {Object} value\n
     * @param {Number} defaultValue The value to return if the original value is non-numeric\n
     * @return {Number} value, if numeric, defaultValue otherwise\n
     */\n
    from: function(value, defaultValue) {\n
        if (isFinite(value)) {\n
            value = parseFloat(value);\n
        }\n
\n
        return !isNaN(value) ? value : defaultValue;\n
    }\n
};\n
\n
})();\n
\n
/**\n
 * This method is deprecated, please use {@link Ext.Number#from Ext.Number.from} instead\n
 *\n
 * @deprecated 4.0.0 Replaced by Ext.Number.from\n
 * @member Ext\n
 * @method num\n
 */\n
Ext.num = function() {\n
    return Ext.Number.from.apply(this, arguments);\n
};\n
\n
//@tag foundation,core\n
//@define Ext.Object\n
//@require Ext.Number\n
\n
/**\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @docauthor Jacky Nguyen <jacky@sencha.com>\n
 * @class Ext.Object\n
 *\n
 * A collection of useful static methods to deal with objects.\n
 *\n
 * @singleton\n
 */\n
\n
(function() {\n
\n
// The "constructor" for chain:\n
var TemplateClass = function(){};\n
\n
var ExtObject = Ext.Object = {\n
\n
    /**\n
     * Returns a new object with the given object as the prototype chain.\n
     * @param {Object} object The prototype chain for the new object.\n
     */\n
    chain: (\'create\' in Object) ? function(object){\n
        return Object.create(object);\n
    } : function (object) {\n
        TemplateClass.prototype = object;\n
        var result = new TemplateClass();\n
        TemplateClass.prototype = null;\n
        return result;\n
    },\n
\n
    /**\n
     * Convert a `name` - `value` pair to an array of objects with support for nested structures; useful to construct\n
     * query strings. For example:\n
     *\n
     * Non-recursive:\n
     *\n
     *     var objects = Ext.Object.toQueryObjects(\'hobbies\', [\'reading\', \'cooking\', \'swimming\']);\n
     *\n
     *     // objects then equals:\n
     *     [\n
     *         { name: \'hobbies\', value: \'reading\' },\n
     *         { name: \'hobbies\', value: \'cooking\' },\n
     *         { name: \'hobbies\', value: \'swimming\' }\n
     *     ]\n
     *\n
     * Recursive:\n
     *\n
     *     var objects = Ext.Object.toQueryObjects(\'dateOfBirth\', {\n
     *         day: 3,\n
     *         month: 8,\n
     *         year: 1987,\n
     *         extra: {\n
     *             hour: 4,\n
     *             minute: 30\n
     *         }\n
     *     }, true);\n
     *\n
     *     // objects then equals:\n
     *     [\n
     *         { name: \'dateOfBirth[day]\', value: 3 },\n
     *         { name: \'dateOfBirth[month]\', value: 8 },\n
     *         { name: \'dateOfBirth[year]\', value: 1987 },\n
     *         { name: \'dateOfBirth[extra][hour]\', value: 4 },\n
     *         { name: \'dateOfBirth[extra][minute]\', value: 30 }\n
     *     ]\n
     *\n
     * @param {String} name\n
     * @param {Object} value\n
     * @param {Boolean} [recursive=false] `true` to recursively encode any sub-objects.\n
     * @return {Object[]} Array of objects with `name` and `value` fields.\n
     */\n
    toQueryObjects: function(name, value, recursive) {\n
        var self = ExtObject.toQueryObjects,\n
            objects = [],\n
            i, ln;\n
\n
        if (Ext.isArray(value)) {\n
            for (i = 0, ln = value.length; i < ln; i++) {\n
                if (recursive) {\n
                    objects = objects.concat(self(name + \'[\' + i + \']\', value[i], true));\n
                }\n
                else {\n
                    objects.push({\n
                        name: name,\n
                        value: value[i]\n
                    });\n
                }\n
            }\n
        }\n
        else if (Ext.isObject(value)) {\n
            for (i in value) {\n
                if (value.hasOwnProperty(i)) {\n
                    if (recursive) {\n
                        objects = objects.concat(self(name + \'[\' + i + \']\', value[i], true));\n
                    }\n
                    else {\n
                        objects.push({\n
                            name: name,\n
                            value: value[i]\n
                        });\n
                    }\n
                }\n
            }\n
        }\n
        else {\n
            objects.push({\n
                name: name,\n
                value: value\n
            });\n
        }\n
\n
        return objects;\n
    },\n
\n
    /**\n
     * Takes an object and converts it to an encoded query string.\n
     *\n
     * Non-recursive:\n
     *\n
     *     Ext.Object.toQueryString({foo: 1, bar: 2}); // returns "foo=1&bar=2"\n
     *     Ext.Object.toQueryString({foo: null, bar: 2}); // returns "foo=&bar=2"\n
     *     Ext.Object.toQueryString({\'some price\': \'$300\'}); // returns "some%20price=%24300"\n
     *     Ext.Object.toQueryString({date: new Date(2011, 0, 1)}); // returns "date=%222011-01-01T00%3A00%3A00%22"\n
     *     Ext.Object.toQueryString({colors: [\'red\', \'green\', \'blue\']}); // returns "colors=red&colors=green&colors=blue"\n
     *\n
     * Recursive:\n
     *\n
     *     Ext.Object.toQueryString({\n
     *         username: \'Jacky\',\n
     *         dateOfBirth: {\n
     *             day: 1,\n
     *             month: 2,\n
     *             year: 1911\n
     *         },\n
     *         hobbies: [\'coding\', \'eating\', \'sleeping\', [\'nested\', \'stuff\']]\n
     *     }, true);\n
     *\n
     *     // returns the following string (broken down and url-decoded for ease of reading purpose):\n
     *     // username=Jacky\n
     *     //    &dateOfBirth[day]=1&dateOfBirth[month]=2&dateOfBirth[year]=1911\n
     *     //    &hobbies[0]=coding&hobbies[1]=eating&hobbies[2]=sleeping&hobbies[3][0]=nested&hobbies[3][1]=stuff\n
     *\n
     * @param {Object} object The object to encode.\n
     * @param {Boolean} [recursive=false] Whether or not to interpret the object in recursive format.\n
     * (PHP / Ruby on Rails servers and similar).\n
     * @return {String} queryString\n
     */\n
    toQueryString: function(object, recursive) {\n
        var paramObjects = [],\n
            params = [],\n
            i, j, ln, paramObject, value;\n
\n
        for (i in object) {\n
            if (object.hasOwnProperty(i)) {\n
                paramObjects = paramObjects.concat(ExtObject.toQueryObjects(i, object[i], recursive));\n
            }\n
        }\n
\n
        for (j = 0, ln = paramObjects.length; j < ln; j++) {\n
            paramObject = paramObjects[j];\n
            value = paramObject.value;\n
\n
            if (Ext.isEmpty(value)) {\n
                value = \'\';\n
            }\n
            else if (Ext.isDate(value)) {\n
                value = Ext.Date.toString(value);\n
            }\n
\n
            params.push(encodeURIComponent(paramObject.name) + \'=\' + encodeURIComponent(String(value)));\n
        }\n
\n
        return params.join(\'&\');\n
    },\n
\n
    /**\n
     * Converts a query string back into an object.\n
     *\n
     * Non-recursive:\n
     *\n
     *     Ext.Object.fromQueryString("foo=1&bar=2"); // returns {foo: 1, bar: 2}\n
     *     Ext.Object.fromQueryString("foo=&bar=2"); // returns {foo: null, bar: 2}\n
     *     Ext.Object.fromQueryString("some%20price=%24300"); // returns {\'some price\': \'$300\'}\n
     *     Ext.Object.fromQueryString("colors=red&colors=green&colors=blue"); // returns {colors: [\'red\', \'green\', \'blue\']}\n
     *\n
     * Recursive:\n
     *\n
     *     Ext.Object.fromQueryString("username=Jacky&dateOfBirth[day]=1&dateOfBirth[month]=2&dateOfBirth[year]=1911&hobbies[0]=coding&hobbies[1]=eating&hobbies[2]=sleeping&hobbies[3][0]=nested&hobbies[3][1]=stuff", true);\n
     *\n
     *     // returns\n
     *     {\n
     *         username: \'Jacky\',\n
     *         dateOfBirth: {\n
     *             day: \'1\',\n
     *             month: \'2\',\n
     *             year: \'1911\'\n
     *         },\n
     *         hobbies: [\'coding\', \'eating\', \'sleeping\', [\'nested\', \'stuff\']]\n
     *     }\n
     *\n
     * @param {String} queryString The query string to decode.\n
     * @param {Boolean} [recursive=false] Whether or not to recursively decode the string. This format is supported by\n
     * PHP / Ruby on Rails servers and similar.\n
     * @return {Object}\n
     */\n
    fromQueryString: function(queryString, recursive) {\n
        var parts = queryString.replace(/^\\?/, \'\').split(\'&\'),\n
            object = {},\n
            temp, components, name, value, i, ln,\n
            part, j, subLn, matchedKeys, matchedName,\n
            keys, key, nextKey;\n
\n
        for (i = 0, ln = parts.length; i < ln; i++) {\n
            part = parts[i];\n
\n
            if (part.length > 0) {\n
                components = part.split(\'=\');\n
                name = decodeURIComponent(components[0]);\n
                value = (components[1] !== undefined) ? decodeURIComponent(components[1]) : \'\';\n
\n
                if (!recursive) {\n
                    if (object.hasOwnProperty(name)) {\n
                        if (!Ext.isArray(object[name])) {\n
                            object[name] = [object[name]];\n
                        }\n
\n
                        object[name].push(value);\n
                    }\n
                    else {\n
                        object[name] = value;\n
                    }\n
                }\n
                else {\n
                    matchedKeys = name.match(/(\\[):?([^\\]]*)\\]/g);\n
                    matchedName = name.match(/^([^\\[]+)/);\n
\n
                    //<debug error>\n
                    if (!matchedName) {\n
                        throw new Error(\'[Ext.Object.fromQueryString] Malformed query string given, failed parsing name from "\' + part + \'"\');\n
                    }\n
                    //</debug>\n
\n
                    name = matchedName[0];\n
                    keys = [];\n
\n
                    if (matchedKeys === null) {\n
                        object[name] = value;\n
                        continue;\n
                    }\n
\n
                    for (j = 0, subLn = matchedKeys.length; j < subLn; j++) {\n
                        key = matchedKeys[j];\n
                        key = (key.length === 2) ? \'\' : key.substring(1, key.length - 1);\n
                        keys.push(key);\n
                    }\n
\n
                    keys.unshift(name);\n
\n
                    temp = object;\n
\n
                    for (j = 0, subLn = keys.length; j < subLn; j++) {\n
                        key = keys[j];\n
\n
                        if (j === subLn - 1) {\n
                            if (Ext.isArray(temp) && key === \'\') {\n
                                temp.push(value);\n
                            }\n
                            else {\n
                                temp[key] = value;\n
                            }\n
                        }\n
                        else {\n
                            if (temp[key] === undefined || typeof temp[key] === \'string\') {\n
                                nextKey = keys[j+1];\n
\n
                                temp[key] = (Ext.isNumeric(nextKey) || nextKey === \'\') ? [] : {};\n
                            }\n
\n
                            temp = temp[key];\n
                        }\n
                    }\n
                }\n
            }\n
        }\n
\n
        return object;\n
    },\n
\n
    /**\n
     * Iterate through an object and invoke the given callback function for each iteration. The iteration can be stop\n
     * by returning `false` in the callback function. For example:\n
     *\n
     *     var person = {\n
     *         name: \'Jacky\',\n
     *         hairColor: \'black\',\n
     *         loves: [\'food\', \'sleeping\', \'wife\']\n
     *     };\n
     *\n
     *     Ext.Object.each(person, function(key, value, myself) {\n
     *         console.log(key + ":" + value);\n
     *\n
     *         if (key === \'hairColor\') {\n
     *             return false; // stop the iteration\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} object The object to iterate\n
     * @param {Function} fn The callback function.\n
     * @param {String} fn.key\n
     * @param {Mixed} fn.value\n
     * @param {Object} fn.object The object itself\n
     * @param {Object} [scope] The execution scope (`this`) of the callback function\n
     */\n
    each: function(object, fn, scope) {\n
        for (var property in object) {\n
            if (object.hasOwnProperty(property)) {\n
                if (fn.call(scope || object, property, object[property], object) === false) {\n
                    return;\n
                }\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Merges any number of objects recursively without referencing them or their children.\n
     *\n
     *     var extjs = {\n
     *         companyName: \'Ext JS\',\n
     *         products: [\'Ext JS\', \'Ext GWT\', \'Ext Designer\'],\n
     *         isSuperCool: true,\n
     *         office: {\n
     *             size: 2000,\n
     *             location: \'Palo Alto\',\n
     *             isFun: true\n
     *         }\n
     *     };\n
     *\n
     *     var newStuff = {\n
     *         companyName: \'Sencha Inc.\',\n
     *         products: [\'Ext JS\', \'Ext GWT\', \'Ext Designer\', \'Sencha Touch\', \'Sencha Animator\'],\n
     *         office: {\n
     *             size: 40000,\n
     *             location: \'Redwood City\'\n
     *         }\n
     *     };\n
     *\n
     *     var sencha = Ext.Object.merge({}, extjs, newStuff);\n
     *\n
     *     // sencha then equals to\n
     *     {\n
     *         companyName: \'Sencha Inc.\',\n
     *         products: [\'Ext JS\', \'Ext GWT\', \'Ext Designer\', \'Sencha Touch\', \'Sencha Animator\'],\n
     *         isSuperCool: true\n
     *         office: {\n
     *             size: 40000,\n
     *             location: \'Redwood City\'\n
     *             isFun: true\n
     *         }\n
     *     }\n
     *\n
     * @param {Object} source The first object into which to merge the others.\n
     * @param {Object...} objs One or more objects to be merged into the first.\n
     * @return {Object} The object that is created as a result of merging all the objects passed in.\n
     */\n
    merge: function(source) {\n
        var i = 1,\n
            ln = arguments.length,\n
            mergeFn = ExtObject.merge,\n
            cloneFn = Ext.clone,\n
            object, key, value, sourceKey;\n
\n
        for (; i < ln; i++) {\n
            object = arguments[i];\n
\n
            for (key in object) {\n
                value = object[key];\n
                if (value && value.constructor === Object) {\n
                    sourceKey = source[key];\n
                    if (sourceKey && sourceKey.constructor === Object) {\n
                        mergeFn(sourceKey, value);\n
                    }\n
                    else {\n
                        source[key] = cloneFn(value);\n
                    }\n
                }\n
                else {\n
                    source[key] = value;\n
                }\n
            }\n
        }\n
\n
        return source;\n
    },\n
\n
    /**\n
     * @private\n
     * @param source\n
     */\n
    mergeIf: function(source) {\n
        var i = 1,\n
            ln = arguments.length,\n
            cloneFn = Ext.clone,\n
            object, key, value;\n
\n
        for (; i < ln; i++) {\n
            object = arguments[i];\n
\n
            for (key in object) {\n
                if (!(key in source)) {\n
                    value = object[key];\n
\n
                    if (value && value.constructor === Object) {\n
                        source[key] = cloneFn(value);\n
                    }\n
                    else {\n
                        source[key] = value;\n
                    }\n
                }\n
            }\n
        }\n
\n
        return source;\n
    },\n
\n
    /**\n
     * Returns the first matching key corresponding to the given value.\n
     * If no matching value is found, `null` is returned.\n
     *\n
     *     var person = {\n
     *         name: \'Jacky\',\n
     *         loves: \'food\'\n
     *     };\n
     *\n
     *     alert(Ext.Object.getKey(sencha, \'food\')); // alerts \'loves\'\n
     *\n
     * @param {Object} object\n
     * @param {Object} value The value to find\n
     */\n
    getKey: function(object, value) {\n
        for (var property in object) {\n
            if (object.hasOwnProperty(property) && object[property] === value) {\n
                return property;\n
            }\n
        }\n
\n
        return null;\n
    },\n
\n
    /**\n
     * Gets all values of the given object as an array.\n
     *\n
     *     var values = Ext.Object.getValues({\n
     *         name: \'Jacky\',\n
     *         loves: \'food\'\n
     *     }); // [\'Jacky\', \'food\']\n
     *\n
     * @param {Object} object\n
     * @return {Array} An array of values from the object.\n
     */\n
    getValues: function(object) {\n
        var values = [],\n
            property;\n
\n
        for (property in object) {\n
            if (object.hasOwnProperty(property)) {\n
                values.push(object[property]);\n
            }\n
        }\n
\n
        return values;\n
    },\n
\n
    /**\n
     * Gets all keys of the given object as an array.\n
     *\n
     *     var values = Ext.Object.getKeys({\n
     *         name: \'Jacky\',\n
     *         loves: \'food\'\n
     *     }); // [\'name\', \'loves\']\n
     *\n
     * @param {Object} object\n
     * @return {String[]} An array of keys from the object.\n
     * @method\n
     */\n
    getKeys: (\'keys\' in Object) ? Object.keys : function(object) {\n
        var keys = [],\n
            property;\n
\n
        for (property in object) {\n
            if (object.hasOwnProperty(property)) {\n
                keys.push(property);\n
            }\n
        }\n
\n
        return keys;\n
    },\n
\n
    /**\n
     * Gets the total number of this object\'s own properties.\n
     *\n
     *     var size = Ext.Object.getSize({\n
     *         name: \'Jacky\',\n
     *         loves: \'food\'\n
     *     }); // size equals 2\n
     *\n
     * @param {Object} object\n
     * @return {Number} size\n
     */\n
    getSize: function(object) {\n
        var size = 0,\n
            property;\n
\n
        for (property in object) {\n
            if (object.hasOwnProperty(property)) {\n
                size++;\n
            }\n
        }\n
\n
        return size;\n
    },\n
\n
    /**\n
     * @private\n
     */\n
    classify: function(object) {\n
        var objectProperties = [],\n
            arrayProperties = [],\n
            propertyClassesMap = {},\n
            objectClass = function() {\n
                var i = 0,\n
                    ln = objectProperties.length,\n
                    property;\n
\n
                for (; i < ln; i++) {\n
                    property = objectProperties[i];\n
                    this[property] = new propertyClassesMap[property];\n
                }\n
\n
                ln = arrayProperties.length;\n
\n
                for (i = 0; i < ln; i++) {\n
                    property = arrayProperties[i];\n
                    this[property] = object[property].slice();\n
                }\n
            },\n
            key, value, constructor;\n
\n
        for (key in object) {\n
            if (object.hasOwnProperty(key)) {\n
                value = object[key];\n
\n
                if (value) {\n
                    constructor = value.constructor;\n
\n
                    if (constructor === Object) {\n
                        objectProperties.push(key);\n
                        propertyClassesMap[key] = ExtObject.classify(value);\n
                    }\n
                    else if (constructor === Array) {\n
                        arrayProperties.push(key);\n
                    }\n
                }\n
            }\n
        }\n
\n
        objectClass.prototype = object;\n
\n
        return objectClass;\n
    },\n
\n
    defineProperty: (\'defineProperty\' in Object) ? Object.defineProperty : function(object, name, descriptor) {\n
        if (descriptor.get) {\n
            object.__defineGetter__(name, descriptor.get);\n
        }\n
\n
        if (descriptor.set) {\n
            object.__defineSetter__(name, descriptor.set);\n
        }\n
    }\n
};\n
\n
/**\n
 * A convenient alias method for {@link Ext.Object#merge}.\n
 *\n
 * @member Ext\n
 * @method merge\n
 */\n
Ext.merge = Ext.Object.merge;\n
\n
/**\n
 * @private\n
 */\n
Ext.mergeIf = Ext.Object.mergeIf;\n
\n
/**\n
 * A convenient alias method for {@link Ext.Object#toQueryString}.\n
 *\n
 * @member Ext\n
 * @method urlEncode\n
 * @deprecated 4.0.0 Please use `{@link Ext.Object#toQueryString Ext.Object.toQueryString}` instead\n
 */\n
Ext.urlEncode = function() {\n
    var args = Ext.Array.from(arguments),\n
        prefix = \'\';\n
\n
    // Support for the old `pre` argument\n
    if ((typeof args[1] === \'string\')) {\n
        prefix = args[1] + \'&\';\n
        args[1] = false;\n
    }\n
\n
    return prefix + ExtObject.toQueryString.apply(ExtObject, args);\n
};\n
\n
/**\n
 * A convenient alias method for {@link Ext.Object#fromQueryString}.\n
 *\n
 * @member Ext\n
 * @method urlDecode\n
 * @deprecated 4.0.0 Please use {@link Ext.Object#fromQueryString Ext.Object.fromQueryString} instead\n
 */\n
Ext.urlDecode = function() {\n
    return ExtObject.fromQueryString.apply(ExtObject, arguments);\n
};\n
\n
})();\n
\n
//@tag foundation,core\n
//@define Ext.Function\n
//@require Ext.Object\n
\n
/**\n
 * @class Ext.Function\n
 *\n
 * A collection of useful static methods to deal with function callbacks.\n
 * @singleton\n
 * @alternateClassName Ext.util.Functions\n
 */\n
Ext.Function = {\n
\n
    /**\n
     * A very commonly used method throughout the framework. It acts as a wrapper around another method\n
     * which originally accepts 2 arguments for `name` and `value`.\n
     * The wrapped function then allows "flexible" value setting of either:\n
     *\n
     * - `name` and `value` as 2 arguments\n
     * - one single object argument with multiple key - value pairs\n
     *\n
     * For example:\n
     *\n
     *     var setValue = Ext.Function.flexSetter(function(name, value) {\n
     *         this[name] = value;\n
     *     });\n
     *\n
     *     // Afterwards\n
     *     // Setting a single name - value\n
     *     setValue(\'name1\', \'value1\');\n
     *\n
     *     // Settings multiple name - value pairs\n
     *     setValue({\n
     *         name1: \'value1\',\n
     *         name2: \'value2\',\n
     *         name3: \'value3\'\n
     *     });\n
     *\n
     * @param {Function} setter\n
     * @return {Function} flexSetter\n
     */\n
    flexSetter: function(fn) {\n
        return function(a, b) {\n
            var k, i;\n
\n
            if (a === null) {\n
                return this;\n
            }\n
\n
            if (typeof a !== \'string\') {\n
                for (k in a) {\n
                    if (a.hasOwnProperty(k)) {\n
                        fn.call(this, k, a[k]);\n
                    }\n
                }\n
\n
                if (Ext.enumerables) {\n
                    for (i = Ext.enumerables.length; i--;) {\n
                        k = Ext.enumerables[i];\n
                        if (a.hasOwnProperty(k)) {\n
                            fn.call(this, k, a[k]);\n
                        }\n
                    }\n
                }\n
            } else {\n
                fn.call(this, a, b);\n
            }\n
\n
            return this;\n
        };\n
    },\n
\n
    /**\n
     * Create a new function from the provided `fn`, change `this` to the provided scope, optionally\n
     * overrides arguments for the call. Defaults to the arguments passed by the caller.\n
     *\n
     * {@link Ext#bind Ext.bind} is alias for {@link Ext.Function#bind Ext.Function.bind}\n
     *\n
     * @param {Function} fn The function to delegate.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which the function is executed.\n
     * **If omitted, defaults to the browser window.**\n
     * @param {Array} args (optional) Overrides arguments for the call. (Defaults to the arguments passed by the caller)\n
     * @param {Boolean/Number} appendArgs (optional) if `true` args are appended to call args instead of overriding,\n
     * if a number the args are inserted at the specified position.\n
     * @return {Function} The new function.\n
     */\n
    bind: function(fn, scope, args, appendArgs) {\n
        if (arguments.length === 2) {\n
            return function() {\n
                return fn.apply(scope, arguments);\n
            }\n
        }\n
\n
        var method = fn,\n
            slice = Array.prototype.slice;\n
\n
        return function() {\n
            var callArgs = args || arguments;\n
\n
            if (appendArgs === true) {\n
                callArgs = slice.call(arguments, 0);\n
                callArgs = callArgs.concat(args);\n
            }\n
            else if (typeof appendArgs == \'number\') {\n
                callArgs = slice.call(arguments, 0); // copy arguments first\n
                Ext.Array.insert(callArgs, appendArgs, args);\n
            }\n
\n
            return method.apply(scope || window, callArgs);\n
        };\n
    },\n
\n
    /**\n
     * Create a new function from the provided `fn`, the arguments of which are pre-set to `args`.\n
     * New arguments passed to the newly created callback when it\'s invoked are appended after the pre-set ones.\n
     * This is especially useful when creating callbacks.\n
     *\n
     * For example:\n
     *\n
     *     var originalFunction = function(){\n
     *         alert(Ext.Array.from(arguments).join(\' \'));\n
     *     };\n
     *\n
     *     var callback = Ext.Function.pass(originalFunction, [\'Hello\', \'World\']);\n
     *\n
     *     callback(); // alerts \'Hello World\'\n
     *     callback(\'by Me\'); // alerts \'Hello World by Me\'\n
     *\n
     * {@link Ext#pass Ext.pass} is alias for {@link Ext.Function#pass Ext.Function.pass}\n
     *\n
     * @param {Function} fn The original function.\n
     * @param {Array} args The arguments to pass to new callback.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which the function is executed.\n
     * @return {Function} The new callback function.\n
     */\n
    pass: function(fn, args, scope) {\n
        if (!Ext.isArray(args)) {\n
            args = Ext.Array.clone(args);\n
        }\n
\n
        return function() {\n
            args.push.apply(args, arguments);\n
            return fn.apply(scope || this, args);\n
        };\n
    },\n
\n
    /**\n
     * Create an alias to the provided method property with name `methodName` of `object`.\n
     * Note that the execution scope will still be bound to the provided `object` itself.\n
     *\n
     * @param {Object/Function} object\n
     * @param {String} methodName\n
     * @return {Function} aliasFn\n
     */\n
    alias: function(object, methodName) {\n
        return function() {\n
            return object[methodName].apply(object, arguments);\n
        };\n
    },\n
\n
    /**\n
     * Create a "clone" of the provided method. The returned method will call the given\n
     * method passing along all arguments and the "this" pointer and return its result.\n
     *\n
     * @param {Function} method\n
     * @return {Function} cloneFn\n
     */\n
    clone: function(method) {\n
        return function() {\n
            return method.apply(this, arguments);\n
        };\n
    },\n
\n
    /**\n
     * Creates an interceptor function. The passed function is called before the original one. If it returns false,\n
     * the original one is not called. The resulting function returns the results of the original function.\n
     * The passed function is called with the parameters of the original function. Example usage:\n
     *\n
     *     var sayHi = function(name){\n
     *         alert(\'Hi, \' + name);\n
     *     };\n
     *\n
     *     sayHi(\'Fred\'); // alerts "Hi, Fred"\n
     *\n
     *     // create a new function that validates input without\n
     *     // directly modifying the original function:\n
     *     var sayHiToFriend = Ext.Function.createInterceptor(sayHi, function(name){\n
     *         return name === \'Brian\';\n
     *     });\n
     *\n
     *     sayHiToFriend(\'Fred\');  // no alert\n
     *     sayHiToFriend(\'Brian\'); // alerts "Hi, Brian"\n
     *\n
     * @param {Function} origFn The original function.\n
     * @param {Function} newFn The function to call before the original.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which the passed function is executed.\n
     * **If omitted, defaults to the scope in which the original function is called or the browser window.**\n
     * @param {Object} [returnValue=null] (optional) The value to return if the passed function return `false`.\n
     * @return {Function} The new function.\n
     */\n
    createInterceptor: function(origFn, newFn, scope, returnValue) {\n
        var method = origFn;\n
        if (!Ext.isFunction(newFn)) {\n
            return origFn;\n
        }\n
        else {\n
            return function() {\n
                var me = this,\n
                    args = arguments;\n
                newFn.target = me;\n
                newFn.method = origFn;\n
                return (newFn.apply(scope || me || window, args) !== false) ? origFn.apply(me || window, args) : returnValue || null;\n
            };\n
        }\n
    },\n
\n
    /**\n
     * Creates a delegate (callback) which, when called, executes after a specific delay.\n
     *\n
     * @param {Function} fn The function which will be called on a delay when the returned function is called.\n
     * Optionally, a replacement (or additional) argument list may be specified.\n
     * @param {Number} delay The number of milliseconds to defer execution by whenever called.\n
     * @param {Object} scope (optional) The scope (`this` reference) used by the function at execution time.\n
     * @param {Array} args (optional) Override arguments for the call. (Defaults to the arguments passed by the caller)\n
     * @param {Boolean/Number} appendArgs (optional) if True args are appended to call args instead of overriding,\n
     * if a number the args are inserted at the specified position.\n
     * @return {Function} A function which, when called, executes the original function after the specified delay.\n
     */\n
    createDelayed: function(fn, delay, scope, args, appendArgs) {\n
        if (scope || args) {\n
            fn = Ext.Function.bind(fn, scope, args, appendArgs);\n
        }\n
\n
        return function() {\n
            var me = this,\n
                args = Array.prototype.slice.call(arguments);\n
\n
            setTimeout(function() {\n
                fn.apply(me, args);\n
            }, delay);\n
        }\n
    },\n
\n
    /**\n
     * Calls this function after the number of milliseconds specified, optionally in a specific scope. Example usage:\n
     *\n
     *     var sayHi = function(name){\n
     *         alert(\'Hi, \' + name);\n
     *     };\n
     *\n
     *     // executes immediately:\n
     *     sayHi(\'Fred\');\n
     *\n
     *     // executes after 2 seconds:\n
     *     Ext.Function.defer(sayHi, 2000, this, [\'Fred\']);\n
     *\n
     *     // this syntax is sometimes useful for deferring\n
     *     // execution of an anonymous function:\n
     *     Ext.Function.defer(function(){\n
     *         alert(\'Anonymous\');\n
     *     }, 100);\n
     *\n
     * {@link Ext#defer Ext.defer} is alias for {@link Ext.Function#defer Ext.Function.defer}\n
     *\n
     * @param {Function} fn The function to defer.\n
     * @param {Number} millis The number of milliseconds for the `setTimeout()` call.\n
     * If less than or equal to 0 the function is executed immediately.\n
     * @param {Object} scope (optional) The scope (`this` re

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

ference) in which the function is executed.\n
     * If omitted, defaults to the browser window.\n
     * @param {Array} args (optional) Overrides arguments for the call. Defaults to the arguments passed by the caller.\n
     * @param {Boolean/Number} appendArgs (optional) if `true`, args are appended to call args instead of overriding,\n
     * if a number the args are inserted at the specified position.\n
     * @return {Number} The timeout id that can be used with `clearTimeout()`.\n
     */\n
    defer: function(fn, millis, scope, args, appendArgs) {\n
        fn = Ext.Function.bind(fn, scope, args, appendArgs);\n
        if (millis > 0) {\n
            return setTimeout(fn, millis);\n
        }\n
        fn();\n
        return 0;\n
    },\n
\n
    /**\n
     * Create a combined function call sequence of the original function + the passed function.\n
     * The resulting function returns the results of the original function.\n
     * The passed function is called with the parameters of the original function. Example usage:\n
     *\n
     *     var sayHi = function(name){\n
     *         alert(\'Hi, \' + name);\n
     *     };\n
     *\n
     *     sayHi(\'Fred\'); // alerts "Hi, Fred"\n
     *\n
     *     var sayGoodbye = Ext.Function.createSequence(sayHi, function(name){\n
     *         alert(\'Bye, \' + name);\n
     *     });\n
     *\n
     *     sayGoodbye(\'Fred\'); // both alerts show\n
     *\n
     * @param {Function} originalFn The original function.\n
     * @param {Function} newFn The function to sequence.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which the passed function is executed.\n
     * If omitted, defaults to the scope in which the original function is called or the browser window.\n
     * @return {Function} The new function.\n
     */\n
    createSequence: function(originalFn, newFn, scope) {\n
        if (!newFn) {\n
            return originalFn;\n
        }\n
        else {\n
            return function() {\n
                var result = originalFn.apply(this, arguments);\n
                newFn.apply(scope || this, arguments);\n
                return result;\n
            };\n
        }\n
    },\n
\n
    /**\n
     * Creates a delegate function, optionally with a bound scope which, when called, buffers\n
     * the execution of the passed function for the configured number of milliseconds.\n
     * If called again within that period, the impending invocation will be canceled, and the\n
     * timeout period will begin again.\n
     *\n
     * @param {Function} fn The function to invoke on a buffered timer.\n
     * @param {Number} buffer The number of milliseconds by which to buffer the invocation of the\n
     * function.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which\n
     * the passed function is executed. If omitted, defaults to the scope specified by the caller.\n
     * @param {Array} args (optional) Override arguments for the call. Defaults to the arguments\n
     * passed by the caller.\n
     * @return {Function} A function which invokes the passed function after buffering for the specified time.\n
     */\n
\n
    createBuffered: function(fn, buffer, scope, args) {\n
        var timerId;\n
\n
        return function() {\n
            var callArgs = args || Array.prototype.slice.call(arguments, 0),\n
                me = scope || this;\n
\n
            if (timerId) {\n
                clearTimeout(timerId);\n
            }\n
\n
            timerId = setTimeout(function(){\n
                fn.apply(me, callArgs);\n
            }, buffer);\n
        };\n
    },\n
\n
    /**\n
     * Creates a throttled version of the passed function which, when called repeatedly and\n
     * rapidly, invokes the passed function only after a certain interval has elapsed since the\n
     * previous invocation.\n
     *\n
     * This is useful for wrapping functions which may be called repeatedly, such as\n
     * a handler of a mouse move event when the processing is expensive.\n
     *\n
     * @param {Function} fn The function to execute at a regular time interval.\n
     * @param {Number} interval The interval, in milliseconds, on which the passed function is executed.\n
     * @param {Object} scope (optional) The scope (`this` reference) in which\n
     * the passed function is executed. If omitted, defaults to the scope specified by the caller.\n
     * @return {Function} A function which invokes the passed function at the specified interval.\n
     */\n
    createThrottled: function(fn, interval, scope) {\n
        var lastCallTime, elapsed, lastArgs, timer, execute = function() {\n
            fn.apply(scope || this, lastArgs);\n
            lastCallTime = new Date().getTime();\n
        };\n
\n
        return function() {\n
            elapsed = new Date().getTime() - lastCallTime;\n
            lastArgs = arguments;\n
\n
            clearTimeout(timer);\n
            if (!lastCallTime || (elapsed >= interval)) {\n
                execute();\n
            } else {\n
                timer = setTimeout(execute, interval - elapsed);\n
            }\n
        };\n
    },\n
\n
    interceptBefore: function(object, methodName, fn) {\n
        var method = object[methodName] || Ext.emptyFn;\n
\n
        return object[methodName] = function() {\n
            var ret = fn.apply(this, arguments);\n
            method.apply(this, arguments);\n
\n
            return ret;\n
        };\n
    },\n
\n
    interceptAfter: function(object, methodName, fn) {\n
        var method = object[methodName] || Ext.emptyFn;\n
\n
        return object[methodName] = function() {\n
            method.apply(this, arguments);\n
            return fn.apply(this, arguments);\n
        };\n
    }\n
};\n
\n
/**\n
 * @method\n
 * @member Ext\n
 * @alias Ext.Function#defer\n
 */\n
Ext.defer = Ext.Function.alias(Ext.Function, \'defer\');\n
\n
/**\n
 * @method\n
 * @member Ext\n
 * @alias Ext.Function#pass\n
 */\n
Ext.pass = Ext.Function.alias(Ext.Function, \'pass\');\n
\n
/**\n
 * @method\n
 * @member Ext\n
 * @alias Ext.Function#bind\n
 */\n
Ext.bind = Ext.Function.alias(Ext.Function, \'bind\');\n
\n
//@tag foundation,core\n
//@define Ext.JSON\n
//@require Ext.Function\n
\n
/**\n
 * @class Ext.JSON\n
 * Modified version of Douglas Crockford\'s json.js that doesn\'t\n
 * mess with the Object prototype.\n
 * [http://www.json.org/js.html](http://www.json.org/js.html)\n
 * @singleton\n
 */\n
Ext.JSON = new(function() {\n
    var useHasOwn = !! {}.hasOwnProperty,\n
    isNative = function() {\n
        var useNative = null;\n
\n
        return function() {\n
            if (useNative === null) {\n
                useNative = Ext.USE_NATIVE_JSON && window.JSON && JSON.toString() == \'[object JSON]\';\n
            }\n
\n
            return useNative;\n
        };\n
    }(),\n
    pad = function(n) {\n
        return n < 10 ? "0" + n : n;\n
    },\n
    doDecode = function(json) {\n
        return eval("(" + json + \')\');\n
    },\n
    doEncode = function(o) {\n
        if (!Ext.isDefined(o) || o === null) {\n
            return "null";\n
        } else if (Ext.isArray(o)) {\n
            return encodeArray(o);\n
        } else if (Ext.isDate(o)) {\n
            return Ext.JSON.encodeDate(o);\n
        } else if (Ext.isString(o)) {\n
            return encodeString(o);\n
        } else if (typeof o == "number") {\n
            //don\'t use isNumber here, since finite checks happen inside isNumber\n
            return isFinite(o) ? String(o) : "null";\n
        } else if (Ext.isBoolean(o)) {\n
            return String(o);\n
        } else if (Ext.isObject(o)) {\n
            return encodeObject(o);\n
        } else if (typeof o === "function") {\n
            return "null";\n
        }\n
        return \'undefined\';\n
    },\n
    m = {\n
        "\\b": \'\\\\b\',\n
        "\\t": \'\\\\t\',\n
        "\\n": \'\\\\n\',\n
        "\\f": \'\\\\f\',\n
        "\\r": \'\\\\r\',\n
        \'"\': \'\\\\"\',\n
        "\\\\": \'\\\\\\\\\',\n
        \'\\x0b\': \'\\\\u000b\' //ie doesn\'t handle \\v\n
    },\n
    charToReplace = /[\\\\\\"\\x00-\\x1f\\x7f-\\uffff]/g,\n
    encodeString = function(s) {\n
        return \'"\' + s.replace(charToReplace, function(a) {\n
            var c = m[a];\n
            return typeof c === \'string\' ? c : \'\\\\u\' + (\'0000\' + a.charCodeAt(0).toString(16)).slice(-4);\n
        }) + \'"\';\n
    },\n
    encodeArray = function(o) {\n
        var a = ["[", ""],\n
        // Note empty string in case there are no serializable members.\n
        len = o.length,\n
        i;\n
        for (i = 0; i < len; i += 1) {\n
            a.push(doEncode(o[i]), \',\');\n
        }\n
        // Overwrite trailing comma (or empty string)\n
        a[a.length - 1] = \']\';\n
        return a.join("");\n
    },\n
    encodeObject = function(o) {\n
        var a = ["{", ""],\n
        // Note empty string in case there are no serializable members.\n
        i;\n
        for (i in o) {\n
            if (!useHasOwn || o.hasOwnProperty(i)) {\n
                a.push(doEncode(i), ":", doEncode(o[i]), \',\');\n
            }\n
        }\n
        // Overwrite trailing comma (or empty string)\n
        a[a.length - 1] = \'}\';\n
        return a.join("");\n
    };\n
\n
    /**\n
     * Encodes a Date. This returns the actual string which is inserted into the JSON string as the literal expression.\n
     * __The returned value includes enclosing double quotation marks.__\n
     *\n
     * The default return format is "yyyy-mm-ddThh:mm:ss".\n
     * \n
     * To override this:\n
     *\n
     *     Ext.JSON.encodeDate = function(d) {\n
     *         return Ext.Date.format(d, \'"Y-m-d"\');\n
     *     };\n
     *\n
     * @param {Date} d The Date to encode.\n
     * @return {String} The string literal to use in a JSON string.\n
     */\n
    this.encodeDate = function(o) {\n
        return \'"\' + o.getFullYear() + "-" \n
        + pad(o.getMonth() + 1) + "-"\n
        + pad(o.getDate()) + "T"\n
        + pad(o.getHours()) + ":"\n
        + pad(o.getMinutes()) + ":"\n
        + pad(o.getSeconds()) + \'"\';\n
    };\n
\n
    /**\n
     * Encodes an Object, Array or other value.\n
     * @param {Object} o The variable to encode.\n
     * @return {String} The JSON string.\n
     * @method\n
     */\n
    this.encode = function() {\n
        var ec;\n
        return function(o) {\n
            if (!ec) {\n
                // setup encoding function on first access\n
                ec = isNative() ? JSON.stringify : doEncode;\n
            }\n
            return ec(o);\n
        };\n
    }();\n
\n
\n
    /**\n
     * Decodes (parses) a JSON string to an object. If the JSON is invalid, this function throws a Error unless the safe option is set.\n
     * @param {String} json The JSON string.\n
     * @param {Boolean} safe (optional) Whether to return `null` or throw an exception if the JSON is invalid.\n
     * @return {Object/null} The resulting object.\n
     * @method\n
     */\n
    this.decode = function() {\n
        var dc;\n
        return function(json, safe) {\n
            if (!dc) {\n
                // setup decoding function on first access\n
                dc = isNative() ? JSON.parse : doDecode;\n
            }\n
            try {\n
                return dc(json);\n
            } catch (e) {\n
                if (safe === true) {\n
                    return null;\n
                }\n
                Ext.Error.raise({\n
                    sourceClass: "Ext.JSON",\n
                    sourceMethod: "decode",\n
                    msg: "You\'re trying to decode an invalid JSON String: " + json\n
                });\n
            }\n
        };\n
    }();\n
\n
})();\n
/**\n
 * Shorthand for {@link Ext.JSON#encode}.\n
 * @member Ext\n
 * @method encode\n
 * @alias Ext.JSON#encode\n
 */\n
Ext.encode = Ext.JSON.encode;\n
/**\n
 * Shorthand for {@link Ext.JSON#decode}.\n
 * @member Ext\n
 * @method decode\n
 * @alias Ext.JSON#decode\n
 */\n
Ext.decode = Ext.JSON.decode;\n
\n
\n
//@tag foundation,core\n
//@define Ext.Error\n
//@require Ext.JSON\n
\n
Ext.Error = {\n
    raise: function(object) {\n
        throw new Error(object.msg);\n
    }\n
};\n
\n
//@tag foundation,core\n
//@define Ext.Date\n
//@require Ext.Error\n
\n
/**\n
 *\n
 */\n
Ext.Date = {\n
    /** @ignore */\n
    now: Date.now,\n
\n
    /**\n
     * @private\n
     * Private for now\n
     */\n
    toString: function(date) {\n
        if (!date) {\n
            date = new Date();\n
        }\n
\n
        var pad = Ext.String.leftPad;\n
\n
        return date.getFullYear() + "-"\n
            + pad(date.getMonth() + 1, 2, \'0\') + "-"\n
            + pad(date.getDate(), 2, \'0\') + "T"\n
            + pad(date.getHours(), 2, \'0\') + ":"\n
            + pad(date.getMinutes(), 2, \'0\') + ":"\n
            + pad(date.getSeconds(), 2, \'0\');\n
    }\n
};\n
\n
\n
//@tag foundation,core\n
//@define Ext.Base\n
//@require Ext.Date\n
\n
/**\n
 * @class Ext.Base\n
 *\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @aside guide class_system\n
 * @aside video class-system\n
 *\n
 * The root of all classes created with {@link Ext#define}.\n
 *\n
 * Ext.Base is the building block of all Ext classes. All classes in Ext inherit from Ext.Base. All prototype and static\n
 * members of this class are inherited by all other classes.\n
 *\n
 * See the [Class System Guide](#!/guide/class_system) for more.\n
 *\n
 */\n
(function(flexSetter) {\n
\n
var noArgs = [],\n
    Base = function(){};\n
\n
    // These static properties will be copied to every newly created class with {@link Ext#define}\n
    Ext.apply(Base, {\n
        $className: \'Ext.Base\',\n
\n
        $isClass: true,\n
\n
        /**\n
         * Create a new instance of this Class.\n
         *\n
         *     Ext.define(\'My.cool.Class\', {\n
         *         // ...\n
         *     });\n
         *\n
         *     My.cool.Class.create({\n
         *         someConfig: true\n
         *     });\n
         *\n
         * All parameters are passed to the constructor of the class.\n
         *\n
         * @return {Object} the created instance.\n
         * @static\n
         * @inheritable\n
         */\n
        create: function() {\n
            return Ext.create.apply(Ext, [this].concat(Array.prototype.slice.call(arguments, 0)));\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        extend: function(parent) {\n
            var parentPrototype = parent.prototype,\n
                prototype, i, ln, name, statics;\n
\n
            prototype = this.prototype = Ext.Object.chain(parentPrototype);\n
            prototype.self = this;\n
\n
            this.superclass = prototype.superclass = parentPrototype;\n
\n
            if (!parent.$isClass) {\n
                Ext.apply(prototype, Ext.Base.prototype);\n
                prototype.constructor = function() {\n
                    parentPrototype.constructor.apply(this, arguments);\n
                };\n
            }\n
\n
            //<feature classSystem.inheritableStatics>\n
            // Statics inheritance\n
            statics = parentPrototype.$inheritableStatics;\n
\n
            if (statics) {\n
                for (i = 0,ln = statics.length; i < ln; i++) {\n
                    name = statics[i];\n
\n
                    if (!this.hasOwnProperty(name)) {\n
                        this[name] = parent[name];\n
                    }\n
                }\n
            }\n
            //</feature>\n
\n
            if (parent.$onExtended) {\n
                this.$onExtended = parent.$onExtended.slice();\n
            }\n
\n
            //<feature classSystem.config>\n
            prototype.config = prototype.defaultConfig = new prototype.configClass;\n
            prototype.initConfigList = prototype.initConfigList.slice();\n
            prototype.initConfigMap = Ext.Object.chain(prototype.initConfigMap);\n
            //</feature>\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        \'$onExtended\': [],\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        triggerExtended: function() {\n
            var callbacks = this.$onExtended,\n
                ln = callbacks.length,\n
                i, callback;\n
\n
            if (ln > 0) {\n
                for (i = 0; i < ln; i++) {\n
                    callback = callbacks[i];\n
                    callback.fn.apply(callback.scope || this, arguments);\n
                }\n
            }\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        onExtended: function(fn, scope) {\n
            this.$onExtended.push({\n
                fn: fn,\n
                scope: scope\n
            });\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        addConfig: function(config, fullMerge) {\n
            var prototype = this.prototype,\n
                initConfigList = prototype.initConfigList,\n
                initConfigMap = prototype.initConfigMap,\n
                defaultConfig = prototype.defaultConfig,\n
                hasInitConfigItem, name, value;\n
\n
            fullMerge = Boolean(fullMerge);\n
\n
            for (name in config) {\n
                if (config.hasOwnProperty(name) && (fullMerge || !(name in defaultConfig))) {\n
                    value = config[name];\n
                    hasInitConfigItem = initConfigMap[name];\n
\n
                    if (value !== null) {\n
                        if (!hasInitConfigItem) {\n
                            initConfigMap[name] = true;\n
                            initConfigList.push(name);\n
                        }\n
                    }\n
                    else if (hasInitConfigItem) {\n
                        initConfigMap[name] = false;\n
                        Ext.Array.remove(initConfigList, name);\n
                    }\n
                }\n
            }\n
\n
            if (fullMerge) {\n
                Ext.merge(defaultConfig, config);\n
            }\n
            else {\n
                Ext.mergeIf(defaultConfig, config);\n
            }\n
\n
            prototype.configClass = Ext.Object.classify(defaultConfig);\n
        },\n
\n
        /**\n
         * Add / override static properties of this class.\n
         *\n
         *     Ext.define(\'My.cool.Class\', {\n
         *         // this.se\n
         *     });\n
         *\n
         *     My.cool.Class.addStatics({\n
         *         someProperty: \'someValue\',      // My.cool.Class.someProperty = \'someValue\'\n
         *         method1: function() {  },    // My.cool.Class.method1 = function() { ... };\n
         *         method2: function() {  }     // My.cool.Class.method2 = function() { ... };\n
         *     });\n
         *\n
         * @param {Object} members\n
         * @return {Ext.Base} this\n
         * @static\n
         * @inheritable\n
         */\n
        addStatics: function(members) {\n
            var member, name;\n
            //<debug>\n
            var className = Ext.getClassName(this);\n
            //</debug>\n
\n
            for (name in members) {\n
                if (members.hasOwnProperty(name)) {\n
                    member = members[name];\n
                    //<debug>\n
                    if (typeof member == \'function\') {\n
                        member.displayName = className + \'.\' + name;\n
                    }\n
                    //</debug>\n
                    this[name] = member;\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        addInheritableStatics: function(members) {\n
            var inheritableStatics,\n
                hasInheritableStatics,\n
                prototype = this.prototype,\n
                name, member;\n
\n
            inheritableStatics = prototype.$inheritableStatics;\n
            hasInheritableStatics = prototype.$hasInheritableStatics;\n
\n
            if (!inheritableStatics) {\n
                inheritableStatics = prototype.$inheritableStatics = [];\n
                hasInheritableStatics = prototype.$hasInheritableStatics = {};\n
            }\n
\n
            //<debug>\n
            var className = Ext.getClassName(this);\n
            //</debug>\n
\n
            for (name in members) {\n
                if (members.hasOwnProperty(name)) {\n
                    member = members[name];\n
                    //<debug>\n
                    if (typeof member == \'function\') {\n
                        member.displayName = className + \'.\' + name;\n
                    }\n
                    //</debug>\n
                    this[name] = member;\n
\n
                    if (!hasInheritableStatics[name]) {\n
                        hasInheritableStatics[name] = true;\n
                        inheritableStatics.push(name);\n
                    }\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Add methods / properties to the prototype of this class.\n
         *\n
         *     @example\n
         *     Ext.define(\'My.awesome.Cat\', {\n
         *         constructor: function() {\n
         *             // ...\n
         *         }\n
         *     });\n
         *\n
         *      My.awesome.Cat.addMembers({\n
         *          meow: function() {\n
         *             alert(\'Meowww...\');\n
         *          }\n
         *      });\n
         *\n
         *      var kitty = new My.awesome.Cat();\n
         *      kitty.meow();\n
         *\n
         * @param {Object} members\n
         * @static\n
         * @inheritable\n
         */\n
        addMembers: function(members) {\n
            var prototype = this.prototype,\n
                names = [],\n
                name, member;\n
\n
            //<debug>\n
            var className = this.$className || \'\';\n
            //</debug>\n
\n
            for (name in members) {\n
                if (members.hasOwnProperty(name)) {\n
                    member = members[name];\n
\n
                    if (typeof member == \'function\' && !member.$isClass && member !== Ext.emptyFn) {\n
                        member.$owner = this;\n
                        member.$name = name;\n
                        //<debug>\n
                        member.displayName = className + \'#\' + name;\n
                        //</debug>\n
                    }\n
\n
                    prototype[name] = member;\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        addMember: function(name, member) {\n
            if (typeof member == \'function\' && !member.$isClass && member !== Ext.emptyFn) {\n
                member.$owner = this;\n
                member.$name = name;\n
                //<debug>\n
                member.displayName = (this.$className || \'\') + \'#\' + name;\n
                //</debug>\n
            }\n
\n
            this.prototype[name] = member;\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        implement: function() {\n
            this.addMembers.apply(this, arguments);\n
        },\n
\n
        /**\n
         * Borrow another class\' members to the prototype of this class.\n
         *\n
         *     Ext.define(\'Bank\', {\n
         *         money: \'$$$\',\n
         *         printMoney: function() {\n
         *             alert(\'$$$$$$$\');\n
         *         }\n
         *     });\n
         *\n
         *     Ext.define(\'Thief\', {\n
         *         // ...\n
         *     });\n
         *\n
         *     Thief.borrow(Bank, [\'money\', \'printMoney\']);\n
         *\n
         *     var steve = new Thief();\n
         *\n
         *     alert(steve.money); // alerts \'$$$\'\n
         *     steve.printMoney(); // alerts \'$$$$$$$\'\n
         *\n
         * @param {Ext.Base} fromClass The class to borrow members from\n
         * @param {Array/String} members The names of the members to borrow\n
         * @return {Ext.Base} this\n
         * @static\n
         * @inheritable\n
         * @private\n
         */\n
        borrow: function(fromClass, members) {\n
            var prototype = this.prototype,\n
                fromPrototype = fromClass.prototype,\n
                //<debug>\n
                className = Ext.getClassName(this),\n
                //</debug>\n
                i, ln, name, fn, toBorrow;\n
\n
            members = Ext.Array.from(members);\n
\n
            for (i = 0,ln = members.length; i < ln; i++) {\n
                name = members[i];\n
\n
                toBorrow = fromPrototype[name];\n
\n
                if (typeof toBorrow == \'function\') {\n
                    fn = function() {\n
                        return toBorrow.apply(this, arguments);\n
                    };\n
\n
                    //<debug>\n
                    if (className) {\n
                        fn.displayName = className + \'#\' + name;\n
                    }\n
                    //</debug>\n
\n
                    fn.$owner = this;\n
                    fn.$name = name;\n
\n
                    prototype[name] = fn;\n
                }\n
                else {\n
                    prototype[name] = toBorrow;\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Override members of this class. Overridden methods can be invoked via\n
         * {@link Ext.Base#callParent}.\n
         *\n
         *     Ext.define(\'My.Cat\', {\n
         *         constructor: function() {\n
         *             alert("I\'m a cat!");\n
         *         }\n
         *     });\n
         *\n
         *     My.Cat.override({\n
         *         constructor: function() {\n
         *             alert("I\'m going to be a cat!");\n
         *\n
         *             var instance = this.callParent(arguments);\n
         *\n
         *             alert("Meeeeoooowwww");\n
         *\n
         *             return instance;\n
         *         }\n
         *     });\n
         *\n
         *     var kitty = new My.Cat(); // alerts "I\'m going to be a cat!"\n
         *                               // alerts "I\'m a cat!"\n
         *                               // alerts "Meeeeoooowwww"\n
         *\n
         * As of 2.1, direct use of this method is deprecated. Use {@link Ext#define Ext.define}\n
         * instead:\n
         *\n
         *     Ext.define(\'My.CatOverride\', {\n
         *         override: \'My.Cat\',\n
         *         \n
         *         constructor: function() {\n
         *             alert("I\'m going to be a cat!");\n
         *\n
         *             var instance = this.callParent(arguments);\n
         *\n
         *             alert("Meeeeoooowwww");\n
         *\n
         *             return instance;\n
         *         }\n
         *     });\n
         *\n
         * The above accomplishes the same result but can be managed by the {@link Ext.Loader}\n
         * which can properly order the override and its target class and the build process\n
         * can determine whether the override is needed based on the required state of the\n
         * target class (My.Cat).\n
         *\n
         * @param {Object} members The properties to add to this class. This should be\n
         * specified as an object literal containing one or more properties.\n
         * @return {Ext.Base} this class\n
         * @static\n
         * @inheritable\n
         * @deprecated 2.1.0 Please use {@link Ext#define Ext.define} instead\n
         */\n
        override: function(members) {\n
            var me = this,\n
                enumerables = Ext.enumerables,\n
                target = me.prototype,\n
                cloneFunction = Ext.Function.clone,\n
                name, index, member, statics, names, previous;\n
\n
            if (arguments.length === 2) {\n
                name = members;\n
                members = {};\n
                members[name] = arguments[1];\n
                enumerables = null;\n
            }\n
\n
            do {\n
                names = []; // clean slate for prototype (1st pass) and static (2nd pass)\n
                statics = null; // not needed 1st pass, but needs to be cleared for 2nd pass\n
\n
                for (name in members) { // hasOwnProperty is checked in the next loop...\n
                    if (name == \'statics\') {\n
                        statics = members[name];\n
                    }\n
                    else if (name == \'config\') {\n
                        me.addConfig(members[name], true);\n
                    }\n
                    else {\n
                        names.push(name);\n
                    }\n
                }\n
\n
                if (enumerables) {\n
                    names.push.apply(names, enumerables);\n
                }\n
\n
                for (index = names.length; index--; ) {\n
                    name = names[index];\n
\n
                    if (members.hasOwnProperty(name)) {\n
                        member = members[name];\n
\n
                        if (typeof member == \'function\' && !member.$className && member !== Ext.emptyFn) {\n
                            if (typeof member.$owner != \'undefined\') {\n
                                member = cloneFunction(member);\n
                            }\n
\n
                            //<debug>\n
                            var className = me.$className;\n
                            if (className) {\n
                                member.displayName = className + \'#\' + name;\n
                            }\n
                            //</debug>\n
\n
                            member.$owner = me;\n
                            member.$name = name;\n
\n
                            previous = target[name];\n
                            if (previous) {\n
                                member.$previous = previous;\n
                            }\n
                        }\n
\n
                        target[name] = member;\n
                    }\n
                }\n
\n
                target = me; // 2nd pass is for statics\n
                members = statics; // statics will be null on 2nd pass\n
            } while (members);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @protected\n
         * @static\n
         * @inheritable\n
         */\n
        callParent: function(args) {\n
            var method;\n
\n
            // This code is intentionally inlined for the least amount of debugger stepping\n
            return (method = this.callParent.caller) && (method.$previous ||\n
                  ((method = method.$owner ? method : method.caller) &&\n
                        method.$owner.superclass.$class[method.$name])).apply(this, args || noArgs);\n
        },\n
\n
        //<feature classSystem.mixins>\n
        /**\n
         * Used internally by the mixins pre-processor\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        mixin: function(name, mixinClass) {\n
            var mixin = mixinClass.prototype,\n
                prototype = this.prototype,\n
                key;\n
\n
            if (typeof mixin.onClassMixedIn != \'undefined\') {\n
                mixin.onClassMixedIn.call(mixinClass, this);\n
            }\n
\n
            if (!prototype.hasOwnProperty(\'mixins\')) {\n
                if (\'mixins\' in prototype) {\n
                    prototype.mixins = Ext.Object.chain(prototype.mixins);\n
                }\n
                else {\n
                    prototype.mixins = {};\n
                }\n
            }\n
\n
            for (key in mixin) {\n
                if (key === \'mixins\') {\n
                    Ext.merge(prototype.mixins, mixin[key]);\n
                }\n
                else if (typeof prototype[key] == \'undefined\' && key != \'mixinId\' && key != \'config\') {\n
                    prototype[key] = mixin[key];\n
                }\n
            }\n
\n
            //<feature classSystem.config>\n
            if (\'config\' in mixin) {\n
                this.addConfig(mixin.config, false);\n
            }\n
            //</feature>\n
\n
            prototype.mixins[name] = mixin;\n
        },\n
        //</feature>\n
\n
        /**\n
         * Get the current class\' name in string format.\n
         *\n
         *     Ext.define(\'My.cool.Class\', {\n
         *         constructor: function() {\n
         *             alert(this.self.getName()); // alerts \'My.cool.Class\'\n
         *         }\n
         *     });\n
         *\n
         *     My.cool.Class.getName(); // \'My.cool.Class\'\n
         *\n
         * @return {String} className\n
         * @static\n
         * @inheritable\n
         */\n
        getName: function() {\n
            return Ext.getClassName(this);\n
        },\n
\n
        /**\n
         * Create aliases for existing prototype methods. Example:\n
         *\n
         *     Ext.define(\'My.cool.Class\', {\n
         *         method1: function() {  },\n
         *         method2: function() {  }\n
         *     });\n
         *\n
         *     var test = new My.cool.Class();\n
         *\n
         *     My.cool.Class.createAlias({\n
         *         method3: \'method1\',\n
         *         method4: \'method2\'\n
         *     });\n
         *\n
         *     test.method3(); // test.method1()\n
         *\n
         *     My.cool.Class.createAlias(\'method5\', \'method3\');\n
         *\n
         *     test.method5(); // test.method3() -> test.method1()\n
         *\n
         * @param {String/Object} alias The new method name, or an object to set multiple aliases. See\n
         * {@link Ext.Function#flexSetter flexSetter}\n
         * @param {String/Object} origin The original method name\n
         * @static\n
         * @inheritable\n
         * @method\n
         */\n
        createAlias: flexSetter(function(alias, origin) {\n
            this.override(alias, function() {\n
                return this[origin].apply(this, arguments);\n
            });\n
        }),\n
\n
        /**\n
         * @private\n
         * @static\n
         * @inheritable\n
         */\n
        addXtype: function(xtype) {\n
            var prototype = this.prototype,\n
                xtypesMap = prototype.xtypesMap,\n
                xtypes = prototype.xtypes,\n
                xtypesChain = prototype.xtypesChain;\n
\n
            if (!prototype.hasOwnProperty(\'xtypesMap\')) {\n
                xtypesMap = prototype.xtypesMap = Ext.merge({}, prototype.xtypesMap || {});\n
                xtypes = prototype.xtypes = prototype.xtypes ? [].concat(prototype.xtypes) : [];\n
                xtypesChain = prototype.xtypesChain = prototype.xtypesChain ? [].concat(prototype.xtypesChain) : [];\n
                prototype.xtype = xtype;\n
            }\n
\n
            if (!xtypesMap[xtype]) {\n
                xtypesMap[xtype] = true;\n
                xtypes.push(xtype);\n
                xtypesChain.push(xtype);\n
                Ext.ClassManager.setAlias(this, \'widget.\' + xtype);\n
            }\n
\n
            return this;\n
        }\n
    });\n
\n
    Base.implement({\n
        isInstance: true,\n
\n
        $className: \'Ext.Base\',\n
\n
        configClass: Ext.emptyFn,\n
\n
        initConfigList: [],\n
\n
        initConfigMap: {},\n
\n
        /**\n
         * Get the reference to the class from which this object was instantiated. Note that unlike {@link Ext.Base#self},\n
         * `this.statics()` is scope-independent and it always returns the class from which it was called, regardless of what\n
         * `this` points to during run-time\n
         *\n
         *     Ext.define(\'My.Cat\', {\n
         *         statics: {\n
         *             totalCreated: 0,\n
         *             speciesName: \'Cat\' // My.Cat.speciesName = \'Cat\'\n
         *         },\n
         *\n
         *         constructor: function() {\n
         *             var statics = this.statics();\n
         *\n
         *             alert(statics.speciesName);     // always equals to \'Cat\' no matter what \'this\' refers to\n
         *                                             // equivalent to: My.Cat.speciesName\n
         *\n
         *             alert(this.self.speciesName);   // dependent on \'this\'\n
         *\n
         *             statics.totalCreated++;\n
         *         },\n
         *\n
         *         clone: function() {\n
         *             var cloned = new this.self();                    // dependent on \'this\'\n
         *\n
         *             cloned.groupName = this.statics().speciesName;   // equivalent to: My.Cat.speciesName\n
         *\n
         *             return cloned;\n
         *         }\n
         *     });\n
         *\n
         *\n
         *     Ext.define(\'My.SnowLeopard\', {\n
         *         extend: \'My.Cat\',\n
         *\n
         *         statics: {\n
         *             speciesName: \'Snow Leopard\'     // My.SnowLeopard.speciesName = \'Snow Leopard\'\n
         *         },\n
         *\n
         *         constructor: function() {\n
         *             this.callParent();\n
         *         }\n
         *     });\n
         *\n
         *     var cat = new My.Cat();                 // alerts \'Cat\', then alerts \'Cat\'\n
         *\n
         *     var snowLeopard = new My.SnowLeopard(); // alerts \'Cat\', then alerts \'Snow Leopard\'\n
         *\n
         *     var clone = snowLeopard.clone();\n
         *     alert(Ext.getClassName(clone));         // alerts \'My.SnowLeopard\'\n
         *     alert(clone.groupName);                 // alerts \'Cat\'\n
         *\n
         *     alert(My.Cat.totalCreated);             // alerts 3\n
         *\n
         * @protected\n
         * @return {Ext.Class}\n
         */\n
        statics: function() {\n
            var method = this.statics.caller,\n
                self = this.self;\n
\n
            if (!method) {\n
                return self;\n
            }\n
\n
            return method.$owner;\n
        },\n
\n
        /**\n
         * Call the "parent" method of the current method. That is the method previously\n
         * overridden by derivation or by an override (see {@link Ext#define}).\n
         *\n
         *      Ext.define(\'My.Base\', {\n
         *          constructor: function (x) {\n
         *              this.x = x;\n
         *          },\n
         *\n
         *          statics: {\n
         *              method: function (x) {\n
         *                  return x;\n
         *              }\n
         *          }\n
         *      });\n
         *\n
         *      Ext.define(\'My.Derived\', {\n
         *          extend: \'My.Base\',\n
         *\n
         *          constructor: function () {\n
         *              this.callParent([21]);\n
         *          }\n
         *      });\n
         *\n
         *      var obj = new My.Derived();\n
         *\n
         *      alert(obj.x);  // alerts 21\n
         *\n
         * This can be used with an override as follows:\n
         *\n
         *      Ext.define(\'My.DerivedOverride\', {\n
         *          override: \'My.Derived\',\n
         *\n
         *          constructor: function (x) {\n
         *              this.callParent([x*2]); // calls original My.Derived constructor\n
         *          }\n
         *      });\n
         *\n
         *      var obj = new My.Derived();\n
         *\n
         *      alert(obj.x);  // now alerts 42\n
         *\n
         * This also works with static methods.\n
         *\n
         *      Ext.define(\'My.Derived2\', {\n
         *          extend: \'My.Base\',\n
         *\n
         *          statics: {\n
         *              method: function (x) {\n
         *                  return this.callParent([x*2]); // calls My.Base.method\n
         *              }\n
         *          }\n
         *      });\n
         *\n
         *      alert(My.Base.method(10));     // alerts 10\n
         *      alert(My.Derived2.method(10)); // alerts 20\n
         *\n
         * Lastly, it also works with overridden static methods.\n
         *\n
         *      Ext.define(\'My.Derived2Override\', {\n
         *          override: \'My.Derived2\',\n
         *\n
         *          statics: {\n
         *              method: function (x) {\n
         *                  return this.callParent([x*2]); // calls My.Derived2.method\n
         *              }\n
         *          }\n
         *      });\n
         *\n
         *      alert(My.Derived2.method(10)); // now alerts 40\n
         * \n
         * To override a method and replace it and also call the superclass method, use\n
         * {@link #callSuper}. This is often done to patch a method to fix a bug.\n
         *\n
         * @protected\n
         * @param {Array/Arguments} args The arguments, either an array or the `arguments` object\n
         * from the current method, for example: `this.callParent(arguments)`\n
         * @return {Object} Returns the result of calling the parent method\n
         */\n
        callParent: function(args) {\n
            // NOTE: this code is deliberately as few expressions (and no function calls)\n
            // as possible so that a debugger can skip over this noise with the minimum number\n
            // of steps. Basically, just hit Step Into until you are where you really wanted\n
            // to be.\n
            var method,\n
                superMethod = (method = this.callParent.caller) && (method.$previous ||\n
                        ((method = method.$owner ? method : method.caller) &&\n
                                method.$owner.superclass[method.$name]));\n
\n
            //<debug error>\n
            if (!superMethod) {\n
                method = this.callParent.caller;\n
                var parentClass, methodName;\n
\n
                if (!method.$owner) {\n
                    if (!method.caller) {\n
                        throw new Error("Attempting to call a protected method from the public scope, which is not allowed");\n
                    }\n
\n
                    method = method.caller;\n
                }\n
\n
                parentClass = method.$owner.superclass;\n
                methodName = method.$name;\n
\n
                if (!(methodName in parentClass)) {\n
                    throw new Error("this.callParent() was called but there\'s no such method (" + methodName +\n
                                ") found in the parent class (" + (Ext.getClassName(parentClass) || \'Object\') + ")");\n
                }\n
            }\n
            //</debug>\n
\n
            return superMethod.apply(this, args || noArgs);\n
        },\n
\n
        /**\n
         * This method is used by an override to call the superclass method but bypass any\n
         * overridden method. This is often done to "patch" a method that contains a bug\n
         * but for whatever reason cannot be fixed directly.\n
         * \n
         * Consider:\n
         * \n
         *      Ext.define(\'Ext.some.Class\', {\n
         *          method: function () {\n
         *              console.log(\'Good\');\n
         *          }\n
         *      });\n
         * \n
         *      Ext.define(\'Ext.some.DerivedClass\', {\n
         *          method: function () {\n
         *              console.log(\'Bad\');\n
         * \n
         *              // ... logic but with a bug ...\n
         *              \n
         *              this.callParent();\n
         *          }\n
         *      });\n
         * \n
         * To patch the bug in `DerivedClass.method`, the typical solution is to create an\n
         * override:\n
         * \n
         *      Ext.define(\'App.paches.DerivedClass\', {\n
         *          override: \'Ext.some.DerivedClass\',\n
         *          \n
         *          method: function () {\n
         *              console.log(\'Fixed\');\n
         * \n
         *              // ... logic but with bug fixed ...\n
         *\n
         *              this.callSuper();\n
         *          }\n
         *      });\n
         * \n
         * The patch method cannot use `callParent` to call the superclass `method` since\n
         * that would call the overridden method containing the bug. In other words, the\n
         * above patch would only produce "Fixed" then "Good" in the console log, whereas,\n
         * using `callParent` would produce "Fixed" then "Bad" then "Good".\n
         *\n
         * @protected\n
         * @param {Array/Arguments} args The arguments, either an array or the `arguments` object\n
         * from the current method, for example: `this.callSuper(arguments)`\n
         * @return {Object} Returns the result of calling the superclass method\n
         */\n
        callSuper: function(args) {\n
            var method,\n
                superMethod = (method = this.callSuper.caller) && ((method = method.$owner ? method : method.caller) &&\n
                                method.$owner.superclass[method.$name]);\n
\n
            //<debug error>\n
            if (!superMethod) {\n
                method = this.callSuper.caller;\n
                var parentClass, methodName;\n
\n
                if (!method.$owner) {\n
                    if (!method.caller) {\n
                        throw new Error("Attempting to call a protected method from the public scope, which is not allowed");\n
                    }\n
\n
                    method = method.caller;\n
                }\n
\n
                parentClass = method.$owner.superclass;\n
                methodName = method.$name;\n
\n
                if (!(methodName in parentClass)) {\n
                    throw new Error("this.callSuper() was called but there\'s no such method (" + methodName +\n
                                ") found in the parent class (" + (Ext.getClassName(parentClass) || \'Object\') + ")");\n
                }\n
            }\n
            //</debug>\n
\n
            return superMethod.apply(this, args || noArgs);\n
        },\n
\n
        /**\n
         * Call the original method that was previously overridden with {@link Ext.Base#override},\n
         * \n
         * This method is deprecated as {@link #callParent} does the same thing.\n
         *\n
         *     Ext.define(\'My.Cat\', {\n
         *         constructor: function() {\n
         *             alert("I\'m a cat!");\n
         *         }\n
         *     });\n
         *\n
         *     My.Cat.override({\n
         *         constructor: function() {\n
         *             alert("I\'m going to be a cat!");\n
         *\n
         *             var instance = this.callOverridden();\n
         *\n
         *             alert("Meeeeoooowwww");\n
         *\n
         *             return instance;\n
         *         }\n
         *     });\n
         *\n
         *     var kitty = new My.Cat(); // alerts "I\'m going to be a cat!"\n
         *                               // alerts "I\'m a cat!"\n
         *                               // alerts "Meeeeoooowwww"\n
         *\n
         * @param {Array/Arguments} args The arguments, either an array or the `arguments` object\n
         * from the current method, for example: `this.callOverridden(arguments)`\n
         * @return {Object} Returns the result of calling the overridden method\n
         * @protected\n
         * @deprecated Use callParent instead\n
         */\n
        callOverridden: function(args) {\n
            var method;\n
\n
            return (method = this.callOverridden.caller) && method.$previous.apply(this, args || noArgs);\n
        },\n
\n
        /**\n
         * @property {Ext.Class} self\n
         *\n
         * Get the reference to the current class from which this object was instantiated. Unlike {@link Ext.Base#statics},\n
         * `this.self` is scope-dependent and it\'s meant to be used for dynamic inheritance. See {@link Ext.Base#statics}\n
         * for a detailed comparison\n
         *\n
         *     Ext.define(\'My.Cat\', {\n
         *         statics: {\n
         *             speciesName: \'Cat\' // My.Cat.speciesName = \'Cat\'\n
         *         },\n
         *\n
         *         constructor: function() {\n
         *             alert(this.self.speciesName); // dependent on \'this\'\n
         *         },\n
         *\n
         *         clone: function() {\n
         *             return new this.self();\n
         *         }\n
         *     });\n
         *\n
         *\n
         *     Ext.define(\'My.SnowLeopard\', {\n
         *         extend: \'My.Cat\',\n
         *         statics: {\n
         *             speciesName: \'Snow Leopard\'         // My.SnowLeopard.speciesName = \'Snow Leopard\'\n
         *         }\n
         *     });\n
         *\n
         *     var cat = new My.Cat();                     // alerts \'Cat\'\n
         *     var snowLeopard = new My.SnowLeopard();     // alerts \'Snow Leopard\'\n
         *\n
         *     var clone = snowLeopard.clone();\n
         *     alert(Ext.getClassName(clone));             // alerts \'My.SnowLeopard\'\n
         *\n
         * @protected\n
         */\n
        self: Base,\n
\n
        // Default constructor, simply returns `this`\n
        constructor: function() {\n
            return this;\n
        },\n
\n
        //<feature classSystem.config>\n
\n
        wasInstantiated: false,\n
\n
        /**\n
         * Initialize configuration for this class. a typical example:\n
         *\n
         *     Ext.define(\'My.awesome.Class\', {\n
         *         // The default config\n
         *         config: {\n
         *             name: \'Awesome\',\n
         *             isAwesome: true\n
         *         },\n
         *\n
         *         constructor: function(config) {\n
         *             this.initConfig(config);\n
         *         }\n
         *     });\n
         *\n
         *     var awesome = new My.awesome.Class({\n
         *         name: \'Super Awesome\'\n
         *     });\n
         *\n
         *     alert(awesome.getName()); // \'Super Awesome\'\n
         *\n
         * @protected\n
         * @param {Object} instanceConfig\n
         * @return {Object} mixins The mixin prototypes as key - value pairs\n
         */\n
        initConfig: function(instanceConfig) {\n
            //<debug>\n
//            if (instanceConfig && instanceConfig.breakOnInitConfig) {\n
//                debugger;\n
//            }\n
            //</debug>\n
            var configNameCache = Ext.Class.configNameCache,\n
                prototype = this.self.prototype,\n
                initConfigList = this.initConfigList,\n
                initConfigMap = this.initConfigMap,\n
                config = new this.configClass,\n
                defaultConfig = this.defaultConfig,\n
                i, ln, name, value, nameMap, getName;\n
\n
            this.initConfig = Ext.emptyFn;\n
\n
            this.initialConfig = instanceConfig || {};\n
\n
            if (instanceConfig) {\n
                Ext.merge(config, instanceConfig);\n
            }\n
\n
            this.config = config;\n
\n
            // Optimize initConfigList *once* per class based on the existence of apply* and update* methods\n
            // Happens only once during the first instantiation\n
            if (!prototype.hasOwnProperty(\'wasInstantiated\')) {\n
                prototype.wasInstantiated = true;\n
\n
                for (i = 0,ln = initConfigList.length; i < ln; i++) {\n
                    name = initConfigList[i];\n
                    nameMap = configNameCache[name];\n
                    value = defaultConfig[name];\n
\n
                    if (!(nameMap.apply in prototype)\n
                        && !(nameMap.update in prototype)\n
                        && prototype[nameMap.set].$isDefault\n
                        && typeof value != \'object\') {\n
                        prototype[nameMap.internal] = defaultConfig[name];\n
                        initConfigMap[name] = false;\n
                        Ext.Array.remove(initConfigList, name);\n
                        i--;\n
                        ln--;\n
                    }\n
                }\n
            }\n
\n
            if (instanceConfig) {\n
                initConfigList = initConfigList.slice();\n
\n
                for (name in instanceConfig) {\n
                    if (name in defaultConfig && !initConfigMap[name]) {\n
                        initConfigList.push(name);\n
                    }\n
                }\n
            }\n
\n
            // Point all getters to the initGetters\n
            for (i = 0,ln = initConfigList.length; i < ln; i++) {\n
                name = initConfigList[i];\n
                nameMap = configNameCache[name];\n
                this[nameMap.get] = this[nameMap.initGet];\n
            }\n
\n
            this.beforeInitConfig(config);\n
\n
            for (i = 0,ln = initConfigList.length; i < ln; i++) {\n
                name = initConfigList[i];\n
                nameMap = configNameCache[name];\n
                getName = nameMap.get;\n
\n
                if (this.hasOwnProperty(getName)) {\n
                    this[nameMap.set].call(this, config[name]);\n
                    delete this[getName];\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        beforeInitConfig: Ext.emptyFn,\n
\n
        /**\n
         * @private\n
         */\n
        getCurrentConfig: function() {\n
            var defaultConfig = this.defaultConfig,\n
                configNameCache = Ext.Class.configNameCache,\n
                config = {},\n
                name, nameMap;\n
\n
            for (name in defaultConfig) {\n
                nameMap = configNameCache[name];\n
                config[name] = this[nameMap.get].call(this);\n
            }\n
\n
            return config;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        setConfig: function(config, applyIfNotSet) {\n
            if (!config) {\n
                return this;\n
            }\n
\n
            var configNameCache = Ext.Class.configNameCache,\n
                currentConfig = this.config,\n
                defaultConfig = this.defaultConfig,\n
                initialConfig = this.initialConfig,\n
                configList = [],\n
                name, i, ln, nameMap;\n
\n
            applyIfNotSet = Boolean(applyIfNotSet);\n
\n
            for (name in config) {\n
                if ((applyIfNotSet && (name in initialConfig))) {\n
                    continue;\n
                }\n
\n
                currentConfig[name] = config[name];\n
\n
                if (name in defaultConfig) {\n
                    configList.push(name);\n
                    nameMap = configNameCache[name];\n
                    this[nameMap.get] = this[nameMap.initGet];\n
                }\n
            }\n
\n
            for (i = 0,ln = configList.length; i < ln; i++) {\n
                name = configList[i];\n
                nameMap = configNameCache[name];\n
                this[nameMap.set].call(this, config[name]);\n
                delete this[nameMap.get];\n
            }\n
\n
            return this;\n
        },\n
\n
        set: function(name, value) {\n
            return this[Ext.Class.configNameCache[name].set].call(this, value);\n
        },\n
\n
        get: function(name) {\n
            return this[Ext.Class.configNameCache[name].get].call(this);\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        getConfig: function(name) {\n
            return this[Ext.Class.configNameCache[name].get].call(this);\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        hasConfig: function(name) {\n
            return (name in this.defaultConfig);\n
        },\n
\n
        /**\n
         * Returns the initial configuration passed to constructor.\n
         *\n
         * @param {String} [name] When supplied, value for particular configuration\n
         * option is returned, otherwise the full config object is returned.\n
         * @return {Object/Mixed}\n
         */\n
        getInitialConfig: function(name) {\n
            var config = this.config;\n
\n
            if (!name) {\n
                return config;\n
            }\n
            else {\n
                return config[name];\n
            }\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        onConfigUpdate: function(names, callback, scope) {\n
            var self = this.self,\n
                //<debug>\n
                className = self.$className,\n
                //</debug>\n
                i, ln, name,\n
                updaterName, updater, newUpdater;\n
\n
            names = Ext.Array.from(names);\n
\n
            scope = scope || this;\n
\n
            for (i = 0,ln = names.length; i < ln; i++) {\n
                name = names[i];\n
                updaterName = \'update\' + Ext.String.capitalize(name);\n
                updater = this[updaterName] || Ext.emptyFn;\n
                newUpdater = function() {\n
                    updater.apply(this, arguments);\n
                    scope[callback].apply(scope, arguments);\n
                };\n
                newUpdater.$name = updaterName;\n
                newUpdater.$owner = self;\n
                //<debug>\n
                newUpdater.displayName = className + \'#\' + updaterName;\n
                //</debug>\n
\n
                this[updaterName] = newUpdater;\n
            }\n
        },\n
        //</feature>\n
\n
        /**\n
         * @private\n
         * @param name\n
         * @param value\n
         * @return {Mixed}\n
         */\n
        link: function(name, value) {\n
            this.$links = {};\n
            this.link = this.doLink;\n
            return this.link.apply(this, arguments);\n
        },\n
\n
        doLink: function(name, value) {\n
            this.$links[name] = true;\n
\n
            this[name] = value;\n
\n
            return value;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        unlink: function() {\n
            var i, ln, link, value;\n
\n
            for (i = 0, ln = arguments.length; i < ln; i++) {\n
                link = arguments[i];\n
                if (this.hasOwnProperty(link)) {\n
                    value = this[link];\n
                    if (value) {\n
                        if (value.isInstance && !value.isDestroyed) {\n
                            value.destroy();\n
                        }\n
                        else if (value.parentNode && \'nodeType\' in value) {\n
                            value.parentNode.removeChild(value);\n
                        }\n
                    }\n
                    delete this[link];\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @protected\n
         */\n
        destroy: function() {\n
            this.destroy = Ext.emptyFn;\n
            this.isDestroyed = true;\n
\n
            if (this.hasOwnProperty(\'$links\')) {\n
                this.unlink.apply(this, Ext.Object.getKeys(this.$links));\n
                delete this.$links;\n
            }\n
        }\n
    });\n
\n
    Ext.Base = Base;\n
\n
})(Ext.Function.flexSetter);\n
\n
//@tag foundation,core\n
//@define Ext.Class\n
//@require Ext.Base\n
\n
/**\n
 * @class Ext.Class\n
 *\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @aside guide class_system\n
 * @aside video class-system\n
 *\n
 * Handles class creation throughout the framework. This is a low level factory that is used by Ext.ClassManager and generally\n
 * should not be used directly. If you choose to use Ext.Class you will lose out on the namespace, aliasing and dependency loading\n
 * features made available by Ext.ClassManager. The only time you would use Ext.Class directly is to create an anonymous class.\n
 *\n
 * If you wish to create a class you should use {@link Ext#define Ext.define} which aliases\n
 * {@link Ext.ClassManager#create Ext.ClassManager.create} to enable namespacing and dynamic dependency resolution.\n
 *\n
 * Ext.Class is the factory and **not** the superclass of everything. For the base class that **all** Ext classes inherit\n
 * from, see {@link Ext.Base}.\n
 */\n
(function() {\n
    var ExtClass,\n
        Base = Ext.Base,\n
        baseStaticMembers = [],\n
        baseStaticMember, baseStaticMemberLength;\n
\n
    for (baseStaticMember in Base) {\n
        if (Base.hasOwnProperty(baseStaticMember)) {\n
            baseStaticMembers.push(baseStaticMember);\n
        }\n
    }\n
\n
    baseStaticMemberLength = baseStaticMembers.length;\n
\n
    /**\n
     * @method constructor\n
     * Creates a new anonymous class.\n
     *\n
     * @param {Object} data An object represent the properties of this class.\n
     * @param {Function} onCreated (optional) The callback function to be executed when this class is fully created.\n
     * Note that the creation process can be asynchronous depending on the pre-processors used.\n
     *\n
     * @return {Ext.Base} The newly created class\n
     */\n
    Ext.Class = ExtClass = function(Class, data, onCreated) {\n
        if (typeof Class != \'function\') {\n
            onCreated = data;\n
            data = Class;\n
            Class = null;\n
        }\n
\n
        if (!data) {\n
            data = {};\n
        }\n
\n
        Class = ExtClass.create(Class);\n
\n
        ExtClass.process(Class, data, onCreated);\n
\n
        return Class;\n
    };\n
\n
    Ext.apply(ExtClass, {\n
        /**\n
         * @private\n
         * @static\n
         */\n
        onBeforeCreated: function(Class, data, hooks) {\n
            Class.addMembers(data);\n
\n
            hooks.onCreated.call(Class, Class);\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        create: function(Class) {\n
            var name, i;\n
\n
            if (!Class) {\n
                Class = function() {\n
                    return this.constructor.apply(this, arguments);\n
                };\n
            }\n
\n
            for (i = 0; i < baseStaticMemberLength; i++) {\n
                name = baseStaticMembers[i];\n
                Class[name] = Base[name];\n
            }\n
\n
            return Class;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        process: function(Class, data, onCreated) {\n
            var preprocessorStack = data.preprocessors || ExtClass.defaultPreprocessors,\n
                preprocessors = this.preprocessors,\n
                hooks = {\n
                    onBeforeCreated: this.onBeforeCreated,\n
                    onCreated: onCreated || Ext.emptyFn\n
                },\n
                index = 0,\n
                name, preprocessor, properties,\n
                i, ln, fn, property, process;\n
\n
            delete data.preprocessors;\n
\n
            process = function(Class, data, hooks) {\n
                fn = null;\n
\n
                while (fn === null) {\n
                    name = preprocessorStack[index++];\n
\n
                    if (name) {\n
                        preprocessor = preprocessors[name];\n
                        properties = preprocessor.properties;\n
\n
                        if (properties === true) {\n
                            fn = preprocessor.fn;\n
                        }\n
                        else {\n
                            for (i = 0,ln = properties.length; i < ln; i++) {\n
                                property = properties[i];\n
\n
                                if (data.hasOwnProperty(property)) {\n
                                    fn = preprocessor.fn;\n
                                    break;\n
                                }\n
                            }\n
                        }\n
                    }\n
                    else {\n
                        hooks.onBeforeCreated.apply(this, arguments);\n
                        return;\n
                    }\n
                }\n
\n
                if (fn.call(this, Class, data, hooks, process) !== false) {\n
                    process.apply(this, arguments);\n
                }\n
            };\n
\n
            process.call(this, Class, data, hooks);\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        preprocessors: {},\n
\n
        /**\n
         * Register a new pre-processor to be used during the class creation process.\n
         *\n
         * @private\n
         * @static\n
         * @param {String} name The pre-processor\'s name.\n
         * @param {Function} fn The callback function to be executed. Typical format:\n
         *\n
         *     function(cls, data, fn) {\n
         *         // Your code here\n
         *\n
         *         // Execute this when the processing is finished.\n
         *         // Asynchronous processing is perfectly OK\n
         *         if (fn) {\n
         *             fn.call(this, cls, data);\n
         *         }\n
         *     });\n
         *\n
         * @param {Function} fn.cls The created class.\n
         * @param {Object} fn.data The set of properties passed in {@link Ext.Class} constructor.\n
         * @param {Function} fn.fn The callback function that __must__ to be executed when this pre-processor finishes,\n
         * regardless of whether the processing is synchronous or asynchronous.\n
         *\n
         * @return {Ext.Class} this\n
         */\n
        registerPreprocessor: function(name, fn, properties, position, relativeTo) {\n
            if (!position) {\n
                position = \'last\';\n
            }\n
\n
            if (!properties) {\n
                properties = [name];\n
            }\n
\n
            this.preprocessors[name] = {\n
                name: name,\n
                properties: properties || false,\n
                fn: fn\n
            };\n
\n
            this.setDefaultPreprocessorPosition(name, position, relativeTo);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Retrieve a pre-processor callback function by its name, which has been registered before.\n
         *\n
         * @private\n
         * @static\n
         * @param {String} name\n
         * @return {Function} preprocessor\n
         */\n
        getPreprocessor: function(name) {\n
            return this.preprocessors[name];\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        getPreprocessors: function() {\n
            return this.preprocessors;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        defaultPreprocessors: [],\n
\n
        /**\n
         * Retrieve the array stack of default pre-processors.\n
         * @private\n
         * @static\n
         * @return {Function} defaultPreprocessors\n
         */\n
        getDefaultPreprocessors: function() {\n
            return this.defaultPreprocessors;\n
        },\n
\n
        /**\n
         * Set the default array stack of default pre-processors.\n
         *\n
         * @private\n
         * @static\n
         * @param {Array} preprocessors\n
         * @return {Ext.Class} this\n
         */\n
        setDefaultPreprocessors: function(preprocessors) {\n
            this.defaultPreprocessors = Ext.Array.from(preprocessors);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Insert this pre-processor at a specific position in the stack, optionally relative to\n
         * any existing pre-processor. For example:\n
         *\n
         *     Ext.Class.registerPreprocessor(\'debug\', function(cls, data, fn) {\n
         *         // Your code here\n
         *\n
         *         if (fn) {\n
         *             fn.call(this, cls, data);\n
         *         }\n
         *     }).insertDefaultPreprocessor(\'debug\', \'last\');\n
         *\n
         * @private\n
         * @static\n
         * @param {String} name The pre-processor name. Note that it needs to be registered with\n
         * {@link Ext.Class#registerPreprocessor registerPreprocessor} before this.\n
         * @param {String} offset The insertion position. Four possible values are:\n
         * \'first\', \'last\', or: \'before\', \'after\' (relative to the name provided in the third argument).\n
         * @param {String} relativeName\n
         * @return {Ext.Class} this\n
         */\n
        setDefaultPreprocessorPosition: function(name, offset, relativeName) {\n
            var defaultPreprocessors = this.defaultPreprocessors,\n
                index;\n
\n
            if (typeof offset == \'string\') {\n
                if (offset === \'first\') {\n
                    defaultPreprocessors.unshift(name);\n
\n
                    return this;\n
                }\n
                else if (offset === \'last\') {\n
                    defaultPreprocessors.push(name);\n
\n
                    return this;\n
                }\n
\n
                offset = (offset === \'after\') ? 1 : -1;\n
            }\n
\n
            index = Ext.Array.indexOf(defaultPrepr

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

ocessors, relativeName);\n
\n
            if (index !== -1) {\n
                Ext.Array.splice(defaultPreprocessors, Math.max(0, index + offset), 0, name);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        configNameCache: {},\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        getConfigNameMap: function(name) {\n
            var cache = this.configNameCache,\n
                map = cache[name],\n
                capitalizedName;\n
\n
            if (!map) {\n
                capitalizedName = name.charAt(0).toUpperCase() + name.substr(1);\n
\n
                map = cache[name] = {\n
                    name: name,\n
                    internal: \'_\' + name,\n
                    initializing: \'is\' + capitalizedName + \'Initializing\',\n
                    apply: \'apply\' + capitalizedName,\n
                    update: \'update\' + capitalizedName,\n
                    set: \'set\' + capitalizedName,\n
                    get: \'get\' + capitalizedName,\n
                    initGet: \'initGet\' + capitalizedName,\n
                    doSet : \'doSet\' + capitalizedName,\n
                    changeEvent: name.toLowerCase() + \'change\'\n
                }\n
            }\n
\n
            return map;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        generateSetter: function(nameMap) {\n
            var internalName = nameMap.internal,\n
                getName = nameMap.get,\n
                applyName = nameMap.apply,\n
                updateName = nameMap.update,\n
                setter;\n
\n
            setter = function(value) {\n
                var oldValue = this[internalName],\n
                    applier = this[applyName],\n
                    updater = this[updateName];\n
\n
                delete this[getName];\n
\n
                if (applier) {\n
                    value = applier.call(this, value, oldValue);\n
                }\n
\n
                if (typeof value != \'undefined\') {\n
                    this[internalName] = value;\n
\n
                    if (updater && value !== oldValue) {\n
                        updater.call(this, value, oldValue);\n
                    }\n
                }\n
\n
                return this;\n
            };\n
\n
            setter.$isDefault = true;\n
\n
            return setter;\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        generateInitGetter: function(nameMap) {\n
            var name = nameMap.name,\n
                setName = nameMap.set,\n
                getName = nameMap.get,\n
                initializingName = nameMap.initializing;\n
\n
            return function() {\n
                this[initializingName] = true;\n
                delete this[getName];\n
\n
                this[setName].call(this, this.config[name]);\n
                delete this[initializingName];\n
\n
                return this[getName].apply(this, arguments);\n
            }\n
        },\n
\n
        /**\n
         * @private\n
         * @static\n
         */\n
        generateGetter: function(nameMap) {\n
            var internalName = nameMap.internal;\n
\n
            return function() {\n
                return this[internalName];\n
            }\n
        }\n
    });\n
\n
    /**\n
     * @cfg {String} extend\n
     * The parent class that this class extends. For example:\n
     *\n
     *     @example\n
     *     Ext.define(\'Person\', {\n
     *         say: function(text) {\n
     *             alert(text);\n
     *         }\n
     *     });\n
     *\n
     *     Ext.define(\'Developer\', {\n
     *         extend: \'Person\',\n
     *         say: function(text) {\n
     *             this.callParent(["print " + text]);\n
     *         }\n
     *     });\n
     *\n
     *     var person1 = Ext.create("Person");\n
     *     person1.say("Bill");\n
     *\n
     *     var developer1 = Ext.create("Developer");\n
     *     developer1.say("Ted");\n
     */\n
    ExtClass.registerPreprocessor(\'extend\', function(Class, data) {\n
        var Base = Ext.Base,\n
            extend = data.extend,\n
            Parent;\n
\n
        delete data.extend;\n
\n
        if (extend && extend !== Object) {\n
            Parent = extend;\n
        }\n
        else {\n
            Parent = Base;\n
        }\n
\n
        Class.extend(Parent);\n
\n
        Class.triggerExtended.apply(Class, arguments);\n
\n
        if (data.onClassExtended) {\n
            Class.onExtended(data.onClassExtended, Class);\n
            delete data.onClassExtended;\n
        }\n
\n
    }, true);\n
\n
    //<feature classSystem.statics>\n
    /**\n
     * @cfg {Object} statics\n
     * List of static methods for this class. For example:\n
     *\n
     *     Ext.define(\'Computer\', {\n
     *          statics: {\n
     *              factory: function(brand) {\n
     *                  // \'this\' in static methods refer to the class itself\n
     *                  return new this(brand);\n
     *              }\n
     *          },\n
     *\n
     *          constructor: function() {\n
     *              // ...\n
     *          }\n
     *     });\n
     *\n
     *     var dellComputer = Computer.factory(\'Dell\');\n
     */\n
    ExtClass.registerPreprocessor(\'statics\', function(Class, data) {\n
        Class.addStatics(data.statics);\n
\n
        delete data.statics;\n
    });\n
    //</feature>\n
\n
    //<feature classSystem.inheritableStatics>\n
    /**\n
     * @cfg {Object} inheritableStatics\n
     * List of inheritable static methods for this class.\n
     * Otherwise just like {@link #statics} but subclasses inherit these methods.\n
     */\n
    ExtClass.registerPreprocessor(\'inheritableStatics\', function(Class, data) {\n
        Class.addInheritableStatics(data.inheritableStatics);\n
\n
        delete data.inheritableStatics;\n
    });\n
    //</feature>\n
\n
    //<feature classSystem.config>\n
    /**\n
     * @cfg {Object} config\n
     *\n
     * List of configuration options with their default values.\n
     *\n
     * __Note:__ You need to make sure {@link Ext.Base#initConfig} is called from your constructor if you are defining\n
     * your own class or singleton, unless you are extending a Component. Otherwise the generated getter and setter\n
     * methods will not be initialized.\n
     *\n
     * Each config item will have its own setter and getter method automatically generated inside the class prototype\n
     * during class creation time, if the class does not have those methods explicitly defined.\n
     *\n
     * As an example, let\'s convert the name property of a Person class to be a config item, then add extra age and\n
     * gender items.\n
     *\n
     *     Ext.define(\'My.sample.Person\', {\n
     *         config: {\n
     *             name: \'Mr. Unknown\',\n
     *             age: 0,\n
     *             gender: \'Male\'\n
     *         },\n
     *\n
     *         constructor: function(config) {\n
     *             this.initConfig(config);\n
     *\n
     *             return this;\n
     *         }\n
     *\n
     *         // ...\n
     *     });\n
     *\n
     * Within the class, this.name still has the default value of "Mr. Unknown". However, it\'s now publicly accessible\n
     * without sacrificing encapsulation, via setter and getter methods.\n
     *\n
     *     var jacky = new Person({\n
     *         name: "Jacky",\n
     *         age: 35\n
     *     });\n
     *\n
     *     alert(jacky.getAge());      // alerts 35\n
     *     alert(jacky.getGender());   // alerts "Male"\n
     *\n
     *     jacky.walk(10);             // alerts "Jacky is walking 10 steps"\n
     *\n
     *     jacky.setName("Mr. Nguyen");\n
     *     alert(jacky.getName());     // alerts "Mr. Nguyen"\n
     *\n
     *     jacky.walk(10);             // alerts "Mr. Nguyen is walking 10 steps"\n
     *\n
     * Notice that we changed the class constructor to invoke this.initConfig() and pass in the provided config object.\n
     * Two key things happened:\n
     *\n
     *  - The provided config object when the class is instantiated is recursively merged with the default config object.\n
     *  - All corresponding setter methods are called with the merged values.\n
     *\n
     * Beside storing the given values, throughout the frameworks, setters generally have two key responsibilities:\n
     *\n
     *  - Filtering / validation / transformation of the given value before it\'s actually stored within the instance.\n
     *  - Notification (such as firing events) / post-processing after the value has been set, or changed from a\n
     *    previous value.\n
     *\n
     * By standardize this common pattern, the default generated setters provide two extra template methods that you\n
     * can put your own custom logics into, i.e: an "applyFoo" and "updateFoo" method for a "foo" config item, which are\n
     * executed before and after the value is actually set, respectively. Back to the example class, let\'s validate that\n
     * age must be a valid positive number, and fire an \'agechange\' if the value is modified.\n
     *\n
     *     Ext.define(\'My.sample.Person\', {\n
     *         config: {\n
     *             // ...\n
     *         },\n
     *\n
     *         constructor: {\n
     *             // ...\n
     *         },\n
     *\n
     *         applyAge: function(age) {\n
     *             if (typeof age !== \'number\' || age < 0) {\n
     *                 console.warn("Invalid age, must be a positive number");\n
     *                 return;\n
     *             }\n
     *\n
     *             return age;\n
     *         },\n
     *\n
     *         updateAge: function(newAge, oldAge) {\n
     *             // age has changed from "oldAge" to "newAge"\n
     *             this.fireEvent(\'agechange\', this, newAge, oldAge);\n
     *         }\n
     *\n
     *         // ...\n
     *     });\n
     *\n
     *     var jacky = new Person({\n
     *         name: "Jacky",\n
     *         age: \'invalid\'\n
     *     });\n
     *\n
     *     alert(jacky.getAge());      // alerts 0\n
     *\n
     *     alert(jacky.setAge(-100));  // alerts 0\n
     *     alert(jacky.getAge());      // alerts 0\n
     *\n
     *     alert(jacky.setAge(35));    // alerts 0\n
     *     alert(jacky.getAge());      // alerts 35\n
     *\n
     * In other words, when leveraging the config feature, you mostly never need to define setter and getter methods\n
     * explicitly. Instead, "apply*" and "update*" methods should be implemented where necessary. Your code will be\n
     * consistent throughout and only contain the minimal logic that you actually care about.\n
     *\n
     * When it comes to inheritance, the default config of the parent class is automatically, recursively merged with\n
     * the child\'s default config. The same applies for mixins.\n
     */\n
    ExtClass.registerPreprocessor(\'config\', function(Class, data) {\n
        var config = data.config,\n
            prototype = Class.prototype,\n
            defaultConfig = prototype.config,\n
            nameMap, name, setName, getName, initGetName, internalName, value;\n
\n
        delete data.config;\n
\n
        for (name in config) {\n
            // Once per config item, per class hierarchy\n
            if (config.hasOwnProperty(name) && !(name in defaultConfig)) {\n
                value = config[name];\n
                nameMap = this.getConfigNameMap(name);\n
                setName = nameMap.set;\n
                getName = nameMap.get;\n
                initGetName = nameMap.initGet;\n
                internalName = nameMap.internal;\n
\n
                data[initGetName] = this.generateInitGetter(nameMap);\n
\n
                if (value === null && !data.hasOwnProperty(internalName)) {\n
                    data[internalName] = null;\n
                }\n
\n
                if (!data.hasOwnProperty(getName)) {\n
                    data[getName] = this.generateGetter(nameMap);\n
                }\n
\n
                if (!data.hasOwnProperty(setName)) {\n
                    data[setName] = this.generateSetter(nameMap);\n
                }\n
            }\n
        }\n
\n
        Class.addConfig(config, true);\n
    });\n
    //</feature>\n
\n
    //<feature classSystem.mixins>\n
    /**\n
     * @cfg {Object} mixins\n
     * List of classes to mix into this class. For example:\n
     *\n
     *     Ext.define(\'CanSing\', {\n
     *          sing: function() {\n
     *              alert("I\'m on the highway to hell...");\n
     *          }\n
     *     });\n
     *\n
     *     Ext.define(\'Musician\', {\n
     *          extend: \'Person\',\n
     *\n
     *          mixins: {\n
     *              canSing: \'CanSing\'\n
     *          }\n
     *     });\n
     */\n
    ExtClass.registerPreprocessor(\'mixins\', function(Class, data, hooks) {\n
        var mixins = data.mixins,\n
            name, mixin, i, ln;\n
\n
        delete data.mixins;\n
\n
        Ext.Function.interceptBefore(hooks, \'onCreated\', function() {\n
            if (mixins instanceof Array) {\n
                for (i = 0,ln = mixins.length; i < ln; i++) {\n
                    mixin = mixins[i];\n
                    name = mixin.prototype.mixinId || mixin.$className;\n
\n
                    Class.mixin(name, mixin);\n
                }\n
            }\n
            else {\n
                for (name in mixins) {\n
                    if (mixins.hasOwnProperty(name)) {\n
                        Class.mixin(name, mixins[name]);\n
                    }\n
                }\n
            }\n
        });\n
    });\n
    //</feature>\n
\n
    //<feature classSystem.backwardsCompatible>\n
    // Backwards compatible\n
    Ext.extend = function(Class, Parent, members) {\n
        if (arguments.length === 2 && Ext.isObject(Parent)) {\n
            members = Parent;\n
            Parent = Class;\n
            Class = null;\n
        }\n
\n
        var cls;\n
\n
        if (!Parent) {\n
            throw new Error("[Ext.extend] Attempting to extend from a class which has not been loaded on the page.");\n
        }\n
\n
        members.extend = Parent;\n
        members.preprocessors = [\n
            \'extend\'\n
            //<feature classSystem.statics>\n
            ,\'statics\'\n
            //</feature>\n
            //<feature classSystem.inheritableStatics>\n
            ,\'inheritableStatics\'\n
            //</feature>\n
            //<feature classSystem.mixins>\n
            ,\'mixins\'\n
            //</feature>\n
            //<feature classSystem.config>\n
            ,\'config\'\n
            //</feature>\n
        ];\n
\n
        if (Class) {\n
            cls = new ExtClass(Class, members);\n
        }\n
        else {\n
            cls = new ExtClass(members);\n
        }\n
\n
        cls.prototype.override = function(o) {\n
            for (var m in o) {\n
                if (o.hasOwnProperty(m)) {\n
                    this[m] = o[m];\n
                }\n
            }\n
        };\n
\n
        return cls;\n
    };\n
    //</feature>\n
})();\n
\n
//@tag foundation,core\n
//@define Ext.ClassManager\n
//@require Ext.Class\n
\n
/**\n
 * @class  Ext.ClassManager\n
 *\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @aside guide class_system\n
 * @aside video class-system\n
 *\n
 * Ext.ClassManager manages all classes and handles mapping from string class name to\n
 * actual class objects throughout the whole framework. It is not generally accessed directly, rather through\n
 * these convenient shorthands:\n
 *\n
 * - {@link Ext#define Ext.define}\n
 * - {@link Ext.ClassManager#create Ext.create}\n
 * - {@link Ext#widget Ext.widget}\n
 * - {@link Ext#getClass Ext.getClass}\n
 * - {@link Ext#getClassName Ext.getClassName}\n
 *\n
 * ## Basic syntax:\n
 *\n
 *     Ext.define(className, properties);\n
 *\n
 * in which `properties` is an object represent a collection of properties that apply to the class. See\n
 * {@link Ext.ClassManager#create} for more detailed instructions.\n
 *\n
 *     @example\n
 *     Ext.define(\'Person\', {\n
 *          name: \'Unknown\',\n
 *\n
 *          constructor: function(name) {\n
 *              if (name) {\n
 *                  this.name = name;\n
 *              }\n
 *\n
 *              return this;\n
 *          },\n
 *\n
 *          eat: function(foodType) {\n
 *              alert("I\'m eating: " + foodType);\n
 *\n
 *              return this;\n
 *          }\n
 *     });\n
 *\n
 *     var aaron = new Person("Aaron");\n
 *     aaron.eat("Sandwich"); // alert("I\'m eating: Sandwich");\n
 *\n
 * Ext.Class has a powerful set of extensible {@link Ext.Class#registerPreprocessor pre-processors} which takes care of\n
 * everything related to class creation, including but not limited to inheritance, mixins, configuration, statics, etc.\n
 *\n
 * ## Inheritance:\n
 *\n
 *     Ext.define(\'Developer\', {\n
 *          extend: \'Person\',\n
 *\n
 *          constructor: function(name, isGeek) {\n
 *              this.isGeek = isGeek;\n
 *\n
 *              // Apply a method from the parent class\' prototype\n
 *              this.callParent([name]);\n
 *\n
 *              return this;\n
 *\n
 *          },\n
 *\n
 *          code: function(language) {\n
 *              alert("I\'m coding in: " + language);\n
 *\n
 *              this.eat("Bugs");\n
 *\n
 *              return this;\n
 *          }\n
 *     });\n
 *\n
 *     var jacky = new Developer("Jacky", true);\n
 *     jacky.code("JavaScript"); // alert("I\'m coding in: JavaScript");\n
 *                               // alert("I\'m eating: Bugs");\n
 *\n
 * See {@link Ext.Base#callParent} for more details on calling superclass\' methods\n
 *\n
 * ## Mixins:\n
 *\n
 *     Ext.define(\'CanPlayGuitar\', {\n
 *          playGuitar: function() {\n
 *             alert("F#...G...D...A");\n
 *          }\n
 *     });\n
 *\n
 *     Ext.define(\'CanComposeSongs\', {\n
 *          composeSongs: function() { }\n
 *     });\n
 *\n
 *     Ext.define(\'CanSing\', {\n
 *          sing: function() {\n
 *              alert("I\'m on the highway to hell...");\n
 *          }\n
 *     });\n
 *\n
 *     Ext.define(\'Musician\', {\n
 *          extend: \'Person\',\n
 *\n
 *          mixins: {\n
 *              canPlayGuitar: \'CanPlayGuitar\',\n
 *              canComposeSongs: \'CanComposeSongs\',\n
 *              canSing: \'CanSing\'\n
 *          }\n
 *     });\n
 *\n
 *     Ext.define(\'CoolPerson\', {\n
 *          extend: \'Person\',\n
 *\n
 *          mixins: {\n
 *              canPlayGuitar: \'CanPlayGuitar\',\n
 *              canSing: \'CanSing\'\n
 *          },\n
 *\n
 *          sing: function() {\n
 *              alert("Ahem...");\n
 *\n
 *              this.mixins.canSing.sing.call(this);\n
 *\n
 *              alert("[Playing guitar at the same time...]");\n
 *\n
 *              this.playGuitar();\n
 *          }\n
 *     });\n
 *\n
 *     var me = new CoolPerson("Jacky");\n
 *\n
 *     me.sing(); // alert("Ahem...");\n
 *                // alert("I\'m on the highway to hell...");\n
 *                // alert("[Playing guitar at the same time...]");\n
 *                // alert("F#...G...D...A");\n
 *\n
 * ## Config:\n
 *\n
 *     Ext.define(\'SmartPhone\', {\n
 *          config: {\n
 *              hasTouchScreen: false,\n
 *              operatingSystem: \'Other\',\n
 *              price: 500\n
 *          },\n
 *\n
 *          isExpensive: false,\n
 *\n
 *          constructor: function(config) {\n
 *              this.initConfig(config);\n
 *\n
 *              return this;\n
 *          },\n
 *\n
 *          applyPrice: function(price) {\n
 *              this.isExpensive = (price > 500);\n
 *\n
 *              return price;\n
 *          },\n
 *\n
 *          applyOperatingSystem: function(operatingSystem) {\n
 *              if (!(/^(iOS|Android|BlackBerry)$/i).test(operatingSystem)) {\n
 *                  return \'Other\';\n
 *              }\n
 *\n
 *              return operatingSystem;\n
 *          }\n
 *     });\n
 *\n
 *     var iPhone = new SmartPhone({\n
 *          hasTouchScreen: true,\n
 *          operatingSystem: \'iOS\'\n
 *     });\n
 *\n
 *     iPhone.getPrice(); // 500;\n
 *     iPhone.getOperatingSystem(); // \'iOS\'\n
 *     iPhone.getHasTouchScreen(); // true;\n
 *\n
 *     iPhone.isExpensive; // false;\n
 *     iPhone.setPrice(600);\n
 *     iPhone.getPrice(); // 600\n
 *     iPhone.isExpensive; // true;\n
 *\n
 *     iPhone.setOperatingSystem(\'AlienOS\');\n
 *     iPhone.getOperatingSystem(); // \'Other\'\n
 *\n
 * ## Statics:\n
 *\n
 *     Ext.define(\'Computer\', {\n
 *          statics: {\n
 *              factory: function(brand) {\n
 *                 // \'this\' in static methods refer to the class itself\n
 *                  return new this(brand);\n
 *              }\n
 *          },\n
 *\n
 *          constructor: function() { }\n
 *     });\n
 *\n
 *     var dellComputer = Computer.factory(\'Dell\');\n
 *\n
 * Also see {@link Ext.Base#statics} and {@link Ext.Base#self} for more details on accessing\n
 * static properties within class methods\n
 *\n
 * @singleton\n
 */\n
(function(Class, alias, arraySlice, arrayFrom, global) {\n
    var Manager = Ext.ClassManager = {\n
\n
        /**\n
         * @property classes\n
         * @type Object\n
         * All classes which were defined through the ClassManager. Keys are the\n
         * name of the classes and the values are references to the classes.\n
         * @private\n
         */\n
        classes: {},\n
\n
        /**\n
         * @private\n
         */\n
        existCache: {},\n
\n
        /**\n
         * @private\n
         */\n
        namespaceRewrites: [{\n
            from: \'Ext.\',\n
            to: Ext\n
        }],\n
\n
        /**\n
         * @private\n
         */\n
        maps: {\n
            alternateToName: {},\n
            aliasToName: {},\n
            nameToAliases: {},\n
            nameToAlternates: {}\n
        },\n
\n
        /** @private */\n
        enableNamespaceParseCache: true,\n
\n
        /** @private */\n
        namespaceParseCache: {},\n
\n
        /** @private */\n
        instantiators: [],\n
\n
        /**\n
         * Checks if a class has already been created.\n
         *\n
         * @param {String} className\n
         * @return {Boolean} exist\n
         */\n
        isCreated: function(className) {\n
            var existCache = this.existCache,\n
                i, ln, part, root, parts;\n
\n
            //<debug error>\n
            if (typeof className != \'string\' || className.length < 1) {\n
                throw new Error("[Ext.ClassManager] Invalid classname, must be a string and must not be empty");\n
            }\n
            //</debug>\n
\n
            if (this.classes[className] || existCache[className]) {\n
                return true;\n
            }\n
\n
            root = global;\n
            parts = this.parseNamespace(className);\n
\n
            for (i = 0, ln = parts.length; i < ln; i++) {\n
                part = parts[i];\n
\n
                if (typeof part != \'string\') {\n
                    root = part;\n
                } else {\n
                    if (!root || !root[part]) {\n
                        return false;\n
                    }\n
\n
                    root = root[part];\n
                }\n
            }\n
\n
            existCache[className] = true;\n
\n
            this.triggerCreated(className);\n
\n
            return true;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        createdListeners: [],\n
\n
        /**\n
         * @private\n
         */\n
        nameCreatedListeners: {},\n
\n
        /**\n
         * @private\n
         */\n
        triggerCreated: function(className) {\n
            var listeners = this.createdListeners,\n
                nameListeners = this.nameCreatedListeners,\n
                alternateNames = this.maps.nameToAlternates[className],\n
                names = [className],\n
                i, ln, j, subLn, listener, name;\n
\n
            for (i = 0,ln = listeners.length; i < ln; i++) {\n
                listener = listeners[i];\n
                listener.fn.call(listener.scope, className);\n
            }\n
\n
            if (alternateNames) {\n
                names.push.apply(names, alternateNames);\n
            }\n
\n
            for (i = 0,ln = names.length; i < ln; i++) {\n
                name = names[i];\n
                listeners = nameListeners[name];\n
\n
                if (listeners) {\n
                    for (j = 0,subLn = listeners.length; j < subLn; j++) {\n
                        listener = listeners[j];\n
                        listener.fn.call(listener.scope, name);\n
                    }\n
                    delete nameListeners[name];\n
                }\n
            }\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        onCreated: function(fn, scope, className) {\n
            var listeners = this.createdListeners,\n
                nameListeners = this.nameCreatedListeners,\n
                listener = {\n
                    fn: fn,\n
                    scope: scope\n
                };\n
\n
            if (className) {\n
                if (this.isCreated(className)) {\n
                    fn.call(scope, className);\n
                    return;\n
                }\n
\n
                if (!nameListeners[className]) {\n
                    nameListeners[className] = [];\n
                }\n
\n
                nameListeners[className].push(listener);\n
            }\n
            else {\n
                listeners.push(listener);\n
            }\n
        },\n
\n
        /**\n
         * Supports namespace rewriting.\n
         * @private\n
         */\n
        parseNamespace: function(namespace) {\n
            //<debug error>\n
            if (typeof namespace != \'string\') {\n
                throw new Error("[Ext.ClassManager] Invalid namespace, must be a string");\n
            }\n
            //</debug>\n
\n
            var cache = this.namespaceParseCache;\n
\n
            if (this.enableNamespaceParseCache) {\n
                if (cache.hasOwnProperty(namespace)) {\n
                    return cache[namespace];\n
                }\n
            }\n
\n
            var parts = [],\n
                rewrites = this.namespaceRewrites,\n
                root = global,\n
                name = namespace,\n
                rewrite, from, to, i, ln;\n
\n
            for (i = 0, ln = rewrites.length; i < ln; i++) {\n
                rewrite = rewrites[i];\n
                from = rewrite.from;\n
                to = rewrite.to;\n
\n
                if (name === from || name.substring(0, from.length) === from) {\n
                    name = name.substring(from.length);\n
\n
                    if (typeof to != \'string\') {\n
                        root = to;\n
                    } else {\n
                        parts = parts.concat(to.split(\'.\'));\n
                    }\n
\n
                    break;\n
                }\n
            }\n
\n
            parts.push(root);\n
\n
            parts = parts.concat(name.split(\'.\'));\n
\n
            if (this.enableNamespaceParseCache) {\n
                cache[namespace] = parts;\n
            }\n
\n
            return parts;\n
        },\n
\n
        /**\n
         * Creates a namespace and assign the `value` to the created object.\n
         *\n
         *     Ext.ClassManager.setNamespace(\'MyCompany.pkg.Example\', someObject);\n
         *     alert(MyCompany.pkg.Example === someObject); // alerts true\n
         *\n
         * @param {String} name\n
         * @param {Mixed} value\n
         */\n
        setNamespace: function(name, value) {\n
            var root = global,\n
                parts = this.parseNamespace(name),\n
                ln = parts.length - 1,\n
                leaf = parts[ln],\n
                i, part;\n
\n
            for (i = 0; i < ln; i++) {\n
                part = parts[i];\n
\n
                if (typeof part != \'string\') {\n
                    root = part;\n
                } else {\n
                    if (!root[part]) {\n
                        root[part] = {};\n
                    }\n
\n
                    root = root[part];\n
                }\n
            }\n
\n
            root[leaf] = value;\n
\n
            return root[leaf];\n
        },\n
\n
        /**\n
         * The new Ext.ns, supports namespace rewriting.\n
         * @private\n
         */\n
        createNamespaces: function() {\n
            var root = global,\n
                parts, part, i, j, ln, subLn;\n
\n
            for (i = 0, ln = arguments.length; i < ln; i++) {\n
                parts = this.parseNamespace(arguments[i]);\n
\n
                for (j = 0, subLn = parts.length; j < subLn; j++) {\n
                    part = parts[j];\n
\n
                    if (typeof part != \'string\') {\n
                        root = part;\n
                    } else {\n
                        if (!root[part]) {\n
                            root[part] = {};\n
                        }\n
\n
                        root = root[part];\n
                    }\n
                }\n
            }\n
\n
            return root;\n
        },\n
\n
        /**\n
         * Sets a name reference to a class.\n
         *\n
         * @param {String} name\n
         * @param {Object} value\n
         * @return {Ext.ClassManager} this\n
         */\n
        set: function(name, value) {\n
            var me = this,\n
                maps = me.maps,\n
                nameToAlternates = maps.nameToAlternates,\n
                targetName = me.getName(value),\n
                alternates;\n
\n
            me.classes[name] = me.setNamespace(name, value);\n
\n
            if (targetName && targetName !== name) {\n
                maps.alternateToName[name] = targetName;\n
                alternates = nameToAlternates[targetName] || (nameToAlternates[targetName] = []);\n
                alternates.push(name);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Retrieve a class by its name.\n
         *\n
         * @param {String} name\n
         * @return {Ext.Class} class\n
         */\n
        get: function(name) {\n
            var classes = this.classes;\n
\n
            if (classes[name]) {\n
                return classes[name];\n
            }\n
\n
            var root = global,\n
                parts = this.parseNamespace(name),\n
                part, i, ln;\n
\n
            for (i = 0, ln = parts.length; i < ln; i++) {\n
                part = parts[i];\n
\n
                if (typeof part != \'string\') {\n
                    root = part;\n
                } else {\n
                    if (!root || !root[part]) {\n
                        return null;\n
                    }\n
\n
                    root = root[part];\n
                }\n
            }\n
\n
            return root;\n
        },\n
\n
        /**\n
         * Register the alias for a class.\n
         *\n
         * @param {Ext.Class/String} cls a reference to a class or a `className`.\n
         * @param {String} alias Alias to use when referring to this class.\n
         */\n
        setAlias: function(cls, alias) {\n
            var aliasToNameMap = this.maps.aliasToName,\n
                nameToAliasesMap = this.maps.nameToAliases,\n
                className;\n
\n
            if (typeof cls == \'string\') {\n
                className = cls;\n
            } else {\n
                className = this.getName(cls);\n
            }\n
\n
            if (alias && aliasToNameMap[alias] !== className) {\n
                //<debug info>\n
                if (aliasToNameMap[alias]) {\n
                    Ext.Logger.info("[Ext.ClassManager] Overriding existing alias: \'" + alias + "\' " +\n
                        "of: \'" + aliasToNameMap[alias] + "\' with: \'" + className + "\'. Be sure it\'s intentional.");\n
                }\n
                //</debug>\n
\n
                aliasToNameMap[alias] = className;\n
            }\n
\n
            if (!nameToAliasesMap[className]) {\n
                nameToAliasesMap[className] = [];\n
            }\n
\n
            if (alias) {\n
                Ext.Array.include(nameToAliasesMap[className], alias);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Adds a batch of class name to alias mappings\n
         * @param {Object} aliases The set of mappings of the form\n
         * className : [values...]\n
         */\n
        addNameAliasMappings: function(aliases){\n
            var aliasToNameMap = this.maps.aliasToName,\n
                nameToAliasesMap = this.maps.nameToAliases,\n
                className, aliasList, alias, i;\n
\n
            for (className in aliases) {\n
                aliasList = nameToAliasesMap[className] ||\n
                    (nameToAliasesMap[className] = []);\n
\n
                for (i = 0; i < aliases[className].length; i++) {\n
                    alias = aliases[className][i];\n
                    if (!aliasToNameMap[alias]) {\n
                        aliasToNameMap[alias] = className;\n
                        aliasList.push(alias);\n
                    }\n
                }\n
\n
            }\n
            return this;\n
        },\n
\n
        /**\n
         *\n
         * @param {Object} alternates The set of mappings of the form\n
         * className : [values...]\n
         */\n
        addNameAlternateMappings: function(alternates) {\n
            var alternateToName = this.maps.alternateToName,\n
                nameToAlternates = this.maps.nameToAlternates,\n
                className, aliasList, alternate, i;\n
\n
            for (className in alternates) {\n
                aliasList = nameToAlternates[className] ||\n
                    (nameToAlternates[className] = []);\n
\n
                for (i  = 0; i < alternates[className].length; i++) {\n
                    alternate = alternates[className];\n
                    if (!alternateToName[alternate]) {\n
                        alternateToName[alternate] = className;\n
                        aliasList.push(alternate);\n
                    }\n
                }\n
\n
            }\n
            return this;\n
        },\n
\n
        /**\n
         * Get a reference to the class by its alias.\n
         *\n
         * @param {String} alias\n
         * @return {Ext.Class} class\n
         */\n
        getByAlias: function(alias) {\n
            return this.get(this.getNameByAlias(alias));\n
        },\n
\n
        /**\n
         * Get the name of a class by its alias.\n
         *\n
         * @param {String} alias\n
         * @return {String} className\n
         */\n
        getNameByAlias: function(alias) {\n
            return this.maps.aliasToName[alias] || \'\';\n
        },\n
\n
        /**\n
         * Get the name of a class by its alternate name.\n
         *\n
         * @param {String} alternate\n
         * @return {String} className\n
         */\n
        getNameByAlternate: function(alternate) {\n
            return this.maps.alternateToName[alternate] || \'\';\n
        },\n
\n
        /**\n
         * Get the aliases of a class by the class name\n
         *\n
         * @param {String} name\n
         * @return {Array} aliases\n
         */\n
        getAliasesByName: function(name) {\n
            return this.maps.nameToAliases[name] || [];\n
        },\n
\n
        /**\n
         * Get the name of the class by its reference or its instance;\n
         * usually invoked by the shorthand {@link Ext#getClassName Ext.getClassName}\n
         *\n
         *     Ext.ClassManager.getName(Ext.Action); // returns "Ext.Action"\n
         *\n
         * @param {Ext.Class/Object} object\n
         * @return {String} className\n
         */\n
        getName: function(object) {\n
            return object && object.$className || \'\';\n
        },\n
\n
        /**\n
         * Get the class of the provided object; returns null if it\'s not an instance\n
         * of any class created with Ext.define. This is usually invoked by the shorthand {@link Ext#getClass Ext.getClass}.\n
         *\n
         *     var component = new Ext.Component();\n
         *\n
         *     Ext.ClassManager.getClass(component); // returns Ext.Component\n
         *\n
         * @param {Object} object\n
         * @return {Ext.Class} class\n
         */\n
        getClass: function(object) {\n
            return object && object.self || null;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        create: function(className, data, createdFn) {\n
            //<debug error>\n
            if (typeof className != \'string\') {\n
                throw new Error("[Ext.define] Invalid class name \'" + className + "\' specified, must be a non-empty string");\n
            }\n
            //</debug>\n
\n
            data.$className = className;\n
\n
            return new Class(data, function() {\n
                var postprocessorStack = data.postprocessors || Manager.defaultPostprocessors,\n
                    registeredPostprocessors = Manager.postprocessors,\n
                    index = 0,\n
                    postprocessors = [],\n
                    postprocessor, process, i, ln, j, subLn, postprocessorProperties, postprocessorProperty;\n
\n
                delete data.postprocessors;\n
\n
                for (i = 0,ln = postprocessorStack.length; i < ln; i++) {\n
                    postprocessor = postprocessorStack[i];\n
\n
                    if (typeof postprocessor == \'string\') {\n
                        postprocessor = registeredPostprocessors[postprocessor];\n
                        postprocessorProperties = postprocessor.properties;\n
\n
                        if (postprocessorProperties === true) {\n
                            postprocessors.push(postprocessor.fn);\n
                        }\n
                        else if (postprocessorProperties) {\n
                            for (j = 0,subLn = postprocessorProperties.length; j < subLn; j++) {\n
                                postprocessorProperty = postprocessorProperties[j];\n
\n
                                if (data.hasOwnProperty(postprocessorProperty)) {\n
                                    postprocessors.push(postprocessor.fn);\n
                                    break;\n
                                }\n
                            }\n
                        }\n
                    }\n
                    else {\n
                        postprocessors.push(postprocessor);\n
                    }\n
                }\n
\n
                process = function(clsName, cls, clsData) {\n
                    postprocessor = postprocessors[index++];\n
\n
                    if (!postprocessor) {\n
                        Manager.set(className, cls);\n
\n
                        if (createdFn) {\n
                            createdFn.call(cls, cls);\n
                        }\n
\n
                        Manager.triggerCreated(className);\n
                        return;\n
                    }\n
\n
                    if (postprocessor.call(this, clsName, cls, clsData, process) !== false) {\n
                        process.apply(this, arguments);\n
                    }\n
                };\n
\n
                process.call(Manager, className, this, data);\n
            });\n
        },\n
\n
        createOverride: function(className, data) {\n
            var overriddenClassName = data.override,\n
                requires = Ext.Array.from(data.requires);\n
\n
            delete data.override;\n
            delete data.requires;\n
\n
            this.existCache[className] = true;\n
\n
            Ext.require(requires, function() {\n
                // Override the target class right after it\'s created\n
                this.onCreated(function() {\n
                    this.get(overriddenClassName).override(data);\n
\n
                    // This push the overridding file itself into Ext.Loader.history\n
                    // Hence if the target class never exists, the overriding file will\n
                    // never be included in the build\n
                    this.triggerCreated(className);\n
                }, this, overriddenClassName);\n
            }, this);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Instantiate a class by its alias; usually invoked by the convenient shorthand {@link Ext#createByAlias Ext.createByAlias}\n
         * If {@link Ext.Loader} is {@link Ext.Loader#setConfig enabled} and the class has not been defined yet, it will\n
         * attempt to load the class via synchronous loading.\n
         *\n
         *     var window = Ext.ClassManager.instantiateByAlias(\'widget.window\', { width: 600, height: 800 });\n
         *\n
         * @param {String} alias\n
         * @param {Mixed...} args Additional arguments after the alias will be passed to the class constructor.\n
         * @return {Object} instance\n
         */\n
        instantiateByAlias: function() {\n
            var alias = arguments[0],\n
                args = arraySlice.call(arguments),\n
                className = this.getNameByAlias(alias);\n
\n
            if (!className) {\n
                className = this.maps.aliasToName[alias];\n
\n
                //<debug error>\n
                if (!className) {\n
                    throw new Error("[Ext.createByAlias] Cannot create an instance of unrecognized alias: " + alias);\n
                }\n
                //</debug>\n
\n
                //<debug warn>\n
                Ext.Logger.warn("[Ext.Loader] Synchronously loading \'" + className + "\'; consider adding " +\n
                     "Ext.require(\'" + alias + "\') above Ext.onReady");\n
                //</debug>\n
\n
                Ext.syncRequire(className);\n
            }\n
\n
            args[0] = className;\n
\n
            return this.instantiate.apply(this, args);\n
        },\n
\n
        /**\n
         * Instantiate a class by either full name, alias or alternate name; usually invoked by the convenient\n
         * shorthand {@link Ext.ClassManager#create Ext.create}.\n
         *\n
         * If {@link Ext.Loader} is {@link Ext.Loader#setConfig enabled} and the class has not been defined yet, it will\n
         * attempt to load the class via synchronous loading.\n
         *\n
         * For example, all these three lines return the same result:\n
         *\n
         *     // alias\n
         *     var formPanel = Ext.create(\'widget.formpanel\', { width: 600, height: 800 });\n
         *\n
         *     // alternate name\n
         *     var formPanel = Ext.create(\'Ext.form.FormPanel\', { width: 600, height: 800 });\n
         *\n
         *     // full class name\n
         *     var formPanel = Ext.create(\'Ext.form.Panel\', { width: 600, height: 800 });\n
         *\n
         * @param {String} name\n
         * @param {Mixed} args Additional arguments after the name will be passed to the class\' constructor.\n
         * @return {Object} instance\n
         */\n
        instantiate: function() {\n
            var name = arguments[0],\n
                args = arraySlice.call(arguments, 1),\n
                alias = name,\n
                possibleName, cls;\n
\n
            if (typeof name != \'function\') {\n
                //<debug error>\n
                if ((typeof name != \'string\' || name.length < 1)) {\n
                    throw new Error("[Ext.create] Invalid class name or alias \'" + name + "\' specified, must be a non-empty string");\n
                }\n
                //</debug>\n
\n
                cls = this.get(name);\n
            }\n
            else {\n
                cls = name;\n
            }\n
\n
            // No record of this class name, it\'s possibly an alias, so look it up\n
            if (!cls) {\n
                possibleName = this.getNameByAlias(name);\n
\n
                if (possibleName) {\n
                    name = possibleName;\n
\n
                    cls = this.get(name);\n
                }\n
            }\n
\n
            // Still no record of this class name, it\'s possibly an alternate name, so look it up\n
            if (!cls) {\n
                possibleName = this.getNameByAlternate(name);\n
\n
                if (possibleName) {\n
                    name = possibleName;\n
\n
                    cls = this.get(name);\n
                }\n
            }\n
\n
            // Still not existing at this point, try to load it via synchronous mode as the last resort\n
            if (!cls) {\n
                //<debug warn>\n
                Ext.Logger.warn("[Ext.Loader] Synchronously loading \'" + name + "\'; consider adding \'" +\n
                    ((possibleName) ? alias : name) + "\' explicitly as a require of the corresponding class");\n
                //</debug>\n
\n
                Ext.syncRequire(name);\n
\n
                cls = this.get(name);\n
            }\n
\n
            //<debug error>\n
            if (!cls) {\n
                throw new Error("[Ext.create] Cannot create an instance of unrecognized class name / alias: " + alias);\n
            }\n
\n
            if (typeof cls != \'function\') {\n
                throw new Error("[Ext.create] \'" + name + "\' is a singleton and cannot be instantiated");\n
            }\n
            //</debug>\n
\n
            return this.getInstantiator(args.length)(cls, args);\n
        },\n
\n
        /**\n
         * @private\n
         * @param name\n
         * @param args\n
         */\n
        dynInstantiate: function(name, args) {\n
            args = arrayFrom(args, true);\n
            args.unshift(name);\n
\n
            return this.instantiate.apply(this, args);\n
        },\n
\n
        /**\n
         * @private\n
         * @param length\n
         */\n
        getInstantiator: function(length) {\n
            var instantiators = this.instantiators,\n
                instantiator;\n
\n
            instantiator = instantiators[length];\n
\n
            if (!instantiator) {\n
                var i = length,\n
                    args = [];\n
\n
                for (i = 0; i < length; i++) {\n
                    args.push(\'a[\' + i + \']\');\n
                }\n
\n
                instantiator = instantiators[length] = new Function(\'c\', \'a\', \'return new c(\' + args.join(\',\') + \')\');\n
                //<debug>\n
                instantiator.displayName = "Ext.ClassManager.instantiate" + length;\n
                //</debug>\n
            }\n
\n
            return instantiator;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        postprocessors: {},\n
\n
        /**\n
         * @private\n
         */\n
        defaultPostprocessors: [],\n
\n
        /**\n
         * Register a post-processor function.\n
         *\n
         * @private\n
         * @param {String} name\n
         * @param {Function} postprocessor\n
         */\n
        registerPostprocessor: function(name, fn, properties, position, relativeTo) {\n
            if (!position) {\n
                position = \'last\';\n
            }\n
\n
            if (!properties) {\n
                properties = [name];\n
            }\n
\n
            this.postprocessors[name] = {\n
                name: name,\n
                properties: properties || false,\n
                fn: fn\n
            };\n
\n
            this.setDefaultPostprocessorPosition(name, position, relativeTo);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Set the default post processors array stack which are applied to every class.\n
         *\n
         * @private\n
         * @param {String/Array} The name of a registered post processor or an array of registered names.\n
         * @return {Ext.ClassManager} this\n
         */\n
        setDefaultPostprocessors: function(postprocessors) {\n
            this.defaultPostprocessors = arrayFrom(postprocessors);\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Insert this post-processor at a specific position in the stack, optionally relative to\n
         * any existing post-processor\n
         *\n
         * @private\n
         * @param {String} name The post-processor name. Note that it needs to be registered with\n
         * {@link Ext.ClassManager#registerPostprocessor} before this\n
         * @param {String} offset The insertion position. Four possible values are:\n
         * \'first\', \'last\', or: \'before\', \'after\' (relative to the name provided in the third argument)\n
         * @param {String} relativeName\n
         * @return {Ext.ClassManager} this\n
         */\n
        setDefaultPostprocessorPosition: function(name, offset, relativeName) {\n
            var defaultPostprocessors = this.defaultPostprocessors,\n
                index;\n
\n
            if (typeof offset == \'string\') {\n
                if (offset === \'first\') {\n
                    defaultPostprocessors.unshift(name);\n
\n
                    return this;\n
                }\n
                else if (offset === \'last\') {\n
                    defaultPostprocessors.push(name);\n
\n
                    return this;\n
                }\n
\n
                offset = (offset === \'after\') ? 1 : -1;\n
            }\n
\n
            index = Ext.Array.indexOf(defaultPostprocessors, relativeName);\n
\n
            if (index !== -1) {\n
                Ext.Array.splice(defaultPostprocessors, Math.max(0, index + offset), 0, name);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Converts a string expression to an array of matching class names. An expression can either refers to class aliases\n
         * or class names. Expressions support wildcards:\n
         *\n
         *      // returns [\'Ext.window.Window\']\n
         *     var window = Ext.ClassManager.getNamesByExpression(\'widget.window\');\n
         *\n
         *     // returns [\'widget.panel\', \'widget.window\', ...]\n
         *     var allWidgets = Ext.ClassManager.getNamesByExpression(\'widget.*\');\n
         *\n
         *     // returns [\'Ext.data.Store\', \'Ext.data.ArrayProxy\', ...]\n
         *     var allData = Ext.ClassManager.getNamesByExpression(\'Ext.data.*\');\n
         *\n
         * @param {String} expression\n
         * @return {Array} classNames\n
         */\n
        getNamesByExpression: function(expression) {\n
            var nameToAliasesMap = this.maps.nameToAliases,\n
                names = [],\n
                name, alias, aliases, possibleName, regex, i, ln;\n
\n
            //<debug error>\n
            if (typeof expression != \'string\' || expression.length < 1) {\n
                throw new Error("[Ext.ClassManager.getNamesByExpression] Expression " + expression + " is invalid, must be a non-empty string");\n
            }\n
            //</debug>\n
\n
            if (expression.indexOf(\'*\') !== -1) {\n
                expression = expression.replace(/\\*/g, \'(.*?)\');\n
                regex = new RegExp(\'^\' + expression + \'$\');\n
\n
                for (name in nameToAliasesMap) {\n
                    if (nameToAliasesMap.hasOwnProperty(name)) {\n
                        aliases = nameToAliasesMap[name];\n
\n
                        if (name.search(regex) !== -1) {\n
                            names.push(name);\n
                        }\n
                        else {\n
                            for (i = 0, ln = aliases.length; i < ln; i++) {\n
                                alias = aliases[i];\n
\n
                                if (alias.search(regex) !== -1) {\n
                                    names.push(name);\n
                                    break;\n
                                }\n
                            }\n
                        }\n
                    }\n
                }\n
\n
            } else {\n
                possibleName = this.getNameByAlias(expression);\n
\n
                if (possibleName) {\n
                    names.push(possibleName);\n
                } else {\n
                    possibleName = this.getNameByAlternate(expression);\n
\n
                    if (possibleName) {\n
                        names.push(possibleName);\n
                    } else {\n
                        names.push(expression);\n
                    }\n
                }\n
            }\n
\n
            return names;\n
        }\n
    };\n
\n
    //<feature classSystem.alias>\n
    /**\n
     * @cfg {String[]} alias\n
     * @member Ext.Class\n
     * List of short aliases for class names.  Most useful for defining xtypes for widgets:\n
     *\n
     *     Ext.define(\'MyApp.CoolPanel\', {\n
     *         extend: \'Ext.panel.Panel\',\n
     *         alias: [\'widget.coolpanel\'],\n
     *         title: \'Yeah!\'\n
     *     });\n
     *\n
     *     // Using Ext.create\n
     *     Ext.create(\'widget.coolpanel\');\n
     *\n
     *     // Using the shorthand for widgets and in xtypes\n
     *     Ext.widget(\'panel\', {\n
     *         items: [\n
     *             {xtype: \'coolpanel\', html: \'Foo\'},\n
     *             {xtype: \'coolpanel\', html: \'Bar\'}\n
     *         ]\n
     *     });\n
     */\n
    Manager.registerPostprocessor(\'alias\', function(name, cls, data) {\n
        var aliases = data.alias,\n
            i, ln;\n
\n
        for (i = 0,ln = aliases.length; i < ln; i++) {\n
            alias = aliases[i];\n
\n
            this.setAlias(cls, alias);\n
        }\n
\n
    }, [\'xtype\', \'alias\']);\n
    //</feature>\n
\n
    //<feature classSystem.singleton>\n
    /**\n
     * @cfg {Boolean} singleton\n
     * @member Ext.Class\n
     * When set to true, the class will be instantiated as singleton.  For example:\n
     *\n
     *     Ext.define(\'Logger\', {\n
     *         singleton: true,\n
     *         log: function(msg) {\n
     *             console.log(msg);\n
     *         }\n
     *     });\n
     *\n
     *     Logger.log(\'Hello\');\n
     */\n
    Manager.registerPostprocessor(\'singleton\', function(name, cls, data, fn) {\n
        fn.call(this, name, new cls(), data);\n
        return false;\n
    });\n
    //</feature>\n
\n
    //<feature classSystem.alternateClassName>\n
    /**\n
     * @cfg {String/String[]} alternateClassName\n
     * @member Ext.Class\n
     * Defines alternate names for this class.  For example:\n
     *\n
     *     @example\n
     *     Ext.define(\'Developer\', {\n
     *         alternateClassName: [\'Coder\', \'Hacker\'],\n
     *         code: function(msg) {\n
     *             alert(\'Typing... \' + msg);\n
     *         }\n
     *     });\n
     *\n
     *     var joe = Ext.create(\'Developer\');\n
     *     joe.code(\'stackoverflow\');\n
     *\n
     *     var rms = Ext.create(\'Hacker\');\n
     *     rms.code(\'hack hack\');\n
     */\n
    Manager.registerPostprocessor(\'alternateClassName\', function(name, cls, data) {\n
        var alternates = data.alternateClassName,\n
            i, ln, alternate;\n
\n
        if (!(alternates instanceof Array)) {\n
            alternates = [alternates];\n
        }\n
\n
        for (i = 0, ln = alternates.length; i < ln; i++) {\n
            alternate = alternates[i];\n
\n
            //<debug error>\n
            if (typeof alternate != \'string\') {\n
                throw new Error("[Ext.define] Invalid alternate of: \'" + alternate + "\' for class: \'" + name + "\'; must be a valid string");\n
            }\n
            //</debug>\n
\n
            this.set(alternate, cls);\n
        }\n
    });\n
    //</feature>\n
\n
    Ext.apply(Ext, {\n
        /**\n
         * Instantiate a class by either full name, alias or alternate name.\n
         *\n
         * If {@link Ext.Loader} is {@link Ext.Loader#setConfig enabled} and the class has not been defined yet, it will\n
         * attempt to load the class via synchronous loading.\n
         *\n
         * For example, all these three lines return the same result:\n
         *\n
         *     // alias\n
         *     var formPanel = Ext.create(\'widget.formpanel\', { width: 600, height: 800 });\n
         *\n
         *     // alternate name\n
         *     var formPanel = Ext.create(\'Ext.form.FormPanel\', { width: 600, height: 800 });\n
         *\n
         *     // full class name\n
         *     var formPanel = Ext.create(\'Ext.form.Panel\', { width: 600, height: 800 });\n
         *\n
         * @param {String} name\n
         * @param {Mixed} args Additional arguments after the name will be passed to the class\' constructor.\n
         * @return {Object} instance\n
         * @member Ext\n
         */\n
        create: alias(Manager, \'instantiate\'),\n
\n
        /**\n
         * Convenient shorthand to create a widget by its xtype, also see {@link Ext.ClassManager#instantiateByAlias}\n
         *\n
         *     var button = Ext.widget(\'button\'); // Equivalent to Ext.create(\'widget.button\')\n
         *     var panel = Ext.widget(\'panel\'); // Equivalent to Ext.create(\'widget.panel\')\n
         *\n
         * @member Ext\n
         * @method widget\n
         */\n
        widget: function(name) {\n
            var args = arraySlice.call(arguments);\n
            args[0] = \'widget.\' + name;\n
\n
            return Manager.instantiateByAlias.apply(Manager, args);\n
        },\n
\n
        /**\n
         * Convenient shorthand, see {@link Ext.ClassManager#instantiateByAlias}.\n
         * @member Ext\n
         * @method createByAlias\n
         */\n
        createByAlias: alias(Manager, \'instantiateByAlias\'),\n
\n
        /**\n
         * Defines a class or override. A basic class is defined like this:\n
         *\n
         *      Ext.define(\'My.awesome.Class\', {\n
         *          someProperty: \'something\',\n
         *\n
         *          someMethod: function(s) {\n
         *              console.log(s + this.someProperty);\n
         *          }\n
         *      });\n
         *\n
         *      var obj = new My.awesome.Class();\n
         *\n
         *      obj.someMethod(\'Say \'); // logs \'Say something\' to the console\n
         *\n
         * To defines an override, include the `override` property. The content of an\n
         * override is aggregated with the specified class in order to extend or modify\n
         * that class. This can be as simple as setting default property values or it can\n
         * extend and/or replace methods. This can also extend the statics of the class.\n
         *\n
         * One use for an override is to break a large class into manageable pieces.\n
         *\n
         *      // File: /src/app/Panel.js\n
         *      Ext.define(\'My.app.Panel\', {\n
         *          extend: \'Ext.panel.Panel\',\n
         *          requires: [\n
         *              \'My.app.PanelPart2\',\n
         *              \'My.app.PanelPart3\'\n
         *          ],\n
         *\n
         *          constructor: function (config) {\n
         *              this.callParent(arguments); // calls Ext.panel.Panel\'s constructor\n
         *              // ...\n
         *          },\n
         *\n
         *          statics: {\n
         *              method: function () {\n
         *                  return \'abc\';\n
         *              }\n
         *          }\n
         *      });\n
         *\n
         *      // File: /src/app/PanelPart2.js\n
         *      Ext.define(\'My.app.PanelPart2\', {\n
         *          override: \'My.app.Panel\',\n
         *\n
         *          constructor: function (config) {\n
         *              this.callParent(arguments); // calls My.app.Panel\'s constructor\n
         *              // ...\n
         *          }\n
         *      });\n
         *\n
         * Another use for an override is to provide optional parts of classes that can be\n
         * independently required. In this case, the class may even be unaware of the\n
         * override altogether.\n
         *\n
         *      Ext.define(\'My.ux.CoolTip\', {\n
         *          override: \'Ext.tip.ToolTip\',\n
         *\n
         *          constructor: function (config) {\n
         *              this.callParent(arguments); // calls Ext.tip.ToolTip\'s constructor\n
         *              // ...\n
         *          }\n
         *      });\n
         *\n
         * The above override can now be required as normal.\n
         *\n
         *      Ext.define(\'My.app.App\', {\n
         *          requires: [\n
         *              \'My.ux.CoolTip\'\n
         *          ]\n
         *      });\n
         *\n
         * Overrides can also contain statics:\n
         *\n
         *      Ext.define(\'My.app.BarMod\', {\n
         *          override: \'Ext.foo.Bar\',\n
         *\n
         *          statics: {\n
         *              method: function (x) {\n
         *                  return this.callParent([x * 2]); // call Ext.foo.Bar.method\n
         *              }\n
         *          }\n
         *      });\n
         *\n
         * __IMPORTANT:__ An override is only included in a build if the class it overrides is\n
         * required. Otherwise, the override, like the target class, is not included.\n
         *\n
         * @param {String} className The class name to create in string dot-namespaced format, for example:\n
         * \'My.very.awesome.Class\', \'FeedViewer.plugin.CoolPager\'\n
         *\n
         * It is highly recommended to follow this simple convention:\n
         *  - The root and the class name are \'CamelCased\'\n
         *  - Everything else is lower-cased\n
         *\n
         * @param {Object} data The key - value pairs of properties to apply to this class. Property names can be of\n
         * any valid strings, except those in the reserved listed below:\n
         *\n
         *  - `mixins`\n
         *  - `statics`\n
         *  - `config`\n
         *  - `alias`\n
         *  - `self`\n
         *  - `singleton`\n
         *  - `alternateClassName`\n
         *  - `override`\n
         *\n
         * @param {Function} [createdFn] Optional callback to execute after the class (or override)\n
         * is created. The execution scope (`this`) will be the newly created class itself.\n
         * @return {Ext.Base}\n
         *\n
         * @member Ext\n
         * @method define\n
         */\n
        define: function (className, data, createdFn) {\n
            if (\'override\' in data) {\n
                return Manager.createOverride.apply(Manager, arguments);\n
            }\n
\n
            return Manager.create.apply(Manager, arguments);\n
        },\n
\n
        /**\n
         * Convenient shorthand for {@link Ext.ClassManager#getName}.\n
         * @member Ext\n
         * @method getClassName\n
         * @inheritdoc Ext.ClassManager#getName\n
         */\n
        getClassName: alias(Manager, \'getName\'),\n
\n
        /**\n
         * Returns the display name for object.  This name is looked for in order from the following places:\n
         *\n
         * - `displayName` field of the object.\n
         * - `$name` and `$class` fields of the object.\n
         * - \'$className` field of the object.\n
         *\n
         * This method is used by {@link Ext.Logger#log} to display information about objects.\n
         *\n
         * @param {Mixed} [object] The object who\'s display name to determine.\n
         * @return {String} The determined display name, or "Anonymous" if none found.\n
         * @member Ext\n
         */\n
        getDisplayName: function(object) {\n
            if (object) {\n
                if (object.displayName) {\n
                    return object.displayName;\n
                }\n
\n
                if (object.$name && object.$class) {\n
                    return Ext.getClassName(object.$class) + \'#\' + object.$name;\n
                }\n
\n
                if (object.$className) {\n
                    return object.$className;\n
                }\n
            }\n
\n
            return \'Anonymous\';\n
        },\n
\n
        /**\n
         * Convenient shorthand, see {@link Ext.ClassManager#getClass}.\n
         * @member Ext\n
         * @method getClass\n
         */\n
        getClass: alias(Manager, \'getClass\'),\n
\n
        /**\n
         * Creates namespaces to be used for scoping variables and classes so that they are not global.\n
         * Specifying the last node of a namespace implicitly creates all other nodes. Usage:\n
         *\n
         *     Ext.namespace(\'Company\', \'Company.data\');\n
         *\n
         *      // equivalent and preferable to the above syntax\n
         *     Ext.namespace(\'Company.data\');\n
         *\n
         *     Company.Widget = function() {\n
         *         // ...\n
         *     };\n
         *\n
         *     Company.data.CustomStore = function(config) {\n
         *         // ...\n
         *     };\n
         *\n
         * @param {String} namespace1\n
         * @param {String} namespace2\n
         * @param {String} etc\n
         * @return {Object} The namespace object. If multiple arguments are passed, this will be the last namespace created.\n
         * @member Ext\n
         * @method namespace\n
         */\n
        namespace: alias(Manager, \'createNamespaces\')\n
    });\n
\n
    /**\n
     * Old name for {@link Ext#widget}.\n
     * @deprecated 4.0.0 Please use {@link Ext#widget} instead.\n
     * @method createWidget\n
     * @member Ext\n
     */\n
    Ext.createWidget = Ext.widget;\n
\n
    /**\n
     * Convenient alias for {@link Ext#namespace Ext.namespace}.\n
     * @member Ext\n
     * @method ns\n
     */\n
    Ext.ns = Ext.namespace;\n
\n
    Class.registerPreprocessor(\'className\', function(cls, data) {\n
        if (data.$className) {\n
            cls.$className = data.$className;\n
            //<debug>\n
            cls.displayName = cls.$className;\n
            //</debug>\n
        }\n
    }, true, \'first\');\n
\n
    Class.registerPreprocessor(\'alias\', function(cls, data) {\n
        var prototype = cls.prototype,\n
            xtypes = arrayFrom(data.xtype),\n
            aliases = arrayFrom(data.alias),\n
            widgetPrefix = \'widget.\',\n
            widgetPrefixLength = widgetPrefix.length,\n
            xtypesChain = Array.prototype.slice.call(prototype.xtypesChain || []),\n
            xtypesMap = Ext.merge({}, prototype.xtypesMap || {}),\n
            i, ln, alias, xtype;\n
\n
        for (i = 0,ln = aliases.length; i < ln; i++) {\n
            alias = aliases[i];\n
\n
            //<debug error>\n
            if (typeof alias != \'string\' || alias.length < 1) {\n
                throw new Error("[Ext.define] Invalid alias of: \'" + alias + "\' for class: \'" + name + "\'; must be a valid string");\n
            }\n
            //</debug>\n
\n
            if (alias.substring(0, widgetPrefixLength) === widgetPrefix) {\n
                xtype = alias.substring(widgetPrefixLength);\n
                Ext.Array.include(xtypes, xtype);\n
            }\n
        }\n
\n
        cls.xtype = data.xtype = xtypes[0];\n
        data.xtypes = xtypes;\n
\n
        for (i = 0,ln = xtypes.length; i < ln; i++) {\n
            xtype = xtypes[i];\n
\n
            if (!xtypesMap[xtype]) {\n
                xtypesMap[xtype] = true;\n
                xtypesChain.push(xtype);\n
            }\n
        }\n
\n
        data.xtypesChain = xtypesChain;\n
        data.xtypesMap = xtypesMap;\n
\n
        Ext.Function.interceptAfter(data, \'onClassCreated\', function() {\n
            var mixins = prototype.mixins,\n
                key, mixin;\n
\n
            for (key in mixins) {\n
                if (mixins.hasOwnProperty(key)) {\n
                    mixin = mixins[key];\n
\n
                    xtypes = mixin.xtypes;\n
\n
                    if (xtypes) {\n
                        for (i = 0,ln = xtypes.length; i < ln; i++) {\n
                            xtype = xtypes[i];\n
\n
                            if (!xtypesMap[xtype]) {\n
                                xtypesMap[xtype] = true;\n
                                xtypesChain.push(xtype);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
\n
        for (i = 0,ln = xtypes.length; i < ln; i++) {\n
            xtype = xtypes[i];\n
\n
            //<debug error>\n
            if (typeof xtype != \'string\' || xtype.length < 1) {\n
                throw new Error("[Ext.define] Invalid xtype of: \'" + xtype + "\' for class: \'" + name + "\'; must be a valid non-empty string");\n
            }\n
            //</debug>\n
\n
            Ext.Array.include(aliases, widgetPrefix + xtype);\n
        }\n
\n
        data.alias = aliases;\n
\n
    }, [\'xtype\', \'alias\']);\n
\n
})(Ext.Class, Ext.Function.alias, Array.prototype.slice, Ext.Array.from, Ext.global);\n
\n
//@tag foundation,core\n
//@define Ext.Loader\n
//@require Ext.ClassManager\n
\n
/**\n
 * @class Ext.Loader\n
 *\n
 * @author Jacky Nguyen <jacky@sencha.com>\n
 * @docauthor Jacky Nguyen <jacky@sencha.com>\n
 * @aside guide mvc_dependencies\n
 *\n
 * Ext.Loader is the heart of the new dynamic dependency loading capability in Ext JS 4+. It is most commonly used\n
 * via the {@link Ext#require} shorthand. Ext.Loader supports both asynchronous and synchronous loading\n
 * approaches, and leverage their advantages for the best development flow.\n
 * We\'ll discuss about the pros and cons of each approach.\n
 *\n
 * __Note:__ The Loader is only enabled by default in development v

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

ersions of the library (eg sencha-touch-debug.js). To\n
 * explicitly enable the loader, use `Ext.Loader.setConfig({ enabled: true });` before the start of your script.\n
 *\n
 * ## Asynchronous Loading\n
 *\n
 * - Advantages:\n
 * \t+ Cross-domain\n
 * \t+ No web server needed: you can run the application via the file system protocol (i.e: `file://path/to/your/index\n
 *  .html`)\n
 * \t+ Best possible debugging experience: error messages come with the exact file name and line number\n
 *\n
 * - Disadvantages:\n
 * \t+ Dependencies need to be specified before-hand\n
 *\n
 * ### Method 1: Explicitly include what you need: ###\n
 *\n
 *     // Syntax\n
 *     // Ext.require({String/Array} expressions);\n
 *\n
 *     // Example: Single alias\n
 *     Ext.require(\'widget.window\');\n
 *\n
 *     // Example: Single class name\n
 *     Ext.require(\'Ext.window.Window\');\n
 *\n
 *     // Example: Multiple aliases / class names mix\n
 *     Ext.require([\'widget.window\', \'layout.border\', \'Ext.data.Connection\']);\n
 *\n
 *     // Wildcards\n
 *     Ext.require([\'widget.*\', \'layout.*\', \'Ext.data.*\']);\n
 *\n
 * ### Method 2: Explicitly exclude what you don\'t need: ###\n
 *\n
 *     // Syntax: Note that it must be in this chaining format.\n
 *     // Ext.exclude({String/Array} expressions)\n
 *     //    .require({String/Array} expressions);\n
 *\n
 *     // Include everything except Ext.data.*\n
 *     Ext.exclude(\'Ext.data.*\').require(\'*\');\n
 *\n
 *     // Include all widgets except widget.checkbox*,\n
 *     // which will match widget.checkbox, widget.checkboxfield, widget.checkboxgroup, etc.\n
 *     Ext.exclude(\'widget.checkbox*\').require(\'widget.*\');\n
 *\n
 * # Synchronous Loading on Demand #\n
 *\n
 * - *Advantages:*\n
 * \t+ There\'s no need to specify dependencies before-hand, which is always the convenience of including ext-all.js\n
 *  before\n
 *\n
 * - *Disadvantages:*\n
 * \t+ Not as good debugging experience since file name won\'t be shown (except in Firebug at the moment)\n
 * \t+ Must be from the same domain due to XHR restriction\n
 * \t+ Need a web server, same reason as above\n
 *\n
 * There\'s one simple rule to follow: Instantiate everything with Ext.create instead of the `new` keyword\n
 *\n
 *     Ext.create(\'widget.window\', {}); // Instead of new Ext.window.Window({...});\n
 *\n
 *     Ext.create(\'Ext.window.Window\', {}); // Same as above, using full class name instead of alias\n
 *\n
 *     Ext.widget(\'window\', {}); // Same as above, all you need is the traditional `xtype`\n
 *\n
 * Behind the scene, {@link Ext.ClassManager} will automatically check whether the given class name / alias has already\n
 *  existed on the page. If it\'s not, Ext.Loader will immediately switch itself to synchronous mode and automatic load the given\n
 *  class and all its dependencies.\n
 *\n
 * # Hybrid Loading - The Best of Both Worlds #\n
 *\n
 * It has all the advantages combined from asynchronous and synchronous loading. The development flow is simple:\n
 *\n
 * ### Step 1: Start writing your application using synchronous approach. ###\n
 * Ext.Loader will automatically fetch all dependencies on demand as they\'re \n
 * needed during run-time. For example:\n
 *\n
 *     Ext.onReady(function(){\n
 *         var window = Ext.createWidget(\'window\', {\n
 *             width: 500,\n
 *             height: 300,\n
 *             layout: {\n
 *                 type: \'border\',\n
 *                 padding: 5\n
 *             },\n
 *             title: \'Hello Dialog\',\n
 *             items: [{\n
 *                 title: \'Navigation\',\n
 *                 collapsible: true,\n
 *                 region: \'west\',\n
 *                 width: 200,\n
 *                 html: \'Hello\',\n
 *                 split: true\n
 *             }, {\n
 *                 title: \'TabPanel\',\n
 *                 region: \'center\'\n
 *             }]\n
 *         });\n
 *\n
 *         window.show();\n
 *     });\n
 *\n
 * ### Step 2: Along the way, when you need better debugging ability, watch the console for warnings like these: ###\n
 *\n
 *     [Ext.Loader] Synchronously loading \'Ext.window.Window\'; consider adding Ext.require(\'Ext.window.Window\') before your application\'s code\n
 *     ClassManager.js:432\n
 *     [Ext.Loader] Synchronously loading \'Ext.layout.container.Border\'; consider adding Ext.require(\'Ext.layout.container.Border\') before your application\'s code\n
 *\n
 * Simply copy and paste the suggested code above `Ext.onReady`, i.e:\n
 *\n
 *     Ext.require(\'Ext.window.Window\');\n
 *     Ext.require(\'Ext.layout.container.Border\');\n
 *\n
 *     Ext.onReady(function () {\n
 *         // ...\n
 *     });\n
 *\n
 * Everything should now load via asynchronous mode.\n
 *\n
 * # Deployment #\n
 *\n
 * It\'s important to note that dynamic loading should only be used during development on your local machines.\n
 * During production, all dependencies should be combined into one single JavaScript file. Ext.Loader makes\n
 * the whole process of transitioning from / to between development / maintenance and production as easy as\n
 * possible. Internally {@link Ext.Loader#history Ext.Loader.history} maintains the list of all dependencies your application\n
 * needs in the exact loading sequence. It\'s as simple as concatenating all files in this array into one,\n
 * then include it on top of your application.\n
 *\n
 * This process will be automated with Sencha Command, to be released and documented towards Ext JS 4 Final.\n
 *\n
 * @singleton\n
 */\n
(function(Manager, Class, flexSetter, alias, pass, arrayFrom, arrayErase, arrayInclude) {\n
\n
    var\n
        dependencyProperties = [\'extend\', \'mixins\', \'requires\'],\n
        Loader,\n
        setPathCount = 0;;\n
\n
    Loader = Ext.Loader = {\n
\n
        /**\n
         * @private\n
         */\n
        isInHistory: {},\n
\n
        /**\n
         * An array of class names to keep track of the dependency loading order.\n
         * This is not guaranteed to be the same every time due to the asynchronous\n
         * nature of the Loader.\n
         *\n
         * @property history\n
         * @type Array\n
         */\n
        history: [],\n
\n
        /**\n
         * Configuration\n
         * @private\n
         */\n
        config: {\n
            /**\n
             * Whether or not to enable the dynamic dependency loading feature.\n
             * @cfg {Boolean} enabled\n
             */\n
            enabled: true,\n
\n
            /**\n
             * @cfg {Boolean} disableCaching\n
             * Appends current timestamp to script files to prevent caching.\n
             */\n
            disableCaching: true,\n
\n
            /**\n
             * @cfg {String} disableCachingParam\n
             * The get parameter name for the cache buster\'s timestamp.\n
             */\n
            disableCachingParam: \'_dc\',\n
\n
            /**\n
             * @cfg {Object} paths\n
             * The mapping from namespaces to file paths.\n
             *\n
             *     {\n
             *         \'Ext\': \'.\', // This is set by default, Ext.layout.container.Container will be\n
             *                     // loaded from ./layout/Container.js\n
             *\n
             *         \'My\': \'./src/my_own_folder\' // My.layout.Container will be loaded from\n
             *                                     // ./src/my_own_folder/layout/Container.js\n
             *     }\n
             *\n
             * Note that all relative paths are relative to the current HTML document.\n
             * If not being specified, for example, `Other.awesome.Class`\n
             * will simply be loaded from `./Other/awesome/Class.js`.\n
             */\n
            paths: {\n
                \'Ext\': \'.\'\n
            }\n
        },\n
\n
        /**\n
         * Set the configuration for the loader. This should be called right after ext-(debug).js\n
         * is included in the page, and before Ext.onReady. i.e:\n
         *\n
         *     <script type="text/javascript" src="ext-core-debug.js"></script>\n
         *     <script type="text/javascript">\n
         *         Ext.Loader.setConfig({\n
         *           enabled: true,\n
         *           paths: {\n
         *               \'My\': \'my_own_path\'\n
         *           }\n
         *         });\n
         *     <script>\n
         *     <script type="text/javascript">\n
         *         Ext.require(...);\n
         *\n
         *         Ext.onReady(function() {\n
         *           // application code here\n
         *         });\n
         *     </script>\n
         *\n
         * Refer to config options of {@link Ext.Loader} for the list of possible properties.\n
         *\n
         * @param {Object} config The config object to override the default values.\n
         * @return {Ext.Loader} this\n
         */\n
        setConfig: function(name, value) {\n
            if (Ext.isObject(name) && arguments.length === 1) {\n
                Ext.merge(this.config, name);\n
            }\n
            else {\n
                this.config[name] = (Ext.isObject(value)) ? Ext.merge(this.config[name], value) : value;\n
            }\n
            setPathCount += 1;\n
            return this;\n
        },\n
\n
        /**\n
         * Get the config value corresponding to the specified name. If no name is given, will return the config object.\n
         * @param {String} name The config property name.\n
         * @return {Object/Mixed}\n
         */\n
        getConfig: function(name) {\n
            if (name) {\n
                return this.config[name];\n
            }\n
\n
            return this.config;\n
        },\n
\n
        /**\n
         * Sets the path of a namespace.\n
         * For example:\n
         *\n
         *     Ext.Loader.setPath(\'Ext\', \'.\');\n
         *\n
         * @param {String/Object} name See {@link Ext.Function#flexSetter flexSetter}\n
         * @param {String} [path] See {@link Ext.Function#flexSetter flexSetter}\n
         * @return {Ext.Loader} this\n
         * @method\n
         */\n
        setPath: flexSetter(function(name, path) {\n
            this.config.paths[name] = path;\n
            setPathCount += 1;\n
            return this;\n
        }),\n
\n
        /**\n
         * Sets a batch of path entries\n
         *\n
         * @param {Object } paths a set of className: path mappings\n
         * @return {Ext.Loader} this\n
         */\n
        addClassPathMappings: function(paths) {\n
            var name;\n
\n
            if(setPathCount == 0){\n
                Loader.config.paths = paths;\n
            } else {\n
                for(name in paths){\n
                    Loader.config.paths[name] = paths[name];\n
                }\n
            }\n
            setPathCount++;\n
            return Loader;\n
        },\n
\n
        /**\n
         * Translates a className to a file path by adding the\n
         * the proper prefix and converting the .\'s to /\'s. For example:\n
         *\n
         *     Ext.Loader.setPath(\'My\', \'/path/to/My\');\n
         *\n
         *     alert(Ext.Loader.getPath(\'My.awesome.Class\')); // alerts \'/path/to/My/awesome/Class.js\'\n
         *\n
         * Note that the deeper namespace levels, if explicitly set, are always resolved first. For example:\n
         *\n
         *     Ext.Loader.setPath({\n
         *         \'My\': \'/path/to/lib\',\n
         *         \'My.awesome\': \'/other/path/for/awesome/stuff\',\n
         *         \'My.awesome.more\': \'/more/awesome/path\'\n
         *     });\n
         *\n
         *     alert(Ext.Loader.getPath(\'My.awesome.Class\')); // alerts \'/other/path/for/awesome/stuff/Class.js\'\n
         *\n
         *     alert(Ext.Loader.getPath(\'My.awesome.more.Class\')); // alerts \'/more/awesome/path/Class.js\'\n
         *\n
         *     alert(Ext.Loader.getPath(\'My.cool.Class\')); // alerts \'/path/to/lib/cool/Class.js\'\n
         *\n
         *     alert(Ext.Loader.getPath(\'Unknown.strange.Stuff\')); // alerts \'Unknown/strange/Stuff.js\'\n
         *\n
         * @param {String} className\n
         * @return {String} path\n
         */\n
        getPath: function(className) {\n
            var path = \'\',\n
                paths = this.config.paths,\n
                prefix = this.getPrefix(className);\n
\n
            if (prefix.length > 0) {\n
                if (prefix === className) {\n
                    return paths[prefix];\n
                }\n
\n
                path = paths[prefix];\n
                className = className.substring(prefix.length + 1);\n
            }\n
\n
            if (path.length > 0) {\n
                path += \'/\';\n
            }\n
\n
            return path.replace(/\\/\\.\\//g, \'/\') + className.replace(/\\./g, "/") + \'.js\';\n
        },\n
\n
        /**\n
         * @private\n
         * @param {String} className\n
         */\n
        getPrefix: function(className) {\n
            var paths = this.config.paths,\n
                prefix, deepestPrefix = \'\';\n
\n
            if (paths.hasOwnProperty(className)) {\n
                return className;\n
            }\n
\n
            for (prefix in paths) {\n
                if (paths.hasOwnProperty(prefix) && prefix + \'.\' === className.substring(0, prefix.length + 1)) {\n
                    if (prefix.length > deepestPrefix.length) {\n
                        deepestPrefix = prefix;\n
                    }\n
                }\n
            }\n
\n
            return deepestPrefix;\n
        },\n
\n
        /**\n
         * Loads all classes by the given names and all their direct dependencies; optionally executes the given callback function when\n
         * finishes, within the optional scope. This method is aliased by {@link Ext#require Ext.require} for convenience.\n
         * @param {String/Array} expressions Can either be a string or an array of string.\n
         * @param {Function} fn (optional) The callback function.\n
         * @param {Object} scope (optional) The execution scope (`this`) of the callback function.\n
         * @param {String/Array} excludes (optional) Classes to be excluded, useful when being used with expressions.\n
         */\n
        require: function(expressions, fn, scope, excludes) {\n
            if (fn) {\n
                fn.call(scope);\n
            }\n
        },\n
\n
        /**\n
         * Synchronously loads all classes by the given names and all their direct dependencies; optionally executes the given callback function when finishes, within the optional scope. This method is aliased by {@link Ext#syncRequire} for convenience\n
         * @param {String/Array} expressions Can either be a string or an array of string\n
         * @param {Function} fn (optional) The callback function\n
         * @param {Object} scope (optional) The execution scope (`this`) of the callback function\n
         * @param {String/Array} excludes (optional) Classes to be excluded, useful when being used with expressions\n
         */\n
        syncRequire: function() {},\n
\n
        /**\n
         * Explicitly exclude files from being loaded. Useful when used in conjunction with a broad include expression.\n
         * Can be chained with more `require` and `exclude` methods, eg:\n
         *\n
         *     Ext.exclude(\'Ext.data.*\').require(\'*\');\n
         *\n
         *     Ext.exclude(\'widget.button*\').require(\'widget.*\');\n
         *\n
         * @param {Array} excludes\n
         * @return {Object} object contains `require` method for chaining.\n
         */\n
        exclude: function(excludes) {\n
            var me = this;\n
\n
            return {\n
                require: function(expressions, fn, scope) {\n
                    return me.require(expressions, fn, scope, excludes);\n
                },\n
\n
                syncRequire: function(expressions, fn, scope) {\n
                    return me.syncRequire(expressions, fn, scope, excludes);\n
                }\n
            };\n
        },\n
\n
        /**\n
         * Add a new listener to be executed when all required scripts are fully loaded.\n
         *\n
         * @param {Function} fn The function callback to be executed.\n
         * @param {Object} scope The execution scope (`this`) of the callback function.\n
         * @param {Boolean} withDomReady Whether or not to wait for document DOM ready as well.\n
         */\n
        onReady: function(fn, scope, withDomReady, options) {\n
            var oldFn;\n
\n
            if (withDomReady !== false && Ext.onDocumentReady) {\n
                oldFn = fn;\n
\n
                fn = function() {\n
                    Ext.onDocumentReady(oldFn, scope, options);\n
                };\n
            }\n
\n
            fn.call(scope);\n
        }\n
    };\n
\n
    //<feature classSystem.loader>\n
    Ext.apply(Loader, {\n
        /**\n
         * @private\n
         */\n
        documentHead: typeof document != \'undefined\' && (document.head || document.getElementsByTagName(\'head\')[0]),\n
\n
        /**\n
         * Flag indicating whether there are still files being loaded\n
         * @private\n
         */\n
        isLoading: false,\n
\n
        /**\n
         * Maintain the queue for all dependencies. Each item in the array is an object of the format:\n
         * \n
         *     {\n
         *         requires: [...], // The required classes for this queue item\n
         *         callback: function() { ... } // The function to execute when all classes specified in requires exist\n
         *     }\n
         * @private\n
         */\n
        queue: [],\n
\n
        /**\n
         * Maintain the list of files that have already been handled so that they never get double-loaded\n
         * @private\n
         */\n
        isClassFileLoaded: {},\n
\n
        /**\n
         * @private\n
         */\n
        isFileLoaded: {},\n
\n
        /**\n
         * Maintain the list of listeners to execute when all required scripts are fully loaded\n
         * @private\n
         */\n
        readyListeners: [],\n
\n
        /**\n
         * Contains optional dependencies to be loaded last\n
         * @private\n
         */\n
        optionalRequires: [],\n
\n
        /**\n
         * Map of fully qualified class names to an array of dependent classes.\n
         * @private\n
         */\n
        requiresMap: {},\n
\n
        /**\n
         * @private\n
         */\n
        numPendingFiles: 0,\n
\n
        /**\n
         * @private\n
         */\n
        numLoadedFiles: 0,\n
\n
        /** @private */\n
        hasFileLoadError: false,\n
\n
        /**\n
         * @private\n
         */\n
        classNameToFilePathMap: {},\n
\n
        /**\n
         * @private\n
         */\n
        syncModeEnabled: false,\n
\n
        scriptElements: {},\n
\n
        /**\n
         * Refresh all items in the queue. If all dependencies for an item exist during looping,\n
         * it will execute the callback and call refreshQueue again. Triggers onReady when the queue is\n
         * empty\n
         * @private\n
         */\n
        refreshQueue: function() {\n
            var queue = this.queue,\n
                ln = queue.length,\n
                i, item, j, requires, references;\n
\n
            if (ln === 0) {\n
                this.triggerReady();\n
                return;\n
            }\n
\n
            for (i = 0; i < ln; i++) {\n
                item = queue[i];\n
\n
                if (item) {\n
                    requires = item.requires;\n
                    references = item.references;\n
\n
                    // Don\'t bother checking when the number of files loaded\n
                    // is still less than the array length\n
                    if (requires.length > this.numLoadedFiles) {\n
                        continue;\n
                    }\n
\n
                    j = 0;\n
\n
                    do {\n
                        if (Manager.isCreated(requires[j])) {\n
                            // Take out from the queue\n
                            arrayErase(requires, j, 1);\n
                        }\n
                        else {\n
                            j++;\n
                        }\n
                    } while (j < requires.length);\n
\n
                    if (item.requires.length === 0) {\n
                        arrayErase(queue, i, 1);\n
                        item.callback.call(item.scope);\n
                        this.refreshQueue();\n
                        break;\n
                    }\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Inject a script element to document\'s head, call onLoad and onError accordingly\n
         * @private\n
         */\n
        injectScriptElement: function(url, onLoad, onError, scope) {\n
            var script = document.createElement(\'script\'),\n
                me = this,\n
                onLoadFn = function() {\n
                    me.cleanupScriptElement(script);\n
                    onLoad.call(scope);\n
                },\n
                onErrorFn = function() {\n
                    me.cleanupScriptElement(script);\n
                    onError.call(scope);\n
                };\n
\n
            script.type = \'text/javascript\';\n
            script.src = url;\n
            script.onload = onLoadFn;\n
            script.onerror = onErrorFn;\n
            script.onreadystatechange = function() {\n
                if (this.readyState === \'loaded\' || this.readyState === \'complete\') {\n
                    onLoadFn();\n
                }\n
            };\n
\n
            this.documentHead.appendChild(script);\n
\n
            return script;\n
        },\n
\n
        removeScriptElement: function(url) {\n
            var scriptElements = this.scriptElements;\n
\n
            if (scriptElements[url]) {\n
                this.cleanupScriptElement(scriptElements[url], true);\n
                delete scriptElements[url];\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        cleanupScriptElement: function(script, remove) {\n
            script.onload = null;\n
            script.onreadystatechange = null;\n
            script.onerror = null;\n
\n
            if (remove) {\n
                this.documentHead.removeChild(script);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * Load a script file, supports both asynchronous and synchronous approaches\n
         *\n
         * @param {String} url\n
         * @param {Function} onLoad\n
         * @param {Object} scope\n
         * @param {Boolean} synchronous\n
         * @private\n
         */\n
        loadScriptFile: function(url, onLoad, onError, scope, synchronous) {\n
            var me = this,\n
                isFileLoaded = this.isFileLoaded,\n
                scriptElements = this.scriptElements,\n
                noCacheUrl = url + (this.getConfig(\'disableCaching\') ? (\'?\' + this.getConfig(\'disableCachingParam\') + \'=\' + Ext.Date.now()) : \'\'),\n
                xhr, status, content, onScriptError;\n
\n
            if (isFileLoaded[url]) {\n
                return this;\n
            }\n
\n
            scope = scope || this;\n
\n
            this.isLoading = true;\n
\n
            if (!synchronous) {\n
                onScriptError = function() {\n
                    //<debug error>\n
                    onError.call(scope, "Failed loading \'" + url + "\', please verify that the file exists", synchronous);\n
                    //</debug>\n
                };\n
\n
                if (!Ext.isReady && Ext.onDocumentReady) {\n
                    Ext.onDocumentReady(function() {\n
                        if (!isFileLoaded[url]) {\n
                            scriptElements[url] = me.injectScriptElement(noCacheUrl, onLoad, onScriptError, scope);\n
                        }\n
                    });\n
                }\n
                else {\n
                    scriptElements[url] = this.injectScriptElement(noCacheUrl, onLoad, onScriptError, scope);\n
                }\n
            }\n
            else {\n
                if (typeof XMLHttpRequest != \'undefined\') {\n
                    xhr = new XMLHttpRequest();\n
                } else {\n
                    xhr = new ActiveXObject(\'Microsoft.XMLHTTP\');\n
                }\n
\n
                try {\n
                    xhr.open(\'GET\', noCacheUrl, false);\n
                    xhr.send(null);\n
                }\n
                catch (e) {\n
                    //<debug error>\n
                    onError.call(this, "Failed loading synchronously via XHR: \'" + url + "\'; It\'s likely that the file is either " +\n
                                       "being loaded from a different domain or from the local file system whereby cross origin " +\n
                                       "requests are not allowed due to security reasons. Use asynchronous loading with " +\n
                                       "Ext.require instead.", synchronous);\n
                    //</debug>\n
                }\n
\n
                status = (xhr.status == 1223) ? 204 : xhr.status;\n
                content = xhr.responseText;\n
\n
                if ((status >= 200 && status < 300) || status == 304 || (status == 0 && content.length > 0)) {\n
                    // Debugger friendly, file names are still shown even though they\'re eval\'ed code\n
                    // Breakpoints work on both Firebug and Chrome\'s Web Inspector\n
                    Ext.globalEval(content + "\\n//@ sourceURL=" + url);\n
                    onLoad.call(scope);\n
                }\n
                else {\n
                    //<debug>\n
                    onError.call(this, "Failed loading synchronously via XHR: \'" + url + "\'; please " +\n
                                       "verify that the file exists. " +\n
                                       "XHR status code: " + status, synchronous);\n
                    //</debug>\n
                }\n
\n
                // Prevent potential IE memory leak\n
                xhr = null;\n
            }\n
        },\n
\n
        // documented above\n
        syncRequire: function() {\n
            var syncModeEnabled = this.syncModeEnabled;\n
\n
            if (!syncModeEnabled) {\n
                this.syncModeEnabled = true;\n
            }\n
\n
            this.require.apply(this, arguments);\n
\n
            if (!syncModeEnabled) {\n
                this.syncModeEnabled = false;\n
            }\n
\n
            this.refreshQueue();\n
        },\n
\n
        // documented above\n
        require: function(expressions, fn, scope, excludes) {\n
            var excluded = {},\n
                included = {},\n
                queue = this.queue,\n
                classNameToFilePathMap = this.classNameToFilePathMap,\n
                isClassFileLoaded = this.isClassFileLoaded,\n
                excludedClassNames = [],\n
                possibleClassNames = [],\n
                classNames = [],\n
                references = [],\n
                callback,\n
                syncModeEnabled,\n
                filePath, expression, exclude, className,\n
                possibleClassName, i, j, ln, subLn;\n
\n
            if (excludes) {\n
                excludes = arrayFrom(excludes);\n
\n
                for (i = 0,ln = excludes.length; i < ln; i++) {\n
                    exclude = excludes[i];\n
\n
                    if (typeof exclude == \'string\' && exclude.length > 0) {\n
                        excludedClassNames = Manager.getNamesByExpression(exclude);\n
\n
                        for (j = 0,subLn = excludedClassNames.length; j < subLn; j++) {\n
                            excluded[excludedClassNames[j]] = true;\n
                        }\n
                    }\n
                }\n
            }\n
\n
            expressions = arrayFrom(expressions);\n
\n
            if (fn) {\n
                if (fn.length > 0) {\n
                    callback = function() {\n
                        var classes = [],\n
                            i, ln, name;\n
\n
                        for (i = 0,ln = references.length; i < ln; i++) {\n
                            name = references[i];\n
                            classes.push(Manager.get(name));\n
                        }\n
\n
                        return fn.apply(this, classes);\n
                    };\n
                }\n
                else {\n
                    callback = fn;\n
                }\n
            }\n
            else {\n
                callback = Ext.emptyFn;\n
            }\n
\n
            scope = scope || Ext.global;\n
\n
            for (i = 0,ln = expressions.length; i < ln; i++) {\n
                expression = expressions[i];\n
\n
                if (typeof expression == \'string\' && expression.length > 0) {\n
                    possibleClassNames = Manager.getNamesByExpression(expression);\n
                    subLn = possibleClassNames.length;\n
\n
                    for (j = 0; j < subLn; j++) {\n
                        possibleClassName = possibleClassNames[j];\n
\n
                        if (excluded[possibleClassName] !== true) {\n
                            references.push(possibleClassName);\n
\n
                            if (!Manager.isCreated(possibleClassName) && !included[possibleClassName]) {\n
                                included[possibleClassName] = true;\n
                                classNames.push(possibleClassName);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
\n
            // If the dynamic dependency feature is not being used, throw an error\n
            // if the dependencies are not defined\n
            if (classNames.length > 0) {\n
                if (!this.config.enabled) {\n
                    throw new Error("Ext.Loader is not enabled, so dependencies cannot be resolved dynamically. " +\n
                             "Missing required class" + ((classNames.length > 1) ? "es" : "") + ": " + classNames.join(\', \'));\n
                }\n
            }\n
            else {\n
                callback.call(scope);\n
                return this;\n
            }\n
\n
            syncModeEnabled = this.syncModeEnabled;\n
\n
            if (!syncModeEnabled) {\n
                queue.push({\n
                    requires: classNames.slice(), // this array will be modified as the queue is processed,\n
                                                  // so we need a copy of it\n
                    callback: callback,\n
                    scope: scope\n
                });\n
            }\n
\n
            ln = classNames.length;\n
\n
            for (i = 0; i < ln; i++) {\n
                className = classNames[i];\n
\n
                filePath = this.getPath(className);\n
\n
                // If we are synchronously loading a file that has already been asynchronously loaded before\n
                // we need to destroy the script tag and revert the count\n
                // This file will then be forced loaded in synchronous\n
                if (syncModeEnabled && isClassFileLoaded.hasOwnProperty(className)) {\n
                    this.numPendingFiles--;\n
                    this.removeScriptElement(filePath);\n
                    delete isClassFileLoaded[className];\n
                }\n
\n
                if (!isClassFileLoaded.hasOwnProperty(className)) {\n
                    isClassFileLoaded[className] = false;\n
\n
                    classNameToFilePathMap[className] = filePath;\n
\n
                    this.numPendingFiles++;\n
\n
                    this.loadScriptFile(\n
                        filePath,\n
                        pass(this.onFileLoaded, [className, filePath], this),\n
                        pass(this.onFileLoadError, [className, filePath]),\n
                        this,\n
                        syncModeEnabled\n
                    );\n
                }\n
            }\n
\n
            if (syncModeEnabled) {\n
                callback.call(scope);\n
\n
                if (ln === 1) {\n
                    return Manager.get(className);\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         * @param {String} className\n
         * @param {String} filePath\n
         */\n
        onFileLoaded: function(className, filePath) {\n
            this.numLoadedFiles++;\n
\n
            this.isClassFileLoaded[className] = true;\n
            this.isFileLoaded[filePath] = true;\n
\n
            this.numPendingFiles--;\n
\n
            if (this.numPendingFiles === 0) {\n
                this.refreshQueue();\n
            }\n
\n
            //<debug>\n
            if (!this.syncModeEnabled && this.numPendingFiles === 0 && this.isLoading && !this.hasFileLoadError) {\n
                var queue = this.queue,\n
                    missingClasses = [],\n
                    missingPaths = [],\n
                    requires,\n
                    i, ln, j, subLn;\n
\n
                for (i = 0,ln = queue.length; i < ln; i++) {\n
                    requires = queue[i].requires;\n
\n
                    for (j = 0,subLn = requires.length; j < subLn; j++) {\n
                        if (this.isClassFileLoaded[requires[j]]) {\n
                            missingClasses.push(requires[j]);\n
                        }\n
                    }\n
                }\n
\n
                if (missingClasses.length < 1) {\n
                    return;\n
                }\n
\n
                missingClasses = Ext.Array.filter(Ext.Array.unique(missingClasses), function(item) {\n
                    return !this.requiresMap.hasOwnProperty(item);\n
                }, this);\n
\n
                for (i = 0,ln = missingClasses.length; i < ln; i++) {\n
                    missingPaths.push(this.classNameToFilePathMap[missingClasses[i]]);\n
                }\n
\n
                throw new Error("The following classes are not declared even if their files have been " +\n
                            "loaded: \'" + missingClasses.join("\', \'") + "\'. Please check the source code of their " +\n
                            "corresponding files for possible typos: \'" + missingPaths.join("\', \'"));\n
            }\n
            //</debug>\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        onFileLoadError: function(className, filePath, errorMessage, isSynchronous) {\n
            this.numPendingFiles--;\n
            this.hasFileLoadError = true;\n
\n
            //<debug error>\n
            throw new Error("[Ext.Loader] " + errorMessage);\n
            //</debug>\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        addOptionalRequires: function(requires) {\n
            var optionalRequires = this.optionalRequires,\n
                i, ln, require;\n
\n
            requires = arrayFrom(requires);\n
\n
            for (i = 0, ln = requires.length; i < ln; i++) {\n
                require = requires[i];\n
\n
                arrayInclude(optionalRequires, require);\n
            }\n
\n
            return this;\n
        },\n
\n
        /**\n
         * @private\n
         */\n
        triggerReady: function(force) {\n
            var readyListeners = this.readyListeners,\n
                optionalRequires = this.optionalRequires,\n
                listener;\n
\n
            if (this.isLoading || force) {\n
                this.isLoading = false;\n
\n
                if (optionalRequires.length !== 0) {\n
                    // Clone then empty the array to eliminate potential recursive loop issue\n
                    optionalRequires = optionalRequires.slice();\n
\n
                    // Empty the original array\n
                    this.optionalRequires.length = 0;\n
\n
                    this.require(optionalRequires, pass(this.triggerReady, [true], this), this);\n
                    return this;\n
                }\n
\n
                while (readyListeners.length) {\n
                    listener = readyListeners.shift();\n
                    listener.fn.call(listener.scope);\n
\n
                    if (this.isLoading) {\n
                        return this;\n
                    }\n
                }\n
            }\n
\n
            return this;\n
        },\n
\n
        // duplicate definition (documented above)\n
        onReady: function(fn, scope, withDomReady, options) {\n
            var oldFn;\n
\n
            if (withDomReady !== false && Ext.onDocumentReady) {\n
                oldFn = fn;\n
\n
                fn = function() {\n
                    Ext.onDocumentReady(oldFn, scope, options);\n
                };\n
            }\n
\n
            if (!this.isLoading) {\n
                fn.call(scope);\n
            }\n
            else {\n
                this.readyListeners.push({\n
                    fn: fn,\n
                    scope: scope\n
                });\n
            }\n
        },\n
\n
        /**\n
         * @private\n
         * @param {String} className\n
         */\n
        historyPush: function(className) {\n
            var isInHistory = this.isInHistory;\n
\n
            if (className && this.isClassFileLoaded.hasOwnProperty(className) && !isInHistory[className]) {\n
                isInHistory[className] = true;\n
                this.history.push(className);\n
            }\n
\n
            return this;\n
        }\n
    });\n
\n
    //</feature>\n
\n
    /**\n
     * Convenient alias of {@link Ext.Loader#require}. Please see the introduction documentation of\n
     * {@link Ext.Loader} for examples.\n
     * @member Ext\n
     * @method require\n
     * @inheritdoc Ext.Loader#require\n
     */\n
    Ext.require = alias(Loader, \'require\');\n
\n
    /**\n
     * Synchronous version of {@link Ext#require}, convenient alias of {@link Ext.Loader#syncRequire}.\n
     * @member Ext\n
     * @method syncRequire\n
     * @inheritdoc Ext.Loader#syncRequire\n
     */\n
    Ext.syncRequire = alias(Loader, \'syncRequire\');\n
\n
    /**\n
     * Convenient shortcut to {@link Ext.Loader#exclude}.\n
     * @member Ext\n
     * @method exclude\n
     * @inheritdoc Ext.Loader#exclude\n
     */\n
    Ext.exclude = alias(Loader, \'exclude\');\n
\n
    /**\n
     * Adds a listener to be notified when the document is ready and all dependencies are loaded.\n
     *\n
     * @param {Function} fn The method the event invokes.\n
     * @param {Object} [scope] The scope in which the handler function executes. Defaults to the browser window.\n
     * @param {Boolean} [options] Options object as passed to {@link Ext.Element#addListener}. It is recommended\n
     * that the options `{single: true}` be used so that the handler is removed on first invocation.\n
     * @member Ext\n
     * @method onReady\n
     */\n
    Ext.onReady = function(fn, scope, options) {\n
        Loader.onReady(fn, scope, true, options);\n
    };\n
\n
    Class.registerPreprocessor(\'loader\', function(cls, data, hooks, continueFn) {\n
        var me = this,\n
            dependencies = [],\n
            className = Manager.getName(cls),\n
            i, j, ln, subLn, value, propertyName, propertyValue;\n
\n
        /*\n
        Loop through the dependencyProperties, look for string class names and push\n
        them into a stack, regardless of whether the property\'s value is a string, array or object. For example:\n
        {\n
              extend: \'Ext.MyClass\',\n
              requires: [\'Ext.some.OtherClass\'],\n
              mixins: {\n
                  observable: \'Ext.mixin.Observable\';\n
              }\n
        }\n
        which will later be transformed into:\n
        {\n
              extend: Ext.MyClass,\n
              requires: [Ext.some.OtherClass],\n
              mixins: {\n
                  observable: Ext.mixin.Observable;\n
              }\n
        }\n
        */\n
\n
        for (i = 0,ln = dependencyProperties.length; i < ln; i++) {\n
            propertyName = dependencyProperties[i];\n
\n
            if (data.hasOwnProperty(propertyName)) {\n
                propertyValue = data[propertyName];\n
\n
                if (typeof propertyValue == \'string\') {\n
                    dependencies.push(propertyValue);\n
                }\n
                else if (propertyValue instanceof Array) {\n
                    for (j = 0, subLn = propertyValue.length; j < subLn; j++) {\n
                        value = propertyValue[j];\n
\n
                        if (typeof value == \'string\') {\n
                            dependencies.push(value);\n
                        }\n
                    }\n
                }\n
                else if (typeof propertyValue != \'function\') {\n
                    for (j in propertyValue) {\n
                        if (propertyValue.hasOwnProperty(j)) {\n
                            value = propertyValue[j];\n
\n
                            if (typeof value == \'string\') {\n
                                dependencies.push(value);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
        }\n
\n
        if (dependencies.length === 0) {\n
            return;\n
        }\n
\n
        //<feature classSystem.loader>\n
        //<debug error>\n
        var deadlockPath = [],\n
            requiresMap = Loader.requiresMap,\n
            detectDeadlock;\n
\n
        /*\n
        Automatically detect deadlocks before-hand,\n
        will throw an error with detailed path for ease of debugging. Examples of deadlock cases:\n
\n
        - A extends B, then B extends A\n
        - A requires B, B requires C, then C requires A\n
\n
        The detectDeadlock function will recursively transverse till the leaf, hence it can detect deadlocks\n
        no matter how deep the path is.\n
        */\n
\n
        if (className) {\n
            requiresMap[className] = dependencies;\n
            //<debug>\n
            if (!Loader.requiredByMap) Loader.requiredByMap = {};\n
            Ext.Array.each(dependencies, function(dependency){\n
                if (!Loader.requiredByMap[dependency]) Loader.requiredByMap[dependency] = [];\n
                Loader.requiredByMap[dependency].push(className);\n
            });\n
            //</debug>\n
            detectDeadlock = function(cls) {\n
                deadlockPath.push(cls);\n
\n
                if (requiresMap[cls]) {\n
                    if (Ext.Array.contains(requiresMap[cls], className)) {\n
                        throw new Error("Deadlock detected while loading dependencies! \'" + className + "\' and \'" +\n
                                deadlockPath[1] + "\' " + "mutually require each other. Path: " +\n
                                deadlockPath.join(\' -> \') + " -> " + deadlockPath[0]);\n
                    }\n
\n
                    for (i = 0,ln = requiresMap[cls].length; i < ln; i++) {\n
                        detectDeadlock(requiresMap[cls][i]);\n
                    }\n
                }\n
            };\n
\n
            detectDeadlock(className);\n
        }\n
\n
        //</debug>\n
        //</feature>\n
\n
        Loader.require(dependencies, function() {\n
            for (i = 0,ln = dependencyProperties.length; i < ln; i++) {\n
                propertyName = dependencyProperties[i];\n
\n
                if (data.hasOwnProperty(propertyName)) {\n
                    propertyValue = data[propertyName];\n
\n
                    if (typeof propertyValue == \'string\') {\n
                        data[propertyName] = Manager.get(propertyValue);\n
                    }\n
                    else if (propertyValue instanceof Array) {\n
                        for (j = 0, subLn = propertyValue.length; j < subLn; j++) {\n
                            value = propertyValue[j];\n
\n
                            if (typeof value == \'string\') {\n
                                data[propertyName][j] = Manager.get(value);\n
                            }\n
                        }\n
                    }\n
                    else if (typeof propertyValue != \'function\') {\n
                        for (var k in propertyValue) {\n
                            if (propertyValue.hasOwnProperty(k)) {\n
                                value = propertyValue[k];\n
\n
                                if (typeof value == \'string\') {\n
                                    data[propertyName][k] = Manager.get(value);\n
                                }\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
\n
            continueFn.call(me, cls, data, hooks);\n
        });\n
\n
        return false;\n
    }, true, \'after\', \'className\');\n
\n
    //<feature classSystem.loader>\n
    /**\n
     * @cfg {String[]} uses\n
     * @member Ext.Class\n
     * List of optional classes to load together with this class. These aren\'t necessarily loaded before\n
     * this class is created, but are guaranteed to be available before Ext.onReady listeners are\n
     * invoked\n
     */\n
    Manager.registerPostprocessor(\'uses\', function(name, cls, data) {\n
        var uses = arrayFrom(data.uses),\n
            items = [],\n
            i, ln, item;\n
\n
        for (i = 0,ln = uses.length; i < ln; i++) {\n
            item = uses[i];\n
\n
            if (typeof item == \'string\') {\n
                items.push(item);\n
            }\n
        }\n
\n
        Loader.addOptionalRequires(items);\n
    });\n
\n
    Manager.onCreated(function(className) {\n
        this.historyPush(className);\n
    }, Loader);\n
    //</feature>\n
\n
})(Ext.ClassManager, Ext.Class, Ext.Function.flexSetter, Ext.Function.alias,\n
   Ext.Function.pass, Ext.Array.from, Ext.Array.erase, Ext.Array.include);\n
\n
// initalize the default path of the framework\n
// trimmed down version of sench-touch-debug-suffix.js\n
// with alias / alternates removed, as those are handled separately by\n
// compiler-generated metadata\n
(function() {\n
    var scripts = document.getElementsByTagName(\'script\'),\n
        currentScript = scripts[scripts.length - 1],\n
        src = currentScript.src,\n
        path = src.substring(0, src.lastIndexOf(\'/\') + 1),\n
        Loader = Ext.Loader;\n
\n
    //<debug>\n
    // if we\'re running in dev mode out of the repo src tree, then this\n
    // file will potentially be loaded from the touch/src/core/class folder\n
    // so we\'ll need to adjust for that\n
    if(src.indexOf("src/core/class/") != -1) {\n
        path = path + "../../../";\n
    }\n
    //</debug>\n
    \n
\n
    Loader.setConfig({\n
        enabled: true,\n
        disableCaching: !/[?&](cache|breakpoint)/i.test(location.search),\n
        paths: {\n
            \'Ext\' : path + \'src\'\n
        }\n
    });\n
    \n
})();\n
\n
//@tag dom,core\n
//@define Ext.EventManager\n
//@define Ext.core.EventManager\n
//@require Ext.Loader\n
\n
/**\n
 * @class Ext.EventManager\n
 *\n
 * This object has been deprecated in Sencha Touch 2.0.0. Please refer to the method documentation for specific alternatives.\n
 *\n
 * @deprecated 2.0.0\n
 * @singleton\n
 * @private\n
 */\n
\n
\n
//@tag dom,core\n
//@define Ext-more\n
//@require Ext.EventManager\n
\n
/**\n
 * @class Ext\n
 *\n
 * Ext is the global namespace for the whole Sencha Touch framework. Every class, function and configuration for the\n
 * whole framework exists under this single global variable. The Ext singleton itself contains a set of useful helper\n
 * functions (like {@link #apply}, {@link #min} and others), but most of the framework that you use day to day exists\n
 * in specialized classes (for example {@link Ext.Panel}, {@link Ext.Carousel} and others).\n
 *\n
 * If you are new to Sencha Touch we recommend starting with the [Getting Started Guide][getting_started] to\n
 * get a feel for how the framework operates. After that, use the more focused guides on subjects like panels, forms and data\n
 * to broaden your understanding. The MVC guides take you through the process of building full applications using the\n
 * framework, and detail how to deploy them to production.\n
 *\n
 * The functions listed below are mostly utility functions used internally by many of the classes shipped in the\n
 * framework, but also often useful in your own apps.\n
 *\n
 * A method that is crucial to beginning your application is {@link #setup Ext.setup}. Please refer to it\'s documentation, or the\n
 * [Getting Started Guide][getting_started] as a reference on beginning your application.\n
 *\n
 *     Ext.setup({\n
 *         onReady: function() {\n
 *             Ext.Viewport.add({\n
 *                 xtype: \'component\',\n
 *                 html: \'Hello world!\'\n
 *             });\n
 *         }\n
 *     });\n
 *\n
 * [getting_started]: #!/guide/getting_started\n
 */\n
Ext.setVersion(\'touch\', \'2.1.0\');\n
\n
Ext.apply(Ext, {\n
    /**\n
     * The version of the framework\n
     * @type String\n
     */\n
    version: Ext.getVersion(\'touch\'),\n
\n
    /**\n
     * @private\n
     */\n
    idSeed: 0,\n
\n
    /**\n
     * Repaints the whole page. This fixes frequently encountered painting issues in mobile Safari.\n
     */\n
    repaint: function() {\n
        var mask = Ext.getBody().createChild({\n
            cls: Ext.baseCSSPrefix + \'mask \' + Ext.baseCSSPrefix + \'mask-transparent\'\n
        });\n
        setTimeout(function() {\n
            mask.destroy();\n
        }, 0);\n
    },\n
\n
    /**\n
     * Generates unique ids. If the element already has an `id`, it is unchanged.\n
     * @param {Mixed} el (optional) The element to generate an id for.\n
     * @param {String} [prefix=ext-gen] (optional) The `id` prefix.\n
     * @return {String} The generated `id`.\n
     */\n
    id: function(el, prefix) {\n
        if (el && el.id) {\n
            return el.id;\n
        }\n
\n
        el = Ext.getDom(el) || {};\n
\n
        if (el === document || el === document.documentElement) {\n
            el.id = \'ext-application\';\n
        }\n
        else if (el === document.body) {\n
            el.id = \'ext-viewport\';\n
        }\n
        else if (el === window) {\n
            el.id = \'ext-window\';\n
        }\n
\n
        el.id = el.id || ((prefix || \'ext-element-\') + (++Ext.idSeed));\n
\n
        return el.id;\n
    },\n
\n
    /**\n
     * Returns the current document body as an {@link Ext.Element}.\n
     * @return {Ext.Element} The document body.\n
     */\n
    getBody: function() {\n
        if (!Ext.documentBodyElement) {\n
            if (!document.body) {\n
                throw new Error("[Ext.getBody] document.body does not exist at this point");\n
            }\n
\n
            Ext.documentBodyElement = Ext.get(document.body);\n
        }\n
\n
        return Ext.documentBodyElement;\n
    },\n
\n
    /**\n
     * Returns the current document head as an {@link Ext.Element}.\n
     * @return {Ext.Element} The document head.\n
     */\n
    getHead: function() {\n
        if (!Ext.documentHeadElement) {\n
            Ext.documentHeadElement = Ext.get(document.head || document.getElementsByTagName(\'head\')[0]);\n
        }\n
\n
        return Ext.documentHeadElement;\n
    },\n
\n
    /**\n
     * Returns the current HTML document object as an {@link Ext.Element}.\n
     * @return {Ext.Element} The document.\n
     */\n
    getDoc: function() {\n
        if (!Ext.documentElement) {\n
            Ext.documentElement = Ext.get(document);\n
        }\n
\n
        return Ext.documentElement;\n
    },\n
\n
    /**\n
     * This is shorthand reference to {@link Ext.ComponentMgr#get}.\n
     * Looks up an existing {@link Ext.Component Component} by {@link Ext.Component#getId id}\n
     * @param {String} id The component {@link Ext.Component#getId id}\n
     * @return {Ext.Component} The Component, `undefined` if not found, or `null` if a\n
     * Class was found.\n
    */\n
    getCmp: function(id) {\n
        return Ext.ComponentMgr.get(id);\n
    },\n
\n
    /**\n
     * Copies a set of named properties from the source object to the destination object.\n
     *\n
     * Example:\n
     *\n
     *     ImageComponent = Ext.extend(Ext.Component, {\n
     *         initComponent: function() {\n
     *             this.autoEl = { tag: \'img\' };\n
     *             MyComponent.superclass.initComponent.apply(this, arguments);\n
     *             this.initialBox = Ext.copyTo({}, this.initialConfig, \'x,y,width,height\');\n
     *         }\n
     *     });\n
     *\n
     * Important note: To borrow class prototype methods, use {@link Ext.Base#borrow} instead.\n
     *\n
     * @param {Object} dest The destination object.\n
     * @param {Object} source The source object.\n
     * @param {String/String[]} names Either an Array of property names, or a comma-delimited list\n
     * of property names to copy.\n
     * @param {Boolean} [usePrototypeKeys=false] (optional) Pass `true` to copy keys off of the prototype as well as the instance.\n
     * @return {Object} The modified object.\n
     */\n
    copyTo : function(dest, source, names, usePrototypeKeys) {\n
        if (typeof names == \'string\') {\n
            names = names.split(/[,;\\s]/);\n
        }\n
        Ext.each (names, function(name) {\n
            if (usePrototypeKeys || source.hasOwnProperty(name)) {\n
                dest[name] = source[name];\n
            }\n
        }, this);\n
        return dest;\n
    },\n
\n
    /**\n
     * Attempts to destroy any objects passed to it by removing all event listeners, removing them from the\n
     * DOM (if applicable) and calling their destroy functions (if available).  This method is primarily\n
     * intended for arguments of type {@link Ext.Element} and {@link Ext.Component}.\n
     * Any number of elements and/or components can be passed into this function in a single\n
     * call as separate arguments.\n
     * @param {Mixed...} args An {@link Ext.Element}, {@link Ext.Component}, or an Array of either of these to destroy.\n
     */\n
    destroy: function() {\n
        var args = arguments,\n
            ln = args.length,\n
            i, item;\n
\n
        for (i = 0; i < ln; i++) {\n
            item = args[i];\n
\n
            if (item) {\n
                if (Ext.isArray(item)) {\n
                    this.destroy.apply(this, item);\n
                }\n
                else if (Ext.isFunction(item.destroy)) {\n
                    item.destroy();\n
                }\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Return the dom node for the passed String (id), dom node, or Ext.Element.\n
     * Here are some examples:\n
     *\n
     *     // gets dom node based on id\n
     *     var elDom = Ext.getDom(\'elId\');\n
     *\n
     *     // gets dom node based on the dom node\n
     *     var elDom1 = Ext.getDom(elDom);\n
     *\n
     *     // If we don\'t know if we are working with an\n
     *     // Ext.Element or a dom node use Ext.getDom\n
     *     function(el){\n
     *         var dom = Ext.getDom(el);\n
     *         // do something with the dom node\n
     *     }\n
     *\n
     * __Note:__ the dom node to be found actually needs to exist (be rendered, etc)\n
     * when this method is called to be successful.\n
     * @param {Mixed} el\n
     * @return {HTMLElement}\n
     */\n
    getDom: function(el) {\n
        if (!el || !document) {\n
            return null;\n
        }\n
\n
        return el.dom ? el.dom : (typeof el == \'string\' ? document.getElementById(el) : el);\n
    },\n
\n
    /**\n
     * Removes this element from the document, removes all DOM event listeners, and deletes the cache reference.\n
     * All DOM event listeners are removed from this element.\n
     * @param {HTMLElement} node The node to remove.\n
     */\n
    removeNode: function(node) {\n
        if (node && node.parentNode && node.tagName != \'BODY\') {\n
            Ext.get(node).clearListeners();\n
            node.parentNode.removeChild(node);\n
            delete Ext.cache[node.id];\n
        }\n
    },\n
\n
    /**\n
     * @private\n
     */\n
    defaultSetupConfig: {\n
        eventPublishers: {\n
            dom: {\n
                xclass: \'Ext.event.publisher.Dom\'\n
            },\n
            touchGesture: {\n
                xclass: \'Ext.event.publisher.TouchGesture\',\n
                recognizers: {\n
                    drag: {\n
                        xclass: \'Ext.event.recognizer.Drag\'\n
                    },\n
                    tap: {\n
                        xclass: \'Ext.event.recognizer.Tap\'\n
                    },\n
                    doubleTap: {\n
                        xclass: \'Ext.event.recognizer.DoubleTap\'\n
                    },\n
                    longPress: {\n
                        xclass: \'Ext.event.recognizer.LongPress\'\n
                    },\n
                    swipe: {\n
                        xclass: \'Ext.event.recognizer.HorizontalSwipe\'\n
                    },\n
                    pinch: {\n
                        xclass: \'Ext.event.recognizer.Pinch\'\n
                    },\n
                    rotate: {\n
                        xclass: \'Ext.event.recognizer.Rotate\'\n
                    }\n
                }\n
            },\n
            componentDelegation: {\n
                xclass: \'Ext.event.publisher.ComponentDelegation\'\n
            },\n
            componentPaint: {\n
                xclass: \'Ext.event.publisher.ComponentPaint\'\n
            },\n
//            componentSize: {\n
//                xclass: \'Ext.event.publisher.ComponentSize\'\n
//            },\n
            elementPaint: {\n
                xclass: \'Ext.event.publisher.ElementPaint\'\n
            },\n
            elementSize: {\n
                xclass: \'Ext.event.publisher.ElementSize\'\n
            }\n
            //<feature charts>\n
            ,seriesItemEvents: {\n
                xclass: \'Ext.chart.series.ItemPublisher\'\n
            }\n
            //</feature>\n
        },\n
\n
        //<feature logger>\n
        logger: {\n
            enabled: true,\n
            xclass: \'Ext.log.Logger\',\n
            minPriority: \'deprecate\',\n
            writers: {\n
                console: {\n
                    xclass: \'Ext.log.writer.Console\',\n
                    throwOnErrors: true,\n
                    formatter: {\n
                        xclass: \'Ext.log.formatter.Default\'\n
                    }\n
                }\n
            }\n
        },\n
        //</feature>\n
\n
        animator: {\n
            xclass: \'Ext.fx.Runner\'\n
        },\n
\n
        viewport: {\n
            xclass: \'Ext.viewport.Viewport\'\n
        }\n
    },\n
\n
    /**\n
     * @private\n
     */\n
    isSetup: false,\n
\n
    /**\n
     * This indicate the start timestamp of current cycle.\n
     * It is only reliable during dom-event-initiated cycles and\n
     * {@link Ext.draw.Animator} initiated cycles.\n
     */\n
    frameStartTime: +new Date(),\n
\n
    /**\n
     * @private\n
     */\n
    setupListeners: [],\n
\n
    /**\n
     * @private\n
     */\n
    onSetup: function(fn, scope) {\n
        if (Ext.isSetup) {\n
            fn.call(scope);\n
        }\n
        else {\n
            Ext.setupListeners.push({\n
                fn: fn,\n
                scope: scope\n
            });\n
        }\n
    },\n
\n
    /**\n
     * Ext.setup() is the entry-point to initialize a Sencha Touch application. Note that if your application makes\n
     * use of MVC architecture, use {@link Ext#application} instead.\n
     *\n
     * This method accepts one single argument in object format. The most basic use of Ext.setup() is as follows:\n
     *\n
     *     Ext.setup({\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * This sets up the viewport, initializes the event system, instantiates a default animation runner, and a default\n
     * logger (during development). When all of that is ready, it invokes the callback function given to the `onReady` key.\n
     *\n
     * The default scope (`this`) of `onReady` is the main viewport. By default the viewport instance is stored in\n
     * {@link Ext.Viewport}. For example, this snippet adds a \'Hello World\' button that is centered on the screen:\n
     *\n
     *     Ext.setup({\n
     *         onReady: function() {\n
     *             this.add({\n
     *                 xtype: \'button\',\n
     *                 centered: true,\n
     *                 text: \'Hello world!\'\n
     *             }); // Equivalent to Ext.Viewport.add(...)\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} config An object with the following config options:\n
     *\n
     * @param {Function} config.onReady\n
     * A function to be called when the application is ready. Your application logic should be here.\n
     *\n
     * @param {Object} config.viewport\n
     * A custom config object to be used when creating the global {@link Ext.Viewport} instance. Please refer to the\n
     * {@link Ext.Viewport} documentation for more information.\n
     *\n
     *     Ext.setup({\n
     *         viewport: {\n
     *             width: 500,\n
     *             height: 500\n
     *         },\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * @param {String/Object} config.icon\n
     * Specifies a set of URLs to the application icon for different device form factors. This icon is displayed\n
     * when the application is added to the device\'s Home Screen.\n
     *\n
     *     Ext.setup({\n
     *         icon: {\n
     *             57: \'resources/icons/Icon.png\',\n
     *             72: \'resources/icons/Icon~ipad.png\',\n
     *             114: \'resources/icons/Icon@2x.png\',\n
     *             144: \'resources/icons/Icon~ipad@2x.png\'\n
     *         },\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * Each key represents the dimension of the icon as a square shape. For example: \'57\' is the key for a 57 x 57\n
     * icon image. Here is the breakdown of each dimension and its device target:\n
     *\n
     * - 57: Non-retina iPhone, iPod touch, and all Android devices\n
     * - 72: Retina iPhone and iPod touch\n
     * - 114: Non-retina iPad (first and second generation)\n
     * - 144: Retina iPad (third generation)\n
     *\n
     * Note that the dimensions of the icon images must be exactly 57x57, 72x72, 114x114 and 144x144 respectively.\n
     *\n
     * It is highly recommended that you provide all these different sizes to accommodate a full range of\n
     * devices currently available. However if you only have one icon in one size, make it 57x57 in size and\n
     * specify it as a string value. This same icon will be used on all supported devices.\n
     *\n
     *     Ext.setup({\n
     *         icon: \'resources/icons/Icon.png\',\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} config.startupImage\n
     * Specifies a set of URLs to the application startup images for different device form factors. This image is\n
     * displayed when the application is being launched from the Home Screen icon. Note that this currently only applies\n
     * to iOS devices.\n
     *\n
     *     Ext.setup({\n
     *         startupImage: {\n
     *             \'320x460\': \'resources/startup/320x460.jpg\',\n
     *             \'640x920\': \'resources/startup/640x920.png\',\n
     *             \'640x1096\': \'resources/startup/640x1096.png\',\n
     *             \'768x1004\': \'resources/startup/768x1004.png\',\n
     *             \'748x1024\': \'resources/startup/748x1024.png\',\n
     *             \'1536x2008\': \'resources/startup/1536x2008.png\',\n
     *             \'1496x2048\': \'resources/startup/1496x2048.png\'\n
     *         },\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * Each key represents the dimension of the image. For example: \'320x460\' is the key for a 320px x 460px image.\n
     * Here is the breakdown of each dimension and its device target:\n
     *\n
     * - 320x460: Non-retina iPhone, iPod touch, and all Android devices\n
     * - 640x920: Retina iPhone and iPod touch\n
     * - 640x1096: iPhone 5 and iPod touch (fifth generation)\n
     * - 768x1004: Non-retina iPad (first and second generation) in portrait orientation\n
     * - 748x1024: Non-retina iPad (first and second generation) in landscape orientation\n
     * - 1536x2008: Retina iPad (third generation) in portrait orientation\n
     * - 1496x2048: Retina iPad (third generation) in landscape orientation\n
     *\n
     * Please note that there\'s no automatic fallback mechanism for the startup images. In other words, if you don\'t specify\n
     * a valid image for a certain device, nothing will be displayed while the application is being launched on that device.\n
     *\n
     * @param {Boolean} isIconPrecomposed\n
     * True to not having a glossy effect added to the icon by the OS, which will preserve its exact look. This currently\n
     * only applies to iOS devices.\n
     *\n
     * @param {String} statusBarStyle\n
     * The style of status bar to be shown on applications added to the iOS home screen. Valid options are:\n
     *\n
     * * `default`\n
     * * `black`\n
     * * `black-translucent`\n
     *\n
     * @param {String[]} config.requires\n
     * An array of required classes for your application which will be automatically loaded before `onReady` is invoked.\n
     * Please refer to {@link Ext.Loader} and {@link Ext.Loader#require} for more information.\n
     *\n
     *     Ext.setup({\n
     *         requires: [\'Ext.Button\', \'Ext.tab.Panel\'],\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} config.eventPublishers\n
     * Sencha Touch, by default, includes various {@link Ext.event.recognizer.Recognizer} subclasses to recognize events fired\n
     * in your application. The list of default recognizers can be found in the documentation for\n
     * {@link Ext.event.recognizer.Recognizer}.\n
     *\n
     * To change the default recognizers, you can use the following syntax:\n
     *\n
     *     Ext.setup({\n
     *         eventPublishers: {\n
     *             touchGesture: {\n
     *                 recognizers: {\n
     *                     swipe: {\n
     *                         // this will include both vertical and horizontal swipe recognizers\n
     *                         xclass: \'Ext.event.recognizer.Swipe\'\n
     *                     }\n
     *                 }\n
     *             }\n
     *         },\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * You can also disable recognizers using this syntax:\n
     *\n
     *     Ext.setup({\n
     *         eventPublishers: {\n
     *             touchGesture: {\n
     *                 recognizers: {\n
     *                     swipe: null,\n
     *                     pinch: null,\n
     *                     rotate: null\n
     *                 }\n
     *             }\n
     *         },\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     */\n
    setup: function(config) {\n
        var defaultSetupConfig = Ext.defaultSetupConfig,\n
            emptyFn = Ext.emptyFn,\n
            onReady = config.onReady || emptyFn,\n
            onUpdated = config.onUpdated || emptyFn,\n
            scope = config.scope,\n
            requires = Ext.Array.from(config.requires),\n
            extOnReady = Ext.onReady,\n
            head = Ext.getHead(),\n
            callback, viewport, precomposed;\n
\n
        Ext.setup = function() {\n
            throw new Error("Ext.setup has already been called before");\n
        };\n
\n
        delete config.requires;\n
        delete config.onReady;\n
        delete config.onUpdated;\n
        delete config.scope;\n
\n
        Ext.require([\'Ext.event.Dispatcher\']);\n
\n
        callback = function() {\n
            var listeners = Ext.setupListeners,\n
                ln = listeners.length,\n
                i, listener;\n
\n
            delete Ext.setupListeners;\n
            Ext.isSetup = true;\n
\n
            for (i = 0; i < ln; i++) {\n
                listener = listeners[i];\n
                listener.fn.call(listener.scope);\n
            }\n
\n
            Ext.onReady = extOnReady;\n
            Ext.onReady(onReady, scope);\n
        };\n
\n
        Ext.onUpdated = onUpdated;\n
        Ext.onReady = function(fn, scope) {\n
            var origin = onReady;\n
\n
            onReady = function() {\n
                origin();\n
                Ext.onReady(fn, scope);\n
            };\n
        };\n
\n
        config = Ext.merge({}, defaultSetupConfig, config);\n
\n
        Ext.onDocumentReady(function() {\n
            Ext.factoryConfig(config, function(data) {\n
      

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAY=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="6" aka="AAAAAAAAAAY=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

          Ext.event.Dispatcher.getInstance().setPublishers(data.eventPublishers);\n
\n
                if (data.logger) {\n
                    Ext.Logger = data.logger;\n
                }\n
\n
                if (data.animator) {\n
                    Ext.Animator = data.animator;\n
                }\n
\n
                if (data.viewport) {\n
                    Ext.Viewport = viewport = data.viewport;\n
\n
                    if (!scope) {\n
                        scope = viewport;\n
                    }\n
\n
                    Ext.require(requires, function() {\n
                        Ext.Viewport.on(\'ready\', callback, null, {single: true});\n
                    });\n
                }\n
                else {\n
                    Ext.require(requires, callback);\n
                }\n
            });\n
        });\n
\n
        function addMeta(name, content) {\n
            var meta = document.createElement(\'meta\');\n
            meta.setAttribute(\'name\', name);\n
            meta.setAttribute(\'content\', content);\n
            head.append(meta);\n
        }\n
\n
        function addIcon(href, sizes, precomposed) {\n
            var link = document.createElement(\'link\');\n
            link.setAttribute(\'rel\', \'apple-touch-icon\' + (precomposed ? \'-precomposed\' : \'\'));\n
            link.setAttribute(\'href\', href);\n
            if (sizes) {\n
                link.setAttribute(\'sizes\', sizes);\n
            }\n
            head.append(link);\n
        }\n
\n
        function addStartupImage(href, media) {\n
            var link = document.createElement(\'link\');\n
            link.setAttribute(\'rel\', \'apple-touch-startup-image\');\n
            link.setAttribute(\'href\', href);\n
            if (media) {\n
                link.setAttribute(\'media\', media);\n
            }\n
            head.append(link);\n
        }\n
\n
        var icon = config.icon,\n
            isIconPrecomposed = Boolean(config.isIconPrecomposed),\n
            startupImage = config.startupImage || {},\n
            statusBarStyle = config.statusBarStyle,\n
            devicePixelRatio = window.devicePixelRatio || 1;\n
\n
        if (navigator.standalone) {\n
            addMeta(\'viewport\', \'width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0\');\n
        }\n
        else {\n
            addMeta(\'viewport\', \'initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0\');\n
        }\n
        addMeta(\'apple-mobile-web-app-capable\', \'yes\');\n
        addMeta(\'apple-touch-fullscreen\', \'yes\');\n
\n
        // status bar style\n
        if (statusBarStyle) {\n
            addMeta(\'apple-mobile-web-app-status-bar-style\', statusBarStyle);\n
        }\n
\n
        if (Ext.isString(icon)) {\n
            icon = {\n
                57: icon,\n
                72: icon,\n
                114: icon,\n
                144: icon\n
            };\n
        }\n
        else if (!icon) {\n
            icon = {};\n
        }\n
\n
\n
        if (Ext.os.is.iPad) {\n
            if (devicePixelRatio >= 2) {\n
                // Retina iPad - Landscape\n
                if (\'1496x2048\' in startupImage) {\n
                    addStartupImage(startupImage[\'1496x2048\'], \'(orientation: landscape)\');\n
                }\n
                // Retina iPad - Portrait\n
                if (\'1536x2008\' in startupImage) {\n
                    addStartupImage(startupImage[\'1536x2008\'], \'(orientation: portrait)\');\n
                }\n
\n
                // Retina iPad\n
                if (\'144\' in icon) {\n
                    addIcon(icon[\'144\'], \'144x144\', isIconPrecomposed);\n
                }\n
            }\n
            else {\n
                // Non-Retina iPad - Landscape\n
                if (\'748x1024\' in startupImage) {\n
                    addStartupImage(startupImage[\'748x1024\'], \'(orientation: landscape)\');\n
                }\n
                // Non-Retina iPad - Portrait\n
                if (\'768x1004\' in startupImage) {\n
                    addStartupImage(startupImage[\'768x1004\'], \'(orientation: portrait)\');\n
                }\n
\n
                // Non-Retina iPad\n
                if (\'72\' in icon) {\n
                    addIcon(icon[\'72\'], \'72x72\', isIconPrecomposed);\n
                }\n
            }\n
        }\n
        else {\n
            // Retina iPhone, iPod touch with iOS version >= 4.3\n
            if (devicePixelRatio >= 2 && Ext.os.version.gtEq(\'4.3\')) {\n
                if (Ext.os.is.iPhone5) {\n
                    addStartupImage(startupImage[\'640x1096\']);\n
                } else {\n
                    addStartupImage(startupImage[\'640x920\']);\n
                }\n
\n
                // Retina iPhone and iPod touch\n
                if (\'114\' in icon) {\n
                    addIcon(icon[\'114\'], \'114x114\', isIconPrecomposed);\n
                }\n
            }\n
            else {\n
                addStartupImage(startupImage[\'320x460\']);\n
\n
                // Non-Retina iPhone, iPod touch, and Android devices\n
                if (\'57\' in icon) {\n
                    addIcon(icon[\'57\'], null, isIconPrecomposed);\n
                }\n
            }\n
        }\n
    },\n
\n
    /**\n
     * @member Ext\n
     * @method application\n
     *\n
     * Loads Ext.app.Application class and starts it up with given configuration after the page is ready.\n
     *\n
     *     Ext.application({\n
     *         launch: function() {\n
     *             alert(\'Application launched!\');\n
     *         }\n
     *     });\n
     *\n
     * See {@link Ext.app.Application} for details.\n
     *\n
     * @param {Object} config An object with the following config options:\n
     *\n
     * @param {Function} config.launch\n
     * A function to be called when the application is ready. Your application logic should be here. Please see {@link Ext.app.Application}\n
     * for details.\n
     *\n
     * @param {Object} config.viewport\n
     * An object to be used when creating the global {@link Ext.Viewport} instance. Please refer to the {@link Ext.Viewport}\n
     * documentation for more information.\n
     *\n
     *     Ext.application({\n
     *         viewport: {\n
     *             layout: \'vbox\'\n
     *         },\n
     *         launch: function() {\n
     *             Ext.Viewport.add({\n
     *                 flex: 1,\n
     *                 html: \'top (flex: 1)\'\n
     *             });\n
     *\n
     *             Ext.Viewport.add({\n
     *                 flex: 4,\n
     *                 html: \'bottom (flex: 4)\'\n
     *             });\n
     *         }\n
     *     });\n
     *\n
     * @param {String/Object} config.icon\n
     * Specifies a set of URLs to the application icon for different device form factors. This icon is displayed\n
     * when the application is added to the device\'s Home Screen.\n
     *\n
     *     Ext.application({\n
     *         icon: {\n
     *             57: \'resources/icons/Icon.png\',\n
     *             72: \'resources/icons/Icon~ipad.png\',\n
     *             114: \'resources/icons/Icon@2x.png\',\n
     *             144: \'resources/icons/Icon~ipad@2x.png\'\n
     *         },\n
     *         launch: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * Each key represents the dimension of the icon as a square shape. For example: \'57\' is the key for a 57 x 57\n
     * icon image. Here is the breakdown of each dimension and its device target:\n
     *\n
     * - 57: Non-retina iPhone, iPod touch, and all Android devices\n
     * - 72: Retina iPhone and iPod touch\n
     * - 114: Non-retina iPad (first and second generation)\n
     * - 144: Retina iPad (third generation)\n
     *\n
     * Note that the dimensions of the icon images must be exactly 57x57, 72x72, 114x114 and 144x144 respectively.\n
     *\n
     * It is highly recommended that you provide all these different sizes to accommodate a full range of\n
     * devices currently available. However if you only have one icon in one size, make it 57x57 in size and\n
     * specify it as a string value. This same icon will be used on all supported devices.\n
     *\n
     *     Ext.setup({\n
     *         icon: \'resources/icons/Icon.png\',\n
     *         onReady: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} config.startupImage\n
     * Specifies a set of URLs to the application startup images for different device form factors. This image is\n
     * displayed when the application is being launched from the Home Screen icon. Note that this currently only applies\n
     * to iOS devices.\n
     *\n
     *     Ext.application({\n
     *         startupImage: {\n
     *             \'320x460\': \'resources/startup/320x460.jpg\',\n
     *             \'640x920\': \'resources/startup/640x920.png\',\n
     *             \'640x1096\': \'resources/startup/640x1096.png\',\n
     *             \'768x1004\': \'resources/startup/768x1004.png\',\n
     *             \'748x1024\': \'resources/startup/748x1024.png\',\n
     *             \'1536x2008\': \'resources/startup/1536x2008.png\',\n
     *             \'1496x2048\': \'resources/startup/1496x2048.png\'\n
     *         },\n
     *         launch: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * Each key represents the dimension of the image. For example: \'320x460\' is the key for a 320px x 460px image.\n
     * Here is the breakdown of each dimension and its device target:\n
     *\n
     * - 320x460: Non-retina iPhone, iPod touch, and all Android devices\n
     * - 640x920: Retina iPhone and iPod touch\n
     * - 640x1096: iPhone 5 and iPod touch (fifth generation)\n
     * - 768x1004: Non-retina iPad (first and second generation) in portrait orientation\n
     * - 748x1024: Non-retina iPad (first and second generation) in landscape orientation\n
     * - 1536x2008: Retina iPad (third generation) in portrait orientation\n
     * - 1496x2048: Retina iPad (third generation) in landscape orientation\n
     *\n
     * Please note that there\'s no automatic fallback mechanism for the startup images. In other words, if you don\'t specify\n
     * a valid image for a certain device, nothing will be displayed while the application is being launched on that device.\n
     *\n
     * @param {Boolean} config.isIconPrecomposed\n
     * True to not having a glossy effect added to the icon by the OS, which will preserve its exact look. This currently\n
     * only applies to iOS devices.\n
     *\n
     * @param {String} config.statusBarStyle\n
     * The style of status bar to be shown on applications added to the iOS home screen. Valid options are:\n
     *\n
     * * `default`\n
     * * `black`\n
     * * `black-translucent`\n
     *\n
     * @param {String[]} config.requires\n
     * An array of required classes for your application which will be automatically loaded if {@link Ext.Loader#enabled} is set\n
     * to `true`. Please refer to {@link Ext.Loader} and {@link Ext.Loader#require} for more information.\n
     *\n
     *     Ext.application({\n
     *         requires: [\'Ext.Button\', \'Ext.tab.Panel\'],\n
     *         launch: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * @param {Object} config.eventPublishers\n
     * Sencha Touch, by default, includes various {@link Ext.event.recognizer.Recognizer} subclasses to recognize events fired\n
     * in your application. The list of default recognizers can be found in the documentation for {@link Ext.event.recognizer.Recognizer}.\n
     *\n
     * To change the default recognizers, you can use the following syntax:\n
     *\n
     *     Ext.application({\n
     *         eventPublishers: {\n
     *             touchGesture: {\n
     *                 recognizers: {\n
     *                     swipe: {\n
     *                         // this will include both vertical and horizontal swipe recognizers\n
     *                         xclass: \'Ext.event.recognizer.Swipe\'\n
     *                     }\n
     *                 }\n
     *             }\n
     *         },\n
     *         launch: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     *\n
     * You can also disable recognizers using this syntax:\n
     *\n
     *     Ext.application({\n
     *         eventPublishers: {\n
     *             touchGesture: {\n
     *                 recognizers: {\n
     *                     swipe: null,\n
     *                     pinch: null,\n
     *                     rotate: null\n
     *                 }\n
     *             }\n
     *         },\n
     *         launch: function() {\n
     *             // ...\n
     *         }\n
     *     });\n
     */\n
    application: function(config) {\n
        var appName = config.name,\n
            onReady, scope, requires;\n
\n
        if (!config) {\n
            config = {};\n
        }\n
\n
        if (!Ext.Loader.config.paths[appName]) {\n
            Ext.Loader.setPath(appName, config.appFolder || \'app\');\n
        }\n
\n
        requires = Ext.Array.from(config.requires);\n
        config.requires = [\'Ext.app.Application\'];\n
\n
        onReady = config.onReady;\n
        scope = config.scope;\n
\n
        config.onReady = function() {\n
            config.requires = requires;\n
            new Ext.app.Application(config);\n
\n
            if (onReady) {\n
                onReady.call(scope);\n
            }\n
        };\n
\n
        Ext.setup(config);\n
    },\n
\n
    /**\n
     * @private\n
     * @param config\n
     * @param callback\n
     * @member Ext\n
     */\n
    factoryConfig: function(config, callback) {\n
        var isSimpleObject = Ext.isSimpleObject(config);\n
\n
        if (isSimpleObject && config.xclass) {\n
            var className = config.xclass;\n
\n
            delete config.xclass;\n
\n
            Ext.require(className, function() {\n
                Ext.factoryConfig(config, function(cfg) {\n
                    callback(Ext.create(className, cfg));\n
                });\n
            });\n
\n
            return;\n
        }\n
\n
        var isArray = Ext.isArray(config),\n
            keys = [],\n
            key, value, i, ln;\n
\n
        if (isSimpleObject || isArray) {\n
            if (isSimpleObject) {\n
                for (key in config) {\n
                    if (config.hasOwnProperty(key)) {\n
                        value = config[key];\n
                        if (Ext.isSimpleObject(value) || Ext.isArray(value)) {\n
                            keys.push(key);\n
                        }\n
                    }\n
                }\n
            }\n
            else {\n
                for (i = 0,ln = config.length; i < ln; i++) {\n
                    value = config[i];\n
\n
                    if (Ext.isSimpleObject(value) || Ext.isArray(value)) {\n
                        keys.push(i);\n
                    }\n
                }\n
            }\n
\n
            i = 0;\n
            ln = keys.length;\n
\n
            if (ln === 0) {\n
                callback(config);\n
                return;\n
            }\n
\n
            function fn(value) {\n
                config[key] = value;\n
                i++;\n
                factory();\n
            }\n
\n
            function factory() {\n
                if (i >= ln) {\n
                    callback(config);\n
                    return;\n
                }\n
\n
                key = keys[i];\n
                value = config[key];\n
\n
                Ext.factoryConfig(value, fn);\n
            }\n
\n
            factory();\n
            return;\n
        }\n
\n
        callback(config);\n
    },\n
\n
    /**\n
     * A global factory method to instantiate a class from a config object. For example, these two calls are equivalent:\n
     *\n
     *     Ext.factory({ text: \'My Button\' }, \'Ext.Button\');\n
     *     Ext.create(\'Ext.Button\', { text: \'My Button\' });\n
     *\n
     * If an existing instance is also specified, it will be updated with the supplied config object. This is useful\n
     * if you need to either create or update an object, depending on if an instance already exists. For example:\n
     *\n
     *     var button;\n
     *     button = Ext.factory({ text: \'New Button\' }, \'Ext.Button\', button);     // Button created\n
     *     button = Ext.factory({ text: \'Updated Button\' }, \'Ext.Button\', button); // Button updated\n
     *\n
     * @param {Object} config  The config object to instantiate or update an instance with.\n
     * @param {String} classReference  The class to instantiate from.\n
     * @param {Object} [instance]  The instance to update.\n
     * @param [aliasNamespace]\n
     * @member Ext\n
     */\n
    factory: function(config, classReference, instance, aliasNamespace) {\n
        var manager = Ext.ClassManager,\n
            newInstance;\n
\n
        // If config is falsy or a valid instance, destroy the current instance\n
        // (if it exists) and replace with the new one\n
        if (!config || config.isInstance) {\n
            if (instance && instance !== config) {\n
                instance.destroy();\n
            }\n
\n
            return config;\n
        }\n
\n
        if (aliasNamespace) {\n
             // If config is a string value, treat it as an alias\n
            if (typeof config == \'string\') {\n
                return manager.instantiateByAlias(aliasNamespace + \'.\' + config);\n
            }\n
            // Same if \'type\' is given in config\n
            else if (Ext.isObject(config) && \'type\' in config) {\n
                return manager.instantiateByAlias(aliasNamespace + \'.\' + config.type, config);\n
            }\n
        }\n
\n
        if (config === true) {\n
            return instance || manager.instantiate(classReference);\n
        }\n
\n
        //<debug error>\n
        if (!Ext.isObject(config)) {\n
            Ext.Logger.error("Invalid config, must be a valid config object");\n
        }\n
        //</debug>\n
\n
        if (\'xtype\' in config) {\n
            newInstance = manager.instantiateByAlias(\'widget.\' + config.xtype, config);\n
        }\n
        else if (\'xclass\' in config) {\n
            newInstance = manager.instantiate(config.xclass, config);\n
        }\n
\n
        if (newInstance) {\n
            if (instance) {\n
                instance.destroy();\n
            }\n
\n
            return newInstance;\n
        }\n
\n
        if (instance) {\n
            return instance.setConfig(config);\n
        }\n
\n
        return manager.instantiate(classReference, config);\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecateClassMember: function(cls, oldName, newName, message) {\n
        return this.deprecateProperty(cls.prototype, oldName, newName, message);\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecateClassMembers: function(cls, members) {\n
       var prototype = cls.prototype,\n
           oldName, newName;\n
\n
       for (oldName in members) {\n
           if (members.hasOwnProperty(oldName)) {\n
               newName = members[oldName];\n
\n
               this.deprecateProperty(prototype, oldName, newName);\n
           }\n
       }\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecateProperty: function(object, oldName, newName, message) {\n
        if (!message) {\n
            message = "\'" + oldName + "\' is deprecated";\n
        }\n
        if (newName) {\n
            message += ", please use \'" + newName + "\' instead";\n
        }\n
\n
        if (newName) {\n
            Ext.Object.defineProperty(object, oldName, {\n
                get: function() {\n
                    //<debug warn>\n
                    Ext.Logger.deprecate(message, 1);\n
                    //</debug>\n
                    return this[newName];\n
                },\n
                set: function(value) {\n
                    //<debug warn>\n
                    Ext.Logger.deprecate(message, 1);\n
                    //</debug>\n
\n
                    this[newName] = value;\n
                },\n
                configurable: true\n
            });\n
        }\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecatePropertyValue: function(object, name, value, message) {\n
        Ext.Object.defineProperty(object, name, {\n
            get: function() {\n
                //<debug warn>\n
                Ext.Logger.deprecate(message, 1);\n
                //</debug>\n
                return value;\n
            },\n
            configurable: true\n
        });\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecateMethod: function(object, name, method, message) {\n
        object[name] = function() {\n
            //<debug warn>\n
            Ext.Logger.deprecate(message, 2);\n
            //</debug>\n
            if (method) {\n
                return method.apply(this, arguments);\n
            }\n
        };\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    deprecateClassMethod: function(cls, name, method, message) {\n
        if (typeof name != \'string\') {\n
            var from, to;\n
\n
            for (from in name) {\n
                if (name.hasOwnProperty(from)) {\n
                    to = name[from];\n
                    Ext.deprecateClassMethod(cls, from, to);\n
                }\n
            }\n
            return;\n
        }\n
\n
        var isLateBinding = typeof method == \'string\',\n
            member;\n
\n
        if (!message) {\n
            message = "\'" + name + "()\' is deprecated, please use \'" + (isLateBinding ? method : method.name) +\n
                "()\' instead";\n
        }\n
\n
        if (isLateBinding) {\n
            member = function() {\n
                //<debug warn>\n
                Ext.Logger.deprecate(message, this);\n
                //</debug>\n
\n
                return this[method].apply(this, arguments);\n
            };\n
        }\n
        else {\n
            member = function() {\n
                //<debug warn>\n
                Ext.Logger.deprecate(message, this);\n
                //</debug>\n
\n
                return method.apply(this, arguments);\n
            };\n
        }\n
\n
        if (name in cls.prototype) {\n
            Ext.Object.defineProperty(cls.prototype, name, {\n
                value: null,\n
                writable: true,\n
                configurable: true\n
            });\n
        }\n
\n
        cls.addMember(name, member);\n
    },\n
\n
    //<debug>\n
    /**\n
     * Useful snippet to show an exact, narrowed-down list of top-level Components that are not yet destroyed.\n
     * @private\n
     */\n
    showLeaks: function() {\n
        var map = Ext.ComponentManager.all.map,\n
            leaks = [],\n
            parent;\n
\n
        Ext.Object.each(map, function(id, component) {\n
            while ((parent = component.getParent()) && map.hasOwnProperty(parent.getId())) {\n
                component = parent;\n
            }\n
\n
            if (leaks.indexOf(component) === -1) {\n
                leaks.push(component);\n
            }\n
        });\n
\n
        console.log(leaks);\n
    },\n
    //</debug>\n
\n
    /**\n
     * True when the document is fully initialized and ready for action\n
     * @type Boolean\n
     * @member Ext\n
     * @private\n
     */\n
    isReady : false,\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    readyListeners: [],\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    triggerReady: function() {\n
        var listeners = Ext.readyListeners,\n
            i, ln, listener;\n
\n
        if (!Ext.isReady) {\n
            Ext.isReady = true;\n
\n
            for (i = 0,ln = listeners.length; i < ln; i++) {\n
                listener = listeners[i];\n
                listener.fn.call(listener.scope);\n
            }\n
            delete Ext.readyListeners;\n
        }\n
    },\n
\n
    /**\n
     * @private\n
     * @member Ext\n
     */\n
    onDocumentReady: function(fn, scope) {\n
        if (Ext.isReady) {\n
            fn.call(scope);\n
        }\n
        else {\n
            var triggerFn = Ext.triggerReady;\n
\n
            Ext.readyListeners.push({\n
                fn: fn,\n
                scope: scope\n
            });\n
\n
            if (Ext.browser.is.PhoneGap && !Ext.os.is.Desktop) {\n
                if (!Ext.readyListenerAttached) {\n
                    Ext.readyListenerAttached = true;\n
                    document.addEventListener(\'deviceready\', triggerFn, false);\n
                }\n
            }\n
            else {\n
                if (document.readyState.match(/interactive|complete|loaded/) !== null) {\n
                    triggerFn();\n
                }\n
                else if (!Ext.readyListenerAttached) {\n
                    Ext.readyListenerAttached = true;\n
                    window.addEventListener(\'DOMContentLoaded\', triggerFn, false);\n
                }\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Calls function after specified delay, or right away when delay == 0.\n
     * @param {Function} callback The callback to execute.\n
     * @param {Object} scope (optional) The scope to execute in.\n
     * @param {Array} args (optional) The arguments to pass to the function.\n
     * @param {Number} delay (optional) Pass a number to delay the call by a number of milliseconds.\n
     * @member Ext\n
     */\n
    callback: function(callback, scope, args, delay) {\n
        if (Ext.isFunction(callback)) {\n
            args = args || [];\n
            scope = scope || window;\n
            if (delay) {\n
                Ext.defer(callback, delay, scope, args);\n
            } else {\n
                callback.apply(scope, args);\n
            }\n
        }\n
    }\n
});\n
\n
//<debug>\n
Ext.Object.defineProperty(Ext, \'Msg\', {\n
    get: function() {\n
        Ext.Logger.error("Using Ext.Msg without requiring Ext.MessageBox");\n
        return null;\n
    },\n
    set: function(value) {\n
        Ext.Object.defineProperty(Ext, \'Msg\', {\n
            value: value\n
        });\n
        return value;\n
    },\n
    configurable: true\n
});\n
//</debug>\n
\n
\n
//@tag dom,core\n
//@require Ext-more\n
\n
/**\n
 * Provides information about browser.\n
 *\n
 * Should not be manually instantiated unless for unit-testing.\n
 * Access the global instance stored in {@link Ext.browser} instead.\n
 * @private\n
 */\n
Ext.define(\'Ext.env.Browser\', {\n
    requires: [\'Ext.Version\'],\n
\n
    statics: {\n
        browserNames: {\n
            ie: \'IE\',\n
            firefox: \'Firefox\',\n
            safari: \'Safari\',\n
            chrome: \'Chrome\',\n
            opera: \'Opera\',\n
            dolfin: \'Dolfin\',\n
            webosbrowser: \'webOSBrowser\',\n
            chromeMobile: \'ChromeMobile\',\n
            silk: \'Silk\',\n
            other: \'Other\'\n
        },\n
        engineNames: {\n
            webkit: \'WebKit\',\n
            gecko: \'Gecko\',\n
            presto: \'Presto\',\n
            trident: \'Trident\',\n
            other: \'Other\'\n
        },\n
        enginePrefixes: {\n
            webkit: \'AppleWebKit/\',\n
            gecko: \'Gecko/\',\n
            presto: \'Presto/\',\n
            trident: \'Trident/\'\n
        },\n
        browserPrefixes: {\n
            ie: \'MSIE \',\n
            firefox: \'Firefox/\',\n
            chrome: \'Chrome/\',\n
            safari: \'Version/\',\n
            opera: \'Opera/\',\n
            dolfin: \'Dolfin/\',\n
            webosbrowser: \'wOSBrowser/\',\n
            chromeMobile: \'CrMo/\',\n
            silk: \'Silk/\'\n
        }\n
    },\n
\n
    styleDashPrefixes: {\n
        WebKit: \'-webkit-\',\n
        Gecko: \'-moz-\',\n
        Trident: \'-ms-\',\n
        Presto: \'-o-\',\n
        Other: \'\'\n
    },\n
\n
    stylePrefixes: {\n
        WebKit: \'Webkit\',\n
        Gecko: \'Moz\',\n
        Trident: \'ms\',\n
        Presto: \'O\',\n
        Other: \'\'\n
    },\n
\n
    propertyPrefixes: {\n
        WebKit: \'webkit\',\n
        Gecko: \'moz\',\n
        Trident: \'ms\',\n
        Presto: \'o\',\n
        Other: \'\'\n
    },\n
\n
    // scope: Ext.env.Browser.prototype\n
\n
    /**\n
     * A "hybrid" property, can be either accessed as a method call, for example:\n
     *\n
     *     if (Ext.browser.is(\'IE\')) {\n
     *         // ...\n
     *     }\n
     *\n
     * Or as an object with Boolean properties, for example:\n
     *\n
     *     if (Ext.browser.is.IE) {\n
     *         // ...\n
     *     }\n
     *\n
     * Versions can be conveniently checked as well. For example:\n
     *\n
     *     if (Ext.browser.is.IE6) {\n
     *         // Equivalent to (Ext.browser.is.IE && Ext.browser.version.equals(6))\n
     *     }\n
     *\n
     * __Note:__ Only {@link Ext.Version#getMajor major component}  and {@link Ext.Version#getShortVersion simplified}\n
     * value of the version are available via direct property checking.\n
     *\n
     * Supported values are:\n
     *\n
     * - IE\n
     * - Firefox\n
     * - Safari\n
     * - Chrome\n
     * - Opera\n
     * - WebKit\n
     * - Gecko\n
     * - Presto\n
     * - Trident\n
     * - WebView\n
     * - Other\n
     *\n
     * @param {String} value The OS name to check.\n
     * @return {Boolean}\n
     */\n
    is: Ext.emptyFn,\n
\n
    /**\n
     * The full name of the current browser.\n
     * Possible values are:\n
     *\n
     * - IE\n
     * - Firefox\n
     * - Safari\n
     * - Chrome\n
     * - Opera\n
     * - Other\n
     * @type String\n
     * @readonly\n
     */\n
    name: null,\n
\n
    /**\n
     * Refer to {@link Ext.Version}.\n
     * @type Ext.Version\n
     * @readonly\n
     */\n
    version: null,\n
\n
    /**\n
     * The full name of the current browser\'s engine.\n
     * Possible values are:\n
     *\n
     * - WebKit\n
     * - Gecko\n
     * - Presto\n
     * - Trident\n
     * - Other\n
     * @type String\n
     * @readonly\n
     */\n
    engineName: null,\n
\n
    /**\n
     * Refer to {@link Ext.Version}.\n
     * @type Ext.Version\n
     * @readonly\n
     */\n
    engineVersion: null,\n
\n
    setFlag: function(name, value) {\n
        if (typeof value == \'undefined\') {\n
            value = true;\n
        }\n
\n
        this.is[name] = value;\n
        this.is[name.toLowerCase()] = value;\n
\n
        return this;\n
    },\n
\n
    constructor: function(userAgent) {\n
        /**\n
         * @property {String}\n
         * Browser User Agent string.\n
         */\n
        this.userAgent = userAgent;\n
\n
        is = this.is = function(name) {\n
            return is[name] === true;\n
        };\n
\n
        var statics = this.statics(),\n
            browserMatch = userAgent.match(new RegExp(\'((?:\' + Ext.Object.getValues(statics.browserPrefixes).join(\')|(?:\') + \'))([\\\\w\\\\._]+)\')),\n
            engineMatch = userAgent.match(new RegExp(\'((?:\' + Ext.Object.getValues(statics.enginePrefixes).join(\')|(?:\') + \'))([\\\\w\\\\._]+)\')),\n
            browserNames = statics.browserNames,\n
            browserName = browserNames.other,\n
            engineNames = statics.engineNames,\n
            engineName = engineNames.other,\n
            browserVersion = \'\',\n
            engineVersion = \'\',\n
            isWebView = false,\n
            is, i, name;\n
\n
        if (browserMatch) {\n
            browserName = browserNames[Ext.Object.getKey(statics.browserPrefixes, browserMatch[1])];\n
\n
            browserVersion = new Ext.Version(browserMatch[2]);\n
        }\n
\n
        if (engineMatch) {\n
            engineName = engineNames[Ext.Object.getKey(statics.enginePrefixes, engineMatch[1])];\n
            engineVersion = new Ext.Version(engineMatch[2]);\n
        }\n
\n
        // Facebook changes the userAgent when you view a website within their iOS app. For some reason, the strip out information\n
        // about the browser, so we have to detect that and fake it...\n
        if (userAgent.match(/FB/) && browserName == "Other") {\n
            browserName = browserNames.safari;\n
            engineName = engineNames.webkit;\n
        }\n
\n
        if (userAgent.match(/Android.*Chrome/g)) {\n
            browserName = \'ChromeMobile\';\n
        }\n
\n
        Ext.apply(this, {\n
            engineName: engineName,\n
            engineVersion: engineVersion,\n
            name: browserName,\n
            version: browserVersion\n
        });\n
\n
        this.setFlag(browserName);\n
\n
        if (browserVersion) {\n
            this.setFlag(browserName + (browserVersion.getMajor() || \'\'));\n
            this.setFlag(browserName + browserVersion.getShortVersion());\n
        }\n
\n
        for (i in browserNames) {\n
            if (browserNames.hasOwnProperty(i)) {\n
                name = browserNames[i];\n
\n
                this.setFlag(name, browserName === name);\n
            }\n
        }\n
\n
        this.setFlag(name);\n
\n
        if (engineVersion) {\n
            this.setFlag(engineName + (engineVersion.getMajor() || \'\'));\n
            this.setFlag(engineName + engineVersion.getShortVersion());\n
        }\n
\n
        for (i in engineNames) {\n
            if (engineNames.hasOwnProperty(i)) {\n
                name = engineNames[i];\n
\n
                this.setFlag(name, engineName === name);\n
            }\n
        }\n
\n
        this.setFlag(\'Standalone\', !!navigator.standalone);\n
\n
        if (typeof window.PhoneGap != \'undefined\' || typeof window.Cordova != \'undefined\' || typeof window.cordova != \'undefined\') {\n
            isWebView = true;\n
            this.setFlag(\'PhoneGap\');\n
        }\n
        else if (!!window.isNK) {\n
            isWebView = true;\n
            this.setFlag(\'Sencha\');\n
        }\n
\n
        // Check if running in UIWebView\n
        if (/(iPhone|iPod|iPad).*AppleWebKit(?!.*Safari)(?!.*FBAN)/i.test(userAgent)) {\n
            isWebView = true;\n
        }\n
\n
        // Flag to check if it we are in the WebView\n
        this.setFlag(\'WebView\', isWebView);\n
\n
        /**\n
         * @property {Boolean}\n
         * `true` if browser is using strict mode.\n
         */\n
        this.isStrict = document.compatMode == "CSS1Compat";\n
\n
        /**\n
         * @property {Boolean}\n
         * `true` if page is running over SSL.\n
         */\n
        this.isSecure = /^https/i.test(window.location.protocol);\n
\n
        return this;\n
    },\n
\n
    getStyleDashPrefix: function() {\n
        return this.styleDashPrefixes[this.engineName];\n
    },\n
\n
    getStylePrefix: function() {\n
        return this.stylePrefixes[this.engineName];\n
    },\n
\n
    getVendorProperyName: function(name) {\n
        var prefix = this.propertyPrefixes[this.engineName];\n
\n
        if (prefix.length > 0) {\n
            return prefix + Ext.String.capitalize(name);\n
        }\n
\n
        return name;\n
    }\n
\n
}, function() {\n
    /**\n
     * @class Ext.browser\n
     * @extends Ext.env.Browser\n
     * @singleton\n
     * Provides useful information about the current browser.\n
     *\n
     * Example:\n
     *\n
     *     if (Ext.browser.is.IE) {\n
     *         // IE specific code here\n
     *     }\n
     *\n
     *     if (Ext.browser.is.WebKit) {\n
     *         // WebKit specific code here\n
     *     }\n
     *\n
     *     console.log("Version " + Ext.browser.version);\n
     *\n
     * For a full list of supported values, refer to {@link #is} property/method.\n
     *\n
     * @aside guide environment_package\n
     */\n
    var browserEnv = Ext.browser = new this(Ext.global.navigator.userAgent);\n
\n
});\n
\n
//@tag dom,core\n
//@require Ext.env.Browser\n
\n
/**\n
 * Provides information about operating system environment.\n
 *\n
 * Should not be manually instantiated unless for unit-testing.\n
 * Access the global instance stored in {@link Ext.os} instead.\n
 * @private\n
 */\n
Ext.define(\'Ext.env.OS\', {\n
\n
    requires: [\'Ext.Version\'],\n
\n
    statics: {\n
        names: {\n
            ios: \'iOS\',\n
            android: \'Android\',\n
            webos: \'webOS\',\n
            blackberry: \'BlackBerry\',\n
            rimTablet: \'RIMTablet\',\n
            mac: \'MacOS\',\n
            win: \'Windows\',\n
            linux: \'Linux\',\n
            bada: \'Bada\',\n
            other: \'Other\'\n
        },\n
        prefixes: {\n
            ios: \'i(?:Pad|Phone|Pod)(?:.*)CPU(?: iPhone)? OS \',\n
            android: \'(Android |HTC_|Silk/)\', // Some HTC devices ship with an OSX userAgent by default,\n
                                        // so we need to add a direct check for HTC_\n
            blackberry: \'BlackBerry(?:.*)Version\\/\',\n
            rimTablet: \'RIM Tablet OS \',\n
            webos: \'(?:webOS|hpwOS)\\/\',\n
            bada: \'Bada\\/\'\n
        }\n
    },\n
\n
    /**\n
     * A "hybrid" property, can be either accessed as a method call, i.e:\n
     *\n
     *     if (Ext.os.is(\'Android\')) {\n
     *         // ...\n
     *     }\n
     *\n
     * or as an object with boolean properties, i.e:\n
     *\n
     *     if (Ext.os.is.Android) {\n
     *         // ...\n
     *     }\n
     *\n
     * Versions can be conveniently checked as well. For example:\n
     *\n
     *     if (Ext.os.is.Android2) {\n
     *         // Equivalent to (Ext.os.is.Android && Ext.os.version.equals(2))\n
     *     }\n
     *\n
     *     if (Ext.os.is.iOS32) {\n
     *         // Equivalent to (Ext.os.is.iOS && Ext.os.version.equals(3.2))\n
     *     }\n
     *\n
     * Note that only {@link Ext.Version#getMajor major component} and {@link Ext.Version#getShortVersion simplified}\n
     * value of the version are available via direct property checking. Supported values are:\n
     *\n
     * - iOS\n
     * - iPad\n
     * - iPhone\n
     * - iPhone5 (also true for 4in iPods).\n
     * - iPod\n
     * - Android\n
     * - WebOS\n
     * - BlackBerry\n
     * - Bada\n
     * - MacOS\n
     * - Windows\n
     * - Linux\n
     * - Other\n
     * @param {String} value The OS name to check.\n
     * @return {Boolean}\n
     */\n
    is: Ext.emptyFn,\n
\n
    /**\n
     * @property {String} [name=null]\n
     * @readonly\n
     * The full name of the current operating system. Possible values are:\n
     *\n
     * - iOS\n
     * - Android\n
     * - WebOS\n
     * - BlackBerry,\n
     * - MacOS\n
     * - Windows\n
     * - Linux\n
     * - Other\n
     */\n
    name: null,\n
\n
    /**\n
     * @property {Ext.Version} [version=null]\n
     * Refer to {@link Ext.Version}\n
     * @readonly\n
     */\n
    version: null,\n
\n
    setFlag: function(name, value) {\n
        if (typeof value == \'undefined\') {\n
            value = true;\n
        }\n
\n
        this.is[name] = value;\n
        this.is[name.toLowerCase()] = value;\n
\n
        return this;\n
    },\n
\n
    constructor: function(userAgent, platform) {\n
        var statics = this.statics(),\n
            names = statics.names,\n
            prefixes = statics.prefixes,\n
            name,\n
            version = \'\',\n
            i, prefix, match, item, is;\n
\n
        is = this.is = function(name) {\n
            return this.is[name] === true;\n
        };\n
\n
        for (i in prefixes) {\n
            if (prefixes.hasOwnProperty(i)) {\n
                prefix = prefixes[i];\n
\n
                match = userAgent.match(new RegExp(\'(?:\'+prefix+\')([^\\\\s;]+)\'));\n
\n
                if (match) {\n
                    name = names[i];\n
\n
                    // This is here because some HTC android devices show an OSX Snow Leopard userAgent by default.\n
                    // And the Kindle Fire doesn\'t have any indicator of Android as the OS in its User Agent\n
                    if (match[1] && (match[1] == "HTC_" || match[1] == "Silk/")) {\n
                        version = new Ext.Version("2.3");\n
                    } else {\n
                        version = new Ext.Version(match[match.length - 1]);\n
                    }\n
\n
                    break;\n
                }\n
            }\n
        }\n
\n
        if (!name) {\n
            name = names[(userAgent.toLowerCase().match(/mac|win|linux/) || [\'other\'])[0]];\n
            version = new Ext.Version(\'\');\n
        }\n
\n
        this.name = name;\n
        this.version = version;\n
\n
        if (platform) {\n
            this.setFlag(platform.replace(/ simulator$/i, \'\'));\n
        }\n
\n
        this.setFlag(name);\n
\n
        if (version) {\n
            this.setFlag(name + (version.getMajor() || \'\'));\n
            this.setFlag(name + version.getShortVersion());\n
        }\n
\n
        for (i in names) {\n
            if (names.hasOwnProperty(i)) {\n
                item = names[i];\n
\n
                if (!is.hasOwnProperty(name)) {\n
                    this.setFlag(item, (name === item));\n
                }\n
            }\n
        }\n
\n
        // Detect if the device is the iPhone 5.\n
        if (this.name == "iOS" && window.screen.height == 568) {\n
            this.setFlag(\'iPhone5\');\n
        }\n
\n
        return this;\n
    }\n
\n
}, function() {\n
\n
    var navigation = Ext.global.navigator,\n
        userAgent = navigation.userAgent,\n
        osEnv, osName, deviceType;\n
\n
\n
    /**\n
     * @class Ext.os\n
     * @extends Ext.env.OS\n
     * @singleton\n
     * Provides useful information about the current operating system environment.\n
     *\n
     * Example:\n
     *\n
     *     if (Ext.os.is.Windows) {\n
     *         // Windows specific code here\n
     *     }\n
     *\n
     *     if (Ext.os.is.iOS) {\n
     *         // iPad, iPod, iPhone, etc.\n
     *     }\n
     *\n
     *     console.log("Version " + Ext.os.version);\n
     *\n
     * For a full list of supported values, refer to the {@link #is} property/method.\n
     *\n
     * @aside guide environment_package\n
     */\n
    Ext.os = osEnv = new this(userAgent, navigation.platform);\n
\n
    osName = osEnv.name;\n
\n
    var search = window.location.search.match(/deviceType=(Tablet|Phone)/),\n
        nativeDeviceType = window.deviceType;\n
\n
    // Override deviceType by adding a get variable of deviceType. NEEDED FOR DOCS APP.\n
    // E.g: example/kitchen-sink.html?deviceType=Phone\n
    if (search && search[1]) {\n
        deviceType = search[1];\n
    }\n
    else if (nativeDeviceType === \'iPhone\') {\n
        deviceType = \'Phone\';\n
    }\n
    else if (nativeDeviceType === \'iPad\') {\n
        deviceType = \'Tablet\';\n
    }\n
    else {\n
        if (!osEnv.is.Android && !osEnv.is.iOS && /Windows|Linux|MacOS/.test(osName)) {\n
            deviceType = \'Desktop\';\n
\n
            // always set it to false when you are on a desktop\n
            Ext.browser.is.WebView = false;\n
        }\n
        else if (osEnv.is.iPad || osEnv.is.Android3 || (osEnv.is.Android4 && userAgent.search(/mobile/i) == -1)) {\n
            deviceType = \'Tablet\';\n
        }\n
        else {\n
            deviceType = \'Phone\';\n
        }\n
    }\n
\n
    /**\n
     * @property {String} deviceType\n
     * The generic type of the current device.\n
     *\n
     * Possible values:\n
     *\n
     * - Phone\n
     * - Tablet\n
     * - Desktop\n
     *\n
     * For testing purposes the deviceType can be overridden by adding\n
     * a deviceType parameter to the URL of the page, like so:\n
     *\n
     *     http://localhost/mypage.html?deviceType=Tablet\n
     *\n
     */\n
    osEnv.setFlag(deviceType, true);\n
    osEnv.deviceType = deviceType;\n
\n
\n
    /**\n
     * @class Ext.is\n
     * Used to detect if the current browser supports a certain feature, and the type of the current browser.\n
     * @deprecated 2.0.0\n
     * Please refer to the {@link Ext.browser}, {@link Ext.os} and {@link Ext.feature} classes instead.\n
     */\n
});\n
\n
//@tag dom,core\n
\n
/**\n
 * Provides information about browser.\n
 * \n
 * Should not be manually instantiated unless for unit-testing.\n
 * Access the global instance stored in {@link Ext.browser} instead.\n
 * @private\n
 */\n
Ext.define(\'Ext.env.Feature\', {\n
\n
    requires: [\'Ext.env.Browser\', \'Ext.env.OS\'],\n
\n
    constructor: function() {\n
        this.testElements = {};\n
\n
        this.has = function(name) {\n
            return !!this.has[name];\n
        };\n
\n
        return this;\n
    },\n
\n
    getTestElement: function(tag, createNew) {\n
        if (tag === undefined) {\n
            tag = \'div\';\n
        }\n
        else if (typeof tag !== \'string\') {\n
            return tag;\n
        }\n
\n
        if (createNew) {\n
            return document.createElement(tag);\n
        }\n
\n
        if (!this.testElements[tag]) {\n
            this.testElements[tag] = document.createElement(tag);\n
        }\n
\n
        return this.testElements[tag];\n
    },\n
\n
    isStyleSupported: function(name, tag) {\n
        var elementStyle = this.getTestElement(tag).style,\n
            cName = Ext.String.capitalize(name);\n
\n
        if (typeof elementStyle[name] !== \'undefined\'\n
            || typeof elementStyle[Ext.browser.getStylePrefix(name) + cName] !== \'undefined\') {\n
            return true;\n
        }\n
\n
        return false;\n
    },\n
\n
    isEventSupported: function(name, tag) {\n
        if (tag === undefined) {\n
            tag = window;\n
        }\n
\n
        var element = this.getTestElement(tag),\n
            eventName = \'on\' + name.toLowerCase(),\n
            isSupported = (eventName in element);\n
\n
        if (!isSupported) {\n
            if (element.setAttribute && element.removeAttribute) {\n
                element.setAttribute(eventName, \'\');\n
                isSupported = typeof element[eventName] === \'function\';\n
\n
                if (typeof element[eventName] !== \'undefined\') {\n
                    element[eventName] = undefined;\n
                }\n
\n
                element.removeAttribute(eventName);\n
            }\n
        }\n
\n
        return isSupported;\n
    },\n
\n
    getSupportedPropertyName: function(object, name) {\n
        var vendorName = Ext.browser.getVendorProperyName(name);\n
\n
        if (vendorName in object) {\n
            return vendorName;\n
        }\n
        else if (name in object) {\n
            return name;\n
        }\n
\n
        return null;\n
    },\n
\n
    registerTest: Ext.Function.flexSetter(function(name, fn) {\n
        this.has[name] = fn.call(this);\n
\n
        return this;\n
    })\n
\n
}, function() {\n
\n
    /**\n
     * @class Ext.feature\n
     * @extend Ext.env.Feature\n
     * @singleton\n
     *\n
     * A simple class to verify if a browser feature exists or not on the current device.\n
     *\n
     *     if (Ext.feature.has.Canvas) {\n
     *         // do some cool things with canvas here\n
     *     }\n
     *\n
     * See the {@link #has} property/method for details of the features that can be detected.\n
     * \n
     * @aside guide environment_package\n
     */\n
    Ext.feature = new this;\n
\n
    var has = Ext.feature.has;\n
\n
    /**\n
     * @method has\n
     * @member Ext.feature\n
     * Verifies if a browser feature exists or not on the current device.\n
     * \n
     * A "hybrid" property, can be either accessed as a method call, i.e:\n
     *\n
     *     if (Ext.feature.has(\'Canvas\')) {\n
     *         // ...\n
     *     }\n
     *\n
     * or as an object with boolean properties, i.e:\n
     *\n
     *     if (Ext.feature.has.Canvas) {\n
     *         // ...\n
     *     }\n
     * \n
     * Possible properties/parameter values:\n
     *\n
     * - Canvas\n
     * - Svg\n
     * - Vml\n
     * - Touch - supports touch events (`touchstart`).\n
     * - Orientation - supports different orientations.\n
     * - OrientationChange - supports the `orientationchange` event.\n
     * - DeviceMotion - supports the `devicemotion` event.\n
     * - Geolocation\n
     * - SqlDatabase\n
     * - WebSockets\n
     * - Range - supports [DOM document fragments.][1]\n
     * - CreateContextualFragment - supports HTML fragment parsing using [range.createContextualFragment()][2].\n
     * - History - supports history management with [history.pushState()][3].\n
     * - CssTransforms\n
     * - Css3dTransforms\n
     * - CssAnimations\n
     * - CssTransitions\n
     * - Audio - supports the `<audio>` tag.\n
     * - Video - supports the `<video>` tag.\n
     * - ClassList - supports the HTML5 classList API.\n
     * - LocalStorage - LocalStorage is supported and can be written to.\n
     * \n
     * [1]: https://developer.mozilla.org/en/DOM/range\n
     * [2]: https://developer.mozilla.org/en/DOM/range.createContextualFragment\n
     * [3]: https://developer.mozilla.org/en/DOM/Manipulating_the_browser_history#The_pushState().C2.A0method\n
     *\n
     * @param {String} value The feature name to check.\n
     * @return {Boolean}\n
     */\n
    Ext.feature.registerTest({\n
        Canvas: function() {\n
            var element = this.getTestElement(\'canvas\');\n
            return !!(element && element.getContext && element.getContext(\'2d\'));\n
        },\n
\n
        Svg: function() {\n
            var doc = document;\n
\n
            return !!(doc.createElementNS && !!doc.createElementNS("http:/" + "/www.w3.org/2000/svg", "svg").createSVGRect);\n
        },\n
\n
        Vml: function() {\n
            var element = this.getTestElement(),\n
                ret = false;\n
\n
            element.innerHTML = "<!--[if vml]><br><![endif]-->";\n
            ret = (element.childNodes.length === 1);\n
            element.innerHTML = "";\n
\n
            return ret;\n
        },\n
\n
        Touch: function() {\n
            return this.isEventSupported(\'touchstart\') && !(Ext.os && Ext.os.name.match(/Windows|MacOS|Linux/) && !Ext.os.is.BlackBerry6);\n
        },\n
\n
        Orientation: function() {\n
            return (\'orientation\' in window) && this.isEventSupported(\'orientationchange\');\n
        },\n
\n
        OrientationChange: function() {\n
            return this.isEventSupported(\'orientationchange\');\n
        },\n
\n
        DeviceMotion: function() {\n
            return this.isEventSupported(\'devicemotion\');\n
        },\n
\n
        Geolocation: function() {\n
            return \'geolocation\' in window.navigator;\n
        },\n
\n
        SqlDatabase: function() {\n
            return \'openDatabase\' in window;\n
        },\n
\n
        WebSockets: function() {\n
            return \'WebSocket\' in window;\n
        },\n
\n
        Range: function() {\n
            return !!document.createRange;\n
        },\n
\n
        CreateContextualFragment: function() {\n
            var range = !!document.createRange ? document.createRange() : false;\n
            return range && !!range.createContextualFragment;\n
        },\n
\n
        History: function() {\n
            return (\'history\' in window && \'pushState\' in window.history);\n
        },\n
\n
        CssTransforms: function() {\n
            return this.isStyleSupported(\'transform\');\n
        },\n
\n
        Css3dTransforms: function() {\n
            // See https://sencha.jira.com/browse/TOUCH-1544\n
            return this.has(\'CssTransforms\') && this.isStyleSupported(\'perspective\') && !Ext.os.is.Android2;\n
        },\n
\n
        CssAnimations: function() {\n
            return this.isStyleSupported(\'animationName\');\n
        },\n
\n
        CssTransitions: function() {\n
            return this.isStyleSupported(\'transitionProperty\');\n
        },\n
\n
        Audio: function() {\n
            return !!this.getTestElement(\'audio\').canPlayType;\n
        },\n
\n
        Video: function() {\n
            return !!this.getTestElement(\'video\').canPlayType;\n
        },\n
\n
        ClassList: function() {\n
            return "classList" in this.getTestElement();\n
        },\n
\n
        LocalStorage : function() {\n
            var supported = false;\n
\n
            try {\n
                if (\'localStorage\' in window && window[\'localStorage\'] !== null) {\n
                    //this should throw an error in private browsing mode in iOS\n
                    localStorage.setItem(\'sencha-localstorage-test\', \'test success\');\n
                    //clean up if setItem worked\n
                    localStorage.removeItem(\'sencha-localstorage-test\');\n
                    supported = true;\n
                }\n
            } catch ( e ) {}\n
\n
            return supported;\n
        }\n
    });\n
\n
});\n
\n
//@tag dom,core\n
//@define Ext.DomQuery\n
//@define Ext.core.DomQuery\n
//@require Ext.env.Feature\n
\n
/**\n
 * @class Ext.DomQuery\n
 * @alternateClassName Ext.dom.Query\n
 *\n
 * Provides functionality to select elements on the page based on a CSS selector. Delegates to\n
 * document.querySelectorAll. More information can be found at\n
 * [http://www.w3.org/TR/css3-selectors/](http://www.w3.org/TR/css3-selectors/)\n
 *\n
 * All selectors, attribute filters and pseudos below can be combined infinitely in any order. For example\n
 * `div.foo:nth-child(odd)[@foo=bar].bar:first` would be a perfectly valid selector.\n
 *\n
 * ## Element Selectors:\n
 *\n
 * * \\* any element\n
 * * E an element with the tag E\n
 * * E F All descendant elements of E that have the tag F\n
 * * E > F or E/F all direct children elements of E that have the tag F\n
 * * E + F all elements with the tag F that are immediately preceded by an element with the tag E\n
 * * E ~ F all elements with the tag F that are preceded by a sibling element with the tag E\n
 *\n
 * ## Attribute Selectors:\n
 *\n
 * The use of @ and quotes are optional. For example, div[@foo=\'bar\'] is also a valid attribute selector.\n
 *\n
 * * E[foo] has an attribute "foo"\n
 * * E[foo=bar] has an attribute "foo" that equals "bar"\n
 * * E[foo^=bar] has an attribute "foo" that starts with "bar"\n
 * * E[foo$=bar] has an attribute "foo" that ends with "bar"\n
 * * E[foo*=bar] has an attribute "foo" that contains the substring "bar"\n
 * * E[foo%=2] has an attribute "foo" that is evenly divisible by 2\n
 * * E[foo!=bar] has an attribute "foo" that does not equal "bar"\n
 *\n
 * ## Pseudo Classes:\n
 *\n
 * * E:first-child E is the first child of its parent\n
 * * E:last-child E is the last child of its parent\n
 * * E:nth-child(n) E is the nth child of its parent (1 based as per the spec)\n
 * * E:nth-child(odd) E is an odd child of its parent\n
 * * E:nth-child(even) E is an even child of its parent\n
 * * E:only-child E is the only child of its parent\n
 * * E:checked E is an element that is has a checked attribute that is true (e.g. a radio or checkbox)\n
 * * E:first the first E in the resultset\n
 * * E:last the last E in the resultset\n
 * * E:nth(n) the nth E in the resultset (1 based)\n
 * * E:odd shortcut for :nth-child(odd)\n
 * * E:even shortcut for :nth-child(even)\n
 * * E:not(S) an E element that does not match simple selector S\n
 * * E:has(S) an E element that has a descendant that matches simple selector S\n
 * * E:next(S) an E element whose next sibling matches simple selector S\n
 * * E:prev(S) an E element whose previous sibling matches simple selector S\n
 * * E:any(S1|S2|S2) an E element which matches any of the simple selectors S1, S2 or S3//\\\\\n
 *\n
 * ## CSS Value Selectors:\n
 *\n
 * * E{display=none} CSS value "display" that equals "none"\n
 * * E{display^=none} CSS value "display" that starts with "none"\n
 * * E{display$=none} CSS value "display" that ends with "none"\n
 * * E{display*=none} CSS value "display" that contains the substring "none"\n
 * * E{display%=2} CSS value "display" that is evenly divisible by 2\n
 * * E{display!=none} CSS value "display" that does not equal "none"\n
 */\n
Ext.define(\'Ext.dom.Query\', {\n
    /**\n
     * Selects a group of elements.\n
     * @param {String} selector The selector/xpath query (can be a comma separated list of selectors)\n
     * @param {HTMLElement/String} [root] The start of the query (defaults to document).\n
     * @return {HTMLElement[]} An Array of DOM elements which match the selector. If there are\n
     * no matches, and empty Array is returned.\n
     */\n
    select: function(q, root) {\n
        var results = [],\n
            nodes,\n
            i,\n
            j,\n
            qlen,\n
            nlen;\n
\n
        root = root || document;\n
\n
        if (typeof root == \'string\') {\n
            root = document.getElementById(root);\n
        }\n
\n
        q = q.split(",");\n
\n
        for (i = 0,qlen = q.length; i < qlen; i++) {\n
            if (typeof q[i] == \'string\') {\n
\n
                //support for node attribute selection\n
                if (q[i][0] == \'@\') {\n
                    nodes = root.getAttributeNode(q[i].substring(1));\n
                    results.push(nodes);\n
                }\n
                else {\n
                    nodes = root.querySelectorAll(q[i]);\n
\n
                    for (j = 0,nlen = nodes.length; j < nlen; j++) {\n
                        results.push(nodes[j]);\n
                    }\n
                }\n
            }\n
        }\n
\n
        return results;\n
    },\n
\n
    /**\n
     * Selects a single element.\n
     * @param {String} selector The selector/xpath query\n
     * @param {HTMLElement/String} [root] The start of the query (defaults to document).\n
     * @return {HTMLElement} The DOM element which matched the selector.\n
     */\n
    selectNode: function(q, root) {\n
        return this.select(q, root)[0];\n
    },\n
\n
    /**\n
     * Returns true if the passed element(s) match the passed simple selector (e.g. div.some-class or span:first-child)\n
     * @param {String/HTMLElement/Array} el An element id, element or array of elements\n
     * @param {String} selector The simple selector to test\n
     * @return {Boolean}\n
     */\n
    is: function(el, q) {\n
        if (typeof el == "string") {\n
            el = document.getElementById(el);\n
        }\n
        return this.select(q).indexOf(el) !== -1;\n
    },\n
\n
    isXml: function(el) {\n
        var docEl = (el ? el.ownerDocument || el : 0).documentElement;\n
        return docEl ? docEl.nodeName !== "HTML" : false;\n
    }\n
\n
}, function() {\n
    Ext.ns(\'Ext.core\');\n
    Ext.core.DomQuery = Ext.DomQuery = new this();\n
    Ext.query = Ext.Function.alias(Ext.DomQuery, \'select\');\n
});\n
\n
//@tag dom,core\n
//@define Ext.DomHelper\n
//@require Ext.dom.Query\n
\n
/**\n
 * @class Ext.DomHelper\n
 * @alternateClassName Ext.dom.Helper\n
 *\n
 * The DomHelper class provides a layer of abstraction from DOM and transparently supports creating elements via DOM or\n
 * using HTML fragments. It also has the ability to create HTML fragment templates from your DOM building code.\n
 *\n
 * ## DomHelper element specification object\n
 *\n
 * A specification object is used when creating elements. Attributes of this object are assumed to be element\n
 * attributes, except for 4 special attributes:\n
 *\n
 * * **tag**: The tag name of the element\n
 * * **children (or cn)**: An array of the same kind of element definition objects to be created and appended. These\n
 * can be nested as deep as you want.\n
 * * **cls**: The class attribute of the element. This will end up being either the "class" attribute on a HTML\n
 * fragment or className for a DOM node, depending on whether DomHelper is using fragments or DOM.\n
 * * **html**: The innerHTML for the element\n
 *\n
 * ## Insertion methods\n
 *\n
 * Commonly used insertion methods:\n
 *\n
 * * {@link #append}\n
 * * {@link #insertBefore}\n
 * * {@link #insertAfter}\n
 * * {@link #overwrite}\n
 * * {@link #insertHtml}\n
 *\n
 * ## Example\n
 *\n
 * This is an example, where an unordered list with 3 children items is appended to an existing element with id\n
 * \'my-div\':\n
 *\n
 *     var dh = Ext.DomHelper; // create shorthand alias\n
 *     // specification object\n
 *     var spec = {\n
 *         id: \'my-ul\',\n
 *         tag: \'ul\',\n
 *         cls: \'my-list\',\n
 *         // append children after creating\n
 *         children: [     // may also specify \'cn\' instead of \'children\'\n
 *             {tag: \'li\', id: \'item0\', html: \'List Item 0\'},\n
 *             {tag: \'li\', id: \'item1\', html: \'List Item 1\'},\n
 *             {tag: \'li\', id: \'item2\', html: \'List Item 2\'}\n
 *         ]\n
 *     };\n
 *     var list = dh.append(\n
 *         \'my-div\', // the context element \'my-div\' can either be the id or the actual node\n
 *         spec      // the specification object\n
 *     );\n
 *\n
 * Element creation specification parameters in this class may also be passed as an Array of specification objects.\n
 * This can be used to insert multiple sibling nodes into an existing container very efficiently. For example, to add\n
 * more list items to the example above:\n
 *\n
 *     dh.append(\'my-ul\', [\n
 *         {tag: \'li\', id: \'item3\', html: \'List Item 3\'},\n
 *         {tag: \'li\', id: \'item4\', html: \'List Item 4\'}\n
 *     ]);\n
 *\n
 * ## Templating\n
 *\n
 * The real power is in the built-in templating. Instead of creating or appending any elements, createTemplate returns\n
 * a Template object which can be used over and over to insert new elements. Revisiting the example above, we could\n
 * utilize templating this time:\n
 *\n
 *     // create the node\n
 *     var list = dh.append(\'my-div\', {tag: \'ul\', cls: \'my-list\'});\n
 *     // get template\n
 *     var tpl = dh.createTemplate({tag: \'li\', id: \'item{0}\', html: \'List Item {0}\'});\n
 *\n
 *     for(var i = 0; i < 5; i++){\n
 *         tpl.append(list, i); // use template to append to the actual node\n
 *     }\n
 *\n
 * An example using a template:\n
 *\n
 *     var html = \'"{0}" href="{1}" class="nav">{2}\';\n
 *\n
 *     var tpl = new Ext.DomHelper.createTemplate(html);\n
 *     tpl.append(\'blog-roll\', [\'link1\', \'http://www.tommymaintz.com/\', "Tommy\'s Site"]);\n
 *     tpl.append(\'blog-roll\', [\'link2\', \'http://www.avins.org/\', "Jamie\'s Site"]);\n
 *\n
 * The same example using named parameters:\n
 *\n
 *     var html = \'"{id}" href="{url}" class="nav">{text}\';\n
 *\n
 *     var tpl = new Ext.DomHelper.createTemplate(html);\n
 *     tpl.append(\'blog-roll\', {\n
 *         id: \'link1\',\n
 *         url: \'http://www.tommymaintz.com/\',\n
 *         text: "Tommy\'s Site"\n
 *     });\n
 *     tpl.append(\'blog-roll\', {\n
 *         id: \'link2\',\n
 *         url: \'http://www.avins.org/\',\n
 *         text: "Jamie\'s Site"\n
 *     });\n
 *\n
 * ## Compiling Templates\n
 *\n
 * Templates are applied using regular expressions. The performance is great, but if you are adding a bunch of DOM\n
 * elements using the same template, you can increase performance even further by "compiling" the template. The way\n
 * "compile()" works is the template is parsed and broken up at the different variable points and a dynamic function is\n
 * created and eval\'ed. The generated function performs string concatenation of these parts and the passed variables\n
 * instead of using regular expressions.\n
 *\n
 *     var html = \'"{id}" href="{url}" class="nav">{text}\';\n
 *\n
 *     var tpl = new Ext.DomHelper.createTemplate(html);\n
 *     tpl.compile();\n
 *\n
 *     // ... use template like normal\n
 *\n
 * ## Performance Boost\n
 *\n
 * DomHelper will transparently create HTML fragments when it can. Using HTML fragments instead of DOM can\n
 * significantly boost performance.\n
 *\n
 * Element creation specification parameters may also be strings. If useDom is false, then the string is used as\n
 * innerHTML. If useDom is true, a string specification results in the creation of a text node. Usage:\n
 *\n
 *     Ext.DomHelper.useDom = true; // force it to use DOM; reduces performance\n
 *\n
 */\n
Ext.define(\'Ext.dom.Helper\', {\n
    emptyTags : /^(?:br|frame|hr|img|input|link|meta|range|spacer|wbr|area|param|col)$/i,\n
    confRe : /tag|children|cn|html|tpl|tplData$/i,\n
    endRe : /end/i,\n
\n
    attribXlat: { cls : \'class\', htmlFor : \'for\' },\n
\n
    closeTags: {},\n
\n
    decamelizeName : function () {\n
        var camelCaseRe = /([a-z])([A-Z])/g,\n
            cache = {};\n
\n
        function decamel (match, p1, p2) {\n
            return p1 + \'-\' + p2.toLowerCase();\n
        }\n
\n
        return function (s) {\n
            return cache[s] || (cache[s] = s.replace(camelCaseRe, decamel));\n
        };\n
    }(),\n
\n
    generateMarkup: function(spec, buffer) {\n
        var me = this,\n
            attr, val, tag, i, closeTags;\n
\n
        if (typeof spec == "string") {\n
            buffer.push(spec);\n
        } else if (Ext.isArray(spec)) {\n
            for (i = 0; i < spec.length; i++) {\n
                if (spec[i]) {\n
                    me.generateMarkup(spec[i], buffer);\n
                }\n
            }\n
        } else {\n
            tag = spec.tag || \'div\';\n
            buffer.push(\'<\', tag);\n
\n
            for (attr in spec) {\n
                if (spec.hasOwnProperty(attr)) {\n
                    val = spec[attr];\n
                    if (!me.confRe.test(attr)) {\n
                        if (typeof val == "object") {\n
                            buffer.push(\' \', attr, \'="\');\n
                            me.generateStyles(val, buffer).push(\'"\');\n
                        } else {\n
                            buffer.push(\' \', me.attribXlat[attr] || attr, \'="\', val, \'"\');\n
                        }\n
                    }\n
                }\n
            }\n
\n
            // Now either just close the tag or try to add children and close the tag.\n
            if (me.emptyTags.test(tag)) {\n
                buffer.push(\'/>\');\n
            } else {\n
                buffer.push(\'>\');\n
\n
                // Apply the tpl html, and cn specifications\n
                if ((val = spec.tpl)) {\n
                    val.applyOut(spec.tplData, buffer);\n
                }\n
                if ((val = spec.html)) {\n
                    buffer.push(val);\n
                }\n
                if ((val = spec.cn || spec.children)) {\n
                    me.generateMarkup(val, buffer);\n
                }\n
\n
                // we generate a lot of close tags, so cache them rather than push 3 parts\n
                closeTags = me.closeTags;\n
                buffer.push(closeTags[tag] || (closeTags[tag] = \'</\' + tag + \'>\'));\n
            }\n
        }\n
\n
        return buffer;\n
    },\n
\n
    /**\n
     * Converts the styles from the given object to text. The styles are CSS style names\n
     * with their associated value.\n
     *\n
     * The basic form of this method returns a string:\n
     *\n
     *      var s = Ext.DomHelper.generateStyles({\n
     *          backgroundColor: \'red\'\n
     *      });\n
     *\n
     *      // s = \'background-color:red;\'\n
     *\n
     * Alternatively, this method can append to an output array.\n
     *\n
     *      var buf = [];\n
     *\n
     *      // ...\n
     *\n
     *      Ext.DomHelper.generateStyles({\n
     *          backgroundColor: \'red\'\n
     *      }, buf);\n
     *\n
     * In this case, the style text is pushed on to the array and the array is returned.\n
     *\n
     * @param {Object} styles The object describing the styles.\n
     * @param {String[]} [buffer] The output buffer.\n
     * @return {String/String[]} If buffer is passed, it is returned. Otherwise the style\n
     * string is returned.\n
     */\n
    generateStyles: function (styles, buffer) {\n
        var a = buffer || [],\n
            name;\n
\n
        for (name in styles) {\n
            if (styles.hasOwnProperty(name)) {\n
                a.push(this.decamelizeName(name), \':\', styles[name], \';\');\n
            }\n
        }\n
\n
        return buffer || a.join(\'\');\n
    },\n
\n
    /**\n
     * Returns the markup for the passed Element(s) config.\n
     * @param {Object} spec The DOM object spec (and children).\n
     * @return {String}\n
     */\n
    markup: function(spec) {\n
        if (typeof spec == "string") {\n
            return spec;\n
        }\n
\n
        var buf = this.generateMarkup(spec, []);\n
        return buf.join(\'\');\n
    },\n
\n
    /**\n
     * Applies a style specification to an element.\n
     * @param {String/HTMLElement} el The element to apply styles to\n
     * @param {String/Object/Function} styles A style specification string e.g. \'width:100px\', or object in the form {width:\'100px\'}, or\n
     * a function which returns such a specification.\n
     */\n
    applyStyles: function(el, styles) {\n
        Ext.fly(el).applyStyles(styles);\n
    },\n
\n
    /**\n
     * @private\n
     * Fix for browsers which no longer support createContextualFragment\n
     */\n
    createContextualFragment: function(html){\n
        var div = document.createElement("div"),\n
            fragment = document.createDocumentFragment(),\n
            i = 0,\n
            length, childNodes;\n
\n
        div.innerHTML = html;\n
        childNodes = div.childNodes;\n
        length = childNodes.length;\n
\n
        for (; i < length; i++) {\n
            fragment.appendChild(childNodes[i].cloneNode(true));\n
        }\n
\n
        return fragment;\n
    },\n
\n
    /**\n
     * Inserts an HTML fragment into the DOM.\n
     * @param {String} where Where to insert the html in relation to el - beforeBegin, afterBegin, beforeEnd, afterEnd.\n
     *\n
     * For example take the following HTML: `<div>Contents</div>`\n
     *\n
     * Using different `where` values inserts element to the following places:\n
     *\n
     * - beforeBegin: `<HERE><div>Contents</div>`\n
     * - afterBegin: `<div><HERE>Contents</

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAc=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="7" aka="AAAAAAAAAAc=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

div>`\n
     * - beforeEnd: `<div>Contents<HERE></div>`\n
     * - afterEnd: `<div>Contents</div><HERE>`\n
     *\n
     * @param {HTMLElement/TextNode} el The context element\n
     * @param {String} html The HTML fragment\n
     * @return {HTMLElement} The new node\n
     */\n
    insertHtml: function(where, el, html) {\n
        var setStart, range, frag, rangeEl, isBeforeBegin, isAfterBegin;\n
\n
        where = where.toLowerCase();\n
\n
        if (Ext.isTextNode(el)) {\n
            if (where == \'afterbegin\' ) {\n
                where = \'beforebegin\';\n
            }\n
            else if (where == \'beforeend\') {\n
                where = \'afterend\';\n
            }\n
        }\n
\n
        isBeforeBegin = where == \'beforebegin\';\n
        isAfterBegin = where == \'afterbegin\';\n
\n
        range = Ext.feature.has.CreateContextualFragment ? el.ownerDocument.createRange() : undefined;\n
        setStart = \'setStart\' + (this.endRe.test(where) ? \'After\' : \'Before\');\n
\n
        if (isBeforeBegin || where == \'afterend\') {\n
            if (range) {\n
                range[setStart](el);\n
                frag = range.createContextualFragment(html);\n
            }\n
            else {\n
                frag = this.createContextualFragment(html);\n
            }\n
            el.parentNode.insertBefore(frag, isBeforeBegin ? el : el.nextSibling);\n
            return el[(isBeforeBegin ? \'previous\' : \'next\') + \'Sibling\'];\n
        }\n
        else {\n
            rangeEl = (isAfterBegin ? \'first\' : \'last\') + \'Child\';\n
            if (el.firstChild) {\n
                if (range) {\n
                    range[setStart](el[rangeEl]);\n
                    frag = range.createContextualFragment(html);\n
                } else {\n
                    frag = this.createContextualFragment(html);\n
                }\n
\n
                if (isAfterBegin) {\n
                    el.insertBefore(frag, el.firstChild);\n
                } else {\n
                    el.appendChild(frag);\n
                }\n
            } else {\n
                el.innerHTML = html;\n
            }\n
            return el[rangeEl];\n
        }\n
    },\n
\n
    /**\n
     * Creates new DOM element(s) and inserts them before el.\n
     * @param {String/HTMLElement/Ext.Element} el The context element\n
     * @param {Object/String} o The DOM object spec (and children) or raw HTML blob\n
     * @param {Boolean} [returnElement] true to return a Ext.Element\n
     * @return {HTMLElement/Ext.Element} The new node\n
     */\n
    insertBefore: function(el, o, returnElement) {\n
        return this.doInsert(el, o, returnElement, \'beforebegin\');\n
    },\n
\n
    /**\n
     * Creates new DOM element(s) and inserts them after el.\n
     * @param {String/HTMLElement/Ext.Element} el The context element\n
     * @param {Object} o The DOM object spec (and children)\n
     * @param {Boolean} [returnElement] true to return a Ext.Element\n
     * @return {HTMLElement/Ext.Element} The new node\n
     */\n
    insertAfter: function(el, o, returnElement) {\n
        return this.doInsert(el, o, returnElement, \'afterend\');\n
    },\n
\n
    /**\n
     * Creates new DOM element(s) and inserts them as the first child of el.\n
     * @param {String/HTMLElement/Ext.Element} el The context element\n
     * @param {Object/String} o The DOM object spec (and children) or raw HTML blob\n
     * @param {Boolean} [returnElement] true to return a Ext.Element\n
     * @return {HTMLElement/Ext.Element} The new node\n
     */\n
    insertFirst: function(el, o, returnElement) {\n
        return this.doInsert(el, o, returnElement, \'afterbegin\');\n
    },\n
\n
    /**\n
     * Creates new DOM element(s) and appends them to el.\n
     * @param {String/HTMLElement/Ext.Element} el The context element\n
     * @param {Object/String} o The DOM object spec (and children) or raw HTML blob\n
     * @param {Boolean} [returnElement] true to return a Ext.Element\n
     * @return {HTMLElement/Ext.Element} The new node\n
     */\n
    append: function(el, o, returnElement) {\n
        return this.doInsert(el, o, returnElement, \'beforeend\');\n
    },\n
\n
    /**\n
     * Creates new DOM element(s) and overwrites the contents of el with them.\n
     * @param {String/HTMLElement/Ext.Element} el The context element\n
     * @param {Object/String} o The DOM object spec (and children) or raw HTML blob\n
     * @param {Boolean} [returnElement] true to return a Ext.Element\n
     * @return {HTMLElement/Ext.Element} The new node\n
     */\n
    overwrite: function(el, o, returnElement) {\n
        el = Ext.getDom(el);\n
        el.innerHTML = this.markup(o);\n
        return returnElement ? Ext.get(el.firstChild) : el.firstChild;\n
    },\n
\n
    doInsert: function(el, o, returnElement, pos) {\n
        var newNode = this.insertHtml(pos, Ext.getDom(el), this.markup(o));\n
        return returnElement ? Ext.get(newNode, true) : newNode;\n
    },\n
\n
    /**\n
     * Creates a new Ext.Template from the DOM object spec.\n
     * @param {Object} o The DOM object spec (and children)\n
     * @return {Ext.Template} The new template\n
     */\n
    createTemplate: function(o) {\n
        var html = this.markup(o);\n
        return new Ext.Template(html);\n
    }\n
}, function() {\n
    Ext.ns(\'Ext.core\');\n
    Ext.core.DomHelper = Ext.DomHelper = new this;\n
});\n
\n
//@tag dom,core\n
//@require Ext.dom.Helper\n
\n
/**\n
 * An Identifiable mixin.\n
 * @private\n
 */\n
Ext.define(\'Ext.mixin.Identifiable\', {\n
    statics: {\n
        uniqueIds: {}\n
    },\n
\n
    isIdentifiable: true,\n
\n
    mixinId: \'identifiable\',\n
\n
    idCleanRegex: /\\.|[^\\w\\-]/g,\n
\n
    defaultIdPrefix: \'ext-\',\n
\n
    defaultIdSeparator: \'-\',\n
\n
    getOptimizedId: function() {\n
        return this.id;\n
    },\n
\n
    getUniqueId: function() {\n
        var id = this.id,\n
            prototype, separator, xtype, uniqueIds, prefix;\n
\n
        if (!id) {\n
            prototype = this.self.prototype;\n
            separator = this.defaultIdSeparator;\n
\n
            uniqueIds = Ext.mixin.Identifiable.uniqueIds;\n
\n
            if (!prototype.hasOwnProperty(\'identifiablePrefix\')) {\n
                xtype = this.xtype;\n
\n
                if (xtype) {\n
                    prefix = this.defaultIdPrefix + xtype + separator;\n
                }\n
                else {\n
                    prefix = prototype.$className.replace(this.idCleanRegex, separator).toLowerCase() + separator;\n
                }\n
\n
                prototype.identifiablePrefix = prefix;\n
            }\n
\n
            prefix = this.identifiablePrefix;\n
\n
            if (!uniqueIds.hasOwnProperty(prefix)) {\n
                uniqueIds[prefix] = 0;\n
            }\n
\n
            id = this.id = prefix + (++uniqueIds[prefix]);\n
        }\n
\n
        this.getUniqueId = this.getOptimizedId;\n
\n
        return id;\n
    },\n
\n
    setId: function(id) {\n
        this.id = id;\n
    },\n
\n
    /**\n
     * Retrieves the id of this component. Will autogenerate an id if one has not already been set.\n
     * @return {String} id\n
     */\n
    getId: function() {\n
        var id = this.id;\n
\n
        if (!id) {\n
            id = this.getUniqueId();\n
        }\n
\n
        this.getId = this.getOptimizedId;\n
\n
        return id;\n
    }\n
});\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element\n
\n
/**\n
 * Encapsulates a DOM element, adding simple DOM manipulation facilities, normalizing for browser differences.\n
 *\n
 * All instances of this class inherit the methods of Ext.Fx making visual effects easily available to all DOM elements.\n
 *\n
 * Note that the events documented in this class are not Ext events, they encapsulate browser events. To access the\n
 * underlying browser event, see {@link Ext.EventObject#browserEvent}. Some older browsers may not support the full range of\n
 * events. Which events are supported is beyond the control of Sencha Touch.\n
 *\n
 * ## Usage\n
 *\n
 *     // by id\n
 *     var el = Ext.get("my-div");\n
 *\n
 *     // by DOM element reference\n
 *     var el = Ext.get(myDivElement);\n
 *\n
 * ## Composite (Collections of) Elements\n
 *\n
 * For working with collections of Elements, see {@link Ext.CompositeElement}.\n
 *\n
 * @mixins Ext.mixin.Observable\n
 */\n
Ext.define(\'Ext.dom.Element\', {\n
    alternateClassName: \'Ext.Element\',\n
\n
    mixins: [\n
        \'Ext.mixin.Identifiable\'\n
    ],\n
\n
    requires: [\n
        \'Ext.dom.Query\',\n
        \'Ext.dom.Helper\'\n
    ],\n
\n
    observableType: \'element\',\n
\n
    xtype: \'element\',\n
\n
    statics: {\n
        CREATE_ATTRIBUTES: {\n
            style: \'style\',\n
            className: \'className\',\n
            cls: \'cls\',\n
            classList: \'classList\',\n
            text: \'text\',\n
            hidden: \'hidden\',\n
            html: \'html\',\n
            children: \'children\'\n
        },\n
\n
        create: function(attributes, domNode) {\n
            var ATTRIBUTES = this.CREATE_ATTRIBUTES,\n
                element, elementStyle, tag, value, name, i, ln;\n
\n
            if (!attributes) {\n
                attributes = {};\n
            }\n
\n
            if (attributes.isElement) {\n
                return attributes.dom;\n
            }\n
            else if (\'nodeType\' in attributes) {\n
                return attributes;\n
            }\n
\n
            if (typeof attributes == \'string\') {\n
                return document.createTextNode(attributes);\n
            }\n
\n
            tag = attributes.tag;\n
\n
            if (!tag) {\n
                tag = \'div\';\n
            }\n
            if (attributes.namespace) {\n
                element = document.createElementNS(attributes.namespace, tag);\n
            } else {\n
                element = document.createElement(tag);\n
            }\n
            elementStyle = element.style;\n
\n
            for (name in attributes) {\n
                if (name != \'tag\') {\n
                    value = attributes[name];\n
\n
                    switch (name) {\n
                        case ATTRIBUTES.style:\n
                                if (typeof value == \'string\') {\n
                                    element.setAttribute(name, value);\n
                                }\n
                                else {\n
                                    for (i in value) {\n
                                        if (value.hasOwnProperty(i)) {\n
                                            elementStyle[i] = value[i];\n
                                        }\n
                                    }\n
                                }\n
                            break;\n
\n
                        case ATTRIBUTES.className:\n
                        case ATTRIBUTES.cls:\n
                            element.className = value;\n
                            break;\n
\n
                        case ATTRIBUTES.classList:\n
                            element.className = value.join(\' \');\n
                            break;\n
\n
                        case ATTRIBUTES.text:\n
                            element.textContent = value;\n
                            break;\n
\n
                        case ATTRIBUTES.hidden:\n
                            if (value) {\n
                                element.style.display = \'none\';\n
                            }\n
                            break;\n
\n
                        case ATTRIBUTES.html:\n
                            element.innerHTML = value;\n
                            break;\n
\n
                        case ATTRIBUTES.children:\n
                            for (i = 0,ln = value.length; i < ln; i++) {\n
                                element.appendChild(this.create(value[i], true));\n
                            }\n
                            break;\n
\n
                        default:\n
                            element.setAttribute(name, value);\n
                    }\n
                }\n
            }\n
\n
            if (domNode) {\n
                return element;\n
            }\n
            else {\n
                return this.get(element);\n
            }\n
        },\n
\n
        documentElement: null,\n
\n
        cache: {},\n
\n
        /**\n
         * Retrieves Ext.dom.Element objects. {@link Ext#get} is alias for {@link Ext.dom.Element#get}.\n
         *\n
         * **This method does not retrieve {@link Ext.Element Element}s.** This method retrieves Ext.dom.Element\n
         * objects which encapsulate DOM elements. To retrieve a Element by its ID, use {@link Ext.ElementManager#get}.\n
         *\n
         * Uses simple caching to consistently return the same object. Automatically fixes if an object was recreated with\n
         * the same id via AJAX or DOM.\n
         *\n
         * @param {String/HTMLElement/Ext.Element} el The `id` of the node, a DOM Node or an existing Element.\n
         * @return {Ext.dom.Element} The Element object (or `null` if no matching element was found).\n
         * @static\n
         * @inheritable\n
         */\n
        get: function(element) {\n
            var cache = this.cache,\n
                instance, dom, id;\n
\n
            if (!element) {\n
                return null;\n
            }\n
\n
            if (typeof element == \'string\') {\n
                if (cache.hasOwnProperty(element)) {\n
                    return cache[element];\n
                }\n
\n
                if (!(dom = document.getElementById(element))) {\n
                    return null;\n
                }\n
\n
                cache[element] = instance = new this(dom);\n
\n
                return instance;\n
            }\n
\n
            if (\'tagName\' in element) { // dom element\n
                id = element.id;\n
\n
                if (cache.hasOwnProperty(id)) {\n
                    return cache[id];\n
                }\n
\n
                instance = new this(element);\n
                cache[instance.getId()] = instance;\n
\n
                return instance;\n
            }\n
\n
            if (element.isElement) {\n
                return element;\n
            }\n
\n
            if (element.isComposite) {\n
                return element;\n
            }\n
\n
            if (Ext.isArray(element)) {\n
                return this.select(element);\n
            }\n
\n
            if (element === document) {\n
                // create a bogus element object representing the document object\n
                if (!this.documentElement) {\n
                    this.documentElement = new this(document.documentElement);\n
                    this.documentElement.setId(\'ext-application\');\n
                }\n
\n
                return this.documentElement;\n
            }\n
\n
            return null;\n
        },\n
\n
        data: function(element, key, value) {\n
            var cache = Ext.cache,\n
                id, data;\n
\n
            element = this.get(element);\n
\n
            if (!element) {\n
                return null;\n
            }\n
\n
            id = element.id;\n
\n
            data = cache[id].data;\n
\n
            if (!data) {\n
                cache[id].data = data = {};\n
            }\n
\n
            if (arguments.length == 2) {\n
                return data[key];\n
            }\n
            else {\n
                return (data[key] = value);\n
            }\n
        }\n
    },\n
\n
    isElement: true,\n
\n
\n
    /**\n
     * @event painted\n
     * Fires whenever this Element actually becomes visible (painted) on the screen. This is useful when you need to\n
     * perform \'read\' operations on the DOM element, i.e: calculating natural sizes and positioning.\n
     *\n
     * __Note:__ This event is not available to be used with event delegation. Instead `painted` only fires if you explicitly\n
     * add at least one listener to it, for performance reasons.\n
     *\n
     * @param {Ext.Element} this The component instance.\n
     */\n
\n
    /**\n
     * @event resize\n
     * Important note: For the best performance on mobile devices, use this only when you absolutely need to monitor\n
     * a Element\'s size.\n
     *\n
     * __Note:__ This event is not available to be used with event delegation. Instead `resize` only fires if you explicitly\n
     * add at least one listener to it, for performance reasons.\n
     *\n
     * @param {Ext.Element} this The component instance.\n
     */\n
\n
    constructor: function(dom) {\n
        if (typeof dom == \'string\') {\n
            dom = document.getElementById(dom);\n
        }\n
\n
        if (!dom) {\n
            throw new Error("Invalid domNode reference or an id of an existing domNode: " + dom);\n
        }\n
\n
        /**\n
         * The DOM element\n
         * @property dom\n
         * @type HTMLElement\n
         */\n
        this.dom = dom;\n
\n
        this.getUniqueId();\n
    },\n
\n
    attach: function (dom) {\n
        this.dom = dom;\n
        this.id = dom.id;\n
        return this;\n
    },\n
\n
    getUniqueId: function() {\n
        var id = this.id,\n
            dom;\n
\n
        if (!id) {\n
            dom = this.dom;\n
\n
            if (dom.id.length > 0) {\n
                this.id = id = dom.id;\n
            }\n
            else {\n
                dom.id = id = this.mixins.identifiable.getUniqueId.call(this);\n
            }\n
\n
            this.self.cache[id] = this;\n
        }\n
\n
        return id;\n
    },\n
\n
    setId: function(id) {\n
        var currentId = this.id,\n
            cache = this.self.cache;\n
\n
        if (currentId) {\n
            delete cache[currentId];\n
        }\n
\n
        this.dom.id = id;\n
\n
        /**\n
         * The DOM element ID\n
         * @property id\n
         * @type String\n
         */\n
        this.id = id;\n
\n
        cache[id] = this;\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Sets the `innerHTML` of this element.\n
     * @param {String} html The new HTML.\n
     */\n
    setHtml: function(html) {\n
        this.dom.innerHTML = html;\n
    },\n
\n
    /**\n
     * Returns the `innerHTML` of an element.\n
     * @return {String}\n
     */\n
    getHtml: function() {\n
        return this.dom.innerHTML;\n
    },\n
\n
    setText: function(text) {\n
        this.dom.textContent = text;\n
    },\n
\n
    redraw: function() {\n
        var dom = this.dom,\n
            domStyle = dom.style;\n
\n
        domStyle.display = \'none\';\n
        dom.offsetHeight;\n
        domStyle.display = \'\';\n
    },\n
\n
    isPainted: function() {\n
        var dom = this.dom;\n
        return Boolean(dom && dom.offsetParent);\n
    },\n
\n
    /**\n
     * Sets the passed attributes as attributes of this element (a style attribute can be a string, object or function).\n
     * @param {Object} attributes The object with the attributes.\n
     * @param {Boolean} [useSet=true] `false` to override the default `setAttribute` to use expandos.\n
     * @return {Ext.dom.Element} this\n
     */\n
    set: function(attributes, useSet) {\n
        var dom = this.dom,\n
            attribute, value;\n
\n
        for (attribute in attributes) {\n
            if (attributes.hasOwnProperty(attribute)) {\n
                value = attributes[attribute];\n
\n
                if (attribute == \'style\') {\n
                    this.applyStyles(value);\n
                }\n
                else if (attribute == \'cls\') {\n
                    dom.className = value;\n
                }\n
                else if (useSet !== false) {\n
                    if (value === undefined) {\n
                        dom.removeAttribute(attribute);\n
                    } else {\n
                        dom.setAttribute(attribute, value);\n
                    }\n
                }\n
                else {\n
                    dom[attribute] = value;\n
                }\n
            }\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Returns `true` if this element matches the passed simple selector (e.g. \'div.some-class\' or \'span:first-child\').\n
     * @param {String} selector The simple selector to test.\n
     * @return {Boolean} `true` if this element matches the selector, else `false`.\n
     */\n
    is: function(selector) {\n
        return Ext.DomQuery.is(this.dom, selector);\n
    },\n
\n
    /**\n
     * Returns the value of the `value` attribute.\n
     * @param {Boolean} asNumber `true` to parse the value as a number.\n
     * @return {String/Number}\n
     */\n
    getValue: function(asNumber) {\n
        var value = this.dom.value;\n
\n
        return asNumber ? parseInt(value, 10) : value;\n
    },\n
\n
    /**\n
     * Returns the value of an attribute from the element\'s underlying DOM node.\n
     * @param {String} name The attribute name.\n
     * @param {String} [namespace] The namespace in which to look for the attribute.\n
     * @return {String} The attribute value.\n
     */\n
    getAttribute: function(name, namespace) {\n
        var dom = this.dom;\n
\n
        return dom.getAttributeNS(namespace, name) || dom.getAttribute(namespace + ":" + name)\n
               || dom.getAttribute(name) || dom[name];\n
    },\n
\n
    setSizeState: function(state) {\n
        var classes = [\'x-sized\', \'x-unsized\', \'x-stretched\'],\n
            states = [true, false, null],\n
            index = states.indexOf(state),\n
            addedClass;\n
\n
        if (index !== -1) {\n
            addedClass = classes[index];\n
            classes.splice(index, 1);\n
            this.addCls(addedClass);\n
        }\n
\n
        this.removeCls(classes);\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Removes this element\'s DOM reference. Note that event and cache removal is handled at {@link Ext#removeNode}\n
     */\n
    destroy: function() {\n
        this.isDestroyed = true;\n
\n
        var cache = Ext.Element.cache,\n
            dom = this.dom;\n
\n
        if (dom && dom.parentNode && dom.tagName != \'BODY\') {\n
            dom.parentNode.removeChild(dom);\n
        }\n
\n
        delete cache[this.id];\n
        delete this.dom;\n
    }\n
\n
}, function(Element) {\n
    Ext.elements = Ext.cache = Element.cache;\n
\n
    this.addStatics({\n
        Fly: new Ext.Class({\n
            extend: Element,\n
\n
            constructor: function(dom) {\n
                this.dom = dom;\n
            }\n
        }),\n
\n
        _flyweights: {},\n
\n
        /**\n
         * Gets the globally shared flyweight Element, with the passed node as the active element. Do not store a reference\n
         * to this element - the dom node can be overwritten by other code. {@link Ext#fly} is alias for\n
         * {@link Ext.dom.Element#fly}.\n
         *\n
         * Use this to make one-time references to DOM elements which are not going to be accessed again either by\n
         * application code, or by Ext\'s classes. If accessing an element which will be processed regularly, then {@link\n
         * Ext#get Ext.get} will be more appropriate to take advantage of the caching provided by the {@link Ext.dom.Element}\n
         * class.\n
         *\n
         * @param {String/HTMLElement} element The DOM node or `id`.\n
         * @param {String} [named] Allows for creation of named reusable flyweights to prevent conflicts (e.g.\n
         * internally Ext uses "_global").\n
         * @return {Ext.dom.Element} The shared Element object (or `null` if no matching element was found).\n
         * @static\n
         */\n
        fly: function(element, named) {\n
            var fly = null,\n
                flyweights = Element._flyweights,\n
                cachedElement;\n
\n
            named = named || \'_global\';\n
\n
            element = Ext.getDom(element);\n
\n
            if (element) {\n
                fly = flyweights[named] || (flyweights[named] = new Element.Fly());\n
                fly.dom = element;\n
                fly.isSynchronized = false;\n
                cachedElement = Ext.cache[element.id];\n
                if (cachedElement && cachedElement.isElement) {\n
                    cachedElement.isSynchronized = false;\n
                }\n
            }\n
\n
            return fly;\n
        }\n
    });\n
\n
    /**\n
     * @member Ext\n
     * @method get\n
     * @alias Ext.dom.Element#get\n
     */\n
    Ext.get = function(element) {\n
        return Element.get.call(Element, element);\n
    };\n
\n
    /**\n
     * @member Ext\n
     * @method fly\n
     * @alias Ext.dom.Element#fly\n
     */\n
    Ext.fly = function() {\n
        return Element.fly.apply(Element, arguments);\n
    };\n
\n
    Ext.ClassManager.onCreated(function() {\n
        Element.mixin(\'observable\', Ext.mixin.Observable);\n
    }, null, \'Ext.mixin.Observable\');\n
\n
\n
});\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-static\n
//@require Ext.Element\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
Ext.dom.Element.addStatics({\n
    numberRe: /\\d+$/,\n
    unitRe: /\\d+(px|em|%|en|ex|pt|in|cm|mm|pc)$/i,\n
    camelRe: /(-[a-z])/gi,\n
    cssRe: /([a-z0-9-]+)\\s*:\\s*([^;\\s]+(?:\\s*[^;\\s]+)*);?/gi,\n
    opacityRe: /alpha\\(opacity=(.*)\\)/i,\n
    propertyCache: {},\n
    defaultUnit: "px",\n
    borders: {l: \'border-left-width\', r: \'border-right-width\', t: \'border-top-width\', b: \'border-bottom-width\'},\n
    paddings: {l: \'padding-left\', r: \'padding-right\', t: \'padding-top\', b: \'padding-bottom\'},\n
    margins: {l: \'margin-left\', r: \'margin-right\', t: \'margin-top\', b: \'margin-bottom\'},\n
\n
    /**\n
     * Test if size has a unit, otherwise appends the passed unit string, or the default for this Element.\n
     * @param {Object} size The size to set.\n
     * @param {String} units The units to append to a numeric size value.\n
     * @return {String}\n
     * @private\n
     * @static\n
     */\n
    addUnits: function(size, units) {\n
        // Size set to a value which means "auto"\n
        if (size === "" || size == "auto" || size === undefined || size === null) {\n
            return size || \'\';\n
        }\n
\n
        // Otherwise, warn if it\'s not a valid CSS measurement\n
        if (Ext.isNumber(size) || this.numberRe.test(size)) {\n
            return size + (units || this.defaultUnit || \'px\');\n
        }\n
        else if (!this.unitRe.test(size)) {\n
            //<debug>\n
            Ext.Logger.warn("Warning, size detected (" + size + ") not a valid property value on Element.addUnits.");\n
            //</debug>\n
            return size || \'\';\n
        }\n
\n
        return size;\n
    },\n
\n
    /**\n
     * @static\n
     * @return {Boolean}\n
     * @private\n
     */\n
    isAncestor: function(p, c) {\n
        var ret = false;\n
\n
        p = Ext.getDom(p);\n
        c = Ext.getDom(c);\n
        if (p && c) {\n
            if (p.contains) {\n
                return p.contains(c);\n
            } else if (p.compareDocumentPosition) {\n
                return !!(p.compareDocumentPosition(c) & 16);\n
            } else {\n
                while ((c = c.parentNode)) {\n
                    ret = c == p || ret;\n
                }\n
            }\n
        }\n
        return ret;\n
    },\n
\n
    /**\n
     * Parses a number or string representing margin sizes into an object. Supports CSS-style margin declarations\n
     * (e.g. 10, "10", "10 10", "10 10 10" and "10 10 10 10" are all valid options and would return the same result)\n
     * @static\n
     * @param {Number/String} box The encoded margins\n
     * @return {Object} An object with margin sizes for top, right, bottom and left containing the unit\n
     */\n
    parseBox: function(box) {\n
        if (typeof box != \'string\') {\n
            box = box.toString();\n
        }\n
\n
        var parts = box.split(\' \'),\n
            ln = parts.length;\n
\n
        if (ln == 1) {\n
            parts[1] = parts[2] = parts[3] = parts[0];\n
        }\n
        else if (ln == 2) {\n
            parts[2] = parts[0];\n
            parts[3] = parts[1];\n
        }\n
        else if (ln == 3) {\n
            parts[3] = parts[1];\n
        }\n
\n
        return {\n
            top: parts[0] || 0,\n
            right: parts[1] || 0,\n
            bottom: parts[2] || 0,\n
            left: parts[3] || 0\n
        };\n
    },\n
\n
    /**\n
     * Parses a number or string representing margin sizes into an object. Supports CSS-style margin declarations\n
     * (e.g. 10, "10", "10 10", "10 10 10" and "10 10 10 10" are all valid options and would return the same result)\n
     * @static\n
     * @param {Number/String} box The encoded margins\n
     * @param {String} units The type of units to add\n
     * @return {String} An string with unitized (px if units is not specified) metrics for top, right, bottom and left\n
     */\n
    unitizeBox: function(box, units) {\n
        var me = this;\n
        box = me.parseBox(box);\n
\n
        return me.addUnits(box.top, units) + \' \' +\n
               me.addUnits(box.right, units) + \' \' +\n
               me.addUnits(box.bottom, units) + \' \' +\n
               me.addUnits(box.left, units);\n
    },\n
\n
    // @private\n
    camelReplaceFn: function(m, a) {\n
        return a.charAt(1).toUpperCase();\n
    },\n
\n
    /**\n
     * Normalizes CSS property keys from dash delimited to camel case JavaScript Syntax.\n
     * For example:\n
     *\n
     * - border-width -> borderWidth\n
     * - padding-top -> paddingTop\n
     *\n
     * @static\n
     * @param {String} prop The property to normalize\n
     * @return {String} The normalized string\n
     */\n
    normalize: function(prop) {\n
        // TODO: Mobile optimization?\n
//        if (prop == \'float\') {\n
//            prop = Ext.supports.Float ? \'cssFloat\' : \'styleFloat\';\n
//        }\n
        return this.propertyCache[prop] || (this.propertyCache[prop] = prop.replace(this.camelRe, this.camelReplaceFn));\n
    },\n
\n
    /**\n
     * Returns the top Element that is located at the passed coordinates\n
     * @static\n
     * @param {Number} x The x coordinate\n
     * @param {Number} y The y coordinate\n
     * @return {String} The found Element\n
     */\n
    fromPoint: function(x, y) {\n
        return Ext.get(document.elementFromPoint(x, y));\n
    },\n
\n
    /**\n
     * Converts a CSS string into an object with a property for each style.\n
     *\n
     * The sample code below would return an object with 2 properties, one\n
     * for background-color and one for color.\n
     *\n
     *     var css = \'background-color: red;color: blue; \';\n
     *     console.log(Ext.dom.Element.parseStyles(css));\n
     *\n
     * @static\n
     * @param {String} styles A CSS string\n
     * @return {Object} styles\n
     */\n
    parseStyles: function(styles) {\n
        var out = {},\n
            cssRe = this.cssRe,\n
            matches;\n
\n
        if (styles) {\n
            // Since we\'re using the g flag on the regex, we need to set the lastIndex.\n
            // This automatically happens on some implementations, but not others, see:\n
            // http://stackoverflow.com/questions/2645273/javascript-regular-expression-literal-persists-between-function-calls\n
            // http://blog.stevenlevithan.com/archives/fixing-javascript-regexp\n
            cssRe.lastIndex = 0;\n
            while ((matches = cssRe.exec(styles))) {\n
                out[matches[1]] = matches[2];\n
            }\n
        }\n
        return out;\n
    }\n
});\n
\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-alignment\n
//@require Ext.Element-static\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-insertion\n
//@require Ext.Element-alignment\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
Ext.dom.Element.addMembers({\n
\n
    /**\n
     * Appends the passed element(s) to this element.\n
     * @param {HTMLElement/Ext.dom.Element} element a DOM Node or an existing Element.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    appendChild: function(element) {\n
        this.dom.appendChild(Ext.getDom(element));\n
\n
        return this;\n
    },\n
\n
    removeChild: function(element) {\n
        this.dom.removeChild(Ext.getDom(element));\n
\n
        return this;\n
    },\n
\n
    append: function() {\n
        this.appendChild.apply(this, arguments);\n
    },\n
\n
    /**\n
     * Appends this element to the passed element.\n
     * @param {String/HTMLElement/Ext.dom.Element} el The new parent element.\n
     * The id of the node, a DOM Node or an existing Element.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    appendTo: function(el) {\n
        Ext.getDom(el).appendChild(this.dom);\n
        return this;\n
    },\n
\n
    /**\n
     * Inserts this element before the passed element in the DOM.\n
     * @param {String/HTMLElement/Ext.dom.Element} el The element before which this element will be inserted.\n
     * The id of the node, a DOM Node or an existing Element.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    insertBefore: function(el) {\n
        el = Ext.getDom(el);\n
        el.parentNode.insertBefore(this.dom, el);\n
        return this;\n
    },\n
\n
    /**\n
     * Inserts this element after the passed element in the DOM.\n
     * @param {String/HTMLElement/Ext.dom.Element} el The element to insert after.\n
     * The `id` of the node, a DOM Node or an existing Element.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    insertAfter: function(el) {\n
        el = Ext.getDom(el);\n
        el.parentNode.insertBefore(this.dom, el.nextSibling);\n
        return this;\n
    },\n
\n
\n
    /**\n
     * Inserts an element as the first child of this element.\n
     * @param {String/HTMLElement/Ext.dom.Element} element The `id` or element to insert.\n
     * @return {Ext.dom.Element} this\n
     */\n
    insertFirst: function(element) {\n
        var elementDom = Ext.getDom(element),\n
            dom = this.dom,\n
            firstChild = dom.firstChild;\n
\n
        if (!firstChild) {\n
            dom.appendChild(elementDom);\n
        }\n
        else {\n
            dom.insertBefore(elementDom, firstChild);\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Inserts (or creates) the passed element (or DomHelper config) as a sibling of this element\n
     * @param {String/HTMLElement/Ext.dom.Element/Object/Array} el The id, element to insert or a DomHelper config\n
     * to create and insert *or* an array of any of those.\n
     * @param {String} [where=before] (optional) \'before\' or \'after\'.\n
     * @param {Boolean} returnDom (optional) `true` to return the raw DOM element instead of Ext.dom.Element.\n
     * @return {Ext.dom.Element} The inserted Element. If an array is passed, the last inserted element is returned.\n
     */\n
    insertSibling: function(el, where, returnDom) {\n
        var me = this, rt,\n
            isAfter = (where || \'before\').toLowerCase() == \'after\',\n
            insertEl;\n
\n
        if (Ext.isArray(el)) {\n
            insertEl = me;\n
            Ext.each(el, function(e) {\n
                rt = Ext.fly(insertEl, \'_internal\').insertSibling(e, where, returnDom);\n
                if (isAfter) {\n
                    insertEl = rt;\n
                }\n
            });\n
            return rt;\n
        }\n
\n
        el = el || {};\n
\n
        if (el.nodeType || el.dom) {\n
            rt = me.dom.parentNode.insertBefore(Ext.getDom(el), isAfter ? me.dom.nextSibling : me.dom);\n
            if (!returnDom) {\n
                rt = Ext.get(rt);\n
            }\n
        } else {\n
            if (isAfter && !me.dom.nextSibling) {\n
                rt = Ext.core.DomHelper.append(me.dom.parentNode, el, !returnDom);\n
            } else {\n
                rt = Ext.core.DomHelper[isAfter ? \'insertAfter\' : \'insertBefore\'](me.dom, el, !returnDom);\n
            }\n
        }\n
        return rt;\n
    },\n
\n
    /**\n
     * Replaces the passed element with this element.\n
     * @param {String/HTMLElement/Ext.dom.Element} el The element to replace.\n
     * The id of the node, a DOM Node or an existing Element.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    replace: function(element) {\n
        element = Ext.getDom(element);\n
\n
        element.parentNode.replaceChild(this.dom, element);\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Replaces this element with the passed element.\n
     * @param {String/HTMLElement/Ext.dom.Element/Object} el The new element (id of the node, a DOM Node\n
     * or an existing Element) or a DomHelper config of an element to create.\n
     * @return {Ext.dom.Element} This element.\n
     */\n
    replaceWith: function(el) {\n
        var me = this;\n
\n
        if (el.nodeType || el.dom || typeof el == \'string\') {\n
            el = Ext.get(el);\n
            me.dom.parentNode.insertBefore(el, me.dom);\n
        } else {\n
            el = Ext.core.DomHelper.insertBefore(me.dom, el);\n
        }\n
\n
        delete Ext.cache[me.id];\n
        Ext.removeNode(me.dom);\n
        me.id = Ext.id(me.dom = el);\n
        Ext.dom.Element.addToCache(me.isFlyweight ? new Ext.dom.Element(me.dom) : me);\n
        return me;\n
    },\n
\n
    doReplaceWith: function(element) {\n
        var dom = this.dom;\n
        dom.parentNode.replaceChild(Ext.getDom(element), dom);\n
    },\n
\n
    /**\n
     * Creates the passed DomHelper config and appends it to this element or optionally inserts it before the passed child element.\n
     * @param {Object} config DomHelper element config object.  If no tag is specified (e.g., `{tag:\'input\'}`) then a div will be\n
     * automatically generated with the specified attributes.\n
     * @param {HTMLElement} insertBefore (optional) a child element of this element.\n
     * @param {Boolean} returnDom (optional) `true` to return the dom node instead of creating an Element.\n
     * @return {Ext.dom.Element} The new child element.\n
     */\n
    createChild: function(config, insertBefore, returnDom) {\n
        config = config || {tag: \'div\'};\n
        if (insertBefore) {\n
            return Ext.core.DomHelper.insertBefore(insertBefore, config, returnDom !== true);\n
        }\n
        else {\n
            return Ext.core.DomHelper[!this.dom.firstChild ? \'insertFirst\' : \'append\'](this.dom, config, returnDom !== true);\n
        }\n
    },\n
\n
    /**\n
     * Creates and wraps this element with another element.\n
     * @param {Object} [config] (optional) DomHelper element config object for the wrapper element or `null` for an empty div\n
     * @param {Boolean} [domNode] (optional) `true` to return the raw DOM element instead of Ext.dom.Element.\n
     * @return {HTMLElement/Ext.dom.Element} The newly created wrapper element.\n
     */\n
    wrap: function(config, domNode) {\n
        var dom = this.dom,\n
            wrapper = this.self.create(config, domNode),\n
            wrapperDom = (domNode) ? wrapper : wrapper.dom,\n
            parentNode = dom.parentNode;\n
\n
        if (parentNode) {\n
            parentNode.insertBefore(wrapperDom, dom);\n
        }\n
\n
        wrapperDom.appendChild(dom);\n
\n
        return wrapper;\n
    },\n
\n
    wrapAllChildren: function(config) {\n
        var dom = this.dom,\n
            children = dom.childNodes,\n
            wrapper = this.self.create(config),\n
            wrapperDom = wrapper.dom;\n
\n
        while (children.length > 0) {\n
            wrapperDom.appendChild(dom.firstChild);\n
        }\n
\n
        dom.appendChild(wrapperDom);\n
\n
        return wrapper;\n
    },\n
\n
    unwrapAllChildren: function() {\n
        var dom = this.dom,\n
            children = dom.childNodes,\n
            parentNode = dom.parentNode;\n
\n
        if (parentNode) {\n
            while (children.length > 0) {\n
                parentNode.insertBefore(dom, dom.firstChild);\n
            }\n
\n
            this.destroy();\n
        }\n
    },\n
\n
    unwrap: function() {\n
        var dom = this.dom,\n
            parentNode = dom.parentNode,\n
            grandparentNode;\n
\n
        if (parentNode) {\n
            grandparentNode = parentNode.parentNode;\n
            grandparentNode.insertBefore(dom, parentNode);\n
            grandparentNode.removeChild(parentNode);\n
        }\n
        else {\n
            grandparentNode = document.createDocumentFragment();\n
            grandparentNode.appendChild(dom);\n
        }\n
\n
        return this;\n
    },\n
\n
    detach: function() {\n
        var dom = this.dom;\n
\n
        if (dom && dom.parentNode && dom.tagName !== \'BODY\') {\n
            dom.parentNode.removeChild(dom);\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Inserts an HTML fragment into this element.\n
     * @param {String} where Where to insert the HTML in relation to this element - \'beforeBegin\', \'afterBegin\', \'beforeEnd\', \'afterEnd\'.\n
     * See {@link Ext.DomHelper#insertHtml} for details.\n
     * @param {String} html The HTML fragment\n
     * @param {Boolean} [returnEl=false] (optional) `true` to return an Ext.dom.Element.\n
     * @return {HTMLElement/Ext.dom.Element} The inserted node (or nearest related if more than 1 inserted).\n
     */\n
    insertHtml: function(where, html, returnEl) {\n
        var el = Ext.core.DomHelper.insertHtml(where, this.dom, html);\n
        return returnEl ? Ext.get(el) : el;\n
    }\n
});\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-position\n
//@require Ext.Element-insertion\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
Ext.dom.Element.override({\n
\n
    /**\n
     * Gets the current X position of the element based on page coordinates.  Element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @return {Number} The X position of the element\n
     */\n
    getX: function(el) {\n
        return this.getXY(el)[0];\n
    },\n
\n
    /**\n
     * Gets the current Y position of the element based on page coordinates.  Element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @return {Number} The Y position of the element\n
     */\n
    getY: function(el) {\n
        return this.getXY(el)[1];\n
    },\n
\n
    /**\n
     * Gets the current position of the element based on page coordinates.  Element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @return {Array} The XY position of the element\n
     */\n
\n
    getXY: function() {\n
        var rect = this.dom.getBoundingClientRect(),\n
            round = Math.round;\n
\n
        return [round(rect.left + window.pageXOffset), round(rect.top + window.pageYOffset)];\n
    },\n
\n
    /**\n
     * Returns the offsets of this element from the passed element. Both element must be part of the DOM tree\n
     * and not have `display:none` to have page coordinates.\n
     * @param {Mixed} element The element to get the offsets from.\n
     * @return {Array} The XY page offsets (e.g. [100, -200])\n
     */\n
    getOffsetsTo: function(el) {\n
        var o = this.getXY(),\n
            e = Ext.fly(el, \'_internal\').getXY();\n
        return [o[0] - e[0], o[1] - e[1]];\n
    },\n
\n
    /**\n
     * Sets the X position of the element based on page coordinates.  Element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @param {Number} The X position of the element\n
     * @param {Boolean/Object} animate (optional) `true` for the default animation, or a standard Element animation config object.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setX: function(x) {\n
        return this.setXY([x, this.getY()]);\n
    },\n
\n
    /**\n
     * Sets the Y position of the element based on page coordinates.  Element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @param {Number} The Y position of the element.\n
     * @param {Boolean/Object} animate (optional) `true` for the default animation, or a standard Element animation config object.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setY: function(y) {\n
        return this.setXY([this.getX(), y]);\n
    },\n
\n
    /**\n
     * Sets the position of the element in page coordinates, regardless of how the element is positioned.\n
     * The element must be part of the DOM tree to have page coordinates (`display:none` or elements not appended return `false`).\n
     * @param {Array} pos Contains X & Y [x, y] values for new position (coordinates are page-based).\n
     * @param {Boolean/Object} animate (optional) `true` for the default animation, or a standard Element animation config object.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setXY: function(pos) {\n
        var me = this;\n
\n
        if (arguments.length > 1) {\n
            pos = [pos, arguments[1]];\n
        }\n
\n
        // me.position();\n
        var pts = me.translatePoints(pos),\n
            style = me.dom.style;\n
\n
        for (pos in pts) {\n
            if (!pts.hasOwnProperty(pos)) {\n
                continue;\n
            }\n
            if (!isNaN(pts[pos])) style[pos] = pts[pos] + "px";\n
        }\n
        return me;\n
    },\n
\n
    /**\n
     * Gets the left X coordinate.\n
     * @return {Number}\n
     */\n
    getLeft: function() {\n
        return parseInt(this.getStyle(\'left\'), 10) || 0;\n
    },\n
\n
    /**\n
     * Gets the right X coordinate of the element (element X position + element width).\n
     * @return {Number}\n
     */\n
    getRight: function() {\n
        return parseInt(this.getStyle(\'right\'), 10) || 0;\n
    },\n
\n
    /**\n
     * Gets the top Y coordinate.\n
     * @return {Number}\n
     */\n
    getTop: function() {\n
        return parseInt(this.getStyle(\'top\'), 10) || 0;\n
    },\n
\n
    /**\n
     * Gets the bottom Y coordinate of the element (element Y position + element height).\n
     * @return {Number}\n
     */\n
    getBottom: function() {\n
        return parseInt(this.getStyle(\'bottom\'), 10) || 0;\n
    },\n
\n
    /**\n
     * Translates the passed page coordinates into left/top CSS values for this element.\n
     * @param {Number/Array} x The page `x` or an array containing [x, y].\n
     * @param {Number} y (optional) The page `y`, required if `x` is not an array.\n
     * @return {Object} An object with `left` and `top` properties. e.g. `{left: (value), top: (value)}`.\n
     */\n
    translatePoints: function(x, y) {\n
        y = isNaN(x[1]) ? y : x[1];\n
        x = isNaN(x[0]) ? x : x[0];\n
\n
        var me = this,\n
            relative = me.isStyle(\'position\', \'relative\'),\n
            o = me.getXY(),\n
            l = parseInt(me.getStyle(\'left\'), 10),\n
            t = parseInt(me.getStyle(\'top\'), 10);\n
\n
        l = !isNaN(l) ? l : (relative ? 0 : me.dom.offsetLeft);\n
        t = !isNaN(t) ? t : (relative ? 0 : me.dom.offsetTop);\n
\n
        return {left: (x - o[0] + l), top: (y - o[1] + t)};\n
    },\n
\n
    /**\n
     * Sets the element\'s box. Use {@link #getBox} on another element to get a box object.\n
     * @param {Object} box The box to fill, for example:\n
     *\n
     *     {\n
     *         left: ...,\n
     *         top: ...,\n
     *         width: ...,\n
     *         height: ...\n
     *     }\n
     *\n
     * @return {Ext.dom.Element} this\n
     */\n
    setBox: function(box) {\n
        var me = this,\n
            width = box.width,\n
            height = box.height,\n
            top = box.top,\n
            left = box.left;\n
\n
        if (left !== undefined) {\n
            me.setLeft(left);\n
        }\n
        if (top !== undefined) {\n
            me.setTop(top);\n
        }\n
        if (width !== undefined) {\n
            me.setWidth(width);\n
        }\n
        if (height !== undefined) {\n
            me.setHeight(height);\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Return an object defining the area of this Element which can be passed to {@link #setBox} to\n
     * set another Element\'s size/location to match this element.\n
     *\n
     * The returned object may also be addressed as an Array where index 0 contains the X position\n
     * and index 1 contains the Y position. So the result may also be used for {@link #setXY}.\n
     *\n
     * @param {Boolean} contentBox (optional) If `true` a box for the content of the element is returned.\n
     * @param {Boolean} local (optional) If `true` the element\'s left and top are returned instead of page x/y.\n
     * @return {Object} An object in the format\n
     * @return {Number} return.x The element\'s X position.\n
     * @return {Number} return.y The element\'s Y position.\n
     * @return {Number} return.width The element\'s width.\n
     * @return {Number} return.height The element\'s height.\n
     * @return {Number} return.bottom The element\'s lower bound.\n
     * @return {Number} return.right The element\'s rightmost bound.\n
     */\n
    getBox: function(contentBox, local) {\n
        var me = this,\n
            dom = me.dom,\n
            width = dom.offsetWidth,\n
            height = dom.offsetHeight,\n
            xy, box, l, r, t, b;\n
\n
        if (!local) {\n
            xy = me.getXY();\n
        }\n
        else if (contentBox) {\n
            xy = [0, 0];\n
        }\n
        else {\n
            xy = [parseInt(me.getStyle("left"), 10) || 0, parseInt(me.getStyle("top"), 10) || 0];\n
        }\n
\n
        if (!contentBox) {\n
            box = {\n
                x: xy[0],\n
                y: xy[1],\n
                0: xy[0],\n
                1: xy[1],\n
                width: width,\n
                height: height\n
            };\n
        }\n
        else {\n
            l = me.getBorderWidth.call(me, "l") + me.getPadding.call(me, "l");\n
            r = me.getBorderWidth.call(me, "r") + me.getPadding.call(me, "r");\n
            t = me.getBorderWidth.call(me, "t") + me.getPadding.call(me, "t");\n
            b = me.getBorderWidth.call(me, "b") + me.getPadding.call(me, "b");\n
            box = {\n
                x: xy[0] + l,\n
                y: xy[1] + t,\n
                0: xy[0] + l,\n
                1: xy[1] + t,\n
                width: width - (l + r),\n
                height: height - (t + b)\n
            };\n
        }\n
\n
        box.left = box.x;\n
        box.top = box.y;\n
        box.right = box.x + box.width;\n
        box.bottom = box.y + box.height;\n
\n
        return box;\n
    },\n
\n
    /**\n
     * Return an object defining the area of this Element which can be passed to {@link #setBox} to\n
     * set another Element\'s size/location to match this element.\n
     * @param {Boolean} asRegion (optional) If `true` an {@link Ext.util.Region} will be returned.\n
     * @return {Object} box An object in the format:\n
     *\n
     *     {\n
     *         x: <Element\'s X position>,\n
     *         y: <Element\'s Y position>,\n
     *         width: <Element\'s width>,\n
     *         height: <Element\'s height>,\n
     *         bottom: <Element\'s lower bound>,\n
     *         right: <Element\'s rightmost bound>\n
     *     }\n
     *\n
     * The returned object may also be addressed as an Array where index 0 contains the X position\n
     * and index 1 contains the Y position. So the result may also be used for {@link #setXY}.\n
     */\n
    getPageBox: function(getRegion) {\n
        var me = this,\n
            el = me.dom,\n
            w = el.offsetWidth,\n
            h = el.offsetHeight,\n
            xy = me.getXY(),\n
            t = xy[1],\n
            r = xy[0] + w,\n
            b = xy[1] + h,\n
            l = xy[0];\n
\n
        if (!el) {\n
            return new Ext.util.Region();\n
        }\n
\n
        if (getRegion) {\n
            return new Ext.util.Region(t, r, b, l);\n
        }\n
        else {\n
            return {\n
                left: l,\n
                top: t,\n
                width: w,\n
                height: h,\n
                right: r,\n
                bottom: b\n
            };\n
        }\n
    }\n
});\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-style\n
//@require Ext.Element-position\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
\n
Ext.dom.Element.addMembers({\n
    WIDTH: \'width\',\n
    HEIGHT: \'height\',\n
    MIN_WIDTH: \'min-width\',\n
    MIN_HEIGHT: \'min-height\',\n
    MAX_WIDTH: \'max-width\',\n
    MAX_HEIGHT: \'max-height\',\n
    TOP: \'top\',\n
    RIGHT: \'right\',\n
    BOTTOM: \'bottom\',\n
    LEFT: \'left\',\n
    /**\n
     * @property VISIBILITY\n
     * Visibility mode constant for use with {@link #setVisibilityMode}. Use `visibility` to hide element.\n
     */\n
    VISIBILITY: 1,\n
\n
    /**\n
     * @property DISPLAY\n
     * Visibility mode constant for use with {@link #setVisibilityMode}. Use `display` to hide element.\n
     */\n
    DISPLAY: 2,\n
\n
    /**\n
     * @property OFFSETS\n
     * Visibility mode constant for use with {@link #setVisibilityMode}. Use offsets to hide element.\n
     */\n
    OFFSETS: 3,\n
\n
    SEPARATOR: \'-\',\n
\n
    trimRe: /^\\s+|\\s+$/g,\n
    wordsRe: /\\w/g,\n
    spacesRe: /\\s+/,\n
    styleSplitRe: /\\s*(?::|;)\\s*/,\n
    transparentRe: /^(?:transparent|(?:rgba[(](?:\\s*\\d+\\s*[,]){3}\\s*0\\s*[)]))$/i,\n
    classNameSplitRegex: /[\\s]+/,\n
\n
    borders: {\n
        t: \'border-top-width\',\n
        r: \'border-right-width\',\n
        b: \'border-bottom-width\',\n
        l: \'border-left-width\'\n
    },\n
\n
    paddings: {\n
        t: \'padding-top\',\n
        r: \'padding-right\',\n
        b: \'padding-bottom\',\n
        l: \'padding-left\'\n
    },\n
\n
    margins: {\n
        t: \'margin-top\',\n
        r: \'margin-right\',\n
        b: \'margin-bottom\',\n
        l: \'margin-left\'\n
    },\n
\n
    /**\n
     * @property {String} defaultUnit\n
     * The default unit to append to CSS values where a unit isn\'t provided.\n
     */\n
    defaultUnit: "px",\n
\n
    isSynchronized: false,\n
\n
    /**\n
     * @private\n
     */\n
    synchronize: function() {\n
        var dom = this.dom,\n
            hasClassMap = {},\n
            className = dom.className,\n
            classList, i, ln, name;\n
\n
        if (className.length > 0) {\n
            classList = dom.className.split(this.classNameSplitRegex);\n
\n
            for (i = 0, ln = classList.length; i < ln; i++) {\n
                name = classList[i];\n
                hasClassMap[name] = true;\n
            }\n
        }\n
        else {\n
            classList = [];\n
        }\n
\n
        this.classList = classList;\n
\n
        this.hasClassMap = hasClassMap;\n
\n
        this.isSynchronized = true;\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Adds the given CSS class(es) to this Element.\n
     * @param {String} names The CSS class(es) to add to this element.\n
     * @param {String} [prefix] (optional) Prefix to prepend to each class.\n
     * @param {String} [suffix] (optional) Suffix to append to each class.\n
     */\n
    addCls: function(names, prefix, suffix) {\n
        if (!names) {\n
            return this;\n
        }\n
\n
        if (!this.isSynchronized) {\n
            this.synchronize();\n
        }\n
\n
        var dom = this.dom,\n
            map = this.hasClassMap,\n
            classList = this.classList,\n
            SEPARATOR = this.SEPARATOR,\n
            i, ln, name;\n
\n
        prefix = prefix ? prefix + SEPARATOR : \'\';\n
        suffix = suffix ? SEPARATOR + suffix : \'\';\n
\n
        if (typeof names == \'string\') {\n
            names = names.split(this.spacesRe);\n
        }\n
\n
        for (i = 0, ln = names.length; i < ln; i++) {\n
            name = prefix + names[i] + suffix;\n
\n
            if (!map[name]) {\n
                map[name] = true;\n
                classList.push(name);\n
            }\n
        }\n
\n
        dom.className = classList.join(\' \');\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Removes the given CSS class(es) from this Element.\n
     * @param {String} names The CSS class(es) to remove from this element.\n
     * @param {String} [prefix=\'\'] (optional) Prefix to prepend to each class to be removed.\n
     * @param {String} [suffix=\'\'] (optional) Suffix to append to each class to be removed.\n
     */\n
    removeCls: function(names, prefix, suffix) {\n
        if (!names) {\n
            return this;\n
        }\n
\n
        if (!this.isSynchronized) {\n
            this.synchronize();\n
        }\n
\n
        if (!suffix) {\n
            suffix = \'\';\n
        }\n
\n
        var dom = this.dom,\n
            map = this.hasClassMap,\n
            classList = this.classList,\n
            SEPARATOR = this.SEPARATOR,\n
            i, ln, name;\n
\n
        prefix = prefix ? prefix + SEPARATOR : \'\';\n
        suffix = suffix ? SEPARATOR + suffix : \'\';\n
\n
        if (typeof names == \'string\') {\n
            names = names.split(this.spacesRe);\n
        }\n
\n
        for (i = 0, ln = names.length; i < ln; i++) {\n
            name = prefix + names[i] + suffix;\n
\n
            if (map[name]) {\n
                delete map[name];\n
                Ext.Array.remove(classList, name);\n
            }\n
        }\n
\n
        dom.className = classList.join(\' \');\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Replaces a CSS class on the element with another.  If the old name does not exist, the new name will simply be added.\n
     * @param {String} oldClassName The CSS class to replace.\n
     * @param {String} newClassName The replacement CSS class.\n
     * @return {Ext.dom.Element} this\n
     */\n
    replaceCls: function(oldName, newName, prefix, suffix) {\n
        return this.removeCls(oldName, prefix, suffix).addCls(newName, prefix, suffix);\n
    },\n
\n
    /**\n
     * Checks if the specified CSS class exists on this element\'s DOM node.\n
     * @param {String} className The CSS class to check for.\n
     * @return {Boolean} `true` if the class exists, else `false`.\n
     */\n
    hasCls: function(name) {\n
        if (!this.isSynchronized) {\n
            this.synchronize();\n
        }\n
\n
        return this.hasClassMap.hasOwnProperty(name);\n
    },\n
\n
    /**\n
     * Toggles the specified CSS class on this element (removes it if it already exists, otherwise adds it).\n
     * @param {String} className The CSS class to toggle.\n
     * @return {Ext.dom.Element} this\n
     */\n
    toggleCls: function(className, force){\n
        if (typeof force !== \'boolean\') {\n
            force = !this.hasCls(className);\n
        }\n
\n
   \t\treturn (force) ? this.addCls(className) : this.removeCls(className);\n
   \t},\n
\n
    /**\n
     * @private\n
     * @param firstClass\n
     * @param secondClass\n
     * @param flag\n
     * @param prefix\n
     * @return {Mixed}\n
     */\n
    swapCls: function(firstClass, secondClass, flag, prefix) {\n
        if (flag === undefined) {\n
            flag = true;\n
        }\n
\n
        var addedClass = flag ? firstClass : secondClass,\n
            removedClass = flag ? secondClass : firstClass;\n
\n
        if (removedClass) {\n
            this.removeCls(prefix ? prefix + \'-\' + removedClass : removedClass);\n
        }\n
\n
        if (addedClass) {\n
            this.addCls(prefix ? prefix + \'-\' + addedClass : addedClass);\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Set the width of this Element.\n
     * @param {Number/String} width The new width.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setWidth: function(width) {\n
        return this.setLengthValue(this.WIDTH, width);\n
    },\n
\n
    /**\n
     * Set the height of this Element.\n
     * @param {Number/String} height The new height.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setHeight: function(height) {\n
        return this.setLengthValue(this.HEIGHT, height);\n
    },\n
\n
    /**\n
     * Set the size of this Element.\n
     *\n
     * @param {Number/String} width The new width. This may be one of:\n
     *\n
     * - A Number specifying the new width in this Element\'s {@link #defaultUnit}s (by default, pixels).\n
     * - A String used to set the CSS width style. Animation may **not** be used.\n
     * - A size object in the format `{width: widthValue, height: heightValue}`.\n
     *\n
     * @param {Number/String} height The new height. This may be one of:\n
     *\n
     * - A Number specifying the new height in this Element\'s {@link #defaultUnit}s (by default, pixels).\n
     * - A String used to set the CSS height style. Animation may **not** be used.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setSize: function(width, height) {\n
        if (Ext.isObject(width)) {\n
            // in case of object from getSize()\n
            height = width.height;\n
            width = width.width;\n
        }\n
\n
        this.setWidth(width);\n
        this.setHeight(height);\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Set the minimum width of this Element.\n
     * @param {Number/String} width The new minimum width.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setMinWidth: function(width) {\n
        return this.setLengthValue(this.MIN_WIDTH, width);\n
    },\n
\n
    /**\n
     * Set the minimum height of this Element.\n
     * @param {Number/String} height The new minimum height.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setMinHeight: function(height) {\n
        return this.setLengthValue(this.MIN_HEIGHT, height);\n
    },\n
\n
    /**\n
     * Set the maximum width of this Element.\n
     * @param {Number/String} width The new maximum width.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setMaxWidth: function(width) {\n
        return this.setLengthValue(this.MAX_WIDTH, width);\n
    },\n
\n
    /**\n
     * Set the maximum height of this Element.\n
     * @param {Number/String} height The new maximum height.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setMaxHeight: function(height) {\n
        return this.setLengthValue(this.MAX_HEIGHT, height);\n
    },\n
\n
    /**\n
     * Sets the element\'s top position directly using CSS style (instead of {@link #setY}).\n
     * @param {String} top The top CSS property value.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setTop: function(top) {\n
        return this.setLengthValue(this.TOP, top);\n
    },\n
\n
    /**\n
     * Sets the element\'s CSS right style.\n
     * @param {String} right The right CSS property value.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setRight: function(right) {\n
        return this.setLengthValue(this.RIGHT, right);\n
    },\n
\n
    /**\n
     * Sets the element\'s CSS bottom style.\n
     * @param {String} bottom The bottom CSS property value.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setBottom: function(bottom) {\n
        return this.setLengthValue(this.BOTTOM, bottom);\n
    },\n
\n
    /**\n
     * Sets the element\'s left position directly using CSS style (instead of {@link #setX}).\n
     * @param {String} left The left CSS property value.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setLeft: function(left) {\n
        return this.setLengthValue(this.LEFT, left);\n
    },\n
\n
    setMargin: function(margin) {\n
        var domStyle = this.dom.style;\n
\n
        if (margin || margin === 0) {\n
            margin = this.self.unitizeBox((margin === true) ? 5 : margin);\n
            domStyle.setProperty(\'margin\', margin, \'important\');\n
        }\n
        else {\n
            domStyle.removeProperty(\'margin-top\');\n
            domStyle.removeProperty(\'margin-right\');\n
            domStyle.removeProperty(\'margin-bottom\');\n
            domStyle.removeProperty(\'margin-left\');\n
        }\n
    },\n
\n
    setPadding: function(padding) {\n
        var domStyle = this.dom.style;\n
\n
        if (padding || padding === 0) {\n
            padding = this.self.unitizeBox((padding === true) ? 5 : padding);\n
            domStyle.setProperty(\'padding\', padding, \'important\');\n
        }\n
        else {\n
            domStyle.removeProperty(\'padding-top\');\n
            domStyle.removeProperty(\'padding-right\');\n
            domStyle.removeProperty(\'padding-bottom\');\n
            domStyle.removeProperty(\'padding-left\');\n
        }\n
    },\n
\n
    setBorder: function(border) {\n
        var domStyle = this.dom.style;\n
\n
        if (border || border === 0) {\n
            border = this.self.unitizeBox((border === true) ? 1 : border);\n
            domStyle.setProperty(\'border-width\', border, \'important\');\n
        }\n
        else {\n
            domStyle.removeProperty(\'border-top-width\');\n
            domStyle.removeProperty(\'border-right-width\');\n
            domStyle.removeProperty(\'border-bottom-width\');\n
            domStyle.removeProperty(\'border-left-width\');\n
        }\n
    },\n
\n
    setLengthValue: function(name, value) {\n
        var domStyle = this.dom.style;\n
\n
        if (value === null) {\n
            domStyle.removeProperty(name);\n
            return this;\n
        }\n
\n
        if (typeof value == \'number\') {\n
            value = value + \'px\';\n
        }\n
\n
        domStyle.setProperty(name, value, \'important\');\n
        return this;\n
    },\n
\n
    /**\n
     * Sets the visibility of the element (see details). If the `visibilityMode` is set to `Element.DISPLAY`, it will use\n
     * the display property to hide the element, otherwise it uses visibility. The default is to hide and show using the `visibility` property.\n
     * @param {Boolean} visible Whether the element is visible.\n
     * @return {Ext.Element} this\n
     */\n
    setVisible: function(visible) {\n
        var mode = this.getVisibilityMode(),\n
            method = visible ? \'removeCls\' : \'addCls\';\n
\n
        switch (mode) {\n
            case this.VISIBILITY:\n
                this.removeCls([\'x-hidden-display\', \'x-hidden-offsets\']);\n
                this[method](\'x-hidden-visibility\');\n
                break;\n
\n
            case this.DISPLAY:\n
                this.removeCls([\'x-hidden-visibility\', \'x-hidden-offsets\']);\n
                this[method](\'x-hidden-display\');\n
                break;\n
\n
            case this.OFFSETS:\n
                this.removeCls([\'x-hidden-visibility\', \'x-hidden-display\']);\n
                this[method](\'x-hidden-offsets\');\n
                break;\n
        }\n
\n
        return this;\n
    },\n
\n
    getVisibilityMode: function() {\n
        var dom = this.dom,\n
            mode = Ext.dom.Element.data(dom, \'visibilityMode\');\n
\n
        if (mode === undefined) {\n
            Ext.dom.Element.data(dom, \'visibilityMode\', mode = this.DISPLAY);\n
        }\n
\n
        return mode;\n
    },\n
\n
    /**\n
     * Use this to change the visibility mode between {@link #VISIBILITY}, {@link #DISPLAY} or {@link #OFFSETS}.\n
     */\n
    setVisibilityMode: function(mode) {\n
        this.self.data(this.dom, \'visibilityMode\', mode);\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Shows this element.\n
     * Uses display mode to determine whether to use "display" or "visibility". See {@link #setVisible}.\n
     */\n
    show: function() {\n
        var dom = this.dom;\n
        if (dom) {\n
            dom.style.removeProperty(\'display\');\n
        }\n
    },\n
\n
    /**\n
     * Hides this element.\n
     * Uses display mode to determine whether to use "display" or "visibility". See {@link #setVisible}.\n
     */\n
    hide: function() {\n
        this.dom.style.setProperty(\'display\', \'none\', \'important\');\n
    },\n
\n
    setVisibility: function(isVisible) {\n
        var domStyle = this.dom.style;\n
\n
        if (isVisible) {\n
            domStyle.removeProperty(\'visibility\');\n
        }\n
        else {\n
            domStyle.setProperty(\'visibility\', \'hidden\', \'important\');\n
        }\n
    },\n
\n
    /**\n
     * This shared object is keyed by style name (e.g., \'margin-left\' or \'marginLeft\'). The\n
     * values are objects with the following properties:\n
     *\n
     *  * `name` (String) : The actual name to be presented to the DOM. This is typically the value\n
     *      returned by {@link #normalize}.\n
     *  * `get` (Function) : A hook function that will perform the get on this style. These\n
     *      functions receive "(dom, el)" arguments. The `dom` parameter is the DOM Element\n
     *      from which to get the style. The `el` argument (may be `null`) is the Ext.Element.\n
     *  * `set` (Function) : A hook function that will perform the set on this style. These\n
     *      functions receive "(dom, value, el)" arguments. The `dom` parameter is the DOM Element\n
     *      from which to get this style. The `value` parameter is the new value for the style. The\n
     *      `el` argument (may be `null`) is the Ext.Element.\n
     *\n
     * The `this` pointer is the object that contains `get` or `set`, which means that\n
     * `this.name` can be accessed if needed. The hook functions are both optional.\n
     * @private\n
     */\n
    styleHooks: {},\n
\n
    // @private\n
    addStyles: function(sides, styles) {\n
        var totalSize = 0,\n
            sidesArr = sides.match(this.wordsRe),\n
            i = 0,\n
            len = sidesArr.length,\n
            side, size;\n
        for (; i < len; i++) {\n
    

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAg=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="8" aka="AAAAAAAAAAg=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

        side = sidesArr[i];\n
            size = side && parseInt(this.getStyle(styles[side]), 10);\n
            if (size) {\n
                totalSize += Math.abs(size);\n
            }\n
        }\n
        return totalSize;\n
    },\n
\n
    /**\n
     * Checks if the current value of a style is equal to a given value.\n
     * @param {String} style property whose value is returned.\n
     * @param {String} value to check against.\n
     * @return {Boolean} `true` for when the current value equals the given value.\n
     */\n
    isStyle: function(style, val) {\n
        return this.getStyle(style) == val;\n
    },\n
\n
    getStyleValue: function(name) {\n
        return this.dom.style.getPropertyValue(name);\n
    },\n
\n
    /**\n
     * Normalizes `currentStyle` and `computedStyle`.\n
     * @param {String} prop The style property whose value is returned.\n
     * @return {String} The current value of the style property for this element.\n
     */\n
    getStyle: function(prop) {\n
        var me = this,\n
            dom = me.dom,\n
            hook = me.styleHooks[prop],\n
            cs, result;\n
\n
        if (dom == document) {\n
            return null;\n
        }\n
        if (!hook) {\n
            me.styleHooks[prop] = hook = { name: Ext.dom.Element.normalize(prop) };\n
        }\n
        if (hook.get) {\n
            return hook.get(dom, me);\n
        }\n
\n
        cs = window.getComputedStyle(dom, \'\');\n
\n
        // why the dom.style lookup? It is not true that "style == computedStyle" as\n
        // well as the fact that 0/false are valid answers...\n
        result = (cs && cs[hook.name]); // || dom.style[hook.name];\n
\n
        // WebKit returns rgb values for transparent, how does this work n IE9+\n
        //        if (!supportsTransparentColor && result == \'rgba(0, 0, 0, 0)\') {\n
        //            result = \'transparent\';\n
        //        }\n
\n
        return result;\n
    },\n
\n
    /**\n
     * Wrapper for setting style properties, also takes single object parameter of multiple styles.\n
     * @param {String/Object} property The style property to be set, or an object of multiple styles.\n
     * @param {String} [value] The value to apply to the given property, or `null` if an object was passed.\n
     * @return {Ext.dom.Element} this\n
     */\n
    setStyle: function(prop, value) {\n
        var me = this,\n
            dom = me.dom,\n
            hooks = me.styleHooks,\n
            style = dom.style,\n
            valueFrom = Ext.valueFrom,\n
            name, hook;\n
\n
        // we don\'t promote the 2-arg form to object-form to avoid the overhead...\n
        if (typeof prop == \'string\') {\n
            hook = hooks[prop];\n
\n
            if (!hook) {\n
                hooks[prop] = hook = { name: Ext.dom.Element.normalize(prop) };\n
            }\n
            value = valueFrom(value, \'\');\n
\n
            if (hook.set) {\n
                hook.set(dom, value, me);\n
            } else {\n
                style[hook.name] = value;\n
            }\n
        }\n
        else {\n
            for (name in prop) {\n
                if (prop.hasOwnProperty(name)) {\n
                    hook = hooks[name];\n
\n
                    if (!hook) {\n
                        hooks[name] = hook = { name: Ext.dom.Element.normalize(name) };\n
                    }\n
\n
                    value = valueFrom(prop[name], \'\');\n
\n
                    if (hook.set) {\n
                        hook.set(dom, value, me);\n
                    }\n
                    else {\n
                        style[hook.name] = value;\n
                    }\n
                }\n
            }\n
        }\n
\n
        return me;\n
    },\n
\n
    /**\n
     * Returns the offset height of the element.\n
     * @param {Boolean} [contentHeight] `true` to get the height minus borders and padding.\n
     * @return {Number} The element\'s height.\n
     */\n
    getHeight: function(contentHeight) {\n
        var dom = this.dom,\n
            height = contentHeight ? (dom.clientHeight - this.getPadding("tb")) : dom.offsetHeight;\n
        return height > 0 ? height : 0;\n
    },\n
\n
    /**\n
     * Returns the offset width of the element.\n
     * @param {Boolean} [contentWidth] `true` to get the width minus borders and padding.\n
     * @return {Number} The element\'s width.\n
     */\n
    getWidth: function(contentWidth) {\n
        var dom = this.dom,\n
            width = contentWidth ? (dom.clientWidth - this.getPadding("lr")) : dom.offsetWidth;\n
        return width > 0 ? width : 0;\n
    },\n
\n
    /**\n
     * Gets the width of the border(s) for the specified side(s)\n
     * @param {String} side Can be t, l, r, b or any combination of those to add multiple values. For example,\n
     * passing `\'lr\'` would get the border **l**eft width + the border **r**ight width.\n
     * @return {Number} The width of the sides passed added together\n
     */\n
    getBorderWidth: function(side) {\n
        return this.addStyles(side, this.borders);\n
    },\n
\n
    /**\n
     * Gets the width of the padding(s) for the specified side(s).\n
     * @param {String} side Can be t, l, r, b or any combination of those to add multiple values. For example,\n
     * passing `\'lr\'` would get the padding **l**eft + the padding **r**ight.\n
     * @return {Number} The padding of the sides passed added together.\n
     */\n
    getPadding: function(side) {\n
        return this.addStyles(side, this.paddings);\n
    },\n
\n
    /**\n
     * More flexible version of {@link #setStyle} for setting style properties.\n
     * @param {String/Object/Function} styles A style specification string, e.g. "width:100px", or object in the form `{width:"100px"}`, or\n
     * a function which returns such a specification.\n
     * @return {Ext.dom.Element} this\n
     */\n
    applyStyles: function(styles) {\n
        if (styles) {\n
            var dom = this.dom,\n
                styleType, i, len;\n
\n
            if (typeof styles == \'function\') {\n
                styles = styles.call();\n
            }\n
            styleType = typeof styles;\n
            if (styleType == \'string\') {\n
                styles = Ext.util.Format.trim(styles).split(this.styleSplitRe);\n
                for (i = 0, len = styles.length; i < len;) {\n
                    dom.style[Ext.dom.Element.normalize(styles[i++])] = styles[i++];\n
                }\n
            }\n
            else if (styleType == \'object\') {\n
                this.setStyle(styles);\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Returns the size of the element.\n
     * @param {Boolean} [contentSize] `true` to get the width/size minus borders and padding.\n
     * @return {Object} An object containing the element\'s size:\n
     * @return {Number} return.width\n
     * @return {Number} return.height\n
     */\n
    getSize: function(contentSize) {\n
        var dom = this.dom;\n
        return {\n
            width: Math.max(0, contentSize ? (dom.clientWidth - this.getPadding("lr")) : dom.offsetWidth),\n
            height: Math.max(0, contentSize ? (dom.clientHeight - this.getPadding("tb")) : dom.offsetHeight)\n
        };\n
    },\n
\n
    /**\n
     * Forces the browser to repaint this element.\n
     * @return {Ext.dom.Element} this\n
     */\n
    repaint: function() {\n
        var dom = this.dom;\n
        this.addCls(Ext.baseCSSPrefix + \'repaint\');\n
        setTimeout(function() {\n
            Ext.fly(dom).removeCls(Ext.baseCSSPrefix + \'repaint\');\n
        }, 1);\n
        return this;\n
    },\n
\n
    /**\n
     * Returns an object with properties top, left, right and bottom representing the margins of this element unless sides is passed,\n
     * then it returns the calculated width of the sides (see {@link #getPadding}).\n
     * @param {String} [sides] Any combination of \'l\', \'r\', \'t\', \'b\' to get the sum of those sides.\n
     * @return {Object/Number}\n
     */\n
    getMargin: function(side) {\n
        var me = this,\n
            hash = {t: "top", l: "left", r: "right", b: "bottom"},\n
            o = {},\n
            key;\n
\n
        if (!side) {\n
            for (key in me.margins) {\n
                o[hash[key]] = parseFloat(me.getStyle(me.margins[key])) || 0;\n
            }\n
            return o;\n
        } else {\n
            return me.addStyles.call(me, side, me.margins);\n
        }\n
    }\n
});\n
\n
\n
//@tag dom,core\n
//@define Ext.Element-all\n
//@define Ext.Element-traversal\n
//@require Ext.Element-style\n
\n
/**\n
 * @class Ext.dom.Element\n
 */\n
Ext.dom.Element.addMembers({\n
    getParent: function() {\n
        return Ext.get(this.dom.parentNode);\n
    },\n
\n
    getFirstChild: function() {\n
        return Ext.get(this.dom.firstElementChild);\n
    },\n
\n
    /**\n
     * Returns `true` if this element is an ancestor of the passed element.\n
     * @param {HTMLElement/String} element The element to check.\n
     * @return {Boolean} `true` if this element is an ancestor of `el`, else `false`.\n
     */\n
    contains: function(element) {\n
        if (!element) {\n
            return false;\n
        }\n
\n
        var dom = Ext.getDom(element);\n
\n
        // we need el-contains-itself logic here because isAncestor does not do that:\n
        return (dom === this.dom) || this.self.isAncestor(this.dom, dom);\n
    },\n
\n
    /**\n
     * Looks at this node and then at parent nodes for a match of the passed simple selector (e.g. \'div.some-class\' or \'span:first-child\')\n
     * @param {String} selector The simple selector to test.\n
     * @param {Number/String/HTMLElement/Ext.Element} maxDepth (optional)\n
     * The max depth to search as a number or element (defaults to `50 || document.body`)\n
     * @param {Boolean} returnEl (optional) `true` to return a Ext.Element object instead of DOM node.\n
     * @return {HTMLElement/null} The matching DOM node (or `null` if no match was found).\n
     */\n
    findParent: function(simpleSelector, maxDepth, returnEl) {\n
        var p = this.dom,\n
            b = document.body,\n
            depth = 0,\n
            stopEl;\n
\n
        maxDepth = maxDepth || 50;\n
        if (isNaN(maxDepth)) {\n
            stopEl = Ext.getDom(maxDepth);\n
            maxDepth = Number.MAX_VALUE;\n
        }\n
        while (p && p.nodeType == 1 && depth < maxDepth && p != b && p != stopEl) {\n
            if (Ext.DomQuery.is(p, simpleSelector)) {\n
                return returnEl ? Ext.get(p) : p;\n
            }\n
            depth++;\n
            p = p.parentNode;\n
        }\n
        return null;\n
    },\n
\n
    /**\n
     * Looks at parent nodes for a match of the passed simple selector (e.g. \'div.some-class\' or \'span:first-child\').\n
     * @param {String} selector The simple selector to test.\n
     * @param {Number/String/HTMLElement/Ext.Element} maxDepth (optional)\n
     * The max depth to search as a number or element (defaults to `10 || document.body`).\n
     * @param {Boolean} returnEl (optional) `true` to return a Ext.Element object instead of DOM node.\n
     * @return {HTMLElement/null} The matching DOM node (or `null` if no match was found).\n
     */\n
    findParentNode: function(simpleSelector, maxDepth, returnEl) {\n
        var p = Ext.fly(this.dom.parentNode, \'_internal\');\n
        return p ? p.findParent(simpleSelector, maxDepth, returnEl) : null;\n
    },\n
\n
    /**\n
     * Walks up the dom looking for a parent node that matches the passed simple selector (e.g. \'div.some-class\' or \'span:first-child\').\n
     * This is a shortcut for `findParentNode()` that always returns an Ext.dom.Element.\n
     * @param {String} selector The simple selector to test\n
     * @param {Number/String/HTMLElement/Ext.Element} maxDepth (optional)\n
     * The max depth to search as a number or element (defaults to `10 || document.body`).\n
     * @return {Ext.dom.Element/null} The matching DOM node (or `null` if no match was found).\n
     */\n
    up: function(simpleSelector, maxDepth) {\n
        return this.findParentNode(simpleSelector, maxDepth, true);\n
    },\n
\n
    select: function(selector, composite) {\n
        return Ext.dom.Element.select(selector, this.dom, composite);\n
    },\n
\n
    /**\n
     * Selects child nodes based on the passed CSS selector (the selector should not contain an id).\n
     * @param {String} selector The CSS selector.\n
     * @return {HTMLElement[]} An array of the matched nodes.\n
     */\n
    query: function(selector) {\n
        return Ext.DomQuery.select(selector, this.dom);\n
    },\n
\n
    /**\n
     * Selects a single child at any depth below this element based on the passed CSS selector (the selector should not contain an id).\n
     * @param {String} selector The CSS selector.\n
     * @param {Boolean} [returnDom=false] (optional) `true` to return the DOM node instead of Ext.dom.Element.\n
     * @return {HTMLElement/Ext.dom.Element} The child Ext.dom.Element (or DOM node if `returnDom` is `true`).\n
     */\n
    down: function(selector, returnDom) {\n
        var n = Ext.DomQuery.selectNode(selector, this.dom);\n
        return returnDom ? n : Ext.get(n);\n
    },\n
\n
    /**\n
     * Selects a single *direct* child based on the passed CSS selector (the selector should not contain an id).\n
     * @param {String} selector The CSS selector.\n
     * @param {Boolean} [returnDom=false] (optional) `true` to return the DOM node instead of Ext.dom.Element.\n
     * @return {HTMLElement/Ext.dom.Element} The child Ext.dom.Element (or DOM node if `returnDom` is `true`)\n
     */\n
    child: function(selector, returnDom) {\n
        var node,\n
            me = this,\n
            id;\n
        id = Ext.get(me).id;\n
        // Escape . or :\n
        id = id.replace(/[\\.:]/g, "\\\\$0");\n
        node = Ext.DomQuery.selectNode(\'#\' + id + " > " + selector, me.dom);\n
        return returnDom ? node : Ext.get(node);\n
    },\n
\n
     /**\n
     * Gets the parent node for this element, optionally chaining up trying to match a selector.\n
     * @param {String} selector (optional) Find a parent node that matches the passed simple selector.\n
     * @param {Boolean} returnDom (optional) `true` to return a raw DOM node instead of an Ext.dom.Element.\n
     * @return {Ext.dom.Element/HTMLElement/null} The parent node or `null`.\n
     */\n
    parent: function(selector, returnDom) {\n
        return this.matchNode(\'parentNode\', \'parentNode\', selector, returnDom);\n
    },\n
\n
     /**\n
     * Gets the next sibling, skipping text nodes.\n
     * @param {String} selector (optional) Find the next sibling that matches the passed simple selector.\n
     * @param {Boolean} returnDom (optional) `true` to return a raw dom node instead of an Ext.dom.Element.\n
     * @return {Ext.dom.Element/HTMLElement/null} The next sibling or `null`.\n
     */\n
    next: function(selector, returnDom) {\n
        return this.matchNode(\'nextSibling\', \'nextSibling\', selector, returnDom);\n
    },\n
\n
    /**\n
     * Gets the previous sibling, skipping text nodes.\n
     * @param {String} selector (optional) Find the previous sibling that matches the passed simple selector.\n
     * @param {Boolean} returnDom (optional) `true` to return a raw DOM node instead of an Ext.dom.Element\n
     * @return {Ext.dom.Element/HTMLElement/null} The previous sibling or `null`.\n
     */\n
    prev: function(selector, returnDom) {\n
        return this.matchNode(\'previousSibling\', \'previousSibling\', selector, returnDom);\n
    },\n
\n
\n
    /**\n
     * Gets the first child, skipping text nodes.\n
     * @param {String} selector (optional) Find the next sibling that matches the passed simple selector.\n
     * @param {Boolean} returnDom (optional) `true` to return a raw DOM node instead of an Ext.dom.Element.\n
     * @return {Ext.dom.Element/HTMLElement/null} The first child or `null`.\n
     */\n
    first: function(selector, returnDom) {\n
        return this.matchNode(\'nextSibling\', \'firstChild\', selector, returnDom);\n
    },\n
\n
    /**\n
     * Gets the last child, skipping text nodes.\n
     * @param {String} selector (optional) Find the previous sibling that matches the passed simple selector.\n
     * @param {Boolean} returnDom (optional) `true` to return a raw DOM node instead of an Ext.dom.Element.\n
     * @return {Ext.dom.Element/HTMLElement/null} The last child or `null`.\n
     */\n
    last: function(selector, returnDom) {\n
        return this.matchNode(\'previousSibling\', \'lastChild\', selector, returnDom);\n
    },\n
\n
    matchNode: function(dir, start, selector, returnDom) {\n
        if (!this.dom) {\n
            return null;\n
        }\n
\n
        var n = this.dom[start];\n
        while (n) {\n
            if (n.nodeType == 1 && (!selector || Ext.DomQuery.is(n, selector))) {\n
                return !returnDom ? Ext.get(n) : n;\n
            }\n
            n = n[dir];\n
        }\n
        return null;\n
    },\n
\n
    isAncestor: function(element) {\n
        return this.self.isAncestor.call(this.self, this.dom, element);\n
    }\n
});\n
\n
//@tag dom,core\n
//@require Ext.Element-all\n
\n
/**\n
 * This class encapsulates a *collection* of DOM elements, providing methods to filter members, or to perform collective\n
 * actions upon the whole set.\n
 *\n
 * Although they are not listed, this class supports all of the methods of {@link Ext.dom.Element} and\n
 * {@link Ext.Anim}. The methods from these classes will be performed on all the elements in this collection.\n
 *\n
 * Example:\n
 *\n
 *     var els = Ext.select("#some-el div.some-class");\n
 *     // or select directly from an existing element\n
 *     var el = Ext.get(\'some-el\');\n
 *     el.select(\'div.some-class\');\n
 *\n
 *     els.setWidth(100); // all elements become 100 width\n
 *     els.hide(true); // all elements fade out and hide\n
 *     // or\n
 *     els.setWidth(100).hide(true);\n
 *\n
 * @mixins Ext.dom.Element\n
 */\n
Ext.define(\'Ext.dom.CompositeElementLite\', {\n
    alternateClassName: [\'Ext.CompositeElementLite\', \'Ext.CompositeElement\'],\n
\n
    requires: [\'Ext.dom.Element\'],\n
    \n
    // We use the @mixins tag above to document that CompositeElement has\n
    // all the same methods as Element, but the @mixins tag also pulls in\n
    // configs and properties which we don\'t want, so hide them explicitly:\n
    /** @cfg bubbleEvents @hide */\n
    /** @cfg listeners @hide */\n
    /** @property DISPLAY @hide */\n
    /** @property OFFSETS @hide */\n
    /** @property VISIBILITY @hide */\n
    /** @property defaultUnit @hide */\n
    /** @property dom @hide */\n
    /** @property id @hide */\n
    // Also hide the static #get method that also gets inherited\n
    /** @method get @static @hide */\n
\n
    statics: {\n
        /**\n
         * @private\n
         * @static\n
         * Copies all of the functions from Ext.dom.Element\'s prototype onto CompositeElementLite\'s prototype.\n
         */\n
        importElementMethods: function() {\n
\n
        }\n
    },\n
\n
    constructor: function(elements, root) {\n
        /**\n
         * @property {HTMLElement[]} elements\n
         * @readonly\n
         * The Array of DOM elements which this CompositeElement encapsulates.\n
         *\n
         * This will not *usually* be accessed in developers\' code, but developers wishing to augment the capabilities\n
         * of the CompositeElementLite class may use it when adding methods to the class.\n
         *\n
         * For example to add the `nextAll` method to the class to **add** all following siblings of selected elements,\n
         * the code would be\n
         *\n
         *     Ext.override(Ext.dom.CompositeElementLite, {\n
         *         nextAll: function() {\n
         *             var elements = this.elements, i, l = elements.length, n, r = [], ri = -1;\n
         *\n
         *             // Loop through all elements in this Composite, accumulating\n
         *             // an Array of all siblings.\n
         *             for (i = 0; i < l; i++) {\n
         *                 for (n = elements[i].nextSibling; n; n = n.nextSibling) {\n
         *                     r[++ri] = n;\n
         *                 }\n
         *             }\n
         *\n
         *             // Add all found siblings to this Composite\n
         *             return this.add(r);\n
         *         }\n
         *     });\n
         */\n
        this.elements = [];\n
        this.add(elements, root);\n
        this.el = new Ext.dom.Element.Fly();\n
    },\n
\n
    isComposite: true,\n
\n
    // @private\n
    getElement: function(el) {\n
        // Set the shared flyweight dom property to the current element\n
        return this.el.attach(el).synchronize();\n
    },\n
\n
    // @private\n
    transformElement: function(el) {\n
        return Ext.getDom(el);\n
    },\n
\n
    /**\n
     * Returns the number of elements in this Composite.\n
     * @return {Number}\n
     */\n
    getCount: function() {\n
        return this.elements.length;\n
    },\n
\n
    /**\n
     * Adds elements to this Composite object.\n
     * @param {HTMLElement[]/Ext.dom.CompositeElementLite} els Either an Array of DOM elements to add, or another Composite\n
     * object who\'s elements should be added.\n
     * @param {HTMLElement/String} [root] The root element of the query or id of the root.\n
     * @return {Ext.dom.CompositeElementLite} This Composite object.\n
     */\n
    add: function(els, root) {\n
        var elements = this.elements,\n
            i, ln;\n
\n
        if (!els) {\n
            return this;\n
        }\n
\n
        if (typeof els == "string") {\n
            els = Ext.dom.Element.selectorFunction(els, root);\n
        }\n
        else if (els.isComposite) {\n
            els = els.elements;\n
        }\n
        else if (!Ext.isIterable(els)) {\n
            els = [els];\n
        }\n
\n
        for (i = 0, ln = els.length; i < ln; ++i) {\n
            elements.push(this.transformElement(els[i]));\n
        }\n
\n
        return this;\n
    },\n
\n
    invoke: function(fn, args) {\n
        var elements = this.elements,\n
            ln = elements.length,\n
            element,\n
            i;\n
\n
        for (i = 0; i < ln; i++) {\n
            element = elements[i];\n
\n
            if (element) {\n
                Ext.dom.Element.prototype[fn].apply(this.getElement(element), args);\n
            }\n
        }\n
        return this;\n
    },\n
\n
    /**\n
     * Returns a flyweight Element of the dom element object at the specified index.\n
     * @param {Number} index\n
     * @return {Ext.dom.Element}\n
     */\n
    item: function(index) {\n
        var el = this.elements[index],\n
            out = null;\n
\n
        if (el) {\n
            out = this.getElement(el);\n
        }\n
\n
        return out;\n
    },\n
\n
    // fixes scope with flyweight.\n
    addListener: function(eventName, handler, scope, opt) {\n
        var els = this.elements,\n
                len = els.length,\n
                i, e;\n
\n
        for (i = 0; i < len; i++) {\n
            e = els[i];\n
            if (e) {\n
                e.on(eventName, handler, scope || e, opt);\n
            }\n
        }\n
        return this;\n
    },\n
    /**\n
     * Calls the passed function for each element in this composite.\n
     * @param {Function} fn The function to call.\n
     * @param {Ext.dom.Element} fn.el The current Element in the iteration. **This is the flyweight\n
     * (shared) Ext.dom.Element instance, so if you require a a reference to the dom node, use el.dom.**\n
     * @param {Ext.dom.CompositeElementLite} fn.c This Composite object.\n
     * @param {Number} fn.index The zero-based index in the iteration.\n
     * @param {Object} [scope] The scope (this reference) in which the function is executed.\n
     * Defaults to the Element.\n
     * @return {Ext.dom.CompositeElementLite} this\n
     */\n
    each: function(fn, scope) {\n
        var me = this,\n
                els = me.elements,\n
                len = els.length,\n
                i, e;\n
\n
        for (i = 0; i < len; i++) {\n
            e = els[i];\n
            if (e) {\n
                e = this.getElement(e);\n
                if (fn.call(scope || e, e, me, i) === false) {\n
                    break;\n
                }\n
            }\n
        }\n
        return me;\n
    },\n
\n
    /**\n
     * Clears this Composite and adds the elements passed.\n
     * @param {HTMLElement[]/Ext.dom.CompositeElementLite} els Either an array of DOM elements, or another Composite from which\n
     * to fill this Composite.\n
     * @return {Ext.dom.CompositeElementLite} this\n
     */\n
    fill: function(els) {\n
        var me = this;\n
        me.elements = [];\n
        me.add(els);\n
        return me;\n
    },\n
\n
    /**\n
     * Filters this composite to only elements that match the passed selector.\n
     * @param {String/Function} selector A string CSS selector or a comparison function. The comparison function will be\n
     * called with the following arguments:\n
     * @param {Ext.dom.Element} selector.el The current DOM element.\n
     * @param {Number} selector.index The current index within the collection.\n
     * @return {Ext.dom.CompositeElementLite} this\n
     */\n
    filter: function(selector) {\n
        var els = [],\n
                me = this,\n
                fn = Ext.isFunction(selector) ? selector\n
                        : function(el) {\n
                    return el.is(selector);\n
                };\n
\n
        me.each(function(el, self, i) {\n
            if (fn(el, i) !== false) {\n
                els[els.length] = me.transformElement(el);\n
            }\n
        });\n
\n
        me.elements = els;\n
        return me;\n
    },\n
\n
    /**\n
     * Find the index of the passed element within the composite collection.\n
     * @param {String/HTMLElement/Ext.Element/Number} el The id of an element, or an Ext.dom.Element, or an HtmlElement\n
     * to find within the composite collection.\n
     * @return {Number} The index of the passed Ext.dom.Element in the composite collection, or -1 if not found.\n
     */\n
    indexOf: function(el) {\n
        return Ext.Array.indexOf(this.elements, this.transformElement(el));\n
    },\n
\n
    /**\n
     * Replaces the specified element with the passed element.\n
     * @param {String/HTMLElement/Ext.Element/Number} el The id of an element, the Element itself, the index of the\n
     * element in this composite to replace.\n
     * @param {String/Ext.Element} replacement The id of an element or the Element itself.\n
     * @param {Boolean} [domReplace] `true` to remove and replace the element in the document too.\n
     * @return {Ext.dom.CompositeElementLite} this\n
     */\n
    replaceElement: function(el, replacement, domReplace) {\n
        var index = !isNaN(el) ? el : this.indexOf(el),\n
                d;\n
        if (index > -1) {\n
            replacement = Ext.getDom(replacement);\n
            if (domReplace) {\n
                d = this.elements[index];\n
                d.parentNode.insertBefore(replacement, d);\n
                Ext.removeNode(d);\n
            }\n
            Ext.Array.splice(this.elements, index, 1, replacement);\n
        }\n
        return this;\n
    },\n
\n
    /**\n
     * Removes all elements.\n
     */\n
    clear: function() {\n
        this.elements = [];\n
    },\n
\n
    addElements: function(els, root) {\n
        if (!els) {\n
            return this;\n
        }\n
\n
        if (typeof els == "string") {\n
            els = Ext.dom.Element.selectorFunction(els, root);\n
        }\n
\n
        var yels = this.elements;\n
\n
        Ext.each(els, function(e) {\n
            yels.push(Ext.get(e));\n
        });\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Returns the first Element\n
     * @return {Ext.dom.Element}\n
     */\n
    first: function() {\n
        return this.item(0);\n
    },\n
\n
    /**\n
     * Returns the last Element\n
     * @return {Ext.dom.Element}\n
     */\n
    last: function() {\n
        return this.item(this.getCount() - 1);\n
    },\n
\n
    /**\n
     * Returns `true` if this composite contains the passed element\n
     * @param {String/HTMLElement/Ext.Element/Number} el The id of an element, or an Ext.Element, or an HtmlElement to\n
     * find within the composite collection.\n
     * @return {Boolean}\n
     */\n
    contains: function(el) {\n
        return this.indexOf(el) != -1;\n
    },\n
\n
    /**\n
     * Removes the specified element(s).\n
     * @param {String/HTMLElement/Ext.Element/Number} el The id of an element, the Element itself, the index of the\n
     * element in this composite or an array of any of those.\n
     * @param {Boolean} [removeDom] `true` to also remove the element from the document\n
     * @return {Ext.dom.CompositeElementLite} this\n
     */\n
    removeElement: function(keys, removeDom) {\n
        var me = this,\n
                elements = this.elements,\n
                el;\n
\n
        Ext.each(keys, function(val) {\n
            if ((el = (elements[val] || elements[val = me.indexOf(val)]))) {\n
                if (removeDom) {\n
                    if (el.dom) {\n
                        el.remove();\n
                    }\n
                    else {\n
                        Ext.removeNode(el);\n
                    }\n
                }\n
                Ext.Array.erase(elements, val, 1);\n
            }\n
        });\n
\n
        return this;\n
    }\n
\n
}, function() {\n
    var Element = Ext.dom.Element,\n
        elementPrototype = Element.prototype,\n
        prototype = this.prototype,\n
        name;\n
\n
    for (name in elementPrototype) {\n
        if (typeof elementPrototype[name] == \'function\'){\n
            (function(key) {\n
                prototype[key] = prototype[key] || function() {\n
                    return this.invoke(key, arguments);\n
                };\n
            }).call(prototype, name);\n
        }\n
    }\n
\n
    prototype.on = prototype.addListener;\n
\n
    if (Ext.DomQuery){\n
        Element.selectorFunction = Ext.DomQuery.select;\n
    }\n
\n
    /**\n
     * Selects elements based on the passed CSS selector to enable {@link Ext.Element Element} methods\n
     * to be applied to many related elements in one statement through the returned\n
     * {@link Ext.dom.CompositeElementLite CompositeElementLite} object.\n
     * @param {String/HTMLElement[]} selector The CSS selector or an array of elements\n
     * @param {HTMLElement/String} [root] The root element of the query or id of the root\n
     * @return {Ext.dom.CompositeElementLite}\n
     * @member Ext.dom.Element\n
     * @method select\n
     */\n
   Element.select = function(selector, root) {\n
        var elements;\n
\n
        if (typeof selector == "string") {\n
            elements = Element.selectorFunction(selector, root);\n
        }\n
        else if (selector.length !== undefined) {\n
            elements = selector;\n
        }\n
        else {\n
            //<debug>\n
            throw new Error("[Ext.select] Invalid selector specified: " + selector);\n
            //</debug>\n
        }\n
\n
        return new Ext.CompositeElementLite(elements);\n
    };\n
\n
    /**\n
     * @member Ext\n
     * @method select\n
     * @alias Ext.dom.Element#select\n
     */\n
    Ext.select = function() {\n
        return Element.select.apply(Element, arguments);\n
    };\n
});\n
\n
Ext.ClassManager.addNameAlternateMappings({\n
  "Ext.app.Profile": [],\n
  "Ext.event.recognizer.MultiTouch": [],\n
  "Ext.fx.Runner": [],\n
  "Ext.chart.grid.CircularGrid": [],\n
  "Ext.mixin.Templatable": [],\n
  "Ext.event.recognizer.Pinch": [],\n
  "Ext.util.Format": [],\n
  "Ext.direct.JsonProvider": [],\n
  "Ext.data.identifier.Simple": [],\n
  "Ext.dataview.DataView": [\n
    "Ext.DataView"\n
  ],\n
  "Ext.field.Hidden": [\n
    "Ext.form.Hidden"\n
  ],\n
  "Ext.field.Number": [\n
    "Ext.form.Number"\n
  ],\n
  "Ext.chart.series.CandleStick": [],\n
  "Ext.device.Connection": [],\n
  "Ext.data.Model": [\n
    "Ext.data.Record"\n
  ],\n
  "Ext.data.reader.Reader": [\n
    "Ext.data.Reader",\n
    "Ext.data.DataReader"\n
  ],\n
  "Ext.Sheet": [],\n
  "Ext.tab.Tab": [\n
    "Ext.Tab"\n
  ],\n
  "Ext.chart.series.sprite.StackedCartesian": [],\n
  "Ext.util.Grouper": [],\n
  "Ext.util.translatable.CssPosition": [],\n
  "Ext.util.paintmonitor.Abstract": [],\n
  "Ext.direct.RemotingProvider": [],\n
  "Ext.data.NodeInterface": [\n
    "Ext.data.Node"\n
  ],\n
  "Ext.chart.interactions.PanZoom": [],\n
  "Ext.util.PositionMap": [],\n
  "Ext.chart.series.ItemPublisher": [],\n
  "Ext.util.Sortable": [],\n
  "Ext.chart.series.sprite.AbstractRadial": [],\n
  "Ext.fx.runner.Css": [],\n
  "Ext.fx.runner.CssTransition": [],\n
  "Ext.draw.Group": [],\n
  "Ext.XTemplateCompiler": [],\n
  "Ext.util.Wrapper": [],\n
  "Ext.app.Router": [],\n
  "Ext.direct.Transaction": [\n
    "Ext.Direct.Transaction"\n
  ],\n
  "Ext.util.Offset": [],\n
  "Ext.device.device.Abstract": [],\n
  "Ext.mixin.Mixin": [],\n
  "Ext.fx.animation.FadeOut": [],\n
  "Ext.util.Geolocation": [\n
    "Ext.util.GeoLocation"\n
  ],\n
  "Ext.ComponentManager": [\n
    "Ext.ComponentMgr"\n
  ],\n
  "Ext.util.sizemonitor.OverflowChange": [],\n
  "Ext.event.publisher.ElementSize": [],\n
  "Ext.tab.Bar": [\n
    "Ext.TabBar"\n
  ],\n
  "Ext.event.Dom": [],\n
  "Ext.app.Application": [],\n
  "Ext.dataview.List": [\n
    "Ext.List"\n
  ],\n
  "Ext.util.translatable.Dom": [],\n
  "Ext.fx.layout.card.Scroll": [],\n
  "Ext.draw.LimitedCache": [],\n
  "Ext.device.geolocation.Sencha": [],\n
  "Ext.dataview.ListItemHeader": [],\n
  "Ext.event.publisher.TouchGesture": [],\n
  "Ext.data.SortTypes": [],\n
  "Ext.device.contacts.Abstract": [],\n
  "Ext.device.push.Sencha": [],\n
  "Ext.fx.animation.WipeOut": [],\n
  "Ext.slider.Slider": [],\n
  "Ext.Component": [\n
    "Ext.lib.Component"\n
  ],\n
  "Ext.device.communicator.Default": [],\n
  "Ext.fx.runner.CssAnimation": [],\n
  "Ext.chart.axis.Axis": [],\n
  "Ext.fx.animation.Cube": [],\n
  "Ext.chart.Markers": [],\n
  "Ext.chart.series.sprite.Radar": [],\n
  "Ext.device.device.Simulator": [],\n
  "Ext.Ajax": [],\n
  "Ext.dataview.component.ListItem": [],\n
  "Ext.util.Filter": [],\n
  "Ext.layout.wrapper.Inner": [],\n
  "Ext.draw.Animator": [],\n
  "Ext.device.geolocation.Simulator": [],\n
  "Ext.data.association.BelongsTo": [\n
    "Ext.data.BelongsToAssociation"\n
  ],\n
  "Ext.draw.Surface": [],\n
  "Ext.scroll.indicator.ScrollPosition": [],\n
  "Ext.field.Email": [\n
    "Ext.form.Email"\n
  ],\n
  "Ext.fx.layout.card.Abstract": [],\n
  "Ext.event.Controller": [],\n
  "Ext.dataview.component.Container": [],\n
  "Ext.log.writer.Remote": [],\n
  "Ext.fx.layout.card.Style": [],\n
  "Ext.device.purchases.Sencha": [],\n
  "Ext.chart.axis.segmenter.Segmenter": [],\n
  "Ext.viewport.Android": [],\n
  "Ext.log.formatter.Identity": [],\n
  "Ext.chart.interactions.ItemHighlight": [],\n
  "Ext.picker.Picker": [\n
    "Ext.Picker"\n
  ],\n
  "Ext.data.Batch": [],\n
  "Ext.draw.modifier.Animation": [],\n
  "Ext.chart.AbstractChart": [],\n
  "Ext.tab.Panel": [\n
    "Ext.TabPanel"\n
  ],\n
  "Ext.draw.Path": [],\n
  "Ext.scroll.indicator.Throttled": [],\n
  "Ext.fx.animation.SlideOut": [],\n
  "Ext.device.connection.Sencha": [],\n
  "Ext.fx.layout.card.Pop": [],\n
  "Ext.chart.axis.layout.Discrete": [],\n
  "Ext.data.Field": [],\n
  "Ext.chart.series.Gauge": [],\n
  "Ext.data.StoreManager": [\n
    "Ext.StoreMgr",\n
    "Ext.data.StoreMgr",\n
    "Ext.StoreManager"\n
  ],\n
  "Ext.fx.animation.PopOut": [],\n
  "Ext.chart.label.Callout": [],\n
  "Ext.device.push.Abstract": [],\n
  "Ext.util.DelayedTask": [],\n
  "Ext.fx.easing.Momentum": [],\n
  "Ext.fx.easing.Abstract": [],\n
  "Ext.Title": [],\n
  "Ext.event.recognizer.Drag": [],\n
  "Ext.field.TextArea": [\n
    "Ext.form.TextArea"\n
  ],\n
  "Ext.fx.Easing": [],\n
  "Ext.chart.series.sprite.Scatter": [],\n
  "Ext.data.reader.Array": [\n
    "Ext.data.ArrayReader"\n
  ],\n
  "Ext.picker.Date": [\n
    "Ext.DatePicker"\n
  ],\n
  "Ext.data.proxy.JsonP": [\n
    "Ext.data.ScriptTagProxy"\n
  ],\n
  "Ext.device.communicator.Android": [],\n
  "Ext.chart.series.Area": [],\n
  "Ext.device.device.PhoneGap": [],\n
  "Ext.field.Checkbox": [\n
    "Ext.form.Checkbox"\n
  ],\n
  "Ext.chart.Legend": [],\n
  "Ext.Media": [],\n
  "Ext.TitleBar": [],\n
  "Ext.chart.interactions.RotatePie3D": [],\n
  "Ext.draw.gradient.Linear": [],\n
  "Ext.util.TapRepeater": [],\n
  "Ext.event.Touch": [],\n
  "Ext.mixin.Bindable": [],\n
  "Ext.data.proxy.Server": [\n
    "Ext.data.ServerProxy"\n
  ],\n
  "Ext.chart.series.Cartesian": [],\n
  "Ext.util.sizemonitor.Scroll": [],\n
  "Ext.data.ResultSet": [],\n
  "Ext.data.association.HasMany": [\n
    "Ext.data.HasManyAssociation"\n
  ],\n
  "Ext.draw.TimingFunctions": [],\n
  "Ext.draw.engine.Canvas": [],\n
  "Ext.data.proxy.Ajax": [\n
    "Ext.data.HttpProxy",\n
    "Ext.data.AjaxProxy"\n
  ],\n
  "Ext.fx.animation.Fade": [\n
    "Ext.fx.animation.FadeIn"\n
  ],\n
  "Ext.layout.Default": [],\n
  "Ext.util.paintmonitor.CssAnimation": [],\n
  "Ext.data.writer.Writer": [\n
    "Ext.data.DataWriter",\n
    "Ext.data.Writer"\n
  ],\n
  "Ext.event.recognizer.Recognizer": [],\n
  "Ext.form.FieldSet": [],\n
  "Ext.scroll.Indicator": [\n
    "Ext.util.Indicator"\n
  ],\n
  "Ext.XTemplateParser": [],\n
  "Ext.behavior.Scrollable": [],\n
  "Ext.chart.series.sprite.CandleStick": [],\n
  "Ext.data.JsonP": [\n
    "Ext.util.JSONP"\n
  ],\n
  "Ext.device.connection.PhoneGap": [],\n
  "Ext.event.publisher.Dom": [],\n
  "Ext.fx.layout.card.Fade": [],\n
  "Ext.app.Controller": [],\n
  "Ext.fx.State": [],\n
  "Ext.layout.wrapper.BoxDock": [],\n
  "Ext.chart.series.sprite.Pie3DPart": [],\n
  "Ext.viewport.Default": [],\n
  "Ext.layout.HBox": [],\n
  "Ext.ux.auth.model.Session": [],\n
  "Ext.scroll.indicator.Default": [],\n
  "Ext.data.ModelManager": [\n
    "Ext.ModelMgr",\n
    "Ext.ModelManager"\n
  ],\n
  "Ext.data.Validations": [\n
    "Ext.data.validations"\n
  ],\n
  "Ext.util.translatable.Abstract": [],\n
  "Ext.scroll.indicator.Abstract": [],\n
  "Ext.Button": [],\n
  "Ext.field.Radio": [\n
    "Ext.form.Radio"\n
  ],\n
  "Ext.util.HashMap": [],\n
  "Ext.field.Input": [],\n
  "Ext.device.Camera": [],\n
  "Ext.mixin.Filterable": [],\n
  "Ext.draw.TextMeasurer": [],\n
  "Ext.dataview.element.Container": [],\n
  "Ext.chart.series.sprite.PieSlice": [],\n
  "Ext.data.Connection": [],\n
  "Ext.direct.ExceptionEvent": [],\n
  "Ext.Panel": [\n
    "Ext.lib.Panel"\n
  ],\n
  "Ext.data.association.HasOne": [\n
    "Ext.data.HasOneAssociation"\n
  ],\n
  "Ext.device.geolocation.Abstract": [],\n
  "Ext.ActionSheet": [],\n
  "Ext.layout.Box": [],\n
  "Ext.bb.CrossCut": [],\n
  "Ext.Video": [],\n
  "Ext.ux.auth.Session": [],\n
  "Ext.chart.series.Line": [],\n
  "Ext.fx.layout.card.Cube": [],\n
  "Ext.event.recognizer.HorizontalSwipe": [],\n
  "Ext.data.writer.Json": [\n
    "Ext.data.JsonWriter"\n
  ],\n
  "Ext.layout.Fit": [],\n
  "Ext.fx.animation.Slide": [\n
    "Ext.fx.animation.SlideIn"\n
  ],\n
  "Ext.device.Purchases.Purchase": [],\n
  "Ext.table.Row": [],\n
  "Ext.log.formatter.Formatter": [],\n
  "Ext.Container": [\n
    "Ext.lib.Container"\n
  ],\n
  "Ext.fx.animation.Pop": [\n
    "Ext.fx.animation.PopIn"\n
  ],\n
  "Ext.draw.sprite.Circle": [],\n
  "Ext.fx.layout.card.Reveal": [],\n
  "Ext.fx.layout.card.Cover": [],\n
  "Ext.log.Base": [],\n
  "Ext.data.reader.Xml": [\n
    "Ext.data.XmlReader"\n
  ],\n
  "Ext.event.publisher.ElementPaint": [],\n
  "Ext.chart.axis.Category": [],\n
  "Ext.data.reader.Json": [\n
    "Ext.data.JsonReader"\n
  ],\n
  "Ext.Decorator": [],\n
  "Ext.data.TreeStore": [],\n
  "Ext.device.Purchases": [],\n
  "Ext.device.orientation.HTML5": [],\n
  "Ext.draw.gradient.Gradient": [],\n
  "Ext.event.recognizer.DoubleTap": [],\n
  "Ext.log.Logger": [],\n
  "Ext.picker.Slot": [\n
    "Ext.Picker.Slot"\n
  ],\n
  "Ext.device.notification.Simulator": [],\n
  "Ext.field.Field": [\n
    "Ext.form.Field"\n
  ],\n
  "Ext.log.filter.Priority": [],\n
  "Ext.util.sizemonitor.Abstract": [],\n
  "Ext.chart.series.sprite.Polar": [],\n
  "Ext.util.paintmonitor.OverflowChange": [],\n
  "Ext.util.LineSegment": [],\n
  "Ext.SegmentedButton": [],\n
  "Ext.Sortable": [],\n
  "Ext.fx.easing.Linear": [],\n
  "Ext.chart.series.sprite.Aggregative": [],\n
  "Ext.dom.CompositeElement": [\n
    "Ext.CompositeElement"\n
  ],\n
  "Ext.data.identifier.Uuid": [],\n
  "Ext.data.proxy.Client": [\n
    "Ext.proxy.ClientProxy"\n
  ],\n
  "Ext.fx.easing.Bounce": [],\n
  "Ext.data.Types": [],\n
  "Ext.chart.series.sprite.Cartesian": [],\n
  "Ext.app.Action": [],\n
  "Ext.util.Translatable": [],\n
  "Ext.device.camera.PhoneGap": [],\n
  "Ext.draw.sprite.Path": [],\n
  "Ext.LoadMask": [],\n
  "Ext.data.association.Association": [\n
    "Ext.data.Association"\n
  ],\n
  "Ext.chart.axis.sprite.Axis": [],\n
  "Ext.behavior.Draggable": [],\n
  "Ext.chart.grid.RadialGrid": [],\n
  "Ext.util.TranslatableGroup": [],\n
  "Ext.fx.Animation": [],\n
  "Ext.draw.sprite.Ellipse": [],\n
  "Ext.util.Inflector": [],\n
  "Ext.Map": [],\n
  "Ext.XTemplate": [],\n
  "Ext.data.NodeStore": [],\n
  "Ext.draw.sprite.AttributeParser": [],\n
  "Ext.form.Panel": [\n
    "Ext.form.FormPanel"\n
  ],\n
  "Ext.chart.series.Series": [],\n
  "Ext.data.Request": [],\n
  "Ext.draw.sprite.Text": [],\n
  "Ext.layout.Float": [],\n
  "Ext.dataview.component.DataItem": [],\n
  "Ext.chart.CartesianChart": [\n
    "Ext.chart.Chart"\n
  ],\n
  "Ext.data.proxy.WebStorage": [\n
    "Ext.data.WebStorageProxy"\n
  ],\n
  "Ext.log.writer.Writer": [],\n
  "Ext.device.Communicator": [],\n
  "Ext.fx.animation.Flip": [],\n
  "Ext.util.Point": [],\n
  "Ext.chart.series.StackedCartesian": [],\n
  "Ext.fx.layout.card.Slide": [],\n
  "Ext.Anim": [],\n
  "Ext.data.DirectStore": [],\n
  "Ext.dataview.NestedList": [\n
    "Ext.NestedList"\n
  ],\n
  "Ext.app.Route": [],\n
  "Ext.device.connection.Simulator": [],\n
  "Ext.chart.PolarChart": [],\n
  "Ext.event.publisher.ComponentSize": [],\n
  "Ext.slider.Toggle": [],\n
  "Ext.data.identifier.Sequential": [],\n
  "Ext.Template": [],\n
  "Ext.AbstractComponent": [],\n
  "Ext.device.Push": [],\n
  "Ext.fx.easing.BoundMomentum": [],\n
  "Ext.viewport.Viewport": [],\n
  "Ext.chart.series.Polar": [],\n
  "Ext.event.recognizer.VerticalSwipe": [],\n
  "Ext.event.Event": [\n
    "Ext.EventObject"\n
  ],\n
  "Ext.behavior.Behavior": [],\n
  "Ext.chart.grid.VerticalGrid": [],\n
  "Ext.chart.label.Label": [],\n
  "Ext.draw.sprite.EllipticalArc": [],\n
  "Ext.fx.easing.EaseOut": [],\n
  "Ext.Toolbar": [],\n
  "Ext.event.recognizer.LongPress": [],\n
  "Ext.device.notification.Sencha": [],\n
  "Ext.chart.series.sprite.Line": [],\n
  "Ext.data.ArrayStore": [],\n
  "Ext.data.proxy.SQL": [],\n
  "Ext.mixin.Sortable": [],\n
  "Ext.fx.layout.card.Flip": [],\n
  "Ext.chart.interactions.CrossZoom": [],\n
  "Ext.event.publisher.ComponentPaint": [],\n
  "Ext.event.recognizer.Rotate": [],\n
  "Ext.util.TranslatableList": [],\n
  "Ext.carousel.Item": [],\n
  "Ext.event.recognizer.Swipe": [],\n
  "Ext.util.translatable.ScrollPosition": [],\n
  "Ext.device.camera.Simulator": [],\n
  "Ext.chart.series.sprite.Area": [],\n
  "Ext.event.recognizer.Touch": [],\n
  "Ext.plugin.ListPaging": [],\n
  "Ext.draw.sprite.Sector": [],\n
  "Ext.chart.axis.segmenter.Names": [],\n
  "Ext.mixin.Observable": [\n
    "Ext.util.Observable"\n
  ],\n
  "Ext.carousel.Infinite": [],\n
  "Ext.draw.Matrix": [],\n
  "Ext.Mask": [],\n
  "Ext.event.publisher.Publisher": [],\n
  "Ext.layout.wrapper.Dock": [],\n
  "Ext.app.History": [],\n
  "Ext.data.proxy.Direct": [\n
    "Ext.data.DirectProxy"\n
  ],\n
  "Ext.chart.axis.layout.Continuous": [],\n
  "Ext.table.Cell": [],\n
  "Ext.fx.layout.card.ScrollCover": [],\n
  "Ext.device.orientation.Sencha": [],\n
  "Ext.util.Droppable": [],\n
  "Ext.draw.sprite.Composite": [],\n
  "Ext.chart.series.Pie": [],\n
  "Ext.device.Purchases.Product": [],\n
  "Ext.device.Orientation": [],\n
  "Ext.direct.Provider": [],\n
  "Ext.draw.sprite.Arc": [],\n
  "Ext.chart.axis.segmenter.Time": [],\n
  "Ext.util.Draggable": [],\n
  "Ext.device.contacts.Sencha": [],\n
  "Ext.chart.grid.HorizontalGrid": [],\n
  "Ext.mixin.Traversable": [],\n
  "Ext.util.AbstractMixedCollection": [],\n
  "Ext.data.JsonStore": [],\n
  "Ext.draw.SegmentTree": [],\n
  "Ext.direct.RemotingEvent": [],\n
  "Ext.plugin.PullRefresh": [],\n
  "Ext.log.writer.Console": [],\n
  "Ext.field.Spinner": [\n
    "Ext.form.Spinner"\n
  ],\n
  "Ext.chart.axis.segmenter.Numeric": [],\n
  "Ext.data.proxy.LocalStorage": [\n
    "Ext.data.LocalStorageProxy"\n
  ],\n
  "Ext.fx.animation.Wipe": [\n
    "Ext.fx.animation.WipeIn"\n
  ],\n
  "Ext.fx.layout.Card": [],\n
  "Ext.TaskQueue": [],\n
  "Ext.Label": [],\n
  "Ext.util.translatable.CssTransform": [],\n
  "Ext.viewport.Ios": [],\n
  "Ext.Spacer": [],\n
  "Ext.mixin.Selectable": [],\n
  "Ext.draw.sprite.Image": [],\n
  "Ext.data.proxy.Rest": [\n
    "Ext.data.RestProxy"\n
  ],\n
  "Ext.Img": [],\n
  "Ext.chart.series.sprite.Bar": [],\n
  "Ext.log.writer.DocumentTitle": [],\n
  "Ext.data.Error": [],\n
  "Ext.util.Sorter": [],\n
  "Ext.draw.gradient.Radial": [],\n
  "Ext.layout.Abstract": [],\n
  "Ext.device.notification.Abstract": [],\n
  "Ext.log.filter.Filter": [],\n
  "Ext.device.camera.Sencha": [],\n
  "Ext.draw.sprite.Sprite": [],\n
  "Ext.draw.Color": [],\n
  "Ext.chart.series.Bar": [],\n
  "Ext.field.Slider": [\n
    "Ext.form.Slider"\n
  ],\n
  "Ext.field.Search": [\n
    "Ext.form.Search"\n
  ],\n
  "Ext.chart.series.Scatter": [],\n
  "Ext.device.Device": [],\n
  "Ext.event.Dispatcher": [],\n
  "Ext.data.Store": [],\n
  "Ext.draw.modifier.Highlight": [],\n
  "Ext.behavior.Translatable": [],\n
  "Ext.direct.Manager": [\n
    "Ext.Direct"\n
  ],\n
  "Ext.data.proxy.Proxy": [\n
    "Ext.data.DataProxy",\n
    "Ext.data.Proxy"\n
  ],\n
  "Ext.draw.modifier.Modifier": [],\n
  "Ext.navigation.View": [\n
    "Ext.NavigationView"\n
  ],\n
  "Ext.draw.modifier.Target": [],\n
  "Ext.draw.sprite.AttributeDefinition": [],\n
  "Ext.device.Notification": [],\n
  "Ext.draw.Component": [],\n
  "Ext.layout.VBox": [],\n
  "Ext.slider.Thumb": [],\n
  "Ext.MessageBox": [],\n
  "Ext.ux.Faker": [],\n
  "Ext.dataview.IndexBar": [\n
    "Ext.IndexBar"\n
  ],\n
  "Ext.dataview.element.List": [],\n
  "Ext.layout.FlexBox": [],\n
  "Ext.field.Url": [\n
    "Ext.form.Url"\n
  ],\n
  "Ext.draw.Solver": [],\n
  "Ext.data.proxy.Memory": [\n
    "Ext.data.MemoryProxy"\n
  ],\n
  "Ext.chart.axis.Time": [],\n
  "Ext.layout.Card": [],\n
  "Ext.ComponentQuery": [],\n
  "Ext.chart.series.Pie3D": [],\n
  "Ext.device.camera.Abstract": [],\n
  "Ext.device.device.Sencha": [],\n
  "Ext.scroll.View": [\n
    "Ext.util.ScrollView"\n
  ],\n
  "Ext.draw.sprite.Rect": [],\n
  "Ext.util.Region": [],\n
  "Ext.field.Select": [\n
    "Ext.form.Select"\n
  ],\n
  "Ext.draw.Draw": [],\n
  "Ext.ItemCollection": [],\n
  "Ext.log.formatter.Default": [],\n
  "Ext.navigation.Bar": [],\n
  "Ext.chart.axis.layout.CombineDuplicate": [],\n
  "Ext.device.Geolocation": [],\n
  "Ext.chart.SpaceFillingChart": [],\n
  "Ext.data.proxy.SessionStorage": [\n
    "Ext.data.SessionStorageProxy"\n
  ],\n
  "Ext.fx.easing.EaseIn": [],\n
  "Ext.draw.sprite.AnimationParser": [],\n
  "Ext.field.Password": [\n
    "Ext.form.Password"\n
  ],\n
  "Ext.device.connection.Abstract": [],\n
  "Ext.direct.Event": [],\n
  "Ext.direct.RemotingMethod": [],\n
  "Ext.Evented": [\n
    "Ext.EventedBase"\n
  ],\n
  "Ext.carousel.Indicator": [\n
    "Ext.Carousel.Indicator"\n
  ],\n
  "Ext.util.Collection": [],\n
  "Ext.chart.interactions.ItemInfo": [],\n
  "Ext.chart.MarkerHolder": [],\n
  "Ext.carousel.Carousel": [\n
    "Ext.Carousel"\n
  ],\n
  "Ext.Audio": [],\n
  "Ext.device.Contacts": [],\n
  "Ext.table.Table": [],\n
  "Ext.draw.engine.SvgContext.Gradient": [],\n
  "Ext.chart.axis.layout.Layout": [],\n
  "Ext.data.Errors": [],\n
  "Ext.field.Text": [\n
    "Ext.form.Text"\n
  ],\n
  "Ext.field.TextAreaInput": [],\n
  "Ext.field.DatePicker": [\n
    "Ext.form.DatePicker"\n
  ],\n
  "Ext.draw.engine.Svg": [],\n
  "Ext.event.recognizer.Tap": [],\n
  "Ext.device.orientation.Abstract": [],\n
  "Ext.AbstractManager": [],\n
  "Ext.chart.series.Radar": [],\n
  "Ext.chart.interactions.Abstract": [],\n
  "Ext.scroll.indicator.CssTransform": [],\n
  "Ext.util.PaintMonitor": [],\n
  "Ext.direct.PollingProvider": [],\n
  "Ext.device.notification.PhoneGap": [],\n
  "Ext.data.writer.Xml": [\n
    "Ext.data.XmlWriter"\n
  ],\n
  "Ext.event.recognizer.SingleTouch": [],\n
  "Ext.draw.sprite.Instancing": [],\n
  "Ext.event.publisher.ComponentDelegation": [],\n
  "Ext.chart.axis.Numeric": [],\n
  "Ext.field.Toggle": [\n
    "Ext.form.Toggle"\n
  ],\n
  "Ext.fx.layout.card.ScrollReveal": [],\n
  "Ext.data.Operation": [],\n
  "Ext.fx.animation.Abstract": [],\n
  "Ext.chart.interactions.Rotate": [],\n
  "Ext.draw.engine.SvgContext": [],\n
  "Ext.scroll.Scroller": [],\n
  "Ext.util.SizeMonitor": [],\n
  "Ext.event.ListenerStack": [],\n
  "Ext.util.MixedCollection": []\n
});Ext.ClassManager.addNameAliasMappings({\n
  "Ext.app.Profile": [],\n
  "Ext.event.recognizer.MultiTouch": [],\n
  "Ext.fx.Runner": [],\n
  "Ext.chart.grid.CircularGrid": [\n
    "grid.circular"\n
  ],\n
  "Ext.mixin.Templatable": [],\n
  "Ext.event.recognizer.Pinch": [],\n
  "Ext.util.Format": [],\n
  "Ext.direct.JsonProvider": [\n
    "direct.jsonprovider"\n
  ],\n
  "Ext.data.identifier.Simple": [\n
    "data.identifier.simple"\n
  ],\n
  "Ext.dataview.DataView": [\n
    "widget.dataview"\n
  ],\n
  "Ext.field.Hidden": [\n
    "widget.hiddenfield"\n
  ],\n
  "Ext.field.Number": [\n
    "widget.numberfield"\n
  ],\n
  "Ext.chart.series.CandleStick": [\n
    "series.candlestick"\n
  ],\n
  "Ext.device.Connection": [],\n
  "Ext.data.Model": [],\n
  "Ext.data.reader.Reader": [],\n
  "Ext.Sheet": [\n
    "widget.sheet"\n
  ],\n
  "Ext.tab.Tab": [\n
    "widget.tab"\n
  ],\n
  "Ext.chart.series.sprite.StackedCartesian": [],\n
  "Ext.util.Grouper": [],\n
  "Ext.util.translatable.CssPosition": [],\n
  "Ext.util.paintmonitor.Abstract": [],\n
  "Ext.direct.RemotingProvider": [\n
    "direct.remotingprovider"\n
  ],\n
  "Ext.data.NodeInterface": [],\n
  "Ext.chart.interactions.PanZoom": [\n
    "interaction.panzoom"\n
  ],\n
  "Ext.util.PositionMap": [],\n
  "Ext.chart.series.ItemPublisher": [],\n
  "Ext.util.Sortable": [],\n
  "Ext.chart.series.sprite.AbstractRadial": [],\n
  "Ext.fx.runner.Css": [],\n
  "Ext.fx.runner.CssTransition": [],\n
  "Ext.draw.Group": [],\n
  "Ext.XTemplateCompiler": [],\n
  "Ext.util.Wrapper": [],\n
  "Ext.app.Router": [],\n
  "Ext.direct.Transaction": [\n
    "direct.transaction"\n
  ],\n
  "Ext.util.Offset": [],\n
  "Ext.device.device.Abstract": [],\n
  "Ext.mixin.Mixin": [],\n
  "Ext.fx.animation.FadeOut": [\n
    "animation.fadeOut"\n
  ],\n
  "Ext.util.Geolocation": [],\n
  "Ext.ComponentManager": [],\n
  "Ext.util.sizemonitor.OverflowChange": [],\n
  "Ext.event.publisher.ElementSize": [],\n
  "Ext.tab.Bar": [\n
    "widget.tabbar"\n
  ],\n
  "Ext.event.Dom": [],\n
  "Ext.app.Application": [],\n
  "Ext.dataview.List": [\n
    "widget.list"\n
  ],\n
  "Ext.util.translatable.Dom": [],\n
  "Ext.fx.layout.card.Scroll": [\n
    "fx.layout.card.scroll"\n
  ],\n
  "Ext.draw.LimitedCache": [],\n
  "Ext.device.geolocation.Sencha": [],\n
  "Ext.dataview.ListItemHeader": [\n
    "widget.listitemheader"\n
  ],\n
  "Ext.event.publisher.TouchGesture": [],\n
  "Ext.data.SortTypes": [],\n
  "Ext.device.contacts.Abstract": [],\n
  "Ext.device.push.Sencha": [],\n
  "Ext.fx.animation.WipeOut": [],\n
  "Ext.slider.Slider": [\n
    "widget.slider"\n
  ],\n
  "Ext.Component": [\n
    "widget.component"\n
  ],\n
  "Ext.device.communicator.Default": [],\n
  "Ext.fx.runner.CssAnimation": [],\n
  "Ext.chart.axis.Axis": [\n
    "widget.axis"\n
  ],\n
  "Ext.fx.animation.Cube": [\n
    "animation.cube"\n
  ],\n
  "Ext.chart.Markers": [],\n
  "Ext.chart.series.sprite.Radar": [\n
    "sprite.radar"\n
  ],\n
  "Ext.device.device.Simulator": [],\n
  "Ext.Ajax": [],\n
  "Ext.dataview.component.ListItem": [\n
    "widget.listitem"\n
  ],\n
  "Ext.util.Filter": [],\n
  "Ext.layout.wrapper.Inner": [],\n
  "Ext.draw.Animator": [],\n
  "Ext.device.geolocation.Simulator": [],\n
  "Ext.data.association.BelongsTo": [\n
    "association.belongsto"\n
  ],\n
  "Ext.draw.Surface": [\n
    "widget.surface"\n
  ],\n
  "Ext.scroll.indicator.ScrollPosition": [],\n
  "Ext.field.Email": [\n
    "widget.emailfield"\n
  ],\n
  "Ext.fx.layout.card.Abstract": [],\n
  "Ext.event.Controller": [],\n
  "Ext.dataview.component.Container": [],\n
  "Ext.log.writer.Remote": [],\n
  "Ext.fx.layout.card.Style": [],\n
  "Ext.device.purchases.Sencha": [],\n
  "Ext.chart.axis.segmenter.Segmenter": [],\n
  "Ext.viewport.Android": [],\n
  "Ext.log.formatter.Identity": [],\n
  "Ext.chart.interactions.ItemHighlight": [\n
    "interaction.itemhighlight"\n
  ],\n
  "Ext.picker.Picker": [\n
    "widget.picker"\n
  ],\n
  "Ext.data.Batch": [],\n
  "Ext.draw.modifier.Animation": [\n
    "modifier.animation"\n
  ],\n
  "Ext.chart.AbstractChart": [],\n
  "Ext.tab.Panel": [\n
    "widget.tabpanel"\n
  ],\n
  "Ext.draw.Path": [],\n
  "Ext.scroll.indicator.Throttled": [],\n
  "Ext.fx.animation.SlideOut": [\n
    "animation.slideOut"\n
  ],\n
  "Ext.device.connection.Sencha": [],\n
  "Ext.fx.layout.card.Pop": [\n
    "fx.layout.card.pop"\n
  ],\n
  "Ext.chart.axis.layout.Discrete": [\n
    "axisLayout.discrete"\n
  ],\n
  "Ext.data.Field": [\n
    "data.field"\n
  ],\n
  "Ext.chart.series.Gauge": [\n
    "series.gauge"\n
  ],\n
  "Ext.data.StoreManager": [],\n
  "Ext.fx.animation.PopOut": [\n
    "animation.popOut"\n
  ],\n
  "Ext.chart.label.Callout": [],\n
  "Ext.device.push.Abstract": [],\n
  "Ext.util.DelayedTask": [],\n
  "Ext.fx.easing.Momentum": [],\n
  "Ext.fx.easing.Abstract": [],\n
  "Ext.Title": [\n
    "widget.title"\n
  ],\n
  "Ext.event.recognizer.Drag": [],\n
  "Ext.field.TextArea": [\n
    "widget.textareafield"\n
  ],\n
  "Ext.fx.Easing": [],\n
  "Ext.chart.series.sprite.Scatter": [\n
    "sprite.scatterSeries"\n
  ],\n
  "Ext.data.reader.Array": [\n
    "reader.array"\n
  ],\n
  "Ext.picker.Date": [\n
    "widget.datepicker"\n
  ],\n
  "Ext.data.proxy.JsonP": [\n
    "proxy.jsonp",\n
    "proxy.scripttag"\n
  ],\n
  "Ext.device.communicator.Android": [],\n
  "Ext.chart.series.Area": [\n
    "series.area"\n
  ],\n
  "Ext.device.device.PhoneGap": [],\n
  "Ext.field.Checkbox": [\n
    "widget.checkboxfield"\n
  ],\n
  "Ext.chart.Legend": [\n
    "widget.legend"\n
  ],\n
  "Ext.Media": [\n
    "widget.media"\n
  ],\n
  "Ext.TitleBar": [\n
    "widget.titlebar"\n
  ],\n
  "Ext.chart.interactions.RotatePie3D": [\n
    "interaction.rotatePie3d"\n
  ],\n
  "Ext.draw.gradient.Linear": [],\n
  "Ext.util.TapRepeater": [],\n
  "Ext.event.Touch": [],\n
  "Ext.mixin.Bindable": [],\n
  "Ext.data.proxy.Server": [\n
    "proxy.server"\n
  ],\n
  "Ext.chart.series.Cartesian": [],\n
  "Ext.util.sizemonitor.Scroll": [],\n
  "Ext.data.ResultSet": [],\n
  "Ext.data.association.HasMany": [\n
    "association.hasmany"\n
  ],\n
  "Ext.draw.TimingFunctions": [],\n
  "Ext.draw.engine.Canvas": [],\n
  "Ext.data.proxy.Ajax": [\n
    "proxy.ajax"\n
  ],\n
  "Ext.fx.animation.Fade": [\n
    "animation.fade",\n
    "animation.fadeIn"\n
  ],\n
  "Ext.layout.Default": [\n
    "layout.default",\n
    "layout.auto"\n
  ],\n
  "Ext.util.paintmonitor.CssAnimation": [],\n
  "Ext.data.writer.Writer": [\n
    "writer.base"\n
  ],\n
  "Ext.event.recognizer.Recognizer": [],\n
  "Ext.form.FieldSet": [\n
    "widget.fieldset"\n
  ],\n
  "Ext.scroll.Indicator": [],\n
  "Ext.XTemplateParser": [],\n
  "Ext.behavior.Scrollable": [],\n
  "Ext.chart.series.sprite.CandleStick": [\n
    "sprite.candlestickSeries"\n
  ],\n
  "Ext.data.JsonP": [],\n
  "Ext.device.connection.PhoneGap": [],\n
  "Ext.event.publisher.Dom": [],\n
  "Ext.fx.layout.card.Fade": [\n
    "fx.layout.card.fade"\n
  ],\n
  "Ext.app.Controller": [],\n
  "Ext.fx.State": [],\n
  "Ext.layout.wrapper.BoxDock": [],\n
  "Ext.chart.series.sprite.Pie3DPart": [\n
    "sprite.pie3dPart"\n
  ],\n
  "Ext.viewport.Default": [\n
    "widget.viewport"\n
  ],\n
  "Ext.layout.HBox": [\n
    "layout.hbox"\n
  ],\n
  "Ext.ux.auth.model.Session": [],\n
  "Ext.scroll.indicator.Default": [],\n
  "Ext.data.ModelManager": [],\n
  "Ext.data.Validations": [],\n
  "Ext.util.translatable.Abstract": [],\n
  "Ext.scroll.indicator.Abstract": [],\n
  "Ext.Button": [\n
    "widget.button"\n
  ],\n
  "Ext.field.Radio": [\n
    "widget.radiofield"\n
  ],\n
  "Ext.util.HashMap": [],\n
  "Ext.field.Input": [\n
    "widget.input"\n
  ],\n
  "Ext.device.Camera": [],\n
  "Ext.mixin.Filterable": [],\n
  "Ext.draw.TextMeasurer": [],\n
  "Ext.dataview.element.Container": [],\n
  "Ext.chart.series.sprite.PieSlice": [\n
    "sprite.pieslice"\n
  ],\n
  "Ext.data.Connection": [],\n
  "Ext.direct.ExceptionEvent": [\n
    "direct.exception"\n
  ],\n
  "Ext.Panel": [\n
    "widget.panel"\n
  ],\n
  "Ext.data.association.HasOne": [\n
    "association.hasone"\n
  ],\n
  "Ext.device.geolocation.Abstract": [],\n
  "Ext.ActionSheet": [\n
    "widget.actionsheet"\n
  ],\n
  "Ext.layout.Box": [\n
    "layout.tablebox"\n
  ],\n
  "Ext.bb.CrossCut": [\n
    "widget.crosscut"\n
  ],\n
  "Ext.Video": [\n
    "widget.video"\n
  ],\n
  "Ext.ux.auth.Session": [],\n
  "Ext.chart.series.Line": [\n
    "series.line"\n
  ],\n
  "Ext.fx.layout.card.Cube": [\n
    "fx.layout.card.cube"\n
  ],\n
  "Ext.event.recognizer.HorizontalSwipe": [],\n
  "Ext.data.writer.Json": [\n
    "writer.json"\n
  ],\n
  "Ext.layout.Fit": [\n
    "layout.fit"\n
  ],\n
  "Ext.fx.animation.Slide": [\n
    "animation.slide",\n
    "animation.slideIn"\n
  ],\n
  "Ext.device.Purchases.Purchase": [],\n
  "Ext.table.Row": [\n
    "widget.tablerow"\n
  ],\n
  "Ext.log.formatter.Formatter": [],\n
  "Ext.Container": [\n
    "widget.container"\n
  ],\n
  "Ext.fx.animation.Pop": [\n
    "animation.pop",\n
    "animation.popIn"\n
  ],\n
  "Ext.draw.sprite.Circle": [\n
    "sprite.circle"\n
  ],\n
  "Ext.fx.layout.card.Reveal": [\n
    "fx.layout.card.reveal"\n
  ],\n
  "Ext.fx.layout.card.Cover": [\n
    "fx.layout.card.cover"\n
  ],\n
  "Ext.log.Base": [],\n
  "Ext.data.reader.Xml": [\n
    "reader.xml"\n
  ],\n
  "Ext.event.publisher.ElementPaint": [],\n
  "Ext.chart.axis.Category": [\n
    "axis.category"\n
  ],\n
  "Ext.data.reader.Json": [\n
    "reader.json"\n
  ],\n
  "Ext.Decorator": [],\n
  "Ext.data.TreeStore": [\n
    "store.tree"\n
  ],\n
  "Ext.device.Purchases": [],\n
  "Ext.device.orientation.HTML5": [],\n
  "Ext.draw.gradient.Gradient": [],\n
  "Ext.event.recognizer.DoubleTap": [],\n
  "Ext.log.Logger": [],\n
  "Ext.picker.Slot": [\n
    "widget.pickerslot"\n
  ],\n
  "Ext.device.notification.Simulator": [],\n
  "Ext.field.Field": [\n
    "widget.field"\n
  ],\n
  "Ext.log.filter.Priority": [],\n
  "Ext.util.sizemonitor.Abstract": [],\n
  "Ext.chart.series.sprite.Polar": [],\n
  "Ext.util.paintmonitor.OverflowChange": [],\n
  "Ext.util.LineSegment": [],\n
  "Ext.SegmentedButton": [\n
    "widget.segmentedbutton"\n
  ],\n
  "Ext.Sortable": [],\n
  "Ext.fx.easing.Linear": [\n
    "easing.linear"\n
  ],\n
  "Ext.chart.series.sprite.Aggregative": [],\n
  "Ext.dom.CompositeElement": [],\n
  "Ext.data.identifier.Uuid": [\n
    "data.identifier.uuid"\n
  ],\n
  "Ext.data.proxy.Client": [],\n
  "Ext.fx.easing.Bounce": [],\n
  "Ext.data.Types": [],\n
  "Ext.chart.series.sprite.Cartesian": [],\n
  "Ext.app.Action": [],\n
  "Ext.util.Translatable": [],\n
  "Ext.device.camera.PhoneGap": [],\n
  "Ext.draw.sprite.Path": [\n
    "sprite.path"\n
  ],\n
  "Ext.LoadMask": [\n
    "widget.loadmask"\n
  ],\n
  "Ext.data.association.Association": [],\n
  "Ext.chart.axis.sprite.Axis": [],\n
  "Ext.behavior.Draggable": [],\n
  "Ext.chart.grid.RadialGrid": [\n
    "grid.radial"\n
  ],\n
  "Ext.util.TranslatableGroup": [],\n
  "Ext.fx.Animation": [],\n
  "Ext.draw.sprite.Ellipse": [\n
    "sprite.ellipse"\n
  ],\n
  "Ext.util.Inflector": [],\n
  "Ext.Map": [\n
    "widget.map"\n
  ],\n
  "Ext.XTemplate": [],\n
  "Ext.data.NodeStore": [\n
    "store.node"\n
  ],\n
  "Ext.draw.sprite.AttributeParser": [],\n
  "Ext.form.Panel": [\n
    "widget.formpanel"\n
  ],\n
  "Ext.chart.series.Series": [],\n
  "Ext.data.Request": [],\n
  "Ext.draw.sprite.Text": [\n
    "sprite.text"\n
  ],\n
  "Ext.layout.Float": [\n
    "layout.float"\n
  ],\n
  "Ext.dataview.component.DataItem": [\n
    "widget.dataitem"\n
  ],\n
  "Ext.chart.CartesianChart": [\n
    "widget.chart",\n
    "Ext.chart.Chart"\n
  ],\n
  "Ext.data.proxy.WebStorage": [],\n
  "Ext.log.writer.Writer": [],\n
  "Ext.device.Communicator": [],\n
  "Ext.fx.animation.Flip": [\n
    "animation.flip"\n
  ],\n
  "Ext.util.Point": [],\n
  "Ext.chart.series.StackedCartesian": [],\n
  "Ext.fx.layout.card.Slide": [\n
    "fx.layout.card.slide"\n
  ],\n
  "Ext.Anim": [],\n
  "Ext.data.DirectStore": [\n
    "store.direct"\n
  ],\n
  "Ext.dataview.NestedList": [\n
    "widget.nestedlist"\n
  ],\n
  "Ext.app.Route": [],\n
  "Ext.device.connection.Simulator": [],\n
  "Ext.chart.PolarChart": [\n
    "widget.polar"\n
  ],\n
  "Ext.event.publisher.ComponentSize": [],\n
  "Ext.slider.Toggle": [],\n
  "Ext.data.identifier.Sequential": [\n
    "data.identifier.sequential"\n
  ],\n
  "Ext.Template": [],\n
  "Ext.AbstractComponent": [],\n
  "Ext.device.Push": [],\n
  "Ext.fx.easing.BoundMomentum": [],\n
  "Ext.viewport.Viewport": [],\n
  "Ext.chart.series.Polar": [],\n
  "Ext.event.recognizer.VerticalSwipe": [],\n
  "Ext.event.Event": [],\n
  "Ext.behavior.Behavior": [],\n
  "Ext.chart.grid.VerticalGrid": [\n
    "grid.vertical"\n
  ],\n
  "Ext.chart.label.Label": [],\n
  "Ext.draw.sprite.EllipticalArc": [\n
    "sprite.ellipticalArc"\n
  ],\n
  "Ext.fx.easing.EaseOut": [\n
    "easing.ease-out"\n
  ],\n
  "Ext.Toolbar": [\n
    "widget.toolbar"\n
  ],\n
  "Ext.event.recognizer.LongPress": [],\n
  "Ext.device.notification.Sencha": [],\n
  "Ext.chart.series.sprite.Line": [\n
    "sprite.lineSeries"\n
  ],\n
  "Ext.data.ArrayStore": [\n
    "store.array"\n
  ],\n
  "Ext.data.proxy.SQL": [\n
    "proxy.sql"\n
  ],\n
  "Ext.mixin.Sortable": [],\n
  "Ext.fx.layout.card.Flip": [\n
    "fx.layout.card.flip"\n
  ],\n
  "Ext.chart.interactions.CrossZoom": [\n
    "interaction.crosszoom"\n
  ],\n
  "Ext.event.publisher.ComponentPaint": [],\n
  "Ext.event.recognizer.Rotate": [],\n
  "Ext.util.TranslatableList": [],\n
  "Ext.carousel.Item": [],\n
  "Ext.event.recognizer.Swipe": [],\n
  "Ext.util.translatable.ScrollPosition": [],\n
  "Ext.device.camera.Simulator": [],\n
  "Ext.chart.series.sprite.Area": [\n
    "sprite.areaSeries"\n
  ],\n
  "Ext.event.recognizer.Touch": [],\n
  "Ext.plugin.ListPaging": [\n
    "plugin.listpaging"\n
  ],\n
  "Ext.draw.sprite.Sector": [\n
    "sprite.sector"\n
  ],\n
  "Ext.chart.axis.segmenter.Names": [\n
    "segmenter.names"\n
  ],\n
  "Ext.mixin.Observable": [],\n
  "Ext.carousel.Infinite": [],\n
  "Ext.draw.Matrix": [],\n
  "Ext.Mask": [\n
    "widget.mask"\n
  ],\n
  "Ext.event.publisher.Publisher": [],\n
  "Ext.layout.wrapper.Dock": [],\n
  "Ext.app.History": [],\n
  "Ext.data.proxy.Direct": [\n
    "proxy.direct"\n
  ],\n
  "Ext.chart.axis.layout.Continuous": [\n
    "axisLayout.continuous"\n
  ],\n
  "Ext.table.Cell": [\n
    "widget.tablecell"\n
  ],\n
  "Ext.fx.layout.card.ScrollCover": [\n
    "fx.layout.card.scrollcover"\n
  ],\n
  "Ext.device.orientation.Sencha": [],\n
  "Ext.util.Droppable": [],\n
  "Ext.draw.sprite.Composite": [\n
    "sprite.composite"\n
  ],\n
  "Ext.chart.series.Pie": [\n
    "series.pie"\n
  ],\n
  "Ext.device.Purchases.Product": [],\n
  "Ext.device.Orientation": [],\n
  "Ext.direct.Provider": [\n
    "direct.provider"\n
  ],\n
  "Ext.draw.sprite.Arc": [\n
    "sprite.arc"\n
  ],\n
  "Ext.chart.axis.segmenter.Time": [\n
    "segmenter.time"\n
  ],\n
  "Ext.util.Draggable": [],\n
  "Ext.device.contacts.Sencha": [],\n
  "Ext.chart.grid.HorizontalGrid": [\n
    "grid.horizontal"\n
  ],\n
  "Ext.mixin.Traversable": [],\n
  "Ext.util.AbstractMixedCollection": [],\n
  "Ext.data.JsonStore": [\n
    "store.json"\n
  ],\n
  "Ext.draw.SegmentTree": [],\n
  "Ext.direct.RemotingEvent": [\n
    "direct.rpc"\n
  ],\n
  "Ext.plugin.PullRefresh": [\n
    "plugin.pullrefresh"\n
  ],\n
  "Ext.log.writer.Console": [],\n
  "Ext.field.Spinner": [\n
    "widget.spinnerfield"\n
  ],\n
  "Ext.chart.axis.segmenter.Numeric": [\n
    "segmenter.numeric"\n
  ],\n
  "Ext.data.proxy.LocalStorage": [\n
    "proxy.localstorage"\n
  ],\n
  "Ext.fx.animation.Wipe": [],\n
  "Ext.fx.layout.Card": [],\n
  "Ext.TaskQueue": [],\n
  "Ext.Label": [\n
    "widget.label"\n
  ],\n
  "Ext.util.translatable.CssTransform": [],\n
  "Ext.viewport.Ios": [],\n
  "Ext.Spacer": [\n
    "widget.spacer"\n
  ],\n
  "Ext.mixin.Selectable": [],\n
  "Ext.draw.sprite.Image": [\n
    "sprite.image"\n
  ],\n
  "Ext.data.proxy.Rest": [\n
    "proxy.rest"\n
  ],\n
  "Ext.Img": [\n
    "widget.img",\n
    "widget.image"\n
  ],\n
  "Ext.chart.series.sprite.Bar": [\n
    "sprite.barSeries"\n
  ],\n
  "Ext.log.writer.DocumentTitle": [],\n
  "Ext.data.Error": [],\n
  "Ext.util.Sorter": [],\n
  "Ext.draw.gradient.Radial": [],\n
  "Ext.layout.Abstract": [],\n
  "Ext.device.notification.Abstract": [],\n
  "Ext.log.filter.Filter": [],\n
  "Ext.device.camera.Sencha": [],\n
  "Ext.draw.sprite.Sprite": [\n
    "sprite.sprite"\n
  ],\n
  "Ext.draw.Color": [],\n
  "Ext.chart.series.Bar": [\n
    "series.bar"\n
  ],\n
  "Ext.field.Slider": [\n
    "widget.sliderfield"\n
  ],\n
  "Ext.field.Search": [\n
    "widget.searchfield"\n
  ],\n
  "Ext.chart.series.Scatter": [\n
    "series.scatter"\n
  ],\n
  "Ext.device.Device": [],\n
  "Ext.event.Dispatcher": [],\n
  "Ext.data.Store": [\n
    "store.store"\n
  ],\n
  "Ext.draw.modifier.Highlight": [\n
    "modifier.highlight"\n
  ],\n
  "Ext.behavior.Translatable": [],\n
  "Ext.direct.Manager": [],\n
  "Ext.data.proxy.Proxy": [\n
    "proxy.proxy"\n
  ],\n
  "Ext.draw.modifier.Modifier": [],\n
  "Ext.navigation.View": [\n
    "widget.navigationview"\n
  ],\n
  "Ext.draw.modifier.Target": [\n
    "modifier.target"\n
  ],\n
  "Ext.draw.sprite.AttributeDefinition": [],\n
  "Ext.device.Notification": [],\n
  "Ext.draw.Component": [\n
    "widget.draw"\n
  ],\n
  "Ext.layout.VBox": [\n
    "layout.vbox"\n
  ],\n
  "Ext.slider.Thumb": [\n
    "widget.thumb"\n
  ],\n
  "Ext.MessageBox": [],\n
  "Ext.ux.Faker": [],\n
  "Ext.dataview.IndexBar": [],\n
  "Ext.dataview.element.List": [],\n
  "Ext.layout.FlexBox": [\n
    "layout.box"\n
  ],\n
  "Ext.field.Url": [\n
    "widget.urlfield"\n
  ],\n
  "Ext.draw.Solver": [],\n
  "Ext.data.proxy.Memory": [\n
    "proxy.memory"\n
  ],\n
  "Ext.chart.axis.Time": [\n
    "axis.time"\n
  ],\n
  "Ext.layout.Card": [\n
    "layout.card"\n
  ],\n
  "Ext.ComponentQuery": [],\n
  "Ext.chart.series.Pie3D": [\n
    "series.pie3d"\n
  ],\n
  "Ext.device.camera.Abstract": [],\n
  "Ext.device.device.Sencha": [],\n
  "Ext.scroll.View": [],\n
  "Ext.draw.sprite.Rect": [\n
    "sprite.rect"\n
  ],\n
  "Ext.util.Region": [],\n
  "Ext.field.Select": [\n
    "widget.selectfield"\n
  ],\n
  "Ext.draw.Draw": [],\n
  "Ext.ItemCollection": [],\n
  "Ext.log.formatter.Default": [],\n
  "Ext.navigation.Bar": [],\n
  "Ext.chart.axis.layout.CombineDuplicate": [\n
    "axisLayout.combineDuplicate"\n
  ],\n
  "Ext.device.Geolocation": [],\n
  "Ext.chart.SpaceFillingChart": [\n
    "widget.spacefilling"\n
  ],\n
  "Ext.data.proxy.SessionStorage": [\n
    "proxy.sessionstorage"\n
  ],\n
  "Ext.fx.easing.EaseIn": [\n
    "easing.ease-in"\n
  ],\n
  "Ext.draw.sprite.AnimationParser": [],\n
  "Ext.field.Password": [\n
    "widget.passwordfield"\n
  ],\n
  "Ext.device.connection.Abstract": [],\n
  "Ext.direct.Event": [\n
    "direct.event"\n
  ],\n
  "Ext.direct.RemotingMethod": [],\n
  "Ext.Evented": [],\n
  "Ext.carousel.Indicator": [\n
    "widget.carouselindicator"\n
  ],\n
  "Ext.util.Collection": [],\n
  "Ext.chart.interactions.ItemInfo": [\n
    "interaction.iteminfo"\n
  ],\n
  "Ext.chart.MarkerHolder": [],\n
  "Ext.carousel.Carousel": [\n
    "widget.carousel"\n
  ],\n
  "Ext.Audio": [\n
    "widget.audio"\n
  ],\n
  "Ext.device.Contacts": [],\n
  "Ext.table.Table": [\n
    "widget.table"\n
  ],\n
  "Ext.draw.engine.SvgContext.Gradient": [],\n
  "Ext.chart.axis.layout.Layout": [],\n
  "Ext.data.Errors": [],\n
  "Ext.field.Text": [\n
    "widget.textfield"\n
  ],\n
  "Ext.field.TextAreaInput": [\n
    "widget.textareainput"\n
  ],\n
  "Ext.field.DatePicker": [\n
    "widget.datepickerfield"\n
  ],\n
  "Ext.draw.engine.Svg": [],\n
  "Ext.event.recognizer.Tap": [],\n
  "Ext.device.orientation.Abstract": [],\n
  "Ext.AbstractManager": [],\n
  "Ext.chart.series.Radar": [\n
    "series.radar"\n
  ],\n
  "Ext.chart.interactions.Abstract": [\n
    "widget.interaction"\n
  ],\n
  "Ext.scroll.indicator.CssTransform": [],\n
  "Ext.util.PaintMonitor": [],\n
  "Ext.direct.PollingProvider": [\n
    "direct.pollingprovider"\n
  ],\n
  "Ext.device.notification.PhoneGap": [],\n
  "Ext.data.writer.Xml": [\n
    "writer.xml"\n
  ],\n
  "Ext.event.recognizer.SingleTouch": [],\n
  "Ext.draw.sprite.Instancing": [\n
    "sprite.instancing"\n
  ],\n
  "Ext.event.publisher.ComponentDelegation": [],\n
  "Ext.chart.axis.Numeric": [\n
    "axis.numeric"\n
  ],\n
  "Ext.field.Toggle": [\n
    "widget.togglefield"\n
  ],\n
  "Ext.fx.layout.card.ScrollReveal": [\n
    "fx.layout.card.scrollreveal"\n
  ],\n
  "Ext.data.Operation": [],\n
  "Ext.fx.animation.Abstract": [],\n
  "Ext.chart.interactions.Rotate": [\n
    "interaction.rotate"\n
  ],\n
  "Ext.draw.engine.SvgContext": [],\n
  "Ext.scroll.Scroller": [],\n
  "Ext.util.SizeMonitor": [],\n
  "Ext.event.ListenerStack": [],\n
  "Ext.util.MixedCollection": []\n
});

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
