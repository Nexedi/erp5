/*global window, rJS, RSVP, jIO */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS, RSVP, jIO) {
  "use strict";

  rJS(window)
    .setState({
      editable: false,
      value: undefined,
      checked: undefined,
      title: '',
      type: 'text',
      required: false,
      trim: false,
      focus: undefined
    })

    .declareMethod('render', function (options) {
      var state_dict = {
          value: options.value || "",
          checked: options.checked,
          editable: options.editable,
          required: options.required,
          name: options.name,
          type: options.type || 'text',
          title: options.title,
          focus: options.focus,
          step: options.step,
          hidden: options.hidden,
          trim: options.trim || false
        };
      return this.changeState(state_dict);
    })

    .onStateChange(function () {
      var textarea = this.element.querySelector('input');
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

}(window, rJS, RSVP, jIO));