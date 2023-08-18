/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, URLSearchParams, Blob*/
(function (window, rJS, domsugar, document, URLSearchParams, Blob) {
  "use strict";

  //Drone default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 10,
    SIMULATION_TIME = 270,
    //HARDCODED map size: it is defined by min-max lat-lon distance
    //this is done by the map manager (latLonDistance)
    //but map_size is needed here for map randomization (location of objects)
    //TODO refactor: or randomization is moved to map manager (seed as param)
    //or randomization is done here but with geo-coordinates (not meters)
    MAP_SIZE = 900,
    //square map
    min_lat = 45.6419,
    max_lat = 45.65,
    min_lon = 14.265,
    max_lon = 14.2766,
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
    NUMBER_OF_DRONES = 10,
    FLAG_WEIGHT = 5,
    SEED = '6',
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      'var EPSILON = 15,\n' +
      '  DODGE_DISTANCE = 100;\n' +
      '\n' +
      'function distance(a, b) {\n' +
      '  var R = 6371e3, // meters\n' +
      '    la1 = a.x * Math.PI / 180, // lat, lon in radians\n' +
      '    la2 = b.x * Math.PI / 180,\n' +
      '    lo1 = a.y * Math.PI / 180,\n' +
      '    lo2 = b.y * Math.PI / 180,\n' +
      '    haversine_phi = Math.pow(Math.sin((la2 - la1) / 2), 2),\n' +
      '    sin_lon = Math.sin((lo2 - lo1) / 2),\n' +
      '    h = haversine_phi + Math.cos(la1) * Math.cos(la2) * sin_lon * sin_lon;\n' +
      '  return 2 * R * Math.asin(Math.sqrt(h));\n' +
      '}\n' +
      '\n' +
      'me.onStart = function () {\n' +
      '  me.direction_set = false;\n' +
      '  me.dodging = false;\n' +
      '  me.ongoing_detection = false;\n' +
      '};\n' +
      '\n' +
      'me.onGetMsg = function (msg) {\n' +
      '  if (msg && msg.flag_positions) {\n' +
      '    me.flag_positions = msg.flag_positions\n' +
      '    me.next_checkpoint = me.id % me.flag_positions.length;\n' +
      '  }\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
      '  if (!me.flag_positions) return;\n' +
      '  if (me.dodging) {\n' +
      '    me.current_position = me.getCurrentPosition();\n' +
      '    var dist = distance(\n' +
      '      me.current_position,\n' +
      '      me.dodging.position\n' +
      '    );\n' +
      '    if (dist >= DODGE_DISTANCE) {\n' +
      //'      console.log("Good distance to obstacle. DODGED.");\n' +
      '      me.dodging = false;\n' +
      '    }\n' +
      '    return;\n' +
      '  }\n' +
      '  if (!me.direction_set) {\n' +
      '    if (me.next_checkpoint < me.flag_positions.length) {\n' +
      '      me.setTargetCoordinates(\n' +
      '        me.flag_positions[me.next_checkpoint].x,\n' +
      '        me.flag_positions[me.next_checkpoint].y,\n' +
      '        me.flag_positions[me.next_checkpoint].z + me.id\n' +
      '      );\n' +
      //'      console.log("[DEMO] Going to Checkpoint %d", me.next_checkpoint);\n' +
      '    }\n' +
      '    me.direction_set = true;\n' +
      '    return;\n' +
      '  }\n' +
      '  if (me.next_checkpoint < me.flag_positions.length) {\n' +
      '    if (!me.ongoing_detection) {\n' +
      '      me.getDroneViewInfo();\n' +
      '      me.ongoing_detection = true;\n' +
      '    }\n' +
      '  }\n' +
      '  if (me.next_checkpoint < me.flag_positions.length) {\n' +
      '    me.current_position = me.getCurrentPosition();\n' +
      '    me.distance = distance(\n' +
      '      me.current_position,\n' +
      '      me.flag_positions[me.next_checkpoint]\n' +
      '    );\n' +
      '    if (me.distance <= EPSILON) {\n' +
      //'      console.log("[DEMO] Reached Checkpoint %d", me.next_checkpoint);\n' +
      '      me.next_checkpoint += 1;\n' +
      '      me.direction_set = false;\n' +
      '    }\n' +
      '    return;\n' +
      '  }\n' +
      '};\n' +
      '\n' +
      'me.onDroneViewInfo = function (drone_view) {\n' +
      '  me.ongoing_detection = false;\n' +
      '  if (drone_view && drone_view.obstacles && drone_view.obstacles.length) {\n' +
      '    me.dodging = drone_view.obstacles[0];\n' +
      '    me.direction_set = false;\n' +
      '    var random = Math.random() < 0.5, dodge_point = {};\n' +
      '    Object.assign(dodge_point, me.flag_positions[me.next_checkpoint]);\n' +
      '    if (random) {\n' +
      '      dodge_point.x = dodge_point.x * -1;\n' +
      '    } else {\n' +
      '      dodge_point.y = dodge_point.y * -1;\n' +
      '    }\n' +
      '    me.setTargetCoordinates(dodge_point.x, dodge_point.y, me.getCurrentPosition().z);\n' +
      '    return;\n' +
      '  }\n' +
      '};',
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    DRONE_LIST = [],
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_capture_flag_logic.js',
      'gadget_erp5_page_drone_capture_flag_fixedwingdrone.js',
      'gadget_erp5_page_drone_capture_flag_enemydrone.js'
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
      var gadget = this, url_sp = new URLSearchParams(window.location.hash),
        url_seed = url_sp.get("seed");
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
                /*"my_map_size": {
                  "description": "",
                  "title": "Map size",
                  "default": MAP_SIZE,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "map_size",
                  "hidden": 0,
                  "type": "FloatField"
                },*/
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
                "my_map_seed": {
                  "description": "Seed value to randomize the map",
                  "title": "Seed value",
                  "default": url_seed ? url_seed : SEED,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "map_seed",
                  "hidden": 0,
                  "type": "StringField"
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
                /*"my_flag_weight": {
                  "description": "",
                  "title": "Flag Weight",
                  "default": FLAG_WEIGHT,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "flag_weight",
                  "hidden": 0,
                  "type": "IntegerField"
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
                 /*["my_map_size"], */["my_map_height"],// ["my_flag_weight"],
                 ["my_start_AMSL"], ["my_map_seed"]]
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
        game_parameters_json, map_json;
      options.map_size = MAP_SIZE;
      DRONE_LIST = [];
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      for (i = 0; i < options.number_of_drones; i += 1) {
        DRONE_LIST[i] = {"id": i, "type": "FixedWingDroneAPI",
                         "script_content": options.script};
      }

      function randomizeMap(json_map) {
        function randomIntFromInterval(min, max, random_seed) {
          return Math.floor(random_seed.quick() * (max - min + 1) + min);
        }
        function randomPosition(random_seed, map_size) {
          var sign_x = random_seed.quick() < 0.5 ? -1 : 1,
            sign_y = random_seed.quick() < 0.5 ? -1 : 1,
            pos_x = sign_x * random_seed.quick() * map_size / 2,
            pos_y = sign_y * random_seed.quick() * map_size / 2;
          return [pos_x, pos_y];
        }
        var seed_value = options.map_seed,
          random_seed = new Math.seedrandom(seed_value), i,
          n_enemies = randomIntFromInterval(5, 10, random_seed),
          n_flags = randomIntFromInterval(5, 10, random_seed),
          n_obstacles = randomIntFromInterval(5, 15, random_seed),
          flag_list = [], obstacle_list = [], enemy_list = [], random_position,
          obstacles_types = ["box"/*, "sphere"*/, "cylinder"], type,
          obstacle_limit = [options.map_size / 6, options.map_size / 100,
                            options.map_size / 6, 30];
        //enemies
        for (i = 0; i < n_enemies; i += 1) {
          random_position = randomPosition(random_seed, options.map_size);
          enemy_list.push({
            "id": i + parseInt(options.number_of_drones),
            "type": "EnemyDroneAPI",
            "position": {
              "x": random_position[0],
              "y": random_position[1],
              "z": 15 //TODO random z?
            }
          });
        }
        //flags
        for (i = 0; i < n_flags; i += 1) {
          //avoid flags near the limits
          random_position = randomPosition(random_seed, options.map_size * 0.75);
          flag_list.push({
            "position": {
              "x": random_position[0],
              "y": random_position[1],
              "z": 10
            }
          });
        }
        function checkDistance(position, position_list) {
          function distance(a, b) {
            return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
          }
          var el;
          for (el = 0; el < position_list.length; el += 1) {
            if (distance(position, position_list[el].position) < options.map_size / 6) {
              return true;
            }
          }
          return false;
        }
        //obstacles
        for (i = 0; i < n_obstacles; i += 1) {
          random_position = randomPosition(random_seed, options.map_size);
          if (checkDistance({ 'x': random_position[0],
                              'y': random_position[1]}, flag_list)) {
            i -= 1;
          } else {
            type = randomIntFromInterval(0, 2, random_seed);
            obstacle_list.push({
              "type": obstacles_types[type],
              "position": {
                "x": random_position[0],
                "y": random_position[1],
                "z": 15 //TODO random z?
              },
              "scale": {
                "x": randomIntFromInterval(20, obstacle_limit[type], random_seed),
                "y": randomIntFromInterval(20, obstacle_limit[type], random_seed),
                "z": randomIntFromInterval(5, obstacle_limit[3], random_seed)
              },
              "rotation": {
                "x": 0,
                "y": 0,
                "z": 0
              }
            });
          }
        }
        json_map.obstacle_list = obstacle_list;
        json_map.drones.enemy = enemy_list;
        json_map.flag_list = flag_list;
        return json_map;
      }

      map_json = {
        "map_size": parseFloat(options.map_size),
        "height": parseInt(options.map_height, 10),
        "start_AMSL": parseFloat(options.start_AMSL),
        "min_lat": parseFloat(min_lat),
        "max_lat": parseFloat(max_lat),
        "min_lon": parseFloat(min_lon),
        "max_lon": parseFloat(max_lon),
        "flag_list": [],
        "obstacle_list" : [],
        "drones": {
          "user": DRONE_LIST,
          "enemy": []
        }
      };

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
        "map": randomizeMap(map_json),
        "draw_flight_path": DRAW,
        "temp_flight_path": true,
        "log_drone_flight": LOG,
        "log_interval_time": LOG_TIME
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
                  "renderjs_extra": '{"autorun": false, ' +
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
          var a, blob, div, key, log, log_content, aux;
          i = 0;
          div = domsugar('div', { text: result.message });
          document.querySelector('.container').parentNode.appendChild(div);
          for (key in result.content) {
            if (result.content.hasOwnProperty(key)) {
              log_content = result.content[key].join('\n').replaceAll(",", ";");
              blob = new Blob([log_content], {type: 'text/plain'});
              a = domsugar('a', {
                text: 'Download Simulation LOG ' + i,
                download: 'simulation_log_' + i +
                '_speed_' + game_parameters_json.drone.speed +
                '_min-speed_' + game_parameters_json.drone.minSpeed +
                '_max-speed_' + game_parameters_json.drone.maxSpeed +
                '_max-accel_' + game_parameters_json.drone.maxAcceleration +
                '_max-decel_' + game_parameters_json.drone.maxDeceleration +
                '_max-roll_' + game_parameters_json.drone.maxRoll +
                '_min-pitch_' + game_parameters_json.drone.minPitchAngle +
                '_max-pitch_' + game_parameters_json.drone.maxPitchAngle +
                '_max-sink_' + game_parameters_json.drone.maxSinkRate +
                '_max-climb_' + game_parameters_json.drone.maxClimbRate +
                '.txt',
                href: window.URL.createObjectURL(blob)
              });
              log = domsugar('textarea',
                             { value: log_content, id: 'log_result_' + i });
              div = domsugar('div', [a]);
              a.dataset.downloadurl =  ['text/plain', a.download,
                                        a.href].join(':');
              document.querySelector('.container').parentNode.appendChild(div);
              document.querySelector('.container').parentNode.appendChild(log);
              i += 1;
              if (i === DRONE_LIST.length) {
                break;
                //Do not show enemy drone logs for now
                /*aux = domsugar('div', { text: "Enemy drones logs:" });
                document.querySelector('.container').parentNode.appendChild(aux);*/
              }
            }
          }
        }, function (error) {
          return gadget.notifySubmitted({message: "Error: " + error.message,
                                         status: 'error'});
        });
    });

}(window, rJS, domsugar, document, URLSearchParams, Blob));