(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  //HARDCODED VALUES to present as defaults
  var SIMULATION_SPEED = 200,
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
    // Non-inputs parameters
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
    DRONE_LIST = [
      {"id": 0, "type": "DroneAaileFixeAPI", "script_content": ""}
    ];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .onEvent('submit', function () {
      var gadget = this;
      return gadget.getDeclaredGadget('form_view')
        .push(function (form_gadget) {
          return form_gadget.getContent();
        })
        .push(function (input) {
          console.log("from input:", input);
          gadget.runGame(input);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('input[type="submit"]').click();
    })

    .declareMethod('render', function render() {
      var gadget = this, query,
        fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;
      //TODO this should come from inputs textareas
      return new RSVP.Queue()
        .push(function () {
          query = '(portal_type:"Web Script") AND (reference:"loiter_flight_script")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          DRONE_LIST[0].script_content = result.data.rows[0].value.text_content;
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render();
        })
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
                  "required": 0,
                  "editable": 1,
                  "key": "simulation_speed",
                  "hidden": 0,
                  "type": "StringField"
                },
                "my_simulation_time": {
                  "description": "The name of a document in ERP5",
                  "title": "Simulation Time",
                  "default": SIMULATION_TIME,
                  "css_class": "",
                  "required": 0,
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
                  "required": 0,
                  "editable": 1,
                  "key": "drone_acceleration",
                  "hidden": 0,
                  "type": "TextAreaField"
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
                "my_script": {
                  "description": "",
                  "title": "",
                  "default": DRONE_LIST[0].script_content,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "script",
                  "hidden": 0,
                  "type": "TextAreaField"
                }

              }}, // TODO drone type listbox?
              "_links": {
                "type": {
                  // form_list display portal_type in header
                  name: ""
                }
              }
            },
            form_definition: {
              group_list: [[
                "left",
                [["my_simulation_speed"], ["my_simulation_time"], ["my_drone_speed"], ["my_drone_acceleration"],
                  ["my_minimum_latitud"], ["my_maximum_latitud"],
                  ["my_minimum_longitud"], ["my_maximum_longitud"],
                  ["my_init_pos_x"], ["my_init_pos_y"], ["my_init_pos_z"],
                  ["my_start_AMSL"], ["my_map_height"]]
              ],[
                "right",
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
      var gadget = this;
      return new RSVP.Queue()
        //Reload the entire gadget?
        /*var fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;
        return new RSVP.Queue()
        .push(function () {
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render();
        })*/
        .push(function () {
          return gadget.getDeclaredGadget('simulator');
        })
        .push(function (simulator) {
          DRONE_LIST[0].script_content = options.script;
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
              div = document.createElement('div');
            a.download = 'simulation_log.txt';
            a.href = window.URL.createObjectURL(blob);
            a.dataset.downloadurl =  ['text/plain', a.download,
                                      a.href].join(':');
            a.textContent = 'Download Simulation LOG ' + i;
            div.appendChild(a);
            document.querySelector('.container').appendChild(div);
          }
        });
    });

}(window, RSVP, rJS, domsugar, document, Blob));