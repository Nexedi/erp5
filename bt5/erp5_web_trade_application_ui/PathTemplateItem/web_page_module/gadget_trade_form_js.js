/*jslint nomen: true, indent: 2, maxerr: 3 */
/*global window, document, rJS, RSVP*/
(function (window, document, rJS, RSVP) {
  "use strict";

  /////////////////////////////////////////////////////////////////
  // Handlebars
  /////////////////////////////////////////////////////////////////
  // Precompile the templates while loading the first gadget instance
  var gadget_klass = rJS(window);

  function getFieldTypeGadgetUrl(type) {
    var field_url = 'gadget_erp5_field_readonly.html';
    if (type === 'ListField') {
      field_url = 'gadget_trade_field_list.html';
    } else if ((type === 'ParallelListField') ||
               (type === 'MultiListField')) {
      field_url = 'gadget_erp5_field_multilist.html';
    } else if (type === 'CheckBoxField') {
      field_url = 'gadget_erp5_field_checkbox.html';
    } else if (type === 'MultiCheckBoxField') {
      field_url = 'gadget_erp5_field_multicheckbox.html';
    } else if (type === 'StringField') {
      field_url = 'gadget_trade_field_string.html';
    } else if (type === 'PasswordField') {
      field_url = 'gadget_erp5_field_password.html';
    } else if (type === 'RelationStringField') {
      field_url = 'gadget_erp5_field_relationstring.html';
    } else if (type === 'MultiRelationStringField') {
      field_url = 'gadget_erp5_field_multirelationstring.html';
    } else if (type === 'TextAreaField') {
      field_url = 'gadget_erp5_field_textarea.html';
    } else if (type === 'DateTimeField') {
      field_url = 'gadget_trade_field_datetime.html';
    } else if (type === 'FloatField') {
      field_url = 'gadget_erp5_field_float.html';
    } else if (type === 'FileField') {
      field_url = 'gadget_erp5_field_file.html';
    } else if (type === 'IntegerField') {
      field_url = 'gadget_erp5_field_integer.html';
    } else if (type === 'ListBox') {
      field_url = 'gadget_erp5_field_listbox.html';
    } else if (type === 'EditorField') {
      field_url = 'gadget_erp5_field_textarea.html';
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

  gadget_klass
    /////////////////////////////////////////////////////////////////
    // ready
    /////////////////////////////////////////////////////////////////
    // Init local properties
    .ready(function (g) {
      g.props = {};
    })

    // Assign the element to a variable
    .ready(function (g) {
      return g.getElement()
        .push(function (element) {
          g.props.element = element;
        });
    })

    .declareAcquiredMethod("inputChange", "inputChange")
    .declareAcquiredMethod("translateHtml", "translateHtml")
    .allowPublicAcquisition("notifyInvalid", function (param_list, scope) {
      return this.getDeclaredGadget(scope)
        .push(function (gadget) {
          return gadget.getElement();
        })
        .push(function (gadget_element) {
          gadget_element.previousElementSibling.querySelector("span").textContent = " (" + param_list[0] + ")";
        });
    })

    .allowPublicAcquisition("notifyValid", function (param_list, scope) {
      /*jslint unparam:true*/
      return this.getDeclaredGadget(scope)
        .push(function (gadget) {
          return gadget.getElement();
        })
        .push(function (gadget_element) {
          gadget_element.previousElementSibling.querySelector("span").textContent = "";
        });
    })

    .allowPublicAcquisition("getFieldTypeGadgetUrl", function (param_list) {
      return getFieldTypeGadgetUrl(param_list[0]);
    })
    .allowPublicAcquisition("getFormContent", function (param_list) {
      return this.getContent(param_list[0]);
    })
    .allowPublicAcquisition("inputChange", function (param_list, scope) {
      return this.inputChange(param_list[0], scope);
    })

    /////////////////////////////////////////////////////////////////
    // declared methods
    /////////////////////////////////////////////////////////////////
    .declareMethod('render', function (options) {
      var i,
        erp5_document = options.erp5_document,
        form_definition = options.form_definition,
        rendered_form = erp5_document._embedded._view,
        group_list,
        add_new_field = 1,
        queue = new RSVP.Queue(),
        form_gadget = this,
        suboption_dict = {},
        parent_element = document.createElement("div");

      delete options.erp5_document;
      delete options.form_definition;

      if (options.gadget_created !== undefined) {
        return queue
          .push(function () {
            return form_gadget.getDeclaredGadget(options.gadget_created);
          })
          .push(function (field_gadget) {
            return field_gadget.render(rendered_form);
          });
      }
      group_list = form_definition.group_list;
       //options = options.form_gadget || {};
      form_gadget.state_parameter_dict = options.form_gadget || {};
      // XXX Hardcoded for searchfield - remove later!
      if (form_definition.extended_search) {
        suboption_dict.extended_search = form_definition.extended_search;
      }
      // XXX Hardcoded for listbox's hide functionality
      suboption_dict.hide_enabled = form_definition.hide_enabled;


      if (form_gadget.props.gadget_list === undefined) {
        form_gadget.props.gadget_list = [];
        add_new_field = 0;
      }
      form_gadget.props.id = options.jio_key;

      function addGroup(group) {
        queue
          .push(function () {
            var j,
              // XXX: > Romain: fieldset will be needed later for menus
              fieldset_element,
              group_queue = new RSVP.Queue();
            if (add_new_field) {
              fieldset_element = form_gadget.props
                .element.querySelector("." + group[0]);
            } else {
              fieldset_element = document.createElement("div");
              fieldset_element.setAttribute("class", group[0]);
            }
            function addField(field) {
              group_queue.push(function () {
                if (rendered_form.hasOwnProperty(field[0])) {
                  // Field is enabled in this context
                  var field_queue = new RSVP.Queue(),
                    sandbox = "public",
                    field_url,
                    // Don't change the structure without changing notifyValid and notifyInvalid
                    field_element = document.createElement("div"),
                    gadget_element = document.createElement("div"),
                    label_element = document.createElement("label"),
                    error_element = document.createElement("span"),
                    renderered_field = rendered_form[field[0]];

                  field_element.className = "ui-field-contain";
                  if (renderered_field.hidden === 1) {
                    // Hide field
                    field_element.className = field_element.className + " ui-screen-hidden";
                  }
//                   field_element.setAttribute('data-role', 'fieldcontain');
                  label_element.setAttribute('for', renderered_field.key);
                  label_element.textContent = renderered_field.title;
                  label_element.setAttribute('data-i18n', renderered_field.title);
                  if (renderered_field.hasOwnProperty('error_text')) {
                    error_element.textContent = " (" + renderered_field.error_text + ")";
                  }
                  // error_element.setAttribute('class', 'ui-state-error ui-corner-all');
                  label_element.appendChild(error_element);
                  if (group[0] !== "bottom") {
                    field_element.appendChild(label_element);
                  }

                  field_url = getFieldTypeGadgetUrl(renderered_field.type);

                  return field_queue
                    .push(function () {
                      return form_gadget.translateHtml(field_element.innerHTML);
                    })
                    .push(function (my_translate_html) {
                      field_element.innerHTML = my_translate_html;
                      field_element.appendChild(gadget_element);
                      fieldset_element.appendChild(field_element);
                    })
                    .push(function () {
                      return form_gadget.declareGadget(field_url, {
                        scope: renderered_field.key,
                        element: gadget_element,
                        sandbox: sandbox
                      });
                    })
                    .push(function (field_gadget) {
                      //XXXXX Hardcoded to get one listbox gadget
                      //pt form list gadget will get this listbox's info
                      //then pass to search field gadget
                      if (field_url === "gadget_erp5_field_listbox.html") {
                        form_gadget.props.listbox_gadget = field_gadget;
                      }
                      form_gadget.props.gadget_list.push(field_gadget);
                      var suboptions = options[renderered_field.key] || suboption_dict;
                      suboptions.field_json = renderered_field;
                      suboptions.field_json.view = options.view;
                      return field_gadget.render(suboptions);
                    });
                }
              });
            }

            for (j = 0; j < group[1].length; j += 1) {
              addField(group[1][j]);
            }
            return group_queue.push(function () {
              parent_element.appendChild(fieldset_element);
            });
          });
      }

      for (i = 0; i < group_list.length; i += 1) {
        addGroup(group_list[i]);
      }

      return queue
        .push(function () {
          var dom_element = form_gadget.props.element
            .querySelector(".field_container");
          while (dom_element.firstChild) {
            dom_element.removeChild(dom_element.firstChild);
          }
          dom_element.appendChild(parent_element);
          // return $(parent_element).trigger("create");

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