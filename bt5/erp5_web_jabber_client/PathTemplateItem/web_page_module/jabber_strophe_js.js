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
            <value> <string>strophe.js</string> </value>
        </item>
        <item>
            <key> <string>description</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>jabber_strophe_js</string> </value>
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
            <value> <string>// This code was written by Tyler Akins and has been placed in the\n
// public domain.  It would be nice if you left this header intact.\n
// Base64 code from Tyler Akins -- http://rumkin.com\n
\n
var Base64 = (function () {\n
    var keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";\n
\n
    var obj = {\n
        /**\n
         * Encodes a string in base64\n
         * @param {String} input The string to encode in base64.\n
         */\n
        encode: function (input) {\n
            var output = "";\n
            var chr1, chr2, chr3;\n
            var enc1, enc2, enc3, enc4;\n
            var i = 0;\n
\n
            do {\n
                chr1 = input.charCodeAt(i++);\n
                chr2 = input.charCodeAt(i++);\n
                chr3 = input.charCodeAt(i++);\n
\n
                enc1 = chr1 \076\076 2;\n
                enc2 = ((chr1 \046 3) \074\074 4) | (chr2 \076\076 4);\n
                enc3 = ((chr2 \046 15) \074\074 2) | (chr3 \076\076 6);\n
                enc4 = chr3 \046 63;\n
\n
                if (isNaN(chr2)) {\n
                    enc3 = enc4 = 64;\n
                } else if (isNaN(chr3)) {\n
                    enc4 = 64;\n
                }\n
\n
                output = output + keyStr.charAt(enc1) + keyStr.charAt(enc2) +\n
                    keyStr.charAt(enc3) + keyStr.charAt(enc4);\n
            } while (i \074 input.length);\n
\n
            return output;\n
        },\n
\n
        /**\n
         * Decodes a base64 string.\n
         * @param {String} input The string to decode.\n
         */\n
        decode: function (input) {\n
            var output = "";\n
            var chr1, chr2, chr3;\n
            var enc1, enc2, enc3, enc4;\n
            var i = 0;\n
\n
            // remove all characters that are not A-Z, a-z, 0-9, +, /, or =\n
            input = input.replace(/[^A-Za-z0-9\\+\\/\\=]/g, "");\n
\n
            do {\n
                enc1 = keyStr.indexOf(input.charAt(i++));\n
                enc2 = keyStr.indexOf(input.charAt(i++));\n
                enc3 = keyStr.indexOf(input.charAt(i++));\n
                enc4 = keyStr.indexOf(input.charAt(i++));\n
\n
                chr1 = (enc1 \074\074 2) | (enc2 \076\076 4);\n
                chr2 = ((enc2 \046 15) \074\074 4) | (enc3 \076\076 2);\n
                chr3 = ((enc3 \046 3) \074\074 6) | enc4;\n
\n
                output = output + String.fromCharCode(chr1);\n
\n
                if (enc3 != 64) {\n
                    output = output + String.fromCharCode(chr2);\n
                }\n
                if (enc4 != 64) {\n
                    output = output + String.fromCharCode(chr3);\n
                }\n
            } while (i \074 input.length);\n
\n
            return output;\n
        }\n
    };\n
\n
    return obj;\n
})();\n
\n
/*\n
 * A JavaScript implementation of the Secure Hash Algorithm, SHA-1, as defined\n
 * in FIPS PUB 180-1\n
 * Version 2.1a Copyright Paul Johnston 2000 - 2002.\n
 * Other contributors: Greg Holt, Andrew Kepert, Ydnar, Lostinet\n
 * Distributed under the BSD License\n
 * See http://pajhome.org.uk/crypt/md5 for details.\n
 */\n
\n
/* Some functions and variables have been stripped for use with Strophe */\n
\n
/*\n
 * These are the functions you\'ll usually want to call\n
 * They take string arguments and return either hex or base-64 encoded strings\n
 */\n
function b64_sha1(s){return binb2b64(core_sha1(str2binb(s),s.length * 8));}\n
function str_sha1(s){return binb2str(core_sha1(str2binb(s),s.length * 8));}\n
function b64_hmac_sha1(key, data){ return binb2b64(core_hmac_sha1(key, data));}\n
function str_hmac_sha1(key, data){ return binb2str(core_hmac_sha1(key, data));}\n
\n
/*\n
 * Calculate the SHA-1 of an array of big-endian words, and a bit length\n
 */\n
function core_sha1(x, len)\n
{\n
  /* append padding */\n
  x[len \076\076 5] |= 0x80 \074\074 (24 - len % 32);\n
  x[((len + 64 \076\076 9) \074\074 4) + 15] = len;\n
\n
  var w = new Array(80);\n
  var a =  1732584193;\n
  var b = -271733879;\n
  var c = -1732584194;\n
  var d =  271733878;\n
  var e = -1009589776;\n
\n
  var i, j, t, olda, oldb, oldc, oldd, olde;\n
  for (i = 0; i \074 x.length; i += 16)\n
  {\n
    olda = a;\n
    oldb = b;\n
    oldc = c;\n
    oldd = d;\n
    olde = e;\n
\n
    for (j = 0; j \074 80; j++)\n
    {\n
      if (j \074 16) { w[j] = x[i + j]; }\n
      else { w[j] = rol(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16], 1); }\n
      t = safe_add(safe_add(rol(a, 5), sha1_ft(j, b, c, d)),\n
                       safe_add(safe_add(e, w[j]), sha1_kt(j)));\n
      e = d;\n
      d = c;\n
      c = rol(b, 30);\n
      b = a;\n
      a = t;\n
    }\n
\n
    a = safe_add(a, olda);\n
    b = safe_add(b, oldb);\n
    c = safe_add(c, oldc);\n
    d = safe_add(d, oldd);\n
    e = safe_add(e, olde);\n
  }\n
  return [a, b, c, d, e];\n
}\n
\n
/*\n
 * Perform the appropriate triplet combination function for the current\n
 * iteration\n
 */\n
function sha1_ft(t, b, c, d)\n
{\n
  if (t \074 20) { return (b \046 c) | ((~b) \046 d); }\n
  if (t \074 40) { return b ^ c ^ d; }\n
  if (t \074 60) { return (b \046 c) | (b \046 d) | (c \046 d); }\n
  return b ^ c ^ d;\n
}\n
\n
/*\n
 * Determine the appropriate additive constant for the current iteration\n
 */\n
function sha1_kt(t)\n
{\n
  return (t \074 20) ?  1518500249 : (t \074 40) ?  1859775393 :\n
         (t \074 60) ? -1894007588 : -899497514;\n
}\n
\n
/*\n
 * Calculate the HMAC-SHA1 of a key and some data\n
 */\n
function core_hmac_sha1(key, data)\n
{\n
  var bkey = str2binb(key);\n
  if (bkey.length \076 16) { bkey = core_sha1(bkey, key.length * 8); }\n
\n
  var ipad = new Array(16), opad = new Array(16);\n
  for (var i = 0; i \074 16; i++)\n
  {\n
    ipad[i] = bkey[i] ^ 0x36363636;\n
    opad[i] = bkey[i] ^ 0x5C5C5C5C;\n
  }\n
\n
  var hash = core_sha1(ipad.concat(str2binb(data)), 512 + data.length * 8);\n
  return core_sha1(opad.concat(hash), 512 + 160);\n
}\n
\n
/*\n
 * Add integers, wrapping at 2^32. This uses 16-bit operations internally\n
 * to work around bugs in some JS interpreters.\n
 */\n
function safe_add(x, y)\n
{\n
  var lsw = (x \046 0xFFFF) + (y \046 0xFFFF);\n
  var msw = (x \076\076 16) + (y \076\076 16) + (lsw \076\076 16);\n
  return (msw \074\074 16) | (lsw \046 0xFFFF);\n
}\n
\n
/*\n
 * Bitwise rotate a 32-bit number to the left.\n
 */\n
function rol(num, cnt)\n
{\n
  return (num \074\074 cnt) | (num \076\076\076 (32 - cnt));\n
}\n
\n
/*\n
 * Convert an 8-bit or 16-bit string to an array of big-endian words\n
 * In 8-bit function, characters \076255 have their hi-byte silently ignored.\n
 */\n
function str2binb(str)\n
{\n
  var bin = [];\n
  var mask = 255;\n
  for (var i = 0; i \074 str.length * 8; i += 8)\n
  {\n
    bin[i\076\0765] |= (str.charCodeAt(i / 8) \046 mask) \074\074 (24 - i%32);\n
  }\n
  return bin;\n
}\n
\n
/*\n
 * Convert an array of big-endian words to a string\n
 */\n
function binb2str(bin)\n
{\n
  var str = "";\n
  var mask = 255;\n
  for (var i = 0; i \074 bin.length * 32; i += 8)\n
  {\n
    str += String.fromCharCode((bin[i\076\0765] \076\076\076 (24 - i%32)) \046 mask);\n
  }\n
  return str;\n
}\n
\n
/*\n
 * Convert an array of big-endian words to a base-64 string\n
 */\n
function binb2b64(binarray)\n
{\n
  var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";\n
  var str = "";\n
  var triplet, j;\n
  for (var i = 0; i \074 binarray.length * 4; i += 3)\n
  {\n
    triplet = (((binarray[i   \076\076 2] \076\076 8 * (3 -  i   %4)) \046 0xFF) \074\074 16) |\n
              (((binarray[i+1 \076\076 2] \076\076 8 * (3 - (i+1)%4)) \046 0xFF) \074\074 8 ) |\n
               ((binarray[i+2 \076\076 2] \076\076 8 * (3 - (i+2)%4)) \046 0xFF);\n
    for (j = 0; j \074 4; j++)\n
    {\n
      if (i * 8 + j * 6 \076 binarray.length * 32) { str += "="; }\n
      else { str += tab.charAt((triplet \076\076 6*(3-j)) \046 0x3F); }\n
    }\n
  }\n
  return str;\n
}\n
\n
/*\n
 * A JavaScript implementation of the RSA Data Security, Inc. MD5 Message\n
 * Digest Algorithm, as defined in RFC 1321.\n
 * Version 2.1 Copyright (C) Paul Johnston 1999 - 2002.\n
 * Other contributors: Greg Holt, Andrew Kepert, Ydnar, Lostinet\n
 * Distributed under the BSD License\n
 * See http://pajhome.org.uk/crypt/md5 for more info.\n
 */\n
\n
/*\n
 * Everything that isn\'t used by Strophe has been stripped here!\n
 */\n
\n
var MD5 = (function () {\n
    /*\n
     * Add integers, wrapping at 2^32. This uses 16-bit operations internally\n
     * to work around bugs in some JS interpreters.\n
     */\n
    var safe_add = function (x, y) {\n
        var lsw = (x \046 0xFFFF) + (y \046 0xFFFF);\n
        var msw = (x \076\076 16) + (y \076\076 16) + (lsw \076\076 16);\n
        return (msw \074\074 16) | (lsw \046 0xFFFF);\n
    };\n
\n
    /*\n
     * Bitwise rotate a 32-bit number to the left.\n
     */\n
    var bit_rol = function (num, cnt) {\n
        return (num \074\074 cnt) | (num \076\076\076 (32 - cnt));\n
    };\n
\n
    /*\n
     * Convert a string to an array of little-endian words\n
     */\n
    var str2binl = function (str) {\n
        var bin = [];\n
        for(var i = 0; i \074 str.length * 8; i += 8)\n
        {\n
            bin[i\076\0765] |= (str.charCodeAt(i / 8) \046 255) \074\074 (i%32);\n
        }\n
        return bin;\n
    };\n
\n
    /*\n
     * Convert an array of little-endian words to a string\n
     */\n
    var binl2str = function (bin) {\n
        var str = "";\n
        for(var i = 0; i \074 bin.length * 32; i += 8)\n
        {\n
            str += String.fromCharCode((bin[i\076\0765] \076\076\076 (i % 32)) \046 255);\n
        }\n
        return str;\n
    };\n
\n
    /*\n
     * Convert an array of little-endian words to a hex string.\n
     */\n
    var binl2hex = function (binarray) {\n
        var hex_tab = "0123456789abcdef";\n
        var str = "";\n
        for(var i = 0; i \074 binarray.length * 4; i++)\n
        {\n
            str += hex_tab.charAt((binarray[i\076\0762] \076\076 ((i%4)*8+4)) \046 0xF) +\n
                hex_tab.charAt((binarray[i\076\0762] \076\076 ((i%4)*8  )) \046 0xF);\n
        }\n
        return str;\n
    };\n
\n
    /*\n
     * These functions implement the four basic operations the algorithm uses.\n
     */\n
    var md5_cmn = function (q, a, b, x, s, t) {\n
        return safe_add(bit_rol(safe_add(safe_add(a, q),safe_add(x, t)), s),b);\n
    };\n
\n
    var md5_ff = function (a, b, c, d, x, s, t) {\n
        return md5_cmn((b \046 c) | ((~b) \046 d), a, b, x, s, t);\n
    };\n
\n
    var md5_gg = function (a, b, c, d, x, s, t) {\n
        return md5_cmn((b \046 d) | (c \046 (~d)), a, b, x, s, t);\n
    };\n
\n
    var md5_hh = function (a, b, c, d, x, s, t) {\n
        return md5_cmn(b ^ c ^ d, a, b, x, s, t);\n
    };\n
\n
    var md5_ii = function (a, b, c, d, x, s, t) {\n
        return md5_cmn(c ^ (b | (~d)), a, b, x, s, t);\n
    };\n
\n
    /*\n
     * Calculate the MD5 of an array of little-endian words, and a bit length\n
     */\n
    var core_md5 = function (x, len) {\n
        /* append padding */\n
        x[len \076\076 5] |= 0x80 \074\074 ((len) % 32);\n
        x[(((len + 64) \076\076\076 9) \074\074 4) + 14] = len;\n
\n
        var a =  1732584193;\n
        var b = -271733879;\n
        var c = -1732584194;\n
        var d =  271733878;\n
\n
        var olda, oldb, oldc, oldd;\n
        for (var i = 0; i \074 x.length; i += 16)\n
        {\n
            olda = a;\n
            oldb = b;\n
            oldc = c;\n
            oldd = d;\n
\n
            a = md5_ff(a, b, c, d, x[i+ 0], 7 , -680876936);\n
            d = md5_ff(d, a, b, c, x[i+ 1], 12, -389564586);\n
            c = md5_ff(c, d, a, b, x[i+ 2], 17,  606105819);\n
            b = md5_ff(b, c, d, a, x[i+ 3], 22, -1044525330);\n
            a = md5_ff(a, b, c, d, x[i+ 4], 7 , -176418897);\n
            d = md5_ff(d, a, b, c, x[i+ 5], 12,  1200080426);\n
            c = md5_ff(c, d, a, b, x[i+ 6], 17, -1473231341);\n
            b = md5_ff(b, c, d, a, x[i+ 7], 22, -45705983);\n
            a = md5_ff(a, b, c, d, x[i+ 8], 7 ,  1770035416);\n
            d = md5_ff(d, a, b, c, x[i+ 9], 12, -1958414417);\n
            c = md5_ff(c, d, a, b, x[i+10], 17, -42063);\n
            b = md5_ff(b, c, d, a, x[i+11], 22, -1990404162);\n
            a = md5_ff(a, b, c, d, x[i+12], 7 ,  1804603682);\n
            d = md5_ff(d, a, b, c, x[i+13], 12, -40341101);\n
            c = md5_ff(c, d, a, b, x[i+14], 17, -1502002290);\n
            b = md5_ff(b, c, d, a, x[i+15], 22,  1236535329);\n
\n
            a = md5_gg(a, b, c, d, x[i+ 1], 5 , -165796510);\n
            d = md5_gg(d, a, b, c, x[i+ 6], 9 , -1069501632);\n
            c = md5_gg(c, d, a, b, x[i+11], 14,  643717713);\n
            b = md5_gg(b, c, d, a, x[i+ 0], 20, -373897302);\n
            a = md5_gg(a, b, c, d, x[i+ 5], 5 , -701558691);\n
            d = md5_gg(d, a, b, c, x[i+10], 9 ,  38016083);\n
            c = md5_gg(c, d, a, b, x[i+15], 14, -660478335);\n
            b = md5_gg(b, c, d, a, x[i+ 4], 20, -405537848);\n
            a = md5_gg(a, b, c, d, x[i+ 9], 5 ,  568446438);\n
            d = md5_gg(d, a, b, c, x[i+14], 9 , -1019803690);\n
            c = md5_gg(c, d, a, b, x[i+ 3], 14, -187363961);\n
            b = md5_gg(b, c, d, a, x[i+ 8], 20,  1163531501);\n
            a = md5_gg(a, b, c, d, x[i+13], 5 , -1444681467);\n
            d = md5_gg(d, a, b, c, x[i+ 2], 9 , -51403784);\n
            c = md5_gg(c, d, a, b, x[i+ 7], 14,  1735328473);\n
            b = md5_gg(b, c, d, a, x[i+12], 20, -1926607734);\n
\n
            a = md5_hh(a, b, c, d, x[i+ 5], 4 , -378558);\n
            d = md5_hh(d, a, b, c, x[i+ 8], 11, -2022574463);\n
            c = md5_hh(c, d, a, b, x[i+11], 16,  1839030562);\n
            b = md5_hh(b, c, d, a, x[i+14], 23, -35309556);\n
            a = md5_hh(a, b, c, d, x[i+ 1], 4 , -1530992060);\n
            d = md5_hh(d, a, b, c, x[i+ 4], 11,  1272893353);\n
            c = md5_hh(c, d, a, b, x[i+ 7], 16, -155497632);\n
            b = md5_hh(b, c, d, a, x[i+10], 23, -1094730640);\n
            a = md5_hh(a, b, c, d, x[i+13], 4 ,  681279174);\n
            d = md5_hh(d, a, b, c, x[i+ 0], 11, -358537222);\n
            c = md5_hh(c, d, a, b, x[i+ 3], 16, -722521979);\n
            b = md5_hh(b, c, d, a, x[i+ 6], 23,  76029189);\n
            a = md5_hh(a, b, c, d, x[i+ 9], 4 , -640364487);\n
            d = md5_hh(d, a, b, c, x[i+12], 11, -421815835);\n
            c = md5_hh(c, d, a, b, x[i+15], 16,  530742520);\n
            b = md5_hh(b, c, d, a, x[i+ 2], 23, -995338651);\n
\n
            a = md5_ii(a, b, c, d, x[i+ 0], 6 , -198630844);\n
            d = md5_ii(d, a, b, c, x[i+ 7], 10,  1126891415);\n
            c = md5_ii(c, d, a, b, x[i+14], 15, -1416354905);\n
            b = md5_ii(b, c, d, a, x[i+ 5], 21, -57434055);\n
            a = md5_ii(a, b, c, d, x[i+12], 6 ,  1700485571);\n
            d = md5_ii(d, a, b, c, x[i+ 3], 10, -1894986606);\n
            c = md5_ii(c, d, a, b, x[i+10], 15, -1051523);\n
            b = md5_ii(b, c, d, a, x[i+ 1], 21, -2054922799);\n
            a = md5_ii(a, b, c, d, x[i+ 8], 6 ,  1873313359);\n
            d = md5_ii(d, a, b, c, x[i+15], 10, -30611744);\n
            c = md5_ii(c, d, a, b, x[i+ 6], 15, -1560198380);\n
            b = md5_ii(b, c, d, a, x[i+13], 21,  1309151649);\n
            a = md5_ii(a, b, c, d, x[i+ 4], 6 , -145523070);\n
            d = md5_ii(d, a, b, c, x[i+11], 10, -1120210379);\n
            c = md5_ii(c, d, a, b, x[i+ 2], 15,  718787259);\n
            b = md5_ii(b, c, d, a, x[i+ 9], 21, -343485551);\n
\n
            a = safe_add(a, olda);\n
            b = safe_add(b, oldb);\n
            c = safe_add(c, oldc);\n
            d = safe_add(d, oldd);\n
        }\n
        return [a, b, c, d];\n
    };\n
\n
\n
    var obj = {\n
        /*\n
         * These are the functions you\'ll usually want to call.\n
         * They take string arguments and return either hex or base-64 encoded\n
         * strings.\n
         */\n
        hexdigest: function (s) {\n
            return binl2hex(core_md5(str2binl(s), s.length * 8));\n
        },\n
\n
        hash: function (s) {\n
            return binl2str(core_md5(str2binl(s), s.length * 8));\n
        }\n
    };\n
\n
    return obj;\n
})();\n
\n
/*\n
    This program is distributed under the terms of the MIT license.\n
    Please see the LICENSE file for details.\n
\n
    Copyright 2006-2008, OGG, LLC\n
*/\n
\n
/* jshint undef: true, unused: true:, noarg: true, latedef: true */\n
/*global document, window, setTimeout, clearTimeout, console,\n
    ActiveXObject, Base64, MD5, DOMParser */\n
// from sha1.js\n
/*global core_hmac_sha1, binb2str, str_hmac_sha1, str_sha1, b64_hmac_sha1*/\n
\n
/** File: strophe.js\n
 *  A JavaScript library for XMPP BOSH/XMPP over Websocket.\n
 *\n
 *  This is the JavaScript version of the Strophe library.  Since JavaScript\n
 *  had no facilities for persistent TCP connections, this library uses\n
 *  Bidirectional-streams Over Synchronous HTTP (BOSH) to emulate\n
 *  a persistent, stateful, two-way connection to an XMPP server.  More\n
 *  information on BOSH can be found in XEP 124.\n
 *\n
 *  This version of Strophe also works with WebSockets.\n
 *  For more information on XMPP-over WebSocket see this RFC draft:\n
 *  http://tools.ietf.org/html/draft-ietf-xmpp-websocket-00\n
 */\n
\n
/** PrivateFunction: Function.prototype.bind\n
 *  Bind a function to an instance.\n
 *\n
 *  This Function object extension method creates a bound method similar\n
 *  to those in Python.  This means that the \'this\' object will point\n
 *  to the instance you want.  See\n
 *  \074a href=\'https://developer.mozilla.org/en/JavaScript/Reference/Global_Objects/Function/bind\'\076MDC\'s bind() documentation\074/a\076 and\n
 *  \074a href=\'http://benjamin.smedbergs.us/blog/2007-01-03/bound-functions-and-function-imports-in-javascript/\'\076Bound Functions and Function Imports in JavaScript\074/a\076\n
 *  for a complete explanation.\n
 *\n
 *  This extension already exists in some browsers (namely, Firefox 3), but\n
 *  we provide it to support those that don\'t.\n
 *\n
 *  Parameters:\n
 *    (Object) obj - The object that will become \'this\' in the bound function.\n
 *    (Object) argN - An option argument that will be prepended to the\n
 *      arguments given for the function call\n
 *\n
 *  Returns:\n
 *    The bound function.\n
 */\n
