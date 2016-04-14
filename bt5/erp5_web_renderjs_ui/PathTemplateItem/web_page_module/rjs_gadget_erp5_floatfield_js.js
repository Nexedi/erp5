/*global window, rJS, RSVP, loopEventListener */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, RSVP, loopEventListener) {
  "use strict";

  rJS(window)
    .ready(function (gadget) {
      return gadget.getElement()
        .push(function (element) {
          gadget.element = element;
          gadget.props = {};
        });
    })
    .declareAcquiredMethod("notifyValid", "notifyValid")
    .declareAcquiredMethod("notifyInvalid", "notifyInvalid")
    .declareAcquiredMethod("notifyChange", "notifyChange")
    .declareMethod('getTextContent', function () {
      return this.element.querySelector('input').getAttribute('value');
    })
    .declareMethod('render', function (options) {
      var input = this.element.querySelector('input'),
        step = 0.00000001,
        field_json = options.field_json || {};
      input.setAttribute(
        'value',
        field_json.value || field_json.default || ""
      );
      this.props.field_json = options.field_json;
      if (field_json.precision !== "") {
        step = 1 / Math.pow(10, field_json.precision);
      }
      input.setAttribute("step", step);
      input.setAttribute('name', field_json.key);
      input.setAttribute('title', field_json.title);
      if (field_json.required === 1) {
        input.setAttribute('required', 'required');
      }
      if (field_json.editable !== 1) {
        input.setAttribute('readonly', 'readonly');
        input.setAttribute('data-wrapper-class', 'ui-state-disabled ui-state-readonly');
        input.setAttribute('disabled', 'disabled');

      }
    })

    .declareMethod('getContent', function () {
      var input = this.element.querySelector('input'),
        result = {};
      result[input.getAttribute('name')] = input.value;
      return result;
    })
    .declareMethod('checkValidity', function () {
      var result;
      result = this.element.querySelector('input').checkValidity();
      if (result) {
        return this.notifyValid()
          .push(function () {
            return result;
          });
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

    .declareService(function () {
      ////////////////////////////////////
      // Check field validity when the value changes
      ////////////////////////////////////
      var field_gadget = this;

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

}(window, rJS, RSVP, loopEventListener));