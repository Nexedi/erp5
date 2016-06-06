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
            <value> <string>ts16390871.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>md5.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\r\n
 * A JavaScript implementation of the RSA Data Security, Inc. MD5 Message\r\n
 * Digest Algorithm, as defined in RFC 1321.\r\n
 * Version 2.2 Copyright (C) Paul Johnston 1999 - 2009\r\n
 * Other contributors: Greg Holt, Andrew Kepert, Ydnar, Lostinet\r\n
 * Distributed under the BSD License\r\n
 * See http://pajhome.org.uk/crypt/md5 for more info.\r\n
 */\r\n
\r\n
/*\r\n
 * Configurable variables. You may need to tweak these to be compatible with\r\n
 * the server-side, but the defaults work in most cases.\r\n
 */\r\n
var hexcase = 0;   /* hex output format. 0 - lowercase; 1 - uppercase        */\r\n
var b64pad  = "";  /* base-64 pad character. "=" for strict RFC compliance   */\r\n
\r\n
/*\r\n
 * These are the functions you\'ll usually want to call\r\n
 * They take string arguments and return either hex or base-64 encoded strings\r\n
 */\r\n
function hex_md5(s)    { return rstr2hex(rstr_md5(str2rstr_utf8(s))); }\r\n
function b64_md5(s)    { return rstr2b64(rstr_md5(str2rstr_utf8(s))); }\r\n
function any_md5(s, e) { return rstr2any(rstr_md5(str2rstr_utf8(s)), e); }\r\n
function hex_hmac_md5(k, d)\r\n
  { return rstr2hex(rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d))); }\r\n
function b64_hmac_md5(k, d)\r\n
  { return rstr2b64(rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d))); }\r\n
function any_hmac_md5(k, d, e)\r\n
  { return rstr2any(rstr_hmac_md5(str2rstr_utf8(k), str2rstr_utf8(d)), e); }\r\n
\r\n
/*\r\n
 * Perform a simple self-test to see if the VM is working\r\n
 */\r\n
