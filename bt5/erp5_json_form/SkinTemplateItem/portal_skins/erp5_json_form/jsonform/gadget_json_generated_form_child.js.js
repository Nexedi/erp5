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

  function render_enum(g, schema, json_document) {
    var input = document.createElement("select"),
      option,
      i,
      ser_value,
      selected = false,
      enum_arr = schema['enum'];
    input.size = 1;
    if (schema.default) {
      if (json_document === undefined) {
        json_document = schema.default;
        g.props.changed = true;
      }
    } else {
      option = document.createElement("option");
      option.value = "";
      if (json_document === undefined) {
        option.selected = true;
      }
      input.appendChild(option);
    }
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

  function render_boolean(g, schema, json_document) {
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
    if (getDocumentType(schema.default) === "boolean") {
      schema_for_selection.default = schema.default;
    }
    input = render_enum(g, schema_for_selection, json_document);
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
      input.value = ser_const;
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
          schema: options.schema_part,
          schema_path: options.schema_path,
          document: options.default_dict,
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
          schema_arr[0].schema.hasOwnProperty('enum'))) {
        return false;
      }
      if (schema_arr[0].schema.type instanceof Array) {
        return schema_arr[0].schema.type.length <= 1;
      }
      return true;
    }
    return false;
  }

  function checkSchemaSimpleType(schema) {
    return [
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
    var i,
      flag,
      ret_arr = [],
      schema;
    if (schema_arr.length === 1) {
      return schema_arr[0];
    }
    if (json_document !== undefined) {
      for (i = 0; i < schema_arr.length; i += 1) {
        schema = schema_arr[i].schema;
        if (schema === true) {
          flag = true;
        } else if (schema === false) {
          flag = false;
        } else {
          flag = tv4.validate(json_document, schema);
        }
        if (flag) {
          ret_arr.push(schema_arr[i]);
        }
      }
      if (ret_arr.length === 0) {
        // XXX find schema more compatible with document
        return schema_arr[0];
      }
    }
    // XXX if (ret_arr.length > 1) notify user
    return ret_arr[0];
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
              schema_item.schema.hasOwnProperty('enum'))) {
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
                          return gadget.rootNotifyChange();
                        })
                        .push(function () {
                          if (rerender) {
                            return rerender(g, schema_alternatives);
                          }
                          return render_options;
                        })
                        .push(function (render_options) {
                          return g.render(render_options);
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
    if (schema.default === undefined &&
        json_document === undefined) {
      div_input.setAttribute("data-undefined", "true");
    }

    function element_append(child) {
      if (child) {
        input.parentNode.insertBefore(child, input);
        div_input.removeAttribute("data-undefined");
      }
    }

    function div_append(child) {
      if (child) {
        div_input.appendChild(child);
        div_input.removeAttribute("data-undefined");
      }
    }

    if (json_document === undefined) {
      if (schema.hasOwnProperty('default')) {
        json_document = schema.default;
        gadget.props.changed = true;
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
          schema_path_item = schema_path + '/items',
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
                schema_path_item = schema_path + '/items/' + i;
              } else {
                schema_arr = additionalItems;
                schema_path_item = schema_path + '/additionalItems';
              }
            }
            queue
              .push(
                addSubForm.bind(gadget, {
                  gadget: gadget,
                  parent_type: 'array',
                  schema_path: schema_path_item,
                  schema_part: schema_arr,
                  default_dict: json_document[i],
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
                    schema_path: schema_arr[0].schema_path,
                    schema_part: schema_arr[0].schema,
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
                schema_path: value.schema_path,
                schema_part: value.schema
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
                    schema_path: schema_arr[0].schema_path,
                    schema_part: schema_arr[0].schema,
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
                schema_path: value.schema_path,
                schema_part: value.schema
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

  function render_field(gadget, key, path, json_field, default_value, root, schema_path, options) {
    var type,
      div,
      delete_button,
      label,
      label_text,
      div_input,
      span_info,
      error_message,
      input,
      first_path,
      type_changed,
      queue = RSVP.Queue();

    if (json_field instanceof Array) {
      json_field = schemaArrFilteredByDocument(json_field, default_value);
      schema_path = json_field.schema_path;
      json_field = json_field.schema;
    }

    options = options || {};
    type = options.type;

    if (path && key) {
      first_path = path + encodeJsonPointer(key);
    } else {
      first_path = "";
    }

    if (json_field === undefined) {
      json_field = getDocumentSchema(default_value);
    }

    if (getDocumentType(json_field.type) === "string") {
      type = json_field.type;
    } else if (type === undefined &&
               default_value === undefined &&
               getDocumentType(json_field.type) === "array") {
      type = json_field.type[0];
    }
    if (["object", "array"].indexOf(type) >= 0 &&
        !(path !== "" && default_value === undefined) &&
        getDocumentType(default_value) !== type) {
      if (gadget.props.saveOrigValue) {
        // XXX is not useful for user
        // only for tests
        json_field = {
          const: default_value
        };
      } else {
        gadget.props.changed = true;
      }
    }
    if (type === undefined && default_value !== undefined) {
      type = getDocumentType(default_value);
    }

    if (typeof type === "string") {
      // it's only for simple types so we not use
      // complex type detection
      type_changed = default_value !== undefined &&
                     typeof default_value !== type;
    }

    div = document.createElement("div");
    div.setAttribute("class", "jsonformfield ui-field-contain");
    div.title = json_field.description;
    // if (key && !first_path) {
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
    if (false) {
      // XXX;
      label = document.createElement("input");
      label.value = key;
      gadget.props.property_name_edit = label;
    } else {
      label_text = [key, json_field.title]
          .filter(function (v) { return v; })
          .join(" ")
          // use non-breaking hyphen
          .replace(/-/g, "‑");
      if (label_text) {
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
    }
    div_input = document.createElement("div");
    div_input.setAttribute("id", gadget.element.getAttribute("data-gadget-scope") + first_path + '/');
    div_input.setAttribute("class", "input");

    if (json_field.const !== undefined) {
      input = render_const(gadget, json_field, default_value);
    } else if (json_field.enum !== undefined) {
      input = render_enum(gadget, json_field, default_value);
      // XXX take in account existing type with enum
      type_changed = false;
    }

    if (!input && type === "null") {
      input = render_const(gadget, {const: null}, default_value);
    }

    if (!input && type === "boolean") {
      input = render_boolean(gadget, json_field, default_value);
    }

    if (!input && ["string", "integer", "number", "null"].indexOf(type) >= 0) {
      if (json_field.contentMediaType === "text/plain") {
        input = render_textarea(default_value, "string");
      } else {
        input = document.createElement("input");
        if (default_value !== undefined) {
          if (typeof default_value === "object") {
            input.value = JSON.stringify(default_value);
          } else {
            input.value = default_value;
          }
        }

        if (type === "integer" || type === "number") {
          if (default_value === undefined && typeof json_field.default === "number") {
            input.value = json_field.default;
            gadget.props.changed = true;
          }
          input.setAttribute("data-json-type", type);
          if (default_value === undefined || default_value === null ||
              typeof default_value === "number") {
            input.type = "number";
          }
          if (type === "integer") {
            input.setAttribute("step", "1");
            if (typeof default_value === "number" &&
                parseInt(default_value, 10) !== default_value) {
              // original json_document contain float schema
              // limit integer we can save original document
              type_changed = true;
            }
          }
          if (type === "number") {
            input.setAttribute("step", "any");
          }
        } else {
          if (default_value === undefined && typeof json_field.default === "string") {
            input.value = json_field.default;
            gadget.props.changed = true;
          }
          input.type = "text";
          if (json_field.pattern) {
            input.pattern = json_field.pattern;
          }
          if (json_field.format === 'uri') {
            input.type = "url";
            input.spellcheck = false;
          }
        }
      }
    }

    if (!input && type === "array") {
      queue = render_array(
        gadget,
        json_field,
        default_value,
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
            json_field,
            default_value,
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
        input.setAttribute('data-origin-value', JSON.stringify(default_value));
      }
      // XXX for gui
      //input.setAttribute("class", "slapos-parameter");
      div_input.appendChild(input);
    } else {
      div.setAttribute("data-json-path", first_path + '/');
      div.setAttribute("data-json-type", type);
    }

    if (json_field.info !== undefined) {
      span_info = document.createElement("span");
      span_info.textContent = json_field.info;
      div_input.appendChild(span_info);
    }
    error_message = document.createElement("span");
    error_message.setAttribute("class", "error");
    error_message.hidden = true;
    div_input.appendChild(error_message);
    div.appendChild(div_input);

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
    // div.title = json_field.description;

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
                  schema_path: schema_path,
                  schema_part: schema_arr,
                  default_dict: json_document[property_name]
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
              schema_path: value.schema_path,
              schema_part: value.schema
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

  render_object = function (g, json_field, default_dict, root, path, schema_path) {
    var required = json_field.required || [],
      schema_editor = checkSchemaIsMetaSchema(json_field),
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

    if (default_dict === undefined) {
      if (json_field.hasOwnProperty('default')) {
        default_dict = json_field.default;
        g.props.changed = true;
      } else {
        default_dict = {};
      }
    }

    return expandProperties(g, json_field.properties, schema_path + '/properties/', required)
      .push(function (ret) {
        var schema_arr,
          q = RSVP.Queue(),
          s_o,
          key;
        properties = ret;
        for (key in properties) {
          if (properties.hasOwnProperty(key)) {
            schema_arr = properties[key];
            s_o = schemaArrFilteredByDocument(schema_arr, default_dict[key]);
            // XXX need schema merge with patternProperties passed key
            if (checkSchemaArrOneChoise(schema_arr)) {
              if (required.indexOf(key) >= 0) {
                used_properties[key] = false;
                q.push(render_field.bind(g, g, key, path,
                    s_o.schema, default_dict[key], root, s_o.schema_path, {required: true})
                  );
              }
              if (!used_properties.hasOwnProperty(key) &&
                  !schema_editor &&
                  (checkSchemaSimpleType(s_o.schema) || !s_o.circular)
                  ) {
                used_properties[key] = false;
                q.push(render_field.bind(g, g, key, path,
                  s_o.schema, default_dict[key], root, s_o.schema_path, {
                    required: false,
                    delete_button: false
                  }));
              }
            }
            if (!used_properties.hasOwnProperty(key) &&
                default_dict.hasOwnProperty(key)) {
              used_properties[key] = "";
              q.push(
                addSubForm.bind(g, {
                  gadget: g,
                  property_name: key,
                  path: path,
                  schema_path: s_o.schema_path,
                  schema_part: s_o.schema,
                  default_dict: default_dict[key]
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
            schema_path: value.schema_path,
            schema_part: value.schema
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
        if (json_field.patternProperties !== undefined) {
          for (key in json_field.patternProperties) {
            if (json_field.patternProperties.hasOwnProperty(key)) {
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
                  default_dict,
                  path,
                  json_field.patternProperties[key],
                  schema_path + '/patternProperties/' + key,
                  used_properties,
                  element_append
                ))
                .push(root_append);
            }
          }
        }

        if (additionalProperties === undefined) {
          if (json_field.additionalProperties === undefined) {
            additionalProperties = true;
          } else {
            additionalProperties = json_field.additionalProperties;
          }
        }
        if (additionalProperties !== false) {
          queue
            .push(render_object_additionalProperty.bind(g,
              g,
              "additional property",
              default_dict,
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
        for (key in default_dict) {
          if (default_dict.hasOwnProperty(key)) {
            if (!used_properties.hasOwnProperty(key)) {
              queue
                .push(
                  addSubForm.bind(g, {
                    gadget: g,
                    property_name: key,
                    path: path,
                    schema_path: "",
                    schema_part: undefined,
                    default_dict: default_dict[key]
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
      count_of_values = 0,
      scope,
      options = g.props,
      array,
      path,
      key,
      i,
      len,
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
            count_of_values += 1;
          } else {
            return d[kk];
          }
        } else {
          if (!d.hasOwnProperty(kk)) {
            d[kk] = {};
          }
          d = d[kk];
        }
      }
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

    for (path in options.arrays) {
      if (options.arrays.hasOwnProperty(path)) {
        array = options.arrays[path]
          .querySelectorAll("div[data-gadget-parent-scope='" + g.element.getAttribute("data-gadget-scope") + "']");
        len = array.length;
        if (len === 0 &&
            !options.arrays[path].hasAttribute('data-undefined')) {
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
        var json_dict = {},
          k;
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
        for (k in json_dict) {
          if (json_dict.hasOwnProperty(k)) {
            convertOnMultiLevel(multi_level_dict, k, json_dict[k]);
          }
        }
        if (count_of_values === 0) {
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
    .declareAcquiredMethod("renameChildrenParent", "renameChildren")
    .allowPublicAcquisition("renameChildren", function (opt_arr, scope) {
      var property_name,
        objects = this.props.objects,
        new_name = opt_arr[0],
        element = getSubGadgetElement(this, scope),
        parent = element.getAttribute('data-json-parent');
      if (objects.hasOwnProperty(parent)) {
        parent = objects[parent];
        if (parent.hasOwnProperty(new_name)) {
          throw new Error("property already exist");
        }
        // XXX validate property if property pattern
        for (property_name in parent) {
          if (parent.hasOwnProperty(property_name) && parent[property_name] === scope) {
            delete parent[property_name];
            parent[new_name] = scope;
            return new_name;
          }
        }
        throw new Error("gadget not found for renaming");
      }
    })
    .declareMethod("rename", function (new_name, event) {
      var g = this,
        name = g.element.getAttribute('data-json-property-name');
      return this.renameChildrenParent(new_name)
        .push(function () {
          return g.element.setAttribute('data-json-property-name', new_name);
        })
        .push(undefined, function () {
          // XXX notify user
          event.srcElement.value = name;
          event.srcElement.focus();
        });
    })
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
        schema = options.schema,
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
      return render_field(g, property_name, "", schema,
        options.document, root, options.schema_path,
        {
          type: options.type,
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
      if (evt.target === this.props.property_name_edit) {
        return this.rename(this.props.property_name_edit.value, evt);
      }

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