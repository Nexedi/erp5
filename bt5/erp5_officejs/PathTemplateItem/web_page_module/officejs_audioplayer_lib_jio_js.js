(function (dependencies, module) {
    if (typeof define === 'function' && define.amd) {
        return define(dependencies, module);
    }
    if (typeof exports === 'object') {
        return module(exports);
    }
    module(window);
}(['exports'], function (window) {
/* A JavaScript implementation of the Secure Hash Algorithm, SHA-256
 * Version 0.3 Copyright Angel Marin 2003-2004 - http://anmar.eu.org/
 * Distributed under the BSD License
 * Some bits taken from Paul Johnston's SHA-1 implementation
 */
(function () {
    var chrsz = 8;  /* bits per input character. 8 - ASCII; 16 - Unicode  */
    function safe_add (x, y) {
        var lsw = (x & 0xFFFF) + (y & 0xFFFF);
        var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
        return (msw << 16) | (lsw & 0xFFFF);
    }
    function S (X, n) {return ( X >>> n ) | (X << (32 - n));}
    function R (X, n) {return ( X >>> n );}
    function Ch(x, y, z) {return ((x & y) ^ ((~x) & z));}
    function Maj(x, y, z) {return ((x & y) ^ (x & z) ^ (y & z));}
    function Sigma0256(x) {return (S(x, 2) ^ S(x, 13) ^ S(x, 22));}
    function Sigma1256(x) {return (S(x, 6) ^ S(x, 11) ^ S(x, 25));}
    function Gamma0256(x) {return (S(x, 7) ^ S(x, 18) ^ R(x, 3));}
    function Gamma1256(x) {return (S(x, 17) ^ S(x, 19) ^ R(x, 10));}
    function newArray (n) {
        var a = [];
        for (;n>0;n--) {
            a.push(undefined);
        }
        return a;
    }
    function core_sha256 (m, l) {
        var K = [0x428A2F98,0x71374491,0xB5C0FBCF,0xE9B5DBA5,0x3956C25B,0x59F111F1,0x923F82A4,0xAB1C5ED5,0xD807AA98,0x12835B01,0x243185BE,0x550C7DC3,0x72BE5D74,0x80DEB1FE,0x9BDC06A7,0xC19BF174,0xE49B69C1,0xEFBE4786,0xFC19DC6,0x240CA1CC,0x2DE92C6F,0x4A7484AA,0x5CB0A9DC,0x76F988DA,0x983E5152,0xA831C66D,0xB00327C8,0xBF597FC7,0xC6E00BF3,0xD5A79147,0x6CA6351,0x14292967,0x27B70A85,0x2E1B2138,0x4D2C6DFC,0x53380D13,0x650A7354,0x766A0ABB,0x81C2C92E,0x92722C85,0xA2BFE8A1,0xA81A664B,0xC24B8B70,0xC76C51A3,0xD192E819,0xD6990624,0xF40E3585,0x106AA070,0x19A4C116,0x1E376C08,0x2748774C,0x34B0BCB5,0x391C0CB3,0x4ED8AA4A,0x5B9CCA4F,0x682E6FF3,0x748F82EE,0x78A5636F,0x84C87814,0x8CC70208,0x90BEFFFA,0xA4506CEB,0xBEF9A3F7,0xC67178F2];
        var HASH = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19];
        var W = newArray(64);
        var a, b, c, d, e, f, g, h, i, j;
        var T1, T2;
        /* append padding */
        m[l >> 5] |= 0x80 << (24 - l % 32);
        m[((l + 64 >> 9) << 4) + 15] = l;
        for ( var i = 0; i<m.length; i+=16 ) {
            a = HASH[0]; b = HASH[1]; c = HASH[2]; d = HASH[3];
            e = HASH[4]; f = HASH[5]; g = HASH[6]; h = HASH[7];
            for ( var j = 0; j<64; j++) {
                if (j < 16) {
                    W[j] = m[j + i];
                } else {
                    W[j] = safe_add(safe_add(safe_add(Gamma1256(
                        W[j - 2]), W[j - 7]), Gamma0256(W[j - 15])), W[j - 16]);
                }
                T1 = safe_add(safe_add(safe_add(
                    safe_add(h, Sigma1256(e)), Ch(e, f, g)), K[j]), W[j]);
                T2 = safe_add(Sigma0256(a), Maj(a, b, c));
                h = g; g = f; f = e; e = safe_add(d, T1);
                d = c; c = b; b = a; a = safe_add(T1, T2);
            }
            HASH[0] = safe_add(a, HASH[0]); HASH[1] = safe_add(b, HASH[1]);
            HASH[2] = safe_add(c, HASH[2]); HASH[3] = safe_add(d, HASH[3]);
            HASH[4] = safe_add(e, HASH[4]); HASH[5] = safe_add(f, HASH[5]);
            HASH[6] = safe_add(g, HASH[6]); HASH[7] = safe_add(h, HASH[7]);
        }
        return HASH;
    }
    function str2binb (str) {
        var bin = Array();
        var mask = (1 << chrsz) - 1;
        for(var i = 0; i < str.length * chrsz; i += chrsz)
            bin[i>>5] |= (str.charCodeAt(i / chrsz) & mask) << (24 - i%32);
        return bin;
    }
    function binb2hex (binarray) {
        var hexcase = 0; /* hex output format. 0 - lowercase; 1 - uppercase */
        var hex_tab = hexcase ? "0123456789ABCDEF" : "0123456789abcdef";
        var str = "";
        for (var i = 0; i < binarray.length * 4; i++) {
            str += hex_tab.charAt((binarray[i>>2] >> ((3 - i%4)*8+4)) & 0xF) +
                hex_tab.charAt((binarray[i>>2] >> ((3 - i%4)*8  )) & 0xF);
        }
        return str;
    }
    function hex_sha256(s){
        return binb2hex(core_sha256(str2binb(s),s.length * chrsz));
    }
    window.hex_sha256 = hex_sha256;
}());
}));
;(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  window.jIO = {};
  module(window.jIO, RSVP, {hex_sha256: hex_sha256});
}(['exports', 'rsvp', 'sha256'], function (exports, RSVP, sha256) {
  "use strict";

  var hex_sha256 = sha256.hex_sha256;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global uniqueJSONStringify, methodType */

var defaults = {}, constants = {};

defaults.storage_types = {};

constants.dcmi_types = {
  'Collection': 'Collection',
  'Dataset': 'Dataset',
  'Event': 'Event',
  'Image': 'Image',
  'InteractiveResource': 'InteractiveResource',
  'MovingImage': 'MovingImage',
  'PhysicalObject': 'PhysicalObject',
  'Service': 'Service',
  'Software': 'Software',
  'Sound': 'Sound',
  'StillImage': 'StillImage',
  'Text': 'Text'
};
// if (dcmi_types.Collection === 'Collection') { is a DCMI type }
// if (typeof dcmi_types[name] === 'string')   { is a DCMI type }

constants.http_status_text = {
  "0": "Unknown",
  "550": "Internal JIO Error",
  "551": "Internal Storage Error",
  "Unknown": "Unknown",
  "Internal JIO Error": "Internal JIO Error",
  "Internal Storage Error": "Internal Storage Error",
  "unknown": "Unknown",
  "internal_jio_error": "Internal JIO Error",
  "internal_storage_error": "Internal Storage Error",

  "200": "Ok",
  "201": "Created",
  "204": "No Content",
  "205": "Reset Content",
  "206": "Partial Content",
  "304": "Not Modified",
  "400": "Bad Request",
  "401": "Unauthorized",
  "402": "Payment Required",
  "403": "Forbidden",
  "404": "Not Found",
  "405": "Method Not Allowed",
  "406": "Not Acceptable",
  "407": "Proxy Authentication Required",
  "408": "Request Timeout",
  "409": "Conflict",
  "410": "Gone",
  "411": "Length Required",
  "412": "Precondition Failed",
  "413": "Request Entity Too Large",
  "414": "Request-URI Too Long",
  "415": "Unsupported Media Type",
  "416": "Requested Range Not Satisfiable",
  "417": "Expectation Failed",
  "418": "I'm a teapot",
  "419": "Authentication Timeout",
  "500": "Internal Server Error",
  "501": "Not Implemented",
  "502": "Bad Gateway",
  "503": "Service Unavailable",
  "504": "Gateway Timeout",
  "507": "Insufficient Storage",

  "Ok": "Ok",
  "OK": "Ok",
  "Created": "Created",
  "No Content": "No Content",
  "Reset Content": "Reset Content",
  "Partial Content": "Partial Content",
  "Not Modified": "Not Modified",
  "Bad Request": "Bad Request",
  "Unauthorized": "Unauthorized",
  "Payment Required": "Payment Required",
  "Forbidden": "Forbidden",
  "Not Found": "Not Found",
  "Method Not Allowed": "Method Not Allowed",
  "Not Acceptable": "Not Acceptable",
  "Proxy Authentication Required": "Proxy Authentication Required",
  "Request Timeout": "Request Timeout",
  "Conflict": "Conflict",
  "Gone": "Gone",
  "Length Required": "Length Required",
  "Precondition Failed": "Precondition Failed",
  "Request Entity Too Large": "Request Entity Too Large",
  "Request-URI Too Long": "Request-URI Too Long",
  "Unsupported Media Type": "Unsupported Media Type",
  "Requested Range Not Satisfiable": "Requested Range Not Satisfiable",
  "Expectation Failed": "Expectation Failed",
  "I'm a teapot": "I'm a teapot",
  "Authentication Timeout": "Authentication Timeout",
  "Internal Server Error": "Internal Server Error",
  "Not Implemented": "Not Implemented",
  "Bad Gateway": "Bad Gateway",
  "Service Unavailable": "Service Unavailable",
  "Gateway Timeout": "Gateway Timeout",
  "Insufficient Storage": "Insufficient Storage",

  "ok": "Ok",
  "created": "Created",
  "no_content": "No Content",
  "reset_content": "Reset Content",
  "partial_content": "Partial Content",
  "not_modified": "Not Modified",
  "bad_request": "Bad Request",
  "unauthorized": "Unauthorized",
  "payment_required": "Payment Required",
  "forbidden": "Forbidden",
  "not_found": "Not Found",
  "method_not_allowed": "Method Not Allowed",
  "not_acceptable": "Not Acceptable",
  "proxy_authentication_required": "Proxy Authentication Required",
  "request_timeout": "Request Timeout",
  "conflict": "Conflict",
  "gone": "Gone",
  "length_required": "Length Required",
  "precondition_failed": "Precondition Failed",
  "request_entity_too_large": "Request Entity Too Large",
  "request-uri_too_long": "Request-URI Too Long",
  "unsupported_media_type": "Unsupported Media Type",
  "requested_range_not_satisfiable": "Requested Range Not Satisfiable",
  "expectation_failed": "Expectation Failed",
  "im_a_teapot": "I'm a teapot",
  "authentication_timeout": "Authentication Timeout",
  "internal_server_error": "Internal Server Error",
  "not_implemented": "Not Implemented",
  "bad_gateway": "Bad Gateway",
  "service_unavailable": "Service Unavailable",
  "gateway_timeout": "Gateway Timeout",
  "insufficient_storage": "Insufficient Storage"
};

constants.http_status = {
  "0": 0,
  "550": 550,
  "551": 551,
  "Unknown": 0,
  "Internal JIO Error": 550,
  "Internal Storage Error": 551,
  "unknown": 0,
  "internal_jio_error": 550,
  "internal_storage_error": 551,

  "200": 200,
  "201": 201,
  "204": 204,
  "205": 205,
  "206": 206,
  "304": 304,
  "400": 400,
  "401": 401,
  "402": 402,
  "403": 403,
  "404": 404,
  "405": 405,
  "406": 406,
  "407": 407,
  "408": 408,
  "409": 409,
  "410": 410,
  "411": 411,
  "412": 412,
  "413": 413,
  "414": 414,
  "415": 415,
  "416": 416,
  "417": 417,
  "418": 418,
  "419": 419,
  "500": 500,
  "501": 501,
  "502": 502,
  "503": 503,
  "504": 504,
  "507": 507,

  "Ok": 200,
  "OK": 200,
  "Created": 201,
  "No Content": 204,
  "Reset Content": 205,
  "Partial Content": 206,
  "Not Modified": 304,
  "Bad Request": 400,
  "Unauthorized": 401,
  "Payment Required": 402,
  "Forbidden": 403,
  "Not Found": 404,
  "Method Not Allowed": 405,
  "Not Acceptable": 406,
  "Proxy Authentication Required": 407,
  "Request Timeout": 408,
  "Conflict": 409,
  "Gone": 410,
  "Length Required": 411,
  "Precondition Failed": 412,
  "Request Entity Too Large": 413,
  "Request-URI Too Long": 414,
  "Unsupported Media Type": 415,
  "Requested Range Not Satisfiable": 416,
  "Expectation Failed": 417,
  "I'm a teapot": 418,
  "Authentication Timeout": 419,
  "Internal Server Error": 500,
  "Not Implemented": 501,
  "Bad Gateway": 502,
  "Service Unavailable": 503,
  "Gateway Timeout": 504,
  "Insufficient Storage": 507,

  "ok": 200,
  "created": 201,
  "no_content": 204,
  "reset_content": 205,
  "partial_content": 206,
  "not_modified": 304,
  "bad_request": 400,
  "unauthorized": 401,
  "payment_required": 402,
  "forbidden": 403,
  "not_found": 404,
  "method_not_allowed": 405,
  "not_acceptable": 406,
  "proxy_authentication_required": 407,
  "request_timeout": 408,
  "conflict": 409,
  "gone": 410,
  "length_required": 411,
  "precondition_failed": 412,
  "request_entity_too_large": 413,
  "request-uri_too_long": 414,
  "unsupported_media_type": 415,
  "requested_range_not_satisfiable": 416,
  "expectation_failed": 417,
  "im_a_teapot": 418,
  "authentication_timeout": 419,
  "internal_server_error": 500,
  "not_implemented": 501,
  "bad_gateway": 502,
  "service_unavailable": 503,
  "gateway_timeout": 504,
  "insufficient_storage": 507
};

constants.http_action = {
  "0": "error",
  "550": "error",
  "551": "error",
  "Unknown": "error",
  "Internal JIO Error": "error",
  "Internal Storage Error": "error",
  "unknown": "error",
  "internal_jio_error": "error",
  "internal_storage_error": "error",

  "200": "success",
  "201": "success",
  "204": "success",
  "205": "success",
  "206": "success",
  "304": "success",
  "400": "error",
  "401": "error",
  "402": "error",
  "403": "error",
  "404": "error",
  "405": "error",
  "406": "error",
  "407": "error",
  "408": "error",
  "409": "error",
  "410": "error",
  "411": "error",
  "412": "error",
  "413": "error",
  "414": "error",
  "415": "error",
  "416": "error",
  "417": "error",
  "418": "error",
  "419": "retry",
  "500": "retry",
  "501": "error",
  "502": "error",
  "503": "retry",
  "504": "retry",
  "507": "error",

  "Ok": "success",
  "OK": "success",
  "Created": "success",
  "No Content": "success",
  "Reset Content": "success",
  "Partial Content": "success",
  "Not Modified": "success",
  "Bad Request": "error",
  "Unauthorized": "error",
  "Payment Required": "error",
  "Forbidden": "error",
  "Not Found": "error",
  "Method Not Allowed": "error",
  "Not Acceptable": "error",
  "Proxy Authentication Required": "error",
  "Request Timeout": "error",
  "Conflict": "error",
  "Gone": "error",
  "Length Required": "error",
  "Precondition Failed": "error",
  "Request Entity Too Large": "error",
  "Request-URI Too Long": "error",
  "Unsupported Media Type": "error",
  "Requested Range Not Satisfiable": "error",
  "Expectation Failed": "error",
  "I'm a teapot": "error",
  "Authentication Timeout": "retry",
  "Internal Server Error": "retry",
  "Not Implemented": "error",
  "Bad Gateway": "error",
  "Service Unavailable": "retry",
  "Gateway Timeout": "retry",
  "Insufficient Storage": "error",

  "ok": "success",
  "created": "success",
  "no_content": "success",
  "reset_content": "success",
  "partial_content": "success",
  "not_modified": "success",
  "bad_request": "error",
  "unauthorized": "error",
  "payment_required": "error",
  "forbidden": "error",
  "not_found": "error",
  "method_not_allowed": "error",
  "not_acceptable": "error",
  "proxy_authentication_required": "error",
  "request_timeout": "error",
  "conflict": "error",
  "gone": "error",
  "length_required": "error",
  "precondition_failed": "error",
  "request_entity_too_large": "error",
  "request-uri_too_long": "error",
  "unsupported_media_type": "error",
  "requested_range_not_satisfiable": "error",
  "expectation_failed": "error",
  "im_a_teapot": "error",
  "authentication_timeout": "retry",
  "internal_server_error": "retry",
  "not_implemented": "error",
  "bad_gateway": "error",
  "service_unavailable": "retry",
  "gateway_timeout": "retry",
  "insufficient_storage": "error"
};

constants.content_type_re =
  /^([a-z]+\/[a-zA-Z0-9\+\-\.]+)(?:\s*;\s*charset\s*=\s*([a-zA-Z0-9\-]+))?$/;

/**
 * Function that does nothing
 */
constants.emptyFunction = function () {
  return;
};

defaults.job_rule_conditions = {};

/**
 * Adds some job rule conditions
 */
(function () {

  /**
   * Compare two jobs and test if they use the same storage description
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function sameStorageDescription(a, b) {
    return uniqueJSONStringify(a.storage_spec) ===
      uniqueJSONStringify(b.storage_spec);
  }

  /**
   * Compare two jobs and test if they are writers
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function areWriters(a, b) {
    return methodType(a.method) === 'writer' &&
      methodType(b.method) === 'writer';
  }

  /**
   * Compare two jobs and test if they use metadata only
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function useMetadataOnly(a, b) {
    if (['post', 'put', 'get', 'remove', 'allDocs'].indexOf(a.method) === -1) {
      return false;
    }
    if (['post', 'put', 'get', 'remove', 'allDocs'].indexOf(b.method) === -1) {
      return false;
    }
    return true;
  }

  /**
   * Compare two jobs and test if they are readers
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function areReaders(a, b) {
    return methodType(a.method) === 'reader' &&
      methodType(b.method) === 'reader';
  }

  /**
   * Compare two jobs and test if their methods are the same
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function sameMethod(a, b) {
    return a.method === b.method;
  }

  /**
   * Compare two jobs and test if their document ids are the same
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function sameDocumentId(a, b) {
    return a.kwargs._id === b.kwargs._id;
  }

  /**
   * Test if the jobs have a document id.
   *
   * @param  {Object} a The first job to test
   * @param  {Object} b The second job to test
   * @return {Boolean} True if ids exist, else false
   */
  function haveDocumentIds(a, b) {
    if (typeof a.kwargs._id !== "string" || a.kwargs._id === "") {
      return false;
    }
    if (typeof b.kwargs._id !== "string" || b.kwargs._id === "") {
      return false;
    }
    return true;
  }

  /**
   * Compare two jobs and test if their kwargs are equal
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function sameParameters(a, b) {
    return uniqueJSONStringify(a.kwargs) ===
      uniqueJSONStringify(b.kwargs);
  }

  /**
   * Compare two jobs and test if their options are equal
   *
   * @param  {Object} a The first job to compare
   * @param  {Object} b The second job to compare
   * @return {Boolean} True if equal, else false
   */
  function sameOptions(a, b) {
    return uniqueJSONStringify(a.options) ===
      uniqueJSONStringify(b.options);
  }

  defaults.job_rule_conditions = {
    "sameStorageDescription": sameStorageDescription,
    "areWriters": areWriters,
    "areReaders": areReaders,
    "useMetadataOnly": useMetadataOnly,
    "sameMethod": sameMethod,
    "sameDocumentId": sameDocumentId,
    "sameParameters": sameParameters,
    "sameOptions": sameOptions,
    "haveDocumentIds": haveDocumentIds
  };

}());

/*jslint indent: 2, maxlen: 80, nomen: true, sloppy: true */
/*global exports, Blob, FileReader, RSVP, hex_sha256, XMLHttpRequest,
  constants */

/**
 * Do not exports these tools unless they are not writable, not configurable.
 */

exports.util = {};

/**
 * Inherits the prototype methods from one constructor into another. The
 * prototype of `constructor` will be set to a new object created from
 * `superConstructor`.
 *
 * @param  {Function} constructor The constructor which inherits the super
 *   one
 * @param  {Function} superConstructor The super constructor
 */
function inherits(constructor, superConstructor) {
  constructor.super_ = superConstructor;
  constructor.prototype = Object.create(superConstructor.prototype, {
    "constructor": {
      "configurable": true,
      "enumerable": false,
      "writable": true,
      "value": constructor
    }
  });
}

/**
 * Clones jsonable object in depth
 *
 * @param  {A} object The jsonable object to clone
 * @return {A} The cloned object
 */
function jsonDeepClone(object) {
  var tmp = JSON.stringify(object);
  if (tmp === undefined) {
    return undefined;
  }
  return JSON.parse(tmp);
}
exports.util.jsonDeepClone = jsonDeepClone;

/**
 * Clones all native object in deep. Managed types: Object, Array, String,
 * Number, Boolean, Function, null.
 *
 * It can also clone object which are serializable, like Date.
 *
 * To make a class serializable, you need to implement the `toJSON` function
 * which returns a JSON representation of the object. The returned value is used
 * as first parameter of the object constructor.
 *
 * @param  {A} object The object to clone
 * @return {A} The cloned object
 */
function deepClone(object) {
  var i, cloned;
  if (Array.isArray(object)) {
    cloned = [];
    for (i = 0; i < object.length; i += 1) {
      cloned[i] = deepClone(object[i]);
    }
    return cloned;
  }
  if (object === null) {
    return null;
  }
  if (typeof object === 'object') {
    if (Object.getPrototypeOf(object) === Object.prototype) {
      cloned = {};
      for (i in object) {
        if (object.hasOwnProperty(i)) {
          cloned[i] = deepClone(object[i]);
        }
      }
      return cloned;
    }
    if (object instanceof Date) {
      // XXX this block is to enable phantomjs and browsers compatibility with
      // Date.prototype.toJSON when it is an invalid date. In phantomjs, it
      // returns `"Invalid Date"` but in browsers it returns `null`. In
      // browsers, giving `null` as parameter to `new Date()` doesn't return an
      // invalid date.

      // Cloning a date with `return new Date(object)` has problems on Firefox.
      // I don't know why...  (Tested on Firefox 23)

      if (isFinite(object.getTime())) {
        return new Date(object.toJSON());
      }
      return new Date("Invalid Date");
    }
    // clone serializable objects
    if (typeof object.toJSON === 'function') {
      return new (Object.getPrototypeOf(object).constructor)(object.toJSON());
    }
    // cannot clone
    return object;
  }
  return object;
}
exports.util.deepClone = deepClone;

/**
 * Update a dictionary by adding/replacing key values from another dict.
 * Enumerable values equal to undefined are also used.
 *
 * @param  {Object} original The dict to update
 * @param  {Object} other The other dict
 * @return {Object} The updated original dict
 */
function dictUpdate(original, other) {
  var k;
  for (k in other) {
    if (other.hasOwnProperty(k)) {
      original[k] = other[k];
    }
  }
  return original;
}
exports.util.dictUpdate = dictUpdate;

/**
 * Like 'dict.clear()' in python. Delete all dict entries.
 *
 * @method dictClear
 * @param  {Object} self The dict to clear
 */
function dictClear(dict) {
  var i;
  for (i in dict) {
    if (dict.hasOwnProperty(i)) {
      delete dict[i];
      // dictClear(dict);
      // break;
    }
  }
}
exports.util.dictClear = dictClear;

/**
 * Filter a dict to keep only values which keys are in `keys` list.
 *
 * @param  {Object} dict The dict to filter
 * @param  {Array} keys The key list to keep
 */
function dictFilter(dict, keys) {
  var i, buffer = [];
  for (i = 0; i < keys.length; i += 1) {
    buffer[i] = dict[keys[i]];
  }
  dictClear(dict);
  for (i = 0; i < buffer.length; i += 1) {
    dict[keys[i]] = buffer[i];
  }
}
exports.util.dictFilter = dictFilter;

/**
 * Gets all elements of an array and classifies them in a dict of array.
 * Dict keys are element types, and values are list of element of type 'key'.
 *
 * @param  {Array} array The array of elements to pop
 * @return {Object} The type dict
 */
function arrayValuesToTypeDict(array) {
  var i, l, type_object = {}, type, v;
  for (i = 0, l = array.length; i < l; i += 1) {
    v = array[i];
    type = Array.isArray(v) ? "array" : typeof v;
    /*jslint ass: true */
    (type_object[type] = type_object[type] || []).push(v);
  }
  return type_object;
}

/**
 * An Universal Unique ID generator
 *
 * @return {String} The new UUID.
 */
function generateUuid() {
  function S4() {
    return ('0000' + Math.floor(
      Math.random() * 0x10000 /* 65536 */
    ).toString(16)).slice(-4);
  }
  return S4() + S4() + "-" +
    S4() + "-" +
    S4() + "-" +
    S4() + "-" +
    S4() + S4() + S4();
}
exports.util.generateUuid = generateUuid;

/**
 * JSON stringify a value. Dict keys are sorted in order to make a kind of
 * deepEqual thanks to a simple strict equal string comparison.
 *
 *     JSON.stringify({"a": "b", "c": "d"}) ===
 *       JSON.stringify({"c": "d", "a": "b"})                 // false
 *
 *     deepEqual({"a": "b", "c": "d"}, {"c": "d", "a": "b"}); // true
 *
 *     uniqueJSONStringify({"a": "b", "c": "d"}) ===
 *       uniqueJSONStringify({"c": "d", "a": "b"})            // true
 *
 * @param  {Any} value The value to stringify
 * @param  {Function} [replacer] A function to replace values during parse
 */
function uniqueJSONStringify(value, replacer) {
  function subStringify(value, key) {
    var i, res;
    if (typeof replacer === 'function') {
      value = replacer(key, value);
    }
    if (Array.isArray(value)) {
      res = [];
      for (i = 0; i < value.length; i += 1) {
        res[res.length] = subStringify(value[i], i);
        if (res[res.length - 1] === undefined) {
          res[res.length - 1] = 'null';
        }
      }
      return '[' + res.join(',') + ']';
    }
    if (typeof value === 'object' && value !== null &&
        typeof value.toJSON !== 'function') {
      res = [];
      for (i in value) {
        if (value.hasOwnProperty(i)) {
          res[res.length] = subStringify(value[i], i);
          if (res[res.length - 1] !== undefined) {
            res[res.length - 1] = JSON.stringify(i) + ":" + res[res.length - 1];
          } else {
            res.length -= 1;
          }
        }
      }
      res.sort();
      return '{' + res.join(',') + '}';
    }
    return JSON.stringify(value);
  }
  return subStringify(value, '');
}
exports.util.uniqueJSONStringify = uniqueJSONStringify;

function makeBinaryStringDigest(string) {
  return 'sha256-' + hex_sha256(string);
}
exports.util.makeBinaryStringDigest = makeBinaryStringDigest;

function readBlobAsBinaryString(blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", resolve);
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsBinaryString(blob);
  }, function () {
    fr.abort();
  });
}
exports.util.readBlobAsBinaryString = readBlobAsBinaryString;

function readBlobAsArrayBuffer(blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", resolve);
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsArrayBuffer(blob);
  }, function () {
    fr.abort();
  });
}
exports.util.readBlobAsArrayBuffer = readBlobAsArrayBuffer;

function readBlobAsText(blob) {
  var fr = new FileReader();
  return new RSVP.Promise(function (resolve, reject, notify) {
    fr.addEventListener("load", resolve);
    fr.addEventListener("error", reject);
    fr.addEventListener("progress", notify);
    fr.readAsText(blob);
  }, function () {
    fr.abort();
  });
}
exports.util.readBlobAsText = readBlobAsText;

/**
 * Send request with XHR and return a promise. xhr.onload: The promise is
 * resolved when the status code is lower than 400 with the xhr object as first
 * parameter. xhr.onerror: reject with xhr object as first
 * parameter. xhr.onprogress: notifies the xhr object.
 *
 * @param  {Object} param The parameters
 * @param  {String} [param.type="GET"] The request method
 * @param  {String} [param.dataType=""] The data type to retrieve
 * @param  {String} param.url The url
 * @param  {Any} [param.data] The data to send
 * @param  {Function} [param.beforeSend] A function called just before the send
 *   request. The first parameter of this function is the XHR object.
 * @return {Promise} The promise
 */
function ajax(param) {
  var xhr = new XMLHttpRequest();
  return new RSVP.Promise(function (resolve, reject, notify) {
    var k;
    xhr.open(param.type || "GET", param.url, true);
    xhr.responseType = param.dataType || "";
    if (typeof param.headers === 'object' && param.headers !== null) {
      for (k in param.headers) {
        if (param.headers.hasOwnProperty(k)) {
          xhr.setRequestHeader(k, param.headers[k]);
        }
      }
    }
    xhr.addEventListener("load", function (e) {
      if (e.target.status >= 400) {
        return reject(e);
      }
      resolve(e);
    });
    xhr.addEventListener("error", reject);
    xhr.addEventListener("progress", notify);
    if (typeof param.xhrFields === 'object' && param.xhrFields !== null) {
      for (k in param.xhrFields) {
        if (param.xhrFields.hasOwnProperty(k)) {
          xhr[k] = param.xhrFields[k];
        }
      }
    }
    if (typeof param.beforeSend === 'function') {
      param.beforeSend(xhr);
    }
    xhr.send(param.data);
  }, function () {
    xhr.abort();
  });
}
exports.util.ajax = ajax;

/**
 * Acts like `Array.prototype.concat` but does not create a copy of the original
 * array. It extends the original array and return it.
 *
 * @param  {Array} array The array to extend
 * @param  {Any} [args]* Values to add in the array
 * @return {Array} The original array
 */
function arrayExtend(array) { // args*
  var i, j;
  for (i = 1; i < arguments.length; i += 1) {
    if (Array.isArray(arguments[i])) {
      for (j = 0; j < arguments[i].length; j += 1) {
        array[array.length] = arguments[i][j];
      }
    } else {
      array[array.length] = arguments[i];
    }
  }
  return array;
}
exports.util.arrayExtend = arrayExtend;

/**
 * Acts like `Array.prototype.concat` but does not create a copy of the original
 * array. It extends the original array from a specific position and return it.
 *
 * @param  {Array} array The array to extend
 * @param  {Number} position The position where to extend
 * @param  {Any} [args]* Values to add in the array
 * @return {Array} The original array
 */
function arrayInsert(array, position) { // args*
  var array_part = array.splice(position, array.length - position);
  arrayExtend.apply(null, arrayExtend([
  ], [array], Array.prototype.slice.call(arguments, 2)));
  return arrayExtend(array, array_part);
}
exports.util.arrayInsert = arrayInsert;

/**
 * Guess if the method is a writer or a reader.
 *
 * @param  {String} method The method name
 * @return {String} "writer", "reader" or "unknown"
 */
function methodType(method) {
  switch (method) {
  case "post":
  case "put":
  case "putAttachment":
  case "remove":
  case "removeAttachment":
  case "repair":
    return 'writer';
  case "get":
  case "getAttachment":
  case "allDocs":
  case "check":
    return 'reader';
  default:
    return 'unknown';
  }
}

/**
 *     forEach(array, callback[, thisArg]): Promise
 *
 * It executes the provided `callback` once for each element of the array with
 * an assigned value asynchronously. If the `callback` returns a promise, then
 * the function will wait for its fulfillment before executing the next
 * iteration.
 *
 * `callback` is invoked with three arguments:
 *
 * - the element value
 * - the element index
 * - the array being traversed
 *
 * If a `thisArg` parameter is provided to `forEach`, it will be passed to
 * `callback` when invoked, for use as its `this` value.  Otherwise, the value
 * `undefined` will be passed for use as its `this` value.
 *
 * Unlike `Array.prototype.forEach`, you can stop the iteration by throwing
 * something, or by doing a `cancel` to the returned promise if it is
 * cancellable promise.
 *
 * Inspired by `Array.prototype.forEach` from Mozilla Developer Network.
 *
 * @param  {Array} array The array to parse
 * @param  {Function} callback Function to execute for each element.
 * @param  {Any} [thisArg] Value to use as `this` when executing `callback`.
 * @param  {Promise} A new promise.
 */
function forEach(array, fn, thisArg) {
  if (arguments.length === 0) {
    throw new TypeError("missing argument 0 when calling function forEach");
  }
  if (!Array.isArray(array)) {
    throw new TypeError(array + " is not an array");
  }
  if (arguments.length === 1) {
    throw new TypeError("missing argument 1 when calling function forEach");
  }
  if (typeof fn !== "function") {
    throw new TypeError(fn + " is not a function");
  }
  var cancelled, current_promise = RSVP.resolve();
  return new RSVP.Promise(function (done, fail, notify) {
    var i = 0;
    function next() {
      if (cancelled) {
        fail(new Error("Cancelled"));
        return;
      }
      if (i < array.length) {
        current_promise =
          current_promise.then(fn.bind(thisArg, array[i], i, array));
        current_promise.then(next, fail, notify);
        i += 1;
        return;
      }
      done();
    }
    next();
  }, function () {
    cancelled = true;
    if (typeof current_promise.cancel === "function") {
      current_promise.cancel();
    }
  });
}
exports.util.forEach = forEach;

/**
 *     range(stop, callback): Promise
 *     range(start, stop[, step], callback): Promise
 *
 * It executes the provided `callback` once for each step between `start` and
 * `stop`. If the `callback` returns a promise, then the function will wait
 * for its fulfillment before executing the next iteration.
 *
 * `callback` is invoked with one argument:
 *
 * - the index of the step
 *
 * `start`, `stop` and `step` must be finite numbers. If `step` is not
 * provided, then the default step will be `1`. If `start` and `step` are not
 * provided, `start` will be `0` and `step` will be `1`.
 *
 * Inspired by `range()` from Python 3 built-in functions.
 *
 *     range(10, function (index) {
 *       return notifyIndex(index);
 *     }).then(onDone, onError, onNotify);
 *
 * @param  {Number} [start=0] The start index
 * @param  {Number} stop The stop index
 * @param  {Number} [step=1] One step
 * @param  {Function} callback Function to execute on each iteration.
 * @param  {Promise} A new promise with no fulfillment value.
 */
