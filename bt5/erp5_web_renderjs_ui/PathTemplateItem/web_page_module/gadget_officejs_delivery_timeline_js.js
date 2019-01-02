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
          option_dict = gadget.property_dict.option_dict;
      return gadget.declareGadget(
        "unsafe/gadget_officejs_widget_timeline_fullcalendar.html",
        {scope: "timeline",
         sandbox: "iframe",
         element: gadget.element.querySelector(".timeline-content")
      })
      .push(function (timeline_widget) {
        var query;
        gadget.property_dict.timeline_widget = timeline_widget;
        console.log("timeline_widget", timeline_widget);
        // portal_type:="Sale Order Line" AND relative_url:"sale_order_module/4572/%"
        query = 'portal_type:="' + option_dict.portal_type + '" AND relative_url:"' + option_dict.relative_url + '"';
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['reference', 'ascending']],
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'parent_uid', 'uid', 'source_title']
        });
      })
      .push(function (line_list) {
        var i, line,
            timeline_data = {},
            data_list = [],
            tree_list = [],
            tree_data,
            sale_order_uid,
            color_list = ['blue', 'green', 'purple', 'orange', 'grey', 'black', 'red', 'pink'],
            color,
            source_list = [],
            line_data;
        line_list = line_list.data.rows;
        console.log("line_list", line_list);
        for (i = 0; i < line_list.length; i = i + 1) {
          line = line_list[i].value;
          if (i === 0) {
            // We assume that by the sort on order_reference that the first line is a level 1 line
            sale_order_uid = line.parent_uid;
          }
          if (line.start_date !== undefined && line.stop_date !== undefined) {
            tree_data = {'title': line.title,
                         'id': line.uid
                        };
            if (source_list.indexOf(line.source_title) === -1) {
              source_list.push(line.source_title);
            }
            console.log('source_list', source_list);
            color = color_list[source_list.indexOf(line.source_title) % color_list.length];
            line_data = {'title': line.title,
                         'id': line.uid,
                         'tree_id': line.uid,
                         'start_date': new Date(line.start_date).toISOString(),
                         'stop_date': new Date(line.stop_date).toISOString(),
                         'background_color': color};
            if (line.parent_uid !== sale_order_uid) {
              tree_data.parent_id = line.parent_uid;
            }
            data_list.push(line_data);
            tree_list.push(tree_data);
          }
        }
        timeline_data.data_list = data_list;
        timeline_data.tree_list = tree_list;
        timeline_data.tree_title = "Tasks";
        console.log("timeline_data", timeline_data);
        return gadget.property_dict.timeline_widget.render(timeline_data);

      });
    });


}(window, rJS, RSVP));