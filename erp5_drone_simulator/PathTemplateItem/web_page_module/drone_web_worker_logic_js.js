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


  runGame = function (canvas, script, map, log) {
    console.log('runGame', canvas);
    
    //ROMAIN
    /*// Create the Babylon engine
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
    scene.render();*/
    
    
    //ROQUE
    var GAMEPARAMETERS = {};
    Object.assign(GAMEPARAMETERS, map);
    var _ground_truth_target, _scene, _engine;
    function randomSpherePoint(x0, y0, z0, rx0, ry0, rz0) {
      var u = Math.random(), v = Math.random(), rx = Math.random() * rx0, ry = Math.random() * ry0, rz = Math.random() * rz0, theta = 2 * Math.PI * u, phi = Math.acos(2 * v - 1), x = x0 + (rx * Math.sin(phi) * Math.cos(theta)), y = y0 + (ry * Math.sin(phi) * Math.sin(theta)), z = z0 + (rz * Math.cos(phi));
      return new BABYLON.Vector3(x, y, z);
    }
    var _this = this,
      center = GAMEPARAMETERS.randomSpawn.rightTeam.position,
      dispertion = GAMEPARAMETERS.randomSpawn.rightTeam.dispertion;
    if (GAMEPARAMETERS.randomSpawn.rightTeam.dispersed)
      dispertion = {x: 0, y: 0, z: 0};
    _ground_truth_target = randomSpherePoint(center.x, center.y, center.z, dispertion.x, dispertion.y, dispertion.z);
    if (_scene) {
      _scene.dispose();
    }
    // Create the Babylon engine
    _engine = new BABYLON.Engine(canvas, true);
    _engine.enableOfflineSupport = false;
    // Create the base scene
    _scene = new BABYLON.Scene(_engine);
    _scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
    // Collisions
    _scene.collisionsEnabled = true;
    // Lights
    var hemi_north = new BABYLON.HemisphericLight("hemiN", new BABYLON.Vector3(1, -1, 1), _scene);
    hemi_north.intensity = .75;
    var hemi_south = new BABYLON.HemisphericLight("hemiS", new BABYLON.Vector3(-1, 1, -1), _scene);
    hemi_south.intensity = .75;
    var radius = (GAMEPARAMETERS.mapSize.width/3 < 75) ? 75 : GAMEPARAMETERS.mapSize.width/3,
      vector_x = (_ground_truth_target.x > -50 && _ground_truth_target.x < 50) ? 0 : _ground_truth_target.x,
      vector_y = (_ground_truth_target.y > -50 && _ground_truth_target.y < 50) ? 0 : _ground_truth_target.y,
      camera, x_rotation;
    if (_ground_truth_target.x > 0 && _ground_truth_target.y > 0) {
      x_rotation = 1;
    } else if (_ground_truth_target.x > 0 && _ground_truth_target.y < 0) {
      x_rotation = 200;
    } else if (_ground_truth_target.x < 0 && _ground_truth_target.y < 0) {
      x_rotation = 400;
    } else {
      x_rotation = 750;
    }
    //cap camera distance to 1km
    if (radius > 800) radius = 800;
    var target = new BABYLON.Vector3(vector_x, 0, vector_y);
    if (GAMEPARAMETERS.compareFlights) {
      target = BABYLON.Vector3.Zero();
    }
    camera = new BABYLON.ArcRotateCamera("camera", x_rotation, 1.25, radius, target, _scene);
    camera.wheelPrecision = 10;
    camera.attachControl(_scene.getEngine().getRenderingCanvas());
    camera.maxz = 40000
    // Render loop
    _engine.runRenderLoop(function () {
        _scene.render();
    });
  };

/*
        // Resize canvas on window resize
        window.addEventListener('resize', function () {
          engine.resize();
        });
*/
}(this));