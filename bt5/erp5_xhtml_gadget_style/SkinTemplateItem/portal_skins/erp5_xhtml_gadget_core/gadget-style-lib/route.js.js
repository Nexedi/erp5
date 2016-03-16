/*global window, jQuery */
/*!
 * route.js v1.0.0
 *
 * Copyright 2012, Romain Courteaud
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * Date: Mon Jul 16 2012
 */
"use strict";
(function (window, $) {

  $.extend({
    StatelessDeferred: function () {
      var doneList = $.Callbacks("memory"),
        promise = {
          done: doneList.add,

          // Get a promise for this deferred
          // If obj is provided, the promise aspect is added to the object
          promise: function (obj) {
            var i,
              keys = ['done', 'promise'];
            if (obj === undefined) {
              obj = promise;
            } else {
              for (i = 0; i < keys.length; i += 1) {
                obj[keys[i]] = promise[keys[i]];
              }
            }
            return obj;
          }
        },
        deferred = promise.promise({});

      deferred.resolveWith = doneList.fireWith;

      // All done!
      return deferred;
    }
  });

  var routes = [],
    current_priority = 0,
    methods = {
      add: function (pattern, priority) {
        var i = 0,
          inserted = false,
          length = routes.length,
          dfr = $.StatelessDeferred(),
          context = $(this),
          escapepattern,
          matchingpattern;

        if (priority === undefined) {
          priority = 0;
        }
        if (pattern !== undefined) {

          // http://simonwillison.net/2006/Jan/20/escape/
          escapepattern = pattern.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$&");
          matchingpattern = escapepattern
                              .replace(/<int:\w+>/g, "(\\d+)")
                              .replace(/<path:\w+>/g, "(.+)")
                              .replace(/<\w+>/g, "([^/]+)");

          while (!inserted) {
            if ((i === length) || (priority >= routes[i][2])) {
              routes.splice(i, 0, [new RegExp('^' + matchingpattern + '$'), dfr, priority, context]);
              inserted = true;
            } else {
              i += 1;
            }
          }
        }
        return dfr.promise();
      },
      go: function (path, min_priority) {
        var dfr = $.Deferred(),
          context = $(this),
          result;

        if (min_priority === undefined) {
          min_priority = 0;
        }
        setTimeout(function () {
          var i = 0,
            found = false,
            slice_index = -1,
            slice_priority = -1;
          for (i = 0; i < routes.length; i += 1) {
            if (slice_priority !== routes[i][2]) {
              slice_priority = routes[i][2];
              slice_index = i;
            }
            if (routes[i][2] < min_priority) {
              break;
            } else if (routes[i][0].test(path)) {
              result = routes[i][0].exec(path);
              dfr = routes[i][1];
              context = routes[i][3];
              current_priority = routes[i][2];
              found = true;
              break;
            }
          }
          if (i === routes.length) {
            slice_index = i;
          }
          if (slice_index > -1) {
            routes = routes.slice(slice_index);
          }
          if (found) {
            dfr.resolveWith(
              context,
              result.slice(1)
            );
          } else {
            dfr.rejectWith(context);
          }
        });
        return dfr.promise();
      },
    };


  $.routereset = function () {
    routes = [];
    current_priority = 0;
  };

  $.routepriority = function () {
    return current_priority;
  };

  $.fn.route = function (method) {
    var result;
    if (methods.hasOwnProperty(method)) {
      result = methods[method].apply(
        this,
        Array.prototype.slice.call(arguments, 1)
      );
    } else {
      $.error('Method ' + method +
              ' does not exist on jQuery.route');
    }
    return result;
  };

}(window, jQuery));
