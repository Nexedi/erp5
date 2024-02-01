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
      var gadget = this, portal_type, extended_search, query_parts_list,
        redirect_options = {
          "page": "ojsm_dispatch",
          "url": options.url,
          "username": options.username,
          "password": options.password,
          "query": options.query
        };
      //specific instance tree/software
      if (options.query) {
        // URL queries from slapos master / panel rapid space:
        // query = portal_type: Instance Tree AND title:"my-title"
        // query = portal_type: Software Instance AND title:"my-title"
        //           AND specialise_title:"my-parent-title"
        if (options.query.includes("portal_type")) {
          query_parts_list = options.query.split('AND');
          portal_type = query_parts_list[0].replace('portal_type:', '').trim();
          extended_search = options.query.replace(query_parts_list[0] + 'AND ', '').trim();
          redirect_options = {
            "page": "ojs_local_controller",
            "portal_type": portal_type + " Module",
            "url": options.url,
            "username": options.username,
            "password": options.password,
            "extended_search": extended_search
          };
        }
        return gadget.redirect({"command": "display",
                                "options": redirect_options
                               });
      }
      // add opml (old setting configurator)
      if (options.url && options.username && options.password) {
        redirect_options.page = "ojsm_opml_add";
        return gadget.redirect({"command": "display",
                                "options": redirect_options
                               });
      }
      // default front page (list of promises)
      return gadget.redirect({command: 'display',
                              options: {page: "ojs_local_controller",
                                        portal_type: "Promise Module"}
                             });
      //TODO check here the last sync and redirect to import-export page?
    });

}(window, rJS));