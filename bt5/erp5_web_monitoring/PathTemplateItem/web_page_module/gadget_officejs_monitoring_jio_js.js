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

    .declareMethod('updateConfiguration', function (appcache_storage, migration_version, current_version, jio_storage) {
      var gadget = this;
      if (!appcache_storage) { return; }
      return RSVP.Queue()
        .push(function () {
          return appcache_storage.repair(current_version);
        })
        .push(function () {
          return jio_storage.repair();
        })
        .push(function () {
          return gadget.setSetting("migration_version", current_version);
        });
    })

    .declareMethod('createStorage', function (options, monitoring_jio) {
      var gadget = this;
      if (options !== undefined) {
        gadget.props.jio_storage = jIO.createJIO(options);
      } else {
        gadget.props.jio_storage = jIO.createJIO(monitoring_jio);
      }
    })

    .declareMethod('createJio', function (options) {
      var gadget = this, current_version, index, appcache_storage,
        monitoring_jio, appcache_jio, migration_version, manifest,
        origin_url = window.location.href;
      return gadget.getSettingList(['configuration_manifest',
                                    'migration_version'])
        .push(function (result_list) {
          //TODO fix missing router setting (it's set but get returns undefined)
          migration_version = result_list[1];
          current_version = window.location.href.replace(window.location.hash, "");
          index = current_version.indexOf(window.location.host) + window.location.host.length;
          current_version = current_version.substr(index);
          manifest = "gadget_officejs_monitoring.configuration";
          monitoring_jio = {
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
            }
          };
          appcache_jio = {
            type: "replicate",
            parallel_operation_attachment_amount: 10,
            parallel_operation_amount: 1,
            conflict_handling: 2, //keep remote
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
                database: "monitoring-configuration-hash"
              }
            },
            local_sub_storage: JSON.parse(JSON.stringify(monitoring_jio)),
            remote_sub_storage: {
              type: "saferepair",
              sub_storage: {
                type: "configuration",
                origin_url: origin_url,
                hateoas_appcache: "hateoas_appcache",
                manifest: manifest,
                sub_storage: {
                  type: "appcache",
                  origin_url: origin_url,
                  manifest: manifest
                }
              }
            }
          };
          return gadget.createStorage(options, monitoring_jio);
        })
        .push(function () {
          if (migration_version !== current_version) {
            if (gadget.props.jio_storage) {
              return gadget.props.jio_storage.allDocs();
            }
          }
        })
        .push(function (all_docs) {
          if (all_docs && all_docs.data.total_rows) {
            //iterate all docs, jio_remove, and recreate
            var remove_queue = new RSVP.Queue(), i;
            function remove_doc(id) {
              remove_queue
                .push(function () {
                  return gadget.props.jio_storage.remove(id);
                });
            }
            for (i = 0; i < all_docs.data.total_rows; i += 1) {
              remove_doc(all_docs.data.rows[i].id);
            }
            return RSVP.all([
              remove_queue,
              gadget.createStorage(options, monitoring_jio),
              gadget.setSetting("latest_import_date", undefined)
            ]);
          }
        })
        .push(function () {
          if (migration_version !== current_version) {
            appcache_storage = jIO.createJIO(appcache_jio);
            return gadget.updateConfiguration(appcache_storage, migration_version, current_version, gadget.props.jio_storage);
          }
        })
        .push(function () {
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