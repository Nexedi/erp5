/*global window, rJS, RSVP, Handlebars, $, console */
/*jslint nomen: true, indent: 2, maxerr: 3*/
(function (window, rJS, RSVP, Handlebars, $, console) {
  "use strict";

  var gadget_klass = rJS(window),
    templater = gadget_klass.__template_element,
    graph_labels_widget = Handlebars.compile(
      templater.getElementById("graph-label-widget-template").innerHTML
    );

  gadget_klass
    .setState({
      opml: "",
      opml_outline: "",
      breadcrumb_gadget: ""
    })
    .ready(function (gadget) {
      gadget.property_dict = {};
      return gadget.getElement()
        .push(function (element) {
          gadget.property_dict.element = element;
          gadget.property_dict.render_deferred = RSVP.defer();
          gadget.property_dict.ressource_dict = {
            memory_resource: "monitor_resource_memory.data",
            cpu_resource: "monitor_resource_process.data",
            io_resource: "monitor_resource_io.data"
          };
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("breadcrumb_gadget")
        .push(function (breadcrumb_gadget) {
          return gadget.changeState({breadcrumb_gadget: breadcrumb_gadget});
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_memory_used")
        .push(function (graph_memory_used) {
          gadget.property_dict.graph_mem_used = graph_memory_used;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_memory_percent")
        .push(function (graph_memory_percent) {
          gadget.property_dict.graph_mem_percent = graph_memory_percent;
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
      return gadget.getDeclaredGadget("graph_io_counter")
        .push(function (graph_io_counter) {
          gadget.property_dict.graph_io_counter = graph_io_counter;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_io_rw")
        .push(function (graph_io_rw) {
          gadget.property_dict.graph_io_rw = graph_io_rw;
        });
    })
    .ready(function (gadget) {
      return gadget.getDeclaredGadget("graph_disk_used")
        .push(function (graph_disk_used) {
          gadget.property_dict.graph_disk_used = graph_disk_used;
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

      function loadGraphData(key) {
        var resource_key = gadget.property_dict.ressource_dict[key];
        return gadget.property_dict.jio_gadget.get(resource_key)
          .push(undefined, function (error) {
            console.log(error);
            $.notify(
              "Error: Failed to download resource file '" + resource_key +
                "' from URL: " + gadget.state.opml_outline.url,
              {
                  position: "top right",
                  autoHideDelay: 7000,
                  className: "error"
                }
            );
            return {
              data: []
            };
          })
          .push(function (jio_element) {
            if (!jio_element.hasOwnProperty('data')) {
              return {data: []};
            }
            switch (key) {
            case "memory_resource":
              gadget.property_dict.mem_data = jio_element;
              break;
            case "cpu_resource":
              gadget.property_dict.process_data = jio_element;
              if (jio_element.data.length > 0) {
                gadget.property_dict.graph_cpu_label_list = jio_element.data[0].split(',');
              }
              break;
            case "io_resource":
              gadget.property_dict.io_data = jio_element;
              break;
            }
            return jio_element;
          });
      }

      return gadget.updateHeader({
        title: "Monitoring resources view"
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
            icon: "desktop",
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
                title: "Resource consumption"
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
          for (key in gadget.property_dict.ressource_dict) {
            if (gadget.property_dict.ressource_dict.hasOwnProperty(key)) {
              promise_list.push(loadGraphData(key));
            }
          }
          return RSVP.all(promise_list);
        })
        .push(function () {
          return gadget.property_dict.render_deferred.resolve();
        });
    })

    .declareAcquiredMethod("getUrlFor", "getUrlFor")
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod('jio_allDocs', 'jio_allDocs')
    .declareAcquiredMethod('jio_get', 'jio_get')

    /////////////////////////////////////////////////////////////////
    // declared service
    /////////////////////////////////////////////////////////////////
    .declareService(function () {
      var gadget = this,
        date_window = [];

      function toggleSerieVisibility(evt) {
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
      }

      function updateIOData() {
        var i,
          element,
          prev_element,
          date_diff,
          io_data = "";

        function convertElement(element) {
          var element_list = element.split(',');
          return [
            element_list[0],
            parseFloat(element_list[1].trim()),
            parseFloat(element_list[2].trim()),
            element_list[3].trim()
          ];
        }
        if (gadget.property_dict.io_data.data.length > 1) {
          prev_element = convertElement(gadget.property_dict.io_data.data[1]);
          io_data = gadget.property_dict.io_data.data[0];
          for (i = 2; i < gadget.property_dict.io_data.data.length; i += 1) {
            element = convertElement(gadget.property_dict.io_data.data[i]);
            date_diff = (new Date(element[0]).getTime() - new Date(prev_element[0]).getTime()) / 1000;
            io_data += "\n" + element[0] + "," +
              (element[1] - prev_element[1]) / (1024 * date_diff) +
              "," + (element[2] - prev_element[2]) / 1000 + "," + element[3];
            prev_element = element;
          }
        }
        gadget.property_dict.io_data_csv = io_data;
      }

      function formatDateToString(d) {
        return d.toISOString().slice(0,10) + ' ' + d.getHours() + ':' + d.getMinutes() + ':' + d.getSeconds();
      }

      function getDateWindow(data) {
        var max_date,
          begin_date,
          end_date,
          date_window = [];
        gadget.property_dict.timer = null;
        gadget.property_dict.loading = false;
        if (data.length > 0) {
          max_date = data[data.length - 1].split(',')[0];
          begin_date = new Date(max_date);
          end_date = new Date(max_date);
          begin_date.setHours(begin_date.getHours() -2);
          date_window = [Date.parse(begin_date), Date.parse(end_date)];
        }
        return date_window;
      }

      function updateGraphData (key) {
        return gadget.property_dict.jio_gadget.get(gadget.property_dict.ressource_dict[key])
          .push(function (jio_element) {
            if (!jio_element.hasOwnProperty('data')) {
              return {};
            }
            // FIX
            //jio_element.data[0] = jio_element.data[0].replace('%', 'percent');
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
              default:
                
            }
            return jio_element;
          });
      }

      function updateGraph () {
        return new RSVP.Queue()
          .push(function () {
            var key,
              promise_list = [];
            for (key in gadget.property_dict.ressource_dict) {
              promise_list.push(updateGraphData(key));
            }
            return RSVP.all(promise_list);
          })
          .push(function () {
            date_window = getDateWindow(gadget.property_dict.mem_data.data);
            return gadget.property_dict.graph_mem_used.updateOptions({
              file: gadget.property_dict.mem_data.data.join('\n'),
              dateWindow: date_window
            });
          })
          .push(function () {
            return gadget.property_dict.graph_mem_percent.updateOptions({
              file: gadget.property_dict.mem_data.data.join('\n'),
              dateWindow: date_window
            });
          })
          .push(function () {
            updateIOData();
            return gadget.property_dict.graph_io_rw.updateOptions({
              file: gadget.property_dict.io_data_csv,
              dateWindow: date_window
            });
          })
          .push(function () {
            return gadget.property_dict.graph_io_counter.updateOptions({
              file: gadget.property_dict.io_data_csv,
              dateWindow: date_window
            });
          })
          .push(function () {
            return gadget.property_dict.graph_disk_used.updateOptions({
              file: gadget.property_dict.io_data_csv,
              dateWindow: date_window
            });
          })
          .push(function () {
            return gadget.property_dict.graph_cpu.updateOptions({
              file: gadget.property_dict.process_data.data.join('\n'),
              dateWindow: date_window
            });
          });
      }

      function updateGraphTimer() {
        if (gadget.property_dict.loading && gadget.property_dict.timer) {
          clearInterval(gadget.property_dict.timer);
        }
        gadget.property_dict.timer = setInterval(function(){
            var hash = window.location.toString().split('#')[1];
            if (hash.indexOf('page=resource_view') < 0) {
              clearInterval(gadget.property_dict.timer);
              return;
            }
            updateGraph();
          },
          65000);
      }

      return new RSVP.Queue()
        .push(function () {
          return gadget.property_dict.render_deferred.promise;
        })
        .push(function () {
          date_window = getDateWindow(gadget.property_dict.mem_data.data);

          return gadget.property_dict.graph_mem_used.render(
            gadget.property_dict.mem_data.data.join('\n'),
            {
              xlabel: '<span class="graph-label"><i class="fa fa-area-chart"></i> Memory used (Mo)</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              legend: 'always',
              visibility: [false, true],
              dateWindow: date_window,
              fillGraph: true
            },
            "customInteractionModel"
          );
        })
        .push(function () {
          return gadget.property_dict.graph_mem_percent.render(
            gadget.property_dict.mem_data.data.join('\n'),
            {
              xlabel: '<span class="graph-label"><i class="fa fa-area-chart"></i> Memory used %</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              legend: 'always',
              visibility: [true, false],
              dateWindow: date_window,
              fillGraph: true
            },
            "customInteractionModel"
          );
        })
        .push(function () {
          updateIOData();
          return gadget.property_dict.graph_io_rw.render(
            gadget.property_dict.io_data_csv,
            {
              xlabel: '<span class="graph-label"><i class="fa fa-bar-chart"></i> IO RW KBytes/s</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              legend: 'always',
              visibility: [true, false, false],
              dateWindow: date_window,
              fillGraph: true
            },
            "customInteractionModel"
          );
        })
        .push(function () {
          return gadget.property_dict.graph_io_counter.render(
            gadget.property_dict.io_data_csv,
            {
              xlabel: '<span class="graph-label"><i class="fa fa-bar-chart"></i> IO RW counter/1000</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              legend: 'always',
              visibility: [false, true, false],
              dateWindow: date_window,
              fillGraph: true
            },
            "customInteractionModel"
          );
        })
        .push(function () {
          return gadget.property_dict.graph_disk_used.render(
            gadget.property_dict.io_data_csv,
            {
              xlabel: '<span class="graph-label"><i class="fa fa-pie-chart"></i> Disk Used (Mo)</span>',
              labelsDivStyles: { 'textAlign': 'right' },
              legend: 'always',
              visibility: [false, false, true],
              dateWindow: date_window,
              fillGraph: true
            },
            "customInteractionModel"
          );
        })
        .push(function () {
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
                //return promise_list.push(renderGraphLabel(gadget, color_list, label_list, element));
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
                /*return RSVP.all([
                  $(gadget.property_dict.element.querySelectorAll("[type=checkbox]"))
                  .checkboxradio()]);*/
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
        });
    });

}(window, rJS, RSVP, Handlebars, $, console));