if (!Function.prototype.bind) {\n
    Function.prototype.bind = function (obj /*, arg1, arg2, ... */)\n
    {\n
        var func = this;\n
        var _slice = Array.prototype.slice;\n
        var _concat = Array.prototype.concat;\n
        var _args = _slice.call(arguments, 1);\n
\n
        return function () {\n
            return func.apply(obj ? obj : this,\n
                              _concat.call(_args,\n
                                           _slice.call(arguments, 0)));\n
        };\n
    };\n
}\n
\n
/** PrivateFunction: Array.prototype.indexOf\n
 *  Return the index of an object in an array.\n
 *\n
 *  This function is not supplied by some JavaScript implementations, so\n
 *  we provide it if it is missing.  This code is from:\n
 *  http://developer.mozilla.org/En/Core_JavaScript_1.5_Reference:Objects:Array:indexOf\n
 *\n
 *  Parameters:\n
 *    (Object) elt - The object to look for.\n
 *    (Integer) from - The index from which to start looking. (optional).\n
 *\n
 *  Returns:\n
 *    The index of elt in the array or -1 if not found.\n
 */\n
if (!Array.prototype.indexOf)\n
{\n
    Array.prototype.indexOf = function(elt /*, from*/)\n
    {\n
        var len = this.length;\n
\n
        var from = Number(arguments[1]) || 0;\n
        from = (from \074 0) ? Math.ceil(from) : Math.floor(from);\n
        if (from \074 0) {\n
            from += len;\n
        }\n
\n
        for (; from \074 len; from++) {\n
            if (from in this \046\046 this[from] === elt) {\n
                return from;\n
            }\n
        }\n
\n
        return -1;\n
    };\n
}\n
\n
/* All of the Strophe globals are defined in this special function below so\n
 * that references to the globals become closures.  This will ensure that\n
 * on page reload, these references will still be available to callbacks\n
 * that are still executing.\n
 */\n
