/// <reference path="./GameManager.ts" />

var DroneAaileFixeAPI = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneAaileFixeAPI(gameManager, team, log_flight_parameters) {
        this._gameManager = gameManager;
        this._team = team;
        this._log_flight_parameters = log_flight_parameters;
        this._convertPosition = function (lon, lat, z) {
          var logFlightParameters = this.getLogFlightParameters();
          function longitudToX(lon, logFlightParameters) {
            return (logFlightParameters.MAP_SIZE / 360.0) * (180 + lon);
          }
          function latitudeToY(lat, logFlightParameters) {
            return (logFlightParameters.MAP_SIZE / 180.0) * (90 - lat);
          }
          function normalizeToMap(x, y, logFlightParameters) {
            var n_x = (x - logFlightParameters.MIN_X) / (logFlightParameters.MAX_X - logFlightParameters.MIN_X),
              n_y = (y - logFlightParameters.MIN_Y) / (logFlightParameters.MAX_Y - logFlightParameters.MIN_Y);
            return [n_x * 1000 - logFlightParameters.MAP_SIZE / 2, n_y * 1000 - logFlightParameters.MAP_SIZE / 2];
          }
          var x = longitudToX(lon, logFlightParameters),
            y = latitudeToY(lat, logFlightParameters),
            position = normalizeToMap(x, y, logFlightParameters);
          return {
            x: position[0],
            y: position[1],
            z: z
          };
        };
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
    DroneAaileFixeAPI.prototype.getDirectionFromCoordinates = function (x, y, z, drone_position) {
      if(isNaN(x) || isNaN(y) || isNaN(z)){
        throw new Error('Target coordinates must be numbers');
      }
      var converted_position = this._convertPosition(y, x, z);
      x = converted_position.x;
      y = converted_position.y;
      z = converted_position.z;

      x -= drone_position.x;
      y -= drone_position.y;
      z -= drone_position.z;
      if (this._team == "R")
        y = -y;
      return {
        x: x,
        y: y,
        z: z
      };
    };
    DroneAaileFixeAPI.prototype.getDroneAI = function () {
      return null;
    };
    DroneAaileFixeAPI.prototype.setAltitude = function (altitude) {
      return altitude;
    };
    DroneAaileFixeAPI.prototype.getMaxSpeed = function () {
      return 3000;
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
    DroneAaileFixeAPI.prototype.getLogFlightParameters = function () {
      return this._log_flight_parameters;
    };
    return DroneAaileFixeAPI;
}());
