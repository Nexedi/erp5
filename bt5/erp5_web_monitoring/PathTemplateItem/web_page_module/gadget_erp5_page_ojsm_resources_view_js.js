/*global window, rJS, RSVP, console */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, console) {
  "use strict";

  var gadget_klass = rJS(window);


  function loadGraphData(gadget, key) {
    var resource_key = gadget.property_dict.ressource_dict[key];
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
      axis_dict = {};

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
    line_list = ["date", "io rw count (Kb/s)", "io cycles count (/1000)"]; //, "disk used"];
    axis_dict["0"] = {
      "title": "IO resources usage",
      "scale_type": "linear",
      "value_type": "date",
      "zoom_range": date_window
    };
    for (i = 1; i < line_list.length; i += 1) {
      line_list[i] = line_list[i].trim();
      data_list.push({
        value_dict: {"0": [], "1": []},
        type: "surface",
        axis_mapping_id_dict: {"1": "1_" + i},
        title: line_list[i]
      });
      axis_dict["1_" + i] = {"title": line_list[i], "position": "right"};
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
    return {
      value: {
        data: data_list,
        layout: {
          axis_dict : axis_dict,
          title: "IO resources usage"
        }
      }
    };
  }

  function getDateWindow(data) {
    var max_date,
      begin_date,
      end_date,
      date_window = [];
    if (data.length > 0) {
      max_date = data[data.length - 1].split(',')[0];
      begin_date = new Date(max_date);
      end_date = new Date(max_date);
      begin_date.setHours(begin_date.getHours() - 2);
      date_window = [Date.parse(begin_date), Date.parse(end_date)];
    }
    return date_window;
  }

  function updateGraph(gadget) {
    return new RSVP.Queue()
      .push(function () {
        var key,
          promise_list = [];
        for (key in gadget.property_dict.ressource_dict) {
          promise_list.push(loadGraphData(gadget, key));
        }
        return RSVP.all(promise_list);
      })
      .push(function () {
        var data = updateIOData(gadget, gadget.property_dict.date_window);
        return gadget.property_dict.graph_io.render(data);
      })
      .push(function () {
        var data_list = [],
          axis_dict = {},
          line_list,
          i,
          j;

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
        /*data_list.push({
          value_dict: {"0": [], "1": []},
          type: "surface",
          axis_mapping_id_dict: {"1": "1_1"},
          title: "Memory used percent"
        });*/
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
        var data_list = [],
          axis_dict = {},
          previous_time = 0,
          line_list,
          cpu_time_index = -1,
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
        axis_dict["0"] = {
          "title": "Process resources usage",
          "scale_type": "linear",
          "value_type": "date",
          "zoom_range": gadget.property_dict.date_window
        };
        for (i = 1; i < line_list.length; i += 1) {
          line_list[i] = line_list[i].trim();
          data_list.push({
            value_dict: {"0": [], "1": []},
            type: "line",
            axis_mapping_id_dict: {"1": "1_" + i},
            title: line_list[i]
          });
          if (line_list[i] === "CPU time") {
            cpu_time_index = i;
          }
          axis_dict["1_" + i] = {"title": line_list[i], "position": "right"};
        }
        for (i = 1; i < gadget.property_dict.process_data.data.length; i += 1) {
          line_list = gadget.property_dict.process_data.data[i].split(',');
          for (j = 1; j < line_list.length; j += 1) {
            // XXX - repeating date everytime
            data_list[j - 1].value_dict["0"].push(line_list[0]);
            if (j === cpu_time_index) {
              data_list[j - 1].value_dict["1"].push(getCPUTime(line_list[j]));
            } else {
              data_list[j - 1].value_dict["1"].push(line_list[j]);
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
      gadget.property_dict.render_deferred = RSVP.defer();
      gadget.property_dict.ressource_dict = {
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
          gadget.property_dict.graph_cpu_label_list = [];
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_io")
        .push(function (graph_io) {
          gadget.property_dict.graph_io = graph_io;
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

      gadget.property_dict.document_key = options.key;
      return gadget.jio_get(options.key)
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
          gadget.property_dict.jio_gadget.createJio({
            type: "webhttp",
            // XXX Fix URL
            url: (gadget.state.opml_outline.url
              .replace("jio_private", "private") +
              'documents/'),
            basic_login: gadget.state.opml.basic_login
          });
          gadget.property_dict.mem_data = {data: []};
          gadget.property_dict.process_data = {data: []};
          gadget.property_dict.io_data = {data: []};
          return gadget.property_dict.render_deferred.resolve();
        });
    })

    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_get', 'jio_get')
    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("notifySubmitted", 'notifySubmitted')

    .onLoop(function () {
      return updateGraph(this);
    }, 65000)

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        date_window = [];

      /*function toggleSerieVisibility(evt) {
        var checkbox = evt.target.nextSibling,
          index = $(evt.target).attr('rel');
        if ($(checkbox).prop("checked")) {
          $(checkbox).prop("checked", false).checkboxradio("refresh");
        } else {
          $(checkbox).prop("checked", true).checkboxradio("refresh");
        }
        return gadget.property_dict.graph_cpu.setVisibility(parseInt(index, 10), $(checkbox).prop("checked"))
          .push(function () {
            return evt;
          });
      }*/

      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        /**.push(function () {
          return gadget.property_dict.graph_cpu.render(
            gadget.property_dict.process_data.data.join('\n'),
            {
              xlabel: '<span class="graph-label"><i class="fa fa-line-chart"></i> Process resources usage</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              dateWindow: date_window,
            },
            "customInteractionModel"
          );
        })
        .push(function () {
          var label_list = gadget.property_dict.graph_cpu_label_list,
            element = 'graph_cpu';
          if (gadget.property_dict.graph_cpu_label_list.length > 0) {
            label_list = label_list.slice(1); // remove date column
            return gadget.property_dict.graph_cpu.getColors()
              .push(function (color_list) {
                var label_content,
                  name_list = [],
                  i;
                for (i = 0; i < label_list.length; i += 1) {
                  name_list.push({
                    name: label_list[i],
                    id: "label_" + label_list[i].trim().replace(/\s/g, '_'),
                    color: color_list[i],
                    graph: element,
                    index: i
                  });
                }
                label_content = graph_labels_widget({
                  label_list: name_list
                });
                gadget.property_dict.element.querySelector(".ui-panel-overview ." + element + " .ui-grid-span-1")
                  .innerHTML = label_content;
                  return $(gadget.property_dict.element.querySelectorAll("[data-role=controlgroup]"))
                    .controlgroup().controlgroup("refresh");
              });
          }
        })
        .push(function () {
          var promise_list = [],
            element_list = gadget.property_dict.element.querySelectorAll("label.graph_cpu"),
            i;
          for (i = 0; i < element_list.length; i += 1) {
            promise_list.push(
              loopEventListener(
                element_list[i],
                'click',
                false,
                toggleSerieVisibility
              )
            );
            if ($(element_list[i]).attr('for').toLowerCase() !== 'label_cpu_percent' && $(element_list[i]).attr('for').toLowerCase() !== 'label_total_process') {
              promise_list.push(gadget.property_dict.graph_cpu.setVisibility(
                parseInt($(element_list[i]).attr('rel'), 10), false)
              );
              promise_list.push($(element_list[i]).click());
            }
          }
          RSVP.all(promise_list);
          return updateGraphTimer();
        })**/
        .push(function () {
          return updateGraph(gadget);
        });
    });

}(window, rJS, RSVP, console));