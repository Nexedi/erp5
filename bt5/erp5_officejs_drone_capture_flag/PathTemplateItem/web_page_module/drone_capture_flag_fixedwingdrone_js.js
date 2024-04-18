/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true */

/************************** FIXED WING DRONE API ****************************/
var FixedWingDroneAPI = /** @class */ (function () {
  "use strict";

  var DEFAULT_SPEED = 16,
    PARACHUTE_SPEED = 8,
    EARTH_GRAVITY = 9.81,
    LOITER_LIMIT = 30,
    MAX_ACCELERATION = 6,
    MAX_DECELERATION = 1,
    MIN_SPEED = 12,
    MAX_SPEED = 26,
    MAX_ROLL = 35,
    MIN_PITCH = -20,
    MAX_PITCH = 25,
    MAX_CLIMB_RATE = 8,
    MAX_SINK_RATE = 3,
    VIEW_SCOPE = 100,
    MAX_MESSAGE_SIZE = 1024;

  //** CONSTRUCTOR
  function FixedWingDroneAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._map_dict = this._mapManager.getMapInfo();
    this._flight_parameters = flight_parameters;
    this._id = id;
    this._drone_info = drone_info;
    this._loiter_radius = 100;
    //this._start_altitude = 0;
    this._loiter_mode = false;
    this._is_landing = false;
    this._is_ready_to_fly = true;
    this._drone_dict_list = [];
  }
  /*
  ** Function called on start phase of the drone, just before onStart AI script
  */
  FixedWingDroneAPI.prototype.internal_start = function (drone) {
    drone._maxDeceleration = this.getMaxDeceleration();
    if (drone._maxDeceleration <= 0) {
      throw new Error('max deceleration must be superior to 0');
    }
    drone._maxAcceleration = this.getMaxAcceleration();
    if (drone._maxAcceleration <= 0) {
      throw new Error('max acceleration must be superior to 0');
    }
    drone._minSpeed = this.getMinSpeed();
    if (drone._minSpeed < 0) {
      throw new Error('min speed must be superior to 0');
    }
    drone._maxSpeed = this.getMaxSpeed();
    if (drone._minSpeed > drone._maxSpeed) {
      throw new Error('min speed cannot be superior to max speed');
    }
    drone._speed = drone._targetSpeed = this.getInitialSpeed();
    if (drone._speed < drone._minSpeed || drone._speed > drone._maxSpeed) {
      throw new Error('Drone speed must be between min speed and max speed');
    }
    drone._minPitchAngle = this.getMinPitchAngle();
    if (drone._minPitchAngle >= 0) {
      throw new Error('min pitch angle must be inferior to 0');
    }
    drone._maxPitchAngle = this.getMaxPitchAngle();
    if (drone._maxPitchAngle <= 0) {
      throw new Error('max pitch angle must be superior to 0');
    }
    if (drone._minPitchAngle > drone._maxPitchAngle) {
      throw new Error('min pitch angle cannot be superior to max pitch angle');
    }
    drone._maxRollAngle = this.getMaxRollAngle();
    if (drone._maxRollAngle <= 0) {
      throw new Error('max roll angle must be superior to 0');
    }
    drone._maxSinkRate = this.getMaxSinkRate();
    if (drone._maxSinkRate <= 0) {
      throw new Error('max sink rate must be superior to 0');
    }
    if (drone._maxSinkRate > drone._maxSpeed) {
      throw new Error('max sink rate cannot be superior to max speed');
    }
    drone._maxClimbRate = this.getMaxClimbRate();
    if (drone._maxClimbRate <= 0) {
      throw new Error('max climb rate must be superior to 0');
    }
    if (drone._maxClimbRate > drone._maxSpeed) {
      throw new Error('max climb rate cannot be superior to max speed');
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
  FixedWingDroneAPI.prototype.internal_position_update = function (context, delta_time) {
    if (context.position.z > 0) {
      this._updateSpeed(context, delta_time);
      this._updatePosition(context, delta_time);
    } else {
      context.setDirection(0, 0, 0);
    }

    context._controlMesh.computeWorldMatrix(true);
    context._mesh.computeWorldMatrix(true);
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  FixedWingDroneAPI.prototype.internal_info_update = function (drone) {
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

  FixedWingDroneAPI.prototype._updateSpeed = function (drone, delta_time) {
    var speed = drone.get3DSpeed(), speedDiff, speedUpdate;
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

  FixedWingDroneAPI.prototype._updatePosition = function (drone, delta_time) {
    var R = 6371e3,
      currentGeoCoordinates = this._mapManager.convertToGeoCoordinates(
        drone.position.x,
        drone.position.y,
        drone.position.z
      ),
      targetCoordinates = this._mapManager.convertToGeoCoordinates(
        drone._targetCoordinates.x,
        drone._targetCoordinates.y,
        drone._targetCoordinates.z
      ),
      bearing = this._computeBearing(
        currentGeoCoordinates.latitude,
        currentGeoCoordinates.longitude,
        targetCoordinates.latitude,
        targetCoordinates.longitude
      ),
      currentCosLat,
      currentLatRad,
      distance,
      distanceCos,
      distanceSin,
      distanceToTarget,
      currentSinLat,
      currentLonRad,
      groundSpeed,
      newCoordinates,
      newLatRad,
      newLonRad,
      newYaw,
      newYawRad,
      verticalSpeed,
      yawToDirection;

    if (this._loiter_mode) {
      distanceToTarget = Math.sqrt(
        Math.pow(drone._targetCoordinates.x - drone.position.x, 2)
          + Math.pow(drone._targetCoordinates.y - drone.position.y, 2)
      );

      if (Math.abs(distanceToTarget - this._loiter_radius) <= 1) {
        newYaw = bearing - 90;
      } else if (distanceToTarget < this._loiter_radius) {
        newYaw = bearing - 135;
      } else {
        newYaw = this._getNewYaw(drone, bearing, delta_time);
      }
    } else {
      newYaw = this._getNewYaw(drone, bearing, delta_time);
    }
    newYawRad = this._toRad(newYaw);

    currentLatRad = this._toRad(currentGeoCoordinates.latitude);
    currentCosLat = Math.cos(currentLatRad);
    currentSinLat = Math.sin(currentLatRad);
    currentLonRad = this._toRad(currentGeoCoordinates.longitude);

    verticalSpeed = this._getVerticalSpeed(drone);
    groundSpeed = Math.sqrt(
      Math.pow(drone.get3DSpeed(), 2) - Math.pow(verticalSpeed, 2)
    );

    distance = (groundSpeed * delta_time / 1000) / R;
    distanceCos = Math.cos(distance);
    distanceSin = Math.sin(distance);

    newLatRad = Math.asin(
      currentSinLat * distanceCos +
        currentCosLat * distanceSin * Math.cos(newYawRad)
    );
    newLonRad = currentLonRad + Math.atan2(
      Math.sin(newYawRad) * distanceSin * currentCosLat,
      distanceCos - currentSinLat * Math.sin(newLatRad)
    );

    newCoordinates = this._mapManager.convertToLocalCoordinates(
      this._toDeg(newLatRad),
      this._toDeg(newLonRad),
      drone.position.z
    );

    // swap y and z axis so z axis represents altitude
    drone._controlMesh.position.addInPlace(new BABYLON.Vector3(
      Math.abs(newCoordinates.x - drone.position.x) *
        (newCoordinates.x < drone.position.x ? -1 : 1),
      verticalSpeed * delta_time / 1000,
      Math.abs(newCoordinates.y - drone.position.y) *
        (newCoordinates.y < drone.position.y ? -1 : 1)
    ));
    yawToDirection = this._toRad(-newYaw + 90);
    drone.setDirection(
      groundSpeed * Math.cos(yawToDirection),
      groundSpeed * Math.sin(yawToDirection),
      verticalSpeed
    );
  };

  FixedWingDroneAPI.prototype._getNewYaw =
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

  FixedWingDroneAPI.prototype._getVerticalSpeed = function (drone) {
    // swap y and z axis so z axis represents altitude
    var altitudeDiff = drone._targetCoordinates.z - drone.position.z,
      verticalSpeed;

    if (altitudeDiff >= 0) {
      verticalSpeed = this._computeVerticalSpeed(
        altitudeDiff,
        this.getMaxClimbRate(),
        drone.get3DSpeed(),
        this.getMaxPitchAngle()
      );
    } else {
      verticalSpeed = -this._computeVerticalSpeed(
        Math.abs(altitudeDiff),
        this.getMaxSinkRate(),
        drone.get3DSpeed(),
        -this.getMinPitchAngle()
      );
    }
    return verticalSpeed;
  };

  FixedWingDroneAPI.prototype.setSpeed = function (drone, speed) {
    this._targetSpeed = Math.max(
      Math.min(speed, this.getMaxSpeed()),
      this.getMinSpeed()
    );

    drone._acceleration = (this._targetSpeed > drone.get3DSpeed()) ?
        this.getMaxAcceleration() : -this.getMaxDeceleration();
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

  FixedWingDroneAPI.prototype.internal_setTargetCoordinates =
    function (drone, coordinates, speed, radius) {
      if (radius) {
        this._loiter_mode = true;
        if (radius >= LOITER_LIMIT) {
          this._loiter_radius = radius;
        }
      } else {
        this._loiter_mode = false;
      }
      this.setSpeed(drone, speed);
    };

  FixedWingDroneAPI.prototype.sendMsg = function (msg, to) {
    if (JSON.stringify(msg).length > MAX_MESSAGE_SIZE) {
      //TODO what to do? truncate the msg? log a warning? crash the drone?
      msg = {"error": "message too long (max 1024)"};
    }
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
              console.warn('Drone crashed on onGetMsg due to error:', error);
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
            console.warn('Drone crashed on onGetMsg due to error:', error);
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
    var processed_coordinates =
      this._mapManager.convertToLocalCoordinates(lat, lon, z);
    if (processed_coordinates.z > this._map_dict.start_AMSL) {
      processed_coordinates.z -= this._map_dict.start_AMSL;
    }
    return processed_coordinates;
  };

  FixedWingDroneAPI.prototype.getCurrentPosition = function (x, y, z) {
    return this._mapManager.convertToGeoCoordinates(x, y, z);
  };
  FixedWingDroneAPI.prototype.getDroneViewInfo = function (drone) {
    var context = this, result = { "obstacles": [], "drones": [] }, distance,
      other_position, drone_position = drone.getCurrentPosition();
    function calculateDistance(a, b, _this) {
      return _this._mapManager.latLonDistance([a.latitude, a.longitude],
                                              [b.latitude, b.longitude]);
    }
    context._gameManager._droneList.forEach(function (other) {
      if (other.can_play && drone.id !== other.id) {
        other_position = other.getCurrentPosition();
        distance = calculateDistance(drone_position, other_position, context);
        if (distance <= VIEW_SCOPE) {
          result.drones.push({
            position: other.getCurrentPosition(),
            direction: other.direction,
            rotation: other.rotation,
            speed: other.speed,
            team: other.team
          });
        }
      }
    });
    context._map_dict.obstacle_list.forEach(function (obstacle) {
      distance = calculateDistance(drone_position, obstacle.position, context);
      if (distance <= VIEW_SCOPE) {
        result.obstacles.push(obstacle);
      }
    });
    if (drone.__is_getting_drone_view !== true) {
      drone.__is_getting_drone_view = true;
      context._gameManager.delay(function () {
        drone.__is_getting_drone_view = false;
        try {
          drone.onDroneViewInfo(result);
        } catch (error) {
          console.warn('Drone crashed on drone view due to error:', error);
          drone._internal_crash();
        }
      }, 1000);
    }
  };
  FixedWingDroneAPI.prototype.getDroneAI = function () {
    return null;
  };
  FixedWingDroneAPI.prototype.getMinSpeed = function () {
    return this._flight_parameters.drone.minSpeed;
  };
  FixedWingDroneAPI.prototype.getMaxSpeed = function () {
    return this._flight_parameters.drone.maxSpeed;
  };
  FixedWingDroneAPI.prototype.getInitialSpeed = function () {
    return this._flight_parameters.drone.speed;
  };
  FixedWingDroneAPI.prototype.getMaxDeceleration = function () {
    return this._flight_parameters.drone.maxDeceleration;
  };
  FixedWingDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration;
  };
  FixedWingDroneAPI.prototype.getMinPitchAngle = function () {
    return this._flight_parameters.drone.minPitchAngle;
  };
  FixedWingDroneAPI.prototype.getMaxPitchAngle = function () {
    return this._flight_parameters.drone.maxPitchAngle;
  };
  FixedWingDroneAPI.prototype.getMaxRollAngle = function () {
    return this._flight_parameters.drone.maxRoll;
  };
  FixedWingDroneAPI.prototype.getMaxSinkRate = function () {
    return this._flight_parameters.drone.maxSinkRate;
  };
  FixedWingDroneAPI.prototype.getMaxClimbRate = function () {
    return this._flight_parameters.drone.maxClimbRate;
  };
  FixedWingDroneAPI.prototype.getMaxCommandFrequency = function () {
    return this._flight_parameters.drone.maxCommandFrequency;
  };
  FixedWingDroneAPI.prototype.getYawVelocity = function (drone) {
    return 360 * EARTH_GRAVITY *
      Math.tan(this._toRad(this.getMaxRollAngle())) /
      (2 * Math.PI * drone.get3DSpeed());
  };
  FixedWingDroneAPI.prototype.getYaw = function (drone) {
    var direction = drone.worldDirection;
    return this._toDeg(Math.atan2(direction.x, direction.z));
  };
  FixedWingDroneAPI.prototype._computeBearing =
    function (lat1, lon1, lat2, lon2) {
      var dLon = this._toRad(lon2 - lon1),
        lat1Rad = this._toRad(lat1),
        lat2Rad = this._toRad(lat2),
        x = Math.cos(lat2Rad) * Math.sin(dLon),
        y = Math.cos(lat1Rad) * Math.sin(lat2Rad) -
          Math.sin(lat1Rad) * Math.cos(lat2Rad) * Math.cos(dLon);
      return this._toDeg(Math.atan2(x, y));
    };
  FixedWingDroneAPI.prototype._computeYawDiff = function (yaw1, yaw2) {
    var diff = yaw2 - yaw1;
    diff += (diff > 180) ? -360 : (diff < -180) ? 360 : 0;
    return diff;
  };
  FixedWingDroneAPI.prototype._computeVerticalSpeed =
    function (altitude_diff, max_climb_rate, speed, max_pitch) {
      var maxVerticalSpeed =
          Math.min(altitude_diff, Math.min(max_climb_rate, speed));
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
    return drone.worldDirection.y * drone.get3DSpeed();
  };
  FixedWingDroneAPI.prototype.getSpeed = function (drone) {
    var direction = drone.worldDirection;
    return Math.sqrt(
      Math.pow(direction.x * drone.get3DSpeed(), 2) +
        Math.pow(direction.z * drone.get3DSpeed(), 2)
    );
  };
  FixedWingDroneAPI.prototype.takeOff = function () {
    return console.log("Fixed-wing drones can only be taken off manually.");
  };
  FixedWingDroneAPI.prototype.land = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    this._flight_parameters.drone.minSpeed = 0;
    drone._speed = 0;
    drone._acceleration = EARTH_GRAVITY;
    this._flight_parameters.drone.maxSinkRate = PARACHUTE_SPEED;
    this._flight_parameters.drone.minPitchAngle = -90;
    drone._internal_setTargetCoordinates(
      drone_pos.latitude,
      drone_pos.longitude,
      -PARACHUTE_SPEED,
      PARACHUTE_SPEED
    );
    this._is_ready_to_fly = false;
    this._is_landing = true;
  };
  FixedWingDroneAPI.prototype.isReadyToFly = function () {
    return this._is_ready_to_fly;
  };
  FixedWingDroneAPI.prototype.isLanding = function () {
    return this._is_landing;
  };
  FixedWingDroneAPI.prototype.getInitialAltitude = function () {
    return this._map_dict.start_AMSL;
  };
  FixedWingDroneAPI.prototype.getAltitudeAbs = function (altitude) {
    return altitude + this._map_dict.start_AMSL;
  };
  FixedWingDroneAPI.prototype.getMinHeight = function () {
    return 0;
  };
  FixedWingDroneAPI.prototype.getMaxHeight = function () {
    return 800;
  };
  FixedWingDroneAPI.prototype.getOnUpdateInterval = function () {
    return this._flight_parameters.drone.onUpdateInterval;
  };
  FixedWingDroneAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return FixedWingDroneAPI;
}());
