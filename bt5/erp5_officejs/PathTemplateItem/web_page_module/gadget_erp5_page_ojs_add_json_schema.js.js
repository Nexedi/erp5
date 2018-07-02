/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob) {
  "use strict";

  var content_type = {
    Spreadsheet: 'application/x-asc-spreadsheet',
    Presentation: 'application/x-asc-presentation',
    Text: 'application/x-asc-text'
  };

  var file_ext = {
    Spreadsheet: 'xlsy',
    Presentation: 'ppty',
    Text: 'docy'
  };

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("updatePanel", "updatePanel")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")
    .declareAcquiredMethod("jio_put", "jio_put")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        portal_type = options.portal_type,
        ext = file_ext[portal_type],
        ret = {
          title: "Untitled Schema",
          portal_type: "JSON Schema",
          parent_relative_url: "schema_module",
          content_type: content_type[portal_type] || undefined
        };
      return RSVP.Queue()
        .push(function () {
          if (ext) {
            ret.filename = "default." + ext;
          }
          return gadget.jio_post(ret);
        })
        .push(function (id) {
          ret.reference = id;
          return gadget.jio_put(id, ret)
            .push(function () {
              return gadget.jio_putAttachment(id, 'data',
                new Blob(['{"$schema": "http://json-schema.org/draft-07/schema#" }']));
            })
            .push(function () {
              return gadget.updatePanel({editable: true});
            })
            .push(function () {
              return gadget.redirect({
                command: 'display',
                options: {
                  jio_key: id,
                  editable: true
                }
              });
            });
        });
    });
}(window, rJS, RSVP, Blob));
