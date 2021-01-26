/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  var separator_re = /\d([\., \-_])?\d\d\d/,
    input_format_re = /(-?)(\d+)(\.\d+)?/,
    HTML5_INPUT_STYLE = "-1234.5",
    SPACE_INPUT_STYLE = "-1 234.5",
    SPACE_COMMA_INPUT_STYLE = "-1 234,5",
    DOT_COMMA_INPUT_STYLE = "-1.234,5",
    COMMA_DOT_INPUT_STYLE = "-1,234.5",
    PERCENT_INPUT_STYLE = "-12.3%";

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

  function convertFloatToHTML5Input(precision, input_style, float) {
    // ERP5 always devides the value by 100 if it is set to percentages
    // thus we have to mitigate that in javascript here
    if (input_style === PERCENT_INPUT_STYLE) {
      float *= 100.0;
    }
    return float.toString();
    // XXX precision
    // Always convert
  }

  function convertERP5InputToHTML5Input(precision, input_style, text) {
    // Convert ERP5 input style to html5 float text
    if (input_style === HTML5_INPUT_STYLE) {
      return text;
    } else {
      throw new Error('No supported input style: ' + input_style);
    }
  }

  function convertHTML5InputToERP5Input(precision, input_style, text) {
    if (input_style === HTML5_INPUT_STYLE) {
      return text;
    } else {
      throw new Error('No supported input style: ' + input_style);
    }
  }

  rJS(window)
    .setState({
      tag: 'p',  // important for CSS styles - noneditable element must be <p>
      type: "number"
    })
    .declareMethod('render', function (options) {
      console.log('floatfield.render', options.field_json);
      var field_json = options.field_json || {},
        input_style = (field_json.input_style || DEFAULT_INPUT_STYLE),
        value = field_json.default,
        text_content,
        precision = field_json.precision,
        // percentage = input_style.endsWith("%"),
        // thousand_sep = separator_re.test(input_style) ? (separator_re.exec(input_style)[1] || "") : "",
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          hidden: field_json.hidden,
          id: field_json.key,
          name: field_json.key,
          title: field_json.description,
          // precision: window.parseFloat(field_json.precision),
          error_text: field_json.error_text,
          // erp5 always put value into "default" (never "value")
          // value: window.parseFloat(field_json.default),
          // text_content: '',
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

      if (typeof(value) === 'number') {
        value = convertFloatToHTML5Input(precision, input_style, value);
        text_content = convertHTML5InputToERP5Input(precision, input_style, value);
      } else {
        text_content = value;
        value = convertERP5InputToHTML5Input(precision, input_style, value);
      }

      state_dict.value = value;
      state_dict.text_content = text_content;
      state_dict.input_style = input_style;

/*
      if (percentage) {
        // ERP5 always devides the value by 100 if it is set to percentages
        // thus we have to mitigate that in javascript here
        // (field_json.default type is number, only when it is initially loaded)
        if (typeof(field_json.default) == 'number') {
          state_dict.value *= 100.0;
        }
        state_dict.append = "%";
      }
      if (!window.isNaN(state_dict.precision)) {
        state_dict.step = Math.pow(10, -state_dict.precision).toFixed(state_dict.precision);
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
      console.log('floatfield.render2', state_dict.value);
*/

      return this.changeState(state_dict);
    })

    .onStateChange(function (modification_dict) {
      console.log('floatfield.onstatechange', modification_dict.value);
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
      var gadget = this;
      if (this.state.editable) {
        return this.getDeclaredGadget('sub')
          .push(function (sub_gadget) {
            return sub_gadget.getContent();
          })
          .push(function (result) {
            result[gadget.state.key] =
              convertHTML5InputToERP5Input(
                gadget.state.precision,
                gadget.state.input_style,
                result[gadget.state.key]
              );

            console.log('floatfield.getContent', result);
            return result;
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