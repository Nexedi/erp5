/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, URLSearchParams, Blob, require, MapUtils*/
(function (window, rJS, domsugar, document, URLSearchParams, Blob, require) {
  "use strict";

  //Drone default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 10,
    SIMULATION_TIME = 270,
    //default square map
    MAP_HEIGHT = 700,
    START_AMSL = 595,
    MIN_LAT = 45.6419,
    MAX_LAT = 45.65,
    MIN_LON = 14.265,
    MAX_LON = 14.2766,
    //SEED FORM PARAMETER IS BROKEN (used in randomization before user inputs)
    // only way to set it and use it is via url parameter 'seed'
    url_sp = new URLSearchParams(window.location.hash),
    url_seed = url_sp.get("seed"),
    SEED = url_seed ? url_seed : '6!',
    MAP = {
      "height": MAP_HEIGHT,
      "start_AMSL": START_AMSL,
      "map_seed": SEED,
      "min_lat": MIN_LAT,
      "max_lat": MAX_LAT,
      "min_lon": MIN_LON,
      "max_lon": MAX_LON
    },
    JSON_MAP,
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
      '    me.flag_positions = msg.flag_positions;\n' +
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
      '        me.flag_positions[me.next_checkpoint].position.x,\n' +
      '        me.flag_positions[me.next_checkpoint].position.y,\n' +
      '        me.flag_positions[me.next_checkpoint].position.z + me.id\n' +
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
      '      me.flag_positions[me.next_checkpoint].position\n' +
      '    );\n' +
      '    if (me.distance <= EPSILON) {\n' +
      //'      console.log("[DEMO] Reached Checkpoint %d", me.next_checkpoint);\n' +
      '      me.next_checkpoint += 1;\n' +
      '      me.direction_set = false;\n' +
      '    }\n' +
      '    return;\n' +
      '  }\n' +
      '  if (me.next_checkpoint == me.flag_positions.length) {\n' +
      '    me.triggerParachute();\n' +
      '  }\n' +
      '  if (me.landed()) {\n' +
      '    me.exit();\n' +
      '  }\n' +
      '};\n' +
      '\n' +
      'me.onDroneViewInfo = function (drone_view) {\n' +
      '  me.ongoing_detection = false;\n' +
      '  if (drone_view && drone_view.obstacles && drone_view.obstacles.length) {\n' +
      '    me.dodging = drone_view.obstacles[0];\n' +
      '    me.direction_set = false;\n' +
      '    var random = Math.random() < 0.5, dodge_point = {};\n' +
      '    Object.assign(dodge_point, me.flag_positions[me.next_checkpoint].position);\n' +
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
      'gadget_erp5_page_drone_capture_flag_enemydrone.js',
      './libraries/seedrandom.min.js'
    ];

  function handleFileSelect(event, gadget, options) {
    var reader = new FileReader()
    reader.onload = (event) => handleFileLoad(event, gadget, options);
    reader.readAsText(event.target.files[0]);
  }

  function handleFileLoad(event, gadget, options) {
    options.operator_script = event.target.result;
    return gadget.changeState(options);
  }

  function downloadFromTextContent(gadget, text_content, title) {
    var element = gadget.element,
      a = window.document.createElement("a"),
      url = window.URL.createObjectURL(new Blob([text_content], {type: 'text/plain'})),
      name_list = [title, "js"];
    element.appendChild(a);
    a.style = "display: none";
    a.href = url;
    a.download = name_list.join('.');
    a.click();
    element.removeChild(a);
    window.URL.revokeObjectURL(url);
  }

  //Randomize map before render, so it's available on operator editor
  require(['gadget_erp5_page_drone_capture_flag_logic.js'], function () {
    JSON_MAP = new MapUtils(MAP).randomize();
  });

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
      var gadget = this, operator_init_msg, script_content;
      return gadget.getDeclaredGadget('operator-editor')
        .push(function (operator_editor) {
          return operator_editor.getContent();
        })
        .push(function (content) {
          /*jslint evil: true*/
          try {
            operator_init_msg = new Function(content.operator_editor)();
          } catch (error) {
            operator_init_msg = {'error': error};
          }
          /*jslint evil: false*/
          if (!operator_init_msg) operator_init_msg = {};
          return gadget.getDeclaredGadget('script-editor');
        })
        .push(function (script_editor) {
          return script_editor.getContent();
        })
        .push(function (content) {
          script_content = content.script_editor;
          return gadget.getDeclaredGadget('form_view');
        })
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (input) {
          input.operator_init_msg = operator_init_msg;
          input.script = script_content;
          gadget.runGame(input);
        });
    })

    .onEvent('click', function (evt) {
      var gadget = this;
      if (evt.target.id === "import") {
        return;
      }
      if (evt.target.id === "export") {
        return gadget.getDeclaredGadget('operator-editor')
          .push(function (operator_editor) {
            return operator_editor.getContent();
          })
          .push(function (content) {
            downloadFromTextContent(gadget, content.operator_editor, 'operator_script');
          });
      }
    }, false, false)

    .declareMethod('render', function render(options) {
      var gadget = this,
        loadedFile = (event) => handleFileSelect(event, gadget, options);
      gadget.element.querySelector('#import').addEventListener("change", loadedFile);
      MAP.map_seed = SEED;
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
                [["my_simulation_speed"], ["my_simulation_time"],
                 ["my_number_of_drones"], ["my_map_seed"]]
              ], [
                "right",
                [["my_drone_min_speed"], ["my_drone_speed"], ["my_drone_max_speed"],
                  ["my_drone_max_acceleration"], ["my_drone_max_deceleration"],
                  ["my_drone_max_roll"], ["my_drone_min_pitch"], ["my_drone_max_pitch"],
                  ["my_drone_max_sink_rate"], ["my_drone_max_climb_rate"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("operator-editor");
        })
        .push(function (operator_editor) {
          var operator_map = {}, DEFAULT_OPERATOR_SCRIPT_CONTENT;
          Object.assign(operator_map, JSON_MAP);
          delete operator_map.flag_list;
          delete operator_map.obstacle_list;
          delete operator_map.enemy_list;
          delete operator_map.geo_obstacle_list;
          delete operator_map.flag_distance_epsilon;
          DEFAULT_OPERATOR_SCRIPT_CONTENT = 'var json_map = ' +
            JSON.stringify(operator_map) + ';\n' +
            '\n' +
            'return {"flag_positions": json_map.geo_flag_list};\n';
          return operator_editor.render({
            "editor": "codemirror",
            "maximize": true,
            "portal_type": "Web Script",
            "key": "operator_editor",
            "value": DEFAULT_OPERATOR_SCRIPT_CONTENT,
            "editable": 1,
            "hidden": 0
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget("script-editor");
        })
        .push(function (script_editor) {
          return script_editor.render({
            "editor": "codemirror",
            "maximize": true,
            "portal_type": "Web Script",
            "key": "script_editor",
            "value": DEFAULT_SCRIPT_CONTENT,
            "editable": 1,
            "hidden": 0
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Capture Flag',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .onStateChange(function (modification_dict) {
      if (modification_dict.hasOwnProperty('operator_script')) {
        return this.getDeclaredGadget('operator-editor')
          .push(function (operator_editor) {
            return operator_editor.render({
              "editor": "codemirror",
              "maximize": true,
              "portal_type": "Web Script",
              "key": "operator_editor",
              "value": modification_dict.operator_script,
              "editable": 1,
              "hidden": 0
            });
          });
      }
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
          "maxClimbRate": parseFloat(options.drone_max_climb_rate),
          "list": DRONE_LIST
        },
        "gameTime": parseInt(options.simulation_time, 10),
        "simulation_speed": parseInt(options.simulation_speed, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": JSON_MAP || MAP,
        "operator_init_msg": options.operator_init_msg,
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
          var a, blob, div, key, log, log_content, aux, label;
          i = 0;
          div = domsugar('div', { text: result.message });
          label = domsugar('label', { text: "Results" });
          label.classList.add("item-label");
          document.querySelector('.container').parentNode.appendChild(label);
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

}(window, rJS, domsugar, document, URLSearchParams, Blob, require));