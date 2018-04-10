/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Blob) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("jio_putAttachment", "jio_putAttachment")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function () {
      var gadget = this, doc_id;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('parent_relative_url'),
            gadget.getSetting('content_type', undefined),
            gadget.getSetting('file_extension', undefined)
          ]);
        })
        .push(function (result) {
          var doc = {
            title: "Untitled Document",
            portal_type: result[0],
            parent_relative_url: result[1],
            content_type: result[2]
          };
          if (result[3]) {
            doc.filename = "default." + result[3];
          }
          return gadget.jio_post(doc);
        })
        .push(function (id) {
          return gadget.redirect({
            command: 'display',
            options: {
              jio_key: id,
              editable: true
            }
          });
        });
    });
}(window, rJS, RSVP, Blob));
