/*global window, rJS, RSVP, console, $ */
/*jslint nomen: true, indent: 2 */
(function (window, rJS, RSVP, $) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // templates
  /////////////////////////////////////////////////////////////////
  var gadget_klass = rJS(window);

  var getDataAndParameterFromConfiguration = function (configuration_dict) {
    var parameter_dict = {}, parent_resource, data_item,
        resource, event, tree_item, resource_dict = {},
        i, eventDrop;

    eventDrop = function (event, dayDelta, minuteDelta) {
                      console.log(event);
                      console.log(event.start);
                      console.log(event.end);
                      console.log(event.id);
                    };

    parameter_dict = {
        eventDrop: eventDrop,
        schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
        //now: '2017-04-24',
        editable: true,
        aspectRatio: 1.8,
        scrollTime: '00:00',
        timezone: 'local',
        header: {
          left: 'today prev,next',
          center: 'title',
          right: 'timelineDay,timelineTenDay,timelineMonth,timelineYear,timelineTenYears'
        },
        defaultView: 'timelineDay',
        views: {
          timelineDay: {
            buttonText: ':15 slots',
            slotDuration: '00:15'
          },
          timelineTenDay: {
            type: 'timeline',
            duration: { days: 10 }
          },
          timelineTenYears: {
            type: 'timeline',
            buttonText: 'Ten years',
            duration: { days: 365.25 * 10 }
          }
        },
        navLinks: true,
        resourceAreaWidth: '25%',
        resourceLabelText: configuration_dict.tree_title || ""
      };
    parameter_dict.resources = [];
    parameter_dict.events = [];
    for (i = 0 ; i < configuration_dict.tree_list.length; i = i + 1) {
      tree_item = configuration_dict.tree_list[i];
      resource = {id: tree_item.id,
                  eventColor: 'green',
                  title: tree_item.title};
      resource_dict[tree_item.id] = resource;
      if (tree_item.parent_id !== undefined) {
        parent_resource = resource_dict[tree_item.parent_id];
        if (parent_resource.children === undefined) {
          parent_resource.children = [];
        }
        parent_resource.children.push(resource);
      } else {
        parameter_dict.resources.push(resource);
      }
    }
    for (i = 0 ; i < configuration_dict.data_list.length; i = i + 1) {
      data_item = configuration_dict.data_list[i];
      if (data_item.background_color !== undefined) {
        resource_dict[data_item.tree_id].eventColor = data_item.background_color;
      }
      event = {resourceId: data_item.tree_id,
               start: data_item.start_date,
               end: data_item.stop_date,
               title: data_item.title,
               id: data_item.id};
      parameter_dict.events.push(event);
    }
    console.log('parameter_dict', parameter_dict);
    return parameter_dict;
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
          data_and_parameter,
          chart;

      container = gadget.element.querySelector(".graph-content");
      gadget.property_dict.container = container;
      console.log("container inside iframe");
      data_and_parameter = getDataAndParameterFromConfiguration(configuration_dict);
      console.log("graph_data_and_parameter", data_and_parameter);

      $('#calendar').fullCalendar(data_and_parameter);

    })
    .declareMethod('updateConfiguration', function (configuration_dict) {
      /* Update the graph with new data/configuration.

        There is many functions in Plotly for updating style, adding points to data, for adding new series of data, etc.
        Though, this is way too complex to guess what has been changed to know if we could just call a few functions to
        take into account changes. Therefore just erase and redraw the whole graph.
      */
      var gadget = this,
          data_and_parameter;
      console.log("updateConfiguration");
      data_and_parameter = getDataAndParameterFromConfiguration(configuration_dict);
    });

}(window, rJS, RSVP, $));





