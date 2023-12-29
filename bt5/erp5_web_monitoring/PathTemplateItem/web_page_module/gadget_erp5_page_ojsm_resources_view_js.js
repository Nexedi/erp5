/*global window, rJS, RSVP */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP) {
  "use strict";

  var gadget_klass = rJS(window);

  function getDateWindow(data) {
    var max_date,
      begin_date,
      end_date,
      date_window = [];
    if (data.length > 0) {
      max_date = data[data.length - 1].split(',')[0];
      begin_date = new Date(max_date);
      end_date = new Date(max_date);
      begin_date.setHours(begin_date.getHours() - 8);
      date_window = [Date.parse(begin_date), Date.parse(end_date)];
    }
    return date_window;
  }

  function loadGraphData(gadget, key) {
    var resource_key = gadget.property_dict.resource_dict[key];
    return gadget.property_dict.jio_gadget.get(resource_key)
      .push(undefined, function () {
        return gadget.notifySubmitted({
          message: "Error: Failed to download resource file '" + resource_key +
            "' from URL: " + gadget.state.opml_outline.url,
          status: "error"
        })
          .push(function () {
            return {data: []};
          });
      })
      .push(function (jio_element) {
        gadget.property_dict.date_window = getDateWindow(gadget.property_dict.mem_data.data);
        if (!jio_element.hasOwnProperty('data')) {
          return {data: []};
        }
        switch (key) {
        case "memory_resource":
          gadget.property_dict.mem_data = jio_element;
          break;
        case "cpu_resource":
          gadget.property_dict.process_data = jio_element;
          break;
        case "io_resource":
          gadget.property_dict.io_data = jio_element;
          break;
        }
        return jio_element;
      });
  }

  function updateIOData(gadget, date_window) {
    var i,
      element,
      prev_element,
      date_diff,
      line_list = [],
      data_list = [],
      axis_list = [];

    function convertElement(element) {
      var element_list = element.split(',');
      return [
        element_list[0],
        parseFloat(element_list[1].trim()),
        parseFloat(element_list[2].trim()),
        element_list[3].trim()
      ];
    }
    //"date, io rw counter, io cycles counter, disk used"
    line_list = ["io rw count (Kb/s)", "io cycles count (/1000)"]; //, "disk used"];
    axis_list.push({
        "0": {
          "title": "IO read/write counter",
          "scale_type": "linear",
          "value_type": "date",
          "zoom_range": date_window
        }
      });
    axis_list.push({
        "0": {
          "title": "IO cycles counter",
          "scale_type": "linear",
          "value_type": "date",
          "zoom_range": date_window
        }
      });
    for (i = 0; i < line_list.length; i += 1) {
      line_list[i] = line_list[i].trim();
      data_list.push({
        value_dict: {"0": [], "1": []},
        type: "surface",
        axis_mapping_id_dict: {"1": "1_1"},
        title: line_list[i]
      });
      axis_list[i]["1_1"] = {"title": line_list[i], "position": "right"};
    }
    if (gadget.property_dict.io_data.data.length > 2) {
      prev_element = convertElement(gadget.property_dict.io_data.data[1]);
      for (i = 2; i < gadget.property_dict.io_data.data.length; i += 1) {
        element = convertElement(gadget.property_dict.io_data.data[i]);
        date_diff = (new Date(element[0]).getTime() - new Date(prev_element[0]).getTime()) / 1000;
        // XXX - repeating date everytime
        data_list[0].value_dict["0"].push(element[0]);
        data_list[0].value_dict["1"].push((element[1] - prev_element[1]) / (1024 * date_diff));
        // XXX - repeating date everytime
        data_list[1].value_dict["0"].push(element[0]);
        data_list[1].value_dict["1"].push((element[2] - prev_element[2]) / 1000);
        // XXX - repeating date everytime
        /*data_list[2].value_dict["0"].push(element[0]);
        data_list[2].value_dict["1"].push(element[3]);*/
        prev_element = element;
      }
    }
    return [
      {
        value: {
          data: [data_list[0]],
          layout: {
            axis_dict : axis_list[0],
            title: "IO write counter"
          }
        }
      },
      {
        value: {
          data: [data_list[1]],
          layout: {
            axis_dict : axis_list[1],
            title: "IO cycles counter"
          }
        }
      }
    ];
  }

  function updateGraph(gadget, reload_only) {
    return new RSVP.Queue()
      .push(function () {
        if (reload_only === true) {
          return;
        }
        return new RSVP.Queue()
          .push(function () {
            var key,
              promise_list = [];
            for (key in gadget.property_dict.resource_dict) {
              if (gadget.property_dict.resource_dict.hasOwnProperty(key)) {
                promise_list.push(loadGraphData(gadget, key));
              }
            }
            return RSVP.all(promise_list);
          })
          .push(function () {
            var data = updateIOData(gadget, gadget.property_dict.date_window);
            return RSVP.all([
              gadget.property_dict.graph_io_read.render(data[0]),
              gadget.property_dict.graph_io_write.render(data[1])
            ]);
          });
      })
      .push(function () {
        var data_list = [],
          axis_dict = {},
          line_list,
          i;

        axis_dict = {
          "0": {
            "title": "Memory resources usage (Mo)",
            "scale_type": "linear",
            "value_type": "date",
            "zoom_range": gadget.property_dict.date_window
          },
          "1_2": {
            "title": "Memory used percent",
            "position": "right"
          },
          "1_1": {
            "title": "Memory used",
            "position": "right"
          }
        };
        data_list.push({
          value_dict: {"0": [], "1": []},
          type: "surface",
          axis_mapping_id_dict: {"1": "1_2"},
          title: "Memory used"
        });
        for (i = 1; i < gadget.property_dict.mem_data.data.length; i += 1) {
          line_list = gadget.property_dict.mem_data.data[i].split(',');
          data_list[0].value_dict["0"].push(line_list[0]);
          data_list[0].value_dict["1"].push(line_list[2]);
        }
        return gadget.property_dict.graph_mem_used.render({
          value: {
            data: data_list,
            layout: {
              axis_dict : axis_dict,
              title: "Memory resources usage"
            }
          }
        });
      })
      .push(function () {
        //return gadget.element.querySelector('form button[type="submit"]').click();
        return  gadget.getDeclaredGadget('form_cpu_graph')
          .push(function (form_gadget) {
            return form_gadget.getContent();
          })
          .push(function (form_doc) {
            return form_doc.cpu_graph_select_key;
          });
      })
      .push(function (cpu_graph_key) {
        var data_list = [],
          axis_dict = {},
          previous_time = 0,
          line_list,
          graph_index = 1,
          cpu_time_index = -1,
          cpu_graph_dict = {
            cpu_percent: "CPU percent",
            cpu_time: "CPU time",
            cpu_threads: "CPU threads",
            cpu_process: "total process"
          },
          i,
          j;

        function getCPUTime(current) {
          var increment = 0;
          if (previous_time === 0) {
            previous_time = current;
            return 0;
          }
          increment = current - previous_time;
          previous_time = current;
          return increment;
        }

        //"date, total process, CPU percent, CPU time, CPU threads"
        if (gadget.property_dict.process_data.data.length > 0) {
          line_list = gadget.property_dict.process_data.data[0].split(',');
        } else {
          line_list = ["date", "total process", "CPU percent",
                       "CPU time", "CPU threads"];
        }
        for (i = 1; i < line_list.length; i += 1) {
          line_list[i] = line_list[i].trim();
          if (line_list[i] === "CPU time") {
            cpu_time_index = i;
          }
          if (line_list[i] === cpu_graph_dict[cpu_graph_key]) {
            graph_index = i;
            break;
          }
        }
        axis_dict["0"] = {
          "title": line_list[graph_index],
          "scale_type": "linear",
          "value_type": "date",
          "zoom_range": gadget.property_dict.date_window
        };
        axis_dict["1_1"] = {"title": line_list[graph_index], "position": "right"};
        data_list.push({
          value_dict: {"0": [], "1": []},
          type: "line",
          axis_mapping_id_dict: {"1": "1_1"},
          title: line_list[graph_index]
        });
        for (i = 1; i < gadget.property_dict.process_data.data.length; i += 1) {
          line_list = gadget.property_dict.process_data.data[i].split(',');
          for (j = 1; j < line_list.length; j += 1) {
            // Date
            if (j === graph_index) {
              data_list[0].value_dict["0"].push(line_list[0]);
              if (j === cpu_time_index) {
                data_list[0].value_dict["1"].push(getCPUTime(line_list[j]));
              } else {
                data_list[0].value_dict["1"].push(line_list[j]);
              }
            }
          }
        }
        return gadget.property_dict.graph_cpu.render({
          value: {
            data: data_list,
            layout: {
              axis_dict : axis_dict,
              title: "Process resources usage"
            }
          }
        });
      });
  }

  gadget_klass
    .setState({
      opml: "",
      opml_outline: ""
    })
    .ready(function (gadget) {
      gadget.property_dict = {};
      gadget.property_dict.disable_update = true;
      gadget.property_dict.resource_dict = {
        memory_resource: "monitor_resource_memory.data",
        cpu_resource: "monitor_resource_process.data",
        io_resource: "monitor_resource_io.data"
      };
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_memory_used")
        .push(function (graph_memory_used) {
          gadget.property_dict.graph_mem_used = graph_memory_used;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_cpu")
        .push(function (graph_cpu) {
          gadget.property_dict.graph_cpu = graph_cpu;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_io_read")
        .push(function (graph_io_read) {
          gadget.property_dict.graph_io_read = graph_io_read;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_io_write")
        .push(function (graph_io_write) {
          gadget.property_dict.graph_io_write = graph_io_write;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("jio_gadget")
        .push(function (jio_gadget) {
          gadget.property_dict.jio_gadget = jio_gadget;
        });
    })
    .declareMethod("render", function (options) {
      var gadget = this;

      gadget.property_dict.document_key = options.parent_id;
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
              page: 'ojsm_processes_view',
              key: gadget.state.opml_outline.reference
            }}),
            gadget.getUrlFor({command: 'change', options: {
              page: 'ojsm_resources_view',
              key: gadget.state.opml_outline.reference,
              auto_reload: "yes"
            }})
          ]);
        })
        .push(function (url_list) {
          return gadget.updateHeader({
            page_title: gadget.state.opml_outline.title + ": Resources Consumption View",
            front_url: url_list[0],
            processes_url: url_list[1]
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_cpu_graph');
        })
        .push(function (form_view) {
          return form_view.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_graph_auto_update": {
                  "description": "Enable graph content automatic update",
                  "title": "Auto update graph every minutes",
                  "default": "off",
                  "items": [
                    ["Off", "off"],
                    ["On", "on"]
                  ],
                  "css_class": "",
                  "editable": 1,
                  "key": "graph_auto_update_key",
                  "hidden": 0,
                  "type": "ListField"
                },
                "my_cpu_graph_select": {
                  "description": "",
                  "title": "CPU graph to display",
                  "default": "cpu_percent",
                  "items": [
                    ["CPU Percentage", "cpu_percent"],
                    ["CPU Used Time", "cpu_time"],
                    ["CPU Threads Amount", "cpu_threads"],
                    ["Total Process Amount", "cpu_process"]
                  ],
                  "editable": 1,
                  "key": "cpu_graph_select_key",
                  "hidden": 0,
                  "type": "ListField"
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
                "left",
                [["my_graph_auto_update"], ["my_cpu_graph_select"]]
              ],
              [
                "right",
                []
              ],
              [
                "bottom",
                []
              ]]
            }
          });
        })
        .push(function () {
          gadget.property_dict.jio_gadget.createJio({
            type: "webhttp",
            // XXX Fix URL
            url: (gadget.state.opml_outline.url
              .replace("jio_private", "private") + 'documents/'),
            basic_login: gadget.state.opml.basic_login
          });
          gadget.property_dict.mem_data = {data: []};
          gadget.property_dict.process_data = {data: []};
          gadget.property_dict.io_data = {data: []};
          return gadget.deferUpdateGraph();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')
    .declareAcquiredMethod("redirect", "redirect")

    .onLoop(function () {
      if (!this.property_dict.disable_update) {
        return updateGraph(this);
      }
    }, 65000)

    .onEvent('change', function (evt) {
      var gadget = this;
      if (evt.target.getAttribute("name") === "cpu_graph_select_key") {
        updateGraph(gadget, true);
      }
      if (evt.target.getAttribute("name") === "graph_auto_update_key") {
        if (evt.target.value == "on") {
          gadget.property_dict.disable_update = false;
        } else {
          gadget.property_dict.disable_update = true;
        }
      }
    })

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareJob("deferUpdateGraph", function () {

      return updateGraph(this);

    });

}(window, rJS, RSVP));