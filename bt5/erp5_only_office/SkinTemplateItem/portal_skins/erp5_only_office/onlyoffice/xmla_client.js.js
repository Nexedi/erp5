/*jslint nomen: true, maxlen: 200, indent: 2*/
/*global rJS, console, window, document, RSVP, Xmla*/

(function (window, rJS) {
  "use strict";


  function getFromCache(cache, key) {
    if (cache[key].hasOwnProperty("push") &&
        typeof cache[key].push === "function") {
      return cache[key]
        .push(function () {
          return cache[key];
        });
    }
    return cache[key];
  }

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

  function request(g, function_name, settings, connection_name) {
    var queue;
    if (connection_name) {
      queue = g.getConnectionSettings(connection_name);
    } else {
      queue = RSVP.Queue();
    }
    return queue
      .push(function (connection_settings) {
        if (!settings) {
          settings = {};
        }
        if (!settings.prop) {
          settings.prop = {};
        }
        if (!settings.prop.restrictions) {
          settings.prop.restrictions = {};
        }
        if (connection_settings) {
          settings.urls = connection_settings.urls;
          settings.prop.restrictions.CATALOG_NAME = connection_settings.properties.Catalog;
          settings.prop.restrictions.CUBE_NAME = connection_settings.properties.Cube;
        }
        return xmla_request_retry(function_name, settings);
      });
  }

  function levelDiscovery(g, connection_name, row) {
    var level_uname = row["LEVEL_UNIQUE_NAME"],
      cache = g.props.cache[connection_name],
      queue,
      LEVEL_CARDINALITY = row.LEVEL_CARDINALITY;
    if (LEVEL_CARDINALITY < 0) {
      // XXX LEVEL_CARDINALITY broken in saiku xmla
      queue = g.getMembersOnLevel(connection_name, level_uname);
    } else {
      queue = RSVP.Queue();
    }
    queue
      .push(function (members) {
        var level;
        if (LEVEL_CARDINALITY < 0 && members) {
          LEVEL_CARDINALITY = members.length;
        }
        level = {
          LEVEL_UNIQUE_NAME: row.LEVEL_UNIQUE_NAME,
          LEVEL_TYPE: row.LEVEL_TYPE,
          LEVEL_NAME: row.LEVEL_NAME || undefined,
          LEVEL_CARDINALITY: LEVEL_CARDINALITY,
        };
        cache.levels[level_uname] = level;
        return level;
      });
    return queue;
  }

  function row2member(row) {
    return {
      uname: row.getMemberUniqueName(),
      level: row.getLevelUniqueName(),
      h: row.getHierarchyUniqueName(),
      caption: row.getMemberCaption(),
      type: row.getMemberType()
    };
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
              levels: {},
              membersOnLevel: {}
            };
            g.props.connections[key] = JSON.parse(m_dict[key]);
          }
        }
      }
    })
    .declareMethod("request", function (function_name, connection_name, settings) {
      return request(this, function_name, settings, connection_name)
        .push(function (response) {
          var ret = [];
          while (response.hasMoreRows()) {
            ret.push(response.readAsObject());
            response.nextRow();
          }
          return ret;
        })
        .push(undefined, function (error) {
          console.error(error);
        });
    })
    .declareMethod("getLevel", function (connection_name, level_uname) {
      var g = this,
        cache = g.props.cache[connection_name],
        queue;
      if (cache.levels.hasOwnProperty(level_uname)) {
        return getFromCache(cache.levels, level_uname);
      }
      queue = g.getLevels(connection_name, {
        LEVEL_UNIQUE_NAME: level_uname
      })
        .push(function () {
          return cache.levels[level_uname];
        })
        .push(undefined, function (err) {
          delete cache.levels[level_uname];
          console.error(err);
        });
      cache.levels[level_uname] = queue;
      return queue;
    })
    .declareMethod("getLevels", function (connection_name, restrictions) {
      var g = this,
        cache = g.props.cache[connection_name];
      return request(g, "discoverMDLevels", {
        prop: {
          restrictions: restrictions
        }
      }, connection_name)
        .push(function (response) {
          var ret = [],
            row,
            level,
            level_uname;
          if (response && response.numRows > 0) {
            while (response.hasMoreRows()) {
              row = response.readAsObject();
              level_uname =  row["LEVEL_UNIQUE_NAME"];
              if (cache.levels.hasOwnProperty(level_uname)) {
                if (cache.levels[level_uname].hasOwnProperty("LEVEL_UNIQUE_NAME")) {
                  level = cache.levels[level_uname];
                } else {
                  level = levelDiscovery(g, connection_name, row);
                }
              } else {
                level = levelDiscovery(g, connection_name, row);
                cache.levels[level_uname] = level;
              }
              ret.push(level);
              response.nextRow();
            }
          }
          return RSVP.all(ret);
        })
        .push(undefined, function (err) {
          console.error(err);
        });
    })
    .declareMethod("getMembersOnLevel", function (connection_name, level_uname) {
      var g = this,
        cache = g.props.cache[connection_name],
        queue;
      if (cache.membersOnLevel.hasOwnProperty(level_uname)) {
        return getFromCache(cache.membersOnLevel, level_uname);
      }
      queue = request(g,"discoverMDMembers", {
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
            members = [];
          while (r.hasMoreRows()) {
            uname = r["getMemberUniqueName"]();
            if (level_uname !== r["getLevelUniqueName"]()) {
              throw "xmla server fail";
            }
            member = row2member(r);
            r.nextRow();
            cache.members[uname] = member;
            members.push(member);
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

          members.sort(compare);
          for (i = 0; i < members.length; i += 1) {
            members[i].level_index = i;
          }
          cache.membersOnLevel[level_uname] = members;
          return members;
        })
        .push(undefined, function (err) {
          delete cache.membersOnLevel[level_uname];
          console.error(err);
        });
      cache.membersOnLevel[level_uname] = queue;
      return queue;
    })
    .declareMethod("getMember", function (connection_name, memeber_uname) {
      var g = this,
        cache = g.props.cache[connection_name],
        queue;
      if (cache.members.hasOwnProperty(memeber_uname)) {
        return getFromCache(cache.members, memeber_uname);
      }
      queue = request(g, "discoverMDMembers", {
        prop: {
          restrictions: {
            MEMBER_UNIQUE_NAME: memeber_uname,
            TREE_OP: 0x08 // MDTREEOP_SELF
            // TREE_OP: 0x02 // MDTREEOP_SIBLINGS
          }
        }
      }, connection_name)
        .push(function (r) {
          if (r.rowCount() === 0) {
            delete cache.members[memeber_uname];
            return;
          }
          var member = row2member(r);
          cache.members[memeber_uname] = member;
          return member;
        })
        .push(undefined, function (err) {
          delete cache.members[memeber_uname];
          console.error(err);
          // throw err;
        });
      cache.members[memeber_uname] = queue;
      return queue;
    })
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

