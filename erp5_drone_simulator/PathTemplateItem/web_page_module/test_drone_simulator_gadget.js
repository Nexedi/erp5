/*global window, rJS, RSVP, domsugar, console, URL, Error, jIO */
/*jslint nomen: true, indent: 2, maxerr: 30, maxlen: 80, plusplus: true */
(function () {
  "use strict";

  var SIMULATION_SPEED = 100,
    MAP_KEY = "rescue_swarm_map_module/compare_map",
    SCRIPT_KEY = "rescue_swarm_script_module/28",
    LOG_KEY = "rescue_swarm_script_module/log_1",
    MAP_SIZE = 1000;

  rJS(window)
    /////////////////////////////////////////////////////////////////
    // Acquired methods
    /////////////////////////////////////////////////////////////////
    .declareAcquiredMethod("updateHeader", "updateHeader")
    .declareAcquiredMethod("jio_get", "jio_get")

    .declareJob('run', function () {
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
        print_drone_flight: true,
        log_drone_flight: true,
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
          console.log("test result:", result);
          //TODO compare logs
          return result;
        });
      return queue;
    })

    .declareMethod('render', function (options) {
      var gadget = this;
      options.map = MAP_KEY;
      options.script = SCRIPT_KEY;
      options.log = LOG_KEY;
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
            i, min_x, min_y, max_x, max_y, n_x, n_y, start_time, end_time,
            log_entry, splitted_log_entry, lat, lon, x, y, pos_x, pos_y,
            min_lon = 99999, min_lat = 99999, max_lon = 0, max_lat = 0,
            previous, start_position, dist = 0, path_point, average_speed = 0,
            log_interval_time, previous_log_time;
          function distance(x1, y1, x2, y2) {
            var a = x1 - x2,
              b = y1 - y2;
            return Math.sqrt(a * a + b * b);
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
          for (i = 0; i < line_list.length; i += 1) {
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
          MAP_SIZE = Math.ceil(Math.max(max_width, max_height));
          //convert geo cordinates into 2D plane coordinates
          min_x = (MAP_SIZE / 360.0) * (180 + min_lon);
          max_x = (MAP_SIZE / 360.0) * (180 + max_lon);
          min_y = (MAP_SIZE / 180.0) * (90 - min_lat);
          max_y = (MAP_SIZE / 180.0) * (90 - max_lat);
          for (i = 0; i < log_entry_list.length; i += 1) {
            splitted_log_entry = log_entry_list[i].split(";");
            if (i === 0) {
              log_interval_time = 0;
              start_time = parseInt(splitted_log_entry[0]);
            } else {
              log_interval_time += parseInt(splitted_log_entry[0]) - previous_log_time;
            }
            previous_log_time = parseInt(splitted_log_entry[0]);
            if (i === log_entry_list.length - 1) {
              end_time = parseInt(splitted_log_entry[0]);
            }
            average_speed += parseFloat(splitted_log_entry[8]);
            lat = parseFloat(splitted_log_entry[1]);
            lon = parseFloat(splitted_log_entry[2]);
            x = (MAP_SIZE / 360.0) * (180 + lon);
            y = (MAP_SIZE / 180.0) * (90 - lat);
            //normalize coordinate values
            n_x = (x - min_x) / (max_x - min_x);
            n_y = (y - min_y) / (max_y - min_y);
            pos_x = n_x * 1000 - MAP_SIZE / 2;
            pos_y = n_y * 1000 - MAP_SIZE / 2;
            if (!previous) {
              start_position = [pos_x, pos_y];
              previous = [pos_x, pos_y];
            }
            dist = distance(previous[0], previous[1], pos_x, pos_y);
            if (dist > 15) {
              previous = [pos_x, pos_y];
              path_point = {
                "type": "sphere",
                "position": {
                  "x": pos_x,
                  "y": pos_y,
                  "z": 0.1
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
                }
              };
              path_point_list.push(path_point);
            }
          }
          average_speed = average_speed / log_entry_list.length;
          log_interval_time = log_interval_time / log_entry_list.length;
          options.json_map.logFlight = {
            log: true,
            print: true,
            map_width: MAP_SIZE,
            map_height: MAP_SIZE,
            min_x: min_x,
            max_x: max_x,
            min_y: min_y,
            max_y: max_y,
            flight_time: end_time - start_time,
            average_speed: average_speed,
            log_interval_time: log_interval_time
          };
          options.json_map.drone.maxSpeed = average_speed;
          options.json_map.obstacles = path_point_list;
          options.json_map.randomSpawn.leftTeam.position.x = start_position[0];
          options.json_map.randomSpawn.leftTeam.position.y = start_position[1];
          //give map some margin from the flight
          options.json_map.mapSize.width = MAP_SIZE * 1.10;
          options.json_map.mapSize.depth = MAP_SIZE * 1.10;
          return gadget.changeState({
            script_content: options.script_content,
            json_map: options.json_map
          });
        });
    })
    .onStateChange(function () {
      function frechetDistance(a, b) {
        var dist = function (p1, p2) {
          return Math.sqrt(Math.pow(p1[0] - p2[0], 2) +
                           Math.pow(p1[1] - p2[1], 2));
        },
          C = new Float32Array(a.length * b.length),
          dim = a.length,
          i, j;
        C[0] = dist(a[0], b[0]);
        for (j = 1; j < dim; j++) {
          C[j] = Math.max(C[j - 1], dist(a[0], b[j]));
        }
        for (i = 1; i < dim; i++) {
          C[i * dim] = Math.max(C[(i - 1) * dim], dist(a[i], b[0]));
        }
        for (i = 1; i < dim; i++) {
          for (j = 1; j < dim; j++) {
            C[i * dim + j] = Math.max(
              Math.min(C[(i - 1) * dim + j], C[(i - 1) * dim + j - 1],
                       C[i * dim + j - 1]),
              dist(a[i], b[j])
            );
          }
        }
        return C[C.length - 1];
      }
      var gadget = this;
      return gadget.updateHeader({
        page_title: "Test drone gadget"
      })
        .push(function () {
          gadget.run();
        });
    });
}());