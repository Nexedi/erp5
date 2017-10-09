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
            gadget.getSetting('parent_relative_url')
          ]);
        })
        .push(function (result) {
          var ext = file_ext[result[0]],
            ret = {
            title: "Untitled Document",
            portal_type: result[0],
            parent_relative_url: result[1],
            content_type: content_type[result[0]] || undefined
          };
          if (ext) {
            ret.filename = "default." + ext;
          }
          return gadget.jio_post(ret);
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
