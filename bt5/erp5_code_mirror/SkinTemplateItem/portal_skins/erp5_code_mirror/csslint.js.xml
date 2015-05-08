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
            <value> <string>ts29784826.78</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>csslint.js</string> </value>
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
            <value> <int>306511</int> </value>
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
CSSLint\n
Copyright (c) 2013 Nicole Sullivan and Nicholas C. Zakas. All rights reserved.\n
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
*/\n
/* Build: v0.10.0 15-August-2013 01:07:22 */\n
var exports = exports || {};\n
var CSSLint = (function(){\n
/*!\n
Parser-Lib\n
Copyright (c) 2009-2011 Nicholas C. Zakas. All rights reserved.\n
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
*/\n
/* Version v0.2.3, Build time: 19-June-2013 11:16:15 */\n
var parserlib = {};\n
(function(){\n
\n
\n
/**\n
 * A generic base to inherit from for any object\n
 * that needs event handling.\n
 * @class EventTarget\n
 * @constructor\n
 */\n
function EventTarget(){\n
\n
    /**\n
     * The array of listeners for various events.\n
     * @type Object\n
     * @property _listeners\n
     * @private\n
     */\n
    this._listeners = {};\n
}\n
\n
EventTarget.prototype = {\n
\n
    //restore constructor\n
    constructor: EventTarget,\n
\n
    /**\n
     * Adds a listener for a given event type.\n
     * @param {String} type The type of event to add a listener for.\n
     * @param {Function} listener The function to call when the event occurs.\n
     * @return {void}\n
     * @method addListener\n
     */\n
    addListener: function(type, listener){\n
        if (!this._listeners[type]){\n
            this._listeners[type] = [];\n
        }\n
\n
        this._listeners[type].push(listener);\n
    },\n
\n
    /**\n
     * Fires an event based on the passed-in object.\n
     * @param {Object|String} event An object with at least a \'type\' attribute\n
     *      or a string indicating the event name.\n
     * @return {void}\n
     * @method fire\n
     */\n
    fire: function(event){\n
        if (typeof event == "string"){\n
            event = { type: event };\n
        }\n
        if (typeof event.target != "undefined"){\n
            event.target = this;\n
        }\n
\n
        if (typeof event.type == "undefined"){\n
            throw new Error("Event object missing \'type\' property.");\n
        }\n
\n
        if (this._listeners[event.type]){\n
\n
            //create a copy of the array and use that so listeners can\'t chane\n
            var listeners = this._listeners[event.type].concat();\n
            for (var i=0, len=listeners.length; i < len; i++){\n
                listeners[i].call(this, event);\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Removes a listener for a given event type.\n
     * @param {String} type The type of event to remove a listener from.\n
     * @param {Function} listener The function to remove from the event.\n
     * @return {void}\n
     * @method removeListener\n
     */\n
    removeListener: function(type, listener){\n
        if (this._listeners[type]){\n
            var listeners = this._listeners[type];\n
            for (var i=0, len=listeners.length; i < len; i++){\n
                if (listeners[i] === listener){\n
                    listeners.splice(i, 1);\n
                    break;\n
                }\n
            }\n
\n
\n
        }\n
    }\n
};\n
/**\n
 * Convenient way to read through strings.\n
 * @namespace parserlib.util\n
 * @class StringReader\n
 * @constructor\n
 * @param {String} text The text to read.\n
 */\n
function StringReader(text){\n
\n
    /**\n
     * The input text with line endings normalized.\n
     * @property _input\n
     * @type String\n
     * @private\n
     */\n
    this._input = text.replace(/\\n\\r?/g, "\\n");\n
\n
\n
    /**\n
     * The row for the character to be read next.\n
     * @property _line\n
     * @type int\n
     * @private\n
     */\n
    this._line = 1;\n
\n
\n
    /**\n
     * The column for the character to be read next.\n
     * @property _col\n
     * @type int\n
     * @private\n
     */\n
    this._col = 1;\n
\n
    /**\n
     * The index of the character in the input to be read next.\n
     * @property _cursor\n
     * @type int\n
     * @private\n
     */\n
    this._cursor = 0;\n
}\n
\n
StringReader.prototype = {\n
\n
    //restore constructor\n
    constructor: StringReader,\n
\n
    //-------------------------------------------------------------------------\n
    // Position info\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Returns the column of the character to be read next.\n
     * @return {int} The column of the character to be read next.\n
     * @method getCol\n
     */\n
    getCol: function(){\n
        return this._col;\n
    },\n
\n
    /**\n
     * Returns the row of the character to be read next.\n
     * @return {int} The row of the character to be read next.\n
     * @method getLine\n
     */\n
    getLine: function(){\n
        return this._line ;\n
    },\n
\n
    /**\n
     * Determines if you\'re at the end of the input.\n
     * @return {Boolean} True if there\'s no more input, false otherwise.\n
     * @method eof\n
     */\n
    eof: function(){\n
        return (this._cursor == this._input.length);\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Basic reading\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Reads the next character without advancing the cursor.\n
     * @param {int} count How many characters to look ahead (default is 1).\n
     * @return {String} The next character or null if there is no next character.\n
     * @method peek\n
     */\n
    peek: function(count){\n
        var c = null;\n
        count = (typeof count == "undefined" ? 1 : count);\n
\n
        //if we\'re not at the end of the input...\n
        if (this._cursor < this._input.length){\n
\n
            //get character and increment cursor and column\n
            c = this._input.charAt(this._cursor + count - 1);\n
        }\n
\n
        return c;\n
    },\n
\n
    /**\n
     * Reads the next character from the input and adjusts the row and column\n
     * accordingly.\n
     * @return {String} The next character or null if there is no next character.\n
     * @method read\n
     */\n
    read: function(){\n
        var c = null;\n
\n
        //if we\'re not at the end of the input...\n
        if (this._cursor < this._input.length){\n
\n
            //if the last character was a newline, increment row count\n
            //and reset column count\n
            if (this._input.charAt(this._cursor) == "\\n"){\n
                this._line++;\n
                this._col=1;\n
            } else {\n
                this._col++;\n
            }\n
\n
            //get character and increment cursor and column\n
            c = this._input.charAt(this._cursor++);\n
        }\n
\n
        return c;\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Misc\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Saves the current location so it can be returned to later.\n
     * @method mark\n
     * @return {void}\n
     */\n
    mark: function(){\n
        this._bookmark = {\n
            cursor: this._cursor,\n
            line:   this._line,\n
            col:    this._col\n
        };\n
    },\n
\n
    reset: function(){\n
        if (this._bookmark){\n
            this._cursor = this._bookmark.cursor;\n
            this._line = this._bookmark.line;\n
            this._col = this._bookmark.col;\n
            delete this._bookmark;\n
        }\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Advanced reading\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Reads up to and including the given string. Throws an error if that\n
     * string is not found.\n
     * @param {String} pattern The string to read.\n
     * @return {String} The string when it is found.\n
     * @throws Error when the string pattern is not found.\n
     * @method readTo\n
     */\n
    readTo: function(pattern){\n
\n
        var buffer = "",\n
            c;\n
\n
        /*\n
         * First, buffer must be the same length as the pattern.\n
         * Then, buffer must end with the pattern or else reach the\n
         * end of the input.\n
         */\n
        while (buffer.length < pattern.length || buffer.lastIndexOf(pattern) != buffer.length - pattern.length){\n
            c = this.read();\n
            if (c){\n
                buffer += c;\n
            } else {\n
                throw new Error("Expected \\"" + pattern + "\\" at line " + this._line  + ", col " + this._col + ".");\n
            }\n
        }\n
\n
        return buffer;\n
\n
    },\n
\n
    /**\n
     * Reads characters while each character causes the given\n
     * filter function to return true. The function is passed\n
     * in each character and either returns true to continue\n
     * reading or false to stop.\n
     * @param {Function} filter The function to read on each character.\n
     * @return {String} The string made up of all characters that passed the\n
     *      filter check.\n
     * @method readWhile\n
     */\n
    readWhile: function(filter){\n
\n
        var buffer = "",\n
            c = this.read();\n
\n
        while(c !== null && filter(c)){\n
            buffer += c;\n
            c = this.read();\n
        }\n
\n
        return buffer;\n
\n
    },\n
\n
    /**\n
     * Reads characters that match either text or a regular expression and\n
     * returns those characters. If a match is found, the row and column\n
     * are adjusted; if no match is found, the reader\'s state is unchanged.\n
     * reading or false to stop.\n
     * @param {String|RegExp} matchter If a string, then the literal string\n
     *      value is searched for. If a regular expression, then any string\n
     *      matching the pattern is search for.\n
     * @return {String} The string made up of all characters that matched or\n
     *      null if there was no match.\n
     * @method readMatch\n
     */\n
    readMatch: function(matcher){\n
\n
        var source = this._input.substring(this._cursor),\n
            value = null;\n
\n
        //if it\'s a string, just do a straight match\n
        if (typeof matcher == "string"){\n
            if (source.indexOf(matcher) === 0){\n
                value = this.readCount(matcher.length);\n
            }\n
        } else if (matcher instanceof RegExp){\n
            if (matcher.test(source)){\n
                value = this.readCount(RegExp.lastMatch.length);\n
            }\n
        }\n
\n
        return value;\n
    },\n
\n
\n
    /**\n
     * Reads a given number of characters. If the end of the input is reached,\n
     * it reads only the remaining characters and does not throw an error.\n
     * @param {int} count The number of characters to read.\n
     * @return {String} The string made up the read characters.\n
     * @method readCount\n
     */\n
    readCount: function(count){\n
        var buffer = "";\n
\n
        while(count--){\n
            buffer += this.read();\n
        }\n
\n
        return buffer;\n
    }\n
\n
};\n
/**\n
 * Type to use when a syntax error occurs.\n
 * @class SyntaxError\n
 * @namespace parserlib.util\n
 * @constructor\n
 * @param {String} message The error message.\n
 * @param {int} line The line at which the error occurred.\n
 * @param {int} col The column at which the error occurred.\n
 */\n
function SyntaxError(message, line, col){\n
\n
    /**\n
     * The column at which the error occurred.\n
     * @type int\n
     * @property col\n
     */\n
    this.col = col;\n
\n
    /**\n
     * The line at which the error occurred.\n
     * @type int\n
     * @property line\n
     */\n
    this.line = line;\n
\n
    /**\n
     * The text representation of the unit.\n
     * @type String\n
     * @property text\n
     */\n
    this.message = message;\n
\n
}\n
\n
//inherit from Error\n
SyntaxError.prototype = new Error();\n
/**\n
 * Base type to represent a single syntactic unit.\n
 * @class SyntaxUnit\n
 * @namespace parserlib.util\n
 * @constructor\n
 * @param {String} text The text of the unit.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function SyntaxUnit(text, line, col, type){\n
\n
\n
    /**\n
     * The column of text on which the unit resides.\n
     * @type int\n
     * @property col\n
     */\n
    this.col = col;\n
\n
    /**\n
     * The line of text on which the unit resides.\n
     * @type int\n
     * @property line\n
     */\n
    this.line = line;\n
\n
    /**\n
     * The text representation of the unit.\n
     * @type String\n
     * @property text\n
     */\n
    this.text = text;\n
\n
    /**\n
     * The type of syntax unit.\n
     * @type int\n
     * @property type\n
     */\n
    this.type = type;\n
}\n
\n
/**\n
 * Create a new syntax unit based solely on the given token.\n
 * Convenience method for creating a new syntax unit when\n
 * it represents a single token instead of multiple.\n
 * @param {Object} token The token object to represent.\n
 * @return {parserlib.util.SyntaxUnit} The object representing the token.\n
 * @static\n
 * @method fromToken\n
 */\n
SyntaxUnit.fromToken = function(token){\n
    return new SyntaxUnit(token.value, token.startLine, token.startCol);\n
};\n
\n
SyntaxUnit.prototype = {\n
\n
    //restore constructor\n
    constructor: SyntaxUnit,\n
\n
    /**\n
     * Returns the text representation of the unit.\n
     * @return {String} The text representation of the unit.\n
     * @method valueOf\n
     */\n
    valueOf: function(){\n
        return this.toString();\n
    },\n
\n
    /**\n
     * Returns the text representation of the unit.\n
     * @return {String} The text representation of the unit.\n
     * @method toString\n
     */\n
    toString: function(){\n
        return this.text;\n
    }\n
\n
};\n
/*global StringReader, SyntaxError*/\n
\n
/**\n
 * Generic TokenStream providing base functionality.\n
 * @class TokenStreamBase\n
 * @namespace parserlib.util\n
 * @constructor\n
 * @param {String|StringReader} input The text to tokenize or a reader from\n
 *      which to read the input.\n
 */\n
function TokenStreamBase(input, tokenData){\n
\n
    /**\n
     * The string reader for easy access to the text.\n
     * @type StringReader\n
     * @property _reader\n
     * @private\n
     */\n
    this._reader = input ? new StringReader(input.toString()) : null;\n
\n
    /**\n
     * Token object for the last consumed token.\n
     * @type Token\n
     * @property _token\n
     * @private\n
     */\n
    this._token = null;\n
\n
    /**\n
     * The array of token information.\n
     * @type Array\n
     * @property _tokenData\n
     * @private\n
     */\n
    this._tokenData = tokenData;\n
\n
    /**\n
     * Lookahead token buffer.\n
     * @type Array\n
     * @property _lt\n
     * @private\n
     */\n
    this._lt = [];\n
\n
    /**\n
     * Lookahead token buffer index.\n
     * @type int\n
     * @property _ltIndex\n
     * @private\n
     */\n
    this._ltIndex = 0;\n
\n
    this._ltIndexCache = [];\n
}\n
\n
/**\n
 * Accepts an array of token information and outputs\n
 * an array of token data containing key-value mappings\n
 * and matching functions that the TokenStream needs.\n
 * @param {Array} tokens An array of token descriptors.\n
 * @return {Array} An array of processed token data.\n
 * @method createTokenData\n
 * @static\n
 */\n
TokenStreamBase.createTokenData = function(tokens){\n
\n
    var nameMap     = [],\n
        typeMap     = {},\n
        tokenData     = tokens.concat([]),\n
        i            = 0,\n
        len            = tokenData.length+1;\n
\n
    tokenData.UNKNOWN = -1;\n
    tokenData.unshift({name:"EOF"});\n
\n
    for (; i < len; i++){\n
        nameMap.push(tokenData[i].name);\n
        tokenData[tokenData[i].name] = i;\n
        if (tokenData[i].text){\n
            typeMap[tokenData[i].text] = i;\n
        }\n
    }\n
\n
    tokenData.name = function(tt){\n
        return nameMap[tt];\n
    };\n
\n
    tokenData.type = function(c){\n
        return typeMap[c];\n
    };\n
\n
    return tokenData;\n
};\n
\n
TokenStreamBase.prototype = {\n
\n
    //restore constructor\n
    constructor: TokenStreamBase,\n
\n
    //-------------------------------------------------------------------------\n
    // Matching methods\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Determines if the next token matches the given token type.\n
     * If so, that token is consumed; if not, the token is placed\n
     * back onto the token stream. You can pass in any number of\n
     * token types and this will return true if any of the token\n
     * types is found.\n
     * @param {int|int[]} tokenTypes Either a single token type or an array of\n
     *      token types that the next token might be. If an array is passed,\n
     *      it\'s assumed that the token can be any of these.\n
     * @param {variant} channel (Optional) The channel to read from. If not\n
     *      provided, reads from the default (unnamed) channel.\n
     * @return {Boolean} True if the token type matches, false if not.\n
     * @method match\n
     */\n
    match: function(tokenTypes, channel){\n
\n
        //always convert to an array, makes things easier\n
        if (!(tokenTypes instanceof Array)){\n
            tokenTypes = [tokenTypes];\n
        }\n
\n
        var tt  = this.get(channel),\n
            i   = 0,\n
            len = tokenTypes.length;\n
\n
        while(i < len){\n
            if (tt == tokenTypes[i++]){\n
                return true;\n
            }\n
        }\n
\n
        //no match found, put the token back\n
        this.unget();\n
        return false;\n
    },\n
\n
    /**\n
     * Determines if the next token matches the given token type.\n
     * If so, that token is consumed; if not, an error is thrown.\n
     * @param {int|int[]} tokenTypes Either a single token type or an array of\n
     *      token types that the next token should be. If an array is passed,\n
     *      it\'s assumed that the token must be one of these.\n
     * @param {variant} channel (Optional) The channel to read from. If not\n
     *      provided, reads from the default (unnamed) channel.\n
     * @return {void}\n
     * @method mustMatch\n
     */\n
    mustMatch: function(tokenTypes, channel){\n
\n
        var token;\n
\n
        //always convert to an array, makes things easier\n
        if (!(tokenTypes instanceof Array)){\n
            tokenTypes = [tokenTypes];\n
        }\n
\n
        if (!this.match.apply(this, arguments)){\n
            token = this.LT(1);\n
            throw new SyntaxError("Expected " + this._tokenData[tokenTypes[0]].name +\n
                " at line " + token.startLine + ", col " + token.startCol + ".", token.startLine, token.startCol);\n
        }\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Consuming methods\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Keeps reading from the token stream until either one of the specified\n
     * token types is found or until the end of the input is reached.\n
     * @param {int|int[]} tokenTypes Either a single token type or an array of\n
     *      token types that the next token should be. If an array is passed,\n
     *      it\'s assumed that the token must be one of these.\n
     * @param {variant} channel (Optional) The channel to read from. If not\n
     *      provided, reads from the default (unnamed) channel.\n
     * @return {void}\n
     * @method advance\n
     */\n
    advance: function(tokenTypes, channel){\n
\n
        while(this.LA(0) !== 0 && !this.match(tokenTypes, channel)){\n
            this.get();\n
        }\n
\n
        return this.LA(0);\n
    },\n
\n
    /**\n
     * Consumes the next token from the token stream.\n
     * @return {int} The token type of the token that was just consumed.\n
     * @method get\n
     */\n
    get: function(channel){\n
\n
        var tokenInfo   = this._tokenData,\n
            reader      = this._reader,\n
            value,\n
            i           =0,\n
            len         = tokenInfo.length,\n
            found       = false,\n
            token,\n
            info;\n
\n
        //check the lookahead buffer first\n
        if (this._lt.length && this._ltIndex >= 0 && this._ltIndex < this._lt.length){\n
\n
            i++;\n
            this._token = this._lt[this._ltIndex++];\n
            info = tokenInfo[this._token.type];\n
\n
            //obey channels logic\n
            while((info.channel !== undefined && channel !== info.channel) &&\n
                    this._ltIndex < this._lt.length){\n
                this._token = this._lt[this._ltIndex++];\n
                info = tokenInfo[this._token.type];\n
                i++;\n
            }\n
\n
            //here be dragons\n
            if ((info.channel === undefined || channel === info.channel) &&\n
                    this._ltIndex <= this._lt.length){\n
                this._ltIndexCache.push(i);\n
                return this._token.type;\n
            }\n
        }\n
\n
        //call token retriever method\n
        token = this._getToken();\n
\n
        //if it should be hidden, don\'t save a token\n
        if (token.type > -1 && !tokenInfo[token.type].hide){\n
\n
            //apply token channel\n
            token.channel = tokenInfo[token.type].channel;\n
\n
            //save for later\n
            this._token = token;\n
            this._lt.push(token);\n
\n
            //save space that will be moved (must be done before array is truncated)\n
            this._ltIndexCache.push(this._lt.length - this._ltIndex + i);\n
\n
            //keep the buffer under 5 items\n
            if (this._lt.length > 5){\n
                this._lt.shift();\n
            }\n
\n
            //also keep the shift buffer under 5 items\n
            if (this._ltIndexCache.length > 5){\n
                this._ltIndexCache.shift();\n
            }\n
\n
            //update lookahead index\n
            this._ltIndex = this._lt.length;\n
        }\n
\n
        /*\n
         * Skip to the next token if:\n
         * 1. The token type is marked as hidden.\n
         * 2. The token type has a channel specified and it isn\'t the current channel.\n
         */\n
        info = tokenInfo[token.type];\n
        if (info &&\n
                (info.hide ||\n
                (info.channel !== undefined && channel !== info.channel))){\n
            return this.get(channel);\n
        } else {\n
            //return just the type\n
            return token.type;\n
        }\n
    },\n
\n
    /**\n
     * Looks ahead a certain number of tokens and returns the token type at\n
     * that position. This will throw an error if you lookahead past the\n
     * end of input, past the size of the lookahead buffer, or back past\n
     * the first token in the lookahead buffer.\n
     * @param {int} The index of the token type to retrieve. 0 for the\n
     *      current token, 1 for the next, -1 for the previous, etc.\n
     * @return {int} The token type of the token in the given position.\n
     * @method LA\n
     */\n
    LA: function(index){\n
        var total = index,\n
            tt;\n
        if (index > 0){\n
            //TODO: Store 5 somewhere\n
            if (index > 5){\n
                throw new Error("Too much lookahead.");\n
            }\n
\n
            //get all those tokens\n
            while(total){\n
                tt = this.get();\n
                total--;\n
            }\n
\n
            //unget all those tokens\n
            while(total < index){\n
                this.unget();\n
                total++;\n
            }\n
        } else if (index < 0){\n
\n
            if(this._lt[this._ltIndex+index]){\n
                tt = this._lt[this._ltIndex+index].type;\n
            } else {\n
                throw new Error("Too much lookbehind.");\n
            }\n
\n
        } else {\n
            tt = this._token.type;\n
        }\n
\n
        return tt;\n
\n
    },\n
\n
    /**\n
     * Looks ahead a certain number of tokens and returns the token at\n
     * that position. This will throw an error if you lookahead past the\n
     * end of input, past the size of the lookahead buffer, or back past\n
     * the first token in the lookahead buffer.\n
     * @param {int} The index of the token type to retrieve. 0 for the\n
     *      current token, 1 for the next, -1 for the previous, etc.\n
     * @return {Object} The token of the token in the given position.\n
     * @method LA\n
     */\n
    LT: function(index){\n
\n
        //lookahead first to prime the token buffer\n
        this.LA(index);\n
\n
        //now find the token, subtract one because _ltIndex is already at the next index\n
        return this._lt[this._ltIndex+index-1];\n
    },\n
\n
    /**\n
     * Returns the token type for the next token in the stream without\n
     * consuming it.\n
     * @return {int} The token type of the next token in the stream.\n
     * @method peek\n
     */\n
    peek: function(){\n
        return this.LA(1);\n
    },\n
\n
    /**\n
     * Returns the actual token object for the last consumed token.\n
     * @return {Token} The token object for the last consumed token.\n
     * @method token\n
     */\n
    token: function(){\n
        return this._token;\n
    },\n
\n
    /**\n
     * Returns the name of the token for the given token type.\n
     * @param {int} tokenType The type of token to get the name of.\n
     * @return {String} The name of the token or "UNKNOWN_TOKEN" for any\n
     *      invalid token type.\n
     * @method tokenName\n
     */\n
    tokenName: function(tokenType){\n
        if (tokenType < 0 || tokenType > this._tokenData.length){\n
            return "UNKNOWN_TOKEN";\n
        } else {\n
            return this._tokenData[tokenType].name;\n
        }\n
    },\n
\n
    /**\n
     * Returns the token type value for the given token name.\n
     * @param {String} tokenName The name of the token whose value should be returned.\n
     * @return {int} The token type value for the given token name or -1\n
     *      for an unknown token.\n
     * @method tokenName\n
     */\n
    tokenType: function(tokenName){\n
        return this._tokenData[tokenName] || -1;\n
    },\n
\n
    /**\n
     * Returns the last consumed token to the token stream.\n
     * @method unget\n
     */\n
    unget: function(){\n
        //if (this._ltIndex > -1){\n
        if (this._ltIndexCache.length){\n
            this._ltIndex -= this._ltIndexCache.pop();//--;\n
            this._token = this._lt[this._ltIndex - 1];\n
        } else {\n
            throw new Error("Too much lookahead.");\n
        }\n
    }\n
\n
};\n
\n
\n
\n
\n
parserlib.util = {\n
StringReader: StringReader,\n
SyntaxError : SyntaxError,\n
SyntaxUnit  : SyntaxUnit,\n
EventTarget : EventTarget,\n
TokenStreamBase : TokenStreamBase\n
};\n
})();\n
\n
\n
/*\n
Parser-Lib\n
Copyright (c) 2009-2011 Nicholas C. Zakas. All rights reserved.\n
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
*/\n
/* Version v0.2.3, Build time: 19-June-2013 11:16:15 */\n
(function(){\n
var EventTarget = parserlib.util.EventTarget,\n
TokenStreamBase = parserlib.util.TokenStreamBase,\n
StringReader = parserlib.util.StringReader,\n
SyntaxError = parserlib.util.SyntaxError,\n
SyntaxUnit  = parserlib.util.SyntaxUnit;\n
\n
\n
var Colors = {\n
    aliceblue       :"#f0f8ff",\n
    antiquewhite    :"#faebd7",\n
    aqua            :"#00ffff",\n
    aquamarine      :"#7fffd4",\n
    azure           :"#f0ffff",\n
    beige           :"#f5f5dc",\n
    bisque          :"#ffe4c4",\n
    black           :"#000000",\n
    blanchedalmond  :"#ffebcd",\n
    blue            :"#0000ff",\n
    blueviolet      :"#8a2be2",\n
    brown           :"#a52a2a",\n
    burlywood       :"#deb887",\n
    cadetblue       :"#5f9ea0",\n
    chartreuse      :"#7fff00",\n
    chocolate       :"#d2691e",\n
    coral           :"#ff7f50",\n
    cornflowerblue  :"#6495ed",\n
    cornsilk        :"#fff8dc",\n
    crimson         :"#dc143c",\n
    cyan            :"#00ffff",\n
    darkblue        :"#00008b",\n
    darkcyan        :"#008b8b",\n
    darkgoldenrod   :"#b8860b",\n
    darkgray        :"#a9a9a9",\n
    darkgreen       :"#006400",\n
    darkkhaki       :"#bdb76b",\n
    darkmagenta     :"#8b008b",\n
    darkolivegreen  :"#556b2f",\n
    darkorange      :"#ff8c00",\n
    darkorchid      :"#9932cc",\n
    darkred         :"#8b0000",\n
    darksalmon      :"#e9967a",\n
    darkseagreen    :"#8fbc8f",\n
    darkslateblue   :"#483d8b",\n
    darkslategray   :"#2f4f4f",\n
    darkturquoise   :"#00ced1",\n
    darkviolet      :"#9400d3",\n
    deeppink        :"#ff1493",\n
    deepskyblue     :"#00bfff",\n
    dimgray         :"#696969",\n
    dodgerblue      :"#1e90ff",\n
    firebrick       :"#b22222",\n
    floralwhite     :"#fffaf0",\n
    forestgreen     :"#228b22",\n
    fuchsia         :"#ff00ff",\n
    gainsboro       :"#dcdcdc",\n
    ghostwhite      :"#f8f8ff",\n
    gold            :"#ffd700",\n
    goldenrod       :"#daa520",\n
    gray            :"#808080",\n
    green           :"#008000",\n
    greenyellow     :"#adff2f",\n
    honeydew        :"#f0fff0",\n
    hotpink         :"#ff69b4",\n
    indianred       :"#cd5c5c",\n
    indigo          :"#4b0082",\n
    ivory           :"#fffff0",\n
    khaki           :"#f0e68c",\n
    lavender        :"#e6e6fa",\n
    lavenderblush   :"#fff0f5",\n
    lawngreen       :"#7cfc00",\n
    lemonchiffon    :"#fffacd",\n
    lightblue       :"#add8e6",\n
    lightcoral      :"#f08080",\n
    lightcyan       :"#e0ffff",\n
    lightgoldenrodyellow  :"#fafad2",\n
    lightgray       :"#d3d3d3",\n
    lightgreen      :"#90ee90",\n
    lightpink       :"#ffb6c1",\n
    lightsalmon     :"#ffa07a",\n
    lightseagreen   :"#20b2aa",\n
    lightskyblue    :"#87cefa",\n
    lightslategray  :"#778899",\n
    lightsteelblue  :"#b0c4de",\n
    lightyellow     :"#ffffe0",\n
    lime            :"#00ff00",\n
    limegreen       :"#32cd32",\n
    linen           :"#faf0e6",\n
    magenta         :"#ff00ff",\n
    maroon          :"#800000",\n
    mediumaquamarine:"#66cdaa",\n
    mediumblue      :"#0000cd",\n
    mediumorchid    :"#ba55d3",\n
    mediumpurple    :"#9370d8",\n
    mediumseagreen  :"#3cb371",\n
    mediumslateblue :"#7b68ee",\n
    mediumspringgreen   :"#00fa9a",\n
    mediumturquoise :"#48d1cc",\n
    mediumvioletred :"#c71585",\n
    midnightblue    :"#191970",\n
    mintcream       :"#f5fffa",\n
    mistyrose       :"#ffe4e1",\n
    moccasin        :"#ffe4b5",\n
    navajowhite     :"#ffdead",\n
    navy            :"#000080",\n
    oldlace         :"#fdf5e6",\n
    olive           :"#808000",\n
    olivedrab       :"#6b8e23",\n
    orange          :"#ffa500",\n
    orangered       :"#ff4500",\n
    orchid          :"#da70d6",\n
    palegoldenrod   :"#eee8aa",\n
    palegreen       :"#98fb98",\n
    paleturquoise   :"#afeeee",\n
    palevioletred   :"#d87093",\n
    papayawhip      :"#ffefd5",\n
    peachpuff       :"#ffdab9",\n
    peru            :"#cd853f",\n
    pink            :"#ffc0cb",\n
    plum            :"#dda0dd",\n
    powderblue      :"#b0e0e6",\n
    purple          :"#800080",\n
    red             :"#ff0000",\n
    rosybrown       :"#bc8f8f",\n
    royalblue       :"#4169e1",\n
    saddlebrown     :"#8b4513",\n
    salmon          :"#fa8072",\n
    sandybrown      :"#f4a460",\n
    seagreen        :"#2e8b57",\n
    seashell        :"#fff5ee",\n
    sienna          :"#a0522d",\n
    silver          :"#c0c0c0",\n
    skyblue         :"#87ceeb",\n
    slateblue       :"#6a5acd",\n
    slategray       :"#708090",\n
    snow            :"#fffafa",\n
    springgreen     :"#00ff7f",\n
    steelblue       :"#4682b4",\n
    tan             :"#d2b48c",\n
    teal            :"#008080",\n
    thistle         :"#d8bfd8",\n
    tomato          :"#ff6347",\n
    turquoise       :"#40e0d0",\n
    violet          :"#ee82ee",\n
    wheat           :"#f5deb3",\n
    white           :"#ffffff",\n
    whitesmoke      :"#f5f5f5",\n
    yellow          :"#ffff00",\n
    yellowgreen     :"#9acd32",\n
    //CSS2 system colors http://www.w3.org/TR/css3-color/#css2-system\n
    activeBorder        :"Active window border.",\n
    activecaption       :"Active window caption.",\n
    appworkspace        :"Background color of multiple document interface.",\n
    background          :"Desktop background.",\n
    buttonface          :"The face background color for 3-D elements that appear 3-D due to one layer of surrounding border.",\n
    buttonhighlight     :"The color of the border facing the light source for 3-D elements that appear 3-D due to one layer of surrounding border.",\n
    buttonshadow        :"The color of the border away from the light source for 3-D elements that appear 3-D due to one layer of surrounding border.",\n
    buttontext          :"Text on push buttons.",\n
    captiontext         :"Text in caption, size box, and scrollbar arrow box.",\n
    graytext            :"Grayed (disabled) text. This color is set to #000 if the current display driver does not support a solid gray color.",\n
    highlight           :"Item(s) selected in a control.",\n
    highlighttext       :"Text of item(s) selected in a control.",\n
    inactiveborder      :"Inactive window border.",\n
    inactivecaption     :"Inactive window caption.",\n
    inactivecaptiontext :"Color of text in an inactive caption.",\n
    infobackground      :"Background color for tooltip controls.",\n
    infotext            :"Text color for tooltip controls.",\n
    menu                :"Menu background.",\n
    menutext            :"Text in menus.",\n
    scrollbar           :"Scroll bar gray area.",\n
    threeddarkshadow    :"The color of the darker (generally outer) of the two borders away from the light source for 3-D elements that appear 3-D due to two concentric layers of surrounding border.",\n
    threedface          :"The face background color for 3-D elements that appear 3-D due to two concentric layers of surrounding border.",\n
    threedhighlight     :"The color of the lighter (generally outer) of the two borders facing the light source for 3-D elements that appear 3-D due to two concentric layers of surrounding border.",\n
    threedlightshadow   :"The color of the darker (generally inner) of the two borders facing the light source for 3-D elements that appear 3-D due to two concentric layers of surrounding border.",\n
    threedshadow        :"The color of the lighter (generally inner) of the two borders away from the light source for 3-D elements that appear 3-D due to two concentric layers of surrounding border.",\n
    window              :"Window background.",\n
    windowframe         :"Window frame.",\n
    windowtext          :"Text in windows."\n
};\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a selector combinator (whitespace, +, >).\n
 * @namespace parserlib.css\n
 * @class Combinator\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {String} text The text representation of the unit.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function Combinator(text, line, col){\n
\n
    SyntaxUnit.call(this, text, line, col, Parser.COMBINATOR_TYPE);\n
\n
    /**\n
     * The type of modifier.\n
     * @type String\n
     * @property type\n
     */\n
    this.type = "unknown";\n
\n
    //pretty simple\n
    if (/^\\s+$/.test(text)){\n
        this.type = "descendant";\n
    } else if (text == ">"){\n
        this.type = "child";\n
    } else if (text == "+"){\n
        this.type = "adjacent-sibling";\n
    } else if (text == "~"){\n
        this.type = "sibling";\n
    }\n
\n
}\n
\n
Combinator.prototype = new SyntaxUnit();\n
Combinator.prototype.constructor = Combinator;\n
\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a media feature, such as max-width:500.\n
 * @namespace parserlib.css\n
 * @class MediaFeature\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {SyntaxUnit} name The name of the feature.\n
 * @param {SyntaxUnit} value The value of the feature or null if none.\n
 */\n
function MediaFeature(name, value){\n
\n
    SyntaxUnit.call(this, "(" + name + (value !== null ? ":" + value : "") + ")", name.startLine, name.startCol, Parser.MEDIA_FEATURE_TYPE);\n
\n
    /**\n
     * The name of the media feature\n
     * @type String\n
     * @property name\n
     */\n
    this.name = name;\n
\n
    /**\n
     * The value for the feature or null if there is none.\n
     * @type SyntaxUnit\n
     * @property value\n
     */\n
    this.value = value;\n
}\n
\n
MediaFeature.prototype = new SyntaxUnit();\n
MediaFeature.prototype.constructor = MediaFeature;\n
\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents an individual media query.\n
 * @namespace parserlib.css\n
 * @class MediaQuery\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {String} modifier The modifier "not" or "only" (or null).\n
 * @param {String} mediaType The type of media (i.e., "print").\n
 * @param {Array} parts Array of selectors parts making up this selector.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function MediaQuery(modifier, mediaType, features, line, col){\n
\n
    SyntaxUnit.call(this, (modifier ? modifier + " ": "") + (mediaType ? mediaType : "") + (mediaType && features.length > 0 ? " and " : "") + features.join(" and "), line, col, Parser.MEDIA_QUERY_TYPE);\n
\n
    /**\n
     * The media modifier ("not" or "only")\n
     * @type String\n
     * @property modifier\n
     */\n
    this.modifier = modifier;\n
\n
    /**\n
     * The mediaType (i.e., "print")\n
     * @type String\n
     * @property mediaType\n
     */\n
    this.mediaType = mediaType;\n
\n
    /**\n
     * The parts that make up the selector.\n
     * @type Array\n
     * @property features\n
     */\n
    this.features = features;\n
\n
}\n
\n
MediaQuery.prototype = new SyntaxUnit();\n
MediaQuery.prototype.constructor = MediaQuery;\n
\n
\n
/*global Tokens, TokenStream, SyntaxError, Properties, Validation, ValidationError, SyntaxUnit,\n
    PropertyValue, PropertyValuePart, SelectorPart, SelectorSubPart, Selector,\n
    PropertyName, Combinator, MediaFeature, MediaQuery, EventTarget */\n
\n
/**\n
 * A CSS3 parser.\n
 * @namespace parserlib.css\n
 * @class Parser\n
 * @constructor\n
 * @param {Object} options (Optional) Various options for the parser:\n
 *      starHack (true|false) to allow IE6 star hack as valid,\n
 *      underscoreHack (true|false) to interpret leading underscores\n
 *      as IE6-7 targeting for known properties, ieFilters (true|false)\n
 *      to indicate that IE < 8 filters should be accepted and not throw\n
 *      syntax errors.\n
 */\n
function Parser(options){\n
\n
    //inherit event functionality\n
    EventTarget.call(this);\n
\n
\n
    this.options = options || {};\n
\n
    this._tokenStream = null;\n
}\n
\n
//Static constants\n
Parser.DEFAULT_TYPE = 0;\n
Parser.COMBINATOR_TYPE = 1;\n
Parser.MEDIA_FEATURE_TYPE = 2;\n
Parser.MEDIA_QUERY_TYPE = 3;\n
Parser.PROPERTY_NAME_TYPE = 4;\n
Parser.PROPERTY_VALUE_TYPE = 5;\n
Parser.PROPERTY_VALUE_PART_TYPE = 6;\n
Parser.SELECTOR_TYPE = 7;\n
Parser.SELECTOR_PART_TYPE = 8;\n
Parser.SELECTOR_SUB_PART_TYPE = 9;\n
\n
Parser.prototype = function(){\n
\n
    var proto = new EventTarget(),  //new prototype\n
        prop,\n
        additions =  {\n
\n
            //restore constructor\n
            constructor: Parser,\n
\n
            //instance constants - yuck\n
            DEFAULT_TYPE : 0,\n
            COMBINATOR_TYPE : 1,\n
            MEDIA_FEATURE_TYPE : 2,\n
            MEDIA_QUERY_TYPE : 3,\n
            PROPERTY_NAME_TYPE : 4,\n
            PROPERTY_VALUE_TYPE : 5,\n
            PROPERTY_VALUE_PART_TYPE : 6,\n
            SELECTOR_TYPE : 7,\n
            SELECTOR_PART_TYPE : 8,\n
            SELECTOR_SUB_PART_TYPE : 9,\n
\n
            //-----------------------------------------------------------------\n
            // Grammar\n
            //-----------------------------------------------------------------\n
\n
            _stylesheet: function(){\n
\n
                /*\n
                 * stylesheet\n
                 *  : [ CHARSET_SYM S* STRING S* \';\' ]?\n
                 *    [S|CDO|CDC]* [ import [S|CDO|CDC]* ]*\n
                 *    [ namespace [S|CDO|CDC]* ]*\n
                 *    [ [ ruleset | media | page | font_face | keyframes ] [S|CDO|CDC]* ]*\n
                 *  ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    charset     = null,\n
                    count,\n
                    token,\n
                    tt;\n
\n
                this.fire("startstylesheet");\n
\n
                //try to read character set\n
                this._charset();\n
\n
                this._skipCruft();\n
\n
                //try to read imports - may be more than one\n
                while (tokenStream.peek() == Tokens.IMPORT_SYM){\n
                    this._import();\n
                    this._skipCruft();\n
                }\n
\n
                //try to read namespaces - may be more than one\n
                while (tokenStream.peek() == Tokens.NAMESPACE_SYM){\n
                    this._namespace();\n
                    this._skipCruft();\n
                }\n
\n
                //get the next token\n
                tt = tokenStream.peek();\n
\n
                //try to read the rest\n
                while(tt > Tokens.EOF){\n
\n
                    try {\n
\n
                        switch(tt){\n
                            case Tokens.MEDIA_SYM:\n
                                this._media();\n
                                this._skipCruft();\n
                                break;\n
                            case Tokens.PAGE_SYM:\n
                                this._page();\n
                                this._skipCruft();\n
                                break;\n
                            case Tokens.FONT_FACE_SYM:\n
                                this._font_face();\n
                                this._skipCruft();\n
                                break;\n
                            case Tokens.KEYFRAMES_SYM:\n
                                this._keyframes();\n
                                this._skipCruft();\n
                                break;\n
                            case Tokens.VIEWPORT_SYM:\n
                                this._viewport();\n
                                this._skipCruft();\n
                                break;\n
                            case Tokens.UNKNOWN_SYM:  //unknown @ rule\n
                                tokenStream.get();\n
                                if (!this.options.strict){\n
\n
                                    //fire error event\n
                                    this.fire({\n
                                        type:       "error",\n
                                        error:      null,\n
                                        message:    "Unknown @ rule: " + tokenStream.LT(0).value + ".",\n
                                        line:       tokenStream.LT(0).startLine,\n
                                        col:        tokenStream.LT(0).startCol\n
                                    });\n
\n
                                    //skip braces\n
                                    count=0;\n
                                    while (tokenStream.advance([Tokens.LBRACE, Tokens.RBRACE]) == Tokens.LBRACE){\n
                                        count++;    //keep track of nesting depth\n
                                    }\n
\n
                                    while(count){\n
                                        tokenStream.advance([Tokens.RBRACE]);\n
                                        count--;\n
                                    }\n
\n
                                } else {\n
                                    //not a syntax error, rethrow it\n
                                    throw new SyntaxError("Unknown @ rule.", tokenStream.LT(0).startLine, tokenStream.LT(0).startCol);\n
                                }\n
                                break;\n
                            case Tokens.S:\n
                                this._readWhitespace();\n
                                break;\n
                            default:\n
                                if(!this._ruleset()){\n
\n
                                    //error handling for known issues\n
                                    switch(tt){\n
                                        case Tokens.CHARSET_SYM:\n
                                            token = tokenStream.LT(1);\n
                                            this._charset(false);\n
                                            throw new SyntaxError("@charset not allowed here.", token.startLine, token.startCol);\n
                                        case Tokens.IMPORT_SYM:\n
                                            token = tokenStream.LT(1);\n
                                            this._import(false);\n
                                            throw new SyntaxError("@import not allowed here.", token.startLine, token.startCol);\n
                                        case Tokens.NAMESPACE_SYM:\n
                                            token = tokenStream.LT(1);\n
                                            this._namespace(false);\n
                                            throw new SyntaxError("@namespace not allowed here.", token.startLine, token.startCol);\n
                                        default:\n
                                            tokenStream.get();  //get the last token\n
                                            this._unexpectedToken(tokenStream.token());\n
                                    }\n
\n
                                }\n
                        }\n
                    } catch(ex) {\n
                        if (ex instanceof SyntaxError && !this.options.strict){\n
                            this.fire({\n
                                type:       "error",\n
                                error:      ex,\n
                                message:    ex.message,\n
                                line:       ex.line,\n
                                col:        ex.col\n
                            });\n
                        } else {\n
                            throw ex;\n
                        }\n
                    }\n
\n
                    tt = tokenStream.peek();\n
                }\n
\n
                if (tt != Tokens.EOF){\n
                    this._unexpectedToken(tokenStream.token());\n
                }\n
\n
                this.fire("endstylesheet");\n
            },\n
\n
            _charset: function(emit){\n
                var tokenStream = this._tokenStream,\n
                    charset,\n
                    token,\n
                    line,\n
                    col;\n
\n
                if (tokenStream.match(Tokens.CHARSET_SYM)){\n
                    line = tokenStream.token().startLine;\n
                    col = tokenStream.token().startCol;\n
\n
                    this._readWhitespace();\n
                    tokenStream.mustMatch(Tokens.STRING);\n
\n
                    token = tokenStream.token();\n
                    charset = token.value;\n
\n
                    this._readWhitespace();\n
                    tokenStream.mustMatch(Tokens.SEMICOLON);\n
\n
                    if (emit !== false){\n
                        this.fire({\n
                            type:   "charset",\n
                            charset:charset,\n
                            line:   line,\n
                            col:    col\n
                        });\n
                    }\n
                }\n
            },\n
\n
            _import: function(emit){\n
                /*\n
                 * import\n
                 *   : IMPORT_SYM S*\n
                 *    [STRING|URI] S* media_query_list? \';\' S*\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    tt,\n
                    uri,\n
                    importToken,\n
                    mediaList   = [];\n
\n
                //read import symbol\n
                tokenStream.mustMatch(Tokens.IMPORT_SYM);\n
                importToken = tokenStream.token();\n
                this._readWhitespace();\n
\n
                tokenStream.mustMatch([Tokens.STRING, Tokens.URI]);\n
\n
                //grab the URI value\n
                uri = tokenStream.token().value.replace(/(?:url\\()?["\']([^"\']+)["\']\\)?/, "$1");\n
\n
                this._readWhitespace();\n
\n
                mediaList = this._media_query_list();\n
\n
                //must end with a semicolon\n
                tokenStream.mustMatch(Tokens.SEMICOLON);\n
                this._readWhitespace();\n
\n
                if (emit !== false){\n
                    this.fire({\n
                        type:   "import",\n
                        uri:    uri,\n
                        media:  mediaList,\n
                        line:   importToken.startLine,\n
                        col:    importToken.startCol\n
                    });\n
                }\n
\n
            },\n
\n
            _namespace: function(emit){\n
                /*\n
                 * namespace\n
                 *   : NAMESPACE_SYM S* [namespace_prefix S*]? [STRING|URI] S* \';\' S*\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    line,\n
                    col,\n
                    prefix,\n
                    uri;\n
\n
                //read import symbol\n
                tokenStream.mustMatch(Tokens.NAMESPACE_SYM);\n
                line = tokenStream.token().startLine;\n
                col = tokenStream.token().startCol;\n
                this._readWhitespace();\n
\n
                //it\'s a namespace prefix - no _namespace_prefix() method because it\'s just an IDENT\n
                if (tokenStream.match(Tokens.IDENT)){\n
                    prefix = tokenStream.token().value;\n
                    this._readWhitespace();\n
                }\n
\n
                tokenStream.mustMatch([Tokens.STRING, Tokens.URI]);\n
                /*if (!tokenStream.match(Tokens.STRING)){\n
                    tokenStream.mustMatch(Tokens.URI);\n
                }*/\n
\n
                //grab the URI value\n
                uri = tokenStream.token().value.replace(/(?:url\\()?["\']([^"\']+)["\']\\)?/, "$1");\n
\n
                this._readWhitespace();\n
\n
                //must end with a semicolon\n
                tokenStream.mustMatch(Tokens.SEMICOLON);\n
                this._readWhitespace();\n
\n
                if (emit !== false){\n
                    this.fire({\n
                        type:   "namespace",\n
                        prefix: prefix,\n
                        uri:    uri,\n
                        line:   line,\n
                        col:    col\n
                    });\n
                }\n
\n
            },\n
\n
            _media: function(){\n
                /*\n
                 * media\n
                 *   : MEDIA_SYM S* media_query_list S* \'{\' S* ruleset* \'}\' S*\n
                 *   ;\n
                 */\n
                var tokenStream     = this._tokenStream,\n
                    line,\n
                    col,\n
                    mediaList;//       = [];\n
\n
                //look for @media\n
                tokenStream.mustMatch(Tokens.MEDIA_SYM);\n
                line = tokenStream.token().startLine;\n
                col = tokenStream.token().startCol;\n
\n
                this._readWhitespace();\n
\n
                mediaList = this._media_query_list();\n
\n
                tokenStream.mustMatch(Tokens.LBRACE);\n
                this._readWhitespace();\n
\n
                this.fire({\n
                    type:   "startmedia",\n
                    media:  mediaList,\n
                    line:   line,\n
                    col:    col\n
                });\n
\n
                while(true) {\n
                    if (tokenStream.peek() == Tokens.PAGE_SYM){\n
                        this._page();\n
                    } else   if (tokenStream.peek() == Tokens.FONT_FACE_SYM){\n
                        this._font_face();\n
                    } else if (!this._ruleset()){\n
                        break;\n
                    }\n
                }\n
\n
                tokenStream.mustMatch(Tokens.RBRACE);\n
                this._readWhitespace();\n
\n
                this.fire({\n
                    type:   "endmedia",\n
                    media:  mediaList,\n
                    line:   line,\n
                    col:    col\n
                });\n
            },\n
\n
\n
            //CSS3 Media Queries\n
            _media_query_list: function(){\n
                /*\n
                 * media_query_list\n
                 *   : S* [media_query [ \',\' S* media_query ]* ]?\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    mediaList   = [];\n
\n
\n
                this._readWhitespace();\n
\n
                if (tokenStream.peek() == Tokens.IDENT || tokenStream.peek() == Tokens.LPAREN){\n
                    mediaList.push(this._media_query());\n
                }\n
\n
                while(tokenStream.match(Tokens.COMMA)){\n
                    this._readWhitespace();\n
                    mediaList.push(this._media_query());\n
                }\n
\n
                return mediaList;\n
            },\n
\n
            /*\n
             * Note: "expression" in the grammar maps to the _media_expression\n
             * method.\n
\n
             */\n
            _media_query: function(){\n
                /*\n
                 * media_query\n
                 *   : [ONLY | NOT]? S* media_type S* [ AND S* expression ]*\n
                 *   | expression [ AND S* expression ]*\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    type        = null,\n
                    ident       = null,\n
                    token       = null,\n
                    expressions = [];\n
\n
                if (tokenStream.match(Tokens.IDENT)){\n
                    ident = tokenStream.token().value.toLowerCase();\n
\n
                    //since there\'s no custom tokens for these, need to manually check\n
                    if (ident != "only" && ident != "not"){\n
                        tokenStream.unget();\n
                        ident = null;\n
                    } else {\n
                        token = tokenStream.token();\n
                    }\n
                }\n
\n
                this._readWhitespace();\n
\n
                if (tokenStream.peek() == Tokens.IDENT){\n
                    type = this._media_type();\n
                    if (token === null){\n
                        token = tokenStream.token();\n
                    }\n
                } else if (tokenStream.peek() == Tokens.LPAREN){\n
                    if (token === null){\n
                        token = tokenStream.LT(1);\n
                    }\n
                    expressions.push(this._media_expression());\n
                }\n
\n
                if (type === null && expressions.length === 0){\n
                    return null;\n
                } else {\n
                    this._readWhitespace();\n
                    while (tokenStream.match(Tokens.IDENT)){\n
                        if (tokenStream.token().value.toLowerCase() != "and"){\n
                            this._unexpectedToken(tokenStream.token());\n
                        }\n
\n
                        this._readWhitespace();\n
                        expressions.push(this._media_expression());\n
                    }\n
                }\n
\n
                return new MediaQuery(ident, type, expressions, token.startLine, token.startCol);\n
            },\n
\n
            //CSS3 Media Queries\n
            _media_type: function(){\n
                /*\n
                 * media_type\n
                 *   : IDENT\n
                 *   ;\n
                 */\n
                return this._media_feature();\n
            },\n
\n
            /**\n
             * Note: in CSS3 Media Queries, this is called "expression".\n
             * Renamed here to avoid conflict with CSS3 Selectors\n
             * definition of "expression". Also note that "expr" in the\n
             * grammar now maps to "expression" from CSS3 selectors.\n
             * @method _media_expression\n
             * @private\n
             */\n
            _media_expression: function(){\n
                /*\n
                 * expression\n
                 *  : \'(\' S* media_feature S* [ \':\' S* expr ]? \')\' S*\n
                 *  ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    feature     = null,\n
                    token,\n
                    expression  = null;\n
\n
                tokenStream.mustMatch(Tokens.LPAREN);\n
\n
                feature = this._media_feature();\n
                this._readWhitespace();\n
\n
                if (tokenStream.match(Tokens.COLON)){\n
                    this._readWhitespace();\n
                    token = tokenStream.LT(1);\n
                    expression = this._expression();\n
                }\n
\n
                tokenStream.mustMatch(Tokens.RPAREN);\n
                this._readWhitespace();\n
\n
                return new MediaFeature(feature, (expression ? new SyntaxUnit(expression, token.startLine, token.startCol) : null));\n
            },\n
\n
            //CSS3 Media Queries\n
            _media_feature: function(){\n
                /*\n
                 * media_feature\n
                 *   : IDENT\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream;\n
\n
                tokenStream.mustMatch(Tokens.IDENT);\n
\n
                return SyntaxUnit.fromToken(tokenStream.token());\n
            },\n
\n
            //CSS3 Paged Media\n
            _page: function(){\n
                /*\n
                 * page:\n
                 *    PAGE_SYM S* IDENT? pseudo_page? S*\n
                 *    \'{\' S* [ declaration | margin ]? [ \';\' S* [ declaration | margin ]? ]* \'}\' S*\n
                 *    ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    line,\n
                    col,\n
                    identifier  = null,\n
                    pseudoPage  = null;\n
\n
                //look for @page\n
                tokenStream.mustMatch(Tokens.PAGE_SYM);\n
                line = tokenStream.token().startLine;\n
                col = tokenStream.token().startCol;\n
\n
                this._readWhitespace();\n
\n
                if (tokenStream.match(Tokens.IDENT)){\n
                    identifier = tokenStream.token().value;\n
\n
                    //The value \'auto\' may not be used as a page name and MUST be treated as a syntax error.\n
                    if (identifier.toLowerCase() === "auto"){\n
                        this._unexpectedToken(tokenStream.token());\n
                    }\n
                }\n
\n
                //see if there\'s a colon upcoming\n
                if (tokenStream.peek() == Tokens.COLON){\n
                    pseudoPage = this._pseudo_page();\n
                }\n
\n
                this._readWhitespace();\n
\n
                this.fire({\n
                    type:   "startpage",\n
                    id:     identifier,\n
                    pseudo: pseudoPage,\n
                    line:   line,\n
                    col:    col\n
                });\n
\n
                this._readDeclarations(true, true);\n
\n
                this.fire({\n
                    type:   "endpage",\n
                    id:     identifier,\n
                    pseudo: pseudoPage,\n
                    line:   line,\n
                    col:    col\n
                });\n
\n
            },\n
\n
            //CSS3 Paged Media\n
            _margin: function(){\n
                /*\n
                 * margin :\n
                 *    margin_sym S* \'{\' declaration [ \';\' S* declaration? ]* \'}\' S*\n
                 *    ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    line,\n
                    col,\n
                    marginSym   = this._margin_sym();\n
\n
                if (marginSym){\n
                    line = tokenStream.token().startLine;\n
                    col = tokenStream.token().startCol;\n
\n
                    this.fire({\n
                        type: "startpagemargin",\n
                        margin: marginSym,\n
                        line:   line,\n
                        col:    col\n
                    });\n
\n
                    this._readDeclarations(true);\n
\n
                    this.fire({\n
                        type: "endpagemargin",\n
                        margin: marginSym,\n
                        line:   line,\n
                        col:    col\n
                    });\n
                    return true;\n
                } else {\n
                    return false;\n
                }\n
            },\n
\n
            //CSS3 Paged Media\n
            _margin_sym: function(){\n
\n
                /*\n
                 * margin_sym :\n
                 *    TOPLEFTCORNER_SYM |\n
                 *    TOPLEFT_SYM |\n
                 *    TOPCENTER_SYM |\n
                 *    TOPRIGHT_SYM |\n
                 *    TOPRIGHTCORNER_SYM |\n
                 *    BOTTOMLEFTCORNER_SYM |\n
                 *    BOTTOMLEFT_SYM |\n
                 *    BOTTOMCENTER_SYM |\n
                 *    BOTTOMRIGHT_SYM |\n
                 *    BOTTOMRIGHTCORNER_SYM |\n
                 *    LEFTTOP_SYM |\n
                 *    LEFTMIDDLE_SYM |\n
                 *    LEFTBOTTOM_SYM |\n
                 *    RIGHTTOP_SYM |\n
                 *    RIGHTMIDDLE_SYM |\n
                 *    RIGHTBOTTOM_SYM\n
                 *    ;\n
                 */\n
\n
                var tokenStream = this._tokenStream;\n
\n
                if(tokenStream.match([Tokens.TOPLEFTCORNER_SYM, Tokens.TOPLEFT_SYM,\n
                        Tokens.TOPCENTER_SYM, Tokens.TOPRIGHT_SYM, Tokens.TOPRIGHTCORNER_SYM,\n
                        Tokens.BOTTOMLEFTCORNER_SYM, Tokens.BOTTOMLEFT_SYM,\n
                        Tokens.BOTTOMCENTER_SYM, Tokens.BOTTOMRIGHT_SYM,\n
                        Tokens.BOTTOMRIGHTCORNER_SYM, Tokens.LEFTTOP_SYM,\n
                        Tokens.LEFTMIDDLE_SYM, Tokens.LEFTBOTTOM_SYM, Tokens.RIGHTTOP_SYM,\n
                        Tokens.RIGHTMIDDLE_SYM, Tokens.RIGHTBOTTOM_SYM]))\n
                {\n
                    return SyntaxUnit.fromToken(tokenStream.token());\n
                } else {\n
                    return null;\n
                }\n
\n
            },\n
\n
            _pseudo_page: function(){\n
                /*\n
                 * pseudo_page\n
                 *   : \':\' IDENT\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream;\n
\n
                tokenStream.mustMatch(Tokens.COLON);\n
                tokenStream.mustMatch(Tokens.IDENT);\n
\n
                //TODO: CSS3 Paged Media says only "left", "center", and "right" are allowed\n
\n
                return tokenStream.token().value;\n
            },\n
\n
            _font_face: function(){\n
                /*\n
                 * font_face\n
                 *   : FONT_FACE_SYM S*\n
                 *     \'{\' S* declaration [ \';\' S* declaration ]* \'}\' S*\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    line,\n
                    col;\n
\n
                //look for @page\n
                tokenStream.mustMatch(Tokens.FONT_FACE_SYM);\n
                line = tokenStream.token().startLine;\n
                col = tokenStream.token().startCol;\n
\n
                this._readWhitespace();\n
\n
                this.fire({\n
                    type:   "startfontface",\n
                    line:   line,\n
                    col:    col\n
                });\n
\n
                this._readDeclarations(true);\n
\n
                this.fire({\n
                    type:   "endfontface",\n
                    line:   line,\n
                    col:    col\n
                });\n
            },\n
\n
            _viewport: function(){\n
                /*\n
                 * viewport\n
                 *   : VIEWPORT_SYM S*\n
                 *     \'{\' S* declaration? [ \';\' S* declaration? ]* \'}\' S*\n
                 *   ;\n
                 */\n
                 var tokenStream = this._tokenStream,\n
                    line,\n
                    col;\n
\n
                    tokenStream.mustMatch(Tokens.VIEWPORT_SYM);\n
                    line = tokenStream.token().startLine;\n
                    col = tokenStream.token().startCol;\n
\n
                    this._readWhitespace();\n
\n
                    this.fire({\n
                        type:   "startviewport",\n
                        line:   line,\n
                        col:    col\n
                    });\n
\n
                    this._readDeclarations(true);\n
\n
                    this.fire({\n
                        type:   "endviewport",\n
                        line:   line,\n
                        col:    col\n
                    });\n
\n
            },\n
\n
            _operator: function(inFunction){\n
\n
                /*\n
                 * operator (outside function)\n
                 *  : \'/\' S* | \',\' S* | /( empty )/\n
                 * operator (inside function)\n
                 *  : \'/\' S* | \'+\' S* | \'*\' S* | \'-\' S* /( empty )/\n
                 *  ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    token       = null;\n
\n
                if (tokenStream.match([Tokens.SLASH, Tokens.COMMA]) ||\n
                    (inFunction && tokenStream.match([Tokens.PLUS, Tokens.STAR, Tokens.MINUS]))){\n
                    token =  tokenStream.token();\n
                    this._readWhitespace();\n
                }\n
                return token ? PropertyValuePart.fromToken(token) : null;\n
\n
            },\n
\n
            _combinator: function(){\n
\n
                /*\n
                 * combinator\n
                 *  : PLUS S* | GREATER S* | TILDE S* | S+\n
                 *  ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    value       = null,\n
                    token;\n
\n
                if(tokenStream.match([Tokens.PLUS, Tokens.GREATER, Tokens.TILDE])){\n
                    token = tokenStream.token();\n
                    value = new Combinator(token.value, token.startLine, token.startCol);\n
                    this._readWhitespace();\n
                }\n
\n
                return value;\n
            },\n
\n
            _unary_operator: function(){\n
\n
                /*\n
                 * unary_operator\n
                 *  : \'-\' | \'+\'\n
                 *  ;\n
                 */\n
\n
                var tokenStream = this._tokenStream;\n
\n
                if (tokenStream.match([Tokens.MINUS, Tokens.PLUS])){\n
                    return tokenStream.token().value;\n
                } else {\n
                    return null;\n
                }\n
            },\n
\n
            _property: function(){\n
\n
                /*\n
                 * property\n
                 *   : IDENT S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    value       = null,\n
                    hack        = null,\n
                    tokenValue,\n
                    token,\n
                    line,\n
                    col;\n
\n
                //check for star hack - throws error if not allowed\n
                if (tokenStream.peek() == Tokens.STAR && this.options.starHack){\n
                    tokenStream.get();\n
                    token = tokenStream.token();\n
                    hack = token.value;\n
                    line = token.startLine;\n
                    col = token.startCol;\n
                }\n
\n
                if(tokenStream.match(Tokens.IDENT)){\n
                    token = tokenStream.token();\n
                    tokenValue = token.value;\n
\n
                    //check for underscore hack - no error if not allowed because it\'s valid CSS syntax\n
                    if (tokenValue.charAt(0) == "_" && this.options.underscoreHack){\n
                        hack = "_";\n
                        tokenValue = tokenValue.substring(1);\n
                    }\n
\n
                    value = new PropertyName(tokenValue, hack, (line||token.startLine), (col||token.startCol));\n
                    this._readWhitespace();\n
                }\n
\n
                return value;\n
            },\n
\n
            //Augmented with CSS3 Selectors\n
            _ruleset: function(){\n
                /*\n
                 * ruleset\n
                 *   : selectors_group\n
                 *     \'{\' S* declaration? [ \';\' S* declaration? ]* \'}\' S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    tt,\n
                    selectors;\n
\n
\n
                /*\n
                 * Error Recovery: If even a single selector fails to parse,\n
                 * then the entire ruleset should be thrown away.\n
                 */\n
                try {\n
                    selectors = this._selectors_group();\n
                } catch (ex){\n
                    if (ex instanceof SyntaxError && !this.options.strict){\n
\n
                        //fire error event\n
                        this.fire({\n
                            type:       "error",\n
                            error:      ex,\n
                            message:    ex.message,\n
                            line:       ex.line,\n
                            col:        ex.col\n
                        });\n
\n
                        //skip over everything until closing brace\n
                        tt = tokenStream.advance([Tokens.RBRACE]);\n
                        if (tt == Tokens.RBRACE){\n
                            //if there\'s a right brace, the rule is finished so don\'t do anything\n
                        } else {\n
                            //otherwise, rethrow the error because it wasn\'t handled properly\n
                            throw ex;\n
                        }\n
\n
                    } else {\n
                        //not a syntax error, rethrow it\n
                        throw ex;\n
                    }\n
\n
                    //trigger parser to continue\n
                    return true;\n
                }\n
\n
                //if it got here, all selectors parsed\n
                if (selectors){\n
\n
                    this.fire({\n
                        type:       "startrule",\n
                        selectors:  selectors,\n
                        line:       selectors[0].line,\n
                        col:        selectors[0].col\n
                    });\n
\n
                    this._readDeclarations(true);\n
\n
                    this.fire({\n
                        type:       "endrule",\n
                        selectors:  selectors,\n
                        line:       selectors[0].line,\n
                        col:        selectors[0].col\n
                    });\n
\n
                }\n
\n
                return selectors;\n
\n
            },\n
\n
            //CSS3 Selectors\n
            _selectors_group: function(){\n
\n
                /*\n
                 * selectors_group\n
                 *   : selector [ COMMA S* selector ]*\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    selectors   = [],\n
                    selector;\n
\n
                selector = this._selector();\n
                if (selector !== null){\n
\n
                    selectors.push(selector);\n
                    while(tokenStream.match(Tokens.COMMA)){\n
                        this._readWhitespace();\n
                        selector = this._selector();\n
                        if (selector !== null){\n
                            selectors.push(selector);\n
                        } else {\n
                            this._unexpectedToken(tokenStream.LT(1));\n
                        }\n
                    }\n
                }\n
\n
                return selectors.length ? selectors : null;\n
            },\n
\n
            //CSS3 Selectors\n
            _selector: function(){\n
                /*\n
                 * selector\n
                 *   : simple_selector_sequence [ combinator simple_selector_sequence ]*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    selector    = [],\n
                    nextSelector = null,\n
                    combinator  = null,\n
                    ws          = null;\n
\n
                //if there\'s no simple selector, then there\'s no selector\n
                nextSelector = this._simple_selector_sequence();\n
                if (nextSelector === null){\n
                    return null;\n
                }\n
\n
                selector.push(nextSelector);\n
\n
                do {\n
\n
                    //look for a combinator\n
                    combinator = this._combinator();\n
\n
                    if (combinator !== null){\n
                        selector.push(combinator);\n
                        nextSelector = this._simple_selector_sequence();\n
\n
                        //there must be a next selector\n
                        if (nextSelector === null){\n
                            this._unexpectedToken(tokenStream.LT(1));\n
                        } else {\n
\n
                            //nextSelector is an instance of SelectorPart\n
                            selector.push(nextSelector);\n
                        }\n
                    } else {\n
\n
                        //if there\'s not whitespace, we\'re done\n
                        if (this._readWhitespace()){\n
\n
                            //add whitespace separator\n
                            ws = new Combinator(tokenStream.token().value, tokenStream.token().startLine, tokenStream.token().startCol);\n
\n
                            //combinator is not required\n
                            combinator = this._combinator();\n
\n
                            //selector is required if there\'s a combinator\n
                            nextSelector = this._simple_selector_sequence();\n
                            if (nextSelector === null){\n
                                if (combinator !== null){\n
                                    this._unexpectedToken(tokenStream.LT(1));\n
                                }\n
                            } else {\n
\n
                                if (combinator !== null){\n
                                    selector.push(combinator);\n
                                } else {\n
                                    selector.push(ws);\n
                                }\n
\n
                                selector.push(nextSelector);\n
                            }\n
                        } else {\n
                            break;\n
                        }\n
\n
                    }\n
                } while(true);\n
\n
                return new Selector(selector, selector[0].line, selector[0].col);\n
            },\n
\n
            //CSS3 Selectors\n
            _simple_selector_sequence: function(){\n
                /*\n
                 * simple_selector_sequence\n
                 *   : [ type_selector | universal ]\n
                 *     [ HASH | class | attrib | pseudo | negation ]*\n
                 *   | [ HASH | class | attrib | pseudo | negation ]+\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
\n
                    //parts of a simple selector\n
                    elementName = null,\n
                    modifiers   = [],\n
\n
                    //complete selector text\n
                    selectorText= "",\n
\n
                    //the different parts after the element name to search for\n
                    components  = [\n
                        //HASH\n
                        function(){\n
                            return tokenStream.match(Tokens.HASH) ?\n
                                    new SelectorSubPart(tokenStream.token().value, "id", tokenStream.token().startLine, tokenStream.token().startCol) :\n
                                    null;\n
                        },\n
                        this._class,\n
                        this._attrib,\n
                        this._pseudo,\n
                        this._negation\n
                    ],\n
                    i           = 0,\n
                    len         = components.length,\n
                    component   = null,\n
                    found       = false,\n
                    line,\n
                    col;\n
\n
\n
                //get starting line and column for the selector\n
                line = tokenStream.LT(1).startLine;\n
                col = tokenStream.LT(1).startCol;\n
\n
                elementName = this._type_selector();\n
                if (!elementName){\n
                    elementName = this._universal();\n
                }\n
\n
                if (elementName !== null){\n
                    selectorText += elementName;\n
                }\n
\n
                while(true){\n
\n
                    //whitespace means we\'re done\n
                    if (tokenStream.peek() === Tokens.S){\n
                        break;\n
                    }\n
\n
                    //check for each component\n
                    while(i < len && component === null){\n
                        component = components[i++].call(this);\n
                    }\n
\n
                    if (component === null){\n
\n
                        //we don\'t have a selector\n
                        if (selectorText === ""){\n
                            return null;\n
                        } else {\n
                            break;\n
                        }\n
                    } else {\n
                        i = 0;\n
                        modifiers.push(component);\n
                        selectorText += component.toString();\n
                        component = null;\n
                    }\n
                }\n
\n
\n
                return selectorText !== "" ?\n
                        new SelectorPart(elementName, modifiers, selectorText, line, col) :\n
                        null;\n
            },\n
\n
            //CSS3 Selectors\n
            _type_selector: function(){\n
                /*\n
                 * type_selector\n
                 *   : [ namespace_prefix ]? element_name\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    ns          = this._namespace_prefix(),\n
                    elementName = this._element_name();\n
\n
                if (!elementName){\n
                    /*\n
                     * Need to back out the namespace that was read due to both\n
                     * type_selector and universal reading namespace_prefix\n
                     * first. Kind of hacky, but only way I can figure out\n
                     * right now how to not change the grammar.\n
                     */\n
                    if (ns){\n
                        tokenStream.unget();\n
                        if (ns.length > 1){\n
                            tokenStream.unget();\n
                        }\n
                    }\n
\n
                    return null;\n
                } else {\n
                    if (ns){\n
                        elementName.text = ns + elementName.text;\n
                        elementName.col -= ns.length;\n
                    }\n
                    return elementName;\n
                }\n
            },\n
\n
            //CSS3 Selectors\n
            _class: function(){\n
                /*\n
                 * class\n
                 *   : \'.\' IDENT\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    token;\n
\n
                if (tokenStream.match(Tokens.DOT)){\n
                    tokenStream.mustMatch(Tokens.IDENT);\n
                    token = tokenStream.token();\n
                    return new SelectorSubPart("." + token.value, "class", token.startLine, token.startCol - 1);\n
                } else {\n
                    return null;\n
                }\n
\n
            },\n
\n
            //CSS3 Selectors\n
            _element_name: function(){\n
                /*\n
                 * element_name\n
                 *   : IDENT\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    token;\n
\n
                if (tokenStream.match(Tokens.IDENT)){\n
                    token = tokenStream.token();\n
                    return new SelectorSubPart(token.value, "elementName", token.startLine, token.startCol);\n
\n
                } else {\n
                    return null;\n
                }\n
            },\n
\n
            //CSS3 Selectors\n
            _namespace_prefix: function(){\n
                /*\n
                 * namespace_prefix\n
                 *   : [ IDENT | \'*\' ]? \'|\'\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    value       = "";\n
\n
                //verify that this is a namespace prefix\n
                if (tokenStream.LA(1) === Tokens.PIPE || tokenStream.LA(2) === Tokens.PIPE){\n
\n
                    if(tokenStream.match([Tokens.IDENT, Tokens.STAR])){\n
                        value += tokenStream.token().value;\n
                    }\n
\n
                    tokenStream.mustMatch(Tokens.PIPE);\n
                    value += "|";\n
\n
                }\n
\n
                return value.length ? value : null;\n
            },\n
\n
            //CSS3 Selectors\n
            _universal: function(){\n
                /*\n
                 * universal\n
                 *   : [ namespace_prefix ]? \'*\'\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    value       = "",\n
                    ns;\n
\n
                ns = this._namespace_prefix();\n
                if(ns){\n
                    value += ns;\n
                }\n
\n
                if(tokenStream.match(Tokens.STAR)){\n
                    value += "*";\n
                }\n
\n
                return value.length ? value : null;\n
\n
           },\n
\n
            //CSS3 Selectors\n
            _attrib: function(){\n
                /*\n
                 * attrib\n
                 *   : \'[\' S* [ namespace_prefix ]? IDENT S*\n
                 *         [ [ PREFIXMATCH |\n
                 *             SUFFIXMATCH |\n
                 *             SUBSTRINGMATCH |\n
                 *             \'=\' |\n
                 *             INCLUDES |\n
                 *             DASHMATCH ] S* [ IDENT | STRING ] S*\n
                 *         ]? \']\'\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    value       = null,\n
                    ns,\n
                    token;\n
\n
                if (tokenStream.match(Tokens.LBRACKET)){\n
                    token = tokenStream.token();\n
                    value = token.value;\n
                    value += this._readWhitespace();\n
\n
                    ns = this._namespace_prefix();\n
\n
                    if (ns){\n
                        value += ns;\n
                    }\n
\n
                    tokenStream.mustMatch(Tokens.IDENT);\n
                    value += tokenStream.token().value;\n
                    value += this._readWhitespace();\n
\n
                    if(tokenStream.match([Tokens.PREFIXMATCH, Tokens.SUFFIXMATCH, Tokens.SUBSTRINGMATCH,\n
                            Tokens.EQUALS, Tokens.INCLUDES, Tokens.DASHMATCH])){\n
\n
                        value += tokenStream.token().value;\n
                        value += this._readWhitespace();\n
\n
                        tokenStream.mustMatch([Tokens.IDENT, Tokens.STRING]);\n
                        value += tokenStream.token().value;\n
                        value += this._readWhitespace();\n
                    }\n
\n
                    tokenStream.mustMatch(Tokens.RBRACKET);\n
\n
                    return new SelectorSubPart(value + "]", "attribute", token.startLine, token.startCol);\n
                } else {\n
                    return null;\n
                }\n
            },\n
\n
            //CSS3 Selectors\n
            _pseudo: function(){\n
\n
                /*\n
                 * pseudo\n
                 *   : \':\' \':\'? [ IDENT | functional_pseudo ]\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    pseudo      = null,\n
                    colons      = ":",\n
                    line,\n
                    col;\n
\n
                if (tokenStream.match(Tokens.COLON)){\n
\n
                    if (tokenStream.match(Tokens.COLON)){\n
                        colons += ":";\n
                    }\n
\n
                    if (tokenStream.match(Tokens.IDENT)){\n
                        pseudo = tokenStream.token().value;\n
                        line = tokenStream.token().startLine;\n
                        col = tokenStream.token().startCol - colons.length;\n
                    } else if (tokenStream.peek() == Tokens.FUNCTION){\n
                        line = tokenStream.LT(1).startLine;\n
                        col = tokenStream.LT(1).startCol - colons.length;\n
                        pseudo = this._functional_pseudo();\n
                    }\n
\n
                    if (pseudo){\n
                        pseudo = new SelectorSubPart(colons + pseudo, "pseudo", line, col);\n
                    }\n
                }\n
\n
                return pseudo;\n
            },\n
\n
            //CSS3 Selectors\n
            _functional_pseudo: function(){\n
                /*\n
                 * functional_pseudo\n
                 *   : FUNCTION S* expression \')\'\n
                 *   ;\n
                */\n
\n
                var tokenStream = this._tokenStream,\n
                    value = null;\n
\n
                if(tokenStream.match(Tokens.FUNCTION)){\n
                    value = tokenStream.token().value;\n
                    value += this._readWhitespace();\n
                    value += this._expression();\n
                    tokenStream.mustMatch(Tokens.RPAREN);\n
                    value += ")";\n
                }\n
\n
                return value;\n
            },\n
\n
            //CSS3 Selectors\n
            _expression: function(){\n
                /*\n
                 * expression\n
                 *   : [ [ PLUS | \'-\' | DIMENSION | NUMBER | STRING | IDENT ] S* ]+\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    value       = "";\n
\n
                while(tokenStream.match([Tokens.PLUS, Tokens.MINUS, Tokens.DIMENSION,\n
                        Tokens.NUMBER, Tokens.STRING, Tokens.IDENT, Tokens.LENGTH,\n
                        Tokens.FREQ, Tokens.ANGLE, Tokens.TIME,\n
                        Tokens.RESOLUTION, Tokens.SLASH])){\n
\n
                    value += tokenStream.token().value;\n
                    value += this._readWhitespace();\n
                }\n
\n
                return value.length ? value : null;\n
\n
            },\n
\n
            //CSS3 Selectors\n
            _negation: function(){\n
                /*\n
                 * negation\n
                 *   : NOT S* negation_arg S* \')\'\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    line,\n
                    col,\n
                    value       = "",\n
                    arg,\n
                    subpart     = null;\n
\n
                if (tokenStream.match(Tokens.NOT)){\n
                    value = tokenStream.token().value;\n
                    line = tokenStream.token().startLine;\n
                    col = tokenStream.token().startCol;\n
                    value += this._readWhitespace();\n
                    arg = this._negation_arg();\n
                    value += arg;\n
                    value += this._readWhitespace();\n
                    tokenStream.match(Tokens.RPAREN);\n
                    value += tokenStream.token().value;\n
\n
                    subpart = new SelectorSubPart(value, "not", line, col);\n
                    subpart.args.push(arg);\n
                }\n
\n
                return subpart;\n
            },\n
\n
            //CSS3 Selectors\n
            _negation_arg: function(){\n
                /*\n
                 * negation_arg\n
                 *   : type_selector | universal | HASH | class | attrib | pseudo\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    args        = [\n
                        this._type_selector,\n
                        this._universal,\n
                        function(){\n
                            return tokenStream.match(Tokens.HASH) ?\n
                                    new SelectorSubPart(tokenStream.token().value, "id", tokenStream.token().startLine, tokenStream.token().startCol) :\n
                                    null;\n
                        },\n
                        this._class,\n
                        this._attrib,\n
                        this._pseudo\n
                    ],\n
                    arg         = null,\n
                    i           = 0,\n
                    len         = args.length,\n
                    elementName,\n
                    line,\n
                    col,\n
                    part;\n
\n
                line = tokenStream.LT(1).startLine;\n
                col = tokenStream.LT(1).startCol;\n
\n
                while(i < len && arg === null){\n
\n
                    arg = args[i].call(this);\n
                    i++;\n
                }\n
\n
                //must be a negation arg\n
                if (arg === null){\n
                    this._unexpectedToken(tokenStream.LT(1));\n
                }\n
\n
                //it\'s an element name\n
                if (arg.type == "elementName"){\n
                    part = new SelectorPart(arg, [], arg.toString(), line, col);\n
                } else {\n
                    part = new SelectorPart(null, [arg], arg.toString(), line, col);\n
                }\n
\n
                return part;\n
            },\n
\n
            _declaration: function(){\n
\n
                /*\n
                 * declaration\n
                 *   : property \':\' S* expr prio?\n
                 *   | /( empty )/\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    property    = null,\n
                    expr        = null,\n
                    prio        = null,\n
                    error       = null,\n
                    invalid     = null,\n
                    propertyName= "";\n
\n
                property = this._property();\n
                if (property !== null){\n
\n
                    tokenStream.mustMatch(Tokens.COLON);\n
                    this._readWhitespace();\n
\n
                    expr = this._expr();\n
\n
                    //if there\'s no parts for the value, it\'s an error\n
                    if (!expr || expr.length === 0){\n
                        this._unexpectedToken(tokenStream.LT(1));\n
                    }\n
\n
                    prio = this._prio();\n
\n
                    /*\n
                     * If hacks should be allowed, then only check the root\n
                     * property. If hacks should not be allowed, treat\n
                     * _property or *property as invalid properties.\n
                     */\n
                    propertyName = property.toString();\n
                    if (this.options.starHack && property.hack == "*" ||\n
                            this.options.underscoreHack && property.hack == "_") {\n
\n
                        propertyName = property.text;\n
                    }\n
\n
                    try {\n
                        this._validateProperty(propertyName, expr);\n
                    } catch (ex) {\n
                        invalid = ex;\n
                    }\n
\n
                    this.fire({\n
                        type:       "property",\n
                        property:   property,\n
                        value:      expr,\n
                        important:  prio,\n
                        line:       property.line,\n
                        col:        property.col,\n
                        invalid:    invalid\n
                    });\n
\n
                    return true;\n
                } else {\n
                    return false;\n
                }\n
            },\n
\n
            _prio: function(){\n
                /*\n
                 * prio\n
                 *   : IMPORTANT_SYM S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    result      = tokenStream.match(Tokens.IMPORTANT_SYM);\n
\n
                this._readWhitespace();\n
                return result;\n
            },\n
\n
            _expr: function(inFunction){\n
                /*\n
                 * expr\n
                 *   : term [ operator term ]*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    values      = [],\n
                    //valueParts    = [],\n
                    value       = null,\n
                    operator    = null;\n
\n
                value = this._term();\n
                if (value !== null){\n
\n
                    values.push(value);\n
\n
                    do {\n
                        operator = this._operator(inFunction);\n
\n
                        //if there\'s an operator, keep building up the value parts\n
                        if (operator){\n
                            values.push(operator);\n
                        } /*else {\n
                            //if there\'s not an operator, you have a full value\n
                            values.push(new PropertyValue(valueParts, valueParts[0].line, valueParts[0].col));\n
                            valueParts = [];\n
                        }*/\n
\n
                        value = this._term();\n
\n
                        if (value === null){\n
                            break;\n
                        } else {\n
                            values.push(value);\n
                        }\n
                    } while(true);\n
                }\n
\n
                //cleanup\n
                /*if (valueParts.length){\n
                    values.push(new PropertyValue(valueParts, valueParts[0].line, valueParts[0].col));\n
                }*/\n
\n
                return values.length > 0 ? new PropertyValue(values, values[0].line, values[0].col) : null;\n
            },\n
\n
            _term: function(){\n
\n
                /*\n
                 * term\n
                 *   : unary_operator?\n
                 *     [ NUMBER S* | PERCENTAGE S* | LENGTH S* | ANGLE S* |\n
                 *       TIME S* | FREQ S* | function | ie_function ]\n
                 *   | STRING S* | IDENT S* | URI S* | UNICODERANGE S* | hexcolor\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    unary       = null,\n
                    value       = null,\n
                    token,\n
                    line,\n
                    col;\n
\n
                //returns the operator or null\n
                unary = this._unary_operator();\n
                if (unary !== null){\n
                    line = tokenStream.token().startLine;\n
                    col = tokenStream.token().startCol;\n
                }\n
\n
                //exception for IE filters\n
                if (tokenStream.peek() == Tokens.IE_FUNCTION && this.options.ieFilters){\n
\n
                    value = this._ie_function();\n
                    if (unary === null){\n
                        line = tokenStream.token().startLine;\n
                        col = tokenStream.token().startCol;\n
                    }\n
\n
                //see if there\'s a simple match\n
                } else if (tokenStream.match([Tokens.NUMBER, Tokens.PERCENTAGE, Tokens.LENGTH,\n
                        Tokens.ANGLE, Tokens.TIME,\n
                        Tokens.FREQ, Tokens.STRING, Tokens.IDENT, Tokens.URI, Tokens.UNICODE_RANGE])){\n
\n
                    value = tokenStream.token().value;\n
                    if (unary === null){\n
                        line = tokenStream.token().startLine;\n
                        col = tokenStream.token().startCol;\n
                    }\n
                    this._readWhitespace();\n
                } else {\n
\n
                    //see if it\'s a color\n
                    token = this._hexcolor();\n
                    if (token === null){\n
\n
                        //if there\'s no unary, get the start of the next token for line/col info\n
                        if (unary === null){\n
                            line = tokenStream.LT(1).startLine;\n
                            col = tokenStream.LT(1).startCol;\n
                        }\n
\n
                        //has to be a function\n
                        if (value === null){\n
\n
                            /*\n
                             * This checks for alpha(opacity=0) style of IE\n
                             * functions. IE_FUNCTION only presents progid: style.\n
                             */\n
                            if (tokenStream.LA(3) == Tokens.EQUALS && this.options.ieFilters){\n
                                value = this._ie_function();\n
                            } else {\n
                                value = this._function();\n
                            }\n
                        }\n
\n
                        /*if (value === null){\n
                            return null;\n
                            //throw new Error("Expected identifier at line " + tokenStream.token().startLine + ", character " +  tokenStream.token().startCol + ".");\n
                        }*/\n
\n
                    } else {\n
                        value = token.value;\n
                        if (unary === null){\n
                            line = token.startLine;\n
                            col = token.startCol;\n
                        }\n
                    }\n
\n
                }\n
\n
                return value !== null ?\n
                        new PropertyValuePart(unary !== null ? unary + value : value, line, col) :\n
                        null;\n
\n
            },\n
\n
            _function: function(){\n
\n
                /*\n
                 * function\n
                 *   : FUNCTION S* expr \')\' S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    functionText = null,\n
                    expr        = null,\n
                    lt;\n
\n
                if (tokenStream.match(Tokens.FUNCTION)){\n
                    functionText = tokenStream.token().value;\n
                    this._readWhitespace();\n
                    expr = this._expr(true);\n
                    functionText += expr;\n
\n
                    //START: Horrible hack in case it\'s an IE filter\n
                    if (this.options.ieFilters && tokenStream.peek() == Tokens.EQUALS){\n
                        do {\n
\n
                            if (this._readWhitespace()){\n
                                functionText += tokenStream.token().value;\n
                            }\n
\n
                            //might be second time in the loop\n
                            if (tokenStream.LA(0) == Tokens.COMMA){\n
                                functionText += tokenStream.token().value;\n
                            }\n
\n
                            tokenStream.match(Tokens.IDENT);\n
                            functionText += tokenStream.token().value;\n
\n
                            tokenStream.match(Tokens.EQUALS);\n
                            functionText += tokenStream.token().value;\n
\n
                            //functionText += this._term();\n
                            lt = tokenStream.peek();\n
                            while(lt != Tokens.COMMA && lt != Tokens.S && lt != Tokens.RPAREN){\n
                                tokenStream.get();\n
                                functionText += tokenStream.token().value;\n
                                lt = tokenStream.peek();\n
                            }\n
                        } while(tokenStream.match([Tokens.COMMA, Tokens.S]));\n
                    }\n
\n
                    //END: Horrible Hack\n
\n
                    tokenStream.match(Tokens.RPAREN);\n
                    functionText += ")";\n
                    this._readWhitespace();\n
                }\n
\n
                return functionText;\n
            },\n
\n
            _ie_function: function(){\n
\n
                /* (My own extension)\n
                 * ie_function\n
                 *   : IE_FUNCTION S* IDENT \'=\' term [S* \',\'? IDENT \'=\' term]+ \')\' S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    functionText = null,\n
                    expr        = null,\n
                    lt;\n
\n
                //IE function can begin like a regular function, too\n
                if (tokenStream.match([Tokens.IE_FUNCTION, Tokens.FUNCTION])){\n
                    functionText = tokenStream.token().value;\n
\n
                    do {\n
\n
                        if (this._readWhitespace()){\n
                            functionText += tokenStream.token().value;\n
                        }\n
\n
                        //might be second time in the loop\n
                        if (tokenStream.LA(0) == Tokens.COMMA){\n
                            functionText += tokenStream.token().value;\n
                        }\n
\n
                        tokenStream.match(Tokens.IDENT);\n
                        functionText += tokenStream.token().value;\n
\n
                        tokenStream.match(Tokens.EQUALS);\n
                        functionText += tokenStream.token().value;\n
\n
                        //functionText += this._term();\n
                        lt = tokenStream.peek();\n
                        while(lt != Tokens.COMMA && lt != Tokens.S && lt != Tokens.RPAREN){\n
                            tokenStream.get();\n
                            functionText += tokenStream.token().value;\n
                            lt = tokenStream.peek();\n
                        }\n
                    } while(tokenStream.match([Tokens.COMMA, Tokens.S]));\n
\n
                    tokenStream.match(Tokens.RPAREN);\n
                    functionText += ")";\n
                    this._readWhitespace();\n
                }\n
\n
                return functionText;\n
            },\n
\n
            _hexcolor: function(){\n
                /*\n
                 * There is a constraint on the color that it must\n
                 * have either 3 or 6 hex-digits (i.e., [0-9a-fA-F])\n
                 * after the "#"; e.g., "#000" is OK, but "#abcd" is not.\n
                 *\n
                 * hexcolor\n
                 *   : HASH S*\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    token = null,\n
                    color;\n
\n
                if(tokenStream.match(Tokens.HASH)){\n
\n
                    //need to do some validation here\n
\n
                    token = tokenStream.token();\n
                    color = token.value;\n
                    if (!/#[a-f0-9]{3,6}/i.test(color)){\n
                        throw new SyntaxError("Expected a hex color but found \'" + color + "\' at line " + token.startLine + ", col " + token.startCol + ".", token.startLine, token.startCol);\n
                    }\n
                    this._readWhitespace();\n
                }\n
\n
                return token;\n
            },\n
\n
            //-----------------------------------------------------------------\n
            // Animations methods\n
            //-----------------------------------------------------------------\n
\n
            _keyframes: function(){\n
\n
                /*\n
                 * keyframes:\n
                 *   : KEYFRAMES_SYM S* keyframe_name S* \'{\' S* keyframe_rule* \'}\' {\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    token,\n
                    tt,\n
                    name,\n
                    prefix = "";\n
\n
                tokenStream.mustMatch(Tokens.KEYFRAMES_SYM);\n
                token = tokenStream.token();\n
                if (/^@\\-([^\\-]+)\\-/.test(token.value)) {\n
                    prefix = RegExp.$1;\n
                }\n
\n
                this._readWhitespace();\n
                name = this._keyframe_name();\n
\n
                this._readWhitespace();\n
                tokenStream.mustMatch(Tokens.LBRACE);\n
\n
                this.fire({\n
                    type:   "startkeyframes",\n
                    name:   name,\n
                    prefix: prefix,\n
                    line:   token.startLine,\n
                    col:    token.startCol\n
                });\n
\n
                this._readWhitespace();\n
                tt = tokenStream.peek();\n
\n
                //check for key\n
                while(tt == Tokens.IDENT || tt == Tokens.PERCENTAGE) {\n
                    this._keyframe_rule();\n
                    this._readWhitespace();\n
                    tt = tokenStream.peek();\n
                }\n
\n
                this.fire({\n
                    type:   "endkeyframes",\n
                    name:   name,\n
                    prefix: prefix,\n
                    line:   token.startLine,\n
                    col:    token.startCol\n
                });\n
\n
                this._readWhitespace();\n
                tokenStream.mustMatch(Tokens.RBRACE);\n
\n
            },\n
\n
            _keyframe_name: function(){\n
\n
                /*\n
                 * keyframe_name:\n
                 *   : IDENT\n
                 *   | STRING\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    token;\n
\n
                tokenStream.mustMatch([Tokens.IDENT, Tokens.STRING]);\n
                return SyntaxUnit.fromToken(tokenStream.token());\n
            },\n
\n
            _keyframe_rule: function(){\n
\n
                /*\n
                 * keyframe_rule:\n
                 *   : key_list S*\n
                 *     \'{\' S* declaration [ \';\' S* declaration ]* \'}\' S*\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    token,\n
                    keyList = this._key_list();\n
\n
                this.fire({\n
                    type:   "startkeyframerule",\n
                    keys:   keyList,\n
                    line:   keyList[0].line,\n
                    col:    keyList[0].col\n
                });\n
\n
                this._readDeclarations(true);\n
\n
                this.fire({\n
                    type:   "endkeyframerule",\n
                    keys:   keyList,\n
                    line:   keyList[0].line,\n
                    col:    keyList[0].col\n
                });\n
\n
            },\n
\n
            _key_list: function(){\n
\n
                /*\n
                 * key_list:\n
                 *   : key [ S* \',\' S* key]*\n
                 *   ;\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    token,\n
                    key,\n
                    keyList = [];\n
\n
                //must be least one key\n
                keyList.push(this._key());\n
\n
                this._readWhitespace();\n
\n
                while(tokenStream.match(Tokens.COMMA)){\n
                    this._readWhitespace();\n
                    keyList.push(this._key());\n
                    this._readWhitespace();\n
                }\n
\n
                return keyList;\n
            },\n
\n
            _key: function(){\n
                /*\n
                 * There is a restriction that IDENT can be only "from" or "to".\n
                 *\n
                 * key\n
                 *   : PERCENTAGE\n
                 *   | IDENT\n
                 *   ;\n
                 */\n
\n
                var tokenStream = this._tokenStream,\n
                    token;\n
\n
                if (tokenStream.match(Tokens.PERCENTAGE)){\n
                    return SyntaxUnit.fromToken(tokenStream.token());\n
                } else if (tokenStream.match(Tokens.IDENT)){\n
                    token = tokenStream.token();\n
\n
                    if (/from|to/i.test(token.value)){\n
                        return SyntaxUnit.fromToken(token);\n
                    }\n
\n
                    tokenStream.unget();\n
                }\n
\n
                //if it gets here, there wasn\'t a valid token, so time to explode\n
                this._unexpectedToken(tokenStream.LT(1));\n
            },\n
\n
            //-----------------------------------------------------------------\n
            // Helper methods\n
            //-----------------------------------------------------------------\n
\n
            /**\n
             * Not part of CSS grammar, but useful for skipping over\n
             * combination of white space and HTML-style comments.\n
             * @return {void}\n
             * @method _skipCruft\n
             * @private\n
             */\n
            _skipCruft: function(){\n
                while(this._tokenStream.match([Tokens.S, Tokens.CDO, Tokens.CDC])){\n
                    //noop\n
                }\n
            },\n
\n
            /**\n
             * Not part of CSS grammar, but this pattern occurs frequently\n
             * in the official CSS grammar. Split out here to eliminate\n
             * duplicate code.\n
             * @param {Boolean} checkStart Indicates if the rule should check\n
             *      for the left brace at the beginning.\n
             * @param {Boolean} readMargins Indicates if the rule should check\n
             *      for margin patterns.\n
             * @return {void}\n
             * @method _readDeclarations\n
             * @private\n
             */\n
            _readDeclarations: function(checkStart, readMargins){\n
                /*\n
                 * Reads the pattern\n
                 * S* \'{\' S* declaration [ \';\' S* declaration ]* \'}\' S*\n
                 * or\n
                 * S* \'{\' S* [ declaration | margin ]? [ \';\' S* [ declaration | margin ]? ]* \'}\' S*\n
                 * Note that this is how it is described in CSS3 Paged Media, but is actually incorrect.\n
                 * A semicolon is only necessary following a declaration is there\'s another declaration\n
                 * or margin afterwards.\n
                 */\n
                var tokenStream = this._tokenStream,\n
                    tt;\n
\n
\n
                this._readWhitespace();\n
\n
                if (checkStart){\n
                    tokenStream.mustMatch(Tokens.LBRACE);\n
                }\n
\n
                this._readWhitespace();\n
\n
                try {\n
\n
                    while(true){\n
\n
                        if (tokenStream.match(Tokens.SEMICOLON) || (readMargins && this._margin())){\n
            

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

                //noop\n
                        } else if (this._declaration()){\n
                            if (!tokenStream.match(Tokens.SEMICOLON)){\n
                                break;\n
                            }\n
                        } else {\n
                            break;\n
                        }\n
\n
                        //if ((!this._margin() && !this._declaration()) || !tokenStream.match(Tokens.SEMICOLON)){\n
                        //    break;\n
                        //}\n
                        this._readWhitespace();\n
                    }\n
\n
                    tokenStream.mustMatch(Tokens.RBRACE);\n
                    this._readWhitespace();\n
\n
                } catch (ex) {\n
                    if (ex instanceof SyntaxError && !this.options.strict){\n
\n
                        //fire error event\n
                        this.fire({\n
                            type:       "error",\n
                            error:      ex,\n
                            message:    ex.message,\n
                            line:       ex.line,\n
                            col:        ex.col\n
                        });\n
\n
                        //see if there\'s another declaration\n
                        tt = tokenStream.advance([Tokens.SEMICOLON, Tokens.RBRACE]);\n
                        if (tt == Tokens.SEMICOLON){\n
                            //if there\'s a semicolon, then there might be another declaration\n
                            this._readDeclarations(false, readMargins);\n
                        } else if (tt != Tokens.RBRACE){\n
                            //if there\'s a right brace, the rule is finished so don\'t do anything\n
                            //otherwise, rethrow the error because it wasn\'t handled properly\n
                            throw ex;\n
                        }\n
\n
                    } else {\n
                        //not a syntax error, rethrow it\n
                        throw ex;\n
                    }\n
                }\n
\n
            },\n
\n
            /**\n
             * In some cases, you can end up with two white space tokens in a\n
             * row. Instead of making a change in every function that looks for\n
             * white space, this function is used to match as much white space\n
             * as necessary.\n
             * @method _readWhitespace\n
             * @return {String} The white space if found, empty string if not.\n
             * @private\n
             */\n
            _readWhitespace: function(){\n
\n
                var tokenStream = this._tokenStream,\n
                    ws = "";\n
\n
                while(tokenStream.match(Tokens.S)){\n
                    ws += tokenStream.token().value;\n
                }\n
\n
                return ws;\n
            },\n
\n
\n
            /**\n
             * Throws an error when an unexpected token is found.\n
             * @param {Object} token The token that was found.\n
             * @method _unexpectedToken\n
             * @return {void}\n
             * @private\n
             */\n
            _unexpectedToken: function(token){\n
                throw new SyntaxError("Unexpected token \'" + token.value + "\' at line " + token.startLine + ", col " + token.startCol + ".", token.startLine, token.startCol);\n
            },\n
\n
            /**\n
             * Helper method used for parsing subparts of a style sheet.\n
             * @return {void}\n
             * @method _verifyEnd\n
             * @private\n
             */\n
            _verifyEnd: function(){\n
                if (this._tokenStream.LA(1) != Tokens.EOF){\n
                    this._unexpectedToken(this._tokenStream.LT(1));\n
                }\n
            },\n
\n
            //-----------------------------------------------------------------\n
            // Validation methods\n
            //-----------------------------------------------------------------\n
            _validateProperty: function(property, value){\n
                Validation.validate(property, value);\n
            },\n
\n
            //-----------------------------------------------------------------\n
            // Parsing methods\n
            //-----------------------------------------------------------------\n
\n
            parse: function(input){\n
                this._tokenStream = new TokenStream(input, Tokens);\n
                this._stylesheet();\n
            },\n
\n
            parseStyleSheet: function(input){\n
                //just passthrough\n
                return this.parse(input);\n
            },\n
\n
            parseMediaQuery: function(input){\n
                this._tokenStream = new TokenStream(input, Tokens);\n
                var result = this._media_query();\n
\n
                //if there\'s anything more, then it\'s an invalid selector\n
                this._verifyEnd();\n
\n
                //otherwise return result\n
                return result;\n
            },\n
\n
            /**\n
             * Parses a property value (everything after the semicolon).\n
             * @return {parserlib.css.PropertyValue} The property value.\n
             * @throws parserlib.util.SyntaxError If an unexpected token is found.\n
             * @method parserPropertyValue\n
             */\n
            parsePropertyValue: function(input){\n
\n
                this._tokenStream = new TokenStream(input, Tokens);\n
                this._readWhitespace();\n
\n
                var result = this._expr();\n
\n
                //okay to have a trailing white space\n
                this._readWhitespace();\n
\n
                //if there\'s anything more, then it\'s an invalid selector\n
                this._verifyEnd();\n
\n
                //otherwise return result\n
                return result;\n
            },\n
\n
            /**\n
             * Parses a complete CSS rule, including selectors and\n
             * properties.\n
             * @param {String} input The text to parser.\n
             * @return {Boolean} True if the parse completed successfully, false if not.\n
             * @method parseRule\n
             */\n
            parseRule: function(input){\n
                this._tokenStream = new TokenStream(input, Tokens);\n
\n
                //skip any leading white space\n
                this._readWhitespace();\n
\n
                var result = this._ruleset();\n
\n
                //skip any trailing white space\n
                this._readWhitespace();\n
\n
                //if there\'s anything more, then it\'s an invalid selector\n
                this._verifyEnd();\n
\n
                //otherwise return result\n
                return result;\n
            },\n
\n
            /**\n
             * Parses a single CSS selector (no comma)\n
             * @param {String} input The text to parse as a CSS selector.\n
             * @return {Selector} An object representing the selector.\n
             * @throws parserlib.util.SyntaxError If an unexpected token is found.\n
             * @method parseSelector\n
             */\n
            parseSelector: function(input){\n
\n
                this._tokenStream = new TokenStream(input, Tokens);\n
\n
                //skip any leading white space\n
                this._readWhitespace();\n
\n
                var result = this._selector();\n
\n
                //skip any trailing white space\n
                this._readWhitespace();\n
\n
                //if there\'s anything more, then it\'s an invalid selector\n
                this._verifyEnd();\n
\n
                //otherwise return result\n
                return result;\n
            },\n
\n
            /**\n
             * Parses an HTML style attribute: a set of CSS declarations\n
             * separated by semicolons.\n
             * @param {String} input The text to parse as a style attribute\n
             * @return {void}\n
             * @method parseStyleAttribute\n
             */\n
            parseStyleAttribute: function(input){\n
                input += "}"; // for error recovery in _readDeclarations()\n
                this._tokenStream = new TokenStream(input, Tokens);\n
                this._readDeclarations();\n
            }\n
        };\n
\n
    //copy over onto prototype\n
    for (prop in additions){\n
        if (additions.hasOwnProperty(prop)){\n
            proto[prop] = additions[prop];\n
        }\n
    }\n
\n
    return proto;\n
}();\n
\n
\n
/*\n
nth\n
  : S* [ [\'-\'|\'+\']? INTEGER? {N} [ S* [\'-\'|\'+\'] S* INTEGER ]? |\n
         [\'-\'|\'+\']? INTEGER | {O}{D}{D} | {E}{V}{E}{N} ] S*\n
  ;\n
*/\n
\n
/*global Validation, ValidationTypes, ValidationError*/\n
var Properties = {\n
\n
    //A\n
    "alignment-adjust"              : "auto | baseline | before-edge | text-before-edge | middle | central | after-edge | text-after-edge | ideographic | alphabetic | hanging | mathematical | <percentage> | <length>",\n
    "alignment-baseline"            : "baseline | use-script | before-edge | text-before-edge | after-edge | text-after-edge | central | middle | ideographic | alphabetic | hanging | mathematical",\n
    "animation"                     : 1,\n
    "animation-delay"               : { multi: "<time>", comma: true },\n
    "animation-direction"           : { multi: "normal | alternate", comma: true },\n
    "animation-duration"            : { multi: "<time>", comma: true },\n
    "animation-iteration-count"     : { multi: "<number> | infinite", comma: true },\n
    "animation-name"                : { multi: "none | <ident>", comma: true },\n
    "animation-play-state"          : { multi: "running | paused", comma: true },\n
    "animation-timing-function"     : 1,\n
\n
    //vendor prefixed\n
    "-moz-animation-delay"               : { multi: "<time>", comma: true },\n
    "-moz-animation-direction"           : { multi: "normal | alternate", comma: true },\n
    "-moz-animation-duration"            : { multi: "<time>", comma: true },\n
    "-moz-animation-iteration-count"     : { multi: "<number> | infinite", comma: true },\n
    "-moz-animation-name"                : { multi: "none | <ident>", comma: true },\n
    "-moz-animation-play-state"          : { multi: "running | paused", comma: true },\n
\n
    "-ms-animation-delay"               : { multi: "<time>", comma: true },\n
    "-ms-animation-direction"           : { multi: "normal | alternate", comma: true },\n
    "-ms-animation-duration"            : { multi: "<time>", comma: true },\n
    "-ms-animation-iteration-count"     : { multi: "<number> | infinite", comma: true },\n
    "-ms-animation-name"                : { multi: "none | <ident>", comma: true },\n
    "-ms-animation-play-state"          : { multi: "running | paused", comma: true },\n
\n
    "-webkit-animation-delay"               : { multi: "<time>", comma: true },\n
    "-webkit-animation-direction"           : { multi: "normal | alternate", comma: true },\n
    "-webkit-animation-duration"            : { multi: "<time>", comma: true },\n
    "-webkit-animation-iteration-count"     : { multi: "<number> | infinite", comma: true },\n
    "-webkit-animation-name"                : { multi: "none | <ident>", comma: true },\n
    "-webkit-animation-play-state"          : { multi: "running | paused", comma: true },\n
\n
    "-o-animation-delay"               : { multi: "<time>", comma: true },\n
    "-o-animation-direction"           : { multi: "normal | alternate", comma: true },\n
    "-o-animation-duration"            : { multi: "<time>", comma: true },\n
    "-o-animation-iteration-count"     : { multi: "<number> | infinite", comma: true },\n
    "-o-animation-name"                : { multi: "none | <ident>", comma: true },\n
    "-o-animation-play-state"          : { multi: "running | paused", comma: true },\n
\n
    "appearance"                    : "icon | window | desktop | workspace | document | tooltip | dialog | button | push-button | hyperlink | radio-button | checkbox | menu-item | tab | menu | menubar | pull-down-menu | pop-up-menu | list-menu | radio-group | checkbox-group | outline-tree | range | field | combo-box | signature | password | normal | none | inherit",\n
    "azimuth"                       : function (expression) {\n
        var simple      = "<angle> | leftwards | rightwards | inherit",\n
            direction   = "left-side | far-left | left | center-left | center | center-right | right | far-right | right-side",\n
            behind      = false,\n
            valid       = false,\n
            part;\n
\n
        if (!ValidationTypes.isAny(expression, simple)) {\n
            if (ValidationTypes.isAny(expression, "behind")) {\n
                behind = true;\n
                valid = true;\n
            }\n
\n
            if (ValidationTypes.isAny(expression, direction)) {\n
                valid = true;\n
                if (!behind) {\n
                    ValidationTypes.isAny(expression, "behind");\n
                }\n
            }\n
        }\n
\n
        if (expression.hasNext()) {\n
            part = expression.next();\n
            if (valid) {\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                throw new ValidationError("Expected (<\'azimuth\'>) but found \'" + part + "\'.", part.line, part.col);\n
            }\n
        }\n
    },\n
\n
    //B\n
    "backface-visibility"           : "visible | hidden",\n
    "background"                    : 1,\n
    "background-attachment"         : { multi: "<attachment>", comma: true },\n
    "background-clip"               : { multi: "<box>", comma: true },\n
    "background-color"              : "<color> | inherit",\n
    "background-image"              : { multi: "<bg-image>", comma: true },\n
    "background-origin"             : { multi: "<box>", comma: true },\n
    "background-position"           : { multi: "<bg-position>", comma: true },\n
    "background-repeat"             : { multi: "<repeat-style>" },\n
    "background-size"               : { multi: "<bg-size>", comma: true },\n
    "baseline-shift"                : "baseline | sub | super | <percentage> | <length>",\n
    "behavior"                      : 1,\n
    "binding"                       : 1,\n
    "bleed"                         : "<length>",\n
    "bookmark-label"                : "<content> | <attr> | <string>",\n
    "bookmark-level"                : "none | <integer>",\n
    "bookmark-state"                : "open | closed",\n
    "bookmark-target"               : "none | <uri> | <attr>",\n
    "border"                        : "<border-width> || <border-style> || <color>",\n
    "border-bottom"                 : "<border-width> || <border-style> || <color>",\n
    "border-bottom-color"           : "<color> | inherit",\n
    "border-bottom-left-radius"     :  "<x-one-radius>",\n
    "border-bottom-right-radius"    :  "<x-one-radius>",\n
    "border-bottom-style"           : "<border-style>",\n
    "border-bottom-width"           : "<border-width>",\n
    "border-collapse"               : "collapse | separate | inherit",\n
    "border-color"                  : { multi: "<color> | inherit", max: 4 },\n
    "border-image"                  : 1,\n
    "border-image-outset"           : { multi: "<length> | <number>", max: 4 },\n
    "border-image-repeat"           : { multi: "stretch | repeat | round", max: 2 },\n
    "border-image-slice"            : function(expression) {\n
\n
        var valid   = false,\n
            numeric = "<number> | <percentage>",\n
            fill    = false,\n
            count   = 0,\n
            max     = 4,\n
            part;\n
\n
        if (ValidationTypes.isAny(expression, "fill")) {\n
            fill = true;\n
            valid = true;\n
        }\n
\n
        while (expression.hasNext() && count < max) {\n
            valid = ValidationTypes.isAny(expression, numeric);\n
            if (!valid) {\n
                break;\n
            }\n
            count++;\n
        }\n
\n
\n
        if (!fill) {\n
            ValidationTypes.isAny(expression, "fill");\n
        } else {\n
            valid = true;\n
        }\n
\n
        if (expression.hasNext()) {\n
            part = expression.next();\n
            if (valid) {\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                throw new ValidationError("Expected ([<number> | <percentage>]{1,4} && fill?) but found \'" + part + "\'.", part.line, part.col);\n
            }\n
        }\n
    },\n
    "border-image-source"           : "<image> | none",\n
    "border-image-width"            : { multi: "<length> | <percentage> | <number> | auto", max: 4 },\n
    "border-left"                   : "<border-width> || <border-style> || <color>",\n
    "border-left-color"             : "<color> | inherit",\n
    "border-left-style"             : "<border-style>",\n
    "border-left-width"             : "<border-width>",\n
    "border-radius"                 : function(expression) {\n
\n
        var valid   = false,\n
            simple = "<length> | <percentage> | inherit",\n
            slash   = false,\n
            fill    = false,\n
            count   = 0,\n
            max     = 8,\n
            part;\n
\n
        while (expression.hasNext() && count < max) {\n
            valid = ValidationTypes.isAny(expression, simple);\n
            if (!valid) {\n
\n
                if (expression.peek() == "/" && count > 0 && !slash) {\n
                    slash = true;\n
                    max = count + 5;\n
                    expression.next();\n
                } else {\n
                    break;\n
                }\n
            }\n
            count++;\n
        }\n
\n
        if (expression.hasNext()) {\n
            part = expression.next();\n
            if (valid) {\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                throw new ValidationError("Expected (<\'border-radius\'>) but found \'" + part + "\'.", part.line, part.col);\n
            }\n
        }\n
    },\n
    "border-right"                  : "<border-width> || <border-style> || <color>",\n
    "border-right-color"            : "<color> | inherit",\n
    "border-right-style"            : "<border-style>",\n
    "border-right-width"            : "<border-width>",\n
    "border-spacing"                : { multi: "<length> | inherit", max: 2 },\n
    "border-style"                  : { multi: "<border-style>", max: 4 },\n
    "border-top"                    : "<border-width> || <border-style> || <color>",\n
    "border-top-color"              : "<color> | inherit",\n
    "border-top-left-radius"        : "<x-one-radius>",\n
    "border-top-right-radius"       : "<x-one-radius>",\n
    "border-top-style"              : "<border-style>",\n
    "border-top-width"              : "<border-width>",\n
    "border-width"                  : { multi: "<border-width>", max: 4 },\n
    "bottom"                        : "<margin-width> | inherit",\n
    "box-align"                     : "start | end | center | baseline | stretch",        //http://www.w3.org/TR/2009/WD-css3-flexbox-20090723/\n
    "box-decoration-break"          : "slice |clone",\n
    "box-direction"                 : "normal | reverse | inherit",\n
    "box-flex"                      : "<number>",\n
    "box-flex-group"                : "<integer>",\n
    "box-lines"                     : "single | multiple",\n
    "box-ordinal-group"             : "<integer>",\n
    "box-orient"                    : "horizontal | vertical | inline-axis | block-axis | inherit",\n
    "box-pack"                      : "start | end | center | justify",\n
    "box-shadow"                    : function (expression) {\n
        var result      = false,\n
            part;\n
\n
        if (!ValidationTypes.isAny(expression, "none")) {\n
            Validation.multiProperty("<shadow>", expression, true, Infinity);\n
        } else {\n
            if (expression.hasNext()) {\n
                part = expression.next();\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            }\n
        }\n
    },\n
    "box-sizing"                    : "content-box | border-box | inherit",\n
    "break-after"                   : "auto | always | avoid | left | right | page | column | avoid-page | avoid-column",\n
    "break-before"                  : "auto | always | avoid | left | right | page | column | avoid-page | avoid-column",\n
    "break-inside"                  : "auto | avoid | avoid-page | avoid-column",\n
\n
    //C\n
    "caption-side"                  : "top | bottom | inherit",\n
    "clear"                         : "none | right | left | both | inherit",\n
    "clip"                          : 1,\n
    "color"                         : "<color> | inherit",\n
    "color-profile"                 : 1,\n
    "column-count"                  : "<integer> | auto",                      //http://www.w3.org/TR/css3-multicol/\n
    "column-fill"                   : "auto | balance",\n
    "column-gap"                    : "<length> | normal",\n
    "column-rule"                   : "<border-width> || <border-style> || <color>",\n
    "column-rule-color"             : "<color>",\n
    "column-rule-style"             : "<border-style>",\n
    "column-rule-width"             : "<border-width>",\n
    "column-span"                   : "none | all",\n
    "column-width"                  : "<length> | auto",\n
    "columns"                       : 1,\n
    "content"                       : 1,\n
    "counter-increment"             : 1,\n
    "counter-reset"                 : 1,\n
    "crop"                          : "<shape> | auto",\n
    "cue"                           : "cue-after | cue-before | inherit",\n
    "cue-after"                     : 1,\n
    "cue-before"                    : 1,\n
    "cursor"                        : 1,\n
\n
    //D\n
    "direction"                     : "ltr | rtl | inherit",\n
    "display"                       : "inline | block | list-item | inline-block | table | inline-table | table-row-group | table-header-group | table-footer-group | table-row | table-column-group | table-column | table-cell | table-caption | box | inline-box | grid | inline-grid | none | inherit | -moz-box | -moz-inline-block | -moz-inline-box | -moz-inline-grid | -moz-inline-stack | -moz-inline-table | -moz-grid | -moz-grid-group | -moz-grid-line | -moz-groupbox | -moz-deck | -moz-popup | -moz-stack | -moz-marker | -webkit-box | -webkit-inline-box",\n
    "dominant-baseline"             : 1,\n
    "drop-initial-after-adjust"     : "central | middle | after-edge | text-after-edge | ideographic | alphabetic | mathematical | <percentage> | <length>",\n
    "drop-initial-after-align"      : "baseline | use-script | before-edge | text-before-edge | after-edge | text-after-edge | central | middle | ideographic | alphabetic | hanging | mathematical",\n
    "drop-initial-before-adjust"    : "before-edge | text-before-edge | central | middle | hanging | mathematical | <percentage> | <length>",\n
    "drop-initial-before-align"     : "caps-height | baseline | use-script | before-edge | text-before-edge | after-edge | text-after-edge | central | middle | ideographic | alphabetic | hanging | mathematical",\n
    "drop-initial-size"             : "auto | line | <length> | <percentage>",\n
    "drop-initial-value"            : "initial | <integer>",\n
\n
    //E\n
    "elevation"                     : "<angle> | below | level | above | higher | lower | inherit",\n
    "empty-cells"                   : "show | hide | inherit",\n
\n
    //F\n
    "filter"                        : 1,\n
    "fit"                           : "fill | hidden | meet | slice",\n
    "fit-position"                  : 1,\n
    "float"                         : "left | right | none | inherit",\n
    "float-offset"                  : 1,\n
    "font"                          : 1,\n
    "font-family"                   : 1,\n
    "font-size"                     : "<absolute-size> | <relative-size> | <length> | <percentage> | inherit",\n
    "font-size-adjust"              : "<number> | none | inherit",\n
    "font-stretch"                  : "normal | ultra-condensed | extra-condensed | condensed | semi-condensed | semi-expanded | expanded | extra-expanded | ultra-expanded | inherit",\n
    "font-style"                    : "normal | italic | oblique | inherit",\n
    "font-variant"                  : "normal | small-caps | inherit",\n
    "font-weight"                   : "normal | bold | bolder | lighter | 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900 | inherit",\n
\n
    //G\n
    "grid-cell-stacking"            : "columns | rows | layer",\n
    "grid-column"                   : 1,\n
    "grid-columns"                  : 1,\n
    "grid-column-align"             : "start | end | center | stretch",\n
    "grid-column-sizing"            : 1,\n
    "grid-column-span"              : "<integer>",\n
    "grid-flow"                     : "none | rows | columns",\n
    "grid-layer"                    : "<integer>",\n
    "grid-row"                      : 1,\n
    "grid-rows"                     : 1,\n
    "grid-row-align"                : "start | end | center | stretch",\n
    "grid-row-span"                 : "<integer>",\n
    "grid-row-sizing"               : 1,\n
\n
    //H\n
    "hanging-punctuation"           : 1,\n
    "height"                        : "<margin-width> | inherit",\n
    "hyphenate-after"               : "<integer> | auto",\n
    "hyphenate-before"              : "<integer> | auto",\n
    "hyphenate-character"           : "<string> | auto",\n
    "hyphenate-lines"               : "no-limit | <integer>",\n
    "hyphenate-resource"            : 1,\n
    "hyphens"                       : "none | manual | auto",\n
\n
    //I\n
    "icon"                          : 1,\n
    "image-orientation"             : "angle | auto",\n
    "image-rendering"               : 1,\n
    "image-resolution"              : 1,\n
    "inline-box-align"              : "initial | last | <integer>",\n
\n
    //L\n
    "left"                          : "<margin-width> | inherit",\n
    "letter-spacing"                : "<length> | normal | inherit",\n
    "line-height"                   : "<number> | <length> | <percentage> | normal | inherit",\n
    "line-break"                    : "auto | loose | normal | strict",\n
    "line-stacking"                 : 1,\n
    "line-stacking-ruby"            : "exclude-ruby | include-ruby",\n
    "line-stacking-shift"           : "consider-shifts | disregard-shifts",\n
    "line-stacking-strategy"        : "inline-line-height | block-line-height | max-height | grid-height",\n
    "list-style"                    : 1,\n
    "list-style-image"              : "<uri> | none | inherit",\n
    "list-style-position"           : "inside | outside | inherit",\n
    "list-style-type"               : "disc | circle | square | decimal | decimal-leading-zero | lower-roman | upper-roman | lower-greek | lower-latin | upper-latin | armenian | georgian | lower-alpha | upper-alpha | none | inherit",\n
\n
    //M\n
    "margin"                        : { multi: "<margin-width> | inherit", max: 4 },\n
    "margin-bottom"                 : "<margin-width> | inherit",\n
    "margin-left"                   : "<margin-width> | inherit",\n
    "margin-right"                  : "<margin-width> | inherit",\n
    "margin-top"                    : "<margin-width> | inherit",\n
    "mark"                          : 1,\n
    "mark-after"                    : 1,\n
    "mark-before"                   : 1,\n
    "marks"                         : 1,\n
    "marquee-direction"             : 1,\n
    "marquee-play-count"            : 1,\n
    "marquee-speed"                 : 1,\n
    "marquee-style"                 : 1,\n
    "max-height"                    : "<length> | <percentage> | none | inherit",\n
    "max-width"                     : "<length> | <percentage> | none | inherit",\n
    "min-height"                    : "<length> | <percentage> | inherit",\n
    "min-width"                     : "<length> | <percentage> | inherit",\n
    "move-to"                       : 1,\n
\n
    //N\n
    "nav-down"                      : 1,\n
    "nav-index"                     : 1,\n
    "nav-left"                      : 1,\n
    "nav-right"                     : 1,\n
    "nav-up"                        : 1,\n
\n
    //O\n
    "opacity"                       : "<number> | inherit",\n
    "orphans"                       : "<integer> | inherit",\n
    "outline"                       : 1,\n
    "outline-color"                 : "<color> | invert | inherit",\n
    "outline-offset"                : 1,\n
    "outline-style"                 : "<border-style> | inherit",\n
    "outline-width"                 : "<border-width> | inherit",\n
    "overflow"                      : "visible | hidden | scroll | auto | inherit",\n
    "overflow-style"                : 1,\n
    "overflow-x"                    : 1,\n
    "overflow-y"                    : 1,\n
\n
    //P\n
    "padding"                       : { multi: "<padding-width> | inherit", max: 4 },\n
    "padding-bottom"                : "<padding-width> | inherit",\n
    "padding-left"                  : "<padding-width> | inherit",\n
    "padding-right"                 : "<padding-width> | inherit",\n
    "padding-top"                   : "<padding-width> | inherit",\n
    "page"                          : 1,\n
    "page-break-after"              : "auto | always | avoid | left | right | inherit",\n
    "page-break-before"             : "auto | always | avoid | left | right | inherit",\n
    "page-break-inside"             : "auto | avoid | inherit",\n
    "page-policy"                   : 1,\n
    "pause"                         : 1,\n
    "pause-after"                   : 1,\n
    "pause-before"                  : 1,\n
    "perspective"                   : 1,\n
    "perspective-origin"            : 1,\n
    "phonemes"                      : 1,\n
    "pitch"                         : 1,\n
    "pitch-range"                   : 1,\n
    "play-during"                   : 1,\n
    "pointer-events"                : "auto | none | visiblePainted | visibleFill | visibleStroke | visible | painted | fill | stroke | all | inherit",\n
    "position"                      : "static | relative | absolute | fixed | inherit",\n
    "presentation-level"            : 1,\n
    "punctuation-trim"              : 1,\n
\n
    //Q\n
    "quotes"                        : 1,\n
\n
    //R\n
    "rendering-intent"              : 1,\n
    "resize"                        : 1,\n
    "rest"                          : 1,\n
    "rest-after"                    : 1,\n
    "rest-before"                   : 1,\n
    "richness"                      : 1,\n
    "right"                         : "<margin-width> | inherit",\n
    "rotation"                      : 1,\n
    "rotation-point"                : 1,\n
    "ruby-align"                    : 1,\n
    "ruby-overhang"                 : 1,\n
    "ruby-position"                 : 1,\n
    "ruby-span"                     : 1,\n
\n
    //S\n
    "size"                          : 1,\n
    "speak"                         : "normal | none | spell-out | inherit",\n
    "speak-header"                  : "once | always | inherit",\n
    "speak-numeral"                 : "digits | continuous | inherit",\n
    "speak-punctuation"             : "code | none | inherit",\n
    "speech-rate"                   : 1,\n
    "src"                           : 1,\n
    "stress"                        : 1,\n
    "string-set"                    : 1,\n
\n
    "table-layout"                  : "auto | fixed | inherit",\n
    "tab-size"                      : "<integer> | <length>",\n
    "target"                        : 1,\n
    "target-name"                   : 1,\n
    "target-new"                    : 1,\n
    "target-position"               : 1,\n
    "text-align"                    : "left | right | center | justify | inherit" ,\n
    "text-align-last"               : 1,\n
    "text-decoration"               : 1,\n
    "text-emphasis"                 : 1,\n
    "text-height"                   : 1,\n
    "text-indent"                   : "<length> | <percentage> | inherit",\n
    "text-justify"                  : "auto | none | inter-word | inter-ideograph | inter-cluster | distribute | kashida",\n
    "text-outline"                  : 1,\n
    "text-overflow"                 : 1,\n
    "text-rendering"                : "auto | optimizeSpeed | optimizeLegibility | geometricPrecision | inherit",\n
    "text-shadow"                   : 1,\n
    "text-transform"                : "capitalize | uppercase | lowercase | none | inherit",\n
    "text-wrap"                     : "normal | none | avoid",\n
    "top"                           : "<margin-width> | inherit",\n
    "transform"                     : 1,\n
    "transform-origin"              : 1,\n
    "transform-style"               : 1,\n
    "transition"                    : 1,\n
    "transition-delay"              : 1,\n
    "transition-duration"           : 1,\n
    "transition-property"           : 1,\n
    "transition-timing-function"    : 1,\n
\n
    //U\n
    "unicode-bidi"                  : "normal | embed | bidi-override | inherit",\n
    "user-modify"                   : "read-only | read-write | write-only | inherit",\n
    "user-select"                   : "none | text | toggle | element | elements | all | inherit",\n
\n
    //V\n
    "vertical-align"                : "auto | use-script | baseline | sub | super | top | text-top | central | middle | bottom | text-bottom | <percentage> | <length>",\n
    "visibility"                    : "visible | hidden | collapse | inherit",\n
    "voice-balance"                 : 1,\n
    "voice-duration"                : 1,\n
    "voice-family"                  : 1,\n
    "voice-pitch"                   : 1,\n
    "voice-pitch-range"             : 1,\n
    "voice-rate"                    : 1,\n
    "voice-stress"                  : 1,\n
    "voice-volume"                  : 1,\n
    "volume"                        : 1,\n
\n
    //W\n
    "white-space"                   : "normal | pre | nowrap | pre-wrap | pre-line | inherit | -pre-wrap | -o-pre-wrap | -moz-pre-wrap | -hp-pre-wrap", //http://perishablepress.com/wrapping-content/\n
    "white-space-collapse"          : 1,\n
    "widows"                        : "<integer> | inherit",\n
    "width"                         : "<length> | <percentage> | auto | inherit" ,\n
    "word-break"                    : "normal | keep-all | break-all",\n
    "word-spacing"                  : "<length> | normal | inherit",\n
    "word-wrap"                     : 1,\n
\n
    //Z\n
    "z-index"                       : "<integer> | auto | inherit",\n
    "zoom"                          : "<number> | <percentage> | normal"\n
};\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a selector combinator (whitespace, +, >).\n
 * @namespace parserlib.css\n
 * @class PropertyName\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {String} text The text representation of the unit.\n
 * @param {String} hack The type of IE hack applied ("*", "_", or null).\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function PropertyName(text, hack, line, col){\n
\n
    SyntaxUnit.call(this, text, line, col, Parser.PROPERTY_NAME_TYPE);\n
\n
    /**\n
     * The type of IE hack applied ("*", "_", or null).\n
     * @type String\n
     * @property hack\n
     */\n
    this.hack = hack;\n
\n
}\n
\n
PropertyName.prototype = new SyntaxUnit();\n
PropertyName.prototype.constructor = PropertyName;\n
PropertyName.prototype.toString = function(){\n
    return (this.hack ? this.hack : "") + this.text;\n
};\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a single part of a CSS property value, meaning that it represents\n
 * just everything single part between ":" and ";". If there are multiple values\n
 * separated by commas, this type represents just one of the values.\n
 * @param {String[]} parts An array of value parts making up this value.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 * @namespace parserlib.css\n
 * @class PropertyValue\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 */\n
function PropertyValue(parts, line, col){\n
\n
    SyntaxUnit.call(this, parts.join(" "), line, col, Parser.PROPERTY_VALUE_TYPE);\n
\n
    /**\n
     * The parts that make up the selector.\n
     * @type Array\n
     * @property parts\n
     */\n
    this.parts = parts;\n
\n
}\n
\n
PropertyValue.prototype = new SyntaxUnit();\n
PropertyValue.prototype.constructor = PropertyValue;\n
\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * A utility class that allows for easy iteration over the various parts of a\n
 * property value.\n
 * @param {parserlib.css.PropertyValue} value The property value to iterate over.\n
 * @namespace parserlib.css\n
 * @class PropertyValueIterator\n
 * @constructor\n
 */\n
function PropertyValueIterator(value){\n
\n
    /**\n
     * Iterator value\n
     * @type int\n
     * @property _i\n
     * @private\n
     */\n
    this._i = 0;\n
\n
    /**\n
     * The parts that make up the value.\n
     * @type Array\n
     * @property _parts\n
     * @private\n
     */\n
    this._parts = value.parts;\n
\n
    /**\n
     * Keeps track of bookmarks along the way.\n
     * @type Array\n
     * @property _marks\n
     * @private\n
     */\n
    this._marks = [];\n
\n
    /**\n
     * Holds the original property value.\n
     * @type parserlib.css.PropertyValue\n
     * @property value\n
     */\n
    this.value = value;\n
\n
}\n
\n
/**\n
 * Returns the total number of parts in the value.\n
 * @return {int} The total number of parts in the value.\n
 * @method count\n
 */\n
PropertyValueIterator.prototype.count = function(){\n
    return this._parts.length;\n
};\n
\n
/**\n
 * Indicates if the iterator is positioned at the first item.\n
 * @return {Boolean} True if positioned at first item, false if not.\n
 * @method isFirst\n
 */\n
PropertyValueIterator.prototype.isFirst = function(){\n
    return this._i === 0;\n
};\n
\n
/**\n
 * Indicates if there are more parts of the property value.\n
 * @return {Boolean} True if there are more parts, false if not.\n
 * @method hasNext\n
 */\n
PropertyValueIterator.prototype.hasNext = function(){\n
    return (this._i < this._parts.length);\n
};\n
\n
/**\n
 * Marks the current spot in the iteration so it can be restored to\n
 * later on.\n
 * @return {void}\n
 * @method mark\n
 */\n
PropertyValueIterator.prototype.mark = function(){\n
    this._marks.push(this._i);\n
};\n
\n
/**\n
 * Returns the next part of the property value or null if there is no next\n
 * part. Does not move the internal counter forward.\n
 * @return {parserlib.css.PropertyValuePart} The next part of the property value or null if there is no next\n
 * part.\n
 * @method peek\n
 */\n
PropertyValueIterator.prototype.peek = function(count){\n
    return this.hasNext() ? this._parts[this._i + (count || 0)] : null;\n
};\n
\n
/**\n
 * Returns the next part of the property value or null if there is no next\n
 * part.\n
 * @return {parserlib.css.PropertyValuePart} The next part of the property value or null if there is no next\n
 * part.\n
 * @method next\n
 */\n
PropertyValueIterator.prototype.next = function(){\n
    return this.hasNext() ? this._parts[this._i++] : null;\n
};\n
\n
/**\n
 * Returns the previous part of the property value or null if there is no\n
 * previous part.\n
 * @return {parserlib.css.PropertyValuePart} The previous part of the\n
 * property value or null if there is no next part.\n
 * @method previous\n
 */\n
PropertyValueIterator.prototype.previous = function(){\n
    return this._i > 0 ? this._parts[--this._i] : null;\n
};\n
\n
/**\n
 * Restores the last saved bookmark.\n
 * @return {void}\n
 * @method restore\n
 */\n
PropertyValueIterator.prototype.restore = function(){\n
    if (this._marks.length){\n
        this._i = this._marks.pop();\n
    }\n
};\n
\n
\n
/*global SyntaxUnit, Parser, Colors*/\n
/**\n
 * Represents a single part of a CSS property value, meaning that it represents\n
 * just one part of the data between ":" and ";".\n
 * @param {String} text The text representation of the unit.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 * @namespace parserlib.css\n
 * @class PropertyValuePart\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 */\n
function PropertyValuePart(text, line, col){\n
\n
    SyntaxUnit.call(this, text, line, col, Parser.PROPERTY_VALUE_PART_TYPE);\n
\n
    /**\n
     * Indicates the type of value unit.\n
     * @type String\n
     * @property type\n
     */\n
    this.type = "unknown";\n
\n
    //figure out what type of data it is\n
\n
    var temp;\n
\n
    //it is a measurement?\n
    if (/^([+\\-]?[\\d\\.]+)([a-z]+)$/i.test(text)){  //dimension\n
        this.type = "dimension";\n
        this.value = +RegExp.$1;\n
        this.units = RegExp.$2;\n
\n
        //try to narrow down\n
        switch(this.units.toLowerCase()){\n
\n
            case "em":\n
            case "rem":\n
            case "ex":\n
            case "px":\n
            case "cm":\n
            case "mm":\n
            case "in":\n
            case "pt":\n
            case "pc":\n
            case "ch":\n
            case "vh":\n
            case "vw":\n
            case "vm":\n
                this.type = "length";\n
                break;\n
\n
            case "deg":\n
            case "rad":\n
            case "grad":\n
                this.type = "angle";\n
                break;\n
\n
            case "ms":\n
            case "s":\n
                this.type = "time";\n
                break;\n
\n
            case "hz":\n
            case "khz":\n
                this.type = "frequency";\n
                break;\n
\n
            case "dpi":\n
            case "dpcm":\n
                this.type = "resolution";\n
                break;\n
\n
            //default\n
\n
        }\n
\n
    } else if (/^([+\\-]?[\\d\\.]+)%$/i.test(text)){  //percentage\n
        this.type = "percentage";\n
        this.value = +RegExp.$1;\n
    } else if (/^([+\\-]?[\\d\\.]+)%$/i.test(text)){  //percentage\n
        this.type = "percentage";\n
        this.value = +RegExp.$1;\n
    } else if (/^([+\\-]?\\d+)$/i.test(text)){  //integer\n
        this.type = "integer";\n
        this.value = +RegExp.$1;\n
    } else if (/^([+\\-]?[\\d\\.]+)$/i.test(text)){  //number\n
        this.type = "number";\n
        this.value = +RegExp.$1;\n
\n
    } else if (/^#([a-f0-9]{3,6})/i.test(text)){  //hexcolor\n
        this.type = "color";\n
        temp = RegExp.$1;\n
        if (temp.length == 3){\n
            this.red    = parseInt(temp.charAt(0)+temp.charAt(0),16);\n
            this.green  = parseInt(temp.charAt(1)+temp.charAt(1),16);\n
            this.blue   = parseInt(temp.charAt(2)+temp.charAt(2),16);\n
        } else {\n
            this.red    = parseInt(temp.substring(0,2),16);\n
            this.green  = parseInt(temp.substring(2,4),16);\n
            this.blue   = parseInt(temp.substring(4,6),16);\n
        }\n
    } else if (/^rgb\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*\\)/i.test(text)){ //rgb() color with absolute numbers\n
        this.type   = "color";\n
        this.red    = +RegExp.$1;\n
        this.green  = +RegExp.$2;\n
        this.blue   = +RegExp.$3;\n
    } else if (/^rgb\\(\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*\\)/i.test(text)){ //rgb() color with percentages\n
        this.type   = "color";\n
        this.red    = +RegExp.$1 * 255 / 100;\n
        this.green  = +RegExp.$2 * 255 / 100;\n
        this.blue   = +RegExp.$3 * 255 / 100;\n
    } else if (/^rgba\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*([\\d\\.]+)\\s*\\)/i.test(text)){ //rgba() color with absolute numbers\n
        this.type   = "color";\n
        this.red    = +RegExp.$1;\n
        this.green  = +RegExp.$2;\n
        this.blue   = +RegExp.$3;\n
        this.alpha  = +RegExp.$4;\n
    } else if (/^rgba\\(\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*,\\s*([\\d\\.]+)\\s*\\)/i.test(text)){ //rgba() color with percentages\n
        this.type   = "color";\n
        this.red    = +RegExp.$1 * 255 / 100;\n
        this.green  = +RegExp.$2 * 255 / 100;\n
        this.blue   = +RegExp.$3 * 255 / 100;\n
        this.alpha  = +RegExp.$4;\n
    } else if (/^hsl\\(\\s*(\\d+)\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*\\)/i.test(text)){ //hsl()\n
        this.type   = "color";\n
        this.hue    = +RegExp.$1;\n
        this.saturation = +RegExp.$2 / 100;\n
        this.lightness  = +RegExp.$3 / 100;\n
    } else if (/^hsla\\(\\s*(\\d+)\\s*,\\s*(\\d+)%\\s*,\\s*(\\d+)%\\s*,\\s*([\\d\\.]+)\\s*\\)/i.test(text)){ //hsla() color with percentages\n
        this.type   = "color";\n
        this.hue    = +RegExp.$1;\n
        this.saturation = +RegExp.$2 / 100;\n
        this.lightness  = +RegExp.$3 / 100;\n
        this.alpha  = +RegExp.$4;\n
    } else if (/^url\\(["\']?([^\\)"\']+)["\']?\\)/i.test(text)){ //URI\n
        this.type   = "uri";\n
        this.uri    = RegExp.$1;\n
    } else if (/^([^\\(]+)\\(/i.test(text)){\n
        this.type   = "function";\n
        this.name   = RegExp.$1;\n
        this.value  = text;\n
    } else if (/^["\'][^"\']*["\']/.test(text)){    //string\n
        this.type   = "string";\n
        this.value  = eval(text);\n
    } else if (Colors[text.toLowerCase()]){  //named color\n
        this.type   = "color";\n
        temp        = Colors[text.toLowerCase()].substring(1);\n
        this.red    = parseInt(temp.substring(0,2),16);\n
        this.green  = parseInt(temp.substring(2,4),16);\n
        this.blue   = parseInt(temp.substring(4,6),16);\n
    } else if (/^[\\,\\/]$/.test(text)){\n
        this.type   = "operator";\n
        this.value  = text;\n
    } else if (/^[a-z\\-\\u0080-\\uFFFF][a-z0-9\\-\\u0080-\\uFFFF]*$/i.test(text)){\n
        this.type   = "identifier";\n
        this.value  = text;\n
    }\n
\n
}\n
\n
PropertyValuePart.prototype = new SyntaxUnit();\n
PropertyValuePart.prototype.constructor = PropertyValuePart;\n
\n
/**\n
 * Create a new syntax unit based solely on the given token.\n
 * Convenience method for creating a new syntax unit when\n
 * it represents a single token instead of multiple.\n
 * @param {Object} token The token object to represent.\n
 * @return {parserlib.css.PropertyValuePart} The object representing the token.\n
 * @static\n
 * @method fromToken\n
 */\n
PropertyValuePart.fromToken = function(token){\n
    return new PropertyValuePart(token.value, token.startLine, token.startCol);\n
};\n
var Pseudos = {\n
    ":first-letter": 1,\n
    ":first-line":   1,\n
    ":before":       1,\n
    ":after":        1\n
};\n
\n
Pseudos.ELEMENT = 1;\n
Pseudos.CLASS = 2;\n
\n
Pseudos.isElement = function(pseudo){\n
    return pseudo.indexOf("::") === 0 || Pseudos[pseudo.toLowerCase()] == Pseudos.ELEMENT;\n
};\n
/*global SyntaxUnit, Parser, Specificity*/\n
/**\n
 * Represents an entire single selector, including all parts but not\n
 * including multiple selectors (those separated by commas).\n
 * @namespace parserlib.css\n
 * @class Selector\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {Array} parts Array of selectors parts making up this selector.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function Selector(parts, line, col){\n
\n
    SyntaxUnit.call(this, parts.join(" "), line, col, Parser.SELECTOR_TYPE);\n
\n
    /**\n
     * The parts that make up the selector.\n
     * @type Array\n
     * @property parts\n
     */\n
    this.parts = parts;\n
\n
    /**\n
     * The specificity of the selector.\n
     * @type parserlib.css.Specificity\n
     * @property specificity\n
     */\n
    this.specificity = Specificity.calculate(this);\n
\n
}\n
\n
Selector.prototype = new SyntaxUnit();\n
Selector.prototype.constructor = Selector;\n
\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a single part of a selector string, meaning a single set of\n
 * element name and modifiers. This does not include combinators such as\n
 * spaces, +, >, etc.\n
 * @namespace parserlib.css\n
 * @class SelectorPart\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {String} elementName The element name in the selector or null\n
 *      if there is no element name.\n
 * @param {Array} modifiers Array of individual modifiers for the element.\n
 *      May be empty if there are none.\n
 * @param {String} text The text representation of the unit.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function SelectorPart(elementName, modifiers, text, line, col){\n
\n
    SyntaxUnit.call(this, text, line, col, Parser.SELECTOR_PART_TYPE);\n
\n
    /**\n
     * The tag name of the element to which this part\n
     * of the selector affects.\n
     * @type String\n
     * @property elementName\n
     */\n
    this.elementName = elementName;\n
\n
    /**\n
     * The parts that come after the element name, such as class names, IDs,\n
     * pseudo classes/elements, etc.\n
     * @type Array\n
     * @property modifiers\n
     */\n
    this.modifiers = modifiers;\n
\n
}\n
\n
SelectorPart.prototype = new SyntaxUnit();\n
SelectorPart.prototype.constructor = SelectorPart;\n
\n
\n
/*global SyntaxUnit, Parser*/\n
/**\n
 * Represents a selector modifier string, meaning a class name, element name,\n
 * element ID, pseudo rule, etc.\n
 * @namespace parserlib.css\n
 * @class SelectorSubPart\n
 * @extends parserlib.util.SyntaxUnit\n
 * @constructor\n
 * @param {String} text The text representation of the unit.\n
 * @param {String} type The type of selector modifier.\n
 * @param {int} line The line of text on which the unit resides.\n
 * @param {int} col The column of text on which the unit resides.\n
 */\n
function SelectorSubPart(text, type, line, col){\n
\n
    SyntaxUnit.call(this, text, line, col, Parser.SELECTOR_SUB_PART_TYPE);\n
\n
    /**\n
     * The type of modifier.\n
     * @type String\n
     * @property type\n
     */\n
    this.type = type;\n
\n
    /**\n
     * Some subparts have arguments, this represents them.\n
     * @type Array\n
     * @property args\n
     */\n
    this.args = [];\n
\n
}\n
\n
SelectorSubPart.prototype = new SyntaxUnit();\n
SelectorSubPart.prototype.constructor = SelectorSubPart;\n
\n
\n
/*global Pseudos, SelectorPart*/\n
/**\n
 * Represents a selector\'s specificity.\n
 * @namespace parserlib.css\n
 * @class Specificity\n
 * @constructor\n
 * @param {int} a Should be 1 for inline styles, zero for stylesheet styles\n
 * @param {int} b Number of ID selectors\n
 * @param {int} c Number of classes and pseudo classes\n
 * @param {int} d Number of element names and pseudo elements\n
 */\n
function Specificity(a, b, c, d){\n
    this.a = a;\n
    this.b = b;\n
    this.c = c;\n
    this.d = d;\n
}\n
\n
Specificity.prototype = {\n
    constructor: Specificity,\n
\n
    /**\n
     * Compare this specificity to another.\n
     * @param {Specificity} other The other specificity to compare to.\n
     * @return {int} -1 if the other specificity is larger, 1 if smaller, 0 if equal.\n
     * @method compare\n
     */\n
    compare: function(other){\n
        var comps = ["a", "b", "c", "d"],\n
            i, len;\n
\n
        for (i=0, len=comps.length; i < len; i++){\n
            if (this[comps[i]] < other[comps[i]]){\n
                return -1;\n
            } else if (this[comps[i]] > other[comps[i]]){\n
                return 1;\n
            }\n
        }\n
\n
        return 0;\n
    },\n
\n
    /**\n
     * Creates a numeric value for the specificity.\n
     * @return {int} The numeric value for the specificity.\n
     * @method valueOf\n
     */\n
    valueOf: function(){\n
        return (this.a * 1000) + (this.b * 100) + (this.c * 10) + this.d;\n
    },\n
\n
    /**\n
     * Returns a string representation for specificity.\n
     * @return {String} The string representation of specificity.\n
     * @method toString\n
     */\n
    toString: function(){\n
        return this.a + "," + this.b + "," + this.c + "," + this.d;\n
    }\n
\n
};\n
\n
/**\n
 * Calculates the specificity of the given selector.\n
 * @param {parserlib.css.Selector} The selector to calculate specificity for.\n
 * @return {parserlib.css.Specificity} The specificity of the selector.\n
 * @static\n
 * @method calculate\n
 */\n
Specificity.calculate = function(selector){\n
\n
    var i, len,\n
        part,\n
        b=0, c=0, d=0;\n
\n
    function updateValues(part){\n
\n
        var i, j, len, num,\n
            elementName = part.elementName ? part.elementName.text : "",\n
            modifier;\n
\n
        if (elementName && elementName.charAt(elementName.length-1) != "*") {\n
            d++;\n
        }\n
\n
        for (i=0, len=part.modifiers.length; i < len; i++){\n
            modifier = part.modifiers[i];\n
            switch(modifier.type){\n
                case "class":\n
                case "attribute":\n
                    c++;\n
                    break;\n
\n
                case "id":\n
                    b++;\n
                    break;\n
\n
                case "pseudo":\n
                    if (Pseudos.isElement(modifier.text)){\n
                        d++;\n
                    } else {\n
                        c++;\n
                    }\n
                    break;\n
\n
                case "not":\n
                    for (j=0, num=modifier.args.length; j < num; j++){\n
                        updateValues(modifier.args[j]);\n
                    }\n
            }\n
         }\n
    }\n
\n
    for (i=0, len=selector.parts.length; i < len; i++){\n
        part = selector.parts[i];\n
\n
        if (part instanceof SelectorPart){\n
            updateValues(part);\n
        }\n
    }\n
\n
    return new Specificity(0, b, c, d);\n
};\n
\n
/*global Tokens, TokenStreamBase*/\n
\n
var h = /^[0-9a-fA-F]$/,\n
    nonascii = /^[\\u0080-\\uFFFF]$/,\n
    nl = /\\n|\\r\\n|\\r|\\f/;\n
\n
//-----------------------------------------------------------------------------\n
// Helper functions\n
//-----------------------------------------------------------------------------\n
\n
\n
function isHexDigit(c){\n
    return c !== null && h.test(c);\n
}\n
\n
function isDigit(c){\n
    return c !== null && /\\d/.test(c);\n
}\n
\n
function isWhitespace(c){\n
    return c !== null && /\\s/.test(c);\n
}\n
\n
function isNewLine(c){\n
    return c !== null && nl.test(c);\n
}\n
\n
function isNameStart(c){\n
    return c !== null && (/[a-z_\\u0080-\\uFFFF\\\\]/i.test(c));\n
}\n
\n
function isNameChar(c){\n
    return c !== null && (isNameStart(c) || /[0-9\\-\\\\]/.test(c));\n
}\n
\n
function isIdentStart(c){\n
    return c !== null && (isNameStart(c) || /\\-\\\\/.test(c));\n
}\n
\n
function mix(receiver, supplier){\n
    for (var prop in supplier){\n
        if (supplier.hasOwnProperty(prop)){\n
            receiver[prop] = supplier[prop];\n
        }\n
    }\n
    return receiver;\n
}\n
\n
//-----------------------------------------------------------------------------\n
// CSS Token Stream\n
//-----------------------------------------------------------------------------\n
\n
\n
/**\n
 * A token stream that produces CSS tokens.\n
 * @param {String|Reader} input The source of text to tokenize.\n
 * @constructor\n
 * @class TokenStream\n
 * @namespace parserlib.css\n
 */\n
function TokenStream(input){\n
    TokenStreamBase.call(this, input, Tokens);\n
}\n
\n
TokenStream.prototype = mix(new TokenStreamBase(), {\n
\n
    /**\n
     * Overrides the TokenStreamBase method of the same name\n
     * to produce CSS tokens.\n
     * @param {variant} channel The name of the channel to use\n
     *      for the next token.\n
     * @return {Object} A token object representing the next token.\n
     * @method _getToken\n
     * @private\n
     */\n
    _getToken: function(channel){\n
\n
        var c,\n
            reader = this._reader,\n
            token   = null,\n
            startLine   = reader.getLine(),\n
            startCol    = reader.getCol();\n
\n
        c = reader.read();\n
\n
\n
        while(c){\n
            switch(c){\n
\n
                /*\n
                 * Potential tokens:\n
                 * - COMMENT\n
                 * - SLASH\n
                 * - CHAR\n
                 */\n
                case "/":\n
\n
                    if(reader.peek() == "*"){\n
                        token = this.commentToken(c, startLine, startCol);\n
                    } else {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - DASHMATCH\n
                 * - INCLUDES\n
                 * - PREFIXMATCH\n
                 * - SUFFIXMATCH\n
                 * - SUBSTRINGMATCH\n
                 * - CHAR\n
                 */\n
                case "|":\n
                case "~":\n
                case "^":\n
                case "$":\n
                case "*":\n
                    if(reader.peek() == "="){\n
                        token = this.comparisonToken(c, startLine, startCol);\n
                    } else {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - STRING\n
                 * - INVALID\n
                 */\n
                case "\\"":\n
                case "\'":\n
                    token = this.stringToken(c, startLine, startCol);\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - HASH\n
                 * - CHAR\n
                 */\n
                case "#":\n
                    if (isNameChar(reader.peek())){\n
                        token = this.hashToken(c, startLine, startCol);\n
                    } else {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - DOT\n
                 * - NUMBER\n
                 * - DIMENSION\n
                 * - PERCENTAGE\n
                 */\n
                case ".":\n
                    if (isDigit(reader.peek())){\n
                        token = this.numberToken(c, startLine, startCol);\n
                    } else {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - CDC\n
                 * - MINUS\n
                 * - NUMBER\n
                 * - DIMENSION\n
                 * - PERCENTAGE\n
                 */\n
                case "-":\n
                    if (reader.peek() == "-"){  //could be closing HTML-style comment\n
                        token = this.htmlCommentEndToken(c, startLine, startCol);\n
                    } else if (isNameStart(reader.peek())){\n
                        token = this.identOrFunctionToken(c, startLine, startCol);\n
                    } else {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - IMPORTANT_SYM\n
                 * - CHAR\n
                 */\n
                case "!":\n
                    token = this.importantToken(c, startLine, startCol);\n
                    break;\n
\n
                /*\n
                 * Any at-keyword or CHAR\n
                 */\n
                case "@":\n
                    token = this.atRuleToken(c, startLine, startCol);\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - NOT\n
                 * - CHAR\n
                 */\n
                case ":":\n
                    token = this.notToken(c, startLine, startCol);\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - CDO\n
                 * - CHAR\n
                 */\n
                case "<":\n
                    token = this.htmlCommentStartToken(c, startLine, startCol);\n
                    break;\n
\n
                /*\n
                 * Potential tokens:\n
                 * - UNICODE_RANGE\n
                 * - URL\n
                 * - CHAR\n
                 */\n
                case "U":\n
                case "u":\n
                    if (reader.peek() == "+"){\n
                        token = this.unicodeRangeToken(c, startLine, startCol);\n
                        break;\n
                    }\n
                    /* falls through */\n
                default:\n
\n
                    /*\n
                     * Potential tokens:\n
                     * - NUMBER\n
                     * - DIMENSION\n
                     * - LENGTH\n
                     * - FREQ\n
                     * - TIME\n
                     * - EMS\n
                     * - EXS\n
                     * - ANGLE\n
                     */\n
                    if (isDigit(c)){\n
                        token = this.numberToken(c, startLine, startCol);\n
                    } else\n
\n
                    /*\n
                     * Potential tokens:\n
                     * - S\n
                     */\n
                    if (isWhitespace(c)){\n
                        token = this.whitespaceToken(c, startLine, startCol);\n
                    } else\n
\n
                    /*\n
                     * Potential tokens:\n
                     * - IDENT\n
                     */\n
                    if (isIdentStart(c)){\n
                        token = this.identOrFunctionToken(c, startLine, startCol);\n
                    } else\n
\n
                    /*\n
                     * Potential tokens:\n
                     * - CHAR\n
                     * - PLUS\n
                     */\n
                    {\n
                        token = this.charToken(c, startLine, startCol);\n
                    }\n
\n
\n
\n
\n
\n
\n
            }\n
\n
            //make sure this token is wanted\n
            //TODO: check channel\n
            break;\n
        }\n
\n
        if (!token && c === null){\n
            token = this.createToken(Tokens.EOF,null,startLine,startCol);\n
        }\n
\n
        return token;\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Methods to create tokens\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Produces a token based on available data and the current\n
     * reader position information. This method is called by other\n
     * private methods to create tokens and is never called directly.\n
     * @param {int} tt The token type.\n
     * @param {String} value The text value of the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @param {Object} options (Optional) Specifies a channel property\n
     *      to indicate that a different channel should be scanned\n
     *      and/or a hide property indicating that the token should\n
     *      be hidden.\n
     * @return {Object} A token object.\n
     * @method createToken\n
     */\n
    createToken: function(tt, value, startLine, startCol, options){\n
        var reader = this._reader;\n
        options = options || {};\n
\n
        return {\n
            value:      value,\n
            type:       tt,\n
            channel:    options.channel,\n
            hide:       options.hide || false,\n
            startLine:  startLine,\n
            startCol:   startCol,\n
            endLine:    reader.getLine(),\n
            endCol:     reader.getCol()\n
        };\n
    },\n
\n
    //-------------------------------------------------------------------------\n
    // Methods to create specific tokens\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Produces a token for any at-rule. If the at-rule is unknown, then\n
     * the token is for a single "@" character.\n
     * @param {String} first The first character for the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method atRuleToken\n
     */\n
    atRuleToken: function(first, startLine, startCol){\n
        var rule    = first,\n
            reader  = this._reader,\n
            tt      = Tokens.CHAR,\n
            valid   = false,\n
            ident,\n
            c;\n
\n
        /*\n
         * First, mark where we are. There are only four @ rules,\n
         * so anything else is really just an invalid token.\n
         * Basically, if this doesn\'t match one of the known @\n
         * rules, just return \'@\' as an unknown token and allow\n
         * parsing to continue after that point.\n
         */\n
        reader.mark();\n
\n
        //try to find the at-keyword\n
        ident = this.readName();\n
        rule = first + ident;\n
        tt = Tokens.type(rule.toLowerCase());\n
\n
        //if it\'s not valid, use the first character only and reset the reader\n
        if (tt == Tokens.CHAR || tt == Tokens.UNKNOWN){\n
            if (rule.length > 1){\n
                tt = Tokens.UNKNOWN_SYM;\n
            } else {\n
                tt = Tokens.CHAR;\n
                rule = first;\n
                reader.reset();\n
            }\n
        }\n
\n
        return this.createToken(tt, rule, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a character token based on the given character\n
     * and location in the stream. If there\'s a special (non-standard)\n
     * token name, this is used; otherwise CHAR is used.\n
     * @param {String} c The character for the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method charToken\n
     */\n
    charToken: function(c, startLine, startCol){\n
        var tt = Tokens.type(c);\n
\n
        if (tt == -1){\n
            tt = Tokens.CHAR;\n
        }\n
\n
        return this.createToken(tt, c, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a character token based on the given character\n
     * and location in the stream. If there\'s a special (non-standard)\n
     * token name, this is used; otherwise CHAR is used.\n
     * @param {String} first The first character for the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method commentToken\n
     */\n
    commentToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            comment = this.readComment(first);\n
\n
        return this.createToken(Tokens.COMMENT, comment, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a comparison token based on the given character\n
     * and location in the stream. The next character must be\n
     * read and is already known to be an equals sign.\n
     * @param {String} c The character for the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method comparisonToken\n
     */\n
    comparisonToken: function(c, startLine, startCol){\n
        var reader  = this._reader,\n
            comparison  = c + reader.read(),\n
            tt      = Tokens.type(comparison) || Tokens.CHAR;\n
\n
        return this.createToken(tt, comparison, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a hash token based on the specified information. The\n
     * first character provided is the pound sign (#) and then this\n
     * method reads a name afterward.\n
     * @param {String} first The first character (#) in the hash nam

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

e.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method hashToken\n
     */\n
    hashToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            name    = this.readName(first);\n
\n
        return this.createToken(Tokens.HASH, name, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a CDO or CHAR token based on the specified information. The\n
     * first character is provided and the rest is read by the function to determine\n
     * the correct token to create.\n
     * @param {String} first The first character in the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method htmlCommentStartToken\n
     */\n
    htmlCommentStartToken: function(first, startLine, startCol){\n
        var reader      = this._reader,\n
            text        = first;\n
\n
        reader.mark();\n
        text += reader.readCount(3);\n
\n
        if (text == "<!--"){\n
            return this.createToken(Tokens.CDO, text, startLine, startCol);\n
        } else {\n
            reader.reset();\n
            return this.charToken(first, startLine, startCol);\n
        }\n
    },\n
\n
    /**\n
     * Produces a CDC or CHAR token based on the specified information. The\n
     * first character is provided and the rest is read by the function to determine\n
     * the correct token to create.\n
     * @param {String} first The first character in the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method htmlCommentEndToken\n
     */\n
    htmlCommentEndToken: function(first, startLine, startCol){\n
        var reader      = this._reader,\n
            text        = first;\n
\n
        reader.mark();\n
        text += reader.readCount(2);\n
\n
        if (text == "-->"){\n
            return this.createToken(Tokens.CDC, text, startLine, startCol);\n
        } else {\n
            reader.reset();\n
            return this.charToken(first, startLine, startCol);\n
        }\n
    },\n
\n
    /**\n
     * Produces an IDENT or FUNCTION token based on the specified information. The\n
     * first character is provided and the rest is read by the function to determine\n
     * the correct token to create.\n
     * @param {String} first The first character in the identifier.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method identOrFunctionToken\n
     */\n
    identOrFunctionToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            ident   = this.readName(first),\n
            tt      = Tokens.IDENT;\n
\n
        //if there\'s a left paren immediately after, it\'s a URI or function\n
        if (reader.peek() == "("){\n
            ident += reader.read();\n
            if (ident.toLowerCase() == "url("){\n
                tt = Tokens.URI;\n
                ident = this.readURI(ident);\n
\n
                //didn\'t find a valid URL or there\'s no closing paren\n
                if (ident.toLowerCase() == "url("){\n
                    tt = Tokens.FUNCTION;\n
                }\n
            } else {\n
                tt = Tokens.FUNCTION;\n
            }\n
        } else if (reader.peek() == ":"){  //might be an IE function\n
\n
            //IE-specific functions always being with progid:\n
            if (ident.toLowerCase() == "progid"){\n
                ident += reader.readTo("(");\n
                tt = Tokens.IE_FUNCTION;\n
            }\n
        }\n
\n
        return this.createToken(tt, ident, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces an IMPORTANT_SYM or CHAR token based on the specified information. The\n
     * first character is provided and the rest is read by the function to determine\n
     * the correct token to create.\n
     * @param {String} first The first character in the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method importantToken\n
     */\n
    importantToken: function(first, startLine, startCol){\n
        var reader      = this._reader,\n
            important   = first,\n
            tt          = Tokens.CHAR,\n
            temp,\n
            c;\n
\n
        reader.mark();\n
        c = reader.read();\n
\n
        while(c){\n
\n
            //there can be a comment in here\n
            if (c == "/"){\n
\n
                //if the next character isn\'t a star, then this isn\'t a valid !important token\n
                if (reader.peek() != "*"){\n
                    break;\n
                } else {\n
                    temp = this.readComment(c);\n
                    if (temp === ""){    //broken!\n
                        break;\n
                    }\n
                }\n
            } else if (isWhitespace(c)){\n
                important += c + this.readWhitespace();\n
            } else if (/i/i.test(c)){\n
                temp = reader.readCount(8);\n
                if (/mportant/i.test(temp)){\n
                    important += c + temp;\n
                    tt = Tokens.IMPORTANT_SYM;\n
\n
                }\n
                break;  //we\'re done\n
            } else {\n
                break;\n
            }\n
\n
            c = reader.read();\n
        }\n
\n
        if (tt == Tokens.CHAR){\n
            reader.reset();\n
            return this.charToken(first, startLine, startCol);\n
        } else {\n
            return this.createToken(tt, important, startLine, startCol);\n
        }\n
\n
\n
    },\n
\n
    /**\n
     * Produces a NOT or CHAR token based on the specified information. The\n
     * first character is provided and the rest is read by the function to determine\n
     * the correct token to create.\n
     * @param {String} first The first character in the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method notToken\n
     */\n
    notToken: function(first, startLine, startCol){\n
        var reader      = this._reader,\n
            text        = first;\n
\n
        reader.mark();\n
        text += reader.readCount(4);\n
\n
        if (text.toLowerCase() == ":not("){\n
            return this.createToken(Tokens.NOT, text, startLine, startCol);\n
        } else {\n
            reader.reset();\n
            return this.charToken(first, startLine, startCol);\n
        }\n
    },\n
\n
    /**\n
     * Produces a number token based on the given character\n
     * and location in the stream. This may return a token of\n
     * NUMBER, EMS, EXS, LENGTH, ANGLE, TIME, FREQ, DIMENSION,\n
     * or PERCENTAGE.\n
     * @param {String} first The first character for the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method numberToken\n
     */\n
    numberToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            value   = this.readNumber(first),\n
            ident,\n
            tt      = Tokens.NUMBER,\n
            c       = reader.peek();\n
\n
        if (isIdentStart(c)){\n
            ident = this.readName(reader.read());\n
            value += ident;\n
\n
            if (/^em$|^ex$|^px$|^gd$|^rem$|^vw$|^vh$|^vm$|^ch$|^cm$|^mm$|^in$|^pt$|^pc$/i.test(ident)){\n
                tt = Tokens.LENGTH;\n
            } else if (/^deg|^rad$|^grad$/i.test(ident)){\n
                tt = Tokens.ANGLE;\n
            } else if (/^ms$|^s$/i.test(ident)){\n
                tt = Tokens.TIME;\n
            } else if (/^hz$|^khz$/i.test(ident)){\n
                tt = Tokens.FREQ;\n
            } else if (/^dpi$|^dpcm$/i.test(ident)){\n
                tt = Tokens.RESOLUTION;\n
            } else {\n
                tt = Tokens.DIMENSION;\n
            }\n
\n
        } else if (c == "%"){\n
            value += reader.read();\n
            tt = Tokens.PERCENTAGE;\n
        }\n
\n
        return this.createToken(tt, value, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a string token based on the given character\n
     * and location in the stream. Since strings may be indicated\n
     * by single or double quotes, a failure to match starting\n
     * and ending quotes results in an INVALID token being generated.\n
     * The first character in the string is passed in and then\n
     * the rest are read up to and including the final quotation mark.\n
     * @param {String} first The first character in the string.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method stringToken\n
     */\n
    stringToken: function(first, startLine, startCol){\n
        var delim   = first,\n
            string  = first,\n
            reader  = this._reader,\n
            prev    = first,\n
            tt      = Tokens.STRING,\n
            c       = reader.read();\n
\n
        while(c){\n
            string += c;\n
\n
            //if the delimiter is found with an escapement, we\'re done.\n
            if (c == delim && prev != "\\\\"){\n
                break;\n
            }\n
\n
            //if there\'s a newline without an escapement, it\'s an invalid string\n
            if (isNewLine(reader.peek()) && c != "\\\\"){\n
                tt = Tokens.INVALID;\n
                break;\n
            }\n
\n
            //save previous and get next\n
            prev = c;\n
            c = reader.read();\n
        }\n
\n
        //if c is null, that means we\'re out of input and the string was never closed\n
        if (c === null){\n
            tt = Tokens.INVALID;\n
        }\n
\n
        return this.createToken(tt, string, startLine, startCol);\n
    },\n
\n
    unicodeRangeToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            value   = first,\n
            temp,\n
            tt      = Tokens.CHAR;\n
\n
        //then it should be a unicode range\n
        if (reader.peek() == "+"){\n
            reader.mark();\n
            value += reader.read();\n
            value += this.readUnicodeRangePart(true);\n
\n
            //ensure there\'s an actual unicode range here\n
            if (value.length == 2){\n
                reader.reset();\n
            } else {\n
\n
                tt = Tokens.UNICODE_RANGE;\n
\n
                //if there\'s a ? in the first part, there can\'t be a second part\n
                if (value.indexOf("?") == -1){\n
\n
                    if (reader.peek() == "-"){\n
                        reader.mark();\n
                        temp = reader.read();\n
                        temp += this.readUnicodeRangePart(false);\n
\n
                        //if there\'s not another value, back up and just take the first\n
                        if (temp.length == 1){\n
                            reader.reset();\n
                        } else {\n
                            value += temp;\n
                        }\n
                    }\n
\n
                }\n
            }\n
        }\n
\n
        return this.createToken(tt, value, startLine, startCol);\n
    },\n
\n
    /**\n
     * Produces a S token based on the specified information. Since whitespace\n
     * may have multiple characters, this consumes all whitespace characters\n
     * into a single token.\n
     * @param {String} first The first character in the token.\n
     * @param {int} startLine The beginning line for the character.\n
     * @param {int} startCol The beginning column for the character.\n
     * @return {Object} A token object.\n
     * @method whitespaceToken\n
     */\n
    whitespaceToken: function(first, startLine, startCol){\n
        var reader  = this._reader,\n
            value   = first + this.readWhitespace();\n
        return this.createToken(Tokens.S, value, startLine, startCol);\n
    },\n
\n
\n
\n
\n
    //-------------------------------------------------------------------------\n
    // Methods to read values from the string stream\n
    //-------------------------------------------------------------------------\n
\n
    readUnicodeRangePart: function(allowQuestionMark){\n
        var reader  = this._reader,\n
            part = "",\n
            c       = reader.peek();\n
\n
        //first read hex digits\n
        while(isHexDigit(c) && part.length < 6){\n
            reader.read();\n
            part += c;\n
            c = reader.peek();\n
        }\n
\n
        //then read question marks if allowed\n
        if (allowQuestionMark){\n
            while(c == "?" && part.length < 6){\n
                reader.read();\n
                part += c;\n
                c = reader.peek();\n
            }\n
        }\n
\n
        //there can\'t be any other characters after this point\n
\n
        return part;\n
    },\n
\n
    readWhitespace: function(){\n
        var reader  = this._reader,\n
            whitespace = "",\n
            c       = reader.peek();\n
\n
        while(isWhitespace(c)){\n
            reader.read();\n
            whitespace += c;\n
            c = reader.peek();\n
        }\n
\n
        return whitespace;\n
    },\n
    readNumber: function(first){\n
        var reader  = this._reader,\n
            number  = first,\n
            hasDot  = (first == "."),\n
            c       = reader.peek();\n
\n
\n
        while(c){\n
            if (isDigit(c)){\n
                number += reader.read();\n
            } else if (c == "."){\n
                if (hasDot){\n
                    break;\n
                } else {\n
                    hasDot = true;\n
                    number += reader.read();\n
                }\n
            } else {\n
                break;\n
            }\n
\n
            c = reader.peek();\n
        }\n
\n
        return number;\n
    },\n
    readString: function(){\n
        var reader  = this._reader,\n
            delim   = reader.read(),\n
            string  = delim,\n
            prev    = delim,\n
            c       = reader.peek();\n
\n
        while(c){\n
            c = reader.read();\n
            string += c;\n
\n
            //if the delimiter is found with an escapement, we\'re done.\n
            if (c == delim && prev != "\\\\"){\n
                break;\n
            }\n
\n
            //if there\'s a newline without an escapement, it\'s an invalid string\n
            if (isNewLine(reader.peek()) && c != "\\\\"){\n
                string = "";\n
                break;\n
            }\n
\n
            //save previous and get next\n
            prev = c;\n
            c = reader.peek();\n
        }\n
\n
        //if c is null, that means we\'re out of input and the string was never closed\n
        if (c === null){\n
            string = "";\n
        }\n
\n
        return string;\n
    },\n
    readURI: function(first){\n
        var reader  = this._reader,\n
            uri     = first,\n
            inner   = "",\n
            c       = reader.peek();\n
\n
        reader.mark();\n
\n
        //skip whitespace before\n
        while(c && isWhitespace(c)){\n
            reader.read();\n
            c = reader.peek();\n
        }\n
\n
        //it\'s a string\n
        if (c == "\'" || c == "\\""){\n
            inner = this.readString();\n
        } else {\n
            inner = this.readURL();\n
        }\n
\n
        c = reader.peek();\n
\n
        //skip whitespace after\n
        while(c && isWhitespace(c)){\n
            reader.read();\n
            c = reader.peek();\n
        }\n
\n
        //if there was no inner value or the next character isn\'t closing paren, it\'s not a URI\n
        if (inner === "" || c != ")"){\n
            uri = first;\n
            reader.reset();\n
        } else {\n
            uri += inner + reader.read();\n
        }\n
\n
        return uri;\n
    },\n
    readURL: function(){\n
        var reader  = this._reader,\n
            url     = "",\n
            c       = reader.peek();\n
\n
        //TODO: Check for escape and nonascii\n
        while (/^[!#$%&\\\\*-~]$/.test(c)){\n
            url += reader.read();\n
            c = reader.peek();\n
        }\n
\n
        return url;\n
\n
    },\n
    readName: function(first){\n
        var reader  = this._reader,\n
            ident   = first || "",\n
            c       = reader.peek();\n
\n
        while(true){\n
            if (c == "\\\\"){\n
                ident += this.readEscape(reader.read());\n
                c = reader.peek();\n
            } else if(c && isNameChar(c)){\n
                ident += reader.read();\n
                c = reader.peek();\n
            } else {\n
                break;\n
            }\n
        }\n
\n
        return ident;\n
    },\n
\n
    readEscape: function(first){\n
        var reader  = this._reader,\n
            cssEscape = first || "",\n
            i       = 0,\n
            c       = reader.peek();\n
\n
        if (isHexDigit(c)){\n
            do {\n
                cssEscape += reader.read();\n
                c = reader.peek();\n
            } while(c && isHexDigit(c) && ++i < 6);\n
        }\n
\n
        if (cssEscape.length == 3 && /\\s/.test(c) ||\n
            cssEscape.length == 7 || cssEscape.length == 1){\n
                reader.read();\n
        } else {\n
            c = "";\n
        }\n
\n
        return cssEscape + c;\n
    },\n
\n
    readComment: function(first){\n
        var reader  = this._reader,\n
            comment = first || "",\n
            c       = reader.read();\n
\n
        if (c == "*"){\n
            while(c){\n
                comment += c;\n
\n
                //look for end of comment\n
                if (comment.length > 2 && c == "*" && reader.peek() == "/"){\n
                    comment += reader.read();\n
                    break;\n
                }\n
\n
                c = reader.read();\n
            }\n
\n
            return comment;\n
        } else {\n
            return "";\n
        }\n
\n
    }\n
});\n
\n
\n
var Tokens  = [\n
\n
    /*\n
     * The following token names are defined in CSS3 Grammar: http://www.w3.org/TR/css3-syntax/#lexical\n
     */\n
\n
    //HTML-style comments\n
    { name: "CDO"},\n
    { name: "CDC"},\n
\n
    //ignorables\n
    { name: "S", whitespace: true/*, channel: "ws"*/},\n
    { name: "COMMENT", comment: true, hide: true, channel: "comment" },\n
\n
    //attribute equality\n
    { name: "INCLUDES", text: "~="},\n
    { name: "DASHMATCH", text: "|="},\n
    { name: "PREFIXMATCH", text: "^="},\n
    { name: "SUFFIXMATCH", text: "$="},\n
    { name: "SUBSTRINGMATCH", text: "*="},\n
\n
    //identifier types\n
    { name: "STRING"},\n
    { name: "IDENT"},\n
    { name: "HASH"},\n
\n
    //at-keywords\n
    { name: "IMPORT_SYM", text: "@import"},\n
    { name: "PAGE_SYM", text: "@page"},\n
    { name: "MEDIA_SYM", text: "@media"},\n
    { name: "FONT_FACE_SYM", text: "@font-face"},\n
    { name: "CHARSET_SYM", text: "@charset"},\n
    { name: "NAMESPACE_SYM", text: "@namespace"},\n
    { name: "VIEWPORT_SYM", text: "@viewport"},\n
    { name: "UNKNOWN_SYM" },\n
    //{ name: "ATKEYWORD"},\n
\n
    //CSS3 animations\n
    { name: "KEYFRAMES_SYM", text: [ "@keyframes", "@-webkit-keyframes", "@-moz-keyframes", "@-o-keyframes" ] },\n
\n
    //important symbol\n
    { name: "IMPORTANT_SYM"},\n
\n
    //measurements\n
    { name: "LENGTH"},\n
    { name: "ANGLE"},\n
    { name: "TIME"},\n
    { name: "FREQ"},\n
    { name: "DIMENSION"},\n
    { name: "PERCENTAGE"},\n
    { name: "NUMBER"},\n
\n
    //functions\n
    { name: "URI"},\n
    { name: "FUNCTION"},\n
\n
    //Unicode ranges\n
    { name: "UNICODE_RANGE"},\n
\n
    /*\n
     * The following token names are defined in CSS3 Selectors: http://www.w3.org/TR/css3-selectors/#selector-syntax\n
     */\n
\n
    //invalid string\n
    { name: "INVALID"},\n
\n
    //combinators\n
    { name: "PLUS", text: "+" },\n
    { name: "GREATER", text: ">"},\n
    { name: "COMMA", text: ","},\n
    { name: "TILDE", text: "~"},\n
\n
    //modifier\n
    { name: "NOT"},\n
\n
    /*\n
     * Defined in CSS3 Paged Media\n
     */\n
    { name: "TOPLEFTCORNER_SYM", text: "@top-left-corner"},\n
    { name: "TOPLEFT_SYM", text: "@top-left"},\n
    { name: "TOPCENTER_SYM", text: "@top-center"},\n
    { name: "TOPRIGHT_SYM", text: "@top-right"},\n
    { name: "TOPRIGHTCORNER_SYM", text: "@top-right-corner"},\n
    { name: "BOTTOMLEFTCORNER_SYM", text: "@bottom-left-corner"},\n
    { name: "BOTTOMLEFT_SYM", text: "@bottom-left"},\n
    { name: "BOTTOMCENTER_SYM", text: "@bottom-center"},\n
    { name: "BOTTOMRIGHT_SYM", text: "@bottom-right"},\n
    { name: "BOTTOMRIGHTCORNER_SYM", text: "@bottom-right-corner"},\n
    { name: "LEFTTOP_SYM", text: "@left-top"},\n
    { name: "LEFTMIDDLE_SYM", text: "@left-middle"},\n
    { name: "LEFTBOTTOM_SYM", text: "@left-bottom"},\n
    { name: "RIGHTTOP_SYM", text: "@right-top"},\n
    { name: "RIGHTMIDDLE_SYM", text: "@right-middle"},\n
    { name: "RIGHTBOTTOM_SYM", text: "@right-bottom"},\n
\n
    /*\n
     * The following token names are defined in CSS3 Media Queries: http://www.w3.org/TR/css3-mediaqueries/#syntax\n
     */\n
    /*{ name: "MEDIA_ONLY", state: "media"},\n
    { name: "MEDIA_NOT", state: "media"},\n
    { name: "MEDIA_AND", state: "media"},*/\n
    { name: "RESOLUTION", state: "media"},\n
\n
    /*\n
     * The following token names are not defined in any CSS specification but are used by the lexer.\n
     */\n
\n
    //not a real token, but useful for stupid IE filters\n
    { name: "IE_FUNCTION" },\n
\n
    //part of CSS3 grammar but not the Flex code\n
    { name: "CHAR" },\n
\n
    //TODO: Needed?\n
    //Not defined as tokens, but might as well be\n
    {\n
        name: "PIPE",\n
        text: "|"\n
    },\n
    {\n
        name: "SLASH",\n
        text: "/"\n
    },\n
    {\n
        name: "MINUS",\n
        text: "-"\n
    },\n
    {\n
        name: "STAR",\n
        text: "*"\n
    },\n
\n
    {\n
        name: "LBRACE",\n
        text: "{"\n
    },\n
    {\n
        name: "RBRACE",\n
        text: "}"\n
    },\n
    {\n
        name: "LBRACKET",\n
        text: "["\n
    },\n
    {\n
        name: "RBRACKET",\n
        text: "]"\n
    },\n
    {\n
        name: "EQUALS",\n
        text: "="\n
    },\n
    {\n
        name: "COLON",\n
        text: ":"\n
    },\n
    {\n
        name: "SEMICOLON",\n
        text: ";"\n
    },\n
\n
    {\n
        name: "LPAREN",\n
        text: "("\n
    },\n
    {\n
        name: "RPAREN",\n
        text: ")"\n
    },\n
    {\n
        name: "DOT",\n
        text: "."\n
    }\n
];\n
\n
(function(){\n
\n
    var nameMap = [],\n
        typeMap = {};\n
\n
    Tokens.UNKNOWN = -1;\n
    Tokens.unshift({name:"EOF"});\n
    for (var i=0, len = Tokens.length; i < len; i++){\n
        nameMap.push(Tokens[i].name);\n
        Tokens[Tokens[i].name] = i;\n
        if (Tokens[i].text){\n
            if (Tokens[i].text instanceof Array){\n
                for (var j=0; j < Tokens[i].text.length; j++){\n
                    typeMap[Tokens[i].text[j]] = i;\n
                }\n
            } else {\n
                typeMap[Tokens[i].text] = i;\n
            }\n
        }\n
    }\n
\n
    Tokens.name = function(tt){\n
        return nameMap[tt];\n
    };\n
\n
    Tokens.type = function(c){\n
        return typeMap[c] || -1;\n
    };\n
\n
})();\n
\n
\n
\n
\n
//This file will likely change a lot! Very experimental!\n
/*global Properties, ValidationTypes, ValidationError, PropertyValueIterator */\n
var Validation = {\n
\n
    validate: function(property, value){\n
\n
        //normalize name\n
        var name        = property.toString().toLowerCase(),\n
            parts       = value.parts,\n
            expression  = new PropertyValueIterator(value),\n
            spec        = Properties[name],\n
            part,\n
            valid,\n
            j, count,\n
            msg,\n
            types,\n
            last,\n
            literals,\n
            max, multi, group;\n
\n
        if (!spec) {\n
            if (name.indexOf("-") !== 0){    //vendor prefixed are ok\n
                throw new ValidationError("Unknown property \'" + property + "\'.", property.line, property.col);\n
            }\n
        } else if (typeof spec != "number"){\n
\n
            //initialization\n
            if (typeof spec == "string"){\n
                if (spec.indexOf("||") > -1) {\n
                    this.groupProperty(spec, expression);\n
                } else {\n
                    this.singleProperty(spec, expression, 1);\n
                }\n
\n
            } else if (spec.multi) {\n
                this.multiProperty(spec.multi, expression, spec.comma, spec.max || Infinity);\n
            } else if (typeof spec == "function") {\n
                spec(expression);\n
            }\n
\n
        }\n
\n
    },\n
\n
    singleProperty: function(types, expression, max, partial) {\n
\n
        var result      = false,\n
            value       = expression.value,\n
            count       = 0,\n
            part;\n
\n
        while (expression.hasNext() && count < max) {\n
            result = ValidationTypes.isAny(expression, types);\n
            if (!result) {\n
                break;\n
            }\n
            count++;\n
        }\n
\n
        if (!result) {\n
            if (expression.hasNext() && !expression.isFirst()) {\n
                part = expression.peek();\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                 throw new ValidationError("Expected (" + types + ") but found \'" + value + "\'.", value.line, value.col);\n
            }\n
        } else if (expression.hasNext()) {\n
            part = expression.next();\n
            throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
        }\n
\n
    },\n
\n
    multiProperty: function (types, expression, comma, max) {\n
\n
        var result      = false,\n
            value       = expression.value,\n
            count       = 0,\n
            sep         = false,\n
            part;\n
\n
        while(expression.hasNext() && !result && count < max) {\n
            if (ValidationTypes.isAny(expression, types)) {\n
                count++;\n
                if (!expression.hasNext()) {\n
                    result = true;\n
\n
                } else if (comma) {\n
                    if (expression.peek() == ",") {\n
                        part = expression.next();\n
                    } else {\n
                        break;\n
                    }\n
                }\n
            } else {\n
                break;\n
\n
            }\n
        }\n
\n
        if (!result) {\n
            if (expression.hasNext() && !expression.isFirst()) {\n
                part = expression.peek();\n
                throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                part = expression.previous();\n
                if (comma && part == ",") {\n
                    throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
                } else {\n
                    throw new ValidationError("Expected (" + types + ") but found \'" + value + "\'.", value.line, value.col);\n
                }\n
            }\n
\n
        } else if (expression.hasNext()) {\n
            part = expression.next();\n
            throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
        }\n
\n
    },\n
\n
    groupProperty: function (types, expression, comma) {\n
\n
        var result      = false,\n
            value       = expression.value,\n
            typeCount   = types.split("||").length,\n
            groups      = { count: 0 },\n
            partial     = false,\n
            name,\n
            part;\n
\n
        while(expression.hasNext() && !result) {\n
            name = ValidationTypes.isAnyOfGroup(expression, types);\n
            if (name) {\n
\n
                //no dupes\n
                if (groups[name]) {\n
                    break;\n
                } else {\n
                    groups[name] = 1;\n
                    groups.count++;\n
                    partial = true;\n
\n
                    if (groups.count == typeCount || !expression.hasNext()) {\n
                        result = true;\n
                    }\n
                }\n
            } else {\n
                break;\n
            }\n
        }\n
\n
        if (!result) {\n
            if (partial && expression.hasNext()) {\n
                    part = expression.peek();\n
                    throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
            } else {\n
                throw new ValidationError("Expected (" + types + ") but found \'" + value + "\'.", value.line, value.col);\n
            }\n
        } else if (expression.hasNext()) {\n
            part = expression.next();\n
            throw new ValidationError("Expected end of value but found \'" + part + "\'.", part.line, part.col);\n
        }\n
    }\n
\n
\n
\n
};\n
/**\n
 * Type to use when a validation error occurs.\n
 * @class ValidationError\n
 * @namespace parserlib.util\n
 * @constructor\n
 * @param {String} message The error message.\n
 * @param {int} line The line at which the error occurred.\n
 * @param {int} col The column at which the error occurred.\n
 */\n
function ValidationError(message, line, col){\n
\n
    /**\n
     * The column at which the error occurred.\n
     * @type int\n
     * @property col\n
     */\n
    this.col = col;\n
\n
    /**\n
     * The line at which the error occurred.\n
     * @type int\n
     * @property line\n
     */\n
    this.line = line;\n
\n
    /**\n
     * The text representation of the unit.\n
     * @type String\n
     * @property text\n
     */\n
    this.message = message;\n
\n
}\n
\n
//inherit from Error\n
ValidationError.prototype = new Error();\n
//This file will likely change a lot! Very experimental!\n
/*global Properties, Validation, ValidationError, PropertyValueIterator, console*/\n
var ValidationTypes = {\n
\n
    isLiteral: function (part, literals) {\n
        var text = part.text.toString().toLowerCase(),\n
            args = literals.split(" | "),\n
            i, len, found = false;\n
\n
        for (i=0,len=args.length; i < len && !found; i++){\n
            if (text == args[i].toLowerCase()){\n
                found = true;\n
            }\n
        }\n
\n
        return found;\n
    },\n
\n
    isSimple: function(type) {\n
        return !!this.simple[type];\n
    },\n
\n
    isComplex: function(type) {\n
        return !!this.complex[type];\n
    },\n
\n
    /**\n
     * Determines if the next part(s) of the given expression\n
     * are any of the given types.\n
     */\n
    isAny: function (expression, types) {\n
        var args = types.split(" | "),\n
            i, len, found = false;\n
\n
        for (i=0,len=args.length; i < len && !found && expression.hasNext(); i++){\n
            found = this.isType(expression, args[i]);\n
        }\n
\n
        return found;\n
    },\n
\n
    /**\n
     * Determines if the next part(s) of the given expression\n
     * are one of a group.\n
     */\n
    isAnyOfGroup: function(expression, types) {\n
        var args = types.split(" || "),\n
            i, len, found = false;\n
\n
        for (i=0,len=args.length; i < len && !found; i++){\n
            found = this.isType(expression, args[i]);\n
        }\n
\n
        return found ? args[i-1] : false;\n
    },\n
\n
    /**\n
     * Determines if the next part(s) of the given expression\n
     * are of a given type.\n
     */\n
    isType: function (expression, type) {\n
        var part = expression.peek(),\n
            result = false;\n
\n
        if (type.charAt(0) != "<") {\n
            result = this.isLiteral(part, type);\n
            if (result) {\n
                expression.next();\n
            }\n
        } else if (this.simple[type]) {\n
            result = this.simple[type](part);\n
            if (result) {\n
                expression.next();\n
            }\n
        } else {\n
            result = this.complex[type](expression);\n
        }\n
\n
        return result;\n
    },\n
\n
\n
\n
    simple: {\n
\n
        "<absolute-size>": function(part){\n
            return ValidationTypes.isLiteral(part, "xx-small | x-small | small | medium | large | x-large | xx-large");\n
        },\n
\n
        "<attachment>": function(part){\n
            return ValidationTypes.isLiteral(part, "scroll | fixed | local");\n
        },\n
\n
        "<attr>": function(part){\n
            return part.type == "function" && part.name == "attr";\n
        },\n
\n
        "<bg-image>": function(part){\n
            return this["<image>"](part) || this["<gradient>"](part) ||  part == "none";\n
        },\n
\n
        "<gradient>": function(part) {\n
            return part.type == "function" && /^(?:\\-(?:ms|moz|o|webkit)\\-)?(?:repeating\\-)?(?:radial\\-|linear\\-)?gradient/i.test(part);\n
        },\n
\n
        "<box>": function(part){\n
            return ValidationTypes.isLiteral(part, "padding-box | border-box | content-box");\n
        },\n
\n
        "<content>": function(part){\n
            return part.type == "function" && part.name == "content";\n
        },\n
\n
        "<relative-size>": function(part){\n
            return ValidationTypes.isLiteral(part, "smaller | larger");\n
        },\n
\n
        //any identifier\n
        "<ident>": function(part){\n
            return part.type == "identifier";\n
        },\n
\n
        "<length>": function(part){\n
            if (part.type == "function" && /^(?:\\-(?:ms|moz|o|webkit)\\-)?calc/i.test(part)){\n
                return true;\n
            }else{\n
                return part.type == "length" || part.type == "number" || part.type == "integer" || part == "0";\n
            }\n
        },\n
\n
        "<color>": function(part){\n
            return part.type == "color" || part == "transparent";\n
        },\n
\n
        "<number>": function(part){\n
            return part.type == "number" || this["<integer>"](part);\n
        },\n
\n
        "<integer>": function(part){\n
            return part.type == "integer";\n
        },\n
\n
        "<line>": function(part){\n
            return part.type == "integer";\n
        },\n
\n
        "<angle>": function(part){\n
            return part.type == "angle";\n
        },\n
\n
        "<uri>": function(part){\n
            return part.type == "uri";\n
        },\n
\n
        "<image>": function(part){\n
            return this["<uri>"](part);\n
        },\n
\n
        "<percentage>": function(part){\n
            return part.type == "percentage" || part == "0";\n
        },\n
\n
        "<border-width>": function(part){\n
            return this["<length>"](part) || ValidationTypes.isLiteral(part, "thin | medium | thick");\n
        },\n
\n
        "<border-style>": function(part){\n
            return ValidationTypes.isLiteral(part, "none | hidden | dotted | dashed | solid | double | groove | ridge | inset | outset");\n
        },\n
\n
        "<margin-width>": function(part){\n
            return this["<length>"](part) || this["<percentage>"](part) || ValidationTypes.isLiteral(part, "auto");\n
        },\n
\n
        "<padding-width>": function(part){\n
            return this["<length>"](part) || this["<percentage>"](part);\n
        },\n
\n
        "<shape>": function(part){\n
            return part.type == "function" && (part.name == "rect" || part.name == "inset-rect");\n
        },\n
\n
        "<time>": function(part) {\n
            return part.type == "time";\n
        }\n
    },\n
\n
    complex: {\n
\n
        "<bg-position>": function(expression){\n
            var types   = this,\n
                result  = false,\n
                numeric = "<percentage> | <length>",\n
                xDir    = "left | right",\n
                yDir    = "top | bottom",\n
                count = 0,\n
                hasNext = function() {\n
                    return expression.hasNext() && expression.peek() != ",";\n
                };\n
\n
            while (expression.peek(count) && expression.peek(count) != ",") {\n
                count++;\n
            }\n
\n
/*\n
<position> = [\n
  [ left | center | right | top | bottom | <percentage> | <length> ]\n
|\n
  [ left | center | right | <percentage> | <length> ]\n
  [ top | center | bottom | <percentage> | <length> ]\n
|\n
  [ center | [ left | right ] [ <percentage> | <length> ]? ] &&\n
  [ center | [ top | bottom ] [ <percentage> | <length> ]? ]\n
]\n
*/\n
\n
            if (count < 3) {\n
                if (ValidationTypes.isAny(expression, xDir + " | center | " + numeric)) {\n
                        result = true;\n
                        ValidationTypes.isAny(expression, yDir + " | center | " + numeric);\n
                } else if (ValidationTypes.isAny(expression, yDir)) {\n
                        result = true;\n
                        ValidationTypes.isAny(expression, xDir + " | center");\n
                }\n
            } else {\n
                if (ValidationTypes.isAny(expression, xDir)) {\n
                    if (ValidationTypes.isAny(expression, yDir)) {\n
                        result = true;\n
                        ValidationTypes.isAny(expression, numeric);\n
                    } else if (ValidationTypes.isAny(expression, numeric)) {\n
                        if (ValidationTypes.isAny(expression, yDir)) {\n
                            result = true;\n
                            ValidationTypes.isAny(expression, numeric);\n
                        } else if (ValidationTypes.isAny(expression, "center")) {\n
                            result = true;\n
                        }\n
                    }\n
                } else if (ValidationTypes.isAny(expression, yDir)) {\n
                    if (ValidationTypes.isAny(expression, xDir)) {\n
                        result = true;\n
                        ValidationTypes.isAny(expression, numeric);\n
                    } else if (ValidationTypes.isAny(expression, numeric)) {\n
                        if (ValidationTypes.isAny(expression, xDir)) {\n
                                result = true;\n
                                ValidationTypes.isAny(expression, numeric);\n
                        } else if (ValidationTypes.isAny(expression, "center")) {\n
                            result = true;\n
                        }\n
                    }\n
                } else if (ValidationTypes.isAny(expression, "center")) {\n
                    if (ValidationTypes.isAny(expression, xDir + " | " + yDir)) {\n
                        result = true;\n
                        ValidationTypes.isAny(expression, numeric);\n
                    }\n
                }\n
            }\n
\n
            return result;\n
        },\n
\n
        "<bg-size>": function(expression){\n
            //<bg-size> = [ <length> | <percentage> | auto ]{1,2} | cover | contain\n
            var types   = this,\n
                result  = false,\n
                numeric = "<percentage> | <length> | auto",\n
                part,\n
                i, len;\n
\n
            if (ValidationTypes.isAny(expression, "cover | contain")) {\n
                result = true;\n
            } else if (ValidationTypes.isAny(expression, numeric)) {\n
                result = true;\n
                ValidationTypes.isAny(expression, numeric);\n
            }\n
\n
            return result;\n
        },\n
\n
        "<repeat-style>": function(expression){\n
            //repeat-x | repeat-y | [repeat | space | round | no-repeat]{1,2}\n
            var result  = false,\n
                values  = "repeat | space | round | no-repeat",\n
                part;\n
\n
            if (expression.hasNext()){\n
                part = expression.next();\n
\n
                if (ValidationTypes.isLiteral(part, "repeat-x | repeat-y")) {\n
                    result = true;\n
                } else if (ValidationTypes.isLiteral(part, values)) {\n
                    result = true;\n
\n
                    if (expression.hasNext() && ValidationTypes.isLiteral(expression.peek(), values)) {\n
                        expression.next();\n
                    }\n
                }\n
            }\n
\n
            return result;\n
\n
        },\n
\n
        "<shadow>": function(expression) {\n
            //inset? && [ <length>{2,4} && <color>? ]\n
            var result  = false,\n
                count   = 0,\n
                inset   = false,\n
                color   = false,\n
                part;\n
\n
            if (expression.hasNext()) {\n
\n
                if (ValidationTypes.isAny(expression, "inset")){\n
                    inset = true;\n
                }\n
\n
                if (ValidationTypes.isAny(expression, "<color>")) {\n
                    color = true;\n
                }\n
\n
                while (ValidationTypes.isAny(expression, "<length>") && count < 4) {\n
                    count++;\n
                }\n
\n
\n
                if (expression.hasNext()) {\n
                    if (!color) {\n
                        ValidationTypes.isAny(expression, "<color>");\n
                    }\n
\n
                    if (!inset) {\n
                        ValidationTypes.isAny(expression, "inset");\n
                    }\n
\n
                }\n
\n
                result = (count >= 2 && count <= 4);\n
\n
            }\n
\n
            return result;\n
        },\n
\n
        "<x-one-radius>": function(expression) {\n
            //[ <length> | <percentage> ] [ <length> | <percentage> ]?\n
            var result  = false,\n
                simple = "<length> | <percentage> | inherit";\n
\n
            if (ValidationTypes.isAny(expression, simple)){\n
                result = true;\n
                ValidationTypes.isAny(expression, simple);\n
            }\n
\n
            return result;\n
        }\n
    }\n
};\n
\n
\n
\n
parserlib.css = {\n
Colors              :Colors,\n
Combinator          :Combinator,\n
Parser              :Parser,\n
PropertyName        :PropertyName,\n
PropertyValue       :PropertyValue,\n
PropertyValuePart   :PropertyValuePart,\n
MediaFeature        :MediaFeature,\n
MediaQuery          :MediaQuery,\n
Selector            :Selector,\n
SelectorPart        :SelectorPart,\n
SelectorSubPart     :SelectorSubPart,\n
Specificity         :Specificity,\n
TokenStream         :TokenStream,\n
Tokens              :Tokens,\n
ValidationError     :ValidationError\n
};\n
})();\n
\n
\n
\n
\n
(function(){\n
for(var prop in parserlib){\n
exports[prop] = parserlib[prop];\n
}\n
})();\n
\n
\n
/**\n
 * Main CSSLint object.\n
 * @class CSSLint\n
 * @static\n
 * @extends parserlib.util.EventTarget\n
 */\n
/*global parserlib, Reporter*/\n
var CSSLint = (function(){\n
\n
    var rules           = [],\n
        formatters      = [],\n
        embeddedRuleset = /\\/\\*csslint([^\\*]*)\\*\\//,\n
        api             = new parserlib.util.EventTarget();\n
\n
    api.version = "0.10.0";\n
\n
    //-------------------------------------------------------------------------\n
    // Rule Management\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Adds a new rule to the engine.\n
     * @param {Object} rule The rule to add.\n
     * @method addRule\n
     */\n
    api.addRule = function(rule){\n
        rules.push(rule);\n
        rules[rule.id] = rule;\n
    };\n
\n
    /**\n
     * Clears all rule from the engine.\n
     * @method clearRules\n
     */\n
    api.clearRules = function(){\n
        rules = [];\n
    };\n
\n
    /**\n
     * Returns the rule objects.\n
     * @return An array of rule objects.\n
     * @method getRules\n
     */\n
    api.getRules = function(){\n
        return [].concat(rules).sort(function(a,b){\n
            return a.id > b.id ? 1 : 0;\n
        });\n
    };\n
\n
    /**\n
     * Returns a ruleset configuration object with all current rules.\n
     * @return A ruleset object.\n
     * @method getRuleset\n
     */\n
    api.getRuleset = function() {\n
        var ruleset = {},\n
            i = 0,\n
            len = rules.length;\n
\n
        while (i < len){\n
            ruleset[rules[i++].id] = 1;    //by default, everything is a warning\n
        }\n
\n
        return ruleset;\n
    };\n
\n
    /**\n
     * Returns a ruleset object based on embedded rules.\n
     * @param {String} text A string of css containing embedded rules.\n
     * @param {Object} ruleset A ruleset object to modify.\n
     * @return {Object} A ruleset object.\n
     * @method getEmbeddedRuleset\n
     */\n
    function applyEmbeddedRuleset(text, ruleset){\n
        var valueMap,\n
            embedded = text && text.match(embeddedRuleset),\n
            rules = embedded && embedded[1];\n
\n
        if (rules) {\n
            valueMap = {\n
                "true": 2,  // true is error\n
                "": 1,      // blank is warning\n
                "false": 0, // false is ignore\n
\n
                "2": 2,     // explicit error\n
                "1": 1,     // explicit warning\n
                "0": 0      // explicit ignore\n
            };\n
\n
            rules.toLowerCase().split(",").forEach(function(rule){\n
                var pair = rule.split(":"),\n
                    property = pair[0] || "",\n
                    value = pair[1] || "";\n
\n
                ruleset[property.trim()] = valueMap[value.trim()];\n
            });\n
        }\n
\n
        return ruleset;\n
    }\n
\n
    //-------------------------------------------------------------------------\n
    // Formatters\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Adds a new formatter to the engine.\n
     * @param {Object} formatter The formatter to add.\n
     * @method addFormatter\n
     */\n
    api.addFormatter = function(formatter) {\n
        // formatters.push(formatter);\n
        formatters[formatter.id] = formatter;\n
    };\n
\n
    /**\n
     * Retrieves a formatter for use.\n
     * @param {String} formatId The name of the format to retrieve.\n
     * @return {Object} The formatter or undefined.\n
     * @method getFormatter\n
     */\n
    api.getFormatter = function(formatId){\n
        return formatters[formatId];\n
    };\n
\n
    /**\n
     * Formats the results in a particular format for a single file.\n
     * @param {Object} result The results returned from CSSLint.verify().\n
     * @param {String} filename The filename for which the results apply.\n
     * @param {String} formatId The name of the formatter to use.\n
     * @param {Object} options (Optional) for special output handling.\n
     * @return {String} A formatted string for the results.\n
     * @method format\n
     */\n
    api.format = function(results, filename, formatId, options) {\n
        var formatter = this.getFormatter(formatId),\n
            result = null;\n
\n
        if (formatter){\n
            result = formatter.startFormat();\n
            result += formatter.formatResults(results, filename, options || {});\n
            result += formatter.endFormat();\n
        }\n
\n
        return result;\n
    };\n
\n
    /**\n
     * Indicates if the given format is supported.\n
     * @param {String} formatId The ID of the format to check.\n
     * @return {Boolean} True if the format exists, false if not.\n
     * @method hasFormat\n
     */\n
    api.hasFormat = function(formatId){\n
        return formatters.hasOwnProperty(formatId);\n
    };\n
\n
    //-------------------------------------------------------------------------\n
    // Verification\n
    //-------------------------------------------------------------------------\n
\n
    /**\n
     * Starts the verification process for the given CSS text.\n
     * @param {String} text The CSS text to verify.\n
     * @param {Object} ruleset (Optional) List of rules to apply. If null, then\n
     *      all rules are used. If a rule has a value of 1 then it\'s a warning,\n
     *      a value of 2 means it\'s an error.\n
     * @return {Object} Results of the verification.\n
     * @method verify\n
     */\n
    api.verify = function(text, ruleset){\n
\n
        var i       = 0,\n
            len     = rules.length,\n
            reporter,\n
            lines,\n
            report,\n
            parser = new parserlib.css.Parser({ starHack: true, ieFilters: true,\n
                                                underscoreHack: true, strict: false });\n
\n
        // normalize line endings\n
        lines = text.replace(/\\n\\r?/g, "$split$").split(\'$split$\');\n
\n
        if (!ruleset){\n
            ruleset = this.getRuleset();\n
        }\n
\n
        if (embeddedRuleset.test(text)){\n
            ruleset = applyEmbeddedRuleset(text, ruleset);\n
        }\n
\n
        reporter = new Reporter(lines, ruleset);\n
\n
        ruleset.errors = 2;       //always report parsing errors as errors\n
        for (i in ruleset){\n
            if(ruleset.hasOwnProperty(i) && ruleset[i]){\n
                if (rules[i]){\n
                    rules[i].init(parser, reporter);\n
                }\n
            }\n
        }\n
\n
\n
        //capture most horrible error type\n
        try {\n
            parser.parse(text);\n
        } catch (ex) {\n
            reporter.error("Fatal error, cannot continue: " + ex.message, ex.line, ex.col, {});\n
        }\n
\n
        report = {\n
            messages    : reporter.messages,\n
            stats       : reporter.stats,\n
            ruleset     : reporter.ruleset\n
        };\n
\n
        //sort by line numbers, rollups at the bottom\n
        report.messages.sort(function (a, b){\n
            if (a.rollup && !b.rollup){\n
                return 1;\n
            } else if (!a.rollup && b.rollup){\n
                return -1;\n
            } else {\n
                return a.line - b.line;\n
            }\n
        });\n
\n
        return report;\n
    };\n
\n
    //-------------------------------------------------------------------------\n
    // Publish the API\n
    //-------------------------------------------------------------------------\n
\n
    return api;\n
\n
})();\n
\n
/*global CSSLint*/\n
/**\n
 * An instance of Report is used to report results of the\n
 * verification back to the main API.\n
 * @class Reporter\n
 * @constructor\n
 * @param {String[]} lines The text lines of the source.\n
 * @param {Object} ruleset The set of rules to work with, including if\n
 *      they are errors or warnings.\n
 */\n
function Reporter(lines, ruleset){\n
\n
    /**\n
     * List of messages being reported.\n
     * @property messages\n
     * @type String[]\n
     */\n
    this.messages = [];\n
\n
    /**\n
     * List of statistics being reported.\n
     * @property stats\n
     * @type String[]\n
     */\n
    this.stats = [];\n
\n
    /**\n
     * Lines of code being reported on. Used to provide contextual information\n
     * for messages.\n
     * @property lines\n
     * @type String[]\n
     */\n
    this.lines = lines;\n
\n
    /**\n
     * Information about the rules. Used to determine whether an issue is an\n
     * error or warning.\n
     * @property ruleset\n
     * @type Object\n
     */\n
    this.ruleset = ruleset;\n
}\n
\n
Reporter.prototype = {\n
\n
    //restore constructor\n
    constructor: Reporter,\n
\n
    /**\n
     * Report an error.\n
     * @param {String} message The message to store.\n
     * @param {int} line The line number.\n
     * @param {int} col The column number.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method error\n
     */\n
    error: function(message, line, col, rule){\n
        this.messages.push({\n
            type    : "error",\n
            line    : line,\n
            col     : col,\n
            message : message,\n
            evidence: this.lines[line-1],\n
            rule    : rule || {}\n
        });\n
    },\n
\n
    /**\n
     * Report an warning.\n
     * @param {String} message The message to store.\n
     * @param {int} line The line number.\n
     * @param {int} col The column number.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method warn\n
     * @deprecated Use report instead.\n
     */\n
    warn: function(message, line, col, rule){\n
        this.report(message, line, col, rule);\n
    },\n
\n
    /**\n
     * Report an issue.\n
     * @param {String} message The message to store.\n
     * @param {int} line The line number.\n
     * @param {int} col The column number.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method report\n
     */\n
    report: function(message, line, col, rule){\n
        this.messages.push({\n
            type    : this.ruleset[rule.id] == 2 ? "error" : "warning",\n
            line    : line,\n
            col     : col,\n
            message : message,\n
            evidence: this.lines[line-1],\n
            rule    : rule\n
        });\n
    },\n
\n
    /**\n
     * Report some informational text.\n
     * @param {String} message The message to store.\n
     * @param {int} line The line number.\n
     * @param {int} col The column number.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method info\n
     */\n
    info: function(message, line, col, rule){\n
        this.messages.push({\n
            type    : "info",\n
            line    : line,\n
            col     : col,\n
            message : message,\n
            evidence: this.lines[line-1],\n
            rule    : rule\n
        });\n
    },\n
\n
    /**\n
     * Report some rollup error information.\n
     * @param {String} message The message to store.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method rollupError\n
     */\n
    rollupError: function(message, rule){\n
        this.messages.push({\n
            type    : "error",\n
            rollup  : true,\n
            message : message,\n
            rule    : rule\n
        });\n
    },\n
\n
    /**\n
     * Report some rollup warning information.\n
     * @param {String} message The message to store.\n
     * @param {Object} rule The rule this message relates to.\n
     * @method rollupWarn\n
     */\n
    rollupWarn: function(message, rule){\n
        this.messages.push({\n
            type    : "warning",\n
            rollup  : true,\n
            message : message,\n
            rule    : rule\n
        });\n
    },\n
\n
    /**\n
     * Report a statistic.\n
     * @param {String} name The name of the stat to store.\n
     * @param {Variant} value The value of the stat.\n
     * @method stat\n
     */\n
    stat: function(name, value){\n
        this.stats[name] = value;\n
    }\n
};\n
\n
//expose for testing purposes\n
CSSLint._Reporter = Reporter;\n
\n
/*global CSSLint*/\n
\n
/*\n
 * Utility functions that make life easier.\n
 */\n
CSSLint.Util = {\n
    /*\n
     * Adds all properties from supplier onto receiver,\n
     * overwriting if the same name already exists on\n
     * reciever.\n
     * @param {Object} The object to receive the properties.\n
     * @param {Object} The object to provide the properties.\n
     * @return {Object} The receiver\n
     */\n
    mix: function(receiver, supplier){\n
        var prop;\n
\n
        for (prop in supplier){\n
            if (supplier.hasOwnProperty(prop)){\n
                receiver[prop] = supplier[prop];\n
            }\n
        }\n
\n
        return prop;\n
    },\n
\n
    /*\n
     * Polyfill for array indexOf() method.\n
     * @param {Array} values The array to search.\n
     * @param {Variant} value The value to search for.\n
     * @return {int} The index of the value if found, -1 if not.\n
     */\n
    indexOf: function(values, value){\n
        if (values.indexOf){\n
            return values.indexOf(value);\n
        } else {\n
            for (var i=0, len=values.length; i < len; i++){\n
                if (values[i] === value){\n
                    return i;\n
                }\n
            }\n
            return -1;\n
        }\n
    },\n
\n
    /*\n
     * Polyfill for array forEach() method.\n
     * @param {Array} values The array to operate on.\n
     * @param {Function} func The function to call on each item.\n
     * @return {void}\n
     */\n
    forEach: function(values, func) {\n
        if (values.forEach){\n
            return values.forEach(func);\n
        } else {\n
            for (var i=0, len=values.length; i < len; i++){\n
                func(values[i], i, values);\n
            }\n
        }\n
    }\n
};\n
/*global CSSLint*/\n
/*\n
 * Rule: Don\'t use adjoining classes (.foo.bar).\n
 */\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "adjoining-classes",\n
    name: "Disallow adjoining classes",\n
    desc: "Don\'t use adjoining classes.",\n
    browsers: "IE6",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                classCount,\n
                i, j, k;\n
\n
            for (i=0; i < selectors.length; i++){\n
                selector = selectors[i];\n
                for (j=0; j < selector.parts.length; j++){\n
                    part = selector.parts[j];\n
                    if (part.type == parser.SELECTOR_PART_TYPE){\n
                        classCount = 0;\n
                        for (k=0; k < part.modifiers.length; k++){\n
                            modifier = part.modifiers[k];\n
                            if (modifier.type == "class"){\n
                                classCount++;\n
                            }\n
                            if (classCount > 1){\n
                                reporter.report("Don\'t use adjoining classes.", part.line, part.col, rule);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
    }\n
\n
});\n
/*global CSSLint*/\n
\n
/*\n
 * Rule: Don\'t use width or height when using padding or border.\n
 */\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "box-model",\n
    name: "Beware of broken box size",\n
    desc: "Don\'t use width or height when using padding or border.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            widthProperties = {\n
                border: 1,\n
                "border-left": 1,\n
                "border-right": 1,\n
                padding: 1,\n
                "padding-left": 1,\n
                "padding-right": 1\n
            },\n
            heightProperties = {\n
                border: 1,\n
                "border-bottom": 1,\n
                "border-top": 1,\n
                padding: 1,\n
                "padding-bottom": 1,\n
                "padding-top": 1\n
            },\n
            properties,\n
            boxSizing = false;\n
\n
        function startRule(){\n
            properties = {};\n
            boxSizing = false;\n
        }\n
\n
        function endRule(){\n
            var prop, value;\n
\n
            if (!boxSizing) {\n
                if (properties.height){\n
                    for (prop in heightProperties){\n
                        if (heightProperties.hasOwnProperty(prop) && properties[prop]){\n
                            value = properties[prop].value;\n
                            //special case for padding\n
                            if (!(prop == "padding" && value.parts.length === 2 && value.parts[0].value === 0)){\n
                                reporter.report("Using height with " + prop + " can sometimes make elements larger than you expect.", properties[prop].line, properties[prop].col, rule);\n
                            }\n
                        }\n
                    }\n
                }\n
\n
                if (properties.width){\n
                    for (prop in widthProperties){\n
                        if (widthProperties.hasOwnProperty(prop) && properties[prop]){\n
                            value = properties[prop].value;\n
\n
                            if (!(prop == "padding" && value.parts.length === 2 && value.parts[1].value === 0)){\n
                                reporter.report("Using width with " + prop + " can sometimes make elements larger than you expect.", properties[prop].line, properties[prop].col, rule);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startpage", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase();\n
\n
            if (heightProperties[name] || widthProperties[name]){\n
                if (!/^0\\S*$/.test(event.value) && !(name == "border" && event.value == "none")){\n
                    properties[name] = { line: event.property.line, col: event.property.col, value: event.value };\n
                }\n
            } else {\n
                if (/^(width|height)/i.test(name) && /^(length|percentage)/.test(event.value.parts[0].type)){\n
                    properties[name] = 1;\n
                } else if (name == "box-sizing") {\n
                    boxSizing = true;\n
                }\n
            }\n
\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
        parser.addListener("endpage", endRule);\n
        parser.addListener("endpagemargin", endRule);\n
        parser.addListener("endkeyframerule", endRule);\n
    }\n
\n
});\n
/*global CSSLint*/\n
\n
/*\n
 * Rule: box-sizing doesn\'t work in IE6 and IE7.\n
 */\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "box-sizing",\n
    name: "Disallow use of box-sizing",\n
    desc: "The box-sizing properties isn\'t supported in IE6 and IE7.",\n
    browsers: "IE6, IE7",\n
    tags: ["Compatibility"],\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase();\n
\n
            if (name == "box-sizing"){\n
                reporter.report("The box-sizing property isn\'t supported in IE6 and IE7.", event.line, event.col, rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Use the bulletproof @font-face syntax to avoid 404\'s in old IE\n
 * (http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax)\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "bulletproof-font-face",\n
    name: "Use the bulletproof @font-face syntax",\n
    desc: "Use the bulletproof @font-face syntax to avoid 404\'s in old IE (http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax).",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0,\n
            fontFaceRule = false,\n
            firstSrc     = true,\n
            ruleFailed    = false,\n
            line, col;\n
\n
        // Mark the start of a @font-face declaration so we only test properties inside it\n
        parser.addListener("startfontface", function(event){\n
            fontFaceRule = true;\n
        });\n
\n
        parser.addListener("property", function(event){\n
            // If we aren\'t inside an @font-face declaration then just return\n
            if (!fontFaceRule) {\n
                return;\n
            }\n
\n
            var propertyName = event.property.toString().toLowerCase(),\n
                value        = event.value.toString();\n
\n
            // Set the line and col numbers for use in the endfontface listener\n
            line = event.line;\n
            col  = event.col;\n
\n
            // This is the property that we care about, we can ignore the rest\n
            if (propertyName === \'src\') {\n
                var regex = /^\\s?url\\([\'"].+\\.eot\\?.*[\'"]\\)\\s*format\\([\'"]embedded-opentype[\'"]\\).*$/i;\n
\n
                // We need to handle the advanced syntax with two src properties\n
                if (!value.match(regex) && firstSrc) {\n
                    ruleFailed = true;\n
                    firstSrc = false;\n
                } else if (value.match(regex) && !firstSrc) {\n
                    ruleFailed = false;\n
                }\n
            }\n
\n
\n
        });\n
\n
        // Back to normal rules that we don\'t need to test\n
        parser.addListener("endfontface", function(event){\n
            fontFaceRule = false;\n
\n
            if (ruleFailed) {\n
                reporter.report("@font-face declaration doesn\'t follow the fontspring bulletproof syntax.", line, col, rule);\n
            }\n
        });\n
    }\n
});\n
/*\n
 * Rule: Include all compatible vendor prefixes to reach a wider\n
 * range of users.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "compatible-vendor-prefixes",\n
    name: "Require compatible vendor prefixes",\n
    desc: "Include all compatible vendor prefixes to reach a wider range of users.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function (parser, reporter) {\n
        var rule = this,\n
            compatiblePrefixes,\n
            properties,\n
            prop,\n
            variations,\n
            prefixed,\n
            i,\n
            len,\n
            inKeyFrame = false,\n
            arrayPush = Array.prototype.push,\n
            applyTo = [];\n
\n
        // See http://peter.sh/experiments/vendor-prefixed-css-property-overview/ for details\n
        compatiblePrefixes = {\n
            "animation"                  : "webkit moz",\n
            "animation-delay"            : "webkit moz",\n
            "animation-direction"        : "webkit moz",\n
            "animation-duration"         : "webkit moz",\n
            "animation-fill-mode"        : "webkit moz",\n
            "animation-iteration-count"  : "webkit moz",\n
            "animation-name"             : "webkit moz",\n
            "animation-play-state"       : "webkit moz",\n
            "animation-timing-function"  : "webkit moz",\n
            "appearance"                 : "webkit moz",\n
            "border-end"                 : "webkit moz",\n
            "border-end-color"           : "webkit moz",\n
            "border-end-style"           : "webkit moz",\n
            "border-end-width"           : "webkit moz",\n
            "border-image"               : "webkit moz o",\n
            "border-radius"              : "webkit",\n
            "border-start"               : "webkit moz",\n
            "border-start-color"         : "webkit moz",\n
            "border-start-style"         : "webkit moz",\n
            "border-start-width"         : "webkit moz",\n
            "box-align"                  : "webkit moz ms",\n
            "box-direction"              : "webkit moz ms",\n
            "box-flex"                   : "webkit moz ms",\n
            "box-lines"                  : "webkit ms",\n
            "box-ordinal-group"          : "webkit moz ms",\n
            "box-orient"                 : "webkit moz ms",\n
            "box-pack"                   : "webkit moz ms",\n
            "box-sizing"                 : "webkit moz",\n
            "box-shadow"                 : "webkit moz",\n
            "column-count"               : "webkit moz ms",\n
            "column-gap"                 : "webkit moz ms",\n
            "column-rule"                : "webkit moz ms",\n
            "column-rule-color"          : "webkit moz ms",\n
            "column-rule-style"          : "webkit moz ms",\n
            "column-rule-width"          : "webkit moz ms",\n
            "column-width"               : "webkit moz ms",\n
            "hyphens"                    : "epub moz",\n
            "line-break"                 : "webkit ms",\n
            "margin-end"                 : "webkit moz",\n
            "margin-start"               : "webkit moz",\n
            "marquee-speed"              : "webkit wap",\n
            "marquee-style"              : "webkit wap",\n
            "padding-end"                : "webkit moz",\n
            "padding-start"              : "webkit moz",\n
            "tab-size"                   : "moz o",\n
            "text-size-adjust"           : "webkit ms",\n
            "transform"                  

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
            <value> <string>: "webkit moz ms o",\n
            "transform-origin"           : "webkit moz ms o",\n
            "transition"                 : "webkit moz o",\n
            "transition-delay"           : "webkit moz o",\n
            "transition-duration"        : "webkit moz o",\n
            "transition-property"        : "webkit moz o",\n
            "transition-timing-function" : "webkit moz o",\n
            "user-modify"                : "webkit moz",\n
            "user-select"                : "webkit moz ms",\n
            "word-break"                 : "epub ms",\n
            "writing-mode"               : "epub ms"\n
        };\n
\n
\n
        for (prop in compatiblePrefixes) {\n
            if (compatiblePrefixes.hasOwnProperty(prop)) {\n
                variations = [];\n
                prefixed = compatiblePrefixes[prop].split(\' \');\n
                for (i = 0, len = prefixed.length; i \074 len; i++) {\n
                    variations.push(\'-\' + prefixed[i] + \'-\' + prop);\n
                }\n
                compatiblePrefixes[prop] = variations;\n
                arrayPush.apply(applyTo, variations);\n
            }\n
        }\n
\n
        parser.addListener("startrule", function () {\n
            properties = [];\n
        });\n
\n
        parser.addListener("startkeyframes", function (event) {\n
            inKeyFrame = event.prefix || true;\n
        });\n
\n
        parser.addListener("endkeyframes", function (event) {\n
            inKeyFrame = false;\n
        });\n
\n
        parser.addListener("property", function (event) {\n
            var name = event.property;\n
            if (CSSLint.Util.indexOf(applyTo, name.text) \076 -1) {\n
\n
                // e.g., -moz-transform is okay to be alone in @-moz-keyframes\n
                if (!inKeyFrame || typeof inKeyFrame != "string" ||\n
                        name.text.indexOf("-" + inKeyFrame + "-") !== 0) {\n
                    properties.push(name);\n
                }\n
            }\n
        });\n
\n
        parser.addListener("endrule", function (event) {\n
            if (!properties.length) {\n
                return;\n
            }\n
\n
            var propertyGroups = {},\n
                i,\n
                len,\n
                name,\n
                prop,\n
                variations,\n
                value,\n
                full,\n
                actual,\n
                item,\n
                propertiesSpecified;\n
\n
            for (i = 0, len = properties.length; i \074 len; i++) {\n
                name = properties[i];\n
\n
                for (prop in compatiblePrefixes) {\n
                    if (compatiblePrefixes.hasOwnProperty(prop)) {\n
                        variations = compatiblePrefixes[prop];\n
                        if (CSSLint.Util.indexOf(variations, name.text) \076 -1) {\n
                            if (!propertyGroups[prop]) {\n
                                propertyGroups[prop] = {\n
                                    full : variations.slice(0),\n
                                    actual : [],\n
                                    actualNodes: []\n
                                };\n
                            }\n
                            if (CSSLint.Util.indexOf(propertyGroups[prop].actual, name.text) === -1) {\n
                                propertyGroups[prop].actual.push(name.text);\n
                                propertyGroups[prop].actualNodes.push(name);\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
\n
            for (prop in propertyGroups) {\n
                if (propertyGroups.hasOwnProperty(prop)) {\n
                    value = propertyGroups[prop];\n
                    full = value.full;\n
                    actual = value.actual;\n
\n
                    if (full.length \076 actual.length) {\n
                        for (i = 0, len = full.length; i \074 len; i++) {\n
                            item = full[i];\n
                            if (CSSLint.Util.indexOf(actual, item) === -1) {\n
                                propertiesSpecified = (actual.length === 1) ? actual[0] : (actual.length == 2) ? actual.join(" and ") : actual.join(", ");\n
                                reporter.report("The property " + item + " is compatible with " + propertiesSpecified + " and should be included as well.", value.actualNodes[0].line, value.actualNodes[0].col, rule);\n
                            }\n
                        }\n
\n
                    }\n
                }\n
            }\n
        });\n
    }\n
});\n
/*\n
 * Rule: Certain properties don\'t play well with certain display values.\n
 * - float should not be used with inline-block\n
 * - height, width, margin-top, margin-bottom, float should not be used with inline\n
 * - vertical-align should not be used with block\n
 * - margin, float should not be used with table-*\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "display-property-grouping",\n
    name: "Require properties appropriate for display",\n
    desc: "Certain properties shouldn\'t be used with certain display property values.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        var propertiesToCheck = {\n
                display: 1,\n
                "float": "none",\n
                height: 1,\n
                width: 1,\n
                margin: 1,\n
                "margin-left": 1,\n
                "margin-right": 1,\n
                "margin-bottom": 1,\n
                "margin-top": 1,\n
                padding: 1,\n
                "padding-left": 1,\n
                "padding-right": 1,\n
                "padding-bottom": 1,\n
                "padding-top": 1,\n
                "vertical-align": 1\n
            },\n
            properties;\n
\n
        function reportProperty(name, display, msg){\n
            if (properties[name]){\n
                if (typeof propertiesToCheck[name] != "string" || properties[name].value.toLowerCase() != propertiesToCheck[name]){\n
                    reporter.report(msg || name + " can\'t be used with display: " + display + ".", properties[name].line, properties[name].col, rule);\n
                }\n
            }\n
        }\n
\n
        function startRule(){\n
            properties = {};\n
        }\n
\n
        function endRule(){\n
\n
            var display = properties.display ? properties.display.value : null;\n
            if (display){\n
                switch(display){\n
\n
                    case "inline":\n
                        //height, width, margin-top, margin-bottom, float should not be used with inline\n
                        reportProperty("height", display);\n
                        reportProperty("width", display);\n
                        reportProperty("margin", display);\n
                        reportProperty("margin-top", display);\n
                        reportProperty("margin-bottom", display);\n
                        reportProperty("float", display, "display:inline has no effect on floated elements (but may be used to fix the IE6 double-margin bug).");\n
                        break;\n
\n
                    case "block":\n
                        //vertical-align should not be used with block\n
                        reportProperty("vertical-align", display);\n
                        break;\n
\n
                    case "inline-block":\n
                        //float should not be used with inline-block\n
                        reportProperty("float", display);\n
                        break;\n
\n
                    default:\n
                        //margin, float should not be used with table\n
                        if (display.indexOf("table-") === 0){\n
                            reportProperty("margin", display);\n
                            reportProperty("margin-left", display);\n
                            reportProperty("margin-right", display);\n
                            reportProperty("margin-top", display);\n
                            reportProperty("margin-bottom", display);\n
                            reportProperty("float", display);\n
                        }\n
\n
                        //otherwise do nothing\n
                }\n
            }\n
\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startpage", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase();\n
\n
            if (propertiesToCheck[name]){\n
                properties[name] = { value: event.value.text, line: event.property.line, col: event.property.col };\n
            }\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
        parser.addListener("endkeyframerule", endRule);\n
        parser.addListener("endpagemargin", endRule);\n
        parser.addListener("endpage", endRule);\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Disallow duplicate background-images (using url).\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "duplicate-background-images",\n
    name: "Disallow duplicate background images",\n
    desc: "Every background-image should be unique. Use a common class for e.g. sprites.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            stack = {};\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text,\n
                value = event.value,\n
                i, len;\n
\n
            if (name.match(/background/i)) {\n
                for (i=0, len=value.parts.length; i \074 len; i++) {\n
                    if (value.parts[i].type == \'uri\') {\n
                        if (typeof stack[value.parts[i].uri] === \'undefined\') {\n
                            stack[value.parts[i].uri] = event;\n
                        }\n
                        else {\n
                            reporter.report("Background image \'" + value.parts[i].uri + "\' was used multiple times, first declared at line " + stack[value.parts[i].uri].line + ", col " + stack[value.parts[i].uri].col + ".", event.line, event.col, rule);\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
    }\n
});\n
/*\n
 * Rule: Duplicate properties must appear one after the other. If an already-defined\n
 * property appears somewhere else in the rule, then it\'s likely an error.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "duplicate-properties",\n
    name: "Disallow duplicate properties",\n
    desc: "Duplicate properties must appear one after the other.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            properties,\n
            lastProperty;\n
\n
        function startRule(event){\n
            properties = {};\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startpage", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var property = event.property,\n
                name = property.text.toLowerCase();\n
\n
            if (properties[name] \046\046 (lastProperty != name || properties[name] == event.value.text)){\n
                reporter.report("Duplicate property \'" + event.property + "\' found.", event.line, event.col, rule);\n
            }\n
\n
            properties[name] = event.value.text;\n
            lastProperty = name;\n
\n
        });\n
\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Style rules without any properties defined should be removed.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "empty-rules",\n
    name: "Disallow empty rules",\n
    desc: "Rules without any properties specified should be removed.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0;\n
\n
        parser.addListener("startrule", function(){\n
            count=0;\n
        });\n
\n
        parser.addListener("property", function(){\n
            count++;\n
        });\n
\n
        parser.addListener("endrule", function(event){\n
            var selectors = event.selectors;\n
            if (count === 0){\n
                reporter.report("Rule is empty.", selectors[0].line, selectors[0].col, rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: There should be no syntax errors. (Duh.)\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "errors",\n
    name: "Parsing Errors",\n
    desc: "This rule looks for recoverable syntax errors.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("error", function(event){\n
            reporter.error(event.message, event.line, event.col, rule);\n
        });\n
\n
    }\n
\n
});\n
\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "fallback-colors",\n
    name: "Require fallback colors",\n
    desc: "For older browsers that don\'t support RGBA, HSL, or HSLA, provide a fallback color.",\n
    browsers: "IE6,IE7,IE8",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            lastProperty,\n
            propertiesToCheck = {\n
                color: 1,\n
                background: 1,\n
                "border-color": 1,\n
                "border-top-color": 1,\n
                "border-right-color": 1,\n
                "border-bottom-color": 1,\n
                "border-left-color": 1,\n
                border: 1,\n
                "border-top": 1,\n
                "border-right": 1,\n
                "border-bottom": 1,\n
                "border-left": 1,\n
                "background-color": 1\n
            },\n
            properties;\n
\n
        function startRule(event){\n
            properties = {};\n
            lastProperty = null;\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startpage", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var property = event.property,\n
                name = property.text.toLowerCase(),\n
                parts = event.value.parts,\n
                i = 0,\n
                colorType = "",\n
                len = parts.length;\n
\n
            if(propertiesToCheck[name]){\n
                while(i \074 len){\n
                    if (parts[i].type == "color"){\n
                        if ("alpha" in parts[i] || "hue" in parts[i]){\n
\n
                            if (/([^\\)]+)\\(/.test(parts[i])){\n
                                colorType = RegExp.$1.toUpperCase();\n
                            }\n
\n
                            if (!lastProperty || (lastProperty.property.text.toLowerCase() != name || lastProperty.colorType != "compat")){\n
                                reporter.report("Fallback " + name + " (hex or RGB) should precede " + colorType + " " + name + ".", event.line, event.col, rule);\n
                            }\n
                        } else {\n
                            event.colorType = "compat";\n
                        }\n
                    }\n
\n
                    i++;\n
                }\n
            }\n
\n
            lastProperty = event;\n
        });\n
\n
    }\n
\n
});\n
/*\n
 * Rule: You shouldn\'t use more than 10 floats. If you do, there\'s probably\n
 * room for some abstraction.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "floats",\n
    name: "Disallow too many floats",\n
    desc: "This rule tests if the float property is used too many times",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
        var count = 0;\n
\n
        //count how many times "float" is used\n
        parser.addListener("property", function(event){\n
            if (event.property.text.toLowerCase() == "float" \046\046\n
                    event.value.text.toLowerCase() != "none"){\n
                count++;\n
            }\n
        });\n
\n
        //report the results\n
        parser.addListener("endstylesheet", function(){\n
            reporter.stat("floats", count);\n
            if (count \076= 10){\n
                reporter.rollupWarn("Too many floats (" + count + "), you\'re probably using them for layout. Consider using a grid system instead.", rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Avoid too many @font-face declarations in the same stylesheet.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "font-faces",\n
    name: "Don\'t use too many web fonts",\n
    desc: "Too many different web fonts in the same stylesheet.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0;\n
\n
\n
        parser.addListener("startfontface", function(){\n
            count++;\n
        });\n
\n
        parser.addListener("endstylesheet", function(){\n
            if (count \076 5){\n
                reporter.rollupWarn("Too many @font-face declarations (" + count + ").", rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: You shouldn\'t need more than 9 font-size declarations.\n
 */\n
\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "font-sizes",\n
    name: "Disallow too many font sizes",\n
    desc: "Checks the number of font-size declarations.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0;\n
\n
        //check for use of "font-size"\n
        parser.addListener("property", function(event){\n
            if (event.property == "font-size"){\n
                count++;\n
            }\n
        });\n
\n
        //report the results\n
        parser.addListener("endstylesheet", function(){\n
            reporter.stat("font-sizes", count);\n
            if (count \076= 10){\n
                reporter.rollupWarn("Too many font-size declarations (" + count + "), abstraction needed.", rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: When using a vendor-prefixed gradient, make sure to use them all.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "gradients",\n
    name: "Require all gradient definitions",\n
    desc: "When using a vendor-prefixed gradient, make sure to use them all.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            gradients;\n
\n
        parser.addListener("startrule", function(){\n
            gradients = {\n
                moz: 0,\n
                webkit: 0,\n
                oldWebkit: 0,\n
                o: 0\n
            };\n
        });\n
\n
        parser.addListener("property", function(event){\n
\n
            if (/\\-(moz|o|webkit)(?:\\-(?:linear|radial))\\-gradient/i.test(event.value)){\n
                gradients[RegExp.$1] = 1;\n
            } else if (/\\-webkit\\-gradient/i.test(event.value)){\n
                gradients.oldWebkit = 1;\n
            }\n
\n
        });\n
\n
        parser.addListener("endrule", function(event){\n
            var missing = [];\n
\n
            if (!gradients.moz){\n
                missing.push("Firefox 3.6+");\n
            }\n
\n
            if (!gradients.webkit){\n
                missing.push("Webkit (Safari 5+, Chrome)");\n
            }\n
\n
            if (!gradients.oldWebkit){\n
                missing.push("Old Webkit (Safari 4+, Chrome)");\n
            }\n
\n
            if (!gradients.o){\n
                missing.push("Opera 11.1+");\n
            }\n
\n
            if (missing.length \046\046 missing.length \074 4){\n
                reporter.report("Missing vendor-prefixed CSS gradients for " + missing.join(", ") + ".", event.selectors[0].line, event.selectors[0].col, rule);\n
            }\n
\n
        });\n
\n
    }\n
\n
});\n
\n
/*\n
 * Rule: Don\'t use IDs for selectors.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "ids",\n
    name: "Disallow IDs in selectors",\n
    desc: "Selectors should not contain IDs.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                idCount,\n
                i, j, k;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
                idCount = 0;\n
\n
                for (j=0; j \074 selector.parts.length; j++){\n
                    part = selector.parts[j];\n
                    if (part.type == parser.SELECTOR_PART_TYPE){\n
                        for (k=0; k \074 part.modifiers.length; k++){\n
                            modifier = part.modifiers[k];\n
                            if (modifier.type == "id"){\n
                                idCount++;\n
                            }\n
                        }\n
                    }\n
                }\n
\n
                if (idCount == 1){\n
                    reporter.report("Don\'t use IDs in selectors.", selector.line, selector.col, rule);\n
                } else if (idCount \076 1){\n
                    reporter.report(idCount + " IDs in the selector, really?", selector.line, selector.col, rule);\n
                }\n
            }\n
\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use @import, use \074link\076 instead.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "import",\n
    name: "Disallow @import",\n
    desc: "Don\'t use @import, use \074link\076 instead.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("import", function(event){\n
            reporter.report("@import prevents parallel downloads, use \074link\076 instead.", event.line, event.col, rule);\n
        });\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Make sure !important is not overused, this could lead to specificity\n
 * war. Display a warning on !important declarations, an error if it\'s\n
 * used more at least 10 times.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "important",\n
    name: "Disallow !important",\n
    desc: "Be careful when using !important declaration",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0;\n
\n
        //warn that important is used and increment the declaration counter\n
        parser.addListener("property", function(event){\n
            if (event.important === true){\n
                count++;\n
                reporter.report("Use of !important", event.line, event.col, rule);\n
            }\n
        });\n
\n
        //if there are more than 10, show an error\n
        parser.addListener("endstylesheet", function(){\n
            reporter.stat("important", count);\n
            if (count \076= 10){\n
                reporter.rollupWarn("Too many !important declarations (" + count + "), try to use less than 10 to avoid specificity issues.", rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Properties should be known (listed in CSS3 specification) or\n
 * be a vendor-prefixed property.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "known-properties",\n
    name: "Require use of known properties",\n
    desc: "Properties should be known (listed in CSS3 specification) or be a vendor-prefixed property.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase();\n
\n
            // the check is handled entirely by the parser-lib (https://github.com/nzakas/parser-lib)\n
            if (event.invalid) {\n
                reporter.report(event.invalid.message, event.line, event.col, rule);\n
            }\n
\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: outline: none or outline: 0 should only be used in a :focus rule\n
 *       and only if there are other properties in the same rule.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "outline-none",\n
    name: "Disallow outline: none",\n
    desc: "Use of outline: none or outline: 0 should be limited to :focus rules.",\n
    browsers: "All",\n
    tags: ["Accessibility"],\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            lastRule;\n
\n
        function startRule(event){\n
            if (event.selectors){\n
                lastRule = {\n
                    line: event.line,\n
                    col: event.col,\n
                    selectors: event.selectors,\n
                    propCount: 0,\n
                    outline: false\n
                };\n
            } else {\n
                lastRule = null;\n
            }\n
        }\n
\n
        function endRule(event){\n
            if (lastRule){\n
                if (lastRule.outline){\n
                    if (lastRule.selectors.toString().toLowerCase().indexOf(":focus") == -1){\n
                        reporter.report("Outlines should only be modified using :focus.", lastRule.line, lastRule.col, rule);\n
                    } else if (lastRule.propCount == 1) {\n
                        reporter.report("Outlines shouldn\'t be hidden unless other visual changes are made.", lastRule.line, lastRule.col, rule);\n
                    }\n
                }\n
            }\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startpage", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase(),\n
                value = event.value;\n
\n
            if (lastRule){\n
                lastRule.propCount++;\n
                if (name == "outline" \046\046 (value == "none" || value == "0")){\n
                    lastRule.outline = true;\n
                }\n
            }\n
\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
        parser.addListener("endpage", endRule);\n
        parser.addListener("endpagemargin", endRule);\n
        parser.addListener("endkeyframerule", endRule);\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use classes or IDs with elements (a.foo or a#foo).\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "overqualified-elements",\n
    name: "Disallow overqualified elements",\n
    desc: "Don\'t use classes or IDs with elements (a.foo or a#foo).",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            classes = {};\n
\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                i, j, k;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
\n
                for (j=0; j \074 selector.parts.length; j++){\n
                    part = selector.parts[j];\n
                    if (part.type == parser.SELECTOR_PART_TYPE){\n
                        for (k=0; k \074 part.modifiers.length; k++){\n
                            modifier = part.modifiers[k];\n
                            if (part.elementName \046\046 modifier.type == "id"){\n
                                reporter.report("Element (" + part + ") is overqualified, just use " + modifier + " without element name.", part.line, part.col, rule);\n
                            } else if (modifier.type == "class"){\n
\n
                                if (!classes[modifier]){\n
                                    classes[modifier] = [];\n
                                }\n
                                classes[modifier].push({ modifier: modifier, part: part });\n
                            }\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
\n
        parser.addListener("endstylesheet", function(){\n
\n
            var prop;\n
            for (prop in classes){\n
                if (classes.hasOwnProperty(prop)){\n
\n
                    //one use means that this is overqualified\n
                    if (classes[prop].length == 1 \046\046 classes[prop][0].part.elementName){\n
                        reporter.report("Element (" + classes[prop][0].part + ") is overqualified, just use " + classes[prop][0].modifier + " without element name.", classes[prop][0].part.line, classes[prop][0].part.col, rule);\n
                    }\n
                }\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Headings (h1-h6) should not be qualified (namespaced).\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "qualified-headings",\n
    name: "Disallow qualified headings",\n
    desc: "Headings should not be qualified (namespaced).",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                i, j;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
\n
                for (j=0; j \074 selector.parts.length; j++){\n
                    part = selector.parts[j];\n
                    if (part.type == parser.SELECTOR_PART_TYPE){\n
                        if (part.elementName \046\046 /h[1-6]/.test(part.elementName.toString()) \046\046 j \076 0){\n
                            reporter.report("Heading (" + part.elementName + ") should not be qualified.", part.line, part.col, rule);\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Selectors that look like regular expressions are slow and should be avoided.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "regex-selectors",\n
    name: "Disallow selectors that look like regexs",\n
    desc: "Selectors that look like regular expressions are slow and should be avoided.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                i, j, k;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
                for (j=0; j \074 selector.parts.length; j++){\n
                    part = selector.parts[j];\n
                    if (part.type == parser.SELECTOR_PART_TYPE){\n
                        for (k=0; k \074 part.modifiers.length; k++){\n
                            modifier = part.modifiers[k];\n
                            if (modifier.type == "attribute"){\n
                                if (/([\\~\\|\\^\\$\\*]=)/.test(modifier)){\n
                                    reporter.report("Attribute selectors with " + RegExp.$1 + " are slow!", modifier.line, modifier.col, rule);\n
                                }\n
                            }\n
\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Total number of rules should not exceed x.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "rules-count",\n
    name: "Rules Count",\n
    desc: "Track how many rules there are.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            count = 0;\n
\n
        //count each rule\n
        parser.addListener("startrule", function(){\n
            count++;\n
        });\n
\n
        parser.addListener("endstylesheet", function(){\n
            reporter.stat("rule-count", count);\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Warn people with approaching the IE 4095 limit\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "selector-max-approaching",\n
    name: "Warn when approaching the 4095 selector limit for IE",\n
    desc: "Will warn when selector count is \076= 3800 selectors.",\n
    browsers: "IE",\n
\n
    //initialization\n
    init: function(parser, reporter) {\n
        var rule = this, count = 0;\n
\n
        parser.addListener(\'startrule\', function(event) {\n
            count += event.selectors.length;\n
        });\n
\n
        parser.addListener("endstylesheet", function() {\n
            if (count \076= 3800) {\n
                reporter.report("You have " + count + " selectors. Internet Explorer supports a maximum of 4095 selectors per stylesheet. Consider refactoring.",0,0,rule);\n
            }\n
        });\n
    }\n
\n
});\n
\n
/*\n
 * Rule: Warn people past the IE 4095 limit\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "selector-max",\n
    name: "Error when past the 4095 selector limit for IE",\n
    desc: "Will error when selector count is \076 4095.",\n
    browsers: "IE",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this, count = 0;\n
\n
        parser.addListener(\'startrule\',function(event) {\n
            count += event.selectors.length;\n
        });\n
\n
        parser.addListener("endstylesheet", function() {\n
            if (count \076 4095) {\n
                reporter.report("You have " + count + " selectors. Internet Explorer supports a maximum of 4095 selectors per stylesheet. Consider refactoring.",0,0,rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Use shorthand properties where possible.\n
 *\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "shorthand",\n
    name: "Require shorthand properties",\n
    desc: "Use shorthand properties where possible.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            prop, i, len,\n
            propertiesToCheck = {},\n
            properties,\n
            mapping = {\n
                "margin": [\n
                    "margin-top",\n
                    "margin-bottom",\n
                    "margin-left",\n
                    "margin-right"\n
                ],\n
                "padding": [\n
                    "padding-top",\n
                    "padding-bottom",\n
                    "padding-left",\n
                    "padding-right"\n
                ]\n
            };\n
\n
        //initialize propertiesToCheck\n
        for (prop in mapping){\n
            if (mapping.hasOwnProperty(prop)){\n
                for (i=0, len=mapping[prop].length; i \074 len; i++){\n
                    propertiesToCheck[mapping[prop][i]] = prop;\n
                }\n
            }\n
        }\n
\n
        function startRule(event){\n
            properties = {};\n
        }\n
\n
        //event handler for end of rules\n
        function endRule(event){\n
\n
            var prop, i, len, total;\n
\n
            //check which properties this rule has\n
            for (prop in mapping){\n
                if (mapping.hasOwnProperty(prop)){\n
                    total=0;\n
\n
                    for (i=0, len=mapping[prop].length; i \074 len; i++){\n
                        total += properties[mapping[prop][i]] ? 1 : 0;\n
                    }\n
\n
                    if (total == mapping[prop].length){\n
                        reporter.report("The properties " + mapping[prop].join(", ") + " can be replaced by " + prop + ".", event.line, event.col, rule);\n
                    }\n
                }\n
            }\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
\n
        //check for use of "font-size"\n
        parser.addListener("property", function(event){\n
            var name = event.property.toString().toLowerCase(),\n
                value = event.value.parts[0].value;\n
\n
            if (propertiesToCheck[name]){\n
                properties[name] = 1;\n
            }\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use properties with a star prefix.\n
 *\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "star-property-hack",\n
    name: "Disallow properties with a star prefix",\n
    desc: "Checks for the star property hack (targets IE6/7)",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        //check if property name starts with "*"\n
        parser.addListener("property", function(event){\n
            var property = event.property;\n
\n
            if (property.hack == "*") {\n
                reporter.report("Property with star prefix found.", event.property.line, event.property.col, rule);\n
            }\n
        });\n
    }\n
});\n
/*\n
 * Rule: Don\'t use text-indent for image replacement if you need to support rtl.\n
 *\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "text-indent",\n
    name: "Disallow negative text-indent",\n
    desc: "Checks for text indent less than -99px",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            textIndent,\n
            direction;\n
\n
\n
        function startRule(event){\n
            textIndent = false;\n
            direction = "inherit";\n
        }\n
\n
        //event handler for end of rules\n
        function endRule(event){\n
            if (textIndent \046\046 direction != "ltr"){\n
                reporter.report("Negative text-indent doesn\'t work well with RTL. If you use text-indent for image replacement explicitly set direction for that item to ltr.", textIndent.line, textIndent.col, rule);\n
            }\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
\n
        //check for use of "font-size"\n
        parser.addListener("property", function(event){\n
            var name = event.property.toString().toLowerCase(),\n
                value = event.value;\n
\n
            if (name == "text-indent" \046\046 value.parts[0].value \074 -99){\n
                textIndent = event.property;\n
            } else if (name == "direction" \046\046 value == "ltr"){\n
                direction = "ltr";\n
            }\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use properties with a underscore prefix.\n
 *\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "underscore-property-hack",\n
    name: "Disallow properties with an underscore prefix",\n
    desc: "Checks for the underscore property hack (targets IE6)",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        //check if property name starts with "_"\n
        parser.addListener("property", function(event){\n
            var property = event.property;\n
\n
            if (property.hack == "_") {\n
                reporter.report("Property with underscore prefix found.", event.property.line, event.property.col, rule);\n
            }\n
        });\n
    }\n
});\n
/*\n
 * Rule: Headings (h1-h6) should be defined only once.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "unique-headings",\n
    name: "Headings should only be defined once",\n
    desc: "Headings should be defined only once.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        var headings =  {\n
                h1: 0,\n
                h2: 0,\n
                h3: 0,\n
                h4: 0,\n
                h5: 0,\n
                h6: 0\n
            };\n
\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                pseudo,\n
                i, j;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
                part = selector.parts[selector.parts.length-1];\n
\n
                if (part.elementName \046\046 /(h[1-6])/i.test(part.elementName.toString())){\n
\n
                    for (j=0; j \074 part.modifiers.length; j++){\n
                        if (part.modifiers[j].type == "pseudo"){\n
                            pseudo = true;\n
                            break;\n
                        }\n
                    }\n
\n
                    if (!pseudo){\n
                        headings[RegExp.$1]++;\n
                        if (headings[RegExp.$1] \076 1) {\n
                            reporter.report("Heading (" + part.elementName + ") has already been defined.", part.line, part.col, rule);\n
                        }\n
                    }\n
                }\n
            }\n
        });\n
\n
        parser.addListener("endstylesheet", function(event){\n
            var prop,\n
                messages = [];\n
\n
            for (prop in headings){\n
                if (headings.hasOwnProperty(prop)){\n
                    if (headings[prop] \076 1){\n
                        messages.push(headings[prop] + " " + prop + "s");\n
                    }\n
                }\n
            }\n
\n
            if (messages.length){\n
                reporter.rollupWarn("You have " + messages.join(", ") + " defined in this stylesheet.", rule);\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use universal selector because it\'s slow.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "universal-selector",\n
    name: "Disallow universal selector",\n
    desc: "The universal selector (*) is known to be slow.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("startrule", function(event){\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                i, j, k;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
\n
                part = selector.parts[selector.parts.length-1];\n
                if (part.elementName == "*"){\n
                    reporter.report(rule.desc, part.line, part.col, rule);\n
                }\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: Don\'t use unqualified attribute selectors because they\'re just like universal selectors.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "unqualified-attributes",\n
    name: "Disallow unqualified attribute selectors",\n
    desc: "Unqualified attribute selectors are known to be slow.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        parser.addListener("startrule", function(event){\n
\n
            var selectors = event.selectors,\n
                selector,\n
                part,\n
                modifier,\n
                i, j, k;\n
\n
            for (i=0; i \074 selectors.length; i++){\n
                selector = selectors[i];\n
\n
                part = selector.parts[selector.parts.length-1];\n
                if (part.type == parser.SELECTOR_PART_TYPE){\n
                    for (k=0; k \074 part.modifiers.length; k++){\n
                        modifier = part.modifiers[k];\n
                        if (modifier.type == "attribute" \046\046 (!part.elementName || part.elementName == "*")){\n
                            reporter.report(rule.desc, part.line, part.col, rule);\n
                        }\n
                    }\n
                }\n
\n
            }\n
        });\n
    }\n
\n
});\n
/*\n
 * Rule: When using a vendor-prefixed property, make sure to\n
 * include the standard one.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "vendor-prefix",\n
    name: "Require standard property with vendor prefix",\n
    desc: "When using a vendor-prefixed property, make sure to include the standard one.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this,\n
            properties,\n
            num,\n
            propertiesToCheck = {\n
                "-webkit-border-radius": "border-radius",\n
                "-webkit-border-top-left-radius": "border-top-left-radius",\n
                "-webkit-border-top-right-radius": "border-top-right-radius",\n
                "-webkit-border-bottom-left-radius": "border-bottom-left-radius",\n
                "-webkit-border-bottom-right-radius": "border-bottom-right-radius",\n
\n
                "-o-border-radius": "border-radius",\n
                "-o-border-top-left-radius": "border-top-left-radius",\n
                "-o-border-top-right-radius": "border-top-right-radius",\n
                "-o-border-bottom-left-radius": "border-bottom-left-radius",\n
                "-o-border-bottom-right-radius": "border-bottom-right-radius",\n
\n
                "-moz-border-radius": "border-radius",\n
                "-moz-border-radius-topleft": "border-top-left-radius",\n
                "-moz-border-radius-topright": "border-top-right-radius",\n
                "-moz-border-radius-bottomleft": "border-bottom-left-radius",\n
                "-moz-border-radius-bottomright": "border-bottom-right-radius",\n
\n
                "-moz-column-count": "column-count",\n
                "-webkit-column-count": "column-count",\n
\n
                "-moz-column-gap": "column-gap",\n
                "-webkit-column-gap": "column-gap",\n
\n
                "-moz-column-rule": "column-rule",\n
                "-webkit-column-rule": "column-rule",\n
\n
                "-moz-column-rule-style": "column-rule-style",\n
                "-webkit-column-rule-style": "column-rule-style",\n
\n
                "-moz-column-rule-color": "column-rule-color",\n
                "-webkit-column-rule-color": "column-rule-color",\n
\n
                "-moz-column-rule-width": "column-rule-width",\n
                "-webkit-column-rule-width": "column-rule-width",\n
\n
                "-moz-column-width": "column-width",\n
                "-webkit-column-width": "column-width",\n
\n
                "-webkit-column-span": "column-span",\n
                "-webkit-columns": "columns",\n
\n
                "-moz-box-shadow": "box-shadow",\n
                "-webkit-box-shadow": "box-shadow",\n
\n
                "-moz-transform" : "transform",\n
                "-webkit-transform" : "transform",\n
                "-o-transform" : "transform",\n
                "-ms-transform" : "transform",\n
\n
                "-moz-transform-origin" : "transform-origin",\n
                "-webkit-transform-origin" : "transform-origin",\n
                "-o-transform-origin" : "transform-origin",\n
                "-ms-transform-origin" : "transform-origin",\n
\n
                "-moz-box-sizing" : "box-sizing",\n
                "-webkit-box-sizing" : "box-sizing",\n
\n
                "-moz-user-select" : "user-select",\n
                "-khtml-user-select" : "user-select",\n
                "-webkit-user-select" : "user-select"\n
            };\n
\n
        //event handler for beginning of rules\n
        function startRule(){\n
            properties = {};\n
            num=1;\n
        }\n
\n
        //event handler for end of rules\n
        function endRule(event){\n
            var prop,\n
                i, len,\n
                standard,\n
                needed,\n
                actual,\n
                needsStandard = [];\n
\n
            for (prop in properties){\n
                if (propertiesToCheck[prop]){\n
                    needsStandard.push({ actual: prop, needed: propertiesToCheck[prop]});\n
                }\n
            }\n
\n
            for (i=0, len=needsStandard.length; i \074 len; i++){\n
                needed = needsStandard[i].needed;\n
                actual = needsStandard[i].actual;\n
\n
                if (!properties[needed]){\n
                    reporter.report("Missing standard property \'" + needed + "\' to go along with \'" + actual + "\'.", properties[actual][0].name.line, properties[actual][0].name.col, rule);\n
                } else {\n
                    //make sure standard property is last\n
                    if (properties[needed][0].pos \074 properties[actual][0].pos){\n
                        reporter.report("Standard property \'" + needed + "\' should come after vendor-prefixed property \'" + actual + "\'.", properties[actual][0].name.line, properties[actual][0].name.col, rule);\n
                    }\n
                }\n
            }\n
\n
        }\n
\n
        parser.addListener("startrule", startRule);\n
        parser.addListener("startfontface", startRule);\n
        parser.addListener("startpage", startRule);\n
        parser.addListener("startpagemargin", startRule);\n
        parser.addListener("startkeyframerule", startRule);\n
\n
        parser.addListener("property", function(event){\n
            var name = event.property.text.toLowerCase();\n
\n
            if (!properties[name]){\n
                properties[name] = [];\n
            }\n
\n
            properties[name].push({ name: event.property, value : event.value, pos:num++ });\n
        });\n
\n
        parser.addListener("endrule", endRule);\n
        parser.addListener("endfontface", endRule);\n
        parser.addListener("endpage", endRule);\n
        parser.addListener("endpagemargin", endRule);\n
        parser.addListener("endkeyframerule", endRule);\n
    }\n
\n
});\n
/*\n
 * Rule: You don\'t need to specify units when a value is 0.\n
 */\n
/*global CSSLint*/\n
CSSLint.addRule({\n
\n
    //rule information\n
    id: "zero-units",\n
    name: "Disallow units for 0 values",\n
    desc: "You don\'t need to specify units when a value is 0.",\n
    browsers: "All",\n
\n
    //initialization\n
    init: function(parser, reporter){\n
        var rule = this;\n
\n
        //count how many times "float" is used\n
        parser.addListener("property", function(event){\n
            var parts = event.value.parts,\n
                i = 0,\n
                len = parts.length;\n
\n
            while(i \074 len){\n
                if ((parts[i].units || parts[i].type == "percentage") \046\046 parts[i].value === 0 \046\046 parts[i].type != "time"){\n
                    reporter.report("Values of 0 shouldn\'t have units specified.", parts[i].line, parts[i].col, rule);\n
                }\n
                i++;\n
            }\n
\n
        });\n
\n
    }\n
\n
});\n
/*global CSSLint*/\n
(function() {\n
\n
    /**\n
     * Replace special characters before write to output.\n
     *\n
     * Rules:\n
     *  - single quotes is the escape sequence for double-quotes\n
     *  - \046amp; is the escape sequence for \046\n
     *  - \046lt; is the escape sequence for \074\n
     *  - \046gt; is the escape sequence for \076\n
     *\n
     * @param {String} message to escape\n
     * @return escaped message as {String}\n
     */\n
    var xmlEscape = function(str) {\n
        if (!str || str.constructor !== String) {\n
            return "";\n
        }\n
\n
        return str.replace(/[\\"\046\076\074]/g, function(match) {\n
            switch (match) {\n
                case "\\"":\n
                    return "\046quot;";\n
                case "\046":\n
                    return "\046amp;";\n
                case "\074":\n
                    return "\046lt;";\n
                case "\076":\n
                    return "\046gt;";\n
            }\n
        });\n
    };\n
\n
    CSSLint.addFormatter({\n
        //format information\n
        id: "checkstyle-xml",\n
        name: "Checkstyle XML format",\n
\n
        /**\n
         * Return opening root XML tag.\n
         * @return {String} to prepend before all results\n
         */\n
        startFormat: function(){\n
            return "\074?xml version=\\"1.0\\" encoding=\\"utf-8\\"?\076\074checkstyle\076";\n
        },\n
\n
        /**\n
         * Return closing root XML tag.\n
         * @return {String} to append after all results\n
         */\n
        endFormat: function(){\n
            return "\074/checkstyle\076";\n
        },\n
\n
        /**\n
         * Returns message when there is a file read error.\n
         * @param {String} filename The name of the file that caused the error.\n
         * @param {String} message The error message\n
         * @return {String} The error message.\n
         */\n
        readError: function(filename, message) {\n
            return "\074file name=\\"" + xmlEscape(filename) + "\\"\076\074error line=\\"0\\" column=\\"0\\" severty=\\"error\\" message=\\"" + xmlEscape(message) + "\\"\076\074/error\076\074/file\076";\n
        },\n
\n
        /**\n
         * Given CSS Lint results for a file, return output for this format.\n
         * @param results {Object} with error and warning messages\n
         * @param filename {String} relative file path\n
         * @param options {Object} (UNUSED for now) specifies special handling of output\n
         * @return {String} output for results\n
         */\n
        formatResults: function(results, filename, options) {\n
            var messages = results.messages,\n
                output = [];\n
\n
            /**\n
             * Generate a source string for a rule.\n
             * Checkstyle source strings usually resemble Java class names e.g\n
             * net.csslint.SomeRuleName\n
             * @param {Object} rule\n
             * @return rule source as {String}\n
             */\n
            var generateSource = function(rule) {\n
                if (!rule || !(\'name\' in rule)) {\n
                    return "";\n
                }\n
                return \'net.csslint.\' + rule.name.replace(/\\s/g,\'\');\n
            };\n
\n
\n
\n
            if (messages.length \076 0) {\n
                output.push("\074file name=\\""+filename+"\\"\076");\n
                CSSLint.Util.forEach(messages, function (message, i) {\n
                    //ignore rollups for now\n
                    if (!message.rollup) {\n
                      output.push("\074error line=\\"" + message.line + "\\" column=\\"" + message.col + "\\" severity=\\"" + message.type + "\\"" +\n
                          " message=\\"" + xmlEscape(message.message) + "\\" source=\\"" + generateSource(message.rule) +"\\"/\076");\n
                    }\n
                });\n
                output.push("\074/file\076");\n
            }\n
\n
            return output.join("");\n
        }\n
    });\n
\n
}());\n
/*global CSSLint*/\n
CSSLint.addFormatter({\n
    //format information\n
    id: "compact",\n
    name: "Compact, \'porcelain\' format",\n
\n
    /**\n
     * Return content to be printed before all file results.\n
     * @return {String} to prepend before all results\n
     */\n
    startFormat: function() {\n
        return "";\n
    },\n
\n
    /**\n
     * Return content to be printed after all file results.\n
     * @return {String} to append after all results\n
     */\n
    endFormat: function() {\n
        return "";\n
    },\n
\n
    /**\n
     * Given CSS Lint results for a file, return output for this format.\n
     * @param results {Object} with error and warning messages\n
     * @param filename {String} relative file path\n
     * @param options {Object} (Optional) specifies special handling of output\n
     * @return {String} output for results\n
     */\n
    formatResults: function(results, filename, options) {\n
        var messages = results.messages,\n
            output = "";\n
        options = options || {};\n
\n
        /**\n
         * Capitalize and return given string.\n
         * @param str {String} to capitalize\n
         * @return {String} capitalized\n
         */\n
        var capitalize = function(str) {\n
            return str.charAt(0).toUpperCase() + str.slice(1);\n
        };\n
\n
        if (messages.length === 0) {\n
            return options.quiet ? "" : filename + ": Lint Free!";\n
        }\n
\n
        CSSLint.Util.forEach(messages, function(message, i) {\n
            if (message.rollup) {\n
                output += filename + ": " + capitalize(message.type) + " - " + message.message + "\\n";\n
            } else {\n
                output += filename + ": " + "line " + message.line +\n
                    ", col " + message.col + ", " + capitalize(message.type) + " - " + message.message + "\\n";\n
            }\n
        });\n
\n
        return output;\n
    }\n
});\n
/*global CSSLint*/\n
CSSLint.addFormatter({\n
    //format information\n
    id: "csslint-xml",\n
    name: "CSSLint XML format",\n
\n
    /**\n
     * Return opening root XML tag.\n
     * @return {String} to prepend before all results\n
     */\n
    startFormat: function(){\n
        return "\074?xml version=\\"1.0\\" encoding=\\"utf-8\\"?\076\074csslint\076";\n
    },\n
\n
    /**\n
     * Return closing root XML tag.\n
     * @return {String} to append after all results\n
     */\n
    endFormat: function(){\n
        return "\074/csslint\076";\n
    },\n
\n
    /**\n
     * Given CSS Lint results for a file, return output for this format.\n
     * @param results {Object} with error and warning messages\n
     * @param filename {String} relative file path\n
     * @param options {Object} (UNUSED for now) specifies special handling of output\n
     * @return {String} output for results\n
     */\n
    formatResults: function(results, filename, options) {\n
        var messages = results.messages,\n
            output = [];\n
\n
        /**\n
         * Replace special characters before write to output.\n
         *\n
         * Rules:\n
         *  - single quotes is the escape sequence for double-quotes\n
         *  - \046amp; is the escape sequence for \046\n
         *  - \046lt; is the escape sequence for \074\n
         *  - \046gt; is the escape sequence for \076\n
         *\n
         * @param {String} message to escape\n
         * @return escaped message as {String}\n
         */\n
        var escapeSpecialCharacters = function(str) {\n
            if (!str || str.constructor !== String) {\n
                return "";\n
            }\n
            return str.replace(/\\"/g, "\'").replace(/\046/g, "\046amp;").replace(/\074/g, "\046lt;").replace(/\076/g, "\046gt;");\n
        };\n
\n
        if (messages.length \076 0) {\n
            output.push("\074file name=\\""+filename+"\\"\076");\n
            CSSLint.Util.forEach(messages, function (message, i) {\n
                if (message.rollup) {\n
                    output.push("\074issue severity=\\"" + message.type + "\\" reason=\\"" + escapeSpecialCharacters(message.message) + "\\" evidence=\\"" + escapeSpecialCharacters(message.evidence) + "\\"/\076");\n
                } else {\n
                    output.push("\074issue line=\\"" + message.line + "\\" char=\\"" + message.col + "\\" severity=\\"" + message.type + "\\"" +\n
                        " reason=\\"" + escapeSpecialCharacters(message.message) + "\\" evidence=\\"" + escapeSpecialCharacters(message.evidence) + "\\"/\076");\n
                }\n
            });\n
            output.push("\074/file\076");\n
        }\n
\n
        return output.join("");\n
    }\n
});\n
/*global CSSLint*/\n
CSSLint.addFormatter({\n
    //format information\n
    id: "junit-xml",\n
    name: "JUNIT XML format",\n
\n
    /**\n
     * Return opening root XML tag.\n
     * @return {String} to prepend before all results\n
     */\n
    startFormat: function(){\n
        return "\074?xml version=\\"1.0\\" encoding=\\"utf-8\\"?\076\074testsuites\076";\n
    },\n
\n
    /**\n
     * Return closing root XML tag.\n
     * @return {String} to append after all results\n
     */\n
    endFormat: function() {\n
        return "\074/testsuites\076";\n
    },\n
\n
    /**\n
     * Given CSS Lint results for a file, return output for this format.\n
     * @param results {Object} with error and warning messages\n
     * @param filename {String} relative file path\n
     * @param options {Object} (UNUSED for now) specifies special handling of output\n
     * @return {String} output for results\n
     */\n
    formatResults: function(results, filename, options) {\n
\n
        var messages = results.messages,\n
            output = [],\n
            tests = {\n
                \'error\': 0,\n
                \'failure\': 0\n
            };\n
\n
        /**\n
         * Generate a source string for a rule.\n
         * JUNIT source strings usually resemble Java class names e.g\n
         * net.csslint.SomeRuleName\n
         * @param {Object} rule\n
         * @return rule source as {String}\n
         */\n
        var generateSource = function(rule) {\n
            if (!rule || !(\'name\' in rule)) {\n
                return "";\n
            }\n
            return \'net.csslint.\' + rule.name.replace(/\\s/g,\'\');\n
        };\n
\n
        /**\n
         * Replace special characters before write to output.\n
         *\n
         * Rules:\n
         *  - single quotes is the escape sequence for double-quotes\n
         *  - \046lt; is the escape sequence for \074\n
         *  - \046gt; is the escape sequence for \076\n
         *\n
         * @param {String} message to escape\n
         * @return escaped message as {String}\n
         */\n
        var escapeSpecialCharacters = function(str) {\n
\n
            if (!str || str.constructor !== String) {\n
                return "";\n
            }\n
\n
            return str.replace(/\\"/g, "\'").replace(/\074/g, "\046lt;").replace(/\076/g, "\046gt;");\n
\n
        };\n
\n
        if (messages.length \076 0) {\n
\n
            messages.forEach(function (message, i) {\n
\n
                // since junit has no warning class\n
                // all issues as errors\n
                var type = message.type === \'warning\' ? \'error\' : message.type;\n
\n
                //ignore rollups for now\n
                if (!message.rollup) {\n
\n
                    // build the test case seperately, once joined\n
                    // we\'ll add it to a custom array filtered by type\n
                    output.push("\074testcase time=\\"0\\" name=\\"" + generateSource(message.rule) + "\\"\076");\n
                    output.push("\074" + type + " message=\\"" + escapeSpecialCharacters(message.message) + "\\"\076\074![CDATA[" + message.line + \':\' + message.col + \':\' + escapeSpecialCharacters(message.evidence)  + "]]\076\074/" + type + "\076");\n
                    output.push("\074/testcase\076");\n
\n
                    tests[type] += 1;\n
\n
                }\n
\n
            });\n
\n
            output.unshift("\074testsuite time=\\"0\\" tests=\\"" + messages.length + "\\" skipped=\\"0\\" errors=\\"" + tests.error + "\\" failures=\\"" + tests.failure + "\\" package=\\"net.csslint\\" name=\\"" + filename + "\\"\076");\n
            output.push("\074/testsuite\076");\n
\n
        }\n
\n
        return output.join("");\n
\n
    }\n
});\n
/*global CSSLint*/\n
CSSLint.addFormatter({\n
    //format information\n
    id: "lint-xml",\n
    name: "Lint XML format",\n
\n
    /**\n
     * Return opening root XML tag.\n
     * @return {String} to prepend before all results\n
     */\n
    startFormat: function(){\n
        return "\074?xml version=\\"1.0\\" encoding=\\"utf-8\\"?\076\074lint\076";\n
    },\n
\n
    /**\n
     * Return closing root XML tag.\n
     * @return {String} to append after all results\n
     */\n
    endFormat: function(){\n
        return "\074/lint\076";\n
    },\n
\n
    /**\n
     * Given CSS Lint results for a file, return output for this format.\n
     * @param results {Object} with error and warning messages\n
     * @param filename {String} relative file path\n
     * @param options {Object} (UNUSED for now) specifies special handling of output\n
     * @return {String} output for results\n
     */\n
    formatResults: function(results, filename, options) {\n
        var messages = results.messages,\n
            output = [];\n
\n
        /**\n
         * Replace special characters before write to output.\n
         *\n
         * Rules:\n
         *  - single quotes is the escape sequence for double-quotes\n
         *  - \046amp; is the escape sequence for \046\n
         *  - \046lt; is the escape sequence for \074\n
         *  - \046gt; is the escape sequence for \076\n
         *\n
         * @param {String} message to escape\n
         * @return escaped message as {String}\n
         */\n
        var escapeSpecialCharacters = function(str) {\n
            if (!str || str.constructor !== String) {\n
                return "";\n
            }\n
            return str.replace(/\\"/g, "\'").replace(/\046/g, "\046amp;").replace(/\074/g, "\046lt;").replace(/\076/g, "\046gt;");\n
        };\n
\n
        if (messages.length \076 0) {\n
\n
            output.push("\074file name=\\""+filename+"\\"\076");\n
            CSSLint.Util.forEach(messages, function (message, i) {\n
                if (message.rollup) {\n
                    output.push("\074issue severity=\\"" + message.type + "\\" reason=\\"" + escapeSpecialCharacters(message.message) + "\\" evidence=\\"" + escapeSpecialCharacters(message.evidence) + "\\"/\076");\n
                } else {\n
                    output.push("\074issue line=\\"" + message.line + "\\" char=\\"" + message.col + "\\" severity=\\"" + message.type + "\\"" +\n
                        " reason=\\"" + escapeSpecialCharacters(message.message) + "\\" evidence=\\"" + escapeSpecialCharacters(message.evidence) + "\\"/\076");\n
                }\n
            });\n
            output.push("\074/file\076");\n
        }\n
\n
        return output.join("");\n
    }\n
});\n
/*global CSSLint*/\n
CSSLint.addFormatter({\n
    //format information\n
    id: "text",\n
    name: "Plain Text",\n
\n
    /**\n
     * Return content to be printed before all file results.\n
     * @return {String} to prepend before all results\n
     */\n
    startFormat: function() {\n
        return "";\n
    },\n
\n
    /**\n
     * Return content to be printed after all file results.\n
     * @return {String} to append after all results\n
     */\n
    endFormat: function() {\n
        return "";\n
    },\n
\n
    /**\n
     * Given CSS Lint results for a file, return output for this format.\n
     * @param results {Object} with error and warning messages\n
     * @param filename {String} relative file path\n
     * @param options {Object} (Optional) specifies special handling of output\n
     * @return {String} output for results\n
     */\n
    formatResults: function(results, filename, options) {\n
        var messages = results.messages,\n
            output = "";\n
        options = options || {};\n
\n
        if (messages.length === 0) {\n
            return options.quiet ? "" : "\\n\\ncsslint: No errors in " + filename + ".";\n
        }\n
\n
        output = "\\n\\ncsslint: There are " + messages.length  +  " problems in " + filename + ".";\n
        var pos = filename.lastIndexOf("/"),\n
            shortFilename = filename;\n
\n
        if (pos === -1){\n
            pos = filename.lastIndexOf("\\\\");\n
        }\n
        if (pos \076 -1){\n
            shortFilename = filename.substring(pos+1);\n
        }\n
\n
        CSSLint.Util.forEach(messages, function (message, i) {\n
            output = output + "\\n\\n" + shortFilename;\n
            if (message.rollup) {\n
                output += "\\n" + (i+1) + ": " + message.type;\n
                output += "\\n" + message.message;\n
            } else {\n
                output += "\\n" + (i+1) + ": " + message.type + " at line " + message.line + ", col " + message.col;\n
                output += "\\n" + message.message;\n
                output += "\\n" + message.evidence;\n
            }\n
        });\n
\n
        return output;\n
    }\n
});\n
return CSSLint;\n
})();</string> </value>
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
