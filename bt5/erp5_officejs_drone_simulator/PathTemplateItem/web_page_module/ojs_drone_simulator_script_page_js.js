/*jslint indent: 2, maxlen: 100*/
/*global window, rJS, domsugar, document, Blob, FixedWingDroneAPI, MulticopterDroneAPI*/
(function (window, rJS, domsugar, document, Blob, API_LIST) {
  "use strict";

  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1500,
    min_lat = 45.6364,
    max_lat = 45.65,
    min_lon = 14.2521,
    max_lon = 14.2766,
    map_height = 100,
    start_AMSL = 100,
    DEFAULT_SPEED = 16,
    INITIAL_POSITION = {
      "latitude": 45.6412,
      "longitude": 14.2658,
      "altitude": 0
    },
    NUMBER_OF_DRONES = 2,
    DEFAULT_SCRIPT_CONTENT =
      '/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */\n' +
      '/*global console, me*/\n' +
      '\n' +
      '(function (console, me) {\n' +
      '  "use strict";\n' +
      '\n' +
      '  var ALTITUDE = 100,\n' +
      '    EPSILON = 9,\n' +
      '    CHECKPOINT_LIST = [],\n' +
      '    DIRECTION_LIST = [\n' +
      '      {\n' +
      '        distance: 1053,\n' +
      '        bearing: 293\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 800,\n' +
      '        bearing: 104\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 669,\n' +
      '        bearing: 352\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 925,\n' +
      '        bearing: 162\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 690,\n' +
      '        bearing: 47\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 935,\n' +
      '        bearing: 166\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 1129,\n' +
      '        bearing: 289\n' +
      '      },\n' +
      '      {\n' +
      '        distance: 520,\n' +
      '        bearing: 94\n' +
      '      }\n' +
      '    ],\n' +
      '    R = 6371e3; // meters\n' +
      '\n' +
      '  function to_deg(rad) {\n' +
      '    return rad * 180 / Math.PI;\n' +
      '  }\n' +
      '\n' +
      '  function to_rad(deg) {\n' +
      '    return deg * Math.PI / 180;\n' +
      '  }\n' +
      '\n' +
      '  function set_checkpoints(lat, lon) {\n' +
      '    var bearing_rad,\n' +
      '      lat_end,\n' +
      '      lon_end,\n' +
      '      lat_start = to_rad(lat),\n' +
      '      lon_start = to_rad(lon),\n' +
      '      relative_d;\n' +
      '\n' +
      '    DIRECTION_LIST.forEach(function (e) {\n' +
      '      bearing_rad = to_rad(e.bearing);\n' +
      '      relative_d = e.distance / R;\n' +
      '\n' +
      '      lat_end = Math.asin(Math.sin(lat_start) * Math.cos(relative_d) +\n' +
      '        Math.cos(lat_start) * Math.sin(relative_d) * Math.cos(bearing_rad));\n' +
      '      lon_end = lon_start + Math.atan2(\n' +
      '        Math.sin(bearing_rad) * Math.sin(relative_d) * Math.cos(lat_start),\n' +
      '        Math.cos(relative_d) - Math.sin(lat_start) * Math.sin(lon_start));\n' +
      '\n' +
      '      CHECKPOINT_LIST.push({' +
      '        latitude: to_deg(lat_end),\n' +
      '        longitude: to_deg(lon_end)\n' +
      '      });\n' +
      '\n' +
      '      lat_start = lat_end;\n' +
      '      lon_start = lon_end;\n' +
      '    });\n' +
      '  }\n' +
      '\n' +
      '  function distance(lat1, lon1, lat2, lon2) {\n' +
      '    var la1 = lat1 * Math.PI / 180, // lat, lon in radians\n' +
      '      la2 = lat2 * Math.PI / 180,\n' +
      '      lo1 = lon1 * Math.PI / 180,\n' +
      '      lo2 = lon2 * Math.PI / 180,\n' +
      '      haversine_phi = Math.pow(Math.sin((la2 - la1) / 2), 2),\n' +
      '      sin_lon = Math.sin((lo2 - lo1) / 2),\n' +
      '      h = haversine_phi + Math.cos(la1) * Math.cos(la2) * sin_lon * sin_lon;\n' +
      '    return 2 * R * Math.asin(Math.sqrt(h));\n' +
      '  }\n' +
      '\n' +
      '  me.onStart = function (timestamp) {\n' +
      '    me.direction_set = false;\n' +
      '    me.next_checkpoint = 0;\n' +
      '    me.takeOff();\n' +
      '  };\n' +
      '\n' +
      '  me.onUpdate = function (timestamp) {\n' +
      '    if (!me.isReadyToFly()) {\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    me.current_position = me.getCurrentPosition();\n' +
      '    if (CHECKPOINT_LIST.length === 0) {\n' +
      '      set_checkpoints(me.current_position.latitude,\n' +
      '                      me.current_position.longitude);\n' +
      '    }\n' +
      '\n' +
      '    if (!me.direction_set) {\n' +
      '      if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '        me.setTargetCoordinates(\n' +
      '          CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '          CHECKPOINT_LIST[me.next_checkpoint].longitude,\n' +
      '          ' + start_AMSL + ' + ALTITUDE + ALTITUDE * me.id,\n' +
      '          ' + DEFAULT_SPEED + '\n' +
      '        );\n' +
      '        console.log("[DEMO] Going to Checkpoint", me.next_checkpoint);\n' +
      '      }\n' +
      '      me.direction_set = true;\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    if (me.next_checkpoint < CHECKPOINT_LIST.length) {\n' +
      '      me.current_position = me.getCurrentPosition();\n' +
      '      me.distance = distance(\n' +
      '        me.current_position.latitude,\n' +
      '        me.current_position.longitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].latitude,\n' +
      '        CHECKPOINT_LIST[me.next_checkpoint].longitude\n' +
      '      );\n' +
      '      if (me.distance <= EPSILON) {\n' +
      '        console.log("[DEMO] Reached Checkpoint", me.next_checkpoint);\n' +
      '        me.next_checkpoint += 1;\n' +
      '        me.direction_set = false;\n' +
      '      }\n' +
      '      return;\n' +
      '    }\n' +
      '\n' +
      '    if (!me.isLanding()) {\n' +
      '      me.land();\n' +
      '    }\n' +
      '    if (me.getCurrentPosition().altitude <= 0) {\n' +
      '      me.exit(0);\n' +
      '    }\n' +
      '  };\n' +
      '}(console, me));\n',
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    ONUPDATE_INTERVAL = 100,
    LOGIC_FILE_LIST = [
      'gadget_erp5_page_drone_simulator_logic.js',
      'gadget_erp5_page_drone_simulator_dronelogfollower.js'
    ].concat(API_LIST.map(function (api) {
      return api.SCRIPT_NAME;
    }));

  function getAPI(droneType) {
    return API_LIST.find(function (api) {
      return api.DRONE_TYPE === droneType;
    });
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
  // Game parameters
  //////////////////////////////////////////////////
  function renderGameParameterView(gadget) {
    var api = getAPI(gadget.state.drone_type), erp5_view, form_gadget;
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "parameter_form"
    })
      .push(function (sub_gadget) {
        form_gadget = sub_gadget;

        erp5_view = {
          "my_drone_type": {
            "description": "Type of drone to simulate",
            "title": "Drone Type",
            "items": API_LIST.map(function (api) {
              return api.DRONE_TYPE;
            }),
            "value": gadget.state.drone_type,
            "css_class": "",
            "required": 1,
            "editable": 1,
            "key": "drone_type",
            "hidden": 0,
            "type": "ListField"
          },
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
          "my_minimum_latitud": {
            "description": "",
            "title": "Minimum latitude",
            "default": min_lat,
            "css_class": "",
            "required": 1,
            "editable": 1,
            "key": "min_lat",
            "hidden": 0,
            "type": "FloatField"
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
            "type": "FloatField"
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
            "type": "FloatField"
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
          "my_init_pos_lon": {
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
          "my_init_pos_alt": {
            "description": "",
            "title": "Initial drone altitude",
            "default": INITIAL_POSITION.altitude,
            "css_class": "",
            "required": 1,
            "editable": 1,
            "key": "init_pos_alt",
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
          },
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
        };
        Object.keys(api.FORM_VIEW).forEach(function (key) {
          erp5_view[key] = api.FORM_VIEW[key];
        });

        return form_gadget.render({
          erp5_document: {
            "_embedded": {"_view": erp5_view},
            "_links": {
              "type": {
                name: ""
              }
            }
          },
          form_definition: {
            group_list: [[
              "left",
              [["my_drone_type"], ["my_simulation_speed"], ["my_simulation_time"], ["my_onupdate_interval"],
                ["my_number_of_drones"], ["my_minimum_latitud"], ["my_maximum_latitud"],
                ["my_minimum_longitud"], ["my_maximum_longitud"],
                ["my_init_pos_lat"], ["my_init_pos_lon"], ["my_init_pos_alt"],
                ["my_map_height"]]
            ], [
              "right",
              [["my_start_AMSL"]].concat(
                Object.keys(api.FORM_VIEW).map(function (property_name) {
                  return [property_name];
                })
              )
            ], [
              "bottom",
              [["my_drone_script"]]
            ]]
          }
        });
      })
      .push(function () {
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div[data-gadget-scope="form_view"]'), [
          form_gadget.element
        ]);
      });

  }

  //////////////////////////////////////////////////
  // Play
  //////////////////////////////////////////////////
  function renderPlayView(gadget) {
    return gadget.declareGadget("gadget_erp5_form.html", {
      scope: "form_view_babylonjs"
    })
      .push(function (sub_gadget) {
        // Attach the form to the page
        domsugar(gadget.element.querySelector('div[data-gadget-scope="form_view_babylonjs"]'), [
          domsugar('div', {
            'class': 'simulator_div'
          }),
          sub_gadget.element
        ]);

        gadget.runGame();
      });
  }

  function formToFilename(form, drone) {
    return Object.keys(form).map(function (field_name) {
      var key = form[field_name].key;
      return key + "_" + drone[key];
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

    .allowPublicAcquisition('notifyChange', function (argument_list, scope) {
      return this.triggerAPIChange(scope);
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('input[type="submit"]').click();
    })

    .onEvent('submit', function () {
      return this.getContent();
    })

    .declareMethod("triggerAPIChange", function (scope) {
      var gadget = this,
        sub_gadget;

      return gadget.getDeclaredGadget(scope)
        .push(function (result) {
          sub_gadget = result;
          return sub_gadget.getContent();
        })
        .push(function (result) {
          if (gadget.state.drone_type !== result.drone_type) {
            return gadget.changeState({
              drone_type: result.drone_type
            });
          }
        });
    })

    .declareJob('runGame', function runGame() {
      var gadget = this, i,
        fragment = domsugar(gadget.element.querySelector('.simulator_div'),
                    [domsugar('div')]).firstElementChild,
        game_parameters_json,
        drone_list = [],
        api = getAPI(gadget.state.drone_type),
        drone_parameter_list = Object.keys(api.FORM_VIEW);
      for (i = 0; i < gadget.state.number_of_drones; i += 1) {
        drone_list[i] = {"id": i, "type": api.name,
                         "script_content": gadget.state.drone_script};
      }
      game_parameters_json = {
        "drone": {
          "onUpdateInterval": parseInt(gadget.state.onupdate_interval, 10),
          "list": drone_list
        },
        "gameTime": parseInt(gadget.state.simulation_time, 10),
        "simulation_speed": parseInt(gadget.state.simulation_speed, 10),
        "latency": {
          "information": 0,
          "communication": 0
        },
        "map": {
          "min_lat": parseFloat(gadget.state.min_lat),
          "max_lat": parseFloat(gadget.state.max_lat),
          "min_lon": parseFloat(gadget.state.min_lon),
          "max_lon": parseFloat(gadget.state.max_lon),
          "height": parseInt(gadget.state.map_height, 10),
          "start_AMSL": parseFloat(gadget.state.start_AMSL)
        },
        "initialPosition": {
          "longitude": parseFloat(gadget.state.init_pos_lon),
          "latitude": parseFloat(gadget.state.init_pos_lat),
          "altitude": parseFloat(gadget.state.init_pos_alt)
        },
        "draw_flight_path": DRAW,
        "temp_flight_path": true,
        "log_drone_flight": LOG,
        "log_interval_time": LOG_TIME
      };
      drone_parameter_list.forEach(function (parameter) {
        var field = api.FORM_VIEW[parameter];
        switch (field.type) {
        case 'IntegerField':
          game_parameters_json.drone[field.key] = parseInt(gadget.state[field.key], 10);
          break;
        case 'FloatField':
          game_parameters_json.drone[field.key] = parseFloat(gadget.state[field.key]);
          break;
        default:
          throw new Error("Unhandled field type");
        }
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
          var a, blob, div, key, log, log_content;
          i = 0;
          for (key in result.content) {
            if (result.content.hasOwnProperty(key)) {
              log_content = result.content[key].join('\n').replaceAll(",", ";");
              blob = new Blob([log_content], {type: 'text/plain'});
              a = domsugar('a', {
                text: 'Download Simulation LOG ' + i,
                download: ['simulation_log_' + i].concat(
                  formToFilename(api.FORM_VIEW, game_parameters_json.drone)
                ).join("_") + ".txt",
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
    })

    .setState({
      drone_type: API_LIST[0].DRONE_TYPE,
      drone_script: DEFAULT_SCRIPT_CONTENT,
      number_of_drones: NUMBER_OF_DRONES,
      onupdate_interval: ONUPDATE_INTERVAL,
      simulation_time: SIMULATION_TIME,
      simulation_speed: SIMULATION_SPEED,
      min_lat: min_lat,
      max_lat: max_lat,
      min_lon: min_lon,
      max_lon: max_lon,
      height: map_height,
      start_AMSL: start_AMSL,
      longitude: INITIAL_POSITION.longitude,
      latitude: INITIAL_POSITION.latitude,
      altitude: INITIAL_POSITION.altitude
    })

    .declareMethod('render', function render() {
      var gadget = this;
      return renderGameParameterView(gadget)
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Edit and run script',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .onStateChange(function (modification_dict) {
      var gadget = this;

      if (modification_dict.hasOwnProperty('drone_type')) {
        return getContentFromParameterForm(this)
          .push(function () {
            return renderGameParameterView(gadget);
          });
      }
    })

    .declareMethod('getContent', function () {
      var gadget = this;
      return getContentFromParameterForm(this)
        .push(function () {
          return renderPlayView(gadget);
        });
    }, {mutex: 'changestate'});

}(window, rJS, domsugar, document, Blob, [MulticopterDroneAPI, FixedWingDroneAPI]));