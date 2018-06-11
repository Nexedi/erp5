/*jslint nomen: true, maxlen: 200, indent: 2, maxerr: 100*/
/*global window, document, URL, rJS, RSVP, jIO, tv4, location */

(function (window, document, location, rJS, RSVP, jIO, tv4) {
  "use strict";
  var expandSchema;

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

  function checkCircular(g, path, url) {
    var required_stack,
      idx,
      prev_field_path = getMaxPathInDict(g.props.schema_required_urls, path);
    required_stack = g.props.schema_required_urls[prev_field_path] || [];
    idx = required_stack.indexOf(url);
    if (idx >= 0) {
      if (path === prev_field_path && idx === 0) {
        return;
      }
      throw new Error("Circular reference detected");
    }
    g.props.schema_required_urls[path] = [url].concat(required_stack);
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
      absolute_url = new URL(url, base_url_failback);
    } else {
      absolute_url = new URL(url, base_url);
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

  function loadJSONSchema(g, $ref, path) {
    var protocol,
      url,
      download_url,
      hash,
      schema_url_map;
    // XXX need use `id` property
    if (!path) {
      path = "/";
    }
    url = convertUrlToAbsolute(g, path, $ref, window.location);
    download_url = url.origin + url.pathname;
    schema_url_map = {
      "http://json-schema.org/draft-04/schema": "json-schema/schema4.json",
      "http://json-schema.org/draft-06/schema": "json-schema/schema6.json",
      "http://json-schema.org/draft-07/schema": "json-schema/schema7.json",
      "http://json-schema.org/schema": "json-schema/schema7.json"
    };
    if (schema_url_map.hasOwnProperty(download_url)) {
      url = new URL(schema_url_map[download_url], g.__path);
      download_url = url.origin + url.pathname;
    }
    protocol = url.protocol;
    if (protocol === "http:" || protocol === "https:") {
      if (window.location.protocol !==  protocol) {
        throw new Error("You cannot mixed http and https calls");
      }
    }
    hash = url.hash;
    url = url.href;
    return downloadJSON(download_url)
      .push(function (json) {
        checkCircular(g, path, url);
        return resolveLocalReference(json, hash);
      })
      .push(undefined, function (err) {
        // XXX it will be great to have ability convert json_pointers(hash)
        // in line numbers for pointed to line in rich editors.
        // we can use https://github.com/vtrushin/json-to-ast for it
        var url_from_pointed = convertToRealWorldSchemaPath(g, path),
          schema_a = document.createElement("a"),
          pointed_a = document.createElement("a");
        schema_a.setAttribute("href", download_url);
        schema_a.text = (new URL(download_url)).pathname;
        pointed_a.setAttribute("href", url_from_pointed);
        pointed_a.text = (new URL(url_from_pointed)).pathname;
        g.props.schema_resolve_errors[url_from_pointed] = {
          schemaPath: path,
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
        // console.log(path);
        if (schema_part === null) {
          // if resolving schema part contain errors
          // use {} as failback
          schema_part = {};
        } else {
          // save map url only for correctly resolved schema
          // otherwise we have issue in convertToRealWorldSchemaPath
          g.props.schema_map[path] = url;
        }
        schemaPushSchemaPart(g.props.schema, path, JSON.parse(JSON.stringify(schema_part)));
        // console.log(g.props.schema[""]);
        return expandSchema(g, schema_part, path, $ref);
      })
      .push(function (schema_arr) {
        // if length array > 1 form rendered on demand already
        // so not needed circular detection
        if (schema_arr.length === 1) {
          // XXX need smart circular detection in this place
          schema_arr[0].circular = true;
        }
        return schema_arr;
      });
  }

  function allOf(g, schema_array, schema_path) {
    return RSVP.Queue()
      .push(function () {
        var i,
          arr = [];
        for (i = 0; i < schema_array.length; i += 1) {
          arr.push(expandSchema(g, schema_array[i], schema_path + '/allOf/' + i.toString()));
        }
        return RSVP.all(arr);
      })
      .push(function (arr) {
        var i,
          x,
          y,
          key,
          next_schema,
          schema,
          schema_item,
          summ_arr;
        for (i = 0; i < arr.length - 1; i += 1) {
          summ_arr = [];
          for (x = 0; x < arr[i].length; x += 1) {
            for (y = 0; y < arr[i + 1].length; y += 1) {
              schema = arr[i][x].schema;
              next_schema = arr[i + 1][y].schema;
              if (schema === true && next_schema === true) {
                schema_item = {
                  schema: true,
                  schema_path: arr[i][x].schema_path
                };
              } else if (schema === false || next_schema === false) {
                schema_item = {
                  schema: false,
                  schema_path: arr[i][x].schema_path
                };
              } else {
                if (schema === true) {
                  schema = {};
                }
                if (next_schema === true) {
                  next_schema = {};
                }
                // copy before change
                schema = JSON.parse(JSON.stringify(schema));
                for (key in next_schema) {
                  if (next_schema.hasOwnProperty(key)) {
                    if (schema.hasOwnProperty(key)) {
                      // XXX need use many many rules for merging
                      schema[key] = next_schema[key];
                    } else {
                      schema[key] = next_schema[key];
                    }
                  }
                }
                schema_item = {
                  schema: schema,
                  schema_path: arr[i][x].schema_path
                };
              }
              summ_arr.push(schema_item);
            }
          }
          arr[i + 1] = summ_arr;
        }
        return arr[arr.length - 1];
      });
  }

  function anyOf(g, schema_array, schema_path) {
    return RSVP.Queue()
      .push(function () {
        var i,
          arr = [];
        for (i = 0; i < schema_array.length; i += 1) {
          arr.push(expandSchema(g, schema_array[i], schema_path + '/anyOf/' + i.toString()));
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
            schema_arr.push(arr[i][z]);
          }
        }
        return schema_arr;
      });
  }

  expandSchema = function (g, schema, schema_path, ref) {
    // XXX `if then else` construction can be simplify to
    // anyOf(allOf(if_schema, then_schema), else_schema)
    // and realized by existed rails
    if (schema === undefined) {
      schema = true;
    }
    if (schema.anyOf !== undefined) {
      return anyOf(g, schema.anyOf, schema_path);
    }
    if (schema.allOf !== undefined) {
      return allOf(g, schema.allOf, schema_path);
    }
    if (schema.$ref) {
      return loadJSONSchema(g, schema.$ref, schema_path);
    }
    return RSVP.Queue()
      .push(function () {
        return [{
          title: ref || schema.title,
          schema: schema,
          schema_path: schema_path
        }];
      });
  };

  function expandSchemaForField(g, schema, schema_path, for_required) {
    var required_stack,
      prev_field_path;
    if (for_required) {
      prev_field_path = getMaxPathInDict(g.props.schema_required_urls, schema_path);
      required_stack = g.props.schema_required_urls[prev_field_path];
    } else {
      required_stack = [];
    }
    g.props.schema_required_urls[schema_path] = required_stack;
    return expandSchema(g, schema, schema_path);
  }

  rJS(window)
    .ready(function () {
      var g = this;
      g.props = {};
      g.options = {};
    })
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .allowPublicAcquisition("notifyChange", function () {
      return this.notifyChange();
    })
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .allowPublicAcquisition("checkValidity", function (arr) {
      return this.checkValidity(arr[0]);
    })
    .declareMethod('checkValidity', function (json_document) {
      // XXX need use local schema and local json document
      // in every subgadget to take into account user anyOf choice
      // and so more precisely point to issue
      var g = this.props.form_gadget,
        gadget = this;
      return RSVP.Queue()
        .push(function () {
          if (json_document === undefined) {
            return g.getContent();
          }
          return json_document;
        })
        .push(function (json_d) {
          return tv4.validateMultiple(json_d, gadget.props.schema[""]);
        })
        .push(function (validation) {
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

          for (i in schema_resolve_errors) {
            if (schema_resolve_errors.hasOwnProperty(i)) {
              errors.push(schema_resolve_errors[i]);
            }
          }

          errors = errors.concat(validation.errors);
          errors = errors.concat(validation.missing);

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
              var id = element.id,
                error_message,
                createTextNode = document.createTextNode.bind(document),
                a = document.createElement("a");
              a.setAttribute("href", "#" + errorUid);
              a.text = errorId;
              element.setAttribute("class", "error-input");
              error_message = element.querySelector("#" + id.replace(/\//g, "\\/") + " > .error");
              error_message.appendChild(a);
              error_message.setAttribute("id", errorUid);
              if (error.message instanceof Array) {
                error.message.forEach(function (x) {
                  error_message.appendChild(x);
                });
              } else {
                error_message.appendChild(createTextNode(error.message));
              }
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
            tasks.push(
              g.getElementByPath(error.dataPath || "/")
                .push(print_error(error, "error" + error_id, error_id))
            );
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

    .declareMethod('render', function (options) {
      return this.changeState({
        key: options.key,
        value: options.value || "",
        schema: options.schema,
        schema_url: options.schema_url,
        editable: options.editable === undefined ? true : options.editable
      });
    })
    .onStateChange(function (options) {
      var g = this;
      g.props.toplevel = true;
      // contain map of current normalized schema
      // json pointer and corresponding url
      // it's need for schema uri computation
      g.props.schema = {};
      g.props.schema_map = {};
      // schema_required_urls[path] = [
      // stack required urls, on every unrequired field stack begining from []
      // "url1",
      // "url2"
      // ]
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
          if (options.schema) {
            return options.schema;
          }
          var schema_url = options.schema_url ||
            (options.value && options.value.$schema);
          if (schema_url) {
            return loadJSONSchema(g, schema_url)
              .push(function (schema_arr) {
                return schema_arr[0].schema;
              });
          }
          return {};
        })
        .push(function (schema) {
          g.options.schema = schema;
          return g.props.form_gadget.renderForm({
            schema: schema,
            schema_path: "",
            document: options.value,
            required: true,
            top: true
          });
        })
        .push(function () {
          return g.checkValidity();
        })
        .push(function () {
          return g;
        });
    })
    .allowPublicAcquisition("expandSchema", function (arr) {
      return expandSchemaForField(this, arr[0], arr[1], arr[2]);
    })
    .onEvent('click', function (evt) {
      if (evt.target === this.props.delete_button) {
        return this.selfRemove(evt);
      }

      var link = evt.target.getAttribute("data-error-link"),
        button_list = this.props.add_buttons,
        i;
      if (link) {
        location.href = link;
        return;
      }

      for (i = 0; i < button_list.length; i = i + 1) {
        if (evt.target === button_list[i].element) {
          return button_list[i].event(evt);
        }
      }
    })
    .declareJob('listenEvents', function () {
      // XXX Disable
      return;
    })

    .declareMethod('getContent', function () {
      var g = this;
      if (g.state.editable) {
        return g.props.form_gadget.getContent()
          .push(function (value) {
            // Change the value state in place
            // This will prevent the gadget to be changed if
            // its parent call render with the same value
            // (as ERP5 does in case of formulator error)
            g.state.value = value;
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
    });

}(window, document, location, rJS, RSVP, jIO, tv4));