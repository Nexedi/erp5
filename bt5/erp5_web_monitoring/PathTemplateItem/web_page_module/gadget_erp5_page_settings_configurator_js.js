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
      var redirect_options = {
          "url": options.url,
          "username": options.username,
          "password": options.password,
          "page": "ojsm_opml_add"
        };
      return this.redirect({"command": "display",
                            "options": redirect_options
                           });
    });

}(window, rJS));
