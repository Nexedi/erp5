/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    source = gadget_klass.__template_element
                         .getElementById("dispatch-template")
                         .innerHTML,
    dispatch_template = Handlebars.compile(source);

  function searchItem(gadget, search_query) {
    var redirect_options = {},
      select_list = ["portal_type"];
    if (search_query === undefined || search_query === "") {
      return new RSVP.Queue()
        .push(function () {
          return;
        });
    }
    return new RSVP.Queue()
      .push(function () {
        return gadget.getSetting("listbox_lines_limit", 20);
      })
      .push(function (lines_limit) {
        return gadget.jio_allDocs({
          query: search_query,
          select_list: select_list,
          limit: [0, lines_limit]
        });
      })
      .push(function (result) {
        if (result === undefined || result.data.total_rows === 0) {
          // no result from the query
          return;
        }
        if (result.data.total_rows === 1) {
          // one item found, redirect to it
          redirect_options = {
            jio_key: result.data.rows[0].id
          };
          return gadget.redirect({"command": "index", options: redirect_options});
        }
        redirect_options = {
          extended_search: gadget.state.query
        };
        if (gadget.state.portal_type === undefined) {
          // take the first one
          gadget.state.portal_type = result.data.rows[0].value.portal_type;
        }
        if (gadget.state.portal_type === "Hosting Subscription") {
          redirect_options.page = "ojsm_hosting_subscription_list";
        } else if (gadget.state.portal_type === "Software Instance") {
          redirect_options.page = "ojsm_software_instance_list";
        } else if (gadget.state.portal_type === "promise") {
          redirect_options.page = "ojsm_status_list";
        }
        return gadget.redirect({"command": "display", options: redirect_options});
      });
  }

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("triggerSubmit", function () {
      var argument_list = arguments;
      return this.getDeclaredGadget('form_view')
        .push(function (gadget) {
          return gadget.triggerSubmit.apply(gadget, argument_list);
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this,
        regex = /portal_type\s*\:\s*[\'\"]([\w+\s+]+)[\'\"]/i,
        regex_list = /\(?([\w\d\_]+)\s*\:\s*\(([\"\w\_\d\-\.\s*\,]+)\)\)?/g,
        query_list = [],
        i,
        tmp,
        page_title = "Monitoring Search",
        original_query,
        portal_type,
        pt_result,
        result;

      result = regex_list.exec(options.query);
      if (result !== null) {
        tmp = result[2].split(',');
        for (i = 0; i < tmp.length; i += 1) {
          query_list.push(result[1] + ': ' + tmp[i].trim());
        }
        options.query = options.query
          .replace(regex_list, '(' + query_list.join(' OR ') + ')');
      }
      original_query = JSON.parse(JSON.stringify(options.query || ""));

      pt_result = regex.exec(options.query);
      if (pt_result !== null) {
        page_title = "Searching " + pt_result[1] + "(s)";
        portal_type = pt_result[1];
      }

      return gadget.getUrlFor({command: 'display', options: {page: 'ojsm_status_list'}})
        .push(function (back_url) {
          return gadget.updateHeader({
            page_title: page_title,
            back_url: back_url
          });
        })
        .push(function () {
          return gadget.changeState({
            original_query: original_query,
            query: options.query,
            portal_type: portal_type || "promise",
            import_opml: portal_type === undefined ? false : options.import_opml || true
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;

      return new RSVP.Queue()
        .push(function () {
          if (gadget.state.import_opml) {
            return gadget.getSetting('latest_import_date')
              .push(function (import_date) {
                // If import was never done, or was done more than 2 weeks ago
                // 1209600000 = 1000*60*60*24*14
                var current_date = new Date().getTime();
                if (import_date === undefined ||
                    (import_date + 1209600000) < current_date) {
                  return gadget.setSetting('sync_redirect_options', {
                    query: gadget.state.original_query,
                    page: 'ojsm_dispatch'
                  })
                    .push(function () {
                      return gadget.redirect({command: 'change', options: {
                        page: "ojsm_erp5_configurator",
                        type: "erp5"
                      }});
                    });
                }
              });
          }
        })
        .push(function () {
          return gadget.getDeclaredGadget('erp5_searchfield');
        })
        .push(function (searchfield) {
          return searchfield.render({
            extended_search: gadget.state.original_query,
            focus: true
          });
        })
        .push(function () {
          return searchItem(gadget, gadget.state.query);
        })
        .push(function (search_result) {
          if (search_result === undefined && gadget.state.query) {
            gadget.element.querySelector('.search-result')
              .innerHTML = dispatch_template({});
          }
        });
    })
    .onEvent('submit', function () {
      var gadget = this;

      return gadget.getDeclaredGadget("erp5_searchfield")
        .push(function (search_gadget) {
          return search_gadget.getContent();
        })
        .push(function (data) {
          var options = {
            page: "ojsm_dispatch"
          };
          if (data.search) {
            options.query = data.search;
            return gadget.redirect({command: 'change', options: options});
          }
        });

    }, false, true);

}(window, rJS, RSVP, Handlebars));