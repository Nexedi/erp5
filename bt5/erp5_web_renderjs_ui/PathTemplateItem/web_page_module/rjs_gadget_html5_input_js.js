/*global window, document, rJS, RSVP, jIO */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, document, rJS, RSVP, jIO) {
  "use strict";

  /** Missing value can have different values based on type.
   *
   * In general `undefined` and `null` are considered missing values
   * Float is missing when `NaN`
   */
  function is_missing(value) {
    if (value === undefined || value === null) {return true; }
    if (typeof value === "number") {return window.isNaN(value); }
    return false;
  }

  rJS(window)

    .declareMethod('render', function (options) {
      return this.changeState({
        // display nothing for missing values
        value: is_missing(options.value) ? "" : options.value,
        checked: options.checked,
        editable: options.editable,
        required: options.required,
        name: options.name,
        type: options.type || 'text',
        title: options.title,
        focus: options.focus,
        step: options.step,
        hidden: options.hidden,
        trim: options.trim || false,
        append: options.append, // text to apend after the field
        prepend: options.prepend // text to prepend infront the field
      });
    })

    .onStateChange(function (modification_dict) {
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
      textarea.setAttribute('name', this.state.name);
      textarea.setAttribute('id', this.state.name);

      textarea.setAttribute('type', this.state.type);
      if (this.state.title) {
        textarea.setAttribute('title', this.state.title);
      }
      if (this.state.step) {
        textarea.setAttribute('step', this.state.step);
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

    .declareService(function () {
      if (this.state.focus === true) {
        this.element.querySelector('input').focus();
      }
    })

    .declareMethod('getContent', function () {
      var result = {},
        input;
      if (this.state.editable) {
        input = this.element.querySelector('input');
        if (this.state.type === 'file') {
          if (input.files[0] !== undefined) {
            return new RSVP.Queue()
              .push(function () {
                return jIO.util.readBlobAsDataURL(input.files[0]);
              })
              .push(function (evt) {
                result[input.getAttribute('name')] = {
                  url: evt.target.result,
                  file_name: input.files[0].name
                };
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
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareMethod('checkValidity', function () {
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
    })

    .declareAcquiredMethod("notifyChange", "notifyChange")
    .onEvent('change', function () {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)
    .onEvent('input', function () {
      return RSVP.all([
        this.checkValidity(),
        this.notifyChange()
      ]);
    }, false, false)

    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .onEvent('invalid', function (evt) {
      // invalid event does not bubble
      return this.notifyInvalid(evt.target.validationMessage);
    }, true, false);

}(window, document, rJS, RSVP, jIO));