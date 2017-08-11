/*global window, rJS, RSVP, console, Chart */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Chart) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);

  var getGraphDataAndParameterFromConfiguration = function (configuration_dict) {
    var graph_data_and_parameter = {},
        data,
        trace,
        trace_type,
        type_list = [],
        label_list = [],
        trace_value_dict,
        dataset_list = [],
        dataset,
        i, j,
        layout,
        title,
        type = 'bar',
        x_label, y_label;

    if (configuration_dict.constructor === String) {
      configuration_dict = JSON.parse(configuration_dict);
    }
    data = configuration_dict.data || [];
    layout = configuration_dict.layout || {};
    title = layout.title;

    /* title seems to be ignored by Chart.js, so do not handle it for now */

    /* In Chart.js, there is not yet full support of different types of graph, it only work
       under some conditions. So we have to set a global type for whole the graph.

       Also Chart.js only support 2D, se we assume we have only only two axis for data.
       Then for now we only support series having same x, it can be enhanced later.*/
    for (i = 0; i < data.length; i = i + 1) {
      trace = data[i];
      trace_type = trace.type || 'bar';
      type_list.push(trace_type);
      trace_value_dict = trace.value_dict || {};
      if (trace_value_dict[0] === undefined || trace_value_dict[1] === undefined) {
        throw new Error("Unexpected data for Chart.js", data);
      }
      if (label_list.length === 0) {
        for (j = 0; j < trace_value_dict[0].length; j = j + 1) {
          label_list[j] = trace_value_dict[0][j];
        }
      }
      dataset = {};
      dataset.type = trace_type;
      dataset.label = trace.title;
      dataset.data = [];
      dataset.fill = false;
      for (j = 0; j < trace_value_dict[1].length; j = j + 1) {
        dataset.data[j] = trace_value_dict[1][j];
      }
      dataset_list.push(dataset);
    }
    // Only one type of graph, so set it globally
    console.log('type_list', type_list);
    if (type_list.length === 1) {
      type = type_list[0];
    }
    graph_data_and_parameter.type = type;
    graph_data_and_parameter.data = {};
    graph_data_and_parameter.data.labels = label_list;
    graph_data_and_parameter.data.datasets = dataset_list;

    return graph_data_and_parameter;
  };
  /////////////////////////////////////////////////////////////////
  // some methods
  /////////////////////////////////////////////////////////////////

  gadget_klass

    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    .ready(function (gadget) {
      gadget.property_dict = {};
    })

    /////////////////////////////////////////////////////////////////
    // published methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // acquired methods
    /////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (option_dict) {


      var gadget = this;
      //delegate rendering to onStateChange to avoid redrawing the graph
      //every time render is called (a form might call render every time
      //some other fields needs update
      gadget.changeState({value: option_dict.value});

    })
    .onStateChange(function (modification_dict) {
      var gadget = this,
          container,
          graph_data_and_parameter,
          chart;
      container = gadget.element.querySelector(".graph-content");
      graph_data_and_parameter = getGraphDataAndParameterFromConfiguration(modification_dict.value);
      console.log("graph_data_and_parameter", graph_data_and_parameter);
      chart = new Chart(container, graph_data_and_parameter);
      gadget.property_dict.chart = chart;
    });


}(window, rJS, RSVP, Chart));





