/*globals window, document, RSVP, rJS, URI, navigator, jIO*/
/*jslint indent: 2, maxlen: 80, nomen: true*/
var repair = false;
(function (window, document, RSVP, rJS, jIO) {
  "use strict";

  // in future this will be synchro with replicate and attachment :D
  var cached_url = [
    "handlebars.js",
    "https://netdna.bootstrapcdn.com/"
      + "font-awesome/4.2.0/css/font-awesome.min.css",
    "https://netdna.bootstrapcdn.com/"
      + "font-awesome/4.2.0/fonts/fontawesome-webfont.woff?v=4.2.0",
    "ckeditor/ckeditor.js",
    "ckeditor/config.js",
    "ckeditor/skins/moono/editor.css",
    "ckeditor/skins/moono/icons.png",
    "ckeditor/lang/fr.js",
    "ckeditor/styles.js"
  ];

  function postMessage(gadget, message, callback) {
    var messageChannel = new MessageChannel();
    new RSVP.Queue()
      .push(function () {
        return new RSVP.Promise(function (resolve, reject, notify) {
          var messageChannel = new MessageChannel();
          messageChannel.port1.onmessage = function(event) {
            console.log(event);
            if (event.data.error) {
              reject(event.data.error);
            } else {
              resolve(event.data);
            }
            callback();
          };
          return gadget.props.serviceWorker.postMessage(
            JSON.stringify(message),
            [messageChannel.port2]
          );
        });
      });
  }

  rJS(window)
    .ready(function (gadget) {
      gadget.props = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.props.element = element;
          gadget.props.redirect = "development/";
          gadget.props.version = "OSP-11-dev";
          if ("serviceWorker" in navigator) {
            return gadget.notifyInstalling();
          }
          if (gadget.props.redirect) {
            window.location.href = gadget.props.redirect;
          } else {
            gadget.renderError();
          }
        });
    })

    .declareMethod("renderError", function () {
      // TODO : great and beautifull error page.
      this.props.element.innerHTML = "<h2> please get a device with service "
        + 'worker installed</h2>';
    })

    .declareMethod("renderInstalling", function () {
      this.props.element.innerHTML = "<h2> Installing ... </h2>";
    })

    .declareMethod("notifyInstalling", function () {
      var gadget = this,
        query_date = {
          select_list: ['modification_date'],
          sort_on: [['modification_date','descending']]
        };
      function notifyInstalled () {
        return gadget.notifyInstalled();
      }
      gadget.renderInstalling();

      gadget.props.storage = jIO.createJIO({
        type: "replicate",
        conflict_handling: 2,
        check_remote_modification: true,
        check_remote_creation: true,
        check_remote_deletion: true,
        query: {
          query:'portal_type: ("Web Illustration",'
            + '"Web Manifest","Web Script","Web Style","Web Page")',
          "limit": [0,27131]
        },
        signature_storage: {
          type: "indexeddb",
          database: gadget.props.version + "_hash"
        },
        local_sub_storage: {
          type: "query",
          sub_storage: {
            type: "uuid",
            sub_storage: {
              type: "indexeddb",
              database: gadget.props.version,
            }
          }
        },
        remote_sub_storage: {
          type: "mapping",
          map_all_property: true,
          mapping_dict: {
            "id": {"equal": "reference"},
            "version": {"default_value": gadget.props.version} 
          },
          sub_storage: {
            type: "erp5",
            url: window.location.origin + "/erp5/web_site_module/hateoas",
            default_view_reference: "jio_view"
          }
        }
      });
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.props.storage.__storage.
              _local_sub_storage.allDocs(query_date),
            gadget.props.storage.__storage.
              _remote_sub_storage.allDocs(query_date)
          ]);
        })
        .push(function (result) {
          if (result[0].data.rows.length === 0) {
            console.log("cache will load");
            return gadget.props.storage.repair();
          }
          if (new Date(result[0].data.rows[0].value.modification_date)
              < new Date(result[1].data.rows[0].value.modification_date)) {
            console.log("cache refresh");
            return gadget.props.storage.repair({
              query: 'modification_date: >="'
                + result[0].data.rows[0].value.modification_date + '"'
            });
          }
          console.log("No cache update");
        })
        .push(function () {
          return navigator.serviceWorker.register(
            "gadget_officejs_install_serviceworker.js",
            {"scope": gadget.props.redirect}
          );
        })
        .push(function (registration) {
          console.log("Service Worker Installed: ",registration.scope);
          if (registration.installing) {
            gadget.props.serviceWorker = registration.installing;
          } else if (registration.waiting) {
            gadget.props.serviceWorker = registration.waiting;
          } else if (registration.active) {
            gadget.props.serviceWorker = registration.active;
          }
          return postMessage(
            gadget,
            {
              "action": "install",
              "urls": cached_url,
              "version": gadget.props.version
            },
            notifyInstalled
          );
        });
    })

    .declareMethod("notifyInstalled", function () {

      console.log("Chargement de la page");
      window.location.href = this.props.redirect;
      return;
    });


}(window, document, RSVP, rJS, jIO));