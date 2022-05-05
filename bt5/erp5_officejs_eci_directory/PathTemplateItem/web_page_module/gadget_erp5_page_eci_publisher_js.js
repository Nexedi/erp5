/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 100*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var WIKI_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/",
    EMPTY = ["N/A", "", 0],
    FALLBACK_SOFTWARE_LOGO_PATH = "gadget_erp5_afs_camera.png?format=png",
    GET = "GET",
    HEADERS_DICT = {"api-user-agent": "https://www.nexedi.com/contact"},
    gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  function clean(case_list) {
    var i,
      len,
      entry;
    for (i = 0, len = case_list.length; i < len; i += 1) {
      entry = case_list[i];
      if (entry.image === "N/A" || entry.image === "") {
        entry.image = 'gadget_erp5_afs_camera.png?format=png';
        entry.image_class = "custom-placeholder";
      }
    }
    return case_list;
  }

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')

    .declareMethod('render', function (options) {
      var gadget = this;

      return gadget.jio_get(options.jio_key)
        .push(function (publisher) {
          var wiki_list = [];
          publisher.solution_list.map(function (solution) {
            if (EMPTY.includes(solution.commercial_support_available)) {
              delete solution.commercial_support_available;
            }
            if (EMPTY.includes(solution.logo_url)) {
              solution.logo_url = FALLBACK_SOFTWARE_LOGO_PATH;
            }
            if (EMPTY.includes(solution.success_case_list) ||
              EMPTY.includes(solution.success_case_list.length)
            ) {
              delete solution.success_case_list;
            } else {
              solution.success_case_list = solution.success_case_list
                .filter(function (entry) {
                  if (!EMPTY.includes(entry.title)) {
                    return entry;
                  }
                });
              solution.success_case_list = clean(solution.success_case_list);
            }
            if (EMPTY.includes(solution.wikipedia_url)) {
              delete solution.wikipedia_url;
            } else {
              wiki_list.push(
                new RSVP.Queue()
                  .push(function () {
                    return jIO.util.ajax({
                      type: GET,
                      headers: HEADERS_DICT,
                      url: WIKI_URL + solution.wikipedia_url.split("/").pop()
                    });
                  })
                  .push(function (my_content) {
                    return JSON.parse(
                      my_content.target.response || my_content.target.responseText
                    ).extract;
                  }, function () {
                    return undefined;
                  })
              );
            }
          });
          return new RSVP.Queue()
            .push(function () {
              return RSVP.all(wiki_list);
            })
            .push(function (my_wiki_list) {
              var i, len;
              if (my_wiki_list && my_wiki_list.length > 0) {
                for (i = 0, len = publisher.solution_list.length; i < len; i += 1) {
                  if (publisher.solution_list[i].wikipedia_url) {
                    publisher.solution_list[i].wikipedia_description = my_wiki_list[i];
                  }
                }
              }
              return publisher;
            });
        })
        .push(function (my_publisher) {
          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(my_publisher);

          return gadget.updateHeader({page_title: my_publisher.title});
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));