function range(start, stop, step, callback) {
  var type_object, cancelled, current_promise;
  type_object = arrayValuesToTypeDict([start, stop, step, callback]);

  if (type_object["function"].length !== 1) {
    throw new TypeError("range(): only one callback is needed");
  }
  start = type_object.number.length;
  if (start < 1) {
    throw new TypeError("range(): 1, 2 or 3 numbers are needed");
  }
  if (start > 3) {
    throw new TypeError("range(): only 1, 2 or 3 numbers are needed");
  }

  callback = type_object["function"][0];

  if (start === 1) {
    start = 0;
    stop = type_object.number[0];
    step = 1;
  }

  if (start === 2) {
    start = type_object.number[0];
    stop = type_object.number[1];
    step = 1;
  }

  if (start === 3) {
    start = type_object.number[0];
    stop = type_object.number[1];
    step = type_object.number[2];
    if (step === 0) {
      throw new TypeError("range(): step must not be zero");
    }
  }

  type_object = undefined;
  current_promise = RSVP.resolve();
  return new RSVP.Promise(function (done, fail, notify) {
    var i = start, test;
    function next() {
      if (cancelled) {
        fail(new Error("Cancelled"));
        return;
      }
      test = step > 0 ? i < stop : i > stop;
      if (test) {
        current_promise = current_promise.then(callback.bind(null, i));
        current_promise.then(next, fail, notify);
        i += step;
        return;
      }
      done();
    }
    next();
  }, function () {
    cancelled = true;
    if (typeof current_promise.cancel === "function") {
      current_promise.cancel();
    }
  });
}
exports.util.range = range;

/*jslint indent: 2, maxlen: 80, nomen: true, sloppy: true */
/*global secureMethods, exports, console */

/**
 * Inspired by nodejs EventEmitter class
 * http://nodejs.org/api/events.html
 *
 * When an EventEmitter instance experiences an error, the typical action is
 * to emit an 'error' event. Error events are treated as a special case in
 * node. If there is no listener for it, then the default action throws the
 * exception again.
 *
 * All EventEmitters emit the event 'newListener' when new listeners are added
 * and 'removeListener' when a listener is removed.
 *
 * @class EventEmitter
 * @constructor
 */
function EventEmitter() {
  this._events = {};
  this._maxListeners = 10;
}

/**
 * Adds a listener to the end of the listeners array for the specified
 * event.
 *
 * @method addListener
 * @param  {String} event The event name
 * @param  {Function} listener The listener callback
 * @return {EventEmitter} This emitter
 */
EventEmitter.prototype.addListener = function (event, listener) {
  var listener_list;
  if (typeof listener !== "function") {
    return this;
  }
  this.emit("newListener", event, listener);
  listener_list = this._events[event];
  if (listener_list === undefined) {
    this._events[event] = listener;
    listener_list = listener;
  } else if (typeof listener_list === "function") {
    this._events[event] = [listener_list, listener];
    listener_list = this._events[event];
  } else {
    listener_list[listener_list.length] = listener;
  }
  if (this._maxListeners > 0 &&
      typeof listener_list !== "function" &&
      listener_list.length > this._maxListeners &&
      listener_list.warned !== true) {
    console.warn("warning: possible EventEmitter memory leak detected. " +
                 listener_list.length + " listeners added. " +
                 "Use emitter.setMaxListeners() to increase limit.");
    listener_list.warned = true;
  }
  return this;
};

/**
 * #crossLink "EventEmitter/addListener:method"
 *
 * @method on
 */
EventEmitter.prototype.on = EventEmitter.prototype.addListener;

/**
 * Adds a one time listener for the event. This listener is invoked only the
 * next time the event is fired, after which it is removed.
 *
 * @method once
 * @param  {String} event The event name
 * @param  {Function} listener The listener callback
 * @return {EventEmitter} This emitter
 */
EventEmitter.prototype.once = function (event, listener) {
  var that = this, wrapper = function () {
    that.removeListener(event, wrapper);
    listener.apply(that, arguments);
  };
  wrapper.original = listener;
  return that.on(event, wrapper);
};

/**
 * Remove a listener from the listener array for the specified event.
 * Caution: changes array indices in the listener array behind the listener
 *
 * @method removeListener
 * @param  {String} event The event name
 * @param  {Function} listener The listener callback
 * @return {EventEmitter} This emitter
 */
EventEmitter.prototype.removeListener = function (event, listener) {
  var listener_list = this._events[event], i;
  if (listener_list) {
    if (typeof listener_list === "function") {
      if (listener_list === listener || listener_list.original === listener) {
        delete this._events[event];
      }
      return this;
    }
    for (i = 0; i < listener_list.length; i += 1) {
      if (listener_list[i] === listener ||
          listener_list[i].original === listener) {
        listener_list.splice(i, 1);
        this.emit("removeListener", event, listener);
        break;
      }
    }
    if (listener_list.length === 1) {
      this._events[event] = listener_list[0];
    }
    if (listener_list.length === 0) {
      this._events[event] = undefined;
    }
  }
  return this;
};

/**
 * Removes all listeners, or those of the specified event.
 *
 * @method removeAllListeners
 * @param  {String} event The event name (optional)
 * @return {EventEmitter} This emitter
 */
EventEmitter.prototype.removeAllListeners = function (event) {
  var key;
  if (event === undefined) {
    for (key in this._events) {
      if (this._events.hasOwnProperty(key)) {
        delete this._events[key];
      }
    }
    return this;
  }
  delete this._events[event];
  return this;
};

/**
 * By default EventEmitters will print a warning if more than 10 listeners
 * are added for a particular event. This is a useful default which helps
 * finding memory leaks. Obviously not all Emitters should be limited to 10.
 * This function allows that to be increased. Set to zero for unlimited.
 *
 * @method setMaxListeners
 * @param  {Number} max_listeners The maximum of listeners
 */
EventEmitter.prototype.setMaxListeners = function (max_listeners) {
  this._maxListeners = max_listeners;
};

/**
 * Execute each of the listeners in order with the supplied arguments.
 *
 * @method emit
 * @param  {String} event The event name
 * @param  {Any} [args]* The listener argument to give
 * @return {Boolean} true if event had listeners, false otherwise.
 */
EventEmitter.prototype.emit = function (event) {
  var i, argument_list, listener_list;
  listener_list = this._events[event];
  if (typeof listener_list === 'function') {
    listener_list = [listener_list];
  } else if (Array.isArray(listener_list)) {
    listener_list = listener_list.slice();
  } else {
    return false;
  }
  argument_list = Array.prototype.slice.call(arguments, 1);
  for (i = 0; i < listener_list.length; i += 1) {
    try {
      listener_list[i].apply(this, argument_list);
    } catch (e) {
      if (this.listeners("error").length > 0) {
        this.emit("error", e);
        break;
      }
      throw e;
    }
  }
  return true;
};

/**
 * Returns an array of listeners for the specified event.
 *
 * @method listeners
 * @param  {String} event The event name
 * @return {Array} The array of listeners
 */
EventEmitter.prototype.listeners = function (event) {
  return (typeof this._events[event] === 'function' ?
          [this._events[event]] : (this._events[event] || []).slice());
};

/**
 * Static method; Return the number of listeners for a given event.
 *
 * @method listenerCount
 * @static
 * @param  {EventEmitter} emitter The event emitter
 * @param  {String} event The event name
 * @return {Number} The number of listener
 */
EventEmitter.listenerCount = function (emitter, event) {
  return emitter.listeners(event).length;
};

exports.EventEmitter = EventEmitter;

/*jslint indent: 2, maxlen: 80, nomen: true, sloppy: true */
/*global EventEmitter, deepClone, inherits, exports */
/*global enableRestAPI, enableRestParamChecker, enableJobMaker, enableJobRetry,
  enableJobReference, enableJobChecker, enableJobQueue, enableJobRecovery,
  enableJobTimeout, enableJobExecuter */

function JIO(storage_spec, options) {
  JIO.super_.call(this);
  var shared = new EventEmitter();

  shared.storage_spec = deepClone(storage_spec);

  if (options === undefined) {
    options = {};
  } else if (typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError("JIO(): Optional argument 2 is not of type 'object'");
  }

  enableRestAPI(this, shared, options);
  enableRestParamChecker(this, shared, options);
  enableJobMaker(this, shared, options);
  enableJobReference(this, shared, options);
  enableJobRetry(this, shared, options);
//  enableJobTimeout(this, shared, options);
  enableJobChecker(this, shared, options);
  enableJobQueue(this, shared, options);
  enableJobRecovery(this, shared, options);
  enableJobExecuter(this, shared, options);

  shared.emit('load');
}
inherits(JIO, EventEmitter);

JIO.createInstance = function (storage_spec, options) {
  return new JIO(storage_spec, options);
};

exports.JIO = JIO;

exports.createJIO = JIO.createInstance;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global deepClone, dictFilter, uniqueJSONStringify */

/**
 * Tool to manipulate a list of object containing at least one property: 'id'.
 * Id must be a number > 0.
 *
 * @class JobQueue
 * @constructor
 * @param  {Workspace} workspace The workspace where to store
 * @param  {String} namespace The namespace to use in the workspace
 * @param  {Array} job_keys An array of job keys to store
 * @param  {Array} [array] An array of object
 */
function JobQueue(workspace, namespace, job_keys, array) {
  this._workspace = workspace;
  this._namespace = namespace;
  this._job_keys = job_keys;
  if (Array.isArray(array)) {
    this._array = array;
  } else {
    this._array = [];
  }
}

/**
 * Store the job queue into the workspace.
 *
 * @method save
 */
JobQueue.prototype.save = function () {
  var i, job_queue = deepClone(this._array);
  for (i = 0; i < job_queue.length; i += 1) {
    dictFilter(job_queue[i], this._job_keys);
  }
  if (this._array.length === 0) {
    this._workspace.removeItem(this._namespace);
  } else {
    this._workspace.setItem(
      this._namespace,
      uniqueJSONStringify(job_queue)
    );
  }
  return this;
};

/**
 * Loads the job queue from the workspace.
 *
 * @method load
 */
JobQueue.prototype.load = function () {
  var job_list;
  try {
    job_list = JSON.parse(this._workspace.getItem(this._namespace));
  } catch (ignore) {}
  if (!Array.isArray(job_list)) {
    job_list = [];
  }
  this.clear();
  new JobQueue(job_list).repair();
  this.update(job_list);
  return this;
};

/**
 * Returns the array version of the job queue
 *
 * @method asArray
 * @return {Array} The job queue as array
 */
JobQueue.prototype.asArray = function () {
  return this._array;
};

/**
 * Removes elements which are not objects containing at least 'id' property.
 *
 * @method repair
 */
JobQueue.prototype.repair = function () {
  var i, job;
  for (i = 0; i < this._array.length; i += 1) {
    job = this._array[i];
    if (typeof job !== 'object' || Array.isArray(job) ||
        typeof job.id !== 'number' || job.id <= 0) {
      this._array.splice(i, 1);
      i -= 1;
    }
  }
};

/**
 * Post an object and generate an id
 *
 * @method post
 * @param  {Object} job The job object
 * @return {Number} The generated id
 */
JobQueue.prototype.post = function (job) {
  var i, next = 1;
  // get next id
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i].id >= next) {
      next = this._array[i].id + 1;
    }
  }
  job.id = next;
  this._array[this._array.length] = deepClone(job);
  return this;
};

/**
 * Put an object to the list. If an object contains the same id, it is replaced
 * by the new one.
 *
 * @method put
 * @param  {Object} job The job object with an id
 */
JobQueue.prototype.put = function (job) {
  var i;
  if (typeof job.id !== 'number' || job.id <= 0) {
    throw new TypeError("JobQueue().put(): Job id should be a positive number");
  }
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i].id === job.id) {
      break;
    }
  }
  this._array[i] = deepClone(job);
  return this;
};

/**
 * Puts some object into the list. Update object with the same id, and add
 * unreferenced one.
 *
 * @method update
 * @param  {Array} job_list A list of new jobs
 */
JobQueue.prototype.update = function (job_list) {
  var i, j = 0, j_max, index = {}, next = 1, job, post_list = [];
  j_max = this._array.length;
  for (i = 0; i < job_list.length; i += 1) {
    if (typeof job_list[i].id !== 'number' || job_list[i].id <= 0) {
      // this job has no id, it has to be post
      post_list[post_list.length] = job_list[i];
    } else {
      job = deepClone(job_list[i]);
      if (index[job.id] !== undefined) {
        // this job is on the list, update
        this._array[index[job.id]] = job;
      } else if (j === j_max) {
        // this job is not on the list, update
        this._array[this._array.length] = job;
      } else {
        // don't if the job is there or not
        // searching same job in the original list
        while (j < j_max) {
          // references visited job
          index[this._array[j].id] = j;
          if (this._array[j].id >= next) {
            next = this._array[j].id + 1;
          }
          if (this._array[j].id === job.id) {
            // found on the list, just update
            this._array[j] = job;
            break;
          }
          j += 1;
        }
        if (j === j_max) {
          // not found on the list, add to the end
          this._array[this._array.length] = job;
        } else {
          // found on the list, already updated
          j += 1;
        }
      }
      if (job.id >= next) {
        next = job.id + 1;
      }
    }
  }
  for (i = 0; i < post_list.length; i += 1) {
    // adding job without id
    post_list[i].id = next;
    next += 1;
    this._array[this._array.length] = deepClone(post_list[i]);
  }
  return this;
};

/**
 * Get an object from an id. Returns undefined if not found
 *
 * @method get
 * @param  {Number} id The job id
 * @return {Object} The job or undefined
 */
JobQueue.prototype.get = function (id) {
  var i;
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i].id === id) {
      return deepClone(this._array[i]);
    }
  }
};

/**
 * Removes an object from an id
 *
 * @method remove
 * @param  {Number} id The job id
 */
JobQueue.prototype.remove = function (id) {
  var i;
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i].id === id) {
      this._array.splice(i, 1);
      return true;
    }
  }
  return false;
};

/**
 * Clears the list.
 *
 * @method clear
 */
JobQueue.prototype.clear = function () {
  this._array.length = 0;
  return this;
};


/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global localStorage */

// keywords: js, javascript, store on local storage as array

function LocalStorageArray(namespace) {
  var index, next;

  function nextId() {
    var i = next;
    next += 1;
    return i;
  }

  this.length = function () {
    return index.length;
  };

  this.truncate = function (length) {
    var i;
    if (length === index.length) {
      return this;
    }
    if (length > index.length) {
      index.length = length;
      localStorage[namespace + '.index'] = JSON.stringify(index);
      return this;
    }
    while (length < index.length) {
      i = index.pop();
      if (i !== undefined && i !== null) {
        delete localStorage[namespace + '.' + i];
      }
    }
    localStorage[namespace + '.index'] = JSON.stringify(index);
    return this;
  };

  this.get = function (i) {
    return JSON.parse(localStorage[namespace + '.' + index[i]] || 'null');
  };

  this.set = function (i, value) {
    if (index[i] === undefined || index[i] === null) {
      index[i] = nextId();
      localStorage[namespace + '.' + index[i]] = JSON.stringify(value);
      localStorage[namespace + '.index'] = JSON.stringify(index);
    } else {
      localStorage[namespace + '.' + index[i]] = JSON.stringify(value);
    }
    return this;
  };

  this.append = function (value) {
    index[index.length] = nextId();
    localStorage[namespace + '.' + index[index.length - 1]] =
      JSON.stringify(value);
    localStorage[namespace + '.index'] = JSON.stringify(index);
    return this;
  };

  this.pop = function (i) {
    var value, key;
    if (i === undefined || i === null) {
      key = namespace + '.' + index[index.length - 1];
      index.pop();
    } else {
      if (i < 0 || i >= index.length) {
        return null;
      }
      key = namespace + '.' + i;
      index.splice(i, 1);
    }

    value = localStorage[key];

    if (index.length === 0) {
      delete localStorage[namespace + '.index'];
    } else {
      localStorage[namespace + '.index'] = JSON.stringify(index);
    }
    delete localStorage[key];

    return JSON.parse(value || 'null');
  };

  this.clear = function () {
    var i;
    for (i = 0; i < index.length; i += 1) {
      delete localStorage[namespace + '.' + index[i]];
    }
    index = [];
    delete localStorage[namespace + '.index'];
    return this;
  };

  this.reload = function () {
    var i;
    index = JSON.parse(localStorage[namespace + '.index'] || '[]');
    next = 0;
    for (i = 0; i < index.length; i += 1) {
      if (next < index[i]) {
        next = index[i];
      }
    }
    return this;
  };

  this.toArray = function () {
    var i, list = [];
    for (i = 0; i < index.length; i += 1) {
      list[list.length] = this.get(i);
    }
    return list;
  };

  this.update = function (list) {
    if (!Array.isArray(list)) {
      throw new TypeError("LocalStorageArray().saveArray(): " +
                          "Argument 1 is not of type 'array'");
    }
    var i, location;
    // update previous values
    for (i = 0; i < list.length; i += 1) {
      location = index[i];
      if (location === undefined || location === null) {
        location = nextId();
        index[i] = location;
      }
      localStorage[namespace + '.' + location] =
        JSON.stringify(list[i]);
    }
    // remove last ones
    while (list.length < index.length) {
      location = index.pop();
      if (location !== undefined && location !== null) {
        delete localStorage[namespace + '.' + location];
      }
    }
    // store index
    localStorage[namespace + '.index'] = JSON.stringify(index);
    return this;
  };

  this.reload();
}

LocalStorageArray.saveArray = function (namespace, list) {
  if (!Array.isArray(list)) {
    throw new TypeError("LocalStorageArray.saveArray(): " +
                        "Argument 2 is not of type 'array'");
  }
  var local_storage_array = new LocalStorageArray(namespace).clear(), i;
  for (i = 0; i < list.length; i += 1) {
    local_storage_array.append(list[i]);
  }
};

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global exports, deepClone, jsonDeepClone */

/**
 * A class to manipulate metadata
 *
 * @class Metadata
 * @constructor
 */
function Metadata(metadata) {
  if (arguments.length > 0) {
    if (metadata === null || typeof metadata !== 'object' ||
        Array.isArray(metadata)) {
      throw new TypeError("Metadata(): Optional argument 1 is not an object");
    }
    this._dict = metadata;
  } else {
    this._dict = {};
  }
}

Metadata.prototype.format = function () {
  return this.update(this._dict);
};

Metadata.prototype.check = function () {
  var k;
  for (k in this._dict) {
    if (this._dict.hasOwnProperty(k)) {
      if (k[0] !== '_') {
        if (!Metadata.checkValue(this._dict[k])) {
          return false;
        }
      }
    }
  }
  return true;
};

Metadata.prototype.update = function (metadata) {
  var k;
  for (k in metadata) {
    if (metadata.hasOwnProperty(k)) {
      if (k[0] === '_') {
        this._dict[k] = jsonDeepClone(metadata[k]);
      } else {
        this._dict[k] = Metadata.normalizeValue(metadata[k]);
      }
      if (this._dict[k] === undefined) {
        delete this._dict[k];
      }
    }
  }
  return this;
};

Metadata.prototype.get = function (key) {
  return this._dict[key];
};

Metadata.prototype.add = function (key, value) {
  var i;
  if (key[0] === '_') {
    return this;
  }
  if (this._dict[key] === undefined) {
    this._dict[key] = Metadata.normalizeValue(value);
    if (this._dict[key] === undefined) {
      delete this._dict[key];
    }
    return this;
  }
  if (!Array.isArray(this._dict[key])) {
    this._dict[key] = [this._dict[key]];
  }
  value = Metadata.normalizeValue(value);
  if (value === undefined) {
    return this;
  }
  if (!Array.isArray(value)) {
    value = [value];
  }
  for (i = 0; i < value.length; i += 1) {
    this._dict[key][this._dict[key].length] = value[i];
  }
  return this;
};

Metadata.prototype.set = function (key, value) {
  if (key[0] === '_') {
    this._dict[key] = JSON.parse(JSON.stringify(value));
  } else {
    this._dict[key] = Metadata.normalizeValue(value);
  }
  if (this._dict[key] === undefined) {
    delete this._dict[key];
  }
  return this;
};

Metadata.prototype.remove = function (key) {
  delete this._dict[key];
  return this;
};


Metadata.prototype.forEach = function (key, fun) {
  var k, i, value, that = this;
  if (typeof key === 'function') {
    fun = key;
    key = undefined;
  }
  function forEach(key, fun) {
    value = that._dict[key];
    if (!Array.isArray(that._dict[key])) {
      value = [value];
    }
    for (i = 0; i < value.length; i += 1) {
      if (typeof value[i] === 'object') {
        fun.call(that, key, deepClone(value[i]), i);
      } else {
        fun.call(that, key, {'content': value[i]}, i);
      }
    }
  }
  if (key === undefined) {
    for (k in this._dict) {
      if (this._dict.hasOwnProperty(k)) {
        forEach(k, fun);
      }
    }
  } else {
    forEach(key, fun);
  }
  return this;
};

Metadata.prototype.toFullDict = function () {
  var dict = {};
  this.forEach(function (key, value, index) {
    dict[key] = dict[key] || [];
    dict[key][index] = value;
  });
  return dict;
};

Metadata.asJsonableValue = function (value) {
  switch (typeof value) {
  case 'string':
  case 'boolean':
    return value;
  case 'number':
    if (isFinite(value)) {
      return value;
    }
    return null;
  case 'object':
    if (value === null) {
      return null;
    }
    if (value instanceof Date) {
      // XXX this block is to enable phantomjs and browsers compatibility with
      // Date.prototype.toJSON when it is a invalid date. In phantomjs, it
      // returns `"Invalid Date"` but in browsers it returns `null`. Here, the
      // result will always be `null`.
      if (isNaN(value.getTime())) {
        return null;
      }
    }
    if (typeof value.toJSON === 'function') {
      return Metadata.asJsonableValue(value.toJSON());
    }
    return value; // dict, array
  // case 'undefined':
  default:
    return null;
  }
};

Metadata.isDict = function (o) {
  return typeof o === 'object' &&
    Object.getPrototypeOf(o || []) === Object.prototype;
};

Metadata.isContent = function (c) {
  return typeof c === 'string' ||
    (typeof c === 'number' && isFinite(c)) ||
    typeof c === 'boolean';
};

Metadata.contentValue = function (value) {
  if (Array.isArray(value)) {
    return Metadata.contentValue(value[0]);
  }
  if (Metadata.isDict(value)) {
    return value.content;
  }
  return value;
};

Metadata.normalizeArray = function (value) {
  var i;
  value = value.slice();
  i = 0;
  while (i < value.length) {
    value[i] = Metadata.asJsonableValue(value[i]);
    if (Metadata.isDict(value[i])) {
      value[i] = Metadata.normalizeObject(value[i]);
      if (value[i] === undefined) {
        value.splice(i, 1);
      } else {
        i += 1;
      }
    } else if (Metadata.isContent(value[i])) {
      i += 1;
    } else {
      value.splice(i, 1);
    }
  }
  if (value.length === 0) {
    return;
  }
  if (value.length === 1) {
    return value[0];
  }
  return value;
};

Metadata.normalizeObject = function (value) {
  var i, count = 0, ok = false, new_value = {};
  for (i in value) {
    if (value.hasOwnProperty(i)) {
      value[i] = Metadata.asJsonableValue(value[i]);
      if (Metadata.isContent(value[i])) {
        new_value[i] = value[i];
        if (new_value[i] === undefined) {
          delete new_value[i];
        }
        count += 1;
        if (i === 'content') {
          ok = true;
        }
      }
    }
  }
  if (ok === false) {
    return;
  }
  if (count === 1) {
    return new_value.content;
  }
  return new_value;
};

Metadata.normalizeValue = function (value) {
  value = Metadata.asJsonableValue(value);
  if (Metadata.isContent(value)) {
    return value;
  }
  if (Array.isArray(value)) {
    return Metadata.normalizeArray(value);
  }
  if (Metadata.isDict(value)) {
    return Metadata.normalizeObject(value);
  }
};

Metadata.checkArray = function (value) {
  var i;
  for (i = 0; i < value.length; i += 1) {
    if (Metadata.isDict(value[i])) {
      if (!Metadata.checkObject(value[i])) {
        return false;
      }
    } else if (!Metadata.isContent(value[i])) {
      return false;
    }
  }
  return true;
};

Metadata.checkObject = function (value) {
  var i, ok = false;
  for (i in value) {
    if (value.hasOwnProperty(i)) {
      if (Metadata.isContent(value[i])) {
        if (i === 'content') {
          ok = true;
        }
      } else {
        return false;
      }
    }
  }
  if (ok === false) {
    return false;
  }
  return true;
};

Metadata.checkValue = function (value) {
  if (Metadata.isContent(value)) {
    return true;
  }
  if (Array.isArray(value)) {
    return Metadata.checkArray(value);
  }
  if (Metadata.isDict(value)) {
    return Metadata.checkObject(value);
  }
  return false;
};

exports.Metadata = Metadata;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global */

/**
 * An array that contain object (or array) references.
 *
 * @class ReferenceArray
 * @constructor
 * @param  {array} [array] The array where to work on
 */
function ReferenceArray(array) {
  if (Array.isArray(array)) {
    this._array = array;
  } else {
    this._array = [];
  }
}

/**
 * Returns the array version of the job queue
 *
 * @method asArray
 * @return {Array} The job queue as array
 */
ReferenceArray.prototype.asArray = function () {
  return this._array;
};

/**
 * Returns the index of the object
 *
 * @method indexOf
 * @param  {Object} object The object to search
 */
ReferenceArray.prototype.indexOf = function (object) {
  var i;
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i] === object) {
      return i;
    }
  }
  return -1;
};

/**
 * Put an object to the list. If an object already exists, do nothing.
 *
 * @method put
 * @param  {Object} object The object to add
 */
ReferenceArray.prototype.put = function (object) {
  var i;
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i] === object) {
      return false;
    }
  }
  this._array[i] = object;
  return true;
};

/**
 * Removes an object from the list
 *
 * @method remove
 * @param  {Object} object The object to remove
 */
ReferenceArray.prototype.remove = function (object) {
  var i;
  for (i = 0; i < this._array.length; i += 1) {
    if (this._array[i] === object) {
      this._array.splice(i, 1);
      return true;
    }
  }
  return false;
};

/**
 * Clears the list.
 *
 * @method clear
 */
ReferenceArray.prototype.clear = function () {
  this._array.length = 0;
  return this;
};

/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global exports, defaults */

function Storage() { // (storage_spec, util)
  return undefined; // this is a constructor
}
// end Storage

function createStorage(storage_spec, util) {
  if (typeof storage_spec.type !== 'string') {
    throw new TypeError("Invalid storage description");
  }
  if (!defaults.storage_types[storage_spec.type]) {
    throw new TypeError("Unknown storage '" + storage_spec.type + "'");
  }
  return new defaults.storage_types[storage_spec.type](storage_spec, util);
}

function addStorage(type, Constructor) {
  // var proto = {};
  if (typeof type !== 'string') {
    throw new TypeError("jIO.addStorage(): Argument 1 is not of type 'string'");
  }
  if (typeof Constructor !== 'function') {
    throw new TypeError("jIO.addStorage(): " +
                        "Argument 2 is not of type 'function'");
  }
  if (defaults.storage_types[type]) {
    throw new TypeError("jIO.addStorage(): Storage type already exists");
  }
  // dictUpdate(proto, Constructor.prototype);
  // inherits(Constructor, Storage);
  // dictUpdate(Constructor.prototype, proto);
  defaults.storage_types[type] = Constructor;
}
exports.addStorage = addStorage;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global */

/**
 * A class that acts like localStorage on a simple object.
 *
 * Like localStorage, the object will contain only strings.
 *
 * @class Workspace
 * @constructor
 */
function Workspace(object) {
  this._object = object;
}

// // Too dangerous, never use it
// /**
//  * Empty the entire space.
//  *
//  * @method clear
//  */
// Workspace.prototype.clear = function () {
//   var k;
//   for (k in this._object) {
//     if (this._object.hasOwnProperty(k)) {
//       delete this._object;
//     }
//   }
//   return undefined;
// };

/**
 * Get an item from the space. If the value does not exists, it returns
 * null. Else, it returns the string value.
 *
 * @method getItem
 * @param  {String} key The location where to get the item
 * @return {String} The item
 */
Workspace.prototype.getItem = function (key) {
  return this._object[key] === undefined ? null : this._object[key];
};

/**
 * Set an item into the space. The value to store is converted to string before.
 *
 * @method setItem
 * @param  {String} key The location where to set the item
 * @param  {Any} value The value to store
 */
Workspace.prototype.setItem = function (key, value) {
  if (value === undefined) {
    this._object[key] = 'undefined';
  } else if (value === null) {
    this._object[key] = 'null';
  } else {
    this._object[key] = value.toString();
  }
  return undefined;
};

/**
 * Removes an item from the space.
 *
 * @method removeItem
 * @param  {String} key The location where to remove the item
 */
Workspace.prototype.removeItem = function (key) {
  delete this._object[key];
  return undefined;
};

/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global exports, defaults */

// adds
// - jIO.addJobRuleCondition(name, function)

function addJobRuleCondition(name, method) {
  if (typeof name !== 'string') {
    throw new TypeError("jIO.addJobRuleAction(): " +
                        "Argument 1 is not of type 'string'");
  }
  if (typeof method !== 'function') {
    throw new TypeError("jIO.addJobRuleAction(): " +
                        "Argument 2 is not of type 'function'");
  }
  if (defaults.job_rule_conditions[name]) {
    throw new TypeError("jIO.addJobRuleAction(): Action already exists");
  }
  defaults.job_rule_conditions[name] = method;
}
exports.addJobRuleCondition = addJobRuleCondition;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, regexp: true */
/*global constants, dictUpdate, deepClone */

