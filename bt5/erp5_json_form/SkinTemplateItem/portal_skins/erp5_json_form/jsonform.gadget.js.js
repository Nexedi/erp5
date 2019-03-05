/*jslint nomen: true, maxlen: 200, indent: 2, maxerr: 100*/
/*global window, document, URL, rJS, RSVP, jIO, Blob */

(function (window, document, Blob, rJS, RSVP, jIO) {
  "use strict";
  var expandSchema;

  function arrayIntersect(x, y) {
    return x.filter(function (value) {
      return y.indexOf(value) >= 0;
    });
  }

  function getUrlWithoutHash(url) {
    if (typeof url !== "string") {
      url = url.href;
    }
    var index = url.indexOf('#');

    if (index >= 0) {
      return url.substring(0, index);
    }
    return url;
  }

  function URLwithJio(url, base_url) {
    var urn_prefix,
      pathname,
      fake_prefix = "https://jio_urn_prefix/";
    // XXX urn: can any case
    if (url.startsWith("urn:jio:reference?")) {
      urn_prefix = url.indexOf("?") + 1;
      urn_prefix = url.slice(0, urn_prefix);
      url = fake_prefix + decodeURIComponent(url.replace(urn_prefix, ""));
    }
    if (typeof base_url === "string" &&
        !(url.startsWith("http://") || url.startsWith("https://") || url.startsWith("//")) &&
        base_url.startsWith("urn:jio:reference?")) {
      if (!urn_prefix) {
        urn_prefix = base_url.indexOf("?") + 1;
        urn_prefix = base_url.slice(0, urn_prefix);
      }
      base_url = fake_prefix + decodeURIComponent(base_url.replace(urn_prefix, ""));
    }
    url = new URL(url, base_url);
    if (urn_prefix) {
      pathname = url.pathname.slice(1);
      this.href = urn_prefix + encodeURIComponent(pathname + url.search + url.hash);
      this.origin = urn_prefix;
      this.pathname = encodeURIComponent(pathname);
      this.hash = url.hash;
      this.search = "";
      return this;
    }
    return url;
  }

  function decodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~1/g, '/').replace(/~0/g, '~');
  }

  function encodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~/g, '~0').replace(/\//g, '~1');
  }

  function getMaxPathInDict(dict, path) {
    var target,
      key,
      max_len = 0;
    if (!path) {
      return "";
    }
    for (key in dict) {
      if (dict.hasOwnProperty(key) &&
          path.startsWith(key) &&
          key.length > max_len) {
        target = key;
        max_len = key.length;
      }
    }
    return target;
  }

  function checkCircular(urls, path, url) {
    var stack,
      idx,
      prev_field_path = getMaxPathInDict(urls, path);
    stack = urls[prev_field_path] || [];
    idx = stack.indexOf(url);
    if (idx >= 0) {
      if (path === prev_field_path && idx === 0) {
        return;
      }
      return true;
    }
    // copy and add url as first element
    urls[path] = [url].concat(stack);
  }

  function checkHardCircular(g, path, url) {
    return checkCircular(g.props.schema_required_urls, path, url);
  }

  function checkAndMarkSoftCircular(g, schema_arr, path, url) {
    var ret = true;
    // if schema_arr.length > 1 selection rendered in any case
    // so we not need checkCircular and have small optimisation
    if (schema_arr.length === 1) {
      ret = checkCircular(g.props.schema_urls, path, url);
      schema_arr[0].circular = ret;
    }
    if (ret) {
      // if schema_arr.length > 1 selection rendered and loop break
      // if circular found selection rendered and loop break
      // so we can begin from start
      g.props.schema_urls[path] = [];
    }
  }

  function convertToRealWorldSchemaPath(g, path) {
    var url,
      hash,
      map = g.props.schema_map,
      prev_downl_path,
      max_len = 0;
    if (!path) {
      return "";
    }
    // previous downloaded path
    prev_downl_path = getMaxPathInDict(map, path);
    if (prev_downl_path === undefined) {
      url = "";
      max_len = 0;
    } else {
      url = map[prev_downl_path];
      if (prev_downl_path === "/") {
        max_len = 0;
      } else {
        max_len = prev_downl_path.length;
      }
    }
    hash = path.substr(max_len);
    if (hash) {
      // XXX urlencode for hash
      if (url.indexOf("#") >= 0) {
        url = url + hash;
      } else {
        url = url + "#" + hash;
      }
    }
    return url;
  }

  function convertUrlToAbsolute(g, path, url, base_url_failback) {
    var // previous downloaded path
      base_url = convertToRealWorldSchemaPath(g, path),
      absolute_url;
    if (base_url === "" || base_url.indexOf("#") === 0) {
      absolute_url = new URLwithJio(url, base_url_failback);
    } else {
      absolute_url = new URLwithJio(url, base_url);
    }
    return absolute_url;
  }

  function downloadJSON(url) {
    return RSVP.Queue()
      .push(function () {
        return jIO.util.ajax({
          url: url,
          dataType: "json"
        });
      })
      .push(function (evt) {
        return evt.target.response;
      });
  }

  function resolveLocalReference(schema, ref) {
    // 2 here is for #/
    var i, ref_path = ref.substr(2, ref.length),
      parts = ref_path.split("/");
    if (parts.length === 1 && parts[0] === "") {
      // It was uses #/ to reference the entire json so just return it.
      return schema;
    }
    for (i = 0; i < parts.length; i += 1) {
      if (schema === undefined) {
        throw new Error("local ref `" + ref + "` does not exist in:");
      }
      schema = schema[decodeJsonPointer(parts[i])];
    }
    return schema;
  }

  function schemaPushSchemaPart(schema, schema_path, schema_part) {
    var i,
      k,
      key_list;
    if (schema_path === "/") {
      schema_path = "";
    }
    key_list = schema_path.split("/");
    for (i = 0; i < key_list.length; i += 1) {
      k = decodeJsonPointer(key_list[i]);
      if (i === key_list.length - 1) {
        if (schema_part !== undefined) {
          schema[k] = schema_part;
        } else {
          return schema[k];
        }
      } else {
        if (!schema.hasOwnProperty(k)) {
          schema[k] = {};
        }
        schema = schema[k];
      }
    }
  }

  function map_url(g, download_url) {
    var hash = download_url.hash,
      mapped_url = getUrlWithoutHash(download_url),
      i,
      schemas = g.props.schemas,
      next_mapped_url;
    // simple defence forever loop
    for (i = 0; i < Object.keys(schemas).length; i += 1) {
      next_mapped_url = schemas[mapped_url];
      if (next_mapped_url === undefined) {
        break;
      }
      mapped_url = new URL(next_mapped_url, g.__path);
      if (hash[0] === '#') {
        hash = hash.slice(1);
      }
      if (hash === '/') {
        hash = '';
      }
      hash = mapped_url.hash || "#" + hash;
      mapped_url = getUrlWithoutHash(mapped_url);
    }
    return new URL(mapped_url + hash);
  }

  function loadJSONSchema(g, $ref, schema_path, path) {
    var protocol,
      abs_url,
      url,
      download_url,
      hash,
      external_reference = false,
      queue;
    // XXX need use `id` property
    if (!schema_path) {
      schema_path = "/";
    }
    abs_url = convertUrlToAbsolute(g, schema_path, decodeURI($ref), window.location);
    url = map_url(g, abs_url);
    abs_url = abs_url.href;
    protocol = url.protocol;
    if (protocol === "http:") {
      if (window.location.protocol !==  protocol) {
        // try change url protocol to https
        url = new URL(url.toString().replace(protocol + "//", window.location.protocol + "//"));
        // throw new Error("You cannot mixed http and https calls");
      }
    }
    download_url = getUrlWithoutHash(url);
    hash = url.hash;
    url = url.href;
    if (download_url.startsWith("urn:jio:")) {
      external_reference = true;
      queue = RSVP.Queue()
        .push(function () {
          return g.resolveExternalReference(download_url, schema_path, path);
        });
    } else {
      queue = RSVP.Queue()
        .push(function () {
          return downloadJSON(download_url);
        });
    }
    return queue
      .push(function (json) {
        if (checkHardCircular(g, schema_path, url)) {
          throw new Error("Circular reference detected");
        }
        return resolveLocalReference(json, hash);
      })
      .push(undefined, function (err) {
        // XXX it will be great to have ability convert json_pointers(hash)
        // in line numbers for pointed to line in rich editors.
        // we can use https://github.com/vtrushin/json-to-ast for it
        var url_from_pointed = convertToRealWorldSchemaPath(g, schema_path),
          schema_a = document.createElement("a"),
          pointed_a = document.createElement("a");
        schema_a.setAttribute("href", download_url);
        schema_a.text = (new URLwithJio(download_url)).pathname;
        pointed_a.setAttribute("href", url_from_pointed);
        pointed_a.text = (new URLwithJio(url_from_pointed)).pathname;
        g.props.schema_resolve_errors[url_from_pointed] = {
          schemaPath: schema_path,
          message: [
            document.createTextNode("schema error: "),
            document.createTextNode(err.message),
            schema_a,
            document.createTextNode(" pointed from schema: "),
            pointed_a
          ]
        };
        return null; // schema part can't be null
      })
      .push(function (schema_part) {
        if (schema_part === null) {
          // if resolving schema part contain errors
          // use {} as failback
          schema_part = {};
        } else {
          // save map url only for correctly resolved schema
          // otherwise we have issue in convertToRealWorldSchemaPath
          if (!g.props.hasOwnProperty(schema_path)) {
            g.props.schema_map[schema_path] = abs_url;
          }
        }
        schemaPushSchemaPart(g.props.schema, schema_path, JSON.parse(JSON.stringify(schema_part)));
        // console.log(g.props.schema[""]);
        return expandSchema(g, schema_part, schema_path, path, $ref);
      })
      .push(function (schema_arr) {
        checkAndMarkSoftCircular(g, schema_arr, schema_path, url);
        schema_arr.external_reference = external_reference;
        return schema_arr;
      });
  }

  function mergeSchemas(x, y, doesntcopy) {
    if (x === true && y === true) {
      return true;
    }
    if (x === false || y === false) {
      return false;
    }
    var key,
      p;
    if (x.hasOwnProperty("$ref") ||
        y.hasOwnProperty("$ref")) {
      if (doesntcopy) {
        // we need reference resolve before merging
        // so allOf schema returned and array item or object field
        // run merging on next iteration.
        return {
          allOf: [
            x,
            y
          ]
        };
      }
      throw new Error("all reference must be resolved before merge run on first recursion level");
    }
    if (x === true) {
      x = {};
    } else if (!doesntcopy) {
      x = JSON.parse(JSON.stringify(x));
      // cleanup already walked schema variations
      if (x.anyOf) {
        delete x.anyOf;
      }
      if (x.oneOf) {
        delete x.oneOf;
      }
      if (x.allOf) {
        delete x.allOf;
      }
    }
    if (y === true) {
      y = {};
    }
    for (key in y) {
      if (y.hasOwnProperty(key)) {
        if (x.hasOwnProperty(key)) {
          switch (key) {
          case "maxProperties":
          case "maxLength":
          case "maxItems":
          case "maximum":
          case "exclusiveMaximum":
            if (y[key] < x[key]) {
              x[key] = y[key];
            }
            break;
          case "minProperties":
          case "minItems":
          case "minLength":
          case "minimum":
          case "exclusiveMinimum":
            if (x[key] < y[key]) {
              x[key] = y[key];
            }
            break;
          case "additionalProperties":
          case "additionalItems":
          case "contains":
          case "propertyNames":
            x[key] = mergeSchemas(x[key], y[key], true);
            break;
          case "items":
            // XXX items can be array
            x[key] = mergeSchemas(x[key], y[key], true);
            break;
          case "contentEncoding":
          case "contentMediaType":
            if (x[key] !== y[key]) {
              return false;
            }
            break;
          case "multipleOf":
            x[key] = x[key] * y[key];
            break;
          case "type":
            if (typeof x.type === "string") {
              if (typeof y.type === "string") {
                if (x.type !== y.type) {
                  return false;
                }
              } else if (y.type.indexOf(x.type) === -1) {
                return false;
              }
            } else {
              if (typeof y.type === "string") {
                if (x.type.indexOf(y.type) === -1) {
                  return false;
                }
              } else {
                x.type = arrayIntersect(x.type, y.type);
                if (x.type.length === 0) {
                  return false;
                }
              }
            }
            break;
          case "properties":
          case "patternProperties":
            for (p in y[key]) {
              if (y[key].hasOwnProperty(p)) {
                if (x[key].hasOwnProperty(p)) {
                  x[key][p] = mergeSchemas(x[key][p], y[key][p], true);
                } else {
                  x[key][p] = y[key][p];
                }
              }
            }
            break;
          case "pattern":
            // XXX regex string merge
          case "dependencies":
            // XXX find solution how merge
            x[key] = y[key];
            break;
          case "required":
            for (p = 0; p < y.required.length; p += 1) {
              if (x.required.indexOf(y.required[p]) < 0) {
                x.required.push(y.required[p]);
              }
            }
            break;
          case "uniqueItems":
            x[key] = y[key];
            break;
          case "allOf":
          case "anyOf":
          case "oneOf":
          case "$ref":
          case "id":
          case "$id":
            // XXX
            break;
          default:
            // XXX
            x[key] = y[key];
          }
        } else {
          switch (key) {
          case "allOf":
          case "anyOf":
          case "oneOf":
          case "$ref":
            break;
          default:
            x[key] = y[key];
          }
        }
      }
    }
    return x;
  }

  function allOf(g, schema_array, schema_path, path, base_schema) {
    return RSVP.Queue()
      .push(function () {
        var i,
          arr = [];
        for (i = 0; i < schema_array.length; i += 1) {
          arr.push(expandSchema(g, schema_array[i], schema_path + '/' + i.toString(), path));
        }
        return RSVP.all(arr);
      })
      .push(function (arr) {
        var i,
          x,
          y,
          next_schema,
          schema,
          summ_arr;
        for (i = 0; i < arr.length - 1; i += 1) {
          summ_arr = [];
          for (x = 0; x < arr[i].length; x += 1) {
            for (y = 0; y < arr[i + 1].length; y += 1) {
              schema = arr[i][x].schema;
              next_schema = arr[i + 1][y].schema;
              schema = mergeSchemas(schema, next_schema);
              summ_arr.push({
                schema: schema,
                // XXX we loss path arr[i + 1][y].schema_path
                schema_path: arr[i][x].schema_path
              });
            }
          }
          arr[i + 1] = summ_arr;
        }
        for (x = 0; x < summ_arr.length; x += 1) {
          summ_arr[x].schema = mergeSchemas(summ_arr[x].schema, base_schema);
        }
        return summ_arr;
      });
  }

  function anyOf(g, schema_array, schema_path, path, base_schema) {
    return RSVP.Queue()
      .push(function () {
        var i,
          arr = [];
        for (i = 0; i < schema_array.length; i += 1) {
          arr.push(expandSchema(g, schema_array[i], schema_path + '/' + i.toString(), path));
        }
        return RSVP.all(arr);
      })
      .push(function (arr) {
        var i,
          z,
          schema_arr = [];
        for (i = 0; i < arr.length; i += 1) {
          for (z = 0; z < arr[i].length; z += 1) {
            if (arr[i][z].schema === true) {
              // or(any, restricted, restricted, .. ) simplify to any
              return [arr[i][z]];
            }
            if (base_schema.title) {
              arr[i][z].title = base_schema.title;
            }
            if (base_schema.description) {
              arr[i][z].description = base_schema.description;
            }
            arr[i][z].schema = mergeSchemas(base_schema, arr[i][z].schema);
            schema_arr.push(arr[i][z]);
          }
        }
        return schema_arr;
      });
  }

  expandSchema = function (g, schema, schema_path, path, ref) {
    // XXX `if then else` construction can be simplify to
    // anyOf(allOf(if_schema, then_schema), else_schema)
    // and realized by existed rails
    var schema_p;
    if (schema === undefined ||
        Object.keys(schema).length === 0) {
      schema = true;
    }
    if (schema_path === "/") {
      schema_p = "";
    } else {
      schema_p = schema_path;
    }
    if (schema.anyOf !== undefined) {
      return anyOf(g, schema.anyOf, schema_p + '/anyOf', path, schema);
    }
    if (schema.oneOf !== undefined) {
      return anyOf(g, schema.oneOf, schema_p + '/oneOf', path, schema)
        .push(function (ret) {
          ret.schema_path = schema_path;
          return ret;
        });
    }
    if (schema.allOf !== undefined) {
      return allOf(g, schema.allOf, schema_p + '/allOf', path, schema)
        .push(function (ret) {
          ret.schema_path = schema_path;
          return ret;
        });
    }
    if (schema.$ref) {
      return loadJSONSchema(g, schema.$ref, schema_path, path);
    }
    if (schema.definitions) {
      var key,
        d,
        url,
        mapped_url;
      for (key in schema.definitions) {
        if (schema.definitions.hasOwnProperty(key)) {
          d = schema.definitions[key];
          url = d.$id || d.id;
          if (url) {
            mapped_url = convertUrlToAbsolute(g, schema_path, '#' + schema_path, window.location);
            // XXX                     /?
            mapped_url = mapped_url + 'definitions/' + key;
            if (!g.props.schemas.hasOwnProperty(url)) {
              g.props.schemas[url] = mapped_url;
            }
          }
        }
      }
    }
    return RSVP.Queue()
      .push(function () {
        return [{
          title: schema.title,
          ref: ref,
          schema: schema,
          schema_path: schema_path
        }];
      });
  };

  function schema_arr_marker(schema_arr) {
    var i;
    // XXX need cleanup false schema before
    for (i = 0; i < schema_arr.length; i += 1) {
      if (!schema_arr[i].schema.hasOwnProperty('const')) {
        schema_arr[0].is_arr_of_const = false;
        break;
      }
      if (i === schema_arr.length - 1) {
        schema_arr[0].is_arr_of_const = true;
      }
    }
    return schema_arr;
  }

  function expandSchemaForField(g, schema, schema_path, path, for_required) {
    var required_stack,
      prev_field_path;
    if (for_required) {
      prev_field_path = getMaxPathInDict(g.props.schema_required_urls, schema_path);
      required_stack = g.props.schema_required_urls[prev_field_path];
    } else {
      required_stack = [];
    }
    g.props.schema_required_urls[schema_path] = required_stack;
    return expandSchema(g, schema, schema_path, path)
      .push(schema_arr_marker);
  }

  function convertOnMultiLevel(d, key) {
    var ii,
      kk,
      key_list = key.split("/");
    if (key === "/") {
      return d;
    }
    for (ii = 1; ii < key_list.length; ii += 1) {
      kk = decodeJsonPointer(key_list[ii]);
      if (ii === key_list.length - 1) {
        return d[kk];
      }
      if (!d.hasOwnProperty(kk)) {
        return;
      }
      d = d[kk];
    }
  }

  rJS(window)
    .ready(function () {
      var g = this;
      g.props = {
        errors: {}
      };
      g.options = {};
    })
    .declareAcquiredMethod("resolveExternalReference", "resolveExternalReference")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition("rootNotifyChange", function (arr, scope) {
      return this.notifyChange(arr[0], scope);
    })
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .allowPublicAcquisition("notifyInvalid", function (arr) {
      if (arr[0].length === 0) {
        delete this.props.errors[arr[1]];
      } else {
        this.props.errors[arr[1]] = arr[0];
      }
    })
    .declareMethod('getGadgetByPath', function (path) {
      return this.props.form_gadget.getGadgetByPath(path || "/");
    })
    .allowPublicAcquisition("getSchema", function (arr) {
      var schema_path = arr[0];
      return convertOnMultiLevel(this.props.schema[""], schema_path);
    })
    .declareJob('jobPrintErrors', function () {
      return this.printErrors();
    })
    .allowPublicAcquisition("printErrors", function () {
      return this.jobPrintErrors();
    })
    .declareMethod("printErrors", function () {
      var g = this.props.form_gadget,
        gadget = this;
      return RSVP.Queue()
        .push(function () {
          var i,
            error_id,
            error,
            span,
            tasks = [],
            errors = [],
            schema_resolve_errors = gadget.props.schema_resolve_errors,
            errors_block = g.element.querySelector("div.error-block");

          if (errors_block) {
            errors_block.parentNode.removeChild(errors_block);
          }
          g.element.querySelectorAll(".error").forEach(function (error_message) {
            error_message.textContent = "";
            error_message.removeAttribute("id");
            error_message.hidden = true;
          });

          g.element.querySelectorAll("div.error-input").forEach(function (div) {
            div.setAttribute("class", "");
          });

          for (i in gadget.props.errors) {
            if (gadget.props.errors.hasOwnProperty(i)) {
              errors = errors.concat(gadget.props.errors[i]);
            }
          }

          for (i in schema_resolve_errors) {
            if (schema_resolve_errors.hasOwnProperty(i)) {
              errors.push(schema_resolve_errors[i]);
            }
          }

          if (errors.length === 0) {
            return gadget.notifyValid()
              .push(function () {
                return false;
              });
          }
          span = document.createElement("span");
          span.setAttribute("class", "error");
          span.textContent = "errors: ";
          errors_block = document.createElement("div");
          errors_block.setAttribute("class", "subfield error-block");
          errors_block.appendChild(span);

          function print_error(error, errorUid, errorId) {
            return function (element) {
              var error_message,
                createTextNode = document.createTextNode.bind(document),
                a = document.createElement("a");
              element = element || error.element;
              a.setAttribute("href", "#" + errorUid);
              a.text = errorId;
              element.setAttribute("class", "error-input");
              error_message = element.querySelector(".error");
              error_message.appendChild(a);
              error_message.setAttribute("id", errorUid);
              if (error.message instanceof Array) {
                error.message.forEach(function (x) {
                  error_message.appendChild(x);
                });
              } else {
                error_message.appendChild(createTextNode(error.message));
              }
              error_message.appendChild(document.createElement("br"));
              error_message.hidden = false;

              a = document.createElement("a");
              a.text = errorId;
              a.setAttribute("data-error-link", "#" + errorUid);
              a.setAttribute("class", "error-link");
              if (errorId !== "1") {
                errors_block.appendChild(createTextNode(","));
              }
              errors_block.appendChild(a);
            };
          }
          for (i = 0; i < errors.length; i += 1) {
            error = errors[i];
            error_id = (i + 1).toString();
            if (error.element) {
              tasks.push(
                new RSVP.Queue()
                  .push(print_error(error, "error" + error_id, error_id))
              );
            } else {
              tasks.push(
                g.getElementByPath(error.dataPath || "/")
                  .push(print_error(error, "error" + error_id, error_id))
              );
            }
          }

          return RSVP.Queue()
            .push(function () {
              return RSVP.all(tasks);
            })
            .push(function () {
              g.element.insertBefore(errors_block, g.element.firstChild);
            })
            .push(gadget.notifyInvalid.bind(gadget))
            .push(function () {
              return false;
            });
        });
    })

    .allowPublicAcquisition('parentGetJsonPath', function (arr, scope) {
      return "";
    })

    .declareMethod('render', function (options) {
      var z = {
        saveOrigValue: options.saveOrigValue,
        editable: options.editable === undefined ? true : options.editable
      };
      if (options.hasOwnProperty("key")) {
        z.key = options.key;
      }
      if (options.hasOwnProperty("schema")) {
        if (typeof options.schema === "string") {
          z.schema = options.schema;
        } else {
          z.schema = JSON.stringify(options.schema);
        }
      }
      if (options.schema_url) {
        z.schema_url = (new URL(options.schema_url, window.location))
          .toString();
      }
      if (options.value !== undefined) {
        z.value = JSON.stringify(options.value);
      }
      return this.changeState(z);
    })
    .onStateChange(function () {
      var g = this,
        json_document = g.state.value,
        schema;
      if (json_document !== undefined) {
        json_document = JSON.parse(json_document);
      }
      if (g.state.schema !== undefined) {
        schema = JSON.parse(g.state.schema);
      }
      g.props.toplevel = true;
      // contain map of current normalized schema
      // json pointer and corresponding url
      // it's need for schema uri computation
      g.props.schema = {};
      g.props.schema_map = {};
      g.props.schemas = {
        "http://json-schema.org/draft-04/schema": "json-schema/schema4.json",
        "http://json-schema.org/draft-06/schema": "json-schema/schema6.json",
        "http://json-schema.org/draft-07/schema": "json-schema/schema7.json",
        "http://json-schema.org/schema": "json-schema/schema7.json"
      };
      // schema_urls[path] = [
      // stack urls
      // "url1",
      // "url2"
      // ]
      // used for break soft circular relation of schemas
      g.props.schema_urls = {};
      // schema_required_urls[path] = [
      // stack required urls, on every unrequired field stack begining from []
      // "url1",
      // "url2"
      // ]
      // used for break hard circular relation of schemas
      g.props.schema_required_urls = {};
      // schema_resolve_errors[schema_url] = {
      //   schemaPath: local_schema_path,
      //   message: error_message can be array containing dom elements
      // }
      g.props.schema_resolve_errors = {};
      return RSVP.Queue()
        .push(function () {
          if (!g.props.form_gadget) {
            return g.declareGadget('jsonform/gadget_json_generated_form_child.html',
              {scope: "j" + Math.random().toString(36).substr(2, 9)})
              .push(function (json_form_child) {
                g.props.form_gadget = json_form_child;
                g.element.appendChild(json_form_child.element);
              });
          }
        })
        .push(function () {
          var schema_url,
            queue;
          if (schema !== undefined) {
            schema_url = g.state.schema_url ||
                  schema.$id ||
                  schema.id ||
                  window.location.toString();
            g.props.schema[""] = schema;
            g.props.schema_map["/"] = schema_url;
            g.props.schemas[schema_url] = URL
              .createObjectURL(new Blob([g.state.schema], {type : 'application/json'}));
            queue = expandSchemaForField(g, schema, "/", "/", true);
          } else {
            schema_url = g.state.schema_url ||
                         (json_document && json_document.$schema);
            if (schema_url) {
              queue = loadJSONSchema(g, schema_url)
                .push(schema_arr_marker);
            }
          }
          if (queue) {
            return queue;
          }
          return [{
            schema: true,
            schema_path: ""
          }];
        })
        .push(function (schema_arr) {
          return g.props.form_gadget.renderForm({
            schema_arr: schema_arr,
            document: json_document,
            saveOrigValue: g.state.saveOrigValue,
            required: true,
            top: true
          });
        })
        .push(function () {
          return g.printErrors();
        })
        .push(function () {
          if (g.props.form_gadget.props.changed) {
            g.notifyChange();
          }
        })
        .push(function () {
          return g;
        })
        .push(undefined, function (err) {
          console.error(err);
        });
    })
    .declareMethod('rerender', function (opt) {
      var g = this,
        gadget,
        queue = RSVP.Queue();
      if (opt.scope) {
        queue
          .push(function () {
            return g.props.form_gadget.getDeclaredGadget(opt.scope);
          })
          .push(function (ret) {
            gadget = ret;
          });
      }
      if (opt.path) {
        queue
          .push(function () {
            if (!gadget) {
              gadget = g.props.form_gadget;
            }
            return gadget.getGadgetByPath(opt.path);
          })
          .push(function (ret) {
            gadget = ret.gadget;
          });
      }
      return queue
        .push(function () {
          return gadget.getContent();
        })
        .push(function (value) {
          return gadget.rerender({
            schema: opt.schema,
            value: value,
            ignore_incorrect: opt.ignore_incorrect
          })
            .push(function () {
              if (gadget.props.changed) {
                value = undefined;
              }
              return gadget.reValidate(value, opt.schema);
            });
        });
    })

    .allowPublicAcquisition("expandSchema", function (arr) {
      return expandSchemaForField(this, arr[0], arr[1], arr[2], arr[3]);
    })

    .declareMethod('getContent', function (sub_path) {
      var g = this;
      if (g.state.editable) {
        return g.props.form_gadget.getContent()
          .push(function (value) {
            // Change the value state in place
            // This will prevent the gadget to be changed if
            // its parent call render with the same value
            // (as ERP5 does in case of formulator error)
            g.state.value = JSON.stringify(value);
            if (sub_path) {
              value = convertOnMultiLevel(value, sub_path);
            }
            if (g.state.key) {
              var form_data = {};
              value = JSON.stringify(value);
              form_data[g.state.key] = value;
              return form_data;
            }
            return value;
          });
      }
      return {};
    }, {mutex: 'changestate'});

}(window, document, Blob, rJS, RSVP, jIO));