(function (window, RSVP, rJS, domsugar, document, Blob) {
  "use strict";

  //HARDCODED VALUES FROM LOG, TODO get from UI inputs
  var SIMULATION_SPEED = 200,
    SIMULATION_TIME = 2000,
    map_size = 1143,
    map_height = 100,
    //TODO this should be lat-lon and drone or map should convert it to x-t
    min_x = 616.7504175,
    max_x = 616.828205,
    min_y = 281.70885999999996,
    max_y = 281.6225,
    min_lat = 45.6364,
    max_lat = 45.65,
    min_lon = 14.2521,
    max_lon = 14.2766,
    start_AMSL = 595.328,
    MAX_SPEED = 7.542174921016468, //16.666667,
    MAX_ACCELERATION = 1,
    INITIAL_POSITION = {
      "x": -12.316326531328059,
      "y": -218.55882352976022,
      "z": 15
    },
    DRAW = true,
    LOG = true,
    LOG_TIME = 1662.7915426540285,
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

    .declareMethod('render', function render() {
      var gadget = this, log_content_1, log_content_2, query,
        fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;
      //TODO this should come from inputs textareas
      return new RSVP.Queue()
        .push(function () {
          query = '(portal_type:"Web Manifest") AND (reference:"loiter_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          log_content_1 = result.data.rows[0].value.text_content;
          DRONE_LIST[0].log_content = result.data.rows[0].value.text_content;
          query = '(portal_type:"Web Manifest") AND (reference:"bounce_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          log_content_2 = result.data.rows[0].value.text_content;
          DRONE_LIST[1].log_content = result.data.rows[0].value.text_content;
          return gadget.declareGadget("gadget_erp5_page_flight_comparison_gadget.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render();
        })
        .push(function () {
          //TODO this should be called in a button click event
          gadget.runGame({
            log: log_content_1
          });
          return gadget.updateHeader({
            page_title: 'Drone Simulator - Run flight logs',
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
            "initialPosition": INITIAL_POSITION,
            "draw_flight_path": DRAW,
            "log_drone_flight": LOG,
            "log_interval_time": LOG_TIME,
            "droneList": DRONE_LIST
          };
          return simulator.runGame({
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