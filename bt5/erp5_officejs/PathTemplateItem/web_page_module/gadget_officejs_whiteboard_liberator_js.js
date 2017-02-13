/*global window, rJS, jIO, FormData, RSVP, MessageChannel */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO, MessageChannel, RSVP) {
  "use strict";

  var cached_url = [
    "renderjs.js",
    "rsvp.js",
    "jiodev.js",
    "jio_mappingstorage.js",
    "gadget_officejs_whiteboard_liberator.js",
    "gadget_officejs_whiteboard_liberator.html"
  ];

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
      gadget.state_parameter_dict = {};
      gadget.props = {};
      return new RSVP.Queue()
        .push(function () {
          return window.navigator.serviceWorker.register(
            "gadget_officejs_bootloader_serviceworker.js"
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
              "url_list": cached_url,
              "version": "001"
            }
          );
        });
    })

    .declareMethod('createStorage', function (erp5_url) {
      var gadget = this;
      gadget.state_parameter_dict.jio_storage = jIO.createJIO({
        use_remote_post: false,
        conflict_handling: 1,
        check_local_modification: true,
        check_local_creation: true,
        check_local_deletion: false,
        check_remote_modification: false,
        check_remote_creation: false,
        check_remote_deletion: false,
        type: "replicate",
        query: {query: 'content_type: "text%"'},
        signature_storage: {
          type: "indexeddb",
          database: "sync_hash"
        },
        local_sub_storage: {
          type: "uuid",
          sub_storage: {
            type: "query",
            sub_storage: {
              type: "indexeddb",
              database: (window.location.origin + window.location.pathname)
                .replace("gadget_officejs_whiteboard_liberator.html", "")
            }
          }
        },
        remote_sub_storage: {
          type: "mapping",
          id: ["equalSubProperty", "reference"],
          property: {
            "relative_url": ["ignore"],
            "version": ["ignore"]
          },
          sub_storage: {
            type: "erp5",
            url: erp5_url + "/hateoas",
            default_view_reference: "jio_view"
          }
        }
      });
      return gadget.state_parameter_dict.jio_storage.get("/")
        .push(undefined, function (error) {
          if (error.status_code === 404) {
            return gadget.state_parameter_dict.jio_storage.put("/", {
              "reference": "/",
              "title": "Root Page",
              "portal_type": "Web Page",
              "parent_relative_url": "web_page_module",
              "content_type": "text/html",
              "text_content": "<html>Root of your Free Web Site</html>",
              "modification_date": (new Date()).toISOString()
            });
          }
          throw error;
        });
    })
    .declareMethod('allDocs', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allDocs.apply(storage, arguments);
    })
    .declareMethod('allAttachments', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.allAttachments.apply(storage, arguments);
    })
    .declareMethod('get', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.get.apply(storage, arguments);
    })
    .declareMethod('put', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.put.apply(storage, arguments);
    })
    .declareMethod('post', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.post.apply(storage, arguments);
    })
    .declareMethod('remove', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.remove.apply(storage, arguments);
    })
    .declareMethod('getAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.getAttachment.apply(storage, arguments);
    })
    .declareMethod('putAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.putAttachment.apply(storage, arguments);
    })
    .declareMethod('removeAttachment', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.removeAttachment.apply(storage, arguments);
    })
    .declareMethod('repair', function () {
      var storage = this.state_parameter_dict.jio_storage;
      return storage.repair.apply(storage, arguments);
    });

}(window, rJS, jIO, MessageChannel, RSVP));