\n
(function (callback) {\n
var Strophe;\n
\n
/** Function: $build\n
 *  Create a Strophe.Builder.\n
 *  This is an alias for \'new Strophe.Builder(name, attrs)\'.\n
 *\n
 *  Parameters:\n
 *    (String) name - The root element name.\n
 *    (Object) attrs - The attributes for the root element in object notation.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Builder object.\n
 */\n
function $build(name, attrs) { return new Strophe.Builder(name, attrs); }\n
/** Function: $msg\n
 *  Create a Strophe.Builder with a \074message/\076 element as the root.\n
 *\n
 *  Parmaeters:\n
 *    (Object) attrs - The \074message/\076 element attributes in object notation.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Builder object.\n
 */\n
function $msg(attrs) { return new Strophe.Builder("message", attrs); }\n
/** Function: $iq\n
 *  Create a Strophe.Builder with an \074iq/\076 element as the root.\n
 *\n
 *  Parameters:\n
 *    (Object) attrs - The \074iq/\076 element attributes in object notation.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Builder object.\n
 */\n
function $iq(attrs) { return new Strophe.Builder("iq", attrs); }\n
/** Function: $pres\n
 *  Create a Strophe.Builder with a \074presence/\076 element as the root.\n
 *\n
 *  Parameters:\n
 *    (Object) attrs - The \074presence/\076 element attributes in object notation.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Builder object.\n
 */\n
function $pres(attrs) { return new Strophe.Builder("presence", attrs); }\n
\n
/** Class: Strophe\n
 *  An object container for all Strophe library functions.\n
 *\n
 *  This class is just a container for all the objects and constants\n
 *  used in the library.  It is not meant to be instantiated, but to\n
 *  provide a namespace for library objects, constants, and functions.\n
 */\n
Strophe = {\n
    /** Constant: VERSION\n
     *  The version of the Strophe library. Unreleased builds will have\n
     *  a version of head-HASH where HASH is a partial revision.\n
     */\n
    VERSION: "1.1.3",\n
\n
    /** Constants: XMPP Namespace Constants\n
     *  Common namespace constants from the XMPP RFCs and XEPs.\n
     *\n
     *  NS.HTTPBIND - HTTP BIND namespace from XEP 124.\n
     *  NS.BOSH - BOSH namespace from XEP 206.\n
     *  NS.CLIENT - Main XMPP client namespace.\n
     *  NS.AUTH - Legacy authentication namespace.\n
     *  NS.ROSTER - Roster operations namespace.\n
     *  NS.PROFILE - Profile namespace.\n
     *  NS.DISCO_INFO - Service discovery info namespace from XEP 30.\n
     *  NS.DISCO_ITEMS - Service discovery items namespace from XEP 30.\n
     *  NS.MUC - Multi-User Chat namespace from XEP 45.\n
     *  NS.SASL - XMPP SASL namespace from RFC 3920.\n
     *  NS.STREAM - XMPP Streams namespace from RFC 3920.\n
     *  NS.BIND - XMPP Binding namespace from RFC 3920.\n
     *  NS.SESSION - XMPP Session namespace from RFC 3920.\n
     *  NS.XHTML_IM - XHTML-IM namespace from XEP 71.\n
     *  NS.XHTML - XHTML body namespace from XEP 71.\n
     */\n
    NS: {\n
        HTTPBIND: "http://jabber.org/protocol/httpbind",\n
        BOSH: "urn:xmpp:xbosh",\n
        CLIENT: "jabber:client",\n
        AUTH: "jabber:iq:auth",\n
        ROSTER: "jabber:iq:roster",\n
        PROFILE: "jabber:iq:profile",\n
        DISCO_INFO: "http://jabber.org/protocol/disco#info",\n
        DISCO_ITEMS: "http://jabber.org/protocol/disco#items",\n
        MUC: "http://jabber.org/protocol/muc",\n
        SASL: "urn:ietf:params:xml:ns:xmpp-sasl",\n
        STREAM: "http://etherx.jabber.org/streams",\n
        BIND: "urn:ietf:params:xml:ns:xmpp-bind",\n
        SESSION: "urn:ietf:params:xml:ns:xmpp-session",\n
        VERSION: "jabber:iq:version",\n
        STANZAS: "urn:ietf:params:xml:ns:xmpp-stanzas",\n
        XHTML_IM: "http://jabber.org/protocol/xhtml-im",\n
        XHTML: "http://www.w3.org/1999/xhtml"\n
    },\n
\n
\n
    /** Constants: XHTML_IM Namespace\n
     *  contains allowed tags, tag attributes, and css properties.\n
     *  Used in the createHtml function to filter incoming html into the allowed XHTML-IM subset.\n
     *  See http://xmpp.org/extensions/xep-0071.html#profile-summary for the list of recommended\n
     *  allowed tags and their attributes.\n
     */\n
    XHTML: {\n
                tags: [\'a\',\'blockquote\',\'br\',\'cite\',\'em\',\'img\',\'li\',\'ol\',\'p\',\'span\',\'strong\',\'ul\',\'body\'],\n
                attributes: {\n
                        \'a\':          [\'href\'],\n
                        \'blockquote\': [\'style\'],\n
                        \'br\':         [],\n
                        \'cite\':       [\'style\'],\n
                        \'em\':         [],\n
                        \'img\':        [\'src\', \'alt\', \'style\', \'height\', \'width\'],\n
                        \'li\':         [\'style\'],\n
                        \'ol\':         [\'style\'],\n
                        \'p\':          [\'style\'],\n
                        \'span\':       [\'style\'],\n
                        \'strong\':     [],\n
                        \'ul\':         [\'style\'],\n
                        \'body\':       []\n
                },\n
                css: [\'background-color\',\'color\',\'font-family\',\'font-size\',\'font-style\',\'font-weight\',\'margin-left\',\'margin-right\',\'text-align\',\'text-decoration\'],\n
                validTag: function(tag)\n
                {\n
                        for(var i = 0; i \074 Strophe.XHTML.tags.length; i++) {\n
                                if(tag == Strophe.XHTML.tags[i]) {\n
                                        return true;\n
                                }\n
                        }\n
                        return false;\n
                },\n
                validAttribute: function(tag, attribute)\n
                {\n
                        if(typeof Strophe.XHTML.attributes[tag] !== \'undefined\' \046\046 Strophe.XHTML.attributes[tag].length \076 0) {\n
                                for(var i = 0; i \074 Strophe.XHTML.attributes[tag].length; i++) {\n
                                        if(attribute == Strophe.XHTML.attributes[tag][i]) {\n
                                                return true;\n
                                        }\n
                                }\n
                        }\n
                        return false;\n
                },\n
                validCSS: function(style)\n
                {\n
                        for(var i = 0; i \074 Strophe.XHTML.css.length; i++) {\n
                                if(style == Strophe.XHTML.css[i]) {\n
                                        return true;\n
                                }\n
                        }\n
                        return false;\n
                }\n
    },\n
\n
    /** Constants: Connection Status Constants\n
     *  Connection status constants for use by the connection handler\n
     *  callback.\n
     *\n
     *  Status.ERROR - An error has occurred\n
     *  Status.CONNECTING - The connection is currently being made\n
     *  Status.CONNFAIL - The connection attempt failed\n
     *  Status.AUTHENTICATING - The connection is authenticating\n
     *  Status.AUTHFAIL - The authentication attempt failed\n
     *  Status.CONNECTED - The connection has succeeded\n
     *  Status.DISCONNECTED - The connection has been terminated\n
     *  Status.DISCONNECTING - The connection is currently being terminated\n
     *  Status.ATTACHED - The connection has been attached\n
     */\n
    Status: {\n
        ERROR: 0,\n
        CONNECTING: 1,\n
        CONNFAIL: 2,\n
        AUTHENTICATING: 3,\n
        AUTHFAIL: 4,\n
        CONNECTED: 5,\n
        DISCONNECTED: 6,\n
        DISCONNECTING: 7,\n
        ATTACHED: 8\n
    },\n
\n
    /** Constants: Log Level Constants\n
     *  Logging level indicators.\n
     *\n
     *  LogLevel.DEBUG - Debug output\n
     *  LogLevel.INFO - Informational output\n
     *  LogLevel.WARN - Warnings\n
     *  LogLevel.ERROR - Errors\n
     *  LogLevel.FATAL - Fatal errors\n
     */\n
    LogLevel: {\n
        DEBUG: 0,\n
        INFO: 1,\n
        WARN: 2,\n
        ERROR: 3,\n
        FATAL: 4\n
    },\n
\n
    /** PrivateConstants: DOM Element Type Constants\n
     *  DOM element types.\n
     *\n
     *  ElementType.NORMAL - Normal element.\n
     *  ElementType.TEXT - Text data element.\n
     *  ElementType.FRAGMENT - XHTML fragment element.\n
     */\n
    ElementType: {\n
        NORMAL: 1,\n
        TEXT: 3,\n
        CDATA: 4,\n
        FRAGMENT: 11\n
    },\n
\n
    /** PrivateConstants: Timeout Values\n
     *  Timeout values for error states.  These values are in seconds.\n
     *  These should not be changed unless you know exactly what you are\n
     *  doing.\n
     *\n
     *  TIMEOUT - Timeout multiplier. A waiting request will be considered\n
     *      failed after Math.floor(TIMEOUT * wait) seconds have elapsed.\n
     *      This defaults to 1.1, and with default wait, 66 seconds.\n
     *  SECONDARY_TIMEOUT - Secondary timeout multiplier. In cases where\n
     *      Strophe can detect early failure, it will consider the request\n
     *      failed if it doesn\'t return after\n
     *      Math.floor(SECONDARY_TIMEOUT * wait) seconds have elapsed.\n
     *      This defaults to 0.1, and with default wait, 6 seconds.\n
     */\n
    TIMEOUT: 1.1,\n
    SECONDARY_TIMEOUT: 0.1,\n
\n
    /** Function: addNamespace\n
     *  This function is used to extend the current namespaces in\n
     *  Strophe.NS.  It takes a key and a value with the key being the\n
     *  name of the new namespace, with its actual value.\n
     *  For example:\n
     *  Strophe.addNamespace(\'PUBSUB\', "http://jabber.org/protocol/pubsub");\n
     *\n
     *  Parameters:\n
     *    (String) name - The name under which the namespace will be\n
     *      referenced under Strophe.NS\n
     *    (String) value - The actual namespace.\n
     */\n
    addNamespace: function (name, value)\n
    {\n
      Strophe.NS[name] = value;\n
    },\n
\n
    /** Function: forEachChild\n
     *  Map a function over some or all child elements of a given element.\n
     *\n
     *  This is a small convenience function for mapping a function over\n
     *  some or all of the children of an element.  If elemName is null, all\n
     *  children will be passed to the function, otherwise only children\n
     *  whose tag names match elemName will be passed.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The element to operate on.\n
     *    (String) elemName - The child element tag name filter.\n
     *    (Function) func - The function to apply to each child.  This\n
     *      function should take a single argument, a DOM element.\n
     */\n
    forEachChild: function (elem, elemName, func)\n
    {\n
        var i, childNode;\n
\n
        for (i = 0; i \074 elem.childNodes.length; i++) {\n
            childNode = elem.childNodes[i];\n
            if (childNode.nodeType == Strophe.ElementType.NORMAL \046\046\n
                (!elemName || this.isTagEqual(childNode, elemName))) {\n
                func(childNode);\n
            }\n
        }\n
    },\n
\n
    /** Function: isTagEqual\n
     *  Compare an element\'s tag name with a string.\n
     *\n
     *  This function is case insensitive.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) el - A DOM element.\n
     *    (String) name - The element name.\n
     *\n
     *  Returns:\n
     *    true if the element\'s tag name matches _el_, and false\n
     *    otherwise.\n
     */\n
    isTagEqual: function (el, name)\n
    {\n
        return el.tagName.toLowerCase() == name.toLowerCase();\n
    },\n
\n
    /** PrivateVariable: _xmlGenerator\n
     *  _Private_ variable that caches a DOM document to\n
     *  generate elements.\n
     */\n
    _xmlGenerator: null,\n
\n
    /** PrivateFunction: _makeGenerator\n
     *  _Private_ function that creates a dummy XML DOM document to serve as\n
     *  an element and text node generator.\n
     */\n
    _makeGenerator: function () {\n
        var doc;\n
\n
        // IE9 does implement createDocument(); however, using it will cause the browser to leak memory on page unload.\n
        // Here, we test for presence of createDocument() plus IE\'s proprietary documentMode attribute, which would be\n
                // less than 10 in the case of IE9 and below.\n
        if (document.implementation.createDocument === undefined ||\n
                        document.implementation.createDocument \046\046 document.documentMode \046\046 document.documentMode \074 10) {\n
            doc = this._getIEXmlDom();\n
            doc.appendChild(doc.createElement(\'strophe\'));\n
        } else {\n
            doc = document.implementation\n
                .createDocument(\'jabber:client\', \'strophe\', null);\n
        }\n
\n
        return doc;\n
    },\n
\n
    /** Function: xmlGenerator\n
     *  Get the DOM document to generate elements.\n
     *\n
     *  Returns:\n
     *    The currently used DOM document.\n
     */\n
    xmlGenerator: function () {\n
        if (!Strophe._xmlGenerator) {\n
            Strophe._xmlGenerator = Strophe._makeGenerator();\n
        }\n
        return Strophe._xmlGenerator;\n
    },\n
\n
    /** PrivateFunction: _getIEXmlDom\n
     *  Gets IE xml doc object\n
     *\n
     *  Returns:\n
     *    A Microsoft XML DOM Object\n
     *  See Also:\n
     *    http://msdn.microsoft.com/en-us/library/ms757837%28VS.85%29.aspx\n
     */\n
    _getIEXmlDom : function() {\n
        var doc = null;\n
        var docStrings = [\n
            "Msxml2.DOMDocument.6.0",\n
            "Msxml2.DOMDocument.5.0",\n
            "Msxml2.DOMDocument.4.0",\n
            "MSXML2.DOMDocument.3.0",\n
            "MSXML2.DOMDocument",\n
            "MSXML.DOMDocument",\n
            "Microsoft.XMLDOM"\n
        ];\n
\n
        for (var d = 0; d \074 docStrings.length; d++) {\n
            if (doc === null) {\n
                try {\n
                    doc = new ActiveXObject(docStrings[d]);\n
                } catch (e) {\n
                    doc = null;\n
                }\n
            } else {\n
                break;\n
            }\n
        }\n
\n
        return doc;\n
    },\n
\n
    /** Function: xmlElement\n
     *  Create an XML DOM element.\n
     *\n
     *  This function creates an XML DOM element correctly across all\n
     *  implementations. Note that these are not HTML DOM elements, which\n
     *  aren\'t appropriate for XMPP stanzas.\n
     *\n
     *  Parameters:\n
     *    (String) name - The name for the element.\n
     *    (Array|Object) attrs - An optional array or object containing\n
     *      key/value pairs to use as element attributes. The object should\n
     *      be in the format {\'key\': \'value\'} or {key: \'value\'}. The array\n
     *      should have the format [[\'key1\', \'value1\'], [\'key2\', \'value2\']].\n
     *    (String) text - The text child data for the element.\n
     *\n
     *  Returns:\n
     *    A new XML DOM element.\n
     */\n
    xmlElement: function (name)\n
    {\n
        if (!name) { return null; }\n
\n
        var node = Strophe.xmlGenerator().createElement(name);\n
\n
        // FIXME: this should throw errors if args are the wrong type or\n
        // there are more than two optional args\n
        var a, i, k;\n
        for (a = 1; a \074 arguments.length; a++) {\n
            if (!arguments[a]) { continue; }\n
            if (typeof(arguments[a]) == "string" ||\n
                typeof(arguments[a]) == "number") {\n
                node.appendChild(Strophe.xmlTextNode(arguments[a]));\n
            } else if (typeof(arguments[a]) == "object" \046\046\n
                       typeof(arguments[a].sort) == "function") {\n
                for (i = 0; i \074 arguments[a].length; i++) {\n
                    if (typeof(arguments[a][i]) == "object" \046\046\n
                        typeof(arguments[a][i].sort) == "function") {\n
                        node.setAttribute(arguments[a][i][0],\n
                                          arguments[a][i][1]);\n
                    }\n
                }\n
            } else if (typeof(arguments[a]) == "object") {\n
                for (k in arguments[a]) {\n
                    if (arguments[a].hasOwnProperty(k)) {\n
                        node.setAttribute(k, arguments[a][k]);\n
                    }\n
                }\n
            }\n
        }\n
\n
        return node;\n
    },\n
\n
    /*  Function: xmlescape\n
     *  Excapes invalid xml characters.\n
     *\n
     *  Parameters:\n
     *     (String) text - text to escape.\n
     *\n
     *  Returns:\n
     *      Escaped text.\n
     */\n
    xmlescape: function(text)\n
    {\n
        text = text.replace(/\\\046/g, "\046amp;");\n
        text = text.replace(/\074/g,  "\046lt;");\n
        text = text.replace(/\076/g,  "\046gt;");\n
        text = text.replace(/\'/g,  "\046apos;");\n
        text = text.replace(/"/g,  "\046quot;");\n
        return text;\n
    },\n
\n
    /** Function: xmlTextNode\n
     *  Creates an XML DOM text node.\n
     *\n
     *  Provides a cross implementation version of document.createTextNode.\n
     *\n
     *  Parameters:\n
     *    (String) text - The content of the text node.\n
     *\n
     *  Returns:\n
     *    A new XML DOM text node.\n
     */\n
    xmlTextNode: function (text)\n
    {\n
        return Strophe.xmlGenerator().createTextNode(text);\n
    },\n
\n
    /** Function: xmlHtmlNode\n
     *  Creates an XML DOM html node.\n
     *\n
     *  Parameters:\n
     *    (String) html - The content of the html node.\n
     *\n
     *  Returns:\n
     *    A new XML DOM text node.\n
     */\n
    xmlHtmlNode: function (html)\n
    {\n
        var node;\n
        //ensure text is escaped\n
        if (window.DOMParser) {\n
            var parser = new DOMParser();\n
            node = parser.parseFromString(html, "text/xml");\n
        } else {\n
            node = new ActiveXObject("Microsoft.XMLDOM");\n
            node.async="false";\n
            node.loadXML(html);\n
        }\n
        return node;\n
    },\n
\n
    /** Function: getText\n
     *  Get the concatenation of all text children of an element.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - A DOM element.\n
     *\n
     *  Returns:\n
     *    A String with the concatenated text of all text element children.\n
     */\n
    getText: function (elem)\n
    {\n
        if (!elem) { return null; }\n
\n
        var str = "";\n
        if (elem.childNodes.length === 0 \046\046 elem.nodeType ==\n
            Strophe.ElementType.TEXT) {\n
            str += elem.nodeValue;\n
        }\n
\n
        for (var i = 0; i \074 elem.childNodes.length; i++) {\n
            if (elem.childNodes[i].nodeType == Strophe.ElementType.TEXT) {\n
                str += elem.childNodes[i].nodeValue;\n
            }\n
        }\n
\n
        return Strophe.xmlescape(str);\n
    },\n
\n
    /** Function: copyElement\n
     *  Copy an XML DOM element.\n
     *\n
     *  This function copies a DOM element and all its descendants and returns\n
     *  the new copy.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - A DOM element.\n
     *\n
     *  Returns:\n
     *    A new, copied DOM element tree.\n
     */\n
    copyElement: function (elem)\n
    {\n
        var i, el;\n
        if (elem.nodeType == Strophe.ElementType.NORMAL) {\n
            el = Strophe.xmlElement(elem.tagName);\n
\n
            for (i = 0; i \074 elem.attributes.length; i++) {\n
                el.setAttribute(elem.attributes[i].nodeName.toLowerCase(),\n
                                elem.attributes[i].value);\n
            }\n
\n
            for (i = 0; i \074 elem.childNodes.length; i++) {\n
                el.appendChild(Strophe.copyElement(elem.childNodes[i]));\n
            }\n
        } else if (elem.nodeType == Strophe.ElementType.TEXT) {\n
            el = Strophe.xmlGenerator().createTextNode(elem.nodeValue);\n
        }\n
\n
        return el;\n
    },\n
\n
\n
    /** Function: createHtml\n
     *  Copy an HTML DOM element into an XML DOM.\n
     *\n
     *  This function copies a DOM element and all its descendants and returns\n
     *  the new copy.\n
     *\n
     *  Parameters:\n
     *    (HTMLElement) elem - A DOM element.\n
     *\n
     *  Returns:\n
     *    A new, copied DOM element tree.\n
     */\n
    createHtml: function (elem)\n
    {\n
        var i, el, j, tag, attribute, value, css, cssAttrs, attr, cssName, cssValue;\n
        if (elem.nodeType == Strophe.ElementType.NORMAL) {\n
            tag = elem.nodeName.toLowerCase();\n
            if(Strophe.XHTML.validTag(tag)) {\n
                try {\n
                    el = Strophe.xmlElement(tag);\n
                    for(i = 0; i \074 Strophe.XHTML.attributes[tag].length; i++) {\n
                        attribute = Strophe.XHTML.attributes[tag][i];\n
                        value = elem.getAttribute(attribute);\n
                        if(typeof value == \'undefined\' || value === null || value === \'\' || value === false || value === 0) {\n
                            continue;\n
                        }\n
                        if(attribute == \'style\' \046\046 typeof value == \'object\') {\n
                            if(typeof value.cssText != \'undefined\') {\n
                                value = value.cssText; // we\'re dealing with IE, need to get CSS out\n
                            }\n
                        }\n
                        // filter out invalid css styles\n
                        if(attribute == \'style\') {\n
                            css = [];\n
                            cssAttrs = value.split(\';\');\n
                            for(j = 0; j \074 cssAttrs.length; j++) {\n
                                attr = cssAttrs[j].split(\':\');\n
                                cssName = attr[0].replace(/^\\s*/, "").replace(/\\s*$/, "").toLowerCase();\n
                                if(Strophe.XHTML.validCSS(cssName)) {\n
                                    cssValue = attr[1].replace(/^\\s*/, "").replace(/\\s*$/, "");\n
                                    css.push(cssName + \': \' + cssValue);\n
                                }\n
                            }\n
                            if(css.length \076 0) {\n
                                value = css.join(\'; \');\n
                                el.setAttribute(attribute, value);\n
                            }\n
                        } else {\n
                            el.setAttribute(attribute, value);\n
                        }\n
                    }\n
\n
                    for (i = 0; i \074 elem.childNodes.length; i++) {\n
                        el.appendChild(Strophe.createHtml(elem.childNodes[i]));\n
                    }\n
                } catch(e) { // invalid elements\n
                  el = Strophe.xmlTextNode(\'\');\n
                }\n
            } else {\n
                el = Strophe.xmlGenerator().createDocumentFragment();\n
                for (i = 0; i \074 elem.childNodes.length; i++) {\n
                    el.appendChild(Strophe.createHtml(elem.childNodes[i]));\n
                }\n
            }\n
        } else if (elem.nodeType == Strophe.ElementType.FRAGMENT) {\n
            el = Strophe.xmlGenerator().createDocumentFragment();\n
            for (i = 0; i \074 elem.childNodes.length; i++) {\n
                el.appendChild(Strophe.createHtml(elem.childNodes[i]));\n
            }\n
        } else if (elem.nodeType == Strophe.ElementType.TEXT) {\n
            el = Strophe.xmlTextNode(elem.nodeValue);\n
        }\n
\n
        return el;\n
    },\n
\n
    /** Function: escapeNode\n
     *  Escape the node part (also called local part) of a JID.\n
     *\n
     *  Parameters:\n
     *    (String) node - A node (or local part).\n
     *\n
     *  Returns:\n
     *    An escaped node (or local part).\n
     */\n
    escapeNode: function (node)\n
    {\n
        return node.replace(/^\\s+|\\s+$/g, \'\')\n
            .replace(/\\\\/g,  "\\\\5c")\n
            .replace(/ /g,   "\\\\20")\n
            .replace(/\\"/g,  "\\\\22")\n
            .replace(/\\\046/g,  "\\\\26")\n
            .replace(/\\\'/g,  "\\\\27")\n
            .replace(/\\//g,  "\\\\2f")\n
            .replace(/:/g,   "\\\\3a")\n
            .replace(/\074/g,   "\\\\3c")\n
            .replace(/\076/g,   "\\\\3e")\n
            .replace(/@/g,   "\\\\40");\n
    },\n
\n
    /** Function: unescapeNode\n
     *  Unescape a node part (also called local part) of a JID.\n
     *\n
     *  Parameters:\n
     *    (String) node - A node (or local part).\n
     *\n
     *  Returns:\n
     *    An unescaped node (or local part).\n
     */\n
    unescapeNode: function (node)\n
    {\n
        return node.replace(/\\\\20/g, " ")\n
            .replace(/\\\\22/g, \'"\')\n
            .replace(/\\\\26/g, "\046")\n
            .replace(/\\\\27/g, "\'")\n
            .replace(/\\\\2f/g, "/")\n
            .replace(/\\\\3a/g, ":")\n
            .replace(/\\\\3c/g, "\074")\n
            .replace(/\\\\3e/g, "\076")\n
            .replace(/\\\\40/g, "@")\n
            .replace(/\\\\5c/g, "\\\\");\n
    },\n
\n
    /** Function: getNodeFromJid\n
     *  Get the node portion of a JID String.\n
     *\n
     *  Parameters:\n
     *    (String) jid - A JID.\n
     *\n
     *  Returns:\n
     *    A String containing the node.\n
     */\n
    getNodeFromJid: function (jid)\n
    {\n
        if (jid.indexOf("@") \074 0) { return null; }\n
        return jid.split("@")[0];\n
    },\n
\n
    /** Function: getDomainFromJid\n
     *  Get the domain portion of a JID String.\n
     *\n
     *  Parameters:\n
     *    (String) jid - A JID.\n
     *\n
     *  Returns:\n
     *    A String containing the domain.\n
     */\n
    getDomainFromJid: function (jid)\n
    {\n
        var bare = Strophe.getBareJidFromJid(jid);\n
        if (bare.indexOf("@") \074 0) {\n
            return bare;\n
        } else {\n
            var parts = bare.split("@");\n
            parts.splice(0, 1);\n
            return parts.join(\'@\');\n
        }\n
    },\n
\n
    /** Function: getResourceFromJid\n
     *  Get the resource portion of a JID String.\n
     *\n
     *  Parameters:\n
     *    (String) jid - A JID.\n
     *\n
     *  Returns:\n
     *    A String containing the resource.\n
     */\n
    getResourceFromJid: function (jid)\n
    {\n
        var s = jid.split("/");\n
        if (s.length \074 2) { return null; }\n
        s.splice(0, 1);\n
        return s.join(\'/\');\n
    },\n
\n
    /** Function: getBareJidFromJid\n
     *  Get the bare JID from a JID String.\n
     *\n
     *  Parameters:\n
     *    (String) jid - A JID.\n
     *\n
     *  Returns:\n
     *    A String containing the bare JID.\n
     */\n
    getBareJidFromJid: function (jid)\n
    {\n
        return jid ? jid.split("/")[0] : null;\n
    },\n
\n
    /** Function: log\n
     *  User overrideable logging function.\n
     *\n
     *  This function is called whenever the Strophe library calls any\n
     *  of the logging functions.  The default implementation of this\n
     *  function does nothing.  If client code wishes to handle the logging\n
     *  messages, it should override this with\n
     *  \076 Strophe.log = function (level, msg) {\n
     *  \076   (user code here)\n
     *  \076 };\n
     *\n
     *  Please note that data sent and received over the wire is logged\n
     *  via Strophe.Connection.rawInput() and Strophe.Connection.rawOutput().\n
     *\n
     *  The different levels and their meanings are\n
     *\n
     *    DEBUG - Messages useful for debugging purposes.\n
     *    INFO - Informational messages.  This is mostly information like\n
     *      \'disconnect was called\' or \'SASL auth succeeded\'.\n
     *    WARN - Warnings about potential problems.  This is mostly used\n
     *      to report transient connection errors like request timeouts.\n
     *    ERROR - Some error occurred.\n
     *    FATAL - A non-recoverable fatal error occurred.\n
     *\n
     *  Parameters:\n
     *    (Integer) level - The log level of the log message.  This will\n
     *      be one of the values in Strophe.LogLevel.\n
     *    (String) msg - The log message.\n
     */\n
    /* jshint ignore:start */\n
    log: function (level, msg)\n
    {\n
        return;\n
    },\n
    /* jshint ignore:end */\n
\n
    /** Function: debug\n
     *  Log a message at the Strophe.LogLevel.DEBUG level.\n
     *\n
     *  Parameters:\n
     *    (String) msg - The log message.\n
     */\n
    debug: function(msg)\n
    {\n
        this.log(this.LogLevel.DEBUG, msg);\n
    },\n
\n
    /** Function: info\n
     *  Log a message at the Strophe.LogLevel.INFO level.\n
     *\n
     *  Parameters:\n
     *    (String) msg - The log message.\n
     */\n
    info: function (msg)\n
    {\n
        this.log(this.LogLevel.INFO, msg);\n
    },\n
\n
    /** Function: warn\n
     *  Log a message at the Strophe.LogLevel.WARN level.\n
     *\n
     *  Parameters:\n
     *    (String) msg - The log message.\n
     */\n
    warn: function (msg)\n
    {\n
        this.log(this.LogLevel.WARN, msg);\n
    },\n
\n
    /** Function: error\n
     *  Log a message at the Strophe.LogLevel.ERROR level.\n
     *\n
     *  Parameters:\n
     *    (String) msg - The log message.\n
     */\n
    error: function (msg)\n
    {\n
        this.log(this.LogLevel.ERROR, msg);\n
    },\n
\n
    /** Function: fatal\n
     *  Log a message at the Strophe.LogLevel.FATAL level.\n
     *\n
     *  Parameters:\n
     *    (String) msg - The log message.\n
     */\n
    fatal: function (msg)\n
    {\n
        this.log(this.LogLevel.FATAL, msg);\n
    },\n
\n
    /** Function: serialize\n
     *  Render a DOM element and all descendants to a String.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - A DOM element.\n
     *\n
     *  Returns:\n
     *    The serialized element tree as a String.\n
     */\n
    serialize: function (elem)\n
    {\n
        var result;\n
\n
        if (!elem) { return null; }\n
\n
        if (typeof(elem.tree) === "function") {\n
            elem = elem.tree();\n
        }\n
\n
        var nodeName = elem.nodeName;\n
        var i, child;\n
\n
        if (elem.getAttribute("_realname")) {\n
            nodeName = elem.getAttribute("_realname");\n
        }\n
\n
        result = "\074" + nodeName;\n
        for (i = 0; i \074 elem.attributes.length; i++) {\n
               if(elem.attributes[i].nodeName != "_realname") {\n
                 result += " " + elem.attributes[i].nodeName.toLowerCase() +\n
                "=\'" + elem.attributes[i].value\n
                    .replace(/\046/g, "\046amp;")\n
                       .replace(/\\\'/g, "\046apos;")\n
                       .replace(/\076/g, "\046gt;")\n
                       .replace(/\074/g, "\046lt;") + "\'";\n
               }\n
        }\n
\n
        if (elem.childNodes.length \076 0) {\n
            result += "\076";\n
            for (i = 0; i \074 elem.childNodes.length; i++) {\n
                child = elem.childNodes[i];\n
                switch( child.nodeType ){\n
                  case Strophe.ElementType.NORMAL:\n
                    // normal element, so recurse\n
                    result += Strophe.serialize(child);\n
                    break;\n
                  case Strophe.ElementType.TEXT:\n
                    // text element to escape values\n
                    result += Strophe.xmlescape(child.nodeValue);\n
                    break;\n
                  case Strophe.ElementType.CDATA:\n
                    // cdata section so don\'t escape values\n
                    result += "\074![CDATA["+child.nodeValue+"]]\076";\n
                }\n
            }\n
            result += "\074/" + nodeName + "\076";\n
        } else {\n
            result += "/\076";\n
        }\n
\n
        return result;\n
    },\n
\n
    /** PrivateVariable: _requestId\n
     *  _Private_ variable that keeps track of the request ids for\n
     *  connections.\n
     */\n
    _requestId: 0,\n
\n
    /** PrivateVariable: Strophe.connectionPlugins\n
     *  _Private_ variable Used to store plugin names that need\n
     *  initialization on Strophe.Connection construction.\n
     */\n
    _connectionPlugins: {},\n
\n
    /** Function: addConnectionPlugin\n
     *  Extends the Strophe.Connection object with the given plugin.\n
     *\n
     *  Parameters:\n
     *    (String) name - The name of the extension.\n
     *    (Object) ptype - The plugin\'s prototype.\n
     */\n
    addConnectionPlugin: function (name, ptype)\n
    {\n
        Strophe._connectionPlugins[name] = ptype;\n
    }\n
};\n
\n
/** Class: Strophe.Builder\n
 *  XML DOM builder.\n
 *\n
 *  This object provides an interface similar to JQuery but for building\n
 *  DOM element easily and rapidly.  All the functions except for toString()\n
 *  and tree() return the object, so calls can be chained.  Here\'s an\n
 *  example using the $iq() builder helper.\n
 *  \076 $iq({to: \'you\', from: \'me\', type: \'get\', id: \'1\'})\n
 *  \076     .c(\'query\', {xmlns: \'strophe:example\'})\n
 *  \076     .c(\'example\')\n
 *  \076     .toString()\n
 *  The above generates this XML fragment\n
 *  \076 \074iq to=\'you\' from=\'me\' type=\'get\' id=\'1\'\076\n
 *  \076   \074query xmlns=\'strophe:example\'\076\n
 *  \076     \074example/\076\n
 *  \076   \074/query\076\n
 *  \076 \074/iq\076\n
 *  The corresponding DOM manipulations to get a similar fragment would be\n
 *  a lot more tedious and probably involve several helper variables.\n
 *\n
 *  Since adding children makes new operations operate on the child, up()\n
 *  is provided to traverse up the tree.  To add two children, do\n
 *  \076 builder.c(\'child1\', ...).up().c(\'child2\', ...)\n
 *  The next operation on the Builder will be relative to the second child.\n
 */\n
\n
/** Constructor: Strophe.Builder\n
 *  Create a Strophe.Builder object.\n
 *\n
 *  The attributes should be passed in object notation.  For example\n
 *  \076 var b = new Builder(\'message\', {to: \'you\', from: \'me\'});\n
 *  or\n
 *  \076 var b = new Builder(\'messsage\', {\'xml:lang\': \'en\'});\n
 *\n
 *  Parameters:\n
 *    (String) name - The name of the root element.\n
 *    (Object) attrs - The attributes for the root element in object notation.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Builder.\n
 */\n
Strophe.Builder = function (name, attrs)\n
{\n
    // Set correct namespace for jabber:client elements\n
    if (name == "presence" || name == "message" || name == "iq") {\n
        if (attrs \046\046 !attrs.xmlns) {\n
            attrs.xmlns = Strophe.NS.CLIENT;\n
        } else if (!attrs) {\n
            attrs = {xmlns: Strophe.NS.CLIENT};\n
        }\n
    }\n
\n
    // Holds the tree being built.\n
    this.nodeTree = Strophe.xmlElement(name, attrs);\n
\n
    // Points to the current operation node.\n
    this.node = this.nodeTree;\n
};\n
\n
Strophe.Builder.prototype = {\n
    /** Function: tree\n
     *  Return the DOM tree.\n
     *\n
     *  This function returns the current DOM tree as an element object.  This\n
     *  is suitable for passing to functions like Strophe.Connection.send().\n
     *\n
     *  Returns:\n
     *    The DOM tree as a element object.\n
     */\n
    tree: function ()\n
    {\n
        return this.nodeTree;\n
    },\n
\n
    /** Function: toString\n
     *  Serialize the DOM tree to a String.\n
     *\n
     *  This function returns a string serialization of the current DOM\n
     *  tree.  It is often used internally to pass data to a\n
     *  Strophe.Request object.\n
     *\n
     *  Returns:\n
     *    The serialized DOM tree in a String.\n
     */\n
    toString: function ()\n
    {\n
        return Strophe.serialize(this.nodeTree);\n
    },\n
\n
    /** Function: up\n
     *  Make the current parent element the new current element.\n
     *\n
     *  This function is often used after c() to traverse back up the tree.\n
     *  For example, to add two children to the same element\n
     *  \076 builder.c(\'child1\', {}).up().c(\'child2\', {});\n
     *\n
     *  Returns:\n
     *    The Stophe.Builder object.\n
     */\n
    up: function ()\n
    {\n
        this.node = this.node.parentNode;\n
        return this;\n
    },\n
\n
    /** Function: attrs\n
     *  Add or modify attributes of the current element.\n
     *\n
     *  The attributes should be passed in object notation.  This function\n
     *  does not move the current element pointer.\n
     *\n
     *  Parameters:\n
     *    (Object) moreattrs - The attributes to add/modify in object notation.\n
     *\n
     *  Returns:\n
     *    The Strophe.Builder object.\n
     */\n
    attrs: function (moreattrs)\n
    {\n
        for (var k in moreattrs) {\n
            if (moreattrs.hasOwnProperty(k)) {\n
                this.node.setAttribute(k, moreattrs[k]);\n
            }\n
        }\n
        return this;\n
    },\n
\n
    /** Function: c\n
     *  Add a child to the current element and make it the new current\n
     *  element.\n
     *\n
     *  This function moves the current element pointer to the child,\n
     *  unless text is provided.  If you need to add another child, it\n
     *  is necessary to use up() to go back to the parent in the tree.\n
     *\n
     *  Parameters:\n
     *    (String) name - The name of the child.\n
     *    (Object) attrs - The attributes of the child in object notation.\n
     *    (String) text - The text to add to the child.\n
     *\n
     *  Returns:\n
     *    The Strophe.Builder object.\n
     */\n
    c: function (name, attrs, text)\n
    {\n
        var child = Strophe.xmlElement(name, attrs, text);\n
        this.node.appendChild(child);\n
        if (!text) {\n
            this.node = child;\n
        }\n
        return this;\n
    },\n
\n
    /** Function: cnode\n
     *  Add a child to the current element and make it the new current\n
     *  element.\n
     *\n
     *  This function is the same as c() except that instead of using a\n
     *  name and an attributes object to create the child it uses an\n
     *  existing DOM element object.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - A DOM element.\n
     *\n
     *  Returns:\n
     *    The Strophe.Builder object.\n
     */\n
    cnode: function (elem)\n
    {\n
        var impNode;\n
        var xmlGen = Strophe.xmlGenerator();\n
        try {\n
            impNode = (xmlGen.importNode !== undefined);\n
        }\n
        catch (e) {\n
            impNode = false;\n
        }\n
        var newElem = impNode ?\n
                      xmlGen.importNode(elem, true) :\n
                      Strophe.copyElement(elem);\n
        this.node.appendChild(newElem);\n
        this.node = newElem;\n
        return this;\n
    },\n
\n
    /** Function: t\n
     *  Add a child text element.\n
     *\n
     *  This *does not* make the child the new current element since there\n
     *  are no children of text elements.\n
     *\n
     *  Parameters:\n
     *    (String) text - The text data to append to the current element.\n
     *\n
     *  Returns:\n
     *    The Strophe.Builder object.\n
     */\n
    t: function (text)\n
    {\n
        var child = Strophe.xmlTextNode(text);\n
        this.node.appendChild(child);\n
        return this;\n
    },\n
\n
    /** Function: h\n
     *  Replace current element contents with the HTML passed in.\n
     *\n
     *  This *does not* make the child the new current element\n
     *\n
     *  Parameters:\n
     *    (String) html - The html to insert as contents of current element.\n
     *\n
     *  Returns:\n
     *    The Strophe.Builder object.\n
     */\n
    h: function (html)\n
    {\n
        var fragment = document.createElement(\'body\');\n
\n
        // force the browser to try and fix any invalid HTML tags\n
        fragment.innerHTML = html;\n
\n
        // copy cleaned html into an xml dom\n
        var xhtml = Strophe.createHtml(fragment);\n
\n
        while(xhtml.childNodes.length \076 0) {\n
            this.node.appendChild(xhtml.childNodes[0]);\n
        }\n
        return this;\n
    }\n
};\n
\n
/** PrivateClass: Strophe.Handler\n
 *  _Private_ helper class for managing stanza handlers.\n
 *\n
 *  A Strophe.Handler encapsulates a user provided callback function to be\n
 *  executed when matching stanzas are received by the connection.\n
 *  Handlers can be either one-off or persistant depending on their\n
 *  return value. Returning true will cause a Handler to remain active, and\n
 *  returning false will remove the Handler.\n
 *\n
 *  Users will not use Strophe.Handler objects directly, but instead they\n
 *  will use Strophe.Connection.addHandler() and\n
 *  Strophe.Connection.deleteHandler().\n
 */\n
\n
/** PrivateConstructor: Strophe.Handler\n
 *  Create and initialize a new Strophe.Handler.\n
 *\n
 *  Parameters:\n
 *    (Function) handler - A function to be executed when the handler is run.\n
 *    (String) ns - The namespace to match.\n
 *    (String) name - The element name to match.\n
 *    (String) type - The element type to match.\n
 *    (String) id - The element id attribute to match.\n
 *    (String) from - The element from attribute to match.\n
 *    (Object) options - Handler options\n
 *\n
 *  Returns:\n
 *    A new Strophe.Handler object.\n
 */\n
Strophe.Handler = function (handler, ns, name, type, id, from, options)\n
{\n
    this.handler = handler;\n
    this.ns = ns;\n
    this.name = name;\n
    this.type = type;\n
    this.id = id;\n
    this.options = options || {matchBare: false};\n
\n
    // default matchBare to false if undefined\n
    if (!this.options.matchBare) {\n
        this.options.matchBare = false;\n
    }\n
\n
    if (this.options.matchBare) {\n
        this.from = from ? Strophe.getBareJidFromJid(from) : null;\n
    } else {\n
        this.from = from;\n
    }\n
\n
    // whether the handler is a user handler or a system handler\n
    this.user = true;\n
};\n
\n
Strophe.Handler.prototype = {\n
    /** PrivateFunction: isMatch\n
     *  Tests if a stanza matches the Strophe.Handler.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The XML element to test.\n
     *\n
     *  Returns:\n
     *    true if the stanza matches and false otherwise.\n
     */\n
    isMatch: function (elem)\n
    {\n
        var nsMatch;\n
        var from = null;\n
\n
        if (this.options.matchBare) {\n
            from = Strophe.getBareJidFromJid(elem.getAttribute(\'from\'));\n
        } else {\n
            from = elem.getAttribute(\'from\');\n
        }\n
\n
        nsMatch = false;\n
        if (!this.ns) {\n
            nsMatch = true;\n
        } else {\n
            var that = this;\n
            Strophe.forEachChild(elem, null, function (elem) {\n
                if (elem.getAttribute("xmlns") == that.ns) {\n
                    nsMatch = true;\n
                }\n
            });\n
\n
            nsMatch = nsMatch || elem.getAttribute("xmlns") == this.ns;\n
        }\n
\n
        if (nsMatch \046\046\n
            (!this.name || Strophe.isTagEqual(elem, this.name)) \046\046\n
            (!this.type || elem.getAttribute("type") == this.type) \046\046\n
            (!this.id || elem.getAttribute("id") == this.id) \046\046\n
            (!this.from || from == this.from)) {\n
                return true;\n
        }\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: run\n
     *  Run the callback on a matching stanza.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The DOM element that triggered the\n
     *      Strophe.Handler.\n
     *\n
     *  Returns:\n
     *    A boolean indicating if the handler should remain active.\n
     */\n
    run: function (elem)\n
    {\n
        var result = null;\n
        try {\n
            result = this.handler(elem);\n
        } catch (e) {\n
            if (e.sourceURL) {\n
                Strophe.fatal("error: " + this.handler +\n
                              " " + e.sourceURL + ":" +\n
                              e.line + " - " + e.name + ": " + e.message);\n
            } else if (e.fileName) {\n
                if (typeof(console) != "undefined") {\n
                    console.trace();\n
                    console.error(this.handler, " - error - ", e, e.message);\n
                }\n
                Strophe.fatal("error: " + this.handler + " " +\n
                              e.fileName + ":" + e.lineNumber + " - " +\n
                              e.name + ": " + e.message);\n
            } else {\n
                Strophe.fatal("error: " + e.message + "\\n" + e.stack);\n
            }\n
\n
            throw e;\n
        }\n
\n
        return result;\n
    },\n
\n
    /** PrivateFunction: toString\n
     *  Get a String representation of the Strophe.Handler object.\n
     *\n
     *  Returns:\n
     *    A String.\n
     */\n
    toString: function ()\n
    {\n
        return "{Handler: " + this.handler + "(" + this.name + "," +\n
            this.id + "," + this.ns + ")}";\n
    }\n
};\n
\n
/** PrivateClass: Strophe.TimedHandler\n
 *  _Private_ helper class for managing timed handlers.\n
 *\n
 *  A Strophe.TimedHandler encapsulates a user provided callback that\n
 *  should be called after a certain period of time or at regular\n
 *  intervals.  The return value of the callback determines whether the\n
 *  Strophe.TimedHandler will continue to fire.\n
 *\n
 *  Users will not use Strophe.TimedHandler objects directly, but instead\n
 *  they will use Strophe.Connection.addTimedHandler() and\n
 *  Strophe.Connection.deleteTimedHandler().\n
 */\n
\n
/** PrivateConstructor: Strophe.TimedHandler\n
 *  Create and initialize a new Strophe.TimedHandler object.\n
 *\n
 *  Parameters:\n
 *    (Integer) period - The number of milliseconds to wait before the\n
 *      handler is called.\n
 *    (Function) handler - The callback to run when the handler fires.  This\n
 *      function should take no arguments.\n
 *\n
 *  Returns:\n
 *    A new Strophe.TimedHandler object.\n
 */\n
Strophe.TimedHandler = function (period, handler)\n
{\n
    this.period = period;\n
    this.handler = handler;\n
\n
    this.lastCalled = new Date().getTime();\n
    this.user = true;\n
};\n
\n
Strophe.TimedHandler.prototype = {\n
    /** PrivateFunction: run\n
     *  Run the callback for the Strophe.TimedHandler.\n
     *\n
     *  Returns:\n
     *    true if the Strophe.TimedHandler should be called again, and false\n
     *      otherwise.\n
     */\n
    run: function ()\n
    {\n
        this.lastCalled = new Date().getTime();\n
        return this.handler();\n
    },\n
\n
    /** PrivateFunction: reset\n
     *  Reset the last called time for the Strophe.TimedHandler.\n
     */\n
    reset: function ()\n
    {\n
        this.lastCalled = new Date().getTime();\n
    },\n
\n
    /** PrivateFunction: toString\n
     *  Get a string representation of the Strophe.TimedHandler object.\n
     *\n
     *  Returns:\n
     *    The string representation.\n
     */\n
    toString: function ()\n
    {\n
        return "{TimedHandler: " + this.handler + "(" + this.period +")}";\n
    }\n
};\n
\n
/** Class: Strophe.Connection\n
 *  XMPP Connection manager.\n
 *\n
 *  This class is the main part of Strophe.  It manages a BOSH connection\n
 *  to an XMPP server and dispatches events to the user callbacks as\n
 *  data arrives.  It supports SASL PLAIN, SASL DIGEST-MD5, SASL SCRAM-SHA1\n
 *  and legacy authentication.\n
 *\n
 *  After creating a Strophe.Connection object, the user will typically\n
 *  call connect() with a user supplied callback to handle connection level\n
 *  events like authentication failure, disconnection, or connection\n
 *  complete.\n
 *\n
 *  The user will also have several event handlers defined by using\n
 *  addHandler() and addTimedHandler().  These will allow the user code to\n
 *  respond to interesting stanzas or do something periodically with the\n
 *  connection.  These handlers will be active once authentication is\n
 *  finished.\n
 *\n
 *  To send data to the connection, use send().\n
 */\n
\n
/** Constructor: Strophe.Connection\n
 *  Create and initialize a Strophe.Connection object.\n
 *\n
 *  The transport-protocol for this connection will be chosen automatically\n
 *  based on the given service parameter. URLs starting with "ws://" or\n
 *  "wss://" will use WebSockets, URLs starting with "http://", "https://"\n
 *  or without a protocol will use BOSH.\n
 *\n
 *  To make Strophe connect to the current host you can leave out the protocol\n
 *  and host part and just pass the path, e.g.\n
 *\n
 *  \076 var conn = new Strophe.Connection("/http-bind/");\n
 *\n
 *  WebSocket options:\n
 *\n
 *  If you want to connect to the current host with a WebSocket connection you\n
 *  can tell Strophe to use WebSockets through a "protocol" attribute in the\n
 *  optional options parameter. Valid values are "ws" for WebSocket and "wss"\n
 *  for Secure WebSocket.\n
 *  So to connect to "wss://CURRENT_HOSTNAME/xmpp-websocket" you would call\n
 *\n
 *  \076 var conn = new Strophe.Connection("/xmpp-websocket/", {protocol: "wss"});\n
 *\n
 *  Note that relative URLs _NOT_ starting with a "/" will also include the path\n
 *  of the current site.\n
 *\n
 *  Also because downgrading security is not permitted by browsers, when using\n
 *  relative URLs both BOSH and WebSocket connections will use their secure\n
 *  variants if the current connection to the site is also secure (https).\n
 *\n
 *  BOSH options:\n
 *\n
 *  by adding "sync" to the options, you can control if requests will\n
 *  be made synchronously or not. The default behaviour is asynchronous.\n
 *  If you want to make requests synchronous, make "sync" evaluate to true:\n
 *  \076 var conn = new Strophe.Connection("/http-bind/", {sync: true});\n
 *  You can also toggle this on an already established connection:\n
 *  \076 conn.options.sync = true;\n
 *\n
 *\n
 *  Parameters:\n
 *    (String) service - The BOSH or WebSocket service URL.\n
 *    (Object) options - A hash of configuration options\n
 *\n
 *  Returns:\n
 *    A new Strophe.Connection object.\n
 */\n
Strophe.Connection = function (service, options)\n
{\n
    // The service URL\n
    this.service = service;\n
\n
    // Configuration options\n
    this.options = options || {};\n
    var proto = this.options.protocol || "";\n
\n
    // Select protocal based on service or options\n
    if (service.indexOf("ws:") === 0 || service.indexOf("wss:") === 0 ||\n
            proto.indexOf("ws") === 0) {\n
        this._proto = new Strophe.Websocket(this);\n
    } else {\n
        this._proto = new Strophe.Bosh(this);\n
    }\n
    /* The connected JID. */\n
    this.jid = "";\n
    /* the JIDs domain */\n
    this.domain = null;\n
    /* stream:features */\n
    this.features = null;\n
\n
    // SASL\n
    this._sasl_data = {};\n
    this.do_session = false;\n
    this.do_bind = false;\n
\n
    // handler lists\n
    this.timedHandlers = [];\n
    this.handlers = [];\n
    this.removeTimeds = [];\n
    this.removeHandlers = [];\n
    this.addTimeds = [];\n
    this.addHandlers = [];\n
\n
    this._authentication = {};\n
    this._idleTimeout = null;\n
    this._disconnectTimeout = null;\n
\n
    this.do_authentication = true;\n
    this.authenticated = false;\n
    this.disconnecting = false;\n
    this.connected = false;\n
\n
    this.errors = 0;\n
\n
    this.paused = false;\n
\n
    this._data = [];\n
    this._uniqueId = 0;\n
\n
    this._sasl_success_handler = null;\n
    this._sasl_failure_handler = null;\n
    this._sasl_challenge_handler = null;\n
\n
    // Max retries before disconnecting\n
    this.maxRetries = 5;\n
\n
    // setup onIdle callback every 1/10th of a second\n
    this._idleTimeout = setTimeout(this._onIdle.bind(this), 100);\n
\n
    // initialize plugins\n
    for (var k in Strophe._connectionPlugins) {\n
        if (Strophe._connectionPlugins.hasOwnProperty(k)) {\n
            var ptype = Strophe._connectionPlugins[k];\n
            // jslint complaints about the below line, but this is fine\n
            var F = function () {}; // jshint ignore:line\n
            F.prototype = ptype;\n
            this[k] = new F();\n
            this[k].init(this);\n
        }\n
    }\n
};\n
\n
Strophe.Connection.prototype = {\n
    /** Function: reset\n
     *  Reset the connection.\n
     *\n
     *  This function should be called after a connection is disconnected\n
     *  before that connection is reused.\n
     */\n
    reset: function ()\n
    {\n
        this._proto._reset();\n
\n
        // SASL\n
        this.do_session = false;\n
        this.do_bind = false;\n
\n
        // handler lists\n
        this.timedHandlers = [];\n
        this.handlers = [];\n
        this.removeTimeds = [];\n
        this.removeHandlers = [];\n
        this.addTimeds = [];\n
        this.addHandlers = [];\n
        this._authentication = {};\n
\n
        this.authenticated = false;\n
        this.disconnecting = false;\n
        this.connected = false;\n
\n
        this.errors = 0;\n
\n
        this._requests = [];\n
        this._uniqueId = 0;\n
    },\n
\n
    /** Function: pause\n
     *  Pause the request manager.\n
     *\n
     *  This will prevent Strophe from sending any more requests to the\n
     *  server.  This is very useful for temporarily pausing\n
     *  BOSH-Connections while a lot of send() calls are happening quickly.\n
     *  This causes Strophe to send the data in a single request, saving\n
     *  many request trips.\n
     */\n
    pause: function ()\n
    {\n
        this.paused = true;\n
    },\n
\n
    /** Function: resume\n
     *  Resume the request manager.\n
     *\n
     *  This resumes after pause() has been called.\n
     */\n
    resume: function ()\n
    {\n
        this.paused = false;\n
    },\n
\n
    /** Function: getUniqueId\n
     *  Generate a unique ID for use in \074iq/\076 elements.\n
     *\n
     *  All \074iq/\076 stanzas are required to have unique id attributes.  This\n
     *  function makes creating these easy.  Each connection instance has\n
     *  a counter which starts from zero, and the value of this counter\n
     *  plus a colon followed by the suffix becomes the unique id. If no\n
     *  suffix is supplied, the counter is used as the unique id.\n
     *\n
     *  Suffixes are used to make debugging easier when reading the stream\n
     *  data, and their use is recommended.  The counter resets to 0 for\n
     *  every new connection for the same reason.  For connections to the\n
     *  same server that authenticate the same way, all the ids should be\n
     *  the same, which makes it easy to see changes.  This is useful for\n
     *  automated testing as well.\n
     *\n
     *  Parameters:\n
     *    (String) suffix - A optional suffix to append to the id.\n
     *\n
     *  Returns:\n
     *    A unique string to be used for the id attribute.\n
     */\n
    getUniqueId: function (suffix)\n
    {\n
        if (typeof(suffix) == "string" || typeof(suffix) == "number") {\n
            return ++this._uniqueId + ":" + suffix;\n
        } else {\n
            return ++this._uniqueId + "";\n
        }\n
    },\n
\n
    /** Function: connect\n
     *  Starts the connection process.\n
     *\n
     *  As the connection process proceeds, the user supplied callback will\n
     *  be triggered multiple times with status updates.  The callback\n
     *  should take two arguments - the status code and the error condition.\n
     *\n
     *  The status code will be one of the values in the Strophe.Status\n
     *  constants.  The error condition will be one of the conditions\n
     *  defined in RFC 3920 or the condition \'strophe-parsererror\'.\n
     *\n
     *  The Parameters _wait_, _hold_ and _route_ are optional and only relevant\n
     *  for BOSH connections. Please see XEP 124 for a more detailed explanation\n
     *  of the optional parameters.\n
     *\n
     *  Parameters:\n
     *    (String) jid - The user\'s JID.  This may be a bare JID,\n
     *      or a full JID.  If a node is not supplied, SASL ANONYMOUS\n
     *      authentication will be attempted.\n
     *    (String) pass - The user\'s password.\n
     *    (Function) callback - The connect callback function.\n
     *    (Integer) wait - The optional HTTPBIND wait value.  This is the\n
     *      time the server will wait before returning an empty result for\n
     *      a request.  The default setting of 60 seconds is recommended.\n
     *    (Integer) hold - The optional HTTPBIND hold value.  This is the\n
     *      number of connections the server will hold at one time.  This\n
     *      should almost always be set to 1 (the default).\n
     *    (String) route - The optional route value.\n
     */\n
    connect: function (jid, pass, callback, wait, hold, route)\n
    {\n
        this.jid = jid;\n
        /** Variable: authzid\n
         *  Authorization identity.\n
         */\n
        this.authzid = Strophe.getBareJidFromJid(this.jid);\n
        /** Variable: authcid\n
         *  Authentication identity (User name).\n
         */\n
        this.authcid = Strophe.getNodeFromJid(this.jid);\n
        /** Variable: pass\n
         *  Authentication identity (User password).\n
         */\n
        this.pass = pass;\n
        /** Variable: servtype\n
         *  Digest MD5 compatibility.\n
         */\n
        this.servtype = "xmpp";\n
        this.connect_callback = callback;\n
        this.disconnecting = false;\n
        this.connected = false;\n
        this.authenticated = false;\n
        this.errors = 0;\n
\n
        // parse jid for domain\n
        this.domain = Strophe.getDomainFromJid(this.jid);\n
\n
        this._changeConnectStatus(Strophe.Status.CONNECTING, null);\n
\n
        this._proto._connect(wait, hold, route);\n
    },\n
\n
    /** Function: attach\n
     *  Attach to an already created and authenticated BOSH session.\n
     *\n
     *  This function is provided to allow Strophe to attach to BOSH\n
     *  sessions which have been created externally, perhaps by a Web\n
     *  application.  This is often used to support auto-login type features\n
     *  without putting user credentials into the page.\n
     *\n
     *  Parameters:\n
     *    (String) jid - The full JID that is bound by the session.\n
     *    (String) sid - The SID of the BOSH session.\n
     *    (String) rid - The current RID of the BOSH session.  This RID\n
     *      will be used by the next request.\n
     *    (Function) callback The connect callback function.\n
     *    (Integer) wait - The optional HTTPBIND wait value.  This is the\n
     *      time the server will wait before returning an empty result for\n
     *      a request.  The default setting of 60 seconds is recommended.\n
     *      Other settings will require tweaks to the Strophe.TIMEOUT value.\n
     *    (Integer) hold - The optional HTTPBIND hold value.  This is the\n
     *      number of connections the server will hold at one time.  This\n
     *      should almost always be set to 1 (the default).\n
     *    (Integer) wind - The optional HTTBIND window value.  This is the\n
     *      allowed range of request ids that are valid.  The default is 5.\n
     */\n
    attach: function (jid, sid, rid, callback, wait, hold, wind)\n
    {\n
        this._proto._attach(jid, sid, rid, callback, wait, hold, wind);\n
    },\n
\n
    /** Function: xmlInput\n
     *  User overrideable function that receives XML data coming into the\n
     *  connection.\n
     *\n
     *  The default function does nothing.  User code can override this with\n
     *  \076 Strophe.Connection.xmlInput = function (elem) {\n
     *  \076   (user code)\n
     *  \076 };\n
     *\n
     *  Due to limitations of current Browsers\' XML-Parsers the opening and closing\n
     *  \074stream\076 tag for WebSocket-Connoctions will be passed as selfclosing here.\n
     *\n
     *  BOSH-Connections will have all stanzas wrapped in a \074body\076 tag. See\n
     *  \074Strophe.Bosh.strip\076 if you want to strip this tag.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The XML data received by the connection.\n
     */\n
    /* jshint unused:false */\n
    xmlInput: function (elem)\n
    {\n
        return;\n
    },\n
    /* jshint unused:true */\n
\n
    /** Function: xmlOutput\n
     *  User overrideable function that receives XML data sent to the\n
     *  connection.\n
     *\n
     *  The default function does nothing.  User code can override this with\n
     *  \076 Strophe.Connection.xmlOutput = function (elem) {\n
     *  \076   (user code)\n
     *  \076 };\n
     *\n
     *  Due to limitations of current Browsers\' XML-Parsers the opening and closing\n
     *  \074stream\076 tag for WebSocket-Connoctions will be passed as selfclosing here.\n
     *\n
     *  BOSH-Connections will have all stanzas wrapped in a \074body\076 tag. See\n
     *  \074Strophe.Bosh.strip\076 if you want to strip this tag.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The XMLdata sent by the connection.\n
     */\n
    /* jshint unused:false */\n
    xmlOutput: function (elem)\n
    {\n
        return;\n
    },\n
    /* jshint unused:true */\n
\n
    /** Function: rawInput\n
     *  User overrideable function that receives raw data coming into the\n
     *  connection.\n
     *\n
     *  The default function does nothing.  User code can override this with\n
     *  \076 Strophe.Connection.rawInput = function (data) {\n
     *  \076   (user code)\n
     *  \076 };\n
     *\n
     *  Parameters:\n
     *    (String) data - The data received by the connection.\n
     */\n
    /* jshint unused:false */\n
    rawInput: function (data)\n
    {\n
        return;\n
    },\n
    /* jshint unused:true */\n
\n
    /** Function: rawOutput\n
     *  User overrideable function that receives raw data sent to the\n
     *  connection.\n
     *\n
     *  The default function does nothing.  User code can override this with\n
     *  \076 Strophe.Connection.rawOutput = function (data) {\n
     *  \076   (user code)\n
     *  \076 };\n
     *\n
     *  Parameters:\n
     *    (String) data - The data sent by the connection.\n
     */\n
    /* jshint unused:false */\n
    rawOutput: function (data)\n
    {\n
        return;\n
    },\n
    /* jshint unused:true */\n
\n
    /** Function: send\n
     *  Send a stanza.\n
     *\n
     *  This function is called to push data onto the send queue to\n
     *  go out over the wire.  Whenever a request is sent to the BOSH\n
     *  server, all pending data is sent and the queue is flushed.\n
     *\n
     *  Parameters:\n
     *    (XMLElement |\n
     *     [XMLElement] |\n
     *     Strophe.Builder) elem - The stanza to send.\n
     */\n
    send: function (elem)\n
    {\n
        if (elem === null) { return ; }\n
        if (typeof(elem.sort) === "function") {\n
            for (var i = 0; i \074 elem.length; i++) {\n
                this._queueData(elem[i]);\n
            }\n
        } else if (typeof(elem.tree) === "function") {\n
            this._queueData(elem.tree());\n
        } else {\n
            this._queueData(elem);\n
        }\n
\n
        this._proto._send();\n
    },\n
\n
    /** Function: flush\n
     *  Immediately send any pending outgoing data.\n
     *\n
     *  Normally send() queues outgoing data until the next idle period\n
     *  (100ms), which optimizes network use in the common cases when\n
     *  several send()s are called in succession. flush() can be used to\n
     *  immediately send all pending data.\n
     */\n
    flush: function ()\n
    {\n
        // cancel the pending idle period and run the idle function\n
        // immediately\n
        clearTimeout(this._idleTimeout);\n
        this._onIdle();\n
    },\n
\n
    /** Function: sendIQ\n
     *  Helper function to send IQ stanzas.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The stanza to send.\n
     *    (Function) callback - The callback function for a successful request.\n
     *    (Function) errback - The callback function for a failed or timed\n
     *      out request.  On timeout, the stanza will be null.\n
     *    (Integer) timeout - The time specified in milliseconds for a\n
     *      timeout to occur.\n
     *\n
     *  Returns:\n
     *    The id used to send the IQ.\n
    */\n
    sendIQ: function(elem, callback, errback, timeout) {\n
        var timeoutHandler = null;\n
        var that = this;\n
\n
        if (typeof(elem.tree) === "function") {\n
            elem = elem.tree();\n
        }\n
        var id = elem.getAttribute(\'id\');\n
\n
        // inject id if not found\n
        if (!id) {\n
            id = this.getUniqueId("sendIQ");\n
            elem.setAttribute("id", id);\n
        }\n
\n
        var handler = this.addHandler(function (stanza) {\n
            // remove timeout handler if there is one\n
            if (timeoutHandler) {\n
                that.deleteTimedHandler(timeoutHandler);\n
            }\n
\n
            var iqtype = stanza.getAttribute(\'type\');\n
            if (iqtype == \'result\') {\n
                if (callback) {\n
                    callback(stanza);\n
                }\n
            } else if (iqtype == \'error\') {\n
                if (errback) {\n
                    errback(stanza);\n
                }\n
            } else {\n
                throw {\n
                    name: "StropheError",\n
            message: "Got bad IQ type of " + iqtype\n
                };\n
            }\n
        }, null, \'iq\', null, id);\n
\n
        // if timeout specified, setup timeout handler.\n
        if (timeout) {\n
            timeoutHandler = this.addTimedHandler(timeout, function () {\n
                // get rid of normal handler\n
                that.deleteHandler(handler);\n
\n
                // call errback on timeout with null stanza\n
                if (errback) {\n
                    errback(null);\n
                }\n
                return false;\n
            });\n
        }\n
\n
        this.send(elem);\n
\n
        return id;\n
    },\n
\n
    /** PrivateFunction: _queueData\n
     *  Queue outgoing data for later sending.  Also ensures that the data\n
     *  is a DOMElement.\n
     */\n
    _queueData: function (element) {\n
        if (element === null ||\n
            !element.tagName ||\n
            !element.childNodes) {\n
            throw {\n
                name: "StropheError",\n
                message: "Cannot queue non-DOMElement."\n
            };\n
        }\n
\n
        this._data.push(element);\n
    },\n
\n
    /** PrivateFunction: _sendRestart\n
     *  Send an xmpp:restart stanza.\n
     */\n
    _sendRestart: function ()\n
    {\n
        this._data.push("restart");\n
\n
        this._proto._sendRestart();\n
\n
        this._idleTimeout = setTimeout(this._onIdle.bind(this), 100);\n
    },\n
\n
    /** Function: addTimedHandler\n
     *  Add a timed handler to the connection.\n
     *\n
     *  This function adds a timed handler.  The provided handler will\n
     *  be called every period milliseconds until it returns false,\n
     *  the connection is terminated, or the handler is removed.  Handlers\n
     *  that wish to continue being invoked should return true.\n
     *\n
     *  Because of method binding it is necessary to save the result of\n
     *  this function if you wish to remove a handler with\n
     *  deleteTimedHandler().\n
     *\n
     *  Note that user handlers are not active until authentication is\n
     *  successful.\n
     *\n
     *  Parameters:\n
     *    (Integer) period - The period of the handler.\n
     *    (Function) handler - The callback function.\n
     *\n
     *  Returns:\n
     *    A reference to the handler that can be used to remove it.\n
     */\n
    addTimedHandler: function (period, handler)\n
    {\n
        var thand = new Strophe.TimedHandler(period, handler);\n
        this.addTimeds.push(thand);\n
        return thand;\n
    },\n
\n
    /** Function: deleteTimedHandler\n
     *  Delete a timed handler for a connection.\n
     *\n
     *  This function removes a timed handler from the connection.  The\n
     *  handRef parameter is *not* the function passed to addTimedHandler(),\n
     *  but is the reference returned from addTimedHandler().\n
     *\n
     *  Parameters:\n
     *    (Strophe.TimedHandler) handRef - The handler reference.\n
     */\n
    deleteTimedHandler: function (handRef)\n
    {\n
        // this must be done in the Idle loop so that we don\'t change\n
        // the handlers during iteration\n
        this.removeTimeds.push(handRef);\n
    },\n
\n
    /** Function: addHandler\n
     *  Add a stanza handler for the connection.\n
     *\n
     *  This function adds a stanza handler to the connection.  The\n
     *  handler callback will be called for any stanza that matches\n
     *  the parameters.  Note that if multiple parameters are supplied,\n
     *  they must all match for the handler to be invoked.\n
     *\n
     *  The handler will receive the stanza that triggered it as its argument.\n
     *  The handler should return true if it is to be invoked again;\n
     *  returning false will remove the handler after it returns.\n
     *\n
     *  As a convenience, the ns parameters applies to the top level element\n
     *  and also any of its immediate children.  This is primarily to make\n
     *  matching /iq/query elements easy.\n
     *\n
     *  The options argument contains handler matching flags that affect how\n
     *  matches are determined. Currently the only flag is matchBare (a\n
     *  boolean). When matchBare is true, the from parameter and the from\n
     *  attribute on the stanza will be matched as bare JIDs instead of\n
     *  full JIDs. To use this, pass {matchBare: true} as the value of\n
     *  options. The default value for matchBare is false.\n
     *\n
     *  The return value should be saved if you wish to remove the handler\n
     *  with deleteHandler().\n
     *\n
     *  Parameters:\n
     *    (Function) handler - The user callback.\n
     *    (String) ns - The namespace to match.\n
     *    (String) name - The stanza name to match.\n
     *    (String) type - The stanza type attribute to match.\n
     *    (String) id - The stanza id attribute to match.\n
     *    (String) from - The stanza from attribute to match.\n
     *    (String) options - The handler options\n
     *\n
     *  Returns:\n
     *    A reference to the handler that can be used to remove it.\n
     */\n
    addHandler: function (handler, ns, name, type, id, from, options)\n
    {\n
        var hand = new Strophe.Handler(handler, ns, name, type, id, from, options);\n
        this.addHandlers.push(hand);\n
        return hand;\n
    },\n
\n
    /** Function: deleteHandler\n
     *  Delete a stanza handler for a connection.\n
     *\n
     *  This function removes a stanza handler from the connection.  The\n
     *  handRef parameter is *not* the function passed to addHandler(),\n
     *  but is the reference returned from addHandler().\n
     *\n
     *  Parameters:\n
     *    (Strophe.Handler) handRef - The handler reference.\n
     */\n
    deleteHandler: function (handRef)\n
    {\n
        // this must be done in the Idle loop so that we don\'t change\n
        // the handlers during iteration\n
        this.removeHandlers.push(handRef);\n
    },\n
\n
    /** Function: disconnect\n
     *  Start the graceful disconnection process.\n
     *\n
     *  This function starts the disconnection process.  This process starts\n
     *  by sending unavailable presence and sending BOSH body of type\n
     *  terminate.  A timeout handler makes sure that disconnection happens\n
     *  even if the BOSH server does not respond.\n
     *\n
     *  The user supplied connection callback will be notified of the\n
     *  progress as this process happens.\n
     *\n
     *  Parameters:\n
     *    (String) reason - The reason the disconnect is occuring.\n
     */\n
    disconnect: function (reason)\n
    {\n
        this._changeConnectStatus(Strophe.Status.DISCONNECTING, reason);\n
\n
        Strophe.info("Disconnect was called because: " + reason);\n
        if (this.connected) {\n
            var pres = false;\n
            this.disconnecting = true;\n
            if (this.authenticated) {\n
                pres = $pres({\n
                    xmlns: Strophe.NS.CLIENT,\n
                    type: \'unavailable\'\n
                });\n
            }\n
            // setup timeout handler\n
            this._disconnectTimeout = this._addSysTimedHandler(\n
                3000, this._onDisconnectTimeout.bind(this));\n
            this._proto._disconnect(pres);\n
        }\n
    },\n
\n
    /** PrivateFunction: _changeConnectStatus\n
     *  _Private_ helper function that makes sure plugins and the user\'s\n
     *  callback are notified of connection status changes.\n
     *\n
     *  Parameters:\n
     *    (Integer) status - the new connection status, one of the values\n
     *      in Strophe.Status\n
     *    (String) condition - the error condition or null\n
     */\n
    _changeConnectStatus: function (status, condition)\n
    {\n
        // notify all plugins listening for status changes\n
        for (var k in Strophe._connectionPlugins) {\n
            if (Strophe._connectionPlugins.hasOwnProperty(k)) {\n
                var plugin = this[k];\n
                if (plugin.statusChanged) {\n
                    try {\n
                        plugin.statusChanged(status, condition);\n
                    } catch (err) {\n
                        Strophe.error("" + k + " plugin caused an exception " +\n
                                      "changing status: " + err);\n
                    }\n
                }\n
            }\n
        }\n
\n
        // notify the user\'s callback\n
        if (this.connect_callback) {\n
            try {\n
                this.connect_callback(status, condition);\n
            } catch (e) {\n
                Strophe.error("User connection callback caused an " +\n
                              "exception: " + e);\n
            }\n
        }\n
    },\n
\n
    /** PrivateFunction: _doDisconnect\n
     *  _Private_ function to disconnect.\n
     *\n
     *  This is the last piece of the disconnection logic.  This resets the\n
     *  connection and alerts the user\'s connection callback.\n
     */\n
    _doDisconnect: function ()\n
    {\n
        // Cancel Disconnect Timeout\n
        if (this._disconnectTimeout !== null) {\n
            this.deleteTimedHandler(this._disconnectTimeout);\n
            this._disconnectTimeout = null;\n
        }\n
\n
        Strophe.info("_doDisconnect was called");\n
        this._proto._doDisconnect();\n
\n
        this.authenticated = false;\n
        this.disconnecting = false;\n
\n
        // delete handlers\n
        this.handlers = [];\n
        this.timedHandlers = [];\n
        this.removeTimeds = [];\n
        this.removeHandlers = [];\n
        this.addTimeds = [];\n
        this.addHandlers = [];\n
\n
        // tell the parent we disconnected\n
        this._changeConnectStatus(Strophe.Status.DISCONNECTED, null);\n
        this.connected = false;\n
    },\n
\n
    /** PrivateFunction: _dataRecv\n
     *  _Private_ handler to processes incoming data from the the connection.\n
     *\n
     *  Except for _connect_cb handling the initial connection request,\n
     *  this function handles the incoming data for all requests.  This\n
     *  function also fires stanza handlers that match each incoming\n
     *  stanza.\n
     *\n
     *  Parameters:\n
     *    (Strophe.Request) req - The request that has data ready.\n
     *    (string) req - The stanza a raw string (optiona).\n
     */\n
    _dataRecv: function (req, raw)\n
    {\n
        Strophe.info("_dataRecv called");\n
        var elem = this._proto._reqToData(req);\n
        if (elem === null) { return; }\n
\n
        if (this.xmlInput !== Strophe.Connection.prototype.xmlInput) {\n
            if (elem.nodeName === this._proto.strip \046\046 elem.childNodes.length) {\n
                this.xmlInput(elem.childNodes[0]);\n
            } else {\n
                this.xmlInput(elem);\n
            }\n
        }\n
        if (this.rawInput !== Strophe.Connection.prototype.rawInput) {\n
            if (raw) {\n
                this.rawInput(raw);\n
            } else {\n
                this.rawInput(Strophe.serialize(elem));\n
            }\n
        }\n
\n
        // remove handlers scheduled for deletion\n
        var i, hand;\n
        while (this.removeHandlers.length \076 0) {\n
            hand = this.removeHandlers.pop();\n
            i = this.handlers.indexOf(hand);\n
            if (i \076= 0) {\n
                this.handlers.splice(i, 1);\n
            }\n
        }\n
\n
        // add handlers scheduled for addition\n
        while (this.addHandlers.length \076 0) {\n
            this.handlers.push(this.addHandlers.pop());\n
        }\n
\n
        // handle graceful disconnect\n
        if (this.disconnecting \046\046 this._proto._emptyQueue()) {\n
            this._doDisconnect();\n
            return;\n
        }\n
\n
        var typ = elem.getAttribute("type");\n
        var cond, conflict;\n
        if (typ !== null \046\046 typ == "terminate") {\n
            // Don\'t process stanzas that come in after disconnect\n
            if (this.disconnecting) {\n
                return;\n
            }\n
\n
            // an error occurred\n
            cond = elem.getAttribute("condition");\n
            conflict = elem.getElementsByTagName("conflict");\n
            if (cond !== null) {\n
                if (cond == "remote-stream-error" \046\046 conflict.length \076 0) {\n
                    cond = "conflict";\n
                }\n
                this._changeConnectStatus(Strophe.Status.CONNFAIL, cond);\n
            } else {\n
                this._changeConnectStatus(Strophe.Status.CONNFAIL, "unknown");\n
            }\n
            this.disconnect(\'unknown stream-error\');\n
            return;\n
        }\n
\n
        // send each incoming stanza through the handler chain\n
        var that = this;\n
        Strophe.forEachChild(elem, null, function (child) {\n
            var i, newList;\n
            // process handlers\n
            newList = that.handlers;\n
            that.handlers = [];\n
            for (i = 0; i \074 newList.length; i++) {\n
                var hand = newList[i];\n
                // encapsulate \'handler.run\' not to lose the whole handler list if\n
                // one of the handlers throws an exception\n
                try {\n
                    if (hand.isMatch(child) \046\046\n
                        (that.authenticated || !hand.user)) {\n
                        if (hand.run(child)) {\n
                            that.handlers.push(hand);\n
                        }\n
                    } else {\n
                        that.handlers.push(hand);\n
                    }\n
                } catch(e) {\n
                    // if the handler throws an exception, we consider it as false\n
                    Strophe.warn(\'Removing Strophe handlers due to uncaught exception: \' + e.message);\n
                }\n
            }\n
        });\n
    },\n
\n
\n
    /** Attribute: mechanisms\n
     *  SASL Mechanisms available for Conncection.\n
     */\n
    mechanisms: {},\n
\n
    /** PrivateFunction: _connect_cb\n
     *  _Private_ handler for initial connection request.\n
     *\n
     *  This handler is used to process the initial connection request\n
     *  response from the BOSH server. It is used to set up authentication\n
     *  handlers and start the authentication process.\n
     *\n
     *  SASL authentication will be attempted if available, otherwise\n
     *  the code will fall back to legacy authentication.\n
     *\n
     *  Parameters:\n
     *    (Strophe.Request) req - The current request.\n
     *    (Function) _callback - low level (xmpp) connect callback function.\n
     *      Useful for plugins with their own xmpp connect callback (when their)\n
     *      want to do something special).\n
     */\n
    _connect_cb: function (req, _callback, raw)\n
    {\n
        Strophe.info("_connect_cb was called");\n
\n
        this.connected = true;\n
\n
        var bodyWrap = this._proto._reqToData(req);\n
        if (!bodyWrap) { return; }\n
\n
        if (this.xmlInput !== Strophe.Connection.prototype.xmlInput) {\n
            if (bodyWrap.nodeName === this._proto.strip \046\046 bodyWrap.childNodes.length) {\n
                this.xmlInput(bodyWrap.childNodes[0]);\n
            } else {\n
                this.xmlInput(bodyWrap);\n
            }\n
        }\n
        if (this.rawInput !== Strophe.Connection.prototype.rawInput) {\n
            if (raw) {\n
                this.rawInput(raw);\n
            } else {\n
                this.rawInput(Strophe.serialize(bodyWrap));\n
            }\n
        }\n
\n
        var conncheck = this._proto._connect_cb(bodyWrap);\n
        if (conncheck === Strophe.Status.CONNFAIL) {\n
            return;\n
        }\n
\n
        this._authentication.sasl_scram_sha1 = false;\n
        this._authentication.sasl_plain = false;\n
        this._authentication.sasl_digest_md5 = false;\n
        this._authentication.sasl_anonymous = false;\n
\n
        this._authentication.legacy_auth = false;\n
\n
        // Check for the stream:features tag\n
        var hasFeatures = bodyWrap.getElementsByTagName("stream:features").length \076 0;\n
        if (!hasFeatures) {\n
            hasFeatures = bodyWrap.getElementsByTagName("features").length \076 0;\n
        }\n
        var mechanisms = bodyWrap.getElementsByTagName("mechanism");\n
        var matched = [];\n
        var i, mech, found_authentication = false;\n
        if (!hasFeatures) {\n
            this._proto._no_auth_received(_callback);\n
            return;\n
        }\n
        if (mechanisms.length \076 0) {\n
            for (i = 0; i \074 mechanisms.length; i++) {\n
                mech = Strophe.getText(mechanisms[i]);\n
                if (this.mechanisms[mech]) matched.push(this.mechanisms[mech]);\n
            }\n
        }\n
        this._authentication.legacy_auth =\n
            bodyWrap.getElementsByTagName("auth").length \076 0;\n
        found_authentication = this._authentication.legacy_auth ||\n
            matched.length \076 0;\n
        if (!found_authentication) {\n
            this._proto._no_auth_received(_callback);\n
            return;\n
        }\n
        if (this.do_authentication !== false)\n
            this.authenticate(matched);\n
    },\n
\n
    /** Function: authenticate\n
     * Set up authentication\n
     *\n
     *  Contiunues the initial connection request by setting up authentication\n
     *  handlers and start the authentication process.\n
     *\n
     *  SASL authentication will be attempted if available, otherwise\n
     *  the code will fall back to legacy authentication.\n
     *\n
     */\n
    authenticate: function (matched)\n
    {\n
      var i;\n
      // Sorting matched mechanisms according to priority.\n
      for (i = 0; i \074 matched.length - 1; ++i) {\n
        var higher = i;\n
        for (var j = i + 1; j \074 matched.length; ++j) {\n
          if (matched[j].prototype.priority \076 matched[higher].prototype.priority) {\n
            higher = j;\n
          }\n
        }\n
        if (higher != i) {\n
          var swap = matched[i];\n
          matched[i] = matched[higher];\n
          matched[higher] = swap;\n
        }\n
      }\n
\n
      // run each mechanism\n
      var mechanism_found = false;\n
      for (i = 0; i \074 matched.length; ++i) {\n
        if (!matched[i].test(this)) continue;\n
\n
        this._sasl_success_handler = this._addSysHandler(\n
          this._sasl_success_cb.bind(this), null,\n
          "success", null, null);\n
        this._sasl_failure_handler = this._addSysHandler(\n
          this._sasl_failure_cb.bind(this), null,\n
          "failure", null, null);\n
        this._sasl_challenge_handler = this._addSysHandler(\n
          this._sasl_challenge_cb.bind(this), null,\n
          "challenge", null, null);\n
\n
        this._sasl_mechanism = new matched[i]();\n
        this._sasl_mechanism.onStart(this);\n
\n
        var request_auth_exchange = $build("auth", {\n
          xmlns: Strophe.NS.SASL,\n
          mechanism: this._sasl_mechanism.name\n
        });\n
\n
        if (this._sasl_mechanism.isClientFirst) {\n
          var response = this._sasl_mechanism.onChallenge(this, null);\n
          request_auth_exchange.t(Base64.encode(response));\n
        }\n
\n
        this.send(request_auth_exchange.tree());\n
\n
        mechanism_found = true;\n
        break;\n
      }\n
\n
      if (!mechanism_found) {\n
        // if none of the mechanism worked\n
        if (Strophe.getNodeFromJid(this.jid) === null) {\n
            // we don\'t have a node, which is required for non-anonymous\n
            // client connections\n
            this._changeConnectStatus(Strophe.Status.CONNFAIL,\n
                                      \'x-strophe-bad-non-anon-jid\');\n
            this.disconnect(\'x-strophe-bad-non-anon-jid\');\n
        } else {\n
          // fall back to legacy authentication\n
          this._changeConnectStatus(Strophe.Status.AUTHENTICATING, null);\n
          this._addSysHandler(this._auth1_cb.bind(this), null, null,\n
                              null, "_auth_1");\n
\n
          this.send($iq({\n
            type: "get",\n
            to: this.domain,\n
            id: "_auth_1"\n
          }).c("query", {\n
            xmlns: Strophe.NS.AUTH\n
          }).c("username", {}).t(Strophe.getNodeFromJid(this.jid)).tree());\n
        }\n
      }\n
\n
    },\n
\n
    _sasl_challenge_cb: function(elem) {\n
      var challenge = Base64.decode(Strophe.getText(elem));\n
      var response = this._sasl_mechanism.onChallenge(this, challenge);\n
\n
      var stanza = $build(\'response\', {\n
          xmlns: Strophe.NS.SASL\n
      });\n
      if (response !== "") {\n
        stanza.t(Base64.encode(response));\n
      }\n
      this.send(stanza.tree());\n
\n
      return true;\n
    },\n
\n
    /** PrivateFunction: _auth1_cb\n
     *  _Private_ handler for legacy authentication.\n
     *\n
     *  This handler is called in response to the initial \074iq type=\'get\'/\076\n
     *  for legacy authentication.  It builds an authentication \074iq/\076 and\n
     *  sends it, creating a handler (calling back to _auth2_cb()) to\n
     *  handle the result\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The stanza that triggered the callback.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    /* jshint unused:false */\n
    _auth1_cb: function (elem)\n
    {\n
        // build plaintext auth iq\n
        var iq = $iq({type: "set", id: "_auth_2"})\n
            .c(\'query\', {xmlns: Strophe.NS.AUTH})\n
            .c(\'username\', {}).t(Strophe.getNodeFromJid(this.jid))\n
            .up()\n
            .c(\'password\').t(this.pass);\n
\n
        if (!Strophe.getResourceFromJid(this.jid)) {\n
            // since the user has not supplied a resource, we pick\n
            // a default one here.  unlike other auth methods, the server\n
            // cannot do this for us.\n
            this.jid = Strophe.getBareJidFromJid(this.jid) + \'/strophe\';\n
        }\n
        iq.up().c(\'resource\', {}).t(Strophe.getResourceFromJid(this.jid));\n
\n
        this._addSysHandler(this._auth2_cb.bind(this), null,\n
                            null, null, "_auth_2");\n
\n
        this.send(iq.tree());\n
\n
        return false;\n
    },\n
    /* jshint unused:true */\n
\n
    /** PrivateFunction: _sasl_success_cb\n
     *  _Private_ handler for succesful SASL authentication.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The matching stanza.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _sasl_success_cb: function (elem)\n
    {\n
        if (this._sasl_data["server-signature"]) {\n
            var serverSignature;\n
            var success = Base64.decode(Strophe.getText(elem));\n
            var attribMatch = /([a-z]+)=([^,]+)(,|$)/;\n
            var matches = success.match(attribMatch);\n
            if (matches[1] == "v") {\n
                serverSignature = matches[2];\n
            }\n
\n
            if (serverSignature != this._sasl_data["server-signature"]) {\n
              // remove old handlers\n
              this.deleteHandler(this._sasl_failure_handler);\n
              this._sasl_failure_handler = null;\n
              if (this._sasl_challenge_handler) {\n
                this.deleteHandler(this._sasl_challenge_handler);\n
                this._sasl_challenge_handler = null;\n
              }\n
\n
              this._sasl_data = {};\n
              return this._sasl_failure_cb(null);\n
            }\n
        }\n
\n
        Strophe.info("SASL authentication succeeded.");\n
\n
        if(this._sasl_mechanism)\n
          this._sasl_mechanism.onSuccess();\n
\n
        // remove old handlers\n
        this.deleteHandler(this._sasl_failure_handler);\n
        this._sasl_failure_handler = null;\n
        if (this._sasl_challenge_handler) {\n
            this.deleteHandler(this._sasl_challenge_handler);\n
            this._sasl_challenge_handler = null;\n
        }\n
\n
        this._addSysHandler(this._sasl_auth1_cb.bind(this), null,\n
                            "stream:features", null, null);\n
\n
        // we must send an xmpp:restart now\n
        this._sendRestart();\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: _sasl_auth1_cb\n
     *  _Private_ handler to start stream binding.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The matching stanza.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _sasl_auth1_cb: function (elem)\n
    {\n
        // save stream:features for future usage\n
        this.features = elem;\n
\n
        var i, child;\n
\n
        for (i = 0; i \074 elem.childNodes.length; i++) {\n
            child = elem.childNodes[i];\n
            if (child.nodeName == \'bind\') {\n
                this.do_bind = true;\n
            }\n
\n
            if (child.nodeName == \'session\') {\n
                this.do_session = true;\n
            }\n
        }\n
\n
        if (!this.do_bind) {\n
            this._changeConnectStatus(Strophe.Status.AUTHFAIL, null);\n
            return false;\n
        } else {\n
            this._addSysHandler(this._sasl_bind_cb.bind(this), null, null,\n
                                null, "_bind_auth_2");\n
\n
            var resource = Strophe.getResourceFromJid(this.jid);\n
            if (resource) {\n
                this.send($iq({type: "set", id: "_bind_auth_2"})\n
                          .c(\'bind\', {xmlns: Strophe.NS.BIND})\n
                          .c(\'resource\', {}).t(resource).tree());\n
            } else {\n
                this.send($iq({type: "set", id: "_bind_auth_2"})\n
                          .c(\'bind\', {xmlns: Strophe.NS.BIND})\n
                          .tree());\n
            }\n
        }\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: _sasl_bind_cb\n
     *  _Private_ handler for binding result and session start.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The matching stanza.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _sasl_bind_cb: function (elem)\n
    {\n
        if (elem.getAttribute("type") == "error") {\n
            Strophe.info("SASL binding failed.");\n
            var conflict = elem.getElementsByTagName("conflict"), condition;\n
            if (conflict.length \076 0) {\n
                condition = \'conflict\';\n
            }\n
            this._changeConnectStatus(Strophe.Status.AUTHFAIL, condition);\n
            return false;\n
        }\n
\n
        // TODO - need to grab errors\n
        var bind = elem.getElementsByTagName("bind");\n
        var jidNode;\n
        if (bind.length \076 0) {\n
            // Grab jid\n
            jidNode = bind[0].getElementsByTagName("jid");\n
            if (jidNode.length \076 0) {\n
                this.jid = Strophe.getText(jidNode[0]);\n
\n
                if (this.do_session) {\n
                    this._addSysHandler(this._sasl_session_cb.bind(this),\n
                                        null, null, null, "_session_auth_2");\n
\n
                    this.send($iq({type: "set", id: "_session_auth_2"})\n
                                  .c(\'session\', {xmlns: Strophe.NS.SESSION})\n
                                  .tree());\n
                } else {\n
                    this.authenticated = true;\n
                    this._changeConnectStatus(Strophe.Status.CONNECTED, null);\n
                }\n
            }\n
        } else {\n
            Strophe.info("SASL binding failed.");\n
            this._changeConnectStatus(Strophe.Status.AUTHFAIL, null);\n
            return false;\n
        }\n
    },\n
\n
    /** PrivateFunction: _sasl_session_cb\n
     *  _Private_ handler to finish successful SASL connection.\n
     *\n
     *  This sets Connection.authenticated to true on success, which\n
     *  starts the processing of user handlers.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The matching stanza.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _sasl_session_cb: function (elem)\n
    {\n
        if (elem.getAttribute("type") == "result") {\n
            this.authenticated = true;\n
            this._changeConnectStatus(Strophe.Status.CONNECTED, null);\n
        } else if (elem.getAttribute("type") == "error") {\n
            Strophe.info("Session creation failed.");\n
            this._changeConnectStatus(Strophe.Status.AUTHFAIL, null);\n
            return false;\n
        }\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: _sasl_failure_cb\n
     *  _Private_ handler for SASL authentication failure.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The matching stanza.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    /* jshint unused:false */\n
    _sasl_failure_cb: function (elem)\n
    {\n
        // delete unneeded handlers\n
        if (this._sasl_success_handler) {\n
            this.deleteHandler(this._sasl_success_handler);\n
            this._sasl_success_handler = null;\n
        }\n
        if (this._sasl_challenge_handler) {\n
            this.deleteHandler(this._sasl_challenge_handler);\n
            this._sasl_challenge_handler = null;\n
        }\n
\n
        if(this._sasl_mechanism)\n
          this._sasl_mechanism.onFailure();\n
        this._changeConnectStatus(Strophe.Status.AUTHFAIL, null);\n
        return false;\n
    },\n
    /* jshint unused:true */\n
\n
    /** PrivateFunction: _auth2_cb\n
     *  _Private_ handler to finish legacy authentication.\n
     *\n
     *  This handler is called when the result from the jabber:iq:auth\n
     *  \074iq/\076 stanza is returned.\n
     *\n
     *  Parameters:\n
     *    (XMLElement) elem - The stanza that triggered the callback.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _auth2_cb: function (elem)\n
    {\n
        if (elem.getAttribute("type") == "result") {\n
            this.authenticated = true;\n
            this._changeConnectStatus(Strophe.Status.CONNECTED, null);\n
        } else if (elem.getAttribute("type") == "error") {\n
            this._changeConnectStatus(Strophe.Status.AUTHFAIL, null);\n
            this.disconnect(\'authentication failed\');\n
        }\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: _addSysTimedHandler\n
     *  _Private_ function to add a system level timed handler.\n
     *\n
     *  This function is used to add a Strophe.TimedHandler for the\n
     *  library code.  System timed handlers are allowed to run before\n
     *  authentication is complete.\n
     *\n
     *  Parameters:\n
     *    (Integer) period - The period of the handler.\n
     *    (Function) handler - The callback function.\n
     */\n
    _addSysTimedHandler: function (period, handler)\n
    {\n
        var thand = new Strophe.TimedHandler(period, handler);\n
        thand.user = false;\n
        this.addTimeds.push(thand);\n
        return thand;\n
    },\n
\n
    /** PrivateFunction: _addSysHandler\n
     *  _Private_ function to add a system level stanza handler.\n
     *\n
     *  This function is used to add a Strophe.Handler for the\n
     *  library code.  System stanza handlers are allowed to run before\n
     *  authentication is complete.\n
     *\n
     *  Parameters:\n
     *    (Function) handler - The callback function.\n
     *    (String) ns - The namespace to match.\n
     *    (String) name - The stanza name to match.\n
     *    (String) type - The stanza type attribute to match.\n
     *    (String) id - The stanza id attribute to match.\n
     */\n
    _addSysHandler: function (handler, ns, name, type, id)\n
    {\n
        var hand = new Strophe.Handler(handler, ns, name, type, id);\n
        hand.user = false;\n
        this.addHandlers.push(hand);\n
        return hand;\n
    },\n
\n
    /** PrivateFunction: _onDisconnectTimeout\n
     *  _Private_ timeout handler for handling non-graceful disconnection.\n
     *\n
     *  If the graceful disconnect process does not complete within the\n
     *  time allotted, this handler finishes the disconnect anyway.\n
     *\n
     *  Returns:\n
     *    false to remove the handler.\n
     */\n
    _onDisconnectTimeout: function ()\n
    {\n
        Strophe.info("_onDisconnectTimeout was called");\n
\n
        this._proto._onDisconnectTimeout();\n
\n
        // actually disconnect\n
        this._doDisconnect();\n
\n
        return false;\n
    },\n
\n
    /** PrivateFunction: _onIdle\n
     *  _Private_ handler to process events during idle cycle.\n
     *\n
     *  This handler is called every 100ms to fire timed handlers that\n
     *  are ready and keep poll requests going.\n
     */\n
    _onIdle: function ()\n
    {\n
        var i, thand, since, newList;\n
\n
        // add timed handlers scheduled for addition\n
        // NOTE: we add before remove in the case a timed handler is\n
        // added and then deleted before the next _onIdle() call.\n
        while (this.addTimeds.length \076 0) {\n
            this.timedHandlers.push(this.addTimeds.pop());\n
        }\n
\n
        // remove timed handlers that have been scheduled for deletion\n
        while (this.removeTimeds.length \076 0) {\n
            thand = this.removeTimeds.pop();\n
            i = this.timedHandlers.indexOf(thand);\n
            if (i \076= 0) {\n
                this.timedHandlers.splice(i, 1);\n
            }\n
        }\n
\n
        // call ready timed handlers\n
        var now = new Date().getTime();\n
        newList = [];\n
        for (i = 0; i \074 this.timedHandlers.length; i++) {\n
            thand = this.timedHandlers[i];\n
            if (this.authenticated || !thand.user) {\n
                since = thand.lastCalled + thand.period;\n
                if (since - now \074= 0) {\n
                    if (thand.run()) {\n
                        newList.push(thand);\n
                    }\n
                } else {\n
                    newList.push(thand);\n
                }\n
            }\n
        }\n
        this.timedHandlers = newList;\n
\n
        clearTimeout(this._idleTimeout);\n
\n
        this._proto._onIdle();\n
\n
        // reactivate the timer only if connected\n
        if (this.connected) {\n
            this._idleTimeout = setTimeout(this._onIdle.bind(this), 100);\n
        }\n
    }\n
};\n
\n
if (callback) {\n
    callback(Strophe, $build, $msg, $iq, $pres);\n
}\n
\n
/** Class: Strophe.SASLMechanism\n
 *\n
 *  encapsulates SASL authentication mechanisms.\n
 *\n
 *  User code may override the priority for each mechanism or disable it completely.\n
 *  See \074priority\076 for information about changing priority and \074test\076 for informatian on\n
 *  how to disable a mechanism.\n
 *\n
 *  By default, all mechanisms are enabled and the priorities are\n
 *\n
 *  SCRAM-SHA1 - 40\n
 *  DIGEST-MD5 - 30\n
 *  Plain - 20\n
 */\n
\n
/**\n
 * PrivateConstructor: Strophe.SASLMechanism\n
 * SASL auth mechanism abstraction.\n
 *\n
 *  Parameters:\n
 *    (String) name - SASL Mechanism name.\n
 *    (Boolean) isClientFirst - If client should send response first without challenge.\n
 *    (Number) priority - Priority.\n
 *\n
 *  Returns:\n
 *    A new Strophe.SASLMechanism object.\n
 */\n
Strophe.SASLMechanism = function(name, isClientFirst, priority) {\n
  /** PrivateVariable: name\n
   *  Mechanism name.\n
   */\n
  this.name = name;\n
  /** PrivateVariable: isClientFirst\n
   *  If client sends response without initial server challenge.\n
   */\n
  this.isClientFirst = isClientFirst;\n
  /** Variable: priority\n
   *  Determines which \074SASLMechanism\076 is chosen for authentication (Higher is better).\n
   *  Users may override this to prioritize mechanisms differently.\n
   *\n
   *  In the default configuration the priorities are\n
   *\n
   *  SCRAM-SHA1 - 40\n
   *  DIGEST-MD5 - 30\n
   *  Plain - 20\n
   *\n
   *  Example: (This will cause Strophe to choose the mechanism that the server sent first)\n
   *\n
   *  \076 Strophe.SASLMD5.priority = Strophe.SASLSHA1.priority;\n
   *\n
   *  See \074SASL mechanisms\076 for a list of available mechanisms.\n
   *\n
   */\n
  this.priority = priority;\n
};\n
\n
Strophe.SASLMechanism.prototype = {\n
  /**\n
   *  Function: test\n
   *  Checks if mechanism able to run.\n
   *  To disable a mechanism, make this return false;\n
   *\n
   *  To disable plain authentication run\n
   *  \076 Strophe.SASLPlain.test = function() {\n
   *  \076   return false;\n
   *  \076 }\n
   *\n
   *  See \074SASL mechanisms\076 for a list of available mechanisms.\n
   *\n
   *  Parameters:\n
   *    (Strophe.Connection) connection - Target Connection.\n
   *\n
   *  Returns:\n
   *    (Boolean) If mechanism was able to run.\n
   */\n
  /* jshint unused:false */\n
  test: function(connection) {\n
    return true;\n
  },\n
  /* jshint unused:true */\n
\n
  /** PrivateFunction: onStart\n
   *  Called before starting mechanism on some connection.\n
   *\n
   *  Parameters:\n
   *    (Strophe.Connection) connection - Target Connection.\n
   */\n
  onStart: function(connection)\n
  {\n
    this._connection = connection;\n
  },\n
\n
  /** PrivateFunction: onChallenge\n
   *  Called by protocol implementation on incoming challenge. If client is\n
   *  first (isClientFirst == true) challenge will be null on the first call.\n
   *\n
   *  Parameters:\n
   *    (Strophe.Connection) connection - Target Connection.\n
   *    (String) challenge - current challenge to handle.\n
   *\n
   *  Returns:\n
   *    (String) Mechanism response.\n
   */\n
  /* jshint unused:false */\n
  onChallenge: function(connection, challenge) {\n
    throw new Error("You should implement challenge handling!");\n
  },\n
  /* jshint unused:true */\n
\n
  /** PrivateFunction: onFailure\n
   *  Protocol informs mechanism implementation about SASL failure.\n
   */\n
  onFailure: function() {\n
    this._connection = null;\n
  },\n
\n
  /** PrivateFunction: onSuccess\n
   *  Protocol informs mechanism implementation about SASL success.\n
   */\n
  onSuccess: function() {\n
    this._connection = null;\n
  }\n
};\n
\n
  /** Constants: SASL mechanisms\n
   *  Available authentication mechanisms\n
   *\n
   *  Strophe.SASLAnonymous - SASL Anonymous authentication.\n
   *  Strophe.SASLPlain - SASL Plain authentication.\n
   *  Strophe.SASLMD5 - SASL Digest-MD5 authentication\n
   *  Strophe.SASLSHA1 - SASL SCRAM-SHA1 authentication\n
   */\n
\n
// Building SASL callbacks\n
\n
/** PrivateConstructor: SASLAnonymous\n
 *  SASL Anonymous authentication.\n
 */\n
Strophe.SASLAnonymous = function() {};\n
\n
Strophe.SASLAnonymous.prototype = new Strophe.SASLMechanism("ANONYMOUS", false, 10);\n
\n
Strophe.SASLAnonymous.test = function(connection) {\n
  return connection.authcid === null;\n
};\n
\n
Strophe.Connection.prototype.mechanisms[Strophe.SASLAnonymous.prototype.name] = Strophe.SASLAnonymous;\n
\n
/** PrivateConstructor: SASLPlain\n
 *  SASL Plain authentication.\n
 */\n
Strophe.SASLPlain = function() {};\n
\n
Strophe.SASLPlain.prototype = new Strophe.SASLMechanism("PLAIN", true, 20);\n
\n
Strophe.SASLPlain.test = function(connection) {\n
  return connection.authcid !== null;\n
};\n
\n
Strophe.SASLPlain.prototype.onChallenge = function(connection) {\n
  var auth_str = connection.authzid;\n
  auth_str = auth_str + "\\u0000";\n
  auth_str = auth_str + connection.authcid;\n
  auth_str = auth_str + "\\u0000";\n
  auth_str = auth_str + connection.pass;\n
  return auth_str;\n
};\n
\n
Strophe.Connection.prototype.mechanisms[Strophe.SASLPlain.prototype.name] = Strophe.SASLPlain;\n
\n
/** PrivateConstructor: SASLSHA1\n
 *  SASL SCRAM SHA 1 authentication.\n
 */\n
Strophe.SASLSHA1 = function() {};\n
\n
/* TEST:\n
 * This is a simple example of a SCRAM-SHA-1 authentication exchange\n
 * when the client doesn\'t support channel bindings (username \'user\' and\n
 * password \'pencil\' are used):\n
 *\n
 * C: n,,n=user,r=fyko+d2lbbFgONRv9qkxdawL\n
 * S: r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j,s=QSXCR+Q6sek8bf92,\n
 * i=4096\n
 * C: c=biws,r=fyko+d2lbbFgONRv9qkxdawL3rfcNHYJY1ZVvWVs7j,\n
 * p=v0X8v3Bz2T0CJGbJQyF0X+HI4Ts=\n
 * S: v=rmF9pqV8S7suAoZWja4dJRkFsKQ=\n
 *\n
 */\n
\n
Strophe.SASLSHA1.prototype = new Strophe.SASLMechanism("SCRAM-SHA-1", true, 40);\n
\n
Strophe.SASLSHA1.test = function(connection) {\n
  return connection.authcid !== null;\n
};\n
\n
Strophe.SASLSHA1.prototype.onChallenge = function(connection, challenge, test_cnonce) {\n
  var cnonce = test_cnonce || MD5.hexdigest(Math.random() * 1234567890);\n
\n
  var auth_str = "n=" + connection.authcid;\n
  auth_str += ",r=";\n
  auth_str += cnonce;\n
\n
  connection._sasl_data.cnonce = cnonce;\n
  connection._sasl_data["client-first-message-bare"] = auth_str;\n
\n
  auth_str = "n,," + auth_str;\n
\n
  this.onChallenge = function (connection, challenge)\n
  {\n
    var nonce, salt, iter, Hi, U, U_old, i, k;\n
    var clientKey, serverKey, clientSignature;\n
    var responseText = "c=biws,";\n
    var authMessage = connection._sasl_data["client-first-message-bare"] + "," +\n
      challenge + ",";\n
    var cnonce = connection._sasl_data.cnonce;\n
    var attribMatch = /([a-z]+)=([^,]+)(,|$)/;\n
\n
    while (challenge.match(attribMatch)) {\n
      var matches = challenge.match(attribMatch);\n
      challenge = challenge.replace(matches[0], "");\n
      switch (matches[1]) {\n
      case "r":\n
        nonce = matches[2];\n
        break;\n
      case "s":\n
        salt = matches[2];\n
        break;\n
      case "i":\n
        iter = matches[2];\n
        break;\n
      }\n
    }\n
\n
    if (nonce.substr(0, cnonce.length) !== cnonce) {\n
      connection._sasl_data = {};\n
      return connection._sasl_failure_cb();\n
    }\n
\n
    responseText += "r=" + nonce;\n
    authMessage += responseText;\n
\n
    salt = Base64.decode(salt);\n
    salt += "\\x00\\x00\\x00\\x01";\n
\n
    Hi = U_old = core_hmac_sha1(connection.pass, salt);\n
    for (i = 1; i \074 iter; i++) {\n
      U = core_hmac_sha1(connection.pass, binb2str(U_old));\n
      for (k = 0; k \074 5; k++) {\n
        Hi[k] ^= U[k];\n
      }\n
      U_old = U;\n
    }\n
    Hi = binb2str(Hi);\n
\n
    clientKey = core_hmac_sha1(Hi, "Client Key");\n
    serverKey = str_hmac_sha1(Hi, "Server Key");\n
    clientSignature = core_hmac_sha1(str_sha1(binb2str(clientKey)), authMessage);\n
    connection._sasl_data["server-signature"] = b64_hmac_sha1(serverKey, authMessage);\n
\n
    for (k = 0; k \074 5; k++) {\n
      clientKey[k] ^= clientSignature[k];\n
    }\n
\n
    responseText += ",p=" + Base64.encode(binb2str(clientKey));\n
\n
    return responseText;\n
  }.bind(this);\n
\n
  return auth_str;\n
};\n
\n
Strophe.Connection.prototype.mechanisms[Strophe.SASLSHA1.prototype.name] = Strophe.SASLSHA1;\n
\n
/** PrivateConstructor: SASLMD5\n
 *  SASL DIGEST MD5 authentication.\n
 */\n
Strophe.SASLMD5 = function() {};\n
\n
Strophe.SASLMD5.prototype = new Strophe.SASLMechanism("DIGEST-MD5", false, 30);\n
\n
Strophe.SASLMD5.test = function(connection) {\n
  return connection.authcid !== null;\n
};\n
\n
/** PrivateFunction: _quote\n
 *  _Private_ utility function to backslash escape and quote strings.\n
 *\n
 *  Parameters:\n
 *    (String) str - The string to be quoted.\n
 *\n
 *  Returns:\n
 *    quoted string\n
 */\n
Strophe.SASLMD5.prototype._quote = function (str)\n
  {\n
    return \'"\' + str.replace(/\\\\/g, "\\\\\\\\").replace(/"/g, \'\\\\"\') + \'"\';\n
    //" end string workaround for emacs\n
  };\n
\n
\n
Strophe.SASLMD5.prototype.onChallenge = function(connection, challenge, test_cnonce) {\n
  var attribMatch = /([a-z]+)=("[^"]+"|[^,"]+)(?:,|$)/;\n
  var cnonce = test_cnonce || MD5.hexdigest("" + (Math.random() * 1234567890));\n
  var realm = "";\n
  var host = null;\n
  var nonce = "";\n
  var qop = "";\n
  var matches;\n
\n
  while (challenge.match(attribMatch)) {\n
    matches = challenge.match(attribMatch);\n
    challenge = challenge.replace(matches[0], "");\n
    matches[2] = matches[2].replace(/^"(.+)"$/, "$1");\n
    switch (matches[1]) {\n
    case "realm":\n
      realm = matches[2];\n
      break;\n
    case "nonce":\n
      nonce = matches[2];\n
      break;\n
    case "qop":\n
      qop = matches[2];\n
      break;\n
    case "host":\n
      host = matches[2];\n
      break;\n
    }\n
  }\n
\n
  var digest_uri = connection.servtype + "/" + connection.domain;\n
  if (host !== null) {\n
    digest_uri = digest_uri + "/" + host;\n
  }\n
\n
  var A1 = MD5.hash(connection.authcid +\n
                    ":" + realm + ":" + this._connection.pass) +\n
    ":" + nonce + ":" + cnonce;\n
  var A2 = \'AUTHENTICATE:\' + digest_uri;\n
\n
  var responseText = "";\n
  responseText += \'charset=utf-8,\';\n
  responseText += \'username=\' +\n
    this._quote(connection.authcid) + \',\';\n
  responseText += \'realm=\' + this._quote(realm) + \',\';\n
  responseText += \'nonce=\' + this._quote(nonce) + \',\';\n
  responseText += \'nc=00000001,\';\n
  responseText += \'cnonce=\' + this._quote(cnonce) + \',\';\n
  responseText += \'digest-uri=\' + this._quote(digest_uri) + \',\';\n
  responseText += \'response=\' + MD5.hexdigest(MD5.hexdigest(A1) + ":" +\n
                                              nonce + ":00000001:" +\n
                                              cnonce + ":auth:" +\n
                                              MD5.hexdigest(A2)) + ",";\n
  responseText += \'qop=auth\';\n
\n
  this.onChallenge = function ()\n
  {\n
    return "";\n
  }.bind(this);\n
\n
  return responseText;\n
};\n
\n
Strophe.Connection.prototype.mechanisms[Strophe.SASLMD5.prototype.name] = Strophe.SASLMD5;\n
\n
})(function () {\n
    window.Strophe = arguments[0];\n
    window.$build = arguments[1];\n
    window.$msg = arguments[2];\n
    window.$iq = arguments[3];\n
    window.$pres = arguments[4];\n
});\n
\n
/*\n
    This program is distributed under the terms of the MIT license.\n
    Please see the LICENSE file for details.\n
\n
    Copyright 2006-2008, OGG, LLC\n
*/\n
\n
/* jshint undef: true, unused: true:, noarg: true, latedef: true */\n
/*global window, setTimeout, clearTimeout,\n
    XMLHttpRequest, ActiveXObject,\n
    Strophe, $build */\n
\n
\n
/** PrivateClass: Strophe.Request\n
 *  _Private_ helper class that provides a cross implementation abstraction\n
 *  for a BOSH related XMLHttpRequest.\n
 *\n
 *  The Strophe.Request class is used internally to encapsulate BOSH request\n
 *  information.  It is not meant to be used from user\'s code.\n
 */\n
\n
/** PrivateConstructor: Strophe.Request\n
 *  Create and initialize a new Strophe.Request object.\n
 *\n
 *  Parameters:\n
 *    (XMLElement) elem - The XML data to be sent in the request.\n
 *    (Function) func - The function that will be called when the\n
 *      XMLHttpRequest readyState changes.\n
 *    (Integer) rid - The BOSH rid attribute associated with this request.\n
 *    (Integer) sends - The number of times this same request has been\n
 *      sent.\n
 */\n
Strophe.Request = function (elem, func, rid, sends)\n
{\n
    this.id = ++Strophe._requestId;\n
    this.xmlData = elem;\n
    this.data = Strophe.serialize(elem);\n
    // save original function in case we need to make a new request\n
    // from this one.\n
    this.origFunc = func;\n
    this.func = func;\n
    this.rid = rid;\n
    this.date = NaN;\n
    this.sends = sends || 0;\n
    this.abort = false;\n
    this.dead = null;\n
\n
    this.age = function () {\n
        if (!this.date) { return 0; }\n
        var now = new Date();\n
        return (now - this.date) / 1000;\n
    };\n
    this.timeDead = function () {\n
        if (!this.dead) { return 0; }\n
        var now = new Date();\n
        return (now - this.dead) / 1000;\n
    };\n
    this.xhr = this._newXHR();\n
};\n
\n
Strophe.Request.prototype = {\n
    /** PrivateFunction: getResponse\n
     *  Get a response from the underlying XMLHttpRequest.\n
     *\n
     *  This function attempts to get a response from the request and checks\n
     *  for errors.\n
     *\n
     *  Throws:\n
     *    "parsererror" - A parser error occured.\n
     *\n
     *  Returns:\n
     *    The DOM element tree of the response.\n
     */\n
    getResponse: function ()\n
    {\n
        var node = null;\n
        if (this.xhr.responseXML \046\046 this.xhr.responseXML.documentElement) {\n
            node = this.xhr.responseXML.documentElement;\n
            if (node.tagName == "parsererror") {\n
                Strophe.error("invalid response received");\n
                Strophe.error("responseText: " + this.xhr.responseText);\n
                Strophe.error("responseXML: " +\n
                              Strophe.serialize(this.xhr.responseXML));\n
                throw "parsererror";\n
            }\n
        } else if (this.xhr.responseText) {\n
            Strophe.error("invalid response received");\n
            Strophe.error("responseText: " + this.xhr.responseText);\n
            Strophe.error("responseXML: " +\n
                          Strophe.serialize(this.xhr.responseXML));\n
        }\n
\n
        return node;\n
    },\n
\n
    /** PrivateFunction: _newXHR\n
     *  _Private_ helper function to create XMLHttpRequests.\n
     *\n
     *  This function creates XMLHttpRequests across all implementations.\n
     *\n
     *  Returns:\n
     *    A new XMLHttpRequest.\n
     */\n
    _newXHR: function ()\n
    {\n
        var xhr = null;\n
        if (window.XMLHttpRequest) {\n
            xhr = new XMLHttpRequest();\n
            if (xhr.overrideMimeType) {\n
                xhr.overrideMimeType("text/xml");\n
            }\n
        } else if (window.ActiveXObject) {\n
            xhr = new ActiveXObject("Microsoft.XMLHTTP");\n
        }\n
\n
        // use Function.bind() to prepend ourselves as an argument\n
        xhr.onreadystatechange = this.func.bind(null, this);\n
\n
        return xhr;\n
    }\n
};\n
\n
/** Class: Strophe.Bosh\n
 *  _Private_ helper class that handles BOSH Connections\n
 *\n
 *  The Strophe.Bosh class is used internally by Strophe.Connection\n
 *  to encapsulate BOSH sessions. It is not meant to be used from user\'s code.\n
 */\n
\n
/** File: bosh.js\n
 *  A JavaScript library to enable BOSH in Strophejs.\n
 *\n
 *  this library uses Bidirectional-streams Over Synchronous HTTP (BOSH)\n
 *  to emulate a persistent, stateful, two-way connection to an XMPP server.\n
 *  More information on BOSH can be found in XEP 124.\n
 */\n
\n
/** PrivateConstructor: Strophe.Bosh\n
 *  Create and initialize a Strophe.Bosh object.\n
 *\n
 *  Parameters:\n
 *    (Strophe.Connection) connection - The Strophe.Connection that will use BOSH.\n
 *\n
 *  Returns:\n
 *    A new Strophe.Bosh object.\n
 */\n
Strophe.Bosh = function(connection) {\n
    this._conn = connection;\n
    /* request id for body tags */\n
    this.rid = Math.floor(Math.random() * 4294967295);\n
    /* The current session ID. */\n
    this.sid = null;\n
\n
    // default BOSH values\n
    this.hold = 1;\n
    this.wait = 60;\n
    this.window = 5;\n
\n
    this._requests = [];\n
};\n
\n
Strophe.Bosh.prototype = {\n
    /** Variable: strip\n
     *\n
     *  BOSH-Connections will have all stanzas wrapped in a \074body\076 tag when\n
     *  passed to \074Strophe.Connection.xmlInput\076 or \074Strophe.Connection.xmlOutput\076.\n
     *  To strip this tag, User code can set \074Strophe.Bosh.strip\076 to "body":\n
     *\n
     *  \076 Strophe.Bosh.prototype.strip = "body";\n
     *\n
     *  This will enable stripping of the body tag in both\n
     *  \074Strophe.Connection.xmlInput\076 and \074Strophe.Connection.xmlOutput\076.\n
     */\n
    strip: null,\n
\n
    /** PrivateFunction: _buildBody\n
     *  _Private_ helper function to generate the \074body/\076 wrapper for BOSH.\n
     *\n
     *  Returns:\n
     *    A Strophe.Builder with a \074body/\076 element.\n
     */\n
    _buildBody: function ()\n
    {\n
        var bodyWrap = $build(\'body\', {\n
            rid: this.rid++,\n
            xmlns: Strophe.NS.HTTPBIND\n
        });\n
\n
        if (this.sid !== null) {\n
            bodyWrap.attrs({sid: this.sid});\n
        }\n
\n
        return bodyWrap;\n
    },\n
\n
    /** PrivateFunction: _reset\n
     *  Reset the connection.\n
     *\n
     *  This function is called by the reset function of the Strophe Connection\n
     */\n
    _reset: function ()\n
    {\n
        this.rid = Math.floor(Math.random() * 4294967295);\n
        this.sid = null;\n
    },\n
\n
    /** PrivateFunction: _connect\n
     *  _Private_ function that initializes the BOSH connection.\n
     *\n
     *  Creates and sends the Request that initializes the BOSH connection.\n
     */\n
    _connect: function (wait, hold, route)\n
    {\n
        this.wait = wait || this.wait;\n
        this.hold = hold || this.hold;\n
\n
        // build the body tag\n
        var body = this._buildBody().attrs({\n
            to: this._conn.domain,\n
            "xml:lang": "en",\n
            wait: this.wait,\n
            hold: this.hold,\n
            content: "text/xml; charset=utf-8",\n
            ver: "1.6",\n
            "xmpp:version": "1.0",\n
            "xmlns:xmpp": Strophe.NS.BOSH\n
        });\n
\n
        if(route){\n
            body.attrs({\n
                route: route\n
            });\n
        }\n
\n
        var _connect_cb = this._conn._connect_cb;\n
\n
        this._requests.push(\n
            new Strophe.Request(body.tree(),\n
                                this._onRequestStateChange.bind(\n
                                    this, _connect_cb.bind(this._conn)),\n
                                body.tree().getAttribute("rid")));\n
        this._throttledRequestHandler();\n
    },\n
\n
    /** PrivateFunction: _attach\n
     *  Attach to an already created and authenticated BOSH session.\n
     *\n
     *  This function is provided to allow Strophe to attach to BOSH\n
     *  sessions which have been created externally, perhaps by a Web\n
     *  application.  This is often used to support auto-login type features\n
     *  without putting user credentials into the page.\n
     *\n
     *  Parameters:\n
     *    (String) jid - The full JID that is bound by the session.\n
     *    (String) sid - The SID of the BOSH session.\n
     *    (String) rid - The current RID of the BOSH session.  This RID\n
     *      will be used by the next request.\n
     *    (Function) callback The connect callback function.\n
     *    (Integer) wait - The optional HTTPBIND wait value.  This is the\n
     *      time the server will wait before returning an empty result for\n
     *      a request.  The default setting of 60 seconds is recommended.\n
     *      Other settings will require tweaks to the Strophe.TIMEOUT value.\n
     *    (Integer) hold - The optional HTTPBIND hold value.  This is the\n
     *      number of connections the server will hold at one time.  This\n
     *      should almost always be set to 1 (the default).\n
     *    (Integer) wind - The optional HTTBIND window value.  This is the\n
     *      allowed range of request ids that are valid.  The default is 5.\n
     */\n
    _attach: function (jid, sid, rid, callback, wait, hold, wind)\n
    {\n
        this._conn.jid = jid;\n
        this.sid = sid;\n
        this.rid = rid;\n
\n
        this._conn.connect_callback = callback;\n
\n
        this._conn.domain = Strophe.getDomainFromJid(this._conn.jid);\n
\n
        this._conn.authenticated = true;\n
        this._conn.connected = true;\n
\n
        this.wait = wait || this.wait;\n
        this.hold = hold || this.hold;\n
        this.window = wind || this.window;\n
\n
        this._conn._changeConnectStatus(Strophe.Status.ATTACHED, null);\n
    },\n
\n
    /** PrivateFunction: _connect_cb\n
     *  _Private_ handler for initial connection request.\n
     *\n
     *  This handler is used to process the Bosh-part of the initial request.\n
     *  Parameters:\n
     *    (Strophe.Request) bodyWrap - The received stanza.\n
     */\n
    _connect_cb: function (bodyWrap)\n
    {\n
        var typ = bodyWrap.getAttribute("type");\n
        var cond, conflict;\n
        if (typ !== null \046\046 typ == "terminate") {\n
            // an error occurred\n
            Strophe.error("BOSH-Connection failed: " + cond);\n
            cond = bodyWrap.getAttribute("condition");\n
            conflict = bodyWrap.getElementsByTagName("conflict");\n
            if (cond !== null) {\n
                if (cond == "remote-stream-error" \046\046 conflict.length \076 0) {\n
                    cond = "conflict";\n
                }\n
                this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, cond);\n
            } else {\n
                this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, "unknown");\n
            }\n
            this._conn._doDisconnect();\n
            return Strophe.Status.CONNFAIL;\n
        }\n
\n
        // check to make sure we don\'t overwrite these if _connect_cb is\n
        // called multiple times in the case of missing stream:features\n
        if (!this.sid) {\n
            this.sid = bodyWrap.getAttribute("sid");\n
        }\n
        var wind = bodyWrap.getAttribute(\'requests\');\n
        if (wind) { this.window = parseInt(wind, 10); }\n
        var hold = bodyWrap.getAttribute(\'hold\');\n
        if (hold) { this.hold = parseInt(hold, 10); }\n
        var wait = bodyWrap.getAttribute(\'wait\');\n
        if (wait) { this.wait = parseInt(wait, 10); }\n
    },\n
\n
    /** PrivateFunction: _disconnect\n
     *  _Private_ part of Connection.disconnect for Bosh\n
     *\n
     *  Parameters:\n
     *    (Request) pres - This stanza will be sent before disconnecting.\n
     */\n
    _disconnect: function (pres)\n
    {\n
        this._sendTerminate(pres);\n
    },\n
\n
    /** PrivateFunction: _doDisconnect\n
     *  _Private_ function to disconnect.\n
     *\n
     *  Resets the SID and RID.\n
     */\n
    _doDisconnect: function ()\n
    {\n
        this.sid = null;\n
        this.rid = Math.floor(Math.random() * 4294967295);\n
    },\n
\n
    /** PrivateFunction: _emptyQueue\n
     * _Private_ function to check if the Request queue is empty.\n
     *\n
     *  Returns:\n
     *    True, if there are no Requests queued, False otherwise.\n
     */\n
    _emptyQueue: function ()\n
    {\n
        return this._requests.length === 0;\n
    },\n
\n
    /** PrivateFunction: _hitError\n
     *  _Private_ function to handle the error count.\n
     *\n
     *  Requests are resent automatically until their error count reaches\n
     *  5.  Each time an error is encountered, this function is called to\n
     *  increment the count and disconnect if the count is too high.\n
     *\n
     *  Parameters:\n
     *    (Integer) reqStatus - The request status.\n
     */\n
    _hitError: function (reqStatus)\n
    {\n
        this.errors++;\n
        Strophe.warn("request errored, status: " + reqStatus +\n
                     ", number of errors: " + this.errors);\n
        if (this.errors \076 4) {\n
            this._onDisconnectTimeout();\n
        }\n
    },\n
\n
    /** PrivateFunction: _no_auth_received\n
     *\n
     * Called on stream start/restart when no stream:features\n
     * has been received and sends a blank poll request.\n
     */\n
    _no_auth_received: function (_callback)\n
    {\n
        if (_callback) {\n
            _callback = _callback.bind(this._conn);\n
        } else {\n
            _callback = this._conn._connect_cb.bind(this._conn);\n
        }\n
        var body = this._buildBody();\n
        this._requests.push(\n
                new Strophe.Request(body.tree(),\n
                    this._onRequestStateChange.bind(\n
                        this, _callback.bind(this._conn)),\n
                    body.tree().getAttribute("rid")));\n
        this._throttledRequestHandler();\n
    },\n
\n
    /** PrivateFunction: _onDisconnectTimeout\n
     *  _Private_ timeout handler for handling non-graceful disconnection.\n
     *\n
     *  Cancels all remaining Requests and clears the queue.\n
     */\n
    _onDisconnectTimeout: function ()\n
    {\n
        var req;\n
        while (this._requests.length \076 0) {\n
            req = this._requests.pop();\n
            req.abort = true;\n
            req.xhr.abort();\n
            // jslint complains, but this is fine. setting to empty func\n
            // is necessary for IE6\n
            req.xhr.onreadystatechange = function () {}; // jshint ignore:line\n
        }\n
    },\n
\n
    /** PrivateFunction: _onIdle\n
     *  _Private_ handler called by Strophe.Connection._onIdle\n
     *\n
     *  Sends all queued Requests or polls with empty Request if there are none.\n
     */\n
    _onIdle: function () {\n
        var data = this._conn._data;\n
\n
        // if no requests are in progress, poll\n
        if (this._conn.authenticated \046\046 this._requests.length === 0 \046\046\n
            data.length === 0 \046\046 !this._conn.disconnecting) {\n
            Strophe.info("no requests during idle cycle, sending " +\n
                         "blank request");\n
            data.push(null);\n
        }\n
\n
        if (this._requests.length \074 2 \046\046 data.length \076 0 \046\046\n
            !this._conn.paused) {\n
            var body = this._buildBody();\n
            for (var i = 0; i \074 data.length; i++) {\n
                if (data[i] !== null) {\n
                    if (data[i] === "restart") {\n
                        body.attrs({\n
                            to: this._conn.domain,\n
                            "xml:lang": "en",\n
                            "xmpp:restart": "true",\n
                            "xmlns:xmpp": Strophe.NS.BOSH\n
                        });\n
                    } else {\n
                        body.cnode(data[i]).up();\n
                    }\n
                }\n
            }\n
            delete this._conn._data;\n
            this._conn._data = [];\n
            this._requests.push(\n
                new Strophe.Request(body.tree(),\n
                                    this._onRequestStateChange.bind(\n
                                        this, this._conn._dataRecv.bind(this._conn)),\n
                                    body.tree().getAttribute("rid")));\n
            this._processRequest(this._requests.length - 1);\n
        }\n
\n
        if (this._requests.length \076 0) {\n
            var time_elapsed = this._requests[0].age();\n
            if (this._requests[0].dead !== null) {\n
                if (this._requests[0].timeDead() \076\n
                    Math.floor(Strophe.SECONDARY_TIMEOUT * this.wait)) {\n
                    this._throttledRequestHandler();\n
                }\n
            }\n
\n
            if (time_elapsed \076 Math.floor(Strophe.TIMEOUT * this.wait)) {\n
                Strophe.warn("Request " +\n
                             this._requests[0].id +\n
                             " timed out, over " + Math.floor(Strophe.TIMEOUT * this.wait) +\n
                             " seconds since last activity");\n
                this._throttledRequestHandler();\n
            }\n
        }\n
    },\n
\n
    /** PrivateFunction: _onRequestStateChange\n
     *  _Private_ handler for Strophe.Request state changes.\n
     *\n
     *  This function is called when the XMLHttpRequest readyState changes.\n
     *  It contains a lot of error handling logic for the many ways that\n
     *  requests can fail, and calls the request callback when requests\n
     *  succeed.\n
     *\n
     *  Parameters:\n
     *    (Function) func - The handler for the request.\n
     *    (Strophe.Request) req - The request that is changing readyState.\n
     */\n
    _onRequestStateChange: function (func, req)\n
    {\n
        Strophe.debug("request id " + req.id +\n
                      "." + req.sends + " state changed to " +\n
                      req.xhr.readyState);\n
\n
        if (req.abort) {\n
            req.abort = false;\n
            return;\n
        }\n
\n
        // request complete\n
        var reqStatus;\n
        if (req.xhr.readyState == 4) {\n
            reqStatus = 0;\n
            try {\n
                reqStatus = req.xhr.status;\n
            } catch (e) {\n
                // ignore errors from undefined status attribute.  works\n
                // around a browser bug\n
            }\n
\n
            if (typeof(reqStatus) == "undefined") {\n
                reqStatus = 0;\n
            }\n
\n
            if (this.disconnecting) {\n
                if (reqStatus \076= 400) {\n
                    this._hitError(reqStatus);\n
                    return;\n
                }\n
            }\n
\n
            var reqIs0 = (this._requests[0] == req);\n
            var reqIs1 = (this._requests[1] == req);\n
\n
            if ((reqStatus \076 0 \046\046 reqStatus \074 500) || req.sends \076 5) {\n
                // remove from internal queue\n
                this._removeRequest(req);\n
                Strophe.debug("request id " +\n
                              req.id +\n
                              " should now be removed");\n
            }\n
\n
            // request succeeded\n
            if (reqStatus == 200) {\n
                // if request 1 finished, or request 0 finished and request\n
                // 1 is over Strophe.SECONDARY_TIMEOUT seconds old, we need to\n
                // restart the other - both will be in the first spot, as the\n
                // completed request has been removed from the queue already\n
                if (reqIs1 ||\n
                    (reqIs0 \046\046 this._requests.length \076 0 \046\046\n
                     this._requests[0].age() \076 Math.floor(Strophe.SECONDARY_TIMEOUT * this.wait))) {\n
                    this._restartRequest(0);\n
                }\n
                // call handler\n
                Strophe.debug("request id " +\n
                              req.id + "." +\n
                              req.sends + " got 200");\n
                func(req);\n
                this.errors = 0;\n
            } else {\n
                Strophe.error("request id " +\n
                              req.id + "." +\n
                              req.sends + " error " + reqStatus +\n
                              " happened");\n
                if (reqStatus === 0 ||\n
                    (reqStatus \076= 400 \046\046 reqStatus \074 600) ||\n
                    reqStatus \076= 12000) {\n
                    this._hitError(reqStatus);\n
                    if (reqStatus \076= 400 \046\046 reqStatus \074 500) {\n
                        this._conn._changeConnectStatus(Strophe.Status.DISCONNECTING,\n
                                                  null);\n
                        this._conn._doDisconnect();\n
                    }\n
                }\n
            }\n
\n
            if (!((reqStatus \076 0 \046\046 reqStatus \074 500) ||\n
                  req.sends \076 5)) {\n
                this._throttledRequestHandler();\n
            }\n
        }\n
    },\n
\n
    /** PrivateFunction: _processRequest\n
     *  _Private_ function to process a request in the queue.\n
     *\n
     *  This function takes requests off the queue and sends them and\n
     *  restarts dead requests.\n
     *\n
     *  Parameters:\n
     *    (Integer) i - The index of the request in the queue.\n
     */\n
    _processRequest: function (i)\n
    {\n
        var self = this;\n
        var req = this._requests[i];\n
        var reqStatus = -1;\n
\n
        try {\n
            if (req.xhr.readyState == 4) {\n
                reqStatus = req.xhr.status;\n
            }\n
        } catch (e) {\n
            Strophe.error("caught an error in _requests[" + i +\n
                          "], reqStatus: " + reqStatus);\n
        }\n
\n
        if (typeof(reqStatus) == "undefined") {\n
            reqStatus = -1;\n
        }\n
\n
        // make sure we limit the number of retries\n
        if (req.sends \076 this.maxRetries) {\n
            this._onDisconnectTimeout();\n
            return;\n
        }\n
\n
        var time_elapsed = req.age();\n
        var primaryTimeout = (!isNaN(time_elapsed) \046\046\n
                              time_elapsed \076 Math.floor(Strophe.TIMEOUT * this.wait));\n
        var secondaryTimeout = (req.dead !== null \046\046\n
                                req.timeDead() \076 Math.floor(Strophe.SECONDARY_TIMEOUT * this.wait));\n
        var requestCompletedWithServerError = (req.xhr.readyState == 4 \046\046\n
                                               (reqStatus \074 1 ||\n
                                                reqStatus \076= 500));\n
        if (primaryTimeout || secondaryTimeout ||\n
            requestCompletedWithServerError) {\n
            if (secondaryTimeout) {\n
                Strophe.error("Request " +\n
                              this._requests[i].id +\n
                              " timed out (secondary), restarting");\n
            }\n
            req.abort = true;\n
            req.xhr.abort();\n
            // setting to null fails on IE6, so set to empty function\n
            req.xhr.onreadystatechange = function () {};\n
            this._requests[i] = new Strophe.Request(req.xmlData,\n
                                                    req.origFunc,\n
                                                    req.rid,\n
                                                    req.sends);\n
            req = this._requests[i];\n
        }\n
\n
        if (req.xhr.readyState === 0) {\n
            Strophe.debug("request id " + req.id +\n
                          "." + req.sends + " posting");\n
\n
            try {\n
                req.xhr.open("POST", this._conn.service, this._conn.options.sync ? false : true);\n
            } catch (e2) {\n
                Strophe.error("XHR open failed.");\n
                if (!this._conn.connected) {\n
                    this._conn._changeConnectStatus(Strophe.Status.CONNFAIL,\n
                                              "bad-service");\n
                }\n
                this._conn.disconnect();\n
                return;\n
            }\n
\n
            // Fires the XHR request -- may be invoked immediately\n
            // or on a gradually expanding retry window for reconnects\n
            var sendFunc = function () {\n
                req.date = new Date();\n
                if (self._conn.options.customHeaders){\n
                    var headers = self._conn.options.customHeaders;\n
                    for (var header in headers) {\n
                        if (headers.hasOwnProperty(header)) {\n
                            req.xhr.setRequestHeader(header, headers[header]);\n
                        }\n
                    }\n
                }\n
                req.xhr.send(req.data);\n
            };\n
\n
            // Implement progressive backoff for reconnects --\n
            // First retry (send == 1) should also be instantaneous\n
            if (req.sends \076 1) {\n
                // Using a cube of the retry number creates a nicely\n
                // expanding retry window\n
                var backoff = Math.min(Math.floor(Strophe.TIMEOUT * this.wait),\n
                                       Math.pow(req.sends, 3)) * 1000;\n
                setTimeout(sendFunc, backoff);\n
            } else {\n
                sendFunc();\n
            }\n
\n
            req.sends++;\n
\n
            if (this._conn.xmlOutput !== Strophe.Connection.prototype.xmlOutput) {\n
                if (req.xmlData.nodeName === this.strip \046\046 req.xmlData.childNodes.length) {\n
                    this._conn.xmlOutput(req.xmlData.childNodes[0]);\n
                } else {\n
                    this._conn.xmlOutput(req.xmlData);\n
                }\n
            }\n
            if (this._conn.rawOutput !== Strophe.Connection.prototype.rawOutput) {\n
                this._conn.rawOutput(req.data);\n
            }\n
        } else {\n
            Strophe.debug("_processRequest: " +\n
                          (i === 0 ? "first" : "second") +\n
                          " request has readyState of " +\n
                          req.xhr.readyState);\n
        }\n
    },\n
\n
    /** PrivateFunction: _removeRequest\n
     *  _Private_ function to remove a request from the queue.\n
     *\n
     *  Parameters:\n
     *    (Strophe.Request) req - The request to remove.\n
     */\n
    _removeRequest: function (req)\n
    {\n
        Strophe.debug("removing request");\n
\n
        var i;\n
        for (i = this._requests.length - 1; i \076= 0; i--) {\n
            if (req == this._requests[i]) {\n
                this._requests.splice(i, 1);\n
            }\n
        }\n
\n
        // IE6 fails on setting to null, so set to empty function\n
        req.xhr.onreadystatechange = function () {};\n
\n
        this._throttledRequestHandler();\n
    },\n
\n
    /** PrivateFunction: _restartRequest\n
     *  _Private_ function to restart a request that is presumed dead.\n
     *\n
     *  Parameters:\n
     *    (Integer) i - The index of the request in the queue.\n
     */\n
    _restartRequest: function (i)\n
    {\n
        var req = this._requests[i];\n
        if (req.dead === null) {\n
            req.dead = new Date();\n
        }\n
\n
        this._processRequest(i);\n
    },\n
\n
    /** PrivateFunction: _reqToData\n
     * _Private_ function to get a stanza out of a request.\n
     *\n
     * Tries to extract a stanza out of a Request Object.\n
     * When this fails the current connection will be disconnected.\n
     *\n
     *  Parameters:\n
     *    (Object) req - The Request.\n
     *\n
     *  Returns:\n
     *    The stanza that was passed.\n
     */\n
    _reqToData: function (req)\n
    {\n
        try {\n
            return req.getResponse();\n
        } catch (e) {\n
            if (e != "parsererror") { throw e; }\n
            this._conn.disconnect("strophe-parsererror");\n
        }\n
    },\n
\n
    /** PrivateFunction: _sendTerminate\n
     *  _Private_ function to send initial disconnect sequence.\n
     *\n
     *  This is the first step in a graceful disconnect.  It sends\n
     *  the BOSH server a terminate body and includes an unavailable\n
     *  presence if authentication has completed.\n
     */\n
    _sendTerminate: function (pres)\n
    {\n
        Strophe.info("_sendTerminate was called");\n
        var body = this._buildBody().attrs({type: "terminate"});\n
\n
        if (pres) {\n
            body.cnode(pres.tree());\n
        }\n
\n
        var req = new Strophe.Request(body.tree(),\n
                                      this._onRequestStateChange.bind(\n
                                          this, this._conn._dataRecv.bind(this._conn)),\n
                                      body.tree().getAttribute("rid"));\n
\n
        this._requests.push(req);\n
        this._throttledRequestHandler();\n
    },\n
\n
    /** PrivateFunction: _send\n
     *  _Private_ part of the Connection.send function for BOSH\n
     *\n
     * Just triggers the RequestHandler to send the messages that are in the queue\n
     */\n
    _send: function () {\n
        clearTimeout(this._conn._idleTimeout);\n
        this._throttledRequestHandler();\n
        this._conn._idleTimeout = setTimeout(this._conn._onIdle.bind(this._conn), 100);\n
    },\n
\n
    /** PrivateFunction: _sendRestart\n
     *\n
     *  Send an xmpp:restart stanza.\n
     */\n
    _sendRestart: function ()\n
    {\n
        this._throttledRequestHandler();\n
        clearTimeout(this._conn._idleTimeout);\n
    },\n
\n
    /** PrivateFunction: _throttledRequestHandler\n
     *  _Private_ function to throttle requests to the connection window.\n
     *\n
     *  This function makes sure we don\'t send requests so fast that the\n
     *  request ids overflow the connection window in the case that one\n
     *  request died.\n
     */\n
    _throttledRequestHandler: function ()\n
    {\n
        if (!this._requests) {\n
            Strophe.debug("_throttledRequestHandler called with " +\n
                          "undefined requests");\n
        } else {\n
            Strophe.debug("_throttledRequestHandler called with " +\n
                          this._requests.length + " requests");\n
        }\n
\n
        if (!this._requests || this._requests.length === 0) {\n
            return;\n
        }\n
\n
        if (this._requests.length \076 0) {\n
            this._processRequest(0);\n
        }\n
\n
        if (this._requests.length \076 1 \046\046\n
            Math.abs(this._requests[0].rid -\n
                     this._requests[1].rid) \074 this.window) {\n
            this._processRequest(1);\n
        }\n
    }\n
};\n
\n
/*\n
    This program is distributed under the terms of the MIT license.\n
    Please see the LICENSE file for details.\n
\n
    Copyright 2006-2008, OGG, LLC\n
*/\n
\n
/* jshint undef: true, unused: true:, noarg: true, latedef: true */\n
/*global document, window, clearTimeout, WebSocket,\n
    DOMParser, Strophe, $build */\n
\n
/** Class: Strophe.WebSocket\n
 *  _Private_ helper class that handles WebSocket Connections\n
 *\n
 *  The Strophe.WebSocket class is used internally by Strophe.Connection\n
 *  to encapsulate WebSocket sessions. It is not meant to be used from user\'s code.\n
 */\n
\n
/** File: websocket.js\n
 *  A JavaScript library to enable XMPP over Websocket in Strophejs.\n
 *\n
 *  This file implements XMPP over WebSockets for Strophejs.\n
 *  If a Connection is established with a Websocket url (ws://...)\n
 *  Strophe will use WebSockets.\n
 *  For more information on XMPP-over WebSocket see this RFC draft:\n
 *  http://tools.ietf.org/html/draft-ietf-xmpp-websocket-00\n
 *\n
 *  WebSocket support implemented by Andreas Guth (andreas.guth@rwth-aachen.de)\n
 */\n
\n
/** PrivateConstructor: Strophe.Websocket\n
 *  Create and initialize a Strophe.WebSocket object.\n
 *  Currently only sets the connection Object.\n
 *\n
 *  Parameters:\n
 *    (Strophe.Connection) connection - The Strophe.Connection that will use WebSockets.\n
 *\n
 *  Returns:\n
 *    A new Strophe.WebSocket object.\n
 */\n
Strophe.Websocket = function(connection) {\n
    this._conn = connection;\n
    this.strip = "stream:stream";\n
\n
    var service = connection.service;\n
    if (service.indexOf("ws:") !== 0 \046\046 service.indexOf("wss:") !== 0) {\n
        // If the service is not an absolute URL, assume it is a path and put the absolute\n
        // URL together from options, current URL and the path.\n
        var new_service = "";\n
\n
        if (connection.options.protocol === "ws" \046\046 window.location.protocol !== "https:") {\n
            new_service += "ws";\n
        } else {\n
            new_service += "wss";\n
        }\n
\n
        new_service += "://" + window.location.host;\n
\n
        if (service.indexOf("/") !== 0) {\n
            new_service += window.location.pathname + service;\n
        } else {\n
            new_service += service;\n
        }\n
\n
        connection.service = new_service;\n
    }\n
};\n
\n
Strophe.Websocket.prototype = {\n
    /** PrivateFunction: _buildStream\n
     *  _Private_ helper function to generate the \074stream\076 start tag for WebSockets\n
     *\n
     *  Returns:\n
     *    A Strophe.Builder with a \074stream\076 element.\n
     */\n
    _buildStream: function ()\n
    {\n
        return $build("stream:stream", {\n
            "to": this._conn.domain,\n
            "xmlns": Strophe.NS.CLIENT,\n
            "xmlns:stream": Strophe.NS.STREAM,\n
            "version": \'1.0\'\n
        });\n
    },\n
\n
    /** PrivateFunction: _check_streamerror\n
     * _Private_ checks a message for stream:error\n
     *\n
     *  Parameters:\n
     *    (Strophe.Request) bodyWrap - The received stanza.\n
     *    connectstatus - The ConnectStatus that will be set on error.\n
     *  Returns:\n
     *     true if there was a streamerror, false otherwise.\n
     */\n
    _check_streamerror: function (bodyWrap, connectstatus) {\n
        var errors = bodyWrap.getElementsByTagName("stream:error");\n
        if (errors.length === 0) {\n
            return false;\n
        }\n
        var error = errors[0];\n
\n
        var condition = "";\n
        var text = "";\n
\n
        var ns = "urn:ietf:params:xml:ns:xmpp-streams";\n
        for (var i = 0; i \074 error.childNodes.length; i++) {\n
            var e = error.childNodes[i];\n
            if (e.getAttribute("xmlns") !== ns) {\n
                break;\n
            } if (e.nodeName === "text") {\n
                text = e.textContent;\n
            } else {\n
                condition = e.nodeName;\n
            }\n
        }\n
\n
        var errorString = "WebSocket stream error: ";\n
\n
        if (condition) {\n
            errorString += condition;\n
        } else {\n
            errorString += "unknown";\n
        }\n
\n
        if (text) {\n
            errorString += " - " + condition;\n
        }\n
\n
        Strophe.error(errorString);\n
\n
        // close the connection on stream_error\n
        this._conn._changeConnectStatus(connectstatus, condition);\n
        this._conn._doDisconnect();\n
        return true;\n
    },\n
\n
    /** PrivateFunction: _reset\n
     *  Reset the connection.\n
     *\n
     *  This function is called by the reset function of the Strophe Connection.\n
     *  Is not needed by WebSockets.\n
     */\n
    _reset: function ()\n
    {\n
        return;\n
    },\n
\n
    /** PrivateFunction: _connect\n
     *  _Private_ function called by Strophe.Connection.connect\n
     *\n
     *  Creates a WebSocket for a connection and assigns Callbacks to it.\n
     *  Does nothing if there already is a WebSocket.\n
     */\n
    _connect: function () {\n
        // Ensure that there is no open WebSocket from a previous Connection.\n
        this._closeSocket();\n
\n
        // Create the new WobSocket\n
        this.socket = new WebSocket(this._conn.service, "xmpp");\n
        this.socket.onopen = this._onOpen.bind(this);\n
        this.socket.onerror = this._onError.bind(this);\n
        this.socket.onclose = this._onClose.bind(this);\n
        this.socket.onmessage = this._connect_cb_wrapper.bind(this);\n
    },\n
\n
    /** PrivateFunction: _connect_cb\n
     *  _Private_ function called by Strophe.Connection._connect_cb\n
     *\n
     * checks for stream:error\n
     *\n
     *  Parameters:\n
     *    (Strophe.Request) bodyWrap - The received stanza.\n
     */\n
    _connect_cb: function(bodyWrap) {\n
        var error = this._check_streamerror(bodyWrap, Strophe.Status.CONNFAIL);\n
        if (error) {\n
            return Strophe.Status.CONNFAIL;\n
        }\n
    },\n
\n
    /** PrivateFunction: _handleStreamStart\n
     * _Private_ function that checks the opening stream:stream tag for errors.\n
     *\n
     * Disconnects if there is an error and returns false, true otherwise.\n
     *\n
     *  Parameters:\n
     *    (Node) message - Stanza containing the stream:stream.\n
     */\n
    _handleStreamStart: function(message) {\n
        var error = false;\n
        // Check for errors in the stream:stream tag\n
        var ns = message.getAttribute("xmlns");\n
        if (typeof ns !== "string") {\n
            error = "Missing xmlns in stream:stream";\n
        } else if (ns !== Strophe.NS.CLIENT) {\n
            error = "Wrong xmlns in stream:stream: " + ns;\n
        }\n
\n
        var ns_stream = message.namespaceURI;\n
        if (typeof ns_stream !== "string") {\n
            error = "Missing xmlns:stream in stream:stream";\n
        } else if (ns_stream !== Strophe.NS.STREAM) {\n
            error = "Wrong xmlns:stream in stream:stream: " + ns_stream;\n
        }\n
\n
        var ver = message.getAttribute("version");\n
        if (typeof ver !== "string") {\n
            error = "Missing version in stream:stream";\n
        } else if (ver !== "1.0") {\n
            error = "Wrong version in stream:stream: " + ver;\n
        }\n
\n
        if (error) {\n
            this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, error);\n
            this._conn._doDisconnect();\n
            return false;\n
        }\n
\n
        return true;\n
    },\n
\n
    /** PrivateFunction: _connect_cb_wrapper\n
     * _Private_ function that handles the first connection messages.\n
     *\n
     * On receiving an opening stream tag this callback replaces itself with the real\n
     * message handler. On receiving a stream error the connection is terminated.\n
     */\n
    _connect_cb_wrapper: function(message) {\n
        if (message.data.indexOf("\074stream:stream ") === 0 || message.data.indexOf("\074?xml") === 0) {\n
            // Strip the XML Declaration, if there is one\n
            var data = message.data.replace(/^(\074\\?.*?\\?\076\\s*)*/, "");\n
            if (data === \'\') return;\n
\n
            //Make the initial stream:stream selfclosing to parse it without a SAX parser.\n
            data = message.data.replace(/\074stream:stream (.*[^\\/])\076/, "\074stream:stream $1/\076");\n
\n
            var streamStart = new DOMParser().parseFromString(data, "text/xml").documentElement;\n
            this._conn.xmlInput(streamStart);\n
            this._conn.rawInput(message.data);\n
\n
            //_handleStreamSteart will check for XML errors and disconnect on error\n
            if (this._handleStreamStart(streamStart)) {\n
\n
                //_connect_cb will check for stream:error and disconnect on error\n
                this._connect_cb(streamStart);\n
\n
                // ensure received stream:stream is NOT selfclosing and save it for following messages\n
                this.streamStart = message.data.replace(/^\074stream:(.*)\\/\076$/, "\074stream:$1\076");\n
            }\n
        } else if (message.data === "\074/stream:stream\076") {\n
            this._conn.rawInput(message.data);\n
            this._conn.xmlInput(document.createElement("stream:stream"));\n
            this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, "Received closing stream");\n
            this._conn._doDisconnect();\n
            return;\n
        } else {\n
            var string = this._streamWrap(message.data);\n
            var elem = new DOMParser().parseFromString(string, "text/xml").documentElement;\n
            this.socket.onmessage = this._onMessage.bind(this);\n
            this._conn._connect_cb(elem, null, message.data);\n
        }\n
    },\n
\n
    /** PrivateFunction: _disconnect\n
     *  _Private_ function called by Strophe.Connection.disconnect\n
     *\n
     *  Disconnects and sends a last stanza if one is given\n
     *\n
     *  Parameters:\n
     *    (Request) pres - This stanza will be sent before disconnecting.\n
     */\n
    _disconnect: function (pres)\n
    {\n
        if (this.socket.readyState !== WebSocket.CLOSED) {\n
            if (pres) {\n
                this._conn.send(pres);\n
            }\n
            var close = \'\074/stream:stream\076\';\n
            this._conn.xmlOutput(document.createElement("stream:stream"));\n
            this._conn.rawOutput(close);\n
            try {\n
                this.socket.send(close);\n
            } catch (e) {\n
                Strophe.info("Couldn\'t send closing stream tag.");\n
            }\n
        }\n
\n
        this._conn._doDisconnect();\n
    },\n
\n
    /** PrivateFunction: _doDisconnect\n
     *  _Private_ function to disconnect.\n
     *\n
     *  Just closes the Socket for WebSockets\n
     */\n
    _doDisconnect: function ()\n
    {\n
        Strophe.info("WebSockets _doDisconnect was called");\n
        this._closeSocket();\n
    },\n
\n
    /** PrivateFunction _streamWrap\n
     *  _Private_ helper function to wrap a stanza in a \074stream\076 tag.\n
     *  This is used so Strophe can process stanzas from WebSockets like BOSH\n
     */\n
    _streamWrap: function (stanza)\n
    {\n
        return this.streamStart + stanza + \'\074/stream:stream\076\';\n
    },\n
\n
\n
    /** PrivateFunction: _closeSocket\n
     *  _Private_ function to close the WebSocket.\n
     *\n
     *  Closes the socket if it is still open and deletes it\n
     */\n
    _closeSocket: function ()\n
    {\n
        if (this.socket) { try {\n
            this.socket.close();\n
        } catch (e) {} }\n
        this.socket = null;\n
    },\n
\n
    /** PrivateFunction: _emptyQueue\n
     * _Private_ function to check if the message queue is empty.\n
     *\n
     *  Returns:\n
     *    True, because WebSocket messages are send immediately after queueing.\n
     */\n
    _emptyQueue: function ()\n
    {\n
        return true;\n
    },\n
\n
    /** PrivateFunction: _onClose\n
     * _Private_ function to handle websockets closing.\n
     *\n
     * Nothing to do here for WebSockets\n
     */\n
    _onClose: function() {\n
        if(this._conn.connected \046\046 !this._conn.disconnecting) {\n
            Strophe.error("Websocket closed unexcectedly");\n
            this._conn._doDisconnect();\n
        } else {\n
            Strophe.info("Websocket closed");\n
        }\n
    },\n
\n
    /** PrivateFunction: _no_auth_received\n
     *\n
     * Called on stream start/restart when no stream:features\n
     * has been received.\n
     */\n
    _no_auth_received: function (_callback)\n
    {\n
        Strophe.error("Server did not send any auth methods");\n
        this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, "Server did not send any auth methods");\n
        if (_callback) {\n
            _callback = _callback.bind(this._conn);\n
            _callback();\n
        }\n
        this._conn._doDisconnect();\n
    },\n
\n
    /** PrivateFunction: _onDisconnectTimeout\n
     *  _Private_ timeout handler for handling non-graceful disconnection.\n
     *\n
     *  This does nothing for WebSockets\n
     */\n
    _onDisconnectTimeout: function () {},\n
\n
    /** PrivateFunction: _onError\n
     * _Private_ function to handle websockets errors.\n
     *\n
     * Parameters:\n
     * (Object) error - The websocket error.\n
     */\n
    _onError: function(error) {\n
        Strophe.error("Websocket error " + error);\n
        this._conn._changeConnectStatus(Strophe.Status.CONNFAIL, "The WebSocket connection could not be established was disconnected.");\n
        this._disconnect();\n
    },\n
\n
    /** PrivateFunction: _onIdle\n
     *  _Private_ function called by Strophe.Connection._onIdle\n
     *\n
     *  sends all queued stanzas\n
     */\n
    _onIdle: function () {\n
        var data = this._conn._data;\n
        if (data.length \076 0 \046\046 !this._conn.paused) {\n
            for (var i = 0; i \074 data.length; i++) {\n
                if (data[i] !== null) {\n
                    var stanza, rawStanza;\n
                    if (data[i] === "restart") {\n
                        stanza = this._buildStream();\n
                        rawStanza = this._removeClosingTag(stanza);\n
                        stanza = stanza.tree();\n
                    } else {\n
                        stanza = data[i];\n
                        rawStanza = Strophe.serialize(stanza);\n
                    }\n
                    this._conn.xmlOutput(stanza);\n
                    this._conn.rawOutput(rawStanza);\n
                    this.socket.send(rawStanza);\n
                }\n
            }\n
            this._conn._data = [];\n
        }\n
    },\n
\n
    /** PrivateFunction: _onMessage\n
     * _Private_ function to handle websockets messages.\n
     *\n
     * This function parses each of the messages as if they are full documents. [TODO : We may actually want to use a SAX Push parser].\n
     *\n
     * Since all XMPP traffic starts with "\074stream:stream version=\'1.0\' xml:lang=\'en\' xmlns=\'jabber:client\' xmlns:stream=\'http://etherx.jabber.org/streams\' id=\'3697395463\' from=\'SERVER\'\076"\n
     * The first stanza will always fail to be parsed...\n
     * Addtionnaly, the seconds stanza will always be a \074stream:features\076 with the stream NS defined in the previous stanza... so we need to \'force\' the inclusion of the NS in this stanza!\n
     *\n
     * Parameters:\n
     * (string) message - The websocket message.\n
     */\n
    _onMessage: function(message) {\n
        var elem, data;\n
        // check for closing stream\n
        if (message.data === "\074/stream:stream\076") {\n
            var close = "\074/stream:stream\076";\n
            this._conn.rawInput(close);\n
            this._conn.xmlInput(document.createElement("stream:stream"));\n
            if (!this._conn.disconnecting) {\n
                this._conn._doDisconnect();\n
            }\n
            return;\n
        } else if (message.data.search("\074stream:stream ") === 0) {\n
            //Make the initial stream:stream selfclosing to parse it without a SAX parser.\n
            data = message.data.replace(/\074stream:stream (.*[^\\/])\076/, "\074stream:stream $1/\076");\n
            elem = new DOMParser().parseFromString(data, "text/xml").documentElement;\n
\n
            if (!this._handleStreamStart(elem)) {\n
                return;\n
            }\n
        } else {\n
            data = this._streamWrap(message.data);\n
            elem = new DOMParser().parseFromString(data, "text/xml").documentElement;\n
        }\n
\n
        if (this._check_streamerror(elem, Strophe.Status.ERROR)) {\n
            return;\n
        }\n
\n
        //handle unavailable presence stanza before disconnecting\n
        if (this._conn.disconnecting \046\046\n
                elem.firstChild.nodeName === "presence" \046\046\n
                elem.firstChild.getAttribute("type") === "unavailable") {\n
            this._conn.xmlInput(elem);\n
            this._conn.rawInput(Strophe.serialize(elem));\n
            // if we are already disconnecting we will ignore the unavailable stanza and\n
            // wait for the \074/stream:stream\076 tag before we close the connection\n
            return;\n
        }\n
        this._conn._dataRecv(elem, message.data);\n
    },\n
\n
    /** PrivateFunction: _onOpen\n
     * _Private_ function to handle websockets connection setup.\n
     *\n
     * The opening stream tag is sent here.\n
     */\n
    _onOpen: function() {\n
        Strophe.info("Websocket open");\n
        var start = this._buildStream();\n
        this._conn.xmlOutput(start.tree());\n
\n
        var startString = this._removeClosingTag(start);\n
        this._conn.rawOutput(startString);\n
        this.socket.send(startString);\n
    },\n
\n
    /** PrivateFunction: _removeClosingTag\n
     *  _Private_ function to Make the first \074stream:stream\076 non-selfclosing\n
     *\n
     *  Parameters:\n
     *      (Object) elem - The \074stream:stream\076 tag.\n
     *\n
     *  Returns:\n
     *      The stream:stream tag as String\n
     */\n
    _removeClosingTag: function(elem) {\n
        var string = Strophe.serialize(elem);\n
        string = string.replace(/\074(stream:stream .*[^\\/])\\/\076$/, "\074$1\076");\n
        return string;\n
    },\n
\n
    /** PrivateFunction: _reqToData\n
     * _Private_ function to get a stanza out of a request.\n
     *\n
     * WebSockets don\'t use requests, so the passed argument is just returned.\n
     *\n
     *  Parameters:\n
     *    (Object) stanza - The stanza.\n
     *\n
     *  Returns:\n
     *    The stanza that was passed.\n
     */\n
    _reqToData: function (stanza)\n
    {\n
        return stanza;\n
    },\n
\n
    /** PrivateFunction: _send\n
     *  _Private_ part of the Connection.send function for WebSocket\n
     *\n
     * Just flushes the messages that are in the queue\n
     */\n
    _send: function () {\n
        this._conn.flush();\n
    },\n
\n
    /** PrivateFunction: _sendRestart\n
     *\n
     *  Send an xmpp:restart stanza.\n
     */\n
    _sendRestart: function ()\n
    {\n
        clearTimeout(this._conn._idleTimeout);\n
        this._conn._onIdle.bind(this._conn)();\n
    }\n
};</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>strophe</string> </value>
        </item>
        <item>
            <key> <string>version</string> </key>
            <value> <string>001</string> </value>
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
                <value> <string>romain</string> </value>
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
                        <float>1418207088.03</float>
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
                <value> <string>romain</string> </value>
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
                <value> <string>939.33839.60138.34338</string> </value>
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
                        <float>1418207076.94</float>
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
                <value> <string>romain</string> </value>
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
                        <float>1418207006.15</float>
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
