/*global window, rJS, RSVP, BABYLON, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

var runGame, updateGame;

(function () {
  "use strict";

  runGame = function (canvas) {

    console.log('runGame', canvas);

    var finish_deferred = RSVP.defer(), engine, scene, camera, light, sphere;

    // Create the Babylon engine
    engine = new BABYLON.Engine(canvas, true);
    engine.enableOfflineSupport = false;
    // Create the base scene
    scene = new BABYLON.Scene(engine);
    scene.clearColor = new BABYLON.Color4(88 / 255, 171 / 255, 217 / 255, 1);
    // Camera
    camera = new BABYLON.ArcRotateCamera("camera1", 400, 1.25, 10,
                                         new BABYLON.Vector3(0, 5, -10), scene);
    camera.setTarget(BABYLON.Vector3.Zero());
    camera.wheelPrecision = 10;
    camera.maxz = 40000;
    camera.attachControl(canvas, true);
    // Light
    light = new BABYLON.HemisphericLight("light",
                                               new BABYLON.Vector3(0, 1, 0),
                                               scene);
    light.intensity = 0.7;
    // Some objects (sphere and plane)
    sphere = BABYLON.MeshBuilder.CreateSphere("sphere",
                                                    {diameter: 2, segments: 32},
                                                    scene);
    sphere.position.y = 1;
    BABYLON.MeshBuilder.CreateGround("ground", {width: 6, height: 6}, scene);

    engine.runRenderLoop(function () { scene.render(); });

    return finish_deferred.promise;
  };

  updateGame = function () {
    console.log("updateGame loop");
  };

}(this));
