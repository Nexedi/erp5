/*globals window, RSVP, rJS, Handlebars, QueryFactory*/
/*jslint indent: 2, nomen: true, maxlen: 180*/
(function (window, RSVP, rJS, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getUrlForList', 'getUrlForList')
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")

    .declareMethod('render', function (options) {
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_get(options.value.jio_key),
            gadget.getUrlParameter('extended_search')
          ]);
        })
        .push(function (result_list) {
          var i,
            j,
            promise_list = [],
            solution = result_list[0],
            search = result_list[1],
            search_operator,
            search_list = [];
          gadget.solution = solution;
          if (solution.image_url === "N/A" || solution.image_url === "") {
            solution.image_url = 'gadget_erp5_eci_camera.png?format=png';
            solution.image_class = "custom-placeholder";
          }
          promise_list.push({
            command: "index",
            options: {
              jio_key: solution.publisher_id,
              page: "eci_publisher"
            }
          });
          promise_list.push({
            command: "index",
            options: {
              jio_key: solution.uid,
              page: "eci_solution"
            }
          });
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_country: "' + solution.selection_domain_country[0] + '"',
              field_listbox_begin_from: undefined
            }
          });
          if (search) {
            search = QueryFactory.create(search.trim());
            search_operator = search.operator;
            if (search.query_list) {
              for (i = 0; i < search.query_list.length; i += 1) {
                if (search.query_list[i].key.startsWith("selection_domain_reference_")) {
                  search_list.push({
                    key: search.query_list[i].key.substring("selection_domain_reference_".length),
                    value: search.query_list[i].value
                  });
                }
              }
            } else {
              if (search.key.startsWith("selection_domain_reference_")) {
                search_list.push({
                  key: search.key.substring("selection_domain_reference_".length),
                  value: search.value
                });
              }
            }
          }
          var new_reference_list = [],
            found;
          for (i = 0; i < solution.reference_list.length; i += 1) {
            found = false;
            for (j = 0; j < search_list.length; j += 1) {
              if (solution.reference_list[i][search_list[j].key] === search_list[j].value) {
                search_list[j].found = true;
              } else {
                search_list[j].found = false;
              }
            }
            if (search_list.length) {
              if (search_operator === "OR") {
                // find one true
                found = search_list.filter(search => search.found).length > 0;
              } else {
                // find 0 false
                found = search_list.filter(search => !search.found).length == 0;
              }
            } else {
              found = true;
            }
            if (!found) {
              continue;
            }
            new_reference_list.push(solution.reference_list[i]);
            promise_list.push({
              command: "store_and_change",
              options: {
                extended_search: 'selection_domain_reference_industry: "' + solution.reference_list[i].industry + '"',
                page: "eci_reference_list",
                field_listbox_begin_from: undefined
              }
            });
            promise_list.push({
              command: "store_and_change",
              options: {
                extended_search: 'selection_domain_reference_country: "' + solution.reference_list[i].country + '"',
                page: "eci_reference_list",
                field_listbox_begin_from: undefined
              }
            });
          }
          solution.reference_list = new_reference_list;

          return gadget.getUrlForList(promise_list);
        })
        .push(function (url_list) {
          var i, cursor = 0;
          gadget.solution.provider_url = url_list[0];
          gadget.solution.solution_url = url_list[1];
          gadget.solution.country_search_url = url_list[2];
          gadget.solution.country_code = window.reverse_country_data[gadget.solution.selection_domain_country[0]];
          cursor = 3;
          for (i = 0; i < gadget.solution.reference_list.length; i += 1) {
            gadget.solution.reference_list[i].industry_search_url = url_list[cursor + i * 2];
            gadget.solution.reference_list[i].country_search_url = url_list[cursor + i * 2 + 1];
          }
          gadget.element.querySelector(".display-widget-in-listbox").innerHTML = display_widget_table(gadget.solution);
        });
    });
}(window, RSVP, rJS, Handlebars));
