/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, URLSearchParams, Blob*/
(function (window, rJS, domsugar, document, URLSearchParams, Blob) {
  "use strict";

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
    NUMBER_OF_DRONES = 1,
    FLAG_WEIGHT = 5,
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      'function assert(a, b, msg) {\n' +
      '  if (a === b)\n' +
      '    console.log(msg + ": OK");\n' +
      '  else\n' +
      '    console.log(msg + ": FAIL");\n' +
      '}\n' +
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
      'function compare(coord1, coord2) {\n' +
      '  assert(coord1.x, coord2.x, "Latitude")\n' +
      '  assert(coord1.y, coord2.y, "Longitude")\n' +
      '  assert(coord1.z, coord2.z, "Altitude")\n' +
      '}\n' +
      'me.onStart = function () {\n' +
      '  assert(me.getAirSpeed(), 16, "Initial speed");\n' +
      '  assert(me.getYaw(), 0, "Yaw angle")\n' +
      '  me.initialPosition = me.getCurrentPosition();\n' +
      '  me.setTargetCoordinates(\n' +
      '    me.initialPosition.x + 0.01,\n' +
      '    me.initialPosition.y,\n' +
      '    me.initialPosition.z\n' +
      '  );\n' +
      '};\n' +
      'me.onUpdate = function (timestamp) {\n' +
      'var realDistance = distance(\n' +
      '  me.initialPosition.x,\n' +
      '  me.initialPosition.y,\n' +
      '  me.getCurrentPosition().x,\n' +
      '  me.getCurrentPosition().y\n' +
      ').toFixed(8),\n' +
      '  expectedDistance = (me.getAirSpeed() * timestamp / 1000).toFixed(8);\n' +
      '  assert(timestamp, 1000 / 60, "Timestamp");\n' +
      '  assert(realDistance, expectedDistance, "Distance");\n' +
      'compare(me.getCurrentPosition(), {\n' +
      '  x: me.initialPosition.x + 2.3992831666911723e-06,\n' +
      '  y: me.initialPosition.y,\n' +
      '  z: me.initialPosition.z\n' +
      '});\n' +
      'me.exit(me.triggerParachute());\n' +
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
    .declareAcquiredMethod("notifySubmitted", "notifySubmitted")

    .declareMethod('render', function render() {
      var gadget = this;
      return gadget.runGame();
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this, i,
        fragment = gadget.element.querySelector('.simulator_div'),
        game_parameters_json, map_json;
      DRONE_LIST = [];
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      for (i = 0; i < NUMBER_OF_DRONES; i += 1) {
        DRONE_LIST[i] = {"id": i, "type": "FixedWingDroneAPI",
                         "script_content": DEFAULT_SCRIPT_CONTENT};
      }
      map_json = {
        "map_size": parseFloat(MAP_SIZE),
        "height": parseInt(map_height, 10),
        "start_AMSL": parseFloat(start_AMSL),
        "flag_list": [{
          "position": {
            "x": -27,
            "y": 72,
            "z": 10
          }
        }],
        "obstacle_list" : [],
        "drones": {
          "user": DRONE_LIST,
          "enemy": []
        }
      };
      game_parameters_json = {
        "debug_test_mode": true,
        "drone": {
          "maxAcceleration": parseInt(MAX_ACCELERATION, 10),
          "maxDeceleration": parseInt(MAX_DECELERATION, 10),
          "minSpeed": parseInt(MIN_SPEED, 10),
          "speed": parseFloat(DEFAULT_SPEED),
          "maxSpeed": parseInt(MAX_SPEED, 10),
          "maxRoll": parseFloat(MAX_ROLL),
          "minPitchAngle": parseFloat(MIN_PITCH),
          "maxPitchAngle": parseFloat(MAX_PITCH),
          "maxSinkRate": parseFloat(MAX_SINK_RATE),
          "maxClimbRate": parseFloat(MAX_CLIMB_RATE)
        },
        "gameTime": parseInt(SIMULATION_TIME, 10),
        "simulation_speed": parseInt(SIMULATION_SPEED, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": map_json,
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