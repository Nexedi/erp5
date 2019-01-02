var priv = {};



  /* ====================================================================== */
  /*                              ERP5 CONVERTER                            */
  /* ====================================================================== */
  // since we are making something generic!



  /**
    * map ERP5 field type to HTML elements
    * @method mapFieldType
    * @param {string} type ERP5 field type
    * @return {string} element
    */
  priv.mapFieldType = function (type) {
    var element;
    switch (type) {
      case "StringField":
      case "RelationStringField":
      case "IntegerField":
        element = "input";
        break;
      case "ListField":
        element = "select";
        break;
      case "TextareaField":
        element = "textarea";
        break;
    };
    return element;
  };


  /**
   * map ERP5 field type to input type
   * @method mapFieldType
   * @param {string} type ERP5 field type
   * @return {string} element
   */
  priv.mapInputType = function (type) {
    var field_type = null;
    switch (type) {
      case "StringField":
      case "RelationStringField":
        field_type = "text";
        break;
      case "IntegerField":
        field_type = "number";
        break;
    }
    return field_type;
  };

  /**
   * Build a string from array
   * @method: buildValue
   * @param: {string/array} value String/Array passed
   * @returns: {string} string
   */
  priv.buildValue = function (value) {
    var i = 0,
      setter = "",
      property;

    if (typeof value === "string") {
      setter = value;
    } else if (typeof value === "object") {
      for (property in value) {
        if (value.hasOwnProperty(property)) {
          setter += (i === 0 ? "" : ", ") + value[property];
          i += 1
        }
      }
    } else {
      for (i; i < value.length; i += 1) {
        setter += (i === 0 ? "" : ", ") + value[i];
      }
    }
    return setter || "could not generate value";
  };

  /**
   * Append values in form
   * @method: setValue
   * @param: {string} type Type of object
   * @param: {string} key Key to set
   * @param: {string/array} value Value to set key to
   */
  priv.setValue = function (type, key, value) {
    var i,
      j,
      k,
      unit,
      element,
      getter,
      single_option,
      elements = document.getElementsByName(type + "_" + key),
      setter = priv.buildValue(value),
      // ...PFFFFFFFFFFFFFF standards require so much customization...
      dublin_core_date_time_fields = [
        "date",
        "created",
        "modified",
        "effective_date",
        "expiration_date"
      ],
      time_fields = ["year", "month", "day"];

    // can't be generic... yet
    for (i = 0; i < dublin_core_date_time_fields.length; i += 1) {
      if (key === dublin_core_date_time_fields[i]) {
        for (k = 0; k < time_fields.length; k += 1) {
          unit = time_fields[k];
          element = document.getElementsByName(
            type + "_" + key + "_" + unit
          );

          if (element.length > 0) {
            single_option = element[0].getElementsByTagName("option");
            switch(unit) {
            case "year":
              getter = new Date(setter).getFullYear();
              break;
            case "month":
              getter = new Date(setter).getMonth() + 1;
              break;
            case "day":
              getter = new Date(setter).getDate();
              break;
            }
            if (single_option.length === 1) {
              single_option[0].setAttribute("value", getter);
              single_option[0].text = getter;
              single_option[0].parentNode.parentNode.getElementsByTagName("span")[0].innerHTML = getter;
            } else {
              element[0].value = getter;
            }
          }
        }
      }
    }

    for (j = 0; j < elements.length; j += 1) {
      elements[j].value = setter;
    }
  };

  /**
    * Generate input form for an item
    * @method generateItem
    * @param  {string} mode View Clone/Edit/Add
    * @param  {string} item Element to show
    */
  // NOTE: this should be in another gadget/file
  priv.generateItem = function (mode, item) {

    if (item) {
      // fetch data
      priv.erp5.get({"_id": item}, function (error, response) {
        var property, value, abort;

        if (response) {
          for (property in response) {
            if (response.hasOwnProperty(property)) {
              value = response[property];
              priv.setValue(response.type.toLowerCase(), property, value);
            }
          }
        } else {
          abort = confirm("Error trying to retrieve data! Go back to overview?");
          if (abort === true) {
            $.mobile.changePage("computers.html");
          }
        }
      });
    }
  };

  /**
    * Create a serialized object from all values in the form
    * @method serializeObject
    * @param  {object} form Form to serialize
    * @returns  {string} JSON form values
    */
  priv.serializeObject = function(form) {
    var o = {};
    var a = form.serializeArray();
    $.each(a, function() {
      if (o[this.name] !== undefined) {
          if (!o[this.name].push) {
              o[this.name] = [o[this.name]];
          }
          o[this.name].push(this.value || '');
      } else {
          o[this.name] = this.value || '';
      }
    });
    return o;
  };

  // date conversion object container
  priv.dates = {};

  /**
    * Create a serialized object from all values in the form
    * @method validateObject
    * @param  {object} serialized object
    * @returns  {object} object ready to pass to JIO
    */
  // TODO: should be made generic by passing the type and a recipe for
  // which fields to format how
  priv.validateObject = function (object) {
    var validatedObject = {},
      property,
      setter,
      value,
      i,
      j,
      clean_property,
      add_property,
      date_property,
      date_component,
      new_date,
      // NOTE: ... to time to be generic...
      convertToArray = ["contributor", "category"],
      seperator_character = ",",
      convertToDate = ["effective_date", "expiration_date"];

    for (property in object) {
      add_property = true;
      if (object.hasOwnProperty(property)) {
        value = object[property];
        clean_property = property.replace("computer_", "");

        // multiple entries
        if (typeof value !== "string") {
          if(value.length > 0) {
            // this should only happen if a field is in the form multiple times!
            // NOTE: not nice
            setter = value[0];
          }
        } else {
          setter = value;
        }

        // convert to array
        for (i = 0; i < convertToArray.length; i += 1) {
          if (convertToArray[i] === clean_property ) {
            setter = object[property].split(seperator_character);
          }
        }

        // set up date conversion
        for (j = 0; j < convertToDate.length; j += 1) {
          date_property = convertToDate[j];
          if (clean_property.search(date_property) !== -1) {
            add_property = false;
            if (priv.dates[date_property] === undefined) {
              priv.dates[date_property] = {};
            }
            // ...
            date_component = clean_property.split("_")[2];
            priv.dates[date_property][date_component] = value;
          }
        }
        if (add_property) {
          validatedObject[clean_property] = setter;
        }
      }
    }

    // timestamp modified
    validatedObject.modified = new Date().toJSON();

    // timestamp create and date
    if (validatedObject.date === undefined) {
      validatedObject.date =  validatedObject.modified;
    }
    if (validatedObject.create === undefined) {
      validatedObject.create =  validatedObject.modified;
    }

    // HACK: add missing type!
    if (validatedObject.type === undefined || validatedObject.type === "") {
      validatedObject.type = "Computer";
    }

    // build dates
    for (date in priv.dates) {
      if (priv.dates.hasOwnProperty(date)) {
        new_date = priv.dates[date];
        validatedObject[date] = new Date(
          new_date["year"], new_date["month"], new_date["day"]
        ).toJSON();
        // delete this date
        delete priv.dates[date];
      }
    }
    return validatedObject;
  }

   /**
    * Store object in EPR5
    * @method modifyObject
    * @param  {object} object Validated object
    * @param  {method} string PUT or POST
    */
  priv.modifyObject = function (object, method, callback) {
    priv.erp5[method](object, function (error, response) {
      if (error) {
        alert("oops..., an error occurred trying to store");
      } else {
        alert("worked");
        if (callback) {
          callback();
        }
      }
    });
  };

  /**
    * Create array of URL parameters
    * @method splitSearchParams
    * @param  {string} url URL to split
    * @returns {array} array of url parameters
    */
  priv.splitSearchParams = function (url) {
    var path;

    if (url === undefined) {
      path = window.location;
    } else {
      path = url;
    }

    return $.mobile.path.parseUrl(path).search.slice(1).split("&");
  }





  /**
  * Replace substrings to another strings
  * @method recursiveReplace
  * @param  {string} string The string to do replacement
  * @param  {array} list_of_replacement An array of couple
  * ["substring to select", "selected substring replaced by this string"].
  * @return {string} The replaced string
  */
  priv.recursiveReplace = function (string, list_of_replacement) {
    var i, split_string = string.split(list_of_replacement[0][0]);
    if (list_of_replacement[1]) {
      for (i = 0; i < split_string.length; i += 1) {
        split_string[i] = priv.recursiveReplace(
          split_string[i],
          list_of_replacement.slice(1)
        );
      }
    }
    return split_string.join(list_of_replacement[0][1]);
  };

  /**
  * Changes & to %26
  * @method convertToUrlParameter
  * @param  {string} parameter The parameter to convert
  * @return {string} The converted parameter
  */
  priv.convertToUrlParameter = function (parameter) {
    return priv.recursiveReplace(parameter, [[" ", "%20"], ["&", "%26"]]);
  };


  /**
    * Create a URL string for authentication (same as ERP5 storage)
    * @method createEncodedLogin
    */
  priv.createEncodedLogin = function () {
    return "__ac_name=" + priv.convertToUrlParameter(priv.username) +
        "&" + (typeof priv.password === "string" ?
                "__ac_password=" +
                priv.convertToUrlParameter(priv.password) + "&" : "");
  };

  /**
    * Modify an ajax object to add default values
    * @method makeAjaxObject
    * @param  {object} json The JSON object
    * @param  {object} option The option object
    * @param  {string} method The erp5 request method
    * @param  {object} ajax_object The ajax object to override
    * @return {object} A new ajax object with default values
    */
  priv.makeAjaxObject = function (key) {
    var ajax_object = {};

    ajax_object.url = priv.url + key + "?" + priv.createEncodedLogin() + "disable_cookie_login__=1";
    // exception: ajax_object.url = priv.username + ":" + priv.password + "@" + priv.url + key;
    ajax_object.dataType = "text/plain";
    ajax_object.async = ajax_object.async === false ? false : true;
    ajax_object.crossdomain = ajax_object.crossdomain === false ? false : true;
    return ajax_object;
  };

  /**
    * Runs all ajax requests for propertyLookups
    * @method getERP5property
    * @param  {string} id The id of the object to query
    * @param  {string} lookup The method to retrieve the property
    * @return {string} The property value
    */
  // NOTE: need a different way because this triggers a ton of http requests!
  priv.getERP5property = function (id, lookup) {
    var key = id + "/" + lookup;
    // return $.ajax(priv.makeAjaxObject(key));
    return {"error":"foo"}
  };








  /* ********************************************************************** */
  /*                            TAB FIELD LIST                              */
  /* ********************************************************************** */
  /**
    * Create tab menu
    * @method constructTabs
    * @param {object} element Base table to enhance
    * @param {string} mode View to display
    * @param {string} item Id of item to display
    * @param {object} properties Properties of item to display
    * @returns {object} html object / deferred
    */
  priv.constructTabs = function (element, mode, item, properties) {
    var property,
      value,
      abort,
      i,
      j,
      k,
      set,
      collapsible,
      tab,
      tag,
      box,
      content,
      wrap,
      field,
      overrides,
      config,
      exist,
      validate,
      element_wrap,
      fragment = window.document.createDocumentFragment(),
      // tab config
      gadget_id = element.getAttribute("data-gadget-id"),
      settings = priv.gadget_properties[gadget_id],
      portal_type = settings.portal_type_title,

      // wrapper - could be a slot, too
      $parent = $(element.parentNode);

    // TODO: get settings here if not loaded
    if (settings !== undefined) {
      // tab container
      set = priv.generateElement(
        "div",
        {"className": "ui-dynamic-tabs"},
        {"data-role": "collapsible-set", "data-tabs": settings.layout.length || 1, "data-type": "tabs"}
      );

      // tabs
      for (i = 0; i < settings.layout.length; i += 1) {
        tab = settings.layout[i];
        collapsible = priv.generateElement(
          "div",
          {},
          {"data-role":"collapsible", "data-icon":"false", "data-collapsed": i === 0 ? false : true}
        );
        collapsible.appendChild(priv.generateElement(
          "h1",
          {"className":"translate"},
          {"data-i18n": tab.i18n},
          {"text": tab.title}
        ));

        if (tab.blocks !== undefined) {
          for (j = 0; j < tab.blocks.length; j += 1) {
            box = tab.blocks[j];

            // content element
            content = priv.generateElement(
              "div",
              {"className": box.fullscreen ? " content_element_fullscreen content_element" : "content_element"}
            );
            // fields
            if (box.fields) {
              for (k = 0; k < box.fields.length; k += 1) {
                field = box.fields[k];
                config = priv.field_definitions[portal_type][field];
                overrides = box.overrides[field] || {};
                // all-in-one...
                content.appendChild(priv.generateFormField(config, overrides));
              }
              fragment.appendChild(content);
            }
            // actions
            if (box.actions) {
              for (l = 0; l < box.actions.length; l += 1) {
                content.appendChild(priv.generateControlgroup(box.actions[l]));
              }
            }
            // nested gadgets ASYNC
            if (box.view) {
//               $.when(priv[box.view.renderWith](content, box.view.gadget_id)).then(function(fragment) {
//                   $(fragment.target).append(fragment.element).enhanceWithin();
//               });
            }
            collapsible.appendChild(content);
          }
        }
        set.appendChild(collapsible);
      }

      // add dynamic tabs
      if (settings.configuration.editable) {
        collapsible = priv.generateElement("div",
            {"className": "dashed add_tab"},
            {"data-role":"collapsible", "data-icon": "plus", "data-expanded-icon":"plus"},
            {}
        );
        collapsible.appendChild(priv.generateElement("h1",
            {"className":"translate"},
            {"data-i18n": "generic.layouts.tabs.add"},
            {"text":"Add tab"}
          )
        );
        set.appendChild(collapsible);
      }
      fragment.appendChild(set);
      if (settings.configuration.editable) {
        fragment.appendChild(
          priv.generateElement("p",
            {"className":"center ui-dynamic-info translate"},
            {"data-i18n": "generic.messages.tabs.empty"},
            {"text":"Your dashboard is empty. Click above to add tabs and gadgets displaying key information to your dashboard."}
          )
        );
      }

      // la viola - we touch the DOM once!!
      $parent.empty().append( fragment ).enhanceWithin();
    } else {
      element.appendChild(
        priv.generateElement("p",
          {"className":"center translate"},
          {"data-i18n": "generic.errors.no_settings"},
          {"text": "Error: No configuration available for this type of data!"}
        )
      );
    }
  };



  /* ********************************************************************** */
  /*                                 action menu                            */
  /* ********************************************************************** */
  /*
   * Creates a controlgroup (just a passthrough method)
   * @constructActionMenu
   * @param {object} element Wrapper element
   * @returns {object} document fragment
   */
  priv.constructActionMenu = function (element) {
    var gadget_id = element.getAttribute("data-gadget-id"),
      settings = priv.gadget_properties[gadget_id],
      portal_type = settings.portal_type_title,
      $parent = $(element.parentNode);
      fragment = priv.generateControlgroup(settings.layout);

    $(element.parentNode).empty().append( fragment ).enhanceWithin();
  };

  /* ====================================================================== */
  /*                                 SETUP                                  */
  /* ====================================================================== */
  // NOTE: custom, content generation methods = non generic stuff needed to
  // display custom content. Above this section = generic, below = custom


  /* ********************************************************************** */
  /*                       table search/config methods                      */
  /* ********************************************************************** */
  /**
    * generates a popup contents
    * @method generatePopupContents
    * @param  {object} e Event that triggered opening a popup
    * @param  {string} type Pointer to object holding popup config info
    * @param  {string} portal_type To be loaded and referenced
    * @param  {object} view gadget Configuration properties (pass through)
    * @oaram  {string} gadget_id
    */
  priv.generatePopupContents = function (e, type, portal_type, view, gadget_id) {
    var property,
      i,
      field,
      popup_body,
      popup_content,
      popup_message,
      popup_title,
      popup_info,
      popup_method,
      element,
      reference,
      popup = document.getElementById(e.target.href.split("#")[1]),
      state = popup.getAttribute("data-state");

    switch(type) {
      case "self":
        reference = e.target.getAttribute("data-reference");
        // portal_type should be defined
      break;
      case "action":
        element = e.target.parentNode.getElementsByTagName("input")[0];
        reference = element.getAttribute("data-reference");
        portal_type = element.getAttribute("data-relation");
      break;
    };

    // only regenerate the popup if switching content
    if (state !== reference) {
      popup_body = document.createDocumentFragment();
      switch (reference) {
        // NOTE: table wrapper configure menu
        // TODO: a global dump for reusable button config would be nice!
        case "configure":
          popup_title = "Configuration";
          popup_info = "Please select columns to display and priority of display on smaller screens (6-1). Drag columns to modify the order of display"
          popup_methods = ["generatePortalTypeFieldSelector", "generateDefaultColumnConfig"];
          popup_footer = {
            "type": "controlgroup",
            "direction": "horizontal",
            "class": "ui-grid ui-table-wrapper-bottom ui-table-wrapper-inset ui-corner-all",
            "controls_class": "ui-grid-3",
            "buttons": [
              {
                "type": "a",
                "direct": {"className": "ui-grid-button ui-link ui-btn ui-icon-remove ui-btn-icon-right ui-shadow ui-corner-all ui-first-child"},
                "attributes": {"data-i18n": "", "data-enhanced":"true", "data-role": "button", "data-iconpos": "right", "data-icon":"remove", "data-rel": "back"},
                "logic": {"text":"Cancel"}
              }, {
                "type": "a",
                "direct": {"className": "ui-grid-button table_action ui-link ui-btn ui-icon-refresh ui-btn-icon-right ui-shadow ui-corner-all"},
                "attributes": {"data-i18n": "", "data-enhanced":"true", "data-role": "button", "data-iconpos": "right", "data-icon":"refresh", "data-action": "rest"},
                "logic": {"text":"Reset"}
              }, {
                "type": "a",
                "direct": {"className": "ui-grid-button table_action ui-btn-active ui-link ui-btn ui-icon-save ui-btn-icon-right ui-shadow ui-corner-all ui-last-child"},
                "attributes": {"data-i18n": "generic.buttons.save", "data-role": "button", "data-iconpos": "right", "data-icon":"save", "data-action": "save"},
                "logic": {"text":"Save"}
              }
            ]
          };
          popup_action = "add_criteria_config";
          popup_hint = "Add Columns";
        break;
        // NOTE: table wrapper detail search
        case "details":
          popup_title = "Detail Search";
          popup_info = "Create a multi field search by adding fields below. For faster lookups, you can save your search criteria if needed."
          popup_methods = ["generatePortalTypeFieldSelector"];
          popup_footer = {
            "type": "controlgroup",
            "direction": "horizontal",
            "class": "ui-grid ui-table-wrapper-bottom ui-table-wrapper-inset ui-corner-all",
            "controls_class": "ui-grid-2",
            "buttons": [
              {
                "type": "a",
                "direct": {"className": "ui-grid-button ui-link ui-btn ui-icon-remove ui-btn-icon-right ui-shadow ui-corner-all ui-first-child"},
                "attributes": {"data-i18n": "", "data-enhanced":"true", "data-role": "button", "data-iconpos": "right", "data-icon":"remove", "data-rel": "back"},
                "logic": {"text":"Cancel"}
              }, {
                "type": "a",
                "direct": {"className": "ui-grid-button table_action ui-btn-active ui-link ui-btn ui-icon-search ui-btn-icon-right ui-shadow ui-corner-all ui-last-child"},
                "attributes": {"data-i18n": "", "data-enhanced":"true", "data-role": "button", "data-iconpos": "right", "data-icon":"search", "data-action": "search"},
                "logic": {"text":"Search"}
              }
            ]
          };
          popup_action = "add_criteria_search";
          popup_hint = "Select Search Criteria";
        break;
      }
      // header
      if (popup_title) {
        popup_body.appendChild(priv.generateHeader({"title":popup_title}));
      }
      // content
      popup_content = priv.generateElement("div", {"className":"ui-content"},{"data-role":"content"},{});
      if (popup_info) {
        popup_content.appendChild(priv.generateElement("p", {},{},{"text": popup_info || null}));
      }
      // data
      for (i = 0; i < popup_methods.length; i += 1) {
        popup_content.appendChild( priv[popup_methods[i]]( view, gadget_id, popup_action, popup_hint ) );
      }
      popup_body.appendChild( popup_content);
      // footer
      if (popup_footer) {
        popup_body.appendChild( priv.generateFooter(popup_footer));
      }
      popup.setAttribute("data-state", reference);
      popup.setAttribute("data-type", portal_type);

      // empty popup
      popup.innerHTML = "";

      // add content directly
      $(popup).append( popup_body ).enhanceWithin();
    }
  };

  /**
  * generates a detail search field for the portal_type
  * @method generatePortalTypeFieldSelector
  * @param  {object} table The table configuration
  * @return {object} element The element fragment
  */
  priv.generatePortalTypeFieldSelector = function (table, gadget_id, action, hint) {
    var controls,
      property,
      config,
      unique_field_name,
      all_options = [];

    for (property in table) {
      if (table.hasOwnProperty(property)) {
        field = table[property];
        unique_field_name = "search_" + gadget_id + "_" + property;
        all_options.push({
          "value":gadget_id + ":" + property,
          "text": priv.capFirstLetter(property)
        });
      }
    }

    controls = priv.generateElement("div",
      {"className":"ui-controlgoup ui-controlgroup-horizontal ui-popup-menu"},
      {"data-role":"controlgroup", "data-type":"horizontal"},
      {}
    );
    controls.appendChild(priv.generateElement("label",
      {"className": "ui-hidden-accessible"},{"for": action + "_" + gadget_id}, {"text": hint}
    ));
    controls.appendChild(priv.generateElement("select",
      {"name": action + "_" + gadget_id, "id": action + "_" + gadget_id },
      {},
      {"options": all_options}
    ));
    controls.appendChild(priv.generateElement("a",
      {"className": "responsive ui-btn-active table_action"},
      {"data-role":"button", "data-iconpos":"right", "data-icon":"plus", "data-action":action},
      {"text":"Add"}
    ));
    return controls;
  };

  /**
  * generates a grid configuration entry
  * @method generateConfigCriteria
  * @param  {object} element clicked element
  */
  priv.generateConfigCriteria = function (element, id, prop) {
    var field,
      property,
      grid,
      cell,
      i,
      unique_field_name,
      prev,
      val,
      portal_type,
      property;

    if (typeof element === "object") {
      prev = element.previousSibling.getElementsByTagName("select")[0],
      val = prev.options[prev.selectedIndex].value,
      gadget_id = val.split(":")[0],
      property = val.split(":")[1];
    } else {
      val = "skip";
      gadget_id = id;
      property = prop;
    }

    if (val === "" || val === undefined) {
      alert("Please select a valid column!");
    } else {
       // look up field in gadget_id, generate grid and add it to form
      field = priv.gadget_properties[gadget_id].view[property];

      if (field) {
        unique_field_name = "configure_" + gadget_id + "_" + property;

        grid = priv.generateElement("div",
          {"className":"ui-grid-d ui-grid-row"}, {}, {"grid":5}
        );

        for (i = 0; i < grid.childNodes.length; i += 1) {
          cell = grid.childNodes[i];
          switch(i) {
            case 0:
              cell.className = "ui-block-a ui-grid-title";
              cell.appendChild(priv.generateElement("span",
                {}, {}, {"text": priv.capFirstLetter(property)}
              ));
            break;
            case 1:
              cell.className = "ui-block-b";
              cell.appendChild(priv.generateElement("label",
                {"className": "ui-hidden-accessible"},
                {"for": unique_field_name + "_priority"},
                {"text": "Set priority"}
              ));
              cell.appendChild(priv.generateElement("input",
                {
                "name": unique_field_name + "_priority",
                "id": unique_field_name + "_priority",
                "min":1,
                "max":6,
                "type":"number",
                "value": field.priority || ""
                },
                {"data-mini": "true"},
                {"disabled": field.priority === undefined ? "disabled" : null}
              ));
            break;
            case 2:
              cell.className = "ui-block-c";
              cell.appendChild(priv.generateElement("label",
                {"className": "ui-hidden-accessible"},
                {"for": unique_field_name + "_toggle"},
                {"text": "Set visibility"}
              ));
              cell.appendChild(priv.generateElement("select",
                {"name": unique_field_name + "_toggle", "id": unique_field_name + "_toggle"},
                {"data-mini": "true", "data-role":"slider"},
                {
                  "disabled": field.priority === undefined ? "disabled" : null,
                  "options": [
                    {"text": "Show", "value": "on", "selected": field.show ? "selected": null},
                    {"text": "Hide", "value": "off", "selected": field.show ? "selected": null}
                  ]
                }
              ));
            break;
            case 3:
              cell.className = "ui-block-d";
              cell.appendChild(priv.generateElement(
                "label",
                {"className": "ui-hidden-accessible"},
                {"for": unique_field_name + "_sort"},
                {"text": "Set sorting"})
              );
              cell.appendChild(priv.generateElement("select",
                {"name": unique_field_name + "_sort", "id": unique_field_name + "_sort"},
                {"data-mini": "true", "data-role":"slider"},
                {
                  "disabled": field.priority === undefined ? "disabled" : null,
                  "options": [
                    {"text": "Sort", "value": "on", "selected": field.show ? "selected": null},
                    {"text": "Static", "value": "off", "selected": field.show ? "selected": null}
                  ]
                }
              ));
            break;
            case 4:
              cell.className = "ui-block-e ui-grid-action";
              cell.appendChild(priv.generateElement("a",
                {"className":"table_action"},
                {"data-role":"button", "data-icon":"delete", "data-iconpos":"notext", "data-action":"delete_criteria"},
                {"text":"Delete"}
              ));
            break;
          };
        }

        return grid;
      } else {
        alert("Field name does not exist in field defition list!");
      }
    }
  };

  /**
  * generates a grid search criteria entry
  * @method generateSearchCriteria
  * @param  {object} element clicked element
  */
  priv.generateSearchCriteria = function (element) {
    var grid,
      cell,
      opts = [],
      i,
      j,
      field,
      new_form,
      prev = element.previousSibling.getElementsByTagName("select")[0],
      val = prev.options[prev.selectedIndex].value,
      portal_type = val.split(":")[0],
      property = val.split(":")[1],
      form = $( element ).closest(".ui-popup").find("form");

    // form should be create here instead to keep column selector generic
    if (form.length === 0) {
      new_form = document.createElement("form");
    }
    if (val === "" || val === undefined) {
      alert("Please select a valid criteria!");
    } else {
      // look up field in portal_type, generate grid and add it to form
      field = priv.gadget_properties[portal_type].view[property];

      if (field) {

        grid = priv.generateElement("div",
          {"className":"ui-grid-d ui-grid-row"}, {}, {"grid":4}
        );

        for (i = 0; i < grid.childNodes.length; i += 1) {
          cell = grid.childNodes[i];
          switch(i) {
            case 0:
              cell.className = "ui-block-a ui-grid-title";
              cell.appendChild(priv.generateElement("span",
                {}, {}, {"text": priv.capFirstLetter(property)}
              ));
            break;
            case 1:
              cell.className = "ui-block-b ui-grid-search";
              if (field.search !== undefined) {
                cell.appendChild(priv.generateElement("label",
                  {"className": "ui-hidden-accessible"},
                  {"for": "run_search_" + portal_type + "_" + property},
                  {"text": "Search Term"})
                );
                switch(field.search.type) {
                  case "text":
                    cell.appendChild(priv.generateElement("input",
                      {
                        "name": "run_search_" + portal_type + "_" + property,
                        "id": "run_search_" + portal_type + "_" + property,
                        "type": field.search.type
                      },
                      {"data-clear-btn": "true"}
                    ));
                  break;
                  case "select":
                    for (j = 0; j < field.search.options.length; j += 1) {
                      if (j === 0) {
                        opts.push({"value":"","text":"", "selected":"selected"})
                      }
                      opts.push({"value":field.search.options[j], "text":field.search.options[j]})
                    }
                    cell.appendChild(priv.generateElement("select",
                      {"name": "run_search_" + portal_type + "_" + property, "id": "run_search_" + portal_type + "_" + property,},
                      {},
                      {"options": opts}
                    ));
                  break;
                }
              }
            break;
            case 2:
              cell.className = "ui-block-c ui-grid-search";
              if (field.search !== undefined) {
                cell.appendChild(priv.generateElement("label",
                  {"className": "ui-hidden-accessible"},
                  {"for": "run_search_finetune_" + portal_type + "_" + property},
                  {"text": "Specify"})
                );
                switch(field.search.subsearch) {
                  case "flip":
                    for (i = 0; i < field.search.options.length; i += 1) {
                      opts.push({"value":field.search.options[i], "text":field.search.options[i], "selected": i === 0 ? "selected" : null})
                    }
                    cell.appendChild(priv.generateElement("select",
                      {"name": "run_search_finetune_" + portal_type + "_" + property, "id": "run_search_finetune_" + portal_type + "_" + property},
                      {"data-mini":"true", "data-role":"slider"},
                      {"options": opts}
                    ));
                  break;
                  case "checkbox":
                    cell.lastChild.className = "";
                    cell.appendChild(priv.generateElement("input",
                      {
                        "name":"run_search_finetune_" + portal_type + "_" + property,
                        "id":"run_search_finetune_" + portal_type + "_" + property,
                        "type":"checkbox",
                        "value": field.search.value
                      },
                      {"data-mini":"true"},
                      {}
                    ));
                  break;
                };
              }
            break;
            case 3:
              cell.className = "ui-block-e ui-grid-action";
              cell.appendChild(priv.generateElement("a",
                {"className":"table_action"},
                {"data-role":"button", "data-icon":"delete", "data-iconpos":"notext", "data-action":"delete_criteria"},
                {"text":"Delete"}
              ));
            break;
          }
        }

        // first row
        if (form.length === 0) {
          new_form.appendChild(grid);
          return new_form;
        }
        // other rows
        return grid;
      } else {
        alert("Field name does not exist in field defition list!");
      }
    }
  };

  /**
    * generates a configuration form for the portal_type
    * @method generateDefaultColumnConfig
    * @param  {object} table The table configuration
    * @return {object} element The element fragment
    */
  priv.generateDefaultColumnConfig = function (table, gadget_id) {
    var element = priv.generateElement("form",
      {"className": "draggable"}, {"data-sortable":"true"}, {}
    );

    for (property in table) {
      if (table.hasOwnProperty(property)) {
        field = table[property];
        if (field.show) {
          element.appendChild(priv.generateConfigCriteria("none", gadget_id, property));
        }
      }
    }

    return element;
  };



  /* ********************************************************************** */
  /*                             login popup                                */
  /* ********************************************************************** */
  // NOTE: This should be loaded as the HTML content of a login gadget
  // TODO: convert to JSON configuration!

  /**
  * Generates the content of the login popup
  * @method generateLoginPopup
  * @return {object} HTML fragment
  */
  priv.generateLoginPopup = function () {
    var popup_element,
      external,
      // NOTE: in case we need a classic login (yet again) uncomment below
      //internal,
      //form,
      //note,
      p,
      img,
      content,
      info,
      hint = document.createDocumentFragment(),
      login_form = document.createDocumentFragment(),
      popup_content = document.createDocumentFragment(),

    img = priv.generateElement(
      "div", {"className": "popup_element logo_wrap"}
    );
    img.appendChild(priv.generateElement(
      "img", {"src":"img/slapos.png", "alt": "slapos logo"}
    ));
    popup_content.appendChild(img);

    login_form.appendChild(priv.generateElement(
      "p",{},{},{"text":"Sign in using"}
    ));
    external = priv.generateElement(
      "div",
      {"className":"ui-controlgroup"},
      {"data-role":"controlgroup"}
    );
    //internal = external.cloneNode();
    external.appendChild(priv.generateElement(
      "a",
      {"href":"#", "className":"signin_google ui-link ui-btn ui-icon-google-plus-sign ui-btn-icon-left ui-first-child"},
      {"data-role":"button", "data-icon":"google-plus-sign", "data-iconpos":"left", "data-enhanced":"true"},
      {"text":"Google"}
    ));
    external.appendChild(priv.generateElement(
      "a",
      {"href":"#", "className":"signin_fb ui-link ui-btn ui-icon-facebook-sign ui-btn-icon-left"},
      {"data-role":"button", "data-icon":"facebook-sign", "data-iconpos":"left", "data-enhanced":"true"},
      {"text":"Facebook"}
    ));
    external.appendChild(priv.generateElement(
      "a",
      {"href":"#", "className":"signin_browser ui-link ui-btn ui-icon-lock ui-btn-icon-left ui-last-child"},
      {"data-role":"button", "data-icon":"lock", "data-iconpos":"left", "data-enhanced":"true"},
      {"text":"Browser ID"}
    ));
    login_form.appendChild(external);
//     // classic login
//     login_form.appendChild(priv.generateElement(
//       "p", {},{},{"text":"Classic Login"}
//     ));
//     form = priv.generateElement("form");
//     internal.appendChild(priv.generateElement(
//       "label",
//       {"className":"ui-hidden-accessible"},
//       {"for":"login", "data-i18n":"generic.text.login"},
//       {"text":"Login"}
//     ));
//     internal.appendChild(priv.generateElement(
//       "input",
//       {"name":"login", "id":"login", "type":"text"},
//       {
//         "placeholder":"Login",
//         "data-icon":"user",
//         "data-i18n":"[placeholder]generic.text.login;generic.text.login"
//       }
//     ));
//     internal.appendChild(priv.generateElement(
//       "label",
//       {"className":"ui-hidden-accessible"},
//       {"for":"password","data-i18n":"generic.text.password"},
//       {"text":"Password"}
//     ));
//     internal.appendChild(priv.generateElement(
//       "input",
//       {"name":"password", "id":"password", "type":"password"},
//       {
//         "placeholder":"Password",
//         "data-icon":"lock"
//         "data-i18n":"[placeholder]generic.text.password;generic.text.password"
//       }
//     ));
//     internal.appendChild(priv.generateElement(
//       "label",
//       {"className":"ui-hidden-accessible"},
//       {"for":"submit","data-i18n":"generic.text.go"},
//       {"text":"Go"}
//     ));
//     internal.appendChild(priv.generateElement(
//       "input",
//       {
//         "className":"submit_form",
//         "name":"submit",
//         "id":"submit",
//         "type":"button",
//         "value":"submit"},
//       {"data-i18n":"[placeholder]generic.text.go;generic.text.go"}
//     ));
//     form.appendChild(internal);
//     login_form.appendChild(form)
//     note = priv.generateElement(
//       "span", {"className":"mini right note"}
//     );
//     note.appendChild(
//       priv.generateElement(
//       "a", {"href":"#"},{},{"text":"Forgot Password"}
//       )
//     );
//     login_form.appendChild(note);
    content = priv.generateElement(
      "div", {"className": "popup_element"}
    );
    content.appendChild(login_form);
    popup_content.appendChild(content);
    p = priv.generateElement("p", {"className":"mini"});
    p.appendChild(
      priv.generateElement(
        "span", {"className":"note"},{},{"text":"Please note:"}
      )
    );
    p.appendChild(
      priv.generateElement(
        "span",
        {
          "innerHTML":"To maintain sufficient resources, a minimal fee of 1 " +
          "EUR will be charged if you use SlapOS services for <strong>more " +
          " than 24 hours</strong>. By clicking on one of the signup " +
          "buttons, you agree that you are subscribing to a payable service." +
          " All services you request will be invoiced to you at the end of" +
          " the month."
        }
      )
    );
    hint.appendChild(p);
    hint.appendChild(priv.generateElement(
      "p", {},{},{"text":"To find out more, please refer to"}
    ));
    hint.appendChild(priv.generateElement(
      "a",
      {
        "href":"#",
        "className":"ui-btn ui-btn-icon-left ui-icon-eur ui-shadow ui-corner-all"
      },
      {"data-i18n":"generic.text.pricing"},
      {"text":"SlapOS Pricing"}
    ));

    info = priv.generateElement(
      "div", {"className": "popup_element"}
    );
    info.appendChild(hint);
    popup_content.appendChild(info);

    return popup_content;
  };


