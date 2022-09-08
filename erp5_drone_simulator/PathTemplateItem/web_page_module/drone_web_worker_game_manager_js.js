var GAMEPARAMETERS = {};

var GameManager = /** @class */ (function () {
  // *** CONSTRUCTOR ***
  function GameManager(canvas, script, map, simulation_speed) {
    var _this = this;
    this._canvas = canvas;
    this._scene = null;
    this._ground_truth_target = null;
    this._engine = null;
    Object.assign(GAMEPARAMETERS, map);
  }

  GameManager.prototype.run = function () {
    var gadget = this;
    return gadget._init();
  };

  GameManager.prototype._dispose = function () {
    if (this._scene) {
      this._scene.dispose();
    }
  };

  GameManager.prototype._init = function () {
    function randomSpherePoint(x0, y0, z0, rx0, ry0, rz0) {
      var u = Math.random(), v = Math.random(),
        rx = Math.random() * rx0, ry = Math.random() * ry0,
        rz = Math.random() * rz0, theta = 2 * Math.PI * u,
        phi = Math.acos(2 * v - 1),
        x = x0 + (rx * Math.sin(phi) * Math.cos(theta)),
        y = y0 + (ry * Math.sin(phi) * Math.sin(theta)),
        z = z0 + (rz * Math.cos(phi));
      return new BABYLON.Vector3(x, y, z);
    }
    var _this = this,
      center = GAMEPARAMETERS.randomSpawn.rightTeam.position,
      dispertion = GAMEPARAMETERS.randomSpawn.rightTeam.dispertion;
    if (GAMEPARAMETERS.randomSpawn.rightTeam.dispersed)
      dispertion = {x: 0, y: 0, z: 0};
    this._ground_truth_target =
      randomSpherePoint(center.x, center.y, center.z,
                        dispertion.x, dispertion.y, dispertion.z);
    this._dispose();
    var canvas = this._canvas;
    // Create the Babylon engine
    this._engine = new BABYLON.Engine(canvas, true);
    this._engine.enableOfflineSupport = false;
    this._scene = new BABYLON.Scene(this._engine);
    _scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
    this._scene.collisionsEnabled = true;
    // Lights
    var hemi_north = new BABYLON.HemisphericLight("hemiN", new BABYLON.Vector3(1, -1, 1), this._scene);
    hemi_north.intensity = 0.75;
    var hemi_south = new BABYLON.HemisphericLight("hemiS", new BABYLON.Vector3(-1, 1, -1), this._scene);
    hemi_south.intensity = 0.75;
    var radius = (GAMEPARAMETERS.mapSize.width/3 < 75) ? 75 : GAMEPARAMETERS.mapSize.width/3,
      vector_x = (this._ground_truth_target.x > -50 && this._ground_truth_target.x < 50) ? 0 : this._ground_truth_target.x,
      vector_y = (this._ground_truth_target.y > -50 && this._ground_truth_target.y < 50) ? 0 : this._ground_truth_target.y,
      camera, x_rotation;
    if (this._ground_truth_target.x > 0 && this._ground_truth_target.y > 0) {
      x_rotation = 1;
    } else if (this._ground_truth_target.x > 0 && this._ground_truth_target.y < 0) {
      x_rotation = 200;
    } else if (this._ground_truth_target.x < 0 && this._ground_truth_target.y < 0) {
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
    camera = new BABYLON.ArcRotateCamera("camera", x_rotation, 1.25, radius, target, this._scene);
    camera.wheelPrecision = 10;
    camera.attachControl(this._scene.getEngine().getRenderingCanvas());
    camera.maxz = 40000;
    // Render loop
    //this._engine.runRenderLoop(function () {
    _this._scene.render();
    //});
  };
  return GameManager;
}());
