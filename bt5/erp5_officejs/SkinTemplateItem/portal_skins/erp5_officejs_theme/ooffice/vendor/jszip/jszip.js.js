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
            <value> <string>ts44314536.43</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jszip.js</string> </value>
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
            <value> <int>293472</int> </value>
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
\n
JSZip - A Javascript class for generating and reading zip files\n
<http://stuartk.com/jszip>\n
\n
(c) 2009-2014 Stuart Knightley <stuart [at] stuartk.com>\n
Dual licenced under the MIT license or GPLv3. See https://raw.github.com/Stuk/jszip/master/LICENSE.markdown.\n
\n
JSZip uses the library pako released under the MIT license :\n
https://github.com/nodeca/pako/blob/master/LICENSE\n
*/\n
!function(e){if("object"==typeof exports&&"undefined"!=typeof module)module.exports=e();else if("function"==typeof define&&define.amd)define([],e);else{var f;"undefined"!=typeof window?f=window:"undefined"!=typeof global?f=global:"undefined"!=typeof self&&(f=self),f.JSZip=e()}}(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module \'"+o+"\'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(_dereq_,module,exports){\n
\'use strict\';\n
// private property\n
var _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";\n
\n
\n
// public method for encoding\n
exports.encode = function(input, utf8) {\n
    var output = "";\n
    var chr1, chr2, chr3, enc1, enc2, enc3, enc4;\n
    var i = 0;\n
\n
    while (i < input.length) {\n
\n
        chr1 = input.charCodeAt(i++);\n
        chr2 = input.charCodeAt(i++);\n
        chr3 = input.charCodeAt(i++);\n
\n
        enc1 = chr1 >> 2;\n
        enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);\n
        enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);\n
        enc4 = chr3 & 63;\n
\n
        if (isNaN(chr2)) {\n
            enc3 = enc4 = 64;\n
        }\n
        else if (isNaN(chr3)) {\n
            enc4 = 64;\n
        }\n
\n
        output = output + _keyStr.charAt(enc1) + _keyStr.charAt(enc2) + _keyStr.charAt(enc3) + _keyStr.charAt(enc4);\n
\n
    }\n
\n
    return output;\n
};\n
\n
// public method for decoding\n
exports.decode = function(input, utf8) {\n
    var output = "";\n
    var chr1, chr2, chr3;\n
    var enc1, enc2, enc3, enc4;\n
    var i = 0;\n
\n
    input = input.replace(/[^A-Za-z0-9\\+\\/\\=]/g, "");\n
\n
    while (i < input.length) {\n
\n
        enc1 = _keyStr.indexOf(input.charAt(i++));\n
        enc2 = _keyStr.indexOf(input.charAt(i++));\n
        enc3 = _keyStr.indexOf(input.charAt(i++));\n
        enc4 = _keyStr.indexOf(input.charAt(i++));\n
\n
        chr1 = (enc1 << 2) | (enc2 >> 4);\n
        chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);\n
        chr3 = ((enc3 & 3) << 6) | enc4;\n
\n
        output = output + String.fromCharCode(chr1);\n
\n
        if (enc3 != 64) {\n
            output = output + String.fromCharCode(chr2);\n
        }\n
        if (enc4 != 64) {\n
            output = output + String.fromCharCode(chr3);\n
        }\n
\n
    }\n
\n
    return output;\n
\n
};\n
\n
},{}],2:[function(_dereq_,module,exports){\n
\'use strict\';\n
function CompressedObject() {\n
    this.compressedSize = 0;\n
    this.uncompressedSize = 0;\n
    this.crc32 = 0;\n
    this.compressionMethod = null;\n
    this.compressedContent = null;\n
}\n
\n
CompressedObject.prototype = {\n
    /**\n
     * Return the decompressed content in an unspecified format.\n
     * The format will depend on the decompressor.\n
     * @return {Object} the decompressed content.\n
     */\n
    getContent: function() {\n
        return null; // see implementation\n
    },\n
    /**\n
     * Return the compressed content in an unspecified format.\n
     * The format will depend on the compressed conten source.\n
     * @return {Object} the compressed content.\n
     */\n
    getCompressedContent: function() {\n
        return null; // see implementation\n
    }\n
};\n
module.exports = CompressedObject;\n
\n
},{}],3:[function(_dereq_,module,exports){\n
\'use strict\';\n
exports.STORE = {\n
    magic: "\\x00\\x00",\n
    compress: function(content, compressionOptions) {\n
        return content; // no compression\n
    },\n
    uncompress: function(content) {\n
        return content; // no compression\n
    },\n
    compressInputType: null,\n
    uncompressInputType: null\n
};\n
exports.DEFLATE = _dereq_(\'./flate\');\n
\n
},{"./flate":8}],4:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var utils = _dereq_(\'./utils\');\n
\n
var table = [\n
    0x00000000, 0x77073096, 0xEE0E612C, 0x990951BA,\n
    0x076DC419, 0x706AF48F, 0xE963A535, 0x9E6495A3,\n
    0x0EDB8832, 0x79DCB8A4, 0xE0D5E91E, 0x97D2D988,\n
    0x09B64C2B, 0x7EB17CBD, 0xE7B82D07, 0x90BF1D91,\n
    0x1DB71064, 0x6AB020F2, 0xF3B97148, 0x84BE41DE,\n
    0x1ADAD47D, 0x6DDDE4EB, 0xF4D4B551, 0x83D385C7,\n
    0x136C9856, 0x646BA8C0, 0xFD62F97A, 0x8A65C9EC,\n
    0x14015C4F, 0x63066CD9, 0xFA0F3D63, 0x8D080DF5,\n
    0x3B6E20C8, 0x4C69105E, 0xD56041E4, 0xA2677172,\n
    0x3C03E4D1, 0x4B04D447, 0xD20D85FD, 0xA50AB56B,\n
    0x35B5A8FA, 0x42B2986C, 0xDBBBC9D6, 0xACBCF940,\n
    0x32D86CE3, 0x45DF5C75, 0xDCD60DCF, 0xABD13D59,\n
    0x26D930AC, 0x51DE003A, 0xC8D75180, 0xBFD06116,\n
    0x21B4F4B5, 0x56B3C423, 0xCFBA9599, 0xB8BDA50F,\n
    0x2802B89E, 0x5F058808, 0xC60CD9B2, 0xB10BE924,\n
    0x2F6F7C87, 0x58684C11, 0xC1611DAB, 0xB6662D3D,\n
    0x76DC4190, 0x01DB7106, 0x98D220BC, 0xEFD5102A,\n
    0x71B18589, 0x06B6B51F, 0x9FBFE4A5, 0xE8B8D433,\n
    0x7807C9A2, 0x0F00F934, 0x9609A88E, 0xE10E9818,\n
    0x7F6A0DBB, 0x086D3D2D, 0x91646C97, 0xE6635C01,\n
    0x6B6B51F4, 0x1C6C6162, 0x856530D8, 0xF262004E,\n
    0x6C0695ED, 0x1B01A57B, 0x8208F4C1, 0xF50FC457,\n
    0x65B0D9C6, 0x12B7E950, 0x8BBEB8EA, 0xFCB9887C,\n
    0x62DD1DDF, 0x15DA2D49, 0x8CD37CF3, 0xFBD44C65,\n
    0x4DB26158, 0x3AB551CE, 0xA3BC0074, 0xD4BB30E2,\n
    0x4ADFA541, 0x3DD895D7, 0xA4D1C46D, 0xD3D6F4FB,\n
    0x4369E96A, 0x346ED9FC, 0xAD678846, 0xDA60B8D0,\n
    0x44042D73, 0x33031DE5, 0xAA0A4C5F, 0xDD0D7CC9,\n
    0x5005713C, 0x270241AA, 0xBE0B1010, 0xC90C2086,\n
    0x5768B525, 0x206F85B3, 0xB966D409, 0xCE61E49F,\n
    0x5EDEF90E, 0x29D9C998, 0xB0D09822, 0xC7D7A8B4,\n
    0x59B33D17, 0x2EB40D81, 0xB7BD5C3B, 0xC0BA6CAD,\n
    0xEDB88320, 0x9ABFB3B6, 0x03B6E20C, 0x74B1D29A,\n
    0xEAD54739, 0x9DD277AF, 0x04DB2615, 0x73DC1683,\n
    0xE3630B12, 0x94643B84, 0x0D6D6A3E, 0x7A6A5AA8,\n
    0xE40ECF0B, 0x9309FF9D, 0x0A00AE27, 0x7D079EB1,\n
    0xF00F9344, 0x8708A3D2, 0x1E01F268, 0x6906C2FE,\n
    0xF762575D, 0x806567CB, 0x196C3671, 0x6E6B06E7,\n
    0xFED41B76, 0x89D32BE0, 0x10DA7A5A, 0x67DD4ACC,\n
    0xF9B9DF6F, 0x8EBEEFF9, 0x17B7BE43, 0x60B08ED5,\n
    0xD6D6A3E8, 0xA1D1937E, 0x38D8C2C4, 0x4FDFF252,\n
    0xD1BB67F1, 0xA6BC5767, 0x3FB506DD, 0x48B2364B,\n
    0xD80D2BDA, 0xAF0A1B4C, 0x36034AF6, 0x41047A60,\n
    0xDF60EFC3, 0xA867DF55, 0x316E8EEF, 0x4669BE79,\n
    0xCB61B38C, 0xBC66831A, 0x256FD2A0, 0x5268E236,\n
    0xCC0C7795, 0xBB0B4703, 0x220216B9, 0x5505262F,\n
    0xC5BA3BBE, 0xB2BD0B28, 0x2BB45A92, 0x5CB36A04,\n
    0xC2D7FFA7, 0xB5D0CF31, 0x2CD99E8B, 0x5BDEAE1D,\n
    0x9B64C2B0, 0xEC63F226, 0x756AA39C, 0x026D930A,\n
    0x9C0906A9, 0xEB0E363F, 0x72076785, 0x05005713,\n
    0x95BF4A82, 0xE2B87A14, 0x7BB12BAE, 0x0CB61B38,\n
    0x92D28E9B, 0xE5D5BE0D, 0x7CDCEFB7, 0x0BDBDF21,\n
    0x86D3D2D4, 0xF1D4E242, 0x68DDB3F8, 0x1FDA836E,\n
    0x81BE16CD, 0xF6B9265B, 0x6FB077E1, 0x18B74777,\n
    0x88085AE6, 0xFF0F6A70, 0x66063BCA, 0x11010B5C,\n
    0x8F659EFF, 0xF862AE69, 0x616BFFD3, 0x166CCF45,\n
    0xA00AE278, 0xD70DD2EE, 0x4E048354, 0x3903B3C2,\n
    0xA7672661, 0xD06016F7, 0x4969474D, 0x3E6E77DB,\n
    0xAED16A4A, 0xD9D65ADC, 0x40DF0B66, 0x37D83BF0,\n
    0xA9BCAE53, 0xDEBB9EC5, 0x47B2CF7F, 0x30B5FFE9,\n
    0xBDBDF21C, 0xCABAC28A, 0x53B39330, 0x24B4A3A6,\n
    0xBAD03605, 0xCDD70693, 0x54DE5729, 0x23D967BF,\n
    0xB3667A2E, 0xC4614AB8, 0x5D681B02, 0x2A6F2B94,\n
    0xB40BBE37, 0xC30C8EA1, 0x5A05DF1B, 0x2D02EF8D\n
];\n
\n
/**\n
 *\n
 *  Javascript crc32\n
 *  http://www.webtoolkit.info/\n
 *\n
 */\n
module.exports = function crc32(input, crc) {\n
    if (typeof input === "undefined" || !input.length) {\n
        return 0;\n
    }\n
\n
    var isArray = utils.getTypeOf(input) !== "string";\n
\n
    if (typeof(crc) == "undefined") {\n
        crc = 0;\n
    }\n
    var x = 0;\n
    var y = 0;\n
    var b = 0;\n
\n
    crc = crc ^ (-1);\n
    for (var i = 0, iTop = input.length; i < iTop; i++) {\n
        b = isArray ? input[i] : input.charCodeAt(i);\n
        y = (crc ^ b) & 0xFF;\n
        x = table[y];\n
        crc = (crc >>> 8) ^ x;\n
    }\n
\n
    return crc ^ (-1);\n
};\n
// vim: set shiftwidth=4 softtabstop=4:\n
\n
},{"./utils":21}],5:[function(_dereq_,module,exports){\n
\'use strict\';\n
var utils = _dereq_(\'./utils\');\n
\n
function DataReader(data) {\n
    this.data = null; // type : see implementation\n
    this.length = 0;\n
    this.index = 0;\n
}\n
DataReader.prototype = {\n
    /**\n
     * Check that the offset will not go too far.\n
     * @param {string} offset the additional offset to check.\n
     * @throws {Error} an Error if the offset is out of bounds.\n
     */\n
    checkOffset: function(offset) {\n
        this.checkIndex(this.index + offset);\n
    },\n
    /**\n
     * Check that the specifed index will not be too far.\n
     * @param {string} newIndex the index to check.\n
     * @throws {Error} an Error if the index is out of bounds.\n
     */\n
    checkIndex: function(newIndex) {\n
        if (this.length < newIndex || newIndex < 0) {\n
            throw new Error("End of data reached (data length = " + this.length + ", asked index = " + (newIndex) + "). Corrupted zip ?");\n
        }\n
    },\n
    /**\n
     * Change the index.\n
     * @param {number} newIndex The new index.\n
     * @throws {Error} if the new index is out of the data.\n
     */\n
    setIndex: function(newIndex) {\n
        this.checkIndex(newIndex);\n
        this.index = newIndex;\n
    },\n
    /**\n
     * Skip the next n bytes.\n
     * @param {number} n the number of bytes to skip.\n
     * @throws {Error} if the new index is out of the data.\n
     */\n
    skip: function(n) {\n
        this.setIndex(this.index + n);\n
    },\n
    /**\n
     * Get the byte at the specified index.\n
     * @param {number} i the index to use.\n
     * @return {number} a byte.\n
     */\n
    byteAt: function(i) {\n
        // see implementations\n
    },\n
    /**\n
     * Get the next number with a given byte size.\n
     * @param {number} size the number of bytes to read.\n
     * @return {number} the corresponding number.\n
     */\n
    readInt: function(size) {\n
        var result = 0,\n
            i;\n
        this.checkOffset(size);\n
        for (i = this.index + size - 1; i >= this.index; i--) {\n
            result = (result << 8) + this.byteAt(i);\n
        }\n
        this.index += size;\n
        return result;\n
    },\n
    /**\n
     * Get the next string with a given byte size.\n
     * @param {number} size the number of bytes to read.\n
     * @return {string} the corresponding string.\n
     */\n
    readString: function(size) {\n
        return utils.transformTo("string", this.readData(size));\n
    },\n
    /**\n
     * Get raw data without conversion, <size> bytes.\n
     * @param {number} size the number of bytes to read.\n
     * @return {Object} the raw data, implementation specific.\n
     */\n
    readData: function(size) {\n
        // see implementations\n
    },\n
    /**\n
     * Find the last occurence of a zip signature (4 bytes).\n
     * @param {string} sig the signature to find.\n
     * @return {number} the index of the last occurence, -1 if not found.\n
     */\n
    lastIndexOfSignature: function(sig) {\n
        // see implementations\n
    },\n
    /**\n
     * Get the next date.\n
     * @return {Date} the date.\n
     */\n
    readDate: function() {\n
        var dostime = this.readInt(4);\n
        return new Date(\n
        ((dostime >> 25) & 0x7f) + 1980, // year\n
        ((dostime >> 21) & 0x0f) - 1, // month\n
        (dostime >> 16) & 0x1f, // day\n
        (dostime >> 11) & 0x1f, // hour\n
        (dostime >> 5) & 0x3f, // minute\n
        (dostime & 0x1f) << 1); // second\n
    }\n
};\n
module.exports = DataReader;\n
\n
},{"./utils":21}],6:[function(_dereq_,module,exports){\n
\'use strict\';\n
exports.base64 = false;\n
exports.binary = false;\n
exports.dir = false;\n
exports.createFolders = false;\n
exports.date = null;\n
exports.compression = null;\n
exports.compressionOptions = null;\n
exports.comment = null;\n
exports.unixPermissions = null;\n
exports.dosPermissions = null;\n
\n
},{}],7:[function(_dereq_,module,exports){\n
\'use strict\';\n
var utils = _dereq_(\'./utils\');\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.string2binary = function(str) {\n
    return utils.string2binary(str);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.string2Uint8Array = function(str) {\n
    return utils.transformTo("uint8array", str);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.uint8Array2String = function(array) {\n
    return utils.transformTo("string", array);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.string2Blob = function(str) {\n
    var buffer = utils.transformTo("arraybuffer", str);\n
    return utils.arrayBuffer2Blob(buffer);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.arrayBuffer2Blob = function(buffer) {\n
    return utils.arrayBuffer2Blob(buffer);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.transformTo = function(outputType, input) {\n
    return utils.transformTo(outputType, input);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.getTypeOf = function(input) {\n
    return utils.getTypeOf(input);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.checkSupport = function(type) {\n
    return utils.checkSupport(type);\n
};\n
\n
/**\n
 * @deprecated\n
 * This value will be removed in a future version without replacement.\n
 */\n
exports.MAX_VALUE_16BITS = utils.MAX_VALUE_16BITS;\n
\n
/**\n
 * @deprecated\n
 * This value will be removed in a future version without replacement.\n
 */\n
exports.MAX_VALUE_32BITS = utils.MAX_VALUE_32BITS;\n
\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.pretty = function(str) {\n
    return utils.pretty(str);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.findCompression = function(compressionMethod) {\n
    return utils.findCompression(compressionMethod);\n
};\n
\n
/**\n
 * @deprecated\n
 * This function will be removed in a future version without replacement.\n
 */\n
exports.isRegExp = function (object) {\n
    return utils.isRegExp(object);\n
};\n
\n
\n
},{"./utils":21}],8:[function(_dereq_,module,exports){\n
\'use strict\';\n
var USE_TYPEDARRAY = (typeof Uint8Array !== \'undefined\') && (typeof Uint16Array !== \'undefined\') && (typeof Uint32Array !== \'undefined\');\n
\n
var pako = _dereq_("pako");\n
exports.uncompressInputType = USE_TYPEDARRAY ? "uint8array" : "array";\n
exports.compressInputType = USE_TYPEDARRAY ? "uint8array" : "array";\n
\n
exports.magic = "\\x08\\x00";\n
exports.compress = function(input, compressionOptions) {\n
    return pako.deflateRaw(input, {\n
        level : compressionOptions.level || -1 // default compression\n
    });\n
};\n
exports.uncompress =  function(input) {\n
    return pako.inflateRaw(input);\n
};\n
\n
},{"pako":24}],9:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var base64 = _dereq_(\'./base64\');\n
\n
/**\n
Usage:\n
   zip = new JSZip();\n
   zip.file("hello.txt", "Hello, World!").file("tempfile", "nothing");\n
   zip.folder("images").file("smile.gif", base64Data, {base64: true});\n
   zip.file("Xmas.txt", "Ho ho ho !", {date : new Date("December 25, 2007 00:00:01")});\n
   zip.remove("tempfile");\n
\n
   base64zip = zip.generate();\n
\n
**/\n
\n
/**\n
 * Representation a of zip file in js\n
 * @constructor\n
 * @param {String=|ArrayBuffer=|Uint8Array=} data the data to load, if any (optional).\n
 * @param {Object=} options the options for creating this objects (optional).\n
 */\n
function JSZip(data, options) {\n
    // if this constructor is used without `new`, it adds `new` before itself:\n
    if(!(this instanceof JSZip)) return new JSZip(data, options);\n
\n
    // object containing the files :\n
    // {\n
    //   "folder/" : {...},\n
    //   "folder/data.txt" : {...}\n
    // }\n
    this.files = {};\n
\n
    this.comment = null;\n
\n
    // Where we are in the hierarchy\n
    this.root = "";\n
    if (data) {\n
        this.load(data, options);\n
    }\n
    this.clone = function() {\n
        var newObj = new JSZip();\n
        for (var i in this) {\n
            if (typeof this[i] !== "function") {\n
                newObj[i] = this[i];\n
            }\n
        }\n
        return newObj;\n
    };\n
}\n
JSZip.prototype = _dereq_(\'./object\');\n
JSZip.prototype.load = _dereq_(\'./load\');\n
JSZip.support = _dereq_(\'./support\');\n
JSZip.defaults = _dereq_(\'./defaults\');\n
\n
/**\n
 * @deprecated\n
 * This namespace will be removed in a future version without replacement.\n
 */\n
JSZip.utils = _dereq_(\'./deprecatedPublicUtils\');\n
\n
JSZip.base64 = {\n
    /**\n
     * @deprecated\n
     * This method will be removed in a future version without replacement.\n
     */\n
    encode : function(input) {\n
        return base64.encode(input);\n
    },\n
    /**\n
     * @deprecated\n
     * This method will be removed in a future version without replacement.\n
     */\n
    decode : function(input) {\n
        return base64.decode(input);\n
    }\n
};\n
JSZip.compressions = _dereq_(\'./compressions\');\n
module.exports = JSZip;\n
\n
},{"./base64":1,"./compressions":3,"./defaults":6,"./deprecatedPublicUtils":7,"./load":10,"./object":13,"./support":17}],10:[function(_dereq_,module,exports){\n
\'use strict\';\n
var base64 = _dereq_(\'./base64\');\n
var ZipEntries = _dereq_(\'./zipEntries\');\n
module.exports = function(data, options) {\n
    var files, zipEntries, i, input;\n
    options = options || {};\n
    if (options.base64) {\n
        data = base64.decode(data);\n
    }\n
\n
    zipEntries = new ZipEntries(data, options);\n
    files = zipEntries.files;\n
    for (i = 0; i < files.length; i++) {\n
        input = files[i];\n
        this.file(input.fileName, input.decompressed, {\n
            binary: true,\n
            optimizedBinaryString: true,\n
            date: input.date,\n
            dir: input.dir,\n
            comment : input.fileComment.length ? input.fileComment : null,\n
            unixPermissions : input.unixPermissions,\n
            dosPermissions : input.dosPermissions,\n
            createFolders: options.createFolders\n
        });\n
    }\n
    if (zipEntries.zipComment.length) {\n
        this.comment = zipEntries.zipComment;\n
    }\n
\n
    return this;\n
};\n
\n
},{"./base64":1,"./zipEntries":22}],11:[function(_dereq_,module,exports){\n
(function (Buffer){\n
\'use strict\';\n
module.exports = function(data, encoding){\n
    return new Buffer(data, encoding);\n
};\n
module.exports.test = function(b){\n
    return Buffer.isBuffer(b);\n
};\n
\n
}).call(this,(typeof Buffer !== "undefined" ? Buffer : undefined))\n
},{}],12:[function(_dereq_,module,exports){\n
\'use strict\';\n
var Uint8ArrayReader = _dereq_(\'./uint8ArrayReader\');\n
\n
function NodeBufferReader(data) {\n
    this.data = data;\n
    this.length = this.data.length;\n
    this.index = 0;\n
}\n
NodeBufferReader.prototype = new Uint8ArrayReader();\n
\n
/**\n
 * @see DataReader.readData\n
 */\n
NodeBufferReader.prototype.readData = function(size) {\n
    this.checkOffset(size);\n
    var result = this.data.slice(this.index, this.index + size);\n
    this.index += size;\n
    return result;\n
};\n
module.exports = NodeBufferReader;\n
\n
},{"./uint8ArrayReader":18}],13:[function(_dereq_,module,exports){\n
\'use strict\';\n
var support = _dereq_(\'./support\');\n
var utils = _dereq_(\'./utils\');\n
var crc32 = _dereq_(\'./crc32\');\n
var signature = _dereq_(\'./signature\');\n
var defaults = _dereq_(\'./defaults\');\n
var base64 = _dereq_(\'./base64\');\n
var compressions = _dereq_(\'./compressions\');\n
var CompressedObject = _dereq_(\'./compressedObject\');\n
var nodeBuffer = _dereq_(\'./nodeBuffer\');\n
var utf8 = _dereq_(\'./utf8\');\n
var StringWriter = _dereq_(\'./stringWriter\');\n
var Uint8ArrayWriter = _dereq_(\'./uint8ArrayWriter\');\n
\n
/**\n
 * Returns the raw data of a ZipObject, decompress the content if necessary.\n
 * @param {ZipObject} file the file to use.\n
 * @return {String|ArrayBuffer|Uint8Array|Buffer} the data.\n
 */\n
var getRawData = function(file) {\n
    if (file._data instanceof CompressedObject) {\n
        file._data = file._data.getContent();\n
        file.options.binary = true;\n
        file.options.base64 = false;\n
\n
        if (utils.getTypeOf(file._data) === "uint8array") {\n
            var copy = file._data;\n
            // when reading an arraybuffer, the CompressedObject mechanism will keep it and subarray() a Uint8Array.\n
            // if we request a file in the same format, we might get the same Uint8Array or its ArrayBuffer (the original zip file).\n
            file._data = new Uint8Array(copy.length);\n
            // with an empty Uint8Array, Opera fails with a "Offset larger than array size"\n
            if (copy.length !== 0) {\n
                file._data.set(copy, 0);\n
            }\n
        }\n
    }\n
    return file._data;\n
};\n
\n
/**\n
 * Returns the data of a ZipObject in a binary form. If the content is an unicode string, encode it.\n
 * @param {ZipObject} file the file to use.\n
 * @return {String|ArrayBuffer|Uint8Array|Buffer} the data.\n
 */\n
var getBinaryData = function(file) {\n
    var result = getRawData(file),\n
        type = utils.getTypeOf(result);\n
    if (type === "string") {\n
        if (!file.options.binary) {\n
            // unicode text !\n
            // unicode string => binary string is a painful process, check if we can avoid it.\n
            if (support.nodebuffer) {\n
                return nodeBuffer(result, "utf-8");\n
            }\n
        }\n
        return file.asBinary();\n
    }\n
    return result;\n
};\n
\n
/**\n
 * Transform this._data into a string.\n
 * @param {function} filter a function String -> String, applied if not null on the result.\n
 * @return {String} the string representing this._data.\n
 */\n
var dataToString = function(asUTF8) {\n
    var result = getRawData(this);\n
    if (result === null || typeof result === "undefined") {\n
        return "";\n
    }\n
    // if the data is a base64 string, we decode it before checking the encoding !\n
    if (this.options.base64) {\n
        result = base64.decode(result);\n
    }\n
    if (asUTF8 && this.options.binary) {\n
        // JSZip.prototype.utf8decode supports arrays as input\n
        // skip to array => string step, utf8decode will do it.\n
        result = out.utf8decode(result);\n
    }\n
    else {\n
        // no utf8 transformation, do the array => string step.\n
        result = utils.transformTo("string", result);\n
    }\n
\n
    if (!asUTF8 && !this.options.binary) {\n
        result = utils.transformTo("string", out.utf8encode(result));\n
    }\n
    return result;\n
};\n
/**\n
 * A simple object representing a file in the zip file.\n
 * @constructor\n
 * @param {string} name the name of the file\n
 * @param {String|ArrayBuffer|Uint8Array|Buffer} data the data\n
 * @param {Object} options the options of the file\n
 */\n
var ZipObject = function(name, data, options) {\n
    this.name = name;\n
    this.dir = options.dir;\n
    this.date = options.date;\n
    this.comment = options.comment;\n
    this.unixPermissions = options.unixPermissions;\n
    this.dosPermissions = options.dosPermissions;\n
\n
    this._data = data;\n
    this.options = options;\n
\n
    /*\n
     * This object contains initial values for dir and date.\n
     * With them, we can check if the user changed the deprecated metadata in\n
     * `ZipObject#options` or not.\n
     */\n
    this._initialMetadata = {\n
      dir : options.dir,\n
      date : options.date\n
    };\n
};\n
\n
ZipObject.prototype = {\n
    /**\n
     * Return the content as UTF8 string.\n
     * @return {string} the UTF8 string.\n
     */\n
    asText: function() {\n
        return dataToString.call(this, true);\n
    },\n
    /**\n
     * Returns the binary content.\n
     * @return {string} the content as binary.\n
     */\n
    asBinary: function() {\n
        return dataToString.call(this, false);\n
    },\n
    /**\n
     * Returns the content as a nodejs Buffer.\n
     * @return {Buffer} the content as a Buffer.\n
     */\n
    asNodeBuffer: function() {\n
        var result = getBinaryData(this);\n
        return utils.transformTo("nodebuffer", result);\n
    },\n
    /**\n
     * Returns the content as an Uint8Array.\n
     * @return {Uint8Array} the content as an Uint8Array.\n
     */\n
    asUint8Array: function() {\n
        var result = getBinaryData(this);\n
        return utils.transformTo("uint8array", result);\n
    },\n
    /**\n
     * Returns the content as an ArrayBuffer.\n
     * @return {ArrayBuffer} the content as an ArrayBufer.\n
     */\n
    asArrayBuffer: function() {\n
        return this.asUint8Array().buffer;\n
    }\n
};\n
\n
/**\n
 * Transform an integer into a string in hexadecimal.\n
 * @private\n
 * @param {number} dec the number to convert.\n
 * @param {number} bytes the number of bytes to generate.\n
 * @returns {string} the result.\n
 */\n
var decToHex = function(dec, bytes) {\n
    var hex = "",\n
        i;\n
    for (i = 0; i < bytes; i++) {\n
        hex += String.fromCharCode(dec & 0xff);\n
        dec = dec >>> 8;\n
    }\n
    return hex;\n
};\n
\n
/**\n
 * Merge the objects passed as parameters into a new one.\n
 * @private\n
 * @param {...Object} var_args All objects to merge.\n
 * @return {Object} a new object with the data of the others.\n
 */\n
var extend = function() {\n
    var result = {}, i, attr;\n
    for (i = 0; i < arguments.length; i++) { // arguments is not enumerable in some browsers\n
        for (attr in arguments[i]) {\n
            if (arguments[i].hasOwnProperty(attr) && typeof result[attr] === "undefined") {\n
                result[attr] = arguments[i][attr];\n
            }\n
        }\n
    }\n
    return result;\n
};\n
\n
/**\n
 * Transforms the (incomplete) options from the user into the complete\n
 * set of options to create a file.\n
 * @private\n
 * @param {Object} o the options from the user.\n
 * @return {Object} the complete set of options.\n
 */\n
var prepareFileAttrs = function(o) {\n
    o = o || {};\n
    if (o.base64 === true && (o.binary === null || o.binary === undefined)) {\n
        o.binary = true;\n
    }\n
    o = extend(o, defaults);\n
    o.date = o.date || new Date();\n
    if (o.compression !== null) o.compression = o.compression.toUpperCase();\n
\n
    return o;\n
};\n
\n
/**\n
 * Add a file in the current folder.\n
 * @private\n
 * @param {string} name the name of the file\n
 * @param {String|ArrayBuffer|Uint8Array|Buffer} data the data of the file\n
 * @param {Object} o the options of the file\n
 * @return {Object} the new file.\n
 */\n
var fileAdd = function(name, data, o) {\n
    // be sure sub folders exist\n
    var dataType = utils.getTypeOf(data),\n
        parent;\n
\n
    o = prepareFileAttrs(o);\n
\n
    if (typeof o.unixPermissions === "string") {\n
        o.unixPermissions = parseInt(o.unixPermissions, 8);\n
    }\n
\n
    // UNX_IFDIR  0040000 see zipinfo.c\n
    if (o.unixPermissions && (o.unixPermissions & 0x4000)) {\n
        o.dir = true;\n
    }\n
    // Bit 4    Directory\n
    if (o.dosPermissions && (o.dosPermissions & 0x0010)) {\n
        o.dir = true;\n
    }\n
\n
    if (o.dir) {\n
        name = forceTrailingSlash(name);\n
    }\n
\n
    if (o.createFolders && (parent = parentFolder(name))) {\n
        folderAdd.call(this, parent, true);\n
    }\n
\n
    if (o.dir || data === null || typeof data === "undefined") {\n
        o.base64 = false;\n
        o.binary = false;\n
        data = null;\n
        dataType = null;\n
    }\n
    else if (dataType === "string") {\n
        if (o.binary && !o.base64) {\n
            // optimizedBinaryString == true means that the file has already been filtered with a 0xFF mask\n
            if (o.optimizedBinaryString !== true) {\n
                // this is a string, not in a base64 format.\n
                // Be sure that this is a correct "binary string"\n
                data = utils.string2binary(data);\n
            }\n
        }\n
    }\n
    else { // arraybuffer, uint8array, ...\n
        o.base64 = false;\n
        o.binary = true;\n
\n
        if (!dataType && !(data instanceof CompressedObject)) {\n
            throw new Error("The data of \'" + name + "\' is in an unsupported format !");\n
        }\n
\n
        // special case : it\'s way easier to work with Uint8Array than with ArrayBuffer\n
        if (dataType === "arraybuffer") {\n
            data = utils.transformTo("uint8array", data);\n
        }\n
    }\n
\n
    var object = new ZipObject(name, data, o);\n
    this.files[name] = object;\n
    return object;\n
};\n
\n
/**\n
 * Find the parent folder of the path.\n
 * @private\n
 * @param {string} path the path to use\n
 * @return {string} the parent folder, or ""\n
 */\n
var parentFolder = function (path) {\n
    if (path.slice(-1) == \'/\') {\n
        path = path.substring(0, path.length - 1);\n
    }\n
    var lastSlash = path.lastIndexOf(\'/\');\n
    return (lastSlash > 0) ? path.substring(0, lastSlash) : "";\n
};\n
\n
\n
/**\n
 * Returns the path with a slash at the end.\n
 * @private\n
 * @param {String} path the path to check.\n
 * @return {String} the path with a trailing slash.\n
 */\n
var forceTrailingSlash = function(path) {\n
    // Check the name ends with a /\n
    if (path.slice(-1) != "/") {\n
        path += "/"; // IE doesn\'t like substr(-1)\n
    }\n
    return path;\n
};\n
/**\n
 * Add a (sub) folder in the current folder.\n
 * @private\n
 * @param {string} name the folder\'s name\n
 * @param {boolean=} [createFolders] If true, automatically create sub\n
 *  folders. Defaults to false.\n
 * @return {Object} the new folder.\n
 */\n
var folderAdd = function(name, createFolders) {\n
    createFolders = (typeof createFolders !== \'undefined\') ? createFolders : false;\n
\n
    name = forceTrailingSlash(name);\n
\n
    // Does this folder already exist?\n
    if (!this.files[name]) {\n
        fileAdd.call(this, name, null, {\n
            dir: true,\n
            createFolders: createFolders\n
        });\n
    }\n
    return this.files[name];\n
};\n
\n
/**\n
 * Generate a JSZip.CompressedObject for a given zipOject.\n
 * @param {ZipObject} file the object to read.\n
 * @param {JSZip.compression} compression the compression to use.\n
 * @param {Object} compressionOptions the options to use when compressing.\n
 * @return {JSZip.CompressedObject} the compressed result.\n
 */\n
var generateCompressedObjectFrom = function(file, compression, compressionOptions) {\n
    var result = new CompressedObject(),\n
        content;\n
\n
    // the data has not been decompressed, we might reuse things !\n
    if (file._data instanceof CompressedObject) {\n
        result.uncompressedSize = file._data.uncompressedSize;\n
        result.crc32 = file._data.crc32;\n
\n
        if (result.uncompressedSize === 0 || file.dir) {\n
            compression = compressions[\'STORE\'];\n
            result.compressedContent = "";\n
            result.crc32 = 0;\n
        }\n
        else if (file._data.compressionMethod === compression.magic) {\n
            result.compressedContent = file._data.getCompressedContent();\n
        }\n
        else {\n
            content = file._data.getContent();\n
            // need to decompress / recompress\n
            result.compressedContent = compression.compress(utils.transformTo(compression.compressInputType, content), compressionOptions);\n
        }\n
    }\n
    else {\n
        // have uncompressed data\n
        content = getBinaryData(file);\n
        if (!content || content.length === 0 || file.dir) {\n
            compression = compressions[\'STORE\'];\n
            content = "";\n
        }\n
        result.uncompressedSize = content.length;\n
        result.crc32 = crc32(content);\n
        result.compressedContent = compression.compress(utils.transformTo(compression.compressInputType, content), compressionOptions);\n
    }\n
\n
    result.compressedSize = result.compressedContent.length;\n
    result.compressionMethod = compression.magic;\n
\n
    return result;\n
};\n
\n
\n
\n
\n
/**\n
 * Generate the UNIX part of the external file attributes.\n
 * @param {Object} unixPermissions the unix permissions or null.\n
 * @param {Boolean} isDir true if the entry is a directory, false otherwise.\n
 * @return {Number} a 32 bit integer.\n
 *\n
 * adapted from http://unix.stackexchange.com/questions/14705/the-zip-formats-external-file-attribute :\n
 *\n
 * TTTTsstrwxrwxrwx0000000000ADVSHR\n
 * ^^^^____________________________ file type, see zipinfo.c (UNX_*)\n
 *     ^^^_________________________ setuid, setgid, sticky\n
 *        ^^^^^^^^^________________ permissions\n
 *                 ^^^^^^^^^^______ not used ?\n
 *                           ^^^^^^ DOS attribute bits : Archive, Directory, Volume label, System file, Hidden, Read only\n
 */\n
var generateUnixExternalFileAttr = function (unixPermissions, isDir) {\n
\n
    var result = unixPermissions;\n
    if (!unixPermissions) {\n
        // I can\'t use octal values in strict mode, hence the hexa.\n
        //  040775 => 0x41fd\n
        // 0100664 => 0x81b4\n
        result = isDir ? 0x41fd : 0x81b4;\n
    }\n
\n
    return (result & 0xFFFF) << 16;\n
};\n
\n
/**\n
 * Generate the DOS part of the external file attributes.\n
 * @param {Object} dosPermissions the dos permissions or null.\n
 * @param {Boolean} isDir true if the entry is a directory, false otherwise.\n
 * @return {Number} a 32 bit integer.\n
 *\n
 * Bit 0     Read-Only\n
 * Bit 1     Hidden\n
 * Bit 2     System\n
 * Bit 3     Volume Label\n
 * Bit 4     Directory\n
 * Bit 5     Archive\n
 */\n
var generateDosExternalFileAttr = function (dosPermissions, isDir) {\n
\n
    // the dir flag is already set for compatibility\n
\n
    return (dosPermissions || 0)  & 0x3F;\n
};\n
\n
/**\n
 * Generate the various parts used in the construction of the final zip file.\n
 * @param {string} name the file name.\n
 * @param {ZipObject} file the file content.\n
 * @param {JSZip.CompressedObject} compressedObject the compressed object.\n
 * @param {number} offset the current offset from the start of the zip file.\n
 * @param {String} platform let\'s pretend we are this platform (change platform dependents fields)\n
 * @return {object} the zip parts.\n
 */\n
var generateZipParts = function(name, file, compressedObject, offset, platform) {\n
    var data = compressedObject.compressedContent,\n
        utfEncodedFileName = utils.transformTo("string", utf8.utf8encode(file.name)),\n
        comment = file.comment || "",\n
        utfEncodedComment = utils.transformTo("string", utf8.utf8encode(comment)),\n
        useUTF8ForFileName = utfEncodedFileName.length !== file.name.length,\n
        useUTF8ForComment = utfEncodedComment.length !== comment.length,\n
        o = file.options,\n
        dosTime,\n
        dosDate,\n
        extraFields = "",\n
        unicodePathExtraField = "",\n
        unicodeCommentExtraField = "",\n
        dir, date;\n
\n
\n
    // handle the deprecated options.dir\n
    if (file._initialMetadata.dir !== file.dir) {\n
        dir = file.dir;\n
    } else {\n
        dir = o.dir;\n
    }\n
\n
    // handle the deprecated options.date\n
    if(file._initialMetadata.date !== file.date) {\n
        date = file.date;\n
    } else {\n
        date = o.date;\n
    }\n
\n
    var extFileAttr = 0;\n
    var versionMadeBy = 0;\n
    if (dir) {\n
        // dos or unix, we set the dos dir flag\n
        extFileAttr |= 0x00010;\n
    }\n
    if(platform === "UNIX") {\n
        versionMadeBy = 0x031E; // UNIX, version 3.0\n
        extFileAttr |= generateUnixExternalFileAttr(file.unixPermissions, dir);\n
    } else { // DOS or other, fallback to DOS\n
        versionMadeBy = 0x0014; // DOS, version 2.0\n
        extFileAttr |= generateDosExternalFileAttr(file.dosPermissions, dir);\n
    }\n
\n
    // date\n
    // @see http://www.delorie.com/djgpp/doc/rbinter/it/52/13.html\n
    // @see http://www.delorie.com/djgpp/doc/rbinter/it/65/16.html\n
    // @see http://www.delorie.com/djgpp/doc/rbinter/it/66/16.html\n
\n
    dosTime = date.getHours();\n
    dosTime = dosTime << 6;\n
    dosTime = dosTime | date.getMinutes();\n
    dosTime = dosTime << 5;\n
    dosTime = dosTime | date.getSeconds() / 2;\n
\n
    dosDate = date.getFullYear() - 1980;\n
    dosDate = dosDate << 4;\n
    dosDate = dosDate | (date.getMonth() + 1);\n
    dosDate = dosDate << 5;\n
    dosDate = dosDate | date.getDate();\n
\n
    if (useUTF8ForFileName) {\n
        // set the unicode path extra field. unzip needs at least one extra\n
        // field to correctly handle unicode path, so using the path is as good\n
        // as any other information. This could improve the situation with\n
        // other archive managers too.\n
        // This field is usually used without the utf8 flag, with a non\n
        // unicode path in the header (winrar, winzip). This helps (a bit)\n
        // with the messy Windows\' default compressed folders feature but\n
        // breaks on p7zip which doesn\'t seek the unicode path extra field.\n
        // So for now, UTF-8 everywhere !\n
        unicodePathExtraField =\n
            // Version\n
            decToHex(1, 1) +\n
            // NameCRC32\n
            decToHex(crc32(utfEncodedFileName), 4) +\n
            // UnicodeName\n
            utfEncodedFileName;\n
\n
        extraFields +=\n
            // Info-ZIP Unicode Path Extra Field\n
            "\\x75\\x70" +\n
            // size\n
            decToHex(unicodePathExtraField.length, 2) +\n
            // content\n
            unicodePathExtraField;\n
    }\n
\n
    if(useUTF8ForComment) {\n
\n
        unicodeCommentExtraField =\n
            // Version\n
            decToHex(1, 1) +\n
            // CommentCRC32\n
            decToHex(this.crc32(utfEncodedComment), 4) +\n
            // UnicodeName\n
            utfEncodedComment;\n
\n
        extraFields +=\n
            // Info-ZIP Unicode Path Extra Field\n
            "\\x75\\x63" +\n
            // size\n
            decToHex(unicodeCommentExtraField.length, 2) +\n
            // content\n
            unicodeCommentExtraField;\n
    }\n
\n
    var header = "";\n
\n
    // version needed to extract\n
    header += "\\x0A\\x00";\n
    // general purpose bit flag\n
    // set bit 11 if utf8\n
    header += (useUTF8ForFileName || useUTF8ForComment) ? "\\x00\\x08" : "\\x00\\x00";\n
    // compression method\n
    header += compressedObject.compressionMethod;\n
    // last mod file time\n
    header += decToHex(dosTime, 2);\n
    // last mod file date\n
    header += decToHex(dosDate, 2);\n
    // crc-32\n
    header += decToHex(compressedObject.crc32, 4);\n
    // compressed size\n
    header += decToHex(compressedObject.compressedSize, 4);\n
    // uncompressed size\n
    header += decToHex(compressedObject.uncompressedSize, 4);\n
    // file name length\n
    header += decToHex(utfEncodedFileName.length, 2);\n
    // extra field length\n
    header += decToHex(extraFields.length, 2);\n
\n
\n
    var fileRecord = signature.LOCAL_FILE_HEADER + header + utfEncodedFileName + extraFields;\n
\n
    var dirRecord = signature.CENTRAL_FILE_HEADER +\n
    // version made by (00: DOS)\n
    decToHex(versionMadeBy, 2) +\n
    // file header (common to file and central directory)\n
    header +\n
    // file comment length\n
    decToHex(utfEncodedComment.length, 2) +\n
    // disk number start\n
    "\\x00\\x00" +\n
    // internal file attributes TODO\n
    "\\x00\\x00" +\n
    // external file attributes\n
    decToHex(extFileAttr, 4) +\n
    // relative offset of local header\n
    decToHex(offset, 4) +\n
    // file name\n
    utfEncodedFileName +\n
    // extra field\n
    extraFields +\n
    // file comment\n
    utfEncodedComment;\n
\n
    return {\n
        fileRecord: fileRecord,\n
        dirRecord: dirRecord,\n
        compressedObject: compressedObject\n
    };\n
};\n
\n
\n
// return the actual prototype of JSZip\n
var out = {\n
    /**\n
     * Read an existing zip and merge the data in the current JSZip object.\n
     * The implementation is in jszip-load.js, don\'t forget to include it.\n
     * @param {String|ArrayBuffer|Uint8Array|Buffer} stream  The stream to load\n
     * @param {Object} options Options for loading the stream.\n
     *  options.base64 : is the stream in base64 ? default : false\n
     * @return {JSZip} the current JSZip object\n
     */\n
    load: function(stream, options) {\n
        throw new Error("Load method is not defined. Is the file jszip-load.js included ?");\n
    },\n
\n
    /**\n
     * Filter nested files/folders with the specified function.\n
     * @param {Function} search the predicate to use :\n
     * function (relativePath, file) {...}\n
     * It takes 2 arguments : the relative path and the file.\n
     * @return {Array} An array of matching elements.\n
     */\n
    filter: function(search) {\n
        var result = [],\n
            filename, relativePath, file, fileClone;\n
        for (filename in this.files) {\n
            if (!this.files.hasOwnProperty(filename)) {\n
                continue;\n
            }\n
            file = this.files[filename];\n
            // return a new object, don\'t let the user mess with our internal objects :)\n
            fileClone = new ZipObject(file.name, file._data, extend(file.options));\n
            relativePath = filename.slice(this.root.length, filename.length);\n
            if (filename.slice(0, this.root.length) === this.root && // the file is in the current root\n
            search(relativePath, fileClone)) { // and the file matches the function\n
                result.push(fileClone);\n
            }\n
        }\n
        return result;\n
    },\n
\n
    /**\n
     * Add a file to the zip file, or search a file.\n
     * @param   {string|RegExp} name The name of the file to add (if data is defined),\n
     * the name of the file to find (if no data) or a regex to match files.\n
     * @param   {String|ArrayBuffer|Uint8Array|Buffer} data  The file data, either raw or base64 encoded\n
     * @param   {Object} o     File options\n
     * @return  {JSZip|Object|Array} this JSZip object (when adding a file),\n
     * a file (when searching by string) or an array of files (when searching by regex).\n
     */\n
    file: function(name, data, o) {\n
        if (arguments.length === 1) {\n
            if (utils.isRegExp(name)) {\n
                var regexp = name;\n
                return this.filter(function(relativePath, file) {\n
                    return !file.dir && regexp.test(relativePath);\n
                });\n
            }\n
            else { // text\n
                return this.filter(function(relativePath, file) {\n
                    return !file.dir && relativePath === name;\n
                })[0] || null;\n
            }\n
        }\n
        else { // more than one argument : we have data !\n
            name = this.root + name;\n
            fileAdd.call(this, name, data, o);\n
        }\n
        return this;\n
    },\n
\n
    /**\n
     * Add a directory to the zip file, or search.\n
     * @param   {String|RegExp} arg The name of the directory to add, or a regex to search folders.\n
     * @return  {JSZip} an object with the new directory as the root, or an array containing matching folders.\n
     */\n
    folder: function(arg) {\n
        if (!arg) {\n
            return this;\n
        }\n
\n
        if (utils.isRegExp(arg)) {\n
            return this.filter(function(relativePath, file) {\n
                return file.dir && arg.test(relativePath);\n
            });\n
        }\n
\n
        // else, name is a new folder\n
        var name = this.root + arg;\n
        var newFolder = folderAdd.call(this, name);\n
\n
        // Allow chaining by returning a new object with this folder as the root\n
        var ret = this.clone();\n
        ret.root = newFolder.name;\n
        return ret;\n
    },\n
\n
    /**\n
     * Delete a file, or a directory and all sub-files, from the zip\n
     * @param {string} name the name of the file to delete\n
     * @return {JSZip} this JSZip object\n
     */\n
    remove: function(name) {\n
        name = this.root + name;\n
        var file = this.files[name];\n
        if (!file) {\n
            // Look for any folders\n
            if (name.slice(-1) != "/") {\n
                name += "/";\n
            }\n
            file = this.files[name];\n
        }\n
\n
        if (file && !file.dir) {\n
            // file\n
            delete this.files[name];\n
        } else {\n
            // maybe a folder, delete recursively\n
            var kids = this.filter(function(relativePath, file) {\n
                return file.name.slice(0, name.length) === name;\n
            });\n
            for (var i = 0; i < kids.length; i++) {\n
                delete this.files[kids[i].name];\n
            }\n
        }\n
\n
        return this;\n
    },\n
\n
    /**\n
     * Generate the complete zip file\n
     * @param {Object} options the options to generate the zip file :\n
     * - base64, (deprecated, use type instead) true to generate base64.\n
     * - compression, "STORE" by default.\n
     * - type, "base64" by default. Values are : string, base64, uint8array, arraybuffer, blob.\n
     * @return {String|Uint8Array|ArrayBuffer|Buffer|Blob} the zip file\n
     */\n
    generate: function(options) {\n
        options = extend(options || {}, {\n
            base64: true,\n
            compression: "STORE",\n
            compressionOptions : null,\n
            type: "base64",\n
            platform: "DOS",\n
            comment: null,\n
            mimeType: \'application/zip\'\n
        });\n
\n
        utils.checkSupport(options.type);\n
\n
        // accept nodejs `process.platform`\n
        if(\n
          options.platform === \'darwin\' ||\n
          options.platform === \'freebsd\' ||\n
          options.platform === \'linux\' ||\n
          options.platform === \'sunos\'\n
        ) {\n
          options.platform = "UNIX";\n
        }\n
        if (options.platform === \'win32\') {\n
          options.platform = "DOS";\n
        }\n
\n
        var zipData = [],\n
            localDirLength = 0,\n
            centralDirLength = 0,\n
            writer, i,\n
            utfEncodedComment = utils.transformTo("string", this.utf8encode(options.comment || this.comment || ""));\n
\n
        // first, generate all the zip parts.\n
        for (var name in this.files) {\n
            if (!this.files.hasOwnProperty(name)) {\n
                continue;\n
            }\n
            var file = this.files[name];\n
\n
            var compressionName = file.options.compression || options.compression.toUpperCase();\n
            var compression = compressions[compressionName];\n
            if (!compression) {\n
                throw new Error(compressionName + " is not a valid compression method !");\n
            }\n
            var compressionOptions = file.options.compressionOptions || options.compressionOptions || {};\n
\n
            var compressedObject = generateCompressedObjectFrom.call(this, file, compression, compressionOptions);\n
\n
            var zipPart = generateZipParts.call(this, name, file, compressedObject, localDirLength, options.platform);\n
            localDirLength += zipPart.fileRecord.length + compressedObject.compressedSize;\n
            centralDirLength += zipPart.dirRecord.length;\n
            zipData.push(zipPart);\n
        }\n
\n
        var dirEnd = "";\n
\n
        // end of central dir signature\n
        dirEnd = signature.CENTRAL_DIRECTORY_END +\n
        // number of this disk\n
        "\\x00\\x00" +\n
        // number of the disk with the start of the central directory\n
        "\\x00\\x00" +\n
        // total number of entries in the central directory on this disk\n
        decToHex(zipData.length, 2) +\n
        // total number of entries in the central directory\n
        decToHex(zipData.length, 2) +\n
        // size of the central directory   4 bytes\n
        decToHex(centralDirLength, 4) +\n
        // offset of start of central directory with respect to the starting disk number\n
        decToHex(localDirLength, 4) +\n
        // .ZIP file comment length\n
        decToHex(utfEncodedComment.length, 2) +\n
        // .ZIP file comment\n
        utfEncodedComment;\n
\n
\n
        // we have all the parts (and the total length)\n
        // time to create a writer !\n
        var typeName = options.type.toLowerCase();\n
        if(typeName==="uint8array"||typeName==="arraybuffer"||typeName==="blob"||typeName==="nodebuffer") {\n
            writer = new Uint8ArrayWriter(localDirLength + centralDirLength + dirEnd.length);\n
        }else{\n
            writer = new StringWriter(localDirLength + centralDirLength + dirEnd.length);\n
        }\n
\n
        for (i = 0; i < zipData.length; i++) {\n
            writer.append(zipData[i].fileRecord);\n
            writer.append(zipData[i].compressedObject.compressedContent);\n
        }\n
        for (i = 0; i < zipData.length; i++) {\n
            writer.append(zipData[i].dirRecord);\n
        }\n
\n
        writer.append(dirEnd);\n
\n
        var zip = writer.finalize();\n
\n
\n
\n
        switch(options.type.toLowerCase()) {\n
            // case "zip is an Uint8Array"\n
            case "uint8array" :\n
            case "arraybuffer" :\n
            case "nodebuffer" :\n
               return utils.transformTo(options.type.toLowerCase(), zip);\n
            case "blob" :\n
               return utils.arrayBuffer2Blob(utils.transformTo("arraybuffer", zip), options.mimeType);\n
            // case "zip is a string"\n
            case "base64" :\n
               return (options.base64) ? base64.encode(zip) : zip;\n
            default : // case "string" :\n
               return zip;\n
         }\n
\n
    },\n
\n
    /**\n
     * @deprecated\n
     * This method will be removed in a future version without replacement.\n
     */\n
    crc32: function (input, crc) {\n
        return crc32(input, crc);\n
    },\n
\n
    /**\n
     * @deprecated\n
     * This method will be removed in a future version without replacement.\n
     */\n
    utf8encode: function (string) {\n
        return utils.transformTo("string", utf8.utf8encode(string));\n
    },\n
\n
    /**\n
     * @deprecated\n
     * This method will be removed in a future version without replacement.\n
     */\n
    utf8decode: function (input) {\n
        return utf8.utf8decode(input);\n
    }\n
};\n
module.exports = out;\n
\n
},{"./base64":1,"./compressedObject":2,"./compressions":3,"./crc32":4,"./defaults":6,"./nodeBuffer":11,"./signature":14,"./stringWriter":16,"./support":17,"./uint8ArrayWriter":19,"./utf8":20,"./utils":21}],14:[function(_dereq_,module,exports){\n
\'use strict\';\n
exports.LOCAL_FILE_HEADER = "PK\\x03\\x04";\n
exports.CENTRAL_FILE_HEADER = "PK\\x01\\x02";\n
exports.CENTRAL_DIRECTORY_END = "PK\\x05\\x06";\n
exports.ZIP64_CENTRAL_DIRECTORY_LOCATOR = "PK\\x06\\x07";\n
exports.ZIP64_CENTRAL_DIRECTORY_END = "PK\\x06\\x06";\n
exports.DATA_DESCRIPTOR = "PK\\x07\\x08";\n
\n
},{}],15:[function(_dereq_,module,exports){\n
\'use strict\';\n
var DataReader = _dereq_(\'./dataReader\');\n
var utils = _dereq_(\'./utils\');\n
\n
function StringReader(data, optimizedBinaryString) {\n
    this.data = data;\n
    if (!optimizedBinaryString) {\n
        this.data = utils.string2binary(this.data);\n
    }\n
    this.length = this.data.length;\n
    this.index = 0;\n
}\n
StringReader.prototype = new DataReader();\n
/**\n
 * @see DataReader.byteAt\n
 */\n
StringReader.prototype.byteAt = function(i) {\n
    return this.data.charCodeAt(i);\n
};\n
/**\n
 * @see DataReader.lastIndexOfSignature\n
 */\n
StringReader.prototype.lastIndexOfSignature = function(sig) {\n
    return this.data.lastIndexOf(sig);\n
};\n
/**\n
 * @see DataReader.readData\n
 */\n
StringReader.prototype.readData = function(size) {\n
    this.checkOffset(size);\n
    // this will work because the constructor applied the "& 0xff" mask.\n
    var result = this.data.slice(this.index, this.index + size);\n
    this.index += size;\n
    return result;\n
};\n
module.exports = StringReader;\n
\n
},{"./dataReader":5,"./utils":21}],16:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var utils = _dereq_(\'./utils\');\n
\n
/**\n
 * An object to write any content to a string.\n
 * @constructor\n
 */\n
var StringWriter = function() {\n
    this.data = [];\n
};\n
StringWriter.prototype = {\n
    /**\n
     * Append any content to the current string.\n
     * @param {Object} input the content to add.\n
     */\n
    append: function(input) {\n
        input = utils.transformTo("string", input);\n
        this.data.push(input);\n
    },\n
    /**\n
     * Finalize the construction an return the result.\n
     * @return {string} the generated string.\n
     */\n
    finalize: function() {\n
        return this.data.join("");\n
    }\n
};\n
\n
module.exports = StringWriter;\n
\n
},{"./utils":21}],17:[function(_dereq_,module,exports){\n
(function (Buffer){\n
\'use strict\';\n
exports.base64 = true;\n
exports.array = true;\n
exports.string = true;\n
exports.arraybuffer = typeof ArrayBuffer !== "undefined" && typeof Uint8Array !== "undefined";\n
// contains true if JSZip can read/generate nodejs Buffer, false otherwise.\n
// Browserify will provide a Buffer implementation for browsers, which is\n
// an augmented Uint8Array (i.e., can be used as either Buffer or U8).\n
exports.nodebuffer = typeof Buffer !== "undefined";\n
// contains true if JSZip can read/generate Uint8Array, false otherwise.\n
exports.uint8array = typeof Uint8Array !== "undefined";\n
\n
if (typeof ArrayBuffer === "undefined") {\n
    exports.blob = false;\n
}\n
else {\n
    var buffer = new ArrayBuffer(0);\n
    try {\n
        exports.blob = new Blob([buffer], {\n
            type: "application/zip"\n
        }).size === 0;\n
    }\n
    catch (e) {\n
        try {\n
            var Builder = window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder || window.MSBlobBuilder;\n
            var builder = new Builder();\n
            builder.append(buffer);\n
            exports.blob = builder.getBlob(\'application/zip\').size === 0;\n
        }\n
        catch (e) {\n
            exports.blob = false;\n
        }\n
    }\n
}\n
\n
}).call(this,(typeof Buffer !== "undefined" ? Buffer : undefined))\n
},{}],18:[function(_dereq_,module,exports){\n
\'use strict\';\n
var DataReader = _dereq_(\'./dataReader\');\n
\n
function Uint8ArrayReader(data) {\n
    if (data) {\n
        this.data = data;\n
        this.length = this.data.length;\n
        this.index = 0;\n
    }\n
}\n
Uint8ArrayReader.prototype = new DataReader();\n
/**\n
 * @see DataReader.byteAt\n
 */\n
Uint8ArrayReader.prototype.byteAt = function(i) {\n
    return this.data[i];\n
};\n
/**\n
 * @see DataReader.lastIndexOfSignature\n
 */\n
Uint8ArrayReader.prototype.lastIndexOfSignature = function(sig) {\n
    var sig0 = sig.charCodeAt(0),\n
        sig1 = sig.charCodeAt(1),\n
        sig2 = sig.charCodeAt(2),\n
        sig3 = sig.charCodeAt(3);\n
    for (var i = this.length - 4; i >= 0; --i) {\n
        if (this.data[i] === sig0 && this.data[i + 1] === sig1 && this.data[i + 2] === sig2 && this.data[i + 3] === sig3) {\n
            return i;\n
        }\n
    }\n
\n
    return -1;\n
};\n
/**\n
 * @see DataReader.readData\n
 */\n
Uint8ArrayReader.prototype.readData = function(size) {\n
    this.checkOffset(size);\n
    if(size === 0) {\n
        // in IE10, when using subarray(idx, idx), we get the array [0x00] instead of [].\n
        return new Uint8Array(0);\n
    }\n
    var result = this.data.subarray(this.index, this.index + size);\n
    this.index += size;\n
    return result;\n
};\n
module.exports = Uint8ArrayReader;\n
\n
},{"./dataReader":5}],19:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var utils = _dereq_(\'./utils\');\n
\n
/**\n
 * An object to write any content to an Uint8Array.\n
 * @constructor\n
 * @param {number} length The length of the array.\n
 */\n
var Uint8ArrayWriter = function(length) {\n
    this.data = new Uint8Array(length);\n
    this.index = 0;\n
};\n
Uint8ArrayWriter.prototype = {\n
    /**\n
     * Append any content to the current array.\n
     * @param {Object} input the content to add.\n
     */\n
    append: function(input) {\n
        if (input.length !== 0) {\n
            // with an empty Uint8Array, Opera fails with a "Offset larger than array size"\n
            input = utils.transformTo("uint8array", input);\n
            this.data.set(input, this.index);\n
            this.index += input.length;\n
        }\n
    },\n
    /**\n
     * Finalize the construction an return the result.\n
     * @return {Uint8Array} the generated array.\n
     */\n
    finalize: function() {\n
        return this.data;\n
    }\n
};\n
\n
module.exports = Uint8ArrayWriter;\n
\n
},{"./utils":21}],20:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var utils = _dereq_(\'./utils\');\n
var support = _dereq_(\'./support\');\n
var nodeBuffer = _dereq_(\'./nodeBuffer\');\n
\n
/**\n
 * The following functions come from pako, from pako/lib/utils/strings\n
 * released under the MIT license, see pako https://github.com/nodeca/pako/\n
 */\n
\n
// Table with utf8 lengths (calculated by first byte of sequence)\n
// Note, that 5 & 6-byte values and some 4-byte values can not be represented in JS,\n
// because max possible codepoint is 0x10ffff\n
var _utf8len = new Array(256);\n
for (var i=0; i<256; i++) {\n
  _utf8len[i] = (i >= 252 ? 6 : i >= 248 ? 5 : i >= 240 ? 4 : i >= 224 ? 3 : i >= 192 ? 2 : 1);\n
}\n
_utf8len[254]=_utf8len[254]=1; // Invalid sequence start\n
\n
// convert string to array (typed, when possible)\n
var string2buf = function (str) {\n
    var buf, c, c2, m_pos, i, str_len = str.length, buf_len = 0;\n
\n
    // count binary size\n
    for (m_pos = 0; m_pos < str_len; m_pos++) {\n
        c = str.charCodeAt(m_pos);\n
        if ((c & 0xfc00) === 0xd800 && (m_pos+1 < str_len)) {\n
            c2 = str.charCodeAt(m_pos+1);\n
            if ((c2 & 0xfc00) === 0xdc00) {\n
                c = 0x10000 + ((c - 0xd800) << 10) + (c2 - 0xdc00);\n
                m_pos++;\n
            }\n
        }\n
        buf_len += c < 0x80 ? 1 : c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;\n
    }\n
\n
    // allocate buffer\n
    if (support.uint8array) {\n
        buf = new Uint8Array(buf_len);\n
    } else {\n
        buf = new Array(buf_len);\n
    }\n
\n
    // convert\n
    for (i=0, m_pos = 0; i < buf_len; m_pos++) {\n
        c = str.charCodeAt(m_pos);\n
        if ((c & 0xfc00) === 0xd800 && (m_pos+1 < str_len)) {\n
            c2 = str.charCodeAt(m_pos+1);\n
            if ((c2 & 0xfc00) === 0xdc00) {\n
                c = 0x10000 + ((c - 0xd800) << 10) + (c2 - 0xdc00);\n
                m_pos++;\n
            }\n
        }\n
        if (c < 0x80) {\n
            /* one byte */\n
            buf[i++] = c;\n
        } else if (c < 0x800) {\n
            /* two bytes */\n
            buf[i++] = 0xC0 | (c >>> 6);\n
            buf[i++] = 0x80 | (c & 0x3f);\n
        } else if (c < 0x10000) {\n
            /* three bytes */\n
            buf[i++] = 0xE0 | (c >>> 12);\n
            buf[i++] = 0x80 | (c >>> 6 & 0x3f);\n
            buf[i++] = 0x80 | (c & 0x3f);\n
        } else {\n
            /* four bytes */\n
            buf[i++] = 0xf0 | (c >>> 18);\n
            buf[i++] = 0x80 | (c >>> 12 & 0x3f);\n
            buf[i++] = 0x80 | (c >>> 6 & 0x3f);\n
            buf[i++] = 0x80 | (c & 0x3f);\n
        }\n
    }\n
\n
    return buf;\n
};\n
\n
// Calculate max possible position in utf8 buffer,\n
// that will not break sequence. If that\'s not possible\n
// - (very small limits) return max size as is.\n
//\n
// buf[] - utf8 bytes array\n
// max   - length limit (mandatory);\n
var utf8border = function(buf, max) {\n
    var pos;\n
\n
    max = max || buf.length;\n
    if (max > buf.length) { max = buf.length; }\n
\n
    // go back from last position, until start of sequence found\n
    pos = max-1;\n
    while (pos >= 0 && (buf[pos] & 0xC0) === 0x80) { pos--; }\n
\n
    // Fuckup - very small and broken sequence,\n
    // return max, because we should return something anyway.\n
    if (pos < 0) { return max; }\n
\n
    // If we came to start of buffer - that means vuffer is too small,\n
    // return max too.\n
    if (pos === 0) { return max; }\n
\n
    return (pos + _utf8len[buf[pos]] > max) ? pos : max;\n
};\n
\n
// convert array to string\n
var buf2string = function (buf) {\n
    var str, i, out, c, c_len;\n
    var len = buf.length;\n
\n
    // Reserve max possible length (2 words per char)\n
    // NB: by unknown reasons, Array is significantly faster for\n
    //     String.fromCharCode.apply than Uint16Array.\n
    var utf16buf = new Array(len*2);\n
\n
    for (out=0, i=0; i<len;) {\n
        c = buf[i++];\n
        // quick process ascii\n
        if (c < 0x80) { utf16buf[out++] = c; continue; }\n
\n
        c_len = _utf8len[c];\n
        // skip 5 & 6 byte codes\n
        if (c_len > 4) { utf16buf[out++] = 0xfffd; i += c_len-1; continue; }\n
\n
        // apply mask on first byte\n
        c &= c_len === 2 ? 0x1f : c_len === 3 ? 0x0f : 0x07;\n
        // join the rest\n
        while (c_len > 1 && i < len) {\n
            c = (c << 6) | (buf[i++] & 0x3f);\n
            c_len--;\n
        }\n
\n
        // terminated by end of string?\n
        if (c_len > 1) { utf16buf[out++] = 0xfffd; continue; }\n
\n
        if (c < 0x10000) {\n
            utf16buf[out++] = c;\n
        } else {\n
            c -= 0x10000;\n
            utf16buf[out++] = 0xd800 | ((c >> 10) & 0x3ff);\n
            utf16buf[out++] = 0xdc00 | (c & 0x3ff);\n
        }\n
    }\n
\n
    // shrinkBuf(utf16buf, out)\n
    if (utf16buf.length !== out) {\n
        if(utf16buf.subarray) {\n
            utf16buf = utf16buf.subarray(0, out);\n
        } else {\n
            utf16buf.length = out;\n
        }\n
    }\n
\n
    // return String.fromCharCode.apply(null, utf16buf);\n
    return utils.applyFromCharCode(utf16buf);\n
};\n
\n
\n
// That\'s all for the pako functions.\n
\n
\n
/**\n
 * Transform a javascript string into an array (typed if possible) of bytes,\n
 * UTF-8 encoded.\n
 * @param {String} str the string to encode\n
 * @return {Array|Uint8Array|Buffer} the UTF-8 encoded string.\n
 */\n
exports.utf8encode = function utf8encode(str) {\n
    if (support.nodebuffer) {\n
        return nodeBuffer(str, "utf-8");\n
    }\n
\n
    return string2buf(str);\n
};\n
\n
\n
/**\n
 * Transform a bytes array (or a representation) representing an UTF-8 encoded\n
 * string into a javascript string.\n
 * @param {Array|Uint8Array|Buffer} buf the data de decode\n
 * @return {String} the decoded string.\n
 */\n
exports.utf8decode = function utf8decode(buf) {\n
    if (support.nodebuffer) {\n
        return utils.transformTo("nodebuffer", buf).toString("utf-8");\n
    }\n
\n
    buf = utils.transformTo(support.uint8array ? "uint8array" : "array", buf);\n
\n
    // return buf2string(buf);\n
    // Chrome prefers to work with "small" chunks of data\n
    // for the method buf2string.\n
    // Firefox and Chrome has their own shortcut, IE doesn\'t seem to really care.\n
    var result = [], k = 0, len = buf.length, chunk = 65536;\n
    while (k < len) {\n
        var nextBoundary = utf8border(buf, Math.min(k + chunk, len));\n
        if (support.uint8array) {\n
            result.push(buf2string(buf.subarray(k, nextBoundary)));\n
        } else {\n
            result.push(buf2string(buf.slice(k, nextBoundary)));\n
        }\n
        k = nextBoundary;\n
    }\n
    return result.join("");\n
\n
};\n
// vim: set shiftwidth=4 softtabstop=4:\n
\n
},{"./nodeBuffer":11,"./support":17,"./utils":21}],21:[function(_dereq_,module,exports){\n
\'use strict\';\n
var support = _dereq_(\'./support\');\n
var compressions = _dereq_(\'./compressions\');\n
var nodeBuffer = _dereq_(\'./nodeBuffer\');\n
/**\n
 * Convert a string to a "binary string" : a string containing only char codes between 0 and 255.\n
 * @param {string} str the string to transform.\n
 * @return {String} the binary string.\n
 */\n
exports.string2binary = function(str) {\n
    var result = "";\n
    for (var i = 0; i < str.length; i++) {\n
        result += String.fromCharCode(str.charCodeAt(i) & 0xff);\n
    }\n
    return result;\n
};\n
exports.arrayBuffer2Blob = function(buffer, mimeType) {\n
    exports.checkSupport("blob");\n
\tmimeType = mimeType || \'application/zip\';\n
\n
    try {\n
        // Blob constructor\n
        return new Blob([buffer], {\n
            type: mimeType\n
        });\n
    }\n
    catch (e) {\n
\n
        try {\n
            // deprecated, browser only, old way\n
            var Builder = window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder || window.MSBlobBuilder;\n
            var builder = new Builder();\n
            builder.append(buffer);\n
            return builder.getBlob(mimeType);\n
        }\n
        catch (e) {\n
\n
            // well, fuck ?!\n
            throw new Error("Bug : can\'t construct the Blob.");\n
        }\n
    }\n
\n
\n
};\n
/**\n
 * The identity function.\n
 * @param {Object} input the input.\n
 * @return {Object} the same input.\n
 */\n
function identity(input) {\n
    return input;\n
}\n
\n
/**\n
 * Fill in an array with a string.\n
 * @param {String} str the string to use.\n
 * @param {Array|ArrayBuffer|Uint8Array|Buffer} array the array to fill in (will be mutated).\n
 * @return {Array|ArrayBuffer|Uint8Array|Buffer} the updated array.\n
 */\n
function stringToArrayLike(str, array) {\n
    for (var i = 0; i < str.length; ++i) {\n
        array[i] = str.charCodeAt(i) & 0xFF;\n
    }\n
    return array;\n
}\n
\n
/**\n
 * Transform an array-like object to a string.\n
 * @param {Array|ArrayBuffer|Uint8Array|Buffer} array the array to transform.\n
 * @return {String} the result.\n
 */\n
function arrayLikeToString(array) {\n
    // Performances notes :\n
    // --------------------\n
    // String.fromCharCode.apply(null, array) is the fastest, see\n
    // see http://jsperf.com/converting-a-uint8array-to-a-string/2\n
    // but the stack is limited (and we can get huge arrays !).\n
    //\n
    // result += String.fromCharCode(array[i]); generate too many strings !\n
    //\n
    // This code is inspired by http://jsperf.com/arraybuffer-to-string-apply-performance/2\n
    var chunk = 65536;\n
    var result = [],\n
        len = array.length,\n
        type = exports.getTypeOf(array),\n
        k = 0,\n
        canUseApply = true;\n
      try {\n
         switch(type) {\n
            case "uint8array":\n
               String.fromCharCode.apply(null, new Uint8Array(0));\n
               break;\n
            case "nodebuffer":\n
               String.fromCharCode.apply(null, nodeBuffer(0));\n
               break;\n
         }\n
      } catch(e) {\n
         canUseApply = false;\n
      }\n
\n
      // no apply : slow and painful algorithm\n
      // default browser on android 4.*\n
      if (!canUseApply) {\n
         var resultStr = "";\n
         for(var i = 0; i < array.length;i++) {\n
            resultStr += String.fromCharCode(array[i]);\n
         }\n
    return resultStr;\n
    }\n
    while (k < len && chunk > 1) {\n
        try {\n
            if (type === "array" || type === "nodebuffer") {\n
                result.push(String.fromCharCode.apply(null, array.slice(k, Math.min(k + chunk, len))));\n
            }\n
            else {\n
                result.push(String.fromCharCode.apply(null, array.subarray(k, Math.min(k + chunk, len))));\n
            }\n
            k += chunk;\n
        }\n
        catch (e) {\n
            chunk = Math.floor(chunk / 2);\n
        }\n
    }\n
    return result.join("");\n
}\n
\n
exports.applyFromCharCode = arrayLikeToString;\n
\n
\n
/**\n
 * Copy the data from an array-like to an other array-like.\n
 * @param {Array|ArrayBuffer|Uint8Array|Buffer} arrayFrom the origin array.\n
 * @param {Array|ArrayBuffer|Uint8Array|Buffer} arrayTo the destination array which will be mutated.\n
 * @return {Array|ArrayBuffer|Uint8Array|Buffer} the updated destination array.\n
 */\n
function arrayLikeToArrayLike(arrayFrom, arrayTo) {\n
    for (var i = 0; i < arrayFrom.length; i++) {\n
        arrayTo[i] = arrayFrom[i];\n
    }\n
    return arrayTo;\n
}\n
\n
// a matrix containing functions to transform everything into everything.\n
var transform = {};\n
\n
// string to ?\n
transform["string"] = {\n
    "string": identity,\n
    "array": function(input) {\n
        return stringToArrayLike(input, new Array(input.length));\n
    },\n
    "arraybuffer": function(input) {\n
        return transform["string"]["uint8array"](input).buffer;\n
    },\n
    "uint8array": function(input) {\n
        return stringToArrayLike(input, new Uint8Array(input.length));\n
    },\n
    "nodebuffer": function(input) {\n
        return stringToArrayLike(input, nodeBuffer(input.length));\n
    }\n
};\n
\n
// array to ?\n
transform["array"] = {\n
    "string": arrayLikeToString,\n
    "array": identity,\n
    "arraybuffer": function(input) {\n
        return (new Uint8Array(input)).buffer;\n
    },\n
    "uint8array": function(input) {\n
        return new Uint8Array(input);\n
    },\n
    "nodebuffer": function(input) {\n
        return nodeBuffer(input);\n
    }\n
};\n
\n
// arraybuffer to ?\n
transform["arraybuffer"] = {\n
    "string": function(input) {\n
        return arrayLikeToString(new Uint8Array(input));\n
    },\n
    "array": function(input) {\n
        return arrayLikeToArrayLike(new Uint8Array(input), new Array(input.byteLength));\n
    },\n
    "arraybuffer": identity,\n
    "uint8array": function(input) {\n
        return new Uint8Array(input);\n
    },\n
    "nodebuffer": function(input) {\n
        return nodeBuffer(new Uint8Array(input));\n
    }\n
};\n
\n
// uint8array to ?\n
transform["uint8array"] = {\n
    "string": arrayLikeToString,\n
    "array": function(input) {\n
        return arrayLikeToArrayLike(input, new Array(input.length));\n
    },\n
    "arraybuffer": function(input) {\n
        return input.buffer;\n
    },\n
    "uint8array": identity,\n
    "nodebuffer": function(input) {\n
        return nodeBuffer(input);\n
    }\n
};\n
\n
// nodebuffer to ?\n
transform["nodebuffer"] = {\n
    "string": arrayLikeToString,\n
    "array": function(input) {\n
        return arrayLikeToArrayLike(input, new Array(input.length));\n
    },\n
    "arraybuffer": function(input) {\n
        return transform["nodebuffer"]["uint8array"](input).buffer;\n
    },\n
    "uint8array": function(input) {\n
        return arrayLikeToArrayLike(input, new Uint8Array(input.length));\n
    },\n
    "nodebuffer": identity\n
};\n
\n
/**\n
 * Transform an input into any type.\n
 * The supported output type are : string, array, uint8array, arraybuffer, nodebuffer.\n
 * If no output type is specified, the unmodified input will be returned.\n
 * @param {String} outputType the output type.\n
 * @param {String|Array|ArrayBuffer|Uint8Array|Buffer} input the input to convert.\n
 * @throws {Error} an Error if the browser doesn\'t support the requested output type.\n
 */\n
exports.transformTo = function(outputType, input) {\n
    if (!input) {\n
        // undefined, null, etc\n
        // an empty string won\'t harm.\n
        input = "";\n
    }\n
    if (!outputType) {\n
        return input;\n
    }\n
    exports.checkSupport(outputType);\n
    var inputType = exports.getTypeOf(input);\n
    var result = transform[inputType][outputType](input);\n
    return result;\n
};\n
\n
/**\n
 * Return the type of the input.\n
 * The type will be in a format valid for JSZip.utils.transformTo : string, array, uint8array, arraybuffer.\n
 * @param {Object} input the input to identify.\n
 * @return {String} the (lowercase) type of the input.\n
 */\n
exports.getTypeOf = function(input) {\n
    if (typeof input === "string") {\n
        return "string";\n
    }\n
    if (Object.prototype.toString.call(input) === "[object Array]") {\n
        return "array";\n
    }\n
    if (support.nodebuffer && nodeBuffer.test(input)) {\n
        return "nodebuffer";\n
    }\n
    if (support.uint8array && input instanceof Uint8Array) {\n
        return "uint8array";\n
    }\n
    if (support.arraybuffer && input instanceof ArrayBuffer) {\n
        return "arraybuffer";\n
    }\n
};\n
\n
/**\n
 * Throw an exception if the type is not supported.\n
 * @param {String} type the type to check.\n
 * @throws {Error} an Error if the browser doesn\'t support the requested type.\n
 */\n
exports.checkSupport = function(type) {\n
    var supported = support[type.toLowerCase()];\n
    if (!supported) {\n
        throw new Error(type + " is not supported by this browser");\n
    }\n
};\n
exports.MAX_VALUE_16BITS = 65535;\n
exports.MAX_VALUE_32BITS = -1; // well, "\\xFF\\xFF\\xFF\\xFF\\xFF\\xFF\\xFF\\xFF" is parsed as -1\n
\n
/**\n
 * Prettify a string read as binary.\n
 * @param {string} str the string to prettify.\n
 * @return {string} a pretty string.\n
 */\n
exports.pretty = function(str) {\n
    var res = \'\',\n
        code, i;\n
    for (i = 0; i < (str || "").length; i++) {\n
        code = str.charCodeAt(i);\n
        res += \'\\\\x\' + (code < 16 ? "0" : "") + code.toString(16).toUpperCase();\n
    }\n
    return res;\n
};\n
\n
/**\n
 * Find a compression registered in JSZip.\n
 * @param {string} compressionMethod the method magic to find.\n
 * @return {Object|null} the JSZip compression object, null if none found.\n
 */\n
exports.findCompression = function(compressionMethod) {\n
    for (var method in compressions) {\n
        if (!compressions.hasOwnProperty(method)) {\n
            continue;\n
        }\n
        if (compressions[method].magic === compressionMethod) {\n
            return compressions[method];\n
        }\n
    }\n
    return null;\n
};\n
/**\n
* Cross-window, cross-Node-context regular expression detection\n
* @param  {Object}  object Anything\n
* @return {Boolean}        true if the object is a regular expression,\n
* false otherwise\n
*/\n
exports.isRegExp = function (object) {\n
    return Object.prototype.toString.call(object) === "[object RegExp]";\n
};\n
\n
\n
},{"./compressions":3,"./nodeBuffer":11,"./support":17}],22:[function(_dereq_,module,exports){\n
\'use strict\';\n
var StringReader = _dereq_(\'./stringReader\');\n
var NodeBufferReader = _dereq_(\'./nodeBufferReader\');\n
var Uint8ArrayReader = _dereq_(\'./uint8ArrayReader\');\n
var utils = _dereq_(\'./utils\');\n
var sig = _dereq_(\'./signature\');\n
var ZipEntry = _dereq_(\'./zipEntry\');\n
var support = _dereq_(\'./support\');\n
var jszipProto = _dereq_(\'./object\');\n
//  class ZipEntries {{{\n
/**\n
 * All the entries in the zip file.\n
 * @constructor\n
 * @param {String|ArrayBuffer|Uint8Array} data the binary stream to load.\n
 * @param {Object} loadOptions Options for loading the stream.\n
 */\n
function ZipEntries(data, loadOptions) {\n
    this.files = [];\n
    this.loadOptions = loadOptions;\n
    if (data) {\n
        this.load(data);\n
    }\n
}\n
ZipEntries.prototype = {\n
    /**\n
     * Check that the reader is on the speficied signature.\n
     * @param {string} expectedSignature the expected signature.\n
     * @throws {Error} if it is an other signature.\n
     */\n
    checkSignature: function(expectedSignature) {\n
        var signature = this.reader.readString(4);\n
        if (signature !== expectedSignature) {\n
            throw new Error("Corrupted zip or bug : unexpected signature " + "(" + utils.pretty(signature) + ", expected " + utils.pretty(expectedSignature) + ")");\n
        }\n
    },\n
    /**\n
     * Read the end of the central directory.\n
     */\n
    readBlockEndOfCentral: function() {\n
        this.diskNumber = this.reader.readInt(2);\n
        this.diskWithCentralDirStart = this.reader.readInt(2);\n
        this.centralDirRecordsOnThisDisk = this.reader.readInt(2);\n
        this.centralDirRecords = this.reader.readInt(2);\n
        this.centralDirSize = this.reader.readInt(4);\n
        this.centralDirOffset = this.reader.readInt(4);\n
\n
        this.zipCommentLength = this.reader.readInt(2);\n
        // warning : the encoding depends of the system locale\n
        // On a linux machine with LANG=en_US.utf8, this field is utf8 encoded.\n
        // On a windows machine, this field is encoded with the localized windows code page.\n
        this.zipComment = this.reader.readString(this.zipCommentLength);\n
        // To get consistent behavior with the generation part, we will assume that\n
        // this is utf8 encoded.\n
        this.zipComment = jszipProto.utf8decode(this.zipComment);\n
    },\n
    /**\n
     * Read the end of the Zip 64 central directory.\n
     * Not merged with the method readEndOfCentral :\n
     * The end of central can coexist with its Zip64 brother,\n
     * I don\'t want to read the wrong number of bytes !\n
     */\n
    readBlockZip64EndOfCentral: function() {\n
        this.zip64EndOfCentralSize = this.reader.readInt(8);\n
        this.versionMadeBy = this.reader.readString(2);\n
        this.versionNeeded = this.reader.readInt(2);\n
        this.diskNumber = this.reader.readInt(4);\n
        this.diskWithCentralDirStart = this.reader.readInt(4);\n
        this.centralDirRecordsOnThisDisk = this.reader.readInt(8);\n
        this.centralDirRecords = this.reader.readInt(8);\n
        this.centralDirSize = this.reader.readInt(8);\n
        this.centralDirOffset = this.reader.readInt(8);\n
\n
        this.zip64ExtensibleData = {};\n
        var extraDataSize = this.zip64EndOfCentralSize - 44,\n
            index = 0,\n
            extraFieldId,\n
            extraFieldLength,\n
            extraFieldValue;\n
        while (index < extraDataSize) {\n
            extraFieldId = this.reader.readInt(2);\n
            extraFieldLength = this.reader.readInt(4);\n
            extraFieldValue = this.reader.readString(extraFieldLength);\n
            this.zip64ExtensibleData[extraFieldId] = {\n
                id: extraFieldId,\n
                length: extraFieldLength,\n
                value: extraFieldValue\n
            };\n
        }\n
    },\n
    /**\n
     * Read the end of the Zip 64 central directory locator.\n
     */\n
    readBlockZip64EndOfCentralLocator: function() {\n
        this.diskWithZip64CentralDirStart = this.reader.readInt(4);\n
        this.relativeOffsetEndOfZip64CentralDir = this.reader.readInt(8);\n
        this.disksCount = this.reader.readInt(4);\n
        if (this.disksCount > 1) {\n
            throw new Error("Multi-volumes zip are not supported");\n
        }\n
    },\n
    /**\n
     * Read the local files, based on the offset read in the central part.\n
     */\n
    readLocalFiles: function() {\n
        var i, file;\n
        for (i = 0; i < this.files.length; i++) {\n
            file = this.files[i];\n
            this.reader.setIndex(file.localHeaderOffset);\n
            this.checkSignature(sig.LOCAL_FILE_HEADER);\n
            file.readLocalPart(this.reader);\n
            file.handleUTF8();\n
            file.processAttributes();\n
        }\n
    },\n
    /**\n
     * Read the central directory.\n
     */\n
    readCentralDir: function() {\n
        var file;\n
\n
        this.reader.setIndex(this.centralDirOffset);\n
        while (this.reader.readString(4) === sig.CENTRAL_FILE_HEADER) {\n
            file = new ZipEntry({\n
                zip64: this.zip64\n
            }, this.loadOptions);\n
            file.readCentralPart(this.reader);\n
            this.files.push(file);\n
        }\n
    },\n
    /**\n
     * Read the end of central directory.\n
     */\n
    readEndOfCentral: function() {\n
        var offset = this.reader.lastIndexOfSignature(sig.CENTRAL_DIRECTORY_END);\n
        if (offset === -1) {\n
            // Check if the content is a truncated zip or complete garbage.\n
            // A "LOCAL_FILE_HEADER" is not required at the beginning (auto\n
            // extractible zip for example) but it can give a good hint.\n
            // If an ajax request was used without responseType, we will also\n
            // get unreadable data.\n
            var isGarbage = true;\n
            try {\n
                this.reader.setIndex(0);\n
                this.checkSignature(sig.LOCAL_FILE_HEADER);\n
                isGarbage = false;\n
            } catch (e) {}\n
\n
            if (isGarbage) {\n
                throw new Error("Can\'t find end of central directory : is this a zip file ? " +\n
                                "If it is, see http://stuk.github.io/jszip/documentation/howto/read_zip.html");\n
            } else {\n
                throw new Error("Corrupted zip : can\'t find end of central directory");\n
            }\n
        }\n
        this.reader.setIndex(offset);\n
        this.checkSignature(sig.CENTRAL_DIRECTORY_END);\n
        this.readBlockEndOfCentral();\n
\n
\n
        /* extract from the zip spec :\n
            4)  If one of the fields in the end of central directory\n
                record is too small to hold required data, the field\n
                should be set to -1 (0xFFFF or 0xFFFFFFFF) and the\n
                ZIP64 format record should be created.\n
            5)  The end of central directory record and the\n
                Zip64 end of central directory locator record must\n
                reside on the same disk when splitting or spanning\n
                an archive.\n
         */\n
        if (this.diskNumber === utils.MAX_VALUE_16BITS || this.diskWithCentralDirStart === utils.MAX_VALUE_16BITS || this.centralDirRecordsOnThisDisk === utils.MAX_VALUE_16BITS || this.centralDirRecords === utils.MAX_VALUE_16BITS || this.centralDirSize === utils.MAX_VALUE_32BITS || this.centralDirOffset === utils.MAX_VALUE_32BITS) {\n
            this.zip64 = true;\n
\n
            /*\n
            Warning : the zip64 extension is supported, but ONLY if the 64bits integer read from\n
            the zip file can fit into a 32bits integer. This cannot be solved : Javascript represents\n
            all numbers as 64-bit double precision IEEE 754 floating point numbers.\n
            So, we have 53bits for integers and bitwise operations treat everything as 32bits.\n
            see https://developer.mozilla.org/en-US/docs/JavaScript/Reference/Operators/Bitwise_Operators\n
            and http://www.ecma-international.org/publications/files/ECMA-ST/ECMA-262.pdf section 8.5\n
            */\n
\n
            // should look for a zip64 EOCD locator\n
            offset = this.reader.lastIndexOfSignature(sig.ZIP64_CENTRAL_DIRECTORY_LOCATOR);\n
            if (offset === -1) {\n
                throw new Error("Corrupted zip : can\'t find the ZIP64 end of central directory locator");\n
            }\n
            this.reader.setIndex(offset);\n
            this.checkSignature(sig.ZIP64_CENTRAL_DIRECTORY_LOCATOR);\n
            this.readBlockZip64EndOfCentralLocator();\n
\n
            // now the zip64 EOCD record\n
            this.reader.setIndex(this.relativeOffsetEndOfZip64CentralDir);\n
            this.checkSignature(sig.ZIP64_CENTRAL_DIRECTORY_END);\n
            this.readBlockZip64EndOfCentral();\n
        }\n
    },\n
    prepareReader: function(data) {\n
        var type = utils.getTypeOf(data);\n
        if (type === "string" && !support.uint8array) {\n
            this.reader = new StringReader(data, this.loadOptions.optimizedBinaryString);\n
        }\n
        else if (type === "nodebuffer") {\n
            this.reader = new NodeBufferReader(data);\n
        }\n
        else {\n
            this.reader = new Uint8ArrayReader(utils.transformTo("uint8array", data));\n
        }\n
    },\n
    /**\n
     * Read a zip file and create ZipEntries.\n
     * @param {String|ArrayBuffer|Uint8Array|Buffer} data the binary string representing a zip file.\n
     */\n
    load: function(data) {\n
        this.prepareReader(data);\n
        this.readEndOfCentral();\n
        this.readCentralDir();\n
        this.readLocalFiles();\n
    }\n
};\n
// }}} end of ZipEntries\n
module.exports = ZipEntries;\n
\n
},{"./nodeBufferReader":12,"./object":13,"./signature":14,"./stringReader":15,"./support":17,"./uint8ArrayReader":18,"./utils":21,"./zipEntry":23}],23:[function(_dereq_,module,exports){\n
\'use strict\';\n
var StringReader = _dereq_(\'./stringReader\');\n
var utils = _dereq_(\'./utils\');\n
var CompressedObject = _dereq_(\'./compressedObject\');\n
var jszipProto = _dereq_(\'./object\');\n
\n
var MADE_BY_DOS = 0x00;\n
var MADE_BY_UNIX = 0x03;\n
\n
// class ZipEntry {{{\n
/**\n
 * An entry in the zip file.\n
 * @constructor\n
 * @param {Object} options Options of the current file.\n
 * @param {Object} loadOptions Options for loading the stream.\n
 */\n
function ZipEntry(options, loadOptions) {\n
    this.options = options;\n
    this.loadOptions = loadOptions;\n
}\n
ZipEntry.prototype = {\n
    /**\n
     * say if the file is encrypted.\n
     * @return {boolean} true if the file is encrypted, false otherwise.\n
     */\n
    isEncrypted: function() {\n
        // bit 1 is set\n
        return (this.bitFlag & 0x0001) === 0x0001;\n
    },\n
    /**\n
     * say if the file has utf-8 filename/comment.\n
     * @return {boolean} true if the filename/comment is in utf-8, false otherwise.\n
     */\n
    useUTF8: function() {\n
        // bit 11 is set\n
        return (this.bitFlag & 0x0800) === 0x0800;\n
    },\n
    /**\n
     * Prepare the function used to generate the compressed content from this ZipFile.\n
     * @param {DataReader} reader the reader to use.\n
     * @param {number} from the offset from where we should read the data.\n
     * @param {number} length the length of the data to read.\n
     * @return {Function} the callback to get the compressed content (the type depends of the DataReader class).\n
     */\n
    prepareCompressedContent: function(reader, from, length) {\n
        return function() {\n
            var previousIndex = reader.index;\n
            reader.setIndex(from);\n
            var compressedFileData = reader.readData(length);\n
            reader.setIndex(previousIndex);\n
\n
            return compressedFileData;\n
        };\n
    },\n
    /**\n
     * Prepare the function used to generate the uncompressed content from this ZipFile.\n
     * @param {DataReader} reader the reader to use.\n
     * @param {number} from the offset from where we should read the data.\n
     * @param {number} length the length of the data to read.\n
     * @param {JSZip.compression} compression the compression used on this file.\n
     * @param {number} uncompressedSize the uncompressed size to expect.\n
     * @return {Function} the callback to get the uncompressed content (the type depends of the DataReader class).\n
     */\n
    prepareContent: function(reader, from, length, compression, uncompressedSize) {\n
        return function() {\n
\n
            var compressedFileData = utils.transformTo(compression.uncompressInputType, this.getCompressedContent());\n
            var uncompressedFileData = compression.uncompress(compressedFileData);\n
\n
            if (uncompressedFileData.length !== uncompressedSize) {\n
                throw new Error("Bug : uncompressed data size mismatch");\n
            }\n
\n
            return uncompressedFileData;\n
        };\n
    },\n
    /**\n
     * Read the local part of a zip file and add the info in this object.\n
     * @param {DataReader} reader the reader to use.\n
     */\n
    readLocalPart: function(reader) {\n
        var compression, localExtraFieldsLength;\n
\n
        // we already know everything from the central dir !\n
        // If the central dir data are false, we are doomed.\n
        // On the bright side, the local part is scary  : zip64, data descriptors, both, etc.\n
        // The less data we get here, the more reliable this should be.\n
        // Let\'s skip the whole header and dash to the data !\n
        reader.skip(22);\n
        // in some zip created on windows, the filename stored in the central dir contains \\ instead of /.\n
        // Strangely, the filename here is OK.\n
        // I would love to treat these zip files as corrupted (see http://www.info-zip.org/FAQ.html#backslashes\n
        // or APPNOTE#4.4.17.1, "All slashes MUST be forward slashes \'/\'") but there are a lot of bad zip generators...\n
        // Search "unzip mismatching "local" filename continuing with "central" filename version" on\n
        // the internet.\n
        //\n
        // I think I see the logic here : the central directory is used to display\n
        // content and the local directory is used to extract the files. Mixing / and \\\n
        // may be used to display \\ to windows users and use / when extracting the files.\n
        // Unfortunately, this lead also to some issues : http://seclists.org/fulldisclosure/2009/Sep/394\n
        this.fileNameLength = reader.readInt(2);\n
        localExtraFieldsLength = reader.readInt(2); // can\'t be sure this will be the same as the central dir\n
        this.fileName = reader.readString(this.fileNameLength);\n
        reader.skip(localExtraFieldsLength);\n
\n
        if (this.compressedSize == -1 || this.uncompressedSize == -1) {\n
            throw new Error("Bug or corrupted zip : didn\'t get enough informations from the central directory " + "(compressedSize == -1 || uncompressedSize == -1)");\n
        }\n
\n
        compression = utils.findCompression(this.compressionMethod);\n
        if (compression === null) { // no compression found\n
            throw new Error("Corrupted zip : compression " + utils.pretty(this.compressionMethod) + " unknown (inner file : " + this.fileName + ")");\n
        }\n
        this.decompressed = new CompressedObject();\n
        this.decompressed.compressedSize = this.compressedSize;\n
        this.decompressed.uncompressedSize = this.uncompressedSize;\n
        this.decompressed.crc32 = this.crc32;\n
        this.decompressed.compressionMethod = this.compressionMethod;\n
        this.decompressed.getCompressedContent = this.prepareCompressedContent(reader, reader.index, this.compressedSize, compression);\n
        this.decompressed.getContent = this.prepareContent(reader, reader.index, this.compressedSize, compression, this.uncompressedSize);\n
\n
        // we need to compute the crc32...\n
        if (this.loadOptions.checkCRC32) {\n
            this.decompressed = utils.transformTo("string", this.decompressed.getContent());\n
            if (jszipProto.crc32(this.decompressed) !== this.crc32) {\n
                throw new Error("Corrupted zip : CRC32 mismatch");\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Read the central part of a zip file and add the info in this object.\n
     * @param {DataReader} reader the reader to use.\n
     */\n
    readCentralPart: function(reader) {\n
        this.versionMadeBy = reader.readInt(2);\n
        this.versionNeeded = reader.readInt(2);\n
        this.bitFlag = reader.readInt(2);\n
        this.compressionMethod = reader.readString(2);\n
        this.date = reader.readDate();\n
        this.crc32 = reader.readInt(4);\n
        this.compressedSize = reader.readInt(4);\n
        this.uncompressedSize = reader.readInt(4);\n
        this.fileNameLength = reader.readInt(2);\n
        this.extraFieldsLength = reader.readInt(2);\n
        this.fileCommentLength = reader.readInt(2);\n
        this.diskNumberStart = reader.readInt(2);\n
        this.internalFileAttributes = reader.readInt(2);\n
        this.externalFileAttributes = reader.readInt(4);\n
        this.localHeaderOffset = reader.readInt(4);\n
\n
        if (this.isEncrypted()) {\n
            throw new Error("Encrypted zip are not supported");\n
        }\n
\n
        this.fileName = reader.readString(this.fileNameLength);\n
        this.readExtraFields(reader);\n
        this.parseZIP64ExtraField(reader);\n
        this.fileComment = reader.readString(this.fileCommentLength);\n
    },\n
\n
    /**\n
     * Parse the external file attributes and get the unix/dos permissions.\n
     */\n
    processAttributes: function () {\n
        this.unixPermissions = null;\n
        this.dosPermissions = null;\n
        var madeBy = this.versionMadeBy >> 8;\n
\n
        // Check if we have the DOS directory flag set.\n
        // We look for it in the DOS and UNIX permissions\n
        // but some unknown platform could set it as a compatibility flag.\n
        this.dir = this.externalFileAttributes & 0x0010 ? true : false;\n
\n
        if(madeBy === MADE_BY_DOS) {\n
            // first 6 bits (0 to 5)\n
            this.dosPermissions = this.externalFileAttributes & 0x3F;\n
        }\n
\n
        if(madeBy === MADE_BY_UNIX) {\n
            this.unixPermissions = (this.externalFileAttributes >> 16) & 0xFFFF;\n
            // the octal permissions are in (this.unixPermissions & 0x01FF).toString(8);\n
        }\n
\n
        // fail safe : if the name ends with a / it probably means a folder\n
        if (!this.dir && this.fileName.slice(-1) === \'/\') {\n
            this.dir = true;\n
        }\n
    },\n
\n
    /**\n
     * Parse the ZIP64 extra field and merge the info in the current ZipEntry.\n
     * @param {DataReader} reader the reader to use.\n
     */\n
    parseZIP64ExtraField: function(reader) {\n
\n
        if (!this.extraFields[0x0001]) {\n
            return;\n
        }\n
\n
        // should be something, preparing the extra reader\n
        var extraReader = new StringReader(this.extraFields[0x0001].value);\n
\n
        // I really hope that these 64bits integer can fit in 32 bits integer, because js\n
        // won\'t let us have more.\n
        if (this.uncompressedSize === utils.MAX_VALUE_32BITS) {\n
            this.uncompressedSize = extraReader.readInt(8);\n
        }\n
        if (this.compressedSize === utils.MAX_VALUE_32BITS) {\n
            this.compressedSize = extraReader.readInt(8);\n
        }\n
        if (this.localHeaderOffset === utils.MAX_VALUE_32BITS) {\n
            this.localHeaderOffset = extraReader.readInt(8);\n
        }\n
        if (this.diskNumberStart === utils.MAX_VALUE_32BITS) {\n
            this.diskNumberStart = extraReader.readInt(4);\n
        }\n
    },\n
    /**\n
     * Read the central part of a zip file and add the info in this object.\n
     * @param {DataReader} reader the reader to use.\n
     */\n
    readExtraFields: function(reader) {\n
        var start = reader.index,\n
            extraFieldId,\n
            extraFieldLength,\n
            extraFieldValue;\n
\n
        this.extraFields = this.extraFields || {};\n
\n
        while (reader.index < start + this.extraFieldsLength) {\n
            extraFieldId = reader.readInt(2);\n
            extraFieldLength = reader.readInt(2);\n
            extraFieldValue = reader.readString(extraFieldLength);\n
\n
            this.extraFields[extraFieldId] = {\n
                id: extraFieldId,\n
                length: extraFieldLength,\n
                value: extraFieldValue\n
            };\n
        }\n
    },\n
    /**\n
     * Apply an UTF8 transformation if needed.\n
     */\n
    handleUTF8: function() {\n
        if (this.useUTF8()) {\n
            this.fileName = jszipProto.utf8decode(this.fileName);\n
            this.fileComment = jszipProto.utf8decode(this.fileComment);\n
        } else {\n
            var upath = this.findExtraFieldUnicodePath();\n
            if (upath !== null) {\n
                this.fileName = upath;\n
            }\n
            var ucomment = this.findExtraFieldUnicodeComment();\n
            if (ucomment !== null) {\n
                this.fileComment = ucomment;\n
            }\n
        }\n
    },\n
\n
    /**\n
     * Find the unicode path declared in the extra field, if any.\n
     * @return {String} the unicode path, null otherwise.\n
     */\n
    findExtraFieldUnicodePath: function() {\n
        var upathField = this.extraFields[0x7075];\n
        if (upathField) {\n
            var extraReader = new StringReader(upathField.value);\n
\n
            // wrong version\n
            if (extraReader.readInt(1) !== 1) {\n
                return null;\n
            }\n
\n
            // the crc of the filename changed, this field is out of date.\n
            if (jszipProto.crc32(this.fileName) !== extraReader.readInt(4)) {\n
                return null;\n
            }\n
\n
            return jszipProto.utf8decode(extraReader.readString(upathField.length - 5));\n
        }\n
        return null;\n
    },\n
\n
    /**\n
     * Find the unicode comment declared in the extra field, if any.\n
     * @return {String} the unicode comment, null otherwise.\n
     */\n
    findExtraFieldUnicodeComment: function() {\n
        var ucommentField = this.extraFields[0x6375];\n
        if (ucommentField) {\n
            var extraReader = new StringReader(ucommentField.value);\n
\n
            // wrong version\n
            if (extraReader.readInt(1) !== 1) {\n
                return null;\n
            }\n
\n
            // the crc of the comment changed, this field is out of date.\n
            if (jszipProto.crc32(this.fileComment) !== extraReader.readInt(4)) {\n
                return null;\n
            }\n
\n
            return jszipProto.utf8decode(extraReader.readString(ucommentField.length - 5));\n
        }\n
        return null;\n
    }\n
};\n
module.exports = ZipEntry;\n
\n
},{"./compressedObject":2,"./object":13,"./stringReader":15,"./utils":21}],24:[function(_dereq_,module,exports){\n
// Top level file is just a mixin of submodules & constants\n
\'use strict\';\n
\n
var assign    = _dereq_(\'./lib/utils/common\').assign;\n
\n
var deflate   = _dereq_(\'./lib/deflate\');\n
var inflate   = _dereq_(\'./lib/inflate\');\n
var constants = _dereq_(\'./lib/zlib/constants\');\n
\n
var pako = {};\n
\n
assign(pako, deflate, inflate, constants);\n
\n
module.exports = pako;\n
},{"./lib/deflate":25,"./lib/inflate":26,"./lib/utils/common":27,"./lib/zlib/constants":30}],25:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var zlib_deflate = _dereq_(\'./zlib/deflate.js\');\n
var utils = _dereq_(\'./utils/common\');\n
var strings = _dereq_(\'./utils/strings\');\n
var msg = _dereq_(\'./zlib/messages\');\n
var zstream = _dereq_(\'./zlib/zstream\');\n
\n
\n
/* Public constants ==========================================================*/\n
/* ===========================================================================*/\n
\n
var Z_NO_FLUSH      = 0;\n
var Z_FINISH        = 4;\n
\n
var Z_OK            = 0;\n
var Z_STREAM_END    = 1;\n
\n
var Z_DEFAULT_COMPRESSION = -1;\n
\n
var Z_DEFAULT_STRATEGY    = 0;\n
\n
var Z_DEFLATED  = 8;\n
\n
/* ===========================================================================*/\n
\n
\n
/**\n
 * class Deflate\n
 *\n
 * Generic JS-style wrapper for zlib calls. If you don\'t need\n
 * streaming behaviour - use more simple functions: [[deflate]],\n
 * [[deflateRaw]] and [[gzip]].\n
 **/\n
\n
/* internal\n
 * Deflate.chunks -> Array\n
 *\n
 * Chunks of output data, if [[Deflate#onData]] not overriden.\n
 **/\n
\n
/**\n
 * Deflate.result -> Uint8Array|Array\n
 *\n
 * Compressed result, generated by default [[Deflate#onData]]\n
 * and [[Deflate#onEnd]] handlers. Filled after you push last chunk\n
 * (call [[Deflate#push]] with `Z_FINISH` / `true` param).\n
 **/\n
\n
/**\n
 * Deflate.err -> Number\n
 *\n
 * Error code after deflate finished. 0 (Z_OK) on success.\n
 * You will not need it in real life, because deflate errors\n
 * are possible only on wrong options or bad `onData` / `onEnd`\n
 * custom handlers.\n
 **/\n
\n
/**\n
 * Deflate.msg -> String\n
 *\n
 * Error message, if [[Deflate.err]] != 0\n
 **/\n
\n
\n
/**\n
 * new Deflate(options)\n
 * - options (Object): zlib deflate options.\n
 *\n
 * Creates new deflator instance with specified params. Throws exception\n
 * on bad params. Supported options:\n
 *\n
 * - `level`\n
 * - `windowBits`\n
 * - `memLevel`\n
 * - `strategy`\n
 *\n
 * [http://zlib.net/manual.html#Advanced](http://zlib.net/manual.html#Advanced)\n
 * for more information on these.\n
 *\n
 * Additional options, for internal needs:\n
 *\n
 * - `chunkSize` - size of generated data chunks (16K by default)\n
 * - `raw` (Boolean) - do raw deflate\n
 * - `gzip` (Boolean) - create gzip wrapper\n
 * - `to` (String) - if equal to \'string\', then result will be "binary string"\n
 *    (each char code [0..255])\n
 * - `header` (Object) - custom header for gzip\n
 *   - `text` (Boolean) - true if compressed data believed to be text\n
 *   - `time` (Number) - modification time, unix timestamp\n
 *   - `os` (Number) - operation system code\n
 *   - `extra` (Array) - array of bytes with extra data (max 65536)\n
 *   - `name` (String) - file name (binary string)\n
 *   - `comment` (String) - comment (binary string)\n
 *   - `hcrc` (Boolean) - true if header crc should be added\n
 *\n
 * ##### Example:\n
 *\n
 * ```javascript\n
 * var pako = require(\'pako\')\n
 *   , chunk1 = Uint8Array([1,2,3,4,5,6,7,8,9])\n
 *   , chunk2 = Uint8Array([10,11,12,13,14,15,16,17,18,19]);\n
 *\n
 * var deflate = new pako.Deflate({ level: 3});\n
 *\n
 * deflate.push(chunk1, false);\n
 * deflate.push(chunk2, true);  // true -> last chunk\n
 *\n
 * if (deflate.err) { throw new Error(deflate.err); }\n
 *\n
 * console.log(deflate.result);\n
 * ```\n
 **/\n
var Deflate = function(options) 

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

{\n
\n
  this.options = utils.assign({\n
    level: Z_DEFAULT_COMPRESSION,\n
    method: Z_DEFLATED,\n
    chunkSize: 16384,\n
    windowBits: 15,\n
    memLevel: 8,\n
    strategy: Z_DEFAULT_STRATEGY,\n
    to: \'\'\n
  }, options || {});\n
\n
  var opt = this.options;\n
\n
  if (opt.raw && (opt.windowBits > 0)) {\n
    opt.windowBits = -opt.windowBits;\n
  }\n
\n
  else if (opt.gzip && (opt.windowBits > 0) && (opt.windowBits < 16)) {\n
    opt.windowBits += 16;\n
  }\n
\n
  this.err    = 0;      // error code, if happens (0 = Z_OK)\n
  this.msg    = \'\';     // error message\n
  this.ended  = false;  // used to avoid multiple onEnd() calls\n
  this.chunks = [];     // chunks of compressed data\n
\n
  this.strm = new zstream();\n
  this.strm.avail_out = 0;\n
\n
  var status = zlib_deflate.deflateInit2(\n
    this.strm,\n
    opt.level,\n
    opt.method,\n
    opt.windowBits,\n
    opt.memLevel,\n
    opt.strategy\n
  );\n
\n
  if (status !== Z_OK) {\n
    throw new Error(msg[status]);\n
  }\n
\n
  if (opt.header) {\n
    zlib_deflate.deflateSetHeader(this.strm, opt.header);\n
  }\n
};\n
\n
/**\n
 * Deflate#push(data[, mode]) -> Boolean\n
 * - data (Uint8Array|Array|String): input data. Strings will be converted to\n
 *   utf8 byte sequence.\n
 * - mode (Number|Boolean): 0..6 for corresponding Z_NO_FLUSH..Z_TREE modes.\n
 *   See constants. Skipped or `false` means Z_NO_FLUSH, `true` meansh Z_FINISH.\n
 *\n
 * Sends input data to deflate pipe, generating [[Deflate#onData]] calls with\n
 * new compressed chunks. Returns `true` on success. The last data block must have\n
 * mode Z_FINISH (or `true`). That flush internal pending buffers and call\n
 * [[Deflate#onEnd]].\n
 *\n
 * On fail call [[Deflate#onEnd]] with error code and return false.\n
 *\n
 * We strongly recommend to use `Uint8Array` on input for best speed (output\n
 * array format is detected automatically). Also, don\'t skip last param and always\n
 * use the same type in your code (boolean or number). That will improve JS speed.\n
 *\n
 * For regular `Array`-s make sure all elements are [0..255].\n
 *\n
 * ##### Example\n
 *\n
 * ```javascript\n
 * push(chunk, false); // push one of data chunks\n
 * ...\n
 * push(chunk, true);  // push last chunk\n
 * ```\n
 **/\n
Deflate.prototype.push = function(data, mode) {\n
  var strm = this.strm;\n
  var chunkSize = this.options.chunkSize;\n
  var status, _mode;\n
\n
  if (this.ended) { return false; }\n
\n
  _mode = (mode === ~~mode) ? mode : ((mode === true) ? Z_FINISH : Z_NO_FLUSH);\n
\n
  // Convert data if needed\n
  if (typeof data === \'string\') {\n
    // If we need to compress text, change encoding to utf8.\n
    strm.input = strings.string2buf(data);\n
  } else {\n
    strm.input = data;\n
  }\n
\n
  strm.next_in = 0;\n
  strm.avail_in = strm.input.length;\n
\n
  do {\n
    if (strm.avail_out === 0) {\n
      strm.output = new utils.Buf8(chunkSize);\n
      strm.next_out = 0;\n
      strm.avail_out = chunkSize;\n
    }\n
    status = zlib_deflate.deflate(strm, _mode);    /* no bad return value */\n
\n
    if (status !== Z_STREAM_END && status !== Z_OK) {\n
      this.onEnd(status);\n
      this.ended = true;\n
      return false;\n
    }\n
    if (strm.avail_out === 0 || (strm.avail_in === 0 && _mode === Z_FINISH)) {\n
      if (this.options.to === \'string\') {\n
        this.onData(strings.buf2binstring(utils.shrinkBuf(strm.output, strm.next_out)));\n
      } else {\n
        this.onData(utils.shrinkBuf(strm.output, strm.next_out));\n
      }\n
    }\n
  } while ((strm.avail_in > 0 || strm.avail_out === 0) && status !== Z_STREAM_END);\n
\n
  // Finalize on the last chunk.\n
  if (_mode === Z_FINISH) {\n
    status = zlib_deflate.deflateEnd(this.strm);\n
    this.onEnd(status);\n
    this.ended = true;\n
    return status === Z_OK;\n
  }\n
\n
  return true;\n
};\n
\n
\n
/**\n
 * Deflate#onData(chunk) -> Void\n
 * - chunk (Uint8Array|Array|String): ouput data. Type of array depends\n
 *   on js engine support. When string output requested, each chunk\n
 *   will be string.\n
 *\n
 * By default, stores data blocks in `chunks[]` property and glue\n
 * those in `onEnd`. Override this handler, if you need another behaviour.\n
 **/\n
Deflate.prototype.onData = function(chunk) {\n
  this.chunks.push(chunk);\n
};\n
\n
\n
/**\n
 * Deflate#onEnd(status) -> Void\n
 * - status (Number): deflate status. 0 (Z_OK) on success,\n
 *   other if not.\n
 *\n
 * Called once after you tell deflate that input stream complete\n
 * or error happenned. By default - join collected chunks,\n
 * free memory and fill `results` / `err` properties.\n
 **/\n
Deflate.prototype.onEnd = function(status) {\n
  // On success - join\n
  if (status === Z_OK) {\n
    if (this.options.to === \'string\') {\n
      this.result = this.chunks.join(\'\');\n
    } else {\n
      this.result = utils.flattenChunks(this.chunks);\n
    }\n
  }\n
  this.chunks = [];\n
  this.err = status;\n
  this.msg = this.strm.msg;\n
};\n
\n
\n
/**\n
 * deflate(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to compress.\n
 * - options (Object): zlib deflate options.\n
 *\n
 * Compress `data` with deflate alrorythm and `options`.\n
 *\n
 * Supported options are:\n
 *\n
 * - level\n
 * - windowBits\n
 * - memLevel\n
 * - strategy\n
 *\n
 * [http://zlib.net/manual.html#Advanced](http://zlib.net/manual.html#Advanced)\n
 * for more information on these.\n
 *\n
 * Sugar (options):\n
 *\n
 * - `raw` (Boolean) - say that we work with raw stream, if you don\'t wish to specify\n
 *   negative windowBits implicitly.\n
 * - `to` (String) - if equal to \'string\', then result will be "binary string"\n
 *    (each char code [0..255])\n
 *\n
 * ##### Example:\n
 *\n
 * ```javascript\n
 * var pako = require(\'pako\')\n
 *   , data = Uint8Array([1,2,3,4,5,6,7,8,9]);\n
 *\n
 * console.log(pako.deflate(data));\n
 * ```\n
 **/\n
function deflate(input, options) {\n
  var deflator = new Deflate(options);\n
\n
  deflator.push(input, true);\n
\n
  // That will never happens, if you don\'t cheat with options :)\n
  if (deflator.err) { throw deflator.msg; }\n
\n
  return deflator.result;\n
}\n
\n
\n
/**\n
 * deflateRaw(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to compress.\n
 * - options (Object): zlib deflate options.\n
 *\n
 * The same as [[deflate]], but creates raw data, without wrapper\n
 * (header and adler32 crc).\n
 **/\n
function deflateRaw(input, options) {\n
  options = options || {};\n
  options.raw = true;\n
  return deflate(input, options);\n
}\n
\n
\n
/**\n
 * gzip(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to compress.\n
 * - options (Object): zlib deflate options.\n
 *\n
 * The same as [[deflate]], but create gzip wrapper instead of\n
 * deflate one.\n
 **/\n
function gzip(input, options) {\n
  options = options || {};\n
  options.gzip = true;\n
  return deflate(input, options);\n
}\n
\n
\n
exports.Deflate = Deflate;\n
exports.deflate = deflate;\n
exports.deflateRaw = deflateRaw;\n
exports.gzip = gzip;\n
},{"./utils/common":27,"./utils/strings":28,"./zlib/deflate.js":32,"./zlib/messages":37,"./zlib/zstream":39}],26:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var zlib_inflate = _dereq_(\'./zlib/inflate.js\');\n
var utils = _dereq_(\'./utils/common\');\n
var strings = _dereq_(\'./utils/strings\');\n
var c = _dereq_(\'./zlib/constants\');\n
var msg = _dereq_(\'./zlib/messages\');\n
var zstream = _dereq_(\'./zlib/zstream\');\n
var gzheader = _dereq_(\'./zlib/gzheader\');\n
\n
\n
/**\n
 * class Inflate\n
 *\n
 * Generic JS-style wrapper for zlib calls. If you don\'t need\n
 * streaming behaviour - use more simple functions: [[inflate]]\n
 * and [[inflateRaw]].\n
 **/\n
\n
/* internal\n
 * inflate.chunks -> Array\n
 *\n
 * Chunks of output data, if [[Inflate#onData]] not overriden.\n
 **/\n
\n
/**\n
 * Inflate.result -> Uint8Array|Array|String\n
 *\n
 * Uncompressed result, generated by default [[Inflate#onData]]\n
 * and [[Inflate#onEnd]] handlers. Filled after you push last chunk\n
 * (call [[Inflate#push]] with `Z_FINISH` / `true` param).\n
 **/\n
\n
/**\n
 * Inflate.err -> Number\n
 *\n
 * Error code after inflate finished. 0 (Z_OK) on success.\n
 * Should be checked if broken data possible.\n
 **/\n
\n
/**\n
 * Inflate.msg -> String\n
 *\n
 * Error message, if [[Inflate.err]] != 0\n
 **/\n
\n
\n
/**\n
 * new Inflate(options)\n
 * - options (Object): zlib inflate options.\n
 *\n
 * Creates new inflator instance with specified params. Throws exception\n
 * on bad params. Supported options:\n
 *\n
 * - `windowBits`\n
 *\n
 * [http://zlib.net/manual.html#Advanced](http://zlib.net/manual.html#Advanced)\n
 * for more information on these.\n
 *\n
 * Additional options, for internal needs:\n
 *\n
 * - `chunkSize` - size of generated data chunks (16K by default)\n
 * - `raw` (Boolean) - do raw inflate\n
 * - `to` (String) - if equal to \'string\', then result will be converted\n
 *   from utf8 to utf16 (javascript) string. When string output requested,\n
 *   chunk length can differ from `chunkSize`, depending on content.\n
 *\n
 * By default, when no options set, autodetect deflate/gzip data format via\n
 * wrapper header.\n
 *\n
 * ##### Example:\n
 *\n
 * ```javascript\n
 * var pako = require(\'pako\')\n
 *   , chunk1 = Uint8Array([1,2,3,4,5,6,7,8,9])\n
 *   , chunk2 = Uint8Array([10,11,12,13,14,15,16,17,18,19]);\n
 *\n
 * var inflate = new pako.Inflate({ level: 3});\n
 *\n
 * inflate.push(chunk1, false);\n
 * inflate.push(chunk2, true);  // true -> last chunk\n
 *\n
 * if (inflate.err) { throw new Error(inflate.err); }\n
 *\n
 * console.log(inflate.result);\n
 * ```\n
 **/\n
var Inflate = function(options) {\n
\n
  this.options = utils.assign({\n
    chunkSize: 16384,\n
    windowBits: 0,\n
    to: \'\'\n
  }, options || {});\n
\n
  var opt = this.options;\n
\n
  // Force window size for `raw` data, if not set directly,\n
  // because we have no header for autodetect.\n
  if (opt.raw && (opt.windowBits >= 0) && (opt.windowBits < 16)) {\n
    opt.windowBits = -opt.windowBits;\n
    if (opt.windowBits === 0) { opt.windowBits = -15; }\n
  }\n
\n
  // If `windowBits` not defined (and mode not raw) - set autodetect flag for gzip/deflate\n
  if ((opt.windowBits >= 0) && (opt.windowBits < 16) &&\n
      !(options && options.windowBits)) {\n
    opt.windowBits += 32;\n
  }\n
\n
  // Gzip header has no info about windows size, we can do autodetect only\n
  // for deflate. So, if window size not set, force it to max when gzip possible\n
  if ((opt.windowBits > 15) && (opt.windowBits < 48)) {\n
    // bit 3 (16) -> gzipped data\n
    // bit 4 (32) -> autodetect gzip/deflate\n
    if ((opt.windowBits & 15) === 0) {\n
      opt.windowBits |= 15;\n
    }\n
  }\n
\n
  this.err    = 0;      // error code, if happens (0 = Z_OK)\n
  this.msg    = \'\';     // error message\n
  this.ended  = false;  // used to avoid multiple onEnd() calls\n
  this.chunks = [];     // chunks of compressed data\n
\n
  this.strm   = new zstream();\n
  this.strm.avail_out = 0;\n
\n
  var status  = zlib_inflate.inflateInit2(\n
    this.strm,\n
    opt.windowBits\n
  );\n
\n
  if (status !== c.Z_OK) {\n
    throw new Error(msg[status]);\n
  }\n
\n
  this.header = new gzheader();\n
\n
  zlib_inflate.inflateGetHeader(this.strm, this.header);\n
};\n
\n
/**\n
 * Inflate#push(data[, mode]) -> Boolean\n
 * - data (Uint8Array|Array|String): input data\n
 * - mode (Number|Boolean): 0..6 for corresponding Z_NO_FLUSH..Z_TREE modes.\n
 *   See constants. Skipped or `false` means Z_NO_FLUSH, `true` meansh Z_FINISH.\n
 *\n
 * Sends input data to inflate pipe, generating [[Inflate#onData]] calls with\n
 * new output chunks. Returns `true` on success. The last data block must have\n
 * mode Z_FINISH (or `true`). That flush internal pending buffers and call\n
 * [[Inflate#onEnd]].\n
 *\n
 * On fail call [[Inflate#onEnd]] with error code and return false.\n
 *\n
 * We strongly recommend to use `Uint8Array` on input for best speed (output\n
 * format is detected automatically). Also, don\'t skip last param and always\n
 * use the same type in your code (boolean or number). That will improve JS speed.\n
 *\n
 * For regular `Array`-s make sure all elements are [0..255].\n
 *\n
 * ##### Example\n
 *\n
 * ```javascript\n
 * push(chunk, false); // push one of data chunks\n
 * ...\n
 * push(chunk, true);  // push last chunk\n
 * ```\n
 **/\n
Inflate.prototype.push = function(data, mode) {\n
  var strm = this.strm;\n
  var chunkSize = this.options.chunkSize;\n
  var status, _mode;\n
  var next_out_utf8, tail, utf8str;\n
\n
  if (this.ended) { return false; }\n
  _mode = (mode === ~~mode) ? mode : ((mode === true) ? c.Z_FINISH : c.Z_NO_FLUSH);\n
\n
  // Convert data if needed\n
  if (typeof data === \'string\') {\n
    // Only binary strings can be decompressed on practice\n
    strm.input = strings.binstring2buf(data);\n
  } else {\n
    strm.input = data;\n
  }\n
\n
  strm.next_in = 0;\n
  strm.avail_in = strm.input.length;\n
\n
  do {\n
    if (strm.avail_out === 0) {\n
      strm.output = new utils.Buf8(chunkSize);\n
      strm.next_out = 0;\n
      strm.avail_out = chunkSize;\n
    }\n
\n
    status = zlib_inflate.inflate(strm, c.Z_NO_FLUSH);    /* no bad return value */\n
\n
    if (status !== c.Z_STREAM_END && status !== c.Z_OK) {\n
      this.onEnd(status);\n
      this.ended = true;\n
      return false;\n
    }\n
\n
    if (strm.next_out) {\n
      if (strm.avail_out === 0 || status === c.Z_STREAM_END || (strm.avail_in === 0 && _mode === c.Z_FINISH)) {\n
\n
        if (this.options.to === \'string\') {\n
\n
          next_out_utf8 = strings.utf8border(strm.output, strm.next_out);\n
\n
          tail = strm.next_out - next_out_utf8;\n
          utf8str = strings.buf2string(strm.output, next_out_utf8);\n
\n
          // move tail\n
          strm.next_out = tail;\n
          strm.avail_out = chunkSize - tail;\n
          if (tail) { utils.arraySet(strm.output, strm.output, next_out_utf8, tail, 0); }\n
\n
          this.onData(utf8str);\n
\n
        } else {\n
          this.onData(utils.shrinkBuf(strm.output, strm.next_out));\n
        }\n
      }\n
    }\n
  } while ((strm.avail_in > 0) && status !== c.Z_STREAM_END);\n
\n
  if (status === c.Z_STREAM_END) {\n
    _mode = c.Z_FINISH;\n
  }\n
  // Finalize on the last chunk.\n
  if (_mode === c.Z_FINISH) {\n
    status = zlib_inflate.inflateEnd(this.strm);\n
    this.onEnd(status);\n
    this.ended = true;\n
    return status === c.Z_OK;\n
  }\n
\n
  return true;\n
};\n
\n
\n
/**\n
 * Inflate#onData(chunk) -> Void\n
 * - chunk (Uint8Array|Array|String): ouput data. Type of array depends\n
 *   on js engine support. When string output requested, each chunk\n
 *   will be string.\n
 *\n
 * By default, stores data blocks in `chunks[]` property and glue\n
 * those in `onEnd`. Override this handler, if you need another behaviour.\n
 **/\n
Inflate.prototype.onData = function(chunk) {\n
  this.chunks.push(chunk);\n
};\n
\n
\n
/**\n
 * Inflate#onEnd(status) -> Void\n
 * - status (Number): inflate status. 0 (Z_OK) on success,\n
 *   other if not.\n
 *\n
 * Called once after you tell inflate that input stream complete\n
 * or error happenned. By default - join collected chunks,\n
 * free memory and fill `results` / `err` properties.\n
 **/\n
Inflate.prototype.onEnd = function(status) {\n
  // On success - join\n
  if (status === c.Z_OK) {\n
    if (this.options.to === \'string\') {\n
      // Glue & convert here, until we teach pako to send\n
      // utf8 alligned strings to onData\n
      this.result = this.chunks.join(\'\');\n
    } else {\n
      this.result = utils.flattenChunks(this.chunks);\n
    }\n
  }\n
  this.chunks = [];\n
  this.err = status;\n
  this.msg = this.strm.msg;\n
};\n
\n
\n
/**\n
 * inflate(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to decompress.\n
 * - options (Object): zlib inflate options.\n
 *\n
 * Decompress `data` with inflate/ungzip and `options`. Autodetect\n
 * format via wrapper header by default. That\'s why we don\'t provide\n
 * separate `ungzip` method.\n
 *\n
 * Supported options are:\n
 *\n
 * - windowBits\n
 *\n
 * [http://zlib.net/manual.html#Advanced](http://zlib.net/manual.html#Advanced)\n
 * for more information.\n
 *\n
 * Sugar (options):\n
 *\n
 * - `raw` (Boolean) - say that we work with raw stream, if you don\'t wish to specify\n
 *   negative windowBits implicitly.\n
 * - `to` (String) - if equal to \'string\', then result will be converted\n
 *   from utf8 to utf16 (javascript) string. When string output requested,\n
 *   chunk length can differ from `chunkSize`, depending on content.\n
 *\n
 *\n
 * ##### Example:\n
 *\n
 * ```javascript\n
 * var pako = require(\'pako\')\n
 *   , input = pako.deflate([1,2,3,4,5,6,7,8,9])\n
 *   , output;\n
 *\n
 * try {\n
 *   output = pako.inflate(input);\n
 * } catch (err)\n
 *   console.log(err);\n
 * }\n
 * ```\n
 **/\n
function inflate(input, options) {\n
  var inflator = new Inflate(options);\n
\n
  inflator.push(input, true);\n
\n
  // That will never happens, if you don\'t cheat with options :)\n
  if (inflator.err) { throw inflator.msg; }\n
\n
  return inflator.result;\n
}\n
\n
\n
/**\n
 * inflateRaw(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to decompress.\n
 * - options (Object): zlib inflate options.\n
 *\n
 * The same as [[inflate]], but creates raw data, without wrapper\n
 * (header and adler32 crc).\n
 **/\n
function inflateRaw(input, options) {\n
  options = options || {};\n
  options.raw = true;\n
  return inflate(input, options);\n
}\n
\n
\n
/**\n
 * ungzip(data[, options]) -> Uint8Array|Array|String\n
 * - data (Uint8Array|Array|String): input data to decompress.\n
 * - options (Object): zlib inflate options.\n
 *\n
 * Just shortcut to [[inflate]], because it autodetects format\n
 * by header.content. Done for convenience.\n
 **/\n
\n
\n
exports.Inflate = Inflate;\n
exports.inflate = inflate;\n
exports.inflateRaw = inflateRaw;\n
exports.ungzip  = inflate;\n
\n
},{"./utils/common":27,"./utils/strings":28,"./zlib/constants":30,"./zlib/gzheader":33,"./zlib/inflate.js":35,"./zlib/messages":37,"./zlib/zstream":39}],27:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var TYPED_OK =  (typeof Uint8Array !== \'undefined\') &&\n
                (typeof Uint16Array !== \'undefined\') &&\n
                (typeof Int32Array !== \'undefined\');\n
\n
\n
exports.assign = function (obj /*from1, from2, from3, ...*/) {\n
  var sources = Array.prototype.slice.call(arguments, 1);\n
  while (sources.length) {\n
    var source = sources.shift();\n
    if (!source) { continue; }\n
\n
    if (typeof(source) !== \'object\') {\n
      throw new TypeError(source + \'must be non-object\');\n
    }\n
\n
    for (var p in source) {\n
      if (source.hasOwnProperty(p)) {\n
        obj[p] = source[p];\n
      }\n
    }\n
  }\n
\n
  return obj;\n
};\n
\n
\n
// reduce buffer size, avoiding mem copy\n
exports.shrinkBuf = function (buf, size) {\n
  if (buf.length === size) { return buf; }\n
  if (buf.subarray) { return buf.subarray(0, size); }\n
  buf.length = size;\n
  return buf;\n
};\n
\n
\n
var fnTyped = {\n
  arraySet: function (dest, src, src_offs, len, dest_offs) {\n
    if (src.subarray && dest.subarray) {\n
      dest.set(src.subarray(src_offs, src_offs+len), dest_offs);\n
      return;\n
    }\n
    // Fallback to ordinary array\n
    for(var i=0; i<len; i++) {\n
      dest[dest_offs + i] = src[src_offs + i];\n
    }\n
  },\n
  // Join array of chunks to single array.\n
  flattenChunks: function(chunks) {\n
    var i, l, len, pos, chunk, result;\n
\n
    // calculate data length\n
    len = 0;\n
    for (i=0, l=chunks.length; i<l; i++) {\n
      len += chunks[i].length;\n
    }\n
\n
    // join chunks\n
    result = new Uint8Array(len);\n
    pos = 0;\n
    for (i=0, l=chunks.length; i<l; i++) {\n
      chunk = chunks[i];\n
      result.set(chunk, pos);\n
      pos += chunk.length;\n
    }\n
\n
    return result;\n
  }\n
};\n
\n
var fnUntyped = {\n
  arraySet: function (dest, src, src_offs, len, dest_offs) {\n
    for(var i=0; i<len; i++) {\n
      dest[dest_offs + i] = src[src_offs + i];\n
    }\n
  },\n
  // Join array of chunks to single array.\n
  flattenChunks: function(chunks) {\n
    return [].concat.apply([], chunks);\n
  }\n
};\n
\n
\n
// Enable/Disable typed arrays use, for testing\n
//\n
exports.setTyped = function (on) {\n
  if (on) {\n
    exports.Buf8  = Uint8Array;\n
    exports.Buf16 = Uint16Array;\n
    exports.Buf32 = Int32Array;\n
    exports.assign(exports, fnTyped);\n
  } else {\n
    exports.Buf8  = Array;\n
    exports.Buf16 = Array;\n
    exports.Buf32 = Array;\n
    exports.assign(exports, fnUntyped);\n
  }\n
};\n
\n
exports.setTyped(TYPED_OK);\n
},{}],28:[function(_dereq_,module,exports){\n
// String encode/decode helpers\n
\'use strict\';\n
\n
\n
var utils = _dereq_(\'./common\');\n
\n
\n
// Quick check if we can use fast array to bin string conversion\n
//\n
// - apply(Array) can fail on Android 2.2\n
// - apply(Uint8Array) can fail on iOS 5.1 Safary\n
//\n
var STR_APPLY_OK = true;\n
var STR_APPLY_UIA_OK = true;\n
\n
try { String.fromCharCode.apply(null, [0]); } catch(__) { STR_APPLY_OK = false; }\n
try { String.fromCharCode.apply(null, new Uint8Array(1)); } catch(__) { STR_APPLY_UIA_OK = false; }\n
\n
\n
// Table with utf8 lengths (calculated by first byte of sequence)\n
// Note, that 5 & 6-byte values and some 4-byte values can not be represented in JS,\n
// because max possible codepoint is 0x10ffff\n
var _utf8len = new utils.Buf8(256);\n
for (var i=0; i<256; i++) {\n
  _utf8len[i] = (i >= 252 ? 6 : i >= 248 ? 5 : i >= 240 ? 4 : i >= 224 ? 3 : i >= 192 ? 2 : 1);\n
}\n
_utf8len[254]=_utf8len[254]=1; // Invalid sequence start\n
\n
\n
// convert string to array (typed, when possible)\n
exports.string2buf = function (str) {\n
  var buf, c, c2, m_pos, i, str_len = str.length, buf_len = 0;\n
\n
  // count binary size\n
  for (m_pos = 0; m_pos < str_len; m_pos++) {\n
    c = str.charCodeAt(m_pos);\n
    if ((c & 0xfc00) === 0xd800 && (m_pos+1 < str_len)) {\n
      c2 = str.charCodeAt(m_pos+1);\n
      if ((c2 & 0xfc00) === 0xdc00) {\n
        c = 0x10000 + ((c - 0xd800) << 10) + (c2 - 0xdc00);\n
        m_pos++;\n
      }\n
    }\n
    buf_len += c < 0x80 ? 1 : c < 0x800 ? 2 : c < 0x10000 ? 3 : 4;\n
  }\n
\n
  // allocate buffer\n
  buf = new utils.Buf8(buf_len);\n
\n
  // convert\n
  for (i=0, m_pos = 0; i < buf_len; m_pos++) {\n
    c = str.charCodeAt(m_pos);\n
    if ((c & 0xfc00) === 0xd800 && (m_pos+1 < str_len)) {\n
      c2 = str.charCodeAt(m_pos+1);\n
      if ((c2 & 0xfc00) === 0xdc00) {\n
        c = 0x10000 + ((c - 0xd800) << 10) + (c2 - 0xdc00);\n
        m_pos++;\n
      }\n
    }\n
    if (c < 0x80) {\n
      /* one byte */\n
      buf[i++] = c;\n
    } else if (c < 0x800) {\n
      /* two bytes */\n
      buf[i++] = 0xC0 | (c >>> 6);\n
      buf[i++] = 0x80 | (c & 0x3f);\n
    } else if (c < 0x10000) {\n
      /* three bytes */\n
      buf[i++] = 0xE0 | (c >>> 12);\n
      buf[i++] = 0x80 | (c >>> 6 & 0x3f);\n
      buf[i++] = 0x80 | (c & 0x3f);\n
    } else {\n
      /* four bytes */\n
      buf[i++] = 0xf0 | (c >>> 18);\n
      buf[i++] = 0x80 | (c >>> 12 & 0x3f);\n
      buf[i++] = 0x80 | (c >>> 6 & 0x3f);\n
      buf[i++] = 0x80 | (c & 0x3f);\n
    }\n
  }\n
\n
  return buf;\n
};\n
\n
// Helper (used in 2 places)\n
function buf2binstring(buf, len) {\n
  // use fallback for big arrays to avoid stack overflow\n
  if (len < 65537) {\n
    if ((buf.subarray && STR_APPLY_UIA_OK) || (!buf.subarray && STR_APPLY_OK)) {\n
      return String.fromCharCode.apply(null, utils.shrinkBuf(buf, len));\n
    }\n
  }\n
\n
  var result = \'\';\n
  for(var i=0; i < len; i++) {\n
    result += String.fromCharCode(buf[i]);\n
  }\n
  return result;\n
}\n
\n
\n
// Convert byte array to binary string\n
exports.buf2binstring = function(buf) {\n
  return buf2binstring(buf, buf.length);\n
};\n
\n
\n
// Convert binary string (typed, when possible)\n
exports.binstring2buf = function(str) {\n
  var buf = new utils.Buf8(str.length);\n
  for(var i=0, len=buf.length; i < len; i++) {\n
    buf[i] = str.charCodeAt(i);\n
  }\n
  return buf;\n
};\n
\n
\n
// convert array to string\n
exports.buf2string = function (buf, max) {\n
  var i, out, c, c_len;\n
  var len = max || buf.length;\n
\n
  // Reserve max possible length (2 words per char)\n
  // NB: by unknown reasons, Array is significantly faster for\n
  //     String.fromCharCode.apply than Uint16Array.\n
  var utf16buf = new Array(len*2);\n
\n
  for (out=0, i=0; i<len;) {\n
    c = buf[i++];\n
    // quick process ascii\n
    if (c < 0x80) { utf16buf[out++] = c; continue; }\n
\n
    c_len = _utf8len[c];\n
    // skip 5 & 6 byte codes\n
    if (c_len > 4) { utf16buf[out++] = 0xfffd; i += c_len-1; continue; }\n
\n
    // apply mask on first byte\n
    c &= c_len === 2 ? 0x1f : c_len === 3 ? 0x0f : 0x07;\n
    // join the rest\n
    while (c_len > 1 && i < len) {\n
      c = (c << 6) | (buf[i++] & 0x3f);\n
      c_len--;\n
    }\n
\n
    // terminated by end of string?\n
    if (c_len > 1) { utf16buf[out++] = 0xfffd; continue; }\n
\n
    if (c < 0x10000) {\n
      utf16buf[out++] = c;\n
    } else {\n
      c -= 0x10000;\n
      utf16buf[out++] = 0xd800 | ((c >> 10) & 0x3ff);\n
      utf16buf[out++] = 0xdc00 | (c & 0x3ff);\n
    }\n
  }\n
\n
  return buf2binstring(utf16buf, out);\n
};\n
\n
\n
// Calculate max possible position in utf8 buffer,\n
// that will not break sequence. If that\'s not possible\n
// - (very small limits) return max size as is.\n
//\n
// buf[] - utf8 bytes array\n
// max   - length limit (mandatory);\n
exports.utf8border = function(buf, max) {\n
  var pos;\n
\n
  max = max || buf.length;\n
  if (max > buf.length) { max = buf.length; }\n
\n
  // go back from last position, until start of sequence found\n
  pos = max-1;\n
  while (pos >= 0 && (buf[pos] & 0xC0) === 0x80) { pos--; }\n
\n
  // Fuckup - very small and broken sequence,\n
  // return max, because we should return something anyway.\n
  if (pos < 0) { return max; }\n
\n
  // If we came to start of buffer - that means vuffer is too small,\n
  // return max too.\n
  if (pos === 0) { return max; }\n
\n
  return (pos + _utf8len[buf[pos]] > max) ? pos : max;\n
};\n
\n
},{"./common":27}],29:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
// Note: adler32 takes 12% for level 0 and 2% for level 6.\n
// It doesn\'t worth to make additional optimizationa as in original.\n
// Small size is preferable.\n
\n
function adler32(adler, buf, len, pos) {\n
  var s1 = (adler & 0xffff) |0\n
    , s2 = ((adler >>> 16) & 0xffff) |0\n
    , n = 0;\n
\n
  while (len !== 0) {\n
    // Set limit ~ twice less than 5552, to keep\n
    // s2 in 31-bits, because we force signed ints.\n
    // in other case %= will fail.\n
    n = len > 2000 ? 2000 : len;\n
    len -= n;\n
\n
    do {\n
      s1 = (s1 + buf[pos++]) |0;\n
      s2 = (s2 + s1) |0;\n
    } while (--n);\n
\n
    s1 %= 65521;\n
    s2 %= 65521;\n
  }\n
\n
  return (s1 | (s2 << 16)) |0;\n
}\n
\n
\n
module.exports = adler32;\n
},{}],30:[function(_dereq_,module,exports){\n
module.exports = {\n
\n
  /* Allowed flush values; see deflate() and inflate() below for details */\n
  Z_NO_FLUSH:         0,\n
  Z_PARTIAL_FLUSH:    1,\n
  Z_SYNC_FLUSH:       2,\n
  Z_FULL_FLUSH:       3,\n
  Z_FINISH:           4,\n
  Z_BLOCK:            5,\n
  Z_TREES:            6,\n
\n
  /* Return codes for the compression/decompression functions. Negative values\n
  * are errors, positive values are used for special but normal events.\n
  */\n
  Z_OK:               0,\n
  Z_STREAM_END:       1,\n
  Z_NEED_DICT:        2,\n
  Z_ERRNO:           -1,\n
  Z_STREAM_ERROR:    -2,\n
  Z_DATA_ERROR:      -3,\n
  //Z_MEM_ERROR:     -4,\n
  Z_BUF_ERROR:       -5,\n
  //Z_VERSION_ERROR: -6,\n
\n
  /* compression levels */\n
  Z_NO_COMPRESSION:         0,\n
  Z_BEST_SPEED:             1,\n
  Z_BEST_COMPRESSION:       9,\n
  Z_DEFAULT_COMPRESSION:   -1,\n
\n
\n
  Z_FILTERED:               1,\n
  Z_HUFFMAN_ONLY:           2,\n
  Z_RLE:                    3,\n
  Z_FIXED:                  4,\n
  Z_DEFAULT_STRATEGY:       0,\n
\n
  /* Possible values of the data_type field (though see inflate()) */\n
  Z_BINARY:                 0,\n
  Z_TEXT:                   1,\n
  //Z_ASCII:                1, // = Z_TEXT (deprecated)\n
  Z_UNKNOWN:                2,\n
\n
  /* The deflate compression method */\n
  Z_DEFLATED:               8\n
  //Z_NULL:                 null // Use -1 or null inline, depending on var type\n
};\n
},{}],31:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
// Note: we can\'t get significant speed boost here.\n
// So write code to minimize size - no pregenerated tables\n
// and array tools dependencies.\n
\n
\n
// Use ordinary array, since untyped makes no boost here\n
function makeTable() {\n
  var c, table = [];\n
\n
  for(var n =0; n < 256; n++){\n
    c = n;\n
    for(var k =0; k < 8; k++){\n
      c = ((c&1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));\n
    }\n
    table[n] = c;\n
  }\n
\n
  return table;\n
}\n
\n
// Create table on load. Just 255 signed longs. Not a problem.\n
var crcTable = makeTable();\n
\n
\n
function crc32(crc, buf, len, pos) {\n
  var t = crcTable\n
    , end = pos + len;\n
\n
  crc = crc ^ (-1);\n
\n
  for (var i = pos; i < end; i++ ) {\n
    crc = (crc >>> 8) ^ t[(crc ^ buf[i]) & 0xFF];\n
  }\n
\n
  return (crc ^ (-1)); // >>> 0;\n
}\n
\n
\n
module.exports = crc32;\n
},{}],32:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
var utils   = _dereq_(\'../utils/common\');\n
var trees   = _dereq_(\'./trees\');\n
var adler32 = _dereq_(\'./adler32\');\n
var crc32   = _dereq_(\'./crc32\');\n
var msg   = _dereq_(\'./messages\');\n
\n
/* Public constants ==========================================================*/\n
/* ===========================================================================*/\n
\n
\n
/* Allowed flush values; see deflate() and inflate() below for details */\n
var Z_NO_FLUSH      = 0;\n
var Z_PARTIAL_FLUSH = 1;\n
//var Z_SYNC_FLUSH    = 2;\n
var Z_FULL_FLUSH    = 3;\n
var Z_FINISH        = 4;\n
var Z_BLOCK         = 5;\n
//var Z_TREES         = 6;\n
\n
\n
/* Return codes for the compression/decompression functions. Negative values\n
 * are errors, positive values are used for special but normal events.\n
 */\n
var Z_OK            = 0;\n
var Z_STREAM_END    = 1;\n
//var Z_NEED_DICT     = 2;\n
//var Z_ERRNO         = -1;\n
var Z_STREAM_ERROR  = -2;\n
var Z_DATA_ERROR    = -3;\n
//var Z_MEM_ERROR     = -4;\n
var Z_BUF_ERROR     = -5;\n
//var Z_VERSION_ERROR = -6;\n
\n
\n
/* compression levels */\n
//var Z_NO_COMPRESSION      = 0;\n
//var Z_BEST_SPEED          = 1;\n
//var Z_BEST_COMPRESSION    = 9;\n
var Z_DEFAULT_COMPRESSION = -1;\n
\n
\n
var Z_FILTERED            = 1;\n
var Z_HUFFMAN_ONLY        = 2;\n
var Z_RLE                 = 3;\n
var Z_FIXED               = 4;\n
var Z_DEFAULT_STRATEGY    = 0;\n
\n
/* Possible values of the data_type field (though see inflate()) */\n
//var Z_BINARY              = 0;\n
//var Z_TEXT                = 1;\n
//var Z_ASCII               = 1; // = Z_TEXT\n
var Z_UNKNOWN             = 2;\n
\n
\n
/* The deflate compression method */\n
var Z_DEFLATED  = 8;\n
\n
/*============================================================================*/\n
\n
\n
var MAX_MEM_LEVEL = 9;\n
/* Maximum value for memLevel in deflateInit2 */\n
var MAX_WBITS = 15;\n
/* 32K LZ77 window */\n
var DEF_MEM_LEVEL = 8;\n
\n
\n
var LENGTH_CODES  = 29;\n
/* number of length codes, not counting the special END_BLOCK code */\n
var LITERALS      = 256;\n
/* number of literal bytes 0..255 */\n
var L_CODES       = LITERALS + 1 + LENGTH_CODES;\n
/* number of Literal or Length codes, including the END_BLOCK code */\n
var D_CODES       = 30;\n
/* number of distance codes */\n
var BL_CODES      = 19;\n
/* number of codes used to transfer the bit lengths */\n
var HEAP_SIZE     = 2*L_CODES + 1;\n
/* maximum heap size */\n
var MAX_BITS  = 15;\n
/* All codes must not exceed MAX_BITS bits */\n
\n
var MIN_MATCH = 3;\n
var MAX_MATCH = 258;\n
var MIN_LOOKAHEAD = (MAX_MATCH + MIN_MATCH + 1);\n
\n
var PRESET_DICT = 0x20;\n
\n
var INIT_STATE = 42;\n
var EXTRA_STATE = 69;\n
var NAME_STATE = 73;\n
var COMMENT_STATE = 91;\n
var HCRC_STATE = 103;\n
var BUSY_STATE = 113;\n
var FINISH_STATE = 666;\n
\n
var BS_NEED_MORE      = 1; /* block not completed, need more input or more output */\n
var BS_BLOCK_DONE     = 2; /* block flush performed */\n
var BS_FINISH_STARTED = 3; /* finish started, need only more output at next deflate */\n
var BS_FINISH_DONE    = 4; /* finish done, accept no more input or output */\n
\n
var OS_CODE = 0x03; // Unix :) . Don\'t detect, use this default.\n
\n
function err(strm, errorCode) {\n
  strm.msg = msg[errorCode];\n
  return errorCode;\n
}\n
\n
function rank(f) {\n
  return ((f) << 1) - ((f) > 4 ? 9 : 0);\n
}\n
\n
function zero(buf) { var len = buf.length; while (--len >= 0) { buf[len] = 0; } }\n
\n
\n
/* =========================================================================\n
 * Flush as much pending output as possible. All deflate() output goes\n
 * through this function so some applications may wish to modify it\n
 * to avoid allocating a large strm->output buffer and copying into it.\n
 * (See also read_buf()).\n
 */\n
function flush_pending(strm) {\n
  var s = strm.state;\n
\n
  //_tr_flush_bits(s);\n
  var len = s.pending;\n
  if (len > strm.avail_out) {\n
    len = strm.avail_out;\n
  }\n
  if (len === 0) { return; }\n
\n
  utils.arraySet(strm.output, s.pending_buf, s.pending_out, len, strm.next_out);\n
  strm.next_out += len;\n
  s.pending_out += len;\n
  strm.total_out += len;\n
  strm.avail_out -= len;\n
  s.pending -= len;\n
  if (s.pending === 0) {\n
    s.pending_out = 0;\n
  }\n
}\n
\n
\n
function flush_block_only (s, last) {\n
  trees._tr_flush_block(s, (s.block_start >= 0 ? s.block_start : -1), s.strstart - s.block_start, last);\n
  s.block_start = s.strstart;\n
  flush_pending(s.strm);\n
}\n
\n
\n
function put_byte(s, b) {\n
  s.pending_buf[s.pending++] = b;\n
}\n
\n
\n
/* =========================================================================\n
 * Put a short in the pending buffer. The 16-bit value is put in MSB order.\n
 * IN assertion: the stream state is correct and there is enough room in\n
 * pending_buf.\n
 */\n
function putShortMSB(s, b) {\n
//  put_byte(s, (Byte)(b >> 8));\n
//  put_byte(s, (Byte)(b & 0xff));\n
  s.pending_buf[s.pending++] = (b >>> 8) & 0xff;\n
  s.pending_buf[s.pending++] = b & 0xff;\n
}\n
\n
\n
/* ===========================================================================\n
 * Read a new buffer from the current input stream, update the adler32\n
 * and total number of bytes read.  All deflate() input goes through\n
 * this function so some applications may wish to modify it to avoid\n
 * allocating a large strm->input buffer and copying from it.\n
 * (See also flush_pending()).\n
 */\n
function read_buf(strm, buf, start, size) {\n
  var len = strm.avail_in;\n
\n
  if (len > size) { len = size; }\n
  if (len === 0) { return 0; }\n
\n
  strm.avail_in -= len;\n
\n
  utils.arraySet(buf, strm.input, strm.next_in, len, start);\n
  if (strm.state.wrap === 1) {\n
    strm.adler = adler32(strm.adler, buf, len, start);\n
  }\n
\n
  else if (strm.state.wrap === 2) {\n
    strm.adler = crc32(strm.adler, buf, len, start);\n
  }\n
\n
  strm.next_in += len;\n
  strm.total_in += len;\n
\n
  return len;\n
}\n
\n
\n
/* ===========================================================================\n
 * Set match_start to the longest match starting at the given string and\n
 * return its length. Matches shorter or equal to prev_length are discarded,\n
 * in which case the result is equal to prev_length and match_start is\n
 * garbage.\n
 * IN assertions: cur_match is the head of the hash chain for the current\n
 *   string (strstart) and its distance is <= MAX_DIST, and prev_length >= 1\n
 * OUT assertion: the match length is not greater than s->lookahead.\n
 */\n
function longest_match(s, cur_match) {\n
  var chain_length = s.max_chain_length;      /* max hash chain length */\n
  var scan = s.strstart; /* current string */\n
  var match;                       /* matched string */\n
  var len;                           /* length of current match */\n
  var best_len = s.prev_length;              /* best match length so far */\n
  var nice_match = s.nice_match;             /* stop if match long enough */\n
  var limit = (s.strstart > (s.w_size - MIN_LOOKAHEAD)) ?\n
      s.strstart - (s.w_size - MIN_LOOKAHEAD) : 0/*NIL*/;\n
\n
  var _win = s.window; // shortcut\n
\n
  var wmask = s.w_mask;\n
  var prev  = s.prev;\n
\n
  /* Stop when cur_match becomes <= limit. To simplify the code,\n
   * we prevent matches with the string of window index 0.\n
   */\n
\n
  var strend = s.strstart + MAX_MATCH;\n
  var scan_end1  = _win[scan + best_len - 1];\n
  var scan_end   = _win[scan + best_len];\n
\n
  /* The code is optimized for HASH_BITS >= 8 and MAX_MATCH-2 multiple of 16.\n
   * It is easy to get rid of this optimization if necessary.\n
   */\n
  // Assert(s->hash_bits >= 8 && MAX_MATCH == 258, "Code too clever");\n
\n
  /* Do not waste too much time if we already have a good match: */\n
  if (s.prev_length >= s.good_match) {\n
    chain_length >>= 2;\n
  }\n
  /* Do not look for matches beyond the end of the input. This is necessary\n
   * to make deflate deterministic.\n
   */\n
  if (nice_match > s.lookahead) { nice_match = s.lookahead; }\n
\n
  // Assert((ulg)s->strstart <= s->window_size-MIN_LOOKAHEAD, "need lookahead");\n
\n
  do {\n
    // Assert(cur_match < s->strstart, "no future");\n
    match = cur_match;\n
\n
    /* Skip to next match if the match length cannot increase\n
     * or if the match length is less than 2.  Note that the checks below\n
     * for insufficient lookahead only occur occasionally for performance\n
     * reasons.  Therefore uninitialized memory will be accessed, and\n
     * conditional jumps will be made that depend on those values.\n
     * However the length of the match is limited to the lookahead, so\n
     * the output of deflate is not affected by the uninitialized values.\n
     */\n
\n
    if (_win[match + best_len]     !== scan_end  ||\n
        _win[match + best_len - 1] !== scan_end1 ||\n
        _win[match]                !== _win[scan] ||\n
        _win[++match]              !== _win[scan + 1]) {\n
      continue;\n
    }\n
\n
    /* The check at best_len-1 can be removed because it will be made\n
     * again later. (This heuristic is not always a win.)\n
     * It is not necessary to compare scan[2] and match[2] since they\n
     * are always equal when the other bytes match, given that\n
     * the hash keys are equal and that HASH_BITS >= 8.\n
     */\n
    scan += 2;\n
    match++;\n
    // Assert(*scan == *match, "match[2]?");\n
\n
    /* We check for insufficient lookahead only every 8th comparison;\n
     * the 256th check will be made at strstart+258.\n
     */\n
    do {\n
      /*jshint noempty:false*/\n
    } while (_win[++scan] === _win[++match] && _win[++scan] === _win[++match] &&\n
             _win[++scan] === _win[++match] && _win[++scan] === _win[++match] &&\n
             _win[++scan] === _win[++match] && _win[++scan] === _win[++match] &&\n
             _win[++scan] === _win[++match] && _win[++scan] === _win[++match] &&\n
             scan < strend);\n
\n
    // Assert(scan <= s->window+(unsigned)(s->window_size-1), "wild scan");\n
\n
    len = MAX_MATCH - (strend - scan);\n
    scan = strend - MAX_MATCH;\n
\n
    if (len > best_len) {\n
      s.match_start = cur_match;\n
      best_len = len;\n
      if (len >= nice_match) {\n
        break;\n
      }\n
      scan_end1  = _win[scan + best_len - 1];\n
      scan_end   = _win[scan + best_len];\n
    }\n
  } while ((cur_match = prev[cur_match & wmask]) > limit && --chain_length !== 0);\n
\n
  if (best_len <= s.lookahead) {\n
    return best_len;\n
  }\n
  return s.lookahead;\n
}\n
\n
\n
/* ===========================================================================\n
 * Fill the window when the lookahead becomes insufficient.\n
 * Updates strstart and lookahead.\n
 *\n
 * IN assertion: lookahead < MIN_LOOKAHEAD\n
 * OUT assertions: strstart <= window_size-MIN_LOOKAHEAD\n
 *    At least one byte has been read, or avail_in == 0; reads are\n
 *    performed for at least two bytes (required for the zip translate_eol\n
 *    option -- not supported here).\n
 */\n
function fill_window(s) {\n
  var _w_size = s.w_size;\n
  var p, n, m, more, str;\n
\n
  //Assert(s->lookahead < MIN_LOOKAHEAD, "already enough lookahead");\n
\n
  do {\n
    more = s.window_size - s.lookahead - s.strstart;\n
\n
    // JS ints have 32 bit, block below not needed\n
    /* Deal with !@#$% 64K limit: */\n
    //if (sizeof(int) <= 2) {\n
    //    if (more == 0 && s->strstart == 0 && s->lookahead == 0) {\n
    //        more = wsize;\n
    //\n
    //  } else if (more == (unsigned)(-1)) {\n
    //        /* Very unlikely, but possible on 16 bit machine if\n
    //         * strstart == 0 && lookahead == 1 (input done a byte at time)\n
    //         */\n
    //        more--;\n
    //    }\n
    //}\n
\n
\n
    /* If the window is almost full and there is insufficient lookahead,\n
     * move the upper half to the lower one to make room in the upper half.\n
     */\n
    if (s.strstart >= _w_size + (_w_size - MIN_LOOKAHEAD)) {\n
\n
      utils.arraySet(s.window, s.window, _w_size, _w_size, 0);\n
      s.match_start -= _w_size;\n
      s.strstart -= _w_size;\n
      /* we now have strstart >= MAX_DIST */\n
      s.block_start -= _w_size;\n
\n
      /* Slide the hash table (could be avoided with 32 bit values\n
       at the expense of memory usage). We slide even when level == 0\n
       to keep the hash table consistent if we switch back to level > 0\n
       later. (Using level 0 permanently is not an optimal usage of\n
       zlib, so we don\'t care about this pathological case.)\n
       */\n
\n
      n = s.hash_size;\n
      p = n;\n
      do {\n
        m = s.head[--p];\n
        s.head[p] = (m >= _w_size ? m - _w_size : 0);\n
      } while (--n);\n
\n
      n = _w_size;\n
      p = n;\n
      do {\n
        m = s.prev[--p];\n
        s.prev[p] = (m >= _w_size ? m - _w_size : 0);\n
        /* If n is not on any hash chain, prev[n] is garbage but\n
         * its value will never be used.\n
         */\n
      } while (--n);\n
\n
      more += _w_size;\n
    }\n
    if (s.strm.avail_in === 0) {\n
      break;\n
    }\n
\n
    /* If there was no sliding:\n
     *    strstart <= WSIZE+MAX_DIST-1 && lookahead <= MIN_LOOKAHEAD - 1 &&\n
     *    more == window_size - lookahead - strstart\n
     * => more >= window_size - (MIN_LOOKAHEAD-1 + WSIZE + MAX_DIST-1)\n
     * => more >= window_size - 2*WSIZE + 2\n
     * In the BIG_MEM or MMAP case (not yet supported),\n
     *   window_size == input_size + MIN_LOOKAHEAD  &&\n
     *   strstart + s->lookahead <= input_size => more >= MIN_LOOKAHEAD.\n
     * Otherwise, window_size == 2*WSIZE so more >= 2.\n
     * If there was sliding, more >= WSIZE. So in all cases, more >= 2.\n
     */\n
    //Assert(more >= 2, "more < 2");\n
    n = read_buf(s.strm, s.window, s.strstart + s.lookahead, more);\n
    s.lookahead += n;\n
\n
    /* Initialize the hash value now that we have some input: */\n
    if (s.lookahead + s.insert >= MIN_MATCH) {\n
      str = s.strstart - s.insert;\n
      s.ins_h = s.window[str];\n
\n
      /* UPDATE_HASH(s, s->ins_h, s->window[str + 1]); */\n
      s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[str + 1]) & s.hash_mask;\n
//#if MIN_MATCH != 3\n
//        Call update_hash() MIN_MATCH-3 more times\n
//#endif\n
      while (s.insert) {\n
        /* UPDATE_HASH(s, s->ins_h, s->window[str + MIN_MATCH-1]); */\n
        s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[str + MIN_MATCH-1]) & s.hash_mask;\n
\n
        s.prev[str & s.w_mask] = s.head[s.ins_h];\n
        s.head[s.ins_h] = str;\n
        str++;\n
        s.insert--;\n
        if (s.lookahead + s.insert < MIN_MATCH) {\n
          break;\n
        }\n
      }\n
    }\n
    /* If the whole input has less than MIN_MATCH bytes, ins_h is garbage,\n
     * but this is not important since only literal bytes will be emitted.\n
     */\n
\n
  } while (s.lookahead < MIN_LOOKAHEAD && s.strm.avail_in !== 0);\n
\n
  /* If the WIN_INIT bytes after the end of the current data have never been\n
   * written, then zero those bytes in order to avoid memory check reports of\n
   * the use of uninitialized (or uninitialised as Julian writes) bytes by\n
   * the longest match routines.  Update the high water mark for the next\n
   * time through here.  WIN_INIT is set to MAX_MATCH since the longest match\n
   * routines allow scanning to strstart + MAX_MATCH, ignoring lookahead.\n
   */\n
//  if (s.high_water < s.window_size) {\n
//    var curr = s.strstart + s.lookahead;\n
//    var init = 0;\n
//\n
//    if (s.high_water < curr) {\n
//      /* Previous high water mark below current data -- zero WIN_INIT\n
//       * bytes or up to end of window, whichever is less.\n
//       */\n
//      init = s.window_size - curr;\n
//      if (init > WIN_INIT)\n
//        init = WIN_INIT;\n
//      zmemzero(s->window + curr, (unsigned)init);\n
//      s->high_water = curr + init;\n
//    }\n
//    else if (s->high_water < (ulg)curr + WIN_INIT) {\n
//      /* High water mark at or above current data, but below current data\n
//       * plus WIN_INIT -- zero out to current data plus WIN_INIT, or up\n
//       * to end of window, whichever is less.\n
//       */\n
//      init = (ulg)curr + WIN_INIT - s->high_water;\n
//      if (init > s->window_size - s->high_water)\n
//        init = s->window_size - s->high_water;\n
//      zmemzero(s->window + s->high_water, (unsigned)init);\n
//      s->high_water += init;\n
//    }\n
//  }\n
//\n
//  Assert((ulg)s->strstart <= s->window_size - MIN_LOOKAHEAD,\n
//    "not enough room for search");\n
}\n
\n
/* ===========================================================================\n
 * Copy without compression as much as possible from the input stream, return\n
 * the current block state.\n
 * This function does not insert new strings in the dictionary since\n
 * uncompressible data is probably not useful. This function is used\n
 * only for the level=0 compression option.\n
 * NOTE: this function should be optimized to avoid extra copying from\n
 * window to pending_buf.\n
 */\n
function deflate_stored(s, flush) {\n
  /* Stored blocks are limited to 0xffff bytes, pending_buf is limited\n
   * to pending_buf_size, and each stored block has a 5 byte header:\n
   */\n
  var max_block_size = 0xffff;\n
\n
  if (max_block_size > s.pending_buf_size - 5) {\n
    max_block_size = s.pending_buf_size - 5;\n
  }\n
\n
  /* Copy as much as possible from input to output: */\n
  for (;;) {\n
    /* Fill the window as much as possible: */\n
    if (s.lookahead <= 1) {\n
\n
      //Assert(s->strstart < s->w_size+MAX_DIST(s) ||\n
      //  s->block_start >= (long)s->w_size, "slide too late");\n
//      if (!(s.strstart < s.w_size + (s.w_size - MIN_LOOKAHEAD) ||\n
//        s.block_start >= s.w_size)) {\n
//        throw  new Error("slide too late");\n
//      }\n
\n
      fill_window(s);\n
      if (s.lookahead === 0 && flush === Z_NO_FLUSH) {\n
        return BS_NEED_MORE;\n
      }\n
\n
      if (s.lookahead === 0) {\n
        break;\n
      }\n
      /* flush the current block */\n
    }\n
    //Assert(s->block_start >= 0L, "block gone");\n
//    if (s.block_start < 0) throw new Error("block gone");\n
\n
    s.strstart += s.lookahead;\n
    s.lookahead = 0;\n
\n
    /* Emit a stored block if pending_buf will be full: */\n
    var max_start = s.block_start + max_block_size;\n
\n
    if (s.strstart === 0 || s.strstart >= max_start) {\n
      /* strstart == 0 is possible when wraparound on 16-bit machine */\n
      s.lookahead = s.strstart - max_start;\n
      s.strstart = max_start;\n
      /*** FLUSH_BLOCK(s, 0); ***/\n
      flush_block_only(s, false);\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
      /***/\n
\n
\n
    }\n
    /* Flush if we may have to slide, otherwise block_start may become\n
     * negative and the data will be gone:\n
     */\n
    if (s.strstart - s.block_start >= (s.w_size - MIN_LOOKAHEAD)) {\n
      /*** FLUSH_BLOCK(s, 0); ***/\n
      flush_block_only(s, false);\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
      /***/\n
    }\n
  }\n
\n
  s.insert = 0;\n
\n
  if (flush === Z_FINISH) {\n
    /*** FLUSH_BLOCK(s, 1); ***/\n
    flush_block_only(s, true);\n
    if (s.strm.avail_out === 0) {\n
      return BS_FINISH_STARTED;\n
    }\n
    /***/\n
    return BS_FINISH_DONE;\n
  }\n
\n
  if (s.strstart > s.block_start) {\n
    /*** FLUSH_BLOCK(s, 0); ***/\n
    flush_block_only(s, false);\n
    if (s.strm.avail_out === 0) {\n
      return BS_NEED_MORE;\n
    }\n
    /***/\n
  }\n
\n
  return BS_NEED_MORE;\n
}\n
\n
/* ===========================================================================\n
 * Compress as much as possible from the input stream, return the current\n
 * block state.\n
 * This function does not perform lazy evaluation of matches and inserts\n
 * new strings in the dictionary only for unmatched strings or for short\n
 * matches. It is used only for the fast compression options.\n
 */\n
function deflate_fast(s, flush) {\n
  var hash_head;        /* head of the hash chain */\n
  var bflush;           /* set if current block must be flushed */\n
\n
  for (;;) {\n
    /* Make sure that we always have enough lookahead, except\n
     * at the end of the input file. We need MAX_MATCH bytes\n
     * for the next match, plus MIN_MATCH bytes to insert the\n
     * string following the next match.\n
     */\n
    if (s.lookahead < MIN_LOOKAHEAD) {\n
      fill_window(s);\n
      if (s.lookahead < MIN_LOOKAHEAD && flush === Z_NO_FLUSH) {\n
        return BS_NEED_MORE;\n
      }\n
      if (s.lookahead === 0) {\n
        break; /* flush the current block */\n
      }\n
    }\n
\n
    /* Insert the string window[strstart .. strstart+2] in the\n
     * dictionary, and set hash_head to the head of the hash chain:\n
     */\n
    hash_head = 0/*NIL*/;\n
    if (s.lookahead >= MIN_MATCH) {\n
      /*** INSERT_STRING(s, s.strstart, hash_head); ***/\n
      s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[s.strstart + MIN_MATCH - 1]) & s.hash_mask;\n
      hash_head = s.prev[s.strstart & s.w_mask] = s.head[s.ins_h];\n
      s.head[s.ins_h] = s.strstart;\n
      /***/\n
    }\n
\n
    /* Find the longest match, discarding those <= prev_length.\n
     * At this point we have always match_length < MIN_MATCH\n
     */\n
    if (hash_head !== 0/*NIL*/ && ((s.strstart - hash_head) <= (s.w_size - MIN_LOOKAHEAD))) {\n
      /* To simplify the code, we prevent matches with the string\n
       * of window index 0 (in particular we have to avoid a match\n
       * of the string with itself at the start of the input file).\n
       */\n
      s.match_length = longest_match(s, hash_head);\n
      /* longest_match() sets match_start */\n
    }\n
    if (s.match_length >= MIN_MATCH) {\n
      // check_match(s, s.strstart, s.match_start, s.match_length); // for debug only\n
\n
      /*** _tr_tally_dist(s, s.strstart - s.match_start,\n
                     s.match_length - MIN_MATCH, bflush); ***/\n
      bflush = trees._tr_tally(s, s.strstart - s.match_start, s.match_length - MIN_MATCH);\n
\n
      s.lookahead -= s.match_length;\n
\n
      /* Insert new strings in the hash table only if the match length\n
       * is not too large. This saves time but degrades compression.\n
       */\n
      if (s.match_length <= s.max_lazy_match/*max_insert_length*/ && s.lookahead >= MIN_MATCH) {\n
        s.match_length--; /* string at strstart already in table */\n
        do {\n
          s.strstart++;\n
          /*** INSERT_STRING(s, s.strstart, hash_head); ***/\n
          s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[s.strstart + MIN_MATCH - 1]) & s.hash_mask;\n
          hash_head = s.prev[s.strstart & s.w_mask] = s.head[s.ins_h];\n
          s.head[s.ins_h] = s.strstart;\n
          /***/\n
          /* strstart never exceeds WSIZE-MAX_MATCH, so there are\n
           * always MIN_MATCH bytes ahead.\n
           */\n
        } while (--s.match_length !== 0);\n
        s.strstart++;\n
      } else\n
      {\n
        s.strstart += s.match_length;\n
        s.match_length = 0;\n
        s.ins_h = s.window[s.strstart];\n
        /* UPDATE_HASH(s, s.ins_h, s.window[s.strstart+1]); */\n
        s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[s.strstart + 1]) & s.hash_mask;\n
\n
//#if MIN_MATCH != 3\n
//                Call UPDATE_HASH() MIN_MATCH-3 more times\n
//#endif\n
        /* If lookahead < MIN_MATCH, ins_h is garbage, but it does not\n
         * matter since it will be recomputed at next deflate call.\n
         */\n
      }\n
    } else {\n
      /* No match, output a literal byte */\n
      //Tracevv((stderr,"%c", s.window[s.strstart]));\n
      /*** _tr_tally_lit(s, s.window[s.strstart], bflush); ***/\n
      bflush = trees._tr_tally(s, 0, s.window[s.strstart]);\n
\n
      s.lookahead--;\n
      s.strstart++;\n
    }\n
    if (bflush) {\n
      /*** FLUSH_BLOCK(s, 0); ***/\n
      flush_block_only(s, false);\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
      /***/\n
    }\n
  }\n
  s.insert = ((s.strstart < (MIN_MATCH-1)) ? s.strstart : MIN_MATCH-1);\n
  if (flush === Z_FINISH) {\n
    /*** FLUSH_BLOCK(s, 1); ***/\n
    flush_block_only(s, true);\n
    if (s.strm.avail_out === 0) {\n
      return BS_FINISH_STARTED;\n
    }\n
    /***/\n
    return BS_FINISH_DONE;\n
  }\n
  if (s.last_lit) {\n
    /*** FLUSH_BLOCK(s, 0); ***/\n
    flush_block_only(s, false);\n
    if (s.strm.avail_out === 0) {\n
      return BS_NEED_MORE;\n
    }\n
    /***/\n
  }\n
  return BS_BLOCK_DONE;\n
}\n
\n
/* ===========================================================================\n
 * Same as above, but achieves better compression. We use a lazy\n
 * evaluation for matches: a match is finally adopted only if there is\n
 * no better match at the next window position.\n
 */\n
function deflate_slow(s, flush) {\n
  var hash_head;          /* head of hash chain */\n
  var bflush;              /* set if current block must be flushed */\n
\n
  var max_insert;\n
\n
  /* Process the input block. */\n
  for (;;) {\n
    /* Make sure that we always have enough lookahead, except\n
     * at the end of the input file. We need MAX_MATCH bytes\n
     * for the next match, plus MIN_MATCH bytes to insert the\n
     * string following the next match.\n
     */\n
    if (s.lookahead < MIN_LOOKAHEAD) {\n
      fill_window(s);\n
      if (s.lookahead < MIN_LOOKAHEAD && flush === Z_NO_FLUSH) {\n
        return BS_NEED_MORE;\n
      }\n
      if (s.lookahead === 0) { break; } /* flush the current block */\n
    }\n
\n
    /* Insert the string window[strstart .. strstart+2] in the\n
     * dictionary, and set hash_head to the head of the hash chain:\n
     */\n
    hash_head = 0/*NIL*/;\n
    if (s.lookahead >= MIN_MATCH) {\n
      /*** INSERT_STRING(s, s.strstart, hash_head); ***/\n
      s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[s.strstart + MIN_MATCH - 1]) & s.hash_mask;\n
      hash_head = s.prev[s.strstart & s.w_mask] = s.head[s.ins_h];\n
      s.head[s.ins_h] = s.strstart;\n
      /***/\n
    }\n
\n
    /* Find the longest match, discarding those <= prev_length.\n
     */\n
    s.prev_length = s.match_length;\n
    s.prev_match = s.match_start;\n
    s.match_length = MIN_MATCH-1;\n
\n
    if (hash_head !== 0/*NIL*/ && s.prev_length < s.max_lazy_match &&\n
        s.strstart - hash_head <= (s.w_size-MIN_LOOKAHEAD)/*MAX_DIST(s)*/) {\n
      /* To simplify the code, we prevent matches with the string\n
       * of window index 0 (in particular we have to avoid a match\n
       * of the string with itself at the start of the input file).\n
       */\n
      s.match_length = longest_match(s, hash_head);\n
      /* longest_match() sets match_start */\n
\n
      if (s.match_length <= 5 &&\n
         (s.strategy === Z_FILTERED || (s.match_length === MIN_MATCH && s.strstart - s.match_start > 4096/*TOO_FAR*/))) {\n
\n
        /* If prev_match is also MIN_MATCH, match_start is garbage\n
         * but we will ignore the current match anyway.\n
         */\n
        s.match_length = MIN_MATCH-1;\n
      }\n
    }\n
    /* If there was a match at the previous step and the current\n
     * match is not better, output the previous match:\n
     */\n
    if (s.prev_length >= MIN_MATCH && s.match_length <= s.prev_length) {\n
      max_insert = s.strstart + s.lookahead - MIN_MATCH;\n
      /* Do not insert strings in hash table beyond this. */\n
\n
      //check_match(s, s.strstart-1, s.prev_match, s.prev_length);\n
\n
      /***_tr_tally_dist(s, s.strstart - 1 - s.prev_match,\n
                     s.prev_length - MIN_MATCH, bflush);***/\n
      bflush = trees._tr_tally(s, s.strstart - 1- s.prev_match, s.prev_length - MIN_MATCH);\n
      /* Insert in hash table all strings up to the end of the match.\n
       * strstart-1 and strstart are already inserted. If there is not\n
       * enough lookahead, the last two strings are not inserted in\n
       * the hash table.\n
       */\n
      s.lookahead -= s.prev_length-1;\n
      s.prev_length -= 2;\n
      do {\n
        if (++s.strstart <= max_insert) {\n
          /*** INSERT_STRING(s, s.strstart, hash_head); ***/\n
          s.ins_h = ((s.ins_h << s.hash_shift) ^ s.window[s.strstart + MIN_MATCH - 1]) & s.hash_mask;\n
          hash_head = s.prev[s.strstart & s.w_mask] = s.head[s.ins_h];\n
          s.head[s.ins_h] = s.strstart;\n
          /***/\n
        }\n
      } while (--s.prev_length !== 0);\n
      s.match_available = 0;\n
      s.match_length = MIN_MATCH-1;\n
      s.strstart++;\n
\n
      if (bflush) {\n
        /*** FLUSH_BLOCK(s, 0); ***/\n
        flush_block_only(s, false);\n
        if (s.strm.avail_out === 0) {\n
          return BS_NEED_MORE;\n
        }\n
        /***/\n
      }\n
\n
    } else if (s.match_available) {\n
      /* If there was no match at the previous position, output a\n
       * single literal. If there was a match but the current match\n
       * is longer, truncate the previous match to a single literal.\n
       */\n
      //Tracevv((stderr,"%c", s->window[s->strstart-1]));\n
      /*** _tr_tally_lit(s, s.window[s.strstart-1], bflush); ***/\n
      bflush = trees._tr_tally(s, 0, s.window[s.strstart-1]);\n
\n
      if (bflush) {\n
        /*** FLUSH_BLOCK_ONLY(s, 0) ***/\n
        flush_block_only(s, false);\n
        /***/\n
      }\n
      s.strstart++;\n
      s.lookahead--;\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
    } else {\n
      /* There is no previous match to compare with, wait for\n
       * the next step to decide.\n
       */\n
      s.match_available = 1;\n
      s.strstart++;\n
      s.lookahead--;\n
    }\n
  }\n
  //Assert (flush != Z_NO_FLUSH, "no flush?");\n
  if (s.match_available) {\n
    //Tracevv((stderr,"%c", s->window[s->strstart-1]));\n
    /*** _tr_tally_lit(s, s.window[s.strstart-1], bflush); ***/\n
    bflush = trees._tr_tally(s, 0, s.window[s.strstart-1]);\n
\n
    s.match_available = 0;\n
  }\n
  s.insert = s.strstart < MIN_MATCH-1 ? s.strstart : MIN_MATCH-1;\n
  if (flush === Z_FINISH) {\n
    /*** FLUSH_BLOCK(s, 1); ***/\n
    flush_block_only(s, true);\n
    if (s.strm.avail_out === 0) {\n
      return BS_FINISH_STARTED;\n
    }\n
    /***/\n
    return BS_FINISH_DONE;\n
  }\n
  if (s.last_lit) {\n
    /*** FLUSH_BLOCK(s, 0); ***/\n
    flush_block_only(s, false);\n
    if (s.strm.avail_out === 0) {\n
      return BS_NEED_MORE;\n
    }\n
    /***/\n
  }\n
\n
  return BS_BLOCK_DONE;\n
}\n
\n
\n
/* ===========================================================================\n
 * For Z_RLE, simply look for runs of bytes, generate matches only of distance\n
 * one.  Do not maintain a hash table.  (It will be regenerated if this run of\n
 * deflate switches away from Z_RLE.)\n
 */\n
function deflate_rle(s, flush) {\n
  var bflush;            /* set if current block must be flushed */\n
  var prev;              /* byte at distance one to match */\n
  var scan, strend;      /* scan goes up to strend for length of run */\n
\n
  var _win = s.window;\n
\n
  for (;;) {\n
    /* Make sure that we always have enough lookahead, except\n
     * at the end of the input file. We need MAX_MATCH bytes\n
     * for the longest run, plus one for the unrolled loop.\n
     */\n
    if (s.lookahead <= MAX_MATCH) {\n
      fill_window(s);\n
      if (s.lookahead <= MAX_MATCH && flush === Z_NO_FLUSH) {\n
        return BS_NEED_MORE;\n
      }\n
      if (s.lookahead === 0) { break; } /* flush the current block */\n
    }\n
\n
    /* See how many times the previous byte repeats */\n
    s.match_length = 0;\n
    if (s.lookahead >= MIN_MATCH && s.strstart > 0) {\n
      scan = s.strstart - 1;\n
      prev = _win[scan];\n
      if (prev === _win[++scan] && prev === _win[++scan] && prev === _win[++scan]) {\n
        strend = s.strstart + MAX_MATCH;\n
        do {\n
          /*jshint noempty:false*/\n
        } while (prev === _win[++scan] && prev === _win[++scan] &&\n
                 prev === _win[++scan] && prev === _win[++scan] &&\n
                 prev === _win[++scan] && prev === _win[++scan] &&\n
                 prev === _win[++scan] && prev === _win[++scan] &&\n
                 scan < strend);\n
        s.match_length = MAX_MATCH - (strend - scan);\n
        if (s.match_length > s.lookahead) {\n
          s.match_length = s.lookahead;\n
        }\n
      }\n
      //Assert(scan <= s->window+(uInt)(s->window_size-1), "wild scan");\n
    }\n
\n
    /* Emit match if have run of MIN_MATCH or longer, else emit literal */\n
    if (s.match_length >= MIN_MATCH) {\n
      //check_match(s, s.strstart, s.strstart - 1, s.match_length);\n
\n
      /*** _tr_tally_dist(s, 1, s.match_length - MIN_MATCH, bflush); ***/\n
      bflush = trees._tr_tally(s, 1, s.match_length - MIN_MATCH);\n
\n
      s.lookahead -= s.match_length;\n
      s.strstart += s.match_length;\n
      s.match_length = 0;\n
    } else {\n
      /* No match, output a literal byte */\n
      //Tracevv((stderr,"%c", s->window[s->strstart]));\n
      /*** _tr_tally_lit(s, s.window[s.strstart], bflush); ***/\n
      bflush = trees._tr_tally(s, 0, s.window[s.strstart]);\n
\n
      s.lookahead--;\n
      s.strstart++;\n
    }\n
    if (bflush) {\n
      /*** FLUSH_BLOCK(s, 0); ***/\n
      flush_block_only(s, false);\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
      /***/\n
    }\n
  }\n
  s.insert = 0;\n
  if (flush === Z_FINISH) {\n
    /*** FLUSH_BLOCK(s, 1); ***/\n
    flush_block_only(s, true);\n
    if (s.strm.avail_out === 0) {\n
      return BS_FINISH_STARTED;\n
    }\n
    /***/\n
    return BS_FINISH_DONE;\n
  }\n
  if (s.last_lit) {\n
    /*** FLUSH_BLOCK(s, 0); ***/\n
    flush_block_only(s, false);\n
    if (s.strm.avail_out === 0) {\n
      return BS_NEED_MORE;\n
    }\n
    /***/\n
  }\n
  return BS_BLOCK_DONE;\n
}\n
\n
/* ===========================================================================\n
 * For Z_HUFFMAN_ONLY, do not look for matches.  Do not maintain a hash table.\n
 * (It will be regenerated if this run of deflate switches away from Huffman.)\n
 */\n
function deflate_huff(s, flush) {\n
  var bflush;             /* set if current block must be flushed */\n
\n
  for (;;) {\n
    /* Make sure that we have a literal to write. */\n
    if (s.lookahead === 0) {\n
      fill_window(s);\n
      if (s.lookahead === 0) {\n
        if (flush === Z_NO_FLUSH) {\n
          return BS_NEED_MORE;\n
        }\n
        break;      /* flush the current block */\n
      }\n
    }\n
\n
    /* Output a literal byte */\n
    s.match_length = 0;\n
    //Tracevv((stderr,"%c", s->window[s->strstart]));\n
    /*** _tr_tally_lit(s, s.window[s.strstart], bflush); ***/\n
    bflush = trees._tr_tally(s, 0, s.window[s.strstart]);\n
    s.lookahead--;\n
    s.strstart++;\n
    if (bflush) {\n
      /*** FLUSH_BLOCK(s, 0); ***/\n
      flush_block_only(s, false);\n
      if (s.strm.avail_out === 0) {\n
        return BS_NEED_MORE;\n
      }\n
      /***/\n
    }\n
  }\n
  s.insert = 0;\n
  if (flush === Z_FINISH) {\n
    /*** FLUSH_BLOCK(s, 1); ***/\n
    flush_block_only(s, true);\n
    if (s.strm.avail_out === 0) {\n
      return BS_FINISH_STARTED;\n
    }\n
    /***/\n
    return BS_FINISH_DONE;\n
  }\n
  if (s.last_lit) {\n
    /*** FLUSH_BLOCK(s, 0); ***/\n
    flush_block_only(s, false);\n
    if (s.strm.avail_out === 0) {\n
      return BS_NEED_MORE;\n
    }\n
    /***/\n
  }\n
  return BS_BLOCK_DONE;\n
}\n
\n
/* Values for max_lazy_match, good_match and max_chain_length, depending on\n
 * the desired pack level (0..9). The values given below have been tuned to\n
 * exclude worst case performance for pathological files. Better values may be\n
 * found for specific files.\n
 */\n
var Config = function (good_length, max_lazy, nice_length, max_chain, func) {\n
  this.good_length = good_length;\n
  this.max_lazy = max_lazy;\n
  this.nice_length = nice_length;\n
  this.max_chain = max_chain;\n
  this.func = func;\n
};\n
\n
var configuration_table;\n
\n
configuration_table = [\n
  /*      good lazy nice chain */\n
  new Config(0, 0, 0, 0, deflate_stored),          /* 0 store only */\n
  new Config(4, 4, 8, 4, deflate_fast),            /* 1 max speed, no lazy matches */\n
  new Config(4, 5, 16, 8, deflate_fast),           /* 2 */\n
  new Config(4, 6, 32, 32, deflate_fast),          /* 3 */\n
\n
  new Config(4, 4, 16, 16, deflate_slow),          /* 4 lazy matches */\n
  new Config(8, 16, 32, 32, deflate_slow),         /* 5 */\n
  new Config(8, 16, 128, 128, deflate_slow),       /* 6 */\n
  new Config(8, 32, 128, 256, deflate_slow),       /* 7 */\n
  new Config(32, 128, 258, 1024, deflate_slow),    /* 8 */\n
  new Config(32, 258, 258, 4096, deflate_slow)     /* 9 max compression */\n
];\n
\n
\n
/* ===========================================================================\n
 * Initialize the "longest match" routines for a new zlib stream\n
 */\n
function lm_init(s) {\n
  s.window_size = 2 * s.w_size;\n
\n
  /*** CLEAR_HASH(s); ***/\n
  zero(s.head); // Fill with NIL (= 0);\n
\n
  /* Set the default configuration parameters:\n
   */\n
  s.max_lazy_match = configuration_table[s.level].max_lazy;\n
  s.good_match = configuration_table[s.level].good_length;\n
  s.nice_match = configuration_table[s.level].nice_length;\n
  s.max_chain_length = configuration_table[s.level].max_chain;\n
\n
  s.strstart = 0;\n
  s.block_start = 0;\n
  s.lookahead = 0;\n
  s.insert = 0;\n
  s.match_length = s.prev_length = MIN_MATCH - 1;\n
  s.match_available = 0;\n
  s.ins_h = 0;\n
}\n
\n
\n
function DeflateState() {\n
  this.strm = null;            /* pointer back to this zlib stream */\n
  this.status = 0;            /* as the name implies */\n
  this.pending_buf = null;      /* output still pending */\n
  this.pending_buf_size = 0;  /* size of pending_buf */\n
  this.pending_out = 0;       /* next pending byte to output to the stream */\n
  this.pending = 0;           /* nb of bytes in the pending buffer */\n
  this.wrap = 0;              /* bit 0 true for zlib, bit 1 true for gzip */\n
  this.gzhead = null;         /* gzip header information to write */\n
  this.gzindex = 0;           /* where in extra, name, or comment */\n
  this.method = Z_DEFLATED; /* can only be DEFLATED */\n
  this.last_flush = -1;   /* value of flush param for previous deflate call */\n
\n
  this.w_size = 0;  /* LZ77 window size (32K by default) */\n
  this.w_bits = 0;  /* log2(w_size)  (8..16) */\n
  this.w_mask = 0;  /* w_size - 1 */\n
\n
  this.window = null;\n
  /* Sliding window. Input bytes are read into the second half of the window,\n
   * and move to the first half later to keep a dictionary of at least wSize\n
   * bytes. With this organization, matches are limited to a distance of\n
   * wSize-MAX_MATCH bytes, but this ensures that IO is always\n
   * performed with a length multiple of the block size.\n
   */\n
\n
  this.window_size = 0;\n
  /* Actual size of window: 2*wSize, except when the user input buffer\n
   * is directly used as sliding window.\n
   */\n
\n
  this.prev = null;\n
  /* Link to older string with same hash index. To limit the size of this\n
   * array to 64K, this link is maintained only for the last 32K strings.\n
   * An index in this array is thus a window index modulo 32K.\n
   */\n
\n
  this.head = null;   /* Heads of the hash chains or NIL. */\n
\n
  this.ins_h = 0;       /* hash index of string to be inserted */\n
  this.hash_size = 0;   /* number of elements in hash table */\n
  this.hash_bits = 0;   /* log2(hash_size) */\n
  this.hash_mask = 0;   /* hash_size-1 */\n
\n
  this.hash_shift = 0;\n
  /* Number of bits by which ins_h must be shifted at each input\n
   * step. It must be such that after MIN_MATCH steps, the oldest\n
   * byte no longer takes part in the hash key, that is:\n
   *   hash_shift * MIN_MATCH >= hash_bits\n
   */\n
\n
  this.block_start = 0;\n
  /* Window position at the beginning of the current output block. Gets\n
   * negative when the window is moved backwards.\n
   */\n
\n
  this.match_length = 0;      /* length of best match */\n
  this.prev_match = 0;        /* previous match */\n
  this.match_available = 0;   /* se

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

t if previous match exists */\n
  this.strstart = 0;          /* start of string to insert */\n
  this.match_start = 0;       /* start of matching string */\n
  this.lookahead = 0;         /* number of valid bytes ahead in window */\n
\n
  this.prev_length = 0;\n
  /* Length of the best match at previous step. Matches not greater than this\n
   * are discarded. This is used in the lazy match evaluation.\n
   */\n
\n
  this.max_chain_length = 0;\n
  /* To speed up deflation, hash chains are never searched beyond this\n
   * length.  A higher limit improves compression ratio but degrades the\n
   * speed.\n
   */\n
\n
  this.max_lazy_match = 0;\n
  /* Attempt to find a better match only when the current match is strictly\n
   * smaller than this value. This mechanism is used only for compression\n
   * levels >= 4.\n
   */\n
  // That\'s alias to max_lazy_match, don\'t use directly\n
  //this.max_insert_length = 0;\n
  /* Insert new strings in the hash table only if the match length is not\n
   * greater than this length. This saves time but degrades compression.\n
   * max_insert_length is used only for compression levels <= 3.\n
   */\n
\n
  this.level = 0;     /* compression level (1..9) */\n
  this.strategy = 0;  /* favor or force Huffman coding*/\n
\n
  this.good_match = 0;\n
  /* Use a faster search when the previous match is longer than this */\n
\n
  this.nice_match = 0; /* Stop searching when current match exceeds this */\n
\n
              /* used by trees.c: */\n
\n
  /* Didn\'t use ct_data typedef below to suppress compiler warning */\n
\n
  // struct ct_data_s dyn_ltree[HEAP_SIZE];   /* literal and length tree */\n
  // struct ct_data_s dyn_dtree[2*D_CODES+1]; /* distance tree */\n
  // struct ct_data_s bl_tree[2*BL_CODES+1];  /* Huffman tree for bit lengths */\n
\n
  // Use flat array of DOUBLE size, with interleaved fata,\n
  // because JS does not support effective\n
  this.dyn_ltree  = new utils.Buf16(HEAP_SIZE * 2);\n
  this.dyn_dtree  = new utils.Buf16((2*D_CODES+1) * 2);\n
  this.bl_tree    = new utils.Buf16((2*BL_CODES+1) * 2);\n
  zero(this.dyn_ltree);\n
  zero(this.dyn_dtree);\n
  zero(this.bl_tree);\n
\n
  this.l_desc   = null;         /* desc. for literal tree */\n
  this.d_desc   = null;         /* desc. for distance tree */\n
  this.bl_desc  = null;         /* desc. for bit length tree */\n
\n
  //ush bl_count[MAX_BITS+1];\n
  this.bl_count = new utils.Buf16(MAX_BITS+1);\n
  /* number of codes at each bit length for an optimal tree */\n
\n
  //int heap[2*L_CODES+1];      /* heap used to build the Huffman trees */\n
  this.heap = new utils.Buf16(2*L_CODES+1);  /* heap used to build the Huffman trees */\n
  zero(this.heap);\n
\n
  this.heap_len = 0;               /* number of elements in the heap */\n
  this.heap_max = 0;               /* element of largest frequency */\n
  /* The sons of heap[n] are heap[2*n] and heap[2*n+1]. heap[0] is not used.\n
   * The same heap array is used to build all trees.\n
   */\n
\n
  this.depth = new utils.Buf16(2*L_CODES+1); //uch depth[2*L_CODES+1];\n
  zero(this.depth);\n
  /* Depth of each subtree used as tie breaker for trees of equal frequency\n
   */\n
\n
  this.l_buf = 0;          /* buffer index for literals or lengths */\n
\n
  this.lit_bufsize = 0;\n
  /* Size of match buffer for literals/lengths.  There are 4 reasons for\n
   * limiting lit_bufsize to 64K:\n
   *   - frequencies can be kept in 16 bit counters\n
   *   - if compression is not successful for the first block, all input\n
   *     data is still in the window so we can still emit a stored block even\n
   *     when input comes from standard input.  (This can also be done for\n
   *     all blocks if lit_bufsize is not greater than 32K.)\n
   *   - if compression is not successful for a file smaller than 64K, we can\n
   *     even emit a stored file instead of a stored block (saving 5 bytes).\n
   *     This is applicable only for zip (not gzip or zlib).\n
   *   - creating new Huffman trees less frequently may not provide fast\n
   *     adaptation to changes in the input data statistics. (Take for\n
   *     example a binary file with poorly compressible code followed by\n
   *     a highly compressible string table.) Smaller buffer sizes give\n
   *     fast adaptation but have of course the overhead of transmitting\n
   *     trees more frequently.\n
   *   - I can\'t count above 4\n
   */\n
\n
  this.last_lit = 0;      /* running index in l_buf */\n
\n
  this.d_buf = 0;\n
  /* Buffer index for distances. To simplify the code, d_buf and l_buf have\n
   * the same number of elements. To use different lengths, an extra flag\n
   * array would be necessary.\n
   */\n
\n
  this.opt_len = 0;       /* bit length of current block with optimal trees */\n
  this.static_len = 0;    /* bit length of current block with static trees */\n
  this.matches = 0;       /* number of string matches in current block */\n
  this.insert = 0;        /* bytes at end of window left to insert */\n
\n
\n
  this.bi_buf = 0;\n
  /* Output buffer. bits are inserted starting at the bottom (least\n
   * significant bits).\n
   */\n
  this.bi_valid = 0;\n
  /* Number of valid bits in bi_buf.  All bits above the last valid bit\n
   * are always zero.\n
   */\n
\n
  // Used for window memory init. We safely ignore it for JS. That makes\n
  // sense only for pointers and memory check tools.\n
  //this.high_water = 0;\n
  /* High water mark offset in window for initialized bytes -- bytes above\n
   * this are set to zero in order to avoid memory check warnings when\n
   * longest match routines access bytes past the input.  This is then\n
   * updated to the new high water mark.\n
   */\n
}\n
\n
\n
function deflateResetKeep(strm) {\n
  var s;\n
\n
  if (!strm || !strm.state) {\n
    return err(strm, Z_STREAM_ERROR);\n
  }\n
\n
  strm.total_in = strm.total_out = 0;\n
  strm.data_type = Z_UNKNOWN;\n
\n
  s = strm.state;\n
  s.pending = 0;\n
  s.pending_out = 0;\n
\n
  if (s.wrap < 0) {\n
    s.wrap = -s.wrap;\n
    /* was made negative by deflate(..., Z_FINISH); */\n
  }\n
  s.status = (s.wrap ? INIT_STATE : BUSY_STATE);\n
  strm.adler = (s.wrap === 2) ?\n
    0  // crc32(0, Z_NULL, 0)\n
  :\n
    1; // adler32(0, Z_NULL, 0)\n
  s.last_flush = Z_NO_FLUSH;\n
  trees._tr_init(s);\n
  return Z_OK;\n
}\n
\n
\n
function deflateReset(strm) {\n
  var ret = deflateResetKeep(strm);\n
  if (ret === Z_OK) {\n
    lm_init(strm.state);\n
  }\n
  return ret;\n
}\n
\n
\n
function deflateSetHeader(strm, head) {\n
  if (!strm || !strm.state) { return Z_STREAM_ERROR; }\n
  if (strm.state.wrap !== 2) { return Z_STREAM_ERROR; }\n
  strm.state.gzhead = head;\n
  return Z_OK;\n
}\n
\n
\n
function deflateInit2(strm, level, method, windowBits, memLevel, strategy) {\n
  if (!strm) { // === Z_NULL\n
    return Z_STREAM_ERROR;\n
  }\n
  var wrap = 1;\n
\n
  if (level === Z_DEFAULT_COMPRESSION) {\n
    level = 6;\n
  }\n
\n
  if (windowBits < 0) { /* suppress zlib wrapper */\n
    wrap = 0;\n
    windowBits = -windowBits;\n
  }\n
\n
  else if (windowBits > 15) {\n
    wrap = 2;           /* write gzip wrapper instead */\n
    windowBits -= 16;\n
  }\n
\n
\n
  if (memLevel < 1 || memLevel > MAX_MEM_LEVEL || method !== Z_DEFLATED ||\n
    windowBits < 8 || windowBits > 15 || level < 0 || level > 9 ||\n
    strategy < 0 || strategy > Z_FIXED) {\n
    return err(strm, Z_STREAM_ERROR);\n
  }\n
\n
\n
  if (windowBits === 8) {\n
    windowBits = 9;\n
  }\n
  /* until 256-byte window bug fixed */\n
\n
  var s = new DeflateState();\n
\n
  strm.state = s;\n
  s.strm = strm;\n
\n
  s.wrap = wrap;\n
  s.gzhead = null;\n
  s.w_bits = windowBits;\n
  s.w_size = 1 << s.w_bits;\n
  s.w_mask = s.w_size - 1;\n
\n
  s.hash_bits = memLevel + 7;\n
  s.hash_size = 1 << s.hash_bits;\n
  s.hash_mask = s.hash_size - 1;\n
  s.hash_shift = ~~((s.hash_bits + MIN_MATCH - 1) / MIN_MATCH);\n
\n
  s.window = new utils.Buf8(s.w_size * 2);\n
  s.head = new utils.Buf16(s.hash_size);\n
  s.prev = new utils.Buf16(s.w_size);\n
\n
  // Don\'t need mem init magic for JS.\n
  //s.high_water = 0;  /* nothing written to s->window yet */\n
\n
  s.lit_bufsize = 1 << (memLevel + 6); /* 16K elements by default */\n
\n
  s.pending_buf_size = s.lit_bufsize * 4;\n
  s.pending_buf = new utils.Buf8(s.pending_buf_size);\n
\n
  s.d_buf = s.lit_bufsize >> 1;\n
  s.l_buf = (1 + 2) * s.lit_bufsize;\n
\n
  s.level = level;\n
  s.strategy = strategy;\n
  s.method = method;\n
\n
  return deflateReset(strm);\n
}\n
\n
function deflateInit(strm, level) {\n
  return deflateInit2(strm, level, Z_DEFLATED, MAX_WBITS, DEF_MEM_LEVEL, Z_DEFAULT_STRATEGY);\n
}\n
\n
\n
function deflate(strm, flush) {\n
  var old_flush, s;\n
  var beg, val; // for gzip header write only\n
\n
  if (!strm || !strm.state ||\n
    flush > Z_BLOCK || flush < 0) {\n
    return strm ? err(strm, Z_STREAM_ERROR) : Z_STREAM_ERROR;\n
  }\n
\n
  s = strm.state;\n
\n
  if (!strm.output ||\n
      (!strm.input && strm.avail_in !== 0) ||\n
      (s.status === FINISH_STATE && flush !== Z_FINISH)) {\n
    return err(strm, (strm.avail_out === 0) ? Z_BUF_ERROR : Z_STREAM_ERROR);\n
  }\n
\n
  s.strm = strm; /* just in case */\n
  old_flush = s.last_flush;\n
  s.last_flush = flush;\n
\n
  /* Write the header */\n
  if (s.status === INIT_STATE) {\n
\n
    if (s.wrap === 2) { // GZIP header\n
      strm.adler = 0;  //crc32(0L, Z_NULL, 0);\n
      put_byte(s, 31);\n
      put_byte(s, 139);\n
      put_byte(s, 8);\n
      if (!s.gzhead) { // s->gzhead == Z_NULL\n
        put_byte(s, 0);\n
        put_byte(s, 0);\n
        put_byte(s, 0);\n
        put_byte(s, 0);\n
        put_byte(s, 0);\n
        put_byte(s, s.level === 9 ? 2 :\n
                    (s.strategy >= Z_HUFFMAN_ONLY || s.level < 2 ?\n
                     4 : 0));\n
        put_byte(s, OS_CODE);\n
        s.status = BUSY_STATE;\n
      }\n
      else {\n
        put_byte(s, (s.gzhead.text ? 1 : 0) +\n
                    (s.gzhead.hcrc ? 2 : 0) +\n
                    (!s.gzhead.extra ? 0 : 4) +\n
                    (!s.gzhead.name ? 0 : 8) +\n
                    (!s.gzhead.comment ? 0 : 16)\n
                );\n
        put_byte(s, s.gzhead.time & 0xff);\n
        put_byte(s, (s.gzhead.time >> 8) & 0xff);\n
        put_byte(s, (s.gzhead.time >> 16) & 0xff);\n
        put_byte(s, (s.gzhead.time >> 24) & 0xff);\n
        put_byte(s, s.level === 9 ? 2 :\n
                    (s.strategy >= Z_HUFFMAN_ONLY || s.level < 2 ?\n
                     4 : 0));\n
        put_byte(s, s.gzhead.os & 0xff);\n
        if (s.gzhead.extra && s.gzhead.extra.length) {\n
          put_byte(s, s.gzhead.extra.length & 0xff);\n
          put_byte(s, (s.gzhead.extra.length >> 8) & 0xff);\n
        }\n
        if (s.gzhead.hcrc) {\n
          strm.adler = crc32(strm.adler, s.pending_buf, s.pending, 0);\n
        }\n
        s.gzindex = 0;\n
        s.status = EXTRA_STATE;\n
      }\n
    }\n
    else // DEFLATE header\n
    {\n
      var header = (Z_DEFLATED + ((s.w_bits - 8) << 4)) << 8;\n
      var level_flags = -1;\n
\n
      if (s.strategy >= Z_HUFFMAN_ONLY || s.level < 2) {\n
        level_flags = 0;\n
      } else if (s.level < 6) {\n
        level_flags = 1;\n
      } else if (s.level === 6) {\n
        level_flags = 2;\n
      } else {\n
        level_flags = 3;\n
      }\n
      header |= (level_flags << 6);\n
      if (s.strstart !== 0) { header |= PRESET_DICT; }\n
      header += 31 - (header % 31);\n
\n
      s.status = BUSY_STATE;\n
      putShortMSB(s, header);\n
\n
      /* Save the adler32 of the preset dictionary: */\n
      if (s.strstart !== 0) {\n
        putShortMSB(s, strm.adler >>> 16);\n
        putShortMSB(s, strm.adler & 0xffff);\n
      }\n
      strm.adler = 1; // adler32(0L, Z_NULL, 0);\n
    }\n
  }\n
\n
//#ifdef GZIP\n
  if (s.status === EXTRA_STATE) {\n
    if (s.gzhead.extra/* != Z_NULL*/) {\n
      beg = s.pending;  /* start of bytes to update crc */\n
\n
      while (s.gzindex < (s.gzhead.extra.length & 0xffff)) {\n
        if (s.pending === s.pending_buf_size) {\n
          if (s.gzhead.hcrc && s.pending > beg) {\n
            strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
          }\n
          flush_pending(strm);\n
          beg = s.pending;\n
          if (s.pending === s.pending_buf_size) {\n
            break;\n
          }\n
        }\n
        put_byte(s, s.gzhead.extra[s.gzindex] & 0xff);\n
        s.gzindex++;\n
      }\n
      if (s.gzhead.hcrc && s.pending > beg) {\n
        strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
      }\n
      if (s.gzindex === s.gzhead.extra.length) {\n
        s.gzindex = 0;\n
        s.status = NAME_STATE;\n
      }\n
    }\n
    else {\n
      s.status = NAME_STATE;\n
    }\n
  }\n
  if (s.status === NAME_STATE) {\n
    if (s.gzhead.name/* != Z_NULL*/) {\n
      beg = s.pending;  /* start of bytes to update crc */\n
      //int val;\n
\n
      do {\n
        if (s.pending === s.pending_buf_size) {\n
          if (s.gzhead.hcrc && s.pending > beg) {\n
            strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
          }\n
          flush_pending(strm);\n
          beg = s.pending;\n
          if (s.pending === s.pending_buf_size) {\n
            val = 1;\n
            break;\n
          }\n
        }\n
        // JS specific: little magic to add zero terminator to end of string\n
        if (s.gzindex < s.gzhead.name.length) {\n
          val = s.gzhead.name.charCodeAt(s.gzindex++) & 0xff;\n
        } else {\n
          val = 0;\n
        }\n
        put_byte(s, val);\n
      } while (val !== 0);\n
\n
      if (s.gzhead.hcrc && s.pending > beg){\n
        strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
      }\n
      if (val === 0) {\n
        s.gzindex = 0;\n
        s.status = COMMENT_STATE;\n
      }\n
    }\n
    else {\n
      s.status = COMMENT_STATE;\n
    }\n
  }\n
  if (s.status === COMMENT_STATE) {\n
    if (s.gzhead.comment/* != Z_NULL*/) {\n
      beg = s.pending;  /* start of bytes to update crc */\n
      //int val;\n
\n
      do {\n
        if (s.pending === s.pending_buf_size) {\n
          if (s.gzhead.hcrc && s.pending > beg) {\n
            strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
          }\n
          flush_pending(strm);\n
          beg = s.pending;\n
          if (s.pending === s.pending_buf_size) {\n
            val = 1;\n
            break;\n
          }\n
        }\n
        // JS specific: little magic to add zero terminator to end of string\n
        if (s.gzindex < s.gzhead.comment.length) {\n
          val = s.gzhead.comment.charCodeAt(s.gzindex++) & 0xff;\n
        } else {\n
          val = 0;\n
        }\n
        put_byte(s, val);\n
      } while (val !== 0);\n
\n
      if (s.gzhead.hcrc && s.pending > beg) {\n
        strm.adler = crc32(strm.adler, s.pending_buf, s.pending - beg, beg);\n
      }\n
      if (val === 0) {\n
        s.status = HCRC_STATE;\n
      }\n
    }\n
    else {\n
      s.status = HCRC_STATE;\n
    }\n
  }\n
  if (s.status === HCRC_STATE) {\n
    if (s.gzhead.hcrc) {\n
      if (s.pending + 2 > s.pending_buf_size) {\n
        flush_pending(strm);\n
      }\n
      if (s.pending + 2 <= s.pending_buf_size) {\n
        put_byte(s, strm.adler & 0xff);\n
        put_byte(s, (strm.adler >> 8) & 0xff);\n
        strm.adler = 0; //crc32(0L, Z_NULL, 0);\n
        s.status = BUSY_STATE;\n
      }\n
    }\n
    else {\n
      s.status = BUSY_STATE;\n
    }\n
  }\n
//#endif\n
\n
  /* Flush as much pending output as possible */\n
  if (s.pending !== 0) {\n
    flush_pending(strm);\n
    if (strm.avail_out === 0) {\n
      /* Since avail_out is 0, deflate will be called again with\n
       * more output space, but possibly with both pending and\n
       * avail_in equal to zero. There won\'t be anything to do,\n
       * but this is not an error situation so make sure we\n
       * return OK instead of BUF_ERROR at next call of deflate:\n
       */\n
      s.last_flush = -1;\n
      return Z_OK;\n
    }\n
\n
    /* Make sure there is something to do and avoid duplicate consecutive\n
     * flushes. For repeated and useless calls with Z_FINISH, we keep\n
     * returning Z_STREAM_END instead of Z_BUF_ERROR.\n
     */\n
  } else if (strm.avail_in === 0 && rank(flush) <= rank(old_flush) &&\n
    flush !== Z_FINISH) {\n
    return err(strm, Z_BUF_ERROR);\n
  }\n
\n
  /* User must not provide more input after the first FINISH: */\n
  if (s.status === FINISH_STATE && strm.avail_in !== 0) {\n
    return err(strm, Z_BUF_ERROR);\n
  }\n
\n
  /* Start a new block or continue the current one.\n
   */\n
  if (strm.avail_in !== 0 || s.lookahead !== 0 ||\n
    (flush !== Z_NO_FLUSH && s.status !== FINISH_STATE)) {\n
    var bstate = (s.strategy === Z_HUFFMAN_ONLY) ? deflate_huff(s, flush) :\n
      (s.strategy === Z_RLE ? deflate_rle(s, flush) :\n
        configuration_table[s.level].func(s, flush));\n
\n
    if (bstate === BS_FINISH_STARTED || bstate === BS_FINISH_DONE) {\n
      s.status = FINISH_STATE;\n
    }\n
    if (bstate === BS_NEED_MORE || bstate === BS_FINISH_STARTED) {\n
      if (strm.avail_out === 0) {\n
        s.last_flush = -1;\n
        /* avoid BUF_ERROR next call, see above */\n
      }\n
      return Z_OK;\n
      /* If flush != Z_NO_FLUSH && avail_out == 0, the next call\n
       * of deflate should use the same flush parameter to make sure\n
       * that the flush is complete. So we don\'t have to output an\n
       * empty block here, this will be done at next call. This also\n
       * ensures that for a very small output buffer, we emit at most\n
       * one empty block.\n
       */\n
    }\n
    if (bstate === BS_BLOCK_DONE) {\n
      if (flush === Z_PARTIAL_FLUSH) {\n
        trees._tr_align(s);\n
      }\n
      else if (flush !== Z_BLOCK) { /* FULL_FLUSH or SYNC_FLUSH */\n
\n
        trees._tr_stored_block(s, 0, 0, false);\n
        /* For a full flush, this empty block will be recognized\n
         * as a special marker by inflate_sync().\n
         */\n
        if (flush === Z_FULL_FLUSH) {\n
          /*** CLEAR_HASH(s); ***/             /* forget history */\n
          zero(s.head); // Fill with NIL (= 0);\n
\n
          if (s.lookahead === 0) {\n
            s.strstart = 0;\n
            s.block_start = 0;\n
            s.insert = 0;\n
          }\n
        }\n
      }\n
      flush_pending(strm);\n
      if (strm.avail_out === 0) {\n
        s.last_flush = -1; /* avoid BUF_ERROR at next call, see above */\n
        return Z_OK;\n
      }\n
    }\n
  }\n
  //Assert(strm->avail_out > 0, "bug2");\n
  //if (strm.avail_out <= 0) { throw new Error("bug2");}\n
\n
  if (flush !== Z_FINISH) { return Z_OK; }\n
  if (s.wrap <= 0) { return Z_STREAM_END; }\n
\n
  /* Write the trailer */\n
  if (s.wrap === 2) {\n
    put_byte(s, strm.adler & 0xff);\n
    put_byte(s, (strm.adler >> 8) & 0xff);\n
    put_byte(s, (strm.adler >> 16) & 0xff);\n
    put_byte(s, (strm.adler >> 24) & 0xff);\n
    put_byte(s, strm.total_in & 0xff);\n
    put_byte(s, (strm.total_in >> 8) & 0xff);\n
    put_byte(s, (strm.total_in >> 16) & 0xff);\n
    put_byte(s, (strm.total_in >> 24) & 0xff);\n
  }\n
  else\n
  {\n
    putShortMSB(s, strm.adler >>> 16);\n
    putShortMSB(s, strm.adler & 0xffff);\n
  }\n
\n
  flush_pending(strm);\n
  /* If avail_out is zero, the application will call deflate again\n
   * to flush the rest.\n
   */\n
  if (s.wrap > 0) { s.wrap = -s.wrap; }\n
  /* write the trailer only once! */\n
  return s.pending !== 0 ? Z_OK : Z_STREAM_END;\n
}\n
\n
function deflateEnd(strm) {\n
  var status;\n
\n
  if (!strm/*== Z_NULL*/ || !strm.state/*== Z_NULL*/) {\n
    return Z_STREAM_ERROR;\n
  }\n
\n
  status = strm.state.status;\n
  if (status !== INIT_STATE &&\n
    status !== EXTRA_STATE &&\n
    status !== NAME_STATE &&\n
    status !== COMMENT_STATE &&\n
    status !== HCRC_STATE &&\n
    status !== BUSY_STATE &&\n
    status !== FINISH_STATE\n
  ) {\n
    return err(strm, Z_STREAM_ERROR);\n
  }\n
\n
  strm.state = null;\n
\n
  return status === BUSY_STATE ? err(strm, Z_DATA_ERROR) : Z_OK;\n
}\n
\n
/* =========================================================================\n
 * Copy the source state to the destination state\n
 */\n
//function deflateCopy(dest, source) {\n
//\n
//}\n
\n
exports.deflateInit = deflateInit;\n
exports.deflateInit2 = deflateInit2;\n
exports.deflateReset = deflateReset;\n
exports.deflateResetKeep = deflateResetKeep;\n
exports.deflateSetHeader = deflateSetHeader;\n
exports.deflate = deflate;\n
exports.deflateEnd = deflateEnd;\n
exports.deflateInfo = \'pako deflate (from Nodeca project)\';\n
\n
/* Not implemented\n
exports.deflateBound = deflateBound;\n
exports.deflateCopy = deflateCopy;\n
exports.deflateSetDictionary = deflateSetDictionary;\n
exports.deflateParams = deflateParams;\n
exports.deflatePending = deflatePending;\n
exports.deflatePrime = deflatePrime;\n
exports.deflateTune = deflateTune;\n
*/\n
},{"../utils/common":27,"./adler32":29,"./crc32":31,"./messages":37,"./trees":38}],33:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
function GZheader() {\n
  /* true if compressed data believed to be text */\n
  this.text       = 0;\n
  /* modification time */\n
  this.time       = 0;\n
  /* extra flags (not used when writing a gzip file) */\n
  this.xflags     = 0;\n
  /* operating system */\n
  this.os         = 0;\n
  /* pointer to extra field or Z_NULL if none */\n
  this.extra      = null;\n
  /* extra field length (valid if extra != Z_NULL) */\n
  this.extra_len  = 0; // Actually, we don\'t need it in JS,\n
                       // but leave for few code modifications\n
\n
  //\n
  // Setup limits is not necessary because in js we should not preallocate memory \n
  // for inflate use constant limit in 65536 bytes\n
  //\n
\n
  /* space at extra (only when reading header) */\n
  // this.extra_max  = 0;\n
  /* pointer to zero-terminated file name or Z_NULL */\n
  this.name       = \'\';\n
  /* space at name (only when reading header) */\n
  // this.name_max   = 0;\n
  /* pointer to zero-terminated comment or Z_NULL */\n
  this.comment    = \'\';\n
  /* space at comment (only when reading header) */\n
  // this.comm_max   = 0;\n
  /* true if there was or will be a header crc */\n
  this.hcrc       = 0;\n
  /* true when done reading gzip header (not used when writing a gzip file) */\n
  this.done       = false;\n
}\n
\n
module.exports = GZheader;\n
},{}],34:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
// See state defs from inflate.js\n
var BAD = 30;       /* got a data error -- remain here until reset */\n
var TYPE = 12;      /* i: waiting for type bits, including last-flag bit */\n
\n
/*\n
   Decode literal, length, and distance codes and write out the resulting\n
   literal and match bytes until either not enough input or output is\n
   available, an end-of-block is encountered, or a data error is encountered.\n
   When large enough input and output buffers are supplied to inflate(), for\n
   example, a 16K input buffer and a 64K output buffer, more than 95% of the\n
   inflate execution time is spent in this routine.\n
\n
   Entry assumptions:\n
\n
        state.mode === LEN\n
        strm.avail_in >= 6\n
        strm.avail_out >= 258\n
        start >= strm.avail_out\n
        state.bits < 8\n
\n
   On return, state.mode is one of:\n
\n
        LEN -- ran out of enough output space or enough available input\n
        TYPE -- reached end of block code, inflate() to interpret next block\n
        BAD -- error in block data\n
\n
   Notes:\n
\n
    - The maximum input bits used by a length/distance pair is 15 bits for the\n
      length code, 5 bits for the length extra, 15 bits for the distance code,\n
      and 13 bits for the distance extra.  This totals 48 bits, or six bytes.\n
      Therefore if strm.avail_in >= 6, then there is enough input to avoid\n
      checking for available input while decoding.\n
\n
    - The maximum bytes that a single length/distance pair can output is 258\n
      bytes, which is the maximum length that can be coded.  inflate_fast()\n
      requires strm.avail_out >= 258 for each loop to avoid checking for\n
      output space.\n
 */\n
module.exports = function inflate_fast(strm, start) {\n
  var state;\n
  var _in;                    /* local strm.input */\n
  var last;                   /* have enough input while in < last */\n
  var _out;                   /* local strm.output */\n
  var beg;                    /* inflate()\'s initial strm.output */\n
  var end;                    /* while out < end, enough space available */\n
//#ifdef INFLATE_STRICT\n
  var dmax;                   /* maximum distance from zlib header */\n
//#endif\n
  var wsize;                  /* window size or zero if not using window */\n
  var whave;                  /* valid bytes in the window */\n
  var wnext;                  /* window write index */\n
  var window;                 /* allocated sliding window, if wsize != 0 */\n
  var hold;                   /* local strm.hold */\n
  var bits;                   /* local strm.bits */\n
  var lcode;                  /* local strm.lencode */\n
  var dcode;                  /* local strm.distcode */\n
  var lmask;                  /* mask for first level of length codes */\n
  var dmask;                  /* mask for first level of distance codes */\n
  var here;                   /* retrieved table entry */\n
  var op;                     /* code bits, operation, extra bits, or */\n
                              /*  window position, window bytes to copy */\n
  var len;                    /* match length, unused bytes */\n
  var dist;                   /* match distance */\n
  var from;                   /* where to copy match from */\n
  var from_source;\n
\n
\n
  var input, output; // JS specific, because we have no pointers\n
\n
  /* copy state to local variables */\n
  state = strm.state;\n
  //here = state.here;\n
  _in = strm.next_in;\n
  input = strm.input;\n
  last = _in + (strm.avail_in - 5);\n
  _out = strm.next_out;\n
  output = strm.output;\n
  beg = _out - (start - strm.avail_out);\n
  end = _out + (strm.avail_out - 257);\n
//#ifdef INFLATE_STRICT\n
  dmax = state.dmax;\n
//#endif\n
  wsize = state.wsize;\n
  whave = state.whave;\n
  wnext = state.wnext;\n
  window = state.window;\n
  hold = state.hold;\n
  bits = state.bits;\n
  lcode = state.lencode;\n
  dcode = state.distcode;\n
  lmask = (1 << state.lenbits) - 1;\n
  dmask = (1 << state.distbits) - 1;\n
\n
\n
  /* decode literals and length/distances until end-of-block or not enough\n
     input data or output space */\n
\n
  top:\n
  do {\n
    if (bits < 15) {\n
      hold += input[_in++] << bits;\n
      bits += 8;\n
      hold += input[_in++] << bits;\n
      bits += 8;\n
    }\n
\n
    here = lcode[hold & lmask];\n
\n
    dolen:\n
    for (;;) { // Goto emulation\n
      op = here >>> 24/*here.bits*/;\n
      hold >>>= op;\n
      bits -= op;\n
      op = (here >>> 16) & 0xff/*here.op*/;\n
      if (op === 0) {                          /* literal */\n
        //Tracevv((stderr, here.val >= 0x20 && here.val < 0x7f ?\n
        //        "inflate:         literal \'%c\'\\n" :\n
        //        "inflate:         literal 0x%02x\\n", here.val));\n
        output[_out++] = here & 0xffff/*here.val*/;\n
      }\n
      else if (op & 16) {                     /* length base */\n
        len = here & 0xffff/*here.val*/;\n
        op &= 15;                           /* number of extra bits */\n
        if (op) {\n
          if (bits < op) {\n
            hold += input[_in++] << bits;\n
            bits += 8;\n
          }\n
          len += hold & ((1 << op) - 1);\n
          hold >>>= op;\n
          bits -= op;\n
        }\n
        //Tracevv((stderr, "inflate:         length %u\\n", len));\n
        if (bits < 15) {\n
          hold += input[_in++] << bits;\n
          bits += 8;\n
          hold += input[_in++] << bits;\n
          bits += 8;\n
        }\n
        here = dcode[hold & dmask];\n
\n
        dodist:\n
        for (;;) { // goto emulation\n
          op = here >>> 24/*here.bits*/;\n
          hold >>>= op;\n
          bits -= op;\n
          op = (here >>> 16) & 0xff/*here.op*/;\n
\n
          if (op & 16) {                      /* distance base */\n
            dist = here & 0xffff/*here.val*/;\n
            op &= 15;                       /* number of extra bits */\n
            if (bits < op) {\n
              hold += input[_in++] << bits;\n
              bits += 8;\n
              if (bits < op) {\n
                hold += input[_in++] << bits;\n
                bits += 8;\n
              }\n
            }\n
            dist += hold & ((1 << op) - 1);\n
//#ifdef INFLATE_STRICT\n
            if (dist > dmax) {\n
              strm.msg = \'invalid distance too far back\';\n
              state.mode = BAD;\n
              break top;\n
            }\n
//#endif\n
            hold >>>= op;\n
            bits -= op;\n
            //Tracevv((stderr, "inflate:         distance %u\\n", dist));\n
            op = _out - beg;                /* max distance in output */\n
            if (dist > op) {                /* see if copy from window */\n
              op = dist - op;               /* distance back in window */\n
              if (op > whave) {\n
                if (state.sane) {\n
                  strm.msg = \'invalid distance too far back\';\n
                  state.mode = BAD;\n
                  break top;\n
                }\n
\n
// (!) This block is disabled in zlib defailts,\n
// don\'t enable it for binary compatibility\n
//#ifdef INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR\n
//                if (len <= op - whave) {\n
//                  do {\n
//                    output[_out++] = 0;\n
//                  } while (--len);\n
//                  continue top;\n
//                }\n
//                len -= op - whave;\n
//                do {\n
//                  output[_out++] = 0;\n
//                } while (--op > whave);\n
//                if (op === 0) {\n
//                  from = _out - dist;\n
//                  do {\n
//                    output[_out++] = output[from++];\n
//                  } while (--len);\n
//                  continue top;\n
//                }\n
//#endif\n
              }\n
              from = 0; // window index\n
              from_source = window;\n
              if (wnext === 0) {           /* very common case */\n
                from += wsize - op;\n
                if (op < len) {         /* some from window */\n
                  len -= op;\n
                  do {\n
                    output[_out++] = window[from++];\n
                  } while (--op);\n
                  from = _out - dist;  /* rest from output */\n
                  from_source = output;\n
                }\n
              }\n
              else if (wnext < op) {      /* wrap around window */\n
                from += wsize + wnext - op;\n
                op -= wnext;\n
                if (op < len) {         /* some from end of window */\n
                  len -= op;\n
                  do {\n
                    output[_out++] = window[from++];\n
                  } while (--op);\n
                  from = 0;\n
                  if (wnext < len) {  /* some from start of window */\n
                    op = wnext;\n
                    len -= op;\n
                    do {\n
                      output[_out++] = window[from++];\n
                    } while (--op);\n
                    from = _out - dist;      /* rest from output */\n
                    from_source = output;\n
                  }\n
                }\n
              }\n
              else {                      /* contiguous in window */\n
                from += wnext - op;\n
                if (op < len) {         /* some from window */\n
                  len -= op;\n
                  do {\n
                    output[_out++] = window[from++];\n
                  } while (--op);\n
                  from = _out - dist;  /* rest from output */\n
                  from_source = output;\n
                }\n
              }\n
              while (len > 2) {\n
                output[_out++] = from_source[from++];\n
                output[_out++] = from_source[from++];\n
                output[_out++] = from_source[from++];\n
                len -= 3;\n
              }\n
              if (len) {\n
                output[_out++] = from_source[from++];\n
                if (len > 1) {\n
                  output[_out++] = from_source[from++];\n
                }\n
              }\n
            }\n
            else {\n
              from = _out - dist;          /* copy direct from output */\n
              do {                        /* minimum length is three */\n
                output[_out++] = output[from++];\n
                output[_out++] = output[from++];\n
                output[_out++] = output[from++];\n
                len -= 3;\n
              } while (len > 2);\n
              if (len) {\n
                output[_out++] = output[from++];\n
                if (len > 1) {\n
                  output[_out++] = output[from++];\n
                }\n
              }\n
            }\n
          }\n
          else if ((op & 64) === 0) {          /* 2nd level distance code */\n
            here = dcode[(here & 0xffff)/*here.val*/ + (hold & ((1 << op) - 1))];\n
            continue dodist;\n
          }\n
          else {\n
            strm.msg = \'invalid distance code\';\n
            state.mode = BAD;\n
            break top;\n
          }\n
\n
          break; // need to emulate goto via "continue"\n
        }\n
      }\n
      else if ((op & 64) === 0) {              /* 2nd level length code */\n
        here = lcode[(here & 0xffff)/*here.val*/ + (hold & ((1 << op) - 1))];\n
        continue dolen;\n
      }\n
      else if (op & 32) {                     /* end-of-block */\n
        //Tracevv((stderr, "inflate:         end of block\\n"));\n
        state.mode = TYPE;\n
        break top;\n
      }\n
      else {\n
        strm.msg = \'invalid literal/length code\';\n
        state.mode = BAD;\n
        break top;\n
      }\n
\n
      break; // need to emulate goto via "continue"\n
    }\n
  } while (_in < last && _out < end);\n
\n
  /* return unused bytes (on entry, bits < 8, so in won\'t go too far back) */\n
  len = bits >> 3;\n
  _in -= len;\n
  bits -= len << 3;\n
  hold &= (1 << bits) - 1;\n
\n
  /* update state and return */\n
  strm.next_in = _in;\n
  strm.next_out = _out;\n
  strm.avail_in = (_in < last ? 5 + (last - _in) : 5 - (_in - last));\n
  strm.avail_out = (_out < end ? 257 + (end - _out) : 257 - (_out - end));\n
  state.hold = hold;\n
  state.bits = bits;\n
  return;\n
};\n
\n
},{}],35:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var utils = _dereq_(\'../utils/common\');\n
var adler32 = _dereq_(\'./adler32\');\n
var crc32   = _dereq_(\'./crc32\');\n
var inflate_fast = _dereq_(\'./inffast\');\n
var inflate_table = _dereq_(\'./inftrees\');\n
\n
var CODES = 0;\n
var LENS = 1;\n
var DISTS = 2;\n
\n
/* Public constants ==========================================================*/\n
/* ===========================================================================*/\n
\n
\n
/* Allowed flush values; see deflate() and inflate() below for details */\n
//var Z_NO_FLUSH      = 0;\n
//var Z_PARTIAL_FLUSH = 1;\n
//var Z_SYNC_FLUSH    = 2;\n
//var Z_FULL_FLUSH    = 3;\n
var Z_FINISH        = 4;\n
var Z_BLOCK         = 5;\n
var Z_TREES         = 6;\n
\n
\n
/* Return codes for the compression/decompression functions. Negative values\n
 * are errors, positive values are used for special but normal events.\n
 */\n
var Z_OK            = 0;\n
var Z_STREAM_END    = 1;\n
var Z_NEED_DICT     = 2;\n
//var Z_ERRNO         = -1;\n
var Z_STREAM_ERROR  = -2;\n
var Z_DATA_ERROR    = -3;\n
var Z_MEM_ERROR     = -4;\n
var Z_BUF_ERROR     = -5;\n
//var Z_VERSION_ERROR = -6;\n
\n
/* The deflate compression method */\n
var Z_DEFLATED  = 8;\n
\n
\n
/* STATES ====================================================================*/\n
/* ===========================================================================*/\n
\n
\n
var    HEAD = 1;       /* i: waiting for magic header */\n
var    FLAGS = 2;      /* i: waiting for method and flags (gzip) */\n
var    TIME = 3;       /* i: waiting for modification time (gzip) */\n
var    OS = 4;         /* i: waiting for extra flags and operating system (gzip) */\n
var    EXLEN = 5;      /* i: waiting for extra length (gzip) */\n
var    EXTRA = 6;      /* i: waiting for extra bytes (gzip) */\n
var    NAME = 7;       /* i: waiting for end of file name (gzip) */\n
var    COMMENT = 8;    /* i: waiting for end of comment (gzip) */\n
var    HCRC = 9;       /* i: waiting for header crc (gzip) */\n
var    DICTID = 10;    /* i: waiting for dictionary check value */\n
var    DICT = 11;      /* waiting for inflateSetDictionary() call */\n
var        TYPE = 12;      /* i: waiting for type bits, including last-flag bit */\n
var        TYPEDO = 13;    /* i: same, but skip check to exit inflate on new block */\n
var        STORED = 14;    /* i: waiting for stored size (length and complement) */\n
var        COPY_ = 15;     /* i/o: same as COPY below, but only first time in */\n
var        COPY = 16;      /* i/o: waiting for input or output to copy stored block */\n
var        TABLE = 17;     /* i: waiting for dynamic block table lengths */\n
var        LENLENS = 18;   /* i: waiting for code length code lengths */\n
var        CODELENS = 19;  /* i: waiting for length/lit and distance code lengths */\n
var            LEN_ = 20;      /* i: same as LEN below, but only first time in */\n
var            LEN = 21;       /* i: waiting for length/lit/eob code */\n
var            LENEXT = 22;    /* i: waiting for length extra bits */\n
var            DIST = 23;      /* i: waiting for distance code */\n
var            DISTEXT = 24;   /* i: waiting for distance extra bits */\n
var            MATCH = 25;     /* o: waiting for output space to copy string */\n
var            LIT = 26;       /* o: waiting for output space to write literal */\n
var    CHECK = 27;     /* i: waiting for 32-bit check value */\n
var    LENGTH = 28;    /* i: waiting for 32-bit length (gzip) */\n
var    DONE = 29;      /* finished check, done -- remain here until reset */\n
var    BAD = 30;       /* got a data error -- remain here until reset */\n
var    MEM = 31;       /* got an inflate() memory error -- remain here until reset */\n
var    SYNC = 32;      /* looking for synchronization bytes to restart inflate() */\n
\n
/* ===========================================================================*/\n
\n
\n
\n
var ENOUGH_LENS = 852;\n
var ENOUGH_DISTS = 592;\n
//var ENOUGH =  (ENOUGH_LENS+ENOUGH_DISTS);\n
\n
var MAX_WBITS = 15;\n
/* 32K LZ77 window */\n
var DEF_WBITS = MAX_WBITS;\n
\n
\n
function ZSWAP32(q) {\n
  return  (((q >>> 24) & 0xff) +\n
          ((q >>> 8) & 0xff00) +\n
          ((q & 0xff00) << 8) +\n
          ((q & 0xff) << 24));\n
}\n
\n
\n
function InflateState() {\n
  this.mode = 0;             /* current inflate mode */\n
  this.last = false;          /* true if processing last block */\n
  this.wrap = 0;              /* bit 0 true for zlib, bit 1 true for gzip */\n
  this.havedict = false;      /* true if dictionary provided */\n
  this.flags = 0;             /* gzip header method and flags (0 if zlib) */\n
  this.dmax = 0;              /* zlib header max distance (INFLATE_STRICT) */\n
  this.check = 0;             /* protected copy of check value */\n
  this.total = 0;             /* protected copy of output count */\n
  // TODO: may be {}\n
  this.head = null;           /* where to save gzip header information */\n
\n
  /* sliding window */\n
  this.wbits = 0;             /* log base 2 of requested window size */\n
  this.wsize = 0;             /* window size or zero if not using window */\n
  this.whave = 0;             /* valid bytes in the window */\n
  this.wnext = 0;             /* window write index */\n
  this.window = null;         /* allocated sliding window, if needed */\n
\n
  /* bit accumulator */\n
  this.hold = 0;              /* input bit accumulator */\n
  this.bits = 0;              /* number of bits in "in" */\n
\n
  /* for string and stored block copying */\n
  this.length = 0;            /* literal or length of data to copy */\n
  this.offset = 0;            /* distance back to copy string from */\n
\n
  /* for table and code decoding */\n
  this.extra = 0;             /* extra bits needed */\n
\n
  /* fixed and dynamic code tables */\n
  this.lencode = null;          /* starting table for length/literal codes */\n
  this.distcode = null;         /* starting table for distance codes */\n
  this.lenbits = 0;           /* index bits for lencode */\n
  this.distbits = 0;          /* index bits for distcode */\n
\n
  /* dynamic table building */\n
  this.ncode = 0;             /* number of code length code lengths */\n
  this.nlen = 0;              /* number of length code lengths */\n
  this.ndist = 0;             /* number of distance code lengths */\n
  this.have = 0;              /* number of code lengths in lens[] */\n
  this.next = null;              /* next available space in codes[] */\n
\n
  this.lens = new utils.Buf16(320); /* temporary storage for code lengths */\n
  this.work = new utils.Buf16(288); /* work area for code table building */\n
\n
  /*\n
   because we don\'t have pointers in js, we use lencode and distcode directly\n
   as buffers so we don\'t need codes\n
  */\n
  //this.codes = new utils.Buf32(ENOUGH);       /* space for code tables */\n
  this.lendyn = null;              /* dynamic table for length/literal codes (JS specific) */\n
  this.distdyn = null;             /* dynamic table for distance codes (JS specific) */\n
  this.sane = 0;                   /* if false, allow invalid distance too far */\n
  this.back = 0;                   /* bits back of last unprocessed length/lit */\n
  this.was = 0;                    /* initial length of match */\n
}\n
\n
function inflateResetKeep(strm) {\n
  var state;\n
\n
  if (!strm || !strm.state) { return Z_STREAM_ERROR; }\n
  state = strm.state;\n
  strm.total_in = strm.total_out = state.total = 0;\n
  strm.msg = \'\'; /*Z_NULL*/\n
  if (state.wrap) {       /* to support ill-conceived Java test suite */\n
    strm.adler = state.wrap & 1;\n
  }\n
  state.mode = HEAD;\n
  state.last = 0;\n
  state.havedict = 0;\n
  state.dmax = 32768;\n
  state.head = null/*Z_NULL*/;\n
  state.hold = 0;\n
  state.bits = 0;\n
  //state.lencode = state.distcode = state.next = state.codes;\n
  state.lencode = state.lendyn = new utils.Buf32(ENOUGH_LENS);\n
  state.distcode = state.distdyn = new utils.Buf32(ENOUGH_DISTS);\n
\n
  state.sane = 1;\n
  state.back = -1;\n
  //Tracev((stderr, "inflate: reset\\n"));\n
  return Z_OK;\n
}\n
\n
function inflateReset(strm) {\n
  var state;\n
\n
  if (!strm || !strm.state) { return Z_STREAM_ERROR; }\n
  state = strm.state;\n
  state.wsize = 0;\n
  state.whave = 0;\n
  state.wnext = 0;\n
  return inflateResetKeep(strm);\n
\n
}\n
\n
function inflateReset2(strm, windowBits) {\n
  var wrap;\n
  var state;\n
\n
  /* get the state */\n
  if (!strm || !strm.state) { return Z_STREAM_ERROR; }\n
  state = strm.state;\n
\n
  /* extract wrap request from windowBits parameter */\n
  if (windowBits < 0) {\n
    wrap = 0;\n
    windowBits = -windowBits;\n
  }\n
  else {\n
    wrap = (windowBits >> 4) + 1;\n
    if (windowBits < 48) {\n
      windowBits &= 15;\n
    }\n
  }\n
\n
  /* set number of window bits, free window if different */\n
  if (windowBits && (windowBits < 8 || windowBits > 15)) {\n
    return Z_STREAM_ERROR;\n
  }\n
  if (state.window !== null && state.wbits !== windowBits) {\n
    state.window = null;\n
  }\n
\n
  /* update state and reset the rest of it */\n
  state.wrap = wrap;\n
  state.wbits = windowBits;\n
  return inflateReset(strm);\n
}\n
\n
function inflateInit2(strm, windowBits) {\n
  var ret;\n
  var state;\n
\n
  if (!strm) { return Z_STREAM_ERROR; }\n
  //strm.msg = Z_NULL;                 /* in case we return an error */\n
\n
  state = new InflateState();\n
\n
  //if (state === Z_NULL) return Z_MEM_ERROR;\n
  //Tracev((stderr, "inflate: allocated\\n"));\n
  strm.state = state;\n
  state.window = null/*Z_NULL*/;\n
  ret = inflateReset2(strm, windowBits);\n
  if (ret !== Z_OK) {\n
    strm.state = null/*Z_NULL*/;\n
  }\n
  return ret;\n
}\n
\n
function inflateInit(strm) {\n
  return inflateInit2(strm, DEF_WBITS);\n
}\n
\n
\n
/*\n
 Return state with length and distance decoding tables and index sizes set to\n
 fixed code decoding.  Normally this returns fixed tables from inffixed.h.\n
 If BUILDFIXED is defined, then instead this routine builds the tables the\n
 first time it\'s called, and returns those tables the first time and\n
 thereafter.  This reduces the size of the code by about 2K bytes, in\n
 exchange for a little execution time.  However, BUILDFIXED should not be\n
 used for threaded applications, since the rewriting of the tables and virgin\n
 may not be thread-safe.\n
 */\n
var virgin = true;\n
\n
var lenfix, distfix; // We have no pointers in JS, so keep tables separate\n
\n
function fixedtables(state) {\n
  /* build fixed huffman tables if first call (may not be thread safe) */\n
  if (virgin) {\n
    var sym;\n
\n
    lenfix = new utils.Buf32(512);\n
    distfix = new utils.Buf32(32);\n
\n
    /* literal/length table */\n
    sym = 0;\n
    while (sym < 144) { state.lens[sym++] = 8; }\n
    while (sym < 256) { state.lens[sym++] = 9; }\n
    while (sym < 280) { state.lens[sym++] = 7; }\n
    while (sym < 288) { state.lens[sym++] = 8; }\n
\n
    inflate_table(LENS,  state.lens, 0, 288, lenfix,   0, state.work, {bits: 9});\n
\n
    /* distance table */\n
    sym = 0;\n
    while (sym < 32) { state.lens[sym++] = 5; }\n
\n
    inflate_table(DISTS, state.lens, 0, 32,   distfix, 0, state.work, {bits: 5});\n
\n
    /* do this just once */\n
    virgin = false;\n
  }\n
\n
  state.lencode = lenfix;\n
  state.lenbits = 9;\n
  state.distcode = distfix;\n
  state.distbits = 5;\n
}\n
\n
\n
/*\n
 Update the window with the last wsize (normally 32K) bytes written before\n
 returning.  If window does not exist yet, create it.  This is only called\n
 when a window is already in use, or when output has been written during this\n
 inflate call, but the end of the deflate stream has not been reached yet.\n
 It is also called to create a window for dictionary data when a dictionary\n
 is loaded.\n
\n
 Providing output buffers larger than 32K to inflate() should provide a speed\n
 advantage, since only the last 32K of output is copied to the sliding window\n
 upon return from inflate(), and since all distances after the first 32K of\n
 output will fall in the output data, making match copies simpler and faster.\n
 The advantage may be dependent on the size of the processor\'s data caches.\n
 */\n
function updatewindow(strm, src, end, copy) {\n
  var dist;\n
  var state = strm.state;\n
\n
  /* if it hasn\'t been done already, allocate space for the window */\n
  if (state.window === null) {\n
    state.wsize = 1 << state.wbits;\n
    state.wnext = 0;\n
    state.whave = 0;\n
\n
    state.window = new utils.Buf8(state.wsize);\n
  }\n
\n
  /* copy state->wsize or less output bytes into the circular window */\n
  if (copy >= state.wsize) {\n
    utils.arraySet(state.window,src, end - state.wsize, state.wsize, 0);\n
    state.wnext = 0;\n
    state.whave = state.wsize;\n
  }\n
  else {\n
    dist = state.wsize - state.wnext;\n
    if (dist > copy) {\n
      dist = copy;\n
    }\n
    //zmemcpy(state->window + state->wnext, end - copy, dist);\n
    utils.arraySet(state.window,src, end - copy, dist, state.wnext);\n
    copy -= dist;\n
    if (copy) {\n
      //zmemcpy(state->window, end - copy, copy);\n
      utils.arraySet(state.window,src, end - copy, copy, 0);\n
      state.wnext = copy;\n
      state.whave = state.wsize;\n
    }\n
    else {\n
      state.wnext += dist;\n
      if (state.wnext === state.wsize) { state.wnext = 0; }\n
      if (state.whave < state.wsize) { state.whave += dist; }\n
    }\n
  }\n
  return 0;\n
}\n
\n
function inflate(strm, flush) {\n
  var state;\n
  var input, output;          // input/output buffers\n
  var next;                   /* next input INDEX */\n
  var put;                    /* next output INDEX */\n
  var have, left;             /* available input and output */\n
  var hold;                   /* bit buffer */\n
  var bits;                   /* bits in bit buffer */\n
  var _in, _out;              /* save starting available input and output */\n
  var copy;                   /* number of stored or match bytes to copy */\n
  var from;                   /* where to copy match bytes from */\n
  var from_source;\n
  var here = 0;               /* current decoding table entry */\n
  var here_bits, here_op, here_val; // paked "here" denormalized (JS specific)\n
  //var last;                   /* parent table entry */\n
  var last_bits, last_op, last_val; // paked "last" denormalized (JS specific)\n
  var len;                    /* length to copy for repeats, bits to drop */\n
  var ret;                    /* return code */\n
  var hbuf = new utils.Buf8(4);    /* buffer for gzip header crc calculation */\n
  var opts;\n
\n
  var n; // temporary var for NEED_BITS\n
\n
  var order = /* permutation of code lengths */\n
    [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];\n
\n
\n
  if (!strm || !strm.state || !strm.output ||\n
      (!strm.input && strm.avail_in !== 0)) {\n
    return Z_STREAM_ERROR;\n
  }\n
\n
  state = strm.state;\n
  if (state.mode === TYPE) { state.mode = TYPEDO; }    /* skip check */\n
\n
\n
  //--- LOAD() ---\n
  put = strm.next_out;\n
  output = strm.output;\n
  left = strm.avail_out;\n
  next = strm.next_in;\n
  input = strm.input;\n
  have = strm.avail_in;\n
  hold = state.hold;\n
  bits = state.bits;\n
  //---\n
\n
  _in = have;\n
  _out = left;\n
  ret = Z_OK;\n
\n
  inf_leave: // goto emulation\n
  for (;;) {\n
    switch (state.mode) {\n
    case HEAD:\n
      if (state.wrap === 0) {\n
        state.mode = TYPEDO;\n
        break;\n
      }\n
      //=== NEEDBITS(16);\n
      while (bits < 16) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      if ((state.wrap & 2) && hold === 0x8b1f) {  /* gzip header */\n
        state.check = 0/*crc32(0L, Z_NULL, 0)*/;\n
        //=== CRC2(state.check, hold);\n
        hbuf[0] = hold & 0xff;\n
        hbuf[1] = (hold >>> 8) & 0xff;\n
        state.check = crc32(state.check, hbuf, 2, 0);\n
        //===//\n
\n
        //=== INITBITS();\n
        hold = 0;\n
        bits = 0;\n
        //===//\n
        state.mode = FLAGS;\n
        break;\n
      }\n
      state.flags = 0;           /* expect zlib header */\n
      if (state.head) {\n
        state.head.done = false;\n
      }\n
      if (!(state.wrap & 1) ||   /* check if zlib header allowed */\n
        (((hold & 0xff)/*BITS(8)*/ << 8) + (hold >> 8)) % 31) {\n
        strm.msg = \'incorrect header check\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      if ((hold & 0x0f)/*BITS(4)*/ !== Z_DEFLATED) {\n
        strm.msg = \'unknown compression method\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      //--- DROPBITS(4) ---//\n
      hold >>>= 4;\n
      bits -= 4;\n
      //---//\n
      len = (hold & 0x0f)/*BITS(4)*/ + 8;\n
      if (state.wbits === 0) {\n
        state.wbits = len;\n
      }\n
      else if (len > state.wbits) {\n
        strm.msg = \'invalid window size\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      state.dmax = 1 << len;\n
      //Tracev((stderr, "inflate:   zlib header ok\\n"));\n
      strm.adler = state.check = 1/*adler32(0L, Z_NULL, 0)*/;\n
      state.mode = hold & 0x200 ? DICTID : TYPE;\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      break;\n
    case FLAGS:\n
      //=== NEEDBITS(16); */\n
      while (bits < 16) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      state.flags = hold;\n
      if ((state.flags & 0xff) !== Z_DEFLATED) {\n
        strm.msg = \'unknown compression method\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      if (state.flags & 0xe000) {\n
        strm.msg = \'unknown header flags set\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      if (state.head) {\n
        state.head.text = ((hold >> 8) & 1);\n
      }\n
      if (state.flags & 0x0200) {\n
        //=== CRC2(state.check, hold);\n
        hbuf[0] = hold & 0xff;\n
        hbuf[1] = (hold >>> 8) & 0xff;\n
        state.check = crc32(state.check, hbuf, 2, 0);\n
        //===//\n
      }\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      state.mode = TIME;\n
      /* falls through */\n
    case TIME:\n
      //=== NEEDBITS(32); */\n
      while (bits < 32) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      if (state.head) {\n
        state.head.time = hold;\n
      }\n
      if (state.flags & 0x0200) {\n
        //=== CRC4(state.check, hold)\n
        hbuf[0] = hold & 0xff;\n
        hbuf[1] = (hold >>> 8) & 0xff;\n
        hbuf[2] = (hold >>> 16) & 0xff;\n
        hbuf[3] = (hold >>> 24) & 0xff;\n
        state.check = crc32(state.check, hbuf, 4, 0);\n
        //===\n
      }\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      state.mode = OS;\n
      /* falls through */\n
    case OS:\n
      //=== NEEDBITS(16); */\n
      while (bits < 16) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      if (state.head) {\n
        state.head.xflags = (hold & 0xff);\n
        state.head.os = (hold >> 8);\n
      }\n
      if (state.flags & 0x0200) {\n
        //=== CRC2(state.check, hold);\n
        hbuf[0] = hold & 0xff;\n
        hbuf[1] = (hold >>> 8) & 0xff;\n
        state.check = crc32(state.check, hbuf, 2, 0);\n
        //===//\n
      }\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      state.mode = EXLEN;\n
      /* falls through */\n
    case EXLEN:\n
      if (state.flags & 0x0400) {\n
        //=== NEEDBITS(16); */\n
        while (bits < 16) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        state.length = hold;\n
        if (state.head) {\n
          state.head.extra_len = hold;\n
        }\n
        if (state.flags & 0x0200) {\n
          //=== CRC2(state.check, hold);\n
          hbuf[0] = hold & 0xff;\n
          hbuf[1] = (hold >>> 8) & 0xff;\n
          state.check = crc32(state.check, hbuf, 2, 0);\n
          //===//\n
        }\n
        //=== INITBITS();\n
        hold = 0;\n
        bits = 0;\n
        //===//\n
      }\n
      else if (state.head) {\n
        state.head.extra = null/*Z_NULL*/;\n
      }\n
      state.mode = EXTRA;\n
      /* falls through */\n
    case EXTRA:\n
      if (state.flags & 0x0400) {\n
        copy = state.length;\n
        if (copy > have) { copy = have; }\n
        if (copy) {\n
          if (state.head) {\n
            len = state.head.extra_len - state.length;\n
            if (!state.head.extra) {\n
              // Use untyped array for more conveniend processing later\n
              state.head.extra = new Array(state.head.extra_len);\n
            }\n
            utils.arraySet(\n
              state.head.extra,\n
              input,\n
              next,\n
              // extra field is limited to 65536 bytes\n
              // - no need for additional size check\n
              copy,\n
              /*len + copy > state.head.extra_max - len ? state.head.extra_max : copy,*/\n
              len\n
            );\n
            //zmemcpy(state.head.extra + len, next,\n
            //        len + copy > state.head.extra_max ?\n
            //        state.head.extra_max - len : copy);\n
          }\n
          if (state.flags & 0x0200) {\n
            state.check = crc32(state.check, input, copy, next);\n
          }\n
          have -= copy;\n
          next += copy;\n
          state.length -= copy;\n
        }\n
        if (state.length) { break inf_leave; }\n
      }\n
      state.length = 0;\n
      state.mode = NAME;\n
      /* falls through */\n
    case NAME:\n
      if (state.flags & 0x0800) {\n
        if (have === 0) { break inf_leave; }\n
        copy = 0;\n
        do {\n
          // TODO: 2 or 1 bytes?\n
          len = input[next + copy++];\n
          /* use constant limit because in js we should not preallocate memory */\n
          if (state.head && len &&\n
              (state.length < 65536 /*state.head.name_max*/)) {\n
            state.head.name += String.fromCharCode(len);\n
          }\n
        } while (len && copy < have);\n
\n
        if (state.flags & 0x0200) {\n
          state.check = crc32(state.check, input, copy, next);\n
        }\n
        have -= copy;\n
        next += copy;\n
        if (len) { break inf_leave; }\n
      }\n
      else if (state.head) {\n
        state.head.name = null;\n
      }\n
      state.length = 0;\n
      state.mode = COMMENT;\n
      /* falls through */\n
    case COMMENT:\n
      if (state.flags & 0x1000) {\n
        if (have === 0) { break inf_leave; }\n
        copy = 0;\n
        do {\n
          len = input[next + copy++];\n
          /* use constant limit because in js we should not preallocate memory */\n
          if (state.head && len &&\n
              (state.length < 65536 /*state.head.comm_max*/)) {\n
            state.head.comment += String.fromCharCode(len);\n
          }\n
        } while (len && copy < have);\n
        if (state.flags & 0x0200) {\n
          state.check = crc32(state.check, input, copy, next);\n
        }\n
        have -= copy;\n
        next += copy;\n
        if (len) { break inf_leave; }\n
      }\n
      else if (state.head) {\n
        state.head.comment = null;\n
      }\n
      state.mode = HCRC;\n
      /* falls through */\n
    case HCRC:\n
      if (state.flags & 0x0200) {\n
        //=== NEEDBITS(16); */\n
        while (bits < 16) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        if (hold !== (state.check & 0xffff)) {\n
          strm.msg = \'header crc mismatch\';\n
          state.mode = BAD;\n
          break;\n
        }\n
        //=== INITBITS();\n
        hold = 0;\n
        bits = 0;\n
        //===//\n
      }\n
      if (state.head) {\n
        state.head.hcrc = ((state.flags >> 9) & 1);\n
        state.head.done = true;\n
      }\n
      strm.adler = state.check = 0 /*crc32(0L, Z_NULL, 0)*/;\n
      state.mode = TYPE;\n
      break;\n
    case DICTID:\n
      //=== NEEDBITS(32); */\n
      while (bits < 32) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      strm.adler = state.check = ZSWAP32(hold);\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      state.mode = DICT;\n
      /* falls through */\n
    case DICT:\n
      if (state.havedict === 0) {\n
        //--- RESTORE() ---\n
        strm.next_out = put;\n
        strm.avail_out = left;\n
        strm.next_in = next;\n
        strm.avail_in = have;\n
        state.hold = hold;\n
        state.bits = bits;\n
        //---\n
        return Z_NEED_DICT;\n
      }\n
      strm.adler = state.check = 1/*adler32(0L, Z_NULL, 0)*/;\n
      state.mode = TYPE;\n
      /* falls through */\n
    case TYPE:\n
      if (flush === Z_BLOCK || flush === Z_TREES) { break inf_leave; }\n
      /* falls through */\n
    case TYPEDO:\n
      if (state.last) {\n
        //--- BYTEBITS() ---//\n
        hold >>>= bits & 7;\n
        bits -= bits & 7;\n
        //---//\n
        state.mode = CHECK;\n
        break;\n
      }\n
      //=== NEEDBITS(3); */\n
      while (bits < 3) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      state.last = (hold & 0x01)/*BITS(1)*/;\n
      //--- DROPBITS(1) ---//\n
      hold >>>= 1;\n
      bits -= 1;\n
      //---//\n
\n
      switch ((hold & 0x03)/*BITS(2)*/) {\n
      case 0:                             /* stored block */\n
        //Tracev((stderr, "inflate:     stored block%s\\n",\n
        //        state.last ? " (last)" : ""));\n
        state.mode = STORED;\n
        break;\n
      case 1:                             /* fixed block */\n
        fixedtables(state);\n
        //Tracev((stderr, "inflate:     fixed codes block%s\\n",\n
        //        state.last ? " (last)" : ""));\n
        state.mode = LEN_;             /* decode codes */\n
        if (flush === Z_TREES) {\n
          //--- DROPBITS(2) ---//\n
          hold >>>= 2;\n
          bits -= 2;\n
          //---//\n
          break inf_leave;\n
        }\n
        break;\n
      case 2:                             /* dynamic block */\n
        //Tracev((stderr, "inflate:     dynamic codes block%s\\n",\n
        //        state.last ? " (last)" : ""));\n
        state.mode = TABLE;\n
        break;\n
      case 3:\n
        strm.msg = \'invalid block type\';\n
        state.mode = BAD;\n
      }\n
      //--- DROPBITS(2) ---//\n
      hold >>>= 2;\n
      bits -= 2;\n
      //---//\n
      break;\n
    case STORED:\n
      //--- BYTEBITS() ---// /* go to byte boundary */\n
      hold >>>= bits & 7;\n
      bits -= bits & 7;\n
      //---//\n
      //=== NEEDBITS(32); */\n
      while (bits < 32) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      if ((hold & 0xffff) !== ((hold >>> 16) ^ 0xffff)) {\n
        strm.msg = \'invalid stored block lengths\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      state.length = hold & 0xffff;\n
      //Tracev((stderr, "inflate:       stored length %u\\n",\n
      //        state.length));\n
      //=== INITBITS();\n
      hold = 0;\n
      bits = 0;\n
      //===//\n
      state.mode = COPY_;\n
      if (flush === Z_TREES) { break inf_leave; }\n
      /* falls through */\n
    case COPY_:\n
      state.mode = COPY;\n
      /* falls through */\n
    case COPY:\n
      copy = state.length;\n
      if (copy) {\n
        if (copy > have) { copy = have; }\n
        if (copy > left) { copy = left; }\n
        if (copy === 0) { break inf_leave; }\n
        //--- zmemcpy(put, next, copy); ---\n
        utils.arraySet(output, input, next, copy, put);\n
        //---//\n
        have -= copy;\n
        next += copy;\n
        left -= copy;\n
        put += copy;\n
        state.length -= copy;\n
        break;\n
      }\n
      //Tracev((stderr, "inflate:       stored end\\n"));\n
      state.mode = TYPE;\n
      break;\n
    case TABLE:\n
      //=== NEEDBITS(14); */\n
      while (bits < 14) {\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
      }\n
      //===//\n
      state.nlen = (hold & 0x1f)/*BITS(5)*/ + 257;\n
      //--- DROPBITS(5) ---//\n
      hold >>>= 5;\n
      bits -= 5;\n
      //---//\n
      state.ndist = (hold & 0x1f)/*BITS(5)*/ + 1;\n
      //--- DROPBITS(5) ---//\n
      hold >>>= 5;\n
      bits -= 5;\n
      //---//\n
      state.ncode = (hold & 0x0f)/*BITS(4)*/ + 4;\n
      //--- DROPBITS(4) ---//\n
      hold >>>= 4;\n
      bits -= 4;\n
      //---//\n
//#ifndef PKZIP_BUG_WORKAROUND\n
      if (state.nlen > 286 || state.ndist > 30) {\n
        strm.msg = \'too many length or distance symbols\';\n
        state.mode = BAD;\n
        break;\n
      }\n
//#endif\n
      //Tracev((stderr, "inflate:       table sizes ok\\n"));\n
      state.have = 0;\n
      state.mode = LENLENS;\n
      /* falls through */\n
    case LENLENS:\n
      while (state.have < state.ncode) {\n
        //=== NEEDBITS(3);\n
        while (bits < 3) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        state.lens[order[state.have++]] = (hold & 0x07);//BITS(3);\n
        //--- DROPBITS(3) ---//\n
        hold >>>= 3;\n
        bits -= 3;\n
        //---//\n
      }\n
      while (state.have < 19) {\n
        state.lens[order[state.have++]] = 0;\n
      }\n
      // We have separate tables & no pointers. 2 commented lines below not needed.\n
      //state.next = state.codes;\n
      //state.lencode = state.next;\n
      // Switch to use dynamic table\n
      state.lencode = state.lendyn;\n
      state.lenbits = 7;\n
\n
      opts = {bits: state.lenbits};\n
      ret = inflate_table(CODES, state.lens, 0, 19, state.lencode, 0, state.work, opts);\n
      state.lenbits = opts.bits;\n
\n
      if (ret) {\n
        strm.msg = \'invalid code lengths set\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      //Tracev((stderr, "inflate:       code lengths ok\\n"));\n
      state.have = 0;\n
      state.mode = CODELENS;\n
      /* falls through */\n
    case CODELENS:\n
      while (state.have < state.nlen + state.ndist) {\n
        for (;;) {\n
          here = state.lencode[hold & ((1 << state.lenbits) - 1)];/*BITS(state.lenbits)*/\n
          here_bits = here >>> 24;\n
          here_op = (here >>> 16) & 0xff;\n
          here_val = here & 0xffff;\n
\n
          if ((here_bits) <= bits) { break; }\n
          //--- PULLBYTE() ---//\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
          //---//\n
        }\n
        if (here_val < 16) {\n
          //--- DROPBITS(here.bits) ---//\n
          hold >>>= here_bits;\n
          bits -= here_bits;\n
          //---//\n
          state.lens[state.have++] = here_val;\n
        }\n
        else {\n
          if (here_val === 16) {\n
            //=== NEEDBITS(here.bits + 2);\n
            n = here_bits + 2;\n
            while (bits < n) {\n
              if (have === 0) { break inf_leave; }\n
              have--;\n
              hold += input[next++] << bits;\n
              bits += 8;\n
            }\n
            //===//\n
            //--- DROPBITS(here.bits) ---//\n
            hold >>>= here_bits;\n
            bits -= here_bits;\n
            //---//\n
            if (state.have === 0) {\n
              strm.msg = \'invalid bit length repeat\';\n
              state.mode = BAD;\n
              break;\n
            }\n
            len = state.lens[state.have - 1];\n
            copy = 3 + (hold & 0x03);//BITS(2);\n
            //--- DROPBITS(2) ---//\n
            hold >>>= 2;\n
            bits -= 2;\n
            //---//\n
          }\n
          else if (here_val === 17) {\n
            //=== NEEDBITS(here.bits + 3);\n
            n = here_bits + 3;\n
            while (bits < n) {\n
              if (have === 0) { break inf_leave; }\n
              have--;\n
              hold += input[next++] << bits;\n
              bits += 8;\n
            }\n
            //===//\n
            //--- DROPBITS(here.bits) ---//\n
            hold >>>= here_bits;\n
            bits -= here_bits;\n
            //---//\n
            len = 0;\n
            copy = 3 + (hold & 0x07);//BITS(3);\n
            //--- DROPBITS(3) ---//\n
            hold >>>= 3;\n
            bits -= 3;\n
            //---//\n
          }\n
          else {\n
            //=== NEEDBITS(here.bits + 7);\n
            n = here_bits + 7;\n
            while (bits < n) {\n
              if (have === 0) { break inf_leave; }\n
              have--;\n
              hold += input[next++] << bits;\n
              bits += 8;\n
            }\n
            //===//\n
            //--- DROPBITS(here.bits) ---//\n
            hold >>>= here_bits;\n
            bits -= here_bits;\n
            //---//\n
            len = 0;\n
            copy = 11 + (hold & 0x7f);//BITS(7);\n
            //--- DROPBITS(7) ---//\n
            hold >>>= 7;\n
            bits -= 7;\n
            //---//\n
          }\n
          if (state.have + copy > state.nlen + state.ndist) {\n
            strm.msg = \'invalid bit length repeat\';\n
            state.mode = BAD;\n
            break;\n
          }\n
          while (copy--) {\n
            state.lens[state.have++] = len;\n
          }\n
        }\n
      }\n
\n
      /* handle error breaks in while */\n
      if (state.mode === BAD) { break; }\n
\n
      /* check for end-of-block code (better have one) */\n
      if (state.lens[256] === 0) {\n
        strm.msg = \'invalid code -- missing end-of-block\';\n
        state.mode = BAD;\n
        break;\n
      }\n
\n
      /* build code tables -- note: do not change the lenbits or distbits\n
         values here (9 and 6) without reading the comments in inftrees.h\n
         concerning the ENOUGH constants, which depend on those values */\n
      state.lenbits = 9;\n
\n
      opts = {bits: state.lenbits};\n
      ret = inflat

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

e_table(LENS, state.lens, 0, state.nlen, state.lencode, 0, state.work, opts);\n
      // We have separate tables & no pointers. 2 commented lines below not needed.\n
      // state.next_index = opts.table_index;\n
      state.lenbits = opts.bits;\n
      // state.lencode = state.next;\n
\n
      if (ret) {\n
        strm.msg = \'invalid literal/lengths set\';\n
        state.mode = BAD;\n
        break;\n
      }\n
\n
      state.distbits = 6;\n
      //state.distcode.copy(state.codes);\n
      // Switch to use dynamic table\n
      state.distcode = state.distdyn;\n
      opts = {bits: state.distbits};\n
      ret = inflate_table(DISTS, state.lens, state.nlen, state.ndist, state.distcode, 0, state.work, opts);\n
      // We have separate tables & no pointers. 2 commented lines below not needed.\n
      // state.next_index = opts.table_index;\n
      state.distbits = opts.bits;\n
      // state.distcode = state.next;\n
\n
      if (ret) {\n
        strm.msg = \'invalid distances set\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      //Tracev((stderr, \'inflate:       codes ok\\n\'));\n
      state.mode = LEN_;\n
      if (flush === Z_TREES) { break inf_leave; }\n
      /* falls through */\n
    case LEN_:\n
      state.mode = LEN;\n
      /* falls through */\n
    case LEN:\n
      if (have >= 6 && left >= 258) {\n
        //--- RESTORE() ---\n
        strm.next_out = put;\n
        strm.avail_out = left;\n
        strm.next_in = next;\n
        strm.avail_in = have;\n
        state.hold = hold;\n
        state.bits = bits;\n
        //---\n
        inflate_fast(strm, _out);\n
        //--- LOAD() ---\n
        put = strm.next_out;\n
        output = strm.output;\n
        left = strm.avail_out;\n
        next = strm.next_in;\n
        input = strm.input;\n
        have = strm.avail_in;\n
        hold = state.hold;\n
        bits = state.bits;\n
        //---\n
\n
        if (state.mode === TYPE) {\n
          state.back = -1;\n
        }\n
        break;\n
      }\n
      state.back = 0;\n
      for (;;) {\n
        here = state.lencode[hold & ((1 << state.lenbits) -1)];  /*BITS(state.lenbits)*/\n
        here_bits = here >>> 24;\n
        here_op = (here >>> 16) & 0xff;\n
        here_val = here & 0xffff;\n
\n
        if (here_bits <= bits) { break; }\n
        //--- PULLBYTE() ---//\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
        //---//\n
      }\n
      if (here_op && (here_op & 0xf0) === 0) {\n
        last_bits = here_bits;\n
        last_op = here_op;\n
        last_val = here_val;\n
        for (;;) {\n
          here = state.lencode[last_val +\n
                  ((hold & ((1 << (last_bits + last_op)) -1))/*BITS(last.bits + last.op)*/ >> last_bits)];\n
          here_bits = here >>> 24;\n
          here_op = (here >>> 16) & 0xff;\n
          here_val = here & 0xffff;\n
\n
          if ((last_bits + here_bits) <= bits) { break; }\n
          //--- PULLBYTE() ---//\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
          //---//\n
        }\n
        //--- DROPBITS(last.bits) ---//\n
        hold >>>= last_bits;\n
        bits -= last_bits;\n
        //---//\n
        state.back += last_bits;\n
      }\n
      //--- DROPBITS(here.bits) ---//\n
      hold >>>= here_bits;\n
      bits -= here_bits;\n
      //---//\n
      state.back += here_bits;\n
      state.length = here_val;\n
      if (here_op === 0) {\n
        //Tracevv((stderr, here.val >= 0x20 && here.val < 0x7f ?\n
        //        "inflate:         literal \'%c\'\\n" :\n
        //        "inflate:         literal 0x%02x\\n", here.val));\n
        state.mode = LIT;\n
        break;\n
      }\n
      if (here_op & 32) {\n
        //Tracevv((stderr, "inflate:         end of block\\n"));\n
        state.back = -1;\n
        state.mode = TYPE;\n
        break;\n
      }\n
      if (here_op & 64) {\n
        strm.msg = \'invalid literal/length code\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      state.extra = here_op & 15;\n
      state.mode = LENEXT;\n
      /* falls through */\n
    case LENEXT:\n
      if (state.extra) {\n
        //=== NEEDBITS(state.extra);\n
        n = state.extra;\n
        while (bits < n) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        state.length += hold & ((1 << state.extra) -1)/*BITS(state.extra)*/;\n
        //--- DROPBITS(state.extra) ---//\n
        hold >>>= state.extra;\n
        bits -= state.extra;\n
        //---//\n
        state.back += state.extra;\n
      }\n
      //Tracevv((stderr, "inflate:         length %u\\n", state.length));\n
      state.was = state.length;\n
      state.mode = DIST;\n
      /* falls through */\n
    case DIST:\n
      for (;;) {\n
        here = state.distcode[hold & ((1 << state.distbits) -1)];/*BITS(state.distbits)*/\n
        here_bits = here >>> 24;\n
        here_op = (here >>> 16) & 0xff;\n
        here_val = here & 0xffff;\n
\n
        if ((here_bits) <= bits) { break; }\n
        //--- PULLBYTE() ---//\n
        if (have === 0) { break inf_leave; }\n
        have--;\n
        hold += input[next++] << bits;\n
        bits += 8;\n
        //---//\n
      }\n
      if ((here_op & 0xf0) === 0) {\n
        last_bits = here_bits;\n
        last_op = here_op;\n
        last_val = here_val;\n
        for (;;) {\n
          here = state.distcode[last_val +\n
                  ((hold & ((1 << (last_bits + last_op)) -1))/*BITS(last.bits + last.op)*/ >> last_bits)];\n
          here_bits = here >>> 24;\n
          here_op = (here >>> 16) & 0xff;\n
          here_val = here & 0xffff;\n
\n
          if ((last_bits + here_bits) <= bits) { break; }\n
          //--- PULLBYTE() ---//\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
          //---//\n
        }\n
        //--- DROPBITS(last.bits) ---//\n
        hold >>>= last_bits;\n
        bits -= last_bits;\n
        //---//\n
        state.back += last_bits;\n
      }\n
      //--- DROPBITS(here.bits) ---//\n
      hold >>>= here_bits;\n
      bits -= here_bits;\n
      //---//\n
      state.back += here_bits;\n
      if (here_op & 64) {\n
        strm.msg = \'invalid distance code\';\n
        state.mode = BAD;\n
        break;\n
      }\n
      state.offset = here_val;\n
      state.extra = (here_op) & 15;\n
      state.mode = DISTEXT;\n
      /* falls through */\n
    case DISTEXT:\n
      if (state.extra) {\n
        //=== NEEDBITS(state.extra);\n
        n = state.extra;\n
        while (bits < n) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        state.offset += hold & ((1 << state.extra) -1)/*BITS(state.extra)*/;\n
        //--- DROPBITS(state.extra) ---//\n
        hold >>>= state.extra;\n
        bits -= state.extra;\n
        //---//\n
        state.back += state.extra;\n
      }\n
//#ifdef INFLATE_STRICT\n
      if (state.offset > state.dmax) {\n
        strm.msg = \'invalid distance too far back\';\n
        state.mode = BAD;\n
        break;\n
      }\n
//#endif\n
      //Tracevv((stderr, "inflate:         distance %u\\n", state.offset));\n
      state.mode = MATCH;\n
      /* falls through */\n
    case MATCH:\n
      if (left === 0) { break inf_leave; }\n
      copy = _out - left;\n
      if (state.offset > copy) {         /* copy from window */\n
        copy = state.offset - copy;\n
        if (copy > state.whave) {\n
          if (state.sane) {\n
            strm.msg = \'invalid distance too far back\';\n
            state.mode = BAD;\n
            break;\n
          }\n
// (!) This block is disabled in zlib defailts,\n
// don\'t enable it for binary compatibility\n
//#ifdef INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR\n
//          Trace((stderr, "inflate.c too far\\n"));\n
//          copy -= state.whave;\n
//          if (copy > state.length) { copy = state.length; }\n
//          if (copy > left) { copy = left; }\n
//          left -= copy;\n
//          state.length -= copy;\n
//          do {\n
//            output[put++] = 0;\n
//          } while (--copy);\n
//          if (state.length === 0) { state.mode = LEN; }\n
//          break;\n
//#endif\n
        }\n
        if (copy > state.wnext) {\n
          copy -= state.wnext;\n
          from = state.wsize - copy;\n
        }\n
        else {\n
          from = state.wnext - copy;\n
        }\n
        if (copy > state.length) { copy = state.length; }\n
        from_source = state.window;\n
      }\n
      else {                              /* copy from output */\n
        from_source = output;\n
        from = put - state.offset;\n
        copy = state.length;\n
      }\n
      if (copy > left) { copy = left; }\n
      left -= copy;\n
      state.length -= copy;\n
      do {\n
        output[put++] = from_source[from++];\n
      } while (--copy);\n
      if (state.length === 0) { state.mode = LEN; }\n
      break;\n
    case LIT:\n
      if (left === 0) { break inf_leave; }\n
      output[put++] = state.length;\n
      left--;\n
      state.mode = LEN;\n
      break;\n
    case CHECK:\n
      if (state.wrap) {\n
        //=== NEEDBITS(32);\n
        while (bits < 32) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          // Use \'|\' insdead of \'+\' to make sure that result is signed\n
          hold |= input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        _out -= left;\n
        strm.total_out += _out;\n
        state.total += _out;\n
        if (_out) {\n
          strm.adler = state.check =\n
              /*UPDATE(state.check, put - _out, _out);*/\n
              (state.flags ? crc32(state.check, output, _out, put - _out) : adler32(state.check, output, _out, put - _out));\n
\n
        }\n
        _out = left;\n
        // NB: crc32 stored as signed 32-bit int, ZSWAP32 returns signed too\n
        if ((state.flags ? hold : ZSWAP32(hold)) !== state.check) {\n
          strm.msg = \'incorrect data check\';\n
          state.mode = BAD;\n
          break;\n
        }\n
        //=== INITBITS();\n
        hold = 0;\n
        bits = 0;\n
        //===//\n
        //Tracev((stderr, "inflate:   check matches trailer\\n"));\n
      }\n
      state.mode = LENGTH;\n
      /* falls through */\n
    case LENGTH:\n
      if (state.wrap && state.flags) {\n
        //=== NEEDBITS(32);\n
        while (bits < 32) {\n
          if (have === 0) { break inf_leave; }\n
          have--;\n
          hold += input[next++] << bits;\n
          bits += 8;\n
        }\n
        //===//\n
        if (hold !== (state.total & 0xffffffff)) {\n
          strm.msg = \'incorrect length check\';\n
          state.mode = BAD;\n
          break;\n
        }\n
        //=== INITBITS();\n
        hold = 0;\n
        bits = 0;\n
        //===//\n
        //Tracev((stderr, "inflate:   length matches trailer\\n"));\n
      }\n
      state.mode = DONE;\n
      /* falls through */\n
    case DONE:\n
      ret = Z_STREAM_END;\n
      break inf_leave;\n
    case BAD:\n
      ret = Z_DATA_ERROR;\n
      break inf_leave;\n
    case MEM:\n
      return Z_MEM_ERROR;\n
    case SYNC:\n
      /* falls through */\n
    default:\n
      return Z_STREAM_ERROR;\n
    }\n
  }\n
\n
  // inf_leave <- here is real place for "goto inf_leave", emulated via "break inf_leave"\n
\n
  /*\n
     Return from inflate(), updating the total counts and the check value.\n
     If there was no progress during the inflate() call, return a buffer\n
     error.  Call updatewindow() to create and/or update the window state.\n
     Note: a memory error from inflate() is non-recoverable.\n
   */\n
\n
  //--- RESTORE() ---\n
  strm.next_out = put;\n
  strm.avail_out = left;\n
  strm.next_in = next;\n
  strm.avail_in = have;\n
  state.hold = hold;\n
  state.bits = bits;\n
  //---\n
\n
  if (state.wsize || (_out !== strm.avail_out && state.mode < BAD &&\n
                      (state.mode < CHECK || flush !== Z_FINISH))) {\n
    if (updatewindow(strm, strm.output, strm.next_out, _out - strm.avail_out)) {\n
      state.mode = MEM;\n
      return Z_MEM_ERROR;\n
    }\n
  }\n
  _in -= strm.avail_in;\n
  _out -= strm.avail_out;\n
  strm.total_in += _in;\n
  strm.total_out += _out;\n
  state.total += _out;\n
  if (state.wrap && _out) {\n
    strm.adler = state.check = /*UPDATE(state.check, strm.next_out - _out, _out);*/\n
      (state.flags ? crc32(state.check, output, _out, strm.next_out - _out) : adler32(state.check, output, _out, strm.next_out - _out));\n
  }\n
  strm.data_type = state.bits + (state.last ? 64 : 0) +\n
                    (state.mode === TYPE ? 128 : 0) +\n
                    (state.mode === LEN_ || state.mode === COPY_ ? 256 : 0);\n
  if (((_in === 0 && _out === 0) || flush === Z_FINISH) && ret === Z_OK) {\n
    ret = Z_BUF_ERROR;\n
  }\n
  return ret;\n
}\n
\n
function inflateEnd(strm) {\n
\n
  if (!strm || !strm.state /*|| strm->zfree == (free_func)0*/) {\n
    return Z_STREAM_ERROR;\n
  }\n
\n
  var state = strm.state;\n
  if (state.window) {\n
    state.window = null;\n
  }\n
  strm.state = null;\n
  return Z_OK;\n
}\n
\n
function inflateGetHeader(strm, head) {\n
  var state;\n
\n
  /* check state */\n
  if (!strm || !strm.state) { return Z_STREAM_ERROR; }\n
  state = strm.state;\n
  if ((state.wrap & 2) === 0) { return Z_STREAM_ERROR; }\n
\n
  /* save header structure */\n
  state.head = head;\n
  head.done = false;\n
  return Z_OK;\n
}\n
\n
\n
exports.inflateReset = inflateReset;\n
exports.inflateReset2 = inflateReset2;\n
exports.inflateResetKeep = inflateResetKeep;\n
exports.inflateInit = inflateInit;\n
exports.inflateInit2 = inflateInit2;\n
exports.inflate = inflate;\n
exports.inflateEnd = inflateEnd;\n
exports.inflateGetHeader = inflateGetHeader;\n
exports.inflateInfo = \'pako inflate (from Nodeca project)\';\n
\n
/* Not implemented\n
exports.inflateCopy = inflateCopy;\n
exports.inflateGetDictionary = inflateGetDictionary;\n
exports.inflateMark = inflateMark;\n
exports.inflatePrime = inflatePrime;\n
exports.inflateSetDictionary = inflateSetDictionary;\n
exports.inflateSync = inflateSync;\n
exports.inflateSyncPoint = inflateSyncPoint;\n
exports.inflateUndermine = inflateUndermine;\n
*/\n
},{"../utils/common":27,"./adler32":29,"./crc32":31,"./inffast":34,"./inftrees":36}],36:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var utils = _dereq_(\'../utils/common\');\n
\n
var MAXBITS = 15;\n
var ENOUGH_LENS = 852;\n
var ENOUGH_DISTS = 592;\n
//var ENOUGH = (ENOUGH_LENS+ENOUGH_DISTS);\n
\n
var CODES = 0;\n
var LENS = 1;\n
var DISTS = 2;\n
\n
var lbase = [ /* Length codes 257..285 base */\n
  3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,\n
  35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258, 0, 0\n
];\n
\n
var lext = [ /* Length codes 257..285 extra */\n
  16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17, 17, 18, 18, 18, 18,\n
  19, 19, 19, 19, 20, 20, 20, 20, 21, 21, 21, 21, 16, 72, 78\n
];\n
\n
var dbase = [ /* Distance codes 0..29 base */\n
  1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193,\n
  257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145,\n
  8193, 12289, 16385, 24577, 0, 0\n
];\n
\n
var dext = [ /* Distance codes 0..29 extra */\n
  16, 16, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22,\n
  23, 23, 24, 24, 25, 25, 26, 26, 27, 27,\n
  28, 28, 29, 29, 64, 64\n
];\n
\n
module.exports = function inflate_table(type, lens, lens_index, codes, table, table_index, work, opts)\n
{\n
  var bits = opts.bits;\n
      //here = opts.here; /* table entry for duplication */\n
\n
  var len = 0;               /* a code\'s length in bits */\n
  var sym = 0;               /* index of code symbols */\n
  var min = 0, max = 0;          /* minimum and maximum code lengths */\n
  var root = 0;              /* number of index bits for root table */\n
  var curr = 0;              /* number of index bits for current table */\n
  var drop = 0;              /* code bits to drop for sub-table */\n
  var left = 0;                   /* number of prefix codes available */\n
  var used = 0;              /* code entries in table used */\n
  var huff = 0;              /* Huffman code */\n
  var incr;              /* for incrementing code, index */\n
  var fill;              /* index for replicating entries */\n
  var low;               /* low bits for current root entry */\n
  var mask;              /* mask for low root bits */\n
  var next;             /* next available space in table */\n
  var base = null;     /* base value table to use */\n
  var base_index = 0;\n
//  var shoextra;    /* extra bits table to use */\n
  var end;                    /* use base and extra for symbol > end */\n
  var count = new utils.Buf16(MAXBITS+1); //[MAXBITS+1];    /* number of codes of each length */\n
  var offs = new utils.Buf16(MAXBITS+1); //[MAXBITS+1];     /* offsets in table for each length */\n
  var extra = null;\n
  var extra_index = 0;\n
\n
  var here_bits, here_op, here_val;\n
\n
  /*\n
   Process a set of code lengths to create a canonical Huffman code.  The\n
   code lengths are lens[0..codes-1].  Each length corresponds to the\n
   symbols 0..codes-1.  The Huffman code is generated by first sorting the\n
   symbols by length from short to long, and retaining the symbol order\n
   for codes with equal lengths.  Then the code starts with all zero bits\n
   for the first code of the shortest length, and the codes are integer\n
   increments for the same length, and zeros are appended as the length\n
   increases.  For the deflate format, these bits are stored backwards\n
   from their more natural integer increment ordering, and so when the\n
   decoding tables are built in the large loop below, the integer codes\n
   are incremented backwards.\n
\n
   This routine assumes, but does not check, that all of the entries in\n
   lens[] are in the range 0..MAXBITS.  The caller must assure this.\n
   1..MAXBITS is interpreted as that code length.  zero means that that\n
   symbol does not occur in this code.\n
\n
   The codes are sorted by computing a count of codes for each length,\n
   creating from that a table of starting indices for each length in the\n
   sorted table, and then entering the symbols in order in the sorted\n
   table.  The sorted table is work[], with that space being provided by\n
   the caller.\n
\n
   The length counts are used for other purposes as well, i.e. finding\n
   the minimum and maximum length codes, determining if there are any\n
   codes at all, checking for a valid set of lengths, and looking ahead\n
   at length counts to determine sub-table sizes when building the\n
   decoding tables.\n
   */\n
\n
  /* accumulate lengths for codes (assumes lens[] all in 0..MAXBITS) */\n
  for (len = 0; len <= MAXBITS; len++) {\n
    count[len] = 0;\n
  }\n
  for (sym = 0; sym < codes; sym++) {\n
    count[lens[lens_index + sym]]++;\n
  }\n
\n
  /* bound code lengths, force root to be within code lengths */\n
  root = bits;\n
  for (max = MAXBITS; max >= 1; max--) {\n
    if (count[max] !== 0) { break; }\n
  }\n
  if (root > max) {\n
    root = max;\n
  }\n
  if (max === 0) {                     /* no symbols to code at all */\n
    //table.op[opts.table_index] = 64;  //here.op = (var char)64;    /* invalid code marker */\n
    //table.bits[opts.table_index] = 1;   //here.bits = (var char)1;\n
    //table.val[opts.table_index++] = 0;   //here.val = (var short)0;\n
    table[table_index++] = (1 << 24) | (64 << 16) | 0;\n
\n
\n
    //table.op[opts.table_index] = 64;\n
    //table.bits[opts.table_index] = 1;\n
    //table.val[opts.table_index++] = 0;\n
    table[table_index++] = (1 << 24) | (64 << 16) | 0;\n
\n
    opts.bits = 1;\n
    return 0;     /* no symbols, but wait for decoding to report error */\n
  }\n
  for (min = 1; min < max; min++) {\n
    if (count[min] !== 0) { break; }\n
  }\n
  if (root < min) {\n
    root = min;\n
  }\n
\n
  /* check for an over-subscribed or incomplete set of lengths */\n
  left = 1;\n
  for (len = 1; len <= MAXBITS; len++) {\n
    left <<= 1;\n
    left -= count[len];\n
    if (left < 0) {\n
      return -1;\n
    }        /* over-subscribed */\n
  }\n
  if (left > 0 && (type === CODES || max !== 1)) {\n
    return -1;                      /* incomplete set */\n
  }\n
\n
  /* generate offsets into symbol table for each length for sorting */\n
  offs[1] = 0;\n
  for (len = 1; len < MAXBITS; len++) {\n
    offs[len + 1] = offs[len] + count[len];\n
  }\n
\n
  /* sort symbols by length, by symbol order within each length */\n
  for (sym = 0; sym < codes; sym++) {\n
    if (lens[lens_index + sym] !== 0) {\n
      work[offs[lens[lens_index + sym]]++] = sym;\n
    }\n
  }\n
\n
  /*\n
   Create and fill in decoding tables.  In this loop, the table being\n
   filled is at next and has curr index bits.  The code being used is huff\n
   with length len.  That code is converted to an index by dropping drop\n
   bits off of the bottom.  For codes where len is less than drop + curr,\n
   those top drop + curr - len bits are incremented through all values to\n
   fill the table with replicated entries.\n
\n
   root is the number of index bits for the root table.  When len exceeds\n
   root, sub-tables are created pointed to by the root entry with an index\n
   of the low root bits of huff.  This is saved in low to check for when a\n
   new sub-table should be started.  drop is zero when the root table is\n
   being filled, and drop is root when sub-tables are being filled.\n
\n
   When a new sub-table is needed, it is necessary to look ahead in the\n
   code lengths to determine what size sub-table is needed.  The length\n
   counts are used for this, and so count[] is decremented as codes are\n
   entered in the tables.\n
\n
   used keeps track of how many table entries have been allocated from the\n
   provided *table space.  It is checked for LENS and DIST tables against\n
   the constants ENOUGH_LENS and ENOUGH_DISTS to guard against changes in\n
   the initial root table size constants.  See the comments in inftrees.h\n
   for more information.\n
\n
   sym increments through all symbols, and the loop terminates when\n
   all codes of length max, i.e. all codes, have been processed.  This\n
   routine permits incomplete codes, so another loop after this one fills\n
   in the rest of the decoding tables with invalid code markers.\n
   */\n
\n
  /* set up for code type */\n
  // poor man optimization - use if-else instead of switch,\n
  // to avoid deopts in old v8\n
  if (type === CODES) {\n
      base = extra = work;    /* dummy value--not used */\n
      end = 19;\n
  } else if (type === LENS) {\n
      base = lbase;\n
      base_index -= 257;\n
      extra = lext;\n
      extra_index -= 257;\n
      end = 256;\n
  } else {                    /* DISTS */\n
      base = dbase;\n
      extra = dext;\n
      end = -1;\n
  }\n
\n
  /* initialize opts for loop */\n
  huff = 0;                   /* starting code */\n
  sym = 0;                    /* starting code symbol */\n
  len = min;                  /* starting code length */\n
  next = table_index;              /* current table to fill in */\n
  curr = root;                /* current table index bits */\n
  drop = 0;                   /* current bits to drop from code for index */\n
  low = -1;                   /* trigger new sub-table when len > root */\n
  used = 1 << root;          /* use root table entries */\n
  mask = used - 1;            /* mask for comparing low */\n
\n
  /* check available table space */\n
  if ((type === LENS && used > ENOUGH_LENS) ||\n
    (type === DISTS && used > ENOUGH_DISTS)) {\n
    return 1;\n
  }\n
\n
  var i=0;\n
  /* process all codes and make table entries */\n
  for (;;) {\n
    i++;\n
    /* create table entry */\n
    here_bits = len - drop;\n
    if (work[sym] < end) {\n
      here_op = 0;\n
      here_val = work[sym];\n
    }\n
    else if (work[sym] > end) {\n
      here_op = extra[extra_index + work[sym]];\n
      here_val = base[base_index + work[sym]];\n
    }\n
    else {\n
      here_op = 32 + 64;         /* end of block */\n
      here_val = 0;\n
    }\n
\n
    /* replicate for those indices with low len bits equal to huff */\n
    incr = 1 << (len - drop);\n
    fill = 1 << curr;\n
    min = fill;                 /* save offset to next table */\n
    do {\n
      fill -= incr;\n
      table[next + (huff >> drop) + fill] = (here_bits << 24) | (here_op << 16) | here_val |0;\n
    } while (fill !== 0);\n
\n
    /* backwards increment the len-bit code huff */\n
    incr = 1 << (len - 1);\n
    while (huff & incr) {\n
      incr >>= 1;\n
    }\n
    if (incr !== 0) {\n
      huff &= incr - 1;\n
      huff += incr;\n
    } else {\n
      huff = 0;\n
    }\n
\n
    /* go to next symbol, update count, len */\n
    sym++;\n
    if (--count[len] === 0) {\n
      if (len === max) { break; }\n
      len = lens[lens_index + work[sym]];\n
    }\n
\n
    /* create new sub-table if needed */\n
    if (len > root && (huff & mask) !== low) {\n
      /* if first time, transition to sub-tables */\n
      if (drop === 0) {\n
        drop = root;\n
      }\n
\n
      /* increment past last table */\n
      next += min;            /* here min is 1 << curr */\n
\n
      /* determine length of next table */\n
      curr = len - drop;\n
      left = 1 << curr;\n
      while (curr + drop < max) {\n
        left -= count[curr + drop];\n
        if (left <= 0) { break; }\n
        curr++;\n
        left <<= 1;\n
      }\n
\n
      /* check for enough space */\n
      used += 1 << curr;\n
      if ((type === LENS && used > ENOUGH_LENS) ||\n
        (type === DISTS && used > ENOUGH_DISTS)) {\n
        return 1;\n
      }\n
\n
      /* point entry in root table to sub-table */\n
      low = huff & mask;\n
      /*table.op[low] = curr;\n
      table.bits[low] = root;\n
      table.val[low] = next - opts.table_index;*/\n
      table[low] = (root << 24) | (curr << 16) | (next - table_index) |0;\n
    }\n
  }\n
\n
  /* fill in remaining table entry if code is incomplete (guaranteed to have\n
   at most one remaining entry, since if the code is incomplete, the\n
   maximum code length that was allowed to get this far is one bit) */\n
  if (huff !== 0) {\n
    //table.op[next + huff] = 64;            /* invalid code marker */\n
    //table.bits[next + huff] = len - drop;\n
    //table.val[next + huff] = 0;\n
    table[next + huff] = ((len - drop) << 24) | (64 << 16) |0;\n
  }\n
\n
  /* set return parameters */\n
  //opts.table_index += used;\n
  opts.bits = root;\n
  return 0;\n
};\n
\n
},{"../utils/common":27}],37:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
module.exports = {\n
  \'2\':    \'need dictionary\',     /* Z_NEED_DICT       2  */\n
  \'1\':    \'stream end\',          /* Z_STREAM_END      1  */\n
  \'0\':    \'\',                    /* Z_OK              0  */\n
  \'-1\':   \'file error\',          /* Z_ERRNO         (-1) */\n
  \'-2\':   \'stream error\',        /* Z_STREAM_ERROR  (-2) */\n
  \'-3\':   \'data error\',          /* Z_DATA_ERROR    (-3) */\n
  \'-4\':   \'insufficient memory\', /* Z_MEM_ERROR     (-4) */\n
  \'-5\':   \'buffer error\',        /* Z_BUF_ERROR     (-5) */\n
  \'-6\':   \'incompatible version\' /* Z_VERSION_ERROR (-6) */\n
};\n
},{}],38:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
var utils = _dereq_(\'../utils/common\');\n
\n
/* Public constants ==========================================================*/\n
/* ===========================================================================*/\n
\n
\n
//var Z_FILTERED          = 1;\n
//var Z_HUFFMAN_ONLY      = 2;\n
//var Z_RLE               = 3;\n
var Z_FIXED               = 4;\n
//var Z_DEFAULT_STRATEGY  = 0;\n
\n
/* Possible values of the data_type field (though see inflate()) */\n
var Z_BINARY              = 0;\n
var Z_TEXT                = 1;\n
//var Z_ASCII             = 1; // = Z_TEXT\n
var Z_UNKNOWN             = 2;\n
\n
/*============================================================================*/\n
\n
\n
function zero(buf) { var len = buf.length; while (--len >= 0) { buf[len] = 0; } }\n
\n
// From zutil.h\n
\n
var STORED_BLOCK = 0;\n
var STATIC_TREES = 1;\n
var DYN_TREES    = 2;\n
/* The three kinds of block type */\n
\n
var MIN_MATCH    = 3;\n
var MAX_MATCH    = 258;\n
/* The minimum and maximum match lengths */\n
\n
// From deflate.h\n
/* ===========================================================================\n
 * Internal compression state.\n
 */\n
\n
var LENGTH_CODES  = 29;\n
/* number of length codes, not counting the special END_BLOCK code */\n
\n
var LITERALS      = 256;\n
/* number of literal bytes 0..255 */\n
\n
var L_CODES       = LITERALS + 1 + LENGTH_CODES;\n
/* number of Literal or Length codes, including the END_BLOCK code */\n
\n
var D_CODES       = 30;\n
/* number of distance codes */\n
\n
var BL_CODES      = 19;\n
/* number of codes used to transfer the bit lengths */\n
\n
var HEAP_SIZE     = 2*L_CODES + 1;\n
/* maximum heap size */\n
\n
var MAX_BITS      = 15;\n
/* All codes must not exceed MAX_BITS bits */\n
\n
var Buf_size      = 16;\n
/* size of bit buffer in bi_buf */\n
\n
\n
/* ===========================================================================\n
 * Constants\n
 */\n
\n
var MAX_BL_BITS = 7;\n
/* Bit length codes must not exceed MAX_BL_BITS bits */\n
\n
var END_BLOCK   = 256;\n
/* end of block literal code */\n
\n
var REP_3_6     = 16;\n
/* repeat previous bit length 3-6 times (2 bits of repeat count) */\n
\n
var REPZ_3_10   = 17;\n
/* repeat a zero length 3-10 times  (3 bits of repeat count) */\n
\n
var REPZ_11_138 = 18;\n
/* repeat a zero length 11-138 times  (7 bits of repeat count) */\n
\n
var extra_lbits =   /* extra bits for each length code */\n
  [0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];\n
\n
var extra_dbits =   /* extra bits for each distance code */\n
  [0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];\n
\n
var extra_blbits =  /* extra bits for each bit length code */\n
  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,3,7];\n
\n
var bl_order =\n
  [16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15];\n
/* The lengths of the bit length codes are sent in order of decreasing\n
 * probability, to avoid transmitting the lengths for unused bit length codes.\n
 */\n
\n
/* ===========================================================================\n
 * Local data. These are initialized only once.\n
 */\n
\n
// We pre-fill arrays with 0 to avoid uninitialized gaps\n
\n
var DIST_CODE_LEN = 512; /* see definition of array dist_code below */\n
\n
// !!!! Use flat array insdead of structure, Freq = i*2, Len = i*2+1\n
var static_ltree  = new Array((L_CODES+2) * 2);\n
zero(static_ltree);\n
/* The static literal tree. Since the bit lengths are imposed, there is no\n
 * need for the L_CODES extra codes used during heap construction. However\n
 * The codes 286 and 287 are needed to build a canonical tree (see _tr_init\n
 * below).\n
 */\n
\n
var static_dtree  = new Array(D_CODES * 2);\n
zero(static_dtree);\n
/* The static distance tree. (Actually a trivial tree since all codes use\n
 * 5 bits.)\n
 */\n
\n
var _dist_code    = new Array(DIST_CODE_LEN);\n
zero(_dist_code);\n
/* Distance codes. The first 256 values correspond to the distances\n
 * 3 .. 258, the last 256 values correspond to the top 8 bits of\n
 * the 15 bit distances.\n
 */\n
\n
var _length_code  = new Array(MAX_MATCH-MIN_MATCH+1);\n
zero(_length_code);\n
/* length code for each normalized match length (0 == MIN_MATCH) */\n
\n
var base_length   = new Array(LENGTH_CODES);\n
zero(base_length);\n
/* First normalized length for each code (0 = MIN_MATCH) */\n
\n
var base_dist     = new Array(D_CODES);\n
zero(base_dist);\n
/* First normalized distance for each code (0 = distance of 1) */\n
\n
\n
var StaticTreeDesc = function (static_tree, extra_bits, extra_base, elems, max_length) {\n
\n
  this.static_tree  = static_tree;  /* static tree or NULL */\n
  this.extra_bits   = extra_bits;   /* extra bits for each code or NULL */\n
  this.extra_base   = extra_base;   /* base index for extra_bits */\n
  this.elems        = elems;        /* max number of elements in the tree */\n
  this.max_length   = max_length;   /* max bit length for the codes */\n
\n
  // show if `static_tree` has data or dummy - needed for monomorphic objects\n
  this.has_stree    = static_tree && static_tree.length;\n
};\n
\n
\n
var static_l_desc;\n
var static_d_desc;\n
var static_bl_desc;\n
\n
\n
var TreeDesc = function(dyn_tree, stat_desc) {\n
  this.dyn_tree = dyn_tree;     /* the dynamic tree */\n
  this.max_code = 0;            /* largest code with non zero frequency */\n
  this.stat_desc = stat_desc;   /* the corresponding static tree */\n
};\n
\n
\n
\n
function d_code(dist) {\n
  return dist < 256 ? _dist_code[dist] : _dist_code[256 + (dist >>> 7)];\n
}\n
\n
\n
/* ===========================================================================\n
 * Output a short LSB first on the stream.\n
 * IN assertion: there is enough room in pendingBuf.\n
 */\n
function put_short (s, w) {\n
//    put_byte(s, (uch)((w) & 0xff));\n
//    put_byte(s, (uch)((ush)(w) >> 8));\n
  s.pending_buf[s.pending++] = (w) & 0xff;\n
  s.pending_buf[s.pending++] = (w >>> 8) & 0xff;\n
}\n
\n
\n
/* ===========================================================================\n
 * Send a value on a given number of bits.\n
 * IN assertion: length <= 16 and value fits in length bits.\n
 */\n
function send_bits(s, value, length) {\n
  if (s.bi_valid > (Buf_size - length)) {\n
    s.bi_buf |= (value << s.bi_valid) & 0xffff;\n
    put_short(s, s.bi_buf);\n
    s.bi_buf = value >> (Buf_size - s.bi_valid);\n
    s.bi_valid += length - Buf_size;\n
  } else {\n
    s.bi_buf |= (value << s.bi_valid) & 0xffff;\n
    s.bi_valid += length;\n
  }\n
}\n
\n
\n
function send_code(s, c, tree) {\n
  send_bits(s, tree[c*2]/*.Code*/, tree[c*2 + 1]/*.Len*/);\n
}\n
\n
\n
/* ===========================================================================\n
 * Reverse the first len bits of a code, using straightforward code (a faster\n
 * method would use a table)\n
 * IN assertion: 1 <= len <= 15\n
 */\n
function bi_reverse(code, len) {\n
  var res = 0;\n
  do {\n
    res |= code & 1;\n
    code >>>= 1;\n
    res <<= 1;\n
  } while (--len > 0);\n
  return res >>> 1;\n
}\n
\n
\n
/* ===========================================================================\n
 * Flush the bit buffer, keeping at most 7 bits in it.\n
 */\n
function bi_flush(s) {\n
  if (s.bi_valid === 16) {\n
    put_short(s, s.bi_buf);\n
    s.bi_buf = 0;\n
    s.bi_valid = 0;\n
\n
  } else if (s.bi_valid >= 8) {\n
    s.pending_buf[s.pending++] = s.bi_buf & 0xff;\n
    s.bi_buf >>= 8;\n
    s.bi_valid -= 8;\n
  }\n
}\n
\n
\n
/* ===========================================================================\n
 * Compute the optimal bit lengths for a tree and update the total bit length\n
 * for the current block.\n
 * IN assertion: the fields freq and dad are set, heap[heap_max] and\n
 *    above are the tree nodes sorted by increasing frequency.\n
 * OUT assertions: the field len is set to the optimal bit length, the\n
 *     array bl_count contains the frequencies for each bit length.\n
 *     The length opt_len is updated; static_len is also updated if stree is\n
 *     not null.\n
 */\n
function gen_bitlen(s, desc)\n
//    deflate_state *s;\n
//    tree_desc *desc;    /* the tree descriptor */\n
{\n
  var tree            = desc.dyn_tree;\n
  var max_code        = desc.max_code;\n
  var stree           = desc.stat_desc.static_tree;\n
  var has_stree       = desc.stat_desc.has_stree;\n
  var extra           = desc.stat_desc.extra_bits;\n
  var base            = desc.stat_desc.extra_base;\n
  var max_length      = desc.stat_desc.max_length;\n
  var h;              /* heap index */\n
  var n, m;           /* iterate over the tree elements */\n
  var bits;           /* bit length */\n
  var xbits;          /* extra bits */\n
  var f;              /* frequency */\n
  var overflow = 0;   /* number of elements with bit length too large */\n
\n
  for (bits = 0; bits <= MAX_BITS; bits++) {\n
    s.bl_count[bits] = 0;\n
  }\n
\n
  /* In a first pass, compute the optimal bit lengths (which may\n
   * overflow in the case of the bit length tree).\n
   */\n
  tree[s.heap[s.heap_max]*2 + 1]/*.Len*/ = 0; /* root of the heap */\n
\n
  for (h = s.heap_max+1; h < HEAP_SIZE; h++) {\n
    n = s.heap[h];\n
    bits = tree[tree[n*2 +1]/*.Dad*/ * 2 + 1]/*.Len*/ + 1;\n
    if (bits > max_length) {\n
      bits = max_length;\n
      overflow++;\n
    }\n
    tree[n*2 + 1]/*.Len*/ = bits;\n
    /* We overwrite tree[n].Dad which is no longer needed */\n
\n
    if (n > max_code) { continue; } /* not a leaf node */\n
\n
    s.bl_count[bits]++;\n
    xbits = 0;\n
    if (n >= base) {\n
      xbits = extra[n-base];\n
    }\n
    f = tree[n * 2]/*.Freq*/;\n
    s.opt_len += f * (bits + xbits);\n
    if (has_stree) {\n
      s.static_len += f * (stree[n*2 + 1]/*.Len*/ + xbits);\n
    }\n
  }\n
  if (overflow === 0) { return; }\n
\n
  // Trace((stderr,"\\nbit length overflow\\n"));\n
  /* This happens for example on obj2 and pic of the Calgary corpus */\n
\n
  /* Find the first bit length which could increase: */\n
  do {\n
    bits = max_length-1;\n
    while (s.bl_count[bits] === 0) { bits--; }\n
    s.bl_count[bits]--;      /* move one leaf down the tree */\n
    s.bl_count[bits+1] += 2; /* move one overflow item as its brother */\n
    s.bl_count[max_length]--;\n
    /* The brother of the overflow item also moves one step up,\n
     * but this does not affect bl_count[max_length]\n
     */\n
    overflow -= 2;\n
  } while (overflow > 0);\n
\n
  /* Now recompute all bit lengths, scanning in increasing frequency.\n
   * h is still equal to HEAP_SIZE. (It is simpler to reconstruct all\n
   * lengths instead of fixing only the wrong ones. This idea is taken\n
   * from \'ar\' written by Haruhiko Okumura.)\n
   */\n
  for (bits = max_length; bits !== 0; bits--) {\n
    n = s.bl_count[bits];\n
    while (n !== 0) {\n
      m = s.heap[--h];\n
      if (m > max_code) { continue; }\n
      if (tree[m*2 + 1]/*.Len*/ !== bits) {\n
        // Trace((stderr,"code %d bits %d->%d\\n", m, tree[m].Len, bits));\n
        s.opt_len += (bits - tree[m*2 + 1]/*.Len*/)*tree[m*2]/*.Freq*/;\n
        tree[m*2 + 1]/*.Len*/ = bits;\n
      }\n
      n--;\n
    }\n
  }\n
}\n
\n
\n
/* ===========================================================================\n
 * Generate the codes for a given tree and bit counts (which need not be\n
 * optimal).\n
 * IN assertion: the array bl_count contains the bit length statistics for\n
 * the given tree and the field len is set for all tree elements.\n
 * OUT assertion: the field code is set for all tree elements of non\n
 *     zero code length.\n
 */\n
function gen_codes(tree, max_code, bl_count)\n
//    ct_data *tree;             /* the tree to decorate */\n
//    int max_code;              /* largest code with non zero frequency */\n
//    ushf *bl_count;            /* number of codes at each bit length */\n
{\n
  var next_code = new Array(MAX_BITS+1); /* next code value for each bit length */\n
  var code = 0;              /* running code value */\n
  var bits;                  /* bit index */\n
  var n;                     /* code index */\n
\n
  /* The distribution counts are first used to generate the code values\n
   * without bit reversal.\n
   */\n
  for (bits = 1; bits <= MAX_BITS; bits++) {\n
    next_code[bits] = code = (code + bl_count[bits-1]) << 1;\n
  }\n
  /* Check that the bit counts in bl_count are consistent. The last code\n
   * must be all ones.\n
   */\n
  //Assert (code + bl_count[MAX_BITS]-1 == (1<<MAX_BITS)-1,\n
  //        "inconsistent bit counts");\n
  //Tracev((stderr,"\\ngen_codes: max_code %d ", max_code));\n
\n
  for (n = 0;  n <= max_code; n++) {\n
    var len = tree[n*2 + 1]/*.Len*/;\n
    if (len === 0) { continue; }\n
    /* Now reverse the bits */\n
    tree[n*2]/*.Code*/ = bi_reverse(next_code[len]++, len);\n
\n
    //Tracecv(tree != static_ltree, (stderr,"\\nn %3d %c l %2d c %4x (%x) ",\n
    //     n, (isgraph(n) ? n : \' \'), len, tree[n].Code, next_code[len]-1));\n
  }\n
}\n
\n
\n
/* ===========================================================================\n
 * Initialize the various \'constant\' tables.\n
 */\n
function tr_static_init() {\n
  var n;        /* iterates over tree elements */\n
  var bits;     /* bit counter */\n
  var length;   /* length value */\n
  var code;     /* code value */\n
  var dist;     /* distance index */\n
  var bl_count = new Array(MAX_BITS+1);\n
  /* number of codes at each bit length for an optimal tree */\n
\n
  // do check in _tr_init()\n
  //if (static_init_done) return;\n
\n
  /* For some embedded targets, global variables are not initialized: */\n
/*#ifdef NO_INIT_GLOBAL_POINTERS\n
  static_l_desc.static_tree = static_ltree;\n
  static_l_desc.extra_bits = extra_lbits;\n
  static_d_desc.static_tree = static_dtree;\n
  static_d_desc.extra_bits = extra_dbits;\n
  static_bl_desc.extra_bits = extra_blbits;\n
#endif*/\n
\n
  /* Initialize the mapping length (0..255) -> length code (0..28) */\n
  length = 0;\n
  for (code = 0; code < LENGTH_CODES-1; code++) {\n
    base_length[code] = length;\n
    for (n = 0; n < (1<<extra_lbits[code]); n++) {\n
      _length_code[length++] = code;\n
    }\n
  }\n
  //Assert (length == 256, "tr_static_init: length != 256");\n
  /* Note that the length 255 (match length 258) can be represented\n
   * in two different ways: code 284 + 5 bits or code 285, so we\n
   * overwrite length_code[255] to use the best encoding:\n
   */\n
  _length_code[length-1] = code;\n
\n
  /* Initialize the mapping dist (0..32K) -> dist code (0..29) */\n
  dist = 0;\n
  for (code = 0 ; code < 16; code++) {\n
    base_dist[code] = dist;\n
    for (n = 0; n < (1<<extra_dbits[code]); n++) {\n
      _dist_code[dist++] = code;\n
    }\n
  }\n
  //Assert (dist == 256, "tr_static_init: dist != 256");\n
  dist >>= 7; /* from now on, all distances are divided by 128 */\n
  for ( ; code < D_CODES; code++) {\n
    base_dist[code] = dist << 7;\n
    for (n = 0; n < (1<<(extra_dbits[code]-7)); n++) {\n
      _dist_code[256 + dist++] = code;\n
    }\n
  }\n
  //Assert (dist == 256, "tr_static_init: 256+dist != 512");\n
\n
  /* Construct the codes of the static literal tree */\n
  for (bits = 0; bits <= MAX_BITS; bits++) {\n
    bl_count[bits] = 0;\n
  }\n
\n
  n = 0;\n
  while (n <= 143) {\n
    static_ltree[n*2 + 1]/*.Len*/ = 8;\n
    n++;\n
    bl_count[8]++;\n
  }\n
  while (n <= 255) {\n
    static_ltree[n*2 + 1]/*.Len*/ = 9;\n
    n++;\n
    bl_count[9]++;\n
  }\n
  while (n <= 279) {\n
    static_ltree[n*2 + 1]/*.Len*/ = 7;\n
    n++;\n
    bl_count[7]++;\n
  }\n
  while (n <= 287) {\n
    static_ltree[n*2 + 1]/*.Len*/ = 8;\n
    n++;\n
    bl_count[8]++;\n
  }\n
  /* Codes 286 and 287 do not exist, but we must include them in the\n
   * tree construction to get a canonical Huffman tree (longest code\n
   * all ones)\n
   */\n
  gen_codes(static_ltree, L_CODES+1, bl_count);\n
\n
  /* The static distance tree is trivial: */\n
  for (n = 0; n < D_CODES; n++) {\n
    static_dtree[n*2 + 1]/*.Len*/ = 5;\n
    static_dtree[n*2]/*.Code*/ = bi_reverse(n, 5);\n
  }\n
\n
  // Now data ready and we can init static trees\n
  static_l_desc = new StaticTreeDesc(static_ltree, extra_lbits, LITERALS+1, L_CODES, MAX_BITS);\n
  static_d_desc = new StaticTreeDesc(static_dtree, extra_dbits, 0,          D_CODES, MAX_BITS);\n
  static_bl_desc =new StaticTreeDesc(new Array(0), extra_blbits, 0,         BL_CODES, MAX_BL_BITS);\n
\n
  //static_init_done = true;\n
}\n
\n
\n
/* ===========================================================================\n
 * Initialize a new block.\n
 */\n
function init_block(s) {\n
  var n; /* iterates over tree elements */\n
\n
  /* Initialize the trees. */\n
  for (n = 0; n < L_CODES;  n++) { s.dyn_ltree[n*2]/*.Freq*/ = 0; }\n
  for (n = 0; n < D_CODES;  n++) { s.dyn_dtree[n*2]/*.Freq*/ = 0; }\n
  for (n = 0; n < BL_CODES; n++) { s.bl_tree[n*2]/*.Freq*/ = 0; }\n
\n
  s.dyn_ltree[END_BLOCK*2]/*.Freq*/ = 1;\n
  s.opt_len = s.static_len = 0;\n
  s.last_lit = s.matches = 0;\n
}\n
\n
\n
/* ===========================================================================\n
 * Flush the bit buffer and align the output on a byte boundary\n
 */\n
function bi_windup(s)\n
{\n
  if (s.bi_valid > 8) {\n
    put_short(s, s.bi_buf);\n
  } else if (s.bi_valid > 0) {\n
    //put_byte(s, (Byte)s->bi_buf);\n
    s.pending_buf[s.pending++] = s.bi_buf;\n
  }\n
  s.bi_buf = 0;\n
  s.bi_valid = 0;\n
}\n
\n
/* ===========================================================================\n
 * Copy a stored block, storing first the length and its\n
 * one\'s complement if requested.\n
 */\n
function copy_block(s, buf, len, header)\n
//DeflateState *s;\n
//charf    *buf;    /* the input data */\n
//unsigned len;     /* its length */\n
//int      header;  /* true if block header must be written */\n
{\n
  bi_windup(s);        /* align on byte boundary */\n
\n
  if (header) {\n
    put_short(s, len);\n
    put_short(s, ~len);\n
  }\n
//  while (len--) {\n
//    put_byte(s, *buf++);\n
//  }\n
  utils.arraySet(s.pending_buf, s.window, buf, len, s.pending);\n
  s.pending += len;\n
}\n
\n
/* ===========================================================================\n
 * Compares to subtrees, using the tree depth as tie breaker when\n
 * the subtrees have equal frequency. This minimizes the worst case length.\n
 */\n
function smaller(tree, n, m, depth) {\n
  var _n2 = n*2;\n
  var _m2 = m*2;\n
  return (tree[_n2]/*.Freq*/ < tree[_m2]/*.Freq*/ ||\n
         (tree[_n2]/*.Freq*/ === tree[_m2]/*.Freq*/ && depth[n] <= depth[m]));\n
}\n
\n
/* ===========================================================================\n
 * Restore the heap property by moving down the tree starting at node k,\n
 * exchanging a node with the smallest of its two sons if necessary, stopping\n
 * when the heap property is re-established (each father smaller than its\n
 * two sons).\n
 */\n
function pqdownheap(s, tree, k)\n
//    deflate_state *s;\n
//    ct_data *tree;  /* the tree to restore */\n
//    int k;               /* node to move down */\n
{\n
  var v = s.heap[k];\n
  var j = k << 1;  /* left son of k */\n
  while (j <= s.heap_len) {\n
    /* Set j to the smallest of the two sons: */\n
    if (j < s.heap_len &&\n
      smaller(tree, s.heap[j+1], s.heap[j], s.depth)) {\n
      j++;\n
    }\n
    /* Exit if v is smaller than both sons */\n
    if (smaller(tree, v, s.heap[j], s.depth)) { break; }\n
\n
    /* Exchange v with the smallest son */\n
    s.heap[k] = s.heap[j];\n
    k = j;\n
\n
    /* And continue down the tree, setting j to the left son of k */\n
    j <<= 1;\n
  }\n
  s.heap[k] = v;\n
}\n
\n
\n
// inlined manually\n
// var SMALLEST = 1;\n
\n
/* ===========================================================================\n
 * Send the block data compressed using the given Huffman trees\n
 */\n
function compress_block(s, ltree, dtree)\n
//    deflate_state *s;\n
//    const ct_data *ltree; /* literal tree */\n
//    const ct_data *dtree; /* distance tree */\n
{\n
  var dist;           /* distance of matched string */\n
  var lc;             /* match length or unmatched char (if dist == 0) */\n
  var lx = 0;         /* running index in l_buf */\n
  var code;           /* the code to send */\n
  var extra;          /* number of extra bits to send */\n
\n
  if (s.last_lit !== 0) {\n
    do {\n
      dist = (s.pending_buf[s.d_buf + lx*2] << 8) | (s.pending_buf[s.d_buf + lx*2 + 1]);\n
      lc = s.pending_buf[s.l_buf + lx];\n
      lx++;\n
\n
      if (dist === 0) {\n
        send_code(s, lc, ltree); /* send a literal byte */\n
        //Tracecv(isgraph(lc), (stderr," \'%c\' ", lc));\n
      } else {\n
        /* Here, lc is the match length - MIN_MATCH */\n
        code = _length_code[lc];\n
        send_code(s, code+LITERALS+1, ltree); /* send the length code */\n
        extra = extra_lbits[code];\n
        if (extra !== 0) {\n
          lc -= base_length[code];\n
          send_bits(s, lc, extra);       /* send the extra length bits */\n
        }\n
        dist--; /* dist is now the match distance - 1 */\n
        code = d_code(dist);\n
        //Assert (code < D_CODES, "bad d_code");\n
\n
        send_code(s, code, dtree);       /* send the distance code */\n
        extra = extra_dbits[code];\n
        if (extra !== 0) {\n
          dist -= base_dist[code];\n
          send_bits(s, dist, extra);   /* send the extra distance bits */\n
        }\n
      } /* literal or match pair ? */\n
\n
      /* Check that the overlay between pending_buf and d_buf+l_buf is ok: */\n
      //Assert((uInt)(s->pending) < s->lit_bufsize + 2*lx,\n
      //       "pendingBuf overflow");\n
\n
    } while (lx < s.last_lit);\n
  }\n
\n
  send_code(s, END_BLOCK, ltree);\n
}\n
\n
\n
/* ===========================================================================\n
 * Construct one Huffman tree and assigns the code bit strings and lengths.\n
 * Update the total bit length for the current block.\n
 * IN assertion: the field freq is set for all tree elements.\n
 * OUT assertions: the fields len and code are set to the optimal bit length\n
 *     and corresponding code. The length opt_len is updated; static_len is\n
 *     also updated if stree is not null. The field max_code is set.\n
 */\n
function build_tree(s, desc)\n
//    deflate_state *s;\n
//    tree_desc *desc; /* the tree descriptor */\n
{\n
  var tree     = desc.dyn_tree;\n
  var stree    = desc.stat_desc.static_tree;\n
  var has_stree = desc.stat_desc.has_stree;\n
  var elems    = desc.stat_desc.elems;\n
  var n, m;          /* iterate over heap elements */\n
  var max_code = -1; /* largest code with non zero frequency */\n
  var node;          /* new node being created */\n
\n
  /* Construct the initial heap, with least frequent element in\n
   * heap[SMALLEST]. The sons of heap[n] are heap[2*n] and heap[2*n+1].\n
   * heap[0] is not used.\n
   */\n
  s.heap_len = 0;\n
  s.heap_max = HEAP_SIZE;\n
\n
  for (n = 0; n < elems; n++) {\n
    if (tree[n * 2]/*.Freq*/ !== 0) {\n
      s.heap[++s.heap_len] = max_code = n;\n
      s.depth[n] = 0;\n
\n
    } else {\n
      tree[n*2 + 1]/*.Len*/ = 0;\n
    }\n
  }\n
\n
  /* The pkzip format requires that at least one distance code exists,\n
   * and that at least one bit should be sent even if there is only one\n
   * possible code. So to avoid special checks later on we force at least\n
   * two codes of non zero frequency.\n
   */\n
  while (s.heap_len < 2) {\n
    node = s.heap[++s.heap_len] = (max_code < 2 ? ++max_code : 0);\n
    tree[node * 2]/*.Freq*/ = 1;\n
    s.depth[node] = 0;\n
    s.opt_len--;\n
\n
    if (has_stree) {\n
      s.static_len -= stree[node*2 + 1]/*.Len*/;\n
    }\n
    /* node is 0 or 1 so it does not have extra bits */\n
  }\n
  desc.max_code = max_code;\n
\n
  /* The elements heap[heap_len/2+1 .. heap_len] are leaves of the tree,\n
   * establish sub-heaps of increasing lengths:\n
   */\n
  for (n = (s.heap_len >> 1/*int /2*/); n >= 1; n--) { pqdownheap(s, tree, n); }\n
\n
  /* Construct the Huffman tree by repeatedly combining the least two\n
   * frequent nodes.\n
   */\n
  node = elems;              /* next internal node of the tree */\n
  do {\n
    //pqremove(s, tree, n);  /* n = node of least frequency */\n
    /*** pqremove ***/\n
    n = s.heap[1/*SMALLEST*/];\n
    s.heap[1/*SMALLEST*/] = s.heap[s.heap_len--];\n
    pqdownheap(s, tree, 1/*SMALLEST*/);\n
    /***/\n
\n
    m = s.heap[1/*SMALLEST*/]; /* m = node of next least frequency */\n
\n
    s.heap[--s.heap_max] = n; /* keep the nodes sorted by frequency */\n
    s.heap[--s.heap_max] = m;\n
\n
    /* Create a new node father of n and m */\n
    tree[node * 2]/*.Freq*/ = tree[n * 2]/*.Freq*/ + tree[m * 2]/*.Freq*/;\n
    s.depth[node] = (s.depth[n] >= s.depth[m] ? s.depth[n] : s.depth[m]) + 1;\n
    tree[n*2 + 1]/*.Dad*/ = tree[m*2 + 1]/*.Dad*/ = node;\n
\n
    /* and insert the new node in the heap */\n
    s.heap[1/*SMALLEST*/] = node++;\n
    pqdownheap(s, tree, 1/*SMALLEST*/);\n
\n
  } while (s.heap_len >= 2);\n
\n
  s.heap[--s.heap_max] = s.heap[1/*SMALLEST*/];\n
\n
  /* At this point, the fields freq and dad are set. We can now\n
   * generate the bit lengths.\n
   */\n
  gen_bitlen(s, desc);\n
\n
  /* The field len is now set, we can generate the bit codes */\n
  gen_codes(tree, max_code, s.bl_count);\n
}\n
\n
\n
/* ===========================================================================\n
 * Scan a literal or distance tree to determine the frequencies of the codes\n
 * in the bit length tree.\n
 */\n
function scan_tree(s, tree, max_code)\n
//    deflate_state *s;\n
//    ct_data *tree;   /* the tree to be scanned */\n
//    int max_code;    /* and its largest code of non zero frequency */\n
{\n
  var n;                     /* iterates over all tree elements */\n
  var prevlen = -1;          /* last emitted length */\n
  var curlen;                /* length of current code */\n
\n
  var nextlen = tree[0*2 + 1]/*.Len*/; /* length of next code */\n
\n
  var count = 0;             /* repeat count of the current code */\n
  var max_count = 7;         /* max repeat count */\n
  var min_count = 4;         /* min repeat count */\n
\n
  if (nextlen === 0) {\n
    max_count = 138;\n
    min_count = 3;\n
  }\n
  tree[(max_code+1)*2 + 1]/*.Len*/ = 0xffff; /* guard */\n
\n
  for (n = 0; n <= max_code; n++) {\n
    curlen = nextlen;\n
    nextlen = tree[(n+1)*2 + 1]/*.Len*/;\n
\n
    if (++count < max_count && curlen === nextlen) {\n
      continue;\n
\n
    } else if (count < min_count) {\n
      s.bl_tree[curlen * 2]/*.Freq*/ += count;\n
\n
    } else if (curlen !== 0) {\n
\n
      if (curlen !== prevlen) { s.bl_tree[curlen * 2]/*.Freq*/++; }\n
      s.bl_tree[REP_3_6*2]/*.Freq*/++;\n
\n
    } else if (count <= 10) {\n
      s.bl_tree[REPZ_3_10*2]/*.Freq*/++;\n
\n
    } else {\n
      s.bl_tree[REPZ_11_138*2]/*.Freq*/++;\n
    }\n
\n
    count = 0;\n
    prevlen = curlen;\n
\n
    if (nextlen === 0) {\n
      max_count = 138;\n
      min_count = 3;\n
\n
    } else if (curlen === nextlen) {\n
      max_count = 6;\n
      min_count = 3;\n
\n
    } else {\n
      max_count = 7;\n
      min_count = 4;\n
    }\n
  }\n
}\n
\n
\n
/* ===========================================================================\n
 * Send a literal or distance tree in compressed form, using the codes in\n
 * bl_tree.\n
 */\n
function send_tree(s, tree, max_code)\n
//    deflate_state *s;\n
//    ct_data *tree; /* the tree to be scanned */\n
//    int max_code;       /* and its largest code of non zero frequency */\n
{\n
  var n;                     /* iterates over all tree elements */\n
  var prevlen = -1;          /* last emitted length */\n
  var curlen;                /* length of current code */\n
\n
  var nextlen = tree[0*2 + 1]/*.Len*/; /* length of next code */\n
\n
  var count = 0;             /* repeat count of the current code */\n
  var max_count = 7;         /* max repeat count */\n
  var min_count = 4;         /* min repeat count */\n
\n
  /* tree[max_code+1].Len = -1; */  /* guard already set */\n
  if (nextlen === 0) {\n
    max_count = 138;\n
    min_count = 3;\n
  }\n
\n
  for (n = 0; n <= max_code; n++) {\n
    curlen = nextlen;\n
    nextlen = tree[(n+1)*2 + 1]/*.Len*/;\n
\n
    if (++count < max_count && curlen === nextlen) {\n
      continue;\n
\n
    } else if (count < min_count) {\n
      do { send_code(s, curlen, s.bl_tree); } while (--count !== 0);\n
\n
    } else if (curlen !== 0) {\n
      if (curlen !== prevlen) {\n
        send_code(s, curlen, s.bl_tree);\n
        count--;\n
      }\n
      //Assert(count >= 3 && count <= 6, " 3_6?");\n
      send_code(s, REP_3_6, s.bl_tree);\n
      send_bits(s, count-3, 2);\n
\n
    } else if (count <= 10) {\n
      send_code(s, REPZ_3_10, s.bl_tree);\n
      send_bits(s, count-3, 3);\n
\n
    } else {\n
      send_code(s, REPZ_11_138, s.bl_tree);\n
      send_bits(s, count-11, 7);\n
    }\n
\n
    count = 0;\n
    prevlen = curlen;\n
    if (nextlen === 0) {\n
      max_count = 138;\n
      min_count = 3;\n
\n
    } else if (curlen === nextlen) {\n
      max_count = 6;\n
      min_count = 3;\n
\n
    } else {\n
      max_count = 7;\n
      min_count = 4;\n
    }\n
  }\n
}\n
\n
\n
/* ===========================================================================\n
 * Construct the Huffman tree for the bit lengths and return the index in\n
 * bl_order of the last bit length code to send.\n
 */\n
function build_bl_tree(s) {\n
  var max_blindex;  /* index of last bit length code of non zero freq */\n
\n
  /* Determine the bit length frequencies for literal and distance trees */\n
  scan_tree(s, s.dyn_ltree, s.l_desc.max_code);\n
  scan_tree(s, s.dyn_dtree, s.d_desc.max_code);\n
\n
  /* Build the bit length tree: */\n
  build_tree(s, s.bl_desc);\n
  /* opt_len now includes the length of the tree representations, except\n
   * the lengths of the bit lengths codes and the 5+5+4 bits for the counts.\n
   */\n
\n
  /* Determine the number of bit length codes to send. The pkzip format\n
   * requires that at least 4 bit length codes be sent. (appnote.txt says\n
   * 3 but the actual value used is 4.)\n
   */\n
  for (max_blindex = BL_CODES-1; max_blindex >= 3; max_blindex--) {\n
    if (s.bl_tree[bl_order[max_blindex]*2 + 1]/*.Len*/ !== 0) {\n
      break;\n
    }\n
  }\n
  /* Update opt_len to include the bit length tree and counts */\n
  s.opt_len += 3*(max_blindex+1) + 5+5+4;\n
  //Tracev((stderr, "\\ndyn trees: dyn %ld, stat %ld",\n
  //        s->opt_len, s->static_len));\n
\n
  return max_blindex;\n
}\n
\n
\n
/* ===========================================================================\n
 * Send the header for a block using dynamic Huffman trees: the counts, the\n
 * lengths of the bit length codes, the literal tree and the distance tree.\n
 * IN assertion: lcodes >= 257, dcodes >= 1, blcodes >= 4.\n
 */\n
function send_all_trees(s, lcodes, dcodes, blcodes)\n
//    deflate_state *s;\n
//    int lcodes, dcodes, blcodes; /* number of codes for each tree */\n
{\n
  var rank;                    /* index in bl_order */\n
\n
  //Assert (lcodes >= 257 && dcodes >= 1 && blcodes >= 4, "not enough codes");\n
  //Assert (lcodes <= L_CODES && dcodes <= D_CODES && blcodes <= BL_CODES,\n
  //        "too many codes");\n
  //Tracev((stderr, "\\nbl counts: "));\n
  send_bits(s, lcodes-257, 5); /* not +255 as stated in appnote.txt */\n
  send_bits(s, dcodes-1,   5);\n
  send_bits(s, blcodes-4,  4); /* not -3 as stated in appnote.txt */\n
  for (rank = 0; rank < blcodes; rank++) {\n
    //Tracev((stderr, "\\nbl code %2d ", bl_order[rank]));\n
    send_bits(s, s.bl_tree[bl_order[rank]*2 + 1]/*.Len*/, 3);\n
  }\n
  //Tracev((stderr, "\\nbl tree: sent %ld", s->bits_sent));\n
\n
  send_tree(s, s.dyn_ltree, lcodes-1); /* literal tree */\n
  //Tracev((stderr, "\\nlit tree: sent %ld", s->bits_sent));\n
\n
  send_tree(s, s.dyn_dtree, dcodes-1); /* distance tree */\n
  //Tracev((stderr, "\\ndist tree: sent %ld", s->bits_sent));\n
}\n
\n
\n
/* ===========================================================================\n
 * Check if the data type is TEXT or BINARY, using the following algorithm:\n
 * - TEXT if the two conditions below are satisfied:\n
 *    a) There are no non-portable control characters belonging to the\n
 *       "black list" (0..6, 14..25, 28..31).\n
 *    b) There is at least one printable character belonging to the\n
 *       "white list" (9 {TAB}, 10 {LF}, 13 {CR}, 32..255).\n
 * - BINARY otherwise.\n
 * - The following partially-portable control characters form a\n
 *   "gray list" that is ignored in this detection algorithm:\n
 *   (7 {BEL}, 8 {BS}, 11 {VT}, 12 {FF}, 26 {SUB}, 27 {ESC}).\n
 * IN assertion: the fields Freq of dyn_ltree are set.\n
 */\n
function detect_data_type(s) {\n
  /* black_mask is the bit mask of black-listed bytes\n
   * set bits 0..6, 14..25, and 28..31\n
   * 0xf3ffc07f = binary 11110011111111111100000001111111\n
   */\n
  var black_mask = 0xf3ffc07f;\n
  var n;\n
\n
  /* Check for non-textual ("black-listed") bytes. */\n
  for (n = 0; n <= 31; n++, black_mask >>>= 1) {\n
    if ((black_mask & 1) && (s.dyn_ltree[n*2]/*.Freq*/ !== 0)) {\n
      return Z_BINARY;\n
    }\n
  }\n
\n
  /* Check for textual ("white-listed") bytes. */\n
  if (s.dyn_ltree[9 * 2]/*.Freq*/ !== 0 || s.dyn_ltree[10 * 2]/*.Freq*/ !== 0 ||\n
      s.dyn_ltree[13 * 2]/*.Freq*/ !== 0) {\n
    return Z_TEXT;\n
  }\n
  for (n = 32; n < LITERALS; n++) {\n
    if (s.dyn_ltree[n * 2]/*.Freq*/ !== 0) {\n
      return Z_TEXT;\n
    }\n
  }\n
\n
  /* There are no "black-listed" or "white-listed" bytes:\n
   * this stream either is empty or has tolerated ("gray-listed") bytes only.\n
   */\n
  return Z_BINARY;\n
}\n
\n
\n
var static_init_done = false;\n
\n
/* ===========================================================================\n
 * Initialize the tree data structures for a new zlib stream.\n
 */\n
function _tr_init(s)\n
{\n
\n
  if (!static_init_done) {\n
    tr_static_init();\n
    static_init_done = true;\n
  }\n
\n
  s.l_desc  = new TreeDesc(s.dyn_ltree, static_l_desc);\n
  s.d_desc  = new TreeDesc(s.dyn_dtree, static_d_desc);\n
  s.bl_desc = new TreeDesc(s.bl_tree, static_bl_desc);\n
\n
  s.bi_buf = 0;\n
  s.bi_valid = 0;\n
\n
  /* Initialize the first block of the first file: */\n
  init_block(s);\n
}\n
\n
\n
/* ===========================================================================\n
 * Send a stored block\n
 */\n
function _tr_stored_block(s, buf, stored_len, last)\n
//DeflateState *s;\n
//charf *buf;       /* input block */\n
//ulg stored_len;   /* length of input block */\n
//int last;         /* one if this is the last block for a file */\n
{\n
  send_bits(s, (STORED_BLOCK<<1)+(last ? 1 : 0), 3);    /* send block type */\n
  copy_block(s, buf, stored_len, true); /* with header */\n
}\n
\n
\n
/* ===========================================================================\n
 * Send one empty static block to give enough lookahead for inflate.\n
 * This takes 10 bits, of which 7 may remain in the bit buffer.\n
 */\n
function _tr_align(s) {\n
  send_bits(s, STATIC_TREES<<1, 3);\n
  send_code(s, END_BLOCK, static_ltree);\n
  bi_flush(s);\n
}\n
\n
\n
/* ===========================================================================\n
 * Determine the best encoding for the current block: dynamic trees, static\n
 * trees or store, and output the encoded block to the zip file.\n
 */\n
function _tr_flush_block(s, buf, stored_len, last)\n
//DeflateState *s;\n
//charf *buf;       /* input block, or NULL if too old */\n
//ulg stored_len;   /* length of input block */\n
//int last;         /* one if this is the last block for a file */\n
{\n
  var opt_lenb, static_lenb;  /* opt_len and static_len in bytes */\n
  var max_blindex = 0;        /* index of last bit length code of non zero freq */\n
\n
  /* Build the Huffman trees unless a stored block is forced */\n
  if (s.level > 0) {\n
\n
    /* Check if the file is binary or text */\n
    if (s.strm.data_type === Z_UNKNOWN) {\n
      s.strm.data_type = detect_data_type(s);\n
    }\n
\n
    /* Construct the literal and distance trees */\n
    build_tree(s, s.l_desc);\n
    // Tracev((stderr, "\\nlit data: dyn %ld, stat %ld", s->opt_len,\n
    //        s->static_len));\n
\n
    build_tree(s, s.d_desc);\n
    // Tracev((stderr, "\\ndist data: dyn %ld, stat %ld", s->opt_len,\n
    //        s->static_len));\n
    /* At this point, opt_len and static_len are the total bit lengths of\n
     * the compressed block data, excluding the tree representations.\n
     */\n
\n
    /* Build the bit length tree for the above two trees, and get the index\n
     * in bl_order of the last bit length code to send.\n
     */\n
    max_blindex = build_bl_tree(s);\n
\n
    /* Determine the best encoding. Compute the block lengths in bytes. */\n
    opt_lenb = (s.opt_len+3+7) >>> 3;\n
    static_lenb = (s.static_len+3+7) >>> 3;\n
\n
    // Tracev((stderr, "\\nopt %lu(%lu) stat %lu(%lu) stored %lu lit %u ",\n
    //        opt_lenb, s->opt_len, static_lenb, s->static_len, stored_len,\n
    //        s->last_lit));\n
\n
    if (static_lenb <= opt_lenb) { opt_lenb = static_lenb; }\n
\n
  } else {\n
    // Assert(buf != (char*)0, "lost buf");\n
    opt_lenb = static_lenb = stored_len + 5; /* force a stored block */\n
  }\n
\n
  if ((stored_len+4 <= opt_lenb) && (buf !== -1)) {\n
    /* 4: two words for the lengths */\n
\n
    /* The test buf != NULL is only necessary if LIT_BUFSIZE > WSIZE.\n
     * Otherwise we can\'t have processed more than WSIZE input bytes since\n
     * the last block flush, because compression would have been\n
     * successful. If LIT_BUFSIZE <= WSIZE, it is never too late to\n
     * transform a block into a stored block.\n
     */\n
    _tr_stored_block(s, buf, stored_len, last);\n
\n
  } else if (s.strategy === Z_FIXED || static_lenb === opt_lenb) {\n
\n
    send_bits(s, (STATIC_TREES<<1) + (last ? 1 : 0), 3);\n
    compress_block(s, static_ltree, static_dtree);\n
\n
  } else {\n
    send_bits(s, (DYN_TREES<<1) + (last ? 1 : 0), 3);\n
    send_all_trees(s, s.l_desc.max_code+1, s.d_desc.max_code+1, max_blindex+1);\n
    compress_block(s, s.dyn_ltree, s.dyn_dtree);\n
  }\n
  // Assert (s->compressed_len == s->bits_sent, "bad compressed size");\n
  /* The above check is made mod 2^32, for files larger than 512 MB\n
   * and uLong implemented on 32 bits.\n
   */\n
  init_block(s);\n
\n
  if (last) {\n
    bi_windup(s);\n
  }\n
  // Tracev((stderr,"\\ncomprlen %lu(%lu) ", s->compressed_len>>3,\n
  //       s->compressed_len-7*last));\n
}\n
\n
/* ===========================================================================\n
 * Save the match info and tally the frequency counts. Return true if\n
 * the current block must be flushed.\n
 */\n
function _tr_tally(s, dist, lc)\n
//    deflate_state *s;\n
//    unsigned dist;  /* distance of matched string */\n
//    unsigned lc;    /* match length-MIN_MATCH or unmatched char (if dist==0) */\n
{\n
  //var out_length, in_length, dcode;\n
\n
  s.pending_buf[s.d_buf + s.last_lit * 2]     = (dist >>> 8) & 0xff;\n
  s.pending_buf[s.d_buf + s.last_lit * 2 + 1] = dist & 0xff;\n
\n
  s.pending_buf[s.l_buf + s.last_lit] = lc & 0xff;\n
  s.last_lit++;\n
\n
  if (dist === 0) {\n
    /* lc is the unmatched char */\n
    s.dyn_ltree[lc*2]/*.Freq*/++;\n
  } else {\n
    s.matches++;\n
    /* Here, lc is the match length - MIN_MATCH */\n
    dist--;             /* dist = match distance - 1 */\n
    //Assert((ush)dist < (ush)MAX_DIST(s) &&\n
    //       (ush)lc <= (ush)(MAX_MATCH-MIN_MATCH) &&\n
    //       (ush)d_code(dist) < (ush)D_CODES,  "_tr_tally: bad match");\n
\n
    s.dyn_ltree[(_length_code[lc]+LITERALS+1) * 2]/*.Freq*/++;\n
    s.dyn_dtree[d_code(dist) * 2]/*.Freq*/++;\n
  }\n
\n
// (!) This block is disabled in zlib defailts,\n
// don\'t enable it for binary compatibility\n
\n
//#ifdef TRUNCATE_BLOCK\n
//  /* Try to guess if it is profitable to stop the current block here */\n
//  if ((s.last_lit & 0x1fff) === 0 && s.level > 2) {\n
//    /* Compute an upper bound for the compressed length */\n
//    out_length = s.last_lit*8;\n
//    in_length = s.strstart - s.block_start;\n
//\n
//    for (dcode = 0; dcode < D_CODES; dcode++) {\n
//      out_length += s.dyn_dtree[dcode*2]/*.Freq*/ * (5 + extra_dbits[dcode]);\n
//    }\n
//    out_length >>>= 3;\n
//    //Tracev((stderr,"\\nlast_lit %u, in %ld, out ~%ld(%ld%%) ",\n
//    //       s->last_lit, in_length, out_length,\n
//    //       100L - out_length*100L/in_length));\n
//    if (s.matches < (s.last_lit>>1)/*int /2*/ && out_length < (in_length>>1)/*int /2*/) {\n
//      return true;\n
//    }\n
//  }\n
//#endif\n
\n
  return (s.last_lit === s.lit_bufsize-1);\n
  /* We avoid equality with lit_bufsize because of wraparound at 64K\n
   * on 16 bit machines and because stored blocks are restricted to\n
   * 64K-1 bytes.\n
   */\n
}\n
\n
exports._tr_init  = _tr_init;\n
exports._tr_stored_block = _tr_stored_block;\n
exports._tr_flush_block  = _tr_flush_block;\n
exports._tr_tally = _tr_tally;\n
exports._tr_align = _tr_align;\n
},{"../utils/common":27}],39:[function(_dereq_,module,exports){\n
\'use strict\';\n
\n
\n
function ZStream() {\n
  /* next input byte */\n
  this.input = null; // JS specific, because we have no pointers\n
  this.next_in = 0;\n
  /* number of bytes available at input */\n
  this.avail_in = 0;\n
  /* total number of input bytes read so far */\n
  this.total_in = 0;\n
  /* next output byte should be put there */\n
  this.output = null; // JS specific, because we have no pointers\n
  this.next_out = 0;\n
  /* remaining free space at output */\n
  this.avail_out = 0;\n
  /* total number of bytes output so far */\n
  this.total_out = 0;\n
  /* last error message, NULL if no error */\n
  this.msg = \'\'/*Z_NULL*/;\n
  /* not visible by applications */\n
  this.state = null;\n
  /* best guess about the data type: binary or text */\n
  this.data_type = 2/*Z_UNKNOWN*/;\n
  /* adler32 value of the uncompressed data */\n
  this.adler = 0;\n
}\n
\n
module.exports = ZStream;\n
},{}]},{},[9])\n
(9)\n
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
