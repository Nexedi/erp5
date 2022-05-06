/*global window, document, rJS, RSVP, jIO, getFirstNonEmpty */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, document, rJS, RSVP, jIO, getFirstNonEmpty) {
  "use strict";

  function saveAsDataURL(file) {
    return new RSVP.Queue()
      .push(function () {
        return jIO.util.readBlobAsDataURL(file);
      })
      .push(function (evt) {
        return {
          url: evt.target.result,
          file_name: file.name
        };
      });
  }

  rJS(window)
    .declareAcquiredMethod("translate", "translate")
    .declareMethod('render', function render(options) {
      return this.changeState({
        value: getFirstNonEmpty(options.value, ""),
        checked: options.checked,
        editable: options.editable,
        required: options.required,
        id: options.id,
        name: options.name,
        type: options.type || 'text',
        title: options.title,
        focus: options.focus,
        error_text: options.error_text || "",
        step: options.step,
        hidden: options.hidden,
        trim: options.trim || false,
        maxlength: options.maxlength,
        min: options.min,
        max: options.max,
        multiple: options.multiple,
        accept: options.accept,
        capture: options.capture,
        append: options.append, // text to apend after the field
        prepend: options.prepend // text to prepend infront the field
      });
    })

    .onStateChange(function onStateChange(modification_dict) {
      var textarea = this.element.querySelector('input'),
        tmp; // general use short-scope variable

      if (modification_dict.hasOwnProperty('value') ||
          modification_dict.hasOwnProperty('checked') ||
          modification_dict.hasOwnProperty('editable') ||
          modification_dict.hasOwnProperty('required') ||
          modification_dict.hasOwnProperty('id') ||
          modification_dict.hasOwnProperty('name') ||
          modification_dict.hasOwnProperty('type') ||
          modification_dict.hasOwnProperty('title') ||
          modification_dict.hasOwnProperty('focus') ||
          modification_dict.hasOwnProperty('step') ||
          modification_dict.hasOwnProperty('trim') ||
          modification_dict.hasOwnProperty('multiple') ||
          modification_dict.hasOwnProperty('accept') ||
          modification_dict.hasOwnProperty('capture') ||
          modification_dict.hasOwnProperty('append') ||
          modification_dict.hasOwnProperty('prepend')
          ) {

        if (this.state.type === 'checkbox') {
          textarea.checked = this.state.checked;
        } else {
          textarea.setAttribute('value', this.state.value);
          textarea.value = this.state.value;
        }

        if (this.state.type === 'radio') {
          textarea.checked = this.state.checked;
        }
        textarea.id = this.state.id || this.state.name;
        textarea.setAttribute('name', this.state.name);

        textarea.setAttribute('type', this.state.type);
        if (this.state.title) {
          textarea.setAttribute('title', this.state.title);
        }
        if (this.state.step) {
          textarea.setAttribute('step', this.state.step);
        }
        if (this.state.capture) {
          textarea.setAttribute('capture', this.state.capture);
        }
        if (this.state.accept) {
          textarea.setAttribute('accept', this.state.accept);
        }
        if (this.state.maxlength) {
          textarea.setAttribute('maxlength', this.state.maxlength);
        }
        if (this.state.min !== "") {
          textarea.setAttribute('min', this.state.min);
        }
        if (this.state.max !== "") {
          textarea.setAttribute('max', this.state.max);
        }

        if (this.state.multiple) {
          textarea.multiple = true;
        }

        if (this.state.required) {
          textarea.required = true;
        } else {
          textarea.required = false;
        }

        if (this.state.editable) {
          textarea.readonly = true;
        } else {
          textarea.readonly = false;
        }

        if (this.state.focus === true) {
          textarea.autofocus = true;
          textarea.focus();
        }

        if (this.state.focus === false) {
          textarea.autofocus = false;
          textarea.blur();
        }

        if (modification_dict.append) {
          this.element.classList.add('ui-input-has-appendinx');
          tmp = document.createElement('i');
          tmp.appendChild(document.createTextNode(modification_dict.append));
          this.element.appendChild(tmp);
          tmp = undefined;
        }

        if (modification_dict.prepend) {
          this.element.classList.add('ui-input-has-prependinx');
          tmp = document.createElement('i');
          tmp.appendChild(document.createTextNode(modification_dict.append));
          this.element.insertBefore(tmp, textarea);
          tmp = undefined;
        }
      }

      if (modification_dict.hasOwnProperty('error_text') ||
          modification_dict.hasOwnProperty('hidden')) {
        if (this.state.hidden && !this.state.error_text) {
          textarea.hidden = true;
        } else {
          textarea.hidden = false;
        }

        if (this.state.error_text &&
            !textarea.classList.contains("is-invalid")) {
          textarea.classList.add("is-invalid");
        } else if (!this.state.error_text &&
                   textarea.classList.contains("is-invalid")) {
          textarea.classList.remove("is-invalid");
        }
      }

    })

    .declareService(function focus() {
      if (this.state.focus === true) {
        this.element.querySelector('input').focus();
      }
    })

    .declareMethod('getContent', function getContent() {
      var gadget = this,
        result = {},
        input;

      if (this.state.editable) {
        input = this.element.querySelector('input');
        if (this.state.type === 'file') {
          if (input.files[0] !== undefined) {
            return new RSVP.Queue()
              .push(function () {
                var i,
                  promise_array = [];

                if (gadget.state.multiple) {
                  for (i = 0; i < input.files.length; i += 1) {
                    promise_array.push(saveAsDataURL(input.files[i]));
                  }
                  return RSVP.all(promise_array);
                }
                return saveAsDataURL(input.files[0]);
              })
              .push(function (result_dict) {
                result[input.getAttribute('name')] = result_dict;
                return result;
              });
          }
        } else if (this.state.type === 'checkbox') {
          result[input.getAttribute('name')] = (input.checked ? 1 : 0);
        } else if (this.state.type === 'radio') {
          if (input.checked) {
            result[input.getAttribute('name')] = input.value;
          }
        } else {
          if (this.state.trim) {
            result[input.getAttribute('name')] = input.value.trim();
          } else {
            result[input.getAttribute('name')] = input.value;
          }
        }
      }
      // Change the value state in place
      // This will prevent the gadget to be changed if
      // its parent call render with the same value
      // (as ERP5 does in case of formulator error)
      this.state.value = result[input.getAttribute('name')];
      return result;
    }, {mutex: 'changestate'})

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function checkValidity() {
      var input = this.element.querySelector('input'),
        result = input.checkValidity(),
        gadget = this;

      if (gadget.state.type === "radio") {
        result = result && !gadget.state.error_text;
      }

      if (result) {
        return gadget.notifyValid()
          .push(function () {
            var date,
              value;
            if ((gadget.state.type === 'checkbox') && gadget.state.error_text) {
              return gadget.notifyInvalid(gadget.state.error_text)
                .push(function () {
                  return result;
                });
            }
            if ((gadget.state.type === 'date') ||
                (gadget.state.type === 'datetime-local')) {
              value = gadget.element.querySelector('input').value;
              if (value) {
                date = Date.parse(value);
                if (isNaN(date)) {
                  return gadget.translate("Invalid DateTime")
                    .push(function (error_message) {
                      return RSVP.all([
                        gadget.deferErrorText(error_message),
                        gadget.notifyInvalid(error_message)
                      ]);
                    })
                    .push(function () {
                      return false;
                    });
                }
              }
            }
            return result;
          });
      }
      if (gadget.state.error_text) {
        return gadget.notifyInvalid(gadget.state.error_text)
          .push(function () {
            return result;
          });
      }

      return result;
    }, {mutex: 'changestate'})

    .declareJob('deferErrorText', function deferErrorText(error_text) {
      return this.changeState({
        error_text: error_text
      });
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function change() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange("change")
      ]);
    }, false, false)

    .onEvent('input', function input() {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange("input")
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyFocus", "notifyFocus")
    .onEvent('focus', function focus() {
      return this.notifyFocus();
    }, true, false)

    .declareAcquiredMethod("notifyBlur", "notifyBlur")
    .onEvent('blur', function blur() {
      return this.notifyBlur();
    }, true, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function invalid(evt) {
      // invalid event does not bubble
      return RSVP.all([
        this.deferErrorText(evt.target.validationMessage),
        this.notifyInvalid(evt.target.validationMessage)
      ]);
    }, true, false);

}(window, document, rJS, RSVP, jIO, getFirstNonEmpty));