/*global BABYLON, console*/
/*jslint nomen: true, indent: 2, maxlen: 80, white: true */

/**************************** DRONE LOG FOLLOWER ******************************/

var DroneLogAPI = /** @class */ (function () {
  "use strict";
  var TOP_SPEED = 250; //so fast that it virtually "teleports" to target
  //** CONSTRUCTOR
  function DroneLogAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._drone_info = drone_info;
    this._flight_parameters = flight_parameters;
  }
  Object.defineProperty(DroneLogAPI.prototype, "isCollidable", {
    get: function () { return false; },
    enumerable: true,
    configurable: true
  });
  /*
  ** Function called at start phase of the drone, just before onStart AI script
  */
  DroneLogAPI.prototype.internal_start = function (drone) {
    drone._minAcceleration = -1;
    drone._maxAcceleration = 1;
    drone._minSpeed = TOP_SPEED;
    drone._maxSpeed = TOP_SPEED;
    drone._acceleration = 10;
    drone._speed = TOP_SPEED;
    function getLogEntries(log) {
      var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
        log_header_found;
      for (i = 0; i < line_list.length; i += 1) {
        if (!log_header_found && !line_list[i].includes("timestamp (ms);")) {
          continue;
        }
        log_header_found = true;
        if (line_list[i].indexOf("AMSL") >= 0 ||
            !line_list[i].includes(";")) {
          continue;
        }
        log_entry = line_list[i].trim();
        if (log_entry) {
          log_entry_list.push(log_entry);
        }
      }
      return log_entry_list;
    }
    var log = this._drone_info.log_content, entry_1, entry_2, interval,
      min_height = 15, converted_log_point_list = [],
      i, splitted_log_entry, position, lat, lon, height, timestamp,
      time_offset = 1, log_entry_list = getLogEntries(log);
    //XXX: Patch to determine log time format (if this is standarized, drop it)
    if (log_entry_list[0] && log_entry_list[1]) {
      entry_1 = log_entry_list[0].split(";");
      entry_2 = log_entry_list[1].split(";");
      interval = parseInt(entry_2[0], 10) - parseInt(entry_1[0], 10);
      //if interval > 1' then timestamp is in microseconds
      if (Math.floor(interval / 1000) > 60) {
        time_offset = 1000;
      }
    }
    for (i = 0; i < log_entry_list.length; i += 1) {
      splitted_log_entry = log_entry_list[i].split(";");
      timestamp = parseInt(splitted_log_entry[0], 10);
      lat = parseFloat(splitted_log_entry[1]);
      lon = parseFloat(splitted_log_entry[2]);
      height = parseFloat(splitted_log_entry[4]);
      if (height < min_height) {
        height = min_height;
      }
      position = this._mapManager.convertToLocalCoordinates(lat, lon, height);
      converted_log_point_list.push([position.x,
                                    position.y,
                                    position.z, timestamp / time_offset]);
    }
    this._flight_parameters.converted_log_point_list = converted_log_point_list;
  };
  /*
  ** Function called on every drone update, right before onUpdate AI script
  */
  DroneLogAPI.prototype.internal_position_update = function (context, delta_time) {
    var updateSpeed;
    context._speed += context._acceleration * delta_time / 1000;
    if (context._speed > context._maxSpeed) {
      context._speed = context._maxSpeed;
    }
    if (context._speed < -context._maxSpeed) {
      context._speed = -context._maxSpeed;
    }
    updateSpeed = context._speed * delta_time / 1000;
    if (context._direction.x !== 0 ||
        context._direction.y !== 0 ||
        context._direction.z !== 0) {
      context._controlMesh.position.addInPlace(new BABYLON.Vector3(
        context._direction.x * updateSpeed,
        context._direction.y * updateSpeed,
        context._direction.z * updateSpeed));
    }
    context._controlMesh.computeWorldMatrix(true);
    context._mesh.computeWorldMatrix(true);
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  DroneLogAPI.prototype.internal_info_update = function (drone) {
    return;
  };
  DroneLogAPI.prototype.internal_setTargetCoordinates =
    function (drone, coordinates) {
    coordinates.x -= drone._controlMesh.position.x;
    coordinates.y -= drone._controlMesh.position.z;
    coordinates.z -= drone._controlMesh.position.y;
    drone.setDirection(coordinates.x, coordinates.y, coordinates.z);
    return;
  };
  DroneLogAPI.prototype.sendMsg = function (msg, to) {
    return;
  };
  DroneLogAPI.prototype.log = function (msg) {
    console.log("API say : " + msg);
  };
  DroneLogAPI.prototype.getGameParameter = function (name) {
    if (["gameTime", "map"].includes(name)) {
      return this._gameManager.gameParameter[name];
    }
  };
  DroneLogAPI.prototype.setStartingPosition = function (drone, x, y, z) {
    if (!drone._canPlay) {
      if (z <= 0.05) {
        z = 0.05;
      }
      drone._controlMesh.position = new BABYLON.Vector3(x, z, y);
    }
    drone._controlMesh.computeWorldMatrix(true);
    drone._mesh.computeWorldMatrix(true);
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
      'me.checkpoint_list = me.flightParameters.converted_log_point_list;' +
      'if (me.checkpoint_list.length === 0)' +
      'throw "flight log is empty or it does not contain valid entries";' +
      'me.startTime = new Date();' +
      'me.initTimestamp = me.checkpoint_list[0][3];' +
      'me.setTargetCoordinates(me.checkpoint_list[0][0], ' +
      'me.checkpoint_list[0][1], me.checkpoint_list[0][2]);' +
      'me.last_checkpoint_reached = -1;' +
      '};' +
      'me.onUpdate = function(timestamp) {' +
      'var next_checkpoint = me.checkpoint_list' +
      '[me.last_checkpoint_reached+1];' +
      'if (distance([me.position.x, me.position.y], next_checkpoint) < 10) {' +
      'me.going = false;' +
      'var log_elapsed = next_checkpoint[3] - me.initTimestamp,' +
      'time_elapsed = new Date() - me.startTime;' +
      'if (time_elapsed < log_elapsed) {' +
      'me.setDirection(0, 0, 0);' +
      'return;' +
      '}' +
      'if (me.last_checkpoint_reached + 1 === ' +
      'me.checkpoint_list.length - 1) {' +
      'me.exit(0);' +
      'return;' +
      '}' +
      'me.last_checkpoint_reached += 1;' +
      'next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], ' +
      'next_checkpoint[2]);' +
      '} else {' +
      'if (!me.going) {' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], ' +
      'next_checkpoint[2]);' +
      'me.going = true;' +
      '}' +
      '}' +
      '};';
  };

  DroneLogAPI.prototype.getCurrentPosition = function (x, y, z) {
    return {
      latitude: x,
      longitude: y,
      altitude: z
    };
  };
  DroneLogAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  DroneLogAPI.prototype.isReadyToFly = function () {
    return true;
  };
  DroneLogAPI.prototype.getMaxCommandFrequency = function () {
    return Infinity;
  };
  DroneLogAPI.prototype.getOnUpdateInterval = function () {
    return 0;
  };

  return DroneLogAPI;
}());