/*globals window, RSVP, rJS, Handlebars, jIO, QueryFactory, URI*/
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
    .declareAcquiredMethod('getUrlParameter', 'getUrlParameter')
    .declareMethod('render', function (options) {
      var gadget = this,
          i,
          begin_from,
          sort_list_json,
          extended_search,
          search_criteria,
          new_solution_list,
          solution_uid;
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
        .push(function (provider) {
          var promise_list = [];
          gadget.provider = provider;
          if (provider.logo_url === "N/A" || provider.logo_url === "") {
            provider.logo_url = 'gadget_erp5_eci_camera.png?format=png';
          }
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_country: "' + provider.selection_domain_country + '"',
              field_listbox_begin_from: undefined
            }
          });
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_type: "' + provider.selection_domain_type + '"',
              field_listbox_begin_from: undefined
            }
          });
          var query_string = new URI(options.value.query).query(true).query;
          if (extended_search) {
            search_criteria = QueryFactory.create(extended_search.trim());
            if (search_criteria.query_list) {
              for (i = 0; i < search_criteria.query_list.length; i += 1) {
                if (search_criteria.query_list[i].key === "selection_domain_category") {
                  search_criteria = search_criteria.query_list[i];
                  break;
                }
              }
            }
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
          new_solution_list = [];
          for (i = 0; i < provider.solution_list.length; i += 1) {
            if (search_criteria && search_criteria.key == 'selection_domain_category') {
              if (provider.solution_list[i].category_list.indexOf(search_criteria.value) == -1) {
                continue;
              }
            }
            new_solution_list.push(provider.solution_list[i]);
            solution_uid = "software_" + provider.solution_list[i].title.replace(/\?/g, '.');
            promise_list.push({
              command: "index",
              options: {
                jio_key: solution_uid,
                page: "eci_solution"
              }
            });
            promise_list = promise_list.concat(provider.solution_list[i].category_list.map(function (data) {
              return {
                command: 'store_and_change',
                options : {
                  extended_search: 'selection_domain_category: "' + data + '"',
                  field_listbox_begin_from: undefined
                }
              };
            }));
          }
          provider.solution_list = new_solution_list;
          return gadget.getUrlForList(promise_list);
        })
        .push(function (url_list) {
          var i, cursor = 2, j;
          gadget.provider.country_search_url = url_list[0];
          gadget.provider.type_search_url = url_list[1];
          gadget.provider.entry_url = url_list[2];
          for (i = 0; i < gadget.provider.solution_list.length; i += 1) {
            cursor += 1;
            gadget.provider.solution_list[i].solution_url = url_list[cursor];
            gadget.provider.solution_list[i].category_search_url_list = [];
            for (j = 0; j < gadget.provider.solution_list[i].category_list.length; j += 1) {
              cursor += 1;
              gadget.provider.solution_list[i].category_search_url_list.push({
                'title': gadget.provider.solution_list[i].category_list[j],
                'type_search_url': url_list[cursor]
              });
            }
          }
          gadget.element.querySelector(".display-widget-in-listbox").innerHTML = display_widget_table(gadget.provider);
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));

