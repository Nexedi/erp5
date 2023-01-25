/*globals window, RSVP, rJS, Handlebars, jIO*/
/*jslint indent: 2, nomen: true, maxlen: 200*/
(function (window, RSVP, rJS, Handlebars, jIO) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    display_widget_table = Handlebars.compile(
      templater.getElementById("display-template").innerHTML
    );

  function clean(case_list, software_website, software_title, publisher_website, publisher_title) {
    var emptry_string = "",
      i,
      len,
      entry;
    if (! case_list) {
      return [];
    }
    for (i = 0, len = case_list.length; i < len; i += 1) {
      entry = case_list[i];
      if (entry.constructor !== Object) {
        continue;
      }
      if (entry.image === "N/A" || entry.image === "") {
        entry.image = 'gadget_erp5_eci_camera.png?format=png';
        entry.image_class = "custom-placeholder";
      }
      entry.software_website = software_website || emptry_string;
      entry.software = software_title || emptry_string;
      entry.publisher_website = publisher_website || emptry_string;
      entry.publisher = publisher_title  || emptry_string;
    }
    return case_list;
  }

  rJS(window)
    .declareAcquiredMethod('updateHeader', 'updateHeader')
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod('getUrlForList', 'getUrlForList')
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.jio_get(options.jio_key)
        .push(function (solution) {
          var promise_list = [];
          if (solution.logo_url === "N/A" || solution.logo_url === "") {
            solution.logo_url = 'gadget_erp5_eci_camera.png?format=png';
          }
          solution.success_case_list = clean(
            solution.success_case_list,
            solution.website_url,
            solution.title,
            solution.publisher_website,
            solution.publisher
          );
          gadget.solution = solution;
          solution.display_provider = options.display_provider === false ? false: true;
          promise_list = solution.selection_domain_category.map(function (data) {
            return {
              command: 'store_and_change',
              options : {
                extended_search: 'selection_domain_category: "' + data + '"',
                page: "eci_solution_list",
                field_listbox_begin_from: undefined
              }
            };
          });
          promise_list.push({
            command: "store_and_change",
            options : {
              extended_search: 'selection_domain_country: "' + solution.selection_domain_country[0] + '"',
              page: "eci_solution_list",
              field_listbox_begin_from: undefined
            }
          });
          return gadget.getUrlForList(promise_list);
        })
        .push(function (url_list) {
          var i;
          gadget.solution.category_with_url_list = [];
          gadget.solution.country_code = window.reverse_country_data[gadget.solution.selection_domain_country[0]];
          for (i = 0; i < gadget.solution.selection_domain_category.length; i += 1) {
            gadget.solution.category_with_url_list.push({
              title: gadget.solution.selection_domain_category[i],
              url: url_list[i]
            });
          }
          gadget.solution.country_search_url = url_list[i];
          gadget.element.querySelector(".display-widget").innerHTML = display_widget_table(gadget.solution);
          return RSVP.all([
            gadget.getUrlForList([
              {command: "history_previous"},
              {command: 'selection_previous'},
              {command: 'selection_next'}
            ]),
            gadget.getUrlParameter('selection_index')
          ]);
        })
        .push(function (result_list) {
          return gadget.updateHeader({
            page_title: gadget.solution.title,
            back_url: result_list[0][0],
            previous_url: result_list[1] ? result_list[0][1] : '',
            next_url: result_list[1] ? result_list[0][2] : ''
          });
        });
    });
}(window, RSVP, rJS, Handlebars, jIO));

