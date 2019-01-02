/*global window, rJS, RSVP, console, gantt */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, gantt) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);

  var transformDateStringToDhtmlxDate = function (date_string) {
    var my_date;
    my_date = new Date(date_string);
    return "" + my_date.getDate() + "-" + (my_date.getMonth() + 1) + "-" + my_date.getFullYear();
  };

  var getGanttDataAndParameterFromConfiguration = function (configuration_dict) {
    var gantt_configuration = {},
        data_list = configuration_dict.data_list,
        task,
        data,
        start_date,
        stop_date,
        owner_section_dict = {name: "owner", height: 22, map_to: "owner", type: "select", options: []},
        i;
    gantt_configuration.data = {};
    gantt_configuration.data.data = [];
    gantt_configuration.start_date_list = [];
    gantt_configuration.stop_date_list = [];
    /*
        {name: "description", height: 38, map_to: "text", type: "textarea", focus: true},
        {name: "owner", height: 22, map_to: "owner", type: "select", options: [
          {key:"0", label: ""},
          {key:"1", label: "Mark"},
          {key:"2", label: "John"},
          {key:"3", label: "Rebecca"},
          {key:"4", label: "Alex"}]},
        {name: "time", type: "duration", map_to: "auto", time_format:["%d","%m","%Y","%H:%i"]}
      ];*/
    for (i = 0 ; i < data_list.length ; i = i + 1) {
      task = {};
      data = data_list[i];
      task.id = data.id;
      task.text = data.title;
      // Be Careful, DHTMLX seems less and less open source, and nice features when we
      // have a type "project" is unfortunately available only with paid license. Though
      // We will still use it to set a different color for this kind of task
      if (data.type === 'project') {
        task.type = gantt.config.types.project;
      }
      if (data.background_color) {
        task.color = data.background_color;
      }
      task.start_date = transformDateStringToDhtmlxDate(data.start_date);
      start_date = new Date(data.start_date);
      gantt_configuration.start_date_list.push(start_date);
      stop_date = new Date(data.stop_date);
      gantt_configuration.stop_date_list.push(stop_date);
      task.duration = (stop_date - start_date) / (86400 * 1000);
      if (data.parent_id !== undefined) {
        task.parent = data.parent_id;
      }
      task.open = true;
      console.log("data", data);
      console.log("adding task", task);
      gantt_configuration.data.data.push(task);
    }

    return gantt_configuration;

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
          min_start_date, max_stop_date, day_difference,
          gantt_configuration;

      //graph_data_and_parameter = getGraphDataAndParameterFromConfiguration(configuration_dict);
      //console.log("graph_data_and_parameter", graph_data_and_parameter);
      //chart = new Chart(container, graph_data_and_parameter);
      //gadget.property_dict.chart = chart;
      console.log("configuration_dict", configuration_dict);
      gantt_configuration = getGanttDataAndParameterFromConfiguration(configuration_dict);

      gantt.init("dhtmlx-gantt");


      //gantt.parse(tasks);
      console.log("gantt_configuration", gantt_configuration);
      gantt.config.columns = [{
        name: "text",
        label: "Task Name",
        width: "200",
        tree: true
      }, {
        name: "start_date",
        label: "Start Date",
        /*template: function (obj) {
          return gantt.getLabel("owner", obj.owner);
        },*/
        align: "center"
        //width: 140
      }, {
        name: "duration",
        label: "Duration",
        /*template: function (obj) {
          return gantt.getLabel("owner", obj.owner);
        },*/
        align: "center"
        //width: 140
      }
        ];

      // To change column based on an color_id_attribute
      gantt.templates.task_class = function (start, end, obj) {
        var class_name = "task";
        if (obj.type === gantt.config.types.project) {
          class_name = "project";
        }
        return class_name;
      };

      gantt.templates.scale_cell_class = function (date) {
        if (date.getDay() === 0 || date.getDay() == 6) {
          return "weekend";
        }
      };
      gantt.templates.task_cell_class = function (item, date) {
        if (date.getDay() === 0 || date.getDay() == 6) {
          return "weekend";
        }
      };

      // Customize scales depending on min start date and max stop date
      if (gantt_configuration.start_date_list.length > 0) {
        min_start_date = new Date(Math.min.apply(null, gantt_configuration.start_date_list));
        max_stop_date = new Date(Math.max.apply(null, gantt_configuration.stop_date_list));
        day_difference = (max_stop_date - min_start_date) / (1000 * 60 * 60 * 24);
        if (day_difference > (365 * 2)) {
          // switch to year scale
          gantt.config.min_column_width = 30;
          gantt.config.scale_unit = "year";
          gantt.config.date_scale = "%Y";
          gantt.config.scale_height = 60;
          gantt.config.subscales = [{
            unit: "month",
            step: 2,
            date: "#%M"
          }];
        } else if (day_difference > 30) {
          gantt.config.scale_unit = "day";
          gantt.config.duration_unit = "day";
          gantt.config.date_scale = "%d";


          gantt.config.subscales = [
            {unit: "month", step: 1, date: "%F, %Y"}
          ];
          gantt.config.scale_height = 50;
          gantt.config.min_column_width = 30;
        }
      }

      // Interaction when a box is moved. Only for demo purpose, we might
      // later find some ways to save changes
      gantt.attachEvent("onAfterTaskDrag", function (id, mode) {
        var task = gantt.getTask(id);
        if (mode == gantt.config.drag_mode.progress) {
          var pr = Math.floor(task.progress * 100 * 10) / 10;
          gantt.message(task.text + " is now " + pr + "% completed!");
        } else {
          var convert = gantt.date.date_to_str("%H:%i, %F %j");
          var s = convert(task.start_date);
          var e = convert(task.end_date);
          gantt.message(task.text + " starts at " + s + " and ends at " + e);
        }
      });

      gantt.parse(gantt_configuration.data);


    });


}(window, rJS, RSVP, gantt));