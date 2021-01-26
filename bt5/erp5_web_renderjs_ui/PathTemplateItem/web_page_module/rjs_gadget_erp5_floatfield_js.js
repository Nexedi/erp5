/*global window, rJS, Math, parseFloat, isNaN */
/*jslint indent: 2, maxerr: 3 */
(function (window, rJS, Math, parseFloat, isNaN) {
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
    if (!isNaN(precision)) {
      float = float.toFixed(precision);
    }
    return float.toString();
  }

  function convertERP5InputToHTML5Input(input_style, text) {
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

    return text;
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
    return text;
  }

  rJS(window)
    .setState({
      tag: 'p',  // important for CSS styles - noneditable element must be <p>
      type: "number"
    })
    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        input_style = (field_json.input_style || HTML5_INPUT_STYLE),
        value = field_json.default,
        text_content,
        precision = parseFloat(field_json.precision),
        state_dict = {
          editable: field_json.editable,
          required: field_json.required,
          hidden: field_json.hidden,
          id: field_json.key,
          name: field_json.key,
          title: field_json.description,
          // precision: window.parseFloat(field_json.precision),
          error_text: field_json.error_text,
          // `step` is used for browser-level validation thus a mandatory value
          // if unspecified we can use "any" value
          step: "any",
          // `append` is a string to display next to the field ("%", "EUR"...)
          append: '',
          // Force calling subfield render
          // as user may have modified the input value
          render_timestamp: new Date().getTime()
        };

      if (!isNaN(value)) {
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
      if (!isNaN(precision)) {
        state_dict.step = Math.pow(10, -precision)
                              .toFixed(precision);
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

}(window, rJS, Math, parseFloat, isNaN));