/*global BABYLON, RSVP, console, DroneAaileFixeAPI, DroneLogAPI, document*/
/*jslint nomen: true, indent: 2, maxlen: 80, white: true, todo: true,
         unparam: true */

var GAMEPARAMETERS = {};

/******************************* DRONE MANAGER ********************************/
var DroneManager = /** @class */ (function () {
  "use strict";

  //** CONSTRUCTOR
  function DroneManager(scene, id, API) {
    this._mesh = null;
    this._controlMesh = null;
    this._canPlay = false;
    this._canCommunicate = false;
    this._maxAcceleration = 0;
    this._maxSpeed = 0;
    this._speed = 0;
    this._acceleration = 0;
    this._direction = BABYLON.Vector3.Zero();
    this._maxOrientation = Math.PI / 4;
    this._scene = scene;
    this._canUpdate = true;
    this._id = id;
    this._leader_id = 0;
    this._API = API; // var API created on AI evel
    // Create the control mesh
    this._controlMesh = BABYLON.Mesh.CreateBox(
      "droneControl_" + id, 0.01, this._scene);
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
    return new BABYLON.Vector3(vector.x, vector.z, vector.y);
  };
  Object.defineProperty(DroneManager.prototype, "leader_id", {
    get: function () { return this._leader_id; },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "drone_dict", {
    get: function () { return this._API._drone_dict_list; },
    enumerable: true,
    configurable: true
  });
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
  Object.defineProperty(DroneManager.prototype, "direction", {
    get: function () { return this._swapAxe(this._direction); },
    enumerable: true,
    configurable: true
  });
  Object.defineProperty(DroneManager.prototype, "worldDirection", {
    get: function () {
      return new BABYLON.Vector3(
        this._direction.x, this._direction.y, this._direction.z);
    },
    enumerable: true,
    configurable: true
  });
  DroneManager.prototype.internal_start = function () {
      this._maxAcceleration = GAMEPARAMETERS.drone.maxAcceleration;
      this._maxSpeed = this._API.getMaxSpeed();
      this._API.internal_start();
      this._canPlay = true;
      this._canCommunicate = true;
      try {
        return this.onStart();
      } catch (error) {
        console.warn('Drone crashed on start due to error:', error);
        this._internal_crash(error);
      }
  };
  /**
   * Set a target point to move
   */
  DroneManager.prototype.setTargetCoordinates = function (x, y, z) {
    if (!this._canPlay) {
      return;
    }
    return this._API.internal_setTargetCoordinates(this, x, y, z);
  };
  DroneManager.prototype.internal_update = function (delta_time) {
    var context = this, updateSpeed;
    if (this._controlMesh) {
      context._speed += context._acceleration * delta_time / 1000;
      if (context._speed > context._maxSpeed) {
        context._speed = context._maxSpeed;
      }
      if (context._speed < -context._maxSpeed) {
        context._speed = -context._maxSpeed;
      }
      updateSpeed = context._speed * delta_time / 1000;
      if (context._direction.x !== 0 ||
          context._direction.y !== 0 ||
          context._direction.z !== 0) {
        context._controlMesh.position.addInPlace(new BABYLON.Vector3(
          context._direction.x * updateSpeed,
          context._direction.y * updateSpeed,
          context._direction.z * updateSpeed));
      }
      context._controlMesh.computeWorldMatrix(true);
      context._mesh.computeWorldMatrix(true);
      if (context._canUpdate) {
        context._canUpdate = false;
        return new RSVP.Queue()
          .push(function () {
            return context.onUpdate(context._API._gameManager._game_duration);
          })
          .push(function () {
            context._canUpdate = true;
          }, function (error) {
            console.warn('Drone crashed on update due to error:', error);
            context._internal_crash(error);
          })
          .push(function () {
            context._API.internal_update(context);
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
    if(isNaN(x) || isNaN(y) || isNaN(z)){
      throw new Error('Position coordinates must be numbers');
    }
    if (!this._canPlay) {
      if (z <= 0.05) {
        z = 0.05;
      }
      this._controlMesh.position = new BABYLON.Vector3(x, z, y);
    }
    this._controlMesh.computeWorldMatrix(true);
    this._mesh.computeWorldMatrix(true);
  };
  DroneManager.prototype.setAcceleration = function (factor) {
    if (!this._canPlay) {
      return;
    }
    if (isNaN(factor)){
      throw new Error('Acceleration must be a number');
    }
    if (factor > this._maxAcceleration) {
      factor = this._maxAcceleration;
    }
    this._acceleration = factor;
  };
  DroneManager.prototype.setDirection = function (x, y, z) {
    if (!this._canPlay) {
      return;
    }
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
      throw new Error('Direction coordinates must be numbers');
    }
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
      return this._API.getCurrentPosition(
        this._controlMesh.position.x,
        this._controlMesh.position.z,
        this._controlMesh.position.y
      );
    }
    return null;
  };
  DroneManager.prototype.setAltitude = function (altitude) {
    if (!this._canPlay) {
      return;
    }
    return this._API.setAltitude(altitude, this);
  };
  /**
   * Make the drone loiter (circle with a set radius)
   */
  DroneManager.prototype.loiter = function (radius) {
    if (!this._canPlay) {
      return;
    }
    this._API.set_loiter_mode(radius);
  };
  DroneManager.prototype.getFlightParameters = function () {
    if (this._API.getFlightParameters) {
      return this._API.getFlightParameters();
    }
    return null;
  };
  DroneManager.prototype.getYaw = function () {
    return 0;
  };
  DroneManager.prototype.triggerParachute = function () {
    return this._API.triggerParachute(this);
  };
  DroneManager.prototype.exit = function () {
    this._internal_crash();
    return this._API.exit();
  };
  DroneManager.prototype.landed = function () {
    return this._API.landed(this);
  };
  /**
   * Set the drone last checkpoint reached
   * @param checkpoint to be set
   */
  DroneManager.prototype.setCheckpoint = function (checkpoint) {
    return checkpoint;
  };
  /**
   * Function called on game start
   */
  DroneManager.prototype.onStart = function () { return;};
  /**
   * Function called on game update
   * @param timestamp The tic value
   */
  DroneManager.prototype.onUpdate = function () { return;};
  /**
   * Function called when drone crashes
   */
  DroneManager.prototype.onTouched = function () { return;};
  /**
   * Function called when a message is received
   * @param msg The message
   */
  DroneManager.prototype.onGetMsg = function () { return;};
  return DroneManager;
}());

/******************************************************************************/



/******************************** MAP MANAGER *********************************/

var MapManager = /** @class */ (function () {
  "use strict";
  function calculateMapInfo(map, map_dict, initial_position) {
    var max_width = map.latLonDistance([map_dict.min_lat, map_dict.min_lon],
                                       [map_dict.min_lat, map_dict.max_lon]),
      max_height = map.latLonDistance([map_dict.min_lat, map_dict.min_lon],
                                      [map_dict.max_lat, map_dict.min_lon]),
      map_size = Math.ceil(Math.max(max_width, max_height)) * 0.6,
      map_info = {
        "depth": map_size,
        "height": map_dict.height,
        "width": map_size,
        "map_size": map_size,
        "min_x": map.longitudToX(map_dict.min_lon, map_size),
        "min_y": map.latitudeToY(map_dict.min_lat, map_size),
        "max_x": map.longitudToX(map_dict.max_lon, map_size),
        "max_y": map.latitudeToY(map_dict.max_lat, map_size),
        "start_AMSL": map_dict.start_AMSL
      },
      position = map.normalize(
        map.longitudToX(initial_position.longitude, map_size),
        map.latitudeToY(initial_position.latitude, map_size),
        map_info);
    map_info.initial_position = {
      "x": position[0],
      "y": position[1],
      "z": initial_position.z
    };
    return map_info;
  }
  //** CONSTRUCTOR
  function MapManager(scene) {
    var _this = this, max_sky, skybox, skyboxMat, largeGroundMat,
      largeGroundBottom, width, depth, terrain, max;
    _this.map_info = calculateMapInfo(_this, GAMEPARAMETERS.map,
                                      GAMEPARAMETERS.initialPosition);
    max = _this.map_info.width;
    if (_this.map_info.depth > max) {
      max = _this.map_info.depth;
    }
    if (_this.map_info.height > max) {
      max = _this.map_info.height;
    }
    max = max < _this.map_info.depth ? _this.map_info.depth : max;
    // Skybox
    max_sky = (max * 10 < 20000) ? max * 10 : 20000;
    skybox = BABYLON.Mesh.CreateBox("skyBox", max_sky, scene);
    skybox.infiniteDistance = true;
    skybox.renderingGroupId = 0;
    skyboxMat = new BABYLON.StandardMaterial("skybox", scene);
    skyboxMat.backFaceCulling = false;
    skyboxMat.disableLighting = true;
    skyboxMat.reflectionTexture = new BABYLON.CubeTexture("./assets/skybox/sky",
                                                          scene);
    skyboxMat.reflectionTexture.coordinatesMode = BABYLON.Texture.SKYBOX_MODE;
    skyboxMat.infiniteDistance = true;
    skybox.material = skyboxMat;
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
    // Camera
    scene.activeCamera.upperRadiusLimit = max * 4;
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
  }
  MapManager.prototype.getMapInfo = function () {
    return this.map_info;
  };
  MapManager.prototype.longitudToX = function (lon, map_size) {
    return (map_size / 360.0) * (180 + lon);
  };
  MapManager.prototype.latitudeToY = function (lat, map_size) {
    return (map_size / 180.0) * (90 - lat);
  };
  MapManager.prototype.latLonDistance = function (c1, c2) {
    var R = 6371e3,
      q1 = c1[0] * Math.PI / 180,
      q2 = c2[0] * Math.PI / 180,
      dq = (c2[0] - c1[0]) * Math.PI / 180,
      dl = (c2[1] - c1[1]) * Math.PI / 180,
      a = Math.sin(dq / 2) * Math.sin(dq / 2) +
        Math.cos(q1) * Math.cos(q2) *
        Math.sin(dl / 2) * Math.sin(dl / 2),
      c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };
  MapManager.prototype.normalize = function (x, y, map_dict) {
    var n_x = (x - map_dict.min_x) / (map_dict.max_x - map_dict.min_x),
      n_y = (y - map_dict.min_y) / (map_dict.max_y - map_dict.min_y);
    return [n_x * 1000 - map_dict.width / 2,
            n_y * 1000 - map_dict.depth / 2];
  };
  MapManager.prototype.convertToGeoCoordinates = function (x, y, z, map_dict) {
    var lon = x + map_dict.width / 2,
      lat = y + map_dict.depth / 2;
    lon = lon / 1000;
    lon = lon * (map_dict.max_x - map_dict.min_x) +
      map_dict.min_x;
    lon = lon / (map_dict.width / 360.0) - 180;
    lat = lat / 1000;
    lat = lat * (map_dict.max_y - map_dict.min_y) +
      map_dict.min_y;
    lat = 90 - lat / (map_dict.depth / 180.0);
    return {
      x: lat,
      y: lon,
      z: z
    };
  };
  return MapManager;
}());

/******************************************************************************/



/******************************** GAME MANAGER ********************************/

var GameManager = /** @class */ (function () {
  "use strict";
  // *** CONSTRUCTOR ***
  function GameManager(canvas, game_parameters_json) {
    var drone, header_list;
    this._canvas = canvas;
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
      header_list = ["timestamp;", "latitude;", "longitude;", "AMSL (m);",
                     "rel altitude (m);", "pitch (Â°);", "roll(Â°);",
                     "yaw(Â°);", "air speed (m/s);", "throttle(%);",
                     "climb rate(m/s)"];
      for (drone = 0; drone < GAMEPARAMETERS.droneList.length; drone+=1) {
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
      DroneAaileFixeAPI: DroneAaileFixeAPI,
      DroneLogAPI: DroneLogAPI
    };
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
        return gadget._flight_log;
      });
  };

  GameManager.prototype.update = function () {
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
        _this.ongoing_update_promise = _this._update(
          TIME_DELTA, (_this.waiting_update_count === 1))
          .push(function () {
            _this.waiting_update_count -= 1;
            _this.ongoing_update_promise = null;
            triggerUpdateIfPossible();
          })
          .push(undefined, function(error) {
            console.log("ERROR on update:", error);
            console.log("rejecting finish_deferred promise...");
            _this.finish_deferred.reject.bind(_this.finish_deferred);
          });
      }
    }
    triggerUpdateIfPossible();
  };

  GameManager.prototype.delay = function (callback, millisecond) {
    this._delayed_defer_list.push([callback, millisecond]);
  };

  GameManager.prototype.logError = function (drone, error) {
    this._flight_log[drone._id].push(error.stack);
  };

  GameManager.prototype._checkDroneRules = function (drone) {
    //TODO move this to API methods
    if (drone.getCurrentPosition()) {
      return drone.getCurrentPosition().z > 1;
    }
    return false;
  };

  GameManager.prototype._update = function (delta_time) {
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

    this._droneList.forEach(function (drone) {
      queue.push(function () {
        drone._tick += 1;
        if (_this._checkDroneRules(drone)) {
          return drone.internal_update(delta_time);
        }
        //TODO error must be defined by the api?
        drone._internal_crash('Drone touched the floor');
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
    var seconds = Math.floor(this._game_duration / 1000), drone,
      drone_position, map_info, geo_coordinates, position_obj, material, color;
    if (GAMEPARAMETERS.log_drone_flight || GAMEPARAMETERS.draw_flight_path) {
      for (drone = 0; drone < GAMEPARAMETERS.droneList.length; drone+=1) {
        if (this._droneList[drone].can_play) {
          drone_position = this._droneList[drone].position;
          if (GAMEPARAMETERS.log_drone_flight) {
            map_info = this._mapManager.getMapInfo();
            if (this._log_count[drone] === 0 ||
                this._game_duration / this._log_count[drone] > 1) {
              this._log_count[drone] += GAMEPARAMETERS.log_interval_time;
              geo_coordinates = this._mapManager.convertToGeoCoordinates(
                drone_position.x, drone_position.y, drone_position.z, map_info);
              this._flight_log[drone].push(
                [this._game_duration, geo_coordinates.x, geo_coordinates.y,
                 map_info.start_AMSL + drone_position.z, drone_position.z]);
            }
          }
          if (GAMEPARAMETERS.draw_flight_path) {
            //draw drone position every some seconds
            if (seconds - this._last_position_drawn[drone] > 0.2) {
              this._last_position_drawn[drone] = seconds;
              position_obj = BABYLON.MeshBuilder.CreateBox("obs_" + seconds,
                                                           { size: 1 },
                                                           this._scene);
              position_obj.position = new BABYLON.Vector3(drone_position.x,
                                                          drone_position.z,
                                                          drone_position.y);
              position_obj.scaling = new BABYLON.Vector3(4, 4, 4);
              material = new BABYLON.StandardMaterial(this._scene);
              material.alpha = 1;
              color = new BABYLON.Color3(255, 0, 0);
              if (this._colors[drone]) {
                color = this._colors[drone];
              }
              material.diffuseColor = color;
              position_obj.material = material;
              if (GAMEPARAMETERS.temp_flight_path) {
                if (this._trace_objects_per_drone[drone].length === 10) {
                  this._trace_objects_per_drone[drone][0].dispose();
                  this._trace_objects_per_drone[drone].splice(0, 1);
                }
                this._trace_objects_per_drone[drone].push(position_obj);
              }
            }
          }
        }
      }
    }
  };

  GameManager.prototype._timeOut = function () {
    var seconds = Math.floor(this._game_duration / 1000);
    return this._totalTime - seconds <= 0;
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
    var _this = this, canvas, hemi_north, hemi_south, camera, on3DmodelsReady;
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
    this._scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
    //removed for event handling
    //this._engine.enableOfflineSupport = false;
    //this._scene.collisionsEnabled = true;
    // Lights
    hemi_north = new BABYLON.HemisphericLight(
      "hemiN", new BABYLON.Vector3(1, -1, 1), this._scene);
    hemi_north.intensity = 0.75;
    hemi_south = new BABYLON.HemisphericLight(
      "hemiS", new BABYLON.Vector3(-1, 1, -1), this._scene);
    hemi_south.intensity = 0.75;
    camera = new BABYLON.ArcRotateCamera("camera", 0, 1.25, 800,
                                         BABYLON.Vector3.Zero(), this._scene);
    camera.wheelPrecision = 10;
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
      _this._mapManager = new MapManager(ctx._scene);
      ctx._spawnDrones(_this._mapManager.map_info.initial_position,
                       GAMEPARAMETERS.droneList, ctx);
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //Hack to make advanced texture work
      var documentTmp = document, advancedTexture, count,
          controlMesh, rect, label;
      document = undefined;
      advancedTexture = BABYLON.GUI.AdvancedDynamicTexture
      .CreateFullscreenUI("UI", true, ctx._scene);
      document = documentTmp;
      for (count = 0; count < GAMEPARAMETERS.droneList.length; count+=1) {
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
    this._game_duration = 0;
    this._totalTime = GAMEPARAMETERS.gameTime;

    return new RSVP.Queue()
      .push(function () {
        promise_list = [];
        _this._droneList.forEach(function (drone) {
          drone._tick = 0;
          promise_list.push(drone.internal_start());
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
    function spawnDrone(x, y, z, index, drone_info, api) {
      var default_drone_AI = api.getDroneAI(), code, base, code_eval;
      if (default_drone_AI) {
        code = default_drone_AI;
      } else {
        code = drone_info.script_content;
      }
      code_eval = "let drone = new DroneManager(ctx._scene, " +
          index + ', api);' +
          "let droneMe = function(NativeDate, me, Math, window, DroneManager," +
          " GameManager, DroneLogAPI, DroneAaileFixeAPI, BABYLON, " +
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
      base = code_eval;
      code_eval += code + "}; droneMe(Date, drone, Math, {});";
        base += "};ctx._droneList.push(drone)";
        code_eval += "ctx._droneList.push(drone)";
      /*jslint evil: true*/
      try {
        eval(code_eval);
      }
      catch (error) {
        eval(base);
      }
      /*jslint evil: false*/
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
      }
      else {
        position_list.push(position);
        api = new this.APIs_dict[drone_list[i].type](
          this, drone_list[i], GAMEPARAMETERS, i);
        spawnDrone(position.x, position.y, position.z, i,
                   drone_list[i], api);
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

  updateGame = function () {
    if (game_manager_instance) {
      return game_manager_instance.update();
    }
  };

  /*// Resize canvas on window resize
  window.addEventListener('resize', function () {
    engine.resize();
  });*/


}(this));

/******************************************************************************/