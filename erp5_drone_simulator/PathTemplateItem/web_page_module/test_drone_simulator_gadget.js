/*global window, rJS, RSVP, domsugar, console, URL, Error, jIO */
/*jslint nomen: true, indent: 2, maxerr: 30, maxlen: 80, plusplus: true */
(function () {
  "use strict";

  var SIMULATION_SPEED = 100,
    MAP_KEY = "rescue_swarm_map_module/middle_of_the_sea",
    SCRIPT_KEY = "rescue_swarm_script_module/28",
    LOG_KEY = "rescue_swarm_script_module/log_1";

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
          return gadget.jio_get(options.log);
        })
        .push(function (log) {
          var i, log_entry_list = [], line_list = log.text_content.split('\n');
          for (i = 0; i < line_list.length; i += 1) {
            if (line_list[i].indexOf("AMSL") >= 0 ||
                !line_list[i].includes(";")) {
              continue;
            }
            log_entry_list.push(line_list[i]);
            console.log(line_list[i]);
          }
          return gadget.jio_get(options.map);
        })
        .push(function (map_doc) {
          options.json_map = JSON.parse(map_doc.text_content);
          return gadget.changeState({
            script_content: options.script_content,
            json_map: options.json_map
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