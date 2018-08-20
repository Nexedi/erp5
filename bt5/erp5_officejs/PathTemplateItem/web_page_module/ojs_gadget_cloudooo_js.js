/*global window, rJS, jIO, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  rJS(window)
    .ready(function (g) {
      g.getDeclaredGadget("jio")
        .push(function (jio_gadget) {
          return jio_gadget.createJio({
            type: "cloudooo",
            url: "https://cloudooo.erp5.net/",
            sub_storage: {
              type: "memory"
            }
          });
        });
    })
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_getAttachment", "jio_getAttachment")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("jio_put", "jio_put")
    .declareAcquiredMethod("jio_get", "jio_get")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("convertFromOperation", function (id) {
      var gadget = this;
      return gadget.jio_get(id)
        .push(function (doc) {
          return gadget.convert(doc)
            .push(function () {
              doc.status = "converted";
              return gadget.jio_put(id, doc);
            }, function (error) {
              if (error instanceof jIO.util.jIOError) {
                doc.status = "error";
                doc.error = jIO.util.stringify(error);
                return gadget.jio_put(id, doc);
              }
              throw error;
            });
        });
    })
    .declareMethod("convert", function (options) {
      var gadget = this, jio_gadget;
      return gadget.getDeclaredGadget("jio")
        .push(function (sub_gadget) {
          jio_gadget = sub_gadget;
          return RSVP.all([
            gadget.jio_getAttachment(options.id, options.name),
            jio_gadget.put(options.id, {from: options.from, to: options.to})
          ]);
        })
        .push(function (result) {
          return jio_gadget.putAttachment(options.id, options.name, result[0]);
        })
        .push(function () {
          return jio_gadget.getAttachment(options.id, options.name);
        })
        .push(function (converted_blob) {
          return gadget.jio_putAttachment(
            options.id,
            options.to_name ? options.to_name : options.to,
            converted_blob
          );
        });
    })
    .declareMethod('repair', function () {
      var gadget = this;
      function convertAndPush(rows, i) {
        if (i === -1) {
          return new RSVP.Queue();
        }
        return convertAndPush(rows, i - 1)
          .push(function () {
            return gadget.convertFromOperation(rows[i].id);
          });
      }
      return gadget.jio_allDocs({
        'query': 'status: "convert"'
      })
        .push(function (result) {
          var i = result.data.total_rows - 1;
          return convertAndPush(result.data.rows, i);
        });
    });
}(window, rJS, jIO, RSVP));