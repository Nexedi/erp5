/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, Blob*/
(function (window, rJS, domsugar, document, Blob) {
  "use strict";

  //Default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 10,
    SIMULATION_TIME = 1500,
    MAP_SIZE = 1000,
    map_height = 700,
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
    /*INITIAL_POSITION = {
      "latitude": 45.6412,
      "longitude": 14.26,
      "z": 15
    },*/
    NUMBER_OF_DRONES = 1,
    FLAG_WEIGHT = 5,
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      'var ALTITUDE = 1000,\n' +
      '  EPSILON = 9,\n' +
      '  CHECKPOINT_LIST = [\n' +
      '    {\n' +
      '      altitude: 585.1806861589965,\n' +
      '      latitude: 45.64492790560583,\n' +
      '      longitude: 14.25334942966329\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 589.8802607573035,\n' +
      '      latitude: 45.64316335436476,\n' +
      '      longitude: 14.26332880184475\n' +
      '    }\n' +
      '  ];\n' +
      '\n' +
      'function distance(lat1, lon1, lat2, lon2) {\n' +
      '  var R = 6371e3, // meters\n' +
      '    la1 = lat1 * Math.PI / 180, // lat, lon in radians\n' +
      '    la2 = lat2 * Math.PI / 180,\n' +
      '    lo1 = lon1 * Math.PI / 180,\n' +
      '    lo2 = lon2 * Math.PI / 180,\n' +
      '    haversine_phi = Math.pow(Math.sin((la2 - la1) / 2), 2),\n' +
      '    sin_lon = Math.sin((lo2 - lo1) / 2),\n' +
      '    h = haversine_phi + Math.cos(la1) * Math.cos(la2) * sin_lon * sin_lon;\n' +
      '  return 2 * R * Math.asin(Math.sqrt(h));\n' +
      '}\n' +
      '\n' +
      'me.onStart = function () {\n' +
      '  me.direction_set = false;\n' +
      '  me.next_checkpoint = 0;\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {' +
      '  if (!me.direction_set) {\n' +
      '    if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '      me.setTargetCoordinates(\n' +
      '        50,//CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '        80,//CHECKPOINT_LIST[me.next_checkpoint].longitude,\n' +
      '        10, true//ALTITUDE + me.id\n' +
      '      );\n' +
      '      console.log("[DEMO] Going to Checkpoint %d", me.next_checkpoint);\n' +
      '    }\n' +
      '    me.direction_set = true;\n' +
      '    return;\n' +
      '  }\n' +
      '  if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '    me.current_position = me.getCurrentPosition();\n' +
      '    me.distance = distance(\n' +
      '      me.current_position.x,\n' +
      '      me.current_position.y,\n' +
      '      CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '      CHECKPOINT_LIST[me.next_checkpoint].longitude\n' +
      '    );\n' +
      '    if (me.distance <= EPSILON) {\n' +
      '      console.log("[DEMO] Reached Checkpoint %d", me.next_checkpoint);\n' +
      '      me.next_checkpoint += 1;\n' +
      '      me.direction_set = false;\n' +
      '    }\n' +
      '    return;\n' +
      '  }\n' +
      '  me.exit(0);\n' +
      '};',
    DRAW = false,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    DRONE_LIST = [],
    WIDTH = 680,
    HEIGHT = 340,
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_capture_flag_logic.js',
      'gadget_erp5_page_drone_capture_flag_fixedwingdrone.js'/*,
      'gadget_erp5_page_drone_capture_flag_dronelogfollower.js'*/
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
                  "type": "IntegerField"
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
                "my_map_size": {
                  "description": "",
                  "title": "Map size",
                  "default": MAP_SIZE,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "map_size",
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
                //TODO drop initial position inputs
                /*"my_init_pos_lon": {
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
                "my_init_pos_z": {
                  "description": "",
                  "title": "Initial drone position Z",
                  "default": INITIAL_POSITION.z,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_z",
                  "hidden": 0,
                  "type": "FloatField"
                },*/
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
                [["my_simulation_speed"], ["my_simulation_time"], ["my_number_of_drones"],
                  ["my_map_size"], ["my_map_height"],
                  //["my_init_pos_lat"], ["my_init_pos_lon"], ["my_init_pos_z"],
                  ["my_start_AMSL"]]
              ], [
                "right",
                [["my_drone_min_speed"], ["my_drone_speed"], ["my_drone_max_speed"],
                  ["my_drone_max_acceleration"], ["my_drone_max_deceleration"],
                  ["my_drone_max_roll"], ["my_drone_min_pitch"], ["my_drone_max_pitch"],
                  ["my_drone_max_sink_rate"], ["my_drone_max_climb_rate"]]
              ], [
                "bottom",
                [["my_script"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Capture Flag',
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

      function randomizeMap(json_map) {
        var random_seed = new Math.seedrandom(Math.random()),
          map_size, sign_x, sign_y, pos_x, pos_y;
        map_size = json_map.mapSize.depth;
        sign_x = random_seed.quick() < 0.5 ? -1 : 1;
        sign_y = random_seed.quick() < 0.5 ? -1 : 1;
        pos_x = (random_seed.quick() *
               (map_size / 2.5 - map_size / 4) + map_size / 4) * sign_x;
        pos_y = (random_seed.quick() *
               (map_size / 2.5 - map_size / 4) + map_size / 4) * sign_y;
        json_map.random_init_pos = [pos_x, pos_y];
        return json_map;
      }

      game_parameters_json = {
        "drone": {
          "maxAcceleration": parseInt(options.drone_max_acceleration, 10),
          "maxDeceleration": parseInt(options.drone_max_deceleration, 10),
          "minSpeed": parseInt(options.drone_min_speed, 10),
          "speed": parseFloat(options.drone_speed),
          "maxSpeed": parseInt(options.drone_max_speed, 10),
          "maxRoll": parseFloat(options.drone_max_roll),
          "minPitchAngle": parseFloat(options.drone_min_pitch),
          "maxPitchAngle": parseFloat(options.drone_max_pitch),
          "maxSinkRate": parseFloat(options.drone_max_sink_rate),
          "maxClimbRate": parseFloat(options.drone_max_climb_rate)
        },
        "gameTime": parseInt(options.simulation_time, 10),
        "simulation_speed": parseInt(options.simulation_speed, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": {
          "map_size": parseFloat(options.map_size),
          "height": parseInt(options.map_height, 10),
          "start_AMSL": parseFloat(options.start_AMSL),
          "flag_weight": FLAG_WEIGHT,
          "flag_list": [{
            "team": 0,
            "position": {
              "x": -0.8 * options.map_size / 2,
              "y": -0.8 * options.map_size / 2,
              "z": 0
            }
          }, {
            "team": 0,
            "position": {
              "x": 0.8 * options.map_size / 2,
              "y": -0.8 * options.map_size / 2,
              "z": 0
            }
          }, {
            "team": 1,
            "position": {
              "x": 0.8 * options.map_size / 2,
              "y": 0.8 * options.map_size / 2,
              "z": 0
            }
          }, {
            "team": 1,
            "position": {
              "x": -0.8 * options.map_size / 2,
              "y": 0.8 * options.map_size / 2,
              "z": 0
            }
          }],
          "obstacle_list" : [{
            "type": "sphere",
            "position": {
              "x": 0.6 * options.map_size / 2,
              "y": 0.4 * options.map_size / 2,
              "z": 8
            },
            "scale": {
              "x": 4,
              "y": 4,
              "z": 4
            },
            "rotation": {
              "x": 0,
              "y": 0,
              "z": 0
            }
          }, {
            "type": "cylinder",
            "position": {
              "x": -0.5 * options.map_size / 2,
              "y": 0.5 * options.map_size / 2,
              "z": 10
            },
            "scale": {
              "x": 4.5,
              "y": 4.5,
              "z": 20
            },
            "rotation": {
              "x": 0,
              "y": 0,
              "z": 0
            }
          }, {
            "type": "box",
            "position": {
              "x": -0.25 * options.map_size / 2,
              "y": -0.25 * options.map_size / 2,
              "z": 10
            },
            "scale": {
              "x": 150,
              "y": 2.5,
              "z": 30
            },
            "rotation": {
              "x": 0,
              "y": 0,
              "z": 0
            }
          }]
        },
        /*"initialPosition": {
          "longitude": parseFloat(options.init_pos_lon),
          "latitude": parseFloat(options.init_pos_lat),
          "z": parseFloat(options.init_pos_z)
        },*/
        "draw_flight_path": DRAW,
        "temp_flight_path": true,
        "log_drone_flight": LOG,
        "log_interval_time": LOG_TIME,
        "droneList": {
          "team_A": DRONE_LIST,
          "team_B": DRONE_LIST
        }
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
          for (key in result) {
            if (result.hasOwnProperty(key)) {
              log_content = result[key].join('\n').replaceAll(",", ";");
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