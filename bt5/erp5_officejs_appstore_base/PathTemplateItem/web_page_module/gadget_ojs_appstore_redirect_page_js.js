/*globals window, document, RSVP, rJS, navigator*/
/*jslint indent: 2, maxlen: 80, nomen: true*/

(function (window, document, RSVP, rJS, navigator) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      var latest_version = document.head.querySelector(
        'script[app-configuration="latest_version"]'
      ).textContent,
        queue = new RSVP.Queue();
      return queue
        .push(function () {
          return navigator.serviceWorker.register(
            "gadget_officejs_root_serviceworker.js");
        })
        .push(function (registration) {
          function redirect_version() {
            document.location.replace(latest_version + "/" +
                                      document.location.hash);
          }
          var timeout_duration = 10000;
          try {
            window.applicationCache.addEventListener('cached', redirect_version);
            window.applicationCache.addEventListener('noupdate', redirect_version);
            window.applicationCache.addEventListener('error', redirect_version);
            window.applicationCache.addEventListener('updateready', function () {window.location.reload(); });
          } catch (e) {
            timeout_duration = 1;
          }
          window.setTimeout(redirect_version, 1);
        });
    });

}(window, document, RSVP, rJS, navigator));