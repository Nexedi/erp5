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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var gadget = this, portal_type, extended_search, query_parts_list, query_redirect;
      if (options.query && options.url && options.username && options.password) {
        return new RSVP.Queue()
          .push(function () {
            return gadget.jio_allDocs({
              query: options.query
            });
          })
        .push(function (result) {
          // URL queries from slapos master / panel rapid space:
          // 'portal_type: "Instance Tree" AND title:"my-title"
          //           AND slapos_master_url:"url"'
          // or
          // 'portal_type: "Software Instance" AND title:"my-title"
          //           AND specialise_title:"my-parent-title"
          //           AND slapos_master_url:"url"'
          query_parts_list = options.query.split('AND');
          portal_type = query_parts_list[0].replace('portal_type:', '').replaceAll('"', '').trim();
          extended_search = options.query.replace(query_parts_list[0] + 'AND ', '').trim();
          if (options.slapos_master_url) {
            // disambiguate equal instances by slapos master url
            if (result !== undefined && result.data.total_rows > 1) {
              extended_search += ' AND slapos_master_url:"' + options.slapos_master_url + '"';
            }
          }
          query_redirect = {
            "page": "ojs_local_controller",
            "portal_type": portal_type + " Module",
            "extended_search": extended_search
          };
          if (result === undefined || result.data.total_rows === 0) {
            return gadget.setSetting('sync_redirect_options', query_redirect)
              .push(function (result) {
                return gadget.redirect(
                  {"command": "display",
                   "options": {
                     "url": options.url,
                     "username": options.username,
                     "password": options.password,
                     "slapos_master_url": options.slapos_master_url || "not-provided",
                     "page": "ojsm_opml_add"
                   }
                  });
              });
          } else {
            return gadget.redirect({
              "command": "display",
              "options": query_redirect
            });
          }
        });
      } else if (options.url && options.username && options.password) {
        return gadget.redirect(
          {"command": "display",
           "options": {
             "url": options.url,
             "username": options.username,
             "password": options.password,
             "slapos_master_url": options.slapos_master_url || "not-provided",
             "page": "ojsm_opml_add"
           }
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
                return gadget.redirect({command: 'change', options: {
                  page: "ojsm_erp5_configurator",
                  type: "erp5"
                }});
              }
            });
        })
        .push(function () {
          // default front page (list of promises)
          return gadget.redirect({command: 'display',
                                  options: {page: "ojs_local_controller",
                                            portal_type: "Promise Module"}
                                 });
        });
    });

}(window, rJS, RSVP));