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
        "unsafe/gadget_officejs_widget_gantt_dhtmlx.html",
        {scope: "gantt",
         sandbox: "iframe",
         element: gadget.element.querySelector(".gantt-content")
      })
      .push(function (gantt_widget) {
        gadget.property_dict.gantt_widget = gantt_widget;
        var query, delivery_uid_list;
        query = 'portal_type:="Manufacturing Order" AND simulation_state:="planned"';
        delivery_uid_list = option_dict.delivery_uid_list;
        if ((delivery_uid_list !== undefined) && (delivery_uid_list.length > 0)) {
          query = query + ' AND uid: (' + delivery_uid_list.join(', ') + ')';
        }
        console.log("orders query", query);
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['delivery.start_date', 'ascending']],
          //select_list: ['reference', 'title', 'uid']
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'uid']
        });
      })
      .push(function (order_list) {
        var query, delivery_uid_list, empty_causality_delivery_list = [], i, order;
        gadget.property_dict.empty_causality_delivery_list = empty_causality_delivery_list;
        order_list = order_list.data.rows;
        console.log("order_list", order_list);
        console.log("order_list.length", order_list.length);
        for (i = 0; i < order_list.length; i = i + 1) {
          order = order_list[i].value;
          order.gantt_color = "rgb(208, 72, 72)";
          empty_causality_delivery_list.push(order);
        }
        console.log("empty_causality_delivery_list with orders", empty_causality_delivery_list);
        // Then search all production report not finished to find out the
        // list of production orders still having work on them
        query = 'portal_type:="Manufacturing Execution" AND NOT simulation_state: ("draft", "cancelled", "delivered")';
        delivery_uid_list = option_dict.delivery_uid_list;
        if ((delivery_uid_list !== undefined) && (delivery_uid_list.length > 0)) {
          query = query + ' AND uid: (' + delivery_uid_list.join(', ') + ')';
        }
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['delivery.start_date', 'ascending']],
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'uid', 'causality_uid']
        });
      })
      .push(function (delivery_list) {
        // try to search for other manufacturing execution having same causality as
        // other manufacturing execution already found
        var causality_uid_list = [0], // Initiliaze with 0 to make sure to have at least one uid to search for
            i, delivery, query, empty_causality_delivery_list = gadget.property_dict.empty_causality_delivery_list,
            delivery_uid_list;

        delivery_list = delivery_list.data.rows;
        for (i = 0; i < delivery_list.length; i = i + 1) {
          delivery = delivery_list[i].value;
          delivery.gantt_color = "#3db9d3";
          console.log("delivery.causality_uid", delivery.causality_uid);
          if ((delivery.causality_uid || 0) > 0) {
            if (causality_uid_list.indexOf(delivery.causality_uid) === -1) {
              causality_uid_list.push(delivery.causality_uid);
            }
          } else {
            empty_causality_delivery_list.push(delivery);
          }
        }
        query = 'portal_type:="Manufacturing Execution" AND causality_uid: (' + causality_uid_list.join(', ') + ') AND NOT simulation_state: ("draft", "cancelled")';
        console.log("QUERY", query);
        delivery_uid_list = option_dict.delivery_uid_list;
        // No need to get more
        if ((delivery_uid_list !== undefined) && (delivery_uid_list.length > 0)) {
          query = query + ' AND uid: (' + delivery_uid_list.join(', ') + ')';
        }
        return gadget.jio_allDocs({
          query: query,
          limit: 10000,
          sort_on: [['delivery.start_date', 'ascending']],
          select_list: ['reference', 'title', 'start_date', 'stop_date', 'uid', 'causality_uid', 'causality_title']
        });
      })
      .push(function (delivery_list) {
        var i, delivery, causality_list = [],
            causality_dict = {}, causality_data,
            gantt_data = {},
            tree_list = [],
            data_list = [],
            sale_order_uid,
            initial_delivery_list = [],
            delivery_data, tree_data;
        initial_delivery_list = delivery_list.data.rows;
        delivery_list = [];
        for (i = 0; i < initial_delivery_list.length; i = i + 1) {
          delivery_list.push(initial_delivery_list[i].value);
        }
        for (i = 0; i < gadget.property_dict.empty_causality_delivery_list.length; i = i + 1) {
          console.log("pushing empty causality delivery", gadget.property_dict.empty_causality_delivery_list[i]);
          delivery_list.push(gadget.property_dict.empty_causality_delivery_list[i]);
        }
        for (i = 0; i < delivery_list.length; i = i + 1) {
          delivery = delivery_list[i];
          if ((delivery.causality_uid || 0) > 0) {
            if (causality_list.indexOf(delivery.causality_uid) === -1) {
              causality_list.push(delivery.causality_uid);
            }
            causality_data = causality_dict[delivery.causality_uid] || {'start_date': new Date(delivery.start_date),
                                                                        'stop_date': new Date(delivery.stop_date),
                                                                        'title': delivery.causality_title,
                                                                        'type': 'project',
                                                                        'id': delivery.causality_uid};
            causality_data.start_date = new Date(Math.min.apply(
                null, [causality_data.start_date, new Date(delivery.start_date)]));
            causality_data.stop_date = new Date(Math.max.apply(
                null, [causality_data.stop_date, new Date(delivery.stop_date)]));
            causality_dict[delivery.causality_uid] = causality_data;
          }
          if (i === 0) {
            // We assume that by the sort on order_reference that the first line is a level 1 line
            sale_order_uid = delivery.parent_uid;
          }
          if (delivery.start_date !== undefined && delivery.stop_date !== undefined) {
            delivery_data = {'title': delivery.title,
                         'id': delivery.uid,
                         'start_date': delivery.start_date,
                         'stop_date': delivery.stop_date,
                         'background_color': delivery.gantt_color};
            if (delivery.causality_uid !== undefined) {
              delivery_data.parent_id = delivery.causality_uid;
            }
            if (delivery.parent_uid !== sale_order_uid) {
              delivery_data.parent_id = delivery.parent_uid;
            }
            data_list.push(delivery_data);
          }
        }
        for (i = 0; i < causality_list.length; i = i + 1) {
          causality_data = causality_dict[causality_list[i]];
          data_list.push(causality_data);
        }
        gantt_data.data_list = data_list;
        console.log("gantt_data", gantt_data);
        return gadget.property_dict.gantt_widget.render(gantt_data);
      });
    });


}(window, rJS, RSVP));