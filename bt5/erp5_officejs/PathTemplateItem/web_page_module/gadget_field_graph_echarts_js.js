/*global window, rJS, RSVP, echarts */
/*jslint nomen: true, indent: 2, unparam: true */
(function (window, rJS, RSVP, echarts, loopEventListener) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window),
    getGraphDataAndParameterFromConfiguration = function (configuration_dict) {
      var graph_data_and_parameter = {},
        data,
        trace,
        trace_type,
        type_list = [],
        label_list = [],
        trace_value_dict,
        dataset_list = [],
        dataset,
        i,
        j,
        layout,
        title;

      if (configuration_dict.constructor === String) {
        configuration_dict = JSON.parse(configuration_dict);
      }

      data = configuration_dict.data || [];
      layout = configuration_dict.layout || {};
      title = layout.title;

      // title
      // The position of the title in plotly was fixed, like the "x:center" in echarts.
      // For now, every graph have to provide a title.
      if (title === undefined) {
        throw new Error("No title provided", data);
      }
      graph_data_and_parameter.title = { text: title, x: "center" };

      // tooltip
      // ECharts have to enable the tooltip manually.
      graph_data_and_parameter.tooltip = {};
      graph_data_and_parameter.tooltip.trigger = "item";

      // legend
      // Initialize the legend.
      graph_data_and_parameter.legend = {};
      graph_data_and_parameter.legend.y = 25;
      graph_data_and_parameter.legend.data = [];

      // Axis
      // Initialize the axis
      graph_data_and_parameter.xAxis = [];
      graph_data_and_parameter.yAxis = [];

      for (i = 0; i < data.length; i = i + 1) {
        trace = data[i];
        trace_type = trace.type || "bar";
        type_list.push(trace_type);
        trace_value_dict = trace.value_dict || {};
        if (
          trace_value_dict[0] === undefined ||
            trace_value_dict[1] === undefined
        ) {
          throw new Error("Unexpected data for ECharts", data);
        }

        dataset = {};
        dataset.type = trace_type;
        dataset.name = trace.title || {};

        // If the graph type is pie, set the pie radius
        // plotly doesn't have this option.
        if (trace_type === "pie") {
          dataset.radius = "55%";
          dataset.center = ["50%", "60%"];
        }

        // For pie graph, the legend labels come from each item's title(aka trace.title)
        // For graph which contains the axis, the legend labels come from the item's value_dict[0].
        // See the trace_value_dict in below. But the duplicated value_dict[0] seems for 2D graph
        // seems is redandunt.
        if (trace.type !== "pie") {
          graph_data_and_parameter.legend.data.push(dataset.name);
        }

        dataset.data = [];
        for (j = 0; j < trace_value_dict[0].length; j = j + 1) {
          if (label_list.length !== trace_value_dict[0].length) {
            label_list[j] = trace_value_dict[0][j];
          }
        }

        // Value
        for (j = 0; j < trace_value_dict[1].length; j = j + 1) {
          dataset.data.push({
            value: trace_value_dict[1][j],
            name: label_list[j],
            itemStyle: null
          });
          // Handle the colors in different ways. Maybe enhanced latter
          if (trace.colors) {
            // In the pie graph, set the color each individual "data" item.
            if (trace.type === "pie") {
              dataset.data[j].itemStyle = {
                normal: { color: trace.colors[j] }
              };
            } else {
              // In other types of graph, set the color for each group.
              dataset.itemStyle = { normal: { color: trace.colors[0] } };
            }
          }
        }
        dataset_list.push(dataset);
      }

      // For the pie graph, the legend label is the value_dict[0]
      if (trace.type === "pie") {
        graph_data_and_parameter.legend.data = label_list;
      }

      // Axis
      if (trace.type !== "pie") {
        // if not value type provided, set it as "value".
        graph_data_and_parameter.yAxis.push({
          type: "value",
          name: layout.axis_dict[1].title
        });
        graph_data_and_parameter.xAxis.push({
          data: label_list,
          name: layout.axis_dict[0].title
        });
      } else {
        graph_data_and_parameter.xAxis = null;
        graph_data_and_parameter.yAxis = null;
      }

      graph_data_and_parameter.series = dataset_list;

      return graph_data_and_parameter;
    };
  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////
  function promiseChartEventListener(chart, type) {
    //////////////////////////
    // Resolve the promise as soon as the event is triggered
    // eventListener is removed when promise is cancelled/resolved/rejected
    //////////////////////////
    var handle_event_callback;

    function canceller() {
      chart.off(type, handle_event_callback);
    }

    function resolver(resolve) {
      handle_event_callback = function (params) {
        canceller();
        resolve(params);
        return false;
      };

      chart.on(type, handle_event_callback);
    }
    return new RSVP.Promise(resolver, canceller);
  }

  function loopChartEventListener(chart, type, callback) {
    //////////////////////////
    // Infinite event listener (promise is never resolved)
    // eventListener is removed when promise is cancelled/rejected
    //////////////////////////
    var handle_event_callback,
      callback_promise;

    function cancelResolver() {
      if ((callback_promise !== undefined) &&
          (typeof callback_promise.cancel === "function")) {
        callback_promise.cancel();
      }
    }

    function canceller() {
      if (handle_event_callback !== undefined) {
        chart.off(type, handle_event_callback);
      }
      cancelResolver();
    }
    function itsANonResolvableTrap(resolve, reject) {
      var result;
      handle_event_callback = function handleEventCallback(params) {

        cancelResolver();

        try {
          result = callback(params);
        } catch (e) {
          return reject(e);
        }

        callback_promise = new RSVP.Queue(result)
          .push(undefined, function handleEventCallbackError(error) {
            // Prevent rejecting the loop, if the result cancelled itself
            if (!(error instanceof RSVP.CancellationError)) {
              canceller();
              reject(error);
            }
          });
      };

      chart.on(type, handle_event_callback);
    }
    return new RSVP.Promise(itsANonResolvableTrap, canceller);
  }


  gadget_klass
    .declareAcquiredMethod("chartItemClick", "chartItemClick")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod("render", function (option_dict) {
      //delegate rendering to onStateChange to avoid redrawing the graph
      //every time render is called (a form might call render every time
      //some other fields needs update)
      return this.changeState({
        value: option_dict.value,
        clickHandlerReady: false
      });
    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
        chart;
      // the gadget is ready when both the graph is rendered and the click handler is attached.
      if (modification_dict.hasOwnProperty("clickHandlerReady")) {
        if (gadget.state.clickHandlerReady) {
          gadget.element.querySelector(".graph-content").removeAttribute("disabled");
        } else {
          gadget.element.querySelector(".graph-content").setAttribute("disabled", "disabled");
        }
      }

      if (modification_dict.hasOwnProperty("value")) {
        chart = echarts.init(
          gadget.element.querySelector(".graph-content")
        );

        return new RSVP.Queue(RSVP.all([
          promiseChartEventListener(chart, 'finished'),
          chart.setOption(getGraphDataAndParameterFromConfiguration(
            modification_dict.value
          ))
        ]))
          .push(function () {
            gadget.listenToWindowResize(chart);
            gadget.listenToClickEventOnTheChart(chart);
          });

      }
    })
    .declareJob("listenToWindowResize", function (chart) {
      return loopEventListener(
        window,
        "resize",
        { passive: true },
        function () {
          return chart.resize();
        },
        false
      );
    })

    .declareJob("listenToClickEventOnTheChart", function (chart) {
      var gadget = this;
      return RSVP.all([
        loopChartEventListener(chart, "click", function (params) {
          return gadget.chartItemClick([params.name, params.seriesName]);
        }),
        gadget.changeState({clickHandlerReady: true})
      ]);
    });
}(window, rJS, RSVP, echarts, rJS.loopEventListener));
