/*global console*/
/*jslint nomen: true, indent: 2, maxlen: 80, white: true */

/**************************** DRONE LOG FOLLOWER ******************************/

var DroneLogAPI = /** @class */ (function () {
  "use strict";
  //** CONSTRUCTOR
  function DroneLogAPI(gameManager, drone_info, flight_parameters, id) {
    this._gameManager = gameManager;
    this._mapManager = this._gameManager._mapManager;
    this._drone_info = drone_info;
    this._flight_parameters = flight_parameters;
  }
  /*
  ** Function called at start phase of the drone, just before onStart AI script
  */
  DroneLogAPI.prototype.internal_start = function () {
    function getLogEntries(log) {
      var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
        log_header_found;
      for (i = 0; i < line_list.length; i += 1) {
        if (!log_header_found && !line_list[i].includes("timestamp;")) {
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
      map_dict = this._mapManager.getMapInfo(),
      min_height = 15, converted_log_point_list = [],
      i, splitted_log_entry, x, y, position, lat, lon, height, timestamp,
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
      x = this._mapManager.longitudToX(lon, map_dict.map_size);
      y = this._mapManager.latitudeToY(lat, map_dict.map_size);
      position = this._mapManager.normalize(x, y, map_dict);
      height = parseFloat(splitted_log_entry[4]);
      if (height < min_height) {
        height = min_height;
      }
      converted_log_point_list.push([position[0],
                                    position[1],
                                    height, timestamp / time_offset]);
    }
    this._flight_parameters.converted_log_point_list = converted_log_point_list;
  };
  /*
  ** Function called on every drone update, right after onUpdate AI script
  */
  DroneLogAPI.prototype.internal_update = function () {
    return;
  };
  DroneLogAPI.prototype.internal_setTargetCoordinates =
    function (drone, x, y, z) {
    var coordinates = this.processCoordinates(x, y, z);
    coordinates.x -= drone._controlMesh.position.x;
    coordinates.y -= drone._controlMesh.position.z;
    coordinates.z -= drone._controlMesh.position.y;
    drone.setDirection(coordinates.x, coordinates.y, coordinates.z);
    drone.setAcceleration(drone._maxAcceleration);
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
      'me.setAcceleration(10);' +
      '};' +
      'me.onUpdate = function(timestamp) {' +
      'var next_checkpoint = me.checkpoint_list' +
      '[me.last_checkpoint_reached+1];' +
      'if (distance([me.position.x, me.position.y], next_checkpoint) < 12) {' +
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
      x: x,
      y: y,
      z: z
    };
  };
  DroneLogAPI.prototype.set_loiter_mode = function (radius, drone) {
    return;
  };
  DroneLogAPI.prototype.setAltitude = function (altitude, drone) {
    return;
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
  DroneLogAPI.prototype.triggerParachute = function (drone) {
    return;
  };
  DroneLogAPI.prototype.getFlightParameters = function () {
    return this._flight_parameters;
  };
  DroneLogAPI.prototype.exit = function (drone) {
    return;
  };

  return DroneLogAPI;
}());