/*globals window, document, RSVP, rJS, navigator, jIO, MessageChannel, ProgressEvent*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO, navigator, MessageChannel,
  ProgressEvent) {
  "use strict";

  var setting_storage = jIO.createJIO({
    type: "indexeddb",
    database: "setting"
  });

  var server_storage_spec = {
    type: "erp5",
    url: window.location.href + "/hateoasnoauth",
    default_view_reference: "jio_view"
  };

  function setSetting(key, value) {
    return setting_storage.get("setting")
      .push(undefined, function (error) {
        if (error.status_code === 404) {
          return {};
        }
        throw error;
      })
      .push(function (doc) {
        doc[key] = value;
        return setting_storage.put('setting', doc);
      });
  }

  function createStorage(version_url, document_version) {
    return jIO.createJIO({
      type: "replicate",
      conflict_handling: 2,
      check_remote_modification: true,
      check_remote_deletion: false,
      check_local_creation: false,
      check_local_deletion: false,
      check_local_modification: false,
      query: {
        query: 'portal_type: ("Web Illustration",' +
          '"Web Script","Web Style","Web Page")' +
          'AND version:"' + document_version + '"',
        "limit": [0, 27131],
        "select_list": ["url_string"]
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
        no_query_sub_id: true,
        map_all_property: true,
        map_id: ["equalSubProperty", "relative_url"],
        mapping_dict: {
          "url_string": ["equalSubId"]
        },
        sub_storage: {
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              type: "indexeddb",
              database: window.location.href + version_url
            }
          }
        }
      },
      remote_sub_storage: server_storage_spec
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
      gadget.props.sub_gadget_version = {};

      function pushGadget(sub_info, i) {
        var element = document.createElement("div"),
          info = sub_info.split(',');
        element.setAttribute("style", "display: none");
        gadget.element.appendChild(element);
        
        return gadget.declareGadget(info[0],
          {
            "scope": "sub_app_installer_" + i,
            "element": element,
            "sandbox": "iframe"
          })
          .push(function (sub_gadget) {
            gadget.gadget_list.push(sub_gadget);
            gadget.props.sub_gadget_version[info[0]] = info[1];
            return sub_gadget.setSubInstall(
              {"version": info[1] || "development"}
            );
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
        "gadget_officejs_install_presentation.html",
        {"scope": "presentation", "element": element}
      )
        .push(function (presentation_gadget) {
          return presentation_gadget.render(
            {"app_name": gadget.props.app_name}
          );
        });
    })

    .declareMethod("setSubInstall", function (option) {
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
            window.location.href = gadget.props.version_url;
          }
        })
        .push(undefined, function (error) {
          if (error instanceof ProgressEvent) {
            if (gadget.props.sub === undefined) {
              window.location.href = gadget.props.version_url;
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
      var gadget = this,
        server_storage = jIO.createJIO(
          {
            type: "mapping",
            query: {query: 'version: "' + gadget.props.document_version + '"'},
            map_id: ["equalSubProperty", "url_string"],
            sub_storage: server_storage_spec
          });

      return server_storage.get(gadget.props.cache_file)
        .push(function (doc) {
          var i,
            take = false,
            url_list = doc.text_content.split('\r\n');
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
              url_list[i].replace("\r","");
              gadget.props.cached_url.push(url_list[i]);
            }
            if (url_list[i].indexOf("CACHE:") >= 0) {
              take = true;
            }
          }
          return setSetting(
            "sub_gadget_version",
            gadget.props.sub_gadget_version
          );
        })
        .push(function () {
          gadget.props.storage = createStorage(
            gadget.props.version_url,
            gadget.props.document_version
          );
          return gadget.props.storage.repair();
        })
        .push(function () {
          // remove base if present
          if (document.querySelector("base")) {
            document.querySelector("head").removeChild(
              document.querySelector("base")
            );
          }
          return navigator.serviceWorker.register(
            "gadget_officejs_install_serviceworker.js",
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
              "url_list": gadget.props.cached_url,
              "version": gadget.props.document_version
            }
          );
        });
    })

    .declareService(function () {
      var gadget = this;

      function redirect() {
        window.location.href = gadget.props.redirect_url;
      }

      if (!("serviceWorker" in navigator)) {
        window.applicationCache.addEventListener("cached", redirect);
        window.applicationCache.addEventListener('noupdate', redirect);
        window.setTimeout(redirect, 10000);
      } else {
        return gadget.mainInstall();
      }
    });


}(window, document, RSVP, rJS, jIO, navigator, MessageChannel, ProgressEvent));