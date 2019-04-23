/*jslint nomen: true, maxlen: 200, indent: 2*/
/*global rJS, console, window, document, RSVP*/

(function (window, rJS) {
  "use strict";

  function discoverDataSources(g, opt) {
    return g.request("discoverDataSources", undefined, opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (!response) {
          return;
        }
        var arr = [],
          i,
          row;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          arr.push({
            const: row["DataSourceInfo"] || undefined,
            title: row["DataSourceName"] || undefined,
            description: row["DataSourceDescription"] || undefined
          });
        }
        return arr;
      });
  }

  function discoverDBCatalogs(g, opt) {
    return g.request("discoverDBCatalogs", undefined, opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (!response) {
          return;
        }
        var arr = [],
          i,
          row;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          arr.push({
            const: row["CATALOG_NAME"] || undefined,
            title: row["CATALOG_NAME"] || undefined
          });
        }
        return arr;
      });
  }

  function discoverMDCubes(g, opt) {
    return g.request("discoverMDCubes", undefined, opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (!response) {
          return;
        }
        var arr = [],
          i,
          row;
        for (i = 0; i < response.length; i += 1) {
          row = response[i];
          arr.push({
            const: row["CUBE_NAME"] || undefined,
            title: row["CUBE_NAME"] || undefined
          });
        }
        return arr;
      });
  }

  function generateSchema(g, settings) {
    var schema = {
      "type": "object",
      "additionalProperties": false,
      "required": ["Cube"],
      "properties": {
        "DataSourceInfo": {"type": "string"},
        "Catalog": {"type": "string"},
        "Cube": {"type": "string"}
      }
    };
    if (!settings) {
      return new RSVP.Queue()
        .push(function () {
          return schema;
        });
    }
    if (!settings.hasOwnProperty('properties')) {
      settings.properties = {};
    }
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all([
          discoverDataSources(g, {
            urls: settings.urls,
            prop: {}
          }),
          discoverDBCatalogs(g, {
            urls: settings.urls,
            prop: {
              properties: {
                DataSourceInfo: settings.properties.DataSourceInfo
              }
            }
          }),
          discoverMDCubes(g, {
            urls: settings.urls,
            prop: {
              properties: {
                DataSourceInfo: settings.properties.DataSourceInfo,
                Catalog: settings.properties.Catalog
              }
            }
          })
        ]);
      })
      .push(function (arr) {
        if (arr[0] && arr[0].length !== 0) {
          schema.properties.DataSourceInfo = {
            title: " ",
            oneOf: arr[0]
          };
        }
        if (arr[1] && arr[1].length !== 0) {
          schema.properties.Catalog = {
            title: " ",
            oneOf: arr[1]
          };
        }
        if (arr[2] && arr[2].length !== 0) {
          schema.properties.Cube = {
            title: " ",
            oneOf: arr[2]
          };
        }
        return schema;
      });
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.xmla_connections = {};
    })
    .declareAcquiredMethod("request", "xmla_request")
    .declareAcquiredMethod("getLevels", "xmla_getLevels")
    .allowPublicAcquisition("notifyValid", function (arr, scope) {
    })
    .allowPublicAcquisition("notifyInvalid", function (arr, scope) {
    })
    .declareMethod("render", function (opt) {
      var gadget = this;
      return gadget.getDeclaredGadget("xmla_settings")
        .push(function (g) {
          return g.render(opt);
        });
    })
    .declareMethod("getContent", function (sub_path) {
      return this.getDeclaredGadget("xmla_settings")
        .push(function (g) {
          return g.getContent(sub_path);
        });
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition("notifyChange", function (arr, s) {
      var g = this,
        p = arr[0].path,
        scope = arr[0].scope,
        action = arr[0].action,
        url = arr[0].ref,
        connection_path,
        path;

      function rerender(sub_scope, settings_path) {
        var gadget_settings;
        return g.getDeclaredGadget("xmla_settings")
          .push(function (gadget) {
            gadget_settings = gadget;
            return gadget.getContent(settings_path);
          })
          .push(function (settings) {
            return generateSchema(g, settings);
          })
          .push(function (schema) {
            return gadget_settings.rerender({
              scope: sub_scope,
              path: '/properties',
              schema: schema,
              ignore_incorrect: true
            });
          })
          .push(function () {
            return g.notifyChange();
          });
      }

      if (action === "render") {
        if ("urn:jio:properties_from_xmla.connection.json" === url) {
          connection_path = p.split('/').slice(0, -2).join('/');
          g.props.xmla_connections[connection_path] = scope.split('_').slice(0, -1).join('_');
        }
        // action `render` fake change so do nothing
        return;
      }
      for (path in g.props.xmla_connections) {
        if (g.props.xmla_connections.hasOwnProperty(path)) {
          if (p === path && action === "add") {
            return rerender(scope, path);
          }
          s = g.props.xmla_connections[path];
          if (action === "delete") {
            if (s === scope) {
              delete g.props.xmla_connections[path];
            }
          } else {
            // check if receive message from gadget with scope == s or his sub_gadgets
            if (scope.startsWith(s)) {
              return rerender(s, path);
            }
          }
        }
      }
      return g.notifyChange();
    })
    .allowPublicAcquisition("resolveExternalReference", function (arr) {
      var g = this,
        url = arr[0],
        schema_path = arr[1],
        path = arr[2],
        connection_path = path.split('/').slice(0, -1).join('/');
      if ("urn:jio:properties_from_xmla.connection.json" === url) {
        return this.getContent(connection_path)
          .push(function (settings) {
            return generateSchema(g, settings);
          });
      }
      throw new Error("urn: '" + url + "' not supported");
    });

}(window, rJS));
