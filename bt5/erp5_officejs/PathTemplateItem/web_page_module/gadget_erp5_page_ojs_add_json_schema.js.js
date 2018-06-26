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

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          var portal_type = options.portal_type,
            ext = file_ext[portal_type],
            ret = {
              title: "Untitled Schema",
              portal_type: "JSON Schema",
              parent_relative_url: "schema_module",
              content_type: content_type[portal_type] || undefined
            };
          if (ext) {
            ret.filename = "default." + ext;
          }
          return gadget.jio_post(ret);
        })
        .push(function (id) {
          return gadget.jio_putAttachment(id, 'data',
            new Blob(['{"$schema": "http://json-schema.org/draft-04/schema#" }']))
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
