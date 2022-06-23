/// <reference path="./GameManager.ts" />

var DroneAPI = /** @class */ (function () {
    //*************************************************** CONSTRUCTOR **************************************************
    function DroneAPI(gameManager, team) {
        this._gameManager = gameManager;
        this._team = team;
    }
    Object.defineProperty(DroneAPI.prototype, "team", {
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
    DroneAPI.prototype.internal_sendMsg = function (msg, to) {
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
    DroneAPI.prototype.log = function (msg) {
        console.log("API say : " + msg);
    };
    DroneAPI.prototype.getGameParameter = function (name) {
        if (["gameTime", "mapSize", "teamSize", "derive", "meteo", "initialHumanAreaPosition"].includes(name))
          return this._gameManager.gameParameter[name];
    };
    DroneAPI.prototype.getMapInfos = function () {
      return {
        width: GAMEPARAMETERS.mapSize.width,
        depth: GAMEPARAMETERS.mapSize.depth,
        height: GAMEPARAMETERS.mapSize.height
      };
    };
    DroneAPI.prototype._isWithinDroneView = function (drone_position, element_position) {
        // Check if element is under the drone cone-view
        var angle = GAMEPARAMETERS.drone.viewAngle ? GAMEPARAMETERS.drone.viewAngle : 60,
          radius = drone_position.z * Math.tan(angle/2 * Math.PI/180),
          distance = (drone_position.x - element_position.x) * (drone_position.x - element_position.x) +
            (drone_position.y - element_position.y) * (drone_position.y - element_position.y);
        if (distance < (radius*radius))
          return true;
        return false;
    };
    DroneAPI.prototype._getProbabilityOfDetection = function (drone_position) {
        var h = drone_position.z,
          km = GAMEPARAMETERS.meteo;
          prob = 20 * (1 + (110-h)/25) * km;
        return prob;
    };
    DroneAPI.prototype.isHumanPositionSpottedCalculation = function (drone) {
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
    DroneAPI.prototype.isHumanPositionSpotted = function (drone) {
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
    return DroneAPI;
}());
