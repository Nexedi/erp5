/*global window, rJS */
/*jslint indent: 2, maxerr: 3, maxlen: 80 */
(function (window, rJS) {
  "use strict";

  function asBool(obj) {
    if (typeof obj === "boolean") {
      return obj;
    }
    if (typeof obj === "string") {
      return obj.toLowerCase() === "true" || obj === "1";
    }
    if (typeof obj === "number") {
      return obj !== 0;
    }
    return Boolean(obj);
  }

  rJS(window)
    .setState({
      type: 'checkbox',
      tag: 'p'
    })

    .declareMethod('render', function (options) {
      var field_json = options.field_json || {},
        state_dict = {
          checked: asBool(field_json.value || field_json.default),
          editable: field_json.editable,
          name: field_json.key,
          title: field_json.title,
          hidden: field_json.hidden
        };
      state_dict.text_content = state_dict.checked ? '✓' : '';
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
            // Clear first to DOM, append after to reduce flickering/manip
            while (element.firstChild) {
              element.removeChild(element.firstChild);
            }
            element.appendChild(input.element);
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
          })
          .push(function (result) {
            // Automatically add default_%s:int:0
            //   https://lab.nexedi.com/nexedi/erp5/blob/8ae0706177/product/Formulator/Widget.py#L476
            var key_list = Object.keys(result), i;
            for (i = 0; i < key_list.length; i += 1) {
              result["default_" + key_list[i] + ":int"] = 0;
            }
            return result;
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
}(window, rJS));