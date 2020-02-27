/*global window, RSVP, FileReader */
/*jslint indent: 2, maxerr: 3, unparam: true */
(function (window, RSVP, FileReader) {
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

  Calling getNonEmpy(a, b, "") is more robust way of writing a || b || "".
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

  window.loopEventListener = function (target, type, useCapture, callback,
                                       prevent_default) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback,
      callback_promise;

    if (prevent_default === undefined) {
      prevent_default = true;
    }

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        target.removeEventListener(type, handle_event_callback, useCapture);
      }
      cancelResolver();
    }
    function itsANonResolvableTrap(resolve, reject) {
      var result;
      handle_event_callback = function (evt) {
        if (prevent_default) {
          evt.stopPropagation();
          evt.preventDefault();
        }

        cancelResolver();

        try {
          result = callback(evt);
        } catch (e) {
          return reject(e);
        }

        callback_promise = new RSVP.Queue(result).push(undefined, reject);
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  };

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

  /** Internal function to prepare gadget to hold a mutex */
  function ensureLockable(gadget) {
    if (gadget.props === undefined) {
      gadget.props = {};
    }
    // waiting_line is container of mutexes which already blocks some Promise
    if (gadget.props.waiting_line === undefined) {
      gadget.props.waiting_line = [];
    }
  }

  /** Synchronously lock gadget and return previous lock's promise.

  NON-RECURSIVE lock! If you lock inside locked execution you will wait forever.

  If used in a Queue (@see lockGadgetInQueue) it blocks when acquiring the lock.
  */
  window.lockGadget = function (gadget) {
    var ahead_of_me;
    ensureLockable(gadget);
    // step in line
    gadget.props.waiting_line.push(RSVP.defer());

    if (gadget.props.waiting_line.length >= 2) {
      // wait for the promise ahead of me
      ahead_of_me = gadget.props.waiting_line[gadget.props.waiting_line.length - 2].promise;
    } else {
      ahead_of_me = RSVP.resolve();
    }
    // return previous lock's Promise to postpone execution
    return ahead_of_me;
  };

  /** Lock gadget as a step in RSVP.Queue waiting for previous lock to unlock.

  Use in RSVP.Queue to block execution until manually called `unlockGadget`.
  Both lock/unlockGadget pass through any value in RSVP.Queue manner.
  Pass through any value.

  Example:
    new RSVP.Queue()
      .push(function () {return some_value;})
      .push(lockGadgetInQueue(gadget), lockGadgetInFailedQueue(gadget))
      .push(function (some_value) {return someWork(some_value);})
      .push(unlockGadgetInQueue(gadget), unlockGadgetInFailedQueue(gadget));
  */
  window.lockGadgetInQueue = function (gadget) {
    // return function to be used in RSVP.Queue
    return function (pass_through) {
      return new RSVP.Queue()
        .push(function () {
          return window.lockGadget(gadget);
        })
        .push(function () {
          return pass_through;
        });
    };
  };
  /** Lock Gagdet in Queue but intended to be used in "fail" branch (the second function).

  Rethrows any argument.
  */
  window.lockGadgetInFailedQueue = function (gadget) {
    // return function to be used in RSVP.Queue
    return function (error) {
      return new RSVP.Queue()
        .push(function () {
          return window.lockGadget(gadget);
        })
        .push(function () {
          throw error;
        });
    };
  };

  /** Synchronously unlock gadget by resolving props.mutex.promise.

  That promise is most likely blocking some RSVP.Queue or is then-ed on another
  Promise.
  */
  window.unlockGadget = function (gadget) {
    if (gadget.props === undefined ||
        gadget.props.waiting_line === undefined ||
        gadget.props.waiting_line.length === 0) {
      throw new Error("Gadget " + gadget + " is not locked!");
    }
    gadget.props.waiting_line.shift().resolve();
  };

  /** Unlock gadget without blocking as a step in RSVP.Queue.

  Pass through any value. Not re-throwing errors in fail branch!

  For example @see lockGadgetInQueue.
  */
  window.unlockGadgetInQueue = function (gadget) {
    return function (pass_through) {
      window.unlockGadget(gadget);
      return pass_through;
    };
  };

  /** Unlock gadget without blocking and throw any argument received. */
  window.unlockGadgetInFailedQueue = function (gadget) {
    return function (error) {
      window.unlockGadget(gadget);
      throw error;
    };
  };


}(window, RSVP, FileReader));