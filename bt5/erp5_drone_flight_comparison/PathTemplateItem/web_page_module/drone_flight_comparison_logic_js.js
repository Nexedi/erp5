/*global GameManager, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

/*********************** DRONE SIMULATOR LOGIC ********************************/

var runGame, updateGame, game_manager_instance;
var SIMULATION_SPEED = 10;

(function () {
  "use strict";
  console.log('game logic');

  runGame = function (canvas, script, log) {

    var game_parameters_json = {
      "drone": {
        "maxAcceleration": 1,
        "maxSpeed": 16.666667
      },
      "gameTime": 1800,
      "latency": {
        "information": 0,
        "communication": 0
      },
      "initialPosition": {
        "x": 0,
        "y": 0,
        "z": 20
      },
      "droneList": ["DroneAaileFixeAPI", "DroneLogAPI"]
    };

    function processLog(game_parameters_json, log) {
      var MAP_SIZE,
        MIN_HEIGHT = 15,
        MIN_X,
        MAX_X,
        MIN_Y,
        MAX_Y,
        SPEED_FACTOR = 0.75,
        log_point_list = [],
        converted_log_point_list = [];
      function longitudToX(lon) {
        return (MAP_SIZE / 360.0) * (180 + lon);
      }
      function latitudeToY(lat) {
        return (MAP_SIZE / 180.0) * (90 - lat);
      }
      function normalizeToMap(x, y) {
        var n_x = (x - MIN_X) / (MAX_X - MIN_X),
          n_y = (y - MIN_Y) / (MAX_Y - MIN_Y);
        return [n_x * 1000 - MAP_SIZE / 2, n_y * 1000 - MAP_SIZE / 2];
      }
      function latLonDistance(c1, c2) {
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
      }
      function distance(p1, p2) {
        return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                         Math.pow(p1[1] - p2[1], 2));
      }
      var path_point_list = [], max_width, max_height,
        line_list = log.split('\n'), log_entry_list = [],
        i, start_time, end_time, log_entry, splitted_log_entry,
        lat, lon, x, y, position, min_lon = 99999, min_lat = 99999,
        max_lon = 0, max_lat = 0, previous, start_position, dist = 0,
        path_point, average_speed = 0, flight_time, log_interval_time,
        previous_log_time, height, timestamp, log_header_found, time_offset = 1,
        flight_dist = 0, start_AMSL = 0;
      for (i = 0; i < line_list.length; i += 1) {
        if (!log_header_found && !line_list[i].includes("timestamp;")) {
          continue;
        } else {
          log_header_found = true;
        }
        if (line_list[i].indexOf("AMSL") >= 0 ||
            !line_list[i].includes(";")) {
          continue;
        }
        log_entry = line_list[i].trim();
        if (log_entry) {
          log_entry_list.push(log_entry);
          splitted_log_entry = log_entry.split(";");
          lat = parseFloat(splitted_log_entry[1]);
          lon = parseFloat(splitted_log_entry[2]);
          //get min and max lat and lon
          if (lon < min_lon) {
            min_lon = lon;
          }
          if (lat < min_lat) {
            min_lat = lat;
          }
          if (lon > max_lon) {
            max_lon = lon;
          }
          if (lat > max_lat) {
            max_lat = lat;
          }
        }
      }
      //get map size from max distance
      max_width = latLonDistance([min_lat, min_lon], [min_lat, max_lon]);
      max_height = latLonDistance([min_lat, min_lon], [max_lat, min_lon]);
      MAP_SIZE = Math.ceil(Math.max(max_width, max_height)) * 0.6;
      MIN_X = longitudToX(min_lon);
      MAX_X = longitudToX(max_lon);
      MIN_Y = latitudeToY(min_lat);
      MAX_Y = latitudeToY(max_lat);
      if (log_entry_list[0] && log_entry_list[1]) {
        var entry_1 = log_entry_list[0].split(";"),
          entry_2 = log_entry_list[1].split(";"),
          interval = parseInt(entry_2[0], 10) - parseInt(entry_1[0], 10);
        //if interval > 1' then timestamp is in microseconds
        if (Math.floor(interval / 1000) > 60) {
          time_offset = 1000;
        }
      }
      for (i = 0; i < log_entry_list.length; i += 1) {
        splitted_log_entry = log_entry_list[i].split(";");
        timestamp = parseInt(splitted_log_entry[0], 10);
        if (i === 0) {
          log_interval_time = 0;
          start_time = timestamp;
        } else {
          log_interval_time += (parseInt(splitted_log_entry[0], 10) -
            previous_log_time);
        }
        previous_log_time = parseInt(splitted_log_entry[0], 10);
        average_speed += parseFloat(splitted_log_entry[8]);
        lat = parseFloat(splitted_log_entry[1]);
        lon = parseFloat(splitted_log_entry[2]);
        if (i === log_entry_list.length - 1) {
          end_time = timestamp;
        }
        height = parseFloat(splitted_log_entry[4]);
        if (height < MIN_HEIGHT) {
          height = MIN_HEIGHT;
        } else {
          height = height;
        }
        x = longitudToX(lon);
        y = latitudeToY(lat);
        position = normalizeToMap(x, y);
        if (!previous) {
          start_AMSL = parseFloat(splitted_log_entry[3]);
          start_position = position;
          start_position.push(height);
          previous = position;
        }
        dist = distance(previous, position);
        flight_dist += dist;
        if (dist > 15) {
          previous = position;
          path_point = {
            "type": "box",
            "position": {
              "x": position[0],
              "y": position[1],
              "z": height
            },
            "scale": {
              "x": 3.5,
              "y": 3.5,
              "z": 3.5
            },
            "color": {
              "r": 0,
              "g": 255,
              "b": 0
            },
            "timestamp": timestamp
          };
          path_point_list.push(path_point);
        }
        converted_log_point_list.push([position[0],
                                      position[1],
                                      height, timestamp / time_offset]);
        log_point_list.push([parseFloat(splitted_log_entry[1]),
                            parseFloat(splitted_log_entry[2]),
                            height, timestamp]);
      }
      average_speed = average_speed / log_entry_list.length;
      log_interval_time = log_interval_time / log_entry_list.length / time_offset;
      flight_time = (end_time - start_time) / 1000 / time_offset;
      //TODO refactor this
      game_parameters_json.compareFlights = {
        log: true,
        draw: true,
        map_width: MAP_SIZE,
        map_height: MAP_SIZE,
        MAP_SIZE: MAP_SIZE,
        MIN_X: MIN_X,
        MAX_X: MAX_X,
        MIN_Y: MIN_Y,
        MAX_Y: MAX_Y,
        start_AMSL: start_AMSL,
        flight_time: flight_time,
        average_speed: average_speed,
        log_interval_time: log_interval_time,
        path: path_point_list,
        full_log: log_point_list,
        converted_log_point_list: converted_log_point_list
      };
      game_parameters_json.drone.maxSpeed = (flight_dist / flight_time) * SPEED_FACTOR;
      game_parameters_json.flight_path_point_list = path_point_list;
      game_parameters_json.initialPosition.x = start_position[0];
      game_parameters_json.initialPosition.y = start_position[1];
      game_parameters_json.initialPosition.z = start_position[2];
      game_parameters_json.gameTime = flight_time;
      //give map some margin from flight limits
      MAP_SIZE *= 1.10;
      game_parameters_json.mapSize = {
        "depth": MAP_SIZE,
        "height": 100,
        "width": MAP_SIZE
      }
      return game_parameters_json;
    }

    game_parameters_json = processLog(game_parameters_json, log);

    if (!game_manager_instance) {
      game_manager_instance = new GameManager(canvas, script,
                                              game_parameters_json,
                                              SIMULATION_SPEED
                                             );
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



/******************************** GAME MANAGER ********************************/

var GAMEPARAMETERS = {};

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

var GameManager = /** @class */ (function () {
  // *** CONSTRUCTOR ***
  function GameManager(canvas, script, game_parameters_json, simulation_speed) {
    var _this = this;
    this._canvas = canvas;
    this._scene = null;
    this._engine = null;
    this._droneList = [];
    this._canUpdate = false;
    if (!simulation_speed) { simulation_speed = 5; }
    this._max_step_animation_frame = simulation_speed;
    Object.assign(GAMEPARAMETERS, game_parameters_json);
    this._game_parameters_json = game_parameters_json;
    this._map_swapped = false;
    this._script = script;
    this._last_position_drawn = [];
    this._log_count = [];
    this._flight_log = [];
    if (GAMEPARAMETERS.compareFlights) {
      for (var count = 0; count < GAMEPARAMETERS.droneList.length; count++) {
        this._flight_log[count] = [];
        this._log_count[count] = 0;
        this._last_position_drawn[count] = null;
      }
      this._colors = [
        new BABYLON.Color3(255, 165, 0),
        new BABYLON.Color3(0, 0, 255),
        new BABYLON.Color3(255, 0, 0),
        new BABYLON.Color3(0, 255, 0)
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
        //TODO return result
        gadget._final_score = "fake-result 000";
        return gadget._final_score;
      });
  };

  GameManager.prototype.update = function () {
    var _this = this;
    // time delta means that drone are updated every virtual second
    // This is fixed and must not be modified
    // otherwise, it will lead to different scenario results
    // (as drone calculations may be triggered less often)
    var TIME_DELTA = 1000 / 60, i;
    // init the value on the first step
    _this.waiting_update_count = _this._max_step_animation_frame;
    function triggerUpdateIfPossible() {
      if ((_this._canUpdate) && (_this.ongoing_update_promise === null) && (0 < _this.waiting_update_count)) {
        _this.ongoing_update_promise = _this._update(TIME_DELTA, (_this.waiting_update_count === 1))
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

  GameManager.prototype._update = function (delta_time, update_dom) {
    var _this = this,
      queue = new RSVP.Queue(),
      i;
    this._updateDisplayedInfo(delta_time, update_dom);

    // trigger all deferred calls if it is time
    for (i = _this._delayed_defer_list.length - 1; 0 <= i; i -= 1) {
      _this._delayed_defer_list[i][1] = _this._delayed_defer_list[i][1] - delta_time;
      if (_this._delayed_defer_list[i][1] <= 0) {
        queue.push(_this._delayed_defer_list[i][0]);
        _this._delayed_defer_list.splice(i, 1);
      }
    }

    this._droneList.forEach(function (drone) {
      queue.push(function () {
        drone._tick += 1; //TODO don't access _tick, use an API method
        return drone.internal_update(delta_time);
      });
    });

    return queue
      .push(function () {
        if (_this._timeOut()) {
          console.log("TIMEOUT!");
          return _this._finish();
        }
      });
  };

  GameManager.prototype._updateDisplayedInfo = function (delta_time, update_dom) {
    this._game_duration += delta_time;
    var seconds = Math.floor(this._game_duration / 1000);
    if (GAMEPARAMETERS.compareFlights) {
      for (var count = 0; count < GAMEPARAMETERS.droneList.length; count++) {
        if (this._droneList[count].can_play) {
          var drone_position_x = this._droneList[count].position.x,
            drone_position_y = this._droneList[count].position.y,
            drone_position_z = this._droneList[count].position.z;
          if (GAMEPARAMETERS.compareFlights.log) {
            if (this._log_count[count] === 0 || this._game_duration / this._log_count[count] > 1) {
              this._log_count[count] += GAMEPARAMETERS.compareFlights.log_interval_time;
              //convert x-y coordinates into latitud-longitude
              var lon = drone_position_x + GAMEPARAMETERS.compareFlights.map_width / 2;
              lon = lon / 1000;
              lon = lon * (GAMEPARAMETERS.compareFlights.MAX_X - GAMEPARAMETERS.compareFlights.MIN_X) + GAMEPARAMETERS.compareFlights.MIN_X;
              lon = lon / (GAMEPARAMETERS.compareFlights.map_width / 360.0) - 180;
              var lat = drone_position_y + GAMEPARAMETERS.compareFlights.map_height / 2;
              lat = lat / 1000;
              lat = lat * (GAMEPARAMETERS.compareFlights.MAX_Y - GAMEPARAMETERS.compareFlights.MIN_Y) + GAMEPARAMETERS.compareFlights.MIN_Y;
              lat = 90 - lat / (GAMEPARAMETERS.compareFlights.map_height / 180.0);
              this._flight_log[count].push([lat, lon, drone_position_z]);
            }
          }
          if (GAMEPARAMETERS.compareFlights.draw) { //TODO review this in JSON dict
            //draw drone position every second
            if (this._last_position_drawn[count] !== seconds) {
              this._last_position_drawn[count] = seconds;
              var position_obj = BABYLON.MeshBuilder.CreateSphere("obs_" + seconds, {
                  'diameterX': 3.5,
                  'diameterY': 3.5,
                  'diameterZ': 3.5
              }, this._scene);
              position_obj.position = new BABYLON.Vector3(drone_position_x, drone_position_z, drone_position_y);
              position_obj.scaling = new BABYLON.Vector3(3.5, 3.5, 3.5);
              var material = new BABYLON.StandardMaterial(this._scene);
              material.alpha = 1;
              var color = new BABYLON.Color3(255, 0, 0);
              if (this._colors[count]) {
                color = this._colors[count];
              }
              material.diffuseColor = color;
              position_obj.material = material;
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
    var _this = this;
    this._delayed_defer_list = [];
    this._dispose();
    var canvas = this._canvas;
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
    var hemi_north = new BABYLON.HemisphericLight(
      "hemiN", new BABYLON.Vector3(1, -1, 1), this._scene);
    hemi_north.intensity = 0.75;
    var hemi_south = new BABYLON.HemisphericLight(
      "hemiS", new BABYLON.Vector3(-1, 1, -1), this._scene);
    hemi_south.intensity = 0.75;
    var camera = new BABYLON.ArcRotateCamera("camera", 0, 1.25, 800,
                                         BABYLON.Vector3.Zero(), this._scene);
    camera.wheelPrecision = 10;
    //changed for event handling
    //camera.attachControl(this._scene.getEngine().getRenderingCanvas()); //original
    camera.attachControl(canvas, true);
    camera.maxz = 40000;
    this._camera = camera;

    // Render loop
    this._engine.runRenderLoop(function () {
      _this._scene.render();
    });
    // -------------------------------- SIMULATION - Prepare API, Map and Teams
    var on3DmodelsReady = function (ctx) {
      // Get the game parameters
      if (!ctx._map_swapped) {
        GAMEPARAMETERS = ctx._getGameParameter();
        ctx._map_swapped = true;
      }
      // Init the map
      _this._mapManager = new MapManager(ctx._scene);
      ctx._spawnDrones(GAMEPARAMETERS.initialPosition,
                       GAMEPARAMETERS.droneList, ctx._script);
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //Hack to make advanced texture work
      const documentTmp = document;
      document = undefined;
      var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI", true, ctx._scene);
      document = documentTmp;
      for (var count = 0; count < GAMEPARAMETERS.droneList.length; count++) { //TODO use one color per drone
        var controlMeshBlue = ctx._droneList[count].infosMesh; //TODO check
        var rectBlue = new BABYLON.GUI.Rectangle();
        rectBlue.width = "10px";
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
        return result.push(_this._start.bind(_this));
      });
  };

  GameManager.prototype._start = function () {
    var _this = this;
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
          drone._tick = 0; //TODO don't access _tick, use an API method
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
    var _this = this, droneTask, mapTask, obstacleTask,
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
    var parameter = {}, i,
      swap = function (pos) {
        return {
          x: pos.x,
          y: pos.z,
          z: pos.y
        };
      };
    Object.assign(parameter, this._game_parameters_json);
    this._gameParameter = {};
    Object.assign(this._gameParameter, this._game_parameters_json);
    for (i = 0; i < parameter.flight_path_point_list.length; i += 1) {
      parameter.flight_path_point_list[i].position =
        swap(parameter.flight_path_point_list[i].position);
      if (parameter.flight_path_point_list[i].scale) {
        parameter.flight_path_point_list[i].scale =
          swap(parameter.flight_path_point_list[i].scale);
      }
    }
    return parameter;
  };

  GameManager.prototype._spawnDrones = function (center, drone_list, code) {
    var position, i, position_list = [], max_collision = 10 * drone_list.length,
      collision_nb = 0;
    function checkCollision(position, list) {
      var i;
      for (i = 0; i < list.length; i += 1) {
        if (position.equalsWithEpsilon(list[i], 0.5)) {
          return true;
        }
      }
      return false;
    }
    function spawnDrone(x, y, z, index, api, code, ctx) {
      var default_drone_AI = api.getDroneAI();
      if (default_drone_AI) {
        code = default_drone_AI;
      }
      var base, code_eval = "let drone = new DroneManager(ctx._scene, " +
          index + ', api);' +
          "let droneMe = function(NativeDate, me, Math, window, DroneManager, GameManager, DroneLogAPI, DroneAaileFixeAPI, BABYLON, GAMEPARAMETERS) {" +
          "var start_time = (new Date(2070, 0, 0, 0, 0, 0, 0)).getTime();" +
          "Date.now = function () {return start_time + drone._tick * 1000/60;}; " +
          "function Date() {if (!(this instanceof Date)) {throw new Error('Missing new operator');} " +
          "if (arguments.length === 0) {return new NativeDate(Date.now());} else {return new NativeDate(...arguments);}}";
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
      try {
        eval(code_eval);
      }
      catch (error) {
        eval(base);
      }
    }
    for (i = 0; i < drone_list.length; i += 1) {
      position = randomSpherePoint(center.x + i, center.y + i, center.z + i, 0, 0, 0);
      if (checkCollision(position, position_list) || position.z < 0.05) {
        collision_nb += 1;
        if (collision_nb < max_collision) {
          i -= 1;
        }
      }
      else {
        position_list.push(position);
        var api = new this.APIs_dict[drone_list[i]](this, GAMEPARAMETERS.compareFlights);
        spawnDrone(position.x, position.y, position.z, i, api, code, this);
      }
    }
  };

  return GameManager;
}());


/*****************************************************************************/


/******************************* DRONE LOG API ********************************/

var DroneLogAPI = /** @class */ (function () {
  //** CONSTRUCTOR
  function DroneLogAPI(gameManager, flight_parameters) {
    this._gameManager = gameManager;
    this._flight_parameters = flight_parameters;
  }
  //TODO test sendMsg (what is iterable _this.team??) (latency.communication?)(GM.delay?)
  DroneLogAPI.prototype.internal_sendMsg = function (msg, to) {
    var _this = this;
    _this._gameManager.delay(function () {
      if (to < 0) {
        // Send to all drones
        _this.team.forEach(function (drone) {
          if (drone.infosMesh) {
            try {
              drone.onGetMsg(msg);
            }
            catch (error) {
              console.warn('Drone crashed on sendMsg due to error:', error);
              drone._internal_crash();
            }
          }
        });
      }
      else {
        // Send to specific drone
        if (drone.infosMesh) {
          try {
            _this.team[to].onGetMsg(msg);
          }
          catch (error) {
            console.warn('Drone crashed on sendMsg due to error:', error);
            _this.team[to]._internal_crash();
          }
        }
      }
    }, GAMEPARAMETERS.latency.communication);
  };
  DroneLogAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  DroneLogAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "mapSize"].includes(name))
      return this._gameManager.gameParameter[name];
  };
  DroneLogAPI.prototype.processCoordinates = function (x, y, z) {
    if(isNaN(x) || isNaN(y) || isNaN(z)){
      throw new Error('Target coordinates must be numbers');
    }
    return {
      x: x,
      y: y,
      z: z
    };
  };
  //Internal AI: drone follows the flight log points
  DroneLogAPI.prototype.getDroneAI = function () {
    return 'function distance(p1, p2) {' +
      'var a = p1[0] - p2[0],' +
      'b = p1[1] - p2[1];' +
      'return Math.sqrt(a * a + b * b);' +
      '}' +
      'me.onStart = function() {' +
      'console.log("DRONE LOG START!");' +
      'if (!me.getFlightParameters())' +
      'throw "DroneLog API must implement getFlightParameters";' +
      'me.flightParameters = me.getFlightParameters();' +
      'me.checkpoint_list = me.flightParameters.converted_log_point_list;' +
      'me.startTime = new Date();' +
      'me.initTimestamp = me.flightParameters.converted_log_point_list[0][3];' +
      'me.setTargetCoordinates(me.checkpoint_list[0][0], me.checkpoint_list[0][1], me.checkpoint_list[0][2]);' +
      'me.last_checkpoint_reached = -1;' +
      'me.setAcceleration(10);' +
      '};' +
      'me.onUpdate = function () {' +
      'var next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
      'if (distance([me.position.x, me.position.y], next_checkpoint) < 12) {' +
      'var log_elapsed = next_checkpoint[3] - me.initTimestamp,' +
      'time_elapsed = new Date() - me.startTime;' +
      'if (time_elapsed < log_elapsed) {' +
      'me.setDirection(0, 0, 0);' +
      'return;' +
      '}' +
      'if (me.last_checkpoint_reached + 1 === me.checkpoint_list.length - 1) {' +
      'me.setTargetCoordinates(me.position.x, me.position.y, me.position.z);' +
      'return;' +
      '}' +
      'me.last_checkpoint_reached += 1;' +
      'next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
      '} else {' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
      '}' +
      '};';
  };
  DroneLogAPI.prototype.setAltitude = function (altitude) {
    return altitude;
  };
  DroneLogAPI.prototype.getMaxSpeed = function () {
    return 3000;
  };
  DroneLogAPI.prototype.getInitialAltitude = function () {
    return 0;
  };
  DroneLogAPI.prototype.getAltitudeAbs = function () {
    return 0;
  };
  DroneLogAPI.prototype.getMinHeight = function () {
    return 0;
  };
  DroneLogAPI.prototype.getMaxHeight = function () {
    return 220;
  };
  DroneLogAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return DroneLogAPI;
}());


/*****************************************************************************/


/************************** DRONE A AILE FIXE API ****************************/

TAKEOFF_RADIUS = 60;
LOITER_LIMIT = 30;
LOITER_RADIUS_FACTOR = 0.60;
LOITER_SPEED_FACTOR = 1.5;

var DroneAaileFixeAPI = /** @class */ (function () {
  //** CONSTRUCTOR
  function DroneAaileFixeAPI(gameManager, flight_parameters) {
      this._gameManager = gameManager;
      this._flight_parameters = flight_parameters;
      this._loiter_radius = 0;
      this._last_loiter_point_reached = -1;
      this._last_altitude_point_reached = -1;
  }
  DroneAaileFixeAPI.prototype.internal_sendMsg = function (msg, to) {
    var _this = this;
    _this._gameManager.delay(function () {
      if (to < 0) {
        // Send to all drones
        _this.team.forEach(function (drone) {
          if (drone.infosMesh) {
            try {
              drone.onGetMsg(msg);
            }
            catch (error) {
              console.warn('Drone crashed on sendMsg due to error:', error);
              drone._internal_crash();
            }
          }
        });
      }
      else {
        // Send to specific drone
        if (drone.infosMesh) {
          try {
            _this.team[to].onGetMsg(msg);
          }
          catch (error) {
            console.warn('Drone crashed on sendMsg due to error:', error);
            _this.team[to]._internal_crash();
          }
        }
      }
    }, GAMEPARAMETERS.latency.communication);
  };
  DroneAaileFixeAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  DroneAaileFixeAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "mapSize"].includes(name))
      return this._gameManager.gameParameter[name];
  };
  DroneAaileFixeAPI.prototype.processCoordinates = function (lat, lon, z, r) {
    if(isNaN(lat) || isNaN(lon) || isNaN(z)){
      throw new Error('Target coordinates must be numbers');
    }
    var flightParameters = this.getFlightParameters();
    function longitudToX(lon, flightParameters) {
      return (flightParameters.MAP_SIZE / 360.0) * (180 + lon);
    }
    function latitudeToY(lat, flightParameters) {
      return (flightParameters.MAP_SIZE / 180.0) * (90 - lat);
    }
    function normalizeToMap(x, y, flightParameters) {
      var n_x = (x - flightParameters.MIN_X) / (flightParameters.MAX_X - flightParameters.MIN_X),
        n_y = (y - flightParameters.MIN_Y) / (flightParameters.MAX_Y - flightParameters.MIN_Y);
      return [n_x * 1000 - flightParameters.MAP_SIZE / 2, n_y * 1000 - flightParameters.MAP_SIZE / 2];
    }
    var x = longitudToX(lon, flightParameters),
      y = latitudeToY(lat, flightParameters),
      position = normalizeToMap(x, y, flightParameters);
    if (z > flightParameters.start_AMSL) {
      z -= flightParameters.start_AMSL;
    }
    var processed_coordinates = {
      x: position[0],
      y: position[1],
      z: z
    };
    if (r && r > LOITER_LIMIT) {
      this._loiter_radius = r * LOITER_RADIUS_FACTOR;
      this._loiter_center = processed_coordinates;
      this._loiter_coordinates = [];
      this._last_loiter_point_reached = -1;
      var x1, y1;
      //for (var angle = 0; angle <360; angle+=8){ //counter-clockwise
      for (var angle = 360; angle > 0; angle-=8){ //clockwise
        x1 = this._loiter_radius * Math.cos(angle * (Math.PI / 180)) + this._loiter_center.x;
        y1 = this._loiter_radius * Math.sin(angle * (Math.PI / 180)) + this._loiter_center.y;
        this._loiter_coordinates.push(this.processCurrentPosition(x1, y1, z));
      }
    }
    this._last_altitude_point_reached = -1;
    this.takeoff_path = [];
    return processed_coordinates;
  };
  DroneAaileFixeAPI.prototype.processCurrentPosition = function (x, y, z) {
    //convert x-y coordinates into latitud-longitude
    var flightParameters = this.getFlightParameters();
    var lon = x + flightParameters.map_width / 2;
    lon = lon / 1000;
    lon = lon * (flightParameters.MAX_X - flightParameters.MIN_X) + flightParameters.MIN_X;
    lon = lon / (flightParameters.map_width / 360.0) - 180;
    var lat = y + flightParameters.map_height / 2;
    lat = lat / 1000;
    lat = lat * (flightParameters.MAX_Y - flightParameters.MIN_Y) + flightParameters.MIN_Y;
    lat = 90 - lat / (flightParameters.map_height / 180.0);
    return {
      x: lat,
      y: lon,
      z: z
    };
  };
  DroneAaileFixeAPI.prototype.loiter = function (drone) {
    function distance(c1, c2) {
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
    }
    if (this._loiter_radius > LOITER_LIMIT) {
      var drone_pos = drone.getCurrentPosition();
      //shift loiter circle to nearest point
      if (this._last_loiter_point_reached === -1) {
        if (!this.shifted) {
          drone._maxSpeed = drone._maxSpeed * LOITER_SPEED_FACTOR;
          var min = 9999, min_i;
          for (var i = 0; i < this._loiter_coordinates.length; i++){
            var d = distance([drone_pos.x, drone_pos.y], [this._loiter_coordinates[i].x, this._loiter_coordinates[i].y]);
            if (d < min) {
              min = d;
              min_i = i;
            }
          }
          this._loiter_coordinates = this._loiter_coordinates.concat(this._loiter_coordinates.splice(0,min_i));
          this.shifted = true;
        }
      } else {
        this.shifted = false;
      }
      //stop
      if (this._last_loiter_point_reached === this._loiter_coordinates.length - 1) {
        if (drone._maxSpeed !== this.getMaxSpeed()) {
          drone._maxSpeed = this.getMaxSpeed();
        }
        drone.setDirection(0, 0, 0);
        return;
      }
      //loiter
      var next_point = this._loiter_coordinates[this._last_loiter_point_reached + 1];
      drone.setTargetCoordinates(next_point.x, next_point.y, next_point.z, -1);
      if (distance([drone_pos.x, drone_pos.y], [next_point.x, next_point.y]) < 1) {
        this._last_loiter_point_reached += 1;
        if (this._last_loiter_point_reached === this._loiter_coordinates.length - 1) {
          return;
        }
        next_point = this._loiter_coordinates[this._last_loiter_point_reached + 1];
        drone.setTargetCoordinates(next_point.x, next_point.y, next_point.z, -1);
      }
    }
  };
  DroneAaileFixeAPI.prototype.getDroneAI = function () {
    return null;
  };
  DroneAaileFixeAPI.prototype.setAltitude = function (altitude, drone, skip_loiter) {
    this.takeoff_path = [];
    if (skip_loiter) {
      var drone_pos = drone.getCurrentPosition();
      drone.setTargetCoordinates(drone_pos.x, drone_pos.y, altitude);
      return;
    }
    var x1, y1,
      LOOPS = 1,
      CIRCLE_ANGLE = 8,
      current_point = 0,
      total_points = 360/CIRCLE_ANGLE*LOOPS,
      initial_altitude = drone.getAltitudeAbs(),
      center = {
        x: drone.position.x,
        y: drone.position.y,
        z: drone.position.z
      };
    for (var l = 0; l <= LOOPS; l+=1){
      for (var angle = 360; angle > 0; angle-=CIRCLE_ANGLE){ //clockwise sense
        current_point++;
        x1 = TAKEOFF_RADIUS * Math.cos(angle * (Math.PI / 180)) + center.x;
        y1 = TAKEOFF_RADIUS * Math.sin(angle * (Math.PI / 180)) + center.y;
        if (current_point < total_points/3) {
          var FACTOR = 0.5;
          x1 = center.x*FACTOR + x1*(1-FACTOR);
          y1 = center.y*FACTOR + y1*(1-FACTOR);
        }
        this.takeoff_path.push({x: x1, y: y1, z: initial_altitude + current_point * (altitude-initial_altitude)/total_points});
      }
    }
  };
  DroneAaileFixeAPI.prototype.reachAltitude = function (drone) {
    function distance(p1, p2) {
      return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                       Math.pow(p1[1] - p2[1], 2));
    }
    //stop
    if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
      this._last_altitude_point_reached = -1;
      this.takeoff_path = [];
      drone._start_altitude = 0;
      drone.setDirection(0, 0, 0);
      return;
    }
    //loiter
    var drone_pos = {
      x: drone.position.x,
      y: drone.position.y,
      z: drone.position.z
    };
    var next_point = this.takeoff_path[this._last_altitude_point_reached + 1];
    drone.internal_setTargetCoordinates(next_point.x, next_point.y, next_point.z);
    if (distance([drone_pos.x, drone_pos.y], [next_point.x, next_point.y]) < 1) {
      this._last_altitude_point_reached += 1;
      if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
        return;
      }
      next_point = this.takeoff_path[this._last_altitude_point_reached + 1];
      drone.internal_setTargetCoordinates(next_point.x, next_point.y, next_point.z);
    }
  };
  DroneAaileFixeAPI.prototype.getMaxSpeed = function () {
    return GAMEPARAMETERS.drone.maxSpeed;
  };
  DroneAaileFixeAPI.prototype.doParachute = function (drone) {
    //TODO what to do here?
    drone.setDirection(0, 0, 0);
  };
  DroneAaileFixeAPI.prototype.landed = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    return Math.floor(drone_pos.z) === 0;
  };
  DroneAaileFixeAPI.prototype.exit = function (drone) {
    //TODO what to do here?
    drone.setDirection(0, 0, 0);
  };
  DroneAaileFixeAPI.prototype.getInitialAltitude = function () {
    return 0;
  };
  DroneAaileFixeAPI.prototype.getAltitudeAbs = function (altitude) {
    return altitude;
  };
  DroneAaileFixeAPI.prototype.getMinHeight = function () {
    return 0;
  };
  DroneAaileFixeAPI.prototype.getMaxHeight = function () {
    return 800;
  };
  DroneAaileFixeAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return DroneAaileFixeAPI;
}());

/******************************************************************************/



/******************************* DRONE MANAGER ********************************/

var DroneManager = /** @class */ (function () {
  //** CONSTRUCTOR
  function DroneManager(scene, id, API) {
    var _this = this;
    // Mesh
    this._mesh = null;
    this._controlMesh = null;
    this._colliderBackMesh = null; //TODO drop?
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
    this._start_loiter = 0;
    this._start_altitude = 0;
    this._API = API; // var API created on AI evel
    // Create the control mesh
    this._controlMesh = BABYLON.Mesh.CreateBox("droneControl_" + id, 0.01, this._scene);
    this._controlMesh.isVisible = false;
    this._controlMesh.computeWorldMatrix(true);
    // Create the mesh from the drone prefab
    this._mesh = DroneManager.Prefab.clone("drone_" + id, this._controlMesh);
    this._mesh.position = BABYLON.Vector3.Zero();
    this._mesh.isVisible = false;
    this._mesh.computeWorldMatrix(true);
    // Get the back collider
    this._mesh.getChildMeshes().forEach(function (mesh) {
      if (mesh.name.substring(mesh.name.length - 13) == "Dummy_arriere") {
        _this._colliderBackMesh = mesh;
        _this._colliderBackMesh.isVisible = false;
      }
      else {
        mesh.isVisible = true;
      }
    });
    if (!DroneManager.PrefabBlueMat) {
      DroneManager.PrefabBlueMat = new BABYLON.StandardMaterial("blueTeamMat", scene);
      DroneManager.PrefabBlueMat.diffuseTexture = new BABYLON.Texture("assets/drone/drone_bleu.jpg", scene);
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
  Object.defineProperty(DroneManager.prototype, "colliderBackMesh", {
    get: function () { return this._colliderBackMesh; },
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
      return new BABYLON.Vector3(this._direction.x, this._direction.y, this._direction.z);
    },
    enumerable: true,
    configurable: true
  });
  DroneManager.prototype.internal_start = function () {
      this._maxAcceleration = GAMEPARAMETERS.drone.maxAcceleration;
      this._maxSpeed = this._API.getMaxSpeed();
      this._canPlay = true;
      this._canCommunicate = true;
      try {
        return this.onStart();
      } catch (error) {
        console.warn('Drone crashed on start due to error:', error);
        this._internal_crash();
      }
  };
  DroneManager.prototype.internal_setTargetCoordinates = function (x, y, z) {
    if (!this._canPlay)
      return;
    x -= this._controlMesh.position.x;
    y -= this._controlMesh.position.z;
    z -= this._controlMesh.position.y;
    this.setDirection(x, y, z);
    this.setAcceleration(this._maxAcceleration);
    return;
  };
  DroneManager.prototype.internal_update = function (delta_time) {
    var context = this;
    if (this._controlMesh) {
      context._speed += context._acceleration * delta_time / 1000;
      if (context._speed > context._maxSpeed)
        context._speed = context._maxSpeed;
      if (context._speed < -context._maxSpeed)
        context._speed = -context._maxSpeed;
      var updateSpeed = context._speed * delta_time / 1000;
      if (context._direction.x != 0
        || context._direction.y != 0
        || context._direction.z != 0) {
        context._controlMesh.position.addInPlace(new BABYLON.Vector3(context._direction.x * updateSpeed, context._direction.y * updateSpeed, context._direction.z * updateSpeed));
      }
      var orientationValue = context._maxOrientation * (context._speed / context._maxSpeed);
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
          }, function (err) {
            console.warn('Drone crashed on update due to error:', err);
            context._internal_crash();
          })
          .push(function () {
            if (context._start_loiter > 0) {
              context._API.loiter(context);
            }
            if (context._start_altitude > 0) {
              context._API.reachAltitude(context);
            }
          });
      }
      return;
    }
    return;
  };
  DroneManager.prototype._internal_crash = function () {
    this._canCommunicate = false;
    this._controlMesh = null;
    this._mesh = null;
    this._canPlay = false;
    this.onTouched();
  };
  DroneManager.prototype.setStartingPosition = function (x, y, z) {
    if(isNaN(x) || isNaN(y) || isNaN(z)){
      throw new Error('Position coordinates must be numbers');
    }
    if (!this._canPlay) {
      if (z <= 0.05)
        z = 0.05;
      this._controlMesh.position = new BABYLON.Vector3(x, z, y);
    }
    this._controlMesh.computeWorldMatrix(true);
    this._mesh.computeWorldMatrix(true);
  };
  DroneManager.prototype.setAcceleration = function (factor) {
    if (!this._canPlay)
      return;
    if (isNaN(factor)){
      throw new Error('Acceleration must be a number');
    }
    if (factor > this._maxAcceleration)
      factor = this._maxAcceleration;
    this._acceleration = factor;
  };
  DroneManager.prototype.setDirection = function (x, y, z) {
    if (!this._canPlay)
      return;
    if(isNaN(x) || isNaN(y) || isNaN(z)){
      throw new Error('Direction coordinates must be numbers');
    }
    this._direction = new BABYLON.Vector3(x, z, y).normalize();
  };
  /**
   * Set a target point to move
   */
  DroneManager.prototype.setTargetCoordinates = function (x, y, z, r) {
    if (!this._canPlay)
      return;
    //HACK too specific for DroneAaileFixe, should be a flag: (bool)process?
    if (r !== -1) {
      this._start_loiter = 0;
      this._maxSpeed = this._API.getMaxSpeed();
    }
    this._start_altitude = 0;
    var coordinates = this._API.processCoordinates(x, y, z, r);
    coordinates.x -= this._controlMesh.position.x;
    coordinates.y -= this._controlMesh.position.z;
    coordinates.z -= this._controlMesh.position.y;
    this.setDirection(coordinates.x, coordinates.y, coordinates.z);
    this.setAcceleration(this._maxAcceleration);
    return;
  };
  /**
   * Send a message to team drones
   * @param msg The message to send
   * @param id The targeted drone. -1 or nothing to broadcast
   */
  DroneManager.prototype.sendMsg = function (msg, id) {
    //TODO
    return;
    var _this = this;
    if (!this._canCommunicate)
      return;
    if (id >= 0) { }
    else
      id = -1;
    if (_this.infosMesh) {
      return _this._API.internal_sendMsg(JSON.parse(JSON.stringify(msg)), id);
    }
  };
  /** Perform a console.log with drone id + the message */
  DroneManager.prototype.log = function (msg) { };
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
    if (!this._canCommunicate)
      return;
    return this._API.getGameParameter(name);
  };
  DroneManager.prototype.getCurrentPosition = function () {
    if (this._controlMesh)
      return this._API.processCurrentPosition(
        this._controlMesh.position.x,
        this._controlMesh.position.z,
        this._controlMesh.position.y
      );
    return null;
  };
  DroneManager.prototype.setAltitude = function (altitude, skip_loiter) {
    if (!this._canPlay)
      return;
    if (this._start_altitude === 0) {
      this._start_altitude = 1;
    }
    altitude = this._API.setAltitude(altitude, this, skip_loiter);
    return;
  };
  /**
   * Make the drone loiter (circle with a set radius)
   */
  DroneManager.prototype.loiter = function () {
    if (!this._canPlay)
      return;
    if (this._start_loiter === 0) {
      this._start_loiter = 1;
    }
  };
  DroneManager.prototype.getFlightParameters = function () {
    if (this._API.getFlightParameters)
      return this._API.getFlightParameters();
    return null;
  };
  DroneManager.prototype.getYaw = function () {
    //TODO
    return 0;
  };
  DroneManager.prototype.doParachute = function () {
    return this._API.doParachute(this);
  };
  DroneManager.prototype.exit = function () {
    return this._API.exit(this);
  };
  DroneManager.prototype.landed = function () {
    return this._API.landed(this);
  };
  /**
   * Set the drone last checkpoint reached
   * @param checkpoint to be set
   */
  DroneManager.prototype.setCheckpoint = function (checkpoint) {
    //TODO
    return null;
  };
  /**
   * Function called on game start
   */
  DroneManager.prototype.onStart = function () { };
  ;
  /**
   * Function called on game update
   */
  DroneManager.prototype.onUpdate = function (timestamp) { };
  ;
  /**
   * Function called when drone crashes
   */
  DroneManager.prototype.onTouched = function () { };
  ;
  /**
   * Function called when a message is received
   * @param msg The message
   */
  DroneManager.prototype.onGetMsg = function (msg) { };
  ;
  return DroneManager;
}());

