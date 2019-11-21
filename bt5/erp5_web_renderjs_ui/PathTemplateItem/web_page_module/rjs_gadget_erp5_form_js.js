/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, RSVP*/

/** Form is one of a complicated gadget!
 *
 * Editability - the form overrides editability of its fields. Editability is
 *               hard-coded changed either in Page Templates or soft-coded
 *               changed in FormBox gadget which renders form as a subgadget
**/

(function (window, document, rJS, RSVP) {
  "use strict";

  /**
   * Physically append rendered field to DOM.
   *
   * Wraps every field in label gadget.
   * @argument field: array<tuple<str, object>> where first item is name, second meta info of the field
   *           (obsolete to specify the meta information which is returned by JSON style since it is duplicate of information in document instance)
   */
  function addField(field, rendered_document, form_definition, form_gadget, group_name, modification_dict) {
    var field_name = field[0],
      field_element,
      suboptions,
      queue;

    if (!rendered_document.hasOwnProperty(field_name)) {
      return;
    }

    suboptions = {
      hide_enabled: form_definition.hide_enabled, // listbox specific
      configure_enabled: form_definition.configure_enabled, // listbox specific
      extended_search: ((group_name === "bottom") && (form_definition.extended_search)), // searchfield specific
      field_type: rendered_document[field_name].type,
      label: ((group_name !== "bottom") && (rendered_document[field_name].title.length > 0)), // no label for bottom group and field without title
      field_json: rendered_document[field_name] // pass
    };

    // XXX: what is the purpose of this?
    suboptions.field_json.view = form_gadget.state.view;

    // if the whole form is non-editable than every field has to be non-editable
    if (form_gadget.state.editable === 0) {
      suboptions.field_json.editable = 0;
    }

    if (modification_dict.hasOwnProperty('hash')) {
      queue = form_gadget.declareGadget('gadget_erp5_label_field.html', {
        scope: rendered_document[field_name].key, // ugly! Should be just `field_name` but too many tests depend on it
        sandbox: "public"
      });
    } else {
      queue = form_gadget.getDeclaredGadget(rendered_document[field_name].key);
    }
    return queue
      .push(function (label_gadget) {
        if (modification_dict.hasOwnProperty('hash')) {

          // XXX Hardcoded to get one listbox gadget
          //pt form list gadget will get this listbox's info
          //then pass to search field gadget
          if (suboptions.field_type === 'ListBox') {
            form_gadget.props.listbox_gadget = label_gadget;
          }

          // gadget_list hold references to all created gadgets
          form_gadget.props.gadget_list.push(label_gadget);
        }
        if (modification_dict.hasOwnProperty('hash')) {
          field_element = label_gadget.element;
        } else {
          // XXX Investigate why removing this break everything
          // There is not reason to always create a DOM element
          field_element = document.createElement("div");
        }
        return label_gadget.render(suboptions);
      })
      .push(function () {
        return field_element;
      });
  }


  function addGroup(group, rendered_document, form_definition, form_gadget, modification_dict) {
    // XXX: > Romain: fieldset will be needed later for menus
    var fieldset_element = document.createElement("div"),
      group_name = group[0],
      field_list = group[1];

    fieldset_element.setAttribute("class", group_name);

    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(field_list.map(function (field) {
          return addField(field, rendered_document, form_definition, form_gadget, group_name, modification_dict);
        }));
      })
      .push(function (result_list) {
        // append all rendered fields into DOM
        result_list.forEach(function (result) {
          if (result) {fieldset_element.appendChild(result); }
        });
        return fieldset_element;
      });
  }


  rJS(window)
    .ready(function (g) {
      g.props = {
        gadget_list: []  // holds references to all subgadgets to be able to grab their content on submit
      };
    })

    .setState({
      // erp5 document is an instance of a document referenced by jio_key
      erp5_document: undefined,
      jio_key: undefined,
      // form definition holds positioning of fields
      form_definition: undefined,
      view: undefined,  // Kato: still have no idea what that means
      // hash is used to spot changes in positioning of fields
      hash: undefined,
      // attributes of the form - no magic there
      title: undefined,
      editable: undefined
    })

    .allowPublicAcquisition("getFormContent", function (param_list) {
      return this.getContent(param_list[0]);
    })

    .allowPublicAcquisition("getFormDefinition", function getFormDefinition() {
      return JSON.parse(JSON.stringify(this.state.form_definition));
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////

    .declareMethod('render', function (options) {
      var group_list = options.form_definition.group_list,
        rendered_document = options.erp5_document._embedded._view,
        hash = "",
        group_name,
        group_field_list,
        i,
        j;

      // Contruct a hash of <placement>+<field names> to snapshot rendering.
      // The `hash` will make it to the `onStateChange` only if it has changed.
      // If so, DOM content will be dropped and recreated
      for (i = 0; i < group_list.length; i += 1) {
        group_name = group_list[i][0];
        group_field_list = group_list[i][1];
        hash += group_name;

        for (j = 0; j < group_field_list.length; j += 1) {
          if (rendered_document.hasOwnProperty(group_field_list[j][0])) {
            hash += group_field_list[j][0];
          }
        }
      }

      return this.changeState({
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        jio_key: options.jio_key,
        hash: hash,
        view: options.view,
        editable: options.editable,
        title: options.title
      });
    })

    .onStateChange(function (modification_dict) {
      var erp5_document = this.state.erp5_document,
        form_definition = this.state.form_definition,
        rendered_document = erp5_document._embedded._view,
        group_list = form_definition.group_list,
        form_gadget = this,
        tmp;

      if (modification_dict.hasOwnProperty('hash')) {
        form_gadget.props.gadget_list = [];
      }
      /* Update or remove h3 element based on value of `title` */
      if (modification_dict.hasOwnProperty('title')) {
        tmp = this.element.querySelector("h3");
        if (modification_dict.title) {
          if (tmp === null) {
            // create new title element for existing title
            tmp = document.createElement("h3");
            this.element.insertBefore(tmp, this.element.firstChild);
          }
          tmp.textContent = modification_dict.title;
        }
        if (modification_dict.title === null || modification_dict.title === "") {
          // user tends to remove the title
          if (tmp !== null) {tmp.remove(); }
        }
        tmp = undefined;
      }
      return new RSVP.Queue()
        .push(function () {
          return RSVP.all(group_list.map(function (group) {
            return addGroup(group, rendered_document, form_definition, form_gadget, modification_dict);
          }));
        })
        .push(function (result_list) {
          if (modification_dict.hasOwnProperty('hash')) {
            var dom_element = form_gadget.element
              .querySelector(".field_container"),
              j,
              parent_element = document.createDocumentFragment();
            // Add all fieldset into the fragment
            for (j = 0; j < result_list.length; j += 1) {
              parent_element.appendChild(result_list[j]);
            }
            while (dom_element.firstChild) {
              dom_element.removeChild(dom_element.firstChild);
            }
            dom_element.appendChild(parent_element);
          }
        });
    })

    .declareMethod("getListboxInfo", function () {
      //XXXXX get listbox gadget's info
      var gadget = this;
      if (gadget.props.listbox_gadget) {
        return gadget.props.listbox_gadget.getListboxInfo();
      }
      return {};
    }, {mutex: 'changestate'})
    .declareMethod("getContent", function (options) {
      var form_gadget = this,
        k,
        field_gadget,
        count = form_gadget.props.gadget_list.length,
        data = {},
        queue = new RSVP.Queue();
      function extendData(field_data) {
        var key;
        for (key in field_data) {
          if (field_data.hasOwnProperty(key)) {
            data[key] = field_data[key];
          }
        }
      }
      if (options === undefined) {
        options = {
          "format": "erp5"
        };
      }
      for (k = 0; k < count; k += 1) {
        field_gadget = form_gadget.props.gadget_list[k];
        // XXX Hack until better defined
        if (field_gadget.getContent !== undefined) {
          queue
            .push(field_gadget.getContent.bind(field_gadget, options))
            .push(extendData);
        }
      }
      return queue
        .push(function () {
          return data;
        });
    }, {mutex: 'changestate'})
    .declareMethod("checkValidity", function () {
      var form_gadget = this,
        k,
        field_gadget,
        count = form_gadget.props.gadget_list.length,
        result = true,
        queue = new RSVP.Queue();

      function extendData(field_validity) {
        result = result && field_validity;
      }

      for (k = 0; k < count; k += 1) {
        field_gadget = form_gadget.props.gadget_list[k];
        // XXX Hack until better defined
        if (field_gadget.checkValidity !== undefined) {
          queue
            .push(field_gadget.checkValidity.bind(field_gadget))
            .push(extendData);
        }
      }
      return queue
        .push(function () {
          return result;
        });

    }, {mutex: 'changestate'});

}(window, document, rJS, RSVP));
