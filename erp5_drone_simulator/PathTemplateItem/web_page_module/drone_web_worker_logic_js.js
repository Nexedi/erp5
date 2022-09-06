/*global window, rJS, jIO, RSVP, domsugar, console,
         requestAnimationFrame, cancelAnimationFrame,
         Worker,
         DroneGameManager*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

var runGame;
// game.js
(function () {
  "use strict";
  console.log('game logic');


  runGame = function (canvas) {

    console.log('runGame', canvas);
    // Create the Babylon engine
    var engine = new BABYLON.Engine(canvas, true);
    engine.enableOfflineSupport = false;
    // Create the base scene
    var scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
      // this._scene.debugLayer.show();
      // Collisions
    scene.collisionsEnabled = true;

        // Camera
  //cap camera distance to 1km
    var camera = new BABYLON.ArcRotateCamera("camera", 3, 1.25, 800, new BABYLON.Vector3(1, 0, 1), scene);
    camera.wheelPrecision = 10;
    //camera.attachControl(scene.getEngine().getRenderingCanvas());
    camera.maxz = 40000

    scene.render();
  };

/*
        // Resize canvas on window resize
        window.addEventListener('resize', function () {
          engine.resize();
        });
*/
}(this));