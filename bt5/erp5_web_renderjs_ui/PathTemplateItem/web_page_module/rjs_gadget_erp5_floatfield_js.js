/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  rJS(window)
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        percentage = (field_json.input_style || "").endsWith("%"),
        state_dict = {
          type: "number",
          editable: field_json.editable,
          required: field_json.required,
          hidden: field_json.hidden,
          name: field_json.key,
          title: field_json.title,
          precision: window.parseFloat(field_json.precision),
          // erp5 always put value into "default" (never "value")
          value: window.parseFloat(field_json.default),
          text_content: '',
          // `step` is used for browser-level validation thus a mandatory value
          // if unspecified we can use "any" value
          step: "any",
          // `append` is a string to display next to the field ("%", "EUR"...)
          append: ''
        };
      if (!window.isNaN(state_dict.value)) {
        state_dict.text_content = state_dict.value.toString();
      }
      if (!window.isNaN(state_dict.precision)) {
        state_dict.step = Math.pow(10, -state_dict.precision);
        state_dict.value = state_dict.value.toFixed(state_dict.precision);
      }
      if (percentage) {
        // ERP5 always devides the value by 100 if it is set to pe percentages
        // thus we have to mitigate that in javascript here
        state_dict.value *= 100.0;
        state_dict.append = "%";
      }

      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      var element = this.element,
        gadget = this,
        url,
        result;
      if (modification_dict.hasOwnProperty('editable')) {
        if (gadget.state.editable) {
          url = 'gadget_html5_input.html';
        } else {
          url = 'gadget_html5_element.html';
        }
        result = this.declareGadget(url, {scope: 'sub'})
          .push(function (input) {
            var child = element.firstChild;
            // Clear first to DOM, append after to reduce flickering/manip
            while (child.firstChild) {
              child.removeChild(child.firstChild);
            }
            child.appendChild(input.element);
            return input;
          });
      } else {
        result = this.getDeclaredGadget('sub');
      }
      return result
        .push(function (input) {
          return input.render(gadget.state);
        });
    })

    .declareMethod('getContent', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.getContent();
          });
      }
      return {};
    })

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    });

}(window, rJS, Math));