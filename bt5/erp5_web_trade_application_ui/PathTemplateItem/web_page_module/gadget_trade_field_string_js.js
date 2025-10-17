/*global window, rJS, RSVP, loopEventListener, document */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener, document) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.props = {};
          gadget.element = element;
        });
    })

    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareAcquiredMethod("inputChange", "inputChange")
    .declareMethod('getTextContent', function () {
      return this.props.value;
    })
    .declareMethod('render', function (options) {
      var element,
        text,
        input,
        p,
        field_json = options.field_json || {},
        gadget = this;
      this.props.value = field_json.value || field_json.default || "";
      this.props.editable = field_json.editable;
      if (this.props.change !== undefined) {
        if (field_json.editable) {
          input = this.element.querySelector('input');
          input.value = this.props.value;
          if (field_json.disabled) {
            input.setAttribute("disabled", "disabled");
          } else {
            input.disabled = false;
          }
        } else {
          p = this.element.querySelector('p');
          text = document.createTextNode(this.props.value);
          p.appendChild(text);
        }
        if (this.props.value !== '' && this.props.value !== undefined) {
          return new RSVP.Queue()
            .push(function () {
              return gadget.notifyValid();
            });
        }
      } else {
        if (field_json.editable) {
          element = document.createElement('input');
          if (field_json.key === "date") {
            element.setAttribute("type", "date");
          } else {
            element.setAttribute("type", "text");
          }
          element.setAttribute('value', this.props.value);
          element.setAttribute('name', field_json.key);
          element.setAttribute('title', field_json.title);
          if (field_json.disabled) {
            element.setAttribute("disabled", "disabled");
          } else {
            element.removeAttribute('disabled');
          }
          if (field_json.required === 1) {
            element.setAttribute('required', 'required');
          } else {
            element.removeAttribute('required');
          }
        } else {
          element = document.createElement("p");
          element.setAttribute("class", "ui-content-non-editable");
          text = document.createTextNode(this.props.value);
          element.appendChild(text);
        }
        this.element.appendChild(element);
        this.props.change = true;
      }
    }
      )

    .declareMethod('getContent', function () {
      var input,
        result = {};
      if (this.props.editable) {
        input = this.element.querySelector('input');
        result[input.getAttribute('name')] = input.value;
      }
      return result;
    })

    .declareMethod('checkValidity', function () {
      var result;
      if (!this.props.editable) {
        return true;
      }
      result = this.element.querySelector('input').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
      }
      return result;
    })

    .declareService(function () {
      ////////////////////////////////////
      // Check field validity when the value changes
      ////////////////////////////////////
      var field_gadget = this;
      if (!field_gadget.props.editable) {
        return;
      }
      function notifyChange() {
        return RSVP.all([
          field_gadget.checkValidity(),
          field_gadget.notifyChange()
        ]);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('input'),
        'change',
        false,
        notifyChange
      );
    })

    .declareService(function () {
      ////////////////////////////////////
      // Check field validity when the value changes
      ////////////////////////////////////
      var field_gadget = this;
      if (!field_gadget.props.editable) {
        return;
      }
      function inputChange() {
        return new RSVP.Queue()
          .push(function () {
            // Wait for user to finish typing
            return RSVP.delay(100);
          })
          .push(function () {
            return field_gadget.getContent();
          })
          .push(function (contentChange) {
            return field_gadget.inputChange(contentChange);
          }
            );
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('input'),
        'input',
        false,
        inputChange
      );
    })

    .declareService(function () {
      ////////////////////////////////////
      // Inform when the field input is invalid
      ////////////////////////////////////
      var field_gadget = this;
      if (!field_gadget.props.editable) {
        return;
      }
      function notifyInvalid(evt) {
        return field_gadget.notifyInvalid(evt.target.validationMessage);
      }

      // Listen to input change
      return loopEventListener(
        field_gadget.element.querySelector('input'),
        'invalid',
        false,
        notifyInvalid
      );
    });

}(window, rJS, RSVP, loopEventListener, document));