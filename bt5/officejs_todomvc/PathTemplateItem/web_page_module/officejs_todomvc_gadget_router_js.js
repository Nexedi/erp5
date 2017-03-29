/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS*/
(function (window, RSVP, rJS) {
  "use strict";


  /* Functions */

  function getQueryFromHash(hash) {
    switch (hash) {
    case "#/active":
      return 'completed: "false"';
    case "#/completed":
      return 'completed: "true"';
    default:
      return "";
    }
  }

  function loopEventListener(target, type, useCapture, callback,
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
          result = RSVP.reject(e);
        }

        callback_promise = result;
        new RSVP.Queue()
          .push(function () {
            return result;
          })
          .push(undefined, function (error) {
            if (!(error instanceof RSVP.CancellationError)) {
              canceller();
              reject(error);
            }
          });
      };

      target.addEventListener(type, handle_event_callback, useCapture);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  }


  /* Initialization */

  rJS(window)

    .ready(function () {
      var gadget = this;
      return gadget.setQuery(getQueryFromHash(window.location.hash));
    })

    .declareService(function () {
      var gadget = this;
      return loopEventListener(window, "hashchange", false,
        function () {
          return gadget.setQuery(getQueryFromHash(window.location.hash));
        });
    }, false)


    /* Acquisition */

    .declareAcquiredMethod("setQuery", "setQuery");

}(window, RSVP, rJS));