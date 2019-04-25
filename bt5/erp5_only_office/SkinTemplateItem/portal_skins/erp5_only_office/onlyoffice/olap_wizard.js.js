/*jslint nomen: true, maxlen: 200, indent: 2*/
/*global rJS, console, window, document, RSVP*/

(function (window, rJS) {
  "use strict";

  function get_used_hierarchies(g) {
    return g.getContent()
      .push(function (v) {
        var hierarchies = [],
          key,
          hierarchy;
        if (v) {
          if (v.columns) {
            for (key in v.columns) {
              if (v.columns.hasOwnProperty(key)) {
                hierarchy = v.columns[key].hierarchy;
                if (hierarchy) {
                  hierarchies.push(hierarchy);
                }
              }
            }
          }
          if (v.rows) {
            for (key in v.rows) {
              if (v.rows.hasOwnProperty(key)) {
                hierarchy = v.rows[key].hierarchy;
                if (hierarchy) {
                  hierarchies.push(hierarchy);
                }
              }
            }
          }
        }
        return hierarchies;
      });
  }
  function discoverDimensions(g, connection_name, used_hierarchies) {
    return g.getHierarchies(connection_name)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var dimensions = {},
          i,
          row,
          uname,
          tasks = [];
        if (response) {
          for (i = 0; i < response.length; i += 1) {
            row = response[i];
            uname = row.DIMENSION_UNIQUE_NAME;
            if (!dimensions.hasOwnProperty(uname) &&
                used_hierarchies.indexOf(row.HIERARCHY_UNIQUE_NAME) < 0 &&
                row.DIMENSION_TYPE !== 2 // !measure
            ) {
              dimensions[uname] = true;
            }
          }
        }
        for (i in dimensions) {
          if (dimensions.hasOwnProperty(i)) {
            tasks.push(g.getDimension(connection_name, i))
          }
        }
        return RSVP.all(tasks);
      })
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          i,
          row;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          arr.push({
            const: row.DIMENSION_UNIQUE_NAME || undefined,
            title: row.DIMENSION_NAME || undefined
          });
        }
        return arr;
      });
  }

  function discoverHierarchies(g, connection_name, used_hierarchies, opt) {
    return g.request("discoverMDHierarchies", connection_name, opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          i,
          row,
          uname;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          uname = row.HIERARCHY_UNIQUE_NAME;
          if (used_hierarchies.indexOf(uname) < 0) {
            arr.push({
              const: uname || undefined,
              title: row.HIERARCHY_NAME || undefined
            });
          }
        }
        return arr;
      });
  }

  function discoverLevels(g, connection_name, opt) {
    return g.getLevels(connection_name, opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        var arr = [],
          i,
          row;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          if (
            row["LEVEL_CARDINALITY"] < 600 &&
            row["LEVEL_TYPE"] !== 1 // exclude all level type
          ) {
            arr.push({
              const: row["LEVEL_UNIQUE_NAME"] || undefined,
              title: row["LEVEL_NAME"] || undefined
            });
          }
        }
        return arr;
      });
  }

  function generateChoiceSchema(g, connection_name, used_hierarchies, choice_settings) {
    var schema = {
      "type": "object",
      "additionalProperties": false,
      "properties": {}
    },
      current_hierarchy;
    if (!connection_name) {
      return new RSVP.Queue()
        .push(function () {
          return schema;
        });
    }
    if (!choice_settings) {
      choice_settings = {};
    }

    current_hierarchy = choice_settings.hierarchy;
    if (current_hierarchy) {
      used_hierarchies = used_hierarchies
        .filter(function (h) {
          return h !== current_hierarchy;
        });
    }

    return new RSVP.Queue()
      .push(function () {
        var tasks = [discoverDimensions(g, connection_name, used_hierarchies)];

        if (choice_settings.dimension) {
          tasks.push(
            discoverHierarchies(g, connection_name,
              used_hierarchies,
              {prop: {
                restrictions: {
                  DIMENSION_UNIQUE_NAME: choice_settings.dimension
                }
              }})
          );
        }
        if (choice_settings.hierarchy) {
          tasks.push(discoverLevels(g, connection_name, {
            DIMENSION_UNIQUE_NAME: choice_settings.dimension,
            HIERARCHY_UNIQUE_NAME: choice_settings.hierarchy
          }));
        }

        return RSVP.all(tasks);
      })
      .push(function (arr) {
        if (arr[0].length !== 0) {
          schema.properties.dimension = {
            title: " ",
            oneOf: arr[0]
          };
        }
        if (arr[1] && arr[1].length !== 0) {
          schema.properties.hierarchy = {
            title: " ",
            oneOf: arr[1]
          };
        }
        if (arr[2] && arr[2].length !== 0) {
          schema.properties.level = {
            title: " ",
            oneOf: arr[2]
          };
        }

        return schema;
      })
      .push(undefined, function () {
        return schema;
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.choices = [];
      return g.render({
        schema_url: new URL("olap_wizard.json", window.location).toString(),
        value: {}
      });
    })
    .declareAcquiredMethod("getRemoteSettings", "getRemoteSettings")
    .declareAcquiredMethod("request", "xmla_request")
    .declareAcquiredMethod("getDimension", "xmla_getDimension")
    .declareAcquiredMethod("getHierarchies", "xmla_getHierarchies")
    .declareAcquiredMethod("getLevels", "xmla_getLevels")
    .allowPublicAcquisition("notifyValid", function (arr, scope) {
    })
    .allowPublicAcquisition("notifyInvalid", function (arr, scope) {
    })
    .declareMethod("rerender", function () {
      return this.getDeclaredGadget("olap_wizard")
        .push(function (gadget) {
          return gadget.rerender();
        })
        .push(undefined, function (err) {
          console.error(err);
        });
    })
    .declareMethod("render", function (opt) {
      if (!opt) {
        opt = {};
      }
      return this.getDeclaredGadget("olap_wizard")
        .push(function (gadget) {
          return gadget.render(opt);
        });
    })
    .declareMethod("getContent", function (path) {
      return this.getDeclaredGadget("olap_wizard")
        .push(function (g) {
          return g.getContent(path);
        });
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition("notifyChange", function (arr, s) {
      var g = this,
        scope = arr[0].scope,
        relPath = arr[0].rel_path,
        action = arr[0].action,
        used_hierarchy,
        url = arr[0].ref,
        allRerender,
        y;

      function rerender(sub_scope) {
        var queue,
          gadget_settings;
        if (!used_hierarchy) {
          queue = get_used_hierarchies(g)
            .push(function (v) {
              used_hierarchy = v;
            });
        } else {
          queue = RSVP.Queue();
        }

        function rerender_once(connection_name, sub_gadget) {
          return sub_gadget.getContent()
            .push(function (content) {
              return generateChoiceSchema(g, connection_name, used_hierarchy, content);
            })
            .push(function (schema) {
              return gadget_settings.rerender({
                scope: sub_scope,
                schema: schema,
                ignore_incorrect: true
              });
            });
        }

        return queue
          .push(function () {
            return g.getDeclaredGadget("olap_wizard");
          })
          .push(function (gadget) {
            gadget_settings = gadget;
            return RSVP.all([
              gadget.getContent("/connection_name"),
              gadget.getSubGadget(sub_scope)
            ]);
          })
          .push(function (arr) {
            var connection_name = arr[0],
              sub_gadget = arr[1];
            return rerender_once(connection_name, sub_gadget)
              .push(function (changed) {
                if (changed && changed.length > 0) {
                  if (changed.indexOf('/hierarchy') >= 0) {
                    return allRerender();
                  }
                  return rerender_once(connection_name, sub_gadget);
                }
              })
              .push(function (changed) {
                if (changed && changed.length > 0) {
                  return rerender_once(connection_name, sub_gadget);
                }
              });
          });
      }

      allRerender = function () {
        return get_used_hierarchies(g)
          .push(function (v) {
            used_hierarchy = v;
            return RSVP.all(g.props.choices.map(function (q) {
              return rerender(q);
            }));
          })
          .push(function () {
            return g.notifyChange();
          });
      };

      if ("urn:jio:remote_connections.json" === url) {
        return allRerender();
      }
      if (action === "render") {
        if ("urn:jio:choice.json" === url) {
          g.props.choices.push(scope);
        }
        // action `render` fake change so do nothing
        return;
      }
      for (y = 0; y < g.props.choices.length; y += 1) {
        s = g.props.choices[y];
        if (scope.startsWith(s)) {
          if (action === "delete") {
            g.props.choices.splice(y, 1);
            return allRerender();
          }
          if (relPath === "/hierarchy") {
            return allRerender();
          }
          return rerender(s)
            .push(function () {
              return g.notifyChange();
            });
        }
      }
      return g.notifyChange();
    })
    .allowPublicAcquisition("resolveExternalReference", function (arr) {
      var g = this,
        url = arr[0],
        schema_path = arr[1],
        path = arr[2];
      if ("urn:jio:remote_connections.json" === url) {
        return new RSVP.Queue()
          .push(function () {
            return g.getRemoteSettings();
          })
          .push(function (connections) {
            var key,
              schema = {
                enum: []
              };
            for (key in connections) {
              if (connections.hasOwnProperty(key)) {
                schema.enum.push(key);
              }
            }
            return schema;
          });
      }
      if ("urn:jio:choice.json" === url) {
        return new RSVP.Queue()
          .push(function () {
            return RSVP.all([
              g.getContent("/connection_name"),
              get_used_hierarchies(g),
              g.getContent(path)
            ]);
          })
          .push(function (arr) {
            var choice_settings;

            if (path !== "/columns/" && path !== "/rows/") {
              choice_settings = arr[2];
            }
            return generateChoiceSchema(g, arr[0], arr[1], choice_settings);
          });
      }
      throw new Error("urn: '" + url + "' not supported");
    });

}(window, rJS));