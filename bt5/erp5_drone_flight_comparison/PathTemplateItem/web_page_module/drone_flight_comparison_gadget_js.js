
//TODO move this full JS to MAIN

(function (window, rJS, domsugar, DroneGameManager, document, Blob) {
  "use strict";

  var canvas, offscreen;
  var LOGIC_FILE_LIST = [
    'gadget_erp5_page_drone_simulator_logic_comparison.js',
    'gadget_erp5_page_flight_comparison_droneaaailefixe.js',
    'gadget_erp5_page_flight_comparison_dronelogfollower.js'
  ];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    // for standaloneDemo
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")
    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function render() {
      var gadget = this,
        container = domsugar('div');
      canvas = domsugar('canvas');
      container.className = 'container';
      container.appendChild(canvas);
      domsugar(gadget.element, [container]);
      //TODO fix hardcoded
      canvas.width = 680;//canvas.clientWidth; <-- this is 0
      canvas.height = 340;//canvas.clientHeight; <-- this is 0
      // https://doc.babylonjs.com/divingDeeper/scene/offscreenCanvas
      offscreen = canvas.transferControlToOffscreen();
    })

    // To be called outside
    .declareMethod('runGame', function runGame(options) {
      options.canvas = offscreen;
      options.canvas_original = canvas;
      options.width = canvas.width;
      options.height = canvas.height;
      options.logic_url_list = LOGIC_FILE_LIST;
      var gadget = this,
        game_manager = new DroneGameManager();
      return game_manager.play(options)
      .push(function () {
        return game_manager.result();
      });
    });

}(window, rJS, domsugar, DroneGameManager, document, Blob));