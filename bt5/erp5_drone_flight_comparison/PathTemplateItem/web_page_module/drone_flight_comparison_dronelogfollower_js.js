/**************************** DRONE LOG FOLLOWER ******************************/

var DroneLogAPI = /** @class */ (function () {
  //** CONSTRUCTOR
  function DroneLogAPI(gameManager, drone_info, flight_parameters) {
    this._gameManager = gameManager;
    this._drone_info = drone_info;
    this._flight_parameters = flight_parameters;
  }
  /*
  ** Function called at start phase of the drone, just before onStart AI script
  */
  DroneLogAPI.prototype.internal_start = function () {
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  DroneLogAPI.prototype.internal_update = function () {
  };
  DroneLogAPI.prototype.internal_setTargetCoordinates =
    function (drone, x, y, z, r) {
    var coordinates = this.processCoordinates(x, y, z, r);
    coordinates.x -= drone._controlMesh.position.x; //TODO use position
    coordinates.y -= drone._controlMesh.position.z;
    coordinates.z -= drone._controlMesh.position.y;
    drone.setDirection(coordinates.x, coordinates.y, coordinates.z);
    drone.setAcceleration(drone._maxAcceleration);
    return;
  };
  //TODO test sendMsg (what is iterable _this.team??) (latency.communication?)(GM.delay?)
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
  DroneLogAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  DroneLogAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "map"].includes(name))
      return this._gameManager.gameParameter[name];
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
  //Internal AI: drone follows the flight log points
  DroneLogAPI.prototype.getDroneAI = function () {
    return 'function distance(p1, p2) {' +
      'var a = p1[0] - p2[0],' +
      'b = p1[1] - p2[1];' +
      'return Math.sqrt(a * a + b * b);' +
      '}' +
      'me.onStart = function() {' +
      'console.log("DRONE LOG START!");' +
      'if (!me.getFlightParameters())' +
      'throw "DroneLog API must implement getFlightParameters";' +
      'me.flightParameters = me.getFlightParameters();' +
      'me.checkpoint_list = me.flightParameters.logInfo.converted_log_point_list;' +
      'me.startTime = new Date();' +
      'me.initTimestamp = me.flightParameters.logInfo.converted_log_point_list[0][3];' +
      'me.setTargetCoordinates(me.checkpoint_list[0][0], me.checkpoint_list[0][1], me.checkpoint_list[0][2]);' +
      'me.last_checkpoint_reached = -1;' +
      'me.setAcceleration(10);' +
      '};' +
      'me.onUpdate = function () {' +
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
  DroneLogAPI.prototype.set_loiter_mode = function () {
  };
  DroneLogAPI.prototype.setAltitude = function (altitude) {
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