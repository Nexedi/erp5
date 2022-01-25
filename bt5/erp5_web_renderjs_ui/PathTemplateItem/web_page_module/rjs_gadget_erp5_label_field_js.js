/*global window, document, rJS, domsugar, HTMLLabelElement*/
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
(function (window, document, rJS, domsugar, HTMLLabelElement) {
  "use strict";

  var SCOPE = 'field';

  function getFieldTypeGadgetUrl(field_type) {
    var field_url = 'gadget_erp5_field_readonly.html';
    if (field_type === 'ListField') {
      field_url = 'gadget_erp5_field_list.html';
    } else if (field_type === 'MultiListField') {
      field_url = 'gadget_erp5_field_multilist.html';
    } else if (field_type === 'ParallelListField') {
      field_url = 'gadget_erp5_field_parallellist.html';
    } else if (field_type === 'CheckBoxField') {
      field_url = 'gadget_erp5_field_checkbox.html';
    } else if (field_type === 'MultiCheckBoxField') {
      field_url = 'gadget_erp5_field_multicheckbox.html';
    } else if (field_type === 'StringField') {
      field_url = 'gadget_erp5_field_string.html';
    } else if (field_type === 'HyperLinkField') {
      field_url = 'gadget_erp5_field_hyperlink.html';
    } else if (field_type === 'LinkField') {
      field_url = 'gadget_erp5_field_link.html';
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
    } else if (field_type === 'LabelField') {
      field_url = 'gadget_erp5_field_label.html';
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

  function addDeveloperAction(class_name, title_href, title, root_element) {
    var div,
      field_href = domsugar("a", {
        "class": class_name,
        href: title_href,
        title: title
      });
    if (root_element.constructor === HTMLLabelElement) {
      root_element.appendChild(field_href);
      return;
    }
    div = root_element.querySelector("div");
    if (div) {
      root_element.insertBefore(field_href, div);
    }
  }

  rJS(window)
    .setState({
      label_text: '',
      error_text: '',
      label: true,  // the label element is already present in the HTML template
      css_class: '',
      display_error_text: false,
      first_call: false
    })
    //////////////////////////////////////////////
    // acquired method
    //////////////////////////////////////////////
    .declareAcquiredMethod("getTranslationList", "getTranslationList")

    .declareMethod('render', function render(options) {
      var state_dict = {
        first_call: true,
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

    .onStateChange(function onStateChange(modification_dict) {
      var gadget = this,
        options = modification_dict.options || {},
        field_json = options.field_json,
        field_gadget,
        span,
        css_class,
        i,
        queue,
        new_div;

      if (modification_dict.hasOwnProperty('first_call')) {
        gadget.props = {
          container_element: gadget.element.querySelector('div'),
          label_element: gadget.element.querySelector('label')
        };
      }
      if (gadget.state.hidden && !gadget.state.error_text) {
        this.element.hidden = true;
      } else {
        this.element.hidden = false;
      }

      if (modification_dict.hasOwnProperty('label_text')) {
        this.props.label_element.textContent = this.state.label_text;
      }
      this.props.label_element.setAttribute('for', gadget.state.scope);

      if (modification_dict.hasOwnProperty('css_class') && this.state.css_class) {
        css_class = this.state.css_class.split(' ');
        for (i = 0; i < css_class.length; i += 1) {
          this.element.classList.add(css_class[i]);
        }
      }

      // Remove/add label_element from DOM
      if (modification_dict.hasOwnProperty('label')) {
        if (this.state.label === true) {
          this.props.container_element.insertBefore(this.props.label_element, this.props.container_element.firstChild);
        } else {
          this.props.container_element.removeChild(this.props.label_element);
        }
      }

      if (this.state.error_text && this.props.label_element &&
          !this.props.label_element.classList.contains("is-invalid")) {
        this.props.label_element.classList.add("is-invalid");
      } else if (!this.state.error_text &&
                 this.props.label_element.classList.contains("is-invalid")) {
        this.props.label_element.classList.remove("is-invalid");
      }

      if (modification_dict.hasOwnProperty('display_error_text') || modification_dict.hasOwnProperty('error_text')) {
        // first remove old errors
        span = this.props.container_element.lastElementChild;
        if ((span !== null) && (span.tagName.toLowerCase() !== 'span')) {
          span = null;
        }
        // display new error if present
        if (this.state.error_text && this.state.display_error_text) {
          if (span === null) {
            span = document.createElement('span');
            span.textContent = this.state.error_text;
            this.props.container_element.appendChild(span);
          } else {
            span.textContent = this.state.error_text;
          }
        } else {
          if (span !== null) {
            this.props.container_element.removeChild(span);
          }
        }
      }
      if (modification_dict.hasOwnProperty('options')) {
        if (this.state.field_url) {
          if (modification_dict.hasOwnProperty('field_url')) {
            gadget.props.container_element.removeChild(
              gadget.props.container_element.querySelector('div')
            );
            new_div = document.createElement('div');
            span = gadget.props.container_element.lastElementChild;
            if ((span !== null) && (span.tagName.toLowerCase() !== 'span')) {
              span = null;
            }
            if (span === null) {
              gadget.props.container_element.appendChild(new_div);
            } else {
              gadget.props.container_element.insertBefore(
                new_div,
                span
              );
            }
            queue = gadget.declareGadget(gadget.state.field_url, {
              scope: SCOPE,
              element: new_div
            });
          } else {
            queue = gadget.getDeclaredGadget(SCOPE);
          }

          queue
            .push(function (declared_gadget) {
              field_gadget = declared_gadget;
            });
          if (field_json && gadget.state.options.development_link !== false) {
            queue
              .push(function () {
                return gadget.getTranslationList([
                  "Edit this field",
                  "Translate this field title",
                  "Translate this field description"
                ]);
              })
              .push(function (translation_list) {
                var root_element,
                  field;

                if (gadget.state.label === true) {
                  root_element = gadget.props.label_element;
                } else {
                  root_element = gadget.element;
                }

                if (field_json.hasOwnProperty('edit_field_href') &&
                    !root_element.querySelector(".edit-field")) {
                  addDeveloperAction(
                    "edit-field ui-icon-edit ui-btn-icon-left",
                    field_json.edit_field_href,
                    translation_list[0],
                    root_element
                  );
                } else if (!field_json.hasOwnProperty('edit_field_href')) {
                  field = root_element.querySelector(".edit-field");
                  if (field) {
                    root_element.removeChild(field);
                  }
                }

                if (field_json.hasOwnProperty('translate_title_href') &&
                    !root_element.querySelector(".translate-title")) {
                  addDeveloperAction(
                    "translate-title ui-icon-language ui-btn-icon-left",
                    field_json.translate_title_href,
                    translation_list[1],
                    root_element
                  );
                } else if (!field_json.hasOwnProperty('translate_title_href')) {
                  field = root_element.querySelector(".translate-title");
                  if (field) {
                    root_element.removeChild(field);
                  }
                }

                if (field_json.hasOwnProperty('translate_description_href') &&
                    !root_element.querySelector(".translate-description")) {
                  addDeveloperAction(
                    "translate-description ui-icon-language ui-btn-icon-left",
                    field_json.translate_description_href,
                    translation_list[2],
                    root_element
                  );
                } else if (!field_json.hasOwnProperty('translate_description_href')) {
                  field = root_element.querySelector(".translate-description");
                  if (field) {
                    root_element.removeChild(field);
                  }
                }
              });
          }
          return queue
            .push(function () {
              return field_gadget.render(gadget.state.options);
            });
        }
      }

    })

    .declareMethod("checkValidity", function checkValidity() {
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          // XXX Implement checkValidity on all fields
          if (gadget.checkValidity !== undefined) {
            return gadget.checkValidity();
          }
          return true;
        });
    }, {mutex: 'changestate'})

    .declareMethod('getContent', function getContent() {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          if (gadget.getContent !== undefined) {
            return gadget.getContent.apply(gadget, argument_list);
          }
          return {};
        });
    }, {mutex: 'changestate'})

    .declareMethod('getListboxInfo', function getListboxInfo() {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          return gadget.getListboxInfo.apply(gadget, argument_list);
        });
    }, {mutex: 'changestate'})

    .declareMethod('getGraphicType', function getGraphicType() {
      var argument_list = arguments;
      return this.getDeclaredGadget(SCOPE)
        .push(function (gadget) {
          return gadget.getGraphicType.apply(gadget, argument_list);
        });
    }, {mutex: 'changestate'})

    .allowPublicAcquisition("notifyFocus", function notifyFocus() {
      return this.changeState({display_error_text: true});
    })

    .allowPublicAcquisition("notifyBlur", function notifyBlur() {
      return this.changeState({display_error_text: false});
    })

    .allowPublicAcquisition("notifyInvalid", function notifyInvalid(param_list) {
      // Label doesn't know when a subgadget calls notifyInvalid
      // Prevent mutex dead lock by defering the changeState call
      return this.deferErrorTextRender(param_list[0]);
    })

    .allowPublicAcquisition("notifyValid", function notifyValid() {
      // Label doesn't know when a subgadget calls notifyValid
      // Prevent mutex dead lock by defering the changeState call
      return this.deferErrorTextRender('');
    })

    .declareJob('deferErrorTextRender', function deferErrorTextRender(error_text) {
      return this.changeState({first_call: true, error_text: error_text});
    });

}(window, document, rJS, domsugar, HTMLLabelElement));