(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1500,
    DRAW = true,
    LOG = false,
    DRONE_LIST = [
      {"id": 0, "type": "DroneLogAPI", "log_content": ""},
      {"id": 1, "type": "DroneLogAPI", "log_content": ""}
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
          gadget.runGame(input);
        });
    })

    .declareMethod("triggerSubmit", function () {
      return this.element.querySelector('input[type="submit"]').click();
    })

    .declareMethod('render', function render() {
      var gadget = this, query;
      return new RSVP.Queue()
        .push(function () {
          query = '(portal_type:"Web Manifest") AND (reference:"loiter_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          DRONE_LIST[0].log_content = result.data.rows[0].value.text_content;
          //query = '(portal_type:"Web Manifest") AND (reference:"bounce_flight_log")';
          query = '(portal_type:"Web Manifest") AND (reference:"result_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          DRONE_LIST[1].log_content = result.data.rows[0].value.text_content;
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
                "my_log_1": {
                  "description": "Log 1 content",
                  "title": "",
                  "default": DRONE_LIST[0].log_content,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "log_1",
                  "hidden": 0,
                  "type": "TextAreaField"
                },
                "my_log_2": {
                  "description": "Log 2 content",
                  "title": "",
                  "default": DRONE_LIST[1].log_content,
                  "css_class": "",
                  "required": 1,
                  "editable": 1,
                  "key": "log_2",
                  "hidden": 0,
                  "type": "TextAreaField"
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
                [["my_log_1"], ["my_simulation_speed"]]
              ],[
                "right",
                [["my_log_2"]]
              ]]
            }
          });
        })
        .push(function () {
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Run flight logs',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
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
          DRONE_LIST[0].log_content = options.log_1;
          DRONE_LIST[1].log_content = options.log_2;
          var game_parameters_json = {
            "drone": {
              "maxAcceleration": 1,
              "maxSpeed": 1
            },
            "gameTime": SIMULATION_TIME,
            "simulation_speed": parseFloat(options.simulation_speed),
            "latency": {
              "information": 0,
              "communication": 0
            },
            "draw_flight_path": DRAW,
            "log_drone_flight": LOG,
            "droneList": DRONE_LIST
          };
          return simulator.runGame({
            game_parameters: game_parameters_json
          });
        });
    });

}(window, RSVP, rJS, domsugar, document, Blob));