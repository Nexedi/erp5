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
    .declareMethod('getTextContent', function () {
      return this.props.value;
    })
    .declareMethod('render', function (options) {
      var element,
        text,
        field_json = options.field_json || {};
      this.props.value = field_json.value || field_json.default || "";
      this.props.editable = field_json.editable;
      this.props.field_json = options.field_json;
      if (field_json.editable) {
        element = document.createElement('input');
        element.setAttribute("type", "text");
        element.setAttribute('value', this.props.value);
        element.setAttribute('name', field_json.key);
        element.setAttribute('title', field_json.title);
        if (field_json.required === 1) {
          element.setAttribute('required', 'required');
        }
      } else {
        element = document.createElement("p");
        element.setAttribute("class", "ui-content-non-editable");
        text = document.createTextNode(this.props.value);
        element.appendChild(text);
      }
      this.element.appendChild(element);
    })

    .declareMethod('getContent', function () {
      var input,
        result = {};
      if (this.props.editable) {
        input = this.element.querySelector('input');
        result[input.getAttribute('name')] = input.value;
      }
      return result;
    })
    .declareMethod('getNonSavedValue', function () {
      var input,
        result = {},
        props = this.props;
      input = this.element.querySelector('input');
      props.field_json.default = input.value;
      result[props.field_json.key] = props.field_json;
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