/*globals window, document, RSVP, rJS, navigator, jIO, console*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO, navigator, console) {
  "use strict";

  function createStorage(gadget) {
    return jIO.createJIO({
      type: "replicate",
      parallel_operation_attachment_amount: 10,
      signature_hash_key: 'hash',
      check_remote_attachment_modification: true,
      check_remote_attachment_creation: true,
      check_remote_attachment_deletion: true,
      check_remote_deletion: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_local_modification: false,
      signature_sub_storage: {
        type: "query",
        sub_storage: {
          type: "indexeddb",
          database: "ojs_source_hash"
        }
      },
      local_sub_storage: {
        type: "query",
        sub_storage: {
          type: "uuid",
          sub_storage: {
            type: "indexeddb",
            database: "ojs_source_code"
          }
        }
      },
      remote_sub_storage: {
        type: "appcache",
        manifest: gadget.state.cache_file,
        version: gadget.state.version_url
      }
    });
  }

  rJS(window)
    .ready(function (gadget) {
      var i,
        state = {},
        sub_gadget_list = [],
        element_list =
        gadget.element.querySelectorAll('[data-install-configuration]');
      window.Bootloader = gadget;

      for (i = 0; i < element_list.length; i += 1) {
        state[element_list[i].getAttribute('data-install-configuration')] =
          element_list[i].textContent;
      }
      return gadget.changeState(state);
    })

/*    .allowPublicAcquisition('isChildren', function () {
      return true;
    })
    .declareAcquiredMethod('isChildren', 'isChildren')*/

    .declareMethod('isChildren', function () {
      // XXX to change in future
      return window.self !== window.top;
    })

    .declareService(function () {
      var gadget = this;
      return gadget.isChildren()
        .push(function (isChildren) {
          if (!isChildren) {
            console.warn("Not children ", gadget.state.app_name);
            return RSVP.all([
              new RSVP.Queue()
                .push(function () {
                  return RSVP.delay(400);
                })
                .push(function () {
                  return gadget.render();
                }),
              gadget.install()
                .push(function () {
                  window.location.pathname += gadget.state.version_url;
                })
            ]);
          } else {
            console.warn("isChildren ", gadget.state.app_name);
          }
        });
    })

    .declareMethod("render", function () {
      var gadget = this,
        element = document.createElement("div");
      element.className = "presentation";
      gadget.element.insertBefore(element, gadget.element.firstChild);
      return gadget.declareGadget(
        "gadget_officejs_bootloader_presentation.html",
        {"scope": "presentation", "element": element}
      )
        .push(function (presentation_gadget) {
          return presentation_gadget.render(
            {"app_name": gadget.state.app_name}
          );
        });
    })
    .declareMethod('declareAndInstall', function (url) {
      var element = document.createElement("div");
      element.setAttribute("style", "display: none");
      this.element.appendChild(element);
      return this.declareGadget(url,
        {
          "element": element,
          "sandbox": "iframe"
        })
        .push(function (sub_gadget) {
          console.warn("After declare ", url);
          return sub_gadget.install();
        });
    })

    .declareMethod("install", function () {
      var gadget = this,
        storage = createStorage(gadget);
      return new RSVP.Queue()
        .push(function () {
          return navigator.serviceWorker.register(
            "gadget_officejs_bootloader_serviceworker.js",
            {"scope": gadget.state.version_url}
          );
        })
        .push(function () {
          return storage.repair();
        });
    });

}(window, document, RSVP, rJS, jIO, navigator, console));