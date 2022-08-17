/// <reference path="./typings/babylon.3.1.d.ts" />
/// <reference path="./DroneAPI.ts" />
/// <reference path="./DroneLogAPI.ts" />
/// <reference path="./DroneAaileFixeAPI.ts" />

var DroneManager = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneManager(scene, id, team, API) {
        var _this = this;
        // Mesh
        this._mesh = null;
        this._controlMesh = null;
        this._colliderBackMesh = null;
        this._canPlay = false;
        this._canCommunicate = false;
        this._maxAcceleration = 0;
        this._maxSpeed = 0;
        this._speed = 0;
        this._acceleration = 0;
        this._direction = BABYLON.Vector3.Zero();
        this._rotationSpeed = 0.4;
        this._maxOrientation = Math.PI / 4;
        this._scene = scene;
        this._canUpdate = true;
        this._id = id;
        this._leader_id = 0;
        this._team = team;
        this._start_wait = 0;
        this._API = API; // var API created on AI evel
        // Create the control mesh
        this._controlMesh = BABYLON.Mesh.CreateBox("droneControl_" + id, 0.01, this._scene);
        this._controlMesh.isVisible = false;
        if (this._team == "R")
            this._controlMesh.rotation = new BABYLON.Vector3(0, Math.PI, 0);
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
                if (_this._team !== "R") {
                  mesh.isVisible = true;
                } else {
                  mesh.isVisible = false;
                  _this._colliderBackMesh = mesh;
                  _this._colliderBackMesh.isVisible = false;
                }
            }
        });
        // Team color
        if (!DroneManager.PrefabBlueMat || !DroneManager.PrefabRedMat) {
            DroneManager.PrefabBlueMat = new BABYLON.StandardMaterial("blueTeamMat", scene);
            DroneManager.PrefabBlueMat.diffuseTexture = new BABYLON.Texture("assets/drone/drone_bleu.jpg", scene);
            DroneManager.PrefabRedMat = new BABYLON.StandardMaterial("redTeamMat", scene);
            DroneManager.PrefabRedMat.diffuseTexture = new BABYLON.Texture("assets/drone/drone_rouge.jpg", scene);
        }
        this._propellerAnimMeshes = [];
        this._mesh.getChildren().forEach(function (mesh) {
            // Propeller animation
            if (mesh.name.substring(mesh.name.length - 7, mesh.name.length - 1) == "helice") {
                var anim = new BABYLON.Animation("propellerTurning_" + mesh.name, "rotation.y", 20, BABYLON.Animation.ANIMATIONTYPE_FLOAT, BABYLON.Animation.ANIMATIONLOOPMODE_CYCLE);
                var keys = [
                    { frame: 0, value: 0 },
                    { frame: 2, value: Math.PI },
                    { frame: 4, value: Math.PI * 2 }
                ];
                anim.setKeys(keys);
                mesh.animations.push(anim);
                _this._scene.beginAnimation(mesh, 0, 4, true);
                _this._propellerAnimMeshes.push(mesh);
            }
            else {
                if (_this._team == "L") {
                    mesh.material = DroneManager.PrefabBlueMat;
                }
                else if (_this._team == "R") {
                    mesh.material = DroneManager.PrefabRedMat;
                }
            }
        });
        // jIO auto save
        // TO DO : Faire ça avec un vrai timer, puisque le setInterval est cassé si on met en pause
        this._internal_jIO_save();
    }
    DroneManager.prototype._swapAxe = function (vector) {
        return new BABYLON.Vector3(vector.x, vector.z, vector.y);
    };
    Object.defineProperty(DroneManager.prototype, "leader_id", {
        //*************************************************** ACCESSOR *****************************************************
        get: function () { return this._leader_id; },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(DroneManager.prototype, "id", {
        //*************************************************** ACCESSOR *****************************************************
        get: function () { return this._id; },
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
    Object.defineProperty(DroneManager.prototype, "rotation", {
        get: function () { return this._swapAxe(this._controlMesh.rotation); },
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
            var t = this.team === "L" ? 1 : -1;
            return new BABYLON.Vector3(t * this._direction.x, this._direction.y, t * this._direction.z);
        },
        enumerable: true,
        configurable: true
    });
    //*************************************************** FUNCTIONS ****************************************************
    //#region ------------------ Internal
    // Function called by the GameManager
    // Set internal variables then call API function
    DroneManager.prototype.internal_start = function () {
        this._maxAcceleration = GAMEPARAMETERS.drone.maxAcceleration;
        if (this._team == "R") {
          if (GAMEPARAMETERS.derive) {
            this._maxSpeed = GAMEPARAMETERS.derive.speed;
          } else {
            this._maxSpeed = 0;
          }
        } else {
          this._maxSpeed = this._API.getMaxSpeed();
        }
        this._canPlay = true;
        this._canCommunicate = true;
        try {
          return this.onStart();
        } catch (error) {
          console.warn('Drone crashed on start due to error:', error);
          this._internal_crash();
        }
    };
    DroneManager.prototype.internal_update = function (delta_time) {
        var context = this;
        if (this._controlMesh) {
            if (context._rotationTarget) {
                var rotStep = BABYLON.Vector3.Zero();
                var diff = context._rotationTarget.subtract(context._controlMesh.rotation);
                if (diff.x >= 1)
                    rotStep.x = 1;
                else
                    rotStep.x = diff.x;
                if (diff.y >= 1)
                    rotStep.y = 1;
                else
                    rotStep.y = diff.y;
                if (diff.z >= 1)
                    rotStep.z = 1;
                else
                    rotStep.z = diff.z;
                if (rotStep == BABYLON.Vector3.Zero()) {
                    context._rotationTarget = null;
                    return;
                }
                var newrot = new BABYLON.Vector3(context._controlMesh.rotation.x + (rotStep.x * context._rotationSpeed), context._controlMesh.rotation.y + (rotStep.y * context._rotationSpeed), context._controlMesh.rotation.z + (rotStep.z * context._rotationSpeed));
                context._controlMesh.rotation = newrot;
            }
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
            context._mesh.rotation = new BABYLON.Vector3(orientationValue * context._direction.z, 0, -orientationValue * context._direction.x);
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
                    if (context._start_wait > 0) {
                      context._API.wait(context, context._wait);
                    }
                  });
            }
            return;
        }
        return;
    };
    DroneManager.prototype.internal_touch = function () {
        var _this = this;
        this.setRotationBy(0, 0, 0);
        this.setDirection(0, 0, -1);
        this.setAcceleration(this._maxAcceleration);
        this._canPlay = false;
        if (this._propellerAnimMeshes != null) {
            try {
                this._propellerAnimMeshes.forEach(function (mesh) {
                    _this._scene.stopAnimation(mesh);
                });
            }
            catch (ex) { }
            this._propellerAnimMeshes = null;
        }
        this._canCommunicate = false;
        this._controlMesh = null;
        this._mesh = null;
        this.onTouched();
    };
    DroneManager.prototype._internal_crash = function () {
        var _this = this;
        if (this._propellerAnimMeshes !== null) {
            try {
                this._propellerAnimMeshes.forEach(function (mesh) {
                    _this._scene.stopAnimation(mesh);
                });
            }
            catch (ex) { }
            this._propellerAnimMeshes = null;
        }
        this._canCommunicate = false;
        this._controlMesh = null;
        this._mesh = null;
        this._canPlay = false;
        this.onTouched();
        this._API._gameManager._onDroneInternalCrash(this);
    };
    DroneManager.prototype._internal_dispose = function () {
        if (this._mesh) {
            this._mesh.dispose();
            this._mesh = null;
            this._controlMesh.dispose();
            this._controlMesh = null;
        }
    };
    DroneManager.prototype.internal_finish = function () {
        this._canPlay = false;
        this._canCommunicate = false;
        this._controlMesh = null;
    };
    DroneManager.prototype.can_play = function () {
        return this._canPlay;
    };
    DroneManager.prototype._internal_jIO_save = function () {
        if (this._controlMesh) {
            var timestamp = Date.now();
            return DroneManager.jIOstorage.put(this._id + "_" + this._team + "_" + timestamp, {
                type: "state",
                id: this._id,
                team: this._team,
                timestamp: timestamp,
                direction: {
                    x: this._direction.x,
                    y: this._direction.z,
                    z: this._direction.y
                },
                position: {
                    x: this._controlMesh.position.x,
                    y: this._controlMesh.position.z,
                    z: this._controlMesh.position.y
                },
                rotation: {
                    x: this._controlMesh.rotation.x,
                    y: this._controlMesh.rotation.z,
                    z: this._controlMesh.rotation.y
                },
                speed: this._speed
            });
        }
    };
    //#endregion
    //#region ------------------ Accessible from AI
    // Function callable by "me.functionName()" in AI code
    // -- Starting info
    /**
     * Set the starting position of the drone
     * Take x,y,z coordinates as parameters
     */
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
    //#region -- Movements
    /**
     * Set the drone acceleration
     * It is in meter / second
     */
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
    //#region -- Movements
    /**
     * Set the human derive acceleration
     * It is in meter / second
     * It has no cap to allow constant speed
     */
    DroneManager.prototype.setHumanAcceleration = function (factor) {
        if (!this._canPlay)
            return;
        if (isNaN(factor)){
          throw new Error('Acceleration must be a number');
        }
        this._acceleration = factor;
    };
    /**
     * Set the drone direction
     */
    DroneManager.prototype.setDirection = function (x, y, z) {
        if (!this._canPlay)
            return;
        if(isNaN(x) || isNaN(y) || isNaN(z)){
          throw new Error('Direction coordinates must be numbers');
        }
        this._direction = new BABYLON.Vector3(x, z, y).normalize();
    };
    /**
     * Set the drone rotation
     */
    DroneManager.prototype.setRotation = function (x, y, z) {
        if (!this._canPlay)
            return;
        if (this._team == "R")
            y += Math.PI;
        this._rotationTarget = new BABYLON.Vector3(x, z, y);
    };
    /**
     * Add this rotation to the actual drone rotation
     */
    DroneManager.prototype.setRotationBy = function (x, y, z) {
        if (!this._canPlay)
            return;
        this._rotationTarget = new BABYLON.Vector3(this.rotation.x + x, this.rotation.y + z, this.rotation.z + y);
    };
    /**
     * Set a target point to move
     */
    DroneManager.prototype.setTargetCoordinates = function (x, y, z, r) {
      if (!this._canPlay)
        return;
      var coordinates = this._API.processCoordinates(x, y, z, r);
      //HACK to ignore checkpoints high altitudes //TODO fix altitude issue
      if (z > 500) {
        coordinates.z = this._controlMesh.position.y;
      }
      coordinates.x -= this._controlMesh.position.x;
      coordinates.y -= this._controlMesh.position.z;
      coordinates.z -= this._controlMesh.position.y;
      if (this.team == "R")
        coordinates.y = -coordinates.y;
      this.setDirection(coordinates.x, coordinates.y, coordinates.z);
      this.setAcceleration(this._maxAcceleration);
      return;
    };
    //#endregion
    //#region -- Messaging
    /**
     * Send a message to team drones
     * @param msg The message to send
     * @param id The targeted drone. -1 or nothing to broadcast
     */
    DroneManager.prototype.sendMsg = function (msg, id) {
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
    /**
     * Perform a console.log with drone id + the message
     */
    DroneManager.prototype.log = function (msg) { };
    //#endregion
    //#region -- Game informations
    /**
     * Get drone max height
     */
    DroneManager.prototype.getMaxHeight = function () {
        return this._API.getMaxHeight();
    };
    /**
     * Get drone min height
     */
    DroneManager.prototype.getMinHeight = function () {
        return this._API.getMinHeight();
    };
    /**
     * Get drone initial altitude
     */
    DroneManager.prototype.getInitialAltitude = function () {
        return this._API.getInitialAltitude();
    };
    /**
     * Get drone absolute altitude
     */
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
    /**
     * get if drone detects the human position
     */
    DroneManager.prototype.isHumanPositionSpotted = function () {
        if (!this._canCommunicate)
            return;
        return this._API.isHumanPositionSpotted(this);
    };
    /**
     * get current drone position
     */
    DroneManager.prototype.getCurrentPosition = function () {
        if (this._controlMesh)
          return this._API.processCurrentPosition(
            this._controlMesh.position.x,
            this._controlMesh.position.z,
            this._controlMesh.position.y
          );
        return null;
    };
    /**
     * Set the drone altitude
     * @param altitude information to be set
     */
    DroneManager.prototype.setAltitude = function (altitude) {
        if (!this._canPlay)
          return;
        altitude = this._API.setAltitude(altitude);
        altitude -= this._controlMesh.position.y;
        this.setDirection(this._direction.x, this._direction.y, altitude);
        this.setAcceleration(this._maxAcceleration);
    };
    /**
     * Make the drone wait
     * @param time to wait
     */
    DroneManager.prototype.wait = function (time) {
        if (!this._canPlay)
          return;
        if (this._start_wait === 0) {
          this._start_wait = this._API._gameManager._game_duration;
        }
        this._wait = time;
    };
    /**
     * Set the reported human position
     * @param position information to be set
     */
    DroneManager.prototype.reportHumanPosition = function (position) {
        this._API._gameManager.reportHumanPosition(position);
    };
    /**
     * get log flight parameters
     */
    DroneManager.prototype.getFlightParameters = function () {
        if (this._API.getFlightParameters)
          return this._API.getFlightParameters();
        return null;
    };
    /**
     * get yaw flight parameters
     */
    DroneManager.prototype.getYaw = function () {
        //TODO
        return 0;
    };
    /**
     * do parachute
     */
    DroneManager.prototype.doParachute = function () {
        //TODO
        return null;
    };
    /**
     * exit
     */
    DroneManager.prototype.exit = function () {
        //TODO
        this.setDirection(0, 0, 0);
        return null;
    };
    /**
     * Set the drone last checkpoint reached
     * @param checkpoint to be set
     */
    DroneManager.prototype.setCheckpoint = function (checkpoint) {
        //TODO
        return null;
    };
    //#endregion
    //#endregion
    //#region ------------------ To be defined in AI code
    // Function called on evt.
    // These functions must be defined in the AI code
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
     * Function called when drone die (crash or collision)
     */
    DroneManager.prototype.onTouched = function () { };
    ;
    /**
     * Function called when a message is received
     * @param msg The message
     */
    DroneManager.prototype.onGetMsg = function (msg) { };
    ;
    /**
     * Function called when drone finishes the detection process
     * @param human_detected true or false
     */
    DroneManager.prototype.onCapture = function (human_detected) { };
    ;
    return DroneManager;
}());
