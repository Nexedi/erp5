/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
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
    .declareMethod("render", function (options) {
      var gadget = this;
      return RSVP.Queue()
        .push(function () {
          var ret = {
              title: "Untitled Document",
              portal_type: "JSON Document",
              schema: options.schema,
              parent_relative_url: "document_module"
            };
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
}(window, rJS, RSVP));
