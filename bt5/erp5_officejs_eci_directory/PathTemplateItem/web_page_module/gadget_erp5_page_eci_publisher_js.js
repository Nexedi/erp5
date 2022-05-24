/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var EMPTY = ["N/A", "", 0],
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
        entry.image = 'gadget_erp5_eci_camera.png?format=png';
        entry.image_class = "custom-placeholder";
      }
    }
    return case_list;
  }

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')

    .declareMethod('render', function (options) {
      var gadget = this,
        publisher;

      return gadget.jio_get(options.jio_key)
        .push(function (result) {
          var wiki_list = [];
          publisher = result;
          publisher.solution_list.map(function (solution) {
            if (EMPTY.includes(solution.commercial_support_available)) {
              delete solution.commercial_support_available;
            }
            if (EMPTY.includes(solution.logo_url)) {
              solution.logo_url = "gadget_erp5_eci_camera.png?format=png";
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
                      type: "GET",
                      headers: {"api-user-agent": "https://www.nexedi.com/contact"},
                      url: "https://en.wikipedia.org/api/rest_v1/page/summary/" + solution.wikipedia_url.split("/").pop()
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
          gadget.element.querySelector(".display-widget")
            .innerHTML = display_widget_table(publisher);
          return gadget.getUrlFor({command: "history_previous"});
        })
        .push(function (url) {
          return gadget.updateHeader({
            page_title: publisher.title,
            back_url: url
          });
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));
