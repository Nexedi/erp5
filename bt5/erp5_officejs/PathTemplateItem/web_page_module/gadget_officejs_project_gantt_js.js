/*global window, rJS, RSVP, console */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);


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
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")
    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (option_dict) {


      var gadget = this,
          container,
          graph_data_and_parameter,
          chart;
      gadget.property_dict.option_dict = option_dict.value;

      console.log("gantt option_dict", option_dict.value);
      gadget.renderGantt(); //Launched as service, not blocking
    })
    .declareJob("renderGantt", function () {
      var gadget = this,
          empty_gantt_element = gadget.element.querySelector(".empty-gantt"),
          option_dict = gadget.property_dict.option_dict;
      return gadget.declareGadget(
        "unsafe/gadget_officejs_widget_gantt_dhtmlx.html",
        {scope: "gantt",
         sandbox: "iframe",
         element: gadget.element.querySelector(".gantt-content")
      })
      .push(function (gantt_widget) {
        // First search all project lines
        var query;
        gadget.property_dict.gantt_widget = gantt_widget;
        console.log("gantt_widget", gantt_widget);
        query = 'portal_type: ="Project Line" AND relative_url: "' + option_dict.project_relative_url + '/%"';
        console.log("going to query catalog for project_line", query);
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['creation_date', 'ascending']],
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'uid']
        });
      })
      .push(function (project_line_list) {
        // Then find all task and task reports related to it
        var source_project_uid_list = [0], // Initiliaze with 0 to make sure to have at least one uid to search for
            i, project_line, query,
            now = new Date();

        project_line_list = project_line_list.data.rows;
        for (i = 0; i < project_line_list.length; i = i + 1) {
          project_line = project_line_list[i].value;
          if (project_line.stop_date === undefined || (new Date(project_line.stop_date) > now)) {
            if (source_project_uid_list.indexOf(source_project_uid_list.uid) === -1) {
              source_project_uid_list.push(project_line.uid);
            }
          }
        }
        query = '((portal_type: = "Task" AND NOT simulation_state: ("cancelled", "deleted", "confirmed")) OR (portal_type: ="Task Report" AND NOT simulation_state: ("cancelled", "deleted"))) AND source_project_uid: (' + source_project_uid_list.join(', ') + ')';
        console.log("QUERY", query);
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['delivery.start_date', 'ascending']],
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'uid', 'source_project_uid', 'source_project_title']
        });
      })
      .push(function (task_list) {
        var i, task, source_project_uid_list = [],
            source_project_dict = {}, source_project_data,
            gantt_data = {},
            tree_list = [],
            data_list = [],
            sale_order_uid,
            delivery_data, tree_data, start_date,
            now = new Date();
        task_list = task_list.data.rows;
        console.log("task_list:", task_list);
        if (task_list.length) {
          gadget.element.querySelector(".gantt-content").classList.remove("ui-hidden");
          for (i = 0; i < task_list.length; i = i + 1) {
            task = task_list[i].value;
            if (task.source_project_uid !== undefined) {
              if (source_project_uid_list.indexOf(task.source_project_uid) === -1) {
                source_project_uid_list.push(task.source_project_uid);
              }
              if (!task.start_date) {
                start_date = new Date();
              } else {
                start_date = task.start_date;
              }
              source_project_data = source_project_dict[task.source_project_uid] || {'start_date': new Date(start_date),
                                                                          'stop_date': new Date(task.stop_date),
                                                                          'title': task.source_project_title,
                                                                          'type': 'project',
                                                                          'id': task.source_project_uid};
              source_project_data.start_date = new Date(Math.min.apply(
                  null, [source_project_data.start_date, new Date(start_date)]));
              source_project_data.stop_date = new Date(Math.max.apply(
                  null, [source_project_data.stop_date, new Date(task.stop_date)]));
              source_project_dict[task.source_project_uid] = source_project_data;
            }
            if (i === 0) {
              // We assume that by the sort on order_reference that the first line is a level 1 line
              sale_order_uid = task.parent_uid;
            }
            if (task.start_date && task.stop_date) {
              delivery_data = {'title': task.title,
                           'id': task.uid,
                           'tree_id': task.uid,
                           'parent_id': task.source_project_uid,
                           'start_date': task.start_date,
                           'stop_date': task.stop_date};
              if (task.parent_uid !== sale_order_uid) {
                delivery_data.parent_id = task.parent_uid;
              }
              data_list.push(delivery_data);
            }
          }
          for (i = 0; i < source_project_uid_list.length; i = i + 1) {
            source_project_data = source_project_dict[source_project_uid_list[i]];
            data_list.push(source_project_data);
          }

          gantt_data.data_list = data_list;
          return gadget.property_dict.gantt_widget.render(gantt_data);
        } else {
          empty_gantt_element.classList.remove("ui-hidden");
        }
      });
    });


}(window, rJS, RSVP));