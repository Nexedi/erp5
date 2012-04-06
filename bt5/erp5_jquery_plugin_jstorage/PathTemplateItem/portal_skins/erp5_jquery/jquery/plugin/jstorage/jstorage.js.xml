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
            <value> <string>ts30948097.92</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jstorage.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * ----------------------------- JSTORAGE -------------------------------------\n
 * Simple local storage wrapper to save data on the browser side, supporting\n
 * all major browsers - IE6+, Firefox2+, Safari4+, Chrome4+ and Opera 10.5+\n
 *\n
 * Copyright (c) 2010 Andris Reinman, andris.reinman@gmail.com\n
 * Project homepage: www.jstorage.info\n
 *\n
 * Licensed under MIT-style license:\n
 *\n
 * Permission is hereby granted, free of charge, to any person obtaining a copy\n
 * of this software and associated documentation files (the "Software"), to deal\n
 * in the Software without restriction, including without limitation the rights\n
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n
 * copies of the Software, and to permit persons to whom the Software is\n
 * furnished to do so, subject to the following conditions:\n
 *\n
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n
 * SOFTWARE.\n
 */\n
\n
/**\n
 * $.jStorage\n
 *\n
 * USAGE:\n
 *\n
 * jStorage requires Prototype, MooTools or jQuery! If jQuery is used, then\n
 * jQuery-JSON (http://code.google.com/p/jquery-json/) is also needed.\n
 * (jQuery-JSON needs to be loaded BEFORE jStorage!)\n
 *\n
 * Methods:\n
 *\n
 * -set(key, value)\n
 * $.jStorage.set(key, value) -> saves a value\n
 *\n
 * -get(key[, default])\n
 * value = $.jStorage.get(key [, default]) ->\n
 *    retrieves value if key exists, or default if it doesn\'t\n
 *\n
 * -deleteKey(key)\n
 * $.jStorage.deleteKey(key) -> removes a key from the storage\n
 *\n
 * -flush()\n
 * $.jStorage.flush() -> clears the cache\n
 *\n
 * -storageObj()\n
 * $.jStorage.storageObj() -> returns a read-ony copy of the actual storage\n
 *\n
 * -storageSize()\n
 * $.jStorage.storageSize() -> returns the size of the storage in bytes\n
 *\n
 * -index()\n
 * $.jStorage.index() -> returns the used keys as an array\n
 *\n
 * -storageAvailable()\n
 * $.jStorage.storageAvailable() -> returns true if storage is available\n
 *\n
 * -reInit()\n
 * $.jStorage.reInit() -> reloads the data from browser storage\n
 *\n
 * <value> can be any JSON-able value, including objects and arrays.\n
 *\n
 **/\n
