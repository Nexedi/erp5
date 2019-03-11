/*globals window, document, RSVP, rJS, navigator, jIO, URL*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO, navigator, URL) {
  "use strict";

  function createStorage(gadget) {
    var jio_options = {
      type: "replicate",
      parallel_operation_attachment_amount: 10,
      parallel_operation_amount: 1,
      conflict_handling: 2,
      signature_hash_key: 'hash',
      check_remote_attachment_modification: true,
      check_remote_attachment_creation: true,
      check_remote_attachment_deletion: true,
      check_remote_deletion: true,
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
        manifest: gadget.props.cache_file,
        version: gadget.props.version_url,
        take_installer: true
      }
    }
    return jIO.createJIO(jio_options);
  }

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
    .setState({error_amount: 0})
    .ready(function (gadget) {
      var i,
        element_list =
          gadget.element.querySelectorAll('[data-install-configuration]');

      gadget.props = {};
      for (i = 0; i < element_list.length; i += 1) {
        gadget.props[element_list[i].getAttribute(
          'data-install-configuration'
        )] = element_list[i].textContent;
      }
      gadget.props.redirect_url = new URL(window.location);
      gadget.props.redirect_url.pathname += gadget.props.version_url;
      if (gadget.props.redirect_url.hash) {
        if (gadget.props.redirect_url.hash.startsWith('#access_token')) {
          // This is a bad hack to support dropbox.
          gadget.props.redirect_url.hash =
            gadget.props.redirect_url.hash.replace(
            '#access_token',
            '#/?page=ojs_dropbox_configurator&access_token'
          );
        } else if (gadget.props.redirect_url.hash
            .startsWith('#page=settings_configurator')) {
          // Make monitoring app still compatible with old instances setup URLs
          gadget.props.redirect_url.hash =
            gadget.props.redirect_url.hash.replace(
            '#page=settings_configurator',
            '#/?page=settings_configurator'
          );
        }
      }
    })

    .declareService(function () {
      var gadget = this;
      return RSVP.all([
        new RSVP.Queue()
          .push(function () {
            return RSVP.delay(600);
          })
          .push(function () {
            return gadget.changeState({
              app_name: gadget.props.app_name,
              redirect_url: gadget.props.redirect_url
            });
          }),
        gadget.install()
          .push(function () {
            window.location.replace(gadget.props.redirect_url);
          })
      ]);
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          var element = gadget.element.querySelector('.presentation');
          if (element) {
            return gadget.getDeclaredGadget('view');
          }
          element = document.createElement("div");
          element.className = "presentation";
          gadget.element.appendChild(element);
          return gadget.declareGadget(
            "gadget_officejs_bootloader_presentation.html",
            {"scope": "view", "element": element}
          );
        })
        .push(function (view_gadget) {
          return view_gadget.render(options);
        });
    })

    .onStateChange(function (modification_dict) {
      return this.render(modification_dict);
    })

    .declareMethod("install", function () {
      var gadget = this,
        storage = createStorage(gadget);
      if (navigator.serviceWorker !== undefined) {
        return storage.repair()
          .push(function () {
            return navigator.serviceWorker.register(
              "gadget_officejs_bootloader_serviceworker.js"
            );
          })
          .push(function (registration) {
            return waitForServiceWorkerActive(registration);
          })
          .push(undefined, function (error) {
            return gadget.changeState({
              error_amount: gadget.state.error_amount + 1,
              error: error
            })
              .push(function () {
                return RSVP.delay(1000);
              })
              .push(function () {
                return gadget.install();
              });
          });
      }
      return;
    });

}(window, document, RSVP, rJS, jIO, navigator, URL));