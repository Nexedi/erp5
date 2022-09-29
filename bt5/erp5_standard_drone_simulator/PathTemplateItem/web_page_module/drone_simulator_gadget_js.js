(function (window, rJS, domsugar, DroneGameManager) {
  "use strict";

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")

    .declareMethod('render', function renderHeader() {
      var gadget = this,
        logic_file_list = [],
        canvas = domsugar('canvas'),
        offscreen;
      domsugar(gadget.element, [canvas]);

      // XXX hardcoded
      logic_file_list.push('gadget_erp5_page_drone_simulator_logic.js');

      //TODO fix hardcoded
      canvas.width = 680;//canvas.clientWidth; <-- this is 0
      canvas.height = 340;//canvas.clientHeight; <-- this is 0

      // https://doc.babylonjs.com/divingDeeper/scene/offscreenCanvas
      offscreen = canvas.transferControlToOffscreen();

      return new RSVP.Queue()
        .push(function () {
          gadget.runGame({
            logic_url_list: logic_file_list,
            canvas: offscreen,
            canvas_original: canvas,
            width: canvas.width,
            height: canvas.height
          });

          return gadget.updateHeader({
            page_title: 'BabylonJS Canvas In Web Worker',
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      var gadget = this,
        game_manager = new DroneGameManager();
      return game_manager.play(options);
    });

}(window, rJS, domsugar, DroneGameManager));