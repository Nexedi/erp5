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
      given_data_list,
      current_data,
      given_data,
      axis_mapping_id_dict,
      i, j, AXIS_MAPPING_DICT,
      mapped_axis_list,
      axis_list_dict = {};

    AXIS_MAPPING_DICT = {0: "x",
                         1: "y",
                         2: "z"};

    if (configuration_dict.constructor === String) {
      configuration_dict = JSON.parse(configuration_dict);
    }
    given_data_list = configuration_dict.data;

    console.log("getGraphDataAndParameterFromConfiguration 1 configuration_dict", configuration_dict);
    graph_data_and_parameter.data_list = [];
    graph_data_and_parameter.layout = {modeBarButtonsToRemove: ['sendDataToCloud']};
    if (configuration_dict.title !== undefined) {
      graph_data_and_parameter.layout.title = configuration_dict.title;
    }

    function setCurrentData(axis_data) {
      console.log("setCurrentData, axis_data", axis_data);
      var axis_id = AXIS_MAPPING_DICT[axis_data[0]],
          axis_value_list = axis_data[1];
      current_data[axis_id] = axis_value_list;
    }
    console.log("getGraphDataAndParameterFromConfiguration 2");
    console.log("plotly given_data_list", given_data_list);
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
          chart,
          graph_value;

      container = gadget.element.querySelector(".graph-content");
      gadget.property_dict.container = container;
      console.log("container inside iframe");
      graph_value = modification_dict.value;
      graph_data_and_parameter = getGraphDataAndParameterFromConfiguration(graph_value);
      console.log("plotly graph_data_and_parameter", graph_data_and_parameter);
      if (gadget.property_dict.already_rendered === true) {
        Plotly.purge(container);
      }
      Plotly.plot(container, graph_data_and_parameter.data_list, graph_data_and_parameter.layout, graph_data_and_parameter.bar_config);
      gadget.property_dict.already_rendered = true;

    });

}(window, rJS, RSVP, Plotly));