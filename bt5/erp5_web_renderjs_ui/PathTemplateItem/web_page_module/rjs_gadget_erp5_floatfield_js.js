/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  rJS(window)
    .setState({
      tag: 'p',
      step: 1,
      type: "number"
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        value = field_json.value || field_json.default || "",
        percents = (field_json.input_style || "").endsWith("%"),
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          name: field_json.key,
          title: field_json.title,
          precision: field_json.precision,
          hidden: field_json.hidden
        };

      // if value is 0.0 we assign empty instead - so we fix it here
      if (field_json.value !== undefined && field_json.value !== '') {
        value = field_json.value;
      } else if (field_json.default !== undefined && field_json.default !== '') {
        value = field_json.default;
      }
      value = window.parseFloat(value); // at this step we finished joggling with value

      if (field_json.precision) {
        state_dict.step = Math.pow(10, -field_json.precision);
        value = value.toFixed(field_json.precision);
      } else {
        state_dict.step = 0.00000001;
      }
      if (percents) {
        // ERP5 always devides the value by 10 if it is set to pe percentages
        // thus we have to mitigate that in javascript here
        value *= 100.0;
        state_dict.append = "%";
      }
      state_dict.value = value;
      if (window.isNaN(value)) {
        state_dict.text_content = "";
      } else {
        state_dict.text_content = value.toString();
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
