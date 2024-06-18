/*jslint nomen: true, indent: 2, maxlen: 80, todo: true, unparam: true */

/******************************* MAP UTILS ************************************/

var MapUtils = /** @class */ (function () {
  "use strict";

  var FLAG_EPSILON = 15, R = 6371e3, FLAG_WEIGHT = 5, FLAG_SCORE = 5;

  //** CONSTRUCTOR
  function MapUtils(map_param) {
    var _this = this;
    _this.map_param = {};
    _this.map_param.height = map_param.height;
    _this.map_param.start_AMSL = map_param.start_AMSL;
    _this.map_param.min_lat = map_param.min_lat;
    _this.map_param.max_lat = map_param.max_lat;
    _this.map_param.min_lon = map_param.min_lon;
    _this.map_param.max_lon = map_param.max_lon;
    _this.map_param.depth = _this.latLonDistance(
      [map_param.min_lat, map_param.min_lon],
      [map_param.max_lat, map_param.min_lon]
    );
    _this.map_param.width = _this.latLonDistance(
      [map_param.min_lat, map_param.min_lon],
      [map_param.min_lat, map_param.max_lon]
    );
    _this.map_info = {
      "depth": _this.map_param.depth,
      "width": _this.map_param.width,
      "flag_distance_epsilon": map_param.flag_distance_epsilon || FLAG_EPSILON
    };
    _this.map_info.height = _this.map_param.height;
    _this.map_info.start_AMSL = _this.map_param.start_AMSL;
    _this.map_info.min_x = _this.longitudToX(map_param.min_lon);
    _this.map_info.min_y = _this.latitudeToY(map_param.min_lat);
    _this.map_info.max_x = _this.longitudToX(map_param.max_lon);
    _this.map_info.max_y = _this.latitudeToY(map_param.max_lat);
  }

  MapUtils.prototype.latLonDistance = function (c1, c2) {
    var q1 = c1[0] * Math.PI / 180,
      q2 = c2[0] * Math.PI / 180,
      dq = (c2[0] - c1[0]) * Math.PI / 180,
      dl = (c2[1] - c1[1]) * Math.PI / 180,
      a = Math.sin(dq / 2) * Math.sin(dq / 2) +
        Math.cos(q1) * Math.cos(q2) *
        Math.sin(dl / 2) * Math.sin(dl / 2),
      c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };
  MapUtils.prototype.longitudToX = function (lon) {
    return (this.map_info.width / 360.0) * (180 + lon);
  };
  MapUtils.prototype.latitudeToY = function (lat) {
    return (this.map_info.depth / 180.0) * (90 - lat);
  };
  MapUtils.prototype.convertToLocalCoordinates =
    function (latitude, longitude, altitude) {
      var map_info = this.map_info,
        x = this.longitudToX(longitude),
        y = this.latitudeToY(latitude);
      return {
        x: (((x - map_info.min_x) / (map_info.max_x - map_info.min_x)) - 0.5)
            * map_info.width,
        y: (((y - map_info.min_y) / (map_info.max_y - map_info.min_y)) - 0.5)
            * map_info.depth,
        z: altitude
      };
    };
  MapUtils.prototype.convertToGeoCoordinates = function (x, y, z) {
    var lon = (x / this.map_info.width) + 0.5,
      lat = (y / this.map_info.depth) + 0.5;
    lon = lon * (this.map_info.max_x - this.map_info.min_x) +
      this.map_info.min_x;
    lon = lon / (this.map_info.width / 360.0) - 180;
    lat = lat * (this.map_info.max_y - this.map_info.min_y) +
      this.map_info.min_y;
    lat = 90 - lat / (this.map_info.depth / 180.0);
    return {
      latitude: lat,
      longitude: lon,
      altitude: z
    };
  };

  /*
  ** Randomizes all map elements: starting point, enemies, flags, obstacles
  */
  MapUtils.prototype.randomizeByBlockTemplates = function (seed) {
    function normalize(x, min, max) {
      return min + (max - min) * x / 100;
    }
    function fillTemplate(template, min_x, min_y, max_x, max_y) {
      function fillFlagList(list, min_x, min_y, max_x, max_y) {
        var i, el, result_list = [];
        for (i = 0; i < list.length; i += 1) {
          el = {"position":
                {"x": 0, "y": 0, "z": 0},
                "score": Math.floor(seed.quick() * FLAG_SCORE) + 1,
                "weight": Math.floor(seed.quick() * FLAG_WEIGHT) + 1
               };
          el.position.x = normalize(list[i].position.x, min_x, max_x);
          el.position.y = normalize(list[i].position.y, min_y, max_y);
          //TODO normalize z to map height?
          el.position.z = list[i].position.z;
          result_list.push(el);
        }
        return result_list;
      }
      function fillEnemyList(list, min_x, min_y, max_x, max_y) {
        var i, el, result_list = [];
        for (i = 0; i < list.length; i += 1) {
          el = {"position":
                {"x": 0, "y": 0, "z": 0},
                "type": list[i].type};
          el.position.x = normalize(list[i].position.x, min_x, max_x);
          el.position.y = normalize(list[i].position.y, min_y, max_y);
          //TODO normalize z to map height?
          el.position.z = list[i].position.z;
          result_list.push(el);
        }
        return result_list;
      }
      function fillObstacleList(list, min_x, min_y, max_x, max_y) {
        var i, el, result_list = [];
        for (i = 0; i < list.length; i += 1) {
          el = {
            "position": {"x": 0, "y": 0, "z": 0},
            "rotation": null,
            "scale": {"x": 0, "y": 0, "z": 0},
            "type": list[i].type
          };
          if (list[i].rotation) {
            el.rotation = {"x": list[i].rotation.x, "y": list[i].rotation.y,
                           "z": list[i].rotation.z};
          }
          el.position.x = normalize(list[i].position.x, min_x, max_x);
          el.position.y = normalize(list[i].position.y, min_y, max_y);
          //TODO normalize z to map height?
          el.position.z = list[i].position.z;
          el.scale.x = normalize(list[i].scale.x, 0, Math.abs(max_x - min_x));
          el.scale.y = normalize(list[i].scale.y, 0, Math.abs(max_x - min_x));
          //TODO normalize z to map height?
          el.scale.z = list[i].scale.z;
          result_list.push(el);
        }
        return result_list;
      }
      return {
        "flag_list":
          fillFlagList(template.flag_list, min_x, min_y, max_x, max_y),
        "obstacle_list":
          fillObstacleList(template.obstacle_list, min_x, min_y, max_x, max_y),
        "enemy_list":
          fillEnemyList(template.enemy_list, min_x, min_y, max_x, max_y)
      };
    }
    // 4x4 grid
    var GRID = 4, i, j, max_width = this.map_info.width,
      max_depth = this.map_info.depth, initial_block, x1, y1, x2, y2,
      block_result, index, block_size = Math.max(max_width, max_depth) / GRID,
      result_map,
      BLOCK_TEMPLATE_LIST = [{
        "flag_list": [{"position":
                      {"x": 50, "y": 50, "z": 10},
                      "score": 1, "weight": 1}],
        "obstacle_list": [{"type": "box",
                          "position": {"x": 50, "y": 70, "z": 20},
                          "scale": {"x": 80, "y": 4, "z": 40},
                          "rotation": {"x": 0, "y": 0, "z": 0}}],
        "enemy_list": [{"type": "EnemyDroneAPI",
                        "position": {"x": 50, "y": 30, "z": 10}}
                      ]
      }, {
        "flag_list": [],
        "obstacle_list": [{"type": "box",
                          "position": {"x": 20, "y": 65, "z": 20},
                          "scale": {"x": 4, "y": 70, "z": 40},
                          "rotation": {"x": 0, "y": 0, "z": 0}},
                          {"type": "box",
                          "position": {"x": 50, "y": 35, "z": 20},
                          "scale": {"x": 4, "y": 70, "z": 40},
                          "rotation": {"x": 0, "y": 0, "z": 0}},
                          {"type": "box",
                          "position": {"x": 80, "y": 65, "z": 20},
                          "scale": {"x": 4, "y": 70, "z": 40},
                          "rotation": {"x": 0, "y": 0, "z": 0}}],
        "enemy_list": []
      }, {
        "flag_list": [],
        "obstacle_list": [{"type": "mountain",
                          "position": {"x": 50, "y": 50, "z": 200},
                          "scale": {"x": 80, "y": 80,
                                    "z": 400} //this.map_info.height?
                          }],
        "enemy_list": []
      }, {
        "flag_list": [],
        "obstacle_list": [],
        "enemy_list": [{"type": "EnemyDroneAPI",
                        "position": {"x": 20, "y": 20, "z": 10}},
                      {"type": "EnemyDroneAPI",
                        "position": {"x": 20, "y": 80, "z": 10}},
                      {"type": "EnemyDroneAPI",
                        "position": {"x": 80, "y": 20, "z": 10}},
                      {"type": "EnemyDroneAPI",
                        "position": {"x": 80, "y": 80, "z": 10}}]
      }, {
        "flag_list": [{"position":
                      {"x": 50, "y": 50, "z": 10},
                      "score": 1, "weight": 1}],
        "obstacle_list": [],
        "enemy_list": []
      }, {
        "flag_list": [{"position":
                      {"x": 50, "y": 50, "z": 10},
                      "score": 1, "weight": 1}],
        "obstacle_list": [],
        "enemy_list": [{"type": "EnemyDroneAPI",
                        "position": {"x": 50, "y": 20, "z": 10}},
                      {"type": "EnemyDroneAPI",
                        "position": {"x": 50, "y": 80, "z": 10}}]
      }, {
        "flag_list": [{"position":
                      {"x": 50, "y": 50, "z": 10},
                      "score": 1, "weight": 1}],
        "obstacle_list": [{"type": "box",
                          "position": {"x": 50, "y": 10, "z": 25},
                          "scale": {"x": 80, "y": 2, "z": 50},
                          "rotation": {"x": 0, "y": 0, "z": 0}},
                        {"type": "box",
                          "position": {"x": 10, "y": 50, "z": 25},
                          "scale": {"x": 2, "y": 80, "z": 50},
                          "rotation": {"x": 0, "y": 0, "z": 0}},
                        {"type": "box",
                          "position": {"x": 50, "y": 90, "z": 25},
                          "scale": {"x": 80, "y": 2, "z": 50},
                          "rotation": {"x": 0, "y": 0, "z": 0}},
                        {"type": "box",
                          "position": {"x": 90, "y": 50, "z": 25},
                          "scale": {"x": 2, "y": 80, "z": 50},
                          "rotation": {"x": 0, "y": 0, "z": 0}}],
        "enemy_list": []
      }, {
        "flag_list": [],
        "obstacle_list": [],
        "enemy_list": []
      }];
    function getInitialBlock(GRID) {
      var x, y;
      do {
        x = Math.floor(seed.quick() * GRID);
        y = Math.floor(seed.quick() * GRID);
        //ensure intial block is in the edge of map
      } while (x !== 0 && x !== GRID - 1 && y !== 0 && y !== GRID - 1);
      return {x: x, y: y};
    }
    initial_block = getInitialBlock(GRID);
    function checkConditions(json_map, GRID) {
      var f, flag, g, n_mountains = 0;

      if (!json_map) {
        return false;
      }
      // set ~20% of the blocks with flags
      if (json_map.flag_list.length !== Math.round(GRID * GRID * 0.2)) {
        return false;
      }
      // limit n_mountains
      if (json_map.obstacle_list.length > 3) {
        for (g = 0; g < json_map.obstacle_list.length; g += 1) {
          if (json_map.obstacle_list[g].type === "mountain") {
            n_mountains += 1;
            if (n_mountains > 3) {
              return false;
            }
            json_map.obstacle_list[g].type = "box";
          }
        }
      }
      // at least one flag in the oposite side of drones initial position
      for (f = 0; f < json_map.flag_list.length; f += 1) {
        flag = json_map.flag_list[f];
        if ((flag.position.x * json_map.initial_position.x) < 0 ||
            (flag.position.y * json_map.initial_position.y) < 0) {
          return true;
        }
      }
      return false;
    }
    do {
      result_map = {
        "flag_list": [],
        "initial_position": null,
        "obstacle_list": [],
        "enemy_list": []
      };
      for (i = 0; i < GRID; i += 1) {
        for (j = 0; j < GRID; j += 1) {
          index = Math.floor(seed.quick() * BLOCK_TEMPLATE_LIST.length);
          x1 = block_size * i - max_width / 2;
          y1 = block_size * j - max_depth / 2;
          x2 = block_size * i + block_size - max_width / 2;
          y2 = block_size * j + block_size - max_depth / 2;
          if (initial_block.x === i && initial_block.y === j) {
            result_map.initial_position = {x: normalize(50, x1, x2),
                                           y: normalize(50, y1, y2),
                                           z: 15 };
          } else {
            block_result =
              fillTemplate(BLOCK_TEMPLATE_LIST[index], x1, y1, x2, y2);
            result_map.flag_list =
              result_map.flag_list.concat(block_result.flag_list);
            result_map.obstacle_list =
              result_map.obstacle_list.concat(block_result.obstacle_list);
            result_map.enemy_list =
              result_map.enemy_list.concat(block_result.enemy_list);
          }
        }
      }
    } while (!checkConditions(result_map, GRID));
    return result_map;
  };

  /*
  ** Generates a random map json
  */
  MapUtils.prototype.randomize = function (seed) {
    //TODO randomize start_ASML, map height, depth and width?
    var _this = this, flag_list, obstacle_list, enemy_list,
      geo_flag_info, geo_obstacle, geo_enemy,
      random_seed = new Math.seedrandom(seed),
      randomized_map = _this.randomizeByBlockTemplates(random_seed);
    obstacle_list = randomized_map.obstacle_list;
    enemy_list = randomized_map.enemy_list;
    flag_list = randomized_map.flag_list;
    _this.map_param.obstacle_list = [];
    _this.map_param.enemy_list = [];
    _this.map_param.flag_list = [];
    //convert all map elements positions to geo coordinates
    _this.map_info.initial_position = _this.convertToGeoCoordinates(
      randomized_map.initial_position.x,
      randomized_map.initial_position.y,
      randomized_map.initial_position.z
    );
    Object.assign(_this.map_info, _this.map_param);
    flag_list.forEach(function (flag_info, index) {
      geo_flag_info = {
        'id': flag_info.id,
        'score': flag_info.score,
        'weight': flag_info.weight,
        'position': _this.convertToGeoCoordinates(
          flag_info.position.x,
          flag_info.position.y,
          flag_info.position.z
        )
      };
      _this.map_info.flag_list.push(geo_flag_info);
    });
    obstacle_list.forEach(function (obstacle_info, index) {
      geo_obstacle = {position: null};
      Object.assign(geo_obstacle, obstacle_info);
      geo_obstacle.position = _this.convertToGeoCoordinates(
        obstacle_info.position.x,
        obstacle_info.position.y,
        obstacle_info.position.z
      );
      _this.map_info.obstacle_list.push(geo_obstacle);
    });
    enemy_list.forEach(function (enemy_info, index) {
      geo_enemy = {position: null};
      Object.assign(geo_enemy, enemy_info);
      geo_enemy.position = _this.convertToGeoCoordinates(
        enemy_info.position.x,
        enemy_info.position.y,
        enemy_info.position.z
      );
      _this.map_info.enemy_list.push(geo_enemy);
    });
    //return only base parameters
    randomized_map.min_lat = _this.map_info.min_lat;
    randomized_map.max_lat = _this.map_info.max_lat;
    randomized_map.min_lon = _this.map_info.min_lon;
    randomized_map.max_lon = _this.map_info.max_lon;
    randomized_map.height = _this.map_info.height;
    randomized_map.start_AMSL = _this.map_info.start_AMSL;
    randomized_map.flag_list = _this.map_info.flag_list;
    randomized_map.obstacle_list = _this.map_info.obstacle_list;
    randomized_map.enemy_list = _this.map_info.enemy_list;
    randomized_map.initial_position = _this.map_info.initial_position;
    return randomized_map;
  };

  return MapUtils;
}());

/******************************************************************************/