/******************************************************************************/



/******************************** MAP MANAGER *********************************/

var MapManager = /** @class */ (function () {
  //** CONSTRUCTOR
  function MapManager(scene) {
    var _this = this;
    var max = GAMEPARAMETERS.mapSize.width;
    if (GAMEPARAMETERS.mapSize.depth > max)
        max = GAMEPARAMETERS.mapSize.depth;
    if (GAMEPARAMETERS.mapSize.height > max)
        max = GAMEPARAMETERS.mapSize.height;
    max = max < GAMEPARAMETERS.mapSize.depth ? GAMEPARAMETERS.mapSize.depth : max;
    // Skybox
    var max_sky = (max * 10 < 20000) ? max * 10 : 20000,
      skybox = BABYLON.Mesh.CreateBox("skyBox", max_sky, scene);
    skybox.infiniteDistance = true;
    skybox.renderingGroupId = 0;
    var skyboxMat = new BABYLON.StandardMaterial("skybox", scene);
    skyboxMat.backFaceCulling = false;
    skyboxMat.disableLighting = true;
    skyboxMat.reflectionTexture = new BABYLON.CubeTexture("./assets/skybox/sky", scene);
    skyboxMat.reflectionTexture.coordinatesMode = BABYLON.Texture.SKYBOX_MODE;
    skyboxMat.infiniteDistance = true;
    skybox.material = skyboxMat;
    // Plane from bottom
    var largeGroundMat = new BABYLON.StandardMaterial("largeGroundMat", scene);
    largeGroundMat.specularColor = BABYLON.Color3.Black();
    largeGroundMat.alpha = 0.4;
    var largeGroundBottom = BABYLON.Mesh.CreatePlane("largeGroundBottom", max * 11, scene);
    largeGroundBottom.position.y = -0.01;
    largeGroundBottom.rotation.x = -Math.PI / 2;
    largeGroundBottom.rotation.y = Math.PI;
    largeGroundBottom.material = largeGroundMat;
    // Camera
    scene.activeCamera.upperRadiusLimit = max * 4;
    // Terrain
    var width = GAMEPARAMETERS.mapSize.width,
      depth = GAMEPARAMETERS.mapSize.depth,
      height = GAMEPARAMETERS.mapSize.height,
      terrain = scene.getMeshByName("terrain001");
    terrain.isVisible = true;
    terrain.position = BABYLON.Vector3.Zero();
    terrain.scaling = new BABYLON.Vector3(depth / 50000, depth / 50000, width / 50000);
    // Flight path point list
    var count = 0;
    this._flight_path_point_list = [];
    GAMEPARAMETERS.flight_path_point_list.forEach(function (obs) {
      var newObj;
      switch (obs.type) {
        case "box":
          newObj = BABYLON.MeshBuilder.CreateBox("obs_" + count, { 'size': 1 }, scene);
          break;
        case "cylinder":
          newObj = BABYLON.MeshBuilder.CreateCylinder("obs_" + count, {
            'diameterBottom': obs.diameterBottom,
            'diameterTop': obs.diameterTop,
            'height': 1
          }, scene);
          break;
        case "sphere":
          newObj = BABYLON.MeshBuilder.CreateSphere("obs_" + count, {
            'diameterX': obs.scale.x,
            'diameterY': obs.scale.y,
            'diameterZ': obs.scale.z
          }, scene);
          break;
        default:
          return;
      }
      newObj.obsType = obs.type;
      var convertion = Math.PI / 180;
      if ("position" in obs)
        newObj.position = new BABYLON.Vector3(obs.position.x, obs.position.y, obs.position.z);
      if ("rotation" in obs)
        newObj.rotation = new BABYLON.Vector3(obs.rotation.x * convertion, obs.rotation.y * convertion, obs.rotation.z * convertion);
      if ("scale" in obs)
        newObj.scaling = new BABYLON.Vector3(obs.scale.x, obs.scale.y, obs.scale.z);
      if ("color" in obs) {
        var material = new BABYLON.StandardMaterial(scene);
        material.alpha = 1;
        material.diffuseColor = new BABYLON.Color3(obs.color.r, obs.color.g, obs.color.b);
        newObj.material = material;
      }
      _this._flight_path_point_list.push(newObj);
    });
  }
  return MapManager;
}());