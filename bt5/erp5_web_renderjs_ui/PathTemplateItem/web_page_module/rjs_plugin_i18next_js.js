<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="Web Script" module="erp5.portal_type"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Access_contents_information_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Add_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Change_local_roles_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_Modify_portal_content_Permission</string> </key>
            <value>
              <tuple>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>_View_Permission</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>content_md5</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>default_reference</string> </key>
            <value> <string>i18next.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>rjs_plugin_i18next_js</string> </value>
        </item>
        <item>
            <key> <string>language</string> </key>
            <value> <string>en</string> </value>
        </item>
        <item>
            <key> <string>portal_type</string> </key>
            <value> <string>Web Script</string> </value>
        </item>
        <item>
            <key> <string>short_title</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>text_content</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// i18next, v1.7.4\n
// Copyright (c)2014 Jan Mühlemann (jamuhl).\n
// Distributed under MIT license\n
// http://i18next.com\n
(function() {\n
\n
    // add indexOf to non ECMA-262 standard compliant browsers\n
    if (!Array.prototype.indexOf) {\n
        Array.prototype.indexOf = function (searchElement /*, fromIndex */ ) {\n
            "use strict";\n
            if (this == null) {\n
                throw new TypeError();\n
            }\n
            var t = Object(this);\n
            var len = t.length >>> 0;\n
            if (len === 0) {\n
                return -1;\n
            }\n
            var n = 0;\n
            if (arguments.length > 0) {\n
                n = Number(arguments[1]);\n
                if (n != n) { // shortcut for verifying if it\'s NaN\n
                    n = 0;\n
                } else if (n != 0 && n != Infinity && n != -Infinity) {\n
                    n = (n > 0 || -1) * Math.floor(Math.abs(n));\n
                }\n
            }\n
            if (n >= len) {\n
                return -1;\n
            }\n
            var k = n >= 0 ? n : Math.max(len - Math.abs(n), 0);\n
            for (; k < len; k++) {\n
                if (k in t && t[k] === searchElement) {\n
                    return k;\n
                }\n
            }\n
            return -1;\n
        }\n
    }\n
    \n
    // add lastIndexOf to non ECMA-262 standard compliant browsers\n
    if (!Array.prototype.lastIndexOf) {\n
        Array.prototype.lastIndexOf = function(searchElement /*, fromIndex*/) {\n
            "use strict";\n
            if (this == null) {\n
                throw new TypeError();\n
            }\n
            var t = Object(this);\n
            var len = t.length >>> 0;\n
            if (len === 0) {\n
                return -1;\n
            }\n
            var n = len;\n
            if (arguments.length > 1) {\n
                n = Number(arguments[1]);\n
                if (n != n) {\n
                    n = 0;\n
                } else if (n != 0 && n != (1 / 0) && n != -(1 / 0)) {\n
                    n = (n > 0 || -1) * Math.floor(Math.abs(n));\n
                }\n
            }\n
            var k = n >= 0 ? Math.min(n, len - 1) : len - Math.abs(n);\n
            for (; k >= 0; k--) {\n
                if (k in t && t[k] === searchElement) {\n
                    return k;\n
                }\n
            }\n
            return -1;\n
        };\n
    }\n
    \n
    // Add string trim for IE8.\n
    if (typeof String.prototype.trim !== \'function\') {\n
        String.prototype.trim = function() {\n
            return this.replace(/^\\s+|\\s+$/g, \'\'); \n
        }\n
    }\n
\n
    var root = this\n
      , $ = root.jQuery || root.Zepto\n
      , i18n = {}\n
      , resStore = {}\n
      , currentLng\n
      , replacementCounter = 0\n
      , languages = []\n
      , initialized = false\n
      , sync = {};\n
\n
\n
\n
    // Export the i18next object for **CommonJS**. \n
    // If we\'re not in CommonJS, add `i18n` to the\n
    // global object or to jquery.\n
    if (typeof module !== \'undefined\' && module.exports) {\n
        if (!$) {\n
          try {\n
            $ = require(\'jquery\');\n
          } catch(e) {\n
            // just ignore\n
          }\n
        }\n
        if ($) {\n
            $.i18n = $.i18n || i18n;\n
        }\n
        module.exports = i18n;\n
    } else {\n
        if ($) {\n
            $.i18n = $.i18n || i18n;\n
        }\n
        \n
        root.i18n = root.i18n || i18n;\n
    }\n
    sync = {\n
    \n
        load: function(lngs, options, cb) {\n
            if (options.useLocalStorage) {\n
                sync._loadLocal(lngs, options, function(err, store) {\n
                    var missingLngs = [];\n
                    for (var i = 0, len = lngs.length; i < len; i++) {\n
                        if (!store[lngs[i]]) missingLngs.push(lngs[i]);\n
                    }\n
    \n
                    if (missingLngs.length > 0) {\n
                        sync._fetch(missingLngs, options, function(err, fetched) {\n
                            f.extend(store, fetched);\n
                            sync._storeLocal(fetched);\n
    \n
                            cb(null, store);\n
                        });\n
                    } else {\n
                        cb(null, store);\n
                    }\n
                });\n
            } else {\n
                sync._fetch(lngs, options, function(err, store){\n
                    cb(null, store);\n
                });\n
            }\n
        },\n
    \n
        _loadLocal: function(lngs, options, cb) {\n
            var store = {}\n
              , nowMS = new Date().getTime();\n
    \n
            if(window.localStorage) {\n
    \n
                var todo = lngs.length;\n
    \n
                f.each(lngs, function(key, lng) {\n
                    var local = window.localStorage.getItem(\'res_\' + lng);\n
    \n
                    if (local) {\n
                        local = JSON.parse(local);\n
    \n
                        if (local.i18nStamp && local.i18nStamp + options.localStorageExpirationTime > nowMS) {\n
                            store[lng] = local;\n
                        }\n
                    }\n
    \n
                    todo--; // wait for all done befor callback\n
                    if (todo === 0) cb(null, store);\n
                });\n
            }\n
        },\n
    \n
        _storeLocal: function(store) {\n
            if(window.localStorage) {\n
                for (var m in store) {\n
                    store[m].i18nStamp = new Date().getTime();\n
                    window.localStorage.setItem(\'res_\' + m, JSON.stringify(store[m]));\n
                }\n
            }\n
            return;\n
        },\n
    \n
        _fetch: function(lngs, options, cb) {\n
            var ns = options.ns\n
              , store = {};\n
            \n
            if (!options.dynamicLoad) {\n
                var todo = ns.namespaces.length * lngs.length\n
                  , errors;\n
    \n
                // load each file individual\n
                f.each(ns.namespaces, function(nsIndex, nsValue) {\n
                    f.each(lngs, function(lngIndex, lngValue) {\n
                        \n
                        // Call this once our translation has returned.\n
                        var loadComplete = function(err, data) {\n
                            if (err) {\n
                                errors = errors || [];\n
                                errors.push(err);\n
                            }\n
                            store[lngValue] = store[lngValue] || {};\n
                            store[lngValue][nsValue] = data;\n
    \n
                            todo--; // wait for all done befor callback\n
                            if (todo === 0) cb(errors, store);\n
                        };\n
                        \n
                        if(typeof options.customLoad == \'function\'){\n
                            // Use the specified custom callback.\n
                            options.customLoad(lngValue, nsValue, options, loadComplete);\n
                        } else {\n
                            //~ // Use our inbuilt sync.\n
                            sync._fetchOne(lngValue, nsValue, options, loadComplete);\n
                        }\n
                    });\n
                });\n
            } else {\n
                // Call this once our translation has returned.\n
                var loadComplete = function(err, data) {\n
                    cb(null, data);\n
                };\n
    \n
                if(typeof options.customLoad == \'function\'){\n
                    // Use the specified custom callback.\n
                    options.customLoad(lngs, ns.namespaces, options, loadComplete);\n
                } else {\n
                    var url = applyReplacement(options.resGetPath, { lng: lngs.join(\'+\'), ns: ns.namespaces.join(\'+\') });\n
                    // load all needed stuff once\n
                    f.ajax({\n
                        url: url,\n
                        success: function(data, status, xhr) {\n
                            f.log(\'loaded: \' + url);\n
                            loadComplete(null, data);\n
                        },\n
                        error : function(xhr, status, error) {\n
                            f.log(\'failed loading: \' + url);\n
                            loadComplete(\'failed loading resource.json error: \' + error);\n
                        },\n
                        dataType: "json",\n
                        async : options.getAsync\n
                    });\n
                }    \n
            }\n
        },\n
    \n
        _fetchOne: function(lng, ns, options, done) {\n
            var url = applyReplacement(options.resGetPath, { lng: lng, ns: ns });\n
            f.ajax({\n
                url: url,\n
                success: function(data, status, xhr) {\n
                    f.log(\'loaded: \' + url);\n
                    done(null, data);\n
                },\n
                error : function(xhr, status, error) {\n
                    if ((status && status == 200) || (xhr && xhr.status && xhr.status == 200)) {\n
                        // file loaded but invalid json, stop waste time !\n
                        f.error(\'There is a typo in: \' + url);\n
                    } else if ((status && status == 404) || (xhr && xhr.status && xhr.status == 404)) {\n
                        f.log(\'Does not exist: \' + url);\n
                    } else {\n
                        var theStatus = status ? status : ((xhr && xhr.status) ? xhr.status : null);\n
                        f.log(theStatus + \' when loading \' + url);\n
                    }\n
                    \n
                    done(error, {});\n
                },\n
                dataType: "json",\n
                async : options.getAsync\n
            });\n
        },\n
    \n
        postMissing: function(lng, ns, key, defaultValue, lngs) {\n
            var payload = {};\n
            payload[key] = defaultValue;\n
    \n
            var urls = [];\n
    \n
            if (o.sendMissingTo === \'fallback\' && o.fallbackLng[0] !== false) {\n
                for (var i = 0; i < o.fallbackLng.length; i++) {\n
                    urls.push({lng: o.fallbackLng[i], url: applyReplacement(o.resPostPath, { lng: o.fallbackLng[i], ns: ns })});\n
                }\n
            } else if (o.sendMissingTo === \'current\' || (o.sendMissingTo === \'fallback\' && o.fallbackLng[0] === false) ) {\n
                urls.push({lng: lng, url: applyReplacement(o.resPostPath, { lng: lng, ns: ns })});\n
            } else if (o.sendMissingTo === \'all\') {\n
                for (var i = 0, l = lngs.length; i < l; i++) {\n
                    urls.push({lng: lngs[i], url: applyReplacement(o.resPostPath, { lng: lngs[i], ns: ns })});\n
                }\n
            }\n
    \n
            for (var y = 0, len = urls.length; y < len; y++) {\n
                var item = urls[y];\n
                f.ajax({\n
                    url: item.url,\n
                    type: o.sendType,\n
                    data: payload,\n
                    success: function(data, status, xhr) {\n
                        f.log(\'posted missing key \\\'\' + key + \'\\\' to: \' + item.url);\n
    \n
                        // add key to resStore\n
                        var keys = key.split(\'.\');\n
                        var x = 0;\n
                        var value = resStore[item.lng][ns];\n
                        while (keys[x]) {\n
                            if (x === keys.length - 1) {\n
                                value = value[keys[x]] = defaultValue;\n
                            } else {\n
                                value = value[keys[x]] = value[keys[x]] || {};\n
                            }\n
                            x++;\n
                        }\n
                    },\n
                    error : function(xhr, status, error) {\n
                        f.log(\'failed posting missing key \\\'\' + key + \'\\\' to: \' + item.url);\n
                    },\n
                    dataType: "json",\n
                    async : o.postAsync\n
                });\n
            }\n
        }\n
    };\n
    // defaults\n
    var o = {\n
        lng: undefined,\n
        load: \'all\',\n
        preload: [],\n
        lowerCaseLng: false,\n
        returnObjectTrees: false,\n
        fallbackLng: [\'dev\'],\n
        fallbackNS: [],\n
        detectLngQS: \'setLng\',\n
        detectLngFromLocalStorage: false,\n
        ns: \'translation\',\n
        fallbackOnNull: true,\n
        fallbackOnEmpty: false,\n
        fallbackToDefaultNS: false,\n
        nsseparator: \':\',\n
        keyseparator: \'.\',\n
        selectorAttr: \'data-i18n\',\n
        debug: false,\n
        \n
        resGetPath: \'locales/__lng__/__ns__.json\',\n
        resPostPath: \'locales/add/__lng__/__ns__\',\n
    \n
        getAsync: true,\n
        postAsync: true,\n
    \n
        resStore: undefined,\n
        useLocalStorage: false,\n
        localStorageExpirationTime: 7*24*60*60*1000,\n
    \n
        dynamicLoad: false,\n
        sendMissing: false,\n
        sendMissingTo: \'fallback\', // current | all\n
        sendType: \'POST\',\n
    \n
        interpolationPrefix: \'__\',\n
        interpolationSuffix: \'__\',\n
        reusePrefix: \'$t(\',\n
        reuseSuffix: \')\',\n
        pluralSuffix: \'_plural\',\n
        pluralNotFound: [\'plural_not_found\', Math.random()].join(\'\'),\n
        contextNotFound: [\'context_not_found\', Math.random()].join(\'\'),\n
        escapeInterpolation: false,\n
        indefiniteSuffix: \'_indefinite\',\n
        indefiniteNotFound: [\'indefinite_not_found\', Math.random()].join(\'\'),\n
    \n
        setJqueryExt: true,\n
        defaultValueFromContent: true,\n
        useDataAttrOptions: false,\n
        cookieExpirationTime: undefined,\n
        useCookie: true,\n
        cookieName: \'i18next\',\n
        cookieDomain: undefined,\n
    \n
        objectTreeKeyHandler: undefined,\n
        postProcess: undefined,\n
        parseMissingKey: undefined,\n
        missingKeyHandler: sync.postMissing,\n
    \n
        shortcutFunction: \'sprintf\' // or: defaultValue\n
    };\n
    function _extend(target, source) {\n
        if (!source || typeof source === \'function\') {\n
            return target;\n
        }\n
    \n
        for (var attr in source) { target[attr] = source[attr]; }\n
        return target;\n
    }\n
    \n
    function _deepExtend(target, source) {\n
        for (var prop in source)\n
            if (prop in target)\n
                _deepExtend(target[prop], source[prop]);\n
            else\n
                target[prop] = source[prop];\n
        return target;\n
    }\n
    \n
    function _each(object, callback, args) {\n
        var name, i = 0,\n
            length = object.length,\n
            isObj = length === undefined || Object.prototype.toString.apply(object) !== \'[object Array]\' || typeof object === "function";\n
    \n
        if (args) {\n
            if (isObj) {\n
                for (name in object) {\n
                    if (callback.apply(object[name], args) === false) {\n
                        break;\n
                    }\n
                }\n
            } else {\n
                for ( ; i < length; ) {\n
                    if (callback.apply(object[i++], args) === false) {\n
                        break;\n
                    }\n
                }\n
            }\n
    \n
        // A special, fast, case for the most common use of each\n
        } else {\n
            if (isObj) {\n
                for (name in object) {\n
                    if (callback.call(object[name], name, object[name]) === false) {\n
                        break;\n
                    }\n
                }\n
            } else {\n
                for ( ; i < length; ) {\n
                    if (callback.call(object[i], i, object[i++]) === false) {\n
                        break;\n
                    }\n
                }\n
            }\n
        }\n
    \n
        return object;\n
    }\n
    \n
    var _entityMap = {\n
        "&": "&amp;",\n
        "<": "&lt;",\n
        ">": "&gt;",\n
        \'"\': \'&quot;\',\n
        "\'": \'&#39;\',\n
        "/": \'&#x2F;\'\n
    };\n
    \n
    function _escape(data) {\n
        if (typeof data === \'string\') {\n
            return data.replace(/[&<>"\'\\/]/g, function (s) {\n
                return _entityMap[s];\n
            });\n
        }else{\n
            return data;\n
        }\n
    }\n
    \n
    function _ajax(options) {\n
    \n
        // v0.5.0 of https://github.com/goloroden/http.js\n
        var getXhr = function (callback) {\n
            // Use the native XHR object if the browser supports it.\n
            if (window.XMLHttpRequest) {\n
                return callback(null, new XMLHttpRequest());\n
            } else if (window.ActiveXObject) {\n
                // In Internet Explorer check for ActiveX versions of the XHR object.\n
                try {\n
                    return callback(null, new ActiveXObject("Msxml2.XMLHTTP"));\n
                } catch (e) {\n
                    return callback(null, new ActiveXObject("Microsoft.XMLHTTP"));\n
                }\n
            }\n
    \n
            // If no XHR support was found, throw an error.\n
            return callback(new Error());\n
        };\n
    \n
        var encodeUsingUrlEncoding = function (data) {\n
            if(typeof data === \'string\') {\n
                return data;\n
            }\n
    \n
            var result = [];\n
            for(var dataItem in data) {\n
                if(data.hasOwnProperty(dataItem)) {\n
                    result.push(encodeURIComponent(dataItem) + \'=\' + encodeURIComponent(data[dataItem]));\n
                }\n
            }\n
    \n
            return result.join(\'&\');\n
        };\n
    \n
        var utf8 = function (text) {\n
            text = text.replace(/\\r\\n/g, \'\\n\');\n
            var result = \'\';\n
    \n
            for(var i = 0; i < text.length; i++) {\n
                var c = text.charCodeAt(i);\n
    \n
                if(c < 128) {\n
                        result += String.fromCharCode(c);\n
                } else if((c > 127) && (c < 2048)) {\n
                        result += String.fromCharCode((c >> 6) | 192);\n
                        result += String.fromCharCode((c & 63) | 128);\n
                } else {\n
                        result += String.fromCharCode((c >> 12) | 224);\n
                        result += String.fromCharCode(((c >> 6) & 63) | 128);\n
                        result += String.fromCharCode((c & 63) | 128);\n
                }\n
            }\n
    \n
            return result;\n
        };\n
    \n
        var base64 = function (text) {\n
            var keyStr = \'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\';\n
    \n
            text = utf8(text);\n
            var result = \'\',\n
                    chr1, chr2, chr3,\n
                    enc1, enc2, enc3, enc4,\n
                    i = 0;\n
    \n
            do {\n
                chr1 = text.charCodeAt(i++);\n
                chr2 = text.charCodeAt(i++);\n
                chr3 = text.charCodeAt(i++);\n
    \n
                enc1 = chr1 >> 2;\n
                enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);\n
                enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);\n
                enc4 = chr3 & 63;\n
    \n
                if(isNaN(chr2)) {\n
                    enc3 = enc4 = 64;\n
                } else if(isNaN(chr3)) {\n
                    enc4 = 64;\n
                }\n
    \n
                result +=\n
                    keyStr.charAt(enc1) +\n
                    keyStr.charAt(enc2) +\n
                    keyStr.charAt(enc3) +\n
                    keyStr.charAt(enc4);\n
                chr1 = chr2 = chr3 = \'\';\n
                enc1 = enc2 = enc3 = enc4 = \'\';\n
            } while(i < text.length);\n
    \n
            return result;\n
        };\n
    \n
        var mergeHeaders = function () {\n
            // Use the first header object as base.\n
            var result = arguments[0];\n
    \n
            // Iterate through the remaining header objects and add them.\n
            for(var i = 1; i < arguments.length; i++) {\n
                var currentHeaders = arguments[i];\n
                for(var header in currentHeaders) {\n
                    if(currentHeaders.hasOwnProperty(header)) {\n
                        result[header] = currentHeaders[header];\n
                    }\n
                }\n
            }\n
    \n
            // Return the merged headers.\n
            return result;\n
        };\n
    \n
        var ajax = function (method, url, options, callback) {\n
            // Adjust parameters.\n
            if(typeof options === \'function\') {\n
                callback = options;\n
                options = {};\n
            }\n
    \n
            // Set default parameter values.\n
            options.cache = options.cache || false;\n
            options.data = options.data || {};\n
            options.headers = options.headers || {};\n
            options.jsonp = options.jsonp || false;\n
            options.async = options.async === undefined ? true : options.async;\n
    \n
            // Merge the various header objects.\n
            var headers = mergeHeaders({\n
                \'accept\': \'*/*\',\n
                \'content-type\': \'application/x-www-form-urlencoded;charset=UTF-8\'\n
            }, ajax.headers, options.headers);\n
    \n
            // Encode the data according to the content-type.\n
            var payload;\n
            if (headers[\'content-type\'] === \'application/json\') {\n
                payload = JSON.stringify(options.data);\n
            } else {\n
                payload = encodeUsingUrlEncoding(options.data);\n
            }\n
    \n
            // Specially prepare GET requests: Setup the query string, handle caching and make a JSONP call\n
            // if neccessary.\n
            if(method === \'GET\') {\n
                // Setup the query string.\n
                var queryString = [];\n
                if(payload) {\n
                    queryString.push(payload);\n
                    payload = null;\n
                }\n
    \n
                // Handle caching.\n
                if(!options.cache) {\n
                    queryString.push(\'_=\' + (new Date()).getTime());\n
                }\n
    \n
                // If neccessary prepare the query string for a JSONP call.\n
                if(options.jsonp) {\n
                    queryString.push(\'callback=\' + options.jsonp);\n
                    queryString.push(\'jsonp=\' + options.jsonp);\n
                }\n
    \n
                // Merge the query string and attach it to the url.\n
                queryString = queryString.join(\'&\');\n
                if (queryString.length > 1) {\n
                    if (url.indexOf(\'?\') > -1) {\n
                        url += \'&\' + queryString;\n
                    } else {\n
                        url += \'?\' + queryString;\n
                    }\n
                }\n
    \n
                // Make a JSONP call if neccessary.\n
                if(options.jsonp) {\n
                    var head = document.getElementsByTagName(\'head\')[0];\n
                    var script = document.createElement(\'script\');\n
                    script.type = \'text/javascript\';\n
                    script.src = url;\n
                    head.appendChild(script);\n
                    return;\n
                }\n
            }\n
    \n
            // Since we got here, it is no JSONP request, so make a normal XHR request.\n
            getXhr(function (err, xhr) {\n
                if(err) return callback(err);\n
    \n
                // Open the request.\n
                xhr.open(method, url, options.async);\n
    \n
                // Set the request headers.\n
                for(var header in headers) {\n
                    if(headers.hasOwnProperty(header)) {\n
                        xhr.setRequestHeader(header, headers[header]);\n
                    }\n
                }\n
    \n
                // Handle the request events.\n
                xhr.onreadystatechange = function () {\n
                    if(xhr.readyState === 4) {\n
                        var data = xhr.responseText || \'\';\n
    \n
                        // If no callback is given, return.\n
                        if(!callback) {\n
                            return;\n
                        }\n
    \n
                        // Return an object that provides access to the data as text and JSON.\n
                        callback(xhr.status, {\n
                            text: function () {\n
                                return data;\n
                            },\n
    \n
                            json: function () {\n
                                return JSON.parse(data);\n
                            }\n
                        });\n
                    }\n
                };\n
    \n
                // Actually send the XHR request.\n
                xhr.send(payload);\n
            });\n
        };\n
    \n
        // Define the external interface.\n
        var http = {\n
            authBasic: function (username, password) {\n
                ajax.headers[\'Authorization\'] = \'Basic \' + base64(username + \':\' + password);\n
            },\n
    \n
            connect: function (url, options, callback) {\n
                return ajax(\'CONNECT\', url, options, callback);\n
            },\n
    \n
            del: function (url, options, callback) {\n
                return ajax(\'DELETE\', url, options, callback);\n
            },\n
    \n
            get: function (url, options, callback) {\n
                return ajax(\'GET\', url, options, callback);\n
            },\n
    \n
            head: function (url, options, callback) {\n
                return ajax(\'HEAD\', url, options, callback);\n
            },\n
    \n
            headers: function (headers) {\n
                ajax.headers = headers || {};\n
            },\n
    \n
            isAllowed: function (url, verb, callback) {\n
                this.options(url, function (status, data) {\n
                    callback(data.text().indexOf(verb) !== -1);\n
                });\n
            },\n
    \n
            options: function (url, options, callback) {\n
                return ajax(\'OPTIONS\', url, options, callback);\n
            },\n
    \n
            patch: function (url, options, callback) {\n
                return ajax(\'PATCH\', url, options, callback);\n
            },\n
    \n
            post: function (url, options, callback) {\n
                return ajax(\'POST\', url, options, callback);\n
            },\n
    \n
            put: function (url, options, callback) {\n
                return ajax(\'PUT\', url, options, callback);\n
            },\n
    \n
            trace: function (url, options, callback) {\n
                return ajax(\'TRACE\', url, options, callback);\n
            }\n
        };\n
    \n
    \n
        var methode = options.type ? options.type.toLowerCase() : \'get\';\n
    \n
        http[methode](options.url, options, function (status, data) {\n
            // file: protocol always gives status code 0, so check for data\n
            if (status === 200 || (status === 0 && data.text())) {\n
                options.success(data.json(), status, null);\n
            } else {\n
                options.error(data.text(), status, null);\n
            }\n
        });\n
    }\n
    \n
    var _cookie = {\n
        create: function(name,value,minutes,domain) {\n
            var expires;\n
            if (minutes) {\n
                var date = new Date();\n
                date.setTime(date.getTime()+(minutes*60*1000));\n
                expires = "; expires="+date.toGMTString();\n
            }\n
            else expires = "";\n
            domain = (domain)? "domain="+domain+";" : "";\n
            document.cookie = name+"="+value+expires+";"+domain+"path=/";\n
        },\n
    \n
        read: function(name) {\n
            var nameEQ = name + "=";\n
            var ca = document.cookie.split(\';\');\n
            for(var i=0;i < ca.length;i++) {\n
                var c = ca[i];\n
                while (c.charAt(0)==\' \') c = c.substring(1,c.length);\n
                if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length,c.length);\n
            }\n
            return null;\n
        },\n
    \n
        remove: function(name) {\n
            this.create(name,"",-1);\n
        }\n
    };\n
    \n
    var cookie_noop = {\n
        create: function(name,value,minutes,domain) {},\n
        read: function(name) { return null; },\n
        remove: function(name) {}\n
    };\n
    \n
    \n
    \n
    // move dependent functions to a container so that\n
    // they can be overriden easier in no jquery environment (node.js)\n
    var f = {\n
        extend: $ ? $.extend : _extend,\n
        deepExtend: _deepExtend,\n
        each: $ ? $.each : _each,\n
        ajax: $ ? $.ajax : (typeof document !== \'undefined\' ? _ajax : function() {}),\n
        cookie: typeof document !== \'undefined\' ? _cookie : cookie_noop,\n
        detectLanguage: detectLanguage,\n
        escape: _escape,\n
        log: function(str) {\n
            if (o.debug && typeof console !== "undefined") console.log(str);\n
        },\n
        error: function(str) {\n
            if (typeof console !== "undefined") console.error(str);\n
        },\n
        getCountyIndexOfLng: function(lng) {\n
            var lng_index = 0;\n
            if (lng === \'nb-NO\' || lng === \'nn-NO\') lng_index = 1;\n
            return lng_index;\n
        },\n
        toLanguages: function(lng) {\n
            var log = this.log;\n
    \n
            var languages = [];\n
            var whitelist = o.lngWhitelist || false;\n
            var addLanguage = function(language){\n
              //reject langs not whitelisted\n
              if(!whitelist || whitelist.indexOf(language) > -1){\n
                languages.push(language);\n
              }else{\n
                log(\'rejecting non-whitelisted language: \' + language);\n
              }\n
            };\n
            if (typeof lng === \'string\' && lng.indexOf(\'-\') > -1) {\n
                var parts = lng.split(\'-\');\n
    \n
                lng = o.lowerCaseLng ?\n
                    parts[0].toLowerCase() +  \'-\' + parts[1].toLowerCase() :\n
                    parts[0].toLowerCase() +  \'-\' + parts[1].toUpperCase();\n
    \n
                if (o.load !== \'unspecific\') addLanguage(lng);\n
                if (o.load !== \'current\') addLanguage(parts[this.getCountyIndexOfLng(lng)]);\n
            } else {\n
                addLanguage(lng);\n
            }\n
    \n
            for (var i = 0; i < o.fallbackLng.length; i++) {\n
                if (languages.indexOf(o.fallbackLng[i]) === -1 && o.fallbackLng[i]) languages.push(o.fallbackLng[i]);\n
            }\n
            return languages;\n
        },\n
        regexEscape: function(str) {\n
            return str.replace(/[\\-\\[\\]\\/\\{\\}\\(\\)\\*\\+\\?\\.\\\\\\^\\$\\|]/g, "\\\\$&");\n
        },\n
        regexReplacementEscape: function(strOrFn) {\n
            if (typeof strOrFn === \'string\') {\n
                return strOrFn.replace(/\\$/g, "$$$$");\n
            } else {\n
                return strOrFn;\n
            }\n
        }\n
    };\n
    function init(options, cb) {\n
        \n
        if (typeof options === \'function\') {\n
            cb = options;\n
            options = {};\n
        }\n
        options = options || {};\n
        \n
        // override defaults with passed in options\n
        f.extend(o, options);\n
        delete o.fixLng; /* passed in each time */\n
    \n
        // create namespace object if namespace is passed in as string\n
        if (typeof o.ns == \'string\') {\n
            o.ns = { namespaces: [o.ns], defaultNs: o.ns};\n
        }\n
    \n
        // fallback namespaces\n
        if (typeof o.fallbackNS == \'string\') {\n
            o.fallbackNS = [o.fallbackNS];\n
        }\n
    \n
        // fallback languages\n
        if (typeof o.fallbackLng == \'string\' || typeof o.fallbackLng == \'boolean\') {\n
            o.fallbackLng = [o.fallbackLng];\n
        }\n
    \n
        // escape prefix/suffix\n
        o.interpolationPrefixEscaped = f.regexEscape(o.interpolationPrefix);\n
        o.interpolationSuffixEscaped = f.regexEscape(o.interpolationSuffix);\n
    \n
        if (!o.lng) o.lng = f.detectLanguage();\n
    \n
        languages = f.toLanguages(o.lng);\n
        currentLng = languages[0];\n
        f.log(\'currentLng set to: \' + currentLng);\n
    \n
        if (o.useCookie && f.cookie.read(o.cookieName) !== currentLng){ //cookie is unset or invalid\n
            f.cookie.create(o.cookieName, currentLng, o.cookieExpirationTime, o.cookieDomain);\n
        }\n
        if (o.detectLngFromLocalStorage && typeof document !== \'undefined\' && window.localstorage) {\n
            window.localStorage.setItem(\'i18next_lng\', currentLng);\n
        }\n
    \n
        var lngTranslate = translate;\n
        if (options.fixLng) {\n
            lngTranslate = function(key, options) {\n
                options = options || {};\n
                options.lng = options.lng || lngTranslate.lng;\n
                return translate(key, options);\n
            };\n
            lngTranslate.lng = currentLng;\n
        }\n
    \n
        pluralExtensions.setCurrentLng(currentLng);\n
    \n
        // add JQuery extensions\n
        if ($ && o.setJqueryExt) addJqueryFunct();\n
    \n
        // jQuery deferred\n
        var deferred;\n
        if ($ && $.Deferred) {\n
            deferred = $.Deferred();\n
        }\n
    \n
        // return immidiatly if res are passed in\n
        if (o.resStore) {\n
            resStore = o.resStore;\n
            initialized = true;\n
            if (cb) cb(lngTranslate);\n
            if (deferred) deferred.resolve(lngTranslate);\n
            if (deferred) return deferred.promise();\n
            return;\n
        }\n
    \n
        // languages to load\n
        var lngsToLoad = f.toLanguages(o.lng);\n
        if (typeof o.preload === \'string\') o.preload = [o.preload];\n
        for (var i = 0, l = o.preload.length; i < l; i++) {\n
            var pres = f.toLanguages(o.preload[i]);\n
            for (var y = 0, len = pres.length; y < len; y++) {\n
                if (lngsToLoad.indexOf(pres[y]) < 0) {\n
                    lngsToLoad.push(pres[y]);\n
                }\n
            }\n
        }\n
    \n
        // else load them\n
        i18n.sync.load(lngsToLoad, o, function(err, store) {\n
            resStore = store;\n
            initialized = true;\n
    \n
            if (cb) cb(lngTranslate);\n
            if (deferred) deferred.resolve(lngTranslate);\n
        });\n
    \n
        if (deferred) return deferred.promise();\n
    }\n
    function preload(lngs, cb) {\n
        if (typeof lngs === \'string\') lngs = [lngs];\n
        for (var i = 0, l = lngs.length; i < l; i++) {\n
            if (o.preload.indexOf(lngs[i]) < 0) {\n
                o.preload.push(lngs[i]);\n
            }\n
        }\n
        return init(cb);\n
    }\n
    \n
    function addResourceBundle(lng, ns, resources, deep) {\n
        if (typeof ns !== \'string\') {\n
            resources = ns;\n
            ns = o.ns.defaultNs;\n
        } else if (o.ns.namespaces.indexOf(ns) < 0) {\n
            o.ns.namespaces.push(ns);\n
        }\n
    \n
        resStore[lng] = resStore[lng] || {};\n
        resStore[lng][ns] = resStore[lng][ns] || {};\n
    \n
        if (deep) {\n
            f.deepExtend(resStore[lng][ns], resources);\n
        } else {\n
            f.extend(resStore[lng][ns], resources);\n
        }\n
    }\n
    \n
    function removeResourceBundle(lng, ns) {\n
        if (typeof ns !== \'string\') {\n
            ns = o.ns.defaultNs;\n
        }\n
    \n
        resStore[lng] = resStore[lng] || {};\n
        resStore[lng][ns] = {};\n
    }\n
    \n
    function addResource(lng, ns, key, value) {\n
        if (typeof ns !== \'string\') {\n
            resource = ns;\n
            ns = o.ns.defaultNs;\n
        } else if (o.ns.namespaces.indexOf(ns) < 0) {\n
            o.ns.namespaces.push(ns);\n
        }\n
    \n
        resStore[lng] = resStore[lng] || {};\n
        resStore[lng][ns] = resStore[lng][ns] || {};\n
    \n
        var keys = key.split(o.keyseparator);\n
        var x = 0;\n
        var node = resStore[o.lng][ns];\n
        var origRef = node;\n
    \n
        while (keys[x]) {\n
            if (x == keys.length - 1)\n
                node[keys[x]] = value;\n
            else {\n
                if (node[keys[x]] == null)\n
                    node[keys[x]] = {};\n
    \n
                node = node[keys[x]];\n
            }\n
            x++;\n
        }\n
    }\n
    \n
    function addResources(lng, ns, resources) {\n
        if (typeof ns !== \'string\') {\n
            resource = ns;\n
            ns = o.ns.defaultNs;\n
        } else if (o.ns.namespaces.indexOf(ns) < 0) {\n
            o.ns.namespaces.push(ns);\n
        }\n
    \n
        for (var m in resources) {\n
            if (typeof resources[m] === \'string\') addResource(lng, ns, m, resources[m]);\n
        }\n
    }\n
    \n
    function setDefaultNamespace(ns) {\n
        o.ns.defaultNs = ns;\n
    }\n
    \n
    function loadNamespace(namespace, cb) {\n
        loadNamespaces([namespace], cb);\n
    }\n
    \n
    function loadNamespaces(namespaces, cb) {\n
        var opts = {\n
            dynamicLoad: o.dynamicLoad,\n
            resGetPath: o.resGetPath,\n
            getAsync: o.getAsync,\n
            customLoad: o.customLoad,\n
            ns: { namespaces: namespaces, defaultNs: \'\'} /* new namespaces to load */\n
        };\n
    \n
        // languages to load\n
        var lngsToLoad = f.toLanguages(o.lng);\n
        if (typeof o.preload === \'string\') o.preload = [o.preload];\n
        for (var i = 0, l = o.preload.length; i < l; i++) {\n
            var pres = f.toLanguages(o.preload[i]);\n
            for (var y = 0, len = pres.length; y < len; y++) {\n
                if (lngsToLoad.indexOf(pres[y]) < 0) {\n
                    lngsToLoad.push(pres[y]);\n
                }\n
            }\n
        }\n
    \n
        // check if we have to load\n
        var lngNeedLoad = [];\n
        for (var a = 0, lenA = lngsToLoad.length; a < lenA; a++) {\n
            var needLoad = false;\n
            var resSet = resStore[lngsToLoad[a]];\n
            if (resSet) {\n
                for (var b = 0, lenB = namespaces.length; b < lenB; b++) {\n
                    if (!resSet[namespaces[b]]) needLoad = true;\n
                }\n
            } else {\n
                needLoad = true;\n
            }\n
    \n
            if (needLoad) lngNeedLoad.push(lngsToLoad[a]);\n
        }\n
    \n
        if (lngNeedLoad.length) {\n
            i18n.sync._fetch(lngNeedLoad, opts, function(err, store) {\n
                var todo = namespaces.length * lngNeedLoad.length;\n
    \n
                // load each file individual\n
                f.each(namespaces, function(nsIndex, nsValue) {\n
    \n
                    // append namespace to namespace array\n
                    if (o.ns.namespaces.indexOf(nsValue) < 0) {\n
                        o.ns.namespaces.push(nsValue);\n
                    }\n
    \n
                    f.each(lngNeedLoad, function(lngIndex, lngValue) {\n
                        resStore[lngValue] = resStore[lngValue] || {};\n
                        resStore[lngValue][nsValue] = store[lngValue][nsValue];\n
    \n
                        todo--; // wait for all done befor callback\n
                        if (todo === 0 && cb) {\n
                            if (o.useLocalStorage) i18n.sync._storeLocal(resStore);\n
                            cb();\n
                        }\n
                    });\n
                });\n
            });\n
        } else {\n
            if (cb) cb();\n
        }\n
    }\n
    \n
    function setLng(lng, options, cb) {\n
        if (typeof options === \'function\') {\n
            cb = options;\n
            options = {};\n
        } else if (!options) {\n
            options = {};\n
        }\n
    \n
        options.lng = lng;\n
        return init(options, cb);\n
    }\n
    \n
    function lng() {\n
        return currentLng;\n
    }\n
    function addJqueryFunct() {\n
        // $.t shortcut\n
        $.t = $.t || translate;\n
    \n
        function parse(ele, key, options) {\n
            if (key.length === 0) return;\n
    \n
            var attr = \'text\';\n
    \n
            if (key.indexOf(\'[\') === 0) {\n
                var parts = key.split(\']\');\n
                key = parts[1];\n
                attr = parts[0].substr(1, parts[0].length-1);\n
            }\n
    \n
            if (key.indexOf(\';\') === key.length-1) {\n
                key = key.substr(0, key.length-2);\n
            }\n
    \n
            var optionsToUse;\n
            if (attr === \'html\') {\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.html() }, options) : options;\n
                ele.html($.t(key, optionsToUse));\n
            } else if (attr === \'text\') {\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.text() }, options) : options;\n
                ele.text($.t(key, optionsToUse));\n
            } else if (attr === \'prepend\') {\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.html() }, options) : options;\n
                ele.prepend($.t(key, optionsToUse));\n
            } else if (attr === \'append\') {\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.html() }, options) : options;\n
                ele.append($.t(key, optionsToUse));\n
            } else if (attr.indexOf("data-") === 0) {\n
                var dataAttr = attr.substr(("data-").length);\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.data(dataAttr) }, options) : options;\n
                var translated = $.t(key, optionsToUse);\n
                //we change into the data cache\n
                ele.data(dataAttr, translated);\n
                //we change into the dom\n
                ele.attr(attr, translated);\n
            } else {\n
                optionsToUse = o.defaultValueFromContent ? $.extend({ defaultValue: ele.attr(attr) }, options) : options;\n
                ele.attr(attr, $.t(key, optionsToUse));\n
            }\n
        }\n
    \n
        function localize(ele, options) {\n
            var key = ele.attr(o.selectorAttr);\n
            if (!key && typeof key !== \'undefined\' && key !== false) key = ele.text() || ele.val();\n
            if (!key) return;\n
    \n
            var target = ele\n
              , targetSelector = ele.data("i18n-target");\n
            if (targetSelector) {\n
                target = ele.find(targetSelector) || ele;\n
            }\n
    \n
            if (!options && o.useDataAttrOptions === true) {\n
                options = ele.data("i18n-options");\n
            }\n
            options = options || {};\n
    \n
            if (key.indexOf(\';\') >= 0) {\n
                var keys = key.split(\';\');\n
    \n
                $.each(keys, function(m, k) {\n
                    if (k !== \'\') parse(target, k, options);\n
                });\n
    \n
            } else {\n
                parse(target, key, options);\n
            }\n
    \n
            if (o.useDataAttrOptions === true) ele.data("i18n-options", options);\n
        }\n
    \n
        // fn\n
        $.fn.i18n = function (options) {\n
            return this.each(function() {\n
                // localize element itself\n
                localize($(this), options);\n
    \n
                // localize childs\n
                var elements =  $(this).find(\'[\' + o.selectorAttr + \']\');\n
                elements.each(function() { \n
                    localize($(this), options);\n
                });\n
            });\n
        };\n
    }\n
    function applyReplacement(str, replacementHash, nestedKey, options) {\n
        if (!str) return str;\n
    \n
        options = options || replacementHash; // first call uses replacement hash combined with options\n
        if (str.indexOf(options.interpolationPrefix || o.interpolationPrefix) < 0) return str;\n
    \n
        var prefix = options.interpolationPrefix ? f.regexEscape(options.interpolationPrefix) : o.interpolationPrefixEscaped\n
          , suffix = options.interpolationSuffix ? f.regexEscape(options.interpolationSuffix) : o.interpolationSuffixEscaped\n
          , unEscapingSuffix = \'HTML\'+suffix;\n
    \n
        var hash = replacementHash.replace && typeof replacementHash.replace === \'object\' ? replacementHash.replace : replacementHash;\n
        f.each(hash, function(key, value) {\n
            var nextKey = nestedKey ? nestedKey + o.keyseparator + key : key;\n
            if (typeof value === \'object\' && value !== null) {\n
                str = applyReplacement(str, value, nextKey, options);\n
            } else {\n
                if (options.escapeInterpolation || o.escapeInterpolation) {\n
                    str = str.replace(new RegExp([prefix, nextKey, unEscapingSuffix].join(\'\'), \'g\'), f.regexReplacementEscape(value));\n
                    str = str.replace(new RegExp([prefix, nextKey, suffix].join(\'\'), \'g\'), f.regexReplacementEscape(f.escape(value)));\n
                } else {\n
                    str = str.replace(new RegExp([prefix, nextKey, suffix].join(\'\'), \'g\'), f.regexReplacementEscape(value));\n
                }\n
                // str = options.escapeInterpolation;\n
            }\n
        });\n
        return str;\n
    }\n
    \n
    // append it to functions\n
    f.applyReplacement = applyReplacement;\n
    \n
    function applyReuse(translated, options) {\n
        var comma = \',\';\n
        var options_open = \'{\';\n
        var options_close = \'}\';\n
    \n
        var opts = f.extend({}, options);\n
        delete opts.postProcess;\n
    \n
        while (translated.indexOf(o.reusePrefix) != -1) {\n
            replacementCounter++;\n
            if (replacementCounter > o.maxRecursion) { break; } // safety net for too much recursion\n
            var index_of_opening = translated.lastIndexOf(o.reusePrefix);\n
            var index_of_end_of_closing = translated.indexOf(o.reuseSuffix, index_of_opening) + o.reuseSuffix.length;\n
            var token = translated.substring(index_of_opening, index_of_end_of_closing);\n
            var token_without_symbols = token.replace(o.reusePrefix, \'\').replace(o.reuseSuffix, \'\');\n
    \n
            if (index_of_end_of_closing <= index_of_opening) {\n
                f.error(\'there is an missing closing in following translation value\', translated);\n
                return \'\';\n
            }\n
    \n
            if (token_without_symbols.indexOf(comma) != -1) {\n
                var index_of_token_end_of_closing = token_without_symbols.indexOf(comma);\n
                if (token_without_symbols.indexOf(options_open, index_of_token_end_of_closing) != -1 && token_without_symbols.indexOf(options_close, index_of_token_end_of_closing) != -1) {\n
                    var index_of_opts_opening = token_without_symbols.indexOf(options_open, index_of_token_end_of_closing);\n
                    var index_of_opts_end_of_closing = token_without_symbols.indexOf(options_close, index_of_opts_opening) + options_close.length;\n
                    try {\n
                        opts = f.extend(opts, JSON.parse(token_without_symbols.substring(index_of_opts_opening, index_of_opts_end_of_closing)));\n
                        token_without_symbols = token_without_symbols.substring(0, index_of_token_end_of_closing);\n
                    } catch (e) {\n
                    }\n
                }\n
            }\n
    \n
            var translated_token = _translate(token_without_symbols, opts);\n
            translated = translated.replace(token, f.regexReplacementEscape(translated_token));\n
        }\n
        return translated;\n
    }\n
    \n
    function hasContext(options) {\n
        return (options.context && (typeof options.context == \'string\' || typeof options.context == \'number\'));\n
    }\n
    \n
    function needsPlural(options, lng) {\n
        return (options.count !== undefined && typeof options.count != \'string\' && pluralExtensions.needsPlural(lng, options.count));\n
    }\n
    \n
    function needsIndefiniteArticle(options) {\n
        return (options.indefinite_article !== undefined && typeof options.indefinite_article != \'string\' && options.indefinite_article);\n
    }\n
    \n
    function exists(key, options) {\n
        options = options || {};\n
    \n
        var notFound = _getDefaultValue(key, options)\n
            , found = _find(key, options);\n
    \n
        return found !== undefined || found === notFound;\n
    }\n
    \n
    function translate(key, options) {\n
        options = options || {};\n
    \n
        if (!initialized) {\n
            f.log(\'i18next not finished initialization. you might have called t function before loading resources finished.\')\n
            return options.defaultValue || \'\';\n
        };\n
        replacementCounter = 0;\n
        return _translate.apply(null, arguments);\n
    }\n
    \n
    function _getDefaultValue(key, options) {\n
        return (options.defaultValue !== undefined) ? options.defaultValue : key;\n
    }\n
    \n
    function _injectSprintfProcessor() {\n
    \n
        var values = [];\n
    \n
        // mh: build array from second argument onwards\n
        for (var i = 1; i < arguments.length; i++) {\n
            values.push(arguments[i]);\n
        }\n
    \n
        return {\n
            postProcess: \'sprintf\',\n
            sprintf:     values\n
        };\n
    }\n
    \n
    function _translate(potentialKeys, options) {\n
        if (options && typeof options !== \'object\') {\n
            if (o.shortcutFunction === \'sprintf\') {\n
                // mh: gettext like sprintf syntax found, automatically create sprintf processor\n
                options = _injectSprintfProcessor.apply(null, arguments);\n
            } else if (o.shortcutFunction === \'defaultValue\') {\n
                options = {\n
                    defaultValue: options\n
                }\n
            }\n
        } else {\n
            options = options || {};\n
        }\n
    \n
        if (potentialKeys === undefined || potentialKeys === null || potentialKeys === \'\') return \'\';\n
    \n
        if (typeof potentialKeys == \'string\') {\n
            potentialKeys = [potentialKeys];\n
        }\n
    \n
        var key = potentialKeys[0];\n
    \n
        if (potentialKeys.length > 1) {\n
            for (var i = 0; i < potentialKeys.length; i++) {\n
                key = potentialKeys[i];\n
                if (exists(key, options)) {\n
                    break;\n
                }\n
            }\n
        }\n
    \n
        var notFound = _getDefaultValue(key, options)\n
            , found = _find(key, options)\n
            , lngs = options.lng ? f.toLanguages(options.lng, options.fallbackLng) : languages\n
            , ns = options.ns || o.ns.defaultNs\n
            , parts;\n
    \n
        // split ns and key\n
        if (key.indexOf(o.nsseparator) > -1) {\n
            parts = key.split(o.nsseparator);\n
            ns = parts[0];\n
            key = parts[1];\n
        }\n
    \n
        if (found === undefined && o.sendMissing && typeof o.missingKeyHandler === \'function\') {\n
            if (options.lng) {\n
                o.missingKeyHandler(lngs[0], ns, key, notFound, lngs);\n
            } else {\n
                o.missingKeyHandler(o.lng, ns, key, notFound, lngs);\n
            }\n
        }\n
    \n
        var postProcessor = options.postProcess || o.postProcess;\n
        if (found !== undefined && postProcessor) {\n
            if (postProcessors[postProcessor]) {\n
                found = postProcessors[postProcessor](found, key, options);\n
            }\n
        }\n
    \n
        // process notFound if function exists\n
        var splitNotFound = notFound;\n
        if (notFound.indexOf(o.nsseparator) > -1) {\n
            parts = notFound.split(o.nsseparator);\n
            splitNotFound = parts[1];\n
        }\n
        if (splitNotFound === key && o.parseMissingKey) {\n
            notFound = o.parseMissingKey(notFound);\n
        }\n
    \n
        if (found === undefined) {\n
            notFound = applyReplacement(notFound, options);\n
            notFound = applyReuse(notFound, options);\n
    \n
            if (postProcessor && postProcessors[postProcessor]) {\n
                var val = _getDefaultValue(key, options);\n
                found = postProcessors[postProcessor](val, key, options);\n
            }\n
        }\n
    \n
        return (found !== undefined) ? found : notFound;\n
    }\n
    \n
    function _find(key, options) {\n
        options = options || {};\n
    \n
        var optionWithoutCount, translated\n
            , notFound = _getDefaultValue(key, options)\n
            , lngs = languages;\n
    \n
        if (!resStore) { return notFound; } // no resStore to translate from\n
    \n
        // CI mode\n
        if (lngs[0].toLowerCase() === \'cimode\') return notFound;\n
    \n
        // passed in lng\n
        if (options.lng) {\n
            lngs = f.toLanguages(options.lng, options.fallbackLng);\n
    \n
            if (!resStore[lngs[0]]) {\n
                var oldAsync = o.getAsync;\n
                o.getAsync = false;\n
    \n
                i18n.sync.load(lngs, o, function(err, store) {\n
                    f.extend(resStore, store);\n
                    o.getAsync = oldAsync;\n
                });\n
            }\n
        }\n
    \n
        var ns = options.ns || o.ns.defaultNs;\n
        if (key.indexOf(o.nsseparator) > -1) {\n
            var parts = key.split(o.nsseparator);\n
            ns = parts[0];\n
            key = parts[1];\n
        }\n
    \n
        if (hasContext(options)) {\n
            optionWithoutCount = f.extend({}, options);\n
            delete optionWithoutCount.context;\n
            optionWithoutCount.defaultValue = o.contextNotFound;\n
    \n
            var contextKey = ns + o.nsseparator + key + \'_\' + options.context;\n
    \n
            translated = translate(contextKey, optionWithoutCount);\n
            if (translated != o.contextNotFound) {\n
                return applyReplacement(translated, { context: options.context }); // apply replacement for context only\n
            } // else continue translation with original/nonContext key\n
        }\n
    \n
        if (needsPlural(options, lngs[0])) {\n
            optionWithoutCount = f.extend({}, options);\n
            delete optionWithoutCount.count;\n
            optionWithoutCount.defaultValue = o.pluralNotFound;\n
    \n
            var pluralKey = ns + o.nsseparator + key + o.pluralSuffix;\n
            var pluralExtension = pluralExtensions.get(lngs[0], options.count);\n
            if (pluralExtension >= 0) {\n
                pluralKey = pluralKey + \'_\' + pluralExtension;\n
            } else if (pluralExtension === 1) {\n
                pluralKey = ns + o.nsseparator + key; // singular\n
            }\n
    \n
            translated = translate(pluralKey, optionWithoutCount);\n
            if (translated != o.pluralNotFound) {\n
                return applyReplacement(translated, {\n
                    count: options.count,\n
                    interpolationPrefix: options.interpolationPrefix,\n
                    interpolationSuffix: options.interpolationSuffix\n
                }); // apply replacement for count only\n
            } // else continue translation with original/singular key\n
        }\n
    \n
        if (needsIndefiniteArticle(options)) {\n
            var optionsWithoutIndef = f.extend({}, options);\n
            delete optionsWithoutIndef.indefinite_article;\n
            optionsWithoutIndef.defaultValue = o.indefiniteNotFound;\n
            // If we don\'t have a count, we want the indefinite, if we do have a count, and needsPlural is false\n
            var indefiniteKey = ns + o.nsseparator + key + (((options.count && !needsPlural(options, lngs[0])) || !options.count) ? o.indefiniteSuffix : "");\n
            translated = translate(indefiniteKey, optionsWithoutIndef);\n
            if (translated != o.indefiniteNotFound) {\n
                return translated;\n
            }\n
        }\n
    \n
        var found;\n
        var keys = key.split(o.keyseparator);\n
        for (var i = 0, len = lngs.length; i < len; i++ ) {\n
            if (found !== undefined) break;\n
    \n
            var l = lngs[i];\n
    \n
            var x = 0;\n
            var value = resStore[l] && resStore[l][ns];\n
            while (keys[x]) {\n
                value = value && value[keys[x]];\n
                x++;\n
            }\n
            if (value !== undefined) {\n
                var valueType = Object.prototype.toString.apply(value);\n
                if (typeof value === \'string\') {\n
                    value = applyReplacement(value, options);\n
                    value = applyReuse(value, options);\n
                } else if (valueType === \'[object Array]\' && !o.returnObjectTrees && !options.returnObjectTrees) {\n
                    value = value.join(\'\\n\');\n
                    value = applyReplacement(value, options);\n
                    value = applyReuse(value, options);\n
                } else if (value === null && o.fallbackOnNull === true) {\n
                    value = undefined;\n
                } else if (value !== null) {\n
                    if (!o.returnObjectTrees && !options.returnObjectTrees) {\n
                        if (o.objectTreeKeyHandler && typeof o.objectTreeKeyHandler == \'function\') {\n
                            value = o.objectTreeKeyHandler(key, value, l, ns, options);\n
                        } else {\n
                            value = \'key \\\'\' + ns + \':\' + key + \' (\' + l + \')\\\' \' +\n
                                \'returned an object instead of string.\';\n
                            f.log(value);\n
                        }\n
                    } else if (valueType !== \'[object Number]\' && valueType !== \'[object Function]\' && valueType !== \'[object RegExp]\') {\n
                        var copy = (valueType === \'[object Array]\') ? [] : {}; // apply child translation on a copy\n
                        f.each(value, function(m) {\n
                            copy[m] = _translate(ns + o.nsseparator + key + o.keyseparator + m, options);\n
                        });\n
                        value = copy;\n
                    }\n
                }\n
    \n
                if (typeof value === \'string\' && value.trim() === \'\' && o.fallbackOnEmpty === true)\n
                    value = undefined;\n
    \n
                found = value;\n
            }\n
        }\n
    \n
        if (found === undefined && !options.isFallbackLookup && (o.fallbackToDefaultNS === true || (o.fallbackNS && o.fallbackNS.length > 0))) {\n
            // set flag for fallback lookup - avoid recursion\n
            options.isFallbackLookup = true;\n
    \n
            if (o.fallbackNS.length) {\n
    \n
                for (var y = 0, lenY = o.fallbackNS.length; y < lenY; y++) {\n
                    found = _find(o.fallbackNS[y] + o.nsseparator + key, options);\n
    \n
                    if (found) {\n
                        /* compare value without namespace */\n
                        var foundValue = found.indexOf(o.nsseparator) > -1 ? found.split(o.nsseparator)[1] : found\n
                          , notFoundValue = notFound.indexOf(o.nsseparator) > -1 ? notFound.split(o.nsseparator)[1] : notFound;\n
    \n
                        if (foundValue !== notFoundValue) break;\n
                    }\n
                }\n
            } else {\n
                found = _find(key, options); // fallback to default NS\n
            }\n
            options.isFallbackLookup = false;\n
        }\n
    \n
        return found;\n
    }\n
    function detectLanguage() {\n
        var detectedLng;\n
    \n
        // get from qs\n
        var qsParm = [];\n
        if (typeof window !== \'undefined\') {\n
            (function() {\n
                var query = window.location.search.substring(1);\n
                var parms = query.split(\'&\');\n
                for (var i=0; i<parms.length; i++) {\n
                    var pos = parms[i].indexOf(\'=\');\n
                    if (pos > 0) {\n
                        var key = parms[i].substring(0,pos);\n
                        var val = parms[i].substring(pos+1);\n
                        qsParm[key] = val;\n
                    }\n
                }\n
            })();\n
            if (qsParm[o.detectLngQS]) {\n
                detectedLng = qsParm[o.detectLngQS];\n
            }\n
        }\n
    \n
        // get from cookie\n
        if (!detectedLng && typeof document !== \'undefined\' && o.useCookie ) {\n
            var c = f.cookie.read(o.cookieName);\n
            if (c) detectedLng = c;\n
        }\n
    \n
        // get from localstorage\n
        if (!detectedLng && typeof document !== \'undefined\' && window.localstorage && o.detectLngFromLocalStorage) {\n
            detectedLng = window.localStorage.getItem(\'i18next_lng\');\n
        }\n
    \n
        // get from navigator\n
        if (!detectedLng && typeof navigator !== \'undefined\') {\n
            detectedLng = (navigator.language) ? navigator.language : navigator.userLanguage;\n
        }\n
    \n
        //fallback\n
        if(!detectedLng){\n
          detectedLng = o.fallbackLng[0];\n
        }\n
        \n
        return detectedLng;\n
    }\n
    // definition http://translate.sourceforge.net/wiki/l10n/pluralforms\n
    var pluralExtensions = {\n
    \n
        rules: {\n
            "ach": {\n
                "name": "Acholi", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "af": {\n
                "name": "Afrikaans", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ak": {\n
                "name": "Akan", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "am": {\n
                "name": "Amharic", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "an": {\n
                "name": "Aragonese", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ar": {\n
                "name": "Arabic", \n
                "numbers": [\n
                    0, \n
                    1, \n
                    2, \n
                    3, \n
                    11, \n
                    100\n
                ], \n
                "plurals": function(n) { return Number(n===0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5); }\n
            }, \n
            "arn": {\n
                "name": "Mapudungun", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "ast": {\n
                "name": "Asturian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ay": {\n
                "name": "Aymar\\u00e1", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "az": {\n
                "name": "Azerbaijani", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "be": {\n
                "name": "Belarusian", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "bg": {\n
                "name": "Bulgarian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "bn": {\n
                "name": "Bengali", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "bo": {\n
                "name": "Tibetan", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "br": {\n
                "name": "Breton", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "bs": {\n
                "name": "Bosnian", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "ca": {\n
                "name": "Catalan", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "cgg": {\n
                "name": "Chiga", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "cs": {\n
                "name": "Czech", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number((n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2); }\n
            }, \n
            "csb": {\n
                "name": "Kashubian", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "cy": {\n
                "name": "Welsh", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    3, \n
                    8\n
                ], \n
                "plurals": function(n) { return Number((n==1) ? 0 : (n==2) ? 1 : (n != 8 && n != 11) ? 2 : 3); }\n
            }, \n
            "da": {\n
                "name": "Danish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "de": {\n
                "name": "German", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "dz": {\n
                "name": "Dzongkha", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "el": {\n
                "name": "Greek", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "en": {\n
                "name": "English", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "eo": {\n
                "name": "Esperanto", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "es": {\n
                "name": "Spanish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "es_ar": {\n
                "name": "Argentinean Spanish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "et": {\n
                "name": "Estonian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "eu": {\n
                "name": "Basque", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "fa": {\n
                "name": "Persian", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "fi": {\n
                "name": "Finnish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "fil": {\n
                "name": "Filipino", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "fo": {\n
                "name": "Faroese", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "fr": {\n
                "name": "French", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n >= 2); }\n
            }, \n
            "fur": {\n
                "name": "Friulian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "fy": {\n
                "name": "Frisian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ga": {\n
                "name": "Irish", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    3,\n
                    7, \n
                    11\n
                ], \n
                "plurals": function(n) { return Number(n==1 ? 0 : n==2 ? 1 : n<7 ? 2 : n<11 ? 3 : 4) ;}\n
            }, \n
            "gd": {\n
                "name": "Scottish Gaelic", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    3,\n
                    20\n
                ], \n
                "plurals": function(n) { return Number((n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3); }\n
            }, \n
            "gl": {\n
                "name": "Galician", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "gu": {\n
                "name": "Gujarati", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "gun": {\n
                "name": "Gun", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "ha": {\n
                "name": "Hausa", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "he": {\n
                "name": "Hebrew", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "hi": {\n
                "name": "Hindi", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "hr": {\n
                "name": "Croatian", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "hu": {\n
                "name": "Hungarian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "hy": {\n
                "name": "Armenian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ia": {\n
                "name": "Interlingua", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "id": {\n
                "name": "Indonesian", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "is": {\n
                "name": "Icelandic", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n%10!=1 || n%100==11); }\n
            }, \n
            "it": {\n
                "name": "Italian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ja": {\n
                "name": "Japanese", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "jbo": {\n
                "name": "Lojban", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "jv": {\n
                "name": "Javanese", \n
                "numbers": [\n
                    0, \n
                    1\n
                ], \n
                "plurals": function(n) { return Number(n !== 0); }\n
            }, \n
            "ka": {\n
                "name": "Georgian", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "kk": {\n
                "name": "Kazakh", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "km": {\n
                "name": "Khmer", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "kn": {\n
                "name": "Kannada", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ko": {\n
                "name": "Korean", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "ku": {\n
                "name": "Kurdish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "kw": {\n
                "name": "Cornish", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    3,\n
                    4\n
                ], \n
                "plurals": function(n) { return Number((n==1) ? 0 : (n==2) ? 1 : (n == 3) ? 2 : 3); }\n
            }, \n
            "ky": {\n
                "name": "Kyrgyz", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "lb": {\n
                "name": "Letzeburgesch", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ln": {\n
                "name": "Lingala", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "lo": {\n
                "name": "Lao", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "lt": {\n
                "name": "Lithuanian", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    10\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "lv": {\n
                "name": "Latvian", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    0\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n !== 0 ? 1 : 2); }\n
            }, \n
            "mai": {\n
                "name": "Maithili", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "mfe": {\n
                "name": "Mauritian Creole", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "mg": {\n
                "name": "Malagasy", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "mi": {\n
                "name": "Maori", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "mk": {\n
                "name": "Macedonian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n==1 || n%10==1 ? 0 : 1); }\n
            }, \n
            "ml": {\n
                "name": "Malayalam", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "mn": {\n
                "name": "Mongolian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "mnk": {\n
                "name": "Mandinka", \n
                "numbers": [\n
                    0, \n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(0 ? 0 : n==1 ? 1 : 2); }\n
            }, \n
            "mr": {\n
                "name": "Marathi", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ms": {\n
                "name": "Malay", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "mt": {\n
                "name": "Maltese", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    11, \n
                    20\n
                ], \n
                "plurals": function(n) { return Number(n==1 ? 0 : n===0 || ( n%100>1 && n%100<11) ? 1 : (n%100>10 && n%100<20 ) ? 2 : 3); }\n
            }, \n
            "nah": {\n
                "name": "Nahuatl", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "nap": {\n
                "name": "Neapolitan", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "nb": {\n
                "name": "Norwegian Bokmal", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ne": {\n
                "name": "Nepali", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "nl": {\n
                "name": "Dutch", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "nn": {\n
                "name": "Norwegian Nynorsk", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "no": {\n
                "name": "Norwegian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "nso": {\n
                "name": "Northern Sotho", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "oc": {\n
                "name": "Occitan", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "or": {\n
                "name": "Oriya", \n
                "numbers": [\n
                    2, \n
                    1\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "pa": {\n
                "name": "Punjabi", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "pap": {\n
                "name": "Papiamento", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "pl": {\n
                "name": "Polish", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "pms": {\n
                "name": "Piemontese", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ps": {\n
                "name": "Pashto", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "pt": {\n
                "name": "Portuguese", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "pt_br": {\n
                "name": "Brazilian Portuguese", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "rm": {\n
                "name": "Romansh", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ro": {\n
                "name": "Romanian", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    20\n
                ], \n
                "plurals": function(n) { return Number(n==1 ? 0 : (n===0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2); }\n
            }, \n
            "ru": {\n
                "name": "Russian", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "sah": {\n
                "name": "Yakut", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "sco": {\n
                "name": "Scots", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "se": {\n
                "name": "Northern Sami", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "si": {\n
                "name": "Sinhala", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "sk": {\n
                "name": "Slovak", \n
                "numbers": [\n
                    1, \n
                    2, \n
                    5\n
                ], \n
                "plurals": function(n) { return Number((n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2); }\n
            }, \n
            "sl": {\n
                "name": "Slovenian", \n
                "numbers": [\n
                    5, \n
                    1, \n
                    2, \n
                    3\n
                ], \n
                "plurals": function(n) { return Number(n%100==1 ? 1 : n%100==2 ? 2 : n%100==3 || n%100==4 ? 3 : 0); }\n
            }, \n
            "so": {\n
                "name": "Somali", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "son": {\n
                "name": "Songhay", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "sq": {\n
                "name": "Albanian", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "sr": {\n
                "name": "Serbian", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "su": {\n
                "name": "Sundanese", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "sv": {\n
                "name": "Swedish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "sw": {\n
                "name": "Swahili", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "ta": {\n
                "name": "Tamil", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "te": {\n
                "name": "Telugu", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "tg": {\n
                "name": "Tajik", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "th": {\n
                "name": "Thai", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "ti": {\n
                "name": "Tigrinya", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "tk": {\n
                "name": "Turkmen", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "tr": {\n
                "name": "Turkish", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "tt": {\n
                "name": "Tatar", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "ug": {\n
                "name": "Uyghur", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "uk": {\n
                "name": "Ukrainian", \n
                "numbers": [\n
                    1, \n
                    2,\n
                    5\n
                ], \n
                "plurals": function(n) { return Number(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); }\n
            }, \n
            "ur": {\n
                "name": "Urdu", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "uz": {\n
                "name": "Uzbek", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "vi": {\n
                "name": "Vietnamese", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "wa": {\n
                "name": "Walloon", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n > 1); }\n
            }, \n
            "wo": {\n
                "name": "Wolof", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }, \n
            "yo": {\n
                "name": "Yoruba", \n
                "numbers": [\n
                    1, \n
                    2\n
                ], \n
                "plurals": function(n) { return Number(n != 1); }\n
            }, \n
            "zh": {\n
                "name": "Chinese", \n
                "numbers": [\n
                    1\n
                ], \n
                "plurals": function(n) { return 0; }\n
            }\n
        },\n
    \n
        // for demonstration only sl and ar is added but you can add your own pluralExtensions\n
        addRule: function(lng, obj) {\n
            pluralExtensions.rules[lng] = obj;    \n
        },\n
    \n
        setCurrentLng: function(lng) {\n
            if (!pluralExtensions.currentRule || pluralExtensions.currentRule.lng !== lng) {\n
                var parts = lng.split(\'-\');\n
    \n
                pluralExtensions.currentRule = {\n
                    lng: lng,\n
                    rule: pluralExtensions.rules[parts[0]]\n
                };\n
            }\n
        },\n
    \n
        needsPlural: function(lng, count) {\n
            var parts = lng.split(\'-\');\n
    \n
            var ext;\n
            if (pluralExtensions.currentRule && pluralExtensions.currentRule.lng === lng) {\n
                ext = pluralExtensions.currentRule.rule; \n
            } else {\n
                ext = pluralExtensions.rules[parts[f.getCountyIndexOfLng(lng)]];\n
            }\n
    \n
            if (ext && ext.numbers.length <= 1) {\n
                return false;\n
            } else {\n
                return this.get(lng, count) !== 1;\n
            }\n
        },\n
    \n
        get: function(lng, count) {\n
            var parts = lng.split(\'-\');\n
    \n
            function getResult(l, c) {\n
                var ext;\n
                if (pluralExtensions.currentRule && pluralExtensions.currentRule.lng === lng) {\n
                    ext = pluralExtensions.currentRule.rule; \n
                } else {\n
                    ext = pluralExtensions.rules[l];\n
                }\n
                if (ext) {\n
                    var i;\n
                    if (ext.noAbs) {\n
                        i = ext.plurals(c);\n
                    } else {\n
                        i = ext.plurals(Math.abs(c));\n
                    }\n
                    \n
                    var number = ext.numbers[i];\n
                    if (ext.numbers.length === 2 && ext.numbers[0] === 1) {\n
                        if (number === 2) { \n
                            number = -1; // regular plural\n
                        } else if (number === 1) {\n
                            number = 1; // singular\n
                        }\n
                    }//console.log(count + \'-\' + number);\n
                    return number;\n
                } else {\n
                    return c === 1 ? \'1\' : \'-1\';\n
                }\n
            }\n
                        \n
            return getResult(parts[f.getCountyIndexOfLng(lng)], count);\n
        }\n
    \n
    };\n
    var postProcessors = {};\n
    var addPostProcessor = function(name, fc) {\n
        postProcessors[name] = fc;\n
    };\n
    // sprintf support\n
    var sprintf = (function() {\n
        function get_type(variable) {\n
            return Object.prototype.toString.call(variable).slice(8, -1).toLowerCase();\n
        }\n
        function str_repeat(input, multiplier) {\n
            for (var output = []; multiplier > 0; output[--multiplier] = input) {/* do nothing */}\n
            return output.join(\'\');\n
        }\n
    \n
        var str_format = function() {\n
            if (!str_format.cache.hasOwnProperty(arguments[0])) {\n
                str_format.cache[arguments[0]] = str_format.parse(arguments[0]);\n
            }\n
            return str_format.format.call(null, str_format.cache[arguments[0]], arguments);\n
        };\n
    \n
        str_format.format = function(parse_tree, argv) {\n
            var cursor = 1, tree_length = parse_tree.length, node_type = \'\', arg, output = [], i, k, match, pad, pad_character, pad_length;\n
            for (i = 0; i < tree_length; i++) {\n
                node_type = get_type(parse_tree[i]);\n
                if (node_type === \'string\') {\n
                    output.push(parse_tree[i]);\n
                }\n
                else if (node_type === \'array\') {\n
                    match = parse_tree[i]; // convenience purposes only\n
                    if (match[2]) { // keyword argument\n
                        arg = argv[cursor];\n
                        for (k = 0; k < match[2].length; k++) {\n
                            if (!arg.hasOwnProperty(match[2][k])) {\n
                                throw(sprintf(\'[sprintf] property "%s" does not exist\', match[2][k]));\n
                            }\n
                            arg = arg[match[2][k]];\n
                        }\n
                    }\n
                    else if (match[1]) { // positional argument (explicit)\n
                        arg = argv[match[1]];\n
                    }\n
                    else { // positional argument (implicit)\n
                        arg = argv[cursor++];\n
                    }\n
    \n
                    if (/[^s]/.test(match[8]) && (get_type(arg) != \'number\')) {\n
                        throw(sprintf(\'[sprintf] expecting number but found %s\', get_type(arg)));\n
                    }\n
                    switch (match[8]) {\n
                        case \'b\': arg = arg.toString(2); break;\n
                        case \'c\': arg = String.fromCharCode(arg); break;\n
                        case \'d\': arg = parseInt(arg, 10); break;\n
                        case \'e\': arg = match[7] ? arg.toExponential(match[7]) : arg.toExponential(); break;\n
                        case \'f\': arg = match[7] ? parseFloat(arg).toFixed(match[7]) : parseFloat(arg); break;\n
                        case \'o\': arg = arg.toString(8); break;\n
                        case \'s\': arg = ((arg = String(arg)) && match[7] ? arg.substring(0, match[7]) : arg); break;\n
                        case \'u\': arg = Math.abs(arg); break;\n
                        case \'x\': arg = arg.toString(16); break;\n
                        case \'X\': arg = arg.toString(16).toUpperCase(); break;\n
                    }\n
                    arg = (/[def]/.test(match[8]) && match[3] && arg >= 0 ? \'+\'+ arg : arg);\n
                    pad_character = match[4] ? match[4] == \'0\' ? \'0\' : match[4].charAt(1) : \' \';\n
                    pad_length = match[6] - String(arg).length;\n
                    pad = match[6] ? str_repeat(pad_character, pad_length) : \'\';\n
                    output.push(match[5] ? arg + pad : pad + arg);\n
                }\n
            }\n
            return output.join(\'\');\n
        };\n
    \n
        str_format.cache = {};\n
    \n
        str_format.parse = function(fmt) {\n
            var _fmt = fmt, match = [], parse_tree = [], arg_names = 0;\n
            while (_fmt) {\n
                if ((match = /^[^\\x25]+/.exec(_fmt)) !== null) {\n
                    parse_tree.push(match[0]);\n
                }\n
                else if ((match = /^\\x25{2}/.exec(_fmt)) !== null) {\n
                    parse_tree.push(\'%\');\n
                }\n
                else if ((match = /^\\x25(?:([1-9]\\d*)\\$|\\(([^\\)]+)\\))?(\\+)?(0|\'[^$])?(-)?(\\d+)?(?:\\.(\\d+))?([b-fosuxX])/.exec(_fmt)) !== null) {\n
                    if (match[2]) {\n
                        arg_names |= 1;\n
                        var field_list = [], replacement_field = match[2], field_match = [];\n
                        if ((field_match = /^([a-z_][a-z_\\d]*)/i.exec(replacement_field)) !== null) {\n
                            field_list.push(field_match[1]);\n
                            while ((replacement_field = replacement_field.substring(field_match[0].length)) !== \'\') {\n
                                if ((field_match = /^\\.([a-z_][a-z_\\d]*)/i.exec(replacement_field)) !== null) {\n
                                    field_list.push(field_match[1]);\n
                                }\n
                                else if ((field_match = /^\\[(\\d+)\\]/.exec(replacement_field)) !== null) {\n
                                    field_list.push(field_match[1]);\n
                                }\n
                                else {\n
                                    throw(\'[sprintf] huh?\');\n
                                }\n
                            }\n
                        }\n
                        else {\n
                            throw(\'[sprintf] huh?\');\n
                        }\n
                        match[2] = field_list;\n
                    }\n
                    else {\n
                        arg_names |= 2;\n
                    }\n
                    if (arg_names === 3) {\n
                        throw(\'[sprintf] mixing positional and named placeholders is not (yet) supported\');\n
                    }\n
                    parse_tree.push(match);\n
                }\n
                else {\n
                    throw(\'[sprintf] huh?\');\n
                }\n
                _fmt = _fmt.substring(match[0].length);\n
            }\n
            return parse_tree;\n
        };\n
    \n
        return str_format;\n
    })();\n
    \n
    var vsprintf = function(fmt, argv) {\n
        argv.unshift(fmt);\n
        return sprintf.apply(null, argv);\n
    };\n
    \n
    addPostProcessor("sprintf", function(val, key, opts) {\n
        if (!opts.sprintf) return val;\n
    \n
        if (Object.prototype.toString.apply(opts.sprintf) === \'[object Array]\') {\n
            return vsprintf(val, opts.sprintf);\n
        } else if (typeof opts.sprintf === \'object\') {\n
            return sprintf(val, opts.sprintf);\n
        }\n
    \n
        return val;\n
    });\n
    // public api interface\n
    i18n.init = init;\n
    i18n.setLng = setLng;\n
    i18n.preload = preload;\n
    i18n.addResourceBundle = addResourceBundle;\n
    i18n.addResource = addResource;\n
    i18n.addResources = addResources;\n
    i18n.removeResourceBundle = removeResourceBundle;\n
    i18n.loadNamespace = loadNamespace;\n
    i18n.loadNamespaces = loadNamespaces;\n
    i18n.setDefaultNamespace = setDefaultNamespace;\n
    i18n.t = translate;\n
    i18n.translate = translate;\n
    i18n.exists = exists;\n
    i18n.detectLanguage = f.detectLanguage;\n
    i18n.pluralExtensions = pluralExtensions;\n
    i18n.sync = sync;\n
    i18n.functions = f;\n
    i18n.lng = lng;\n
    i18n.addPostProcessor = addPostProcessor;\n
    i18n.options = o;\n
\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>plugin i18next JS</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value> <string>1.7.4</string> </value>
        </item>
        <item>
            <key> <string>workflow_history</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="PersistentMapping" module="Persistence.mapping"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value>
              <dictionary>
                <item>
                    <key> <string>document_publication_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>edit_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
                    </value>
                </item>
                <item>
                    <key> <string>processing_status_workflow</string> </key>
                    <value>
                      <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
                    </value>
                </item>
              </dictionary>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>publish_alive</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>super_sven</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1418835142.27</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
            <item>
                <key> <string>validation_state</string> </key>
                <value> <string>published_alive</string> </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>edit</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>super_sven</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value>
                  <none/>
                </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>939.44304.41368.21111</string> </value>
            </item>
            <item>
                <key> <string>state</string> </key>
                <value> <string>current</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1418834941.27</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="WorkflowHistoryList" module="Products.ERP5Type.patches.WorkflowTool"/>
    </pickle>
    <pickle>
      <tuple>
        <none/>
        <list>
          <dictionary>
            <item>
                <key> <string>action</string> </key>
                <value> <string>detect_converted_file</string> </value>
            </item>
            <item>
                <key> <string>actor</string> </key>
                <value> <string>super_sven</string> </value>
            </item>
            <item>
                <key> <string>comment</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>error_message</string> </key>
                <value> <string></string> </value>
            </item>
            <item>
                <key> <string>external_processing_state</string> </key>
                <value> <string>converted</string> </value>
            </item>
            <item>
                <key> <string>serial</string> </key>
                <value> <string>0.0.0.0</string> </value>
            </item>
            <item>
                <key> <string>time</string> </key>
                <value>
                  <object>
                    <klass>
                      <global name="DateTime" module="DateTime.DateTime"/>
                    </klass>
                    <tuple>
                      <none/>
                    </tuple>
                    <state>
                      <tuple>
                        <float>1418834767.8</float>
                        <string>GMT</string>
                      </tuple>
                    </state>
                  </object>
                </value>
            </item>
          </dictionary>
        </list>
      </tuple>
    </pickle>
  </record>
</ZopeData>
