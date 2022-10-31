/*global window, rJS, domsugar, DroneGameManager*/
/*jslint nomen: true, indent: 2, maxlen: 80, white: true, evil: false */

(function (window, rJS, domsugar, DroneGameManager) {
  "use strict";

  var LOGIC_FILE_LIST = ['gadget_erp5_page_babylonjs_logic.js'],
    WIDTH = 680, HEIGHT = 340;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("translate", "translate")

    .declareMethod('render', function (options) {
      var gadget = this,
        canvas = domsugar('canvas'),
        offscreen;
      domsugar(gadget.element, [canvas]);
      canvas.width = options.width || WIDTH;
      canvas.height = options.height || HEIGHT;
      // https://doc.babylonjs.com/divingDeeper/scene/offscreenCanvas
      offscreen = canvas.transferControlToOffscreen();
      gadget.runGame({
        logic_url_list: LOGIC_FILE_LIST,
        canvas: offscreen,
        canvas_original: canvas,
        width: canvas.width,
        height: canvas.height
      });
      return gadget.translate('BabylonJS Canvas In Web Worker')
        .push(function (translated) {
          return gadget.updateHeader({
            page_title: translated,
            page_icon: 'puzzle-piece'
          });
        });
    })

    .declareJob('runGame', function runGame(options) {
      var game_manager = new DroneGameManager();
      return game_manager.play(options);
    });

}(window, rJS, domsugar, DroneGameManager));