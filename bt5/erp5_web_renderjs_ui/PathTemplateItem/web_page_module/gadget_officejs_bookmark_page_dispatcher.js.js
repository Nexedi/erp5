/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  function redirectFromSearch(gadget, search) {
    return new RSVP.Queue()
      .push(function () {
        var query = "",
          command = "",
          parameter = "",
          index;
        if (search) {
          if (search.startsWith("!")) {
            index = search.indexOf(" ");
            if (index !== -1) {
              command = search.substring(1, index);
              parameter = search.substr(index + 1);
            } else {
              command = search.substr(1);
              parameter = "";
            }
            if (command === "add") {
              return gadget.redirect({
                command: 'display',
                options: {
                  page: "ojs_add_bookmark",
                  url_string: parameter
                }
              });
            }
            query = {
              query: '(reference:"' + command + '")' +
                ' AND portal_type:"' + gadget.state.portal_type + '"',
              select_list: ['url_string']
            };
          } else {
            query = {
              query: '("' + search +
                '") AND portal_type:"' + gadget.state.portal_type + '"',
              select_list: ['title', 'url_string', 'description']
            };
          }
          return gadget.jio_allDocs(query)
            .push(function (query_result) {
              var result_list_length = query_result.data.rows.length;

              // if 0 result, let's search with a real search engine
              if (result_list_length === 0 &&
                  gadget.state.search_engine !== '') {
                return gadget.redirect({
                  command: 'raw',
                  options: {
                    url: gadget.state.search_engine +
                      window.encodeURIComponent(search)
                  }
                });
              }
              if (result_list_length === 1 &&
                  (gadget.state.auto_redirect === true ||
                    command !== "")) {
                // if 1 result, and redirect or command ,we go there
                return gadget.redirect({
                  command: 'raw',
                  options: {
                    url: query_result.data.rows[0].value.url_string +
                      parameter
                  }
                });
              }
              return gadget.redirect({
                command: 'display',
                options: {
                  page: "ojs_bookmark_list",
                  extended_search: search
                }
              });
            });
        }
      });
  }

  rJS(window)
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareAcquiredMethod("notifySubmitting", "notifySubmitting")



    .declareMethod('triggerSubmit', function () {
      return this.element.querySelector('button[type="submit"]').click();
    })

    .declareMethod("render", function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Search in Bookmarks',
            submit_action: true
          });
        })
        .push(function () {
          return RSVP.all([
            gadget.getSetting('portal_type'),
            gadget.getSetting('bookmark_auto_redirect', true),
            gadget.getSetting(
              'bookmark_search_engine',
              "https://duckduckgo.com/?q="
            )
          ]);
        })
        .push(function (result) {
          return gadget.changeState({
            search: options.search || "",
            portal_type: result[0],
            auto_redirect: result[1],
            search_engine: result[2],
            extended_search: options.extended_search || ""
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;
      if (modification_dict.search) {
        return redirectFromSearch(gadget, gadget.state.search);
      }
      if (modification_dict.extended_search) {
        return redirectFromSearch(gadget, modification_dict.extended_search);
      }
      return gadget.getDeclaredGadget('erp5_searchfield')
        .push(function (search_gadget) {
          return search_gadget.render({
            field_json: {
              value: gadget.state.search,
              editable: true,
              title: "Search",
              required: true,
              key: "search"
            }
          });
        });
    })
    .allowPublicAcquisition("notifyValid", function () {
      return true;
    })
    .allowPublicAcquisition("notifyInvalid", function () {
      return true;
    })
    .onEvent("submit", function () {
      var gadget = this;
      return gadget.notifySubmitting()
        .push(function () {
          return gadget.getDeclaredGadget('erp5_searchfield');
        })
        .push(function (search_gadget) {
          return search_gadget.getContent();
        })
        .push(function (content) {
          return redirectFromSearch(gadget, content.search);
        });
    });

}(window, RSVP, rJS));