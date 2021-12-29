/*global window, rJS, RSVP, Array, SimpleQuery, Query, ComplexQuery, domsugar */
/*jslint nomen: true, indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, Array, SimpleQuery, Query, ComplexQuery,
           domsugar) {
  "use strict";

  var color_list = ["#CCA08D", "#58ADC4", "#F9B39B", "#B75937",
                    "#E3663D", "#C69580", "#68B5CA", "#F8A78B"];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    .declareAcquiredMethod("redirect", "redirect")
    .declareAcquiredMethod("getUrlParameter", "getUrlParameter")
    .allowPublicAcquisition("chartItemClick", function (params) {
      var gadget = this;
      return gadget.getSearchCriteria(params[0][0], params[0][1])
        .push(function (result) {
          return gadget.redirect({
            command: 'change',
            options: {
              extended_search: result
            }
          });
        });
    })
    .declareMethod('getSearchCriteria', function (a, b) {
      var key, value;
      if (this.state.extended_search_mapping.hasOwnProperty(b)) {
        key = this.state.extended_search_mapping[b].value;
        value = a;
      } else {
        key = this.state.extended_search_mapping[a].key;
        value = this.state.extended_search_mapping[a].value;
      }
      return Query.objectToSearchText(
        new SimpleQuery({
          operator: "",
          key: key,
          type: "simple",
          value: value
        })
      );
    })
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (options) {
      var group_by,
        gadget = this,
        query_by = options.query_by,
        select_list = options.select_list || [],
        query_list = [],
        jio_query_list = [],
        sub_query_list = [],
        column_list = options.layout.x.column_list,
        domain_id = options.layout.x.domain_id,
        data = {
          x: options.layout.x.key,
          title: options.title || options.layout.x.title,
          x_title: options.layout.x.title,
          y_title: options.layout.y.title,
          column_list: column_list,
          extended_search_mapping: {},
          graph_gadget: "unsafe/gadget_field_graph_echarts.html"
        },
        performance_mapping = {
          "translated_simulation_state_title": [
            "simulation_state", "getTranslatedSimulationStateTitle"
          ]
        },
        domain_list,
        i,
        j;

      if ("object" === typeof options.group_by &&
          Array.isArray(options.group_by) &&
          options.group_by.length === 0) {
        group_by.push(query_by);
      } else if (!Array.isArray(options.group_by)) {
        group_by = [options.group_by || options.layout.x.key];
      } else {
        group_by = options.group_by;
      }

      for (i = 0; i < group_by.length; i += 1) {
        if (performance_mapping.hasOwnProperty(group_by[i])) {
          options.layout.x.key = performance_mapping[group_by[i]][1];
          data.x = options.layout.x.key;
          group_by[i] = performance_mapping[group_by[i]][0];
        }
      }

      data.y = "count(*)";

      for (i in query_by) {
        if (query_by.hasOwnProperty(i)) {
          if (Array.isArray(query_by[i])) {
            for (j = 0; j < query_by[i].length; j += 1) {
              sub_query_list.push(new SimpleQuery({
                operator: "",
                key: i,
                type: "simple",
                value: query_by[i][j]
              }));
            }
            jio_query_list.push(new ComplexQuery({
              operator: "OR",
              type: "complex",
              query_list: sub_query_list
            }));
          } else {
            jio_query_list.push(new SimpleQuery({
              operator: "",
              key: i,
              type: "simple",
              value: query_by[i]
            }));
          }
        }
      }

      select_list = select_list.concat(
        [data.y, options.layout.x.key].filter(function (el, index) {
          return select_list.indexOf(el) !== index;
        })
      );

      if (domain_id) {
        domain_list = options.layout.x.domain_list || [];
        for (i = 0; i < domain_list.length; i += 1) {
          data.extended_search_mapping[column_list[i]] = {
            "key": "selection_domain_" + domain_id,
            "value": domain_list[i]
          };
          sub_query_list.push(new SimpleQuery({
            key: "selection_domain_" + domain_id,
            operator: "",
            type: "simple",
            value: domain_list[i]
          }));
          query_list.push({
            "query": Query.objectToSearchText(new ComplexQuery({
              operator: "AND",
              query_list: jio_query_list.concat(sub_query_list),
              type: "complex"
            })),
            "list_method_template": options.list_method_template,
            "list_method": options.list_method,
            "relative_url": options.relative_url,
            "group_by": group_by,
            "select_list": select_list
          });
          sub_query_list = [];
        }
        data.query_list = query_list;
      } else if (group_by instanceof Array && group_by.length > 1) {
        data.query = {
          "query": Query.objectToSearchText(new ComplexQuery({
            operator: "AND",
            query_list: jio_query_list,
            type: "complex"
          })),
          "list_method_template": options.list_method_template,
          "list_method": options.list_method,
          "relative_url": options.relative_url,
          "group_by": group_by,
          "select_list": select_list.concat(group_by)
        };
      } else {
        data.extended_search_mapping[options.title] = {
          "key": group_by,
          "value": options.group_by
        };
        data.query = {
          "query": Query.objectToSearchText(new ComplexQuery({
            operator: "AND",
            query_list: jio_query_list,
            type: "complex"
          })),
          "list_method_template": options.list_method_template,
          "list_method": options.list_method,
          "relative_url": options.relative_url,
          "group_by": group_by,
          "select_list": select_list
        };
      }
      return new RSVP.Queue(RSVP.all([
          gadget.getUrlParameter('extended_search'),
          gadget.getUrlParameter('graphic_select_id')
        ]))
        .push(function (result_list) {
          var extended_search = result_list[0],
              graphic_select_id = result_list[1];
          if (extended_search) {
            jio_query_list.push(Query.parseStringToObject(extended_search));
          }
          return gadget.changeState(data);
        });
    })
    .onEvent("click", function (evt) {
      var gadget = this,
        restore_filter_input = gadget.element.querySelectorAll("input")[0];
      if (evt.target === restore_filter_input) {
        evt.preventDefault();
        restore_filter_input.disabled = true;
        restore_filter_input.classList.add("ui-disabled");
        return gadget.redirect({
          command: "change",
          options: {
            extended_search: undefined,
            graphic_type: undefined
          }
        });
      }
    })
    .onStateChange(function (modification_dict) {
      var i,
        gadget = this,
        query_list = modification_dict.query_list || [],
        queue_list = [
          gadget.declareGadget(modification_dict.graph_gadget, {
            scope: "graph",
            sandbox: "iframe",
            element: gadget.element.querySelector(".wrap")
          })
        ];

      if (gadget.state.query) {
        queue_list.push(gadget.jio_allDocs(gadget.state.query));
      }
      for (i = 0; i < query_list.length; i += 1) {
        queue_list.push(gadget.jio_allDocs(query_list[i]));
      }
      return new RSVP.Queue(RSVP.all(queue_list))
        .push(function (result_list) {
          var bar_chart = gadget.element.querySelector(".wrap"),
            loader = gadget.element.querySelector(".graph-spinner"),
            graph_gadget = result_list[0],
            data_mapping = {},
            label_list = [],
            state_list = [],
            data_list = [],
            value_list,
            row_list,
            label,
            state,
            j;
          loader.style.display = "none";
          bar_chart.style.display = "block";

          function avoidFunction(el) {
            return el && !el.match(/^\D+\((\w+|\*)\)$/);
          }
          if (gadget.state.query &&
              "object" === typeof gadget.state.query &&
              gadget.state.query.select_list.filter(avoidFunction).length <= 1) {
            row_list = result_list[1].data.rows;
            data_list = [{
              "value_dict": {
                '0': [],
                '1': []
              },
              colors: [],
              type: "pie",
              title: gadget.state.x_title || gadget.state.title
            }];
            for (i = 0; i < row_list.length; i += 1) {
              data_list[0].value_dict['0'].push(
                row_list[i].value[gadget.state.x]
              );
              data_list[0].value_dict['1'].push(
                row_list[i].value[gadget.state.y]
              );
              data_list[0].colors.push(color_list[i]);
            }
          } else if (gadget.state.query && gadget.state.query.select_list.length > 1) {
            for (i = 1; i < result_list.length; i += 1) {
              for (j = 0; j < result_list[i].data.rows.length; j += 1) {
                label = result_list[i].data.rows[j].value[gadget.state.query.select_list[0]];
                if (label && !data_mapping.hasOwnProperty(label)) {
                  data_mapping[label] = {};
                  if (label_list.indexOf(label) === -1) {
                    label_list.push(label);
                  }
                }
                state = result_list[i].data.rows[j].value[gadget.state.query.select_list[1]];
                if (state) {
                  data_mapping[label][state] =
                    result_list[i].data.rows[j].value[gadget.state.y];
                }
                if (state_list.indexOf(state) === -1) {
                  state_list.push(state);
                }
              }
            }

            for (i = 0; i < state_list.length; i += 1) {
              value_list = [];
              for (j = 0; j < label_list.length; j += 1) {
                value_list.push(data_mapping[label_list[j]][state_list[i]] || 0);
              }
              data_list.push({
                value_dict: {
                  0: label_list,
                  1: value_list
                },
                colors: [color_list[i]],
                type: "bar",
                title: state_list[i]
              });
            }

          } else if (gadget.state.column_list.length > 0) {
            for (i = 0; i < gadget.state.column_list.length; i += 1) {
              label = gadget.state.column_list[i];
              if (label && !data_mapping.hasOwnProperty(label)) {
                data_mapping[label] = {};
                if (label_list.indexOf(label) === -1) {
                  label_list.push(label);
                }
              }
            }

            for (i = 1; i < result_list.length; i += 1) {
              for (j = 0; j < result_list[i].data.rows.length; j += 1) {
                state = result_list[i].data.rows[j].value[gadget.state.x];
                if (state) {
                  data_mapping[label_list[i - 1]][state] =
                    result_list[i].data.rows[j].value[gadget.state.y];
                }
                if (state_list.indexOf(state) === -1) {
                  state_list.push(state);
                }
              }
            }

            for (i = 0; i < state_list.length; i += 1) {
              value_list = [];
              for (j = 0; j < label_list.length; j += 1) {
                value_list.push(data_mapping[label_list[j]][state_list[i]] || 0);
              }
              data_list.push({
                value_dict: {
                  0: label_list,
                  1: value_list
                },
                colors: [color_list[i]],
                type: "bar",
                title: state_list[i]
              });
            }
          }
          if (data_list.length === 0) {
            return domsugar(gadget.element, [
              domsugar("p", {"text": "No data"})
            ]);
          }
          return graph_gadget.render({
            value: {
              data: data_list,
              layout: {
                axis_dict : {
                  '0': {"title": gadget.state.x_title},
                  '1': {
                    "title": gadget.state.y_title || "Quantity",
                    "value_type": "number"
                  }
                },
                title: ""
              }
            }
          });
        })
        .push(function () {
          var restore_filter_input = gadget.element.querySelectorAll("input")[0];
          restore_filter_input.disabled = false;
          restore_filter_input.classList.remove("ui-disabled");
        });
    });

}(window, rJS, RSVP, Array, SimpleQuery, Query, ComplexQuery, domsugar));