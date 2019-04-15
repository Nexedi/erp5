/*jslint nomen: true, maxlen: 200, indent: 2*/
/*global rJS, console, window, document, RSVP, Xmla*/

(function (window, rJS) {
  "use strict";


  function xmla_request(func, prop) {
    var xmla = new Xmla({async: true});
    prop = JSON.parse(JSON.stringify(prop));
    // return function () {
    return new RSVP.Queue()
      .push(function () {
        return new RSVP.Promise(function (resolve, reject) {
          prop.success = function (xmla, options, response) {
            resolve(response);
          };
          prop.error = function (xmla, options, response) {
            reject(response);
          };
          xmla[func](prop);
        });
      });
  }

  function xmla_request_retry(func, settings) {
    var queue,
      urls = settings.urls || [""],
      i;

    function make_request(url) {
      return function (error) {
        settings.prop.url = url;
        return xmla_request(func, settings.prop)
          .push(undefined, function (response) {
            // fix mondrian Internal and Sql errors
            if (response) {
              switch (response["code"]) {
              case "SOAP-ENV:Server.00HSBE02":
              case "SOAP-ENV:00UE001.Internal Error":
                // rarely server error, so try again
                return xmla_request(func, settings.prop);
              }
            }
            throw response;
          });
      };
    }

    queue = make_request(urls[0])();
    for (i = 1; i < urls.length; i += 1) {
      queue.push(undefined, make_request(urls[i]));
    }
    return queue;
  }

  function discoverDimensions(schema, used_dimensions, opt) {
    return xmla_request_retry("discoverMDDimensions", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          row;
        if (response && response.numRows > 0) {
          while (response.hasMoreRows()) {
            row = response.readAsObject();
            if (row["DIMENSION_TYPE"] !== 2) {
              if (used_dimensions.indexOf(row["DIMENSION_UNIQUE_NAME"]) < 0) {
                arr.push({
                  const: row["DIMENSION_UNIQUE_NAME"] || undefined,
                  title: row["DIMENSION_NAME"] || undefined
                });
              }
            }
            response.nextRow();
          }
        }
        if (arr.length !== 0) {
          schema.properties.dimension = {
            title: " ",
            oneOf: arr
          };
        }
      });
  }

  function  discoverHierarchies(schema, opt) {
    return xmla_request_retry("discoverMDHierarchies", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          row;
        if (response && response.numRows > 0) {
          while (response.hasMoreRows()) {
            row = response.readAsObject();
            arr.push({
              const: row["HIERARCHY_UNIQUE_NAME"] || undefined,
              title: row["HIERARCHY_NAME"] || undefined
            });
            response.nextRow();
          }
        }
        if (arr.length !== 0) {
          schema.properties.hierarchy = {
            title: " ",
            oneOf: arr
          };
        }
      });
  }

  function discoverLevels(schema, opt) {
    return xmla_request_retry("discoverMDLevels", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          row;
        if (response && response.numRows > 0) {
          while (response.hasMoreRows()) {
            row = response.readAsObject();
            arr.push({
              const: row["LEVEL_UNIQUE_NAME"] || undefined,
              title: row["LEVEL_NAME"] || undefined
            });
            response.nextRow();
          }
        }
        if (arr.length !== 0) {
          schema.properties.level = {
            title: " ",
            oneOf: arr
          };
        }
      });
  }

  rJS(window)
    .ready(function () {
      var g = this;
      console.log("xmla_client");
      g.props = {
        cache: {},
        connections: {}
      };
    })
    .declareMethod("render", function () {
      var g = this;
      return g.getRemoteSettings()
        .push(function (settings) {
          return g.setConnectionsSettings(settings);
        })
    })
    .declareAcquiredMethod("getRemoteSettings", "getRemoteSettings")
    .declareMethod("getConnectionSettings", function (name) {
      return this.props.connections[name];
    })
    .declareMethod("setConnectionsSettings", function (connections) {
      var key,
        new_state = {};
      for (key in connections) {
        if (connections.hasOwnProperty(key) && connections[key]) {
          new_state[key] = JSON.stringify(connections[key]);
        }
      }
      for (key in this.state) {
        if (this.state.hasOwnProperty(key) && !connections[key]) {
          new_state[key] = null;
        }
      }
      return this.changeState(new_state);
    })
    .onStateChange(function (m_dict) {
      var g = this,
        key;
      for (key in m_dict) {
        if (m_dict.hasOwnProperty(key)) {
          delete g.props.cache[key];
          delete g.props.connections[key];
          if (m_dict[key] !== null) {
            g.props.cache[key] = {
              members: {},
              levels: {}
            };
            g.props.connections[key] = JSON.parse(m_dict[key]);
          }
        }
      }
    })
    .declareMethod("request", function (function_name, settings, connection_name) {
      var queue;
      if (connection_name) {
        queue = this.getConnectionSettings(connection_name);
      } else {
        queue = RSVP.Queue();
      }
      return queue
        .push(function (connection_settings) {
          if (!settings) {
            settings = {};
          }
          if (connection_settings) {
            settings.urls = connection_settings.urls;
            settings.prop.restrictions.CATALOG_NAME = connection_settings.properties.Catalog;
            settings.prop.restrictions.CUBE_NAME = connection_settings.properties.Cube;
          }
          return xmla_request_retry(function_name, settings);
        })
        .push(undefined, function (error) {
          console.error(error);
        });
    })
    .declareMethod("getMembersOnLevel", function (connection_name, level_uname) {
      var g = this,
        cache = g.props.cache[connection_name];
      if (cache.levels.hasOwnProperty(level_uname)) {
        return cache.levels[level_uname];
      }
      return g.request("discoverMDMembers", {
        prop: {
          restrictions: {
            LEVEL_UNIQUE_NAME: level_uname
          }
        }
      }, connection_name)
        .push(function (r) {
          var uname,
            member,
            i,
            level = [];
          while (r.hasMoreRows()) {
            uname = r["getMemberUniqueName"]();
            if (level_uname !== r["getLevelUniqueName"]()) {
              throw "xmla server fail";
            }
            member = {
              uname: uname,
              level: level_uname,
              h: r["getHierarchyUniqueName"](),
              caption: r["getMemberCaption"](),
              type: r["getMemberType"]()
            };
            r.nextRow();
            cache.members[uname] = member;
            level.push(member);
          }

          function compare(a, b) {
            if (a.uname < b.uname) {
              return -1;
            }
            if (a.uname > b.uname) {
              return 1;
            }
            return 0;
          }

          level.sort(compare);
          for (i = 0; i < level.length; i += 1) {
            level[i].level_index = i;
          }
          cache.levels[level_uname] = level;
          return level;
        });
    }, {mutex: 'getMembersOnLevel'})
    .declareMethod("getMember", function (connection_name, memeber_uname) {
      var g = this,
        cache = g.props.cache[connection_name];
      if (cache.members.hasOwnProperty(memeber_uname)) {
        return cache.members[memeber_uname];
      }
      return g.request("discoverMDMembers", {
        prop: {
          restrictions: {
            MEMBER_UNIQUE_NAME: memeber_uname,
            TREE_OP: 0x08 // MDTREEOP_SELF
            // TREE_OP: 0x02 // MDTREEOP_SIBLINGS
          }
        }
      }, connection_name)
        .push(function (r) {
          if (r.length === 0) {
            return;
          }
          return g.getMembersOnLevel(connection_name, r["getLevelUniqueName"]());
        })
        .push(function (level) {
          if (!level) {
            return;
          }
          return cache.members[memeber_uname];
        });
    }, {mutex: 'getMember'})
    .declareMethod("getMemberWithOffset", function (connection_name, memeber_uname, offset) {
      var g = this,
        member;
      return g.getMember(connection_name, memeber_uname)
        .push(function (m) {
          member = m;
          if (member && (member.level_index >= 0)) {
            return g.getMembersOnLevel(connection_name, member.level);
          }
        })
        .push(function (level) {
          if (level) {
            return level[member.level_index + offset];
          }
        });
    });


}(window, rJS));

