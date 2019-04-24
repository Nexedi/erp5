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
        step: options.step,
        hidden: options.hidden,
        trim: options.trim || false,
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

      if (this.state.hidden) {
        textarea.hidden = true;
      } else {
        textarea.hidden = false;
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
      var result = this.element.querySelector('input').checkValidity(),
        gadget = this;
      if (result) {
        return this.notifyValid()
          .push(function () {
            var date,
              value;
            if (!result) {
              return result;
            }
            if ((gadget.state.type === 'date') ||
                (gadget.state.type === 'datetime-local')) {
              value = gadget.element.querySelector('input').value;
              if (value) {
                date = Date.parse(value);
                if (isNaN(date)) {
                  return gadget.notifyInvalid("Invalid DateTime")
                    .push(function () {
                      return false;
                    });
                }
              }
            }
            return result;
          });
      }
      return result;
    }, {mutex: 'changestate'})

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function change() {
      var input = this.element.querySelector("input");
      if (input) {
        // force the state to have the current edited value
        this.state.checked = input.checked;
        this.state.value = input.value;
      }
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

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function invalid(evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false);

}(window, document, rJS, RSVP, jIO, getFirstNonEmpty));