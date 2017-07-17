/*globals window, RSVP, rJS*/
/*jslint indent: 2, nomen: true, maxlen: 80*/
(function (window, RSVP, rJS) {
  "use strict";

  function getSearchedString() {                                                                                                        
    var regex = new RegExp("[\\#?&]search=([^&]*)"),
    results = regex.exec(window.location.hash);
    return results === null ? "" : decodeURIComponent(results[1].trim().replace(/\+/g, " "));
  }

  function updateSearchUrl(event) {
    var gadget = this;
    makeOptionDict(gadget)
      .push(function() {
        return gadget.getSetting("option");
      })
      .push(function(option) {
        return gadget.getUrlFor(option);
      })
      .push(function(url) {
        url = window.location.href + url;
        gadget.props.element.getElementsByClassName("search-engine-url")[0].innerHTML = url;
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })
    .declareAcquiredMethod("translate", "translate")
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('getSetting', 'getSetting')
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("setSetting", "setSetting")
    .declareMethod("render", function (options) {
      var gadget = this,
        portal_type = null,
        option = {
          auto_redirect: true,
          search_engine: "https://duckduckgo.com/?q="
        };

      return new RSVP.Queue()
        .push(gadget.updateHeader({title: 'Search in Bookmarks'}))
        .push(function () {
          return gadget.getSetting("portal_type")
            .push(function(result) {
              portal_type = result;
            });
        })
        .push(function (){
          return gadget.getSetting("option")
            .push(function(result) {
              if (result) {
                option = result;
              }
            });
        })
        .push(function () {
          var search = window.decodeURIComponent(getSearchedString()),
            query = "",
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
                return gadget.getUrlFor({
                  page: "add_bookmark",
                  url_string: parameter
                }).push(function (url) {
                  window.location.href = url;
                });
              }
              query = {
                query: '(reference:"' + command + '")'
                  + ' AND portal_type:"' + portal_type + '"',
                select_list: ['url_string']
              };
            } else {
              query = {
                query: '(title:"%' + search + '%" OR url_string:"%' + search + '%" OR description:"%' + search + '%") AND portal_type:"' + portal_type + '"',
                select_list: ['title', 'url_string', 'description'],
              };
            }
            return gadget.jio_allDocs(query)
              .push(function (query_result) {
                var result_list_length = query_result.data.rows.length;

                // if 0 result, let's search with a real search engine
                if (result_list_length === 0 && option.search_engine !== '') {
                  window.location.href = option.search_engine + window.encodeURIComponent(search);
                } else if (result_list_length === 1
                         && (option.auto_redirect === true || command !== "")) {
                  // if 1 result, and redirect or command ,we go there
                  window.location.href = query_result.data.rows[0].value.url_string
                    + parameter;
                }
                else {
                  return gadget.getUrlFor({page: "bookmark_list", search: window.encodeURIComponent(search)})
                    .push(function (url) {
                      window.location.href = url;
                    });
                }
              });
          }
        });
    })
    .onEvent("submit", function () {
      var gadget = this;
      //var option_parameter = gadget.getSetting("option");
      var option_parameter = {
        search: window.encodeURIComponent(gadget.props.element.getElementsByTagName('input')[0].value),
        page: 'bookmark_dispatcher'
      };
      return gadget.getUrlFor(option_parameter)
        .push(function (url) {
          window.location.href = url;
        });
    });

}(window, RSVP, rJS));