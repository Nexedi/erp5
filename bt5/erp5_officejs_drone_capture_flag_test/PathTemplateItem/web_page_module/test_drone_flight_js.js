/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, URLSearchParams, Blob*/
(function (window, rJS, domsugar, document, URLSearchParams, Blob) {
  "use strict";

  //Drone default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 10,
    SIMULATION_TIME = 270,
    MAP_SIZE = 600,
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
    SEED = 'flag',
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
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
  /*function compare(coord1, coord2) {
    console.assert(coord1.x === coord2.x, "Wrong latitude", coord1.x, coord2.x);
    console.assert(coord1.y === coord2.y, "Wrong longitude", coord1.y, coord2.y);
    console.assert(coord1.z === coord2.z, "Wrong altitude", coord1.z, coord2.z);
  }*/
      '\n' +
      'me.onStart = function () {\n' +
      'console.log("me.id");\n' +
    /*console.assert(me.getAirSpeed() === 16, "Wrong initial speed");
    console.assert(me.getYaw() === 0, "Wrong yaw angle");
    me.initialPosition = me.getCurrentPosition();
    me.setTargetCoordinates(
      me.initialPosition.x + 0.01,
      me.initialPosition.y,
      me.initialPosition.z
    );*/
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
    /*var realDistance = distance(
      me.initialPosition.x,
      me.initialPosition.y,
      me.getCurrentPosition().x,
      me.getCurrentPosition().y
    ).toFixed(8),
      expectedDistance = (me.getAirSpeed() * timestamp / 1000).toFixed(8);
    console.assert(timestamp === 1000 / 60, "Wrong timestamp");
    console.assert(
      realDistance == expectedDistance,
      "Wrong distance",
      realDistance,
      expectedDistance
    );
    compare(me.getCurrentPosition(), {
      x: me.initialPosition.x + 2.3992831666911723e-06,
      y: me.initialPosition.y,
      z: me.initialPosition.z
    });
    me.exit(me.triggerParachute());*/
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
                 ["my_map_size"], ["my_map_height"],// ["my_flag_weight"],
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
          n_obstacles = randomIntFromInterval(5, 10, random_seed),
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
                "x": randomIntFromInterval(0, obstacle_limit[type], random_seed),
                "y": randomIntFromInterval(0, obstacle_limit[type], random_seed),
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
        //"flag_weight": parseInt(options.flag_weight, 10),
        "flag_list": [],
        "obstacle_list" : [],
        "drones": {
          "user": DRONE_LIST,
          "enemy": []
        }
      };

      game_parameters_json = {
        "debug_test_mode": true,
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
          var div = domsugar('div', { text: "CONSOLE LOG ENTRIES:" });
          document.querySelector('.container').parentNode.appendChild(div);
          function createLogNode(message) {
            var node = document.createElement("div");
            var textNode = document.createTextNode(message);
            node.appendChild(textNode);
            return node;
          }
          var lines = result.console_log.split('\n');
          for (var i = 0;i < lines.length;i++) {
            var node = createLogNode(lines[i]);
            document.querySelector('.test_log').appendChild(node);
          }
        }, function (error) {
          return gadget.notifySubmitted({message: "Error: " + error.message,
                                         status: 'error'});
        });
    });

}(window, rJS, domsugar, document, URLSearchParams, Blob));