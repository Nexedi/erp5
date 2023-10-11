/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document*/
(function (window, rJS, domsugar, document) {
  "use strict";

  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 2000,
    DRAW = true,
    LOG = false,
    DRONE_LIST = [
      {"id": 0, "type": "DroneLogAPI", "log_content": ""},
      {"id": 1, "type": "DroneLogAPI", "log_content": ""}
    ],
    WIDTH = 680,
    HEIGHT = 340,
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_simulator_logic.js',
      'gadget_erp5_page_drone_simulator_fixedwingdrone.js',
      'gadget_erp5_page_drone_simulator_dronelogfollower.js'
    ];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

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
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
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
              ], [
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
      var gadget = this, dist, fragment = gadget.element.querySelector('.simulator_div'),
        game_parameters_json, log_1_entry_list, log_2_entry_list, map_info,
        span = document.querySelector('#distance');
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
      function getLogEntries(log) {
        var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
          log_header_found;
        for (i = 0; i < line_list.length; i += 1) {
          if (log_header_found || line_list[i].includes("timestamp (ms);")) {
            log_header_found = true;
            if (line_list[i].indexOf("AMSL") < 0 &&
                line_list[i].includes(";")) {
              log_entry = line_list[i].trim();
              if (log_entry) {
                log_entry = log_entry.split(';');
                log_entry_list.push(log_entry);
              }
            }
          }
        }
        return log_entry_list;
      }
      function averageLogDistance(a, b, z) {
        function distance3D(p1, p2) {
          return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                           Math.pow(p1[1] - p2[1], 2) +
                           Math.pow(p1[2] - p2[2], 2));
        }
        var d, i, sum = 0, point_a, point_b, penalization = 0, length;
        for (i = 0; i < a.length; i += 1) {
          if (b[i]) {
            point_a = [a[i][1], a[i][1]];
            point_b = [b[i][1], b[i][1]];
            if (z) {
              sum += distance3D(point_a, point_b);
            } else {
              d = latLonDistance(point_a, point_b);
              sum += d;
            }
          }
        }
        length = Math.min(a.length, b.length);
        if (Math.abs(a.length - b.length) > 50) {
          //penalize very different logs
          penalization = Math.abs(a.length - b.length);
        }
        return sum / length + penalization;
      }
      log_1_entry_list = getLogEntries(options.log_1);
      log_2_entry_list = getLogEntries(options.log_2);
      dist = averageLogDistance(log_1_entry_list, log_2_entry_list, false);
      if (isNaN(dist)) {
        return gadget.notifySubmitted({message: 'Invalid log content', status: 'error'});
      }
      span.textContent = 'Average flights distance: ' +
        Math.round(dist * 100) / 100;
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      DRONE_LIST[0].log_content = options.log_1;
      DRONE_LIST[1].log_content = options.log_2;
      function generateMapInfo(list_1, list_2) {
        var all = list_1.concat(list_2), i,
          min_lat = 999, min_lon = 999,
          max_lat = 0, max_lon = 0;
        for (i = 0; i < all.length; i += 1) {
          if (all[i][1] < min_lat) {
            min_lat = all[i][1];
          }
          if (all[i][1] > max_lat) {
            max_lat = all[i][1];
          }
          if (all[i][2] < min_lon) {
            min_lon = all[i][2];
          }
          if (all[i][2] > max_lon) {
            max_lon = all[i][2];
          }
        }
        return {
          "min_lat": min_lat,
          "max_lat": max_lat,
          "min_lon": min_lon,
          "max_lon": max_lon,
          "start_AMSL": all[0][3] - all[0][4],
          "init_pos_lat": all[0][1],
          "init_pos_lon": all[0][2],
          "init_pos_alt": all[0][4]
        };
      }
      map_info = generateMapInfo(log_1_entry_list, log_2_entry_list);
      options.min_lat = map_info.min_lat;
      options.max_lat = map_info.max_lat;
      options.min_lon = map_info.min_lon;
      options.max_lon = map_info.max_lon;
      options.map_height = 100;
      options.start_AMSL = map_info.start_AMSL;
      options.init_pos_lon = map_info.init_pos_lon;
      options.init_pos_lat = map_info.init_pos_lat;
      options.init_pos_alt = map_info.init_pos_alt;
      game_parameters_json = {
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
        "map": {
          "min_lat": parseFloat(options.min_lat),
          "max_lat": parseFloat(options.max_lat),
          "min_lon": parseFloat(options.min_lon),
          "max_lon": parseFloat(options.max_lon),
          "height": parseFloat(options.map_height),
          "start_AMSL": parseFloat(options.start_AMSL)
        },
        "initialPosition": {
          "longitude": parseFloat(options.init_pos_lon),
          "latitude": parseFloat(options.init_pos_lat),
          "altitude": parseFloat(options.init_pos_alt)
        },
        "draw_flight_path": DRAW,
        "log_drone_flight": LOG,
        "temp_flight_path": false,
        "droneList": DRONE_LIST
      };
      return gadget.declareGadget("babylonjs.gadget.html",
                                  {element: fragment, scope: 'simulator'})
        .push(function () {
          return gadget.getDeclaredGadget('form_view_babylonjs');
        })
        .push(function (form_gadget) {
          return form_gadget.render({
            erp5_document: {
              "_embedded": {"_view": {
                "my_babylonjs": {
                  "default": "",
                  "css_class": "",
                  "required": 0,
                  "editable": 1,
                  "key": "babylonjs",
                  "hidden": 0,
                  "type": "GadgetField",
                  "url": "babylonjs.gadget.html",
                  "sandbox": "public",
                  "renderjs_extra": '{"autorun": false, "width": ' + WIDTH + ', ' +
                    '"height": ' + HEIGHT + ', ' +
                    '"logic_file_list": ' + JSON.stringify(LOGIC_FILE_LIST) + ', ' +
                    '"game_parameters": ' + JSON.stringify(game_parameters_json) +
                    '}'
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
                "bottom",
                [["my_babylonjs"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('form_view_babylonjs');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        });
    });

}(window, rJS, domsugar, document));