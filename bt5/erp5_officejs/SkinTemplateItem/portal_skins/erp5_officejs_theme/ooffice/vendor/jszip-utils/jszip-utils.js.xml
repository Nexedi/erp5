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
            <value> <string>ts44314536.13</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jszip-utils.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
\n
JSZipUtils - A collection of cross-browser utilities to go along with JSZip.\n
<http://stuk.github.io/jszip-utils>\n
\n
(c) 2014 Stuart Knightley, David Duponchel\n
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip-utils/master/LICENSE.markdown.\n
\n
*/\n
!function(e){"object"==typeof exports?module.exports=e():"function"==typeof define&&define.amd?define(e):"undefined"!=typeof window?window.JSZipUtils=e():"undefined"!=typeof global?global.JSZipUtils=e():"undefined"!=typeof self&&(self.JSZipUtils=e())}(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module \'"+o+"\'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){\n
\'use strict\';\n
\n
var JSZipUtils = {};\n
// just use the responseText with xhr1, response with xhr2.\n
// The transformation doesn\'t throw away high-order byte (with responseText)\n
// because JSZip handles that case. If not used with JSZip, you may need to\n
// do it, see https://developer.mozilla.org/En/Using_XMLHttpRequest#Handling_binary_data\n
JSZipUtils._getBinaryFromXHR = function (xhr) {\n
    // for xhr.responseText, the 0xFF mask is applied by JSZip\n
    return xhr.response || xhr.responseText;\n
};\n
\n
// taken from jQuery\n
function createStandardXHR() {\n
    try {\n
        return new window.XMLHttpRequest();\n
    } catch( e ) {}\n
}\n
\n
function createActiveXHR() {\n
    try {\n
        return new window.ActiveXObject("Microsoft.XMLHTTP");\n
    } catch( e ) {}\n
}\n
\n
// Create the request object\n
var createXHR = window.ActiveXObject ?\n
    /* Microsoft failed to properly\n
     * implement the XMLHttpRequest in IE7 (can\'t request local files),\n
     * so we use the ActiveXObject when it is available\n
     * Additionally XMLHttpRequest can be disabled in IE7/IE8 so\n
     * we need a fallback.\n
     */\n
    function() {\n
    return createStandardXHR() || createActiveXHR();\n
} :\n
    // For all other browsers, use the standard XMLHttpRequest object\n
    createStandardXHR;\n
\n
\n
\n
JSZipUtils.getBinaryContent = function(path, callback) {\n
    /*\n
     * Here is the tricky part : getting the data.\n
     * In firefox/chrome/opera/... setting the mimeType to \'text/plain; charset=x-user-defined\'\n
     * is enough, the result is in the standard xhr.responseText.\n
     * cf https://developer.mozilla.org/En/XMLHttpRequest/Using_XMLHttpRequest#Receiving_binary_data_in_older_browsers\n
     * In IE <= 9, we must use (the IE only) attribute responseBody\n
     * (for binary data, its content is different from responseText).\n
     * In IE 10, the \'charset=x-user-defined\' trick doesn\'t work, only the\n
     * responseType will work :\n
     * http://msdn.microsoft.com/en-us/library/ie/hh673569%28v=vs.85%29.aspx#Binary_Object_upload_and_download\n
     *\n
     * I\'d like to use jQuery to avoid this XHR madness, but it doesn\'t support\n
     * the responseType attribute : http://bugs.jquery.com/ticket/11461\n
     */\n
    try {\n
\n
        var xhr = createXHR();\n
\n
        xhr.open(\'GET\', path, true);\n
\n
        // recent browsers\n
        if ("responseType" in xhr) {\n
            xhr.responseType = "arraybuffer";\n
        }\n
\n
        // older browser\n
        if(xhr.overrideMimeType) {\n
            xhr.overrideMimeType("text/plain; charset=x-user-defined");\n
        }\n
\n
        xhr.onreadystatechange = function(evt) {\n
            var file, err;\n
            // use `xhr` and not `this`... thanks IE\n
            if (xhr.readyState === 4) {\n
                if (xhr.status === 200 || xhr.status === 0) {\n
                    file = null;\n
                    err = null;\n
                    try {\n
                        file = JSZipUtils._getBinaryFromXHR(xhr);\n
                    } catch(e) {\n
                        err = new Error(e);\n
                    }\n
                    callback(err, file);\n
                } else {\n
                    callback(new Error("Ajax error for " + path + " : " + this.status + " " + this.statusText), null);\n
                }\n
            }\n
        };\n
\n
        xhr.send();\n
\n
    } catch (e) {\n
        callback(new Error(e), null);\n
    }\n
};\n
\n
// export\n
module.exports = JSZipUtils;\n
\n
// enforcing Stuk\'s coding style\n
// vim: set shiftwidth=4 softtabstop=4:\n
\n
},{}]},{},[1])\n
(1)\n
});\n
;

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>4482</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
