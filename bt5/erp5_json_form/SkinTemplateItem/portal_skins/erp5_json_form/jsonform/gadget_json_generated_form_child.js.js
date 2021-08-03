/*jslint nomen: true, maxlen: 200, indent: 2, maxerr: 100*/
/*global window, document, URL, rJS, RSVP, jIO, tv4, location */

(function (window, document, location, rJS, RSVP, tv4) {
  "use strict";
  var render_object;

  function deepEqual(x, y) {
    if (x === y) {
      return true;
    }
    if ((typeof x === "object" && x !== null) && (typeof y === "object" && y !== null)) {
      if (Object.keys(x).length !== Object.keys(y).length) {
        return false;
      }
      var prop;
      for (prop in x) {
        if (x.hasOwnProperty(prop)) {
          if (y.hasOwnProperty(prop)) {
            if (!deepEqual(x[prop], y[prop])) {
              return false;
            }
          } else {
            return false;
          }
        }
      }
      return true;
    }
    return false;
  }

  function decodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~1/g, '/').replace(/~0/g, '~');
  }

  function encodeJsonPointer(_str) {
    // https://tools.ietf.org/html/rfc6901#section-5
    return _str.replace(/~/g, '~0').replace(/\//g, '~1');
  }

  function getDocumentType(doc) {
    if (doc === undefined) {
      return;
    }
    if (doc === null) {
      return "null";
    }
    if (doc instanceof Array) {
      return "array";
    }
    return typeof doc;
  }

  function guessSchemaType(schema) {
    var property_name;
    for (property_name in schema) {
      if (schema.hasOwnProperty(property_name)) {
        switch (property_name) {
          // case "allOf":
          // case "anyOf":
          // case "oneOf":
          //   return false;
        case "required":
        case "maxProperties":
        case "minProperties":
        case "additionalProperties":
        case "properties":
        case "patternProperties":
        case "dependencies":
        case "propertyNames":
          return "object";
        case "additionalItems":
        case "items":
        case "maxItems":
        case "minItems":
        case "uniqueItems":
        case "contains":
          return "array";
        case "maxLength":
        case "minLength":
        case "pattern":
        case "contentEncoding":
        case "contentMediaType":
          return "string";
        case "multipleOf":
        case "maximum":
        case "exclusiveMaximum":
        case "minimum":
        case "exclusiveMinimum":
          return "number";
        }
      }
    }
  }

  function createElement(type, props) {
    var element = document.createElement(type),
      key;
    for (key in props) {
      if (props.hasOwnProperty(key)) {
        element.setAttribute(key, props[key]);
      }
    }
    return element;
  }

  function getDocumentSchema(doc) {
    var type = getDocumentType(doc),
      schema = {
        type: type
      };
    if (type === "array") {
      schema.maxItems = 0;
    } else if (type === "object") {
      schema.additionalProperties = false;
    } else {
      schema.readOnly = true;
    }
    return schema;
  }

  function render_enum(schema, json_document) {
    var input = document.createElement("select"),
      option,
      i,
      ser_value,
      selected = false,
      enum_arr = schema['enum'];
    input.size = 1;
    option = document.createElement("option");
    option.value = "";
    if (json_document === undefined) {
      option.selected = true;
    }
    input.appendChild(option);
    for (i = 0; i < enum_arr.length; i += 1) {
      if (enum_arr.hasOwnProperty(i)) {
        option = document.createElement("option");
        // XXX use number id for speedup
        ser_value = JSON.stringify(enum_arr[i]);
        option.value = ser_value;
        if (typeof enum_arr[i] === "string") {
          option.textContent = enum_arr[i];
        } else {
          option.textContent = ser_value;
        }
        if (deepEqual(enum_arr[i], json_document)) {
          option.selected = true;
          selected = true;
        }
        input.appendChild(option);
      }
    }
    if (json_document !== undefined && !selected) {
      // save original json_document even if it
      // not support with schema
      // XXX element should be removed on first user interact
      option = document.createElement("option");
      ser_value = JSON.stringify(json_document);
      option.value = ser_value;
      if (typeof json_document === "string") {
        option.textContent = json_document;
      } else {
        option.textContent = ser_value;
      }
      option.selected = true;
      input.appendChild(option);
    }
    return input;
  }

  function render_enum_with_title(schema_arr, json_document, selected_schema) {
    var input = document.createElement("select"),
      option,
      i,
      ser_value,
      selected = false;
    input.size = 1;
    if (json_document === undefined && selected_schema !== undefined) {
      json_document = selected_schema.schema.const;
    }
    option = document.createElement("option");
    option.value = "";
    if (json_document === undefined) {
      option.selected = true;
    }
    input.appendChild(option);
    for (i = 0; i < schema_arr.length; i += 1) {
      option = document.createElement("option");
      // XXX use number id for speedup
      ser_value = JSON.stringify(schema_arr[i].schema.const);
      option.value = ser_value;
      if (schema_arr[i].schema.title) {
        option.textContent = schema_arr[i].schema.title;
      } else if (typeof schema_arr[i].schema.const === "string") {
        option.textContent = schema_arr[i].schema.const;
      } else {
        option.textContent = ser_value;
      }
      if (deepEqual(schema_arr[i].schema.const, json_document)) {
        option.selected = true;
        selected = true;
      }
      input.appendChild(option);
    }
    if (json_document !== undefined && !selected) {
      // save original json_document even if it
      // not support with schema
      // XXX element should be removed on first user interact
      option = document.createElement("option");
      ser_value = JSON.stringify(json_document);
      option.value = ser_value;
      if (typeof json_document === "string") {
        option.textContent = json_document;
      } else {
        option.textContent = ser_value;
      }
      option.selected = true;
      input.appendChild(option);
    }
    return input;
  }

  function render_boolean(json_document) {
    var input,
      schema_for_selection = {
        type: "boolean",
        enum: [true, false]
      };
    // XXX change json_document on open is not correct @bk
    if (json_document === "true") {
      json_document = true;
    }
    if (json_document === "false") {
      json_document = false;
    }
    input = render_enum(schema_for_selection, json_document);
    input.setAttribute('data-json-type', "boolean");
    return input;
  }

  function render_const(g, schema, json_document) {
    var input = document.createElement("input"),
      ser_doc = JSON.stringify(json_document),
      ser_const = JSON.stringify(schema.const);
    input.setAttribute('readonly', true);
    if (json_document === undefined || deepEqual(json_document, schema.const)) {
      if (json_document === undefined) {
        g.props.changed = true;
      }
      input.setAttribute('data-origin-value', ser_const);
      if (schema.title) {
        input.value = schema.title;
      } else {
        input.value = ser_const;
      }
    } else {
      input.value = ser_doc + ' ≠ ' + ser_const;
      input.setAttribute('data-origin-value', ser_doc);
      input.setAttribute('data-const-value', ser_const);
    }
    return input;
  }

  function render_textarea(json_document, data_format) {
    var input = document.createElement("textarea");
    if (json_document !== undefined) {
      if (typeof json_document === "object") {
        input.value = JSON.stringify(json_document, null, 2);
      } else {
        input.value = json_document;
      }
    }
    input["data-format"] = data_format;
    return input;
  }

  function addSubForm(options) {
    var input_element = options.element,
      g = options.gadget,
      property_name,
      parent_path,
      scope;

    scope = "j" + Math.random().toString(36).substr(2, 9);
    if (options.parent_type !== "array") {
      parent_path = options.path;
      property_name = options.property_name;
      if (!property_name) {
        property_name = input_element.value;
      }
      if (!property_name) {
        // XXX notify user
        // you can't create property without property_name
        return RSVP.Queue();
      }
      if (g.props.objects[parent_path].hasOwnProperty(property_name) && g.props.objects[parent_path][property_name] !== "") {
        // XXX notify user
        // you can't create property with existed property_name
        return RSVP.Queue();
      }
      if (input_element) {
        input_element.value = "";
      }
    }

    return g.declareGadget('gadget_json_generated_form_child.html', {scope: scope})
      .push(function (form_gadget) {
        form_gadget.element.setAttribute("data-gadget-parent-scope",
          g.element.getAttribute("data-gadget-scope"));
        if (options.parent_type !== "array") {
          g.props.objects[parent_path][property_name] = scope;
          form_gadget.element.setAttribute("data-json-parent", parent_path);
          form_gadget.element.setAttribute("data-json-property-name", property_name);
        }
        return form_gadget.renderForm({
          type: options.type,
          required: options.required,
          delete_button: options.delete_button,
          selected_schema: options.selected_schema,
          schema_arr: options.schema_arr,
          document: options.json_document,
          display_label: options.parent_type !== "array",
          saveOrigValue: g.props.saveOrigValue,
          scope: scope
        })
          .push(function () {
            if (form_gadget.props.changed) {
              g.props.changed = true;
            }
            return form_gadget.element;
          });
      });
  }

  function expandItems(g, items, schema_path, minItems) {
    if (!(items instanceof Array)) {
      return g.expandSchema(items, schema_path, minItems !== 0);
    }
    var i,
      tasks = [];
    for (i = 0; i < items.length; i += 1) {
      tasks.push(g.expandSchema(items[i], schema_path + '/' + i, i < minItems));
    }
    return RSVP.Queue()
      .push(function () {
        return RSVP.all(tasks);
      });
  }

  function expandProperties(g, properties, schema_path, required) {
    var ret_obj = {};
    return RSVP.Queue()
      .push(function () {
        var property_name,
          arr = [];
        function addPropertyName(p_name) {
          return function (schema_array) {
            ret_obj[p_name] = schema_array;
          };
        }
        for (property_name in properties) {
          if (properties.hasOwnProperty(property_name)) {
            arr.push(
              g.expandSchema(
                properties[property_name],
                schema_path + encodeJsonPointer(property_name),
                required.indexOf(property_name) >= 0
              )
                .push(addPropertyName(property_name))
            );
          }
        }
        return RSVP.all(arr);
      })
      .push(function () {
        return ret_obj;
      });
  }

  function checkSchemaArrOneChoise(schema_arr) {
    if (schema_arr.length === 1) {
      if (schema_arr[0].schema === true ||
          !(schema_arr[0].schema.hasOwnProperty('type') ||
          schema_arr[0].schema.hasOwnProperty('enum') ||
          schema_arr[0].schema.hasOwnProperty('const')
          )) {
        return false;
      }
      if (schema_arr[0].schema.type instanceof Array) {
        return schema_arr[0].schema.type.length <= 1;
      }
      return true;
    }
    if (schema_arr[0].is_arr_of_const) {
      return true;
    }
    return false;
  }

  function checkSchemaSimpleType(schema_arr) {
    // return true if rendering are not recursive
    var schema = schema_arr[0].schema;
    return schema_arr[0].is_arr_of_const ||
           schema.hasOwnProperty('const') ||
       [
        'string',
        'integer',
        'number',
        'boolean',
        'null'
      ].indexOf(schema.type) >= 0;
  }

  function convertExpandedProperties2array(properties) {
    var property_name,
      arr = [],
      i,
      schema_array;
    for (property_name in properties) {
      if (properties.hasOwnProperty(property_name)) {
        schema_array = properties[property_name];
        for (i = 0; i < schema_array.length; i += 1) {
          // add propertyName to title
          if (schema_array[i].title && schema_array.length > 1) {
            schema_array[i].title = property_name + ' /' + schema_array[i].title;
          } else if (schema_array[i].ref && schema_array.length > 1) {
            schema_array[i].title = property_name + ' /' + schema_array[i].ref;
          } else {
            schema_array[i].title = property_name;
          }
          // add propertyName to schemaItem
          schema_array[i].property_name = property_name;
          arr.push(schema_array[i]);
        }
      }
    }
    return arr;
  }

  function schemaArrFilteredByDocument(schema_arr, json_document) {
    var x,
      i,
      errors,
      error,
      flag,
      circular = schema_arr[0].circular,
      ret_arr = [],
      validation,
      schema;
    if (schema_arr.length === 1 ||
        schema_arr[0].is_arr_of_const) {
      return schema_arr;
    }
    if (json_document !== undefined) {
      for (x = 0; x < schema_arr.length; x += 1) {
        schema = schema_arr[x].schema;
        if (schema === true) {
          flag = true;
        } else if (schema === false) {
          flag = false;
        } else {
          flag = tv4.validate(json_document, schema);
        }
        if (flag) {
          ret_arr.push(schema_arr[x]);
        }
      }
      if (ret_arr.length === 0) {
        // currently try to find
        // more compatible schema for current document
        // XXX it may be need be more smart in future
        // (every error has weigh, weigh depend from level...),
        // may be not.
        for (x = 0; x < schema_arr.length; x += 1) {
          schema = schema_arr[x].schema;
          if (schema !== false) {
            validation = tv4.validateMultiple(json_document, schema);
            errors = validation.errors;
            flag = true;
            for (i = 0; i < errors.length; i += 1) {
              error = errors[i];
              if (error.code === 0 || // INVALID_TYPE
                  error.code === 13 || // NOT_PASSED
                  error.code === 14 // BOOLEAN_SCHEMA_FALSE
                  ) {
                if (error.dataPath.split('/').length === 1) {
                  flag = false;
                  break;
                }
              }
              if (error.code === 15 // CONST_NOT_EQUAL
                  ) {
                // take in account errors only on fist level
                if (error.dataPath.split('/').length <= 2) {
                  flag = false;
                  break;
                }
              }
            }
            if (flag) {
              ret_arr = [schema_arr[x]];
              break;
            }
          }
        }
      }
      if (ret_arr.length === 0) {
        return schema_arr;
      }
      ret_arr[0].circular = circular;
      return ret_arr;
    }
    return schema_arr;
  }

  function render_schema_selector(gadget, title, schema_arr, event, rerender) {
    return RSVP.Queue()
      .push(function () {
        var schema_alternatives = [],
          schema_item,
          description,
          i,
          z,
          type;
        function generateItemsForAny(property_name, schema_path) {
          var desc,
            types = [
              "string",
              "number",
              "boolean",
              "array",
              "object",
              "null"
            ],
            ii;
          if (property_name) {
            desc = property_name + " # ";
          } else {
            desc = "";
          }
          for (ii = 0; ii < types.length; ii += 1) {
            schema_alternatives.push({
              title: desc + types[ii],
              value: {
                property_name: property_name,
                schema: { type: types[ii] },
                schema_path: schema_path
              }
            });
          }
        }
        for (i = 0; i < schema_arr.length; i += 1) {
          schema_item = schema_arr[i];
          description = schema_item.title;
          if (schema_item.schema === true ||
              !(schema_item.schema.hasOwnProperty('type') ||
              schema_item.schema.hasOwnProperty('enum') ||
              schema_item.schema.hasOwnProperty('const'))) {
            generateItemsForAny(schema_item.property_name, schema_item.schema_path);
          } else if (getDocumentType(schema_item.schema.type) === "array") {
            description = description || schema_item.schema.description;
            for (z = 0; z < schema_item.schema.type.length; z += 1) {
              type = schema_item.schema.type[z];
              schema_alternatives.push({
                title: description + ' # ' + type,
                value: {
                  type: type,
                  property_name: schema_item.property_name,
                  schema_path: schema_item.schema_path,
                  schema: schema_item.schema
                }
              });
            }
          } else {
            description = description ||
              schema_item.schema.type ||
              schema_item.schema.description;
            schema_alternatives.push({
              title: description,
              value: {
                property_name: schema_item.property_name,
                schema_path: schema_item.schema_path,
                schema: schema_item.schema
              }
            });
          }
        }
        return schema_alternatives;
      })
      .push(function (schema_alternatives) {
        var scope = 's' + Math.random().toString(36).substr(2, 9);
        if (schema_alternatives.length > 1) {
          return gadget.declareGadget("../gadget_html5_select.html", {scope: scope})
            .push(function (g) {
              return RSVP.Queue()
                .push(function () {
                  var x,
                    item_list = [[title, title]],
                    item;
                  if (rerender) {
                    return rerender(g, schema_alternatives);
                  }
                  for (x = 0; x < schema_alternatives.length; x += 1) {
                    item = schema_alternatives[x];
                    item_list.push([item.title, x]);
                  }
                  return {
                    name: scope,
                    editable: true,
                    hidden: item_list.length === 0,
                    value: item_list[0][1],
                    item_list: item_list
                  };
                })
                .push(function (render_options) {
                  gadget.props.add_custom_data[scope] = {
                    element: g.element,
                    event: function () {
                      return g.getContent()
                        .push(function (value) {
                          return event(schema_alternatives[value[scope]].value);
                        })
                        .push(function () {
                          if (rerender) {
                            return rerender(g, schema_alternatives);
                          }
                          return render_options;
                        })
                        .push(function (render_options) {
                          return g.render(render_options);
                        })
                        .push(function () {
                          return gadget.rootNotifyChange();
                        });
                    },
                    rerender: function () {
                      return RSVP.Queue()
                        .push(function () {
                          if (rerender) {
                            return rerender(g, schema_alternatives);
                          }
                          return render_options;
                        })
                        .push(function (render_options) {
                          return g.render(render_options);
                        });
                    }
                  };
                  return g.render(render_options);
                })
                //not need if gadget_html5_select.render return element
                .push(function () {
                  return g.element;
                });
            });
        }
        if (schema_alternatives.length === 1) {
          return RSVP.Queue()
            .push(function () {
              if (rerender) {
                return rerender(undefined, schema_alternatives);
              }
              return true;
            })
            .push(function (ret) {
              var input = document.createElement("button");
              input.setAttribute("class", "ui-btn-icon-notext ui-icon-plus");
              input.type = "button";
              input.title = title;
              if (!ret) {
                input.setAttribute("style", "display: none;");
              }
              gadget.props.add_buttons.push({
                element: input,
                event: function () {
                  return event(schema_alternatives[0].value)
                    .push(function () {
                      if (rerender) {
                        return rerender(undefined, schema_alternatives);
                      }
                      return true;
                    })
                    .push(function (r) {
                      if (!r) {
                        input.setAttribute("style", "display: none;");
                      } else {
                        input.removeAttribute("style");
                      }
                      return gadget.rootNotifyChange();
                    });
                },
                rerender: function () {
                  return RSVP.Queue()
                    .push(function () {
                      if (rerender) {
                        return rerender(undefined, schema_alternatives);
                      }
                      return true;
                    })
                    .push(function (r) {
                      if (!r) {
                        input.setAttribute("style", "display: none;");
                      } else {
                        input.removeAttribute("style");
                      }
                    });
                }
              });
              return input;
            });
        }
        return RSVP.Queue()
          .push(function () {
            return document.createElement("div");
          });
      });
  }

  function render_array(gadget, schema, json_document, div_input, path, schema_path) {
    var input,
      is_items_arr = schema.items instanceof Array,
      minItems = schema.minItems || 0;
    if (json_document instanceof Array &&
        json_document.length === 0) {
      div_input.setAttribute("data-json-empty-array", "true");
    }

    function element_append(child) {
      if (child) {
        input.parentNode.insertBefore(child, input);
        div_input.removeAttribute("data-json-empty-array");
      }
    }

    function div_append(child) {
      if (child) {
        div_input.appendChild(child);
        div_input.removeAttribute("data-json-empty-array");
      }
    }

    // XXX add failback rendering if json_document not array
    // input = render_textarea(schema, default_value, "array");
    return RSVP.Queue()
      .push(function () {
        return RSVP.all([
          expandItems(gadget, schema.items, schema_path + '/items', minItems),
          gadget.expandSchema(schema.additionalItems, schema_path + '/additionalItems', false)
        ]);
      })
      .push(function (arr) {
        var queue = RSVP.Queue(),
          i,
          schema_arr_arr = arr[0],
          additionalItems = arr[1],
          schema_arr = schema_arr_arr,
          len = 0;
        // XXX rewrite loading document for anyOf schema
        if (json_document) {
          for (i = 0; i < json_document.length; i = i + 1) {
            if (is_items_arr) {
              if (i < schema_arr_arr.length) {
                schema_arr = schema_arr_arr[i];
              } else {
                schema_arr = additionalItems;
              }
            }
            queue
              .push(
                addSubForm.bind(gadget, {
                  gadget: gadget,
                  parent_type: 'array',
                  schema_arr: schema_arr,
                  json_document: json_document[i],
                  required: i < minItems
                })
              )
              .push(div_append);
          }
          len = json_document.length;
        }

        if (is_items_arr) {
          if (minItems > len) {
            for (i; i < (minItems - len); i += 1) {
              if (i < schema_arr_arr.length) {
                schema_arr = schema_arr_arr[i];
              } else {
                schema_arr = additionalItems;
              }
              if (!checkSchemaArrOneChoise(schema_arr)) {
                break;
              }
              queue
                .push(
                  addSubForm.bind(gadget, {
                    gadget: gadget,
                    parent_type: 'array',
                    schema_arr: schema_arr,
                    required: true
                  })
                )
                .push(div_append);
            }
          }
          if (i < schema_arr_arr.length) {
            schema_arr = schema_arr_arr[i];
          } else {
            schema_arr = additionalItems;
          }
          // XXX rerender on next item in schema.items
          queue.push(render_schema_selector.bind(gadget,
            gadget, "add item to array",
            schema_arr, function (value) {
              return addSubForm({
                gadget: gadget,
                parent_type: 'array',
                type: value.type,
                selected_schema: value,
                schema_arr: schema_arr
              })
                .push(element_append);
            }));
        } else {
          if (minItems > len && checkSchemaArrOneChoise(schema_arr)) {
            for (i = 0; i < (minItems - len); i += 1) {
              queue
                .push(
                  addSubForm.bind(gadget, {
                    gadget: gadget,
                    parent_type: 'array',
                    schema_arr: schema_arr,
                    required: true
                  })
                )
                .push(div_append);
            }
          }

          queue.push(render_schema_selector.bind(gadget,
            gadget, "add item to array",
            schema_arr, function (value) {
              return addSubForm({
                gadget: gadget,
                parent_type: 'array',
                type: value.type,
                selected_schema: value,
                schema_arr: schema_arr
              })
                .push(element_append);
            }));
        }
        return queue;
      })
      .push(function (element) {
        // var maxItems = schema.maxItems;
        input = element;
        // XXX update on every add/delete item
        // input.hidden = maxItems !== undefined && json_document.length >= maxItems;
        div_input.appendChild(input);
        gadget.props.arrays[path] = div_input;
      });
  }

  function render_field(gadget, property_name, path, schema_arr, json_document, root, options) {
    var type,
      div,
      delete_button,
      label,
      label_text,
      div_input,
      span_info,
      error_message,
      input,
      schema,
      schema_path,
      schema_ob,
      first_path,
      type_changed,
      queue = RSVP.Queue();

    if (options.selected_schema) {
      schema_ob = options.selected_schema;
    } else {
      // XXX if (ret_arr.length > 1) notify user
      schema_ob = schemaArrFilteredByDocument(schema_arr, json_document)[0];
    }
    schema = schema_ob.schema;
    schema_path = schema_ob.schema_path;

    if (schema_path === '/') {
      schema_path = '';
    }

    options = options || {};
    type = options.type;

    if (path && property_name) {
      first_path = path + encodeJsonPointer(property_name);
    } else {
      first_path = "";
    }

    if (schema === undefined) {
      schema = getDocumentSchema(json_document);
    }

    if (getDocumentType(schema.type) === "string") {
      type = schema.type;
    } else if (type === undefined &&
               json_document === undefined &&
               getDocumentType(schema.type) === "array") {
      type = schema.type[0];
    }
    if (["object", "array"].indexOf(type) >= 0 &&
        !(path !== "" && json_document === undefined) &&
        getDocumentType(json_document) !== type) {
      if (gadget.props.saveOrigValue) {
        // XXX is not useful for user
        // only for tests
        schema = {
          const: json_document
        };
      } else {
        gadget.props.changed = true;
      }
    }
    if (type === undefined && json_document !== undefined) {
      type = getDocumentType(json_document);
    }

    if (typeof type === "string") {
      // it's only for simple types so we not use
      // complex type detection
      type_changed = json_document !== undefined &&
                     typeof json_document !== type;
    }

    // render input begin
    if (!input && schema_arr[0].is_arr_of_const && schema_arr.length > 1) {
      input = render_enum_with_title(schema_arr, json_document, options.selected_schema);
    }
    if (!input && schema.const !== undefined) {
      input = render_const(gadget, schema, json_document);
    }
    if (!input && schema.enum !== undefined) {
      input = render_enum(schema, json_document);
      // XXX take in account existing type with enum
      type_changed = false;
    }

    if (!input && type === "null") {
      input = render_const(gadget, {const: null}, json_document);
    }

    if (!input && type === "boolean") {
      input = render_boolean(json_document);
    }

    if (!input && ["string", "integer", "number", "null"].indexOf(type) >= 0) {
      if (schema.contentMediaType === "text/plain") {
        input = render_textarea(json_document, "string");
      } else {
        input = document.createElement("input");
        if (json_document !== undefined) {
          if (typeof json_document === "object") {
            input.value = JSON.stringify(json_document);
          } else {
            input.value = json_document;
          }
        }

        if (type === "integer" || type === "number") {
          input.setAttribute("data-json-type", type);
          if (json_document === undefined || json_document === null ||
              typeof json_document === "number") {
            input.type = "number";
          }
          if (type === "integer") {
            input.setAttribute("step", "1");
            if (typeof json_document === "number" &&
                parseInt(json_document, 10) !== json_document) {
              // original json_document contain float schema
              // limit integer we can save original document
              type_changed = true;
            }
          }
          if (type === "number") {
            input.setAttribute("step", "any");
          }
          if (schema.multipleOf && schema.multipleOf >= 0) {
            input.step = schema.multipleOf;
          }
          if (schema.minimum &&
              // step work from min value so we can't
              // use min if min not multipleOf step
              !(schema.multipleOf &&
              (schema.minimum % schema.multipleOf) !== 0)) {
            input.min = schema.minimum;
          }
          if (schema.maximum) {
            input.max = schema.maximum;
          }
        } else {
          input.type = "text";
          if (schema.pattern) {
            input.pattern = schema.pattern;
          } else if (schema.minLength) {
            // minLength absent in html5 so
            // use pattern for this task
            input.pattern = ".{" + schema.minLength + ",}";
          }
          if (schema.maxLength) {
            input.maxLength = schema.maxLength;
          }
          if (schema.format === 'uri') {
            input.type = "url";
            input.spellcheck = false;
          }
        }
      }
    }
    // render input end

    // html layout render begin
    div = document.createElement("div");
    div.setAttribute("class", "jsonformfield ui-field-contain");
    if (schema.description) {
      div.title = schema.description;
    }
    // if (property_name && !first_path) {
    if (options.delete_button === true) {
      delete_button = createElement("span",
        {"class": "ui-btn-icon-top ui-icon-trash-o"}
        );
      gadget.props.delete_button = delete_button;
      div.appendChild(delete_button);
    } else if (options.top !== true) {
      if (options.required) {
        delete_button = createElement("span",
          {"class": "ui-btn-icon-top ui-icon-circle"}
          );
        div.appendChild(delete_button);
      } else {
        delete_button = createElement("span");
        delete_button.innerHTML = "&emsp;";
        div.appendChild(delete_button);
      }
    }

    label_text = [property_name, schema_ob.title]
      .filter(function (v) { return v; })
      .join(" ")
      // use non-breaking hyphen
      .replace(/-/g, "‑");
    if (property_name || options.top) {
      if (options.top) {
        label = document.createElement("span");
        label.textContent = label_text;
        root.appendChild(label);
      } else {
        label = document.createElement("label");
        label.textContent = label_text;
        div.appendChild(label);
      }
    }

    div_input = document.createElement("div");
    div_input.setAttribute("id", gadget.element.getAttribute("data-gadget-scope") + first_path + '/');
    div_input.setAttribute("class", "input");

    if (!input && type === "array") {
      queue = render_array(
        gadget,
        schema,
        json_document,
        div_input,
        first_path + '/',
        schema_path
      );
    }

    if (!input && type === "object") {
      queue
        .push(function () {
          return render_object(
            gadget,
            schema,
            json_document,
            div_input,
            first_path + '/',
            schema_path
          );
        });
    }

    if (input) {
      // object and array excluded from
      // gadget.props.inputs not contain values
      gadget.props.inputs.push(input);
      input.name = first_path;
      input.required = options.required;
      if (type_changed) {
        input.setAttribute('data-origin-value', JSON.stringify(json_document));
      }
      // XXX for gui
      //input.setAttribute("class", "slapos-parameter");
      div_input.appendChild(input);
    } else {
      div.setAttribute("data-parent-scope", gadget.element.getAttribute("data-gadget-scope"));
      div.setAttribute("data-json-path", first_path + '/');
      div.setAttribute("data-json-type", type);
      if (options.required) {
        div.setAttribute("data-json-required", "true");
      }
    }

    if (schema.info !== undefined) {
      span_info = document.createElement("span");
      span_info.textContent = schema.info;
      div_input.appendChild(span_info);
    }
    error_message = document.createElement("span");
    error_message.setAttribute("class", "error");
    error_message.hidden = true;
    div_input.appendChild(error_message);
    div.appendChild(div_input);
    // html layout render end

    return queue
      .push(function () {
        root.appendChild(div);
        return div;
      });
  }

  function render_object_additionalProperty(g, title, json_document, path, schema, schema_path, used, element_append) {
    var div,
      div_input,
      input;

    div = document.createElement("div");
    div.setAttribute("class", "jsonformfield");
    // div.title = schema.description;

    div_input = document.createElement("div");
    div_input.setAttribute("class", "input");

    input = document.createElement("input");
    input.type = "text";
    input.placeholder = "name of " + title;
    div_input.appendChild(input);

    return g.expandSchema(schema, schema_path)
      .push(function (schema_arr) {
        var queue = RSVP.Queue(),
          property_name;
        for (property_name in json_document) {
          if (json_document.hasOwnProperty(property_name) && !used.hasOwnProperty(property_name)) {
            used[property_name] = "";
            queue
              .push(
                addSubForm.bind(g, {
                  gadget: g,
                  property_name: property_name,
                  path: path,
                  schema_arr: schema_arr,
                  json_document: json_document[property_name]
                })
              )
              .push(element_append);
          }
        }
        queue.push(function () {
          return render_schema_selector(g, "add " + title, schema_arr, function (value) {
            return addSubForm({
              gadget: g,
              element: input,
              path: path,
              type: value.type,
              schema_arr: [value]
            })
              .push(element_append);
          });
        });
        return queue;
      })
      .push(function (input) {
        div_input.appendChild(input);
        div.appendChild(div_input);
        return div;
      });
  }

  function checkSchemaIsMetaSchema(schema) {
    if (!schema) {
      return false;
    }
    if (schema instanceof Array) {
      var i,
        sch;
      for (i = 0; i < schema.length; i += 1) {
        sch = schema[i].schema;
        if (sch.hasOwnProperty("properties") &&
            sch.properties.hasOwnProperty("$schema")) {
          return true;
        }
      }
      return false;
    }
    return schema.hasOwnProperty("properties") &&
           schema.properties.hasOwnProperty("$schema");
  }

  function checkSchemaType(type, check) {
    if (type instanceof Array) {
      return type.indexOf(check) >= 0;
    }
    return type === check;
  }

  // filter property for schema editor mode
  function filterPropery(property_name, current_document) {
    if (current_document.hasOwnProperty("type")) {
      switch (property_name) {
      case "allOf":
      case "anyOf":
      case "oneOf":
        return false;
      case "additionalItems":
      case "items":
      case "maxItems":
      case "minItems":
      case "uniqueItems":
      case "contains":
        if (!checkSchemaType(current_document.type, "array")) {
          return false;
        }
        break;
      case "required":
      case "maxProperties":
      case "minProperties":
      case "additionalProperties":
      case "properties":
      case "patternProperties":
      case "dependencies":
      case "propertyNames":
        if (!checkSchemaType(current_document.type, "object")) {
          return false;
        }
        break;
      case "maxLength":
      case "minLength":
      case "pattern":
      case "contentEncoding":
      case "contentMediaType":
        if (!checkSchemaType(current_document.type, "string")) {
          return false;
        }
        break;
      case "multipleOf":
      case "maximum":
      case "exclusiveMaximum":
      case "minimum":
      case "exclusiveMinimum":
        if (!(checkSchemaType(current_document.type, "number") ||
              checkSchemaType(current_document.type, "integer"))) {
          return false;
        }
        break;
      }
    } else {
      if (current_document.hasOwnProperty("allOf") ||
          current_document.hasOwnProperty("anyOf") ||
          current_document.hasOwnProperty("oneOf")) {
        switch (property_name) {
        case "type":
        case "allOf":
        case "anyOf":
        case "oneOf":
          return false;
        }
      }
      switch (property_name) {
      case "additionalItems":
      case "items":
      case "maxItems":
      case "minItems":
      case "uniqueItems":
      case "required":
      case "maxProperties":
      case "minProperties":
      case "additionalProperties":
      case "properties":
      case "patternProperties":
      case "propertyNames":
      case "maxLength":
      case "minLength":
      case "pattern":
      case "multipleOf":
      case "maximum":
      case "exclusiveMaximum":
      case "minimum":
      case "exclusiveMinimum":
      case "contains":
      case "dependencies":
      case "contentEncoding":
      case "contentMediaType":
        return false;
      }
    }
    return true;
  }

  render_object = function (g, schema, json_document, root, path, schema_path) {
    var required = schema.required || [],
      schema_editor = checkSchemaIsMetaSchema(schema),
      used_properties = {},
      properties,
      selector = {};

    g.props.objects[path] = used_properties;

    function element_append(child) {
      if (child) {
        // insert additionalProperty before selector
        selector.element.parentNode.insertBefore(child, selector.element);
      }
    }

    function root_append(child) {
      root.appendChild(child);
    }

    if (json_document === undefined) {
      json_document = {};
    }

    return expandProperties(g, schema.properties, schema_path + '/properties/', required)
      .push(function (ret) {
        var schema_arr,
          q = RSVP.Queue(),
          filtered_schema_arr,
          key;
        properties = ret;
        for (key in properties) {
          if (properties.hasOwnProperty(key)) {
            schema_arr = properties[key];
            filtered_schema_arr = schemaArrFilteredByDocument(schema_arr, json_document[key]);
            // XXX need schema merge with patternProperties passed key
            if (checkSchemaArrOneChoise(schema_arr)) {
              if (required.indexOf(key) >= 0) {
                used_properties[key] = false;
                q.push(render_field.bind(g, g, key, path,
                    filtered_schema_arr, json_document[key], root, {required: true})
                  );
              }
              if (!used_properties.hasOwnProperty(key) &&
                  !schema_editor &&
                  (checkSchemaSimpleType(filtered_schema_arr) || !filtered_schema_arr[0].circular)
                  ) {
                used_properties[key] = false;
                q.push(render_field.bind(g, g, key, path,
                  filtered_schema_arr, json_document[key], root, {
                    required: false,
                    delete_button: false
                  }));
              }
            }
            if (!used_properties.hasOwnProperty(key) &&
                json_document.hasOwnProperty(key)) {
              used_properties[key] = "";
              q.push(
                addSubForm.bind(g, {
                  gadget: g,
                  property_name: key,
                  path: path,
                  schema_arr: filtered_schema_arr,
                  json_document: json_document[key]
                })
              )
                .push(root_append);
            }
          }
        }
        return q;
      })
      .push(function () {
        var schema_arr = convertExpandedProperties2array(properties);
        return render_schema_selector(g, "add property", schema_arr, function (value) {
          used_properties[value.property_name] = "";
          return addSubForm({
            gadget: g,
            property_name: value.property_name,
            path: path,
            type: value.type,
            schema_arr: [value]
          })
            .push(function (element) {
              var s_e = selector.element;
              if (s_e) {
                s_e.parentNode.insertBefore(element, s_e);
              }
            });
        },
          function (gadget_s, schema_alternatives) {
            var x,
              item_list = [["add property", "add property"]],
              item,
              current_document = g.props.current_document;
            if (schema_alternatives) {
              for (x = 0; x < schema_alternatives.length; x += 1) {
                item = schema_alternatives[x];
                if (!used_properties.hasOwnProperty(item.value.property_name) &&
                    !(schema_editor && current_document &&
                      !filterPropery(item.value.property_name, current_document))) {
                  item_list.push([item.title, x]);
                }
              }
              if (gadget_s) {
                return {
                  name: gadget_s.element.getAttribute('data-gadget-scope'),
                  editable: true,
                  hidden: item_list.length === 1,
                  value: item_list[0][1],
                  item_list: item_list
                };
              }
              return item_list.length > 1;
            }
          });
      })
      .push(function (element) {
        selector.element = element;
        return root_append(element);
      })
      .push(function () {
        var queue = RSVP.Queue(),
          key,
          additionalProperties;

        // XXX for pattern properties needs schemas merge for
        // all passed patterns
        if (schema.patternProperties !== undefined) {
          for (key in schema.patternProperties) {
            if (schema.patternProperties.hasOwnProperty(key)) {
              if (key === ".*" ||
                  key === "^.*$" ||
                  key === ".*$" ||
                  key === "^.*"
                  ) {
                // additionalProperties nether used in this case
                additionalProperties = false;
              }
              queue
                .push(render_object_additionalProperty.bind(g,
                  g,
                  key + " property",
                  json_document,
                  path,
                  schema.patternProperties[key],
                  schema_path + '/patternProperties/' + key,
                  used_properties,
                  element_append
                  ))
                .push(root_append);
            }
          }
        }

        if (additionalProperties === undefined) {
          if (schema.additionalProperties === undefined) {
            additionalProperties = true;
          } else {
            additionalProperties = schema.additionalProperties;
          }
        }
        if (additionalProperties !== false) {
          queue
            .push(render_object_additionalProperty.bind(g,
              g,
              "additional property",
              json_document,
              path,
              additionalProperties,
              schema_path + '/additionalProperties',
              used_properties,
              element_append
              ))
            .push(root_append);
        }

        return queue;
      })
      .push(function () {
        var key,
          queue = RSVP.Queue();
        for (key in json_document) {
          if (json_document.hasOwnProperty(key)) {
            if (!used_properties.hasOwnProperty(key)) {
              queue
                .push(
                  addSubForm.bind(g, {
                    gadget: g,
                    property_name: key,
                    path: path,
                    schema_arr: [{
                      schema: undefined,
                      schema_path: ""
                    }],
                    json_document: json_document[key]
                  })
                )
                .push(root_append);
            }
          }
        }
        return queue;
      });
  };

  function getFormValuesAsJSONDict(g) {
    var multi_level_dict = {"": {}},
      is_empty = true,
      scope,
      options = g.props,
      array,
      path,
      key,
      i,
      len,
      json_dict = {},
      queue = RSVP.Queue();

    function convertOnMultiLevel(d, key, value) {
      var ii,
        kk,
        key_list = key.split("/");
      for (ii = 0; ii < key_list.length; ii += 1) {
        kk = decodeJsonPointer(key_list[ii]);
        if (ii === key_list.length - 1) {
          if (value !== undefined) {
            d[kk] = value;
            is_empty = false;
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

    function check_parent_path_not_empty(path) {
      var key_list = path.split("/"),
        parent_path = key_list.slice(0, key_list.length - 1).join("/");
      return convertOnMultiLevel(multi_level_dict, parent_path) !== undefined;
    }

    function recursiveGetContent(scope, path) {
      queue
        .push(function () {
          return g.getDeclaredGadget(scope);
        })
        .push(function (gadget) {
          return gadget.getContent();
        })
        .push(function (jdict) {
          if (jdict === undefined) {
            return;
          }
          convertOnMultiLevel(multi_level_dict, path, jdict);
        });
    }

    function getContentAndPushArray(scope, parent_path) {
      queue
        .push(function () {
          return g.getDeclaredGadget(scope);
        })
        .push(function (gadget) {
          return gadget.getContent();
        })
        .push(function (jdict) {
          if (jdict === undefined) {
            return;
          }
          var arr = convertOnMultiLevel(multi_level_dict, parent_path);
          if (!(arr instanceof Array)) {
            arr = [];
            convertOnMultiLevel(multi_level_dict, parent_path, arr);
          }
          arr.push(jdict);
        });
    }

    g.props.inputs.forEach(function (input) {
      if (input.hasAttribute('data-origin-value')) {
        json_dict[input.name] = JSON.parse(input.getAttribute('data-origin-value'));
      } else {
        if (input.value !== "") {
          var type = input.getAttribute('data-json-type');
          if (input.tagName === "SELECT" && input.value) {
            // selection used for enums
            json_dict[input.name] = JSON.parse(input.value);
          } else if (type === 'number') {
            json_dict[input.name] = parseFloat(input.value);
          } else if (type === "integer") {
            json_dict[input.name] = parseInt(input.value, 10);
          } else if (type === "boolean") {
            if (input.value === "true") {
              json_dict[input.name] = true;
            } else if (input.value === "false") {
              json_dict[input.name] = false;
            }
          } else if (input.tagName === "TEXTAREA") {
            if (input["data-format"] === "string") {
              json_dict[input.name] = input.value;
            } else {
              json_dict[input.name] = input.value.split('\n');
            }
          } else {
            json_dict[input.name] = input.value;
          }
        }
      }
    });
    for (path in json_dict) {
      if (json_dict.hasOwnProperty(path)) {
        convertOnMultiLevel(multi_level_dict, path, json_dict[path]);
      }
    }


    for (path in options.arrays) {
      if (options.arrays.hasOwnProperty(path)) {
        array = options.arrays[path]
          .querySelectorAll("div[data-gadget-parent-scope='" + g.element.getAttribute("data-gadget-scope") + "']");
        len = array.length;
        if (len === 0 &&
            options.arrays[path].hasAttribute('data-json-empty-array')) {
          convertOnMultiLevel(multi_level_dict, path.slice(0, -1), []);
        }
        for (i = 0; i < len; i = i + 1) {
          getContentAndPushArray(
            array[i].getAttribute('data-gadget-scope'),
            // slice remove concluding '/'
            path.slice(0, -1)
          );
        }
      }
    }

    for (path in options.objects) {
      if (options.objects.hasOwnProperty(path)) {
        for (key in options.objects[path]) {
          if (options.objects[path].hasOwnProperty(key)) {
            scope = options.objects[path][key];
            if (scope) {
              recursiveGetContent(scope, path + encodeJsonPointer(key));
            }
          }
        }
      }
    }

    return queue
      .push(function () {
        // set empty object/array for required properties/items
        // if parent object/array existed
        array = g.element
          .querySelectorAll("div[data-parent-scope='" +
                            g.element.getAttribute("data-gadget-scope") + "']");
        for (i = 0; i < array.length; i += 1) {
          path = array[i].getAttribute("data-json-path").slice(0, -1);
          if (check_parent_path_not_empty(path) &&
              convertOnMultiLevel(multi_level_dict, path) === undefined) {
            if (array[i].hasAttribute("data-json-required")) {
              if (array[i].getAttribute("data-json-type") === "object") {
                convertOnMultiLevel(multi_level_dict, path, {});
              } else {
                convertOnMultiLevel(multi_level_dict, path, []);
              }
            }
          }
        }

        if (is_empty) {
          switch (g.props.type) {
          case "string":
            return "";
          case "number":
            return null;
          case "boolean":
            return null;
          case "array":
            return [];
          case "object":
            return {};
          default:
            return;
          }
        }
        return multi_level_dict[""];
      });
  }

  function getSubGadgetElement(g, scope) {
    return g.element.querySelector("div[data-gadget-scope='" + scope + "']");
  }

  rJS(window)
    .ready(function () {
      var g = this;
      g.props = {};
      g.options = {};
    })
    .declareAcquiredMethod("rootNotifyChange", "rootNotifyChange")
    .declareAcquiredMethod("selfRemove", "deleteChildren")
    .allowPublicAcquisition("deleteChildren", function (arr, scope) {
      var g = this,
        key,
        i,
        button_list = this.props.add_buttons,
        objects = this.props.objects,
        element = getSubGadgetElement(g, scope),
        parent = element.getAttribute("data-json-parent"),
        tasks = [];
      if (objects.hasOwnProperty(parent)) {
        parent = objects[parent];
        for (key in parent) {
          if (parent.hasOwnProperty(key) && parent[key] === scope) {
            delete parent[key];
          }
        }
      }
      element.parentNode.removeChild(element);
      for (key in g.props.add_custom_data) {
        if (g.props.add_custom_data.hasOwnProperty(key)) {
          tasks.push(g.props.add_custom_data[key].rerender());
        }
      }
      for (i = 0; i < button_list.length; i = i + 1) {
        tasks.push(button_list[i].rerender());
      }
      tasks.push(g.rootNotifyChange());
      return RSVP.Queue()
        .push(function () {
          return RSVP.all(tasks);
        });
    })

    .declareMethod('getElementByPath', function (data_path) {
      var g = this,
        array,
        path,
        scope,
        key,
        next_data_path,
        slash_count = 0,
        slash_count_next,
        bingo,
        idx,
        options = g.props;
      if (data_path !== "/") {
        for (path in options.arrays) {
          if (options.arrays.hasOwnProperty(path) && data_path.startsWith(path)) {
            slash_count_next = path.split("/").length - 1;
            if (slash_count_next > slash_count) {
              bingo = path;
              slash_count = slash_count_next;
            }
          }
        }
        if (bingo) {
          array = options.arrays[bingo]
            .querySelectorAll("div[data-gadget-parent-scope='" + g.element.getAttribute("data-gadget-scope") + "']");
          next_data_path = data_path.slice(bingo.length).split("/");
          idx = next_data_path[0];
          next_data_path = "/" + next_data_path.slice(1).join("/");
          return g.getDeclaredGadget(array[idx].getAttribute('data-gadget-scope'))
            .push(function (gadget) {
              return gadget.getElementByPath(next_data_path);
            });
        }

        slash_count = 0;
        for (path in options.objects) {
          if (options.objects.hasOwnProperty(path) && data_path.startsWith(path)) {
            slash_count_next = path.split("/").length - 1;
            if (slash_count_next > slash_count) {
              bingo = path;
              slash_count = slash_count_next;
            }
          }
        }
        if (bingo) {
          path = options.objects[bingo];
          key = decodeJsonPointer(data_path.slice(bingo.length).split('/')[0]);
          if (path.hasOwnProperty(key)) {
            next_data_path = data_path.slice(bingo.length + encodeJsonPointer(key).length);
            if (!next_data_path) {
              next_data_path = "/";
            }
            scope = path[key];
          }
        }
        if (scope === false) {
          // gadget for this element absent
          // so find element in current gadget
          return document.getElementById(
            g.element.getAttribute("data-gadget-scope") + bingo + key + '/'
          );
        }
        if (scope) {
          // get gadget by scope and use relative path for find element in gadget
          return g.getDeclaredGadget(scope)
            .push(function (gadget) {
              return gadget.getElementByPath(next_data_path);
            });
        }
      }
      return RSVP.Queue()
        .push(function () {
          return document.getElementById(
            g.element.getAttribute("data-gadget-scope") + data_path
          );
        });
    })
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("checkValidity", "checkValidity")

    .allowPublicAcquisition("notifyValid", function () {
      return true;
    })
    .allowPublicAcquisition("notifyChange", function (arr, sub_scope) {
      var g = this,
        opt = arr[0],
        event_object;
      event_object = g.props.add_custom_data[sub_scope];
      if (event_object && opt.type === "change") {
        return event_object.event();
      }
      return g.rootNotifyChange();
    })
    .declareMethod('renderForm', function (options) {
      var g = this,
        property_name = g.element.getAttribute('data-json-property-name'),
        schema = options.schema_arr !== undefined && options.schema_arr[0].schema,
        root;
      g.props.changed = false;
      g.props.saveOrigValue = options.saveOrigValue;
      g.props.inputs = [];
      g.props.add_buttons = [];
      g.props.add_custom_data = {};
      g.props.arrays = {};
      g.props.objects = {};
      g.props.path = options.path; // self gadget scope
      if (!property_name || !options.display_label) {
        property_name = "";
      }
      root = g.element.querySelector('[data-json-path="/"]');
      if (!root) {
        root = g.element;
      }
      if (options.delete_button === undefined) {
        if (options.top) {
          options.delete_button = false;
        } else {
          options.delete_button = !options.required;
        }
      }
      if (!options.type && schema && !schema.type) {
        options.type = guessSchemaType(schema);
      }
      // used for empty document generation
      g.props.type = (schema && typeof schema.type === "string" && schema.type) ||
                     options.type || getDocumentType(options.document);
      while (root.firstChild) {
        root.removeChild(root.firstChild);
      }
      if (checkSchemaIsMetaSchema(schema)) {
        g.props.updatePropertySelectors = true;
        g.props.current_document = options.document;
      }
      return render_field(g, property_name, "", options.schema_arr,
        options.document, root,
        {
          type: options.type,
          selected_schema: options.selected_schema,
          required: options.required,
          delete_button: options.delete_button,
          top: options.top
        })
        .push(function () {
          return g.element;
        });
    })

    .declareAcquiredMethod("expandSchema", "expandSchema")
    .onEvent('click', function (evt) {
      if (evt.target === this.props.delete_button) {
        return this.selfRemove(evt);
      }

      var link = evt.target.getAttribute("data-error-link"),
        button_list = this.props.add_buttons,
        field_list = this.props.inputs,
        input,
        changed = false,
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

      for (i = 0; i < field_list.length; i = i + 1) {
        if (evt.target === field_list[i]) {
          input = evt.target;
          if (input.hasAttribute('data-const-value')) {
            input.value = input.getAttribute('data-const-value');
            input.setAttribute('data-origin-value', input.value);
            input.removeAttribute('data-const-value');
            changed = true;
          }
        }
      }
      if (changed) {
        return this.rootNotifyChange();
      }
    })

    .onEvent('input', function (evt) {
      var gadget = this,
        field_list = this.props.inputs,
        i,
        input,
        changed = false;
      // on form data field
      for (i = 0; i < field_list.length; i = i + 1) {
        if (evt.target === field_list[i]) {
          input = evt.target;
          if (input.hasAttribute('data-origin-value')) {
            input.removeAttribute('data-origin-value');
          }
          if (!input.hasAttribute("type")) {
            if (["integer", "number"]
                  .indexOf(input.getAttribute('data-json-type')) >= 0) {
              input.type = "number";
            }
          }
          changed = true;
        }
      }
      if (changed) {
        return gadget.rootNotifyChange();
      }
    })

    .declareMethod('getContent', function () {
      var g = this;
      return getFormValuesAsJSONDict(g)
        .push(function (data) {
          if (g.props.updatePropertySelectors) {
            g.props.current_document = data;
            var key,
              tasks = [];
            for (key in g.props.add_custom_data) {
              if (g.props.add_custom_data.hasOwnProperty(key)) {
                tasks.push(g.props.add_custom_data[key].rerender());
              }
            }
            if (tasks.length > 0) {
              return RSVP.Queue()
                .push(function () {
                  return RSVP.all(tasks);
                })
                .push(function () {
                  return data;
                });
            }
          }
          return data;
        });
    });

}(window, document, location, rJS, RSVP, tv4));