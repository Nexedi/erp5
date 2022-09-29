(function (window, rJS, domsugar, DroneGameManager) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function renderHeader() {
      var gadget = this,
        logic_file_list = [],
        canvas = domsugar('canvas'),
        simulation_speed,
        offscreen;
      domsugar(gadget.element, [canvas]);

      // XXX hardcoded
      simulation_speed = 100;
      logic_file_list.push('gadget_erp5_page_drone_simulator_logic_comparison.js');
      logic_file_list.push('gadget_erp5_page_flight_comparison_droneaaailefixe.js');
      logic_file_list.push('gadget_erp5_page_flight_comparison_dronelogfollower.js');
      //TODO fix hardcoded
      canvas.width = 680;//canvas.clientWidth; <-- this is 0
      canvas.height = 340;//canvas.clientHeight; <-- this is 0

      // https://doc.babylonjs.com/divingDeeper/scene/offscreenCanvas
      offscreen = canvas.transferControlToOffscreen();

      var script_content, log_content;
      return new RSVP.Queue()
        .push(function () {
          var query = '(portal_type:"Web Script") AND (reference:"loiter_flight_script")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          script_content = result.data.rows[0].value.text_content;
          var query = '(portal_type:"Web Manifest") AND (reference:"loiter_flight_log")';
          return gadget.jio_allDocs({query: query, select_list: ["text_content"]});
        })
        .push(function (result) {
          log_content = result.data.rows[0].value.text_content;

          gadget.runGame({
            logic_url_list: logic_file_list,
            canvas: offscreen,
            canvas_original: canvas,
            width: canvas.width,
            height: canvas.height,
            script: script_content,
            log: log_content,
            simulation_speed: simulation_speed
          });

          return gadget.updateHeader({
            page_title: 'Drone Simulator - Flight comparison',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this,
        game_manager = new DroneGameManager();
      return game_manager.play(options)
      .push(function () {
        console.log("simulation result:", game_manager.result());
      });
    });

}(window, rJS, domsugar, DroneGameManager));