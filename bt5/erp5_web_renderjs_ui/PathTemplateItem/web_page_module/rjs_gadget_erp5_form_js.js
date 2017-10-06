/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, RSVP*/

(function (window, document, rJS, RSVP) {
  "use strict";

  /** Form is one of a complicated gadget!
   *
   * Editability - the form overrides editability of its fields. Editability is
   *               hard-coded changed either in Page Templates or soft-coded
   *               changed in FormBox gadget which renders form as a subgadget
  **/

  function getFieldTypeGadgetUrl(type) {
    var field_url = 'gadget_erp5_field_readonly.html';
    if (type === 'ListField') {
      field_url = 'gadget_erp5_field_list.html';
    } else if ((type === 'ParallelListField') ||
               (type === 'MultiListField')) {
      field_url = 'gadget_erp5_field_multilist.html';
    } else if (type === 'CheckBoxField') {
      field_url = 'gadget_erp5_field_checkbox.html';
    } else if (type === 'MultiCheckBoxField') {
      field_url = 'gadget_erp5_field_multicheckbox.html';
    } else if (type === 'StringField') {
      field_url = 'gadget_erp5_field_string.html';
    } else if (type === 'PasswordField') {
      field_url = 'gadget_erp5_field_password.html';
    } else if (type === 'RelationStringField') {
      field_url = 'gadget_erp5_field_relationstring.html';
    } else if (type === 'MultiRelationStringField') {
      field_url = 'gadget_erp5_field_multirelationstring.html';
    } else if (type === 'TextAreaField') {
      field_url = 'gadget_erp5_field_textarea.html';
    } else if (type === 'DateTimeField') {
      field_url = 'gadget_erp5_field_datetime.html';
    } else if (type === 'FloatField') {
      field_url = 'gadget_erp5_field_float.html';
    } else if (type === 'FileField') {
      field_url = 'gadget_erp5_field_file.html';
    } else if (type === 'IntegerField') {
      field_url = 'gadget_erp5_field_integer.html';
    } else if (type === 'ListBox') {
      field_url = 'gadget_erp5_field_listbox.html';
    } else if (type === 'EditorField') {
      field_url = 'gadget_erp5_field_editor.html';
      // field_url = 'gadget_codemirror.html';
      // sandbox = 'iframe';
    } else if (type === 'GadgetField') {
      field_url = 'gadget_erp5_field_gadget.html';
    } else if (type === 'RadioField') {
      field_url = 'gadget_erp5_field_radio.html';
    } else if (type === 'ImageField') {
      field_url = 'gadget_erp5_field_image.html';
    } else if (type === 'EmailField') {
      field_url = 'gadget_erp5_field_email.html';
    } else if (type === 'FormBox') {
      field_url = 'gadget_erp5_field_formbox.html';
    }
    return field_url;
  }

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
      suboptions;

    if (!rendered_document.hasOwnProperty(field_name)) {
      return;
    }

    suboptions = {
      hide_enabled: form_definition.hide_enabled, // listbox specific
      extended_search: form_definition.extended_search, // searchfield specific
      field_url: getFieldTypeGadgetUrl(rendered_document[field_name].type),
      label: ((group_name !== "bottom") && (rendered_document[field_name].title.length > 0)), // no label for bottom group and field without title
      field_json: rendered_document[field_name] // pass
    };

    // XXX: what is the purpose of this?
    suboptions.field_json.view = form_gadget.state.view;

    // if the whole form is non-editable than every field has to be non-editable
    if (form_gadget.state.editable === 0) {
      suboptions.field_json.editable = 0;
    }

    field_element = document.createElement("div");
    return new RSVP.Queue()
      .push(function () {
        var rendered_field_name = rendered_document[field_name].key;
        if (modification_dict.hasOwnProperty('hash')) {
          return form_gadget.declareGadget('gadget_erp5_label_field.html', {
            scope: rendered_field_name, // ugly! Should be just `field_name` but too many tests depend on it
            element: field_element,
            sandbox: "public"
          });
        }
        return form_gadget.getDeclaredGadget(rendered_field_name);
      })
      .push(function (label_gadget) {
        if (modification_dict.hasOwnProperty('hash')) {

          // XXX Hardcoded to get one listbox gadget
          //pt form list gadget will get this listbox's info
          //then pass to search field gadget
          if (suboptions.field_url === "gadget_erp5_field_listbox.html") {
            form_gadget.props.listbox_gadget = label_gadget;
          }
          form_gadget.props.gadget_list.push(label_gadget);
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

    .allowPublicAcquisition("getFieldTypeGadgetUrl", function (param_list) {
      return getFieldTypeGadgetUrl(param_list[0]);
    })
    .allowPublicAcquisition("getFormContent", function (param_list) {
      return this.getContent(param_list[0]);
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
        form_gadget = this;

      if (modification_dict.hasOwnProperty('hash')) {
        form_gadget.props.gadget_list = [];
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
    })
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
    })
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

    });

}(window, document, rJS, RSVP));