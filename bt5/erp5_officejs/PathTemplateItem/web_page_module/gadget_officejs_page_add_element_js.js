/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */

(function (window, rJS) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_post", "jio_post")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("render", function (options) {
      var gadget = this,
        doc = {
          title: "Untitled Document",
          portal_type: options.portal_type,
          parent_relative_url: options.parent_portal_type.replace(/ /g, '_').toLowerCase()
        };
      return gadget.jio_post(doc)
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

}(window, rJS));
