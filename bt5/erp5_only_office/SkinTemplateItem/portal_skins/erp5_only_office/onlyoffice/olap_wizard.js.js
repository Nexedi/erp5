/*jslint nomen: true, maxlen: 200, indent: 2*/
/*global rJS, console, window, document, RSVP, Xmla*/

(function (window, rJS) {
  "use strict";

  function getCurrentConnectionSettings(g, gadget) {
    var connections;
    return RSVP.Queue()
      .push(function () {
        return g.getRemoteSettings();
      })
      .push(function (c) {
        connections = c;
        return gadget.getContent("/connection_name");
      })
      .push(function (connection_name) {
        return connections[connection_name];
      })
      .push(undefined, function (err) {
        console.error(err);
      });
  }

  function get_used_dimensions(g) {
    return g.getContent()
      .push(function (v) {
        var dimensions = [],
          key,
          dimension;
        if (v) {
          if (v.columns) {
            for (key in v.columns) {
              if (v.columns.hasOwnProperty(key)) {
                dimension = v.columns[key].dimension;
                if (dimension) {
                  dimensions.push(dimension);
                }
              }
            }
          }
          if (v.rows) {
            for (key in v.rows) {
              if (v.rows.hasOwnProperty(key)) {
                dimension = v.rows[key].dimension;
                if (dimension) {
                  dimensions.push(dimension);
                }
              }
            }
          }
        }
        return dimensions;
      });
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

  function print_content(gadget) {
    return gadget.getDeclaredGadget("olap_wizard")
      .push(function (g) {
        return g.getContent();
      })
      .push(function (v) {
        console.log(JSON.stringify(v));
      });
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

  function generateChoiceSchema(connection_settings, used_dimensions, choice_settings) {
    var schema = {
      "type": "object",
      "additionalProperties": false,
      "properties": {}
    },
      current_dimension;
    if (!connection_settings) {
      return new RSVP.Queue()
        .push(function () {
          return schema;
        });
    }
    if (!connection_settings.hasOwnProperty('properties')) {
      connection_settings.properties = {};
    }
    if (!choice_settings) {
      choice_settings = {};
    }
    current_dimension = choice_settings.dimension;
    if (current_dimension) {
      used_dimensions = used_dimensions
        .filter(function (d) {
          return d !== current_dimension;
        });
    }

    return new RSVP.Queue()
      .push(function () {
        var tasks = [discoverDimensions(schema, used_dimensions, {
          urls: connection_settings.urls,
          prop: {
            restrictions: {
              CATALOG_NAME: connection_settings.properties.Catalog,
              CUBE_NAME: connection_settings.properties.Cube
            }
          }
        })];

        if (choice_settings.dimension) {
          tasks.push(
            discoverHierarchies(schema, {
              urls: connection_settings.urls,
              prop: {
                restrictions: {
                  CATALOG_NAME: connection_settings.properties.Catalog,
                  CUBE_NAME: connection_settings.properties.Cube,
                  DIMENSION_UNIQUE_NAME: choice_settings.dimension
                }
              }
            })
          );
        }
        if (choice_settings.hierarchy) {
          tasks.push(discoverLevels(schema, {
            urls: connection_settings.urls,
            prop: {
              restrictions: {
                CATALOG_NAME: connection_settings.properties.Catalog,
                CUBE_NAME: connection_settings.properties.Cube,
                DIMENSION_UNIQUE_NAME: choice_settings.dimension,
                HIERARCHY_UNIQUE_NAME: choice_settings.hierarchy
              }
            }
          }));
        }

        return RSVP.all(tasks);
      })
      .push(function () {
        return schema;
      });
  }

  function decodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~1/g, '/').replace(/~0/g, '~');
  }

  function convertOnMultiLevel(d, key, value) {
    var ii,
      kk,
      prev_value,
      key_list = key.split("/");
    for (ii = 1; ii < key_list.length; ii += 1) {
      kk = decodeJsonPointer(key_list[ii]);
      if (ii === key_list.length - 1) {
        if (value !== undefined) {
          prev_value = d[kk];
          d[kk] = value[0];
          return prev_value;
        }
        return d[kk];
      }
      if (!d.hasOwnProperty(kk)) {
        if (value !== undefined) {
          d[kk] = {};
        } else {
          return;
        }
      }
      d = d[kk];
    }
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
    .allowPublicAcquisition("notifyValid", function (arr, scope) {
    })
    .allowPublicAcquisition("notifyInvalid", function (arr, scope) {
    })
    .declareMethod("rerender", function () {
      return this.getDeclaredGadget("olap_wizard")
        .push(function (gadget) {
          return gadget.rerender();
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
        used_diemensions,
        url = arr[0].ref,
        allRerender,
        y;

      function rerender(sub_scope) {
        var queue,
          gadget_settings;
        if (!used_diemensions) {
          queue = get_used_dimensions(g)
            .push(function (v) {
              used_diemensions = v;
            });
        } else {
          queue = RSVP.Queue();
        }

        function rerender_once(connection_settings, sub_gadget) {
          return sub_gadget.getContent()
            .push(function (content) {
              console.log(content);
              return generateChoiceSchema(connection_settings, used_diemensions, content);
            })
            .push(function (schema) {
              return gadget_settings.rerender({
                scope: sub_scope,
                schema: schema,
                ignore_incorrect: true
              });
            });
        }

        queue
          .push(function () {
            return g.getDeclaredGadget("olap_wizard");
          })
          .push(function (gadget) {
            gadget_settings = gadget;
            return RSVP.all([
              getCurrentConnectionSettings(g, gadget),
              gadget.getSubGadget(sub_scope)
            ]);
          })
          .push(function (arr) {
            var connection_settings = arr[0],
              sub_gadget = arr[1];
            return rerender_once(connection_settings, sub_gadget)
              .push(function (changed) {
                if (changed.length > 0) {
                  if (changed.indexOf('/dimension') >= 0) {
                    return allRerender();
                  }
                  return rerender_once(connection_settings, sub_gadget);
                }
              })
              .push(function (changed) {
                if (changed.length > 0) {
                  return rerender_once(connection_settings, sub_gadget);
                }
              });
          })
          .push(function () {
            // return g.notifyChange();
            return print_content(g);
          });
      }

      allRerender = function () {
        return get_used_dimensions(g)
          .push(function (v) {
            used_diemensions = v;
            return RSVP.all(g.props.choices.map(function (q) {
              return rerender(q);
            }));
          })
          .push(function () {
            return [];
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
          if (relPath === "/dimension") {
            return allRerender();
          }
          return rerender(s);
        }
      }
      // return g.notifyChange();
      return print_content(g);
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
              g.getRemoteSettings(),
              g.getContent("/connection_name"),
              g.getContent(path),
              get_used_dimensions(g)
            ]);
          })
          .push(function (arr) {
            var connection_settings,
              choice_settings;
            connection_settings = arr[0][arr[1]];
            if (path !== "/columns/" && path !== "/rows/") {
              choice_settings = arr[2];
            }
            return generateChoiceSchema(connection_settings, arr[3], choice_settings);
          });
      }
      throw new Error("urn: '" + url + "' not supported");
    });

}(window, rJS));