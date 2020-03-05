/*global window, rJS, RSVP, domsugar, navigator */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, RSVP, domsugar, navigator) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('render', function () {
      var gadget = this;
      // Wait a bit a allow the header loader to be displayed
      return new RSVP.Queue(RSVP.delay(200))
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Test Service Worker',
            page_icon: 'puzzle-piece'
          });
        });
    })
    .declareService(function () {
      var gadget = this,
        has_service_worker = (navigator.serviceWorker.controller !== null);

      domsugar(gadget.element, {
        text: "Has SW: " + has_service_worker.toString()
      });
      return new RSVP.Queue(navigator.serviceWorker.ready)
        .push(function (worker) {
          domsugar(gadget.element, {
            text: "SW: " + worker.toString()
          });
          return gadget.getUrlFor({command: 'change'});
        })
        .push(function (url) {
          domsugar(gadget.element, [
            domsugar('a', {href: url, text: "Check navigation"})
          ]);
        });
    });

}(window, rJS, RSVP, domsugar, navigator));