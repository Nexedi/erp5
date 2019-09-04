/*global window, rJS, jIO, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO, RSVP) {
  "use strict";

  function fixDocument(gadget, id) {
    var doc, from, name_list;
    return gadget.jio_get(id)
      .push(function (result) {
        doc = result;
        delete doc.mime_type;
        return RSVP.all([
          gadget.getSetting('parent_relative_url'),
          gadget.getSetting('file_extension')
        ]);
      })
      .push(function (result) {
        doc.parent_relative_url = result[0];
        if (doc.filename.indexOf(result[1]) < 0) {
          name_list = doc.filename.split('.');
          from = name_list.pop();
          name_list.push(result[1]);
          doc.filename = name_list.join('.');
          return gadget.jio_put(
            'CloudoooConversion/' + id + '/' + result[1],
            {
              status: 'convert',
              from: from,
              to: result[1],
              id: id,
              name: from,
              to_name: 'data'
            }
          )
            .push(function () {
              return gadget.jio_getAttachment(id, 'data');
            })
            .push(function (blob) {
              return gadget.jio_putAttachment(id, from, blob);
            });
        }
      })
      .push(function () {
        return gadget.jio_put(id, doc);
      });
  }

  function fixAllDocument(gadget) {
    return gadget.getSetting('portal_type')
      .push(function (portal_type) {
        return gadget.jio_allDocs({
          'query': '(portal_type: "' + portal_type +
            '") AND (mime_type: "%")'
        });
      })
      .push(function (result) {
        var i, promise_list = [];
        for (i = 0; i < result.data.total_rows; i += 1) {
          promise_list.push(fixDocument(gadget, result.data.rows[i].id));
        }
        return RSVP.all(promise_list);
      });
  }

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
    .declareAcquiredMethod("getSetting", "getSetting")

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
          return jio_gadget.putAttachment(options.id, options.name, result[0], options.conversion_kw);
        })
        .push(function () {
          return jio_gadget.getAttachment(options.id, options.name);
        })
        .push(function (converted_blob) {
          return gadget.jio_putAttachment(
            options.id,
            options.to_name || options.to,
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
      return fixAllDocument(gadget)
        .push(function () {
          return gadget.jio_allDocs({
            'query': 'status: "convert"'
          });
        })
        .push(function (result) {
          var i = result.data.total_rows - 1;
          return convertAndPush(result.data.rows, i);
        });
    });
}(window, rJS, jIO, RSVP));