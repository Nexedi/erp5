/*global window, rJS, RSVP, Handlebars */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, Handlebars) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    infobox_widget_template = Handlebars.compile(
      templater.getElementById("infobox-widget-template").innerHTML
    );

  gadget_klass
    .setState({
      opml: "",
      opml_outline: ""
    })
    .ready(function (gadget) {
      gadget.property_dict = {
        process_state: "monitor_process_resource.status",
        monitor_process_state: "monitor_resource.status"
      };
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          gadget.property_dict.jio_gadget = jio_gadget;
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this;

      return gadget.jio_get(options.parent_id)
        .push(function (outline) {
          return gadget.changeState({opml_outline: outline});
        })
        .push(function () {
          return gadget.jio_get(gadget.state.opml_outline.parent_url);
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc});
        })
        .push(function () {
          return RSVP.all([
            gadget.getUrlFor({command: 'history_previous'}),
            gadget.getUrlFor({command: 'change', options: {
              page: 'ojsm_resources_view',
              key: gadget.state.opml_outline.reference
            }})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.opml_outline.title + ": Processes View",
            front_url: url_list[0],
            resources_url: url_list[1]
          });
        })
        .push(function () {
          return gadget.property_dict.jio_gadget.createJio({
            type: "webhttp",
            // XXX fix URL
            url: (gadget.state.opml_outline.url
              .replace("jio_private", "private") +
              'documents/'),
            basic_login: gadget.state.opml.basic_login
          });
        })
        .push(function () {
          return gadget.property_dict.jio_gadget
            .get(gadget.property_dict.monitor_process_state);
        })
        .push(undefined, function () {
          return gadget.notifySubmitted({
            message: "Error: Failed to download data files!",
            status: "error"
          })
            .push(function () {
              return undefined;
            });
        })
        .push(function (average_result) {
          if (average_result !== undefined) {
            return gadget.changeState({
              average_state: average_result
            });
          }
        });
    })
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .allowPublicAcquisition("jio_allDocs", function () {
      var gadget = this,
        result = {data: {total_rows: 0, rows: []}};
      return gadget.property_dict.jio_gadget.get(gadget.property_dict.process_state)
        .push(function (process_list) {
          var i;
          result.data.total_rows = process_list.length;
          for (i = 0; i < process_list.length; i += 1) {
            result.data.rows.push({
              id: "process_t" + i,
              value: {
                process: process_list[i].name || '-',
                pid: process_list[i].pid,
                user: process_list[i].user || '-',
                date: process_list[i].date || '-',
                cpu_load: process_list[i].cpu_percent,
                cpu_threads: process_list[i].cpu_num_threads,
                memory_used: process_list[i].memory_rss,
                memory_percent: process_list[i].memory_percent
              }
            });
          }
          return result;
        });
    })

    .onStateChange(function (change_dict) {
      var gadget = this,
        monitor_resource_list,
        resource_state_content;
      if (!change_dict.hasOwnProperty('average_state')) {
        return;
      }
      monitor_resource_list = [
        {
          title: "CPU Used",
          icon_name: "bolt",
          value: change_dict.average_state.cpu_percent + " %"
        },
        {
          title: "CPU Used Time",
          icon_name: "clock-o",
          value: change_dict.average_state.cpu_time + " min"
        },
        {
          title: "CPU Num Threads",
          icon_name: "dashboard",
          value: change_dict.average_state.cpu_num_threads
        },
        {
          title: "Used Memory",
          icon_name: "ticket",
          value: change_dict.average_state.memory_rss + " Mo"
        },
        {
          title: "Memory Used",
          icon_name: "pie-chart",
          value: change_dict.average_state.memory_percent + " %"
        }
      ];
      resource_state_content = infobox_widget_template({
        resource_list: monitor_resource_list
      });
      gadget.element.querySelector(".infobox-container")
        .innerHTML = resource_state_content;

      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_view) {
          var column_list = [
            ['process', 'process'],
            ['pid', 'PID'],
            ['user', 'User'],
            ['date', 'Create Date'],
            ['cpu_load', 'CPU %'],
            ['cpu_threads', 'CPU Threads'],
            ['memory_used', 'Memory (Mo)'],
            ['memory_percent', 'Memory %']
          ];
          return form_view.render({
            erp5_document: {
              "_embedded": {"_view": {
                "listbox": {
                  "column_list": column_list,
                  "show_anchor": 0,
                  "default_params": {},
                  "editable": 0,
                  "editable_column_list": [],
                  "key": "field_listbox",
                  "lines": 200,
                  "list_method": "portal_catalog",
                  "query": "urn:jio:allDocs?query=portal_type%3A%22" +
                    "process_consumption" + "%22",
                  "portal_type": [],
                  "search_column_list": [],
                  "sort_column_list": [],
                  "sort": [],
                  "title": "Instance Processes Consumption",
                  "command": "reload",
                  "type": "ListBox"
                }
              }},
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "bottom",
                [["listbox"]]
              ]]
            }
          });
        });
    })

    .onLoop(function () {
      var gadget = this;

      return gadget.property_dict.jio_gadget
        .get(gadget.property_dict.monitor_process_state)
        .push(undefined, function () {
          return gadget.notifySubmitted({
            message: "Error: Failed to download data files!",
            status: "error"
          })
            .push(function () {
              return undefined;
            });
        })
        .push(function (average_result) {
          if (average_result !== undefined) {
            return gadget.changeState({
              average_state: average_result
            });
          }
        });
    }, 65000);

}(window, rJS, RSVP, Handlebars));