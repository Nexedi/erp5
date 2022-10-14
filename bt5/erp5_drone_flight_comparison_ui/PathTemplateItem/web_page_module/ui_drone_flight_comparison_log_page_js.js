(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1500,
    DRAW = true,
    LOG = false,
    DRONE_LIST = [
      {"id": 0, "type": "DroneLogAPI", "log_content": ""},
      {"id": 1, "type": "DroneLogAPI", "log_content": ""}
    ];

  function latLonDistance(c1, c2) {
    var R = 6371e3,
      q1 = c1[0] * Math.PI / 180,
      q2 = c2[0] * Math.PI / 180,
      dq = (c2[0] - c1[0]) * Math.PI / 180,
      dl = (c2[1] - c1[1]) * Math.PI / 180,
      a = Math.sin(dq / 2) * Math.sin(dq / 2) +
        Math.cos(q1) * Math.cos(q2) *
        Math.sin(dl / 2) * Math.sin(dl / 2),
      c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }
  function averageDistance(a, b, z) {
    function distance3D(p1, p2) {
      return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                       Math.pow(p1[1] - p2[1], 2) +
                       Math.pow(p1[2] - p2[2], 2));
    }
    var i, sum = 0;
    for (i = 0; i < a.length; i++) {
      if (b[i]) {
        if (z) {
          sum += distance3D(a[i], b[i]);
        } else {
          sum += latLonDistance(a[i], b[i]);
        }
      }
    }
    /*if (Math.abs(a.length - b.length) > 50) {
      //penalize very different logs ?
      sum += 100;
    }*/
    return sum / a.length;
  }
  function getLogEntries(log) {
    var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
      log_header_found;
    for (i = 0; i < line_list.length; i += 1) {
      if (!log_header_found && !line_list[i].includes("timestamp;")) {
        continue;
      } else {
        log_header_found = true;
      }
      if (line_list[i].indexOf("AMSL") >= 0 ||
          !line_list[i].includes(";")) {
        continue;
      }
      log_entry = line_list[i].trim();
      if (log_entry) {
        log_entry_list.push(log_entry);
      }
    }
    return log_entry_list;
  }

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (input) {
          gadget.runGame(input);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('input[type="submit"]').click();
    })

    .declareMethod('render', function render() {
      var gadget = this, query;
      return new RSVP.Queue()
        .push(function () {
          query = '(portal_type:"Web Manifest") AND (reference:"loiter_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          DRONE_LIST[0].log_content = result.data.rows[0].value.text_content;
          //query = '(portal_type:"Web Manifest") AND (reference:"bounce_flight_log")';
          query = '(portal_type:"Web Manifest") AND (reference:"result_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          DRONE_LIST[1].log_content = result.data.rows[0].value.text_content;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_simulation_speed": {
                  "description": "",
                  "title": "Simulation Speed",
                  "default": SIMULATION_SPEED,
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "simulation_speed",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_log_1": {
                  "description": "Log 1 content",
                  "title": "",
                  "default": DRONE_LIST[0].log_content,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "log_1",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_log_2": {
                  "description": "Log 2 content",
                  "title": "",
                  "default": DRONE_LIST[1].log_content,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "log_2",
                  "hidden": 0,
                  "type": "TextAreaField"
                }
              }},
              "_links": {
                "type": {
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_log_1"], ["my_simulation_speed"]]
              ],[
                "right",
                [["my_log_2"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Run flight logs',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this, simulator;
      return new RSVP.Queue()
        .push(function () {
          console.log("log 1 entries:", getLogEntries(options.log_1));
          console.log("log 2 entries:", getLogEntries(options.log_2));
          var span = document.querySelector('#distance'),
            //dist_2 = averageDistance(getLogEntries(options.log_2), getLogEntries(options.log_1), false),
            dist = averageDistance(getLogEntries(options.log_1), getLogEntries(options.log_2), false);
          span.textContent = 'Average flights distance: ' +
            Math.round(dist * 100) / 100;
          var fragment = gadget.element.querySelector('#fragment');
          //drop previous execution
          if (fragment.childNodes[0]) {
            fragment.removeChild(fragment.childNodes[0]);
          }
          fragment = domsugar(gadget.element.querySelector('#fragment'),
                                  [domsugar('div')]).firstElementChild;
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          simulator = drone_gadget;
          return simulator.render();
        })
        .push(function () {
          DRONE_LIST[0].log_content = options.log_1;
          DRONE_LIST[1].log_content = options.log_2;
          var game_parameters_json = {
            "drone": {
              "maxAcceleration": 1,
              "maxSpeed": 1
            },
            "gameTime": SIMULATION_TIME,
            "simulation_speed": parseFloat(options.simulation_speed),
            "latency": {
              "information": 0,
              "communication": 0
            },
            "draw_flight_path": DRAW,
            "log_drone_flight": LOG,
            "droneList": DRONE_LIST
          };
          return simulator.runGame({
            game_parameters: game_parameters_json
          });
        });
    });

}(window, RSVP, rJS, domsugar, document, Blob));