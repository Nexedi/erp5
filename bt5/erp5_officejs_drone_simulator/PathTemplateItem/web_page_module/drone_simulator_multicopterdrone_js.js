/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true */

/************************** MULTICOPTER DRONE API ****************************/
var MulticopterDroneAPI = /** @class */ (function () {
  "use strict";

  var DEFAULT_SPEED = 5,
    DEFAULT_TAKEOFF_ALTITUDE = 7,
    MAX_ACCELERATION = 1,
    MAX_DECELERATION = 3,
    MIN_SPEED = 0,
    MAX_SPEED = 7,
    MAX_ROLL = 13,
    MIN_APPROACH_SPEED = 0.1,
    SPEED_FACTOR = 1.2, //some drones look to fly faster than the speed expected
    TAKE_OFF_FACTOR = 20,
    YAW_ACCEPTANCE = 1;

  //** CONSTRUCTOR
  function MulticopterDroneAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._map_dict = this._mapManager.getMapInfo();
    this._flight_parameters = flight_parameters;
    this._id = id;
    this._drone_info = drone_info;
    //this._start_altitude = 0;
    this._is_landing = false;
    this._is_ready_to_fly = false;
    this._drone_dict_list = [];
  }
  Object.defineProperty(MulticopterDroneAPI.prototype, "isCollidable", {
    get: function () { return true; },
    enumerable: true,
    configurable: true
  });
  /*
  ** Function called on start phase of the drone, just before onStart AI script
  */
  MulticopterDroneAPI.prototype.internal_start = function (drone) {
    drone._maxDeceleration = this.getMaxDeceleration();
    if (drone._maxDeceleration <= 0) {
      throw new Error('max deceleration must be superior to 0');
    }
    drone._maxAcceleration = this.getMaxAcceleration();
    if (drone._maxAcceleration <= 0) {
      throw new Error('max acceleration must be superior to 0');
    }
    drone._minSpeed = MIN_SPEED;
    drone._maxSpeed = this.getMaxSpeed();
    if (drone._maxSpeed <= 0) {
      throw new Error('Max speed must be superior to 0');
    }
    drone._speed = drone._targetSpeed = this.getInitialSpeed();
    drone._maxRollAngle = this.getMaxRollAngle();
    if (drone._maxRollAngle <= 0) {
      throw new Error('max roll angle must be superior to 0');
    }
    drone._maxCommandFrequency = this.getMaxCommandFrequency();
    if (drone._maxCommandFrequency <= 0) {
      throw new Error('max command frequence must be superior to 0');
    }
    return;
  };
  /*
  ** Function called on every drone update, right before onUpdate AI script
  */
  MulticopterDroneAPI.prototype.internal_position_update =
    function (context, delta_time) {
      var currentGeoCoordinates = this._mapManager.convertToGeoCoordinates(
          context.position.x,
          context.position.y,
          context.position.z
        ),
        targetCoordinates = this._mapManager.convertToGeoCoordinates(
          context._targetCoordinates.x,
          context._targetCoordinates.y,
          context._targetCoordinates.z
        ),
        bearing = this._computeBearing(
          currentGeoCoordinates.latitude,
          currentGeoCoordinates.longitude,
          targetCoordinates.latitude,
          targetCoordinates.longitude
        ),
        newYaw = this._getNewYaw(context, bearing, delta_time);

      if (!this.isReadyToFly() && !this.isLanding()
          && context.position.z >= DEFAULT_TAKEOFF_ALTITUDE) {
        this._is_ready_to_fly = true;
        context._speed = 0;
      }

      if (Math.abs(bearing - newYaw) < YAW_ACCEPTANCE) {
        this._updateSpeed(context, currentGeoCoordinates, targetCoordinates,
                          delta_time);
      }
      this._updatePosition(context, newYaw, delta_time);

      context._controlMesh.computeWorldMatrix(true);
      context._mesh.computeWorldMatrix(true);
    };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  MulticopterDroneAPI.prototype.internal_info_update = function (drone) {
    var _this = this, drone_position = drone.getCurrentPosition(), drone_info;
    /*if (_this._start_altitude > 0) { //TODO move start_altitude here
      _this.reachAltitude(drone);
    }*/
    if (drone_position) {
      drone_info = {
        'altitudeRel' : drone_position.altitude,
        'altitudeAbs' : _this._mapManager.getMapInfo().start_AMSL +
          drone_position.altitude,
        'latitude' : drone_position.latitude,
        'longitude' : drone_position.longitude,
        'yaw': drone.getYaw(),
        'speed': drone.getSpeed(),
        'climbRate': drone.getClimbRate(),
        'timestamp': drone_position.timestamp
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

  MulticopterDroneAPI.prototype._updateSpeed =
    function (drone, currentGeoCoordinates, targetCoordinates, delta_time) {
      var speed = drone.get3DSpeed(), speedDiff, speedUpdate,
        distance = Math.sqrt(
          Math.pow(
            this._mapManager.mapUtils.latLonDistance(
              [currentGeoCoordinates.latitude, currentGeoCoordinates.longitude],
              [targetCoordinates.latitude, targetCoordinates.longitude]
            ),
            2
          ) + Math.pow(
            targetCoordinates.altitude - currentGeoCoordinates.altitude,
            2
          )
        );

      if (this._targetSpeed > distance) {
        drone._acceleration = this.getMaxDeceleration();
        this._targetSpeed = Math.max(distance, MIN_APPROACH_SPEED);
      }

      speedUpdate = drone._acceleration * delta_time / 1000;
      if (speed > this._targetSpeed) {
        speedUpdate *= -1;
      }

      if (speed !== this._targetSpeed) {
        speedDiff = this._targetSpeed - speed;
        if (Math.abs(speedDiff) < Math.abs(speedUpdate)) {
          drone._speed = this._targetSpeed;
        } else {
          drone._speed += speedUpdate;
        }
      }
    };

  MulticopterDroneAPI.prototype._updatePosition =
    function (drone, yaw, delta_time) {
      var positionUpdate = drone.get3DSpeed() * delta_time / 1000,
        yawToDirection = this._toRad(-yaw + 90),
        xDiff = drone._targetCoordinates.x - drone.position.x,
        yDiff = drone._targetCoordinates.y - drone.position.y,
        zDiff = drone._targetCoordinates.z - drone.position.z,
        distanceToTarget = Math.sqrt(
          Math.pow(xDiff, 2) + Math.pow(yDiff, 2) + Math.pow(zDiff, 2)
        ),
        zNorm = zDiff / distanceToTarget,
        xyCoef = Math.sqrt(1 - Math.abs(zNorm));

      drone.setDirection(
        xyCoef * Math.cos(yawToDirection),
        xyCoef * Math.sin(yawToDirection),
        zNorm
      );

      drone._controlMesh.position.addInPlace(new BABYLON.Vector3(
        drone._direction.x * positionUpdate,
        drone._direction.y * positionUpdate,
        drone._direction.z * positionUpdate
      ));
    };

  MulticopterDroneAPI.prototype._getNewYaw =
    function (drone, bearing, delta_time) {
      // swap y and z axis so z axis represents altitude
      var yaw = drone.getYaw(),
        yawDiff = this._computeYawDiff(yaw, bearing),
        yawUpdate = this.getYawVelocity(drone) * delta_time / 1000;

      if (yawUpdate >= Math.abs(yawDiff)) {
        yawUpdate = yawDiff;
      } else if (yawDiff < 0) {
        yawUpdate *= -1;
      }
      return yaw + yawUpdate;
    };

  MulticopterDroneAPI.prototype._setSpeedInternal = function (speed) {
    this._targetSpeed = speed;
  };

  MulticopterDroneAPI.prototype.setSpeed = function (drone, speed) {
    this._requestedSpeed = Math.max(
      Math.min(speed, this.getMaxSpeed()),
      this.getMinSpeed()
    );
    this._setSpeedInternal(this._requestedSpeed * SPEED_FACTOR);

    drone._acceleration = (this._targetSpeed > drone.get3DSpeed())
      ? this.getMaxAcceleration() : this.getMaxDeceleration();
  };

  MulticopterDroneAPI.prototype.setStartingPosition =
    function (drone, x, y, z) {
      if (!drone._canPlay) {
        if (z <= 0.05) {
          z = 0.05;
        }
        drone._controlMesh.position = new BABYLON.Vector3(x, z, y);
      }
      drone._controlMesh.computeWorldMatrix(true);
      drone._mesh.computeWorldMatrix(true);
    };

  MulticopterDroneAPI.prototype.internal_getMsg = function (msg, id) {
    this._drone_dict_list[id] = msg;
  };

  MulticopterDroneAPI.prototype.internal_setTargetCoordinates =
    function (drone, coordinates, speed, radius) {
      this.setSpeed(drone, speed);
    };

  MulticopterDroneAPI.prototype.sendMsg = function (msg, to) {
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
  MulticopterDroneAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  MulticopterDroneAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "map"].includes(name)) {
      return this._gameManager.gameParameter[name];
    }
  };
  /*
  ** Converts geo latitude-longitud coordinates (º) to x,y plane coordinates (m)
  */
  MulticopterDroneAPI.prototype.processCoordinates = function (lat, lon, z) {
    if (isNaN(lat) || isNaN(lon) || isNaN(z)) {
      throw new Error('Target coordinates must be numbers');
    }
    var processed_coordinates =
      this._mapManager.convertToLocalCoordinates(lat, lon, z);
    return processed_coordinates;
  };
  MulticopterDroneAPI.prototype.getCurrentPosition = function (x, y, z) {
    return this._mapManager.convertToGeoCoordinates(x, y, z);
  };
  MulticopterDroneAPI.prototype.getDroneAI = function () {
    return null;
  };
  MulticopterDroneAPI.prototype.getMinSpeed = function () {
    return MIN_SPEED;
  };
  MulticopterDroneAPI.prototype.getMaxSpeed = function () {
    return this._flight_parameters.drone.maxSpeed;
  };
  MulticopterDroneAPI.prototype.getInitialSpeed = function () {
    return 0;
  };
  MulticopterDroneAPI.prototype.getMaxDeceleration = function () {
    return this._flight_parameters.drone.maxDeceleration;
  };
  MulticopterDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration;
  };
  MulticopterDroneAPI.prototype.getMaxRollAngle = function () {
    return this._flight_parameters.drone.maxRoll;
  };
  MulticopterDroneAPI.prototype.getMaxSinkRate = function () {
    return this._flight_parameters.drone.maxSpeed;
  };
  MulticopterDroneAPI.prototype.getMaxClimbRate = function () {
    return this._flight_parameters.drone.maxSpeed;
  };
  MulticopterDroneAPI.prototype.getMaxCommandFrequency = function () {
    return this._flight_parameters.drone.maxCommandFrequency;
  };
  MulticopterDroneAPI.prototype.getYawVelocity = function (drone) {
    return this.getMaxRollAngle();
  };
  MulticopterDroneAPI.prototype.getYaw = function (drone) {
    var direction = drone.worldDirection;
    return this._toDeg(Math.atan2(direction.x, direction.z));
  };
  MulticopterDroneAPI.prototype._computeBearing =
      function (lat1, lon1, lat2, lon2) {
      var dLon = this._toRad(lon2 - lon1),
        lat1Rad = this._toRad(lat1),
        lat2Rad = this._toRad(lat2),
        x = Math.cos(lat2Rad) * Math.sin(dLon),
        y = Math.cos(lat1Rad) * Math.sin(lat2Rad)
          - Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
      return this._toDeg(Math.atan2(x, y));
    };

  MulticopterDroneAPI.prototype._computeYawDiff = function (yaw1, yaw2) {
    var diff = yaw2 - yaw1;
    diff += (diff > 180) ? -360 : (diff < -180) ? 360 : 0;
    return diff;
  };
  MulticopterDroneAPI.prototype._toRad = function (angle) {
    return angle * Math.PI / 180;
  };
  MulticopterDroneAPI.prototype._toDeg = function (angle) {
    return angle * 180 / Math.PI;
  };
  MulticopterDroneAPI.prototype.getClimbRate = function (drone) {
    return drone.worldDirection.y * drone.get3DSpeed();
  };
  MulticopterDroneAPI.prototype.getSpeed = function (drone) {
    var direction = drone.worldDirection;
    return Math.sqrt(
      Math.pow(direction.x * drone.get3DSpeed(), 2)
        + Math.pow(direction.z * drone.get3DSpeed(), 2)
    );
  };
  MulticopterDroneAPI.prototype.takeOff = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    drone._internal_setTargetCoordinates(
      drone_pos.latitude,
      drone_pos.longitude,
      DEFAULT_TAKEOFF_ALTITUDE,
      DEFAULT_SPEED
    );
    drone._acceleration = this.getMaxAcceleration() / TAKE_OFF_FACTOR;
  };
  MulticopterDroneAPI.prototype.land = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    drone._internal_setTargetCoordinates(
      drone_pos.latitude,
      drone_pos.longitude,
      0,
      DEFAULT_SPEED
    );
    this._is_ready_to_fly = false;
    this._is_landing = true;
  };
  MulticopterDroneAPI.prototype.isReadyToFly = function () {
    return this._is_ready_to_fly;
  };
  MulticopterDroneAPI.prototype.isLanding = function () {
    return this._is_landing;
  };
  MulticopterDroneAPI.prototype.getInitialAltitude = function () {
    return this._map_dict.start_AMSL;
  };
  MulticopterDroneAPI.prototype.getAltitudeAbs = function (altitude) {
    return altitude + this._map_dict.start_AMSL;
  };
  MulticopterDroneAPI.prototype.getMinHeight = function () {
    return 0;
  };
  MulticopterDroneAPI.prototype.getMaxHeight = function () {
    return 800;
  };
  MulticopterDroneAPI.prototype.getOnUpdateInterval = function () {
    return this._flight_parameters.drone.onUpdateInterval;
  };
  MulticopterDroneAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return MulticopterDroneAPI;
}());
