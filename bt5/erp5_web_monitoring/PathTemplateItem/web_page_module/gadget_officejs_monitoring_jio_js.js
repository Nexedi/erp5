/*global window, rJS, jIO, FormData, AbortController, RSVP, navigator */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  var LOCK_NAME = "sync_lock";

  function promiseLock(name, options, callback) {
    var callback_promise = null,
      controller = new AbortController();

    function canceller(msg) {
      controller.abort();
      if (callback_promise !== null) {
        callback_promise.cancel(msg);
      }
    }

    function resolver(resolve, reject) {
      if (callback === undefined) {
        callback = options;
        options = {};
      }
      options.signal = controller.signal;

      function handleCallback(lock) {
        if (!lock) {
          // The lock was not granted - get out fast.
          return reject('Lock not granted');
        }
        try {
          callback_promise = callback();
        } catch (e) {
          return reject(e);
        }

        callback_promise = new RSVP.Queue(callback_promise)
          .push(resolve, function handleCallbackError(error) {
            // Prevent rejecting the lock, if the result cancelled itself
            if (!(error instanceof RSVP.CancellationError)) {
              canceller(error.toString());
              reject(error);
            }
          });
        return callback_promise;
      }

      return navigator.locks.request(name, options, handleCallback)
        .then(undefined, reject);
    }

    return new RSVP.Promise(resolver, canceller);
  }

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.props = {};
    })

    .declareAcquiredMethod("getSettingList", "getSettingList")
    .declareAcquiredMethod("setSetting", "setSetting")

    .declareMethod('createJio', function (options) {
      var gadget = this, current_version, index, manifest;
      return gadget.getSettingList(['configuration_manifest', 'migration_version'])
        .push(function (result_list) {
          manifest = result_list[0];
          console.log("manifest:", manifest);
          current_version = window.location.href.replace(window.location.hash, "");
          index = current_version.indexOf(window.location.host) + window.location.host.length;
          current_version = current_version.substr(index);
          if (result_list[1] !== current_version) {
            return gadget.setSetting("migration_version", current_version);
          }
        })
        .push(function () {
          if (options !== undefined) {
            gadget.props.jio_storage = jIO.createJIO(options);
          } else {
            gadget.props.jio_storage = jIO.createJIO({
              type: "replicatedopml",
              remote_storage_unreachable_status: "WARNING",
              remote_opml_check_time_interval: 86400000,
              request_timeout: 25000, // timeout is to 25 second
              local_sub_storage: {
                type: "query",
                sub_storage: {
                  type: "uuid",
                  sub_storage: {
                    type: "indexeddb",
                    database: "monitoring_local.db"
                  }
                }
              }/*,
              signature_sub_storage: {
                type: "query",
                sub_storage: {
                  type: "indexeddb",
                  database: "monitoring-configuration-hash"
                }
              },
              remote_sub_storage: {
                type: "saferepair",
                sub_storage: {
                  type: "configuration",
                  origin_url: window.location.href,
                  hateoas_appcache: "hateoas_appcache",
                  manifest: manifest,
                  sub_storage: {
                    type: "appcache",
                    origin_url: window.location.href,
                    manifest: manifest
                  }
                }
              }*/
            });
          }
          return gadget.props.jio_storage;
        });
    })
    .declareMethod('allDocs', function () {
      var storage = this.props.jio_storage;
      return storage.allDocs.apply(storage, arguments);
    })
    .declareMethod('allAttachments', function () {
      var storage = this.props.jio_storage;
      return storage.allAttachments.apply(storage, arguments);
    })
    .declareMethod('get', function () {
      var storage = this.props.jio_storage;
      return storage.get.apply(storage, arguments);
    })
    .declareMethod('put', function () {
      var storage = this.props.jio_storage,
        argument_list = arguments;
      return promiseLock(LOCK_NAME, {}, function () {
        return storage.put.apply(storage, argument_list);
      });
    })
    .declareMethod('remove', function () {
      var storage = this.props.jio_storage,
        argument_list = arguments;
      return promiseLock(LOCK_NAME, {}, function () {
        return storage.remove.apply(storage, argument_list);
      });
    })
    .declareMethod('getAttachment', function () {
      var storage = this.props.jio_storage;
      return storage.getAttachment.apply(storage, arguments);
    })
    .declareMethod('removeAttachment', function () {
      var storage = this.props.jio_storage,
        argument_list = arguments;
      return promiseLock(LOCK_NAME, {}, function () {
        return storage.removeAttachment.apply(storage, argument_list);
      });
    })
    .declareMethod('repair', function () {
      var storage = this.props.jio_storage,
        argument_list = arguments;
      return promiseLock(LOCK_NAME, {}, function () {
        return storage.repair.apply(storage, argument_list);
      });
    });

}(window, rJS, jIO));