/*global window, rJS, jIO, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  var ATT_NAME = "data";

  function getCloudoooId(key, format) {
    return 'CloudoooConversion/' + key + '/' + format;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("getSetting", "getSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("getConvertedBlob", function (options) {
      var gadget = this,
        mime_type = options.filename.split('.').pop();
      if (mime_type === options.format) {
        return gadget.jio_getAttachment(options.jio_key, ATT_NAME);
      }
      return gadget.jio_get(
        getCloudoooId(options.jio_key, options.format)
      )
        .push(function (doc) {
          var err, obj;
          if (doc.status === "converted") {
            return gadget.jio_getAttachment(options.jio_key, options.format);
          }
          if (doc.status === "error") {
            obj = window.JSON.parse(doc.error);
            err = new jIO.util.jIOError(obj.message, obj.status_code);
            err.detail = obj.detail;
          } else {
            err = new jIO.util.jIOError("Not converted", 500);
          }
          throw err;
        }, function (error) {
          if (error instanceof jIO.util.jIOError && error.status_code === 404) {
            return gadget.putAllCloudoooConvertionOperation({
              format: options.mime_type,
              jio_key: options.jio_key
            });
          }
          throw error;
        });
    })
    .declareMethod("putCloudoooConvertOperation", function (options) {
      return this.jio_put(getCloudoooId(options.id, options.to), options);
    })
    .declareMethod("putAllCloudoooConvertionOperation", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting("conversion_dict"),
            gadget.getSetting("file_extension")
          ]);
        })
        .push(function (result) {
          var promise_list = [],
            format_list = window.JSON.parse(result[0])[options.format],
            len = format_list.length,
            i;
          for (i = 0; i < len; i += 1) {
            promise_list.push(gadget.putCloudoooConvertOperation({
              status: "convert",
              from: options.format,
              to: format_list[i],
              id: options.jio_key,
              name: ATT_NAME
            }));
          }
          return RSVP.all(promise_list);
        });
    });
}(window, rJS, jIO, RSVP));