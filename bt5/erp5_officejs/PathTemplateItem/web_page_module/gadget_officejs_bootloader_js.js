/*globals window, document, RSVP, rJS, navigator, jIO, MessageChannel, ProgressEvent, console*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO, navigator, MessageChannel,
  ProgressEvent, console) {
  "use strict";

  var serviceWorker_setting_storage = jIO.createJIO({
    type: "uuid",
    sub_storage: {
      type: "indexeddb",
      database: "serviceWorker_settings"
    }
  }), remote_storage = {
    type: "erp5",
    url: window.location.origin +
      window.location.pathname + "hateoasnoauth",
    default_view_reference: "jio_view"
  };

  function createStorage(query, version_url, version) {
    return jIO.createJIO({
      type: "replicate",
      conflict_handling: 2,
      check_remote_modification: true, // put false for prod
      check_remote_deletion: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_local_modification: false,
      query: {
        query: 'portal_type: ("Web Illustration",' +
          '"Web Manifest","Web Script","Web Style","Web Page") AND version: "' +
            version + '" ' + query,
        "limit": [0, 27131]
      },
      signature_storage: {
        type: "uuid",
        sub_storage: {
          type: "indexeddb",
          database: "installer_hash"
        }
      },
      local_sub_storage: {
        type: "mapping",
        no_sub_query_id: true,
        id: ["equalSubProperty", "relative_url"],
        property: {
          "reference": ["equalSubId"]
        },
        sub_storage: {
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              type: "indexeddb",
              database: window.location.origin + window.location.pathname +
                version_url
            }
          }
        }
      },
      remote_sub_storage: remote_storage
    });
  }

  function postMessage(gadget, message) {
    return new RSVP.Promise(function (resolve, reject) {
      var messageChannel = new MessageChannel();
      messageChannel.port1.onmessage = function (event) {
        if (event.data.error) {
          reject(event.data.error);
        } else {
          return resolve(event.data);
        }
      };
      gadget.props.serviceWorker.postMessage(
        JSON.stringify(message),
        [messageChannel.port2]
      );
    });
  }

  rJS(window)
    .ready(function (gadget) {
      var element_list =
        gadget.element.querySelectorAll("[data-install-configuration]"),
        i,
        key,
        value,
        gadget_list = [];
      gadget.props = {};
      gadget.props.cached_url = [];
      gadget.gadget_list = [];
      gadget.props.query_list = [];

      function pushGadget(url, i) {
        var element = document.createElement("div");
        element.setAttribute("style", "display: none");
        gadget.element.appendChild(element);
        return gadget.declareGadget(url,
          {
            "scope": "sub_app_installer_" + i,
            "element": element,
            "sandbox": "iframe"
          })
          .push(function (sub_gadget) {
            gadget.gadget_list.push(sub_gadget);
            return sub_gadget.setSubInstall();
          });
      }

      for (i = 0; i < element_list.length; i += 1) {
        key = element_list[i].getAttribute('data-install-configuration');
        value = element_list[i].textContent;
        if (key === "sub_app_installer") {
          if (value !== "") {
            gadget_list = value.split('\n');
          }
        } else {
          gadget.props[key] = value;
        }
      }

      return gadget.render()
        .push(function () {
          var promise_list = [];
          for (i = 0; i < gadget_list.length; i += 1) {
            promise_list.push(pushGadget(gadget_list[i], i + 1));
          }
          return RSVP.all(promise_list);
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
            {"app_name": gadget.props.app_name}
          );
        });
    })

    .declareMethod("setSubInstall", function () {
      this.props.sub = true;
    })

    .declareMethod("mainInstall", function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          if (gadget.props.document_version) {
            return gadget.install();
          }
        })
        .push(function () {
          var promise_list = [], i;
          for (i = 0; i < gadget.gadget_list.length; i += 1) {
            promise_list.push(gadget.gadget_list[i].waitInstall());
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          gadget.props.is_installed = true;
          if (gadget.installing !== undefined) {
            gadget.installing.resolve();
          }
          if (!gadget.props.sub) {
            window.location.pathname += gadget.props.version_url;
          }
        })
        .push(undefined, function (error) {
          console.log(error);
          if (error instanceof ProgressEvent) {
            if (gadget.props.sub === undefined) {
              window.location.pathname += gadget.props.version_url;
            }
            return;
          }
          throw error;
        });
    })

    .declareMethod("waitInstall", function () {
      if (this.props.is_installed) {
        return;
      }
      this.installing = RSVP.defer();
      return this.installing.promise;
    })

    .declareMethod("install", function () {
      var gadget = this;

      return serviceWorker_setting_storage.put(
        window.location.origin + window.location.pathname +
          gadget.props.version_url,
        {
            "version": gadget.props.document_version,
            "landing_page": gadget.props.landing_page
          }
      )
        .push(function () {
          // transform a cache to url_list
          gadget.props.storage = jIO.createJIO({
            type: "mapping",
            id: ["equalSubProperty", "reference"],
            sub_storage: remote_storage
          });
          return gadget.props.storage.get(gadget.props.cache_file)
            .push(function (doc) {
              var url_list = doc.text_content.split('\r\n'),
                i,
                take = false;
              if (url_list.length === 1) {
                url_list = doc.text_content.split('\n');
              }
              if (url_list.length === 1) {
                url_list = doc.text_content.split('\r');
              }
              for (i = 0; i < url_list.length; i += 1) {
                if (url_list[i].indexOf("NETWORK:") >= 0) {
                  take = false;
                }
                if (take &&
                    url_list[i] !== "" &&
                    url_list[i].charAt(0) !== '#' &&
                    url_list[i].charAt(0) !== ' ') {
                  url_list[i].replace("\r", "");
                  gadget.props.cached_url.push(url_list[i]);
                  gadget.props.query_list.push('( reference: "' +
                    url_list[i] + '" )');
                }
                if (url_list[i].indexOf("CACHE:") >= 0) {
                  take = true;
                }
              }
            });
        })
        .push(function () {
          var query = " AND (" + gadget.props.query_list.join(' OR ') + ')';
          gadget.props.storage = createStorage(
            query,
            gadget.props.version_url,
            gadget.props.document_version
          );
          return gadget.props.storage.repair();
        })
        .push(undefined, function (error) {
          console.log(error);
        }) // Here For Url too long: ex officejs_ckeditor_gadget
        .push(function () {
          // remove base if present
          if (document.querySelector("base")) {
            document.querySelector("head").removeChild(
              document.querySelector("base")
            );
          }
          navigator.serviceWorker.onerror = function (event) {
            console.log(event);
          };
          return navigator.serviceWorker.register(
            "gadget_officejs_bootloader_serviceworker.js",
            {"scope": gadget.props.version_url }
          );
        })
        .push(function (registration) {
          if (registration.installing) {
            gadget.props.serviceWorker = registration.installing;
          } else if (registration.waiting) {
            gadget.props.serviceWorker = registration.waiting;
          } else if (registration.active) {
            gadget.props.serviceWorker = registration.active;
          }
        })
        .push(function () {
          return postMessage(
            gadget,
            {
              "action": "install",
              "url_list": gadget.props.cached_url
            }
          );
        });
    })

    .declareService(function () {
      var gadget = this;

      function redirect() {
        window.location.href = gadget.props.redirect_url;
      }

      if (navigator.serviceWorker === undefined) {
        window.applicationCache.addEventListener("cached", redirect);
        window.applicationCache.addEventListener('noupdate', redirect);
        window.setTimeout(redirect, 10000);
      } else {
        return this.mainInstall();
      }
    });


}(window, document, RSVP, rJS, jIO, navigator, MessageChannel, ProgressEvent,
  console));