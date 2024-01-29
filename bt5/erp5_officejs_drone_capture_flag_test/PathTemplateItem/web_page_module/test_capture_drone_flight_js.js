/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document*/
(function (window, rJS, domsugar, document) {
  "use strict";

  var SIMULATION_SPEED = 10,
    SIMULATION_TIME = 270,
    MIN_LAT = 45.6364,
    MAX_LAT = 45.65,
    MIN_LON = 14.2521,
    MAX_LON = 14.2766,
    map_height = 700,
    start_AMSL = 595,
    INIT_LON = 14.2658,
    INIT_LAT = 45.6412,
    INIT_ALT = 15,
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
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      'function assert(a, b, msg) {\n' +
      '  if (a === b)\n' +
      '    console.log(msg + ": OK");\n' +
      '  else\n' +
      '    console.log(msg + ": FAIL");\n' +
      '}\n' +
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
      'function compare(coord1, coord2) {\n' +
      '  assert(coord1.latitude, coord2.latitude, "Latitude")\n' +
      '  assert(coord1.longitude, coord2.longitude, "Longitude")\n' +
      '  assert(coord1.altitude, coord2.altitude, "Altitude")\n' +
      '}\n' +
      '\n' +
      'me.onStart = function () {\n' +
      '  assert(me.getAirSpeed(), 16, "Initial speed");\n' +
      '  assert(me.getYaw(), 0, "Yaw angle")\n' +
      '  me.initialPosition = me.getCurrentPosition();\n' +
      '  me.setTargetCoordinates(\n' +
      '    me.initialPosition.latitude + 0.01,\n' +
      '    me.initialPosition.longitude,\n' +
      '    me.getAltitudeAbs(),\n' +
      '    16\n' +
      '  );\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
      '  var current_position = me.getCurrentPosition(),\n' +
      '    realDistance = distance(\n' +
      '    me.initialPosition.latitude,\n' +
      '    me.initialPosition.longitude,\n' +
      '    me.getCurrentPosition().latitude,\n' +
      '    me.getCurrentPosition().longitude\n' +
      '  ).toFixed(8),\n' +
      '    expectedDistance = (me.getAirSpeed() * timestamp / 1000).toFixed(8);\n' +
      '    assert(timestamp, 1000 / 60, "Timestamp");\n' +
      '    assert(realDistance, expectedDistance, "Distance");\n' +
      '  current_position.latitude = current_position.latitude.toFixed(7);\n' +
      '  compare(current_position, {\n' +
      '    latitude: (me.initialPosition.latitude + 2.3992831666911723e-06).toFixed(7),\n' +
      '    longitude: me.initialPosition.longitude,\n' +
      '    altitude: me.initialPosition.altitude\n' +
      '  });\n' +
      '  me.exit(me.triggerParachute());\n' +
      '};',
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    DRONE_LIST = [],
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_capture_flag_logic.js',
      'gadget_erp5_page_drone_capture_map_utils.js',
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

    .declareJob('runGame', function runGame() {
      var gadget = this, i,
        fragment = gadget.element.querySelector('.simulator_div'),
        game_parameters_json, map_json, operator_init_msg;
      DRONE_LIST = [];
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      for (i = 0; i < NUMBER_OF_DRONES; i += 1) {
        DRONE_LIST[i] = {"id": i, "type": "FixedWingDroneAPI",
                         "script_content": DEFAULT_SCRIPT_CONTENT};
      }
      map_json = {
        "height": parseInt(map_height, 10),
        "start_AMSL": parseFloat(start_AMSL),
        "min_lat": parseFloat(MIN_LAT),
        "max_lat": parseFloat(MAX_LAT),
        "min_lon": parseFloat(MIN_LON),
        "max_lon": parseFloat(MAX_LON),
        "flag_list": [],
        "obstacle_list" : [],
        "enemy_list" : [],
        "initial_position": {
          "longitude": parseFloat(INIT_LON),
          "latitude": parseFloat(INIT_LAT),
          "altitude": parseFloat(INIT_ALT)
        }
      };
      operator_init_msg = {
        "flag_positions": []
      };
      /*jslint evil: false*/
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
          "maxClimbRate": parseFloat(MAX_CLIMB_RATE),
          "list": DRONE_LIST
        },
        "gameTime": parseInt(SIMULATION_TIME, 10),
        "simulation_speed": parseInt(SIMULATION_SPEED, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": map_json,
        "operator_init_msg": operator_init_msg,
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
          var div = domsugar('div', { text: "CONSOLE LOG ENTRIES:" }), lines,
            l, node;
          document.querySelector('.container').parentNode.appendChild(div);
          function createLogNode(message) {
            var log_node = document.createElement("div"),
              textNode = document.createTextNode(message);
            log_node.appendChild(textNode);
            return log_node;
          }
          lines = result.console_log.split('\n');
          for (l = 0; l < lines.length; l += 1) {
            node = createLogNode(lines[l]);
            document.querySelector('.test_log').appendChild(node);
          }
        }, function (error) {
          return gadget.notifySubmitted({message: "Error: " + error.message,
                                         status: 'error'});
        });
    });

}(window, rJS, domsugar, document));