function md5_vm_test()\r\n
{\r\n
  return hex_md5("abc").toLowerCase() == "900150983cd24fb0d6963f7d28e17f72";\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the MD5 of a raw string\r\n
 */\r\n
function rstr_md5(s)\r\n
{\r\n
  return binl2rstr(binl_md5(rstr2binl(s), s.length * 8));\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the HMAC-MD5, of a key and some data (raw strings)\r\n
 */\r\n
function rstr_hmac_md5(key, data)\r\n
{\r\n
  var bkey = rstr2binl(key);\r\n
  if(bkey.length > 16) bkey = binl_md5(bkey, key.length * 8);\r\n
\r\n
  var ipad = Array(16), opad = Array(16);\r\n
  for(var i = 0; i < 16; i++)\r\n
  {\r\n
    ipad[i] = bkey[i] ^ 0x36363636;\r\n
    opad[i] = bkey[i] ^ 0x5C5C5C5C;\r\n
  }\r\n
\r\n
  var hash = binl_md5(ipad.concat(rstr2binl(data)), 512 + data.length * 8);\r\n
  return binl2rstr(binl_md5(opad.concat(hash), 512 + 128));\r\n
}\r\n
\r\n
/*\r\n
 * Convert a raw string to a hex string\r\n
 */\r\n
function rstr2hex(input)\r\n
{\r\n
  try { hexcase } catch(e) { hexcase=0; }\r\n
  var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";\r\n
  var output = "";\r\n
  var x;\r\n
  for(var i = 0; i < input.length; i++)\r\n
  {\r\n
    x = input.charCodeAt(i);\r\n
    output += hex_tab.charAt((x >>> 4) & 0x0F)\r\n
           +  hex_tab.charAt( x        & 0x0F);\r\n
  }\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Convert a raw string to a base-64 string\r\n
 */\r\n
function rstr2b64(input)\r\n
{\r\n
  try { b64pad } catch(e) { b64pad=\'\'; }\r\n
  var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";\r\n
  var output = "";\r\n
  var len = input.length;\r\n
  for(var i = 0; i < len; i += 3)\r\n
  {\r\n
    var triplet = (input.charCodeAt(i) << 16)\r\n
                | (i + 1 < len ? input.charCodeAt(i+1) << 8 : 0)\r\n
                | (i + 2 < len ? input.charCodeAt(i+2)      : 0);\r\n
    for(var j = 0; j < 4; j++)\r\n
    {\r\n
      if(i * 8 + j * 6 > input.length * 8) output += b64pad;\r\n
      else output += tab.charAt((triplet >>> 6*(3-j)) & 0x3F);\r\n
    }\r\n
  }\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Convert a raw string to an arbitrary string encoding\r\n
 */\r\n
function rstr2any(input, encoding)\r\n
{\r\n
  var divisor = encoding.length;\r\n
  var i, j, q, x, quotient;\r\n
\r\n
  /* Convert to an array of 16-bit big-endian values, forming the dividend */\r\n
  var dividend = Array(Math.ceil(input.length / 2));\r\n
  for(i = 0; i < dividend.length; i++)\r\n
  {\r\n
    dividend[i] = (input.charCodeAt(i * 2) << 8) | input.charCodeAt(i * 2 + 1);\r\n
  }\r\n
\r\n
  /*\r\n
   * Repeatedly perform a long division. The binary array forms the dividend,\r\n
   * the length of the encoding is the divisor. Once computed, the quotient\r\n
   * forms the dividend for the next step. All remainders are stored for later\r\n
   * use.\r\n
   */\r\n
  var full_length = Math.ceil(input.length * 8 /\r\n
                                    (Math.log(encoding.length) / Math.log(2)));\r\n
  var remainders = Array(full_length);\r\n
  for(j = 0; j < full_length; j++)\r\n
  {\r\n
    quotient = Array();\r\n
    x = 0;\r\n
    for(i = 0; i < dividend.length; i++)\r\n
    {\r\n
      x = (x << 16) + dividend[i];\r\n
      q = Math.floor(x / divisor);\r\n
      x -= q * divisor;\r\n
      if(quotient.length > 0 || q > 0)\r\n
        quotient[quotient.length] = q;\r\n
    }\r\n
    remainders[j] = x;\r\n
    dividend = quotient;\r\n
  }\r\n
\r\n
  /* Convert the remainders to the output string */\r\n
  var output = "";\r\n
  for(i = remainders.length - 1; i >= 0; i--)\r\n
    output += encoding.charAt(remainders[i]);\r\n
\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Encode a string as utf-8.\r\n
 * For efficiency, this assumes the input is valid utf-16.\r\n
 */\r\n
function str2rstr_utf8(input)\r\n
{\r\n
  var output = "";\r\n
  var i = -1;\r\n
  var x, y;\r\n
\r\n
  while(++i < input.length)\r\n
  {\r\n
    /* Decode utf-16 surrogate pairs */\r\n
    x = input.charCodeAt(i);\r\n
    y = i + 1 < input.length ? input.charCodeAt(i + 1) : 0;\r\n
    if(0xD800 <= x && x <= 0xDBFF && 0xDC00 <= y && y <= 0xDFFF)\r\n
    {\r\n
      x = 0x10000 + ((x & 0x03FF) << 10) + (y & 0x03FF);\r\n
      i++;\r\n
    }\r\n
\r\n
    /* Encode output as utf-8 */\r\n
    if(x <= 0x7F)\r\n
      output += String.fromCharCode(x);\r\n
    else if(x <= 0x7FF)\r\n
      output += String.fromCharCode(0xC0 | ((x >>> 6 ) & 0x1F),\r\n
                                    0x80 | ( x         & 0x3F));\r\n
    else if(x <= 0xFFFF)\r\n
      output += String.fromCharCode(0xE0 | ((x >>> 12) & 0x0F),\r\n
                                    0x80 | ((x >>> 6 ) & 0x3F),\r\n
                                    0x80 | ( x         & 0x3F));\r\n
    else if(x <= 0x1FFFFF)\r\n
      output += String.fromCharCode(0xF0 | ((x >>> 18) & 0x07),\r\n
                                    0x80 | ((x >>> 12) & 0x3F),\r\n
                                    0x80 | ((x >>> 6 ) & 0x3F),\r\n
                                    0x80 | ( x         & 0x3F));\r\n
  }\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Encode a string as utf-16\r\n
 */\r\n
function str2rstr_utf16le(input)\r\n
{\r\n
  var output = "";\r\n
  for(var i = 0; i < input.length; i++)\r\n
    output += String.fromCharCode( input.charCodeAt(i)        & 0xFF,\r\n
                                  (input.charCodeAt(i) >>> 8) & 0xFF);\r\n
  return output;\r\n
}\r\n
\r\n
function str2rstr_utf16be(input)\r\n
{\r\n
  var output = "";\r\n
  for(var i = 0; i < input.length; i++)\r\n
    output += String.fromCharCode((input.charCodeAt(i) >>> 8) & 0xFF,\r\n
                                   input.charCodeAt(i)        & 0xFF);\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Convert a raw string to an array of little-endian words\r\n
 * Characters >255 have their high-byte silently ignored.\r\n
 */\r\n
function rstr2binl(input)\r\n
{\r\n
  var output = Array(input.length >> 2);\r\n
  for(var i = 0; i < output.length; i++)\r\n
    output[i] = 0;\r\n
  for(var i = 0; i < input.length * 8; i += 8)\r\n
    output[i>>5] |= (input.charCodeAt(i / 8) & 0xFF) << (i%32);\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Convert an array of little-endian words to a string\r\n
 */\r\n
function binl2rstr(input)\r\n
{\r\n
  var output = "";\r\n
  for(var i = 0; i < input.length * 32; i += 8)\r\n
    output += String.fromCharCode((input[i>>5] >>> (i % 32)) & 0xFF);\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the MD5 of an array of little-endian words, and a bit length.\r\n
 */\r\n
function binl_md5(x, len)\r\n
{\r\n
  /* append padding */\r\n
  x[len >> 5] |= 0x80 << ((len) % 32);\r\n
  x[(((len + 64) >>> 9) << 4) + 14] = len;\r\n
\r\n
  var a =  1732584193;\r\n
  var b = -271733879;\r\n
  var c = -1732584194;\r\n
  var d =  271733878;\r\n
\r\n
  for(var i = 0; i < x.length; i += 16)\r\n
  {\r\n
    var olda = a;\r\n
    var oldb = b;\r\n
    var oldc = c;\r\n
    var oldd = d;\r\n
\r\n
    a = md5_ff(a, b, c, d, x[i+ 0], 7 , -680876936);\r\n
    d = md5_ff(d, a, b, c, x[i+ 1], 12, -389564586);\r\n
    c = md5_ff(c, d, a, b, x[i+ 2], 17,  606105819);\r\n
    b = md5_ff(b, c, d, a, x[i+ 3], 22, -1044525330);\r\n
    a = md5_ff(a, b, c, d, x[i+ 4], 7 , -176418897);\r\n
    d = md5_ff(d, a, b, c, x[i+ 5], 12,  1200080426);\r\n
    c = md5_ff(c, d, a, b, x[i+ 6], 17, -1473231341);\r\n
    b = md5_ff(b, c, d, a, x[i+ 7], 22, -45705983);\r\n
    a = md5_ff(a, b, c, d, x[i+ 8], 7 ,  1770035416);\r\n
    d = md5_ff(d, a, b, c, x[i+ 9], 12, -1958414417);\r\n
    c = md5_ff(c, d, a, b, x[i+10], 17, -42063);\r\n
    b = md5_ff(b, c, d, a, x[i+11], 22, -1990404162);\r\n
    a = md5_ff(a, b, c, d, x[i+12], 7 ,  1804603682);\r\n
    d = md5_ff(d, a, b, c, x[i+13], 12, -40341101);\r\n
    c = md5_ff(c, d, a, b, x[i+14], 17, -1502002290);\r\n
    b = md5_ff(b, c, d, a, x[i+15], 22,  1236535329);\r\n
\r\n
    a = md5_gg(a, b, c, d, x[i+ 1], 5 , -165796510);\r\n
    d = md5_gg(d, a, b, c, x[i+ 6], 9 , -1069501632);\r\n
    c = md5_gg(c, d, a, b, x[i+11], 14,  643717713);\r\n
    b = md5_gg(b, c, d, a, x[i+ 0], 20, -373897302);\r\n
    a = md5_gg(a, b, c, d, x[i+ 5], 5 , -701558691);\r\n
    d = md5_gg(d, a, b, c, x[i+10], 9 ,  38016083);\r\n
    c = md5_gg(c, d, a, b, x[i+15], 14, -660478335);\r\n
    b = md5_gg(b, c, d, a, x[i+ 4], 20, -405537848);\r\n
    a = md5_gg(a, b, c, d, x[i+ 9], 5 ,  568446438);\r\n
    d = md5_gg(d, a, b, c, x[i+14], 9 , -1019803690);\r\n
    c = md5_gg(c, d, a, b, x[i+ 3], 14, -187363961);\r\n
    b = md5_gg(b, c, d, a, x[i+ 8], 20,  1163531501);\r\n
    a = md5_gg(a, b, c, d, x[i+13], 5 , -1444681467);\r\n
    d = md5_gg(d, a, b, c, x[i+ 2], 9 , -51403784);\r\n
    c = md5_gg(c, d, a, b, x[i+ 7], 14,  1735328473);\r\n
    b = md5_gg(b, c, d, a, x[i+12], 20, -1926607734);\r\n
\r\n
    a = md5_hh(a, b, c, d, x[i+ 5], 4 , -378558);\r\n
    d = md5_hh(d, a, b, c, x[i+ 8], 11, -2022574463);\r\n
    c = md5_hh(c, d, a, b, x[i+11], 16,  1839030562);\r\n
    b = md5_hh(b, c, d, a, x[i+14], 23, -35309556);\r\n
    a = md5_hh(a, b, c, d, x[i+ 1], 4 , -1530992060);\r\n
    d = md5_hh(d, a, b, c, x[i+ 4], 11,  1272893353);\r\n
    c = md5_hh(c, d, a, b, x[i+ 7], 16, -155497632);\r\n
    b = md5_hh(b, c, d, a, x[i+10], 23, -1094730640);\r\n
    a = md5_hh(a, b, c, d, x[i+13], 4 ,  681279174);\r\n
    d = md5_hh(d, a, b, c, x[i+ 0], 11, -358537222);\r\n
    c = md5_hh(c, d, a, b, x[i+ 3], 16, -722521979);\r\n
    b = md5_hh(b, c, d, a, x[i+ 6], 23,  76029189);\r\n
    a = md5_hh(a, b, c, d, x[i+ 9], 4 , -640364487);\r\n
    d = md5_hh(d, a, b, c, x[i+12], 11, -421815835);\r\n
    c = md5_hh(c, d, a, b, x[i+15], 16,  530742520);\r\n
    b = md5_hh(b, c, d, a, x[i+ 2], 23, -995338651);\r\n
\r\n
    a = md5_ii(a, b, c, d, x[i+ 0], 6 , -198630844);\r\n
    d = md5_ii(d, a, b, c, x[i+ 7], 10,  1126891415);\r\n
    c = md5_ii(c, d, a, b, x[i+14], 15, -1416354905);\r\n
    b = md5_ii(b, c, d, a, x[i+ 5], 21, -57434055);\r\n
    a = md5_ii(a, b, c, d, x[i+12], 6 ,  1700485571);\r\n
    d = md5_ii(d, a, b, c, x[i+ 3], 10, -1894986606);\r\n
    c = md5_ii(c, d, a, b, x[i+10], 15, -1051523);\r\n
    b = md5_ii(b, c, d, a, x[i+ 1], 21, -2054922799);\r\n
    a = md5_ii(a, b, c, d, x[i+ 8], 6 ,  1873313359);\r\n
    d = md5_ii(d, a, b, c, x[i+15], 10, -30611744);\r\n
    c = md5_ii(c, d, a, b, x[i+ 6], 15, -1560198380);\r\n
    b = md5_ii(b, c, d, a, x[i+13], 21,  1309151649);\r\n
    a = md5_ii(a, b, c, d, x[i+ 4], 6 , -145523070);\r\n
    d = md5_ii(d, a, b, c, x[i+11], 10, -1120210379);\r\n
    c = md5_ii(c, d, a, b, x[i+ 2], 15,  718787259);\r\n
    b = md5_ii(b, c, d, a, x[i+ 9], 21, -343485551);\r\n
\r\n
    a = safe_add(a, olda);\r\n
    b = safe_add(b, oldb);\r\n
    c = safe_add(c, oldc);\r\n
    d = safe_add(d, oldd);\r\n
  }\r\n
  return Array(a, b, c, d);\r\n
}\r\n
\r\n
/*\r\n
 * These functions implement the four basic operations the algorithm uses.\r\n
 */\r\n
function md5_cmn(q, a, b, x, s, t)\r\n
{\r\n
  return safe_add(bit_rol(safe_add(safe_add(a, q), safe_add(x, t)), s),b);\r\n
}\r\n
function md5_ff(a, b, c, d, x, s, t)\r\n
{\r\n
  return md5_cmn((b & c) | ((~b) & d), a, b, x, s, t);\r\n
}\r\n
function md5_gg(a, b, c, d, x, s, t)\r\n
{\r\n
  return md5_cmn((b & d) | (c & (~d)), a, b, x, s, t);\r\n
}\r\n
function md5_hh(a, b, c, d, x, s, t)\r\n
{\r\n
  return md5_cmn(b ^ c ^ d, a, b, x, s, t);\r\n
}\r\n
function md5_ii(a, b, c, d, x, s, t)\r\n
{\r\n
  return md5_cmn(c ^ (b | (~d)), a, b, x, s, t);\r\n
}\r\n
\r\n
/*\r\n
 * Add integers, wrapping at 2^32. This uses 16-bit operations internally\r\n
 * to work around bugs in some JS interpreters.\r\n
 */\r\n
function safe_add(x, y)\r\n
{\r\n
  var lsw = (x & 0xFFFF) + (y & 0xFFFF);\r\n
  var msw = (x >> 16) + (y >> 16) + (lsw >> 16);\r\n
  return (msw << 16) | (lsw & 0xFFFF);\r\n
}\r\n
\r\n
/*\r\n
 * Bitwise rotate a 32-bit number to the left.\r\n
 */\r\n
function bit_rol(num, cnt)\r\n
{\r\n
  return (num << cnt) | (num >>> (32 - cnt));\r\n
}\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12297</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
