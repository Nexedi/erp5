/*global window, rJS */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this,
        redirect_options = {
          "page": "ojsm_dispatch",
          "url": options.url,
          "username": options.username,
          "password": options.password,
          "query": options.query
        };
      if (options.query) {
        return gadget.redirect({"command": "display",
                                "options": redirect_options
                               });
      }
      if (options.url && options.username && options.password) {
        redirect_options.page = "ojsm_opml_add";
        return gadget.redirect({"command": "display",
                                "options": redirect_options
                               });
      }
      return gadget.redirect({"command": "display",
                              "options": {"page": "ojsm_status_list"}
                             });
    });

}(window, rJS));