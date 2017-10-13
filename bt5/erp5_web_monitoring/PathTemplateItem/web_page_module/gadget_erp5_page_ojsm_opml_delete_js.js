/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_remove", "jio_remove")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .declareMethod("render", function (options) {
      var gadget = this;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.jio_remove(options.jio_key);
        })
        .push(function () {
          return gadget.notifySubmitted("Document Deleted");
        })
        .push(function () {
          return gadget.redirect({command: 'change', options: {
            page: options.return_url || 'settings_configurator'
          }});
        });
    });
}(window, rJS, RSVP, Handlebars));
