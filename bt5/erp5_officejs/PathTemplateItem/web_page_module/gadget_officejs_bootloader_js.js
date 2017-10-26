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
        manifest: gadget.props.cache_file,
        version: gadget.props.version_url,
        take_installer: true
      }
    });
  }

  rJS(window)
    .setState({error_amount: 0})
    .ready(function (gadget) {
      var i,
        element_list =
          gadget.element.querySelectorAll('[data-install-configuration]');
      gadget.props = {};
      if (window.Bootloader === undefined) {
        window.Bootloader = gadget;
      }

      for (i = 0; i < element_list.length; i += 1) {
        gadget.props[
          element_list[i].getAttribute('data-install-configuration')
        ] = element_list[i].textContent;
      }
      gadget.props.redirect_url = new URL(window.location);
      gadget.props.redirect_url.pathname += gadget.props.version_url;
      // This is a bad hack to support dropbox.
      if (gadget.props.redirect_url.hash &&
          gadget.props.redirect_url.hash.startsWith('#access_token')) {
        gadget.props.redirect_url.hash = gadget.props.redirect_url.hash.replace(
          '#access_token',
          '#/?page=ojs_dropbox_configurator&access_token'
        );
      }
    })

    .allowPublicAcquisition('isChildren', function () {
      return true;
    })
    .declareAcquiredMethod('isChildren', 'isChildren')
    .declareAcquiredMethod('renderError', 'renderError')

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
                  return gadget.changeState({main: true});
                }),
              gadget.install()
                .push(function () {
                  window.location = gadget.props.redirect_url;
                })
            ]);
          }
          throw error;
        });
    })

    .allowPublicAcquisition('renderError', function (param_list) {
      param_list[0].error_amount = this.state.error_amount + 1;
      return this.changeState(param_list[0]);
    })

    .declareMethod('render', function (options) {
      return this.getDeclaredGadget('view_gadget')
        .push(function (view_gadget) {
          return view_gadget.render(options);
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this, element, options;
      if (modification_dict.main) {
        element = document.createElement("div");
        element.className = "presentation";
        gadget.element.insertBefore(element, gadget.element.firstChild);
        return gadget.declareGadget(
          "gadget_officejs_bootloader_presentation.html",
          {"scope": "view_gadget", "element": element}
        )
          .push(function (view_gadget) {
            return view_gadget.render({
              app_name: gadget.props.app_name,
              redirect_url: gadget.state.redirect_url
            });
          });
      }
      if (modification_dict.error) {
        options = {
          error: gadget.state.error,
          error_amount: gadget.state.error_amount
        };
        if (modification_dict.error_source) {
          options.error_source = gadget.state.error_source;
        }
        if (gadget.state.main) {
          return gadget.render(options);
        }
        options.error_source = gadget.state.app_name;
        return gadget.renderError(options);
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
              error_amount: gadget.state.error_amount + 1,
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