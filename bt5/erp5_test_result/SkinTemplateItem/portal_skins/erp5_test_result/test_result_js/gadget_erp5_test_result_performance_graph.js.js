/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, console */
(function (window, rJS, RSVP) {
  "use strict";

  var WIDGET_GRAPH_URL = "../unsafe/gadget_officejs_widget_graph_plotly.html";

  function getDateAsString(date) {
    var date_string = "" + date.getFullYear() + "-",
        month = date.getMonth() + 1,
        day = date.getDate();
    if (month < 10) {
      date_string = date_string + "0";
    }
    date_string = date_string  + month + "-";
    if (day < 10) {
      date_string = date_string + "0";
    }
    date_string = date_string  + day;
    return date_string;
  }

  function getCheckDateAndRefreshGraphFunction(gadget) {
    return function checkDateAndRefreshGraph() {
      var from_date, at_date, i;
      from_date = gadget.element.querySelector('[name="from_date"]').value;
      at_date = gadget.element.querySelector('[name="at_date"]').value;
      if (at_date !== "" && from_date !== "") {
        console.log("will need to get data");
        return gadget.jio_allDocs({
          "list_method_template": gadget.property_dict.option_dict.list_method_template,
          "query": '( delivery.start_date: >= "' + from_date + '" AND delivery.start_date: < "' + at_date + '" )',
          "limit": [],
          "select_list": [],
          "sort_on": []
        })
        .push(function (data_list) {
          console.log('data_list', data_list);
          var graph_data_list = [],
              revision, line_list = data_list.data.rows, value, i, j,
              property_list = [];
          if (line_list.length !== 0) {
            Object.keys(line_list[0].value).forEach(function (property) {
              if (property !== "revision") {
                property_list.push(property);
              }
            });
            if (property_list.length !== 0) {
              property_list.forEach(function (property) {
                var i, data = {};
                console.log("property", property);
                data.type = "scatter";
                data.title = property;
                data.value_dict = {0: [], 1: []};
                for (i = 0 ; i < line_list.length; i = i + 1) {
                  data.value_dict[0].push(line_list[i].value.revision);
                  data.value_dict[1].push(line_list[i].value[property]);
                }
                graph_data_list.push(data);
              });
            }
          }
          gadget.property_dict.graph_data_dict.data = graph_data_list;
          return gadget.property_dict.graph_widget.render(
            {value: gadget.property_dict.graph_data_dict});
        });
      }
    };
  }

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {
      };
    })

    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    //////////////////////////////////////////////
    // initialize the gadget content
    //////////////////////////////////////////////
    .declareMethod("render", function (option_dict) {
      console.log("gadget_erp5_test_result_performance_graph, render, options", option_dict);
      var gadget = this;
      gadget.property_dict.option_dict = option_dict.value;
      gadget.renderGraph(); //Launch as a service, not blocking, we could run other job if we wish.
    })
    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareJob("renderGraph", function () {
      var gadget = this,
        graph_gadget = null;

      return gadget.declareGadget(
              WIDGET_GRAPH_URL,
              {
                scope: "graph",
                sandbox: "iframe",
                element: gadget.element.querySelector(".document-content")
      })
        .push(function (graph_gadget) {
          gadget.property_dict.graph_widget = graph_gadget;
          gadget.property_dict.graph_data_dict = {data: [{
            value_dict: {0: [],
                         1: []},
            type: "scatter"
            }],
            layout: {axis_dict : {0: {"title": "commit"},
                              1: {"title": "performance"}
                             },
                     title: "Test Result Performance"}
          };
          return graph_gadget.render(
            gadget.property_dict.graph_data_dict
            );
        })
        .push(function () {
          var now = new Date(), last_month, tomorrow;
          last_month = new Date(now.valueOf() - 86400 * 1000 * 30); // - 30 days
          tomorrow = new Date(now.valueOf() + 86400 * 1000 * 1); // + 1 day
          gadget.element.querySelector('[name="from_date"]').value = getDateAsString(last_month);
          gadget.element.querySelector('[name="at_date"]').value = getDateAsString(tomorrow);
        })
        .push(function () {
          return getCheckDateAndRefreshGraphFunction(gadget)();
        });
    })
    .onEvent('change', function (evt) {
      if (evt.target === this.element.querySelector('[name="from_date"]')) {
        return getCheckDateAndRefreshGraphFunction(this)();
      } else if (evt.target === this.element.querySelector('[name="at_date"]')) {
        return getCheckDateAndRefreshGraphFunction(this)();
      }
    });
}(window, rJS, RSVP));