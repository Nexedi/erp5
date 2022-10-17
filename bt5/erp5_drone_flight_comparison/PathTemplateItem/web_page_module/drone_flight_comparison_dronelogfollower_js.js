/**************************** DRONE LOG FOLLOWER ******************************/

function longitudToX(lon, map_size) {
  return (map_size / 360.0) * (180 + lon);
}
function latitudeToY(lat, map_size) {
  return (map_size / 180.0) * (90 - lat);
}
function normalizeToMap(x, y, map_dict) {
  var n_x = (x - map_dict.min_x) / (map_dict.max_x - map_dict.min_x),
      n_y = (y - map_dict.min_y) / (map_dict.max_y - map_dict.min_y);
  return [n_x * 1000 - map_dict.map_size / 2,
          n_y * 1000 - map_dict.map_size / 2];
}
function distance(p1, p2) {
  return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                   Math.pow(p1[1] - p2[1], 2));
}
function latLonDistance(c1, c2) {
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

var DroneLogAPI = /** @class */ (function () {
  //** CONSTRUCTOR
  function DroneLogAPI(gameManager, drone_info, flight_parameters) {
    this._gameManager = gameManager;
    this._drone_info = drone_info;
    this._flight_parameters = flight_parameters;
  }

  DroneLogAPI.prototype.parseLog = function (log_content) {
    var log = log_content,
      min_height = 15,
      SPEED_FACTOR = 0.75;
    function getLogInfo(log) {
      var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
        log_header_found, splitted_log_entry, lat, lon, max_lon = 0,
        max_lat = 0, min_lon = 99999, min_lat = 99999, max_width, max_height;
      for (i = 0; i < line_list.length; i += 1) {
        if (!log_header_found && !line_list[i].includes("timestamp;")) {
          continue;
        } else {
          log_header_found = true;
        }
        if (line_list[i].indexOf("AMSL") >= 0 ||
            !line_list[i].includes(";")) {
          continue;
        }
        log_entry = line_list[i].trim();
        if (log_entry) {
          log_entry_list.push(log_entry);
          splitted_log_entry = log_entry.split(";");
          lat = parseFloat(splitted_log_entry[1]);
          lon = parseFloat(splitted_log_entry[2]);
          if (lon < min_lon) {
            min_lon = lon;
          }
          if (lat < min_lat) {
            min_lat = lat;
          }
          if (lon > max_lon) {
            max_lon = lon;
          }
          if (lat > max_lat) {
            max_lat = lat;
          }
        }
      }
      max_width = latLonDistance([min_lat, min_lon], [min_lat, max_lon]);
      max_height = latLonDistance([min_lat, min_lon], [max_lat, min_lon]);
      var map_size = Math.ceil(Math.max(max_width, max_height)) * 0.6;
      return {
        "log_entry_list": log_entry_list,
        "min_lat": min_lat,
        "min_lon": min_lon,
        "max_lat": max_lat,
        "max_lon": max_lon,
        "map_size": map_size,
        "width": map_size,
        "depth": map_size,
        "min_x": longitudToX(min_lon, map_size),
        "min_y": latitudeToY(min_lat, map_size),
        "max_x": longitudToX(max_lon, map_size),
        "max_y": latitudeToY(max_lat, map_size)
      };
    }
    var i,
      splitted_log_entry, start_time, end_time, x, y, position, lat, lon,
      previous, start_position, dist = 0, average_speed = 0,
      flight_time, log_interval_time, previous_log_time, height, timestamp,
      time_offset = 1, log_info = getLogInfo(log),
      flight_dist = 0, start_AMSL = 0, log_entry_list = log_info.log_entry_list;
    if (log_entry_list[0] && log_entry_list[1]) {
      var entry_1 = log_entry_list[0].split(";"),
        entry_2 = log_entry_list[1].split(";"),
        interval = parseInt(entry_2[0], 10) - parseInt(entry_1[0], 10);
      //if interval > 1' then timestamp is in microseconds
      if (Math.floor(interval / 1000) > 60) {
        time_offset = 1000;
      }
    }
    for (i = 0; i < log_entry_list.length; i += 1) {
      splitted_log_entry = log_entry_list[i].split(";");
      timestamp = parseInt(splitted_log_entry[0], 10);
      if (i === 0) {
        log_interval_time = 0;
        start_time = timestamp;
      } else {
        log_interval_time += (parseInt(splitted_log_entry[0], 10) -
          previous_log_time);
      }
      previous_log_time = parseInt(splitted_log_entry[0], 10);
      average_speed += parseFloat(splitted_log_entry[8]);
      lat = parseFloat(splitted_log_entry[1]);
      lon = parseFloat(splitted_log_entry[2]);
      if (i === log_entry_list.length - 1) {
        end_time = timestamp;
      }
      height = parseFloat(splitted_log_entry[4]);
      if (height < min_height) {
        height = min_height;
      } else {
        height = height;
      }
      x = longitudToX(lon, log_info.map_size);
      y = latitudeToY(lat, log_info.map_size);
      position = normalizeToMap(x, y, log_info);
      if (!previous) {
        start_AMSL = parseFloat(splitted_log_entry[3]);
        start_position = position;
        start_position.push(height);
        previous = position;
      }
      dist = distance(previous, position);
      flight_dist += dist;
      previous = position;
      if (dist > 15) {
        previous = position;
        // XXX: old pre-drawn flight path (obsolete?)
        /*path_point = {
          "type": "box",
          "position": {
            "x": position[0],
            "y": position[1],
            "z": height
          },
          "scale": {
            "x": 3.5,
            "y": 3.5,
            "z": 3.5
          },
          "color": {
            "r": 0,
            "g": 255,
            "b": 0
          },
          "timestamp": timestamp
        };
        path_point_list.push(path_point);*/
      }
    }
    //log_info.draw_path_point_list = path_point_list;
    log_info.average_speed = average_speed / log_entry_list.length;
    log_info.log_interval_time = log_interval_time / log_entry_list.length / time_offset;
    log_info.flight_time = (end_time - start_time) / 1000 / time_offset;
    log_info.initialPosition = {
      "x": start_position[0],
      "y": start_position[1],
      "z": start_position[2]
    };
    log_info.maxSpeed = (flight_dist / log_info.flight_time) * SPEED_FACTOR;
    log_info.height = 100;
    log_info.start_AMSL = start_AMSL;
    return log_info;
  };
  /*
  ** Function called at start phase of the drone, just before onStart AI script
  */
  DroneLogAPI.prototype.internal_start = function () {
    var log = this._drone_info.log_content,
      map_dict = this._gameManager._mapManager.getMapInfo(),
      min_height = 15,
      SPEED_FACTOR = 0.75,
      converted_log_point_list = [];
    function getLogEntries(log) {
      var i, line_list = log.split('\n'), log_entry_list = [], log_entry,
        log_header_found;
      for (i = 0; i < line_list.length; i += 1) {
        if (!log_header_found && !line_list[i].includes("timestamp;")) {
          continue;
        } else {
          log_header_found = true;
        }
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
    var i, splitted_log_entry, x, y, position, lat, lon, height, timestamp,
      time_offset = 1, log_entry_list = getLogEntries(log);
    //XXX: Patch to determine log time format (if this is standarized, drop it)
    if (log_entry_list[0] && log_entry_list[1]) {
      var entry_1 = log_entry_list[0].split(";"),
        entry_2 = log_entry_list[1].split(";"),
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
      x = longitudToX(lon, map_dict.map_size);
      y = latitudeToY(lat, map_dict.map_size);
      position = normalizeToMap(x, y, map_dict);
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
      'me.checkpoint_list = me.flightParameters.converted_log_point_list;' +
      'if (me.checkpoint_list.length === 0)' +
      'throw "flight log is empty or it does not contain valid entries";' +
      'me.startTime = new Date();' +
      'me.initTimestamp = me.checkpoint_list[0][3];' +
      'me.setTargetCoordinates(me.checkpoint_list[0][0], me.checkpoint_list[0][1], me.checkpoint_list[0][2]);' +
      'me.last_checkpoint_reached = -1;' +
      'me.setAcceleration(10);' +
      '};' +
      'me.onUpdate = function () {' +
      'var next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
      'if (distance([me.position.x, me.position.y], next_checkpoint) < 12) {' +
      'me.going = false;' +
      'var log_elapsed = next_checkpoint[3] - me.initTimestamp,' +
      'time_elapsed = new Date() - me.startTime;' +
      'if (time_elapsed < log_elapsed) {' +
      'me.setDirection(0, 0, 0);' +
      'return;' +
      '}' +
      'if (me.last_checkpoint_reached + 1 === me.checkpoint_list.length - 1) {' +
      'me.exit(0);' +
      'return;' +
      '}' +
      'me.last_checkpoint_reached += 1;' +
      'next_checkpoint = me.checkpoint_list[me.last_checkpoint_reached+1];' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
      '} else {' +
      'if (!me.going) {' +
      'me.setTargetCoordinates(next_checkpoint[0], next_checkpoint[1], next_checkpoint[2]);' +
      'me.going = true;' +
      '}' +
      '}' +
      '};';
  };
  DroneLogAPI.prototype.set_loiter_mode = function (radius, drone) {
  };
  DroneLogAPI.prototype.setAltitude = function (altitude, drone) {
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
  DroneLogAPI.prototype.exit = function (drone) {
  };
  return DroneLogAPI;
}());