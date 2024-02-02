/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP) {
  "use strict";

  rJS(window)

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this, portal_type, extended_search, query_parts_list,
        redirect_options = {
          "page": "ojsm_erp5_configurator",
          "url": options.url,
          "username": options.username,
          "password": options.password,
          "query": options.query
        };
      // add opml (old setting configurator)
      if (!options.query && options.url && options.username && options.password) {
        redirect_options.page = "ojsm_opml_add";
        return gadget.redirect({"command": "display",
                                "options": redirect_options
                               });
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.getSetting('latest_import_date')
            .push(function (import_date) {
              // If import was never done, or was done more than 2 weeks ago
              // 1209600000 = 1000*60*60*24*14
              if (import_date === undefined ||
                  (import_date + 1209600000) < new Date().getTime()) {
                return gadget.setSetting('sync_redirect_options', {
                  query: options.query,
                  page: 'ojsm_landing'
                })
                  .push(function () {
                    return gadget.redirect({command: 'change', options: {
                      page: "ojsm_erp5_configurator",
                      type: "erp5"
                    }});
                  });
              }
            });
        })
        .push(function () {
          //specific instance tree/software
          if (options.query) {
            // URL queries from slapos master / panel rapid space:
            // 'portal_type: "Instance Tree" AND title:"my-title"'
            // 'portal_type: "Software Instance" AND title:"my-title"'
            //           AND specialise_title:"my-parent-title"
            if (options.query.includes("portal_type")) {
              query_parts_list = options.query.split('AND');
              portal_type = query_parts_list[0].replace('portal_type:', '').replaceAll('"', '').trim();
              extended_search = options.query.replace(query_parts_list[0] + 'AND ', '').trim();
              redirect_options = {
                "page": "ojs_local_controller",
                "portal_type": portal_type + " Module",
                "extended_search": extended_search
              };
            }
            return gadget.redirect({"command": "display",
                                    "options": redirect_options
                                   });
          }
          // default front page (list of promises)
          return gadget.redirect({command: 'display',
                                  options: {page: "ojs_local_controller",
                                            portal_type: "Promise Module"}
                                 });
        });
    });

}(window, rJS, RSVP));