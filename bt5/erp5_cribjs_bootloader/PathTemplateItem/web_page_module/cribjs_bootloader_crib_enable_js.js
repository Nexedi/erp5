/*global window, rJS, jIO, FormData, navigator, RSVP */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  function waitForServiceWorkerActive(registration) {
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
      // Initialize the gadget local parameters
      var path = "", path_list = window.location.pathname.split("/");
      if (path_list) {
        if (path_list[path_list.length - 1] !== "") {
          if (path_list[path_list.length - 1].endsWith(".html")) {
            path_list[path_list.length - 1] = "";
          } else {
            path_list.push("");
          }
        }
        path = path_list.join("/");
      }
      gadget.state_parameter_dict = {};
      gadget.state_parameter_dict.default_document = window.location.protocol +
        "//" + window.location.host + path;
      this.state_parameter_dict.jio_storage = jIO.createJIO({
        "type": "indexeddb",
        "database": "ojs_source_code"
      });
      return this.state_parameter_dict.jio_storage.put(gadget.state_parameter_dict.default_document, {});
    })
    .ready(function (gadget) {
      var jio_storage;
      return RSVP.Queue()
        .push(function () {
          jio_storage = jIO.createJIO({
            type: "indexeddb",
            database: "setting"
          });
          return jio_storage.get("setting");
        })
        .push(function (result) {
          if (result.site_editor_gadget_url) {
            return;
          }
          result.site_editor_gadget_url = window.location.href;
          return jio_storage.put("setting", result);
        }, function (error) {
          if (error.status_code === 404) {
            return jio_storage.put(
              "setting", {
                site_editor_gadget_url: window.location.href
              });
          }
        });
    })
    .ready(function () {
      if ('serviceWorker' in navigator) {
        // XXX Hack to not add a new service worker when one is already declared
        if (!navigator.serviceWorker.controller) {
          return new RSVP.Queue()
            .push(function () {
              return navigator.serviceWorker.register(
                'gadget_cribjs_bootloader_serviceworker.js',
                {scope: './'}
              );
            })
            .push(function (registration) {
              return waitForServiceWorkerActive(registration);
            });
        }
      } else {
        throw "Service Worker are not available in your browser";
      }
    })

    .declareMethod('get', function (url) {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.getAttachment(this.state_parameter_dict.default_document, url)
        .push(function (result) {
          return jIO.util.readBlobAsDataURL(result);
        })
        .push(function (e) {
          return e.target.result;
        });
    })
    .declareMethod('put', function (url, data_uri) {
      var storage = this.state_parameter_dict.jio_storage;
      data_uri = jIO.util.dataURItoBlob(data_uri);
      return storage.putAttachment(
        this.state_parameter_dict.default_document,
        url,
        data_uri
      );
    })
    .declareMethod('allDocs', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allAttachments(this.state_parameter_dict.default_document)
        .push(function (result) {
          return result;
        });
    })
    .declareMethod('remove', function (url) {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.removeAttachment(
        this.state_parameter_dict.default_document,
        url
      );
    });

}(window, rJS, jIO));