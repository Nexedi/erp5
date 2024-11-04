/*global window, rJS, jIO */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, jIO) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("jio_remove", "jio_remove")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .declareMethod("render", function (options) {
      var gadget = this;
      return gadget.jio_remove(options.jio_key)
        .push(function () {
          return gadget.notifySubmitted({message: "Document Deleted", status: "success"});
        }, function (error) {
          if (error instanceof jIO.util.jIOError) {
            return gadget.notifySubmitted({message: error.message, status: "error"});
          } else {
            throw error;
          }
        })
        .push(function () {
          return gadget.redirect({command: 'change', options: {
            page: options.return_url || 'settings_configurator'
          }});
        });
    }, {mutex: 'render'});
}(window, rJS, jIO));