/*global window, rJS, RSVP, domsugar, console, URL, Error, jIO */
/*jslint nomen: true, indent: 2, maxerr: 30, maxlen: 80, plusplus: true */
(function () {
  "use strict";

  var SIMULATION_SPEED = 100,
    MAP_KEY = "compare_map",
    SCRIPT_KEY = "28", //roque participant script
    //SCRIPT_KEY = "emulate_loiter",
    //SCRIPT_KEY = "emulate_bounce",
    LOG_KEY = "lp_loiter", //LP first log
    //LOG_KEY = "lp_bounce", //LP bounce log
    MAP_SIZE = 1000,
    MIN_HEIGHT = 15,
    MIN_X,
    MAX_X,
    MIN_Y,
    MAX_Y,
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

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")

    .declareJob('run', function () {
      function frechetDistance(a, b) {
        var C = new Float32Array(a.length * b.length),
          dim = a.length,
          i,
          j;
        C[0] = distance(a[0], b[0]);
        for (j = 1; j < dim; j++) {
          C[j] = Math.max(C[j - 1], distance(a[0], b[j]));
        }
        for (i = 1; i < dim; i++) {
          C[i * dim] = Math.max(C[(i - 1) * dim], distance(a[i], b[0]));
        }
        for (i = 1; i < dim; i++) {
          for (j = 1; j < dim; j++) {
            C[i * dim + j] = Math.max(
              Math.min(C[(i - 1) * dim + j], C[(i - 1) * dim + j - 1],
                       C[i * dim + j - 1]),
              distance(a[i], b[j])
            );
          }
        }
        return C[C.length - 1];
      }
      function averageDistance(a, b, z) {
        function distance3D(p1, p2) {
          return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                           Math.pow(p1[1] - p2[1], 2) +
                           Math.pow(p1[2] - p2[2], 2));
        }
        var i, x, y, pos_a, pos_b, sum = 0;
        for (i = 0; i < a.length; i++) {
          x = longitudToX(a[i][1]);
          y = latitudeToY(a[i][0]);
          pos_a = normalizeToMap(x, y);
          x = longitudToX(b[i][1]);
          y = latitudeToY(b[i][0]);
          pos_b = normalizeToMap(x, y);
          if (z) {
            sum += distance3D([pos_a[0], pos_a[1], a[i][2]],
                              [pos_b[0], pos_b[1], b[i][2]]);
          } else {
            sum += distance([pos_a[0], pos_a[1]], [pos_b[0], pos_b[1]]);
          }
        }
        return sum / a.length;
      }
      var gadget = this,
        queue = new RSVP.Queue(),
        game_value,
        fragment = domsugar(gadget.element.querySelector('#fragment'),
                            [domsugar('div')]).firstElementChild;

      gadget.state.json_map.randomSpawn.rightTeam.dispersed = true;
      game_value = JSON.stringify({
        map: gadget.state.json_map,
        autorun: true,
        script: gadget.state.script_content,
        simulation_speed: SIMULATION_SPEED
      });
      queue
        .push(function () {
          return gadget.declareGadget("gadget_drone_simulator.html",
                                      {element: fragment, scope: 'simulator'});
        })
        .push(function (drone_gadget) {
          return drone_gadget.render({
            "key": 'simulator',
            "maximize": false,
            "value": game_value,
            "autorun": true
          });
        })
        .push(function () {
          return gadget.getDeclaredGadget('simulator');
        })
        .push(function (game_editor) {
          return game_editor.getContent();
        })
        .push(function (result) {
          console.log("simulation log:", result);
          console.log("ground truth log:", log_point_list);
          console.log("COMPARISON:");
          for (var i = 0; i < result.length; i += 1) {
            try {
              console.log("frechet distance:",
                          frechetDistance(log_point_list, result[i]));
              console.log("average distance:",
                          averageDistance(log_point_list, result[i], false));
              console.log("average distance with z:",
                          averageDistance(log_point_list, result[i], true));
              console.log("------------------------------------------------");
            } catch (ee) {
              console.log("error calculating distance:", ee);
            }
          }
          return result;
        });
      return queue;
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      if (!options.map) {
        options.map = MAP_KEY;
      }
      options.map = "rescue_swarm_map_module/" + options.map;
      if (!options.script) {
        options.script = SCRIPT_KEY;
      }
      options.script = "rescue_swarm_script_module/" + options.script;
      if (!options.log) {
        options.log = LOG_KEY;
      }
      options.log = "rescue_swarm_script_module/" + options.log;
      return new RSVP.Queue()
        .push(function () {
          return gadget.jio_get(options.script);
        })
        .push(function (script) {
          options.script_content = script.text_content;
          return gadget.jio_get(options.map);
        })
        .push(function (map_doc) {
          options.json_map = JSON.parse(map_doc.text_content);
          return gadget.jio_get(options.log);
        })
        .push(function (log) {
          var path_point_list = [], max_width, max_height,
            line_list = log.text_content.split('\n'), log_entry_list = [],
            i, start_time, end_time, log_entry, splitted_log_entry,
            lat, lon, x, y, position, min_lon = 99999, min_lat = 99999,
            max_lon = 0, max_lat = 0, previous, start_position, dist = 0,
            path_point, average_speed = 0, flight_time, log_interval_time,
            previous_log_time, height, timestamp, destination_lon,
            destination_lat, log_header_found, time_offset = 1, flight_dist = 0;
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
          options.json_map.compareFlights = {
            log: true,
            draw: true,
            map_width: MAP_SIZE,
            map_height: MAP_SIZE,
            MAP_SIZE: MAP_SIZE,
            MIN_X: MIN_X,
            MAX_X: MAX_X,
            MIN_Y: MIN_Y,
            MAX_Y: MAX_Y,
            flight_time: flight_time,
            average_speed: average_speed,
            log_interval_time: log_interval_time,
            path: path_point_list,
            full_log: log_point_list,
            converted_log_point_list: converted_log_point_list
          };
          options.json_map.drone.maxSpeed = flight_dist / flight_time;
          options.json_map.obstacles = path_point_list;
          options.json_map.randomSpawn.leftTeam.position.x = start_position[0];
          options.json_map.randomSpawn.leftTeam.position.y = start_position[1];
          options.json_map.randomSpawn.leftTeam.position.z = start_position[2];
          options.json_map.gameTime = flight_time;
          //give map some margin from the flight
          options.json_map.mapSize.width = MAP_SIZE * 1.10;
          options.json_map.mapSize.depth = MAP_SIZE * 1.10;
          //flight destination
          var destination_x = longitudToX(destination_lon),
            destination_y = latitudeToY(destination_lat),
            destination = normalizeToMap(destination_x, destination_y);
          options.json_map.randomSpawn.rightTeam.position.x = destination[0];
          options.json_map.randomSpawn.rightTeam.position.y = destination[1];
          return gadget.changeState({
            script_content: options.script_content,
            json_map: options.json_map
          });
        });
    })
    .onStateChange(function () {
      var gadget = this;
      return gadget.updateHeader({
        page_title: "Test drone gadget"
      })
        .push(function () {
          gadget.run();
        });
    });
}());