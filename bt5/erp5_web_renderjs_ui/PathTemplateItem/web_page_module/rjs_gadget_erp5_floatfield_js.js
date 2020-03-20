/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  var separator_re = /\d([\., \-_])?\d\d\d/,
    input_format_re = /(-?)(\d+)(\.\d+)?/;

  /** Slice any slice-able parameter into triplets **/
  function toTriplets(sliceable) {
    var parts = [],
      i = sliceable.length;
    for (i = sliceable.length; i > 3; i -= 3) {
      parts.unshift(sliceable.slice(i - 3, i));
    }
    parts.unshift(sliceable.slice(0, i));
    return parts;
  }

  rJS(window)
    .setState({
      tag: 'p',  // important for CSS styles - noneditable element must be <p>
      type: "number"
    })
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        input_style = (field_json.input_style || ""),
        percentage = input_style.endsWith("%"),
        thousand_sep = separator_re.test(input_style) ? (separator_re.exec(input_style)[1] || "") : "",
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          hidden: field_json.hidden,
          id: field_json.key,
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
          append: '',
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        },
        tmp;

      if (percentage) {
        // ERP5 always devides the value by 100 if it is set to percentages
        // thus we have to mitigate that in javascript here
        state_dict.value *= 100.0;
        state_dict.append = "%";
      }
      if (!window.isNaN(state_dict.precision)) {
        state_dict.step = Math.pow(10, -state_dict.precision);
        state_dict.value = state_dict.value.toFixed(state_dict.precision);
      }
      if (!window.isNaN(state_dict.value)) {
        state_dict.text_content = state_dict.value.toString();
        if (state_dict.text_content !== "" && thousand_sep !== "") {
          tmp = input_format_re.exec(state_dict.text_content);
          // tmp == [full-number, sign, integer-part, .decimal-part (can be undefined because of permissive regexp), ...]
          state_dict.text_content = tmp[1] + toTriplets(tmp[2]).join(thousand_sep) + (tmp[3] || "");
          tmp = undefined;
        }
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
    }, {mutex: 'changestate'})

    .declareMethod('checkValidity', function () {
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (gadget) {
            return gadget.checkValidity();
          });
      }
      return true;
    }, {mutex: 'changestate'});

}(window, rJS, Math));