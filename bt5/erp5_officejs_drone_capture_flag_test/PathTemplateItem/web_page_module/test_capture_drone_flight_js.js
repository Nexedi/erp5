/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document*/
(function (window, rJS, domsugar, document) {
  "use strict";

  var SIMULATION_SPEED = 1,
    LOOP_INTERVAL = 1000 / 60,
    SIMULATION_TIME = LOOP_INTERVAL / 1000,
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
      'me.onStart = function (timestamp) {\n' +
      '  assert(me.getSpeed(), ' + DEFAULT_SPEED + ', "Initial speed");\n' +
      '  assert(me.getYaw(), 0, "Yaw angle")\n' +
      '  me.initialPosition = me.getCurrentPosition();\n' +
      '  me.start_time = timestamp;\n' +
      '  me.setTargetCoordinates(\n' +
      '    me.initialPosition.latitude + 0.01,\n' +
      '    me.initialPosition.longitude,\n' +
      '    me.getAltitudeAbs(),\n' +
      '    ' + DEFAULT_SPEED + '\n' +
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
      '    time_interval = timestamp - me.start_time,\n' +
      '    expected_interval = ' + LOOP_INTERVAL + ',\n' +
      '    expectedDistance = (me.getSpeed() * expected_interval / 1000).toFixed(8);\n' +
      '    assert(time_interval, Math.floor(expected_interval), "Timestamp");\n' +
      '    assert(realDistance, expectedDistance, "Distance");\n' +
      '  current_position.latitude = current_position.latitude.toFixed(7);\n' +
      '  compare(current_position, {\n' +
      '    latitude: (me.initialPosition.latitude + 2.3992831666911723e-06).toFixed(7),\n' +
      '    longitude: me.initialPosition.longitude,\n' +
      '    altitude: me.initialPosition.altitude\n' +
      '  });\n' +
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
        "height": map_height,
        "start_AMSL": start_AMSL,
        "min_lat": MIN_LAT,
        "max_lat": MAX_LAT,
        "min_lon": MIN_LON,
        "max_lon": MAX_LON,
        "flag_list": [],
        "obstacle_list" : [],
        "enemy_list" : [],
        "initial_position": {
          "longitude": INIT_LON,
          "latitude": INIT_LAT,
          "altitude": INIT_ALT
        }
      };
      operator_init_msg = {
        "flag_positions": []
      };
      /*jslint evil: false*/
      game_parameters_json = {
        "debug_test_mode": true,
        "drone": {
          "maxAcceleration": MAX_ACCELERATION,
          "maxDeceleration": MAX_DECELERATION,
          "minSpeed": MIN_SPEED,
          "speed": DEFAULT_SPEED,
          "maxSpeed": MAX_SPEED,
          "maxRoll": MAX_ROLL,
          "minPitchAngle": MIN_PITCH,
          "maxPitchAngle": MAX_PITCH,
          "maxSinkRate": MAX_SINK_RATE,
          "maxClimbRate": MAX_CLIMB_RATE,
          "list": DRONE_LIST
        },
        "gameTime": SIMULATION_TIME,
        "simulation_speed": SIMULATION_SPEED,
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
            l, test_log_node = document.querySelector('.test_log');
          document.querySelector('.container').parentNode.appendChild(div);
          function appendToTestLog(test_log_node, message) {
            var log_node = document.createElement("div"),
              textNode = document.createTextNode(message);
            log_node.appendChild(textNode);
            test_log_node.appendChild(log_node);
          }
          lines = result.console_log.split('\n');
          for (l = 0; l < lines.length; l += 1) {
            if (lines[l] !== 'TIMEOUT!') {
              appendToTestLog(test_log_node, lines[l]);
            } else {
              appendToTestLog(test_log_node, 'Timeout: OK');
              return;
            }
          }
          appendToTestLog(test_log_node, 'Timeout: FAILED');
        }, function (error) {
          return gadget.notifySubmitted({message: "Error: " + error.message,
                                         status: 'error'});
        });
    });

}(window, rJS, domsugar, document));