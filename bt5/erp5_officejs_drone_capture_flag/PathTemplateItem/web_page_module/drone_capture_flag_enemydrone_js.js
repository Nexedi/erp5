/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true */

/************************** ENEMY DRONE API ****************************/
var EnemyDroneAPI = /** @class */ (function () {
  "use strict";

  var DEFAULT_ACCELERATION = 1,
    VIEW_SCOPE = 25,
    DEFAULT_SPEED = 16.5,
    MIN_SPEED = 12,
    MAX_SPEED = 26,
    COLLISION_SECTOR = 10;

  //** CONSTRUCTOR
  function EnemyDroneAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._map_dict = this._mapManager.getMapInfo();
    this._flight_parameters = flight_parameters;
    this._id = id;
    this._drone_info = drone_info;
    this._drone_dict_list = [];
    this._acceleration = DEFAULT_ACCELERATION;
    this._collision_sector = COLLISION_SECTOR;
    this._is_landing = false;
    this._is_ready_to_fly = true;
  }
  /*
  ** Function called on start phase of the drone, just before onStart AI script
  */
  EnemyDroneAPI.prototype.internal_start = function (drone) {
    //TODO check, _targetCoordinates is not used. obsolete?
    drone._targetCoordinates = drone.getCurrentPosition();
    drone._maxAcceleration = this.getMaxAcceleration();
    if (drone._maxAcceleration <= 0) {
      throw new Error('max acceleration must be superior to 0');
    }
    drone._minSpeed = this.getMinSpeed();
    if (drone._minSpeed <= 0) {
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
    if (drone._maxSinkRate > drone._maxSpeed) {
      throw new Error('max sink rate cannot be superior to max speed');
    }
    return;
  };
  /*
  ** Function called on every drone update, right before onUpdate AI script
  */
  EnemyDroneAPI.prototype.internal_position_update = function (context, delta_time) {
    context._speed += context._acceleration * delta_time / 1000;
    if (context._speed > context._maxSpeed) {
      context._speed = context._maxSpeed;
    }
    if (context._speed < -context._maxSpeed) {
      context._speed = -context._maxSpeed;
    }
    var updateSpeed = context._speed * delta_time / 1000;
    if (context._direction.x !== 0 ||
        context._direction.y !== 0 ||
        context._direction.z !== 0) {
      context._controlMesh.position.addInPlace(
        new BABYLON.Vector3(context._direction.x * updateSpeed,
                            context._direction.y * updateSpeed,
                            context._direction.z * updateSpeed)
      );
    }
    context._controlMesh.computeWorldMatrix(true);
    context._mesh.computeWorldMatrix(true);
    return;
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  EnemyDroneAPI.prototype.internal_info_update = function (drone) {
    var _this = this, drone_position = drone.getCurrentPosition(), drone_info;
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

  EnemyDroneAPI.prototype.setStartingPosition = function (drone, x, y, z) {
    if (!drone._canPlay) {
      if (z <= 0.05) {
        z = 0.05;
      }
      drone._controlMesh.position = new BABYLON.Vector3(x, z, y);
    }
    drone._controlMesh.computeWorldMatrix(true);
    drone._mesh.computeWorldMatrix(true);
  };

  EnemyDroneAPI.prototype.internal_getMsg = function (msg, id) {
    this._drone_dict_list[id] = msg;
  };

  EnemyDroneAPI.prototype.internal_setTargetCoordinates =
    function (drone, coordinates) {
      if (!drone._canPlay) {
        return;
      }
      var x = coordinates.x, y = coordinates.y, z = coordinates.z;
      if (isNaN(x) || isNaN(y) || isNaN(z)) {
        throw new Error('Target coordinates must be numbers');
      }
      x -= drone._controlMesh.position.x;
      y -= drone._controlMesh.position.z;
      z -= drone._controlMesh.position.y;
      drone.setDirection(x, y, z);
    };
  EnemyDroneAPI.prototype.sendMsg = function (msg, to) {
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
  EnemyDroneAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  EnemyDroneAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "map"].includes(name)) {
      return this._gameManager.gameParameter[name];
    }
  };
  /*
  ** Enemy drone works with cartesian, no geo conversion
  */
  EnemyDroneAPI.prototype.processCoordinates = function (x, y, z) {
    if (isNaN(x) || isNaN(y) || isNaN(z)) {
      throw new Error('Target coordinates must be numbers');
    }
    if (z > this._map_dict.start_AMSL) {
      z -= this._map_dict.start_AMSL;
    }
    return {
      'x': x,
      'y': y,
      'z': z
    };
  };
  EnemyDroneAPI.prototype.getCurrentPosition = function (x, y, z) {
    return this._mapManager.convertToGeoCoordinates(x, y, z);
  };
  EnemyDroneAPI.prototype.getDroneViewInfo = function (drone) {
    var context = this, result = [], distance,
      drone_position = drone.position, other_position;
    function calculateDistance(a, b, _3D) {
      var z = (_3D ?  Math.pow((a.z - b.z), 2) : 0);
      return Math.sqrt(Math.pow((a.x - b.x), 2) + Math.pow((a.y - b.y), 2) + z);
    }
    context._gameManager._droneList_user.forEach(function (other) {
      if (other.can_play) {
        other_position = other.position;
        distance = calculateDistance(drone_position, other_position);
        //the higher the drone, the easier to detect
        if (distance / (other_position.z * 0.05) <= VIEW_SCOPE) {
          result.push({
            position: other_position,
            direction: other.direction,
            rotation: other.rotation,
            speed: other.speed,
            target: other._targetCoordinates, //check
            team: other.team
          });
        }
      }
    });
    return result;
  };
  EnemyDroneAPI.prototype.getDroneAI = function () {
    //interception math based on https://www.codeproject.com/Articles/990452/Interception-of-Two-Moving-Objects-in-D-Space
    return 'function calculateInterception(hunter_position, prey_position, hunter_speed, prey_speed, prey_velocity_vector) {\n' +
      '  var vector_from_drone, distance_to_prey, distance_to_prey_vector, a, b, c, t1, t2, interception_time, interception_point;\n' +
      '  function dot(a, b) {\n' +
      '    return a.map((x, i) => a[i] * b[i]).reduce((m, n) => m + n);\n' +
      '  }\n' +
      '  distance_to_prey_vector = [hunter_position.x - prey_position.x, hunter_position.y - prey_position.y, hunter_position.z - prey_position.z];\n' +
      '  distance_to_prey = distance(hunter_position, prey_position);\n' +
      '  a = hunter_speed * hunter_speed - prey_speed * prey_speed;\n' +
      '  b = 2 * dot(distance_to_prey_vector, prey_velocity_vector);\n' +
      '  c = - distance_to_prey * distance_to_prey;\n' +
      '  t1 = (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a);\n' +
      '  t2 = (-b - Math.sqrt(b * b - 4 * a * c)) / (2 * a);\n' +
      '  if (t1 > 0 && t2 > 0) {\n' +
      '    interception_time = Math.min( t1, t2 );\n' +
      '  } else {\n' +
      '    interception_time = Math.max( t1, t2 );\n' +
      '  }\n' +
      '  interception_point = [prey_position.x + prey_velocity_vector[0] * interception_time, prey_position.y + prey_velocity_vector[1] * interception_time, prey_position.z + prey_velocity_vector[2] * interception_time];\n' +
      '  if (isNaN(interception_point[0]) || isNaN(interception_point[1]) || isNaN(interception_point[2])) {\n' +
      '    return;\n' +
      '  }\n' +
      '  return interception_point;\n' +
      '}\n' +
      'function distance(a, b) {\n' +
      '  return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2);\n' +
      '}\n' +
      '\n' +
      'me.onStart = function (timestamp) {\n' +
      '  me.setDirection(0,0,0);\n' +
      '  return;\n' +
      '\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
      '  me.current_position = me.position;\n' +
      '  var drone_position, drone_velocity_vector, interception_point, drone_view,\n' +
      '  drone_view = me.getDroneViewInfo();\n' +
      '  if (drone_view.length) {\n' +
      '    drone_position = drone_view[0].position;\n' +
      '    drone_velocity_vector = [drone_view[0].target.x - drone_position.x, drone_view[0].target.y - drone_position.y, drone_view[0].target.z - drone_position.z];\n' +
      '    interception_point = calculateInterception(me.current_position, drone_position, me.speed, drone_view[0].speed, drone_velocity_vector);\n' +
      '    if (!interception_point) {\n' +
      '      return;\n' +
      '    }\n' +
      '    me.setTargetCoordinates(interception_point[0], interception_point[1], interception_point[2]);\n' +
      '  }\n' +
      '};';
  };
  EnemyDroneAPI.prototype.getMinSpeed = function () {
    return MIN_SPEED;
    //return this._flight_parameters.drone.minSpeed;
  };
  EnemyDroneAPI.prototype.getMaxSpeed = function () {
    return MAX_SPEED;
    //return this._flight_parameters.drone.maxSpeed;
  };
  EnemyDroneAPI.prototype.getInitialSpeed = function () {
    return DEFAULT_SPEED;
    //return this._flight_parameters.drone.speed;
  };
  EnemyDroneAPI.prototype.getMaxDeceleration = function () {
    return this._flight_parameters.drone.maxDeceleration;
  };
  EnemyDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration;
  };
  EnemyDroneAPI.prototype.getMaxCommandFrequency = function () {
    return Infinity;
  };
  EnemyDroneAPI.prototype.land = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    drone.setTargetCoordinates(drone_pos.latitude, drone_pos.longitude, 0);
    this._is_ready_to_fly = false;
    this._is_landing = true;
  };
  EnemyDroneAPI.prototype.isReadyToFly = function () {
    return this._is_ready_to_fly;
  };
  EnemyDroneAPI.prototype.isLanding = function () {
    return this._is_landing;
  };
  EnemyDroneAPI.prototype.getInitialAltitude = function () {
    return 0;
  };
  EnemyDroneAPI.prototype.getAltitudeAbs = function (altitude) {
    return altitude;
  };
  EnemyDroneAPI.prototype.getMinHeight = function () {
    return 0;
  };
  EnemyDroneAPI.prototype.getMaxHeight = function () {
    return 800;
  };
  EnemyDroneAPI.prototype.getOnUpdateInterval = function () {
    return 0;
  };
  EnemyDroneAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  EnemyDroneAPI.prototype.getCollisionSector = function () {
    return this._collision_sector;
  };
  return EnemyDroneAPI;
}());
