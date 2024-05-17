/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, Blob, MapUtils, RSVP*/

/******************************* OPERATOR API ********************************/
var OperatorAPI = /** @class */ (function () {
  "use strict";

  //** CONSTRUCTOR
  function OperatorAPI(json_map) {
    this.message = "default init message";
    this.json_map = json_map;
  }
  OperatorAPI.prototype.getMapJSON = function () {
    return this.json_map;
  };
  OperatorAPI.prototype.sendMsg = function (msg) {
    this.message = msg;
  };
  OperatorAPI.prototype.getDroneStartMessage = function () {
    return this.message;
  };

  return OperatorAPI;
}());

(function (window, rJS, domsugar, document, Blob, MapUtils, RSVP) {
  "use strict";

  //Drone default values - TODO: get them from the drone API
  var SIMULATION_SPEED = 60,
    SIMULATION_TIME = 270,
    //default square map
    MAP_HEIGHT = 700,
    START_AMSL = 595,
    MIN_LAT = 45.6419,
    MAX_LAT = 45.65,
    MIN_LON = 14.265,
    MAX_LON = 14.2766,
    //seed
    //url_sp = new URLSearchParams(window.location.hash),
    //url_seed = url_sp.get("seed"),
    SEED = '123',//'6!',
    MAP = {
      "height": MAP_HEIGHT,
      "start_AMSL": START_AMSL,
      "min_lat": MIN_LAT,
      "max_lat": MAX_LAT,
      "min_lon": MIN_LON,
      "max_lon": MAX_LON,
      "flag_list": [{"position":
                     {"latitude": 45.6464947316632,
                     "longitude": 14.270747186236491,
                     "altitude": 10},
                     "score": 1,
                     "weight": 1}],
      "obstacle_list": [{"type": "box",
                         "position": {"latitude": 45.6456815316444,
                                      "longitude": 14.274667031215898,
                                      "altitude": 15},
                         "scale": {"x": 132, "y": 56, "z": 10},
                         "rotation": {"x": 0, "y": 0, "z": 0}}],
      "enemy_list": [{"type": "EnemyDroneAPI",
                      "position": {"latitude": 45.6455531,
                                   "longitude": 14.270747186236491,
                                   "altitude": 15}}],
      "initial_position": {"latitude": 45.642813275,
                           "longitude": 14.270231599999988,
                           "altitude": 15}
    },
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
    NUMBER_OF_DRONES = 5,
    // Non-inputs parameters
    EPSILON = "15",
    DEFAULT_OPERATOR_SCRIPT = 'var map = operator.getMapJSON();\n' +
      'operator.sendMsg({flag_positions: map.flag_list});\n',
    DEFAULT_SCRIPT_CONTENT =
      'var EPSILON = ' + EPSILON + ',\n' +
      '  DODGE_DISTANCE = 100;\n' +
      '\n' +
      'function distance2D(a, b) {\n' +
      '  var R = 6371e3, // meters\n' +
      '    la1 = a.latitude * Math.PI / 180, // lat, lon in radians\n' +
      '    la2 = b.latitude * Math.PI / 180,\n' +
      '    lo1 = a.longitude * Math.PI / 180,\n' +
      '    lo2 = b.longitude * Math.PI / 180,\n' +
      '    haversine_phi = Math.pow(Math.sin((la2 - la1) / 2), 2),\n' +
      '    sin_lon = Math.sin((lo2 - lo1) / 2),\n' +
      '    h = haversine_phi + Math.cos(la1) * Math.cos(la2) * sin_lon * sin_lon;\n' +
      '  return 2 * R * Math.asin(Math.sqrt(h));\n' +
      '}\n' +
      '\n' +
      'function distance(a, b) {\n' +
      '  return Math.sqrt(\n' +
      '    Math.pow(a.altitude - b.altitude, 2) + Math.pow(distance2D(a, b), 2)\n' +
      '  );\n' +
      '}\n' +
      '\n' +
      'me.onStart = function (timestamp) {\n' +
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
      '        me.flag_positions[me.next_checkpoint].position.latitude,\n' +
      '        me.flag_positions[me.next_checkpoint].position.longitude,\n' +
      '        me.flag_positions[me.next_checkpoint].position.altitude + me.id,\n' +
      '        ' + DEFAULT_SPEED + '\n' +
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
      '      dodge_point.latitude = dodge_point.latitude * -1;\n' +
      '    } else {\n' +
      '      dodge_point.longitude = dodge_point.longitude * -1;\n' +
      '    }\n' +
      '    me.setTargetCoordinates(dodge_point.latitude, dodge_point.longitude, me.getCurrentPosition().altitude, ' + DEFAULT_SPEED + ');\n' +
      '    return;\n' +
      '  }\n' +
      '};',
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    ONUPDATE_INTERVAL = 100,
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_capture_flag_logic.js',
      'gadget_erp5_page_drone_capture_map_utils.js',
      'gadget_erp5_page_drone_capture_flag_fixedwingdrone.js',
      'gadget_erp5_page_drone_capture_flag_enemydrone.js'
    ],
    DISPLAY_MAP_PARAMETER = 'display_map_parameter',
    DISPLAY_RANDOMIZE = 'display_randomize',
    DISPLAY_OPERATOR_PARAMETER = 'display_operator_parameter',
    DISPLAY_DRONE_PARAMETER = 'display_drone_parameter',
    DISPLAY_GAME_PARAMETER = 'display_game_parameter',
    DISPLAY_PLAY = "display_play";

  function renderGadgetHeader(gadget, loading) {
    var element_list = [],
      game_map_icon = 'ui-icon-map-marker',
      game_randomize_icon = 'ui-icon-random',
      game_operator_icon = 'ui-icon-rss',
      game_drone_icon = 'ui-icon-paper-plane',
      game_parameter_icon = 'ui-icon-gears',
      game_play_icon = 'ui-icon-play';


    if (loading) {
      if (gadget.state.display_step === DISPLAY_MAP_PARAMETER) {
        game_map_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_RANDOMIZE) {
        game_randomize_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_OPERATOR_PARAMETER) {
        game_operator_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_DRONE_PARAMETER) {
        game_drone_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_GAME_PARAMETER) {
        game_parameter_icon = 'ui-icon-spinner';
      } else if (gadget.state.display_step === DISPLAY_PLAY) {
        game_play_icon = 'ui-icon-spinner';
      } else {
        throw new Error("Can't render header state " +
                        gadget.state.display_step);
      }
    }

    element_list.push(
      domsugar('button', {
        type: 'button',
        text: "Map",
        disabled: (gadget.state.display_step === DISPLAY_MAP_PARAMETER),
        'class': 'display-map-parameter-btn ui-btn-icon-left ' + game_map_icon
      }),
      domsugar('button', {
        type: 'button',
        text: "Randomize",
        disabled: (gadget.state.display_step === DISPLAY_RANDOMIZE),
        'class': 'display-randomize-btn ui-btn-icon-left ' + game_randomize_icon
      }),
      domsugar('button', {
        type: 'button',
        text: "Parameters",
        disabled: (gadget.state.display_step === DISPLAY_GAME_PARAMETER),
        'class': 'display-game-parameter-btn ui-btn-icon-left ' + game_parameter_icon
      }),
      domsugar('button', {
        type: 'button',
        text: "Operator Script",
        disabled: (gadget.state.display_step === DISPLAY_OPERATOR_PARAMETER),
        'class': 'display-operator-script-btn ui-btn-icon-left ' + game_operator_icon
      }),
      domsugar('button', {
        type: 'button',
        text: "Drone Script",
        disabled: (gadget.state.display_step === DISPLAY_DRONE_PARAMETER),
        'class': 'display-drone-script-btn ui-btn-icon-left ' + game_drone_icon
      }),
      domsugar('button', {
        type: 'button',
        text: "Run",
        // Always make this button clickable, so that user can run it twice
        // disabled: (gadget.state.display_step === DISPLAY_PLAY),
        'class': 'display-play-btn ui-btn-icon-left ' + game_play_icon
      })
    );

    domsugar(gadget.element.querySelector('div.captureflagpageheader'), element_list);
  }

  function getContentFromParameterForm(gadget) {
    return gadget.getDeclaredGadget('parameter_form')
      .push(function (form_gadget) {
        return form_gadget.getContent();
      })
      .push(function (content_dict) {
        var key;
        for (key in content_dict) {
          if (content_dict.hasOwnProperty(key)) {
            gadget.state[key] = content_dict[key];
          }
        }
      });
  }

  //////////////////////////////////////////////////
  // Map parameters
  //////////////////////////////////////////////////
  function renderMapParameterView(gadget) {
    var form_gadget;
    renderGadgetHeader(gadget, true);

    //Drop backward compatibility sanitation
    function sanitize(position) {
      delete position.x;
      delete position.y;
      delete position.z;
      return position;
    }
    var map_json = JSON.parse(gadget.state.map_json);
    map_json.initial_position = sanitize(map_json.initial_position);
    map_json.flag_list.forEach(function (flag, index) {
      flag.position = sanitize(flag.position);
    });
    map_json.obstacle_list.forEach(function (obstacle, index) {
      obstacle.position = sanitize(obstacle.position);
    });
    map_json.enemy_list.forEach(function (enemy, index) {
      enemy.position = sanitize(enemy.position);
    });
    gadget.state.map_json = JSON.stringify(map_json, undefined, 4);

    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;
        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": {
              "my_map_json": {
                "description": "",
                "title": "Map JSON",
                "default": gadget.state.map_json,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "map_json",
                "hidden": 0,
                "url": "gadget_editor.html",
                "renderjs_extra": JSON.stringify({
                  "maximize": true,
                  "language": "en",
                  "editor": "codemirror"
                }),
                "type": "GadgetField"
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
              [["my_map_json"]]
            ]]
          }
        });
      })
      .push(function () {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          form_gadget.element
        ]);
      });
  }


  //////////////////////////////////////////////////
  // Map parameters
  //////////////////////////////////////////////////
  function renderRandomizeView(gadget) {
    var form_gadget;
    renderGadgetHeader(gadget, true);
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;
        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": {
              "my_map_seed": {
                "description": "Seed value to randomize the map",
                "title": "Seed value (ex: " + SEED + ")",
                "default": gadget.state.map_seed,
                "placeholder": SEED,
                "css_class": "",
                "required": 0,
                "editable": 1,
                "key": "map_seed",
                "hidden": 0,
                "type": "StringField"
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
              "center",
              [["my_map_seed"]]
            ]]
          }
        });
      })
      .push(function () {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          /*
          domsugar('label', {
            'class': 'item-label',
            text: 'Map'
          }),*/
          form_gadget.element
        ]);
      });
  }

  //////////////////////////////////////////////////
  // Operator parameters
  //////////////////////////////////////////////////
  function renderOperatorParameterView(gadget) {
    var form_gadget;
    renderGadgetHeader(gadget, true);
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;
        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": {
              "my_operator_script": {
                "description": "",
                "title": "Operator script",
                "default": gadget.state.operator_script,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "operator_script",
                "hidden": 0,
                "url": "gadget_editor.html",
                "renderjs_extra": JSON.stringify({
                  "maximize": true,
                  "language": "en",
                  "portal_type": "Web Script",
                  "editor": "codemirror"
                }),
                "type": "GadgetField"
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
              [["my_operator_script"]]
            ]]
          }
        });
      })
      .push(function () {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          form_gadget.element
        ]);
      });
  }

  //////////////////////////////////////////////////
  // Drone script parameter
  //////////////////////////////////////////////////
  function renderDroneParameterView(gadget) {
    var form_gadget;
    renderGadgetHeader(gadget, true);
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;
        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": {
              "my_drone_script": {
                "description": "",
                "title": "Drone script",
                "default": gadget.state.drone_script,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "drone_script",
                "hidden": 0,
                "url": "gadget_editor.html",
                "renderjs_extra": JSON.stringify({
                  "maximize": true,
                  "language": "en",
                  "portal_type": "Web Script",
                  "editor": "codemirror"
                }),
                "type": "GadgetField"
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
              [["my_drone_script"]]
            ]]
          }
        });
      })
      .push(function () {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          form_gadget.element
        ]);
      });
  }

  //////////////////////////////////////////////////
  // Game parameters
  //////////////////////////////////////////////////
  function renderGameParameterView(gadget) {
    var form_gadget;
    renderGadgetHeader(gadget, true);
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;

        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": {
              "my_simulation_speed": {
                "description": "",
                "title": "Simulation Speed",
                "default": gadget.state.simulation_speed,
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
                "default": gadget.state.simulation_time,
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
                "default": gadget.state.onupdate_interval,
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
                "default": gadget.state.drone_min_speed,
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
                "default": gadget.state.drone_speed,
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
                "default": gadget.state.drone_max_speed,
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
                "default": gadget.state.drone_max_acceleration,
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
                "default": gadget.state.drone_max_deceleration,
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
                "default": gadget.state.drone_max_roll,
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
                "default": gadget.state.drone_min_pitch,
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
                "default": gadget.state.drone_max_pitch,
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
                "default": gadget.state.drone_max_sink_rate,
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
                "default": gadget.state.drone_max_climb_rate,
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
                "default": gadget.state.drone_max_command_frequency,
                "css_class": "",
                "required": 1,
                "editable": 1,
                "key": "drone_max_command_frequency",
                "hidden": 0,
                "type": "FloatField"
              },
              "my_number_of_drones": {
                "description": "",
                "title": "Number of drones",
                "default": gadget.state.number_of_drones,
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
              [["my_simulation_speed"], ["my_simulation_time"], ["my_onupdate_interval"],
                ["my_number_of_drones"], ["my_map_seed"]]
            ], [
              "right",
              [["my_drone_min_speed"], ["my_drone_speed"], ["my_drone_max_speed"],
                ["my_drone_max_acceleration"], ["my_drone_max_deceleration"],
                ["my_drone_max_roll"], ["my_drone_min_pitch"], ["my_drone_max_pitch"],
                ["my_drone_max_sink_rate"], ["my_drone_max_climb_rate"],
                ["my_drone_max_command_frequency"]]
            ]]
          }
        });
      })
      .push(function () {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          form_gadget.element
        ]);
      });

  }

  //////////////////////////////////////////////////
  // Play
  //////////////////////////////////////////////////
  function renderPlayView(gadget) {
    renderGadgetHeader(gadget, true);
    // XXX Load babylonjs and run game
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "form_view_babylonjs"
    })
      .push(function (sub_gadget) {
        renderGadgetHeader(gadget, false);
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div.captureflagpagebody'), [
          domsugar('div', {
            'class': 'simulator_div'
          }),
          sub_gadget.element
        ]);

        //Backward compatibility sanitation
        function sanitize(position) {
          if (!position.latitude) {
            position.latitude = position.x;
            position.longitude = position.y;
            position.altitude = position.z;
          } else if (!position.x) {
            position.x = position.latitude;
            position.y = position.longitude;
            position.z = position.altitude;
          }
          return position;
        }
        var map_json = JSON.parse(gadget.state.map_json);
        map_json.initial_position = sanitize(map_json.initial_position);
        map_json.flag_list.forEach(function (flag, index) {
          flag.position = sanitize(flag.position);
        });
        map_json.obstacle_list.forEach(function (obstacle, index) {
          obstacle.position = sanitize(obstacle.position);
        });
        map_json.enemy_list.forEach(function (enemy, index) {
          enemy.position = sanitize(enemy.position);
        });
        gadget.state.map_json = JSON.stringify(map_json, undefined, 4);

        var operator_code = "let operator = function(operator){" +
          gadget.state.operator_script +
          "return operator.getDroneStartMessage();" +
          "}; return operator(new OperatorAPI(" + gadget.state.map_json + "));";

        /*jslint evil: true*/
        try {
          gadget.state.operator_init_msg = new Function(operator_code)();
        } catch (error) {
          return gadget.notifySubmitted({message: "Error in operator script: " +
                                         error.message, status: 'error'});
        }
        /*jslint evil: false*/

        gadget.runGame();
      });
  }

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
      return;
    })

    .declareJob('runGame', function runGame(do_nothing) {
      if (do_nothing) {
        // Cancel the previous job execution
        return;
      }
      var gadget = this,
        i,
        parsed_map,
        fragment = gadget.element.querySelector('.simulator_div'),
        game_parameters_json,
        drone_list = [];
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      for (i = 0; i < gadget.state.number_of_drones; i += 1) {
        drone_list[i] = {"id": i, "type": "FixedWingDroneAPI",
                         "script_content": gadget.state.drone_script};
      }
      try {
        parsed_map = JSON.parse(gadget.state.map_json);
      } catch (error) {
        return gadget.notifySubmitted({message: "Error: " + error.message,
                                       status: 'error'});
      }
      game_parameters_json = {
        "drone": {
          "maxAcceleration": parseInt(gadget.state.drone_max_acceleration, 10),
          "maxDeceleration": parseInt(gadget.state.drone_max_deceleration, 10),
          "minSpeed": parseInt(gadget.state.drone_min_speed, 10),
          "speed": parseFloat(gadget.state.drone_speed),
          "maxSpeed": parseInt(gadget.state.drone_max_speed, 10),
          "maxRoll": parseFloat(gadget.state.drone_max_roll),
          "minPitchAngle": parseFloat(gadget.state.drone_min_pitch),
          "maxPitchAngle": parseFloat(gadget.state.drone_max_pitch),
          "maxSinkRate": parseFloat(gadget.state.drone_max_sink_rate),
          "maxClimbRate": parseFloat(gadget.state.drone_max_climb_rate),
          "maxCommandFrequency": parseFloat(gadget.state.drone_max_command_frequency),
          "onUpdateInterval": parseInt(gadget.state.onupdate_interval, 10),
          "list": drone_list
        },
        "gameTime": parseInt(gadget.state.simulation_time, 10),
        "simulation_speed": parseInt(gadget.state.simulation_speed, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": parsed_map,
        "operator_init_msg": gadget.state.operator_init_msg,
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
          var a, blob, div, key, log, log_content, label;
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
              if (i === drone_list.length) {
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
    })

    .setState({
      operator_script: DEFAULT_OPERATOR_SCRIPT,
      drone_script: DEFAULT_SCRIPT_CONTENT,
      number_of_drones: NUMBER_OF_DRONES,
      drone_max_command_frequency: MAX_COMMAND_FREQUENCY,
      drone_max_climb_rate: MAX_CLIMB_RATE,
      drone_max_sink_rate: MAX_SINK_RATE,
      drone_max_pitch: MAX_PITCH,
      drone_min_pitch: MIN_PITCH,
      drone_max_roll: MAX_ROLL,
      drone_max_deceleration: MAX_DECELERATION,
      drone_max_acceleration: MAX_ACCELERATION,
      drone_max_speed: MAX_SPEED,
      drone_speed: DEFAULT_SPEED,
      drone_min_speed: MIN_SPEED,
      onupdate_interval: ONUPDATE_INTERVAL,
      simulation_time: SIMULATION_TIME,
      simulation_speed: SIMULATION_SPEED,
      operator_init_msg: {},
      // Force user to fill a value, to prevent
      // deleting the map by accident
      map_seed: null,
      map_json: JSON.stringify(MAP, undefined, 4)
    })

    .declareMethod('render', function render() {
      var gadget = this;
      return gadget.changeState({
        display_step: DISPLAY_PLAY
      })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Capture Flag',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (gadget.state.display_step === DISPLAY_MAP_PARAMETER) {
        if (modification_dict.hasOwnProperty('display_step')) {
          // do not update the form if it is already displayed
          return renderMapParameterView(gadget);
        }
      }

      if (gadget.state.display_step === DISPLAY_RANDOMIZE) {
        if (modification_dict.hasOwnProperty('display_step')) {
          // do not update the form if it is already displayed
          return renderRandomizeView(gadget);
        }
      }

      if (gadget.state.display_step === DISPLAY_GAME_PARAMETER) {
        if (modification_dict.hasOwnProperty('display_step')) {
          // do not update the form if it is already displayed
          return renderGameParameterView(gadget);
        }
      }

      if (gadget.state.display_step === DISPLAY_OPERATOR_PARAMETER) {
        if (modification_dict.hasOwnProperty('display_step')) {
          // do not update the form if it is already displayed
          return renderOperatorParameterView(gadget);
        }
      }

      if (gadget.state.display_step === DISPLAY_DRONE_PARAMETER) {
        if (modification_dict.hasOwnProperty('display_step')) {
          // do not update the form if it is already displayed
          return renderDroneParameterView(gadget);
        }
      }

      if (gadget.state.display_step === DISPLAY_PLAY) {
        return renderPlayView(gadget);
      }

      if (modification_dict.hasOwnProperty('display_step')) {
        throw new Error('Unhandled display step: ' + gadget.state.display_step);
      }
    })

    //////////////////////////////////////////////////
    // Used when submitting the form
    //////////////////////////////////////////////////
    .declareMethod('getContent', function () {
      var gadget = this,
        display_step = gadget.state.display_step,
        queue;

      if ([DISPLAY_OPERATOR_PARAMETER,
           DISPLAY_DRONE_PARAMETER,
           DISPLAY_MAP_PARAMETER,
           DISPLAY_GAME_PARAMETER].indexOf(gadget.state.display_step) !== -1) {
        queue = new RSVP.Queue(getContentFromParameterForm(gadget));
      } else if (gadget.state.display_step === DISPLAY_RANDOMIZE) {
        // Randomizing function is called, only if user entered a feed
        queue = new RSVP.Queue(getContentFromParameterForm(gadget))
          .push(function () {
            if (gadget.state.map_seed) {
              gadget.state.map_json = JSON.stringify(
                new MapUtils(MAP).randomize(gadget.state.map_seed),
                undefined,
                4
              );
            }
          });
      } else if (gadget.state.display_step === DISPLAY_PLAY) {
        // Cancel the run execution, by triggering the job again
        // Out job does nothing if no parameter is passed
        gadget.runGame(true);
        // Nothing to store in the play view
        queue = new RSVP.Queue();
      } else {
        throw new Error('getContent form not handled: ' + display_step);
      }

      return queue;
    }, {mutex: 'changestate'})


    .onEvent("click", function (evt) {
      // Only handle click on BUTTON element
      var gadget = this,
        tag_name = evt.target.tagName,
        queue;

      if (tag_name !== 'BUTTON') {
        return;
      }

      // Disable any button. It must be managed by this gadget
      evt.preventDefault();

      // Always get content to ensure the possible displayed form
      // is checked and content propagated to the gadget state value
      queue = gadget.getContent();

      if (evt.target.className.indexOf("display-map-parameter-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_MAP_PARAMETER
            });
          });
      }

      if (evt.target.className.indexOf("display-randomize-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_RANDOMIZE
            });
          });
      }

      if (evt.target.className.indexOf("display-operator-script-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_OPERATOR_PARAMETER
            });
          });
      }

      if (evt.target.className.indexOf("display-drone-script-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_DRONE_PARAMETER
            });
          });
      }

      if (evt.target.className.indexOf("display-game-parameter-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_GAME_PARAMETER
            });
          });
      }

      if (evt.target.className.indexOf("display-play-btn") !== -1) {
        return queue
          .push(function () {
            return gadget.changeState({
              display_step: DISPLAY_PLAY,
              force_timestamp: new Date()
            });
          });
      }

      throw new Error('Unhandled button: ' + evt.target.textContent);
    }, false, false);




}(window, rJS, domsugar, document, Blob, MapUtils, RSVP));