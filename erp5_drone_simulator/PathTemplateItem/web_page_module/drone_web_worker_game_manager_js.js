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
    this._ground_truth_target = null;
    this._engine = null;
    this._teamLeft = [];
    this._teamRight = [];
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
      for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
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
      DroneLogAPI: DroneLogAPI,
      DroneAPI: DroneAPI
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

  /*GameManager.prototype.event = function (event) {
    var _this = this;
    console.log("[GM] Event. this._camera:", this._camera);
    console.log("[GM] Event. event:", event);
  };*/

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
    //TODO Timing display?
    /*if (update_dom) {
      this._timeDisplay.textContent = this._formatTimeToMinutesAndSeconds(this._game_duration);
    }*/
    if (GAMEPARAMETERS.compareFlights) {
      for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
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
          if (GAMEPARAMETERS.compareFlights.draw) {
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
      var msg = '';
      drone._tick += 1;
      if (drone.can_play()) {
        //TODO check collisions
      }
      return drone.internal_update(delta_time);
    }

    function updateHuman(human) {
      var result = human.internal_update(delta_time);
      _this._ground_truth_target = {
        x: human.position.x,
        y: human.position.y,
        z: human.position.z
      };
      return result;
    }
    // Check collisions -- Drone swarm
    this._teamLeft.forEach(function (drone) {
      queue.push(function () {
        return updateDrone(drone);
      });
    });

    // Update position -- Human
    this._teamRight.forEach(function (human) {
      queue.push(function () {
        return updateHuman(human);
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
    var _this = this,
      center = GAMEPARAMETERS.randomSpawn.rightTeam.position,
      dispertion = GAMEPARAMETERS.randomSpawn.rightTeam.dispertion;
    if (GAMEPARAMETERS.randomSpawn.rightTeam.dispersed)
      dispertion = {x: 0, y: 0, z: 0};
    this._ground_truth_target =
      randomSpherePoint(center.x, center.y, center.z,
                        dispertion.x, dispertion.y, dispertion.z);
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
    //removed for event handling
    //this._engine.enableOfflineSupport = false;
    this._scene = new BABYLON.Scene(this._engine);
    this._scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
    //removed for event handling
    //this._scene.collisionsEnabled = true;
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
      // Create the API
      var lAPI = new DroneAPI(ctx, "L");
      var rAPI = new DroneAPI(ctx, "R");
      console.log("APIs created");
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
      _this._mapManager = new MapManager(ctx._scene);
      console.log("Map manager instantiated");
      if (GAMEPARAMETERS.randomSpawn) {
        ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.leftTeam, GAMEPARAMETERS.teamSize, lAPI, AIcodeLeft, "L");
        ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.rightTeam, GAMEPARAMETERS.teamSize, rAPI, AIcodeRight, "R");
      }
      // Hide the drone prefab
      DroneManager.Prefab.isVisible = false;
      //GUI for drones ID display
      //Hack to make advanced texture work
      const documentTmp = document;
      document = undefined;
      var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI", true, ctx._scene);
      document = documentTmp;
      for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
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
        // 3,2,1,GO before start. To animate.
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
    // Timing
    this._game_duration = 0;
    this._totalTime = GAMEPARAMETERS.gameTime;

    return new RSVP.Queue()
      .push(function () {
        promise_list = [];
        _this._teamLeft.forEach(function (drone) {
          drone._tick = 0;
          promise_list.push(drone.internal_start());
        });
        _this._teamRight.forEach(function (drone) {
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

  GameManager.prototype._setRandomSpawnPosition = function (randomSpawn, team_size, api, code, team) {
      var position, i, position_list = [], center = randomSpawn.position, max_collision = randomSpawn.maxCollision || 10 * team_size, collision_nb = 0;
      function checkCollision(position, list) {
        var i;
        for (i = 0; i < list.length; i += 1) {
          if (position.equalsWithEpsilon(list[i], 0.5)) {
            return true;
          }
        }
        return false;
      }
      for (i = 0; i < team_size; i += 1) {
        //set only one element for right team (the human)
        if (team === "L" || i === 0) {
          if (GAMEPARAMETERS.randomSpawn.rightTeam.dispersed) {
            position = randomSpherePoint(center.x + i, center.y + i, center.z + i, 0, 0, 0);
          } else {
            position = randomSpherePoint(center.x, center.y, center.z, randomSpawn.dispertion.x, randomSpawn.dispertion.y, randomSpawn.dispertion.z);
          }
          if (team === "R") {
            this._setSpawnDrone(this._ground_truth_target.x, this._ground_truth_target.y, this._ground_truth_target.z, i, api, code, team);
          } else {
            if (checkCollision(position, position_list) || position.z < 0.05) {
              collision_nb += 1;
              if (collision_nb < max_collision) {
                i -= 1;
              }
            }
            else {
              position_list.push(position);
              var lAPI = api;
              if (randomSpawn.types) {
                if (randomSpawn.types[i] in this.APIs_dict) {
                  lAPI = new this.APIs_dict[randomSpawn.types[i]](this, "L", GAMEPARAMETERS.compareFlights);
                }
              }
              this._setSpawnDrone(position.x, position.y, position.z, i, lAPI, code, team);
            }
          }
        }
      }
  };

  GameManager.prototype._setSpawnDrone = function (x, y, z, index, api, code, team) {
      var default_drone_AI = api.getDroneAI();
      if (default_drone_AI) {
        code = default_drone_AI;
      }
      var ctx = this, base, code_eval = "let drone = new DroneManager(ctx._scene, " +
          index + ', "' + team + '", api);' +
          "let droneMe = function(NativeDate, me, Math, window, DroneManager, GameManager, DroneAPI, DroneLogAPI, DroneAaileFixeAPI, BABYLON, GAMEPARAMETERS) {" +
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
      if (team == "R") {
        base += "};ctx._teamRight.push(drone)";
        code_eval += "ctx._teamRight.push(drone)";
      }
      else {
        base += "};ctx._teamLeft.push(drone)";
        code_eval += "ctx._teamLeft.push(drone)";
      }
      try {
        eval(code_eval);
      }
      catch (error) {
        eval(base);
      }
  };

  return GameManager;
}());
