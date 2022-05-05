/*globals window, RSVP, rJS, Handlebars*/
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
    .declareAcquiredMethod('getUrlFor', 'getUrlFor')
    .declareAcquiredMethod('getUrlForList', 'getUrlForList')

    .declareMethod('render', function (options) {
      var gadget = this;
      return gadget.jio_get(options.value.jio_key)
        .push(function (success_case) {
          var promise_list = [];
          gadget.success_case = success_case;
          if (success_case.image_url === "N/A" || success_case.image_url === "") {
            success_case.image_url = 'gadget_erp5_eci_camera.png?format=png';
            success_case.image_class = "custom-placeholder";
          }
          promise_list.push({
            command: "index",
            options: {
              jio_key: success_case.publisher_id,
              page: "eci_publisher"
            }
          });
          promise_list.push({
            command: "index",
            options: {
              jio_key: success_case.software_id,
              page: "eci_solution"
            }
          });
          promise_list.push({
            command: 'store_and_change',
            options : {
              extended_search: 'selection_domain_publisher_country: "' + success_case.selection_domain_publisher_country[0] + '"',
              field_listbox_begin_from: undefined
            }
          });
          promise_list = promise_list.concat(success_case.selection_domain_industry.map(function (data) {
            return {
              command: 'store_and_change',
              options : {
                extended_search: 'selection_domain_industry: "' + data + '"',
                page: "eci_success_case_list",
                field_listbox_begin_from: undefined
              }
            };
          }));

          promise_list = promise_list.concat(success_case.selection_domain_category.map(function (data) {
            return {
              command: 'store_and_change',
              options : {
                extended_search: 'selection_domain_category: "' + data + '"',
                page: "eci_success_case_list",
                field_listbox_begin_from: undefined
              }
            };
          }));
          return gadget.getUrlForList(promise_list);
        })
        .push(function (url_list) {
          var i, cursor = 0;
          gadget.success_case.provider_url = url_list[0];
          gadget.success_case.solution_url = url_list[1];
          gadget.success_case.publisher_country_code = window.reverse_country_data[gadget.success_case.selection_domain_publisher_country[0]];
          gadget.success_case.publisher_country_search_url = url_list[2];
          cursor = 3;
          gadget.success_case.country_with_url_list = [];
          gadget.success_case.industry_with_url_list = [];
          gadget.success_case.category_with_url_list = [];

          for (i = 0; i < gadget.success_case.selection_domain_country.length; i += 1) {
            gadget.success_case.country_with_url_list.push({
              title: gadget.success_case.selection_domain_country[i],
              country_code: gadget.success_case.country_code
            });
          }

          for (i = 0; i < gadget.success_case.selection_domain_industry.length; i += 1) {
            gadget.success_case.industry_with_url_list.push({
              title: gadget.success_case.selection_domain_industry[i],
              url: url_list[i + cursor]
            });
          }

          cursor += i;
          for (i = 0; i < gadget.success_case.selection_domain_category.length; i += 1) {
            gadget.success_case.category_with_url_list.push({
              title: gadget.success_case.selection_domain_category[i],
              url: url_list[i + cursor]
            });
          }
          gadget.element.querySelector(".display-widget-in-listbox").innerHTML = display_widget_table(gadget.success_case);
        });
    });
}(window, RSVP, rJS, Handlebars));