function restCommandRejecter(param, args) {
  // reject(status, reason, message, {"custom": "value"});
  // reject(status, reason, {..});
  // reject(status, {..});
  var arg, current_priority, priority = [
    // 0 - custom parameter values
    {},
    // 1 - default values
    {
      "status": constants.http_status.unknown,
      "statusText": constants.http_status_text.unknown,
      "message": "Command failed",
      "reason": "unknown"
    },
    // 2 - status, reason, message properties
    {},
    // 3 - status, reason, message parameters
    {},
    // 4 - never change
    {"result": "error", "method": param.method}
  ];
  args = Array.prototype.slice.call(args);
  arg = args.shift();

  // priority 4 - never change
  current_priority = priority[4];
  if (param.kwargs._id) {
    current_priority.id = param.kwargs._id;
  }
  if (/Attachment$/.test(param.method)) {
    current_priority.attachment = param.kwargs._attachment;
  }

  // priority 3 - status, reason, message parameters
  current_priority = priority[3];
  // parsing first parameter if is not an object
  if (typeof arg !== 'object' || arg === null || Array.isArray(arg)) {
    // first parameter is mandatory
    current_priority.status = arg;
    arg = args.shift();
  }
  // parsing second parameter if is not an object
  if (typeof arg !== 'object' || arg === null || Array.isArray(arg)) {
    if (arg !== undefined) {
      current_priority.reason = arg;
    }
    arg = args.shift();
  }
  // parsing third parameter if is not an object
  if (typeof arg !== 'object' || arg === null || Array.isArray(arg)) {
    if (arg !== undefined) {
      current_priority.message = arg;
    }
    arg = args.shift();
  }

  // parsing fourth parameter if is an object
  if (typeof arg === 'object' && arg !== null && !Array.isArray(arg)) {
    // priority 0 - custom values
    dictUpdate(priority[0], arg);
    // priority 2 - status, reason, message properties
    current_priority = priority[2];
    if (arg.hasOwnProperty('reason')) {
      current_priority.reason = arg.reason;
    }
    if (arg.hasOwnProperty('message')) {
      current_priority.message = arg.message;
    }
    if ((arg.statusText || arg.status >= 0)) {
      current_priority.status = arg.statusText || arg.status;
    }
    if (arg instanceof Error) {
      current_priority.reason = arg.message || "";
      current_priority.error = arg.name;
    }
  }

  // merge priority dicts
  for (current_priority = priority.length - 1;
       current_priority > 0;
       current_priority -= 1) {
    dictUpdate(priority[current_priority - 1], priority[current_priority]);
  }
  priority = priority[0];

  // check status
  priority.statusText = constants.http_status_text[priority.status];
  if (priority.statusText === undefined) {
    return restCommandRejecter(param, [
      // can create infernal loop if 'internal_storage_error' is not defined in
      // the constants
      'internal_storage_error',
      'invalid response',
      'Unknown status "' + priority.status + '"'
    ]);
  }
  priority.status = constants.http_status[priority.statusText];

  // set default priority error if not already set
  if (priority.error === undefined) {
    priority.error = priority.statusText.toLowerCase().replace(/ /g, '_').
      replace(/[^_a-z]/g, '');
  }
  return param.solver.reject(deepClone(priority));
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global constants, methodType, dictUpdate, Blob, deepClone,
  restCommandRejecter */

function restCommandResolver(param, args) {
  // resolve('ok', {"custom": "value"});
  // resolve(200, {...});
  // resolve({...});
  var arg, current_priority, priority = [
    // 0 - custom parameter values
    {},
    // 1 - default values
    {},
    // 2 - status property
    {},
    // 3 - status parameter
    {},
    // 4 - never change
    {"result": "success", "method": param.method}
  ];
  args = Array.prototype.slice.call(args);
  arg = args.shift();

  // priority 4 - never change
  current_priority = priority[4];
  if (param.kwargs._id) {
    current_priority.id = param.kwargs._id;
  }
  if (/Attachment$/.test(param.method)) {
    current_priority.attachment = param.kwargs._attachment;
  }

  // priority 1 - default values
  current_priority = priority[1];
  if (param.method === 'post') {
    current_priority.status = constants.http_status.created;
    current_priority.statusText = constants.http_status_text.created;
  } else if (methodType(param.method) === "writer" ||
             param.method === "check") {
    current_priority.status = constants.http_status.no_content;
    current_priority.statusText = constants.http_status_text.no_content;
  } else {
    current_priority.status = constants.http_status.ok;
    current_priority.statusText = constants.http_status_text.ok;
  }

  // priority 3 - status parameter
  current_priority = priority[3];
  // parsing first parameter if is not an object
  if (typeof arg !== 'object' || arg === null || Array.isArray(arg)) {
    if (arg !== undefined) {
      current_priority.status = arg;
    }
    arg = args.shift();
  }

  // parsing second parameter if is an object
  if (typeof arg === 'object' && arg !== null && !Array.isArray(arg)) {
    // priority 0 - custom values
    dictUpdate(current_priority, arg);
    // priority 2 - status property
    if (arg.hasOwnProperty("status") || arg.hasOwnProperty("statusText")) {
      priority[2].status = arg.statusText || arg.status;
    }
  }

  // merge priority dicts
  for (current_priority = priority.length - 1;
       current_priority > 0;
       current_priority -= 1) {
    dictUpdate(priority[current_priority - 1], priority[current_priority]);
  }
  priority = priority[0];

  // check document id if post method
  if (param.method === 'post' &&
      (typeof priority.id !== 'string' || !priority.id)) {
    return restCommandRejecter(param, [
      'internal_storage_error',
      'invalid response',
      'New document id have to be specified'
    ]);
  }

  // check status
  priority.statusText = constants.http_status_text[priority.status];
  if (priority.statusText === undefined) {
    return restCommandRejecter(param, [
      'internal_storage_error',
      'invalid response',
      'Unknown status "' + priority.status + '"'
    ]);
  }
  priority.status = constants.http_status[priority.statusText];

  // check data for get Attachment
  if (param.method === 'getAttachment') {
    if (typeof priority.data === 'string') {
      priority.data = new Blob([priority.data], {
        "type": priority.content_type || priority.mimetype || ""
      });
      delete priority.content_type;
      delete priority.mimetype;
    }
    if (!(priority.data instanceof Blob)) {
      return restCommandRejecter(param, [
        'internal_storage_error',
        'invalid response',
        'getAttachment method needs a Blob as returned "data".'
      ]);
    }
    // check data for readers (except check method)
  } else if (methodType(param.method) === 'reader' &&
             param.method !== 'check' &&
             (typeof priority.data !== 'object' ||
              priority.data === null ||
              Object.getPrototypeOf(priority.data) !== Object.prototype)) {
    return restCommandRejecter(param, [
      'internal_storage_error',
      'invalid response',
      param.method + ' method needs a dict as returned "data".'
    ]);
  }

  return param.solver.resolve(deepClone(priority));
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayInsert, deepClone, defaults */

// creates
// - some defaults job rule actions

function enableJobChecker(jio, shared, options) {

  // dependencies
  // - shared.jobs Object Array
  // - param.promise Object

  // creates
  // - shared.job_rules Array

  // uses 'job:new' event
  // emits 'job:modified', 'job:start', 'job:resolved',
  // 'job:end', 'job:reject' events

  shared.job_rule_action_names = [undefined, "ok", "wait", "update", "deny"];

  shared.job_rule_actions = {
    wait: function (original_job, new_job) {
      original_job.promise.always(function () {
        new_job.state = 'ready';
        new_job.modified = new Date();
        shared.emit('job:modified', new_job);
        shared.emit('job:start', new_job);
      });
      new_job.state = 'waiting';
      new_job.modified = new Date();
      shared.emit('job:modified', new_job);
    },
    update: function (original_job, new_job) {
      if (!new_job.solver) {
        // promise associated to the job
        new_job.state = 'done';
        shared.emit('job:resolved', new_job, []); // XXX why resolve?
        shared.emit('job:end', new_job);
      } else {
        if (!original_job.solver) {
          original_job.solver = new_job.solver;
        } else {
          original_job.promise.then(
            new_job.command.resolve,
            new_job.command.reject,
            new_job.command.notify
          );
        }
      }
      new_job.state = 'running';
      new_job.modified = new Date();
      shared.emit('job:modified', new_job);
    },
    deny: function (original_job, new_job) {
      new_job.state = "running";
      shared.emit('job:reject', new_job, [
        'precondition_failed',
        'command denied',
        'Command rejected by the job checker.'
      ]);
    }
  };

  function addJobRule(job_rule) {
    var i, old_position, before_position, after_position;
    // job_rule = {
    //   code_name: string
    //   conditions: [string, ...]
    //   action: 'wait',
    //   after: code_name
    //   before: code_name
    // }
    if (typeof job_rule !== 'object' || job_rule === null) {
      // wrong job rule
      return;
    }
    if (typeof job_rule.code_name !== 'string') {
      // wrong code name
      return;
    }
    if (!Array.isArray(job_rule.conditions)) {
      // wrong conditions
      return;
    }
    if (job_rule.single !== undefined && typeof job_rule.single !== 'boolean') {
      // wrong single property
      return;
    }
    if (shared.job_rule_action_names.indexOf(job_rule.action) === -1) {
      // wrong action
      return;
    }
    if (job_rule.action !== 'deny' && job_rule.single === true) {
      // only 'deny' action doesn't require original_job parameter
      return;
    }

    if (typeof job_rule.after !== 'string') {
      job_rule.after = '';
    }
    if (typeof job_rule.before !== 'string') {
      job_rule.before = '';
    }

    for (i = 0; i < shared.job_rules.length; i += 1) {
      if (shared.job_rules[i].code_name === job_rule.after) {
        after_position = i + 1;
      }
      if (shared.job_rules[i].code_name === job_rule.before) {
        before_position = i;
      }
      if (shared.job_rules[i].code_name === job_rule.code_name) {
        old_position = i;
      }
    }

    job_rule = {
      "code_name": job_rule.code_name,
      "conditions": job_rule.conditions,
      "single": job_rule.single || false,
      "action": job_rule.action || "ok"
    };

    if (before_position === undefined) {
      before_position = shared.job_rules.length;
    }
    if (after_position > before_position) {
      before_position = undefined;
    }
    if (job_rule.action !== "ok" && before_position !== undefined) {
      arrayInsert(shared.job_rules, before_position, job_rule);
    }
    if (old_position !== undefined) {
      if (old_position >= before_position) {
        old_position += 1;
      }
      shared.job_rules.splice(old_position, 1);
    }
  }

  function jobsRespectConditions(original_job, new_job, conditions) {
    var j;
    // browsing conditions
    for (j = 0; j < conditions.length; j += 1) {
      if (defaults.job_rule_conditions[conditions[j]]) {
        if (
          !defaults.job_rule_conditions[conditions[j]](original_job, new_job)
        ) {
          return false;
        }
      }
    }
    return true;
  }

  function checkJob(job) {
    var i, j;
    if (job.state === 'ready') {
      // browsing rules
      for (i = 0; i < shared.job_rules.length; i += 1) {
        if (shared.job_rules[i].single) {
          // no browse
          if (
            jobsRespectConditions(
              job,
              undefined,
              shared.job_rules[i].conditions
            )
          ) {
            shared.job_rule_actions[shared.job_rules[i].action](
              undefined,
              job
            );
            return;
          }
        } else {
          // browsing jobs
          for (j = shared.jobs.length - 1; j >= 0; j -= 1) {
            if (shared.jobs[j] !== job) {
              if (
                jobsRespectConditions(
                  shared.jobs[j],
                  job,
                  shared.job_rules[i].conditions
                )
              ) {
                shared.job_rule_actions[shared.job_rules[i].action](
                  shared.jobs[j],
                  job
                );
                return;
              }
            }
          }
        }
      }
    }
  }

  var index;

  if (options.job_management !== false) {

    shared.job_rules = [{
      "code_name": "readers update",
      "conditions": [
        "sameStorageDescription",
        "areReaders",
        "sameMethod",
        "sameParameters",
        "sameOptions"
      ],
      "action": "update"
    }, {
      "code_name": "metadata writers update",
      "conditions": [
        "sameStorageDescription",
        "areWriters",
        "useMetadataOnly",
        "sameMethod",
        "haveDocumentIds",
        "sameParameters"
      ],
      "action": "update"
    }, {
      "code_name": "writers wait",
      "conditions": [
        "sameStorageDescription",
        "areWriters",
        "haveDocumentIds",
        "sameDocumentId"
      ],
      "action": "wait"
    }];

    if (options.clear_job_rules === true) {
      shared.job_rules.length = 0;
    }

    if (Array.isArray(options.job_rules)) {
      for (index = 0; index < options.job_rules.length; index += 1) {
        addJobRule(deepClone(options.job_rules[index]));
      }
    }

    shared.on('job:new', checkJob);

  }

  jio.jobRules = function () {
    return deepClone(shared.job_rules);
  };

}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global setTimeout, Job, createStorage, deepClone, restCommandResolver,
  restCommandRejecter */

function enableJobExecuter(jio, shared) { // , options) {

  // uses 'job:new' events
  // uses actions 'job:resolve', 'job:reject' and 'job:notify'

  // emits 'job:modified', 'job:started', 'job:resolved',
  // 'job:rejected', 'job:notified' and 'job:end' events
  // emits action 'job:start'

  function startJobIfReady(job) {
    if (job.state === 'ready') {
      shared.emit('job:start', job);
    }
  }

  function executeJobIfReady(param) {
    var storage;
    if (param.state === 'ready') {
      param.tried += 1;
      param.started = new Date();
      param.state = 'running';
      param.modified = new Date();
      shared.emit('job:modified', param);
      shared.emit('job:started', param);
      try {
        storage = createStorage(deepClone(param.storage_spec));
      } catch (e) {
        return param.command.reject(
          'internal_storage_error',
          'invalid description',
          'Check if the storage description respects the ' +
            'constraints provided by the storage designer. (' +
            e.name + ": " + e.message + ')'
        );
      }
      if (typeof storage[param.method] !== 'function') {
        return param.command.reject(
          'not_implemented',
          'method missing',
          'Storage "' + param.storage_spec.type + '", "' +
            param.method + '" method is missing.'
        );
      }
      setTimeout(function () {
        storage[param.method](
          deepClone(param.command),
          deepClone(param.kwargs),
          deepClone(param.options)
        );
      });
    }
  }

  function endAndResolveIfRunning(job, args) {
    if (job.state === 'running') {
      job.state = 'done';
      job.modified = new Date();
      shared.emit('job:modified', job);
      if (job.solver) {
        restCommandResolver(job, args);
      }
      shared.emit('job:resolved', job, args);
      shared.emit('job:end', job);
    }
  }

  function endAndRejectIfRunning(job, args) {
    if (job.state === 'running') {
      job.state = 'fail';
      job.modified = new Date();
      shared.emit('job:modified', job);
      if (job.solver) {
        restCommandRejecter(job, args);
      }
      shared.emit('job:rejected', job, args);
      shared.emit('job:end', job);
    }
  }

  function notifyJobIfRunning(job, args) {
    if (job.state === 'running' && job.solver) {
      job.solver.notify(args[0]);
      shared.emit('job:notified', job, args);
    }
  }

  // listeners

  shared.on('job:new', startJobIfReady);
  shared.on('job:start', executeJobIfReady);

  shared.on('job:resolve', endAndResolveIfRunning);
  shared.on('job:reject', endAndRejectIfRunning);
  shared.on('job:notify', notifyJobIfRunning);
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayExtend */

function enableJobMaker(jio, shared, options) {

  // dependencies
  // - param.method
  // - param.storage_spec
  // - param.kwargs
  // - param.options

  // uses (Job)
  // - param.created date
  // - param.modified date
  // - param.tried number >= 0
  // - param.state string 'ready'
  // - param.method string
  // - param.storage_spec object
  // - param.kwargs object
  // - param.options object
  // - param.command object

  // list of job events:
  // - Job existence -> new, end
  // - Job execution -> started, stopped
  // - Job resolution -> resolved, rejected, notified, cancelled
  // - Job modification -> modified

  // emits actions 'job:resolve', 'job:reject' and 'job:notify'

  // uses `rest method` events
  // emits 'job:new' event

  shared.job_keys = arrayExtend(shared.job_keys || [], [
    "created",
    "modified",
    "tried",
    "state",
    "method",
    "storage_spec",
    "kwargs",
    "options"
  ]);

  function addCommandToJob(job) {
    job.command = {};
    job.command.resolve = function () {
      shared.emit('job:resolve', job, arguments);
    };
    job.command.success = job.command.resolve;
    job.command.reject = function () {
      shared.emit('job:reject', job, arguments);
    };
    job.command.error = job.command.reject;
    job.command.notify = function () {
      shared.emit('job:notify', job, arguments);
    };
    job.command.storage = function () {
      return shared.createRestApi.apply(null, arguments);
    };
  }

  function createJobFromRest(param) {
    if (param.solver) {
      // rest parameters are good
      shared.emit('job:new', param);
    }
  }

  function initJob(job) {
    job.state = 'ready';
    if (typeof job.tried !== 'number' || !isFinite(job.tried)) {
      job.tried = 0;
    }
    if (!job.created) {
      job.created = new Date();
    }
    addCommandToJob(job);
    job.modified = new Date();
  }

  // listeners

  shared.rest_method_names.forEach(function (method) {
    shared.on(method, createJobFromRest);
  });

  shared.on('job:new', initJob);

}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayExtend, localStorage, Workspace, uniqueJSONStringify, JobQueue,
  constants, setTimeout, clearTimeout */

function enableJobQueue(jio, shared, options) {

  // dependencies
  // - shared.storage_spec Object

  // uses
  // - options.workspace Workspace
  // - shared.job_keys String Array

  // creates
  // - shared.storage_spec_str String
  // - shared.workspace Workspace
  // - shared.job_queue JobQueue

  // uses 'job:new', 'job:started', 'job:stopped', 'job:modified',
  // 'job:notified', 'job:end' events

  // emits 'job:end' event

  function postJobIfReady(param) {
    if (!param.stored && param.state === 'ready') {
      clearTimeout(param.queue_ident);
      delete param.queue_ident;
      shared.job_queue.load();
      shared.job_queue.post(param);
      shared.job_queue.save();
      param.stored = true;
    }
  }

  function deferredPutJob(param) {
    if (param.queue_ident === undefined) {
      param.queue_ident = setTimeout(function () {
        delete param.queue_ident;
        if (param.stored) {
          shared.job_queue.load();
          shared.job_queue.put(param);
          shared.job_queue.save();
        }
      });
    }
  }

  function removeJob(param) {
    clearTimeout(param.queue_ident);
    delete param.queue_ident;
    if (param.stored) {
      shared.job_queue.load();
      shared.job_queue.remove(param.id);
      shared.job_queue.save();
      delete param.stored;
      delete param.id;
    }
  }

  function initJob(param) {
    if (!param.command.end) {
      param.command.end = function () {
        shared.emit('job:end', param);
      };
    }
  }

  shared.on('job:new', initJob);

  if (options.job_management !== false) {

    shared.job_keys = arrayExtend(shared.job_keys || [], ["id"]);

    if (typeof options.workspace !== 'object') {
      shared.workspace = localStorage;
    } else {
      shared.workspace = new Workspace(options.workspace);
    }

    if (!shared.storage_spec_str) {
      shared.storage_spec_str = uniqueJSONStringify(shared.storage_spec);
    }

    shared.job_queue = new JobQueue(
      shared.workspace,
      'jio/jobs/' + shared.storage_spec_str,
      shared.job_keys
    );

    // Listeners

    shared.on('job:new', postJobIfReady);

    shared.on('job:started', deferredPutJob);
    shared.on('job:stopped', deferredPutJob);
    shared.on('job:modified', deferredPutJob);
    shared.on('job:notified', deferredPutJob);

    shared.on('job:end', removeJob);

  }

}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global setTimeout, methodType */

function enableJobRecovery(jio, shared, options) {

  // dependencies
  // - JobQueue enabled and before this

  // uses
  // - shared.job_queue JobQueue

  // emits 'job:new' event

  function numberOrDefault(number, default_value) {
    return (typeof number === 'number' &&
            isFinite(number) ? number : default_value);
  }

  function recoverJob(param) {
    shared.job_queue.load();
    shared.job_queue.remove(param.id);
    delete param.id;
    if (methodType(param.method) === 'writer' &&
        (param.state === 'ready' ||
         param.state === 'running' ||
         param.state === 'waiting')) {
      shared.job_queue.save();
      shared.emit('job:new', param);
    }
  }

  function jobWaiter(id, modified) {
    return function () {
      var job;
      shared.job_queue.load();
      job = shared.job_queue.get(id);
      if (job && job.modified === modified) {
        // job not modified, no one takes care of it
        recoverJob(job);
      }
    };
  }

  var i, job_array, delay, deadline, recovery_delay;

  recovery_delay = numberOrDefault(options.recovery_delay, 10000);
  if (recovery_delay < 0) {
    recovery_delay = 10000;
  }

  if (options.job_management !== false && options.job_recovery !== false) {

    shared.job_queue.load();
    job_array = shared.job_queue.asArray();

    for (i = 0; i < job_array.length; i += 1) {
      delay = numberOrDefault(job_array[i].timeout + recovery_delay,
                              recovery_delay);
      deadline = new Date(job_array[i].modified).getTime() + delay;
      if (!isFinite(delay)) {
        // 'modified' date is broken
        recoverJob(job_array[i]);
      } else if (deadline <= Date.now()) {
        // deadline reached
        recoverJob(job_array[i]);
      } else {
        // deadline not reached yet
        // wait until deadline is reached then check job again
        setTimeout(jobWaiter(job_array[i].id, job_array[i].modified),
                   deadline - Date.now());
      }
    }

  }
}

/*jslint indent: 2, maxlen: 80, sloppy: true, unparam: true */
/*global ReferenceArray */

function enableJobReference(jio, shared, options) {

  // creates
  // - shared.jobs Object Array

  // uses 'job:new' and 'job:end' events

  shared.jobs = [];

  var job_references = new ReferenceArray(shared.jobs);

  shared.on('job:new', function (param) {
    job_references.put(param);
  });

  shared.on('job:end', function (param) {
    job_references.remove(param);
  });
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayExtend, setTimeout, methodType, constants */

function enableJobRetry(jio, shared, options) {

  // dependencies
  // - param.method
  // - param.storage_spec
  // - param.kwargs
  // - param.options
  // - param.command

  // uses
  // - options.default_writers_max_retry number >= 0 or null
  // - options.default_readers_max_retry number >= 0 or null
  // - options.default_max_retry number >= 0 or null
  // - options.writers_max_retry number >= 0 or null
  // - options.readers_max_retry number >= 0 or null
  // - options.max_retry number >= 0 or null
  // - param.modified date
  // - param.tried number >= 0
  // - param.max_retry >= 0 or undefined
  // - param.state string 'ready' 'waiting'
  // - param.method string
  // - param.storage_spec object
  // - param.kwargs object
  // - param.options object
  // - param.command object

  // uses 'job:new' and 'job:retry' events
  // emits action 'job:start' event
  // emits 'job:retry', 'job:reject', 'job:modified' and 'job:stopped' events

  shared.job_keys = arrayExtend(shared.job_keys || [], ["max_retry"]);

  var writers_max_retry, readers_max_retry, max_retry;

  function defaultMaxRetry(param) {
    if (methodType(param.method) === 'writers') {
      if (max_retry === undefined) {
        return writers_max_retry;
      }
      return max_retry;
    }
    if (max_retry === undefined) {
      return readers_max_retry;
    }
    return max_retry;
  }

  function positiveNumberOrDefault(number, default_value) {
    return (typeof number === 'number' &&
            number >= 0 ?
            number : default_value);
  }

  function positiveNumberNullOrDefault(number, default_value) {
    return ((typeof number === 'number' &&
            number >= 0) || number === null ?
            number : default_value);
  }

  max_retry = positiveNumberNullOrDefault(
    options.max_retry || options.default_max_retry,
    undefined
  );
  writers_max_retry = positiveNumberNullOrDefault(
    options.writers_max_retry || options.default_writers_max_retry,
    null
  );
  readers_max_retry = positiveNumberNullOrDefault(
    options.readers_max_retry || options.default_readers_max_retry,
    2
  );

  function initJob(param) {
    if (typeof param.max_retry !== 'number' || param.max_retry < 0) {
      param.max_retry = positiveNumberOrDefault(
        param.options.max_retry,
        defaultMaxRetry(param)
      );
    }
    param.command.reject = function (status) {
      if (constants.http_action[status || 0] === "retry") {
        shared.emit('job:retry', param, arguments);
      } else {
        shared.emit('job:reject', param, arguments);
      }
    };
    param.command.retry = function () {
      shared.emit('job:retry', param, arguments);
    };
  }

  function retryIfRunning(param, args) {
    if (param.state === 'running') {
      if (param.max_retry === undefined ||
          param.max_retry === null ||
          param.max_retry >= param.tried) {
        param.state = 'waiting';
        param.modified = new Date();
        shared.emit('job:modified', param);
        shared.emit('job:stopped', param);
        setTimeout(function () {
          param.state = 'ready';
          param.modified = new Date();
          shared.emit('job:modified', param);
          shared.emit('job:start', param);
        }, Math.min(10000, param.tried * 2000));
      } else {
        shared.emit('job:reject', param, args);
      }
    }
  }

  // listeners

  shared.on('job:new', initJob);

  shared.on('job:retry', retryIfRunning);
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayExtend, setTimeout, clearTimeout */

function enableJobTimeout(jio, shared, options) {

  // dependencies
  // - param.tried number > 0
  // - param.state string 'running'

  // uses
  // - param.tried number > 0
  // - param.timeout number >= 0
  // - param.timeout_ident Timeout
  // - param.state string 'running'

  // uses 'job:new', 'job:stopped', 'job:started',
  // 'job:notified' and 'job:end' events
  // emits 'job:modified' event

  shared.job_keys = arrayExtend(shared.job_keys || [], ["timeout"]);

  function positiveNumberOrDefault(number, default_value) {
    return (typeof number === 'number' &&
            number >= 0 ?
            number : default_value);
  }

  // 10 seconds by default
  var default_timeout = positiveNumberOrDefault(options.default_timeout, 10000);

  function timeoutReject(param) {
    return function () {
      param.command.reject(
        'request_timeout',
        'timeout',
        'Operation canceled after around ' + (
          Date.now() - param.modified.getTime()
        ) + ' milliseconds of inactivity.'
      );
    };
  }

  function initJob(job) {
    if (typeof job.timeout !== 'number' || job.timeout < 0) {
      job.timeout = positiveNumberOrDefault(
        job.options.timeout,
        default_timeout
      );
    }
    job.modified = new Date();
    shared.emit('job:modified', job);
  }

  function clearJobTimeout(job) {
    clearTimeout(job.timeout_ident);
    delete job.timeout_ident;
  }

  function restartJobTimeoutIfRunning(job) {
    clearTimeout(job.timeout_ident);
    if (job.state === 'running' && job.timeout > 0) {
      job.timeout_ident = setTimeout(timeoutReject(job), job.timeout);
      job.modified = new Date();
    } else {
      delete job.timeout_ident;
    }
  }

  // listeners

  shared.on('job:new', initJob);

  shared.on("job:stopped", clearJobTimeout);
  shared.on("job:end", clearJobTimeout);

  shared.on("job:started", restartJobTimeoutIfRunning);
  shared.on("job:notified", restartJobTimeoutIfRunning);
}

/*jslint indent: 2, maxlen: 80, sloppy: true */
/*global arrayValuesToTypeDict, dictClear, RSVP, deepClone */

// adds methods to JIO
// - post
// - put
// - get
// - remove
// - allDocs
// - putAttachment
// - getAttachment
// - removeAttachment
// - check
// - repair

// event shared objet
// - storage_spec object
// - method string
// - kwargs object
// - options object
// - solver object
// - solver.resolve function
// - solver.reject function
// - solver.notify function
// - cancellers object
// - promise object

function enableRestAPI(jio, shared) { // (jio, shared, options)

  shared.rest_method_names = [
    "post",
    "put",
    "get",
    "remove",
    "allDocs",
    "putAttachment",
    "getAttachment",
    "removeAttachment",
    "check",
    "repair"
  ];

  function prepareParamAndEmit(method, storage_spec, args) {
    var callback, type_dict, param = {};
    type_dict = arrayValuesToTypeDict(Array.prototype.slice.call(args));
    type_dict.object = type_dict.object || [];
    if (method !== 'allDocs') {
      param.kwargs = type_dict.object.shift();
      if (param.kwargs === undefined) {
        throw new TypeError("JIO()." + method +
                            "(): Argument 1 is not of type 'object'");
      }
      param.kwargs = deepClone(param.kwargs);
    } else {
      param.kwargs = {};
    }
    param.solver = {};
    param.options = deepClone(type_dict.object.shift()) || {};
    param.promise = new RSVP.Promise(function (resolve, reject, notify) {
      param.solver.resolve = resolve;
      param.solver.reject = reject;
      param.solver.notify = notify;
    }, function () {
      var k;
      for (k in param.cancellers) {
        if (param.cancellers.hasOwnProperty(k)) {
          param.cancellers[k]();
        }
      }
    });
    type_dict['function'] = type_dict['function'] || [];
    if (type_dict['function'].length === 1) {
      callback = type_dict['function'][0];
      param.promise.then(function (answer) {
        callback(undefined, answer);
      }, function (answer) {
        callback(answer, undefined);
      });
    } else if (type_dict['function'].length > 1) {
      param.promise.then(type_dict['function'][0],
                         type_dict['function'][1],
                         type_dict['function'][2]);
    }
    type_dict = dictClear(type_dict);
    param.storage_spec = storage_spec;
    param.method = method;
    shared.emit(method, param);
    return param.promise;
  }

  shared.createRestApi = function (storage_spec, that) {
    if (that === undefined) {
      that = {};
    }
    shared.rest_method_names.forEach(function (method) {
      that[method] = function () {
        return prepareParamAndEmit(method, storage_spec, arguments);
      };
    });
    return that;
  };

  shared.createRestApi(shared.storage_spec, jio);
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global Blob, restCommandRejecter, Metadata */

function enableRestParamChecker(jio, shared) {

  // dependencies
  // - param.solver
  // - param.kwargs

  // checks the kwargs and convert value if necessary

  // which is a dict of method to use to announce that
  // the command is finished


  // tools

  function checkId(param) {
    if (typeof param.kwargs._id !== 'string' || param.kwargs._id === '') {
      restCommandRejecter(param, [
        'bad_request',
        'wrong document id',
        'Document id must be a non empty string.'
      ]);
      delete param.solver;
      return false;
    }
    return true;
  }

  function checkAttachmentId(param) {
    if (typeof param.kwargs._attachment !== 'string' ||
        param.kwargs._attachment === '') {
      restCommandRejecter(param, [
        'bad_request',
        'wrong attachment id',
        'Attachment id must be a non empty string.'
      ]);
      delete param.solver;
      return false;
    }
    return true;
  }

  // listeners

  shared.on('post', function (param) {
    if (param.kwargs._id !== undefined) {
      if (!checkId(param)) {
        return;
      }
    }
    new Metadata(param.kwargs).format();
  });

  ["put", "get", "remove"].forEach(function (method) {
    shared.on(method, function (param) {
      if (!checkId(param)) {
        return;
      }
      new Metadata(param.kwargs).format();
    });
  });

  shared.on('putAttachment', function (param) {
    if (!checkId(param) || !checkAttachmentId(param)) {
      return;
    }
    if (!(param.kwargs._blob instanceof Blob) &&
        typeof param.kwargs._data === 'string') {
      param.kwargs._blob = new Blob([param.kwargs._data], {
        "type": param.kwargs._content_type || param.kwargs._mimetype || ""
      });
      delete param.kwargs._data;
      delete param.kwargs._mimetype;
      delete param.kwargs._content_type;
    } else if (param.kwargs._blob instanceof Blob) {
      delete param.kwargs._data;
      delete param.kwargs._mimetype;
      delete param.kwargs._content_type;
    } else if (param.kwargs._data instanceof Blob) {
      param.kwargs._blob = param.kwargs._data;
      delete param.kwargs._data;
      delete param.kwargs._mimetype;
      delete param.kwargs._content_type;
    } else {
      restCommandRejecter(param, [
        'bad_request',
        'wrong attachment',
        'Attachment information must be like {"_id": document id, ' +
          '"_attachment": attachment name, "_data": string, ["_mimetype": ' +
          'content type]} or {"_id": document id, "_attachment": ' +
          'attachment name, "_blob": Blob}'
      ]);
      delete param.solver;
    }
  });


  shared.on('getAttachment', function (param) {
    if (param.storage_spec.type !== "indexeddb" &&
        param.storage_spec.type !== "dav" &&
        (param.kwargs._start !== undefined ||
         param.kwargs._end !== undefined)) {
      restCommandRejecter(param, [
        'bad_request',
        'not support',
        'options _start, _end do not support.'
      ]);
      delete param.solver;
      return false;
    }
    if (!checkId(param)) {
      checkAttachmentId(param);
    }
  });


  shared.on('removeAttachment', function (param) {
    if (!checkId(param)) {
      checkAttachmentId(param);
    }
  });

/*
  ["getAttachment", "removeAttachment"].forEach(function (method) {
    shared.on(method, function (param) {
      if (!checkId(param)) {
        checkAttachmentId(param);
      }
    });
  });*/

  ["check", "repair"].forEach(function (method) {
    shared.on(method, function (param) {
      if (param.kwargs._id !== undefined) {
        if (!checkId(param)) {
          return;
        }
      }
    });
  });

}

/*jslint indent: 2, maxlen: 80, sloppy: true */

var query_class_dict = {};

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global parseStringToObject: true, emptyFunction: true, sortOn: true, limit:
  true, select: true, exports, stringEscapeRegexpCharacters: true,
  deepClone, RSVP, sequence */

/**
 * The query to use to filter a list of objects.
 * This is an abstract class.
 *
 * @class Query
 * @constructor
 */
function Query() {

  /**
   * Called before parsing the query. Must be overridden!
   *
   * @method onParseStart
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseStart = emptyFunction;

  /**
   * Called when parsing a simple query. Must be overridden!
   *
   * @method onParseSimpleQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseSimpleQuery = emptyFunction;

  /**
   * Called when parsing a complex query. Must be overridden!
   *
   * @method onParseComplexQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseComplexQuery = emptyFunction;

  /**
   * Called after parsing the query. Must be overridden!
   *
   * @method onParseEnd
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseEnd = emptyFunction;

}

/**
 * Filter the item list with matching item only
 *
 * @method exec
 * @param  {Array} item_list The list of object
 * @param  {Object} [option] Some operation option
 * @param  {Array} [option.select_list] A object keys to retrieve
 * @param  {Array} [option.sort_on] Couples of object keys and "ascending"
 *                 or "descending"
 * @param  {Array} [option.limit] Couple of integer, first is an index and
 *                 second is the length.
 */
Query.prototype.exec = function (item_list, option) {
  var i, promises = [];
  if (!Array.isArray(item_list)) {
    throw new TypeError("Query().exec(): Argument 1 is not of type 'array'");
  }
  if (option === undefined) {
    option = {};
  }
  if (typeof option !== 'object') {
    throw new TypeError("Query().exec(): " +
                        "Optional argument 2 is not of type 'object'");
  }
  for (i = 0; i < item_list.length; i += 1) {
    if (!item_list[i]) {
      promises.push(RSVP.resolve(false));
    } else {
      promises.push(this.match(item_list[i]));
    }
  }
  return sequence([function () {
    return RSVP.all(promises);
  }, function (answers) {
    var j;
    for (j = answers.length - 1; j >= 0; j -= 1) {
      if (!answers[j]) {
        item_list.splice(j, 1);
      }
    }
    if (option.sort_on) {
      return sortOn(option.sort_on, item_list);
    }
  }, function () {
    if (option.limit) {
      return limit(option.limit, item_list);
    }
  }, function () {
    return select(option.select_list || [], item_list);
  }, function () {
    return item_list;
  }]);
};

/**
 * Test if an item matches this query
 *
 * @method match
 * @param  {Object} item The object to test
 * @return {Boolean} true if match, false otherwise
 */
Query.prototype.match = function () {
  return RSVP.resolve(true);
};


/**
 * Browse the Query in deep calling parser method in each step.
 *
 * `onParseStart` is called first, on end `onParseEnd` is called.
 * It starts from the simple queries at the bottom of the tree calling the
 * parser method `onParseSimpleQuery`, and go up calling the
 * `onParseComplexQuery` method.
 *
 * @method parse
 * @param  {Object} option Any options you want (except 'parsed')
 * @return {Any} The parse result
 */
Query.prototype.parse = function (option) {
  var that = this, object;
  /**
   * The recursive parser.
   *
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} options Some options usable in the parseMethods
   * @return {Any} The parser result
   */
  function recParse(object, option) {
    var query = object.parsed;
    if (query.type === "complex") {
      return sequence([function () {
        return sequence(query.query_list.map(function (v, i) {
          /*jslint unparam: true */
          return function () {
            return sequence([function () {
              object.parsed = query.query_list[i];
              return recParse(object, option);
            }, function () {
              query.query_list[i] = object.parsed;
            }]);
          };
        }));
      }, function () {
        object.parsed = query;
        return that.onParseComplexQuery(object, option);
      }]);
    }
    if (query.type === "simple") {
      return that.onParseSimpleQuery(object, option);
    }
  }
  object = {"parsed": JSON.parse(JSON.stringify(that.serialized()))};
  return sequence([function () {
    return that.onParseStart(object, option);
  }, function () {
    return recParse(object, option);
  }, function () {
    return that.onParseEnd(object, option);
  }, function () {
    return object.parsed;
  }]);
};

/**
 * Convert this query to a parsable string.
 *
 * @method toString
 * @return {String} The string version of this query
 */
Query.prototype.toString = function () {
  return "";
};

/**
 * Convert this query to an jsonable object in order to be remake thanks to
 * QueryFactory class.
 *
 * @method serialized
 * @return {Object} The jsonable object
 */
Query.prototype.serialized = function () {
  return undefined;
};

exports.Query = Query;

/**
 * Parse a text request to a json query object tree
 *
 * @param  {String} string The string to parse
 * @return {Object} The json query tree
 */
function parseStringToObject(string) {


/*
	Default template driver for JS/CC generated parsers running as
	browser-based JavaScript/ECMAScript applications.
	
	WARNING: 	This parser template will not run as console and has lesser
				features for debugging than the console derivates for the
				various JavaScript platforms.
	
	Features:
	- Parser trace messages
	- Integrated panic-mode error recovery
	
	Written 2007, 2008 by Jan Max Meyer, J.M.K S.F. Software Technologies
	
	This is in the public domain.
*/

var NODEJS__dbg_withtrace		= false;
var NODEJS__dbg_string			= new String();

function __NODEJS_dbg_print( text )
{
	NODEJS__dbg_string += text + "\n";
}

function __NODEJS_lex( info )
{
	var state		= 0;
	var match		= -1;
	var match_pos	= 0;
	var start		= 0;
	var pos			= info.offset + 1;

	do
	{
		pos--;
		state = 0;
		match = -2;
		start = pos;

		if( info.src.length <= start )
			return 19;

		do
		{

switch( state )
{
	case 0:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 8 ) || ( info.src.charCodeAt( pos ) >= 10 && info.src.charCodeAt( pos ) <= 31 ) || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || info.src.charCodeAt( pos ) == 59 || ( info.src.charCodeAt( pos ) >= 63 && info.src.charCodeAt( pos ) <= 64 ) || ( info.src.charCodeAt( pos ) >= 66 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 9 ) state = 2;
		else if( info.src.charCodeAt( pos ) == 40 ) state = 3;
		else if( info.src.charCodeAt( pos ) == 41 ) state = 4;
		else if( info.src.charCodeAt( pos ) == 60 || info.src.charCodeAt( pos ) == 62 ) state = 5;
		else if( info.src.charCodeAt( pos ) == 33 ) state = 11;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 12;
		else if( info.src.charCodeAt( pos ) == 32 ) state = 13;
		else if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else if( info.src.charCodeAt( pos ) == 34 ) state = 15;
		else if( info.src.charCodeAt( pos ) == 65 ) state = 19;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 20;
		else state = -1;
		break;

	case 1:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 2:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 3:
		state = -1;
		match = 3;
		match_pos = pos;
		break;

	case 4:
		state = -1;
		match = 4;
		match_pos = pos;
		break;

	case 5:
		if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 6:
		state = -1;
		match = 8;
		match_pos = pos;
		break;

	case 7:
		state = -1;
		match = 9;
		match_pos = pos;
		break;

	case 8:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 6;
		match_pos = pos;
		break;

	case 9:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 5;
		match_pos = pos;
		break;

	case 10:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 7;
		match_pos = pos;
		break;

	case 11:
		if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else state = -1;
		break;

	case 12:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 81 ) || ( info.src.charCodeAt( pos ) >= 83 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 82 ) state = 8;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 13:
		state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 14:
		state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 15:
		if( info.src.charCodeAt( pos ) == 34 ) state = 7;
		else if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 33 ) || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 91 ) || ( info.src.charCodeAt( pos ) >= 93 && info.src.charCodeAt( pos ) <= 254 ) ) state = 15;
		else if( info.src.charCodeAt( pos ) == 92 ) state = 17;
		else state = -1;
		break;

	case 16:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 67 ) || ( info.src.charCodeAt( pos ) >= 69 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 68 ) state = 9;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 17:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 254 ) ) state = 15;
		else state = -1;
		break;

	case 18:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 83 ) || ( info.src.charCodeAt( pos ) >= 85 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 84 ) state = 10;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 19:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 79 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 16;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 20:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 78 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 18;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

}


			pos++;

		}
		while( state > -1 );

	}
	while( 1 > -1 && match == 1 );

	if( match > -1 )
	{
		info.att = info.src.substr( start, match_pos - start );
		info.offset = match_pos;
		

	}
	else
	{
		info.att = new String();
		match = -1;
	}

	return match;
}


