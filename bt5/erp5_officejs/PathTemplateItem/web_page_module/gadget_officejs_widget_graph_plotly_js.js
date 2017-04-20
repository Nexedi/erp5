/*global window, rJS, RSVP, console, Plotly */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Plotly) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);

  var getGraphDataAndParameterFromConfiguration = function (configuration_dict) {
    var graph_data_and_parameter = {},
      given_data_list = configuration_dict.data,
      current_data,
      given_data,
      axis_mapping_id_dict,
      i, j, AXIS_MAPPING_DICT,
      mapped_axis_list,
      axis_list_dict = {};
    AXIS_MAPPING_DICT = {0: "x",
                         1: "y",
                         2: "z"};
    console.log("getGraphDataAndParameterFromConfiguration 1");
    graph_data_and_parameter.data_list = [];
    graph_data_and_parameter.layout = {modeBarButtonsToRemove: ['sendDataToCloud']};

    function setCurrentData(axis_data) {
      console.log("setCurrentData, axis_data", axis_data);
      var axis_id = AXIS_MAPPING_DICT[axis_data[0]],
          axis_value_list = axis_data[1];
      current_data[axis_id] = axis_value_list;
    }
    console.log("getGraphDataAndParameterFromConfiguration 2");
    console.log("given_data_list", given_data_list);
    function setAxisLayout(axis_mapping) {
      var axis_id = AXIS_MAPPING_DICT[axis_mapping[0]],
          axis_identifier = axis_mapping[1],
          axis_name,
          axis_layout,
          mapped_axis_list;
      mapped_axis_list = axis_list_dict[axis_id] || [];
      if (mapped_axis_list.indexOf(axis_identifier) === -1) {
        mapped_axis_list.push(axis_identifier);
        axis_list_dict[axis_id] = mapped_axis_list;
        axis_name = axis_id + "axis";
        console.log("mapped_axis_list in loop", mapped_axis_list);
        axis_layout = {};
        if (mapped_axis_list.indexOf(axis_identifier) !== 0) {
          axis_name = axis_name + (mapped_axis_list.indexOf(axis_identifier) + 1);
          axis_layout.overlaying = axis_id;
          axis_layout.side = 'right';
          axis_layout.position = 1 - (0.05 * mapped_axis_list.indexOf(axis_identifier));
          // We must also reduce graph size to display all the axis labels. We assume here that this
          // happens only for cases of having multiple y axis
          graph_data_and_parameter.layout.xaxis = graph_data_and_parameter.layout.xaxis || {};
          graph_data_and_parameter.layout.xaxis.domain = [0.0, axis_layout.position];
          current_data[axis_id + "axis"] = axis_id + (mapped_axis_list.indexOf(axis_identifier) + 1);
        }
        console.log("axis_name", axis_name);
        if (given_data.title !== undefined) {
          axis_layout.title = given_data.title;
        }
        graph_data_and_parameter.layout[axis_name] = axis_layout;
      }


    }
    for (i = 0; i < given_data_list.length; i = i + 1) {
      current_data = {};
      given_data = given_data_list[i];
      Object.entries(given_data.value_dict).forEach(setCurrentData);
      if (given_data.title !== undefined) {
        current_data.name = given_data.title;
      }
      if (given_data.type !== undefined) {
        current_data.type = given_data.type;
        if (given_data.type === "scatter") {
          current_data.mode = 'markers';
        }
      }

      axis_mapping_id_dict = given_data.axis_mapping_id_dict || {};
      Object.entries(axis_mapping_id_dict).forEach(setAxisLayout);
      graph_data_and_parameter.data_list.push(current_data);
    }
    console.log("getGraphDataAndParameterFromConfiguration 3");
    console.log("axis_list_dict", axis_list_dict);
    console.log("graph_data_and_parameter", graph_data_and_parameter);
    graph_data_and_parameter.bar_config = {modeBarButtonsToRemove: ['sendDataToCloud']};

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
    .declareMethod('render', function (configuration_dict) {


      var gadget = this,
          container,
          graph_data_and_parameter,
          chart;

      container = gadget.element.querySelector(".graph-content");
      gadget.property_dict.container = container;
      console.log("container inside iframe");
      graph_data_and_parameter = getGraphDataAndParameterFromConfiguration(configuration_dict);
      console.log("graph_data_and_parameter", graph_data_and_parameter);
      Plotly.plot(container, graph_data_and_parameter.data_list, graph_data_and_parameter.layout, graph_data_and_parameter.bar_config);

    })
    .declareMethod('updateConfiguration', function (configuration_dict) {
      /* Update the graph with new data/configuration.

        There is many functions in Plotly for updating style, adding points to data, for adding new series of data, etc.
        Though, this is way too complex to guess what has been changed to know if we could just call a few functions to
        take into account changes. Therefore just erase and redraw the whole graph.
      */
      var gadget = this,
          graph_data_and_parameter;
      console.log("updateConfiguration");
      graph_data_and_parameter = getGraphDataAndParameterFromConfiguration(configuration_dict);
      Plotly.purge(gadget.property_dict.container);
      Plotly.plot(gadget.property_dict.container, graph_data_and_parameter.data_list, graph_data_and_parameter.layout, graph_data_and_parameter.bar_config);
    });

}(window, rJS, RSVP, Plotly));





