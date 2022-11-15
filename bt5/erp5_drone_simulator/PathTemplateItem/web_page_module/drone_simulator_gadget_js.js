(function (window, rJS, domsugar, DroneGameManager, document, Blob) {
  "use strict";

  var canvas, offscreen,
    WIDTH = 680, HEIGHT = 340,
    LOGIC_FILE_LIST = [
    'gadget_erp5_page_drone_simulator_logic.js',
    'gadget_erp5_page_drone_simulator_droneaaailefixe.js',
    'gadget_erp5_page_drone_simulator_dronelogfollower.js'
  ];

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////

    .declareAcquiredMethod("jio_allDocs", "jio_allDocs")

    .declareMethod('render', function render(options) {
      var gadget = this,
        loading = domsugar('span', ["Loading..."]),
        container = domsugar('div');
      canvas = domsugar('canvas');
      loading.id = "loading";
      container.className = 'container';
      container.appendChild(canvas);
      domsugar(gadget.element, [loading, container]);
      canvas.width = WIDTH;
      canvas.height = HEIGHT;
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
        game_manager = new DroneGameManager(gadget);
      return game_manager.play(options)
      .push(function () {
        return game_manager.result();
      });
    });

}(window, rJS, domsugar, DroneGameManager, document, Blob));