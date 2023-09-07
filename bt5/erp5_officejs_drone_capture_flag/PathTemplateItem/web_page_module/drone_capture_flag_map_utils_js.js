/******************************* MAP UTILS ************************************/

var MapUtils = /** @class */ (function () {
  "use strict";

  var FLAG_EPSILON = 15, R = 6371e3;

  //** CONSTRUCTOR
  function MapUtils(map_param) {
    var _this = this, max_width = _this.latLonDistance(
      [map_param.min_lat, map_param.min_lon],
      [map_param.min_lat, map_param.max_lon]),
      max_depth = _this.latLonDistance(
        [map_param.min_lat, map_param.min_lon],
        [map_param.max_lat, map_param.min_lon]),
      map_size = Math.ceil(Math.max(max_width, max_depth));
    _this.map_param = {};
    _this.map_param.height = map_param.height;
    _this.map_param.start_AMSL = map_param.start_AMSL;
    _this.map_param.min_lat = map_param.min_lat;
    _this.map_param.max_lat = map_param.max_lat;
    _this.map_param.min_lon = map_param.min_lon;
    _this.map_param.max_lon = map_param.max_lon;
    _this.map_param.depth = map_size;
    _this.map_param.width = map_size;
    _this.map_param.map_size = map_size;
    _this.map_info = {
      "depth": _this.map_param.depth,
      "width": _this.map_param.width,
      "flag_distance_epsilon": map_param.flag_distance_epsilon || FLAG_EPSILON
    };
    _this.map_info.map_size = _this.map_param.map_size;
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
    return (this.map_info.map_size / 360.0) * (180 + lon);
  };
  MapUtils.prototype.latitudeToY = function (lat) {
    return (this.map_info.map_size / 180.0) * (90 - lat);
  };
  MapUtils.prototype.convertToLocalCoordinates =
    function (latitude, longitude, altitude) {
      var map_info = this.map_info,
        x = this.longitudToX(longitude),
        y = this.latitudeToY(latitude);
      return {
        x: ((x - map_info.min_x) / (map_info.max_x - map_info.min_x)) *
          1000 - map_info.width / 2,
        y: ((y - map_info.min_y) / (map_info.max_y - map_info.min_y)) *
          1000 - map_info.depth / 2,
        z: altitude
      };
    };
  MapUtils.prototype.convertToGeoCoordinates = function (x, y, z) {
    var lon = x + this.map_info.width / 2,
      lat = y + this.map_info.depth / 2;
    lon = lon / 1000;
    lon = lon * (this.map_info.max_x - this.map_info.min_x) +
      this.map_info.min_x;
    lon = lon / (this.map_info.map_size / 360.0) - 180;
    lat = lat / 1000;
    lat = lat * (this.map_info.max_y - this.map_info.min_y) +
      this.map_info.min_y;
    lat = 90 - lat / (this.map_info.map_size / 180.0);
    return {
      x: lat,
      y: lon,
      z: z
    };
  };

  /*
  ** Randomizes all map elements: starting point, enemies, flags, obstacles
  */
  MapUtils.prototype.randomize = function (seed) {
    //TODO randomize start_ASML, map height, depth and width?
    var _this = this, randomized_map = {};
    function randomIntFromInterval(min, max, random_seed) {
      return Math.floor(random_seed.quick() * (max - min + 1) + min);
    }
    function randomPosition(random_seed, map_size) {
      var sign_x = random_seed.quick() < 0.5 ? -1 : 1,
        sign_y = random_seed.quick() < 0.5 ? -1 : 1,
        pos_x = sign_x * random_seed.quick() * map_size / 2,
        pos_y = sign_y * random_seed.quick() * map_size / 2;
      return [pos_x, pos_y];
    }
    var random_seed = new Math.seedrandom(seed), i,
      n_enemies = randomIntFromInterval(5, 10, random_seed),
      n_flags = randomIntFromInterval(5, 10, random_seed), //TODO change range
      n_obstacles = randomIntFromInterval(5, 15, random_seed),
      flag_list = [], obstacle_list = [], enemy_list = [], random_position,
      obstacles_types = ["box", "cylinder"], type,
      obstacle_limit = [_this.map_param.map_size / 6, _this.map_param.map_size / 100,
                        _this.map_param.map_size / 6, 30],
      geo_flag_info, geo_obstacle, geo_enemy, coordinates;
    //enemies
    for (i = 0; i < n_enemies; i += 1) {
      random_position = randomPosition(random_seed, _this.map_param.map_size);
      enemy_list.push({
        "type": "EnemyDroneAPI",
        "position": {
          "x": random_position[0],
          "y": random_position[1],
          "z": 15 //TODO random z? yes
        }
      });
    }
    //flags
    for (i = 0; i < n_flags; i += 1) {
      //avoid flags near the limits
      random_position = randomPosition(random_seed, _this.map_param.map_size * 0.75);
      flag_list.push({
        "position": {
          "x": random_position[0],
          "y": random_position[1],
          "z": 10
        },
        "score": randomIntFromInterval(1, 5, random_seed),
        "weight": randomIntFromInterval(1, 5, random_seed)
      });
    }
    function checkDistance(position, position_list) {
      function distance(a, b) {
        return Math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2);
      }
      var el;
      for (el = 0; el < position_list.length; el += 1) {
        if (distance(position, position_list[el].position) < _this.map_param.map_size / 6) {
          return true;
        }
      }
      return false;
    }
    //obstacles
    for (i = 0; i < n_obstacles; i += 1) {
      random_position = randomPosition(random_seed, _this.map_param.map_size);
      if (checkDistance({ 'x': random_position[0],
                          'y': random_position[1]}, flag_list)) {
        i -= 1;
      } else {
        type = randomIntFromInterval(0, 2, random_seed);
        obstacle_list.push({
          "type": obstacles_types[type],
          "position": {
            "x": random_position[0],
            "y": random_position[1],
            "z": 15 //TODO random z?
          },
          "scale": {
            "x": randomIntFromInterval(20, obstacle_limit[type], random_seed),
            "y": randomIntFromInterval(20, obstacle_limit[type], random_seed),
            "z": randomIntFromInterval(5, obstacle_limit[3], random_seed)
          },
          "rotation": {
            "x": 0,
            "y": 0,
            "z": 0
          }
        });
      }
    }
    _this.map_param.obstacle_list = [];
    _this.map_param.enemy_list = [];
    _this.map_param.flag_list = [];
    //TODO make it random
    _this.map_info.initial_position = _this.convertToGeoCoordinates(
      0, _this.map_param.map_size / 2 * -0.75, 15
    );
    //convert all map elements positions to geo coordinates
    Object.assign(_this.map_info, _this.map_param);
    flag_list.forEach(function (flag_info, index) {
      coordinates = _this.convertToGeoCoordinates(
        flag_info.position.x,
        flag_info.position.y,
        flag_info.position.z
      );
      geo_flag_info = {
        'id': flag_info.id,
        'score': flag_info.score,
        'weight': flag_info.weight,
        'position': {
          'x': coordinates.x,
          'y': coordinates.y,
          'z': coordinates.z
        }
      };
      _this.map_info.flag_list.push(geo_flag_info);
    });
    obstacle_list.forEach(function (obstacle_info, index) {
      geo_obstacle = {};
      Object.assign(geo_obstacle, obstacle_info);
      geo_obstacle.position = _this.convertToGeoCoordinates(
        obstacle_info.position.x,
        obstacle_info.position.y,
        obstacle_info.position.z
      );
      _this.map_info.obstacle_list.push(geo_obstacle);
    });
    enemy_list.forEach(function (enemy_info, index) {
      geo_enemy = {};
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
