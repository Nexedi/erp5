/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, MulticopterDroneAPI*/
(function (window, rJS, domsugar, document, MulticopterDroneAPI) {
  "use strict";

  var SIMULATION_SPEED = 100,
    LOOP_INTERVAL = 1000 / 60,
    ON_UPDATE_INTERVAL = LOOP_INTERVAL,
    SIMULATION_TIME = 714 * LOOP_INTERVAL / 1000,
    MIN_LAT = 45.6364,
    MAX_LAT = 45.65,
    MIN_LON = 14.2521,
    MAX_LON = 14.2766,
    map_height = 700,
    start_AMSL = 595,
    INIT_LON = 14.2658,
    INIT_LAT = 45.6412,
    INIT_ALT = 0,
    DEFAULT_SPEED = 5,
    STEP = 2.3992831666911723e-06 / 16,
    TAKEOFF_ALTITUDE = 7,
    NUMBER_OF_DRONES = 1,
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
      '  assert(coord1.latitude, coord2.latitude, "Latitude");\n' +
      '  assert(coord1.longitude, coord2.longitude, "Longitude");\n' +
      '  assert(coord1.altitude, coord2.altitude, "Altitude");\n' +
      '}\n' +
      '\n' +
      'me.onStart = function (timestamp) {\n' +
      '  assert(me.getSpeed(), 0, "Initial speed");\n' +
      '  assert(me.getYaw(), 0, "Yaw angle");\n' +
      '  me.start_time = timestamp;\n' +
      '  me.takeOff();\n' +
      '  me.direction_set = false;\n' +
      '  me.interval_ckecked = false;\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
      '  if (!me.interval_ckecked) {\n' +
      '    var time_interval = timestamp - me.start_time,\n' +
      '      expected_interval = ' + LOOP_INTERVAL + ';\n' +
      '    assert(time_interval.toFixed(4), expected_interval.toFixed(4), "Timestamp");\n' +
      '    assert(Date.now(), timestamp, "Date");\n' +
      '    me.interval_ckecked = true;\n' +
      '  }\n' +
      '  if (!me.isReadyToFly()) {\n' +
      '    return;\n' +
      '  } else {\n' +
      '    if (me.direction_set === false) {\n' +
      '      me.initialPosition = me.getCurrentPosition();\n' +
      '      me.initialPosition.altitude = me.initialPosition.altitude.toFixed(2);\n' +
      '      assert(me.initialPosition.altitude, (' + TAKEOFF_ALTITUDE + ').toFixed(2),\n' +
      '             "Altitude");\n' +
      '      me.direction_set = true;\n' +
      '      return me.setTargetCoordinates(\n' +
      '        me.initialPosition.latitude + 0.01,\n' +
      '        me.initialPosition.longitude,\n' +
      '        me.getAltitudeAbs(),\n' +
      '        ' + DEFAULT_SPEED + '\n' +
      '      );\n' +
      '    }\n' +
      '  }\n' +
      '  var current_position = me.getCurrentPosition(),\n' +
      '    realDistance = distance(\n' +
      '    me.initialPosition.latitude,\n' +
      '    me.initialPosition.longitude,\n' +
      '    me.getCurrentPosition().latitude,\n' +
      '    me.getCurrentPosition().longitude\n' +
      '  ).toFixed(8),\n' +
      '    expectedDistance = (me.getSpeed() * ' + LOOP_INTERVAL + ' / 1000).toFixed(8);\n' +
      '    assert(realDistance, expectedDistance, "Distance");\n' +
      '  current_position.latitude = current_position.latitude.toFixed(7);\n' +
      '  current_position.altitude = current_position.altitude.toFixed(2);\n' +
      '  compare(current_position, {\n' +
      '    latitude: (me.initialPosition.latitude + me.getSpeed() *' + STEP + ').toFixed(7),\n' +
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
      'gadget_erp5_page_drone_capture_flag_enemydrone.js',
      MulticopterDroneAPI.SCRIPT_NAME
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
        DRONE_LIST[i] = {"id": i, "type": MulticopterDroneAPI.name,
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
          "onUpdateInterval": ON_UPDATE_INTERVAL,
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
      Object.keys(MulticopterDroneAPI.FORM_VIEW).forEach(function (parameter) {
        var field = MulticopterDroneAPI.FORM_VIEW[parameter];
        game_parameters_json.drone[field.key] = field.default;
      });
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

}(window, rJS, domsugar, document, MulticopterDroneAPI));