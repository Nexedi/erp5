/*global BABYLON, RSVP, console, FixedWingDroneAPI, EnemyDroneAPI, document, MapUtils*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true,
         unparam: true */

var GAMEPARAMETERS = {}, TEAM_USER = "user", TEAM_ENEMY = "enemy";
//for DEBUG/TEST mode
var baseLogFunction = console.log, console_log = "";

/******************************* DRONE MANAGER ********************************/
var DroneManager = /** @class */ (function () {
  "use strict";

  //** CONSTRUCTOR
  function DroneManager(scene, id, API, team) {
    this._mesh = null;
    this._controlMesh = null;
    this._canPlay = false;
    this._canCommunicate = false;
    this._maxDeceleration = 0;
    this._maxAcceleration = 0;
    this._minSpeed = 0;
    this._maxSpeed = 0;
    this._minPitchAngle = 0;
    this._maxPitchAngle = 0;
    this._maxRollAngle = 0;
    this._maxSinkRate = 0;
    this._maxClimbRate = 0;
    this._maxCommandFrequency = 0;
    this._last_command_timestamp = 0;
    this._speed = 0;
    this._acceleration = 0;
    this._direction = new BABYLON.Vector3(0, 0, 1); // North
    this._scene = scene;
    this._canUpdate = true;
    this._id = id;
    this._team = team;
    this._API = API; // var API created on AI evel
    this._score = 0;
    // Create the control mesh
    this._controlMesh = BABYLON.Mesh.CreateBox(
      "droneControl_" + id,
      0.01,
      this._scene
    );
    this._controlMesh.isVisible = false;
    this._controlMesh.computeWorldMatrix(true);
    // Create the mesh from the drone prefab
    this._mesh = DroneManager.Prefab.clone("drone_" + id, this._controlMesh);
    this._mesh.position = BABYLON.Vector3.Zero();
    this._mesh.isVisible = false;
    this._mesh.computeWorldMatrix(true);
    // Get the back collider
    this._mesh.getChildMeshes().forEach(function (mesh) {
      mesh.isVisible = true;
    });
    if (!DroneManager.PrefabBlueMat) {
      DroneManager.PrefabBlueMat =
        new BABYLON.StandardMaterial("blueTeamMat", scene);
      DroneManager.PrefabBlueMat.diffuseTexture =
        new BABYLON.Texture("assets/drone/drone_bleu.jpg", scene);
    }
  }
  DroneManager.prototype._swapAxe = function (vector) {
    // swap y and z axis so z axis represents altitude
    return new BABYLON.Vector3(vector.x, vector.z, vector.y);
  };
  Object.defineProperty(DroneManager.prototype, "can_play", {
    get: function () { return this._canPlay; },
    set: function (value) { this._canPlay = value; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "id", {
    get: function () { return this._id; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "score", {
    get: function () { return this._score; },
    set: function (value) { this._score = value; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "team", {
    get: function () { return this._team; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "colliderMesh", {
    get: function () { return this._mesh; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "infosMesh", {
    get: function () { return this._controlMesh; },
    enumerable: true,
    configurable: true
  });
  // swap y and z axis so z axis represents altitude
  Object.defineProperty(DroneManager.prototype, "position", {
    get: function () {
      if (this._controlMesh !== null) {
        return this._swapAxe(this._controlMesh.position);
      }
      return null;
    },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "speed", {
    get: function () { return this._speed; },
    enumerable: true,
    configurable: true
  });
  // swap y and z axis so z axis represents altitude
  Object.defineProperty(DroneManager.prototype, "direction", {
    get: function () { return this._swapAxe(this._direction); },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "worldDirection", {
    get: function () {
      return new BABYLON.Vector3(
        this._direction.x,
        this._direction.y,
        this._direction.z
      );
    },
    enumerable: true,
    configurable: true
  });
  DroneManager.prototype.internal_start = function () {
    this._targetCoordinates = this.position;
    this._API.internal_start(this);
    this._canPlay = true;
    this._canCommunicate = true;
    try {
      return this.onStart(this._API._gameManager._game_duration);
    } catch (error) {
      console.warn('Drone crashed on start due to error:', error);
      this._internal_crash(error);
    }
  };
  /**
   * Set a target point to move
   */
  DroneManager.prototype.setTargetCoordinates =
    function (latitude, longitude, altitude, speed) {
      this._internal_setTargetCoordinates(latitude, longitude, altitude, speed);
    };
  DroneManager.prototype._internal_setTargetCoordinates =
    function (latitude, longitude, altitude, speed, radius) {
      if (!this._canPlay || !this.isReadyToFly()) {
        return;
      }
      if (this._API._gameManager._game_duration - this._last_command_timestamp
            < 1000 / this._API.getMaxCommandFrequency()) {
        this._internal_crash(new Error('Minimum interval between commands is ' +
            1000 / this._API.getMaxCommandFrequency() + ' milliseconds'));
      }
      //each drone API process coordinates on its needs
      //e.g. fixedwing drone converts real geo-coordinates to virtual x-y
      this._targetCoordinates =
        this._API.processCoordinates(latitude, longitude, altitude);
      this._API.internal_setTargetCoordinates(
        this,
        this._targetCoordinates,
        speed,
        radius
      );
      this._last_command_timestamp = this._API._gameManager._game_duration;
    };
  DroneManager.prototype.getDroneDict = function () {
    return this._API._drone_dict_list;
  };
  /**
   * Returns the list of things a drone "sees"
   */
  DroneManager.prototype.getDroneViewInfo = function () {
    var context = this;
    if (this._controlMesh) {
      return context._API.getDroneViewInfo(context);
    }
    return;
  };
  DroneManager.prototype.internal_update = function (delta_time) {
    var context = this, milliseconds;
    if (this._controlMesh) {
      context._API.internal_update(context, delta_time);
      if (context._canUpdate) {
        context._canUpdate = false;
        return new RSVP.Queue()
          .push(function () {
            milliseconds = Math.floor(context._API._gameManager._game_duration);
            return context.onUpdate(milliseconds);
          })
          .push(function () {
            context._canUpdate = true;
          }, function (error) {
            console.warn('Drone crashed on update due to error:', error);
            context._internal_crash(error);
          })
          .push(function () {
            context._API.internal_post_update(context);
          })
          .push(undefined, function (error) {
            console.warn('Drone crashed on update due to error:', error);
            context._internal_crash(error);
          });
      }
      return;
    }
    return;
  };
  DroneManager.prototype._internal_crash = function (error, print_stack) {
    if (print_stack === "undefined") { print_stack = true; }
    this.last_position = this.position;
    this._canCommunicate = false;
    this._controlMesh = null;
    this._mesh = null;
    this._canPlay = false;
    if (error) {
      this._API._gameManager.logError(this, error, print_stack);
    }
    this.onTouched();
  };
  DroneManager.prototype.setStartingPosition = function (x, y, z) {
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
      throw new Error('Position coordinates must be numbers');
    }
    return this._API.setStartingPosition(this, x, y, z);
  };
  DroneManager.prototype.setDirection = function (x, y, z) {
    if (!this._canPlay) {
      return;
    }
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
      throw new Error('Direction coordinates must be numbers');
    }
    // swap y and z axis so z axis represents altitude
    this._direction = new BABYLON.Vector3(x, z, y).normalize();
  };

  /**
   * Send a message to drones
   * @param msg The message to send
   * @param id The targeted drone. -1 or nothing to broadcast
   */
  DroneManager.prototype.sendMsg = function (msg, id) {
    var _this = this;
    if (!this._canCommunicate) {
      return;
    }
    if (!id || id < 0) {
      id = -1;
    }
    if (_this.infosMesh) {
      return _this._API.sendMsg(JSON.parse(JSON.stringify(msg)), id);
    }
  };
  /**
   * Handle internal get msg
   * @param msg The message to send
   * @param id of the sender
   */
  DroneManager.prototype.internal_getMsg = function (msg, id) {
    return this._API.internal_getMsg(msg, id);
  };
  /** Perform a console.log with drone id + the message */
  DroneManager.prototype.log = function (msg) { return msg; };
  DroneManager.prototype.getMaxHeight = function () {
    return this._API.getMaxHeight();
  };
  DroneManager.prototype.getMinHeight = function () {
    return this._API.getMinHeight();
  };
  DroneManager.prototype.getInitialAltitude = function () {
    return this._API.getInitialAltitude();
  };
  DroneManager.prototype.getCollisionSector = function () {
    return this._API.getCollisionSector();
  };
  DroneManager.prototype.getAltitudeAbs = function () {
    if (this._controlMesh) {
      var altitude = this._controlMesh.position.y;
      return this._API.getAltitudeAbs(altitude);
    }
    return null;
  };
  /**
   * Get a game parameter by name
   * @param name Name of the parameter to retrieve
   */
  DroneManager.prototype.getGameParameter = function (name) {
    if (!this._canCommunicate) {
      return;
    }
    return this._API.getGameParameter(name);
  };
  DroneManager.prototype.getCurrentPosition = function () {
    if (this._controlMesh) {
      // swap y and z axis so z axis represents altitude
      var position = this._API.getCurrentPosition(
        this._controlMesh.position.x,
        this._controlMesh.position.z,
        this._controlMesh.position.y
      );
      position.timestamp = this._API._gameManager._game_duration;
      //Backward compatibility sanitation
      position.x = position.latitude;
      position.y = position.longitude;
      position.z = position.altitude;
      return position;
    }
    return null;
  };
  /**
   * Make the drone loiter (circle with a set radius)
   */
  DroneManager.prototype.loiter =
    function (latitude, longitude, altitude, radius, speed) {
      this._internal_setTargetCoordinates(
        latitude,
        longitude,
        altitude,
        speed,
        radius
      );
    };
  DroneManager.prototype.getFlightParameters = function () {
    if (this._API.getFlightParameters) {
      return this._API.getFlightParameters();
    }
    return null;
  };
  DroneManager.prototype.getYaw = function () {
    if (this._API.getYaw !== undefined) {
      return this._API.getYaw(this);
    }
    return;
  };
  DroneManager.prototype.get3DSpeed = function () {
    return this._speed;
  };
  DroneManager.prototype.getSpeed = function () {
    if (this._API.getSpeed !== "undefined") {
      return this._API.getSpeed(this);
    }
    return;
  };
  DroneManager.prototype.getClimbRate = function () {
    if (this._API.getClimbRate !== "undefined") {
      return this._API.getClimbRate(this);
    }
    return;
  };
  DroneManager.prototype.takeOff = function () {
    return this._API.takeOff();
  };
  DroneManager.prototype.land = function () {
    return this._API.land(this);
  };
  DroneManager.prototype.exit = function () {
    return this._internal_crash();
  };
  DroneManager.prototype.isReadyToFly = function () {
    return this._API.isReadyToFly();
  };
  DroneManager.prototype.isLanding = function () {
    return this._API.isLanding();
  };
  /**
   * Set the drone last checkpoint reached
   * @param checkpoint to be set
   */
  DroneManager.prototype.setCheckpoint = function (checkpoint) {
    //TODO
    return checkpoint;
  };
  /**
   * Function called on game start
   */
  DroneManager.prototype.onStart = function (timestamp) { return; };
  /**
   * Function called on game update
   * @param timestamp The tic value
   */
  DroneManager.prototype.onUpdate = function (timestamp) { return; };
  /**
   * Function called when drone crashes
   */
  DroneManager.prototype.onTouched = function () { return; };
  /**
   * Function called when a message is received
   * @param msg The message
   */
  DroneManager.prototype.onGetMsg = function () { return; };
  /**
   * Function called when drone finished processing drone view
   * (as result of getDroneViewInfo call)
   */
  DroneManager.prototype.onDroneViewInfo = function (drone_view) { return; };

  return DroneManager;
}());

/******************************************************************************/


/******************************** MAP MANAGER *********************************/

var MapManager = /** @class */ (function () {
  "use strict";
  var SEED = '6!',
    //default square map
    MAP_HEIGHT = 700,
    START_AMSL = 595,
    MIN_LAT = 45.6419,
    MAX_LAT = 45.65,
    MIN_LON = 14.265,
    MAX_LON = 14.2766,
    MAP = {
      "height": MAP_HEIGHT,
      "start_AMSL": START_AMSL,
      "map_seed": SEED,
      "min_lat": MIN_LAT,
      "max_lat": MAX_LAT,
      "min_lon": MIN_LON,
      "max_lon": MAX_LON
    };

  //** CONSTRUCTOR
  function MapManager(scene, map_param) {
    var _this = this, max_sky, skybox, skyboxMat, largeGroundMat, flag_material,
      largeGroundBottom, width, depth, terrain, max, flag_a, flag_b, mast, flag,
      count = 0, new_obstacle, obstacle, flag_info, enemy,
      FLAG_SIZE = {
        'x': 1,
        'y': 1,
        'z': 6
      };
    if (!map_param) {
      // Use default map base parameters
      map_param = MAP;
    }
    _this.mapUtils = new MapUtils(map_param);
    _this.map_info = map_param;
    Object.assign(_this.map_info, _this.mapUtils.map_info);
    _this.map_info.initial_position = _this.mapUtils.convertToLocalCoordinates(
      _this.map_info.initial_position.latitude,
      _this.map_info.initial_position.longitude,
      _this.map_info.initial_position.altitude
    );
    max = _this.map_info.width;
    if (_this.map_info.depth > max) {
      max = _this.map_info.depth;
    }
    if (_this.map_info.height > max) {
      max = _this.map_info.height;
    }
    max = max < _this.map_info.depth ? _this.map_info.depth : max;
    // Skybox
    max_sky =  (max * 15 < 20000) ? max * 15 : 20000; //skybox scene limit
    skybox = BABYLON.MeshBuilder.CreateBox("skyBox", { size: max_sky }, scene);
    skyboxMat = new BABYLON.StandardMaterial("skybox", scene);
    skyboxMat.backFaceCulling = false;
    skyboxMat.disableLighting = true;
    skybox.material = skyboxMat;
    skybox.infiniteDistance = true;
    skyboxMat.disableLighting = true;
    skyboxMat.reflectionTexture = new BABYLON.CubeTexture("./assets/skybox/sky",
                                                          scene);
    skyboxMat.reflectionTexture.coordinatesMode = BABYLON.Texture.SKYBOX_MODE;
    skybox.renderingGroupId = 0;
    // Plane from bottom
    largeGroundMat = new BABYLON.StandardMaterial("largeGroundMat", scene);
    largeGroundMat.specularColor = BABYLON.Color3.Black();
    largeGroundMat.alpha = 0.4;
    largeGroundBottom = BABYLON.Mesh.CreatePlane("largeGroundBottom",
                                                 max * 11, scene);
    largeGroundBottom.position.y = -0.01;
    largeGroundBottom.rotation.x = -Math.PI / 2;
    largeGroundBottom.rotation.y = Math.PI;
    largeGroundBottom.material = largeGroundMat;
    largeGroundBottom.renderingGroupId = 1;
    // Terrain
    // Give map some margin from the flight limits
    width = _this.map_info.width * 1.10;
    depth = _this.map_info.depth * 1.10;
    //height = _this.map_info.height;
    terrain = scene.getMeshByName("terrain001");
    terrain.isVisible = true;
    terrain.position = BABYLON.Vector3.Zero();
    terrain.scaling = new BABYLON.Vector3(depth / 50000, depth / 50000,
                                          width / 50000);
    // Enemies
    _this._enemy_list = [];
    _this.map_info.enemy_list.forEach(function (geo_enemy) {
      enemy = {};
      Object.assign(enemy, geo_enemy);
      enemy.position = _this.mapUtils.convertToLocalCoordinates(
        geo_enemy.position.latitude,
        geo_enemy.position.longitude,
        geo_enemy.position.altitude
      );
      _this._enemy_list.push(enemy);
    });
    // Obstacles
    _this._obstacle_list = [];
    _this.map_info.obstacle_list.forEach(function (geo_obstacle) {
      obstacle = {};
      Object.assign(obstacle, geo_obstacle);
      obstacle.position = _this.mapUtils.convertToLocalCoordinates(
        geo_obstacle.position.latitude,
        geo_obstacle.position.longitude,
        geo_obstacle.position.altitude
      );
      switch (obstacle.type) {
      case "box":
        new_obstacle = BABYLON.MeshBuilder.CreateBox("obs_" + count,
                                                     { 'size': 1 }, scene);
        break;
      case "cylinder":
        new_obstacle = BABYLON.MeshBuilder.CreateCylinder("obs_" + count, {
          'diameterBottom': obstacle.diameterBottom,
          'diameterTop': obstacle.diameterTop,
          'height': 1
        }, scene);
        break;
      case "sphere":
        new_obstacle = BABYLON.MeshBuilder.CreateSphere("obs_" + count, {
          'diameterX': obstacle.scale.x,
          'diameterY': obstacle.scale.z,
          'diameterZ': obstacle.scale.y
        }, scene);
        break;
      default:
        return;
      }
      new_obstacle.type = obstacle.type;
      var convertion = Math.PI / 180,
        obs_material = new BABYLON.StandardMaterial("obsmat_" + count, scene);
      if (obstacle.hasOwnProperty("position")) {
        new_obstacle.position = new BABYLON.Vector3(obstacle.position.x,
                                                    obstacle.position.z,
                                                    obstacle.position.y);
      }
      if (obstacle.hasOwnProperty("rotation")) {
        new_obstacle.rotation =
          new BABYLON.Vector3(obstacle.rotation.x * convertion,
                              obstacle.rotation.z * convertion,
                              obstacle.rotation.y * convertion);
      }
      if (obstacle.hasOwnProperty("scale")) {
        new_obstacle.scaling = new BABYLON.Vector3(obstacle.scale.x,
                                                   obstacle.scale.z,
                                                   obstacle.scale.y);
      }

      obs_material.alpha = 1;
      obs_material.diffuseColor = new BABYLON.Color3(255, 153, 0);
      new_obstacle.material = obs_material;
      _this._obstacle_list.push(new_obstacle);
      count += 1;
    });
    // Flags
    _this._flag_list = [];
    _this.map_info.flag_list.forEach(function (geo_flag, index) {
      flag_info = {};
      Object.assign(flag_info, geo_flag);
      flag_info.position = _this.mapUtils.convertToLocalCoordinates(
        geo_flag.position.latitude,
        geo_flag.position.longitude,
        geo_flag.position.altitude
      );
      flag_material = new BABYLON.StandardMaterial("flag_mat_" + index, scene);
      flag_material.alpha = 1;
      flag_material.diffuseColor = BABYLON.Color3.Green();
      flag_a = BABYLON.MeshBuilder.CreateDisc("flag_a_" + index,
                                              {radius: 7, tessellation: 3},
                                              scene);
      flag_a.material = flag_material;
      flag_a.position = new BABYLON.Vector3(
        flag_info.position.x + 1,
        flag_info.position.z + FLAG_SIZE.z + 1, //swap
        flag_info.position.y - 1
      );
      flag_a.rotation = new BABYLON.Vector3(0, 1, 0);
      flag_b = BABYLON.MeshBuilder.CreateDisc("flag_b_" + index,
                                              {radius: 3, tessellation: 3},
                                              scene);
      flag_b.material = flag_material;
      flag_b.position = new BABYLON.Vector3(
        flag_info.position.x - 1,
        flag_info.position.z + FLAG_SIZE.z + 1, //swap
        flag_info.position.y + 1
      );
      flag_b.rotation = new BABYLON.Vector3(0, 4, 0);
      mast = BABYLON.MeshBuilder.CreateBox("mast_" + index,
                                           { 'size': 1 }, scene);
      mast.position = new BABYLON.Vector3(
        flag_info.position.x,
        flag_info.position.z + FLAG_SIZE.z / 2, //swap
        flag_info.position.y
      );
      mast.scaling = new BABYLON.Vector3(
        FLAG_SIZE.x,
        FLAG_SIZE.z, //swap
        FLAG_SIZE.y
      );
      mast.material = flag_material;
      flag = BABYLON.Mesh.MergeMeshes([flag_a, flag_b, mast]);
      flag.id = index;
      flag.location = flag_info.position;
      flag.weight = flag_info.weight;
      flag.score = flag_info.score;
      flag.id = index;
      _this._flag_list.push(flag);
    });
  }
  MapManager.prototype.getMapInfo = function () {
    return this.map_info;
  };
  MapManager.prototype.latLonDistance = function (c1, c2) {
    return this.mapUtils.latLonDistance(c1, c2);
  };
  MapManager.prototype.longitudToX = function (lon) {
    return this.mapUtils.longitudToX(lon);
  };
  MapManager.prototype.latitudeToY = function (lat) {
    return this.mapUtils.latitudeToY(lat);
  };
  MapManager.prototype.convertToLocalCoordinates =
    function (latitude, longitude, altitude) {
      return this.mapUtils.convertToLocalCoordinates(
        latitude,
        longitude,
        altitude
      );
    };
  MapManager.prototype.convertToGeoCoordinates = function (x, y, z) {
    return this.mapUtils.convertToGeoCoordinates(x, y, z);
  };
  return MapManager;
}());

/******************************************************************************/



/******************************** GAME MANAGER ********************************/

var GameManager = /** @class */ (function () {
  "use strict";
  var BASE_DISTANCE = 30;
  // *** CONSTRUCTOR ***
  function GameManager(canvas, game_parameters_json) {
    var drone, header_list, drone_count, i;
    this._canvas = canvas;
    this._canvas_width = canvas.width;
    this._canvas_height = canvas.height;
    this._scene = null;
    this._engine = null;
    this._droneList = [];
    this._droneList_user = [];
    this._droneList_enemy = [];
    this._canUpdate = false;
    this._max_step_animation_frame = game_parameters_json.simulation_speed;
    if (!this._max_step_animation_frame) { this._max_step_animation_frame = 5; }
    Object.assign(GAMEPARAMETERS, game_parameters_json);
    this._game_parameters_json = game_parameters_json;
    this._map_swapped = false;
    this._log_count = [];
    this._flight_log = [];
    this._result_message = "";
    if (GAMEPARAMETERS.log_drone_flight) {
      // ! Be aware that the following functions relies on this log format:
      // - getLogEntries at Drone Simulator Log Page
      // - getLogEntries at Drone Log Follower API
      header_list = ["timestamp (ms)", "latitude (°)", "longitude (°)",
                     "AMSL (m)", "rel altitude (m)", "yaw (°)",
                     "ground speed (m/s)", "climb rate (m/s)"];
      drone_count = GAMEPARAMETERS.drone.list.length;
      for (drone = 0; drone < drone_count; drone += 1) {
        this._flight_log[drone] = [];
        this._flight_log[drone].push(header_list);
        this._log_count[drone] = 0;
      }
      if (GAMEPARAMETERS.draw_flight_path) {
        this._last_position_drawn = [];
        this._trace_objects_per_drone = [];
        for (drone = 0; drone < drone_count; drone += 1) {
          this._last_position_drawn[drone] = null;
          this._trace_objects_per_drone[drone] = [];
        }
        this._colors = [
          new BABYLON.Color3(255, 165, 0),
          new BABYLON.Color3(0, 0, 255),
          new BABYLON.Color3(255, 0, 0),
          new BABYLON.Color3(0, 255, 0),
          new BABYLON.Color3(0, 128, 128),
          new BABYLON.Color3(0, 0, 0),
          new BABYLON.Color3(255, 255, 255),
          new BABYLON.Color3(128, 128, 0),
          new BABYLON.Color3(128, 0, 128),
          new BABYLON.Color3(0, 0, 128)
        ];
      }
    }
    this.APIs_dict = {
      FixedWingDroneAPI: FixedWingDroneAPI,
      EnemyDroneAPI: EnemyDroneAPI
    };
    if (this._game_parameters_json.debug_test_mode) {
      console.log = function () {
        baseLogFunction.apply(console, arguments);
        var args = Array.prototype.slice.call(arguments);
        for (i = 0; i < args.length; i += 1) {
          console_log += args[i] + "\n";
        }
      };
    }
  }

  Object.defineProperty(GameManager.prototype, "gameParameter", {
    get: function () {
      return this._gameParameter;
    },
    enumerable: true,
    configurable: true
  });

  GameManager.prototype.run = function () {
    var gadget = this;
    return gadget._init()
      .push(function () {
        return {
          'message': gadget._result_message,
          'content': gadget._flight_log,
          'console_log': console_log
        };
      });
  };

  GameManager.prototype.update = function (fullscreen) {
    // time delta means that drone are updated every virtual second
    // This is fixed and must not be modified
    // otherwise, it will lead to different scenario results
    // (as drone calculations may be triggered less often)
    var _this = this,
      TIME_DELTA = 1000 / 60;
    // init the value on the first step
    _this.waiting_update_count = _this._max_step_animation_frame;
    function triggerUpdateIfPossible() {
      if ((_this._canUpdate) && (_this.ongoing_update_promise === null) &&
          (0 < _this.waiting_update_count)) {
        _this.ongoing_update_promise = _this._update(TIME_DELTA, fullscreen)
          .push(function () {
            _this.waiting_update_count -= 1;
            _this.ongoing_update_promise = null;
            triggerUpdateIfPossible();
          }).push(undefined, function (error) {
            console.log("ERROR on Game Manager update:", error);
            _this.finish_deferred.reject.bind(_this.finish_deferred);
          });
      }
    }
    try {
      triggerUpdateIfPossible();
    } catch (error) {
      console.log("ERROR on Game Manager update:", error);
      _this.finish_deferred.reject.bind(_this.finish_deferred);
      throw error;
    }
  };

  GameManager.prototype.delay = function (callback, millisecond) {
    this._delayed_defer_list.push([callback, millisecond]);
  };

  GameManager.prototype.logError = function (drone, error, print_stack) {
    if (drone._id < this._flight_log.length) { // don't log enemies
      this._flight_log[drone._id].push(error.message);
      if (print_stack) {
        this._flight_log[drone._id].push(error.stack);
      }
    }
  };

  GameManager.prototype._checkDroneOut = function (drone) {
    if (drone.position) {
      var map_limit = this._mapManager.getMapInfo().map_size / 2;
      return (drone.position.z > this._mapManager.getMapInfo().height) ||
        (drone.position.x < -map_limit) ||
        (drone.position.x > map_limit) ||
        (drone.position.y < -map_limit) ||
        (drone.position.y > map_limit);
    }
  };

  GameManager.prototype._checkObstacleCollision = function (drone, obstacle) {
    if (drone.colliderMesh &&
        drone.colliderMesh.intersectsMesh(obstacle, true)) {
      drone._internal_crash(new Error('Drone ' + drone.id +
                                      ' touched an obstacle.'), false);
      //Following workaround seems not needed with new babylonjs versions
      /**
       * Closest facet check is needed for sphere and cylinder,
       * but just seemed bugged with the box
       * So only need to check intersectMesh for the box
       */
      /*if (obstacle.type == "box") {
        closest = true;
      } else {
        obstacle.updateFacetData();
        closest = obstacle.getClosestFacetAtCoordinates(
          drone.infosMesh.position.x,
          drone.infosMesh.position.y,
          drone.infosMesh.position.z, projected);
      }
      if (closest !== null) {
        drone._internal_crash(new Error('Drone ' + drone.id +
                                        ' touched an obstacle.'));
      }*/
    }
  };

  GameManager.prototype._checkFlagCollision = function (drone, flag) {
    if (drone.team === TEAM_ENEMY) {
      return;
    }
    function distance(a, b) {
      return Math.sqrt(Math.pow((a.x - b.x), 2) + Math.pow((a.y - b.y), 2) +
                       Math.pow((a.z - b.z), 2));
    }
    if (drone.position) {
      //TODO epsilon distance is 15 because of fixed wing loiter flights
      //there is not a proper collision
      if (distance(drone.position, flag.location) <=
          this._mapManager.getMapInfo().flag_distance_epsilon) {
        drone._internal_crash(new Error('Drone ' + drone.id +
                                        ' touched flag ' + flag.id), false);
        if (flag.weight > 0) {
          flag.weight -= 1;
          drone.score += flag.score; // move score to a global place? GM, MM?
        }
      }
    }
  };

  GameManager.prototype._checkCollision = function (drone, other) {
    if (drone.team === TEAM_ENEMY && other.team === TEAM_ENEMY) {
      return;
    }
    function distance(a, b) {
      return Math.sqrt(Math.pow((a.x - b.x), 2) + Math.pow((a.y - b.y), 2) +
                       Math.pow((a.z - b.z), 2));
    }
    if (drone.team !== other.team) {
      var enemy, prey;
      if (drone.team === TEAM_ENEMY) {
        enemy = drone;
        prey = other;
      } else if (other.team === TEAM_ENEMY) {
        enemy = other;
        prey = drone;
      }
      if (drone.position && other.position) {
        if (distance(drone.position, other.position) <
            enemy.getCollisionSector()) {
          drone._internal_crash(new Error('enemy drone ' + enemy.id +
                               ' bumped drone ' + prey.id + '.'), false);
          other._internal_crash(new Error('enemy drone ' + enemy.id +
                               ' bumped drone ' + prey.id + '.'), false);
        }
      }
    }
    if (drone.colliderMesh && other.colliderMesh &&
        drone.colliderMesh.intersectsMesh(other.colliderMesh, false)) {
      drone._internal_crash(new Error('drone ' + drone.id +
                           ' touched drone ' + other.id + '.'), false);
      other._internal_crash(new Error('drone ' + drone.id +
                           ' touched drone ' + other.id + '.'), false);
    }
  };

  GameManager.prototype._update = function (delta_time, fullscreen) {
    var _this = this,
      queue = new RSVP.Queue(),
      i;
    this._updateTimeAndLog(delta_time);

    // trigger all deferred calls if it is time
    for (i = _this._delayed_defer_list.length - 1; 0 <= i; i -= 1) {
      _this._delayed_defer_list[i][1] =
        _this._delayed_defer_list[i][1] - delta_time;
      if (_this._delayed_defer_list[i][1] <= 0) {
        queue.push(_this._delayed_defer_list[i][0]);
        _this._delayed_defer_list.splice(i, 1);
      }
    }

    if (fullscreen) {
      //Only resize if size changes
      if (this._canvas.width !== GAMEPARAMETERS.fullscreen.width) {
        this._canvas.width = GAMEPARAMETERS.fullscreen.width;
        this._canvas.height = GAMEPARAMETERS.fullscreen.height;
      }
    } else {
      if (this._canvas.width !== this._canvas_width) {
        this._canvas.width = this._canvas_width;
        this._canvas.height = this._canvas_height;
        this._engine.resize(true);
      }
    }

    this._droneList.forEach(function (drone) {
      queue.push(function () {
        drone._tick += 1;
        if (drone.can_play) {
          if (drone.getCurrentPosition().altitude <= 0) {
            if (!drone.isLanding()) {
              drone._internal_crash(new Error('Drone ' + drone.id +
                                              ' touched the floor.'), false);
            } else {
              drone._internal_crash();
            }
          } else if (_this._checkDroneOut(drone)) {
            drone._internal_crash(new Error('Drone ' + drone.id +
                                            ' out of limits.'), false);
          } else {
            _this._droneList.forEach(function (other) {
              if (other.can_play && drone.id !== other.id) {
                _this._checkCollision(drone, other);
              }
            });
            _this._mapManager._obstacle_list.forEach(function (obstacle) {
              _this._checkObstacleCollision(drone, obstacle);
            });
            _this._mapManager._flag_list.forEach(function (flag) {
              _this._checkFlagCollision(drone, flag);
            });
          }
        }
        return drone.internal_update(delta_time);
      });
    });

    return queue
      .push(function () {
        if (_this._timeOut()) {
          console.log("TIMEOUT!");
          _this._droneList.forEach(function (drone) {
            if (drone.can_play) {
              drone._internal_crash(new Error('Timeout.'), false);
            }
          });
          _this._result_message += "TIMEOUT!";
          return _this._finish();
        }
        if (_this._allDronesFinished()) {
          console.log("ALL DRONES DOWN");
          _this._result_message += "ALL DRONES DOWN!";
          return _this._finish();
        }
        /*if (_this._allFlagsCaptured()) {
          console.log("ALL FLAGS CAPTURED");
          _this._result_message += "ALL FLAGS CAPTURED!";
          return _this._finish();
        }*/
      });
  };

  GameManager.prototype._updateTimeAndLog =
    function (delta_time) {
      this._game_duration += delta_time;
      var color, drone_position, game_manager = this, geo_coordinates,
        log_count, map_info, map_manager, material, position_obj,
        seconds = Math.floor(this._game_duration / 1000), trace_objects;

      if (GAMEPARAMETERS.log_drone_flight || GAMEPARAMETERS.draw_flight_path) {
        this._droneList_user.forEach(function (drone, index) {
          if (drone.can_play) {
            drone_position = drone.position;
            if (GAMEPARAMETERS.log_drone_flight) {
              map_manager = game_manager._mapManager;
              map_info = map_manager.getMapInfo();
              log_count = game_manager._log_count[index];
              if (log_count === 0 ||
                  game_manager._game_duration / log_count > 1) {
                log_count += GAMEPARAMETERS.log_interval_time;
                geo_coordinates = map_manager.convertToGeoCoordinates(
                  drone_position.x,
                  drone_position.y,
                  drone_position.z
                );
                game_manager._flight_log[index].push([
                  game_manager._game_duration, geo_coordinates.latitude,
                  geo_coordinates.longitude,
                  map_info.start_AMSL + drone_position.z,
                  drone_position.z, drone.getYaw(), drone.getSpeed(),
                  drone.getClimbRate()
                ]);
              }
            }
            if (GAMEPARAMETERS.draw_flight_path) {
              //draw drone position every some seconds
              if (seconds - game_manager._last_position_drawn[index] > 0.2) {
                game_manager._last_position_drawn[index] = seconds;
                position_obj = BABYLON.MeshBuilder.CreateBox(
                  "obs_" + seconds,
                  { size: 1 },
                  game_manager._scene
                );
                // swap y and z axis so z axis represents altitude
                position_obj.position = new BABYLON.Vector3(drone_position.x,
                                                            drone_position.z,
                                                            drone_position.y);
                //TODO base it on map_size
                position_obj.scaling = new BABYLON.Vector3(4, 4, 4);
                material = new BABYLON.StandardMaterial(game_manager._scene);
                material.alpha = 1;
                color = new BABYLON.Color3(255, 0, 0);
                var color_index = index % 10;
                if (game_manager._colors[color_index]) {
                  color = game_manager._colors[color_index];
                }
                material.diffuseColor = color;
                position_obj.material = material;
                if (GAMEPARAMETERS.temp_flight_path) {
                  trace_objects = game_manager._trace_objects_per_drone[index];
                  if (trace_objects.length === 10) {
                    trace_objects[0].dispose();
                    trace_objects.splice(0, 1);
                  }
                  trace_objects.push(position_obj);
                }
              }
            }
          }
        });
      }
    };

  GameManager.prototype._timeOut = function () {
    return this._totalTime - this._game_duration <= 0;
  };

  GameManager.prototype._allDronesFinished = function () {
    var finish = true;
    this._droneList_user.forEach(function (drone) {
      if (drone.can_play) {
        finish = false;
      }
    });
    return finish;
  };

  GameManager.prototype._calculateUserScore = function () {
    var score = 0, base = this._mapManager.getMapInfo().initial_position, dist;
    this._droneList_user.forEach(function (drone) {
      score += drone.score;
      if (drone.last_position) {
        dist = Math.sqrt(Math.pow((drone.last_position.x - base.x), 2)
                         + Math.pow((drone.last_position.y - base.y), 2));
        if (dist < BASE_DISTANCE) {
          score += 1;
        }
      }
    });
    return score;
  };

  GameManager.prototype._finish = function () {
    console.log("Simulation finished");
    this._result_message += " User score: " + this._calculateUserScore();
    this._canUpdate = false;
    return this.finish_deferred.resolve();
  };

  GameManager.prototype._dispose = function () {
    if (this._scene) {
      this._scene.dispose();
    }
  };

  GameManager.prototype._init = function () {
    var _this = this, canvas, hemi_north, hemi_south, camera, cam_radius,
      on3DmodelsReady, map_size = 900; //GAMEPARAMETERS.map.map_size
    canvas = this._canvas;
    this._delayed_defer_list = [];
    this._dispose();
    // Create the Babylon engine
    this._engine = new BABYLON.Engine(canvas, true, {
      //options for event handling
      stencil: true,
      disableWebGL2Support: false,
      audioEngine: false
    });
    this._scene = new BABYLON.Scene(this._engine);
    //for DEBUG - fondo negro
    //this._scene.clearColor = BABYLON.Color3.Black();
    //deep ground color - light blue simile sky
    this._scene.clearColor = new BABYLON.Color4(
      88 / 255,
      171 / 255,
      217 / 255,
      255 / 255
    );
    //removed for event handling
    //this._engine.enableOfflineSupport = false;
    //this._scene.collisionsEnabled = true;
    // Lights
    hemi_north = new BABYLON.HemisphericLight(
      "hemiN",
      new BABYLON.Vector3(1, -1, 1),
      this._scene
    );
    hemi_north.intensity = 0.75;
    hemi_south = new BABYLON.HemisphericLight(
      "hemiS",
      new BABYLON.Vector3(-1, 1, -1),
      this._scene
    );
    hemi_south.intensity = 0.75;
    //HARDCODE camera to a hardcoded map_size
     //skybox scene limit
    cam_radius = (map_size * 1.10 < 6000) ? map_size * 1.10 : 6000;
    camera = new BABYLON.ArcRotateCamera("camera", 0, 1.25, cam_radius,
                                         BABYLON.Vector3.Zero(), this._scene);
    camera.wheelPrecision = 10;
    //zoom out limit
    camera.upperRadiusLimit = map_size * 10;
    //scene.activeCamera.upperRadiusLimit = max * 4;
    //changed for event handling
    //camera.attachControl(this._scene.getEngine().getRenderingCanvas()); //orig
    camera.attachControl(canvas, true);
    camera.maxz = 400000;
    this._camera = camera;

    // Render loop
    this._engine.runRenderLoop(function () {
      _this._scene.render();
    });
    // -------------------------------- SIMULATION - Prepare API, Map and Teams
    on3DmodelsReady = function (ctx) {
      // Get the game parameters
      if (!ctx._map_swapped) {
        GAMEPARAMETERS = ctx._getGameParameter();
        ctx._map_swapped = true;
      }
      // Init the map
      _this._mapManager = new MapManager(ctx._scene, GAMEPARAMETERS.map);
      ctx._spawnDrones(_this._mapManager.getMapInfo().initial_position,
                       GAMEPARAMETERS.drone.list, TEAM_USER, ctx);
      ctx._spawnDrones(null, _this._mapManager._enemy_list, TEAM_ENEMY, ctx);
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //Hack to make advanced texture work
      var documentTmp = document, advancedTexture, count,
        controlMesh, rect;
      document = undefined;
      advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI(
        "UI",
        true,
        ctx._scene
      );
      document = documentTmp;
      function colourDrones(drone_list, colour) {
        for (count = 0; count < drone_list.length; count += 1) {
          controlMesh = drone_list[count].infosMesh;
          rect = new BABYLON.GUI.Rectangle();
          rect.width = "10px";
          rect.height = "10px";
          rect.cornerRadius = 20;
          rect.color = "white";
          rect.thickness = 0.5;
          rect.background = colour;
          advancedTexture.addControl(rect);
          rect.linkWithMesh(controlMesh);
        }
      }
      function colourFlags(flag_list) {
        for (count = 0; count < flag_list.length; count += 1) {
          controlMesh = flag_list[count].subMeshes[0]._mesh;
          rect = new BABYLON.GUI.Rectangle();
          rect.width = "15px";
          rect.height = "10px";
          rect.cornerRadius = 1;
          rect.color = "white";
          rect.thickness = 0.5;
          rect.background = "green";
          advancedTexture.addControl(rect);
          rect.linkWithMesh(controlMesh);
        }
      }
      colourFlags(_this._mapManager._flag_list);
      colourDrones(ctx._droneList_user, "blue");
      colourDrones(ctx._droneList_enemy, "red");
      console.log("on3DmodelsReady - advaced textures added");
      return ctx;
    };
    // ----------------------------------- SIMULATION - Load 3D models
    return new RSVP.Queue()
      .push(function () {
        return new RSVP.Promise(function (resolve) {
          return _this._load3DModel(resolve);
        });
      })
      .push(function () {
        on3DmodelsReady(_this);
        _this._droneList =
          _this._droneList_user.concat(_this._droneList_enemy);
        var result = new RSVP.Queue();
        result.push(function () {
          return RSVP.delay(1000);
        });
        return result.push(_this._start.bind(_this));
      });
  };

  GameManager.prototype._start = function () {
    var _this = this, promise_list, start_msg;
    _this.waiting_update_count = 0;
    _this.ongoing_update_promise = null;
    _this.finish_deferred = RSVP.defer();
    console.log("Simulation started.");
    this._game_duration = Date.now();
    this._totalTime = GAMEPARAMETERS.gameTime * 1000 + this._game_duration;

    return new RSVP.Queue()
      .push(function () {
        promise_list = [];
        _this._droneList_user.forEach(function (drone) {
          drone._tick = 0;
          promise_list.push(drone.internal_start());
        });
        start_msg = GAMEPARAMETERS.operator_init_msg;
        promise_list.push(_this._droneList_user[0].sendMsg(start_msg));
        _this._droneList_enemy.forEach(function (drone) {
          drone._tick = 0;
          promise_list.push(drone.internal_start());
        });
        return RSVP.all(promise_list);
      })
      .push(function () {
        _this._canUpdate = true;
        return _this.finish_deferred.promise;
      }, function (error) {
        throw new Error('Error on drone initialization msg -' + error.message);
      });
  };

  GameManager.prototype._load3DModel = function (callback) {
    var _this = this, droneTask, mapTask,
      assetManager = new BABYLON.AssetsManager(this._scene);
    assetManager.useDefaultLoadingScreen = true;
    // DRONE
    droneTask = assetManager.addMeshTask("loadingDrone", "", "assets/drone/",
                                         "drone.babylon");
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
    mapTask = assetManager.addMeshTask("loadingMap", "", "assets/map/",
                                       "map.babylon");
    mapTask.onSuccess = function (task) {
      task.loadedMeshes.forEach(function (mesh) {
        mesh.isPickable = false;
        mesh.isVisible = false;
      });
    };
    mapTask.onError = function () {
      console.log("Error loading 3D model for Map");
    };
    assetManager.onFinish = function () {
      return callback();
    };
    assetManager.load();
  };

  GameManager.prototype._getGameParameter = function () {
    var parameter = {};
    Object.assign(parameter, this._game_parameters_json);
    this._gameParameter = {};
    Object.assign(this._gameParameter, this._game_parameters_json);
    return parameter;
  };

  GameManager.prototype._spawnDrones = function (init_position, drone_list,
                                                 team, ctx, drone_location) {
    var position, i, position_list = [], max_collision = 10 * drone_list.length,
      collision_nb = 0, api, center, id_offset;
    function checkCollision(position, list) {
      var el;
      for (el = 0; el < list.length; el += 1) {
        if (position.equalsWithEpsilon(list[el], 0.5)) {
          return true;
        }
      }
      return false;
    }
    function spawnDrone(x, y, z, index, drone_info, api, team) {
      var default_drone_AI = api.getDroneAI(), code, code_eval;
      if (default_drone_AI) {
        code = default_drone_AI;
      } else {
        code = drone_info.script_content;
      }
      if (!code.includes("me.onStart")) {
        code = "me.onStart = function () { me.exit(); };";
      }
      code_eval = "let drone = new DroneManager(ctx._scene, " +
          index + ', api, team);' +
          "let droneMe = function(NativeDate, me, Math, window, DroneManager," +
          " GameManager, FixedWingDroneAPI, EnemyDroneAPI, BABYLON, " +
          "GAMEPARAMETERS) {" +
          "var start_time = (new Date(2070, 0, 0, 0, 0, 0, 0)).getTime();" +
          "Date.now = function () {" +
          "return start_time + drone._tick * 1000/60;}; " +
          "function Date() {if (!(this instanceof Date)) " +
          "{throw new Error('Missing new operator');} " +
          "if (arguments.length === 0) {return new NativeDate(Date.now());} " +
          "else {return new NativeDate(...arguments);}}";
      // Simple desactivation of direct access of all globals
      // It is still accessible in reality, but it will me more visible
      // if people really access them
      if (x !== null && y !== null && z !== null) {
        code_eval += "me.setStartingPosition(" + x + ", " + y + ", " + z + ");";
      }
      //base = code_eval;
      code_eval += code + "}; droneMe(Date, drone, Math, {});";
      //base += "};ctx._droneList_" + team + ".push(drone)";
      code_eval += "ctx._droneList_" + team + ".push(drone)";
      /*jslint evil: true*/
      eval(code_eval);
      /*jslint evil: false*/
      /*try {
        eval(code_eval);
      } catch (error) {
        eval(base);
      }*/
    }
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
    for (i = 0; i < drone_list.length; i += 1) {
      if (!init_position) {
        center = drone_list[i].position;
      } else {
        center = init_position;
      }
      position = randomSpherePoint(center.x + i, center.y + i, center.z + i,
                                   0, 0, 0);
      if (checkCollision(position, position_list)) {
        collision_nb += 1;
        if (collision_nb < max_collision) {
          i -= 1;
        }
      } else {
        position_list.push(position);
        id_offset = team === TEAM_ENEMY ? GAMEPARAMETERS.drone.list.length : 0;
        api = new this.APIs_dict[drone_list[i].type](
          this,
          drone_list[i],
          GAMEPARAMETERS,
          i + id_offset
        );
        spawnDrone(position.x, position.y, position.z, i + id_offset,
                   drone_list[i], api, team);
      }
    }
  };

  return GameManager;
}());

/******************************************************************************/

/*********************** DRONE SIMULATOR LOGIC ********************************/

var runGame, updateGame;

(function () {
  "use strict";
  console.log('game logic');
  var game_manager_instance;

  runGame = function (canvas, game_parameters_json) {
    if (!game_manager_instance) {
      game_manager_instance = new GameManager(canvas, game_parameters_json);
    }
    return game_manager_instance.run();
  };

  updateGame = function (fullscreen) {
    if (game_manager_instance) {
      return game_manager_instance.update(fullscreen);
    }
  };

}(this));

/******************************************************************************/