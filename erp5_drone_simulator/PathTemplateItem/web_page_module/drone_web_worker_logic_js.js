/*global GameManager, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */



/*********************** DRONE SIMULATOR LOGIC ********************************/

var runGame, updateGame, eventGame, game_manager_instance;
// game.js
(function () {
  "use strict";
  console.log('game logic');

  runGame = function (canvas, script, game_parameters_json, log) {

    function processLog(game_parameters_json, log) {
      var MAP_SIZE = 1000,
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
        previous_log_time, height, timestamp, destination_lon,
        destination_lat, log_header_found, time_offset = 1,
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
          destination_lon = lon;
          destination_lat = lat;
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
            "rotation": {
              "x": 0,
              "y": 0,
              "z": 0
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
      game_parameters_json.obstacles = path_point_list;
      /*game_parameters_json.randomSpawn.leftTeam.position.x = start_position[0];
      game_parameters_json.randomSpawn.leftTeam.position.y = start_position[1];
      game_parameters_json.randomSpawn.leftTeam.position.z = start_position[2];*/
      game_parameters_json.dronesPosition.x = start_position[0];
      game_parameters_json.dronesPosition.y = start_position[1];
      game_parameters_json.dronesPosition.z = start_position[2];
      game_parameters_json.gameTime = flight_time;
      //give map some margin from the flight
      game_parameters_json.mapSize.width = MAP_SIZE * 1.10;
      game_parameters_json.mapSize.depth = MAP_SIZE * 1.10;
      //flight destination
      var destination_x = longitudToX(destination_lon),
        destination_y = latitudeToY(destination_lat),
        destination = normalizeToMap(destination_x, destination_y);
      game_parameters_json.randomSpawn.rightTeam.position.x = destination[0];
      game_parameters_json.randomSpawn.rightTeam.position.y = destination[1];
      return game_parameters_json;
    }
    game_parameters_json = processLog(game_parameters_json, log);
    if (!game_manager_instance) {
      game_manager_instance = new GameManager(canvas, script,
                                              game_parameters_json, 5);
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
    this._teamLeft = []; //TODO rename as drone list or something
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
    //TODO drop the use of RS map and use a JSON instead. drop randomspawn and similar names //rename all
    //TODO do this in above, in game logic game_parameters_json
    //move this to JSON dict
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
    // To increase the game speed, increase this value
    _this._max_step_animation_frame = 10;
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

  GameManager.prototype._updateDisplayedInfo = function (delta_time, update_dom) {
    this._game_duration += delta_time;
    var seconds = Math.floor(this._game_duration / 1000);
    if (GAMEPARAMETERS.compareFlights) {
      for (var count = 0; count < GAMEPARAMETERS.droneList.length; count++) {
        if (this._teamLeft[count]._controlMesh) {
          var drone_position_x = this._teamLeft[count]._controlMesh.position.x,
            drone_position_z = this._teamLeft[count]._controlMesh.position.y,
            drone_position_y = this._teamLeft[count]._controlMesh.position.z;
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

    function updateDrone(drone) {
      drone._tick += 1;
      return drone.internal_update(delta_time);
    }

    this._teamLeft.forEach(function (drone) {
      queue.push(function () {
        return updateDrone(drone);
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
      console.log("on3DmodelsReady!");
      // Get the game parameters
      if (!ctx._map_swapped) {
        GAMEPARAMETERS = ctx._getGameParameter();
        ctx._map_swapped = true;
      }
      console.log("APIs created");
      // Set the AI code into drones
      var AIcodeEval, AIcodeLeft; //TODO rename all left/team/'L'
      AIcodeLeft = ctx._script;
      // Init the map
      _this._mapManager = new MapManager(ctx._scene);
      console.log("Map manager instantiated");
      ctx._spawnDrones(GAMEPARAMETERS.dronesPosition, GAMEPARAMETERS.droneList, AIcodeLeft);
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //Hack to make advanced texture work
      const documentTmp = document;
      document = undefined;
      var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI", true, ctx._scene);
      document = documentTmp;
      for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) { //TODO use one color per drone
        var controlMeshBlue = ctx._teamLeft[count].infosMesh;
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
      console.log("advaced textures added");
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
        // 3,2,1,GO before start. To animate. //TODO DROP this countdown
        var result = new RSVP.Queue(),
          i;
        function countdown (count) {
          return function () {
            console.log(count + " ...");
            return RSVP.delay(200);
          };
        }
        for (i = 5; 0 <= i; i -= 1) {
          result.push(countdown(i));
        }
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
        _this._teamLeft.forEach(function (drone) {
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
    console.log("_load3DModel!");
    var _this = this, droneTask, mapTask, obstacleTask,
      assetManager = new BABYLON.AssetsManager(this._scene);
    assetManager.useDefaultLoadingScreen = true;
    // DRONE
    droneTask = assetManager.addMeshTask("loadingDrone", "", "assets/drone/", "drone.babylon"); //TODO got from RS skin!
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
        ObstacleManager.Prefab = _this._scene.getMeshByName("car"); //TODO DELETE this is the boat
    };
    obstacleTask.onError = function () {
        console.log("Error loading 3D model for Obstacle");
    };
    assetManager.onFinish = function () {
      return callback();
    };
    assetManager.load();
    console.log("asset manager loaded (tasks for map, drones and obstacles)");
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
    //TODO obstacle is kept as real flight log uses for path draw. Refactor this
    for (i = 0; i < parameter.obstacles.length; i += 1) {
      parameter.obstacles[i].position = swap(parameter.obstacles[i].position);
      if (parameter.obstacles[i].scale) {
        parameter.obstacles[i].scale = swap(parameter.obstacles[i].scale);
      }
      if (parameter.obstacles[i].rotation) {
        parameter.obstacles[i].rotation = swap(parameter.obstacles[i].rotation);
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
        var api = new this.APIs_dict[drone_list[i]](this, "L", GAMEPARAMETERS.compareFlights); //TODO drip L team in DroneAPI
        this._setSpawnDrone(position.x, position.y, position.z, i, api, code);
      }
    }
  };

  GameManager.prototype._setSpawnDrone = function (x, y, z, index, api, code) {
      var default_drone_AI = api.getDroneAI();
      if (default_drone_AI) {
        code = default_drone_AI;
      }
      var team = "L"; //TODO DROP TEAM
      var ctx = this, base, code_eval = "let drone = new DroneManager(ctx._scene, " +
          index + ', "' + team + '", api);' +
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
        base += "};ctx._teamLeft.push(drone)";
        code_eval += "ctx._teamLeft.push(drone)";
      try {
        eval(code_eval);
      }
      catch (error) {
        eval(base);
      }
  };

  return GameManager;
}());

