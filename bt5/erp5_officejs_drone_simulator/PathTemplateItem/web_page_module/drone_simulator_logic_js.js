/*global BABYLON, RSVP, console, FixedWingDroneAPI, DroneLogAPI, document*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true,
         unparam: true */

var GAMEPARAMETERS = {};
//for DEBUG/TEST mode
var baseLogFunction = console.log, console_log = "";

function spawnDrone(spawnDrone_x, spawnDrone_y, spawnDrone_z, spawnDrone_index,
                    spawnDrone_drone_info, spawnDrone_api, spawnDrone_scene,
                    spawnDrone_droneList) {
  "use strict";
  var default_drone_AI = spawnDrone_api.getDroneAI(), spawnDrone_code,
    spawnDrone_base, code_eval;
  if (default_drone_AI) {
    spawnDrone_code = default_drone_AI;
  } else {
    spawnDrone_code = spawnDrone_drone_info.script_content;
  }
  code_eval = "let spawnDrone_drone = new DroneManager(spawnDrone_scene, " +
      spawnDrone_index + ', spawnDrone_api);' +
      "let droneMe = function(NativeDate, me, Math, window, DroneManager," +
      " GameManager, DroneLogAPI, FixedWingDroneAPI, BABYLON, " +
      "GAMEPARAMETERS) {" +
      "Date.now = function () {" +
      "return me._API._gameManager.getCurrentTime();}; " +
      "function Date() {if (!(this instanceof Date)) " +
      "{throw new Error('Missing new operator');} " +
      "if (arguments.length === 0) {return new NativeDate(Date.now());} " +
      "else {return new NativeDate(...arguments);}}";
  // Simple desactivation of direct access of all globals
  // It is still accessible in reality, but it will me more visible
  // if people really access them
  if (spawnDrone_x !== null && spawnDrone_y !== null && spawnDrone_z !== null) {
    code_eval += "me.setStartingPosition(" + spawnDrone_x + ", "
      + spawnDrone_y + ", " + spawnDrone_z + ");";
  }
  spawnDrone_base = code_eval;
  code_eval +=
    spawnDrone_code + "}; droneMe(Date, spawnDrone_drone, Math, {});";
  spawnDrone_base += "};spawnDrone_droneList.push(spawnDrone_drone)";
  code_eval += "spawnDrone_droneList.push(spawnDrone_drone)";
  /*jslint evil: true*/
  try {
    eval(code_eval);
  } catch (error) {
    console.error(error);
    eval(spawnDrone_base);
  }
  /*jslint evil: false*/
}

