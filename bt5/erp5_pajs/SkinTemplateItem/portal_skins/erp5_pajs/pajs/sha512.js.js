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
            <value> <string>ts16390948.7</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>sha512.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\r\n
 * A JavaScript implementation of the Secure Hash Algorithm, SHA-512, as defined\r\n
 * in FIPS 180-2\r\n
 * Version 2.2 Copyright Anonymous Contributor, Paul Johnston 2000 - 2009.\r\n
 * Other contributors: Greg Holt, Andrew Kepert, Ydnar, Lostinet\r\n
 * Distributed under the BSD License\r\n
 * See http://pajhome.org.uk/crypt/md5 for details.\r\n
 */\r\n
\r\n
/*\r\n
 * Configurable variables. You may need to tweak these to be compatible with\r\n
 * the server-side, but the defaults work in most cases.\r\n
 */\r\n
var hexcase = 0;  /* hex output format. 0 - lowercase; 1 - uppercase        */\r\n
var b64pad  = ""; /* base-64 pad character. "=" for strict RFC compliance   */\r\n
\r\n
/*\r\n
 * These are the functions you\'ll usually want to call\r\n
 * They take string arguments and return either hex or base-64 encoded strings\r\n
 */\r\n
function hex_sha512(s)    { return rstr2hex(rstr_sha512(str2rstr_utf8(s))); }\r\n
function b64_sha512(s)    { return rstr2b64(rstr_sha512(str2rstr_utf8(s))); }\r\n
function any_sha512(s, e) { return rstr2any(rstr_sha512(str2rstr_utf8(s)), e);}\r\n
function hex_hmac_sha512(k, d)\r\n
  { return rstr2hex(rstr_hmac_sha512(str2rstr_utf8(k), str2rstr_utf8(d))); }\r\n
function b64_hmac_sha512(k, d)\r\n
  { return rstr2b64(rstr_hmac_sha512(str2rstr_utf8(k), str2rstr_utf8(d))); }\r\n
function any_hmac_sha512(k, d, e)\r\n
  { return rstr2any(rstr_hmac_sha512(str2rstr_utf8(k), str2rstr_utf8(d)), e);}\r\n
\r\n
/*\r\n
 * Perform a simple self-test to see if the VM is working\r\n
 */\r\n