\n
(function($){\n
    if(!$ || !($.toJSON || Object.toJSON || window.JSON)){\n
        throw new Error("jQuery, MooTools or Prototype needs to be loaded before jStorage!");\n
    }\n
\n
    var\n
        /* This is the object, that holds the cached values */\n
        _storage = {},\n
\n
        /* Actual browser storage (localStorage or globalStorage[\'domain\']) */\n
        _storage_service = {jStorage:"{}"},\n
\n
        /* DOM element for older IE versions, holds userData behavior */\n
        _storage_elm = null,\n
\n
        /* How much space does the storage take */\n
        _storage_size = 0,\n
\n
        /* function to encode objects to JSON strings */\n
        json_encode = $.toJSON || Object.toJSON || (window.JSON && (JSON.encode || JSON.stringify)),\n
\n
        /* function to decode objects from JSON strings */\n
        json_decode = $.evalJSON || (window.JSON && (JSON.decode || JSON.parse)) || function(str){\n
            return String(str).evalJSON();\n
        },\n
\n
        /* which backend is currently used */\n
        _backend = false,\n
\n
        /* Next check for TTL */\n
        _ttl_timeout,\n
\n
        /**\n
         * XML encoding and decoding as XML nodes can\'t be JSON\'ized\n
         * XML nodes are encoded and decoded if the node is the value to be saved\n
         * but not if it\'s as a property of another object\n
         * Eg. -\n
         *   $.jStorage.set("key", xmlNode);        // IS OK\n
         *   $.jStorage.set("key", {xml: xmlNode}); // NOT OK\n
         */\n
        _XMLService = {\n
\n
            /**\n
             * Validates a XML node to be XML\n
             * based on jQuery.isXML function\n
             */\n
            isXML: function(elm){\n
                var documentElement = (elm ? elm.ownerDocument || elm : 0).documentElement;\n
                return documentElement ? documentElement.nodeName !== "HTML" : false;\n
            },\n
\n
            /**\n
             * Encodes a XML node to string\n
             * based on http://www.mercurytide.co.uk/news/article/issues-when-working-ajax/\n
             */\n
            encode: function(xmlNode) {\n
                if(!this.isXML(xmlNode)){\n
                    return false;\n
                }\n
                try{ // Mozilla, Webkit, Opera\n
                    return new XMLSerializer().serializeToString(xmlNode);\n
                }catch(E1) {\n
                    try {  // IE\n
                        return xmlNode.xml;\n
                    }catch(E2){}\n
                }\n
                return false;\n
            },\n
\n
            /**\n
             * Decodes a XML node from string\n
             * loosely based on http://outwestmedia.com/jquery-plugins/xmldom/\n
             */\n
            decode: function(xmlString){\n
                var dom_parser = ("DOMParser" in window && (new DOMParser()).parseFromString) ||\n
                        (window.ActiveXObject && function(_xmlString) {\n
                    var xml_doc = new ActiveXObject(\'Microsoft.XMLDOM\');\n
                    xml_doc.async = \'false\';\n
                    xml_doc.loadXML(_xmlString);\n
                    return xml_doc;\n
                }),\n
                resultXML;\n
                if(!dom_parser){\n
                    return false;\n
                }\n
                resultXML = dom_parser.call("DOMParser" in window && (new DOMParser()) || window, xmlString, \'text/xml\');\n
                return this.isXML(resultXML)?resultXML:false;\n
            }\n
        };\n
\n
    ////////////////////////// PRIVATE METHODS ////////////////////////\n
\n
    /**\n
     * Initialization function. Detects if the browser supports DOM Storage\n
     * or userData behavior and behaves accordingly.\n
     * @returns undefined\n
     */\n
    function _init(){\n
        /* Check if browser supports localStorage */\n
        var localStorageReallyWorks = false;\n
        if("localStorage" in window){\n
            try {\n
                window.localStorage.setItem(\'_tmptest\', \'tmpval\');\n
                localStorageReallyWorks = true;\n
                window.localStorage.removeItem(\'_tmptest\');\n
            } catch(BogusQuotaExceededErrorOnIos5) {\n
                // Thanks be to iOS5 Private Browsing mode which throws\n
                // QUOTA_EXCEEDED_ERRROR DOM Exception 22.\n
            }\n
        }\n
        if(localStorageReallyWorks){\n
            try {\n
                if(window.localStorage) {\n
                    _storage_service = window.localStorage;\n
                    _backend = "localStorage";\n
                }\n
            } catch(E3) {/* Firefox fails when touching localStorage and cookies are disabled */}\n
        }\n
        /* Check if browser supports globalStorage */\n
        else if("globalStorage" in window){\n
            try {\n
                if(window.globalStorage) {\n
                    _storage_service = window.globalStorage[window.location.hostname];\n
                    _backend = "globalStorage";\n
                }\n
            } catch(E4) {/* Firefox fails when touching localStorage and cookies are disabled */}\n
        }\n
        /* Check if browser supports userData behavior */\n
        else {\n
            _storage_elm = document.createElement(\'link\');\n
            if(_storage_elm.addBehavior){\n
\n
                /* Use a DOM element to act as userData storage */\n
                _storage_elm.style.behavior = \'url(#default#userData)\';\n
\n
                /* userData element needs to be inserted into the DOM! */\n
                document.getElementsByTagName(\'head\')[0].appendChild(_storage_elm);\n
\n
                _storage_elm.load("jStorage");\n
                var data = "{}";\n
                try{\n
                    data = _storage_elm.getAttribute("jStorage");\n
                }catch(E5){}\n
                _storage_service.jStorage = data;\n
                _backend = "userDataBehavior";\n
            }else{\n
                _storage_elm = null;\n
                return;\n
            }\n
        }\n
\n
        _load_storage();\n
\n
        // remove dead keys\n
        _handleTTL();\n
    }\n
\n
    /**\n
     * Loads the data from the storage based on the supported mechanism\n
     * @returns undefined\n
     */\n
    function _load_storage(){\n
        /* if jStorage string is retrieved, then decode it */\n
        if(_storage_service.jStorage){\n
            try{\n
                _storage = json_decode(String(_storage_service.jStorage));\n
            }catch(E6){_storage_service.jStorage = "{}";}\n
        }else{\n
            _storage_service.jStorage = "{}";\n
        }\n
        _storage_size = _storage_service.jStorage?String(_storage_service.jStorage).length:0;\n
    }\n
\n
    /**\n
     * This functions provides the "save" mechanism to store the jStorage object\n
     * @returns undefined\n
     */\n
    function _save(){\n
        try{\n
            _storage_service.jStorage = json_encode(_storage);\n
            // If userData is used as the storage engine, additional\n
            if(_storage_elm) {\n
                _storage_elm.setAttribute("jStorage",_storage_service.jStorage);\n
                _storage_elm.save("jStorage");\n
            }\n
            _storage_size = _storage_service.jStorage?String(_storage_service.jStorage).length:0;\n
        }catch(E7){/* probably cache is full, nothing is saved this way*/}\n
    }\n
\n
    /**\n
     * Function checks if a key is set and is string or numberic\n
     */\n
    function _checkKey(key){\n
        if(!key || (typeof key != "string" && typeof key != "number")){\n
            throw new TypeError(\'Key name must be string or numeric\');\n
        }\n
        if(key == "__jstorage_meta"){\n
            throw new TypeError(\'Reserved key name\');\n
        }\n
        return true;\n
    }\n
\n
    /**\n
     * Removes expired keys\n
     */\n
    function _handleTTL(){\n
        var curtime, i, TTL, nextExpire = Infinity, changed = false;\n
\n
        clearTimeout(_ttl_timeout);\n
\n
        if(!_storage.__jstorage_meta || typeof _storage.__jstorage_meta.TTL != "object"){\n
            // nothing to do here\n
            return;\n
        }\n
\n
        curtime = +new Date();\n
        TTL = _storage.__jstorage_meta.TTL;\n
        for(i in TTL){\n
            if(TTL.hasOwnProperty(i)){\n
                if(TTL[i] <= curtime){\n
                    delete TTL[i];\n
                    delete _storage[i];\n
                    changed = true;\n
                }else if(TTL[i] < nextExpire){\n
                    nextExpire = TTL[i];\n
                }\n
            }\n
        }\n
\n
        // set next check\n
        if(nextExpire != Infinity){\n
            _ttl_timeout = setTimeout(_handleTTL, nextExpire - curtime);\n
        }\n
\n
        // save changes\n
        if(changed){\n
            _save();\n
        }\n
    }\n
\n
    ////////////////////////// PUBLIC INTERFACE /////////////////////////\n
\n
    $.jStorage = {\n
        /* Version number */\n
        version: "0.1.6.1",\n
\n
        /**\n
         * Sets a key\'s value.\n
         *\n
         * @param {String} key - Key to set. If this value is not set or not\n
         *              a string an exception is raised.\n
         * @param value - Value to set. This can be any value that is JSON\n
         *              compatible (Numbers, Strings, Objects etc.).\n
         * @returns the used value\n
         */\n
        set: function(key, value){\n
            _checkKey(key);\n
            if(_XMLService.isXML(value)){\n
                value = {_is_xml:true,xml:_XMLService.encode(value)};\n
            }else if(typeof value == "function"){\n
                value = null; // functions can\'t be saved!\n
            }else if(value && typeof value == "object"){\n
                // clone the object before saving to _storage tree\n
                value = json_decode(json_encode(value));\n
            }\n
            _storage[key] = value;\n
            _save();\n
            return value;\n
        },\n
\n
        /**\n
         * Looks up a key in cache\n
         *\n
         * @param {String} key - Key to look up.\n
         * @param {mixed} def - Default value to return, if key didn\'t exist.\n
         * @returns the key value, default value or <null>\n
         */\n
        get: function(key, def){\n
            _checkKey(key);\n
            if(key in _storage){\n
                if(_storage[key] && typeof _storage[key] == "object" &&\n
                        _storage[key]._is_xml &&\n
                            _storage[key]._is_xml){\n
                    return _XMLService.decode(_storage[key].xml);\n
                }else{\n
                    return _storage[key];\n
                }\n
            }\n
            return typeof(def) == \'undefined\' ? null : def;\n
        },\n
\n
        /**\n
         * Deletes a key from cache.\n
         *\n
         * @param {String} key - Key to delete.\n
         * @returns true if key existed or false if it didn\'t\n
         */\n
        deleteKey: function(key){\n
            _checkKey(key);\n
            if(key in _storage){\n
                delete _storage[key];\n
                // remove from TTL list\n
                if(_storage.__jstorage_meta &&\n
                  typeof _storage.__jstorage_meta.TTL == "object" &&\n
                  key in _storage.__jstorage_meta.TTL){\n
                    delete _storage.__jstorage_meta.TTL[key];\n
                }\n
                _save();\n
                return true;\n
            }\n
            return false;\n
        },\n
\n
        /**\n
         * Sets a TTL for a key, or remove it if ttl value is 0 or below\n
         *\n
         * @param {String} key - key to set the TTL for\n
         * @param {Number} ttl - TTL timeout in milliseconds\n
         * @returns true if key existed or false if it didn\'t\n
         */\n
        setTTL: function(key, ttl){\n
            var curtime = +new Date();\n
            _checkKey(key);\n
            ttl = Number(ttl) || 0;\n
            if(key in _storage){\n
\n
                if(!_storage.__jstorage_meta){\n
                    _storage.__jstorage_meta = {};\n
                }\n
                if(!_storage.__jstorage_meta.TTL){\n
                    _storage.__jstorage_meta.TTL = {};\n
                }\n
\n
                // Set TTL value for the key\n
                if(ttl>0){\n
                    _storage.__jstorage_meta.TTL[key] = curtime + ttl;\n
                }else{\n
                    delete _storage.__jstorage_meta.TTL[key];\n
                }\n
\n
                _save();\n
\n
                _handleTTL();\n
                return true;\n
            }\n
            return false;\n
        },\n
\n
        /**\n
         * Deletes everything in cache.\n
         *\n
         * @return true\n
         */\n
        flush: function(){\n
            _storage = {};\n
            _save();\n
            return true;\n
        },\n
\n
        /**\n
         * Returns a read-only copy of _storage\n
         *\n
         * @returns Object\n
        */\n
        storageObj: function(){\n
            function F() {}\n
            F.prototype = _storage;\n
            return new F();\n
        },\n
\n
        /**\n
         * Returns an index of all used keys as an array\n
         * [\'key1\', \'key2\',..\'keyN\']\n
         *\n
         * @returns Array\n
        */\n
        index: function(){\n
            var index = [], i;\n
            for(i in _storage){\n
                if(_storage.hasOwnProperty(i) && i != "__jstorage_meta"){\n
                    index.push(i);\n
                }\n
            }\n
            return index;\n
        },\n
\n
        /**\n
         * How much space in bytes does the storage take?\n
         *\n
         * @returns Number\n
         */\n
        storageSize: function(){\n
            return _storage_size;\n
        },\n
\n
        /**\n
         * Which backend is currently in use?\n
         *\n
         * @returns String\n
         */\n
        currentBackend: function(){\n
            return _backend;\n
        },\n
\n
        /**\n
         * Test if storage is available\n
         *\n
         * @returns Boolean\n
         */\n
        storageAvailable: function(){\n
            return !!_backend;\n
        },\n
\n
        /**\n
         * Reloads the data from browser storage\n
         *\n
         * @returns undefined\n
         */\n
        reInit: function(){\n
            var new_storage_elm, data;\n
            if(_storage_elm && _storage_elm.addBehavior){\n
                new_storage_elm = document.createElement(\'link\');\n
\n
                _storage_elm.parentNode.replaceChild(new_storage_elm, _storage_elm);\n
                _storage_elm = new_storage_elm;\n
\n
                /* Use a DOM element to act as userData storage */\n
                _storage_elm.style.behavior = \'url(#default#userData)\';\n
\n
                /* userData element needs to be inserted into the DOM! */\n
                document.getElementsByTagName(\'head\')[0].appendChild(_storage_elm);\n
\n
                _storage_elm.load("jStorage");\n
                data = "{}";\n
                try{\n
                    data = _storage_elm.getAttribute("jStorage");\n
                }catch(E5){}\n
                _storage_service.jStorage = data;\n
                _backend = "userDataBehavior";\n
            }\n
\n
            _load_storage();\n
        }\n
    };\n
\n
    // Initialize jStorage\n
    _init();\n
\n
})(window.jQuery || window.$);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>17169</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>jstorage.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
