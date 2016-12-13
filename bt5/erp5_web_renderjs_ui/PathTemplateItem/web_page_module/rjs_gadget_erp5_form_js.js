/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, RSVP*/
(function (window, document, rJS, RSVP) {
  "use strict";


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
    }
    return field_url;
  }


  function addField(field, rendered_form, form_definition, form_gadget, group, modification_dict) {
    if (rendered_form.hasOwnProperty(field[0])) {
      // Field is enabled in this context
      var sandbox = "public",
        field_element = document.createElement("div"),
        renderered_field = rendered_form[field[0]],
        // suboptions = options[renderered_field.key] || suboption_dict;
        suboptions = {};

      // XXX Hardcoded for searchfield - remove later!
      if (form_definition.extended_search) {
        suboptions.extended_search = form_definition.extended_search;
      }
      // XXX Hardcoded for listbox's hide functionality
      suboptions.hide_enabled = form_definition.hide_enabled;

      suboptions.field_url = getFieldTypeGadgetUrl(renderered_field.type);
      suboptions.label = false;
      suboptions.field_json = renderered_field;
      suboptions.field_json.view = form_gadget.state.view;

      if (group[0] !== "bottom") {
        suboptions.label = true;
      }

      return new RSVP.Queue()
        .push(function () {
          if (modification_dict.hasOwnProperty('hash')) {
            return form_gadget.declareGadget('gadget_erp5_label_field.html', {
              scope: renderered_field.key,
              element: field_element,
              sandbox: sandbox
            });
          }
          return form_gadget.getDeclaredGadget(renderered_field.key);
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
          // return fieldset_element;
          // fieldset_element.appendChild(field_element);
        });
    }
  }


  function addGroup(group, rendered_form, form_definition, form_gadget, modification_dict) {
    // XXX: > Romain: fieldset will be needed later for menus
    var fieldset_element = document.createElement("div"),
      promise_field_list = [],
      j;

    fieldset_element.setAttribute("class", group[0]);

    for (j = 0; j < group[1].length; j += 1) {
      promise_field_list.push(addField(group[1][j], rendered_form, form_definition, form_gadget, group, modification_dict));
    }
    return new RSVP.Queue()
      .push(function () {
        return RSVP.all(promise_field_list);
      })
      .push(function (result_list) {
        var i;
        for (i = 0; i < result_list.length; i += 1) {
          if (result_list[i]) {
            fieldset_element.appendChild(result_list[i]);
          }
        }
        return fieldset_element;
      });
  }


  rJS(window)
    .ready(function (g) {
      g.props = {};
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
        rendered_form = options.erp5_document._embedded._view,
        i,
        j,
        hash = "";

      // Check the list of field to render
      // If the list is different, DOM content will be dropped
      // and recreated
      for (i = 0; i < group_list.length; i += 1) {
        hash += group_list[i][0];
        for (j = 0; j < group_list[i][1].length; j += 1) {
          if (rendered_form.hasOwnProperty(group_list[i][1][j][0])) {
            hash += group_list[i][1][j][0];
          }
        }
      }

      return this.changeState({
        erp5_document: options.erp5_document,
        form_definition: options.form_definition,
        hash: hash,
        view: options.view
      });
    })

    .onStateChange(function (modification_dict) {
      var erp5_document = this.state.erp5_document,
        form_definition = this.state.form_definition,
        rendered_form = erp5_document._embedded._view,
        group_list = form_definition.group_list,
        form_gadget = this;

      if (modification_dict.hasOwnProperty('hash')) {
        form_gadget.props.gadget_list = [];
      }

      return new RSVP.Queue()
        .push(function () {
          var group_promise_list = [],
            j;
          for (j = 0; j < group_list.length; j += 1) {
            group_promise_list.push(addGroup(group_list[j], rendered_form, form_definition, form_gadget, modification_dict));
          }
          return RSVP.all(group_promise_list);
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