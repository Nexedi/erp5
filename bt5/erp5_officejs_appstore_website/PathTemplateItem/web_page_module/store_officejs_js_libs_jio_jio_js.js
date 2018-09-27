(function (dependencies, module) {
  "use strict";
  if (typeof define === 'function' && define.amd) {
    return define(dependencies, module);
  }
  if (typeof exports === 'object') {
    return module(exports, require('rsvp'), require('sha256'));
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
  "Created": "Created",
  "No Content": "No Content",
  "Reset Content": "Reset Content",
  "Partial Content": "Partial Content",
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
  "Created": 201,
  "No Content": 204,
  "Reset Content": 205,
  "Partial Content": 206,
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
  "Created": "success",
  "No Content": "success",
  "Reset Content": "success",
  "Partial Content": "success",
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
 * Clones jsonable object in deep
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
 * which returns a JSON representation of the object. The return value is used
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
      // Date.prototype.toJSON when it is a invalid date. In phantomjs, it
      // returns `"Invalid Date"` but in browsers it returns `null`. In
      // browsers, give `null` as parameter to `new Date()` doesn't return an
      // invalid date.

      // Clonning date with `return new Date(object)` make problems on Firefox.
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
 * Update a dictionnary by adding/replacing key values from another dict.
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
 * A faster version of `array.indexOf(value)` -> `indexOf(value, array)`
 *
 * @param  {Any} value The value to search for
 * @param  {Array} array The array to browse
 * @return {Number} index of value, -1 otherwise
 */
function indexOf(value, array) {
  var i;
  for (i = 0; i < array.length; i += 1) {
    if (array[i] === value) {
      return i;
    }
  }
  return -1;
}
exports.util.indexOf = indexOf;

/**
 * Gets all elements of an array and classifies them in a dict of array.
 * Dict keys are element types, and values are list of element of type 'key'.
 *
 * @param  {Array} array The array of elements to pop
 * @return {Object} The type dict
 */
function arrayValuesToTypeDict(array) {
  var i, type, types = {};
  for (i = 0; i < array.length; i += 1) {
    type = Array.isArray(array[i]) ? 'array' : typeof array[i];
    if (!types[type]) {
      types[type] = [array[i]];
    } else {
      types[type][types[type].length] = array[i];
    }
  }
  return types;
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
 * Returns the number with the lowest value
 *
 * @param  {Number} *values The values to compare
 * @return {Number} The minimum
 */
function min() {
  var i, val;
  for (i = 1; i < arguments.length; i += 1) {
    if (val === undefined || val > arguments[i]) {
      val = arguments[i];
    }
  }
  return val;
}
exports.util.min = min;

/**
 * Returns the number with the greatest value
 *
 * @param  {Number} *values The values to compare
 * @return {Number} The maximum
 */
function max() {
  var i, val;
  for (i = 1; i < arguments.length; i += 1) {
    if (val === undefined || val < arguments[i]) {
      val = arguments[i];
    }
  }
  return val;
}
exports.util.max = max;

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
 * resolve when the status code is lower than 400 with the xhr object as first
 * parameter. xhr.onerror: reject with xhr object as first
 * parameter. xhr.onprogress: notifies the xhr object.
 *
 * @param  {Object} param The parameters
 * @param  {String} [param.type="GET"] The request method
 * @param  {String} [param.dataType=""] The data type to retrieve
 * @param  {String} param.url The url
 * @param  {Any} [param.data] The data to send
 * @param  {Function} [param.beforeSend] A function called just before send
 *   request. The first parameter of this function is the XHR object.
 * @return {Promise} The promise
 */
function ajax(param) {
  var xhr = new XMLHttpRequest();
  return new RSVP.Promise(function (resolve, reject, notify) {
    var k;
    xhr.open(param.type || "GET", param.url, true);
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
  enableJobTimeout(this, shared, options);
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
  var a = args[0], b = args[1], c = args[2], d = args[3], weak, strong;
  weak = {"result": "error"};
  strong = {};
  weak.status = constants.http_status.unknown;
  weak.statusText = constants.http_status_text.unknown;
  weak.message = 'Command failed';
  weak.reason = 'fail';
  weak.method = param.method;
  if (param.kwargs._id) {
    weak.id = param.kwargs._id;
  }
  if (/Attachment$/.test(param.method)) {
    weak.attachment = param.kwargs._attachment;
  }

  if (typeof a !== 'object' || Array.isArray(a)) {
    strong.status = constants.http_status[a];
    strong.statusText = constants.http_status_text[a];
    if (strong.status === undefined ||
        strong.statusText === undefined) {
      return restCommandRejecter(param, [
        // can create infernal loop if 'internal_storage_error' is not defined
        // in the constants
        'internal_storage_error',
        'invalid response',
        'Unknown status "' + a + '"'
      ]);
    }
    a = b;
    b = c;
    c = d;
  }

  if (typeof a !== 'object' || Array.isArray(a)) {
    strong.reason = a;
    a = b;
    b = c;
  }

  if (typeof a !== 'object' || Array.isArray(a)) {
    strong.message = a;
    a = b;
  }

  if (typeof a === 'object' && !Array.isArray(a)) {
    dictUpdate(weak, a);
    if (a instanceof Error) {
      weak.reason = a.message;
      weak.error = a.name;
    }
  }

  dictUpdate(weak, strong);
  strong = undefined;
  if (weak.error === undefined) {
    weak.error = weak.statusText.toLowerCase().replace(/ /g, '_').
      replace(/[^_a-z]/g, '');
  }
  if (typeof weak.message !== 'string') {
    weak.message = "";
  }
  if (typeof weak.reason !== 'string') {
    weak.reason = "unknown";
  }
  return param.solver.reject(deepClone(weak));
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true */
/*global constants, methodType, dictUpdate, Blob, deepClone,
  restCommandRejecter */

function restCommandResolver(param, args) {
  // resolve('ok', {"custom": "value"});
  // resolve(200, {...});
  // resolve({...});
  var a = args[0], b = args[1], weak = {"result": "success"}, strong = {};
  if (param.method === 'post') {
    weak.status = constants.http_status.created;
    weak.statusText = constants.http_status_text.created;
  } else if (methodType(param.method) === "writer" ||
             param.method === "check") {
    weak.status = constants.http_status.no_content;
    weak.statusText = constants.http_status_text.no_content;
  } else {
    weak.status = constants.http_status.ok;
    weak.statusText = constants.http_status_text.ok;
  }
  if (param.kwargs._id) {
    weak.id = param.kwargs._id;
  }
  if (/Attachment$/.test(param.method)) {
    weak.attachment = param.kwargs._attachment;
  }
  weak.method = param.method;

  if (typeof a === 'string' || (typeof a === 'number' && isFinite(a))) {
    strong.status = constants.http_status[a];
    strong.statusText = constants.http_status_text[a];
    if (strong.status === undefined ||
        strong.statusText === undefined) {
      return restCommandRejecter(param, [
        'internal_storage_error',
        'invalid response',
        'Unknown status "' + a + '"'
      ]);
    }
    a = b;
  }
  if (typeof a === 'object' && !Array.isArray(a)) {
    dictUpdate(weak, a);
  }
  dictUpdate(weak, strong);
  strong = undefined; // free memory
  if (param.method === 'post' && (typeof weak.id !== 'string' || !weak.id)) {
    return restCommandRejecter(param, [
      'internal_storage_error',
      'invalid response',
      'New document id have to be specified'
    ]);
  }
  if (param.method === 'getAttachment') {
    if (typeof weak.data === 'string') {
      weak.data = new Blob([weak.data], {
        "type": weak.content_type || weak.mimetype || ""
      });
      delete weak.content_type;
      delete weak.mimetype;
    }
    if (!(weak.data instanceof Blob)) {
      return restCommandRejecter(param, [
        'internal_storage_error',
        'invalid response',
        'getAttachment method needs a Blob as returned "data".'
      ]);
    }
  } else if (methodType(param.method) === 'reader' &&
             param.method !== 'check' &&
             (typeof weak.data !== 'object' ||
              Object.getPrototypeOf(weak.data) !== Object.prototype)) {
    return restCommandRejecter(param, [
      'internal_storage_error',
      'invalid response',
      param.method + ' method needs a dict as returned "data".'
    ]);
  }
  return param.solver.resolve(deepClone(weak));
}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global arrayInsert, indexOf, deepClone, defaults, restCommandRejecter */

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

  var i;

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
    if (indexOf(job_rule.action, shared.job_rule_action_names) === -1) {
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
      for (i = 0; i < options.job_rules.length; i += 1) {
        addJobRule(deepClone(options.job_rules[i]));
      }
    }

    shared.on('job:new', checkJob);

  }

  jio.jobRules = function () {
    return deepClone(shared.job_rules);
  };

}

/*jslint indent: 2, maxlen: 80, sloppy: true, nomen: true, unparam: true */
/*global setTimeout, Job, createStorage, deepClone, min, restCommandResolver,
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
  constants, indexOf, setTimeout, clearTimeout */

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
/*global arrayExtend, setTimeout, methodType, min, constants */

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
        }, min(10000, param.tried * 2000));
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

  ["getAttachment", "removeAttachment"].forEach(function (method) {
    shared.on(method, function (param) {
      if (!checkId(param)) {
        checkAttachmentId(param);
      }
    });
  });

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

}));
