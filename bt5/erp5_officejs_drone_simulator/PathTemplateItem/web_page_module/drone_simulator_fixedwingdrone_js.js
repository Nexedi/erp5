/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true */

/************************** FIXED WING DRONE API ****************************/
var FixedWingDroneAPI = /** @class */ (function () {
  "use strict";

  // var TAKEOFF_RADIUS = 60,
  var DEFAULT_SPEED = 16,
    EARTH_GRAVITY = 9.81,
    LOITER_LIMIT = 30,
    LOITER_RADIUS_FACTOR = 0.60,
    LOITER_SPEED_FACTOR = 1.5,
    MAX_ACCELERATION = 6,
    MAX_DECELERATION = 1,
    MIN_SPEED = 12,
    MAX_SPEED = 26,
    MAX_ROLL = 35,
    MIN_PITCH = -20,
    MAX_PITCH = 25,
    MAX_CLIMB_RATE = 8,
    MAX_SINK_RATE = 3;

  //** CONSTRUCTOR
  function FixedWingDroneAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._map_dict = this._mapManager.getMapInfo();
    this._flight_parameters = flight_parameters;
    this._id = id;
    this._drone_info = drone_info;
    this._loiter_radius = 0;
    this._last_loiter_point_reached = -1;
    //this._start_altitude = 0;
    //this._last_altitude_point_reached = -1;
    this._loiter_mode = false;
    this._drone_dict_list = [];
  }
  /*
  ** Function called on start phase of the drone, just before onStart AI script
  */
  FixedWingDroneAPI.prototype.internal_start = function (drone) {
    drone._maxDeceleration = this.getMaxDeceleration();
    drone._maxAcceleration = this.getMaxAcceleration();
    drone._minSpeed = this.getMinSpeed();
    drone._maxSpeed = this.getMaxSpeed();
    drone._speed = drone._targetSpeed = this.getInitialSpeed();
    drone._minPitchAngle = this.getMinPitchAngle();
    drone._maxPitchAngle = this.getMaxPitchAngle();
    drone._maxRollAngle = this.getMaxRollAngle();
    drone._maxSinkRate = this.getMaxSinkRate();
    drone._maxClimbRate = this.getMaxClimbRate();
    drone._maxOrientation = this.getMaxOrientation();
    return;
  };
  /*
  ** Function called on every drone update, right before onUpdate AI script
  */
  FixedWingDroneAPI.prototype.internal_update = function (context, delta_time) {
    var diff, newrot, orientationValue, rotStep, updateSpeed;

    //TODO rotation
    if (context._rotationTarget) {
      rotStep = BABYLON.Vector3.Zero();
      diff = context._rotationTarget.subtract(context._controlMesh.rotation);
      rotStep.x = (diff.x >= 1) ? 1 : diff.x;
      rotStep.y = (diff.y >= 1) ? 1 : diff.y;
      rotStep.z = (diff.z >= 1) ? 1 : diff.z;
      if (rotStep === BABYLON.Vector3.Zero()) {
        context._rotationTarget = null;
        return;
      }
      newrot = new BABYLON.Vector3(context._controlMesh.rotation.x +
                                    (rotStep.x * context._rotationSpeed),
                                    context._controlMesh.rotation.y +
                                    (rotStep.y * context._rotationSpeed),
                                    context._controlMesh.rotation.z +
                                    (rotStep.z * context._rotationSpeed)
                                  );
      context._controlMesh.rotation = newrot;
    }

    this._updateSpeed(context, delta_time);
    this._updateDirection(context, delta_time);

    updateSpeed = context._speed * delta_time / 1000;
    if (context._direction.x !== 0 ||
        context._direction.y !== 0 ||
        context._direction.z !== 0) {
      context._controlMesh.position.addInPlace(new BABYLON.Vector3(
        context._direction.x * updateSpeed,
        context._direction.y * updateSpeed,
        context._direction.z * updateSpeed
      ));
    }
    //TODO rotation
    orientationValue = context._maxOrientation *
      (context._speed / context._maxSpeed);
    context._mesh.rotation =
      new BABYLON.Vector3(orientationValue * context._direction.z, 0,
                          -orientationValue * context._direction.x);
    context._controlMesh.computeWorldMatrix(true);
    context._mesh.computeWorldMatrix(true);
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  FixedWingDroneAPI.prototype.internal_post_update = function (drone) {
    var _this = this, drone_position = drone.getCurrentPosition(), drone_info;
    if (_this._loiter_mode) {
      _this.loiter(drone);
    }
    /*if (_this._start_altitude > 0) { //TODO move start_altitude here
      _this.reachAltitude(drone);
    }*/
    if (drone_position) {
      drone_info = {
        'altitudeRel' : drone_position.z,
        'altitudeAbs' : _this._mapManager.getMapInfo().start_AMSL +
          drone_position.z,
        'latitude' : drone_position.x,
        'longitude' : drone_position.y
      };
      _this._drone_dict_list[_this._id] = drone_info;
      //broadcast drone info using internal msg
      _this._gameManager._droneList.forEach(function (drone) {
        if (drone.id !== _this._id) {
          drone.internal_getMsg(drone_info, _this._id);
        }
      });
    }
  };

  FixedWingDroneAPI.prototype._updateSpeed = function (drone, delta_time) {
    var speed = drone.getSpeed(), speedDiff, speedUpdate;
    if (speed !== this._targetSpeed) {
      speedDiff = this._targetSpeed - speed;
      speedUpdate = drone._acceleration * delta_time / 1000;
      if (Math.abs(speedDiff) < Math.abs(speedUpdate)) {
        drone._speed = this._targetSpeed;
        drone._acceleration = 0;
      } else {
        drone._speed += speedUpdate;
      }
    }
  };

  FixedWingDroneAPI.prototype._updateDirection = function (drone, delta_time) {
    var horizontalCoeff, newX, newY, newZ;
    [newX, newZ] = this._getNewYaw(drone, delta_time);
    newY = this._getNewAltitude(drone);

    horizontalCoeff = Math.sqrt(
      (
        Math.pow(drone.getSpeed(), 2) - Math.pow(newY, 2)
      ) / (
        Math.pow(newX, 2) + Math.pow(newZ, 2)
      )
    );
    newX *= horizontalCoeff;
    newZ *= horizontalCoeff;
    // swap y and z axis so z axis represents altitude
    drone.setDirection(newX, newZ, newY);
  };

  FixedWingDroneAPI.prototype._getNewYaw = function (drone, delta_time) {
    // swap y and z axis so z axis represents altitude
    var bearing = this._computeBearing(
        drone.position.x,
        drone.position.y,
        drone._targetCoordinates.x,
        drone._targetCoordinates.y
      ),
      yaw = drone.getYaw(),
      yawDiff = this._computeYawDiff(yaw, bearing),
      yawUpdate = this.getYawVelocity(drone) * delta_time / 1000;

    if (yawUpdate >= Math.abs(yawDiff)) {
      yawUpdate = yawDiff;
    } else if (yawDiff < 0) {
      yawUpdate *= -1;
    }
    yaw += yawUpdate;

    // trigonometric circle is east oriented, yaw angle is clockwise
    yaw = this._toRad(-yaw + 90);
    return [Math.cos(yaw), Math.sin(yaw)];
  };

  FixedWingDroneAPI.prototype._getNewAltitude = function (drone) {
    // swap y and z axis so z axis represents altitude
    var altitudeDiff = drone._targetCoordinates.z - drone.position.z,
      verticalSpeed;

    if (altitudeDiff >= 0) {
      verticalSpeed = this._computeVerticalSpeed(
        altitudeDiff,
        this.getMaxClimbRate(),
        drone.getSpeed(),
        this.getMaxPitchAngle()
      );
    } else {
      verticalSpeed = -this._computeVerticalSpeed(
        Math.abs(altitudeDiff),
        this.getMaxSinkRate(),
        drone.getSpeed(),
        -this.getMinPitchAngle()
      );
    }
    return verticalSpeed;
  };

  FixedWingDroneAPI.prototype.setRotation = function (drone, x, y, z) {
    //TODO rotation
    drone._rotationTarget = new BABYLON.Vector3(x, z, y);
  };

  FixedWingDroneAPI.prototype.setRotationBy = function (drone, x, y, z) {
    //TODO rotation
    drone._rotationTarget = new BABYLON.Vector3(drone.rotation.x + x,
                                                drone.rotation.y + z,
                                                drone.rotation.z + y);
  };

  FixedWingDroneAPI.prototype.setAltitude = function (drone, altitude) {
    drone._targetCoordinates.z = altitude;
  };

  FixedWingDroneAPI.prototype.setSpeed = function (drone, speed) {
    this._targetSpeed = Math.max(
      Math.min(speed, this.getMaxSpeed()),
      this.getMinSpeed()
    );

    drone._acceleration = (this._targetSpeed > drone.getSpeed())
      ? this.getMaxAcceleration() : -this.getMaxDeceleration();
  };

  FixedWingDroneAPI.prototype.setStartingPosition = function (drone, x, y, z) {
    if (!drone._canPlay) {
      if (z <= 0.05) {
        z = 0.05;
      }
      drone._controlMesh.position = new BABYLON.Vector3(x, z, y);
    }
    drone._controlMesh.computeWorldMatrix(true);
    drone._mesh.computeWorldMatrix(true);
  };

  FixedWingDroneAPI.prototype.internal_getMsg = function (msg, id) {
    this._drone_dict_list[id] = msg;
  };

  FixedWingDroneAPI.prototype.set_loiter_mode = function (radius) {
    this._loiter_mode = true;
    if (radius && radius > LOITER_LIMIT) {
      this._loiter_radius = radius * LOITER_RADIUS_FACTOR;
      this._loiter_center = this._last_target;
      this._loiter_coordinates = [];
      this._last_loiter_point_reached = -1;
      var x1, y1, angle;
      //for (var angle = 0; angle <360; angle+=8){ //counter-clockwise
      for (angle = 360; angle > 0; angle -= 8) { //clockwise
        x1 = this._loiter_radius *
          Math.cos(this._toRad(angle)) + this._loiter_center.x;
        y1 = this._loiter_radius *
          Math.sin(this._toRad(angle)) + this._loiter_center.y;
        this._loiter_coordinates.push(
          this.getCurrentPosition(x1, y1, this._loiter_center.z)
        );
      }
    }
  };
  FixedWingDroneAPI.prototype.internal_setTargetCoordinates =
    function (drone, coordinates, loiter) {
      if (!loiter) {
        this._loiter_mode = false;
        //save last target point to use as next loiter center
        this._last_target = coordinates;
      }
    };
  FixedWingDroneAPI.prototype.sendMsg = function (msg, to) {
    var _this = this,
      droneList = _this._gameManager._droneList;
    _this._gameManager.delay(function () {
      if (to < 0) {
        // Send to all drones
        droneList.forEach(function (drone) {
          if (drone.infosMesh) {
            try {
              drone.onGetMsg(msg);
            } catch (error) {
              console.warn('Drone crashed on sendMsg due to error:', error);
              drone._internal_crash();
            }
          }
        });
      } else {
        // Send to specific drone
        if (droneList[to].infosMesh) {
          try {
            droneList[to].onGetMsg(msg);
          } catch (error) {
            console.warn('Drone crashed on sendMsg due to error:', error);
            droneList[to]._internal_crash();
          }
        }
      }
    }, _this._flight_parameters.latency.communication);
  };
  FixedWingDroneAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  FixedWingDroneAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "map"].includes(name)) {
      return this._gameManager.gameParameter[name];
    }
  };
  /*
  ** Converts geo latitude-longitud coordinates (º) to x,y plane coordinates (m)
  */
  FixedWingDroneAPI.prototype.processCoordinates = function (lat, lon, z) {
    if (isNaN(lat) || isNaN(lon) || isNaN(z)) {
      throw new Error('Target coordinates must be numbers');
    }
    var x = this._mapManager.longitudToX(lon, this._map_dict.width),
      y = this._mapManager.latitudeToY(lat, this._map_dict.depth),
      position = this._mapManager.normalize(x, y, this._map_dict),
      processed_coordinates;
    if (z > this._map_dict.start_AMSL) {
      z -= this._map_dict.start_AMSL;
    }
    processed_coordinates = {
      x: position[0],
      y: position[1],
      z: z
    };
    //this._last_altitude_point_reached = -1;
    //this.takeoff_path = [];
    return processed_coordinates;
  };
  FixedWingDroneAPI.prototype.getCurrentPosition = function (x, y, z) {
    return this._mapManager.convertToGeoCoordinates(x, y, z, this._map_dict);
  };
  FixedWingDroneAPI.prototype.loiter = function (drone) {
    if (this._loiter_radius > LOITER_LIMIT) {
      var drone_pos = drone.getCurrentPosition(),
        min = 9999,
        min_i,
        i,
        d,
        next_point;
      //shift loiter circle to nearest point
      if (this._last_loiter_point_reached === -1) {
        if (!this.shifted) {
          drone._maxSpeed = drone._maxSpeed * LOITER_SPEED_FACTOR;
          for (i = 0; i < this._loiter_coordinates.length; i += 1) {
            d = this._mapManager.latLonDistance([drone_pos.x, drone_pos.y],
                                                [this._loiter_coordinates[i].x,
                                                this._loiter_coordinates[i].y]);
            if (d < min) {
              min = d;
              min_i = i;
            }
          }
          this._loiter_coordinates = this._loiter_coordinates.concat(
            this._loiter_coordinates.splice(0, min_i)
          );
          this.shifted = true;
        }
      } else {
        this.shifted = false;
      }
      //stop
      if (this._last_loiter_point_reached ===
          this._loiter_coordinates.length - 1) {
        if (drone._maxSpeed !== this.getMaxSpeed()) {
          drone._maxSpeed = this.getMaxSpeed();
        }
        drone.setDirection(0, 0, 0);
        return;
      }
      //loiter
      next_point =
        this._loiter_coordinates[this._last_loiter_point_reached + 1];
      this.internal_setTargetCoordinates(drone, next_point, true);
      if (this._mapManager.latLonDistance([drone_pos.x, drone_pos.y],
                                          [next_point.x, next_point.y]) < 1) {
        this._last_loiter_point_reached += 1;
        if (this._last_loiter_point_reached ===
            this._loiter_coordinates.length - 1) {
          return;
        }
        next_point = this._loiter_coordinates[
          this._last_loiter_point_reached + 1
        ];
        this.internal_setTargetCoordinates(drone, next_point, true);
      }
    }
  };
  FixedWingDroneAPI.prototype.getDroneAI = function () {
    return null;
  };
  FixedWingDroneAPI.prototype.getMinSpeed = function () {
    return this._flight_parameters.drone.minSpeed || MIN_SPEED;
  };
  FixedWingDroneAPI.prototype.getMaxSpeed = function () {
    return this._flight_parameters.drone.maxSpeed || MAX_SPEED;
  };
  FixedWingDroneAPI.prototype.getInitialSpeed = function () {
    return this._flight_parameters.drone.speed || DEFAULT_SPEED;
  };
  FixedWingDroneAPI.prototype.getMaxDeceleration = function () {
    return this._flight_parameters.drone.maxDeceleration || MAX_DECELERATION;
  };
  FixedWingDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration || MAX_ACCELERATION;
  };
  FixedWingDroneAPI.prototype.getMinPitchAngle = function () {
    return this._flight_parameters.drone.minPitchAngle || MIN_PITCH;
  };
  FixedWingDroneAPI.prototype.getMaxPitchAngle = function () {
    return this._flight_parameters.drone.maxPitchAngle || MAX_PITCH;
  };
  FixedWingDroneAPI.prototype.getMaxRollAngle = function () {
    return this._flight_parameters.drone.maxRoll || MAX_ROLL;
  };
  FixedWingDroneAPI.prototype.getMaxSinkRate = function () {
    return this._flight_parameters.drone.maxSinkRate || MAX_SINK_RATE;
  };
  FixedWingDroneAPI.prototype.getMaxClimbRate = function () {
    return this._flight_parameters.drone.maxClimbRate || MAX_CLIMB_RATE;
  };
  FixedWingDroneAPI.prototype.getMaxOrientation = function () {
    //TODO should be a game parameter (but how to force value to PI quarters?)
    return Math.PI / 4;
  };
  FixedWingDroneAPI.prototype.getYawVelocity = function (drone) {
    return 360 * EARTH_GRAVITY
      * Math.tan(this._toRad(this.getMaxRollAngle()))
      / (2 * Math.PI * drone.getSpeed());
  };
  FixedWingDroneAPI.prototype.getYaw = function (drone) {
    var direction = drone.worldDirection;
    return this._computeBearing(0, 0, direction.x, direction.z);
  };
  FixedWingDroneAPI.prototype._computeBearing = function (x1, z1, x2, z2) {
    return this._toDeg(Math.atan2(x2 - x1, z2 - z1));
  };
  FixedWingDroneAPI.prototype._computeYawDiff = function (yaw1, yaw2) {
    var diff = yaw2 - yaw1;
    diff += (diff > 180) ? -360 : (diff < -180) ? 360 : 0;
    return diff;
  };
  FixedWingDroneAPI.prototype._computeVerticalSpeed =
    function (altitude_diff, max_climb_rate, speed, max_pitch) {
      var maxVerticalSpeed = Math.min(altitude_diff, max_climb_rate);
      return (this._toDeg(Math.asin(maxVerticalSpeed / speed)) > max_pitch)
        ? speed * Math.sin(this._toRad(max_pitch))
        : maxVerticalSpeed;
    };
  FixedWingDroneAPI.prototype._toRad = function (angle) {
    return angle * Math.PI / 180;
  };
  FixedWingDroneAPI.prototype._toDeg = function (angle) {
    return angle * 180 / Math.PI;
  };
  FixedWingDroneAPI.prototype.getClimbRate = function (drone) {
    return drone.worldDirection.y * drone.getSpeed();
  };
  FixedWingDroneAPI.prototype.triggerParachute = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    drone.setTargetCoordinates(drone_pos.x, drone_pos.y, 5);
  };
  FixedWingDroneAPI.prototype.landed = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    return Math.floor(drone_pos.z) < 10;
  };
  FixedWingDroneAPI.prototype.exit = function () {
    return;
  };
  FixedWingDroneAPI.prototype.getInitialAltitude = function () {
    return 0;
  };
  FixedWingDroneAPI.prototype.getAltitudeAbs = function (altitude) {
    return altitude;
  };
  FixedWingDroneAPI.prototype.getMinHeight = function () {
    return 0;
  };
  FixedWingDroneAPI.prototype.getMaxHeight = function () {
    return 800;
  };
  FixedWingDroneAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return FixedWingDroneAPI;
}());
