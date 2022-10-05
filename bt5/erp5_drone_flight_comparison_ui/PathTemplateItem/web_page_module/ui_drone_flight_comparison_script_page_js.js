(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  //HARDCODED VALUES, TODO get from UI inputs
  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 1800,
    map_size = 1143,
    map_height = 100,
    min_x = 616.7504175,
    max_x = 616.828205,
    min_y = 281.70885999999996,
    max_y = 281.6225,
    start_AMSL = 595.328,
    MAX_SPEED = 16.666667,
    MAX_ACCELERATION = 1,
    DRONE_LIST = ["DroneAaileFixeAPI", "DroneLogAPI"];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function renderHeader() {
      var gadget = this, script_content, log_content, query,
        fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;
      //TODO this should come from inputs textareas
      return new RSVP.Queue()
        .push(function () {
          query = '(portal_type:"Web Script") AND (reference:"loiter_flight_script")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          script_content = result.data.rows[0].value.text_content;
          query = '(portal_type:"Web Manifest") AND (reference:"loiter_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          log_content = result.data.rows[0].value.text_content;
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render();
        })
        .push(function () {
          //TODO this should be called in a button click event
          gadget.runGame({
            script: script_content,
            log: log_content
          });
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Edit and run script',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      //TODO handle crash. e.g. pass empty log_content
      var gadget = this;
      return new RSVP.Queue()
        .push(function () {
          return gadget.getDeclaredGadget('simulator');
        })
        .push(function (simulator) {
          var game_parameters_json = {
            "drone": {
              "maxAcceleration": 1,
              "maxSpeed": MAX_SPEED
            },
            "gameTime": SIMULATION_TIME,
            "simulation_speed": SIMULATION_SPEED,
            "latency": {
              "information": 0,
              "communication": 0
            },
            "map": {
              "depth": map_size,
              "height": map_height,
              "width": map_size,
              "min_x": min_x,
              "min_y": min_y,
              "max_x": max_x,
              "max_y": max_y,
              "start_AMSL": start_AMSL
            },
            "initialPosition": {
              "x": 0,
              "y": 0,
              "z": 20
            },
            "droneList": DRONE_LIST
          };
          return simulator.runGame({
            script: options.script,
            log: options.log,
            game_parameters: game_parameters_json
          });
        })
        .push(function (result_list) {
          for (var i = 0; i < result_list.length; i += 1) {
            var log_content = result_list[i].join(' ') + '\n',
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