function __NODEJS_parse( src, err_off, err_la )
{
	var		sstack			= new Array();
	var		vstack			= new Array();
	var 	err_cnt			= 0;
	var		act;
	var		go;
	var		la;
	var		rval;
	var 	parseinfo		= new Function( "", "var offset; var src; var att;" );
	var		info			= new parseinfo();
	
/* Pop-Table */
var pop_tab = new Array(
	new Array( 0/* begin' */, 1 ),
	new Array( 13/* begin */, 1 ),
	new Array( 12/* search_text */, 1 ),
	new Array( 12/* search_text */, 2 ),
	new Array( 12/* search_text */, 3 ),
	new Array( 14/* and_expression */, 1 ),
	new Array( 14/* and_expression */, 3 ),
	new Array( 15/* boolean_expression */, 2 ),
	new Array( 15/* boolean_expression */, 1 ),
	new Array( 16/* expression */, 3 ),
	new Array( 16/* expression */, 2 ),
	new Array( 16/* expression */, 1 ),
	new Array( 17/* value */, 2 ),
	new Array( 17/* value */, 1 ),
	new Array( 18/* string */, 1 ),
	new Array( 18/* string */, 1 )
);

/* Action-Table */
var act_tab = new Array(
	/* State 0 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 1 */ new Array( 19/* "$" */,0 ),
	/* State 2 */ new Array( 19/* "$" */,-1 ),
	/* State 3 */ new Array( 6/* "OR" */,14 , 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 , 19/* "$" */,-2 , 4/* "RIGHT_PARENTHESE" */,-2 ),
	/* State 4 */ new Array( 5/* "AND" */,16 , 19/* "$" */,-5 , 7/* "NOT" */,-5 , 3/* "LEFT_PARENTHESE" */,-5 , 8/* "COLUMN" */,-5 , 11/* "OPERATOR" */,-5 , 10/* "WORD" */,-5 , 9/* "STRING" */,-5 , 6/* "OR" */,-5 , 4/* "RIGHT_PARENTHESE" */,-5 ),
	/* State 5 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 6 */ new Array( 19/* "$" */,-8 , 7/* "NOT" */,-8 , 3/* "LEFT_PARENTHESE" */,-8 , 8/* "COLUMN" */,-8 , 11/* "OPERATOR" */,-8 , 10/* "WORD" */,-8 , 9/* "STRING" */,-8 , 6/* "OR" */,-8 , 5/* "AND" */,-8 , 4/* "RIGHT_PARENTHESE" */,-8 ),
	/* State 7 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 8 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 9 */ new Array( 19/* "$" */,-11 , 7/* "NOT" */,-11 , 3/* "LEFT_PARENTHESE" */,-11 , 8/* "COLUMN" */,-11 , 11/* "OPERATOR" */,-11 , 10/* "WORD" */,-11 , 9/* "STRING" */,-11 , 6/* "OR" */,-11 , 5/* "AND" */,-11 , 4/* "RIGHT_PARENTHESE" */,-11 ),
	/* State 10 */ new Array( 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 11 */ new Array( 19/* "$" */,-13 , 7/* "NOT" */,-13 , 3/* "LEFT_PARENTHESE" */,-13 , 8/* "COLUMN" */,-13 , 11/* "OPERATOR" */,-13 , 10/* "WORD" */,-13 , 9/* "STRING" */,-13 , 6/* "OR" */,-13 , 5/* "AND" */,-13 , 4/* "RIGHT_PARENTHESE" */,-13 ),
	/* State 12 */ new Array( 19/* "$" */,-14 , 7/* "NOT" */,-14 , 3/* "LEFT_PARENTHESE" */,-14 , 8/* "COLUMN" */,-14 , 11/* "OPERATOR" */,-14 , 10/* "WORD" */,-14 , 9/* "STRING" */,-14 , 6/* "OR" */,-14 , 5/* "AND" */,-14 , 4/* "RIGHT_PARENTHESE" */,-14 ),
	/* State 13 */ new Array( 19/* "$" */,-15 , 7/* "NOT" */,-15 , 3/* "LEFT_PARENTHESE" */,-15 , 8/* "COLUMN" */,-15 , 11/* "OPERATOR" */,-15 , 10/* "WORD" */,-15 , 9/* "STRING" */,-15 , 6/* "OR" */,-15 , 5/* "AND" */,-15 , 4/* "RIGHT_PARENTHESE" */,-15 ),
	/* State 14 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 15 */ new Array( 19/* "$" */,-3 , 4/* "RIGHT_PARENTHESE" */,-3 ),
	/* State 16 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 17 */ new Array( 19/* "$" */,-7 , 7/* "NOT" */,-7 , 3/* "LEFT_PARENTHESE" */,-7 , 8/* "COLUMN" */,-7 , 11/* "OPERATOR" */,-7 , 10/* "WORD" */,-7 , 9/* "STRING" */,-7 , 6/* "OR" */,-7 , 5/* "AND" */,-7 , 4/* "RIGHT_PARENTHESE" */,-7 ),
	/* State 18 */ new Array( 4/* "RIGHT_PARENTHESE" */,23 ),
	/* State 19 */ new Array( 19/* "$" */,-10 , 7/* "NOT" */,-10 , 3/* "LEFT_PARENTHESE" */,-10 , 8/* "COLUMN" */,-10 , 11/* "OPERATOR" */,-10 , 10/* "WORD" */,-10 , 9/* "STRING" */,-10 , 6/* "OR" */,-10 , 5/* "AND" */,-10 , 4/* "RIGHT_PARENTHESE" */,-10 ),
	/* State 20 */ new Array( 19/* "$" */,-12 , 7/* "NOT" */,-12 , 3/* "LEFT_PARENTHESE" */,-12 , 8/* "COLUMN" */,-12 , 11/* "OPERATOR" */,-12 , 10/* "WORD" */,-12 , 9/* "STRING" */,-12 , 6/* "OR" */,-12 , 5/* "AND" */,-12 , 4/* "RIGHT_PARENTHESE" */,-12 ),
	/* State 21 */ new Array( 19/* "$" */,-4 , 4/* "RIGHT_PARENTHESE" */,-4 ),
	/* State 22 */ new Array( 19/* "$" */,-6 , 7/* "NOT" */,-6 , 3/* "LEFT_PARENTHESE" */,-6 , 8/* "COLUMN" */,-6 , 11/* "OPERATOR" */,-6 , 10/* "WORD" */,-6 , 9/* "STRING" */,-6 , 6/* "OR" */,-6 , 4/* "RIGHT_PARENTHESE" */,-6 ),
	/* State 23 */ new Array( 19/* "$" */,-9 , 7/* "NOT" */,-9 , 3/* "LEFT_PARENTHESE" */,-9 , 8/* "COLUMN" */,-9 , 11/* "OPERATOR" */,-9 , 10/* "WORD" */,-9 , 9/* "STRING" */,-9 , 6/* "OR" */,-9 , 5/* "AND" */,-9 , 4/* "RIGHT_PARENTHESE" */,-9 )
);

/* Goto-Table */
var goto_tab = new Array(
	/* State 0 */ new Array( 13/* begin */,1 , 12/* search_text */,2 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 1 */ new Array(  ),
	/* State 2 */ new Array(  ),
	/* State 3 */ new Array( 12/* search_text */,15 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 4 */ new Array(  ),
	/* State 5 */ new Array( 16/* expression */,17 , 17/* value */,9 , 18/* string */,11 ),
	/* State 6 */ new Array(  ),
	/* State 7 */ new Array( 12/* search_text */,18 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 8 */ new Array( 16/* expression */,19 , 17/* value */,9 , 18/* string */,11 ),
	/* State 9 */ new Array(  ),
	/* State 10 */ new Array( 18/* string */,20 ),
	/* State 11 */ new Array(  ),
	/* State 12 */ new Array(  ),
	/* State 13 */ new Array(  ),
	/* State 14 */ new Array( 12/* search_text */,21 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 15 */ new Array(  ),
	/* State 16 */ new Array( 14/* and_expression */,22 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 17 */ new Array(  ),
	/* State 18 */ new Array(  ),
	/* State 19 */ new Array(  ),
	/* State 20 */ new Array(  ),
	/* State 21 */ new Array(  ),
	/* State 22 */ new Array(  ),
	/* State 23 */ new Array(  )
);



/* Symbol labels */
var labels = new Array(
	"begin'" /* Non-terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"LEFT_PARENTHESE" /* Terminal symbol */,
	"RIGHT_PARENTHESE" /* Terminal symbol */,
	"AND" /* Terminal symbol */,
	"OR" /* Terminal symbol */,
	"NOT" /* Terminal symbol */,
	"COLUMN" /* Terminal symbol */,
	"STRING" /* Terminal symbol */,
	"WORD" /* Terminal symbol */,
	"OPERATOR" /* Terminal symbol */,
	"search_text" /* Non-terminal symbol */,
	"begin" /* Non-terminal symbol */,
	"and_expression" /* Non-terminal symbol */,
	"boolean_expression" /* Non-terminal symbol */,
	"expression" /* Non-terminal symbol */,
	"value" /* Non-terminal symbol */,
	"string" /* Non-terminal symbol */,
	"$" /* Terminal symbol */
);


	
	info.offset = 0;
	info.src = src;
	info.att = new String();
	
	if( !err_off )
		err_off	= new Array();
	if( !err_la )
	err_la = new Array();
	
	sstack.push( 0 );
	vstack.push( 0 );
	
	la = __NODEJS_lex( info );

	while( true )
	{
		act = 25;
		for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
		{
			if( act_tab[sstack[sstack.length-1]][i] == la )
			{
				act = act_tab[sstack[sstack.length-1]][i+1];
				break;
			}
		}

		if( NODEJS__dbg_withtrace && sstack.length > 0 )
		{
			__NODEJS_dbg_print( "\nState " + sstack[sstack.length-1] + "\n" +
							"\tLookahead: " + labels[la] + " (\"" + info.att + "\")\n" +
							"\tAction: " + act + "\n" + 
							"\tSource: \"" + info.src.substr( info.offset, 30 ) + ( ( info.offset + 30 < info.src.length ) ?
									"..." : "" ) + "\"\n" +
							"\tStack: " + sstack.join() + "\n" +
							"\tValue stack: " + vstack.join() + "\n" );
		}
		
			
		//Panic-mode: Try recovery when parse-error occurs!
		if( act == 25 )
		{
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Error detected: There is no reduce or shift on the symbol " + labels[la] );
			
			err_cnt++;
			err_off.push( info.offset - info.att.length );			
			err_la.push( new Array() );
			for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
				err_la[err_la.length-1].push( labels[act_tab[sstack[sstack.length-1]][i]] );
			
			//Remember the original stack!
			var rsstack = new Array();
			var rvstack = new Array();
			for( var i = 0; i < sstack.length; i++ )
			{
				rsstack[i] = sstack[i];
				rvstack[i] = vstack[i];
			}
			
			while( act == 25 && la != 19 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery\n" +
									"Current lookahead: " + labels[la] + " (" + info.att + ")\n" +
									"Action: " + act + "\n\n" );
				if( la == -1 )
					info.offset++;
					
				while( act == 25 && sstack.length > 0 )
				{
					sstack.pop();
					vstack.pop();
					
					if( sstack.length == 0 )
						break;
						
					act = 25;
					for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
					{
						if( act_tab[sstack[sstack.length-1]][i] == la )
						{
							act = act_tab[sstack[sstack.length-1]][i+1];
							break;
						}
					}
				}
				
				if( act != 25 )
					break;
				
				for( var i = 0; i < rsstack.length; i++ )
				{
					sstack.push( rsstack[i] );
					vstack.push( rvstack[i] );
				}
				
				la = __NODEJS_lex( info );
			}
			
			if( act == 25 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery failed, terminating parse process..." );
				break;
			}


			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tError recovery succeeded, continuing" );
		}
		
		/*
		if( act == 25 )
			break;
		*/
		
		
		//Shift
		if( act > 0 )
		{			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Shifting symbol: " + labels[la] + " (" + info.att + ")" );
		
			sstack.push( act );
			vstack.push( info.att );
			
			la = __NODEJS_lex( info );
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tNew lookahead symbol: " + labels[la] + " (" + info.att + ")" );
		}
		//Reduce
		else
		{		
			act *= -1;
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Reducing by producution: " + act );
			
			rval = void(0);
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPerforming semantic action..." );
			
switch( act )
{
	case 0:
	{
		rval = vstack[ vstack.length - 1 ];
	}
	break;
	case 1:
	{
		 result = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 2:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 3:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 2 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 4:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 5:
	{
		 rval = vstack[ vstack.length - 1 ] ; 
	}
	break;
	case 6:
	{
		 rval = mkComplexQuery('AND',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 7:
	{
		 rval = mkNotQuery(vstack[ vstack.length - 1 ]); 
	}
	break;
	case 8:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 9:
	{
		 rval = vstack[ vstack.length - 2 ]; 
	}
	break;
	case 10:
	{
		 simpleQuerySetKey(vstack[ vstack.length - 1 ],vstack[ vstack.length - 2 ].split(':').slice(0,-1).join(':')); rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 11:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 12:
	{
		 vstack[ vstack.length - 1 ].operator = vstack[ vstack.length - 2 ] ; rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 13:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 14:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ]); 
	}
	break;
	case 15:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ].split('"').slice(1,-1).join('"')); 
	}
	break;
}



			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPopping " + pop_tab[act][1] + " off the stack..." );
				
			for( var i = 0; i < pop_tab[act][1]; i++ )
			{
				sstack.pop();
				vstack.pop();
			}
									
			go = -1;
			for( var i = 0; i < goto_tab[sstack[sstack.length-1]].length; i+=2 )
			{
				if( goto_tab[sstack[sstack.length-1]][i] == pop_tab[act][0] )
				{
					go = goto_tab[sstack[sstack.length-1]][i+1];
					break;
				}
			}
			
			if( act == 0 )
				break;
				
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPushing non-terminal " + labels[ pop_tab[act][0] ] );
				
			sstack.push( go );
			vstack.push( rval );			
		}
		
		if( NODEJS__dbg_withtrace )
		{		
			alert( NODEJS__dbg_string );
			NODEJS__dbg_string = new String();
		}
	}

	if( NODEJS__dbg_withtrace )
	{
		__NODEJS_dbg_print( "\nParse complete." );
		alert( NODEJS__dbg_string );
	}
	
	return err_cnt;
}



var arrayExtend = function () {
  var j, i, newlist = [], list_list = arguments;
  for (j = 0; j < list_list.length; j += 1) {
    for (i = 0; i < list_list[j].length; i += 1) {
      newlist.push(list_list[j][i]);
    }
  }
  return newlist;

}, mkSimpleQuery = function (key, value, operator) {
  var object = {"type": "simple", "key": key, "value": value};
  if (operator !== undefined) {
    object.operator = operator;
  }
  return object;

}, mkNotQuery = function (query) {
  if (query.operator === "NOT") {
    return query.query_list[0];
  }
  return {"type": "complex", "operator": "NOT", "query_list": [query]};

}, mkComplexQuery = function (operator, query_list) {
  var i, query_list2 = [];
  for (i = 0; i < query_list.length; i += 1) {
    if (query_list[i].operator === operator) {
      query_list2 = arrayExtend(query_list2, query_list[i].query_list);
    } else {
      query_list2.push(query_list[i]);
    }
  }
  return {type:"complex",operator:operator,query_list:query_list2};

}, simpleQuerySetKey = function (query, key) {
  var i;
  if (query.type === "complex") {
    for (i = 0; i < query.query_list.length; ++i) {
      simpleQuerySetKey (query.query_list[i],key);
    }
    return true;
  }
  if (query.type === "simple" && !query.key) {
    query.key = key;
    return true;
  }
  return false;
},
  error_offsets = [],
  error_lookaheads = [],
  error_count = 0,
  result;

if ((error_count = __NODEJS_parse(string, error_offsets, error_lookaheads)) > 0) {
  var i;
  for (i = 0; i < error_count; i += 1) {
    throw new Error("Parse error near \"" +
                    string.substr(error_offsets[i]) +
                    "\", expecting \"" +
                    error_lookaheads[i].join() + "\"");
  }
}


  return result;
} // parseStringToObject

Query.parseStringToObject = parseStringToObject;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query: true, query_class_dict: true, inherits: true,
         exports, QueryFactory, RSVP, sequence */

/**
 * The ComplexQuery inherits from Query, and compares one or several metadata
 * values.
 *
 * @class ComplexQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="AND"] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function ComplexQuery(spec, key_schema) {
  Query.call(this);

  /**
   * Logical operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @default "AND"
   * @optional
   */
  this.operator = spec.operator;

  /**
   * The sub Query list which are used to query an item.
   *
   * @attribute query_list
   * @type Array
   * @default []
   * @optional
   */
  this.query_list = spec.query_list || [];
  /*jslint unparam: true*/
  this.query_list = this.query_list.map(
    // decorate the map to avoid sending the index as key_schema argument
    function (o, i) { return QueryFactory.create(o, key_schema); }
  );
  /*jslint unparam: false*/

}
inherits(ComplexQuery, Query);

ComplexQuery.prototype.operator = "AND";
ComplexQuery.prototype.type = "complex";

/**
 * #crossLink "Query/match:method"
 */
ComplexQuery.prototype.match = function (item) {
  var operator = this.operator;
  if (!(/^(?:AND|OR|NOT)$/i.test(operator))) {
    operator = "AND";
  }
  return this[operator.toUpperCase()](item);
};

/**
 * #crossLink "Query/toString:method"
 */
ComplexQuery.prototype.toString = function () {
  var str_list = [], this_operator = this.operator;
  if (this.operator === "NOT") {
    str_list.push("NOT (");
    str_list.push(this.query_list[0].toString());
    str_list.push(")");
    return str_list.join(" ");
  }
  this.query_list.forEach(function (query) {
    str_list.push("(");
    str_list.push(query.toString());
    str_list.push(")");
    str_list.push(this_operator);
  });
  str_list.length -= 1;
  return str_list.join(" ");
};

/**
 * #crossLink "Query/serialized:method"
 */
ComplexQuery.prototype.serialized = function () {
  var s = {
    "type": "complex",
    "operator": this.operator,
    "query_list": []
  };
  this.query_list.forEach(function (query) {
    s.query_list.push(
      typeof query.toJSON === "function" ? query.toJSON() : query
    );
  });
  return s;
};
ComplexQuery.prototype.toJSON = ComplexQuery.prototype.serialized;

/**
 * Comparison operator, test if all sub queries match the
 * item value
 *
 * @method AND
 * @param  {Object} item The item to match
 * @return {Boolean} true if all match, false otherwise
 */
ComplexQuery.prototype.AND = function (item) {
  var j, promises = [];
  for (j = 0; j < this.query_list.length; j += 1) {
    promises.push(this.query_list[j].match(item));
  }

  function cancel() {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      if (typeof promises.cancel === 'function') {
        promises.cancel();
      }
    }
  }

  return new RSVP.Promise(function (resolve, reject) {
    var i, count = 0;
    function resolver(value) {
      if (!value) {
        resolve(false);
      }
      count += 1;
      if (count === promises.length) {
        resolve(true);
      }
    }

    function rejecter(err) {
      reject(err);
      cancel();
    }

    for (i = 0; i < promises.length; i += 1) {
      promises[i].then(resolver, rejecter);
    }
  }, cancel);
};

/**
 * Comparison operator, test if one of the sub queries matches the
 * item value
 *
 * @method OR
 * @param  {Object} item The item to match
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.OR =  function (item) {
  var j, promises = [];
  for (j = 0; j < this.query_list.length; j += 1) {
    promises.push(this.query_list[j].match(item));
  }

  function cancel() {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      if (typeof promises.cancel === 'function') {
        promises.cancel();
      }
    }
  }

  return new RSVP.Promise(function (resolve, reject) {
    var i, count = 0;
    function resolver(value) {
      if (value) {
        resolve(true);
      }
      count += 1;
      if (count === promises.length) {
        resolve(false);
      }
    }

    function rejecter(err) {
      reject(err);
      cancel();
    }

    for (i = 0; i < promises.length; i += 1) {
      promises[i].then(resolver, rejecter);
    }
  }, cancel);
};

/**
 * Comparison operator, test if the sub query does not match the
 * item value
 *
 * @method NOT
 * @param  {Object} item The item to match
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.NOT = function (item) {
  return sequence([function () {
    return this.query_list[0].match(item);
  }, function (answer) {
    return !answer;
  }]);
};

query_class_dict.complex = ComplexQuery;

exports.ComplexQuery = ComplexQuery;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global exports, ComplexQuery, SimpleQuery, Query, parseStringToObject,
  query_class_dict */

/**
 * Provides static methods to create Query object
 *
 * @class QueryFactory
 */
function QueryFactory() {
  return;
}

/**
 * Creates Query object from a search text string or a serialized version
 * of a Query.
 *
 * @method create
 * @static
 * @param  {Object,String} object The search text or the serialized version
 *         of a Query
 * @return {Query} A Query object
 */
QueryFactory.create = function (object, key_schema) {
  if (object === "") {
    return new Query();
  }
  if (typeof object === "string") {
    object = parseStringToObject(object);
  }
  if (typeof (object || {}).type === "string" &&
      query_class_dict[object.type]) {
    return new query_class_dict[object.type](object, key_schema);
  }
  throw new TypeError("QueryFactory.create(): " +
                      "Argument 1 is not a search text or a parsable object");
};

exports.QueryFactory = QueryFactory;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query, exports */

function objectToSearchText(query) {
  var str_list = [];
  if (query.type === "complex") {
    str_list.push("(");
    (query.query_list || []).forEach(function (sub_query) {
      str_list.push(objectToSearchText(sub_query));
      str_list.push(query.operator);
    });
    str_list.length -= 1;
    str_list.push(")");
    return str_list.join(" ");
  }
  if (query.type === "simple") {
    return (query.key ? query.key + ": " : "") +
      (query.operator || "") + ' "' + query.value + '"';
  }
  throw new TypeError("This object is not a query");
}
Query.objectToSearchText = objectToSearchText;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query, inherits, query_class_dict, exports,
  searchTextToRegExp, RSVP */

var checkKeySchema = function (key_schema) {
  var prop;

  if (key_schema !== undefined) {
    if (typeof key_schema !== 'object') {
      throw new TypeError("SimpleQuery().create(): " +
                          "key_schema is not of type 'object'");
    }
    // key_set is mandatory
    if (key_schema.key_set === undefined) {
      throw new TypeError("SimpleQuery().create(): " +
                          "key_schema has no 'key_set' property");
    }
    for (prop in key_schema) {
      if (key_schema.hasOwnProperty(prop)) {
        switch (prop) {
        case 'key_set':
        case 'cast_lookup':
        case 'match_lookup':
          break;
        default:
          throw new TypeError("SimpleQuery().create(): " +
                             "key_schema has unknown property '" + prop + "'");
        }
      }
    }
  }
};


/**
 * The SimpleQuery inherits from Query, and compares one metadata value
 *
 * @class SimpleQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="="] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function SimpleQuery(spec, key_schema) {
  Query.call(this);

  checkKeySchema(key_schema);

  this._key_schema = key_schema || {};

  /**
   * Operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @optional
   */
  this.operator = spec.operator;

  /**
   * Key of the object which refers to the value to compare
   *
   * @attribute key
   * @type String
   */
  this.key = spec.key;

  /**
   * Value is used to do the comparison with the object value
   *
   * @attribute value
   * @type String
   */
  this.value = spec.value;

}
inherits(SimpleQuery, Query);

SimpleQuery.prototype.type = "simple";

var checkKey = function (key) {
  var prop;

  if (key.read_from === undefined) {
    throw new TypeError("Custom key is missing the read_from property");
  }

  for (prop in key) {
    if (key.hasOwnProperty(prop)) {
      switch (prop) {
      case 'read_from':
      case 'cast_to':
      case 'equal_match':
        break;
      default:
        throw new TypeError("Custom key has unknown property '" +
                            prop + "'");
      }
    }
  }
};


/**
 * #crossLink "Query/match:method"
 */
SimpleQuery.prototype.match = function (item) {
  var object_value = null,
    equal_match = null,
    cast_to = null,
    matchMethod = null,
    operator = this.operator,
    value = null,
    key = this.key;

  /*jslint regexp: true */
  if (!(/^(?:!?=|<=?|>=?)$/i.test(operator))) {
    // `operator` is not correct, we have to change it to "like" or "="
    if (/%/.test(this.value)) {
      // `value` contains a non escaped `%`
      operator = "like";
    } else {
      // `value` does not contain non escaped `%`
      operator = "=";
    }
  }

  matchMethod = this[operator];

  if (this._key_schema.key_set && this._key_schema.key_set[key] !== undefined) {
    key = this._key_schema.key_set[key];
  }

  if (typeof key === 'object') {
    checkKey(key);
    object_value = item[key.read_from];

    equal_match = key.equal_match;

    // equal_match can be a string
    if (typeof equal_match === 'string') {
      // XXX raise error if equal_match not in match_lookup
      equal_match = this._key_schema.match_lookup[equal_match];
    }

    // equal_match overrides the default '=' operator
    if (equal_match !== undefined) {
      matchMethod = (operator === "=" || operator === "like" ?
                     equal_match : matchMethod);
    }

    value = this.value;
    cast_to = key.cast_to;
    if (cast_to) {
      // cast_to can be a string
      if (typeof cast_to === 'string') {
        // XXX raise error if cast_to not in cast_lookup
        cast_to = this._key_schema.cast_lookup[cast_to];
      }

      try {
        value = cast_to(value);
      } catch (e) {
        value = undefined;
      }

      try {
        object_value = cast_to(object_value);
      } catch (e) {
        object_value = undefined;
      }
    }
  } else {
    object_value = item[key];
    value = this.value;
  }
  if (object_value === undefined || value === undefined) {
    return RSVP.resolve(false);
  }
  return matchMethod(object_value, value);
};

/**
 * #crossLink "Query/toString:method"
 */
SimpleQuery.prototype.toString = function () {
  return (this.key ? this.key + ":" : "") +
    (this.operator ? " " + this.operator : "") + ' "' + this.value + '"';
};

/**
 * #crossLink "Query/serialized:method"
 */
SimpleQuery.prototype.serialized = function () {
  var object = {
    "type": "simple",
    "key": this.key,
    "value": this.value
  };
  if (this.operator !== undefined) {
    object.operator = this.operator;
  }
  return object;
};
SimpleQuery.prototype.toJSON = SimpleQuery.prototype.serialized;

/**
 * Comparison operator, test if this query value matches the item value
 *
 * @method =
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if match, false otherwise
 */
SimpleQuery.prototype["="] = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) === 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString(), false).
        test(value.toString())
    ) {
      return RSVP.resolve(true);
    }
  }
  return RSVP.resolve(false);
};

/**
 * Comparison operator, test if this query value matches the item value
 *
 * @method like
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if match, false otherwise
 */
SimpleQuery.prototype.like = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) === 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString()).test(value.toString())
    ) {
      return RSVP.resolve(true);
    }
  }
  return RSVP.resolve(false);
};

/**
 * Comparison operator, test if this query value does not match the item value
 *
 * @method !=
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if not match, false otherwise
 */
SimpleQuery.prototype["!="] = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) !== 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString(), false).
        test(value.toString())
    ) {
      return RSVP.resolve(false);
    }
  }
  return RSVP.resolve(true);
};

/**
 * Comparison operator, test if this query value is lower than the item value
 *
 * @method <
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if lower, false otherwise
 */
SimpleQuery.prototype["<"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) < 0);
  }
  return RSVP.resolve(value < comparison_value);
};

/**
 * Comparison operator, test if this query value is equal or lower than the
 * item value
 *
 * @method <=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or lower, false otherwise
 */
SimpleQuery.prototype["<="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) <= 0);
  }
  return RSVP.resolve(value <= comparison_value);
};

/**
 * Comparison operator, test if this query value is greater than the item
 * value
 *
 * @method >
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if greater, false otherwise
 */
SimpleQuery.prototype[">"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) > 0);
  }
  return RSVP.resolve(value > comparison_value);
};

/**
 * Comparison operator, test if this query value is equal or greater than the
 * item value
 *
 * @method >=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or greater, false otherwise
 */
SimpleQuery.prototype[">="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) >= 0);
  }
  return RSVP.resolve(value >= comparison_value);
};

query_class_dict.simple = SimpleQuery;

exports.SimpleQuery = SimpleQuery;

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query, RSVP, deepClone */

/**
 * Escapes regexp special chars from a string.
 *
 * @param  {String} string The string to escape
 * @return {String} The escaped string
 */
function stringEscapeRegexpCharacters(string) {
  if (typeof string === "string") {
    return string.replace(/([\\\.\$\[\]\(\)\{\}\^\?\*\+\-])/g, "\\$1");
  }
  throw new TypeError("Query.stringEscapeRegexpCharacters(): " +
                      "Argument no 1 is not of type 'string'");
}

Query.stringEscapeRegexpCharacters = stringEscapeRegexpCharacters;

/**
 * Convert metadata values to array of strings. ex:
 *
 *     "a" -> ["a"],
 *     {"content": "a"} -> ["a"]
 *
 * @param  {Any} value The metadata value
 * @return {Array} The value in string array format
 */
function metadataValueToStringArray(value) {
  var i, new_value = [];
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    value = [value];
  }
  for (i = 0; i < value.length; i += 1) {
    if (typeof value[i] === 'object') {
      new_value[i] = value[i].content;
    } else {
      new_value[i] = value[i];
    }
  }
  return new_value;
}

/**
 * A sort function to sort items by key
 *
 * @param  {String} key The key to sort on
 * @param  {String} [way="ascending"] 'ascending' or 'descending'
 * @return {Function} The sort function
 */
function sortFunction(key, way) {
  if (way === 'descending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return 1;
        }
        if (b[i] === undefined) {
          return -1;
        }
        if (a[i] > b[i]) {
          return -1;
        }
        if (a[i] < b[i]) {
          return 1;
        }
      }
      return 0;
    };
  }
  if (way === 'ascending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return -1;
        }
        if (b[i] === undefined) {
          return 1;
        }
        if (a[i] > b[i]) {
          return 1;
        }
        if (a[i] < b[i]) {
          return -1;
        }
      }
      return 0;
    };
  }
  throw new TypeError("Query.sortFunction(): " +
                      "Argument 2 must be 'ascending' or 'descending'");
}

/**
 * Inherits the prototype methods from one constructor into another. The
 * prototype of `constructor` will be set to a new object created from
 * `superConstructor`.
 *
 * @param  {Function} constructor The constructor which inherits the super one
 * @param  {Function} superConstructor The super constructor
 */
function inherits(constructor, superConstructor) {
  constructor.super_ = superConstructor;
  constructor.prototype = Object.create(superConstructor.prototype, {
    "constructor": {
      "configurable": true,
      "enumerable": false,
      "writable": true,
      "value": constructor
    }
  });
}

/**
 * Does nothing
 */
function emptyFunction() {
  return;
}

