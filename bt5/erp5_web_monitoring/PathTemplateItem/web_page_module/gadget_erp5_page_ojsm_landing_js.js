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
      var gadget = this;
      if (options.query) {
        return gadget.redirect({"command": "display",
                                "options": {"page": "ojsm_dispatch",
                                            "query": options.query}
                               });
      }
      if (options.url && options.username && options.password) {
        return gadget.redirect({"command": "display",
                                "options": {"page": "settings_configurator",
                                            "url": options.url,
                                            "username": options.username,
                                            "password": options.password}
                               });
      }
      return gadget.redirect({"command": "display",
                              "options": {"page": "ojsm_status_list"}
                             });
    });

}(window, rJS));