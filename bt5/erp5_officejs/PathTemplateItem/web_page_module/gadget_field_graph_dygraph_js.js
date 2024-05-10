/*global window, rJS, RSVP, console, Dygraph */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, Dygraph) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);

  var getGraphDataAndParameterFromConfiguration = function (configuration_dict) {
    var graph_data_and_parameter = {},
        layout,
        data,
        x_label, y_label,
        label_list = [],
        trace_value_dict,
        dygraph_data = [],
        trace,
        dygraph_data_and_parameter = {},
        axis_dict,
        object_key_list,
        axis_definition,
        axis_mapping_id_dict,
        type,
        serie,
        serie_value_list = [],
        serie_value_mapping = {},
        i, j;

    if (configuration_dict.constructor === String) {
      configuration_dict = JSON.parse(configuration_dict);
    }
    layout = configuration_dict.layout || {};
    data = configuration_dict.data || [];
    axis_dict = layout.axis_dict || {};
    x_label = (axis_dict[0] || {}).title;
    y_label = (axis_dict[1] || {}).title;
    if (x_label !== undefined) {
      graph_data_and_parameter.xlabel = x_label;
    }
    if (y_label !== undefined) {
      graph_data_and_parameter.ylabel = y_label;
    }
    label_list.push(x_label);

    /* Dygraph only support 2D, so we assume we have only only two axis for data.
       Then for now we only support series having same x, it can be enhanced later.*/


    /* We assume below that the x axis for all data is the same. Otherwise, dygraph needs that we fill
       empty values by hand, which is not done here yet

       When having several series, we can set mapping to [y1, y2, y3, etc]. Though dygraph expect having
       exactly y, y2, y3, etc]. So we have to remap.
     */
    graph_data_and_parameter.series = {};
    function setSerie(value) {
      var serie_value_index;
      var mapped_serie;
      serie = {};
      serie_value_list.push(value);
      serie_value_index = serie_value_list.indexOf(value);
      if (serie_value_index === 0) {
        mapped_serie = "y";
      } else {
        mapped_serie = "y" + (serie_value_index + 1);
      }
      serie.axis = mapped_serie;
      serie_value_mapping[value] = mapped_serie;
      if (type === "scatter") {
        serie.drawPoints = true;
        serie.strokeWidth = 0;
      }
      console.log("serie", serie);
      graph_data_and_parameter.series[trace.title || ''] = serie;
    }
    for (i = 0; i < data.length; i = i + 1) {
      trace = data[i];
      trace_value_dict = trace.value_dict || {};
      label_list.push(trace.title || '');
      if (trace_value_dict[0] === undefined || trace_value_dict[1] === undefined) {
        throw new Error("Unexpected data for dygraph", data);
      }
      if (dygraph_data.length === 0) {
        // Initialize x axis
        for (j = 0; j < trace_value_dict[0].length; j = j + 1) {
          // When used within iframe, we have to recreate date object since the date is now string
          dygraph_data[j] = [new Date(trace_value_dict[0][j])];
        }
      }
      type = trace.type || 'line';
      // to fill y axis for trace
      for (j = 0; j < trace_value_dict[1].length; j = j + 1) {
        dygraph_data[j].push(trace_value_dict[1][j]);
      }
      axis_mapping_id_dict = trace.axis_mapping_id_dict || {};
      Object.values(axis_mapping_id_dict).forEach(setSerie);
    }
    /* Define parameters of axes */
    graph_data_and_parameter.axes = {};
    object_key_list = Object.keys(axis_dict);
    Object.entries(axis_dict).forEach(function (axis_data) {
      var axis_id = axis_data[0],
          axis_configuration = axis_data[1];
      if (serie_value_mapping[axis_id] !== undefined) {
        axis_id = serie_value_mapping[axis_id];
      }
      graph_data_and_parameter.axes[axis_id] = {};
      if (axis_configuration.position !== undefined) {
        graph_data_and_parameter.axes[axis_id].position = axis_configuration.position;
        graph_data_and_parameter.axes[axis_id].independentTicks = true; // XXX Needed ???
      }
    });
    if (graph_data_and_parameter.axes[0] !== undefined) {
      graph_data_and_parameter.axes.x = graph_data_and_parameter.axes[0];
      graph_data_and_parameter.axes.x.title = "date"; // XXX FIX
      delete graph_data_and_parameter.axes[0];
    }

    graph_data_and_parameter.labels = label_list;
    graph_data_and_parameter.dygraph_data = dygraph_data;
    graph_data_and_parameter.dygraph_parameter_dict = graph_data_and_parameter;
    return graph_data_and_parameter;
  };

  var formatGraphDict = function (input_dict) {
    var i, j, key, series = [], label_list = ['x'], point_list = [], serie_length, point;
    for (i = 0; i < input_dict.data.length; i = i + 1) {
      for (key of Object.keys(input_dict.data[i].value_dict)) {
        serie_length = input_dict.data[i].value_dict[key].length;
        if (key == 0) {
          if (series.length === 0) {
            series.push(input_dict.data[i].value_dict[key]); //x
          }
        } else {
          series.push(input_dict.data[i].value_dict[key]); //yi
        }
      }
      label_list.push(input_dict.data[i].title);
    }
    for (i = 0; i < serie_length; i = i + 1) {
      point = [];
      for (j = 0; j < series.length; j = j + 1) {
        point.push(series[j][i]);
      }
      point_list.push(point);
    }
    var dygraph_dict = {
      dygraph_data: point_list,
      dygraph_parameter_dict: {
        labels: label_list,
        drawPoints : true,
        pointSize : 1,
      }
    };
    return dygraph_dict;
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
          graph_data_and_parameter;

      container = gadget.element.querySelector(".graph-content");
      graph_data_and_parameter = formatGraphDict(modification_dict.value);
      gadget.property_dict.graph = new Dygraph(container,
                                               graph_data_and_parameter.dygraph_data,
                                               graph_data_and_parameter.dygraph_parameter_dict);
    });



}(window, rJS, RSVP, Dygraph));





