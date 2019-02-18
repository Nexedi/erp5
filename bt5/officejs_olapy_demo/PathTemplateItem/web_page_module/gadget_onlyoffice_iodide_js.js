/*jslint indent: 2, unparam: true*/
/*global rJS, window, RSVP, jIO, Promise, console, DOMParser */
(function (rJS, window, RSVP, jIO, Promise) {
  "use strict";

  var SW = "gadget_onlyoffice_iodide_sw.js";

  function makeRequestOnIodide(gadget, xml) {

    return gadget.getDeclaredGadget('iodide')
      .push(function (iodide) {

        return iodide.evalCode(
          'callFunction(' +
            JSON.stringify({
              fun: "requestOlapy",
              argument_list: [xml]
            }) +
            ')'
        );
      })
      .push(function (result) {
        // console.log('eval result', result);
        return result;
      }, function (error) {
        console.warn('eval error', error);
        throw error;
      });
  }

  function waitForServiceWorkerActive(gadget, registration) {
    var serviceWorker;
    if (registration.installing) {
      serviceWorker = registration.installing;
    } else if (registration.waiting) {
      serviceWorker = registration.waiting;
    } else if (registration.active) {
      serviceWorker = registration.active;
    }
    if (serviceWorker.state !== "activated") {
      return RSVP.Promise(function (resolve, reject) {
        serviceWorker.addEventListener('statechange', function (e) {
          if (e.target.state === "activated") {
            resolve();
          }
        });
        RSVP.delay(500).then(function () {
          reject(new Error("Timeout service worker install"));
        });
      });
    }
  }

  rJS(window)
    .ready(function (gadget) {
      return new RSVP.Queue()
        .push(function () {
          return window.navigator.serviceWorker.register(SW);
        })
        .push(function (registration) {
          window.navigator.serviceWorker.addEventListener('message', function (event) {
            return makeRequestOnIodide(gadget, event.data)
              .push(function (result) {
                event.ports[0].postMessage(result);
              }, function (error) {
                event.ports[0].postMessage(error);
              });
          });
          return waitForServiceWorkerActive(gadget, registration);
        });
    })
    .allowPublicAcquisition('notifyChange', function (options) {
      window.console.warn(options);
    })
    .allowPublicAcquisition('notifyInvalid', function (options) {
      window.console.error(options);
    })
    .allowPublicAcquisition('notifyValid', function (options) {
      window.console.log(options);
    })
    .allowPublicAcquisition('submitContent', function () {
      window.console.warn(arguments);
    })
    .allowPublicAcquisition('getSetting', function (param) {
      if (param[0] === 'portal_type') {
        return 'Spreadsheet';
      }
      throw new Error("get Setting undefined for : " + param[0]);
    })
    .ready(function (gadget) {
      return gadget.render();
    })
    .declareMethod("render", function () {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getDeclaredGadget('iodide'),
            jIO.util.ajax({
              url: "olapy_notebook.jsmd"
            }),
            gadget.getDeclaredGadget('onlyoffice')
          ]);
        })
        .push(function (result) {
          return result[0].render({
            key: 'script',
            value: result[1].target.response
          })
            .push(function () {
              var storage = jIO.createJIO({
                type: "erp5",
                url: "https://softinst114089.host.vifib.net/erp5/web_site_module/hateoas/",
                default_view_reference: "jio_view_attachment"
              });
              return storage.getAttachment(
                'document_module/onlyoffice_iodide_test_2_xlsy',
                'https://softinst114089.host.vifib.net/erp5/web_site_module/hateoas/document_module/onlyoffice_iodide_test_2_xlsy/Document_downloadForOnlyOfficeApp'
              );
            })
            .push(function (blob) {
              return jIO.util.readBlobAsDataURL(blob);
            })
            .push(function (event) {
              return result[2].render({
                key: 'content',
                value: event.target.result
              });
            });
        });
    });

}(rJS, window, RSVP, jIO, Promise));
