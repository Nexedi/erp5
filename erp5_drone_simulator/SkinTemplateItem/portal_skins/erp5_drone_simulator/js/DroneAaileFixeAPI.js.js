/// <reference path="./GameManager.ts" />

var DroneAaileFixeAPI = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneAaileFixeAPI(gameManager, team, flight_parameters) {
        this._gameManager = gameManager;
        this._team = team;
        this._flight_parameters = flight_parameters;
        this._loiter_radius = 0;
        this._loiter_center = [0, 0, 0];
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
      if (r && r > 30) {
        this._loiter_radius = r;
        this._loiter_center = [position[0], position[1], z];
      }
      return {
        x: position[0],
        y: position[1],
        z: z
      };
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
    /*DroneAaileFixeAPI.prototype.wait = function (drone, time) {
      if (this._gameManager._game_duration - drone._start_wait < time) {
        drone.setDirection(0, 0, 0);
      } else {
        drone._start_wait = 0;
      }
    };*/
    DroneAaileFixeAPI.prototype.loiter = function (drone) {
      //TODO loiter instead of wait
      /*if (this._loiter_radius > 30) {
        this._loiter_radius;
        this._loiter_center;
      }*/
      drone.setDirection(0, 0, 0);
    };
    DroneAaileFixeAPI.prototype.getDroneAI = function () {
      return null;
    };
    DroneAaileFixeAPI.prototype.setAltitude = function (altitude) {
      return altitude;
    };
    DroneAaileFixeAPI.prototype.getMaxSpeed = function () {
      return GAMEPARAMETERS.drone.maxSpeed;
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
