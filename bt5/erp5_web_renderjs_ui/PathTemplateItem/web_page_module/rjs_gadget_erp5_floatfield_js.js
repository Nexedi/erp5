/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  rJS(window)
    .setState({
      type: "number",
      // `step` is used for browser-level validation thus a mandatory value
      // HTML5 default is 1.0 which is not feasible most of the time thus we
      // default to over-sufficiently small value
      step: 0.00000001,
      required: false,
      editable: true,
      hidden: false,
      name: undefined,
      title: undefined,
      value: undefined,
      text_content: undefined,
      // `append` is a string to display next to the field (%, currency...)
      append: undefined
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        percentage = (field_json.input_style || "").endsWith("%"),
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.title,
          precision: window.parseFloat(field_json.precision),
          hidden: field_json.hidden,
          // erp5 always put value into "default"
          value: window.parseFloat(field_json.default)
        };

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

      if (window.isNaN(state_dict.value)) {
        state_dict.text_content = "";  // show empty value insted of ugly "NaN"
      } else {
        state_dict.text_content = state_dict.value.toString();
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