/*global GameManager, console*/
/*jslint nomen: true, indent: 2, maxerr: 3, maxlen: 80 */

var runGame, updateGame, eventGame, game_manager_instance;
// game.js
(function () {
  "use strict";
  console.log('game logic');

  runGame = function (canvas, script, game_parameters_json, log) {

    function processLog(game_parameters_json, log) {
      var MAP_SIZE = 1000,
        MIN_HEIGHT = 15,
        MIN_X,
        MAX_X,
        MIN_Y,
        MAX_Y,
        SPEED_FACTOR = 0.75,
        log_point_list = [],
        converted_log_point_list = [];
      function longitudToX(lon) {
        return (MAP_SIZE / 360.0) * (180 + lon);
      }
      function latitudeToY(lat) {
        return (MAP_SIZE / 180.0) * (90 - lat);
      }
      function normalizeToMap(x, y) {
        var n_x = (x - MIN_X) / (MAX_X - MIN_X),
          n_y = (y - MIN_Y) / (MAX_Y - MIN_Y);
        return [n_x * 1000 - MAP_SIZE / 2, n_y * 1000 - MAP_SIZE / 2];
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
      function distance(p1, p2) {
        return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                         Math.pow(p1[1] - p2[1], 2));
      }
      var path_point_list = [], max_width, max_height,
        line_list = log.split('\n'), log_entry_list = [],
        i, start_time, end_time, log_entry, splitted_log_entry,
        lat, lon, x, y, position, min_lon = 99999, min_lat = 99999,
        max_lon = 0, max_lat = 0, previous, start_position, dist = 0,
        path_point, average_speed = 0, flight_time, log_interval_time,
        previous_log_time, height, timestamp, destination_lon,
        destination_lat, log_header_found, time_offset = 1,
        flight_dist = 0, start_AMSL = 0;
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
          //get min and max lat and lon
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
      //get map size from max distance
      max_width = latLonDistance([min_lat, min_lon], [min_lat, max_lon]);
      max_height = latLonDistance([min_lat, min_lon], [max_lat, min_lon]);
      MAP_SIZE = Math.ceil(Math.max(max_width, max_height)) * 0.6;
      MIN_X = longitudToX(min_lon);
      MAX_X = longitudToX(max_lon);
      MIN_Y = latitudeToY(min_lat);
      MAX_Y = latitudeToY(max_lat);
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
          destination_lon = lon;
          destination_lat = lat;
          end_time = timestamp;
        }
        height = parseFloat(splitted_log_entry[4]);
        if (height < MIN_HEIGHT) {
          height = MIN_HEIGHT;
        } else {
          height = height;
        }
        x = longitudToX(lon);
        y = latitudeToY(lat);
        position = normalizeToMap(x, y);
        if (!previous) {
          start_AMSL = parseFloat(splitted_log_entry[3]);
          start_position = position;
          start_position.push(height);
          previous = position;
        }
        dist = distance(previous, position);
        flight_dist += dist;
        if (dist > 15) {
          previous = position;
          path_point = {
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
            "rotation": {
              "x": 0,
              "y": 0,
              "z": 0
            },
            "color": {
              "r": 0,
              "g": 255,
              "b": 0
            },
            "timestamp": timestamp
          };
          path_point_list.push(path_point);
        }
        converted_log_point_list.push([position[0],
                                      position[1],
                                      height, timestamp / time_offset]);
        log_point_list.push([parseFloat(splitted_log_entry[1]),
                            parseFloat(splitted_log_entry[2]),
                            height, timestamp]);
      }
      average_speed = average_speed / log_entry_list.length;
      log_interval_time = log_interval_time / log_entry_list.length / time_offset;
      flight_time = (end_time - start_time) / 1000 / time_offset;
      game_parameters_json.compareFlights = {
        log: true,
        draw: true,
        map_width: MAP_SIZE,
        map_height: MAP_SIZE,
        MAP_SIZE: MAP_SIZE,
        MIN_X: MIN_X,
        MAX_X: MAX_X,
        MIN_Y: MIN_Y,
        MAX_Y: MAX_Y,
        start_AMSL: start_AMSL,
        flight_time: flight_time,
        average_speed: average_speed,
        log_interval_time: log_interval_time,
        path: path_point_list,
        full_log: log_point_list,
        converted_log_point_list: converted_log_point_list
      };
      game_parameters_json.drone.maxSpeed = (flight_dist / flight_time) * SPEED_FACTOR;
      game_parameters_json.obstacles = path_point_list;
      game_parameters_json.randomSpawn.leftTeam.position.x = start_position[0];
      game_parameters_json.randomSpawn.leftTeam.position.y = start_position[1];
      game_parameters_json.randomSpawn.leftTeam.position.z = start_position[2];
      game_parameters_json.gameTime = flight_time;
      //give map some margin from the flight
      game_parameters_json.mapSize.width = MAP_SIZE * 1.10;
      game_parameters_json.mapSize.depth = MAP_SIZE * 1.10;
      //flight destination
      var destination_x = longitudToX(destination_lon),
        destination_y = latitudeToY(destination_lat),
        destination = normalizeToMap(destination_x, destination_y);
      game_parameters_json.randomSpawn.rightTeam.position.x = destination[0];
      game_parameters_json.randomSpawn.rightTeam.position.y = destination[1];
      return game_parameters_json;
    }
    game_parameters_json = processLog(game_parameters_json, log);
    if (!game_manager_instance) {
      game_manager_instance = new GameManager(canvas, script,
                                              game_parameters_json, 5);
    }
    return game_manager_instance.run();
  };

  updateGame = function () {
    if (game_manager_instance) {
      return game_manager_instance.update();
    }
  };

  /*eventGame = function (event) {
    return game_manager_instance.event(event);
  };*/

  /*// Resize canvas on window resize
  window.addEventListener('resize', function () {
    engine.resize();
  });*/


}(this));