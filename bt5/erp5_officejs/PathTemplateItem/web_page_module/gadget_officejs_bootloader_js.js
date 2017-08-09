/*globals window, document, RSVP, rJS, navigator, jIO, URL*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO, navigator, URL) {
  "use strict";

  function createStorage(gadget) {
    return jIO.createJIO({
      type: "replicate",
      parallel_operation_attachment_amount: 10,
      parallel_operation_amount: 1,
      conflict_handling: 2,
      signature_hash_key: 'hash',
      check_remote_attachment_modification: true,
      check_remote_attachment_creation: true,
      check_remote_attachment_deletion: false,
      check_remote_deletion: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_local_modification: false,
      signature_sub_storage: {
        type: "query",
        sub_storage: {
          type: "indexeddb",
          database: "officejs-hash"
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
        element_list =
          gadget.element.querySelectorAll('[data-install-configuration]');
      window.Bootloader = gadget;

      for (i = 0; i < element_list.length; i += 1) {
        state[element_list[i].getAttribute('data-install-configuration')] =
          element_list[i].textContent;
      }
      state.redirect_url = new URL(window.location);
      state.redirect_url.pathname += state.version_url;
      // This is a bad hack to support dropbox.
      if (state.redirect_url.hash &&
          state.redirect_url.hash.startsWith('#access_token')) {
        state.redirect_url.hash = state.redirect_url.hash.replace(
          '#access_token',
          '#/?page=ojs_dropbox_configurator&access_token'
        );
      }
      return gadget.changeState(state);
    })

    .allowPublicAcquisition('isChildren', function () {
      return true;
    })
    .declareAcquiredMethod('isChildren', 'isChildren')

    .declareService(function () {
      var gadget = this;
      return gadget.isChildren()
        .push(undefined, function (error) {
          if (error instanceof rJS.AcquisitionError) {
            return RSVP.all([
              new RSVP.Queue()
                .push(function () {
                  return RSVP.delay(600);
                })
                .push(function () {
                  return gadget.changeState({retry: 0});
                }),
              gadget.install()
                .push(function () {
                  window.location = gadget.state.redirect_url;
                })
            ]);
          }
          throw error;
        });
    })

    .onStateChange(function () {
      var gadget = this, element;
      if (gadget.state.retry !== undefined) {
        return new RSVP.Queue()
          .push(function () {
            if (gadget.state.retry === 0) {
              element = document.createElement("div");
              element.className = "presentation";
              gadget.element.insertBefore(element, gadget.element.firstChild);
              return gadget.declareGadget(
                "gadget_officejs_bootloader_presentation.html",
                {"scope": "view_gadget", "element": element}
              );
            }
            return gadget.getDeclaredGadget('view_gadget');
          })
          .push(function (view_gadget) {
            return view_gadget.render({
              app_name: gadget.state.app_name,
              retry: gadget.state.retry,
              error: gadget.state.error,
              redirect_url: gadget.state.redirect_url
            });
          });
      }
    })

    .declareMethod('declareAndInstall', function (url) {
      var element = document.createElement("div");
      element.setAttribute("style", "display: none");
      this.element.appendChild(element);
      return this.declareGadget(url,
        {
          "element": element,
          "scope": url,
          "sandbox": "iframe"
        })
        .push(function (sub_gadget) {
          return sub_gadget.install();
        });
    })

    .declareMethod("install", function () {
      var gadget = this,
        storage = createStorage(gadget);
      if (navigator.serviceWorker !== undefined) {
        return storage.repair()
          .push(undefined, function (error) {
            return gadget.changeState({
              retry: gadget.state.retry !== undefined ?
                  gadget.state.retry + 1 : 0,
              error: error
            })
              .push(function () {
                return RSVP.delay(1000);
              })
              .push(function () {
                return gadget.install();
              });
          })
          .push(function () {
            return navigator.serviceWorker.register(
              "gadget_officejs_bootloader_serviceworker.js"
            );
          });
      }
      return;
    });

}(window, document, RSVP, rJS, jIO, navigator, URL));