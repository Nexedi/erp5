/*global window, rJS, RSVP, Handlebars, URI, console, jIO, document, Boolean */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function(window, rJS, RSVP, domsugar, URI, document, Boolean) {
  "use strict";

  rJS(window)
    .declareAcquiredMethod("getUrlForList", "getUrlForList")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareMethod("render", function () {
      var gadget = this;
      return gadget.updateHeader({
          page_title: 'European Technology Directory'
        })
        .push(function () {
          return gadget.renderPage();
        });
    })
    .declareJob("renderPage", function () {
      var gadget = this;
      return gadget.jio_allDocs({
          select_list: ["location"],
          query: 'portal_type:"publisher"'
        })
        .push(function (data_list) {
          var promise_list = [];
          data_list = data_list.data.rows.filter(data => data.value.location.coordinate_list.length > 0);
          promise_list = data_list.map(function(data) {
            return {
              command: "index",
              options: {
                jio_key: data.id,
                page: "eci_publisher"
              }
            };
          });
          gadget.data_list = data_list;
          return gadget.getUrlForList(promise_list);
        })
        .push(function(url_list) {
          var location_list = [],
            i;
          for (i = 0; i < gadget.data_list.length; i += 1) {
            gadget.data_list[i].value.location.href = url_list[i];
            location_list.push(gadget.data_list[i].value.location);
          }
          return gadget.declareGadget("gadget_erp5_eci_map.html", {
              "element": gadget.element.querySelector('.map_container')
            })
            .push(function(map_gadget) {
              return map_gadget.render(location_list);
            });
        })
        .push(function () {
           return gadget.changeState({
             "render_link": true
           });
        });
    })
    .onStateChange(function(modification_dict) {
      var gadget = this,
        solution_container = gadget.element.querySelector(
          '.solution-container'
        ),
        success_case_container = gadget.element.querySelector(
          '.success-case-container'
        ),
        provider_container = gadget.element.querySelector(
          '.provider-container'
        ),
        similar_solution_container = gadget.element.querySelector(
          '.similar-solution-container'
        );
      if (!modification_dict.render_link) {
        return;
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all([
            gadget.jio_allDocs({
              select_list: ['selection_domain_category', 'selection_domain_similar_solution'],
              query: 'portal_type:"solution"'
            }),
            gadget.jio_allDocs({
              select_list: ['selection_domain_industry'],
              query: 'portal_type:"success_case"'
            }),
            gadget.jio_allDocs({
              select_list: ['selection_domain_country'],
              query: 'portal_type:"publisher"'
            })
          ]);
        })
        .push(function (result_list) {
          function getUniqueArray(data_list, property) {
            var value = data_list.map((obj) => obj.value[property])
              .reduce((cur, prev) => cur.concat(prev))
              .filter(Boolean);
            return Array.from(new Set(value)).sort();
          }
          var category = getUniqueArray(result_list[0].data.rows, 'selection_domain_category'),
            success_case_industry = getUniqueArray(result_list[1].data.rows, 'selection_domain_industry'),
            provider_country = getUniqueArray(result_list[2].data.rows, 'selection_domain_country'),
            similar_solution = getUniqueArray(result_list[0].data.rows, 'selection_domain_similar_solution'),
            solution_promise_list,
            provider_promise_list,
            success_case_promise_list,
            similar_solution_promise_list;
          solution_promise_list = category.map(function(category) {
            return {
              command: 'store_and_change',
              options: {
                page: 'eci_solution_list',
                extended_search: 'selection_domain_category: "' + category + '"',
                field_listbox_begin_from: undefined
              }
            };
          });
          success_case_promise_list = success_case_industry.map(function(industry) {
            return {
              command: 'store_and_change',
              options: {
                page: 'eci_success_case_list',
                extended_search: 'selection_domain_industry: "' + industry + '"',
                field_listbox_begin_from: undefined
              }
            };
          });
          provider_promise_list = provider_country.map(function(country) {
            return {
              command: 'store_and_change',
              options: {
                page: 'eci_provider_list',
                extended_search: 'selection_domain_country: "' + country + '"',
                field_listbox_begin_from: undefined
              }
            };
          });
          similar_solution_promise_list = similar_solution.map(function(ss) {
            return {
              command: 'store_and_change',
              options: {
                page: 'eci_solution_list',
                extended_search: 'selection_domain_similar_solution: "' + ss + '"',
                field_listbox_begin_from: undefined
              }
            };
          });
          return RSVP.all([
            category,
            gadget.getUrlForList(solution_promise_list),
            success_case_industry,
            gadget.getUrlForList(success_case_promise_list),
            provider_country,
            gadget.getUrlForList(provider_promise_list),
            similar_solution,
            gadget.getUrlForList(similar_solution_promise_list)
          ]);
        })
        .push(function (result_list) {
          var i,
            category_count_promise_list,
            success_case_industry_count_promise_list,
            provider_country_count_promise_list,
            similar_solution_count_promise_list,
            dom_list = [],
            solution_element =  domsugar('section', {class: 'ui-content-section ui-body-c'}),
            success_element = domsugar('section', {class: 'ui-content-section ui-body-c'}),
            provider_element = domsugar('section', {class: 'ui-content-section ui-body-c'}),
            similar_solution_element = domsugar('section', {class: 'ui-content-section ui-body-c'});
          for (i = 0; i < result_list[0].length; i += 1) {
            dom_list.push(domsugar('li', [
              domsugar('a', {
                "data-value": result_list[0][i],
                href: result_list[1][i],
                text: result_list[0][i]
              },
              [
                domsugar('span', {
                  class: "ui-icon-spinner ui-btn-icon-notext"
                })
              ])
              ]));
          }
          domsugar(solution_container, [domsugar(solution_element, [domsugar('h1', {text: "Solutions"}), domsugar('ul', dom_list)])]);

          dom_list = [];
          for (i = 0; i < result_list[2].length; i += 1) {
            dom_list.push(domsugar('li', [
              domsugar('a', {
                "data-value": result_list[2][i],
                href: result_list[3][i],
                text: result_list[2][i]
              },
              [
                domsugar('span', {
                  class: "ui-icon-spinner ui-btn-icon-notext"
                })
              ])
              ]));
          }
          domsugar(success_case_container, [domsugar(success_element, [domsugar('h1', {text: "Success cases"}), domsugar('ul', dom_list)])]);

          dom_list = [];
          for (i = 0; i < result_list[4].length; i += 1) {
            dom_list.push(domsugar('li', [
              domsugar('span',{
                class: "fi fi-" + window.reverse_country_data[result_list[4][i]]
              }),
              domsugar('a', {
                "data-value": result_list[4][i],
                href: result_list[5][i],
                text: result_list[4][i]
              },
              [
                domsugar('span', {
                  class: "ui-icon-spinner ui-btn-icon-notext"
                })
              ])
              ]));
          }
          domsugar(provider_container, [domsugar(provider_element, [domsugar('h1', {text: "Providers"}), domsugar('ul', dom_list)])]);

          dom_list = [];
          for (i = 0; i < result_list[6].length; i += 1) {
            dom_list.push(domsugar('li', [
              domsugar('a', {
                "data-value": result_list[6][i],
                href: result_list[7][i],
                text: result_list[6][i]
              },
              [
                domsugar('span', {
                  class: "ui-icon-spinner ui-btn-icon-notext"
                })
              ])
              ]));
          }
          domsugar(similar_solution_container, [domsugar(similar_solution_element, [domsugar('h1', {text: "Similar solutions"}), domsugar('ul', dom_list)])]);

          var all_promise_list = new RSVP.Queue(),
            max_length = Math.max(
              result_list[0].length,
              result_list[2].length,
              result_list[4].length,
              result_list[6].length),
           data;
          function createSearchMethod(query, data, container) {
            return function () {
              return gadget.jio_allDocs({
                query: query
              })
                .push(function (result) {
                  container.querySelector('a[data-value="' + data + '"]').textContent = data + ' (' + result.data.total_rows + ')';
                  return RSVP.delay(10);
                });
            }
          }

          for (i = 0; i < max_length; i += 1) {
            if (i < result_list[0].length) {
              data = result_list[0][i];
              all_promise_list
                .push(createSearchMethod('(portal_type:"solution") AND (selection_domain_category: "' + data + '")', data, solution_container));
            }
            if (i < result_list[2].length) {
              data = result_list[2][i];
              all_promise_list
                .push(createSearchMethod('(portal_type:"success_case") AND (selection_domain_industry: "' + data + '")', data, success_case_container));
            }
            if (i < result_list[4].length) {
              data = result_list[4][i];
                all_promise_list
                .push(createSearchMethod('(portal_type:"publisher") AND (selection_domain_country: "' + data + '")', data, provider_container));
            }
            if (i < result_list[6].length) {
              data = result_list[6][i];
                all_promise_list
                .push(createSearchMethod('(portal_type:"solution") AND (selection_domain_similar_solution: "' + data + '")', data, similar_solution_container));
            }
          }
          return all_promise_list;
        });
    });
}(window, rJS, RSVP, domsugar, URI, document, Boolean));