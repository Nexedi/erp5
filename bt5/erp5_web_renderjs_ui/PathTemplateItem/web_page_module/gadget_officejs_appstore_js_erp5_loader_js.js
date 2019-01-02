/*jslint indent: 2, maxlen: 80, nomen: true, sloppy: true, todo: true */
/*global console, window, jIO, complex_queries, FormData, RSVP, document,
 jQuery */

(function (window, document, $) {
  "use strict";

  // methods for initialization
  var init = {},
    // utility methods
    util = {},
    // ERP5 custom methods
    erp5 = {},
    // JQM content erateerator
    factory = {};

  /* ====================================================================== */
  /*                              MAPPING ERP5                              */
  /* ====================================================================== */
  erp5.map_buttons = {
    "jump": {
      "classes": " action ui-disabled",
      "icon": "plane",
      "text": "Jump",
      "i18n": "",
      "rel": "popup",
      "href": "#global_popup"
    },
    "search": {
      "classes": " action",
      "icon": "search",
      "text": "search",
      "text_i18n": "",
      "href": ""
    },
    "download": {
      "classes": " action",
      "icon": "file-alt",
      "text": "Download",
      "text_i18n": "",
      "href": ""
    }
  };

  // TODO: remove duplicate code for pagination
  erp5.map_actions = {

    /** translate the active page
     * @method translate
     * @param {object} obj Action Object
     * @param {string} language Language to change to
     * @param {boolean} init Flag for inital translation
     */
    // TODO: figure out a way to translate per gadget!
    // TODO: figure out why pagebeforeshow does not trigger on the first page
    "translate": function (obj, language, init) {
      var class_list,
        new_language,
        tag = obj.element.tagName,
        current_language = $.i18n.lng(),
        shortcut = function (language) {
          switch (language) {
          case "zh-CN":
            return "flag-cn";
          case "en-EN":
            return "flag-en";
          }
        };

      // no way to set
      if (current_language !== language || init) {

        if (tag === "SELECT") {
          class_list = obj.element.parentNode.className.replace(
            shortcut(current_language),
            shortcut(language)
          );
          obj.element.parentNode.className = class_list;
          new_language = language;
        } else {
          new_language = current_language;
        }

        $.i18n.setLng(new_language, function () {
          // TODO: not really...
          $($.makeArray(document.querySelectorAll(".translate"))).i18n();
          //           .find("select").selectMenu("refresh").end()
          //           .find("input").filter(function() {
          //             switch (this.type || this.attr(type)) {
          //               case "submit":
          //               case "reset":
          //               case "button":
          //                 return true;
          //               break;
          //             }
          //             return false;
          //           }).checkboxRadio("refresh");
        });
      }
    },

    /**
     * submit a form
     * @method submit
     * @param {object} obj Action Object
     */
    "add": function (obj) {
      init.add(obj);
    },

    /**
     * show jumps popup
     * @method jump
     * @param {object} obj Action Object
     */
    "browse": function (obj) {
      util.setPopupContentPointer(obj, "browse");
    },

    /**
     * show task popup
     * @method tasks
     * @param {object} obj Action Object
     */
    "tasks": function (obj) {
      util.setPopupContentPointer(obj, "tasks");
    },

    /**
     * show application popup
     * @method login
     * @param {object} obj Action Object
     */
    "login": function (obj) {
      util.setPopupContentPointer(obj, "login");
    },

    /**
     * show export popup
     * @method export
     * @param {object} obj Action Object
     */
    "export": function (obj) {
      util.setPopupContentPointer(obj, "export");
    },

    /**
     * generic pagination method changing number of records displayed
     * @method limit
     * @param {object} obj Action Object
     * @param {string} value Value of select
     */
    "limit": function (obj, value) {
      init.paginate(obj, "limit", value);
    },

    /**
     * generic pagination method going to first page
     * @method first
     * @param {object} obj Action Object
     */
    "first": function (obj) {
      init.paginate(obj, "first");
    },

    /**
     * generic pagination method going to last page
     * @method last
     * @param {object} obj Action Object
     */
    "last": function (obj) {
      init.paginate(obj, "last");
    },

    /**
     * generic pagination method going backward
     * @method prev
     * @param {object} obj Action Object
     */
    "prev": function (obj) {
      init.paginate(obj, "prev");
    },

    /**
     * generic pagination method going forward
     * @method next
     * @param {object} obj Action Object
     */
    "next": function (obj) {
      init.paginate(obj, "next");
    },

    /**
     * switch sorting state and trigger update of gadget
     * @method sort
     * @param {object} obj Action Object
     */
    "sort": function (obj) {
      // sorting 5-states (none|abc_asc|123_asc|abc_desc|123_desc)
      switch (obj.element.getAttribute("data-direction")) {
      case "desc_abc":
        init.sort(
          obj,
          "desc_123",
          "sort-by-alphabet-alt",
          "sort-by-order-alt"
        );
        break;
      case "desc_123":
        init.sort(obj, "asc_abc", "sort-by-order-alt", "sort-by-alphabet");
        break;
      case "asc_abc":
        init.sort(obj, "asc_123", "sort-by-alphabet", "sort-by-order");
        break;
      case "asc_123":
        init.sort(obj, undefined, "sort-by-order", "sort");
        break;
      default:
        init.sort(obj, "desc_abc", "sort", "sort-by-alphabet-alt");
        break;
      }
    },

    /**
     * selecting single checkbox
     * @method check
     * @param {object} obj Action Object
     */
    "check": function (obj) {
      init.check(obj, undefined);
    },

    /**
     * select all visible rows (default)
     * @method check_all_visible
     * @param {object} obj Action Object
     */
    "check_all_visible": function (obj) {
      init.check(obj, false);
    },

    /**
     * select ALL rows (visible and not visible)
     * @method check_all
     * @param {object} obj Action Object
     */
    // NOTE: checkbox has 3 states (this hijacks indeterminate state!!!)
    "check_all": function (obj) {
      var checkbox = obj.element,
        label = checkbox.previousSibling;

      if (checkbox.checked) {
        if (checkbox.indeterminate === false) {
          checkbox.setAttribute("flag", true);
        }
      } else {
        if (checkbox.getAttribute("flag")) {
          checkbox.removeAttribute("flag");
          checkbox.indeterminate = true;
          checkbox.checked = true;

          label.className = label.className.replace(
            util.filterForClass("ui-checkbox-on"),
            " ui-icon-globe"
          );
        } else {
          checkbox.indeterminate = false;
          label.className = label.className.replace(
            util.filterForClass("ui-icon-globe"),
            ""
          );
        }
      }
      // create visual and state
      init.check(obj, true);
    },

    /**
     * search (default)
     * @method search
     * @param {object} obj Action Object
     */
    "search": function (obj) {
      init.search(obj);
    }
  };

  erp5.map_utils = {

    /**
     * Map erp5? (actually it's JIO) items object generateListview can handle
     * @method mapListItems
     * @param {object} items Items to be mapped
     * @param {string} replace Indicator of portal_type
     * @return {object} mapped object
     */
    // TODO: this should be in a storage-related utility object!
    // TODO: how to get count? run query on underlying_portal_type with
    // category? Lot of queries
    // TODO: add remaining mapping!
    // TODO: bad because not generic! Try!!!
    "mapListItems": function (items, replace) {
      var property,
        obj,
        i,
        item,
        clean,
        value,
        store,
        split,
        host,
        i18n,
        app,
        arr = [];

      for (i = 0; i < items.length; i += 1) {
        item = items[i].doc;
        obj = {
          "type": "item",
          "center": {
            "text": []
          }
        };

        for (property in item) {
          if (item.hasOwnProperty(property)) {
            clean = property.replace((replace + "_"), "");

            switch (clean) {
            case "url":
              obj["href"] = item[property];
              split = item[property].split("//");

              if (split.length > 1) {
                host = split[1].split("/")[0];
                // HACK: Don't do it like that!
                app = split[1].split("/")[1];
              }
              // TODO: Make generic handler for this
              if (item[property] === "") {
                console.log("ribbon")
                obj.ribbon = true;
              }
              if ((split.length > 1 && window.location.host !== host) || 
                  app === "app") {
                obj.external = true;
              }
              break;
            case "_id":
              obj.id = item[property];
              break;
            case "title":
              value = item[property];
              obj[clean] = value;
              i18n = item[property + "_i18n"] || null;
              obj.center.text.unshift({
                "type": "h1",
                "text": value,
                "text_i18n": i18n
              });
              break;
            case "description":
              i18n = item[property + "_i18n"] || null;
              obj.center.text.push({
                "type": "p",
                "text": item[property],
                "text_i18n": i18n
              });
              break;
            case "image_type":
              obj.left = {};
              obj.left[item[property]] = (store !== undefined ? store : false);
              break;
            case "image_url":
              if (obj.left !== undefined) {
                if (obj.left.image === false) {
                  obj.left.image = item[property];
                  obj.left.alt = item.title;
                }
                if (obj.left.icon === false) {
                  obj.left.icon = item[property];
                }
              } else {
                store = item[property];
              }
              break;
            }
          }
        }
        arr.push(obj);
      }
      return arr;
    },

    /**
     * Map erp5 form field configuration to factory
     * @method mapFormField
     * @param {object} spec Form field definition
     * @param {object} overrides Overrides for this field
     * @param {string} value Value to set this field to
     * @returns {object} config Configuration object to pass to factory
     */
    "mapFormField": function (spec, overrides, passed_value) {
      var validation_list,
        class_list,
        element,
        type,
        prevail,
        clear,
        config = {};

      // set empty overrides if none are passed
      if (overrides === undefined) {
        prevail = {
          "properties": {},
          "widget": {}
        };
      } else {
        prevail = overrides;
      }

      // NOTE: assumes validval is used for client-side validation
      // TODO: generate criteria to construct special field types for ERP5
      if (spec !== undefined) {
        validation_list = "";
        class_list = "";

        // validation
        // external validator (name)
        // NOTE: method must be present or added to validation handler
        if (prevail.properties.external_validator ||
            spec.properties.external_validator) {
          validation_list += (prevail.properties.external_validator ||
            spec.properties.external_validator);
        }

        // required
        if (prevail.properties.required || spec.properties.required) {
          class_list += "required ";
        }

        // maximum_length
        if (prevail.properties.maximum_length ||
            spec.properties.maximum_length) {
          validation_list += "|max_length:" +
            (prevail.properties.maximum_length ||
            spec.properties.maximum_length) + "&truncate:" +
            (prevail.properties.truncate || spec.properties.truncate);
        }

        // unknown selection?

        // type-related validation, element and type definition
        switch (spec.type) {
        case "StringField":
        case "RelationStringField":
        case "IntegerField":
          element = "input";
          type = "text";
          clear = true;
          break;
        case "PasswordField":
          element = "input";
          type = "password";
          clear = true;
          break;
        case "CheckboxField":
          element = "input";
          type = "checkbox";
          break;
        case "MultiListField":
        case "ListField":
        case "ParallelListField":
          element = "select";
          break;
        case "DateTimeField":
          element = "input";
          clear = true;
          // NOTE: generate datePicker if no support for type="date"
          type = "date";
          validation_list += "|type:dateTime" + "|start:" +
            (prevail.properties.start_datetime ||
            spec.properties.start_datetime) + "|end:" +
            (prevail.properties.end_datetime ||
            spec.properties.end_datetime) + "|null:" +
            (prevail.properties.allow_empty_datetime ||
            spec.properties.allow_empty_datetime);
          break;
        case "TextareaField":
          element = "textarea";
          validation_list += "|max_lines:" +
            (prevail.properties.maximum_lines ||
            spec.properties.maximum_lines) + "|max_characters:" +
            (prevail.properties.maximum_characters ||
            spec.properties.maximum_characters) +
            "|maximum_length_of_line:" +
            (prevail.properties.maximum_length_of_line ||
            spec.properties.maximum_length_of_line);
          break;
        case "EmailField":
          validation_list += "|type:email";
          element = "input";
          clear = true;
          type = "email";
          break;
        }

        if (validation_list === "") {
          validation_list = undefined;
        }

        // construct config
        config.type = element;
        config.direct = {
          "id": (prevail.widget.id || spec.widget.id),
          "className": class_list + " " + (prevail.widget.css_class ||
              spec.widget.css_class || "")
        };
        config.attributes = {
          "data-enhanced": "true",
          "type": (prevail.widget.hidden || spec.widget.hidden) === true ?
              "hidden" : type
        };
        config.logic = {
          "data-vv-validations": validation_list || undefined,
          "extra": prevail.widget.extra || spec.widget.extra || undefined,
          "name": prevail.widget.alternate_name ||
              spec.widget.alternate_name || null,
          "size": prevail.widget.display_width || spec.widget.display_width ||
              prevail.widget.size || spec.widget.size || undefined,
          "rows": prevail.widget.width || spec.widget.width || undefined,
          "cols": prevail.widget.height || spec.widget.height || undefined,
          "disabled": (prevail.properties.enabled || spec.properties.enabled) ?
              (undefined) : true,
          "value": passed_value || (prevail.widget.default_value === "0" ?
              "0" : prevail.widget.default_value) ||
                  spec.widget.default_value || undefined,
          "readonly": (prevail.properties.editable === false ||
            spec.properties.editable === false) ? (true) : undefined,
          "options": (prevail.widget.items || spec.widget.items) ?
              ([
                prevail.widget.items || spec.widget.items || null,
                prevail.widget.extra_per_item || spec.widget.extra_per_item ||
                  null,
                prevail.widget.select_first_item ||
                  spec.widget.select_first_item || null
              ]) : null,
          "label": prevail.widget.title || spec.widget.title,
          "label_i18n": prevail.widget.title_i18n || spec.widget.title_i18n,
          "title": prevail.widget.description || spec.widget.description,
          "title_i18n": prevail.widget.description_i18n ||
            spec.widget.description_i18n,
          "clear": clear || undefined
        };
      } else {
        util.errorHandler({
          "error": "mapFormField: No field definition defined"
        });
      }

      return config;
    }
  };

  erp5.map_gadgets = {
    /**
     * Create a listgrid
     * @method listgrid
     * @param {object} spec Configuration of this gadget
     * @param {object} answer Dynamic data from storage
     * @param {object} fields Field Definition for underlying portal type
     * @param {boolean} update Update or create the gadget
     * @return {object} fragment
     */
    // NOTE: heavy lifting is done inside factory.map_utils.mapListItems
    // NOTE: removed fields and update params for JSLINT!
    listgrid: function (spec, answer) {
      var element, i, empty, target = factory.util.wrapInForm(spec);

      if (answer.data.total_rows > 0) {
        for (i = 0; i < spec.children.length; i += 1) {
          element = spec.children[i];

          if (element.type === "listview") {
            element.id = spec.id;
            element.children = factory.map_utils.mapListItems(
              answer.data.rows,
              spec.portal_type_title
            );
          } else {
            element.reference = spec.id;
          }
          target.appendChild(factory.util.forward(element));
        }
      } else {
        empty = factory.generateElement(
          "p",
          {"className": "responsive ui-content-element"}
        );
        empty.appendChild(factory.generateElement(
          "span",
          {"className": "translate"},
          {"data-i18n": "global.action_list.no_items"},
          {"text": "No items found"}
        ));
        empty.appendChild(factory.generateElement(
          "a",
          {
            "className": "ui-corner-all ui-btn ui-shadow ui-btn-inline " +
              "ui-icon-chevron-sign-left ui-btn-icon-left translate"
          },
          {"data-i18n": "global.action_list.back", "data-rel": "back"},
          {"text": "Back"}
        ));
        target.appendChild(empty);
      }
      return target;
    },

    /**
     * Create a fieldlist
     * @method fieldlist
     * @param {object} spec Configuration of this gadget
     * @param {object} answer Dynamic data from storage
     * @param {object} fields Field Definition for underlying portal type
     * @param {boolean} update Update or create the gadget
     * @return {object} fragment
     */
    // NOTE: removed update parameter for JSLINT
    fieldlist: function (spec, answer, fields) {
      var i, element, target = document.createDocumentFragment();

      for (i = 0; i < spec.children.length; i += 1) {
        element = spec.children[i];

        // new
        if (element.type === "form") {
          if (answer) {
            if (answer.data.total_rows > 1) {
              util.errorHandler({
                "error": "Fieldlist: More than 1 record"
              });
            } else {
              element.data = answer.data.rows[0].doc;
            }
          }
          element.form = spec.form;
          element.fields = fields;
          element.id = spec.id;
        }
        target.appendChild(factory.util.forward(element));
      }

      return target;
    },

    /**
     * Create listbox table
     * @method constructListbox
     * @param {object} config Configuration of this gadget
     * @param {object} answer JIO query
     * @param {object} fields Field definitions
     * @param {boolean} update Update or create gadget
     * @returns {objects} fragment
     */
    // TODO: parameters are not good, modify into something more generic!
    // TODO: only 1 listbox per layout?
    listbox: function (config, answer, fields, update) {
      var fragment,
        bar,
        arr,
        local_popup,
        global_popup,
        set,
        id,
        area,
        table,
        l,
        active_page;

      if (config) {
        set = config.configuration;

        if (update) {
          return factory.generateTableBody(config, answer);
        }

        id = config.base_element.direct.id;
        area = config.layout[0].position === "center" ? 2 : 1;
        fragment = factory.generateElement(
          "div",
          {"className": "span_" + area}
        );

        // add controlbar
        if (set.controlbar.length > 0) {
          bar = factory.generateElement(
            "div",
            {"className": "ui-controlbar"}
          );
          arr = factory.generateToolbar(set.controlbar, undefined, id);
          bar.appendChild(arr[0]);

          // TODO: improve, too much code, array pass-arounds
          global_popup = arr[1].global_popup;
          local_popup = arr[1].local_popup;

          fragment.appendChild(bar);
        }

        // add wrapper
        if (set.wrapper.length > 0) {
          arr = factory.generateToolbar(set.wrapper, true, id);
          fragment.appendChild(arr[0]);

          // TODO: too much popup handling here
          if (global_popup === undefined) {
            global_popup = arr[1].global_popup;
          }
          if (local_popup === undefined) {
            local_popup = arr[1].local_popup;
          }
        }

        // local popup handler
        if (local_popup) {
          active_page = util.getActivePage();
          if (document.getElementById(active_page)
              .querySelectorAll("div.local_popup") === null) {
            fragment.appendChild(
              factory.generatePopup(undefined, active_page)
            );
          }
        }

        // global popup handler
        if (global_popup && document.getElementById("global_popup") === null) {
          document.documentElement.appendChild(
            factory.generatePopup(undefined, undefined)
          );
        }

        // TODO: pre-enhance!
        // table
        config.base_element.attributes["data-role"] = "table";
        table = factory.generateElement(
          config.base_element.type,
          config.base_element.direct,
          config.base_element.attributes,
          config.base_element.logic
        );
        table.appendChild(
          factory.generateTableHeader(config, fields)
        );
        table.appendChild(
          factory.generateTableBody(config, answer)
        );
        // table.appendChild(factory.generateTableFooter(config, portal_type);

        // done
        fragment.appendChild(table);

        if (config.actions) {
          for (l = 0; l < config.actions.length; l += 1) {
            fragment.appendChild(
              factory.generateControlgroup(config.actions[l])
            );
          }
        }
        return fragment;
      }
      return factory.generateElement(
        "p",
        {},
        {},
        {"text": "Error. No configuration found"}
      );
    }
  };

  /* ====================================================================== */
  /*                               FACTORY                                  */
  /* ====================================================================== */

  /* ********************************************************************** */
  /*                             Factory Mappings (to ERP5)                 */
  /* ********************************************************************** */
  factory.map_buttons = erp5.map_buttons;
  factory.map_actions = erp5.map_actions;
  factory.map_gadgets = erp5.map_gadgets;
  factory.map_utils = erp5.map_utils;

  /* ********************************************************************** */
  /*                             Factory Utils                              */
  /* ********************************************************************** */
  factory.util = {};

  /*
   * Forward to factory generator depending on "generate". This method will
   * handle generation of elements, widgets (and gadgets?)
   * @method forward
   * @param {object} spec Configuration object for the element to be created
   * @return {object} HTML object containing generated elements
   */
  factory.util.forward = function (spec) {
    switch (spec.generate) {
      // widget generator
    case "widget":
      return factory[
        "generate" + spec.type.charAt(0).toUpperCase() + spec.type.slice(1)
      ](spec);
      // gadget generator
    case "gadget":

      break;
      // HTML element generator (case "undefined")
    default:
      switch (spec.type) {
      case "input":
      case "select":
        return factory.generateFormElement(spec, false);
      default:
        return factory.generateElement(
          spec.type,
          spec.direct,
          spec.attributes,
          spec.logic
        );
      }
    }
  };

  /*
   * Loop over a selection of elements and generate the respective content
   * @method generateFromArray
   * @param {array} spec Array containing the elements to generate
   * @param {string} type Requesting widget
   * @param {object} hack
   * @param {string} reference Reference to set on the child elements
   * @return {object} fragment HTML object containing the elements
   */
  // TODO: refactor. Remove hack!!!!
  // TODO: this is crap because it adds first/last which in case of
  // wrapping elements ends up on the wrong element, so do it either before
  // or after!
  // TODO: this function is crap, either do all looping here (listview...)
  // or nothing
  // NOTE: this can only handle fully described elements in an array (no li!)
  factory.util.generateFromArray = function (spec, type, hack, reference) {
    var i,
      target,
      element,
      order,
      fragment = document.createDocumentFragment();

    for (i = 0; i < spec.length; i += 1) {
      element = spec[i];
      target = undefined;

      if (reference) {
        if (element.attributes !== undefined) {
          element.attributes["data-reference"] = reference;
        } else {
          element.reference = reference;
        }
      }

      // class string
      if ((element.type !== "input" && element.type !== "select") &&
          element.direct && type !== "controlbar") {
        order = i === 0 ? " ui-first-child " :
            (i === (spec.length - 1) ? " ui-last-child " : " ");

        element.direct.className = (element.direct.className || "") + order +
          (element.type === "a" ? (" ui-btn ui-shadow " +
          factory.generateIconClassString(element)) : " ");
      }

      switch (type) {
      case "panel":
        // TODO: refactor panel_element CSS!
        target = factory.generateElement(
          "div",
          {
            "className": "panel_element " + (i === 0 ?
                "panel_element_first panel_header " :
                ((i === spec.length - 1) ?
                    "panel_element_last" : " "))
          }
        );
        // HACK: this adds the panel close button, don't do this here!
        if (i === 0 && hack) {
          target.appendChild(hack);
        }
        break;
      case "navbar":
        target = factory.generateElement(
          "li",
          {"className": "ui-block-" + util.toLetter(i + 1).toLowerCase()}
        );
        break;
      case "header":
        // TODO: mercy, refactor!
        if (spec.length > 1 && i !== 1) {
          target = factory.generateElement(
            "div",
            {
              "className": " ui-" + ((i === 0 ? "first" :
                  (i === 2 ? "last" : "no")) + "-wrap ")
            }
          );
        }
        break;
      }

      // generate with/without wrapper
      if (target) {
        target.appendChild(factory.util.forward(element));
        fragment.appendChild(target);
      } else {
        fragment.appendChild(factory.util.forward(element));
      }
    }
    return fragment;
  };

  /**
   * Generate a form wrapper
   * @method wrapInForm
   * @param {object} spec configuration of gadget
   * @return {object} form object of fragment
   */
  // TODO: the gadget should not be wrapped by the form - only the form should
  factory.util.wrapInForm = function (spec) {
    if (spec.form) {
      return factory.generateElement(
        "form",
        {
          "method": "POST",
          "action": "#",
          "id": spec.id,
          "className": (spec.class_list || "")
        },
        {"data-ajax": false}
      );
    }
    return document.createDocumentFragment();
  };

  /* ********************************************************************** */
  /*                             Factory Methods                            */
  /* ********************************************************************** */

  /* ********************************************************************** */
  /*                            JQM POPUP                                   */
  /* ********************************************************************** */
  /**
   * Generate a pre-enhanced popup and necessary elements
   * Full options (with defaults)
   * {
   *   "generate": "widget",
   *   "type":"popup",
   *   "class_list": "",
   *   "theme": "",
   *   "id": null,
   *   "property_dict": {
   *     "overlay-theme": null,
   *     "transition": "fade",
   *     "position-to": "window",
   *     "tolerance": "30,30,30,30",
   *     "shadow": true
   *   },
   *   "form": null,
   *   "children": [],
   * }
   * @method generatePopup
   * @param  {object} spec JSON configuration for popup to be generated
   * @param  {string} scope id of page to append popup
   * @return {object} documentFragment (global)/placeholder element (local)
   */
  // TODO: missing state
  // TODO: generate without referencing IDs
  // NOTE: scope (element id) will make the popup local
  factory.generatePopup = function (spec, scope) {
    var target, popup, wrap, id, config, container, placeholder;

    if (spec === undefined) {
      util.errorHandler({
        "error": "GeneratePopup: Missing configuration"
      });
    } else {
      container = document.createDocumentFragment();
      config = spec.property_dict || {};
      id = spec.id || (scope ? (scope + "-popup") : "global_popup");

      // container
      container.appendChild(factory.generateElement(
        "div",
        {
          "className": "ui-popup-screen ui-screen-hidden " +
              (config.overlay_theme ?
                ("ui-overlay-" + config.overlay_theme) : ""),
          "id": id + "-screen"
        }
      ));

      // popup wrapper
      wrap = factory.generateElement(
        "div",
        {
          "className": "ui-popup-container ui-corner-all ui-popup-hidden " +
            " ui-popup-truncate " + (config.transition || "fade"),
          "id": id + "-popup"
        }
      );

      // popup
      popup = factory.generateElement(
        "div",
        {
          "className": "ui-popup ui-body-" + spec.theme +
            (config.shadow ? " ui-overlay-shadow " : " ") +
            " ui-corner-all " + spec.class_list,
          "id": id
        },
        {
          "data-transition": config.transition || "fade",
          "data-role": "popup",
          "data-enhanced": "true",
          "data-position-to": config.position || "window",
          "data-tolerance": config.tolerance || "30,30,30,30"
        },
        {
          "data-reference": spec.reference || null,
          "data-theme": spec.theme || null,
          "data-overlay-theme": config.overlay_theme || null
        }
      );

      // placeholder
      placeholder = factory.generateElement(
        "div",
        {"id": id + "-placeholder"},
        {"style": "display:none;"}
      );

      // form
      target = factory.util.wrapInForm(spec);

      // children/action buttons
      if (spec.children) {
        popup.appendChild(
          factory.util.generateFromArray(spec.children, "popup")
        );
      }

      // assemble popup to target (form/fragment) to wrapper to container
      target.appendChild(popup);
      wrap.appendChild(target);
      container.appendChild(wrap);

      // add to DOM if scoped
      if (scope) {
        document.getElementById(scope).appendChild(container);
        // and return the placeholder for JQM
        return placeholder;
      }

      // also add placeholder to fragment
      container.appendChild(placeholder);
      return container;
    }
  };

  /* ********************************************************************** */
  /*                            JQM Header                                  */
  /* ********************************************************************** */
  /**
   * Generates JQM header. Header buttons are wrapped in controlgroups!
   * Full options (with defaults)
   * {
   *   "generate": "widget",
   *   "type": "Header",
   *   "class_list": "",
   *   "theme": "",
   *   "id": null,
   *   "form": null,
   *   "property_dict": {
   *     "title": "",
   *     "title_i18n":"",
   *     "fixed": true
   *   },
   *   "children": [],
   *   }
   * @method generateHeader
   * @param {object} spec JSON configuration
   * @param {string} scope Id of page header should be appended to
   * @return {object} HTML fragment
   */
  // NOTE: Logos should be added as children of the header!
  // NOTE: page title set in pagehandler, this only sets a placeholder
  factory.generateHeader = function (spec, scope) {
    var config, id, title, position, children, header, target;

    if (spec === undefined) {
      util.errorHandler({
        "error": "Generate Header: Missing configuration"
      });
    } else {
      config = spec.property_dict || {};
      id = spec.id || (scope ? (scope + "-header") : "global_header");
      children = spec.children.length;
      position = children === 2 ? 1 : (children === 0 ? 0 : 1);

      // title
      title = {
        "type": "h1",
        "direct": {
          "className": "translate ui-title"
        },
        "attributes": {
          "data-i18n": config.title_i18n || "",
          "role": "heading",
          "aria-level": "1"
        },
        "logic": {
          "text": config.title || "\u00A0"
        }
      };
      spec.children.splice(position, 0, title);

      // header
      header = factory.generateElement(
        "div",
        {
          "id": id,
          "className": "ui-header " + (spec.class_list || " ") +
            (config.fixed ? "ui-header-fixed " : " ") +
            " slidedown ui-bar-" + (spec.theme || "inherit")
        },
        {
          "data-role": "header",
          "data-theme": spec.theme,
          "data-enhanced": "true",
          "role": "banner"
        },
        {
          "data-reference": spec.reference || null,
          "data-position": config.fixed ? "fixed" : null
        }
      );

      // form
      target = factory.util.wrapInForm(spec);

      // children/action buttons (wrap first/last)
      if (spec.children) {
        target.appendChild(
          factory.util.generateFromArray(spec.children, "header")
        );
      }

      // assemble
      header.appendChild(target);

      // add to DOM if scoped
      if (scope) {
        document.getElementById(scope).appendChild(header);
        return undefined;
      }

      return header;
    }
  };

  /* ********************************************************************** */
  /*                             JQM PANEL                                  */
  /* ********************************************************************** */
  /**
   * Generates a JQM panel (needs enhancement!)
   * Full spec example (with defaults):
   * {
   *   "generate": "widget",
   *   "type": "panel",
   *   "class_list": null,
   *   "id": null,
   *   "theme": null,
   *   "property_dict" : {
   *     "close": true
   *   },
   *   "children": []
   * }
   * @method generatePanel
   * @param  {object} config JSON configuration
   * @param  {string} scope
   * @param  {string} scope id of page to append panel
   * @return {object} HTML fragment
   */
  // TODO: Needs pre-enhancement!
  factory.generatePanel = function (spec, scope) {
    var config, id, panel, closer, target;

    if (spec === undefined) {
      util.errorHandler({
        "error": "Generate Panel: Missing configuration"
      });
    } else {
      config = spec.property_dict || {};
      id = spec.id || (scope ? (scope + "-panel") : "global_panel");

      // panel
      panel = factory.generateElement(
        "div",
        {"id": id, "className": "panel " + (spec.class_list || "")},
        {
          "data-role": "panel",
          "data-theme": spec.theme,
          "data-position": "left",
          "data-display": "push",
          "data-position-fixed": true
        },
        {"data-reference": spec.reference || null}
      );

      // close button, needs to go into first panel element
      // TODO: refactor!!!!!
      if (config.close) {
        closer = factory.generateElement(
          "a",
          {
            "href": "#",
            "className": "panel-close ui-icon-remove ui-btn " +
              "ui-btn-icon-notext ui-shadow ui-corner-all"
          },
          {
            "data-enhanced": true,
            "data-i18n": "",
            "data-rel": "close"
          },
          {"text": "Close"}
        );
      }

      // form
      target = factory.util.wrapInForm(spec);

      // children
      if (spec.children) {
        target.appendChild(
          factory.util.generateFromArray(spec.children, "panel", closer)
        );
      }

      // assemble
      panel.appendChild(target);

      // add to DOM if scoped
      if (scope) {
        document.getElementById(scope).appendChild(panel);
        return undefined;
      }
      return panel;
    }
  };

  /* ********************************************************************** */
  /*                            JQM Footer                                  */
  /* ********************************************************************** */
  /**
   * Generates JQM footer with navbar or controlgroup based on JSON config
   * Full options (with defaults):
   * {
   *   "generate":"widget",
   *   "type": "footer",
   *   "class_list": null,
   *   "id": "null",
   *   "theme": "slapos-white",
   *   "form": null,
   *   "property_dict": {
   *     "fixed": true
   *   },
   *   "children": []
   * }
   * @method generateFooter
   * @param {object} spec JSON configuration
   * @param {string} scope ID of element to append footer to
   * @return {object} HTML fragment
   */
  factory.generateFooter = function (spec, scope) {
    var config, id, footer, target;

    if (spec === undefined) {
      util.errorHandler({
        "error": "Generate Footer: Missing config"
      });
    } else {
      config = spec.property_dict || {};
      id = spec.id || (scope ? (scope + "-footer") : "global_footer");

      // footer
      footer = factory.generateElement(
        "div",
        {
          "id": id,
          "className": "ui-footer " + (spec.class_list || " ") +
            (config.fixed ? "ui-footer-fixed " : " ") +
            "slideup ui-bar-" + (spec.theme || "inherit")
        },
        {
          "data-role": "footer",
          "data-theme": spec.theme,
          "data-enhanced": "true",
          "role": "contentinfo"
        },
        {
          "data-reference": spec.reference || null,
          "data-position": config.fixed ? "fixed" : undefined
        }
      );

      // form
      target = factory.util.wrapInForm(spec);

      // children
      if (spec.children) {
        target.appendChild(
          factory.util.generateFromArray(spec.children, "footer")
        );
      }

      // assemble
      footer.appendChild(target);

      return footer;
    }
  };

  /* ********************************************************************** */
  /*                                 JQM Form                               */
  /* ********************************************************************** */
  /**
   * Generate a list for form elements
   * @method generateControlgroup
   * @param {object} spec Configuration for controlgroup
   * @return controlgroup
   */
  // TODO: crap to use both layout and children!
  factory.generateForm = function (spec) {
    var i,
      j,
      k,
      layout,
      element,
      container,
      area,
      field,
      overrides,
      position,
      doc,
      config,
      value,
      fragment = factory.util.wrapInForm(spec),
      wrap = function (area) {
        return factory.generateElement(
          "div",
          {"className": "span_" + area}
        );
      };

    // form fields = layout
    for (i = 0; i < spec.layout.length; i += 1) {
      layout = spec.layout[i];
      area = layout.position === "center" ? 2 : 1;
      container = wrap(area);

      for (j = 0; j < layout.fieldlist.length; j += 1) {
        field = layout.fieldlist[j];
        config = spec.fields[field.title];
        overrides = field.overrides;
        doc = spec.data || undefined;
        value = doc ? (doc[field.title]) : undefined;

        switch (j) {
        case 0:
          position = true;
          break;
        case (layout.fieldlist.length - 1):
          position = false;
          break;
        case (j === 1 && layout.fieldlist.length === 1):
          position = null;
          break;
        default:
          position = undefined;
          break;
        }

        // generate and append
        container.appendChild(factory.generateFormElement(
          factory.map_utils.mapFormField(config, overrides, value),
          true,
          true,
          position
        ));
      }
      fragment.appendChild(container);
    }

    // children (default to 1 or 2? crap!)
    for (k = 0; k < spec.children.length; k += 1) {
      // pass reference
      element = spec.children[k];
      if (spec.form) {
        // NOTE: I prefer element["reference"] JSLINT does not
        element.reference = spec.id;
      }
      container = wrap(1);
      container.appendChild(factory.util.forward(element));
    }
    fragment.appendChild(container);

    return fragment;
  };


  /* ********************************************************************** */
  /*                         JQM Controlgroup                               */
  /* ********************************************************************** */
  /**
   * Generate an controlgroup = a button or action menu
   * {
   *   "generate": "controlgroup",
   *   "id": null,
   *   "class_list": null,
   *   "theme": null,
   *   "form": null,
   *   "property_dict": {
   *     "direction": "horizontal"
   *   },
   *   "children": [
   *     {"type":a, "direct": {}, "attributes": {}, "logic": {}}
   *   ]
   * }
   * @method generateControlgroup
   * @param {object} spec Configuration for controlgroup
   * @return controlgroup
   */
  factory.generateControlgroup = function (spec) {
    var config, group, direction, controls, target;

    if (spec === undefined) {
      util.errorHandler({
        "error": "Generate Controlgroup: Missing config"
      });
    } else {
      config = spec.property_dict || {};
      direction = config.direction || "vertical";

      // group
      group = factory.generateElement(
        "div",
        {
          "className": "ui-corner-all ui-controlgroup " +
            (spec.class_list || "") + " ui-controlgroup-" + direction
        },
        {
          "data-role": "controlgroup",
          "data-enhanced": "true",
          "data-type": direction
        },
        {"id": spec.id || null}
      );

      // controls
      controls = factory.generateElement(
        "div",
        {"className": "ui-controlgroup-controls"}
      );

      // children
      // TODO: no hack!
      if (spec.children) {
        controls.appendChild(
          factory.util.generateFromArray(
            spec.children,
            "controlgroup",
            null,
            (spec.reference || null)
          )
        );
      }

      // form
      target = factory.util.wrapInForm(spec);

      // assemble
      group.appendChild(controls);
      target.appendChild(group);

      return target;
    }
  };

  /* ********************************************************************** */
  /*                            JQM Navbar                                  */
  /* ********************************************************************** */
  /* Generate a navbar
   * Full example of spec with all options:
   * {
   *  "generate": "widget",
   *  "type": "navbar",
   *  "class_list": null,
   *  "id": null,
   *  "theme": "slapos-white",
   *  "property_dict": {},
   *  "children":[],
   *  "form": null
   * }
   * @method generateNavbar
   * @param {object} config Configuration options
   * @returns navbar HTML fragment
   */
  factory.generateNavbar = function (spec) {
    var navbar, controls, target;

    if (spec === undefined) {
      util.errorHandler({
        "error": "Generate Navbar: Missing Configuration"
      });
    } else {
      //config = spec.property_dict || {};

      // navbar
      navbar = factory.generateElement(
        "div",
        {"className": "navbar ui-navbar " + (spec.class_list || "")},
        {
          "data-role": "navbar",
          "role": "navigation",
          "data-enhanced": "true"
        },
        {"data-reference": spec.reference || null}
      );

      // controls
      controls = factory.generateElement(
        "ul",
        {
          "className": "ui-grid-" +
            util.toLetter(spec.children.length - 1).toLowerCase()
        }
      );

      // children
      if (spec.children) {
        controls.appendChild(
          factory.util.generateFromArray(spec.children, "navbar")
        );
      }

      // form
      target = factory.util.wrapInForm(spec);

      // assemble
      navbar.appendChild(controls);
      target.appendChild(navbar);

      return target;
    }
  };

  /* ********************************************************************** */
  /*                                JQM Listview                            */
  /* ********************************************************************** */
  /*
   * Generate a JQM listview
   * Default spec with defaults and single list item with all options!
   * {
   *   "generate": "gadget",
   *   "type": "listview",
   *   "class_list": "",
   *   "form": null,
   *   "theme": "slapos-black",
   *   "property_dict": {
   *     "alt_icon": null
   *     "numbered": false
   *     "inset": true,
   *     "reveal": true,
   *     "filter": true,
   *     "input": "#foo"
   *     "placeholder": null,
   *     "filter_theme": null,
   *     "divider_theme": "slapos-white",
   *     "autodividers": true,
   *     "count_theme": "slapos-white"
   *   },
   *   "children": [
   *   {
   *     "type": "item/divider",
   *     "id": null,
   *     "external": true,
   *     "href": "index.html",
   *     "icon": "foo"/null,
   *     "title": null,
   *     "title_i18n":"",
   *     "left": {
   *       "icon": "foo",
   *       "image": "http://www.xyz.com/img/foo.png",
   *       "alt": null
   *     },
   *     "center": {
   *       "count": 3689,
   *       "text": [
   *         {"aside": true, "type":"p", "text":"foo", "text_i18n":null}
   *       ]
   *     },
   *   "right": {
   *     "radio": true,
   *     "checkbox": true,
   *     "action": "foo",
   *     "href": "http://www.foo.com",
   *     "title": null,
   *     "title_i18n": "",
   *     "external": true
   *    }
   *  ]
   *}
   * @method generateListview
   * @param {object} spec JSON configuration
   * @return HTML object
   */
  // TODO: add to form support via children
  // TODO: add collapsible support if needed
  // TODO: mesh with live data!
  // TODO: redo like the above and handle the array creation in arrayHandler
  // WARNING: JQM does not support enhanced on listview - update JQM!
  factory.generateListview = function (spec) {
    var fragment,
      config,
      list,
      i,
      item,
      props,
      divider,
      static_item,
      j,
      block,
      target,
      icon,
      auto,
      last,
      ribbon,
      ribbon_wrap,
      theme;

    if (spec === undefined) {
      util.errorHanlder({
        "error": "Generate listview: Missing configuration"
      });
    } else {
      fragment = document.createDocumentFragment();
      config = spec.property_dict || {};

      // filter
      if (config.filter) {
        // NOTE: if input provided, the filter is already there!
        // TODO: need a proper id!
        if (config.input === undefined) {
          fragment.appendChild(factory.generateFormElement({
            "type": "input",
            "direct": {
              "id": "filter_" + (spec.id || "items"),
              "className": "action"
            },
            "attributes": {
              "data-action": "search",
              "data-enhanced": true,
              "data-i18n": "",
              "placeholder": "Search",
              "data-icon": "search"
            },
            "logic": {
              "clear": "true"
            }
          }));
        }
      }

      // list
      list = factory.generateElement(
        config.numbered ? "ol" : "ul",
        {
          "className": "ui-listview " + (spec.class_list || "") +
            (config.inset ? " ui-listview-inset ui-corner-all ui-shadow " : "")
        },
        {"data-role": "listview", "data-enhanced": true},
        {
          "id": spec.id || null,
          "data-reference": spec.reference || null,
          "data-filter": config.filter || null,
          "data-input": config.input || null,
          "data-filter-theme": config.filter_theme || null,
          "data-filter-placeholder": config.placeholder || null,
          "data-divider-theme": config.divider_theme || null
        }
      );

      // generate items
      for (i = 0; i < spec.children.length; i += 1) {
        props = spec.children[i];

        divider = props.type === "divider" ? true : undefined;
        static_item = (props.href === undefined && !divider) ? true : undefined;
        icon = props.icon;
        theme = config.divider_theme || spec.theme || "inherit";

        // autodividers
        if (config.autodividers) {
          auto = props.text[0].text.slice(0, 1).toUpperCase();
          if (last !== auto) {
            list.appendChild(factory.generateElement(
              "li",
              {
                "className": "ui-li-divider ui-bar-" + theme +
                    (i === 0 ? " ui-first-child" :
                      ((i === spec.children.length - 1) ?
                          " ui-last-child" : ""))
              },
              {},
              {"text": auto}
            ));
            last = auto;
          }
        }
        // list item
        item = factory.generateElement(
          "li",
          {
            "className": divider ? ("ui-li-divider ui-bar-" + theme) : " " +
              (i === 0 ? " ui-first-child" :
                  ((i === spec.children.length - 1) ?
                      " ui-last-child" : " ")) +
              (static_item ? " ui-li-static ui-body-inherit " : " ") +
              (props.center.count ? " ui-li-has-count" : " ") +
              (config.alt_icon ? " ui-icon-alt " : "") +
              (props.left !== undefined ? (props.left.icon ?
                  " ui-li-has-icon " : " ") +
                (props.left.image ? " ui-li-has-thumb " : " ") : " ") +
              (props.right ? " ui-li-has-alt " : " ") +
              (config.form_item ? "ui-field-contain " : " ") +
              (config.reveal ? "ui-screen-hidden " : " ")
          },
          {},
          {
            "data-role": divider ? "divider" : null,
            "role": divider ? "heading" : null,
            "data-icon": icon === null ?
                false : (icon === undefined ? null : icon)
          }
        );
        if (props.ribbon) {
          console.log("ribbon");
          ribbon_wrap = factory.generateElement(
            "span",
            {"className":"ribbon-wrapper"}
          );
          ribbon_wrap.appendChild(factory.generateElement(
            "span",
            {"className": "ribbon"}
          ));
          item.appendChild(ribbon_wrap);
        }
        if (static_item || divider) {
          target = item;
        } else {
          // link
          target = factory.generateElement(
            "a",
            {
              "className": "ui-btn " + (icon === null ? "" :
                  "ui-btn-icon-right ui-icon-" + (icon === undefined ?
                      "carat-r" : icon)),
              "href": props.href
            },
            {
              "title": props.title || "",
              "data-i18n": "[title]" + (props.title_i18n || "")
            },
            {
              "rel": props.external ? "external" : null,
              "data-ajax": props.external ? "false" : null
            }
          );
        }

        // image
        if (props.left !== undefined) {
          if (props.left.image !== undefined) {
            target.appendChild(factory.generateElement(
              "img",
              {"src": props.left.image, "alt": props.left.alt}
            ));
          }
          // custom icon
          if (props.left.icon !== undefined) {
            target.appendChild(factory.generateElement(
              "span",
              {
                "className": "ui-li-icon ui-li-icon-custom ui-icon-" +
                  props.left.icon + " ui-icon"
              },
              {},
              {"text": "\u00A0"}
            ));
          }
        }
        // text elements/aside elements
        for (j = 0; j < props.center.text.length; j += 1) {
          block = props.center.text[j];
          target.appendChild(
            factory.generateElement(
              block.type,
              {
                "className": (block.aside ? "ui-li-aside" : "") +
                  (block.text_i18n ? "translate" : "")
              },
              {"data-i18n": block.text_i18n || ""},
              {"text": block.text}
            )
          );
        }
        // count bubble
        if (props.center.count) {
          target.appendChild(factory.generateElement(
            "span",
            {
              "className": "ui-li-count ui-body-" +
                  (config.count_theme || spec.theme)
            },
            {},
            {"text": props.center.count}
          ));
        }

        // NOTE: if we made a link, target = a, else target = item
        if (static_item || divider) {
          item = target;
        } else {
          item.appendChild(target);
        }

        // split
        if (props.right) {
          // split button
          if (props.right.link) {
            item.appendChild(factory.generateElement(
              "a",
              {
                "href": props.right.href,
                "className": "ui-btn ui-btn-icon-notext ui-icon-" +
                  props.right.icon + " ui-btn-" +
                  (config.split_theme || spec.theme || "inherit")
              },
              {
                "title": props.right.title || "",
                "data-i18n": "[title]" + (props.right.title_i18n || "")
              },
              {
                "rel": props.right.external ? "external" : null,
                "data-ajax": props.external ? "false" : null
              }
            ));
            // split check/radio
            if (props.right.check || props.right.radio) {
              item.appendChild(
                factory.generateFormElement(
                  {
                    "type": "input",
                    "direct": {
                      "id": props.right.check ? (props.id) : " " + "_" + i,
                      "name": props.right.check ? (props.id) : " "
                    },
                    "attributes": {
                      "type": props.right.check ? "checkbox" : "radio",
                      "data-i18n": "[value]",
                      "value": "Select item",
                      "data-iconpos": "notext"
                    },
                    "logic": {}
                  },
                  false,
                  true
                )
              );
            }
          }
        }

        // done
        list.appendChild(item);
      }
      // assemble
      fragment.appendChild(list);

      return fragment;
    }
  };

  /* ********************************************************************** */
  /*                             JQM "Controlbar"                           */
  /* ********************************************************************** */
  /**
   * Generate a generic toolbar for tables or listview or ...
   * @method generateControlbar
   * @param {object} spec JSON configuration
   * @return {object} fragment
   */
  factory.generateControlbar = function (spec) {
    var fragment;

    if (spec === undefined) {
      util.errorHanlder({
        "error": "Generate listview: Missing configuration"
      });
    } else {
      fragment = factory.generateElement(
        "div",
        {"className": "ui-controlbar " + (spec.class_list || "")},
        {},
        {"data-reference": spec.reference || null}
      );
      //config = spec.property_dict || {};

      fragment.appendChild(
        factory.util.generateFromArray(
          spec.children,
          "controlbar",
          null,
          (spec.reference || null)
        )
      );
      return fragment;
    }
  };




  /* ********************************************************************** */
  /*                             JQM "Bar"                                  */
  /* ********************************************************************** */
  /*
   * Generate a generic bar (table wrapper, controlbar, collapsible header)
   * @method generateToolbar
   * @param {object} config Elements to add to the bar
   * @param {boolean} slot Wrap element in a slot container
   * @param {string} reference Gadget reference pointer
   * @returns {array} HTML fragment and flag for popups to be created
   */
  factory.generateToolbar = function (elements, slot, reference) {
    var element,
      m,
      o,
      trigger_element,
      target,
      wrapped_in_slot,
      flag = {},
      container = document.createDocumentFragment();

    if (slot) {
      wrapped_in_slot = true;
    }

    // loop functionalities
    for (m = 0; m < elements.length; m += 1) {
      element = elements[m];
      if (wrapped_in_slot) {
        target = factory.generateElement(
          "div",
          {},
          {"data-slot": true, "data-slot-id": element.slot}
        );
      } else {
        target = container;
      }

      trigger_element = element.element || element.widget;
      // TODO: don't set in every case (because of controlgroup);

      switch (trigger_element.type) {
      case "input":
      case "select":
        trigger_element.attributes["data-reference"] = reference;
        target.appendChild(
          factory.generateFormElement(trigger_element, false)
        );
        break;
      case "controlgroup":
        for (o = 0; o < element.children.length; o += 1) {
          element.children[o].attributes["data-reference"] = reference;
        }
        target.appendChild(factory.generateControlgroup({
          "type": "controlgroup",
          "direction": trigger_element.direction,
          "class": trigger_element.widget_class,
          "buttons": element.children
        }));
        break;
      default:
        trigger_element.attributes["data-reference"] = reference;
        target.appendChild(
          factory.generateElement(
            trigger_element.type,
            trigger_element.direct,
            trigger_element.attributes,
            trigger_element.logic
          )
        );
        break;
      }

      // TODO: do differently...
      if (element.global_popup) {
        flag.global_popup = true;
      }
      if (element.local_popup) {
        flag.local_popup = true;
      }
      if (wrapped_in_slot) {
        container.appendChild(target);
      } else {
        container = target;
      }
    }
    return [container, flag];
  };

  /* ********************************************************************** */
  /*                                JQM Page                                */
  /* ********************************************************************** */
  /**
   * Generate an empty JQM page
   * @method generatePage
   * @param {object} config Config object based on parsed link
   * @param {object} layout Layout for the page to generate
   * @return {object} HTML fragment
   */
  // NOTE: we are defaulting to fixed toolbars!
  factory.generatePage = function (spec, layout) {
    return factory.generateElement(
      "div",
      {
        "id": spec.id,
        "className": "ui-page " + ("ui-page-theme-" + layout.theme || "") +
            " " + ((layout.fix && layout.fix === false) ? "" :
                " ui-page-header-fixed ui-page-footer-fixed")
      },
      {
        "data-module": spec.id,
        "data-role": "page",
        // TODO: while JQM does not support query-parameters, we try to cheat
        "data-url": spec.url.split("#")[1].split("?")[0],
        "data-external-page": true,
        "tabindex": 0,
        "data-enhanced": true
      }
    );
  };

  /* ********************************************************************** */
  /*                                JQM Table                               */
  /* ********************************************************************** */
  /*
   * Generates a table header based on configuration and portal_type
   * @method generateTableHeader
   * @param {object} settings Configuration for table to create
   * @param {object} fields Field configurations for this portal Type
   */
  // TODO: single row ok. multi row to make
  factory.generateTableHeader = function (settings, fields) {
    var l,
      cell,
      field,
      config,
      field_config,
      property,
      title,
      set,
      text,
      action,
      temp = {},
      link,
      check = settings.configuration.table.checkbox_rows,
      merger = settings.configuration.table.mergeable_columns,
      target = settings.layout[0].columns,
      table_header = factory.generateElement("thead"),
      row = factory.generateElement("tr");

    // tickbox - all
    if (check) {
      // allow to select all records (not only visible)
      action = settings.configuration.table.select_all ?
          "check_all" : "check_all_visible";

      cell = factory.generateElement("th", {}, {}, {});
      config = {
        "type": "input",
        "direct": {
          "id": settings.portal_type_title + "_check_all",
          "className": "action"
        },
        "attributes": {
          "type": "checkbox",
          "value": "Select All/Unselect All",
          "data-iconpos": "notext",
          "data-reference": settings.base_element.direct.id,
          "data-action": action
        },
        "logic": {}
      };
      cell.appendChild(factory.generateFormElement(config, false, true));
      row.appendChild(cell);
    }

    // reverse columns so they are mergeable :-)
    if (merger) {
      target = util.reverseArray(target);
    }

    for (l = 0; l < target.length; l += 1) {
      link = undefined;
      field = target[l];
      config = {};
      property = field.title;
      field_config = {};

      if (field.show) {
        // TODO: good mapping?
        field_config = fields[field.title];

        if (field.merge === undefined) {
          if (field_config) {
            config["data-i18n"] = field_config.widget.title_i18n;
          }
          if (field.persist === undefined) {
            config["data-priority"] = field.priority || 6;
          }
          if (field_config) {
            title = temp[property] || field_config.widget.title;
          } else {
            title = property;
          }
          if (settings.configuration.table.sorting_columns && field.sort) {
            text = {};
            // sorting link
            link = factory.generateElement(
              "a",
              {
                "className": "action ui-sorting ui-btn ui-icon-sort " +
                  "ui-icon ui-btn-icon-right"
              },
              {
                "data-action": "sort",
                "data-i18n": "",
                "data-reference": settings.base_element.direct.id,
                "data-column-title": field.title
              },
              {"text": title}
            );
          } else {
            text = {
              "text": title
            };
          }
          cell = factory.generateElement(
            "th",
            {"className": "translate"},
            config,
            text
          );
          if (link) {
            cell.appendChild(link);
          }
          if (merger) {
            row.insertBefore(
              cell,
              (set === undefined ? null : row.childNodes[check ? 1 : 0])
            );
            set = true;
          } else {
            row.appendChild(cell);
          }
        } else {
          temp[field.merge] = field.merge_title;
        }
      }
    }
    table_header.appendChild(row);

    return table_header;
  };

  /*
   * Generate table rows based on configuration and data provided. Needed
   * to switch between editable and readonly table rows
   * @method generateTableRow
   * @param {object} settings Configuration for table row to create
   * @param {object} item Data for this table row
   * @returns table_row
   */
  factory.generateTableRow = function (settings, item) {
    var l,
      i,
      cell,
      property,
      field,
      link,
      value,
      logic,
      action_menu,
      action_button,
      action_controls,
      set,
      temp = {},
      row = factory.generateElement("tr"),
      target = settings.layout[0].columns,
      check = settings.configuration.table.checkbox_rows,
      merger = settings.configuration.table.mergeable_columns;

    if (check) {
      cell = factory.generateElement("th", {}, {}, {});
      cell.appendChild(
        factory.generateFormElement(
          {
            "type": "input",
            "direct": {
              "id": "select_" + item._id,
              "name": "select_" + item._id,
              "className": "action"
            },
            "attributes": {
              "type": "checkbox",
              "value": "Select item",
              "data-iconpos": "notext",
              "data-action": "check",
              "data-reference": settings.base_element.direct.id
            },
            "logic": {}
          },
          false,
          true
        )
      );
      row.appendChild(cell);
    }

    // reverse if mergable columns
    if (merger) {
      target = util.reverseArray(target);
    }

    // loop fields to display
    for (l = 0; l < target.length; l += 1) {
      field = target[l];
      property = field.title;
      value = item[property];

      if (field.show) {
        if (field.merge === undefined) {
          cell = factory.generateElement("td", {}, {}, {});
          // TODO: links should reflect value but communicate key aswell
          link = "#" + settings.portal_type_title + "::" + item._id;

          // TODO: crap...refactor whole section
          // fetch non portal_type values
//           if (value === undefined && field.action === false) {
//             // TODO: bah
//             // fetchValue = priv.getERP5property(item._id, field.lookup);
//             if (fetchValue.error) {
//               value = "N/A";
//             }
//           }

          if (field.actions) {
            action_controls = {
              "direction": "horizontal",
              "class": "",
              "buttons": []
            };
            for (i = 0; i < field.actions.length; i += 1) {
              action_button = factory.map_buttons[field.actions[i]];
              if (action_button) {
                action_controls.buttons.push({
                  "type": "a",
                  "direct": {
                    "href": action_button.href,
                    "className": action_button.classes +
                        " translate ui-btn ui-btn-icon-notext " +
                            "ui-shadow ui-corner-all ui-icon-" +
                                action_button.icon
                  },
                  "attributes": {
                    "data-enhanced": "true",
                    "data-i18n": action_button.text_i18n,
                    "data-action": field.actions[i]
                  },
                  "logic": {
                    "text": action_button.text
                  }
                });
              }
            }
            action_menu = factory.generateControlgroup(action_controls);
            cell.appendChild(action_menu);
          } else if (field.status) {
            cell.appendChild(factory.generateElement(
              "a",
              {
                "href": link,
                "className": "status error ui-btn-inline ui-btn " +
                    " translate responsive ui-btn-icon-left ui-shadow " +
                        " ui-corner-all ui-icon-bolt"
              },
              {
                "data-i18n": "[title:" + item.status.message_i18n + ";" +
                    item.status.error_i18n + "]",
                "data-icon": "bolt",
                "title": item.status.message
              },
              {"text": item.status.state}
            ));
          } else {
            // default
            if (field.image) {
              logic = {
                "img": item.image
              };
            } else {
              // TODO: lame merge
              if (temp[property]) {
                value += " " + temp[property];
                //delete temp[property];
              }
              logic = {
                "text": value
              };
            }

            // TODO: a link in every cell? binding?
            // don't touch this just for some status
            if (settings.configuration.table.linkable_rows) {
              cell.appendChild(factory.generateElement(
                "a",
                {"className": "table_link", "href": link},
                {},
                logic
              ));
            } else {
              cell.appendChild(factory.generateElement("span", {}, {}, logic));
            }
          }
          // Grrr...
          if (merger) {
            row.insertBefore(cell, (set === undefined ?
                undefined : row.childNodes[check ? 1 : 0]));
            set = true;
          } else {
            row.appendChild(cell);
          }
        } else {
          // keep the value of cells to be merged
          temp[field.merge] = value;
        }
      }
    }
    return row;
  };

  /*
   * Generates a table body based on configuration and data provided from JIO
   * @method generateTableBody
   * @param {object} settings Configuration for table body to create
   * @param {object} answer from JIO
   * @returns {object} table_body
   */
  factory.generateTableBody = function (settings, answer) {
    var l,
      row,
      item,
      error,
      max,
      table_body = factory.generateElement("tbody", {}, {
        "data-update": "true"
      });

    if (answer && answer.data.total_rows > 0) {
      max = answer.data.total_rows;

      for (l = 0; l < max; l += 1) {
        item = answer.data.rows[l].doc;
        row = factory.generateTableRow(settings, item);
        table_body.appendChild(row);
      }
    } else {
      // error or 0 results
      row = factory.generateElement("tr");
      l = settings.layout[0].columns.length;

      if (answer === undefined) {
        error = "Error retrieving Data";
      } else if (answer.data.total_rows === 0) {
        error = "No records found. Please modify your search!";
      } else {
        error = "Internal error generating gadget";
      }

      if (settings.configuration.table.checkbox_rows) {
        l += 1;
      }

      row.appendChild(factory.generateElement(
        "th",
        {"style": "text-align: center; line-height: 2em;"},
        {"colspan": l},
        {"text": error}
      ));
      table_body.appendChild(row);
    }
    return table_body;
  };

  /* ********************************************************************** */
  /*                         JQM Form Element                               */
  /* ********************************************************************** */
  /**
   * Generates an enhanced JQM form element
   * @method generateFormElement
   * @param {object} config Form field configuration object
   * @param {boolean} wrap Wrap the field in a fieldcontainer
   * @param {boolean} label Show the label for this field
   * @param {boolean} position First = true Last = false;
   * @return {object} HTML fragment
   */
  // TODO: Are actions flexible with a mapper?
  // TODO: clean up once working...
  // TODO: mini? shadow? corners?
  // TODO: slider/custom-select/flip
  // TODO: refactor...
  // TODO: placeholder?
  factory.generateFormElement = function (config, wrap, label, position) {
    var wrapper, container, wrap_in_container, element_reverse,
      label_inside, label_target, element_target, action, clear, map,
      theme, icon_string, input_type, need_text_node, container_class_list,
      label_class_list, index, disabled, active, text, addLabel, readonly;

    // preset
    container_class_list = "";
    label_class_list = "";
    index = "";
    disabled = "";
    readonly = "";
    active = "off";
    text = "text";

    // helper
    addLabel = function (config, label_class_list) {
      return factory.generateElement(
        "label",
        {
          "className": label_class_list + " translate" +
            ((label === undefined || config.logic.text === "") ?
                " ui-hidden-accessible" : "")
        },
        {"for": config.direct.id, "data-i18n": config.logic.label_i18n || ""},
        {"text": config.logic.label || ""}
      );
    };

    // shim missing logic
    if (config.logic === undefined) {
      config.logic = {};
    }

    // first/last in group of elements
    if (position) {
      switch (position) {
      case null:
        index = " ui-first-child ui-last-child ";
        break;
      case true:
        index = " ui-first-child ";
        break;
      case false:
        index = " ui-last-child ";
        break;
      }
    }

    // theme
    if (config.attributes["data-theme"] !== undefined) {
      theme = " ui-btn-" + config.attributes["data-theme"];
    }

    // enhanced!
    config.attributes["data-enhanced"] = true;

    // form field attributes
    if (config.direct.checked) {
      active = "on";
    }
    if (config.attributes.disabled) {
      disabled = " ui-disabled";
    }
    if (config.attributes.readonly) {
      readonly = " ui-readonly";
    }

    // fieldcontain wrapper
    if (wrap === false || wrap === undefined) {
      wrapper = document.createDocumentFragment();
    } else {
      wrapper = factory.generateElement(
        "div",
        {"className": "ui-fieldcontain translate"},
        {
          "title": config.logic.title || "",
          "data-i18n": "[title]" + (config.logic.title_i18n || "")
        }
      );
    }

    // attribute/class generator
    if (config.type === "textarea") {
      config.direct.className += " ui-input-text ui-shadow-inset " +
        "ui-body-inherit ui-corner-all" + disabled;
    }

    // action/clear button
    if (config.logic.action) {
      map = factory.map_buttons[config.logic.action];
      action = " ui-input-has-action ui-input-search-no-pseudo";
      config.direct.className += map.classes;
      config.attributes["data-action-btn"] = "true";
    }
    if (config.logic.clear) {
      clear = " ui-input-has-clear";
      config.attributes["data-clear-btn"] = "true";
    }

    // label position and class
    input_type = config.attributes.type;

    if (input_type) {
      switch (input_type) {
      case "radio":
        container_class_list = "ui-" + config.attributes.type;
        label_inside = true;
        label_class_list = "ui-btn ui-corner-all ui-btn-inherit" +
          " ui-btn-icon-left ui-icon-radio-" + active + " ui-radio-" +
          active + index + disabled + readonly;
        config.attributes["data-cacheval"] = true;
        break;
      case "checkbox":
        icon_string = factory.generateIconClassString(config, "checkbox");
        container_class_list = "ui-" + config.attributes.type;
        label_inside = true;
        label_class_list = "ui-btn ui-corner-all ui-btn-inherit " +
          icon_string + " ui-checkbox-" + active + index + disabled + readonly;
        config.attributes["data-cacheval"] = false;
        break;
      case "submit":
      case "reset":
        container_class_list = "ui-btn ui-input-btn";
        need_text_node = true;
        break;
        // covers all JQM text input types and excludes select/textarea...
      default:
        if (input_type !== "hidden") {
          if (input_type === "search") {
            // need to add all data-attributes...
            config.attributes["data-type"] = "search";
            text = "search";
          }
          container_class_list = "ui-input-" + text + " ui-body-inherit ";
        }
        break;
      }
    }
    // assemble
    container_class_list += " ui-corner-all ui-shadow-inset" +
      disabled + readonly + (action || "") + (clear || "") + (theme || "");

    // container
    if (config.type === "textarea" || config.logic.type === "hidden") {
      container = wrapper;
    } else {
      wrap_in_container = true;
    }

    // select
    if (config.type === "select") {
      icon_string = factory.generateIconClassString(config);
      container_class_list = "ui-" + config.type;
      element_target = factory.generateElement(
        "div",
        {
          "id": config.direct.id + "-button",
          "className": icon_string + " ui-btn ui-corner-all ui-shadow " +
              (config.logic.wrapper_class_list || "")
        },
        {"data-enhanced": "true"}
      );
      element_reverse = true;
    }

    // queued commands (need container_class_list to be set)
    if (wrap_in_container) {
      container = factory.generateElement(
        "div",
        {"className": container_class_list}
      );
    }
    if (label_inside) {
      label_target = container;
    } else {
      label_target = wrapper;
    }

    // NOTE: always label for validity, "no label" means "hide it" not "skip"!
    // NOTE: no label for submit/reset because we don't need an id/name
    // NOTE: for checkboxRadio validation, the label needs to be AFTER
    // the input, otherwise CSS sibling selector will not work. This saves
    // doing "invalid" handler with javascript
    if (need_text_node === undefined && !label_inside) {
      label_target.appendChild(addLabel(config, label_class_list));
    }

    // target
    if (element_reverse) {
      element_target.appendChild(factory.generateElement("span"));
    } else {
      element_target = container;
    }

    // text node
    if (need_text_node) {
      element_target.appendChild(document.createTextNode(config.direct.value));
    }

    // ELEMENT
    element_target.appendChild(factory.generateElement(
      config.type,
      config.direct,
      config.attributes,
      config.logic
    ));

    // checkbox radio gets label after input
    if (label_inside) {
      label_target.appendChild(addLabel(config, label_class_list));
    }

    // reassemble select elements and add spans
    if (element_reverse) {
      container.appendChild(element_target);
    }

    // clear button
    if (config.logic.clear) {
      container.appendChild(factory.generateElement(
        "a",
        {
          "title": "Clear",
          "className": "ui-input-clear ui-btn ui-icon-delete translate " +
            "ui-btn-icon-notext ui-corner-all ui-input-clear-hidden",
          "href": "#"
        },
        {"data-i18n": "global.actions.clear", "tabindex": "-1"},
        {"text": "Clear"}
      ));
    }
    // action button
    if (config.logic.action) {
      container.appendChild(factory.generateElement(
        "a",
        {
          "title": map.text,
          "className": "action ui-input-action ui-btn ui-icon-search " +
            "ui-btn-icon-notext ui-corner-all translate ",
          "href": map.href || "#"
        },
        {
          "data-i18n": map.text_i18n,
          "tabindex": "-1",
          "data-action": map.text.toLowerCase()
        },
        {"data-rel": map.rel || undefined, "text": map.text}
      ));
    }

    // wrap up
    if (wrap_in_container) {
      wrapper.appendChild(container);
    } else {
      wrapper = container;
    }

    // done
    return wrapper;
  };




  /* ********************************************************************** */
  /*                      Class String Generator                            */
  /* ********************************************************************** */
  /**
   * Generate a string for icon and iconpos on any JQM element
   * generateIconClassString
   * @param {object} element Configuration
   * @param {string} default_icon Icon to pass as default
   * @return {string} finished class snippet
   */
  factory.generateIconClassString = function (element, default_icon) {
    var def,
      string = "",
      iconpos = element.attributes["data-iconpos"],
      icon = element.attributes["data-icon"] || default_icon;

    if (icon) {
      string += " ui-icon-" + icon.replace("data-", "");

      if (iconpos) {
        def = iconpos.replace("data-", "");
      }
      string += " ui-btn-icon-" + (def || "left");
    }
    return string;
  };

  /* ********************************************************************** */
  /*                      Plain Element Generation                          */
  /* ********************************************************************** */
  /**
   * Generates elements based on supplied configuration
   * @method: generateElement
   * @param: {type} string Type of element to generate
   * @param: {object} options Parameters settable directly (id, name, value..)
   * @param: {object} attributes Parameters settable with setAttribute
   * @param: {object} setters Parameters requiring logic (if-else-etc)
   * @returns: {object} HTML object
   */
  // TODO: bundle into spec!
  factory.generateElement = function (type, options, attributes, setters) {
    var property,
      attribute,
      data,
      i,
      mock,
      recurse,
      pic,
      element = document.createElement(type);

    // directly settable
    for (property in options) {
      if (options.hasOwnProperty(property)) {
        element[property] = options[property];
      }
    }
    for (data in attributes) {
      if (attributes.hasOwnProperty(data)) {
        element.setAttribute(data, attributes[data]);
      }
    }

    // requiring logic to be set
    // TODO: optgroup
    for (attribute in setters) {
      if (setters.hasOwnProperty(attribute)) {
        mock = attribute.slice(0, 5) === "data-" ? "data-" : attribute;
        switch (mock) {
        case "disabled":
        case "selected":
          if (setters[attribute]) {
            element.setAttribute(attribute, attribute);
          }
          break;
        case "id":
        case "rows":
        case "cols":
        case "name":
        case "value":
        case "data-":
        case "role":
        case "type":
        case "rel":
        case "readonly":
        case "size":
          if (setters[attribute]) {
            element.setAttribute(attribute, setters[attribute]);
          }
          break;
        case "text":
          element.appendChild(document.createTextNode(setters.text));
          break;
        case "img":
          pic = setters.img;
          element.appendChild(factory.generateElement(
            "img",
            {"src": pic.href, "alt": pic.alt}
          ));
          break;
        case "options":
          // TODO: optgroup!!!
          if (setters.options) {
            for (i = 0; i < setters.options.length; i += 1) {
              recurse = setters.options[i];
              element.appendChild(
                factory.generateElement(
                  "option",
                  {
                    "className": (recurse.text_i18n ? "translate" : ""),
                    "value": recurse.value
                  },
                  {"data-i18n": recurse.text_i18n || ""},
                  {
                    "text": recurse.text,
                    "selected": recurse.selected,
                    "disabled": recurse.disabled
                  }
                )
              );
            }
          }
          break;
        case "extra":
          // WARNING: uses JSON not HTML!!!
          if (typeof setters.extra !== "string") {
            for (recurse in setters.extra) {
              if (setters.extra.hasOwnProperty(recurse)) {
                element.setAttribute(recurse, setters.extra[recurse]);
              }
            }
          }
          break;
        case "grid":
          for (i = 0; i < setters.grid; i += 1) {
            element.appendChild(factory.generateElement("div"));
          }
          break;
        }
      }
    }

    return element;
  };

  /* ====================================================================== */
  /*                               UTILS                                    */
  /* ====================================================================== */

  /**
   * Load content into a global or local popup
   * @method loadPopupContents
   * @param {obj} object Action object (popupbeforeposition)
   */
  util.loadPopupContents = function (obj) {
    var fragment,
      popup = obj.gadget,
      reference = popup.getAttribute("data-reference"),
      state = popup.getAttribute("data-state");

    // TODO: caching!
    // don't reload if same popup is opened
    if (state !== reference) {
      if (reference === null) {
        util.errorHandler({
          "Error": "Global Bindings: No handler for popup"
        });
        fragment = factory.generateElement(
          "p",
          {},
          {},
          {"text": "No handler for popup"}
        );
      } else {
        // TODO: where to load the content from!?!
        if (init[reference]) {
          fragment = init[reference]();
        } else {
          util.errorHandler({
            "Error": "Global Bindings: No content for popup"
          });
          fragment = factory.generateElement(
            "p",
            {},
            {},
            {"text": "No content for popup"}
          );
        }
        popup.setAttribute("data-state", reference);
        popup.setAttribute("data-reference", reference);
      }

      // apply jQuery make-up
      $(popup).empty().append(fragment).enhanceWithin();
    }

  };

  /**
   * Identify popup that will open and set content to be loaded
   * @method setPopupContentPointer
   * @param {obj} obj Action Object
   * @param {string} pointer Pointer to set to
   */
  // TODO: set state on the popup, state should include cached content?
  util.setPopupContentPointer = function (obj, pointer) {
    if (obj.gadget.getAttribute("data-reference") === pointer) {
      return;
    }
    obj.gadget.setAttribute("data-reference", pointer);
  };

  /**
   * Get the active JQM page in JavaScript-only
   * @method getActivePageId
   * @return {string} id of active page
   */
  util.getActivePage = function () {
    var i, kid, kids = document.body.children;

    // reverse, because in JQM last page is the active page!
    for (i = kids.length - 1; i >= 0; i -= 1) {
      kid = kids[i];

      if (kid.tagName === "DIV") {
        if (util.testForClass(kid.className, "ui-page")) {
          return kid.id || kid.getAttribute("data-module");
        }
      }
    }
    return undefined;
  };

  /**
   * Filter a string for a class name
   * @method filterForClass
   * @param  {string} class The string to filter
   * @return {object} regex
   */
  util.filterForClass = function (className) {
    return new RegExp("(?:^|\\s)" + className + "(?!\\S)", "g");
  };

  /**
   * Reverse an array
   * @method reverseArray
   * @param {array} array Array to reverse
   * @returns {array} keys Reversed array
   */
  util.reverseArray = function (array) {
    var k, keys = [];

    for (k = 0; k < array.length; k += 1) {
      keys.unshift(array[k]);
    }
    return keys;
  };

  /**
   * Delete an element from an array
   * @method deleteFromArray
   * @param {array} array Original array
   * @param {string} element Element to remove
   * @return {array} new array
   */
  util.deleteFromArray = function (array, element) {
    var i;

    for (i = 0; i <= array.length; i += 1) {
      if (array[i] === element) {
        return array.splice(i, 1);
      }
    }
    return array;
  };

  /**
   * Convert 1,2,3 into a,b,c
   * @method: toLetters
   * @param: {number} number Number to convert
   * @return: {string} letter
   */
  util.toLetter = function (number) {
    return String.fromCharCode(97 + ((number - 1) % 26));
  };

  /**
   * Test for a class name
   * @method testForClass
   * @param {string} classString The string to test
   * @param {string} test The class to test against
   * @return {boolean} result True/False
   */
  // WARNING: requires IE8- requires shim
  util.testForClass = function (classString, test) {
    return (" " + classString + " ").indexOf(" " + test + " ") > -1;
  };

  /*
   * Return
   * @method return
   */
  util.return_out = function () {
    return;
  };

  /**
   * Fetch a configuration file (attachment) from storage. Fallback to
   * disk. Successfull fallback file fetches will be stored in JIO.
   * @method fetchConfiguration
   * @param {object} parcel parameters & baggage to pass to subsequent then()
   * @return {object} object including baggage and reply
   */
  util.fetchPortalTypeConfiguration = function (parcel) {
    //storage, file, attachment, baggage
    var store = init.storages[parcel.storage];

    return store.getAttachment({
      "_id": parcel.file,
      "_attachment": parcel.attachment
    })
      .then(function (response) {
        return jIO.util.readBlobAsText(response.data);
      })
      .then(
        function (answer) {
          return {
            "response": JSON.parse(answer.target.result),
            "baggage": parcel.baggage
          };
        },
        function (error) {
          if (error.status === 404 && error.id === parcel.file) {
            return util.getFromDisk({
              "store": store,
              "file": parcel.file,
              "attachment": parcel.attachment,
              "baggage": parcel.baggage
            })
              .then(function (reply) {
                return {
                  "response": util.parseIfNeeded(reply.response),
                  "baggage": reply.baggage
                };
              });
          }
          throw error;
        }
      );
  };

  /**
   * load files into JIO that are missing
   * @method getFromDisk
   * @param {object} parcel parameters & baggage to pass to subsequent then()
   * @return {object} object including baggage and reply
   */
  util.getFromDisk = function (parcel) {
    var response,
      put = function (e) {
        response = util.parseIfNeeded(e.target.responseText);
        return parcel.store.put({
          "_id": parcel.file
        });
      },
      putAttachment = function () {
        return parcel.store.putAttachment({
          "_id": parcel.file,
          "_attachment": parcel.attachment,
          "_data": JSON.stringify(response),
          "_mimetype": "application/json"
        });
      },
      url = "data/" + parcel.attachment + ".json";

    return jIO.util
      .ajax({
        "url": url
      })
      .then(put)
      .then(putAttachment)
      .then(function () {
        // stored in JIO, continue
        return {
          "response": response,
          "baggage": parcel.baggage
        };
      })
      .fail(util.errorHandler);
  };

  /**
   * Try fetching data from JIO. Fallback to loading fake data until accessible
   * @method fetchData
   * @param {object} parcel Storage, query options and baggage to return
   * @return {object} promise object/baggage
   */
  // NOTE: until we have real data we load fake data on application init!
  util.fetchData = function (parcel) {
    return init.storages[parcel.storage].allDocs(parcel.query)
      .then(function (response) {
        return {
          "response": response,
          "baggage": parcel.baggage
        };
      });
  };

  /**
   * remove trailing slash on a url
   * @method removeTrailingSlash
   * @param {string} url
   * @return {url} cleaned url
   */
  util.removeTrailingSlash = function (url) {
    if (url.substr(-1) === "/") {
      return url.substr(0, url.length - 1);
    }
    return url;
  };

  /**
   * parse a link into query-able parameters
   * @method parseLink
   * @param {string} url Url to go to
   * @return {object} pointer object
   */
  // TODO: renderJS should parse a link
  util.parseLink = function (url) {
    var i,
      query,
      parameter,
      path = $.mobile.path.parseUrl(url),
      clean_hash = path.hash.replace("#", ""),
      config = {
        "url": url
      };

    if (path.hash === "") {
      config.id = config.layout_identifier = util.getActivePage();
    } else {
      // do we have a mode?
      query = clean_hash.split("?");

      for (i = 0; i < query.length; i += 1) {
        parameter = query[i].split("=");
        if (parameter.length === 2 && parameter[0] === "mode") {
          config.mode = parameter[1];
        }
      }

      config.fragment_list = clean_hash.split("::");
      config.id = clean_hash;
      config.layout_level = config.fragment_list.length - 1;
      config.deeplink = true;
      config.layout_identifier = clean_hash.split("::")[0];
    }

    return config;
  };

  /**
   * parse to JSON if element is not in JSON
   * @parseIfNeeded
   * @param {object/string} data Data to parse
   * @return {object} object Parsed object
   */
  util.parseIfNeeded = function (data) {
    if (typeof data === "string") {
      return JSON.parse(data);
    }
    return data;
  };

  /* ====================================================================== */
  /*                             ERROR HANDLER                              */
  /* ====================================================================== */
  /**
   * Capture errors, log to console and trigger bugticker
   * @method errorHandler
   * @param {object} err  Error object
   */
  // TODO: elaborate... throw? send a ticket? update status?
  util.errorHandler = function (err) {
    console.log(err);
  };

  /* ====================================================================== */
  /*                               METHODS                                  */
  /* ====================================================================== */

  /**
   * Build a JIO query object based on passed configuration
   * @method buildQuery
   * @param {object} config JSON parameters for query object
   * @param {string} type Portal Type to fetch
   * @param {string} key Parameter to search for single element
   * @param {string} value Value of single parameter
   * @return {object} query object
   */
  // TODO: bundle all query object construction here
  init.generateQueryObject = function (config, type, key, value) {
    var parameter,
      query_input = config || {},
      obj = {};

    // we must always query the portal type?
    obj.query = '(portal_type:"%' + type + '")';

    // TODO: this is crap, make more generic
    if (query_input.filter_list) {
      for (parameter in query_input.filter_list) {
        if (query_input.filter_list.hasOwnProperty(parameter)) {
          obj.query += ' AND (' +
            parameter + ':"' + query_input.filter_list[parameter] + '")';
        }
      }
    }

    if (query_input.sort) {
      obj.sort_on = [query_input.sort];
    } else {
      // TODO: which id or _id?
      // TODO: this requires pre-setting the column states!!!
      // TODO: what if sorting by a column which is not shown... this is crap
      // obj.sort_on = [['id','ascending']];
      obj.sort_on = [];
    }
    if (query_input.include_documents || value) {
      obj.include_docs = true;
    }
    if (query_input.columns && query_input.columns.length > 0) {
      obj.select_list = query_input.columns;
    }
    if (query_input.limit) {
      obj.start = query_input.limit[0];
      obj.items = query_input.limit[1];
    }
    if (value) {
      obj.query += ' AND (' + key + ':"' + value + '")';
      obj.start = 0;
      obj.items = 1;
    }
    if (obj.start !== undefined) {
      obj.limit = [obj.start, obj.items];
    } else {
      obj.limit = [];
    }
    if (query_input.wildcard) {
      obj.wildcard_character = query_input.wildcard;
    } else {
      obj.wildcard_character = "%";
    }
    return obj;
  };

  /**
   * Update info fields (field displaying some sort of information
   * @method "
   * @param {object} element Element containing info fields
   * @param {object} options Query object used to get records
   * @param {integer} total Total Records
   * @param {integer} selected Total Records currently selected
   */
  init.updateInfoFields = function (element, options, total, selected) {
    var j,
      k,
      reference,
      info_fields,
      info_field,
      info,
      min,
      select_counter;

    // WARNING: IE8- and performance?
    // WARNING: element = documentFragment, can only be searched via QSA!
    info_fields = element.querySelectorAll(".info");

    for (j = 0; j < info_fields.length; j += 1) {
      info_field = info_fields[j];

      // TODO: how to i18n this?
      // TODO: what is more costly? repaint or reset values on every call?
      // TODO: remove this to ERP5 handler
      switch (info_field.getAttribute("data-info")) {
      case "records":
        if (total && total > 0) {
          min = Math.min(total, (options.limit[0] + options.limit[1]));
          info = options.limit[0] + "-" + min + "/" + total + " Records";
        }
        break;
      case "selected":
        select_counter = 0;
        if (selected) {
          if (selected[0] === "all") {
            select_counter = total;
          } else {
            select_counter = selected.length;
          }
        }
        info = select_counter + " item(s) selected";
        break;
      case "filter":
        if (options.query !== undefined) {
          reference = complex_queries.parseStringToObject(
            options.query
          );
          if (reference === "object") {
            info = "Search = " + reference.key.replace("_", " ") + ": " +
              reference.value.replace("%", "");
          } else {
            info = "Search = ";
            for (k = 0; k < reference.length; k += 1) {
              info += reference[k].key.replace("_", " ") + ": " +
                reference[k].value.replace("%", "");
              if (k >= 1 && k < reference.length) {
                info += ", ";
              }
            }
          }
        }
        break;
      }
      info_field.innerHTML = info;
    }
  };


  /**
   * Generate an action object (vs duplicate in every action call)
   * @method generateActionObject
   * @param {object} e Event triggering an action
   * @return {object} action object
   */
  // TODO: integrate in popup handler, make sure "pop" works!
  // TODO: id ... is crap
  init.generateActionObject = function (e) {
    var element, pop, id, gadget;
    switch (e.type) {
    case "popupbeforeposition":
      element = undefined;
      id = e.target.id;
      gadget = e.target;
      break;
    default:
      element = e.target || e;
      pop = element.getAttribute("data-rel") === null;
      id = pop ?
          (element.getAttribute("data-reference") || util.getActivePage()) :
              (element.href === undefined ? util.getActivePage() :
                  element.href.split("#")[1]);
      gadget = document.getElementById(id);
      break;
    }

    return {
      "element": element,
      "id": id,
      "gadget": document.getElementById(id),
      "state": gadget.state
    };
  };

  /**
   * Highlight checkboxes and set a state on items selected
   * @method check
   * @param {object} config Action Object
   * @param {boolean} all Boolean determining whether to check all records
   */
  //TODO: promisable?
  init.check = function (config, all) {
    var i,
      rows,
      checks,
      check,
      checked_or_not,
      id,
      state,
      ids;

    state = config.state;
    checked_or_not = config.element.checked;
    id = config.element.id.replace("select_", "");

    if (config && state.selected === undefined) {
      state.selected = [];
    }

    if (all !== undefined) {
      ids = [];
      rows = config.gadget
        .getElementsByTagName("TBODY")[0]
        .getElementsByTagName("TR");

      for (i = 0; i < rows.length; i += 1) {
        // assumes there is only one checkbox in a first cell
        checks = rows[i].childNodes[0].getElementsByTagName("INPUT");

        if (checks.length > 0) {
          check = checks[0];
          if (check.type === "checkbox") {
            // status is communicated via action object
            check.checked = checked_or_not;
            ids.push(check.id);
            // need to JQM refresh...
            $(check).checkboxradio("refresh");
          }
        }
      }
      // override if indeterminate to select ALL (not only visible)
      if (config.element.indeterminate) {
        ids = ["all"];
      }
    }

    if (checked_or_not === false) {
      if (all === undefined) {
        util.deleteFromArray(state.selected, id);
      } else {
        state.selected = [];
      }
    } else {
      if (all === undefined) {
        state.selected.push(id);
      } else {
        state.selected = ids;
      }
    }

    // update gadget state
    config.gadget.state = {
      "gadget": state.gadget,
      "query": state.query,
      "total": state.total,
      "method": state.method,
      "selected": state.selected
    };

    // update info fields
    init.updateInfoFields(
      config.gadget.parentNode,
      state.query,
      state.total,
      state.selected
    );
  };

  /**
   * Action handler, routing actions to specified method
   * @method action
   * @param {object} e Event that triggered the action
   */
  init.action = function (e) {
    var type, tag, val, action, handler;

    type = e.type;
    tag = e.target.tagName;

    if (type === "click" && e.target.getAttribute("data-rel") === null) {
      e.preventDefault();
      if (type === "click" && (tag === "SELECT" ||
        (tag === "INPUT" && e.target.type !== "submit"))) {
        return;
      }
    }
    if (type === "change" && tag === "SELECT") {
      val = e.target.options[e.target.selectedIndex].value;
    }
    // JQM bug on selects
    // TODO: remove once fixed
    if (tag === "SPAN" || tag === "OPTION") {
      return;
    }
    // map
    action = e.target.getAttribute("data-action");
    handler = factory.map_actions[action];

    if (action) {
      if (handler) {
        handler(init.generateActionObject(e), val);
      } else {
        util.errorHandler({
          "Error": "Action: No method defined"
        });
      }
    } else {
      util.errorHandler({
        "Error": "Action: No action defined for element"
      });
    }
  };

  /**
   * Sort a selection of elements
   * @sort
   * @param {object} e Event triggering the sort action
   * @param {string} direction Direction to sort
   * @param {string} prev Previous icon
   * @param {string} next Next icon
   */
  // TODO: move this into a common JIO function generateQueryObject!
  init.sort = function (config, direction, prev, next) {
    var i, in_array, column;

    column = config.element.getAttribute("data-column-title");

    // change button right away
    config.element.setAttribute("data-direction", direction);
    config.element.setAttribute("data-icon", next);
    config.element.className = config.element.className.replace(
      util.filterForClass("ui-icon-" + prev),
      " ui-icon-" + next
    );

    // trigger sort after 500ms delay, so user can pick sorting criteria
    if (init.timer) {
      window.clearTimeout(init.timer);
      init.timer = 0;
    }

    for (i = 0; i < config.state.query.sort_on.length; i += 1) {
      if (config.state.query.sort_on[i][0] === column) {
        in_array = true;
        //current = config.state.query.sort_on[i][1];
        break;
      }
    }

    // need to make sure, that we not overwrite existing sortings!
    // also check to not overwrite
    switch (direction) {
    case "desc_123":
    case "desc_abc":
      if (column) {
        if (in_array === undefined) {
          config.state.query.sort_on.push([column, "descending"]);
        } else {
          config.state.query.sort_on.splice(i, 1)
            .push([column, "descending"]);
        }
      }
      break;
    case "asc_123":
    case "asc_abc":
      if (column) {
        if (in_array === undefined) {
          config.state.query.sort_on.push([column, "ascending"]);
        } else {
          config.state.query.sort_on.splice(i, 1)
            .push([column, "ascending"]);
        }
      }
      break;
    default:
      // need to remove a column from sorting when set to undefined
      if (column && in_array) {
        config.state.query.sort_on.splice(i, 1);
      }
      break;
    }

    // give user half second to pick his state
    init.timer = window.setTimeout(function () {
      // update gadgets
      init.setPageElements({}, {
        "response": [{
          "section_list": [{
            "gadget": config.id
          }]
        }]
      }, false);
      init.timer = 0;
    }, 500);
  };

  /**
   * Handler for search
   * @method search
   * @param {object} config Action Object
   */
  // TODO: move into JIO method generateQueryObject
  init.search = function (config) {
    var value = config.element.value;

    // need to search all columns for this value
    util.fetchPortalTypeConfiguration({
      "storage": "settings",
      "file": "gadgets",
      "attachment": config.id,
      "baggage": undefined
    })
      .then(function (configuration) {
        var i, field, query, columns, not_first;

        query = config.state.query.query;
        columns = configuration.response.layout[0].columns;

        // trying to handle all cases
        // NOTE: we always query for the portal_type first, so empty search
        // will still query for portal_type!
        query = query.split(' AND ')[0];
        if (value !== "") {
          query += ' AND ';
          for (i = 0; i < columns.length; i += 1) {
            field = columns[i];
            if (i === 0) {
              query += '(';
            }
            if (field.show && field.custom === undefined) {
              if (not_first) {
                query += ' OR ';
              }
              query += field.title + ':"%' + value + '%"';
              not_first = true;
            }
            if (i === columns.length - 1) {
              query += ')';
            }
          }
        }
        config.state.query.query = query;

        // we only want x records

        // update gadget
        init.setPageElements({}, {
          "response": [{
            "section_list": [{
              "gadget": config.id
            }]
          }]
        }, false);
      })
      .fail(util.errorHandler);
  };

  /**
   * Handler for form submission to add a new item
   * @method add
   * @param {object} config Action Object
   */
  // NOTE: we always validate! to skip validation test for class on form
  // TODO: spam protect
  init.add = function (config) {
    var property,
      replace,
      form_element = document.getElementById(config.id),
      formData = new FormData(),
      valid = $(form_element).triggerHandler("submitForm");

    if (valid !== false) {
      replace = form_element.id.split("_")[0] + "_";

      for (property in valid) {
        if (valid.hasOwnProperty(property)) {
          formData.append(property.replace(replace, ""), valid[property]);
        }
      }

      // report to ERP5
      jIO.util
        .ajax({
          "url": "https://nexedi.erp5.net/" +
              "ERP5Site_addApplicationSubmissionRequest",
          "type": "POST",
          "data": formData
        });
    }
  };

  /**
   * Handler for pagination
   * @method paginate
   * @param {object} config Action Object
   * @param {string} type Where to paginate to
   * @param {string} value New limit when changing number of records
   */
  // TODO: move into JIO method generateQueryObject
  init.paginate = function (config, type, value) {
    var start, records;

    if (config.gadget) {
      if (config.state) {
        switch (type) {
        case "first":
          start = 0;
          records = config.state.query.limit[1];
          break;
        case "next":
          start = config.state.query.limit[0] + config.state.query.limit[1];
          records = config.state.query.limit[1];
          break;
        case "prev":
          start = config.state.query.limit[0] - config.state.query.limit[1];
          records = config.state.query.limit[1];
          break;
        case "last":
          start = config.state.total - config.state.query.limit[1];
          records = config.state.query.limit[1];
          break;
        case "limit":
          start = config.state.query.limit[0];
          records = parseInt(value, null);
          break;
        }

        if (start > config.state.total || start < 0) {
          return;
        }

        // set new limits
        config.state.query.limit = [start, records];

        // update gadget
        init.setPageElements({}, {
          "response": [{
            "section_list": [{
              "gadget": config.id
            }]
          }]
        }, false);
      } else {
        util.errorHandler({
          "Error": "No state information stored for gadget"
        });
      }
    } else {
      util.errorHandler({
        "Error": "Action is missing reference gadget"
      });
    }
  };

  /* ====================================================================== */
  /*                                PAGE SETUP                              */
  /* ====================================================================== */

  /**
   * Update a page (which may already be in the DOM)
   * @method updatePage
   * @param {object} e Event (pagebeforechange)
   * @param {object} data Data passed along with this (JQM) event
   */
  // TODO: awful selector!
  // NOTE: removed data for JSLINT form parameters
  init.updatePage = function (e) {
    var page = e.target;

    init.fetchPageLayouts("settings", page.id)
      .then(function (reply) {
        //init.setPageTitle(page, util.parseIfNeeded(reply.response[0]));
        if (!page.querySelectorAll("div.ui-content")[0]
            .getAttribute("data-bound")) {
          return init.setPageElements({
            "id": page.id
          }, reply, undefined);
        }
      })
      .fail(util.errorHandler);
  };

  /**
   * Set the page title
   * @method setPageTitle
   * @param {object} page Page
   * @param {object} spec Config of page being loaded
   */
  init.setPageTitle = function (page, spec) {
    var header, title;

    if (page === undefined) {
      util.errorHandler({
        "error": "Set Title: Missing page"
      });
    } else {
      // find header
      // WARNING: IE8- children() retrieves comments, too
      header = document.getElementById("global_header") || page.children()[0];

      if (util.testForClass(header.className, "ui-header")) {
        title = header.getElementsByTagName("h1")[0];
        title.setAttribute("data-i18n", (spec.title_i18n || ""));
        title.removeChild(title.childNodes[0]);
        title.appendChild(document.createTextNode((spec.title || "\u00A0")));
      }
    }
  };

  /**
   * Prevent filterable from triggering
   * @method preventFilterableTrigger
   * @params {object} element Filterable element
   */
  // TODO: make sure this triggers only once!
  init.preventFilterableTrigger = function (element) {
    $(element).on("filterablebeforefilter", function (e) {
      e.preventDefault();
    });
  };

  /**
   * Set bindings on page specific elements after content has been appended
   * @method setPageBindings
   */
  // TODO: add local popups!
  init.setPageBindings = function () {
    var i,
      j,
      form_element,
      filterable,
      form_list = document.getElementsByTagName("form"),
      filter_list = document.querySelectorAll("[data-filter]");

    // disable default filtering of JQM filterable
    for (i = 0; i < filter_list.length; i += 1) {
      filterable = filter_list[i];

      if (filterable.getAttribute("data-bound") === null) {
        filterable.setAttribute("data-bound", true);
        init.preventFilterableTrigger(filterable);
      }
    }

    // add validation to all forms
    for (j = 0; j < form_list.length; j += 1) {
      form_element = form_list[j];
      if (form_element.getAttribute("data-bound") === null) {
        form_element.setAttribute("data-bound", true);

        // TODO: javascript-able?
        // NOTE: the script is mapped to validval, so replacing it
        // requires it to add a different plugin here as well as
        // updating all data-vv fields being set in mapFormField() and
        // generateFormElement
        $(form_element).validVal({
          validate: {
            onKeyup: "valid",
            onBlur: "valid"
          },
          form: {
            onInvalid: util.return_out
          }
        });
      }
    }
  };

  /**
   * Parse a page for gadgets and run page setup
   * @method parsePage
   * @param {object} e Event (pagebeforechange)
   * @param {object} data Data passed along with this (JQM) event
   */
  init.parsePage = function (e, data) {
    var create, config, raw_url, handle, clean_url, parsed_url, destination;

    // TODO:maybe this is the problem???
    if (data) {
      if (data.options.link) {
        raw_url = data.options.link[0].href;
      } else {
        raw_url = data.toPage;
      }
    } else {
      raw_url = window.location.href;
    }

    if (typeof raw_url === "string") {
      config = util.parseLink(raw_url);

      if (e) {
        if (document.getElementById(raw_url.split("#").pop()) ||
            raw_url === $.mobile.getDocumentUrl() ||
                data.options.role === "popup") {
//           console.log("let JQM go, but stop us!")
          return;
        }
        if (document.getElementById(config.id)) {
//             console.log("stop JQM")
          e.preventDefault();
          return;
        }
//           console.log("HIJACK and stop JQM")
        handle = true;
        e.preventDefault();

      } else {
        // HACK: overwrite JQM history, so deeplinks are correctly handled
        if ($.mobile.navigate.history.initialDst &&
            window.location.hash !== "") {

          // this is the inital page (not) loaded, but stored as initial page!
          clean_url = window.location.href.split("#")[0];
          parsed_url = $.mobile.path.parseUrl(clean_url);

          // overwrite :-)
          $.mobile.navigate.history.stack[0].hash = "";
          $.mobile.navigate.history.stack[0].url = clean_url;
          $.mobile.path.documentUrl = parsed_url;
          $.mobile.path.documentBase = parsed_url;
        }
      }
    }

    if (e === undefined || handle) {
      if (config.deeplink) {
        create = true;
      }

      // prevent browser loading hash?query.json
      if (config.layout_identifier.split("?").length > 1) {
        destination = config.layout_identifier.split("?")[0];
      } else {
        destination = config.layout_identifier;
      }

      init.fetchPageLayouts("settings", destination)
        .then(function (reply) {
          return init.setPageElements(
            config,
            reply,
            create
          );
        })
        .then(init.setPageBindings)
        .fail(util.errorHandler);
    }
  };

  /**
   * Set the page currently being displayed
   * @method fetchPageLayouts
   * @param {object} storage JIO
   * @param {string} id Page id
   */
  init.fetchPageLayouts = function (storage, id) {
    return util.fetchPortalTypeConfiguration({
      "storage": storage,
      "file": "pages",
      "attachment": id,
      "baggage": undefined
    });
  };

  /**
   * parses a gadget configuration file
   * @method parseGadgetConfiguration
   * @param {object} reply gadget configuration 
   * @return {object} response object/promise
   */
  init.parseGadgetConfiguration = function (reply) {
    var parsed, baggage = reply.baggage;

    parsed = util.parseIfNeeded(reply.response);
    baggage.config = parsed;
    baggage.type = parsed.portal_type_source;

    if (baggage.create !== false && baggage.config.portal_type_fields) {
      // 2. field definitions
      return util.fetchPortalTypeConfiguration({
        "storage": "settings",
        "file": "portal_types",
        "attachment": baggage.config.portal_type_fields,
        "baggage": baggage
      });
    }
    return {
      "baggage": baggage
    };
  };

  /**
   * Test if JIO has data of a certain portal_type
   * @method testStorageForData
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  // TODO: remove when not needed anymore
  init.testStorageForData = function (reply) {
    var baggage = reply.baggage;

    if (reply.response) {
      baggage.fields = util.parseIfNeeded(reply.response);
    }
    if (baggage.create !== false) {
      return init.testForSampleData({
        "storage": "items",
        "type": baggage.type,
        "baggage": baggage
      });
    }
    return {
      "baggage": baggage
    };
  };

  /**
   * If no data is found in JIO, we need to load fake data for now
   * @method retrieveSampleData
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  // TODO: remove when not needed anymore
  init.retrieveSampleData = function (reply) {
    var baggage = reply.baggage;

    if (reply.response) {
      if (util.parseIfNeeded(reply.response).data.total_rows === 0) {
        return init.fetchSampleData({
          "type": baggage.config.portal_type_title,
          "baggage": baggage
        });
      }
    }
    return {
      "baggage": baggage
    };
  };

  /**
   * Store retrieved sample data in storage
   * @method storeSampleDataInStorage
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  // TODO: remove when not needed anymore
  init.storeSampleDataInStorage = function (reply) {
    var baggage = reply.baggage;

    if (reply.response) {
      return init.storeSampleData({
        "items": util.parseIfNeeded(reply.response),
        "type": baggage.type,
        "storage": "items",
        "baggage": baggage
      });
    }
    return {
      "baggage": baggage
    };
  };

  /**
   * Fetch total number of records
   * @method fetchPortalTypeDataTotal
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  init.fetchDataTotal = function (reply) {
    var baggage = reply.baggage;

    if (baggage.create === false) {
      baggage.state = document.getElementById(baggage.id).state;
      baggage.constructor = baggage.state.method;
      baggage.store_limit = baggage.state.query.limit;
      baggage.state.query.limit = [];
    } else {
      baggage.state = {};
      baggage.state.method = baggage.constructor;
      baggage.state.query = init.generateQueryObject({}, baggage.type);
    }
    // skip total for single item layouts!
    // TODO: What if the first page should only contain an object?
    if (baggage.layout_level === 0) {
      return util.fetchData({
        "baggage": baggage,
        "storage": "items",
        "query": baggage.state.query
      });
    }
    return {
      "baggage": baggage
    };
  };

  /**
   * Fetch records matching query
   * @method fetchDataQuery
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  init.fetchDataQuery = function (reply) {
    var parsed, baggage = reply.baggage;

    // single item query
    // TODO: more levels? how to generalize and not only search by _id?
    if (baggage.layout_level > 0) {
      baggage.value = baggage.fragments[baggage.layout_level];
    }
    if (reply.response) {
      parsed = util.parseIfNeeded(reply.response);
      baggage.state.total = parsed.data.total_rows;
    }
    if (baggage.create === false) {
      baggage.state.query.limit = baggage.store_limit;
      delete baggage.store_limit;
    } else {
      baggage.state.query = init.generateQueryObject(
        baggage.config.initial_query,
        baggage.type,
        '_id',
        baggage.value
      );
    }
    // new item, no query!
    if (baggage.mode) {
      return {
        "baggage": baggage
      };
    }
    return util.fetchData({
      "storage": "items",
      "query": baggage.state.query,
      "baggage": baggage
    });
  };

  /**
   * Generate gadget content based on query data and passed config
   * @method generateGadgetContent
   * @param {object} reply Response from previous promise and pass-params
   * @return {object} response object/promise
   */
  init.generateGadgetContent = function (reply) {
    var baggage = reply.baggage, selector, element;

    // append gadget to wrapping div
    element = factory.map_gadgets[baggage.constructor](
      baggage.config,
      (reply.response ? util.parseIfNeeded(reply.response) : null),
      baggage.fields,
      (baggage.create === false ? true : null)
    );

    // TODO: not really...
    $($.makeArray(element.querySelectorAll(".translate"))).i18n();
    //           .find("select").selectMenu("refresh").end()
    //           .find("input").filter(function() {
    //             switch (this.type || this.attr(type)) {
    //               case "submit":
    //               case "reset":
    //               case "button":
    //                 return true;
    //               break;
    //             }
    //             return false;
    //           }).checkboxRadio("refresh");

    if (baggage.create === false) {
      selector = baggage.state.gadget;
    } else {
      // NOTE: in case of update, element will be the section to update
      // not the gadget/fragment, so we need to find the gadget
      // NOTE: in case of forms, we find the form!
      selector = element.querySelector("#" + baggage.id) ||
        document.getElementById(baggage.config.form) ||
        element;
      baggage.state.gadget = selector;
    }

    // round up and store state on gadget
    baggage.state.constructor = baggage.constructor;
    delete baggage.constructor;
    baggage.state.selected = baggage.create === false ?
        (baggage.state.selected) : undefined;
    selector.state = baggage.state;

    // TODO: not working - element is fragment or html element
    init.updateInfoFields(
      element,
      baggage.state.query,
      baggage.state.total
    );

    if (baggage.create === false) {
      $(element).replaceAll(
        document.getElementById(baggage.id)
          .querySelectorAll("[data-update]")[0]
      )
        .enhanceWithin();
    } else {
      // please let this work...
      baggage.target.appendChild(element);
    }
  };

  /**
   * Setup/update elements to on the page being shown, generate page
   * @method setupPageElements
   * @param {object} config JSON pointers based on parsed link
   * @param {object} layouts Layouts to be generated for this page
   * @param {boolean} create Create page/Generate content/Refresh content
   */
  init.setPageElements = function (config, layouts, create) {
    var i,
      page,
      target,
      last,
      gadget,
      gadgets,
      baggage,
      promises = [],
      layout = layouts.response[config.layout_level || 0];

    if (create === true) {
      page = factory.generatePage(config, layout);
      target = factory.generateElement(
        "div",
        {"className": "ui-content"},
        {}
      );
    } else {
      page = document.getElementById(config.id || util.getActivePage());
      target = page.querySelectorAll("div.ui-content")[0];
      //       if (create === undefined) {
      //         init.setPageTitle(page, layout);
      //       }
    }

    // prepare baggage
    baggage = {
      "mode": config.mode || null,
      "create": create,
      "layout_level": config.layout_level || null,
      "fragments": config.fragment_list,
      "target": target
    };

    gadgets = layout.children || page.querySelectorAll("[data-gadget-id]");

    // NOTE: this may include local header/footer/panel/popups
    // TODO: beware of target when adding the above! should not be content
    // TODO: bundle into a single DOM operation!
    for (i = 0; i < gadgets.length; i += 1) {
      gadget = gadgets[i];
      // rewrite on every iteration!
      baggage.layout = gadget;
      baggage.id = gadget.id || gadget.getAttribute("data-gadget-id");

      if (create !== false) {
        baggage.constructor = gadget.type ||
            gadget.getAttribute("data-gadget-type");
      }

      // TODO: clear 2x calls like storeSampleData & storeSampleDataInStorage
      promises[i] = util.fetchPortalTypeConfiguration({
        "storage": "settings",
        "file": "gadgets",
        "attachment": baggage.id,
        "baggage": baggage
      })
        .then(init.parseGadgetConfiguration)
        .then(init.testStorageForData)
        .then(init.retrieveSampleData)
        .then(init.storeSampleDataInStorage)
        .then(init.fetchDataTotal)
        .then(init.fetchDataQuery)
        .then(init.generateGadgetContent)
        .fail(util.errorHandler);
    }

    // once the loop is done, we assemble and return the whole thing
    return RSVP.all(promises)
      .then(function () {
        // set a flag on target to indicate it has been enhanced
        target.setAttribute("data-bound", true);

        // append, initialize and enhance new page
        if (create === true) {
          last = document.body.lastChild;
          page.appendChild(target);

          if (util.testForClass(last.className, "ui-footer")) {
            document.body.insertBefore(page, last);
          } else {
            document.body.appendChild(page);
          }

          // JQM treatment
          $(document).enhanceWithin();

          $.mobile.changePage("#" + config.id);
        } else {
          // populate existing page and enhance
          if (gadgets.length > 0 && create === undefined) {
            $(page).empty().append(target).enhanceWithin();
          }
        }
      })
      .fail(util.errorHandler);
  };


  /* ====================================================================== */
  /*                             APPLICATION SETUP                          */
  /* ====================================================================== */

  /**
   * Timer for 500ms delayed actions
   */
  init.timer = 0;

  /**
   * cross-browser wrapper for DOMContentLoaded
   * Thx Diego Perini http://javascript.nwbox.com/ContentLoaded/
   * @method contentLoaded
   * @param {object} win Window
   * @param {method} fn Callback to run
   */
  init.contentLoaded = function (win, fn) {
    var done = false,
      top = true,
      doc = win.document,
      root = doc.documentElement,
      add = doc.addEventListener ? 'addEventListener' : 'attachEvent',
      rem = doc.addEventListener ? 'removeEventListener' : 'detachEvent',
      pre = doc.addEventListener ? '' : 'on',
      init = function(e) {
        if (e.type == 'readystatechange' && doc.readyState != 'complete') {
          return;
        }
        (e.type == 'load' ? win : doc)[rem](pre + e.type, init, false);
        if (!done && (done = true)) {
          fn.call(win, e.type || e);
        }
      },
      poll = function() {
        try {
          root.doScroll('left');
        } catch(e) {
          setTimeout(poll, 50); return;
        }
        init('poll');
      };

    if (doc.readyState == 'complete') {
      fn.call(win, 'lazy');
    } else {
      if (doc.createEventObject && root.doScroll) {
        try { top = !win.frameElement; } catch(e) { }
        if (top) poll();
      }
      doc[add](pre + 'DOMContentLoaded', init, false);
      doc[add](pre + 'readystatechange', init, false);
      win[add](pre + 'load', init, false);
    }
  };

  /**
   * fetch application configuration, store in JIO and setup application
   * @method runApplicationSetup
   * @param {string} file File needed to setup
   * @param {string} attachment Attachement with necessary config
   * @return {object} Promise object
   */
  init.runApplicationSetup = function (attachment) {
    init.storages = {};

    // TODO: find a way to not always refetch application
    // NOTE: can't fetchConfig because need to setup storages first
    if (init.storages[attachment]) {
      return;
    }
    return jIO.util
      .ajax({
        "url": "data/" + attachment + ".json"
      })
      .then(function(e) {
        return e.target.responseText;
      })
      .fail(util.errorHandler);

  };

  /**
   * sets up JIO based on loaded JSON "recipe"
   * @method setupStorages
   * @param {object} response object containing data (jio.util.ajax response)
   * @return {object} promise object
   */
  init.setupStorages = function (reply) {
    var i,
      store,
      promises = [],
      config = JSON.parse(reply);


    for (i = 0; i < config.length; i += 1) {
      store = config[i].definition;

      promises[i] =
        init.storages[store.application_name] =
        jIO.createJIO(store);
    }

    return RSVP.all(promises);
  };

  /**
   * Loads and runs application setters
   * @method loadGlobalElements
   * @return {object} promise object
   */
  init.loadGlobalElements = function () {
    return util.fetchPortalTypeConfiguration({
      "storage": "settings",
      "file": "configuration",
      "attachment": "global",
      "baggage": undefined
    });
  };

  /**
   * Iterates over application configuration and generate defined elements
   * @method setupGlobalElements
   * @param {object} config Application configuration & baggage
   */
  // TODO: run this through the main gadget handler, only difference is scope
  init.setupGlobalElements = function (reply) {
    var i,
      element,
      content,
      config = util.parseIfNeeded(reply.response);

    if (config && config.length) {
      for (i = 0; i < config.length; i += 1) {
        element = config[i];
        content = factory.util.forward(element);

        // TODO: not really...
        $($.makeArray(content.querySelectorAll(".translate"))).i18n();
        //           .find("select").selectMenu("refresh").end()
        //           .find("input").filter(function() {
        //             switch (this.type || this.attr(type)) {
        //               case "submit":
        //               case "reset":
        //               case "button":
        //                 return true;
        //               break;
        //             }
        //             return false;
        //           }).checkboxRadio("refresh");

        switch (element.type) {
        case "panel":
          // NOTE: panel must be either before or after everything else!
          // WARNING: IE8- children() retrieves comments, too
          document.body.insertBefore(content, document.body.children[0]);
          break;
        default:
          document.body.appendChild(content);
          break;
        }
      }
    } else {
      util.errorHandler({
        "Error": "Setup Global Elements: No app data"
      });
    }
  };

  /**
   * Set global bindings for all application elements
   * @method setGlobalBindings
   */
  init.setGlobalBindings = function () {

    $(document)
      .enhanceWithin()

      // generate dynamic pages
      .on("pagebeforechange", function (e, data) {
        init.parsePage(e, data);
      })

      // update
      .on("pagebeforeshow", "div.ui-page", function (e, data) {
        init.updatePage(e, data);
      })

      // clean dynamic pages on hide
      // NOTE: or hack JQM and call "bindRemove" on dynamic pages, too
      .on("pagehide", "div.ui-page", function () {
        if (this.getAttribute("data-external-page")) {
          $(this).page("destroy").remove();
        }
      })

      // block form submits
      .on("submit", "form", function (e) {
        e.preventDefault();
        return false;
      })

      // global actions
      .on("click change keyup input", ".action", function (e) {
        var val,
          last,
          element = e.target,
          type = element.type;

        // delay all input field actions allowing user to type/select
        if (element.tagName === "INPUT") {
          switch (type) {
          case "button":
          case "checkbox":
          case "reset":
            init.action(e);
            break;
          default:
            val = element.value;
            last = element.getAttribute("data-last");
            if ((last && last === val) && type !== "Submit") {
              return;
            }
            if (init.timer) {
              window.clearTimeout(init.timer);
              init.timer = 0;
            }

            // give user half second to pick his state
            init.timer = window.setTimeout(function () {
              element.setAttribute("data-last", val);
              init.action(e);
              init.timer = 0;
            }, 500);
            break;
          }
        } else {
          init.action(e);
        }
      })

      // popup content loading
      .find("#global_popup")
        .on("popupbeforeposition", function (e) {
        util.loadPopupContents(init.generateActionObject(e));
      });
  };

  /* ====================================================================== */
  /*         SAMPLE DATA (remove once live data is available)               */
  /* ====================================================================== */

  /**
   * Create Sample data entries for JIO
   * @method storeSampleData
   * @param {object} parcel object containing storage, type and baggage
   * @return {object} promise object/baggage
   */
  init.storeSampleData = function (parcel) {
    var i, obj, key, promises, record, store = init.storages[parcel.storage];

    if (store && parcel.items && parcel.items.length) {
      promises = [];
      for (i = 0; i < parcel.items.length; i += 1) {
        record = parcel.items[i];
        obj = {};
        for (key in record) {
          if (record.hasOwnProperty(key)) {
            obj[key] = record[key];
          }
        }
        obj.portal_type = parcel.type;
        promises[i] = store.post(obj);
      }
      return RSVP.all(promises)
        .then(function () {
          return {
            "response": undefined,
            "baggage": parcel.baggage
          };
        })
        .fail(util.errorHandler);
    }
    // we may have no sample data!
    return {
      "response": undefined,
      "baggage": parcel.baggage
    };
  };

  /**
   * Test if storage is empty
   * @method testForSampleData
   * @param {object} parcel object containing storage, type and baggage
   * @return {object} promise object/baggage
   */
  init.testForSampleData = function (parcel) {
    return util.fetchData({
      "storage": parcel.storage,
      "query": init.generateQueryObject({
        "limit": [0, 1]
      }, parcel.type),
      "baggage": parcel.baggage
    });
  };

  /**
   * retrieve sample data from disk
   * @method fetchSampleData
   * @param {object} parcel Id of gadget to fetch sample data and baggage
   * @return {object} promise object & baggage
   */
  init.fetchSampleData = function (parcel) {
    return jIO.util
      .ajax({
        "url": "data/" + parcel.type + "_sample.json"
      })
      .then(function (e) {
        return {
          "response": e.target.response,
          "baggage": parcel.baggage
        };
      })
      .fail(util.errorHandler);
  };

  /* ====================================================================== */
  /*                             ENTRY POINT                                */
  /* ====================================================================== */
  init.contentLoaded(window, function () {

    // HACK: don't!
    window.localStorage.clear();

    // initalize translations
    var lng = window.navigator.userLanguage || window.navigator.language;
    if (lng.indexOf("zh") !== 0) {
      lng = "en-EN";
    } else {
      lng = "zh-CN";
    }
    $.i18n.init({
      lng: lng,
      load: 'current',
      fallbackLng: false,
      resGetPath: 'lang/__lng__/__ns__.json',
      ns: 'dict'
    });

    init
      // "Application Setup"
      .runApplicationSetup("storages")
      .then(init.setupStorages)
      .then(init.loadGlobalElements)
      .then(init.setupGlobalElements)
      .then(init.setGlobalBindings)
      // "Page Setup"
      .then(init.parsePage)
      .fail(util.errorHandler);

  });

}(window, document, jQuery));