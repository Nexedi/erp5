/*global console*/
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
    MAX_ACCELERATION = 1,
    MIN_SPEED = 12,
    MAX_SPEED = 26,
    MAX_ROLL = 35;

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
  FixedWingDroneAPI.prototype.internal_start = function () {
    return;
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  FixedWingDroneAPI.prototype.internal_update = function (drone) {
    if (this._loiter_mode) {
      this.loiter(drone);
    }
    /*if (this._start_altitude > 0) { //TODO move start_altitude here
      this.reachAltitude(drone);
    }*/
    var _this = this, drone_position = drone.getCurrentPosition(), drone_info;
    if (drone_position) {
      drone_info = {
        'altitudeRel' : drone_position.z,
        'altitudeAbs' : this._mapManager.getMapInfo().start_AMSL +
          drone_position.z,
        'latitude' : drone_position.x,
        'longitude' : drone_position.y
      };
      this._drone_dict_list[this._id] = drone_info;
      //broadcast drone info using internal msg
      this._gameManager._droneList.forEach(function (drone) {
        if (drone.id !== _this._id) {
          drone.internal_getMsg(drone_info, _this._id);
        }
      });
    }
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
          Math.cos(angle * (Math.PI / 180)) + this._loiter_center.x;
        y1 = this._loiter_radius *
          Math.sin(angle * (Math.PI / 180)) + this._loiter_center.y;
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
        drone._maxSpeed = this.getMaxSpeed();
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
  /*FixedWingDroneAPI.prototype.reachAltitude = function (drone) {
    function distance(p1, p2) {
      return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                       Math.pow(p1[1] - p2[1], 2));
    }
    //stop
    if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
      this._last_altitude_point_reached = -1;
      this.takeoff_path = [];
      this._start_altitude = 0;
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
    this.internal_setVirtualPlaneTargetCoordinates(
      next_point.x, next_point.y, next_point.z);
    if (distance([drone_pos.x, drone_pos.y],
      [next_point.x, next_point.y]) < 1) {
      this._last_altitude_point_reached += 1;
      if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
        return;
      }
      next_point = this.takeoff_path[this._last_altitude_point_reached + 1];
      this.internal_setVirtualPlaneTargetCoordinates(
        next_point.x, next_point.y, next_point.z);
    }
  };*/
  FixedWingDroneAPI.prototype.getMinSpeed = function () {
    return this._flight_parameters.drone.minSpeed || MIN_SPEED;
  };
  FixedWingDroneAPI.prototype.getMaxSpeed = function () {
    return this._flight_parameters.drone.maxSpeed || MAX_SPEED;
  };
  FixedWingDroneAPI.prototype.getInitialSpeed = function () {
    return this._flight_parameters.drone.speed || DEFAULT_SPEED;
  };
  FixedWingDroneAPI.prototype.getMinAcceleration = function () {
    return this._flight_parameters.drone.minAcceleration;
  };
  FixedWingDroneAPI.prototype.getMaxAcceleration = function () {
    return this._flight_parameters.drone.maxAcceleration || MAX_ACCELERATION;
  };
  FixedWingDroneAPI.prototype.getMinPitchAngle = function () {
    return this._flight_parameters.drone.minPitchAngle;
  };
  FixedWingDroneAPI.prototype.getMaxPitchAngle = function () {
    return this._flight_parameters.drone.maxPitchAngle;
  };
  FixedWingDroneAPI.prototype.getMaxRollAngle = function () {
    return this._flight_parameters.drone.maxRoll || MAX_ROLL;
  };
  FixedWingDroneAPI.prototype.getMinVerticalSpeed = function () {
    return this._flight_parameters.drone.minVerticalSpeed;
  };
  FixedWingDroneAPI.prototype.getMaxVerticalSpeed = function () {
    return this._flight_parameters.drone.maxVerticalSpeed;
  };
  FixedWingDroneAPI.prototype.getMaxOrientation = function () {
    //TODO should be a game parameter (but how to force value to PI quarters?)
    return Math.PI / 4;
  };
  FixedWingDroneAPI.prototype.getYawVelocity = function (drone) {
    return 360 * EARTH_GRAVITY
      * Math.tan(this.getMaxRollAngle() * Math.PI / 180)
      / (2 * Math.PI * drone.getSpeed());
  };
  FixedWingDroneAPI.prototype.getSinkRate = function () {
    //TODO
    return 0;
  };
  FixedWingDroneAPI.prototype.getClimbRate = function () {
    //TODO
    return 0;
  };
  FixedWingDroneAPI.prototype.triggerParachute = function (drone) {
    var drone_pos = drone.getCurrentPosition();
    this.internal_setTargetCoordinates(drone, drone_pos, true);
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
