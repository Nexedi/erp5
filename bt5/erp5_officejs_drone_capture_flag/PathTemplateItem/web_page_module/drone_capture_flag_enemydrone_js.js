/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, todo: true */

/************************** ENEMY DRONE API ****************************/
var EnemyDroneAPI = /** @class */ (function () {
  "use strict";

  var DEFAULT_ACCELERATION = 1,
    VIEW_SCOPE = 20;

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
  }
  /*
  ** Function called on start phase of the drone, just before onStart AI script
  */
  EnemyDroneAPI.prototype.internal_start = function (drone) {
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
    drone._maxOrientation = this.getMaxOrientation();
    return;
  };
  /*
  ** Function called on every drone update, right before onUpdate AI script
  */
  EnemyDroneAPI.prototype.internal_update = function (context, delta_time) {
    context._speed += context._acceleration * delta_time / 1000;
    if (context._speed > context._maxSpeed)
      context._speed = context._maxSpeed;
    if (context._speed < -context._maxSpeed)
      context._speed = -context._maxSpeed;
    var updateSpeed = context._speed * delta_time / 1000;
    if (context._direction.x !== 0 ||
        context._direction.y !== 0 ||
        context._direction.z !== 0) {
      context._controlMesh.position.addInPlace(
        new BABYLON.Vector3(context._direction.x * updateSpeed,
                            context._direction.y * updateSpeed,
                            context._direction.z * updateSpeed));
    }
    var orientationValue = context._maxOrientation *
        (context._speed / context._maxSpeed);
    context._mesh.rotation = new BABYLON.Vector3(
      orientationValue * context._direction.z, 0,
      -orientationValue * context._direction.x);
    context._controlMesh.computeWorldMatrix(true);
    context._mesh.computeWorldMatrix(true);
    return;
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  EnemyDroneAPI.prototype.internal_post_update = function (drone) {
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

  EnemyDroneAPI.prototype.setAltitude = function (drone, altitude) {
    drone._targetCoordinates.z = altitude;
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
      if (!drone._canPlay) return;
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
  ** Converts geo latitude-longitud coordinates (º) to x,y plane coordinates (m)
  */
  EnemyDroneAPI.prototype.processCoordinates = function (lat, lon, z) {
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
  EnemyDroneAPI.prototype.getCurrentPosition = function (x, y, z) {
    return this._mapManager.convertToGeoCoordinates(x, y, z, this._map_dict);
  };
  EnemyDroneAPI.prototype.getDroneViewInfo = function (drone) {
    var context = this, result = [], distance,
      drone_position = drone.getCurrentPosition(true), other_position;
    function calculateDistance(a, b) {
      return Math.sqrt(Math.pow((a.x - b.x), 2) + Math.pow((a.y - b.y), 2) +
                       Math.pow((a.z - b.z), 2));
    }
    context._gameManager._droneList_user.forEach(function (other) {
      if (other.can_play) {
        other_position = other.getCurrentPosition(true);
        distance = calculateDistance(drone_position, other_position);
        if (distance <= VIEW_SCOPE) {
          result.push({
            position: drone.position,
            direction: drone.direction,
            rotation: drone.rotation,
            speed: drone.speed,
            team: drone.team
          });
        }
      }
    });
    return result;
  };
  EnemyDroneAPI.prototype.getDroneAI = function () {
    return 'me.onStart = function () {\n' +
      '  me.setDirection(0,0,0);\n' +
      '};\n' +
      '\n' +
      'me.onUpdate = function (timestamp) {\n' +
      '  var drone_view = me.getDroneViewInfo();\n' +
      '  console.log("drone_view:", drone_view);\n' +
      '  if (drone_view.length) {\n' +
      '    me.setTargetCoordinates(\n' +
      '      0,\n' +
      '      0,\n' +
      '      10 + me.id, true\n' +
      '    );\n' +
      '  }\n' +
      '};';
  };
  EnemyDroneAPI.prototype.getMinSpeed = function () {
    return this._flight_parameters.drone.minSpeed;
  };
  EnemyDroneAPI.prototype.getMaxSpeed = function () {
    return this._flight_parameters.drone.maxSpeed;
  };
  EnemyDroneAPI.prototype.getInitialSpeed = function () {
    return this._flight_parameters.drone.speed;
  };
  EnemyDroneAPI.prototype.getMaxDeceleration = function () {
    return this._flight_parameters.drone.maxDeceleration;
  };
  EnemyDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration;
  };
  EnemyDroneAPI.prototype.getMaxOrientation = function () {
    //TODO should be a game parameter (but how to force value to PI quarters?)
    return Math.PI / 4;
  };
  EnemyDroneAPI.prototype.triggerParachute = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    drone.setTargetCoordinates(drone_pos.x, drone_pos.y, 5);
  };
  EnemyDroneAPI.prototype.landed = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    return Math.floor(drone_pos.z) < 10;
  };
  EnemyDroneAPI.prototype.exit = function () {
    return;
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
  EnemyDroneAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  return EnemyDroneAPI;
}());
