/*global window, rJS, jIO, FormData, XMLHttpRequestProgressEvent */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)

    .ready(function (gadget) {
      // Initialize the gadget local parameters
      gadget.props = {};
    })

    .declareMethod('createJio', function (options) {
      if (options !== undefined) {
        this.props.jio_storage = jIO.createJIO(options);
      } else {
        this.props.jio_storage = jIO.createJIO({
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
        });
      }
      return this.props.jio_storage;
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
      var storage = this.props.jio_storage;
      return storage.put.apply(storage, arguments);
    })
    .declareMethod('remove', function () {
      var storage = this.props.jio_storage;
      return storage.remove.apply(storage, arguments);
    })
    .declareMethod('getAttachment', function () {
      var storage = this.props.jio_storage;
      return storage.getAttachment.apply(storage, arguments);
    })
    .declareMethod('removeAttachment', function () {
      var storage = this.props.jio_storage;
      return storage.removeAttachment.apply(storage, arguments);
    })
    .declareMethod('repair', function () {
      var storage = this.props.jio_storage;
      return storage.repair.apply(storage, arguments)
        .push(undefined, function (error) {
          throw error;
        });
    });

}(window, rJS, jIO));