/*jslint indent: 2, nomen: true */
/*global window, rJS, RSVP, console, loopEventListener */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  var WIDGET_GRAPH_URL = "../gadget_officejs_widget_graph_chart.html";

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
      from_date = gadget.property_dict.element.querySelector('[name="from_date"]').value;
      at_date = gadget.property_dict.element.querySelector('[name="at_date"]').value;
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
                data.type = "line";
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
          return gadget.property_dict.graph_widget.updateConfiguration(
            gadget.property_dict.graph_data_dict);
        });
      }
    };
  }

  rJS(window)
    .ready(function (gadget) {
      gadget.property_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
          gadget.property_dict.deferred = RSVP.defer();
        });
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
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.deferred.resolve();
        });
    })
    /////////////////////////////////////////
    // Render text content gadget
    /////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        graph_gadget = null;

      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.deferred.promise;
        })
        .push(function () {
          return RSVP.all([
            gadget.declareGadget(
              WIDGET_GRAPH_URL,
              {
                scope: "graph",
                element: gadget.property_dict.element.querySelector(".document-content")
              })
            ]);
        })

        .push(function (result) {
          graph_gadget = result[0];
          gadget.property_dict.graph_widget = graph_gadget;
          gadget.property_dict.graph_data_dict = {data: [{
            value_dict: {0: [],
                         1: []},
            type: "line"
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
          gadget.property_dict.element.querySelector('[name="from_date"]').value = getDateAsString(last_month);
          gadget.property_dict.element.querySelector('[name="at_date"]').value = getDateAsString(tomorrow);
        })
        .push(function () {
          getCheckDateAndRefreshGraphFunction(gadget)();
        });
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.property_dict.element.querySelector('[name="from_date"]'),
        'change',
        false,
        function () {
          getCheckDateAndRefreshGraphFunction(gadget)();
        });
    })
    .declareService(function () {
      var gadget = this;
      return loopEventListener(
        gadget.property_dict.element.querySelector('[name="at_date"]'),
        'change',
        false,
        function () {
          getCheckDateAndRefreshGraphFunction(gadget)();
        });
    });
}(window, rJS, RSVP, loopEventListener));
