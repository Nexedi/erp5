/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    // this gadget is kept for backward compatibility
    .declareMethod("render", function (options) {
      options.page = 'ojsm_landing';
      return this.redirect({"command": "display",
                            "options": options
                           });
    });

}(window, rJS));