/**
 * Filter a list of items, modifying them to select only wanted keys. If
 * `clone` is true, then the method will act on a cloned list.
 *
 * @param  {Array} select_option Key list to keep
 * @param  {Array} list The item list to filter
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function select(select_option, list, clone) {
  var i, j, new_item;
  if (!Array.isArray(select_option)) {
    throw new TypeError("jioquery.select(): " +
                        "Argument 1 is not of type Array");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("jioquery.select(): " +
                        "Argument 2 is not of type Array");
  }
  if (clone === true) {
    list = deepClone(list);
  }
  for (i = 0; i < list.length; i += 1) {
    new_item = {};
    for (j = 0; j < select_option.length; j += 1) {
      if (list[i].hasOwnProperty([select_option[j]])) {
        new_item[select_option[j]] = list[i][select_option[j]];
      }
    }
    for (j in new_item) {
      if (new_item.hasOwnProperty(j)) {
        list[i] = new_item;
        break;
      }
    }
  }
  return list;
}

Query.select = select;

/**
 * Sort a list of items, according to keys and directions. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} sort_on_option List of couples [key, direction]
 * @param  {Array} list The item list to sort
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function sortOn(sort_on_option, list, clone) {
  var sort_index;
  if (!Array.isArray(sort_on_option)) {
    throw new TypeError("jioquery.sortOn(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  for (sort_index = sort_on_option.length - 1; sort_index >= 0;
       sort_index -= 1) {
    list.sort(sortFunction(
      sort_on_option[sort_index][0],
      sort_on_option[sort_index][1]
    ));
  }
  return list;
}

Query.sortOn = sortOn;

/**
 * Limit a list of items, according to index and length. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} limit_option A couple [from, length]
 * @param  {Array} list The item list to limit
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function limit(limit_option, list, clone) {
  if (!Array.isArray(limit_option)) {
    throw new TypeError("jioquery.limit(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("jioquery.limit(): " +
                        "Argument 2 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  list.splice(0, limit_option[0]);
  if (limit_option[1]) {
    list.splice(limit_option[1]);
  }
  return list;
}

Query.limit = limit;

/**
 * Convert a search text to a regexp.
 *
 * @param  {String} string The string to convert
 * @param  {Boolean} [use_wildcard_character=true] Use wildcard "%" and "_"
 * @return {RegExp} The search text regexp
 */
function searchTextToRegExp(string, use_wildcard_characters) {
  if (typeof string !== 'string') {
    throw new TypeError("jioquery.searchTextToRegExp(): " +
                        "Argument 1 is not of type 'string'");
  }
  if (use_wildcard_characters === false) {
    return new RegExp("^" + stringEscapeRegexpCharacters(string) + "$");
  }
  return new RegExp("^" + stringEscapeRegexpCharacters(string).replace(
    /%/g,
    ".*"
  ).replace(
    /_/g,
    "."
  ) + "$");
}

Query.searchTextToRegExp = searchTextToRegExp;

/**
 * sequence(thens): Promise
 *
 * Executes a sequence of *then* callbacks. It acts like
 * `smth().then(callback).then(callback)...`. The first callback is called with
 * no parameter.
 *
 * Elements of `thens` array can be a function or an array contaning at most
 * three *then* callbacks: *onFulfilled*, *onRejected*, *onNotified*.
 *
 * When `cancel()` is executed, each then promises are cancelled at the same
 * time.
 *
 * @param  {Array} thens An array of *then* callbacks
 * @return {Promise} A new promise
 */
function sequence(thens) {
  var promises = [];
  return new RSVP.Promise(function (resolve, reject, notify) {
    var i;
    promises[0] = new RSVP.Promise(function (resolve) {
      resolve();
    });
    for (i = 0; i < thens.length; i += 1) {
      if (Array.isArray(thens[i])) {
        promises[i + 1] = promises[i].
          then(thens[i][0], thens[i][1], thens[i][2]);
      } else {
        promises[i + 1] = promises[i].then(thens[i]);
      }
    }
    promises[i].then(resolve, reject, notify);
  }, function () {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      promises[i].cancel();
    }
  });
}

}));
;/*
* Copyright 2013, Nexedi SA
* Released under the LGPL license.
* http://www.gnu.org/licenses/lgpl.html
*/

/**
 * Provides some function to use complex queries with item list
 *
 * @module complex_queries
 */
// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports);
  }
  window.complex_queries = {};
  module(window.complex_queries, RSVP);
}(['exports', 'rsvp'], function (to_export, RSVP) {
  "use strict";

  /**
   * Add a secured (write permission denied) property to an object.
   *
   * @param  {Object} object The object to fill
   * @param  {String} key The object key where to store the property
   * @param  {Any} value The value to store
   */
  function _export(key, value) {
    Object.defineProperty(to_export, key, {
      "configurable": false,
      "enumerable": true,
      "writable": false,
      "value": value
    });
  }

/**
 * Parse a text request to a json query object tree
 *
 * @param  {String} string The string to parse
 * @return {Object} The json query tree
 */
function parseStringToObject(string) {


/*
	Default template driver for JS/CC generated parsers running as
	browser-based JavaScript/ECMAScript applications.
	
	WARNING: 	This parser template will not run as console and has lesser
				features for debugging than the console derivates for the
				various JavaScript platforms.
	
	Features:
	- Parser trace messages
	- Integrated panic-mode error recovery
	
	Written 2007, 2008 by Jan Max Meyer, J.M.K S.F. Software Technologies
	
	This is in the public domain.
*/

var NODEJS__dbg_withtrace		= false;
var NODEJS__dbg_string			= new String();

function __NODEJS_dbg_print( text )
{
	NODEJS__dbg_string += text + "\n";
}

function __NODEJS_lex( info )
{
	var state		= 0;
	var match		= -1;
	var match_pos	= 0;
	var start		= 0;
	var pos			= info.offset + 1;

	do
	{
		pos--;
		state = 0;
		match = -2;
		start = pos;

		if( info.src.length <= start )
			return 19;

		do
		{

switch( state )
{
	case 0:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 8 ) || ( info.src.charCodeAt( pos ) >= 10 && info.src.charCodeAt( pos ) <= 31 ) || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || info.src.charCodeAt( pos ) == 59 || ( info.src.charCodeAt( pos ) >= 63 && info.src.charCodeAt( pos ) <= 64 ) || ( info.src.charCodeAt( pos ) >= 66 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 9 ) state = 2;
		else if( info.src.charCodeAt( pos ) == 40 ) state = 3;
		else if( info.src.charCodeAt( pos ) == 41 ) state = 4;
		else if( info.src.charCodeAt( pos ) == 60 || info.src.charCodeAt( pos ) == 62 ) state = 5;
		else if( info.src.charCodeAt( pos ) == 33 ) state = 11;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 12;
		else if( info.src.charCodeAt( pos ) == 32 ) state = 13;
		else if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else if( info.src.charCodeAt( pos ) == 34 ) state = 15;
		else if( info.src.charCodeAt( pos ) == 65 ) state = 19;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 20;
		else state = -1;
		break;

	case 1:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 2:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 3:
		state = -1;
		match = 3;
		match_pos = pos;
		break;

	case 4:
		state = -1;
		match = 4;
		match_pos = pos;
		break;

	case 5:
		if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 6:
		state = -1;
		match = 8;
		match_pos = pos;
		break;

	case 7:
		state = -1;
		match = 9;
		match_pos = pos;
		break;

	case 8:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 6;
		match_pos = pos;
		break;

	case 9:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 5;
		match_pos = pos;
		break;

	case 10:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else state = -1;
		match = 7;
		match_pos = pos;
		break;

	case 11:
		if( info.src.charCodeAt( pos ) == 61 ) state = 14;
		else state = -1;
		break;

	case 12:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 81 ) || ( info.src.charCodeAt( pos ) >= 83 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 82 ) state = 8;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 13:
		state = -1;
		match = 1;
		match_pos = pos;
		break;

	case 14:
		state = -1;
		match = 11;
		match_pos = pos;
		break;

	case 15:
		if( info.src.charCodeAt( pos ) == 34 ) state = 7;
		else if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 33 ) || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 91 ) || ( info.src.charCodeAt( pos ) >= 93 && info.src.charCodeAt( pos ) <= 254 ) ) state = 15;
		else if( info.src.charCodeAt( pos ) == 92 ) state = 17;
		else state = -1;
		break;

	case 16:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 67 ) || ( info.src.charCodeAt( pos ) >= 69 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 68 ) state = 9;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 17:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 254 ) ) state = 15;
		else state = -1;
		break;

	case 18:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 83 ) || ( info.src.charCodeAt( pos ) >= 85 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 84 ) state = 10;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 19:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 77 ) || ( info.src.charCodeAt( pos ) >= 79 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 78 ) state = 16;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

	case 20:
		if( ( info.src.charCodeAt( pos ) >= 0 && info.src.charCodeAt( pos ) <= 31 ) || info.src.charCodeAt( pos ) == 33 || ( info.src.charCodeAt( pos ) >= 35 && info.src.charCodeAt( pos ) <= 39 ) || ( info.src.charCodeAt( pos ) >= 42 && info.src.charCodeAt( pos ) <= 57 ) || ( info.src.charCodeAt( pos ) >= 59 && info.src.charCodeAt( pos ) <= 78 ) || ( info.src.charCodeAt( pos ) >= 80 && info.src.charCodeAt( pos ) <= 254 ) ) state = 1;
		else if( info.src.charCodeAt( pos ) == 58 ) state = 6;
		else if( info.src.charCodeAt( pos ) == 79 ) state = 18;
		else state = -1;
		match = 10;
		match_pos = pos;
		break;

}


			pos++;

		}
		while( state > -1 );

	}
	while( 1 > -1 && match == 1 );

	if( match > -1 )
	{
		info.att = info.src.substr( start, match_pos - start );
		info.offset = match_pos;
		

	}
	else
	{
		info.att = new String();
		match = -1;
	}

	return match;
}


function __NODEJS_parse( src, err_off, err_la )
{
	var		sstack			= new Array();
	var		vstack			= new Array();
	var 	err_cnt			= 0;
	var		act;
	var		go;
	var		la;
	var		rval;
	var 	parseinfo		= new Function( "", "var offset; var src; var att;" );
	var		info			= new parseinfo();
	
/* Pop-Table */
var pop_tab = new Array(
	new Array( 0/* begin' */, 1 ),
	new Array( 13/* begin */, 1 ),
	new Array( 12/* search_text */, 1 ),
	new Array( 12/* search_text */, 2 ),
	new Array( 12/* search_text */, 3 ),
	new Array( 14/* and_expression */, 1 ),
	new Array( 14/* and_expression */, 3 ),
	new Array( 15/* boolean_expression */, 2 ),
	new Array( 15/* boolean_expression */, 1 ),
	new Array( 16/* expression */, 3 ),
	new Array( 16/* expression */, 2 ),
	new Array( 16/* expression */, 1 ),
	new Array( 17/* value */, 2 ),
	new Array( 17/* value */, 1 ),
	new Array( 18/* string */, 1 ),
	new Array( 18/* string */, 1 )
);

/* Action-Table */
var act_tab = new Array(
	/* State 0 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 1 */ new Array( 19/* "$" */,0 ),
	/* State 2 */ new Array( 19/* "$" */,-1 ),
	/* State 3 */ new Array( 6/* "OR" */,14 , 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 , 19/* "$" */,-2 , 4/* "RIGHT_PARENTHESE" */,-2 ),
	/* State 4 */ new Array( 5/* "AND" */,16 , 19/* "$" */,-5 , 7/* "NOT" */,-5 , 3/* "LEFT_PARENTHESE" */,-5 , 8/* "COLUMN" */,-5 , 11/* "OPERATOR" */,-5 , 10/* "WORD" */,-5 , 9/* "STRING" */,-5 , 6/* "OR" */,-5 , 4/* "RIGHT_PARENTHESE" */,-5 ),
	/* State 5 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 6 */ new Array( 19/* "$" */,-8 , 7/* "NOT" */,-8 , 3/* "LEFT_PARENTHESE" */,-8 , 8/* "COLUMN" */,-8 , 11/* "OPERATOR" */,-8 , 10/* "WORD" */,-8 , 9/* "STRING" */,-8 , 6/* "OR" */,-8 , 5/* "AND" */,-8 , 4/* "RIGHT_PARENTHESE" */,-8 ),
	/* State 7 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 8 */ new Array( 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 9 */ new Array( 19/* "$" */,-11 , 7/* "NOT" */,-11 , 3/* "LEFT_PARENTHESE" */,-11 , 8/* "COLUMN" */,-11 , 11/* "OPERATOR" */,-11 , 10/* "WORD" */,-11 , 9/* "STRING" */,-11 , 6/* "OR" */,-11 , 5/* "AND" */,-11 , 4/* "RIGHT_PARENTHESE" */,-11 ),
	/* State 10 */ new Array( 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 11 */ new Array( 19/* "$" */,-13 , 7/* "NOT" */,-13 , 3/* "LEFT_PARENTHESE" */,-13 , 8/* "COLUMN" */,-13 , 11/* "OPERATOR" */,-13 , 10/* "WORD" */,-13 , 9/* "STRING" */,-13 , 6/* "OR" */,-13 , 5/* "AND" */,-13 , 4/* "RIGHT_PARENTHESE" */,-13 ),
	/* State 12 */ new Array( 19/* "$" */,-14 , 7/* "NOT" */,-14 , 3/* "LEFT_PARENTHESE" */,-14 , 8/* "COLUMN" */,-14 , 11/* "OPERATOR" */,-14 , 10/* "WORD" */,-14 , 9/* "STRING" */,-14 , 6/* "OR" */,-14 , 5/* "AND" */,-14 , 4/* "RIGHT_PARENTHESE" */,-14 ),
	/* State 13 */ new Array( 19/* "$" */,-15 , 7/* "NOT" */,-15 , 3/* "LEFT_PARENTHESE" */,-15 , 8/* "COLUMN" */,-15 , 11/* "OPERATOR" */,-15 , 10/* "WORD" */,-15 , 9/* "STRING" */,-15 , 6/* "OR" */,-15 , 5/* "AND" */,-15 , 4/* "RIGHT_PARENTHESE" */,-15 ),
	/* State 14 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 15 */ new Array( 19/* "$" */,-3 , 4/* "RIGHT_PARENTHESE" */,-3 ),
	/* State 16 */ new Array( 7/* "NOT" */,5 , 3/* "LEFT_PARENTHESE" */,7 , 8/* "COLUMN" */,8 , 11/* "OPERATOR" */,10 , 10/* "WORD" */,12 , 9/* "STRING" */,13 ),
	/* State 17 */ new Array( 19/* "$" */,-7 , 7/* "NOT" */,-7 , 3/* "LEFT_PARENTHESE" */,-7 , 8/* "COLUMN" */,-7 , 11/* "OPERATOR" */,-7 , 10/* "WORD" */,-7 , 9/* "STRING" */,-7 , 6/* "OR" */,-7 , 5/* "AND" */,-7 , 4/* "RIGHT_PARENTHESE" */,-7 ),
	/* State 18 */ new Array( 4/* "RIGHT_PARENTHESE" */,23 ),
	/* State 19 */ new Array( 19/* "$" */,-10 , 7/* "NOT" */,-10 , 3/* "LEFT_PARENTHESE" */,-10 , 8/* "COLUMN" */,-10 , 11/* "OPERATOR" */,-10 , 10/* "WORD" */,-10 , 9/* "STRING" */,-10 , 6/* "OR" */,-10 , 5/* "AND" */,-10 , 4/* "RIGHT_PARENTHESE" */,-10 ),
	/* State 20 */ new Array( 19/* "$" */,-12 , 7/* "NOT" */,-12 , 3/* "LEFT_PARENTHESE" */,-12 , 8/* "COLUMN" */,-12 , 11/* "OPERATOR" */,-12 , 10/* "WORD" */,-12 , 9/* "STRING" */,-12 , 6/* "OR" */,-12 , 5/* "AND" */,-12 , 4/* "RIGHT_PARENTHESE" */,-12 ),
	/* State 21 */ new Array( 19/* "$" */,-4 , 4/* "RIGHT_PARENTHESE" */,-4 ),
	/* State 22 */ new Array( 19/* "$" */,-6 , 7/* "NOT" */,-6 , 3/* "LEFT_PARENTHESE" */,-6 , 8/* "COLUMN" */,-6 , 11/* "OPERATOR" */,-6 , 10/* "WORD" */,-6 , 9/* "STRING" */,-6 , 6/* "OR" */,-6 , 4/* "RIGHT_PARENTHESE" */,-6 ),
	/* State 23 */ new Array( 19/* "$" */,-9 , 7/* "NOT" */,-9 , 3/* "LEFT_PARENTHESE" */,-9 , 8/* "COLUMN" */,-9 , 11/* "OPERATOR" */,-9 , 10/* "WORD" */,-9 , 9/* "STRING" */,-9 , 6/* "OR" */,-9 , 5/* "AND" */,-9 , 4/* "RIGHT_PARENTHESE" */,-9 )
);

/* Goto-Table */
var goto_tab = new Array(
	/* State 0 */ new Array( 13/* begin */,1 , 12/* search_text */,2 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 1 */ new Array(  ),
	/* State 2 */ new Array(  ),
	/* State 3 */ new Array( 12/* search_text */,15 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 4 */ new Array(  ),
	/* State 5 */ new Array( 16/* expression */,17 , 17/* value */,9 , 18/* string */,11 ),
	/* State 6 */ new Array(  ),
	/* State 7 */ new Array( 12/* search_text */,18 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 8 */ new Array( 16/* expression */,19 , 17/* value */,9 , 18/* string */,11 ),
	/* State 9 */ new Array(  ),
	/* State 10 */ new Array( 18/* string */,20 ),
	/* State 11 */ new Array(  ),
	/* State 12 */ new Array(  ),
	/* State 13 */ new Array(  ),
	/* State 14 */ new Array( 12/* search_text */,21 , 14/* and_expression */,3 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 15 */ new Array(  ),
	/* State 16 */ new Array( 14/* and_expression */,22 , 15/* boolean_expression */,4 , 16/* expression */,6 , 17/* value */,9 , 18/* string */,11 ),
	/* State 17 */ new Array(  ),
	/* State 18 */ new Array(  ),
	/* State 19 */ new Array(  ),
	/* State 20 */ new Array(  ),
	/* State 21 */ new Array(  ),
	/* State 22 */ new Array(  ),
	/* State 23 */ new Array(  )
);



/* Symbol labels */
var labels = new Array(
	"begin'" /* Non-terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"WHITESPACE" /* Terminal symbol */,
	"LEFT_PARENTHESE" /* Terminal symbol */,
	"RIGHT_PARENTHESE" /* Terminal symbol */,
	"AND" /* Terminal symbol */,
	"OR" /* Terminal symbol */,
	"NOT" /* Terminal symbol */,
	"COLUMN" /* Terminal symbol */,
	"STRING" /* Terminal symbol */,
	"WORD" /* Terminal symbol */,
	"OPERATOR" /* Terminal symbol */,
	"search_text" /* Non-terminal symbol */,
	"begin" /* Non-terminal symbol */,
	"and_expression" /* Non-terminal symbol */,
	"boolean_expression" /* Non-terminal symbol */,
	"expression" /* Non-terminal symbol */,
	"value" /* Non-terminal symbol */,
	"string" /* Non-terminal symbol */,
	"$" /* Terminal symbol */
);


	
	info.offset = 0;
	info.src = src;
	info.att = new String();
	
	if( !err_off )
		err_off	= new Array();
	if( !err_la )
	err_la = new Array();
	
	sstack.push( 0 );
	vstack.push( 0 );
	
	la = __NODEJS_lex( info );

	while( true )
	{
		act = 25;
		for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
		{
			if( act_tab[sstack[sstack.length-1]][i] == la )
			{
				act = act_tab[sstack[sstack.length-1]][i+1];
				break;
			}
		}

		if( NODEJS__dbg_withtrace && sstack.length > 0 )
		{
			__NODEJS_dbg_print( "\nState " + sstack[sstack.length-1] + "\n" +
							"\tLookahead: " + labels[la] + " (\"" + info.att + "\")\n" +
							"\tAction: " + act + "\n" + 
							"\tSource: \"" + info.src.substr( info.offset, 30 ) + ( ( info.offset + 30 < info.src.length ) ?
									"..." : "" ) + "\"\n" +
							"\tStack: " + sstack.join() + "\n" +
							"\tValue stack: " + vstack.join() + "\n" );
		}
		
			
		//Panic-mode: Try recovery when parse-error occurs!
		if( act == 25 )
		{
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Error detected: There is no reduce or shift on the symbol " + labels[la] );
			
			err_cnt++;
			err_off.push( info.offset - info.att.length );			
			err_la.push( new Array() );
			for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
				err_la[err_la.length-1].push( labels[act_tab[sstack[sstack.length-1]][i]] );
			
			//Remember the original stack!
			var rsstack = new Array();
			var rvstack = new Array();
			for( var i = 0; i < sstack.length; i++ )
			{
				rsstack[i] = sstack[i];
				rvstack[i] = vstack[i];
			}
			
			while( act == 25 && la != 19 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery\n" +
									"Current lookahead: " + labels[la] + " (" + info.att + ")\n" +
									"Action: " + act + "\n\n" );
				if( la == -1 )
					info.offset++;
					
				while( act == 25 && sstack.length > 0 )
				{
					sstack.pop();
					vstack.pop();
					
					if( sstack.length == 0 )
						break;
						
					act = 25;
					for( var i = 0; i < act_tab[sstack[sstack.length-1]].length; i+=2 )
					{
						if( act_tab[sstack[sstack.length-1]][i] == la )
						{
							act = act_tab[sstack[sstack.length-1]][i+1];
							break;
						}
					}
				}
				
				if( act != 25 )
					break;
				
				for( var i = 0; i < rsstack.length; i++ )
				{
					sstack.push( rsstack[i] );
					vstack.push( rvstack[i] );
				}
				
				la = __NODEJS_lex( info );
			}
			
			if( act == 25 )
			{
				if( NODEJS__dbg_withtrace )
					__NODEJS_dbg_print( "\tError recovery failed, terminating parse process..." );
				break;
			}


			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tError recovery succeeded, continuing" );
		}
		
		/*
		if( act == 25 )
			break;
		*/
		
		
		//Shift
		if( act > 0 )
		{			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Shifting symbol: " + labels[la] + " (" + info.att + ")" );
		
			sstack.push( act );
			vstack.push( info.att );
			
			la = __NODEJS_lex( info );
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tNew lookahead symbol: " + labels[la] + " (" + info.att + ")" );
		}
		//Reduce
		else
		{		
			act *= -1;
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "Reducing by producution: " + act );
			
			rval = void(0);
			
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPerforming semantic action..." );
			
switch( act )
{
	case 0:
	{
		rval = vstack[ vstack.length - 1 ];
	}
	break;
	case 1:
	{
		 result = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 2:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 3:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 2 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 4:
	{
		 rval = mkComplexQuery('OR',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 5:
	{
		 rval = vstack[ vstack.length - 1 ] ; 
	}
	break;
	case 6:
	{
		 rval = mkComplexQuery('AND',[vstack[ vstack.length - 3 ],vstack[ vstack.length - 1 ]]); 
	}
	break;
	case 7:
	{
		 rval = mkNotQuery(vstack[ vstack.length - 1 ]); 
	}
	break;
	case 8:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 9:
	{
		 rval = vstack[ vstack.length - 2 ]; 
	}
	break;
	case 10:
	{
		 simpleQuerySetKey(vstack[ vstack.length - 1 ],vstack[ vstack.length - 2 ].split(':').slice(0,-1).join(':')); rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 11:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 12:
	{
		 vstack[ vstack.length - 1 ].operator = vstack[ vstack.length - 2 ] ; rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 13:
	{
		 rval = vstack[ vstack.length - 1 ]; 
	}
	break;
	case 14:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ]); 
	}
	break;
	case 15:
	{
		 rval = mkSimpleQuery('',vstack[ vstack.length - 1 ].split('"').slice(1,-1).join('"')); 
	}
	break;
}



			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPopping " + pop_tab[act][1] + " off the stack..." );
				
			for( var i = 0; i < pop_tab[act][1]; i++ )
			{
				sstack.pop();
				vstack.pop();
			}
									
			go = -1;
			for( var i = 0; i < goto_tab[sstack[sstack.length-1]].length; i+=2 )
			{
				if( goto_tab[sstack[sstack.length-1]][i] == pop_tab[act][0] )
				{
					go = goto_tab[sstack[sstack.length-1]][i+1];
					break;
				}
			}
			
			if( act == 0 )
				break;
				
			if( NODEJS__dbg_withtrace )
				__NODEJS_dbg_print( "\tPushing non-terminal " + labels[ pop_tab[act][0] ] );
				
			sstack.push( go );
			vstack.push( rval );			
		}
		
		if( NODEJS__dbg_withtrace )
		{		
			alert( NODEJS__dbg_string );
			NODEJS__dbg_string = new String();
		}
	}

	if( NODEJS__dbg_withtrace )
	{
		__NODEJS_dbg_print( "\nParse complete." );
		alert( NODEJS__dbg_string );
	}
	
	return err_cnt;
}



var arrayExtend = function () {
  var j, i, newlist = [], list_list = arguments;
  for (j = 0; j < list_list.length; j += 1) {
    for (i = 0; i < list_list[j].length; i += 1) {
      newlist.push(list_list[j][i]);
    }
  }
  return newlist;

}, mkSimpleQuery = function (key, value, operator) {
  var object = {"type": "simple", "key": key, "value": value};
  if (operator !== undefined) {
    object.operator = operator;
  }
  return object;

}, mkNotQuery = function (query) {
  if (query.operator === "NOT") {
    return query.query_list[0];
  }
  return {"type": "complex", "operator": "NOT", "query_list": [query]};

}, mkComplexQuery = function (operator, query_list) {
  var i, query_list2 = [];
  for (i = 0; i < query_list.length; i += 1) {
    if (query_list[i].operator === operator) {
      query_list2 = arrayExtend(query_list2, query_list[i].query_list);
    } else {
      query_list2.push(query_list[i]);
    }
  }
  return {type:"complex",operator:operator,query_list:query_list2};

}, simpleQuerySetKey = function (query, key) {
  var i;
  if (query.type === "complex") {
    for (i = 0; i < query.query_list.length; ++i) {
      simpleQuerySetKey (query.query_list[i],key);
    }
    return true;
  }
  if (query.type === "simple" && !query.key) {
    query.key = key;
    return true;
  }
  return false;
},
  error_offsets = [],
  error_lookaheads = [],
  error_count = 0,
  result;

if ((error_count = __NODEJS_parse(string, error_offsets, error_lookaheads)) > 0) {
  var i;
  for (i = 0; i < error_count; i += 1) {
    throw new Error("Parse error near \"" +
                    string.substr(error_offsets[i]) +
                    "\", expecting \"" +
                    error_lookaheads[i].join() + "\"");
  }
}


  return result;
} // parseStringToObject

_export('parseStringToObject', parseStringToObject);

/*jslint indent: 2, maxlen: 80, sloppy: true */

var query_class_dict = {};

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query: true, query_class_dict: true, inherits: true,
         _export, QueryFactory, RSVP, sequence */

/**
 * The ComplexQuery inherits from Query, and compares one or several metadata
 * values.
 *
 * @class ComplexQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="AND"] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function ComplexQuery(spec, key_schema) {
  Query.call(this);

  /**
   * Logical operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @default "AND"
   * @optional
   */
  this.operator = spec.operator || "AND";

  /**
   * The sub Query list which are used to query an item.
   *
   * @attribute query_list
   * @type Array
   * @default []
   * @optional
   */
  this.query_list = spec.query_list || [];
  /*jslint unparam: true*/
  this.query_list = this.query_list.map(
    // decorate the map to avoid sending the index as key_schema argument
    function (o, i) { return QueryFactory.create(o, key_schema); }
  );
  /*jslint unparam: false*/

}
inherits(ComplexQuery, Query);

/**
 * #crossLink "Query/match:method"
 */
ComplexQuery.prototype.match = function (item) {
  var operator = this.operator;
  if (!(/^(?:AND|OR|NOT)$/i.test(operator))) {
    operator = "AND";
  }
  return this[operator.toUpperCase()](item);
};

/**
 * #crossLink "Query/toString:method"
 */
ComplexQuery.prototype.toString = function () {
  var str_list = ["("], this_operator = this.operator;
  this.query_list.forEach(function (query) {
    str_list.push(query.toString());
    str_list.push(this_operator);
  });
  str_list[str_list.length - 1] = ")"; // replace last operator
  return str_list.join(" ");
};

/**
 * #crossLink "Query/serialized:method"
 */
ComplexQuery.prototype.serialized = function () {
  var s = {
    "type": "complex",
    "operator": this.operator,
    "query_list": []
  };
  this.query_list.forEach(function (query) {
    s.query_list.push(query.serialized());
  });
  return s;
};
ComplexQuery.prototype.toJSON = ComplexQuery.prototype.serialized;

/**
 * Comparison operator, test if all sub queries match the
 * item value
 *
 * @method AND
 * @param  {Object} item The item to match
 * @return {Boolean} true if all match, false otherwise
 */
ComplexQuery.prototype.AND = function (item) {
  var j, promises = [];
  for (j = 0; j < this.query_list.length; j += 1) {
    promises.push(this.query_list[j].match(item));
  }

  function cancel() {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      if (typeof promises.cancel === 'function') {
        promises.cancel();
      }
    }
  }

  return new RSVP.Promise(function (resolve, reject) {
    var i, count = 0;
    function resolver(value) {
      if (!value) {
        resolve(false);
      }
      count += 1;
      if (count === promises.length) {
        resolve(true);
      }
    }

    function rejecter(err) {
      reject(err);
      cancel();
    }

    for (i = 0; i < promises.length; i += 1) {
      promises[i].then(resolver, rejecter);
    }
  }, cancel);
};

/**
 * Comparison operator, test if one of the sub queries matches the
 * item value
 *
 * @method OR
 * @param  {Object} item The item to match
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.OR =  function (item) {
  var j, promises = [];
  for (j = 0; j < this.query_list.length; j += 1) {
    promises.push(this.query_list[j].match(item));
  }

  function cancel() {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      if (typeof promises.cancel === 'function') {
        promises.cancel();
      }
    }
  }

  return new RSVP.Promise(function (resolve, reject) {
    var i, count = 0;
    function resolver(value) {
      if (value) {
        resolve(true);
      }
      count += 1;
      if (count === promises.length) {
        resolve(false);
      }
    }

    function rejecter(err) {
      reject(err);
      cancel();
    }

    for (i = 0; i < promises.length; i += 1) {
      promises[i].then(resolver, rejecter);
    }
  }, cancel);
};

/**
 * Comparison operator, test if the sub query does not match the
 * item value
 *
 * @method NOT
 * @param  {Object} item The item to match
 * @return {Boolean} true if one match, false otherwise
 */
ComplexQuery.prototype.NOT = function (item) {
  return sequence([function () {
    return this.query_list[0].match(item);
  }, function (answer) {
    return !answer;
  }]);
};

query_class_dict.complex = ComplexQuery;

_export("ComplexQuery", ComplexQuery);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global parseStringToObject: true, emptyFunction: true, sortOn: true, limit:
  true, select: true, _export: true, stringEscapeRegexpCharacters: true,
  deepClone, RSVP, sequence */

/**
 * The query to use to filter a list of objects.
 * This is an abstract class.
 *
 * @class Query
 * @constructor
 */
function Query() {

  /**
   * Called before parsing the query. Must be overridden!
   *
   * @method onParseStart
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseStart = emptyFunction;

  /**
   * Called when parsing a simple query. Must be overridden!
   *
   * @method onParseSimpleQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseSimpleQuery = emptyFunction;

  /**
   * Called when parsing a complex query. Must be overridden!
   *
   * @method onParseComplexQuery
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseComplexQuery = emptyFunction;

  /**
   * Called after parsing the query. Must be overridden!
   *
   * @method onParseEnd
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} option Some option gave in parse()
   */
  this.onParseEnd = emptyFunction;

}

/**
 * Filter the item list with matching item only
 *
 * @method exec
 * @param  {Array} item_list The list of object
 * @param  {Object} [option] Some operation option
 * @param  {Array} [option.select_list] A object keys to retrieve
 * @param  {Array} [option.sort_on] Couples of object keys and "ascending"
 *                 or "descending"
 * @param  {Array} [option.limit] Couple of integer, first is an index and
 *                 second is the length.
 */
Query.prototype.exec = function (item_list, option) {
  var i, promises = [];
  if (!Array.isArray(item_list)) {
    throw new TypeError("Query().exec(): Argument 1 is not of type 'array'");
  }
  if (option === undefined) {
    option = {};
  }
  if (typeof option !== 'object') {
    throw new TypeError("Query().exec(): " +
                        "Optional argument 2 is not of type 'object'");
  }
  for (i = 0; i < item_list.length; i += 1) {
    if (!item_list[i]) {
      promises.push(RSVP.resolve(false));
    } else {
      promises.push(this.match(item_list[i]));
    }
  }
  return sequence([function () {
    return RSVP.all(promises);
  }, function (answers) {
    var j;
    for (j = answers.length - 1; j >= 0; j -= 1) {
      if (!answers[j]) {
        item_list.splice(j, 1);
      }
    }
    if (option.sort_on) {
      return sortOn(option.sort_on, item_list);
    }
  }, function () {
    if (option.limit) {
      return limit(option.limit, item_list);
    }
  }, function () {
    return select(option.select_list || [], item_list);
  }, function () {
    return item_list;
  }]);
};

/**
 * Test if an item matches this query
 *
 * @method match
 * @param  {Object} item The object to test
 * @return {Boolean} true if match, false otherwise
 */
Query.prototype.match = function () {
  return RSVP.resolve(true);
};


/**
 * Browse the Query in deep calling parser method in each step.
 *
 * `onParseStart` is called first, on end `onParseEnd` is called.
 * It starts from the simple queries at the bottom of the tree calling the
 * parser method `onParseSimpleQuery`, and go up calling the
 * `onParseComplexQuery` method.
 *
 * @method parse
 * @param  {Object} option Any options you want (except 'parsed')
 * @return {Any} The parse result
 */
Query.prototype.parse = function (option) {
  var that = this, object;
  /**
   * The recursive parser.
   *
   * @param  {Object} object The object shared in the parse process
   * @param  {Object} options Some options usable in the parseMethods
   * @return {Any} The parser result
   */
  function recParse(object, option) {
    var query = object.parsed;
    if (query.type === "complex") {
      return sequence([function () {
        return sequence(query.query_list.map(function (v, i) {
          /*jslint unparam: true */
          return function () {
            sequence([function () {
              object.parsed = query.query_list[i];
              return recParse(object, option);
            }, function () {
              query.query_list[i] = object.parsed;
            }]);
          };
        }));
      }, function () {
        object.parsed = query;
        return that.onParseComplexQuery(object, option);
      }]);
    }
    if (query.type === "simple") {
      return that.onParseSimpleQuery(object, option);
    }
  }
  object = {"parsed": JSON.parse(JSON.stringify(that.serialized()))};
  return sequence([function () {
    return that.onParseStart(object, option);
  }, function () {
    return recParse(object, option);
  }, function () {
    return that.onParseEnd(object, option);
  }, function () {
    return object.parsed;
  }]);
};

/**
 * Convert this query to a parsable string.
 *
 * @method toString
 * @return {String} The string version of this query
 */
Query.prototype.toString = function () {
  return "";
};

/**
 * Convert this query to an jsonable object in order to be remake thanks to
 * QueryFactory class.
 *
 * @method serialized
 * @return {Object} The jsonable object
 */
Query.prototype.serialized = function () {
  return undefined;
};

_export("Query", Query);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export, ComplexQuery, SimpleQuery, Query, parseStringToObject,
  query_class_dict */

/**
 * Provides static methods to create Query object
 *
 * @class QueryFactory
 */
function QueryFactory() {
  return;
}

/**
 * Creates Query object from a search text string or a serialized version
 * of a Query.
 *
 * @method create
 * @static
 * @param  {Object,String} object The search text or the serialized version
 *         of a Query
 * @return {Query} A Query object
 */
QueryFactory.create = function (object, key_schema) {
  if (object === "") {
    return new Query();
  }
  if (typeof object === "string") {
    object = parseStringToObject(object);
  }
  if (typeof (object || {}).type === "string" &&
      query_class_dict[object.type]) {
    return new query_class_dict[object.type](object, key_schema);
  }
  throw new TypeError("QueryFactory.create(): " +
                      "Argument 1 is not a search text or a parsable object");
};

_export("QueryFactory", QueryFactory);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export: true */

function objectToSearchText(query) {
  var str_list = [];
  if (query.type === "complex") {
    str_list.push("(");
    (query.query_list || []).forEach(function (sub_query) {
      str_list.push(objectToSearchText(sub_query));
      str_list.push(query.operator);
    });
    str_list.length -= 1;
    str_list.push(")");
    return str_list.join(" ");
  }
  if (query.type === "simple") {
    return (query.key ? query.key + ": " : "") +
      (query.operator || "") + ' "' + query.value + '"';
  }
  throw new TypeError("This object is not a query");
}
_export("objectToSearchText", objectToSearchText);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global Query: true, inherits: true, query_class_dict: true, _export: true,
  searchTextToRegExp, RSVP */

var checkKeySchema = function (key_schema) {
  var prop;

  if (key_schema !== undefined) {
    if (typeof key_schema !== 'object') {
      throw new TypeError("SimpleQuery().create(): " +
                          "key_schema is not of type 'object'");
    }
    // key_set is mandatory
    if (key_schema.key_set === undefined) {
      throw new TypeError("SimpleQuery().create(): " +
                          "key_schema has no 'key_set' property");
    }
    for (prop in key_schema) {
      if (key_schema.hasOwnProperty(prop)) {
        switch (prop) {
        case 'key_set':
        case 'cast_lookup':
        case 'match_lookup':
          break;
        default:
          throw new TypeError("SimpleQuery().create(): " +
                             "key_schema has unknown property '" + prop + "'");
        }
      }
    }
  }
};


/**
 * The SimpleQuery inherits from Query, and compares one metadata value
 *
 * @class SimpleQuery
 * @extends Query
 * @param  {Object} [spec={}] The specifications
 * @param  {String} [spec.operator="="] The compare method to use
 * @param  {String} spec.key The metadata key
 * @param  {String} spec.value The value of the metadata to compare
 */
function SimpleQuery(spec, key_schema) {
  Query.call(this);

  checkKeySchema(key_schema);

  this._key_schema = key_schema || {};

  /**
   * Operator to use to compare object values
   *
   * @attribute operator
   * @type String
   * @optional
   */
  this.operator = spec.operator;

  /**
   * Key of the object which refers to the value to compare
   *
   * @attribute key
   * @type String
   */
  this.key = spec.key;

  /**
   * Value is used to do the comparison with the object value
   *
   * @attribute value
   * @type String
   */
  this.value = spec.value;

}
inherits(SimpleQuery, Query);


var checkKey = function (key) {
  var prop;

  if (key.read_from === undefined) {
    throw new TypeError("Custom key is missing the read_from property");
  }

  for (prop in key) {
    if (key.hasOwnProperty(prop)) {
      switch (prop) {
      case 'read_from':
      case 'cast_to':
      case 'equal_match':
        break;
      default:
        throw new TypeError("Custom key has unknown property '" +
                            prop + "'");
      }
    }
  }
};


/**
 * #crossLink "Query/match:method"
 */
SimpleQuery.prototype.match = function (item) {
  var object_value = null,
    equal_match = null,
    cast_to = null,
    matchMethod = null,
    operator = this.operator,
    value = null,
    key = this.key;

  /*jslint regexp: true */
  if (!(/^(?:!?=|<=?|>=?)$/i.test(operator))) {
    // `operator` is not correct, we have to change it to "like" or "="
    if (/%/.test(this.value)) {
      // `value` contains a non escaped `%`
      operator = "like";
    } else {
      // `value` does not contain non escaped `%`
      operator = "=";
    }
  }

  matchMethod = this[operator];

  if (this._key_schema.key_set && this._key_schema.key_set[key] !== undefined) {
    key = this._key_schema.key_set[key];
  }

  if (typeof key === 'object') {
    checkKey(key);
    object_value = item[key.read_from];

    equal_match = key.equal_match;

    // equal_match can be a string
    if (typeof equal_match === 'string') {
      // XXX raise error if equal_match not in match_lookup
      equal_match = this._key_schema.match_lookup[equal_match];
    }

    // equal_match overrides the default '=' operator
    if (equal_match !== undefined) {
      matchMethod = (operator === "=" || operator === "like" ?
                     equal_match : matchMethod);
    }

    value = this.value;
    cast_to = key.cast_to;
    if (cast_to) {
      // cast_to can be a string
      if (typeof cast_to === 'string') {
        // XXX raise error if cast_to not in cast_lookup
        cast_to = this._key_schema.cast_lookup[cast_to];
      }

      value = cast_to(value);
      object_value = cast_to(object_value);
    }
  } else {
    object_value = item[key];
    value = this.value;
  }
  if (object_value === undefined || value === undefined) {
    return RSVP.resolve(false);
  }
  return matchMethod(object_value, value);
};

/**
 * #crossLink "Query/toString:method"
 */
SimpleQuery.prototype.toString = function () {
  return (this.key ? this.key + ":" : "") +
    (this.operator ? " " + this.operator : "") + ' "' + this.value + '"';
};

/**
 * #crossLink "Query/serialized:method"
 */
SimpleQuery.prototype.serialized = function () {
  var object = {
    "type": "simple",
    "key": this.key,
    "value": this.value
  };
  if (this.operator !== undefined) {
    object.operator = this.operator;
  }
  return object;
};
SimpleQuery.prototype.toJSON = SimpleQuery.prototype.serialized;

/**
 * Comparison operator, test if this query value matches the item value
 *
 * @method =
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if match, false otherwise
 */
SimpleQuery.prototype["="] = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) === 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString(), false).
        test(value.toString())
    ) {
      return RSVP.resolve(true);
    }
  }
  return RSVP.resolve(false);
};

