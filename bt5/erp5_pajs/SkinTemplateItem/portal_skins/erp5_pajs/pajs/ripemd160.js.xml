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
            <value> <string>ts16390927.01</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ripemd160.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * A JavaScript implementation of the RIPEMD-160 Algorithm\n
 * Version 2.2 Copyright Jeremy Lin, Paul Johnston 2000 - 2009.\n
 * Other contributors: Greg Holt, Andrew Kepert, Ydnar, Lostinet\n
 * Distributed under the BSD License\n
 * See http://pajhome.org.uk/crypt/md5 for details.\n
 * Also http://www.ocf.berkeley.edu/~jjlin/jsotp/\n
 */\n
\n
/*\n
 * Configurable variables. You may need to tweak these to be compatible with\n
 * the server-side, but the defaults work in most cases.\n
 */\n
var hexcase = 0;  /* hex output format. 0 - lowercase; 1 - uppercase        */\n
var b64pad  = ""; /* base-64 pad character. "=" for strict RFC compliance   */\n
\n
/*\n
 * These are the functions you\'ll usually want to call\n
 * They take string arguments and return either hex or base-64 encoded strings\n
 */\n
function hex_rmd160(s)    { return rstr2hex(rstr_rmd160(str2rstr_utf8(s))); }\n
function b64_rmd160(s)    { return rstr2b64(rstr_rmd160(str2rstr_utf8(s))); }\n
function any_rmd160(s, e) { return rstr2any(rstr_rmd160(str2rstr_utf8(s)), e); }\n
function hex_hmac_rmd160(k, d)\n
  { return rstr2hex(rstr_hmac_rmd160(str2rstr_utf8(k), str2rstr_utf8(d))); }\n
function b64_hmac_rmd160(k, d)\n
  { return rstr2b64(rstr_hmac_rmd160(str2rstr_utf8(k), str2rstr_utf8(d))); }\n
function any_hmac_rmd160(k, d, e)\n
  { return rstr2any(rstr_hmac_rmd160(str2rstr_utf8(k), str2rstr_utf8(d)), e); }\n
\n
/*\n
 * Perform a simple self-test to see if the VM is working\n
 */\n
function rmd160_vm_test()\n
{\n
  return hex_rmd160("abc").toLowerCase() == "8eb208f7e05d987a9b044a8e98c6b087f15a0bfc";\n
}\n
\n
/*\n
 * Calculate the rmd160 of a raw string\n
 */\n
function rstr_rmd160(s)\n
{\n
  return binl2rstr(binl_rmd160(rstr2binl(s), s.length * 8));\n
}\n
\n
/*\n
 * Calculate the HMAC-rmd160 of a key and some data (raw strings)\n
 */\n
function rstr_hmac_rmd160(key, data)\n
{\n
  var bkey = rstr2binl(key);\n
  if(bkey.length > 16) bkey = binl_rmd160(bkey, key.length * 8);\n
\n
  var ipad = Array(16), opad = Array(16);\n
  for(var i = 0; i < 16; i++)\n
  {\n
    ipad[i] = bkey[i] ^ 0x36363636;\n
    opad[i] = bkey[i] ^ 0x5C5C5C5C;\n
  }\n
\n
  var hash = binl_rmd160(ipad.concat(rstr2binl(data)), 512 + data.length * 8);\n
  return binl2rstr(binl_rmd160(opad.concat(hash), 512 + 160));\n
}\n
\n
/*\n
 * Convert a raw string to a hex string\n
 */\n
function rstr2hex(input)\n
{\n
  try { hexcase } catch(e) { hexcase=0; }\n
  var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";\n
  var output = "";\n
  var x;\n
  for(var i = 0; i < input.length; i++)\n
  {\n
    x = input.charCodeAt(i);\n
    output += hex_tab.charAt((x >>> 4) & 0x0F)\n
           +  hex_tab.charAt( x        & 0x0F);\n
  }\n
  return output;\n
}\n
\n
/*\n
 * Convert a raw string to a base-64 string\n
 */\n
