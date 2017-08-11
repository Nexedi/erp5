/*global window, rJS, RSVP, URI, location, $,
    loopEventListener, btoa */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, $, RSVP) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    process_list_widget = Handlebars.compile(
      templater.getElementById("monitor-process-widget-template").innerHTML
    ),
    infobox_widget_template = Handlebars.compile(
      templater.getElementById("infobox-widget-template").innerHTML
    ),
    hashCode = new Rusha().digestFromString;

  gadget_klass
    .setState({
      opml: "",
      opml_outline: "",
      breadcrumb_gadget: ""
    })
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict = {
            render_deferred: RSVP.defer(),
            process_state: "monitor_process_resource.status",
            monitor_process_state: "monitor_resource.status",
            element: element
          };
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          gadget.property_dict.jio_gadget = jio_gadget;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("breadcrumb_gadget")
        .push(function (breadcrumb_gadget) {
          return gadget.changeState({breadcrumb_gadget: breadcrumb_gadget});
        });
    })
    .declareMethod('render', function (options) {
      var gadget = this;

      return gadget.updateHeader({
        title: "Monitoring processes view"
      })
        .push(function () {
          return gadget.jio_get(options.key);
        })
        .push(function (outline) {
          return gadget.changeState({opml_outline: outline});
        })
        .push(function () {
          return gadget.jio_allDocs({
            select_list: ["basic_login", "url", "title"],
            query: '(portal_type:"opml") AND (url:"' +
              gadget.state.opml_outline.parent_url + '")'
          });
        })
        .push(function (opml_doc) {
          return gadget.changeState({opml: opml_doc.data.rows[0].value});
        })
        .push(function () {
          return gadget.state.breadcrumb_gadget.render({
            icon: "",
            url_list: [
              {
                title: gadget.state.opml.title,
                url: "#page=hosting_subscription_view&key=" +
                  gadget.state.opml.url
              },
              {
                title: gadget.state.opml_outline.title,
                url: "#page=software_instance_view&key=" +
                  gadget.state.opml_outline.reference
              },
              {
                title: "Processes"
              }
            ]
          });
        })
        .push(function () {
          var key,
            promise_list = [];
          gadget.property_dict.jio_gadget.createJio({
            type: "webhttp",
            url: (gadget.state.opml_outline.url
              .replace("jio_private", "private") +
              'documents/').replace("jio_private", "private"),
            basic_login: gadget.state.opml.basic_login
          });
          return gadget.property_dict.jio_gadget
            .get(gadget.property_dict.process_state);
        })
        .push(undefined, function(error) {
          console.error(error);
          $.notify(
            "Error: Failed to download processes data file!", 
            {
              position: "top right",
              autoHideDelay: 7000,
              className: "error"
            }
          );
          return undefined;
        })
        .push(function (process_list) {
          var row_list = [],
            column_list = [],
            process_content,
            i;
          column_list = [
            {title: "Process"},
            {title: "pid"},
            {title: "user"},
            {title: "create date"},
            {title: "CPU %"},
            {title: "threads"},
            {title: "Memory (Mo)"},
            {title: "Memory %"}];
          if(process_list) {
            for (i = 0; i < process_list.length; i += 1) {
              row_list.push({
                message: (process_list[i].command || []).join(' '),
                cell_list: [
                  {
                    value: process_list[i].name || '-',
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].pid,
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].user || '-',
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].date || '-',
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].cpu_percent,
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].cpu_num_threads,
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].memory_rss,
                    href: '',
                    "class": ''
                  },
                  {
                    value: process_list[i].memory_percent,
                    href: '',
                    "class": ''
                  }
                ]
              });
            }
          }
          process_content = process_list_widget({
            column_list: column_list,
            row_list: row_list
          });
          gadget.element.querySelector(".process-all")
            .innerHTML = process_content;
        })
        .push(function () {
          return gadget.property_dict.jio_gadget.get(gadget.property_dict.monitor_process_state);
        })
        .push(undefined, function(error) {
          console.log(error);
          $.notify(
            "Error: Failed to get resource comsumption data!", 
            {
              position:"top right",
              autoHideDelay: 5000,
              className: "error"
            }
          );
          return {
            cpu_percent: 0,
            cpu_num_threads: 0,
            cpu_time: 0,
            memory_rss: 0,
            memory_percent: 0,
            disk_used: 0
          };
        })
        .push(function (monitor_state) {
          var monitor_resource_list = [],
            resource_state_content;
          if (monitor_state) {
            monitor_resource_list = [
              {
                title: "CPU Used",
                icon_name: "bolt",
                value: monitor_state.cpu_percent + " %"
              },
              {
                title: "CPU Used Time",
                icon_name: "clock-o",
                value: monitor_state.cpu_time + " min"
              },
              {
                title: "CPU Num Threads",
                icon_name: "dashboard",
                value: monitor_state.cpu_num_threads
              },
              {
                title: "Used Memory",
                icon_name: "ticket",
                value: monitor_state.memory_rss + " Mo"
              },
              {
                title: "Memory Used",
                icon_name: "pie-chart",
                value: monitor_state.memory_percent + " %"
              },
              {
                title: "Disk Used",
                icon_name: "hdd-o",
                value: monitor_state.disk_used + " Mo"
              }
            ];
          }
          resource_state_content = infobox_widget_template({
            resource_list: monitor_resource_list
          });
          gadget.element.querySelector(".infobox-container")
            .innerHTML = resource_state_content;
          return gadget.property_dict.render_deferred.resolve();
        });
    })
    .declareAcquiredMethod("getSetting", "getSetting")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_get', 'jio_get')

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this;

      function updateProcessTimer() {
        if (gadget.property_dict.loading && gadget.property_dict.timer) {
          clearInterval(gadget.property_dict.timer);
        }

        gadget.property_dict.timer = setInterval(function(){
          var hash = window.location.toString().split('#')[1];
          if (hash.indexOf('page=process_view') < 0) {
            clearInterval(gadget.property_dict.timer);
            return;
          }
          return gadget.property_dict.jio_gadget.get(gadget.property_dict.process_state)
            .push(function (process_list) {
              var row_list = [],
                column_list = [],
                process_content,
                i;
              column_list = [
                {title: "Process"},
                {title: "pid"},
                {title: "user"},
                {title: "create date"},
                {title: "CPU %"},
                {title: "threads"},
                {title: "Memory (Mo)"},
                {title: "Memory %"}];
              if(process_list) {
                for (i = 0; i < process_list.length; i += 1) {
                  row_list.push({
                    message: (process_list[i].command || []).join(' '),
                    cell_list: [
                      {
                        value: process_list[i].name || '-',
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].pid,
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].user || '-',
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].date || '-',
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].cpu_percent,
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].cpu_num_threads,
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].memory_rss,
                        href: '',
                        "class": ''
                      },
                      {
                        value: process_list[i].memory_percent,
                        href: '',
                        "class": ''
                      }
                    ]
                  });
                }
              }
              process_content = process_list_widget({
                column_list: column_list,
                row_list: row_list
              });
              gadget.element.querySelector(".process-all")
                .innerHTML = process_content;
              return '';
            })
            .push(function () {
              return gadget.property_dict.jio_gadget.get(gadget.property_dict.monitor_process_state);
            })
            .push(function (monitor_state) {
              var monitor_resource_list = [],
                resource_state_content;
              if (monitor_state) {
                monitor_resource_list = [
                  {
                    title: "CPU Used",
                    icon_name: "bolt",
                    value: monitor_state.cpu_percent + " %"
                  },
                  {
                    title: "CPU Used Time",
                    icon_name: "clock-o",
                    value: monitor_state.cpu_time + " min"
                  },
                  {
                    title: "CPU Num Threads",
                    icon_name: "dashboard",
                    value: monitor_state.cpu_num_threads
                  },
                  {
                    title: "Used Memory",
                    icon_name: "ticket",
                    value: monitor_state.memory_rss + " Mo"
                  },
                  {
                    title: "Memory Used",
                    icon_name: "pie-chart",
                    value: monitor_state.memory_percent + " %"
                  },
                  {
                    title: "Disk Used",
                    icon_name: "hdd-o",
                    value: monitor_state.disk_used + " Mo"
                  }
                ];
              }
              resource_state_content = infobox_widget_template({
                resource_list: monitor_resource_list
              });
              gadget.element.querySelector(".infobox-container")
                .innerHTML = resource_state_content;
            });
          },
          65000);
      }
      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        .push(function () {
          return updateProcessTimer();
        });
    });

}(window, rJS, $, RSVP));