/**
 * Comparison operator, test if this query value matches the item value
 *
 * @method like
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if match, false otherwise
 */
SimpleQuery.prototype.like = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) === 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString()).test(value.toString())
    ) {
      return RSVP.resolve(true);
    }
  }
  return RSVP.resolve(false);
};

/**
 * Comparison operator, test if this query value does not match the item value
 *
 * @method !=
 * @param  {String} object_value The value to compare
 * @param  {String} comparison_value The comparison value
 * @return {Boolean} true if not match, false otherwise
 */
SimpleQuery.prototype["!="] = function (object_value, comparison_value) {
  var value, i;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  for (i = 0; i < object_value.length; i += 1) {
    value = object_value[i];
    if (typeof value === 'object' && value.hasOwnProperty('content')) {
      value = value.content;
    }
    if (typeof value.cmp === "function") {
      return RSVP.resolve(value.cmp(comparison_value) !== 0);
    }
    if (
      searchTextToRegExp(comparison_value.toString(), false).
        test(value.toString())
    ) {
      return RSVP.resolve(false);
    }
  }
  return RSVP.resolve(true);
};

/**
 * Comparison operator, test if this query value is lower than the item value
 *
 * @method <
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if lower, false otherwise
 */
SimpleQuery.prototype["<"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) < 0);
  }
  return RSVP.resolve(value < comparison_value);
};

/**
 * Comparison operator, test if this query value is equal or lower than the
 * item value
 *
 * @method <=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or lower, false otherwise
 */
SimpleQuery.prototype["<="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) <= 0);
  }
  return RSVP.resolve(value <= comparison_value);
};

/**
 * Comparison operator, test if this query value is greater than the item
 * value
 *
 * @method >
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if greater, false otherwise
 */
SimpleQuery.prototype[">"] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) > 0);
  }
  return RSVP.resolve(value > comparison_value);
};

/**
 * Comparison operator, test if this query value is equal or greater than the
 * item value
 *
 * @method >=
 * @param  {Number, String} object_value The value to compare
 * @param  {Number, String} comparison_value The comparison value
 * @return {Boolean} true if equal or greater, false otherwise
 */
SimpleQuery.prototype[">="] = function (object_value, comparison_value) {
  var value;
  if (!Array.isArray(object_value)) {
    object_value = [object_value];
  }
  value = object_value[0];
  if (typeof value === 'object' && value.hasOwnProperty('content')) {
    value = value.content;
  }
  if (typeof value.cmp === "function") {
    return RSVP.resolve(value.cmp(comparison_value) >= 0);
  }
  return RSVP.resolve(value >= comparison_value);
};

query_class_dict.simple = SimpleQuery;

_export("SimpleQuery", SimpleQuery);

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global _export, RSVP */

/**
 * Escapes regexp special chars from a string.
 *
 * @param  {String} string The string to escape
 * @return {String} The escaped string
 */
function stringEscapeRegexpCharacters(string) {
  if (typeof string === "string") {
    return string.replace(/([\\\.\$\[\]\(\)\{\}\^\?\*\+\-])/g, "\\$1");
  }
  throw new TypeError("complex_queries.stringEscapeRegexpCharacters(): " +
                      "Argument no 1 is not of type 'string'");
}

_export("stringEscapeRegexpCharacters", stringEscapeRegexpCharacters);

/**
 * Convert metadata values to array of strings. ex:
 *
 *     "a" -> ["a"],
 *     {"content": "a"} -> ["a"]
 *
 * @param  {Any} value The metadata value
 * @return {Array} The value in string array format
 */
function metadataValueToStringArray(value) {
  var i, new_value = [];
  if (value === undefined) {
    return undefined;
  }
  if (!Array.isArray(value)) {
    value = [value];
  }
  for (i = 0; i < value.length; i += 1) {
    if (typeof value[i] === 'object') {
      new_value[i] = value[i].content;
    } else {
      new_value[i] = value[i];
    }
  }
  return new_value;
}

/**
 * A sort function to sort items by key
 *
 * @param  {String} key The key to sort on
 * @param  {String} [way="ascending"] 'ascending' or 'descending'
 * @return {Function} The sort function
 */
function sortFunction(key, way) {
  if (way === 'descending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return 1;
        }
        if (b[i] === undefined) {
          return -1;
        }
        if (a[i] > b[i]) {
          return -1;
        }
        if (a[i] < b[i]) {
          return 1;
        }
      }
      return 0;
    };
  }
  if (way === 'ascending') {
    return function (a, b) {
      // this comparison is 5 times faster than json comparison
      var i, l;
      a = metadataValueToStringArray(a[key]) || [];
      b = metadataValueToStringArray(b[key]) || [];
      l = a.length > b.length ? a.length : b.length;
      for (i = 0; i < l; i += 1) {
        if (a[i] === undefined) {
          return -1;
        }
        if (b[i] === undefined) {
          return 1;
        }
        if (a[i] > b[i]) {
          return 1;
        }
        if (a[i] < b[i]) {
          return -1;
        }
      }
      return 0;
    };
  }
  throw new TypeError("complex_queries.sortFunction(): " +
                      "Argument 2 must be 'ascending' or 'descending'");
}

/**
 * Clones all native object in deep. Managed types: Object, Array, String,
 * Number, Boolean, null.
 *
 * @param  {A} object The object to clone
 * @return {A} The cloned object
 */
function deepClone(object) {
  var i, cloned;
  if (Array.isArray(object)) {
    cloned = [];
    for (i = 0; i < object.length; i += 1) {
      cloned[i] = deepClone(object[i]);
    }
    return cloned;
  }
  if (typeof object === "object") {
    cloned = {};
    for (i in object) {
      if (object.hasOwnProperty(i)) {
        cloned[i] = deepClone(object[i]);
      }
    }
    return cloned;
  }
  return object;
}

/**
 * Inherits the prototype methods from one constructor into another. The
 * prototype of `constructor` will be set to a new object created from
 * `superConstructor`.
 *
 * @param  {Function} constructor The constructor which inherits the super one
 * @param  {Function} superConstructor The super constructor
 */
function inherits(constructor, superConstructor) {
  constructor.super_ = superConstructor;
  constructor.prototype = Object.create(superConstructor.prototype, {
    "constructor": {
      "configurable": true,
      "enumerable": false,
      "writable": true,
      "value": constructor
    }
  });
}

/**
 * Does nothing
 */
function emptyFunction() {
  return;
}

/**
 * Filter a list of items, modifying them to select only wanted keys. If
 * `clone` is true, then the method will act on a cloned list.
 *
 * @param  {Array} select_option Key list to keep
 * @param  {Array} list The item list to filter
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function select(select_option, list, clone) {
  var i, j, new_item;
  if (!Array.isArray(select_option)) {
    throw new TypeError("complex_queries.select(): " +
                        "Argument 1 is not of type Array");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("complex_queries.select(): " +
                        "Argument 2 is not of type Array");
  }
  if (clone === true) {
    list = deepClone(list);
  }
  for (i = 0; i < list.length; i += 1) {
    new_item = {};
    for (j = 0; j < select_option.length; j += 1) {
      if (list[i].hasOwnProperty([select_option[j]])) {
        new_item[select_option[j]] = list[i][select_option[j]];
      }
    }
    for (j in new_item) {
      if (new_item.hasOwnProperty(j)) {
        list[i] = new_item;
        break;
      }
    }
  }
  return list;
}

_export('select', select);

/**
 * Sort a list of items, according to keys and directions. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} sort_on_option List of couples [key, direction]
 * @param  {Array} list The item list to sort
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function sortOn(sort_on_option, list, clone) {
  var sort_index;
  if (!Array.isArray(sort_on_option)) {
    throw new TypeError("complex_queries.sortOn(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  for (sort_index = sort_on_option.length - 1; sort_index >= 0;
       sort_index -= 1) {
    list.sort(sortFunction(
      sort_on_option[sort_index][0],
      sort_on_option[sort_index][1]
    ));
  }
  return list;
}

_export('sortOn', sortOn);

/**
 * Limit a list of items, according to index and length. If `clone` is true,
 * then the method will act on a cloned list.
 *
 * @param  {Array} limit_option A couple [from, length]
 * @param  {Array} list The item list to limit
 * @param  {Boolean} [clone=false] If true, modifies a clone of the list
 * @return {Array} The filtered list
 */
function limit(limit_option, list, clone) {
  if (!Array.isArray(limit_option)) {
    throw new TypeError("complex_queries.limit(): " +
                        "Argument 1 is not of type 'array'");
  }
  if (!Array.isArray(list)) {
    throw new TypeError("complex_queries.limit(): " +
                        "Argument 2 is not of type 'array'");
  }
  if (clone) {
    list = deepClone(list);
  }
  list.splice(0, limit_option[0]);
  if (limit_option[1]) {
    list.splice(limit_option[1]);
  }
  return list;
}

_export('limit', limit);

/**
 * Convert a search text to a regexp.
 *
 * @param  {String} string The string to convert
 * @param  {Boolean} [use_wildcard_character=true] Use wildcard "%" and "_"
 * @return {RegExp} The search text regexp
 */
function searchTextToRegExp(string, use_wildcard_characters) {
  if (typeof string !== 'string') {
    throw new TypeError("complex_queries.searchTextToRegExp(): " +
                        "Argument 1 is not of type 'string'");
  }
  if (use_wildcard_characters === false) {
    return new RegExp("^" + stringEscapeRegexpCharacters(string) + "$");
  }
  return new RegExp("^" + stringEscapeRegexpCharacters(string).replace(
    /%/g,
    ".*"
  ).replace(
    /_/g,
    "."
  ) + "$");
}

_export("searchTextToRegExp", searchTextToRegExp);

/**
 * sequence(thens): Promise
 *
 * Executes a sequence of *then* callbacks. It acts like
 * `smth().then(callback).then(callback)...`. The first callback is called with
 * no parameter.
 *
 * Elements of `thens` array can be a function or an array contaning at most
 * three *then* callbacks: *onFulfilled*, *onRejected*, *onNotified*.
 *
 * When `cancel()` is executed, each then promises are cancelled at the same
 * time.
 *
 * @param  {Array} thens An array of *then* callbacks
 * @return {Promise} A new promise
 */
function sequence(thens) {
  var promises = [];
  return new RSVP.Promise(function (resolve, reject, notify) {
    var i;
    promises[0] = new RSVP.Promise(function (resolve) {
      resolve();
    });
    for (i = 0; i < thens.length; i += 1) {
      if (Array.isArray(thens[i])) {
        promises[i + 1] = promises[i].
          then(thens[i][0], thens[i][1], thens[i][2]);
      } else {
        promises[i + 1] = promises[i].then(thens[i]);
      }
    }
    promises[i].then(resolve, reject, notify);
  }, function () {
    var i;
    for (i = 0; i < promises.length; i += 1) {
      promises[i].cancel();
    }
  });
}


  return to_export;
}));
;/*
 * Copyright 2013, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, regexp: true */
/*global jIO, localStorage, setTimeout, window, define, Blob, Uint8Array,
  exports, require */

/**
 * JIO Local Storage. Type = 'local'.
 * Local browser "database" storage.
 *
 * Storage Description:
 *
 *     {
 *       "type": "local",
 *       "mode": <string>,
 *         // - "localStorage" // default
 *         // - "memory"
 *       "username": <non empty string>, // to define user space
 *       "application_name": <string> // default 'untitled'
 *     }
 *
 * Document are stored in path
 * 'jio/localstorage/username/application_name/document_id' like this:
 *
 *     {
 *       "_id": "document_id",
 *       "_attachments": {
 *         "attachment_name": {
 *           "length": data_length,
 *           "digest": "md5-XXX",
 *           "content_type": "mime/type"
 *         },
 *         "attachment_name2": {..}, ...
 *       },
 *       "metadata_name": "metadata_value"
 *       "metadata_name2": ...
 *       ...
 *     }
 *
 * Only "_id" and "_attachments" are specific metadata keys, other one can be
 * added without loss.
 *
 * @class LocalStorage
 */

// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports, require('jio'));
  }
  window.local_storage = {};
  module(window.local_storage, jIO);
}([
  'exports',
  'jio'
], function (exports, jIO) {
  "use strict";

  /**
   * Checks if an object has no enumerable keys
   *
   * @param  {Object} obj The object
   * @return {Boolean} true if empty, else false
   */
  function objectIsEmpty(obj) {
    var k;
    for (k in obj) {
      if (obj.hasOwnProperty(k)) {
        return false;
      }
    }
    return true;
  }

  var ram = {}, memorystorage, localstorage;

  /*
   * Wrapper for the localStorage used to simplify instion of any kind of
   * values
   */
  localstorage = {
    getItem: function (item) {
      var value = localStorage.getItem(item);
      return value === null ? null : JSON.parse(value);
    },
    setItem: function (item, value) {
      return localStorage.setItem(item, JSON.stringify(value));
    },
    removeItem: function (item) {
      return localStorage.removeItem(item);
    }
  };

  /*
   * Wrapper for the localStorage used to simplify instion of any kind of
   * values
   */
  memorystorage = {
    getItem: function (item) {
      var value = ram[item];
      return value === undefined ? null : JSON.parse(value);
    },
    setItem: function (item, value) {
      ram[item] = JSON.stringify(value);
    },
    removeItem: function (item) {
      delete ram[item];
    }
  };

  /**
   * The JIO LocalStorage extension
   *
   * @class LocalStorage
   * @constructor
   */
  function LocalStorage(spec) {
    if (typeof spec.username !== 'string' || spec.username === '') {
      throw new TypeError("LocalStorage 'username' must be a non-empty string");
    }
    this._localpath = 'jio/localstorage/' + spec.username + '/' + (
      spec.application_name === null || spec.application_name ===
        undefined ? 'untitled' : spec.application_name.toString()
    );
    switch (spec.mode) {
    case "memory":
      this._database = ram;
      this._storage = memorystorage;
      this._mode = "memory";
      break;
    default:
      this._database = localStorage;
      this._storage = localstorage;
      this._mode = "localStorage";
      this._key_schema = spec.key_schema;
      break;
    }
  }


  /**
   * Create a document in local storage.
   *
   * @method post
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to store
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.post = function (command, metadata) {
    var doc, doc_id = metadata._id;
    if (!doc_id) {
      doc_id = jIO.util.generateUuid();
    }
    doc = this._storage.getItem(this._localpath + "/" + doc_id);
    if (doc === null) {
      // the document does not exist
      doc = jIO.util.deepClone(metadata);
      doc._id = doc_id;
      delete doc._attachments;
      this._storage.setItem(this._localpath + "/" + doc_id, doc);
      command.success({"id": doc_id});
    } else {
      // the document already exists
      command.error(
        "conflict",
        "document exists",
        "Cannot create a new document"
      );
    }
  };

  /**
   * Create or update a document in local storage.
   *
   * @method put
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to store
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.put = function (command, metadata) {
    var doc, tmp, status;
    doc = this._storage.getItem(this._localpath + "/" + metadata._id);
    if (doc === null) {
      //  the document does not exist
      doc = jIO.util.deepClone(metadata);
      delete doc._attachments;
      status = "created";
    } else {
      // the document already exists
      tmp = jIO.util.deepClone(metadata);
      tmp._attachments = doc._attachments;
      doc = tmp;
      status = "no_content";
    }
    // write
    this._storage.setItem(this._localpath + "/" + metadata._id, doc);
    command.success(status);
  };

  /**
   * Add an attachment to a document
   *
   * @method putAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.putAttachment = function (command, param) {
    var that = this, doc, status = "created";
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (doc === null) {
      //  the document does not exist
      return command.error(
        "not_found",
        "missing",
        "Impossible to add attachment"
      );
    }

    // the document already exists
    // download data
    jIO.util.readBlobAsBinaryString(param._blob).then(function (e) {
      doc._attachments = doc._attachments || {};
      if (doc._attachments[param._attachment]) {
        status = "no_content";
      }
      doc._attachments[param._attachment] = {
        "content_type": param._blob.type,
        "digest": jIO.util.makeBinaryStringDigest(e.target.result),
        "length": param._blob.size
      };

      that._storage.setItem(that._localpath + "/" + param._id + "/" +
                            param._attachment, e.target.result);
      that._storage.setItem(that._localpath + "/" + param._id, doc);
      command.success(status,
                      {"digest": doc._attachments[param._attachment].digest});
    }, function (e) {
      command.error(
        "request_timeout",
        "blob error",
        "Error " + e.status + ", unable to get blob content"
      );
    }, function (e) {
      command.notify((e.loaded / e.total) * 100);
    });
  };

  /**
   * Get a document
   *
   * @method get
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.get = function (command, param) {
    var doc = this._storage.getItem(
      this._localpath + "/" + param._id
    );
    if (doc !== null) {
      command.success({"data": doc});
    } else {
      command.error(
        "not_found",
        "missing",
        "Cannot find document"
      );
    }
  };

  /**
   * Get an attachment
   *
   * @method getAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.getAttachment = function (command, param) {
    var doc, i, uint8array, binarystring;
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (doc === null) {
      return command.error(
        "not_found",
        "missing document",
        "Cannot find document"
      );
    }

    if (typeof doc._attachments !== 'object' ||
        typeof doc._attachments[param._attachment] !== 'object') {
      return command.error(
        "not_found",
        "missing attachment",
        "Cannot find attachment"
      );
    }

    // Storing data twice in binarystring and in uint8array (in memory)
    // is not a problem here because localStorage <= 5MB
    binarystring = this._storage.getItem(
      this._localpath + "/" + param._id + "/" + param._attachment
    ) || "";
    uint8array = new Uint8Array(binarystring.length);
    for (i = 0; i < binarystring.length; i += 1) {
      uint8array[i] = binarystring.charCodeAt(i); // mask `& 0xFF` not necessary
    }
    uint8array = new Blob([uint8array.buffer], {
      "type": doc._attachments[param._attachment].content_type || ""
    });

    command.success({
      "data": uint8array,
      "digest": doc._attachments[param._attachment].digest
    });
  };

  /**
   * Remove a document
   *
   * @method remove
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.remove = function (command, param) {
    var doc, i, attachment_list;
    doc = this._storage.getItem(this._localpath + "/" + param._id);
    attachment_list = [];
    if (doc !== null && typeof doc === "object") {
      if (typeof doc._attachments === "object") {
        // prepare list of attachments
        for (i in doc._attachments) {
          if (doc._attachments.hasOwnProperty(i)) {
            attachment_list.push(i);
          }
        }
      }
    } else {
      return command.error(
        "not_found",
        "missing",
        "Document not found"
      );
    }
    this._storage.removeItem(this._localpath + "/" + param._id);
    // delete all attachments
    for (i = 0; i < attachment_list.length; i += 1) {
      this._storage.removeItem(this._localpath + "/" + param._id +
                               "/" + attachment_list[i]);
    }
    command.success();
  };

  /**
   * Remove an attachment
   *
   * @method removeAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.removeAttachment = function (command, param) {
    var doc = this._storage.getItem(this._localpath + "/" + param._id);
    if (typeof doc !== 'object' || doc === null) {
      return command.error(
        "not_found",
        "missing document",
        "Document not found"
      );
    }
    if (typeof doc._attachments !== "object" ||
        typeof doc._attachments[param._attachment] !== "object") {
      return command.error(
        "not_found",
        "missing attachment",
        "Attachment not found"
      );
    }

    delete doc._attachments[param._attachment];
    if (objectIsEmpty(doc._attachments)) {
      delete doc._attachments;
    }
    this._storage.setItem(this._localpath + "/" + param._id, doc);
    this._storage.removeItem(this._localpath + "/" + param._id +
                             "/" + param._attachment);
    command.success();
  };

  /**
   * Get all filenames belonging to a user from the document index
   *
   * @method allDocs
   * @param  {Object} command The JIO command
   * @param  {Object} param The given parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.allDocs = function (command, param, options) {
    var i, row, path_re, rows, document_list, document_object, delete_id;
    param.unused = true;
    rows = [];
    document_list = [];
    path_re = new RegExp(
      "^" + jIO.Query.stringEscapeRegexpCharacters(this._localpath) +
        "/[^/]+$"
    );
    if (options.query === undefined && options.sort_on === undefined &&
        options.select_list === undefined &&
        options.include_docs === undefined) {
      rows = [];
      for (i in this._database) {
        if (this._database.hasOwnProperty(i)) {
          // filter non-documents
          if (path_re.test(i)) {
            row = { value: {} };
            row.id = i.split('/').slice(-1)[0];
            row.key = row.id;
            if (options.include_docs) {
              row.doc = JSON.parse(this._storage.getItem(i));
            }
            rows.push(row);
          }
        }
      }
      command.success({"data": {"rows": rows, "total_rows": rows.length}});
    } else {
      // create jio query object from returned results
      for (i in this._database) {
        if (this._database.hasOwnProperty(i)) {
          if (path_re.test(i)) {
            document_list.push(this._storage.getItem(i));
          }
        }
      }
      options.select_list = options.select_list || [];
      if (options.select_list.indexOf("_id") === -1) {
        options.select_list.push("_id");
        delete_id = true;
      }
      if (options.include_docs === true) {
        document_object = {};
        document_list.forEach(function (meta) {
          document_object[meta._id] = meta;
        });
      }
      jIO.QueryFactory.create(options.query || "",
                              this._key_schema).
        exec(document_list, options).then(function () {
          document_list = document_list.map(function (value) {
            var o = {
              "id": value._id,
              "key": value._id
            };
            if (options.include_docs === true) {
              o.doc = document_object[value._id];
              delete document_object[value._id];
            }
            if (delete_id) {
              delete value._id;
            }
            o.value = value;
            return o;
          });
          command.success({"data": {
            "total_rows": document_list.length,
            "rows": document_list
          }});
        });
    }
  };

  /**
   * Check the storage or a specific document
   *
   * @method check
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.check = function (command, param) {
    this.genericRepair(command, param, false);
  };

  /**
   * Repair the storage or a specific document
   *
   * @method repair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  LocalStorage.prototype.repair = function (command, param) {
    this.genericRepair(command, param, true);
  };

  /**
   * A generic method that manage check or repair command
   *
   * @method genericRepair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Boolean} repair If true then repair else just check
   */
  LocalStorage.prototype.genericRepair = function (command, param, repair) {

    var that = this, final_result;

    function referenceAttachment(param, attachment) {
      if (param.referenced_attachments.indexOf(attachment) !== -1) {
        return;
      }
      var i = param.unreferenced_attachments.indexOf(attachment);
      if (i !== -1) {
        param.unreferenced_attachments.splice(i, 1);
      }
      param.referenced_attachments[param.referenced_attachments.length] =
        attachment;
    }

    function attachmentFound(param, attachment) {
      if (param.referenced_attachments.indexOf(attachment) !== -1) {
        return;
      }
      if (param.unreferenced_attachments.indexOf(attachment) !== -1) {
        return;
      }
      param.unreferenced_attachments[param.unreferenced_attachments.length] =
        attachment;
    }

    function repairOne(param, repair) {
      var i, doc, modified;
      doc = that._storage.getItem(that._localpath + "/" + param._id);
      if (doc === null) {
        return; // OK
      }

      // check document type
      if (typeof doc !== 'object' || doc === null) {
        // wrong document
        if (!repair) {
          return {"error": true, "answers": [
            "conflict",
            "corrupted",
            "Document is unrecoverable"
          ]};
        }
        // delete the document
        that._storage.removeItem(that._localpath + "/" + param._id);
        return; // OK
      }
      // good document type
      // repair json document
      if (!repair) {
        if (!(new jIO.Metadata(doc).check())) {
          return {"error": true, "answers": [
            "conflict",
            "corrupted",
            "Some metadata might be lost"
          ]};
        }
      } else {
        modified = jIO.util.uniqueJSONStringify(doc) !==
          jIO.util.uniqueJSONStringify(new jIO.Metadata(doc).format()._dict);
      }
      if (doc._attachments !== undefined) {
        if (typeof doc._attachments !== 'object') {
          if (!repair) {
            return {"error": true, "answers": [
              "conflict",
              "corrupted",
              "Attachments are unrecoverable"
            ]};
          }
          delete doc._attachments;
          that._storage.setItem(that._localpath + "/" + param._id, doc);
          return; // OK
        }
        for (i in doc._attachments) {
          if (doc._attachments.hasOwnProperty(i)) {
            // check attachment existence
            if (that._storage.getItem(that._localpath + "/" + param._id + "/" +
                                      i) !== 'string') {
              if (!repair) {
                return {"error": true, "answers": [
                  "conflict",
                  "missing attachment",
                  "Attachment \"" + i + "\" of \"" + param._id + "\" is missing"
                ]};
              }
              delete doc._attachments[i];
              if (objectIsEmpty(doc._attachments)) {
                delete doc._attachments;
              }
              modified = true;
            } else {
              // attachment exists
              // check attachment metadata
              // check length
              referenceAttachment(param, param._id + "/" + doc._attachments[i]);
              if (doc._attachments[i].length !== undefined &&
                  typeof doc._attachments[i].length !== 'number') {
                if (!repair) {
                  return {"error": true, "answers": [
                    "conflict",
                    "corrupted",
                    "Attachment metadata length corrupted"
                  ]};
                }
                // It could take a long time to get the length, no repair.
                // length can be omited
                delete doc._attachments[i].length;
              }
              // It could take a long time to regenerate the hash, no check.
              // Impossible to discover the attachment content type.
            }
          }
        }
      }
      if (modified) {
        that._storage.setItem(that._localpath + "/" + param._id, doc);
      }
      // OK
    }

    function repairAll(param, repair) {
      var i, result;
      for (i in that._database) {
        if (that._database.hasOwnProperty(i)) {
          // browsing every entry
          if (i.slice(0, that._localpath.length) === that._localpath) {
            // is part of the user space
            if (/^[^\/]+\/[^\/]+$/.test(i.slice(that._localpath.length + 1))) {
              // this is an attachment
              attachmentFound(param, i.slice(that._localpath.length + 1));
            } else if (/^[^\/]+$/.test(i.slice(that._localpath.length + 1))) {
              // this is a document
              param._id = i.slice(that._localpath.length + 1);
              result = repairOne(param, repair);
              if (result) {
                return result;
              }
            } else {
              // this is pollution
              that._storage.removeItem(i);
            }
          }
        }
      }
      // remove unreferenced attachments
      for (i = 0; i < param.unreferenced_attachments.length; i += 1) {
        that._storage.removeItem(that._localpath + "/" +
                                 param.unreferenced_attachments[i]);
      }
    }

    param.referenced_attachments = [];
    param.unreferenced_attachments = [];
    if (typeof param._id === 'string') {
      final_result = repairOne(param, repair) || {};
    } else {
      final_result = repairAll(param, repair) || {};
    }
    if (final_result.error) {
      return command.error.apply(command, final_result.answers || []);
    }
    command.success.apply(command, final_result.answers || []);
  };

  jIO.addStorage('local', LocalStorage);

  //////////////////////////////////////////////////////////////////////
  // Tools

  function createLocalDescription(username, application_name) {
    if (typeof username !== 'string') {
      throw new TypeError("LocalStorage username must be a string");
    }
    var description = {
      "type": "local",
      "username": username
    };
    if (typeof application_name === 'string') {
      description.application_name = application_name;
    }
    return description;
  }

  function createMemoryDescription(username, application_name) {
    var description = createLocalDescription(username, application_name);
    description.mode = "memory";
    return description;
  }

  /**
   * Tool to help users to create local storage description for JIO
   *
   * @param  {String} username The username
   * @param  {String} [application_name] The application_name
   * @param  {String} [mode="localStorage"] Use localStorage or memory
   * @return {Object} The storage description
   */
  function createDescription(username, application_name, mode) {
    if (mode === undefined || mode.toString() === 'localStorage') {
      return createLocalDescription(username, application_name);
    }
    if (mode.toString() === 'memory') {
      return createMemoryDescription(username, application_name);
    }
    throw new TypeError("Unknown LocalStorage '" + mode.toString() + "' mode");
  }

  exports.createDescription = createDescription;
  exports.createLocalDescription = createLocalDescription;
  exports.createMemoryDescription = createMemoryDescription;

  function clearLocalStorage() {
    var k;
    for (k in localStorage) {
      if (localStorage.hasOwnProperty(k)) {
        if (/^jio\/localstorage\//.test(k)) {
          localStorage.removeItem(k);
        }
      }
    }
  }

  function clearMemoryStorage() {
    jIO.util.dictClear(ram);
  }

  exports.clear = clearLocalStorage;
  exports.clearLocalStorage = clearLocalStorage;
  exports.clearMemoryStorage = clearMemoryStorage;

}));
;/*
 * Copyright 2013, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */
