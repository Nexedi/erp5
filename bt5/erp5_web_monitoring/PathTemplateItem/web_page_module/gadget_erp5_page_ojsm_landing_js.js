/*global window, rJS, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("landing-template")
                         .innerHTML,
    landing_template = Handlebars.compile(source);

  gadget_klass

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
      gadget.element.querySelector('.search-result')
        .innerHTML = landing_template({});
    });

}(window, rJS, Handlebars));