function rstr2b64(input)\n
{\n
  try { b64pad } catch(e) { b64pad=\'\'; }\n
  var tab = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";\n
  var output = "";\n
  var len = input.length;\n
  for(var i = 0; i < len; i += 3)\n
  {\n
    var triplet = (input.charCodeAt(i) << 16)\n
                | (i + 1 < len ? input.charCodeAt(i+1) << 8 : 0)\n
                | (i + 2 < len ? input.charCodeAt(i+2)      : 0);\n
    for(var j = 0; j < 4; j++)\n
    {\n
      if(i * 8 + j * 6 > input.length * 8) output += b64pad;\n
      else output += tab.charAt((triplet >>> 6*(3-j)) & 0x3F);\n
    }\n
  }\n
  return output;\n
}\n
\n
/*\n
 * Convert a raw string to an arbitrary string encoding\n
 */\n
function rstr2any(input, encoding)\n
{\n
  var divisor = encoding.length;\n
  var remainders = Array();\n
  var i, q, x, quotient;\n
\n
  /* Convert to an array of 16-bit big-endian values, forming the dividend */\n
  var dividend = Array(Math.ceil(input.length / 2));\n
  for(i = 0; i < dividend.length; i++)\n
  {\n
    dividend[i] = (input.charCodeAt(i * 2) << 8) | input.charCodeAt(i * 2 + 1);\n
  }\n
\n
  /*\n
   * Repeatedly perform a long division. The binary array forms the dividend,\n
   * the length of the encoding is the divisor. Once computed, the quotient\n
   * forms the dividend for the next step. We stop when the dividend is zero.\n
   * All remainders are stored for later use.\n
   */\n
  while(dividend.length > 0)\n
  {\n
    quotient = Array();\n
    x = 0;\n
    for(i = 0; i < dividend.length; i++)\n
    {\n
      x = (x << 16) + dividend[i];\n
      q = Math.floor(x / divisor);\n
      x -= q * divisor;\n
      if(quotient.length > 0 || q > 0)\n
        quotient[quotient.length] = q;\n
    }\n
    remainders[remainders.length] = x;\n
    dividend = quotient;\n
  }\n
\n
  /* Convert the remainders to the output string */\n
  var output = "";\n
  for(i = remainders.length - 1; i >= 0; i--)\n
    output += encoding.charAt(remainders[i]);\n
\n
  /* Append leading zero equivalents */\n
  var full_length = Math.ceil(input.length * 8 /\n
                                    (Math.log(encoding.length) / Math.log(2)))\n
  for(i = output.length; i < full_length; i++)\n
    output = encoding[0] + output;\n
\n
  return output;\n
}\n
\n
/*\n
 * Encode a string as utf-8.\n
 * For efficiency, this assumes the input is valid utf-16.\n
 */\n
function str2rstr_utf8(input)\n
{\n
  var output = "";\n
  var i = -1;\n
  var x, y;\n
\n
  while(++i < input.length)\n
  {\n
    /* Decode utf-16 surrogate pairs */\n
    x = input.charCodeAt(i);\n
    y = i + 1 < input.length ? input.charCodeAt(i + 1) : 0;\n
    if(0xD800 <= x && x <= 0xDBFF && 0xDC00 <= y && y <= 0xDFFF)\n
    {\n
      x = 0x10000 + ((x & 0x03FF) << 10) + (y & 0x03FF);\n
      i++;\n
    }\n
\n
    /* Encode output as utf-8 */\n
    if(x <= 0x7F)\n
      output += String.fromCharCode(x);\n
    else if(x <= 0x7FF)\n
      output += String.fromCharCode(0xC0 | ((x >>> 6 ) & 0x1F),\n
                                    0x80 | ( x         & 0x3F));\n
    else if(x <= 0xFFFF)\n
      output += String.fromCharCode(0xE0 | ((x >>> 12) & 0x0F),\n
                                    0x80 | ((x >>> 6 ) & 0x3F),\n
                                    0x80 | ( x         & 0x3F));\n
    else if(x <= 0x1FFFFF)\n
      output += String.fromCharCode(0xF0 | ((x >>> 18) & 0x07),\n
                                    0x80 | ((x >>> 12) & 0x3F),\n
                                    0x80 | ((x >>> 6 ) & 0x3F),\n
                                    0x80 | ( x         & 0x3F));\n
  }\n
  return output;\n
}\n
\n
/*\n
 * Encode a string as utf-16\n
 */\n
function str2rstr_utf16le(input)\n
{\n
  var output = "";\n
  for(var i = 0; i < input.length; i++)\n
    output += String.fromCharCode( input.charCodeAt(i)        & 0xFF,\n
                                  (input.charCodeAt(i) >>> 8) & 0xFF);\n
  return output;\n
}\n
\n
function str2rstr_utf16be(input)\n
{\n
  var output = "";\n
  for(var i = 0; i < input.length; i++)\n
    output += String.fromCharCode((input.charCodeAt(i) >>> 8) & 0xFF,\n
                                   input.charCodeAt(i)        & 0xFF);\n
  return output;\n
}\n
\n
/*\n
 * Convert a raw string to an array of little-endian words\n
 * Characters >255 have their high-byte silently ignored.\n
 */\n
function rstr2binl(input)\n
{\n
  var output = Array(input.length >> 2);\n
  for(var i = 0; i < output.length; i++)\n
    output[i] = 0;\n
  for(var i = 0; i < input.length * 8; i += 8)\n
    output[i>>5] |= (input.charCodeAt(i / 8) & 0xFF) << (i%32);\n
  return output;\n
}\n
\n
/*\n
 * Convert an array of little-endian words to a string\n
 */\n
function binl2rstr(input)\n
{\n
  var output = "";\n
  for(var i = 0; i < input.length * 32; i += 8)\n
    output += String.fromCharCode((input[i>>5] >>> (i % 32)) & 0xFF);\n
  return output;\n
}\n
\n
/*\n
 * Calculate the RIPE-MD160 of an array of little-endian words, and a bit length.\n
 */\n
function binl_rmd160(x, len)\n
{\n
  /* append padding */\n
  x[len >> 5] |= 0x80 << (len % 32);\n
  x[(((len + 64) >>> 9) << 4) + 14] = len;\n
\n
  var h0 = 0x67452301;\n
  var h1 = 0xefcdab89;\n
  var h2 = 0x98badcfe;\n
  var h3 = 0x10325476;\n
  var h4 = 0xc3d2e1f0;\n
\n
  for (var i = 0; i < x.length; i += 16) {\n
    var T;\n
    var A1 = h0, B1 = h1, C1 = h2, D1 = h3, E1 = h4;\n
    var A2 = h0, B2 = h1, C2 = h2, D2 = h3, E2 = h4;\n
    for (var j = 0; j <= 79; ++j) {\n
      T = safe_add(A1, rmd160_f(j, B1, C1, D1));\n
      T = safe_add(T, x[i + rmd160_r1[j]]);\n
      T = safe_add(T, rmd160_K1(j));\n
      T = safe_add(bit_rol(T, rmd160_s1[j]), E1);\n
      A1 = E1; E1 = D1; D1 = bit_rol(C1, 10); C1 = B1; B1 = T;\n
      T = safe_add(A2, rmd160_f(79-j, B2, C2, D2));\n
      T = safe_add(T, x[i + rmd160_r2[j]]);\n
      T = safe_add(T, rmd160_K2(j));\n
      T = safe_add(bit_rol(T, rmd160_s2[j]), E2);\n
      A2 = E2; E2 = D2; D2 = bit_rol(C2, 10); C2 = B2; B2 = T;\n
    }\n
    T = safe_add(h1, safe_add(C1, D2));\n
    h1 = safe_add(h2, safe_add(D1, E2));\n
    h2 = safe_add(h3, safe_add(E1, A2));\n
    h3 = safe_add(h4, safe_add(A1, B2));\n
    h4 = safe_add(h0, safe_add(B1, C2));\n
    h0 = T;\n
  }\n
  return [h0, h1, h2, h3, h4];\n
}\n
\n
function rmd160_f(j, x, y, z)\n
{\n
  return ( 0 <= j && j <= 15) ? (x ^ y ^ z) :\n
         (16 <= j && j <= 31) ? (x & y) | (~x & z) :\n
         (32 <= j && j <= 47) ? (x | ~y) ^ z :\n
         (48 <= j && j <= 63) ? (x & z) | (y & ~z) :\n
         (64 <= j && j <= 79) ? x ^ (y | ~z) :\n
         "rmd160_f: j out of range";\n
}\n
function rmd160_K1(j)\n
{\n
  return ( 0 <= j && j <= 15) ? 0x00000000 :\n
         (16 <= j && j <= 31) ? 0x5a827999 :\n
         (32 <= j && j <= 47) ? 0x6ed9eba1 :\n
         (48 <= j && j <= 63) ? 0x8f1bbcdc :\n
         (64 <= j && j <= 79) ? 0xa953fd4e :\n
         "rmd160_K1: j out of range";\n
}\n
function rmd160_K2(j)\n
{\n
  return ( 0 <= j && j <= 15) ? 0x50a28be6 :\n
         (16 <= j && j <= 31) ? 0x5c4dd124 :\n
         (32 <= j && j <= 47) ? 0x6d703ef3 :\n
         (48 <= j && j <= 63) ? 0x7a6d76e9 :\n
         (64 <= j && j <= 79) ? 0x00000000 :\n
         "rmd160_K2: j out of range";\n
}\n
var rmd160_r1 = [\n
   0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,\n
   7,  4, 13,  1, 10,  6, 15,  3, 12,  0,  9,  5,  2, 14, 11,  8,\n
   3, 10, 14,  4,  9, 15,  8,  1,  2,  7,  0,  6, 13, 11,  5, 12,\n
   1,  9, 11, 10,  0,  8, 12,  4, 13,  3,  7, 15, 14,  5,  6,  2,\n
   4,  0,  5,  9,  7, 12,  2, 10, 14,  1,  3,  8, 11,  6, 15, 13\n
];\n
var rmd160_r2 = [\n
   5, 14,  7,  0,  9,  2, 11,  4, 13,  6, 15,  8,  1, 10,  3, 12,\n
   6, 11,  3,  7,  0, 13,  5, 10, 14, 15,  8, 12,  4,  9,  1,  2,\n
  15,  5,  1,  3,  7, 14,  6,  9, 11,  8, 12,  2, 10,  0,  4, 13,\n
   8,  6,  4,  1,  3, 11, 15,  0,  5, 12,  2, 13,  9,  7, 10, 14,\n
  12, 15, 10,  4,  1,  5,  8,  7,  6,  2, 13, 14,  0,  3,  9, 11\n
];\n
var rmd160_s1 = [\n
  11, 14, 15, 12,  5,  8,  7,  9, 11, 13, 14, 15,  6,  7,  9,  8,\n
   7,  6,  8, 13, 11,  9,  7, 15,  7, 12, 15,  9, 11,  7, 13, 12,\n
  11, 13,  6,  7, 14,  9, 13, 15, 14,  8, 13,  6,  5, 12,  7,  5,\n
  11, 12, 14, 15, 14, 15,  9,  8,  9, 14,  5,  6,  8,  6,  5, 12,\n
   9, 15,  5, 11,  6,  8, 13, 12,  5, 12, 13, 14, 11,  8,  5,  6\n
];\n
var rmd160_s2 = [\n
   8,  9,  9, 11, 13, 15, 15,  5,  7,  7,  8, 11, 14, 14, 12,  6,\n
   9, 13, 15,  7, 12,  8,  9, 11,  7,  7, 12,  7,  6, 15, 13, 11,\n
   9,  7, 15, 11,  8,  6,  6, 14, 12, 13,  5, 14, 13, 13,  7,  5,\n
  15,  5,  8, 11, 14, 14,  6, 14,  6,  9, 12,  9, 12,  5, 15,  8,\n
   8,  5, 12,  9, 12,  5, 14,  6,  8, 13,  6,  5, 15, 13, 11, 11\n
];\n
\n
/*\n
 * Add integers, wrapping at 2^32. This uses 16-bit operations internally\n
 * to work around bugs in some JS interpreters.\n
 */\n
function safe_add(x, y)\n
{\n
  var lsw = (x & 0xFFFF) + (y & 0xFFFF);\n
  var msw = (x >> 16) + (y >> 16) + (lsw >> 16);\n
  return (msw << 16) | (lsw & 0xFFFF);\n
}\n
\n
/*\n
 * Bitwise rotate a 32-bit number to the left.\n
 */\n
function bit_rol(num, cnt)\n
{\n
  return (num << cnt) | (num >>> (32 - cnt));\n
}\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>11181</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
