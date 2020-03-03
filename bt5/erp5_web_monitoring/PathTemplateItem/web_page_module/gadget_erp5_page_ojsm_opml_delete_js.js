/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
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
      return this.remove(options);
    })
    .declareJob("remove", function (options) {
      var gadget = this;

      return gadget.notifySubmitting()
        .push(function () {
          return gadget.jio_remove(options.jio_key);
        })
        .push(function () {
          return gadget.notifySubmitted({message: "Document Deleted", status: "success"});
        })
        .push(function () {
          return gadget.redirect({command: 'change', options: {
            page: options.return_url || 'settings_configurator'
          }});
        });
    });
}(window, rJS));
