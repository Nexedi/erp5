/*global window, rJS, Math */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math) {
  "use strict";

  var HTML5_INPUT_STYLE = "-1234.5",
    SPACE_INPUT_STYLE = "-1 234.5",
    SPACE_COMMA_INPUT_STYLE = "-1 234,5",
    DOT_COMMA_INPUT_STYLE = "-1.234,5",
    COMMA_DOT_INPUT_STYLE = "-1,234.5",
    PERCENT_INPUT_STYLE = "-12.3%";

  function setCharAt(str, index, chr) {
    return str.substring(0, index) + chr + str.substring(index + 1);
  }

  function getSeparatorDict(input_style) {
    if (input_style === SPACE_INPUT_STYLE) {
      return {thousand: ' ', decimal: '.'};
    }
    if (input_style === SPACE_COMMA_INPUT_STYLE) {
      return {thousand: ' ', decimal: ','};
    }
    if (input_style === DOT_COMMA_INPUT_STYLE) {
      return {thousand: '.', decimal: ','};
    }
    if (input_style === COMMA_DOT_INPUT_STYLE) {
      return {thousand: ',', decimal: '.'};
    }
    throw new Error('No supported input style: ' + input_style);
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

  function convertERP5InputToHTML5Input(input_style, text) {
    console.log('convertERP5InputToHTML5Input', text, input_style);
    // Convert ERP5 input style to html5 float text
    if (input_style === HTML5_INPUT_STYLE) {
      return text;
    }

    if (input_style === PERCENT_INPUT_STYLE) {
      if (text[text.length - 1] !== '%') {
        throw new Error('Can not parse: ' + text);
      }
      return text.substring(0, text.length - 1);
    }

    var separator_dict = getSeparatorDict(input_style),
      decimal_index = text.indexOf(separator_dict.decimal),
      original_text = text,
      i;

    if (decimal_index !== -1) {
      text = setCharAt(text, decimal_index, '.');
      i = decimal_index;
    } else {
      i = text.length;
    }

    i = i - 4;
    // Remove thousand separator
    while (i > 0) {
      if (text[i] !== separator_dict.thousand) {
        throw new Error('Can not parse: ' + original_text);
      }
      text = text.substring(0, i) + text.substring(i + 1);
      i -= 4;
    }

    console.log('convertERP5InputToHTML5Input 2', text);
    return text;
    // throw new Error('No supported input style: ' + input_style);
  }

  function convertHTML5InputToERP5Input(input_style, text) {
    if (input_style === HTML5_INPUT_STYLE) {
      return text;
    }

    if (input_style === PERCENT_INPUT_STYLE) {
      return text + '%';
    }

    var separator_dict = getSeparatorDict(input_style),
      decimal_index = text.indexOf('.'),
      i;
    console.log('before', text, decimal_index);
    if (decimal_index !== -1) {
      text = setCharAt(text, decimal_index, separator_dict.decimal);
      i = decimal_index;
    } else {
      i = text.length;
    }
    i = i - 3;
    // Add thousand separator
    while (i > 0) {
      text = text.substring(0, i) + separator_dict.thousand + text.substring(i);
      i -= 3;
    }
    console.log('after', text, decimal_index);
    return text;
    // throw new Error('not implemented');
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
        text_content = convertHTML5InputToERP5Input(input_style, value);
      } else {
        text_content = value;
        value = convertERP5InputToHTML5Input(input_style, value);
      }

      state_dict.value = value;
      state_dict.text_content = text_content;
      state_dict.input_style = input_style;

      if ((input_style === PERCENT_INPUT_STYLE) && state_dict.editable) {
        // Display the % next to the input field
        state_dict.append = "%";
      }
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
            result[gadget.state.name] =
              convertHTML5InputToERP5Input(
                gadget.state.input_style,
                result[gadget.state.name]
              );
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