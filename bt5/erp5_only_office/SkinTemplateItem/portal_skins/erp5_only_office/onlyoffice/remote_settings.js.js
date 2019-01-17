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
      urls = settings.urls,
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
    for (i = 1; i < settings.urls.length; i += 1) {
      queue.push(undefined, make_request(urls[i]));
    }
    return queue;
  }

  function discoverDataSources(schema, opt) {
    return xmla_request_retry("discoverDataSources", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (response && response.numRows > 0) {
          schema.properties.DataSourceInfo = {
            title: " ",
            oneOf: []
          };
          var arr = schema.properties.DataSourceInfo.oneOf;
          while (response.hasMoreRows()) {
            arr.push({
              const: response["getDataSourceInfo"]() || undefined,
              title: response["getDataSourceName"]() || undefined,
              description: response["getDataSourceDescription"]() || undefined
            });
            response.nextRow();
          }
        }
      });
  }

  function discoverDBCatalogs(schema, opt) {
    return xmla_request_retry("discoverDBCatalogs", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (response && response.numRows > 0) {
          schema.properties.Catalog = {
            title: " ",
            oneOf: []
          };
          var arr = schema.properties.Catalog.oneOf;
          while (response.hasMoreRows()) {
            arr.push({
              const: response["getCatalogName"]() || undefined,
              title: response["getCatalogName"]() || undefined
            });
            response.nextRow();
          }
        }
      });
  }

  function discoverMDCubes(schema, opt) {
    return xmla_request_retry("discoverMDCubes", opt)
      .push(undefined, function (error) {
        console.log(error);
      })
      .push(function (response) {
        if (response && response.numRows > 0) {
          schema.properties.Cube = {
            title: " ",
            oneOf: []
          };
          var arr = schema.properties.Cube.oneOf;
          while (response.hasMoreRows()) {
            arr.push({
              const: response["getCubeName"]() || undefined,
              title: response["getCubeName"]() || undefined
              // title: response["getCatalogName"]() || undefined
            });
            response.nextRow();
          }
        }
      });
  }

  function generateSchema(settings) {
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
          discoverDataSources(schema, {
            urls: settings.urls,
            prop: {}
          }),
          discoverDBCatalogs(schema, {
            urls: settings.urls,
            prop: {
              properties: {
                DataSourceInfo: settings.properties.DataSourceInfo
              }
            }
          }),
          discoverMDCubes(schema, {
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
      key_list = key.split("/");
    for (ii = 1; ii < key_list.length; ii += 1) {
      kk = decodeJsonPointer(key_list[ii]);
      if (ii === key_list.length - 1) {
        if (value !== undefined) {
          d[kk] = value[0];
        } else {
          return d[kk];
        }
      } else {
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
  }

  rJS(window)
    .ready(function (g) {
      g.props = {};
      g.props.xmla_connections = {};
    })
    .allowPublicAcquisition("notifyValid", function (arr, scope) {
    })
    .allowPublicAcquisition("notifyInvalid", function (arr, scope) {
    })
    .declareMethod("render", function (opt) {
      this.props.init_value = opt.value;
      return this.getDeclaredGadget("xmla_settings")
        .push(function (g) {
          return g.render(opt);
        });
    })
    .declareMethod("getContent", function () {
      return this.getDeclaredGadget("xmla_settings")
        .push(function (g) {
          return g.getContent();
        });
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition("notifyChange", function (arr, scope) {
      var g = this,
        p = arr[0].path,
        gadget_settings,
        path;

      function f(settings_path, rerender_path) {
        return g.getDeclaredGadget("xmla_settings")
          .push(function (gadget) {
            gadget_settings = gadget;
            return gadget.getContent(settings_path);
          })
          .push(function (settings) {
            return generateSchema(settings);
          })
          .push(function (schema) {
            return gadget_settings.rerender(rerender_path, schema);
          })
          .push(function () {
            return g.notifyChange();
          });
      }

      for (path in g.props.xmla_connections) {
        if (g.props.xmla_connections.hasOwnProperty(path) &&
            p.startsWith(path)) {
          return f(path, g.props.xmla_connections[path]);
        }
      }
      return g.notifyChange();
    })
    .allowPublicAcquisition("resolveExternalReference", function (arr) {
      var g = this,
        url = arr[0],
        schema_path = arr[1],
        path = arr[2],
        settings,
        connection_path;
      if ("urn:jio:properties_from_xmla.connection.json" === url) {
        connection_path = path.split('/').slice(0, -1).join('/');
        return new RSVP.Queue()
          .push(function () {
            if (g.props.init_value) {
              settings = convertOnMultiLevel(g.props.init_value, connection_path);
              if (settings) {
                convertOnMultiLevel(g.props.init_value, connection_path, []);
              }
            }
            return generateSchema(settings);
          })
          .push(function (s) {
            g.props.xmla_connections[connection_path] = path;
            return s;
          });
      }
      throw new Error("urn: '" + url + "' not supported");
    });

}(window, rJS));
