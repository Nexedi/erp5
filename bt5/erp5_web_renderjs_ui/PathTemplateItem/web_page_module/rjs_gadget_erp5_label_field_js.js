/*global window, document, rJS, RSVP */
/*jslint indent: 2, maxerr: 3 */
/**
 * Label gadget takes care of displaying validation errors and label.
 *
 * Every form field is wrapped in that widget which has some consequences:
 *
 * -  CSS classes sharing: label copy CSS classes of embedded field for itself
 *    because CSS selectors are not good in selectin up the DOM tree
 *    -  class "invisible" despite its name is supposed to hide only label
 *    -  class "horizontal_align_form_box" will prevent any label to show as well
 *
 */
(function (window, document, rJS, RSVP) {
  "use strict";

  var SCOPE = 'field';

  function getFieldTypeGadgetUrl(field_type) {
    var field_url = 'gadget_erp5_field_readonly.html';
    if (field_type === 'ListField') {
      field_url = 'gadget_erp5_field_list.html';
    } else if ((field_type === 'ParallelListField') ||
               (field_type === 'MultiListField')) {
      field_url = 'gadget_erp5_field_multilist.html';
    } else if (field_type === 'CheckBoxField') {
      field_url = 'gadget_erp5_field_checkbox.html';
    } else if (field_type === 'MultiCheckBoxField') {
      field_url = 'gadget_erp5_field_multicheckbox.html';
    } else if (field_type === 'StringField') {
      field_url = 'gadget_erp5_field_string.html';
    } else if (field_type === 'LinesField') {
      field_url = 'gadget_erp5_field_lines.html';
    } else if (field_type === 'PasswordField') {
      field_url = 'gadget_erp5_field_password.html';
    } else if (field_type === 'RelationStringField') {
      field_url = 'gadget_erp5_field_relationstring.html';
    } else if (field_type === 'MultiRelationStringField') {
      field_url = 'gadget_erp5_field_multirelationstring.html';
    } else if (field_type === 'TextAreaField') {
      field_url = 'gadget_erp5_field_textarea.html';
    } else if (field_type === 'DateTimeField') {
      field_url = 'gadget_erp5_field_datetime.html';
    } else if (field_type === 'FloatField') {
      field_url = 'gadget_erp5_field_float.html';
    } else if (field_type === 'FileField') {
      field_url = 'gadget_erp5_field_file.html';
    } else if (field_type === 'IntegerField') {
      field_url = 'gadget_erp5_field_integer.html';
    } else if (field_type === 'ListBox') {
      field_url = 'gadget_erp5_field_listbox.html';
    } else if (field_type === 'EditorField') {
      field_url = 'gadget_erp5_field_editor.html';
      // field_url = 'gadget_codemirror.html';
      // sandbox = 'iframe';
    } else if (field_type === 'GadgetField') {
      field_url = 'gadget_erp5_field_gadget.html';
    } else if (field_type === 'RadioField') {
      field_url = 'gadget_erp5_field_radio.html';
    } else if (field_type === 'ImageField') {
      field_url = 'gadget_erp5_field_image.html';
    } else if (field_type === 'EmailField') {
      field_url = 'gadget_erp5_field_email.html';
    } else if (field_type === 'FormBox') {
      field_url = 'gadget_erp5_field_formbox.html';
    } else if (field_type === 'MatrixBox') {
      field_url = 'gadget_erp5_field_matrixbox.html';
    }
    return field_url;
  }

  rJS(window)
    .setState({
      label_text: '',
      error_text: '',
      label: true,  // the label element is already present in the HTML template
      css_class: ''
    })

    .ready(function () {
      return this.changeState({
        container_element: this.element.querySelector('div'),  // matches the closest div
        label_element: this.element.querySelector('label')
      });
    })

    .declareMethod('render', function (options) {
      var state_dict = {
        label_text: options.field_json.title || '',
        label: options.label,
        field_url: getFieldTypeGadgetUrl(options.field_type),
        error_text: options.field_json.error_text || '',
        options: options,
        scope: options.field_json.key,
        hidden: options.field_json.hidden,
        css_class: options.field_json.css_class
      };
      // RenderJS would overwrite default value with empty variables :-(
      // So we have to mitigate this behaviour
      if (state_dict.label === undefined) {
        state_dict.label = true;
      }
      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var gadget = this,
        span;

      if (gadget.state.hidden) {
        this.element.hidden = true;
      } else {
        this.element.hidden = false;
      }

      if (modification_dict.hasOwnProperty('label_text')) {
        this.state.label_element.textContent = this.state.label_text;
      }
      this.state.label_element.setAttribute('for', gadget.state.scope);

      if (modification_dict.hasOwnProperty('css_class') && this.state.css_class) {
        this.state.label_element.classList.add(this.state.css_class);
      }

      if (modification_dict.hasOwnProperty('error_text')) {
        // first remove old errors
        span = this.state.container_element.querySelector('span');
        if (span) {
          this.state.container_element.removeChild(span);
        }
        // display new error if present
        if (this.state.error_text) {
          span = document.createElement('span');
          span.textContent = this.state.error_text;
          this.state.container_element.appendChild(span);
        }
      }

      // Remove/add label_element from DOM
      if (modification_dict.hasOwnProperty('label')) {
        if (this.state.label === true) {
          this.state.container_element.insertBefore(this.state.label_element, this.state.container_element.firstChild);
        } else {
          this.state.container_element.removeChild(this.state.label_element);
        }
      }

      if (modification_dict.hasOwnProperty('options')) {
        if (this.state.field_url) {
          return new RSVP.Queue()
            .push(function () {
              if (modification_dict.hasOwnProperty('field_url')) {
                return gadget.declareGadget(gadget.state.field_url, {
                  scope: SCOPE
                })
                  .push(function (field_gadget) {
                    gadget.state.container_element.removeChild(
                      gadget.state.container_element.querySelector('div')
                    );
                    gadget.state.container_element.appendChild(field_gadget.element);
                    return field_gadget;
                  });
              }
              return gadget.getDeclaredGadget(SCOPE);
            })
            .push(function (field_gadget) {
              return field_gadget.render(gadget.state.options);
            });
        }
      }
    })

    .declareMethod("checkValidity", function () {
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          // XXX Implement checkValidity on all fields
          if (gadget.checkValidity !== undefined) {
            return gadget.checkValidity();
          }
          return true;
        });
    })

    .declareMethod('getContent', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          if (gadget.getContent !== undefined) {
            return gadget.getContent.apply(gadget, argument_list);
          }
          return {};
        });
    })

    .declareMethod('getListboxInfo', function () {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          return gadget.getListboxInfo.apply(gadget, argument_list);
        });
    })

    .allowPublicAcquisition("notifyInvalid", function (param_list) {
      return this.changeState({error_text: param_list[0]});
    })

    .allowPublicAcquisition("notifyValid", function () {
      return this.changeState({error_text: ''});
    });

}(window, document, rJS, RSVP));