//   /* ====================================================================== */
//   /*                             TRASH BUT STILL HERE                       */
//   /* ====================================================================== */
//   // this invokes all gadgets on a page
//   // TODO: should be done differently, the data-gadget property is only used
//   // here to pick the correct function. Later on, the function should be
//   // called form inside the gadget
//   $(document).on("pagebeforeshow", "#computer", function (e, data) {
//     // NOTE: it should not be necessary to fetch this data from the URL
//     // because JQM should pass it in data, too
//     var /*mode*/,
//       item,
//       properties = {},
//       parameters = decodeURIComponent(
//         $.mobile.path.parseUrl(window.location.href).search.split("?")[1]
//       ).split("&");
//
//       mode = parameters[0].split("=")[1];
//       if (parameters.length > 1) {
//         item = parameters[1].split("=")[1];
//       }
//
//     $(".erp5_single").each(function (index, element) {
//       // load data
//       if (mode === "get" || mode === "clone") {
//         priv.erp5.get({"_id": item}, function (error, response) {
//           if (response) {
//             // set to properties, so response
//             properties = {};
//             priv.constructTabs(element, mode, item, properties);
//           } else {
//             abort = confirm("Error trying to retrieve data! Go back to overview?");
//             if (abort === true) {
//               $.mobile.changePage("computers.html", {"rel":"back"});
//             }
//           }
//         });
//       } else {
//         priv.constructTabs(element, mode, item, properties);
//       }
//     });
//
//     // we can set later
//     // priv.generateItem(mode, item);
//   })
//   /* ====================================================================== */
//   /*                             BINDINGS                                   */
//   /* ====================================================================== */
//   // NOTE: should also not be done here, but in the respective gadget
//   // NOTE: still if a form contains 10 relationfields, we should not generate
//   // 10 popups and handlers, but only use a single popup shared across all
//   // load item from table
//   .on("click", "table tbody td a, .navbar li a.new_item", function (e) {
//     var i,
//       item,
//       spec = {},
//       url = e.target.getAttribute("href").split("?"),
//       target = url[0],
//       parameters = url[1].split("&");
//
//     e.preventDefault();
//     for (i = 0; i < parameters.length; i += 1) {
//       item = parameters[i].split("=");
//       spec[item[0]] = item[1];
//     }
//
//     $.mobile.changePage(target, {
//       "transition": "fade",
//       "data": spec
//     });
//   })
//   .on("click", "a.remove_item", function (e) {
//     var i,
//       params = priv.splitSearchParams(),
//       callback = function () {
//         $.mobile.changePage("computers.html", {
//           "transition":"fade",
//           "reverse": "true"
//         });
//       };
//
//     // item in URL?
//     for (i = 0; i < params.length; i += 1) {
//       parameter = params[i].split("=");
//       if (parameter[0] === "item") {
//         priv.modifyObject({"_id": decodeURIComponent(parameter[1])}, "remove", callback );
//       }
//     }
//   })
//   // save form
//   .on("click", "a.save_object", function (e) {
//     var i,
//       parameter,
//       method,
//       object,
//       // check the URL for the state we are in
//       // NOTE: not nice, change later
//       params = priv.splitSearchParams(),
//       callback = function () {
//         $.mobile.changePage("computers.html", {
//           "transition":"fade",
//           "reverse":"true"
//         });
//       };
//
//     for (i = 0; i < params.length; i += 1) {
//       parameter = params[i].split("=");
//       if (parameter[0] === "mode") {
//         switch (parameter[1]) {
//           case "edit":
//             method = "put";
//             break;
//           case "clone":
//           case "add":
//             method = "post";
//             break;
//         }
//         if (method !== undefined) {
//           object = priv.validateObject(
//             priv.serializeObject($(".display_object"))
//           );
//           // fallback to eliminate _id on clone
//           // TODO: do somewhere else!
//           if (method === "post") {
//             delete object._id;
//           }
//           priv.modifyObject(object, method, callback);
//         } else {
//           alert("missing command!, cannot store");
//         }
//       }
//     }
//   })
//   // update navbar depending on item selected
//   .on("change", "table tbody th input[type=checkbox]", function(e) {
//     var allChecks = $(e.target).closest("tbody").find("th input[type=checkbox]:checked"),
//       selected = allChecks.length,
//       trigger = $(".navbar .new_item");
//
//     if (selected === 1) {
//       trigger.addClass("ui-btn-active clone_item").attr("href","computer.html?mode=clone&item=" + e.target.id);
//     } else {
//       trigger.removeClass("ui-btn-active clone_item").attr("href","computer.html?mode=add");
//     }
//
//   });






 




  //       //TODO: can't set bindings, because we don't have a parent?
  //       // or always set on document for local and global should be autoset?
  //       // popup content handling
  //       if (search_popup) {
  //         $parent.on("click", "a.extended_search", function (e) {
  //           priv.generatePopupContents(e, "self", portal_type, settings.view, gadget_id);
  //         });
  //       }
  //
  //       // table actions
  //       if (search_popup) {
  //         // NOTE: can't bind to $parent, because JQM moves the popup
  //         // outside of $parent
  //         page = $parent.closest("div.ui-page");
  //
  //         if (page.data("bindings") === undefined) {
  //           page.data("bindings", {});
  //         }
  //         if (page.data("bindings")["table_action"] === undefined) {
  //           page.data("bindings")["table_action"] = true;
  //
  //           $(document).on("click", "a.table_action", function (e) {
  //             var target,
  //               action = e.target.getAttribute("data-action"),
  //               popup = $(e.target).closest(".ui-popup"),
  //               form = popup.find("form");
  //
  //             if (form.length === 0) {
  //               target = popup.find(".ui-content");
  //             } else {
  //               target = form;
  //             }
  //             switch (action) {
  //               case "add_criteria_search":
  //                 target.append(priv.generateSearchCriteria(e.target))
  //                   .enhanceWithin();
  //               break;
  //
  //               case "add_criteria_config":
  //                 target.append(priv.generateConfigCriteria(e.target))
  //                   .enhanceWithin();
  //               break;
  //               case "delete_criteria":
  //                 $(e.target).closest("div.ui-grid-row").remove();
  //               break;
  //             }
  //           });
  //         }
  //       }
  //
//   });