function sha512_vm_test()\r\n
{\r\n
  return hex_sha512("abc").toLowerCase() ==\r\n
    "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a" +\r\n
    "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f";\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the SHA-512 of a raw string\r\n
 */\r\n
function rstr_sha512(s)\r\n
{\r\n
  return binb2rstr(binb_sha512(rstr2binb(s), s.length * 8));\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the HMAC-SHA-512 of a key and some data (raw strings)\r\n
 */\r\n
function rstr_hmac_sha512(key, data)\r\n
{\r\n
  var bkey = rstr2binb(key);\r\n
  if(bkey.length > 32) bkey = binb_sha512(bkey, key.length * 8);\r\n
\r\n
  var ipad = Array(32), opad = Array(32);\r\n
  for(var i = 0; i < 32; i++)\r\n
  {\r\n
    ipad[i] = bkey[i] ^ 0x36363636;\r\n
    opad[i] = bkey[i] ^ 0x5C5C5C5C;\r\n
  }\r\n
\r\n
  var hash = binb_sha512(ipad.concat(rstr2binb(data)), 1024 + data.length * 8);\r\n
  return binb2rstr(binb_sha512(opad.concat(hash), 1024 + 512));\r\n
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
 * Convert a raw string to an array of big-endian words\r\n
 * Characters >255 have their high-byte silently ignored.\r\n
 */\r\n
function rstr2binb(input)\r\n
{\r\n
  var output = Array(input.length >> 2);\r\n
  for(var i = 0; i < output.length; i++)\r\n
    output[i] = 0;\r\n
  for(var i = 0; i < input.length * 8; i += 8)\r\n
    output[i>>5] |= (input.charCodeAt(i / 8) & 0xFF) << (24 - i % 32);\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Convert an array of big-endian words to a string\r\n
 */\r\n
function binb2rstr(input)\r\n
{\r\n
  var output = "";\r\n
  for(var i = 0; i < input.length * 32; i += 8)\r\n
    output += String.fromCharCode((input[i>>5] >>> (24 - i % 32)) & 0xFF);\r\n
  return output;\r\n
}\r\n
\r\n
/*\r\n
 * Calculate the SHA-512 of an array of big-endian dwords, and a bit length\r\n
 */\r\n
var sha512_k;\r\n
function binb_sha512(x, len)\r\n
{\r\n
  if(sha512_k == undefined)\r\n
  {\r\n
    //SHA512 constants\r\n
    sha512_k = new Array(\r\n
new int64(0x428a2f98, -685199838), new int64(0x71374491, 0x23ef65cd),\r\n
new int64(-1245643825, -330482897), new int64(-373957723, -2121671748),\r\n
new int64(0x3956c25b, -213338824), new int64(0x59f111f1, -1241133031),\r\n
new int64(-1841331548, -1357295717), new int64(-1424204075, -630357736),\r\n
new int64(-670586216, -1560083902), new int64(0x12835b01, 0x45706fbe),\r\n
new int64(0x243185be, 0x4ee4b28c), new int64(0x550c7dc3, -704662302),\r\n
new int64(0x72be5d74, -226784913), new int64(-2132889090, 0x3b1696b1),\r\n
new int64(-1680079193, 0x25c71235), new int64(-1046744716, -815192428),\r\n
new int64(-459576895, -1628353838), new int64(-272742522, 0x384f25e3),\r\n
new int64(0xfc19dc6, -1953704523), new int64(0x240ca1cc, 0x77ac9c65),\r\n
new int64(0x2de92c6f, 0x592b0275), new int64(0x4a7484aa, 0x6ea6e483),\r\n
new int64(0x5cb0a9dc, -1119749164), new int64(0x76f988da, -2096016459),\r\n
new int64(-1740746414, -295247957), new int64(-1473132947, 0x2db43210),\r\n
new int64(-1341970488, -1728372417), new int64(-1084653625, -1091629340),\r\n
new int64(-958395405, 0x3da88fc2), new int64(-710438585, -1828018395),\r\n
new int64(0x6ca6351, -536640913), new int64(0x14292967, 0xa0e6e70),\r\n
new int64(0x27b70a85, 0x46d22ffc), new int64(0x2e1b2138, 0x5c26c926),\r\n
new int64(0x4d2c6dfc, 0x5ac42aed), new int64(0x53380d13, -1651133473),\r\n
new int64(0x650a7354, -1951439906), new int64(0x766a0abb, 0x3c77b2a8),\r\n
new int64(-2117940946, 0x47edaee6), new int64(-1838011259, 0x1482353b),\r\n
new int64(-1564481375, 0x4cf10364), new int64(-1474664885, -1136513023),\r\n
new int64(-1035236496, -789014639), new int64(-949202525, 0x654be30),\r\n
new int64(-778901479, -688958952), new int64(-694614492, 0x5565a910),\r\n
new int64(-200395387, 0x5771202a), new int64(0x106aa070, 0x32bbd1b8),\r\n
new int64(0x19a4c116, -1194143544), new int64(0x1e376c08, 0x5141ab53),\r\n
new int64(0x2748774c, -544281703), new int64(0x34b0bcb5, -509917016),\r\n
new int64(0x391c0cb3, -976659869), new int64(0x4ed8aa4a, -482243893),\r\n
new int64(0x5b9cca4f, 0x7763e373), new int64(0x682e6ff3, -692930397),\r\n
new int64(0x748f82ee, 0x5defb2fc), new int64(0x78a5636f, 0x43172f60),\r\n
new int64(-2067236844, -1578062990), new int64(-1933114872, 0x1a6439ec),\r\n
new int64(-1866530822, 0x23631e28), new int64(-1538233109, -561857047),\r\n
new int64(-1090935817, -1295615723), new int64(-965641998, -479046869),\r\n
new int64(-903397682, -366583396), new int64(-779700025, 0x21c0c207),\r\n
new int64(-354779690, -840897762), new int64(-176337025, -294727304),\r\n
new int64(0x6f067aa, 0x72176fba), new int64(0xa637dc5, -1563912026),\r\n
new int64(0x113f9804, -1090974290), new int64(0x1b710b35, 0x131c471b),\r\n
new int64(0x28db77f5, 0x23047d84), new int64(0x32caab7b, 0x40c72493),\r\n
new int64(0x3c9ebe0a, 0x15c9bebc), new int64(0x431d67c4, -1676669620),\r\n
new int64(0x4cc5d4be, -885112138), new int64(0x597f299c, -60457430),\r\n
new int64(0x5fcb6fab, 0x3ad6faec), new int64(0x6c44198c, 0x4a475817));\r\n
  }\r\n
\r\n
  //Initial hash values\r\n
  var H = new Array(\r\n
new int64(0x6a09e667, -205731576),\r\n
new int64(-1150833019, -2067093701),\r\n
new int64(0x3c6ef372, -23791573),\r\n
new int64(-1521486534, 0x5f1d36f1),\r\n
new int64(0x510e527f, -1377402159),\r\n
new int64(-1694144372, 0x2b3e6c1f),\r\n
new int64(0x1f83d9ab, -79577749),\r\n
new int64(0x5be0cd19, 0x137e2179));\r\n
\r\n
  var T1 = new int64(0, 0),\r\n
    T2 = new int64(0, 0),\r\n
    a = new int64(0,0),\r\n
    b = new int64(0,0),\r\n
    c = new int64(0,0),\r\n
    d = new int64(0,0),\r\n
    e = new int64(0,0),\r\n
    f = new int64(0,0),\r\n
    g = new int64(0,0),\r\n
    h = new int64(0,0),\r\n
    //Temporary variables not specified by the document\r\n
    s0 = new int64(0, 0),\r\n
    s1 = new int64(0, 0),\r\n
    Ch = new int64(0, 0),\r\n
    Maj = new int64(0, 0),\r\n
    r1 = new int64(0, 0),\r\n
    r2 = new int64(0, 0),\r\n
    r3 = new int64(0, 0);\r\n
  var j, i;\r\n
  var W = new Array(80);\r\n
  for(i=0; i<80; i++)\r\n
    W[i] = new int64(0, 0);\r\n
\r\n
  // append padding to the source string. The format is described in the FIPS.\r\n
  x[len >> 5] |= 0x80 << (24 - (len & 0x1f));\r\n
  x[((len + 128 >> 10)<< 5) + 31] = len;\r\n
\r\n
  for(i = 0; i<x.length; i+=32) //32 dwords is the block size\r\n
  {\r\n
    int64copy(a, H[0]);\r\n
    int64copy(b, H[1]);\r\n
    int64copy(c, H[2]);\r\n
    int64copy(d, H[3]);\r\n
    int64copy(e, H[4]);\r\n
    int64copy(f, H[5]);\r\n
    int64copy(g, H[6]);\r\n
    int64copy(h, H[7]);\r\n
\r\n
    for(j=0; j<16; j++)\r\n
    {\r\n
        W[j].h = x[i + 2*j];\r\n
        W[j].l = x[i + 2*j + 1];\r\n
    }\r\n
\r\n
    for(j=16; j<80; j++)\r\n
    {\r\n
      //sigma1\r\n
      int64rrot(r1, W[j-2], 19);\r\n
      int64revrrot(r2, W[j-2], 29);\r\n
      int64shr(r3, W[j-2], 6);\r\n
      s1.l = r1.l ^ r2.l ^ r3.l;\r\n
      s1.h = r1.h ^ r2.h ^ r3.h;\r\n
      //sigma0\r\n
      int64rrot(r1, W[j-15], 1);\r\n
      int64rrot(r2, W[j-15], 8);\r\n
      int64shr(r3, W[j-15], 7);\r\n
      s0.l = r1.l ^ r2.l ^ r3.l;\r\n
      s0.h = r1.h ^ r2.h ^ r3.h;\r\n
\r\n
      int64add4(W[j], s1, W[j-7], s0, W[j-16]);\r\n
    }\r\n
\r\n
    for(j = 0; j < 80; j++)\r\n
    {\r\n
      //Ch\r\n
      Ch.l = (e.l & f.l) ^ (~e.l & g.l);\r\n
      Ch.h = (e.h & f.h) ^ (~e.h & g.h);\r\n
\r\n
      //Sigma1\r\n
      int64rrot(r1, e, 14);\r\n
      int64rrot(r2, e, 18);\r\n
      int64revrrot(r3, e, 9);\r\n
      s1.l = r1.l ^ r2.l ^ r3.l;\r\n
      s1.h = r1.h ^ r2.h ^ r3.h;\r\n
\r\n
      //Sigma0\r\n
      int64rrot(r1, a, 28);\r\n
      int64revrrot(r2, a, 2);\r\n
      int64revrrot(r3, a, 7);\r\n
      s0.l = r1.l ^ r2.l ^ r3.l;\r\n
      s0.h = r1.h ^ r2.h ^ r3.h;\r\n
\r\n
      //Maj\r\n
      Maj.l = (a.l & b.l) ^ (a.l & c.l) ^ (b.l & c.l);\r\n
      Maj.h = (a.h & b.h) ^ (a.h & c.h) ^ (b.h & c.h);\r\n
\r\n
      int64add5(T1, h, s1, Ch, sha512_k[j], W[j]);\r\n
      int64add(T2, s0, Maj);\r\n
\r\n
      int64copy(h, g);\r\n
      int64copy(g, f);\r\n
      int64copy(f, e);\r\n
      int64add(e, d, T1);\r\n
      int64copy(d, c);\r\n
      int64copy(c, b);\r\n
      int64copy(b, a);\r\n
      int64add(a, T1, T2);\r\n
    }\r\n
    int64add(H[0], H[0], a);\r\n
    int64add(H[1], H[1], b);\r\n
    int64add(H[2], H[2], c);\r\n
    int64add(H[3], H[3], d);\r\n
    int64add(H[4], H[4], e);\r\n
    int64add(H[5], H[5], f);\r\n
    int64add(H[6], H[6], g);\r\n
    int64add(H[7], H[7], h);\r\n
  }\r\n
\r\n
  //represent the hash as an array of 32-bit dwords\r\n
  var hash = new Array(16);\r\n
  for(i=0; i<8; i++)\r\n
  {\r\n
    hash[2*i] = H[i].h;\r\n
    hash[2*i + 1] = H[i].l;\r\n
  }\r\n
  return hash;\r\n
}\r\n
\r\n
//A constructor for 64-bit numbers\r\n
function int64(h, l)\r\n
{\r\n
  this.h = h;\r\n
  this.l = l;\r\n
  //this.toString = int64toString;\r\n
}\r\n
\r\n
//Copies src into dst, assuming both are 64-bit numbers\r\n
function int64copy(dst, src)\r\n
{\r\n
  dst.h = src.h;\r\n
  dst.l = src.l;\r\n
}\r\n
\r\n
//Right-rotates a 64-bit number by shift\r\n
//Won\'t handle cases of shift>=32\r\n
//The function revrrot() is for that\r\n
function int64rrot(dst, x, shift)\r\n
{\r\n
    dst.l = (x.l >>> shift) | (x.h << (32-shift));\r\n
    dst.h = (x.h >>> shift) | (x.l << (32-shift));\r\n
}\r\n
\r\n
//Reverses the dwords of the source and then rotates right by shift.\r\n
//This is equivalent to rotation by 32+shift\r\n
function int64revrrot(dst, x, shift)\r\n
{\r\n
    dst.l = (x.h >>> shift) | (x.l << (32-shift));\r\n
    dst.h = (x.l >>> shift) | (x.h << (32-shift));\r\n
}\r\n
\r\n
//Bitwise-shifts right a 64-bit number by shift\r\n
//Won\'t handle shift>=32, but it\'s never needed in SHA512\r\n
function int64shr(dst, x, shift)\r\n
{\r\n
    dst.l = (x.l >>> shift) | (x.h << (32-shift));\r\n
    dst.h = (x.h >>> shift);\r\n
}\r\n
\r\n
//Adds two 64-bit numbers\r\n
//Like the original implementation, does not rely on 32-bit operations\r\n
function int64add(dst, x, y)\r\n
{\r\n
   var w0 = (x.l & 0xffff) + (y.l & 0xffff);\r\n
   var w1 = (x.l >>> 16) + (y.l >>> 16) + (w0 >>> 16);\r\n
   var w2 = (x.h & 0xffff) + (y.h & 0xffff) + (w1 >>> 16);\r\n
   var w3 = (x.h >>> 16) + (y.h >>> 16) + (w2 >>> 16);\r\n
   dst.l = (w0 & 0xffff) | (w1 << 16);\r\n
   dst.h = (w2 & 0xffff) | (w3 << 16);\r\n
}\r\n
\r\n
//Same, except with 4 addends. Works faster than adding them one by one.\r\n
function int64add4(dst, a, b, c, d)\r\n
{\r\n
   var w0 = (a.l & 0xffff) + (b.l & 0xffff) + (c.l & 0xffff) + (d.l & 0xffff);\r\n
   var w1 = (a.l >>> 16) + (b.l >>> 16) + (c.l >>> 16) + (d.l >>> 16) + (w0 >>> 16);\r\n
   var w2 = (a.h & 0xffff) + (b.h & 0xffff) + (c.h & 0xffff) + (d.h & 0xffff) + (w1 >>> 16);\r\n
   var w3 = (a.h >>> 16) + (b.h >>> 16) + (c.h >>> 16) + (d.h >>> 16) + (w2 >>> 16);\r\n
   dst.l = (w0 & 0xffff) | (w1 << 16);\r\n
   dst.h = (w2 & 0xffff) | (w3 << 16);\r\n
}\r\n
\r\n
//Same, except with 5 addends\r\n
function int64add5(dst, a, b, c, d, e)\r\n
{\r\n
   var w0 = (a.l & 0xffff) + (b.l & 0xffff) + (c.l & 0xffff) + (d.l & 0xffff) + (e.l & 0xffff);\r\n
   var w1 = (a.l >>> 16) + (b.l >>> 16) + (c.l >>> 16) + (d.l >>> 16) + (e.l >>> 16) + (w0 >>> 16);\r\n
   var w2 = (a.h & 0xffff) + (b.h & 0xffff) + (c.h & 0xffff) + (d.h & 0xffff) + (e.h & 0xffff) + (w1 >>> 16);\r\n
   var w3 = (a.h >>> 16) + (b.h >>> 16) + (c.h >>> 16) + (d.h >>> 16) + (e.h >>> 16) + (w2 >>> 16);\r\n
   dst.l = (w0 & 0xffff) | (w1 << 16);\r\n
   dst.h = (w2 & 0xffff) | (w3 << 16);\r\n
}\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16337</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