// JIO ERP5 Storage Description :
// {
//   type: "erp5"
//   url: {string}
//   default_view: {string} (optional)
// }

/*jslint indent: 2, nomen: true, unparam: true */
/*global jIO, UriTemplate, FormData, RSVP, URI, DOMParser, Blob,
  ProgressEvent, define */

(function (root, dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  var namespace = module(RSVP, jIO, URI, UriTemplate);
  if (namespace !== undefined) { root.ERP5Storage = namespace; }
}(this, [
  "rsvp",
  "jio",
  "uri",
  "uritemplate"
], function (RSVP, jIO, URI, UriTemplate) {
  "use strict";

  var hasOwnProperty = Function.prototype.call.bind(
    Object.prototype.hasOwnProperty
  ), constant = {};

  constant.method_notification_message_obj = {
    "get": "Getting document.",
    "post": "Posting document.",
    "put": "Putting document.",
    "remove": "Removing document.",
    "getAttachment": "Getting attachment.",
    "putAttachment": "Putting attachment.",
    "removeAttacment": "Removing attachment.",
    "allDocs": "Getting document list."
  };

  // XXX docstring
  function formatGetSuccessAnswer(answer) {
    if (answer === undefined || answer === null) { throw answer; }
    var result;
    if (typeof answer.data === "object" && answer.data) {
      return answer;
    }
    if (answer.target &&
        typeof answer.target.status === "number" &&
        typeof answer.target.statusText === "string") {
      result = {
        "status": answer.target.status
      };
      if (typeof answer.target.response === "object" &&
          answer.target.response !== null) {
        if (typeof answer.target.response.toJSON === "function") {
          result.data = answer.target.response.toJSON();
        } else {
          result.data = answer.target.response;
        }
      } else if (answer.target.response instanceof Blob) {
        return jIO.util.readBlobAsText(answer.target.response).
          then(function (text) {
            result.data = JSON.parse(text);
            return result;
          });
      }
      return result;
    }
    return answer;
  }

  // XXX docstring
  function formatUpdateSuccessAnswer(answer) {
    if (answer === undefined || answer === null) { throw answer; }
    var result;
    if (typeof answer.target === "object" && answer.target !== null &&
        typeof answer.target.status === "number") {
      result = {
        "status": answer.target.status
      };
      return result;
    }
    return answer;
  }

  // XXX docstring
  function formatErrorAnswer(answer) {
    if (answer === undefined || answer === null) { throw answer; }
    var result, dom;
    if (answer.target &&
        typeof answer.target.status === "number" &&
        typeof answer.target.statusText === "string") {
      // seams to be a ProgressEvent
      result = {
        "status": answer.target.status
      };
      if (typeof answer.target.response === "object" &&
          answer.target.response !== null) {
        if (typeof answer.target.response.toJSON === "function") {
          result.data = answer.target.response.toJSON();
        } else {
          result.data = answer.target.response;
        }
      } else if (typeof answer.target.responseText === "string") {
        dom = new DOMParser().parseFromString(
          answer.target.responseText,
          "text/html"
        );
        result.message = (dom.querySelector('#master') ||
                          dom.firstElementChild).textContent;
        if (!result.message) { delete result.message; }
      }
      throw result;
    }
    throw answer;
  }

  // XXX docstring
  function formatNotification(method, notif) {
    var result;
    if (notif) {
      if (typeof notif.loaded === "number" &&
          typeof notif.total === "number") {
        result = {};
        // can be a ProgressEvent or a jIO notification
        if (notif.method !== method) {
          result = {
            "method": method,
            "loaded": notif.loaded,
            "total": notif.total
          };
          if (typeof notif.percentage === "number") {
            result.percentage = notif.percentage;
          }
        }
        if (typeof notif.message === "string") {
          result.message = notif.message;
        } else {
          result.message = constant.method_notification_message_obj[method];
        }
        return result;
      }
    }
    throw null; // stop propagation
  }

  constant.formatSuccessAnswerFor = {
    "post": formatUpdateSuccessAnswer,
    "put": formatUpdateSuccessAnswer,
    "get": formatGetSuccessAnswer
  };

  //////////////////////////////////////////////////////////////////////

  // XXX docstring
  function ERP5Storage(spec) {
    if (typeof spec.url !== "string" || !spec.url) {
      throw new TypeError("ERP5 'url' must be a string " +
                          "which contains more than one character.");
    }
    this._url = spec.url;
    this._default_view = spec.default_view;
  }

  // XXX docstring
  function methodGenerator(method) {
    return function (command, param, options) {
      RSVP.resolve().
        then(function () {
          var view = ERP5Storage.onView[options._view || this._default_view] ||
            ERP5Storage.onView["default"];
          if (typeof view[method] !== "function") {
            view = ERP5Storage.onView["default"];
          }
          return view[method].call(this, param, options);
        }.bind(this)).
        then(constant.formatSuccessAnswerFor[method]).
        then(null, formatErrorAnswer, formatNotification.bind(null, method)).
        then(command.success, command.error, command.progress);
    };
  }

  // XXX docstring
  [
    "post",
    "put",
    "get",
    "remove",
    "putAttachment",
    "getAttachment",
    "removeAttachment",
    "allDocs",
    "check",
    "repair"
  ].forEach(function (method) {
    ERP5Storage.prototype[method] = methodGenerator(method);
  });
  // XXX docstring
  function getSiteDocument(url) {
    if (typeof url !== "string" &&
        typeof (this && this._url) !== "string") {
      throw new TypeError("ERP5Storage.getSiteDocument(): Argument 1 `url` " +
                          "or `this._url` are not of type string.");
    }
    return jIO.util.ajax({
      "type": "GET",
      "url": url || this._url,
      "xhrFields": {
        withCredentials: true
      }
    }).then(function (event) {
      return JSON.parse(event.target.responseText);
    });
  }
  ERP5Storage.getSiteDocument = getSiteDocument;

  // XXX docstring
  function getDocumentAndHatoas(param, options) {
    var this_ = this;
    return ERP5Storage.getSiteDocument(this._url).
      then(function (site_hal) {
        // XXX need to get modified metadata
        return jIO.util.ajax({
          "type": "GET",
          "url": UriTemplate.parse(site_hal._links.traverse.href)
                            .expand({
              relative_url: param._id,
              view: options._view || this_._default_view || "view"
            }),
          "xhrFields": {
            withCredentials: true
          }
        });
      });
  }

  ERP5Storage.onView = {};
  ERP5Storage.onView["default"] = {};

  // XXX docstring
  ERP5Storage.onView["default"].get = function (param, options) {
    return getDocumentAndHatoas.call(this, param, options).
      then(function (response) {
        var result = JSON.parse(response.target.responseText);
        result._id = param._id;
        result.portal_type = result._links.type.name;
        delete result._embedded;
        delete result._links;
        delete result._debug;
        new jIO.Metadata(result).format();
        return {"data": result};
      });
  };

  // XXX docstring
  ERP5Storage.onView["default"].post = function (metadata, options) {
    var final_response;
    return getSiteDocument(this._url)
      .then(function (site_hal) {
        /*jslint forin: true */
        var post_action = site_hal._actions.add,
          data = new FormData();

        data.append("portal_type", metadata.portal_type);

        return jIO.util.ajax({
          "type": post_action.method,
          "url": post_action.href,
          "data": data,
          "xhrFields": {
            withCredentials: true
          }
        });
      }).then(function (event) {
        final_response = {"status": event.target.status};
        if (!metadata._id) {
          // XXX Really depend on server response...
          var uri = new URI(event.target.getResponseHeader("X-Location"));
          final_response.id = uri.segment(2);
          metadata._id = final_response.id;
        }
      }).
      then(ERP5Storage.onView["default"].put.bind(this, metadata, options)).
      then(function () { return final_response; });
  };

  // XXX docstring
  ERP5Storage.onView["default"].put = function (metadata, options) {
    return getDocumentAndHatoas.call(this, metadata, options).
      then(function (result) {
        /*jslint forin: true */
        result = JSON.parse(result.target.responseText);
        var put_action = result._embedded._view._actions.put,
          renderer_form = result._embedded._view,
          data = new FormData(),
          key;
        data.append(renderer_form.form_id.key,
                    renderer_form.form_id['default']);
        for (key in metadata) {
          if (hasOwnProperty(metadata, key)) {
            if (key !== "_id") {
              // Hardcoded my_ ERP5 behaviour
              if (hasOwnProperty(renderer_form, "my_" + key)) {
                data.append(renderer_form["my_" + key].key, metadata[key]);
              }
            }
          }
        }
        return jIO.util.ajax({
          "type": put_action.method,
          "url": put_action.href,
          "data": data,
          "xhrFields": {
            withCredentials: true
          }
        });
      });
  };

  ERP5Storage.onView["default"].remove = function () {
    return;
  };

  ERP5Storage.onView["default"].allDocs = function (param, options) {
    if (typeof options.query !== "string") {
      options.query = (options.query ?
                       jIO.Query.objectToSearchText(options.query) :
                       undefined);
    }
    return getSiteDocument(this._url)
      .then(function (site_hal) {
        return jIO.util.ajax({
          "type": "GET",
          "url": UriTemplate.parse(site_hal._links.raw_search.href)
                            .expand({
              query: options.query,
              // XXX Force erp5 to return embedded document
              select_list: options.select_list || ["title", "reference"],
              limit: options.limit
            }),
          "xhrFields": {
            withCredentials: true
          }
        });
      })
      .then(function (response) {
        return JSON.parse(response.target.responseText);
      })
      .then(function (catalog_json) {
        var data = catalog_json._embedded.contents,
          count = data.length,
          i,
          uri,
          item,
          result = [],
          promise_list = [result];
        for (i = 0; i < count; i += 1) {
          item = data[i];
          uri = new URI(item._links.self.href);
          result.push({
            id: uri.segment(2),
            key: uri.segment(2),
            doc: {},
            value: item
          });
//           if (options.include_docs) {
//             promise_list.push(RSVP.Queue().push(function () {
//               return this._get({_id: item.name}, {_view: "View"});
//             }).push
//           }
        }
        return RSVP.all(promise_list);
      })
      .then(function (promise_list) {
        var result = promise_list[0];
        return {"data": {"rows": result, "total_rows": result.length}};
      });
  };

  ERP5Storage.onView["default"].check = function () {
    return;
  };

  ERP5Storage.onView["default"].repair = function () {
    return;
  };

  jIO.addStorage("erp5", ERP5Storage);

  return ERP5Storage;

}));
;/*
 * Copyright 2014, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/**
 * JIO Indexed Database Storage.
 *
 * A local browser "database" storage greatly more powerful than localStorage.
 *
 * Description:
 *
 *    {
 *      "type": "indexeddb",
 *      "database": <string>,
 *      "unite": <integer> //byte
 *    }
 *
 * The database name will be prefixed by "jio:", so if the database property is
 * "hello", then you can manually reach this database with
 * `indexedDB.open("jio:hello");`. (Or
 * `indexedDB.deleteDatabase("jio:hello");`.)
 *
 * For more informations:
 *
 * - http://www.w3.org/TR/IndexedDB/
 * - https://developer.mozilla.org/en-US/docs/IndexedDB/Using_IndexedDB
 */

/*jslint indent: 2, maxlen: 80, nomen: true */
/*global define, module, require, indexedDB, jIO, RSVP, Blob, Math*/

(function (dependencies, factory) {
  "use strict";
  if (typeof define === "function" && define.amd) {
    return define(dependencies, factory);
  }
  if (typeof module === "object" && module !== null &&
      typeof module.exports === "object" && module.exports !== null &&
      typeof require === "function") {
    module.exports = factory.apply(null, dependencies.map(require));
    return;
  }
  factory(jIO, RSVP);
}(["jio", "rsvp"], function (jIO, RSVP) {
  "use strict";

  var Promise = RSVP.Promise, generateUuid = jIO.util.generateUuid;

  function metadataObjectToString(value) {
    var i, l;
    if (Array.isArray(value)) {
      for (i = 0, l = value.length; i < l; i += 1) {
        value[i] = metadataObjectToString(value[i]);
      }
      return value;
    }
    if (typeof value === "object" && value !== null) {
      return value.content;
    }
    return value;
  }

  /**
   * new IndexedDBStorage(description)
   *
   * Creates a storage object designed for jIO to store documents into
   * indexedDB.
   *
   * @class IndexedDBStorage
   * @constructor
   */
  function IndexedDBStorage(description) {
    if (typeof description.database !== "string" ||
        description.database === "") {
      throw new TypeError("IndexedDBStorage 'database' description property " +
                          "must be a non-empty string");
    }
    if (description.unite !== undefined) {
      if (description.unite !== parseInt(description.unite, 10)) {
        throw new TypeError("IndexedDBStorage 'unite' description property " +
                            "must be a integer");
      }
    } else {
      description.unite = 2000000;
    }
    this._database_name = "jio:" + description.database;
    this._unite = description.unite;
  }


  /**
   * creat 3 objectStores
   * @param {string} the name of the database
   */
  function openIndexedDB(db_name) {
    var request;
    function resolver(resolve, reject) {
      // Open DB //
      request = indexedDB.open(db_name);
      request.onerror = reject;

      // Create DB if necessary //
      request.onupgradeneeded = function (evt) {
        var db = evt.target.result,
          store;
        store = db.createObjectStore("metadata", {
          "keyPath": "_id"
           //"autoIncrement": true
        });
        store.createIndex("_id", "_id");


        store = db.createObjectStore("attachment", {
          "keyPath": "_id"
           //"autoIncrement": true
        });
        store.createIndex("_id", "_id");

        store = db.createObjectStore("blob", {
          "keyPath": ["_id", "_attachment", "_part"]
          //"autoIncrement": true
        });
        store.createIndex("_id_attachment_part",
                          ["_id", "_attachment", "_part"]);
      };
      request.onsuccess = function () {
        resolve(request.result);
      };
    }
    return new RSVP.Promise(resolver);
  }




  IndexedDBStorage.prototype.createDBIfNecessary = function () {
    return openIndexedDB(this._database_name);
  };

  /**
   *put a data into a store object
   *@param {ObjectStore} store The objectstore
   *@param {Object} metadata The data to put in
   *@return a new promise
   */
  function putIndexedDBArrayBuffer(store, metadata) {
    var request,
      resolver;
    request = store.put(metadata);
    resolver = function (resolve, reject) {
      request.onerror = function (e) {
        reject(e);
      };
      request.onsuccess = function () {
        resolve(metadata);
      };
    };
    return new RSVP.Promise(resolver);
  }

  function putIndexedDB(store, metadata, readData) {
    var request,
      resolver;
    try {
      request = store.put(metadata);
      resolver = function (resolve, reject) {
        request.onerror = function (e) {
          reject(e);
        };
        request.onsuccess = function () {
          resolve(metadata);
        };
      };
      return new RSVP.Promise(resolver);
    } catch (e) {
      return putIndexedDBArrayBuffer(store,
                                     {"_id" : metadata._id,
                                      "_attachment" : metadata._attachment,
                                      "_part" : metadata._part,
                                      "blob": readData});
    }
  }

  function transactionEnd(transaction) {
    var resolver;
    resolver = function (resolve, reject) {
      transaction.onabort = reject;
      transaction.oncomplete = function () {
        resolve("end");
      };
    };
    return new RSVP.Promise(resolver);
  }
  /**
   * get a data from a store object
   * @param {ObjectStore} store The objectstore
   * @param {String} id The data id
   * return a new promise
   */
  function getIndexedDB(store, id) {
    function resolver(resolve, reject) {
      var request = store.get(id);
      request.onerror = reject;
      request.onsuccess = function () {
        resolve(request.result);
      };
    }
    return new RSVP.Promise(resolver);
  }

  /**
   * delete a data of a store object
   * @param {ObjectStore} store The objectstore
   * @param {String} id The data id
   * @return a new promise
   *
   */
  function removeIndexedDB(store, id) {
    function resolver(resolve, reject) {
      var request = store["delete"](id);
      request.onerror = function (e) {
        reject(e);
      };
      request.onsuccess = function () {
        resolve(request.result);
      };
    }
    return new RSVP.Promise(resolver);
  }

  /**
   * research an id in a store
   * @param {ObjectStore} store The objectstore
   * @param {String} id The index id
   * @param {var} researchID The data id
   * return a new promise
   */
  function researchIndexedDB(store, id, researchID) {
    function resolver(resolve) {
      var index = store.index(researchID);
      index.get(id).onsuccess = function (evt) {
        resolve({"result" : evt.target.result, "store": store});
      };
    }
    return new RSVP.Promise(resolver);
  }


  function promiseResearch(transaction, id, table, researchID) {
    var store = transaction.objectStore(table);
    return researchIndexedDB(store, id, researchID);
  }

  /**
   * put or post a metadata into objectstore:metadata,attachment
   * @param {function} open The function to open a basedata
   * @param {function} research The function to reserach
   * @param {function} ongoing  The function to process
   * @param {function} end      The completed function
   * @param {Object}  command   The JIO command
   * @param {Object}  metadata  The data to put
   */
  IndexedDBStorage.prototype._putOrPost =
        function (open, research, ongoing, end, command, metadata) {
      var jio_storage = this,
        transaction,
        global_db,
        result;

      return new RSVP.Queue()
        .push(function () {
          //open a database
          return open(jio_storage._database_name);
        })
        .push(function (db) {
          global_db = db;
          transaction =  db.transaction(["metadata",
                                         "attachment"], "readwrite");
          //research in metadata
          return research(transaction, metadata._id, "metadata", "_id");
        })
        .push(function (researchResult) {
          return ongoing(researchResult);
        })
        .push(function (ongoingResult) {
          //research in attachment
          result = ongoingResult;
          return research(transaction, metadata._id, "attachment", "_id");
        })
        .push(function (researchResult) {
          //create an id in attachment si necessary
          if (researchResult.result === undefined) {
            return putIndexedDB(researchResult.store, {"_id": metadata._id});
          }
        })
        .push(function () {
          return transactionEnd(transaction);
        })
        .push(function () {
          return end(result);
        })
        .push(undefined, function (error) {
          if (global_db !== undefined) {
            global_db.close();
          }
          throw error;
        })
        .push(command.success, command.error, command.notify);
    };




  /**
   * Retrieve data
   *
   *@param {Object} command The JIO command
   *@param {Object} param The command parameters
   */
  IndexedDBStorage.prototype.get = function (command, param) {
    var jio_storage = this,
      transaction,
      global_db,
      meta;
    return new RSVP.Queue()
      .push(function () {
        return openIndexedDB(jio_storage._database_name);
      })
      .push(function (db) {
        global_db = db;
        transaction =  db.transaction(["metadata", "attachment"], "readwrite");
        var store = transaction.objectStore("metadata");
        return getIndexedDB(store, param._id);
      })
      .push(function (result) {
        if (result) {
         //get a part data from metadata
          meta = result;
          var store = transaction.objectStore("attachment");
          return getIndexedDB(store, param._id);
        }
        throw ({"status": 404, "reason": "Not Found",
                "message": "IndexeddbStorage, unable to get document."});
      })
      .push(function (result) {
        //get the reste data from attachment
        if (result._attachment) {
          meta._attachment = result._attachment;
        }
        return transactionEnd(transaction);
      })
      .push(function () {
        return ({"data": meta});
      })
      .push(undefined, function (error) {
        if (global_db !== undefined) {
          global_db.close();
        }
        throw error;
      })
      .push(command.success, command.error, command.notify);
  };


  /**
   * Remove a document
   *
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   */
  IndexedDBStorage.prototype.remove = function (command, param) {
    var jio_storage = this,
      transaction,
      global_db,
      queue = new RSVP.Queue();
    function removeAllPart(store, attachment, part, totalLength) {
      if (part * jio_storage._unite >= totalLength) {
        return;
      }
      return removeIndexedDB(store, [param._id, attachment, part])
        .then(function () {
          return removeAllPart(store, attachment, part + 1, totalLength);
        });
    }
    function removeAll(store, array, index, allAttachment) {
      var totalLength = allAttachment[array[index]].length;
      return removeAllPart(store, array[index], 0, totalLength)
        .then(function () {
          if (index < array.length - 1) {
            return removeAll(store, array, index + 1, allAttachment);
          }
        });
    }
    return queue.push(function () {
      return openIndexedDB(jio_storage._database_name);
    })
        .push(function (db) {
        global_db = db;
        transaction =  db.transaction(["metadata",
                                       "attachment", "blob"], "readwrite");
        return promiseResearch(transaction, param._id, "metadata", "_id");
      })
       .push(function (resultResearch) {
        if (resultResearch.result === undefined) {
          throw ({"status": 404, "reason": "Not Found",
                  "message": "IndexeddbStorage, unable to get metadata."});
        }
        //delete metadata
        return removeIndexedDB(resultResearch.store, param._id);
      })
       .push(function () {
        var store = transaction.objectStore("attachment");
        return getIndexedDB(store, param._id);
      })
        .push(function (result) {
        if (result._attachment) {
          var array, store;
          array = Object.keys(result._attachment);
          store = transaction.objectStore("blob");
          return removeAll(store, array, 0, result._attachment);
        }
      })
      .push(function () {
        var store = transaction.objectStore("attachment");
        //delete attachment
        return removeIndexedDB(store, param._id);
      })
      .push(function () {
        return transactionEnd(transaction);
      })
      .push(function () {
        return ({"status": 204});
      })
        .push(undefined, function (error) {
        if (global_db !== undefined) {
          global_db.close();
        }
        throw error;
      })
        .push(command.success, command.error, command.notify);
  };



  /**
   * Creates a new document if not already existes
   * @param {Object} command The JIO command
   * @param {Object} metadata The metadata to put
   */
  IndexedDBStorage.prototype.post = function (command, metadata) {
    var that = this;
    if (!metadata._id) {
      metadata._id = generateUuid();
    }
    function promiseOngoingPost(researchResult) {
      if (researchResult.result === undefined) {
        delete metadata._attachment;
        return putIndexedDB(researchResult.store, metadata);
      }
      throw ({"status": 409, "reason": "Document exists"});
    }

    function promiseEndPost(metadata) {
      return ({"id": metadata._id});
    }

    return that._putOrPost(openIndexedDB, promiseResearch,
                            promiseOngoingPost, promiseEndPost,
                            command, metadata);

  };
  /**
   * Creates or updates a document
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to post
   */
  IndexedDBStorage.prototype.put = function (command, metadata) {
    var that = this,
      found;
    function promiseOngoingPut(researchResult) {
      var key;
      for (key in metadata) {
        if (metadata.hasOwnProperty(key)) {
          metadata[key] = metadataObjectToString(metadata[key]);
        }
      }
      delete metadata._attachment;
      if (researchResult.result !== undefined) {
        found = true;
      }
      return putIndexedDB(researchResult.store, metadata);
    }

    function promiseEndPut() {
      return {"status": (found ? 204 : 201) };
    }
    return that._putOrPost(openIndexedDB, promiseResearch,
                  promiseOngoingPut, promiseEndPut,
                  command, metadata);

  };




  /**
   * Retrieve a list of present document
   *
   * @method allDocs
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   * @param  {Boolean} [options.include_docs=false]
   *   Also retrieve the actual document content.
   */
  IndexedDBStorage.prototype.getListMetadata = function (option) {
    var rows = [], onCancel, open_req = indexedDB.open(this._database_name);
    return new Promise(function (resolve, reject, notify) {
      open_req.onerror = function () {
        if (open_req.result) { open_req.result.close(); }
        reject(open_req.error);
      };
      open_req.onsuccess = function () {
        var tx, date, j = 0, index_req, db = open_req.result;
        try {
          tx = db.transaction(["metadata", "attachment"], "readonly");
          onCancel = function () {
            tx.abort();
            db.close();
          };
          index_req = tx.objectStore("metadata").index("_id").openCursor();
          date = Date.now();
          index_req.onsuccess = function (event) {
            var cursor = event.target.result, now, value, i, key;
            if (cursor) {
              // Called for each matching record
              // notification management
              now = Date.now();
              if (date <= now - 1000) {
                notify({"loaded": rows.length});
                date = now;
              }
              // option.limit management
              if (Array.isArray(option.limit)) {
                if (option.limit.length > 1) {
                  if (option.limit[0] > 0) {
                    option.limit[0] -= 1;
                    cursor["continue"]();
                    return;
                  }
                  if (option.limit[1] <= 0) {
                    // end
                    index_req.onsuccess({"target": {}});
                    return;
                  }
                  option.limit[1] -= 1;
                } else {
                  if (option.limit[0] <= 0) {
                    // end
                    index_req.onsuccess({"target": {}});
                    return;
                  }
                  option.limit[0] -= 1;
                }
              }
              value = {};
              // option.select_list management
              if (option.select_list) {
                for (i = 0; i < option.select_list.length; i += 1) {
                  key = option.select_list[i];
                  value[key] = cursor.value[key];
                }
              }
              // option.include_docs management
              if (option.include_docs) {
                rows.push({
                  "id": cursor.value._id,
                  "doc": cursor.value,
                  "value": value
                });
              } else {
                rows.push({
                  "id": cursor.value._id,
                  "value": value
                });
              }
              // continue to next iteration
              cursor["continue"]();
            } else {
              index_req = tx.objectStore("attachment").
                    index("_id").openCursor();
              index_req.onsuccess = function (event) {
                //second table
                cursor = event.target.result;
                if (cursor) {
                  value = {};
                  if (cursor.value._attachment) {
                    if (option.select_list) {
                      for (i = 0; i < option.select_list.length; i += 1) {
                        key = option.select_list[i];
                        value[key] = cursor.value._attachment[key];
                      }
                    }
                    //add info of attachment into metadata
                    rows[j].value._attachment = value;
                    if (option.include_docs) {
                      rows[j].doc._attachment = cursor.value._attachment;
                    }
                  }
                  j += 1;
                  cursor["continue"]();
                } else {
                  notify({"loaded": rows.length});
                  resolve({"data": {"rows": rows, "total_rows": rows.length}});
                  db.close();
                }
              };
            }
          };
        } catch (e) {
          reject(e);
          db.close();
        }
      };
    }, function () {
      if (typeof onCancel === "function") {
        onCancel();
      }
    });
  };


  /**
   * Add an attachment to a document
   *
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The data
   *
   */
  IndexedDBStorage.prototype.putAttachment = function (command, metadata) {
    var jio_storage = this,
      transaction,
      global_db,
      BlobInfo,
      readResult;
    function putAllPart(store, metadata, readResult, count, part) {
      var blob,
        readPart,
        end;
      if (count >= metadata._blob.size) {
        return;
      }
      end = count + jio_storage._unite;
      blob = metadata._blob.slice(count, end);
      readPart = readResult.slice(count, end);
      return putIndexedDB(store, {"_id": metadata._id,
                                  "_attachment" : metadata._attachment,
                                  "_part" : part,
                                  "blob": blob}, readPart)
        .then(function () {
          return putAllPart(store, metadata, readResult, end, part + 1);
        });
    }
    return jIO.util.readBlobAsArrayBuffer(metadata._blob)
      .then(function (event) {
        readResult = event.target.result;
        BlobInfo = {
          "content_type": metadata._blob.type,
          "length": metadata._blob.size
        };
        return new RSVP.Queue()
            .push(function () {
            return openIndexedDB(jio_storage._database_name);
          })
            .push(function (db) {
            global_db = db;
            transaction = db.transaction(["attachment",
                    "blob"], "readwrite");
            return promiseResearch(transaction,
                                   metadata._id, "attachment", "_id");
          })
            .push(function (researchResult) {
            if (researchResult.result === undefined) {
              throw ({"status": 404, "reason": "Not Found",
                "message": "indexeddbStorage unable to put attachment"});
            }
        //update attachment
            researchResult.result._attachment = researchResult.
                result._attachment || {};
            researchResult.result._attachment[metadata._attachment] =
                    (BlobInfo === undefined) ? "BlobInfo" : BlobInfo;
            return putIndexedDB(researchResult.store, researchResult.result);
          })
          .push(function () {
        //put in blob
            var store = transaction.objectStore("blob");
            return putAllPart(store, metadata, readResult, 0, 0);
          })
          .push(function () {
            return transactionEnd(transaction);
          })
          .push(function () {
            return {"status": 204};
          })
          .push(undefined, function (error) {
            if (global_db !== undefined) {
              global_db.close();
            }
            throw error;
          })
            .push(command.success, command.error, command.notify);
      });
  };



  /**
   * Retriev a document attachment
   *
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameter
   */
  IndexedDBStorage.prototype.getAttachment = function (command, param) {
    var jio_storage = this,
      transaction,
      global_db,
      blob,
      content_type,
      totalLength;
    function getDesirePart(store, start, end) {
      if (start > end) {
        return;
      }
      return getIndexedDB(store, [param._id, param._attachment, start])
        .then(function (result) {
          var blobPart = result.blob;
          if (result.blob.byteLength !== undefined) {
            blobPart = new Blob([result.blob]);
          }
          if (blob) {
            blob = new Blob([blob, blobPart]);
          } else {
            blob = blobPart;
          }
          return getDesirePart(store, start + 1, end);
        });
    }
    return new RSVP.Queue()
      .push(function () {
        return openIndexedDB(jio_storage._database_name);
      })
      .push(function (db) {
        global_db = db;
        transaction = db.transaction(["attachment", "blob"], "readwrite");
        //check if the attachment exists
        return promiseResearch(transaction,
                               param._id, "attachment", "_id");
      })
      .push(function (researchResult) {
        var result = researchResult.result,
          start,
          end;
        if (result === undefined ||
            result._attachment[param._attachment] === undefined) {
          throw ({"status": 404, "reason": "missing attachment",
                  "message": "IndexeddbStorage, unable to get attachment."});
        }
        content_type = result._attachment[param._attachment].content_type;
        totalLength = result._attachment[param._attachment].length;
        param._start = param._start === undefined ? 0 : param._start;
        param._end = param._end === undefined ? totalLength
          : param._end;
        if (param._end > totalLength) {
          param._end = totalLength;
        }
        if (param._start < 0 || param._end < 0) {
          throw ({"status": 404, "reason": "invalide _start, _end",
                  "message": "_start and _end must be positive"});
        }
        if (param._start > param._end) {
          throw ({"status": 404, "reason": "invalide offset",
                  "message": "start is great then end"});
        }
        start = Math.floor(param._start / jio_storage._unite);
        end =  Math.floor(param._end / jio_storage._unite);
        if (param._end % jio_storage._unite === 0) {
          end -= 1;
        }
        return getDesirePart(transaction.objectStore("blob"),
                             start,
                             end);
      })
      .push(function () {
        var start = param._start % jio_storage._unite,
          end = start + param._end - param._start;
        blob = blob.slice(start, end);
        return ({ "data": new Blob([blob], {type: content_type})});
      })
      .push(undefined, function (error) {
        // Check if transaction is ongoing, if so, abort it
        if (transaction !== undefined) {
          transaction.abort();
        }
        if (global_db !== undefined) {
          global_db.close();
        }
        throw error;
      })
            .push(command.success, command.error, command.notify);
  };


  /**
   * Remove an attachment
   *
   * @method removeAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   */
  IndexedDBStorage.prototype.removeAttachment = function (command, param) {
    var jio_storage = this,
      transaction,
      global_db,
      totalLength;
    function removePart(store, part) {
      if (part * jio_storage._unite >= totalLength) {
        return;
      }
      return removeIndexedDB(store, [param._id, param._attachment, part])
        .then(function () {
          return removePart(store, part + 1);
        });
    }
    return new RSVP.Queue()
      .push(function () {
        return openIndexedDB(jio_storage._database_name);
      })
      .push(function (db) {
        global_db = db;
        transaction = db.transaction(["attachment", "blob"], "readwrite");
        //check if the attachment exists
        return promiseResearch(transaction, param._id,
                               "attachment", "_id");
      })
      .push(function (researchResult) {
        var result = researchResult.result;
        if (result === undefined ||
            result._attachment[param._attachment] === undefined) {
          throw ({"status": 404, "reason": "missing attachment",
                  "message":
                  "IndexeddbStorage, document attachment not found."});
        }
        totalLength = result._attachment[param._attachment].length;
        //updata attachment
        delete result._attachment[param._attachment];
        return putIndexedDB(researchResult.store, result);
      })
      .push(function () {
        var store = transaction.objectStore("blob");
        return removePart(store, 0);
      })
      .push(function () {
        return transactionEnd(transaction);
      })
       .push(function () {
        return ({ "status": 204 });
      })
       .push(undefined, function (error) {
        if (global_db !== undefined) {
          global_db.close();
        }
        throw error;
      })
        .push(command.success, command.error, command.notify);
  };


  IndexedDBStorage.prototype.allDocs = function (command, param, option) {
    /*jslint unparam: true */
    this.createDBIfNecessary().
      then(this.getListMetadata.bind(this, option)).
      then(command.success, command.error, command.notify);
  };

  IndexedDBStorage.prototype.check = function (command) {
    command.success();
  };

  IndexedDBStorage.prototype.repair = function (command) {
    command.success();
  };

  jIO.addStorage("indexeddb", IndexedDBStorage);
}));
;/*
 * Copyright 2014, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/**
 *
 * Description:
 *
 *    {
 *      "type": "http",
 *      "database": ip
 *    }
 */

