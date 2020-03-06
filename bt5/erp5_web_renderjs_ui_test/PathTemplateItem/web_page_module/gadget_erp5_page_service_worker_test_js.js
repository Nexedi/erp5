/*global window, rJS, RSVP, domsugar, navigator, promiseEventListener, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, RSVP, domsugar, navigator, promiseEventListener, jIO) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("getUrlForList", "getUrlForList")

    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('render', function () {
      var gadget = this;
      // Wait a bit a allow the header loader to be displayed
      return new RSVP.Queue(RSVP.delay(200))
        .push(function () {
          return gadget.getUrlForList([
            // Home page
            {command: 'display'},
            // Soft reload the gadget
            {command: 'change'}
          ]);
        })
        .push(function (url_list) {
          gadget.checkServiceWorkerStatus();
          return gadget.updateHeader({
            page_title: 'Test Service Worker',
            front_url: url_list[0],
            tab_url: url_list[1],
            submit_action: true
          });
        });
    })

    .declareMethod("triggerSubmit", function () {
      var gadget = this;
      return new RSVP.Queue(jIO.util.ajax({
        type: 'POST',
        url: './Base_changeModificationDateForTest'
      }))
        .push(function () {
          domsugar(gadget.element, {
            text: "SW changed on server"
          });
        });
    })

    .declareJob("checkServiceWorkerStatus", function () {
      var gadget = this,
        has_service_worker = (navigator.serviceWorker.controller !== null);

      domsugar(gadget.element, {
        text: "Has SW: " + has_service_worker.toString()
      });
      return new RSVP.Queue(navigator.serviceWorker.ready)
        .push(function (worker_container) {
          domsugar(gadget.element, {
            text: "Has SW: true"
          });
          return promiseEventListener(worker_container.active, 'statechange');
        })
        .push(function () {
          // Wait a bit until the message is propagated
          return RSVP.delay(2000);
        })
        .push(function () {
          domsugar(gadget.element, {
            text: "New SW ready"
          });
        });
    });

}(window, rJS, RSVP, domsugar, navigator, promiseEventListener, jIO));