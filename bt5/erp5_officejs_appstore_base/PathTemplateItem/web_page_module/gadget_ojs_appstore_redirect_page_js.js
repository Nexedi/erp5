/*globals window, document, RSVP, rJS, navigator*/
/*jslint indent: 2, maxlen: 80, nomen: true*/

(function (window, document, RSVP, rJS, navigator) {
  "use strict";

  rJS(window)
    .declareService(function () {
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
        .push(function () {
          document.location.replace(latest_version + "/" +
                                    document.location.hash);
        });
    });

}(window, document, RSVP, rJS, navigator));