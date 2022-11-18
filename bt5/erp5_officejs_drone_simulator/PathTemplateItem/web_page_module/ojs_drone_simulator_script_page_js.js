(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  //Default values
  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1500,
    MAX_SPEED = 7.5, //16.666667,
    MAX_ACCELERATION = 1,
    min_lat = 45.6364,
    max_lat = 45.65,
    min_lon = 14.2521,
    max_lon = 14.2766,
    map_height = 100,
    start_AMSL = 595,
    INITIAL_POSITION = {
      "latitude": 45.6412,
      "longitude": 14.2658,
      "z": 15
    },
    NUMBER_OF_DRONES = 2,
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      'var ALTITUDE = 100,\n' +
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
      '    },\n' +
      '    {\n' +
      '      altitude: 608.6648153348965,\n' +
      '      latitude: 45.64911917196595,\n' +
      '      longitude: 14.26214792790128\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 606.1448368129072,\n' +
      '      latitude: 45.64122685351364,\n' +
      '      longitude: 14.26590493128597\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 630.0829598206344,\n' +
      '      latitude: 45.64543355564817,\n' +
      '      longitude: 14.27242391207985\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 616.1839898415284,\n' +
      '      latitude: 45.6372792927328,\n' +
      '      longitude: 14.27533492411138\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 598.0603137354178,\n' +
      '      latitude: 45.64061299543953,\n' +
      '      longitude: 14.26161958465814\n' +
      '    },\n' +
      '    {\n' +
      '      altitude: 607.1243119862851,\n' +
      '      latitude: 45.64032340702919,\n' +
      '      longitude: 14.2682896662383\n' +
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
      '        CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].longitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].altitude + ALTITUDE + ALTITUDE * me.id\n' +
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
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    DRONE_LIST = [];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")

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
      var gadget = this, query;
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
                  "type": "StringField"
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
                  "type": "StringField"
                },
                "my_drone_speed": {
                  "description": "",
                  "title": "Drone speed",
                  "default": MAX_SPEED,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_speed",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_drone_acceleration": {
                  "description": "",
                  "title": "Drone Acceleration",
                  "default": MAX_ACCELERATION,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "drone_acceleration",
                  "hidden": 0,
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                  "type": "StringField"
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
                [["my_simulation_speed"], ["my_simulation_time"],
                 ["my_drone_speed"], ["my_drone_acceleration"],
                 ["my_number_of_drones"], ["my_map_height"], ["my_start_AMSL"]]
              ],[
                "right",
                [["my_minimum_latitud"], ["my_maximum_latitud"],
                 ["my_minimum_longitud"], ["my_maximum_longitud"],
                 ["my_init_pos_lat"], ["my_init_pos_lon"], ["my_init_pos_z"]]
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
      var gadget = this, simulator,
        fragment = gadget.element.querySelector('.simulator_div');
      fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                              [domsugar('div')]).firstElementChild;
      DRONE_LIST = [];
      return gadget.declareGadget("gadget_erp5_page_drone_simulator_gadget.html",
                                  {element: fragment, scope: 'simulator'})
        .push(function (drone_gadget) {
          simulator = drone_gadget;
          return simulator.render();
        })
        .push(function () {
          for (var i = 0; i < options.number_of_drones; i += 1) {
            DRONE_LIST[i] = {"id": i, "type": "DroneAaileFixeAPI", "script_content": options.script};
          }
          var game_parameters_json = {
            "drone": {
              "maxAcceleration": parseFloat(options.drone_acceleration),
              "maxSpeed": parseFloat(options.drone_speed)
            },
            "gameTime": parseFloat(options.simulation_time),
            "simulation_speed": parseFloat(options.simulation_speed),
            "latency": {
              "information": 0,
              "communication": 0
            },
            "map": {
              "min_lat": parseFloat(options.min_lat),
              "max_lat": parseFloat(options.max_lat),
              "min_lon": parseFloat(options.min_lon),
              "max_lon": parseFloat(options.max_lon),
              "height": parseFloat(options.map_height),
              "start_AMSL": parseFloat(options.start_AMSL)
            },
            "initialPosition": {
              "longitude": parseFloat(options.init_pos_lon),
              "latitude": parseFloat(options.init_pos_lat),
              "z": parseFloat(options.init_pos_z)
            },
            "draw_flight_path": DRAW,
            "temp_flight_path": true,
            "log_drone_flight": LOG,
            "log_interval_time": LOG_TIME,
            "droneList": DRONE_LIST
          };
          return simulator.runGame({
            game_parameters: game_parameters_json
          });
        })
        .push(function (result_list) {
          for (var i = 0; i < result_list.length; i += 1) {
            var log_content = result_list[i].join('\n').replaceAll(",", ";"),
              blob = new Blob([log_content], {type: 'text/plain'}),
              a = domsugar('a', {
                text: 'Download Simulation LOG ' + i,
                download: 'simulation_log.txt',
                href: window.URL.createObjectURL(blob)
              }),
              log = domsugar('textarea', { value: log_content }),
              div = domsugar('div', [a]);
            a.dataset.downloadurl =  ['text/plain', a.download,
                                      a.href].join(':');
            document.querySelector('.container').appendChild(div);
            document.querySelector('.container').appendChild(log);
          }
        });
    });

}(window, RSVP, rJS, domsugar, document, Blob));