/******************************* DRONE MANAGER ********************************/
var DroneManager = /** @class */ (function () {
  "use strict";

  //** CONSTRUCTOR
  function DroneManager(scene, id, API) {
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
    this._last_onUpdate_timestamp = 0;
    this._speed = 0;
    this._acceleration = 0;
    this._direction = new BABYLON.Vector3(0, 0, 1); // North
    this._scene = scene;
    this._canUpdate = true;
    this._id = id;
    this._API = API; // var API created on AI evel
    // Create the control mesh
    this._controlMesh = BABYLON.Mesh.CreateBox(
      "droneControl_" + id,
      1.55, // 155 cm long wingspan
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
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "id", {
    get: function () { return this._id; },
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
  DroneManager.prototype.getDroneDict = function () {
    return this._API._drone_dict_list;
  };
  DroneManager.prototype.internal_start = function (initial_position) {
    this._API.internal_start(this);
    this._canPlay = true;
    this._canCommunicate = true;
    this._targetCoordinates = initial_position;
    try {
      return this.onStart(this._API._gameManager._start_time);
    } catch (error) {
      console.warn('Drone crashed on start due to error:', error);
      this._internal_crash(error);
    }
  };
  DroneManager.prototype._callSetTargetCommand =
    function (latitude, longitude, altitude, speed, radius) {
      var current_time = this._API._gameManager.getCurrentTime();
      if (!this.isReadyToFly()) {
        return;
      }
      if (current_time - this._last_command_timestamp
            < 1000 / this._API.getMaxCommandFrequency()) {
        this._internal_crash(new Error('Minimum interval between commands is ' +
            1000 / this._API.getMaxCommandFrequency() + ' milliseconds'));
      }
      this._internal_setTargetCoordinates(latitude, longitude, altitude, speed,
                                          radius);
      this._last_command_timestamp = current_time;
    };
  /**
   * Set a target point to move
   */
  DroneManager.prototype.setTargetCoordinates =
    function (latitude, longitude, altitude, speed) {
      this._callSetTargetCommand(latitude, longitude, altitude, speed);
    };
  DroneManager.prototype._internal_setTargetCoordinates =
    function (latitude, longitude, altitude, speed, radius) {
      if (!this._canPlay) {
        return;
      }
      //convert real geo-coordinates to virtual x-y coordinates
      this._targetCoordinates =
        this._API.processCoordinates(latitude, longitude, altitude);
      this._API.internal_setTargetCoordinates(
        this,
        this._targetCoordinates,
        speed,
        radius
      );
    };
  DroneManager.prototype.internal_update = function (delta_time) {
    var context = this,
      current_time = this._API._gameManager.getCurrentTime(),
      onUpdate_interval = this._API.getOnUpdateInterval(),
      onUpdate_start;
    if (this._controlMesh) {
      context._API.internal_position_update(context, delta_time);
      if (context._canUpdate &&
          current_time - this._last_onUpdate_timestamp >= onUpdate_interval) {
        context._canUpdate = false;
        return new RSVP.Queue()
          .push(function () {
            onUpdate_start = Date.now();
            context._last_onUpdate_timestamp = current_time;
            context.onUpdate(current_time);
            if (onUpdate_interval > 0 &&
                Date.now() - onUpdate_start > onUpdate_interval) {
              throw new Error('onUpdate execution took ' +
                              (Date.now() - onUpdate_start) +
                              ' milliseconds but loop interval is only ' +
                              onUpdate_interval +
                              ' milliseconds');
            }
          })
          .push(function () {
            context._canUpdate = true;
          }, function (error) {
            console.warn('Drone crashed on update due to error:', error);
            context._internal_crash(error);
          })
          .push(function () {
            context._API.internal_info_update(context);
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
  DroneManager.prototype._internal_crash = function (error) {
    this._canCommunicate = false;
    this._controlMesh = null;
    this._mesh = null;
    this._canPlay = false;
    if (error) {
      this._API._gameManager.logError(this, error);
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
      position.timestamp = this._API._gameManager.getCurrentTime();
      return position;
    }
    return null;
  };
  /**
   * Make the drone loiter (circle with a set radius)
   */
  DroneManager.prototype.loiter =
    function (latitude, longitude, altitude, radius, speed) {
      this._callSetTargetCommand(latitude, longitude, altitude, speed, radius);
    };
  DroneManager.prototype.getFlightParameters = function () {
    if (this._API.getFlightParameters) {
      return this._API.getFlightParameters();
    }
    return null;
  };
  DroneManager.prototype.getMaxCommandFrequency = function () {
    return this._API.getMaxCommandFrequency();
  };
  DroneManager.prototype.getYaw = function () {
    return this._API.getYaw(this);
  };
  DroneManager.prototype.get3DSpeed = function () {
    return this._speed;
  };
  DroneManager.prototype.getSpeed = function () {
    return this._API.getSpeed(this);
  };
  DroneManager.prototype.getClimbRate = function () {
    return this._API.getClimbRate(this);
  };
  DroneManager.prototype.takeOff = function () {
    return this._API.takeOff();
  };
  DroneManager.prototype.land = function () {
    if (!this.isLanding()) {
      return this._API.land(this);
    }
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
  return DroneManager;
}());

/******************************************************************************/



/******************************** MAP UTILIS **********************************/

var MapUtils = /** @class */ (function () {
  "use strict";

  var R = 6371e3;

  //** CONSTRUCTOR
  function MapUtils(map_param) {
    var _this = this;
    _this.map_param = {};
    _this.map_param.height = map_param.height;
    _this.map_param.start_AMSL = map_param.start_AMSL;
    _this.map_param.min_lat = map_param.min_lat;
    _this.map_param.max_lat = map_param.max_lat;
    _this.map_param.min_lon = map_param.min_lon;
    _this.map_param.max_lon = map_param.max_lon;
    _this.map_param.depth = _this.latLonDistance(
      [map_param.min_lat, map_param.min_lon],
      [map_param.max_lat, map_param.min_lon]
    );
    _this.map_param.width = _this.latLonDistance(
      [map_param.min_lat, map_param.min_lon],
      [map_param.min_lat, map_param.max_lon]
    );
    _this.map_info = {
      "depth": _this.map_param.depth,
      "width": _this.map_param.width
    };
    _this.map_info.height = _this.map_param.height;
    _this.map_info.start_AMSL = _this.map_param.start_AMSL;
    _this.map_info.min_x = _this.longitudToX(map_param.min_lon);
    _this.map_info.min_y = _this.latitudeToY(map_param.min_lat);
    _this.map_info.max_x = _this.longitudToX(map_param.max_lon);
    _this.map_info.max_y = _this.latitudeToY(map_param.max_lat);
  }

  MapUtils.prototype.latLonDistance = function (c1, c2) {
    var q1 = c1[0] * Math.PI / 180,
      q2 = c2[0] * Math.PI / 180,
      dq = (c2[0] - c1[0]) * Math.PI / 180,
      dl = (c2[1] - c1[1]) * Math.PI / 180,
      a = Math.sin(dq / 2) * Math.sin(dq / 2) +
        Math.cos(q1) * Math.cos(q2) *
        Math.sin(dl / 2) * Math.sin(dl / 2),
      c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };
  MapUtils.prototype.longitudToX = function (lon) {
    return (this.map_info.width / 360.0) * (180 + lon);
  };
  MapUtils.prototype.latitudeToY = function (lat) {
    return (this.map_info.depth / 180.0) * (90 - lat);
  };
  MapUtils.prototype.convertToLocalCoordinates =
    function (latitude, longitude, altitude) {
      var map_info = this.map_info,
        x = this.longitudToX(longitude),
        y = this.latitudeToY(latitude);
      return {
        x: (((x - map_info.min_x) / (map_info.max_x - map_info.min_x)) - 0.5)
            * map_info.width,
        y: (((y - map_info.min_y) / (map_info.max_y - map_info.min_y)) - 0.5)
            * map_info.depth,
        z: altitude
      };
    };
  MapUtils.prototype.convertToGeoCoordinates = function (x, y, z) {
    var lon = (x / this.map_info.width) + 0.5,
      lat = (y / this.map_info.depth) + 0.5;
    lon = lon * (this.map_info.max_x - this.map_info.min_x) +
      this.map_info.min_x;
    lon = lon / (this.map_info.width / 360.0) - 180;
    lat = lat * (this.map_info.max_y - this.map_info.min_y) +
      this.map_info.min_y;
    lat = 90 - lat / (this.map_info.depth / 180.0);
    return {
      latitude: lat,
      longitude: lon,
      altitude: z
    };
  };

  return MapUtils;
}());

/******************************************************************************/



/******************************** MAP MANAGER *********************************/

var MapManager = /** @class */ (function () {
  "use strict";
  //default square map
  var  MAP_HEIGHT = 700,
    START_AMSL = 595,
    MIN_LAT = 45.6419,
    MAX_LAT = 45.65,
    MIN_LON = 14.265,
    MAX_LON = 14.2766,
    MAP = {
      "height": MAP_HEIGHT,
      "start_AMSL": START_AMSL,
      "min_lat": MIN_LAT,
      "max_lat": MAX_LAT,
      "min_lon": MIN_LON,
      "max_lon": MAX_LON
    };

  //** CONSTRUCTOR
  function MapManager(scene, map_param, initial_position) {
    var _this = this, max_sky, skybox, skyboxMat, largeGroundMat,
      largeGroundBottom, width, depth, terrain, max;
    if (!map_param) {
      // Use default map base parameters
      map_param = MAP;
    }
    _this.mapUtils = new MapUtils(map_param);
    _this.map_info = map_param;
    Object.assign(_this.map_info, _this.mapUtils.map_info);
    _this.map_info.initial_position = _this.mapUtils.convertToLocalCoordinates(
      initial_position.latitude,
      initial_position.longitude,
      initial_position.altitude
    );
    max = Math.max(
      _this.map_info.depth,
      _this.map_info.height,
      _this.map_info.width
    );
    // Skybox
    max_sky =  (max * 15 < 20000) ? max * 15 : 20000; //skybox scene limit
    skybox = BABYLON.MeshBuilder.CreateBox("skyBox", { size: max_sky }, scene);
    skyboxMat = new BABYLON.StandardMaterial("skybox", scene);
    skyboxMat.backFaceCulling = false;
    skyboxMat.disableLighting = true;
    skyboxMat.reflectionTexture = new BABYLON.CubeTexture("./assets/skybox/sky",
                                                          scene);
    skyboxMat.reflectionTexture.coordinatesMode = BABYLON.Texture.SKYBOX_MODE;
    skyboxMat.infiniteDistance = true;
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
    terrain.scaling = new BABYLON.Vector3(depth / 50000, _this.map_info.height / 50000,
                                          width / 50000);
  }
  MapManager.prototype.getMapInfo = function () {
    return this.map_info;
  };
  MapManager.prototype.latLonDistance = function (c1, c2) {
    return this.mapUtils.latLonDistance(c1, c2);
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
  // *** CONSTRUCTOR ***
  function GameManager(canvas, game_parameters_json) {
    var drone, header_list, i;
    this._canvas = canvas;
    this._canvas_width = canvas.width;
    this._canvas_height = canvas.height;
    this._scene = null;
    this._engine = null;
    this._droneList = [];
    this._canUpdate = false;
    this._max_step_animation_frame = game_parameters_json.simulation_speed;
    if (!this._max_step_animation_frame) { this._max_step_animation_frame = 5; }
    Object.assign(GAMEPARAMETERS, game_parameters_json);
    this._game_parameters_json = game_parameters_json;
    this._map_swapped = false;
    this._log_count = [];
    this._flight_log = [];
    if (GAMEPARAMETERS.draw_flight_path) {
      this._last_position_drawn = [];
      this._trace_objects_per_drone = [];
      // ! Be aware that the following functions relies on this log format:
      // - getLogEntries at Drone Simulator Log Page
      // - getLogEntries at Dron Log Follower API
      header_list = ["timestamp (ms)", "latitude (°)", "longitude (°)",
                     "AMSL (m)", "rel altitude (m)", "yaw (°)",
                     "ground speed (m/s)", "climb rate (m/s)"];
      for (drone = 0; drone < GAMEPARAMETERS.droneList.length; drone += 1) {
        this._flight_log[drone] = [];
        this._flight_log[drone].push(header_list);
        this._log_count[drone] = 0;
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
    this.APIs_dict = {
      FixedWingDroneAPI: FixedWingDroneAPI,
      DroneLogAPI: DroneLogAPI
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

  GameManager.prototype.logError = function (drone, error) {
    this._flight_log[drone._id].push(error.stack);
  };

  GameManager.prototype._checkCollision = function (drone, other) {
    if (drone.colliderMesh && other.colliderMesh &&
        drone.colliderMesh.intersectsMesh(other.colliderMesh, false)) {
      drone._internal_crash(new Error('Drone ' + drone.id +
                            ' touched drone ' + other.id + '.'));
      other._internal_crash(new Error('Drone ' + drone.id +
                            ' touched drone ' + other.id + '.'));
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
        if (drone._API.isCollidable && drone.can_play) {
          if (drone.getCurrentPosition().altitude <= 0) {
            if (!drone.isLanding()) {
              drone._internal_crash(new Error('Drone ' + drone.id +
                                              ' touched the floor.'));
            } else {
              drone._internal_crash();
            }
          } else {
            _this._droneList.forEach(function (other) {
              if (other.can_play && drone.id !== other.id) {
                _this._checkCollision(drone, other);
              }
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
          return _this._finish();
        }
        if (_this._allDronesFinished()) {
          console.log("ALL DRONES EXITED");
          return _this._finish();
        }
      });
  };

  GameManager.prototype._updateTimeAndLog =
    function (delta_time) {
      this._game_duration += delta_time;
      var color, drone_position, game_manager = this, geo_coordinates,
        log_count, map_info, map_manager, material, position_obj,
        current_time = this.getCurrentTime(),
        seconds = Math.floor(current_time  / 1000), trace_objects;

      if (GAMEPARAMETERS.log_drone_flight || GAMEPARAMETERS.draw_flight_path) {
        this._droneList.forEach(function (drone, index) {
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
                  current_time, geo_coordinates.latitude,
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
                position_obj.scaling = new BABYLON.Vector3(4, 4, 4);
                material = new BABYLON.StandardMaterial(game_manager._scene);
                material.alpha = 1;
                color = new BABYLON.Color3(255, 0, 0);
                if (game_manager._colors[index]) {
                  color = game_manager._colors[index];
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
    this._droneList.forEach(function (drone) {
      if (drone.can_play) {
        finish = false;
      }
    });
    return finish;
  };

  GameManager.prototype._finish = function () {
    console.log("Simulation finished");
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
      on3DmodelsReady,
      mapUtils = new MapUtils(GAMEPARAMETERS.map),
      map_size = Math.max(
        mapUtils.map_info.depth,
        mapUtils.map_info.height,
        mapUtils.map_info.width
      );
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
    cam_radius = Math.min(
      1.10 * Math.sqrt(mapUtils.map_info.width * mapUtils.map_info.depth),
      6000
    );
    camera = new BABYLON.ArcRotateCamera("camera", 0, 1.25, cam_radius,
                                         BABYLON.Vector3.Zero(), this._scene);
    camera.wheelPrecision = 10;
    //zoom out limit
    camera.upperRadiusLimit = map_size * 10;
    //changed for event handling
    //camera.attachControl(this._scene.getEngine().getRenderingCanvas()); //orig
    camera.attachControl(canvas, true);
    camera.maxz = 40000;
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
      _this._mapManager = new MapManager(ctx._scene, GAMEPARAMETERS.map,
                                         GAMEPARAMETERS.initialPosition);
      ctx._spawnDrones(_this._mapManager.getMapInfo().initial_position,
                       GAMEPARAMETERS.droneList, ctx);
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //Hack to make advanced texture work
      var documentTmp = document, advancedTexture, count,
        controlMesh, rect, label;
      document = undefined;
      advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI(
        "UI",
        true,
        ctx._scene
      );
      document = documentTmp;
      for (count = 0; count < GAMEPARAMETERS.droneList.length; count += 1) {
        controlMesh = ctx._droneList[count].infosMesh;
        rect = new BABYLON.GUI.Rectangle();
        rect.width = "10px";
        rect.height = "10px";
        rect.cornerRadius = 20;
        rect.color = "white";
        rect.thickness = 0.5;
        rect.background = "grey";
        advancedTexture.addControl(rect);
        label = new BABYLON.GUI.TextBlock();
        label.text = count.toString();
        label.fontSize = 7;
        rect.addControl(label);
        rect.linkWithMesh(controlMesh);
        rect.linkOffsetY = 0;
      }
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
        var result = new RSVP.Queue();
        result.push(function () {
          return RSVP.delay(1000);
        });
        return result.push(_this._start.bind(_this));
      });
  };

  GameManager.prototype._start = function () {
    var _this = this, promise_list;
    _this.waiting_update_count = 0;
    _this.ongoing_update_promise = null;
    _this.finish_deferred = RSVP.defer();
    console.log("Simulation started.");
    this._start_time = Date.now();
    this._game_duration = 0;
    this._totalTime = GAMEPARAMETERS.gameTime * 1000;

    return new RSVP.Queue()
      .push(function () {
        promise_list = [];
        _this._droneList.forEach(function (drone) {
          promise_list.push(drone.internal_start(
            _this._mapManager.getMapInfo().initial_position
          ));
        });
        return RSVP.all(promise_list);
      })
      .push(function () {
        _this._canUpdate = true;
        return _this.finish_deferred.promise;
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

  GameManager.prototype._spawnDrones = function (center, drone_list, ctx) {
    var position, i, position_list = [], max_collision = 10 * drone_list.length,
      collision_nb = 0, api;
    function checkCollision(position, list) {
      var el;
      for (el = 0; el < list.length; el += 1) {
        if (position.equalsWithEpsilon(list[el], 0.5)) {
          return true;
        }
      }
      return false;
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
      position = randomSpherePoint(center.x + i, center.y + i, center.z + i,
                                   0, 0, 0);
      if (checkCollision(position, position_list)) {
        collision_nb += 1;
        if (collision_nb < max_collision) {
          i -= 1;
        }
      } else {
        position_list.push(position);
        api = new this.APIs_dict[drone_list[i].type](
          this,
          drone_list[i],
          GAMEPARAMETERS,
          i
        );
        spawnDrone(position.x, position.y, position.z, i,
                   drone_list[i], api, ctx._scene, ctx._droneList);
      }
    }
  };

  GameManager.prototype.getCurrentTime = function () {
    return this._start_time + this._game_duration;
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

  /*// Resize canvas on window resize
  window.addEventListener('resize', function () {
    engine.resize();
  });*/


}(this));

/******************************************************************************/