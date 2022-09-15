/// <reference path="./GameManager.ts" />

var DroneLogAPI = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneLogAPI(gameManager, team, flight_parameters) {
        this._gameManager = gameManager;
        this._team = team;
        this._flight_parameters = flight_parameters;
    }
    Object.defineProperty(DroneLogAPI.prototype, "team", {
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
    DroneLogAPI.prototype.internal_sendMsg = function (msg, to) {
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
    DroneLogAPI.prototype.log = function (msg) {
        console.log("API say : " + msg);
    };
    DroneLogAPI.prototype.getGameParameter = function (name) {
        if (["gameTime", "mapSize", "teamSize", "derive", "meteo", "initialHumanAreaPosition"].includes(name))
          return this._gameManager.gameParameter[name];
    };
    DroneLogAPI.prototype._isWithinDroneView = function (drone_position, element_position) {
        // Check if element is under the drone cone-view
        var angle = GAMEPARAMETERS.drone.viewAngle ? GAMEPARAMETERS.drone.viewAngle : 60,
          radius = drone_position.z * Math.tan(angle/2 * Math.PI/180),
          distance = (drone_position.x - element_position.x) * (drone_position.x - element_position.x) +
            (drone_position.y - element_position.y) * (drone_position.y - element_position.y);
        if (distance < (radius*radius))
          return true;
        return false;
    };
    DroneLogAPI.prototype._getProbabilityOfDetection = function (drone_position) {
        var h = drone_position.z,
          km = GAMEPARAMETERS.meteo;
          prob = 20 * (1 + (110-h)/25) * km;
        return prob;
    };
    DroneLogAPI.prototype.isHumanPositionSpottedCalculation = function (drone) {
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
    DroneLogAPI.prototype.isHumanPositionSpotted = function (drone) {
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
    DroneLogAPI.prototype.processCoordinates = function (x, y, z) {
      if(isNaN(x) || isNaN(y) || isNaN(z)){
        throw new Error('Target coordinates must be numbers');
      }
      return {
        x: x,
        y: y,
        z: z
      };
    };
    DroneLogAPI.prototype.getDroneAI = function () {
      return 'function distance(p1, p2) {' +
        'var a = p1[0] - p2[0],' +
        'b = p1[1] - p2[1];' +
        'return Math.sqrt(a * a + b * b);' +
        '}' +
        'me.onStart = function() {' +
        'console.log("DRONE LOG START! - TODO: set flight parameters with log path. Direction set!");' +
        'me.setDirection(1, 1, 0);' +
        'me.setAcceleration(10);' +
        'return;' +
        'if (!me.getFlightParameters())' +
        'throw "DroneLog API must implement getFlightParameters";' +
        'me.flightParameters = me.getFlightParameters();' +
        'me.checkpoint_list = me.flightParameters.converted_log_point_list;' +
        'me.startTime = new Date();' +
        'me.initTimestamp = me.flightParameters.converted_log_point_list[0][3];' +
        'me.setTargetCoordinates(me.checkpoint_list[0][0], me.checkpoint_list[0][1], me.checkpoint_list[0][2]);' +
        'me.last_checkpoint_reached = -1;' +
        'me.setAcceleration(10);' +
        '};' +
        'me.onUpdate = function () {' +
        'return;' +
        'var next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
        'if (distance([me.position.x, me.position.y], next_checkpoint) < 12) {' +
        'var log_elapsed = next_checkpoint[3] - me.initTimestamp,' +
        'time_elapsed = new Date() - me.startTime;' +
        'if (time_elapsed < log_elapsed) {' +
        'me.setDirection(0, 0, 0);' +
        'return;' +
        '}' +
        'if (me.last_checkpoint_reached + 1 === me.checkpoint_list.length - 1) {' +
        'me.setTargetCoordinates(me.position.x, me.position.y, me.position.z);' +
        'return;' +
        '}' +
        'me.last_checkpoint_reached += 1;' +
        'next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
        'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
        '} else {' +
        'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
        '}' +
        '};';
    };
    DroneLogAPI.prototype.setAltitude = function (altitude) {
      return altitude;
    };
    DroneLogAPI.prototype.getMaxSpeed = function () {
      return 3000;
    };
    DroneLogAPI.prototype.getInitialAltitude = function () {
      return 0;
    };
    DroneLogAPI.prototype.getAltitudeAbs = function () {
      return 0;
    };
    DroneLogAPI.prototype.getMinHeight = function () {
      return 0;
    };
    DroneLogAPI.prototype.getMaxHeight = function () {
      return 220;
    };
    DroneLogAPI.prototype.getFlightParameters = function () {
      return this._flight_parameters;
    };
    return DroneLogAPI;
}());
