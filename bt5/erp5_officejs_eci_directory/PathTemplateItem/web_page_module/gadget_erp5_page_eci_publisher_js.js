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
    .declareAcquiredMethod('getUrlForList', 'getUrlForList')
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .allowPublicAcquisition('updateHeader', function () {
      return;
    })
    .declareMethod('render', function (options) {
      var gadget = this,
        publisher;

      return gadget.jio_get(options.jio_key)
        .push(function (result) {
          var wiki_list = [];
          publisher = result;
          gadget.location = result.location;
          publisher.solution_list.map(function (solution) {
            if (EMPTY.includes(solution.wikipedia_url)) {
              delete solution.wikipedia_url;
            } else {
              wiki_list.push(
                new RSVP.Queue()
                .push(function () {
                  return jIO.util.ajax({
                    type: "GET",
                    headers: {
                      "api-user-agent": "https://www.nexedi.com/contact"
                    },
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
          return gadget.getUrlForList([{
              command: 'store_and_change',
              options: {
                extended_search: 'selection_domain_country: "' + publisher.selection_domain_country[0] + '"',
                field_listbox_begin_from: undefined,
                page: "eci_provider_list"
              }
            }
          ]);
        })
        .push(function (url_list) {
          publisher.country_search_url = url_list[0];
          gadget.element.querySelector(".display-widget").innerHTML = display_widget_table(publisher);
          return RSVP.all([
            gadget.getUrlForList([
              {command: "history_previous"},
              {command: 'selection_previous'},
              {command: 'selection_next'}
            ]),
            gadget.getUrlParameter('selection_index')
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: publisher.title,
            back_url: url_list[0][0],
            previous_url: url_list[1] ? url_list[0][1] : '',
            next_url: url_list[1] ? url_list[0][2] : ''
          });
        })
        .push(function () {
          var promise_list = [],
            i,
            solution_container = gadget.element.querySelector('.solution-container'),
            div;
          for (i = 0; i < publisher.solution_list.length; i += 1) {
            div = document.createElement('div');
            solution_container.appendChild(div);
            promise_list.push(gadget.declareGadget("gadget_erp5_page_eci_solution.html", {
              "element": div
            }));
          }
          return RSVP.all(promise_list);
        })
        .push(function (result_list) {
          var promise_list = [],
            i;
          for (i = 0; i < publisher.solution_list.length; i += 1) {
            promise_list.push(result_list[i].render({
              jio_key: "software_" + publisher.solution_list[i].title.replace(/\?/g, '.'),
              display_provider: false
            }));
          }
        })
        .push(function () {
          return gadget.renderMap();
        });
    })
    .declareJob("renderMap", function () {
      var gadget = this;
      if (!gadget.location) {
        return;
      }
      return gadget.declareGadget("gadget_erp5_eci_map.html", {
          "element": gadget.element.querySelector('.map_container')
        })
        .push(function (map_gadget) {
          return map_gadget.render([gadget.location]);
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));