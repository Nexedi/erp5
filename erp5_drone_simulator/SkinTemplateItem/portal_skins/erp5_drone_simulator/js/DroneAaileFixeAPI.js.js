/// <reference path="./GameManager.ts" />

TAKEOFF_RADIUS = 60;
LOITER_LIMIT = 30;
LOITER_RADIUS_FACTOR = 0.60;
LOITER_SPEED_FACTOR = 1.5;

var DroneAaileFixeAPI = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneAaileFixeAPI(gameManager, team, flight_parameters) {
        this._gameManager = gameManager;
        this._team = team;
        this._flight_parameters = flight_parameters;
        this._loiter_radius = 0;
        this._last_loiter_point_reached = -1;
        this._last_altitude_point_reached = -1;
    }
    Object.defineProperty(DroneAaileFixeAPI.prototype, "team", {
        //*************************************************** ACCESSOR *****************************************************
        get: function () {
            if (this._team == "L")
                return this._gameManager.teamLeft;
            else if (this._team == "R")
                return this._gameManager.teamRight;
        },
        enumerable: true,
        configurable: true
    });
    //*************************************************** FUNCTIONS ****************************************************
    //#region ------------------ Internal
    DroneAaileFixeAPI.prototype.internal_sendMsg = function (msg, to) {
        var _this = this;
        _this._gameManager.delay(function () {
            if (to < 0) {
                // Send to all drones
                _this.team.forEach(function (drone) {
                    if (drone.infosMesh) {
                        try {
                          drone.onGetMsg(msg);
                        }
                        catch (error) {
                          console.warn('Drone crashed on sendMsg due to error:', error);
                          drone._internal_crash();
                        }
                    }
                });
            }
            else {
                // Send to specific drone
                if (drone.infosMesh) {
                    try {
                      _this.team[to].onGetMsg(msg);
                    }
                    catch (error) {
                      console.warn('Drone crashed on sendMsg due to error:', error);
                      _this.team[to]._internal_crash();
                    }
                }
            }
        }, GAMEPARAMETERS.latency.communication);
    };
    //#endregion
    //#region ------------------ Accessible from AI
    DroneAaileFixeAPI.prototype.log = function (msg) {
        console.log("API say : " + msg);
    };
    DroneAaileFixeAPI.prototype.getGameParameter = function (name) {
        if (["gameTime", "mapSize", "teamSize", "derive", "meteo", "initialHumanAreaPosition"].includes(name))
          return this._gameManager.gameParameter[name];
    };
    DroneAaileFixeAPI.prototype._isWithinDroneView = function (drone_position, element_position) {
        // Check if element is under the drone cone-view
        var angle = GAMEPARAMETERS.drone.viewAngle ? GAMEPARAMETERS.drone.viewAngle : 60,
          radius = drone_position.z * Math.tan(angle/2 * Math.PI/180),
          distance = (drone_position.x - element_position.x) * (drone_position.x - element_position.x) +
            (drone_position.y - element_position.y) * (drone_position.y - element_position.y);
        if (distance < (radius*radius))
          return true;
        return false;
    };
    DroneAaileFixeAPI.prototype._getProbabilityOfDetection = function (drone_position) {
        var h = drone_position.z,
          km = GAMEPARAMETERS.meteo;
          prob = 20 * (1 + (110-h)/25) * km;
        return prob;
    };
    DroneAaileFixeAPI.prototype.isHumanPositionSpottedCalculation = function (drone) {
      var context = this,
        result = false,
        drone_position = drone.infosMesh.position;
      //swap axes back
      drone_position = {
          x: drone_position.x,
          y: drone_position.z,
          z: drone_position.y
      };
      context._gameManager.teamRight.forEach(function (human) {
        if (human.infosMesh && context._isWithinDroneView(drone_position, human.position)) {
          var prob = context._getProbabilityOfDetection(drone_position),
            random = Math.floor(Math.random()*101);
          if (random < prob)
            result = true;
        }
      });
      return result;
    };
    DroneAaileFixeAPI.prototype.isHumanPositionSpotted = function (drone) {
      var context = this,
        human_detected;

      if (drone.__is_calculating_human_position !== true) {
        drone.__is_calculating_human_position = true;
        //human detection is done with the info captured by the drone
        //at the moment this method is called
        human_detected = context.isHumanPositionSpottedCalculation(drone);

        context._gameManager.delay(function () {
          drone.__is_calculating_human_position = false;
          try {
            drone.onCapture(human_detected);
          } catch (error) {
            console.warn('Drone crashed on capture due to error:', error);
            drone._internal_crash();
          }
        }, 2000);
      }
    };
    DroneAaileFixeAPI.prototype.processCoordinates = function (lat, lon, z, r) {
      if(isNaN(lat) || isNaN(lon) || isNaN(z)){
        throw new Error('Target coordinates must be numbers');
      }
      var flightParameters = this.getFlightParameters();
      function longitudToX(lon, flightParameters) {
        return (flightParameters.MAP_SIZE / 360.0) * (180 + lon);
      }
      function latitudeToY(lat, flightParameters) {
        return (flightParameters.MAP_SIZE / 180.0) * (90 - lat);
      }
      function normalizeToMap(x, y, flightParameters) {
        var n_x = (x - flightParameters.MIN_X) / (flightParameters.MAX_X - flightParameters.MIN_X),
          n_y = (y - flightParameters.MIN_Y) / (flightParameters.MAX_Y - flightParameters.MIN_Y);
        return [n_x * 1000 - flightParameters.MAP_SIZE / 2, n_y * 1000 - flightParameters.MAP_SIZE / 2];
      }
      var x = longitudToX(lon, flightParameters),
        y = latitudeToY(lat, flightParameters),
        position = normalizeToMap(x, y, flightParameters);
      if (z > flightParameters.start_AMSL) {
        z -= flightParameters.start_AMSL;
      }
      var processed_coordinates = {
        x: position[0],
        y: position[1],
        z: z
      };
      if (r && r > LOITER_LIMIT) {
        this._loiter_radius = r * LOITER_RADIUS_FACTOR;
        this._loiter_center = processed_coordinates;
        this._loiter_coordinates = [];
        this._last_loiter_point_reached = -1;
        var x1, y1;
        //for (var angle = 0; angle <360; angle+=8){ //counter-clockwise
        for (var angle = 360; angle > 0; angle-=8){ //clockwise
          x1 = this._loiter_radius * Math.cos(angle * (Math.PI / 180)) + this._loiter_center.x;
          y1 = this._loiter_radius * Math.sin(angle * (Math.PI / 180)) + this._loiter_center.y;
          this._loiter_coordinates.push(this.processCurrentPosition(x1, y1, z));
        }
      }
      this._last_altitude_point_reached = -1;
      this.takeoff_path = [];
      return processed_coordinates;
    };
    DroneAaileFixeAPI.prototype.processCurrentPosition = function (x, y, z) {
      //convert x-y coordinates into latitud-longitude
      var flightParameters = this.getFlightParameters();
      var lon = x + flightParameters.map_width / 2;
      lon = lon / 1000;
      lon = lon * (flightParameters.MAX_X - flightParameters.MIN_X) + flightParameters.MIN_X;
      lon = lon / (flightParameters.map_width / 360.0) - 180;
      var lat = y + flightParameters.map_height / 2;
      lat = lat / 1000;
      lat = lat * (flightParameters.MAX_Y - flightParameters.MIN_Y) + flightParameters.MIN_Y;
      lat = 90 - lat / (flightParameters.map_height / 180.0);
      return {
        x: lat,
        y: lon,
        z: z
      };
    };
    DroneAaileFixeAPI.prototype.loiter = function (drone) {
      function distance(c1, c2) {
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
      if (this._loiter_radius > LOITER_LIMIT) {
        var drone_pos = drone.getCurrentPosition();
        //shift loiter circle to nearest point
        if (this._last_loiter_point_reached === -1) {
          if (!this.shifted) {
            drone._maxSpeed = drone._maxSpeed * LOITER_SPEED_FACTOR;
            var min = 9999, min_i;
            for (var i = 0; i < this._loiter_coordinates.length; i++){
              var d = distance([drone_pos.x, drone_pos.y], [this._loiter_coordinates[i].x, this._loiter_coordinates[i].y]);
              if (d < min) {
                min = d;
                min_i = i;
              }
            }
            this._loiter_coordinates = this._loiter_coordinates.concat(this._loiter_coordinates.splice(0,min_i));
            this.shifted = true;
          }
        } else {
          this.shifted = false;
        }
        //stop
        if (this._last_loiter_point_reached === this._loiter_coordinates.length - 1) {
          if (drone._maxSpeed !== this.getMaxSpeed()) {
            drone._maxSpeed = this.getMaxSpeed();
          }
          drone.setDirection(0, 0, 0);
          return;
        }
        //loiter
        var next_point = this._loiter_coordinates[this._last_loiter_point_reached + 1];
        drone.setTargetCoordinates(next_point.x, next_point.y, next_point.z, -1);
        if (distance([drone_pos.x, drone_pos.y], [next_point.x, next_point.y]) < 1) {
          this._last_loiter_point_reached += 1;
          if (this._last_loiter_point_reached === this._loiter_coordinates.length - 1) {
            return;
          }
          next_point = this._loiter_coordinates[this._last_loiter_point_reached + 1];
          drone.setTargetCoordinates(next_point.x, next_point.y, next_point.z, -1);
        }
      }
    };
    DroneAaileFixeAPI.prototype.getDroneAI = function () {
      return null;
    };
    DroneAaileFixeAPI.prototype.setAltitude = function (altitude, drone, skip_loiter) {
      this.takeoff_path = [];
      if (skip_loiter) {
        var drone_pos = drone.getCurrentPosition();
        drone.setTargetCoordinates(drone_pos.x, drone_pos.y, altitude);
        return;
      }
      var x1, y1,
        LOOPS = 1,
        CIRCLE_ANGLE = 8,
        current_point = 0,
        total_points = 360/CIRCLE_ANGLE*LOOPS,
        initial_altitude = drone.getAltitudeAbs(),
        center = {
          x: drone._controlMesh.position.x,
          y: drone._controlMesh.position.z,
          z: drone._controlMesh.position.y
        };
      for (var l = 0; l <= LOOPS; l+=1){
        for (var angle = 360; angle > 0; angle-=CIRCLE_ANGLE){ //clockwise sense
          current_point++;
          x1 = TAKEOFF_RADIUS * Math.cos(angle * (Math.PI / 180)) + center.x;
          y1 = TAKEOFF_RADIUS * Math.sin(angle * (Math.PI / 180)) + center.y;
          if (current_point < total_points/3) {
            var FACTOR = 0.5;
            x1 = center.x*FACTOR + x1*(1-FACTOR);
            y1 = center.y*FACTOR + y1*(1-FACTOR);
          }
          this.takeoff_path.push({x: x1, y: y1, z: initial_altitude + current_point * (altitude-initial_altitude)/total_points});
        }
      }
    };
    DroneAaileFixeAPI.prototype.reachAltitude = function (drone) {
      function distance(p1, p2) {
        return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                         Math.pow(p1[1] - p2[1], 2));
      }
      //stop
      if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
        this._last_altitude_point_reached = -1;
        this.takeoff_path = [];
        drone._start_altitude = 0;
        drone.setDirection(0, 0, 0);
        return;
      }
      //loiter
      var drone_pos = {
          x: drone._controlMesh.position.x,
          y: drone._controlMesh.position.z,
          z: drone._controlMesh.position.y
        };
      var next_point = this.takeoff_path[this._last_altitude_point_reached + 1];
      drone.internal_setTargetCoordinates(next_point.x, next_point.y, next_point.z);
      if (distance([drone_pos.x, drone_pos.y], [next_point.x, next_point.y]) < 1) {
        this._last_altitude_point_reached += 1;
        if (this._last_altitude_point_reached === this.takeoff_path.length - 1) {
          return;
        }
        next_point = this.takeoff_path[this._last_altitude_point_reached + 1];
        drone.internal_setTargetCoordinates(next_point.x, next_point.y, next_point.z);
      }
    };
    DroneAaileFixeAPI.prototype.getMaxSpeed = function () {
      return GAMEPARAMETERS.drone.maxSpeed;
    };
    DroneAaileFixeAPI.prototype.doParachute = function (drone) {
      //TODO what to do here?
      drone.setDirection(0, 0, 0);
    };
    DroneAaileFixeAPI.prototype.getInitialAltitude = function () {
      return 0;
    };
    DroneAaileFixeAPI.prototype.getAltitudeAbs = function (altitude) {
      return altitude;
    };
    DroneAaileFixeAPI.prototype.getMinHeight = function () {
      return 0;
    };
    DroneAaileFixeAPI.prototype.getMaxHeight = function () {
      return 800;
    };
    DroneAaileFixeAPI.prototype.getFlightParameters = function () {
      return this._flight_parameters;
    };
    return DroneAaileFixeAPI;
}());