/*jslint indent: 2, maxlen: 80, nomen: true */
/*global define, module, require, XMLHttpRequest, jIO, RSVP, Blob, JSON,
decodeURI, encodeURI*/

(function (dependencies, factory) {
  "use strict";
  if (typeof define === "function" && define.amd) {
    return define(dependencies, factory);
  }
  if (typeof module === "object" && module !== null &&
      typeof module.exports === "object" && module.exports !== null &&
      typeof require === "function") {
    module.exports = factory.apply(null, dependencies.map(require));
    return;
  }
  factory(jIO, RSVP);
}(["jio", "rsvp"], function (jIO, RSVP) {
  "use strict";

  var Promise = RSVP.Promise;
   // data = {};
  function httpStorage(description) {
    if (typeof description.database !== "string" ||
        description.database === "") {
      throw new TypeError("httpLocalStorage 'database' description property " +
                          "must be a non-empty string");
    }

    this._ip = description.database;
  }

  httpStorage.prototype.getList = function () {
    var xml = new XMLHttpRequest(),
      url = this._ip,
      rows = [],
      result,
      index,
      name,
      that = this;
    return new Promise(function (resolve, reject) {
      xml.onerror = function (e) {
        reject(e);
      };
      xml.onload = function (e) {
        if (this.status === 200) {
          jIO.util.readBlobAsText(this.response).then(function (event) {
            result = event.target.result;
            while (result) {
              index = result.indexOf("href=\"/");
              if (index === -1) {
                break;
              }
              result = result.substring(index + 7);
              index = result.indexOf("\">");
              url = result.substring(0, index);
              if (url.indexOf(".webm") !== -1 ||
                  url.indexOf(".mp4") !== -1) {
                name = decodeURI(url);
                rows.push({
                  "id": url,
                  "doc": {"title" : name,
                          "type" : "video/webm"}
                });
                result = result.substring(index + 2);
              }
              if (url.indexOf(".mp3") !== -1) {
                name = decodeURI(url);
                rows.push({
                  "id": url,
                  "doc": {"title" : name,
                          "type" : "audio/mpeg"}
                });
              }
            }
            that._data = {"data": {"rows": rows, "total_rows": rows.length}};
            resolve(that._data);
          });
        } else {
          reject({"reason" : e});
        }
      };
      xml.open("GET", url, true);
      xml.responseType = 'blob';
      xml.send();
    });
  };

  httpStorage.prototype.get = function (command, param) {
    var jio_storage = this,
      i,
      length;
    return jio_storage.getList()
      .then(function (result) {
        length = result.data.rows.length;
        for (i = 0; i < length; i += 1) {
          if (result.data.rows[i].id === encodeURI(param._id)) {  //xxx
            return ({"data": {"title" : result.data.rows[i].doc.title}});
          }
        }
      })
      .then(command.success, command.error, command.notify);
  };

  httpStorage.prototype.getAttachment = function (command, metadata) {
    var xml = new XMLHttpRequest(),
      url = this._ip + metadata._id,
      pro;
    if (metadata._attachment === "getUrlBlob") {
      pro = new Promise(function (resolve) {
        resolve({"data" : url});
      });
    } else {
      pro = new Promise(function (resolve, reject) {
        xml.onerror = function (e) {
          reject(e);
        };
        xml.onload = function (e) {
          if (this.status === 200) {
            resolve({"data" : this.response});
          } else {
            reject(e);
          }
        };
        xml.open("GET", url, true);
        xml.responseType = 'blob';
        xml.send();
      });
    }
    pro.then(command.success, command.error, command.notify);
  };
  httpStorage.prototype.put = function (command) {
    command.success();
  };


  httpStorage.prototype.allDocs = function (command) {
    this.getList()
      .then(command.success, command.error, command.notify);
  };

  jIO.addStorage("http", httpStorage);
}));
;/*
 * Copyright 2013, Nexedi SA
 * Released under the LGPL license.
 * http://www.gnu.org/licenses/lgpl.html
 */

/*jslint indent: 2, maxlen: 80, nomen: true, regexp: true, unparam: true */
/*global define, window, jIO, RSVP, btoa, DOMParser, Blob */

// JIO Dav Storage Description :
// {
//   type: "dav",
//   url: {string}
//   // No Authentication Here
// }

// {
//   type: "dav",
//   url: {string},
//   basic_login: {string} // Basic authentication
// }

// NOTE: to get the authentication type ->
// curl --verbose  -X OPTION http://domain/
// In the headers: "WWW-Authenticate: Basic realm="DAV-upload"

// URL Characters convertion:
// If I want to retrieve the file which id is -> http://100%.json
// http://domain/collection/http://100%.json cannot be applied
// - '/' is col separator,
// - '?' is url/parameter separator
// - '%' is special char
// - '.' document and attachment separator
// http://100%.json will become
// - http:%2F%2F100%25.json to avoid bad request ('/', '%' -> '%2F', '%25')
// - http:%2F%2F100%25_.json to avoid ids conflicts ('.' -> '_.')
// - http:%252F%252F100%2525_.json to avoid request bad interpretation
//   ('%', '%25')
// The file will be saved as http:%2F%2F100%25_.json

// define([module_name], [dependencies], module);
(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  window.dav_storage = {};
  module(window.dav_storage, RSVP, jIO);
}(['exports', 'rsvp', 'jio'], function (exports, RSVP, jIO) {
  "use strict";

  /**
   * Removes the last character if it is a "/". "/a/b/c/" become "/a/b/c"
   *
   * @param  {String} string The string to modify
   * @return {String} The modified string
   */
  function removeLastSlashes(string) {
    return string.replace(/\/*$/, '');
  }

  /**
   * Tool to create a ready to use JIO storage description for Dav Storage
   *
   * @param  {String} url The url
   * @param  {String} [auth_type] The authentication type: 'none', 'basic' or
   *   'digest'
   * @param  {String} [realm] The realm
   * @param  {String} [username] The username
   * @param  {String} [password] The password
   * @return {Object} The dav storage description
   */
  function createDescription(url, auth_type, realm, username, password) {
    if (typeof url !== 'string') {
      throw new TypeError("dav_storage.createDescription(): URL: " +
                          "Argument 1 is not of type string");
    }

    function checkUserAndPwd(username, password) {
      if (typeof username !== 'string') {
        throw new TypeError("dav_storage.createDescription(): Username: " +
                            "Argument 4 is not of type string");
      }
      if (typeof password !== 'string') {
        throw new TypeError("dav_storage.createDescription(): Password: " +
                            "Argument 5 is not of type string");
      }
    }

    switch (auth_type) {
    case 'none':
      return {
        "type": "dav",
        "url": removeLastSlashes(url)
      };
    case 'basic':
      checkUserAndPwd(username, password);
      return {
        "type": "dav",
        "url": removeLastSlashes(url),
        "basic_login": btoa(username + ":" + password)
      };
    case 'digest':
      // XXX
      realm.toString();
      throw new Error("Not Implemented");
    default:
      throw new TypeError("dav_storage.createDescription(): " +
                          "Authentication type: " +
                          "Argument 2 is not 'none', 'basic' nor 'digest'");
    }
  }
  exports.createDescription = createDescription;

  /**
   * Changes spaces to %20, / to %2f, % to %25 and ? to %3f
   *
   * @param  {String} name The name to secure
   * @return {String} The secured name
   */
  function secureName(name) {
    return encodeURI(name).replace(/\//g, '%2F').replace(/\?/g, '%3F');
  }

  /**
   * Restores the original name from a secured name
   *
   * @param  {String} secured_name The secured name to restore
   * @return {String} The original name
   */
  function restoreName(secured_name) {
    return decodeURI(secured_name.replace(/%3F/ig, '?').replace(/%2F/ig, '/'));
  }

  /**
   * Convert document id and attachment id to a file name
   *
   * @param  {String} doc_id The document id
   * @param  {String} attachment_id The attachment id (optional)
   * @return {String} The file name
   */
  function idsToFileName(doc_id, attachment_id) {
    doc_id = secureName(doc_id).replace(/\./g, '_.');
    if (typeof attachment_id === "string") {
      attachment_id = secureName(attachment_id);
      return doc_id + "." + attachment_id;
    }
    return doc_id;
  }

  /**
   * Convert a file name to a document id (and attachment id if there)
   *
   * @param  {String} file_name The file name to convert
   * @return {Array} ["document id", "attachment id"] or ["document id"]
   */
  function fileNameToIds(file_name) {
    /*jslint regexp: true */
    file_name = /^((?:_\.|[^\.])*)(?:\.(.*))?$/.exec(file_name);
    if (file_name === null ||
        (file_name[1] &&
         file_name[1].length === 0)) {
      return [];
    }
    if (file_name[2]) {
      if (file_name[2].length > 0) {
        return [restoreName(file_name[1].replace(/_\./g, '.')),
                restoreName(file_name[2])];
      }
      return [];
    }
    return [restoreName(file_name[1].replace(/_\./g, '.'))];
  }

  function promiseSucceed(promise) {
    return new RSVP.Promise(function (resolve, reject, notify) {
      promise.then(resolve, reject, notify);
    }, function () {
      promise.cancel();
    });
  }

  /**
   * An ajax object to do the good request according to the auth type
   */
  var ajax = {
    "none": function (method, type, url, data, start, end) {
      var headers = {};
      if (start !== undefined) {
        if (end !== undefined) {
          headers = {"Range" : "bytes=" + start + "-" + end};
        } else {
          headers = {"Range" : "bytes=" + start + "-"};
        }
      }
      if (method === "PROPFIND") {
        headers.Depth = "1";
      }
      return jIO.util.ajax({
        "type": method,
        "url": url,
        "dataType": type,
        "data": data,
        "headers": headers
      });
    },
    "basic": function (method, type, url, data, start, end, login) {
      var headers = {"Authorization": "Basic " + login};
      if (start !== undefined) {
        if (end !== undefined) {
          headers.Range = "bytes=" + start + "-" + end;
        } else {
          headers.Range = "bytes=" + start + "-";
        }
      }
      if (method === "PROPFIND") {
        headers.Depth = "1";
      }
      return jIO.util.ajax({
        "type": method,
        "url": url,
        "dataType": type,
        "data": data,
        "headers": headers
      });
    },
    "digest": function () {
      // XXX
      throw new TypeError("DavStorage digest not implemented");
    }
  };

  /**
   * The JIO WebDAV Storage extension
   *
   * @class DavStorage
   * @constructor
   */
  function DavStorage(spec) {
    if (typeof spec.url !== 'string') {
      throw new TypeError("DavStorage 'url' is not of type string");
    }
    this._url = removeLastSlashes(spec.url);
    // XXX digest login
    if (typeof spec.basic_login === 'string') {
      this._auth_type = 'basic';
      this._login = spec.basic_login;
    } else {
      this._auth_type = 'none';
    }
  }

  DavStorage.prototype._put = function (metadata) {
    return ajax[this._auth_type](
      "PUT",
      "text",
      this._url + '/' + idsToFileName(metadata._id) + "?_=" + Date.now(),
      JSON.stringify(metadata),
      this._login
    );
  };

  DavStorage.prototype._putAttachment = function (param) {
    return ajax[this._auth_type](
      "PUT",
      null,
      this._url + '/' + idsToFileName(param._id, param._attachment) +
        "?_=" + Date.now(),
      param._blob,
      undefined,
      undefined,
      this._login
    );
  };

  DavStorage.prototype._get = function (param) {
    return ajax[this._auth_type](
      "GET",
      "text",
      this._url + '/' + idsToFileName(param._id),
      null,
      undefined,
      undefined,
      this._login
    ).then(function (e) {
      try {
        return {"target": {
          "status": e.target.status,
          "statusText": e.target.statusText,
          "response": JSON.parse(e.target.responseText)
        }};
      } catch (err) {
        throw {"target": {
          "status": 0,
          "statusText": "Parse error"
        }};
      }
    });
  };

  DavStorage.prototype._getAttachment = function (param) {
    return ajax[this._auth_type](
      "GET",
      "blob",
      this._url + '/' + idsToFileName(param._id, param._attachment),
      null,
      param._start,
      param._end - 1,
      this._login
    );
  };

  DavStorage.prototype._remove = function (param) {
    return ajax[this._auth_type](
      "DELETE",
      null,
      this._url + '/' + idsToFileName(param._id) + "?_=" + Date.now(),
      null,
      undefined,
      undefined,
      this._login
    );
  };

  DavStorage.prototype._removeAttachment = function (param) {
    return ajax[this._auth_type](
      "DELETE",
      null,
      this._url + '/' + idsToFileName(param._id, param._attachment) +
        "?_=" + Date.now(),
      null,
      undefined,
      undefined,
      this._login
    );
  };

  DavStorage.prototype._allDocs = function (param) {
    return ajax[this._auth_type](
      "PROPFIND",
      "text",
      this._url + '/',
      null,
      undefined,
      undefined,
      this._login
    ).then(function (e) {
      var i, rows = [], row, responses = new DOMParser().parseFromString(
        e.target.responseText,
        "text/xml"
      ).querySelectorAll(
        "D\\:response, response"
      );
      if (responses.length === 1) {
        return {"target": {"response": {
          "total_rows": 0,
          "rows": []
        }, "status": 200}};
      }
      // exclude parent folder and browse
      for (i = 1; i < responses.length; i += 1) {
        row = {
          "id": "",
          "value": {}
        };
        row.id = responses[i].querySelector("D\\:href, href").
          textContent.split('/').slice(-1)[0];
        row.id = fileNameToIds(row.id);
        if (row.id.length !== 1) {
          row = undefined;
        } else {
          row.id = row.id[0];
        }
        if (row !== undefined) {
          if (row.id !== "") {
            rows[rows.length] = row;
          }
        }
      }
      return {"target": {"response": {
        "total_rows": rows.length,
        "rows": rows
      }, "status": 200}};
    });
  };

  // JIO COMMANDS //

  // wedDav methods rfc4918 (short summary)
  // COPY     Reproduces single resources (files) and collections (directory
  //          trees). Will overwrite files (if specified by request) but will
  //          respond 209 (Conflict) if it would overwrite a tree
  // DELETE   deletes files and directory trees
  // GET      just the vanilla HTTP/1.1 behaviour
  // HEAD     ditto
  // LOCK     locks a resources
  // MKCOL    creates a directory
  // MOVE     Moves (rename or copy) a file or a directory tree. Will
  //          'overwrite' files (if specified by the request) but will respond
  //          209 (Conflict) if it would overwrite a tree.
  // OPTIONS  If WebDAV is enabled and available for the path this reports the
  //          WebDAV extension methods
  // PROPFIND Retrieves the requested file characteristics, DAV lock status
  //          and 'dead' properties for individual files, a directory and its
  //          child files, or a directory tree
  // PROPPATCHset and remove 'dead' meta-data properties
  // PUT      Update or create resource or collections
  // UNLOCK   unlocks a resource

  // Notes: all Ajax requests should be CORS (cross-domain)
  // adding custom headers triggers preflight OPTIONS request!
  // http://remysharp.com/2011/04/21/getting-cors-working/

  DavStorage.prototype.postOrPut = function (method, command, metadata) {
    metadata._id = metadata._id || jIO.util.generateUuid();
    var that = this, o = {
      error_message: "DavStorage, unable to get metadata.",
      notify_message: "Getting metadata",
      percentage: [0, 30],
      notifyProgress: function (e) {
        command.notify({
          "method": method,
          "message": o.notify_message,
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) *
            (o.percentage[1] - o.percentage[0]) +
            o.percentage[0]
        });
      },
      putMetadata: function (e) {
        metadata._attachments = e.target.response._attachments;
        o.notify_message = "Updating metadata";
        o.error_message = "DavStorage, unable to update document.";
        o.percentage = [30, 100];
        that._put(metadata).then(o.success, o.reject, o.notifyProgress);
      },
      errorDocumentExists: function (e) {
        command.error(
          "conflict",
          "Document exists",
          "DavStorage, cannot overwrite document metadata."
        );
      },
      putMetadataIfPossible: function (e) {
        if (e.target.status !== 404) {
          return command.reject(
            e.target.status,
            e.target.statusText,
            o.error_message
          );
        }
        o.percentage = [30, 100];
        o.notify_message = "Updating metadata";
        o.error_message = "DavStorage, unable to create document.";
        that._put(metadata).then(o.success, o.reject, o.notifyProgress);
      },
      success: function (e) {
        command.success(e.target.status, {"id": metadata._id});
      },
      reject: function (e) {
        command.reject(
          e.target.status,
          e.target.statusText,
          o.error_message
        );
      }
    };

    this._get(metadata).then(
      method === 'post' ? o.errorDocumentExists : o.putMetadata,
      o.putMetadataIfPossible,
      o.notifyProgress
    );
  };

  /**
   * Creates a new document if not already exists
   *
   * @method post
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to put
   * @param  {Object} options The command options
   */
  DavStorage.prototype.post = function (command, metadata) {
    this.postOrPut('post', command, metadata);
  };


  /**
   * Creates or updates a document
   *
   * @method put
   * @param  {Object} command The JIO command
   * @param  {Object} metadata The metadata to post
   * @param  {Object} options The command options
   */
  DavStorage.prototype.put = function (command, metadata) {
    this.postOrPut('put', command, metadata);
  };

  /**
   * Add an attachment to a document
   *
   * @method putAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.putAttachment = function (command, param) {
    var that = this, o = {
      error_message: "DavStorage unable to put attachment",
      percentage: [0, 30],
      notify_message: "Getting metadata",
      notifyProgress: function (e) {
        command.notify({
          "method": "putAttachment",
          "message": o.notify_message,
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) *
            (o.percentage[1] - o.percentage[0]) +
            o.percentage[0]
        });
      },
      putAttachmentAndReadBlob: function (e) {
        o.percentage = [30, 70];
        o.notify_message = "Putting attachment";
        o.remote_metadata = e.target.response;
        return RSVP.all([
          that._putAttachment(param),
          jIO.util.readBlobAsBinaryString(param._blob)
        ]).then(null, null, function (e) {
          // propagate only putAttachment progress
          if (e.index === 0) {
            return e.value;
          }
          throw null;
        });
      },
      putMetadata: function (answers) {
        o.percentage = [70, 100];
        o.notify_message = "Updating metadata";
        o.remote_metadata._id = param._id;
        o.remote_metadata._attachments = o.remote_metadata._attachments || {};
        o.remote_metadata._attachments[param._attachment] = {
          "length": param._blob.size,
          "digest": jIO.util.makeBinaryStringDigest(answers[1].target.result),
          "content_type": param._blob.type
        };
        return that._put(o.remote_metadata);
      },
      success: function (e) {
        command.success(e.target.status, {
          "digest": o.remote_metadata._attachments[param._attachment].digest
        });
      },
      reject: function (e) {
        command.reject(
          e.target.status,
          e.target.statusText,
          o.error_message
        );
      }
    };

    this._get(param).
      then(o.putAttachmentAndReadBlob).
      then(o.putMetadata).
      then(o.success, o.reject, o.notifyProgress);
  };

  /**
   * Retrieve metadata
   *
   * @method get
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.get = function (command, param) {
    var o = {
      notifyGetProgress: function (e) {
        command.notify({
          "method": "get",
          "message": "Getting metadata",
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) * 100 // 0% to 100%
        });
      },
      success: function (e) {
        command.success(e.target.status, {"data": e.target.response});
      },
      reject: function (e) {
        command.reject(
          e.target.status,
          e.target.statusText,
          "DavStorage, unable to get document."
        );
      }
    };

    this._get(param).then(o.success, o.reject, o.notifyGetProgress);
  };

  /**
   * Retriev a document attachment
   *
   * @method getAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.getAttachment = function (command, param) {
    var that = this, o = {
      error_message: "DavStorage, unable to get attachment.",
      percentage: [0, 30],
      notify_message: "Getting metedata",
      "404": "missing document", // Not Found
      notifyProgress: function (e) {
        command.notify({
          "method": "getAttachment",
          "message": o.notify_message,
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) *
            (o.percentage[1] - o.percentage[0]) +
            o.percentage[0]
        });
      },
      getAttachment: function (e) {
        var attachment = e.target.response._attachments &&
          e.target.response._attachments[param._attachment];
        delete o["404"];
        if (typeof attachment !== 'object' || attachment === null) {
          throw {"target": {
            "status": 404,
            "statusText": "missing attachment"
          }};
        }
        o.type = attachment.content_type || "application/octet-stream";
        o.notify_message = "Retrieving attachment";
        o.percentage = [30, 100];
        o.digest = attachment.digest;
        return that._getAttachment(param);
      },
      success: function (e) {
        command.success(e.target.status, {
          "data": new Blob([e.target.response], {"type": o.type}),
          "digest": o.digest
        });
      },
      reject: function (e) {
        command.reject(
          e.target.status,
          o[e.target.status] || e.target.statusText,
          o.error_message
        );
      }
    };
    if (param._start < 0 || param._end < 0) {
      command.reject(405,
                     "invalide _start,_end",
                     "_start and _end must be positive");
      return;
    }
    if (param._start > param._end) {
      command.reject(405,
                     "invalide _start,_end",
                     "start is great then end");
      return;
    }
    this._get(param).
      then(o.getAttachment).
      then(o.success, o.reject, o.notifyProgress);
  };

  /**
   * Remove a document
   *
   * @method remove
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.remove = function (command, param) {
    var that = this, o = {
      error_message: "DavStorage, unable to get metadata.",
      notify_message: "Getting metadata",
      percentage: [0, 70],
      notifyProgress: function (e) {
        if (e === null) {
          return;
        }
        command.notify({
          "method": "remove",
          "message": o.notify_message,
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) *
            (o.percentage[1] - o.percentage[0]) + o.percentage[0]
        });
      },
      removeDocument: function (e) {
        o.get_result = e;
        o.percentage = [70, 80];
        o.notify_message = "Removing document";
        o.error_message = "DavStorage, unable to remove document";
        return that._remove(param);
      },
      removeAllAttachments: function (e) {
        var k, requests = [], attachments;
        attachments = o.get_result.target.response._attachments;
        o.remove_result = e;
        if (typeof attachments === 'object' && attachments !== null) {
          for (k in attachments) {
            if (attachments.hasOwnProperty(k)) {
              requests[requests.length] = promiseSucceed(
                that._removeAttachment({
                  "_id": param._id,
                  "_attachment": k
                })
              );
            }
          }
        }
        if (requests.length === 0) {
          return;
        }
        o.count = 0;
        o.nb_requests = requests.length;
        return RSVP.all(requests).then(null, null, function (e) {
          if (e.value.loaded === e.value.total) {
            o.count += 1;
            command.notify({
              "method": "remove",
              "message": "Removing all associated attachments",
              "loaded": o.count,
              "total": o.nb_requests,
              "percentage": Math.min(
                o.count / o.nb_requests * 20 + 80,
                100
              )
            });
          }
          return null;
        });
      },
      success: function () {
        command.success(o.remove_result.target.status);
      },
      reject: function (e) {
        return command.reject(
          e.target.status,
          e.target.statusText,
          o.error_message
        );
      }
    };

    this._get(param).
      then(o.removeDocument).
      then(o.removeAllAttachments).
      then(o.success, o.reject, o.notifyProgress);
  };

  /**
   * Remove an attachment
   *
   * @method removeAttachment
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.removeAttachment = function (command, param) {
    var that = this, o = {
      error_message: "DavStorage, an error occured while getting metadata.",
      percentage: [0, 40],
      notify_message: "Getting metadata",
      notifyProgress: function (e) {
        command.notify({
          "method": "remove",
          "message": o.notify_message,
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) *
            (o.percentage[1] - o.percentage[0]) +
            o.percentage[0]
        });
      },
      updateMetadata: function (e) {
        var k, doc = e.target.response, attachment;
        attachment = doc._attachments && doc._attachments[param._attachment];
        o.error_message = "DavStorage, document attachment not found.";
        if (typeof attachment !== 'object' || attachment === null) {
          throw {"target": {
            "status": 404,
            "statusText": "missing attachment"
          }};
        }
        delete doc._attachments[param._attachment];
        for (k in doc._attachments) {
          if (doc._attachments.hasOwnProperty(k)) {
            break;
          }
        }
        if (k === undefined) {
          delete doc._attachments;
        }
        o.percentage = [40, 80];
        o.notify_message = "Updating metadata";
        o.error_message = "DavStorage, an error occured " +
          "while updating metadata.";
        return that._put(doc);
      },
      removeAttachment: function () {
        o.percentage = [80, 100];
        o.notify_message = "Removing attachment";
        o.error_message = "DavStorage, an error occured " +
          "while removing attachment.";
        return that._removeAttachment(param);
      },
      success: function (e) {
        command.success(e.status);
      },
      reject: function (e) {
        return command.reject(
          e.target.status,
          e.target.statusText,
          o.error_message
        );
      }
    };

    this._get(param).
      then(o.updateMetadata).
      then(o.removeAttachment).
      then(o.success, o.reject, o.notifyProgress);
  };

  /**
   * Retrieve a list of present document
   *
   * @method allDocs
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   * @param  {Boolean} [options.include_docs=false]
   *   Also retrieve the actual document content.
   */
  DavStorage.prototype.allDocs = function (command, param, options) {
    var that = this, o = {
      error_message: "DavStorage, an error occured while " +
        "retrieving document list",
      max_percentage: options.include_docs === true ? 20 : 100,
      notifyAllDocsProgress: function (e) {
        command.notify({
          "method": "remove",
          "message": "Retrieving document list",
          "loaded": e.loaded,
          "total": e.total,
          "percentage": (e.loaded / e.total) * o.max_percentage
        });
      },
      getAllMetadataIfNecessary: function (e) {
        var requests = [];
        o.alldocs_result = e;
        if (options.include_docs !== true ||
            e.target.response.rows.length === 0) {
          return;
        }

        e.target.response.rows.forEach(function (row) {
          if (row.id !== "") {
            requests[requests.length] = that._get({"_id": row.id}).
              then(function (e) {
                row.doc = e.target.response;
              });
          }
        });

        o.count = 0;
        o.nb_requests = requests.length;
        o.error_message = "DavStorage, an error occured while " +
          "getting document metadata";
        return RSVP.all(requests).then(null, null, function (e) {
          if (e.value.loaded === e.value.total) {
            o.count += 1;
            command.notify({
              "method": "allDocs",
              "message": "Getting all documents metadata",
              "loaded": o.count,
              "total": o.nb_requests,
              "percentage": Math.min(
                o.count / o.nb_requests * 80 + 20,
                100
              )
            });
          }
          throw null;
        });
      },
      success: function () {
        command.success(o.alldocs_result.target.status, {
          "data": o.alldocs_result.target.response
        });
      },
      reject: function (e) {
        return command.reject(
          e.target.status,
          e.target.statusText,
          o.error_message
        );
      }
    };

    this._allDocs(param, options).
      then(o.getAllMetadataIfNecessary).
      then(o.success, o.reject, o.notifyProgress);
  };

  /**
   * Check the storage or a specific document
   *
   * @method check
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.check = function (command, param) {
    this.genericRepair(command, param, false);
  };

  /**
   * Repair the storage or a specific document
   *
   * @method repair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Object} options The command options
   */
  DavStorage.prototype.repair = function (command, param) {
    this.genericRepair(command, param, true);
  };

  /**
   * A generic method that manage check or repair command
   *
   * @method genericRepair
   * @param  {Object} command The JIO command
   * @param  {Object} param The command parameters
   * @param  {Boolean} repair If true then repair else just check
   */
  DavStorage.prototype.genericRepair = function (command, param, repair) {

    var that = this, repair_promise;

    // returns a jio object
    function getAllFile() {
      return ajax[that._auth_type](
        "PROPFIND",
        "text",
        that._url + '/',
        null,
        that._login
      ).then(function (e) { // on success
        var i, length, rows = new DOMParser().parseFromString(
          e.target.responseText,
          "text/xml"
        ).querySelectorAll(
          "D\\:response, response"
        );
        if (rows.length === 1) {
          return {"status": 200, "data": []};
        }
        // exclude parent folder and browse
        rows = [].slice.call(rows);
        rows.shift();
        length = rows.length;
        for (i = 0; i < length; i += 1) {
          rows[i] = rows[i].querySelector("D\\:href, href").
            textContent.split('/').slice(-1)[0];
        }
        return {"data": rows, "status": 200};
        // rows -> [
        //   'file_path_1',
        //   ...
        // ]
      }, function (e) { // on error
        // convert into jio error object
        // then propagate
        throw {"status": e.target.status,
               "reason": e.target.statusText};
      });
    }

    // returns jio object
    function repairOne(shared, repair) {
      var modified = false, document_id = shared._id;
      return that._get({"_id": document_id}).then(function (event) {
        var attachment_id, metadata = event.target.response;

        // metadata should be an object
        if (typeof metadata !== 'object' || metadata === null ||
            Array.isArray(metadata)) {
          if (!repair) {
            throw {
              "status": "conflict",
              "reason": "corrupted",
              "message": "Bad metadata found in document \"" +
                document_id + "\""
            };
          }
          return {};
        }

        // check metadata content
        if (!repair) {
          if (!(new jIO.Metadata(metadata).check())) {
            return {
              "status": "conflict",
              "reason": "corrupted",
              "message": "Some metadata might be lost"
            };
          }
        } else {
          modified = (
            jIO.util.uniqueJSONStringify(metadata) !==
              jIO.util.uniqueJSONStringify(
                new jIO.Metadata(metadata).format()._dict
              )
          );
        }

        // check metadata id
        if (metadata._id !== document_id) {
          // metadata id is different than file
          // this is not a critical thing
          modified = true;
          metadata._id = document_id;
        }

        // check attachment metadata container
        if (metadata._attachments &&
            (typeof metadata._attachments !== 'object' ||
             Array.isArray(metadata._attachments))) {
          // is not undefined nor object
          if (!repair) {
            throw {
              "status": "conflict",
              "reason": "corrupted",
              "message": "Bad attachment metadata found in document \"" +
                document_id + "\""
            };
          }
          delete metadata._attachments;
          modified = true;
        }

        // check every attachment metadata
        if (metadata._attachments) {
          for (attachment_id in metadata._attachments) {
            if (metadata._attachments.hasOwnProperty(attachment_id)) {
              // check attachment metadata type
              if (typeof metadata._attachments[attachment_id] !== 'object' ||
                  metadata._attachments[attachment_id] === null ||
                  Array.isArray(metadata._attachments[attachment_id])) {
                // is not object
                if (!repair) {
                  throw {
                    "status": "conflict",
                    "reason": "corrupted",
                    "message": "Bad attachment metadata found in document \"" +
                      document_id + "\", attachment \"" +
                      attachment_id + "\""
                  };
                }
                metadata._attachments[attachment_id] = {};
                modified = true;
              }
              // check attachment existency if all attachment are listed
              if (shared.referenced_dict) {
                if (shared.unreferenced_dict[metadata._id] &&
                    shared.unreferenced_dict[metadata._id][attachment_id]) {
                  // attachment seams to exist but is not referenced
                  shared.referenced_dict[metadata._id] =
                    shared.referenced_dict[metadata._id] || {};
                  shared.referenced_dict[metadata._id][attachment_id] = true;
                  delete shared.unreferenced_dict[metadata._id][attachment_id];
                } else if (
                  !(shared.referenced_dict[metadata._id] &&
                    shared.referenced_dict[metadata._id][attachment_id])
                ) {
                  // attachment doesn't exist, remove attachment id
                  if (!repair) {
                    throw {
                      "status": "conflict",
                      "reason": "attachment missing",
                      "message": "Attachment \"" +
                        attachment_id + "\" from document \"" +
                        document_id + "\" is missing"
                    };
                  }
                  delete metadata._attachments[attachment_id];
                  modified = true;
                }
              }
            }
          }
        }
        return {
          "modified": modified,
          "metadata": metadata
        };
      }, function (event) { // on error
        // convert into jio error object
        // then propagate
        throw {"status": event.target.status,
               "reason": event.target.statustext};
      }).then(function (dict) {
        if (dict.modified) {
          return this._put(dict.metadata);
        }
        return null;
      }).then(function () {
        return "no_content";
      });
    }

    // returns jio object
    function repairAll(shared, repair) {
      return getAllFile().then(function (answer) {
        var index, data = answer.data, length = data.length, id_list,
          document_list = [];
        for (index = 0; index < length; index += 1) {
          // parsing all files
          id_list = fileNameToIds(data[index]);
          if (id_list.length === 1) {
            // this is a document
            document_list[document_list.length] = id_list[0];
          } else if (id_list.length === 2) {
            // this is an attachment
            // reference it
            shared.unreferenced_dict[id_list[0]] =
              shared.unreferenced_dict[id_list[0]] || {};
            shared.unreferenced_dict[id_list[0]][id_list[1]] = true;
          } else {
            shared.unknown_file_list.push(data[index]);
          }
        }
        length = document_list.length;
        for (index = 0; index < length; index += 1) {
          shared._id = document_list[index];
          document_list[index] = repairOne(shared, repair);
        }

        function removeFile(name) {
          return ajax[that._auth_type](
            "DELETE",
            null,
            that._url + '/' + name + "?_=" + Date.now(),
            null,
            that._login
          );
        }

        function errorEventConverter(event) {
          throw {"status": event.target.status,
                 "reason": event.target.statusText};
        }

        length = shared.unknown_file_list.length;
        for (index = 0; index < length; index += 1) {
          document_list.push(
            removeFile(shared.unknown_file_list[index]).
              then(null, errorEventConverter)
          );
        }

        return RSVP.all(document_list);
      }).then(function () {
        return "no_content";
      });
    }

    if (typeof param._id === 'string') {
      repair_promise = repairOne(param, repair);
    } else {
      param.referenced_attachment_path_dict = {};
      param.unreferenced_attachment_path_dict = {};
      param.unknown_file_list = [];
      repair_promise = repairAll(param, repair);
    }

    repair_promise.then(command.success, command.error, command.notify);

  };

  jIO.addStorage('dav', DavStorage);

}));
