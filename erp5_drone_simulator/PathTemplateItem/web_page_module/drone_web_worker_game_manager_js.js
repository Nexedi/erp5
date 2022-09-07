/// <reference path="./typings/babylon.3.1.d.ts" />
/// <reference path="./typings/require.d.ts" />
/// <reference path="./DroneManager.ts" />
/// <reference path="./MapManager.ts" />
/// <reference path="./typings/babylon.gui.d.ts" />

var GAMEPARAMETERS = {};

var GameManager = /** @class */ (function (console) {
    var browser_console = console,
      console_output = '';
    console = {
      warn: browser_console.warn.bind(browser_console),
      log: function () {
        var i,
          len = arguments.length,
          output_list = [];
        for (i = 0; i < len; i += 1) {
          output_list.push(JSON.stringify(arguments[i]));
        }
        console_output += output_list.join(' ') + '\n';
        browser_console.log.apply(browser_console, arguments);
      }
    };
    //*************************************************** CONSTRUCTOR **************************************************
    function GameManager(canvas, script, map, simulation_speed) {
        var _this = this;
        //*************************************************** MEMBERS ******************************************************
        // Base Babylon members
        this._scene = null;
        this._engine = null;
        // Teams
        this._teamLeft = [];
        this._teamRight = [];
        // Update registering
        this._canUpdate = false;
        this._gameFinished = false;
        // this._pauseTime = 0;
        this._isFullscreen = false;
        this._final_score = 0;
        Object.assign(GAMEPARAMETERS, map);
        this._map = map;
        this._canvas = canvas;
        this._map_swapped = false;
        this._script = script;
        this._updated = false;
        this._reported_human_position = false;
        this._time_human_position_reported = false;
        this._ground_truth_target = false;
        this.finish_deferred = null;
        if (!simulation_speed) { simulation_speed = 5; }
        this._max_step_animation_frame = simulation_speed;
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
        // ----------------------------------- CODE ZONES AND PARAMS
        // JIO : AI
        // XXX
        /*DroneManager.jIOstorage = jIO.createJIO({
            "type": "query",
            "sub_storage": {
                "type": "indexeddb",
                "database": "Drones_infos_storage"
            }
        });*/

        // Timing display
        console.log("time display commented");
        /*this._timeDisplay = document.getElementById("timingDisplay");
        document.getElementById("simPlay").style.display = "none";
        document.getElementById("simPause").style.display = "none";*/
    };

    GameManager.prototype.run = function() {
      var gadget = this;
      /*return DroneManager.jIOstorage.allDocs()
        .push(function (result) {
          var promise_list = [], i;
          for (i = 0; i < result.data.total_rows; i += 1) {
              promise_list.push(DroneManager.jIOstorage.remove(result.data.rows[i].id));
          }
          return RSVP.all(promise_list);
        })
        .push(function () {*/
          return gadget._init()/*;
        })*/
        .push(function () {
          if (GAMEPARAMETERS.compareFlights) {
            return gadget._flight_log;
          }
          return gadget._final_score;
        });
    };

    GameManager.getLog = function getLog() {
      return console_output;
    };

    Object.defineProperty(GameManager.prototype, "teamLeft", {
        //*************************************************** ACCESSOR *****************************************************
        get: function () { return this._teamLeft; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(GameManager.prototype, "teamRight", {
        get: function () { return this._teamRight; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(GameManager.prototype, "gameParameter", {
        get: function () {
            return this._gameParameter;
        },
        enumerable: true,
        configurable: true
    });
    //*************************************************** FUNCTIONS ****************************************************
    /**
     * Display a message in the bottom zone
     * @param msg
     */
    GameManager.prototype._displayMsg = function (msg) {
        console.log("display msg commented");
        //document.getElementById("messages").innerText = msg;
    };
    /**
     * Display a message in the bottom zone
     * @param msg
     */
    GameManager.prototype._formatTimeToMinutesAndSeconds = function (time) {
        var seconds = Math.floor(time / 1000),
          minutes = Math.floor(seconds / 60),
          sminutes = "00",
          sseconds = "00";
        sminutes = (minutes < 10) ? "0" + minutes.toString() : minutes.toString();
        seconds -= (minutes * 60);
        sseconds = (seconds < 10) ? "0" + seconds.toString() : sseconds = seconds.toString();
        return sminutes + ":" + sseconds;
    };
    /**
     * Store the human position reported by a drone and the detection time
     * @param position
     */
    GameManager.prototype.reportHumanPosition = function (position) {
        this._reported_human_position = position;
        this._time_human_position_reported = this._game_duration;
        this._finish();
    };
    /**
     * Verify if drone has found the human by checking the position coordinates
     * @param reported_human_position
     */
    GameManager.prototype.checkHumanDistance = function (reported_human_position) {
        if (!reported_human_position)
          return -1;
        var a = reported_human_position.x - this._ground_truth_target.x,
          b = reported_human_position.y - this._ground_truth_target.y,
          distance = Math.sqrt( a*a + b*b );
        return distance;
    };
    GameManager.prototype._calculateScore = function (human_found) {
        var detection_time = this._time_human_position_reported / 1000;
        if (!human_found) {
          this._time_human_position_reported = this._totalTime * 1000;
          detection_time = this._totalTime;
        }
        this._final_score = Math.floor(detection_time);
    };
    GameManager.prototype._displayResult = function () {
        console.log("_displayResult table commented");
        /*var table = document.createElement('table'), tr, th, td, team, div,
          main = document.getElementsByClassName("leftZone")[0];
        table.setAttribute("id", "result_table");
        tr = document.createElement('tr');
        td = document.createElement('td');
        td.textContent = "Total detection time:";
        tr.appendChild(td);
        td = document.createElement('td');
        td.textContent = this._formatTimeToMinutesAndSeconds(this._time_human_position_reported);
        tr.appendChild(td);
        table.appendChild(tr);
        tr = document.createElement('tr');
        td = document.createElement('td');
        td.textContent = "Reported human position:";
        tr.appendChild(td);
        td = document.createElement('td');
        if (this._reported_human_position) {
          td.textContent = "(" +
            Math.round(this._reported_human_position.x * 100) / 100 +
            "," + Math.round(this._reported_human_position.y * 100) / 100 + ")";
        } else {
          td.textContent = "-";
        }
        tr.appendChild(td);
        table.appendChild(tr);
        tr = document.createElement('tr');
        td = document.createElement('td');
        td.textContent = "Real human position:";
        tr.appendChild(td);
        td = document.createElement('td');
        var ground_truth_target_s = "(" +
          Math.round(this._ground_truth_target.x * 100) / 100 +
          "," + Math.round(this._ground_truth_target.y * 100) / 100 + ")";
        td.textContent = ground_truth_target_s;
        tr.appendChild(td);
        table.appendChild(tr);
        tr = document.createElement('tr');
        th = document.createElement('th');
        th.textContent = "Score";
        tr.appendChild(th);
        th = document.createElement('th');
        th.textContent = Math.round(this._final_score * 100) / 100;
        tr.appendChild(th);
        table.appendChild(tr);
        table.className = "result";
        main.appendChild(table);*/
    };
    //**************************** INTERNAL FUNCTIONS
    /**
     * Function called to load all the 3D models
     * @param callback Function called when models loaded
     */
    GameManager.prototype._load3DModel = function (callback) {
        var _this = this;
        var assetManager = new BABYLON.AssetsManager(this._scene);
        assetManager.useDefaultLoadingScreen = true;
        // OBSTACLE
        var obstacleTask = assetManager.addMeshTask("loadingObstacle", "", "assets/obstacle/", "boat.babylon");
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
        // DRONE
        var droneTask = assetManager.addMeshTask("loadingDrone", "", "assets/drone/", "drone.babylon");
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
        var mapTask = assetManager.addMeshTask("loadingMap", "", "assets/map/", "map.babylon");
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
    /**
     * Update the displayed timing
     */
    GameManager.prototype._updateTiming = function (delta_time, update_dom) {
        // Timing display
        this._game_duration += delta_time;
        var seconds = Math.floor(this._game_duration / 1000);
        if (this._totalTime - seconds <= 0) {
            this._time_human_position_reported = this._game_duration;
            this._finish(time_out=true);
        }
        if (update_dom) {
          console.log("_timeDisplay commented", this._formatTimeToMinutesAndSeconds(this._game_duration));
          //this._timeDisplay.textContent = this._formatTimeToMinutesAndSeconds(this._game_duration);
        }
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
    /**
     * Function used to check collision between 2 drones
     * @param drone1
     * @param drone2
     */
    GameManager.prototype._checkCollision = function (drone, other) {
        if (GAMEPARAMETERS.compareFlights) {
          return;
        }
        if (drone.colliderMesh && other.colliderMesh
            && drone.colliderMesh.intersectsMesh(other.colliderMesh, false)) {
            var angle = Math.acos(BABYLON.Vector3.Dot(drone.worldDirection, other.worldDirection) / (drone.worldDirection.length() * other.worldDirection.length()));
            var dteam = "blue";
            var msg = void 0;
            if (drone.team == "R")
                dteam = "red";
            var oteam = "blue";
            if (other.team == "R")
                oteam = "red";
            if (angle < GAMEPARAMETERS.drone.collisionSector) {
                if (drone.speed > other.speed) {
                    this._gameResult[other.team].crash += 1;
                    other.internal_touch();
                    msg = "Drone " + drone.id + " bump drone " + other.id + "!";
                }
                else {
                    this._gameResult[drone.team].crash += 1;
                    drone.internal_touch();
                    msg = "Drone " + other.id + " bump drone " + drone.id + "!";
                }
            }
            else {
                msg = "Drone " + drone.id + " touched drone " + other.id + "!";
                this._gameResult[other.team].crash += 1;
                this._gameResult[drone.team].crash += 1;
                drone.internal_touch();
                other.internal_touch();
            }
            this._displayMsg(msg);
        }
    };
    /**
     * Function used to check collision between 1 drone and an special obstacle
     * @param drone
     * @param obstacle
     */
    GameManager.prototype._checkCollisionWithSpecialObstacle = function (drone, obstacle) {
        if (drone.colliderMesh && obstacle.colliderMesh
            && drone.colliderMesh.intersectsMesh(obstacle.colliderMesh, false)) {
            this._gameResult[drone.team].crash += 1;
            drone.internal_touch();
            this._displayMsg("Drone " + drone.id + " touched an obstacle");
        }
    };
    /**
     * Function used to check collision between 1 drone and an obstacle
     * @param drone
     * @param obstacle
     */
    GameManager.prototype._checkCollisionWithObstacle = function (drone, obstacle) {
        if (GAMEPARAMETERS.compareFlights) {
          return;
        }
        if (obstacle.obsType === "boat") {
            return this._checkCollisionWithSpecialObstacle(drone, obstacle);
        }
        if (drone.colliderMesh
            && drone.colliderMesh.intersectsMesh(obstacle, true)) {
            /**
             * Closest facet check is needed for sphere and cylinder, but just seemed bugged with the box
             * So only need to check intersectMesh for the box
             */
            var closest = void 0;
            if (obstacle["obsType"] == "box") {
                closest = true;
            }
            else {
                obstacle.updateFacetData();
                var projected = BABYLON.Vector3.Zero();
                closest = obstacle.getClosestFacetAtCoordinates(drone.infosMesh.position.x, drone.infosMesh.position.y, drone.infosMesh.position.z, projected);
            }
            if (closest != null) {
                drone.internal_touch();
                var dteam = "blue";
                if (drone.team == "R")
                    dteam = "red";
                this._gameResult[drone.team].obstacle += 1;
                this._displayMsg("Drone n" + drone.id + " touched an obstacle!");
            }
        }
    };
    /**
     * Function to check collision with floor
     * @param drone
     */
    GameManager.prototype._checkCollisionWithFloor = function (drone) {
        if (drone.infosMesh) {
            if (drone.position.z < drone.getMinHeight()) {
                return true;
            }
        }
        return false;
    };
    /**
     * Function to check drone out of the map
     * @param drone
     */
    GameManager.prototype._checkDroneOut = function (drone) {
        if (drone.position !== null) {
            if (drone.position.z > drone.getMaxHeight()) {
              return true;
            }
            return BABYLON.Vector3.Distance(drone.position, BABYLON.Vector3.Zero()) > GAMEPARAMETERS.distances.control;
        }
    };
    /**
     * Function to check game finish
     */
    GameManager.prototype._allDroneAreOut = function () {
        return this._gameResult.L.out + this._gameResult.L.crash === GAMEPARAMETERS.teamSize;
    };
    GameManager.prototype._getGameParameter = function () {
        var parameter = {}, i, swap = function (pos) {
            return {
                x: pos.x,
                y: pos.z,
                z: pos.y
            };
        };
        Object.assign(parameter, this._map);
        this._gameParameter = {};
        Object.assign(this._gameParameter, this._map);
        for (i = 0; i < parameter.obstacles.length; i += 1) {
            parameter.obstacles[i].position = swap(parameter.obstacles[i].position);
            if (parameter.obstacles[i].scale) {
                parameter.obstacles[i].scale = swap(parameter.obstacles[i].scale);
            }
            if (parameter.obstacles[i].rotation) {
                parameter.obstacles[i].rotation = swap(parameter.obstacles[i].rotation);
            }
        }
        parameter.goalPositionLeftTeam = swap(parameter.goalPositionLeftTeam);
        parameter.goalPositionRightTeam = swap(parameter.goalPositionRightTeam);
        return parameter;
    };
    GameManager.prototype._setSpawnDrone = function (x, y, z, index, api, code, team) {
        var default_drone_AI = api.getDroneAI();
        if (default_drone_AI) {
          code = default_drone_AI;
        }
        var ctx = this, base, code_eval = "let drone = new DroneManager(ctx._scene, "
            + index + ', "' + team + '", api);'
            + "let droneMe = function(NativeDate, me, Math, window, DroneManager, GameManager, DroneAPI, DroneLogAPI, DroneAaileFixeAPI, BABYLON, GAMEPARAMETERS) {"
            + "var start_time = (new Date(2070, 0, 0, 0, 0, 0, 0)).getTime();"
            + "Date.now = function () {return start_time + drone._tick * 1000/60;}; "
            + "function Date() {if (!(this instanceof Date)) {throw new Error('Missing new operator');} "
            + "if (arguments.length === 0) {return new NativeDate(Date.now());} else {return new NativeDate(...arguments);}}";
        // Simple desactivation of direct access of all globals
        // It is still accessible in reality, but it will me more visible
        // if people really access them
        if (x !== null && y !== null && z !== null) {
            code_eval += "me.setStartingPosition("
                + x + ", " + y + ", " + z + ");";
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
    GameManager.prototype._setRandomSpawnPosition = function (randomSpawn, team_size, api, code, team) {
        var position, i, position_list = [], center = randomSpawn.position, max_collision = randomSpawn.maxCollision || 10 * team_size, collision_nb = 0;
        function randomSpherePoint(x0, y0, z0, rx0, ry0, rz0) {
            var u = Math.random(),
              v = Math.random(),
              rx = Math.random() * rx0,
              ry = Math.random() * ry0,
              rz = Math.random() * rz0,
              theta = 2 * Math.PI * u,
              phi = Math.acos(2 * v - 1),
              x = x0 + (rx * Math.sin(phi) * Math.cos(theta)),
              y = y0 + (ry * Math.sin(phi) * Math.sin(theta)),
              z = z0 + (rz * Math.cos(phi));
            return new BABYLON.Vector3(x, y, z);
        }
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

    GameManager.prototype.delay = function (callback, millisecond) {
      this._delayed_defer_list.push([callback, millisecond]);
    }
    //**************************** GAME STATES
    /**
     * Function called to init the engine and scene, prepare all the things, then start the game.
     */
    GameManager.prototype._init = function () {
        this._displayMsg("Simulation loading ...");
        function randomSpherePoint(x0, y0, z0, rx0, ry0, rz0) {
            var u = Math.random(), v = Math.random(), rx = Math.random() * rx0, ry = Math.random() * ry0, rz = Math.random() * rz0, theta = 2 * Math.PI * u, phi = Math.acos(2 * v - 1), x = x0 + (rx * Math.sin(phi) * Math.cos(theta)), y = y0 + (ry * Math.sin(phi) * Math.sin(theta)), z = z0 + (rz * Math.cos(phi));
            return new BABYLON.Vector3(x, y, z);
        }
        var _this = this,
          center = GAMEPARAMETERS.randomSpawn.rightTeam.position,
          dispertion = GAMEPARAMETERS.randomSpawn.rightTeam.dispertion;
        if (GAMEPARAMETERS.randomSpawn.rightTeam.dispersed)
          dispertion = {x: 0, y: 0, z: 0};
        this._ground_truth_target = randomSpherePoint(center.x, center.y, center.z, dispertion.x, dispertion.y, dispertion.z);


        this._delayed_defer_list = [];
        // TODO cleanup _gameResult (drop some parts like obstacle)
        this._gameResult = {
            "L": { "goal": 0, "crash": 0, "out": 0, "obstacle": 0 },
            "R": { "goal": 0, "crash": 0, "out": 0, "obstacle": 0 }
        };
        this._dispose();
        console.log("simPlay commented");
        //document.getElementById("simPlay").style.display = "none";
        // ----------------------------------- SIMULATION - 3Dscene
        // Get the canvas
        console.log("canvas commented, use parameter");
        //var canvas = document.getElementById("simCanvas");
        var canvas = this._canvas;
        // Create the Babylon engine
        this._engine = new BABYLON.Engine(canvas, true);
        this._engine.enableOfflineSupport = false;
        // Create the base scene
        this._scene = new BABYLON.Scene(this._engine);
        this._scene.clearColor = new BABYLON.Color4(88/255,171/255,217/255,255/255);
        // this._scene.debugLayer.show();
        // Collisions
        this._scene.collisionsEnabled = true;
        // Lights
        var hemi_north = new BABYLON.HemisphericLight("hemiN", new BABYLON.Vector3(1, -1, 1), this._scene);
        hemi_north.intensity = .75;
        var hemi_south = new BABYLON.HemisphericLight("hemiS", new BABYLON.Vector3(-1, 1, -1), this._scene);
        hemi_south.intensity = .75;
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
        camera.maxz = 40000
        // Render loop
        this._engine.runRenderLoop(function () {
            _this._scene.render();
        });
        console.log("commented window resize");
        // Resize canvas on window resize
        /*window.addEventListener('resize', function () {
            _this._engine.resize();
        });*/
        // ----------------------------------- SIMULATION - Prepare API, Map and Teams
        var on3DmodelsReady = function (ctx) {
            // Get the game parameters
            if (!ctx._map_swapped) {
                GAMEPARAMETERS = ctx._getGameParameter();
                ctx._map_swapped = true;
            }
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
            _this._mapManager = new MapManager(ctx._scene);
            // If positions are defined in GameParameter
            if (GAMEPARAMETERS.spawnPositions && GAMEPARAMETERS.spawnPositions.length > 0) {
                GAMEPARAMETERS.teamSize = GAMEPARAMETERS.spawnPositions.length;
                var pos = void 0;
                // Load the left team code into left team drones
                for (var index = 0; index < GAMEPARAMETERS.spawnPositions.length; index++) {
                    pos = GAMEPARAMETERS.spawnPositions[index];
                    ctx._setSpawnDrone(-pos.x, -pos.y, pos.z, index, lAPI, AIcodeLeft, "L");
                }
                // Load the right team code into right team drones
                for (var index = 0; index < GAMEPARAMETERS.spawnPositions.length; index++) {
                    //set only one drone for right team (the target)
                    if (index === 0) {
                        pos = GAMEPARAMETERS.spawnPositions[index];
                        ctx._setSpawnDrone(pos.x, pos.y, pos.z, index, rAPI, AIcodeRight, "R");
                    }
                }
            }
            else if (GAMEPARAMETERS.randomSpawn) {
                ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.leftTeam, GAMEPARAMETERS.teamSize, lAPI, AIcodeLeft, "L");
                ctx._setRandomSpawnPosition(GAMEPARAMETERS.randomSpawn.rightTeam, GAMEPARAMETERS.teamSize, rAPI, AIcodeRight, "R");
            }
            else {
                // Load the left team code into left team drones
                for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
                    ctx._setSpawnDrone(null, null, null, count, lAPI, AIcodeLeft, "L");
                }
                // Load the right team code into right team drones
                for (var count = 0; count < GAMEPARAMETERS.teamSize; count++) {
                    //set only one drone for right team (the target)
                    if (count === 0) {
                        ctx._setSpawnDrone(null, null, null, count, rAPI, AIcodeRight, "R");
                    }
                }
            }
            // Hide the drone prefab
            DroneManager.Prefab.isVisible = false;
            // Save Game params and AI codes
            // this._saveParamsAndAiCodes();
            //GUI for drones ID display
            var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
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
                _this._displayMsg(count + " ...");
                return RSVP.delay(200);
              };
            }
            for (i = 5; 0 <= i; i -= 1) {
              result.push(countdown(i));
            }
            return result.push(_this._start.bind(_this));
          });
    };
    /**
     * Function called on game start
     */
    GameManager.prototype._start = function () {
        var _this = this,
          waiting_update_count,
          ongoing_update_promise = null;
        _this.finish_deferred = RSVP.defer();
        this._displayMsg("Simulation started.");
        // Timing
        this._game_duration = 0;
        this._totalTime = GAMEPARAMETERS.gameTime;
        this._canUpdate = true;

        return new RSVP.Queue()
          .push(function () {
            promise_list = []
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
            _this._scene.registerBeforeRender(function () {
              // To increase the game speed, increase this value
              //_this._max_step_animation_frame = 10,
                // time delta means that drone are updated every virtual second
                // This is fixed and must not be modified
                // otherwise, it will lead to different scenario results
                // (as drone calculations may be triggered less often)
                //TIME_DELTA = 1000 / 30,
              var TIME_DELTA = 1000 / 60,
                i;

              // init the value on the first step
              waiting_update_count = _this._max_step_animation_frame;

              function triggerUpdateIfPossible() {
                if ((_this._canUpdate) && (ongoing_update_promise === null) && (0 < waiting_update_count)) {
                  //TODO FIX
                  //by duplicating time_delta (to 1000/30) the game runs two times faster (ok)
                  //by adding a delay of a time_delta, it should run 'normal' again
                  //but it runs slower: 1 real minute is around 40 seconds in simulation (but not exactly 40, some miliseconds more)
                  //I don't understand it, there's some kind of (large) overhead here
                  //ongoing_update_promise = new RSVP.Queue(RSVP.all([_this._update(TIME_DELTA), RSVP.delay(TIME_DELTA)]))
                  ongoing_update_promise = _this._update(TIME_DELTA, (waiting_update_count === 1))
                    .push(function () {
                      waiting_update_count -= 1;
                      ongoing_update_promise = null;
                      triggerUpdateIfPossible();
                    })
                    .push(undefined, _this.finish_deferred.reject.bind(_this.finish_deferred));
                }
              }
              triggerUpdateIfPossible();

            });
            return _this.finish_deferred.promise;
          });
    };
    /**
     * Function called after refresh for restart
     */
    GameManager.prototype._restartAfterRefresh = function () {
        if (localStorage.getItem('restart') == 'true') {
            this._init();
            localStorage.setItem('restart', 'false');
        }
    };
    /**
     * Function called after a drone internal crash
     */
    GameManager.prototype._onDroneInternalCrash = function (drone) {
        this._gameResult[drone.team].crash += 1;
        this._displayMsg("Drone " + drone.id + " crashed!");
    };
    /**
     * Function called on game update
     */
    GameManager.prototype._update = function (delta_time, update_dom) {
        var _this = this,
          queue = new RSVP.Queue(),
          i;
        this._updateTiming(delta_time, update_dom);

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
                if (_this._checkCollisionWithFloor(drone)) {
                    _this._gameResult.L.crash += 1;
                    msg = "Drone " + drone.id + " touched the sea!";
                    drone.internal_touch();
                }
                else if (_this._checkDroneOut(drone)) {
                    _this._gameResult.L.out += 1;
                    msg = "Drone " + drone.id + " touched out of limits!";
                    drone.internal_touch();
                }
                else {
                    _this._teamLeft.forEach(function (other) {
                        if (other.can_play() && drone.id != other.id) {
                            _this._checkCollision(drone, other);
                        }
                    });
                    _this._teamRight.forEach(function (other) {
                        if (other.can_play()) {
                            _this._checkCollision(drone, other);
                        }
                    });
                    _this._mapManager.obstacles.forEach(function (obstacle) {
                        _this._checkCollisionWithObstacle(drone, obstacle);
                    });
                }
            }
            if (msg)
                _this._displayMsg(msg);
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
            if (_this._allDroneAreOut()) {
              return _this._finish();
            }
          });
    };
    /**
     * Function called when game end
     */
    GameManager.prototype._finish = function (time_out) {
        this._canUpdate = false;
        if (this._reported_human_position) {
          //mark the reported position with a green point in the map
          var api = new DroneAPI(this, "R"),
            code = `me.start = function() { me.setAcceleration(${GAMEPARAMETERS.derive.acceleration}); me.setDirection(${GAMEPARAMETERS.derive.direction.x},${GAMEPARAMETERS.derive.direction.y},0); }`;
          this._setSpawnDrone(this._reported_human_position.x,
                              this._reported_human_position.y,
                              0.1, 0, api, code, "R");
          var advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI"),
            controlMeshGreen = this._teamRight[1].infosMesh,
            rectGreen = new BABYLON.GUI.Rectangle();
          rectGreen.width = "10px";
          rectGreen.height = "10px";
          rectGreen.cornerRadius = 20;
          rectGreen.color = "white";
          rectGreen.thickness = 0.5;
          rectGreen.background = "green";
          advancedTexture.addControl(rectGreen);
          var labelGreen = new BABYLON.GUI.TextBlock();
          labelGreen.text = "X";
          labelGreen.fontSize = 7;
          rectGreen.addControl(labelGreen);
          rectGreen.linkWithMesh(controlMeshGreen);
          rectGreen.linkOffsetY = 0;
        }
        var msg, human_found = false,
          distance = this.checkHumanDistance(this._reported_human_position);
        if (time_out) {
          msg = "FAIL: timeout. The human position was not reported.";
        } else if (!this._reported_human_position) {
          msg = "FAIL: all drones are down, human position was not reported.";
        } else if (distance > 40) {
          distance = Math.round(distance * 100) / 100;
          msg = "FAIL: human is " + distance + " meters away from the reported position.";
        } else {
          msg = "HUMAN FOUND!";
          human_found = true;
        }
        this._displayMsg(msg);
        this._calculateScore(human_found);
        this._displayResult();
        this._teamLeft.forEach(function (drone) {
            drone.internal_finish();
        });
        this._teamRight.forEach(function (drone) {
            drone.internal_finish();
        });
        return this.finish_deferred.resolve();
    };
    /**
     * Function called on game stop
     */
    GameManager.prototype._dispose = function () {
        // Dispose the engine
        if (this._scene) {
            this._scene.dispose();
        }
    };
    //**************************** UTILS
    GameManager.prototype.YupToZup = function (axes) {
        var tempy = axes.y;
        axes.y = axes.z;
        axes.z = tempy;
    };
    GameManager.prototype.ZupToYup = function (axes) {
        var tempz = axes.z;
        axes.z = axes.y;
        axes.y = tempz;
    };
    return GameManager;
}(console));
