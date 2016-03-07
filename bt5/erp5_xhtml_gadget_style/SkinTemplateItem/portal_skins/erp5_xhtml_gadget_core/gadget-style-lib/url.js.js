/*!
 * url.js v1.0.0
 *
 * Copyright 2012, Romain Courteaud
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Date: Mon Jul 16 2012
 */
"use strict";
(function (window, $) {

  var hashchangeinitialized = false,
    previousurl,
    currentcallback,
    getRawHash = function () {
      return window.location.toString().split('#')[1];
    },
    callbackwrapper = function () {
      if (previousurl !== window.location.hash) {
        previousurl = window.location.hash;
        if (currentcallback !== undefined) {
          currentcallback();
        }
      }
    },
    timeoutwrapper = function () {
      callbackwrapper();
      window.setTimeout(timeoutwrapper, 500);
    };

  function UrlHandler() {}

  UrlHandler.prototype = {
    'generateUrl': function (path, options) {
      var pathhash,
        hash = '#',
        key;
      if (path !== undefined) {
        hash += encodeURIComponent(path);
      }
      hash = hash.replace(/%2F/g, '/');
      pathhash = hash;
      for (key in options) {
        if (options.hasOwnProperty(key)) {
          if (hash === pathhash) {
            hash = hash + '?';
          } else {
            hash = hash + '&';
          }
          hash += encodeURIComponent(key) +
            '=' + encodeURIComponent(options[key]);
        }
      }
      return hash;
    },

    'go': function (path, options) {
      window.location.hash = this.generateUrl(path, options);
    },

    'redirect': function (path, options) {
      var host = window.location.protocol + '//' +
                 window.location.host +
                 window.location.pathname +
                 window.location.search;
      window.location.replace(host + this.generateUrl(path, options));
//       window.location.replace(window.location.href.replace(/#.*/, ""));
    },

    'getPath': function () {
      var hash = getRawHash(),
        result = '';
      if (hash !== undefined) {
        result = decodeURIComponent(hash.split('?')[0]);
      }
      return result;
    },

    'getOptions': function () {
      var options = {},
        hash = getRawHash(),
        subhashes,
        subhash,
        index,
        keyvalue;
      if (hash !== undefined) {
        hash = hash.split('?')[1];
        if (hash !== undefined) {
          subhashes = hash.split('&');
          for (index in subhashes) {
            if (subhashes.hasOwnProperty(index)) {
              subhash = subhashes[index];
              if (subhash !== '') {
                keyvalue = subhash.split('=');
                if (keyvalue.length === 2) {
                  options[decodeURIComponent(keyvalue[0])] =
                    decodeURIComponent(keyvalue[1]);
                }
              }
            }
          }
        }
      }
      return options;
    },

    'onhashchange': function (callback) {
      previousurl = undefined;
      currentcallback = callback;

      if (!hashchangeinitialized) {
        if (window.onhashchange !== undefined) {
          $(window).bind('hashchange', callbackwrapper);
          window.setTimeout(callbackwrapper);
        } else {
          timeoutwrapper();
        }
        hashchangeinitialized = true;
      }
    },
  };

  // Expose to the global object
  $.url = new UrlHandler();

}(window, jQuery));
