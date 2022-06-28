/*global window, rJS, RSVP, domsugar, console, URL, Error, jIO */
/*jslint nomen: true, indent: 2, maxerr: 30, maxlen: 80, plusplus: true */
(function () {
  "use strict";

  var SIMULATION_SPEED = 100,
    MAP_KEY = "rescue_swarm_map_module/medium_map",
    SCRIPT_KEY = "rescue_swarm_script_module/28",
    LOG_KEY = "rescue_swarm_script_module/log_1",
    MAP_WIDTH = 1000,
    MAP_HEIGHT = 1000;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")

    .declareJob('run', function () {
      var gadget = this,
        queue = new RSVP.Queue(),
        game_value,
        fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;

      gadget.state.json_map.randomSpawn.rightTeam.dispersed = true;
      game_value = JSON.stringify({
        map: gadget.state.json_map,
        autorun: true,
        script: gadget.state.script_content,
        simulation_speed: SIMULATION_SPEED
      });
      queue
        .push(function () {
          return gadget.declareGadget("gadget_drone_simulator.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render({
            "key": 'simulator',
            "maximize": false,
            "value": game_value,
            "autorun": true
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('simulator');
        })
        .push(function (game_editor) {
          return game_editor.getContent();
        })
        .push(function (result) {
          return result;
        });
      return queue;
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      options.map = MAP_KEY;
      options.script = SCRIPT_KEY;
      options.log = LOG_KEY;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.script);
        })
        .push(function (script) {
          options.script_content = script.text_content;
          return gadget.jio_get(options.map);
        })
        .push(function (map_doc) {
          options.json_map = JSON.parse(map_doc.text_content);
          MAP_WIDTH = options.json_map.mapSize.width;
          MAP_HEIGHT = options.json_map.mapSize.height;
          return gadget.jio_get(options.log);
        })
        .push(function (log) {
          var position_list = [], line_list = log.text_content.split('\n'),
            i, j, min_x = 99999, min_y = 99999, max_x = 0, max_y = 0, n_x, n_y,
            log_entry, log_entry_array, lat, lon, x, y, pos_x, pos_y;
          for (i = 0; i < line_list.length; i += 1) {
            if (line_list[i].indexOf("AMSL") >= 0 ||
                !line_list[i].includes(";")) {
              continue;
            }
            log_entry = line_list[i].trim();
            if (log_entry) {
              log_entry_array = log_entry.split(";");
              lat = parseFloat(log_entry_array[1]);
              lon = parseFloat(log_entry_array[2]);
              //convert geo cordinates into 2D plane coordinates
              x = (MAP_WIDTH / 360.0) * (180 + lon);
              y = (MAP_HEIGHT / 180.0) * (90 - lat);
              position_list.push([x, y]);
              //get min x and min y to normalize later
              if (x < min_x) {
                min_x = x;
              }
              if (y < min_y) {
                min_y = y;
              }
              if (x > max_x) {
                max_x = x;
              }
              if (y > max_y) {
                max_y = y;
              }
            }
          }
          for (j = 0; j < position_list.length; j += 1) {
            if (position_list[j]) {
              //normalize coordinate values
              n_x = (position_list[j][0] - min_x) / (max_x - min_x);
              n_y = (position_list[j][1] - min_y) / (max_y - min_y);
              pos_x = Math.round(n_x * 1000) - MAP_WIDTH / 2;
              pos_y = Math.round(n_y * 1000) - MAP_HEIGHT / 2;
              position_list[j] = [pos_x, pos_y];
              //console.log(Math.round(n_x * 1000), Math.round(n_y * 1000));
            }
          }
          return gadget.changeState({
            script_content: options.script_content,
            json_map: options.json_map,
            position_list: position_list
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: "Test drone gadget"
      })
        .push(function () {
          gadget.run();
        });
    });
}());