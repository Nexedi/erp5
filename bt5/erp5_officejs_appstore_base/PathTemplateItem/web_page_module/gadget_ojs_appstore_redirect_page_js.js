/*globals window, document, RSVP, rJS, jIO, navigator, URL, console*/
/*jslint indent: 2, maxlen: 80, nomen: true*/

(function (window, document, RSVP, rJS, jIO, navigator, URL) {
  "use strict";
  rJS(window)
    .ready(function (gadget) {
      function redirect_version() {
        //document.location.replace("${latest_version}/" + document.location.hash);
        //XXX HARDOCDED - how to get ${latest_version} from here?
        document.location.replace("23bf8c1dc2/" + document.location.hash);
      };
      var queue = new RSVP.Queue();
      return queue
        .push(function () {
          return navigator.serviceWorker.register(
            "gadget_officejs_root_serviceworker.js"
          );
        })
        .push(function (registration) {
          console.log('(OJS Redirect) ROOT SW REGISTERED with scope: ', registration.scope);
          window.setTimeout(redirect_version, 1);
        })
    });

}(window, document, RSVP, rJS, jIO, navigator, URL));