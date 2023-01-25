/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, RSVP, rJS, Handlebars, jIO) {
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
    .declareAcquiredMethod('getUrlParameter','getUrlParameter')
    .declareMethod('render', function (options) {
      var gadget = this,
          i,
          begin_from,
          sort_list_json,
          extended_search;
      return RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.getUrlParameter('field_listbox_begin_from'),
            gadget.getUrlParameter('field_listbox_sort_list:json'),
            gadget.getUrlParameter('extended_search')
          ]);
        })
        .push(function (result_list) {
          begin_from = parseInt(result_list[0] || '0', 10) || 0;
          sort_list_json = result_list[1];
          extended_search = result_list[2];
          return gadget.jio_get(options.value.jio_key);
        })
        .push(function (solution) {
          var promise_list = [];
          gadget.solution = solution;
          if (solution.logo_url === "N/A" || solution.logo_url === "") {
            solution.logo_url = 'gadget_erp5_eci_camera.png?format=png';
          }
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_floss_software: "' + solution.selection_domain_floss_software + '"',
              field_listbox_begin_from: undefined
            }
          });
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_commercial_support_available: "' + solution.selection_domain_commercial_support_available + '"',
              field_listbox_begin_from: undefined
            }
          });
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_country: "' + solution.selection_domain_country + '"',
              field_listbox_begin_from: undefined
            }
          });
          var query_string = new URI(options.value.query).query(true).query;
          if (extended_search) {
            if (query_string) {
              query_string = '(' + query_string + ') AND (' + extended_search + ')';
            } else {
              query_string = extended_search;
            }
          }

          promise_list.push({
            command: 'index',
            options : {
              jio_key: options.value.jio_key,
              selection_index: begin_from + options.value.index,
              "sort_list:json": sort_list_json,
              query: query_string
            }
          });
          promise_list = promise_list.concat(solution.selection_domain_category.map(function (data) {
            return {
              command: 'store_and_change',
              options : {
                extended_search: 'selection_domain_category: "' + data + '"',
                field_listbox_begin_from: undefined
              }
            };
          }));
          return gadget.getUrlForList(promise_list);
        })
        .push(function (url_list) {
          var i;
          gadget.solution.floss_software_search_url = url_list[0];
          gadget.solution.support_search_url = url_list[1];
          gadget.solution.country_search_url = url_list[2];
          gadget.solution.country_code = window.reverse_country_data[gadget.solution.selection_domain_country[0]];
          gadget.solution.entry_url = url_list[3];
          gadget.solution.category_with_url_list = [];
          for (i = 0; i < gadget.solution.selection_domain_category.length; i += 1) {
            gadget.solution.category_with_url_list.push({
              title: gadget.solution.selection_domain_category[i],
              url: url_list[i + 4]
            });
          }
          gadget.element.querySelector(".display-widget-in-listbox").innerHTML = display_widget_table(gadget.solution);
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));

