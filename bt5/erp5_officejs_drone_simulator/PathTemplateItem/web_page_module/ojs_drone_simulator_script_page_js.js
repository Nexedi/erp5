/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, Blob*/
(function (window, rJS, domsugar, document, Blob) {
  "use strict";

  //Default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1500,
    min_lat = 45.6364,
    max_lat = 45.65,
    min_lon = 14.2521,
    max_lon = 14.2766,
    map_height = 100,
    start_AMSL = 595,
    DEFAULT_SPEED = 16,
    MAX_ACCELERATION = 6,
    MAX_DECELERATION = 1,
    MIN_SPEED = 12,
    MAX_SPEED = 26,
    MAX_ROLL = 35,
    MIN_PITCH = -20,
    MAX_PITCH = 25,
    MAX_CLIMB_RATE = 8,
    MAX_SINK_RATE = 3,
    MAX_COMMAND_FREQUENCY = 2,
    INITIAL_POSITION = {
      "latitude": 45.6412,
      "longitude": 14.2658,
      "altitude": 15
    },
    NUMBER_OF_DRONES = 2,
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      '/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */\n' +
      '/*global console, me*/\n' +
      '\n' +
      '(function (console, me) {\n' +
      '  "use strict";\n' +
      '\n' +
      '  var ALTITUDE = 100,\n' +
      '    EPSILON = 9,\n' +
      '    CHECKPOINT_LIST = [],\n' +
      '    DIRECTION_LIST = [\n' +
      '      {\n' +
      '        distance: 1053,\n' +
      '        bearing: 293\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 800,\n' +
      '        bearing: 104\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 669,\n' +
      '        bearing: 352\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 925,\n' +
      '        bearing: 162\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 690,\n' +
      '        bearing: 47\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 935,\n' +
      '        bearing: 166\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 1129,\n' +
      '        bearing: 289\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 520,\n' +
      '        bearing: 94\n' +
      '      }\n' +
      '    ],\n' +
      '    R = 6371e3 // meters;\n' +
      '\n' +
      '  function to_deg(rad) {\n' +
      '    return rad * 180 / Math.PI;\n' +
      '  }\n' +
      '\n' +
      '  function to_rad(deg) {\n' +
      '    return deg * Math.PI / 180;\n' +
      '  }\n' +
      '\n' +
      '  function set_checkpoints(lat, lon) {\n' +
      '    var bearing_rad,\n' +
      '      lat_end,\n' +
      '      lon_end,\n' +
      '      lat_start = to_rad(lat),\n' +
      '      lon_start = to_rad(lon),\n' +
      '      relative_d;\n' +
      '\n' +
      '    DIRECTION_LIST.forEach(function (e) {\n' +
      '      bearing_rad = to_rad(e.bearing);\n' +
      '      relative_d = e.distance / R;\n' +
      '\n' +
      '      lat_end = Math.asin(Math.sin(lat_start) * Math.cos(relative_d)\n' +
      '        + Math.cos(lat_start) * Math.sin(relative_d) * Math.cos(bearing_rad));\n' +
      '      lon_end = lon_start + Math.atan2(\n' +
      '        Math.sin(bearing_rad) * Math.sin(relative_d) * Math.cos(lat_start),\n' +
      '        Math.cos(relative_d) - Math.sin(lat_start) * Math.sin(lon_start));\n' +
      '\n' +
      '      CHECKPOINT_LIST.push({' +
      '        latitude: to_deg(lat_end),\n' +
      '        longitude: to_deg(lon_end)\n' +
      '      });\n' +
      '\n' +
      '      lat_start = lat_end;\n' +
      '      lon_start = lon_end;\n' +
      '    });\n' +
      '  }\n' +
      '\n' +
      '  function distance(lat1, lon1, lat2, lon2) {\n' +
      '    var la1 = lat1 * Math.PI / 180, // lat, lon in radians\n' +
      '      la2 = lat2 * Math.PI / 180,\n' +
      '      lo1 = lon1 * Math.PI / 180,\n' +
      '      lo2 = lon2 * Math.PI / 180,\n' +
      '      haversine_phi = Math.pow(Math.sin((la2 - la1) / 2), 2),\n' +
      '      sin_lon = Math.sin((lo2 - lo1) / 2),\n' +
      '      h = haversine_phi + Math.cos(la1) * Math.cos(la2) * sin_lon * sin_lon;\n' +
      '    return 2 * R * Math.asin(Math.sqrt(h));\n' +
      '  }\n' +
      '\n' +
      '  me.onStart = function (timestamp) {\n' +
      '    me.direction_set = false;\n' +
      '    me.next_checkpoint = 0;\n' +
      '    me.takeOff();\n' +
      '  };\n' +
      '\n' +
      '  me.onUpdate = function (timestamp) {\n' +
      '    if (!me.isReadyToFly()) {\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    me.current_position = me.getCurrentPosition();\n' +
      '    if (CHECKPOINT_LIST.length === 0) {\n' +
      '      set_checkpoints(me.current_position.latitude,\n' +
      '                      me.current_position.longitude);\n' +
      '    }\n' +
      '\n' +
      '    if (!me.direction_set) {\n' +
      '      if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '        me.setTargetCoordinates(\n' +
      '          CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '          CHECKPOINT_LIST[me.next_checkpoint].longitude,\n' +
      '          ALTITUDE + ALTITUDE * me.id,\n' +
      '          ' + DEFAULT_SPEED + '\n' +
      '        );\n' +
      '        console.log("[DEMO] Going to Checkpoint", me.next_checkpoint);\n' +
      '      }\n' +
      '      me.direction_set = true;\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '      me.current_position = me.getCurrentPosition();\n' +
      '      me.distance = distance(\n' +
      '        me.current_position.latitude,\n' +
      '        me.current_position.longitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].longitude\n' +
      '      );\n' +
      '      if (me.distance <= EPSILON) {\n' +
      '        console.log("[DEMO] Reached Checkpoint", me.next_checkpoint);\n' +
      '        me.next_checkpoint += 1;\n' +
      '        me.direction_set = false;\n' +
      '      }\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    if (!me.isLanding()) {\n' +
      '      me.land();\n' +
      '    }\n' +
      '    if (me.getCurrentPosition().altitude <= 0) {\n' +
      '      me.exit(0);\n' +
      '    }\n' +
      '  };\n' +
      '}(console, me));\n',
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    ONUPDATE_INTERVAL = 100,
    DRONE_LIST = [],
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

    .allowPublicAcquisition('notifySubmit', function () {
      return this.triggerSubmit();
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('input[type="submit"]').click();
    })

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
                  "required": 1,
                  "editable": 1,
                  "key": "simulation_speed",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_simulation_time": {
                  "description": "Duration of the simulation (in seconds)",
                  "title": "Simulation Time",
                  "default": SIMULATION_TIME,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "simulation_time",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_onupdate_interval": {
                  "description": "Minimum interval (in milliseconds) between 2 executions of onUpdate function as well as periodicity to send telemetry to the swarm",
                  "title": "OnUpdate interval",
                  "default": ONUPDATE_INTERVAL,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "onupdate_interval",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_drone_min_speed": {
                  "description": "",
                  "title": "Drone min speed",
                  "default": MIN_SPEED,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_min_speed",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_drone_speed": {
                  "description": "",
                  "title": "Drone speed",
                  "default": DEFAULT_SPEED,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_speed",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_speed": {
                  "description": "",
                  "title": "Drone max speed",
                  "default": MAX_SPEED,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_speed",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_drone_max_acceleration": {
                  "description": "",
                  "title": "Drone max Acceleration",
                  "default": MAX_ACCELERATION,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_acceleration",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_deceleration": {
                  "description": "",
                  "title": "Drone max Deceleration",
                  "default": MAX_DECELERATION,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_deceleration",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_drone_max_roll": {
                  "description": "",
                  "title": "Drone max roll",
                  "default": MAX_ROLL,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_roll",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_min_pitch": {
                  "description": "",
                  "title": "Drone min pitch",
                  "default": MIN_PITCH,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_min_pitch",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_pitch": {
                  "description": "",
                  "title": "Drone max pitch",
                  "default": MAX_PITCH,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_pitch",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_sink_rate": {
                  "description": "",
                  "title": "Drone max sink rate",
                  "default": MAX_SINK_RATE,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_sink_rate",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_climb_rate": {
                  "description": "",
                  "title": "Drone max climb rate",
                  "default": MAX_CLIMB_RATE,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_climb_rate",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_drone_max_command_frequency": {
                  "description": "",
                  "title": "Drone max command frequency",
                  "default": MAX_COMMAND_FREQUENCY,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_max_command_frequency",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_minimum_latitud": {
                  "description": "",
                  "title": "Minimum latitude",
                  "default": min_lat,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "min_lat",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_maximum_latitud": {
                  "description": "",
                  "title": "Maximum latitude",
                  "default": max_lat,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "max_lat",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_minimum_longitud": {
                  "description": "",
                  "title": "Minimum longitude",
                  "default": min_lon,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "min_lon",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_maximum_longitud": {
                  "description": "",
                  "title": "Maximum longitude",
                  "default": max_lon,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "max_lon",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_start_AMSL": {
                  "description": "",
                  "title": "Start AMSL",
                  "default": start_AMSL,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "start_AMSL",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_map_height": {
                  "description": "",
                  "title": "Map Height",
                  "default": map_height,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "map_height",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_init_pos_lon": {
                  "description": "",
                  "title": "Initial drone longitude",
                  "default": INITIAL_POSITION.longitude,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_lon",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_init_pos_lat": {
                  "description": "",
                  "title": "Initial drone latitude",
                  "default": INITIAL_POSITION.latitude,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_lat",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_init_pos_alt": {
                  "description": "",
                  "title": "Initial drone altitude",
                  "default": INITIAL_POSITION.altitude,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_alt",
                  "hidden": 0,
                  "type": "FloatField"
                },
                "my_number_of_drones": {
                  "description": "",
                  "title": "Number of drones",
                  "default": NUMBER_OF_DRONES,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "number_of_drones",
                  "hidden": 0,
                  "type": "IntegerField"
                },
                "my_script": {
                  "default": DEFAULT_SCRIPT_CONTENT,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "script",
                  "hidden": 0,
                  "type": "GadgetField",
                  "renderjs_extra": '{"editor": "codemirror", "maximize": true}',
                  "url": "gadget_editor.html",
                  "sandbox": "public"
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
                [["my_simulation_speed"], ["my_simulation_time"], ["my_onupdate_interval"],
                  ["my_number_of_drones"], ["my_minimum_latitud"], ["my_maximum_latitud"],
                  ["my_minimum_longitud"], ["my_maximum_longitud"],
                  ["my_init_pos_lat"], ["my_init_pos_lon"], ["my_init_pos_alt"],
                  ["my_map_height"]]
              ], [
                "right",
                [["my_start_AMSL"], ["my_drone_min_speed"], ["my_drone_speed"],
                  ["my_drone_max_speed"], ["my_drone_max_acceleration"],
                  ["my_drone_max_deceleration"], ["my_drone_max_roll"], ["my_drone_min_pitch"],
                  ["my_drone_max_pitch"], ["my_drone_max_sink_rate"], ["my_drone_max_climb_rate"],
                  ["my_drone_max_command_frequency"]]
              ], [
                "bottom",
                [["my_script"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Edit and run script',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this, i,
        fragment = gadget.element.querySelector('.simulator_div'),
        game_parameters_json;
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      DRONE_LIST = [];
      for (i = 0; i < options.number_of_drones; i += 1) {
        DRONE_LIST[i] = {"id": i, "type": "FixedWingDroneAPI",
                         "script_content": options.script};
      }
      game_parameters_json = {
        "drone": {
          "maxAcceleration": parseFloat(options.drone_max_acceleration),
          "maxDeceleration": parseInt(options.drone_max_deceleration, 10),
          "minSpeed": parseInt(options.drone_min_speed, 10),
          "speed": parseFloat(options.drone_speed),
          "maxSpeed": parseInt(options.drone_max_speed, 10),
          "maxRoll": parseFloat(options.drone_max_roll),
          "minPitchAngle": parseFloat(options.drone_min_pitch),
          "maxPitchAngle": parseFloat(options.drone_max_pitch),
          "maxSinkRate": parseFloat(options.drone_max_sink_rate),
          "maxClimbRate": parseFloat(options.drone_max_climb_rate),
          "maxCommandFrequency": parseFloat(options.drone_max_command_frequency),
          "onUpdateInterval": parseInt(options.onupdate_interval, 10)
        },
        "gameTime": parseInt(options.simulation_time, 10),
        "simulation_speed": parseInt(options.simulation_speed, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": {
          "min_lat": parseFloat(options.min_lat),
          "max_lat": parseFloat(options.max_lat),
          "min_lon": parseFloat(options.min_lon),
          "max_lon": parseFloat(options.max_lon),
          "height": parseInt(options.map_height, 10),
          "start_AMSL": parseFloat(options.start_AMSL)
        },
        "initialPosition": {
          "longitude": parseFloat(options.init_pos_lon),
          "latitude": parseFloat(options.init_pos_lat),
          "altitude": parseFloat(options.init_pos_alt)
        },
        "draw_flight_path": DRAW,
        "temp_flight_path": true,
        "log_drone_flight": LOG,
        "log_interval_time": LOG_TIME,
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
        })
        .push(function (result) {
          var a, blob, div, key, log, log_content;
          i = 0;
          for (key in result.content) {
            if (result.content.hasOwnProperty(key)) {
              log_content = result.content[key].join('\n').replaceAll(",", ";");
              blob = new Blob([log_content], {type: 'text/plain'});
              a = domsugar('a', {
                text: 'Download Simulation LOG ' + i,
                download: 'simulation_log_' + i
                  + '_speed_' + game_parameters_json.drone.speed
                  + '_min-speed_' + game_parameters_json.drone.minSpeed
                  + '_max-speed_' + game_parameters_json.drone.maxSpeed
                  + '_max-accel_' + game_parameters_json.drone.maxAcceleration
                  + '_max-decel_' + game_parameters_json.drone.maxDeceleration
                  + '_max-roll_' + game_parameters_json.drone.maxRoll
                  + '_min-pitch_' + game_parameters_json.drone.minPitchAngle
                  + '_max-pitch_' + game_parameters_json.drone.maxPitchAngle
                  + '_max-sink_' + game_parameters_json.drone.maxSinkRate
                  + '_max-climb_' + game_parameters_json.drone.maxClimbRate
                  + '.txt',
                href: window.URL.createObjectURL(blob)
              });
              log = domsugar('textarea', { value: log_content, id: 'log_result_' + i });
              div = domsugar('div', [a]);
              a.dataset.downloadurl =  ['text/plain', a.download,
                                        a.href].join(':');
              document.querySelector('.container').appendChild(div);
              document.querySelector('.container').appendChild(log);
              i += 1;
            }
          }
        }, function (error) {
          return gadget.notifySubmitted({message: "Error: " + error.message,
                                         status: 'error'});
        });
    });

}(window, rJS, domsugar, document, Blob));