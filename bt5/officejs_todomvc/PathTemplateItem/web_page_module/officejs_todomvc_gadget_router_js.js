/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80*/
/*global window, RSVP, rJS*/
(function (window, RSVP, rJS, loopEventListener) {
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

}(window, RSVP, rJS, rJS.loopEventListener));