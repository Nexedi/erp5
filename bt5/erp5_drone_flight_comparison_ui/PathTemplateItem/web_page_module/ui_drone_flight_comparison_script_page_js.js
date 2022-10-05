(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  //HARDCODED VALUES to present as defaults
  var SIMULATION_SPEED = 200,
    //TODO end game when all drones are stopped or down
    SIMULATION_TIME = 1000,
    MAX_SPEED = 7.542174921016468, //16.666667,
    MAX_ACCELERATION = 1,
    min_lat = 45.6364,
    max_lat = 45.65,
    min_lon = 14.2521,
    max_lon = 14.2766,
    map_height = 100,
    start_AMSL = 595.328,
    INITIAL_POSITION = {
      "x": -12.316326531328059,
      "y": -218.55882352976022,
      "z": 15
    },
    NUMBER_OF_DRONES = 3,
    // Non-inputs parameters
    DEFAULT_SCRIPT_CONTENT =
      '/**\n' +
      ' * The minimal expresion of a AI drone scrip\n' +
      '**/\n' +
      '/**\n\n' +
      ' * Start function called at the beginning of the simulation\n' +
      ' * "me" is each drone itself\n' +
      '**/\n' +
      'me.onStart = function() {\n' +
      '  //set initial values for a drone like acceleration\n' +
      '  me.setAcceleration(10);\n' +
      '  // e.g. arbitrary coordinates\n' +
      '  var lat = 45.64492790560583 + me.id * 0.01;\n' +
      '  var lon = 14.25334942966329 - me.id * 0.01;\n' +
      '  me.setTargetCoordinates(lat,lon,10);\n' +
      '}\n\n' +
      '/**\n' +
      ' * Update function is called 30 times / second\n' +
      ' * On every execution, information of the current state of simulation can be get\n' +
      ' * and the drone team strategy can be updated\n' +
      '**/\n' +
      'me.onUpdate = function () {\n' +
      '}\n',
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
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('form_view');
        })
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
                "my_init_pos_x": {
                  "description": "",
                  "title": "Initial drone position X",
                  "default": INITIAL_POSITION.x,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_x",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_init_pos_y": {
                  "description": "",
                  "title": "Initial drone position Y",
                  "default": INITIAL_POSITION.y,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "init_pos_y",
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
                 ["my_init_pos_x"], ["my_init_pos_y"], ["my_init_pos_z"]]
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
      //TODO handle crash. e.g. pass empty or invalid script
      var gadget = this, simulator;
      return new RSVP.Queue()
        .push(function () {
          var fragment = gadget.element.querySelector('#fragment');
          //drop previous execution
          if (fragment.childNodes[0]) {
            fragment.removeChild(fragment.childNodes[0]);
          }
          fragment = domsugar(gadget.element.querySelector('#fragment'),
                                  [domsugar('div')]).firstElementChild;
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
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
              "x": parseFloat(options.init_pos_x),
              "y": parseFloat(options.init_pos_y),
              "z": parseFloat(options.init_pos_z)
            },
            "draw_flight_path": DRAW,
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
              a = document.createElement('a'),
              log = document.createElement('textarea'),
              div = document.createElement('div');
            log.value = log_content;
            a.download = 'simulation_log.txt';
            a.href = window.URL.createObjectURL(blob);
            a.dataset.downloadurl =  ['text/plain', a.download,
                                      a.href].join(':');
            a.textContent = 'Download Simulation LOG ' + i;
            div.appendChild(a);
            document.querySelector('.container').appendChild(div);
            document.querySelector('.container').appendChild(log);
          }
        });
    });

}(window, RSVP, rJS, domsugar, document, Blob));