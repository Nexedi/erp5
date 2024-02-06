/*global window, RSVP, FileReader, renderJS */
/*jslint indent: 2, maxerr: 3, unparam: true */
(function (window, RSVP, FileReader, renderJS) {
  "use strict";


  /** Return true if the value truly represents an empty value.

  Calling isEmpty(x) is more robust than expression !x.
  */
  function isEmpty(value) {
    return (value === undefined ||
            value === null ||
            value.length === 0 ||
            (typeof value === "number" && isNaN(value)));
  }
  window.isEmpty = isEmpty;

  /** Make sure that returned object is an Array instance.
  */
  function ensureArray(obj) {
    if (Array.isArray(obj)) {return obj; }
    if (isEmpty(obj)) {return []; }
    return [obj];
  }
  window.ensureArray = ensureArray;

  /** Return first non-empty variable or the last one.

  Calling getFirstNonEmpty(a, b, "") is more robust way of writing a || b || "".
  Variables coercing to false (e.g 0) do not get skipped anymore.
  */
  function getFirstNonEmpty(first_argument) {
    var i;
    if (arguments.length === 0) {
      return null;
    }
    for (i = 0; i < arguments.length; i += 1) {
      if (!isEmpty(arguments[i])) {
        return arguments[i];
      }
    }
    if (arguments.length === 1) {
      return first_argument;
    }
    return arguments[arguments.length - 1];
  }
  window.getFirstNonEmpty = getFirstNonEmpty;

  /** Convert anything to boolean value correctly (even "false" will be false)*/
  function asBoolean(obj) {
    if (typeof obj === "boolean") {
      return obj;
    }
    if (typeof obj === "string") {
      return obj.toLowerCase() === "true" || obj === "1";
    }
    if (typeof obj === "number") {
      return obj !== 0;
    }
    return Boolean(obj);
  }
  window.asBoolean = asBoolean;

  // Compatibility with gadgets not accessing this function from renderJS
  window.loopEventListener = renderJS.loopEventListener;

  window.promiseEventListener = function (target, type, useCapture) {
    //////////////////////////
    // Resolve the promise as soon as the event is triggered
    // eventListener is removed when promise is cancelled/resolved/rejected
    //////////////////////////
    var handle_event_callback;

    function canceller() {
      target.removeEventListener(type, handle_event_callback, useCapture);
    }

    function resolver(resolve) {
      handle_event_callback = function (evt) {
        canceller();
        evt.stopPropagation();
        evt.preventDefault();
        resolve(evt);
        return false;
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(resolver, canceller);
  };

  window.promiseReadAsText = function (file) {
    return new RSVP.Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function (evt) {
        resolve(evt.target.result);
      };
      reader.onerror = function (evt) {
        reject(evt);
      };
      reader.readAsText(file);
    });
  };

  window.promiseDoWhile = function (loopFunction, input) {
    // calls loopFunction(input) until it returns a non positive value

    // this queue is to protect the inner loop queue from the
    // `promiseDoWhile` caller, avoiding it to enqueue the inner
    // loop queue.
    return new RSVP.Queue()
      .push(function () {
        // here is the inner loop queue
        var loop_queue = new RSVP.Queue();
        function iterate(previous_iteration_result) {
          if (!previous_iteration_result) {
            return input;
          }
          loop_queue.push(iterate);
          return loopFunction(input);
        }
        return loop_queue
          .push(function () {
            return loopFunction(input);
          })
          .push(iterate);
      });
  };

}(window, RSVP, FileReader, renderJS));