var GAMEPARAMETERS = {};

var GameManager = /** @class */ (function () {
  // *** CONSTRUCTOR ***
  function GameManager(canvas, script, map, simulation_speed) {
    var _this = this;
    this._canvas = canvas;
    this._scene = null;
    this._ground_truth_target = null;
    this._engine = null;
    this._teamLeft = [];
    this._teamRight = [];
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
    this._scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
    this._scene.collisionsEnabled = true;
    // Lights
    var hemi_north = new BABYLON.HemisphericLight(
      "hemiN", new BABYLON.Vector3(1, -1, 1), this._scene);
    hemi_north.intensity = 0.75;
    var hemi_south = new BABYLON.HemisphericLight(
      "hemiS", new BABYLON.Vector3(-1, 1, -1), this._scene);
    hemi_south.intensity = 0.75;
    var radius = (GAMEPARAMETERS.mapSize.width/3 < 75) ?
        75 : GAMEPARAMETERS.mapSize.width/3,
      vector_x = (this._ground_truth_target.x > -50 &&
                  this._ground_truth_target.x < 50) ?
        0 : this._ground_truth_target.x,
      vector_y = (this._ground_truth_target.y > -50 &&
                  this._ground_truth_target.y < 50) ?
        0 : this._ground_truth_target.y,
      camera, x_rotation;
    if (this._ground_truth_target.x > 0 && this._ground_truth_target.y > 0) {
      x_rotation = 1;
    } else if (this._ground_truth_target.x > 0 &&
               this._ground_truth_target.y < 0) {
      x_rotation = 200;
    } else if (this._ground_truth_target.x < 0 &&
               this._ground_truth_target.y < 0) {
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
    camera = new BABYLON.ArcRotateCamera("camera", x_rotation, 1.25, radius,
                                         target, this._scene);
    camera.wheelPrecision = 10;
    camera.attachControl(this._scene.getEngine().getRenderingCanvas());
    camera.maxz = 40000;
    // Render loop
    //this._engine.runRenderLoop(function () {
    _this._scene.render();
    //});
    _this._load3DModel(_this._on3DmodelsReady);
  };

  GameManager.prototype._load3DModel = function (callback) {
    var _this = this, droneTask, mapTask, obstacleTask,
      assetManager = new BABYLON.AssetsManager(this._scene);
    assetManager.useDefaultLoadingScreen = true;
    // DRONE
    droneTask = assetManager.addMeshTask("loadingDrone", "", "assets/drone/", "drone.babylon");
    droneTask.onSuccess = function (task) {
        task.loadedMeshes.forEach(function (mesh) {
            mesh.isPickable = false;
            mesh.isVisible = false;
        });
        DroneManager.Prefab = _this._scene.getMeshByName("Dummy_Drone");
        DroneManager.Prefab.scaling = new BABYLON.Vector3(0.006, 0.006, 0.006);
        DroneManager.Prefab.position = new BABYLON.Vector3(0, -5, 0);
    };
    droneTask.onError = function () {
        console.log("Error loading 3D model for Drone");
    };
    // MAP
    mapTask = assetManager.addMeshTask("loadingMap", "", "assets/map/", "map.babylon");
    mapTask.onSuccess = function (task) {
        task.loadedMeshes.forEach(function (mesh) {
            mesh.isPickable = false;
            mesh.isVisible = false;
        });
    };
    mapTask.onError = function () {
        console.log("Error loading 3D model for Map");
    };
    // OBSTACLE
    obstacleTask = assetManager.addMeshTask("loadingObstacle", "", "assets/obstacle/", "boat.babylon");
    obstacleTask.onSuccess = function (task) {
        task.loadedMeshes.forEach(function (mesh) {
            mesh.isPickable = false;
            mesh.isVisible = false;
        });
        ObstacleManager.Prefab = _this._scene.getMeshByName("car");
    };
    obstacleTask.onError = function () {
        console.log("Error loading 3D model for Obstacle");
    };
    assetManager.onFinish = function () {
      return callback(_this); //on3DmodelsReady(_this);
    };
    assetManager.load();
  };

  GameManager.prototype._on3DmodelsReady = function (ctx) {
    console.log("_on3DmodelsReady called as callback");
    // Get the game parameters //TODO
    /*if (!ctx._map_swapped) {
      GAMEPARAMETERS = ctx._getGameParameter();
      ctx._map_swapped = true;
    }*/
    // Create the API
    var lAPI = new DroneAPI(ctx, "L");
    var rAPI = new DroneAPI(ctx, "R");
    // Set the AI code into drones
    var AIcodeEval, AIcodeRight, AIcodeLeft;
    AIcodeLeft = ctx._script;
    //set AI for the target (derive or do nothing)
    if (GAMEPARAMETERS.derive) {
      AIcodeRight = `me.onStart = function() { me.setHumanAcceleration(99999); me.setDirection(${GAMEPARAMETERS.derive.direction.x},${GAMEPARAMETERS.derive.direction.y},0); }`;
    } else {
      AIcodeRight = "me.onStart = function() { me.setAcceleration(0); me.setDirection(0,0,0); }";
    }
    // Init the map
    //_this._mapManager = new MapManager(ctx._scene);
    ctx._mapManager = new MapManager(ctx._scene);
    // If positions are defined in GameParameter
    /*if (GAMEPARAMETERS.randomSpawn) {
        //TODO _setRandomSpawnPosition
        ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.leftTeam, GAMEPARAMETERS.teamSize, lAPI, AIcodeLeft, "L");
        ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.rightTeam, GAMEPARAMETERS.teamSize, rAPI, AIcodeRight, "R");
    }*/
    // Hide the drone prefab
    DroneManager.Prefab.isVisible = false;
    //GUI for drones ID display
    //TODO
    console.log("onload3dmodel drones advancedTexture skipped");
    return ctx;
    var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
    for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
      if (ctx._teamLeft[count]) {
        var controlMeshBlue = ctx._teamLeft[count].infosMesh;
        //set only one drone for right team (the target)
        if (count === 0) {
            var controlMeshRed = ctx._teamRight[count].infosMesh;
            var ellipse = new BABYLON.GUI.Ellipse();
            ellipse.height = "10px";
            ellipse.width = "15px";
            ellipse.thickness = 4;
            ellipse.color = "red";
            ellipse.linkOffsetY = 0;
            advancedTexture.addControl(ellipse);
            ellipse.linkWithMesh(controlMeshRed);
        }
        var rectBlue = new BABYLON.GUI.Rectangle();
        if (count < 100)
            rectBlue.width = "10px";
        else
            rectBlue.width = "14px";
        rectBlue.height = "10px";
        rectBlue.cornerRadius = 20;
        rectBlue.color = "white";
        rectBlue.thickness = 0.5;
        rectBlue.background = "blue";
        advancedTexture.addControl(rectBlue);
        var labelBlue = new BABYLON.GUI.TextBlock();
        labelBlue.text = count.toString();
        labelBlue.fontSize = 7;
        rectBlue.addControl(labelBlue);
        rectBlue.linkWithMesh(controlMeshBlue);
        rectBlue.linkOffsetY = 0;
      }
    }
    console.log("onload3dmodel finished");
    return ctx;
  };

  return GameManager;
}());
