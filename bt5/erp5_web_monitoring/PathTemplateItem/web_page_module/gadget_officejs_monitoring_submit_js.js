/*global document, window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 10, maxlen: 80 */
(function (document, window, rJS, RSVP) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod("handle_submit", function (argument_list, options) {
      switch (options.options.portal_type) {
      case "Instance Tree":
        //XXX do the old parameter gadget save here and fix it
        return this.redirect({command: 'reload'});
      default:
        return this.redirect({command: 'reload'});
      }
    });

}(document, window, rJS, RSVP));