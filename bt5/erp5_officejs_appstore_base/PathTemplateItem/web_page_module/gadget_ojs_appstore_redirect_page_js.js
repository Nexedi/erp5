/*globals window, document, RSVP, rJS, navigator*/
/*jslint indent: 2, maxlen: 80, nomen: true*/

(function (window, document, RSVP, rJS, navigator) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      var latest_version = document.head.querySelector(
        'script[data-appconfig="latest_version"]'
      ).textContent,
        queue = new RSVP.Queue();
      // Make this redirection compatible with no-service-worker browsers
      if ('serviceWorker' in navigator) {
        queue.push(function () {
          return navigator.serviceWorker.register(
            "gadget_erp5_serviceworker.js");
        });
      }
      return queue
        .push(function (registration) {
          // XXX This is a hack for when the network is too slow
          return RSVP.delay(1);
        })
        .push(function () {
          document.location.replace(latest_version + "/" +
                                    document.location.hash);
        });
    });

}(window, document, RSVP, rJS, navigator));